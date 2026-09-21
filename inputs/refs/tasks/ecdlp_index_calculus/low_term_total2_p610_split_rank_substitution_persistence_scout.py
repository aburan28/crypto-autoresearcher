#!/usr/bin/env python3
"""P610 adjacent persistence scout for the P609 split rank/substitution signal.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. The adjacent block tests immediate drift/persistence;
the exact P609 phase/mod7 recurrences are transfers 21449 and 21456.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p609_right207_salt207_anchor13_anchor9_source_21365_21376_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p609_order9887_right207_salt207_anchor13_anchor9_21365_21376_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p610_split_rank_substitution_source_21377_21388_probe.json"
DEFAULT_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p610_order9887_split_rank_substitution_21377_21388_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p610_split_rank_substitution_scout_21377_21388_probe.json"

SALT207_ROW_PAIRS = {
    "salt203_salt207",
    "salt205_salt207",
    "salt206_salt207",
}


def phase5_right207_anchor9_salt205(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 5
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt205_salt207"
    )


def phase5_mod7_1_right207_anchor9_salt205(row: p594.Feature) -> bool:
    return phase5_right207_anchor9_salt205(row) and p594.mod7(row) == 1


def phase0_right206_anchor8_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 0
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 8
        and row.get("row_pair") == "salt204_salt206"
    )


def phase0_mod7_1_right206_anchor8_salt204(row: p594.Feature) -> bool:
    return phase0_right206_anchor8_salt204(row) and p594.mod7(row) == 1


def p609_split_union(row: p594.Feature) -> bool:
    return phase5_right207_anchor9_salt205(row) or phase0_right206_anchor8_salt204(row)


def p609_exact_split_union(row: p594.Feature) -> bool:
    return phase5_mod7_1_right207_anchor9_salt205(row) or phase0_mod7_1_right206_anchor8_salt204(row)


def phase5_right207_anchor9_all_salt207(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 5
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") in SALT207_ROW_PAIRS
    )


def right207_anchor9_salt207_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") in SALT207_ROW_PAIRS
    )


def phase0_right206_anchor8_all_rowpairs(row: p594.Feature) -> bool:
    return p594.phase(row) == 0 and row.get("salt_right") == 206 and row.get("right_anchor") == 8


def right206_anchor8_salt204_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 206
        and row.get("right_anchor") == 8
        and row.get("row_pair") == "salt204_salt206"
    )


def right206_salt204_all_anchors_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 206 and row.get("row_pair") == "salt204_salt206"


def anchor8_or9_all_rowpairs(row: p594.Feature) -> bool:
    return row.get("right_anchor") in {8, 9}


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p610_p609_split_union",
            "Primary P609 split union: phase5/right207/anchor9/salt205_salt207 plus phase0/right206/anchor8/salt204_salt206",
            p609_split_union,
        ),
        (
            "p610_p609_exact_split_union",
            "Exact P609 split phase/mod7 recurrence union; expected transfers are 21449 and 21456",
            p609_exact_split_union,
        ),
        (
            "p610_phase5_right207_anchor9_salt205",
            "P609 substitution-positive branch: phase5/right207/anchor9/salt205_salt207",
            phase5_right207_anchor9_salt205,
        ),
        (
            "p610_phase5_mod7_1_right207_anchor9_salt205_exact",
            "Exact transfer-21365 phase5/mod7=1/right207/anchor9/salt205_salt207 recurrence control",
            phase5_mod7_1_right207_anchor9_salt205,
        ),
        (
            "p610_phase0_right206_anchor8_salt204",
            "P609 rank-positive branch: phase0/right206/anchor8/salt204_salt206",
            phase0_right206_anchor8_salt204,
        ),
        (
            "p610_phase0_mod7_1_right206_anchor8_salt204_exact",
            "Exact transfer-21372 phase0/mod7=1/right206/anchor8/salt204_salt206 recurrence control",
            phase0_mod7_1_right206_anchor8_salt204,
        ),
        (
            "p610_phase5_right207_anchor9_all_salt207",
            "phase5/right207/anchor9 across salt203/salt205/salt206_salt207",
            phase5_right207_anchor9_all_salt207,
        ),
        (
            "p610_right207_anchor9_salt207_all_phases",
            "right207/anchor9 over salt207 row pairs across all phases",
            right207_anchor9_salt207_all_phases,
        ),
        (
            "p610_phase0_right206_anchor8_all_rowpairs",
            "phase0/right206/anchor8 across all emitted row pairs",
            phase0_right206_anchor8_all_rowpairs,
        ),
        (
            "p610_right206_anchor8_salt204_all_phases",
            "right206/anchor8/salt204_salt206 across all phases",
            right206_anchor8_salt204_all_phases,
        ),
        (
            "p610_right206_salt204_all_anchors_all_phases",
            "right206/salt204_salt206 across all anchors and phases",
            right206_salt204_all_anchors_all_phases,
        ),
        (
            "p610_anchor8_or9_all_rowpairs",
            "Anchor band {8,9} across all emitted row pairs and phases",
            anchor8_or9_all_rowpairs,
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p609_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p610_validation")
    predicate_reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = predicate_reports[0]
    best_below = p594.best_report(predicate_reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(predicate_reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P610_SPLIT_RANK_SUBSTITUTION_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P610_SPLIT_RANK_SUBSTITUTION_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P610_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P610_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P610_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "CRT BOUNDARY: adjacent block tests drift/persistence, not exact P609 recurrences; exact repeats are transfers 21449 and 21456.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p610_split_rank_substitution_persistence_scout",
        "rule_reports": predicate_reports,
        "schema": "ecdlp.low_term_total2_p610_split_rank_substitution_persistence_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p609_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p609_direct_verified",
                ),
                "p609_split_union": p594.cohort_summary(
                    [row for row in train_rows if p609_split_union(row)],
                    "p609_split_union",
                ),
                "p609_substitution_branch": p594.cohort_summary(
                    [row for row in train_rows if phase5_right207_anchor9_salt205(row)],
                    "p609_substitution_branch",
                ),
                "p609_rank_branch": p594.cohort_summary(
                    [row for row in train_rows if phase0_right206_anchor8_salt204(row)],
                    "p609_rank_branch",
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
