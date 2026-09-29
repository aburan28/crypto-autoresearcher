#!/usr/bin/env python3
"""
Same construction as probe_dimension_sweep.py's try_d(), but run as a
single, FRESH, isolated OS process per invocation (no shared process state
across d values) -- needed because probe_dimension_sweep.py's own combined
run showed 'terminate called recursively' at d=224, run in the SAME
process as an earlier d=192 std::terminate/abort event, raising a concern
that process state was already corrupted for the later measurement. This
script re-measures individual d values, each in complete process
isolation, to confirm the dimension boundary cleanly.

Usage: python3 probe_dimension_single.py <d> [beta]
"""
import json
import sys
import time

import numpy as np

SEED_ROOT = 715923


def main(d, beta):
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
    print(json.dumps(out))
    return out


if __name__ == "__main__":
    d = int(sys.argv[1])
    beta = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    main(d, beta)
