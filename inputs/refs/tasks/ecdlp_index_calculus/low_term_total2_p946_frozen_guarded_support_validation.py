#!/usr/bin/env python3
"""P946 frozen validation for the P945 guarded support selector."""

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
    selected_by_strategy,
)


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p946_frozen_guarded_support_validation.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p946_frozen_guarded_support_validation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p946_frozen_guarded_support_validation.v1"

FROZEN_STRATEGY = Strategy(
    "same_hash_transfer_mod2",
    ("hash",),
    min_clean_count=2,
    transfer_modulus=2,
    transfer_radius=0,
)


def sorted_windows(rows_by_window: dict[str, list[dict[str, Any]]]) -> list[str]:
    return sorted(rows_by_window, key=window_start)


def guard(row: dict[str, Any]) -> bool:
    return row.get("transfer_index") is not None and int(row["transfer_index"]) % 2 == 0


def row_selected(
    row: dict[str, Any],
    train_rows: list[dict[str, Any]],
    blocked_hash: str | None = None,
) -> bool:
    if blocked_hash is not None and str(row.get("hash")) == blocked_hash:
        return False
    filtered_train = [
        train_row for train_row in train_rows if blocked_hash is None or str(train_row.get("hash")) != blocked_hash
    ]
    return guard(row) and selected_by_strategy(row, filtered_train, FROZEN_STRATEGY)


def aggregate(name: str, split_results: list[dict[str, Any]], include_rows: bool) -> dict[str, Any]:
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
        "control_holdouts_with_clean_selection": sum(1 for item in control_holdouts if int_value(item.get("selected_clean_count")) > 0),
        "control_window_count": len(control_holdouts),
        "false_positive_count": sum(int_value(item.get("false_positive_count")) for item in ops_holdouts + control_holdouts),
        "max_selected_ratio": max(ratios) if ratios else None,
        "mean_selected_ratio": mean(ratios),
        "min_selected_ratio": min(ratios) if ratios else None,
        "name": name,
        "non_preserving_count": sum(int_value(item.get("non_preserving_count")) for item in ops_holdouts + control_holdouts),
        "ops_holdouts_with_clean_selection": sum(1 for item in ops_holdouts if int_value(item.get("selected_clean_count")) > 0),
        "ops_window_count": len(ops_holdouts),
        "selected_clean_count": sum(int_value(item.get("selected_clean_count")) for item in ops_holdouts + control_holdouts),
        "selected_count": sum(int_value(item.get("selected_count")) for item in ops_holdouts + control_holdouts),
        "split_count": len(split_results),
        "target_632_clean_selected": sum(
            int_value(item.get("selected_clean_count")) for item in ops_holdouts if item.get("holdout_window") == "632_639"
        ),
        "target_632_selected": sum(
            int_value(item.get("selected_count")) for item in ops_holdouts if item.get("holdout_window") == "632_639"
        ),
        "windows_with_clean_selection": sum(1 for item in ops_holdouts + control_holdouts if int_value(item.get("selected_clean_count")) > 0),
    }
    if include_rows:
        result["splits"] = split_results
    else:
        slim: list[dict[str, Any]] = []
        for split in split_results:
            split_copy = {key: value for key, value in split.items() if key != "holdouts"}
            holdouts = []
            for holdout in split["holdouts"]:
                holdouts.append({key: value for key, value in holdout.items() if key != "selected_rows"})
            split_copy["holdouts"] = holdouts
            slim.append(split_copy)
        result["splits"] = slim
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
        train_rows = [row for window in item["train_windows"] for row in rows_by_window.get(window, [])]
        holdouts: list[dict[str, Any]] = []
        for window in item["test_windows"]:
            holdout_rows = rows_by_window.get(window, [])
            selected = [row for row in holdout_rows if row_selected(row, train_rows, blocked_hash=blocked_hash)]
            summary = {
                "blocked_hash": blocked_hash,
                "holdout_class": holdout_rows[0].get("control_class") if holdout_rows else None,
                "holdout_window": window,
                **summarize_selected(selected, holdout_rows),
            }
            holdouts.append(summary)
        split_results.append(
            {
                "blocked_hash": blocked_hash,
                "split": item["name"],
                "test_windows": item["test_windows"],
                "train_row_count": len(train_rows),
                "train_windows": item["train_windows"],
                "holdouts": holdouts,
            }
        )
    result = aggregate(name, split_results, include_rows=include_rows)
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


def contiguous_folds(windows: list[str], fold_count: int) -> list[dict[str, Any]]:
    n = len(windows)
    base, extra = divmod(n, fold_count)
    folds: list[list[str]] = []
    start = 0
    for index in range(fold_count):
        size = base + (1 if index < extra else 0)
        folds.append(windows[start : start + size])
        start += size
    return [
        {
            "name": f"contiguous_{fold_count}fold_{index}",
            "test_windows": test,
            "train_windows": [window for window in windows if window not in test],
        }
        for index, test in enumerate(folds)
    ]


def bucket_folds(windows: list[str], modulus: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for residue in range(modulus):
        test = [window for window in windows if window_start(window) % modulus == residue]
        if test:
            out.append(
                {
                    "name": f"bucket_mod{modulus}_{residue}",
                    "test_windows": test,
                    "train_windows": [window for window in windows if window not in test],
                }
            )
    return out


def selected_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for split in result.get("splits") or []
        for holdout in split.get("holdouts") or []
        for row in holdout.get("selected_rows") or []
    ]


