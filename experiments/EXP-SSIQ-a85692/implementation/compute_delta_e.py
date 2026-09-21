#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 -- Direct in-session computation of delta_E for the
supersingular 2-isogeny graphs BATCH-003 built, via bounded bidirectional
meet-in-the-middle smooth-degree isogeny search, mirroring
inputs/P13-WESOLOWSKI-2026/paper_fulltext.md Algorithm 1-3 -- followed by
the IDENTICAL (imported, unchanged) M-GAP descent pipeline BATCH-003 froze.

Implements experiments/EXP-SSIQ-a85692/specification.yaml EXACTLY as frozen.
REQUIRED, MANDATORY, EXECUTED-FIRST: the feasibility smoke test at the
LARGEST pre-registered prime (21601), per
inputs.delta_e_computation.feasibility_smoke_test_required_before_phase_minus_1.

REUSE (spec.inputs.reused_from_batch_003, imported unchanged, never forked):
  - build_isogeny_graph.py      (Fp2 arithmetic, Phi_2, BFS, correctness gates)
  - calibration_synthetic.py    (Phase 0 / C-CAL-GAP)
  - descent_hitting_time.py     (OLS-on-logs estimator, population-median-
                                  with-sentinel, content-derived tie-break,
                                  greedy/random hitting-time simulators,
                                  bootstrap CI)
NEW in this experiment (this file, plus its two helper modules):
  - modular_polynomials.py      (Phi_ell for ell in L\\{2}, sourced, PF-2)
  - velu_verify.py              (independent Velu-formula verification, PF-2)
  - compute_delta_e.py          (THIS FILE: the delta_E search instrument,
                                  the feasibility smoke test, the pre-
                                  registered truncation fallback, C-SEARCH-
                                  BIAS, C-BOUND-CHECK, and the four-branch
                                  decision rule)

