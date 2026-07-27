#!/usr/bin/env python3
"""Scout public source-abstention gates before the scout-7 preform scan.

The scout-7 preform collector preserves the clean double ``[11,15]`` signal,
but pays nearly every no-hit public source group.  This scout asks whether
metadata already present in the public source artifacts can abstain from most
source groups before root association or candidate-point checks.

Default features are source-structural: case counts, transfer-offset buckets,
salt-gap buckets, selected-row/leaf shapes, and leaf-index shapes.  Exact
transfer/salt residues and replay-derived fields such as rank/public-key
verification are available only through diagnostic flags.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

from low_term_total2_scout_pos7_source_charged_collector import (
    artifact_window,
    float_value,
    int_value,
    load_json,
    ratio,
    source_cases,
    write_json,
)


SALT_RE = re.compile(r":salt(\d+)$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def salt_values(row_keys: Any) -> list[int]:
    salts: list[int] = []
    for row_key in row_keys or []:
        match = SALT_RE.search(str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return sorted(salts)


def bucket_features(name: str, value: int, thresholds: tuple[int, ...]) -> set[str]:
    features = {f"{name}={value}"}
    for threshold in thresholds:
        if value <= threshold:
            features.add(f"{name}<={threshold}")
        if value >= threshold:
            features.add(f"{name}>={threshold}")
    return features


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


def multiset_label(values: list[int] | tuple[int, ...]) -> str:
    return ",".join(str(value) for value in values)


def leaf_profile(row: dict[str, Any]) -> dict[str, Any]:
    row_leaf_keys = [item for item in row.get("row_leaf_keys") or [] if isinstance(item, dict)]
    leaf_counter: Counter[int] = Counter()
    row_leaf_count_shape: list[int] = []
    row_leaf_index_shapes: list[str] = []
    for item in row_leaf_keys:
        indices = sorted(int_value(index) for index in item.get("leaf_indices") or [])
        row_leaf_count_shape.append(len(indices))
        row_leaf_index_shapes.append(multiset_label(indices))
        for index in indices:
            leaf_counter[index] += 1
    return {
        "leaf_index_set": sorted(leaf_counter),
        "leaf_occurrence_count": sum(leaf_counter.values()),
        "row_leaf_count_shape": multiset_label(sorted(row_leaf_count_shape)),
        "row_leaf_index_shape": ";".join(sorted(row_leaf_index_shapes)),
        "shared_leaf_indices": sorted(index for index, count in leaf_counter.items() if count >= 2),
    }


def case_profile(row: dict[str, Any], window_start: int) -> dict[str, Any]:
    transfer = int_value(row.get("transfer_index"))
    salts = salt_values(row.get("row_keys"))
    leaf = leaf_profile(row)
    salt_gap = salts[-1] - salts[0] if len(salts) >= 2 else 0
    return {
        **leaf,
        "ops_over_rho": float_value(row.get("ops_over_rho")),
        "public_key_verified": bool(row.get("public_key_verified")),
        "rank": int_value(row.get("rank")),
        "relation_count": int_value(row.get("relation_count")),
        "row_key_count": len(row.get("row_keys") or []),
        "salt_gap": salt_gap,
        "salt_max": salts[-1] if salts else 0,
        "salt_min": salts[0] if salts else 0,
        "salt_sum": sum(salts),
        "salt_values": salts,
        "selected_leaf_count": int_value(row.get("selected_leaf_count")),
        "selected_row_count": int_value(row.get("selected_row_count")),
        "source_verified": bool(row.get("source_verified")),
        "transfer_index": transfer,
        "transfer_offset": transfer - window_start,
    }


def case_features(prefix: str, profile: dict[str, Any], include_residue: bool, include_replay_diagnostics: bool) -> set[str]:
    offset = int_value(profile.get("transfer_offset"))
    salt_gap = int_value(profile.get("salt_gap"))
    selected_leaf_count = int_value(profile.get("selected_leaf_count"))
    selected_row_count = int_value(profile.get("selected_row_count"))
    leaf_indices = [int_value(index) for index in profile.get("leaf_index_set") or []]
    shared_leaf_indices = [int_value(index) for index in profile.get("shared_leaf_indices") or []]
    features: set[str] = {
        f"{prefix}_leaf_index_count={len(leaf_indices)}",
        f"{prefix}_offset_bucket={offset_bucket(offset)}",
        f"{prefix}_row_key_count={int_value(profile.get('row_key_count'))}",
        f"{prefix}_row_leaf_count_shape={profile.get('row_leaf_count_shape')}",
        f"{prefix}_row_leaf_index_shape={profile.get('row_leaf_index_shape')}",
        f"{prefix}_salt_count={len(profile.get('salt_values') or [])}",
        f"{prefix}_salt_gap_bucket={gap_bucket(salt_gap)}",
        f"{prefix}_selected_leaf_count={selected_leaf_count}",
        f"{prefix}_selected_row_count={selected_row_count}",
        f"{prefix}_shared_leaf_count={len(shared_leaf_indices)}",
    }
    features.update(bucket_features(f"{prefix}_transfer_offset", offset, (0, 1, 2, 3, 5, 7)))
    features.update(bucket_features(f"{prefix}_salt_gap", salt_gap, (0, 1, 2, 4, 5, 8, 12)))
    features.update(bucket_features(f"{prefix}_selected_leaf_count", selected_leaf_count, (1, 2, 3, 4, 5)))
    features.update(bucket_features(f"{prefix}_selected_row_count", selected_row_count, (1, 2, 3)))
    features.update(bucket_features(f"{prefix}_leaf_index_count", len(leaf_indices), (1, 2, 3, 4, 5)))
    features.update(bucket_features(f"{prefix}_shared_leaf_count", len(shared_leaf_indices), (0, 1, 2, 3)))
    for index in leaf_indices:
        features.add(f"{prefix}_has_leaf_index={index}")
    for index in shared_leaf_indices:
        features.add(f"{prefix}_shared_leaf_index={index}")
    if include_residue:
        features.update(
            {
                f"{prefix}_salt_pair={multiset_label(profile.get('salt_values') or [])}",
                f"{prefix}_salt_min_mod_8={int_value(profile.get('salt_min')) % 8}",
                f"{prefix}_salt_max_mod_8={int_value(profile.get('salt_max')) % 8}",
                f"{prefix}_salt_sum_mod_8={int_value(profile.get('salt_sum')) % 8}",
                f"{prefix}_transfer_mod_8={int_value(profile.get('transfer_index')) % 8}",
                f"{prefix}_transfer_offset_exact={offset}",
            }
        )
    if include_replay_diagnostics:
        rank = int_value(profile.get("rank"))
        relation_count = int_value(profile.get("relation_count"))
        features.update(
            {
                f"{prefix}_public_key_verified={bool(profile.get('public_key_verified'))}",
                f"{prefix}_rank={rank}",
                f"{prefix}_relation_count={relation_count}",
                f"{prefix}_source_verified={bool(profile.get('source_verified'))}",
            }
        )
        features.update(bucket_features(f"{prefix}_rank", rank, (0, 1, 2, 3)))
        features.update(bucket_features(f"{prefix}_relation_count", relation_count, (0, 1, 2, 3)))
    return features


def group_features(
    profiles: list[dict[str, Any]],
    include_residue: bool,
    include_replay_diagnostics: bool,
    first_k: int,
) -> set[str]:
    count = len(profiles)
    transfer_offsets = [int_value(profile.get("transfer_offset")) for profile in profiles]
    salt_gaps = [int_value(profile.get("salt_gap")) for profile in profiles]
    selected_leaf_counts = [int_value(profile.get("selected_leaf_count")) for profile in profiles]
    selected_row_counts = [int_value(profile.get("selected_row_count")) for profile in profiles]
    public_verified_count = sum(1 for profile in profiles if bool(profile.get("public_key_verified")))
    relation_positive_count = sum(1 for profile in profiles if int_value(profile.get("relation_count")) > 0)
    leaf_union = sorted({int_value(index) for profile in profiles for index in profile.get("leaf_index_set") or []})
    shared_union = sorted({int_value(index) for profile in profiles for index in profile.get("shared_leaf_indices") or []})
    features: set[str] = {
        "has_source_cases=True",
        f"public_source_case_count={count}",
        f"public_source_case_count_bucket={min(count, 6)}",
        f"leaf_union_count={len(leaf_union)}",
        f"selected_leaf_count_multiset={multiset_label(sorted(selected_leaf_counts))}",
        f"selected_row_count_multiset={multiset_label(sorted(selected_row_counts))}",
        f"shared_leaf_union_count={len(shared_union)}",
    }
    features.update(bucket_features("public_source_case_count", count, (0, 1, 2, 3, 4, 5, 6)))
    features.update(bucket_features("leaf_union_count", len(leaf_union), (0, 1, 2, 3, 4, 5)))
    features.update(bucket_features("shared_leaf_union_count", len(shared_union), (0, 1, 2, 3)))
    for index in leaf_union:
        features.add(f"group_has_leaf_index={index}")
    for index in shared_union:
        features.add(f"group_shared_leaf_index={index}")
    if profiles:
        offset_min = min(transfer_offsets)
        offset_max = max(transfer_offsets)
        salt_gap_min = min(salt_gaps)
        salt_gap_max = max(salt_gaps)
        features.update(
            {
                f"first_offset_bucket={offset_bucket(transfer_offsets[0])}",
                f"first_salt_gap_bucket={gap_bucket(salt_gaps[0])}",
                f"has_salt_gap_ge_5={any(gap >= 5 for gap in salt_gaps)}",
                f"has_salt_gap_ge_8={any(gap >= 8 for gap in salt_gaps)}",
                f"max_offset_bucket={offset_bucket(offset_max)}",
                f"max_salt_gap_bucket={gap_bucket(salt_gap_max)}",
                f"min_offset_bucket={offset_bucket(offset_min)}",
                f"min_salt_gap_bucket={gap_bucket(salt_gap_min)}",
                f"offset_span_bucket={offset_bucket(offset_max - offset_min)}",
                f"salt_gap_span_bucket={gap_bucket(salt_gap_max - salt_gap_min)}",
            }
        )
        features.update(bucket_features("first_transfer_offset", transfer_offsets[0], (0, 1, 2, 3, 5, 7)))
        features.update(bucket_features("first_salt_gap", salt_gaps[0], (0, 1, 2, 4, 5, 8, 12)))
        features.update(bucket_features("max_salt_gap", salt_gap_max, (0, 1, 2, 4, 5, 8, 12)))
        features.update(bucket_features("min_salt_gap", salt_gap_min, (0, 1, 2, 4, 5, 8, 12)))
    for index, profile in enumerate(profiles[:first_k], start=1):
        features.update(case_features(f"case{index}", profile, include_residue, include_replay_diagnostics))
    if include_residue:
        features.add(f"transfer_offset_multiset={multiset_label(transfer_offsets)}")
        features.add(f"salt_gap_multiset={multiset_label(sorted(salt_gaps))}")
    if include_replay_diagnostics:
        features.update(
            {
                f"public_key_verified_case_count={public_verified_count}",
                f"relation_positive_case_count={relation_positive_count}",
            }
        )
        features.update(bucket_features("public_key_verified_case_count", public_verified_count, (0, 1, 2, 3, 4)))
        features.update(bucket_features("relation_positive_case_count", relation_positive_count, (0, 1, 2, 3, 4)))
    return features


def conjunctions(features: set[str], max_size: int) -> set[str]:
    ordered = sorted(features)
    result = set(ordered)
    for size in range(2, max_size + 1):
        for combo in combinations(ordered, size):
            result.add("|".join(combo))
    return result


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
    gate_cost = sum(float_value(row.get("gate_cost_over_rho")) for row in rows)
    scan_cost = sum(float_value(row.get("scan_cost_over_rho")) for row in selected)
    total_cost = gate_cost + scan_cost
    return {
        "cost_per_positive_over_rho": round(total_cost / len(positives), 8) if positives else None,
        "gate_cost_over_rho": round(gate_cost, 8),
        "positive_count": len(positives),
        "precision": round(len(positives) / len(selected), 8) if selected else None,
        "recall": round(len(positives) / (len(positives) + len(rejected_positives)), 8)
        if positives or rejected_positives
        else None,
        "rejected_positive_count": len(rejected_positives),
        "scan_cost_over_rho": round(scan_cost, 8),
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


def claim_status(selected: dict[str, Any] | None) -> str:
    if selected is None:
        return "SCOUT_POS7_SOURCE_ABSTENTION_NO_VIABLE_CALIBRATION_RULE"
    validation = selected.get("validation") if isinstance(selected.get("validation"), dict) else {}
    positives = int_value(validation.get("positive_count"))
    cost = validation.get("cost_per_positive_over_rho")
    if positives <= 0:
        return "SCOUT_POS7_SOURCE_ABSTENTION_RULE_MISSES_VALIDATION"
    if cost is not None and float_value(cost) < 1.0:
        return "SCOUT_POS7_SOURCE_ABSTENTION_BELOW_RHO_DIAGNOSTIC"
    return "SCOUT_POS7_SOURCE_ABSTENTION_VALIDATES_ABOVE_RHO"


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


def load_rows(
    collector: dict[str, Any],
    include_residue_features: bool,
    include_replay_diagnostics: bool,
    max_conjunction_size: int,
    first_k_cases: int,
    gate_cost_over_rho_per_source_case: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    artifacts = collector.get("artifacts") if isinstance(collector.get("artifacts"), dict) else {}
    source_paths = [Path(str(path)) for path in artifacts.get("source_paths") or []]
    groups_by_source = {
        str(group.get("source_path")): group
        for group in collector.get("groups") or []
        if isinstance(group, dict) and group.get("source_path")
    }
    parameters = collector.get("parameters") if isinstance(collector.get("parameters"), dict) else {}
    target = str(parameters.get("target") or "22050.cf1@11731")
    selector = str(parameters.get("selector") or "mode_low_term_support_total5")
    top_k = int_value(parameters.get("top_k"), 16)
    min_transfer = int_value(parameters.get("min_transfer"), 3560)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for source_path in source_paths:
        group = groups_by_source.get(str(source_path))
        if group is None:
            continue
        source = load_json(source_path)
        window = artifact_window(source_path)
        window_start = int_value(group.get("window_start"), window[0] if window else 0)
        try:
            source_rows = source_cases(source_path, source, target, selector, top_k, min_transfer)
            profiles = [case_profile(row, window_start) for row in source_rows]
            features = conjunctions(
                group_features(
                    profiles,
                    include_residue_features,
                    include_replay_diagnostics,
                    first_k_cases,
                ),
                max_conjunction_size,
            )
            gate_cost = len(profiles) * gate_cost_over_rho_per_source_case
            rows.append(
                {
                    "features": features,
                    "gate_cost_over_rho": gate_cost,
                    "group": {
                        "charged_ops_over_rho": group.get("charged_ops_over_rho"),
                        "gate_cost_over_rho": round(gate_cost, 8),
                        "has_accepted_stop": bool(group.get("has_accepted_stop")),
                        "has_rank_gain_stop": bool(group.get("has_rank_gain_stop")),
                        "source_case_count": len(profiles),
                        "source_path": str(source_path),
                        "stop_transfer_index": (group.get("stop") or {}).get("transfer_index")
                        if isinstance(group.get("stop"), dict)
                        else None,
                        "window": group.get("window"),
                        "window_start": window_start,
                    },
                    "has_accepted_stop": bool(group.get("has_accepted_stop")),
                    "has_rank_gain_stop": bool(group.get("has_rank_gain_stop")),
                    "scan_cost_over_rho": float_value(group.get("charged_ops_over_rho")),
                    "source_case_count": len(profiles),
                    "window_start": window_start,
                }
            )
        except Exception as exc:  # noqa: BLE001 - preserve research replay failures.
            errors.append({"error": "source_profile_failed", "message": str(exc), "source_path": str(source_path)})
    rows.sort(key=lambda row: (int_value(row.get("window_start")), str(row["group"].get("source_path"))))
    return rows, errors


def summarize(rows: list[dict[str, Any]], label_name: str) -> dict[str, Any]:
    scan_cost = sum(float_value(row.get("scan_cost_over_rho")) for row in rows)
    gate_cost = sum(float_value(row.get("gate_cost_over_rho")) for row in rows)
    positives = sum(1 for row in rows if is_positive(row, label_name))
    return {
        "full_preform_scan_cost_over_rho": round(scan_cost + gate_cost, 8),
        "gate_cost_over_rho": round(gate_cost, 8),
        "group_count": len(rows),
        "positive_count": positives,
        "source_case_count": sum(int_value(row.get("source_case_count")) for row in rows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", required=True)
    parser.add_argument("--calibration-end", type=int, default=3831)
    parser.add_argument("--label", choices=["rank_gain_stop", "accepted_stop"], default="rank_gain_stop")
    parser.add_argument("--max-conjunction-size", type=int, default=2)
    parser.add_argument("--min-calibration-hits", type=int, default=2)
    parser.add_argument("--min-calibration-precision", type=float, default=0.5)
    parser.add_argument("--first-k-cases", type=int, default=3)
    parser.add_argument("--gate-cost-over-rho-per-source-case", type=float, default=0.0)
    parser.add_argument("--include-residue-features", action="store_true")
    parser.add_argument("--include-replay-diagnostics", action="store_true")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collector_path = Path(args.collector)
    collector = load_json(collector_path)
    rows, errors = load_rows(
        collector,
        args.include_residue_features,
        args.include_replay_diagnostics,
        args.max_conjunction_size,
        args.first_k_cases,
        args.gate_cost_over_rho_per_source_case,
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
    validation_hits = validation_hit_rules(rules)
    payload = {
        "artifacts": {
            "collector": str(collector_path),
        },
        "claim_status": claim_status(selected),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: default gate features are public source-case metadata before root association and candidate-point checks.",
            "Default features exclude exact transfer/salt residues and replay-derived rank/public-key-verification diagnostics.",
            "Gate feature computation is charged only by the configured source-case proxy; default charge is zero because the source artifacts already exist.",
            "A below-rho diagnostic is a work order for a fresh source-generation policy, not a deployed-curve ECDLP break.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "first_k_cases": args.first_k_cases,
            "gate_cost_over_rho_per_source_case": args.gate_cost_over_rho_per_source_case,
            "include_replay_diagnostics": args.include_replay_diagnostics,
            "include_residue_features": args.include_residue_features,
            "label": args.label,
            "max_conjunction_size": args.max_conjunction_size,
            "min_calibration_hits": args.min_calibration_hits,
            "min_calibration_precision": args.min_calibration_precision,
        },
        "rows": [row["group"] for row in rows],
        "rule_count": len(rules),
        "rules": rules[:20],
        "schema": "ecdlp.low_term_total2_scout_pos7_source_abstention_gate_scout.v1",
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
