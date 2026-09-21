#!/usr/bin/env python3
"""P667 adjacent validation for the right207/salt207 drift-family model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p666_right207_salt207_offbranch_scout as p666


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p667_order9887_right207_salt207_drift_family_22408_22420_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p667_right207_salt207_drift_family_source_22408_22420_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p667_right207_salt207_drift_family_scout_22408_22420_probe.json"


def phase_mod_union(phase: int, mod7: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p666.right207_salt207(f) and f.get("transfer_mod12") == phase and f.get("transfer_mod7") == mod7

    return pred


def phase_anchor_union(phase: int, anchor: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p666.right207_salt207(f) and f.get("transfer_mod12") == phase and f.get("right_anchor") == anchor

    return pred


def mod_anchor_union(mod7: int, anchor: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p666.right207_salt207(f) and f.get("transfer_mod7") == mod7 and f.get("right_anchor") == anchor

    return pred


def broad_anchor_union(anchor: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p666.right207_salt207(f) and f.get("right_anchor") == anchor

    return pred


def phase_mod_anchor_pred(phase: int, mod7: int, anchor: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return (
            p666.right207_salt207(f)
            and f.get("transfer_mod12") == phase
            and f.get("transfer_mod7") == mod7
            and f.get("right_anchor") == anchor
        )

    return pred


def phase_mod_row_pair_pred(phase: int, mod7: int, salt_left: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p666.salt207_row_pair(salt_left)(f) and f.get("transfer_mod12") == phase and f.get("transfer_mod7") == mod7

    return pred


def phase_mod_anchor_row_pair_pred(
    phase: int, mod7: int, anchor: int, salt_left: int
) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return (
            p666.salt207_row_pair(salt_left)(f)
            and f.get("transfer_mod12") == phase
            and f.get("transfer_mod7") == mod7
            and f.get("right_anchor") == anchor
        )

    return pred


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p667_phase11_mod7_3_right207_anchor6_salt207_union",
        "P666 phase11/mod7=3 right207 anchor6 salt207 surface",
        phase_mod_anchor_pred(11, 3, 6),
    ),
    (
        "p667_phase11_mod7_3_right207_salt207_union",
        "P666 phase11/mod7=3 right207 salt207 all-anchor surface",
        phase_mod_union(11, 3),
    ),
    (
        "p667_phase11_right207_anchor6_salt207_union",
        "P666 phase11 right207 anchor6 salt207 phase-only control",
        phase_anchor_union(11, 6),
    ),
    (
        "p667_mod7_3_right207_anchor6_salt207_union",
        "P666 same-mod7=3 right207 anchor6 salt207 control",
        mod_anchor_union(3, 6),
    ),
    (
        "p667_broad_right207_anchor6_salt207_union",
        "P666 broad right207 anchor6 salt207 control",
        broad_anchor_union(6),
    ),
    (
        "p667_phase3_mod7_0_right207_anchor12_salt207_union",
        "P666 phase3/mod7=0 right207 anchor12 salt207 surface",
        phase_mod_anchor_pred(3, 0, 12),
    ),
    (
        "p667_phase3_mod7_0_right207_salt207_union",
        "P666 phase3/mod7=0 right207 salt207 all-anchor surface",
        phase_mod_union(3, 0),
    ),
    (
        "p667_phase3_right207_anchor12_salt207_union",
        "P666 phase3 right207 anchor12 salt207 phase-only control",
        phase_anchor_union(3, 12),
    ),
    (
        "p667_mod7_0_right207_anchor12_salt207_union",
        "P666 same-mod7=0 right207 anchor12 salt207 control",
        mod_anchor_union(0, 12),
    ),
    (
        "p667_broad_right207_anchor12_salt207_union",
        "P666 broad right207 anchor12 salt207 control",
        broad_anchor_union(12),
    ),
    (
        "p667_broad_right207_salt207_union",
        "P666/P667 broad right207 salt207 drift-family control",
        p666.right207_salt207,
    ),
]

for salt_left in sorted(p666.SALT207_LEFTS):
    RULES.extend(
        [
            (
                f"p667_phase11_mod7_3_right207_anchor6_salt{salt_left}_salt207",
                f"P666 phase11/mod7=3 right207 anchor6 salt{salt_left}_salt207 split",
                phase_mod_anchor_row_pair_pred(11, 3, 6, salt_left),
            ),
            (
                f"p667_phase3_mod7_0_right207_anchor12_salt{salt_left}_salt207",
                f"P666 phase3/mod7=0 right207 anchor12 salt{salt_left}_salt207 split",
                phase_mod_anchor_row_pair_pred(3, 0, 12, salt_left),
            ),
            (
                f"p667_broad_right207_salt{salt_left}_salt207",
                f"P666/P667 broad right207 salt{salt_left}_salt207 row-pair split",
                p666.salt207_row_pair(salt_left),
            ),
        ]
    )

for anchor in sorted(p666.ANCHORS):
    RULES.extend(
        [
            (
                f"p667_phase11_mod7_3_right207_anchor{anchor}_salt207_union",
                f"P667 phase11/mod7=3 right207 anchor {anchor} salt207 split",
                phase_mod_anchor_pred(11, 3, anchor),
            ),
            (
                f"p667_phase3_mod7_0_right207_anchor{anchor}_salt207_union",
                f"P667 phase3/mod7=0 right207 anchor {anchor} salt207 split",
                phase_mod_anchor_pred(3, 0, anchor),
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
    phase11_anchor6 = report_named(reports, "p667_phase11_mod7_3_right207_anchor6_salt207_union")
    phase11_all = report_named(reports, "p667_phase11_mod7_3_right207_salt207_union")
    phase3_anchor12 = report_named(reports, "p667_phase3_mod7_0_right207_anchor12_salt207_union")
    phase3_all = report_named(reports, "p667_phase3_mod7_0_right207_salt207_union")
    broad = report_named(reports, "p667_broad_right207_salt207_union")

    if p666.p665.has_below(phase11_anchor6) and p666.p665.has_rank3(phase11_anchor6):
        return f"{claim_prefix}_PHASE11_MOD7_3_RIGHT207_ANCHOR6_BELOW_RHO_RANK3_PERSISTENCE"
    if p666.p665.has_below(phase3_anchor12) and p666.p665.has_rank3(phase3_anchor12):
        return f"{claim_prefix}_PHASE3_MOD7_0_RIGHT207_ANCHOR12_BELOW_RHO_RANK3_PERSISTENCE"
    if p666.p665.has_below(phase11_anchor6):
        return f"{claim_prefix}_PHASE11_MOD7_3_RIGHT207_ANCHOR6_BELOW_RHO_PERSISTENCE"
    if p666.p665.has_below(phase3_anchor12):
        return f"{claim_prefix}_PHASE3_MOD7_0_RIGHT207_ANCHOR12_BELOW_RHO_PERSISTENCE"
    if p666.p665.has_rank3(phase11_anchor6):
        return f"{claim_prefix}_PHASE11_MOD7_3_RIGHT207_ANCHOR6_RANK3_PERSISTENCE"
    if p666.p665.has_rank3(phase3_anchor12):
        return f"{claim_prefix}_PHASE3_MOD7_0_RIGHT207_ANCHOR12_RANK3_PERSISTENCE"
    if p666.p665.has_below(phase11_all):
        return f"{claim_prefix}_PHASE11_MOD7_3_RIGHT207_SALT207_BELOW_RHO_DRIFT"
    if p666.p665.has_below(phase3_all):
        return f"{claim_prefix}_PHASE3_MOD7_0_RIGHT207_SALT207_BELOW_RHO_DRIFT"
    if p666.p665.has_rank3(phase11_all):
        return f"{claim_prefix}_PHASE11_MOD7_3_RIGHT207_SALT207_RANK3_DRIFT"
    if p666.p665.has_rank3(phase3_all):
        return f"{claim_prefix}_PHASE3_MOD7_0_RIGHT207_SALT207_RANK3_DRIFT"
    if p666.p665.has_below(broad):
        return f"{claim_prefix}_BROAD_RIGHT207_SALT207_BELOW_RHO_DRIFT"
    if p666.p665.has_rank3(broad):
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
    parser.add_argument("--claim-prefix", default="P667")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P667_RIGHT207_SALT207_DRIFT_FAMILY_QUIET_BLOCK")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p666.p665.p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p666.p665.summarize_cases(features)
    reports = [p666.p665.rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p667_right207_salt207_drift_family_scout.v1",
        "created_at": p666.p665.utc_now(),
        "method": "p667_right207_salt207_drift_family_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p666.p665.public_feature_counts(features),
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
            "P667 tests adjacent persistence and public-feature drift for the right207/salt207 family.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
