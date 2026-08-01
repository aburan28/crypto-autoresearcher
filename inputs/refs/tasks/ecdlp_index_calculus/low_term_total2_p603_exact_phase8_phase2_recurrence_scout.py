#!/usr/bin/env python3
"""P603 exact recurrence scout for the P601 phase8/phase2 split signal.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. This promotes the exact phase/mod7 recurrence
transfers from P602's future controls to the primary validation rule.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p602_phase8_supply_phase2_rank_scout as p602


p594 = p602.p594

STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p601_phase4_right207_anchor9_salt206_source_21137_21148_probe.json"
DEFAULT_TRAIN_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p601_order9887_phase4_right207_anchor9_salt206_21137_21148_density_gate_probe.json"
DEFAULT_QUIET_SOURCE = STATE_DIR / "low_term_total2_order9887_p602_phase8_supply_phase2_rank_source_21149_21160_probe.json"
DEFAULT_QUIET_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p602_order9887_phase8_supply_phase2_rank_21149_21160_density_gate_probe.json"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p603_exact_phase8_phase2_recurrence_source_21221_21232_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p603_order9887_exact_phase8_phase2_recurrence_21221_21232_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p603_exact_phase8_phase2_recurrence_scout_21221_21232_probe.json"


def phase8_mod7_0_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return p602.phase8_right206_anchor9_salt204(row) and p594.mod7(row) == 0


def exact_phase8_salt206_supply_union(row: p594.Feature) -> bool:
    return (
        p602.phase8_mod7_0_right207_salt206_anchor_band(row)
        or p602.phase8_mod7_0_right208_salt206_anchor_band(row)
        or phase8_mod7_0_right206_anchor9_salt204(row)
    )


def exact_phase2_right208_anchor13_salt205(row: p594.Feature) -> bool:
    return (
        p602.phase2_mod7_6_right208_anchor13_salt208(row)
        and row.get("row_pair") == "salt205_salt208"
    )


def exact_phase2_right208_anchor13_salt208_without_salt205(row: p594.Feature) -> bool:
    return (
        p602.phase2_mod7_6_right208_anchor13_salt208(row)
        and row.get("row_pair") != "salt205_salt208"
    )


def exact_phase8_phase2_recurrence_union(row: p594.Feature) -> bool:
    return exact_phase8_salt206_supply_union(row) or p602.phase2_mod7_6_right208_anchor13_salt208(row)


def adjacent_shift_phase8_salt206_supply_union(row: p594.Feature) -> bool:
    return (
        p602.phase8_mod7_5_right207_salt206_anchor_band(row)
        or p602.phase8_mod7_5_right208_salt206_anchor_band(row)
        or (p602.phase8_right206_anchor9_salt204(row) and p594.mod7(row) == 5)
    )


def adjacent_shift_phase8_phase2_union(row: p594.Feature) -> bool:
    return adjacent_shift_phase8_salt206_supply_union(row) or p602.phase2_mod7_4_right208_anchor13_salt208(row)


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p603_exact_phase8_phase2_recurrence_union",
            "Primary exact recurrence union: phase8/mod7=0 salt206 supply OR phase2/mod7=6 right208/anchor13/salt208 rank line",
            exact_phase8_phase2_recurrence_union,
        ),
        (
            "p603_exact_phase8_salt206_supply_union",
            "Exact P601 phase8/mod7=0 salt206 supply union",
            exact_phase8_salt206_supply_union,
        ),
        (
            "p603_exact_phase8_right207_salt206_anchor_band",
            "Exact phase8/mod7=0 right207/salt206_salt207 anchor band",
            p602.phase8_mod7_0_right207_salt206_anchor_band,
        ),
        (
            "p603_exact_phase8_right208_salt206_anchor_band",
            "Exact phase8/mod7=0 right208/salt206_salt208 anchor band",
            p602.phase8_mod7_0_right208_salt206_anchor_band,
        ),
        (
            "p603_exact_phase8_right206_anchor9_salt204_salt206",
            "Exact phase8/mod7=0 right206/anchor9/salt204_salt206 companion",
            phase8_mod7_0_right206_anchor9_salt204,
        ),
        (
            "p603_exact_phase2_right208_anchor13_salt208_rank_line",
            "Exact phase2/mod7=6 right208/anchor13 row pairs ending in salt208",
            p602.phase2_mod7_6_right208_anchor13_salt208,
        ),
        (
            "p603_exact_phase2_right208_anchor13_salt205_salt208",
            "Exact phase2/mod7=6 rank-gain row-pair focus salt205_salt208",
            exact_phase2_right208_anchor13_salt205,
        ),
        (
            "p603_exact_phase2_right208_anchor13_salt208_without_salt205",
            "Exact phase2/mod7=6 rank-line sibling controls excluding salt205_salt208",
            exact_phase2_right208_anchor13_salt208_without_salt205,
        ),
        (
            "p603_phase8_salt206_supply_any_mod7",
            "P601 phase8 salt206 supply union without mod7 restriction",
            p602.phase8_salt206_supply_union,
        ),
        (
            "p603_phase2_right208_anchor13_salt208_any_mod7",
            "P601 phase2/right208/anchor13 salt208 rank line without mod7 restriction",
            p602.phase2_right208_anchor13_salt208,
        ),
        (
            "p603_adjacent_shift_phase8_phase2_union",
            "P602 adjacent shifted phase8/mod7=5 plus phase2/mod7=4 split union control",
            adjacent_shift_phase8_phase2_union,
        ),
        (
            "p603_adjacent_shift_phase8_salt206_supply_union",
            "P602 adjacent shifted phase8/mod7=5 salt206 supply control",
            adjacent_shift_phase8_salt206_supply_union,
        ),
        (
            "p603_adjacent_shift_phase2_right208_anchor13_salt208",
            "P602 adjacent shifted phase2/mod7=4 right208/anchor13/salt208 control",
            p602.phase2_mod7_4_right208_anchor13_salt208,
        ),
        (
            "p603_right208_anchor13_salt208_all_phases",
            "right208/anchor13 row pairs ending in salt208 across all phases",
            p602.right208_anchor13_salt208_all_phases,
        ),
        (
            "p603_broad_right208_salt208_anchor_band",
            "right208/salt208 anchor band across all phases",
            p602.broad_right208_salt208_anchor_band,
        ),
        (
            "p603_broad_salt206_replay",
            "Broad salt206 row-pair replay control",
            p602.p600.broad_salt206_replay,
        ),
        (
            "p603_broad_salt208_replay",
            "Broad row-pair replay control over row pairs ending in salt208",
            p602.p598.broad_salt208_replay,
        ),
        (
            "p603_stale_p601_phase4_primary",
            "Failed P601 phase4/right207/anchor9/salt206 primary control",
            p602.p601.phase4_right207_anchor9_salt206,
        ),
        (
            "p603_stale_p600_phase7_phase8_union",
            "Failed P600 P599 phase7/phase8 branch union control",
            p602.p600.p599_phase7_phase8_union,
        ),
        (
            "p603_stale_p599_phase3_phase4_union",
            "Failed P599 phase3/phase4 branch union control",
            p602.p599.p598_phase3_phase4_union,
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-source", type=Path, default=DEFAULT_TRAIN_SOURCE)
    parser.add_argument("--train-gate", type=Path, default=DEFAULT_TRAIN_GATE)
    parser.add_argument("--quiet-source", type=Path, default=DEFAULT_QUIET_SOURCE)
    parser.add_argument("--quiet-gate", type=Path, default=DEFAULT_QUIET_GATE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p601_training")
    quiet_rows = p594.p570.source_rows([args.quiet_source], p594.p570.gate_labels([args.quiet_gate]), "p602_quiet")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p603_validation")
    reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = p594.best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P603_EXACT_RECURRENCE_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P603_EXACT_RECURRENCE_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P603_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P603_EXACT_RECURRENCE_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P603_EXACT_RECURRENCE_PRIMARY_MISSED_NONQUIET_BLOCK"
    payload: dict[str, Any] = {
        "artifacts": {
            "gate": str(args.gate),
            "quiet_gate": str(args.quiet_gate),
            "quiet_source": str(args.quiet_source),
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
            "RECURRENCE BOUNDARY: this tests exact phase/mod7 recurrence at transfers 21224 and 21230, not arbitrary target descent.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and individual logarithm/target descent remain separate gates.",
        ],
        "method": "p603_exact_phase8_phase2_recurrence_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p603_exact_phase8_phase2_recurrence_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "p602_quiet_cohorts": {
                "p602_direct_verified": p594.cohort_summary(
                    [row for row in quiet_rows if row["direct_verified"]],
                    "p602_direct_verified",
                ),
                "p602_adjacent_shift_phase8_phase2_union": p594.cohort_summary(
                    [row for row in quiet_rows if adjacent_shift_phase8_phase2_union(row)],
                    "p602_adjacent_shift_phase8_phase2_union",
                ),
                "p602_exact_phase8_phase2_recurrence_union": p594.cohort_summary(
                    [row for row in quiet_rows if exact_phase8_phase2_recurrence_union(row)],
                    "p602_exact_phase8_phase2_recurrence_union",
                ),
            },
            "training_cohorts": {
                "p601_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p601_direct_verified",
                ),
                "p601_exact_phase8_salt206_supply_union": p594.cohort_summary(
                    [row for row in train_rows if exact_phase8_salt206_supply_union(row)],
                    "p601_exact_phase8_salt206_supply_union",
                ),
                "p601_exact_phase2_right208_anchor13_salt208_rank_line": p594.cohort_summary(
                    [row for row in train_rows if p602.phase2_mod7_6_right208_anchor13_salt208(row)],
                    "p601_exact_phase2_right208_anchor13_salt208_rank_line",
                ),
                "p601_exact_phase8_phase2_recurrence_union": p594.cohort_summary(
                    [row for row in train_rows if exact_phase8_phase2_recurrence_union(row)],
                    "p601_exact_phase8_phase2_recurrence_union",
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
