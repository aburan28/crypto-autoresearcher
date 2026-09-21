#!/usr/bin/env python3
"""P673 adjacent-corridor validation for the P671 right207 row-pair shift."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p672_exact_row_pair_shift_scout as p672


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p673_order9887_adjacent_row_pair_shift_22635_22647_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p673_adjacent_row_pair_shift_source_22635_22647_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p673_adjacent_row_pair_shift_corridor_scout_22635_22647_probe.json"
TRANSFERS = tuple(range(22635, 22648))
SALT207_LEFTS = {203, 204, 205, 206}


def in_corridor(base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return f.get("transfer_index") in TRANSFERS and base(f)

    return pred


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


def anchor(anchor: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return f.get("right_anchor") == anchor and base(f)

    return pred


def right207_salt207_pair(salt_left: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p672.p671.p670.standard_row_pair(f, salt_left, 207)

    return pred


def right207_salt207(f: dict[str, Any]) -> bool:
    return any(p672.p671.p670.standard_row_pair(f, salt_left, 207) for salt_left in SALT207_LEFTS)


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p673_corridor_right207_anchor9_salt205_salt207",
        "P671 shifted surface over adjacent corridor: right207 anchor9 salt205_salt207",
        in_corridor(anchor(9, right207_salt207_pair(205))),
    ),
    (
        "p673_corridor_right207_anchor9_salt207_union",
        "Adjacent corridor right207 anchor9 salt207 sibling union",
        in_corridor(anchor(9, right207_salt207)),
    ),
    (
        "p673_corridor_right207_salt205_salt207",
        "Adjacent corridor right207 salt205_salt207 all-anchor control",
        in_corridor(right207_salt207_pair(205)),
    ),
    (
        "p673_corridor_right207_salt207_union",
        "Adjacent corridor broad right207 salt207 sibling control",
        in_corridor(right207_salt207),
    ),
    (
        "p673_corridor_right208_anchor7_salt208_union",
        "Adjacent corridor right208 anchor7 salt208 side control",
        in_corridor(anchor(7, p672.p671.p670.right208_salt208)),
    ),
    (
        "p673_corridor_right208_anchor9_salt208_union",
        "Adjacent corridor right208 anchor9 salt208 side control",
        in_corridor(anchor(9, p672.p671.p670.right208_salt208)),
    ),
    (
        "p673_corridor_right208_salt208_union",
        "Adjacent corridor broad right208 salt208 side control",
        in_corridor(p672.p671.p670.right208_salt208),
    ),
]

for salt_left in sorted(SALT207_LEFTS):
    RULES.extend(
        [
            (
                f"p673_corridor_right207_anchor9_salt{salt_left}_salt207",
                f"Adjacent corridor right207 anchor9 salt{salt_left}_salt207 split",
                in_corridor(anchor(9, right207_salt207_pair(salt_left))),
            ),
            (
                f"p673_corridor_right207_salt{salt_left}_salt207",
                f"Adjacent corridor right207 salt{salt_left}_salt207 all-anchor split",
                in_corridor(right207_salt207_pair(salt_left)),
            ),
        ]
    )

for transfer_index in TRANSFERS:
    phase = transfer_index % 12
    mod7 = transfer_index % 7
    RULES.extend(
        [
            (
                f"p673_t{transfer_index}_phase{phase}_mod7_{mod7}_right207_anchor9_salt205_salt207",
                f"Transfer {transfer_index} phase{phase}/mod7={mod7} right207 anchor9 salt205_salt207",
                at_transfer(transfer_index, phase_mod_anchor(phase, mod7, 9, right207_salt207_pair(205))),
            ),
            (
                f"p673_t{transfer_index}_phase{phase}_mod7_{mod7}_right207_anchor9_salt207_union",
                f"Transfer {transfer_index} phase{phase}/mod7={mod7} right207 anchor9 salt207 union",
                at_transfer(transfer_index, phase_mod_anchor(phase, mod7, 9, right207_salt207)),
            ),
            (
                f"p673_t{transfer_index}_phase{phase}_mod7_{mod7}_right207_salt207_union",
                f"Transfer {transfer_index} phase{phase}/mod7={mod7} broad right207 salt207 union",
                at_transfer(transfer_index, phase_mod(phase, mod7, right207_salt207)),
            ),
            (
                f"p673_t{transfer_index}_phase{phase}_mod7_{mod7}_right208_salt208_union",
                f"Transfer {transfer_index} phase{phase}/mod7={mod7} right208 salt208 side union",
                at_transfer(transfer_index, phase_mod(phase, mod7, p672.p671.p670.right208_salt208)),
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
    has_below = p672.p671.p670.p669.p668.p667.p666.p665.has_below
    has_rank3 = p672.p671.p670.p669.p668.p667.p666.p665.has_rank3
    primary = report_named(reports, "p673_corridor_right207_anchor9_salt205_salt207")
    anchor_union = report_named(reports, "p673_corridor_right207_anchor9_salt207_union")
    all_primary = report_named(reports, "p673_corridor_right207_salt205_salt207")
    broad_r207 = report_named(reports, "p673_corridor_right207_salt207_union")
    side_r208 = report_named(reports, "p673_corridor_right208_salt208_union")

    if has_below(primary) and has_rank3(primary):
        return f"{claim_prefix}_PRIMARY_SHIFT_ADJACENT_BELOW_RHO_RANK3_PERSISTENCE"
    if has_below(primary):
        return f"{claim_prefix}_PRIMARY_SHIFT_ADJACENT_BELOW_RHO_PERSISTENCE"
    if has_rank3(primary):
        return f"{claim_prefix}_PRIMARY_SHIFT_ADJACENT_RANK3_PERSISTENCE"
    if has_below(anchor_union):
        return f"{claim_prefix}_ANCHOR9_SALT207_SIBLING_BELOW_RHO_DRIFT"
    if has_below(all_primary):
        return f"{claim_prefix}_SALT205_SALT207_ALL_ANCHOR_BELOW_RHO_DRIFT"
    if has_below(broad_r207):
        return f"{claim_prefix}_BROAD_RIGHT207_SALT207_BELOW_RHO_DRIFT"
    if has_below(side_r208):
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
    parser.add_argument("--claim-prefix", default="P673")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P673_ADJACENT_ROW_PAIR_SHIFT_CORRIDOR_QUIET")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p672.p671.p670.p669.p668.p667.p666.p665.p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p672.p671.p670.p669.p668.p667.p666.p665.summarize_cases(features)
    reports = [
        p672.p671.p670.p669.p668.p667.p666.p665.rule_report(name, desc, pred, features, raw_summary)
        for name, desc, pred in RULES
    ]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p673_adjacent_row_pair_shift_corridor_scout.v1",
        "created_at": p672.p671.p670.p669.p668.p667.p666.p665.utc_now(),
        "method": "p673_adjacent_row_pair_shift_corridor_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p672.p671.p670.p669.p668.p667.p666.p665.public_feature_counts(features),
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
            "P673 tests adjacent drift of the P671 row-pair-shift surface.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
