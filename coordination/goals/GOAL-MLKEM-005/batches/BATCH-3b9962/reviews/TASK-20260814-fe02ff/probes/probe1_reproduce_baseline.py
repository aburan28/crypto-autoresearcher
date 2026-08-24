#!/usr/bin/env python3
"""
RED TEAM PROBE 1 -- reproduce TASK-20260814-ffd791's own worker_main_cell
EXACTLY (same code path, same seed formula) at (d=256, beta=40), the
producer's own fastest-failing cell, to confirm:
  (a) the ReductionError is genuinely reproducible in THIS session
      (independent re-derivation, not merely re-reading the producer's
      JSON), and
  (b) the seed_used matches the producer's own reported seed_used=1398073216
      exactly, confirming SEED_ROOT=715923 / the default_rng([...]) formula
      was ACTUALLY used (not merely declared).

This is a byte-for-byte transcription of stage0_feasibility.py's own
worker_main_cell function body (read from the committed snapshot at
coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/tasks/TASK-20260814-ffd791/stage0_feasibility.py,
commit dc61fe376a7108b4dd58110f856db5c7589cde86), not a paraphrase.
"""
import json
import sys
import time

import numpy as np

SEED_ROOT = 715923


def run(d, beta, out_path):
    result = {"d": d, "beta": beta}
    try:
        from fpylll import IntegerMatrix, LLL, BKZ, FPLLL
        from fpylll.algorithms.bkz2 import BKZReduction

        seed = int(
            np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1)
        )
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
        result["lll_elapsed_seconds"] = lll_elapsed

        par = BKZ.Param(
            block_size=beta,
            strategies=strategies_path,
            flags=BKZ.AUTO_ABORT,
        )
        bkz = BKZReduction(A)
        t1 = time.time()
        bkz(par, tracer=True)
        bkz_elapsed = time.time() - t1
        result["status"] = "COMPLETED"
        result["bkz_elapsed_seconds"] = bkz_elapsed
    except Exception as exc:  # noqa: BLE001
        import traceback
        result["status"] = "ERROR"
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["traceback"] = traceback.format_exc()

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    d = int(sys.argv[1]) if len(sys.argv) > 1 else 256
    beta = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    out = sys.argv[3] if len(sys.argv) > 3 else "probe1_result.json"
    run(d, beta, out)
