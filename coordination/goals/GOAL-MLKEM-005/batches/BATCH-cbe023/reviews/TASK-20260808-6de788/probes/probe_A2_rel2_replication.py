#!/usr/bin/env python3
"""RED-TEAM PROBE, NOT PRE-REGISTERED.

Section A scores G-REL1 and G-REL2 on ONE basis (index i = 0; measure_am4.py
`src.get((lat, beta, 0))`).  The R3 headline turns on X10 = hkz missing REL-2
by 0.0697 against tau_rel = 0.10.  This probe replicates the SAME frozen
quantity over ALL EIGHT frozen bases at the pair (L7, L8) = ((20,6),(20,14))
and asks whether the decisive number is a stable block-attribution signal or a
single draw from a distribution whose spread covers the threshold.

Frozen construction and frozen HKZ pipeline are reproduced from
measure_am4.py.  Claim tier TOY.  Not a rescoring of any frozen verdict.
"""
import math
import numpy as np
from fpylll import IntegerMatrix, GSO, LLL, BKZ, Enumeration, EnumerationError
from fpylll.fplll.bkz_param import Strategy
from fpylll.algorithms.bkz import BKZReduction

Q = 3329


def basis(d, k, q, i):
    A = np.random.default_rng([1, d, k, i]).integers(0, q, size=(k, d - k))
    B = np.zeros((d, d), dtype=float)
    B[:k, :k] = np.eye(k)
    B[:k, k:] = A
    B[k:, k:] = q * np.eye(d - k)
    return B


def hkz_profile(M, d):
    G = np.rint(M @ M.T)
    A = IntegerMatrix(d, d)
    for i in range(d):
        for j in range(d):
            A[i, j] = int(G[i, j])
    Mg = GSO.Mat(A, gram=True)
    Mg.update_gso()
    LLL.Reduction(Mg)()
    strat = [Strategy(b) for b in range(d + 1)]
    bk = BKZReduction(Mg)
    bk(BKZ.Param(block_size=d, strategies=strat, max_loops=1, flags=BKZ.MAX_LOOPS))
    for _ in range(30):
        changed = False
        for i in range(d - 1):
            ri = Mg.get_r(i, i)
            try:
                nd, sol = Enumeration(Mg).enumerate(i, d, ri, 0)[0]
            except EnumerationError:
                continue
            if nd < ri * (1 - 1e-12):
                bk.svp_postprocessing(i, d - i, sol)
                Mg.update_gso()
                changed = True
        if not changed:
            break
    r = np.array([Mg.get_r(i, i) for i in range(d)], dtype=float)
    viol = 0.0
    for i in range(d - 1):
        try:
            mn = Enumeration(Mg).enumerate(i, d, r[i] * 1.0000001, 0)[0][0]
        except EnumerationError:
            mn = r[i]
        viol = max(viol, (r[i] - mn) / r[i])
    return r, 0.5 * float(np.sum(np.log(r))), viol


def hkz_at(r, logdet, d, beta):
    return float(np.mean(0.5 * np.log(r)[d - beta:]) - logdet / d)


d, BETAS = 20, [5, 10, 15]
vals = {}
viols = []
for k in (6, 14):
    for i in range(8):
        r, ld, v = hkz_profile(basis(d, k, Q, i), d)
        viols.append(v)
        for b in BETAS:
            vals[(k, b, i)] = hkz_at(r, ld, d, b)

print("max HKZ violation over the 16 reductions: %.3e  (0.0 = verified HKZ)"
      % max(viols))
print()
print("REL-2 on the mirrored pair L7 (20,6) / L8 (20,14), per basis")
print("%5s %4s %11s %11s %10s %10s" %
      ("beta", "i", "hkz(k=6)", "hkz(k=14)", "frozen", "relative"))
for b in BETAS:
    fr, rl = [], []
    for i in range(8):
        a, c = vals[(6, b, i)], vals[(14, b, i)]
        f = abs(c - a) / max(abs(a), 1.0)
        rr = abs(c - a) / abs(a)
        fr.append(f); rl.append(rr)
        mark = "  <- the ONLY basis the frozen gate scores" if i == 0 else ""
        print("%5d %4d %11.6f %11.6f %10.5f %10.5f%s" % (b, i, a, c, f, rr, mark))
    fr = np.array(fr); rl = np.array(rl)
    a0 = np.array([vals[(6, b, i)] for i in range(8)])
    c0 = np.array([vals[(14, b, i)] for i in range(8)])
    print("  beta=%2d  frozen REL-2: i=0 -> %.5f | over 8 bases min %.5f med %.5f "
          "max %.5f sd %.5f  (tau_rel = 0.10)"
          % (b, fr[0], fr.min(), np.median(fr), fr.max(), fr.std(ddof=1)))
    print("           relative     : i=0 -> %.5f | over 8 bases min %.5f med %.5f "
          "max %.5f" % (rl[0], rl.min(), np.median(rl), rl.max()))
    print("           between-basis sd of hkz WITHIN a cell: k=6 %.5f  k=14 %.5f"
          "   | mean mirrored gap %.5f" % (a0.std(ddof=1), c0.std(ddof=1),
                                           abs(c0.mean() - a0.mean())))
    t = (c0 - a0).mean() / ((c0 - a0).std(ddof=1) / math.sqrt(8))
    print("           paired t over the 8 bases on the mirrored gap: t = %.3f "
          "(df 7)" % t)
    print()
