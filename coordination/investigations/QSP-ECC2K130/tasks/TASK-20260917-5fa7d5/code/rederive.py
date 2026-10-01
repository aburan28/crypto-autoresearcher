"""BLIND RE-DERIVATION, TASK-20260917-5fa7d5.

K = F_2[z]/(z^131 + z^13 + z^2 + z + 1),  n = 131,  n' = 33.
For each lambda in F_2[X] of exact degree d in {3,...,7} that is NOT linearized,
   L = X^(2^33) - lambda(X),   N(lambda) = #{distinct roots of L in K}.
Report max, argmax, histogram, candidate-set size, Frobenius orbit structure,
and explicit roots.

Method: see method.py docstring.  Nothing in this file reads any repository state.
"""
import json, random, sys, time
from gf2poly import (deg, clmul, sqr, polymod, polygcd, frob_pow_mod,
                     is_irreducible, poly_str)
from gfk import Field, factor_squarefree, roots_of_f2_irreducible_in_K
from method import count_roots, superset_poly, choose_k

N_BITS = 131
NPRIME = 33
FIELD_POLY = (1 << 131) | (1 << 13) | (1 << 2) | (1 << 1) | 1
DEGREES = [3, 4, 5, 6, 7]

def is_linearized(lam):
    """all monomials have exponent a power of 2 (X^(2^i)); exponent 0 is NOT a power of 2."""
    for i in range(lam.bit_length()):
        if (lam >> i) & 1:
            if i == 0 or (i & (i - 1)) != 0:
                return False
    return True

