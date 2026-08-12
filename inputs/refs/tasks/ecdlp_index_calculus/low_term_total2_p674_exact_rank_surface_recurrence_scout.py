#!/usr/bin/env python3
"""P674 exact-repeat validation for P673 rank-surface material."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p673_adjacent_row_pair_shift_corridor_scout as p673


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p674_order9887_exact_rank_surface_22722_22723_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p674_exact_rank_surface_source_22722_22723_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p674_exact_rank_surface_recurrence_scout_22722_22723_probe.json"
T_PHASE6 = 22722
T_PHASE7 = 22723


def at_transfer(transfer_index: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return f.get("transfer_index") == transfer_index and base(f)

    return pred


def phase_mod(phase: int, mod7: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return f.get("transfer_mod12") == phase and f.get("transfer_mod7") == mod7 and base(f)

    return pred


def phase_mod_anchor(
    phase: int, mod7: int, anchor: int, base: Callable[[dict[str, Any]], bool]
) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return (
            f.get("transfer_mod12") == phase
            and f.get("transfer_mod7") == mod7
            and f.get("right_anchor") == anchor
            and base(f)
        )

    return pred


def row_pair(salt_left: int, salt_right: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p673.p672.p671.p670.standard_row_pair(f, salt_left, salt_right)

    return pred


def right207_salt206_salt207(f: dict[str, Any]) -> bool:
    return p673.p672.p671.p670.standard_row_pair(f, 206, 207)


def right208_salt206_salt208(f: dict[str, Any]) -> bool:
    return p673.p672.p671.p670.standard_row_pair(f, 206, 208)


def right206_salt204_salt206(f: dict[str, Any]) -> bool:
    return p673.p672.p671.p670.standard_row_pair(f, 204, 206)


def exact_phase6(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_PHASE6, phase_mod(6, 0, base))


def exact_phase6_anchor(anchor: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_PHASE6, phase_mod_anchor(6, 0, anchor, base))


def exact_phase7(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_PHASE7, phase_mod(7, 1, base))


def exact_phase7_anchor(anchor: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_PHASE7, phase_mod_anchor(7, 1, anchor, base))


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p674_t22722_phase6_mod7_0_right207_salt206_salt207",
        "P673 transfer-22638 +84: phase6/mod7=0 right207 salt206_salt207",
        exact_phase6(right207_salt206_salt207),
    ),
    (
        "p674_t22722_phase6_mod7_0_right207_anchor9_salt206_salt207",
        "P673 transfer-22638 +84: phase6/mod7=0 right207 anchor9 salt206_salt207",
        exact_phase6_anchor(9, right207_salt206_salt207),
    ),
    (
        "p674_t22722_phase6_mod7_0_right208_salt206_salt208",
        "P673 transfer-22638 +84: phase6/mod7=0 right208 salt206_salt208",
        exact_phase6(right208_salt206_salt208),
    ),
    (
        "p674_t22722_phase6_mod7_0_right208_anchor9_salt206_salt208",
        "P673 transfer-22638 +84: phase6/mod7=0 right208 anchor9 salt206_salt208",
        exact_phase6_anchor(9, right208_salt206_salt208),
    ),
    (
        "p674_t22722_phase6_mod7_0_right206_anchor9_salt204_salt206",
        "P673 transfer-22638 +84: phase6/mod7=0 right206 anchor9 salt204_salt206",
        exact_phase6_anchor(9, right206_salt204_salt206),
    ),
    (
        "p674_t22722_phase6_mod7_0_right206_salt204_salt206",
        "P673 transfer-22638 +84: phase6/mod7=0 right206 salt204_salt206 all-anchor control",
        exact_phase6(right206_salt204_salt206),
    ),
    (
        "p674_t22723_phase7_mod7_1_right206_anchor6_salt204_salt206",
        "P673 transfer-22639 +84: phase7/mod7=1 right206 anchor6 salt204_salt206",
        exact_phase7_anchor(6, right206_salt204_salt206),
    ),
    (
        "p674_t22723_phase7_mod7_1_right206_salt204_salt206",
        "P673 transfer-22639 +84: phase7/mod7=1 right206 salt204_salt206 all-anchor control",
        exact_phase7(right206_salt204_salt206),
    ),
]

for salt_left, salt_right in [(203, 207), (205, 207), (206, 207), (206, 208), (204, 206)]:
    RULES.extend(
        [
            (
                f"p674_t22722_phase6_mod7_0_salt{salt_left}_salt{salt_right}",
                f"P674 phase6/mod7=0 sibling row pair salt{salt_left}_salt{salt_right}",
                exact_phase6(row_pair(salt_left, salt_right)),
            ),
            (
                f"p674_t22723_phase7_mod7_1_salt{salt_left}_salt{salt_right}",
                f"P674 phase7/mod7=1 sibling row pair salt{salt_left}_salt{salt_right}",
                exact_phase7(row_pair(salt_left, salt_right)),
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
    has_below = p673.p672.p671.p670.p669.p668.p667.p666.p665.has_below
    has_rank3 = p673.p672.p671.p670.p669.p668.p667.p666.p665.has_rank3
    r207 = report_named(reports, "p674_t22722_phase6_mod7_0_right207_salt206_salt207")
    r208 = report_named(reports, "p674_t22722_phase6_mod7_0_right208_salt206_salt208")
    r206_22638 = report_named(reports, "p674_t22722_phase6_mod7_0_right206_anchor9_salt204_salt206")
    r206_22639 = report_named(reports, "p674_t22723_phase7_mod7_1_right206_anchor6_salt204_salt206")

    if has_below(r207) or has_below(r208) or has_below(r206_22638) or has_below(r206_22639):
        return f"{claim_prefix}_EXACT_RANK_SURFACE_BELOW_RHO_RECURRENCE"
    if has_rank3(r207) and has_rank3(r208):
        return f"{claim_prefix}_EXACT_PHASE6_RIGHT207_RIGHT208_RANK_SURFACE_RECURRENCE"
    if has_rank3(r207):
        return f"{claim_prefix}_EXACT_PHASE6_RIGHT207_RANK_SURFACE_RECURRENCE"
    if has_rank3(r208):
        return f"{claim_prefix}_EXACT_PHASE6_RIGHT208_RANK_SURFACE_RECURRENCE"
    if has_rank3(r206_22638) or has_rank3(r206_22639):
        return f"{claim_prefix}_EXACT_RIGHT206_RANK_SURFACE_RECURRENCE"
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
    parser.add_argument("--claim-prefix", default="P674")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P674_EXACT_RANK_SURFACE_REPEATS_QUIET")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p673.p672.p671.p670.p669.p668.p667.p666.p665.p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p673.p672.p671.p670.p669.p668.p667.p666.p665.summarize_cases(features)
    reports = [
        p673.p672.p671.p670.p669.p668.p667.p666.p665.rule_report(name, desc, pred, features, raw_summary)
        for name, desc, pred in RULES
    ]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p674_exact_rank_surface_recurrence_scout.v1",
        "created_at": p673.p672.p671.p670.p669.p668.p667.p666.p665.utc_now(),
        "method": "p674_exact_rank_surface_recurrence_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p673.p672.p671.p670.p669.p668.p667.p666.p665.public_feature_counts(features),
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
            "P674 tests exact recurrence of P673 rank-surface material.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