SEARCH ALGORITHM, DISCLOSED EXACTLY AS IMPLEMENTED
----------------------------------------------------
Algorithm 1 of the frozen source, read literally, requires an existing
non-empty working list L to extend (step 4: "for psi in L such that
ell*deg(psi) <= X"), yet L starts empty (step 1) and no seed entry is ever
described -- the natural completion of its evident intent (build B-smooth-
degree isogenies OUTWARD from E, tracking every reached codomain) is
implemented here via a shortest-degree-first (Dijkstra-style) expansion:

  build_smooth_table(field, start_j, rng, q, L, X):
    table[start_j] = 1   (the trivial degree-1 "isogeny", i.e. E itself)
    repeatedly pop the UNFINALISED table entry of SMALLEST degree d, mark it
    finalised (this IS its true minimal B-smooth degree from start_j, by the
    standard Dijkstra invariant, since every further step multiplies by a
    prime >= 2 -- monotonic, so smaller-degree entries are correctly settled
    first); for each ell in L with d*ell <= X, evaluate Phi_ell(X, j) at the
    finalised codomain and enqueue every root not yet finalised at degree
    d*ell.

This differs from Algorithm 1's own non-backtracking exclusion
("ker(eta) not subset ker(psi-hat)", implemented explicitly by
build_isogeny_graph.py's WALK-time non-backtracking convention for degree-2
descent/random-walk) in one disclosed respect: this table-builder does not
track cyclic-kernel-ness of composed isogeny paths, and its only exclusion
mechanism is "never re-expand an already-finalised (i.e. already reached at
a smaller-or-equal degree) codomain" -- which subsumes excluding the
immediate parent as a SPECIAL CASE (the parent, having smaller degree, is
always already finalised by the time a child is processed) without needing
explicit parent-tracking. This is a disclosed simplification of Algorithm
1's bookkeeping optimisation, not of its correctness property: any reported
collision degree is the true PRODUCT of two genuine isogeny degrees (isogeny
composition always multiplies degree, regardless of kernel cyclicity), so
every reported delta_E value remains a valid upper bound on the true
minimal degree of an isogeny E -> E^{(p)}, which is all this LABELLING
instrument needs (per H-SSIQ-9e2c71's assumptions block).

TWO-SIDED COLLISION SEARCH (spec.inputs.delta_e_computation.method):
  table_E  = build_smooth_table(field, j(E),      ...)
  table_T  = build_smooth_table(field, target_j,  ...)   # E^{(p)}, real arm
  common   = table_E.keys() & table_T.keys()
  delta_E upper bound = min over c in common of table_E[c] * table_T[c]
(For the REAL arm, target_j = field.frobenius(j) = E^{(p)}, per
inputs.delta_e_computation.known_frobenius_twist_construction. For
C-SEARCH-BIAS, target_j is a uniformly random OTHER graph vertex.)
"""

import argparse
import hashlib
import heapq
import json
import math
import os
import platform
import random
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "..", "EXP-SSIQ-58b642", "implementation"))

import build_isogeny_graph as big          # noqa: E402  (REUSED UNCHANGED)
import calibration_synthetic as cal        # noqa: E402  (REUSED UNCHANGED)
import descent_hitting_time as dht         # noqa: E402  (REUSED UNCHANGED)
import modular_polynomials as mp           # noqa: E402  (NEW, this experiment)
import velu_verify as vv                   # noqa: E402  (NEW, this experiment)

EXPERIMENT_ID = "EXP-SSIQ-a85692"
RUN_ID = "RUN-SSIQ-a85692-a"
SEEDS = [20260805, 11, 977]          # spec.replication.seeds -- FROZEN

PRIMES = [2437, 3889, 5737, 7333, 8893, 10657, 12541, 14389, 16189, 18049,
          19717, 21601]              # IDENTICAL to EXP-SSIQ-58b642, reused

# PF-1 FIX APPLIED -- pinned before any real vertex was searched.
B_SMOOTH = 23
X_LIST_BOUND = 23
L_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23]

WALL_CLOCK_BUDGET_SECONDS = 7200
T_PRIME = 0.5 * WALL_CLOCK_BUDGET_SECONDS / len(PRIMES)   # 300.0s, PF-1 fix


# ==========================================================================
# 0. git / environment bookkeeping (same pattern as descent_hitting_time.py)
# ==========================================================================

def git_state():
    def g(*a):
        try:
            return subprocess.check_output(
                ["git"] + list(a), stderr=subprocess.DEVNULL,
                cwd=os.path.dirname(os.path.abspath(__file__))).decode().strip()
        except Exception:
            return None
    return {"commit": g("rev-parse", "HEAD"),
            "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(g("status", "--porcelain"))}


# ==========================================================================
# 1. The delta_E search instrument (NEW code, this experiment)
# ==========================================================================

def neighbors_ell_isogenous(field, j, ell, rng, q):
    if ell == 2:
        f = big.phi2_coeffs_in_X(field, j)
    else:
        f = mp.phi_ell_coeffs_in_X(field, ell, j)
    return big.find_roots_with_multiplicity(field, f, rng, q)


def build_smooth_table(field, start_j, rng, q, L=L_PRIMES, X=X_LIST_BOUND,
                        time_budget_seconds=None, t0=None):
    """Dijkstra-style expansion -- see module docstring. Returns
    (table: {j: degree}, n_phi_calls, timed_out: bool)."""
    if t0 is None:
        t0 = time.time()
    table = {}
    finalized = set()
    heap = [(1, start_j)]
    n_phi_calls = 0
    timed_out = False
    while heap:
        if (time_budget_seconds is not None
                and time.time() - t0 > time_budget_seconds):
            timed_out = True
            break
        d, j = heapq.heappop(heap)
        if j in finalized:
            continue
        finalized.add(j)
        table[j] = d
        for ell in L:
            nd = d * ell
            if nd > X:
                continue
            n_phi_calls += 1
            roots = neighbors_ell_isogenous(field, j, ell, rng, q)
            for r in roots:
                if r not in finalized:
                    heapq.heappush(heap, (nd, r))
    return table, n_phi_calls, timed_out


def two_sided_search(field, source_j, target_j, rng, q,
                      L=L_PRIMES, X=X_LIST_BOUND, time_budget_seconds=None):
    """The delta_E-computation method: build a table from source_j and one
    from target_j, find the minimum-product collision. Returns a full,
    disclosed report dict; resolved=False if no collision is found within
    (B, X) (an UPPER BOUND was searched, not the exact minimal degree, per
    H-SSIQ-9e2c71's assumptions block)."""
    t0 = time.time()
    half_budget = None if time_budget_seconds is None else time_budget_seconds / 2.0
    table_s, calls_s, to_s = build_smooth_table(
        field, source_j, rng, q, L, X, half_budget, t0)
    t_mid = time.time()
    remaining = None if time_budget_seconds is None else max(
        0.0, time_budget_seconds - (t_mid - t0))
    table_t, calls_t, to_t = build_smooth_table(
        field, target_j, rng, q, L, X, remaining, t_mid)
    common = set(table_s) & set(table_t)
    resolved = len(common) > 0
    best_deg = None
    best_codomain = None
    if resolved:
        best_codomain = min(common, key=lambda c: table_s[c] * table_t[c])
        best_deg = table_s[best_codomain] * table_t[best_codomain]
    elapsed = time.time() - t0
    return {
        "resolved": resolved,
        "delta_e_upper_bound": best_deg,
        "table_source_entries": len(table_s),
        "table_target_entries": len(table_t),
        "phi_calls_total": calls_s + calls_t,
        "n_collisions": len(common),
        "timed_out": bool(to_s or to_t),
        "wall_seconds": elapsed,
    }


# ==========================================================================
# 2. Modular polynomial sourcing + independent verification (PF-2)
# ==========================================================================

def verify_modular_polynomials(seeds):
    """PF-2: verify the LARGEST ell actually used (23, since B=23 is pinned)
    via the from-scratch Velu-formula route (velu_verify.py), independent
    of the root-finding route used everywhere else in this experiment.
    Also runs the SAME check on ell=3 as a cheap additional sanity
    companion (NOT required by the frozen contract, which names only the
    largest ell -- disclosed as extra, non-required verification)."""
    report = {}
    required = vv.load_and_verify(23, n_test_curves=3, seed=seeds[0])
    report["ell_23_required"] = required
    extra = vv.load_and_verify(3, n_test_curves=3, seed=seeds[1])
    report["ell_3_additional_not_required"] = extra
    also_verified_against_batch003 = mp.verify_against_known_phi2(big.Fp2Field)
    report["ell_2_parser_sanity_vs_batch003"] = {
        "ok": also_verified_against_batch003[0],
        "detail": also_verified_against_batch003[1],
    }
    all_required_ok = bool(required["all_ok"])
    return report, all_required_ok


# ==========================================================================
# 3. Graph reuse + correctness gates (build_isogeny_graph, unchanged)
# ==========================================================================

def build_all_graphs(primes, seed, time_budget_per_prime=900):
    graphs = {}
    seed_info = {}
    for p in primes:
        rng = random.Random(seed)
        j0, D = big.seed_j_invariant(p)
        ss, trace, A, B = big.verify_seed_supersingular(p, j0)
        if not ss:
            raise RuntimeError(
                "seed j0=%d for p=%d FAILED independent supersingularity "
                "verification (trace=%d != 0)" % (j0, p, trace))
        seed_info[p] = {"j0": j0, "discriminant": D,
                         "trace_verified_zero": trace, "curve_A": A, "curve_B": B}
        g = big.build_graph_bfs(p, j0, rng, time_budget_seconds=time_budget_per_prime)
        graphs[p] = g
    return graphs, seed_info


def run_correctness_gates(graphs, primes, edgelist_prime):
    """C-CONNECTIVITY, M-DEGSEQ, C-EDGELIST.

    PROTOCOL NOTE (disclosed, see execution_report.yaml protocol_deviations):
    EXP-SSIQ-58b642's C-CONNECTIVITY compared the BFS vertex count against
    BOTH the WISDE-reconstructed curve count AND the floor(p/12) formula
    anchor. This experiment's whole reason for existing is that it needs NO
    external dataset for its real arm (H-SSIQ-9e2c71 "WHAT IS NEW"), so
    C-CONNECTIVITY here uses ONLY the floor(p/12) formula anchor (exact,
    epsilon=0, at p = 1 mod 12 per CGL / De Feo Theorem 47) -- the
    self-contained half of the inherited check, not a weaker replacement of
    it: BATCH-003 itself already reports n_built == n_wisde == n_formula in
    every case, so the formula anchor alone carries the identical
    information content for this residue class.
    """
    connectivity = {}
    degseq = {}
    for p in primes:
        g = graphs[p]
        n_built = len(g["vertices"])
        n_formula = p // 12  # p = 1 (mod 12): epsilon = 0 exactly
        connectivity[p] = {"n_built": n_built, "n_formula_floor_p12": n_formula,
                            "pass": bool(n_built == n_formula)}
        degseq[p] = big.degree_sequence_check(g)
    edgelist = big.independent_edgelist_check(graphs[edgelist_prime], edgelist_prime,
                                               rng_seed=SEEDS[1])
    return {"connectivity": connectivity, "degree_sequence": degseq,
            "edgelist_prime": edgelist_prime, "edgelist_check": edgelist}


# ==========================================================================
# 4. Feasibility smoke test (MANDATORY, FIRST, PF-1)
# ==========================================================================

def run_feasibility_smoke_test(graphs, largest_prime, seeds, n_sample_vertices=3):
    g = graphs[largest_prime]
    field = g["field"]
    q = largest_prime * largest_prime
    non_fp = [v for v in g["vertices"] if not field.is_in_fp(v)]
    rng_pick = random.Random(seeds[0])
    sample = rng_pick.sample(non_fp, min(n_sample_vertices, len(non_fp)))
    rng_search = random.Random(seeds[1])
    per_vertex = []
    for v in sample:
        target = field.frobenius(v)
        r = two_sided_search(field, v, target, rng_search, q,
                              L=L_PRIMES, X=X_LIST_BOUND)
        r["vertex"] = list(v)
        r["target"] = list(target)
        per_vertex.append(r)
    total_wall = sum(r["wall_seconds"] for r in per_vertex)
    avg_wall = total_wall / len(per_vertex)
    theoretical_ceiling = (largest_prime / 2.0) ** (1.0 / 3.0)
    resolved_bounds = [r["delta_e_upper_bound"] for r in per_vertex if r["resolved"]]
    return {
        "prime": largest_prime, "n_non_fp_rational_vertices_at_this_prime": len(non_fp),
        "n_sample_vertices": len(sample), "per_vertex": per_vertex,
        "total_wall_seconds": total_wall,
        "avg_wall_seconds_per_vertex": avg_wall,
        "at_least_one_ell_gt_2_evaluated": True,  # L includes 3..23; always true
        "theoretical_ceiling_p_over_2_cube_root": theoretical_ceiling,
        "largest_resolved_bound_in_sample": (max(resolved_bounds)
                                              if resolved_bounds else None),
        "all_sample_resolved": all(r["resolved"] for r in per_vertex),
    }


# ==========================================================================
# 5. Pre-registered truncation fallback (PF-1)
# ==========================================================================

def apply_truncation_fallback(non_fp_counts_by_prime, primes_ascending,
                               measured_per_vertex_cost, t_prime=T_PRIME):
    """spec.inputs.delta_e_computation.scope_reduction_fallback_pinned_before_data,
    applied MECHANICALLY: using the smoke test's OWN single measured
    per-vertex cost (from the largest-prime smoke test only -- never
    re-measured per prime, which would be a different, improvised fallback),
    estimate each prime's full-coverage cost ascending by prime size, and
    truncate to the largest ascending PREFIX whose estimated cost is each
    <= t_prime."""
    per_prime_estimate = []
    confirmatory = []
    still_ascending = True
    for p in primes_ascending:
        n = non_fp_counts_by_prime[p]
        est_cost = n * measured_per_vertex_cost
        fits = est_cost <= t_prime
        per_prime_estimate.append({"prime": p, "n_non_fp_rational": n,
                                    "estimated_full_coverage_seconds": est_cost,
                                    "t_prime": t_prime, "fits_within_t_prime": bool(fits)})
        if fits and still_ascending:
            confirmatory.append(p)
        else:
            still_ascending = False  # PREFIX rule: stop extending once one fails
    return {
        "t_prime_seconds": t_prime,
        "measured_per_vertex_cost_seconds": measured_per_vertex_cost,
        "per_prime_estimate": per_prime_estimate,
        "confirmatory_prime_set": confirmatory,
        "n_confirmatory_primes": len(confirmatory),
        "truncation_fired": len(confirmatory) < len(primes_ascending),
    }


# ==========================================================================
# 6. Real Phase -1 search on the confirmatory prime set (if any)
# ==========================================================================

def run_phase_minus1_on_confirmatory_set(graphs, confirmatory_primes, seeds,
                                          t_prime=T_PRIME):
    """Real delta_E search over the FULL non-F_p-rational vertex set of
    each prime in the confirmatory set, each capped at its own T_prime
    sub-budget (stopping_rules: 'PHASE -1 (delta_E search) BUDGET CAP, per
    prime'). Returns per-prime delta_E maps and M-COVERAGE."""
    results = {}
    for p in confirmatory_primes:
        g = graphs[p]
        field = g["field"]
        q = p * p
        non_fp = [v for v in g["vertices"] if not field.is_in_fp(v)]
        rng_search = random.Random(seeds[0] * 1000003 + p)
        delta_map = {}
        # F_p-rational vertices resolve for free (delta_E = 1 identity)
        for v in g["vertices"]:
            if field.is_in_fp(v):
                delta_map[v] = 1
        t0 = time.time()
        n_resolved = 0
        n_attempted = 0
        for v in non_fp:
            elapsed = time.time() - t0
            remaining = t_prime - elapsed
            if remaining <= 0:
                break
            n_attempted += 1
            target = field.frobenius(v)
            per_vertex_cap = min(remaining, t_prime)  # never exceed remaining sub-budget
            r = two_sided_search(field, v, target, rng_search, q,
                                  L=L_PRIMES, X=X_LIST_BOUND,
                                  time_budget_seconds=per_vertex_cap)
            if r["resolved"]:
                delta_map[v] = r["delta_e_upper_bound"]
                n_resolved += 1
        coverage = (n_resolved + sum(1 for v in g["vertices"] if field.is_in_fp(v))) / \
            float(len(g["vertices"]))
        non_fp_coverage = (n_resolved / float(len(non_fp))) if non_fp else 1.0
        results[p] = {
            "n_vertices": len(g["vertices"]), "n_non_fp_rational": len(non_fp),
            "n_attempted": n_attempted, "n_resolved": n_resolved,
            "m_coverage_non_fp_fraction": non_fp_coverage,
            "m_coverage_all_vertices_fraction": coverage,
            "sub_budget_seconds": t_prime, "wall_seconds_used": time.time() - t0,
            # RAW (Fp2-tuple-keyed) map, for in-process reuse by C-NULL-LABEL
            # and descent_metrics later in main(). NOT JSON-serialisable as
            # -is; a JSON-safe stringified copy is provided separately below.
            "delta_map_raw": delta_map,
            "delta_map_json_safe": {str(list(k)): v for k, v in delta_map.items()},
            "per_prime_coverage_shortfall": bool(non_fp_coverage < 0.5),
        }
    return results


# ==========================================================================
# 7. C-SEARCH-BIAS (REQUIRED, PF-3)
# ==========================================================================

def pearson_corr(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0.0 or syy == 0.0:
        return 0.0
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return sxy / math.sqrt(sxx * syy)


def run_c_search_bias(graphs, smallest_prime, seeds, n_sample=20):
    g = graphs[smallest_prime]
    field = g["field"]
    q = smallest_prime * smallest_prime
    non_fp = [v for v in g["vertices"] if not field.is_in_fp(v)]
    n_sample = min(n_sample, len(non_fp))
    rng_pick = random.Random(seeds[0])
    sample = rng_pick.sample(non_fp, n_sample)
    rng_target = random.Random(seeds[2])
    rng_search_true = random.Random(seeds[1])
    rng_search_rand = random.Random(seeds[1] + 1)

    true_rows = []
    random_rows = []
    for v in sample:
        # TRUE-target arm: target = E^{(p)}, distance measured on the graph
        true_target = field.frobenius(v)
        dist_map = big.bfs_eccentricities_from(g, v)
        true_dist = dist_map.get(true_target)
        r_true = two_sided_search(field, v, true_target, rng_search_true, q,
                                   L=L_PRIMES, X=X_LIST_BOUND)
        true_rows.append({"vertex": list(v), "target": list(true_target),
                           "distance": true_dist,
                           "delta_e_upper_bound": r_true["delta_e_upper_bound"],
                           "resolved": r_true["resolved"]})

        # RANDOM-target arm: target = uniformly random OTHER graph vertex
        # (excluding the vertex itself and, for a cleaner control, the true
        # Frobenius conjugate -- so the random arm never accidentally
        # coincides with the real arm's target).
        candidates = [u for u in g["vertices"] if u != v and u != true_target]
        random_target = candidates[rng_target.randrange(len(candidates))]
        rand_dist = dist_map.get(random_target)
        r_rand = two_sided_search(field, v, random_target, rng_search_rand, q,
                                   L=L_PRIMES, X=X_LIST_BOUND)
        random_rows.append({"vertex": list(v), "target": list(random_target),
                             "distance": rand_dist,
                             "delta_e_upper_bound": r_rand["delta_e_upper_bound"],
                             "resolved": r_rand["resolved"]})

    true_pairs = [(r["distance"], r["delta_e_upper_bound"]) for r in true_rows
                  if r["resolved"] and r["distance"] is not None]
    rand_pairs = [(r["distance"], r["delta_e_upper_bound"]) for r in random_rows
                  if r["resolved"] and r["distance"] is not None]
    corr_true = pearson_corr([a for a, _ in true_pairs], [b for a, b in true_pairs])
    corr_rand = pearson_corr([a for a, _ in rand_pairs], [b for a, b in rand_pairs])

    comparable = None
    if corr_true is not None and corr_rand is not None:
        comparable = bool(abs(corr_rand) >= 0.5 * max(abs(corr_true), 1e-9)
                           or (abs(corr_true) < 0.1 and abs(corr_rand) < 0.1))
    return {
        "prime": smallest_prime, "n_sample": n_sample,
        "true_target_arm": {"rows": true_rows, "n_resolved_with_distance": len(true_pairs),
                             "correlation_distance_vs_degree": corr_true},
        "random_target_arm": {"rows": random_rows, "n_resolved_with_distance": len(rand_pairs),
                               "correlation_distance_vs_degree": corr_rand},
        "magnitudes_comparable_flag": comparable,
        "comparability_rule": (
            "flagged comparable if |corr_random| >= 0.5 * max(|corr_true|, eps), "
            "OR both magnitudes are below 0.1 (both indistinguishable from no "
            "correlation); PRE-REGISTERED comparison rule stated here since "
            "spec.controls.C-SEARCH-BIAS.pre_registered_expectation asserts no "
            "magnitude in advance -- this rule is fixed BEFORE inspecting the "
            "computed correlations in THIS run and is reported as a diagnostic "
            "alongside the raw correlations themselves, which the Coordinator/"
            "Validator can re-judge independently of this specific threshold"),
    }


# ==========================================================================
# 8. C-BOUND-CHECK (free identity; second route disclosed as not attempted)
# ==========================================================================

def run_c_bound_check(graphs, primes):
    report = {}
    for p in primes:
        g = graphs[p]
        field = g["field"]
        locus1 = big.fp_rational_locus(g)
        report[p] = {
            "n_delta_eq_1_by_identity": len(locus1),
            "identity": "delta_E = 1 iff j in F_p (Galois orbit singleton); "
                        "free, exact, requires no search",
        }
    return {
        "per_prime_free_identity_check": report,
        "second_independent_search_route_for_a_small_sample": {
            "attempted": False,
            "reason": (
                "spec.controls.C-BOUND-CHECK states this second cross-check "
                "runs 'budget permitting' and 'does not gate the run.' This "
                "run's budget was allocated to the MANDATORY items (Phase 0, "
                "the feasibility smoke test, the truncation-fallback "
                "arithmetic, C-SEARCH-BIAS's required >=20-vertex sample); "
                "given the Phase -1 gate result (see decision), a second "
                "independent search route for additional vertices was not "
                "run in this pass. Disclosed here rather than silently "
                "omitted, per AGENTS.md rule 8 and the M-BOUND-TIGHTNESS "
                "definition's own non-gating status."
            ),
        },
    }


# ==========================================================================
# 9. Decision rule (four-branch, mechanical, PF-4's glossary)
# ==========================================================================

def apply_decision_rule(phase0_pass, phase_minus1_gate_pass,
                         c_search_bias_control_failure,
                         c_null_label_control_failure,
                         c_connectivity_all_pass,
                         m_gap_ci_lo=None, m_gap_ci_hi=None):
    if not phase0_pass:
        return {"branch": "N/A-STOPPED-AT-PHASE-0",
                "reason": "C-CAL-GAP failed; run stopped before Phase -1/Phase 1 "
                          "per stopping_rules and invalidation_rules."}
    if not phase_minus1_gate_pass:
        return {"branch": "DATA-UNAVAILABLE-BLOCKED",
                "reason": ("Phase -1 gate failed: M-COVERAGE >= 0.5 was not "
                           "achieved on at least 4 primes (see "
                           "truncation_fallback and phase_minus1_real_search "
                           "in raw-result.json). Per "
                           "outcome_scope_label_glossary this is the NAMED, "
                           "DISTINCT branch from CONTROL-FAILURE-VOID: no "
                           "data existed to test either direction.")}
    if c_search_bias_control_failure or c_null_label_control_failure or not c_connectivity_all_pass:
        return {"branch": "CONTROL-FAILURE-VOID",
                "reason": ("C-SEARCH-BIAS, C-NULL-LABEL, or C-CONNECTIVITY "
                           "failed; signal is contaminated (see "
                           "outcome_scope_label_glossary).")}
    if m_gap_ci_lo is not None and m_gap_ci_lo > 0.0:
        return {"branch": "DETECTED",
                "reason": ("M-GAP's bootstrap 95%% CI [%.6f, %.6f] excludes 0 "
                           "in the positive direction" % (m_gap_ci_lo, m_gap_ci_hi))}
    return {"branch": "UNRESOLVED-BY-THIS-TEST",
            "reason": "M-GAP's CI includes 0 or excludes 0 in the negative "
                      "direction, or M-GAP was not computed under a passing "
                      "Phase -1 gate; per falsification_criterion this is "
                      "reported as 'unresolved by this test', never "
                      "'falsified' or 'refuted'."}


# ==========================================================================
# 10. Main orchestration
# ==========================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    t_run_start = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log = lambda s: print(s, flush=True)  # noqa: E731

    log("[%s] %s / %s" % (started, EXPERIMENT_ID, RUN_ID))
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

    # ---- Modular polynomial sourcing + independent verification (PF-2) --
    log("Verifying sourced modular polynomials (PF-2): ell=23 REQUIRED via "
        "Velu-formula independent route, ell=3 additional sanity companion")
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

    # ---- Graph reuse: build all 12 graphs (cheap, reused code) -----------
    log("Building/reusing %d graphs via Phi_2 BFS (build_isogeny_graph.py, "
        "unchanged from EXP-SSIQ-58b642)" % len(PRIMES))
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

    log("running correctness gates: C-CONNECTIVITY (floor(p/12) anchor, see "
        "run_correctness_gates docstring), M-DEGSEQ, C-EDGELIST")
    gates = run_correctness_gates(graphs, PRIMES, edgelist_prime=PRIMES[0])
    all_connectivity_pass = all(gates["connectivity"][p]["pass"] for p in PRIMES)
    all_degseq_pass = all(gates["degree_sequence"][p]["pass"] for p in PRIMES)
    log("  C-CONNECTIVITY all pass: %s" % all_connectivity_pass)
    log("  M-DEGSEQ all pass: %s" % all_degseq_pass)
    log("  C-EDGELIST (p=%d): pass=%s" % (PRIMES[0], gates["edgelist_check"]["pass"]))

    # ---- PF-1: MANDATORY FEASIBILITY SMOKE TEST (largest prime, FIRST) --
    log("MANDATORY FEASIBILITY SMOKE TEST at largest pre-registered prime "
        "p=%d (PF-1, run BEFORE Phase -1 proceeds across the full prime set)"
        % PRIMES[-1])
    t0 = time.time()
    smoke = run_feasibility_smoke_test(graphs, PRIMES[-1], SEEDS, n_sample_vertices=3)
    budget_split["feasibility_smoke_test_seconds"] = time.time() - t0
    log("  smoke test: %d vertices, avg %.3fs/vertex, all_resolved=%s (%.3fs total)"
        % (smoke["n_sample_vertices"], smoke["avg_wall_seconds_per_vertex"],
           smoke["all_sample_resolved"], budget_split["feasibility_smoke_test_seconds"]))
    payload["feasibility_smoke_test"] = smoke

    # ---- PF-1: apply the pre-registered truncation fallback -------------
    log("Applying pre-registered truncation fallback using the smoke test's "
        "OWN measured per-vertex cost (T_prime=%.1fs)" % T_PRIME)
    truncation = apply_truncation_fallback(
        non_fp_counts, PRIMES, smoke["avg_wall_seconds_per_vertex"], T_PRIME)
    for row in truncation["per_prime_estimate"]:
        log("  p=%-6d n_non_fp=%-5d est_cost=%8.1fs fits_T_prime=%s"
            % (row["prime"], row["n_non_fp_rational"],
               row["estimated_full_coverage_seconds"], row["fits_within_t_prime"]))
    log("  confirmatory_prime_set = %r (n=%d)" % (truncation["confirmatory_prime_set"],
                                                    truncation["n_confirmatory_primes"]))
    payload["truncation_fallback"] = truncation

    phase_minus1_gate_pass = truncation["n_confirmatory_primes"] >= 4

    # ---- Phase -1 real search on confirmatory set (if any) --------------
    t0 = time.time()
    phase_minus1_results = {}
    if truncation["confirmatory_prime_set"]:
        log("Running REAL delta_E search on the %d confirmatory prime(s) "
            "(each capped at its own T_prime=%.1fs sub-budget)"
            % (truncation["n_confirmatory_primes"], T_PRIME))
        phase_minus1_results = run_phase_minus1_on_confirmatory_set(
            graphs, truncation["confirmatory_prime_set"], SEEDS, T_PRIME)
        for p, r in phase_minus1_results.items():
            log("  p=%-6d M-COVERAGE(non-fp)=%.4f attempted=%d resolved=%d"
                % (p, r["m_coverage_non_fp_fraction"], r["n_attempted"], r["n_resolved"]))
    else:
        log("Confirmatory prime set is EMPTY -- per "
            "scope_reduction_fallback_pinned_before_data, Phase -1 is NOT "
            "run on any further prime beyond the smoke test itself "
            "('do not discover the overshoot partway through the prime set').")
    budget_split["delta_e_search_proper_seconds"] = time.time() - t0
    # JSON-safe copy for the payload: drop delta_map_raw (Fp2-tuple-keyed,
    # not JSON-serialisable) and rename delta_map_json_safe -> delta_map for
    # the on-disk record. phase_minus1_results itself (with delta_map_raw
    # intact) is retained in-process for C-NULL-LABEL and descent_metrics
    # below, which run AFTER this point in main().
    def _json_safe_phase_minus1_row(r):
        out = {k: v for k, v in r.items()
               if k not in ("delta_map_raw", "delta_map_json_safe")}
        out["delta_map"] = r["delta_map_json_safe"]
        return out

    payload["phase_minus1_real_search"] = {
        p: _json_safe_phase_minus1_row(r) for p, r in phase_minus1_results.items()
    }

    n_primes_coverage_pass = sum(
        1 for p, r in phase_minus1_results.items()
        if r["m_coverage_non_fp_fraction"] >= 0.5)
    phase_minus1_gate_pass = n_primes_coverage_pass >= 4
    log("Phase -1 gate (M-COVERAGE>=0.5 on >=4 primes): pass=%s (n_primes_pass=%d)"
        % (phase_minus1_gate_pass, n_primes_coverage_pass))

    # ---- C-SEARCH-BIAS (REQUIRED, run regardless of the Phase -1 gate, ---
    # per its own mandate: "at the SMALLEST pre-registered prime", not
    # conditioned on that prime surviving truncation for the MAIN M-GAP fit)
    log("Running C-SEARCH-BIAS (REQUIRED control, PF-3) at smallest "
        "pre-registered prime p=%d, >=20 sampled non-F_p-rational vertices"
        % PRIMES[0])
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

    # ---- C-BOUND-CHECK ----------------------------------------------------
    log("Running C-BOUND-CHECK (free delta_E=1 identity cross-check)")
    bound_check = run_c_bound_check(graphs, PRIMES)
    payload["c_bound_check"] = bound_check

    # ---- C-NULL-LABEL: only meaningful/runnable if real per-vertex labels
    # exist for at least one full prime (needs a FULL delta_E multiset for
    # that prime to shuffle) -----------------------------------------------
    budget_split["c_search_bias_and_null_label_seconds"] = budget_split["c_search_bias_seconds"]
    c_null_label_report = {"ran": False}
    c_null_label_control_failure = False
    if phase_minus1_gate_pass:
        log("Running C-NULL-LABEL (shuffled real-computed delta_E multiset) "
            "on the confirmatory prime set")
        t0 = time.time()
        null_by_prime = {}
        for p in truncation["confirmatory_prime_set"]:
            g = graphs[p]
            # Use the RAW (Fp2-tuple-keyed) delta map kept in-process by
            # run_phase_minus1_on_confirmatory_set (delta_map_raw), never the
            # JSON-safe stringified copy.
            diam = big.bfs_diameter(g)
            multiset = list(phase_minus1_results[p]["delta_map_raw"].values())
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
        # A prime with fewer than full coverage cannot contribute; if too
        # few primes contribute, C-NULL-LABEL cannot be judged and is
        # reported as such rather than forced to a verdict.
        usable = [p for p in null_by_prime if not null_by_prime[p].get("skipped")]
        c_null_label_report["n_primes_usable"] = len(usable)
    payload["c_null_label"] = c_null_label_report

    # ---- Descent metrics (M-GAMMA-GREEDY/RANDOM/M-GAP) -- only if the ----
    # Phase -1 gate passed on real labels for the FULL confirmatory prime set
    descent_metrics = {"ran": False}
    if phase_minus1_gate_pass:
        log("Running descent metrics (M-GAMMA-GREEDY, M-GAMMA-RANDOM, M-GAP) "
            "on the real computed delta_E labels")
        t0 = time.time()
        usable_primes = [p for p in truncation["confirmatory_prime_set"]
                          if phase_minus1_results[p]["m_coverage_non_fp_fraction"] >= 0.5]
        per_prime = {}
        for p in usable_primes:
            g = graphs[p]
            vertices = list(g["vertices"])
            delta_map = phase_minus1_results[p]["delta_map_raw"]
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
                             "random_median": rw["median"]}
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
                                "m_gap": m_gap, "m_gap_ci_lo": lo, "m_gap_ci_hi": hi}
        else:
            descent_metrics = {"ran": False,
                                "reason": "fewer than 4 primes had full delta_E "
                                          "coverage after Phase -1"}
        budget_split["descent_simulation_seconds"] = time.time() - t0
    payload["descent_metrics"] = descent_metrics

    # ---- Decision rule (mechanical) --------------------------------------
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
        "feasibility smoke test, delta_E search proper, C-CAL-GAP, "
        "C-SEARCH-BIAS, and descent simulation, per "
        "spec.budget.delta_e_search_sub_budget_note.")

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
        "objective_boundary": (
            "This run tests for the EXISTENCE of a computable delta_E-"
            "gradient (L4's revisit condition), using a NEW direct in-"
            "session delta_E-computation instrument. Neither the descent "
            "test nor the delta_E-computation search constitutes a "
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
