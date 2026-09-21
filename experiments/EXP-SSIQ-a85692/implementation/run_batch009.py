#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v6 (BATCH-009), RUN-SSIQ-a85692-f -- orchestration entry
point for specification_v6.yaml's amendment:
  PART A (gd12_fix_v6): descent_walk_hardened.py's new
    greedy_descent_hitting_time_v2, gd12_equivalence_regression_test.py's
    required equivalence regression, and funnel_structure_diagnostic_v6.py's
    corrected per-prime cross-check.
  PART B (funnel_structure_diagnostic_v6), DEPENDENT ON PART A:
    funnel_structure_diagnostic_v6.py's basin-assignment / funnel-structure
    diagnostic, gated per-prime on PART A's own crosscheck_pass.

This is a NEW entry-point script (not itself one of the files
required_artifacts_note names explicitly -- descent_walk_hardened.py and "a
diagnostic script e.g. funnel_structure_diagnostic_v6.py" -- disclosed
explicitly in execution_report.yaml's required_artifacts_note diff
cross-check, same disclosure discipline RUN-SSIQ-a85692-e's own
run_batch008.py used). It performs NO new delta_E search, NO Phi_ell
verification, and reads only RUN-SSIQ-a85692-b's already-committed
raw-result.json (read-only, for PART A/B's shared delta_map input).

Writes all four of this run's own JSON artifacts:
  raw-result.json (this file's own summary of both parts)
  gd12_equivalence_regression_test.json
  corrected_crosscheck.json
  funnel_structure_diagnostic.json
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

import gd12_equivalence_regression_test as gd12eq  # noqa: E402  (THIS amendment)
import funnel_structure_diagnostic_v6 as fsd  # noqa: E402  (THIS amendment)

EXPERIMENT_ID = "EXP-SSIQ-a85692"
RUN_ID = "RUN-SSIQ-a85692-f"
SPEC_VERSION = 6


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


def _strip_internal(part_a_result):
    """corrected_crosscheck.json must be JSON-serializable and must not leak
    this run's own internal working state (_internal_rebuild carries a live
    Fp2Field object and the full adjacency; _internal_walks carries a
    per-vertex dict keyed by non-string vertex tuples, which json.dump
    cannot serialize as object keys). Strip both; every REQUIRED reported
    field (crosscheck_pass, disagreements, accounting assertion, graph
    -rebuild verification) is preserved."""
    return {k: v for k, v in part_a_result.items()
            if k not in ("_internal_rebuild", "_internal_walks",
                          "_internal_diameter_sentinel")}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True,
                     help="output directory for this run's artifacts")
    ap.add_argument("--raw-result-b", required=True,
                     help="path to RUN-SSIQ-a85692-b/raw-result.json "
                          "(READ ONLY, source of the shared delta_map)")
    args = ap.parse_args()

    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log = lambda s: print(s, flush=True)  # noqa: E731

    log("[%s] %s / %s (specification_v6.yaml)" % (started, EXPERIMENT_ID, RUN_ID))

    run_dir = args.run_dir
    os.makedirs(run_dir, exist_ok=True)

    # ---- PART A, sub-part 1: REQUIRED EQUIVALENCE REGRESSION -------------
    log("PART A (gd12_fix_v6): running the required equivalence regression "
        "(descent_walk_hardened.greedy_descent_hitting_time_v2 vs "
        "descent_hitting_time.greedy_descent_hitting_time)")
    equiv = gd12eq.run_gd12_equivalence_regression_test(raw_result_path=args.raw_result_b)
    log("  gd12_equivalence_regression_test overall_pass = %s (branches "
        "covered: %s)" % (equiv["overall_pass"], equiv["branches_covered"]))

    equiv_out_path = os.path.join(run_dir, "gd12_equivalence_regression_test.json")
    with open(equiv_out_path, "w") as fh:
        json.dump(equiv, fh, indent=1, sort_keys=True, default=str)

    # ---- PART A, sub-part 2 + PART B --------------------------------------
    log("PART A (corrected cross-check) + PART B (funnel_structure_diagnostic_v6): "
        "rebuilding graphs for primes %s" % fsd.PRIMES_V6)
    part_a, part_b, errors = fsd.run_all(raw_result_path=args.raw_result_b)

    for p in fsd.PRIMES_V6:
        if p in errors and "part_a" in errors[p]:
            log("  p=%-6d PART A FAILED (per-prime halt): %s"
                % (p, errors[p]["part_a"]))
            continue
        a = part_a[p]
        log("  p=%-6d n_vertices=%-5d n_trapped_true=%-5d n_trapped_false=%-5d "
            "accounting_pass=%s crosscheck_pass=%s (%d disagreements)"
            % (p, a["n_vertices"], a["n_trapped_true"], a["n_trapped_false"],
               a["accounting_assertion_pass"], a["crosscheck_pass"],
               a["n_disagreements"]))
        b = part_b.get(p, {})
        if b.get("skipped"):
            log("    PART B SKIPPED for p=%d: %s" % (p, b.get("reason")))
        elif p in errors and "part_b" in errors[p]:
            log("    PART B FAILED (per-prime halt) for p=%d: %s"
                % (p, errors[p]["part_b"]))
        else:
            log("    PART B: n_basin_eligible=%d sum_basin=%d "
                "top_decile_concentration=%s corr(depth,size)=%s "
                "corr(depth,log_size)=%s"
                % (b.get("n_basin_eligible"), b.get("sum_basin"),
                   b["top_decile_concentration"]["concentration_fraction_of_trapped_true_walks"],
                   b["correlation_depth_vs_basin_size"]["value"],
                   b["correlation_depth_vs_log_basin_size"]["value"]))

    corrected_crosscheck_payload = {
        "primes": fsd.PRIMES_V6,
        "per_prime": {
            str(p): _strip_internal(part_a[p]) for p in part_a
        },
        "per_prime_errors": {
            str(p): errors[p]["part_a"] for p in errors if "part_a" in errors[p]
        },
        "all_primes_computed_crosscheck_pass": all(
            part_a[p]["crosscheck_pass"] for p in part_a
        ) if part_a else None,
        "n_primes_part_a_completed": len(part_a),
        "n_primes_part_a_halted": len([p for p in errors if "part_a" in errors[p]]),
        "failure_handling_model": (
            "PER-PRIME (PF-3/PF-7/PF-13 unified): a mismatch in the "
            "REQUIRED ACCOUNTING ASSERTION or the graph-rebuild "
            "verification/coverage assertion halts ONLY that prime's PART A "
            "computation, reported in per_prime_errors; the other primes "
            "proceed normally. crosscheck_pass itself NEVER halts anything "
            "-- it is a per-prime boolean with the full disagreement list."
        ),
    }
    crosscheck_out_path = os.path.join(run_dir, "corrected_crosscheck.json")
    with open(crosscheck_out_path, "w") as fh:
        json.dump(corrected_crosscheck_payload, fh, indent=1, sort_keys=True,
                   default=str)

    funnel_payload = {
        "primes": fsd.PRIMES_V6,
        "per_prime": {
            str(p): part_b[p] for p in part_b
        },
        "per_prime_errors": {
            str(p): errors[p]["part_b"] for p in errors if "part_b" in errors[p]
        },
        "n_primes_part_b_completed": len(
            [p for p in part_b if not part_b[p].get("skipped")]),
        "n_primes_part_b_skipped_precondition": len(
            [p for p in part_b if part_b[p].get("skipped")
             and "PART A crosscheck_pass is False" in part_b[p].get("reason", "")]),
        "n_primes_part_b_halted": len([p for p in errors if "part_b" in errors[p]]),
        "objective_boundary": (
            "This is a DIAGNOSTIC, not a claim. It does not test "
            "H-SSIQ-36e970's real-arm prediction, does not gate any "
            "decision rule, and does not itself constitute evidence for or "
            "against a computable delta_E-gradient."
        ),
    }
    funnel_out_path = os.path.join(run_dir, "funnel_structure_diagnostic.json")
    with open(funnel_out_path, "w") as fh:
        json.dump(funnel_payload, fh, indent=1, sort_keys=True, default=str)

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
                "test plus a graph-structural cross-check; PART B is a "
                "graph-structural basin/funnel diagnostic. Both operate over "
                "already-committed delta_E data (RUN-SSIQ-a85692-b) and "
                "perform no new delta_E search of any kind. "
                "docs/claims-and-verification.md requires kind: none to be "
                "stated explicitly for such runs."
            ),
        },
        "part_a_gd12_fix_v6": {
            "equivalence_regression_artifact": "gd12_equivalence_regression_test.json",
            "equivalence_regression_overall_pass": equiv["overall_pass"],
            "equivalence_regression_branches_covered": equiv["branches_covered"],
            "corrected_crosscheck_artifact": "corrected_crosscheck.json",
            "n_primes_part_a_completed": len(part_a),
            "n_primes_part_a_halted": corrected_crosscheck_payload["n_primes_part_a_halted"],
            "per_prime_summary": {
                str(p): {
                    "n_vertices": part_a[p]["n_vertices"],
                    "n_trapped_true": part_a[p]["n_trapped_true"],
                    "n_trapped_false": part_a[p]["n_trapped_false"],
                    "accounting_assertion_pass": part_a[p]["accounting_assertion_pass"],
                    "crosscheck_pass": part_a[p]["crosscheck_pass"],
                    "n_disagreements": part_a[p]["n_disagreements"],
                } for p in part_a
            },
            "per_prime_errors": corrected_crosscheck_payload["per_prime_errors"],
        },
        "part_b_funnel_structure_diagnostic_v6": {
            "artifact": "funnel_structure_diagnostic.json",
            "n_primes_part_b_completed": funnel_payload["n_primes_part_b_completed"],
            "n_primes_part_b_skipped_precondition": funnel_payload["n_primes_part_b_skipped_precondition"],
            "n_primes_part_b_halted": funnel_payload["n_primes_part_b_halted"],
            "per_prime_summary": {
                str(p): (
                    {"skipped": True, "reason": part_b[p].get("reason")}
                    if part_b[p].get("skipped") else
                    {
                        "n_basin_eligible": part_b[p]["n_basin_eligible"],
                        "sum_basin": part_b[p]["sum_basin"],
                        "n_trapped_false": part_b[p]["n_trapped_false"],
                        "accounting_assertion_pass": part_b[p]["accounting_assertion_pass"],
                        "max_basin_size": part_b[p]["basin_size_distribution"]["max"],
                        "top_decile_concentration":
                            part_b[p]["top_decile_concentration"]["concentration_fraction_of_trapped_true_walks"],
                        "correlation_depth_vs_basin_size":
                            part_b[p]["correlation_depth_vs_basin_size"]["value"],
                        "correlation_depth_vs_log_basin_size":
                            part_b[p]["correlation_depth_vs_log_basin_size"]["value"],
                        "comparison_to_frozen_illustrative_values":
                            part_b[p]["comparison_to_frozen_illustrative_values"],
                    }
                ) for p in part_b
            },
        },
        "objective_boundary": (
            "PART A supersedes GD-12's fix (a shared-library exposure of "
            "the descent walk's terminal vertex, plus a corrected "
            "cross-check) and is unrelated to H-SSIQ-36e970's own "
            "prediction. PART B is a DIAGNOSTIC, not a claim: it does not "
            "test H-SSIQ-36e970's real-arm prediction, does not gate any "
            "decision rule, and does not itself constitute evidence for or "
            "against a computable delta_E-gradient. Scale: toy, graph sizes "
            "203-611 vertices; no result transfers to cryptographic scale."
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
