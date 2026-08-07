#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v8 (BATCH-011) -- delta_e_independent_rng_probe_v8.

Implements experiments/EXP-SSIQ-a85692/specification_v8.yaml
inputs.probe_delta_e_search_v8 (PART A) and
inputs.probe_permutation_null_control_v8 (PART B) EXACTLY as frozen
(version 8, frozen_at 2026-08-06). Single prime only: p=2437, the SAME
prime and the SAME rebuilt graph (pinned graph-construction seed 20260805)
RUN-SSIQ-a85692-b already searched under the ORIGINAL procedure
(compute_delta_e_v2.py's real_execution_budget_v2, a shared, sequentially-
advancing search RNG under a shrinking aggregate time budget). This probe
re-runs the delta_E search on the identical graph using INDEPENDENT,
freshly-seeded per-vertex RNG under a FIXED (never-shrinking) per-vertex
time budget, isolating the ONE variable PF-6 names as a confound.

REUSE / DUPLICATION SPLIT, DISCLOSED EXPLICITLY (matches
required_artifacts_note's own (i)/(ii) split):
  (i)  GENUINELY IMPORTED, UNCHANGED: compute_delta_e.two_sided_search,
       compute_delta_e.L_PRIMES, compute_delta_e.X_LIST_BOUND;
       trapping_diagnostic_v5.build_graph_for_prime,
       trapping_diagnostic_v5.load_archived_prime_data;
       delta_e_permutation_null_control_v7.depth0_fraction,
       delta_e_permutation_null_control_v7.summary_stats.
       DISCLOSED DISCREPANCY (HONESTY RULE, per AGENTS.md rule 9 and this
       run's own execution_report.yaml): specification_v8.yaml's
       amendment_scope PROCEDURE step (1) explicitly REQUIRES re-running
       "the same two-part graph-identity verification v6/v7 already
       established (degree_sequence_check, IMPORTED UNCHANGED from
       build_isogeny_graph, plus a rebuilt-vertex-count match against the
       archived n_vertices=203 for p=2437), before any delta_E search
       begins" (PF-8's own fix) -- yet required_artifacts_note's own
       function-level "GENUINELY IMPORTS, UNCHANGED" list does NOT mention
       build_isogeny_graph.degree_sequence_check anywhere. This file
       resolves the discrepancy by following amendment_scope's explicit,
       reasoned instruction (the more specific, more recently-justified
       text, and the one carrying PF-8's own named fix) and imports
       build_isogeny_graph.degree_sequence_check UNCHANGED, exactly as
       every prior amendment since v5 (trapping_diagnostic_v5.py,
       delta_e_permutation_null_control_v7.py) already does for the same
       purpose -- but reports this required_artifacts_note omission
       explicitly rather than silently reconciling it.
  (ii) AUTHORIZED, DISCLOSED DUPLICATES (new code this amendment's driver
       writes, per PF-12's own required disclosure): the PART A per-vertex
       search-loop orchestration and the REQUIRED CONSTRUCTION STEP wiring
       F_p-rational vertices (PF-9's fix, matching
       compute_delta_e_v2.py:259-261's own construction exactly); the PART
       B 1000-trial permutation loop (base_values/shuffle/zip construction,
       an authorized, disclosed duplicate of
       delta_e_permutation_null_control_v7.run_for_prime's own inline
       logic -- run_for_prime itself is NOT imported); a small git_state()
       helper (infra bookkeeping only, the same trivial pattern every prior
       module in this lineage repeats, never a research function).

Does NOT import or call compute_delta_e.run_phase_minus1_on_confirmatory_set
NOR compute_delta_e_v2.run_phase_minus1_on_confirmatory_set
(real_execution_budget_v2) anywhere -- both are the ORIGINAL, superseded
orchestration procedures this amendment tests against, superseded by
addition, never by edit.

JSON SAFETY (PF-13): every vertex-keyed artifact output in this file uses
the IDENTICAL str(list(v))-keyed convention compute_delta_e_v2.py's own
delta_map_json_safe already established. A raw Fp2-tuple is NEVER written
directly as a JSON dict key; where a vertex must be associated with a value
in a JSON list, the vertex is nested as a list-valued element instead.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import random
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
import build_isogeny_graph as big  # noqa: E402  (FROZEN, UNCHANGED -- (i)
                                    # genuine-import source for
                                    # degree_sequence_check; see the
                                    # DISCLOSED DISCREPANCY note above)
import trapping_diagnostic_v5 as tdv5  # noqa: E402  (FROZEN, UNCHANGED --
                                        # (i) genuine-import source for
                                        # build_graph_for_prime /
                                        # load_archived_prime_data)
import delta_e_permutation_null_control_v7 as v7  # noqa: E402  (FROZEN,
                                        # UNCHANGED -- (i) genuine-import
                                        # source for depth0_fraction /
                                        # summary_stats)
import compute_delta_e  # noqa: E402  (FROZEN, UNCHANGED -- (i) genuine-
                         # import source for two_sided_search / L_PRIMES /
                         # X_LIST_BOUND)

EXPERIMENT_ID = "EXP-SSIQ-a85692"
RUN_ID = "RUN-SSIQ-a85692-h"
SPEC_VERSION = 8

PRIME = 2437
ARCHIVED_N_VERTICES = 203
ARCHIVED_N_NON_FP_RATIONAL = 194
ARCHIVED_N_FP_RATIONAL = ARCHIVED_N_VERTICES - ARCHIVED_N_NON_FP_RATIONAL  # 9

GRAPH_SEED = 20260805     # SEEDS[0], the pinned graph-construction seed
                          # every amendment since v5 has used. NEVER reused
                          # as the search RNG role in this file.
BASE_SEED = 20260811      # NEW, fourth, distinct, newly-pinned constant for
                          # this amendment (PART A's per-vertex RNG
                          # derivation root); never reused from any prior
                          # seed role in this experiment.
PERMUTATION_SEED = 20260806  # SAME constant v7 used, for direct
                              # comparability (PART B).
N_TRIALS = 1000
PER_VERTEX_BUDGET_SECONDS = 15.0  # FIXED CONSTANT -- never a function of
                                   # elapsed or remaining time.

# specification_v8.yaml inputs.probe_permutation_null_control_v8's own
# PRE-REGISTERED thresholds, stated here verbatim before this amendment is
# executed.
PERSISTS_MIN_REAL_DEPTH0_FRACTION = 0.95
PERSISTS_MIN_MARGIN_POINTS = 13.1

RUN_B_RAW_RESULT_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-b", "raw-result.json")


class ProbeError(RuntimeError):
    """Raised on a genuinely unanticipated halt condition this frozen
    contract does not itself specify a recovery path for (e.g. the
    graph-identity re-verification failing, which the contract requires be
    RE-RUN but does not state what should happen on failure)."""


# ==========================================================================
# derive_per_vertex_seed -- EXACT formula from specification_v8.yaml
# inputs.probe_delta_e_search_v8, (1).
# ==========================================================================

def derive_per_vertex_seed(base_seed, vertex):
    payload = "SSIQ-v8-probe:%d:%r" % (base_seed, tuple(int(c) for c in vertex))
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


# ==========================================================================
# PF-8: two-part graph-identity re-verification (amendment_scope PROCEDURE
# step (1)), re-run BEFORE any delta_E search begins. (ii) authorized,
# disclosed duplicate of trapping_diagnostic_v5.py / v7's own inline
# verification, using ONLY the genuinely-imported degree_sequence_check.
# ==========================================================================

def verify_graph_identity(g, archived_n_vertices=ARCHIVED_N_VERTICES):
    degseq = big.degree_sequence_check(g)
    n_built = len(g["vertices"])
    vertex_count_match = bool(n_built == archived_n_vertices)
    degseq_pass = bool(degseq["pass"])
    return {
        "degree_sequence_check": degseq,
        "n_built_vertices": n_built,
        "archived_n_vertices": archived_n_vertices,
        "vertex_count_match": vertex_count_match,
        "pass": bool(degseq_pass and vertex_count_match),
    }


# ==========================================================================
# PART A: probe_delta_e_search_v8.
# ==========================================================================

def run_probe_delta_e_search_v8(graph, base_seed, per_vertex_budget_seconds):
    field = graph["field"]
    q = graph["q"]
    vertices = graph["vertices"]
    fp_rational = [v for v in vertices if field.is_in_fp(v)]
    non_fp_rational = [v for v in vertices if not field.is_in_fp(v)]

    # REQUIRED CONSTRUCTION STEP (PF-9 fix), BEFORE the per-vertex search
    # loop begins: new_delta_map[v] = 1 for EVERY F_p-rational v, matching
    # compute_delta_e_v2.py:259-261's own construction exactly.
    new_delta_map = {}
    for v in fp_rational:
        new_delta_map[v] = 1

    per_vertex_records = []
    n_resolved = 0
    n_attempted = 0
    for v in non_fp_rational:
        n_attempted += 1
        seed_v = derive_per_vertex_seed(base_seed, v)
        # FRESH instance, never shared or advanced across vertices.
        rng_v = random.Random(seed_v)
        target = field.frobenius(v)
        r = compute_delta_e.two_sided_search(
            field, v, target, rng_v, q,
            L=compute_delta_e.L_PRIMES, X=compute_delta_e.X_LIST_BOUND,
            time_budget_seconds=per_vertex_budget_seconds)
        resolved = bool(r["resolved"])
        if resolved:
            new_delta_map[v] = r["delta_e_upper_bound"]
            n_resolved += 1
        per_vertex_records.append({
            "vertex": list(v),
            "seed_used": seed_v,
            "resolved": resolved,
            "delta_e_upper_bound": r["delta_e_upper_bound"],
            "wall_seconds": r["wall_seconds"],
            "timed_out": bool(r["timed_out"]),
        })

    n_non_fp_rational = len(non_fp_rational)
    coverage_fraction = (
        (n_resolved / float(n_non_fp_rational)) if n_non_fp_rational else None)

    return {
        "new_delta_map_raw": new_delta_map,  # tuple-keyed, in-process only
        "per_vertex_records": per_vertex_records,
        "n_resolved": n_resolved,
        "n_attempted": n_attempted,
        "n_non_fp_rational": n_non_fp_rational,
        "n_fp_rational_wired_unconditionally": len(fp_rational),
        "coverage_fraction": coverage_fraction,
    }


def delta_map_json_safe(delta_map):
    """PF-13's required convention (compute_delta_e_v2.py lines 291-303):
    str(list(v))-keyed, never a raw tuple as a JSON dict key."""
    return {str(list(k)): v for k, v in delta_map.items()}


# ==========================================================================
# REQUIRED COMPARISON against RUN-SSIQ-a85692-b's archived delta_map.
# ==========================================================================

def compare_against_archived(new_delta_map, archived_delta_map,
                              non_fp_rational_set):
    """For every vertex resolved in BOTH the new and archived search,
    report whether delta_e_upper_bound MATCHES exactly. The frozen spec
    text does not explicitly restrict this comparison's domain to the
    non-F_p-rational vertices (unlike coverage_fraction, which explicitly
    does) -- DISCLOSED INTERPRETATION (HONESTY RULE): computed here over
    the FULL new_delta_map/archived_delta_map key intersection (all
    resolved vertices, including the 9 F_p-rational vertices, which
    trivially match at value 1 in both since both maps wire them in via
    the identical unconditional identity), WITH a non-F_p-rational-only
    breakdown also reported for transparency, so neither reading is
    silently discarded."""
    archived_keys = set(archived_delta_map.keys())
    new_keys = set(new_delta_map.keys())
    both_resolved = archived_keys & new_keys

    value_matches = []
    value_differs = []
    nfp_both_resolved = 0
    nfp_value_matches = 0
    nfp_value_differs = 0
    for v in both_resolved:
        is_nfp = v in non_fp_rational_set
        if is_nfp:
            nfp_both_resolved += 1
        if archived_delta_map[v] == new_delta_map[v]:
            value_matches.append(v)
            if is_nfp:
                nfp_value_matches += 1
        else:
            value_differs.append({
                "vertex": list(v),
                "archived_value": archived_delta_map[v],
                "new_value": new_delta_map[v],
            })
            if is_nfp:
                nfp_value_differs += 1

    return {
        "domain_note": (
            "Computed over the full new/archived delta_map key "
            "intersection (203-vertex domain at full coverage), including "
            "the 9 F_p-rational vertices which trivially match at value 1 "
            "in both maps by the unconditional identity wiring -- see "
            "non_fp_rational_only sub-breakdown below for the search-only "
            "figures."
        ),
        "n_both_resolved": len(both_resolved),
        "n_value_matches": len(value_matches),
        "n_value_differs": len(value_differs),
        "value_differs_triples": value_differs,
        "n_new_resolved_archived_was_not": len(new_keys - archived_keys),
        "n_archived_resolved_new_was_not": len(archived_keys - new_keys),
        "non_fp_rational_only": {
            "n_both_resolved": nfp_both_resolved,
            "n_value_matches": nfp_value_matches,
            "n_value_differs": nfp_value_differs,
        },
    }


# ==========================================================================
# PF-1 / PF-9's own strengthened gate: len(new_delta_map) == 203, checked
# directly, NOT coverage_fraction alone. PART B does not run if this fails.
# ==========================================================================

def check_coverage_gate(new_delta_map, graph, field):
    vertices = graph["vertices"]
    expected = len(vertices)
    actual = len(new_delta_map)
    gate_pass = bool(actual == expected == ARCHIVED_N_VERTICES)
    missing = []
    if not gate_pass:
        present = set(new_delta_map.keys())
        for v in vertices:
            if v not in present:
                missing.append({
                    "vertex": list(v),
                    "is_fp_rational": bool(field.is_in_fp(v)),
                })
    return {
        "len_new_delta_map": actual,
        "len_graph_vertices": expected,
        "archived_n_vertices": ARCHIVED_N_VERTICES,
        "gate_pass": gate_pass,
        "missing_vertices": missing,
    }


# ==========================================================================
# PART B: probe_permutation_null_control_v8. Only called if the gate above
# passed. (ii) authorized, disclosed duplicate of
# delta_e_permutation_null_control_v7.run_for_prime's own base_values/
# shuffle/zip construction (PF-12) -- run_for_prime itself is NOT imported.
# ==========================================================================

def run_probe_permutation_null_control_v8(new_delta_map, vertices, adjacency,
                                           permutation_seed=PERMUTATION_SEED,
                                           n_trials=N_TRIALS):
    real_stats = v7.depth0_fraction(new_delta_map, vertices, adjacency)
    real_depth0_fraction = real_stats["fraction"]

    # SINGLE freshly-constructed random.Random(PERMUTATION_SEED) instance,
    # never re-seeded per trial.
    rng = random.Random(permutation_seed)
    base_values = list(new_delta_map.values())
    null_fractions = []
    null_n_local_min = []
    null_n_depth0 = []
    for _trial in range(n_trials):
        values = list(base_values)      # fresh copy of the SAME real multiset
        rng.shuffle(values)             # single persistent rng instance
        permuted_map = dict(zip(vertices, values))
        stats = v7.depth0_fraction(permuted_map, vertices, adjacency)
        null_fractions.append(stats["fraction"])
        null_n_local_min.append(stats["n_local_min"])
        null_n_depth0.append(stats["n_depth0"])

    # DISCLOSED, UNANTICIPATED-EDGE-CASE GUARD (HONESTY RULE): the frozen
    # spec's own construction text does not mention filtering undefined
    # (None) trial fractions, and depth0_fraction's own docstring states
    # n_local_min>=1 always holds mathematically (the globally-minimum-
    # valued vertex is always a structural local minimum under any
    # permutation of the same multiset) -- so None is not expected here.
    # If it is nonetheless observed, this is reported as a disclosed
    # anomaly, never silently dropped nor allowed to crash summary_stats.
    n_none = sum(1 for f in null_fractions if f is None)
    stat_input = [f for f in null_fractions if f is not None]
    stats_summary = v7.summary_stats(stat_input, n_trials) if stat_input else None

    anomaly = None
    if n_none:
        anomaly = {
            "id": "ANOM-NULLNONE-v8-p%d" % PRIME,
            "statement": (
                "%d of %d null trials produced an undefined depth0_fraction "
                "(zero local minima in that permuted trial) -- "
                "mathematically unexpected per depth0_fraction's own "
                "documented invariant, disclosed rather than silently "
                "dropped; excluded from null_summary_statistics above."
                % (n_none, n_trials)),
        }

    if real_depth0_fraction is None or stats_summary is None:
        # Genuinely unanticipated by the frozen contract's exhaustive
        # binary PERSISTS/WEAKENS split, which presumes both quantities are
        # defined. Reported as a disclosed anomaly, not forced into either
        # branch.
        outcome = "AMBIGUOUS"
        margin = None
        null_max = None
        anomaly = anomaly or {}
        anomaly.setdefault("id", "ANOM-UNDEFINED-STAT-v8-p%d" % PRIME)
        anomaly["statement"] = (
            (anomaly.get("statement", "") + " ") if anomaly.get("statement") else ""
        ) + (
            "real_depth0_fraction or the null distribution's own summary "
            "statistics were undefined -- the frozen spec's "
            "PERSISTS/WEAKENS binary split presumes both are defined "
            "numbers, so this genuinely unanticipated edge case is "
            "reported as AMBIGUOUS/disclosed anomaly rather than forced "
            "into either branch."
        )
    else:
        null_max = max(f for f in null_fractions if f is not None)
        margin = (real_depth0_fraction - null_max) * 100.0
        if (real_depth0_fraction >= PERSISTS_MIN_REAL_DEPTH0_FRACTION
                and margin >= PERSISTS_MIN_MARGIN_POINTS):
            outcome = "PERSISTS"
        else:
            outcome = "WEAKENS"

    null_exceeds_or_equals_real_count = sum(
        1 for f in null_fractions
        if f is not None and real_depth0_fraction is not None
        and f >= real_depth0_fraction)

    return {
        "part_b_did_not_run": False,
        "prime": PRIME,
        "permutation_seed_used": permutation_seed,
        "n_trials": n_trials,
        "real_depth0_fraction": {
            "n_vertices": len(vertices),
            "n_structural_local_min": real_stats["n_local_min"],
            "n_depth0": real_stats["n_depth0"],
            "fraction": real_depth0_fraction,
        },
        "null_depth0_fractions": null_fractions,
        "null_n_local_min": null_n_local_min,
        "null_n_depth0": null_n_depth0,
        "null_summary_statistics": stats_summary,
        "null_n_undefined_trials_excluded": n_none,
        "null_max": null_max,
        "margin_percentage_points": margin,
        "margin_formula": (
            "(REAL_DEPTH0_FRACTION - max(NULL_DEPTH0_FRACTIONS)) * 100, "
            "using THIS run's own new REAL_DEPTH0_FRACTION and THIS run's "
            "own 1000-trial null distribution's maximum."
        ),
        "null_exceeds_or_equals_real_count": null_exceeds_or_equals_real_count,
        "thresholds_pre_registered": {
            "persists_min_real_depth0_fraction": PERSISTS_MIN_REAL_DEPTH0_FRACTION,
            "persists_min_margin_percentage_points": PERSISTS_MIN_MARGIN_POINTS,
        },
        "outcome": outcome,
        "anomaly": anomaly,
        "objective_boundary": (
            "This is a DIAGNOSTIC CONTROL, not a claim. It does not test "
            "H-SSIQ-36e970's real-arm prediction, does not gate any "
            "decision rule, and does not itself constitute evidence for or "
            "against a computable delta_E-gradient or a p^{1/4} algorithm, "
            "regardless of whether its result is PERSISTS, WEAKENS, or "
            "AMBIGUOUS. A PERSISTS result would license restoring "
            "DEC-20260806-498531 D-2's 'genuine structural fact' language "
            "for THIS ONE PRIME ONLY, not extending it to the other three "
            "primes (untested by this probe) or to any claim about "
            "H-SSIQ-36e970 or lever L4."
        ),
    }


def coverage_shortfall_record(gate, coverage_fraction):
    return {
        "part_b_did_not_run": True,
        "outcome": "COVERAGE-SHORTFALL",
        "prime": PRIME,
        "coverage_fraction_non_fp_rational_only": coverage_fraction,
        "len_new_delta_map": gate["len_new_delta_map"],
        "len_graph_vertices": gate["len_graph_vertices"],
        "archived_n_vertices": gate["archived_n_vertices"],
        "missing_vertices": gate["missing_vertices"],
        "note": (
            "PART B DID NOT RUN. len(new_delta_map) != len(graph[\"vertices\"]) "
            "!= 203, per specification_v8.yaml's own PF-1/PF-9 strengthened "
            "gate. This is an honest, informative outcome, not a failure to "
            "be worked around -- a fixed 15s per-vertex budget proving too "
            "tight for full coverage is itself evidence about the search's "
            "own timing properties. PF-11's own disclosure applies "
            "verbatim: neither half of PF-6's confound (RNG-sharing or "
            "budget-shape) was actually tested this run, since a "
            "partial-coverage REAL_DEPTH0_FRACTION is not comparable to "
            "v7's own full-194-vertex REAL_DEPTH0_FRACTION=1.0 baseline."
        ),
    }


# ==========================================================================
# git / environment bookkeeping (ii) -- small, non-research duplicate of the
# same trivial pattern every prior module in this lineage repeats.
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
                          "delta_map)")
    args = ap.parse_args()

    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log = lambda s: print(s, flush=True)  # noqa: E731

    log("[%s] %s / %s (specification_v8.yaml)" % (started, EXPERIMENT_ID, RUN_ID))
    log("delta_e_independent_rng_probe_v8: prime=%d GRAPH_SEED=%d "
        "BASE_SEED=%d PERMUTATION_SEED=%d PER_VERTEX_BUDGET_SECONDS=%.1f "
        "N_TRIALS=%d" % (PRIME, GRAPH_SEED, BASE_SEED, PERMUTATION_SEED,
                          PER_VERTEX_BUDGET_SECONDS, N_TRIALS))

    run_dir = args.run_dir
    os.makedirs(run_dir, exist_ok=True)

    # ---- (1) rebuild the graph (IMPORTED UNCHANGED) + re-run the two-part
    # graph-identity verification (PF-8), before any delta_E search begins.
    log("Rebuilding graph for p=%d via trapping_diagnostic_v5.build_graph_for_prime "
        "(IMPORTED UNCHANGED, seed=%d)" % (PRIME, GRAPH_SEED))
    g, seed_info = tdv5.build_graph_for_prime(PRIME, GRAPH_SEED)
    field = g["field"]

    log("Re-running two-part graph-identity verification (PF-8): "
        "degree_sequence_check (IMPORTED UNCHANGED from build_isogeny_graph) "
        "+ rebuilt-vertex-count match against archived n_vertices=%d"
        % ARCHIVED_N_VERTICES)
    graph_identity = verify_graph_identity(g, ARCHIVED_N_VERTICES)
    log("  graph_identity_verification pass=%s (n_built=%d, degseq_pass=%s)"
        % (graph_identity["pass"], graph_identity["n_built_vertices"],
           graph_identity["degree_sequence_check"]["pass"]))

    graph_identity_failed_halt = None
    if not graph_identity["pass"]:
        # GENUINELY UNANTICIPATED by the frozen contract text: amendment_scope
        # REQUIRES this re-verification but does not state what to do on
        # failure. Per the campaign's own HONESTY RULE, this halts PART A/
        # PART B rather than proceeding on a graph that failed its own
        # required identity check, and is reported explicitly, not silently
        # worked around.
        graph_identity_failed_halt = (
            "Graph-identity re-verification (PF-8) FAILED. "
            "specification_v8.yaml's amendment_scope requires this check be "
            "re-run before any delta_E search begins but does not specify "
            "a recovery path on failure; this Executor halts PART A/PART B "
            "on this genuinely unanticipated condition rather than "
            "proceeding on an unverified graph, per the governing HONESTY "
            "RULE (report, do not improvise past a specification gap)."
        )
        log("HALTING: %s" % graph_identity_failed_halt)

    non_fp_rational_set = set(v for v in g["vertices"] if not field.is_in_fp(v))

    part_a_result = None
    comparison = None
    gate = None
    part_b_result = None

    if graph_identity_failed_halt is None:
        # ---- (2) PART A: independent per-vertex RNG search --------------
        log("PART A: probe_delta_e_search_v8 -- %d non-F_p-rational vertices, "
            "fresh per-vertex RNG, FIXED %.1fs budget each"
            % (len(non_fp_rational_set), PER_VERTEX_BUDGET_SECONDS))
        t_a = time.time()
        part_a_result = run_probe_delta_e_search_v8(
            g, BASE_SEED, PER_VERTEX_BUDGET_SECONDS)
        part_a_wall = time.time() - t_a
        new_delta_map = part_a_result["new_delta_map_raw"]
        log("  PART A done in %.2fs: n_resolved=%d/%d n_attempted=%d "
            "coverage_fraction=%s len(new_delta_map)=%d"
            % (part_a_wall, part_a_result["n_resolved"],
               part_a_result["n_non_fp_rational"], part_a_result["n_attempted"],
               part_a_result["coverage_fraction"], len(new_delta_map)))

        # ---- (3) REQUIRED COMPARISON against the archived delta_map -----
        log("Loading RUN-SSIQ-a85692-b's archived delta_map for p=%d via "
            "trapping_diagnostic_v5.load_archived_prime_data (IMPORTED "
            "UNCHANGED, READ ONLY)" % PRIME)
        archived = tdv5.load_archived_prime_data(args.raw_result_b, PRIME)
        archived_delta_map = archived["delta_map"]
        comparison = compare_against_archived(
            new_delta_map, archived_delta_map, non_fp_rational_set)
        log("  comparison: n_both_resolved=%d n_value_matches=%d "
            "n_value_differs=%d n_new_resolved_archived_was_not=%d "
            "n_archived_resolved_new_was_not=%d"
            % (comparison["n_both_resolved"], comparison["n_value_matches"],
               comparison["n_value_differs"],
               comparison["n_new_resolved_archived_was_not"],
               comparison["n_archived_resolved_new_was_not"]))

        # ---- PF-1/PF-9 strengthened gate ---------------------------------
        gate = check_coverage_gate(new_delta_map, g, field)
        log("GATE: len(new_delta_map)=%d len(graph[vertices])=%d "
            "archived_n_vertices=%d gate_pass=%s"
            % (gate["len_new_delta_map"], gate["len_graph_vertices"],
               gate["archived_n_vertices"], gate["gate_pass"]))

        if gate["gate_pass"]:
            log("PART B: probe_permutation_null_control_v8 -- reusing the "
                "SAME p=%d graph, N_TRIALS=%d, PERMUTATION_SEED=%d"
                % (PRIME, N_TRIALS, PERMUTATION_SEED))
            t_b = time.time()
            part_b_result = run_probe_permutation_null_control_v8(
                new_delta_map, g["vertices"], g["adjacency"])
            part_b_wall = time.time() - t_b
            log("  PART B done in %.2fs: real_depth0_fraction=%s margin=%s "
                "outcome=%s"
                % (part_b_wall,
                   part_b_result["real_depth0_fraction"]["fraction"],
                   part_b_result["margin_percentage_points"],
                   part_b_result["outcome"]))
        else:
            log("GATE FAILED -- PART B DOES NOT RUN. Writing COVERAGE-SHORTFALL.")
            part_b_result = coverage_shortfall_record(
                gate, part_a_result["coverage_fraction"])

    total_wall = time.time() - t0
    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # ---- probe_delta_e_comparison.json (PART A's full comparison output) --
    comparison_payload = {
        "prime": PRIME,
        "graph_seed": GRAPH_SEED,
        "base_seed": BASE_SEED,
        "per_vertex_budget_seconds": PER_VERTEX_BUDGET_SECONDS,
        "graph_identity_verification": graph_identity,
        "graph_identity_failed_halt": graph_identity_failed_halt,
        "seed_construction": seed_info,
    }
    if part_a_result is not None:
        comparison_payload.update({
            "per_vertex_records": part_a_result["per_vertex_records"],
            "n_resolved": part_a_result["n_resolved"],
            "n_attempted": part_a_result["n_attempted"],
            "n_non_fp_rational": part_a_result["n_non_fp_rational"],
            "n_fp_rational_wired_unconditionally":
                part_a_result["n_fp_rational_wired_unconditionally"],
            "coverage_fraction": part_a_result["coverage_fraction"],
            "new_delta_map": delta_map_json_safe(part_a_result["new_delta_map_raw"]),
            "comparison_against_archived": comparison,
            "coverage_gate": gate,
        })
    comp_path = os.path.join(run_dir, "probe_delta_e_comparison.json")
    with open(comp_path, "w") as fh:
        json.dump(comparison_payload, fh, indent=1, sort_keys=True, default=str)

    # ---- probe_permutation_null_control.json (PART B result OR
    # COVERAGE-SHORTFALL) -- ALWAYS written, never omitted -----------------
    if part_b_result is None:
        # graph_identity re-verification failed -- neither PART A nor PART B
        # ran at all. Still an honest, distinct record, never omitted.
        pnc_payload = {
            "part_b_did_not_run": True,
            "outcome": "COVERAGE-SHORTFALL",
            "prime": PRIME,
            "note": (
                "PART A itself did not run: " + graph_identity_failed_halt
                if graph_identity_failed_halt else
                "PART A did not run for an unspecified reason."
            ),
            "graph_identity_verification": graph_identity,
        }
    else:
        pnc_payload = part_b_result
    pnc_path = os.path.join(run_dir, "probe_permutation_null_control.json")
    with open(pnc_path, "w") as fh:
        json.dump(pnc_payload, fh, indent=1, sort_keys=True, default=str)

    # ---- raw-result.json (top-level summary) ------------------------------
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
        "permutation_seed": PERMUTATION_SEED,
        "per_vertex_budget_seconds": PER_VERTEX_BUDGET_SECONDS,
        "n_trials": N_TRIALS,
        "graph_identity_verification": graph_identity,
        "graph_identity_failed_halt": graph_identity_failed_halt,
        "part_a_summary": (
            None if part_a_result is None else {
                "n_resolved": part_a_result["n_resolved"],
                "n_attempted": part_a_result["n_attempted"],
                "n_non_fp_rational": part_a_result["n_non_fp_rational"],
                "n_fp_rational_wired_unconditionally":
                    part_a_result["n_fp_rational_wired_unconditionally"],
                "coverage_fraction": part_a_result["coverage_fraction"],
            }
        ),
        "comparison_against_archived_summary": (
            None if comparison is None else {
                k: v for k, v in comparison.items()
                if k != "value_differs_triples"
            }
        ),
        "coverage_gate": gate,
        "part_b_outcome": (
            None if part_b_result is None else part_b_result.get("outcome")
        ),
        "part_b_summary": (
            None if part_b_result is None else {
                k: v for k, v in part_b_result.items()
                if k not in ("null_depth0_fractions", "null_n_local_min",
                             "null_n_depth0")
            }
        ),
        "artifact_references": {
            "probe_delta_e_comparison": "probe_delta_e_comparison.json",
            "probe_permutation_null_control": "probe_permutation_null_control.json",
        },
        "objective_boundary": (
            "This is a DIAGNOSTIC CONTROL, not a claim. It does not test "
            "H-SSIQ-36e970's real-arm prediction, does not gate any "
            "decision rule, and does not itself constitute evidence for or "
            "against a computable delta_E-gradient or a p^{1/4} algorithm. "
            "Scale: toy, single prime p=2437 (N=203 vertices, "
            "max log2(p)=%.4f); no result transfers to cryptographic "
            "scale." % math.log2(PRIME)
        ),
        "scale_qualifier": "toy; N (graph size) = 203; single prime p=2437",
    }
    raw_result_path = os.path.join(run_dir, "raw-result.json")
    with open(raw_result_path, "w") as fh:
        json.dump(raw_result_payload, fh, indent=1, sort_keys=True, default=str)

    log("wrote %s, %s, %s (%.2fs total)"
        % (raw_result_path, comp_path, pnc_path, total_wall))
    if part_b_result is not None:
        print("OUTCOME %s" % part_b_result.get("outcome"))
    else:
        print("OUTCOME GRAPH-IDENTITY-VERIFICATION-FAILED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
