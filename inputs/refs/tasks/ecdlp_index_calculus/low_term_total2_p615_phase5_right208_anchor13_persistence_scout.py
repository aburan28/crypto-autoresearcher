#!/usr/bin/env python3
"""P615 scout for the P614 phase5/right208/anchor13 surface.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. The adjacent 21437..21448 block can test phase
surface persistence for P614, while exact P614 mod7 recurrence is at 21509.
The same block also contains the exact P608 right207/salt207 recurrences at
21443 and 21444.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p614_shifted_right208_salt208_source_21425_21436_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p614_order9887_shifted_right208_salt208_21425_21436_density_gate_probe.json"
)
DEFAULT_P608_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p608_right206_salt204_multi_anchor_source_21353_21364_probe.json"
DEFAULT_P608_TRAIN_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p608_order9887_right206_salt204_multi_anchor_21353_21364_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p615_phase5_right208_anchor13_source_21437_21448_probe.json"
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p615_order9887_phase5_right208_anchor13_21437_21448_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p615_phase5_right208_anchor13_scout_21437_21448_probe.json"

P614_RIGHT208_ANCHOR13_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
    "salt205_salt208",
    "salt206_salt208",
}
P614_BELOW_ROW_PAIRS = {
    "salt203_salt208",
    "salt205_salt208",
}
P614_ABOVE_ROW_PAIRS = {
    "salt204_salt208",
    "salt206_salt208",
}
P608_ANCHOR13_ROW_PAIRS = {
    "salt203_salt207",
    "salt205_salt207",
    "salt206_salt207",
}
P608_ANCHOR13_BELOW_ROW_PAIRS = {
    "salt205_salt207",
    "salt206_salt207",
}


def phase5_right208_anchor13_all_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 5
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 13
        and row.get("row_pair") in P614_RIGHT208_ANCHOR13_ROW_PAIRS
    )


def phase5_mod7_5_right208_anchor13_all_pairs(row: p594.Feature) -> bool:
    return phase5_right208_anchor13_all_pairs(row) and p594.mod7(row) == 5


def phase5_right208_anchor13_below_pairs(row: p594.Feature) -> bool:
    return phase5_right208_anchor13_all_pairs(row) and row.get("row_pair") in P614_BELOW_ROW_PAIRS


def phase5_right208_anchor13_above_pairs(row: p594.Feature) -> bool:
    return phase5_right208_anchor13_all_pairs(row) and row.get("row_pair") in P614_ABOVE_ROW_PAIRS


def phase5_right208_anchor13_rank3_branch(row: p594.Feature) -> bool:
    return phase5_right208_anchor13_all_pairs(row) and row.get("row_pair") == "salt204_salt208"


def right208_anchor13_salt208_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 208
        and row.get("right_anchor") == 13
        and row.get("row_pair") in P614_RIGHT208_ANCHOR13_ROW_PAIRS
    )


def right208_salt208_all_anchors_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("row_pair") in P614_RIGHT208_ANCHOR13_ROW_PAIRS


def phase11_mod7_2_right207_anchor13_all_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 11
        and p594.mod7(row) == 2
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 13
        and row.get("row_pair") in P608_ANCHOR13_ROW_PAIRS
    )


def phase11_mod7_2_right207_anchor13_below_pairs(row: p594.Feature) -> bool:
    return (
        phase11_mod7_2_right207_anchor13_all_pairs(row)
        and row.get("row_pair") in P608_ANCHOR13_BELOW_ROW_PAIRS
    )


def phase11_mod7_2_right207_anchor13_rank_branch(row: p594.Feature) -> bool:
    return (
        phase11_mod7_2_right207_anchor13_all_pairs(row)
        and row.get("row_pair") == "salt203_salt207"
    )


def phase0_mod7_3_right207_anchor9_salt206(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 0
        and p594.mod7(row) == 3
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt206_salt207"
    )


def p608_due_exact_controls(row: p594.Feature) -> bool:
    return phase11_mod7_2_right207_anchor13_all_pairs(row) or phase0_mod7_3_right207_anchor9_salt206(row)


def p608_phase_surface_controls(row: p594.Feature) -> bool:
    return (
        (
            p594.phase(row) == 11
            and row.get("salt_right") == 207
            and row.get("right_anchor") == 13
            and row.get("row_pair") in P608_ANCHOR13_ROW_PAIRS
        )
        or (
            p594.phase(row) == 0
            and row.get("salt_right") == 207
            and row.get("right_anchor") == 9
            and row.get("row_pair") == "salt206_salt207"
        )
    )


def right207_salt207_anchor9_or_13_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("row_pair") in P608_ANCHOR13_ROW_PAIRS
        and row.get("right_anchor") in {9, 13}
    )


def right207_salt207_all_anchors_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 207 and row.get("row_pair") in P608_ANCHOR13_ROW_PAIRS


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p615_phase5_right208_anchor13_all_pairs",
            "Primary P614 adjacent phase-surface test: phase5/right208/anchor13 over salt203-206_salt208",
            phase5_right208_anchor13_all_pairs,
        ),
        (
            "p615_phase5_mod7_5_right208_anchor13_exact_control",
            "Exact P614 phase5/mod7=5/right208/anchor13 control; expected later at 21509, not in this block",
            phase5_mod7_5_right208_anchor13_all_pairs,
        ),
        (
            "p615_phase5_right208_anchor13_below_pairs",
            "P614 below-rho row-pair branch: salt203_salt208 and salt205_salt208",
            phase5_right208_anchor13_below_pairs,
        ),
        (
            "p615_phase5_right208_anchor13_above_pairs",
            "P614 above-rho row-pair branch: salt204_salt208 and salt206_salt208",
            phase5_right208_anchor13_above_pairs,
        ),
        (
            "p615_phase5_right208_anchor13_rank3_branch_salt204",
            "P614 rank-3 row-pair branch: salt204_salt208",
            phase5_right208_anchor13_rank3_branch,
        ),
        (
            "p615_right208_anchor13_salt208_all_phases",
            "Broad right208/salt208 anchor13 control across all phases",
            right208_anchor13_salt208_all_phases,
        ),
        (
            "p615_right208_salt208_all_anchors_all_phases",
            "Broad right208/salt208 all-anchor control across all phases",
            right208_salt208_all_anchors_all_phases,
        ),
        (
            "p615_p608_due_exact_controls_union",
            "P608 exact due controls: phase11/mod7=2/right207/anchor13 and phase0/mod7=3/right207/anchor9",
            p608_due_exact_controls,
        ),
        (
            "p615_p608_phase_surface_controls",
            "P608 phase-surface controls without mod7 lock",
            p608_phase_surface_controls,
        ),
        (
            "p615_p608_phase11_mod7_2_right207_anchor13_all_pairs",
            "P608 exact anchor13 branch over salt203/205/206_salt207",
            phase11_mod7_2_right207_anchor13_all_pairs,
        ),
        (
            "p615_p608_phase11_mod7_2_right207_anchor13_below_pairs",
            "P608 exact anchor13 below-rho branch over salt205/206_salt207",
            phase11_mod7_2_right207_anchor13_below_pairs,
        ),
        (
            "p615_p608_phase11_mod7_2_right207_anchor13_rank_branch",
            "P608 exact anchor13 rank branch over salt203_salt207",
            phase11_mod7_2_right207_anchor13_rank_branch,
        ),
        (
            "p615_p608_phase0_mod7_3_right207_anchor9_salt206",
            "P608 exact anchor9/salt206_salt207 branch",
            phase0_mod7_3_right207_anchor9_salt206,
        ),
        (
            "p615_right207_salt207_anchor9_or_13_all_phases",
            "Broad right207/salt207 anchor9-or-13 control across all phases",
            right207_salt207_anchor9_or_13_all_phases,
        ),
        (
            "p615_right207_salt207_all_anchors_all_phases",
            "Broad right207/salt207 all-anchor control across all phases",
            right207_salt207_all_anchors_all_phases,
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-source", type=Path, default=DEFAULT_TRAIN_SOURCE)
    parser.add_argument("--train-gate", type=Path, default=DEFAULT_TRAIN_GATE)
    parser.add_argument("--p608-train-source", type=Path, default=DEFAULT_P608_TRAIN_SOURCE)
    parser.add_argument("--p608-train-gate", type=Path, default=DEFAULT_P608_TRAIN_GATE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p614_training")
    p608_train_rows = p594.p570.source_rows(
        [args.p608_train_source],
        p594.p570.gate_labels([args.p608_train_gate]),
        "p608_training",
    )
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p615_validation")
    predicate_reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = predicate_reports[0]
    p608_due_report = predicate_reports[7]
    best_below = p594.best_report(predicate_reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(predicate_reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P615_PHASE5_RIGHT208_ANCHOR13_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P615_PHASE5_RIGHT208_ANCHOR13_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO_OR_MIXED"
    elif p608_due_report["direct_below_rho_verified_count"] or p608_due_report["direct_verified_count"]:
        claim_status = "P615_DUE_P608_EXACT_CONTROL_POSITIVE_PRIMARY_MISSED"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P615_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P615_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P615_PRIMARY_MISSED_NONQUIET_BLOCK"
    payload: dict[str, Any] = {
        "artifacts": {
            "gate": str(args.gate),
            "p608_train_gate": str(args.p608_train_gate),
            "p608_train_source": str(args.p608_train_source),
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
            "RECURRENCE BOUNDARY: adjacent P615 tests P614 phase-surface persistence, not exact P614 mod7 recurrence at 21509.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, target descent, and individual-log accounting remain separate gates.",
        ],
        "method": "p615_phase5_right208_anchor13_persistence_scout",
        "rule_reports": predicate_reports,
        "schema": "ecdlp.low_term_total2_p615_phase5_right208_anchor13_persistence_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "p608_due_exact_controls_rule": p608_due_report,
            "training_cohorts": {
                "p614_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p614_direct_verified",
                ),
                "p614_phase5_right208_anchor13_all_pairs": p594.cohort_summary(
                    [row for row in train_rows if phase5_right208_anchor13_all_pairs(row)],
                    "p614_phase5_right208_anchor13_all_pairs",
                ),
                "p614_phase5_right208_anchor13_below_pairs": p594.cohort_summary(
                    [row for row in train_rows if phase5_right208_anchor13_below_pairs(row)],
                    "p614_phase5_right208_anchor13_below_pairs",
                ),
                "p614_phase5_right208_anchor13_rank3_branch": p594.cohort_summary(
                    [row for row in train_rows if phase5_right208_anchor13_rank3_branch(row)],
                    "p614_phase5_right208_anchor13_rank3_branch",
                ),
                "p608_direct_verified": p594.cohort_summary(
                    [row for row in p608_train_rows if row["direct_verified"]],
                    "p608_direct_verified",
                ),
                "p608_due_exact_controls": p594.cohort_summary(
                    [row for row in p608_train_rows if p608_due_exact_controls(row)],
                    "p608_due_exact_controls",
                ),
                "p608_phase_surface_controls": p594.cohort_summary(
                    [row for row in p608_train_rows if p608_phase_surface_controls(row)],
                    "p608_phase_surface_controls",
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
