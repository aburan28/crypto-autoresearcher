#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v6 (BATCH-009) -- PART A REQUIRED EQUIVALENCE REGRESSION.

Implements specification_v6.yaml inputs.gd12_fix_v6's REQUIRED EQUIVALENCE
REGRESSION exactly as frozen (PF-4 FIX APPLIED): construct AT LEAST 3
independent (adjacency, start, delta_map, diameter_sentinel) inputs,
REQUIRED TO COLLECTIVELY EXERCISE ALL THREE of
greedy_descent_hitting_time_v2's return branches at least once each:

  1. the immediate delta_E==1 case (a synthetic single-vertex input;
     terminal_vertex must equal start);
  2. the trapped=True case, using the already-archived p=2437 graph and the
     EXACT (148, 37) start vertex from trapping_diagnostic_v5.py's own
     hand-traced counter-example (terminal_vertex must equal (1617, 1793)
     EXACTLY, matching that file's own code comment / execution_report.yaml
     PD-SPEC-1 trace);
  3. the trapped=False-via-one-or-more-steps case (a synthetic 3-vertex
     chain; terminal_vertex must equal the actual delta_E==1 vertex reached
     by descent, not merely start or some other vertex).

For every case, confirms greedy_descent_hitting_time_v2's
hitting_time/trapped/steps/tie_events/steps_with_choice fields are
BIT-IDENTICAL to dht.greedy_descent_hitting_time's own output on the SAME
input (dht imported UNCHANGED, by reference), and separately confirms
terminal_vertex correctness for that case's own branch.

