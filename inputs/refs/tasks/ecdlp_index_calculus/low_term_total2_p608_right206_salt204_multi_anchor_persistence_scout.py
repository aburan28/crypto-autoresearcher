#!/usr/bin/env python3
"""P608 adjacent persistence scout for the P607 right206/salt204_salt206 family.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. The adjacent block tests immediate drift/persistence;
the exact P607 phase/mod7 recurrences are transfers 21427, 21432, and 21433.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p607_phase8_right207_anchor6_source_21341_21352_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p607_order9887_phase8_right207_anchor6_21341_21352_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p608_right206_salt204_multi_anchor_source_21353_21364_probe.json"
DEFAULT_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p608_order9887_right206_salt204_multi_anchor_21353_21364_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p608_right206_salt204_multi_anchor_scout_21353_21364_probe.json"

P607_ROW_PAIR = "salt204_salt206"
P607_ANCHORS = {8, 9, 13}


def right206_salt204_anchor(row: p594.Feature, phase: int, mod7: int | None, anchor: int) -> bool:
    if row.get("salt_right") != 206:
        return False
    if row.get("row_pair") != P607_ROW_PAIR:
        return False
    if row.get("right_anchor") != anchor:
        return False
    if p594.phase(row) != phase:
        return False
    return mod7 is None or p594.mod7(row) == mod7


def phase7_right206_anchor9(row: p594.Feature) -> bool:
    return right206_salt204_anchor(row, 7, None, 9)


def phase7_mod7_0_right206_anchor9(row: p594.Feature) -> bool:
    return right206_salt204_anchor(row, 7, 0, 9)


def phase0_right206_anchor8(row: p594.Feature) -> bool:
    return right206_salt204_anchor(row, 0, None, 8)


def phase0_mod7_5_right206_anchor8(row: p594.Feature) -> bool:
    return right206_salt204_anchor(row, 0, 5, 8)


def phase1_right206_anchor13(row: p594.Feature) -> bool:
    return right206_salt204_anchor(row, 1, None, 13)


def phase1_mod7_6_right206_anchor13(row: p594.Feature) -> bool:
    return right206_salt204_anchor(row, 1, 6, 13)


def p607_phase_anchor_union(row: p594.Feature) -> bool:
    return phase7_right206_anchor9(row) or phase0_right206_anchor8(row) or phase1_right206_anchor13(row)


def p607_exact_phase_mod7_anchor_union(row: p594.Feature) -> bool:
    return (
        phase7_mod7_0_right206_anchor9(row)
        or phase0_mod7_5_right206_anchor8(row)
        or phase1_mod7_6_right206_anchor13(row)
    )


def right206_salt204_anchor_band_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 206
        and row.get("row_pair") == P607_ROW_PAIR
        and row.get("right_anchor") in P607_ANCHORS
    )


def right206_salt204_all_anchors_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 206 and row.get("row_pair") == P607_ROW_PAIR


def anchor_band_all_rowpairs(row: p594.Feature) -> bool:
    return row.get("right_anchor") in P607_ANCHORS


def right206_anchor_band_all_rowpairs(row: p594.Feature) -> bool:
    return row.get("salt_right") == 206 and row.get("right_anchor") in P607_ANCHORS


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p608_p607_phase_anchor_union",
            "Primary P607 drift branch: phase7/anchor9, phase0/anchor8, phase1/anchor13 on right206/salt204_salt206",
            p607_phase_anchor_union,
        ),
        (
            "p608_p607_exact_phase_mod7_anchor_union",
            "Exact P607 phase/mod7 recurrence union; expected transfers are 21427, 21432, and 21433",
            p607_exact_phase_mod7_anchor_union,
        ),
        (
            "p608_phase7_right206_anchor9_salt204",
            "P607 transfer-21343 branch: phase7/right206/anchor9/salt204_salt206",
            phase7_right206_anchor9,
        ),
        (
            "p608_phase7_mod7_0_right206_anchor9_salt204_exact",
            "Exact transfer-21343 phase7/mod7=0 recurrence control",
            phase7_mod7_0_right206_anchor9,
        ),
        (
            "p608_phase0_right206_anchor8_salt204",
            "P607 transfer-21348 branch: phase0/right206/anchor8/salt204_salt206",
            phase0_right206_anchor8,
        ),
        (
            "p608_phase0_mod7_5_right206_anchor8_salt204_exact",
            "Exact transfer-21348 phase0/mod7=5 recurrence control",
            phase0_mod7_5_right206_anchor8,
        ),
        (
            "p608_phase1_right206_anchor13_salt204",
            "P607 transfer-21349 branch: phase1/right206/anchor13/salt204_salt206",
            phase1_right206_anchor13,
        ),
        (
            "p608_phase1_mod7_6_right206_anchor13_salt204_exact",
            "Exact transfer-21349 phase1/mod7=6 recurrence control",
            phase1_mod7_6_right206_anchor13,
        ),
        (
            "p608_right206_salt204_anchor_band_all_phases",
            "Broad right206/salt204_salt206 anchor band {8,9,13} across all phases",
            right206_salt204_anchor_band_all_phases,
        ),
        (
            "p608_right206_salt204_all_anchors_all_phases",
            "Broad right206/salt204_salt206 across all anchors and phases",
            right206_salt204_all_anchors_all_phases,
        ),
        (
            "p608_right206_anchor_band_all_rowpairs",
            "right206 anchor band {8,9,13} across all emitted row pairs",
            right206_anchor_band_all_rowpairs,
        ),
        (
            "p608_anchor_band_all_rowpairs",
            "Anchor band {8,9,13} across all emitted row pairs and phases",
            anchor_band_all_rowpairs,
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-source", type=Path, default=DEFAULT_TRAIN_SOURCE)
    parser.add_argument("--train-gate", type=Path, default=DEFAULT_TRAIN_GATE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p607_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p608_validation")
    predicate_reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = predicate_reports[0]
    best_below = p594.best_report(predicate_reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(predicate_reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P608_RIGHT206_SALT204_MULTI_ANCHOR_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P608_RIGHT206_SALT204_MULTI_ANCHOR_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P608_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P608_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P608_PRIMARY_MISSED_NONQUIET_BLOCK"
    payload: dict[str, Any] = {
        "artifacts": {
            "gate": str(args.gate),
            "source": str(args.source),
            "train_gate": str(args.train_gate),
            "train_source": str(args.train_source),
        },
        "claim_status": claim_status,
        "created_at": p594.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: predicate rules use public phase, mod7, salt, anchor, row-pair, selector, and policy-role metadata only.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "CRT BOUNDARY: adjacent block tests drift/persistence, not exact P607 recurrences; exact repeats are transfers 21427, 21432, and 21433.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p608_right206_salt204_multi_anchor_persistence_scout",
        "rule_reports": predicate_reports,
        "schema": "ecdlp.low_term_total2_p608_right206_salt204_multi_anchor_persistence_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p607_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p607_direct_verified",
                ),
                "p607_phase_anchor_union": p594.cohort_summary(
                    [row for row in train_rows if p607_phase_anchor_union(row)],
                    "p607_phase_anchor_union",
                ),
                "p607_exact_phase_mod7_anchor_union": p594.cohort_summary(
                    [row for row in train_rows if p607_exact_phase_mod7_anchor_union(row)],
                    "p607_exact_phase_mod7_anchor_union",
                ),
                "p607_right206_salt204_anchor_band_all_phases": p594.cohort_summary(
                    [row for row in train_rows if right206_salt204_anchor_band_all_phases(row)],
                    "p607_right206_salt204_anchor_band_all_phases",
                ),
            },
            "validation_dataset": validation_summary,
        },
    }
    p594.write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
