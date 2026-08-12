#!/usr/bin/env python3
"""P596 phase2/right206/anchor9/salt204 adjacent-holdout scout.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. This adjacent block tests phase2 persistence for the
P595 raw-positive right206 pocket; the exact phase2/mod7=4 repeat is transfer
21158 and is not in this block.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = (
    STATE_DIR / "low_term_total2_order9887_p595_phase10_mod7_0_right207_anchor9_salt206_exact_crt_source_21065_21076_probe.json"
)
DEFAULT_TRAIN_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p595_order9887_phase10_mod7_0_right207_anchor9_salt206_exact_crt_21065_21076_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p596_phase2_right206_anchor9_salt204_source_21077_21088_probe.json"
DEFAULT_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p596_order9887_phase2_right206_anchor9_salt204_21077_21088_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p596_phase2_right206_anchor9_salt204_scout_21077_21088_probe.json"


def phase2_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return p594.phase(row) == 2 and row.get("salt_right") == 206 and row.get("right_anchor") == 9 and row.get("row_pair") == "salt204_salt206"


def phase2_mod7_4_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return phase2_right206_anchor9_salt204(row) and p594.mod7(row) == 4


def phase2_right206_anchor9(row: p594.Feature) -> bool:
    return p594.phase(row) == 2 and row.get("salt_right") == 206 and row.get("right_anchor") == 9


def phase2_anchor9_all_rowpairs(row: p594.Feature) -> bool:
    return p594.phase(row) == 2 and row.get("right_anchor") == 9


def right206_anchor9_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 206 and row.get("right_anchor") == 9


def right206_anchor_band_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 206 and row.get("right_anchor") in {3, 6, 9, 13}


def phase2_right206_anchor_band(row: p594.Feature) -> bool:
    return p594.phase(row) == 2 and row.get("salt_right") == 206 and row.get("right_anchor") in {3, 6, 9, 13}


def broad_salt204_replay(row: p594.Feature) -> bool:
    return row.get("row_pair") in {"salt204_salt206", "salt204_salt208"}


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p596_phase2_right206_anchor9_salt204",
            "Primary P595 raw-positive pocket: phase2/right206/anchor9/salt204_salt206",
            phase2_right206_anchor9_salt204,
        ),
        (
            "p596_phase2_mod7_4_right206_anchor9_salt204_exact_future",
            "Exact P595 mod7=4 control; expected zero selections until transfer 21158",
            phase2_mod7_4_right206_anchor9_salt204,
        ),
        (
            "p596_phase2_right206_anchor9",
            "phase2/right206/anchor9 across emitted right206 row pairs",
            phase2_right206_anchor9,
        ),
        (
            "p596_phase2_anchor9_all_rowpairs",
            "phase2/anchor9 across all emitted row pairs",
            phase2_anchor9_all_rowpairs,
        ),
        (
            "p596_phase2_right206_anchor_band",
            "phase2/right206 anchor band {3,6,9,13}",
            phase2_right206_anchor_band,
        ),
        (
            "p596_right206_anchor9_all_phases",
            "right206/anchor9 across all phases",
            right206_anchor9_all_phases,
        ),
        (
            "p596_right206_anchor_band_all_phases",
            "right206 anchor band {3,6,9,13} across all phases",
            right206_anchor_band_all_phases,
        ),
        (
            "p596_broad_salt204_replay",
            "Broad salt204 row-pair replay control",
            broad_salt204_replay,
        ),
        (
            "p596_stale_phase10_mod7_0_right207_anchor9_salt206",
            "Failed P595 exact phase10/mod7=0 right207 salt206 control",
            p594.phase10_mod7_0_right207_anchor9_salt206,
        ),
        (
            "p596_failed_phase9_right208_anchor7",
            "Failed right208 phase9 anchor7 control",
            p594.failed_phase9_right208_anchor7,
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p595_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p596_validation")
    reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = p594.best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P596_PRIMARY_PHASE2_RIGHT206_ANCHOR9_SALT204_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P596_PRIMARY_PHASE2_RIGHT206_ANCHOR9_SALT204_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P596_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P596_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P596_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "CRT BOUNDARY: adjacent block tests phase2 persistence, not exact phase2/mod7=4 recurrence; exact repeat is transfer 21158.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p596_phase2_right206_anchor9_salt204_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p596_phase2_right206_anchor9_salt204_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p595_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p595_direct_verified",
                ),
                "p595_primary_phase2_right206_anchor9_salt204": p594.cohort_summary(
                    [row for row in train_rows if phase2_right206_anchor9_salt204(row)],
                    "p595_primary_phase2_right206_anchor9_salt204",
                ),
                "p595_right206_anchor9_all_phases": p594.cohort_summary(
                    [row for row in train_rows if right206_anchor9_all_phases(row)],
                    "p595_right206_anchor9_all_phases",
                ),
                "p595_broad_salt204": p594.cohort_summary(
                    [row for row in train_rows if broad_salt204_replay(row)],
                    "p595_broad_salt204",
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
