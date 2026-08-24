#!/usr/bin/env python3
"""
RED TEAM PROBE 4 -- find the smallest dimension d at which BKZReduction's
own internal (default float_type="double", flags=GSO.ROW_EXPO) LLL step
fails with "infinite loop in babai" on this class of instance
(IntegerMatrix.random(d, "qary", k=d//2, q=3329), beta_toy analog fixed at
40 to match the producer's own cheapest failing main-grid cell), scanning
DOWN from d=256 -- so a smaller, cheaper reproduction can be used for
follow-up precision-fix probes instead of re-paying d=256's own ~66-70s
LLL.reduction cost every time.

Same isolated internal-only construction as probe3 (no BKZ.Param, no
strategies file -- already shown irrelevant by probe3).
"""
import json
import sys
import time

import numpy as np

SEED_ROOT = 715923


def try_d(d, beta):
    from fpylll import IntegerMatrix, LLL, FPLLL, GSO

    seed = int(
        np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1)
    )
    FPLLL.set_random_seed(seed)

    A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
    t0 = time.time()
    LLL.reduction(A)
    lll_elapsed = time.time() - t0

    M = GSO.Mat(A, flags=GSO.ROW_EXPO)
    lll_obj = LLL.Reduction(M, flags=LLL.DEFAULT)

    t1 = time.time()
    lll_obj()
    elapsed = time.time() - t1
    return {
        "d": d, "beta": beta, "seed_used": seed,
        "lll_elapsed_seconds": lll_elapsed,
        "status": "COMPLETED",
        "lll_obj_call_elapsed_seconds": elapsed,
    }


def main(out_path, ds):
    results = []
    for d in ds:
        beta = 40
        entry = {"d": d, "beta": beta}
        try:
            entry = try_d(d, beta)
        except Exception as exc:  # noqa: BLE001
            entry["status"] = "ERROR"
            entry["error"] = "%s: %s" % (type(exc).__name__, exc)
        print(json.dumps(entry), flush=True)
        results.append(entry)
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
    return results


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "probe4_result.json"
    ds = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else [32, 64, 96, 128, 160, 192, 224, 256]
    main(out, ds)
