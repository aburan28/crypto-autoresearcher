#!/usr/bin/env python3
"""P941 normalized holdout audit for public factor-hash banks."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p941_factor_hash_normalized_holdout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p941_factor_hash_normalized_holdout_probe.json"
P939_SOURCE = STATE_DIR / "low_term_total2_p939_ops_factor_zero_invariant_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p941_factor_hash_normalized_holdout.v1"


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


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 8)


def is_clean(row: dict[str, Any]) -> bool:
    return (
        bool(row.get("public_factor_quadratic_root_beats_rho"))
        and bool(row.get("quadratic_preserves_selected_root_pairs"))
        and not bool(row.get("chosen_false_positive_source"))
    )


def window_start(window: str) -> int:
    try:
        return int(str(window).split("_", 1)[0])
    except (TypeError, ValueError):
        return 10**9


def compact_row(row: dict[str, Any], window: str, control_class: str, best_policy: str, artifact: Path) -> dict[str, Any]:
    ratio_value = row.get("public_factor_quadratic_root_ops_over_rho")
    return {
        "artifact": str(artifact),
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
        "ratio": ratio_value,
        "row_key": row.get("row_key"),
        "surface_id": row.get("surface_id"),
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
        "window": window,
        "window_start": window_start(window),
    }


def artifact_candidates(window: str, record: dict[str, Any]) -> list[tuple[str, Path]]:
    candidates: list[tuple[str, Path]] = [
        (
            "p941_refresh",
            STATE_DIR / f"low_term_total2_ffe_public_factor_quadratic_root_fresh_{window}_expanded_p941_refresh_probe.json",
        ),
        (
            "p939_refresh",
            STATE_DIR / f"low_term_total2_ffe_public_factor_quadratic_root_fresh_{window}_expanded_p939_refresh_probe.json",
        ),
        (
            "regular",
            STATE_DIR / f"low_term_total2_ffe_public_factor_quadratic_root_fresh_{window}_expanded_probe.json",
        ),
    ]
    artifact = record.get("artifact")
    if artifact:
        candidates.append(("recorded", Path(str(artifact))))
    seen: set[Path] = set()
    unique: list[tuple[str, Path]] = []
    for label, path in candidates:
        if path not in seen:
            unique.append((label, path))
            seen.add(path)
    return unique


def load_window_rows(record: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    window = str(record.get("heldout_window"))
    control_class = str(record.get("control_class"))
    tried: list[str] = []
    for label, path in artifact_candidates(window, record):
        tried.append(str(path))
        if not path.exists():
            continue
        payload = load_json(path)
        best_policy = str((payload.get("summary") or {}).get("best_policy") or record.get("best_policy") or "")
        policy_rows = ((payload.get("policy_rows") or {}).get(best_policy) or [])
        rows = [
            compact_row(row, window, control_class, best_policy, path)
            for row in policy_rows
            if isinstance(row, dict) and row.get("selected_factor_hash")
        ]
        meta = {
            "artifact": str(path),
            "artifact_source": label,
            "best_policy": best_policy,
            "best_policy_row_count": len(policy_rows),
            "hash_visible_row_count": len(rows),
            "clean_hash_visible_row_count": sum(1 for row in rows if row.get("clean")),
            "control_class": control_class,
            "false_hash_visible_row_count": sum(1 for row in rows if row.get("false_positive")),
            "non_preserving_hash_visible_row_count": sum(1 for row in rows if not row.get("preserve")),
            "window": window,
        }
        return rows, meta
    return [], {
        "artifact": None,
        "artifact_source": None,
        "best_policy": record.get("best_policy"),
        "best_policy_row_count": 0,
        "clean_hash_visible_row_count": 0,
        "control_class": control_class,
        "false_hash_visible_row_count": 0,
        "hash_visible_row_count": 0,
        "non_preserving_hash_visible_row_count": 0,
        "tried": tried,
        "window": window,
    }


def hash_stats(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("hash"))].append(row)
    out: dict[str, dict[str, Any]] = {}
    for hash_value, items in sorted(grouped.items()):
        out[hash_value] = {
            "below_count": sum(1 for row in items if row.get("below_rho")),
            "clean_count": sum(1 for row in items if row.get("clean")),
            "control_classes": sorted({str(row.get("control_class")) for row in items}),
            "count": len(items),
            "false_count": sum(1 for row in items if row.get("false_positive")),
            "mean_ratio": mean([float(row["ratio"]) for row in items if row.get("ratio") is not None]),
            "preserve_count": sum(1 for row in items if row.get("preserve")),
            "targets": sorted({str(row.get("target")) for row in items}),
            "windows": sorted({str(row.get("window")) for row in items}, key=window_start),
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
    ratios = [float(row["ratio"]) for row in selected if row.get("ratio") is not None]
    return {
        "below_rho_count": sum(1 for row in selected if row.get("below_rho")),
        "clean_holdout_count": len(clean_holdout),
        "clean_recall": ratio(len(selected_clean), len(clean_holdout)) if clean_holdout else None,
        "false_positive_count": sum(1 for row in selected if row.get("false_positive")),
        "max_ratio": max(ratios) if ratios else None,
        "mean_ratio": mean(ratios),
        "min_ratio": min(ratios) if ratios else None,
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
    for window in sorted(rows_by_window, key=window_start):
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
    control_holdouts = [item for item in holdouts if item.get("holdout_class") != "ops_rule_window"]
    ratios = [float(row["ratio"]) for row in all_selected if row.get("ratio") is not None]
    return {
        "all_selected_below_rho": all(bool(row.get("below_rho")) for row in all_selected) if all_selected else False,
        "all_selected_clean": all(bool(row.get("clean")) for row in all_selected) if all_selected else False,
        "all_selected_preserve": all(bool(row.get("preserve")) for row in all_selected) if all_selected else False,
        "control_holdouts_with_selection": sum(1 for item in control_holdouts if int_value(item.get("selected_count")) > 0),
        "control_window_count": len(control_holdouts),
        "false_positive_count": sum(int_value(item.get("false_positive_count")) for item in holdouts),
        "holdouts": holdouts,
        "max_selected_ratio": max(ratios) if ratios else None,
        "mean_selected_ratio": mean(ratios),
        "min_selected_ratio": min(ratios) if ratios else None,
        "non_preserving_count": sum(int_value(item.get("non_preserving_count")) for item in holdouts),
        "ops_holdouts_with_selection": sum(1 for item in ops_holdouts if int_value(item.get("selected_count")) > 0),
        "ops_window_count": len(ops_holdouts),
        "selected_clean_count": sum(int_value(item.get("selected_clean_count")) for item in holdouts),
        "selected_count": sum(int_value(item.get("selected_count")) for item in holdouts),
        "strategy": name,
        "windows_with_selection": sum(1 for item in holdouts if int_value(item.get("selected_count")) > 0),
    }


def strategy_has_dirty_selection(summary: dict[str, Any]) -> bool:
    return int_value(summary.get("false_positive_count")) > 0 or int_value(summary.get("non_preserving_count")) > 0


def determine_claim(strategy_summaries: dict[str, dict[str, Any]]) -> str:
    repeated = strategy_summaries.get("train_clean_count_ge2_all_clean") or {}
    singleton = strategy_summaries.get("train_clean_count_ge1_all_clean") or {}
    unlabeled = strategy_summaries.get("train_repeat_count_ge2_unlabeled") or {}
    if strategy_has_dirty_selection(repeated):
        return "NEGATIVE_RESULT_P941_REPEATED_CLEAN_HASH_BANK_DIRTY_AFTER_NORMALIZATION"
    if strategy_has_dirty_selection(singleton):
        return "NEGATIVE_RESULT_P941_SINGLETON_CLEAN_HASH_BANK_DIRTY_AFTER_NORMALIZATION"
    if (
        repeated.get("all_selected_clean")
        and int_value(repeated.get("ops_holdouts_with_selection")) == int_value(repeated.get("ops_window_count"))
        and int_value(repeated.get("selected_count")) > 0
    ):
        return "P941_REPEATED_CLEAN_HASH_BANK_SELECTS_ALL_OPS_HOLDOUTS_AFTER_NORMALIZATION"
    if (
        singleton.get("all_selected_clean")
        and int_value(singleton.get("ops_holdouts_with_selection")) == int_value(singleton.get("ops_window_count"))
        and int_value(singleton.get("selected_count")) > 0
    ):
        return "P941_SINGLETON_HASH_BANK_SURVIVES_NORMALIZED_CONTROLS"
    if repeated.get("all_selected_clean") and int_value(repeated.get("selected_count")) > 0:
        return "P941_REPEATED_CLEAN_HASH_BANK_PARTIAL_CLEAN_COVERAGE_AFTER_NORMALIZATION"
    if singleton.get("all_selected_clean") and int_value(singleton.get("selected_count")) > 0:
        return "P941_SINGLETON_HASH_BANK_PARTIAL_CLEAN_COVERAGE_AFTER_NORMALIZATION"
    if strategy_has_dirty_selection(unlabeled):
        return "NEGATIVE_RESULT_P941_UNLABELED_REPEAT_HASH_BANK_DIRTY_AFTER_NORMALIZATION"
    return "NEGATIVE_RESULT_P941_HASH_BANK_NO_USEFUL_HOLDOUT_SELECTION_AFTER_NORMALIZATION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p939 = load_json(args.p939_source)
    records = (p939.get("summary") or {}).get("window_records") or []
    rows_by_window: dict[str, list[dict[str, Any]]] = {}
    artifact_summary: dict[str, dict[str, Any]] = {}
    skipped_windows: dict[str, str] = {}
    for record in sorted(records, key=lambda item: window_start(str(item.get("heldout_window")))):
        window = str(record.get("heldout_window"))
        rows, meta = load_window_rows(record)
        artifact_summary[window] = meta
        if rows:
            rows_by_window[window] = rows
        elif meta.get("artifact"):
            skipped_windows[window] = "artifact has no selected_factor_hash rows"
        else:
            skipped_windows[window] = "no artifact found"
    all_rows = [row for rows in rows_by_window.values() for row in rows]
    strategy_summaries = {name: evaluate_strategy(name, rows_by_window) for name in STRATEGIES}
    hash_visible_ops = sorted(
        [window for window, rows in rows_by_window.items() if rows and rows[0].get("control_class") == "ops_rule_window"],
        key=window_start,
    )
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
            "ARCHIVE-SCOUT: this scores normalized archive QR artifacts; no fresh 1160+ replay is claimed.",
            "NORMALIZED-HASH-SCOPE: P941 refresh artifacts are preferred, then P939 refresh artifacts, then regular QR artifacts.",
            "TRAIN-LABEL-AUDIT: clean-hash strategies use training preservation/below-rho labels but never heldout labels.",
            "UNLABELED-COUNT-CONTROL: repeat-count strategies use only train hash multiplicity.",
            "RANK-SIGNAL-NOT-DESCENT: this does not prove full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is a public-factor selector component, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p941_factor_hash_normalized_holdout",
        "parameters": {
            "hash_visible_ops_windows": hash_visible_ops,
            "hash_visible_window_count": len(rows_by_window),
            "source_record_count": len(records),
            "strategy_names": list(STRATEGIES),
            "skipped_windows": skipped_windows,
        },
        "schema": SCHEMA,
        "summary": {
            "artifact_summary": artifact_summary,
            "control_window_count": sum(
                1 for rows in rows_by_window.values() if rows and rows[0].get("control_class") != "ops_rule_window"
            ),
            "hash_visible_row_count": len(all_rows),
            "ops_window_count": len(hash_visible_ops),
            "rows_by_window_count": {window: len(rows) for window, rows in sorted(rows_by_window.items(), key=lambda item: window_start(item[0]))},
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
            "{name}:selected={selected},clean={clean},false={false},nonpres={nonpres},ops={ops}/{ops_total},all_clean={all_clean}".format(
                name=name,
                selected=summary.get("selected_count"),
                clean=summary.get("selected_clean_count"),
                false=summary.get("false_positive_count"),
                nonpres=summary.get("non_preserving_count"),
                ops=summary.get("ops_holdouts_with_selection"),
                ops_total=summary.get("ops_window_count"),
                all_clean=summary.get("all_selected_clean"),
            )
        )
    params = payload.get("parameters") or {}
    print(
        f"claim={payload['claim_status']} "
        + f"hash_visible_windows={params.get('hash_visible_window_count')}/{params.get('source_record_count')} "
        + " | ".join(parts)
        + f" out={args.out}"
    )


if __name__ == "__main__":
    main()
