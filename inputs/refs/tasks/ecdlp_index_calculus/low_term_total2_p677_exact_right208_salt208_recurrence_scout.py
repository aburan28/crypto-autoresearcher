#!/usr/bin/env python3
"""P677 exact-recurrence validation for the P676 right208/salt208 surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p676_adjacent_below_rho_surface_corridor_scout as p676


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p677_order9887_exact_right208_salt208_22808_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p677_exact_right208_salt208_source_22808_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p677_exact_right208_salt208_recurrence_scout_22808_probe.json"
TRANSFER = 22808
PHASE = 8
MOD7 = 2
ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}
SALT_LEFTS = {203, 204, 205, 206}


def at_p677_transfer(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return (
            f.get("transfer_index") == TRANSFER
            and f.get("transfer_mod12") == PHASE
            and f.get("transfer_mod7") == MOD7
            and base(f)
        )

    return pred


def anchor(anchor_value: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return f.get("right_anchor") == anchor_value and base(f)

    return pred


def row_pair(salt_left: int, salt_right: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p676.p675.p674.p673.p672.p671.p670.standard_row_pair(f, salt_left, salt_right)

    return pred


def right_salt_union(salt_right: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return any(
            p676.p675.p674.p673.p672.p671.p670.standard_row_pair(f, salt_left, salt_right)
            for salt_left in SALT_LEFTS
        )

    return pred


def right208_salt208(f: dict[str, Any]) -> bool:
    return right_salt_union(208)(f)


def right207_salt207(f: dict[str, Any]) -> bool:
    return right_salt_union(207)(f)


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p677_t22808_phase8_mod7_2_right208_salt208_union",
        "P677 exact +84 recurrence: broad right208/salt208 union",
        at_p677_transfer(right208_salt208),
    ),
    (
        "p677_t22808_phase8_mod7_2_right208_anchor9_salt208_union",
        "P677 exact +84 recurrence: P676 rank-surface anchor9 right208/salt208 union",
        at_p677_transfer(anchor(9, right208_salt208)),
    ),
    (
        "p677_t22808_phase8_mod7_2_right207_salt207_negative_control",
        "P677 sibling negative control: broad right207/salt207 union",
        at_p677_transfer(right207_salt207),
    ),
]

for salt_left in sorted(SALT_LEFTS):
    RULES.extend(
        [
            (
                f"p677_t22808_phase8_mod7_2_right208_salt{salt_left}_salt208",
                f"P677 exact right208 salt{salt_left}_salt208 row-pair split",
                at_p677_transfer(row_pair(salt_left, 208)),
            ),
            (
                f"p677_t22808_phase8_mod7_2_right208_anchor9_salt{salt_left}_salt208",
                f"P677 exact right208 anchor9 salt{salt_left}_salt208 rank-surface split",
                at_p677_transfer(anchor(9, row_pair(salt_left, 208))),
            ),
            (
                f"p677_t22808_phase8_mod7_2_right207_salt{salt_left}_salt207_negative_control",
                f"P677 sibling right207 salt{salt_left}_salt207 negative-control split",
                at_p677_transfer(row_pair(salt_left, 207)),
            ),
        ]
    )

for anchor_value in sorted(ANCHORS):
    RULES.extend(
        [
            (
                f"p677_t22808_phase8_mod7_2_right208_anchor{anchor_value}_salt208_union",
                f"P677 exact right208 anchor{anchor_value} salt208 union",
                at_p677_transfer(anchor(anchor_value, right208_salt208)),
            ),
            (
                f"p677_t22808_phase8_mod7_2_right207_anchor{anchor_value}_salt207_negative_control",
                f"P677 sibling right207 anchor{anchor_value} salt207 negative-control union",
                at_p677_transfer(anchor(anchor_value, right207_salt207)),
            ),
        ]
    )


def report_named(reports: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((r for r in reports if r["rule"] == name), None)


def determine_claim(
    reports: list[dict[str, Any]],
    raw: dict[str, Any],
    claim_prefix: str,
    quiet_claim: str,
) -> str:
    has_below = p676.p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.has_below
    has_rank3 = p676.p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.has_rank3
    broad = report_named(reports, "p677_t22808_phase8_mod7_2_right208_salt208_union")
    anchor9 = report_named(reports, "p677_t22808_phase8_mod7_2_right208_anchor9_salt208_union")
    sibling = report_named(reports, "p677_t22808_phase8_mod7_2_right207_salt207_negative_control")

    if has_below(anchor9) and has_rank3(anchor9):
        return f"{claim_prefix}_EXACT_RIGHT208_ANCHOR9_BELOW_RHO_RANK3_RECURRENCE"
    if has_below(anchor9):
        return f"{claim_prefix}_EXACT_RIGHT208_ANCHOR9_BELOW_RHO_RECURRENCE"
    if has_rank3(anchor9):
        return f"{claim_prefix}_EXACT_RIGHT208_ANCHOR9_RANK3_RECURRENCE"
    if has_below(broad) and has_rank3(broad):
        return f"{claim_prefix}_EXACT_RIGHT208_SALT208_BELOW_RHO_RANK3_RECURRENCE"
    if has_below(broad):
        return f"{claim_prefix}_EXACT_RIGHT208_SALT208_BELOW_RHO_RECURRENCE"
    if has_rank3(broad):
        return f"{claim_prefix}_EXACT_RIGHT208_SALT208_RANK3_RECURRENCE"
    if has_below(sibling):
        return f"{claim_prefix}_SIBLING_RIGHT207_SALT207_BELOW_RHO_CONTROL_POSITIVE"
    if has_rank3(sibling):
        return f"{claim_prefix}_SIBLING_RIGHT207_SALT207_RANK3_CONTROL_POSITIVE"
    if any(r["direct_below_rho_verified_count"] for r in reports):
        return f"{claim_prefix}_REGISTERED_BELOW_RHO_POSITIVE"
    if any(r["rank3_direct_verified_count"] for r in reports):
        return f"{claim_prefix}_REGISTERED_RANK_SURFACE_POSITIVE"
    if any(r["direct_verified_count"] for r in reports):
        return f"{claim_prefix}_REGISTERED_ABOVE_RHO_POSITIVE"
    if raw["direct_verified_count"]:
        return f"NEGATIVE_RESULT_{claim_prefix}_REGISTERED_CONTROLS_MISSED_NONQUIET_BLOCK"
    return quiet_claim


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default=str(DEFAULT_GATE))
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--claim-prefix", default="P677")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P677_EXACT_RIGHT208_SALT208_RECURRENCE_QUIET")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    feature = p676.p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.p643.feature
    features = [feature(case) for case in gate.get("cases", [])]
    summarize_cases = p676.p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.summarize_cases
    raw_summary = summarize_cases(features)
    rule_report = p676.p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.rule_report
    reports = [rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    public_feature_counts = p676.p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.public_feature_counts
    payload = {
        "schema": "ecdlp.low_term_total2_p677_exact_right208_salt208_recurrence_scout.v1",
        "created_at": p676.p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.utc_now(),
        "method": "p677_exact_right208_salt208_recurrence_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": public_feature_counts(features),
            "best_below_rho_rule": max(
                reports,
                key=lambda r: (
                    r["direct_below_rho_verified_count"],
                    r["direct_below_rho_verified_precision"],
                    -r["selected_count"],
                ),
            ),
            "best_direct_verified_rule": max(
                reports,
                key=lambda r: (
                    r["direct_verified_count"],
                    r["direct_verified_precision"],
                    -r["selected_count"],
                ),
            ),
            "best_rank3_rule": max(
                reports,
                key=lambda r: (
                    r["rank3_direct_verified_count"],
                    r["direct_verified_precision"],
                    -r["selected_count"],
                ),
            ),
        },
        "rule_reports": reports,
        "honesty_boundary": [
            "Verifier labels are used only after public selector evaluation.",
            "P677 tests exact-period recurrence of the P676 right208/salt208 relation surface.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
