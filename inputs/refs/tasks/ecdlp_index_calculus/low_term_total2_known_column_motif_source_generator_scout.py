#!/usr/bin/env python3
"""Scout a public source generator for known-column relation-support motifs.

The motif oracle gap scout showed that an ideal source generator targeting
relation-support motifs such as [8,11], [9,11], [10,13], [10,14], and [11,13]
would be below rho on the current toy target.  This probe removes the oracle
choice: it learns a scoring model from calibration windows using only public
selected-leaf/source metadata, then evaluates later windows while charging a
small source-row cost for skipped public candidates and direct cost only for
candidates selected for relation scanning.

This is still a scout, not a finished index-calculus algorithm.  The learned
weights are heuristic and target-local; the output is useful only if it
survives fresh validation and then gets ported to real shared-product/source
generation.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from low_term_total2_known_column_motif_oracle_gap_scout import (
    case_supports,
    evaluate_current_pressure,
    evaluate_motif_oracle,
    int_value,
    learned_motifs,
    parse_motifs,
    parse_paths,
    stat,
    support_key,
    window_from_path,
)


SALT_RE = re.compile(r"salt(\d+)")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def salts_from_rows(row_keys: list[Any]) -> tuple[int, ...]:
    salts: list[int] = []
    for row_key in row_keys:
        match = SALT_RE.search(str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return tuple(salts)


def public_case_features(case: dict[str, Any]) -> set[str]:
    """Return public-only feature names for a selected pressure-screen case."""
    selected = case.get("selected") if isinstance(case.get("selected"), dict) else {}
    metrics = (
        case.get("public_selection_metrics")
        if isinstance(case.get("public_selection_metrics"), dict)
        else {}
    )
    selected_support = tuple(int_value(value) for value in case.get("selected_term_support") or [])
    selected_support_set = set(selected_support)
    known_overlap = tuple(int_value(value) for value in metrics.get("known_overlap") or [])
    unknown_support = tuple(int_value(value) for value in metrics.get("unknown_selected_support") or [])
    priority_overlap = tuple(int_value(value) for value in metrics.get("priority_overlap") or [])
    row_keys = [str(row) for row in selected.get("row_keys") or []]
    salts = salts_from_rows(row_keys)
    top_k = int_value(selected.get("top_k"))
    transfer_index = int_value(selected.get("transfer_index"))
    support_size = len(selected_support)
    known_count = int_value(metrics.get("known_overlap_count"))
    unknown_count = int_value(metrics.get("unknown_selected_support_count"))
    pressure_score = int_value(metrics.get("pressure_score"))
    features = {
        f"topk={top_k}",
        f"support_size={support_size}",
        f"known_count={known_count}",
        f"unknown_count={unknown_count}",
        f"pressure_score={pressure_score}",
        f"topk={top_k}|support_size={support_size}",
        f"topk={top_k}|known_count={known_count}",
        f"known_tuple={','.join(map(str, known_overlap))}",
        f"unknown_tuple={','.join(map(str, unknown_support))}",
        f"priority_tuple={','.join(map(str, priority_overlap))}",
    }
    for threshold in range(6, 13):
        if support_size <= threshold:
            features.add(f"support_size<=%02d" % threshold)
    for threshold in range(2, 8):
        if known_count >= threshold:
            features.add(f"known_count>={threshold}")
    for threshold in range(0, 8):
        if unknown_count <= threshold:
            features.add(f"unknown_count<={threshold}")
    for col in sorted(selected_support_set):
        features.add(f"selected_has_col={col}")
    for col in sorted(set(range(16)) - selected_support_set):
        features.add(f"selected_lacks_col={col}")
    for index, left in enumerate(selected_support):
        for right in selected_support[index + 1 :]:
            features.add(f"selected_pair={left},{right}")
    for modulus in (3, 4, 5, 8, 16, 32):
        features.add(f"transfer_mod_{modulus}={transfer_index % modulus}")
        features.add(f"topk={top_k}|transfer_mod_{modulus}={transfer_index % modulus}")
    if salts:
        salt_sum = sum(salts)
        features.add(f"salt_count={len(salts)}")
        features.add(f"salt_tuple={','.join(map(str, salts))}")
        features.add(f"salt_first={salts[0]}")
        features.add(f"salt_last={salts[-1]}")
        features.add(f"topk={top_k}|salt_first={salts[0]}")
        features.add(f"topk={top_k}|salt_last={salts[-1]}")
        for modulus in (3, 4, 5, 8, 16, 32):
            features.add(f"salt_sum_mod_{modulus}={salt_sum % modulus}")
            features.add(f"topk={top_k}|salt_sum_mod_{modulus}={salt_sum % modulus}")
        if len(salts) >= 2:
            gap = abs(salts[1] - salts[0])
            features.add(f"salt_gap={gap}")
            features.add(f"salt_order={'inc' if salts[0] < salts[1] else 'dec_or_eq'}")
            features.add(f"topk={top_k}|salt_gap={gap}")
            for modulus in (3, 4, 5, 8, 16):
                features.add(f"salt_gap_mod_{modulus}={gap % modulus}")
    return features


def compact_public_case(case: dict[str, Any] | None) -> dict[str, Any] | None:
    if case is None:
        return None
    return {
        "case_index": case.get("case_index"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "hit": case.get("hit"),
        "known_structural_motifs": [list(motif) for motif in case.get("known_structural_motifs") or []],
        "public_score": case.get("public_score"),
        "row_keys": case.get("row_keys"),
        "top_k": case.get("top_k"),
        "transfer_index": case.get("transfer_index"),
        "unknown_motifs": [list(motif) for motif in case.get("unknown_motifs") or []],
        "verified_motifs": [list(motif) for motif in case.get("verified_motifs") or []],
    }


def load_window(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    start, end = window_from_path(path)
    cases: list[dict[str, Any]] = []
    for index, case in enumerate(payload.get("case_results") or []):
        if not isinstance(case, dict):
            continue
        selected = case.get("selected") if isinstance(case.get("selected"), dict) else {}
        motifs = case_supports(case)
        public_features = public_case_features(case)
        cases.append(
            {
                "artifact": str(path),
                "case_index": index,
                "direct_ops_over_rho": case.get("direct_ops_over_rho"),
                "features": sorted(public_features),
                "hit": bool(case.get("public_known_factor_verified")),
                "known_support_form_count": int_value(case.get("known_support_form_count")),
                **motifs,
                "row_keys": selected.get("row_keys") or [],
                "top_k": int_value(selected.get("top_k")),
                "transfer_index": int_value(selected.get("transfer_index")),
            }
        )
    return {
        "artifact": str(path),
        "end": end,
        "start": start,
        "summary": payload.get("summary") or {},
        "cases": cases,
    }


def has_motif(case: dict[str, Any], fields: tuple[str, ...], motifs: set[tuple[int, ...]]) -> bool:
    if not motifs:
        return False
    for field in fields:
        if any(tuple(motif) in motifs for motif in case.get(field) or []):
            return True
    return False


def target_label(case: dict[str, Any], target_motifs: set[tuple[int, ...]]) -> bool:
    return has_motif(case, ("known_structural_motifs", "verified_motifs"), target_motifs)


def avoid_only_label(case: dict[str, Any], avoid_motifs: set[tuple[int, ...]]) -> bool:
    has_known = bool(case.get("known_structural_motifs") or case.get("verified_motifs"))
    return (not has_known) and has_motif(case, ("unknown_motifs",), avoid_motifs)


def learn_feature_weights(
    calibration: list[dict[str, Any]],
    target_motifs: set[tuple[int, ...]],
    avoid_motifs: set[tuple[int, ...]],
    min_feature_support: int,
) -> dict[str, Any]:
    total = Counter()
    target = Counter()
    avoid = Counter()
    cases = [case for window in calibration for case in window["cases"]]
    target_case_count = 0
    avoid_case_count = 0
    for case in cases:
        is_target = target_label(case, target_motifs)
        is_avoid = avoid_only_label(case, avoid_motifs)
        if is_target:
            target_case_count += 1
        if is_avoid:
            avoid_case_count += 1
        for feature in case.get("features") or []:
            total[feature] += 1
            if is_target:
                target[feature] += 1
            if is_avoid:
                avoid[feature] += 1
    total_case_count = max(1, len(cases))
    base_target = (target_case_count + 0.5) / (total_case_count + 1.0)
    base_avoid = (avoid_case_count + 0.5) / (total_case_count + 1.0)
    weights: dict[str, dict[str, Any]] = {}
    for feature, count in total.items():
        if count < min_feature_support:
            continue
        target_precision = (target[feature] + 0.5) / (count + 1.0)
        avoid_precision = (avoid[feature] + 0.5) / (count + 1.0)
        target_weight = math.log(target_precision / base_target)
        avoid_weight = math.log(avoid_precision / base_avoid)
        weights[feature] = {
            "avoid_count": avoid[feature],
            "avoid_precision": round(avoid_precision, 6),
            "avoid_weight": avoid_weight,
            "count": count,
            "target_count": target[feature],
            "target_precision": round(target_precision, 6),
            "target_weight": target_weight,
        }
    return {
        "base_rates": {
            "avoid_case_count": avoid_case_count,
            "avoid_rate": round(base_avoid, 6),
            "target_case_count": target_case_count,
            "target_rate": round(base_target, 6),
            "total_case_count": len(cases),
        },
        "weights": weights,
    }


def score_case(
    case: dict[str, Any],
    weights: dict[str, dict[str, Any]],
    avoid_penalty: float,
    max_features: int,
) -> tuple[float, list[dict[str, Any]]]:
    contributions: list[dict[str, Any]] = []
    for feature in case.get("features") or []:
        row = weights.get(feature)
        if not row:
            continue
        contribution = float(row["target_weight"]) - avoid_penalty * max(0.0, float(row["avoid_weight"]))
        if contribution <= 0:
            continue
        contributions.append(
            {
                "avoid_weight": round(float(row["avoid_weight"]), 6),
                "contribution": round(contribution, 6),
                "feature": feature,
                "target_weight": round(float(row["target_weight"]), 6),
            }
        )
    contributions.sort(key=lambda item: (-float(item["contribution"]), item["feature"]))
    kept = contributions[:max_features]
    return round(sum(float(item["contribution"]) for item in kept), 8), kept


def annotate_scores(
    windows: list[dict[str, Any]],
    weights: dict[str, dict[str, Any]],
    avoid_penalty: float,
    max_features: int,
) -> list[dict[str, Any]]:
    annotated: list[dict[str, Any]] = []
    for window in windows:
        cases = []
        for case in window["cases"]:
            score, contributions = score_case(case, weights, avoid_penalty, max_features)
            cases.append({**case, "public_score": score, "score_contributions": contributions})
        annotated.append({**window, "cases": cases})
    return annotated


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    hits = [row for row in rows if row.get("hit")]
    structural = [row for row in rows if row.get("selected_structural") or row.get("hit")]
    costs = [float_value(row.get("cost_over_rho")) for row in rows]
    total = sum(costs)
    return {
        "cost_over_rho": stat(costs),
        "cost_per_hit_window_over_rho": round(total / len(hits), 8) if hits else None,
        "cost_per_structural_window_over_rho": round(total / len(structural), 8) if structural else None,
        "direct_scan_count": sum(int_value(row.get("direct_scan_count")) for row in rows),
        "hit_window_count": len(hits),
        "rows": rows,
        "selected_window_count": sum(1 for row in rows if int_value(row.get("direct_scan_count")) > 0),
        "source_row_count": sum(int_value(row.get("source_row_count")) for row in rows),
        "structural_window_count": len(structural),
        "window_count": len(rows),
    }


def evaluate_streaming_filter(
    windows: list[dict[str, Any]],
    threshold: float,
    source_row_cost_over_rho: float,
) -> dict[str, Any]:
    rows = []
    for window in windows:
        cost = 0.0
        source_rows = 0
        direct_scans = 0
        skipped = 0
        selected_structural = None
        hit_case = None
        for case in window["cases"]:
            source_rows += 1
            cost += source_row_cost_over_rho
            if float_value(case.get("public_score")) < threshold:
                skipped += 1
                continue
            direct_scans += 1
            cost += float_value(case.get("direct_ops_over_rho"))
            if selected_structural is None and (case.get("known_structural_motifs") or case.get("verified_motifs")):
                selected_structural = case
            if case.get("hit"):
                hit_case = case
                break
        rows.append(
            {
                "cost_over_rho": round(cost, 8),
                "direct_scan_count": direct_scans,
                "hit": hit_case is not None,
                "hit_case": compact_public_case(hit_case),
                "selected_structural": selected_structural is not None,
                "skipped_source_row_count": skipped,
                "source_row_count": source_rows,
                "structural_case": compact_public_case(selected_structural),
                "threshold": round(threshold, 8),
                "window": f"{window['start']}_{window['end']}",
            }
        )
    return summarize_rows(rows)


def evaluate_ranked_filter(
    windows: list[dict[str, Any]],
    threshold: float,
    source_row_cost_over_rho: float,
) -> dict[str, Any]:
    rows = []
    for window in windows:
        cost = source_row_cost_over_rho * len(window["cases"])
        candidates = [
            case for case in window["cases"]
            if float_value(case.get("public_score")) >= threshold
        ]
        candidates.sort(
            key=lambda case: (
                -float_value(case.get("public_score")),
                int_value(case.get("transfer_index")),
                int_value(case.get("top_k")),
                int_value(case.get("case_index")),
            )
        )
        direct_scans = 0
        selected_structural = None
        hit_case = None
        for case in candidates:
            direct_scans += 1
            cost += float_value(case.get("direct_ops_over_rho"))
            if selected_structural is None and (case.get("known_structural_motifs") or case.get("verified_motifs")):
                selected_structural = case
            if case.get("hit"):
                hit_case = case
                break
        rows.append(
            {
                "candidate_count": len(candidates),
                "cost_over_rho": round(cost, 8),
                "direct_scan_count": direct_scans,
                "hit": hit_case is not None,
                "hit_case": compact_public_case(hit_case),
                "selected_structural": selected_structural is not None,
                "source_row_count": len(window["cases"]),
                "structural_case": compact_public_case(selected_structural),
                "threshold": round(threshold, 8),
                "window": f"{window['start']}_{window['end']}",
            }
        )
    return summarize_rows(rows)


def choose_threshold(
    calibration: list[dict[str, Any]],
    source_row_cost_over_rho: float,
    min_hit_windows: int,
) -> dict[str, Any]:
    scores = sorted(
        {
            round(float_value(case.get("public_score")), 8)
            for window in calibration
            for case in window["cases"]
        },
        reverse=True,
    )
    thresholds = scores + [0.0]
    candidates = []
    for threshold in thresholds:
        result = evaluate_streaming_filter(calibration, threshold, source_row_cost_over_rho)
        hit_count = int_value(result.get("hit_window_count"))
        cost_per_hit = result.get("cost_per_hit_window_over_rho")
        if hit_count < min_hit_windows or cost_per_hit is None:
            continue
        candidates.append(
            {
                "cost_per_hit_window_over_rho": cost_per_hit,
                "direct_scan_count": result.get("direct_scan_count"),
                "hit_window_count": hit_count,
                "selected_window_count": result.get("selected_window_count"),
                "source_row_count": result.get("source_row_count"),
                "threshold": threshold,
            }
        )
    if not candidates:
        fallback = evaluate_streaming_filter(calibration, 0.0, source_row_cost_over_rho)
        return {
            "fallback": True,
            "result": fallback,
            "threshold": 0.0,
            "top_candidates": [],
        }
    candidates.sort(
        key=lambda row: (
            float_value(row.get("cost_per_hit_window_over_rho"), 999.0),
            -int_value(row.get("hit_window_count")),
            int_value(row.get("direct_scan_count")),
            -float_value(row.get("threshold")),
        )
    )
    best = candidates[0]
    return {
        "fallback": False,
        "result": evaluate_streaming_filter(calibration, float_value(best["threshold"]), source_row_cost_over_rho),
        "threshold": float_value(best["threshold"]),
        "top_candidates": candidates[:12],
    }


def top_feature_rows(model: dict[str, Any], limit: int = 24) -> list[dict[str, Any]]:
    rows = []
    for feature, weight in model["weights"].items():
        rows.append(
            {
                "avoid_count": weight["avoid_count"],
                "avoid_precision": weight["avoid_precision"],
                "avoid_weight": round(float(weight["avoid_weight"]), 6),
                "count": weight["count"],
                "feature": feature,
                "target_count": weight["target_count"],
                "target_precision": weight["target_precision"],
                "target_weight": round(float(weight["target_weight"]), 6),
            }
        )
    rows.sort(key=lambda row: (-float(row["target_weight"]), float(row["avoid_weight"]), row["feature"]))
    return rows[:limit]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--avoid-penalty", type=float, default=0.75)
    parser.add_argument("--calibration-end-max", type=int, default=3055)
    parser.add_argument("--max-positive-features", type=int, default=8)
    parser.add_argument("--min-calibration-hit-windows", type=int, default=4)
    parser.add_argument("--min-feature-support", type=int, default=2)
    parser.add_argument("--min-motif-count", type=int, default=2)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--seed-known-motifs",
        default="8:11,9:11,10:13,10:14,11:13",
        help="comma-separated motifs, each encoded with colon-separated columns",
    )
    parser.add_argument(
        "--source-row-cost-over-rho",
        type=float,
        default=1.0 / 137.0,
        help="Cost charged for generating/inspecting a skipped public source row.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = parse_paths(args.artifacts)
    windows = [load_window(path) for path in paths]
    calibration = [window for window in windows if int_value(window.get("end")) <= args.calibration_end_max]
    validation = [window for window in windows if int_value(window.get("end")) > args.calibration_end_max]
    oracle_windows = [
        {
            **window,
            "cases": [
                {key: value for key, value in case.items() if key not in {"features", "score_contributions"}}
                for case in window["cases"]
            ],
        }
        for window in windows
    ]
    oracle_calibration = [window for window in oracle_windows if int_value(window.get("end")) <= args.calibration_end_max]
    oracle_validation = [window for window in oracle_windows if int_value(window.get("end")) > args.calibration_end_max]
    target_motifs, avoid_motifs = learned_motifs(
        oracle_calibration,
        args.min_motif_count,
        parse_motifs(args.seed_known_motifs),
    )
    model = learn_feature_weights(
        calibration,
        target_motifs,
        avoid_motifs,
        args.min_feature_support,
    )
    scored_calibration = annotate_scores(
        calibration,
        model["weights"],
        args.avoid_penalty,
        args.max_positive_features,
    )
    scored_validation = annotate_scores(
        validation,
        model["weights"],
        args.avoid_penalty,
        args.max_positive_features,
    )
    threshold = choose_threshold(
        scored_calibration,
        args.source_row_cost_over_rho,
        args.min_calibration_hit_windows,
    )
    chosen_threshold = float_value(threshold["threshold"])
    public_streaming = evaluate_streaming_filter(
        scored_validation,
        chosen_threshold,
        args.source_row_cost_over_rho,
    )
    public_ranked = evaluate_ranked_filter(
        scored_validation,
        chosen_threshold,
        args.source_row_cost_over_rho,
    )
    current = evaluate_current_pressure(oracle_validation)
    oracle = evaluate_motif_oracle(oracle_validation, target_motifs, avoid_motifs)
    stream_cost = public_streaming.get("cost_per_hit_window_over_rho")
    if isinstance(stream_cost, (int, float)) and stream_cost < 1.0:
        claim_status = "PUBLIC_MOTIF_SCOUT_BELOW_RHO_SOURCE_CHARGED_CANDIDATE"
    elif int_value(public_streaming.get("hit_window_count")) > 0:
        claim_status = "PUBLIC_MOTIF_SCOUT_RECOVERS_NEEDS_DENSITY_GAIN"
    else:
        claim_status = "PUBLIC_MOTIF_SCOUT_NO_FORWARD_HIT"
    payload = {
        "artifacts": [str(path) for path in paths],
        "calibration_end_max": args.calibration_end_max,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "feature_model": {
            "avoid_penalty": args.avoid_penalty,
            "base_rates": model["base_rates"],
            "max_positive_features": args.max_positive_features,
            "min_feature_support": args.min_feature_support,
            "top_positive_features": top_feature_rows(model),
        },
        "honesty_boundary": {
            "assumptions": [
                "The score uses only public selected-leaf/source metadata on validation cases.",
                "Feature weights are learned from relation labels on calibration windows.",
                "Skipped validation source rows are charged with source_row_cost_over_rho.",
                "This is still direct-source pressure-screen data, not a shared-product collector.",
            ],
            "evidence": "TOY-EVIDENCE / MODEL-BOUND / HEURISTIC-COST / PUBLIC-FEATURE-SCOUT",
            "not_claimed": [
                "complete faster-than-rho prime-field ECDLP algorithm",
                "target-independent motif predictor",
                "deployment-relevant attack",
            ],
        },
        "learned_motifs": {
            "avoid_motifs": [list(motif) for motif in sorted(avoid_motifs)],
            "min_motif_count": args.min_motif_count,
            "seed_known_motifs": [list(motif) for motif in sorted(parse_motifs(args.seed_known_motifs))],
            "target_motifs": [list(motif) for motif in sorted(target_motifs)],
        },
        "schema": "ecdlp.low_term_total2_known_column_motif_source_generator_scout.v1",
        "selection_results": {
            "current_pressure_order": current,
            "motif_oracle": oracle,
            "public_ranked_filter": public_ranked,
            "public_streaming_filter": public_streaming,
        },
        "source_row_cost_over_rho": round(args.source_row_cost_over_rho, 8),
        "summary": {
            "current_cost_per_hit_window_over_rho": current.get("cost_per_hit_window_over_rho"),
            "motif_oracle_cost_per_hit_window_over_rho": oracle.get("cost_per_hit_window_over_rho"),
            "public_ranked_cost_per_hit_window_over_rho": public_ranked.get("cost_per_hit_window_over_rho"),
            "public_streaming_cost_per_hit_window_over_rho": public_streaming.get("cost_per_hit_window_over_rho"),
            "public_streaming_hit_window_count": public_streaming.get("hit_window_count"),
            "public_streaming_threshold": round(chosen_threshold, 8),
        },
        "threshold_selection": threshold,
        "window_split": {
            "calibration": [f"{window['start']}_{window['end']}" for window in calibration],
            "validation": [f"{window['start']}_{window['end']}" for window in validation],
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": claim_status}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
