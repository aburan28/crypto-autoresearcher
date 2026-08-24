#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDATOR PROBE 4 -- TASK-20260813-01f482 / BATCH-8d09f5 / GOAL-MLKEM-005

Independent, from-scratch fpylll recomputation of ONE basis at ONE cell
(hkz/L7_b5, basis slot i=0, d=20/k=6/beta=5/q=3329), written by the
Validator without importing measure_hkz_indep.py or
measure_hkz_mutation6.py. This is a direct check on whether the reported
"detection" could be an artifact of fpylll's own convergence behavior
differing on the mutant's genuinely-different (shifted-seed) matrix for
reasons UNRELATED to the seed shift itself, rather than the seed shift
actually causing basis slot i to compute the true HKZ profile of a
DIFFERENT basis.

Two matrices are built and reduced, both via this script's own
independently-written reduction/enumeration driver (same general recipe --
LLL, then one BKZ pass at block_size=d, then an explicit HKZ sweep via
Enumeration -- since that reduction *shape* is the part PREREG-5 2.2 point 3
explicitly licenses both routes to share and is NOT the code path under
test; what is under test is only the seed FORMULA):

  (A) UNMUTATED seed formula at slot i=0: default_rng([1, 20, 6, 0])
      -- expected to reproduce ROUTE-P's own archived X_a[0].
  (B) MUTATED seed formula at slot i=0: default_rng([1, 20, 6, (0+1) % 8])
      = default_rng([1, 20, 6, 1])
      -- this is exactly what the mutant computes when asked for slot 0.
      Predicted (HEURISTIC-M1) to reproduce ROUTE-P's own archived X_a[1],
      NOT X_a[0], if the mechanism is genuinely the claimed cyclic shift.

If (B) reproduces X_a[1] (not X_a[0]) to within the same ~1e-14 floor
BATCH-a6fab5 established for genuine HKZ-quality convergence, that is
direct, independent evidence that the "detection" reflects the seed shift
actually causing a different, genuinely-computed HKZ profile -- not an
unrelated fpylll convergence artifact.
"""
import json
import math
import os
import time

import numpy as np
from fpylll import IntegerMatrix, LLL, GSO, Enumeration
from fpylll.fplll.enumeration import EnumerationError
from fpylll.fplll.bkz import BKZReduction
from fpylll import BKZ

D, K, Q, BETA = 20, 6, 3329, 5
N_BASES = 8


def make_A(d, k, q, i):
    """Independently re-typed from PREREG-6 section 2.2's own quoted
    formula (not copy-pasted from either route file)."""
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, d - k), dtype=np.int64)


def build_basis(d, k, q, i):
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A(d, k, q, i)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def reduce_and_hkz_value(B, d, k, beta, q, deadline_ts):
    """Independently-written reduction driver: LLL -> one BKZ pass at
    block_size=d -> explicit HKZ sweep via Enumeration -> hkz observable.
    Same general algorithmic shape as measure_hkz_indep.py (licensed
    shared reduction/enumeration shape, PREREG-5 2.2 point 3), written
    independently here rather than imported."""
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
    bkz = BKZReduction(M, lll_obj, param)
    bkz()
    M.update_gso()

    round_no = 0
    while round_no < 40:
        if time.time() > deadline_ts:
            break
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

    r = np.array([M.get_r(idx, idx) for idx in range(d)], dtype=float)
    logb = 0.5 * np.log(np.maximum(r, 1e-300))
    logdet = (d - k) * math.log(q)
    hkz_val = float(np.mean(logb[d - beta:]) - logdet / d)
    return hkz_val, round_no


def main():
    deadline = time.time() + 500.0

    # (A) UNMUTATED, slot i=0
    B_unmut_0 = build_basis(D, K, Q, 0)
    hkz_unmut_0, rounds_a = reduce_and_hkz_value(B_unmut_0, D, K, BETA, Q, deadline)

    # (B) MUTATED formula applied at slot i=0 -> (0+1)%8 = 1
    B_mut_0 = build_basis(D, K, Q, (0 + 1) % N_BASES)
    hkz_mut_0, rounds_b = reduce_and_hkz_value(B_mut_0, D, K, BETA, Q, deadline)

    route_p_X_a = [
        -0.17267425560428773, -0.1929579968533437, -0.23882977009594697,
        -0.17224042118823757, -0.18649226890643344, -0.22425794699744994,
        -0.20262184823098472, -0.21193896956714386,
    ]
    lead_mut_value_slot0 = -0.19295799685334192  # from results_hkz_mutation6.json

    out = {
        "cell": "hkz/L7_b5",
        "basis_slot_tested": 0,
        "own_unmutated_recompute_slot0": hkz_unmut_0,
        "route_p_archived_X_a_0": route_p_X_a[0],
        "own_unmutated_matches_route_p_slot0": abs(hkz_unmut_0 - route_p_X_a[0]) < 1e-9,
        "own_unmutated_residual": abs(hkz_unmut_0 - route_p_X_a[0]),
        "own_mutated_recompute_slot0": hkz_mut_0,
        "route_p_archived_X_a_1_shifted_target": route_p_X_a[1],
        "own_mutated_matches_route_p_SHIFTED_slot1": abs(hkz_mut_0 - route_p_X_a[1]) < 1e-9,
        "own_mutated_residual_vs_shifted_target": abs(hkz_mut_0 - route_p_X_a[1]),
        "own_mutated_residual_vs_UNSHIFTED_slot0 (should NOT match)": abs(hkz_mut_0 - route_p_X_a[0]),
        "lead_reported_mut_value_slot0": lead_mut_value_slot0,
        "own_vs_lead_reported_residual": abs(hkz_mut_0 - lead_mut_value_slot0),
        "sweep_rounds": {"unmutated": rounds_a, "mutated": rounds_b},
        "conclusion": (
            "If own_mutated_matches_route_p_SHIFTED_slot1 is true and "
            "own_unmutated_matches_route_p_slot0 is true, this is direct, "
            "independent (separately-written driver, separately-run "
            "fpylll session) confirmation that the seed-index mutation "
            "genuinely causes slot 0 to compute the TRUE HKZ profile of "
            "basis slot 1 -- not an artifact of fpylll's convergence "
            "behavior differing for unrelated reasons."
        ),
    }
    out_path = os.path.join(
        "/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/"
        "batches/BATCH-8d09f5/reviews/TASK-20260813-01f482/probes/"
        "probe4_independent_fpylll_recompute_output.json")
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
