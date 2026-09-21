# dev/probe_null_deep.sage — DEV-ONLY: longer-timeout null probes at n=12 to bound
# the matched null's optimum region (k_fix = 4, 6 with 50 s per-GB timeout).
# Same instance as RUN-EXP-ICI-001-e cell (n=12, curve_seed=1, target 0).

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ici_lib as L
import random

n = int(12)
t = int(3)
k = (n + t - 1) // t
Fq, E, alpha, B = L.build_curve(n, int(1))
V = L.make_V_subspace(Fq, alpha, k)
cseed = L.cell_seed("crossbred", int(1), n)
tgts = L.make_targets(E, t, V, int(1), cseed)
R_X, P_list = tgts[0]
Bring, dpolys = L.descend_system(t, Fq, B, R_X, n, k, alpha)
null_rng = random.Random(L.cell_seed("null", int(1), n))
nulls, match_ok = L.matched_null_polys(dpolys, Bring, null_rng)
print("null match certified:", match_ok, "nb:", Bring.ngens(), flush=True)
rng = random.Random(int(999))
for kfix in [int(4), int(6)]:
    t0 = time.time()
    best, rows, bias = L.crossbred_sweep(
        nulls, Bring, Bring.ngens(), [float(kfix) / Bring.ngens()], int(1),
        float(50), rng, time.time() + float(55))
    print("k_fix=%d rows=%s wall=%.1fs" % (kfix, rows, time.time() - t0), flush=True)
