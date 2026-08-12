#!/usr/bin/env python3
"""P600 adjacent holdout for the P599 phase8 salt206 surface.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. This adjacent block tests phase8 salt206 persistence,
not exact CRT mod7 recurrence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594
import low_term_total2_p598_phase2_right208_anchor11_salt208_scout as p598
import low_term_total2_p599_phase3_anchor13_phase4_salt206_scout as p599


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p599_phase3_anchor13_phase4_salt206_source_21113_21124_probe.json"
DEFAULT_TRAIN_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p599_order9887_phase3_anchor13_phase4_salt206_21113_21124_density_gate_probe.json"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p600_phase8_salt206_source_21125_21136_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p600_order9887_phase8_salt206_21125_21136_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p600_phase8_salt206_scout_21125_21136_probe.json"

PHASE8_ANCHORS = {3, 6, 7, 8, 9, 11, 12, 13}


def phase7_right208_anchor9_salt203(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 7
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt203_salt208"
    )


def phase7_mod7_3_right208_anchor9_salt203(row: p594.Feature) -> bool:
    return phase7_right208_anchor9_salt203(row) and p594.mod7(row) == 3


def phase8_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt204_salt206"
    )


def phase8_mod7_4_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return phase8_right206_anchor9_salt204(row) and p594.mod7(row) == 4


def phase8_right207_salt206_anchor_band(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 207
        and row.get("row_pair") == "salt206_salt207"
        and row.get("right_anchor") in PHASE8_ANCHORS
    )


def phase8_mod7_4_right207_salt206_anchor_band(row: p594.Feature) -> bool:
    return phase8_right207_salt206_anchor_band(row) and p594.mod7(row) == 4


def phase8_right208_salt206_anchor_band(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 208
        and row.get("row_pair") == "salt206_salt208"
        and row.get("right_anchor") in PHASE8_ANCHORS
    )


def phase8_mod7_4_right208_salt206_anchor_band(row: p594.Feature) -> bool:
    return phase8_right208_salt206_anchor_band(row) and p594.mod7(row) == 4


def p599_phase7_phase8_union(row: p594.Feature) -> bool:
    return (
        phase7_right208_anchor9_salt203(row)
        or phase8_right206_anchor9_salt204(row)
        or phase8_right207_salt206_anchor_band(row)
        or phase8_right208_salt206_anchor_band(row)
    )


def right207_salt206_anchor_band_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 207 and row.get("row_pair") == "salt206_salt207" and row.get("right_anchor") in PHASE8_ANCHORS


def right208_salt206_anchor_band_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("row_pair") == "salt206_salt208" and row.get("right_anchor") in PHASE8_ANCHORS


def broad_salt206_replay(row: p594.Feature) -> bool:
    return row.get("row_pair") in {"salt204_salt206", "salt206_salt207", "salt206_salt208"}


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p600_p599_phase7_phase8_union",
            "Primary P599 branch union: phase7/right208/anchor9/salt203 plus phase8 salt206 right206/right207/right208 surface",
            p599_phase7_phase8_union,
        ),
        (
            "p600_phase7_right208_anchor9_salt203",
            "P599 phase7/right208/anchor9/salt203_salt208 seed branch",
            phase7_right208_anchor9_salt203,
        ),
        (
            "p600_phase7_mod7_3_right208_anchor9_salt203_exact_future",
            "Exact phase7/mod7=3 future control; repeat is transfer 21199",
            phase7_mod7_3_right208_anchor9_salt203,
        ),
        (
            "p600_phase8_right206_anchor9_salt204",
            "P599 phase8/right206/anchor9/salt204_salt206 branch",
            phase8_right206_anchor9_salt204,
        ),
        (
            "p600_phase8_mod7_4_right206_anchor9_salt204_exact_future",
            "Exact phase8/mod7=4 companion future control; repeat is transfer 21200",
            phase8_mod7_4_right206_anchor9_salt204,
        ),
        (
            "p600_phase8_right207_salt206_anchor_band",
            "P599 phase8/right207/salt206_salt207 anchor band",
            phase8_right207_salt206_anchor_band,
        ),
        (
            "p600_phase8_mod7_4_right207_salt206_anchor_band_exact_future",
            "Exact phase8/mod7=4 right207 future control; repeat is transfer 21200",
            phase8_mod7_4_right207_salt206_anchor_band,
        ),
        (
            "p600_phase8_right208_salt206_anchor_band",
            "P599 phase8/right208/salt206_salt208 anchor band",
            phase8_right208_salt206_anchor_band,
        ),
        (
            "p600_phase8_mod7_4_right208_salt206_anchor_band_exact_future",
            "Exact phase8/mod7=4 right208 future control; repeat is transfer 21200",
            phase8_mod7_4_right208_salt206_anchor_band,
        ),
        (
            "p600_right207_salt206_anchor_band_all_phases",
            "right207/salt206_salt207 anchor band across all phases",
            right207_salt206_anchor_band_all_phases,
        ),
        (
            "p600_right208_salt206_anchor_band_all_phases",
            "right208/salt206_salt208 anchor band across all phases",
            right208_salt206_anchor_band_all_phases,
        ),
        (
            "p600_broad_salt206_replay",
            "Broad salt206 row-pair replay control",
            broad_salt206_replay,
        ),
        (
            "p600_broad_salt208_replay",
            "Broad row-pair replay control over row pairs ending in salt208",
            p598.broad_salt208_replay,
        ),
        (
            "p600_stale_p599_phase3_phase4_union",
            "Failed P599 phase3/phase4 branch union control",
            p599.p598_phase3_phase4_union,
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p599_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p600_validation")
    reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = p594.best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P600_P599_PHASE7_PHASE8_UNION_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P600_P599_PHASE7_PHASE8_UNION_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P600_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P600_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P600_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "CRT BOUNDARY: adjacent block tests phase persistence, not exact phase7/mod7=3 or phase8/mod7=4 recurrence; exact repeats are transfers 21199 and 21200.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p600_phase8_salt206_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p600_phase8_salt206_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p599_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p599_direct_verified",
                ),
                "p599_phase7_right208_anchor9_salt203": p594.cohort_summary(
                    [row for row in train_rows if phase7_right208_anchor9_salt203(row)],
                    "p599_phase7_right208_anchor9_salt203",
                ),
                "p599_phase8_right206_anchor9_salt204": p594.cohort_summary(
                    [row for row in train_rows if phase8_right206_anchor9_salt204(row)],
                    "p599_phase8_right206_anchor9_salt204",
                ),
                "p599_phase8_right207_salt206_anchor_band": p594.cohort_summary(
                    [row for row in train_rows if phase8_right207_salt206_anchor_band(row)],
                    "p599_phase8_right207_salt206_anchor_band",
                ),
                "p599_phase8_right208_salt206_anchor_band": p594.cohort_summary(
                    [row for row in train_rows if phase8_right208_salt206_anchor_band(row)],
                    "p599_phase8_right208_salt206_anchor_band",
                ),
                "p599_phase7_phase8_union": p594.cohort_summary(
                    [row for row in train_rows if p599_phase7_phase8_union(row)],
                    "p599_phase7_phase8_union",
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
