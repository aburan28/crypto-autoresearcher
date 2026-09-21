#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v5 (BATCH-008) -- PART A required validation.

Implements specification_v5.yaml inputs.gd11_fix_v5's two REQUIRED
VALIDATION parts, both independent of any real run's data:

  (i)  gd11_standalone_regression_test: reproduces RT-BATCH-007.md's own two
       named anomaly cases (N=324/repeat=3, N=611/repeat=6, both confirmed
       anomalous under the ORIGINAL guard) and confirms
       ols_hardened.ols_loglog_fit_v2 correctly raises ValueError on both.

  (ii) bootstrap_gap_ci_v2_regression_test: PF-10 FIX APPLIED -- calls
       ols_hardened.bootstrap_gap_ci_v2 (not only the standalone function)
       with N_list = [N]*n (n identical copies of the single anomalous N
       value, guaranteeing EVERY resample draw is degenerate regardless of
       the RNG's specific draw) and confirms the degenerate resamples are
       correctly discarded from the returned CI (gaps == [], lo == hi ==
       None), contrasted directly against descent_hitting_time.bootstrap_gap_ci
       (the frozen, UNCHANGED original) run on the identical inputs, which
       does NOT discard them -- the direct, code-verified evidence that the
       fix actually reaches the call path it exists to protect.

Both tests use synthetic data hand-constructed in this file; neither reads
any prior run's raw-result.json (same discipline as v4's own
synthetic_self_test_v4 -- see source_access_log.yaml files_read_this_run).

