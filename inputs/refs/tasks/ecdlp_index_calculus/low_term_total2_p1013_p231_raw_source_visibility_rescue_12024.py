#!/usr/bin/env python3
"""P1013 raw-source visibility rescue audit for expanded p231 sources."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1008_p231_expanded_rule_early_stop_11984 as p1008
import low_term_total2_p1009_p231_expanded_rule_family_fallback_11984 as p1009
import low_term_total2_p1010_p231_stress_row_completion_11992 as p1010


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1013_p231_raw_source_visibility_rescue_12024.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1013_p231_raw_source_visibility_rescue_12024_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1013_p231_raw_source_visibility_rescue_12024.v1"
DEFAULT_TARGET = p1010.DEFAULT_TARGET
DISCOVERY_WINDOW = "12016_12023"
DIAGNOSTIC_WINDOW = "12024_12031"
RAW_POLICY = "fixed_target_cap2_ow0_hw3_lw0_sw0_cw0_aw1"
RULE_NAME = "raw_source_offset2_topk12_leaf90_rows_ge2"
NEGATIVE_CONTROL_NAME = "offset2_topk12_rows_ge2_without_leaf90"

Predicate = Callable[[dict[str, Any]], bool]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def int_value(value: Any, default: int = 0) -> int:
    return p1010.int_value(value, default)


def safe_ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    return p1007.safe_ratio(numerator, denominator)


def features(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("features") or {}


def source_case(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_case") or {}


def source_ops(row: dict[str, Any]) -> float:
    return float(source_case(row).get("source_ops_over_rho") or 0.0)


def leaf_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in features(row).get("unique_leaf_indices") or [])


def selector(row: dict[str, Any]) -> str:
    return str(features(row).get("leaf_selector"))


def transfer_index(row: dict[str, Any]) -> int:
    return int_value(source_case(row).get("transfer_index"))


def transfer_offset(row: dict[str, Any]) -> int:
    return transfer_index(row) % 8


def total_suffix(value: str) -> int:
    match = re.search(r"total(\d+)$", value)
    return int(match.group(1)) if match else 0


def builder_rule(row: dict[str, Any]) -> bool:
    return (
        transfer_offset(row) == 2
        and int_value(features(row).get("top_k")) == 12
        and 90 in set(leaf_tuple(row))
        and total_suffix(selector(row)) >= 2
    )


def negative_control_rule(row: dict[str, Any]) -> bool:
    return (
        transfer_offset(row) == 2
        and int_value(features(row).get("top_k")) == 12
        and 90 not in set(leaf_tuple(row))
        and total_suffix(selector(row)) >= 2
    )


def raw_stress_rows(window: str) -> list[dict[str, Any]]:
    payload = load_json(p1007.expanded_source_path(window))
    policy = ((payload.get("policies") or {}).get(RAW_POLICY)) or {}
    return list(policy.get("stress_leaf_results") or [])


def raw_leaf_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    leaves: set[int] = set()
    for item in row.get("row_leaf_keys") or []:
        leaves.update(int_value(value) for value in item.get("leaf_indices") or [])
    return tuple(sorted(leaves))


def raw_transfer_offset(row: dict[str, Any]) -> int:
    return int_value(row.get("transfer_index")) % 8


def raw_rule(row: dict[str, Any]) -> bool:
    return (
        raw_transfer_offset(row) == 2
        and int_value(row.get("top_k")) == 12
        and 90 in set(raw_leaf_tuple(row))
        and int_value(row.get("selected_row_count")) >= 2
    )


def raw_negative_control_rule(row: dict[str, Any]) -> bool:
    return (
        raw_transfer_offset(row) == 2
        and int_value(row.get("top_k")) == 12
        and 90 not in set(raw_leaf_tuple(row))
        and int_value(row.get("selected_row_count")) >= 2
    )


def raw_source_replay_positive(row: dict[str, Any]) -> bool:
    return bool(row.get("source_verified")) and bool(row.get("below_rho"))


def raw_public_positive(row: dict[str, Any]) -> bool:
    return bool(row.get("public_key_verified")) and bool(row.get("below_rho"))


def raw_compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "below_rho": row.get("below_rho"),
        "leaf_tuple": raw_leaf_tuple(row),
        "ops_over_rho": row.get("ops_over_rho"),
        "public_key_verified": row.get("public_key_verified"),
        "rank": row.get("rank"),
        "relation_count": row.get("relation_count"),
        "row_keys": row.get("row_keys"),
        "row_leaf_keys": row.get("row_leaf_keys"),
        "row_selector_public_key_verified": row.get("row_selector_public_key_verified"),
        "selected_row_count": row.get("selected_row_count"),
        "selector": row.get("selector"),
        "source_verified": row.get("source_verified"),
        "top_k": row.get("top_k"),
        "transfer_index": row.get("transfer_index"),
        "transfer_offset": raw_transfer_offset(row),
    }


def flag_counts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[bool, bool, bool, bool]] = Counter()
    for row in rows:
        counts[
            (
                bool(row.get("source_verified")),
                bool(row.get("below_rho")),
                bool(row.get("public_key_verified")),
                bool(row.get("row_selector_public_key_verified")),
            )
        ] += 1
    return [
        {
            "below_rho": below_rho,
            "count": count,
            "public_key_verified": public_key_verified,
            "row_selector_public_key_verified": row_selector_public_key_verified,
            "source_verified": source_verified,
        }
        for (source_verified, below_rho, public_key_verified, row_selector_public_key_verified), count in sorted(counts.items())
    ]


def raw_summary(window: str) -> dict[str, Any]:
    rows = raw_stress_rows(window)
    rule_rows = [row for row in rows if raw_rule(row)]
    negative_rows = [row for row in rows if raw_negative_control_rule(row)]
    source_replay_rows = [row for row in rows if raw_source_replay_positive(row)]
    return {
        "candidate_examples": [raw_compact(row) for row in rule_rows[:12]],
        "candidate_public_positive_count": sum(raw_public_positive(row) for row in rule_rows),
        "candidate_row_count": len(rule_rows),
        "candidate_source_replay_positive_count": sum(raw_source_replay_positive(row) for row in rule_rows),
        "flag_counts": flag_counts(rows),
        "negative_control_public_positive_count": sum(raw_public_positive(row) for row in negative_rows),
        "negative_control_row_count": len(negative_rows),
        "negative_control_source_replay_positive_count": sum(raw_source_replay_positive(row) for row in negative_rows),
        "raw_row_count": len(rows),
        "source_replay_positive_count": len(source_replay_rows),
        "source_replay_sample": [raw_compact(row) for row in source_replay_rows[:12]],
        "window": window,
    }


def build_rows(windows: list[str], targets: str, min_source_rank: int) -> tuple[dict[str, list[dict[str, Any]]], dict[str, bool]]:
    return p1010.build_window_rows(windows, targets, min_source_rank)


def builder_score(rows: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    selected = [row for row in rows if predicate(row)]
    positives = [row for row in rows if p1010.source_stress_positive(row)]
    selected_positives = [row for row in selected if p1010.source_stress_positive(row)]
    selected_ops = sum(source_ops(row) for row in selected)
    return {
        "case_count": len(rows),
        "positive_count": len(positives),
        "precision": safe_ratio(len(selected_positives), len(selected)),
        "recall": safe_ratio(len(selected_positives), len(positives)),
        "selected_count": len(selected),
        "selected_direct_sum_ops_over_rho": round(selected_ops, 8),
        "selected_positive_count": len(selected_positives),
        "useful_amortized_ops_over_rho": safe_ratio(selected_ops, len(selected_positives)),
    }


def selected_cases(rows: list[dict[str, Any]], predicate: Predicate, limit: int = 24) -> list[dict[str, Any]]:
    return [p1010.selected_case_summary(row) for row in rows if predicate(row)][:limit]


def order_diagnostics(selected: list[dict[str, Any]], groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    orders = [
        *p1009.public_order_candidates(),
        *[order for order in p1008.order_candidates() if order.get("diagnostic")],
    ]
    diagnostics = [p1008.first_hit_summary(selected, groups, order) for order in orders]
    diagnostics.sort(
        key=lambda row: (
            not row.get("first_scalar_valid_group_below_rho"),
            (row.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho", 10**9),
            row.get("order_name"),
        )
    )
    return diagnostics


def reconstruction_lane(
    name: str,
    rows: list[dict[str, Any]],
    predicate: Predicate,
    baseline_rank: int,
) -> dict[str, Any]:
    selected = [row for row in rows if predicate(row)]
    analysis, groups = p1005.scalar_valid_groups(
        selected,
        {"lane": name, "rule_family": RULE_NAME if name == "candidate" else NEGATIVE_CONTROL_NAME},
        baseline_rank,
    )
    orders = order_diagnostics(selected, groups)
    best = orders[0] if orders else {}
    return {
        "analysis_summary": analysis.get("summary"),
        "best_first_hit": best,
        "groups": [p1005.compact_group(group) for group in groups[:12]],
        "selected_cases": selected_cases(rows, predicate),
        "stress_selection": builder_score(rows, predicate),
    }


def determine_claim(candidate_lane: dict[str, Any]) -> str:
    stress = candidate_lane.get("stress_selection") or {}
    analysis = candidate_lane.get("analysis_summary") or {}
    first = (candidate_lane.get("best_first_hit") or {}).get("first_scalar_valid_group")
    if int_value(stress.get("selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P1013_RAW_RULE_NO_BUILDER_VISIBLE_POSITIVES"
    if int_value(analysis.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1013_RAW_RULE_NO_CONTEXT_SAFE_SCALAR_GROUP"
    if first and float(first.get("charged_ops_over_rho") or 10**9) < 1.0:
        return "P1013_DIAGNOSTIC_RAW_SOURCE_VISIBILITY_RESCUE_BELOW_RHO"
    if first:
        return "NEGATIVE_RESULT_P1013_RAW_RULE_FIRST_HIT_ABOVE_RHO"
    return "NEGATIVE_RESULT_P1013_RAW_RULE_NO_ORDER_HIT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = [DISCOVERY_WINDOW, DIAGNOSTIC_WINDOW]
    by_window, exists = build_rows(windows, args.targets, args.min_source_rank)
    discovery_rows = by_window[DISCOVERY_WINDOW]
    diagnostic_rows = by_window[DIAGNOSTIC_WINDOW]
    candidate_lane = reconstruction_lane("candidate", diagnostic_rows, builder_rule, args.baseline_rank)
    negative_lane = reconstruction_lane("negative_control", diagnostic_rows, negative_control_rule, args.baseline_rank)
    claim = determine_claim(candidate_lane)
    candidate_first = (candidate_lane.get("best_first_hit") or {}).get("first_scalar_valid_group") or {}
    negative_first = (negative_lane.get("best_first_hit") or {}).get("first_scalar_valid_group") or {}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "diagnostic_source_sha256": p1005.sha256_file(p1007.expanded_source_path(DIAGNOSTIC_WINDOW)),
            "discovery_source_sha256": p1005.sha256_file(p1007.expanded_source_path(DISCOVERY_WINDOW)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1013_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "DIAGNOSTIC BOUNDARY: 12024 was inspected during mismatch triage; next proof obligation is an unchanged frozen test on an unseen window.",
            "SOURCE-LABEL BOUNDARY: raw source_verified/below_rho labels motivate the rule but are not a selector input on the diagnostic builder rows.",
            "CONTEXT-SAFE-GATE: scalar-valid groups spanning multiple public fingerprints are rejected.",
            "INDEX-CALCULUS BOUNDARY: this is relation-surface prediction, not relation collection, sparse linear algebra, target descent, or a cryptographic-size break.",
        ],
        "method": "p1013_p231_raw_source_visibility_rescue_12024",
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "diagnostic_window": DIAGNOSTIC_WINDOW,
            "discovery_window": DISCOVERY_WINDOW,
            "min_source_rank": args.min_source_rank,
            "raw_policy": RAW_POLICY,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "raw_source": {
            DISCOVERY_WINDOW: raw_summary(DISCOVERY_WINDOW),
            DIAGNOSTIC_WINDOW: raw_summary(DIAGNOSTIC_WINDOW),
        },
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
            "candidate_best_charge": candidate_first.get("charged_ops_over_rho"),
            "candidate_context_safe_scalar_valid_group_count": (candidate_lane.get("analysis_summary") or {}).get(
                "context_safe_scalar_valid_group_count"
            ),
            "candidate_first_below_rho": (candidate_lane.get("best_first_hit") or {}).get(
                "first_scalar_valid_group_below_rho"
            ),
            "candidate_precision": (candidate_lane.get("stress_selection") or {}).get("precision"),
            "candidate_recall": (candidate_lane.get("stress_selection") or {}).get("recall"),
            "candidate_selected_count": (candidate_lane.get("stress_selection") or {}).get("selected_count"),
            "candidate_selected_positive_count": (candidate_lane.get("stress_selection") or {}).get(
                "selected_positive_count"
            ),
            "claim_status": claim,
            "diagnostic_builder_positive_count": builder_score(diagnostic_rows, lambda row: True).get("positive_count"),
            "discovery_builder_positive_count": builder_score(discovery_rows, lambda row: True).get("positive_count"),
            "negative_control_best_charge": negative_first.get("charged_ops_over_rho"),
            "negative_control_first_below_rho": (negative_lane.get("best_first_hit") or {}).get(
                "first_scalar_valid_group_below_rho"
            ),
            "negative_control_selected_count": (negative_lane.get("stress_selection") or {}).get("selected_count"),
            "negative_control_selected_positive_count": (negative_lane.get("stress_selection") or {}).get(
                "selected_positive_count"
            ),
        },
        "lanes": {
            "candidate": candidate_lane,
            "negative_control": negative_lane,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1013 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for builder labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} selected={selected} positives={positives} precision={precision} "
        "groups={groups} best_charge={best_charge} negative_selected={negative_selected} out={out}".format(
            claim=payload["claim_status"],
            selected=summary["candidate_selected_count"],
            positives=summary["candidate_selected_positive_count"],
            precision=summary["candidate_precision"],
            groups=summary["candidate_context_safe_scalar_valid_group_count"],
            best_charge=summary["candidate_best_charge"],
            negative_selected=summary["negative_control_selected_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
