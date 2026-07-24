#!/usr/bin/env python3
"""Scout public pre-screen predicates for known-column relation structure.

The known-column pressure screen verifies individual-log recoveries after a
direct relation scan and known-factor substitution.  This scout asks the next
question: do public case features predict, before the scan, which selected
cases will actually contain a relation form supported inside the known factor
columns?

Rules are selected on calibration windows only and evaluated on later windows.
They may use public metadata such as top-k, selected support, transfer index,
and row-key salts.  They do not use public-key verification or relation-form
labels when scoring validation windows.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Callable


Predicate = Callable[[dict[str, Any]], bool]
SALT_RE = re.compile(r"salt(\d+)")
WINDOW_RE = re.compile(r"_(\d+)_(\d+)_probe\.json$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_paths(raw: str) -> list[Path]:
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def salts_from_rows(row_keys: list[Any]) -> list[int]:
    salts: list[int] = []
    for row_key in row_keys:
        match = SALT_RE.search(str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return salts


def window_from_path(path: Path) -> tuple[int, int]:
    match = WINDOW_RE.search(path.name)
    if not match:
        return (0, 0)
    return (int(match.group(1)), int(match.group(2)))


def attempt_support_signatures(case: dict[str, Any]) -> list[tuple[int, ...]]:
    signatures: list[tuple[int, ...]] = []
    for attempt in case.get("attempts") or []:
        if not isinstance(attempt, dict):
            continue
        if attempt.get("reason") == "unknown_factor_support":
            support = tuple(int_value(value) for value in attempt.get("support") or [])
            if support:
                signatures.append(support)
    for attempt in case.get("verified_attempts") or []:
        if not isinstance(attempt, dict):
            continue
        support = tuple(int_value(value) for value in attempt.get("support") or [])
        if support:
            signatures.append(support)
    return sorted(set(signatures))


def load_window(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    start, end = window_from_path(path)
    rows = []
    for case_index, case in enumerate(payload.get("case_results") or []):
        if not isinstance(case, dict):
            continue
        selected = case.get("selected") if isinstance(case.get("selected"), dict) else {}
        metrics = (
            case.get("public_selection_metrics")
            if isinstance(case.get("public_selection_metrics"), dict)
            else {}
        )
        row_keys = [str(row) for row in selected.get("row_keys") or []]
        salts = salts_from_rows(row_keys)
        selected_support = tuple(int_value(value) for value in case.get("selected_term_support") or [])
        salt_gap = abs(salts[1] - salts[0]) if len(salts) >= 2 else None
        salt_sum = sum(salts) if salts else None
        structural = int_value(case.get("known_support_form_count")) > 0
        hit = bool(case.get("public_known_factor_verified"))
        rows.append(
            {
                "artifact": str(path),
                "case_index": case_index,
                "direct_ops_over_rho": case.get("direct_ops_over_rho"),
                "hit": hit,
                "known_overlap_count": int_value(metrics.get("known_overlap_count")),
                "known_support_form_count": int_value(case.get("known_support_form_count")),
                "pressure_score": int_value(metrics.get("pressure_score")),
                "relation_support_signatures": [list(sig) for sig in attempt_support_signatures(case)],
                "row_keys": row_keys,
                "salt_abs_gap": salt_gap,
                "salt_first": salts[0] if salts else None,
                "salt_first_lt_second": salts[0] < salts[1] if len(salts) >= 2 else None,
                "salt_second": salts[1] if len(salts) >= 2 else None,
                "salt_sum": salt_sum,
                "selected_support": selected_support,
                "selected_support_size": len(selected_support),
                "structural": structural,
                "top_k": int_value(selected.get("top_k")),
                "transfer_index": int_value(selected.get("transfer_index")),
                "unknown_selected_support_count": int_value(metrics.get("unknown_selected_support_count")),
            }
        )
    return {
        "artifact": str(path),
        "claim_status": payload.get("claim_status"),
        "end": end,
        "start": start,
        "summary": payload.get("summary") or {},
        "cases": rows,
    }


def numeric_or_false(value: Any, op: str, threshold: int) -> bool:
    if value is None:
        return False
    number = int_value(value)
    if op == "eq":
        return number == threshold
    if op == "le":
        return number <= threshold
    if op == "ge":
        return number >= threshold
    raise ValueError(f"unknown op {op}")


def build_predicates(calibration: list[dict[str, Any]]) -> dict[str, Predicate]:
    all_cases = [case for window in calibration for case in window["cases"]]
    structural_cases = [case for case in all_cases if case.get("structural")]
    predicates: dict[str, Predicate] = {
        "all_pressure_cases": lambda case: True,
        "topk_7": lambda case: int_value(case.get("top_k")) == 7,
        "topk_12": lambda case: int_value(case.get("top_k")) == 12,
        "topk_16": lambda case: int_value(case.get("top_k")) == 16,
        "salt_first_lt_second": lambda case: case.get("salt_first_lt_second") is True,
        "salt_first_gt_second": lambda case: case.get("salt_first_lt_second") is False,
    }
    for field in ("salt_abs_gap", "salt_sum", "salt_first", "salt_second", "transfer_index"):
        values = sorted({int_value(case.get(field)) for case in all_cases if case.get(field) is not None})
        structural_values = sorted({int_value(case.get(field)) for case in structural_cases if case.get(field) is not None})
        for value in structural_values[:64]:
            predicates[f"{field}_eq_{value}"] = (
                lambda case, field=field, value=value: numeric_or_false(case.get(field), "eq", value)
            )
        for value in values:
            predicates[f"{field}_le_{value}"] = (
                lambda case, field=field, value=value: numeric_or_false(case.get(field), "le", value)
            )
            predicates[f"{field}_ge_{value}"] = (
                lambda case, field=field, value=value: numeric_or_false(case.get(field), "ge", value)
            )
    for field in ("salt_abs_gap", "salt_sum", "transfer_index"):
        for modulus in (3, 4, 5, 8, 16):
            residues = sorted(
                {
                    int_value(case.get(field)) % modulus
                    for case in structural_cases
                    if case.get(field) is not None
                }
            )
            for residue in residues:
                predicates[f"{field}_mod_{modulus}_eq_{residue}"] = (
                    lambda case, field=field, modulus=modulus, residue=residue: (
                        case.get(field) is not None
                        and int_value(case.get(field)) % modulus == residue
                    )
                )
    structural_supports = sorted({tuple(case.get("selected_support") or []) for case in structural_cases})
    for index, signature in enumerate(structural_supports[:32]):
        predicates[f"selected_support_structcal_{index}"] = (
            lambda case, signature=signature: tuple(case.get("selected_support") or []) == signature
        )
    return predicates


def evaluate_windows(windows: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    rows = []
    selected_case_count = 0
    selected_structural_case_count = 0
    selected_hit_case_count = 0
    total_structural_case_count = 0
    total_hit_case_count = 0
    total_case_count = 0
    for window in windows:
        selected_cases = []
        cost = 0.0
        structural_case: dict[str, Any] | None = None
        hit_case: dict[str, Any] | None = None
        for case in window["cases"]:
            total_case_count += 1
            if case.get("structural"):
                total_structural_case_count += 1
            if case.get("hit"):
                total_hit_case_count += 1
            if not predicate(case):
                continue
            selected_cases.append(case)
            selected_case_count += 1
            if case.get("structural"):
                selected_structural_case_count += 1
            if case.get("hit"):
                selected_hit_case_count += 1
            if case.get("direct_ops_over_rho") is not None:
                cost += float_value(case.get("direct_ops_over_rho"))
            if structural_case is None and case.get("structural"):
                structural_case = case
            if hit_case is None and case.get("hit"):
                hit_case = case
        rows.append(
            {
                "artifact": Path(str(window["artifact"])).name,
                "cost_over_rho": round(cost, 8),
                "hit": hit_case is not None,
                "hit_case": compact_case(hit_case),
                "selected_case_count": len(selected_cases),
                "structural": structural_case is not None,
                "structural_case": compact_case(structural_case),
                "window": f"{window['start']}_{window['end']}",
            }
        )
    structural_windows = [row for row in rows if row["structural"]]
    hit_windows = [row for row in rows if row["hit"]]
    cost_sum = sum(float_value(row.get("cost_over_rho")) for row in rows)
    return {
        "case_count": total_case_count,
        "cost_over_rho": stat([float_value(row.get("cost_over_rho")) for row in rows]),
        "cost_per_hit_window_over_rho": round(cost_sum / len(hit_windows), 8) if hit_windows else None,
        "cost_per_structural_window_over_rho": (
            round(cost_sum / len(structural_windows), 8) if structural_windows else None
        ),
        "hit_case_precision": ratio(selected_hit_case_count, selected_case_count),
        "hit_case_recall": ratio(selected_hit_case_count, total_hit_case_count),
        "hit_window_count": len(hit_windows),
        "rows": rows,
        "selected_case_count": selected_case_count,
        "selected_hit_case_count": selected_hit_case_count,
        "selected_structural_case_count": selected_structural_case_count,
        "structural_case_precision": ratio(selected_structural_case_count, selected_case_count),
        "structural_case_recall": ratio(selected_structural_case_count, total_structural_case_count),
        "structural_window_count": len(structural_windows),
        "total_hit_case_count": total_hit_case_count,
        "total_structural_case_count": total_structural_case_count,
        "window_count": len(rows),
    }


def compact_case(case: dict[str, Any] | None) -> dict[str, Any] | None:
    if case is None:
        return None
    return {
        "case_index": case.get("case_index"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "known_support_form_count": case.get("known_support_form_count"),
        "relation_support_signatures": case.get("relation_support_signatures"),
        "row_keys": case.get("row_keys"),
        "salt_abs_gap": case.get("salt_abs_gap"),
        "salt_sum": case.get("salt_sum"),
        "top_k": case.get("top_k"),
        "transfer_index": case.get("transfer_index"),
    }


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None, "sum": 0.0}
    return {
        "count": len(values),
        "max": round(max(values), 8),
        "mean": round(mean(values), 8),
        "min": round(min(values), 8),
        "sum": round(sum(values), 8),
    }


def rank_key(metrics: dict[str, Any]) -> tuple[float, int, int, int]:
    structural_cost = metrics.get("cost_per_structural_window_over_rho")
    hit_cost = metrics.get("cost_per_hit_window_over_rho")
    selected = int_value(metrics.get("selected_case_count"))
    structural_windows = int_value(metrics.get("structural_window_count"))
    cost = structural_cost if isinstance(structural_cost, (int, float)) else hit_cost
    return (
        float(cost) if isinstance(cost, (int, float)) else 1e9,
        -structural_windows,
        selected,
        -int_value(metrics.get("hit_window_count")),
    )


def support_signature_counts(windows: list[dict[str, Any]]) -> dict[str, Any]:
    structural = Counter()
    hits = Counter()
    misses = Counter()
    for window in windows:
        for case in window["cases"]:
            signatures = case.get("relation_support_signatures") or []
            key = ",".join(str(sig) for sig in signatures) if signatures else "<none>"
            if case.get("structural"):
                structural[key] += 1
            elif case.get("hit"):
                hits[key] += 1
            else:
                misses[key] += 1
    return {
        "hit_signatures": hits.most_common(12),
        "miss_signatures": misses.most_common(12),
        "structural_signatures": structural.most_common(12),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--calibration-end-max", type=int, default=3007)
    parser.add_argument("--min-calibration-structural-windows", type=int, default=3)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = parse_paths(args.artifacts)
    windows = [load_window(path) for path in paths]
    calibration = [window for window in windows if int_value(window.get("end")) <= args.calibration_end_max]
    validation = [window for window in windows if int_value(window.get("end")) > args.calibration_end_max]
    predicates = build_predicates(calibration)
    calibration_results = {
        name: evaluate_windows(calibration, predicate)
        for name, predicate in sorted(predicates.items())
    }
    viable = [
        (name, metrics)
        for name, metrics in calibration_results.items()
        if int_value(metrics.get("selected_case_count")) > 0
        and int_value(metrics.get("structural_window_count")) >= args.min_calibration_structural_windows
    ]
    selected_name = min(viable, key=lambda item: rank_key(item[1]))[0] if viable else "all_pressure_cases"
    validation_results = {
        name: evaluate_windows(validation, predicate)
        for name, predicate in sorted(predicates.items())
    }
    selected_validation = validation_results[selected_name]
    selected_structural_cost = selected_validation.get("cost_per_structural_window_over_rho")
    selected_hit_cost = selected_validation.get("cost_per_hit_window_over_rho")
    if isinstance(selected_hit_cost, (int, float)) and selected_hit_cost < 1.0:
        claim_status = "PUBLIC_STRUCTURAL_PRESCREEN_HIT_BELOW_RHO"
    elif isinstance(selected_structural_cost, (int, float)) and selected_structural_cost < 1.0:
        claim_status = "PUBLIC_STRUCTURAL_PRESCREEN_STRUCTURAL_BELOW_RHO"
    elif int_value(selected_validation.get("structural_window_count")) > 0:
        claim_status = "PUBLIC_STRUCTURAL_PRESCREEN_RECOVERS_NEEDS_COST_GAIN"
    else:
        claim_status = "PUBLIC_STRUCTURAL_PRESCREEN_NO_FORWARD_STRUCTURAL"
    payload = {
        "artifacts": [str(path) for path in paths],
        "calibration_end_max": args.calibration_end_max,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": {
            "assumptions": [
                "Rules use public pressure-case metadata only.",
                "Rule selection uses calibration windows only.",
                "Structural/hit labels are used only to score calibration and validation outcomes.",
            ],
            "evidence": "TOY-EVIDENCE / MODEL-BOUND / HEURISTIC-COST",
            "not_claimed": [
                "complete faster-than-rho prime-field ECDLP algorithm",
                "relation-form predictor independent of the current toy harness",
                "shared-product/source-charged implementation",
            ],
        },
        "predicate_results": {
            "calibration": calibration_results,
            "validation": validation_results,
        },
        "schema": "ecdlp.low_term_total2_known_column_structural_feature_scout.v1",
        "selection_parameters": {
            "min_calibration_structural_windows": args.min_calibration_structural_windows,
        },
        "selected_by_calibration": {
            "calibration": calibration_results[selected_name],
            "name": selected_name,
            "validation": selected_validation,
        },
        "support_signature_counts": {
            "calibration": support_signature_counts(calibration),
            "validation": support_signature_counts(validation),
        },
        "top_calibration_rules": [
            {"name": name, **metrics}
            for name, metrics in sorted(calibration_results.items(), key=lambda item: rank_key(item[1]))[:16]
        ],
        "top_validation_rules": [
            {"name": name, **metrics}
            for name, metrics in sorted(validation_results.items(), key=lambda item: rank_key(item[1]))[:16]
        ],
        "window_split": {
            "calibration": [f"{window['start']}_{window['end']}" for window in calibration],
            "validation": [f"{window['start']}_{window['end']}" for window in validation],
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["selected_by_calibration"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": claim_status}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
