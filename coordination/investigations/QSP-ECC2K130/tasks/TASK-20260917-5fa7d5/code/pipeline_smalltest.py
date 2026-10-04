"""End-to-end test of the whole pipeline at small n, against brute force.

Pipeline = structural count (method.count_roots) + root extraction (gfk) +
verification.  Compared against exhaustive enumeration of F_(2^n).
"""
import random
from gf2poly import (deg, clmul, sqr, polymod, polygcd, frob_pow_mod,
                     is_irreducible, poly_str)
from gfk import Field, factor_squarefree, roots_of_f2_irreducible_in_K
from method import count_roots, choose_k
from smallcheck import exact_degree_lambdas, brute_all, find_irreducibles

def minpoly_over_K(F, a):
    """min poly of a over GF(2), as a bit-packed GF(2) poly (checked to be in GF(2)[X])."""
    orbit = [a]
    v = F.sqr(a)
    while v != a:
        orbit.append(v); v = F.sqr(v)
    poly = [1]                      # coefficients in K, index=degree
    for r in orbit:
        new = [0] * (len(poly) + 1)
        for i, c in enumerate(poly):
            new[i + 1] ^= c
            new[i] ^= F.mul(c, r)
        poly = new
    out = 0
    for i, c in enumerate(poly):
        assert c in (0, 1), 'minpoly not over GF(2)!'
        out |= c << i
    return out, orbit

def test_minpoly_roundtrip(n, fpoly, trials=6):
    F = Field(fpoly)
    random.seed(1000 + n)
    for t in range(trials):
        a = F.rand()
        mp, orbit = minpoly_over_K(F, a)
        assert is_irreducible(mp), 'minpoly reducible'
        rs = roots_of_f2_irreducible_in_K(F, mp)
        assert sorted(rs) == sorted(orbit), 'root extraction != Frobenius orbit'
        for r in rs:
            assert F.evalpoly_f2(mp, r) == 0
    print(f'  minpoly/root-extraction round trip OK at n={n} '
          f'(degrees seen: {sorted(set(deg(minpoly_over_K(F, F.rand())[0]) for _ in range(8)))})')

def test_full_pipeline(n, nprime, degs):
    k, e = choose_k(n, nprime)
    fpoly = find_irreducibles(n, 1)[0]
    F = Field(fpoly)
    lambdas = [l for d in degs for l in exact_degree_lambdas(d)]
    bt = brute_all(n, nprime, fpoly, lambdas)
    print(f'  full pipeline n={n} n\'={nprime} k={k} e={e} f={poly_str(fpoly,"z")} '
          f'over {len(lambdas)} lambdas')
    worst = 0
    for lam in lambdas:
        N, G = count_roots(lam, n, nprime, k=k, e=e, want_G=True)
        brute = sorted(bt[lam])
        assert N == len(brute), f'count mismatch lam={lam}: {N} vs {len(brute)}'
        if N == 0:
            continue
        # extract roots from G independently and compare as SETS
        facs = factor_squarefree(G)
        got = []
        for q in facs:
            got += roots_of_f2_irreducible_in_K(F, q)
        assert sorted(got) == brute, f'root set mismatch lam={lam}'
        # each extracted root must satisfy the ORIGINAL equation
        for x in got:
            y = x
            for _ in range(nprime):
                y = F.sqr(y)
            assert y == F.evalpoly_f2(lam, x), 'extracted root fails original equation'
        worst = max(worst, N)
    print(f'    all counts AND root sets match brute force; max N seen = {worst}')

if __name__ == '__main__':
    for n, fp in [(13, (1 << 13) | (1 << 4) | (1 << 3) | (1 << 1) | 1),
                  (11, (1 << 11) | (1 << 2) | 1),
                  (9,  (1 << 9) | (1 << 1) | 1)]:
        test_minpoly_roundtrip(n, fp)
    test_full_pipeline(13, 10, range(3, 8))      # prime n, k=4,e=1: mirrors 131/33
    test_full_pipeline(9, 7, range(3, 8))        # composite n: mixed orbit sizes
    test_full_pipeline(11, 3, range(3, 8))
    print('PIPELINE VALIDATED AT SMALL SCALE')
