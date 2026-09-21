#!/usr/bin/env python3
"""P943 frozen validation for the P942 hash + transfer_mod4 selector."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tasks.ecdlp_index_calculus.low_term_total2_p942_hash_context_discriminator import (
    P939_SOURCE,
    context_key,
    int_value,
    load_rows,
    mean,
    now_iso,
    strategy_stats,
    summarize_selected,
    whitelist_from_stats,
    window_start,
    write_json,
)


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p943_frozen_hash_transfer_mod4_validation.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p943_frozen_hash_transfer_mod4_validation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p943_frozen_hash_transfer_mod4_validation.v1"
FROZEN_FEATURES = ("hash", "transfer_mod4")
FROZEN_MODE = "train_clean_all"
FROZEN_MIN_COUNT = 2


def sorted_windows(rows_by_window: dict[str, list[dict[str, Any]]]) -> list[str]:
    return sorted(rows_by_window, key=window_start)


def split_summary(selected: list[dict[str, Any]], holdout_rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarize_selected(selected, holdout_rows)
    return summary


def aggregate_result(name: str, split_results: list[dict[str, Any]], include_rows: bool) -> dict[str, Any]:
    all_selected = [
        row
        for split in split_results
        for holdout in split["holdouts"]
        for row in holdout.get("selected_rows", [])
    ]
    ops_holdouts = [
        holdout
        for split in split_results
        for holdout in split["holdouts"]
        if holdout.get("holdout_class") == "ops_rule_window"
    ]
    control_holdouts = [
        holdout
        for split in split_results
        for holdout in split["holdouts"]
        if holdout.get("holdout_class") != "ops_rule_window"
    ]
    ratios = [float(row["ratio"]) for row in all_selected if row.get("ratio") is not None]
    result = {
        "all_selected_clean": all(bool(row.get("clean")) for row in all_selected) if all_selected else False,
        "all_selected_preserve": all(bool(row.get("preserve")) for row in all_selected) if all_selected else False,
        "context_features": list(FROZEN_FEATURES),
        "control_holdouts_with_clean_selection": sum(1 for item in control_holdouts if int_value(item.get("selected_clean_count")) > 0),
        "control_holdouts_with_selection": sum(1 for item in control_holdouts if int_value(item.get("selected_count")) > 0),
        "control_window_count": len(control_holdouts),
        "false_positive_count": sum(int_value(item.get("false_positive_count")) for item in ops_holdouts + control_holdouts),
        "max_selected_ratio": max(ratios) if ratios else None,
        "mean_selected_ratio": mean(ratios),
        "min_count": FROZEN_MIN_COUNT,
        "min_selected_ratio": min(ratios) if ratios else None,
        "mode": FROZEN_MODE,
        "name": name,
        "non_preserving_count": sum(int_value(item.get("non_preserving_count")) for item in ops_holdouts + control_holdouts),
        "ops_holdouts_with_clean_selection": sum(1 for item in ops_holdouts if int_value(item.get("selected_clean_count")) > 0),
        "ops_holdouts_with_selection": sum(1 for item in ops_holdouts if int_value(item.get("selected_count")) > 0),
        "ops_window_count": len(ops_holdouts),
        "selected_clean_count": sum(int_value(item.get("selected_clean_count")) for item in ops_holdouts + control_holdouts),
        "selected_count": sum(int_value(item.get("selected_count")) for item in ops_holdouts + control_holdouts),
        "split_count": len(split_results),
        "windows_with_clean_selection": sum(1 for item in ops_holdouts + control_holdouts if int_value(item.get("selected_clean_count")) > 0),
        "windows_with_selection": sum(1 for item in ops_holdouts + control_holdouts if int_value(item.get("selected_count")) > 0),
    }
    if include_rows:
        result["splits"] = split_results
    else:
        slim_splits = []
        for split in split_results:
            split_copy = {key: value for key, value in split.items() if key != "holdouts"}
            holdouts = []
            for holdout in split["holdouts"]:
                holdout_copy = {key: value for key, value in holdout.items() if key != "selected_rows"}
                holdouts.append(holdout_copy)
            split_copy["holdouts"] = holdouts
            slim_splits.append(split_copy)
        result["splits"] = slim_splits
    return result


def evaluate_splits(
    name: str,
    split_items: list[dict[str, Any]],
    rows_by_window: dict[str, list[dict[str, Any]]],
    include_rows: bool = False,
    blocked_hash: str | None = None,
) -> dict[str, Any]:
    split_results: list[dict[str, Any]] = []
    for item in split_items:
        train_windows = list(item["train_windows"])
        test_windows = list(item["test_windows"])
        train_rows = [
            row
            for window in train_windows
            for row in rows_by_window.get(window, [])
            if blocked_hash is None or str(row.get("hash")) != blocked_hash
        ]
        stats = strategy_stats(train_rows, FROZEN_FEATURES)
        whitelist = whitelist_from_stats(stats, FROZEN_MODE, FROZEN_MIN_COUNT)
        holdouts: list[dict[str, Any]] = []
        for window in test_windows:
            holdout_rows = rows_by_window.get(window, [])
            selected = [
                row
                for row in holdout_rows
                if (blocked_hash is None or str(row.get("hash")) != blocked_hash)
                and context_key(row, FROZEN_FEATURES) in whitelist
            ]
            summary = {
                "holdout_class": holdout_rows[0].get("control_class") if holdout_rows else None,
                "holdout_window": window,
                **split_summary(selected, holdout_rows),
            }
            holdouts.append(summary)
        split_results.append(
            {
                "blocked_hash": blocked_hash,
                "split": item["name"],
                "test_windows": test_windows,
                "train_context_count": len(stats),
                "train_windows": train_windows,
                "whitelist_count": len(whitelist),
                "holdouts": holdouts,
            }
        )
    result = aggregate_result(name, split_results, include_rows=include_rows)
    if blocked_hash is not None:
        result["blocked_hash"] = blocked_hash
    return result


def leave_one_splits(windows: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "name": f"loo_{window}",
            "test_windows": [window],
            "train_windows": [other for other in windows if other != window],
        }
        for window in windows
    ]


def contiguous_folds(windows: list[str], fold_count: int) -> list[dict[str, Any]]:
    n = len(windows)
    base, extra = divmod(n, fold_count)
    folds: list[list[str]] = []
    start = 0
    for index in range(fold_count):
        size = base + (1 if index < extra else 0)
        folds.append(windows[start : start + size])
        start += size
    out: list[dict[str, Any]] = []
    for index, test_windows in enumerate(folds):
        train_windows = [window for window in windows if window not in test_windows]
        out.append(
            {
                "name": f"contiguous_{fold_count}fold_{index}",
                "test_windows": test_windows,
                "train_windows": train_windows,
            }
        )
    return out


def bucket_folds(windows: list[str], modulus: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for residue in range(modulus):
        test_windows = [window for window in windows if window_start(window) % modulus == residue]
        if not test_windows:
            continue
        train_windows = [window for window in windows if window not in test_windows]
        out.append(
            {
                "name": f"bucket_mod{modulus}_{residue}",
                "test_windows": test_windows,
                "train_windows": train_windows,
            }
        )
    return out


def rolling_past_splits(windows: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "name": f"past_to_{window}",
            "test_windows": [window],
            "train_windows": windows[:index],
        }
        for index, window in enumerate(windows)
    ]


def rolling_future_splits(windows: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "name": f"future_to_{window}",
            "test_windows": [window],
            "train_windows": windows[index + 1 :],
        }
        for index, window in enumerate(windows)
    ]


def selected_hashes(result: dict[str, Any]) -> list[str]:
    hashes: Counter[str] = Counter()
    for split in result.get("splits") or []:
        for holdout in split.get("holdouts") or []:
            for row in holdout.get("selected_rows") or []:
                hashes[str(row.get("hash"))] += 1
    return [hash_value for hash_value, _ in hashes.most_common()]


def is_zero_dirty(result: dict[str, Any]) -> bool:
    return int_value(result.get("false_positive_count")) == 0 and int_value(result.get("non_preserving_count")) == 0


def has_full_ops_clean(result: dict[str, Any]) -> bool:
    return int_value(result.get("ops_holdouts_with_clean_selection")) == int_value(result.get("ops_window_count"))


def determine_claim(results: dict[str, Any]) -> str:
    leave_one = results["leave_one_window"]
    split_checks = [
        value
        for key, value in results.items()
        if key.startswith("contiguous_") or key.startswith("bucket_") or key in {"rolling_past_only", "rolling_future_only"}
    ]
    if not is_zero_dirty(leave_one) or not has_full_ops_clean(leave_one):
        return "NEGATIVE_RESULT_P943_FROZEN_SELECTOR_FAILS_LEAVE_ONE_CONTROL"
    if any(not is_zero_dirty(result) for result in split_checks):
        return "NEGATIVE_RESULT_P943_FROZEN_SELECTOR_DIRTY_UNDER_SPLIT"
    if all(has_full_ops_clean(result) for result in split_checks):
        return "P943_FROZEN_HASH_TRANSFER_MOD4_SPLIT_STABLE"
    if any(has_full_ops_clean(result) for result in split_checks):
        return "P943_FROZEN_HASH_TRANSFER_MOD4_PRECISION_STABLE_PARTIAL_SPLIT_COVERAGE"
    return "P943_FROZEN_HASH_TRANSFER_MOD4_PRECISION_STABLE_LEAVE_ONE_ONLY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    rows_by_window, artifact_summary = load_rows(args.p939_source)
    windows = sorted_windows(rows_by_window)

    leave_one = evaluate_splits("leave_one_window", leave_one_splits(windows), rows_by_window, include_rows=True)
    hashes = selected_hashes(leave_one)
    ablations = {
        hash_value: evaluate_splits(
            f"leave_one_without_hash_{hash_value}",
            leave_one_splits(windows),
            rows_by_window,
            include_rows=False,
            blocked_hash=hash_value,
        )
        for hash_value in hashes
    }
    results: dict[str, Any] = {
        "leave_one_window": leave_one,
        "rolling_past_only": evaluate_splits("rolling_past_only", rolling_past_splits(windows), rows_by_window),
        "rolling_future_only": evaluate_splits("rolling_future_only", rolling_future_splits(windows), rows_by_window),
    }
    for fold_count in [2, 3, 4, 6]:
        results[f"contiguous_{fold_count}fold"] = evaluate_splits(
            f"contiguous_{fold_count}fold",
            contiguous_folds(windows, fold_count),
            rows_by_window,
        )
    for modulus in [3, 4, 5]:
        results[f"bucket_mod{modulus}"] = evaluate_splits(
            f"bucket_mod{modulus}",
            bucket_folds(windows, modulus),
            rows_by_window,
        )

    all_rows = [row for rows in rows_by_window.values() for row in rows]
    return {
        "ablation_results": ablations,
        "artifacts": {
            "contract": str(args.contract),
            "p939_source": str(args.p939_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(results),
        "created_at": now_iso(),
        "frozen_selector": {
            "context_features": list(FROZEN_FEATURES),
            "min_count": FROZEN_MIN_COUNT,
            "mode": FROZEN_MODE,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores normalized archive QR artifacts; no fresh 1160+ replay is claimed.",
            "FROZEN-SELECTOR-VALIDATION: P943 does not search context families; it evaluates P942's preselected hash + transfer_mod4 selector.",
            "TRAIN-LABEL-AUDIT: clean-context selectors use training preservation/below-rho labels but never heldout labels.",
            "SPLIT-COVERAGE-BOUNDARY: rolling or contiguous coverage loss is a support limitation, not a precision failure unless dirty rows are selected.",
            "RANK-SIGNAL-NOT-DESCENT: this does not prove full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is a public-factor selector component, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p943_frozen_hash_transfer_mod4_validation",
        "parameters": {
            "hash_visible_row_count": len(all_rows),
            "hash_visible_window_count": len(rows_by_window),
            "source_window_count": len(artifact_summary),
        },
        "schema": SCHEMA,
        "summary": {
            "artifact_summary": artifact_summary,
            "result_summaries": results,
            "selected_hashes_leave_one": hashes,
            "rows_by_window_count": {window: len(rows) for window, rows in sorted(rows_by_window.items(), key=lambda item: window_start(item[0]))},
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p939-source", type=Path, default=P939_SOURCE)
    return parser.parse_args()


def compact(result: dict[str, Any]) -> str:
    return (
        f"selected={result.get('selected_count')} clean={result.get('selected_clean_count')} "
        f"false={result.get('false_positive_count')} nonpres={result.get('non_preserving_count')} "
        f"ops_clean={result.get('ops_holdouts_with_clean_selection')}/{result.get('ops_window_count')}"
    )


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    results = payload["summary"]["result_summaries"]
    print(
        f"claim={payload['claim_status']} "
        f"leave_one={compact(results['leave_one_window'])} "
        f"contig2={compact(results['contiguous_2fold'])} "
        f"contig4={compact(results['contiguous_4fold'])} "
        f"past={compact(results['rolling_past_only'])} "
        f"future={compact(results['rolling_future_only'])} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
