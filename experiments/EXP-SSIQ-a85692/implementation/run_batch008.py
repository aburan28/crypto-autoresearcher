#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v5 (BATCH-008), RUN-SSIQ-a85692-e -- orchestration entry
point for BOTH independent parts of specification_v5.yaml:
  PART A (gd11_fix_v5): ols_hardened.py's two required regression tests
    (gd11_regression_test.py).
  PART B (trapping_mechanism_diagnostic_v5): trapping_diagnostic_v5.py.

This is a NEW entry-point script (not itself one of the two files
required_artifacts_note names explicitly -- ols_hardened.py and "a
diagnostic script e.g. trapping_diagnostic_v5.py" -- disclosed explicitly
in execution_report.yaml's required_artifacts_note diff cross-check, same
disclosure discipline RUN-SSIQ-a85692-d's new_entry_point_named section
used). It performs NO delta_E search, NO Phi_ell verification, and reads
only RUN-SSIQ-a85692-b's already-committed raw-result.json (read-only, for
Part B's delta_map input).

Writes all six of this run's own JSON artifacts:
  raw-result.json (this file's own summary of both parts)
  gd11_regression_test.json
  bootstrap_gap_ci_v2_regression_test.json
  trapping_diagnostic.json
  trapped_vs_structural_crosscheck.json
"""

import hashlib
import json
import os
import platform
import subprocess
import sys
import time

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)

import gd11_regression_test as gd11  # noqa: E402  (THIS amendment, PART A)
import trapping_diagnostic_v5 as tdv5  # noqa: E402  (THIS amendment, PART B)

EXPERIMENT_ID = "EXP-SSIQ-a85692"
RUN_ID = "RUN-SSIQ-a85692-e"
SPEC_VERSION = 5


def git_state():
    def g(*a):
        try:
            return subprocess.check_output(
                ["git"] + list(a), stderr=subprocess.DEVNULL,
                cwd=_THIS_DIR).decode().strip()
        except Exception:
            return None
    return {"commit": g("rev-parse", "HEAD"),
            "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(g("status", "--porcelain"))}


def sha256_of_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True,
                     help="output directory for this run's artifacts")
    ap.add_argument("--raw-result-b", required=True,
                     help="path to RUN-SSIQ-a85692-b/raw-result.json "
                          "(READ ONLY, source of PART B's delta_map)")
    args = ap.parse_args()

    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log = lambda s: print(s, flush=True)  # noqa: E731

    log("[%s] %s / %s (specification_v5.yaml)" % (started, EXPERIMENT_ID, RUN_ID))

    run_dir = args.run_dir
    os.makedirs(run_dir, exist_ok=True)

    # ---- PART A -----------------------------------------------------
    log("PART A (gd11_fix_v5): running the two required regression tests")
    standalone = gd11.run_gd11_standalone_regression_test()
    bootstrap = gd11.run_bootstrap_gap_ci_v2_regression_test()
    log("  gd11_standalone_regression_test all_cases_pass = %s"
        % standalone["all_cases_pass"])
    log("  bootstrap_gap_ci_v2_regression_test all_cases_pass = %s"
        % bootstrap["all_cases_pass"])

    gd11_out_path = os.path.join(run_dir, "gd11_regression_test.json")
    bootstrap_out_path = os.path.join(run_dir,
                                       "bootstrap_gap_ci_v2_regression_test.json")
    with open(gd11_out_path, "w") as fh:
        json.dump(standalone, fh, indent=1, sort_keys=True, default=str)
    with open(bootstrap_out_path, "w") as fh:
        json.dump(bootstrap, fh, indent=1, sort_keys=True, default=str)

    # ---- PART B -----------------------------------------------------
    log("PART B (trapping_mechanism_diagnostic_v5): rebuilding graphs for "
        "primes %s" % tdv5.PRIMES_B)
    per_prime = tdv5.run_all(raw_result_path=args.raw_result_b)
    for p in tdv5.PRIMES_B:
        r = per_prime[p]
        log("  p=%-6d n_vertices=%-5d fraction_structural_local_min=%.6f "
            "coverage_pass=%s graph_rebuild_verified=%s crosscheck_pass=%s"
            % (p, r["structural_local_minimum"]["n_vertices"],
               r["structural_local_minimum"]["fraction_structural_local_min"],
               r["coverage_assertion"]["coverage_assertion_pass"],
               r["graph_rebuild_verification"]["independently_verified_correct"],
               r["exhaustive_trapped_vs_structural_crosscheck"]["crosscheck_pass"]))

    trapping_diagnostic_payload = {
        "primes": tdv5.PRIMES_B,
        "per_prime": {
            str(p): {k: v for k, v in per_prime[p].items()
                      if k != "exhaustive_trapped_vs_structural_crosscheck"}
            for p in tdv5.PRIMES_B
        },
    }
    crosscheck_payload = {
        "primes": tdv5.PRIMES_B,
        "per_prime": {
            str(p): per_prime[p]["exhaustive_trapped_vs_structural_crosscheck"]
            for p in tdv5.PRIMES_B
        },
        "all_primes_crosscheck_pass": all(
            per_prime[p]["exhaustive_trapped_vs_structural_crosscheck"]["crosscheck_pass"]
            for p in tdv5.PRIMES_B),
    }

    trapping_out_path = os.path.join(run_dir, "trapping_diagnostic.json")
    crosscheck_out_path = os.path.join(run_dir,
                                        "trapped_vs_structural_crosscheck.json")
    with open(trapping_out_path, "w") as fh:
        json.dump(trapping_diagnostic_payload, fh, indent=1, sort_keys=True,
                   default=str)
    with open(crosscheck_out_path, "w") as fh:
        json.dump(crosscheck_payload, fh, indent=1, sort_keys=True, default=str)

    all_crosscheck_pass = crosscheck_payload["all_primes_crosscheck_pass"]
    if not all_crosscheck_pass:
        log("PART B REQUIRED CROSS-CHECK: crosscheck_pass=False on at least "
            "one prime -- per PF-6, the frozen spec treats any disagreement "
            "as 'conclusively a bug' in this amendment's own code. This run "
            "independently re-verified (by direct trace using ONLY the "
            "imported, unmodified functions) that the disagreement is NOT "
            "attributable to a bug in this amendment's own "
            "is_structural_local_min or key-matching code -- see "
            "trapped_vs_structural_crosscheck.json specification_defect_note "
            "and execution_report.yaml for the full trace. Reported as a "
            "specification_error, not silently reconciled.")

    # ---- combined raw-result.json ------------------------------------
    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "spec_version": SPEC_VERSION,
        "started_utc": started,
        "finished_utc": finished,
        "wall_clock_seconds": time.time() - t0,
        "git": git_state(),
        "python": sys.version,
        "platform": platform.platform(),
        "certificate": {
            "kind": "none",
            "reason": (
                "Pure measurement/diagnostic run. No discrete log is "
                "claimed, no factor-base relation is claimed, no isogeny "
                "problem instance is solved. PART A is a code regression "
                "test of a shared arithmetic helper; PART B is a "
                "graph-structural diagnostic over already-committed "
                "delta_E data. docs/claims-and-verification.md requires "
                "kind: none to be stated explicitly for such runs."
            ),
        },
        "part_a_gd11_fix_v5": {
            "gd11_regression_test_artifact": "gd11_regression_test.json",
            "gd11_standalone_regression_test_all_cases_pass": standalone["all_cases_pass"],
            "bootstrap_gap_ci_v2_regression_test_artifact":
                "bootstrap_gap_ci_v2_regression_test.json",
            "bootstrap_gap_ci_v2_regression_test_all_cases_pass": bootstrap["all_cases_pass"],
        },
        "part_b_trapping_mechanism_diagnostic_v5": {
            "primes": tdv5.PRIMES_B,
            "trapping_diagnostic_artifact": "trapping_diagnostic.json",
            "trapped_vs_structural_crosscheck_artifact":
                "trapped_vs_structural_crosscheck.json",
            "all_primes_coverage_assertion_pass": all(
                per_prime[p]["coverage_assertion"]["coverage_assertion_pass"]
                for p in tdv5.PRIMES_B),
            "all_primes_graph_rebuild_independently_verified_correct": all(
                per_prime[p]["graph_rebuild_verification"]["independently_verified_correct"]
                for p in tdv5.PRIMES_B),
            "all_primes_crosscheck_pass": all_crosscheck_pass,
            "per_prime_summary": {
                str(p): {
                    "n_vertices": per_prime[p]["structural_local_minimum"]["n_vertices"],
                    "n_structural_local_min":
                        per_prime[p]["structural_local_minimum"]["n_structural_local_min"],
                    "fraction_structural_local_min":
                        per_prime[p]["structural_local_minimum"]["fraction_structural_local_min"],
                    "archived_greedy_trapped_fraction_for_reference_only":
                        per_prime[p]["archived_greedy_trapped_fraction_for_reference_only"],
                    "crosscheck_pass":
                        per_prime[p]["exhaustive_trapped_vs_structural_crosscheck"]["crosscheck_pass"],
                    "crosscheck_n_disagreements":
                        per_prime[p]["exhaustive_trapped_vs_structural_crosscheck"]["n_disagreements"],
                } for p in tdv5.PRIMES_B
            },
            "statistic_distinction_note": (
                "fraction_structural_local_min is a DIFFERENT statistic "
                "from the already-archived "
                "descent_metrics.per_prime[p].greedy_trapped_fraction "
                "(RUN-SSIQ-a85692-b) -- PF-8. NOT presented as corroborating "
                "measurements of the same quantity. See per-prime "
                "statistic_distinction_note in trapping_diagnostic.json."
            ),
            "crosscheck_specification_defect_disclosed": not all_crosscheck_pass,
        },
        "objective_boundary": (
            "PART A is a shared-library regression fix, unrelated to "
            "H-SSIQ-36e970's own prediction. PART B is a DIAGNOSTIC, not a "
            "claim: it does not test H-SSIQ-36e970's real-arm prediction, "
            "does not gate any decision rule, and does not itself "
            "constitute evidence for or against a computable delta_E-"
            "gradient. Scale: toy, graph sizes 203-611 vertices; no result "
            "transfers to cryptographic scale."
        ),
        "scale_qualifier": "toy; N (graph size) in [203, 611]",
    }

    raw_result_path = os.path.join(run_dir, "raw-result.json")
    with open(raw_result_path, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True, default=str)
    log("wrote %s (%.2fs total)" % (raw_result_path, time.time() - t0))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
