#!/usr/bin/env python3
"""P737 selector-to-matrix bridge for P735/P736 detector-hit rows."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p730_public_window_regime_selector as p730
import low_term_total2_p731_public_regime_shift_override as p731
import low_term_total2_p735_target22050_public_detector_repair as p735


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p737_selector_to_matrix_bridge_probe.json"
FOCUS_SPLIT = "rolling_train24_holdout16_start16"


@dataclass(frozen=True)
class StreamConfig:
    name: str
    target: str
    fresh_source_pattern: str
    expected_detector_total: float


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def round8(value: float) -> float:
    return round(value, 8)


def gf2_rank(masks: list[int]) -> int:
    basis: dict[int, int] = {}
    rank = 0
    for mask in masks:
        value = mask
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
                continue
            basis[pivot] = value
            rank += 1
            break
    return rank


def mask_for(values: list[str], index: dict[str, int]) -> int:
    mask = 0
    for value in values:
        if value not in index:
            index[value] = len(index)
        mask ^= 1 << index[value]
    return mask


def source_case(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_case") or {}


def row_key_variables(row: dict[str, Any]) -> list[str]:
    return [str(item) for item in source_case(row).get("row_keys") or []]


def row_leaf_variables(row: dict[str, Any]) -> list[str]:
    variables: list[str] = []
    for item in source_case(row).get("row_leaf_keys") or []:
        row_key = str(item.get("row_key"))
        leaf_indices = item.get("leaf_indices") or []
        if not leaf_indices:
            variables.append(row_key)
            continue
        for leaf in leaf_indices:
            variables.append(f"{row_key}:leaf{int_value(leaf)}")
    return variables or row_key_variables(row)


def semantic_hit_key(row: dict[str, Any]) -> str:
    case = source_case(row)
    payload = {
        "row_keys": case.get("row_keys") or [],
        "selector": case.get("selector"),
        "target": case.get("target"),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def build_args(config: StreamConfig, args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        attempt_budgets=args.attempt_budgets,
        base_source_pattern=args.base_source_pattern,
        fresh_source_pattern=config.fresh_source_pattern,
        max_transfer=args.max_transfer,
        min_transfer=args.min_transfer,
        out="",
        p709=args.p709,
        p730_reference=args.p730_reference,
        rolling_holdout_size=args.rolling_holdout_size,
        rolling_train_size=args.rolling_train_size,
        sample_limit=args.sample_limit,
        selector_limit=args.selector_limit,
        target=config.target,
        thresholds=args.thresholds,
    )


def split_by_name(reports: list[dict[str, Any]], args: argparse.Namespace, name: str) -> dict[str, Any]:
    for split in p730.split_reports(reports, args):
        if split.get("split") == name:
            return split
    raise KeyError(name)


def reconstruct_stream(config: StreamConfig, args: argparse.Namespace) -> dict[str, Any]:
    stream_args = build_args(config, args)
    factor_charge = 0.992
    p709_payload = p730.p729.load_json(Path(stream_args.p709))
    if p709_payload:
        factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    merged_reports, metadata, merge_stats = p730.p729.build_merged_reports(stream_args)
    gates = {
        gate.policy_budget: gate
        for gate in p730.p729.make_gates(
            merged_reports,
            p730.parse_floats(stream_args.thresholds),
            p730.parse_ints(stream_args.attempt_budgets),
            int_value(stream_args.selector_limit),
        )
    }
    features_by_window = {
        (int_value(report.get("window_start")), int_value(report.get("window_end"))): p730.window_features(report, gates)
        for report in merged_reports
    }
    rules = p730.make_rules()
    split = split_by_name(merged_reports, stream_args, FOCUS_SPLIT)
    train_reports = merged_reports[int_value(split["train_start_index"]): int_value(split["train_end_index"])]
    holdout_reports = merged_reports[int_value(split["holdout_start_index"]): int_value(split["holdout_end_index"])]
    train_scores = [
        p730.evaluate_rule(train_reports, metadata, gates, features_by_window, rule, factor_charge, 1)
        for rule in rules
    ]
    selected_rule_name = str(p730.choose_best(train_scores).get("rule_name"))
    train_features = p731.summarize_feature_block(train_reports, features_by_window)
    holdout_features = p731.summarize_feature_block(holdout_reports, features_by_window)
    decision = p735.repaired_detector_choice(selected_rule_name, train_features, holdout_features)
    detector_rule = p731.rule_by_name(rules, decision["chosen_rule_name"])
    detector_eval = p730.evaluate_rule(
        holdout_reports,
        metadata,
        gates,
        features_by_window,
        detector_rule,
        factor_charge,
        int_value(stream_args.sample_limit),
    )
    rows = collect_detector_rows(holdout_reports, metadata, gates, features_by_window, detector_rule)
    matrix = matrix_summary(rows["hit_rows"])
    reproduced_total = float_value(detector_eval.get("source_replay_total_with_fallback_over_rho"))
    return {
        "detector_decision": decision,
        "detector_eval": {
            "accepted_candidate_count": detector_eval.get("accepted_candidate_count"),
            "attempted_candidate_count": detector_eval.get("attempted_candidate_count"),
            "attempted_source_charge_over_rho": detector_eval.get("attempted_source_charge_over_rho"),
            "beats_rho_with_fallback": detector_eval.get("beats_rho_with_fallback"),
            "fallback_charge_over_rho": detector_eval.get("fallback_charge_over_rho"),
            "factor_charge_over_rho": detector_eval.get("factor_charge_over_rho"),
            "hit_count": detector_eval.get("hit_count"),
            "policy_counts": detector_eval.get("policy_counts"),
            "rule_name": detector_eval.get("rule_name"),
            "source_replay_total_with_fallback_over_rho": reproduced_total,
            "vs_independent_rho_with_fallback_over_rho": detector_eval.get("vs_independent_rho_with_fallback_over_rho"),
            "window_count": detector_eval.get("window_count"),
        },
        "focus_expected_detector_total": config.expected_detector_total,
        "focus_total_delta_vs_expected": round8(reproduced_total - config.expected_detector_total),
        "hit_rows": rows["hit_rows"],
        "matrix_summary": matrix,
        "merge_stats": merge_stats,
        "metadata_summary": {
            "shared_replay_cache_count": len(metadata.get("shared_replay_cache") or {}),
            "shared_replay_error_count": len(metadata.get("shared_replay_errors") or {}),
            "unique_union_mismatch_count": sum(
                1 for replay in (metadata.get("shared_replay_cache") or {}).values()
                if not replay.get("union_matches_all_fields")
            ),
        },
        "row_stream": rows["summary"],
        "sample_hit_rows": rows["sample_hit_rows"],
        "selected_train_rule_name": selected_rule_name,
        "split": FOCUS_SPLIT,
        "stream": config.name,
        "target": config.target,
        "window_ranges": {
            "holdout": p731.split_window_ranges(holdout_reports),
            "train": p731.split_window_ranges(train_reports),
        },
    }


def collect_detector_rows(
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    gates: dict[str, p730.p729.PublicGate],
    features_by_window: dict[tuple[int, int], p730.WindowFeatures],
    rule: p730.RegimeRule,
) -> dict[str, Any]:
    attempted_rows: list[dict[str, Any]] = []
    hit_rows: list[dict[str, Any]] = []
    fallback_windows: list[list[int]] = []
    attempted_charge = 0.0
    mismatch_count = 0
    for report in reports:
        key = (int_value(report.get("window_start")), int_value(report.get("window_end")))
        features = features_by_window[key]
        policy_budget = rule.chooser(features)
        gate = gates[policy_budget]
        accepted = p730.gate_accepts(gate, report)
        hit_seen = False
        for row in accepted[: gate.budget]:
            replay = p730.p720.shared_replay_for_row(row, metadata)
            charge = float_value(row.get("direct_ops_over_rho"))
            if replay is not None:
                charge = float_value(replay.get("shared_ops_over_rho"))
                if not replay.get("union_matches_all_fields"):
                    mismatch_count += 1
            attempted_charge += charge
            record = row_record(row, replay, report, policy_budget, charge)
            attempted_rows.append(record)
            if replay is not None and replay.get("shared_hit"):
                hit_rows.append(record)
                hit_seen = True
                break
        if not hit_seen:
            fallback_windows.append([int_value(report.get("window_start")), int_value(report.get("window_end"))])
    unique_hits = {record["semantic_hit_key"] for record in hit_rows}
    return {
        "hit_rows": hit_rows,
        "sample_hit_rows": hit_rows[:8],
        "summary": {
            "attempted_charge_over_rho": round8(attempted_charge),
            "attempted_row_count": len(attempted_rows),
            "duplicate_hit_count": len(hit_rows) - len(unique_hits),
            "fallback_window_count": len(fallback_windows),
            "fallback_windows": fallback_windows[:8],
            "hit_count": len(hit_rows),
            "mismatch_count": mismatch_count,
            "unique_hit_count": len(unique_hits),
            "window_count": len(reports),
        },
    }


def row_record(
    row: dict[str, Any],
    replay: dict[str, Any] | None,
    report: dict[str, Any],
    policy_budget: str,
    charged_ops_over_rho: float,
) -> dict[str, Any]:
    case = source_case(row)
    return {
        "charged_ops_over_rho": round8(charged_ops_over_rho),
        "direct_ops_over_rho": float_value(row.get("direct_ops_over_rho")),
        "origin": row.get("p722_origin"),
        "policy_budget": policy_budget,
        "rank": None if replay is None else replay.get("rank"),
        "relation_count": int_value(case.get("relation_count")),
        "replay_shared_hit": bool(replay and replay.get("shared_hit")),
        "row_key_variables": row_key_variables(row),
        "row_leaf_variables": row_leaf_variables(row),
        "semantic_hit_key": semantic_hit_key(row),
        "selector": case.get("selector"),
        "shared_ops_over_rho": None if replay is None else replay.get("shared_ops_over_rho"),
        "source": row.get("source"),
        "source_policy": case.get("source_policy"),
        "target": case.get("target"),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
        "union_matches_all_fields": bool(replay and replay.get("union_matches_all_fields")),
        "window": [int_value(report.get("window_start")), int_value(report.get("window_end"))],
    }


def matrix_summary(hit_rows: list[dict[str, Any]]) -> dict[str, Any]:
    row_key_index: dict[str, int] = {}
    row_leaf_index: dict[str, int] = {}
    row_key_masks = [mask_for(row["row_key_variables"], row_key_index) for row in hit_rows]
    row_leaf_masks = [mask_for(row["row_leaf_variables"], row_leaf_index) for row in hit_rows]
    replay_ranks = [int_value(row.get("rank")) for row in hit_rows if row.get("rank") is not None]
    return {
        "hit_row_count": len(hit_rows),
        "max_replay_rank": max(replay_ranks, default=0),
        "replay_rank_sum": sum(replay_ranks),
        "row_key_gf2_rank": gf2_rank(row_key_masks),
        "row_key_rank_deficit": len(row_key_index) - gf2_rank(row_key_masks),
        "row_key_variable_count": len(row_key_index),
        "row_leaf_gf2_rank": gf2_rank(row_leaf_masks),
        "row_leaf_rank_deficit": len(row_leaf_index) - gf2_rank(row_leaf_masks),
        "row_leaf_variable_count": len(row_leaf_index),
    }


def determine_claim(streams: list[dict[str, Any]], combined: dict[str, Any]) -> str:
    totals_match = all(abs(float_value(stream.get("focus_total_delta_vs_expected"))) <= 1e-8 for stream in streams)
    clean_replay = all(
        int_value(stream["metadata_summary"].get("shared_replay_error_count")) == 0
        and int_value(stream["metadata_summary"].get("unique_union_mismatch_count")) == 0
        for stream in streams
    )
    nontrivial_rank = all(int_value(stream["matrix_summary"].get("row_leaf_gf2_rank")) > 0 for stream in streams)
    if totals_match and clean_replay and nontrivial_rank and int_value(combined.get("row_leaf_gf2_rank")) > 0:
        return "P737_SELECTOR_TO_MATRIX_RANK_PROXY_POSITIVE_TARGET_DESCENT_OPEN"
    if not totals_match:
        return "NEGATIVE_RESULT_P737_SCORE_REPRODUCTION_FAILED"
    if not clean_replay:
        return "NEGATIVE_RESULT_P737_REPLAY_INVALID"
    return "NEGATIVE_RESULT_P737_SELECTOR_ROWS_HAVE_TRIVIAL_RANK_PROXY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    configs = [
        StreamConfig(
            name="p735_target22050_focus",
            target="22050.cf1@11731",
            fresh_source_pattern="frontier_public_leaf_policy_p734_target22050_materialized_fixed_row_*_col15_selector_expanded_probe.json",
            expected_detector_total=8.32776636,
        ),
        StreamConfig(
            name="p736_target67_focus",
            target="67.a1@9803",
            fresh_source_pattern="frontier_public_leaf_policy_p72*_target67_materialized_fixed_row_*_col15_selector_expanded_probe.json",
            expected_detector_total=11.112,
        ),
    ]
    streams = [reconstruct_stream(config, args) for config in configs]
    combined = matrix_summary([row for stream in streams for row in stream["hit_rows"]])
    payload = {
        "claim_status": "",
        "combined_matrix_summary": combined,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: reuses archived materialized source banks and replay machinery.",
            "RANK-PROXY ONLY: GF(2) incidence rank is not a modular factor-log solve.",
            "TARGET_DESCENT_OPEN: no complete target-descent or individual-log recovery is claimed.",
        ],
        "method": "p737_selector_to_matrix_bridge",
        "parameters": {
            "base_source_pattern": args.base_source_pattern,
            "focus_split": FOCUS_SPLIT,
            "rank_model": "GF(2) row-key and row-leaf incidence proxy",
            "target_descent_required_for_breakthrough": True,
        },
        "schema": "ecdlp.low_term_total2_p737_selector_to_matrix_bridge.v1",
        "streams": streams,
        "target_descent_status": {
            "status": "OPEN",
            "reason": (
                "P737 exports incidence-rank proxies from verified detector-hit rows, "
                "but does not yet extract a full modular coefficient matrix or solve factor logs for target descent."
            ),
            "next_requirement": (
                "Extract true modular relation coefficients from replay contexts, solve/rank the factor-log matrix, "
                "and charge sparse linear algebra plus individual-log descent against rho."
            ),
        },
    }
    payload["claim_status"] = determine_claim(streams, combined)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budgets", default="1,2")
    parser.add_argument("--base-source-pattern", default=p730.BASE_PATTERN)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(p731.DEFAULT_P709))
    parser.add_argument("--p730-reference", default=str(p731.P730_REFERENCE))
    parser.add_argument("--rolling-holdout-size", type=int, default=16)
    parser.add_argument("--rolling-train-size", type=int, default=24)
    parser.add_argument("--sample-limit", type=int, default=4)
    parser.add_argument("--selector-limit", type=int, default=10)
    parser.add_argument("--thresholds", default="0.488,0.52,0.544,0.568,0.616,0.888,0.928,1.0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    p731.write_json(Path(args.out), payload)
    compact = {
        "claim_status": payload["claim_status"],
        "streams": [
            {
                "detector_eval": stream["detector_eval"],
                "focus_total_delta_vs_expected": stream["focus_total_delta_vs_expected"],
                "matrix_summary": stream["matrix_summary"],
                "row_stream": stream["row_stream"],
                "stream": stream["stream"],
                "target": stream["target"],
            }
            for stream in payload["streams"]
        ],
        "target_descent_status": payload["target_descent_status"],
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
