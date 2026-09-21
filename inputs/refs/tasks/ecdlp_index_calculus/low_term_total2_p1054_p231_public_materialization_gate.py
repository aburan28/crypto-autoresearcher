#!/usr/bin/env python3
"""P1054 public materialization gate for the accepted-factor bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1054_p231_public_materialization_gate.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1054_p231_public_materialization_gate_probe.json"
DEFAULT_FACTOR_GLOB = (
    "low_term_total2_factor_column_target_scout_target67_22050_multibranch_plus_priority_hash6_plus_direct_col15_lowterm_support5_*_probe.json"
)
DEFAULT_SELECTED_GLOB = (
    "low_term_total2_selected_leaf_term_support_scout_22050_col15_selector_expanded_*_probe.json"
)
SCHEMA = "ecdlp.low_term_total2_p1054_p231_public_materialization_gate.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_paths(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def window_from_name(path: Path) -> tuple[int, int] | None:
    match = re.search(r"_(\d+)_(\d+)_probe\.json$", path.name)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def split_for(start: int, train_min: int, train_max: int, gap_min: int, gap_max: int, forward_min: int) -> str | None:
    if train_min <= start <= train_max:
        return "calibration"
    if gap_min <= start <= gap_max:
        return "p1052_gap"
    if start >= forward_min:
        return "forward_validation"
    return None


def extract_salts(row_keys: list[Any]) -> list[int]:
    salts = []
    for row_key in row_keys:
        match = re.search(r"salt(\d+)", str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return salts


def selected_support(case: dict[str, Any]) -> set[int]:
    return {int_value(item) for item in case.get("selected_term_support") or []}


def selected_priority_hits(case: dict[str, Any]) -> set[int]:
    return {int_value(item) for item in case.get("priority_hits") or []}


def empty_source_features(window: str, start: int, end: int, split: str) -> dict[str, Any]:
    return {
        "case_count": 0,
        "diagnostic_direct_below_rho_count": 0,
        "diagnostic_direct_verified_count": 0,
        "diagnostic_shared_below_rho_count": 0,
        "diagnostic_shared_verified_count": 0,
        "has_source_family": False,
        "max_ops": None,
        "mean_ops": None,
        "min_ops": None,
        "op_range": None,
        "priority_count": 0,
        "salt_max": None,
        "salt_min": None,
        "salt_span": None,
        "split": split,
        "transfer_span": None,
        "unique_salts": 0,
        "window": window,
        "window_end": end,
        "window_start": start,
    }


def load_factor_labels(
    paths: list[Path],
    order: str,
    column: int,
    train_min: int,
    train_max: int,
    gap_min: int,
    gap_max: int,
    forward_min: int,
) -> dict[str, dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {}
    for path in paths:
        window = window_from_name(path)
        if window is None:
            continue
        start, end = window
        split = split_for(start, train_min, train_max, gap_min, gap_max, forward_min)
        if split is None:
            continue
        payload = load_json(path)
        order_report = (payload.get("order_reports") or {}).get(order) or {}
        for report in order_report.get("target_column_reports") or []:
            if int_value(report.get("column")) != column:
                continue
            support_counts = {
                "base_relation_support_count": int_value(report.get("base_relation_support_count")),
                "candidate_form_certificate_count": int_value(report.get("candidate_form_certificate_count")),
                "greedy_form_certificate_count": int_value(report.get("greedy_form_certificate_count")),
                "post_greedy_relation_support_count": int_value(report.get("post_greedy_relation_support_count")),
                "remaining_residual_support_count": int_value(report.get("remaining_residual_support_count")),
            }
            accepted_live_support = (
                support_counts["base_relation_support_count"]
                + support_counts["candidate_form_certificate_count"]
                + support_counts["greedy_form_certificate_count"]
                + support_counts["post_greedy_relation_support_count"]
            )
            window_key = f"{start}_{end}"
            labels[window_key] = {
                "accepted_live_support_count": accepted_live_support,
                "artifact": str(path),
                "is_materialized": accepted_live_support > 0,
                "split": split,
                "status": str(report.get("status")),
                "support_counts": support_counts,
                "window": window_key,
                "window_end": end,
                "window_start": start,
            }
    return labels


def load_source_features(
    paths: list[Path],
    target: str,
    selector: str,
    top_k: int,
    column: int,
    train_min: int,
    train_max: int,
    gap_min: int,
    gap_max: int,
    forward_min: int,
) -> dict[str, dict[str, Any]]:
    features: dict[str, dict[str, Any]] = {}
    for path in paths:
        window = window_from_name(path)
        if window is None:
            continue
        start, end = window
        split = split_for(start, train_min, train_max, gap_min, gap_max, forward_min)
        if split is None:
            continue
        payload = load_json(path)
        cases = []
        for case in payload.get("case_reports") or []:
            if not isinstance(case, dict):
                continue
            if str(case.get("target")) != target:
                continue
            if str(case.get("selector")) != selector:
                continue
            if int_value(case.get("top_k"), -1) != top_k:
                continue
            support = selected_support(case)
            priority_hits = selected_priority_hits(case)
            salts = extract_salts(case.get("row_keys") or [])
            direct_ops = float_value(case.get("direct_ops_over_rho"))
            shared_ops = float_value(case.get("shared_product_ops_over_rho"))
            cases.append(
                {
                    "direct_below": bool(case.get("direct_public_key_verified")) and direct_ops is not None and direct_ops < 1.0,
                    "direct_ops": direct_ops,
                    "direct_verified": bool(case.get("direct_public_key_verified")),
                    "priority": column in support or column in priority_hits,
                    "salts": salts,
                    "shared_below": bool(case.get("shared_product_public_key_verified")) and shared_ops is not None and shared_ops < 1.0,
                    "shared_ops": shared_ops,
                    "shared_verified": bool(case.get("shared_product_public_key_verified")),
                    "transfer_index": int_value(case.get("transfer_index")),
                }
            )
        if not cases:
            continue
        window_key = f"{start}_{end}"
        all_salts = [salt for case in cases for salt in case["salts"]]
        ops = [case["direct_ops"] for case in cases if case["direct_ops"] is not None]
        transfers = [case["transfer_index"] for case in cases]
        salt_min = min(all_salts) if all_salts else None
        salt_max = max(all_salts) if all_salts else None
        min_ops = min(ops) if ops else None
        max_ops = max(ops) if ops else None
        features[window_key] = {
            "case_count": len(cases),
            "diagnostic_direct_below_rho_count": sum(1 for case in cases if case["direct_below"]),
            "diagnostic_direct_verified_count": sum(1 for case in cases if case["direct_verified"]),
            "diagnostic_shared_below_rho_count": sum(1 for case in cases if case["shared_below"]),
            "diagnostic_shared_verified_count": sum(1 for case in cases if case["shared_verified"]),
            "has_source_family": True,
            "max_ops": max_ops,
            "mean_ops": mean(ops) if ops else None,
            "min_ops": min_ops,
            "op_range": max_ops - min_ops if min_ops is not None and max_ops is not None else None,
            "priority_count": sum(1 for case in cases if case["priority"]),
            "salt_max": salt_max,
            "salt_min": salt_min,
            "salt_span": salt_max - salt_min if salt_min is not None and salt_max is not None else None,
            "split": split,
            "transfer_span": max(transfers) - min(transfers) if transfers else None,
            "unique_salts": len(set(all_salts)),
            "window": window_key,
            "window_end": end,
            "window_start": start,
        }
    return features


def join_records(labels: dict[str, dict[str, Any]], source_features: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for window_key, label in labels.items():
        features = source_features.get(
            window_key,
            empty_source_features(window_key, label["window_start"], label["window_end"], label["split"]),
        )
        records.append({**features, **label})
    records.sort(key=lambda item: item["window_start"])
    return records


RuleFn = Callable[[dict[str, Any]], bool]


def cmp_value(value: Any, op: str, threshold: Any) -> bool:
    if value is None:
        return False
    if op == ">=":
        return value >= threshold
    if op == "<=":
        return value <= threshold
    if op == "==":
        return value == threshold
    raise ValueError(op)


def condition_rule(feature: str, op: str, threshold: Any) -> tuple[str, RuleFn]:
    if isinstance(threshold, float):
        threshold_label = f"{threshold:.8f}".rstrip("0").rstrip(".")
    else:
        threshold_label = str(threshold)
    name = f"{feature} {op} {threshold_label}"
    return name, lambda row, feature=feature, op=op, threshold=threshold: cmp_value(row.get(feature), op, threshold)


def evaluate_rule(rule: RuleFn, rows: list[dict[str, Any]], baseline_materialized: int | None = None) -> dict[str, Any]:
    selected = [row for row in rows if rule(row)]
    materialized = [row for row in selected if row["is_materialized"]]
    materialized_total = baseline_materialized if baseline_materialized is not None else sum(1 for row in rows if row["is_materialized"])
    support_totals: Counter[str] = Counter()
    for row in materialized:
        support_totals.update(row.get("support_counts") or {})
    diagnostic_direct = sum(int_value(row.get("diagnostic_direct_verified_count")) for row in selected)
    diagnostic_direct_below = sum(int_value(row.get("diagnostic_direct_below_rho_count")) for row in selected)
    diagnostic_shared = sum(int_value(row.get("diagnostic_shared_verified_count")) for row in selected)
    diagnostic_shared_below = sum(int_value(row.get("diagnostic_shared_below_rho_count")) for row in selected)
    return {
        "diagnostic_direct_below_rho_count": diagnostic_direct_below,
        "diagnostic_direct_verified_count": diagnostic_direct,
        "diagnostic_shared_below_rho_count": diagnostic_shared_below,
        "diagnostic_shared_verified_count": diagnostic_shared,
        "materialized_count": len(materialized),
        "materialized_windows": [row["window"] for row in materialized],
        "precision": round(len(materialized) / len(selected), 8) if selected else None,
        "recall": round(len(materialized) / materialized_total, 8) if materialized_total else None,
        "selected_count": len(selected),
        "selected_windows": [row["window"] for row in selected],
        "support_totals": dict(sorted(support_totals.items())),
    }


def split_rows(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {
        "calibration": [row for row in records if row["split"] == "calibration"],
        "p1052_gap": [row for row in records if row["split"] == "p1052_gap"],
        "forward_validation": [row for row in records if row["split"] == "forward_validation"],
    }


def baseline_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    family_rows = [row for row in rows if row["has_source_family"]]
    materialized = [row for row in rows if row["is_materialized"]]
    family_materialized = [row for row in family_rows if row["is_materialized"]]
    return {
        "family_materialized_count": len(family_materialized),
        "family_precision": round(len(family_materialized) / len(family_rows), 8) if family_rows else None,
        "family_window_count": len(family_rows),
        "labeled_materialized_count": len(materialized),
        "labeled_precision": round(len(materialized) / len(rows), 8) if rows else None,
        "labeled_window_count": len(rows),
        "materialized_windows": [row["window"] for row in materialized],
    }


def rule_catalog(train_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    feature_names = [
        "case_count",
        "priority_count",
        "unique_salts",
        "salt_span",
        "salt_min",
        "salt_max",
        "transfer_span",
        "min_ops",
        "mean_ops",
        "max_ops",
        "op_range",
    ]
    conditions: list[dict[str, Any]] = []
    for feature in feature_names:
        values = sorted({row.get(feature) for row in train_rows if row.get(feature) is not None})
        if not values:
            continue
        is_float = any(isinstance(value, float) and not float(value).is_integer() for value in values)
        for value in values:
            ops = [">=", "<="] if is_float else [">=", "<=", "=="]
            for op in ops:
                name, fn = condition_rule(feature, op, value)
                conditions.append({"expression": name, "fn": fn, "kind": "single"})
    rules: list[dict[str, Any]] = []
    rules.extend(conditions)
    for idx, left in enumerate(conditions):
        for right in conditions[idx + 1 :]:
            left_expr = left["expression"]
            right_expr = right["expression"]
            rules.append(
                {
                    "expression": f"({left_expr}) AND ({right_expr})",
                    "fn": lambda row, left=left["fn"], right=right["fn"]: left(row) and right(row),
                    "kind": "and2",
                }
            )
            rules.append(
                {
                    "expression": f"({left_expr}) OR ({right_expr})",
                    "fn": lambda row, left=left["fn"], right=right["fn"]: left(row) or right(row),
                    "kind": "or2",
                }
            )
    return rules


def choose_rule(
    rules: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    train_baseline_precision: float,
    min_selected: int,
    min_materialized: int,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    materialized_total = sum(1 for row in train_rows if row["is_materialized"])
    candidates = []
    for rule in rules:
        result = evaluate_rule(rule["fn"], train_rows, materialized_total)
        precision = result["precision"] or 0.0
        if result["selected_count"] < min_selected:
            continue
        if result["materialized_count"] < min_materialized:
            continue
        if precision < max(0.25, 2.0 * train_baseline_precision):
            continue
        candidates.append(
            {
                "expression": rule["expression"],
                "kind": rule["kind"],
                "rule": rule,
                "train": result,
            }
        )
    candidates.sort(
        key=lambda item: (
            item["train"]["precision"] or 0.0,
            item["train"]["recall"] or 0.0,
            item["train"]["materialized_count"],
            -item["train"]["selected_count"],
            item["expression"],
        ),
        reverse=True,
    )
    public_candidates = [
        {
            "expression": item["expression"],
            "kind": item["kind"],
            "train": {
                key: value
                for key, value in item["train"].items()
                if key not in {"selected_windows", "materialized_windows"}
            },
        }
        for item in candidates[:20]
    ]
    return (candidates[0] if candidates else None), public_candidates


def compact_result(result: dict[str, Any], max_windows: int = 40) -> dict[str, Any]:
    compact = dict(result)
    for key in ("selected_windows", "materialized_windows"):
        values = compact.get(key) or []
        compact[key] = values[:max_windows]
        compact[f"{key}_truncated"] = len(values) > max_windows
    return compact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", default="11779")
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    parser.add_argument("--min-train-selected", type=int, default=10)
    parser.add_argument("--min-train-materialized", type=int, default=3)
    args = parser.parse_args()

    factor_paths = sorted(args.state_dir.glob(args.factor_glob))
    selected_paths = sorted(args.state_dir.glob(args.selected_glob))
    labels = load_factor_labels(
        factor_paths,
        args.order,
        args.column,
        args.train_min_start,
        args.train_max_start,
        args.gap_min_start,
        args.gap_max_start,
        args.forward_min_start,
    )
    source_features = load_source_features(
        selected_paths,
        args.target,
        args.selector,
        args.top_k,
        args.column,
        args.train_min_start,
        args.train_max_start,
        args.gap_min_start,
        args.gap_max_start,
        args.forward_min_start,
    )
    records = join_records(labels, source_features)
    rows_by_split = split_rows(records)
    baselines = {split: baseline_summary(rows) for split, rows in rows_by_split.items()}
    train_baseline_precision = baselines["calibration"]["labeled_precision"] or 0.0
    forward_baseline_precision = baselines["forward_validation"]["labeled_precision"] or 0.0

    rules = rule_catalog(rows_by_split["calibration"])
    selected, top_candidates = choose_rule(
        rules,
        rows_by_split["calibration"],
        train_baseline_precision,
        args.min_train_selected,
        args.min_train_materialized,
    )

    selected_results: dict[str, Any] | None = None
    strict_success = False
    if selected is not None:
        materialized_counts = {
            split: sum(1 for row in rows if row["is_materialized"])
            for split, rows in rows_by_split.items()
        }
        raw_results = {
            split: evaluate_rule(selected["rule"]["fn"], rows, materialized_counts[split])
            for split, rows in rows_by_split.items()
        }
        selected_results = {
            split: compact_result(result)
            for split, result in raw_results.items()
        }
        forward = raw_results["forward_validation"]
        calibration = raw_results["calibration"]
        strict_success = (
            calibration["selected_count"] >= args.min_train_selected
            and calibration["materialized_count"] >= args.min_train_materialized
            and (calibration["precision"] or 0.0) >= 2.0 * train_baseline_precision
            and forward["selected_count"] >= 10
            and forward["materialized_count"] >= 5
            and (forward["precision"] or 0.0) > forward_baseline_precision
        )

    if selected is None:
        claim_status = "NEGATIVE_RESULT_P1054_NO_CALIBRATION_PUBLIC_GATE"
    elif strict_success:
        claim_status = "POSITIVE_SIGNAL_P1054_PUBLIC_MATERIALIZATION_GATE_LOW_RECALL"
    else:
        claim_status = "NEGATIVE_RESULT_P1054_CALIBRATION_GATE_FAILS_FORWARD"

    input_paths = [
        path
        for path in factor_paths + selected_paths
        if window_from_name(path) is not None
    ]
    payload = {
        "artifact_hashes": {
            "contract": sha256_file(args.contract) if args.contract.exists() else None,
            "input_artifact_count": len(input_paths),
            "input_artifact_digest": digest_paths(input_paths),
            "script": sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "factor_glob": args.factor_glob,
            "script": str(Path(__file__)),
            "selected_glob": args.selected_glob,
        },
        "baselines": baselines,
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "PUBLIC-MATERIALIZATION-GATE",
            "ACCEPTED-FACTOR-MATERIALIZATION",
            "INDEX-CALCULUS-PRECURSOR",
            "SOURCE-CHARGED-INCOMPLETE",
            "NOT-SPARSE-LA-CLOSURE",
            "NOT-TARGET-DESCENT",
            "POLLARD-RHO-BOUNDARY",
        ],
        "honesty_boundary": {
            "direct_shared_verification_labels_excluded_from_gate": True,
            "not_a_complete_collector": True,
            "not_a_faster_than_rho_claim": True,
            "selected_rule_uses_calibration_labels_only": selected is not None,
        },
        "parameters": {
            "column": args.column,
            "forward_min_start": args.forward_min_start,
            "gap_max_start": args.gap_max_start,
            "gap_min_start": args.gap_min_start,
            "min_train_materialized": args.min_train_materialized,
            "min_train_selected": args.min_train_selected,
            "order": args.order,
            "selector": args.selector,
            "target": args.target,
            "top_k": args.top_k,
            "train_max_start": args.train_max_start,
            "train_min_start": args.train_min_start,
        },
        "record_counts": {
            split: len(rows)
            for split, rows in rows_by_split.items()
        },
        "schema": SCHEMA,
        "selected_rule": None
        if selected is None
        else {
            "expression": selected["expression"],
            "kind": selected["kind"],
        },
        "selected_rule_results": selected_results,
        "strict_success": strict_success,
        "summary": {
            "calibration_baseline_precision": train_baseline_precision,
            "claim_status": claim_status,
            "forward_baseline_precision": forward_baseline_precision,
            "input_artifact_count": len(input_paths),
            "selected_rule_expression": selected["expression"] if selected else None,
            "strict_success": strict_success,
            "top_candidate_count": len(top_candidates),
        },
        "timestamp": now_iso(),
        "top_calibration_candidates": top_candidates,
    }
    write_json(args.out, payload)
    selected_expr = selected["expression"] if selected else "none"
    forward_precision = None
    if selected_results is not None:
        forward_precision = selected_results["forward_validation"]["precision"]
    print(
        "claim={claim} strict_success={strict} rule={rule} "
        "forward_precision={forward_precision} forward_baseline={forward_baseline} out={out}".format(
            claim=claim_status,
            strict=str(strict_success).lower(),
            rule=selected_expr,
            forward_precision=forward_precision,
            forward_baseline=round(forward_baseline_precision, 8),
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
