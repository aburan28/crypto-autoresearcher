#!/usr/bin/env python3
"""P1019 validation for the unbounded leaf-19 companion scheduler."""

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
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1019_p231_leaf19_companion_unbounded_12216.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1019_p231_leaf19_companion_unbounded_12216_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1019_p231_leaf19_companion_unbounded_12216.v1"
DEFAULT_TARGET = p1010.DEFAULT_TARGET
CONTROL_WINDOWS = ["12184_12191", "12192_12199"]
VALIDATION_WINDOWS = ["12216_12223", "12224_12231", "12232_12239", "12240_12247", "12248_12255"]
ORDER_NAME = "salt_gap_asc_ops"
RULE_NAME = p1018.CONTROL_RULE_NAME

Predicate = Callable[[dict[str, Any]], bool]


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


def scheduler_predicate_for(rows: list[dict[str, Any]]) -> Predicate:
    keys = p1017.companion_keys(rows)
    return lambda row, keys=keys: p1017.row_key_set(row) in keys and p1018.leaf19_hybrid(row)


def candidate(predicate: Predicate) -> dict[str, Any]:
    return {
        "candidate": {
            "description": "exact anchor row-key set, mode_cost_hybrid_support_monic_b_total2, top_k 4, leaf tuple [19]",
            "member_count": 1,
            "members": [RULE_NAME],
            "name": RULE_NAME,
        },
        "predicate": predicate,
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
            "rule_family": RULE_NAME,
            "rule_members": [RULE_NAME],
        },
        baseline_rank,
    )
    fixed_first = p1008.first_hit_summary(selected, groups, order)
    return {
        "analysis_summary": analysis.get("summary"),
        "fixed_order_first_hit": fixed_first,
        "groups": [p1005.compact_group(group) for group in groups[:12]],
        "selected_cases": [
            p1015.selected_case_summary(row)
            | {"max_salt": p1018.max_salt(row), "salt_values": p1018.salt_values(row)}
            for row in selected[:64]
        ],
        "stress_selection": p1015.stress_score(rows, predicate),
    }


def lane_success(lane: dict[str, Any]) -> bool:
    return p1015.lane_success(lane)


def compact_lane_summary(lane: dict[str, Any]) -> dict[str, Any]:
    return p1015.compact_lane_summary(lane)


def aggregate(lanes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    selected = 0
    positives = 0
    groups = 0
    ops = 0.0
    selected_windows: list[str] = []
    false_positive_windows: list[str] = []
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
        if selected_count and not positive_count:
            false_positive_windows.append(window)
        if lane_success(lane):
            success_windows.append(window)
    return {
        "batch_precision": p1007.safe_ratio(positives, selected),
        "batch_selected_count": selected,
        "batch_selected_ops_over_rho": round(ops, 8),
        "batch_selected_positive_count": positives,
        "context_safe_scalar_valid_group_count": groups,
        "false_positive_windows": false_positive_windows,
        "selected_windows": selected_windows,
        "success_windows": success_windows,
    }


def determine_claim(controls_pass: bool, validation_summary: dict[str, Any]) -> str:
    if not controls_pass:
        return "NEGATIVE_RESULT_P1019_CONTROL_REPRODUCTION_FAILURE"
    if validation_summary["success_windows"] and not validation_summary["false_positive_windows"]:
        return "P1019_LEAF19_COMPANION_VALIDATION_HIT_CLEAN"
    if validation_summary["success_windows"]:
        return "P1019_LEAF19_COMPANION_VALIDATION_HIT_WITH_NOISE"
    if int_value(validation_summary.get("batch_selected_count")) == 0:
        return "NEGATIVE_RESULT_P1019_VALIDATION_SELECTS_NO_ROWS"
    if int_value(validation_summary.get("batch_selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P1019_VALIDATION_NO_BUILDER_VISIBLE_POSITIVES"
    if int_value(validation_summary.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1019_VALIDATION_NO_CONTEXT_SAFE_SCALAR_GROUP"
    return "NEGATIVE_RESULT_P1019_VALIDATION_FIRST_HIT_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    order = fixed_order()
    windows = [*CONTROL_WINDOWS, *VALIDATION_WINDOWS]
    by_window, exists = p1010.build_window_rows(windows, args.targets, args.min_source_rank)
    controls = {
        window: lane_full(
            f"control_{window}",
            by_window[window],
            candidate(scheduler_predicate_for(by_window[window])),
            order,
            args.baseline_rank,
        )
        for window in CONTROL_WINDOWS
    }
    validation = {
        window: lane_full(
            f"validation_{window}",
            by_window[window],
            candidate(scheduler_predicate_for(by_window[window])),
            order,
            args.baseline_rank,
        )
        for window in VALIDATION_WINDOWS
    }
    validation_summary = aggregate(validation)
    controls_pass = all(lane_success(lane) for lane in controls.values())
    claim = determine_claim(controls_pass, validation_summary)
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
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1019_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "FROZEN-RULE BOUNDARY: scheduler is inherited from P1018 unbounded control, not fit on P1019 validation labels.",
            "VALIDATION BOUNDARY: 12216_12255 windows are the validation batch.",
            "CONTEXT-SAFE-GATE: scalar-valid groups spanning multiple public fingerprints are rejected.",
            "INDEX-CALCULUS BOUNDARY: this is relation-surface prediction, not sparse linear algebra, target descent, or cryptographic-size evidence.",
        ],
        "method": "p1019_p231_leaf19_companion_unbounded_12216",
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "control_windows": CONTROL_WINDOWS,
            "frozen_order": {"description": order["description"], "name": order["name"]},
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "validation_windows": VALIDATION_WINDOWS,
        },
        "rule": candidate(lambda _row: False)["candidate"],
        "schema": SCHEMA,
        "source": {
            "exists": exists,
            "summaries": {window: p1007.source_summary(window) for window in windows},
        },
        "summary": {
            "claim_status": claim,
            "control_pass": controls_pass,
            "controls": {window: compact_lane_summary(lane) for window, lane in controls.items()},
            "validation_aggregate": validation_summary,
            "validation_windows": {window: compact_lane_summary(lane) for window, lane in validation.items()},
        },
        "lanes": {
            "controls": controls,
            "validation": validation,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1019 contract path")
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
        "claim={claim} control_pass={control_pass} selected={selected} positives={positives} "
        "precision={precision} groups={groups} success={success} false_positive_windows={false_pos} out={out}".format(
            claim=payload["claim_status"],
            control_pass=summary["control_pass"],
            selected=validation["batch_selected_count"],
            positives=validation["batch_selected_positive_count"],
            precision=validation["batch_precision"],
            groups=validation["context_safe_scalar_valid_group_count"],
            success=",".join(validation["success_windows"]) or "none",
            false_pos=",".join(validation["false_positive_windows"]) or "none",
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
