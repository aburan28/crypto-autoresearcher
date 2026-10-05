#!/usr/bin/env python3
"""Method D for |V|: pure NumPy, batched Gauss-Jordan over all 2^k assignments of the FIRST half, pivot-column-major, no code shared with count_solutions.c.
For a fixed first half x1, each generator is  b_e(x1) + sum_j u_e(x1)_j x2_j = 0  (affine in x2).  Built straight from the parsed B-polynomials
(msparse), vectorised over a batch of assignments: u_e = u0_e xor (xor of U_e[i] over set bits i of x1), b_e likewise.
Elimination: for pivot column j = 0..k-1 choose, per assignment, the first not-yet-used row with bit j set, xor it into every other row with bit j set.
Count = sum over consistent assignments of 2^(k - rank).   usage: count_numpy.py SYSTEM.ms [BATCH_LOG2] [--roles2]"""
import sys, os, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msparse import parse_ms

def count(ms, blog=18, swap=False):
    N, B, R, info = parse_ms(ms)
    k = N // 2
    E = list(range(k)) if not swap else list(range(k, N)); Y = list(range(k, N)) if not swap else list(range(k))
    ypos = {v: i for i, v in enumerate(Y)}; epos = {v: i for i, v in enumerate(E)}
    M = len(B)
    u0 = np.zeros(M, dtype=np.uint32); b0 = np.zeros(M, dtype=np.uint8)
    U = np.zeros((M, k), dtype=np.uint32); Bm = np.zeros((M, k), dtype=np.uint8)
    for e, p in enumerate(B):
        for m in p:
            ev = [v for v in range(N) if (m >> v) & 1 and v in epos]; yv = [v for v in range(N) if (m >> v) & 1 and v in ypos]
            assert len(yv) <= 1 and len(ev) <= 1, 'not bilinear/affine'
            if not yv:
                if not ev: b0[e] ^= 1
                else: Bm[e, epos[ev[0]]] ^= 1
            else:
                if not ev: u0[e] ^= np.uint32(1) << np.uint32(ypos[yv[0]])
                else: U[e, epos[ev[0]]] ^= np.uint32(1) << np.uint32(ypos[yv[0]])
    total = 0; nsat = 0
    batch = 1 << blog; nE = 1 << k
    for start in range(0, nE, batch):
        x = np.arange(start, min(start + batch, nE), dtype=np.uint64); nb = len(x)
        u = np.tile(u0[:, None], (1, nb)); b = np.tile(b0[:, None], (1, nb))
        for i in range(k):
            bit = ((x >> np.uint64(i)) & np.uint64(1)).astype(bool)
            u[:, bit] ^= U[:, i][:, None]
            b[:, bit] ^= Bm[:, i][:, None]
        used = np.zeros((M, nb), dtype=bool)
        rank = np.zeros(nb, dtype=np.int64)
        ar = np.arange(nb)
        for j in range(k):
            has = (((u >> np.uint32(j)) & np.uint32(1)).astype(bool)) & (~used)
            anyhas = has.any(axis=0)
            piv = has.argmax(axis=0)                         # first row with bit j among unused rows
            pu = u[piv, ar]; pb = b[piv, ar]
            hit = (((u >> np.uint32(j)) & np.uint32(1)).astype(bool))
            hit[piv, ar] = False
            hit &= anyhas[None, :]
            u ^= np.where(hit, pu[None, :], np.uint32(0))
            b ^= np.where(hit, pb[None, :], np.uint8(0))
            used[piv[anyhas], ar[anyhas]] = True
            rank += anyhas
        incons = ((u == 0) & (b == 1)).any(axis=0)
        ok = ~incons
        total += int(np.sum(np.where(ok, np.left_shift(1, (k - rank)), 0), dtype=np.int64)); nsat += int(ok.sum())
    return total, nsat

if __name__ == '__main__':
    t = time.time()
    swap = '--roles2' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    tot, nsat = count(args[0], int(args[1]) if len(args) > 1 else 18, swap)
    print('%s total=%d consistent_assignments=%d wall=%.1f roles=%s' % (os.path.basename(args[0])[:42], tot, nsat, time.time() - t, 'second-half-enumerated' if swap else 'first-half-enumerated'))
