#!/usr/bin/env python3
"""P942 leave-one-window public context discriminator for factor hashes."""

from __future__ import annotations

import argparse
import itertools
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p942_hash_context_discriminator.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p942_hash_context_discriminator_probe.json"
P939_SOURCE = STATE_DIR / "low_term_total2_p939_ops_factor_zero_invariant_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p942_hash_context_discriminator.v1"


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


def window_start(window: str) -> int:
    try:
        return int(str(window).split("_", 1)[0])
    except (TypeError, ValueError):
        return 10**9


def parse_salt(row_key: Any) -> int | None:
    match = re.search(r"salt(\d+)", str(row_key or ""))
    if not match:
        return None
    return int(match.group(1))


def split_target(target: Any) -> tuple[str | None, int | None]:
    text = str(target or "")
    if "@" not in text:
        return (text or None, None)
    label, prime_text = text.rsplit("@", 1)
    try:
        prime = int(prime_text)
    except ValueError:
        prime = None
    return label, prime


def coefficient_tuple(coefficients: Any) -> tuple[int | None, int | None, int | None, int | None]:
    coeffs = coefficients if isinstance(coefficients, dict) else {}
    return (
        coeffs.get("constant"),
        coeffs.get("b_coeff"),
        coeffs.get("c_coeff"),
        coeffs.get("term_count"),
    )


def is_clean(row: dict[str, Any]) -> bool:
    return (
        bool(row.get("public_factor_quadratic_root_beats_rho"))
        and bool(row.get("quadratic_preserves_selected_root_pairs"))
        and not bool(row.get("chosen_false_positive_source"))
    )


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


def compact_row(row: dict[str, Any], window: str, control_class: str, best_policy: str, artifact: Path, source: str) -> dict[str, Any]:
    target_label, target_prime = split_target(row.get("target"))
    salt = parse_salt(row.get("row_key"))
    coeffs = row.get("selected_factor_coefficients")
    constant, b_coeff, c_coeff, term_count = coefficient_tuple(coeffs)
    factor_index = (row.get("chosen_candidate") or {}).get("factor_index")
    return {
        "artifact": str(artifact),
        "artifact_source": source,
        "below_rho": bool(row.get("public_factor_quadratic_root_beats_rho")),
        "b_coeff": b_coeff,
        "c_coeff": c_coeff,
        "clean": is_clean(row),
        "coefficients": coeffs,
        "constant": constant,
        "control_class": control_class,
        "false_positive": bool(row.get("chosen_false_positive_source")),
        "factor_index": factor_index,
        "factor_monomials": (row.get("chosen_candidate") or {}).get("factor_monomials"),
        "factor_total_degree": (row.get("chosen_candidate") or {}).get("factor_total_degree"),
        "hash": row.get("selected_factor_hash"),
        "policy": best_policy,
        "policy_head": best_policy.split("_", 1)[0] if best_policy else None,
        "preserve": bool(row.get("quadratic_preserves_selected_root_pairs")),
        "ratio": row.get("public_factor_quadratic_root_ops_over_rho"),
        "row_key": row.get("row_key"),
        "salt": salt,
        "surface_id": row.get("surface_id"),
        "target": row.get("target"),
        "target_label": target_label,
        "target_prime": target_prime,
        "term_count": term_count,
        "transfer_index": row.get("transfer_index"),
        "window": window,
        "window_start": window_start(window),
    }


