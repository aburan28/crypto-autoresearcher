#!/usr/bin/env python3
"""P614 scout for the P613 shifted right208/salt208 surface.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. The adjacent 21425..21436 block can test phase
surface persistence, while exact mod7 recurrences from P613 are at 21505 and
21506.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p613_p606_exact_recurrence_source_21413_21424_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p613_order9887_p606_exact_recurrence_21413_21424_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p614_shifted_right208_salt208_source_21425_21436_probe.json"
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p614_order9887_shifted_right208_salt208_21425_21436_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p614_shifted_right208_salt208_scout_21425_21436_probe.json"

PHASE1_ANCHOR9_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
}
PHASE2_ANCHOR12_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
    "salt205_salt208",
    "salt206_salt208",
}
PHASE2_BELOW_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
    "salt206_salt208",
}
RIGHT208_SALT208_ROW_PAIRS = PHASE1_ANCHOR9_ROW_PAIRS | PHASE2_ANCHOR12_ROW_PAIRS
P607_DUE_ROW_PAIR = "salt204_salt206"


def phase1_right208_anchor9_salt203_204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 1
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") in PHASE1_ANCHOR9_ROW_PAIRS
    )


def phase1_mod7_1_right208_anchor9_salt203_204(row: p594.Feature) -> bool:
    return phase1_right208_anchor9_salt203_204(row) and p594.mod7(row) == 1


def phase2_right208_anchor12_salt203_204_205_206(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 2
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 12
        and row.get("row_pair") in PHASE2_ANCHOR12_ROW_PAIRS
    )


def phase2_mod7_2_right208_anchor12_salt203_204_205_206(row: p594.Feature) -> bool:
    return phase2_right208_anchor12_salt203_204_205_206(row) and p594.mod7(row) == 2


def p613_shifted_phase_surface(row: p594.Feature) -> bool:
    return phase1_right208_anchor9_salt203_204(row) or phase2_right208_anchor12_salt203_204_205_206(row)


def p613_shifted_exact_surface(row: p594.Feature) -> bool:
    return phase1_mod7_1_right208_anchor9_salt203_204(row) or phase2_mod7_2_right208_anchor12_salt203_204_205_206(row)


def phase2_right208_anchor12_below_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 2
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 12
        and row.get("row_pair") in PHASE2_BELOW_ROW_PAIRS
    )


def phase2_right208_anchor12_rank_branch(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 2
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 12
        and row.get("row_pair") == "salt205_salt208"
    )


def right208_salt208_anchor9_or_12_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 208
        and row.get("row_pair") in RIGHT208_SALT208_ROW_PAIRS
        and row.get("right_anchor") in {9, 12}
    )


def right208_salt208_all_anchors_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("row_pair") in RIGHT208_SALT208_ROW_PAIRS


def right208_anchor9_all_rowpairs(row: p594.Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("right_anchor") == 9


def right208_anchor12_all_rowpairs(row: p594.Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("right_anchor") == 12


def phase7_mod7_0_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 7
        and p594.mod7(row) == 0
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 9
        and row.get("row_pair") == P607_DUE_ROW_PAIR
    )


def phase0_mod7_5_right206_anchor8_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 0
        and p594.mod7(row) == 5
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 8
        and row.get("row_pair") == P607_DUE_ROW_PAIR
    )


def phase1_mod7_6_right206_anchor13_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 1
        and p594.mod7(row) == 6
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 13
        and row.get("row_pair") == P607_DUE_ROW_PAIR
    )


def p607_due_exact_controls(row: p594.Feature) -> bool:
    return (
        phase7_mod7_0_right206_anchor9_salt204(row)
        or phase0_mod7_5_right206_anchor8_salt204(row)
        or phase1_mod7_6_right206_anchor13_salt204(row)
    )


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p614_p613_shifted_right208_salt208_phase_surface",
            "Primary adjacent phase-surface test: phase1/right208/anchor9/salt203-204 plus phase2/right208/anchor12/salt203-206",
            p613_shifted_phase_surface,
        ),
        (
            "p614_p613_shifted_right208_salt208_exact_mod7_control",
            "Exact P613 shifted mod7 control; expected zero in this adjacent block because exact repeats are 21505 and 21506",
            p613_shifted_exact_surface,
        ),
        (
            "p614_phase1_right208_anchor9_salt203_204",
            "P613 transfer-21421 below-rho branch without mod7 lock",
            phase1_right208_anchor9_salt203_204,
        ),
        (
            "p614_phase2_right208_anchor12_salt203_204_205_206",
            "P613 transfer-21422 verified branch without mod7 lock",
            phase2_right208_anchor12_salt203_204_205_206,
        ),
        (
            "p614_phase2_right208_anchor12_below_pairs",
            "P613 phase2 below-rho row-pair branch excluding salt205_salt208",
            phase2_right208_anchor12_below_pairs,
        ),
        (
            "p614_phase2_right208_anchor12_rank_branch_salt205",
            "P613 phase2 rank-gain row-pair branch: salt205_salt208",
            phase2_right208_anchor12_rank_branch,
        ),
        (
            "p614_right208_salt208_anchor9_or_12_all_phases",
            "Broad right208/salt208 anchor9-or-12 control across all phases",
            right208_salt208_anchor9_or_12_all_phases,
        ),
        (
            "p614_right208_salt208_all_anchors_all_phases",
            "Broad right208/salt208 all-anchor control across all phases",
            right208_salt208_all_anchors_all_phases,
        ),
        (
            "p614_right208_anchor9_all_rowpairs",
            "Broad right208/anchor9 control across all emitted row pairs",
            right208_anchor9_all_rowpairs,
        ),
        (
            "p614_right208_anchor12_all_rowpairs",
            "Broad right208/anchor12 control across all emitted row pairs",
            right208_anchor12_all_rowpairs,
        ),
        (
            "p614_p607_due_exact_controls_union",
            "Secondary P607 exact due-transfer controls in this block over right206/salt204_salt206",
            p607_due_exact_controls,
        ),
        (
            "p614_p607_phase7_mod7_0_right206_anchor9_salt204",
            "P607 exact due control at transfer 21427",
            phase7_mod7_0_right206_anchor9_salt204,
        ),
        (
            "p614_p607_phase0_mod7_5_right206_anchor8_salt204",
            "P607 exact due control at transfer 21432",
            phase0_mod7_5_right206_anchor8_salt204,
        ),
        (
            "p614_p607_phase1_mod7_6_right206_anchor13_salt204",
            "P607 exact due control at transfer 21433",
            phase1_mod7_6_right206_anchor13_salt204,
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p613_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p614_validation")
    predicate_reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = predicate_reports[0]
    exact_shifted_report = predicate_reports[1]
    p607_due_report = predicate_reports[10]
    best_below = p594.best_report(predicate_reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(predicate_reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P614_SHIFTED_RIGHT208_PHASE_SURFACE_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P614_SHIFTED_RIGHT208_PHASE_SURFACE_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO_OR_MIXED"
    elif p607_due_report["direct_below_rho_verified_count"] or p607_due_report["direct_verified_count"]:
        claim_status = "P614_DUE_P607_EXACT_CONTROL_POSITIVE_PRIMARY_MISSED"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P614_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P614_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P614_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "RECURRENCE BOUNDARY: adjacent P614 tests phase-surface persistence, not the exact P613 mod7 recurrence at 21505 and 21506.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, target descent, and individual-log accounting remain separate gates.",
        ],
        "method": "p614_shifted_right208_salt208_persistence_scout",
        "rule_reports": predicate_reports,
        "schema": "ecdlp.low_term_total2_p614_shifted_right208_salt208_persistence_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "exact_shifted_mod7_control_rule": exact_shifted_report,
            "main_rule": main_report,
            "p607_due_exact_controls_rule": p607_due_report,
            "training_cohorts": {
                "p613_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p613_direct_verified",
                ),
                "p613_shifted_phase_surface": p594.cohort_summary(
                    [row for row in train_rows if p613_shifted_phase_surface(row)],
                    "p613_shifted_phase_surface",
                ),
                "p613_shifted_exact_surface": p594.cohort_summary(
                    [row for row in train_rows if p613_shifted_exact_surface(row)],
                    "p613_shifted_exact_surface",
                ),
                "p613_phase2_below_pairs": p594.cohort_summary(
                    [row for row in train_rows if phase2_right208_anchor12_below_pairs(row)],
                    "p613_phase2_below_pairs",
                ),
                "p613_phase2_rank_branch_salt205": p594.cohort_summary(
                    [row for row in train_rows if phase2_right208_anchor12_rank_branch(row)],
                    "p613_phase2_rank_branch_salt205",
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
