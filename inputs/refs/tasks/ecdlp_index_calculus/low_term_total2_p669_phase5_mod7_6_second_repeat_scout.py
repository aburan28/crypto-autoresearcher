#!/usr/bin/env python3
"""P669 second-repeat validation for the phase5/mod7=6 salt206 recurrence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p668_right207_salt207_exact_repeats_scout as p668


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p669_order9887_phase5_mod7_6_second_repeat_22548_22560_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p669_phase5_mod7_6_second_repeat_source_22548_22560_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p669_phase5_mod7_6_second_repeat_scout_22548_22560_probe.json"
EXACT_TRANSFER = 22553
ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}


def standard_row_pair(f: dict[str, Any], salt_left: int, salt_right: int) -> bool:
    return p668.p667.p666.p665.standard_row_pair(f, salt_left, salt_right)


def right206_salt204_salt206(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 204, 206)


def right207_salt206_salt207(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 206, 207)


def right208_salt206_salt208(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 206, 208)


def repeat_salt206_union(f: dict[str, Any]) -> bool:
    return right207_salt206_salt207(f) or right208_salt206_salt208(f)


def phase5_mod7_6(f: dict[str, Any]) -> bool:
    return f.get("transfer_mod12") == 5 and f.get("transfer_mod7") == 6


def exact_transfer(f: dict[str, Any]) -> bool:
    return f.get("transfer_index") == EXACT_TRANSFER


def exact_pred(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return exact_transfer(f) and phase5_mod7_6(f) and base(f)

    return pred


def corridor_pred(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return phase5_mod7_6(f) and base(f)

    return pred


def exact_anchor_pred(base: Callable[[dict[str, Any]], bool], anchor: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return exact_transfer(f) and phase5_mod7_6(f) and base(f) and f.get("right_anchor") == anchor

    return pred


def corridor_anchor_pred(base: Callable[[dict[str, Any]], bool], anchor: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return phase5_mod7_6(f) and base(f) and f.get("right_anchor") == anchor

    return pred


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p669_exact_22553_phase5_mod7_6_right207_salt206_salt207",
        "Second +84 repeat at transfer 22553: right207 salt206_salt207",
        exact_pred(right207_salt206_salt207),
    ),
    (
        "p669_exact_22553_phase5_mod7_6_right208_salt206_salt208",
        "Second +84 repeat at transfer 22553: right208 salt206_salt208",
        exact_pred(right208_salt206_salt208),
    ),
    (
        "p669_exact_22553_phase5_mod7_6_repeat_salt206_union",
        "Second +84 repeat at transfer 22553: right207/right208 salt206 union",
        exact_pred(repeat_salt206_union),
    ),
    (
        "p669_exact_22553_phase5_mod7_6_right206_salt204_salt206_rank_side",
        "Second +84 repeat at transfer 22553: right206 salt204_salt206 rank-side diagnostic",
        exact_pred(right206_salt204_salt206),
    ),
    (
        "p669_corridor_phase5_mod7_6_right207_salt206_salt207",
        "Corridor phase5/mod7=6 right207 salt206_salt207",
        corridor_pred(right207_salt206_salt207),
    ),
    (
        "p669_corridor_phase5_mod7_6_right208_salt206_salt208",
        "Corridor phase5/mod7=6 right208 salt206_salt208",
        corridor_pred(right208_salt206_salt208),
    ),
    (
        "p669_corridor_phase5_mod7_6_repeat_salt206_union",
        "Corridor phase5/mod7=6 right207/right208 salt206 union",
        corridor_pred(repeat_salt206_union),
    ),
    (
        "p669_corridor_phase5_mod7_6_right206_salt204_salt206_rank_side",
        "Corridor phase5/mod7=6 right206 salt204_salt206 rank-side diagnostic",
        corridor_pred(right206_salt204_salt206),
    ),
]

for anchor in sorted(ANCHORS):
    RULES.extend(
        [
            (
                f"p669_exact_22553_phase5_mod7_6_right207_anchor{anchor}_salt206_salt207",
                f"Transfer 22553 right207 salt206_salt207 anchor {anchor}",
                exact_anchor_pred(right207_salt206_salt207, anchor),
            ),
            (
                f"p669_exact_22553_phase5_mod7_6_right208_anchor{anchor}_salt206_salt208",
                f"Transfer 22553 right208 salt206_salt208 anchor {anchor}",
                exact_anchor_pred(right208_salt206_salt208, anchor),
            ),
            (
                f"p669_corridor_phase5_mod7_6_right207_anchor{anchor}_salt206_salt207",
                f"Corridor right207 salt206_salt207 anchor {anchor}",
                corridor_anchor_pred(right207_salt206_salt207, anchor),
            ),
            (
                f"p669_corridor_phase5_mod7_6_right208_anchor{anchor}_salt206_salt208",
                f"Corridor right208 salt206_salt208 anchor {anchor}",
                corridor_anchor_pred(right208_salt206_salt208, anchor),
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
    exact_union = report_named(reports, "p669_exact_22553_phase5_mod7_6_repeat_salt206_union")
    exact_r207 = report_named(reports, "p669_exact_22553_phase5_mod7_6_right207_salt206_salt207")
    exact_r208 = report_named(reports, "p669_exact_22553_phase5_mod7_6_right208_salt206_salt208")
    exact_r206 = report_named(reports, "p669_exact_22553_phase5_mod7_6_right206_salt204_salt206_rank_side")
    corridor_union = report_named(reports, "p669_corridor_phase5_mod7_6_repeat_salt206_union")

    has_below = p668.p667.p666.p665.has_below
    has_rank3 = p668.p667.p666.p665.has_rank3

    if has_below(exact_union) and has_rank3(exact_union):
        return f"{claim_prefix}_EXACT_22553_SALT206_UNION_BELOW_RHO_RANK3_SECOND_RECURRENCE"
    if has_below(exact_union):
        return f"{claim_prefix}_EXACT_22553_SALT206_UNION_BELOW_RHO_SECOND_RECURRENCE"
    if has_below(exact_r207):
        return f"{claim_prefix}_EXACT_22553_RIGHT207_SALT206_SALT207_BELOW_RHO_SECOND_RECURRENCE"
    if has_below(exact_r208):
        return f"{claim_prefix}_EXACT_22553_RIGHT208_SALT206_SALT208_BELOW_RHO_SECOND_RECURRENCE"
    if has_rank3(exact_union):
        return f"{claim_prefix}_EXACT_22553_SALT206_UNION_RANK3_SECOND_RECURRENCE"
    if has_rank3(exact_r206):
        return f"{claim_prefix}_EXACT_22553_RIGHT206_RANK3_SIDE_SECOND_RECURRENCE"
    if has_below(corridor_union):
        return f"{claim_prefix}_CORRIDOR_PHASE5_MOD7_6_SALT206_UNION_BELOW_RHO_DRIFT"
    if has_rank3(corridor_union):
        return f"{claim_prefix}_CORRIDOR_PHASE5_MOD7_6_SALT206_UNION_RANK3_DRIFT"
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
    parser.add_argument("--claim-prefix", default="P669")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P669_PHASE5_MOD7_6_SECOND_REPEAT_QUIET")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p668.p667.p666.p665.p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p668.p667.p666.p665.summarize_cases(features)
    reports = [p668.p667.p666.p665.rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p669_phase5_mod7_6_second_repeat_scout.v1",
        "created_at": p668.p667.p666.p665.utc_now(),
        "method": "p669_phase5_mod7_6_second_repeat_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p668.p667.p666.p665.public_feature_counts(features),
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
            "P669 tests a second +84 recurrence for the P668 phase5/mod7=6 salt206 branch.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
