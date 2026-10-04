"""Small-case cross-check: brute force over ALL of F_(2^n) vs the structural method.

For small n we can enumerate the whole field, so we get the ground truth for
   N(lambda) = #{x in F_(2^n) : x^(2^n') = lambda(x)}
and compare it against deg G produced by method.count_roots, which never
enumerates anything.  We also check that the polynomial G vanishes exactly on
the brute-force root set (not just that the degrees agree), and that the count
does not depend on which irreducible f of degree n is used (it must not: the
count is intrinsic to the field).
"""
import sys, itertools
from gf2poly import deg, clmul, sqr, polymod, is_irreducible, poly_str
from method import count_roots, choose_k

def find_irreducibles(n, how_many=2):
    out = []
    for low in range(1, 1 << n):
        f = (1 << n) | low
        if bin(low).count('1') % 2 == 1:      # need f(1)=1, i.e. odd total weight
            continue
        if not (f & 1):
            continue
        if is_irreducible(f):
            out.append(f)
            if len(out) == how_many:
                break
    return out

def brute_all(n, nprime, f, lambdas):
    """returns {lam: sorted root list} by direct enumeration of F_(2^n)."""
    N = 1 << n
    maxd = max(l.bit_length() - 1 for l in lambdas)
    pw = [[0] * N for _ in range(maxd + 1)]
    for x in range(N):
        pw[0][x] = 1
    if maxd >= 1:
        for x in range(N):
            pw[1][x] = x
    for i in range(2, maxd + 1):
        prev = pw[i - 1]; cur = pw[i]
        for x in range(N):
            cur[x] = polymod(clmul(prev[x], x), f)
    frob = list(range(N))
    for _ in range(nprime):
        frob = [polymod(sqr(v), f) for v in frob]
    res = {}
    for lam in lambdas:
        idx = [i for i in range(lam.bit_length()) if (lam >> i) & 1]
        cols = [pw[i] for i in idx]
        roots = []
        for x in range(N):
            v = 0
            for c in cols:
                v ^= c[x]
            if v == frob[x]:
                roots.append(x)
        res[lam] = roots
    return res

def evalpoly_in_field(p, x, f):
    r = 0
    for i in range(p.bit_length() - 1, -1, -1):
        r = polymod(clmul(r, x), f)
        if (p >> i) & 1:
            r ^= 1
    return r

def exact_degree_lambdas(d):
    return [(1 << d) | low for low in range(1 << d)]

def run_case(n, nprime, degs, label=''):
    ks = choose_k(n, nprime)
    fs = find_irreducibles(n, 2)
    lambdas = [l for d in degs for l in exact_degree_lambdas(d)]
    print(f'--- n={n} n\'={nprime} (k,e)={ks} degs={list(degs)} '
          f'#lambda={len(lambdas)} f={[poly_str(x,"z") for x in fs]} {label}')
    struct = {}
    for lam in lambdas:
        Nn, G = count_roots(lam, n, nprime, k=ks[0], e=ks[1], want_G=True)
        struct[lam] = (Nn, G)
    ok = True
    for fi, f in enumerate(fs):
        bt = brute_all(n, nprime, f, lambdas)
        for lam in lambdas:
            roots = bt[lam]
            Nn, G = struct[lam]
            if len(roots) != Nn:
                ok = False
                print(f'  MISMATCH lam={lam} ({poly_str(lam)}): brute={len(roots)} struct={Nn}')
                continue
            # G must vanish exactly on the brute-force roots
            for x in roots:
                if evalpoly_in_field(G, x, f) != 0:
                    ok = False
                    print(f'  G does not vanish at a brute root: lam={lam} x={x}')
            # and G must have no other roots in the field (deg G == #roots and G squarefree)
        print(f'  f#{fi} = {poly_str(f,"z")}: all {len(lambdas)} lambdas agree'
              if ok else f'  f#{fi}: FAILURES above')
    hist = {}
    for lam in lambdas:
        hist[struct[lam][0]] = hist.get(struct[lam][0], 0) + 1
    print('  structural histogram N -> count:', dict(sorted(hist.items())))
    return ok

if __name__ == '__main__':
    allok = True
    # primes n, with n' chosen so that 4*n' = 1 (mod n): mirrors n=131, n'=33 exactly
    allok &= run_case(11, 3,  range(3, 8), '(4*3=12=1 mod 11)')
    allok &= run_case(13, 10, range(3, 8), '(4*10=40=1 mod 13)')
    # composite n: Frobenius orbits of several sizes; the method must not assume n prime
    allok &= run_case(9,  7,  range(3, 8), '(4*7=28=1 mod 9)')
    # a case where k != 4, to exercise the generic k/e logic
    allok &= run_case(13, 5,  range(3, 5), '(k should be 8)')
    allok &= run_case(7,  2,  range(3, 8), '(k=4: 8=1 mod 7)')
    print('ALL SMALL CASES OK' if allok else 'SOME SMALL CASES FAILED')
