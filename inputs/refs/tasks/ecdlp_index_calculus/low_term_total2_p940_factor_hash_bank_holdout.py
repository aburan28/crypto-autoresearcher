#!/usr/bin/env python3
"""P940 train/test audit for clean public factor-hash banks."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p940_factor_hash_bank_holdout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p940_factor_hash_bank_holdout_probe.json"
P939_SOURCE = STATE_DIR / "low_term_total2_p939_ops_factor_zero_invariant_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p940_factor_hash_bank_holdout.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(num: int | float, den: int | float) -> float | None:
    if den == 0:
        return None
    return round(float(num) / float(den), 8)


def is_clean(row: dict[str, Any]) -> bool:
    return (
        bool(row.get("public_factor_quadratic_root_beats_rho"))
        and bool(row.get("quadratic_preserves_selected_root_pairs"))
        and not bool(row.get("chosen_false_positive_source"))
    )


def compact_row(row: dict[str, Any], window: str, control_class: str, best_policy: str) -> dict[str, Any]:
    return {
        "below_rho": bool(row.get("public_factor_quadratic_root_beats_rho")),
        "clean": is_clean(row),
        "coefficients": row.get("selected_factor_coefficients"),
        "control_class": control_class,
        "false_positive": bool(row.get("chosen_false_positive_source")),
        "factor_index": (row.get("chosen_candidate") or {}).get("factor_index"),
        "factor_monomials": (row.get("chosen_candidate") or {}).get("factor_monomials"),
        "factor_total_degree": (row.get("chosen_candidate") or {}).get("factor_total_degree"),
        "hash": row.get("selected_factor_hash"),
        "policy": best_policy,
        "preserve": bool(row.get("quadratic_preserves_selected_root_pairs")),
        "ratio": row.get("public_factor_quadratic_root_ops_over_rho"),
        "row_key": row.get("row_key"),
        "surface_id": row.get("surface_id"),
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
        "window": window,
    }


def load_window_rows(record: dict[str, Any]) -> list[dict[str, Any]]:
    artifact = record.get("artifact")
    if not artifact:
        return []
    path = Path(str(artifact))
    if not path.exists():
        return []
    payload = load_json(path)
    best_policy = str((payload.get("summary") or {}).get("best_policy") or record.get("best_policy") or "")
    rows = ((payload.get("policy_rows") or {}).get(best_policy) or [])
    window = str(record.get("heldout_window"))
    control_class = str(record.get("control_class"))
    return [
        compact_row(row, window, control_class, best_policy)
        for row in rows
        if isinstance(row, dict) and row.get("selected_factor_hash")
    ]


def hash_stats(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("hash"))].append(row)
    out: dict[str, dict[str, Any]] = {}
    for hash_value, items in sorted(grouped.items()):
        out[hash_value] = {
            "clean_count": sum(1 for row in items if row.get("clean")),
            "count": len(items),
            "false_count": sum(1 for row in items if row.get("false_positive")),
            "preserve_count": sum(1 for row in items if row.get("preserve")),
            "below_count": sum(1 for row in items if row.get("below_rho")),
            "targets": sorted({str(row.get("target")) for row in items}),
            "windows": sorted({str(row.get("window")) for row in items}),
        }
    return out


def whitelist_clean_all(min_clean_count: int) -> Callable[[list[dict[str, Any]]], set[str]]:
    def selector(train_rows: list[dict[str, Any]]) -> set[str]:
        stats = hash_stats(train_rows)
        return {
            hash_value
            for hash_value, stat in stats.items()
            if int_value(stat.get("clean_count")) >= min_clean_count
            and int_value(stat.get("clean_count")) == int_value(stat.get("count"))
        }

    return selector


def whitelist_unlabeled_repeat(min_count: int) -> Callable[[list[dict[str, Any]]], set[str]]:
    def selector(train_rows: list[dict[str, Any]]) -> set[str]:
        stats = hash_stats(train_rows)
        return {
            hash_value
            for hash_value, stat in stats.items()
            if int_value(stat.get("count")) >= min_count
        }

    return selector


STRATEGIES: dict[str, Callable[[list[dict[str, Any]]], set[str]]] = {
    "train_clean_count_ge1_all_clean": whitelist_clean_all(1),
    "train_clean_count_ge2_all_clean": whitelist_clean_all(2),
    "train_clean_count_ge3_all_clean": whitelist_clean_all(3),
    "train_repeat_count_ge2_unlabeled": whitelist_unlabeled_repeat(2),
    "train_repeat_count_ge3_unlabeled": whitelist_unlabeled_repeat(3),
}


def summarize_selected(selected: list[dict[str, Any]], holdout_rows: list[dict[str, Any]]) -> dict[str, Any]:
    clean_holdout = [row for row in holdout_rows if row.get("clean")]
    selected_clean = [row for row in selected if row.get("clean")]
    return {
        "below_rho_count": sum(1 for row in selected if row.get("below_rho")),
        "clean_holdout_count": len(clean_holdout),
        "clean_recall": ratio(len(selected_clean), len(clean_holdout)) if clean_holdout else None,
        "false_positive_count": sum(1 for row in selected if row.get("false_positive")),
        "non_preserving_count": sum(1 for row in selected if not row.get("preserve")),
        "preserve_count": sum(1 for row in selected if row.get("preserve")),
        "selected_clean_count": len(selected_clean),
        "selected_count": len(selected),
        "selected_hashes": sorted({str(row.get("hash")) for row in selected}),
        "selected_rows": selected,
    }


def evaluate_strategy(name: str, rows_by_window: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    selector = STRATEGIES[name]
    holdouts: list[dict[str, Any]] = []
    all_selected: list[dict[str, Any]] = []
    for window in sorted(rows_by_window):
        holdout_rows = rows_by_window[window]
        train_rows = [
            row
            for other_window, rows in rows_by_window.items()
            if other_window != window
            for row in rows
        ]
        whitelist = selector(train_rows)
        selected = [row for row in holdout_rows if str(row.get("hash")) in whitelist]
        all_selected.extend(selected)
        holdouts.append(
            {
                "holdout_window": window,
                "holdout_class": holdout_rows[0].get("control_class") if holdout_rows else None,
                "train_hash_count": len(hash_stats(train_rows)),
                "whitelist": sorted(whitelist),
                **summarize_selected(selected, holdout_rows),
            }
        )
    ops_holdouts = [item for item in holdouts if item.get("holdout_class") == "ops_rule_window"]
    return {
        "all_selected_below_rho": all(bool(row.get("below_rho")) for row in all_selected) if all_selected else False,
        "all_selected_clean": all(bool(row.get("clean")) for row in all_selected) if all_selected else False,
        "all_selected_preserve": all(bool(row.get("preserve")) for row in all_selected) if all_selected else False,
        "false_positive_count": sum(int_value(item.get("false_positive_count")) for item in holdouts),
        "holdouts": holdouts,
        "non_preserving_count": sum(int_value(item.get("non_preserving_count")) for item in holdouts),
        "ops_holdouts_with_selection": sum(1 for item in ops_holdouts if int_value(item.get("selected_count")) > 0),
        "ops_window_count": len(ops_holdouts),
        "selected_clean_count": sum(int_value(item.get("selected_clean_count")) for item in holdouts),
        "selected_count": sum(int_value(item.get("selected_count")) for item in holdouts),
        "strategy": name,
        "windows_with_selection": sum(1 for item in holdouts if int_value(item.get("selected_count")) > 0),
    }


def determine_claim(strategy_summaries: dict[str, dict[str, Any]]) -> str:
    repeated = strategy_summaries.get("train_clean_count_ge2_all_clean") or {}
    singleton = strategy_summaries.get("train_clean_count_ge1_all_clean") or {}
    if (
        repeated.get("all_selected_clean")
        and int_value(repeated.get("ops_holdouts_with_selection")) == int_value(repeated.get("ops_window_count"))
        and int_value(repeated.get("selected_count")) > 0
    ):
        return "P940_REPEATED_CLEAN_HASH_BANK_SELECTS_ALL_OPS_HOLDOUTS"
    if (
        singleton.get("all_selected_clean")
        and int_value(singleton.get("ops_holdouts_with_selection")) == int_value(singleton.get("ops_window_count"))
        and int_value(singleton.get("selected_count")) > 0
    ):
        return "P940_SINGLETON_ASSISTED_HASH_BANK_SELECTS_ALL_OPS_HOLDOUTS"
    if repeated.get("all_selected_clean") and int_value(repeated.get("selected_count")) > 0:
        return "P940_REPEATED_CLEAN_HASH_BANK_PARTIAL_CLEAN_COVERAGE"
    if any(int_value(summary.get("false_positive_count")) > 0 for summary in strategy_summaries.values()):
        return "NEGATIVE_RESULT_P940_HASH_BANK_SELECTS_FALSE_POSITIVES"
    return "NEGATIVE_RESULT_P940_HASH_BANK_NO_USEFUL_HOLDOUT_SELECTION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p939 = load_json(args.p939_source)
    records = (p939.get("summary") or {}).get("window_records") or []
    rows_by_window: dict[str, list[dict[str, Any]]] = {}
    skipped_windows: dict[str, str] = {}
    for record in records:
        window = str(record.get("heldout_window"))
        rows = load_window_rows(record)
        if rows:
            rows_by_window[window] = rows
        else:
            skipped_windows[window] = "no hash-visible best-policy rows"
    all_rows = [row for rows in rows_by_window.values() for row in rows]
    strategy_summaries = {name: evaluate_strategy(name, rows_by_window) for name in STRATEGIES}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p939_source": str(args.p939_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(strategy_summaries),
        "created_at": now_iso(),
        "hash_bank_global": hash_stats(all_rows),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores frozen P939 QR artifacts; no fresh 1160+ replay is claimed.",
            "HASH-VISIBLE-SUBSET: older QR artifacts without selected_factor_hash cannot participate.",
            "TRAIN-LABEL-AUDIT: clean-hash strategies use training preservation/below-rho labels but never heldout labels.",
            "UNLABELED-COUNT-CONTROL: repeat-count strategies use only train hash multiplicity.",
            "RANK-SIGNAL-NOT-DESCENT: this does not prove full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is a public-factor selector component, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p940_factor_hash_bank_holdout",
        "parameters": {
            "strategy_names": list(STRATEGIES),
            "hash_visible_window_count": len(rows_by_window),
            "skipped_windows": skipped_windows,
        },
        "schema": SCHEMA,
        "summary": {
            "row_count": len(all_rows),
            "rows_by_window_count": {window: len(rows) for window, rows in sorted(rows_by_window.items())},
            "strategy_summaries": strategy_summaries,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p939-source", type=Path, default=P939_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    parts = []
    for name in [
        "train_clean_count_ge1_all_clean",
        "train_clean_count_ge2_all_clean",
        "train_repeat_count_ge2_unlabeled",
    ]:
        summary = summaries.get(name) or {}
        parts.append(
            "{name}:selected={selected},clean={clean},false={false},ops={ops}/{ops_total},all_clean={all_clean}".format(
                name=name,
                selected=summary.get("selected_count"),
                clean=summary.get("selected_clean_count"),
                false=summary.get("false_positive_count"),
                ops=summary.get("ops_holdouts_with_selection"),
                ops_total=summary.get("ops_window_count"),
                all_clean=summary.get("all_selected_clean"),
            )
        )
    print(f"claim={payload['claim_status']} " + " | ".join(parts) + f" out={args.out}")


if __name__ == "__main__":
    main()
