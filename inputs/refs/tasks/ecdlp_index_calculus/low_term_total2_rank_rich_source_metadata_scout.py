#!/usr/bin/env python3
"""Predict rank-rich known-factor exports from pre-scan source metadata.

The exported known-factor surface showed that post-relation ``forms_count>=2``
is a useful diagnostic for marginal factor-rank gain, while selected support
alone is too broad.  This scout joins exported certificates back to the exact
public source/support rows and tests whether selected-leaf metadata can predict
multi-form or rank-gain rows before direct relation scanning.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import glob
import json
import re
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

from low_term_total2_known_column_pressure_direct_screen import (
    report_key,
    source_case_key,
    source_cases,
)


WINDOW_RE = re.compile(r"(?:fixed_row_|selector_expanded_|col15_)(\d+)_(\d+)")


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
    paths: list[Path] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        matches = sorted(Path(path) for path in glob.glob(item))
        paths.extend(matches or [Path(item)])
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def window_from_path(path: Path) -> str:
    match = WINDOW_RE.search(path.name)
    if not match:
        return ""
    return f"{int(match.group(1))}_{int(match.group(2))}"


def build_window_map(paths: list[Path]) -> dict[str, Path]:
    mapped: dict[str, Path] = {}
    for path in paths:
        window = window_from_path(path)
        if window:
            mapped[window] = path
    return mapped


def window_start(window: str) -> int:
    try:
        return int(str(window).split("_", 1)[0])
    except (TypeError, ValueError):
        return 0


def canonical_rows(row_keys: Any) -> tuple[str, ...]:
    if not isinstance(row_keys, list):
        return tuple()
    return tuple(sorted(str(row) for row in row_keys))


def salts(row_keys: Any) -> list[int]:
    values: list[int] = []
    for row_key in canonical_rows(row_keys):
        if "salt" not in row_key:
            continue
        try:
            values.append(int(row_key.rsplit("salt", 1)[1]))
        except ValueError:
            continue
    return sorted(values)


def label(values: Any) -> str:
    if not isinstance(values, list):
        return "none"
    return ",".join(str(int_value(value)) for value in values)


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<=%d" % threshold)
        if value >= threshold:
            features.add(f"{name}>=%d" % threshold)
    return features


def support_report_index(support_payload: dict[str, Any]) -> dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]:
    result: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    for report in support_payload.get("case_reports") or []:
        if not isinstance(report, dict):
            continue
        result.setdefault(report_key(report), report)
    return result


def source_case_index(source_payload: dict[str, Any]) -> dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]:
    result: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    for case in source_cases(source_payload):
        result.setdefault(source_case_key(case), case)
    return result


def scorer_labels(payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    labels: dict[int, dict[str, Any]] = {}
    for score in payload.get("scores") or []:
        if not isinstance(score, dict):
            continue
        candidate = score.get("candidate") if isinstance(score.get("candidate"), dict) else {}
        offset = int_value(candidate.get("artifact_offset"), -1)
        if offset < 0:
            continue
        labels[offset] = {
            "rank_gain": int_value(score.get("rank_gain")),
            "unique_factor_relation_gain": int_value(score.get("unique_factor_relation_gain")),
        }
    return labels


def leaf_features(source_case: dict[str, Any]) -> set[str]:
    row_leaf_keys = source_case.get("row_leaf_keys") if isinstance(source_case.get("row_leaf_keys"), list) else []
    counts: list[int] = []
    union: set[int] = set()
    intersection: set[int] | None = None
    per_row_labels: list[str] = []
    for item in row_leaf_keys:
        if not isinstance(item, dict):
            continue
        indices = sorted(int_value(value) for value in item.get("leaf_indices") or [])
        counts.append(len(indices))
        union.update(indices)
        current = set(indices)
        intersection = current if intersection is None else intersection & current
        per_row_labels.append(label(indices))
    counts_sorted = sorted(counts)
    intersection = intersection or set()
    features: set[str] = set()
    features.update(bucket_features("selected_leaf_count", int_value(source_case.get("selected_leaf_count")), (1, 2, 3, 4, 5)))
    features.update(bucket_features("selected_row_count", int_value(source_case.get("selected_row_count")), (1, 2, 3)))
    features.add(f"leaf_count_shape={label(counts_sorted)}")
    features.add(f"leaf_union={label(sorted(union))}")
    features.add(f"leaf_union_size={len(union)}")
    features.add(f"leaf_intersection={label(sorted(intersection))}")
    features.add(f"leaf_intersection_size={len(intersection)}")
    for leaf in sorted(union):
        features.add(f"leaf_union_has={leaf}")
    for leaf in sorted(intersection):
        features.add(f"leaf_intersection_has={leaf}")
    for row_label in sorted(per_row_labels):
        features.add(f"leaf_row={row_label}")
    return features


def base_features(certificate: dict[str, Any], support_report: dict[str, Any], source_case: dict[str, Any], mode: str) -> set[str]:
    selected = certificate.get("selected") if isinstance(certificate.get("selected"), dict) else {}
    features: set[str] = {
        f"selector={selected.get('selector')}",
        f"topk={int_value(selected.get('top_k'))}",
        f"selected_support={label(support_report.get('selected_term_support') or certificate.get('selected_term_support') or [])}",
        f"priority_hits={label(support_report.get('priority_hits') or [])}",
        f"priority_hit_count={len(support_report.get('priority_hits') or [])}",
        f"public_product_gate_selected={bool(support_report.get('public_product_gate_selected'))}",
        f"source_row_selector={source_case.get('row_selector')}",
    }
    features.update(
        bucket_features(
            "selected_support_size",
            len(support_report.get("selected_term_support") or certificate.get("selected_term_support") or []),
            (8, 10, 12, 15),
        )
    )
    if mode in {"public_leaf", "public_leaf_residue"}:
        features.update(leaf_features(source_case))
    if mode == "public_leaf_residue":
        row_salts = salts(selected.get("row_keys"))
        if row_salts:
            gap = max(row_salts) - min(row_salts)
            features.add(f"salt_gap={gap}")
            features.add(f"salt_gap_mod_4={gap % 4}")
            features.add(f"salt_sum_mod_8={sum(row_salts) % 8}")
            features.add(f"transfer_mod_8={int_value(selected.get('transfer_index')) % 8}")
            for salt in row_salts:
                features.add(f"salt_mod_8={salt % 8}")
    return features


def conjunctions(features: set[str], max_size: int) -> set[str]:
    ordered = sorted(features)
    result = set(ordered)
    for size in range(2, max_size + 1):
        for combo in combinations(ordered, size):
            result.add("|".join(combo))
    return result


def load_rows(
    export_payload: dict[str, Any],
    scorer_payload: dict[str, Any],
    source_by_window: dict[str, Path],
    support_by_window: dict[str, Path],
    feature_mode: str,
    max_conjunction_size: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    labels_by_offset = scorer_labels(scorer_payload)
    source_cache: dict[Path, dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]] = {}
    support_cache: dict[Path, dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]] = {}
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for offset, certificate in enumerate(export_payload.get("certificates") or []):
        if not isinstance(certificate, dict):
            continue
        selected = certificate.get("selected") if isinstance(certificate.get("selected"), dict) else {}
        window = str(certificate.get("window") or "")
        source_path = source_by_window.get(window)
        support_path = support_by_window.get(window)
        if source_path is None or support_path is None:
            errors.append({"artifact_offset": offset, "error": "missing_source_or_support", "window": window})
            continue
        if source_path not in source_cache:
            source_cache[source_path] = source_case_index(load_json(source_path))
        if support_path not in support_cache:
            support_cache[support_path] = support_report_index(load_json(support_path))
        key = (
            str(selected.get("target")),
            int_value(selected.get("transfer_index")),
            str(selected.get("selector")),
            int_value(selected.get("top_k")),
            canonical_rows(selected.get("row_keys")),
        )
        source_case = source_cache[source_path].get(key)
        support_report = support_cache[support_path].get(key)
        if source_case is None or support_report is None:
            errors.append({"artifact_offset": offset, "error": "missing_exact_source_or_support_case", "key": list(key), "window": window})
            continue
        labels = labels_by_offset.get(offset, {"rank_gain": 0, "unique_factor_relation_gain": 0})
        features = conjunctions(base_features(certificate, support_report, source_case, feature_mode), max_conjunction_size)
        rows.append(
            {
                "artifact_offset": offset,
                "cost_over_rho": float_value(selected.get("source_family_cost_over_rho")),
                "features": features,
                "forms_count": int_value(certificate.get("forms_count")),
                "rank_gain": int_value(labels.get("rank_gain")),
                "row": {
                    "artifact_offset": offset,
                    "forms_count": int_value(certificate.get("forms_count")),
                    "leaf_count_shape": sorted(len(item.get("leaf_indices") or []) for item in source_case.get("row_leaf_keys") or [] if isinstance(item, dict)),
                    "rank": int_value(certificate.get("rank")),
                    "rank_gain": int_value(labels.get("rank_gain")),
                    "selected_leaf_count": int_value(source_case.get("selected_leaf_count")),
                    "selected_support": support_report.get("selected_term_support") or certificate.get("selected_term_support") or [],
                    "selector": selected.get("selector"),
                    "source_family_cost_over_rho": selected.get("source_family_cost_over_rho"),
                    "top_k": int_value(selected.get("top_k")),
                    "transfer_index": int_value(selected.get("transfer_index")),
                    "unique_factor_relation_gain": int_value(labels.get("unique_factor_relation_gain")),
                    "window": window,
                },
                "window": window,
                "window_start": window_start(window),
            }
        )
    return sorted(rows, key=lambda item: (item["window_start"], item["artifact_offset"])), errors


def split_rows(rows: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [row for row in rows if int_value(row.get("window_start")) <= calibration_end],
        [row for row in rows if int_value(row.get("window_start")) > calibration_end],
    )


def is_positive(row: dict[str, Any], label: str) -> bool:
    if label == "rank_gain":
        return int_value(row.get("rank_gain")) > 0
    if label == "forms_count_ge2":
        return int_value(row.get("forms_count")) >= 2
    raise ValueError(f"unknown label {label!r}")


def evaluate_rule(rule: str, rows: list[dict[str, Any]], label_name: str) -> dict[str, Any]:
    selected = [row for row in rows if rule in row["features"]]
    positives = [row for row in selected if is_positive(row, label_name)]
    cost = sum(float_value(row.get("cost_over_rho")) for row in selected)
    return {
        "cost_over_rho": round(cost, 8),
        "cost_per_positive_over_rho": round(cost / len(positives), 8) if positives else None,
        "positive_count": len(positives),
        "precision": round(len(positives) / len(selected), 8) if selected else None,
        "selected_count": len(selected),
        "selected_rows": [row["row"] for row in selected],
    }


def choose_rules(
    calibration: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    label_name: str,
    min_calibration_hits: int,
    min_calibration_precision: float,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for rule in sorted({feature for row in calibration for feature in row["features"]}):
        calibration_eval = evaluate_rule(rule, calibration, label_name)
        if int_value(calibration_eval.get("positive_count")) < min_calibration_hits:
            continue
        precision = calibration_eval.get("precision")
        if precision is None or float(precision) < min_calibration_precision:
            continue
        validation_eval = evaluate_rule(rule, validation, label_name)
        candidates.append(
            {
                "calibration": calibration_eval,
                "feature_count": rule.count("|") + 1,
                "rule": rule,
                "validation": validation_eval,
            }
        )
    candidates.sort(
        key=lambda item: (
            -float(item["calibration"].get("precision") or 0.0),
            -int_value(item["calibration"].get("positive_count")),
            int_value(item.get("feature_count")),
            float(item["calibration"].get("cost_per_positive_over_rho") or 999999.0),
            str(item.get("rule")),
        )
    )
    return candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exported-certificates", required=True)
    parser.add_argument("--rank-scorer", required=True)
    parser.add_argument(
        "--source-glob",
        default="ecdlp_index_calculus_state/frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_*_col15_selector_expanded_probe.json",
    )
    parser.add_argument(
        "--support-glob",
        default="ecdlp_index_calculus_state/low_term_total2_selected_leaf_term_support_scout_22050_col15_selector_expanded_*_probe.json",
    )
    parser.add_argument("--feature-mode", choices=["public_basic", "public_leaf", "public_leaf_residue"], default="public_leaf")
    parser.add_argument("--label", choices=["forms_count_ge2", "rank_gain"], default="forms_count_ge2")
    parser.add_argument("--calibration-end", type=int, default=3375)
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_path = Path(args.exported_certificates)
    scorer_path = Path(args.rank_scorer)
    source_by_window = build_window_map(parse_paths(args.source_glob))
    support_by_window = build_window_map(parse_paths(args.support_glob))
    rows, errors = load_rows(
        load_json(export_path),
        load_json(scorer_path),
        source_by_window,
        support_by_window,
        args.feature_mode,
        args.max_conjunction_size,
    )
    calibration, validation = split_rows(rows, args.calibration_end)
    rules = choose_rules(
        calibration,
        validation,
        args.label,
        args.min_calibration_hits,
        args.min_calibration_precision,
    )
    selected = rules[0] if rules else None
    payload = {
        "artifacts": {
            "exported_certificates": str(export_path),
            "rank_scorer": str(scorer_path),
            "source_glob": args.source_glob,
            "support_glob": args.support_glob,
        },
        "claim_status": (
            "SOURCE_METADATA_RULE_VALIDATES"
            if selected and int_value(selected["validation"].get("positive_count")) > 0
            else "SOURCE_METADATA_RULE_ABSTAINS_OR_MISSES_VALIDATION"
            if selected
            else "SOURCE_METADATA_RULE_NO_VIABLE_CALIBRATION"
        ),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: labels come from exported known-factor certificates and current factor-rank scorer.",
            "public_leaf mode uses selected leaf/source metadata before direct relation scanning; public_leaf_residue additionally allows salt/transfer residue diagnostics.",
            "A validating rule is a source-generator work order unless it is rerun under source-charged/shared-product accounting.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "feature_mode": args.feature_mode,
            "label": args.label,
            "max_conjunction_size": args.max_conjunction_size,
            "min_calibration_hits": args.min_calibration_hits,
            "min_calibration_precision": args.min_calibration_precision,
        },
        "rows": [row["row"] for row in rows],
        "rules": rules[:20],
        "selected_rule": selected,
        "split_summary": {
            "calibration_positive_count": sum(1 for row in calibration if is_positive(row, args.label)),
            "calibration_row_count": len(calibration),
            "validation_positive_count": sum(1 for row in validation if is_positive(row, args.label)),
            "validation_row_count": len(validation),
        },
        "schema": "ecdlp.low_term_total2_rank_rich_source_metadata_scout.v1",
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["split_summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"], "selected_rule": selected["rule"] if selected else None, "error_count": len(errors)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
