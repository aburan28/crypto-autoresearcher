#!/usr/bin/env python3
"""P731 public regime-shift override for P730 selector instability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p730_public_window_regime_selector as p730


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p731_public_regime_shift_override_probe.json"
DEFAULT_P709 = p730.DEFAULT_P709
P730_REFERENCE = STATE_DIR / "low_term_total2_p730_public_window_regime_selector_probe.json"
FOCUS_SPLIT = p730.FOCUS_SPLIT
ADJACENT_VALIDATION_SPLIT = "rolling_train24_holdout16_start27"
FIXED_RULE = f"always_{p730.FIXED}"
TOPK7_RULE = f"always_{p730.TOPK7_1P0}"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    return p730.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p730.float_value(value, default)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def round8(value: float) -> float:
    return round(value, 8)


def split_slice(split: dict[str, Any], reports: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    start = int_value(split[f"{key}_start_index"])
    end = int_value(split[f"{key}_end_index"])
    return reports[start:end]


def feature_for_report(
    report: dict[str, Any],
    features_by_window: dict[tuple[int, int], p730.WindowFeatures],
) -> p730.WindowFeatures:
    key = (int_value(report.get("window_start")), int_value(report.get("window_end")))
    return features_by_window[key]


def summarize_feature_block(
    reports: list[dict[str, Any]],
    features_by_window: dict[tuple[int, int], p730.WindowFeatures],
) -> dict[str, Any]:
    features = [feature_for_report(report, features_by_window) for report in reports]
    topk7 = [float(feature.topk7_count) for feature in features]
    topk7_fresh = [float(feature.topk7_fresh_count) for feature in features]
    shape = [float(feature.shape_count) for feature in features]
    fixed = [float(feature.fixed_count) for feature in features]
    all_counts = [float(max(feature.all_count, 1)) for feature in features]
    topk7_minus_shape = [float(feature.topk7_count - feature.shape_count) for feature in features]
    return {
        "all_count_mean": round8(mean([float(feature.all_count) for feature in features])),
        "fixed_count_mean": round8(mean(fixed)),
        "fresh_count_mean": round8(mean([float(feature.fresh_count) for feature in features])),
        "shape_count_mean": round8(mean(shape)),
        "topk7_count_mean": round8(mean(topk7)),
        "topk7_fresh_count_mean": round8(mean(topk7_fresh)),
        "topk7_minus_shape_mean": round8(mean(topk7_minus_shape)),
        "topk7_over_all_mean": round8(mean([t / a for t, a in zip(topk7, all_counts)])),
        "topk7_over_fixed_mean": round8(mean([t / max(f, 1.0) for t, f in zip(topk7, fixed)])),
        "window_count": len(features),
    }


def delta_summary(train: dict[str, Any], holdout: dict[str, Any]) -> dict[str, Any]:
    keys = sorted(key for key, value in train.items() if key.endswith("_mean") and isinstance(value, (int, float)))
    return {key: round8(float_value(holdout.get(key)) - float_value(train.get(key))) for key in keys}


def uses_topk(rule_name: str) -> bool:
    return "topk" in rule_name


def detector_choice(selected_rule_name: str, train: dict[str, Any], holdout: dict[str, Any]) -> dict[str, Any]:
    delta = delta_summary(train, holdout)
    topk_margin_delta = float_value(delta.get("topk7_minus_shape_mean"))
    holdout_topk_margin = float_value(holdout.get("topk7_minus_shape_mean"))
    holdout_topk_fresh = float_value(holdout.get("topk7_fresh_count_mean"))
    topk_delta = float_value(delta.get("topk7_count_mean"))
    topk_fresh_delta = float_value(delta.get("topk7_fresh_count_mean"))
    if topk_margin_delta >= 5.0 and holdout_topk_margin >= 4.0 and holdout_topk_fresh >= 8.0:
        return {
            "chosen_rule_name": TOPK7_RULE,
            "reason": "positive_topk_margin_shift",
            "triggered": True,
        }
    if uses_topk(selected_rule_name) and topk_delta <= -5.0 and topk_fresh_delta <= -5.0:
        return {
            "chosen_rule_name": FIXED_RULE,
            "reason": "negative_topk_fresh_shift",
            "triggered": True,
        }
    return {
        "chosen_rule_name": selected_rule_name,
        "reason": "no_public_shift_override",
        "triggered": False,
    }


def rule_by_name(rules: list[p730.RegimeRule], name: str) -> p730.RegimeRule:
    for rule in rules:
        if rule.name == name:
            return rule
    raise KeyError(name)


def split_window_ranges(reports: list[dict[str, Any]]) -> dict[str, Any]:
    return p730.split_window_ranges(reports)


def compact(report: dict[str, Any] | None) -> dict[str, Any] | None:
    return p730.compact(report)


def evaluate_split_with_detector(
    split: dict[str, Any],
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    gates: dict[str, p730.p729.PublicGate],
    features_by_window: dict[tuple[int, int], p730.WindowFeatures],
    rules: list[p730.RegimeRule],
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    train_reports = split_slice(split, reports, "train")
    holdout_reports = split_slice(split, reports, "holdout")
    train_rule_scores = [
        p730.evaluate_rule(train_reports, metadata, gates, features_by_window, rule, factor_charge, sample_limit)
        for rule in rules
    ]
    selected_train_score = p730.choose_best(train_rule_scores)
    selected_rule_name = str(selected_train_score.get("rule_name"))
    train_features = summarize_feature_block(train_reports, features_by_window)
    holdout_features = summarize_feature_block(holdout_reports, features_by_window)
    feature_delta = delta_summary(train_features, holdout_features)
    decision = detector_choice(selected_rule_name, train_features, holdout_features)
    detector_rule = rule_by_name(rules, decision["chosen_rule_name"])
    fixed_rule = rule_by_name(rules, FIXED_RULE)
    topk_rule = rule_by_name(rules, TOPK7_RULE)
    selected_rule = rule_by_name(rules, selected_rule_name)
    holdout_rule_scores = [
        p730.evaluate_rule(holdout_reports, metadata, gates, features_by_window, rule, factor_charge, sample_limit)
        for rule in rules
    ]
    fixed_eval = p730.evaluate_rule(
        holdout_reports, metadata, gates, features_by_window, fixed_rule, factor_charge, sample_limit
    )
    selected_eval = p730.evaluate_rule(
        holdout_reports, metadata, gates, features_by_window, selected_rule, factor_charge, sample_limit
    )
    detector_eval = p730.evaluate_rule(
        holdout_reports, metadata, gates, features_by_window, detector_rule, factor_charge, sample_limit
    )
    topk_eval = p730.evaluate_rule(
        holdout_reports, metadata, gates, features_by_window, topk_rule, factor_charge, sample_limit
    )
    return {
        **split,
        "best_heldout_rule_new_bank": p730.choose_best(holdout_rule_scores),
        "detector": {
            **decision,
            "feature_delta": feature_delta,
            "holdout_features": holdout_features,
            "train_features": train_features,
        },
        "detector_holdout_new_bank": detector_eval,
        "fixed_reference_new_bank": fixed_eval,
        "selected_holdout_new_bank": selected_eval,
        "selected_rule_name": selected_rule_name,
        "top_train_rules": sorted(train_rule_scores, key=p730.eval_sort_key)[:8],
        "topk7_oracle_reference_new_bank": topk_eval,
        "window_ranges": {
            "holdout": split_window_ranges(holdout_reports),
            "train": split_window_ranges(train_reports),
        },
    }


def total(report: dict[str, Any] | None) -> float | None:
    return p730.total(report)


def below_count(split_payloads: list[dict[str, Any]], key: str) -> int:
    return p730.below_count(split_payloads, key)


def focus_report(split_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    for report in split_payloads:
        if report.get("split") == FOCUS_SPLIT:
            return report
    return {}


def adjacent_report(split_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    for report in split_payloads:
        if report.get("split") == ADJACENT_VALIDATION_SPLIT:
            return report
    return {}


def split_regressions_vs_fixed(split_payloads: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    regressions = []
    for report in split_payloads:
        fixed = total(report.get("fixed_reference_new_bank"))
        candidate = total(report.get(key))
        if fixed is not None and candidate is not None and candidate > fixed:
            regressions.append(
                {
                    "candidate_total": candidate,
                    "fixed_total": fixed,
                    "split": report.get("split"),
                }
            )
    return regressions


def determine_claim(split_payloads: list[dict[str, Any]]) -> str:
    focus = focus_report(split_payloads)
    adjacent = adjacent_report(split_payloads)
    focus_selected = total(focus.get("selected_holdout_new_bank"))
    focus_detector = total(focus.get("detector_holdout_new_bank"))
    adjacent_fixed = total(adjacent.get("fixed_reference_new_bank"))
    adjacent_detector = total(adjacent.get("detector_holdout_new_bank"))
    selected_below = below_count(split_payloads, "selected_holdout_new_bank")
    detector_below = below_count(split_payloads, "detector_holdout_new_bank")
    detector_regressions = split_regressions_vs_fixed(split_payloads, "detector_holdout_new_bank")
    adjacent_ok = (
        adjacent_fixed is not None
        and adjacent_detector is not None
        and adjacent_detector <= adjacent_fixed
    )
    if (
        focus_selected is not None
        and focus_detector is not None
        and focus_detector < focus_selected
        and focus_detector < 16
        and detector_below >= selected_below
        and adjacent_ok
        and not detector_regressions
    ):
        return "P731_PUBLIC_SHIFT_OVERRIDE_IMPROVES_FOCUS_AND_REMOVES_SPLIT_REGRESSIONS"
    if (
        focus_selected is not None
        and focus_detector is not None
        and focus_detector < focus_selected
        and focus_detector < 16
        and detector_below >= selected_below
        and adjacent_ok
    ):
        return "P731_PUBLIC_SHIFT_OVERRIDE_IMPROVES_FOCUS_AND_ADJACENT_VALIDATION"
    if focus_selected is not None and focus_detector is not None and focus_detector < focus_selected:
        return "P731_PUBLIC_SHIFT_OVERRIDE_IMPROVES_FOCUS_WITH_OPEN_STABILITY"
    return "NEGATIVE_RESULT_P731_PUBLIC_SHIFT_OVERRIDE_DOES_NOT_IMPROVE_FOCUS"


def non_target67_materialized_sources(state_dir: Path) -> list[str]:
    paths = sorted(
        state_dir.glob("frontier_public_leaf_policy_p72*_target*_materialized_fixed_row_*_col15_selector_expanded_probe.json")
    )
    return [str(path) for path in paths if "target67" not in path.name and not path.name.startswith("._")]


def compact_split(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "best_heldout_rule_new_bank": compact(report.get("best_heldout_rule_new_bank")),
        "detector": report.get("detector"),
        "detector_holdout_new_bank": compact(report.get("detector_holdout_new_bank")),
        "fixed_reference_new_bank": compact(report.get("fixed_reference_new_bank")),
        "selected_holdout_new_bank": compact(report.get("selected_holdout_new_bank")),
        "selected_rule_name": report.get("selected_rule_name"),
        "split": report.get("split"),
        "topk7_oracle_reference_new_bank": compact(report.get("topk7_oracle_reference_new_bank")),
        "window_ranges": report.get("window_ranges"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = p730.load_json(Path(args.p709))
    p730_payload = p730.load_json(Path(args.p730_reference))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    merged_reports, merged_metadata, merge_stats = p730.p729.build_merged_reports(args)
    all_gates = p730.p729.make_gates(
        merged_reports,
        p730.parse_floats(args.thresholds),
        p730.parse_ints(args.attempt_budgets),
        int_value(args.selector_limit),
    )
    gates = {
        policy_budget: p730.p729.gate_by_policy_budget(all_gates, policy_budget)
        for policy_budget in p730.REGIME_POLICY_BUDGETS
    }
    features_by_window = {
        (int_value(report.get("window_start")), int_value(report.get("window_end"))): p730.window_features(report, gates)
        for report in merged_reports
    }
    rules = p730.make_rules()
    split_payloads = [
        evaluate_split_with_detector(
            split,
            merged_reports,
            merged_metadata,
            gates,
            features_by_window,
            rules,
            factor_charge,
            int_value(args.sample_limit),
        )
        for split in p730.split_reports(merged_reports, args)
    ]
    replay_cache = merged_metadata.get("shared_replay_cache") or {}
    focus = focus_report(split_payloads)
    adjacent = adjacent_report(split_payloads)
    non_target67_sources = non_target67_materialized_sources(STATE_DIR)
    payload = {
        "artifacts": {
            "p709": str(Path(args.p709)),
            "p730": str(Path(args.p730_reference)),
        },
        "claim_status": "",
        "created_at": p730.now_iso(),
        "detector_name": "public_margin_shift_override_v1",
        "disjoint_target_check": {
            "available": bool(non_target67_sources),
            "materialized_source_count": len(non_target67_sources),
            "note": (
                "No non-target67 P724-P728 materialized source bank found; P731 reports adjacent validation only."
                if not non_target67_sources
                else "Non-target67 materialized sources are present but not evaluated by this script."
            ),
            "sources": non_target67_sources[:8],
        },
        "focus_split": FOCUS_SPLIT,
        "focus_summary": {
            "best_heldout_rule_name": (focus.get("best_heldout_rule_new_bank") or {}).get("rule_name"),
            "best_heldout_rule_total": total(focus.get("best_heldout_rule_new_bank")),
            "detector_reason": (focus.get("detector") or {}).get("reason"),
            "detector_rule_name": (focus.get("detector") or {}).get("chosen_rule_name"),
            "detector_total": total(focus.get("detector_holdout_new_bank")),
            "fixed_total": total(focus.get("fixed_reference_new_bank")),
            "p730_focus_detector_comparison_total": (p730_payload.get("focus_summary") or {}).get(
                "selected_rule_total"
            ),
            "p730_focus_heldout_oracle_total": (p730_payload.get("focus_summary") or {}).get(
                "best_heldout_rule_total"
            ),
            "rho_baseline": 16,
            "selected_rule_name": focus.get("selected_rule_name"),
            "selected_rule_total": total(focus.get("selected_holdout_new_bank")),
            "topk7_oracle_reference_total": total(focus.get("topk7_oracle_reference_new_bank")),
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: source rows are archived AutoLab materializer rows.",
            "REPLAY-BACKED: charged candidates use the P719 shared-core replay path.",
            "PUBLIC-SHIFT DETECTOR: decisions use aggregate public candidate-count descriptors and training-selected rules only.",
            "ADJACENT-ONLY VALIDATION: no disjoint target materialized source bank is available in this state.",
            "NO DEPLOYED-CURVE CLAIM: sparse linear algebra, target descent, and large-prime scaling remain open.",
        ],
        "method": "p731_public_regime_shift_override",
        "parameters": {
            "attempt_budgets": p730.parse_ints(args.attempt_budgets),
            "base_source_pattern": args.base_source_pattern,
            "detector_thresholds": {
                "negative_topk_count_delta_max": -5.0,
                "negative_topk_fresh_delta_max": -5.0,
                "positive_holdout_topk_fresh_mean_min": 8.0,
                "positive_holdout_topk_minus_shape_mean_min": 4.0,
                "positive_topk_minus_shape_delta_min": 5.0,
            },
            "factor_bank_charge_over_rho": factor_charge,
            "fresh_source_pattern": args.fresh_source_pattern,
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "rolling_holdout_size": int_value(args.rolling_holdout_size),
            "rolling_train_size": int_value(args.rolling_train_size),
            "selector_limit": int_value(args.selector_limit),
            "target": args.target,
            "thresholds": p730.parse_floats(args.thresholds),
        },
        "replay_metadata": {
            "candidate_count": sum(len(report.get("candidates") or []) for report in merged_reports),
            "shared_replay_cache_count": len(replay_cache),
            "shared_replay_error_count": len(merged_metadata.get("shared_replay_errors") or {}),
            "shared_replay_errors": merged_metadata.get("shared_replay_errors") or {},
            "unique_union_mismatch_count": sum(
                1 for replay in replay_cache.values() if not replay.get("union_matches_all_fields")
            ),
        },
        "schema": "ecdlp.low_term_total2_p731_public_regime_shift_override.v1",
        "source_merge_stats": merge_stats,
        "split_reports": split_payloads,
        "split_summary": {
            "adjacent_detector_total": total(adjacent.get("detector_holdout_new_bank")),
            "adjacent_fixed_total": total(adjacent.get("fixed_reference_new_bank")),
            "adjacent_selected_total": total(adjacent.get("selected_holdout_new_bank")),
            "detector_below_rho_splits": below_count(split_payloads, "detector_holdout_new_bank"),
            "detector_regressions_vs_fixed": split_regressions_vs_fixed(
                split_payloads, "detector_holdout_new_bank"
            ),
            "detector_triggered_splits": [
                report.get("split")
                for report in split_payloads
                if (report.get("detector") or {}).get("triggered")
            ],
            "fixed_reference_below_rho_splits": below_count(split_payloads, "fixed_reference_new_bank"),
            "selected_below_rho_splits": below_count(split_payloads, "selected_holdout_new_bank"),
            "selected_regressions_vs_fixed": split_regressions_vs_fixed(
                split_payloads, "selected_holdout_new_bank"
            ),
            "split_count": len(split_payloads),
        },
    }
    payload["claim_status"] = determine_claim(split_payloads)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budgets", default="1,2")
    parser.add_argument("--base-source-pattern", default=p730.BASE_PATTERN)
    parser.add_argument("--fresh-source-pattern", default=p730.FRESH_PATTERN)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--p730-reference", default=str(P730_REFERENCE))
    parser.add_argument("--rolling-holdout-size", type=int, default=16)
    parser.add_argument("--rolling-train-size", type=int, default=24)
    parser.add_argument("--sample-limit", type=int, default=4)
    parser.add_argument("--selector-limit", type=int, default=10)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--thresholds", default="0.488,0.52,0.544,0.568,0.616,0.888,0.928,1.0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "disjoint_target_check": payload["disjoint_target_check"],
                "focus_summary": payload["focus_summary"],
                "replay_metadata": {
                    key: value
                    for key, value in payload["replay_metadata"].items()
                    if key != "shared_replay_errors"
                },
                "source_merge_stats": payload["source_merge_stats"],
                "split_compact": [compact_split(report) for report in payload["split_reports"]],
                "split_summary": payload["split_summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
