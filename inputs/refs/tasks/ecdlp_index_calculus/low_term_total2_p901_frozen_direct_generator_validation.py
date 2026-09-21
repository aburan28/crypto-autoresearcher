#!/usr/bin/env python3
"""P901 frozen validation for the P900 direct-generator family."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p899_source_generator_axis_stop_audit as p899
import low_term_total2_p900_public_prefilter_ordering_audit as p900


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p901_frozen_direct_generator_validation.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p901_frozen_direct_generator_validation_probe.json"
DEFAULT_SOURCES = [
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_976_983_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_984_991_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_992_999_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1000_1007_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1008_1015_expanded_probe.json",
    STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_1016_1023_expanded_probe.json",
]
SCHEMA = "ecdlp.low_term_total2_p901_frozen_direct_generator_validation.v1"
TARGET = p899.TARGET
POLICY = "leaf_b"
STRICT_TARGET_OPS = 136
MARGIN_TARGET_OPS = 135


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p899.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def leaf_signature(case: dict[str, Any]) -> str:
    leaves = [
        int_value(leaf)
        for row_leaf in case.get("row_leaf_keys") or []
        for leaf in row_leaf.get("leaf_indices") or []
    ]
    return "/".join(str(leaf) for leaf in leaves)


def frozen_family_matches(case: dict[str, Any]) -> bool:
    return (
        str(case.get("target")) == TARGET
        and leaf_signature(case) == "19/19"
        and int_value(case.get("top_k")) == 4
        and p900.selector_group(str(case.get("selector"))) in {"low_leaf", "hybrid"}
        and float_value(case.get("ops_over_rho")) >= 0.70
    )


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    row_leaf_keys = case.get("row_leaf_keys") or []
    salts = [p900.row_salt(str(row.get("row_key"))) for row in row_leaf_keys]
    return {
        "leaf_signature": leaf_signature(case),
        "ops_over_rho": case.get("ops_over_rho"),
        "policy": case.get("policy"),
        "public_key_verified": case.get("public_key_verified"),
        "rank": case.get("rank"),
        "relation_count": case.get("relation_count"),
        "row_leaf_keys": row_leaf_keys,
        "row_salts": salts,
        "row_selector": case.get("row_selector"),
        "selector": case.get("selector"),
        "selector_group": p900.selector_group(str(case.get("selector"))),
        "source": case.get("source"),
        "source_index": case.get("source_index"),
        "source_stream_ordinal": case.get("source_stream_ordinal"),
        "source_verified": case.get("source_verified"),
        "target": case.get("target"),
        "top_k": case.get("top_k"),
        "transfer_index": case.get("transfer_index"),
    }


def compact_eval(item: dict[str, Any], total_cost: int | None = None) -> dict[str, Any]:
    case = item.get("case") or {}
    return {
        "case": compact_case(case),
        "concrete_union_dedup_ops": item.get("concrete_union_dedup_ops"),
        "concrete_union_dedup_ops_over_rho": item.get("concrete_union_dedup_ops_over_rho"),
        "errors": item.get("errors"),
        "generator_case_cost_ops": item.get("generator_case_cost_ops"),
        "public_key_verified": case.get("public_key_verified"),
        "reconstructed": item.get("reconstructed"),
        "rho_estimate": item.get("rho_estimate"),
        "strict_below_rho": item.get("strict_below_rho"),
        "strict_below_rho_margin_ops": item.get("strict_below_rho_margin_ops"),
        "total_cost_ops": total_cost,
    }


def is_good_stop(item: dict[str, Any] | None) -> bool:
    if not item:
        return False
    return bool(item.get("strict_below_rho") and (item.get("case") or {}).get("public_key_verified"))


def source_case_cost(item: dict[str, Any]) -> int:
    if item.get("reconstructed"):
        return max(1, int_value(item.get("concrete_union_dedup_ops")))
    row_results = item.get("row_results") or []
    cost = sum(p899.row_attempt_cost(row) for row in row_results if isinstance(row, dict))
    return max(1, cost)


def evaluate_generated_order(evaluated: list[dict[str, Any]], order_name: str) -> dict[str, Any]:
    if order_name == "artifact":
        rows = sorted(evaluated, key=lambda item: ((item.get("case") or {}).get("source_stream_ordinal"), (item.get("case") or {}).get("selector")))
    elif order_name == "source_ops_desc_artifact":
        rows = sorted(
            evaluated,
            key=lambda item: (
                -float_value((item.get("case") or {}).get("ops_over_rho")),
                int_value((item.get("case") or {}).get("source_stream_ordinal")),
                str((item.get("case") or {}).get("selector")),
            ),
        )
    else:
        raise ValueError(f"unknown order {order_name!r}")
    generation_cost = 0
    rematerialization_cost = 0
    false_before = 0
    first_generated = rows[0] if rows else None
    first_strict = None
    for item in rows:
        generation_cost += 1
        rematerialization_cost += int_value(item.get("generator_case_cost_ops"), 1)
        if item.get("strict_below_rho"):
            first_strict = item
            break
        false_before += 1
    total = generation_cost + rematerialization_cost
    return {
        "false_generated_before_stop": false_before,
        "first_generated": compact_eval(first_generated) if first_generated else None,
        "first_strict_stop": compact_eval(first_strict, total) if first_strict else None,
        "first_strict_stop_good": is_good_stop(first_strict),
        "generation_cost_ops": generation_cost,
        "margin_pass": bool(first_strict and is_good_stop(first_strict) and total <= MARGIN_TARGET_OPS),
        "mode": f"direct_family_{order_name}",
        "rematerialization_cost_ops": rematerialization_cost,
        "selected_count": len(rows),
        "strict_boundary_pass": bool(first_strict and is_good_stop(first_strict) and total <= STRICT_TARGET_OPS),
        "total_cost_ops": total,
        "total_cost_over_rho": ratio(total, STRICT_TARGET_OPS + 1),
    }


def evaluate_artifact_control(
    all_cases: list[dict[str, Any]],
    evaluated_by_ordinal_selector: dict[tuple[int, str], dict[str, Any]],
) -> dict[str, Any]:
    screen_cost = 0
    rematerialization_cost = 0
    selected_before = 0
    false_before = 0
    first_selected = None
    first_strict = None
    for case in all_cases:
        screen_cost += 1
        if not frozen_family_matches(case):
            continue
        key = (int_value(case.get("source_stream_ordinal")), str(case.get("selector")))
        item = evaluated_by_ordinal_selector.get(key)
        if item is None:
            continue
        selected_before += 1
        rematerialization_cost += int_value(item.get("generator_case_cost_ops"), 1)
        if first_selected is None:
            first_selected = item
        if item.get("strict_below_rho"):
            first_strict = item
            break
        false_before += 1
    total = screen_cost + rematerialization_cost
    return {
        "false_selected_before_stop": false_before,
        "first_selected": compact_eval(first_selected) if first_selected else None,
        "first_strict_stop": compact_eval(first_strict, total) if first_strict else None,
        "first_strict_stop_good": is_good_stop(first_strict),
        "margin_pass": bool(first_strict and is_good_stop(first_strict) and total <= MARGIN_TARGET_OPS),
        "mode": "artifact_order_control",
        "rematerialization_cost_ops": rematerialization_cost,
        "screen_cost_ops": screen_cost,
        "selected_before_stop_count": selected_before,
        "strict_boundary_pass": bool(first_strict and is_good_stop(first_strict) and total <= STRICT_TARGET_OPS),
        "total_cost_ops": total,
        "total_cost_over_rho": ratio(total, STRICT_TARGET_OPS + 1),
    }


def determine_claim(artifact: dict[str, Any], direct_artifact: dict[str, Any], direct_priority: dict[str, Any], selected_count: int) -> str:
    if artifact.get("strict_boundary_pass"):
        return "P901_FROZEN_FAMILY_ARTIFACT_ORDER_SOURCE_PASS"
    if direct_artifact.get("margin_pass"):
        return "P901_FROZEN_DIRECT_GENERATOR_MARGIN_PASS"
    if direct_artifact.get("strict_boundary_pass"):
        return "P901_FROZEN_DIRECT_GENERATOR_EXACT_BOUNDARY_ONLY"
    if direct_priority.get("margin_pass"):
        return "P901_DIAGNOSTIC_PRIORITY_ORDER_MARGIN_PASS_NEEDS_GENERATOR"
    if direct_priority.get("strict_boundary_pass"):
        return "P901_DIAGNOSTIC_PRIORITY_ORDER_EXACT_BOUNDARY_NEEDS_GENERATOR"
    if direct_artifact.get("first_strict_stop") or direct_priority.get("first_strict_stop"):
        return "NEGATIVE_RESULT_P901_STRICT_STOP_COST_ABOVE_RHO"
    if selected_count:
        return "NEGATIVE_RESULT_P901_FROZEN_FAMILY_SELECTS_NO_STRICT_STOP"
    return "NEGATIVE_RESULT_P901_FROZEN_FAMILY_SELECTS_NO_FRESH_CASES"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    sources = [Path(source) for source in (args.source or DEFAULT_SOURCES)]
    all_cases: list[dict[str, Any]] = []
    source_counts: dict[str, int] = {}
    for source in sources:
        cases = p899.cases_for_expanded_source(source)
        source_counts[str(source)] = len(cases)
        all_cases.extend(cases)
    for ordinal, case in enumerate(all_cases):
        case["source_stream_ordinal"] = int(ordinal)
    selected_cases = [case for case in all_cases if frozen_family_matches(case)]
    ps = p899.p897.p893.p842.load_module("ecdlp_public_slice_for_p901", p899.p897.p893.p842.PUBLIC_SLICE_SCRIPT)
    records_by_case = p899.load_records_by_case(ps, selected_cases, int(args.max_factor_degree))
    evaluated: list[dict[str, Any]] = []
    for case_index, case in enumerate(selected_cases):
        local_records = p899.local_records_for_case(records_by_case, case_index, case)
        item = p899.p897.evaluate_case_policy(ps, local_records, case, POLICY)
        item_case = item.setdefault("case", {})
        item_case["source"] = case.get("source")
        item_case["source_index"] = case.get("source_index")
        item_case["source_stream_ordinal"] = case.get("source_stream_ordinal")
        item_case["target"] = case.get("target")
        item["generator_case_cost_ops"] = source_case_cost(item)
        evaluated.append(item)
    evaluated_by_key = {
        (int_value((item.get("case") or {}).get("source_stream_ordinal")), str((item.get("case") or {}).get("selector"))): item
        for item in evaluated
    }
    artifact = evaluate_artifact_control(all_cases, evaluated_by_key)
    direct_artifact = evaluate_generated_order(evaluated, "artifact")
    direct_priority = evaluate_generated_order(evaluated, "source_ops_desc_artifact")
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(artifact, direct_artifact, direct_priority, len(selected_cases)),
        "created_at": now_iso(),
        "evaluated_generated_cases": evaluated,
        "frozen_family": {
            "axis_policy": POLICY,
            "leaf_signature": "19/19",
            "selector_groups": ["hybrid", "low_leaf"],
            "source_ops_min": 0.70,
            "top_k": 4,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN-FAMILY: filter was fixed from P900 before this fresh holdout.",
            "DIRECT-GENERATOR ASSUMPTION: direct-family cost assumes feature-family enumeration exists.",
            "POLLARD-RHO BOUNDARY: this is a source-generation validation, not a complete ECDLP algorithm.",
        ],
        "method": "p901_frozen_direct_generator_validation",
        "parameters": {
            "fresh_source_count": len(sources),
            "fresh_source_case_count": len(all_cases),
            "margin_target_ops": MARGIN_TARGET_OPS,
            "max_factor_degree": int(args.max_factor_degree),
            "strict_target_ops": STRICT_TARGET_OPS,
            "target": TARGET,
        },
        "schema": SCHEMA,
        "source_paths": [str(source) for source in sources],
        "summary": {
            "artifact_order_control": artifact,
            "direct_family_artifact_order": direct_artifact,
            "direct_family_source_ops_priority": direct_priority,
            "fresh_source_case_count_by_path": source_counts,
            "selected_generated_case_count": len(selected_cases),
            "strict_generated_case_count": len([item for item in evaluated if item.get("strict_below_rho")]),
            "verified_generated_case_count": len([item for item in evaluated if (item.get("case") or {}).get("public_key_verified")]),
            "verified_strict_generated_case_count": len([item for item in evaluated if is_good_stop(item)]),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, action="append")
    parser.add_argument("--max-factor-degree", type=int, default=1)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "frozen_family": payload["frozen_family"],
                "parameters": payload["parameters"],
                "summary": payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
