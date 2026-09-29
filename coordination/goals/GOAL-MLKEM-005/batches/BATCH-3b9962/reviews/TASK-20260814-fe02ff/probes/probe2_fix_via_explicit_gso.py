#!/usr/bin/env python3
"""
RED TEAM PROBE 2 -- test whether BKZReduction's own HARDCODED internal
construction (float_type="double", flags=GSO.ROW_EXPO -- see
fpylll/algorithms/bkz.py BKZReduction.__init__, lines ~100-131 as read
from this environment's installed fpylll 0.6.4 source) is the actual
cause of the "infinite loop in babai" ReductionError, as opposed to a
genuine unfixable fpylll/fplll library limitation.

BKZReduction.__init__, when passed a raw IntegerMatrix (exactly what
stage0_feasibility.py's worker_main_cell does), ALWAYS builds:

    self.M = GSO.Mat(A, flags=GSO.ROW_EXPO)          # float_type NOT passed
                                                        # -> defaults to "double"
    self.lll_obj = LLL.Reduction(self.M, flags=LLL.DEFAULT)

with NO precision escalation whatsoever, REGARDLESS of what float_type any
earlier, separate LLL.reduction(A) call used. This is DIFFERENT from the
top-level LLL.reduction() free function, whose method=None default resolves
to fplll's own "wrapper" strategy (auto-escalating float_type), which is
almost certainly WHY the standalone LLL.reduction(A) call in
worker_main_cell succeeds (see probe1's own 66s "lll_elapsed_seconds") while
BKZReduction's internal, un-escalated LLL call fails immediately after.

fpylll's own GSO.Mat docstring (from `help(GSO.Mat.__init__)` in this
environment) states explicitly:

    "If float_type='mpfr' set precision with set_precision() before
    constructing this object and do not change the precision during the
    lifetime of this object."

    "[GSO.ROW_EXPO] ... works only with float_type='double' and
    float_type='long double'. It is useless and must not be used for
    float_type='dpe', float_type='dd', float_type='qd' or float_type=mpfr_t."

This probe constructs the GSO.Mat / LLL.Reduction pair EXPLICITLY, with a
genuinely elevated precision (mpfr, 212 bits, set via FPLLL.set_precision
BEFORE construction, and WITHOUT the ROW_EXPO flag since it is documented
incompatible with mpfr), and passes THAT GSO.Mat object into BKZReduction
(which takes the isinstance(A, GSO.Mat) branch in its own __init__ and does
NOT rebuild its own double-precision GSO -- see bkz.py source read above),
on the SAME (d, beta, seed) instance probe1 just reproduced failing.

If this succeeds where the raw-IntegerMatrix pattern fails, it is a
significant, concrete finding: the reported "infinite loop in babai" is
NOT necessarily an unfixable fpylll/fplll library defect independent of
usage -- it is (at least in part) explained by stage0_feasibility.py's own
choice to hand BKZReduction a raw IntegerMatrix (implicit float_type=
"double", no escalation) rather than a manually-constructed
higher-precision GSO.Mat, which is fpylll's own documented mechanism for
this exact situation.

This is NOT a claim that this makes Stage-1-grade BKZ at (d=256..512,
beta=40..70) fast or feasible -- mpfr at 212 bits is far slower than
double per-operation. It is a claim about ROOT CAUSE ATTRIBUTION ONLY:
producer-script default-precision choice vs. genuine unfixable library
bug -- which is exactly the distinction the task handoff asks this probe
to make.
"""
import json
import sys
import time

import numpy as np

SEED_ROOT = 715923


def run(d, beta, mpfr_bits, cap_seconds, out_path):
    result = {"d": d, "beta": beta, "mpfr_bits": mpfr_bits, "cap_seconds": cap_seconds}
    try:
        from fpylll import IntegerMatrix, LLL, BKZ, FPLLL, GSO
        from fpylll.algorithms.bkz2 import BKZReduction

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
        LLL.reduction(A)  # same pre-reduction step the producer's script performs
        lll_elapsed = time.time() - t0
        result["lll_elapsed_seconds"] = lll_elapsed

        # --- THE DIFFERENCE FROM stage0_feasibility.py: explicit high-precision GSO ---
        FPLLL.set_precision(mpfr_bits)
        M = GSO.Mat(A, float_type="mpfr")  # NOTE: no flags=GSO.ROW_EXPO -- documented
                                            # incompatible with mpfr
        M.update_gso()
        lll_obj = LLL.Reduction(M, flags=LLL.DEFAULT)
        result["explicit_gso_float_type"] = M.float_type

        par = BKZ.Param(
            block_size=beta,
            strategies=strategies_path,
            flags=BKZ.AUTO_ABORT,
        )
        bkz = BKZReduction(M)  # <-- pass the GSO.Mat directly, not the raw IntegerMatrix
        result["bkz_took_gso_branch"] = (bkz.M is M)

        t1 = time.time()
        # Hard wall-clock self-check inside this single-process probe: if this
        # runs past cap_seconds we abandon it explicitly (recorded as TIMEOUT,
        # never silently left running) -- BKZReduction itself has no built-in
        # wall-clock cap, so this is enforced by the calling harness
        # (run_probe2.sh) via SIGALRM/timeout, not inside this function.
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
    mpfr_bits = int(sys.argv[3]) if len(sys.argv) > 3 else 212
    cap_seconds = int(sys.argv[4]) if len(sys.argv) > 4 else 600
    out = sys.argv[5] if len(sys.argv) > 5 else "probe2_result.json"
    run(d, beta, mpfr_bits, cap_seconds, out)
