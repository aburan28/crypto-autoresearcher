#!/usr/bin/env python3
"""Scout a first-source-case preform gate for the scout-7 relation branch.

The source-abstention replay found that ``public_key_verified`` is a strong
diagnostic for the useful scout-7 branch, but that flag is produced after
relation forms are verified against the public key.  This scout tests the
nearest cheaper precursor that is already present in the charged collector:
run only the first public source case to the point-match/preform boundary for
every source artifact, then continue the full source scan only for groups whose
first-case preform features pass a calibrated rule.

This is not a pure source gate.  It charges the first-case preform work for
every group and treats any below-rho signal as a work order for a cheaper
micro-kernel or source policy.
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


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<={threshold}")
        if value >= threshold:
            features.add(f"{name}>={threshold}")
    return features


def multiset_label(values: list[Any] | tuple[Any, ...]) -> str:
    return ",".join(str(value) for value in values) if values else "none"


def offset_bucket(offset: int) -> str:
    if offset <= 0:
        return "0"
    if offset <= 1:
        return "1"
    if offset <= 3:
        return "2_3"
    if offset <= 5:
        return "4_5"
    return "6_7"


def gap_bucket(gap: int) -> str:
    if gap <= 0:
        return "0"
    if gap <= 2:
        return "1_2"
    if gap <= 4:
        return "3_4"
    if gap <= 8:
        return "5_8"
    if gap <= 12:
        return "9_12"
    return "13_plus"


def feature_conjunctions(features: set[str], max_size: int) -> set[str]:
    ordered = sorted(features)
    result = set(ordered)
    for size in range(2, max_size + 1):
        for combo in combinations(ordered, size):
            result.add("|".join(combo))
    return result


def point_match_rows(attempt: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in attempt.get("point_matches") or [] if isinstance(row, dict)]


def first_attempt_features(
    group: dict[str, Any],
    attempt: dict[str, Any],
    include_form_residue_features: bool,
) -> set[str]:
    matches = point_match_rows(attempt)
    scout_positions = sorted(int_value(row.get("scout_pos")) for row in matches)
    terms_labels = sorted(str(row.get("terms_label") or "none") for row in matches)
    support_labels = sorted(str(row.get("factor_support_label") or "none") for row in matches)
    candidate_positions = sorted(int_value(row.get("candidate_pos")) for row in matches)
    leaf_indices = sorted(int_value(row.get("leaf_index")) for row in matches)
    row_salts = sorted(int_value(row.get("row_salt"), -1) for row in matches if int_value(row.get("row_salt"), -1) >= 0)
    scheduled_trials = sorted(int_value(row.get("scheduled_trial")) for row in matches)
    original_trials = sorted(int_value(row.get("original_trial")) for row in matches)
    point_match_count = int_value(attempt.get("point_match_count"), len(matches))
    pos7_count = int_value(attempt.get("pos7_11111515_point_match_count"))
    distinct_forms = int_value(attempt.get("pos7_11111515_distinct_form_count"))
    distinct_rows = int_value(attempt.get("pos7_11111515_distinct_row_count"))
    selected_leaf_count = int_value(attempt.get("selected_leaf_count"))
    selected_row_count = int_value(attempt.get("selected_row_count"))
    transfer_offset = int_value(attempt.get("transfer_index")) - int_value(group.get("window_start"))
    salt_gap = row_salts[-1] - row_salts[0] if len(row_salts) >= 2 else 0
    scheduled_gap = scheduled_trials[-1] - scheduled_trials[0] if len(scheduled_trials) >= 2 else 0
    original_gap = original_trials[-1] - original_trials[0] if len(original_trials) >= 2 else 0
    scout_counter = Counter(scout_positions)
    terms_counter = Counter(terms_labels)
    support_counter = Counter(support_labels)
    candidate_counter = Counter(candidate_positions)
    has_double_pos7_11111515 = pos7_count >= 2 and terms_counter.get("11,11,15,15", 0) >= 2
    features: set[str] = {
        "has_first_attempt=True",
        f"first_candidate_pos_multiset={multiset_label(candidate_positions)}",
        f"first_distinct_candidate_pos_count={len(candidate_counter)}",
        f"first_distinct_leaf_index_count={len(set(leaf_indices))}",
        f"first_distinct_scout_pos_count={len(scout_counter)}",
        f"first_distinct_support_label_count={len(support_counter)}",
        f"first_distinct_terms_label_count={len(terms_counter)}",
        f"first_has_double_pos7_11111515={has_double_pos7_11111515}",
        f"first_has_point_match={bool(matches)}",
        f"first_has_scout7_11111515={pos7_count > 0}",
        f"first_point_match_candidate_pos_multiset={attempt.get('point_match_candidate_pos_multiset') or multiset_label(candidate_positions)}",
        f"first_point_match_count_bucket={min(point_match_count, 4)}",
        f"first_point_match_scout_pos_multiset={attempt.get('point_match_scout_pos_multiset') or multiset_label(scout_positions)}",
        f"first_point_match_support_multiset={attempt.get('point_match_support_multiset') or multiset_label(support_labels)}",
        f"first_point_match_terms_multiset={attempt.get('point_match_terms_multiset') or ';'.join(terms_labels) if terms_labels else 'none'}",
        f"first_pos7_11111515_distinct_form_count={distinct_forms}",
        f"first_pos7_11111515_distinct_row_count={distinct_rows}",
        f"first_pos7_11111515_point_match_count={pos7_count}",
        f"first_salt_gap_bucket={gap_bucket(salt_gap)}",
        f"first_scheduled_trial_gap_bucket={gap_bucket(scheduled_gap)}",
        f"first_selected_leaf_count={selected_leaf_count}",
        f"first_selected_row_count={selected_row_count}",
        f"first_source_policy={attempt.get('source_policy') or 'none'}",
        f"first_transfer_offset_bucket={offset_bucket(transfer_offset)}",
    }
    features.update(bucket_features("first_point_match_count", point_match_count, (0, 1, 2, 3, 4)))
    features.update(bucket_features("first_pos7_11111515_point_match_count", pos7_count, (0, 1, 2, 3)))
    features.update(bucket_features("first_pos7_11111515_distinct_form_count", distinct_forms, (0, 1, 2, 3)))
    features.update(bucket_features("first_pos7_11111515_distinct_row_count", distinct_rows, (0, 1, 2, 3)))
    features.update(bucket_features("first_selected_leaf_count", selected_leaf_count, (1, 2, 3, 4, 5)))
    features.update(bucket_features("first_selected_row_count", selected_row_count, (1, 2, 3)))
    features.update(bucket_features("first_transfer_offset", transfer_offset, (0, 1, 2, 3, 5, 7)))
    features.update(bucket_features("first_salt_gap", salt_gap, (0, 1, 2, 4, 8, 12)))
    features.update(bucket_features("first_scheduled_trial_gap", scheduled_gap, (0, 1, 2, 4, 8, 16)))
    features.update(bucket_features("first_original_trial_gap", original_gap, (0, 1, 2, 4, 8, 16)))
    for scout_pos in sorted(scout_counter):
        features.add(f"first_has_scout_pos={scout_pos}")
    for terms_label in sorted(terms_counter):
        features.add(f"first_has_terms={terms_label}")
    for support_label in sorted(support_counter):
        features.add(f"first_has_support={support_label}")
    for candidate_pos in sorted(candidate_counter):
        features.add(f"first_has_candidate_pos={candidate_pos}")
    if include_form_residue_features:
        q_coeffs = [int_value(row.get("q_coeff")) for row in matches]
        rhs_values = [int_value(row.get("rhs")) for row in matches]
        q_deltas = [abs(q_coeffs[index] - q_coeffs[index - 1]) for index in range(1, len(q_coeffs))]
        rhs_deltas = [abs(rhs_values[index] - rhs_values[index - 1]) for index in range(1, len(rhs_values))]
        features.update(
            {
                f"first_leaf_index_multiset={multiset_label(leaf_indices)}",
                f"first_original_trial_multiset={multiset_label(original_trials)}",
                f"first_q_coeff_mod_16_multiset={multiset_label(sorted(value % 16 for value in q_coeffs))}",
                f"first_q_delta_mod_16_multiset={multiset_label(sorted(value % 16 for value in q_deltas))}",
                f"first_rhs_delta_mod_16_multiset={multiset_label(sorted(value % 16 for value in rhs_deltas))}",
                f"first_rhs_mod_16_multiset={multiset_label(sorted(value % 16 for value in rhs_values))}",
                f"first_row_salt_mod_16_multiset={multiset_label(sorted(value % 16 for value in row_salts))}",
                f"first_scheduled_trial_multiset={multiset_label(scheduled_trials)}",
                f"first_transfer_offset_exact={transfer_offset}",
            }
        )
    return features


def split_rows(rows: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [row for row in rows if int_value(row.get("window_start")) <= calibration_end],
        [row for row in rows if int_value(row.get("window_start")) > calibration_end],
    )


def is_positive(row: dict[str, Any], label_name: str) -> bool:
    if label_name == "rank_gain_stop":
        return bool(row.get("has_rank_gain_stop"))
    if label_name == "accepted_stop":
        return bool(row.get("has_accepted_stop"))
    raise ValueError(f"unknown label {label_name!r}")


def evaluate_rule(rule: str, rows: list[dict[str, Any]], label_name: str) -> dict[str, Any]:
    selected = [row for row in rows if rule in row["features"]]
    positives = [row for row in selected if is_positive(row, label_name)]
    rejected_positives = [row for row in rows if rule not in row["features"] and is_positive(row, label_name)]
    first_case_gate_cost = sum(float_value(row.get("first_case_cost_over_rho")) for row in rows)
    continuation_cost = sum(float_value(row.get("continuation_cost_over_rho")) for row in selected)
    total_cost = first_case_gate_cost + continuation_cost
    return {
        "continuation_cost_over_rho": round(continuation_cost, 8),
        "cost_per_positive_over_rho": round(total_cost / len(positives), 8) if positives else None,
        "first_case_gate_cost_over_rho": round(first_case_gate_cost, 8),
        "positive_count": len(positives),
        "precision": round(len(positives) / len(selected), 8) if selected else None,
        "recall": round(len(positives) / (len(positives) + len(rejected_positives)), 8)
        if positives or rejected_positives
        else None,
        "rejected_positive_count": len(rejected_positives),
        "selected_count": len(selected),
        "selected_groups": [row["group"] for row in selected],
        "total_cost_over_rho": round(total_cost, 8),
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


def validation_hit_rules(rules: list[dict[str, Any]], limit: int = 20) -> list[dict[str, Any]]:
    hits = [rule for rule in rules if int_value((rule.get("validation") or {}).get("positive_count")) > 0]
    hits.sort(
        key=lambda item: (
            float((item.get("validation") or {}).get("cost_per_positive_over_rho") or 999999.0),
            -float((item.get("validation") or {}).get("precision") or 0.0),
            int_value(item.get("feature_count")),
            -float((item.get("calibration") or {}).get("precision") or 0.0),
            str(item.get("rule")),
        )
    )
    return hits[:limit]


def claim_status(rules: list[dict[str, Any]]) -> str:
    if not rules:
        return "SCOUT_POS7_FIRST_CASE_PREFORM_GATE_NO_VIABLE_CALIBRATION_RULE"
    hits = validation_hit_rules(rules, limit=1)
    if not hits:
        return "SCOUT_POS7_FIRST_CASE_PREFORM_GATE_RULES_MISS_VALIDATION"
    cost = (hits[0].get("validation") or {}).get("cost_per_positive_over_rho")
    if cost is not None and float_value(cost) < 1.0:
        return "SCOUT_POS7_FIRST_CASE_PREFORM_GATE_BELOW_RHO_DIAGNOSTIC"
    return "SCOUT_POS7_FIRST_CASE_PREFORM_GATE_VALIDATES_ABOVE_RHO"


def load_rows(
    collector: dict[str, Any],
    include_form_residue_features: bool,
    max_conjunction_size: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for group in collector.get("groups") or []:
        if not isinstance(group, dict):
            continue
        attempts = [attempt for attempt in group.get("attempts") or [] if isinstance(attempt, dict)]
        if not attempts:
            errors.append({"error": "missing_attempts", "source_path": str(group.get("source_path") or "")})
            continue
        first = attempts[0]
        first_cost = float_value(first.get("charged_ops_over_rho"), float_value(first.get("preform_ops_over_rho")))
        full_cost = float_value(group.get("charged_ops_over_rho"), first_cost)
        continuation_cost = max(0.0, full_cost - first_cost)
        transfer_index = int_value(first.get("transfer_index"))
        features = feature_conjunctions(
            first_attempt_features(group, first, include_form_residue_features),
            max_conjunction_size,
        )
        rows.append(
            {
                "features": features,
                "first_case_cost_over_rho": first_cost,
                "continuation_cost_over_rho": continuation_cost,
                "full_group_cost_over_rho": full_cost,
                "group": {
                    "attempt_count": len(attempts),
                    "first_case_cost_over_rho": round(first_cost, 8),
                    "first_point_match_scout_pos_multiset": first.get("point_match_scout_pos_multiset"),
                    "first_point_match_terms_multiset": first.get("point_match_terms_multiset"),
                    "first_pos7_11111515_point_match_count": first.get("pos7_11111515_point_match_count"),
                    "full_group_cost_over_rho": round(full_cost, 8),
                    "has_accepted_stop": bool(group.get("has_accepted_stop")),
                    "has_rank_gain_stop": bool(group.get("has_rank_gain_stop")),
                    "source_path": str(group.get("source_path") or ""),
                    "stop_transfer_index": (group.get("stop") or {}).get("transfer_index")
                    if isinstance(group.get("stop"), dict)
                    else None,
                    "transfer_index": transfer_index,
                    "window": group.get("window"),
                    "window_start": int_value(group.get("window_start")),
                },
                "has_accepted_stop": bool(group.get("has_accepted_stop")),
                "has_rank_gain_stop": bool(group.get("has_rank_gain_stop")),
                "window_start": int_value(group.get("window_start")),
            }
        )
    rows.sort(key=lambda row: (int_value(row.get("window_start")), str(row["group"].get("source_path"))))
    return rows, errors


def summarize(rows: list[dict[str, Any]], label_name: str) -> dict[str, Any]:
    full_cost = sum(float_value(row.get("full_group_cost_over_rho")) for row in rows)
    first_cost = sum(float_value(row.get("first_case_cost_over_rho")) for row in rows)
    positives = sum(1 for row in rows if is_positive(row, label_name))
    return {
        "first_case_gate_all_groups_cost_over_rho": round(first_cost, 8),
        "full_preform_scan_cost_over_rho": round(full_cost, 8),
        "group_count": len(rows),
        "positive_count": positives,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", required=True)
    parser.add_argument("--calibration-end", type=int, default=3831)
    parser.add_argument("--label", choices=["rank_gain_stop", "accepted_stop"], default="rank_gain_stop")
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--include-form-residue-features", action="store_true")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collector_path = Path(args.collector)
    collector = load_json(collector_path)
    rows, errors = load_rows(
        collector,
        args.include_form_residue_features,
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
    validation_hits = validation_hit_rules(rules)
    selected = rules[0] if rules else None
    payload = {
        "artifacts": {
            "collector": str(collector_path),
        },
        "best_validation_hit_rule": validation_hits[0] if validation_hits else None,
        "claim_status": claim_status(rules),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: features are first-source-case point-match/preform-boundary metadata, not a pure source-level gate.",
            "Default features exclude q/rhs modular residues and replay-derived rank/public-key-verification diagnostics.",
            "The first-case preform cost is charged for every source group; selected groups also pay remaining full-source continuation cost.",
            "A below-rho diagnostic would be a work order for a cheaper scout-7 micro-kernel/source policy, not a deployed-curve ECDLP break.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "include_form_residue_features": args.include_form_residue_features,
            "label": args.label,
            "max_conjunction_size": args.max_conjunction_size,
            "min_calibration_hits": args.min_calibration_hits,
            "min_calibration_precision": args.min_calibration_precision,
        },
        "rows": [row["group"] for row in rows],
        "rule_count": len(rules),
        "rules": rules[:20],
        "schema": "ecdlp.low_term_total2_scout_pos7_first_case_preform_gate_scout.v1",
        "selected_rule": selected,
        "split_summary": {
            "calibration": summarize(calibration, args.label),
            "validation": summarize(validation, args.label),
        },
        "validation_hit_rule_count": sum(1 for rule in rules if int_value((rule.get("validation") or {}).get("positive_count")) > 0),
        "validation_hit_rules": validation_hits,
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "best_validation_hit_rule": (validation_hits[0] or {}).get("rule") if validation_hits else None,
                "claim_status": payload["claim_status"],
                "error_count": len(errors),
                "selected_rule": selected["rule"] if selected else None,
                "split_summary": payload["split_summary"],
                "validation_hit_rule_count": payload["validation_hit_rule_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
