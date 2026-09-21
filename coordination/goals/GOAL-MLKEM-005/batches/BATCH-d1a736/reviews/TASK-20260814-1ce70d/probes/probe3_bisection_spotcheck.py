#!/usr/bin/env python3
"""
TASK-20260814-1ce70d (Validator) -- probe3: independently spot-check the
reported bisection outcome at the isolated-LLL-step level, on the same
(d=256, beta=40) instance stage0_v2_feasibility.py's own bisect_precision()
used.

Completion-gate requirement: "confirm the reported minimum precision itself
succeeds and one lower value fails, at the isolated-LLL-step level, on the
same (d=256, beta=40) instance."

Reported (bisection_results.json): 64 bits -> ERROR ('infinite loop in
babai'); 65 bits -> COMPLETED (0.0025s). This probe is a FRESH, INDEPENDENT
implementation of the isolated-LLL-step construction (not an import of
stage0_v2_feasibility.py), matching the exact shape it documents:
  FPLLL.set_precision(N) called BEFORE GSO.Mat construction
  GSO.Mat(A, float_type="mpfr")   -- no flags=GSO.ROW_EXPO
  M.update_gso()
  LLL.Reduction(M, flags=LLL.DEFAULT)
  lll_obj() called directly (NOT wrapped in BKZReduction)
Same seed formula, SEED_ROOT=715923, (d, beta, arm_index, draw_index) = (256, 40, 0, 0).
"""
import json
import time

import numpy as np
from fpylll import IntegerMatrix, LLL, FPLLL, GSO

SEED_ROOT = 715923
D = 256
BETA = 40


def run_trial(mpfr_bits):
    seed = int(np.random.default_rng([SEED_ROOT, 0, D, BETA, 0, 0]).integers(0, 2**31 - 1))
    FPLLL.set_random_seed(seed)
    result = {"mpfr_bits": mpfr_bits, "seed_used": seed}
    try:
        A = IntegerMatrix.random(D, "qary", k=D // 2, q=3329)
        t0 = time.time()
        LLL.reduction(A)
        result["outer_lll_reduction_elapsed_seconds"] = time.time() - t0

        FPLLL.set_precision(mpfr_bits)
        M = GSO.Mat(A, float_type="mpfr")
        M.update_gso()
        lll_obj = LLL.Reduction(M, flags=LLL.DEFAULT)

        t1 = time.time()
        lll_obj()
        result["inner_lll_obj_elapsed_seconds"] = time.time() - t1
        result["status"] = "COMPLETED"
        FPLLL.set_precision(53)
    except Exception as exc:  # noqa: BLE001
        result["status"] = "ERROR"
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        try:
            FPLLL.set_precision(53)
        except Exception:
            pass
    return result


def main():
    out = {"seed_root": SEED_ROOT, "d": D, "beta": BETA, "trials": []}

    print("Trial: mpfr_bits=64 (reported ERROR / 'infinite loop in babai')", flush=True)
    t64 = run_trial(64)
    print(json.dumps(t64, indent=2), flush=True)
    out["trials"].append(t64)

    print("Trial: mpfr_bits=65 (reported minimum adequate precision, COMPLETED)", flush=True)
    t65 = run_trial(65)
    print(json.dumps(t65, indent=2), flush=True)
    out["trials"].append(t65)

    out["reproduces_reported_boundary"] = (
        t64["status"] == "ERROR" and "infinite loop in babai" in t64.get("error", "")
        and t65["status"] == "COMPLETED"
    )
    out["seed_matches_producer_bisection_results_json"] = (
        t64["seed_used"] == 1398073216 and t65["seed_used"] == 1398073216
    )

    print(json.dumps({"reproduces_reported_boundary": out["reproduces_reported_boundary"],
                       "seed_matches_producer_bisection_results_json": out["seed_matches_producer_bisection_results_json"]}, indent=2))
    with open("probe3_bisection_spotcheck_output.json", "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
