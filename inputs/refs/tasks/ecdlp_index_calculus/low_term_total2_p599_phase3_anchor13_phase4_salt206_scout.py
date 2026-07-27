#!/usr/bin/env python3
"""P599 adjacent holdout for the P598 phase3 and phase4 raw-positive branches.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. This adjacent block tests phase persistence for the
P598 phase3/right208/anchor13 and phase4/salt206 branches, not exact CRT
mod7 recurrence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594
import low_term_total2_p598_phase2_right208_anchor11_salt208_scout as p598


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p598_phase2_right208_anchor11_salt208_source_21101_21112_probe.json"
DEFAULT_TRAIN_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p598_order9887_phase2_right208_anchor11_salt208_21101_21112_density_gate_probe.json"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p599_phase3_anchor13_phase4_salt206_source_21113_21124_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p599_order9887_phase3_anchor13_phase4_salt206_21113_21124_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p599_phase3_anchor13_phase4_salt206_scout_21113_21124_probe.json"

PHASE4_RIGHT208_ANCHORS = {3, 6, 7, 9, 13}


def phase3_right208_anchor13_salt208(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 3
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 13
        and row.get("row_pair") in p598.SALT208_ROW_PAIRS
    )


def phase3_mod7_6_right208_anchor13_salt208(row: p594.Feature) -> bool:
    return phase3_right208_anchor13_salt208(row) and p594.mod7(row) == 6


def phase4_right208_salt206_anchor_band(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 4
        and row.get("salt_right") == 208
        and row.get("row_pair") == "salt206_salt208"
        and row.get("right_anchor") in PHASE4_RIGHT208_ANCHORS
    )


def phase4_mod7_0_right208_salt206_anchor_band(row: p594.Feature) -> bool:
    return phase4_right208_salt206_anchor_band(row) and p594.mod7(row) == 0


def phase4_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 4
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt204_salt206"
    )


def phase4_mod7_0_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return phase4_right206_anchor9_salt204(row) and p594.mod7(row) == 0


def p598_phase3_phase4_union(row: p594.Feature) -> bool:
    return (
        phase3_right208_anchor13_salt208(row)
        or phase4_right208_salt206_anchor_band(row)
        or phase4_right206_anchor9_salt204(row)
    )


def right208_anchor13_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("right_anchor") == 13


def right208_salt206_anchor_band_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("row_pair") == "salt206_salt208" and row.get("right_anchor") in PHASE4_RIGHT208_ANCHORS


def phase4_right208_all_anchors_salt206(row: p594.Feature) -> bool:
    return p594.phase(row) == 4 and row.get("salt_right") == 208 and row.get("row_pair") == "salt206_salt208"


def broad_salt206_replay(row: p594.Feature) -> bool:
    return row.get("row_pair") in {"salt204_salt206", "salt206_salt207", "salt206_salt208"}


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p599_p598_phase3_phase4_union",
            "Primary P598 branch union: phase3/right208/anchor13/salt208 OR phase4/right208/salt206_salt208 anchor band OR phase4/right206/anchor9/salt204",
            p598_phase3_phase4_union,
        ),
        (
            "p599_phase3_right208_anchor13_salt208",
            "P598 phase3/right208/anchor13 row pairs ending in salt208 branch",
            phase3_right208_anchor13_salt208,
        ),
        (
            "p599_phase3_mod7_6_right208_anchor13_salt208_exact_future",
            "Exact phase3/mod7=6 future control; repeat is transfer 21195",
            phase3_mod7_6_right208_anchor13_salt208,
        ),
        (
            "p599_phase4_right208_salt206_anchor_band",
            "P598 phase4/right208/salt206_salt208 anchor band {3,6,7,9,13}",
            phase4_right208_salt206_anchor_band,
        ),
        (
            "p599_phase4_mod7_0_right208_salt206_anchor_band_exact_future",
            "Exact phase4/mod7=0 future control; repeat is transfer 21196",
            phase4_mod7_0_right208_salt206_anchor_band,
        ),
        (
            "p599_phase4_right206_anchor9_salt204",
            "P598 phase4/right206/anchor9/salt204_salt206 companion branch",
            phase4_right206_anchor9_salt204,
        ),
        (
            "p599_phase4_mod7_0_right206_anchor9_salt204_exact_future",
            "Exact companion phase4/mod7=0 future control; repeat is transfer 21196",
            phase4_mod7_0_right206_anchor9_salt204,
        ),
        (
            "p599_right208_anchor13_all_phases",
            "right208/anchor13 across all phases",
            right208_anchor13_all_phases,
        ),
        (
            "p599_right208_salt206_anchor_band_all_phases",
            "right208/salt206_salt208 anchor band {3,6,7,9,13} across all phases",
            right208_salt206_anchor_band_all_phases,
        ),
        (
            "p599_phase4_right208_all_anchors_salt206",
            "phase4/right208/salt206_salt208 across all emitted anchors",
            phase4_right208_all_anchors_salt206,
        ),
        (
            "p599_broad_salt208_replay",
            "Broad row-pair replay control over row pairs ending in salt208",
            p598.broad_salt208_replay,
        ),
        (
            "p599_broad_salt206_replay",
            "Broad salt206 row-pair replay control",
            broad_salt206_replay,
        ),
        (
            "p599_stale_phase2_right208_anchor11_salt208",
            "Failed P598 phase2/right208/anchor11/salt208 primary control",
            p598.phase2_right208_anchor11_salt208,
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p598_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p599_validation")
    reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = p594.best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P599_P598_PHASE3_PHASE4_UNION_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P599_P598_PHASE3_PHASE4_UNION_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P599_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P599_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P599_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "SOURCE-ONLY SELECTION: validation rules use public phase, mod7, salt, anchor, row-pair, selector, and policy-role metadata only.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "CRT BOUNDARY: adjacent block tests phase persistence, not exact phase3/mod7=6 or phase4/mod7=0 recurrence; exact repeats are transfers 21195 and 21196.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p599_phase3_anchor13_phase4_salt206_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p599_phase3_anchor13_phase4_salt206_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p598_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p598_direct_verified",
                ),
                "p598_phase3_right208_anchor13_salt208": p594.cohort_summary(
                    [row for row in train_rows if phase3_right208_anchor13_salt208(row)],
                    "p598_phase3_right208_anchor13_salt208",
                ),
                "p598_phase4_right208_salt206_anchor_band": p594.cohort_summary(
                    [row for row in train_rows if phase4_right208_salt206_anchor_band(row)],
                    "p598_phase4_right208_salt206_anchor_band",
                ),
                "p598_phase4_right206_anchor9_salt204": p594.cohort_summary(
                    [row for row in train_rows if phase4_right206_anchor9_salt204(row)],
                    "p598_phase4_right206_anchor9_salt204",
                ),
                "p598_phase3_phase4_union": p594.cohort_summary(
                    [row for row in train_rows if p598_phase3_phase4_union(row)],
                    "p598_phase3_phase4_union",
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
