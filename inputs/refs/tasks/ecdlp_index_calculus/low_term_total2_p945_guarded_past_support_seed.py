#!/usr/bin/env python3
"""P945 guarded rolling-past support seeding after the P944 unguarded failure."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tasks.ecdlp_index_calculus.low_term_total2_p942_hash_context_discriminator import (
    P939_SOURCE,
    int_value,
    load_rows,
    mean,
    now_iso,
    summarize_selected,
    window_start,
    write_json,
)
from tasks.ecdlp_index_calculus.low_term_total2_p944_past_support_seed import (
    Strategy,
    build_strategies,
    selected_by_strategy,
)


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p945_guarded_past_support_seed.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p945_guarded_past_support_seed_probe.json"
SCHEMA = "ecdlp.low_term_total2_p945_guarded_past_support_seed.v1"


@dataclass(frozen=True)
class Guard:
    name: str
    predicate: Callable[[dict[str, Any]], bool]
    specificity: str


def mod_guard(modulus: int, residue: int) -> Guard:
    return Guard(
        name=f"holdout_transfer_mod{modulus}_eq_{residue}",
        predicate=lambda row, modulus=modulus, residue=residue: row.get("transfer_index") is not None
        and int(row["transfer_index"]) % modulus == residue,
        specificity="coarse_public",
    )


def build_guards() -> list[Guard]:
    guards: list[Guard] = [
        Guard("none", lambda row: True, "unguarded_control"),
        mod_guard(4, 0),
        mod_guard(4, 1),
        mod_guard(4, 2),
        mod_guard(4, 3),
        mod_guard(2, 0),
        mod_guard(2, 1),
        Guard(
            "holdout_transfer_mod4_eq_0_and_target_22050_cf1",
            lambda row: row.get("transfer_index") is not None
            and int(row["transfer_index"]) % 4 == 0
            and row.get("target_label") == "22050.cf1",
            "exact_target_public",
        ),
        Guard(
            "holdout_transfer_mod4_eq_0_and_target_prime_11731",
            lambda row: row.get("transfer_index") is not None
            and int(row["transfer_index"]) % 4 == 0
            and row.get("target_prime") == 11731,
            "exact_target_public",
        ),
    ]
    return guards


def selected_rows_for_window(
    holdout_rows: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    strategy: Strategy,
    guard: Guard,
) -> list[dict[str, Any]]:
    return [
        row
        for row in holdout_rows
        if guard.predicate(row) and selected_by_strategy(row, train_rows, strategy)
    ]


def sorted_windows(rows_by_window: dict[str, list[dict[str, Any]]]) -> list[str]:
    return sorted(rows_by_window, key=window_start)


def evaluate(strategy: Strategy, guard: Guard, rows_by_window: dict[str, list[dict[str, Any]]], include_rows: bool = False) -> dict[str, Any]:
    windows = sorted_windows(rows_by_window)
    holdouts: list[dict[str, Any]] = []
    all_selected: list[dict[str, Any]] = []
    for index, window in enumerate(windows):
        train_windows = windows[:index]
        train_rows = [row for train_window in train_windows for row in rows_by_window[train_window]]
        holdout_rows = rows_by_window[window]
        selected = selected_rows_for_window(holdout_rows, train_rows, strategy, guard)
        all_selected.extend(selected)
        summary = {
            "guard": guard.name,
            "holdout_class": holdout_rows[0].get("control_class") if holdout_rows else None,
            "holdout_window": window,
            "strategy": strategy.name,
            "train_row_count": len(train_rows),
            "train_window_count": len(train_windows),
            **summarize_selected(selected, holdout_rows),
        }
        if not include_rows:
            summary.pop("selected_rows", None)
        holdouts.append(summary)
    ops_holdouts = [item for item in holdouts if item.get("holdout_class") == "ops_rule_window"]
    ratios = [float(row["ratio"]) for row in all_selected if row.get("ratio") is not None]
    target_632 = next((item for item in holdouts if item.get("holdout_window") == "632_639"), {})
    return {
        "all_selected_clean": all(bool(row.get("clean")) for row in all_selected) if all_selected else False,
        "all_selected_preserve": all(bool(row.get("preserve")) for row in all_selected) if all_selected else False,
        "base_public_class": strategy.public_class,
        "features": list(strategy.features),
        "false_positive_count": sum(int_value(item.get("false_positive_count")) for item in holdouts),
        "guard": guard.name,
        "guard_specificity": guard.specificity,
        "holdouts": holdouts,
        "max_selected_ratio": max(ratios) if ratios else None,
        "mean_selected_ratio": mean(ratios),
        "min_clean_count": strategy.min_clean_count,
        "min_selected_ratio": min(ratios) if ratios else None,
        "non_preserving_count": sum(int_value(item.get("non_preserving_count")) for item in holdouts),
        "ops_holdouts_with_clean_selection": sum(1 for item in ops_holdouts if int_value(item.get("selected_clean_count")) > 0),
        "ops_window_count": len(ops_holdouts),
        "selected_clean_count": sum(int_value(item.get("selected_clean_count")) for item in holdouts),
        "selected_count": sum(int_value(item.get("selected_count")) for item in holdouts),
        "strategy": strategy.name,
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
        result.get("guard_specificity") == "coarse_public",
        result.get("base_public_class") == "hash_seeded",
        int_value(result.get("target_632_clean_selected")),
        int_value(result.get("selected_clean_count")),
        -int_value(result.get("selected_count")),
        result.get("strategy", ""),
        result.get("guard", ""),
    )


def base_strategy_subset() -> list[Strategy]:
    wanted = {
        "same_hash_any_transfer",
        "same_hash_transfer_mod2",
        "same_hash_transfer_mod4_radius2",
        "same_target_transfer_mod4",
        "same_target_policy_head_transfer_mod4",
        "same_target_transfer_mod2",
        "target_coeffsum4_transfer_mod4",
        "target_constant4_b4_transfer_mod4",
    }
    return [strategy for strategy in build_strategies() if strategy.name in wanted]


def determine_claim(best: dict[str, Any] | None) -> str:
    if best is None:
        return "NEGATIVE_RESULT_P945_NO_GUARDED_PAST_SUPPORT_RECOVERY"
    if best.get("guard_specificity") == "coarse_public" and best.get("base_public_class") == "hash_seeded":
        return "P945_COARSE_GUARDED_HASH_SUPPORT_RECOVERS_632_PAST_ONLY"
    if best.get("guard_specificity") == "coarse_public":
        return "P945_COARSE_GUARDED_TARGET_SUPPORT_RECOVERS_632_PAST_ONLY"
    return "P945_EXACT_TARGET_GUARD_RECOVERS_632_PAST_ONLY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    rows_by_window, artifact_summary = load_rows(args.p939_source)
    strategies = base_strategy_subset()
    guards = build_guards()
    summaries = [
        evaluate(strategy, guard, rows_by_window, include_rows=False)
        for strategy in strategies
        for guard in guards
    ]
    recovering = [
        item
        for item in summaries
        if dirty_free(item) and int_value(item.get("target_632_clean_selected")) > 0
    ]
    recovering_sorted = sorted(recovering, key=rank_key, reverse=True)
    best = recovering_sorted[0] if recovering_sorted else None
    detailed_best = None
    if best:
        strategy = next(item for item in strategies if item.name == best["strategy"])
        guard = next(item for item in guards if item.name == best["guard"])
        detailed_best = evaluate(strategy, guard, rows_by_window, include_rows=True)
    all_rows = [row for rows in rows_by_window.values() for row in rows]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p939_source": str(args.p939_source),
            "script": str(Path(__file__)),
        },
        "best_recovering": detailed_best,
        "claim_status": determine_claim(best),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores normalized archive QR artifacts; no fresh 1160+ replay is claimed.",
            "PAST-TRAIN-ONLY: selectors use only rows from numerically earlier windows for each holdout.",
            "TRAIN-LABEL-AUDIT: support seeds use training preservation/below-rho labels but never heldout labels.",
            "GUARD-GRID: P945 searches predeclared destination guards over P944 recovering families; any winner must be frozen before forward promotion.",
            "RANK-SIGNAL-NOT-DESCENT: this does not prove full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is a public-factor selector component, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p945_guarded_past_support_seed",
        "parameters": {
            "guard_count": len(guards),
            "hash_visible_row_count": len(all_rows),
            "hash_visible_window_count": len(rows_by_window),
            "source_window_count": len(artifact_summary),
            "strategy_count": len(strategies),
            "strategy_guard_count": len(summaries),
        },
        "schema": SCHEMA,
        "summary": {
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
        f"{result.get('strategy')}+{result.get('guard')}: selected={result.get('selected_count')} "
        f"clean={result.get('selected_clean_count')} false={result.get('false_positive_count')} "
        f"nonpres={result.get('non_preserving_count')} 632={result.get('target_632_clean_selected')}"
    )


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(f"claim={payload['claim_status']} best={compact(payload.get('best_recovering'))} out={args.out}")


if __name__ == "__main__":
    main()
