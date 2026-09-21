"""INDEPENDENT re-implementation of the whole sweep using sympy's GF(2)
polynomial arithmetic (sympy.polys.galoistools).  Shares NO code with
gf2poly.py / method.py / gfk.py: different representation (dense coefficient
lists, highest degree first), different multiplication, division, and gcd.

Same mathematics (derivation in method.py's docstring), independent arithmetic.

usage: python3 sympy_sweep.py <chunk> <nchunks> <outfile>
"""
import json, sys, time
from sympy.polys.galoistools import gf_mul, gf_rem, gf_gcd, gf_add, gf_degree, gf_strip
from sympy.polys.domains import ZZ

P2 = 2
X = [1, 0]

def packed_to_list(lam):
    """bit-packed int -> sympy dense list, highest degree first."""
    if lam == 0:
        return []
    return [(lam >> i) & 1 for i in range(lam.bit_length() - 1, -1, -1)]

def compose(f, g):
    """f(g(X)) by Horner, sympy arithmetic."""
    r = []
    for c in f:                      # f is highest-degree-first
        r = gf_mul(r, g, P2, ZZ)
        if c:
            r = gf_add(r, [1], P2, ZZ)
    return gf_strip(r)

def frob(h, m, times):
    """h^(2^times) mod m."""
    for _ in range(times):
        h = gf_rem(gf_mul(h, h, P2, ZZ), m, P2, ZZ)
    return h

def count(lam, n=131, nprime=33, k=4, e=1):
    ll = packed_to_list(lam)
    c = ll
    for _ in range(k - 1):
        c = compose(ll, c)
    P = gf_add(c, [1] + [0] * (1 << e), P2, ZZ)        # + X^(2^e)
    h = frob(X, P, n)                                  # X^(2^n) mod P
    g = gf_gcd(P, gf_add(h, X, P2, ZZ), P2, ZZ)
    dg = gf_degree(g)
    if dg <= 0:
        return 0, dg, gf_degree(P)
    B = frob(X, g, nprime)                             # X^(2^n') mod g
    G = gf_gcd(g, gf_add(B, gf_rem(ll, g, P2, ZZ), P2, ZZ), P2, ZZ)
    dG = gf_degree(G)
    return max(dG, 0), dg, gf_degree(P)

def is_linearized(lam):
    for i in range(lam.bit_length()):
        if (lam >> i) & 1:
            if i == 0 or (i & (i - 1)) != 0:
                return False
    return True

if __name__ == '__main__':
    chunk, nch, outfile = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    cands = [(1 << d) | low for d in (3, 4, 5, 6, 7) for low in range(1 << d)
             if not is_linearized((1 << d) | low)]
    mine = [l for i, l in enumerate(cands) if i % nch == chunk]
    res = {}
    t0 = time.time()
    for j, lam in enumerate(mine):
        N, dg, dP = count(lam)
        res[lam] = [N, dg, dP]
        print(f'[{chunk}] {j+1}/{len(mine)} lam={lam} deg={lam.bit_length()-1} '
              f'degP={dP} deg_g={dg} N={N}  ({time.time()-t0:.0f}s)', flush=True)
    with open(outfile, 'w') as fh:
        json.dump({str(k_): v for k_, v in res.items()}, fh)
    print(f'[{chunk}] done in {time.time()-t0:.0f}s -> {outfile}', flush=True)
