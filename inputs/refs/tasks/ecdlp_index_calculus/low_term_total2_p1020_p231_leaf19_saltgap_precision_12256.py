#!/usr/bin/env python3
"""P1020 salt-gap precision audit for the leaf-19 companion scheduler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1008_p231_expanded_rule_early_stop_11984 as p1008
import low_term_total2_p1009_p231_expanded_rule_family_fallback_11984 as p1009
import low_term_total2_p1010_p231_stress_row_completion_11992 as p1010
import low_term_total2_p1015_p231_cross_window_public_invariant_12056 as p1015
import low_term_total2_p1017_p231_topk4_companion_row_repair_12136 as p1017
import low_term_total2_p1018_p231_leaf19_companion_salt_guard_12176 as p1018


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1020_p231_leaf19_saltgap_precision_12256.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1020_p231_leaf19_saltgap_precision_12256_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1020_p231_leaf19_saltgap_precision_12256.v1"
DEFAULT_TARGET = p1010.DEFAULT_TARGET
POSITIVE_CALIBRATION_WINDOWS = ["12184_12191", "12192_12199", "12216_12223"]
NEGATIVE_CALIBRATION_WINDOWS = ["12224_12231"]
VALIDATION_WINDOWS = [
    "12256_12263",
    "12264_12271",
    "12272_12279",
    "12280_12287",
    "12288_12295",
    "12296_12303",
    "12304_12311",
]
ORDER_NAME = "salt_gap_asc_ops"
BASE_RULE_NAME = "topk4_anchor_leaf19_hybrid_unbounded"
PRIMARY_RULE_NAME = "topk4_anchor_leaf19_hybrid_saltgap_ge3"
SALT_GAP_MIN = 3

Predicate = Callable[[dict[str, Any]], bool]
PredicateFactory = Callable[[list[dict[str, Any]]], Predicate]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1010.int_value(value, default)


def fixed_order() -> dict[str, Any]:
    orders = {order["name"]: order for order in p1009.public_order_candidates()}
    if ORDER_NAME not in orders:
        raise KeyError(f"missing frozen order {ORDER_NAME}")
    return orders[ORDER_NAME]


def salt_values(row: dict[str, Any]) -> tuple[int, ...]:
    return p1018.salt_values(row)


def salt_gap(row: dict[str, Any]) -> int:
    features = row.get("features") or {}
    if features.get("salt_gap") is not None:
        return int_value(features.get("salt_gap"))
    values = salt_values(row)
    return max(values) - min(values) if values else -1


def min_salt(row: dict[str, Any]) -> int:
    values = salt_values(row)
    return min(values) if values else 10**9


def max_salt(row: dict[str, Any]) -> int:
    values = salt_values(row)
    return max(values) if values else 10**9


def source_ops_over_rho(row: dict[str, Any]) -> float:
    return float((row.get("source_case") or {}).get("source_ops_over_rho") or 0.0)


def has_salt(row: dict[str, Any], salt: int) -> bool:
    return salt in salt_values(row)


def base_predicate_for(rows: list[dict[str, Any]]) -> Predicate:
    keys = p1017.companion_keys(rows)
    return lambda row, keys=keys: p1017.row_key_set(row) in keys and p1018.leaf19_hybrid(row)


def saltgap_predicate_for(rows: list[dict[str, Any]]) -> Predicate:
    base = base_predicate_for(rows)
    return lambda row, base=base: base(row) and salt_gap(row) >= SALT_GAP_MIN


def min_salt_predicate_for(rows: list[dict[str, Any]]) -> Predicate:
    base = saltgap_predicate_for(rows)
    return lambda row, base=base: base(row) and min_salt(row) <= 170


def ops_predicate_for(rows: list[dict[str, Any]]) -> Predicate:
    base = saltgap_predicate_for(rows)
    return lambda row, base=base: base(row) and source_ops_over_rho(row) >= 0.7


def salt165_predicate_for(rows: list[dict[str, Any]]) -> Predicate:
    base = saltgap_predicate_for(rows)
    return lambda row, base=base: base(row) and has_salt(row, 165)


def rule_catalog() -> list[dict[str, Any]]:
    return [
        {
            "claim_role": "baseline",
            "description": "P1019 unbounded exact anchor row-key plus cost-hybrid leaf-19 scheduler",
            "factory": base_predicate_for,
            "name": BASE_RULE_NAME,
        },
        {
            "claim_role": "primary",
            "description": "P1019 unbounded scheduler with public salt gap >= 3",
            "factory": saltgap_predicate_for,
            "name": PRIMARY_RULE_NAME,
        },
        {
            "claim_role": "diagnostic",
            "description": "primary salt-gap rule plus min salt <= 170",
            "factory": min_salt_predicate_for,
            "name": "topk4_anchor_leaf19_hybrid_saltgap_ge3_minsalt_le170",
        },
        {
            "claim_role": "diagnostic",
            "description": "primary salt-gap rule plus source ops/rho >= 0.7",
            "factory": ops_predicate_for,
            "name": "topk4_anchor_leaf19_hybrid_saltgap_ge3_ops_ge_0p7",
        },
        {
            "claim_role": "diagnostic",
            "description": "primary salt-gap rule plus row key set contains salt165",
            "factory": salt165_predicate_for,
            "name": "topk4_anchor_leaf19_hybrid_saltgap_ge3_contains_salt165",
        },
    ]


def candidate(rule: dict[str, Any], predicate: Predicate) -> dict[str, Any]:
    return {
        "candidate": {
            "claim_role": rule["claim_role"],
            "description": rule["description"],
            "member_count": 1,
            "members": [rule["name"]],
            "name": rule["name"],
        },
        "predicate": predicate,
    }


def selected_case_summary(row: dict[str, Any]) -> dict[str, Any]:
    return p1015.selected_case_summary(row) | {
        "max_salt": max_salt(row),
        "min_salt": min_salt(row),
        "row_key_set": p1017.row_key_set(row),
        "salt_gap": salt_gap(row),
        "salt_values": salt_values(row),
    }


def lane_full(
    name: str,
    rows: list[dict[str, Any]],
    candidate_payload: dict[str, Any],
    order: dict[str, Any],
    baseline_rank: int,
) -> dict[str, Any]:
    predicate = candidate_payload["predicate"]
    selected = [row for row in rows if predicate(row)]
    analysis, groups = p1005.scalar_valid_groups(
        selected,
        {
            "frozen_order": ORDER_NAME,
            "lane": name,
            "rule_family": candidate_payload["candidate"]["name"],
            "rule_members": candidate_payload["candidate"]["members"],
        },
        baseline_rank,
    )
    fixed_first = p1008.first_hit_summary(selected, groups, order)
    return {
        "analysis_summary": analysis.get("summary"),
        "candidate": candidate_payload["candidate"],
        "fixed_order_first_hit": fixed_first,
        "groups": [p1005.compact_group(group) for group in groups[:12]],
        "selected_cases": [selected_case_summary(row) for row in selected[:64]],
        "stress_selection": p1015.stress_score(rows, predicate),
    }


def lane_success(lane: dict[str, Any]) -> bool:
    return p1015.lane_success(lane)


def compact_lane_summary(lane: dict[str, Any]) -> dict[str, Any]:
    return p1015.compact_lane_summary(lane) | {"candidate": lane.get("candidate")}


def aggregate(lanes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    selected = 0
    positives = 0
    groups = 0
    ops = 0.0
    noisy_windows: list[str] = []
    false_only_windows: list[str] = []
    selected_windows: list[str] = []
    success_windows: list[str] = []
    for window, lane in lanes.items():
        stress = lane.get("stress_selection") or {}
        analysis = lane.get("analysis_summary") or {}
        selected_count = int_value(stress.get("selected_count"))
        positive_count = int_value(stress.get("selected_positive_count"))
        selected += selected_count
        positives += positive_count
        groups += int_value(analysis.get("context_safe_scalar_valid_group_count"))
        ops += float(stress.get("selected_direct_sum_ops_over_rho") or 0.0)
        if selected_count:
            selected_windows.append(window)
        if selected_count > positive_count:
            noisy_windows.append(window)
        if selected_count and positive_count == 0:
            false_only_windows.append(window)
        if lane_success(lane):
            success_windows.append(window)
    false_count = max(0, selected - positives)
    return {
        "batch_precision": p1007.safe_ratio(positives, selected),
        "batch_selected_count": selected,
        "batch_selected_false_count": false_count,
        "batch_selected_ops_over_rho": round(ops, 8),
        "batch_selected_positive_count": positives,
        "context_safe_scalar_valid_group_count": groups,
        "false_only_windows": false_only_windows,
        "noisy_windows": noisy_windows,
        "selected_windows": selected_windows,
        "success_windows": success_windows,
    }


def evaluate_rule(
    windows: list[str],
    by_window: dict[str, list[dict[str, Any]]],
    rule: dict[str, Any],
    order: dict[str, Any],
    baseline_rank: int,
    prefix: str,
) -> dict[str, dict[str, Any]]:
    lanes: dict[str, dict[str, Any]] = {}
    factory: PredicateFactory = rule["factory"]
    for window in windows:
        predicate = factory(by_window[window])
        lanes[window] = lane_full(
            f"{prefix}_{rule['name']}_{window}",
            by_window[window],
            candidate(rule, predicate),
            order,
            baseline_rank,
        )
    return lanes


def determine_claim(
    positive_controls_pass: bool,
    negative_controls_pass: bool,
    validation_summary: dict[str, Any],
) -> str:
    if not positive_controls_pass:
        return "NEGATIVE_RESULT_P1020_POSITIVE_CONTROL_FAILURE"
    if not negative_controls_pass:
        return "NEGATIVE_RESULT_P1020_NEGATIVE_CONTROL_FAILURE"
    if validation_summary["success_windows"] and int_value(validation_summary.get("batch_selected_false_count")) == 0:
        return "P1020_LEAF19_SALTGAP_VALIDATION_HIT_CLEAN"
    if validation_summary["success_windows"]:
        return "P1020_LEAF19_SALTGAP_VALIDATION_HIT_WITH_NOISE"
    if int_value(validation_summary.get("batch_selected_count")) == 0:
        return "NEGATIVE_RESULT_P1020_VALIDATION_SELECTS_NO_ROWS"
    if int_value(validation_summary.get("batch_selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P1020_VALIDATION_NO_BUILDER_VISIBLE_POSITIVES"
    if int_value(validation_summary.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1020_VALIDATION_NO_CONTEXT_SAFE_SCALAR_GROUP"
    return "NEGATIVE_RESULT_P1020_VALIDATION_FIRST_HIT_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    order = fixed_order()
    all_windows = [
        *POSITIVE_CALIBRATION_WINDOWS,
        *NEGATIVE_CALIBRATION_WINDOWS,
        *VALIDATION_WINDOWS,
    ]
    by_window, exists = p1010.build_window_rows(all_windows, args.targets, args.min_source_rank)
    rules = rule_catalog()
    primary_rule = next(rule for rule in rules if rule["name"] == PRIMARY_RULE_NAME)
    primary_positive = evaluate_rule(
        POSITIVE_CALIBRATION_WINDOWS,
        by_window,
        primary_rule,
        order,
        args.baseline_rank,
        "positive_calibration",
    )
    primary_negative = evaluate_rule(
        NEGATIVE_CALIBRATION_WINDOWS,
        by_window,
        primary_rule,
        order,
        args.baseline_rank,
        "negative_calibration",
    )
    primary_validation = evaluate_rule(
        VALIDATION_WINDOWS,
        by_window,
        primary_rule,
        order,
        args.baseline_rank,
        "validation",
    )
    comparison_validation = {
        rule["name"]: evaluate_rule(
            VALIDATION_WINDOWS,
            by_window,
            rule,
            order,
            args.baseline_rank,
            "comparison",
        )
        for rule in rules
    }
    positive_summary = aggregate(primary_positive)
    negative_summary = aggregate(primary_negative)
    validation_summary = aggregate(primary_validation)
    comparison_summaries = {name: aggregate(lanes) for name, lanes in comparison_validation.items()}
    positive_controls_pass = all(lane_success(lane) for lane in primary_positive.values())
    negative_controls_pass = all(
        int_value((lane.get("stress_selection") or {}).get("selected_count")) == 0
        for lane in primary_negative.values()
    )
    claim = determine_claim(positive_controls_pass, negative_controls_pass, validation_summary)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": {window: p1005.sha256_file(p1007.expanded_source_path(window)) for window in all_windows},
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1020_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "FROZEN-PRIMARY-RULE BOUNDARY: claim is based only on the pre-registered salt_gap >= 3 rule.",
            "DIAGNOSTIC-VARIANT BOUNDARY: stricter comparison rules are reported for next-hypothesis generation only.",
            "VALIDATION BOUNDARY: 12256_12311 windows are the fresh validation batch.",
            "CONTEXT-SAFE-GATE: scalar-valid groups spanning multiple public fingerprints are rejected.",
            "INDEX-CALCULUS BOUNDARY: this is relation-surface prediction, not sparse linear algebra, target descent, or cryptographic-size evidence.",
        ],
        "method": "p1020_p231_leaf19_saltgap_precision_12256",
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "fresh_validation_windows": VALIDATION_WINDOWS,
            "frozen_order": {"description": order["description"], "name": order["name"]},
            "min_source_rank": args.min_source_rank,
            "negative_calibration_windows": NEGATIVE_CALIBRATION_WINDOWS,
            "positive_calibration_windows": POSITIVE_CALIBRATION_WINDOWS,
            "primary_rule": PRIMARY_RULE_NAME,
            "salt_gap_min": SALT_GAP_MIN,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "rules": [
            {
                "claim_role": rule["claim_role"],
                "description": rule["description"],
                "name": rule["name"],
            }
            for rule in rules
        ],
        "schema": SCHEMA,
        "source": {
            "exists": exists,
            "summaries": {window: p1007.source_summary(window) for window in all_windows},
        },
        "summary": {
            "claim_status": claim,
            "comparison_validation_summaries": comparison_summaries,
            "negative_calibration_pass": negative_controls_pass,
            "negative_calibration_primary": {
                window: compact_lane_summary(lane) for window, lane in primary_negative.items()
            },
            "negative_calibration_summary": negative_summary,
            "positive_calibration_pass": positive_controls_pass,
            "positive_calibration_primary": {
                window: compact_lane_summary(lane) for window, lane in primary_positive.items()
            },
            "positive_calibration_summary": positive_summary,
            "validation_aggregate": validation_summary,
            "validation_primary": {
                window: compact_lane_summary(lane) for window, lane in primary_validation.items()
            },
        },
        "lanes": {
            "comparison_validation": comparison_validation,
            "primary_negative_calibration": primary_negative,
            "primary_positive_calibration": primary_positive,
            "primary_validation": primary_validation,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1020 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for builder labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    validation = summary["validation_aggregate"]
    print(
        "claim={claim} positive_controls={positive} negative_controls={negative} "
        "selected={selected} positives={positives} false={false} precision={precision} "
        "groups={groups} success={success} noisy_windows={noisy} out={out}".format(
            claim=payload["claim_status"],
            positive=summary["positive_calibration_pass"],
            negative=summary["negative_calibration_pass"],
            selected=validation["batch_selected_count"],
            positives=validation["batch_selected_positive_count"],
            false=validation["batch_selected_false_count"],
            precision=validation["batch_precision"],
            groups=validation["context_safe_scalar_valid_group_count"],
            success=",".join(validation["success_windows"]) or "none",
            noisy=",".join(validation["noisy_windows"]) or "none",
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
