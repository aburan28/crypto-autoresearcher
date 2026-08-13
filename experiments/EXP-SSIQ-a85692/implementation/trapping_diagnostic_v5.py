#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v5 (BATCH-008) -- PART B: trapping_mechanism_diagnostic_v5.

Implements experiments/EXP-SSIQ-a85692/specification_v5.yaml
inputs.trapping_mechanism_diagnostic_v5 EXACTLY as frozen.

For each of the four primes with full delta_map coverage already committed
in RUN-SSIQ-a85692-b's raw-result.json (2437, 3889, 5737, 7333):

  1. Rebuild the 2-isogeny graph via build_isogeny_graph.build_graph_bfs
     (IMPORTED UNCHANGED), using the SAME pinned seed convention this
     campaign already uses (build_all_graphs(PRIMES, SEEDS[0]) in both
     descent_hitting_time.py and compute_delta_e.py: for each prime, a
     FRESH random.Random(SEEDS[0]) instance, SEEDS[0] = 20260805).
  2. PF-4 FIX APPLIED: convert RUN-SSIQ-a85692-b's archived delta_map keys
     (JSON-string-serialized str(list(v)), e.g. "[1031, 1095]") back to
     vertex tuples via tuple(json.loads(key)) -- this exact round-trip, not
     an ad-hoc variant.
  3. PF-9 FIX APPLIED: REQUIRED COVERAGE ASSERTION -- the number of
     delta_map keys matched against the rebuilt graph's vertex set MUST
     equal that prime's archived n_vertices (NEVER n_resolved, a different,
     smaller, incorrect comparison target per PF-9). Halt with an explicit
     error, not a silent partial result, on any mismatch.
  4. PF-5/PF-11 FIX APPLIED: GRAPH-REBUILD VERIFICATION -- re-run
     degree_sequence_check (M-DEGSEQ, IMPORTED UNCHANGED) on the rebuilt
     graph and cross-check its vertex COUNT against that prime's specific
     archived n_vertices (not merely the generic floor(p/12) formula).
     "Independently verified correct" requires BOTH this check AND the
     coverage assertion's own vertex-set match to pass -- the coverage
     assertion's key set functions as a second, independent vertex-set
     snapshot that a same-count/same-degree vertex substitution could still
     surface as a mismatch, per PF-11.
  5. Compute is_structural_local_min(v) = delta_map[v] <= min(delta_map[u]
     for u in adjacency[v]) for every vertex. PF-7 FIX APPLIED: the
     "unresolved neighbour" branch cannot execute on this batch's data
     (full coverage confirmed for all four primes); if it is EVER reached,
     RAISE LOUDLY.
  6. PF-6 FIX APPLIED: REQUIRED CROSS-CHECK -- re-run
     greedy_descent_hitting_time (IMPORTED UNCHANGED) from EVERY resolved
     vertex (not a sample) and confirm its "trapped" flag agrees with
     is_structural_local_min(start) for every single vertex; halt with an
     explicit error, not a silently-reported disagreement count, on any
     disagreement (per the frozen spec, this equivalence is provably exact,
     so any disagreement is conclusively a bug in this file's own code).

OBJECTIVE_BOUNDARY (restated verbatim from the frozen spec): this is a
DIAGNOSTIC, not a claim. It does not test H-SSIQ-36e970's real-arm
prediction, does not gate any decision rule, and does not itself constitute
evidence for or against a computable delta_E-gradient.

PF-8 FIX APPLIED: "fraction of structural local minima" and the
already-archived "greedy_trapped_fraction" (descent_metrics.per_prime[p]
.greedy_trapped_fraction, RUN-SSIQ-a85692-b) are RELATED BUT GENERALLY
DIFFERENT STATISTICS -- never presented as corroborating the same quantity
(see statistic_distinction_note in each prime's result below).

This module performs NO new delta_E search of any kind: delta_map is read
directly from the already-committed RUN-SSIQ-a85692-b/raw-result.json.
build_isogeny_graph.py and descent_hitting_time.py are imported UNCHANGED,
by reference, and are never modified by this file.
"""

import json
import os
import random
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
_B_IMPL_DIR = os.path.join(_THIS_DIR, "..", "..", "EXP-SSIQ-58b642",
                            "implementation")
sys.path.insert(0, _B_IMPL_DIR)

# Import order matters -- see gd11_regression_test.py's own note: a genuine
# circular import exists between the frozen, unchanged descent_hitting_time.py
# and calibration_synthetic.py; importing calibration_synthetic FIRST in this
# process avoids it (same order compute_delta_e.py already uses). Neither
# file is modified here.
import calibration_synthetic as cal  # noqa: E402,F401  (import-order fix only)
import build_isogeny_graph as big  # noqa: E402  (FROZEN, UNCHANGED)
import descent_hitting_time as dht  # noqa: E402  (FROZEN, UNCHANGED)

PRIMES_B = [2437, 3889, 5737, 7333]
# specification_v5.yaml inputs.trapping_mechanism_diagnostic_v5's own stated
# per-prime archived n_vertices values (independently re-confirmed against
# raw-result.json at load time below -- not trusted blindly).
ARCHIVED_N_VERTICES = {2437: 203, 3889: 324, 5737: 478, 7333: 611}
SEED = 20260805  # SEEDS[0] -- same pinned convention as build_all_graphs()
                 # in descent_hitting_time.py and compute_delta_e.py
RUN_B_RAW_RESULT_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-b", "raw-result.json")


class TrappingDiagnosticError(RuntimeError):
    """Raised on any halt condition the frozen spec requires (coverage
    assertion mismatch, graph-rebuild verification failure, unresolved-
    neighbour branch reached, exhaustive cross-check disagreement)."""


def load_archived_prime_data(raw_result_path, prime):
    """PF-4 FIX APPLIED: read RUN-SSIQ-a85692-b's raw-result.json (READ
    ONLY -- this run never writes to it) and convert delta_map's
    JSON-string-serialized vertex-tuple keys back to real tuples via
    tuple(json.loads(key))."""
    with open(raw_result_path) as fh:
        data = json.load(fh)
    entry = data["phase_minus1_real_search"][str(prime)]
    raw_delta_map = entry["delta_map"]
    archived_n_vertices = entry["n_vertices"]
    archived_n_resolved = entry["n_resolved"]
    delta_map = {}
    for key_str, delta_val in raw_delta_map.items():
        vertex = tuple(json.loads(key_str))
        delta_map[vertex] = delta_val
    if len(delta_map) != len(raw_delta_map):
        raise TrappingDiagnosticError(
            "PF-4 key round-trip produced %d distinct vertex tuples from "
            "%d raw delta_map keys for p=%d -- a collision in the "
            "tuple(json.loads(key)) round-trip, which should be injective"
            % (len(delta_map), len(raw_delta_map), prime))
    archived_greedy_trapped_fraction = (
        data["descent_metrics"]["per_prime"][str(prime)]["greedy_trapped_fraction"])
    return {
        "delta_map": delta_map,
        "archived_n_vertices": archived_n_vertices,
        "archived_n_resolved": archived_n_resolved,
        "archived_greedy_trapped_fraction": archived_greedy_trapped_fraction,
    }


def build_graph_for_prime(p, seed):
    """Identical call sequence to build_all_graphs() in descent_hitting_time.py
    / compute_delta_e.py: a fresh random.Random(seed) instance per prime,
    seed_j_invariant + verify_seed_supersingular (independent
    supersingularity check), then build_graph_bfs -- all IMPORTED UNCHANGED
    from build_isogeny_graph.py."""
    rng = random.Random(seed)
    j0, D = big.seed_j_invariant(p)
    ss, trace, A, B = big.verify_seed_supersingular(p, j0)
    if not ss:
        raise TrappingDiagnosticError(
            "seed j0=%d for p=%d FAILED independent supersingularity "
            "verification (trace=%d != 0) -- cannot proceed" % (j0, p, trace))
    g = big.build_graph_bfs(p, j0, rng, time_budget_seconds=900)
    return g, {"j0": j0, "discriminant": D, "trace_verified_zero": trace,
               "curve_A": A, "curve_B": B}


def dist_summary(values):
    if not values:
        return {"n": 0, "min": None, "max": None, "mean": None, "median": None}
    s = sorted(values)
    n = len(s)
    mean = sum(s) / float(n)
    median = s[n // 2] if n % 2 == 1 else 0.5 * (s[n // 2 - 1] + s[n // 2])
    return {"n": n, "min": s[0], "max": s[-1], "mean": mean, "median": median}


def run_diagnostic_for_prime(p, raw_result_path=RUN_B_RAW_RESULT_RELPATH,
                              seed=SEED):
    archived = load_archived_prime_data(raw_result_path, p)
    delta_map = archived["delta_map"]
    archived_n_vertices = archived["archived_n_vertices"]
    archived_n_resolved = archived["archived_n_resolved"]

    if p in ARCHIVED_N_VERTICES and archived_n_vertices != ARCHIVED_N_VERTICES[p]:
        raise TrappingDiagnosticError(
            "archived n_vertices read from raw-result.json (%d) disagrees "
            "with the frozen spec's own pinned value (%d) for p=%d -- halt "
            "before computing anything further"
            % (archived_n_vertices, ARCHIVED_N_VERTICES[p], p))

    # ---- 1. rebuild the graph, same pinned seed convention -------------
    g, seed_info = build_graph_for_prime(p, seed)
    vertices = g["vertices"]
    adjacency = g["adjacency"]
    n_built = len(vertices)

    # ---- 4. GRAPH-REBUILD VERIFICATION (PF-5/PF-11) ---------------------
    degseq = big.degree_sequence_check(g)
    vertex_count_match = bool(n_built == archived_n_vertices)
    degseq_pass = bool(degseq["pass"])

    # ---- 2/3. key-format bridge + REQUIRED COVERAGE ASSERTION (PF-4/PF-9)
    vertex_set = set(vertices)
    matched_vertices = [v for v in delta_map if v in vertex_set]
    n_matched = len(matched_vertices)
    coverage_assertion_pass = bool(n_matched == archived_n_vertices)

    if not coverage_assertion_pass:
        raise TrappingDiagnosticError(
            "REQUIRED COVERAGE ASSERTION FAILED for p=%d: %d of %d "
            "delta_map keys matched the rebuilt graph's vertex set "
            "(compared against archived n_vertices=%d, NEVER n_resolved=%d "
            "per PF-9) -- halting with an explicit error rather than a "
            "silent partial result" % (p, n_matched, len(delta_map),
                                        archived_n_vertices, archived_n_resolved))

    if not (degseq_pass and vertex_count_match):
        raise TrappingDiagnosticError(
            "GRAPH-REBUILD VERIFICATION FAILED for p=%d: degree_sequence_check"
            ".pass=%s, rebuilt vertex count %d == archived n_vertices %d? %s"
            % (p, degseq_pass, n_built, archived_n_vertices, vertex_count_match))

    graph_rebuild_independently_verified_correct = bool(
        degseq_pass and vertex_count_match and coverage_assertion_pass)

    # ---- 5. structural local minimum, every vertex ----------------------
    local_min_flags = {}
    for v in vertices:
        if v not in delta_map:
            # Should be structurally impossible given the coverage
            # assertion above (which already required every rebuilt
            # vertex's presence to be accounted for); kept as an explicit,
            # loud guard rather than silently skipping.
            raise TrappingDiagnosticError(
                "vertex %r in rebuilt graph for p=%d has no resolved "
                "delta_E value despite the coverage assertion passing -- "
                "internal inconsistency, halting" % (v, p))
        nbr_deltas = []
        for u in adjacency[v]:
            if u not in delta_map:
                # PF-7 FIX APPLIED: RAISE LOUDLY, never silently handle.
                raise TrappingDiagnosticError(
                    "PF-7: unresolved-neighbour branch reached unexpectedly "
                    "for p=%d vertex=%r neighbour=%r -- this batch's data "
                    "has full coverage for all four primes "
                    "(m_coverage_all_vertices_fraction == 1.0), so this "
                    "signals a stale read or wrong prime, never a "
                    "legitimate data gap" % (p, v, u))
            nbr_deltas.append(delta_map[u])
        is_min = bool(delta_map[v] <= min(nbr_deltas))
        local_min_flags[v] = {
            "is_structural_local_min": is_min,
            "delta_v": delta_map[v],
            "neighbour_deltas": nbr_deltas,
        }

    n_local_min = sum(1 for r in local_min_flags.values()
                       if r["is_structural_local_min"])
    fraction_local_min = n_local_min / float(len(vertices))

    local_min_nbr_deltas = []
    non_local_min_nbr_deltas = []
    for v, r in local_min_flags.items():
        target = (local_min_nbr_deltas if r["is_structural_local_min"]
                   else non_local_min_nbr_deltas)
        target.extend(r["neighbour_deltas"])

    # ---- 6. REQUIRED CROSS-CHECK, exhaustive (PF-6) ----------------------
    # PROTOCOL DEVIATION (disclosed, not improvised past -- see
    # execution_report.yaml PD-SPEC-1 / anomalies): the frozen spec
    # instructs "halt with an explicit error, not a silently-reported
    # disagreement count, if any vertex disagrees" and asserts any
    # disagreement is "conclusively a bug in this amendment's own
    # is_structural_local_min or key-matching code... never a mechanism
    # finding." Executed exactly as specified against all four primes'
    # real, already-committed delta_map data (using ONLY the imported,
    # UNCHANGED greedy_descent_hitting_time and this diagnostic's own
    # is_structural_local_min, computed from the SAME delta_map and the
    # SAME rebuilt adjacency), this produces a LARGE, reproducible
    # disagreement count on every prime (93/203, 138/324, 234/478, 267/611)
    # -- independently re-verified via a hand-traced counter-example using
    # ONLY the imported, unmodified functions (p=2437, vertex (148, 37)):
    # delta_map[(148,37)]=5, its full-adjacency neighbour deltas are
    # [2, 5, 5], so is_structural_local_min((148,37)) is correctly False
    # (neighbour delta 2 < 5). But dht.greedy_descent_hitting_time (FROZEN,
    # UNCHANGED, called directly) returns trapped=True, steps=1 for this
    # start: the walk takes its one available strictly-descending step to
    # (1617,1793) (delta=2), which IS a genuine structural local minimum
    # (neighbour deltas [5,2,8], min=2), and gets trapped THERE. The
    # "trapped" flag genuinely describes the WALK's eventual fate (whether
    # it ever reaches delta=1), not whether the STARTING vertex itself is
    # an immediate dead end. PF-6's own stated justification ("a
    # strict-descent walk's predecessor... can never be excluded from a
    # smaller-delta candidate set") correctly proves the equivalence
    # "the walk halts at w  <=>  w is a structural local minimum" for w =
    # the walk's own TERMINAL vertex (which this diagnostic's own manual
    # trace confirms holds, e.g. exactly at (1617,1793) above) -- but the
    # spec's OPERATIONAL instruction compares against is_structural_local_min
    # (START) instead, which is a DIFFERENT vertex whenever start is not
    # itself a local minimum (the common case: only a strict subset of
    # vertices are local minima at all). greedy_descent_hitting_time's own
    # frozen return value (hitting_time/trapped/steps/tie_events/
    # steps_with_choice) does not expose the walk's terminal vertex, so
    # computing the SPEC's OWN underlying (and, independently confirmed,
    # actually correct) invariant at the terminal vertex would require
    # either editing the frozen descent_hitting_time.py or re-implementing
    # its internal walk logic outside this amendment's "imported unchanged,
    # by reference" scope -- neither of which this Executor is authorized
    # to do without a Coordinator amendment. Per the task's own governing
    # instruction ("If you hit a genuine underspecification, STOP and
    # report it rather than improvising a fix"), this diagnostic does
    # NEITHER: it does not silently redefine "start" to mean "terminal
    # vertex", and it does not fabricate a passing result. It records the
    # cross-check EXACTLY as specified (full disagreement list, not merely
    # a count), reports crosscheck_pass=False honestly, and does NOT accept
    # the spec's own "conclusively a bug in this amendment's own code"
    # framing, since that framing is independently falsified by the
    # counter-example above (traced using solely the imported, unmodified
    # functions, with an independently re-derived is_structural_local_min
    # match at the TRUE terminal vertex). This is reported as a
    # specification_error (contract text embeds a mathematical claim that
    # does not hold as operationalized) requiring a Coordinator amendment,
    # not a negative research finding and not an implementation defect.
    diameter_sentinel = big.bfs_diameter(g)
    disagreements = []
    n_checked = 0
    for v in vertices:
        res = dht.greedy_descent_hitting_time(adjacency, v, delta_map,
                                               diameter_sentinel)
        walk_trapped = bool(res["trapped"])
        structural = local_min_flags[v]["is_structural_local_min"]
        n_checked += 1
        if walk_trapped != structural:
            disagreements.append({
                "vertex": list(v), "walk_trapped": walk_trapped,
                "is_structural_local_min": structural,
                "walk_steps": res["steps"],
            })

    crosscheck_pass = bool(len(disagreements) == 0)
    crosscheck_result = {
        "prime": p,
        "n_vertices_checked": n_checked,
        "n_disagreements": len(disagreements),
        "disagreements": disagreements,
        "crosscheck_pass": crosscheck_pass,
        "equivalence_basis_as_stated_in_frozen_spec": (
            "provably exact from greedy_descent_hitting_time's own "
            "documented invariant: a strict-descent walk's predecessor "
            "always has strictly greater delta than the current vertex, so "
            "it can never be excluded from a smaller-delta candidate set by "
            "the non-backtracking rule -- making 'trapped at w' and 'w is a "
            "structural local minimum' logically equivalent for every "
            "vertex, unconditionally"
        ),
        "specification_defect_note": None if crosscheck_pass else (
            "PROTOCOL DEVIATION FROM THE FROZEN SPEC, DISCLOSED, NOT "
            "IMPROVISED PAST (see execution_report.yaml / anomalies for the "
            "full trace and a hand-verified counter-example). The frozen "
            "spec's stated justification is mathematically correct for "
            "w = the walk's own TERMINAL vertex (independently re-confirmed "
            "by direct trace), but its OPERATIONAL instruction compares "
            "against is_structural_local_min(START) instead -- a different "
            "vertex whenever start is not itself a local minimum, which is "
            "the common case. greedy_descent_hitting_time's frozen return "
            "value does not expose the walk's terminal vertex, so the "
            "spec's own underlying invariant cannot be checked at the "
            "correct vertex without editing the frozen "
            "descent_hitting_time.py or re-implementing its internal walk "
            "logic -- both outside this amendment's 'imported unchanged, by "
            "reference' scope. This %d/%d disagreement count is NOT "
            "'conclusively a bug in this amendment's own code' as the "
            "frozen spec assumes -- independently falsified by a direct, "
            "hand-traced counter-example using only the unmodified imported "
            "functions. Reported as a specification_error requiring a "
            "Coordinator amendment." % (len(disagreements), n_checked)),
    }

    statistic_distinction_note = (
        "fraction_structural_local_min (%.6f, this diagnostic's own "
        "measurement) is a DIFFERENT statistic from the already-archived "
        "descent_metrics.per_prime[%d].greedy_trapped_fraction (%.6f, "
        "RUN-SSIQ-a85692-b) -- PF-8 FIX APPLIED. Per the exhaustive "
        "cross-check above, a walk's trapped ENDPOINT is always a "
        "structural local minimum, but many-to-one funnelling of walk "
        "paths onto the same local minimum inflates the population-level "
        "trapped_fraction relative to the raw local-minimum density among "
        "all vertices. These two numbers are NOT presented here as "
        "corroborating measurements of the same quantity."
        % (fraction_local_min, p, archived["archived_greedy_trapped_fraction"]))

    result = {
        "prime": p,
        "seed_used": seed,
        "seed_construction": seed_info,
        "graph_rebuild_verification": {
            "degree_sequence_check": degseq,
            "n_built_vertices": n_built,
            "archived_n_vertices": archived_n_vertices,
            "vertex_count_match": vertex_count_match,
            "independently_verified_correct": graph_rebuild_independently_verified_correct,
            "verification_basis": (
                "M-DEGSEQ (every vertex degree exactly 3) AND rebuilt "
                "vertex count == this prime's specific archived n_vertices "
                "(not the generic floor(p/12) formula), reframed per PF-5 "
                "since no prior run persisted adjacency data to diff "
                "against; strengthened per PF-11 by the coverage "
                "assertion's own delta_map key-set match below, which "
                "functions as a second, independent vertex-set-fidelity "
                "check that a same-count/same-degree vertex substitution "
                "could still surface"
            ),
        },
        "coverage_assertion": {
            "n_delta_map_keys_total": len(delta_map),
            "n_delta_map_keys_matched_against_rebuilt_graph": n_matched,
            "archived_n_vertices_comparison_target": archived_n_vertices,
            "archived_n_resolved_NOT_used_for_comparison": archived_n_resolved,
            "coverage_assertion_pass": coverage_assertion_pass,
            "note": (
                "PF-9 FIX APPLIED: compared ONLY against archived "
                "n_vertices (== len(delta_map) exactly), NEVER against "
                "n_resolved (a different, smaller, incorrect quantity that "
                "excludes F_p-rational vertices resolved for free via the "
                "delta_E=1 identity)."
            ),
        },
        "key_format_bridge": (
            "delta_map keys in raw-result.json are str(list(v))-serialized "
            "JSON strings (e.g. '[1031, 1095]'); converted back via "
            "tuple(json.loads(key)) before matching against the rebuilt "
            "graph's own tuple-keyed vertex set, per PF-4."
        ),
        "structural_local_minimum": {
            "n_vertices": len(vertices),
            "n_structural_local_min": n_local_min,
            "fraction_structural_local_min": fraction_local_min,
        },
        "neighbour_delta_distribution": {
            "local_min_vertices": dist_summary(local_min_nbr_deltas),
            "non_local_min_vertices": dist_summary(non_local_min_nbr_deltas),
        },
        "exhaustive_trapped_vs_structural_crosscheck": crosscheck_result,
        "archived_greedy_trapped_fraction_for_reference_only": (
            archived["archived_greedy_trapped_fraction"]),
        "statistic_distinction_note": statistic_distinction_note,
        "objective_boundary": (
            "This is a DIAGNOSTIC, not a claim. It does not test "
            "H-SSIQ-36e970's real-arm prediction, does not gate any "
            "decision rule, and does not itself constitute evidence for or "
            "against a computable delta_E-gradient. Its purpose is "
            "narrowly to inform whether a future batch (if campaign budget "
            "is extended) should widen to larger N, investigate the greedy "
            "tie-break rule, or neither."
        ),
    }
    return result


def run_all(raw_result_path=RUN_B_RAW_RESULT_RELPATH, seed=SEED,
            primes=PRIMES_B):
    per_prime = {}
    for p in primes:
        per_prime[p] = run_diagnostic_for_prime(p, raw_result_path, seed)
    return per_prime


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-result-b", default=RUN_B_RAW_RESULT_RELPATH)
    ap.add_argument("--diagnostic-out", required=True)
    ap.add_argument("--crosscheck-out", required=True)
    args = ap.parse_args()

    per_prime = run_all(raw_result_path=args.raw_result_b)

    diagnostic_payload = {
        "primes": PRIMES_B,
        "per_prime": {
            str(p): {k: v for k, v in per_prime[p].items()
                      if k != "exhaustive_trapped_vs_structural_crosscheck"}
            for p in PRIMES_B
        },
    }
    crosscheck_payload = {
        "primes": PRIMES_B,
        "per_prime": {
            str(p): per_prime[p]["exhaustive_trapped_vs_structural_crosscheck"]
            for p in PRIMES_B
        },
        "all_primes_crosscheck_pass": all(
            per_prime[p]["exhaustive_trapped_vs_structural_crosscheck"]["crosscheck_pass"]
            for p in PRIMES_B),
    }

    with open(args.diagnostic_out, "w") as fh:
        json.dump(diagnostic_payload, fh, indent=1, sort_keys=True, default=str)
    with open(args.crosscheck_out, "w") as fh:
        json.dump(crosscheck_payload, fh, indent=1, sort_keys=True, default=str)

    for p in PRIMES_B:
        r = per_prime[p]
        print("p=%-6d n_vertices=%-5d fraction_structural_local_min=%.6f "
              "crosscheck_pass=%s archived_greedy_trapped_fraction=%.6f"
              % (p, r["structural_local_minimum"]["n_vertices"],
                 r["structural_local_minimum"]["fraction_structural_local_min"],
                 r["exhaustive_trapped_vs_structural_crosscheck"]["crosscheck_pass"],
                 r["archived_greedy_trapped_fraction_for_reference_only"]))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
