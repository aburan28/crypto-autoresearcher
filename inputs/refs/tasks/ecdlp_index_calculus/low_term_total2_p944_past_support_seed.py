#!/usr/bin/env python3
"""P944 rolling-past public support seeding for the P943 selector gap."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tasks.ecdlp_index_calculus.low_term_total2_p942_hash_context_discriminator import (
    P939_SOURCE,
    feature_value,
    int_value,
    load_rows,
    mean,
    now_iso,
    summarize_selected,
    window_start,
    write_json,
)


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p944_past_support_seed.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p944_past_support_seed_probe.json"
SCHEMA = "ecdlp.low_term_total2_p944_past_support_seed.v1"


@dataclass(frozen=True)
class Strategy:
    name: str
    features: tuple[str, ...]
    min_clean_count: int = 2
    transfer_modulus: int | None = None
    transfer_radius: int = 0

    @property
    def public_class(self) -> str:
        if "hash" in self.features:
            return "hash_seeded"
        if "target" in self.features or "target_label" in self.features:
            return "target_seeded"
        return "coefficient_seeded"


def transfer_residue(row: dict[str, Any], modulus: int) -> int | None:
    transfer = row.get("transfer_index")
    if transfer is None:
        return None
    return int(transfer) % modulus


def circular_distance(left: int, right: int, modulus: int) -> int:
    diff = abs(left - right) % modulus
    return min(diff, modulus - diff)


def support_match(train_row: dict[str, Any], holdout_row: dict[str, Any], strategy: Strategy) -> bool:
    for feature in strategy.features:
        left = feature_value(train_row, feature)
        right = feature_value(holdout_row, feature)
        if left is None or right is None or left != right:
            return False
    if strategy.transfer_modulus is not None:
        left_residue = transfer_residue(train_row, strategy.transfer_modulus)
        right_residue = transfer_residue(holdout_row, strategy.transfer_modulus)
        if left_residue is None or right_residue is None:
            return False
        if circular_distance(left_residue, right_residue, strategy.transfer_modulus) > strategy.transfer_radius:
            return False
    return True


def selected_by_strategy(holdout_row: dict[str, Any], train_rows: list[dict[str, Any]], strategy: Strategy) -> bool:
    support = [row for row in train_rows if support_match(row, holdout_row, strategy)]
    if not support:
        return False
    clean_count = sum(1 for row in support if row.get("clean"))
    if clean_count < strategy.min_clean_count:
        return False
    return clean_count == len(support)


def sorted_windows(rows_by_window: dict[str, list[dict[str, Any]]]) -> list[str]:
    return sorted(rows_by_window, key=window_start)


def build_strategies() -> list[Strategy]:
    strategies: list[Strategy] = [
        Strategy("p943_exact_hash_transfer_mod4", ("hash",), transfer_modulus=4, transfer_radius=0),
        Strategy("same_hash_any_transfer", ("hash",)),
        Strategy("same_hash_same_target_any_transfer", ("hash", "target")),
        Strategy("same_hash_transfer_mod2", ("hash",), transfer_modulus=2, transfer_radius=0),
        Strategy("same_hash_target_transfer_mod2", ("hash", "target"), transfer_modulus=2, transfer_radius=0),
        Strategy("same_hash_transfer_mod4_adjacent1", ("hash",), transfer_modulus=4, transfer_radius=1),
        Strategy("same_hash_target_transfer_mod4_adjacent1", ("hash", "target"), transfer_modulus=4, transfer_radius=1),
        Strategy("same_hash_transfer_mod4_radius2", ("hash",), transfer_modulus=4, transfer_radius=2),
        Strategy("same_hash_target_transfer_mod4_radius2", ("hash", "target"), transfer_modulus=4, transfer_radius=2),
        Strategy("same_target_transfer_mod4", ("target",), transfer_modulus=4, transfer_radius=0),
        Strategy("same_target_label_transfer_mod4", ("target_label",), transfer_modulus=4, transfer_radius=0),
        Strategy("same_target_transfer_mod2", ("target",), transfer_modulus=2, transfer_radius=0),
        Strategy("same_target_label_transfer_mod2", ("target_label",), transfer_modulus=2, transfer_radius=0),
        Strategy("same_target_transfer_mod4_adjacent1", ("target",), transfer_modulus=4, transfer_radius=1),
        Strategy("same_target_label_transfer_mod4_adjacent1", ("target_label",), transfer_modulus=4, transfer_radius=1),
        Strategy("same_target_transfer_mod4_radius2", ("target",), transfer_modulus=4, transfer_radius=2),
        Strategy("same_target_label_transfer_mod4_radius2", ("target_label",), transfer_modulus=4, transfer_radius=2),
        Strategy("same_target_policy_head_transfer_mod4", ("target", "policy_head"), transfer_modulus=4, transfer_radius=0),
        Strategy("target_coeffsum4_transfer_mod4", ("target", "coeff_sum_mod4"), transfer_modulus=4, transfer_radius=0),
        Strategy("target_coeffsum8_transfer_mod4", ("target", "coeff_sum_mod8"), transfer_modulus=4, transfer_radius=0),
        Strategy("target_constant4_b4_transfer_mod4", ("target", "constant_mod4", "b_coeff_mod4"), transfer_modulus=4, transfer_radius=0),
        Strategy("target_constant8_b8_transfer_mod4", ("target", "constant_mod8", "b_coeff_mod8"), transfer_modulus=4, transfer_radius=0),
        Strategy("target_label_coeffsum4_transfer_mod4", ("target_label", "coeff_sum_mod4"), transfer_modulus=4, transfer_radius=0),
        Strategy("target_label_coeffsum8_transfer_mod4", ("target_label", "coeff_sum_mod8"), transfer_modulus=4, transfer_radius=0),
        Strategy("target_factor_shape_transfer_mod4", ("target", "factor_total_degree", "factor_monomials"), transfer_modulus=4, transfer_radius=0),
        Strategy("target_label_factor_shape_transfer_mod4", ("target_label", "factor_total_degree", "factor_monomials"), transfer_modulus=4, transfer_radius=0),
    ]
    return strategies


def evaluate_strategy(strategy: Strategy, rows_by_window: dict[str, list[dict[str, Any]]], include_rows: bool = False) -> dict[str, Any]:
    windows = sorted_windows(rows_by_window)
    holdouts: list[dict[str, Any]] = []
    all_selected: list[dict[str, Any]] = []
    for index, window in enumerate(windows):
        train_windows = windows[:index]
        train_rows = [row for train_window in train_windows for row in rows_by_window[train_window]]
        holdout_rows = rows_by_window[window]
        selected = [row for row in holdout_rows if selected_by_strategy(row, train_rows, strategy)]
        all_selected.extend(selected)
        summary = {
            "holdout_class": holdout_rows[0].get("control_class") if holdout_rows else None,
            "holdout_window": window,
            "train_row_count": len(train_rows),
            "train_window_count": len(train_windows),
            "train_windows": train_windows,
            **summarize_selected(selected, holdout_rows),
        }
        if not include_rows:
            summary.pop("selected_rows", None)
        holdouts.append(summary)
    ops_holdouts = [item for item in holdouts if item.get("holdout_class") == "ops_rule_window"]
    control_holdouts = [item for item in holdouts if item.get("holdout_class") != "ops_rule_window"]
    ratios = [float(row["ratio"]) for row in all_selected if row.get("ratio") is not None]
    target_632 = next((item for item in holdouts if item.get("holdout_window") == "632_639"), {})
    target_520 = next((item for item in holdouts if item.get("holdout_window") == "520_535"), {})
    return {
        "all_selected_clean": all(bool(row.get("clean")) for row in all_selected) if all_selected else False,
        "all_selected_preserve": all(bool(row.get("preserve")) for row in all_selected) if all_selected else False,
        "control_holdouts_with_clean_selection": sum(1 for item in control_holdouts if int_value(item.get("selected_clean_count")) > 0),
        "control_window_count": len(control_holdouts),
        "false_positive_count": sum(int_value(item.get("false_positive_count")) for item in holdouts),
        "features": list(strategy.features),
        "holdouts": holdouts,
        "max_selected_ratio": max(ratios) if ratios else None,
        "mean_selected_ratio": mean(ratios),
        "min_clean_count": strategy.min_clean_count,
        "min_selected_ratio": min(ratios) if ratios else None,
        "non_preserving_count": sum(int_value(item.get("non_preserving_count")) for item in holdouts),
        "ops_holdouts_with_clean_selection": sum(1 for item in ops_holdouts if int_value(item.get("selected_clean_count")) > 0),
        "ops_window_count": len(ops_holdouts),
        "public_class": strategy.public_class,
        "selected_clean_count": sum(int_value(item.get("selected_clean_count")) for item in holdouts),
        "selected_count": sum(int_value(item.get("selected_count")) for item in holdouts),
        "strategy": strategy.name,
        "target_520_clean_selected": int_value(target_520.get("selected_clean_count")),
        "target_520_selected": int_value(target_520.get("selected_count")),
        "target_632_clean_selected": int_value(target_632.get("selected_clean_count")),
        "target_632_selected": int_value(target_632.get("selected_count")),
        "target_632_selected_hashes": target_632.get("selected_hashes") or [],
        "transfer_modulus": strategy.transfer_modulus,
        "transfer_radius": strategy.transfer_radius,
        "windows_with_clean_selection": sum(1 for item in holdouts if int_value(item.get("selected_clean_count")) > 0),
    }


def dirty_free(result: dict[str, Any]) -> bool:
    return int_value(result.get("false_positive_count")) == 0 and int_value(result.get("non_preserving_count")) == 0


def rank_key(result: dict[str, Any]) -> tuple[Any, ...]:
    return (
        dirty_free(result),
        int_value(result.get("target_632_clean_selected")) > 0,
        result.get("public_class") == "hash_seeded",
        result.get("public_class") == "target_seeded",
        int_value(result.get("target_632_clean_selected")),
        int_value(result.get("selected_clean_count")),
        -int_value(result.get("selected_count")),
        -(result.get("transfer_radius") or 0),
        -len(result.get("features") or []),
    )


def determine_claim(baseline: dict[str, Any], best_recovering: dict[str, Any] | None) -> str:
    if not dirty_free(baseline):
        return "NEGATIVE_RESULT_P944_BASELINE_DIRTY_UNEXPECTED"
    if best_recovering is None:
        return "NEGATIVE_RESULT_P944_NO_PAST_SUPPORT_SEED_RECOVERS_632"
    if best_recovering.get("public_class") == "hash_seeded":
        return "P944_HASH_SEEDED_PAST_SUPPORT_RECOVERS_632"
    if best_recovering.get("public_class") == "target_seeded":
        return "P944_TARGET_SEEDED_PAST_SUPPORT_RECOVERS_632"
    return "P944_COEFFICIENT_SEEDED_PAST_SUPPORT_RECOVERS_632"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    rows_by_window, artifact_summary = load_rows(args.p939_source)
    strategies = build_strategies()
    summaries = [evaluate_strategy(strategy, rows_by_window, include_rows=False) for strategy in strategies]
    baseline = next(item for item in summaries if item["strategy"] == "p943_exact_hash_transfer_mod4")
    recovering = [
        item
        for item in summaries
        if dirty_free(item) and int_value(item.get("target_632_clean_selected")) > 0
    ]
    recovering_sorted = sorted(recovering, key=rank_key, reverse=True)
    best_recovering = recovering_sorted[0] if recovering_sorted else None
    detailed_best = None
    if best_recovering:
        strategy = next(item for item in strategies if item.name == best_recovering["strategy"])
        detailed_best = evaluate_strategy(strategy, rows_by_window, include_rows=True)
    all_rows = [row for rows in rows_by_window.values() for row in rows]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p939_source": str(args.p939_source),
            "script": str(Path(__file__)),
        },
        "baseline": baseline,
        "best_recovering": detailed_best,
        "claim_status": determine_claim(baseline, best_recovering),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores normalized archive QR artifacts; no fresh 1160+ replay is claimed.",
            "PAST-TRAIN-ONLY: selectors use only rows from numerically earlier windows for each holdout.",
            "TRAIN-LABEL-AUDIT: support seeds use training preservation/below-rho labels but never heldout labels.",
            "SUPPORT-SEED-GRID: P944 searches a predeclared family of public relaxations; any winner must be frozen before forward promotion.",
            "RANK-SIGNAL-NOT-DESCENT: this does not prove full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is a public-factor selector component, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p944_past_support_seed",
        "parameters": {
            "hash_visible_row_count": len(all_rows),
            "hash_visible_window_count": len(rows_by_window),
            "source_window_count": len(artifact_summary),
            "strategy_count": len(strategies),
        },
        "schema": SCHEMA,
        "summary": {
            "artifact_summary": artifact_summary,
            "recovering_strategy_count": len(recovering),
            "rows_by_window_count": {window: len(rows) for window, rows in sorted(rows_by_window.items(), key=lambda item: window_start(item[0]))},
            "strategy_summaries": sorted(summaries, key=rank_key, reverse=True),
            "top_recovering": recovering_sorted[:10],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p939-source", type=Path, default=P939_SOURCE)
    return parser.parse_args()


def compact(result: dict[str, Any] | None) -> str:
    if not result:
        return "none"
    return (
        f"{result.get('strategy')}: selected={result.get('selected_count')} "
        f"clean={result.get('selected_clean_count')} false={result.get('false_positive_count')} "
        f"nonpres={result.get('non_preserving_count')} 632={result.get('target_632_clean_selected')}"
    )


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        f"claim={payload['claim_status']} "
        f"baseline={compact(payload.get('baseline'))} "
        f"best={compact(payload.get('best_recovering'))} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
