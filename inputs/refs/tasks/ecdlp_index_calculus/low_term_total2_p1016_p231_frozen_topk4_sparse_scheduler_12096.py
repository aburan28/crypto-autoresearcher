#!/usr/bin/env python3
"""P1016 frozen opportunistic validation for the P1015 top-k4 surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1009_p231_expanded_rule_family_fallback_11984 as p1009
import low_term_total2_p1010_p231_stress_row_completion_11992 as p1010
import low_term_total2_p1015_p231_cross_window_public_invariant_12056 as p1015


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1016_p231_frozen_topk4_sparse_scheduler_12096.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1016_p231_frozen_topk4_sparse_scheduler_12096_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1016_p231_frozen_topk4_sparse_scheduler_12096.v1"
DEFAULT_TARGET = p1010.DEFAULT_TARGET
CONTROL_WINDOW = "12064_12071"
VALIDATION_WINDOWS = ["12096_12103", "12104_12111", "12112_12119", "12120_12127", "12128_12135"]
ORDER_NAME = "salt_gap_asc_ops"
RULE_NAME = "topk=4 AND selector=mode_cost_low_term_support_total2"


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


def frozen_rule(row: dict[str, Any]) -> bool:
    return p1015.top_k(row) == 4 and p1015.selector(row) == "mode_cost_low_term_support_total2"


def candidate() -> dict[str, Any]:
    return {
        "candidate": {
            "description": "top_k == 4 AND leaf_selector == mode_cost_low_term_support_total2",
            "member_count": 2,
            "members": ["topk=4", "selector=mode_cost_low_term_support_total2"],
            "name": RULE_NAME,
        },
        "predicate": frozen_rule,
    }


def lane_success(lane: dict[str, Any]) -> bool:
    return p1015.lane_success(lane)


def compact_lane_summary(lane: dict[str, Any]) -> dict[str, Any]:
    return p1015.compact_lane_summary(lane)


def aggregate(lanes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    selected = 0
    positives = 0
    groups = 0
    selected_ops = 0.0
    success_windows = []
    false_positive_windows = []
    selected_windows = []
    for window, lane in lanes.items():
        stress = lane.get("stress_selection") or {}
        analysis = lane.get("analysis_summary") or {}
        selected_count = int_value(stress.get("selected_count"))
        positive_count = int_value(stress.get("selected_positive_count"))
        selected += selected_count
        positives += positive_count
        groups += int_value(analysis.get("context_safe_scalar_valid_group_count"))
        selected_ops += float(stress.get("selected_direct_sum_ops_over_rho") or 0.0)
        if selected_count:
            selected_windows.append(window)
        if selected_count and not positive_count:
            false_positive_windows.append(window)
        if lane_success(lane):
            success_windows.append(window)
    return {
        "batch_precision": p1007.safe_ratio(positives, selected),
        "batch_selected_count": selected,
        "batch_selected_ops_over_rho": round(selected_ops, 8),
        "batch_selected_positive_count": positives,
        "context_safe_scalar_valid_group_count": groups,
        "false_positive_windows": false_positive_windows,
        "selected_windows": selected_windows,
        "success_windows": success_windows,
    }


def determine_claim(control_pass: bool, validation_summary: dict[str, Any]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P1016_CONTROL_REPRODUCTION_FAILURE"
    if validation_summary["success_windows"] and not validation_summary["false_positive_windows"]:
        return "P1016_FROZEN_TOPK4_SPARSE_BATCH_HIT_CLEAN"
    if validation_summary["success_windows"]:
        return "P1016_FROZEN_TOPK4_SPARSE_BATCH_HIT_WITH_NOISE"
    if int_value(validation_summary.get("batch_selected_count")) == 0:
        return "NEGATIVE_RESULT_P1016_BATCH_SELECTS_NO_ROWS"
    if int_value(validation_summary.get("batch_selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P1016_BATCH_NO_BUILDER_VISIBLE_POSITIVES"
    if int_value(validation_summary.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1016_BATCH_NO_CONTEXT_SAFE_SCALAR_GROUP"
    return "NEGATIVE_RESULT_P1016_BATCH_FIRST_HIT_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    order = fixed_order()
    rule = candidate()
    windows = [CONTROL_WINDOW, *VALIDATION_WINDOWS]
    by_window, exists = p1010.build_window_rows(windows, args.targets, args.min_source_rank)
    control_lane = p1015.lane_full(
        f"control_{CONTROL_WINDOW}",
        by_window[CONTROL_WINDOW],
        rule,
        order,
        args.baseline_rank,
    )
    validation_lanes = {
        window: p1015.lane_full(
            f"validation_{window}",
            by_window[window],
            rule,
            order,
            args.baseline_rank,
        )
        for window in VALIDATION_WINDOWS
    }
    validation_summary = aggregate(validation_lanes)
    control_pass = lane_success(control_lane)
    claim = determine_claim(control_pass, validation_summary)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": {window: p1005.sha256_file(p1007.expanded_source_path(window)) for window in windows},
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1016_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "FROZEN-RULE BOUNDARY: predicate and order are inherited from P1015 and not fit on validation labels.",
            "SPARSE-SCHEDULER BOUNDARY: abstentions are allowed, but false-positive windows and total selected cost are reported.",
            "CONTEXT-SAFE-GATE: scalar-valid groups spanning multiple public fingerprints are rejected.",
            "INDEX-CALCULUS BOUNDARY: this is relation-surface prediction, not sparse linear algebra, target descent, or cryptographic-size evidence.",
        ],
        "method": "p1016_p231_frozen_topk4_sparse_scheduler_12096",
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "control_window": CONTROL_WINDOW,
            "frozen_order": {"description": order["description"], "name": order["name"]},
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "validation_windows": VALIDATION_WINDOWS,
        },
        "rule": rule["candidate"],
        "schema": SCHEMA,
        "source": {
            "exists": exists,
            "summaries": {window: p1007.source_summary(window) for window in windows},
        },
        "summary": {
            "claim_status": claim,
            "control": compact_lane_summary(control_lane),
            "control_pass": control_pass,
            "validation_aggregate": validation_summary,
            "validation_windows": {window: compact_lane_summary(lane) for window, lane in validation_lanes.items()},
        },
        "lanes": {
            "control": control_lane,
            "validation": validation_lanes,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1016 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for builder labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    aggregate_summary = summary["validation_aggregate"]
    print(
        "claim={claim} control_pass={control_pass} selected={selected} positives={positives} "
        "precision={precision} success={success} false_positive_windows={false_pos} out={out}".format(
            claim=payload["claim_status"],
            control_pass=summary["control_pass"],
            selected=aggregate_summary["batch_selected_count"],
            positives=aggregate_summary["batch_selected_positive_count"],
            precision=aggregate_summary["batch_precision"],
            success=",".join(aggregate_summary["success_windows"]) or "none",
            false_pos=",".join(aggregate_summary["false_positive_windows"]) or "none",
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
