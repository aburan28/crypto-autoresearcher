# EXP-EQJ-001 audit: independent verification of ranks/kernels for EXP-EQJ-001.
# Re-enumerates the m=4 fiber relation matrix from scratch (independent code path),
# computes ranks with Sage (GF(n) and QQ), and prints kernel vectors for inspection.
# Usage: sage eqj1_verify.sage --p 1009 --seed 20260718
import sys
import numpy as np
from sage.all import *

p = None; seed = None
for _i, _a in enumerate(sys.argv):
    if _a == '--p': p = int(sys.argv[_i+1])
    if _a == '--seed': seed = int(sys.argv[_i+1])
K_MAP = {211: 12, 1009: 12, 4099: 16}
k = K_MAP[p]
F = GF(p)
E = None
_found = False
for a in range(1, 400):
    for b in range(1, 400):
        if (4*a**3 + 27*b**2) % p == 0: continue
        E0 = EllipticCurve(F, [a, b])
        n0 = E0.order()
        if is_prime(n0):
            E, n = E0, int(n0); _found = True; break
    if _found: break
O = E(0)
xs = sorted({int(P[0]) for P in E.points() if P != O})
FB_x = xs[:k]
fb_index = {x: j for j, x in enumerate(FB_x)}
Q = []
for x in FB_x:
    lifts = sorted(E.lift_x(F(x), all=True), key=lambda P: int(P[1]))
    Q.append(lifts[0])
negQ = [-P for P in Q]
def pt(u):
    u = int(u)
    return Q[u >> 1] if (u & 1) == 0 else negQ[u >> 1]
twok = 2*k
PS = [[pt(a) + pt(b) for b in range(twok)] for a in range(twok)]
rng = np.random.RandomState(int(seed))
t0 = int(rng.randint(2, int(n-1)))
T = t0 * Q[0]
# independent enumeration: iterate over x-index triples and sign triples explicitly
rowset = {}
cnt = 0
for i0 in range(k):
    for i1 in range(k):
        for i2 in range(k):
            for s0 in (0, 1):
                P1 = pt(2*i0 + s0)
                for s1 in (0, 1):
                    S1 = P1 + pt(2*i1 + s1)
                    for s2 in (0, 1):
                        S = S1 + pt(2*i2 + s2)
                        R4 = T - S
                        if R4 == O: continue
                        j = fb_index.get(int(R4[0]))
                        if j is None: continue
                        c4 = 1 if R4 == Q[j] else -1
                        v = [0]*k
                        v[i0] += (1 if s0 == 0 else -1)
                        v[i1] += (1 if s1 == 0 else -1)
                        v[i2] += (1 if s2 == 0 else -1)
                        v[j]  += c4
                        key = tuple(v)
                        rowset[key] = v
                        cnt += 1
rows = list(rowset.values())
print("verify p=%d seed=%d: tuples_with_relations=%d distinct_rows=%d k=%d n=%d" % (p, seed, cnt, len(rows), k, n))
Mn = Matrix(GF(n), rows)
print("rank_GF(n)_distinct =", Mn.rank())
allrows = []
for i0 in range(k):
    pass
# full matrix with duplicates, exactly as main script accumulates (mod n)
rng = np.random.RandomState(int(seed))
t0 = int(rng.randint(2, int(n-1)))
T = t0 * Q[0]
A = {}
for u0i in range(twok):
    for u1i in range(twok):
        S01 = PS[u0i][u1i]
        for u2i in range(twok):
            S = S01 + pt(u2i)
            R4 = T - S
            if R4 == O: continue
            j = fb_index.get(int(R4[0]))
            if j is None: continue
            idx = (u0i*twok + u1i)*twok + u2i
            A.setdefault(idx, [0]*k)
            A[idx][u0i >> 1] += (1 if (u0i & 1) == 0 else -1)
            A[idx][u1i >> 1] += (1 if (u1i & 1) == 0 else -1)
            A[idx][u2i >> 1] += (1 if (u2i & 1) == 0 else -1)
            A[idx][j] += (1 if R4 == Q[j] else -1)
Mfull = Matrix(GF(n), list(A.values()))
print("rank_GF(n)_full =", Mfull.rank())
Mqq = Matrix(QQ, list(A.values()))
print("rank_QQ_full =", Mqq.rank())
Kker = Mn.right_kernel()
print("kernel dim (distinct, GF(n)) =", Kker.dimension())
for v in Kker.basis():
    print("kernel vector:", [int(x) for x in v])
