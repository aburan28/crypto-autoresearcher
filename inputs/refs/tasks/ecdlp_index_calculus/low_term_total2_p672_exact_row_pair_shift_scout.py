#!/usr/bin/env python3
"""P672 exact-repeat validation for the P671 right207 row-pair shift."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p671_exact_offsurface_repeats_scout as p671


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p672_order9887_exact_row_pair_shift_22718_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p672_exact_row_pair_shift_source_22718_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p672_exact_row_pair_shift_scout_22718_probe.json"
T_SHIFT = 22718
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


def exact_phase2(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_SHIFT, phase_mod(2, 3, base))


def exact_phase2_anchor(anchor: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(T_SHIFT, phase_mod_anchor(2, 3, anchor, base))


def right207_salt207_pair(salt_left: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p671.p670.standard_row_pair(f, salt_left, 207)

    return pred


def right207_salt207(f: dict[str, Any]) -> bool:
    return any(p671.p670.standard_row_pair(f, salt_left, 207) for salt_left in SALT207_LEFTS)


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p672_t22718_phase2_mod7_3_right207_anchor9_salt205_salt207",
        "P671 transfer-22634 +84: phase2/mod7=3 right207 anchor9 salt205_salt207 primary shift",
        exact_phase2_anchor(9, right207_salt207_pair(205)),
    ),
    (
        "p672_t22718_phase2_mod7_3_right207_anchor9_salt207_union",
        "P671 transfer-22634 +84: phase2/mod7=3 right207 anchor9 salt207 sibling union",
        exact_phase2_anchor(9, right207_salt207),
    ),
    (
        "p672_t22718_phase2_mod7_3_right207_salt205_salt207",
        "P671 transfer-22634 +84: phase2/mod7=3 right207 salt205_salt207 all-anchor control",
        exact_phase2(right207_salt207_pair(205)),
    ),
    (
        "p672_t22718_phase2_mod7_3_right207_salt207_union",
        "P671 transfer-22634 +84: phase2/mod7=3 right207 salt207 all-anchor sibling control",
        exact_phase2(right207_salt207),
    ),
    (
        "p672_t22718_phase2_mod7_3_right208_anchor7_salt208_union",
        "P669/P671 side control: phase2/mod7=3 right208 anchor7 salt208 union",
        exact_phase2_anchor(7, p671.p670.right208_salt208),
    ),
    (
        "p672_t22718_phase2_mod7_3_right208_anchor9_salt208_union",
        "P671 side control: phase2/mod7=3 right208 anchor9 salt208 union",
        exact_phase2_anchor(9, p671.p670.right208_salt208),
    ),
    (
        "p672_t22718_phase2_mod7_3_right208_salt208_union",
        "P671 side control: phase2/mod7=3 right208 salt208 all-anchor union",
        exact_phase2(p671.p670.right208_salt208),
    ),
]

for salt_left in sorted(SALT207_LEFTS):
    RULES.extend(
        [
            (
                f"p672_t22718_phase2_mod7_3_right207_anchor9_salt{salt_left}_salt207",
                f"P672 right207 anchor9 salt{salt_left}_salt207 sibling split",
                exact_phase2_anchor(9, right207_salt207_pair(salt_left)),
            ),
            (
                f"p672_t22718_phase2_mod7_3_right207_salt{salt_left}_salt207",
                f"P672 right207 salt{salt_left}_salt207 all-anchor split",
                exact_phase2(right207_salt207_pair(salt_left)),
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
    has_below = p671.p670.p669.p668.p667.p666.p665.has_below
    has_rank3 = p671.p670.p669.p668.p667.p666.p665.has_rank3
    primary = report_named(reports, "p672_t22718_phase2_mod7_3_right207_anchor9_salt205_salt207")
    anchor_union = report_named(reports, "p672_t22718_phase2_mod7_3_right207_anchor9_salt207_union")
    all_primary = report_named(reports, "p672_t22718_phase2_mod7_3_right207_salt205_salt207")
    side_right208 = report_named(reports, "p672_t22718_phase2_mod7_3_right208_salt208_union")

    if has_below(primary) and has_rank3(primary):
        return f"{claim_prefix}_PRIMARY_ROW_PAIR_SHIFT_BELOW_RHO_RANK3_EXACT_RECURRENCE"
    if has_below(primary):
        return f"{claim_prefix}_PRIMARY_ROW_PAIR_SHIFT_BELOW_RHO_EXACT_RECURRENCE"
    if has_rank3(primary):
        return f"{claim_prefix}_PRIMARY_ROW_PAIR_SHIFT_RANK3_EXACT_RECURRENCE"
    if has_below(anchor_union):
        return f"{claim_prefix}_ANCHOR9_SALT207_SIBLING_BELOW_RHO_RECURRENCE"
    if has_below(all_primary):
        return f"{claim_prefix}_SALT205_SALT207_ALL_ANCHOR_BELOW_RHO_DRIFT"
    if has_below(side_right208):
        return f"{claim_prefix}_RIGHT208_SALT208_SIDE_BELOW_RHO_DRIFT"
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
    parser.add_argument("--claim-prefix", default="P672")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P672_EXACT_ROW_PAIR_SHIFT_QUIET")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p671.p670.p669.p668.p667.p666.p665.p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p671.p670.p669.p668.p667.p666.p665.summarize_cases(features)
    reports = [
        p671.p670.p669.p668.p667.p666.p665.rule_report(name, desc, pred, features, raw_summary)
        for name, desc, pred in RULES
    ]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p672_exact_row_pair_shift_scout.v1",
        "created_at": p671.p670.p669.p668.p667.p666.p665.utc_now(),
        "method": "p672_exact_row_pair_shift_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p671.p670.p669.p668.p667.p666.p665.public_feature_counts(features),
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
            "P672 tests exact recurrence of the P671 row-pair-shift surface.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
