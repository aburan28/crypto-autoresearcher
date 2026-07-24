#!/usr/bin/env python3
"""P609 adjacent persistence scout for the P608 right207/salt207 family.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. The adjacent block tests immediate drift/persistence;
the exact P608 phase/mod7 recurrences are transfers 21443 and 21444.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p608_right206_salt204_multi_anchor_source_21353_21364_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p608_order9887_right206_salt204_multi_anchor_21353_21364_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p609_right207_salt207_anchor13_anchor9_source_21365_21376_probe.json"
DEFAULT_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p609_order9887_right207_salt207_anchor13_anchor9_21365_21376_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p609_right207_salt207_anchor13_anchor9_scout_21365_21376_probe.json"

SALT207_ROW_PAIRS = {
    "salt203_salt207",
    "salt205_salt207",
    "salt206_salt207",
}
P608_ANCHOR13_BELOW_ROW_PAIRS = {
    "salt205_salt207",
    "salt206_salt207",
}


def phase11_right207_anchor13_verified_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 11
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 13
        and row.get("row_pair") in SALT207_ROW_PAIRS
    )


def phase11_mod7_2_right207_anchor13_verified_pairs(row: p594.Feature) -> bool:
    return phase11_right207_anchor13_verified_pairs(row) and p594.mod7(row) == 2


def phase11_right207_anchor13_below_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 11
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 13
        and row.get("row_pair") in P608_ANCHOR13_BELOW_ROW_PAIRS
    )


def phase11_mod7_2_right207_anchor13_below_pairs(row: p594.Feature) -> bool:
    return phase11_right207_anchor13_below_pairs(row) and p594.mod7(row) == 2


def phase0_right207_anchor9_salt206(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 0
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt206_salt207"
    )


def phase0_mod7_3_right207_anchor9_salt206(row: p594.Feature) -> bool:
    return phase0_right207_anchor9_salt206(row) and p594.mod7(row) == 3


def p608_verified_union(row: p594.Feature) -> bool:
    return phase11_right207_anchor13_verified_pairs(row) or phase0_right207_anchor9_salt206(row)


def p608_below_union(row: p594.Feature) -> bool:
    return phase11_right207_anchor13_below_pairs(row) or phase0_right207_anchor9_salt206(row)


def p608_exact_verified_union(row: p594.Feature) -> bool:
    return phase11_mod7_2_right207_anchor13_verified_pairs(row) or phase0_mod7_3_right207_anchor9_salt206(row)


def p608_exact_below_union(row: p594.Feature) -> bool:
    return phase11_mod7_2_right207_anchor13_below_pairs(row) or phase0_mod7_3_right207_anchor9_salt206(row)


def right207_salt207_anchor_band_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("row_pair") in SALT207_ROW_PAIRS
        and row.get("right_anchor") in {9, 13}
    )


def right207_anchor_band_all_rowpairs(row: p594.Feature) -> bool:
    return row.get("salt_right") == 207 and row.get("right_anchor") in {9, 13}


def phase11_right207_anchor13_all_rowpairs(row: p594.Feature) -> bool:
    return p594.phase(row) == 11 and row.get("salt_right") == 207 and row.get("right_anchor") == 13


def phase0_right207_anchor9_all_rowpairs(row: p594.Feature) -> bool:
    return p594.phase(row) == 0 and row.get("salt_right") == 207 and row.get("right_anchor") == 9


def broad_right207_salt207_all_anchors(row: p594.Feature) -> bool:
    return row.get("salt_right") == 207 and row.get("row_pair") in SALT207_ROW_PAIRS


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p609_p608_verified_union",
            "Primary P608 drift branch: phase11/right207/anchor13 salt207 row pairs plus phase0/right207/anchor9/salt206_salt207",
            p608_verified_union,
        ),
        (
            "p609_p608_below_union",
            "P608 below-rho branch: phase11/right207/anchor13 salt205/salt206_salt207 plus phase0/right207/anchor9/salt206_salt207",
            p608_below_union,
        ),
        (
            "p609_p608_exact_verified_union",
            "Exact P608 phase/mod7 recurrence union; expected transfers are 21443 and 21444",
            p608_exact_verified_union,
        ),
        (
            "p609_p608_exact_below_union",
            "Exact P608 below-rho phase/mod7 recurrence union",
            p608_exact_below_union,
        ),
        (
            "p609_phase11_right207_anchor13_verified_pairs",
            "P608 transfer-21359 branch: phase11/right207/anchor13 over salt203/salt205/salt206_salt207",
            phase11_right207_anchor13_verified_pairs,
        ),
        (
            "p609_phase11_mod7_2_right207_anchor13_verified_pairs_exact",
            "Exact transfer-21359 phase11/mod7=2/right207/anchor13 recurrence control",
            phase11_mod7_2_right207_anchor13_verified_pairs,
        ),
        (
            "p609_phase11_right207_anchor13_below_pairs",
            "P608 below-rho transfer-21359 branch: phase11/right207/anchor13 over salt205/salt206_salt207",
            phase11_right207_anchor13_below_pairs,
        ),
        (
            "p609_phase11_mod7_2_right207_anchor13_below_pairs_exact",
            "Exact below-rho transfer-21359 phase11/mod7=2/right207/anchor13 recurrence control",
            phase11_mod7_2_right207_anchor13_below_pairs,
        ),
        (
            "p609_phase0_right207_anchor9_salt206",
            "P608 transfer-21360 branch: phase0/right207/anchor9/salt206_salt207",
            phase0_right207_anchor9_salt206,
        ),
        (
            "p609_phase0_mod7_3_right207_anchor9_salt206_exact",
            "Exact transfer-21360 phase0/mod7=3/right207/anchor9/salt206_salt207 recurrence control",
            phase0_mod7_3_right207_anchor9_salt206,
        ),
        (
            "p609_right207_salt207_anchor_band_all_phases",
            "Broad right207/salt207 anchor band {9,13} across all phases",
            right207_salt207_anchor_band_all_phases,
        ),
        (
            "p609_right207_anchor_band_all_rowpairs",
            "Broad right207 anchor band {9,13} across all emitted row pairs",
            right207_anchor_band_all_rowpairs,
        ),
        (
            "p609_phase11_right207_anchor13_all_rowpairs",
            "phase11/right207/anchor13 across all emitted row pairs",
            phase11_right207_anchor13_all_rowpairs,
        ),
        (
            "p609_phase0_right207_anchor9_all_rowpairs",
            "phase0/right207/anchor9 across all emitted row pairs",
            phase0_right207_anchor9_all_rowpairs,
        ),
        (
            "p609_broad_right207_salt207_all_anchors",
            "Broad right207/salt207 row-pair control across all anchors and phases",
            broad_right207_salt207_all_anchors,
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p608_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p609_validation")
    predicate_reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = predicate_reports[0]
    best_below = p594.best_report(predicate_reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(predicate_reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P609_RIGHT207_SALT207_ANCHOR13_ANCHOR9_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P609_RIGHT207_SALT207_ANCHOR13_ANCHOR9_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P609_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P609_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P609_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "CRT BOUNDARY: adjacent block tests drift/persistence, not exact P608 recurrences; exact repeats are transfers 21443 and 21444.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p609_right207_salt207_anchor13_anchor9_persistence_scout",
        "rule_reports": predicate_reports,
        "schema": "ecdlp.low_term_total2_p609_right207_salt207_anchor13_anchor9_persistence_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p608_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p608_direct_verified",
                ),
                "p608_verified_union": p594.cohort_summary(
                    [row for row in train_rows if p608_verified_union(row)],
                    "p608_verified_union",
                ),
                "p608_below_union": p594.cohort_summary(
                    [row for row in train_rows if p608_below_union(row)],
                    "p608_below_union",
                ),
                "p608_right207_salt207_anchor_band_all_phases": p594.cohort_summary(
                    [row for row in train_rows if right207_salt207_anchor_band_all_phases(row)],
                    "p608_right207_salt207_anchor_band_all_phases",
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
