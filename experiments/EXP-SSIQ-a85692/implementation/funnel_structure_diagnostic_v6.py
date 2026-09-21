#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v6 (BATCH-009) -- PART A's REQUIRED CORRECTED CROSS-CHECK
(gd12_fix_v6) and PART B's funnel_structure_diagnostic_v6.

Implements experiments/EXP-SSIQ-a85692/specification_v6.yaml
inputs.gd12_fix_v6 (corrected-cross-check portion) and
inputs.funnel_structure_diagnostic_v6 EXACTLY as frozen.

REUSE / DUPLICATION SPLIT, DISCLOSED EXPLICITLY, PF-2 FIX APPLIED (matching
required_artifacts_note's own (i)/(ii) split):
  (i)  GENUINELY IMPORTED, UNCHANGED: build_graph_for_prime and
       load_archived_prime_data from trapping_diagnostic_v5.py (both
       confirmed standalone, module-level functions by direct read of that
       file); degree_sequence_check from build_isogeny_graph.py; and this
       amendment's own greedy_descent_hitting_time_v2 from
       descent_walk_hardened.py.
  (ii) AUTHORIZED, DISCLOSED DUPLICATES of trapping_diagnostic_v5.py's own
       inline logic (confirmed NOT separately importable from that file --
       is_structural_local_min is six inline lines inside
       run_diagnostic_for_prime, which never exposes a per-vertex flag or a
       standalone callable): is_structural_local_min(v, delta_map,
       adjacency), the coverage assertion, and the graph-rebuild
       verification. These match trapping_diagnostic_v5.py's own formula
       and procedure exactly, including PF-10's restated missing-neighbour
       loud-raise guard.

Neither trapping_diagnostic_v5.py, descent_hitting_time.py, nor
build_isogeny_graph.py is modified, forked, or edited by this file -- all
three stay exactly as frozen.

FAILURE-HANDLING MODEL, PF-3/PF-7/PF-13 UNIFIED: every halt condition below
(the coverage assertion, the graph-rebuild verification, PART A's
n_trapped_true + n_trapped_false accounting assertion, PART B's
sum(basin) + n_trapped_false accounting assertion) is a PER-PRIME halt,
caught by the orchestration in run_batch009.py -- NEVER a process-aborting,
run-global halt. The trapped=True-vs-is_structural_local_min(terminal_vertex)
comparison itself NEVER halts anything: it is recorded as a per-prime
boolean field, crosscheck_pass, with the full disagreement list (never
merely a count), per the corrected FAILURE-HANDLING MODEL text.
"""

import math
import os
import sys

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
import build_isogeny_graph as big  # noqa: E402  (FROZEN, UNCHANGED)
import trapping_diagnostic_v5 as tdv5  # noqa: E402  (FROZEN, UNCHANGED --
                                        # (i) genuine-import source)
import descent_walk_hardened as dwh  # noqa: E402  (THIS amendment's own new
                                       # module, PART A)

PRIMES_V6 = [2437, 3889, 5737, 7333]
ARCHIVED_N_VERTICES = {2437: 203, 3889: 324, 5737: 478, 7333: 611}
SEED = 20260805  # SEEDS[0] -- same pinned convention as every prior batch
RUN_B_RAW_RESULT_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-b", "raw-result.json")

# Values THIS AMENDMENT'S OWN TEXT (inputs.funnel_structure_diagnostic_v6,
# ILLUSTRATIVE VALUES, PF-8 FIX APPLIED) states the run is EXPECTED to
# reproduce, computed directly from RUN-SSIQ-a85692-b's already-archived
# descent_metrics.per_prime[p].greedy_trapped_fraction. Used ONLY for the
# comparison recorded in this run's own output -- never substituted for a
# measured value, and never used to alter the computation itself.
EXPECTED_PART_B = {
    2437: {"n_vertices": 203, "n_trapped_false": 33, "sum_basin": 170},
    3889: {"n_vertices": 324, "n_trapped_false": 90, "sum_basin": 234},
    5737: {"n_vertices": 478, "n_trapped_false": 86, "sum_basin": 392},
    7333: {"n_vertices": 611, "n_trapped_false": 91, "sum_basin": 520},
}


class FunnelDiagnosticError(RuntimeError):
    """Raised on a per-prime halt condition (coverage assertion,
    graph-rebuild verification, PART A accounting assertion, or PART B
    accounting assertion). ALWAYS caught PER PRIME by the orchestration in
    run_batch009.py -- never propagates past that prime's own computation,
    per PF-3/PF-7/PF-13's unified per-prime failure-handling model."""


# ==========================================================================
# (ii) AUTHORIZED, DISCLOSED DUPLICATES of trapping_diagnostic_v5.py's own
#      inline logic (not separately importable from that file).
# ==========================================================================

def is_structural_local_min(v, delta_map, adjacency):
    """AUTHORIZED, DISCLOSED DUPLICATE of trapping_diagnostic_v5.py's own
    inline formula (run_diagnostic_for_prime, ~line 234):
    delta_map[v] <= min(delta_map[u] for u in adjacency[v]).
    PF-10 FIX APPLIED: restates the source's own missing-neighbour
    loud-raise guard (trapping_diagnostic_v5.py lines 224-232) -- raise
    loudly if any neighbour has no delta_map entry, structurally
    unreachable given the required coverage assertion below but stated for
    completeness rather than silently dropped."""
    nbr_deltas = []
    for u in adjacency[v]:
        if u not in delta_map:
            raise FunnelDiagnosticError(
                "PF-10 missing-neighbour guard (duplicated from "
                "trapping_diagnostic_v5.py): vertex %r has neighbour %r "
                "with no delta_map entry -- structurally unreachable given "
                "the required coverage assertion; signals a stale read or "
                "wrong prime, never a legitimate data gap" % (v, u))
        nbr_deltas.append(delta_map[u])
    return bool(delta_map[v] <= min(nbr_deltas))


def rebuild_and_verify(p, raw_result_path, seed):
    """(i) build_graph_for_prime / load_archived_prime_data GENUINELY
    IMPORTED, UNCHANGED, from trapping_diagnostic_v5.py.
    (ii) the coverage assertion and graph-rebuild verification below are
    AUTHORIZED, DISCLOSED DUPLICATES of that file's own inline procedure
    (confirmed NOT separately importable -- both are inline in
    run_diagnostic_for_prime)."""
    archived = tdv5.load_archived_prime_data(raw_result_path, p)
    delta_map = archived["delta_map"]
    archived_n_vertices = archived["archived_n_vertices"]
    archived_n_resolved = archived["archived_n_resolved"]

    if p in ARCHIVED_N_VERTICES and archived_n_vertices != ARCHIVED_N_VERTICES[p]:
        raise FunnelDiagnosticError(
            "archived n_vertices read from raw-result.json (%d) disagrees "
            "with this amendment's own pinned value (%d) for p=%d -- halt "
            "before computing anything further for this prime"
            % (archived_n_vertices, ARCHIVED_N_VERTICES[p], p))

    g, seed_info = tdv5.build_graph_for_prime(p, seed)  # (i) genuine import
    vertices = g["vertices"]
    adjacency = g["adjacency"]
    n_built = len(vertices)

    degseq = big.degree_sequence_check(g)
    vertex_count_match = bool(n_built == archived_n_vertices)
    degseq_pass = bool(degseq["pass"])

    vertex_set = set(vertices)
    matched_vertices = [v for v in delta_map if v in vertex_set]
    n_matched = len(matched_vertices)
    coverage_assertion_pass = bool(n_matched == archived_n_vertices)

    if not coverage_assertion_pass:
        raise FunnelDiagnosticError(
            "REQUIRED COVERAGE ASSERTION FAILED for p=%d: %d of %d "
            "delta_map keys matched the rebuilt graph's vertex set "
            "(compared against archived n_vertices=%d, NEVER n_resolved=%d) "
            "-- halting ONLY this prime's computation"
            % (p, n_matched, len(delta_map), archived_n_vertices,
               archived_n_resolved))
    if not (degseq_pass and vertex_count_match):
        raise FunnelDiagnosticError(
            "GRAPH-REBUILD VERIFICATION FAILED for p=%d: "
            "degree_sequence_check.pass=%s, rebuilt vertex count %d == "
            "archived n_vertices %d? %s"
            % (p, degseq_pass, n_built, archived_n_vertices, vertex_count_match))

    return {
        "delta_map": delta_map,
        "archived_n_vertices": archived_n_vertices,
        "archived_n_resolved": archived_n_resolved,
        "archived_greedy_trapped_fraction": archived["archived_greedy_trapped_fraction"],
        "graph": g,
        "vertices": vertices,
        "adjacency": adjacency,
        "seed_info": seed_info,
        "degree_sequence_check": degseq,
        "vertex_count_match": vertex_count_match,
        "coverage_assertion_pass": coverage_assertion_pass,
        "n_matched": n_matched,
        "graph_rebuild_independently_verified_correct": bool(
            degseq_pass and vertex_count_match and coverage_assertion_pass),
    }


# ==========================================================================
# PART A (gd12_fix_v6): REQUIRED CORRECTED CROSS-CHECK, per prime.
# ==========================================================================

def run_part_a_for_prime(p, raw_result_path, seed):
    """Runs greedy_descent_hitting_time_v2 from EVERY vertex, partitions
    trapped=True/False, checks the REQUIRED ACCOUNTING ASSERTION
    (n_trapped_true + n_trapped_false == n_vertices, PF-13-unified per-prime
    halt on mismatch), then computes the CORRECTED cross-check: for every
    trapped=True walk, is_structural_local_min(terminal_vertex) must be
    True (never compared against is_structural_local_min(START), which was
    v5's own defect). crosscheck_pass is a per-prime boolean; a disagreement
    NEVER halts anything -- it is recorded in the full disagreement list."""
    rb = rebuild_and_verify(p, raw_result_path, seed)
    delta_map = rb["delta_map"]
    adjacency = rb["adjacency"]
    vertices = rb["vertices"]
    diameter_sentinel = big.bfs_diameter(rb["graph"])

    walks = {}
    n_trapped_true = 0
    n_trapped_false = 0
    for v in vertices:
        res = dwh.greedy_descent_hitting_time_v2(adjacency, v, delta_map,
                                                   diameter_sentinel)
        walks[v] = res
        if res["trapped"]:
            n_trapped_true += 1
        else:
            n_trapped_false += 1

    n_vertices = len(vertices)
    accounting_pass = bool(n_trapped_true + n_trapped_false == n_vertices)
    if not accounting_pass:
        raise FunnelDiagnosticError(
            "PART A REQUIRED ACCOUNTING ASSERTION FAILED for p=%d: "
            "n_trapped_true(%d) + n_trapped_false(%d) != n_vertices(%d) -- "
            "halting ONLY this prime's PART A computation"
            % (p, n_trapped_true, n_trapped_false, n_vertices))

    disagreements = []
    for v, res in walks.items():
        if not res["trapped"]:
            continue
        terminal = res["terminal_vertex"]
        structural = is_structural_local_min(terminal, delta_map, adjacency)
        if not structural:
            disagreements.append({
                "start": list(v), "terminal_vertex": list(terminal),
                "trapped": True,
                "is_structural_local_min_terminal": structural,
                "delta_terminal": delta_map.get(terminal),
            })
    crosscheck_pass = bool(len(disagreements) == 0)

    return {
        "prime": p,
        "n_vertices": n_vertices,
        "n_trapped_true": n_trapped_true,
        "n_trapped_false": n_trapped_false,
        "accounting_assertion_pass": accounting_pass,
        "crosscheck_pass": crosscheck_pass,
        "n_disagreements": len(disagreements),
        "disagreements": disagreements,
        "corrected_equivalence_basis": (
            "for trapped=True walks, is_structural_local_min(terminal_vertex) "
            "is claimed TRUE unconditionally, by the non-backtracking-"
            "exclusion argument (a strict-descent walk's predecessor always "
            "has strictly greater delta than the current vertex, so it can "
            "never be a smaller-delta candidate) -- NOT claimed for "
            "trapped=False walks, excluded from this comparison entirely."
        ),
        "graph_rebuild_verification": {
            "degree_sequence_check": rb["degree_sequence_check"],
            "vertex_count_match": rb["vertex_count_match"],
            "coverage_assertion_pass": rb["coverage_assertion_pass"],
            "independently_verified_correct":
                rb["graph_rebuild_independently_verified_correct"],
        },
        "seed_construction": rb["seed_info"],
        "_internal_rebuild": rb,
        "_internal_walks": walks,
        "_internal_diameter_sentinel": diameter_sentinel,
    }


# ==========================================================================
# Self-contained Pearson correlation (no stats library, per REQUIRED
# CORRELATION's own explicit instruction).
# ==========================================================================

def pearson_corr(xs, ys):
    n = len(xs)
    if n != len(ys):
        raise ValueError("pearson_corr: length mismatch")
    if n < 2:
        return {"value": None, "n": n, "note": "fewer than 2 points -- undefined"}
    xbar = sum(xs) / float(n)
    ybar = sum(ys) / float(n)
    sxx = sum((x - xbar) ** 2 for x in xs)
    syy = sum((y - ybar) ** 2 for y in ys)
    sxy = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    if sxx == 0.0 or syy == 0.0:
        return {"value": None, "n": n,
                "note": "zero variance in x or y -- correlation undefined"}
    r = sxy / math.sqrt(sxx * syy)
    return {"value": r, "n": n, "note": None}


# ==========================================================================
# PART B (funnel_structure_diagnostic_v6), DEPENDENT ON PART A.
# ==========================================================================

def run_part_b_for_prime(part_a_result):
    """REQUIRED PRECONDITION (PF-3 FIX APPLIED): caller must not invoke this
    for a prime whose PART A crosscheck_pass is False -- enforced by
    run_batch009.py's orchestration, not re-checked here defensively (the
    precondition is the caller's own gating responsibility, stated
    explicitly in the frozen spec)."""
    p = part_a_result["prime"]
    rb = part_a_result["_internal_rebuild"]
    delta_map = rb["delta_map"]
    adjacency = rb["adjacency"]
    vertices = rb["vertices"]
    walks = part_a_result["_internal_walks"]
    n_vertices = part_a_result["n_vertices"]
    n_trapped_false = part_a_result["n_trapped_false"]

    # ---- 1. basin assignment -------------------------------------------
    basin = {}  # terminal_vertex -> list of start vertices
    for v in vertices:
        res = walks[v]
        if not res["trapped"]:
            continue
        m = res["terminal_vertex"]
        basin.setdefault(m, []).append(v)

    # basin-eligible local minima = {m : is_structural_local_min(m) AND
    #   delta_map[m] > 1}. By the corrected_equivalence_proof, EVERY
    # trapped=True walk's terminal_vertex satisfies both conditions
    # unconditionally; excluded_but_trapped (below) records any terminal
    # vertex found NOT to satisfy them, as a disclosed, not silently
    # dropped, invariant check -- it is expected to be empty.
    basin_eligible = {}
    excluded_but_trapped = []
    for m, starts in basin.items():
        eligible = (delta_map[m] > 1
                    and is_structural_local_min(m, delta_map, adjacency))
        if eligible:
            basin_eligible[m] = starts
        else:
            excluded_but_trapped.append({
                "terminal_vertex": list(m), "delta_m": delta_map.get(m),
                "n_starts": len(starts),
            })

    sum_basin = sum(len(v) for v in basin_eligible.values())

    # ---- 2. REQUIRED ACCOUNTING ASSERTION (PF-1/PF-13 FIX APPLIED) ------
    accounting_pass = bool(sum_basin + n_trapped_false == n_vertices)
    if not accounting_pass:
        raise FunnelDiagnosticError(
            "PART B REQUIRED ACCOUNTING ASSERTION FAILED for p=%d: "
            "sum(basin)=%d + n_trapped_false=%d != n_vertices=%d "
            "(excluded_but_trapped=%d terminal vertices found NOT "
            "basin-eligible despite a trapped=True walk terminating there) "
            "-- halting ONLY this prime's PART B computation"
            % (p, sum_basin, n_trapped_false, n_vertices,
               len(excluded_but_trapped)))

    basin_sizes = {m: len(starts) for m, starts in basin_eligible.items()}
    n_basin_eligible = len(basin_eligible)

    # ---- 3. basin_size_distribution -------------------------------------
    sizes_sorted = sorted(basin_sizes.values())
    maxv = max(sizes_sorted) if sizes_sorted else None
    meanv = (sum(sizes_sorted) / float(len(sizes_sorted))
              if sizes_sorted else None)
    if sizes_sorted:
        ns = len(sizes_sorted)
        medianv = (sizes_sorted[ns // 2] if ns % 2 == 1
                    else 0.5 * (sizes_sorted[ns // 2 - 1] + sizes_sorted[ns // 2]))
    else:
        medianv = None

    if n_basin_eligible == 0:
        # PF-11 FIX APPLIED: null-with-a-note, never a division by zero.
        top_k = 0
        top_k_minima = []
        top_decile_concentration = None
        top_decile_note = ("n_basin_eligible == 0 -- top_decile_concentration "
                            "reported as null, per PF-11 (not reached by any "
                            "of this amendment's four primes)")
    else:
        top_k = max(1, math.ceil(0.1 * n_basin_eligible))
        # ties broken by (delta value ascending, vertex tuple ascending)
        ranked = sorted(basin_eligible.keys(),
                         key=lambda m: (-basin_sizes[m], delta_map[m], m))
        top_k_minima = ranked[:top_k]
        captured = sum(basin_sizes[m] for m in top_k_minima)
        n_trapped_true_total = sum(basin_sizes.values())
        top_decile_concentration = (
            captured / float(n_trapped_true_total)
            if n_trapped_true_total > 0 else None)
        top_decile_note = None

    # ---- 4. depth(m) ------------------------------------------------------
    depths = {}
    for m in basin_eligible:
        nbr_deltas = [delta_map[u] for u in adjacency[m]]
        depths[m] = min(nbr_deltas) - delta_map[m]

    # ---- 5. REQUIRED CORRELATION ------------------------------------------
    depth_list, size_list, log_size_list = [], [], []
    for m in basin_eligible:
        depth_list.append(depths[m])
        size_list.append(basin_sizes[m])
        log_size_list.append(math.log(basin_sizes[m]))
    corr_depth_size = pearson_corr(depth_list, size_list)
    corr_depth_log_size = pearson_corr(depth_list, log_size_list)

    expected = EXPECTED_PART_B.get(p)
    comparison_to_frozen_illustrative_values = None
    if expected is not None:
        comparison_to_frozen_illustrative_values = {
            "expected_n_vertices": expected["n_vertices"],
            "measured_n_vertices": n_vertices,
            "n_vertices_match": bool(expected["n_vertices"] == n_vertices),
            "expected_n_trapped_false": expected["n_trapped_false"],
            "measured_n_trapped_false": n_trapped_false,
            "n_trapped_false_match": bool(
                expected["n_trapped_false"] == n_trapped_false),
            "expected_sum_basin": expected["sum_basin"],
            "measured_sum_basin": sum_basin,
            "sum_basin_match": bool(expected["sum_basin"] == sum_basin),
        }

    return {
        "prime": p,
        "n_vertices": n_vertices,
        "n_trapped_false": n_trapped_false,
        "n_basin_eligible": n_basin_eligible,
        "sum_basin": sum_basin,
        "accounting_assertion_pass": accounting_pass,
        "excluded_but_trapped": excluded_but_trapped,
        "basin_size_distribution": {
            "sorted_sizes": sizes_sorted,
            "max": maxv, "mean": meanv, "median": medianv,
        },
        "top_decile_concentration": {
            "k": top_k,
            "n_basin_eligible": n_basin_eligible,
            "concentration_fraction_of_trapped_true_walks": top_decile_concentration,
            "note": top_decile_note,
            "top_k_minima": [list(m) for m in top_k_minima],
            "top_k_minima_basin_sizes": [basin_sizes[m] for m in top_k_minima],
        },
        "depth_by_local_min": {
            str(list(m)): depths[m] for m in basin_eligible
        },
        "basin_size_by_local_min": {
            str(list(m)): basin_sizes[m] for m in basin_eligible
        },
        "correlation_depth_vs_basin_size": corr_depth_size,
        "correlation_depth_vs_log_basin_size": corr_depth_log_size,
        "comparison_to_frozen_illustrative_values": comparison_to_frozen_illustrative_values,
        "objective_boundary": (
            "This is a DIAGNOSTIC, not a claim. It does not test "
            "H-SSIQ-36e970's real-arm prediction, does not gate any "
            "decision rule, and does not itself constitute evidence for or "
            "against a computable delta_E-gradient. A strong depth/basin-"
            "size correlation would be a candidate MECHANISM QUESTION for a "
            "future amendment, never itself evidence for or against L4's "
            "revisit condition."
        ),
    }


def run_all(raw_result_path=RUN_B_RAW_RESULT_RELPATH, seed=SEED,
            primes=PRIMES_V6):
    """Orchestrates PART A then, gated on crosscheck_pass, PART B, for every
    prime -- each prime's failures isolated per PF-3/PF-7/PF-13's unified
    per-prime model. Returns (part_a_per_prime, part_b_per_prime,
    per_prime_errors)."""
    part_a = {}
    part_b = {}
    errors = {}
    for p in primes:
        try:
            a_result = run_part_a_for_prime(p, raw_result_path, seed)
        except FunnelDiagnosticError as e:
            errors.setdefault(p, {})["part_a"] = str(e)
            continue
        part_a[p] = a_result
        if not a_result["crosscheck_pass"]:
            part_b[p] = {
                "prime": p, "skipped": True,
                "reason": (
                    "PART A crosscheck_pass is False for this prime -- per "
                    "the REQUIRED PRECONDITION, PART B MUST NOT run: the "
                    "walk-to-local-minimum correspondence is not "
                    "independently confirmed for this prime's data."
                ),
            }
            continue
        try:
            b_result = run_part_b_for_prime(a_result)
        except FunnelDiagnosticError as e:
            errors.setdefault(p, {})["part_b"] = str(e)
            part_b[p] = {"prime": p, "skipped": True,
                          "reason": "PART B accounting assertion failed: %s" % e}
            continue
        part_b[p] = b_result
    return part_a, part_b, errors
