#!/usr/bin/env python3
"""
Independent Validator probe: reproduce TASK-20260814-ffd791's own
stage0_feasibility.py::worker_main_cell EXACTLY (same construction, same
seed derivation) for a chosen (d, beta) cell, to confirm the reported
ReductionError('infinite loop in babai') is real and reproducible under
an INDEPENDENTLY WRITTEN invocation (not by importing the producer's
module -- this file re-implements worker_main_cell's own logic from
prereg.md section 1/2's own text and the producer's own writeup, matching
it exactly so the seed and construction are identical, then reports pass/
fail plus full traceback).

Usage: python3 probe_reproduce_cell.py <d> <beta>
"""
import json
import sys
import time
import traceback

import numpy as np

SEED_ROOT = 715923


def main(d, beta):
    result = {"d": d, "beta": beta}
    from fpylll import IntegerMatrix, LLL, BKZ, FPLLL
    from fpylll.algorithms.bkz2 import BKZReduction

    seed = int(np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1))
    FPLLL.set_random_seed(seed)
    result["seed_used"] = seed

    strategies_path = "/usr/share/libfplll8/strategies/default.json"
    import os
    if not os.path.exists(strategies_path):
        strategies_path = BKZ.DEFAULT_STRATEGY

    A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
    t0 = time.time()
    LLL.reduction(A)
    lll_elapsed = time.time() - t0

    par = BKZ.Param(block_size=beta, strategies=strategies_path, flags=BKZ.AUTO_ABORT)
    bkz = BKZReduction(A)
    t1 = time.time()
    try:
        bkz(par, tracer=True)
        bkz_elapsed = time.time() - t1
        result["status"] = "COMPLETED"
        result["bkz_elapsed_seconds"] = bkz_elapsed
    except Exception as exc:
        bkz_elapsed = time.time() - t1
        result["status"] = "ERROR"
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["traceback"] = traceback.format_exc()
        result["bkz_elapsed_seconds"] = bkz_elapsed

    result["lll_elapsed_seconds"] = lll_elapsed
    result["total_elapsed_seconds"] = time.time() - t0
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    d = int(sys.argv[1])
    beta = int(sys.argv[2])
    out = main(d, beta)
    with open("probe_reproduce_cell_d%d_beta%d.json" % (d, beta), "w") as f:
        json.dump(out, f, indent=2)
