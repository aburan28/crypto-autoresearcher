#!/usr/bin/env python3
"""P735 public detector repair for P734 target-22050 complete coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p731_public_regime_shift_override as p731


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p735_target22050_public_detector_repair_probe.json"
ORIGINAL_DETECTOR_CHOICE = p731.detector_choice


def float_value(value: Any, default: float = 0.0) -> float:
    return p731.float_value(value, default)


def total(report: dict[str, Any] | None) -> float | None:
    return p731.total(report)


def repaired_detector_choice(
    selected_rule_name: str,
    train: dict[str, Any],
    holdout: dict[str, Any],
) -> dict[str, Any]:
    if p731.uses_topk(selected_rule_name):
        holdout_fresh = float_value(holdout.get("fresh_count_mean"))
        holdout_topk_fresh = float_value(holdout.get("topk7_fresh_count_mean"))
        holdout_topk_minus_shape = float_value(holdout.get("topk7_minus_shape_mean"))
        if holdout_fresh <= 1.0 and holdout_topk_fresh <= 1.0:
            return {
                "chosen_rule_name": p731.FIXED_RULE,
                "reason": "p735_no_fresh_topk_support",
                "triggered": True,
            }
        if holdout_fresh >= 8.0 and holdout_topk_minus_shape <= -4.0:
            return {
                "chosen_rule_name": p731.FIXED_RULE,
                "reason": "p735_shape_dominant_fresh_coverage",
                "triggered": True,
            }
    return ORIGINAL_DETECTOR_CHOICE(selected_rule_name, train, holdout)


def detector_regressions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return (payload.get("split_summary") or {}).get("detector_regressions_vs_fixed") or []


def below_count(payload: dict[str, Any], key: str) -> int:
    return sum(1 for report in payload.get("split_reports") or [] if (report.get(key) or {}).get("beats_rho_with_fallback"))


def determine_claim(payload: dict[str, Any]) -> str:
    focus = p731.focus_report(payload.get("split_reports") or [])
    focus_fixed = total(focus.get("fixed_reference_new_bank"))
    focus_selected = total(focus.get("selected_holdout_new_bank"))
    focus_detector = total(focus.get("detector_holdout_new_bank"))
    regressions = detector_regressions(payload)
    detector_below = below_count(payload, "detector_holdout_new_bank")
    fixed_below = below_count(payload, "fixed_reference_new_bank")
    if (
        focus_fixed is not None
        and focus_detector is not None
        and focus_detector <= focus_fixed
        and detector_below >= fixed_below
        and not regressions
    ):
        return "P735_PUBLIC_POLARITY_FALLBACK_REMOVES_TARGET22050_DETECTOR_REGRESSIONS"
    if focus_selected is not None and focus_detector is not None and focus_detector < focus_selected:
        return "P735_PUBLIC_POLARITY_FALLBACK_IMPROVES_FOCUS_WITH_OPEN_STABILITY"
    return "NEGATIVE_RESULT_P735_PUBLIC_POLARITY_FALLBACK_DOES_NOT_REPAIR_FOCUS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p731.detector_choice = repaired_detector_choice
    payload = p731.analyze(args)
    payload["detector_repair"] = {
        "name": "p735_public_topk_polarity_fallback",
        "rules": [
            "if selected uses top-k and holdout fresh/top-k-fresh means are near zero, choose fixed",
            "if selected uses top-k and holdout fresh coverage is high but topk7_minus_shape_mean <= -4, choose fixed",
            "otherwise use P731 public_margin_shift_override_v1",
        ],
        "fresh_high_threshold": 8.0,
        "no_fresh_threshold": 1.0,
        "shape_dominant_topk7_minus_shape_max": -4.0,
    }
    payload["p731_claim_status_with_repaired_detector"] = payload.get("claim_status")
    payload["claim_status"] = determine_claim(payload)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budgets", default="1,2")
    parser.add_argument("--base-source-pattern", default=p731.p730.BASE_PATTERN)
    parser.add_argument("--fresh-source-pattern", default=p731.p730.FRESH_PATTERN)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(p731.DEFAULT_P709))
    parser.add_argument("--p730-reference", default=str(p731.P730_REFERENCE))
    parser.add_argument("--rolling-holdout-size", type=int, default=16)
    parser.add_argument("--rolling-train-size", type=int, default=24)
    parser.add_argument("--sample-limit", type=int, default=4)
    parser.add_argument("--selector-limit", type=int, default=10)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--thresholds", default="0.488,0.52,0.544,0.568,0.616,0.888,0.928,1.0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    p731.write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "detector_repair": payload["detector_repair"],
                "focus_summary": payload["focus_summary"],
                "p731_claim_status_with_repaired_detector": payload["p731_claim_status_with_repaired_detector"],
                "replay_metadata": {
                    key: value
                    for key, value in payload["replay_metadata"].items()
                    if key != "shared_replay_errors"
                },
                "source_merge_stats": payload["source_merge_stats"],
                "split_summary": payload["split_summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
