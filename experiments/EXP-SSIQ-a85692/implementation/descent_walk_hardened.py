#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-a85692 v6 (BATCH-009) -- PART A: gd12_fix_v6.

Implements experiments/EXP-SSIQ-a85692/specification_v6.yaml
inputs.gd12_fix_v6's descent_walk_hardened.py requirement EXACTLY as frozen:
supersedes (never edits) EXP-SSIQ-58b642's own frozen
descent_hitting_time.greedy_descent_hitting_time by ADDITION, defining ONE
new function, greedy_descent_hitting_time_v2, a pure superset of the
original that ALSO exposes the walk's TERMINAL vertex ("terminal_vertex":
the value of `current` at the exact point of return).

This module defines EXACTLY ONE function. The REQUIRED EQUIVALENCE
REGRESSION (bit-identical non-terminal-vertex fields, branch-coverage
required) lives in a SEPARATE file, gd12_equivalence_regression_test.py --
the same file/test separation this lineage's own ols_hardened.py /
gd11_regression_test.py pair already established for GD-11's fix
(specification_v5.yaml).

descent_hitting_time.py (EXP-SSIQ-58b642's own frozen artifact) is imported
UNCHANGED, by reference, for exactly one symbol: tie_break_choice (the
content-derived tie-break rule, per gd12_fix_v6's own text: "the tied-
neighbour tie-break via the imported, unchanged tie_break_choice"). It is
never modified, forked, or reimplemented by this file.
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
_B_IMPL_DIR = os.path.join(_THIS_DIR, "..", "..", "EXP-SSIQ-58b642",
                            "implementation")
sys.path.insert(0, _B_IMPL_DIR)

# Import order matters -- see trapping_diagnostic_v5.py's own note: a
# genuine circular import exists between the frozen, unchanged
# descent_hitting_time.py and calibration_synthetic.py; importing
# calibration_synthetic FIRST in this process avoids it (same order every
# other module in this lineage already uses). Neither frozen file is
# modified here.
import calibration_synthetic as cal  # noqa: E402,F401 (import-order fix only)
import descent_hitting_time as dht  # noqa: E402  (FROZEN, UNCHANGED)

__all__ = ["greedy_descent_hitting_time_v2"]


def greedy_descent_hitting_time_v2(adjacency, start, delta_map,
                                    diameter_sentinel):
    """Pure superset of dht.greedy_descent_hitting_time: IDENTICAL walk
    logic in every branch (the delta_E==1 immediate check, the non-
    backtracking candidate exclusion, the tied-neighbour tie-break via
    dht.tie_break_choice -- imported, unchanged -- and the strict-descent
    termination guarantee), with one addition: every returned dict ALSO
    carries "terminal_vertex", the value of `current` at the EXACT point of
    return:
      - the immediate delta_E==1 branch: terminal_vertex == start (current
        is never reassigned before this return).
      - the trapped=True branch: terminal_vertex == the trapped vertex
        (current at the moment no smaller-delta candidate exists).
      - the trapped=False-via-steps branch: terminal_vertex == the
        delta_E==1 vertex the walk descended to (current after the final
        step, immediately before this return).

    hitting_time/trapped/steps/tie_events/steps_with_choice are computed by
    the IDENTICAL walk logic as dht.greedy_descent_hitting_time and are
    REQUIRED to be bit-identical to that function's own output on every
    input (gd12_equivalence_regression_test.py's required regression
    control), never merely intended to be."""
    current = start
    prev = None
    steps = 0
    tie_events = 0
    steps_with_choice = 0
    if delta_map[start] == 1:
        return {"hitting_time": 0, "trapped": False, "steps": 0,
                "tie_events": 0, "steps_with_choice": 0,
                "terminal_vertex": current}
    while True:
        nbrs = [v for v in adjacency[current] if v != prev]
        if not nbrs:
            nbrs = list(adjacency[current])
        cur_delta = delta_map[current]
        candidates = [v for v in nbrs if delta_map[v] < cur_delta]
        if not candidates:
            return {"hitting_time": diameter_sentinel, "trapped": True,
                    "steps": steps, "tie_events": tie_events,
                    "steps_with_choice": steps_with_choice,
                    "terminal_vertex": current}
        steps_with_choice += 1
        min_delta = min(delta_map[v] for v in candidates)
        tied = [v for v in candidates if delta_map[v] == min_delta]
        if len(tied) > 1:
            tie_events += 1
            nxt = dht.tie_break_choice(min_delta, tied)
        else:
            nxt = tied[0]
        prev = current
        current = nxt
        steps += 1
        if delta_map[current] == 1:
            return {"hitting_time": steps, "trapped": False, "steps": steps,
                    "tie_events": tie_events,
                    "steps_with_choice": steps_with_choice,
                    "terminal_vertex": current}
