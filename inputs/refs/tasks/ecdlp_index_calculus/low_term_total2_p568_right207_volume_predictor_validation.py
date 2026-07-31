#!/usr/bin/env python3
"""Validate frozen right-salt-207 volume predictors for order-9887 leaf-16 cases."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p567_phase_route_predictor_validation as p567


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P566_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p566_order9887_leaf16_frozen_root_saved_20605_20616_density_gate_probe.json"
)
DEFAULT_P567_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p567_order9887_phase_route_20617_20628_density_gate_probe.json"
)
DEFAULT_VALIDATION_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p568_order9887_right207_volume_20629_20640_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p568_right207_volume_predictor_validation_20629_20640_probe.json"


Feature = dict[str, Any]
Predicate = Callable[[Feature], bool]


def right207_phase1or6_hit1(row: Feature) -> bool:
    return row["phase_mod12"] in {1, 6} and row["salt_right"] == 207 and row["hit_root_ops"] >= 1


def right207_phase1_hit1(row: Feature) -> bool:
    return row["phase_mod12"] == 1 and row["salt_right"] == 207 and row["hit_root_ops"] >= 1


def right207_anyphase_hit1(row: Feature) -> bool:
    return row["salt_right"] == 207 and row["hit_root_ops"] >= 1


def right207_phase1or6_cost_hybrid_hit1(row: Feature) -> bool:
    return (
        row["phase_mod12"] in {1, 6}
        and row["salt_right"] == 207
        and row["base_selector"] == "mode_cost_hybrid_support_monic_b_total2"
        and row["hit_root_ops"] >= 1
    )


def rule_specs() -> list[tuple[str, str, Predicate]]:
    return [
        (
            "right207_phase1or6_hit1",
            "transfer mod 12 in {1,6}, right row salt=207, hit>=1",
            right207_phase1or6_hit1,
        ),
        (
            "right207_phase1_hit1",
            "transfer mod 12=1, right row salt=207, hit>=1",
            right207_phase1_hit1,
        ),
        (
            "right207_anyphase_hit1",
            "right row salt=207, hit>=1 load control",
            right207_anyphase_hit1,
        ),
        (
            "right207_phase1or6_cost_hybrid_hit1",
            "phase in {1,6}, right row salt=207, cost_hybrid selector, hit>=1",
            right207_phase1or6_cost_hybrid_hit1,
        ),
        (
            "hit_positive_control",
            "hit>=1 public-metric load control",
            p567.hit_positive_control,
        ),
    ]


def summarize_rule(rows: list[Feature], name: str, description: str, predicate: Predicate) -> dict[str, Any]:
    selected = [row for row in rows if predicate(row)]
    verified = [row for row in selected if row["direct_verified"]]
    below_verified = [row for row in selected if row["direct_below_rho_verified"]]
    best_below = sorted(
        below_verified,
        key=lambda row: (
            p567.float_value(row.get("direct_ops_over_rho"), 10**18),
            p567.int_value(row.get("transfer_index")),
            str(row.get("selector")),
        ),
    )
    return {
        "description": description,
        "direct_below_rho_verified_count": len(below_verified),
        "direct_below_rho_verified_precision": p567.ratio(len(below_verified), len(selected)),
        "direct_verified_count": len(verified),
        "direct_verified_precision": p567.ratio(len(verified), len(selected)),
        "examples": [p567.compact_case(row) for row in best_below[:12]],
        "phase_counts": dict(sorted(Counter(str(row["phase_mod12"]) for row in selected).items(), key=lambda item: int(item[0]))),
        "row_pair_counts": dict(Counter(str(row["row_pair"]) for row in selected).most_common(16)),
        "rule": name,
        "selected_case_entries": [row["case_entry"] for row in selected],
        "selected_count": len(selected),
        "selected_direct_below_rho_verified_case_entries": [row["case_entry"] for row in below_verified],
        "selected_fraction": p567.ratio(len(selected), len(rows)),
        "source_counts": dict(sorted(Counter(str(row["source_name"]) for row in selected).items())),
        "transfer_counts": dict(sorted(Counter(str(row["transfer_index"]) for row in selected).items(), key=lambda item: int(item[0]))),
    }


def evaluate(rows: list[Feature]) -> list[dict[str, Any]]:
    reports = [summarize_rule(rows, name, description, predicate) for name, description, predicate in rule_specs()]
    reports.sort(key=lambda report: (0 if report["rule"] == "right207_phase1or6_hit1" else 1, str(report["rule"])))
    return reports


def main_rule_report(reports: list[dict[str, Any]]) -> dict[str, Any]:
    return next(report for report in reports if report["rule"] == "right207_phase1or6_hit1")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p566-gate", type=Path, default=DEFAULT_P566_GATE)
    parser.add_argument("--p567-gate", type=Path, default=DEFAULT_P567_GATE)
    parser.add_argument("--validation-gate", type=Path, default=DEFAULT_VALIDATION_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    training_rows = p567.load_features(args.p566_gate, "p566_train") + p567.load_features(args.p567_gate, "p567_train")
    validation_rows = p567.load_features(args.validation_gate, "p568_validation")
    training_reports = evaluate(training_rows)
    validation_reports = evaluate(validation_rows)
    main_train = main_rule_report(training_reports)
    main_validation = main_rule_report(validation_reports)
    payload = {
        "artifacts": {
            "p566_gate": str(args.p566_gate),
            "p567_gate": str(args.p567_gate),
            "validation_gate": str(args.validation_gate),
        },
        "created_at": p567.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "FROZEN RULE: rule definitions are in this script before validation scoring.",
            "PUBLIC-FEATURE BOUNDARY: selection uses transfer phase, right row salt, base selector for one control, and public gate hit metrics only.",
            "POST-GATE ROUTE: direct selected-leaf hit metrics are public but not yet a cheap source-generation oracle.",
            "NO SPEEDUP CLAIM: this validates route selection, not a complete index-calculus algorithm or deployed-curve break.",
        ],
        "method": "p568_right207_volume_predictor_validation",
        "schema": "ecdlp.low_term_total2_p568_right207_volume_predictor_validation.v1",
        "summary": {
            "claim_status": (
                "FROZEN_RIGHT207_VOLUME_VALIDATION_POSITIVE"
                if main_validation["direct_below_rho_verified_count"]
                else "NEGATIVE_RESULT_FROZEN_RIGHT207_VOLUME_NO_BELOW_RHO_VERIFIED"
            ),
            "main_rule": "right207_phase1or6_hit1",
            "training": {
                "dataset": p567.dataset_summary(training_rows),
                "main_rule": {
                    key: main_train[key]
                    for key in [
                        "selected_count",
                        "direct_verified_count",
                        "direct_below_rho_verified_count",
                        "direct_below_rho_verified_precision",
                        "selected_fraction",
                    ]
                },
            },
            "validation": {
                "dataset": p567.dataset_summary(validation_rows),
                "main_rule": {
                    key: main_validation[key]
                    for key in [
                        "selected_count",
                        "direct_verified_count",
                        "direct_below_rho_verified_count",
                        "direct_below_rho_verified_precision",
                        "selected_fraction",
                    ]
                },
            },
        },
        "training_rule_reports": training_reports,
        "validation_rule_reports": validation_reports,
    }
    p567.write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
