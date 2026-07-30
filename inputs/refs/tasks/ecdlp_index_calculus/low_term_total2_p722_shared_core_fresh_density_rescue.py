#!/usr/bin/env python3
"""P722 fresh-density rescue audit for the P721 hard split."""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p713_rel2_cost_threshold_temporal_split as p713
import low_term_total2_p716_rel2_source_generation_enrichment as p716
import low_term_total2_p721_shared_core_new_bank_rescue_audit as p721
import low_term_total2_p720_shared_core_temporal_generalization_audit as p720


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_P721 = STATE_DIR / "low_term_total2_p721_shared_core_new_bank_rescue_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p722_shared_core_fresh_density_rescue_probe.json"
BASE_PATTERN = "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_*_col15_selector_expanded_probe.json"
FRESH_PATTERN = "frontier_public_leaf_policy_p722_density*_fixed_row_*_col15_selector_expanded_probe.json"
HARD_SPLIT = "rolling_train24_holdout16_start0"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p720.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p720.float_value(value, default)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def build_reports(args: argparse.Namespace, source_pattern: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    build_args = argparse.Namespace(
        max_transfer=int_value(args.max_transfer),
        min_transfer=int_value(args.min_transfer),
        p709=args.p709,
        source_pattern=source_pattern,
        target=args.target,
        thresholds=args.thresholds,
    )
    reports, metadata = p716.build_window_reports(build_args)
    metadata["shared_replay_cache"] = {}
    metadata["shared_replay_errors"] = {}
    return reports, metadata


def source_case_value(row: dict[str, Any], key: str) -> Any:
    return (row.get("source_case") or {}).get(key, row.get(key))


def semantic_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        source_case_value(row, "target"),
        int_value(source_case_value(row, "transfer_index")),
        source_case_value(row, "source_policy"),
        source_case_value(row, "selector"),
        int_value(source_case_value(row, "top_k")),
        tuple(str(item) for item in source_case_value(row, "row_keys") or []),
        tuple(tuple(str(part) for part in item) for item in source_case_value(row, "row_leaf_keys") or []),
        int_value(source_case_value(row, "selected_leaf_count")),
        int_value(source_case_value(row, "selected_row_count")),
        int_value(source_case_value(row, "relation_count")),
    )


def report_key(report: dict[str, Any]) -> tuple[int, int]:
    return int_value(report.get("window_start")), int_value(report.get("window_end"))


def clone_candidate(row: dict[str, Any], origin: str) -> dict[str, Any]:
    copied = copy.deepcopy(row)
    copied["p722_origin"] = origin
    return copied


