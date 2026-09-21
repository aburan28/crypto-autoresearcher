#!/usr/bin/env python3
"""
Independent Validator probe, decisive test: does fpylll's own top-level
NATIVE C++ convenience function `BKZ.reduction(A, par)` (float_type=None,
i.e. fplll's own automatic precision choice -- the SAME style of call
TASK-20260814-ffd791's own worker_toy_floor() uses successfully at d=8/12)
succeed on the IDENTICAL (d, beta, seed) main-grid cell that
worker_main_cell()'s own BKZReduction(...)-class-based call failed on?

If YES: this is strong evidence the reported ReductionError is a
PARAMETER-CONSTRUCTION artifact of stage0_feasibility.py's own choice to
use the pure-Python BKZReduction class (which builds its own internal GSO
at a fixed 'double' float_type with no automatic precision escalation, per
fpylll/algorithms/bkz.py's own __init__), not an unfixable fpylll/fplll
library limitation at this dimension.

If NO (native BKZ.reduction also fails or errors differently): this
weakens that hypothesis and supports the producer's own "genuine
fplll-internal issue, independent of the calling convention" reading.

Usage: python3 probe_native_bkz.py <d> <beta>
"""
import json
import sys
import time
import traceback

import numpy as np

SEED_ROOT = 715923


def main(d, beta):
    from fpylll import IntegerMatrix, LLL, BKZ, FPLLL
    import os

    strategies_path = "/usr/share/libfplll8/strategies/default.json"
    if not os.path.exists(strategies_path):
        strategies_path = BKZ.DEFAULT_STRATEGY

    seed = int(np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1))
    result = {"d": d, "beta": beta, "seed_used": seed}

    FPLLL.set_random_seed(seed)
    A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
    t0 = time.time()
    LLL.reduction(A)
    result["outer_lll_elapsed_seconds"] = time.time() - t0

    par = BKZ.Param(block_size=beta, strategies=strategies_path, flags=BKZ.AUTO_ABORT)
    t1 = time.time()
    try:
        BKZ.reduction(A, par)  # NATIVE C++ BKZ, float_type=None (automatic)
        result["status"] = "COMPLETED"
        result["native_bkz_elapsed_seconds"] = time.time() - t1

        # compute delta_0 the same way the producer's worker_main_cell does,
        # via a GSO built on the now-reduced A (post-hoc, does not affect
        # the reduction's own success/failure already recorded above).
        from fpylll import GSO
        import math
        M = GSO.Mat(A, flags=GSO.ROW_EXPO)
        M.update_gso()
        log_det = M.get_log_det(0, d)
        r0 = M.get_r(0, 0)
        delta_0 = ((r0 ** 0.5) / math.exp(log_det / d)) ** (1.0 / d)
        result["delta_0_root_hermite_factor"] = delta_0
    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["traceback"] = traceback.format_exc()
        result["native_bkz_elapsed_seconds"] = time.time() - t1

    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    d = int(sys.argv[1])
    beta = int(sys.argv[2])
    out = main(d, beta)
    with open("probe_native_bkz_d%d_beta%d.json" % (d, beta), "w") as f:
        json.dump(out, f, indent=2)
