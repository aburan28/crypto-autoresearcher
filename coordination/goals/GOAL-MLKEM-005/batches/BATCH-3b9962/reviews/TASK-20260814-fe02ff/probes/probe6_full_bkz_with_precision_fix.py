#!/usr/bin/env python3
"""
RED TEAM PROBE 6 -- at d=256, beta=40 (an ACTUAL PREREG-8 main-grid Stage-0
cell, the producer's own fastest-failing one), test whether a FULL
bkz(par, tracer=True) call -- not merely the internal LLL step probes 3/5
isolated -- completes under an explicitly higher-precision (mpfr, 212-bit)
GSO.Mat, using the SAME strategies file (the OS package path, DEV-1) and
the SAME BKZ.Param(block_size=40, flags=BKZ.AUTO_ABORT) the producer's own
worker_main_cell used.

Bounded at a cap this probe itself enforces (argv[3], default 2400s) --
narrower than PREREG-8's own PER_BASIS_FEASIBILITY_CAP=3600s, to preserve
this red-team task's own overall 5400s wall-clock budget for the rest of
its review. A cap here is a probe-budget decision, NOT a claim about
Stage-0's own cap (see the report for that distinction).
"""
import json
import os
import sys
import time

import numpy as np

SEED_ROOT = 715923


def run(d, beta, mpfr_bits, out_path):
    result = {"d": d, "beta": beta, "mpfr_bits": mpfr_bits}
    try:
        from fpylll import IntegerMatrix, LLL, BKZ, FPLLL, GSO
        from fpylll.algorithms.bkz2 import BKZReduction

        seed = int(
            np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1)
        )
        FPLLL.set_random_seed(seed)
        result["seed_used"] = seed

        strategies_path = "/usr/share/libfplll8/strategies/default.json"
        if not os.path.exists(strategies_path):
            strategies_path = BKZ.DEFAULT_STRATEGY
        result["strategies_file_used"] = strategies_path

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
        t0 = time.time()
        LLL.reduction(A)
        result["outer_lll_reduction_elapsed_seconds"] = time.time() - t0

        FPLLL.set_precision(mpfr_bits)
        M = GSO.Mat(A, float_type="mpfr")
        M.update_gso()
        result["gso_float_type_used"] = M.float_type

        par = BKZ.Param(block_size=beta, strategies=strategies_path, flags=BKZ.AUTO_ABORT)
        bkz = BKZReduction(M)  # pass the GSO.Mat -- BKZReduction reuses it, does not rebuild

        t1 = time.time()
        bkz(par, tracer=True)
        bkz_elapsed = time.time() - t1

        n_tours = None
        try:
            if bkz.trace is not None:
                n_tours = sum(1 for child in bkz.trace.children if child.label[0] == "tour")
        except Exception:
            n_tours = None

        log_det = M.get_log_det(0, d)
        r0 = M.get_r(0, 0)
        first_vec_norm = float(r0) ** 0.5
        det_l_pow_1_over_d = np.exp(float(log_det) / d)
        delta_0 = (first_vec_norm / det_l_pow_1_over_d) ** (1.0 / d)

        result.update({
            "status": "COMPLETED",
            "bkz_elapsed_seconds": bkz_elapsed,
            "n_tours": n_tours,
            "delta_0_root_hermite_factor": float(delta_0),
        })
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
    mpfr_bits = int(sys.argv[3]) if len(sys.argv) > 3 else 212
    out = sys.argv[4] if len(sys.argv) > 4 else "probe6_result.json"
    run(d, beta, mpfr_bits, out)
