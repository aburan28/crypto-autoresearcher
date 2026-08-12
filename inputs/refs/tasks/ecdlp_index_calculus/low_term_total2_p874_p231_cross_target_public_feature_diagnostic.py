#!/usr/bin/env python3
"""P874 public-feature diagnostic for the P872/P873 cross-target split."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p869_p231_public_motif_predictor as p869
import low_term_total2_p870_p231_public_rule_materialization as p870
import low_term_total2_p872_p231_two_stage_materialization as p872
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p874_p231_cross_target_public_feature_diagnostic.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p874_p231_cross_target_public_feature_diagnostic_probe.json"
DEFAULT_TARGETS = ("22050.cf1@11731", "67.a1@9803")
SCHEMA = "ecdlp.low_term_total2_p874_p231_cross_target_public_feature_diagnostic.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def rounded(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 8)


def feature_flags(features: dict[str, Any]) -> dict[str, bool]:
    salt_gap = features.get("salt_gap")
    top_k_le_12 = int_value(features.get("top_k")) <= 12
    all_has_double_pair = bool(features.get("all_has_double_pair"))
    count_double_pair_ge_7 = int_value(features.get("count_double_pair")) >= 7
    salt_gap_le_8 = salt_gap is not None and int_value(salt_gap) <= 8
    first_stage = p870.frozen_rule(features)
    second_stage_predicate = p872.second_stage_rule(features)
    return {
        "all_has_double_pair": all_has_double_pair,
        "count_double_pair_ge_7": count_double_pair_ge_7,
        "first_stage": first_stage,
        "salt_gap_le_8": salt_gap_le_8,
        "second_stage": first_stage and second_stage_predicate,
        "second_stage_predicate": second_stage_predicate,
        "top_k_le_12": top_k_le_12,
    }


def compact_row(case: dict[str, Any], features: dict[str, Any], flags: dict[str, bool]) -> dict[str, Any]:
    return {
        "all_has_double_pair": flags["all_has_double_pair"],
        "case_id": features.get("case_id"),
        "count_double_pair": int_value(features.get("count_double_pair")),
        "count_shape_2p2": int_value(features.get("count_shape_2p2")),
        "first_stage": flags["first_stage"],
        "leaf_gap_tuple": list(features.get("leaf_gap_tuple") or []),
        "leaf_selector": features.get("leaf_selector"),
        "leaf_selector_family": features.get("leaf_selector_family"),
        "missing_selected_feature_count": int_value(features.get("missing_selected_feature_count")),
        "salt_gap": features.get("salt_gap"),
        "second_stage": flags["second_stage"],
        "second_stage_predicate": flags["second_stage_predicate"],
        "selected_feature_count": int_value(features.get("selected_feature_count")),
        "selected_leaf_occurrence_count": int_value(features.get("selected_leaf_occurrence_count")),
        "target": case.get("target"),
        "top_k": int_value(features.get("top_k")),
        "top_k_le_12": flags["top_k_le_12"],
        "transfer_index": int_value(case.get("transfer_index")),
        "unique_leaf_count": int_value(features.get("unique_leaf_count")),
        "unique_leaf_indices": list(features.get("unique_leaf_indices") or []),
        "window": case.get("window"),
    }


def percentile(sorted_values: list[float], fraction: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return rounded(sorted_values[0])
    pos = (len(sorted_values) - 1) * fraction
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return rounded(sorted_values[lo])
    lower = sorted_values[lo] * (hi - pos)
    upper = sorted_values[hi] * (pos - lo)
    return rounded(lower + upper)


def numeric_distribution(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    values = [row.get(field) for row in rows if row.get(field) is not None]
    numeric = sorted(float(value) for value in values)
    counts = Counter(int(value) if float(value).is_integer() else value for value in numeric)
    return {
        "count": len(numeric),
        "max": rounded(max(numeric)) if numeric else None,
        "mean": rounded(sum(numeric) / len(numeric)) if numeric else None,
        "median": percentile(numeric, 0.5),
        "min": rounded(min(numeric)) if numeric else None,
        "null_count": len(rows) - len(numeric),
        "p10": percentile(numeric, 0.1),
        "p90": percentile(numeric, 0.9),
        "value_counts": {str(key): counts[key] for key in sorted(counts, key=lambda item: (float(item), str(item)))},
    }


def window_breakdown(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_window: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_window[str(row.get("window"))].append(row)
    return {window: summarize_counts(window_rows) for window, window_rows in sorted(by_window.items())}


def summarize_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    top = sum(1 for row in rows if row["top_k_le_12"])
    all_double = sum(1 for row in rows if row["all_has_double_pair"])
    first = sum(1 for row in rows if row["first_stage"])
    count_ge7 = sum(1 for row in rows if int_value(row.get("count_double_pair")) >= 7)
    salt_gap_le8 = sum(1 for row in rows if row.get("salt_gap") is not None and int_value(row.get("salt_gap")) <= 8)
    second_predicate = sum(1 for row in rows if row["second_stage_predicate"])
    second = sum(1 for row in rows if row["second_stage"])
    top_only_blocked_by_double = sum(1 for row in rows if row["top_k_le_12"] and not row["all_has_double_pair"])
    double_only_blocked_by_top = sum(1 for row in rows if row["all_has_double_pair"] and not row["top_k_le_12"])
    neither_first_conjunct = sum(1 for row in rows if not row["top_k_le_12"] and not row["all_has_double_pair"])
    return {
        "all_has_double_pair_count": all_double,
        "all_has_double_pair_rate": safe_ratio(all_double, total),
        "count_double_pair_ge_7_count": count_ge7,
        "count_double_pair_ge_7_rate": safe_ratio(count_ge7, total),
        "double_only_blocked_by_top_count": double_only_blocked_by_top,
        "first_stage_count": first,
        "first_stage_rate": safe_ratio(first, total),
        "neither_first_conjunct_count": neither_first_conjunct,
        "salt_gap_le_8_count": salt_gap_le8,
        "salt_gap_le_8_rate": safe_ratio(salt_gap_le8, total),
        "second_stage_count": second,
        "second_stage_predicate_count": second_predicate,
        "second_stage_predicate_rate": safe_ratio(second_predicate, total),
        "second_stage_rate": safe_ratio(second, total),
        "source_case_count": total,
        "top_k_le_12_and_all_has_double_pair_count": first,
        "top_k_le_12_count": top,
        "top_k_le_12_rate": safe_ratio(top, total),
        "top_only_blocked_by_double_count": top_only_blocked_by_double,
    }


Rule = tuple[str, Callable[[dict[str, Any]], bool]]


def rule_variants() -> list[Rule]:
    return [
        ("top_k <= 12", lambda row: bool(row["top_k_le_12"])),
        ("all_has_double_pair", lambda row: bool(row["all_has_double_pair"])),
        ("count_double_pair >= 1", lambda row: int_value(row.get("count_double_pair")) >= 1),
        ("count_double_pair >= 2", lambda row: int_value(row.get("count_double_pair")) >= 2),
        ("count_double_pair >= 4", lambda row: int_value(row.get("count_double_pair")) >= 4),
        ("count_double_pair >= 7", lambda row: int_value(row.get("count_double_pair")) >= 7),
        (
            "top_k <= 12 AND count_double_pair >= 1",
            lambda row: bool(row["top_k_le_12"]) and int_value(row.get("count_double_pair")) >= 1,
        ),
        (
            "top_k <= 12 AND count_double_pair >= 2",
            lambda row: bool(row["top_k_le_12"]) and int_value(row.get("count_double_pair")) >= 2,
        ),
        (
            "top_k <= 12 AND count_double_pair >= 4",
            lambda row: bool(row["top_k_le_12"]) and int_value(row.get("count_double_pair")) >= 4,
        ),
        (
            "top_k <= 12 AND count_double_pair >= 7",
            lambda row: bool(row["top_k_le_12"]) and int_value(row.get("count_double_pair")) >= 7,
        ),
        (
            "count_double_pair >= 7 AND salt_gap <= 8",
            lambda row: int_value(row.get("count_double_pair")) >= 7
            and row.get("salt_gap") is not None
            and int_value(row.get("salt_gap")) <= 8,
        ),
        (
            "top_k <= 12 AND count_double_pair >= 7 AND salt_gap <= 8",
            lambda row: bool(row["top_k_le_12"])
            and int_value(row.get("count_double_pair")) >= 7
            and row.get("salt_gap") is not None
            and int_value(row.get("salt_gap")) <= 8,
        ),
        (
            "top_k <= 12 AND count_double_pair == selected_leaf_occurrence_count",
            lambda row: bool(row["top_k_le_12"])
            and int_value(row.get("selected_leaf_occurrence_count")) > 0
            and int_value(row.get("count_double_pair")) == int_value(row.get("selected_leaf_occurrence_count")),
        ),
    ]


def evaluate_rule_variants(rows_by_target: dict[str, list[dict[str, Any]]], targets: list[str]) -> list[dict[str, Any]]:
    results = []
    for name, fn in rule_variants():
        counts = {}
        rates = {}
        for target in targets:
            rows = rows_by_target.get(target, [])
            count = sum(1 for row in rows if fn(row))
            counts[target] = count
            rates[target] = safe_ratio(count, len(rows))
        results.append({"counts": counts, "name": name, "rates": rates})
    return results


def nearest_relaxations(variant_results: list[dict[str, Any]], disjoint_target: str) -> list[dict[str, Any]]:
    selecting = [row for row in variant_results if int_value(row["counts"].get(disjoint_target)) > 0]
    return sorted(
        selecting,
        key=lambda row: (
            int_value(row["counts"].get(disjoint_target)),
            -sum(int_value(value) for target, value in row["counts"].items() if target != disjoint_target),
            row["name"],
        ),
    )[:6]


def near_miss_rows(rows: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    ranked = sorted(
        rows,
        key=lambda row: (
            not bool(row.get("top_k_le_12")),
            -int_value(row.get("count_double_pair")),
            int_value(row.get("salt_gap"), 10**9) if row.get("salt_gap") is not None else 10**9,
            int_value(row.get("top_k")),
            str(row.get("case_id")),
        ),
    )
    return ranked[:limit]


def build_public_rows(windows: list[str], targets: list[str]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    target_set = set(targets)
    source_paths = {window: p868.source_path(window) for window in windows}
    rows: list[dict[str, Any]] = []
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    build_cache: dict[
        str,
        tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace],
    ] = {}
    for window in windows:
        source = p868.load_json(source_paths[window])
        params = repair_probe.source_parameters(source)
        probe_args = repair_probe.probe_args_from_source(source)
        cache_key = p868.json_key(
            {
                "bank_source": params.get("bank_source"),
                "config_source": params.get("config_source"),
                "direct_source": params.get("direct_source"),
                "radius": params.get("radius"),
                "transfer_source": params.get("transfer_source"),
            }
        )
        if cache_key not in build_cache:
            build_cache[cache_key] = (*repair_probe.build_specs(params), probe_args)
        verifier, records, config_source, specs_by_target, probe_args = build_cache[cache_key]
        for case in p868.iter_source_cases(source, window, target_set):
            context = hit_stream_probe.scan_case_context(
                verifier,
                records,
                config_source,
                specs_by_target,
                case,
                probe_args,
                context_cache,
            )
            features = p869.public_features(case, context)
            selected_feature_count = len(p869.selected_public_features(case, context))
            features["selected_feature_count"] = selected_feature_count
            features["missing_selected_feature_count"] = max(
                0,
                int_value(features.get("selected_leaf_occurrence_count")) - selected_feature_count,
            )
            rows.append(compact_row(case, features, feature_flags(features)))
    return rows, {window: str(path) for window, path in source_paths.items()}


def load_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return p868.load_json(path).get("summary") or {}


def control_check(
    target_stats: dict[str, dict[str, Any]],
    calibration_target: str,
    disjoint_target: str,
) -> dict[str, Any]:
    p872_summary = load_summary(STATE_DIR / "low_term_total2_p872_p231_two_stage_materialization_probe.json")
    p873_summary = load_summary(STATE_DIR / "low_term_total2_p873_p231_disjoint_target_two_stage_materialization_probe.json")
    observed_calibration = target_stats.get(calibration_target, {})
    observed_disjoint = target_stats.get(disjoint_target, {})
    checks = {
        "p872_first_stage_match": observed_calibration.get("first_stage_count")
        == p872_summary.get("first_stage_selected_case_count"),
        "p872_second_stage_match": observed_calibration.get("second_stage_count")
        == p872_summary.get("second_stage_selected_case_count"),
        "p872_source_count_match": observed_calibration.get("source_case_count") == p872_summary.get("source_case_count"),
        "p873_first_stage_match": observed_disjoint.get("first_stage_count")
        == p873_summary.get("first_stage_selected_case_count"),
        "p873_second_stage_match": observed_disjoint.get("second_stage_count")
        == p873_summary.get("second_stage_selected_case_count"),
        "p873_source_count_match": observed_disjoint.get("source_case_count") == p873_summary.get("source_case_count"),
    }
    return {
        "all_controls_pass": all(checks.values()),
        "checks": checks,
        "expected": {
            calibration_target: {
                "first_stage_count": p872_summary.get("first_stage_selected_case_count"),
                "second_stage_count": p872_summary.get("second_stage_selected_case_count"),
                "source_case_count": p872_summary.get("source_case_count"),
            },
            disjoint_target: {
                "first_stage_count": p873_summary.get("first_stage_selected_case_count"),
                "second_stage_count": p873_summary.get("second_stage_selected_case_count"),
                "source_case_count": p873_summary.get("source_case_count"),
            },
        },
        "observed": {
            calibration_target: {
                "first_stage_count": observed_calibration.get("first_stage_count"),
                "second_stage_count": observed_calibration.get("second_stage_count"),
                "source_case_count": observed_calibration.get("source_case_count"),
            },
            disjoint_target: {
                "first_stage_count": observed_disjoint.get("first_stage_count"),
                "second_stage_count": observed_disjoint.get("second_stage_count"),
                "source_case_count": observed_disjoint.get("source_case_count"),
            },
        },
    }


def determine_claim(disjoint_stats: dict[str, Any]) -> str:
    if int_value(disjoint_stats.get("first_stage_count")) > 0:
        if int_value(disjoint_stats.get("second_stage_count")) > 0:
            return "OBSERVATION_P874_DISJOINT_TARGET_HAS_PUBLIC_TWO_STAGE_CANDIDATES"
        return "NEGATIVE_RESULT_P874_DISJOINT_TARGET_SECOND_STAGE_BLOCKS_AFTER_FIRST_STAGE"
    if int_value(disjoint_stats.get("top_k_le_12_count")) == 0:
        return "NEGATIVE_RESULT_P874_DISJOINT_TARGET_BLOCKED_BY_TOP_K"
    if int_value(disjoint_stats.get("all_has_double_pair_count")) == 0:
        return "NEGATIVE_RESULT_P874_DISJOINT_TARGET_BLOCKED_BY_ALL_HAS_DOUBLE_PAIR_ABSENCE"
    return "NEGATIVE_RESULT_P874_DISJOINT_TARGET_BLOCKED_BY_FIRST_STAGE_CONJUNCT_INTERACTION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = list(args.windows)
    targets = [target.strip() for target in args.targets.split(",") if target.strip()]
    rows, source_windows = build_public_rows(windows, targets)
    rows_by_target: dict[str, list[dict[str, Any]]] = {target: [] for target in targets}
    for row in rows:
        rows_by_target.setdefault(str(row.get("target")), []).append(row)

    target_stats: dict[str, dict[str, Any]] = {}
    for target in targets:
        target_rows = rows_by_target.get(target, [])
        stats = summarize_counts(target_rows)
        stats["metric_distributions"] = {
            field: numeric_distribution(target_rows, field)
            for field in (
                "count_double_pair",
                "count_shape_2p2",
                "missing_selected_feature_count",
                "salt_gap",
                "selected_feature_count",
                "selected_leaf_occurrence_count",
                "top_k",
                "unique_leaf_count",
            )
        }
        stats["window_breakdown"] = window_breakdown(target_rows)
        target_stats[target] = stats

    calibration_target = targets[0]
    disjoint_target = targets[1] if len(targets) > 1 else targets[0]
    variant_results = evaluate_rule_variants(rows_by_target, targets)
    claim = determine_claim(target_stats.get(disjoint_target, {}))
    controls = control_check(target_stats, calibration_target, disjoint_target)
    disjoint_near_misses = near_miss_rows(rows_by_target.get(disjoint_target, []))
    calibration_selected_examples = near_miss_rows(
        [row for row in rows_by_target.get(calibration_target, []) if row.get("first_stage")],
        limit=12,
    )
    nearest = nearest_relaxations(variant_results, disjoint_target)
    next_selector = nearest[0]["name"] if nearest else None

    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
            "source_windows": source_windows,
        },
        "blocker_summary": {
            "calibration_target": calibration_target,
            "disjoint_target": disjoint_target,
            "disjoint_blocking_claim": claim,
            "disjoint_first_stage_blockers": {
                "all_has_double_pair_count": target_stats.get(disjoint_target, {}).get("all_has_double_pair_count"),
                "neither_first_conjunct_count": target_stats.get(disjoint_target, {}).get(
                    "neither_first_conjunct_count"
                ),
                "top_k_le_12_count": target_stats.get(disjoint_target, {}).get("top_k_le_12_count"),
                "top_only_blocked_by_double_count": target_stats.get(disjoint_target, {}).get(
                    "top_only_blocked_by_double_count"
                ),
            },
            "next_public_selector_hypothesis": next_selector,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("OBSERVATION") else "NEGATIVE RESULT",
        "control_check": controls,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "PUBLIC-FEATURE BOUNDARY: P874 computes selector features only and does not reconstruct relation events.",
            "DIAGNOSTIC BOUNDARY: proposed relaxations require later label-revealing materialization.",
            "CROSS-TARGET BOUNDARY: comparison is inside one p231 fixed-row artifact family.",
            "POLLARD-RHO BOUNDARY: this is selector-obstruction evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p874_p231_cross_target_public_feature_diagnostic",
        "parameters": {
            "first_stage_rule": p872.FIRST_STAGE_RULE,
            "second_stage_rule": p872.SECOND_STAGE_RULE,
            "targets": targets,
            "windows": windows,
        },
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
            "assumptions": [
                "P874 public feature extraction matches the P872/P873 extraction path.",
                "No relation-event labels or verifier outcomes are used to identify the failed conjunct.",
                "A relaxed public selector is only a next hypothesis until a materialization run reveals labels.",
            ],
            "claim_or_task": "Identify the public-feature obstruction that made P873 select zero disjoint-target cases.",
            "evidence_so_far": [
                f"Control pass: {controls['all_controls_pass']}.",
                f"Disjoint first-stage count: {target_stats.get(disjoint_target, {}).get('first_stage_count')}.",
                f"Disjoint top-k-pass but double-pair-blocked count: {target_stats.get(disjoint_target, {}).get('top_only_blocked_by_double_count')}.",
            ],
            "failure_modes": [
                "The feature shift may be window-specific rather than target-specific.",
                "Relaxing all_has_double_pair may select false positives once relation labels are revealed.",
                "Same-p231-family diagnostics may not transfer to larger prime-field targets.",
            ],
            "next_concrete_action": (
                "Build P875 to materialize the best public relaxation on 67.a1@9803, then reveal labels only after selection."
            ),
            "status": "OBSERVATION" if claim.startswith("OBSERVATION") else "NEGATIVE RESULT",
        },
        "rule_variant_counts": variant_results,
        "schema": SCHEMA,
        "target_stats": target_stats,
        "target_comparison_examples": {
            "calibration_first_stage_examples": calibration_selected_examples,
            "disjoint_near_misses": disjoint_near_misses,
        },
        "top_relaxations_selecting_disjoint": nearest,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--windows", nargs="+", default=list(p872.DEFAULT_WINDOWS))
    parser.add_argument("--targets", default=",".join(DEFAULT_TARGETS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(json.dumps({"blocker_summary": payload["blocker_summary"], "control_check": payload["control_check"]}, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
