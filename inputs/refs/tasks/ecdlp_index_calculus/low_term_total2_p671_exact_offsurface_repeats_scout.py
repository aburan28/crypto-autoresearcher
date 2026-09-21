#!/usr/bin/env python3
"""P671 exact-repeat validation for P669 off-surface phase2/phase11 positives."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p670_offsurface_phase2_phase11_corridor_scout as p670


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p671_order9887_exact_offsurface_repeats_22634_22643_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p671_exact_offsurface_repeats_source_22634_22643_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p671_exact_offsurface_repeats_scout_22634_22643_probe.json"
T_PHASE2 = 22634
T_PHASE11 = 22643


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


def exact_phase2(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_PHASE2, phase_mod(2, 3, base))


def exact_phase2_anchor(anchor: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_PHASE2, phase_mod_anchor(2, 3, anchor, base))


def exact_phase11(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_PHASE11, phase_mod(11, 5, base))


def exact_phase11_anchor(anchor: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_PHASE11, phase_mod_anchor(11, 5, anchor, base))


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p671_t22634_phase2_mod7_3_right208_anchor7_salt208_union",
        "P669 transfer-22550 +84: phase2/mod7=3 right208 anchor7 salt208 union",
        exact_phase2_anchor(7, p670.right208_salt208),
    ),
    (
        "p671_t22634_phase2_mod7_3_right208_salt208_union",
        "P669 transfer-22550 +84: phase2/mod7=3 right208 salt208 all-anchor control",
        exact_phase2(p670.right208_salt208),
    ),
    (
        "p671_t22634_phase2_mod7_3_right207_anchor9_salt206_salt207",
        "P669 transfer-22550 +84: phase2/mod7=3 right207 anchor9 salt206_salt207",
        exact_phase2_anchor(9, p670.right207_salt206_salt207),
    ),
    (
        "p671_t22643_phase11_mod7_5_right208_anchor9_salt203_salt208",
        "P669 transfer-22559 +84: phase11/mod7=5 right208 anchor9 salt203_salt208",
        exact_phase11_anchor(9, p670.right208_salt208_pair(203)),
    ),
    (
        "p671_t22643_phase11_mod7_5_right208_salt208_union",
        "P669 transfer-22559 +84: phase11/mod7=5 right208 salt208 all-anchor control",
        exact_phase11(p670.right208_salt208),
    ),
    (
        "p671_all_exact_right208_salt208_union",
        "All exact-repeat transfers broad right208 salt208 union",
        lambda f: (
            (f.get("transfer_index") == T_PHASE2 and f.get("transfer_mod12") == 2 and f.get("transfer_mod7") == 3)
            or (f.get("transfer_index") == T_PHASE11 and f.get("transfer_mod12") == 11 and f.get("transfer_mod7") == 5)
        )
        and p670.right208_salt208(f),
    ),
]

for salt_left in sorted(p670.SALT208_LEFTS):
    RULES.extend(
        [
            (
                f"p671_t22634_phase2_mod7_3_right208_anchor7_salt{salt_left}_salt208",
                f"P669 transfer-22550 +84 right208 anchor7 salt{salt_left}_salt208 split",
                exact_phase2_anchor(7, p670.right208_salt208_pair(salt_left)),
            ),
            (
                f"p671_t22634_phase2_mod7_3_right208_salt{salt_left}_salt208",
                f"P669 transfer-22550 +84 right208 salt{salt_left}_salt208 all-anchor split",
                exact_phase2(p670.right208_salt208_pair(salt_left)),
            ),
            (
                f"p671_t22643_phase11_mod7_5_right208_anchor9_salt{salt_left}_salt208",
                f"P669 transfer-22559 +84 right208 anchor9 salt{salt_left}_salt208 split",
                exact_phase11_anchor(9, p670.right208_salt208_pair(salt_left)),
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
    has_below = p670.p669.p668.p667.p666.p665.has_below
    has_rank3 = p670.p669.p668.p667.p666.p665.has_rank3
    t22634_anchor7 = report_named(reports, "p671_t22634_phase2_mod7_3_right208_anchor7_salt208_union")
    t22634_r207 = report_named(reports, "p671_t22634_phase2_mod7_3_right207_anchor9_salt206_salt207")
    t22643_anchor9 = report_named(reports, "p671_t22643_phase11_mod7_5_right208_anchor9_salt203_salt208")
    broad = report_named(reports, "p671_all_exact_right208_salt208_union")

    if has_below(t22634_anchor7) and has_rank3(t22634_anchor7):
        return f"{claim_prefix}_T22634_RIGHT208_ANCHOR7_BELOW_RHO_RANK3_EXACT_RECURRENCE"
    if has_below(t22634_anchor7):
        return f"{claim_prefix}_T22634_RIGHT208_ANCHOR7_BELOW_RHO_EXACT_RECURRENCE"
    if has_below(t22634_r207):
        return f"{claim_prefix}_T22634_RIGHT207_ANCHOR9_BELOW_RHO_EXACT_RECURRENCE"
    if has_below(t22643_anchor9):
        return f"{claim_prefix}_T22643_RIGHT208_ANCHOR9_BELOW_RHO_EXACT_RECURRENCE"
    if has_rank3(t22634_anchor7):
        return f"{claim_prefix}_T22634_RIGHT208_ANCHOR7_RANK3_EXACT_RECURRENCE"
    if has_below(broad):
        return f"{claim_prefix}_BROAD_EXACT_RIGHT208_SALT208_BELOW_RHO_DRIFT"
    if has_rank3(broad):
        return f"{claim_prefix}_BROAD_EXACT_RIGHT208_SALT208_RANK3_DRIFT"
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
    parser.add_argument("--claim-prefix", default="P671")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P671_EXACT_OFFSURFACE_REPEATS_QUIET")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p670.p669.p668.p667.p666.p665.p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p670.p669.p668.p667.p666.p665.summarize_cases(features)
    reports = [p670.p669.p668.p667.p666.p665.rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p671_exact_offsurface_repeats_scout.v1",
        "created_at": p670.p669.p668.p667.p666.p665.utc_now(),
        "method": "p671_exact_offsurface_repeats_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p670.p669.p668.p667.p666.p665.public_feature_counts(features),
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
            "P671 tests exact recurrence for P669's off-surface phase2/phase11 material.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
