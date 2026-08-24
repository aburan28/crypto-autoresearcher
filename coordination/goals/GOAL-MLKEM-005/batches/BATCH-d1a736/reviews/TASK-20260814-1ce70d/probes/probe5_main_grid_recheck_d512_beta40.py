#!/usr/bin/env python3
"""
TASK-20260814-1ce70d (Validator) -- probe5: SECOND independent main-grid
re-attempt (the completion gate requires at least one; this strengthens
coverage to a distinct failure mode). (d=512, beta=40) reportedly ERRORed
directly with ReductionError('infinite loop in babai') at bkz.py:123
(self.lll_obj() inside BKZReduction.__call__, the FIRST tour -- not the
chained ValueError seen at (256,40)), in 386.0s.

Same fresh, independent re-implementation and seed formula as probe4.
"""
import json
import os
import time

import numpy as np
from fpylll import IntegerMatrix, LLL, BKZ, FPLLL, GSO
from fpylll.algorithms.bkz2 import BKZReduction

SEED_ROOT = 715923
D = 512
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
    result["reported_seed_used_in_run_manifest"] = 2074339090
    result["seed_matches"] = seed == 2074339090

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
    result["reported_producer_wall_clock_seconds"] = 385.9634156227112
    result["reported_producer_status"] = "ERROR"
    result["reported_producer_error"] = "ReductionError: infinite loop in babai (direct, at bkz.py:123, first tour)"

    print(json.dumps(result, indent=2), flush=True)
    with open("probe5_main_grid_recheck_d512_beta40_output.json", "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
