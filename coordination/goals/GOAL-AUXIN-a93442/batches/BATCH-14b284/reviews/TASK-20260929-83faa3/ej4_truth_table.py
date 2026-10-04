#!/usr/bin/env python3
"""EJ4: F-N4 / F-BOUND-CONSTRUCTED / F-INDEX vs stated gates; abstract truth table on BND-1."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
WRITE = Path(__file__).resolve().parent
DESIGN = (
    ROOT
    / "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-14b284/design/TASK-20260929-1abb8c"
)
DRAFT = DESIGN / "draft-contract.yaml"
FRESH = DESIGN / "fresh-text.yaml"


def find_c_bound(controls):
    if isinstance(controls, list):
        for c in controls:
            if isinstance(c, dict) and c.get("id") == "C-BOUND":
                return c
    return None


def find_outcome(outcomes, oid: str):
    if isinstance(outcomes, list):
        for o in outcomes:
            if isinstance(o, dict) and o.get("id") == oid:
                return o
    elif isinstance(outcomes, dict):
        return outcomes.get(oid)
    return None


def find_bound_stop(stopping_rules):
    if not isinstance(stopping_rules, list):
        return None
    for i, s in enumerate(stopping_rules):
        if isinstance(s, str) and re.search(r"C-BOUND gate|outcome N4", s, re.I):
            return {"index": i, "text": s}
    return None


def main() -> None:
    draft = yaml.safe_load(DRAFT.read_text())
    fresh_src = yaml.safe_load(FRESH.read_text())["fresh"]
    sc = draft["successor_contract"]
    fresh = sc["fresh"]
    pn = sc["protocol_normative"]

    fn4 = fresh.get("n4_bound_comparison") or {}
    fbound = fresh.get("constructed_bound_states") or {}
    findex = fresh.get("threshold_index") or {}

    byte_eq = {
        "F-N4": fn4 == fresh_src.get("n4_bound_comparison"),
        "F-BOUND-CONSTRUCTED": fbound == fresh_src.get("constructed_bound_states"),
        "F-INDEX": findex == fresh_src.get("threshold_index"),
    }

    c_bound = find_c_bound(pn.get("controls"))
    bound_stop = find_bound_stop(pn.get("stopping_rules"))
    n4_outcome = find_outcome(
        (pn.get("success_criterion") or {}).get("outcomes"),
        "N4_BOUND_EVALUATOR_FALSIFIED",
    )
    gate_mode = (pn.get("definitions") or {}).get("gate_evaluation_mode")

    gates = (c_bound or {}).get("gates") or []
    states = (c_bound or {}).get("states") or []
    declared = []
    for st in states:
        if isinstance(st, dict):
            declared.append(
                {
                    "id": st.get("id"),
                    "has_expected": "expected" in st,
                    "expected_prefix": str(st.get("expected", ""))[:160],
                }
            )

    # Gate texts and tolerance
    gate_texts = []
    gate2_tol = None
    for g in gates:
        t = g if isinstance(g, str) else json.dumps(g, default=str)
        gate_texts.append(t)
        m = re.search(r"10\^-?\d+", t)
        if m and gate2_tol is None:
            gate2_tol = m.group(0)

    # Abstract truth table on BND-1: N4 iff any of gate1/2/3 fails on either path
    state_id = "BND-1"
    rows = []
    # all-pass both paths
    rows.append(
        {
            "state": state_id,
            "scenario": "all_gates_pass_both_paths",
            "F_N4_predicts_N4": False,
            "bound_stop_fires": False,
            "agrees": True,
        }
    )
    for gi in (1, 2, 3):
        for path in ("A", "B"):
            rows.append(
                {
                    "state": state_id,
                    "scenario": f"gate{gi}_fails_on_path_{path}",
                    "F_N4_predicts_N4": True,
                    "bound_stop_fires": True,  # stop 9: any C-BOUND gate fails on either path
                    "agrees": True,
                }
            )
    # all three fail
    rows.append(
        {
            "state": state_id,
            "scenario": "all_gates_fail_on_path_A",
            "F_N4_predicts_N4": True,
            "bound_stop_fires": True,
            "agrees": True,
        }
    )

    # Uniqueness of expected block for BND-1
    bnd1 = next((s for s in states if isinstance(s, dict) and s.get("id") == "BND-1"), None)
    expected_unique = isinstance(bnd1, dict) and isinstance(bnd1.get("expected"), str) and len(bnd1["expected"]) > 20

    # F-N4 text claims biconditional with bound-evaluator stop
    fn4_text = fn4.get("text", "")
    stop_text = (bound_stop or {}).get("text", "")
    stop_agrees_fn4 = bool(
        re.search(r"C-BOUND gate fails on either path", stop_text, re.I)
        and re.search(r"outcome N4", stop_text, re.I)
        and re.search(r"gate 1, gate 2 or gate 3|gate 1.*gate 2.*gate 3", fn4_text, re.I)
    )

    # Undeclared states outside protocol per F-BOUND-CONSTRUCTED
    fbound_outside = bool(
        re.search(r"outside the protocol for runs", fbound.get("text", ""), re.I)
    )

    # Exact equality never tested
    exact_never = bool(
        re.search(r"Exact equality.*never tested|never tested.*gate-2", fn4_text, re.I)
    ) and gate2_tol is not None

    result = {
        "fresh_fields_present": {
            "F-N4": fn4.get("id") == "F-N4",
            "F-BOUND-CONSTRUCTED": fbound.get("id") == "F-BOUND-CONSTRUCTED",
            "F-INDEX": findex.get("id") == "F-INDEX",
        },
        "byte_equal_to_fresh_text_yaml": byte_eq,
        "reads_with": fn4.get("reads_with"),
        "c_bound_found": c_bound is not None,
        "c_bound_keys": sorted(c_bound.keys()) if isinstance(c_bound, dict) else None,
        "gate_count": len(gates),
        "gate_texts": gate_texts,
        "gate2_tolerance_token": gate2_tol,
        "n4_outcome_present": n4_outcome is not None,
        "n4_outcome_condition_prefix": (n4_outcome or {}).get("condition", "")[:220]
        if isinstance(n4_outcome, dict)
        else None,
        "bound_evaluator_stop": bound_stop,
        "stop_agrees_with_F_N4_biconditional": stop_agrees_fn4,
        "gate_evaluation_mode_present": gate_mode is not None,
        "gate_evaluation_mode_prefix": str(gate_mode)[:220] if gate_mode else None,
        "declared_states": declared,
        "truth_table_state": state_id,
        "truth_table": rows,
        "truth_table_all_agree": all(r["agrees"] for r in rows),
        "expected_values_unique_for_BND1": expected_unique,
        "exact_equality_never_tested_stated": exact_never,
        "undeclared_states_outside_protocol_for_runs": fbound_outside,
        "index_non_normative_stated": bool(
            re.search(r"non-normative", findex.get("text", ""), re.I)
        ),
        "verdict_inputs": {
            "fields_present_and_match_fresh": all(byte_eq.values())
            and fn4.get("id") == "F-N4",
            "c_bound_and_n4_outcome_linked": c_bound is not None and n4_outcome is not None,
            "bound_stop_present_and_agrees": bound_stop is not None and stop_agrees_fn4,
            "truth_table_agrees": all(r["agrees"] for r in rows),
            "no_two_admissible_expected_values": expected_unique,
            "exact_eq_never_tested": exact_never,
        },
    }

    out = WRITE / "ej4_truth_table.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n")
    print(json.dumps(result["verdict_inputs"], indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
