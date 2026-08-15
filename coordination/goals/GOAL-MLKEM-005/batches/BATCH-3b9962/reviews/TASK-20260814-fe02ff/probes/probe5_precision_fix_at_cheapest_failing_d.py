#!/usr/bin/env python3
"""
RED TEAM PROBE 5 -- at d=224 (probe4's own finding: the smallest dimension
in the {32,64,96,128,160,192,224,256} scan at which BKZReduction's default
internal double-precision GSO/LLL step fails -- d=192 succeeds in ~11s,
d=224 fails), test whether an EXPLICITLY higher-precision GSO.Mat
(float_type="mpfr", precision set via FPLLL.set_precision BEFORE
construction, matching fpylll's own GSO.Mat docstring instructions, no
GSO.ROW_EXPO flag since documented incompatible with mpfr) resolves the
"infinite loop in babai" failure that stage0_feasibility.py's own default
(raw IntegerMatrix -> BKZReduction, implicit float_type="double") hits.

This directly tests the producer's own environment.json claim:
  "float_type_mpfr: FAILED -- identical ReductionError('infinite loop in
   babai'), effectively instantly. Rules out a simple default-precision
   explanation."
against this session's own independently-constructed, correctly-configured
mpfr GSO (the producer's own mpfr diagnostic script is NOT an artifact in
this task's write_scope or anywhere else recoverable -- it is described as
"out-of-band", so this probe cannot inspect what code path the producer's
own mpfr test actually exercised; it can only test a CORRECTLY-CONSTRUCTED
mpfr path itself and compare outcomes).
"""
import json
import sys
import time

import numpy as np

SEED_ROOT = 715923


def run(d, beta, mpfr_bits, out_path):
    result = {"d": d, "beta": beta, "mpfr_bits": mpfr_bits}
    try:
        from fpylll import IntegerMatrix, LLL, FPLLL, GSO

        seed = int(
            np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1)
        )
        FPLLL.set_random_seed(seed)
        result["seed_used"] = seed

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
        t0 = time.time()
        LLL.reduction(A)
        result["outer_lll_reduction_elapsed_seconds"] = time.time() - t0

        FPLLL.set_precision(mpfr_bits)
        M = GSO.Mat(A, float_type="mpfr")  # no ROW_EXPO -- documented incompatible w/ mpfr
        M.update_gso()
        result["gso_float_type_used"] = M.float_type
        lll_obj = LLL.Reduction(M, flags=LLL.DEFAULT)

        t1 = time.time()
        lll_obj()
        result["inner_lll_obj_elapsed_seconds"] = time.time() - t1
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
    mpfr_bits = int(sys.argv[3]) if len(sys.argv) > 3 else 212
    out = sys.argv[4] if len(sys.argv) > 4 else "probe5_result.json"
    run(d, beta, mpfr_bits, out)
