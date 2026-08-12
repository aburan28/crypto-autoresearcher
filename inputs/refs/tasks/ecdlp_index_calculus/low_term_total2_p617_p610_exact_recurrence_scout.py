#!/usr/bin/env python3
"""P617 exact recurrence scout for the P610 right206/salt204 surface.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. This block contains the exact P610 phase/mod7
recurrences at transfers 21461 and 21464.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p610_split_rank_substitution_source_21377_21388_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p610_order9887_split_rank_substitution_21377_21388_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p617_p610_exact_recurrence_source_21461_21472_probe.json"
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p617_order9887_p610_exact_recurrence_21461_21472_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p617_p610_exact_recurrence_scout_21461_21472_probe.json"


def phase5_mod7_6_right206_anchor7_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 5
        and p594.mod7(row) == 6
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 7
        and row.get("row_pair") == "salt204_salt206"
    )


def phase8_mod7_2_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and p594.mod7(row) == 2
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt204_salt206"
    )


def p610_exact_surface_union(row: p594.Feature) -> bool:
    return phase5_mod7_6_right206_anchor7_salt204(row) or phase8_mod7_2_right206_anchor9_salt204(row)


def phase5_right206_anchor7_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 5
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 7
        and row.get("row_pair") == "salt204_salt206"
    )


def phase8_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt204_salt206"
    )


def p610_anchor_surface_union(row: p594.Feature) -> bool:
    return phase5_right206_anchor7_salt204(row) or phase8_right206_anchor9_salt204(row)


def right206_salt204_anchor7_or9_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 206
        and row.get("row_pair") == "salt204_salt206"
        and row.get("right_anchor") in {7, 9}
    )


def right206_salt204_all_anchors_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 206 and row.get("row_pair") == "salt204_salt206"


def phase5_right206_salt204_all_anchors(row: p594.Feature) -> bool:
    return p594.phase(row) == 5 and row.get("salt_right") == 206 and row.get("row_pair") == "salt204_salt206"


def phase8_right206_salt204_all_anchors(row: p594.Feature) -> bool:
    return p594.phase(row) == 8 and row.get("salt_right") == 206 and row.get("row_pair") == "salt204_salt206"


def right206_anchor7_all_rowpairs(row: p594.Feature) -> bool:
    return row.get("salt_right") == 206 and row.get("right_anchor") == 7


def right206_anchor9_all_rowpairs(row: p594.Feature) -> bool:
    return row.get("salt_right") == 206 and row.get("right_anchor") == 9


def anchor7_or9_all_rowpairs(row: p594.Feature) -> bool:
    return row.get("right_anchor") in {7, 9}


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p617_p610_exact_surface_union",
            "Primary exact P610 recurrence union: phase5/mod7=6/right206/anchor7/salt204 plus phase8/mod7=2/right206/anchor9/salt204",
            p610_exact_surface_union,
        ),
        (
            "p617_phase5_mod7_6_right206_anchor7_salt204",
            "Exact P610 branch at transfer 21461: phase5/mod7=6/right206/anchor7/salt204_salt206",
            phase5_mod7_6_right206_anchor7_salt204,
        ),
        (
            "p617_phase8_mod7_2_right206_anchor9_salt204",
            "Exact P610 branch at transfer 21464: phase8/mod7=2/right206/anchor9/salt204_salt206",
            phase8_mod7_2_right206_anchor9_salt204,
        ),
        (
            "p617_p610_anchor_surface_union",
            "P610 anchor surface without mod7: phase5/right206/anchor7 plus phase8/right206/anchor9 on salt204_salt206",
            p610_anchor_surface_union,
        ),
        (
            "p617_phase5_right206_anchor7_salt204",
            "phase5/right206/anchor7/salt204_salt206 across all mod7 residues",
            phase5_right206_anchor7_salt204,
        ),
        (
            "p617_phase8_right206_anchor9_salt204",
            "phase8/right206/anchor9/salt204_salt206 across all mod7 residues",
            phase8_right206_anchor9_salt204,
        ),
        (
            "p617_right206_salt204_anchor7_or9_all_phases",
            "right206/salt204_salt206 anchors {7,9} across all phases",
            right206_salt204_anchor7_or9_all_phases,
        ),
        (
            "p617_right206_salt204_all_anchors_all_phases",
            "right206/salt204_salt206 across all anchors and phases",
            right206_salt204_all_anchors_all_phases,
        ),
        (
            "p617_phase5_right206_salt204_all_anchors",
            "phase5/right206/salt204_salt206 across all anchors",
            phase5_right206_salt204_all_anchors,
        ),
        (
            "p617_phase8_right206_salt204_all_anchors",
            "phase8/right206/salt204_salt206 across all anchors",
            phase8_right206_salt204_all_anchors,
        ),
        (
            "p617_right206_anchor7_all_rowpairs",
            "right206/anchor7 across all emitted row pairs and phases",
            right206_anchor7_all_rowpairs,
        ),
        (
            "p617_right206_anchor9_all_rowpairs",
            "right206/anchor9 across all emitted row pairs and phases",
            right206_anchor9_all_rowpairs,
        ),
        (
            "p617_anchor7_or9_all_rowpairs",
            "Anchor band {7,9} across all emitted row pairs and phases",
            anchor7_or9_all_rowpairs,
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p610_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p617_validation")
    predicate_reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = predicate_reports[0]
    best_below = p594.best_report(predicate_reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(predicate_reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    broad_report = next(
        report for report in predicate_reports if report["rule"] == "p617_right206_salt204_all_anchors_all_phases"
    )
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P617_P610_EXACT_SURFACE_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P617_P610_EXACT_SURFACE_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO_OR_MIXED"
    elif broad_report["direct_below_rho_verified_count"]:
        claim_status = "P617_BROAD_RIGHT206_SALT204_BELOW_RHO_CONTROL_POSITIVE"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P617_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P617_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P617_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "RECURRENCE BOUNDARY: this block tests the exact P610 right206/salt204_salt206 recurrences at 21461 and 21464.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, target descent, and individual-log accounting remain separate gates.",
        ],
        "method": "p617_p610_exact_recurrence_scout",
        "rule_reports": predicate_reports,
        "schema": "ecdlp.low_term_total2_p617_p610_exact_recurrence_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "broad_right206_salt204_all_anchors_rule": broad_report,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p610_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p610_direct_verified",
                ),
                "p610_exact_surface_union": p594.cohort_summary(
                    [row for row in train_rows if p610_exact_surface_union(row)],
                    "p610_exact_surface_union",
                ),
                "p610_phase5_anchor7": p594.cohort_summary(
                    [row for row in train_rows if phase5_mod7_6_right206_anchor7_salt204(row)],
                    "p610_phase5_anchor7",
                ),
                "p610_phase8_anchor9": p594.cohort_summary(
                    [row for row in train_rows if phase8_mod7_2_right206_anchor9_salt204(row)],
                    "p610_phase8_anchor9",
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
