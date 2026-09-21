#!/usr/bin/env python3
"""
RED TEAM PROBE 7 -- test the CHEAPEST candidate fix: does simply calling
the top-level `fpylll.BKZ.reduction(A, par)` FREE FUNCTION (float_type=None
by its own docstring default = "automatic choice"), instead of the OOP
`BKZReduction(A)` class stage0_feasibility.py's own worker_main_cell uses
(which hardcodes float_type="double" -- see probe3/probe5), avoid the
"infinite loop in babai" failure with NO manual precision management at
all?

This matters because stage0_feasibility.py's OWN toy-floor sweep
(worker_toy_floor) already calls `BKZ.reduction(A, par)` -- this exact free
function -- successfully at small d/beta_toy, while the MAIN GRID worker
(worker_main_cell) uses the different `BKZReduction` class + manual
`bkz(par, tracer=True)` call that fails. If the free function alone
resolves the failure at the SAME (d, beta) that the class-based call
fails at, this is a two-line producer-script change, not a fplll/fpylll
library defect requiring an upstream investigation.

Tested at d=224 (probe4's own cheapest reproducing dimension) to keep this
probe fast; CPU contention note: this probe was run WHILE probe6 (a
separate, heavier mpfr full-BKZ-tour probe) was also running in the
background on this same 4-vCPU host, so THIS PROBE's own elapsed-time
numbers are NOT presented as clean/uncontended timing measurements --
only its PASS/FAIL outcome is load-bearing, exactly the same discipline
the producer's own run_manifest.yaml DEV-4 entry applies to its own
CPU-contention concern.
"""
import json
import sys
import time

import numpy as np

SEED_ROOT = 715923


def run(d, beta, out_path):
    result = {"d": d, "beta": beta, "note": "elapsed times NOT clean -- see probe docstring re: CPU contention with probe6"}
    try:
        from fpylll import IntegerMatrix, LLL, BKZ, FPLLL

        seed = int(
            np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1)
        )
        FPLLL.set_random_seed(seed)
        result["seed_used"] = seed

        import os
        strategies_path = "/usr/share/libfplll8/strategies/default.json"
        if not os.path.exists(strategies_path):
            strategies_path = BKZ.DEFAULT_STRATEGY

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
        t0 = time.time()
        LLL.reduction(A)
        result["outer_lll_reduction_elapsed_seconds"] = time.time() - t0

        par = BKZ.Param(block_size=beta, strategies=strategies_path, flags=BKZ.AUTO_ABORT)
        t1 = time.time()
        BKZ.reduction(A, par)  # <-- the free function, float_type=None (automatic),
                                 #     NOT the BKZReduction class
        result["bkz_reduction_free_function_elapsed_seconds"] = time.time() - t1
        result["status"] = "COMPLETED"
    except Exception as exc:  # noqa: BLE001
        import traceback
        result["status"] = "ERROR"
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["traceback"] = traceback.format_exc()

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    d = int(sys.argv[1]) if len(sys.argv) > 1 else 224
    beta = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    out = sys.argv[3] if len(sys.argv) > 3 else "probe7_result.json"
    run(d, beta, out)
