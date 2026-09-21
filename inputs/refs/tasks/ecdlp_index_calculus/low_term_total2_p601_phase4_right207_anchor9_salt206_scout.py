#!/usr/bin/env python3
"""P601 adjacent holdout for the P600 phase4/right207/anchor9 salt206 pocket.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. This adjacent block tests shifted phase4 persistence,
not exact phase4/mod7=3 recurrence; the exact repeat is transfer 21220.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594
import low_term_total2_p598_phase2_right208_anchor11_salt208_scout as p598
import low_term_total2_p599_phase3_anchor13_phase4_salt206_scout as p599
import low_term_total2_p600_phase8_salt206_scout as p600


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p600_phase8_salt206_source_21125_21136_probe.json"
DEFAULT_TRAIN_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p600_order9887_phase8_salt206_21125_21136_density_gate_probe.json"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p601_phase4_right207_anchor9_salt206_source_21137_21148_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p601_order9887_phase4_right207_anchor9_salt206_21137_21148_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p601_phase4_right207_anchor9_salt206_scout_21137_21148_probe.json"

ANCHOR_BAND = {3, 6, 7, 8, 9, 11, 12, 13}


def phase4_right207_anchor9_salt206(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 4
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt206_salt207"
    )


def phase4_mod7_3_right207_anchor9_salt206(row: p594.Feature) -> bool:
    return phase4_right207_anchor9_salt206(row) and p594.mod7(row) == 3


def phase4_right207_salt206_anchor_band(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 4
        and row.get("salt_right") == 207
        and row.get("row_pair") == "salt206_salt207"
        and row.get("right_anchor") in ANCHOR_BAND
    )


def phase4_mod7_3_right207_salt206_anchor_band(row: p594.Feature) -> bool:
    return phase4_right207_salt206_anchor_band(row) and p594.mod7(row) == 3


def phase4_right207_anchor9_salt207_all_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 4
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") in p594.SALT207_ROW_PAIRS
    )


def right207_anchor9_salt206_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt206_salt207"
    )


def right207_anchor9_salt207_all_pairs_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") in p594.SALT207_ROW_PAIRS
    )


def phase4_salt206_all_rights_anchor9(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 4
        and row.get("right_anchor") == 9
        and row.get("row_pair") in {"salt204_salt206", "salt206_salt207", "salt206_salt208"}
    )


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p601_phase4_right207_anchor9_salt206",
            "Primary P600 shifted pocket: phase4/right207/anchor9/salt206_salt207",
            phase4_right207_anchor9_salt206,
        ),
        (
            "p601_phase4_mod7_3_right207_anchor9_salt206_exact_future",
            "Exact P600 phase4/mod7=3 primary control; repeat is transfer 21220",
            phase4_mod7_3_right207_anchor9_salt206,
        ),
        (
            "p601_phase4_right207_salt206_anchor_band",
            "phase4/right207/salt206_salt207 anchor band {3,6,7,8,9,11,12,13}",
            phase4_right207_salt206_anchor_band,
        ),
        (
            "p601_phase4_mod7_3_right207_salt206_anchor_band_exact_future",
            "Exact P600 phase4/mod7=3 right207 anchor-band control; repeat is transfer 21220",
            phase4_mod7_3_right207_salt206_anchor_band,
        ),
        (
            "p601_phase4_right207_anchor9_salt207_all_pairs",
            "phase4/right207/anchor9 across emitted salt207 row pairs",
            phase4_right207_anchor9_salt207_all_pairs,
        ),
        (
            "p601_right207_anchor9_salt206_all_phases",
            "right207/anchor9/salt206_salt207 across all phases",
            right207_anchor9_salt206_all_phases,
        ),
        (
            "p601_right207_salt206_anchor_band_all_phases",
            "right207/salt206_salt207 anchor band across all phases",
            p600.right207_salt206_anchor_band_all_phases,
        ),
        (
            "p601_right207_anchor9_salt207_all_pairs_all_phases",
            "right207/anchor9 across all emitted salt207 row pairs and phases",
            right207_anchor9_salt207_all_pairs_all_phases,
        ),
        (
            "p601_phase4_salt206_all_rights_anchor9",
            "phase4/anchor9 over salt206 row pairs ending in 206/207/208",
            phase4_salt206_all_rights_anchor9,
        ),
        (
            "p601_broad_salt206_replay",
            "Broad salt206 row-pair replay control",
            p600.broad_salt206_replay,
        ),
        (
            "p601_broad_salt207_replay",
            "Broad salt207 row-pair replay control",
            p594.right207_anchor_band_all_phases,
        ),
        (
            "p601_broad_salt208_replay",
            "Broad row-pair replay control over row pairs ending in salt208",
            p598.broad_salt208_replay,
        ),
        (
            "p601_stale_p600_phase7_phase8_union",
            "Failed P600 P599 phase7/phase8 branch union control",
            p600.p599_phase7_phase8_union,
        ),
        (
            "p601_stale_p599_phase3_phase4_union",
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p600_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p601_validation")
    reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = p594.best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P601_PHASE4_RIGHT207_ANCHOR9_SALT206_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P601_PHASE4_RIGHT207_ANCHOR9_SALT206_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P601_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P601_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P601_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "CRT BOUNDARY: adjacent block tests shifted phase4 persistence, not exact phase4/mod7=3 recurrence; exact repeat is transfer 21220.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p601_phase4_right207_anchor9_salt206_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p601_phase4_right207_anchor9_salt206_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p600_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p600_direct_verified",
                ),
                "p600_phase4_right207_anchor9_salt206": p594.cohort_summary(
                    [row for row in train_rows if phase4_right207_anchor9_salt206(row)],
                    "p600_phase4_right207_anchor9_salt206",
                ),
                "p600_phase4_mod7_3_right207_anchor9_salt206": p594.cohort_summary(
                    [row for row in train_rows if phase4_mod7_3_right207_anchor9_salt206(row)],
                    "p600_phase4_mod7_3_right207_anchor9_salt206",
                ),
                "p600_right207_anchor9_salt206_all_phases": p594.cohort_summary(
                    [row for row in train_rows if right207_anchor9_salt206_all_phases(row)],
                    "p600_right207_anchor9_salt206_all_phases",
                ),
                "p600_right207_salt206_anchor_band_all_phases": p594.cohort_summary(
                    [row for row in train_rows if p600.right207_salt206_anchor_band_all_phases(row)],
                    "p600_right207_salt206_anchor_band_all_phases",
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
