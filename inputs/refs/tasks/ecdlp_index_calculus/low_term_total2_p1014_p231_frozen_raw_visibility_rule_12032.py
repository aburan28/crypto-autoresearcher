#!/usr/bin/env python3
"""P1014 frozen validation for the P1013 raw-source visibility rule."""

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
import low_term_total2_p1013_p231_raw_source_visibility_rescue_12024 as p1013


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1014_p231_frozen_raw_visibility_rule_12032.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1014_p231_frozen_raw_visibility_rule_12032_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1014_p231_frozen_raw_visibility_rule_12032.v1"
DEFAULT_TARGET = p1010.DEFAULT_TARGET
CONTROL_WINDOW = "12024_12031"
PRIMARY_WINDOW = "12032_12039"
SWEEP_WINDOWS = ["12040_12047", "12048_12055"]
ORDER_NAME = "ops_asc_transfer"
RULE_NAME = p1013.RULE_NAME
NEGATIVE_CONTROL_NAME = p1013.NEGATIVE_CONTROL_NAME

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


def builder_score(rows: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    return p1013.builder_score(rows, predicate)


def selected_cases(rows: list[dict[str, Any]], predicate: Predicate, limit: int = 32) -> list[dict[str, Any]]:
    return [p1010.selected_case_summary(row) for row in rows if predicate(row)][:limit]


def all_order_diagnostics(selected: list[dict[str, Any]], groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    orders = [
        *p1009.public_order_candidates(),
        *[order for order in p1008.order_candidates() if order.get("diagnostic")],
    ]
    rows = [p1008.first_hit_summary(selected, groups, order) for order in orders]
    rows.sort(
        key=lambda row: (
            not row.get("first_scalar_valid_group_below_rho"),
            (row.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho", 10**9),
            row.get("order_name"),
        )
    )
    return rows


def lane_record(
    name: str,
    rows: list[dict[str, Any]],
    predicate: Predicate,
    order: dict[str, Any],
    baseline_rank: int,
    include_diagnostics: bool,
) -> dict[str, Any]:
    selected = [row for row in rows if predicate(row)]
    analysis, groups = p1005.scalar_valid_groups(
        selected,
        {
            "frozen_order": ORDER_NAME,
            "lane": name,
            "rule_family": RULE_NAME if "negative" not in name else NEGATIVE_CONTROL_NAME,
        },
        baseline_rank,
    )
    fixed_first = p1008.first_hit_summary(selected, groups, order)
    out = {
        "analysis_summary": analysis.get("summary"),
        "fixed_order_first_hit": fixed_first,
        "groups": [p1005.compact_group(group) for group in groups[:12]],
        "selected_cases": selected_cases(rows, predicate),
        "stress_selection": builder_score(rows, predicate),
    }
    if include_diagnostics:
        out["all_order_diagnostic"] = all_order_diagnostics(selected, groups)
    return out


def lane_success(lane: dict[str, Any]) -> bool:
    stress = lane.get("stress_selection") or {}
    analysis = lane.get("analysis_summary") or {}
    first = (lane.get("fixed_order_first_hit") or {}).get("first_scalar_valid_group") or {}
    return (
        int_value(stress.get("selected_positive_count")) > 0
        and int_value(analysis.get("context_safe_scalar_valid_group_count")) > 0
        and bool((lane.get("fixed_order_first_hit") or {}).get("first_scalar_valid_group_below_rho"))
        and float(first.get("charged_ops_over_rho") or 10**9) < 1.0
    )


def determine_claim(control_pass: bool, primary_lane: dict[str, Any], sweep_lanes: dict[str, dict[str, Any]]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P1014_CONTROL_REPRODUCTION_FAILURE"
    if lane_success(primary_lane):
        return "P1014_FROZEN_RULE_PRIMARY_BELOW_RHO"
    if any(lane_success(lane) for lane in sweep_lanes.values()):
        return "NEGATIVE_RESULT_P1014_PRIMARY_MISS_WITH_LATER_REAPPEARANCE"
    stress = primary_lane.get("stress_selection") or {}
    analysis = primary_lane.get("analysis_summary") or {}
    if int_value(stress.get("selected_count")) == 0:
        return "NEGATIVE_RESULT_P1014_PRIMARY_SELECTS_NO_ROWS"
    if int_value(stress.get("selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P1014_PRIMARY_NO_BUILDER_VISIBLE_POSITIVES"
    if int_value(analysis.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1014_PRIMARY_NO_CONTEXT_SAFE_SCALAR_GROUP"
    return "NEGATIVE_RESULT_P1014_PRIMARY_FIRST_HIT_ABOVE_RHO"


def compact_lane_summary(lane: dict[str, Any]) -> dict[str, Any]:
    stress = lane.get("stress_selection") or {}
    analysis = lane.get("analysis_summary") or {}
    first = (lane.get("fixed_order_first_hit") or {}).get("first_scalar_valid_group") or {}
    return {
        "best_amortized_ops_over_rho": analysis.get("scalar_valid_best_amortized_ops_over_rho"),
        "context_safe_scalar_valid_group_count": analysis.get("context_safe_scalar_valid_group_count"),
        "fixed_first_below_rho": (lane.get("fixed_order_first_hit") or {}).get("first_scalar_valid_group_below_rho"),
        "fixed_first_charge": first.get("charged_ops_over_rho"),
        "fixed_first_secret": first.get("derived_secret"),
        "precision": stress.get("precision"),
        "recall": stress.get("recall"),
        "selected_count": stress.get("selected_count"),
        "selected_positive_count": stress.get("selected_positive_count"),
        "total_selected_ops_over_rho": stress.get("selected_direct_sum_ops_over_rho"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    order = fixed_order()
    windows = [CONTROL_WINDOW, PRIMARY_WINDOW, *SWEEP_WINDOWS]
    by_window, exists = p1010.build_window_rows(windows, args.targets, args.min_source_rank)
    control_lane = lane_record(
        f"control_{CONTROL_WINDOW}",
        by_window[CONTROL_WINDOW],
        p1013.builder_rule,
        order,
        args.baseline_rank,
        include_diagnostics=False,
    )
    primary_lane = lane_record(
        f"primary_{PRIMARY_WINDOW}",
        by_window[PRIMARY_WINDOW],
        p1013.builder_rule,
        order,
        args.baseline_rank,
        include_diagnostics=True,
    )
    sweep_lanes = {
        window: lane_record(
            f"sweep_{window}",
            by_window[window],
            p1013.builder_rule,
            order,
            args.baseline_rank,
            include_diagnostics=True,
        )
        for window in SWEEP_WINDOWS
    }
    negative_lanes = {
        window: lane_record(
            f"negative_control_{window}",
            by_window[window],
            p1013.negative_control_rule,
            order,
            args.baseline_rank,
            include_diagnostics=False,
        )
        for window in [PRIMARY_WINDOW, *SWEEP_WINDOWS]
    }
    control_pass = lane_success(control_lane)
    claim = determine_claim(control_pass, primary_lane, sweep_lanes)
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
        "claim_taxonomy": "OBSERVATION" if claim == "P1014_FROZEN_RULE_PRIMARY_BELOW_RHO" else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "FROZEN-RULE BOUNDARY: the selector and order are inherited from P1013 and not fit on validation labels.",
            "PRIMARY-VALIDATION BOUNDARY: 12032_12039 is the primary claim window; later positives are stress-sweep reappearance evidence.",
            "CONTEXT-SAFE-GATE: scalar-valid groups spanning multiple public fingerprints are rejected.",
            "INDEX-CALCULUS BOUNDARY: this is relation-surface prediction, not relation collection, sparse linear algebra, target descent, or cryptographic-size evidence.",
        ],
        "method": "p1014_p231_frozen_raw_visibility_rule_12032",
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "control_window": CONTROL_WINDOW,
            "frozen_order": {"description": order["description"], "name": order["name"]},
            "min_source_rank": args.min_source_rank,
            "primary_window": PRIMARY_WINDOW,
            "sweep_windows": SWEEP_WINDOWS,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "raw_source": {window: p1013.raw_summary(window) for window in windows},
        "rule": {
            "description": "transfer_index % 8 == 2 and top_k == 12 and selected leaves contain 90 and selector total suffix >= 2",
            "name": RULE_NAME,
            "negative_control": {
                "description": "same transfer/top-k/two-row shape without leaf 90",
                "name": NEGATIVE_CONTROL_NAME,
            },
        },
        "schema": SCHEMA,
        "source": {
            "exists": exists,
            "summaries": {window: p1007.source_summary(window) for window in windows},
        },
        "summary": {
            "claim_status": claim,
            "control_pass": control_pass,
            "control": compact_lane_summary(control_lane),
            "negative_controls": {window: compact_lane_summary(lane) for window, lane in negative_lanes.items()},
            "primary": compact_lane_summary(primary_lane),
            "primary_success": lane_success(primary_lane),
            "sweep": {window: compact_lane_summary(lane) for window, lane in sweep_lanes.items()},
            "sweep_success_windows": [window for window, lane in sweep_lanes.items() if lane_success(lane)],
        },
        "lanes": {
            "control": control_lane,
            "negative_controls": negative_lanes,
            "primary": primary_lane,
            "sweep": sweep_lanes,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1014 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for builder labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    primary = summary["primary"]
    print(
        "claim={claim} control_pass={control_pass} primary_selected={primary_selected} "
        "primary_pos={primary_pos} primary_groups={primary_groups} primary_first={primary_first} "
        "sweep_success={sweep_success} out={out}".format(
            claim=payload["claim_status"],
            control_pass=summary["control_pass"],
            primary_selected=primary["selected_count"],
            primary_pos=primary["selected_positive_count"],
            primary_groups=primary["context_safe_scalar_valid_group_count"],
            primary_first=primary["fixed_first_charge"],
            sweep_success=",".join(summary["sweep_success_windows"]) or "none",
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
