#!/usr/bin/env python3
"""P604 public schedule-delta scout for P601-vs-P603 recurrence misses.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. The promoted discriminator is exact phase/mod7
recurrence plus the P601 full-period transfer_mod168 residues.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p603_exact_phase8_phase2_recurrence_scout as p603


p594 = p603.p594
p602 = p603.p602

STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p601_phase4_right207_anchor9_salt206_source_21137_21148_probe.json"
DEFAULT_TRAIN_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p601_order9887_phase4_right207_anchor9_salt206_21137_21148_density_gate_probe.json"
DEFAULT_ADJACENT_SOURCE = STATE_DIR / "low_term_total2_order9887_p602_phase8_supply_phase2_rank_source_21149_21160_probe.json"
DEFAULT_ADJACENT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p602_order9887_phase8_supply_phase2_rank_21149_21160_density_gate_probe.json"
DEFAULT_HALF_SOURCE = STATE_DIR / "low_term_total2_order9887_p603_exact_phase8_phase2_recurrence_source_21221_21232_probe.json"
DEFAULT_HALF_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p603_order9887_exact_phase8_phase2_recurrence_21221_21232_density_gate_probe.json"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p604_public_feature_delta_recurrence_source_21305_21316_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p604_order9887_public_feature_delta_recurrence_21305_21316_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p604_public_feature_delta_recurrence_scout_21305_21316_probe.json"

PHASE8_P601_MOD168 = 21140 % 168
PHASE2_P601_MOD168 = 21146 % 168
PHASE8_P603_HALF_MOD168 = 21224 % 168
PHASE2_P603_HALF_MOD168 = 21230 % 168


def mod168(row: p594.Feature) -> int:
    return p594.int_value(row.get("transfer_index"), -1) % 168


def p601_full_period_phase8_supply(row: p594.Feature) -> bool:
    return p603.exact_phase8_salt206_supply_union(row) and mod168(row) == PHASE8_P601_MOD168


def p601_full_period_phase2_rank_line(row: p594.Feature) -> bool:
    return p602.phase2_mod7_6_right208_anchor13_salt208(row) and mod168(row) == PHASE2_P601_MOD168


def p601_full_period_recurrence_union(row: p594.Feature) -> bool:
    return p601_full_period_phase8_supply(row) or p601_full_period_phase2_rank_line(row)


def p603_half_period_phase8_supply(row: p594.Feature) -> bool:
    return p603.exact_phase8_salt206_supply_union(row) and mod168(row) == PHASE8_P603_HALF_MOD168


def p603_half_period_phase2_rank_line(row: p594.Feature) -> bool:
    return p602.phase2_mod7_6_right208_anchor13_salt208(row) and mod168(row) == PHASE2_P603_HALF_MOD168


def p603_half_period_recurrence_union(row: p594.Feature) -> bool:
    return p603_half_period_phase8_supply(row) or p603_half_period_phase2_rank_line(row)


def exact_phase8_phase2_mod84_recurrence_union(row: p594.Feature) -> bool:
    return p603.exact_phase8_phase2_recurrence_union(row)


def p601_full_period_right207_salt206_anchor_band(row: p594.Feature) -> bool:
    return p602.phase8_mod7_0_right207_salt206_anchor_band(row) and mod168(row) == PHASE8_P601_MOD168


def p601_full_period_right208_salt206_anchor_band(row: p594.Feature) -> bool:
    return p602.phase8_mod7_0_right208_salt206_anchor_band(row) and mod168(row) == PHASE8_P601_MOD168


def p601_full_period_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return p603.phase8_mod7_0_right206_anchor9_salt204(row) and mod168(row) == PHASE8_P601_MOD168


def p601_full_period_phase2_salt205(row: p594.Feature) -> bool:
    return p603.exact_phase2_right208_anchor13_salt205(row) and mod168(row) == PHASE2_P601_MOD168


def p601_full_period_phase2_without_salt205(row: p594.Feature) -> bool:
    return p603.exact_phase2_right208_anchor13_salt208_without_salt205(row) and mod168(row) == PHASE2_P601_MOD168


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p604_full_period_mod168_exact_recurrence_union",
            "Primary public feature-delta rule: exact phase/mod7 recurrence plus P601 transfer_mod168 residues {140,146}",
            p601_full_period_recurrence_union,
        ),
        (
            "p604_full_period_phase8_salt206_supply",
            "Full-period phase8/mod7=0 salt206 supply at transfer_mod168=140",
            p601_full_period_phase8_supply,
        ),
        (
            "p604_full_period_phase8_right207_salt206_anchor_band",
            "Full-period phase8/right207/salt206_salt207 anchor band at transfer_mod168=140",
            p601_full_period_right207_salt206_anchor_band,
        ),
        (
            "p604_full_period_phase8_right208_salt206_anchor_band",
            "Full-period phase8/right208/salt206_salt208 anchor band at transfer_mod168=140",
            p601_full_period_right208_salt206_anchor_band,
        ),
        (
            "p604_full_period_phase8_right206_anchor9_salt204_salt206",
            "Full-period phase8/right206/anchor9/salt204_salt206 companion at transfer_mod168=140",
            p601_full_period_right206_anchor9_salt204,
        ),
        (
            "p604_full_period_phase2_right208_anchor13_salt208_rank_line",
            "Full-period phase2/mod7=6 right208/anchor13/salt208 rank line at transfer_mod168=146",
            p601_full_period_phase2_rank_line,
        ),
        (
            "p604_full_period_phase2_right208_anchor13_salt205_salt208",
            "Full-period phase2/mod7=6 rank-gain row-pair focus salt205_salt208 at transfer_mod168=146",
            p601_full_period_phase2_salt205,
        ),
        (
            "p604_full_period_phase2_right208_anchor13_salt208_without_salt205",
            "Full-period phase2/mod7=6 rank-line siblings excluding salt205_salt208 at transfer_mod168=146",
            p601_full_period_phase2_without_salt205,
        ),
        (
            "p604_phase_mod7_only_exact_recurrence_union",
            "Control: exact phase/mod7 recurrence without mod168 discriminator",
            exact_phase8_phase2_mod84_recurrence_union,
        ),
        (
            "p604_half_period_mod168_recurrence_union",
            "P603 half-period miss control: exact phase/mod7 recurrence plus transfer_mod168 residues {56,62}",
            p603_half_period_recurrence_union,
        ),
        (
            "p604_phase8_salt206_supply_any_mod168",
            "P601 phase8 salt206 supply union without mod168 restriction",
            p602.phase8_salt206_supply_union,
        ),
        (
            "p604_phase2_right208_anchor13_salt208_any_mod168",
            "P601 phase2/right208/anchor13 salt208 rank line without mod168 restriction",
            p602.phase2_right208_anchor13_salt208,
        ),
        (
            "p604_broad_salt206_replay",
            "Broad salt206 row-pair replay control",
            p602.p600.broad_salt206_replay,
        ),
        (
            "p604_broad_salt208_replay",
            "Broad row-pair replay control over row pairs ending in salt208",
            p602.p598.broad_salt208_replay,
        ),
        (
            "p604_right208_anchor13_salt208_all_phases",
            "right208/anchor13 row pairs ending in salt208 across all phases",
            p602.right208_anchor13_salt208_all_phases,
        ),
        (
            "p604_adjacent_shift_phase8_phase2_union",
            "P602 adjacent shifted phase8/mod7=5 plus phase2/mod7=4 split union control",
            p603.adjacent_shift_phase8_phase2_union,
        ),
        (
            "p604_stale_p601_phase4_primary",
            "Failed P601 phase4/right207/anchor9/salt206 primary control",
            p602.p601.phase4_right207_anchor9_salt206,
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-source", type=Path, default=DEFAULT_TRAIN_SOURCE)
    parser.add_argument("--train-gate", type=Path, default=DEFAULT_TRAIN_GATE)
    parser.add_argument("--adjacent-source", type=Path, default=DEFAULT_ADJACENT_SOURCE)
    parser.add_argument("--adjacent-gate", type=Path, default=DEFAULT_ADJACENT_GATE)
    parser.add_argument("--half-source", type=Path, default=DEFAULT_HALF_SOURCE)
    parser.add_argument("--half-gate", type=Path, default=DEFAULT_HALF_GATE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def cohort(rows: list[p594.Feature], predicate: p594.Predicate, name: str) -> dict[str, Any]:
    return p594.cohort_summary([row for row in rows if predicate(row)], name)


def main() -> int:
    args = parse_args()
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p601_training")
    adjacent_rows = p594.p570.source_rows(
        [args.adjacent_source], p594.p570.gate_labels([args.adjacent_gate]), "p602_adjacent"
    )
    half_rows = p594.p570.source_rows([args.half_source], p594.p570.gate_labels([args.half_gate]), "p603_half")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p604_validation")
    reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = p594.best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P604_FULL_PERIOD_MOD168_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P604_FULL_PERIOD_MOD168_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P604_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P604_FULL_PERIOD_MOD168_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P604_FULL_PERIOD_MOD168_PRIMARY_MISSED_NONQUIET_BLOCK"
    payload: dict[str, Any] = {
        "artifacts": {
            "adjacent_gate": str(args.adjacent_gate),
            "adjacent_source": str(args.adjacent_source),
            "gate": str(args.gate),
            "half_gate": str(args.half_gate),
            "half_source": str(args.half_source),
            "source": str(args.source),
            "train_gate": str(args.train_gate),
            "train_source": str(args.train_source),
        },
        "claim_status": claim_status,
        "created_at": p594.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: validation rules use public transfer residues, phase, mod7, salt, anchor, row-pair, selector, and policy-role metadata only.",
            "LABEL BOUNDARY: direct verifier outcomes and relation_count are joined only for evaluation; they are not used by P604 selectors.",
            "SCHEDULE HYPOTHESIS: the primary discriminator is transfer_mod168, a public schedule feature inferred from P601 positives and P603 half-period misses.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and individual logarithm/target descent remain separate gates.",
        ],
        "method": "p604_public_feature_delta_recurrence_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p604_public_feature_delta_recurrence_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "schedule_residues": {
                "p601_phase8_transfer_mod168": PHASE8_P601_MOD168,
                "p601_phase2_transfer_mod168": PHASE2_P601_MOD168,
                "p603_half_phase8_transfer_mod168": PHASE8_P603_HALF_MOD168,
                "p603_half_phase2_transfer_mod168": PHASE2_P603_HALF_MOD168,
            },
            "training_cohorts": {
                "p601_full_period_mod168_exact_recurrence_union": cohort(
                    train_rows,
                    p601_full_period_recurrence_union,
                    "p601_full_period_mod168_exact_recurrence_union",
                ),
                "p601_phase_mod7_only_exact_recurrence_union": cohort(
                    train_rows,
                    exact_phase8_phase2_mod84_recurrence_union,
                    "p601_phase_mod7_only_exact_recurrence_union",
                ),
            },
            "miss_cohorts": {
                "p602_adjacent_full_period_mod168_union": cohort(
                    adjacent_rows,
                    p601_full_period_recurrence_union,
                    "p602_adjacent_full_period_mod168_union",
                ),
                "p602_adjacent_phase_mod7_only_exact_union": cohort(
                    adjacent_rows,
                    exact_phase8_phase2_mod84_recurrence_union,
                    "p602_adjacent_phase_mod7_only_exact_union",
                ),
                "p603_half_full_period_mod168_union": cohort(
                    half_rows,
                    p601_full_period_recurrence_union,
                    "p603_half_full_period_mod168_union",
                ),
                "p603_half_phase_mod7_only_exact_union": cohort(
                    half_rows,
                    exact_phase8_phase2_mod84_recurrence_union,
                    "p603_half_phase_mod7_only_exact_union",
                ),
                "p603_half_period_mod168_union": cohort(
                    half_rows,
                    p603_half_period_recurrence_union,
                    "p603_half_period_mod168_union",
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
