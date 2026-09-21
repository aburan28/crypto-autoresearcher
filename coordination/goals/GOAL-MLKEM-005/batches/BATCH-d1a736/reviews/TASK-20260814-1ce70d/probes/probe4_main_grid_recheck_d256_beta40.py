#!/usr/bin/env python3
"""
TASK-20260814-1ce70d (Validator) -- probe4: independently re-attempt the
cheapest main-grid cell (d=256, beta=40), the corrected construction, at the
producer's own bisected precision (65 bits), and compare the reported
wall-clock (223.4s) and the reported outcome (ERROR: ValueError('math domain
error') raised while handling ReductionError('infinite loop in babai')
inside fpylll's own tracer path).

This is a FRESH, INDEPENDENT re-implementation of worker_main_cell(), not an
import of stage0_v2_feasibility.py, matching the same construction shape and
seed formula documented in the producer's writeup.md / bisection_results.json:
  FPLLL.set_precision(65) before GSO.Mat construction
  GSO.Mat(A, float_type="mpfr"), no flags=GSO.ROW_EXPO
  M.update_gso()
  LLL.Reduction(M, flags=LLL.DEFAULT) -> L
  BKZReduction(L)
  bkz(BKZ.Param(block_size=40, strategies=..., flags=BKZ.AUTO_ABORT), tracer=True)

Chosen as the cheapest of the 6 cells that reached a definite outcome
(223.4s reported), so it fits comfortably inside this review task's own
budget alongside the other required checks.
"""
import json
import os
import time

import numpy as np
from fpylll import IntegerMatrix, LLL, BKZ, FPLLL, GSO
from fpylll.algorithms.bkz2 import BKZReduction

SEED_ROOT = 715923
D = 256
BETA = 40
MPFR_BITS = 65

STRATEGIES_PATH_DEFAULT = "/usr/share/libfplll8/strategies/default.json"


def _strategies_path():
    if os.path.exists(STRATEGIES_PATH_DEFAULT):
        return STRATEGIES_PATH_DEFAULT
    return BKZ.DEFAULT_STRATEGY


def main():
    result = {"d": D, "beta": BETA, "mpfr_bits": MPFR_BITS, "construction": "corrected_mpfr_no_row_expo (independent re-implementation)"}
    seed = int(np.random.default_rng([SEED_ROOT, 0, D, BETA, 0, 0]).integers(0, 2**31 - 1))
    FPLLL.set_random_seed(seed)
    result["seed_used"] = seed
    result["reported_seed_used_in_run_manifest"] = 1398073216
    result["seed_matches"] = seed == 1398073216

    strategies_path = _strategies_path()
    result["strategies_file_used"] = strategies_path

    t_wall0 = time.time()
    try:
        A = IntegerMatrix.random(D, "qary", k=D // 2, q=3329)
        t0 = time.time()
        LLL.reduction(A)
        lll_elapsed = time.time() - t0
        result["outer_lll_reduction_elapsed_seconds"] = lll_elapsed

        FPLLL.set_precision(MPFR_BITS)
        M = GSO.Mat(A, float_type="mpfr")
        M.update_gso()
        result["gso_float_type_used"] = M.float_type
        L = LLL.Reduction(M, flags=LLL.DEFAULT)

        par = BKZ.Param(block_size=BETA, strategies=strategies_path, flags=BKZ.AUTO_ABORT)
        bkz = BKZReduction(L)
        t1 = time.time()
        bkz(par, tracer=True)
        bkz_elapsed = time.time() - t1
        result["bkz_elapsed_seconds"] = bkz_elapsed
        result["status"] = "COMPLETED"
        FPLLL.set_precision(53)
    except Exception as exc:  # noqa: BLE001
        import traceback
        result["status"] = "ERROR"
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["traceback"] = traceback.format_exc()
        try:
            FPLLL.set_precision(53)
        except Exception:
            pass

    result["total_wall_clock_seconds"] = time.time() - t_wall0
    result["reported_producer_wall_clock_seconds"] = 223.3597059249878
    result["reported_producer_status"] = "ERROR"
    result["reported_producer_error"] = "ValueError: math domain error (chained from ReductionError('infinite loop in babai'))"

    print(json.dumps(result, indent=2), flush=True)
    with open("probe4_main_grid_recheck_d256_beta40_output.json", "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