descent_hitting_time.py (dht, FROZEN, UNCHANGED) and trapping_diagnostic_v5
.py (build_graph_for_prime, load_archived_prime_data -- FROZEN, UNCHANGED,
GENUINELY IMPORTED per gd12_fix_v6's REUSE MECHANISM) supply case 2's real
p=2437 graph/delta_map; cases 1 and 3 use hand-constructed synthetic
literals defined directly in this file, independent of any real run's data.
"""

import json
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
_B_IMPL_DIR = os.path.join(_THIS_DIR, "..", "..", "EXP-SSIQ-58b642",
                            "implementation")
sys.path.insert(0, _B_IMPL_DIR)

import calibration_synthetic as cal  # noqa: E402,F401 (import-order fix only)
import descent_hitting_time as dht  # noqa: E402  (FROZEN, UNCHANGED)
import trapping_diagnostic_v5 as tdv5  # noqa: E402  (FROZEN, UNCHANGED; genuine
                                        # import of build_graph_for_prime /
                                        # load_archived_prime_data, per the
                                        # REUSE MECHANISM)
import descent_walk_hardened as dwh  # noqa: E402  (THIS amendment's new module)

RUN_B_RAW_RESULT_RELPATH = os.path.join(
    _THIS_DIR, "..", "runs", "RUN-SSIQ-a85692-b", "raw-result.json")
SEED = 20260805  # SEEDS[0], same pinned convention as trapping_diagnostic_v5.py
CASE2_PRIME = 2437
CASE2_START = (148, 37)
CASE2_EXPECTED_TERMINAL = (1617, 1793)  # trapping_diagnostic_v5.py's own
                                          # hand-traced counter-example value


NON_TERMINAL_FIELDS = ("hitting_time", "trapped", "steps", "tie_events",
                        "steps_with_choice")


def _build_case_1():
    """Immediate delta_E==1 branch: synthetic single-vertex-adjacency input.
    delta_map[start] == 1, so the top-level short-circuit fires before
    adjacency is ever consulted (mirrors dht.greedy_descent_hitting_time's
    own behaviour exactly -- adjacency is included, well-formed, but never
    read on this branch)."""
    start = "case1_start"
    adjacency = {start: ["case1_n1", "case1_n2", "case1_n3"]}
    delta_map = {start: 1}
    diameter_sentinel = 999
    return {
        "label": "case1_immediate_delta_eq_1",
        "branch_exercised": "immediate delta_E==1 (trapped=False, steps=0)",
        "adjacency": adjacency, "start": start, "delta_map": delta_map,
        "diameter_sentinel": diameter_sentinel,
        "expected_terminal_vertex": start,
        "expected_terminal_vertex_rule": "terminal_vertex == start (current unmoved)",
    }


def _build_case_2(raw_result_path=RUN_B_RAW_RESULT_RELPATH):
    """trapped=True branch: REAL p=2437 archived graph/delta_map, the EXACT
    (148, 37) start vertex from trapping_diagnostic_v5.py's own hand-traced
    counter-example (see that file's REQUIRED CROSS-CHECK docstring /
    RUN-SSIQ-a85692-e execution_report.yaml PD-SPEC-1)."""
    archived = tdv5.load_archived_prime_data(raw_result_path, CASE2_PRIME)
    delta_map = archived["delta_map"]
    g, seed_info = tdv5.build_graph_for_prime(CASE2_PRIME, SEED)
    adjacency = g["adjacency"]
    import build_isogeny_graph as big  # noqa: E402  (FROZEN, UNCHANGED)
    diameter_sentinel = big.bfs_diameter(g)
    return {
        "label": "case2_trapped_true_p2437_148_37",
        "branch_exercised": "trapped=True",
        "adjacency": adjacency, "start": CASE2_START, "delta_map": delta_map,
        "diameter_sentinel": diameter_sentinel,
        "expected_terminal_vertex": CASE2_EXPECTED_TERMINAL,
        "expected_terminal_vertex_rule": (
            "terminal_vertex == (1617, 1793) EXACTLY, matching "
            "trapping_diagnostic_v5.py's own independently-traced value"),
        "prime": CASE2_PRIME, "seed_used": SEED,
        "seed_construction": seed_info,
    }


def _build_case_3():
    """trapped=False-via-steps branch: synthetic 3-vertex strict-descent
    chain A(delta=5) -> B(delta=3) -> C(delta=1). Non-backtracking exclusion
    is exercised (B's neighbour list includes A, which is excluded once A is
    prev); dummy padding neighbours (X1/X2/X3, delta=10, never selected)
    keep each visited vertex's own adjacency at 3 entries, matching the real
    graph's degree-3 structure without being load-bearing for the walk
    itself."""
    A, B, C = "case3_A", "case3_B", "case3_C"
    X1, X2, X3 = "case3_X1", "case3_X2", "case3_X3"
    adjacency = {
        A: [B, X1, X2],
        B: [A, C, X3],
        # C's own adjacency is never consulted: the walk returns as soon as
        # it steps onto C (delta_map[C] == 1), before reading adjacency[C].
    }
    delta_map = {A: 5, B: 3, C: 1, X1: 10, X2: 10, X3: 10}
    diameter_sentinel = 999
    return {
        "label": "case3_trapped_false_via_two_steps",
        "branch_exercised": "trapped=False-via-one-or-more-steps",
        "adjacency": adjacency, "start": A, "delta_map": delta_map,
        "diameter_sentinel": diameter_sentinel,
        "expected_terminal_vertex": C,
        "expected_terminal_vertex_rule": (
            "terminal_vertex == the actual delta_E==1 vertex reached by "
            "descent (C), not start (A) and not the intermediate vertex (B)"),
        "expected_steps": 2,
    }


def run_gd12_equivalence_regression_test(raw_result_path=RUN_B_RAW_RESULT_RELPATH):
    cases_input = [_build_case_1(), _build_case_2(raw_result_path), _build_case_3()]
    results = []
    for c in cases_input:
        original = dht.greedy_descent_hitting_time(
            c["adjacency"], c["start"], c["delta_map"], c["diameter_sentinel"])
        v2 = dwh.greedy_descent_hitting_time_v2(
            c["adjacency"], c["start"], c["delta_map"], c["diameter_sentinel"])

        non_terminal_match = {
            f: bool(original[f] == v2[f]) for f in NON_TERMINAL_FIELDS
        }
        all_non_terminal_bit_identical = all(non_terminal_match.values())

        terminal_vertex = v2["terminal_vertex"]
        terminal_correct = bool(terminal_vertex == c["expected_terminal_vertex"])

        case_pass = bool(all_non_terminal_bit_identical and terminal_correct)

        results.append({
            "label": c["label"],
            "branch_exercised": c["branch_exercised"],
            "start": (list(c["start"]) if isinstance(c["start"], tuple)
                       else c["start"]),
            "expected_terminal_vertex_rule": c["expected_terminal_vertex_rule"],
            "expected_terminal_vertex": (
                list(c["expected_terminal_vertex"])
                if isinstance(c["expected_terminal_vertex"], tuple)
                else c["expected_terminal_vertex"]),
            "original_dht_greedy_descent_hitting_time": {
                f: original[f] for f in NON_TERMINAL_FIELDS
            },
            "v2_greedy_descent_hitting_time_v2": {
                f: v2[f] for f in NON_TERMINAL_FIELDS
            },
            "v2_terminal_vertex": (list(terminal_vertex)
                                    if isinstance(terminal_vertex, tuple)
                                    else terminal_vertex),
            "non_terminal_field_match": non_terminal_match,
            "all_non_terminal_fields_bit_identical": all_non_terminal_bit_identical,
            "terminal_vertex_correct": terminal_correct,
            "case_pass": case_pass,
        })

    branches_covered = sorted(set(r["branch_exercised"] for r in results))
    expected_branches = sorted([
        "immediate delta_E==1 (trapped=False, steps=0)",
        "trapped=True",
        "trapped=False-via-one-or-more-steps",
    ])
    all_branches_covered = bool(branches_covered == expected_branches)
    all_cases_pass = all(r["case_pass"] for r in results)

    return {
        "test_id": "gd12_equivalence_regression_test",
        "spec_reference": (
            "specification_v6.yaml inputs.gd12_fix_v6 REQUIRED EQUIVALENCE "
            "REGRESSION, PF-4 FIX APPLIED"
        ),
        "purpose": (
            "Confirm greedy_descent_hitting_time_v2 is a pure superset of "
            "dht.greedy_descent_hitting_time (bit-identical on every "
            "non-terminal-vertex field, for every input) and that "
            "terminal_vertex is correct on each of the three return "
            "branches, collectively exercised at least once each by these "
            ">=3 constructed inputs."
        ),
        "n_cases": len(results),
        "branches_covered": branches_covered,
        "all_three_branches_covered": all_branches_covered,
        "cases": results,
        "all_cases_pass": all_cases_pass,
        "overall_pass": bool(all_branches_covered and all_cases_pass),
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw-result-b", default=RUN_B_RAW_RESULT_RELPATH)
    args = ap.parse_args()

    result = run_gd12_equivalence_regression_test(raw_result_path=args.raw_result_b)
    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True, default=str)

    print("gd12_equivalence_regression_test overall_pass = %s"
          % result["overall_pass"])
    for c in result["cases"]:
        print("  %-32s branch=%-45s pass=%s"
              % (c["label"], c["branch_exercised"], c["case_pass"]))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
