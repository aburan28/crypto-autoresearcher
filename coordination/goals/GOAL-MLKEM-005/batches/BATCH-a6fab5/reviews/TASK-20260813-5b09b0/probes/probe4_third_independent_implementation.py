#!/usr/bin/env python3
"""Final, clean run of the third (independently-structured) HKZ control for
cell hkz/L7_b5, bases i=1..7 (i=0 already separately reported as an
anomalous, slow, wrong-answer case in this red-team's own from-scratch
descending-sweep implementation -- see probe_third_route_i0_anomaly.txt).
No Python `signal` module use (conflicts with cysignals' own SIGALRM-based
interrupt handling inside fpylll -- an earlier attempt to add a Python-level
per-basis timeout produced zero output after 250s, most likely from exactly
this conflict; noted here as a recorded, not-followed-up infrastructure
observation, not a finding about the producer)."""
import sys, os, math, json, time
import numpy as np
from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration
from fpylll.fplll.enumeration import EnumerationError
from fpylll.fplll.bkz import BKZReduction as LowBKZ

REPO = "/home/user/crypto-autoresearcher"
RESULTS_HKZ_INDEP = os.path.join(REPO,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/"
    "TASK-20260813-c0ec71/results_hkz_indep.json")
Q = 3329


def build_basis(d, k, q, i):
    rng = np.random.default_rng([1, d, k, i])
    A = rng.integers(0, q, size=(k, d - k), dtype=np.int64)
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = A
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def third_route_hkz(B, d):
    A = IntegerMatrix(d, d)
    for r_ in range(d):
        for c_ in range(d):
            A[r_, c_] = int(B[r_, c_])
    M = GSO.Mat(A, float_type="double")
    M.update_gso()
    LLL.reduction(A)
    M.update_gso()
    BKZ.reduction(A, BKZ.Param(block_size=d, max_loops=1, flags=BKZ.MAX_LOOPS))
    M.update_gso()
    lll_obj = LLL.Reduction(M)
    bk = LowBKZ(M, lll_obj, BKZ.Param(block_size=d))
    for round_no in range(40):
        changed = False
        for idx in range(d - 2, -1, -1):
            r_idx = M.get_r(idx, idx)
            try:
                nd, vec = Enumeration(M).enumerate(idx, d, r_idx, 0)[0]
            except EnumerationError:
                continue
            if nd < r_idx * (1.0 - 1e-12):
                bk.svp_postprocessing(idx, d - idx, vec)
                M.update_gso()
                changed = True
        if not changed:
            break
    r = np.array([M.get_r(idx, idx) for idx in range(d)], dtype=float)
    return r, round_no


def hkz_value(r, d, k, beta, logdet):
    logb = 0.5 * np.log(r)
    return float(np.mean(logb[d - beta:]) - logdet / d)


with open(RESULTS_HKZ_INDEP) as fh:
    hkz_indep = json.load(fh)
cell_name, lat, d, k, beta = "hkz/L7_b5", "L7", 20, 6, 5
cell = hkz_indep["R_V_OUT_2_per_cell"][cell_name]
route_p = cell["route_p_values"]
route_ii = cell["route_ii_values"]
logdet_closed = (d - k) * math.log(Q)

print("cell=%s d=%d k=%d beta=%d -- bases i=1..7 (i=0 excluded, see note)" % (cell_name, d, k, beta))
for i in [1, 2, 3, 4, 5, 6, 7]:
    t0 = time.time()
    B = build_basis(d, k, Q, i)
    r, rounds = third_route_hkz(B, d)
    logdet_empirical = 0.5 * float(np.sum(np.log(r)))
    hv_emp = hkz_value(r, d, k, beta, logdet_empirical)
    hv_closed = hkz_value(r, d, k, beta, logdet_closed)
    dp = route_p[i]
    dii = route_ii[i]
    print("i=%d  route_p=%.17f  route_ii=%.17f  THIRD(empirical_logdet)=%.17f  "
          "THIRD(closed_logdet)=%.17f  |third_emp-p|=%.3e  |third_closed-p|=%.3e  "
          "rounds=%d  (%.2fs)"
          % (i, dp, dii, hv_emp, hv_closed, abs(hv_emp - dp), abs(hv_closed - dp),
             rounds, time.time() - t0))