def merge_reports(
    base_reports: list[dict[str, Any]],
    fresh_reports: list[dict[str, Any]],
    base_metadata: dict[str, Any],
    fresh_metadata: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    fresh_by_window = {report_key(report): report for report in fresh_reports}
    merged_reports = []
    stats = {
        "base_candidate_count": 0,
        "base_window_count": len(base_reports),
        "duplicate_fresh_candidate_count": 0,
        "fresh_candidate_count": sum(len(report.get("candidates") or []) for report in fresh_reports),
        "fresh_window_count": len(fresh_reports),
        "merged_candidate_count": 0,
        "new_fresh_candidate_count": 0,
        "windows_with_fresh_candidates": 0,
    }
    for base in base_reports:
        seen: set[tuple[Any, ...]] = set()
        candidates = []
        for row in sorted(base.get("candidates") or [], key=p716.row_sort_key):
            key = semantic_key(row)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(clone_candidate(row, "base"))
        stats["base_candidate_count"] += len(candidates)
        fresh = fresh_by_window.get(report_key(base))
        fresh_added = 0
        if fresh:
            for row in sorted(fresh.get("candidates") or [], key=p716.row_sort_key):
                key = semantic_key(row)
                if key in seen:
                    stats["duplicate_fresh_candidate_count"] += 1
                    continue
                seen.add(key)
                candidates.append(clone_candidate(row, "fresh"))
                fresh_added += 1
        if fresh_added:
            stats["windows_with_fresh_candidates"] += 1
        stats["new_fresh_candidate_count"] += fresh_added
        stats["merged_candidate_count"] += len(candidates)
        merged_reports.append(
            {
                **base,
                "candidates": sorted(candidates, key=p716.row_sort_key),
                "p722_fresh_added_candidate_count": fresh_added,
            }
        )
    metadata = {
        "group_candidate_counts": {},
        "selector_counts": {},
        "source_cache": {
            **(base_metadata.get("source_cache") or {}),
            **(fresh_metadata.get("source_cache") or {}),
        },
        "shared_replay_cache": {},
        "shared_replay_errors": {},
    }
    return merged_reports, metadata, stats


def split_reports(reports: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    return p713.prefix_splits(reports) + p713.rolling_splits(
        reports,
        int_value(args.rolling_train_size),
        int_value(args.rolling_holdout_size),
    )


def find_split(universe: dict[str, Any], split_name: str = HARD_SPLIT) -> dict[str, Any]:
    for report in universe.get("split_reports") or []:
        if report.get("split") == split_name:
            return report
    return {}


def compact_hard_split(universe: dict[str, Any]) -> dict[str, Any]:
    report = find_split(universe)
    return {
        "fixed_new": p721.compact_or_none(report.get("fixed_two_by_two_1p0_holdout_new_bank")),
        "heldout_oracle_new": p721.compact_or_none(report.get("heldout_oracle_best_new_bank")),
        "marginal_train_selected_new": p721.compact_or_none(report.get("marginal_train_selected_holdout_new_bank")),
        "marginal_train_selected_policy_budget": report.get("marginal_train_selected_policy_budget"),
        "new_bank_train_selected_new": p721.compact_or_none(report.get("new_bank_train_selected_holdout_new_bank")),
        "new_bank_train_selected_policy_budget": report.get("new_bank_train_selected_policy_budget"),
        "window_ranges": report.get("window_ranges"),
    }


def evaluate_stream(
    name: str,
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    args: argparse.Namespace,
    factor_charge: float,
) -> dict[str, Any]:
    thresholds = p720.parse_floats(args.thresholds)
    budgets = p720.parse_ints(args.attempt_budgets)
    return p721.evaluate_universe(
        name,
        p721.parse_groups(args.expanded_groups),
        reports,
        split_reports(reports, args),
        metadata,
        thresholds,
        budgets,
        factor_charge,
        int_value(args.sample_limit),
    )


def total(report: dict[str, Any], key: str) -> float | None:
    item = report.get(key) or {}
    value = item.get("source_replay_total_with_fallback_over_rho")
    return None if value is None else float_value(value)


def determine_claim(fresh_stats: dict[str, Any], baseline: dict[str, Any], merged: dict[str, Any]) -> str:
    if int_value(fresh_stats.get("fresh_window_count")) == 0:
        return "NEGATIVE_RESULT_P722_NO_FRESH_DENSITY_ARTIFACTS"
    hard = find_split(merged)
    fixed = hard.get("fixed_two_by_two_1p0_holdout_new_bank") or {}
    selected_new = hard.get("new_bank_train_selected_holdout_new_bank") or {}
    oracle = hard.get("heldout_oracle_best_new_bank") or {}
    if fixed.get("beats_rho_with_fallback"):
        return "P722_FRESH_DENSITY_RESCUES_START0_FIXED_POLICY"
    if selected_new.get("beats_rho_with_fallback"):
        return "P722_FRESH_DENSITY_RESCUES_START0_TRAIN_SELECTED_POLICY"
    if oracle.get("beats_rho_with_fallback"):
        return "P722_FRESH_DENSITY_ORACLE_RESCUES_START0_SELECTOR_OPEN"
    baseline_oracle = total(find_split(baseline), "heldout_oracle_best_new_bank")
    merged_oracle = total(hard, "heldout_oracle_best_new_bank")
    if baseline_oracle is not None and merged_oracle is not None and merged_oracle < baseline_oracle:
        return "P722_FRESH_DENSITY_NARROWS_START0_GAP_BUT_STILL_ABOVE_RHO"
    return "NEGATIVE_RESULT_P722_FRESH_DENSITY_START0_STILL_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    p721_payload = load_json(Path(args.p721))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    base_reports, base_metadata = build_reports(args, args.base_source_pattern)
    fresh_reports, fresh_metadata = build_reports(args, args.fresh_source_pattern)
    merged_reports, merged_metadata, merge_stats = merge_reports(
        base_reports,
        fresh_reports,
        base_metadata,
        fresh_metadata,
    )
    baseline_universe = evaluate_stream("baseline_public_rel2", base_reports, base_metadata, args, factor_charge)
    merged_universe = evaluate_stream("merged_fresh_public_rel2", merged_reports, merged_metadata, args, factor_charge)
    replay_metadata = {
        "baseline_shared_replay_cache_count": len(base_metadata["shared_replay_cache"]),
        "baseline_shared_replay_error_count": len(base_metadata["shared_replay_errors"]),
        "baseline_unique_mismatch_count": sum(
            1 for replay in base_metadata["shared_replay_cache"].values() if not replay.get("union_matches_all_fields")
        ),
        "merged_shared_replay_cache_count": len(merged_metadata["shared_replay_cache"]),
        "merged_shared_replay_error_count": len(merged_metadata["shared_replay_errors"]),
        "merged_unique_mismatch_count": sum(
            1 for replay in merged_metadata["shared_replay_cache"].values() if not replay.get("union_matches_all_fields")
        ),
        "shared_replay_errors": {
            "baseline": base_metadata["shared_replay_errors"],
            "merged": merged_metadata["shared_replay_errors"],
        },
    }
    payload = {
        "artifacts": {
            "p709": str(Path(args.p709)),
            "p721": str(Path(args.p721)),
        },
        "baseline_hard_split": compact_hard_split(baseline_universe),
        "baseline_universe": baseline_universe,
        "claim_status": "",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: generated source rows are still AutoLab toy-harness rows, not live cryptographic harvesting.",
            "REPLAY-BACKED: every charged candidate uses the P719 shared-core replay path.",
            "NO DUPLICATE-DENSITY CLAIM: semantic duplicate rows are counted once.",
            "NO DEPLOYED-CURVE CLAIM: sparse linear algebra, target descent, and large-prime scaling remain open.",
        ],
        "method": "p722_shared_core_fresh_density_rescue",
        "merged_hard_split": compact_hard_split(merged_universe),
        "merged_universe": merged_universe,
        "parameters": {
            "attempt_budgets": p720.parse_ints(args.attempt_budgets),
            "base_source_pattern": args.base_source_pattern,
            "expanded_groups": p721.parse_groups(args.expanded_groups),
            "factor_bank_charge_over_rho": factor_charge,
            "fresh_source_pattern": args.fresh_source_pattern,
            "hard_split": HARD_SPLIT,
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "rolling_holdout_size": int_value(args.rolling_holdout_size),
            "rolling_train_size": int_value(args.rolling_train_size),
            "target": args.target,
            "thresholds": p720.parse_floats(args.thresholds),
        },
        "p721_reference": {
            "claim_status": p721_payload.get("claim_status"),
            "hard_split": next(
                (
                    report
                    for universe in p721_payload.get("universe_reports") or []
                    if universe.get("name") == "expanded_public_rel2"
                    for report in universe.get("split_reports") or []
                    if report.get("split") == HARD_SPLIT
                ),
                {},
            ),
        },
        "replay_metadata": replay_metadata,
        "schema": "ecdlp.low_term_total2_p722_shared_core_fresh_density_rescue.v1",
        "source_merge_stats": merge_stats,
    }
    payload["claim_status"] = determine_claim(merge_stats, baseline_universe, merged_universe)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budgets", default="1,2")
    parser.add_argument("--base-source-pattern", default=BASE_PATTERN)
    parser.add_argument(
        "--expanded-groups",
        default="baseline_total1,low_term_any,low_term_excluding_total1,cost_low_term_any,two_by_two_any,all_excluding_total1,all_rel2",
    )
    parser.add_argument("--fresh-source-pattern", default=FRESH_PATTERN)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--p721", default=str(DEFAULT_P721))
    parser.add_argument("--rolling-holdout-size", type=int, default=16)
    parser.add_argument("--rolling-train-size", type=int, default=24)
    parser.add_argument("--sample-limit", type=int, default=4)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--thresholds", default="0.544,0.568,0.616,1.0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "baseline_hard_split": payload["baseline_hard_split"],
                "claim_status": payload["claim_status"],
                "merged_hard_split": payload["merged_hard_split"],
                "replay_metadata": payload["replay_metadata"],
                "source_merge_stats": payload["source_merge_stats"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