descent_hitting_time.py (dht) and calibration_synthetic.py are imported
UNCHANGED, by reference, for comparison only -- never modified, never
re-implemented.
"""

import json
import os
import random
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
sys.path.insert(0, os.path.join(_THIS_DIR, "..", "..", "EXP-SSIQ-58b642",
                                 "implementation"))

# Import order matters: descent_hitting_time.py imports calibration_synthetic
# at module scope, and calibration_synthetic.py does
# `from descent_hitting_time import ols_loglog_fit, ...` at ITS module scope
# -- a genuine circular import in the frozen, unchanged pair of files.
# Importing calibration_synthetic FIRST in this process lets Python finish
# loading descent_hitting_time (defining ols_loglog_fit) before
# calibration_synthetic's own `from descent_hitting_time import ...` line
# executes; this is the same order compute_delta_e.py (EXP-SSIQ-a85692's own
# frozen, unchanged v1 script) already uses. Neither file is modified here.
import calibration_synthetic as cal  # noqa: E402,F401  (import-order fix only)
import descent_hitting_time as dht  # noqa: E402  (FROZEN, UNCHANGED)
import ols_hardened as oh  # noqa: E402  (THIS amendment's new module)

GD11_NAMED_ANOMALY_CASES = [
    {"label": "N324_repeat3", "N": 324, "repeat": 3,
     "note": ("prime 3889's real graph size (N); RT-BATCH-007.md Front 4's "
              "own reproduction grid names N=324 anomalous at n=3, 6, 7, 8")},
    {"label": "N611_repeat6", "N": 611, "repeat": 6,
     "note": ("prime 7333's real graph size (N); RT-BATCH-007.md Front 4's "
              "own reproduction grid names N=611 anomalous at n>=5, and its "
              "gamma=0.5 spurious-nonzero-gamma example uses exactly this "
              "(N, repeat) pair with y=36.0 (prime 7333's real "
              "random_median)")},
]


def run_gd11_standalone_regression_test():
    """(i) Standalone-function regression test. For each named anomaly
    case, construct N_list = [N]*repeat and a synthetic y_list (independent
    of any real run's data, but for the N=611/repeat=6 case using y=36.0
    throughout to directly reproduce RT-BATCH-007.md's own disclosed
    genuinely-wrong-nonzero-gamma example), and confirm:
      (a) the ORIGINAL, unchanged dht.ols_loglog_fit does NOT raise
          ValueError on this input (confirming it is genuinely
          "known-anomalous under the ORIGINAL guard", not merely asserted);
      (b) the HARDENED ols_hardened.ols_loglog_fit_v2 DOES raise ValueError
          on the identical input.
    """
    cases = []
    for case in GD11_NAMED_ANOMALY_CASES:
        N_list = [case["N"]] * case["repeat"]
        if case["label"] == "N611_repeat6":
            # Reproduces RT-BATCH-007.md Front 4's own disclosed example
            # exactly: y=36.0 is prime 7333's real random_median
            # (RUN-SSIQ-a85692-b raw-result.json descent_metrics.per_prime
            # ["7333"]["random_median"] == 36.0), used here only as a
            # synthetic numeric literal, not read from that file.
            y_list = [36.0] * case["repeat"]
        else:
            y_list = [float(10 * (i + 1)) for i in range(case["repeat"])]

        original_raised = False
        original_error = None
        original_gamma = None
        try:
            fit = dht.ols_loglog_fit(N_list, y_list)
            original_gamma = fit["gamma"]
        except ValueError as e:
            original_raised = True
            original_error = str(e)

        hardened_raised = False
        hardened_error = None
        try:
            oh.ols_loglog_fit_v2(N_list, y_list)
        except ValueError as e:
            hardened_raised = True
            hardened_error = str(e)

        known_anomalous_under_original_guard = not original_raised
        test_pass = bool(hardened_raised and known_anomalous_under_original_guard)

        cases.append({
            "label": case["label"],
            "note": case["note"],
            "N": case["N"], "repeat": case["repeat"],
            "N_list": N_list, "y_list": y_list,
            "original_dht_ols_loglog_fit": {
                "raised_valueerror": original_raised,
                "error_message": original_error,
                "spurious_gamma_if_not_raised": original_gamma,
            },
            "known_anomalous_under_original_guard": known_anomalous_under_original_guard,
            "hardened_ols_loglog_fit_v2": {
                "raised_valueerror": hardened_raised,
                "error_message": hardened_error,
            },
            "case_pass": test_pass,
        })

    all_pass = all(c["case_pass"] for c in cases)
    return {
        "test_id": "gd11_standalone_regression_test",
        "spec_reference": "specification_v5.yaml inputs.gd11_fix_v5 REQUIRED VALIDATION (i)",
        "purpose": (
            "Reproduce RT-BATCH-007.md's own two named anomaly cases "
            "(N=324/repeat=3, N=611/repeat=6) and confirm "
            "ols_loglog_fit_v2 correctly raises ValueError on both, while "
            "independently re-confirming (not merely re-asserting) that "
            "both cases are genuinely anomalous under the frozen, "
            "unchanged original guard."
        ),
        "cases": cases,
        "all_cases_pass": all_pass,
    }


def run_bootstrap_gap_ci_v2_regression_test(n_boot=2000, rng_seed=20260806):
    """(ii) bootstrap_gap_ci_v2 regression test. PF-10 FIX APPLIED: N_list
    = [N]*n (n identical copies of the single anomalous N value) so that
    EVERY resample draw is degenerate regardless of the RNG's specific
    draw -- the cheapest, most direct construction (round-2 pre-freeze
    review, independently confirmed correct against the actual guard).

    Runs BOTH ols_hardened.bootstrap_gap_ci_v2 (this amendment's fix) and
    the frozen, UNCHANGED dht.bootstrap_gap_ci (the original) on the
    IDENTICAL inputs and RNG seed/state, to show directly that the
    hardened version discards every degenerate resample (gaps == [], lo ==
    hi == None) while the original does not (systematically accepts a
    spuriously-computed gamma into its gap distribution on every degenerate
    draw, per GD-11 / RT-BATCH-007.md Front 4)."""
    cases = [
        {
            "label": "N324_n3",
            "N": 324, "n": 3,
            "median_greedy_list": [10.0, 20.0, 30.0],
            "median_random_list": [15.0, 45.0, 90.0],
            "note": "prime 3889's real N; arbitrary synthetic medians, independent of any real run",
        },
        {
            "label": "N611_n6",
            "N": 611, "n": 6,
            "median_greedy_list": [24.0] * 6,
            "median_random_list": [36.0] * 6,
            "note": (
                "prime 7333's real N; median_random_list held constant at "
                "36.0 (prime 7333's real random_median, used here as a "
                "synthetic numeric literal) to directly reproduce "
                "RT-BATCH-007.md's disclosed genuinely-wrong-nonzero-gamma "
                "(0.5) example inside the bootstrap resampling loop, not "
                "only at the standalone-function level; median_greedy_list "
                "held constant at a DIFFERENT value (24.0) so the spurious "
                "per-resample gap (fr.gamma - fg.gamma) is a genuinely "
                "nonzero, materially wrong number under the original guard "
                "rather than cancelling to 0.0 (which the identical-list "
                "construction would have produced, per PF-10's own "
                "'plausible-looking but entirely spurious slope' framing)"
            ),
        },
    ]

    results = []
    for c in cases:
        N_list = [c["N"]] * c["n"]

        rng_hardened = random.Random(rng_seed)
        lo_v2, hi_v2, gaps_v2 = oh.bootstrap_gap_ci_v2(
            N_list, c["median_greedy_list"], c["median_random_list"],
            rng_hardened, n_boot=n_boot)

        rng_original = random.Random(rng_seed)
        lo_orig, hi_orig, gaps_orig = dht.bootstrap_gap_ci(
            N_list, c["median_greedy_list"], c["median_random_list"],
            rng_original, n_boot=n_boot)

        hardened_discarded_all = bool(
            lo_v2 is None and hi_v2 is None and len(gaps_v2) == 0)
        original_polluted = bool(len(gaps_orig) > 0)

        results.append({
            "label": c["label"],
            "note": c["note"],
            "N": c["N"], "n": c["n"], "n_boot": n_boot, "rng_seed": rng_seed,
            "N_list": N_list,
            "median_greedy_list": c["median_greedy_list"],
            "median_random_list": c["median_random_list"],
            "every_resample_degenerate_by_construction": (
                "N_list is constant (all entries == %d), so EVERY bootstrap "
                "resample draws Nb == [%d]*%d regardless of which indices "
                "the RNG selects -- this construction guarantees full "
                "coverage of the degenerate case, per PF-10." % (c["N"], c["N"], c["n"])
            ),
            "hardened_bootstrap_gap_ci_v2": {
                "lo": lo_v2, "hi": hi_v2, "n_valid_draws": len(gaps_v2),
                "n_boot": n_boot,
            },
            "original_dht_bootstrap_gap_ci": {
                "lo": lo_orig, "hi": hi_orig, "n_valid_draws": len(gaps_orig),
                "n_boot": n_boot,
                "sample_spurious_gaps": gaps_orig[:5],
            },
            "hardened_correctly_discarded_all_degenerate_resamples": hardened_discarded_all,
            "original_silently_accepted_spurious_gaps": original_polluted,
            "case_pass": bool(hardened_discarded_all),
        })

    all_pass = all(r["case_pass"] for r in results)
    return {
        "test_id": "bootstrap_gap_ci_v2_regression_test",
        "spec_reference": "specification_v5.yaml inputs.gd11_fix_v5 REQUIRED VALIDATION (ii), PF-10 FIX APPLIED",
        "purpose": (
            "Direct, code-verified evidence that GD-11's fix reaches the "
            "call path it exists to protect: bootstrap_gap_ci_v2's own "
            "resampling loop, not merely the standalone ols_loglog_fit_v2 "
            "function in isolation. Confirms a degenerate resample is "
            "correctly discarded from the returned CI (not silently "
            "contributing a spurious gap value), contrasted directly "
            "against the frozen, unchanged original on identical inputs."
        ),
        "cases": results,
        "all_cases_pass": all_pass,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--standalone-out", required=True)
    ap.add_argument("--bootstrap-out", required=True)
    args = ap.parse_args()

    standalone = run_gd11_standalone_regression_test()
    bootstrap = run_bootstrap_gap_ci_v2_regression_test()

    with open(args.standalone_out, "w") as fh:
        json.dump(standalone, fh, indent=1, sort_keys=True, default=str)
    with open(args.bootstrap_out, "w") as fh:
        json.dump(bootstrap, fh, indent=1, sort_keys=True, default=str)

    print("gd11_standalone_regression_test all_cases_pass = %s"
          % standalone["all_cases_pass"])
    print("bootstrap_gap_ci_v2_regression_test all_cases_pass = %s"
          % bootstrap["all_cases_pass"])
    return 0 if (standalone["all_cases_pass"] and bootstrap["all_cases_pass"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
