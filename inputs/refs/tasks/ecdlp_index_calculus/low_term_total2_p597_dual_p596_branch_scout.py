#!/usr/bin/env python3
"""P597 adjacent holdout for the two P596 raw-positive branches.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. This adjacent block tests phase recurrence for the
phase6/right206/anchor11 and phase0/right207/anchor3 branches, not exact CRT
mod7 recurrence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594
import low_term_total2_p596_phase2_right206_anchor9_salt204_scout as p596


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p596_phase2_right206_anchor9_salt204_source_21077_21088_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p596_order9887_phase2_right206_anchor9_salt204_21077_21088_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p597_dual_p596_branch_source_21089_21100_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p597_order9887_dual_p596_branch_21089_21100_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p597_dual_p596_branch_scout_21089_21100_probe.json"

SALT207_ROW_PAIRS = {"salt203_salt207", "salt205_salt207", "salt206_salt207"}


def phase6_right206_anchor11_salt204(row: p594.Feature) -> bool:
    return p594.phase(row) == 6 and row.get("salt_right") == 206 and row.get("right_anchor") == 11 and row.get("row_pair") == "salt204_salt206"


def phase6_mod7_1_right206_anchor11_salt204(row: p594.Feature) -> bool:
    return phase6_right206_anchor11_salt204(row) and p594.mod7(row) == 1


def phase0_right207_anchor3_salt207(row: p594.Feature) -> bool:
    return p594.phase(row) == 0 and row.get("salt_right") == 207 and row.get("right_anchor") == 3 and row.get("row_pair") in SALT207_ROW_PAIRS


def phase0_mod7_0_right207_anchor3_salt207(row: p594.Feature) -> bool:
    return phase0_right207_anchor3_salt207(row) and p594.mod7(row) == 0


def dual_p596_branch(row: p594.Feature) -> bool:
    return phase6_right206_anchor11_salt204(row) or phase0_right207_anchor3_salt207(row)


def phase6_right206_anchor11(row: p594.Feature) -> bool:
    return p594.phase(row) == 6 and row.get("salt_right") == 206 and row.get("right_anchor") == 11


def phase0_right207_anchor3(row: p594.Feature) -> bool:
    return p594.phase(row) == 0 and row.get("salt_right") == 207 and row.get("right_anchor") == 3


def right206_anchor11_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 206 and row.get("right_anchor") == 11


def right207_anchor3_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 207 and row.get("right_anchor") == 3


def broad_salt207_anchor3(row: p594.Feature) -> bool:
    return row.get("row_pair") in SALT207_ROW_PAIRS and row.get("right_anchor") == 3


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p597_dual_p596_branch_union",
            "Primary P596 branch union: phase6/right206/anchor11/salt204_salt206 OR phase0/right207/anchor3/salt207",
            dual_p596_branch,
        ),
        (
            "p597_phase6_right206_anchor11_salt204",
            "P596 phase6/right206/anchor11/salt204_salt206 branch",
            phase6_right206_anchor11_salt204,
        ),
        (
            "p597_phase0_right207_anchor3_salt207",
            "P596 phase0/right207/anchor3 row pairs ending in salt207 branch",
            phase0_right207_anchor3_salt207,
        ),
        (
            "p597_phase6_mod7_1_right206_anchor11_salt204_exact_future",
            "Exact phase6/mod7=1 future control; repeat is transfer 21162",
            phase6_mod7_1_right206_anchor11_salt204,
        ),
        (
            "p597_phase0_mod7_0_right207_anchor3_salt207_exact_future",
            "Exact phase0/mod7=0 future control; repeat is transfer 21168",
            phase0_mod7_0_right207_anchor3_salt207,
        ),
        (
            "p597_phase6_right206_anchor11",
            "phase6/right206/anchor11 across all emitted right206 row pairs",
            phase6_right206_anchor11,
        ),
        (
            "p597_phase0_right207_anchor3",
            "phase0/right207/anchor3 across all emitted salt207 row pairs",
            phase0_right207_anchor3,
        ),
        (
            "p597_right206_anchor11_all_phases",
            "right206/anchor11 across all phases",
            right206_anchor11_all_phases,
        ),
        (
            "p597_right207_anchor3_all_phases",
            "right207/anchor3 across all phases",
            right207_anchor3_all_phases,
        ),
        (
            "p597_broad_salt204_replay",
            "Broad salt204 row-pair replay control",
            p596.broad_salt204_replay,
        ),
        (
            "p597_broad_salt207_anchor3",
            "Broad salt207 anchor3 replay control",
            broad_salt207_anchor3,
        ),
        (
            "p597_stale_phase2_right206_anchor9_salt204",
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p596_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p597_validation")
    reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = p594.best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P597_DUAL_BRANCH_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P597_DUAL_BRANCH_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P597_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P597_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P597_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "CRT BOUNDARY: adjacent block tests phase recurrence, not exact mod7 recurrence; exact repeats are transfers 21162 and 21168.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p597_dual_p596_branch_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p597_dual_p596_branch_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p596_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p596_direct_verified",
                ),
                "p596_phase6_right206_anchor11_salt204": p594.cohort_summary(
                    [row for row in train_rows if phase6_right206_anchor11_salt204(row)],
                    "p596_phase6_right206_anchor11_salt204",
                ),
                "p596_phase0_right207_anchor3_salt207": p594.cohort_summary(
                    [row for row in train_rows if phase0_right207_anchor3_salt207(row)],
                    "p596_phase0_right207_anchor3_salt207",
                ),
                "p596_dual_branch_union": p594.cohort_summary(
                    [row for row in train_rows if dual_p596_branch(row)],
                    "p596_dual_branch_union",
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
