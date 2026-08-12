#!/usr/bin/env python3
"""P680 adjacent/future scan for the P679 low-spend right208 foothold."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p639_right208_salt208_recurrence_scout as p639


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p680_order9887_anchor11_salt203_right208_22809_22821_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p680_anchor11_salt203_right208_source_22809_22821_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p680_anchor11_salt203_right208_recurrence_scout_22809_22821_probe.json"
TRANSFERS = tuple(range(22809, 22822))
SALT_LEFTS = {203, 204, 205, 206}
ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}
P679_MODE = "mode_cost_hybrid_support_monic_b_total2"


def selector_mode(feature: dict[str, Any]) -> str:
    return str(feature.get("selector") or "").split("__", 1)[0]


def in_corridor(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(feature: dict[str, Any]) -> bool:
        return feature.get("transfer_index") in TRANSFERS and base(feature)

    return pred


def row_pair(salt_left: int, salt_right: int) -> Callable[[dict[str, Any]], bool]:
    def pred(feature: dict[str, Any]) -> bool:
        return (
            p639.standard_leaf(feature)
            and feature.get("salt_left") == salt_left
            and feature.get("salt_right") == salt_right
            and feature.get("right_anchor") in ANCHORS
        )

    return pred


def right208_salt208(feature: dict[str, Any]) -> bool:
    return p639.right208_salt208_family(feature)


def right207_salt207(feature: dict[str, Any]) -> bool:
    return (
        p639.standard_leaf(feature)
        and feature.get("salt_left") in SALT_LEFTS
        and feature.get("salt_right") == 207
        and feature.get("right_anchor") in ANCHORS
    )


def anchor(anchor_value: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(feature: dict[str, Any]) -> bool:
        return feature.get("right_anchor") == anchor_value and base(feature)

    return pred


def mode(mode_name: str, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(feature: dict[str, Any]) -> bool:
        return selector_mode(feature) == mode_name and base(feature)

    return pred


def phase_mod(phase: int, mod7: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(feature: dict[str, Any]) -> bool:
        return (
            feature.get("transfer_mod12") == phase
            and feature.get("transfer_mod7") == mod7
            and base(feature)
        )

    return pred


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p680_corridor_right208_anchor11_salt203_salt208",
        "P679 low-spend foothold: right208/anchor11 salt203_salt208",
        in_corridor(anchor(11, row_pair(203, 208))),
    ),
    (
        "p680_corridor_right208_anchor11_salt203_salt208_mode_cost_hybrid_support_monic_b_total2",
        "P679 quiet-first foothold: right208/anchor11 salt203_salt208 with mode_cost_hybrid_support_monic_b_total2",
        in_corridor(mode(P679_MODE, anchor(11, row_pair(203, 208)))),
    ),
    (
        "p680_corridor_right208_anchor11_salt208_union",
        "P680 sibling row-pair control: right208/anchor11 all salt208 row-pairs",
        in_corridor(anchor(11, right208_salt208)),
    ),
    (
        "p680_corridor_right208_salt208_union",
        "P680 broad right208/salt208 carrier control",
        in_corridor(right208_salt208),
    ),
    (
        "p680_corridor_right207_salt207_negative_control",
        "P680 broad right207/salt207 negative control",
        in_corridor(right207_salt207),
    ),
]

for salt_left in sorted(SALT_LEFTS):
    RULES.extend(
        [
            (
                f"p680_corridor_right208_anchor11_salt{salt_left}_salt208",
                f"P680 right208/anchor11 salt{salt_left}_salt208 row-pair split",
                in_corridor(anchor(11, row_pair(salt_left, 208))),
            ),
            (
                f"p680_corridor_right208_salt{salt_left}_salt208",
                f"P680 broad right208 salt{salt_left}_salt208 row-pair split",
                in_corridor(row_pair(salt_left, 208)),
            ),
            (
                f"p680_corridor_right207_salt{salt_left}_salt207_negative_control",
                f"P680 right207 salt{salt_left}_salt207 negative-control split",
                in_corridor(row_pair(salt_left, 207)),
            ),
        ]
    )

for anchor_value in sorted(ANCHORS):
    RULES.extend(
        [
            (
                f"p680_corridor_right208_anchor{anchor_value}_salt208_union",
                f"P680 right208 anchor{anchor_value} salt208 union",
                in_corridor(anchor(anchor_value, right208_salt208)),
            ),
            (
                f"p680_corridor_right207_anchor{anchor_value}_salt207_negative_control",
                f"P680 right207 anchor{anchor_value} salt207 negative-control union",
                in_corridor(anchor(anchor_value, right207_salt207)),
            ),
        ]
    )

for transfer in TRANSFERS:
    phase = transfer % 12
    mod7 = transfer % 7
    RULES.extend(
        [
            (
                f"p680_t{transfer}_phase{phase}_mod7_{mod7}_right208_anchor11_salt203_salt208",
                f"P680 transfer {transfer} phase{phase}/mod7={mod7} primary right208/anchor11 salt203_salt208",
                lambda feature, transfer=transfer: feature.get("transfer_index") == transfer
                and anchor(11, row_pair(203, 208))(feature),
            ),
            (
                f"p680_t{transfer}_phase{phase}_mod7_{mod7}_right208_salt208_union",
                f"P680 transfer {transfer} phase{phase}/mod7={mod7} broad right208/salt208",
                lambda feature, transfer=transfer: feature.get("transfer_index") == transfer
                and right208_salt208(feature),
            ),
            (
                f"p680_phase{phase}_mod7_{mod7}_right208_anchor11_salt203_salt208",
                f"P680 phase{phase}/mod7={mod7} primary right208/anchor11 salt203_salt208",
                in_corridor(phase_mod(phase, mod7, anchor(11, row_pair(203, 208)))),
            ),
        ]
    )


def feature_id(feature: dict[str, Any]) -> str:
    return (
        f"phase{feature.get('transfer_mod12')}_mod7{feature.get('transfer_mod7')}"
        f"_right{feature.get('salt_right')}_anchor{feature.get('right_anchor')}"
        f"_salt{feature.get('salt_left')}_salt{feature.get('salt_right')}"
        f"_{selector_mode(feature)}"
    )


def case_entry(feature: dict[str, Any]) -> str:
    return f"{feature.get('target')}|{feature.get('transfer_index')}|{feature.get('selector')}|{feature.get('top_k')}"


def summarize_cases(features: list[dict[str, Any]]) -> dict[str, Any]:
    verified = [feature for feature in features if feature.get("direct_verified")]
    below = [feature for feature in features if feature.get("direct_below_rho_verified")]
    rank3 = [feature for feature in verified if int(feature.get("rank") or 0) >= 3]
    return {
        "case_count": len(features),
        "direct_verified_count": len(verified),
        "direct_below_rho_verified_count": len(below),
        "rank3_direct_verified_count": len(rank3),
        "verified_transfer_counts": dict(Counter(str(feature["transfer_index"]) for feature in verified)),
        "positive_transfer_counts": dict(Counter(str(feature["transfer_index"]) for feature in below)),
        "verified_feature_counts": dict(Counter(feature_id(feature) for feature in verified)),
        "positive_feature_counts": dict(Counter(feature_id(feature) for feature in below)),
        "verified_rank_counts": dict(Counter(str(feature.get("rank")) for feature in verified)),
        "below_ops_over_rho_counts": dict(Counter(str(feature.get("direct_ops_over_rho")) for feature in below)),
    }


def public_feature_counts(features: list[dict[str, Any]]) -> dict[str, Any]:
    verified = [feature for feature in features if feature.get("direct_verified")]
    below = [feature for feature in features if feature.get("direct_below_rho_verified")]
    rank3 = [feature for feature in verified if int(feature.get("rank") or 0) >= 3]

    def counts(key: str, rows: list[dict[str, Any]]) -> dict[str, int]:
        return dict(Counter(str(row.get(key)) for row in rows))

    return {
        "verified_anchor_counts": counts("right_anchor", verified),
        "verified_row_pair_counts": counts("row_pair", verified),
        "verified_mode_counts": dict(Counter(selector_mode(row) for row in verified)),
        "below_anchor_counts": counts("right_anchor", below),
        "below_row_pair_counts": counts("row_pair", below),
        "below_mode_counts": dict(Counter(selector_mode(row) for row in below)),
        "rank3_anchor_counts": counts("right_anchor", rank3),
        "rank3_row_pair_counts": counts("row_pair", rank3),
        "rank3_mode_counts": dict(Counter(selector_mode(row) for row in rank3)),
    }


def rule_report(
    name: str,
    description: str,
    pred: Callable[[dict[str, Any]], bool],
    features: list[dict[str, Any]],
    raw_summary: dict[str, Any],
) -> dict[str, Any]:
    selected = [feature for feature in features if pred(feature)]
    verified = [feature for feature in selected if feature.get("direct_verified")]
    below = [feature for feature in selected if feature.get("direct_below_rho_verified")]
    rank3 = [feature for feature in verified if int(feature.get("rank") or 0) >= 3]
    selected_count = len(selected)
    return {
        "rule": name,
        "description": description,
        "selected_count": selected_count,
        "selected_fraction": selected_count / max(1, raw_summary["case_count"]),
        "direct_verified_count": len(verified),
        "direct_below_rho_verified_count": len(below),
        "rank3_direct_verified_count": len(rank3),
        "direct_verified_precision": len(verified) / selected_count if selected_count else 0.0,
        "direct_below_rho_verified_precision": len(below) / selected_count if selected_count else 0.0,
        "direct_below_rho_verified_recall": len(below)
        / max(1, raw_summary["direct_below_rho_verified_count"]),
        "transfer_counts": dict(Counter(str(feature["transfer_index"]) for feature in selected)),
        "below_transfer_counts": dict(Counter(str(feature["transfer_index"]) for feature in below)),
        "rank3_transfer_counts": dict(Counter(str(feature["transfer_index"]) for feature in rank3)),
        "right_anchor_counts": dict(Counter(str(feature["right_anchor"]) for feature in selected)),
        "row_pair_counts": dict(Counter(str(feature["row_pair"]) for feature in selected)),
        "mode_counts": dict(Counter(selector_mode(feature) for feature in selected)),
        "positive_feature_counts": dict(Counter(feature_id(feature) for feature in below)),
        "rank3_feature_counts": dict(Counter(feature_id(feature) for feature in rank3)),
        "selected_direct_verified_case_entries": [case_entry(feature) for feature in verified],
        "selected_direct_below_rho_verified_case_entries": [case_entry(feature) for feature in below],
        "examples": selected[:24],
        "positive_examples": below[:24],
        "rank3_examples": rank3[:24],
    }


def report_named(reports: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((report for report in reports if report["rule"] == name), None)


def has_below(report: dict[str, Any] | None) -> bool:
    return bool(report and report["direct_below_rho_verified_count"])


def has_rank3(report: dict[str, Any] | None) -> bool:
    return bool(report and report["rank3_direct_verified_count"])


def determine_claim(reports: list[dict[str, Any]], raw_summary: dict[str, Any]) -> str:
    primary = report_named(reports, "p680_corridor_right208_anchor11_salt203_salt208")
    primary_mode = report_named(
        reports,
        "p680_corridor_right208_anchor11_salt203_salt208_mode_cost_hybrid_support_monic_b_total2",
    )
    anchor11 = report_named(reports, "p680_corridor_right208_anchor11_salt208_union")
    broad = report_named(reports, "p680_corridor_right208_salt208_union")
    right207 = report_named(reports, "p680_corridor_right207_salt207_negative_control")
    if has_below(primary_mode):
        return "P680_MODE_SPECIFIC_ANCHOR11_SALT203_RIGHT208_BELOW_RHO_RECURRENCE"
    if has_below(primary):
        return "P680_ANCHOR11_SALT203_RIGHT208_BELOW_RHO_RECURRENCE"
    if has_rank3(primary):
        return "P680_ANCHOR11_SALT203_RIGHT208_RANK3_RECURRENCE"
    if has_below(anchor11):
        return "P680_ANCHOR11_RIGHT208_SALT208_SIBLING_BELOW_RHO_DRIFT"
    if has_rank3(anchor11):
        return "P680_ANCHOR11_RIGHT208_SALT208_SIBLING_RANK3_DRIFT"
    if has_below(broad):
        return "P680_BROAD_RIGHT208_SALT208_BELOW_RHO_DRIFT"
    if has_rank3(broad):
        return "P680_BROAD_RIGHT208_SALT208_RANK3_DRIFT"
    if has_below(right207):
        return "P680_RIGHT207_SALT207_NEGATIVE_CONTROL_BELOW_RHO_POSITIVE"
    if any(report["direct_below_rho_verified_count"] for report in reports):
        return "P680_REGISTERED_BELOW_RHO_POSITIVE"
    if any(report["rank3_direct_verified_count"] for report in reports):
        return "P680_REGISTERED_RANK_SURFACE_POSITIVE"
    if any(report["direct_verified_count"] for report in reports):
        return "P680_REGISTERED_ABOVE_RHO_POSITIVE"
    if raw_summary["direct_verified_count"]:
        return "NEGATIVE_RESULT_P680_REGISTERED_CONTROLS_MISSED_NONQUIET_BLOCK"
    return "NEGATIVE_RESULT_P680_ANCHOR11_SALT203_RIGHT208_CORRIDOR_QUIET"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default=str(DEFAULT_GATE))
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p639.feature(case) for case in gate.get("cases", [])]
    raw_summary = summarize_cases(features)
    reports = [rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary)
    payload = {
        "schema": "ecdlp.low_term_total2_p680_anchor11_salt203_right208_recurrence_scout.v1",
        "created_at": p639.utc_now(),
        "method": "p680_anchor11_salt203_right208_recurrence_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "parameters": {
            "transfers": list(TRANSFERS),
            "primary_selector": "right208/anchor11/salt203_salt208",
            "mode_specific_selector": P679_MODE,
        },
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": public_feature_counts(features),
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
            "P680 tests adjacent/future drift of the P679 low-spend right208/anchor11/salt203_salt208 foothold.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "A quiet corridor is a scoped negative for this foothold only, not for right208/salt208 or index calculus.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
