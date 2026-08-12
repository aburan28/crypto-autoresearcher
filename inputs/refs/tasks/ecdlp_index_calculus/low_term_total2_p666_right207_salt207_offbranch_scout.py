#!/usr/bin/env python3
"""P666 adjacent validation for P665's right207/salt207 off-branch signal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p665_phase0_salt204_drift_scout as p665


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p666_order9887_right207_salt207_offbranch_22395_22407_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p666_right207_salt207_offbranch_source_22395_22407_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p666_right207_salt207_offbranch_scout_22395_22407_probe.json"
ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}
SALT207_LEFTS = {203, 205, 206}


def right207_salt207(f: dict[str, Any]) -> bool:
    return any(p665.standard_row_pair(f, salt_left, 207) for salt_left in SALT207_LEFTS)


def salt207_row_pair(salt_left: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p665.standard_row_pair(f, salt_left, 207)

    return pred


def phase5_mod7_6_anchor6_union(f: dict[str, Any]) -> bool:
    return (
        right207_salt207(f)
        and f.get("transfer_mod12") == 5
        and f.get("transfer_mod7") == 6
        and f.get("right_anchor") == 6
    )


def phase5_anchor6_union(f: dict[str, Any]) -> bool:
    return right207_salt207(f) and f.get("transfer_mod12") == 5 and f.get("right_anchor") == 6


def mod7_6_anchor6_union(f: dict[str, Any]) -> bool:
    return right207_salt207(f) and f.get("transfer_mod7") == 6 and f.get("right_anchor") == 6


def broad_anchor6_union(f: dict[str, Any]) -> bool:
    return right207_salt207(f) and f.get("right_anchor") == 6


def phase10_mod7_4_union(f: dict[str, Any]) -> bool:
    return right207_salt207(f) and f.get("transfer_mod12") == 10 and f.get("transfer_mod7") == 4


def phase10_union(f: dict[str, Any]) -> bool:
    return right207_salt207(f) and f.get("transfer_mod12") == 10


def mod7_4_union(f: dict[str, Any]) -> bool:
    return right207_salt207(f) and f.get("transfer_mod7") == 4


def phase_mod_anchor_pred(phase: int, mod7: int, anchor: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return (
            right207_salt207(f)
            and f.get("transfer_mod12") == phase
            and f.get("transfer_mod7") == mod7
            and f.get("right_anchor") == anchor
        )

    return pred


def phase_mod_row_pair_pred(phase: int, mod7: int, salt_left: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return salt207_row_pair(salt_left)(f) and f.get("transfer_mod12") == phase and f.get("transfer_mod7") == mod7

    return pred


def phase_mod_anchor_row_pair_pred(
    phase: int, mod7: int, anchor: int, salt_left: int
) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return (
            salt207_row_pair(salt_left)(f)
            and f.get("transfer_mod12") == phase
            and f.get("transfer_mod7") == mod7
            and f.get("right_anchor") == anchor
        )

    return pred


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p666_phase5_mod7_6_right207_anchor6_salt207_union",
        "P665 transfer-22385 phase5/mod7=6 right207 anchor6 salt207 union",
        phase5_mod7_6_anchor6_union,
    ),
    (
        "p666_phase5_right207_anchor6_salt207_union",
        "P665 phase5 right207 anchor6 salt207 union",
        phase5_anchor6_union,
    ),
    (
        "p666_mod7_6_right207_anchor6_salt207_union",
        "P665 same-mod7=6 right207 anchor6 salt207 union",
        mod7_6_anchor6_union,
    ),
    (
        "p666_broad_right207_anchor6_salt207_union",
        "P665 broad right207 anchor6 salt207 union",
        broad_anchor6_union,
    ),
    (
        "p666_phase10_mod7_4_right207_salt207_union",
        "P665 transfer-22390 phase10/mod7=4 right207 salt207 union",
        phase10_mod7_4_union,
    ),
    (
        "p666_phase10_right207_salt207_union",
        "P665 phase10 right207 salt207 union",
        phase10_union,
    ),
    (
        "p666_mod7_4_right207_salt207_union",
        "P665 same-mod7=4 right207 salt207 union",
        mod7_4_union,
    ),
    (
        "p666_broad_right207_salt207_union",
        "P665 broad right207 salt207 union",
        right207_salt207,
    ),
]

for salt_left in sorted(SALT207_LEFTS):
    RULES.extend(
        [
            (
                f"p666_phase5_mod7_6_right207_anchor6_salt{salt_left}_salt207",
                f"P665 phase5/mod7=6 right207 anchor6 salt{salt_left}_salt207 split",
                phase_mod_anchor_row_pair_pred(5, 6, 6, salt_left),
            ),
            (
                f"p666_phase10_mod7_4_right207_salt{salt_left}_salt207",
                f"P665 phase10/mod7=4 right207 salt{salt_left}_salt207 row-pair split",
                phase_mod_row_pair_pred(10, 4, salt_left),
            ),
            (
                f"p666_broad_right207_salt{salt_left}_salt207",
                f"P665 broad right207 salt{salt_left}_salt207 row-pair split",
                salt207_row_pair(salt_left),
            ),
        ]
    )

for anchor in sorted(ANCHORS):
    RULES.append(
        (
            f"p666_phase10_mod7_4_right207_anchor{anchor}_salt207_union",
            f"P665 phase10/mod7=4 right207 anchor {anchor} salt207 split",
            phase_mod_anchor_pred(10, 4, anchor),
        )
    )
    for salt_left in sorted(SALT207_LEFTS):
        RULES.append(
            (
                f"p666_phase10_mod7_4_right207_anchor{anchor}_salt{salt_left}_salt207",
                f"P665 phase10/mod7=4 right207 anchor {anchor} salt{salt_left}_salt207 split",
                phase_mod_anchor_row_pair_pred(10, 4, anchor, salt_left),
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
    phase5 = report_named(reports, "p666_phase5_mod7_6_right207_anchor6_salt207_union")
    phase10 = report_named(reports, "p666_phase10_mod7_4_right207_salt207_union")
    broad = report_named(reports, "p666_broad_right207_salt207_union")

    if p665.has_below(phase10) and p665.has_rank3(phase10):
        return f"{claim_prefix}_PHASE10_MOD7_4_RIGHT207_SALT207_BELOW_RHO_RANK3_PERSISTENCE"
    if p665.has_below(phase10):
        return f"{claim_prefix}_PHASE10_MOD7_4_RIGHT207_SALT207_BELOW_RHO_PERSISTENCE"
    if p665.has_rank3(phase10):
        return f"{claim_prefix}_PHASE10_MOD7_4_RIGHT207_SALT207_RANK3_PERSISTENCE"
    if p665.has_below(phase5):
        return f"{claim_prefix}_PHASE5_MOD7_6_RIGHT207_ANCHOR6_SALT207_BELOW_RHO_PERSISTENCE"
    if p665.has_rank3(phase5):
        return f"{claim_prefix}_PHASE5_MOD7_6_RIGHT207_ANCHOR6_SALT207_RANK3_PERSISTENCE"
    if p665.has_below(broad):
        return f"{claim_prefix}_BROAD_RIGHT207_SALT207_BELOW_RHO_DRIFT"
    if p665.has_rank3(broad):
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
    parser.add_argument("--claim-prefix", default="P666")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P666_RIGHT207_SALT207_ADJACENT_QUIET_BLOCK")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p665.p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p665.summarize_cases(features)
    reports = [p665.rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p666_right207_salt207_offbranch_scout.v1",
        "created_at": p665.utc_now(),
        "method": "p666_right207_salt207_offbranch_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p665.public_feature_counts(features),
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
            "P666 tests adjacent persistence and public-feature drift for P665's right207/salt207 off-branch signal.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