def main():
    random.seed(20260917)
    t0 = time.time()
    out = {}
    print('=' * 78)
    print('BLIND RE-DERIVATION  TASK-20260917-5fa7d5')
    print('=' * 78)
    print(f'field polynomial f(z) = {poly_str(FIELD_POLY, "z")}')
    print(f'deg f = {deg(FIELD_POLY)}   f irreducible over GF(2): '
          f'{is_irreducible(FIELD_POLY)}   (Rabin test)')
    print(f'n = {N_BITS}, n\' = {NPRIME}, gcd(n,n\') = '
          f'{__import__("math").gcd(N_BITS, NPRIME)}')
    k, e = choose_k(N_BITS, NPRIME)
    print(f'composition depth: smallest k with k*n\' = e (mod n), e<=1  ->  k={k}, e={e}'
          f'   [{k}*{NPRIME} = {k*NPRIME} = {k*NPRIME//N_BITS}*{N_BITS} + {k*NPRIME%N_BITS}]')
    print(f'superset polynomial P(X) = lambda^({k})(X) + X^(2^{e}), deg P = d^{k} <= {7**k}')
    print()

    # ---- candidate set, derived ----
    print('-' * 78)
    print('CANDIDATE SET (derivation)')
    cands, per_deg = [], {}
    excluded = []
    for d in DEGREES:
        tot = 1 << d                      # c_d = 1 forced, c_0..c_{d-1} free
        lin = [lam for lam in ((1 << d) | low for low in range(1 << d))
               if is_linearized(lam)]
        keep = [lam for lam in ((1 << d) | low for low in range(1 << d))
                if not is_linearized(lam)]
        per_deg[d] = (tot, len(lin), len(keep))
        excluded += lin
        cands += keep
        print(f'  d={d}: exact-degree-{d} polys = 2^{d} = {tot:3d}   '
              f'linearized among them = {len(lin)}   kept = {len(keep):3d}'
              + ('   [' + ', '.join(poly_str(l) for l in lin) + ']' if lin else ''))
    print(f'  TOTAL  = {sum(v[0] for v in per_deg.values())} exact-degree polys'
          f'  -  {len(excluded)} linearized  =  {len(cands)} candidates')
    print()
    out['candidate_set'] = {'per_degree': {str(d): per_deg[d] for d in DEGREES},
                            'excluded_linearized': excluded,
                            'size': len(cands)}

    # ---- sweep ----
    print('-' * 78)
    print('SWEEP')
    results = {}
    Gs = {}
    for lam in cands:
        N, G = count_roots(lam, N_BITS, NPRIME, k=k, e=e, want_G=True)
        results[lam] = N
        Gs[lam] = G
    hist = {}
    for lam in cands:
        hist[results[lam]] = hist.get(results[lam], 0) + 1
    print('  histogram of N(lambda):')
    for v in sorted(hist):
        print(f'    N = {v:4d}   count = {hist[v]:3d}')
    print(f'  sum of counts = {sum(hist.values())} (must equal {len(cands)})')
    assert sum(hist.values()) == len(cands)
    mx = max(results.values())
    arg = sorted([lam for lam in cands if results[lam] == mx])
    print(f'  MAXIMUM N = {mx}, attained by {len(arg)} lambda(s): {arg}')
    for lam in arg:
        print(f'    lambda = {lam}  (0b{lam:b})  =  {poly_str(lam)}   deg={deg(lam)}')
    out['histogram'] = {str(k_): v for k_, v in sorted(hist.items())}
    out['max_N'] = mx
    out['argmax'] = arg
    out['all_counts'] = {str(l): results[l] for l in cands}
    print()

    # ---- explicit roots for the attaining lambdas ----
    print('-' * 78)
    print('EXPLICIT ROOTS FOR THE ATTAINING LAMBDA(S)')
    F = Field(FIELD_POLY)
    out['attaining'] = []
    for lam in arg:
        G = Gs[lam]
        print(f'  lambda = {poly_str(lam)}   (packed {lam})   N = {results[lam]}   '
              f'deg G = {deg(G)}')
        facs = sorted(factor_squarefree(G), key=lambda q: (deg(q), q))
        print(f'    G factors over GF(2) into degrees: {[deg(q) for q in facs]}')
        for q in facs:
            assert is_irreducible(q), 'claimed irreducible factor is not irreducible'
        prod = 1
        for q in facs:
            prod = clmul(prod, q)
        assert prod == G, 'factor product != G'
        orbits, roots = [], []
        for q in facs:
            rs = roots_of_f2_irreducible_in_K(F, q)
            # canonical listing: start the Frobenius cycle at the numerically
            # smallest element, then x, x^2, x^4, ...  (independent of the
            # randomness inside Cantor-Zassenhaus)
            start = min(rs)
            cyc, v = [start], F.sqr(start)
            while v != start:
                cyc.append(v); v = F.sqr(v)
            assert sorted(cyc) == sorted(rs)
            rs = cyc
            orbits.append({'minpoly_packed': q, 'minpoly': poly_str(q),
                           'orbit_size': len(rs), 'roots': rs})
            roots += rs
        assert len(set(roots)) == len(roots) == results[lam], 'root count mismatch'
        print(f'    Frobenius (x->x^2) orbit sizes: {[o["orbit_size"] for o in orbits]}'
              f'   (sum {sum(o["orbit_size"] for o in orbits)})')
        # in-script check (an independent check is run separately by verify_roots.py)
        bad = 0
        for x in roots:
            if F.pow2k(x, NPRIME) != F.evalpoly_f2(lam, x):
                bad += 1
        print(f'    in-script check x^(2^33) == lambda(x): {len(roots)-bad}/{len(roots)} pass'
              + ('' if bad == 0 else f'   *** {bad} FAILURES ***'))
        out['attaining'].append({
            'lambda_packed': lam, 'lambda': poly_str(lam), 'degree': deg(lam),
            'N': results[lam], 'G_degree': deg(G), 'G_packed_hex': hex(G),
            'orbits': [{'minpoly_packed': o['minpoly_packed'],
                        'minpoly': o['minpoly'],
                        'orbit_size': o['orbit_size'],
                        'roots_hex': [hex(r) for r in o['roots']],
                        'roots_bits_lsb_first':
                            [''.join(str((r >> i) & 1) for i in range(N_BITS))
                             for r in o['roots']]} for o in orbits]})
    print()
    print(f'elapsed {time.time()-t0:.1f}s')
    with open('rederivation_results.json', 'w') as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print('wrote rederivation_results.json')

if __name__ == '__main__':
    main()
