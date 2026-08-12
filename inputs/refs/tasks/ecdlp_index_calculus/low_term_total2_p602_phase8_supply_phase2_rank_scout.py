#!/usr/bin/env python3
"""P602 split holdout for P601 phase8 salt206 supply and phase2 salt208 rank.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. Rank is audited later from exported direct
certificates, so this scout only measures source-public direct-hit routing.
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
import low_term_total2_p601_phase4_right207_anchor9_salt206_scout as p601


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p601_phase4_right207_anchor9_salt206_source_21137_21148_probe.json"
DEFAULT_TRAIN_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p601_order9887_phase4_right207_anchor9_salt206_21137_21148_density_gate_probe.json"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p602_phase8_supply_phase2_rank_source_21149_21160_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p602_order9887_phase8_supply_phase2_rank_21149_21160_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p602_phase8_supply_phase2_rank_scout_21149_21160_probe.json"

ANCHOR_BAND = {3, 6, 7, 8, 9, 11, 12, 13}


def phase8_right207_salt206_anchor_band(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 207
        and row.get("row_pair") == "salt206_salt207"
        and row.get("right_anchor") in ANCHOR_BAND
    )


def phase8_mod7_0_right207_salt206_anchor_band(row: p594.Feature) -> bool:
    return phase8_right207_salt206_anchor_band(row) and p594.mod7(row) == 0


def phase8_mod7_5_right207_salt206_anchor_band(row: p594.Feature) -> bool:
    return phase8_right207_salt206_anchor_band(row) and p594.mod7(row) == 5


def phase8_right208_salt206_anchor_band(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 208
        and row.get("row_pair") == "salt206_salt208"
        and row.get("right_anchor") in ANCHOR_BAND
    )


def phase8_mod7_0_right208_salt206_anchor_band(row: p594.Feature) -> bool:
    return phase8_right208_salt206_anchor_band(row) and p594.mod7(row) == 0


def phase8_mod7_5_right208_salt206_anchor_band(row: p594.Feature) -> bool:
    return phase8_right208_salt206_anchor_band(row) and p594.mod7(row) == 5


def phase8_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt204_salt206"
    )


def phase8_salt206_supply_union(row: p594.Feature) -> bool:
    return (
        phase8_right207_salt206_anchor_band(row)
        or phase8_right208_salt206_anchor_band(row)
        or phase8_right206_anchor9_salt204(row)
    )


def phase2_right208_anchor13_salt208(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 2
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 13
        and row.get("row_pair") in p598.SALT208_ROW_PAIRS
    )


def phase2_mod7_6_right208_anchor13_salt208(row: p594.Feature) -> bool:
    return phase2_right208_anchor13_salt208(row) and p594.mod7(row) == 6


def phase2_mod7_4_right208_anchor13_salt208(row: p594.Feature) -> bool:
    return phase2_right208_anchor13_salt208(row) and p594.mod7(row) == 4


def phase2_right208_anchor13_salt205(row: p594.Feature) -> bool:
    return phase2_right208_anchor13_salt208(row) and row.get("row_pair") == "salt205_salt208"


def phase2_right208_anchor13_salt208_without_salt205(row: p594.Feature) -> bool:
    return phase2_right208_anchor13_salt208(row) and row.get("row_pair") != "salt205_salt208"


def split_phase8_supply_phase2_rank_union(row: p594.Feature) -> bool:
    return phase8_salt206_supply_union(row) or phase2_right208_anchor13_salt208(row)


def right208_anchor13_salt208_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 208
        and row.get("right_anchor") == 13
        and row.get("row_pair") in p598.SALT208_ROW_PAIRS
    )


def broad_right208_salt208_anchor_band(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 208
        and row.get("row_pair") in p598.SALT208_ROW_PAIRS
        and row.get("right_anchor") in ANCHOR_BAND
    )


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p602_split_phase8_supply_phase2_rank_union",
            "Primary split union: phase8 salt206 supply OR phase2/right208/anchor13/salt208 rank line",
            split_phase8_supply_phase2_rank_union,
        ),
        (
            "p602_phase8_salt206_supply_union",
            "P601 phase8 salt206 supply union: right207/right208 anchor bands plus right206/anchor9/salt204_salt206",
            phase8_salt206_supply_union,
        ),
        (
            "p602_phase8_right207_salt206_anchor_band",
            "phase8/right207/salt206_salt207 anchor band",
            phase8_right207_salt206_anchor_band,
        ),
        (
            "p602_phase8_mod7_5_right207_salt206_anchor_band_adjacent",
            "Adjacent phase8/mod7=5 right207 salt206 anchor band at transfer 21152",
            phase8_mod7_5_right207_salt206_anchor_band,
        ),
        (
            "p602_phase8_mod7_0_right207_salt206_anchor_band_exact_future",
            "Exact P601 phase8/mod7=0 right207 future control; repeat is transfer 21224",
            phase8_mod7_0_right207_salt206_anchor_band,
        ),
        (
            "p602_phase8_right208_salt206_anchor_band",
            "phase8/right208/salt206_salt208 anchor band",
            phase8_right208_salt206_anchor_band,
        ),
        (
            "p602_phase8_mod7_5_right208_salt206_anchor_band_adjacent",
            "Adjacent phase8/mod7=5 right208 salt206 anchor band at transfer 21152",
            phase8_mod7_5_right208_salt206_anchor_band,
        ),
        (
            "p602_phase8_mod7_0_right208_salt206_anchor_band_exact_future",
            "Exact P601 phase8/mod7=0 right208 future control; repeat is transfer 21224",
            phase8_mod7_0_right208_salt206_anchor_band,
        ),
        (
            "p602_phase8_right206_anchor9_salt204",
            "phase8/right206/anchor9/salt204_salt206 rank-3 companion",
            phase8_right206_anchor9_salt204,
        ),
        (
            "p602_phase2_right208_anchor13_salt208_rank_line",
            "P601 phase2/right208/anchor13 row pairs ending in salt208 rank line",
            phase2_right208_anchor13_salt208,
        ),
        (
            "p602_phase2_mod7_4_right208_anchor13_salt208_adjacent",
            "Adjacent phase2/mod7=4 right208 anchor13 salt208 control at transfer 21158",
            phase2_mod7_4_right208_anchor13_salt208,
        ),
        (
            "p602_phase2_mod7_6_right208_anchor13_salt208_exact_future",
            "Exact P601 phase2/mod7=6 right208 anchor13 future control; repeat is transfer 21230",
            phase2_mod7_6_right208_anchor13_salt208,
        ),
        (
            "p602_phase2_right208_anchor13_salt205_salt208",
            "Rank-gain row-pair focus: phase2/right208/anchor13/salt205_salt208",
            phase2_right208_anchor13_salt205,
        ),
        (
            "p602_phase2_right208_anchor13_salt208_without_salt205",
            "Rank-gain sibling controls: phase2/right208/anchor13/salt208 excluding salt205_salt208",
            phase2_right208_anchor13_salt208_without_salt205,
        ),
        (
            "p602_right208_anchor13_salt208_all_phases",
            "right208/anchor13 row pairs ending in salt208 across all phases",
            right208_anchor13_salt208_all_phases,
        ),
        (
            "p602_broad_right208_salt208_anchor_band",
            "right208/salt208 anchor band across all phases",
            broad_right208_salt208_anchor_band,
        ),
        (
            "p602_broad_salt206_replay",
            "Broad salt206 row-pair replay control",
            p600.broad_salt206_replay,
        ),
        (
            "p602_broad_salt208_replay",
            "Broad row-pair replay control over row pairs ending in salt208",
            p598.broad_salt208_replay,
        ),
        (
            "p602_stale_p601_phase4_primary",
            "Failed P601 phase4/right207/anchor9/salt206 primary control",
            p601.phase4_right207_anchor9_salt206,
        ),
        (
            "p602_stale_p600_phase7_phase8_union",
            "Failed P600 P599 phase7/phase8 branch union control",
            p600.p599_phase7_phase8_union,
        ),
        (
            "p602_stale_p599_phase3_phase4_union",
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p601_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p602_validation")
    reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = p594.best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P602_SPLIT_UNION_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P602_SPLIT_UNION_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P602_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P602_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P602_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation; rank gain is audited later from direct certificates.",
            "CRT BOUNDARY: adjacent block tests shifted persistence; exact phase8/mod7=0 and phase2/mod7=6 repeats are transfers 21224 and 21230.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p602_phase8_supply_phase2_rank_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p602_phase8_supply_phase2_rank_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p601_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p601_direct_verified",
                ),
                "p601_phase8_salt206_supply_union": p594.cohort_summary(
                    [row for row in train_rows if phase8_salt206_supply_union(row)],
                    "p601_phase8_salt206_supply_union",
                ),
                "p601_phase8_right207_salt206_anchor_band": p594.cohort_summary(
                    [row for row in train_rows if phase8_right207_salt206_anchor_band(row)],
                    "p601_phase8_right207_salt206_anchor_band",
                ),
                "p601_phase8_right208_salt206_anchor_band": p594.cohort_summary(
                    [row for row in train_rows if phase8_right208_salt206_anchor_band(row)],
                    "p601_phase8_right208_salt206_anchor_band",
                ),
                "p601_phase2_right208_anchor13_salt208_rank_line": p594.cohort_summary(
                    [row for row in train_rows if phase2_right208_anchor13_salt208(row)],
                    "p601_phase2_right208_anchor13_salt208_rank_line",
                ),
                "p601_phase2_right208_anchor13_salt205_salt208": p594.cohort_summary(
                    [row for row in train_rows if phase2_right208_anchor13_salt205(row)],
                    "p601_phase2_right208_anchor13_salt205_salt208",
                ),
                "p601_split_phase8_supply_phase2_rank_union": p594.cohort_summary(
                    [row for row in train_rows if split_phase8_supply_phase2_rank_union(row)],
                    "p601_split_phase8_supply_phase2_rank_union",
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
