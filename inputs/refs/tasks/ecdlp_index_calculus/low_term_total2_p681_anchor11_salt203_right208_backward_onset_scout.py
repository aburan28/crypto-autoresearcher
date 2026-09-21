#!/usr/bin/env python3
"""P681 backward/onset scan for the P679 low-spend right208 foothold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p639_right208_salt208_recurrence_scout as p639
import low_term_total2_p680_anchor11_salt203_right208_recurrence_scout as p680


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p681_order9887_anchor11_salt203_right208_backward_22711_22723_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p681_anchor11_salt203_right208_backward_source_22711_22723_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p681_anchor11_salt203_right208_backward_onset_scout_22711_22723_probe.json"
TRANSFERS = tuple(range(22711, 22724))
SALT_LEFTS = {203, 204, 205, 206}
ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}


def in_corridor(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(feature: dict[str, Any]) -> bool:
        return feature.get("transfer_index") in TRANSFERS and base(feature)

    return pred


def at_transfer(transfer: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(feature: dict[str, Any]) -> bool:
        return feature.get("transfer_index") == transfer and base(feature)

    return pred


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p681_corridor_right208_anchor11_salt203_salt208",
        "P679 low-spend foothold backward scan: right208/anchor11 salt203_salt208",
        in_corridor(p680.anchor(11, p680.row_pair(203, 208))),
    ),
    (
        "p681_corridor_right208_anchor11_salt203_salt208_mode_cost_hybrid_support_monic_b_total2",
        "P679 quiet-first foothold backward scan: right208/anchor11 salt203_salt208 with mode_cost_hybrid_support_monic_b_total2",
        in_corridor(p680.mode(p680.P679_MODE, p680.anchor(11, p680.row_pair(203, 208)))),
    ),
    (
        "p681_corridor_right208_anchor11_salt208_union",
        "P681 sibling row-pair control: right208/anchor11 all salt208 row-pairs",
        in_corridor(p680.anchor(11, p680.right208_salt208)),
    ),
    (
        "p681_corridor_right208_salt208_union",
        "P681 broad right208/salt208 carrier control",
        in_corridor(p680.right208_salt208),
    ),
    (
        "p681_corridor_right207_anchor8_salt207_union",
        "P674 transition control: right207/anchor8 all salt207 row-pairs",
        in_corridor(p680.anchor(8, p680.right207_salt207)),
    ),
    (
        "p681_corridor_right207_salt207_union",
        "P681 broad right207/salt207 transition control",
        in_corridor(p680.right207_salt207),
    ),
]

for salt_left in sorted(SALT_LEFTS):
    RULES.extend(
        [
            (
                f"p681_corridor_right208_anchor11_salt{salt_left}_salt208",
                f"P681 right208/anchor11 salt{salt_left}_salt208 row-pair split",
                in_corridor(p680.anchor(11, p680.row_pair(salt_left, 208))),
            ),
            (
                f"p681_corridor_right208_salt{salt_left}_salt208",
                f"P681 broad right208 salt{salt_left}_salt208 row-pair split",
                in_corridor(p680.row_pair(salt_left, 208)),
            ),
            (
                f"p681_corridor_right207_anchor8_salt{salt_left}_salt207",
                f"P681 P674 transition right207/anchor8 salt{salt_left}_salt207 split",
                in_corridor(p680.anchor(8, p680.row_pair(salt_left, 207))),
            ),
        ]
    )

for anchor_value in sorted(ANCHORS):
    RULES.extend(
        [
            (
                f"p681_corridor_right208_anchor{anchor_value}_salt208_union",
                f"P681 right208 anchor{anchor_value} salt208 union",
                in_corridor(p680.anchor(anchor_value, p680.right208_salt208)),
            ),
            (
                f"p681_corridor_right207_anchor{anchor_value}_salt207_transition_union",
                f"P681 right207 anchor{anchor_value} salt207 transition union",
                in_corridor(p680.anchor(anchor_value, p680.right207_salt207)),
            ),
        ]
    )

for transfer in TRANSFERS:
    phase = transfer % 12
    mod7 = transfer % 7
    RULES.extend(
        [
            (
                f"p681_t{transfer}_phase{phase}_mod7_{mod7}_right208_anchor11_salt203_salt208",
                f"P681 transfer {transfer} phase{phase}/mod7={mod7} primary right208/anchor11 salt203_salt208",
                at_transfer(transfer, p680.anchor(11, p680.row_pair(203, 208))),
            ),
            (
                f"p681_t{transfer}_phase{phase}_mod7_{mod7}_right207_anchor8_salt207_union",
                f"P681 transfer {transfer} phase{phase}/mod7={mod7} P674 transition right207/anchor8 salt207",
                at_transfer(transfer, p680.anchor(8, p680.right207_salt207)),
            ),
            (
                f"p681_t{transfer}_phase{phase}_mod7_{mod7}_right208_salt208_union",
                f"P681 transfer {transfer} phase{phase}/mod7={mod7} broad right208/salt208",
                at_transfer(transfer, p680.right208_salt208),
            ),
        ]
    )


def report_named(reports: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((report for report in reports if report["rule"] == name), None)


def determine_claim(reports: list[dict[str, Any]], raw_summary: dict[str, Any]) -> str:
    primary = report_named(reports, "p681_corridor_right208_anchor11_salt203_salt208")
    primary_mode = report_named(
        reports,
        "p681_corridor_right208_anchor11_salt203_salt208_mode_cost_hybrid_support_monic_b_total2",
    )
    anchor11 = report_named(reports, "p681_corridor_right208_anchor11_salt208_union")
    broad208 = report_named(reports, "p681_corridor_right208_salt208_union")
    p674 = report_named(reports, "p681_corridor_right207_anchor8_salt207_union")
    broad207 = report_named(reports, "p681_corridor_right207_salt207_union")
    if p680.has_below(primary_mode):
        return "P681_MODE_SPECIFIC_ANCHOR11_SALT203_RIGHT208_BACKWARD_BELOW_RHO"
    if p680.has_below(primary):
        return "P681_ANCHOR11_SALT203_RIGHT208_BACKWARD_BELOW_RHO"
    if p680.has_rank3(primary):
        return "P681_ANCHOR11_SALT203_RIGHT208_BACKWARD_RANK3"
    if p680.has_below(anchor11):
        return "P681_ANCHOR11_RIGHT208_SALT208_BACKWARD_SIBLING_BELOW_RHO"
    if p680.has_below(broad208):
        return "P681_BROAD_RIGHT208_SALT208_BACKWARD_BELOW_RHO"
    if p680.has_rank3(broad208):
        return "P681_BROAD_RIGHT208_SALT208_BACKWARD_RANK3"
    if p680.has_below(p674):
        return "P681_P674_RIGHT207_ANCHOR8_TRANSITION_BELOW_RHO_REPRODUCED"
    if p680.has_rank3(p674):
        return "P681_P674_RIGHT207_ANCHOR8_TRANSITION_RANK3"
    if p680.has_below(broad207):
        return "P681_BROAD_RIGHT207_SALT207_TRANSITION_BELOW_RHO"
    if any(report["direct_below_rho_verified_count"] for report in reports):
        return "P681_REGISTERED_BELOW_RHO_POSITIVE"
    if any(report["rank3_direct_verified_count"] for report in reports):
        return "P681_REGISTERED_RANK_SURFACE_POSITIVE"
    if any(report["direct_verified_count"] for report in reports):
        return "P681_REGISTERED_ABOVE_RHO_POSITIVE"
    if raw_summary["direct_verified_count"]:
        return "NEGATIVE_RESULT_P681_REGISTERED_CONTROLS_MISSED_NONQUIET_BLOCK"
    return "NEGATIVE_RESULT_P681_BACKWARD_ONSET_CORRIDOR_QUIET"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default=str(DEFAULT_GATE))
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p639.feature(case) for case in gate.get("cases", [])]
    raw_summary = p680.summarize_cases(features)
    reports = [p680.rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary)
    payload = {
        "schema": "ecdlp.low_term_total2_p681_anchor11_salt203_right208_backward_onset_scout.v1",
        "created_at": p639.utc_now(),
        "method": "p681_anchor11_salt203_right208_backward_onset_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "parameters": {
            "transfers": list(TRANSFERS),
            "primary_selector": "right208/anchor11/salt203_salt208",
            "mode_specific_selector": p680.P679_MODE,
            "transition_control": "right207/anchor8/salt207",
        },
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p680.public_feature_counts(features),
            "best_below_rho_rule": max(
                reports,
                key=lambda report: (
                    report["direct_below_rho_verified_count"],
                    report["direct_below_rho_verified_precision"],
                    -report["selected_count"],
                ),
            ),
            "best_direct_verified_rule": max(
                reports,
                key=lambda report: (
                    report["direct_verified_count"],
                    report["direct_verified_precision"],
                    -report["selected_count"],
                ),
            ),
            "best_rank3_rule": max(
                reports,
                key=lambda report: (
                    report["rank3_direct_verified_count"],
                    report["direct_verified_precision"],
                    -report["selected_count"],
                ),
            ),
        },
        "rule_reports": reports,
        "honesty_boundary": [
            "Verifier labels are used only after public selector evaluation.",
            "P681 tests backward/onset structure around P676, not a general right208/salt208 theorem.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "A quiet corridor is a scoped negative for this foothold/onset model only.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
