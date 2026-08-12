#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v9 (BATCH-012) -- delta_e_truncation_probe_v9.

Implements experiments/EXP-SSIQ-a85692/specification_v9.yaml inputs
truncation_probe_search_v9 EXACTLY as frozen (version 9, frozen_at
2026-08-06). PART A ONLY -- deliberately NO PART B (permutation-null
control) in this amendment. Single prime only: p=2437, the SAME rebuilt
graph (pinned graph-construction seed 20260805) every amendment since v5 has
used.

This is a TRUNCATION-MUTATION CONTROL on v8's own PART A design
(delta_e_independent_rng_probe_v8.py): reruns the identical per-vertex-
independent-RNG delta_E search at a per-vertex time budget deliberately cut
from v8's 15.0s down to PER_VERTEX_BUDGET_SECONDS=0.5, forcing genuine
truncation, per RT-BATCH-011's own recommended value. It reuses v8's exact
BASE_SEED=20260811 and derive_per_vertex_seed formula so that budget-
truncation is isolated as the sole manipulated variable versus v8.

REUSE / DUPLICATION SPLIT, DISCLOSED EXPLICITLY (matches
required_artifacts_note's own (i)/(ii) split):
  (i)  GENUINELY IMPORTED, UNCHANGED: compute_delta_e.two_sided_search,
       compute_delta_e.L_PRIMES, compute_delta_e.X_LIST_BOUND;
       trapping_diagnostic_v5.build_graph_for_prime,
       trapping_diagnostic_v5.load_archived_prime_data;
       delta_e_independent_rng_probe_v8.derive_per_vertex_seed,
       delta_e_independent_rng_probe_v8.verify_graph_identity (which itself
       imports build_isogeny_graph.degree_sequence_check -- not re-imported
       directly here).
  (ii) AUTHORIZED, DISCLOSED DUPLICATES (new code this file writes): the
       PART-A-only per-vertex search-loop orchestration
       (run_truncation_probe_v9), the F_p-rational unconditional-wiring
       construction step (identical to v8's own PF-9 fix, matching
       compute_delta_e_v2.py's own construction exactly); a small new
       parsing helper, parse_v8_new_delta_map(path), an "(ii) AUTHORIZED,
       DISCLOSED DUPLICATE" of load_archived_prime_data's own
       string-to-tuple round-trip convention, applied to a different source
       file/schema (RUN-SSIQ-a85692-h's probe_delta_e_comparison.json
       top-level new_delta_map field, PF-1's own fix); a small git_state()
       helper (infra bookkeeping only, the same trivial pattern every prior
       module in this lineage repeats).

Does NOT import or call delta_e_permutation_null_control_v7's
depth0_fraction/summary_stats (NO PART B), and does NOT import or call
delta_e_independent_rng_probe_v8's own run_probe_delta_e_search_v8 or
run_probe_permutation_null_control_v8 driver functions -- this file writes
its own PART-A-only driver, reusing only the two named helper functions
listed above.

WRITE-ORDER / FAILURE-ISOLATION DISCIPLINE (PF-5, per round-2 pre-freeze
review): PART A's own core measurement and Comparison 1's result are
captured into the run's in-memory result object BEFORE Comparison 2's own
parsing step is attempted. Comparison 2's own parsing/comparison code is
wrapped so that ANY exception it raises is caught and recorded as a
comparison_2_error field in the written output, rather than propagating
uncaught and discarding PART A's and Comparison 1's own already-computed,
more important results.

JSON SAFETY (PF-13's convention, inherited unchanged): every vertex-keyed
artifact output uses the IDENTICAL str(list(v))-keyed convention
compute_delta_e_v2.py's own delta_map_json_safe already established. A raw
tuple is never written directly as a JSON dict key; the (vertex,
archived_value, new_value) / (vertex, v8_value, new_value) triples nest the
vertex as a list value, never as a key.

OBJECTIVE_BOUNDARY: this is a purely DESCRIPTIVE diagnostic control, not a
test of H-SSIQ-36e970's real-arm prediction. It does NOT produce a
PERSISTS/WEAKENS label (that vocabulary belongs to v8's PART B, not run by
this amendment). It reports measurements only; interpretation of what the
measured relationship between truncation and value-differences means for
PF-6, H-SSIQ-36e970, or lever L4 belongs to the Coordinator and reviewers.
"""

import argparse
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
import trapping_diagnostic_v5 as tdv5  # noqa: E402  (FROZEN, UNCHANGED --
                                        # (i) genuine-import source for
                                        # build_graph_for_prime /
                                        # load_archived_prime_data)
import compute_delta_e  # noqa: E402  (FROZEN, UNCHANGED -- (i) genuine-
                         # import source for two_sided_search / L_PRIMES /
                         # X_LIST_BOUND)
import delta_e_independent_rng_probe_v8 as v8probe  # noqa: E402  (FROZEN,
                         # UNCHANGED -- (i) genuine-import source for
                         # derive_per_vertex_seed / verify_graph_identity.
                         # NEVER edited; its own driver functions
                         # (run_probe_delta_e_search_v8,
                         # run_probe_permutation_null_control_v8) are NOT
                         # called anywhere in this file.)

EXPERIMENT_ID = "EXP-SSIQ-a85692"
RUN_ID = "RUN-SSIQ-a85692-i"
SPEC_VERSION = 9

PRIME = 2437
ARCHIVED_N_VERTICES = 203
ARCHIVED_N_NON_FP_RATIONAL = 194
ARCHIVED_N_FP_RATIONAL = ARCHIVED_N_VERTICES - ARCHIVED_N_NON_FP_RATIONAL  # 9

GRAPH_SEED = 20260805      # SEEDS[0], the pinned graph-construction seed
                           # every amendment since v5 has used.
BASE_SEED = 20260811       # IDENTICAL constant v8 used (deliberate reuse,
                           # per amendment_scope: isolates budget-truncation
                           # as the sole manipulated variable versus v8).
PER_VERTEX_BUDGET_SECONDS = 0.5  # FIXED CONSTANT -- never a function of
                                  # elapsed or remaining time. ~2.3x-3.4x
                                  # smaller than the observed ~1.15-1.70s
                                  # completion range, per RT-BATCH-011's own
                                  # recommended value.

RUN_B_RAW_RESULT_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-b", "raw-result.json")
RUN_H_COMPARISON_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-h", "probe_delta_e_comparison.json")


class TruncationProbeError(RuntimeError):
    """Raised on a genuinely unanticipated halt condition this frozen
    contract does not itself specify a recovery path for (e.g. the
    graph-identity re-verification failing)."""


# ==========================================================================
# PART A: run_truncation_probe_v9. PART A ONLY -- no PART B driver.
# ==========================================================================

def run_truncation_probe_v9(graph, base_seed, per_vertex_budget_seconds):
    """spec_v9.yaml inputs.truncation_probe_search_v9. For every vertex v
    with field.is_in_fp(v) True (9 vertices at p=2437), wire
    new_delta_map[v] = 1 unconditionally BEFORE the search loop begins
    (identical required construction step to v8's own PF-9 fix). For every
    non-F_p-rational vertex (194 vertices), construct a FRESH
    random.Random via v8probe.derive_per_vertex_seed(base_seed, v)
    (GENUINELY IMPORTED, UNCHANGED) and call compute_delta_e.two_sided_search
    with a FIXED per_vertex_budget_seconds."""
    field = graph["field"]
    q = graph["q"]
    vertices = graph["vertices"]
    fp_rational = [v for v in vertices if field.is_in_fp(v)]
    non_fp_rational = [v for v in vertices if not field.is_in_fp(v)]

    # REQUIRED CONSTRUCTION STEP: new_delta_map[v] = 1 for EVERY
    # F_p-rational v, BEFORE the search loop begins.
    new_delta_map = {}
    for v in fp_rational:
        new_delta_map[v] = 1

    per_vertex_records = []
    n_resolved = 0
    n_timed_out = 0
    n_attempted = 0
    for v in non_fp_rational:
        n_attempted += 1
        seed_v = v8probe.derive_per_vertex_seed(base_seed, v)
        # FRESH instance, never shared or advanced across vertices.
        rng_v = random.Random(seed_v)
        target = field.frobenius(v)
        r = compute_delta_e.two_sided_search(
            field, v, target, rng_v, q,
            L=compute_delta_e.L_PRIMES, X=compute_delta_e.X_LIST_BOUND,
            time_budget_seconds=per_vertex_budget_seconds)
        resolved = bool(r["resolved"])
        timed_out = bool(r["timed_out"])
        if resolved:
            new_delta_map[v] = r["delta_e_upper_bound"]
            n_resolved += 1
        if timed_out:
            n_timed_out += 1
        per_vertex_records.append({
            "vertex": list(v),
            "seed_used": seed_v,
            "resolved": resolved,
            "delta_e_upper_bound": r["delta_e_upper_bound"],
            "wall_seconds": r["wall_seconds"],
            "timed_out": timed_out,
        })

    n_non_fp_rational = len(non_fp_rational)
    coverage_fraction = (
        (n_resolved / float(n_non_fp_rational)) if n_non_fp_rational else None)

    return {
        "new_delta_map_raw": new_delta_map,  # tuple-keyed, in-process only
        "per_vertex_records": per_vertex_records,
        "n_resolved": n_resolved,
        "n_timed_out": n_timed_out,
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
# REQUIRED COMPARISON 1, against RUN-SSIQ-a85692-b's archived delta_map.
# ==========================================================================

def compare_against_archived(new_delta_map, archived_delta_map,
                              non_fp_rational_set):
    """For every vertex resolved in THIS run (i.e. present in
    new_delta_map -- includes the 9 F_p-rational vertices, wired
    unconditionally, as well as any non-F_p-rational vertex the search
    resolved), compare delta_e_upper_bound against the archived value.
    Reports n_this_run_resolved, n_value_matches_vs_archived,
    n_value_differs_vs_archived (with the full list of (vertex,
    archived_value, new_value) triples), per spec_v9.yaml's REQUIRED
    COMPARISON 1 text. DISCLOSED INTERPRETATION (HONESTY RULE, same
    disclosed choice v8's own PD-3 made for the analogous ambiguity): the
    frozen spec text does not explicitly restrict this comparison's domain
    to the non-F_p-rational vertices, so it is computed here over the FULL
    new_delta_map key set (including the 9 F_p-rational vertices, which
    trivially match at value 1 in both maps by the unconditional identity
    wiring), WITH a non_fp_rational_only sub-breakdown also reported for
    transparency."""
    new_keys = set(new_delta_map.keys())
    value_matches = []
    value_differs = []
    nfp_this_run_resolved = 0
    nfp_value_matches = 0
    nfp_value_differs = 0
    n_not_in_archived = 0
    for v in new_keys:
        is_nfp = v in non_fp_rational_set
        if is_nfp:
            nfp_this_run_resolved += 1
        if v not in archived_delta_map:
            n_not_in_archived += 1
            continue
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
            "Computed over the full new_delta_map key set this run "
            "produced (9 unconditionally-wired F_p-rational vertices plus "
            "every non-F_p-rational vertex resolved within the 0.5s "
            "budget), which trivially match the archived value 1 for the "
            "F_p-rational vertices by the identical unconditional identity "
            "wiring both procedures share -- see non_fp_rational_only "
            "sub-breakdown below for the search-only figures. DISCLOSED "
            "INTERPRETATION per the HONESTY RULE: the frozen spec's own "
            "text does not explicitly restrict this domain to the "
            "non-F_p-rational vertices, mirroring the identical ambiguity "
            "v8's own PD-3 disclosed for the analogous comparison."
        ),
        "n_this_run_resolved": len(new_keys),
        "n_value_matches_vs_archived": len(value_matches),
        "n_value_differs_vs_archived": len(value_differs),
        "value_differs_vs_archived_triples": value_differs,
        "n_this_run_resolved_not_in_archived": n_not_in_archived,
        "non_fp_rational_only": {
            "n_this_run_resolved": nfp_this_run_resolved,
            "n_value_matches_vs_archived": nfp_value_matches,
            "n_value_differs_vs_archived": nfp_value_differs,
        },
    }


# ==========================================================================
# REQUIRED COMPARISON 2, against RUN-SSIQ-a85692-h's own new_delta_map.
# PF-1's fix: parse ONLY probe_delta_e_comparison.json's top-level
# new_delta_map field (string keys, e.g. "[1031, 1095]"), NOT raw-result.json
# which does not contain this field.
# ==========================================================================

def parse_v8_new_delta_map(path):
    """(ii) AUTHORIZED, DISCLOSED DUPLICATE of
    trapping_diagnostic_v5.load_archived_prime_data's own string-to-tuple
    parsing convention, applied to a DIFFERENT source file/schema:
    RUN-SSIQ-a85692-h's probe_delta_e_comparison.json top-level
    new_delta_map object (string keys like "[1031, 1095]" -> integer
    values, NOT nested under phase_minus1_real_search). Performs the SAME
    collision/injectivity check load_archived_prime_data itself performs:
    asserts the parsed-tuple keyset has the same cardinality as the raw
    string keyset; raises loudly if not."""
    with open(path) as fh:
        data = json.load(fh)
    raw_new_delta_map = data["new_delta_map"]
    parsed = {}
    for key_str, delta_val in raw_new_delta_map.items():
        vertex = tuple(json.loads(key_str))
        parsed[vertex] = delta_val
    if len(parsed) != len(raw_new_delta_map):
        raise TruncationProbeError(
            "parse_v8_new_delta_map: tuple(json.loads(key)) round-trip "
            "produced %d distinct vertex tuples from %d raw new_delta_map "
            "keys in %s -- a collision in the round-trip, which should be "
            "injective" % (len(parsed), len(raw_new_delta_map), path))
    return parsed


def compare_against_v8(new_delta_map, v8_delta_map, non_fp_rational_set):
    """For every vertex resolved in THIS run, compare its
    delta_e_upper_bound against v8's own PARSED value for the IDENTICAL
    vertex under the IDENTICAL per-vertex RNG seed but a 30x LARGER budget
    (15.0s vs. 0.5s). Same domain convention (and same disclosed
    interpretation) as compare_against_archived above."""
    new_keys = set(new_delta_map.keys())
    value_matches = []
    value_differs = []
    nfp_this_run_resolved = 0
    nfp_value_matches = 0
    nfp_value_differs = 0
    n_not_in_v8 = 0
    for v in new_keys:
        is_nfp = v in non_fp_rational_set
        if is_nfp:
            nfp_this_run_resolved += 1
        if v not in v8_delta_map:
            n_not_in_v8 += 1
            continue
        if v8_delta_map[v] == new_delta_map[v]:
            value_matches.append(v)
            if is_nfp:
                nfp_value_matches += 1
        else:
            value_differs.append({
                "vertex": list(v),
                "v8_value": v8_delta_map[v],
                "new_value": new_delta_map[v],
            })
            if is_nfp:
                nfp_value_differs += 1

    return {
        "domain_note": (
            "Computed over the full new_delta_map key set this run "
            "produced (same domain convention, and the same disclosed "
            "interpretation, as compare_against_archived above)."
        ),
        "n_this_run_resolved": len(new_keys),
        "n_value_matches_vs_v8": len(value_matches),
        "n_value_differs_vs_v8": len(value_differs),
        "value_differs_vs_v8_triples": value_differs,
        "n_this_run_resolved_not_in_v8": n_not_in_v8,
        "non_fp_rational_only": {
            "n_this_run_resolved": nfp_this_run_resolved,
            "n_value_matches_vs_v8": nfp_value_matches,
            "n_value_differs_vs_v8": nfp_value_differs,
        },
        "isolation_note": (
            "THIS COMPARISON ISOLATES A PURE TRUNCATION EFFECT, INDEPENDENT "
            "OF RNG CHOICE ENTIRELY: since the RNG stream is byte-for-byte "
            "identical between this run and v8 for every vertex (identical "
            "BASE_SEED and derive_per_vertex_seed formula), any value "
            "difference here is attributable solely to the smaller search "
            "budget (0.5s vs. 15.0s), not to any RNG-sharing or RNG-choice "
            "effect."
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

    log("[%s] %s / %s (specification_v9.yaml)" % (started, EXPERIMENT_ID, RUN_ID))
    log("delta_e_truncation_probe_v9: prime=%d GRAPH_SEED=%d BASE_SEED=%d "
        "PER_VERTEX_BUDGET_SECONDS=%.1f (PART A ONLY -- no PART B)"
        % (PRIME, GRAPH_SEED, BASE_SEED, PER_VERTEX_BUDGET_SECONDS))

    run_dir = args.run_dir
    os.makedirs(run_dir, exist_ok=True)

    # ---- (1) rebuild the graph (IMPORTED UNCHANGED) + re-run the two-part
    # graph-identity verification (v8probe.verify_graph_identity, IMPORTED
    # UNCHANGED), BEFORE any delta_E search begins.
    log("Rebuilding graph for p=%d via trapping_diagnostic_v5.build_graph_for_prime "
        "(IMPORTED UNCHANGED, seed=%d)" % (PRIME, GRAPH_SEED))
    g, seed_info = tdv5.build_graph_for_prime(PRIME, GRAPH_SEED)
    field = g["field"]

    log("Re-running two-part graph-identity verification via "
        "delta_e_independent_rng_probe_v8.verify_graph_identity (GENUINELY "
        "IMPORTED, UNCHANGED)")
    graph_identity = v8probe.verify_graph_identity(g, ARCHIVED_N_VERTICES)
    log("  graph_identity_verification pass=%s (n_built=%d, degseq_pass=%s)"
        % (graph_identity["pass"], graph_identity["n_built_vertices"],
           graph_identity["degree_sequence_check"]["pass"]))

    graph_identity_failed_halt = None
    if not graph_identity["pass"]:
        # GENUINELY UNANTICIPATED by the frozen contract text: the contract
        # requires this re-verification be re-run before any delta_E search
        # begins but does not state what to do on failure -- identical gap
        # v8's own PD-2 disclosed for the SAME check. Per the campaign's own
        # HONESTY RULE, this halts PART A on this genuinely unanticipated
        # condition (following v8's own precedent) rather than proceeding on
        # a graph that failed its own required identity check.
        graph_identity_failed_halt = (
            "Graph-identity re-verification FAILED. specification_v9.yaml's "
            "amendment_scope requires this check be re-run before any "
            "delta_E search begins but does not specify a recovery path on "
            "failure (the identical gap v8's own PD-2 disclosed for this "
            "same check); this Executor halts PART A on this genuinely "
            "unanticipated condition rather than proceeding on an "
            "unverified graph, per the governing HONESTY RULE."
        )
        log("HALTING: %s" % graph_identity_failed_halt)

    non_fp_rational_set = set(v for v in g["vertices"] if not field.is_in_fp(v))

    part_a_result = None
    comparison_1 = None

    if graph_identity_failed_halt is None:
        # ---- (2) PART A: independent per-vertex RNG search, FIXED 0.5s ---
        log("PART A: run_truncation_probe_v9 -- %d non-F_p-rational vertices, "
            "fresh per-vertex RNG (v8's own BASE_SEED=%d, derive_per_vertex_seed "
            "formula, GENUINELY IMPORTED UNCHANGED), FIXED %.1fs budget each"
            % (len(non_fp_rational_set), BASE_SEED, PER_VERTEX_BUDGET_SECONDS))
        t_a = time.time()
        part_a_result = run_truncation_probe_v9(
            g, BASE_SEED, PER_VERTEX_BUDGET_SECONDS)
        part_a_wall = time.time() - t_a
        new_delta_map = part_a_result["new_delta_map_raw"]
        log("  PART A done in %.2fs: n_resolved=%d/%d n_timed_out=%d "
            "n_attempted=%d coverage_fraction=%s len(new_delta_map)=%d"
            % (part_a_wall, part_a_result["n_resolved"],
               part_a_result["n_non_fp_rational"], part_a_result["n_timed_out"],
               part_a_result["n_attempted"], part_a_result["coverage_fraction"],
               len(new_delta_map)))

        # ---- (3) REQUIRED COMPARISON 1 against the archived delta_map ----
        # PF-5: captured into the in-memory result BEFORE Comparison 2's own
        # parsing step is attempted.
        log("Loading RUN-SSIQ-a85692-b's archived delta_map for p=%d via "
            "trapping_diagnostic_v5.load_archived_prime_data (IMPORTED "
            "UNCHANGED, READ ONLY)" % PRIME)
        archived = tdv5.load_archived_prime_data(args.raw_result_b, PRIME)
        archived_delta_map = archived["delta_map"]
        comparison_1 = compare_against_archived(
            new_delta_map, archived_delta_map, non_fp_rational_set)
        log("  comparison_1 (vs archived): n_this_run_resolved=%d "
            "n_value_matches_vs_archived=%d n_value_differs_vs_archived=%d"
            % (comparison_1["n_this_run_resolved"],
               comparison_1["n_value_matches_vs_archived"],
               comparison_1["n_value_differs_vs_archived"]))
    else:
        new_delta_map = {}

    # ---- (4) REQUIRED COMPARISON 2, against v8's own new_delta_map -------
    # PF-5 FIX: wrapped so ANY exception is caught and recorded as
    # comparison_2_error, never propagating uncaught and discarding PART A's
    # and Comparison 1's own already-computed, more important results.
    comparison_2 = None
    comparison_2_error = None
    if graph_identity_failed_halt is None:
        log("REQUIRED COMPARISON 2: parsing RUN-SSIQ-a85692-h's own "
            "new_delta_map via parse_v8_new_delta_map (NEW, disclosed "
            "duplicate parsing helper) from %s" % args.run_h_comparison)
        try:
            v8_delta_map = parse_v8_new_delta_map(args.run_h_comparison)
            comparison_2 = compare_against_v8(
                new_delta_map, v8_delta_map, non_fp_rational_set)
            log("  comparison_2 (vs v8): n_this_run_resolved=%d "
                "n_value_matches_vs_v8=%d n_value_differs_vs_v8=%d"
                % (comparison_2["n_this_run_resolved"],
                   comparison_2["n_value_matches_vs_v8"],
                   comparison_2["n_value_differs_vs_v8"]))
        except Exception as e:  # noqa: BLE001 -- PF-5 requires catching ANY
                                 # exception here, not only a specific one.
            comparison_2_error = "%s: %s" % (type(e).__name__, str(e))
            log("COMPARISON 2 FAILED (caught per PF-5, PART A/Comparison 1 "
                "results preserved): %s" % comparison_2_error)

    total_wall = time.time() - t0
    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if total_wall > 600:
        log("WARNING: total_wall_seconds (%.2f) exceeded the 600s budget "
            "cap -- this should not happen under the 97.0s worst-case "
            "bound, disclosed here per the HONESTY RULE" % total_wall)

    # ---- truncation_probe_comparison.json (PART A + both comparisons) ----
    comparison_payload = {
        "prime": PRIME,
        "graph_seed": GRAPH_SEED,
        "base_seed": BASE_SEED,
        "per_vertex_budget_seconds": PER_VERTEX_BUDGET_SECONDS,
        "graph_identity_verification": graph_identity,
        "graph_identity_failed_halt": graph_identity_failed_halt,
        "seed_construction": seed_info,
        "comparison_2_error": comparison_2_error,
    }
    if part_a_result is not None:
        comparison_payload.update({
            "per_vertex_records": part_a_result["per_vertex_records"],
            "n_resolved": part_a_result["n_resolved"],
            "n_timed_out": part_a_result["n_timed_out"],
            "n_attempted": part_a_result["n_attempted"],
            "n_non_fp_rational": part_a_result["n_non_fp_rational"],
            "n_fp_rational_wired_unconditionally":
                part_a_result["n_fp_rational_wired_unconditionally"],
            "coverage_fraction": part_a_result["coverage_fraction"],
            "new_delta_map": delta_map_json_safe(part_a_result["new_delta_map_raw"]),
        })
    if comparison_1 is not None:
        comparison_payload["comparison_against_archived"] = comparison_1
    if comparison_2 is not None:
        comparison_payload["comparison_against_v8"] = comparison_2
    comp_path = os.path.join(run_dir, "truncation_probe_comparison.json")
    with open(comp_path, "w") as fh:
        json.dump(comparison_payload, fh, indent=1, sort_keys=True, default=str)

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
        "per_vertex_budget_seconds": PER_VERTEX_BUDGET_SECONDS,
        "graph_identity_verification": graph_identity,
        "graph_identity_failed_halt": graph_identity_failed_halt,
        "part_a_summary": (
            None if part_a_result is None else {
                "n_resolved": part_a_result["n_resolved"],
                "n_timed_out": part_a_result["n_timed_out"],
                "n_attempted": part_a_result["n_attempted"],
                "n_non_fp_rational": part_a_result["n_non_fp_rational"],
                "n_fp_rational_wired_unconditionally":
                    part_a_result["n_fp_rational_wired_unconditionally"],
                "coverage_fraction": part_a_result["coverage_fraction"],
            }
        ),
        "comparison_1_against_archived_summary": (
            None if comparison_1 is None else {
                k: v for k, v in comparison_1.items()
                if k != "value_differs_vs_archived_triples"
            }
        ),
        "comparison_2_against_v8_summary": (
            None if comparison_2 is None else {
                k: v for k, v in comparison_2.items()
                if k != "value_differs_vs_v8_triples"
            }
        ),
        "comparison_2_error": comparison_2_error,
        "artifact_references": {
            "truncation_probe_comparison": "truncation_probe_comparison.json",
        },
        "objective_boundary": (
            "This is a DESCRIPTIVE DIAGNOSTIC CONTROL, not a claim. It does "
            "not test H-SSIQ-36e970's real-arm prediction, does not gate "
            "any decision rule, and does not itself constitute evidence for "
            "or against a computable delta_E-gradient or a p^{1/4} "
            "algorithm. It does not produce a PERSISTS/WEAKENS label (that "
            "vocabulary belongs to v8's PART B, not run by this amendment). "
            "Scale: toy, single prime p=2437 (N=203 vertices, "
            "max log2(p)=%.4f); no result transfers to cryptographic "
            "scale." % math.log2(PRIME)
        ),
        "scale_qualifier": "toy; N (graph size) = 203; single prime p=2437",
    }
    raw_result_path = os.path.join(run_dir, "raw-result.json")
    with open(raw_result_path, "w") as fh:
        json.dump(raw_result_payload, fh, indent=1, sort_keys=True, default=str)

    log("wrote %s, %s (%.2fs total)" % (raw_result_path, comp_path, total_wall))
    if part_a_result is not None:
        print("OUTCOME PART-A-COMPLETE n_resolved=%d/%d n_timed_out=%d "
              "comparison_2_error=%s"
              % (part_a_result["n_resolved"], part_a_result["n_non_fp_rational"],
                 part_a_result["n_timed_out"], bool(comparison_2_error)))
    else:
        print("OUTCOME GRAPH-IDENTITY-VERIFICATION-FAILED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
