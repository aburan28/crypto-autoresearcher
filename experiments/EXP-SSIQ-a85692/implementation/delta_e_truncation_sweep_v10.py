#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v10 (BATCH-013) -- delta_e_truncation_sweep_v10.

Implements experiments/EXP-SSIQ-a85692/specification_v10.yaml
inputs.truncation_sweep_search_v10 EXACTLY as frozen (version 10,
frozen_at 2026-08-06). THREE INDEPENDENT PART-A-ONLY BUDGET PASSES over ONE
SHARED, ONCE-BUILT graph for p=2437 (SWEEP_BUDGETS = [0.6, 0.8, 1.0]
seconds/vertex), each strictly below the observed 1.14993s natural-
completion floor (RUN-SSIQ-a85692-h), testing RT-BATCH-012's own
falsifiable prediction: does the resolved-value distribution shift toward
the true population mix as budget grows, and does v9's own Frobenius-
conjugate-pairing selection artifact weaken?

REUSE / DUPLICATION SPLIT, DISCLOSED EXPLICITLY (matches
required_artifacts_note's own (i)/(ii) split):
  (i)  GENUINELY IMPORTED, UNCHANGED: delta_e_truncation_probe_v9.
       run_truncation_probe_v9 (the per-vertex search loop itself, called
       directly, never reimplemented -- PF-3's fix),
       delta_e_truncation_probe_v9.parse_v8_new_delta_map (PF-5's fix),
       delta_e_truncation_probe_v9.compare_against_archived,
       delta_e_truncation_probe_v9.compare_against_v8 (PF-9's fix, round 2
       pre-freeze review); trapping_diagnostic_v5.build_graph_for_prime,
       trapping_diagnostic_v5.load_archived_prime_data;
       delta_e_independent_rng_probe_v8.verify_graph_identity (called once,
       per PF-1's fix -- derive_per_vertex_seed is NOT separately imported
       here, since it is only ever called from inside
       run_truncation_probe_v9's own already-imported body, not by this
       module's own new code directly).
  (ii) AUTHORIZED, DISCLOSED DUPLICATES (new code this file writes): the
       sweep-loop driver (iterating SWEEP_BUDGETS, calling
       run_truncation_probe_v9 once per budget inside a per-sweep-point
       try/except per PF-2's fix), the per-sweep-point Comparison 1/
       Comparison 2 driver (calling the genuinely-imported functions
       above, not reimplementing them), the value-histogram/conjugate-pair
       reporting logic (genuinely new, no v9 equivalent), a small
       vertex_json_safe helper (JSON-safety convention, PF-13, a trivial
       one-line utility identical in shape to v8/v9's own
       delta_map_json_safe, not imported since it is not on
       required_artifacts_note's own genuine-import list), and a small
       git_state() helper (infra bookkeeping only, the same trivial
       pattern every prior module in this lineage repeats).

Does NOT import or call compute_delta_e.two_sided_search directly (that
call lives inside the genuinely-imported run_truncation_probe_v9, not
reimplemented here), compute_delta_e.run_phase_minus1_on_confirmatory_set,
compute_delta_e_v2.run_phase_minus1_on_confirmatory_set,
delta_e_permutation_null_control_v7's depth0_fraction/summary_stats (NO
PART B in this amendment, same as v9), or
delta_e_independent_rng_probe_v8's/delta_e_truncation_probe_v9's own driver
functions (run_probe_delta_e_search_v8, run_probe_permutation_null_control_v8,
v9's own main) anywhere.

STEP (0) FAILURE MODE (explicit, per PF-10): the graph rebuild
(trapping_diagnostic_v5.build_graph_for_prime) and the two-part
graph-identity re-verification (delta_e_independent_rng_probe_v8.
verify_graph_identity) run EXACTLY ONCE, BEFORE the sweep loop, and are
NOT wrapped in any try/except. If either raises, the exception propagates
UNCAUGHT and this run terminates with NO truncation_sweep_comparison.json
or raw-result.json written at all -- an infra/setup failure under
AGENTS.md rule 3, never negative mathematical evidence and never recorded
as a sweep_point_error for any budget.

PER-SWEEP-POINT FAILURE ISOLATION (PF-2): each sweep point's ENTIRE bundle
(PART A search + both required comparisons + the histogram/conjugate-pair
reporting) is wrapped in its own try/except. Any exception there is caught,
recorded as a sweep_point_error string for that budget alone, and the loop
continues to the next sweep point. Results accumulate incrementally; the
final combined artifact write is unconditional on how many sweep points
succeeded (0, 1, 2, or 3).

JSON SAFETY (PF-13's convention, inherited unchanged from v8/v9): every
vertex-keyed artifact output uses the str(list(v))-keyed convention; a raw
tuple is never written directly as a JSON dict key.

OBJECTIVE_BOUNDARY: this is a purely DESCRIPTIVE diagnostic control. It
does NOT produce a PERSISTS/WEAKENS label. It does not interpret what the
measurements mean for PF-6, H-SSIQ-36e970, or lever L4 -- measurements
only. It does NOT itself answer RT-BATCH-011's original truncation-boundary
question (even b=1.0 stays below the 1.14993s floor) -- it only tests
whether the selection-effect artifact from BATCH-012 weakens.
"""

import argparse
import json
import math
import os
import platform
import subprocess
import sys
import time

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
_B_IMPL_DIR = os.path.join(_THIS_DIR, "..", "..", "EXP-SSIQ-58b642",
                            "implementation")
sys.path.insert(0, _B_IMPL_DIR)

# Import order: see trapping_diagnostic_v5.py's own note on the genuine
# circular import between the frozen descent_hitting_time.py and
# calibration_synthetic.py -- importing calibration_synthetic first avoids
# it. Neither frozen file is modified here.
import calibration_synthetic as cal  # noqa: E402,F401 (import-order fix only)
import trapping_diagnostic_v5 as tdv5  # noqa: E402  (FROZEN, UNCHANGED --
                         # (i) genuine-import source for
                         # build_graph_for_prime / load_archived_prime_data)
import delta_e_independent_rng_probe_v8 as v8probe  # noqa: E402  (FROZEN,
                         # UNCHANGED -- (i) genuine-import source for
                         # verify_graph_identity. Its own driver functions
                         # are NOT called anywhere in this file.)
import delta_e_truncation_probe_v9 as v9probe  # noqa: E402  (FROZEN,
                         # UNCHANGED -- (i) genuine-import source for
                         # run_truncation_probe_v9, parse_v8_new_delta_map,
                         # compare_against_archived, compare_against_v8.
                         # Its own main()/CLI entry point is NOT called
                         # anywhere in this file.)

EXPERIMENT_ID = "EXP-SSIQ-a85692"
RUN_ID = "RUN-SSIQ-a85692-j"
SPEC_VERSION = 10

PRIME = 2437
ARCHIVED_N_VERTICES = 203
ARCHIVED_N_NON_FP_RATIONAL = 194
ARCHIVED_N_FP_RATIONAL = ARCHIVED_N_VERTICES - ARCHIVED_N_NON_FP_RATIONAL  # 9

GRAPH_SEED = 20260805      # SEEDS[0], the pinned graph-construction seed
                           # every amendment since v5 has used.
BASE_SEED = 20260811       # IDENTICAL constant v8/v9 both used (deliberate
                           # reuse: isolates budget as the sole manipulated
                           # variable across this entire lineage).

SWEEP_BUDGETS = [0.6, 0.8, 1.0]  # FIXED, PRE-REGISTERED list, never
                                  # computed or adjusted at runtime.

RUN_B_RAW_RESULT_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-b", "raw-result.json")
RUN_H_COMPARISON_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-h", "probe_delta_e_comparison.json")


# ==========================================================================
# JSON SAFETY helper (PF-13's convention, a trivial one-line utility, not
# on required_artifacts_note's own genuine-import list -- authorized,
# disclosed duplicate of the identical one-liner v8/v9/compute_delta_e_v2
# already established, applied here to this module's own new output).
# ==========================================================================

def vertex_json_safe(v):
    return str(list(v))


def delta_map_json_safe(delta_map):
    return {vertex_json_safe(k): v for k, v in delta_map.items()}


# ==========================================================================
# REQUIRED VALUE HISTOGRAM AND CONJUGATE-PAIR REPORTING (genuinely new
# code this amendment adds, per amendment_scope). Operates on THIS sweep
# point's own resolved non-F_p-rational vertices only.
# ==========================================================================

def value_histogram_and_conjugate_pairs(resolved_non_fp_set, new_delta_map,
                                         field):
    """resolved_non_fp_set: the set of non-F_p-rational vertices this sweep
    point's own search resolved (a subset of new_delta_map's keys).
    Returns (histogram, n_resolved, n_conjugate_pairs_among_resolved,
    n_resolved_without_a_paired_partner_in_resolved_set, anomaly_or_None).
    Well-defined, explicitly-handled at n_resolved == 0 (PF-8): histogram
    is {}, both pair counts are 0."""
    n_resolved = len(resolved_non_fp_set)

    histogram = {}
    for v in resolved_non_fp_set:
        val = new_delta_map[v]
        histogram[val] = histogram.get(val, 0) + 1

    n_without_partner = 0
    n_self_conjugate = 0
    for v in resolved_non_fp_set:
        fv = field.frobenius(v)
        if fv == v:
            # DISCLOSED, UNANTICIPATED-EDGE-CASE GUARD (HONESTY RULE): the
            # frozen contract's own pre-freeze review proved this case
            # impossible at p=2437 for non-F_p-rational vertices (p odd =>
            # frobenius(v) == v would require v to be F_p-rational). Kept
            # as an explicit, loud, non-crashing guard rather than a
            # silently-assumed invariant; reported as an anomaly if it is
            # nonetheless ever observed.
            n_self_conjugate += 1
            n_without_partner += 1
        elif fv not in resolved_non_fp_set:
            n_without_partner += 1

    n_paired = n_resolved - n_without_partner
    anomaly = None
    if n_self_conjugate:
        anomaly = (
            "UNEXPECTED: %d resolved vertex/vertices satisfied "
            "frobenius(v) == v (self-conjugate) despite the frozen "
            "contract's own pre-freeze review proving this impossible at "
            "p=2437 for non-F_p-rational vertices -- disclosed, not "
            "silently assumed away." % n_self_conjugate)
    if n_paired % 2 != 0:
        msg = (
            "INTERNAL INCONSISTENCY: n_paired (%d) is odd -- the "
            "paired-vertex count should always be even since frobenius is "
            "an involution and (per the frozen contract's own review) "
            "self-conjugate vertices are impossible among non-F_p-rational "
            "vertices at p=2437. Reported honestly rather than silently "
            "reconciled; n_conjugate_pairs_among_resolved below uses "
            "integer floor division of this odd count." % n_paired)
        anomaly = (anomaly + " " + msg) if anomaly else msg

    n_conjugate_pairs = n_paired // 2

    return (histogram, n_resolved, n_conjugate_pairs, n_without_partner,
            anomaly)


# ==========================================================================
# git / environment bookkeeping (ii) -- small, non-research duplicate of
# the same trivial pattern every prior module in this lineage repeats.
# ==========================================================================

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


# ==========================================================================
# CLI entry point / this run's own artifact writer.
# ==========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True,
                     help="output directory for this run's artifacts")
    ap.add_argument("--raw-result-b", default=RUN_B_RAW_RESULT_RELPATH,
                     help="path to RUN-SSIQ-a85692-b/raw-result.json "
                          "(READ ONLY, source of the archived comparison "
                          "delta_map, Comparison 1)")
    ap.add_argument("--run-h-comparison", default=RUN_H_COMPARISON_RELPATH,
                     help="path to "
                          "RUN-SSIQ-a85692-h/probe_delta_e_comparison.json "
                          "(READ ONLY, source of v8's own new_delta_map, "
                          "Comparison 2)")
    args = ap.parse_args()

    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log = lambda s: print(s, flush=True)  # noqa: E731

    log("[%s] %s / %s (specification_v10.yaml)" % (started, EXPERIMENT_ID, RUN_ID))
    log("delta_e_truncation_sweep_v10: prime=%d GRAPH_SEED=%d BASE_SEED=%d "
        "SWEEP_BUDGETS=%s (PART A ONLY -- no PART B, three independent "
        "sweep points over one shared graph)"
        % (PRIME, GRAPH_SEED, BASE_SEED, SWEEP_BUDGETS))

    run_dir = args.run_dir
    os.makedirs(run_dir, exist_ok=True)

    # ======================================================================
    # STEP (0): rebuild the graph + re-run graph-identity verification,
    # EXACTLY ONCE, BEFORE the sweep loop. NOT wrapped in any try/except --
    # per the frozen contract, an exception here propagates UNCAUGHT and
    # this run terminates with NO output artifact written at all.
    # ======================================================================
    log("STEP (0): Rebuilding graph for p=%d via "
        "trapping_diagnostic_v5.build_graph_for_prime (GENUINELY IMPORTED, "
        "UNCHANGED, seed=%d) -- NOT wrapped in try/except, per the frozen "
        "contract" % (PRIME, GRAPH_SEED))
    g, seed_info = tdv5.build_graph_for_prime(PRIME, GRAPH_SEED)
    field = g["field"]

    log("STEP (0): Re-running two-part graph-identity verification via "
        "delta_e_independent_rng_probe_v8.verify_graph_identity (GENUINELY "
        "IMPORTED, UNCHANGED) -- NOT wrapped in try/except")
    graph_identity = v8probe.verify_graph_identity(g, ARCHIVED_N_VERTICES)
    log("  graph_identity_verification pass=%s (n_built=%d, degseq_pass=%s)"
        % (graph_identity["pass"], graph_identity["n_built_vertices"],
           graph_identity["degree_sequence_check"]["pass"]))

    # non_fp_rational_set: derived ONCE from the graph object, step (0),
    # required by compare_against_archived/compare_against_v8, neither of
    # which returns it.
    non_fp_rational_set = set(v for v in g["vertices"] if not field.is_in_fp(v))
    log("STEP (0): non_fp_rational_set derived once, size=%d (expected %d)"
        % (len(non_fp_rational_set), ARCHIVED_N_NON_FP_RATIONAL))

    # ======================================================================
    # STEP (1): archived comparison source, loaded ONCE (identical for
    # every sweep point; loading is a pure read, safe to hoist outside the
    # per-sweep-point try/except, but re-attempted per sweep point's own
    # try block per the frozen contract's REQUIRED COMPARISON 1 text, which
    # scopes it "per sweep point, inside that sweep point's own try
    # block"). To honor that per-sweep-point scoping literally (so a
    # transient read failure on ONE sweep point cannot silently reuse a
    # DIFFERENT sweep point's success), the load is repeated inside each
    # sweep point's own try block below, not hoisted here.
    # ======================================================================

    sweep_point_results = []

    for b in SWEEP_BUDGETS:
        log("SWEEP POINT b=%.1fs: entering own try/except (PF-2)" % b)
        sweep_point_error = None
        entry = {"per_vertex_budget_seconds": b}
        try:
            t_b = time.time()

            # ---- (1) PART A: run_truncation_probe_v9, DIRECTLY, UNCHANGED
            part_a_result = v9probe.run_truncation_probe_v9(g, BASE_SEED, b)
            new_delta_map = part_a_result["new_delta_map_raw"]
            n_resolved = part_a_result["n_resolved"]
            n_timed_out = part_a_result["n_timed_out"]
            n_attempted = part_a_result["n_attempted"]
            n_non_fp_rational = part_a_result["n_non_fp_rational"]
            coverage_fraction = part_a_result["coverage_fraction"]
            part_a_wall = time.time() - t_b
            log("  PART A done in %.2fs: n_resolved=%d/%d n_timed_out=%d "
                "coverage_fraction=%s" % (
                    part_a_wall, n_resolved, n_non_fp_rational, n_timed_out,
                    coverage_fraction))

            # ---- (2) REQUIRED REPORTING: n_resolved, n_timed_out,
            # coverage_fraction (== n_resolved / 194)
            assert n_non_fp_rational == ARCHIVED_N_NON_FP_RATIONAL, (
                "n_non_fp_rational (%d) != the pinned 194-vertex domain "
                "convention" % n_non_fp_rational)
            coverage_fraction_194 = n_resolved / float(ARCHIVED_N_NON_FP_RATIONAL)

            # ---- (3) REQUIRED COMPARISON 1, against RUN-SSIQ-a85692-b's
            # archived delta_map.
            archived = tdv5.load_archived_prime_data(args.raw_result_b, PRIME)
            archived_delta_map = archived["delta_map"]
            comparison_1 = v9probe.compare_against_archived(
                new_delta_map, archived_delta_map, non_fp_rational_set)
            log("  comparison_1 (vs archived): n_value_matches=%d "
                "n_value_differs=%d"
                % (comparison_1["n_value_matches_vs_archived"],
                   comparison_1["n_value_differs_vs_archived"]))

            # ---- (4) REQUIRED COMPARISON 2, against RUN-SSIQ-a85692-h's
            # own new_delta_map.
            v8_delta_map = v9probe.parse_v8_new_delta_map(args.run_h_comparison)
            comparison_2 = v9probe.compare_against_v8(
                new_delta_map, v8_delta_map, non_fp_rational_set)
            log("  comparison_2 (vs v8): n_value_matches=%d n_value_differs=%d"
                % (comparison_2["n_value_matches_vs_v8"],
                   comparison_2["n_value_differs_vs_v8"]))

            # ---- (5) REQUIRED VALUE HISTOGRAM AND CONJUGATE-PAIR REPORTING
            resolved_non_fp_set = set(
                v for v in non_fp_rational_set if v in new_delta_map)
            (histogram, n_resolved_non_fp, n_conjugate_pairs,
             n_without_partner, hist_anomaly) = value_histogram_and_conjugate_pairs(
                resolved_non_fp_set, new_delta_map, field)
            log("  histogram/conjugate-pair: n_resolved_non_fp=%d "
                "n_conjugate_pairs=%d n_without_partner=%d anomaly=%s"
                % (n_resolved_non_fp, n_conjugate_pairs, n_without_partner,
                   bool(hist_anomaly)))
            if hist_anomaly:
                log("  ANOMALY: %s" % hist_anomaly)

            entry.update({
                "sweep_point_error": None,
                "n_resolved": n_resolved,
                "n_timed_out": n_timed_out,
                "n_attempted": n_attempted,
                "n_non_fp_rational": n_non_fp_rational,
                "n_fp_rational_wired_unconditionally":
                    part_a_result["n_fp_rational_wired_unconditionally"],
                "coverage_fraction": coverage_fraction,
                "coverage_fraction_denominator_194_check": coverage_fraction_194,
                "len_new_delta_map": len(new_delta_map),
                "per_vertex_records": part_a_result["per_vertex_records"],
                "new_delta_map": delta_map_json_safe(new_delta_map),
                "comparison_against_archived": comparison_1,
                "comparison_against_v8": comparison_2,
                "resolved_non_fp_rational_value_histogram": histogram,
                "n_resolved_non_fp_rational": n_resolved_non_fp,
                "n_conjugate_pairs_among_resolved": n_conjugate_pairs,
                "n_resolved_without_a_paired_partner_in_resolved_set":
                    n_without_partner,
                "conjugate_pair_anomaly": hist_anomaly,
                "wall_seconds_this_sweep_point": time.time() - t_b,
            })
            log("SWEEP POINT b=%.1fs: SUCCESS (%.2fs)"
                % (b, time.time() - t_b))

        except Exception as e:  # noqa: BLE001 -- PF-2 requires catching ANY
                                 # exception here, not only a specific one.
            sweep_point_error = "%s: %s" % (type(e).__name__, str(e))
            entry["sweep_point_error"] = sweep_point_error
            log("SWEEP POINT b=%.1fs FAILED (caught per PF-2, other sweep "
                "points' own independent attempts are unaffected): %s"
                % (b, sweep_point_error))

        # Accumulated INCREMENTALLY as each sweep point completes (success
        # or failure) -- never deferred to a single end-of-loop write.
        sweep_point_results.append(entry)

    total_wall = time.time() - t0
    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if total_wall > 1200:
        log("WARNING: total_wall_seconds (%.2f) exceeded the 1200s budget "
            "cap -- this should not happen under the 465.6s worst-case "
            "bound, disclosed here per the HONESTY RULE" % total_wall)

    n_sweep_points_succeeded = sum(
        1 for e in sweep_point_results if e.get("sweep_point_error") is None)

    # ---- truncation_sweep_comparison.json: FULL per-sweep-point results,
    # UNCONDITIONAL on how many sweep points succeeded (0, 1, 2, or 3). ----
    sweep_payload = {
        "prime": PRIME,
        "graph_seed": GRAPH_SEED,
        "base_seed": BASE_SEED,
        "sweep_budgets": SWEEP_BUDGETS,
        "graph_identity_verification": graph_identity,
        "seed_construction": seed_info,
        "non_fp_rational_set_size": len(non_fp_rational_set),
        "n_sweep_points_attempted": len(SWEEP_BUDGETS),
        "n_sweep_points_succeeded": n_sweep_points_succeeded,
        "n_sweep_points_failed": len(SWEEP_BUDGETS) - n_sweep_points_succeeded,
        "sweep_points": sweep_point_results,
        "objective_boundary_note": (
            "DESCRIPTIVE DIAGNOSTIC CONTROL ONLY. Does not produce a "
            "PERSISTS/WEAKENS label. Reports measurements only; "
            "interpretation of what these measurements mean for PF-6, "
            "H-SSIQ-36e970, or lever L4 belongs to the Coordinator and "
            "reviewers. Does not itself answer RT-BATCH-011's original "
            "truncation-boundary question -- even b=1.0 stays below the "
            "1.14993s observed natural-completion floor."
        ),
    }
    sweep_path = os.path.join(run_dir, "truncation_sweep_comparison.json")
    with open(sweep_path, "w") as fh:
        json.dump(sweep_payload, fh, indent=1, sort_keys=True, default=str)

    # ---- raw-result.json (top-level summary, no vertex-level detail) -----
    def summary_for(entry):
        if entry.get("sweep_point_error") is not None:
            return {
                "per_vertex_budget_seconds": entry["per_vertex_budget_seconds"],
                "sweep_point_error": entry["sweep_point_error"],
            }
        return {
            "per_vertex_budget_seconds": entry["per_vertex_budget_seconds"],
            "sweep_point_error": None,
            "n_resolved": entry["n_resolved"],
            "n_timed_out": entry["n_timed_out"],
            "coverage_fraction": entry["coverage_fraction"],
            "comparison_1_n_value_matches_vs_archived":
                entry["comparison_against_archived"]["n_value_matches_vs_archived"],
            "comparison_1_n_value_differs_vs_archived":
                entry["comparison_against_archived"]["n_value_differs_vs_archived"],
            "comparison_2_n_value_matches_vs_v8":
                entry["comparison_against_v8"]["n_value_matches_vs_v8"],
            "comparison_2_n_value_differs_vs_v8":
                entry["comparison_against_v8"]["n_value_differs_vs_v8"],
            "resolved_non_fp_rational_value_histogram":
                entry["resolved_non_fp_rational_value_histogram"],
            "n_resolved_non_fp_rational": entry["n_resolved_non_fp_rational"],
            "n_conjugate_pairs_among_resolved":
                entry["n_conjugate_pairs_among_resolved"],
            "n_resolved_without_a_paired_partner_in_resolved_set":
                entry["n_resolved_without_a_paired_partner_in_resolved_set"],
            "conjugate_pair_anomaly": entry["conjugate_pair_anomaly"],
        }

    raw_result_payload = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "spec_version": SPEC_VERSION,
        "started_utc": started,
        "finished_utc": finished,
        "wall_clock_seconds": total_wall,
        "git": git_state(),
        "python": sys.version,
        "platform": platform.platform(),
        "certificate": {
            "kind": "none",
            "reason": (
                "Pure measurement/probe run. No discrete log is claimed, no "
                "factor-base relation is claimed, no isogeny problem "
                "instance is solved -- delta_E upper bounds are labelling "
                "data for a descent-gradient screen, not a solve claim. "
                "docs/claims-and-verification.md requires kind: none to be "
                "stated explicitly for such runs."
            ),
        },
        "prime": PRIME,
        "graph_seed": GRAPH_SEED,
        "base_seed": BASE_SEED,
        "sweep_budgets": SWEEP_BUDGETS,
        "graph_identity_verification": graph_identity,
        "n_sweep_points_attempted": len(SWEEP_BUDGETS),
        "n_sweep_points_succeeded": n_sweep_points_succeeded,
        "n_sweep_points_failed": len(SWEEP_BUDGETS) - n_sweep_points_succeeded,
        "sweep_summary": [summary_for(e) for e in sweep_point_results],
        "artifact_references": {
            "truncation_sweep_comparison": "truncation_sweep_comparison.json",
        },
        "objective_boundary": (
            "This is a DESCRIPTIVE DIAGNOSTIC CONTROL, not a claim. It does "
            "not test H-SSIQ-36e970's real-arm prediction, does not gate "
            "any decision rule, and does not itself constitute evidence for "
            "or against a computable delta_E-gradient or a p^{1/4} "
            "algorithm. It does not produce a PERSISTS/WEAKENS label. It "
            "does not itself answer RT-BATCH-011's original "
            "truncation-boundary question -- even the b=1.0 sweep point "
            "stays below the 1.14993s observed natural-completion floor, "
            "so every vertex is still guaranteed genuinely truncated at "
            "every sweep point. Scale: toy, single prime p=2437 (N=203 "
            "vertices, max log2(p)=%.4f); no result transfers to "
            "cryptographic scale." % math.log2(PRIME)
        ),
        "scale_qualifier": "toy; N (graph size) = 203; single prime p=2437",
        "cross_hardware_reproducibility_caveat": (
            "This run's 'every budget stays below the observed 1.14993s "
            "floor' premise rests on comparing THIS run's wall-clock "
            "behavior against a DIFFERENT run's (RUN-SSIQ-a85692-h's) "
            "hardware-measured floor -- inheriting v9's own PF-3 finding "
            "that exact per-vertex wall-clock cutoff behavior is not "
            "bit-for-bit reproducible across hardware (PF-6, per the "
            "frozen contract)."
        ),
    }
    raw_result_path = os.path.join(run_dir, "raw-result.json")
    with open(raw_result_path, "w") as fh:
        json.dump(raw_result_payload, fh, indent=1, sort_keys=True, default=str)

    log("wrote %s, %s (%.2fs total)" % (raw_result_path, sweep_path, total_wall))
    print("OUTCOME SWEEP-COMPLETE n_succeeded=%d/%d"
          % (n_sweep_points_succeeded, len(SWEEP_BUDGETS)))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
