#!/usr/bin/env python3
"""P1012 frozen positive-family extraction audit for expanded p231 sources."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1008_p231_expanded_rule_early_stop_11984 as p1008
import low_term_total2_p1009_p231_expanded_rule_family_fallback_11984 as p1009
import low_term_total2_p1010_p231_stress_row_completion_11992 as p1010


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1012_p231_positive_family_extract_12016.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1012_p231_positive_family_extract_12016_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1012_p231_positive_family_extract_12016.v1"
DEFAULT_TARGET = p1010.DEFAULT_TARGET
CALIBRATION_WINDOWS = [p1007.CONTROL_WINDOW, p1007.VALIDATION_WINDOW, p1008.VALIDATION_WINDOW, "12008_12015"]
VALIDATION_WINDOW = "12016_12023"
RULE_NAME = "selector=mode_low_term_support_total5 AND topk=7 AND leaf_tuple=[8, 56, 90]"
RULE_MEMBERS = ["selector=mode_low_term_support_total5", "topk=7", "leaf_tuple=[8, 56, 90]"]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1010.int_value(value, default)


def features(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("features") or {}


def source_case(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_case") or {}


def leaf_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    return p1010.leaf_tuple(row)


def selected_ops(row: dict[str, Any]) -> float:
    return float(source_case(row).get("source_ops_over_rho") or 0.0)


def frozen_rule(row: dict[str, Any]) -> bool:
    return (
        str(features(row).get("leaf_selector")) == "mode_low_term_support_total5"
        and int_value(features(row).get("top_k")) == 7
        and leaf_tuple(row) == (8, 56, 90)
    )


def source_stress_positive(row: dict[str, Any]) -> bool:
    return p1010.source_stress_positive(row)


def selected_case_summary(row: dict[str, Any]) -> dict[str, Any]:
    return p1010.selected_case_summary(row)


def stress_score(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return p1010.stress_score(rows, frozen_rule)


def build_window_rows(windows: list[str], targets: str, min_source_rank: int) -> tuple[dict[str, list[dict[str, Any]]], dict[str, bool]]:
    return p1010.build_window_rows(windows, targets, min_source_rank)


def first_hit(selected: list[dict[str, Any]], groups: list[dict[str, Any]], order: dict[str, Any]) -> dict[str, Any]:
    return p1008.first_hit_summary(selected, groups, order)


def lane_record(name: str, rows: list[dict[str, Any]], baseline_rank: int) -> dict[str, Any]:
    selected = [row for row in rows if frozen_rule(row)]
    analysis, groups = p1005.scalar_valid_groups(
        selected,
        {"lane": name, "rule_family": RULE_NAME, "rule_members": RULE_MEMBERS},
        baseline_rank,
    )
    return {
        "analysis_summary": analysis.get("summary"),
        "groups": groups,
        "metadata": {"lane": name, "rule_family": RULE_NAME, "rule_members": RULE_MEMBERS},
        "scalar_valid_groups": [p1005.compact_group(group) for group in groups[:12]],
        "selected": selected,
        "selected_cases": [selected_case_summary(row) for row in selected[:48]],
        "stress_selection": stress_score(rows),
    }


def score_order(order: dict[str, Any], lanes: list[dict[str, Any]]) -> dict[str, Any]:
    hits = []
    misses = 0
    for lane in lanes:
        if int_value((lane.get("analysis_summary") or {}).get("context_safe_scalar_valid_group_count")) == 0:
            continue
        summary = first_hit(lane["selected"], lane["groups"], order)
        first = summary.get("first_scalar_valid_group")
        if first:
            hits.append(
                {
                    "charged_ops_over_rho": first.get("charged_ops_over_rho"),
                    "lane": lane["metadata"]["lane"],
                    "ordered_index": first.get("ordered_index"),
                }
            )
        else:
            misses += 1
    charges = [float(row["charged_ops_over_rho"]) for row in hits]
    return {
        "below_rho_hit_count": sum(1 for value in charges if value < 1.0),
        "hit_count": len(hits),
        "lane_hits": hits,
        "max_charge": max(charges) if charges else None,
        "mean_charge": round(sum(charges) / len(charges), 8) if charges else None,
        "miss_count": misses,
        "order_description": order["description"],
        "order_name": order["name"],
    }


def choose_order(lanes: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    orders = p1009.public_order_candidates()
    scored = [score_order(order, lanes) for order in orders]
    scored.sort(
        key=lambda row: (
            -int_value(row.get("below_rho_hit_count")),
            -int_value(row.get("hit_count")),
            float(row.get("mean_charge") if row.get("mean_charge") is not None else 10**9),
            float(row.get("max_charge") if row.get("max_charge") is not None else 10**9),
            str(row.get("order_name")),
        )
    )
    by_name = {order["name"]: order for order in orders}
    return by_name[str(scored[0]["order_name"])], scored


def trim_lane(lane: dict[str, Any], order: dict[str, Any]) -> dict[str, Any]:
    return {
        **{key: value for key, value in lane.items() if key not in {"groups", "selected"}},
        "first_hit_chosen_order": first_hit(lane["selected"], lane["groups"], order),
    }


def determine_claim(control_pass: bool, validation_lane: dict[str, Any], validation_first: dict[str, Any]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P1012_POSITIVE_CONTROL_FAILURE"
    summary = validation_lane.get("analysis_summary") or {}
    stress = validation_lane.get("stress_selection") or {}
    if int_value(summary.get("selected_count")) == 0:
        return "NEGATIVE_RESULT_P1012_FROZEN_FAMILY_SELECTS_NO_HOLDOUT_ROWS"
    if int_value(stress.get("selected_stress_positive_count")) == 0:
        return "NEGATIVE_RESULT_P1012_FROZEN_FAMILY_NO_HOLDOUT_STRESS_POSITIVE"
    if int_value(summary.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1012_FROZEN_FAMILY_NO_HOLDOUT_SCALAR_VALID_GROUP"
    first = validation_first.get("first_scalar_valid_group")
    if first and float(first.get("charged_ops_over_rho") or 10**9) < 1.0:
        return "P1012_POSITIVE_FAMILY_TRANSFER_BELOW_RHO"
    if first:
        return "NEGATIVE_RESULT_P1012_POSITIVE_FAMILY_TRANSFER_ABOVE_RHO"
    return "NEGATIVE_RESULT_P1012_POSITIVE_FAMILY_NO_ORDER_HIT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = [*CALIBRATION_WINDOWS, VALIDATION_WINDOW]
    by_window, exists = build_window_rows(windows, args.targets, args.min_source_rank)
    calibration_lanes = [
        lane_record(f"calibration_{window}", by_window[window], args.baseline_rank)
        for window in CALIBRATION_WINDOWS
    ]
    chosen_order, order_scores = choose_order(calibration_lanes)
    calibration_first_hits = [first_hit(lane["selected"], lane["groups"], chosen_order) for lane in calibration_lanes]
    validation_lane = lane_record(f"validation_{VALIDATION_WINDOW}", by_window[VALIDATION_WINDOW], args.baseline_rank)
    validation_first = first_hit(validation_lane["selected"], validation_lane["groups"], chosen_order)
    all_validation_orders = [
        first_hit(validation_lane["selected"], validation_lane["groups"], order)
        for order in [*p1009.public_order_candidates(), *[order for order in p1008.order_candidates() if order.get("diagnostic")]]
    ]
    all_validation_orders.sort(
        key=lambda row: (
            not row.get("first_scalar_valid_group_below_rho"),
            (row.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho", 10**9),
            row.get("order_name"),
        )
    )
    control_pass = any(hit.get("first_scalar_valid_group_below_rho") for hit in calibration_first_hits) and any(
        lane["metadata"]["lane"] == "calibration_12008_12015"
        and int_value((lane.get("analysis_summary") or {}).get("context_safe_scalar_valid_group_count")) > 0
        for lane in calibration_lanes
    )
    claim = determine_claim(control_pass, validation_lane, validation_first)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "validation_source_sha256": p1005.sha256_file(p1007.expanded_source_path(VALIDATION_WINDOW)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1012_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN-FAMILY BOUNDARY: rule is fixed from the public family observed on 12008_12015.",
            "VALIDATION BOUNDARY: validation stress labels and scalar-valid groups are not used for choosing the rule or order.",
            "CONTEXT-SAFE-GATE: groups spanning multiple public fingerprints are rejected.",
            "FULL-ALGORITHM BOUNDARY: this is not relation collection, sparse linear algebra, target descent, or cryptographic-size evidence.",
        ],
        "method": "p1012_p231_positive_family_extract_12016",
        "order_search": {
            "chosen_order": {
                "description": chosen_order["description"],
                "name": chosen_order["name"],
            },
            "training_scores": order_scores,
        },
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "calibration_windows": CALIBRATION_WINDOWS,
            "frozen_rule": RULE_NAME,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "validation_window": VALIDATION_WINDOW,
        },
        "rule": {
            "description": "leaf_selector == mode_low_term_support_total5 and top_k == 7 and unique_leaf_indices == [8, 56, 90]",
            "members": RULE_MEMBERS,
            "name": RULE_NAME,
        },
        "schema": SCHEMA,
        "source": {
            "calibration": {window: p1007.source_summary(window) for window in CALIBRATION_WINDOWS},
            "exists": exists,
            "validation": p1007.source_summary(VALIDATION_WINDOW),
        },
        "summary": {
            "calibration_below_rho_first_hit_count": sum(1 for hit in calibration_first_hits if hit.get("first_scalar_valid_group_below_rho")),
            "calibration_context_safe_scalar_valid_group_count": sum(
                int_value((lane.get("analysis_summary") or {}).get("context_safe_scalar_valid_group_count"))
                for lane in calibration_lanes
            ),
            "chosen_order_name": chosen_order["name"],
            "claim_status": claim,
            "control_pass": control_pass,
            "extraction_window_scalar_valid_groups": next(
                int_value((lane.get("analysis_summary") or {}).get("context_safe_scalar_valid_group_count"))
                for lane in calibration_lanes
                if lane["metadata"]["lane"] == "calibration_12008_12015"
            ),
            "validation_best_scalar_valid_amortized_ops_over_rho": (
                (validation_lane.get("analysis_summary") or {}).get("scalar_valid_best_amortized_ops_over_rho")
            ),
            "validation_chosen_first_charge": (validation_first.get("first_scalar_valid_group") or {}).get(
                "charged_ops_over_rho"
            ),
            "validation_context_safe_scalar_valid_group_count": (
                (validation_lane.get("analysis_summary") or {}).get("context_safe_scalar_valid_group_count")
            ),
            "validation_selected_count": (validation_lane.get("analysis_summary") or {}).get("selected_count"),
            "validation_selected_stress_positive_count": validation_lane["stress_selection"].get(
                "selected_stress_positive_count"
            ),
            "validation_total_selected_ops_over_rho": (validation_lane.get("analysis_summary") or {}).get(
                "selected_direct_sum_ops_over_rho"
            ),
        },
        "lanes": {
            "calibration": [trim_lane(lane, chosen_order) for lane in calibration_lanes],
            "validation": {
                **trim_lane(validation_lane, chosen_order),
                "all_order_diagnostic": all_validation_orders,
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1012 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for source-positive labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} order={order} control_pass={control_pass} validation_selected={validation_selected} "
        "validation_stress={validation_stress} validation_groups={validation_groups} "
        "validation_first={validation_first} out={out}".format(
            claim=payload["claim_status"],
            order=summary["chosen_order_name"],
            control_pass=summary["control_pass"],
            validation_selected=summary["validation_selected_count"],
            validation_stress=summary["validation_selected_stress_positive_count"],
            validation_groups=summary["validation_context_safe_scalar_valid_group_count"],
            validation_first=summary["validation_chosen_first_charge"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
