#!/usr/bin/env python3
"""Scout row-side and coefficient tokens for the scout-7 double preform.

The public source-case ordering scout showed that transfer/salt/row-leaf
metadata only trims a few no-hit cases.  This follow-up moves one layer deeper:
for every source case it builds

* row-side hit-polynomial tokens from the selected source context, and
* point-match coefficient tokens from the scout-7 preform boundary.

It then asks whether calibration-selected tokens can stop a source-group stream
on rank-gain double ``[11,15]`` cases before the aggregate cost exceeds rho.
The token stream is still model-bound: point-match coefficient tokens are only
available after the preform scan for that source case, so no-hit cases are
charged before the token can fire.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from low_term_total2_scout_pos7_preform_source_charged_collector import (
    artifact_window,
    case_key,
    int_value,
    load_json,
    preform_accepts,
    rank_labels_by_source_case,
    ratio,
    scan_preform_case,
    source_cases,
    write_json,
)
from low_term_total2_scout_pos7_source_case_ordering_scout import public_profile


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def label(values: list[Any]) -> str:
    return ",".join(str(value) for value in values) if values else "none"


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<={threshold}")
        if value >= threshold:
            features.add(f"{name}>={threshold}")
    return features


def conjunctions(features: set[str], max_size: int) -> set[str]:
    ordered = sorted(features)
    result = set(ordered)
    for size in range(2, max_size + 1):
        for combo in combinations(ordered, size):
            result.add("|".join(combo))
    return result


def modular_multiset(values: list[int], modulus: int) -> str:
    return label(sorted(value % modulus for value in values))


def gap_bucket(gap: int) -> str:
    if gap <= 0:
        return "0"
    if gap <= 2:
        return "1_2"
    if gap <= 4:
        return "3_4"
    if gap <= 8:
        return "5_8"
    if gap <= 16:
        return "9_16"
    return "17_plus"


def point_match_token_features(attempt: dict[str, Any], include_exact_residue: bool) -> set[str]:
    matches = [row for row in attempt.get("point_matches") or [] if isinstance(row, dict)]
    pos7 = [
        row
        for row in matches
        if int_value(row.get("scout_pos")) == 7 and str(row.get("terms_label")) == "11,11,15,15"
    ]
    features: set[str] = set()
    if not pos7:
        features.add("pm_coeff_has_pos7=False")
        return features
    q_values = [int_value(row.get("q_coeff")) for row in pos7]
    rhs_values = [int_value(row.get("rhs")) for row in pos7]
    row_salts = [int_value(row.get("row_salt"), -1) for row in pos7 if int_value(row.get("row_salt"), -1) >= 0]
    leaf_indices = [int_value(row.get("leaf_index")) for row in pos7]
    candidate_positions = [int_value(row.get("candidate_pos")) for row in pos7]
    scheduled_trials = [int_value(row.get("scheduled_trial")) for row in pos7]
    original_trials = [int_value(row.get("original_trial")) for row in pos7]
    q_deltas = [abs(q_values[index] - q_values[index - 1]) for index in range(1, len(q_values))]
    rhs_deltas = [abs(rhs_values[index] - rhs_values[index - 1]) for index in range(1, len(rhs_values))]
    salt_gap = max(row_salts) - min(row_salts) if len(row_salts) >= 2 else 0
    scheduled_gap = max(scheduled_trials) - min(scheduled_trials) if len(scheduled_trials) >= 2 else 0
    original_gap = max(original_trials) - min(original_trials) if len(original_trials) >= 2 else 0
    features.update(
        {
            "pm_coeff_has_pos7=True",
            f"pm_candidate_pos_multiset={label(sorted(candidate_positions))}",
            f"pm_leaf_index_multiset={label(sorted(leaf_indices))}",
            f"pm_pos7_count_bucket={min(len(pos7), 3)}",
            f"pm_q_less_rhs_multiset={label(sorted(int(q < rhs) for q, rhs in zip(q_values, rhs_values)))}",
            f"pm_salt_gap_bucket={gap_bucket(salt_gap)}",
            f"pm_scheduled_gap_bucket={gap_bucket(scheduled_gap)}",
            f"pm_original_gap_bucket={gap_bucket(original_gap)}",
        }
    )
    features.update(bucket_features("pm_pos7_count", len(pos7), (1, 2, 3)))
    features.update(bucket_features("pm_salt_gap", salt_gap, (0, 1, 2, 4, 8, 12)))
    features.update(bucket_features("pm_scheduled_gap", scheduled_gap, (0, 1, 2, 4, 8, 16)))
    features.update(bucket_features("pm_original_gap", original_gap, (0, 1, 2, 4, 8, 16)))
    for modulus in (2, 4, 8, 16):
        features.update(
            {
                f"pm_q_mod_{modulus}_multiset={modular_multiset(q_values, modulus)}",
                f"pm_rhs_mod_{modulus}_multiset={modular_multiset(rhs_values, modulus)}",
                f"pm_q_delta_mod_{modulus}_multiset={modular_multiset(q_deltas, modulus)}",
                f"pm_rhs_delta_mod_{modulus}_multiset={modular_multiset(rhs_deltas, modulus)}",
                f"pm_q_plus_rhs_mod_{modulus}_multiset={modular_multiset([q + r for q, r in zip(q_values, rhs_values)], modulus)}",
            }
        )
    if include_exact_residue:
        features.update(
            {
                f"pm_q_mod_32_multiset={modular_multiset(q_values, 32)}",
                f"pm_rhs_mod_32_multiset={modular_multiset(rhs_values, 32)}",
                f"pm_row_salt_mod_16_multiset={modular_multiset(row_salts, 16)}",
            }
        )
    return features


def hit_poly_token_features(source: dict[str, Any], row: dict[str, Any], include_exact_residue: bool) -> tuple[set[str], list[dict[str, Any]]]:
    features: set[str] = set()
    errors: list[dict[str, Any]] = []
    try:
        _verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(source, row)
        hit_lengths: list[int] = []
        hit_first_values: list[int] = []
        hit_sum_values: list[int] = []
        hit_max_values: list[int] = []
        for context in contexts:
            hit_poly = [int_value(value) for value in (context.get("components") or {}).get("hit_poly") or []]
            hit_lengths.append(len(hit_poly))
            if hit_poly:
                hit_first_values.append(hit_poly[0])
                hit_sum_values.append(sum(hit_poly))
                hit_max_values.append(max(hit_poly))
        features.add(f"hp_context_count={len(contexts)}")
        features.add(f"hp_len_multiset={label(sorted(hit_lengths))}")
        if hit_lengths:
            features.update(bucket_features("hp_len_min", min(hit_lengths), (8, 12, 16, 20, 24, 28)))
            features.update(bucket_features("hp_len_max", max(hit_lengths), (8, 12, 16, 20, 24, 28)))
            features.add(f"hp_len_span_bucket={gap_bucket(max(hit_lengths) - min(hit_lengths))}")
        for modulus in (4, 8, 16):
            features.update(
                {
                    f"hp_first_mod_{modulus}_multiset={modular_multiset(hit_first_values, modulus)}",
                    f"hp_sum_mod_{modulus}_multiset={modular_multiset(hit_sum_values, modulus)}",
                    f"hp_max_mod_{modulus}_multiset={modular_multiset(hit_max_values, modulus)}",
                }
            )
        if include_exact_residue:
            features.update(
                {
                    f"hp_first_mod_32_multiset={modular_multiset(hit_first_values, 32)}",
                    f"hp_sum_mod_32_multiset={modular_multiset(hit_sum_values, 32)}",
                }
            )
    except Exception as exc:  # noqa: BLE001 - preserve replay failures as data.
        errors.append({"error": "hit_poly_profile_failed", "message": str(exc)})
        features.add("hp_profile_failed=True")
    return features, errors


def case_features(
    source: dict[str, Any],
    row: dict[str, Any],
    attempt: dict[str, Any],
    include_exact_residue: bool,
    max_conjunction_size: int,
) -> tuple[set[str], list[dict[str, Any]]]:
    hp_features, errors = hit_poly_token_features(source, row, include_exact_residue)
    pm_features = point_match_token_features(attempt, include_exact_residue)
    features = hp_features | pm_features
    return conjunctions(features, max_conjunction_size), errors


def build_groups(
    collector: dict[str, Any],
    calibration_end: int,
    include_exact_residue: bool,
    max_conjunction_size: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    artifacts = collector.get("artifacts") if isinstance(collector.get("artifacts"), dict) else {}
    parameters = collector.get("parameters") if isinstance(collector.get("parameters"), dict) else {}
    source_paths = [Path(str(path)) for path in artifacts.get("source_paths") or []]
    rank_labels = rank_labels_by_source_case(
        [Path(str(path)) for path in artifacts.get("direct_certificates") or []],
        [Path(str(path)) for path in artifacts.get("rank_scorers") or []],
    )
    target = str(parameters.get("target") or "22050.cf1@11731")
    selector = str(parameters.get("selector") or "mode_low_term_support_total5")
    top_k = int_value(parameters.get("top_k"), 16)
    min_transfer = int_value(parameters.get("min_transfer"), 3560)
    source_case_charge_ops = int_value(parameters.get("source_case_charge_ops"), 1)
    accept_rule = str(parameters.get("accept_rule") or "point_match_scout7_double_11111515")
    groups: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for source_path in source_paths:
        source = load_json(source_path)
        window = artifact_window(source_path)
        window_start = window[0] if window else 0
        rows = source_cases(source_path, source, target, selector, top_k, min_transfer)
        cases: list[dict[str, Any]] = []
        for row in rows:
            scan, scan_errors = scan_preform_case(source, row, accept_rule)
            score = rank_labels.get(case_key(source_path, row), {})
            rho = int_value(scan.get("rho"))
            charged_ops = source_case_charge_ops + int_value(scan.get("preform_ops"))
            attempt = {
                **scan,
                "accepted": preform_accepts(scan.get("point_matches") or [], accept_rule),
                "charged_ops": charged_ops,
                "charged_ops_over_rho": ratio(charged_ops, rho),
                "rank_gain": int_value(score.get("rank_gain")) if score else None,
                "row_keys": row.get("row_keys") or [],
                "source_path": str(source_path),
                "transfer_index": int_value(row.get("transfer_index")),
                "unique_factor_relation_gain": int_value(score.get("unique_factor_relation_gain")) if score else None,
            }
            features, feature_errors = case_features(source, row, attempt, include_exact_residue, max_conjunction_size)
            case_positive = bool(attempt.get("accepted")) and int_value(attempt.get("rank_gain")) > 0
            cases.append(
                {
                    "attempt": attempt,
                    "features": features,
                    "is_positive": case_positive,
                    "public_profile": public_profile(row, window_start),
                    "row": {
                        "accepted": attempt.get("accepted"),
                        "charged_ops_over_rho": attempt.get("charged_ops_over_rho"),
                        "feature_count": len(features),
                        "is_positive": case_positive,
                        "point_match_support_multiset": attempt.get("point_match_support_multiset"),
                        "pos7_11111515_point_match_count": attempt.get("pos7_11111515_point_match_count"),
                        "rank_gain": attempt.get("rank_gain"),
                        "row_keys": attempt.get("row_keys") or [],
                        "source_path": str(source_path),
                        "transfer_index": attempt.get("transfer_index"),
                        "unique_factor_relation_gain": attempt.get("unique_factor_relation_gain"),
                    },
                }
            )
            for item in scan_errors + feature_errors:
                errors.append({**item, "source_path": str(source_path), "transfer_index": int_value(row.get("transfer_index"))})
        if cases:
            groups.append(
                {
                    "cases": cases,
                    "source_path": str(source_path),
                    "window": f"{window[0]}_{window[1]}" if window else "",
                    "window_start": window_start,
                }
            )
    groups.sort(key=lambda group: (int_value(group.get("window_start")), str(group.get("source_path"))))
    return groups, errors


def split_groups(groups: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [group for group in groups if int_value(group.get("window_start")) <= calibration_end],
        [group for group in groups if int_value(group.get("window_start")) > calibration_end],
    )


def flatten_cases(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [case for group in groups for case in group.get("cases") or []]


def evaluate_case_rule(rule: str, groups: list[dict[str, Any]]) -> dict[str, Any]:
    cases = flatten_cases(groups)
    selected = [case for case in cases if rule in case["features"]]
    positives = [case for case in selected if case.get("is_positive")]
    all_positive_count = sum(1 for case in cases if case.get("is_positive"))
    cost = sum(float_value((case.get("attempt") or {}).get("charged_ops_over_rho")) for case in selected)
    return {
        "cost_over_rho": round(cost, 8),
        "cost_per_positive_over_rho": round(cost / len(positives), 8) if positives else None,
        "positive_count": len(positives),
        "precision": round(len(positives) / len(selected), 8) if selected else None,
        "recall": round(len(positives) / all_positive_count, 8) if all_positive_count else None,
        "selected_count": len(selected),
        "selected_rows": [case["row"] for case in selected[:20]],
    }


def evaluate_stream_rule(rule: str, groups: list[dict[str, Any]]) -> dict[str, Any]:
    selected_groups: list[dict[str, Any]] = []
    charged_cost = 0.0
    positive_stops = 0
    selected_stops = 0
    total_positive_groups = sum(1 for group in groups if any(case.get("is_positive") for case in group.get("cases") or []))
    attempt_count = 0
    for group in groups:
        stopped_case: dict[str, Any] | None = None
        group_cost = 0.0
        cases = sorted(group.get("cases") or [], key=lambda case: int_value((case.get("attempt") or {}).get("transfer_index")))
        for case in cases:
            attempt_count += 1
            group_cost += float_value((case.get("attempt") or {}).get("charged_ops_over_rho"))
            if rule in case["features"]:
                stopped_case = case
                break
        charged_cost += group_cost
        if stopped_case is not None:
            selected_stops += 1
            if stopped_case.get("is_positive"):
                positive_stops += 1
            selected_groups.append(
                {
                    "charged_ops_over_rho": round(group_cost, 8),
                    "is_positive_stop": bool(stopped_case.get("is_positive")),
                    "source_path": group.get("source_path"),
                    "stop": stopped_case["row"],
                    "window": group.get("window"),
                    "window_start": group.get("window_start"),
                }
            )
    return {
        "attempt_count": attempt_count,
        "cost_over_rho": round(charged_cost, 8),
        "cost_per_positive_over_rho": round(charged_cost / positive_stops, 8) if positive_stops else None,
        "positive_count": positive_stops,
        "precision": round(positive_stops / selected_stops, 8) if selected_stops else None,
        "recall": round(positive_stops / total_positive_groups, 8) if total_positive_groups else None,
        "selected_count": selected_stops,
        "selected_groups": selected_groups[:20],
    }


def choose_rules(
    calibration: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    min_calibration_hits: int,
    min_calibration_precision: float,
) -> list[dict[str, Any]]:
    features = sorted({feature for case in flatten_cases(calibration) for feature in case["features"]})
    rules: list[dict[str, Any]] = []
    for rule in features:
        calibration_stream = evaluate_stream_rule(rule, calibration)
        if int_value(calibration_stream.get("positive_count")) < min_calibration_hits:
            continue
        precision = calibration_stream.get("precision")
        if precision is None or float_value(precision) < min_calibration_precision:
            continue
        rules.append(
            {
                "calibration_case": evaluate_case_rule(rule, calibration),
                "calibration_stream": calibration_stream,
                "feature_count": rule.count("|") + 1,
                "rule": rule,
                "validation_case": evaluate_case_rule(rule, validation),
                "validation_stream": evaluate_stream_rule(rule, validation),
            }
        )
    rules.sort(
        key=lambda item: (
            float_value((item.get("calibration_stream") or {}).get("cost_per_positive_over_rho"), 999999.0),
            -float_value((item.get("calibration_stream") or {}).get("precision"), 0.0),
            int_value(item.get("feature_count")),
            str(item.get("rule")),
        )
    )
    return rules


def validation_hit_rules(rules: list[dict[str, Any]], limit: int = 20) -> list[dict[str, Any]]:
    hits = [rule for rule in rules if int_value((rule.get("validation_stream") or {}).get("positive_count")) > 0]
    hits.sort(
        key=lambda item: (
            float_value((item.get("validation_stream") or {}).get("cost_per_positive_over_rho"), 999999.0),
            -float_value((item.get("validation_stream") or {}).get("precision"), 0.0),
            int_value(item.get("feature_count")),
            str(item.get("rule")),
        )
    )
    return hits[:limit]


def summarize(groups: list[dict[str, Any]]) -> dict[str, Any]:
    cases = flatten_cases(groups)
    return {
        "case_count": len(cases),
        "group_count": len(groups),
        "positive_case_count": sum(1 for case in cases if case.get("is_positive")),
        "positive_group_count": sum(1 for group in groups if any(case.get("is_positive") for case in group.get("cases") or [])),
    }


def claim_status(selected: dict[str, Any] | None) -> str:
    if selected is None:
        return "SCOUT_POS7_POINT_MATCH_TOKEN_NO_CALIBRATION_RULE"
    validation = selected.get("validation_stream") if isinstance(selected.get("validation_stream"), dict) else {}
    positives = int_value(validation.get("positive_count"))
    cost = validation.get("cost_per_positive_over_rho")
    if positives <= 0:
        return "SCOUT_POS7_POINT_MATCH_TOKEN_RULE_MISSES_VALIDATION"
    if cost is not None and float_value(cost) < 1.0:
        return "SCOUT_POS7_POINT_MATCH_TOKEN_BELOW_RHO_STREAM"
    return "SCOUT_POS7_POINT_MATCH_TOKEN_VALIDATES_ABOVE_RHO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", required=True)
    parser.add_argument("--calibration-end", type=int, default=4064)
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--include-exact-residue", action="store_true")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collector_path = Path(args.collector)
    collector = load_json(collector_path)
    groups, errors = build_groups(
        collector,
        args.calibration_end,
        args.include_exact_residue,
        args.max_conjunction_size,
    )
    calibration, validation = split_groups(groups, args.calibration_end)
    rules = choose_rules(
        calibration,
        validation,
        args.min_calibration_hits,
        args.min_calibration_precision,
    )
    selected = rules[0] if rules else None
    hits = validation_hit_rules(rules)
    payload = {
        "artifacts": {
            "collector": str(collector_path),
        },
        "claim_status": claim_status(selected),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: hit-polynomial tokens are row-side source-context features; point-match coefficient tokens require preform scanning the source case.",
            "The stream evaluation charges each attempted source case until the selected token fires or the group is exhausted.",
            "Rank/public-key verification labels are not used as features; they are labels joined only for evaluation.",
            "A below-rho token stream would be a precursor work order for a cheaper source generator, not a deployed-curve ECDLP break.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "include_exact_residue": args.include_exact_residue,
            "max_conjunction_size": args.max_conjunction_size,
            "min_calibration_hits": args.min_calibration_hits,
            "min_calibration_precision": args.min_calibration_precision,
        },
        "rule_count": len(rules),
        "rules": rules[:20],
        "schema": "ecdlp.low_term_total2_scout_pos7_point_match_token_scout.v1",
        "selected_rule": selected,
        "split_summary": {
            "calibration": summarize(calibration),
            "validation": summarize(validation),
        },
        "validation_hit_rule_count": sum(1 for rule in rules if int_value((rule.get("validation_stream") or {}).get("positive_count")) > 0),
        "validation_hit_rules": hits,
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "error_count": len(errors),
                "selected_rule": selected["rule"] if selected else None,
                "selected_validation_stream": (selected or {}).get("validation_stream"),
                "split_summary": payload["split_summary"],
                "validation_hit_rule_count": payload["validation_hit_rule_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
