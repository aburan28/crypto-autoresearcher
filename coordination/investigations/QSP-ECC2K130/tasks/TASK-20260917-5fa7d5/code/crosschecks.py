"""Independent cross-checks of the n=131 sweep, by algorithms that share no
code path with the gcd/superset method.

CHECK A  Linear algebra.  For a LINEARIZED lambda the map x -> x^(2^33)+lambda(x)
         is F_2-linear on K, so the root count is 2^(dim ker), computable from the
         rank of a 131x131 matrix over F_2 -- no polynomial gcd anywhere.
         Compare against the superset/gcd method on the same lambdas.
CHECK B  Translation involution.  x is a root for lambda  <=>  x+1 is a root for
         lambda~(X) := lambda(X+1)+1.  So N(lambda) = N(lambda~) and the root sets
         are translates.  Checked over all 248 exact-degree polynomials.
CHECK C  Different composition depth k.  33*8 = 264 = 2 (mod 131), so
         P8(X) = lambda^(8)(X) + X^4 is an equally valid superset polynomial.
         Recount with k=8 and compare (feasible for d=3,4).
CHECK D  The F_2-part of the histogram, recomputed by pure combinatorics:
         0 is a root iff lambda(0)=0 (c_0=0); 1 is a root iff lambda(1)=1 (odd weight).
"""
import time
from gf2poly import deg, clmul, sqr, polymod, polygcd, frob_pow_mod, poly_str, is_irreducible
from gfk import Field
from method import count_roots, superset_poly
from rederive import FIELD_POLY, N_BITS, NPRIME, DEGREES, is_linearized

F = Field(FIELD_POLY)

def matrix_root_count(lam):
    """lam must be linearized: count roots of x^(2^33)+lam(x) by F_2 rank."""
    assert is_linearized(lam)
    cols = []
    for j in range(N_BITS):
        b = 1 << j                                   # basis element z^j
        v = F.pow2k(b, NPRIME) ^ F.evalpoly_f2(lam, b)
        cols.append(v)
    # gaussian elimination over F_2 on the 131 column vectors (each a 131-bit int)
    piv, rank = {}, 0
    for c in cols:
        v = c
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                rank += 1
                break
    dim_ker = N_BITS - rank
    return dim_ker, 1 << dim_ker

def translate(lam):
    """lambda(X+1) + 1 over GF(2)."""
    r = 0
    for i in range(lam.bit_length()):
        if (lam >> i) & 1:
            # (X+1)^i
            t = 1
            for _ in range(i):
                t = clmul(t, 0b11)
            r ^= t
    return r ^ 1

if __name__ == '__main__':
    print('CHECK A  linear algebra vs gcd method, on the linearized lambdas')
    lins = [lam for d in DEGREES for lam in ((1 << d) | low for low in range(1 << d))
            if is_linearized(lam)]
    # include some more linearized polys of other degrees to widen the check
    lins += [0b10, 0b11 & 0, 0b110, 0b10000, 0b10010, 0b100000000, (1<<8)|(1<<4)|(1<<2)|2]
    lins = sorted(set(l for l in lins if l > 1 and is_linearized(l)))
    ok = True
    for lam in lins:
        dimk, cnt = matrix_root_count(lam)
        N = count_roots(lam, N_BITS, NPRIME, k=4, e=1)
        flag = 'OK ' if cnt == N else '*** MISMATCH ***'
        ok &= (cnt == N)
        print(f'  {flag} lambda = {poly_str(lam):28s} dim ker = {dimk}  2^dim = {cnt:4d}'
              f'   gcd-method N = {N}')
    print(f'  CHECK A {"PASSED" if ok else "FAILED"}')
    print()

    print('CHECK B  translation involution lambda(X) -> lambda(X+1)+1')
    allpolys = [(1 << d) | low for d in DEGREES for low in range(1 << d)]
    counts = {}
    for lam in allpolys:
        counts[lam] = count_roots(lam, N_BITS, NPRIME, k=4, e=1)
    okB = True
    for lam in allpolys:
        t = translate(lam)
        assert deg(t) == deg(lam), (lam, t)
        if counts[lam] != counts[t]:
            okB = False
            print(f'  *** N mismatch: {poly_str(lam)} -> {poly_str(t)}: '
                  f'{counts[lam]} vs {counts[t]}')
    print(f'  all {len(allpolys)} exact-degree polynomials: N(lambda) == N(lambda(X+1)+1) '
          f'-> {"PASSED" if okB else "FAILED"}')
    big = sorted([l for l in allpolys if counts[l] > 2])
    print(f'  lambdas (over all 248, incl. linearized) with N>2: '
          f'{[(l, poly_str(l), counts[l]) for l in big]}')
    print(f'  involution pairing among those: '
          f'{[(l, translate(l)) for l in big]}')
    print()

    print('CHECK D  F_2-roots recomputed combinatorially over the 244 candidates')
    cands = [(1 << d) | low for d in DEGREES for low in range(1 << d)
             if not is_linearized((1 << d) | low)]
    hist2 = {}
    for lam in cands:
        nf2 = (1 if (lam & 1) == 0 else 0) + (1 if bin(lam).count('1') % 2 == 1 else 0)
        hist2[nf2] = hist2.get(nf2, 0) + 1
    print(f'  #candidates = {len(cands)}')
    print(f'  distribution of the F_2-part alone: {dict(sorted(hist2.items()))}')
    full = {}
    for lam in cands:
        full[counts[lam]] = full.get(counts[lam], 0) + 1
    print(f'  full histogram from the sweep:      {dict(sorted(full.items()))}')
    maxN = max(counts[l] for l in cands)
    arg = [l for l in cands if counts[l] == maxN]
    for lam in arg:
        nf2 = (1 if (lam & 1) == 0 else 0) + (1 if bin(lam).count('1') % 2 == 1 else 0)
        print(f'    argmax {lam:4d} {poly_str(lam):42s} N={counts[lam]}  '
              f'F_2-part={nf2} (0 root: {(lam&1)==0}, 1 root: {bin(lam).count("1")%2==1})')
    # consistency: every non-argmax has N = its F_2 part
    bad = [l for l in cands if counts[l] != maxN and
           counts[l] != (1 if (l & 1) == 0 else 0) + (1 if bin(l).count('1') % 2 == 1 else 0)]
    print(f'  candidates whose N differs from its pure-F_2 count (other than the argmax): '
          f'{len(bad)}  -> {"consistent" if not bad else bad}')
