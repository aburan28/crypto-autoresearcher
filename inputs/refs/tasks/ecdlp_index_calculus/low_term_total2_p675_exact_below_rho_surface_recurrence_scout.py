#!/usr/bin/env python3
"""P675 exact-repeat validation for the P674 below-rho right207 surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p674_exact_rank_surface_recurrence_scout as p674


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p675_order9887_exact_below_rho_surface_22807_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p675_exact_below_rho_surface_source_22807_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p675_exact_below_rho_surface_recurrence_scout_22807_probe.json"
T_SURFACE = 22807
ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}
SALT207_LEFTS = {203, 204, 205, 206}


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
        return p674.p673.p672.p671.p670.standard_row_pair(f, salt_left, salt_right)

    return pred


def right207_salt207_pair(salt_left: int) -> Callable[[dict[str, Any]], bool]:
    return row_pair(salt_left, 207)


def right207_salt207(f: dict[str, Any]) -> bool:
    return any(p674.p673.p672.p671.p670.standard_row_pair(f, salt_left, 207) for salt_left in SALT207_LEFTS)


def exact_phase7(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_SURFACE, phase_mod(7, 1, base))


def exact_phase7_anchor(anchor: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_SURFACE, phase_mod_anchor(7, 1, anchor, base))


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p675_t22807_phase7_mod7_1_right207_anchor8_salt207_union",
        "P674 transfer-22723 +84: phase7/mod7=1 right207 anchor8 salt207 union",
        exact_phase7_anchor(8, right207_salt207),
    ),
    (
        "p675_t22807_phase7_mod7_1_right207_salt207_union",
        "P674 transfer-22723 +84: phase7/mod7=1 broad right207 salt207 union",
        exact_phase7(right207_salt207),
    ),
]

for salt_left in sorted(SALT207_LEFTS):
    RULES.extend(
        [
            (
                f"p675_t22807_phase7_mod7_1_right207_anchor8_salt{salt_left}_salt207",
                f"P674 transfer-22723 +84: phase7/mod7=1 right207 anchor8 salt{salt_left}_salt207",
                exact_phase7_anchor(8, right207_salt207_pair(salt_left)),
            ),
            (
                f"p675_t22807_phase7_mod7_1_right207_salt{salt_left}_salt207",
                f"P674 transfer-22723 +84: phase7/mod7=1 right207 salt{salt_left}_salt207 all-anchor",
                exact_phase7(right207_salt207_pair(salt_left)),
            ),
        ]
    )

for anchor in sorted(ANCHORS):
    RULES.append(
        (
            f"p675_t22807_phase7_mod7_1_right207_anchor{anchor}_salt207_union",
            f"P675 phase7/mod7=1 right207 anchor{anchor} salt207 sibling-anchor split",
            exact_phase7_anchor(anchor, right207_salt207),
        )
    )


def report_named(reports: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((r for r in reports if r["rule"] == name), None)


def determine_claim(
    reports: list[dict[str, Any]],
    raw: dict[str, Any],
    claim_prefix: str,
    quiet_claim: str,
) -> str:
    has_below = p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.has_below
    has_rank3 = p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.has_rank3
    primary = report_named(reports, "p675_t22807_phase7_mod7_1_right207_anchor8_salt207_union")
    broad = report_named(reports, "p675_t22807_phase7_mod7_1_right207_salt207_union")

    if has_below(primary) and has_rank3(primary):
        return f"{claim_prefix}_PRIMARY_RIGHT207_ANCHOR8_BELOW_RHO_RANK3_EXACT_RECURRENCE"
    if has_below(primary):
        return f"{claim_prefix}_PRIMARY_RIGHT207_ANCHOR8_BELOW_RHO_EXACT_RECURRENCE"
    if has_rank3(primary):
        return f"{claim_prefix}_PRIMARY_RIGHT207_ANCHOR8_RANK3_EXACT_RECURRENCE"
    if has_below(broad):
        return f"{claim_prefix}_BROAD_RIGHT207_SALT207_BELOW_RHO_DRIFT"
    if has_rank3(broad):
        return f"{claim_prefix}_BROAD_RIGHT207_SALT207_RANK3_DRIFT"
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
    parser.add_argument("--claim-prefix", default="P675")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P675_EXACT_BELOW_RHO_SURFACE_QUIET")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.summarize_cases(features)
    reports = [
        p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.rule_report(name, desc, pred, features, raw_summary)
        for name, desc, pred in RULES
    ]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p675_exact_below_rho_surface_recurrence_scout.v1",
        "created_at": p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.utc_now(),
        "method": "p675_exact_below_rho_surface_recurrence_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.public_feature_counts(
                features
            ),
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
            "P675 tests exact recurrence of the P674 below-rho right207/anchor8 surface.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
