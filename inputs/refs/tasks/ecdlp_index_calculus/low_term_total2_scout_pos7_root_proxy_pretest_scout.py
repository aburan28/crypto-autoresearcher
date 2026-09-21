#!/usr/bin/env python3
"""Scout cheap root-association proxies for double ``[11,15]`` rows.

The double ``[11,15]`` compatibility condition is not visible in coarse source
metadata or selected-leaf signatures.  This scout moves to the next boundary:
features available after selected-leaf gcd/root association but before relation
event verification.  It measures whether scout-7 hit coverage, scheduled-row
coverage, or candidate ordering predicts the double ``[11,15]`` rank-gain rows.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_critical_leaf_probe as critical_leaf_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from low_term_total2_auxiliary_relation_event_assembly_scout import canonical_rows
from low_term_total2_scout_pos7_leaf_signature_pretest_scout import source_case_index


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


def attempt_key(attempt: dict[str, Any]) -> tuple[str, int, str, int, tuple[str, ...]]:
    return (
        "22050.cf1@11731",
        int_value(attempt.get("transfer_index")),
        str(attempt.get("selector")),
        int_value(attempt.get("top_k")),
        canonical_rows(attempt.get("row_keys")),
    )


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<={threshold}")
        if value >= threshold:
            features.add(f"{name}>={threshold}")
    return features


def root_proxy_profile(source: dict[str, Any], source_case: dict[str, Any]) -> dict[str, Any]:
    _verifier, contexts, _product_factor, max_relations = timing_probe.selected_contexts_from_source_case(source, source_case)
    if not contexts:
        return {}
    covers = []
    scout_pos_counts: Counter[int] = Counter()
    scout_scheduled_counts: Counter[int] = Counter()
    scout_leaf_counts: Counter[int] = Counter()
    candidate_positions: dict[int, int] = {}
    selected_hit_roots_total = 0
    leaf_gcd_hits_total = 0
    leaf_gcd_x_matches_total = 0
    selected_hit_events_proxy_total = 0
    scheduled_trials: set[int] = set()
    row_hit_total = 0
    selected_leaf_count_total = 0
    for context in contexts:
        built = context["built"]
        components = context["components"]
        selected = {int_value(leaf) for leaf in context.get("selected_leaf_indices") or []}
        cover = direct_witness_probe.preassociation_filter_probe.filtered_leaf_gcd_association(
            built["scouts"],
            components,
            int_value(built.get("p")),
            selected,
        )
        covers.append(cover)
        selected_leaf_count_total += len(selected)
        selected_hit_roots_total += int_value(cover.get("selected_hit_root_values"))
        leaf_gcd_hits_total += int_value(cover.get("leaf_gcd_hits"))
        leaf_gcd_x_matches_total += int_value(cover.get("leaf_gcd_x_matches"))
        row_hit_total += sum(int_value(count) for count in (cover.get("row_hit_count") or {}).values())
        scheduled_rows = direct_witness_probe.eval_cover_probe.schedule_rows(
            built["rows"],
            cover["row_hit_count"],
            int_value(built.get("scheduled_row_count")),
        )
        scheduled_originals = {int_value(row.get("original_trial")) for row in scheduled_rows}
        scheduled_trials.update(scheduled_originals)
        ordered_scouts = direct_witness_probe.eval_cover_probe.order_scouts(
            built["scouts"],
            cover["hits_by_scout"],
            scheduled_rows,
            str(built["scout_order"]),
        )
        scout_to_leaf = critical_leaf_probe.scout_leaf_map(components)
        scheduled_by_original = {int_value(row.get("original_trial")): row for row in scheduled_rows}
        for candidate_pos, scout in enumerate(ordered_scouts[:max_relations], start=1):
            scout_pos = int_value(scout.get("scout_pos"))
            candidate_positions.setdefault(scout_pos, candidate_pos)
            hits = [trial for trial in cover["hits_by_scout"].get(scout_pos, []) if trial in scheduled_by_original]
            if hits:
                scout_pos_counts[scout_pos] += len(cover["hits_by_scout"].get(scout_pos, []))
                scout_scheduled_counts[scout_pos] += len(hits)
                scout_leaf_counts[int_value(scout_to_leaf.get(scout_pos))] += len(hits)
                selected_hit_events_proxy_total += len(hits)
    return {
        "candidate_pos_7": candidate_positions.get(7),
        "candidate_pos_8": candidate_positions.get(8),
        "leaf_gcd_hits_total": leaf_gcd_hits_total,
        "leaf_gcd_x_matches_total": leaf_gcd_x_matches_total,
        "row_hit_total": row_hit_total,
        "scheduled_trial_count": len(scheduled_trials),
        "scout7_hit_count": int_value(scout_pos_counts.get(7)),
        "scout7_leaf65_scheduled_hit_count": int_value(scout_leaf_counts.get(65)),
        "scout7_scheduled_hit_count": int_value(scout_scheduled_counts.get(7)),
        "scout8_hit_count": int_value(scout_pos_counts.get(8)),
        "scout8_scheduled_hit_count": int_value(scout_scheduled_counts.get(8)),
        "selected_hit_events_proxy_total": selected_hit_events_proxy_total,
        "selected_hit_roots_total": selected_hit_roots_total,
        "selected_leaf_count_total": selected_leaf_count_total,
        "unique_candidate_scouts_with_hits": len(scout_scheduled_counts),
    }


def profile_features(profile: dict[str, Any], include_order_positions: bool) -> set[str]:
    features: set[str] = set()
    for name in (
        "leaf_gcd_hits_total",
        "leaf_gcd_x_matches_total",
        "row_hit_total",
        "scheduled_trial_count",
        "scout7_hit_count",
        "scout7_leaf65_scheduled_hit_count",
        "scout7_scheduled_hit_count",
        "scout8_hit_count",
        "scout8_scheduled_hit_count",
        "selected_hit_events_proxy_total",
        "selected_hit_roots_total",
        "selected_leaf_count_total",
        "unique_candidate_scouts_with_hits",
    ):
        value = int_value(profile.get(name))
        features.add(f"{name}={value}")
        features.update(bucket_features(name, value, (0, 1, 2, 3, 4, 5, 8, 12)))
    if include_order_positions:
        for name in ("candidate_pos_7", "candidate_pos_8"):
            value = int_value(profile.get(name), -1)
            features.add(f"{name}={value}")
            if value >= 0:
                features.update(bucket_features(name, value, (1, 2, 4, 8, 16)))
    if int_value(profile.get("scout7_scheduled_hit_count")) >= 2:
        features.add("scout7_scheduled_hit_count>=2")
    if int_value(profile.get("scout7_leaf65_scheduled_hit_count")) >= 2:
        features.add("scout7_leaf65_scheduled_hit_count>=2")
    return features


def conjunctions(features: set[str], max_size: int) -> set[str]:
    ordered = sorted(features)
    result = set(ordered)
    for size in range(2, max_size + 1):
        for combo in combinations(ordered, size):
            result.add("|".join(combo))
    return result


def load_rows(
    collector: dict[str, Any],
    include_order_positions: bool,
    max_conjunction_size: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_cache: dict[Path, dict[str, Any]] = {}
    source_index_cache: dict[Path, dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]]] = {}
    profile_cache: dict[tuple[str, int, str, int, tuple[str, ...]], dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for group in collector.get("groups") or []:
        if not isinstance(group, dict):
            continue
        window_start = int_value(group.get("window_start"))
        for attempt_index, attempt in enumerate(group.get("attempts") or []):
            if not isinstance(attempt, dict):
                continue
            source_path = Path(str(attempt.get("source_path") or ""))
            if not source_path.exists():
                errors.append({"attempt_index": attempt_index, "error": "missing_source", "source_path": str(source_path)})
                continue
            if source_path not in source_cache:
                source_cache[source_path] = load_json(source_path)
                source_index_cache[source_path] = source_case_index(source_cache[source_path])
            key = attempt_key(attempt)
            source_case = source_index_cache[source_path].get(key)
            if source_case is None:
                errors.append({"attempt_index": attempt_index, "error": "missing_source_case", "key": list(key), "source_path": str(source_path)})
                continue
            cache_key = (str(source_path), *key)
            if cache_key not in profile_cache:
                try:
                    profile_cache[cache_key] = root_proxy_profile(source_cache[source_path], source_case)
                except Exception as exc:  # noqa: BLE001 - preserve research replay failures.
                    errors.append(
                        {
                            "attempt_index": attempt_index,
                            "error": "root_proxy_profile_failed",
                            "message": str(exc),
                            "key": list(key),
                            "source_path": str(source_path),
                        }
                    )
                    continue
            profile = profile_cache[cache_key]
            support = str(attempt.get("support_multiset") or "")
            is_double = support == "11,15;11,15" and int_value(attempt.get("pos7_11111515_count")) >= 2
            rank_gain = int_value(attempt.get("rank_gain")) > 0
            rows.append(
                {
                    "cost_over_rho": float_value(attempt.get("charged_ops_over_rho")),
                    "features": conjunctions(profile_features(profile, include_order_positions), max_conjunction_size),
                    "is_double_pos7_11_15": is_double,
                    "is_double_rank_gain": is_double and rank_gain,
                    "rank_gain": rank_gain,
                    "row": {
                        **profile,
                        "attempt_index": attempt_index,
                        "cost_over_rho": attempt.get("charged_ops_over_rho"),
                        "is_double_pos7_11_15": is_double,
                        "is_double_rank_gain": is_double and rank_gain,
                        "public_key_verified": attempt.get("public_key_verified"),
                        "rank": attempt.get("rank"),
                        "rank_gain": attempt.get("rank_gain"),
                        "row_keys": attempt.get("row_keys") or [],
                        "source_path": str(source_path),
                        "support_multiset": support,
                        "transfer_index": attempt.get("transfer_index"),
                        "window": group.get("window"),
                    },
                    "transfer_index": int_value(attempt.get("transfer_index")),
                    "window_start": window_start,
                }
            )
    return sorted(rows, key=lambda item: (item["window_start"], item["transfer_index"], str(item["row"].get("source_path")))), errors


def split_rows(rows: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [row for row in rows if int_value(row.get("window_start")) <= calibration_end],
        [row for row in rows if int_value(row.get("window_start")) > calibration_end],
    )


def is_positive(row: dict[str, Any], label_name: str) -> bool:
    if label_name == "double_pos7_11_15":
        return bool(row.get("is_double_pos7_11_15"))
    if label_name == "double_rank_gain":
        return bool(row.get("is_double_rank_gain"))
    if label_name == "rank_gain":
        return bool(row.get("rank_gain"))
    raise ValueError(f"unknown label {label_name!r}")


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


def claim_status(selected: dict[str, Any] | None) -> str:
    if selected is None:
        return "SCOUT_POS7_ROOT_PROXY_NO_VIABLE_CALIBRATION_RULE"
    validation = selected.get("validation") if isinstance(selected.get("validation"), dict) else {}
    positives = int_value(validation.get("positive_count"))
    cost = validation.get("cost_per_positive_over_rho")
    if positives <= 0:
        return "SCOUT_POS7_ROOT_PROXY_RULE_MISSES_VALIDATION"
    if cost is not None and float_value(cost) < 1.0:
        return "SCOUT_POS7_ROOT_PROXY_RULE_BELOW_RHO"
    return "SCOUT_POS7_ROOT_PROXY_RULE_VALIDATES_ABOVE_RHO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", required=True)
    parser.add_argument("--calibration-end", type=int, default=3831)
    parser.add_argument("--label", choices=["double_pos7_11_15", "double_rank_gain", "rank_gain"], default="double_rank_gain")
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--include-order-positions", action="store_true")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collector_path = Path(args.collector)
    collector = load_json(collector_path)
    rows, errors = load_rows(collector, args.include_order_positions, args.max_conjunction_size)
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
            "collector": str(collector_path),
        },
        "claim_status": claim_status(selected),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: root-association cover features are computed before relation-event verification.",
            "This is a pretest diagnostic, not a full source-charged/shared-product collector.",
            "A validating rule is a work order for a cheaper collector, not a deployed-curve ECDLP break.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "include_order_positions": args.include_order_positions,
            "label": args.label,
            "max_conjunction_size": args.max_conjunction_size,
            "min_calibration_hits": args.min_calibration_hits,
            "min_calibration_precision": args.min_calibration_precision,
        },
        "rows": [row["row"] for row in rows],
        "rules": rules[:20],
        "schema": "ecdlp.low_term_total2_scout_pos7_root_proxy_pretest_scout.v1",
        "selected_rule": selected,
        "split_summary": {
            "calibration_positive_count": sum(1 for row in calibration if is_positive(row, args.label)),
            "calibration_row_count": len(calibration),
            "validation_positive_count": sum(1 for row in validation if is_positive(row, args.label)),
            "validation_row_count": len(validation),
        },
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "error_count": len(errors),
                "selected_rule": selected["rule"] if selected else None,
                "split_summary": payload["split_summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
