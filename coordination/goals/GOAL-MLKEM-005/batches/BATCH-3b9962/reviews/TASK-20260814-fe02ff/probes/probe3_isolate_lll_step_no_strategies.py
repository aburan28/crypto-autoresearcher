#!/usr/bin/env python3
"""
RED TEAM PROBE 3 -- isolate whether the "infinite loop in babai" failure
is caused by anything to do with BKZ.Param / the strategies file (DEV-1:
the OS-package strategies path /usr/share/libfplll8/strategies/default.json
substituted for the wheel's own baked-in, absent path), by reproducing
ONLY the internal call that actually fails --
fpylll.algorithms.bkz.BKZReduction.__call__'s own `self.lll_obj()` at
bkz.py line 123 -- with ZERO reference to BKZ.Param, block_size, or any
strategies file at all.

BKZReduction.__init__ source (read directly from this environment's
installed fpylll 0.6.4, /usr/local/lib/python3.11/dist-packages/fpylll/algorithms/bkz.py):

    elif isinstance(A, IntegerMatrix):
        L = None; M = None; A = A
    if M is None and L is None:
        LLL.reduction(A)              # <-- redundant re-run of LLL.reduction,
                                        #     harmless / idempotent
    self.A = A
    if M is None:
        self.M = GSO.Mat(A, flags=GSO.ROW_EXPO)     # float_type defaults to "double"
    else:
        self.M = M
    if L is None:
        self.lll_obj = LLL.Reduction(self.M, flags=LLL.DEFAULT)
    else:
        self.lll_obj = L

and __call__ (bkz.py line ~122-123):

    with tracer.context("lll"):
        self.lll_obj()

This probe constructs GSO.Mat(A, flags=GSO.ROW_EXPO) and
LLL.Reduction(M, flags=LLL.DEFAULT) EXACTLY as BKZReduction.__init__ does
internally when given a raw IntegerMatrix, and calls lll_obj() directly --
no BKZ.Param object is ever created, no strategies file is ever read or
referenced anywhere in this probe.

If the SAME ReductionError('infinite loop in babai') fires here, this is a
DIRECT, DECISIVE falsification of "the strategies-file substitution (DEV-1)
caused or contributed to the ReductionError": the failing call path
contains no strategies-file-dependent code whatsoever.
"""
import json
import sys
import time

import numpy as np

SEED_ROOT = 715923


def run(d, beta, out_path):
    result = {"d": d, "beta": beta, "strategies_file_referenced_anywhere": False}
    try:
        from fpylll import IntegerMatrix, LLL, FPLLL, GSO

        seed = int(
            np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1)
        )
        FPLLL.set_random_seed(seed)
        result["seed_used"] = seed

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
        t0 = time.time()
        LLL.reduction(A)  # same pre-reduction the producer's script performs (wrapper method)
        lll_elapsed = time.time() - t0
        result["lll_elapsed_seconds"] = lll_elapsed

        # Exact mirror of BKZReduction.__init__'s own internal construction
        # for the isinstance(A, IntegerMatrix) branch -- NO BKZ.Param, NO
        # strategies file, anywhere in this code path.
        M = GSO.Mat(A, flags=GSO.ROW_EXPO)
        result["internal_gso_float_type"] = M.float_type
        lll_obj = LLL.Reduction(M, flags=LLL.DEFAULT)

        t1 = time.time()
        lll_obj()  # <-- the exact call that fails inside BKZReduction.__call__
        elapsed = time.time() - t1
        result["status"] = "COMPLETED"
        result["lll_obj_call_elapsed_seconds"] = elapsed
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
    out = sys.argv[3] if len(sys.argv) > 3 else "probe3_result.json"
    run(d, beta, out)
