"""CHECK C: recount with a DIFFERENT composition depth.

33*4 = 132 = 1 (mod 131)   ->  P4(X) = lambda^(4)(X) + X^2    (used in the sweep)
33*8 = 264 = 2 (mod 131)   ->  P8(X) = lambda^(8)(X) + X^4    (independent choice)

Both are valid superset polynomials by the same lemma at different k, so they
must give the same N.  deg P8 = d^8, so this is affordable for d=3 (6561) and
d=4 (65536), plus a spot check at d=5 (390625).
"""
import time, sys
from gf2poly import deg, poly_str
from method import count_roots
from rederive import is_linearized

def run(degrees, spot=None):
    ok = True
    for d in degrees:
        for low in range(1 << d):
            lam = (1 << d) | low
            if spot is not None and lam not in spot:
                continue
            t = time.time()
            n4 = count_roots(lam, 131, 33, k=4, e=1)
            n8 = count_roots(lam, 131, 33, k=8, e=2)
            good = (n4 == n8)
            ok &= good
            print(f'  {"OK " if good else "*** MISMATCH ***"} lambda={lam:4d} '
                  f'{poly_str(lam):34s} deg={d} linearized={is_linearized(lam)}  '
                  f'N(k=4)={n4:4d}  N(k=8)={n8:4d}   [{time.time()-t:.1f}s]', flush=True)
    return ok

if __name__ == '__main__':
    print('CHECK C: k=4 (deg P = d^4) vs k=8 (deg P = d^8), at n=131, n\'=33')
    print(' d=3 and d=4, every exact-degree polynomial (incl. the linearized ones):')
    ok = run([3, 4])
    print(' d=5 spot checks (deg P8 = 390625):')
    ok &= run([5], spot={32 | 0b00000 | (0), 33, 51, 63})   # X^5, X^5+1, X^5+X^4+X+1, X^5+X^4+X^3+X^2+X+1
    print('CHECK C', 'PASSED' if ok else 'FAILED')
