#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDATOR PROBE 2 -- TASK-20260813-968dc8

Extends probe1 to ALL 6 named PREREG-5 cells (L7/L9/L11, both beta_lo and
beta_hi), independently re-deriving ROUTE-P-algorithm and
ROUTE-I''-algorithm r-vectors (bit-identical check) and hkz values for a
subset of bases per cell (bases 0,1,2 -- 3 of 8, to stay well inside
budget while covering every dimension d in {20,30,40}), and comparing
against the producer's own results_hkz_indep.json AND against
results_relvar.json's own G_REL1.hkz per-basis ground truth, reading
results_relvar.json myself rather than trusting results_hkz_indep.json's
transcription.

Also independently confirms the sha256 of results_relvar.json.
"""
import hashlib
import json
import math
import os
import time

import numpy as np
from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration, EnumerationError
from fpylll.fplll.bkz_param import Strategy
from fpylll.algorithms.bkz import BKZReduction as BKZReductionAlgo
from fpylll.fplll.bkz import BKZReduction as BKZReductionLowLevel

Q = 3329
HKZ_MAX_SWEEP = 30
N_BASES_PROBE = 3  # of 8; keep runtime bounded

REPO_ROOT = "/home/user/crypto-autoresearcher"
RESULTS_RELVAR_PATH = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
    "tasks/TASK-20260809-cda2f6/results_relvar.json")
RESULTS_HKZ_INDEP_PATH = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/"
    "tasks/TASK-20260813-c0ec71/results_hkz_indep.json")

CELLS = [
    ("hkz/L7_b5",   "L7", 20, 6,  5),
    ("hkz/L7_b15",  "L7", 20, 6,  15),
    ("hkz/L9_b7",   "L9", 30, 9,  7),
    ("hkz/L9_b22",  "L9", 30, 9,  22),
    ("hkz/L11_b10", "L11", 40, 12, 10),
    ("hkz/L11_b30", "L11", 40, 12, 30),
]


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def make_A(d, k, q, i):
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, d - k), dtype=np.int64)


def build_basis(d, k, q, i):
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A(d, k, q, i)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def gram_int(M):
    G = M @ M.T
    Gr = np.rint(G)
    return Gr


def route_p_reduce(B, d):
    Gr = gram_int(B.astype(np.float64))
    A = IntegerMatrix(d, d)
    for i in range(d):
        for j in range(d):
            A[i, j] = int(Gr[i, j])
    Mg = GSO.Mat(A, gram=True)
    Mg.update_gso()
    LLL.Reduction(Mg)()
    strat = [Strategy(b) for b in range(d + 1)]
    bk = BKZReductionAlgo(Mg)
    bk(BKZ.Param(block_size=d, strategies=strat, max_loops=1, flags=BKZ.MAX_LOOPS))
    for sweeps in range(HKZ_MAX_SWEEP):
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
    return np.array([Mg.get_r(i, i) for i in range(d)], dtype=float)


def route_ii_reduce(B, d):
    A = IntegerMatrix(d, d)
    for r_ in range(d):
        for c_ in range(d):
            A[r_, c_] = int(B[r_, c_])
    M = GSO.Mat(A, float_type="double")
    M.update_gso()
    lll_obj = LLL.Reduction(M)
    lll_obj()
    M.update_gso()
    param = BKZ.Param(block_size=d, max_loops=1, flags=BKZ.MAX_LOOPS)
    bkz = BKZReductionLowLevel(M, lll_obj, param)
    bkz()
    M.update_gso()
    round_no = 0
    while round_no < 40:
        round_no += 1
        any_improved = False
        for idx in range(d - 1):
            r_idx = M.get_r(idx, idx)
            try:
                sol_nd, sol_vec = Enumeration(M).enumerate(idx, d, r_idx, 0)[0]
            except EnumerationError:
                continue
            if sol_nd < r_idx * (1.0 - 1e-12):
                bkz.svp_postprocessing(idx, d - idx, sol_vec)
                M.update_gso()
                any_improved = True
        if not any_improved:
            break
    return np.array([M.get_r(idx, idx) for idx in range(d)], dtype=float)


def hkz_value_p(r, d, beta):
    logb = 0.5 * np.log(r)
    logdet = 0.5 * float(np.sum(np.log(r)))
    return float(np.mean(logb[d - beta:]) - logdet / d)


def hkz_value_ii(r, d, k, beta, q):
    logb = 0.5 * np.log(np.maximum(r, 1e-300))
    logdet = (d - k) * math.log(q)
    return float(np.mean(logb[d - beta:]) - logdet / d)


if __name__ == "__main__":
    t_start = time.time()
    print("results_relvar.json sha256 (independently computed): %s"
          % sha256_file(RESULTS_RELVAR_PATH))
    with open(RESULTS_RELVAR_PATH) as fh:
        relvar = json.load(fh)
    with open(RESULTS_HKZ_INDEP_PATH) as fh:
        producer = json.load(fh)

    g_rel1_hkz = relvar["G_REL1"]["hkz"]

    all_match_p = True
    all_match_ii = True
    max_diff_seen = 0.0
    for cell_name, lat, d, k, beta in CELLS:
        entry = g_rel1_hkz[lat]
        beta_lo, beta_hi = entry["beta_lo"], entry["beta_hi"]
        field = "X_a" if beta == beta_lo else "X_b"
        route_p_from_relvar = [row[field] for row in entry["per_basis"]]

        prod_cell = producer["R_V_OUT_2_per_cell"][cell_name]
        prod_p = prod_cell["route_p_values"]
        prod_ii = prod_cell["route_ii_values"]
        prod_d_route = prod_cell["D_route_pp"]

        # cross-check producer's own route_p_values against results_relvar.json directly
        relvar_match = route_p_from_relvar[:N_BASES_PROBE] == prod_p[:N_BASES_PROBE]

        print("\n=== %s (lat=%s d=%d k=%d beta=%d, field=%s) ===" %
              (cell_name, lat, d, k, beta, field))
        print("  producer route_p_values[:3] == results_relvar.json G_REL1 read directly: %s"
              % relvar_match)

        my_diffs = []
        for i in range(N_BASES_PROBE):
            B = build_basis(d, k, Q, i)
            r_p = route_p_reduce(B, d)
            r_ii = route_ii_reduce(B, d)
            r_bit_id = bool(np.array_equal(r_p, r_ii))
            hv_p = hkz_value_p(r_p, d, beta)
            hv_ii = hkz_value_ii(r_ii, d, k, beta, Q)
            match_p = (hv_p == prod_p[i])
            match_ii = (hv_ii == prod_ii[i])
            all_match_p &= match_p
            all_match_ii &= match_ii
            diff = abs(hv_p - hv_ii)
            my_diffs.append(diff)
            max_diff_seen = max(max_diff_seen, diff)
            print("    basis %d: r_bit_identical=%-5s  my_hv_p=%.17g match_producer_p=%-5s  "
                  "my_hv_ii=%.17g match_producer_ii=%-5s  |diff|=%.3e"
                  % (i, r_bit_id, hv_p, match_p, hv_ii, match_ii, diff))
        print("  max |diff| over probed bases: %.6e  (producer's reported D_route'' over ALL "
              "8 bases: %.6e)" % (max(my_diffs), prod_d_route))

    print("\n" + "=" * 70)
    print("ALL independently-recomputed route_p values bit-match producer's "
          "route_p_values: %s" % all_match_p)
    print("ALL independently-recomputed route_ii values bit-match producer's "
          "route_ii_values: %s" % all_match_ii)
    print("max |hv_p - hv_ii| seen across all probed (cell,basis) pairs: %.6e" % max_diff_seen)
    print("total probe wall time: %.2fs" % (time.time() - t_start))
