#!/usr/bin/env python3
"""Scout rolling-history abstention gates for targeted known-column expansion.

The static public-feature scout found lowterm `[10,14]` first rows but could not
predict which full-support lowterm windows were worth paying.  This scout adds
online public history features: previous first-row source shape, current public
source-availability deltas, and short-run lowterm/source-support streaks.

This is still direct-source replay over toy ECDLP artifacts.  Validation uses
calibration-selected predicates only.  The default history mode is public: it
does not expose held-out hit labels, exact salts, or exact transfer values.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from statistics import mean
from typing import Any

from low_term_total2_known_column_targeted_abstention_gate_scout import (
    compact_case,
    expand_features,
    feature_complexity,
    float_value,
    int_value,
    load_json,
    parse_paths,
    public_features,
    public_row_counter_features,
    ratio,
    salts_from_rows,
    stat,
    support_label,
    write_json,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def window_start(window: str) -> int:
    try:
        return int(str(window).split("_", 1)[0])
    except (TypeError, ValueError):
        return 0


def bucket_count(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features: set[str] = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<=%03d" % threshold)
        if value >= threshold:
            features.add(f"{name}>=%03d" % threshold)
    return features


def signed_delta_bucket(name: str, value: int) -> set[str]:
    features: set[str] = set()
    if value < 0:
        features.add(f"{name}<0")
    elif value > 0:
        features.add(f"{name}>0")
    else:
        features.add(f"{name}=0")
    abs_value = abs(value)
    for threshold in (5, 10, 20, 40):
        if abs_value <= threshold:
            features.add(f"{name}_abs<=%02d" % threshold)
        if abs_value >= threshold:
            features.add(f"{name}_abs>=%02d" % threshold)
    return features


def first_public(row: dict[str, Any]) -> dict[str, Any]:
    scanned = (row.get("scanned_rows") or [None])[0]
    if not isinstance(scanned, dict):
        return {}
    public = scanned.get("public")
    return public if isinstance(public, dict) else {}


def row_signature(row: dict[str, Any]) -> dict[str, Any]:
    public = first_public(row)
    raw_features = public.get("features") if isinstance(public.get("features"), dict) else {}
    row_keys = public.get("row_keys") or []
    salts = salts_from_rows(row_keys)
    return {
        "candidate_count": int_value(row.get("candidate_count")),
        "hit": bool(row.get("hit")),
        "salt_gap": abs(salts[1] - salts[0]) if len(salts) >= 2 else None,
        "selector": str(public.get("selector")),
        "support": support_label(raw_features.get("selected_support") or []),
        "support_report_count": int_value(row.get("support_report_count")),
        "support_size": int_value(raw_features.get("selected_support_size")),
        "top_k": int_value(public.get("top_k")),
        "window": str(row.get("window")),
    }


def public_history_features(history: list[dict[str, Any]], current: dict[str, Any]) -> set[str]:
    features: set[str] = set()
    selector = current["selector"]
    support = current["support"]
    candidates = current["candidate_count"]
    support_reports = current["support_report_count"]
    features.update(bucket_count("history_index", len(history), (1, 2, 4, 8, 16, 32, 48)))
    for depth in (1, 2, 3):
        if len(history) < depth:
            features.add(f"prev{depth}_missing")
            continue
        prev = history[-depth]
        prev_selector = prev["selector"]
        prev_support = prev["support"]
        features.add(f"prev{depth}_selector={prev_selector}")
        features.add(f"prev{depth}_topk={prev['top_k']}")
        features.add(f"prev{depth}_support_size={prev['support_size']}")
        features.add(f"prev{depth}_same_selector={prev_selector == selector}")
        features.add(f"prev{depth}_same_support={prev_support == support}")
        features.add(f"prev{depth}_selector_pair={prev_selector}->{selector}")
        features.add(f"prev{depth}_support_pair={prev_support}->{support}")
        features.update(signed_delta_bucket(f"prev{depth}_candidate_delta", candidates - prev["candidate_count"]))
        features.update(
            signed_delta_bucket(
                f"prev{depth}_support_report_delta",
                support_reports - prev["support_report_count"],
            )
        )
        if current.get("salt_gap") is not None and prev.get("salt_gap") is not None:
            features.update(signed_delta_bucket(f"prev{depth}_salt_gap_delta", current["salt_gap"] - prev["salt_gap"]))

    same_selector_run = 0
    same_support_run = 0
    lowterm_run = 0
    for prev in reversed(history):
        if prev["selector"] == selector:
            same_selector_run += 1
        else:
            break
    for prev in reversed(history):
        if prev["support"] == support:
            same_support_run += 1
        else:
            break
    for prev in reversed(history):
        if prev["selector"] == "mode_low_term_support_total5":
            lowterm_run += 1
        else:
            break
    for name, value in (
        ("same_selector_run", same_selector_run),
        ("same_support_run", same_support_run),
        ("lowterm_run", lowterm_run),
    ):
        features.update(bucket_count(name, value, (1, 2, 3, 4, 6, 8)))

    for width in (3, 5, 8):
        recent = history[-width:]
        features.add(f"recent{width}_count={len(recent)}")
        if not recent:
            continue
        lowterm_count = sum(1 for row in recent if row["selector"] == "mode_low_term_support_total5")
        same_selector_count = sum(1 for row in recent if row["selector"] == selector)
        same_support_count = sum(1 for row in recent if row["support"] == support)
        features.update(bucket_count(f"recent{width}_lowterm_count", lowterm_count, (1, 2, 3, 4, 5, 8)))
        features.update(bucket_count(f"recent{width}_same_selector_count", same_selector_count, (1, 2, 3, 4, 5, 8)))
        features.update(bucket_count(f"recent{width}_same_support_count", same_support_count, (1, 2, 3, 4, 5, 8)))
        recent_candidates = [row["candidate_count"] for row in recent]
        recent_support_reports = [row["support_report_count"] for row in recent]
        features.update(signed_delta_bucket(f"recent{width}_candidate_delta_min", candidates - min(recent_candidates)))
        features.update(signed_delta_bucket(f"recent{width}_candidate_delta_max", candidates - max(recent_candidates)))
        features.update(
            signed_delta_bucket(
                f"recent{width}_support_report_delta_min",
                support_reports - min(recent_support_reports),
            )
        )
        features.update(
            signed_delta_bucket(
                f"recent{width}_support_report_delta_max",
                support_reports - max(recent_support_reports),
            )
        )
    return features


def observed_history_features(history: list[dict[str, Any]]) -> set[str]:
    features: set[str] = set()
    for width in (1, 2, 3, 5, 8):
        recent = history[-width:]
        hit_count = sum(1 for row in recent if row.get("hit"))
        features.update(bucket_count(f"observed_recent{width}_hit_count", hit_count, (1, 2, 3, 5, 8)))
    if history:
        features.add(f"observed_prev_hit={history[-1].get('hit')}")
    return features


def load_rows(
    paths: list[Path],
    split: str,
    feature_mode: str,
    row_filter_feature: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = load_json(path)
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            public = first_public(row)
            features = public_features(public, feature_mode)
            features.update(public_row_counter_features(row))
            if row_filter_feature and row_filter_feature not in features:
                continue
            signature = row_signature(row)
            rows.append(
                {
                    "artifact": str(path),
                    "base_features": features,
                    "cost_over_rho": float_value(row.get("cost_over_rho")),
                    "hit": bool(row.get("hit")),
                    "row": compact_case(row),
                    "signature": signature,
                    "split": split,
                    "window": str(row.get("window")),
                    "window_start": window_start(str(row.get("window"))),
                }
            )
    return rows


def add_history_features(rows: list[dict[str, Any]], history_mode: str, max_conjunction_size: int) -> list[dict[str, Any]]:
    history: list[dict[str, Any]] = []
    enriched: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: (item["window_start"], item["window"])):
        features = set(row.get("base_features") or set())
        signature = row["signature"]
        features.update(public_history_features(history, signature))
        if history_mode == "observed":
            features.update(observed_history_features(history))
        expanded = expand_features(features, max_conjunction_size)
        enriched.append({**row, "feature_set": expanded, "features": sorted(expanded)})
        history.append(signature)
    return enriched


def evaluate(rows: list[dict[str, Any]], feature: str) -> dict[str, Any]:
    selected = [row for row in rows if feature in (row.get("feature_set") or set())]
    hits = [row for row in selected if row.get("hit")]
    total_hits = [row for row in rows if row.get("hit")]
    cost_sum = sum(float_value(row.get("cost_over_rho")) for row in selected)
    return {
        "cost_over_rho": stat([float_value(row.get("cost_over_rho")) for row in selected]),
        "cost_per_hit_window_over_rho": round(cost_sum / len(hits), 8) if hits else None,
        "hit_window_count": len(hits),
        "hit_window_recall": ratio(len(hits), len(total_hits)),
        "precision": ratio(len(hits), len(selected)),
        "rows": [row["row"] for row in selected],
        "selected_window_count": len(selected),
        "total_hit_window_count": len(total_hits),
        "window_count": len(rows),
    }


def rank_result(item: tuple[str, dict[str, Any]]) -> tuple[float, int, int, int, tuple[int, int, int], str]:
    name, metrics = item
    cost = metrics.get("cost_per_hit_window_over_rho")
    precision = metrics.get("precision")
    return (
        float(cost) if isinstance(cost, (int, float)) else 1e9,
        -int_value(metrics.get("hit_window_count")),
        int_value(metrics.get("selected_window_count")),
        -int(1000000 * float(precision if isinstance(precision, (int, float)) else 0.0)),
        feature_complexity(name),
        name,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration-artifacts", required=True)
    parser.add_argument("--validation-artifacts", required=True)
    parser.add_argument("--candidate-feature-contains", default="")
    parser.add_argument("--feature-mode", choices=["structural", "public"], default="public")
    parser.add_argument("--history-mode", choices=["public", "observed"], default="public")
    parser.add_argument("--max-conjunction-size", type=int, default=1)
    parser.add_argument("--min-calibration-hit-windows", type=int, default=1)
    parser.add_argument("--min-calibration-precision", type=float, default=1.0)
    parser.add_argument("--row-filter-feature", default="")
    parser.add_argument("--top-rules", type=int, default=16)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def feature_allowed(feature: str, contains_raw: str) -> bool:
    needles = [part.strip() for part in contains_raw.split(",") if part.strip()]
    if not needles:
        return True
    return any(needle in feature for needle in needles)


def main() -> None:
    args = parse_args()
    calibration_paths = parse_paths(args.calibration_artifacts)
    validation_paths = parse_paths(args.validation_artifacts)
    max_conjunction_size = max(1, int_value(args.max_conjunction_size, 1))
    raw_rows = load_rows(calibration_paths, "calibration", args.feature_mode, args.row_filter_feature)
    raw_rows.extend(load_rows(validation_paths, "validation", args.feature_mode, args.row_filter_feature))
    rows = add_history_features(raw_rows, args.history_mode, max_conjunction_size)
    calibration_rows = [row for row in rows if row["split"] == "calibration"]
    validation_rows = [row for row in rows if row["split"] == "validation"]
    candidate_features = sorted(
        feature
        for feature in {feature for row in calibration_rows for feature in row.get("features") or []}
        if feature_allowed(feature, args.candidate_feature_contains)
    )
    calibration_results = {feature: evaluate(calibration_rows, feature) for feature in candidate_features}
    viable = {
        feature: metrics
        for feature, metrics in calibration_results.items()
        if int_value(metrics.get("hit_window_count")) >= args.min_calibration_hit_windows
        and (
            isinstance(metrics.get("precision"), (int, float))
            and float(metrics["precision"]) >= args.min_calibration_precision
        )
    }
    selected_feature = min(viable.items(), key=rank_result)[0] if viable else ""
    validation_results = {feature: evaluate(validation_rows, feature) for feature in candidate_features}
    selected_validation = validation_results.get(selected_feature, evaluate(validation_rows, selected_feature))
    validation_cost = selected_validation.get("cost_per_hit_window_over_rho")
    if not selected_feature:
        claim_status = "HISTORY_ABSTENTION_NO_VIABLE_CALIBRATION_RULE"
    elif isinstance(validation_cost, (int, float)) and validation_cost < 1.0:
        claim_status = "HISTORY_ABSTENTION_FORWARD_BELOW_RHO_NARROW"
    elif int_value(selected_validation.get("selected_window_count")) == 0:
        claim_status = "HISTORY_ABSTENTION_ABSTAINS_FORWARD"
    elif int_value(selected_validation.get("hit_window_count")) > 0:
        claim_status = "HISTORY_ABSTENTION_RECOVERS_NEEDS_DENSITY_GAIN"
    else:
        claim_status = "HISTORY_ABSTENTION_NO_FORWARD_HIT"
    payload = {
        "calibration_artifacts": [str(path) for path in calibration_paths],
        "claim_status": claim_status,
        "created_at": now_iso(),
        "feature_mode": args.feature_mode,
        "history_mode": args.history_mode,
        "honesty_boundary": {
            "assumptions": [
                "Rule selection uses calibration labels only.",
                "Public history features use only previous first-row source metadata and row counters.",
                "Observed history mode is a diagnostic because it uses prior replay hit labels.",
                "Validation applies the selected predicate to held-out rows without selecting on validation labels.",
            ],
            "evidence": "TOY-EVIDENCE / MODEL-BOUND / HISTORY-ABSTENTION-SCOUT",
            "not_claimed": [
                "complete faster-than-rho prime-field ECDLP algorithm",
                "deployment-relevant attack",
                "shared-product/source-charged collector",
            ],
        },
        "schema": "ecdlp.low_term_total2_known_column_history_abstention_gate_scout.v1",
        "selection_parameters": {
            "candidate_feature_contains": args.candidate_feature_contains,
            "history_mode": args.history_mode,
            "max_conjunction_size": max_conjunction_size,
            "min_calibration_hit_windows": args.min_calibration_hit_windows,
            "min_calibration_precision": args.min_calibration_precision,
            "row_filter_feature": args.row_filter_feature,
        },
        "selected_by_calibration": {
            "calibration": calibration_results.get(selected_feature),
            "feature": selected_feature,
            "validation": selected_validation,
        },
        "top_calibration_rules": [
            {"feature": feature, **metrics}
            for feature, metrics in sorted(calibration_results.items(), key=rank_result)[: args.top_rules]
        ],
        "top_validation_rules_diagnostic_only": [
            {"feature": feature, **metrics}
            for feature, metrics in sorted(validation_results.items(), key=rank_result)[: args.top_rules]
        ],
        "validation_artifacts": [str(path) for path in validation_paths],
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["selected_by_calibration"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": claim_status}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
