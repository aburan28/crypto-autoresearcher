#!/usr/bin/env python3
"""
Independent Validator probe: characterize the DIMENSION dependence of the
'infinite loop in babai' failure found in probe_reproduce_cell.py /
probe_native_bkz.py, using the fastest available reproduction path (the
NATIVE C++ BKZ.reduction() convenience function, block_size=10 fixed and
cheap, NO redundant pre-LLL step -- BKZ.reduction's own internal LLL
handles that) at a range of d values between the toy-floor sweep's own
d<=20 (which never failed) and the main grid's d=256 (which always
failed), on the SAME q=3329 'qary' k=d//2 random-lattice construction
PREREG-8/stage0_feasibility.py both use.

This is a NEW measurement this task's own scope did not run (it tested
exactly the 6 (d,beta) main-grid cells and separately d<=20 toy points),
included here because it materially changes what a follow-up task should
try first (a narrower failing-dimension boundary vs. "d=256 is already
inside the failing region with no cheaper diagnostic available").

Usage: python3 probe_dimension_sweep.py
"""
import json
import time

import numpy as np

SEED_ROOT = 715923
DS = [32, 48, 64, 96, 128, 160, 192, 224]
BETA = 10


def try_d(d, beta):
    from fpylll import IntegerMatrix, BKZ, FPLLL
    import os

    strategies_path = "/usr/share/libfplll8/strategies/default.json"
    if not os.path.exists(strategies_path):
        strategies_path = BKZ.DEFAULT_STRATEGY

    seed = int(np.random.default_rng([SEED_ROOT, 0, d, beta, 99, 0]).integers(0, 2 ** 31 - 1))
    FPLLL.set_random_seed(seed)
    A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
    par = BKZ.Param(block_size=beta, strategies=strategies_path, flags=BKZ.AUTO_ABORT)
    t0 = time.time()
    out = {"d": d, "beta": beta, "seed_used": seed}
    try:
        BKZ.reduction(A, par)
        out["status"] = "COMPLETED"
        out["elapsed_seconds"] = time.time() - t0
    except Exception as exc:
        out["status"] = "ERROR"
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        out["elapsed_seconds"] = time.time() - t0
    return out


def main():
    results = []
    for d in DS:
        r = try_d(d, BETA)
        print(json.dumps(r), flush=True)
        results.append(r)
    with open("probe_dimension_sweep_results.json", "w") as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == "__main__":
    main()