def factor_bank_readiness(rows: list[dict[str, Any]]) -> dict[str, Any]:
    coeffs = [
        (row.get("constant"), row.get("b_coeff"), row.get("c_coeff"), row.get("term_count"))
        for row in rows
    ]
    hash_counts = Counter(str(row.get("hash")) for row in rows)
    coeff_counts = Counter(coeffs)
    target_counts = Counter(str(row.get("target")) for row in rows)
    window_counts = Counter(str(row.get("window")) for row in rows)
    return {
        "coefficient_tuple_count": len(coeff_counts),
        "coefficient_tuple_counts": {str(key): value for key, value in coeff_counts.most_common()},
        "factor_hash_count": len(hash_counts),
        "factor_hash_counts": dict(hash_counts.most_common()),
        "rank_boundary": "RANK_NOT_MEASURED: coefficient/hash diversity is a readiness proxy, not linear algebra rank or target descent.",
        "ready_for_rank_audit": len(rows) >= 2 and len(hash_counts) >= 2 and len(coeff_counts) >= 2,
        "selected_count": len(rows),
        "target_counts": dict(target_counts.most_common()),
        "window_counts": dict(window_counts.most_common()),
    }


def is_zero_dirty(result: dict[str, Any]) -> bool:
    return int_value(result.get("false_positive_count")) == 0 and int_value(result.get("non_preserving_count")) == 0


def determine_claim(results: dict[str, dict[str, Any]], readiness: dict[str, Any]) -> str:
    if not is_zero_dirty(results["rolling_past_only"]) or int_value(results["rolling_past_only"].get("target_632_clean_selected")) == 0:
        return "NEGATIVE_RESULT_P946_FROZEN_GUARD_FAILS_PAST_RECOVERY"
    split_results = [value for value in results.values() if value["name"] != "rolling_past_only"]
    if any(not is_zero_dirty(result) for result in split_results):
        return "NEGATIVE_RESULT_P946_FROZEN_GUARD_DIRTY_UNDER_SPLIT"
    if readiness.get("ready_for_rank_audit"):
        return "P946_FROZEN_GUARDED_SUPPORT_PRECISION_STABLE_WITH_FACTOR_BANK_SIGNAL"
    return "P946_FROZEN_GUARDED_SUPPORT_PRECISION_STABLE_NO_RANK_BANK_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    rows_by_window, artifact_summary = load_rows(args.p939_source)
    windows = sorted_windows(rows_by_window)
    results = {
        "rolling_past_only": evaluate_splits("rolling_past_only", rolling_past_splits(windows), rows_by_window, include_rows=True),
        "rolling_future_only": evaluate_splits("rolling_future_only", rolling_future_splits(windows), rows_by_window),
        "leave_one_window": evaluate_splits("leave_one_window", leave_one_splits(windows), rows_by_window),
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
    rolling_rows = selected_rows(results["rolling_past_only"])
    selected_hashes = sorted({str(row.get("hash")) for row in rolling_rows})
    ablations = {
        hash_value: evaluate_splits(
            f"rolling_past_without_hash_{hash_value}",
            rolling_past_splits(windows),
            rows_by_window,
            blocked_hash=hash_value,
        )
        for hash_value in selected_hashes
    }
    readiness = factor_bank_readiness(rolling_rows)
    all_rows = [row for rows in rows_by_window.values() for row in rows]
    return {
        "ablation_results": ablations,
        "artifacts": {
            "contract": str(args.contract),
            "p939_source": str(args.p939_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(results, readiness),
        "created_at": now_iso(),
        "factor_bank_readiness": readiness,
        "frozen_selector": {
            "guard": "holdout_transfer_mod2_eq_0",
            "strategy": FROZEN_STRATEGY.name,
            "support_features": list(FROZEN_STRATEGY.features),
            "support_transfer_modulus": FROZEN_STRATEGY.transfer_modulus,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores normalized archive QR artifacts; no fresh 1160+ replay is claimed.",
            "FROZEN-GUARD-VALIDATION: P946 does not search strategies or guards; it evaluates P945's selected rule.",
            "TRAIN-LABEL-AUDIT: support seeds use training preservation/below-rho labels but never heldout labels.",
            "RANK-READINESS-NOT-RANK: factor hash/coefficient diversity is a routing proxy, not matrix rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is a public-factor selector component, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p946_frozen_guarded_support_validation",
        "parameters": {
            "hash_visible_row_count": len(all_rows),
            "hash_visible_window_count": len(rows_by_window),
            "source_window_count": len(artifact_summary),
        },
        "schema": SCHEMA,
        "summary": {
            "artifact_summary": artifact_summary,
            "result_summaries": results,
            "rows_by_window_count": {window: len(rows) for window, rows in sorted(rows_by_window.items(), key=lambda item: window_start(item[0]))},
            "selected_hashes_rolling_past": selected_hashes,
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
        f"632={result.get('target_632_clean_selected')}"
    )


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    results = payload["summary"]["result_summaries"]
    readiness = payload["factor_bank_readiness"]
    print(
        f"claim={payload['claim_status']} "
        f"past={compact(results['rolling_past_only'])} "
        f"leave_one={compact(results['leave_one_window'])} "
        f"contig2={compact(results['contiguous_2fold'])} "
        f"hashes={readiness['factor_hash_count']} coeffs={readiness['coefficient_tuple_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