def load_rows(p939_source: Path) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    p939 = load_json(p939_source)
    records = (p939.get("summary") or {}).get("window_records") or []
    rows_by_window: dict[str, list[dict[str, Any]]] = {}
    artifact_summary: dict[str, dict[str, Any]] = {}
    for record in sorted(records, key=lambda item: window_start(str(item.get("heldout_window")))):
        window = str(record.get("heldout_window"))
        control_class = str(record.get("control_class"))
        meta: dict[str, Any] = {
            "artifact": None,
            "artifact_source": None,
            "best_policy": None,
            "control_class": control_class,
            "hash_visible_row_count": 0,
            "window": window,
        }
        for source, path in artifact_candidates(window, record):
            if not path.exists():
                continue
            payload = load_json(path)
            best_policy = str((payload.get("summary") or {}).get("best_policy") or record.get("best_policy") or "")
            policy_rows = ((payload.get("policy_rows") or {}).get(best_policy) or [])
            rows = [
                compact_row(row, window, control_class, best_policy, path, source)
                for row in policy_rows
                if isinstance(row, dict) and row.get("selected_factor_hash")
            ]
            meta = {
                "artifact": str(path),
                "artifact_source": source,
                "best_policy": best_policy,
                "best_policy_row_count": len(policy_rows),
                "clean_hash_visible_row_count": sum(1 for row in rows if row.get("clean")),
                "control_class": control_class,
                "false_hash_visible_row_count": sum(1 for row in rows if row.get("false_positive")),
                "hash_visible_row_count": len(rows),
                "window": window,
            }
            if rows:
                rows_by_window[window] = rows
            break
        artifact_summary[window] = meta
    return rows_by_window, artifact_summary


def feature_value(row: dict[str, Any], name: str) -> Any:
    if name == "hash":
        return row.get("hash")
    if name in {"target", "target_label", "target_prime", "policy", "policy_head", "factor_index", "factor_total_degree", "factor_monomials", "constant", "b_coeff", "c_coeff", "term_count", "salt", "transfer_index", "window_start"}:
        return row.get(name)
    if name.startswith("salt_mod"):
        modulus = int(name.removeprefix("salt_mod"))
        salt = row.get("salt")
        return None if salt is None else int(salt) % modulus
    if name.startswith("transfer_mod"):
        modulus = int(name.removeprefix("transfer_mod"))
        transfer = row.get("transfer_index")
        return None if transfer is None else int(transfer) % modulus
    if name.startswith("factor_index_mod"):
        modulus = int(name.removeprefix("factor_index_mod"))
        factor_index = row.get("factor_index")
        return None if factor_index is None else int(factor_index) % modulus
    if name.startswith("constant_mod"):
        modulus = int(name.removeprefix("constant_mod"))
        constant = row.get("constant")
        return None if constant is None else int(constant) % modulus
    if name.startswith("b_coeff_mod"):
        modulus = int(name.removeprefix("b_coeff_mod"))
        b_coeff = row.get("b_coeff")
        return None if b_coeff is None else int(b_coeff) % modulus
    if name.startswith("coeff_sum_mod"):
        modulus = int(name.removeprefix("coeff_sum_mod"))
        values = [row.get("constant"), row.get("b_coeff"), row.get("c_coeff")]
        if any(value is None for value in values):
            return None
        return sum(int(value) for value in values) % modulus
    if name.startswith("window_mod"):
        modulus = int(name.removeprefix("window_mod"))
        return int(row.get("window_start")) % modulus
    raise KeyError(name)


def context_key(row: dict[str, Any], features: tuple[str, ...]) -> tuple[tuple[str, Any], ...] | None:
    pairs: list[tuple[str, Any]] = []
    for feature in features:
        value = feature_value(row, feature)
        if value is None:
            return None
        pairs.append((feature, value))
    return tuple(pairs)


def build_context_specs() -> list[tuple[str, ...]]:
    def add_spec(specs: set[tuple[str, ...]], features: tuple[str, ...]) -> None:
        if len(set(features)) == len(features):
            specs.add(features)

    coarse_single = [
        "target",
        "target_label",
        "target_prime",
        "policy",
        "policy_head",
        "factor_index",
        "factor_total_degree",
        "factor_monomials",
    ]
    mod_features = []
    for modulus in [2, 3, 4, 5, 7, 8, 11, 13, 16]:
        mod_features.extend(
            [
                f"salt_mod{modulus}",
                f"transfer_mod{modulus}",
                f"factor_index_mod{modulus}",
                f"constant_mod{modulus}",
                f"b_coeff_mod{modulus}",
                f"coeff_sum_mod{modulus}",
            ]
        )
    exact_features = ["salt", "transfer_index", "window_start", "constant", "b_coeff"]
    feature_pool = coarse_single + mod_features + exact_features

    specs: set[tuple[str, ...]] = {("hash",)}
    for feature in feature_pool:
        add_spec(specs, ("hash", feature))
    for feature in feature_pool:
        add_spec(specs, ("hash", "target", feature))
    focused = [
        "target",
        "policy",
        "policy_head",
        "factor_index",
        "salt_mod4",
        "salt_mod8",
        "salt_mod16",
        "transfer_mod4",
        "transfer_mod8",
        "transfer_mod16",
        "constant_mod8",
        "b_coeff_mod8",
        "coeff_sum_mod8",
    ]
    for left, right in itertools.combinations(focused, 2):
        add_spec(specs, ("hash", left, right))
        add_spec(specs, ("hash", "target", left, right))
    return sorted(specs, key=lambda item: (len(item), item))


