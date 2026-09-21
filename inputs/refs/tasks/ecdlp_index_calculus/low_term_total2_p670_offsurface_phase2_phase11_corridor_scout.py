#!/usr/bin/env python3
"""P670 adjacent validation for P669 off-surface phase2/phase11 material."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p669_phase5_mod7_6_second_repeat_scout as p669


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p670_order9887_offsurface_phase2_phase11_corridor_22561_22573_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p670_offsurface_phase2_phase11_corridor_source_22561_22573_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p670_offsurface_phase2_phase11_corridor_scout_22561_22573_probe.json"
ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}
SALT208_LEFTS = {203, 204, 205, 206}


def standard_row_pair(f: dict[str, Any], salt_left: int, salt_right: int) -> bool:
    return p669.p668.p667.p666.p665.standard_row_pair(f, salt_left, salt_right)


def right207_salt206_salt207(f: dict[str, Any]) -> bool:
    return standard_row_pair(f, 206, 207)


def right208_salt208(f: dict[str, Any]) -> bool:
    return any(standard_row_pair(f, salt_left, 208) for salt_left in SALT208_LEFTS)


def right208_salt208_pair(salt_left: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return standard_row_pair(f, salt_left, 208)

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


def broad_anchor(anchor: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return f.get("right_anchor") == anchor and base(f)

    return pred


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p670_phase2_mod7_3_right208_anchor7_salt208_union",
        "P669 transfer-22550 phase2/mod7=3 right208 anchor7 salt208 union",
        phase_mod_anchor(2, 3, 7, right208_salt208),
    ),
    (
        "p670_phase2_mod7_3_right208_salt208_union",
        "P669 transfer-22550 phase2/mod7=3 right208 salt208 all-anchor control",
        phase_mod(2, 3, right208_salt208),
    ),
    (
        "p670_broad_right208_anchor7_salt208_union",
        "P669 broad right208 anchor7 salt208 control",
        broad_anchor(7, right208_salt208),
    ),
    (
        "p670_phase2_mod7_3_right207_anchor9_salt206_salt207",
        "P669 transfer-22550 phase2/mod7=3 right207 anchor9 salt206_salt207",
        phase_mod_anchor(2, 3, 9, right207_salt206_salt207),
    ),
    (
        "p670_broad_right207_anchor9_salt206_salt207",
        "P669 broad right207 anchor9 salt206_salt207 control",
        broad_anchor(9, right207_salt206_salt207),
    ),
    (
        "p670_phase11_mod7_5_right208_anchor9_salt203_salt208",
        "P669 transfer-22559 phase11/mod7=5 right208 anchor9 salt203_salt208",
        phase_mod_anchor(11, 5, 9, right208_salt208_pair(203)),
    ),
    (
        "p670_phase11_mod7_5_right208_salt208_union",
        "P669 transfer-22559 phase11/mod7=5 right208 salt208 all-anchor control",
        phase_mod(11, 5, right208_salt208),
    ),
    (
        "p670_broad_right208_anchor9_salt208_union",
        "P669 broad right208 anchor9 salt208 control",
        broad_anchor(9, right208_salt208),
    ),
    (
        "p670_broad_right208_salt208_union",
        "P669 broad right208 salt208 union control",
        right208_salt208,
    ),
]

for salt_left in sorted(SALT208_LEFTS):
    RULES.extend(
        [
            (
                f"p670_phase2_mod7_3_right208_anchor7_salt{salt_left}_salt208",
                f"P669 phase2/mod7=3 right208 anchor7 salt{salt_left}_salt208 split",
                phase_mod_anchor(2, 3, 7, right208_salt208_pair(salt_left)),
            ),
            (
                f"p670_phase2_mod7_3_right208_salt{salt_left}_salt208",
                f"P669 phase2/mod7=3 right208 salt{salt_left}_salt208 all-anchor split",
                phase_mod(2, 3, right208_salt208_pair(salt_left)),
            ),
            (
                f"p670_phase11_mod7_5_right208_anchor9_salt{salt_left}_salt208",
                f"P669 phase11/mod7=5 right208 anchor9 salt{salt_left}_salt208 split",
                phase_mod_anchor(11, 5, 9, right208_salt208_pair(salt_left)),
            ),
            (
                f"p670_broad_right208_salt{salt_left}_salt208",
                f"P669 broad right208 salt{salt_left}_salt208 split",
                right208_salt208_pair(salt_left),
            ),
        ]
    )

for anchor in sorted(ANCHORS):
    RULES.extend(
        [
            (
                f"p670_phase2_mod7_3_right208_anchor{anchor}_salt208_union",
                f"P670 phase2/mod7=3 right208 anchor {anchor} salt208 split",
                phase_mod_anchor(2, 3, anchor, right208_salt208),
            ),
            (
                f"p670_phase11_mod7_5_right208_anchor{anchor}_salt208_union",
                f"P670 phase11/mod7=5 right208 anchor {anchor} salt208 split",
                phase_mod_anchor(11, 5, anchor, right208_salt208),
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
    has_below = p669.p668.p667.p666.p665.has_below
    has_rank3 = p669.p668.p667.p666.p665.has_rank3
    phase2_r208_anchor7 = report_named(reports, "p670_phase2_mod7_3_right208_anchor7_salt208_union")
    phase2_r207_anchor9 = report_named(reports, "p670_phase2_mod7_3_right207_anchor9_salt206_salt207")
    phase11_r208_anchor9 = report_named(reports, "p670_phase11_mod7_5_right208_anchor9_salt203_salt208")
    broad_r208 = report_named(reports, "p670_broad_right208_salt208_union")

    if has_below(phase2_r208_anchor7) and has_rank3(phase2_r208_anchor7):
        return f"{claim_prefix}_PHASE2_MOD7_3_RIGHT208_ANCHOR7_BELOW_RHO_RANK3_PERSISTENCE"
    if has_below(phase2_r208_anchor7):
        return f"{claim_prefix}_PHASE2_MOD7_3_RIGHT208_ANCHOR7_BELOW_RHO_PERSISTENCE"
    if has_below(phase2_r207_anchor9):
        return f"{claim_prefix}_PHASE2_MOD7_3_RIGHT207_ANCHOR9_BELOW_RHO_PERSISTENCE"
    if has_below(phase11_r208_anchor9):
        return f"{claim_prefix}_PHASE11_MOD7_5_RIGHT208_ANCHOR9_BELOW_RHO_PERSISTENCE"
    if has_rank3(phase2_r208_anchor7):
        return f"{claim_prefix}_PHASE2_MOD7_3_RIGHT208_ANCHOR7_RANK3_PERSISTENCE"
    if has_below(broad_r208):
        return f"{claim_prefix}_BROAD_RIGHT208_SALT208_BELOW_RHO_DRIFT"
    if has_rank3(broad_r208):
        return f"{claim_prefix}_BROAD_RIGHT208_SALT208_RANK3_DRIFT"
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
    parser.add_argument("--claim-prefix", default="P670")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P670_OFFSURFACE_PHASE2_PHASE11_CORRIDOR_QUIET")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p669.p668.p667.p666.p665.p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p669.p668.p667.p666.p665.summarize_cases(features)
    reports = [p669.p668.p667.p666.p665.rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p670_offsurface_phase2_phase11_corridor_scout.v1",
        "created_at": p669.p668.p667.p666.p665.utc_now(),
        "method": "p670_offsurface_phase2_phase11_corridor_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p669.p668.p667.p666.p665.public_feature_counts(features),
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
            "P670 tests adjacent persistence for P669's off-surface phase2/phase11 material.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
