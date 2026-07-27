#!/usr/bin/env python3
"""P598 phase2/right208/anchor11/salt208 adjacent-holdout scout.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. This adjacent block tests phase2 persistence for the
P597 raw-positive right208 pocket; the exact phase2/mod7=0 repeat is transfer
21182 and is not in this block.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594
import low_term_total2_p596_phase2_right206_anchor9_salt204_scout as p596
import low_term_total2_p597_dual_p596_branch_scout as p597


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p597_dual_p596_branch_source_21089_21100_probe.json"
DEFAULT_TRAIN_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p597_order9887_dual_p596_branch_21089_21100_density_gate_probe.json"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p598_phase2_right208_anchor11_salt208_source_21101_21112_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p598_order9887_phase2_right208_anchor11_salt208_21101_21112_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p598_phase2_right208_anchor11_salt208_scout_21101_21112_probe.json"

SALT208_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
    "salt205_salt208",
    "salt206_salt208",
}


def phase2_right208_anchor11_salt208(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 2
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 11
        and row.get("row_pair") in SALT208_ROW_PAIRS
    )


def phase2_mod7_0_right208_anchor11_salt208(row: p594.Feature) -> bool:
    return phase2_right208_anchor11_salt208(row) and p594.mod7(row) == 0


def phase2_right208_anchor11(row: p594.Feature) -> bool:
    return p594.phase(row) == 2 and row.get("salt_right") == 208 and row.get("right_anchor") == 11


def phase2_anchor11_all_rowpairs(row: p594.Feature) -> bool:
    return p594.phase(row) == 2 and row.get("right_anchor") == 11


def right208_anchor11_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("right_anchor") == 11


def right208_anchor_band_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("right_anchor") in {3, 7, 9, 11, 13}


def phase2_right208_anchor_band(row: p594.Feature) -> bool:
    return p594.phase(row) == 2 and row.get("salt_right") == 208 and row.get("right_anchor") in {3, 7, 9, 11, 13}


def broad_salt208_replay(row: p594.Feature) -> bool:
    return row.get("row_pair") in SALT208_ROW_PAIRS


def phase2_right206_anchor3_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 2
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 3
        and row.get("row_pair") == "salt204_salt206"
    )


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p598_phase2_right208_anchor11_salt208",
            "Primary P597 raw-positive pocket: phase2/right208/anchor11 row pairs ending in salt208",
            phase2_right208_anchor11_salt208,
        ),
        (
            "p598_phase2_mod7_0_right208_anchor11_salt208_exact_future",
            "Exact P597 mod7=0 control; expected zero selections until transfer 21182",
            phase2_mod7_0_right208_anchor11_salt208,
        ),
        (
            "p598_phase2_right208_anchor11",
            "phase2/right208/anchor11 across all emitted salt208 row pairs",
            phase2_right208_anchor11,
        ),
        (
            "p598_phase2_anchor11_all_rowpairs",
            "phase2/anchor11 across all emitted row pairs",
            phase2_anchor11_all_rowpairs,
        ),
        (
            "p598_phase2_right208_anchor_band",
            "phase2/right208 anchor band {3,7,9,11,13}",
            phase2_right208_anchor_band,
        ),
        (
            "p598_right208_anchor11_all_phases",
            "right208/anchor11 across all phases",
            right208_anchor11_all_phases,
        ),
        (
            "p598_right208_anchor_band_all_phases",
            "right208 anchor band {3,7,9,11,13} across all phases",
            right208_anchor_band_all_phases,
        ),
        (
            "p598_broad_salt208_replay",
            "Broad row-pair replay control over row pairs ending in salt208",
            broad_salt208_replay,
        ),
        (
            "p598_p597_rank3_phase2_right206_anchor3_salt204",
            "P597 rank-3 above-rho diagnostic branch: phase2/right206/anchor3/salt204_salt206",
            phase2_right206_anchor3_salt204,
        ),
        (
            "p598_stale_p597_dual_p596_branch_union",
            "Failed P597 dual P596 branch control",
            p597.dual_p596_branch,
        ),
        (
            "p598_stale_p596_phase2_right206_anchor9_salt204",
            "Failed P596 phase2/right206/anchor9/salt204 primary control",
            p596.phase2_right206_anchor9_salt204,
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p597_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p598_validation")
    reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = p594.best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P598_PRIMARY_PHASE2_RIGHT208_ANCHOR11_SALT208_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P598_PRIMARY_PHASE2_RIGHT208_ANCHOR11_SALT208_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P598_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P598_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P598_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "CRT BOUNDARY: adjacent block tests phase2 persistence, not exact phase2/mod7=0 recurrence; exact repeat is transfer 21182.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p598_phase2_right208_anchor11_salt208_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p598_phase2_right208_anchor11_salt208_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p597_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p597_direct_verified",
                ),
                "p597_primary_phase2_right208_anchor11_salt208": p594.cohort_summary(
                    [row for row in train_rows if phase2_right208_anchor11_salt208(row)],
                    "p597_primary_phase2_right208_anchor11_salt208",
                ),
                "p597_rank3_phase2_right206_anchor3_salt204": p594.cohort_summary(
                    [row for row in train_rows if phase2_right206_anchor3_salt204(row)],
                    "p597_rank3_phase2_right206_anchor3_salt204",
                ),
                "p597_broad_salt208": p594.cohort_summary(
                    [row for row in train_rows if broad_salt208_replay(row)],
                    "p597_broad_salt208",
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