def feature_specificity(features: tuple[str, ...]) -> str:
    exact = {"salt", "transfer_index", "window_start", "constant", "b_coeff"}
    if any(feature in exact for feature in features):
        return "exact_public"
    return "coarse_public"


def strategy_stats(train_rows: list[dict[str, Any]], features: tuple[str, ...]) -> dict[tuple[tuple[str, Any], ...], dict[str, int]]:
    stats: dict[tuple[tuple[str, Any], ...], dict[str, int]] = defaultdict(lambda: {"count": 0, "clean": 0, "false": 0, "non_preserving": 0})
    for row in train_rows:
        key = context_key(row, features)
        if key is None:
            continue
        stats[key]["count"] += 1
        if row.get("clean"):
            stats[key]["clean"] += 1
        if row.get("false_positive"):
            stats[key]["false"] += 1
        if not row.get("preserve"):
            stats[key]["non_preserving"] += 1
    return stats


def whitelist_from_stats(stats: dict[tuple[tuple[str, Any], ...], dict[str, int]], mode: str, min_count: int) -> set[tuple[tuple[str, Any], ...]]:
    if mode == "train_clean_all":
        return {
            key
            for key, stat in stats.items()
            if stat["clean"] >= min_count and stat["clean"] == stat["count"]
        }
    if mode == "unlabeled_repeat":
        return {key for key, stat in stats.items() if stat["count"] >= min_count}
    raise ValueError(mode)


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


def evaluate_spec(
    name: str,
    features: tuple[str, ...],
    mode: str,
    min_count: int,
    rows_by_window: dict[str, list[dict[str, Any]]],
    include_rows: bool = False,
) -> dict[str, Any]:
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
        stats = strategy_stats(train_rows, features)
        whitelist = whitelist_from_stats(stats, mode, min_count)
        selected = [row for row in holdout_rows if (context_key(row, features) in whitelist)]
        all_selected.extend(selected)
        summary = {
            "holdout_window": window,
            "holdout_class": holdout_rows[0].get("control_class") if holdout_rows else None,
            "train_context_count": len(stats),
            "whitelist_count": len(whitelist),
            **summarize_selected(selected, holdout_rows),
        }
        if not include_rows:
            summary.pop("selected_rows", None)
        holdouts.append(summary)
    ops_holdouts = [item for item in holdouts if item.get("holdout_class") == "ops_rule_window"]
    control_holdouts = [item for item in holdouts if item.get("holdout_class") != "ops_rule_window"]
    ratios = [float(row["ratio"]) for row in all_selected if row.get("ratio") is not None]
    return {
        "all_selected_below_rho": all(bool(row.get("below_rho")) for row in all_selected) if all_selected else False,
        "all_selected_clean": all(bool(row.get("clean")) for row in all_selected) if all_selected else False,
        "all_selected_preserve": all(bool(row.get("preserve")) for row in all_selected) if all_selected else False,
        "context_features": list(features),
        "context_name": name,
        "context_specificity": feature_specificity(features),
        "control_holdouts_with_clean_selection": sum(1 for item in control_holdouts if int_value(item.get("selected_clean_count")) > 0),
        "control_holdouts_with_selection": sum(1 for item in control_holdouts if int_value(item.get("selected_count")) > 0),
        "control_window_count": len(control_holdouts),
        "false_positive_count": sum(int_value(item.get("false_positive_count")) for item in holdouts),
        "holdouts": holdouts,
        "max_selected_ratio": max(ratios) if ratios else None,
        "mean_selected_ratio": mean(ratios),
        "min_count": min_count,
        "min_selected_ratio": min(ratios) if ratios else None,
        "mode": mode,
        "non_preserving_count": sum(int_value(item.get("non_preserving_count")) for item in holdouts),
        "ops_holdouts_with_clean_selection": sum(1 for item in ops_holdouts if int_value(item.get("selected_clean_count")) > 0),
        "ops_holdouts_with_selection": sum(1 for item in ops_holdouts if int_value(item.get("selected_count")) > 0),
        "ops_window_count": len(ops_holdouts),
        "selected_clean_count": sum(int_value(item.get("selected_clean_count")) for item in holdouts),
        "selected_count": sum(int_value(item.get("selected_count")) for item in holdouts),
        "strategy": f"{mode}_min{min_count}__{name}",
        "windows_with_clean_selection": sum(1 for item in holdouts if int_value(item.get("selected_clean_count")) > 0),
        "windows_with_selection": sum(1 for item in holdouts if int_value(item.get("selected_count")) > 0),
    }


