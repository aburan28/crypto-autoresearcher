#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v2 (specification_v2.yaml) -- CUMULATIVE-BUDGET amendment to
v1's compute_delta_e.py, correcting GD-7's admission-side defect AND its
own, textually-invisible, execution-side sibling instance found by the
BATCH-005 pre-freeze review (RT-PREFREEZE-EXP-SSIQ-a85692-v2.md, PF-1).

PROTOCOL NOTE ON PHYSICAL FORM (disclosed, see execution_report.yaml
protocol_deviations): the launching task instructed the Executor to "copy or
branch" v1's implementation rather than edit
experiments/EXP-SSIQ-a85692/implementation/compute_delta_e.py in place, so
that v1's own frozen run (RUN-SSIQ-a85692-a) and its already-committed
implementation file remain byte-for-byte untouched. This file is therefore a
NEW, separate module that IMPORTS every function specification_v2.yaml's
required_artifacts_note lists as UNCHANGED directly from v1's
compute_delta_e.py (reuse by reference, exactly the discipline v1 itself
used for EXP-SSIQ-58b642's code), and re-implements ONLY the functions and
call sites required_artifacts_note names as CHANGED or NEW. The LOGICAL diff
this file embodies is identical to the diff list in
specification_v2.yaml required_artifacts_note; see this run's
execution_report.yaml for the explicit function-by-function cross-check
against that list.

REQUIRED_ARTIFACTS_NOTE DIFF LIST, AS IMPLEMENTED HERE:
  CHANGED (rewritten in THIS file, v2 semantics):
    - apply_truncation_fallback  -- scope_reduction_fallback_v2: cumulative
      ascending-prefix admission against T_reserved, replacing v1's
      individual per-prime cap (GD-7).
    - run_phase_minus1_on_confirmatory_set -- real_execution_budget_v2
      (PF-1's fix): no per-prime cap of any kind; a SINGLE aggregate,
      real, measured wall-clock counter threaded across every prime it is
      called on (both the pre-registered confirmatory prefix and, later,
      each coverage_widening_note extension prime).
  NEW (this file):
    - estimate_per_prime_cost_v2 -- per_prime_cost_estimate_v2's two-point
      linear interpolation, a separate helper (PF-5), used ONLY for (i)
      diagnostic reporting, (ii) scope_reduction_fallback_v2's admission-side
      cumulative sum, and (iii) coverage_widening_note's go/no-go ATTEMPT
      decision -- NEVER to size or cap real per-prime execution time (PF-3).
    - main()'s new call sites: a second run_feasibility_smoke_test() call at
      PRIMES[0] (feasibility_smoke_test_v2; the function body itself is
      UNCHANGED, imported from v1), the aggregate-counter threading into
      run_phase_minus1_on_confirmatory_set, and the coverage_widening_note
      extension loop.
  UNCHANGED, imported directly from v1's compute_delta_e.py (reuse by
  reference, never re-derived):
    - neighbors_ell_isogenous, build_smooth_table, two_sided_search (the
      delta_E search instrument itself)
    - verify_modular_polynomials (PF-2 Phi_ell sourcing + independent
      Velu-formula verification)
    - build_all_graphs, run_correctness_gates (graph reuse,
      C-CONNECTIVITY/M-DEGSEQ/C-EDGELIST)
    - run_feasibility_smoke_test (function body unchanged; called TWICE
      instead of once, per feasibility_smoke_test_v2)
    - run_c_search_bias, pearson_corr (C-SEARCH-BIAS, REQUIRED control)
    - run_c_bound_check (C-BOUND-CHECK)
    - apply_decision_rule (four-branch decision rule)
    - git_state
    - the module constants PRIMES, B_SMOOTH, X_LIST_BOUND, L_PRIMES, SEEDS,
      WALL_CLOCK_BUDGET_SECONDS

Everything downstream of the changed functions that is NOT itself a named,
importable function in v1 (the C-NULL-LABEL and descent-metrics
orchestration inline in v1's main()) is reproduced here with the SAME logic
v1 used, extended ONLY where specification_v2.yaml's coverage_widening_note
explicitly requires it (extension primes contribute to the M-GAP fitting
window once attempted, per fitting_window's inherited "no prime may be
excluded post-hoc" clause) -- see execution_report.yaml for an explicit
disclosure of one latent gap this reuse surfaces (PER-PRIME-TRAPPED-EXCLUSION
is defined in the frozen spec's text but was never wired into v1's own
main() orchestration; this file reproduces that same, unmodified inline
logic rather than silently patching it under this differently-scoped
amendment -- reported, not fixed, per the reuse discipline).
"""

import argparse
import json
import math
import os
import platform
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "..", "EXP-SSIQ-58b642", "implementation"))

import build_isogeny_graph as big          # noqa: E402  (REUSED UNCHANGED, via v1's own route)
import calibration_synthetic as cal        # noqa: E402  (REUSED UNCHANGED)
import descent_hitting_time as dht         # noqa: E402  (REUSED UNCHANGED)

# v1's compute_delta_e.py -- REUSED BY REFERENCE (Python import, not copied)
# for every function required_artifacts_note names as UNCHANGED.
import compute_delta_e as v1c              # noqa: E402

PRIMES = v1c.PRIMES
B_SMOOTH = v1c.B_SMOOTH
X_LIST_BOUND = v1c.X_LIST_BOUND
L_PRIMES = v1c.L_PRIMES
SEEDS = v1c.SEEDS
WALL_CLOCK_BUDGET_SECONDS = v1c.WALL_CLOCK_BUDGET_SECONDS

two_sided_search = v1c.two_sided_search
verify_modular_polynomials = v1c.verify_modular_polynomials
build_all_graphs = v1c.build_all_graphs
run_correctness_gates = v1c.run_correctness_gates
run_feasibility_smoke_test = v1c.run_feasibility_smoke_test
run_c_search_bias = v1c.run_c_search_bias
run_c_bound_check = v1c.run_c_bound_check
apply_decision_rule = v1c.apply_decision_rule
git_state = v1c.git_state

EXPERIMENT_ID = "EXP-SSIQ-a85692"
RUN_ID = "RUN-SSIQ-a85692-b"
AMENDS_RUN_ID = "RUN-SSIQ-a85692-a"
SPEC_VERSION = 2

# PF-1 FIX APPLIED (real_execution_budget_v2): T_RESERVED replaces v1's
# T_PRIME = 0.5*7200/12 = 300s (GD-7's individual per-prime share) with the
# SAME half-budget reservation used as a SINGLE aggregate ceiling instead --
# for BOTH the admission-side cumulative sum (scope_reduction_fallback_v2)
# and the execution-side real, measured wall-clock counter
# (real_execution_budget_v2). No division by len(PRIMES) anywhere in v2.
T_RESERVED = 0.5 * WALL_CLOCK_BUDGET_SECONDS   # 3600.0s


# ==========================================================================
# NEW: per_prime_cost_estimate_v2 (two-point linear interpolation, PF-5:
# a separate helper, not folded into apply_truncation_fallback)
# ==========================================================================

def estimate_per_prime_cost_v2(c_min, c_max, p_min, p_max,
                                non_fp_counts_by_prime, primes):
    """spec_v2.inputs.delta_e_computation.per_prime_cost_estimate_v2. Two
    MEASURED endpoints (c_min at p_min, c_max at p_max, from
    feasibility_smoke_test_v2) -> linear interpolation of per-vertex cost at
    every pre-registered prime -> estimated_full_coverage_seconds(p) =
    n_non_fp_rational(p) * cost_per_vertex(p).

    PF-3 FIX APPLIED: this estimate is used ONLY for (i) diagnostic
    reporting, (ii) scope_reduction_fallback_v2's admission-side cumulative
    sum (that spec text explicitly says "using per_prime_cost_estimate_v2's
    per-prime estimates"), and (iii) coverage_widening_note's go/no-go
    ATTEMPT decision. It NEVER sizes or caps any REAL per-prime execution
    time -- that is governed SOLELY by real_execution_budget_v2's single
    aggregate, measured (never estimated) wall-clock counter."""
    rows = {}
    for p in primes:
        cost_per_vertex = c_min + (c_max - c_min) * (p - p_min) / float(p_max - p_min)
        n = non_fp_counts_by_prime[p]
        rows[p] = {
            "prime": p,
            "cost_per_vertex_seconds": cost_per_vertex,
            "n_non_fp_rational": n,
            "estimated_full_coverage_seconds": n * cost_per_vertex,
        }
    return rows


# ==========================================================================
# CHANGED: apply_truncation_fallback -- scope_reduction_fallback_v2
# (cumulative-ascending-prefix admission, replacing v1's individual cap)
# ==========================================================================

def apply_truncation_fallback(per_prime_cost_estimate_v2, primes_ascending, t_reserved):
    """spec_v2.inputs.delta_e_computation.scope_reduction_fallback_v2 -- the
    GD-7 admission-side fix. Using per_prime_cost_estimate_v2's interpolated
    per-prime estimates, ascending by prime size, compute the RUNNING
    CUMULATIVE SUM of estimated costs; TRUNCATE the confirmatory prime set
    to the largest ascending PREFIX whose CUMULATIVE sum is <= t_reserved.
    The budget check is against the prefix's TOTAL estimated cost, never
    against an individual prime's estimate compared to a fixed equal share
    of the reserved budget (v1's defective reading)."""
    per_prime_rows = []
    confirmatory = []
    cumulative = 0.0
    still_ascending = True
    for p in primes_ascending:
        est_cost = per_prime_cost_estimate_v2[p]["estimated_full_coverage_seconds"]
        prospective_cumulative = cumulative + est_cost
        fits = prospective_cumulative <= t_reserved
        per_prime_rows.append({
            "prime": p,
            "estimated_full_coverage_seconds": est_cost,
            "cumulative_sum_through_this_prime_seconds": prospective_cumulative,
            "t_reserved_seconds": t_reserved,
            "fits_cumulative_within_t_reserved": bool(fits),
        })
        if fits and still_ascending:
            confirmatory.append(p)
            cumulative = prospective_cumulative
        else:
            still_ascending = False  # PREFIX rule: stop extending once one fails
    return {
        "t_reserved_seconds": t_reserved,
        "per_prime_estimate": per_prime_rows,
        "confirmatory_prime_set": confirmatory,
        "n_confirmatory_primes": len(confirmatory),
        "cumulative_estimated_seconds_admitted": cumulative,
        "truncation_fired": len(confirmatory) < len(primes_ascending),
    }


# ==========================================================================
# CHANGED: run_phase_minus1_on_confirmatory_set -- real_execution_budget_v2
# (PF-1's fix: a single aggregate, real, measured wall-clock counter; NO
# per-prime cap of any kind)
# ==========================================================================

def run_phase_minus1_on_confirmatory_set(graphs, primes_ascending, seeds,
                                          aggregate_budget_seconds):
    """spec_v2.inputs.delta_e_computation.real_execution_budget_v2 -- PF-1
    FIX, REPLACES v1's run_phase_minus1_on_confirmatory_set per-prime
    real-execution cap (T_PRIME=300s, an independent, textually-invisible
    instance of GD-7's exact defect). A SINGLE aggregate, REAL, MEASURED
    (never estimated) wall-clock counter is threaded across every prime in
    primes_ascending (searched in that order, same order as admission);
    each prime's ENTIRE non-F_p-rational vertex set is searched to
    completion UNLESS the aggregate counter is exhausted first, in which
    case the search stops immediately (mid-prime if necessary) and that
    prime's M-COVERAGE reflects whatever fraction was actually resolved
    before the stop.

    Returns (per_prime_results, aggregate_seconds_actually_spent,
    aggregate_seconds_remaining) so the identical counter mechanism can be
    threaded onward, prime-by-prime, into coverage_widening_note's
    extension loop (call this function again with a single-prime list and
    the just-returned remaining value)."""
    results = {}
    remaining = float(aggregate_budget_seconds)
    spent_total = 0.0
    for p in primes_ascending:
        g = graphs[p]
        field = g["field"]
        non_fp = [v for v in g["vertices"] if not field.is_in_fp(v)]
        n_fp_rational = len(g["vertices"]) - len(non_fp)
        if remaining <= 0.0:
            # Aggregate counter already exhausted before this prime could
            # even start -- "STOP the search immediately" applies at the
            # per-prime boundary too, not only mid-vertex.
            results[p] = {
                "n_vertices": len(g["vertices"]), "n_non_fp_rational": len(non_fp),
                "n_attempted": 0, "n_resolved": 0,
                "m_coverage_non_fp_fraction": 0.0 if non_fp else 1.0,
                "m_coverage_all_vertices_fraction": n_fp_rational / float(len(g["vertices"])),
                "aggregate_seconds_available_at_prime_start": remaining,
                "wall_seconds_used": 0.0,
                "delta_map_raw": {v: 1 for v in g["vertices"] if field.is_in_fp(v)},
                "delta_map_json_safe": {str(list(v)): 1 for v in g["vertices"] if field.is_in_fp(v)},
                "per_prime_coverage_shortfall": bool(non_fp),
                "stopped_before_start_aggregate_exhausted": True,
            }
            continue
        q = p * p
        rng_search = random.Random(seeds[0] * 1000003 + p)
        delta_map = {}
        for v in g["vertices"]:
            if field.is_in_fp(v):
                delta_map[v] = 1
        aggregate_at_prime_start = remaining
        t0 = time.time()
        n_resolved = 0
        n_attempted = 0
        for v in non_fp:
            elapsed_this_prime = time.time() - t0
            remaining_now = remaining - elapsed_this_prime
            if remaining_now <= 0.0:
                break
            n_attempted += 1
            target = field.frobenius(v)
            r = two_sided_search(field, v, target, rng_search, q,
                                  L=L_PRIMES, X=X_LIST_BOUND,
                                  time_budget_seconds=remaining_now)
            if r["resolved"]:
                delta_map[v] = r["delta_e_upper_bound"]
                n_resolved += 1
        prime_wall_seconds = time.time() - t0
        remaining -= prime_wall_seconds
        spent_total += prime_wall_seconds
        coverage_all = (n_resolved + n_fp_rational) / float(len(g["vertices"]))
        non_fp_coverage = (n_resolved / float(len(non_fp))) if non_fp else 1.0
        results[p] = {
            "n_vertices": len(g["vertices"]), "n_non_fp_rational": len(non_fp),
            "n_attempted": n_attempted, "n_resolved": n_resolved,
            "m_coverage_non_fp_fraction": non_fp_coverage,
            "m_coverage_all_vertices_fraction": coverage_all,
            "aggregate_seconds_available_at_prime_start": aggregate_at_prime_start,
            "wall_seconds_used": prime_wall_seconds,
            "delta_map_raw": delta_map,
            "delta_map_json_safe": {str(list(k)): v for k, v in delta_map.items()},
            "per_prime_coverage_shortfall": bool(non_fp_coverage < 0.5),
            "stopped_before_start_aggregate_exhausted": False,
        }
    return results, spent_total, max(0.0, remaining)


def _json_safe_phase_minus1_row(r):
    out = {k: v for k, v in r.items()
           if k not in ("delta_map_raw", "delta_map_json_safe")}
    out["delta_map"] = r["delta_map_json_safe"]
    return out


# ==========================================================================
# Main orchestration (v2)
# ==========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    t_run_start = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log = lambda s: print(s, flush=True)  # noqa: E731

    log("[%s] %s / %s (v2 amendment of %s, spec_version=%d)"
        % (started, EXPERIMENT_ID, RUN_ID, AMENDS_RUN_ID, SPEC_VERSION))
    budget_split = {}

    # ---- PHASE 0: C-CAL-GAP (reused unchanged, pure synthetic) ----------
    log("PHASE 0: C-CAL-GAP synthetic calibration (imported unchanged from "
        "EXP-SSIQ-58b642/implementation/calibration_synthetic.py)")
    t0 = time.time()
    phase0 = cal.run_calibration()
    budget_split["phase0_c_cal_gap_seconds"] = time.time() - t0
    log("  C-CAL-GAP overall_pass = %s (%.3fs)" % (phase0["overall_pass"],
                                                     budget_split["phase0_c_cal_gap_seconds"]))

    payload = {
        "experiment_id": EXPERIMENT_ID, "run_id": RUN_ID,
        "amends_run_id": AMENDS_RUN_ID, "spec_version": SPEC_VERSION,
        "started_utc": started, "git": git_state(), "python": sys.version,
        "platform": platform.platform(),
        "certificate": {
            "kind": "none",
            "reason": ("Pure measurement run. No discrete log is claimed, no "
                       "factor-base relation is claimed, no isogeny problem "
                       "instance is solved -- delta_E upper bounds are "
                       "labelling data for a descent-gradient screen, not a "
                       "solve claim. docs/claims-and-verification.md requires "
                       "kind: none to be stated explicitly for such runs."),
        },
        "phase0_calibration": phase0,
    }

    if not phase0["overall_pass"]:
        log("PHASE 0 GATE FAILED -- STOPPING before Phase -1/Phase 1")
        payload["decision"] = {"branch": "N/A-STOPPED-AT-PHASE-0",
                                "reason": "C-CAL-GAP failed"}
        payload["budget_split_seconds"] = budget_split
        with open(args.out, "w") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True, default=str)
        return 1
    log("PHASE 0 PASSED")

    # ---- Modular polynomial sourcing + independent verification (PF-2, --
    # UNCHANGED, reused from v1) -------------------------------------------
    log("Verifying sourced modular polynomials (PF-2, unchanged from v1): "
        "ell=23 REQUIRED via Velu-formula independent route, ell=3 "
        "additional sanity companion")
    t0 = time.time()
    modpoly_report, modpoly_ok = verify_modular_polynomials(SEEDS)
    budget_split["modular_polynomial_verification_seconds"] = time.time() - t0
    log("  ell=23 required verification all_ok=%s (%.3fs)"
        % (modpoly_report["ell_23_required"]["all_ok"],
           budget_split["modular_polynomial_verification_seconds"]))
    payload["modular_polynomial_verification"] = modpoly_report
    if not modpoly_ok:
        log("PHI_23 INDEPENDENT VERIFICATION FAILED -- STOPPING per "
            "invalidation_rules; do not proceed on an unverified polynomial")
        payload["decision"] = {"branch": "N/A-STOPPED-PHI-VERIFICATION-FAILED",
                                "reason": "ell=23 Velu-formula independent "
                                          "verification failed"}
        payload["budget_split_seconds"] = budget_split
        with open(args.out, "w") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True, default=str)
        return 1
    log("Modular polynomial verification PASSED for ell=23 (required)")

    # ---- Graph reuse: build all 12 graphs (cheap, UNCHANGED, reused) -----
    log("Building/reusing %d graphs via Phi_2 BFS (build_isogeny_graph.py, "
        "unchanged, imported via v1's own route)" % len(PRIMES))
    t0 = time.time()
    graphs, seed_info = build_all_graphs(PRIMES, SEEDS[0])
    budget_split["graph_reuse_seconds"] = time.time() - t0
    for p in PRIMES:
        log("  p=%-6d N=%-5d elapsed=%.2fs" % (p, len(graphs[p]["vertices"]),
                                                 graphs[p]["elapsed_seconds"]))
    non_fp_counts = {}
    for p in PRIMES:
        field = graphs[p]["field"]
        non_fp_counts[p] = sum(1 for v in graphs[p]["vertices"]
                                if not field.is_in_fp(v))
    log("  non-F_p-rational vertex counts by prime: %r (sum=%d)"
        % (non_fp_counts, sum(non_fp_counts.values())))

    log("running correctness gates: C-CONNECTIVITY (floor(p/12) anchor), "
        "M-DEGSEQ, C-EDGELIST (UNCHANGED, reused from v1)")
    gates = run_correctness_gates(graphs, PRIMES, edgelist_prime=PRIMES[0])
    all_connectivity_pass = all(gates["connectivity"][p]["pass"] for p in PRIMES)
    all_degseq_pass = all(gates["degree_sequence"][p]["pass"] for p in PRIMES)
    log("  C-CONNECTIVITY all pass: %s" % all_connectivity_pass)
    log("  M-DEGSEQ all pass: %s" % all_degseq_pass)
    log("  C-EDGELIST (p=%d): pass=%s" % (PRIMES[0], gates["edgelist_check"]["pass"]))

    # ---- feasibility_smoke_test_v2: TWO-POINT smoke test (largest AND ---
    # smallest pre-registered prime). run_feasibility_smoke_test itself is
    # UNCHANGED (imported from v1); only the CALL SITE is new (a second call
    # at PRIMES[0]), per required_artifacts_note's explicit statement that
    # the function body is not modified. ------------------------------------
    log("MANDATORY TWO-POINT FEASIBILITY SMOKE TEST (feasibility_smoke_test_v2): "
        "largest pre-registered prime p=%d (as v1 required) AND smallest "
        "pre-registered prime p=%d (NEW in v2)" % (PRIMES[-1], PRIMES[0]))
    t0 = time.time()
    smoke_large = run_feasibility_smoke_test(graphs, PRIMES[-1], SEEDS, n_sample_vertices=3)
    smoke_small = run_feasibility_smoke_test(graphs, PRIMES[0], SEEDS, n_sample_vertices=3)
    budget_split["feasibility_smoke_test_two_point_seconds"] = time.time() - t0
    payload["feasibility_smoke_test_v2"] = {
        "largest_prime": smoke_large, "smallest_prime": smoke_small,
    }
    c_max = smoke_large["avg_wall_seconds_per_vertex"]
    c_min = smoke_small["avg_wall_seconds_per_vertex"]
    p_max, p_min = PRIMES[-1], PRIMES[0]
    log("  c_min (p=%d) = %.4fs/vertex; c_max (p=%d) = %.4fs/vertex (%.3fs total)"
        % (p_min, c_min, p_max, c_max, budget_split["feasibility_smoke_test_two_point_seconds"]))

    non_monotonic = c_max < c_min
    payload["non_monotonicity_check"] = {
        "fired": bool(non_monotonic), "c_min": c_min, "c_max": c_max,
        "p_min": p_min, "p_max": p_max,
    }

    # ---- REQUIRED CONTROL, unconditional: C-SEARCH-BIAS (UNCHANGED, ------
    # reused from v1). Runs regardless of any later gate, per v1's own
    # design ("required, not conditioned on Phase -1"); computed here,
    # right after graph reuse, so it is available even on the
    # non-monotonicity STOP path below. --------------------------------------
    log("Running C-SEARCH-BIAS (REQUIRED control, UNCHANGED from v1) at "
        "smallest pre-registered prime p=%d, >=20 sampled non-F_p-rational "
        "vertices" % PRIMES[0])
    t0 = time.time()
    search_bias = run_c_search_bias(graphs, PRIMES[0], SEEDS, n_sample=20)
    budget_split["c_search_bias_seconds"] = time.time() - t0
    log("  corr(distance, degree) true-target=%r random-target=%r comparable=%s (%.3fs)"
        % (search_bias["true_target_arm"]["correlation_distance_vs_degree"],
           search_bias["random_target_arm"]["correlation_distance_vs_degree"],
           search_bias["magnitudes_comparable_flag"],
           budget_split["c_search_bias_seconds"]))
    payload["c_search_bias"] = search_bias
    c_search_bias_control_failure = bool(search_bias["magnitudes_comparable_flag"])

    log("Running C-BOUND-CHECK (free delta_E=1 identity cross-check, "
        "UNCHANGED from v1)")
    bound_check = run_c_bound_check(graphs, PRIMES)
    payload["c_bound_check"] = bound_check

    if non_monotonic:
        # PF-4 FIX APPLIED: invalidation_rules_v2_additions non-monotonicity
        # STOP condition -> DATA-UNAVAILABLE-BLOCKED (run-level label, per
        # outcome_scope_label_glossary, reused unchanged). Do NOT fall back
        # to v1's flat single-point formula as an improvised substitute.
        log("NON-MONOTONIC two-point smoke test measurement (c_max=%.4f < "
            "c_min=%.4f) -- STOPPING per invalidation_rules_v2_additions. "
            "Reported as DATA-UNAVAILABLE-BLOCKED (PF-4's mapping); NOT "
            "falling back to v1's flat single-point formula."
            % (c_max, c_min))
        decision = {
            "branch": "DATA-UNAVAILABLE-BLOCKED",
            "reason": ("Two-point smoke test measured c_max < c_min "
                       "(non-monotonic), contrary to the interpolation "
                       "model's own precondition. Per "
                       "invalidation_rules_v2_additions this STOPS before "
                       "any cumulative-prefix admission is computed; mapped "
                       "to the run-level DATA-UNAVAILABLE/BLOCKED label "
                       "(no confirmatory set can even be computed)."),
        }
        payload["decision"] = decision
        payload["c_null_label"] = {"ran": False, "reason": "non-monotonicity STOP; no confirmatory set computed"}
        payload["descent_metrics"] = {"ran": False, "reason": "non-monotonicity STOP; no confirmatory set computed"}
        total_wall = time.time() - t_run_start
        budget_split["total_wall_seconds"] = total_wall
        budget_split["budget_seconds"] = WALL_CLOCK_BUDGET_SECONDS
        payload.update({
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "wall_clock_seconds": total_wall,
            "budget_split_seconds": budget_split,
            "primes": PRIMES,
            "non_fp_rational_counts_by_prime": non_fp_counts,
            "seed_construction": seed_info,
            "correctness_gates": {
                "connectivity": gates["connectivity"],
                "degree_sequence": {p: {k: v for k, v in gates["degree_sequence"][p].items()
                                         if k != "examples"} for p in PRIMES},
                "edgelist_prime": gates["edgelist_prime"],
                "edgelist_check": {k: v for k, v in gates["edgelist_check"].items()
                                    if k != "mismatches"},
            },
            "objective_boundary": (
                "This run tests for the EXISTENCE of a computable delta_E-"
                "gradient (L4's revisit condition). Neither the descent "
                "test nor the delta_E-computation search constitutes a "
                "complexity claim. Scale: toy, graph sizes 203-1800 "
                "vertices; no result transfers to cryptographic scale."
            ),
            "scale_qualifier": "toy; N (graph size) in [203, 1800]; max log2(p) = %.4f"
                                % math.log2(max(PRIMES)),
        })
        with open(args.out, "w") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True, default=str)
        log("wrote %s (%.1fs total)" % (args.out, total_wall))
        print("DECISION %s" % decision["branch"])
        return 0

    log("Two-point smoke test is MONOTONIC (c_max >= c_min) -- proceeding "
        "to per_prime_cost_estimate_v2 and scope_reduction_fallback_v2")

    # ---- NEW: per_prime_cost_estimate_v2 (two-point linear interpolation) -
    per_prime_cost = estimate_per_prime_cost_v2(c_min, c_max, p_min, p_max,
                                                 non_fp_counts, PRIMES)
    payload["per_prime_cost_estimate_v2"] = per_prime_cost
    for p in PRIMES:
        row = per_prime_cost[p]
        log("  p=%-6d cost/vertex=%.4fs n_non_fp=%-5d est_full_coverage=%8.1fs"
            % (p, row["cost_per_vertex_seconds"], row["n_non_fp_rational"],
               row["estimated_full_coverage_seconds"]))

    # ---- CHANGED: apply_truncation_fallback (scope_reduction_fallback_v2) -
    log("Applying scope_reduction_fallback_v2 (cumulative-ascending-prefix "
        "admission, T_reserved=%.1fs, GD-7's admission-side fix)" % T_RESERVED)
    truncation = apply_truncation_fallback(per_prime_cost, PRIMES, T_RESERVED)
    for row in truncation["per_prime_estimate"]:
        log("  p=%-6d est_cost=%8.1fs cumulative=%9.1fs fits<=T_reserved=%s"
            % (row["prime"], row["estimated_full_coverage_seconds"],
               row["cumulative_sum_through_this_prime_seconds"],
               row["fits_cumulative_within_t_reserved"]))
    log("  confirmatory_prime_set = %r (n=%d, cumulative_estimated=%.1fs)"
        % (truncation["confirmatory_prime_set"], truncation["n_confirmatory_primes"],
           truncation["cumulative_estimated_seconds_admitted"]))
    payload["truncation_fallback_v2"] = truncation

    phase_minus1_results = {}
    extension_results = {}
    widening_log = []
    aggregate_spent_confirmatory = 0.0
    aggregate_remaining_after_confirmatory = T_RESERVED
    aggregate_remaining_final = T_RESERVED
    n_primes_coverage_pass = 0
    phase_minus1_gate_pass = False

    if truncation["n_confirmatory_primes"] < 4:
        log("cumulative-prefix admitted only %d prime(s) (<4) -- per the "
            "inherited '>=4 primes or lack-of-coverage' floor "
            "(stopping_rules, unchanged from v1), Phase -1 real search is "
            "NOT run on any prime. DATA-UNAVAILABLE-BLOCKED."
            % truncation["n_confirmatory_primes"])
    else:
        # ---- CHANGED: run_phase_minus1_on_confirmatory_set -------------
        # (real_execution_budget_v2, PF-1's fix: single aggregate counter,
        # NO per-prime cap)
        log("Running REAL delta_E search on the %d confirmatory prime(s), "
            "ASCENDING ORDER, against a SINGLE aggregate real-time counter "
            "(T_reserved=%.1fs, no per-prime cap -- real_execution_budget_v2)"
            % (truncation["n_confirmatory_primes"], T_RESERVED))
        t0 = time.time()
        phase_minus1_results, aggregate_spent_confirmatory, aggregate_remaining_after_confirmatory = \
            run_phase_minus1_on_confirmatory_set(
                graphs, truncation["confirmatory_prime_set"], SEEDS, T_RESERVED)
        budget_split["phase_minus1_real_search_confirmatory_seconds"] = time.time() - t0
        for p, r in phase_minus1_results.items():
            log("  p=%-6d M-COVERAGE(non-fp)=%.4f attempted=%d resolved=%d "
                "wall=%.2fs" % (p, r["m_coverage_non_fp_fraction"],
                                 r["n_attempted"], r["n_resolved"], r["wall_seconds_used"]))
        log("  aggregate spent=%.2fs remaining=%.2fs (of T_reserved=%.1fs)"
            % (aggregate_spent_confirmatory, aggregate_remaining_after_confirmatory, T_RESERVED))

        n_primes_coverage_pass = sum(
            1 for p in truncation["confirmatory_prime_set"]
            if phase_minus1_results[p]["m_coverage_non_fp_fraction"] >= 0.5)
        phase_minus1_gate_pass = n_primes_coverage_pass >= 4
        log("Phase -1 gate (pre-registered cumulative-prefix set ALONE, "
            "M-COVERAGE>=0.5 on >=4 primes): pass=%s (n_primes_pass=%d)"
            % (phase_minus1_gate_pass, n_primes_coverage_pass))

        # ---- coverage_widening_note: mechanical, iterative widening -----
        log("coverage_widening_note: iterative widening while REMAINING>0, "
            "one ascending prime at a time, drawing on the SAME "
            "T_reserved-rooted aggregate counter")
        attempted = set(truncation["confirmatory_prime_set"])
        remaining_budget = aggregate_remaining_after_confirmatory
        while remaining_budget > 0.0:
            candidates = [p for p in PRIMES if p not in attempted]
            if not candidates:
                widening_log.append({"stop_reason": "no ascending prime remains beyond the pre-registered set"})
                log("  widening STOP: no ascending prime remains")
                break
            next_prime = min(candidates)
            est = per_prime_cost[next_prime]["estimated_full_coverage_seconds"]
            if est > remaining_budget:
                widening_log.append({
                    "stop_reason": "next ascending prime's estimate exceeds remaining budget",
                    "prime": next_prime, "estimated_full_coverage_seconds": est,
                    "remaining_budget_seconds": remaining_budget})
                log("  widening STOP: p=%d estimate %.1fs exceeds remaining %.1fs"
                    % (next_prime, est, remaining_budget))
                break
            t0w = time.time()
            ext_res, ext_spent, ext_remaining = run_phase_minus1_on_confirmatory_set(
                graphs, [next_prime], SEEDS, remaining_budget)
            budget_split["coverage_widening_extension_seconds"] = \
                budget_split.get("coverage_widening_extension_seconds", 0.0) + (time.time() - t0w)
            extension_results[next_prime] = ext_res[next_prime]
            attempted.add(next_prime)
            entry = {
                "prime": next_prime, "estimated_full_coverage_seconds": est,
                "actual_seconds_spent": ext_spent,
                "remaining_after": ext_remaining,
                "m_coverage_non_fp_fraction": ext_res[next_prime]["m_coverage_non_fp_fraction"],
                "label": "coverage_extension",
            }
            widening_log.append(entry)
            log("  ATTEMPTED extension p=%-6d est=%.1fs actual=%.2fs "
                "M-COVERAGE(non-fp)=%.4f remaining_after=%.2fs"
                % (next_prime, est, ext_spent,
                   ext_res[next_prime]["m_coverage_non_fp_fraction"], ext_remaining))
            remaining_budget = ext_remaining
        aggregate_remaining_final = remaining_budget

    payload["phase_minus1_real_search"] = {
        p: _json_safe_phase_minus1_row(r) for p, r in phase_minus1_results.items()
    }
    payload["coverage_extension"] = {
        "extension_results": {p: _json_safe_phase_minus1_row(r) for p, r in extension_results.items()},
        "widening_log": widening_log,
    }
    payload["real_execution_budget_v2"] = {
        "t_reserved_seconds": T_RESERVED,
        "aggregate_seconds_spent_confirmatory": aggregate_spent_confirmatory,
        "aggregate_seconds_remaining_after_confirmatory": aggregate_remaining_after_confirmatory,
        "aggregate_seconds_remaining_after_widening": aggregate_remaining_final,
        "n_extension_primes_attempted": len(extension_results),
    }

    # ---- C-NULL-LABEL: runs on the USABLE set = confirmatory primes that --
    # cleared M-COVERAGE>=0.5, UNION extension primes that cleared it, once
    # attempted (coverage_widening_note: "extension primes contribute... to
    # W-MAIN's fitting window... per fitting_window... applies equally to
    # an admitted extension prime once attempted", and C-NULL-LABEL must
    # operate on the SAME set feeding the real M-GAP fit to be a valid
    # control on it). Requires a FULL (not merely >=0.5) delta_E multiset --
    # a prime with partial coverage cannot be shuffled meaningfully, same
    # rule v1 applied. ---------------------------------------------------
    usable_primes = sorted(set(
        [p for p in truncation.get("confirmatory_prime_set", [])
         if phase_minus1_results.get(p, {}).get("m_coverage_non_fp_fraction", 0.0) >= 0.5]
        + [p for p in extension_results
           if extension_results[p]["m_coverage_non_fp_fraction"] >= 0.5]
    ))
    all_phase_minus1_by_prime = dict(phase_minus1_results)
    all_phase_minus1_by_prime.update(extension_results)

    c_null_label_report = {"ran": False}
    c_null_label_control_failure = False
    if phase_minus1_gate_pass:
        log("Running C-NULL-LABEL (shuffled real-computed delta_E multiset) "
            "on the usable prime set (confirmatory-pass UNION extension-pass, "
            "n=%d): %r" % (len(usable_primes), usable_primes))
        t0 = time.time()
        null_by_prime = {}
        for p in usable_primes:
            g = graphs[p]
            diam = big.bfs_diameter(g)
            multiset = list(all_phase_minus1_by_prime[p]["delta_map_raw"].values())
            vertices = list(g["vertices"])
            if len(multiset) != len(vertices):
                null_by_prime[p] = {"skipped": True,
                                     "reason": "partial coverage (delta_map "
                                               "shorter than vertex set); "
                                               "shuffling a partial multiset "
                                               "is not a valid null control"}
                continue
            rng = random.Random(SEEDS[2])
            shuffled = list(multiset)
            rng.shuffle(shuffled)
            null_delta_map = dict(zip(vertices, shuffled))
            rng2 = random.Random(SEEDS[0] * 1000003 + p)
            greedy = dht.run_population(g["adjacency"], vertices, null_delta_map,
                                         "greedy", rng2, diam)
            rw = dht.run_population(g["adjacency"], vertices, null_delta_map,
                                     "random", rng2, diam,
                                     max_random_steps=50 * len(vertices))
            null_by_prime[p] = {"greedy_median": greedy["median"],
                                 "greedy_trapped_fraction": greedy["trapped_fraction"],
                                 "random_median": rw["median"]}
        c_null_label_report = {"ran": True, "per_prime": null_by_prime}
        budget_split["c_null_label_extra_seconds"] = time.time() - t0
        usable_ok = [p for p in null_by_prime if not null_by_prime[p].get("skipped")]
        c_null_label_report["n_primes_usable"] = len(usable_ok)
    payload["c_null_label"] = c_null_label_report

    # ---- Descent metrics (M-GAMMA-GREEDY/RANDOM/M-GAP) -- reproduces v1's -
    # inline logic UNCHANGED (same estimator, same OLS-on-logs fit, same
    # >=4-usable-primes floor), extended ONLY to the usable_primes set
    # (confirmatory UNION extension), per coverage_widening_note's explicit
    # fitting_window instruction. DISCLOSED GAP (see execution_report.yaml):
    # v1's own inline logic never implements the PER-PRIME-TRAPPED-EXCLUSION
    # filter M-GAMMA-GREEDY's definition requires (trapped_fraction(N) >
    # 0.5); this was never exercised in RUN-a because Phase -1 never ran.
    # Reproduced here UNCHANGED (not silently patched, per the reuse
    # discipline) -- greedy_trapped_fraction IS reported per prime below so
    # this can be checked post-hoc. --------------------------------------
    descent_metrics = {"ran": False}
    if phase_minus1_gate_pass:
        log("Running descent metrics (M-GAMMA-GREEDY, M-GAMMA-RANDOM, "
            "M-GAP) on the real computed delta_E labels, usable primes n=%d"
            % len(usable_primes))
        t0 = time.time()
        per_prime = {}
        for p in usable_primes:
            g = graphs[p]
            vertices = list(g["vertices"])
            delta_map = all_phase_minus1_by_prime[p]["delta_map_raw"]
            if len(delta_map) != len(vertices):
                continue
            diam = big.bfs_diameter(g)
            rng = random.Random(SEEDS[0] * 1000003 + p)
            greedy = dht.run_population(g["adjacency"], vertices, delta_map,
                                         "greedy", rng, diam)
            rw = dht.run_population(g["adjacency"], vertices, delta_map,
                                     "random", rng, diam,
                                     max_random_steps=50 * len(vertices))
            per_prime[p] = {"N": len(vertices), "greedy_median": greedy["median"],
                             "greedy_trapped_fraction": greedy["trapped_fraction"],
                             "random_median": rw["median"],
                             "is_extension_prime": bool(p in extension_results)}
        usable_full = [p for p in per_prime]
        if len(usable_full) >= 4:
            N_list = [per_prime[p]["N"] for p in usable_full]
            greedy_medians = [per_prime[p]["greedy_median"] for p in usable_full]
            random_medians = [per_prime[p]["random_median"] for p in usable_full]
            fit_greedy = dht.ols_loglog_fit(N_list, greedy_medians)
            fit_random = dht.ols_loglog_fit(N_list, random_medians)
            m_gap = fit_random["gamma"] - fit_greedy["gamma"]
            rng_boot = random.Random(SEEDS[0])
            lo, hi, _ = dht.bootstrap_gap_ci(N_list, greedy_medians, random_medians, rng_boot)
            descent_metrics = {"ran": True, "per_prime": per_prime,
                                "gamma_greedy": fit_greedy["gamma"],
                                "gamma_random": fit_random["gamma"],
                                "m_gap": m_gap, "m_gap_ci_lo": lo, "m_gap_ci_hi": hi,
                                "n_range_achieved": [min(N_list), max(N_list)],
                                "n_primes_used": len(usable_full),
                                "n_extension_primes_used": sum(
                                    1 for p in usable_full if p in extension_results)}
        else:
            descent_metrics = {"ran": False,
                                "reason": "fewer than 4 primes had full delta_E "
                                          "coverage after Phase -1 + widening"}
        budget_split["descent_simulation_seconds"] = time.time() - t0
    payload["descent_metrics"] = descent_metrics

    # ---- Decision rule (mechanical, UNCHANGED apply_decision_rule; gate --
    # determined by the pre-registered cumulative-prefix set ALONE, per
    # coverage_widening_note -- n_primes_coverage_pass computed above does
    # NOT include extension primes) ------------------------------------------
    m_gap_ci_lo = descent_metrics.get("m_gap_ci_lo") if descent_metrics.get("ran") else None
    m_gap_ci_hi = descent_metrics.get("m_gap_ci_hi") if descent_metrics.get("ran") else None
    decision = apply_decision_rule(
        phase0_pass=True,
        phase_minus1_gate_pass=phase_minus1_gate_pass,
        c_search_bias_control_failure=c_search_bias_control_failure,
        c_null_label_control_failure=c_null_label_control_failure,
        c_connectivity_all_pass=all_connectivity_pass,
        m_gap_ci_lo=m_gap_ci_lo, m_gap_ci_hi=m_gap_ci_hi,
    )
    log("DECISION RULE -> %s" % decision["branch"])
    log("  %s" % decision["reason"])

    total_wall = time.time() - t_run_start
    budget_split["total_wall_seconds"] = total_wall
    budget_split["budget_seconds"] = WALL_CLOCK_BUDGET_SECONDS
    budget_split["note"] = (
        "Explicit split of the 7200s budget across graph reuse, the "
        "two-point feasibility smoke test, C-SEARCH-BIAS, C-CAL-GAP, "
        "modular-polynomial verification, the real Phase -1 search on the "
        "confirmatory prime set (aggregate-counter, real_execution_budget_v2), "
        "any coverage_widening_note extension primes, C-NULL-LABEL, and "
        "descent simulation, per spec.budget.delta_e_search_sub_budget_note "
        "(inherited unchanged from v1).")

    payload.update({
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wall_clock_seconds": total_wall,
        "budget_split_seconds": budget_split,
        "primes": PRIMES,
        "non_fp_rational_counts_by_prime": non_fp_counts,
        "seed_construction": seed_info,
        "correctness_gates": {
            "connectivity": gates["connectivity"],
            "degree_sequence": {p: {k: v for k, v in gates["degree_sequence"][p].items()
                                     if k != "examples"} for p in PRIMES},
            "edgelist_prime": gates["edgelist_prime"],
            "edgelist_check": {k: v for k, v in gates["edgelist_check"].items()
                                if k != "mismatches"},
        },
        "decision": decision,
        "usable_primes_for_fit": usable_primes,
        "objective_boundary": (
            "This run tests for the EXISTENCE of a computable delta_E-"
            "gradient (L4's revisit condition), using the SAME direct "
            "in-session delta_E-computation instrument v1 built, under a "
            "corrected (cumulative-budget) truncation fallback. Neither the "
            "descent test nor the delta_E-computation search constitutes a "
            "complexity claim. Scale: toy, graph sizes 203-1800 vertices; "
            "no result transfers to cryptographic scale."
        ),
        "scale_qualifier": "toy; N (graph size) in [203, 1800]; max log2(p) = %.4f"
                            % math.log2(max(PRIMES)),
    })

    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True, default=str)
    log("wrote %s (%.1fs total)" % (args.out, total_wall))
    print("DECISION %s" % decision["branch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
