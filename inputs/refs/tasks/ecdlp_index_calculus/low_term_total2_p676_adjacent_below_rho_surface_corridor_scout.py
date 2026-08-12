#!/usr/bin/env python3
"""P676 adjacent-corridor validation for the P674 below-rho right207 surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p675_exact_below_rho_surface_recurrence_scout as p675


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p676_order9887_adjacent_below_rho_surface_22724_22736_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p676_adjacent_below_rho_surface_source_22724_22736_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p676_adjacent_below_rho_surface_corridor_scout_22724_22736_probe.json"
TRANSFERS = tuple(range(22724, 22737))
ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}
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


def anchor(anchor_value: int, base: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return f.get("right_anchor") == anchor_value and base(f)

    return pred


def row_pair(salt_left: int, salt_right: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p675.p674.p673.p672.p671.p670.standard_row_pair(f, salt_left, salt_right)

    return pred


def right207_salt207_pair(salt_left: int) -> Callable[[dict[str, Any]], bool]:
    return row_pair(salt_left, 207)


def right207_salt207(f: dict[str, Any]) -> bool:
    return any(p675.p674.p673.p672.p671.p670.standard_row_pair(f, salt_left, 207) for salt_left in SALT207_LEFTS)


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p676_corridor_right207_anchor8_salt207_union",
        "P674 adjacent corridor: right207 anchor8 salt207 union",
        in_corridor(anchor(8, right207_salt207)),
    ),
    (
        "p676_corridor_right207_salt207_union",
        "P674 adjacent corridor: broad right207 salt207 union",
        in_corridor(right207_salt207),
    ),
]

for salt_left in sorted(SALT207_LEFTS):
    RULES.extend(
        [
            (
                f"p676_corridor_right207_anchor8_salt{salt_left}_salt207",
                f"P676 corridor right207 anchor8 salt{salt_left}_salt207 split",
                in_corridor(anchor(8, right207_salt207_pair(salt_left))),
            ),
            (
                f"p676_corridor_right207_salt{salt_left}_salt207",
                f"P676 corridor right207 salt{salt_left}_salt207 all-anchor split",
                in_corridor(right207_salt207_pair(salt_left)),
            ),
        ]
    )

for anchor_value in sorted(ANCHORS):
    RULES.append(
        (
            f"p676_corridor_right207_anchor{anchor_value}_salt207_union",
            f"P676 corridor right207 anchor{anchor_value} salt207 sibling-anchor split",
            in_corridor(anchor(anchor_value, right207_salt207)),
        )
    )

for transfer_index in TRANSFERS:
    phase = transfer_index % 12
    mod7 = transfer_index % 7
    RULES.extend(
        [
            (
                f"p676_t{transfer_index}_phase{phase}_mod7_{mod7}_right207_anchor8_salt207_union",
                f"Transfer {transfer_index} phase{phase}/mod7={mod7} right207 anchor8 salt207 union",
                at_transfer(transfer_index, phase_mod_anchor(phase, mod7, 8, right207_salt207)),
            ),
            (
                f"p676_t{transfer_index}_phase{phase}_mod7_{mod7}_right207_salt207_union",
                f"Transfer {transfer_index} phase{phase}/mod7={mod7} broad right207 salt207 union",
                at_transfer(transfer_index, phase_mod(phase, mod7, right207_salt207)),
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
    has_below = p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.has_below
    has_rank3 = p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.has_rank3
    primary = report_named(reports, "p676_corridor_right207_anchor8_salt207_union")
    broad = report_named(reports, "p676_corridor_right207_salt207_union")

    if has_below(primary) and has_rank3(primary):
        return f"{claim_prefix}_PRIMARY_RIGHT207_ANCHOR8_BELOW_RHO_RANK3_ADJACENT_DRIFT"
    if has_below(primary):
        return f"{claim_prefix}_PRIMARY_RIGHT207_ANCHOR8_BELOW_RHO_ADJACENT_DRIFT"
    if has_rank3(primary):
        return f"{claim_prefix}_PRIMARY_RIGHT207_ANCHOR8_RANK3_ADJACENT_DRIFT"
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
    parser.add_argument("--claim-prefix", default="P676")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P676_ADJACENT_BELOW_RHO_SURFACE_CORRIDOR_QUIET")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.summarize_cases(features)
    reports = [
        p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.rule_report(name, desc, pred, features, raw_summary)
        for name, desc, pred in RULES
    ]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p676_adjacent_below_rho_surface_corridor_scout.v1",
        "created_at": p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.utc_now(),
        "method": "p676_adjacent_below_rho_surface_corridor_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p675.p674.p673.p672.p671.p670.p669.p668.p667.p666.p665.public_feature_counts(
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
            "P676 tests adjacent drift of the P674 below-rho right207/anchor8 surface.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
