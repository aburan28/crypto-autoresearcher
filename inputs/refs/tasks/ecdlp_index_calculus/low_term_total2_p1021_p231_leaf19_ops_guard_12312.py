#!/usr/bin/env python3
"""P1021 validation for the frozen leaf-19 salt-gap plus source-ops guard."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1010_p231_stress_row_completion_11992 as p1010
import low_term_total2_p1020_p231_leaf19_saltgap_precision_12256 as p1020


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1021_p231_leaf19_ops_guard_12312.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1021_p231_leaf19_ops_guard_12312_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1021_p231_leaf19_ops_guard_12312.v1"
DEFAULT_TARGET = p1010.DEFAULT_TARGET
POSITIVE_CALIBRATION_WINDOWS = ["12184_12191", "12192_12199", "12216_12223", "12272_12279", "12304_12311"]
NEGATIVE_CALIBRATION_WINDOWS = ["12224_12231", "12264_12271"]
VALIDATION_WINDOWS = [
    "12312_12319",
    "12320_12327",
    "12328_12335",
    "12336_12343",
    "12344_12351",
    "12352_12359",
    "12360_12367",
    "12368_12375",
]
PRIMARY_RULE_NAME = "topk4_anchor_leaf19_hybrid_saltgap_ge3_ops_ge_0p7"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1010.int_value(value, default)


def selected_count(lane: dict[str, Any]) -> int:
    return int_value((lane.get("stress_selection") or {}).get("selected_count"))


def determine_claim(
    positive_controls_pass: bool,
    negative_controls_pass: bool,
    validation_summary: dict[str, Any],
) -> str:
    if not positive_controls_pass:
        return "NEGATIVE_RESULT_P1021_POSITIVE_CONTROL_FAILURE"
    if not negative_controls_pass:
        return "NEGATIVE_RESULT_P1021_NEGATIVE_CONTROL_FAILURE"
    if validation_summary["success_windows"] and int_value(validation_summary.get("batch_selected_false_count")) == 0:
        return "P1021_LEAF19_OPS_GUARD_VALIDATION_HIT_CLEAN"
    if validation_summary["success_windows"]:
        return "P1021_LEAF19_OPS_GUARD_VALIDATION_HIT_WITH_NOISE"
    if int_value(validation_summary.get("batch_selected_count")) == 0:
        return "NEGATIVE_RESULT_P1021_VALIDATION_SELECTS_NO_ROWS"
    if int_value(validation_summary.get("batch_selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P1021_VALIDATION_NO_BUILDER_VISIBLE_POSITIVES"
    if int_value(validation_summary.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1021_VALIDATION_NO_CONTEXT_SAFE_SCALAR_GROUP"
    return "NEGATIVE_RESULT_P1021_VALIDATION_FIRST_HIT_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    order = p1020.fixed_order()
    all_windows = [
        *POSITIVE_CALIBRATION_WINDOWS,
        *NEGATIVE_CALIBRATION_WINDOWS,
        *VALIDATION_WINDOWS,
    ]
    by_window, exists = p1010.build_window_rows(all_windows, args.targets, args.min_source_rank)
    rules = p1020.rule_catalog()
    primary_rule = next(rule for rule in rules if rule["name"] == PRIMARY_RULE_NAME)
    comparison_rules = [rule for rule in rules if rule["name"] in {p1020.BASE_RULE_NAME, p1020.PRIMARY_RULE_NAME, PRIMARY_RULE_NAME}]
    primary_positive = p1020.evaluate_rule(
        POSITIVE_CALIBRATION_WINDOWS,
        by_window,
        primary_rule,
        order,
        args.baseline_rank,
        "positive_calibration",
    )
    primary_negative = p1020.evaluate_rule(
        NEGATIVE_CALIBRATION_WINDOWS,
        by_window,
        primary_rule,
        order,
        args.baseline_rank,
        "negative_calibration",
    )
    primary_validation = p1020.evaluate_rule(
        VALIDATION_WINDOWS,
        by_window,
        primary_rule,
        order,
        args.baseline_rank,
        "validation",
    )
    comparison_validation = {
        rule["name"]: p1020.evaluate_rule(
            VALIDATION_WINDOWS,
            by_window,
            rule,
            order,
            args.baseline_rank,
            "comparison",
        )
        for rule in comparison_rules
    }
    positive_summary = p1020.aggregate(primary_positive)
    negative_summary = p1020.aggregate(primary_negative)
    validation_summary = p1020.aggregate(primary_validation)
    comparison_summaries = {name: p1020.aggregate(lanes) for name, lanes in comparison_validation.items()}
    positive_controls_pass = all(p1020.lane_success(lane) for lane in primary_positive.values()) and int_value(
        positive_summary.get("batch_selected_false_count")
    ) == 0
    negative_controls_pass = all(selected_count(lane) == 0 for lane in primary_negative.values())
    claim = determine_claim(positive_controls_pass, negative_controls_pass, validation_summary)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "p1020_dependency_sha256": p1005.sha256_file(Path(p1020.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": {window: p1005.sha256_file(p1007.expanded_source_path(window)) for window in all_windows},
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1021_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "FROZEN-RULE BOUNDARY: the source-ops guard is inherited from P1020 diagnostics and fixed before 12312_12375 validation.",
            "VALIDATION BOUNDARY: 12312_12375 windows are the fresh validation batch.",
            "CONTEXT-SAFE-GATE: scalar-valid groups spanning multiple public fingerprints are rejected.",
            "INDEX-CALCULUS BOUNDARY: this is relation-surface prediction, not sparse linear algebra, target descent, or cryptographic-size evidence.",
        ],
        "method": "p1021_p231_leaf19_ops_guard_12312",
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "fresh_validation_windows": VALIDATION_WINDOWS,
            "frozen_order": {"description": order["description"], "name": order["name"]},
            "min_source_rank": args.min_source_rank,
            "negative_calibration_windows": NEGATIVE_CALIBRATION_WINDOWS,
            "positive_calibration_windows": POSITIVE_CALIBRATION_WINDOWS,
            "primary_rule": PRIMARY_RULE_NAME,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "rules": [
            {
                "claim_role": rule["claim_role"],
                "description": rule["description"],
                "name": rule["name"],
            }
            for rule in comparison_rules
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
                window: p1020.compact_lane_summary(lane) for window, lane in primary_negative.items()
            },
            "negative_calibration_summary": negative_summary,
            "positive_calibration_pass": positive_controls_pass,
            "positive_calibration_primary": {
                window: p1020.compact_lane_summary(lane) for window, lane in primary_positive.items()
            },
            "positive_calibration_summary": positive_summary,
            "validation_aggregate": validation_summary,
            "validation_primary": {
                window: p1020.compact_lane_summary(lane) for window, lane in primary_validation.items()
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
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1021 contract path")
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