def rank_key(summary: dict[str, Any]) -> tuple[Any, ...]:
    dirty = int_value(summary.get("false_positive_count")) + int_value(summary.get("non_preserving_count"))
    specificity_penalty = 1 if summary.get("context_specificity") == "exact_public" else 0
    return (
        dirty == 0,
        int_value(summary.get("ops_holdouts_with_clean_selection")) == int_value(summary.get("ops_window_count")),
        summary.get("context_specificity") == "coarse_public",
        int_value(summary.get("selected_clean_count")),
        int_value(summary.get("control_holdouts_with_clean_selection")),
        -int_value(summary.get("selected_count")),
        -specificity_penalty,
        -len(summary.get("context_features") or []),
        -int_value(summary.get("min_count")),
    )


def dirty_selected_rows(summary: dict[str, Any], rows_by_window: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    expanded = evaluate_spec(
        summary["context_name"],
        tuple(summary["context_features"]),
        summary["mode"],
        int_value(summary["min_count"]),
        rows_by_window,
        include_rows=True,
    )
    dirty: list[dict[str, Any]] = []
    for holdout in expanded["holdouts"]:
        for row in holdout.get("selected_rows") or []:
            if not row.get("clean"):
                dirty.append(row)
    return dirty


def determine_claim(best: dict[str, Any] | None, best_coarse: dict[str, Any] | None, baseline: dict[str, Any]) -> str:
    if best_coarse and int_value(best_coarse.get("ops_holdouts_with_clean_selection")) == int_value(best_coarse.get("ops_window_count")):
        return "P942_COARSE_PUBLIC_HASH_CONTEXT_REPAIRS_P941_PRECISION"
    if best and int_value(best.get("ops_holdouts_with_clean_selection")) == int_value(best.get("ops_window_count")):
        return "P942_EXACT_PUBLIC_HASH_CONTEXT_REPAIRS_P941_PRECISION"
    if best_coarse and int_value(best_coarse.get("selected_clean_count")) > 0:
        return "P942_COARSE_PUBLIC_HASH_CONTEXT_PARTIAL_PRECISION_REPAIR"
    if int_value(baseline.get("false_positive_count")) > 0:
        return "NEGATIVE_RESULT_P942_NO_FULL_PUBLIC_CONTEXT_REPAIR"
    return "NEGATIVE_RESULT_P942_NO_USEFUL_PUBLIC_CONTEXT_SELECTION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    rows_by_window, artifact_summary = load_rows(args.p939_source)
    specs = build_context_specs()
    summaries: list[dict[str, Any]] = []
    for features in specs:
        name = "__".join(features)
        for min_count in [1, 2, 3]:
            summaries.append(evaluate_spec(name, features, "train_clean_all", min_count, rows_by_window))
        if features == ("hash",) or len(features) <= 3:
            for min_count in [2, 3]:
                summaries.append(evaluate_spec(name, features, "unlabeled_repeat", min_count, rows_by_window))

    baseline = next(
        summary
        for summary in summaries
        if summary["mode"] == "train_clean_all"
        and summary["min_count"] == 2
        and tuple(summary["context_features"]) == ("hash",)
    )
    zero_dirty = [
        summary
        for summary in summaries
        if int_value(summary.get("selected_count")) > 0
        and int_value(summary.get("false_positive_count")) == 0
        and int_value(summary.get("non_preserving_count")) == 0
    ]
    zero_dirty_sorted = sorted(zero_dirty, key=rank_key, reverse=True)
    zero_dirty_coarse = [summary for summary in zero_dirty_sorted if summary.get("context_specificity") == "coarse_public"]
    best = zero_dirty_sorted[0] if zero_dirty_sorted else None
    best_coarse = zero_dirty_coarse[0] if zero_dirty_coarse else None
    dirty_sorted = sorted(
        [summary for summary in summaries if int_value(summary.get("selected_count")) > 0],
        key=rank_key,
        reverse=True,
    )

    detailed_best = None
    if best:
        detailed_best = evaluate_spec(
            best["context_name"],
            tuple(best["context_features"]),
            best["mode"],
            int_value(best["min_count"]),
            rows_by_window,
            include_rows=True,
        )
    detailed_best_coarse = None
    if best_coarse:
        detailed_best_coarse = evaluate_spec(
            best_coarse["context_name"],
            tuple(best_coarse["context_features"]),
            best_coarse["mode"],
            int_value(best_coarse["min_count"]),
            rows_by_window,
            include_rows=True,
        )

    all_rows = [row for rows in rows_by_window.values() for row in rows]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p939_source": str(args.p939_source),
            "script": str(Path(__file__)),
        },
        "baseline_hash_only_repeated_clean": baseline,
        "best_zero_dirty": detailed_best,
        "best_zero_dirty_coarse": detailed_best_coarse,
        "claim_status": determine_claim(best, best_coarse, baseline),
        "created_at": now_iso(),
        "dirty_rows_for_baseline": dirty_selected_rows(baseline, rows_by_window),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores normalized archive QR artifacts; no fresh 1160+ replay is claimed.",
            "TRAIN-LABEL-AUDIT: clean-context selectors use training preservation/below-rho labels but never heldout labels.",
            "PUBLIC-CONTEXT: tested tokens are row hash, target, factor, policy, coefficient, salt, transfer, and residue features already present in QR artifacts.",
            "EXACT-TOKEN-BOUNDARY: exact salt/transfer/window/coefficient contexts are reported separately from coarse public contexts.",
            "IN-SAMPLE-CONTEXT-SELECTION: the best context family is selected by a P942 grid over aggregate heldout outcomes; it must be frozen before split/forward validation.",
            "RANK-SIGNAL-NOT-DESCENT: this does not prove full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is a public-factor selector component, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p942_hash_context_discriminator",
        "parameters": {
            "context_spec_count": len(specs),
            "hash_visible_row_count": len(all_rows),
            "hash_visible_window_count": len(rows_by_window),
            "source_window_count": len(artifact_summary),
            "strategy_count": len(summaries),
        },
        "schema": SCHEMA,
        "summary": {
            "artifact_summary": artifact_summary,
            "rows_by_window_count": {window: len(rows) for window, rows in sorted(rows_by_window.items(), key=lambda item: window_start(item[0]))},
            "top_dirty_or_partial": dirty_sorted[:20],
            "top_zero_dirty": zero_dirty_sorted[:20],
            "top_zero_dirty_coarse": zero_dirty_coarse[:20],
            "zero_dirty_count": len(zero_dirty),
            "zero_dirty_coarse_count": len(zero_dirty_coarse),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p939-source", type=Path, default=P939_SOURCE)
    return parser.parse_args()


def compact_line(summary: dict[str, Any] | None) -> str:
    if not summary:
        return "none"
    return (
        f"{summary.get('strategy')}: selected={summary.get('selected_count')} "
        f"clean={summary.get('selected_clean_count')} false={summary.get('false_positive_count')} "
        f"nonpres={summary.get('non_preserving_count')} ops_clean="
        f"{summary.get('ops_holdouts_with_clean_selection')}/{summary.get('ops_window_count')} "
        f"specificity={summary.get('context_specificity')}"
    )


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        f"claim={payload['claim_status']} "
        f"baseline={compact_line(payload.get('baseline_hash_only_repeated_clean'))} "
        f"best_coarse={compact_line(payload.get('best_zero_dirty_coarse'))} "
        f"best={compact_line(payload.get('best_zero_dirty'))} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
