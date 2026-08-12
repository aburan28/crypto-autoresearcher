#!/usr/bin/env python3
"""P613 exact recurrence scout for the P606 phase8/right207/anchor6 family.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. The block includes transfer 21416, the exact
phase8/mod7=3 recurrence point for the P606 right207/anchor6 row-pair split.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p606_phase4_right207_persistence_source_21329_21340_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p606_order9887_phase4_right207_persistence_21329_21340_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p613_p606_exact_recurrence_source_21413_21424_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p613_order9887_p606_exact_recurrence_21413_21424_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p613_p606_exact_recurrence_scout_21413_21424_probe.json"

P606_VERIFIED_ROW_PAIRS = {
    "salt203_salt207",
    "salt205_salt207",
    "salt206_salt207",
}
P606_BELOW_RHO_ROW_PAIRS = {
    "salt205_salt207",
    "salt206_salt207",
}
P605_BELOW_RHO_ANCHORS = {3, 6, 7, 8, 9, 11}


def phase8_right207_anchor6_verified_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 6
        and row.get("row_pair") in P606_VERIFIED_ROW_PAIRS
    )


def phase8_mod7_3_right207_anchor6_verified_pairs(row: p594.Feature) -> bool:
    return phase8_right207_anchor6_verified_pairs(row) and p594.mod7(row) == 3


def phase8_right207_anchor6_below_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 6
        and row.get("row_pair") in P606_BELOW_RHO_ROW_PAIRS
    )


def phase8_mod7_3_right207_anchor6_below_pairs(row: p594.Feature) -> bool:
    return phase8_right207_anchor6_below_pairs(row) and p594.mod7(row) == 3


def phase8_mod7_3_right207_anchor6_salt203(row: p594.Feature) -> bool:
    return phase8_mod7_3_right207_anchor6_verified_pairs(row) and row.get("row_pair") == "salt203_salt207"


def phase8_mod7_3_right207_anchor6_salt205(row: p594.Feature) -> bool:
    return phase8_mod7_3_right207_anchor6_verified_pairs(row) and row.get("row_pair") == "salt205_salt207"


def phase8_mod7_3_right207_anchor6_salt206(row: p594.Feature) -> bool:
    return phase8_mod7_3_right207_anchor6_verified_pairs(row) and row.get("row_pair") == "salt206_salt207"


def right207_anchor6_verified_pairs_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("right_anchor") == 6
        and row.get("row_pair") in P606_VERIFIED_ROW_PAIRS
    )


def right207_anchor6_below_pairs_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("right_anchor") == 6
        and row.get("row_pair") in P606_BELOW_RHO_ROW_PAIRS
    )


def phase8_right207_p605_anchor_band(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 207
        and row.get("row_pair") in P606_VERIFIED_ROW_PAIRS
        and row.get("right_anchor") in P605_BELOW_RHO_ANCHORS
    )


def broad_right207_anchor6_all_rowpairs(row: p594.Feature) -> bool:
    return row.get("salt_right") == 207 and row.get("right_anchor") == 6


def broad_right207_salt207(row: p594.Feature) -> bool:
    return row.get("salt_right") == 207 and row.get("row_pair") in P606_VERIFIED_ROW_PAIRS


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p613_phase8_mod7_3_right207_anchor6_below_pairs_exact",
            "Primary exact P606 below-rho row-pair recurrence: phase8/mod7=3/right207/anchor6 over salt205_salt207 and salt206_salt207",
            phase8_mod7_3_right207_anchor6_below_pairs,
        ),
        (
            "p613_phase8_mod7_3_right207_anchor6_verified_pairs_exact",
            "Exact P606 verified row-pair recurrence including above-rho salt203_salt207",
            phase8_mod7_3_right207_anchor6_verified_pairs,
        ),
        (
            "p613_phase8_mod7_3_right207_anchor6_salt203",
            "Exact P606 above-rho row-pair control: phase8/mod7=3/right207/anchor6/salt203_salt207",
            phase8_mod7_3_right207_anchor6_salt203,
        ),
        (
            "p613_phase8_mod7_3_right207_anchor6_salt205",
            "Exact P606 below-rho row-pair branch: phase8/mod7=3/right207/anchor6/salt205_salt207",
            phase8_mod7_3_right207_anchor6_salt205,
        ),
        (
            "p613_phase8_mod7_3_right207_anchor6_salt206",
            "Exact P606 below-rho row-pair branch: phase8/mod7=3/right207/anchor6/salt206_salt207",
            phase8_mod7_3_right207_anchor6_salt206,
        ),
        (
            "p613_phase8_right207_anchor6_below_pairs",
            "P606 below-rho row-pair split across all mod7 residues",
            phase8_right207_anchor6_below_pairs,
        ),
        (
            "p613_phase8_right207_anchor6_verified_pairs",
            "P606 verified row-pair split across all mod7 residues",
            phase8_right207_anchor6_verified_pairs,
        ),
        (
            "p613_right207_anchor6_below_pairs_all_phases",
            "P606 right207/anchor6 below-rho row-pair split across all phases",
            right207_anchor6_below_pairs_all_phases,
        ),
        (
            "p613_right207_anchor6_verified_pairs_all_phases",
            "P606 right207/anchor6 verified row pairs across all phases",
            right207_anchor6_verified_pairs_all_phases,
        ),
        (
            "p613_phase8_right207_p605_anchor_band",
            "phase8/right207 over P605 below-rho anchor band and P606 row pairs",
            phase8_right207_p605_anchor_band,
        ),
        (
            "p613_broad_right207_anchor6_all_rowpairs",
            "Broad right207/anchor6 across all emitted row pairs and phases",
            broad_right207_anchor6_all_rowpairs,
        ),
        (
            "p613_broad_right207_salt207",
            "Broad right207/salt207 row-pair control across all phases",
            broad_right207_salt207,
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p606_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p613_validation")
    predicate_reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = predicate_reports[0]
    exact_verified_report = predicate_reports[1]
    best_below = p594.best_report(predicate_reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(predicate_reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P613_P606_EXACT_BELOW_ROWPAIR_BELOW_RHO_VALIDATION_POSITIVE"
    elif exact_verified_report["direct_verified_count"]:
        claim_status = "P613_P606_EXACT_VERIFIED_ROWPAIR_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO_OR_MIXED"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P613_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P613_P606_EXACT_RECURRENCE_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P613_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "RECURRENCE BOUNDARY: transfer 21416 is tested as the exact P606 phase8/mod7=3/right207/anchor6 recurrence point.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, target descent, and individual-log accounting remain separate gates.",
        ],
        "method": "p613_p606_exact_recurrence_scout",
        "rule_reports": predicate_reports,
        "schema": "ecdlp.low_term_total2_p613_p606_exact_recurrence_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "exact_verified_rule": exact_verified_report,
            "main_rule": main_report,
            "training_cohorts": {
                "p606_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p606_direct_verified",
                ),
                "p606_exact_below_pairs": p594.cohort_summary(
                    [row for row in train_rows if phase8_mod7_3_right207_anchor6_below_pairs(row)],
                    "p606_exact_below_pairs",
                ),
                "p606_exact_verified_pairs": p594.cohort_summary(
                    [row for row in train_rows if phase8_mod7_3_right207_anchor6_verified_pairs(row)],
                    "p606_exact_verified_pairs",
                ),
                "p606_salt203": p594.cohort_summary(
                    [row for row in train_rows if phase8_mod7_3_right207_anchor6_salt203(row)],
                    "p606_salt203",
                ),
                "p606_salt205": p594.cohort_summary(
                    [row for row in train_rows if phase8_mod7_3_right207_anchor6_salt205(row)],
                    "p606_salt205",
                ),
                "p606_salt206": p594.cohort_summary(
                    [row for row in train_rows if phase8_mod7_3_right207_anchor6_salt206(row)],
                    "p606_salt206",
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
