#!/usr/bin/env python3
"""Scout public abstention gates for targeted known-column expansion.

The targeted source-family order can put motif-bearing candidates early, but
it still pays too many no-hit windows.  This scout learns simple public
predicates from calibration expansion artifacts and evaluates them on later
artifacts.  It is an abstention test: selected windows pay the first targeted
row cost, unselected windows abstain.

By default the feature set is structural only: selector, top-k, and selected
support.  Salt/transfer residue features can be enabled for diagnostics, but
exact transfer/salt values are intentionally excluded.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from statistics import mean
from typing import Any


SALT_RE = re.compile(r"salt(\d+)")
CONJUNCTION_PREFIXES = (
    "candidate_count",
    "known_column_count",
    "motif_column_count",
    "motif_pair_visible_count",
    "salt_gap_",
    "salt_sum_mod_",
    "selector=",
    "support=",
    "support_report_count",
    "support_size=",
    "topk=",
    "transfer_mod_",
)


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


def parse_paths(raw: str) -> list[Path]:
    return [Path(part.strip()) for part in raw.split(",") if part.strip()]


def salts_from_rows(row_keys: list[Any]) -> tuple[int, ...]:
    salts: list[int] = []
    for row_key in row_keys:
        match = SALT_RE.search(str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return tuple(salts)


def support_label(values: list[Any]) -> str:
    return ",".join(str(int_value(value)) for value in values)


def public_features(public: dict[str, Any], feature_mode: str) -> set[str]:
    features: set[str] = set()
    selector = str(public.get("selector"))
    top_k = int_value(public.get("top_k"))
    transfer = int_value(public.get("transfer_index"))
    row_keys = public.get("row_keys") or []
    salts = salts_from_rows(row_keys)
    raw_features = public.get("features") if isinstance(public.get("features"), dict) else {}
    support = raw_features.get("selected_support") or []
    support_sig = support_label(support)
    support_size = int_value(raw_features.get("selected_support_size"))
    known_count = int_value(raw_features.get("known_column_count"))
    motif_pair_count = int_value(raw_features.get("motif_pair_visible_count"))
    motif_col_count = int_value(raw_features.get("motif_column_count"))

    structural = {
        f"selector={selector}",
        f"topk={top_k}",
        f"support={support_sig}",
        f"support_size={support_size}",
        f"known_column_count={known_count}",
        f"motif_pair_visible_count={motif_pair_count}",
        f"motif_column_count={motif_col_count}",
        f"selector={selector}|topk={top_k}",
        f"selector={selector}|support={support_sig}",
        f"topk={top_k}|support={support_sig}",
        f"selector={selector}|topk={top_k}|support={support_sig}",
    }
    features.update(structural)
    for threshold in range(1, 7):
        if motif_pair_count >= threshold:
            features.add(f"motif_pair_visible_count>={threshold}")
    for threshold in range(1, 9):
        if known_count >= threshold:
            features.add(f"known_column_count>={threshold}")

    if feature_mode == "public":
        for modulus in (3, 4, 5, 8, 16):
            features.add(f"transfer_mod_{modulus}={transfer % modulus}")
            features.add(f"selector={selector}|transfer_mod_{modulus}={transfer % modulus}")
        if salts:
            salt_sum = sum(salts)
            for modulus in (3, 4, 5, 8, 16):
                features.add(f"salt_sum_mod_{modulus}={salt_sum % modulus}")
                features.add(f"selector={selector}|salt_sum_mod_{modulus}={salt_sum % modulus}")
            if len(salts) >= 2:
                gap = abs(salts[1] - salts[0])
                features.add(f"salt_gap_bucket={min(gap, 12)}")
                for modulus in (3, 4, 5, 8):
                    features.add(f"salt_gap_mod_{modulus}={gap % modulus}")
    return features


def compact_case(row: dict[str, Any]) -> dict[str, Any]:
    scanned = (row.get("scanned_rows") or [None])[0]
    if not isinstance(scanned, dict):
        return {
            "cost_over_rho": row.get("cost_over_rho"),
            "hit": row.get("hit"),
            "window": row.get("window"),
        }
    public = scanned.get("public") if isinstance(scanned.get("public"), dict) else {}
    case = scanned.get("case") if isinstance(scanned.get("case"), dict) else {}
    return {
        "cost_over_rho": row.get("cost_over_rho"),
        "hit": row.get("hit"),
        "public": {
            "features": public.get("features"),
            "row_keys": public.get("row_keys") or [],
            "selector": public.get("selector"),
            "top_k": public.get("top_k"),
            "transfer_index": public.get("transfer_index"),
        },
        "verified_motifs": case.get("verified_motifs") or [],
        "window": row.get("window"),
    }


def public_row_counter_features(row: dict[str, Any]) -> set[str]:
    features: set[str] = set()
    candidate_count = int_value(row.get("candidate_count"))
    support_count = int_value(row.get("support_report_count"))
    for name, value in (("candidate_count", candidate_count), ("support_report_count", support_count)):
        features.add(f"{name}={value}")
        for threshold in range(20, 161, 10):
            if value <= threshold:
                features.add(f"{name}<=%03d" % threshold)
            if value >= threshold:
                features.add(f"{name}>=%03d" % threshold)
    return features


def eligible_for_conjunction(feature: str) -> bool:
    return feature.startswith(CONJUNCTION_PREFIXES)


def expand_features(features: set[str], max_conjunction_size: int) -> set[str]:
    expanded = set(features)
    if max_conjunction_size < 2:
        return expanded
    eligible = sorted(feature for feature in features if eligible_for_conjunction(feature))
    for size in range(2, max_conjunction_size + 1):
        for parts in combinations(eligible, size):
            expanded.add(" && ".join(parts))
    return expanded


def load_rows(
    paths: list[Path],
    split: str,
    feature_mode: str,
    row_filter_feature: str = "",
    max_conjunction_size: int = 1,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = load_json(path)
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            scanned = (row.get("scanned_rows") or [None])[0]
            if not isinstance(scanned, dict):
                features: set[str] = set()
            else:
                public = scanned.get("public") if isinstance(scanned.get("public"), dict) else {}
                features = public_features(public, feature_mode)
            features.update(public_row_counter_features(row))
            if row_filter_feature and row_filter_feature not in features:
                continue
            expanded_features = expand_features(features, max_conjunction_size)
            rows.append(
                {
                    "artifact": str(path),
                    "cost_over_rho": float_value(row.get("cost_over_rho")),
                    "feature_set": expanded_features,
                    "features": sorted(expanded_features),
                    "hit": bool(row.get("hit")),
                    "row": compact_case(row),
                    "split": split,
                    "window": str(row.get("window")),
                }
            )
    return rows


def evaluate(rows: list[dict[str, Any]], feature: str) -> dict[str, Any]:
    selected = [row for row in rows if feature in (row.get("feature_set") or set(row.get("features") or []))]
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


def feature_complexity(name: str) -> tuple[int, int, int]:
    return (name.count(" && "), name.count("|"), len(name))


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
    parser.add_argument("--feature-mode", choices=["structural", "public"], default="structural")
    parser.add_argument("--max-conjunction-size", type=int, default=1)
    parser.add_argument("--min-calibration-hit-windows", type=int, default=1)
    parser.add_argument("--min-calibration-precision", type=float, default=1.0)
    parser.add_argument("--row-filter-feature", default="")
    parser.add_argument("--top-rules", type=int, default=16)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    calibration_paths = parse_paths(args.calibration_artifacts)
    validation_paths = parse_paths(args.validation_artifacts)
    max_conjunction_size = max(1, int_value(args.max_conjunction_size, 1))
    calibration_rows = load_rows(
        calibration_paths,
        "calibration",
        args.feature_mode,
        args.row_filter_feature,
        max_conjunction_size,
    )
    validation_rows = load_rows(
        validation_paths,
        "validation",
        args.feature_mode,
        args.row_filter_feature,
        max_conjunction_size,
    )
    candidate_features = sorted({feature for row in calibration_rows for feature in row.get("features") or []})
    calibration_results = {
        feature: evaluate(calibration_rows, feature)
        for feature in candidate_features
    }
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
    validation_results = {
        feature: evaluate(validation_rows, feature)
        for feature in candidate_features
    }
    selected_validation = validation_results.get(selected_feature, evaluate(validation_rows, selected_feature))
    validation_cost = selected_validation.get("cost_per_hit_window_over_rho")
    if not selected_feature:
        claim_status = "ABSTENTION_GATE_NO_VIABLE_CALIBRATION_RULE"
    elif isinstance(validation_cost, (int, float)) and validation_cost < 1.0:
        claim_status = "ABSTENTION_GATE_FORWARD_BELOW_RHO_NARROW"
    elif int_value(selected_validation.get("selected_window_count")) == 0:
        claim_status = "ABSTENTION_GATE_ABSTAINS_FORWARD"
    elif int_value(selected_validation.get("hit_window_count")) > 0:
        claim_status = "ABSTENTION_GATE_RECOVERS_NEEDS_DENSITY_GAIN"
    else:
        claim_status = "ABSTENTION_GATE_NO_FORWARD_HIT"
    payload = {
        "calibration_artifacts": [str(path) for path in calibration_paths],
        "claim_status": claim_status,
        "created_at": now_iso(),
        "feature_mode": args.feature_mode,
        "honesty_boundary": {
            "assumptions": [
                "Rule selection uses calibration labels only.",
                "Validation applies the selected public predicate without label feedback.",
                "Default structural mode excludes exact transfer and salt values.",
                "Rows come from targeted max-1 expansion artifacts and are direct-source replay.",
            ],
            "evidence": "TOY-EVIDENCE / MODEL-BOUND / PUBLIC-ABSTENTION-SCOUT",
            "not_claimed": [
                "complete faster-than-rho prime-field ECDLP algorithm",
                "deployment-relevant attack",
                "shared-product/source-charged collector",
            ],
        },
        "schema": "ecdlp.low_term_total2_known_column_targeted_abstention_gate_scout.v2",
        "selection_parameters": {
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
