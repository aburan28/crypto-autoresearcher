#!/usr/bin/env python3
"""P618 scout for the right208 exact recurrence cluster.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. This block contains exact right208 recurrence checks
from P613 at transfers 21505 and 21506, and from P614 at transfer 21509.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P613_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p613_p606_exact_recurrence_source_21413_21424_probe.json"
DEFAULT_P613_TRAIN_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p613_order9887_p606_exact_recurrence_21413_21424_density_gate_probe.json"
)
DEFAULT_P614_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p614_shifted_right208_salt208_source_21425_21436_probe.json"
DEFAULT_P614_TRAIN_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p614_order9887_shifted_right208_salt208_21425_21436_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p618_right208_exact_cluster_source_21497_21509_probe.json"
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p618_order9887_right208_exact_cluster_21497_21509_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p618_right208_exact_cluster_scout_21497_21509_probe.json"

PHASE1_ANCHOR9_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
}
PHASE2_ANCHOR12_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
    "salt205_salt208",
    "salt206_salt208",
}
PHASE2_BELOW_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
    "salt206_salt208",
}
PHASE5_ANCHOR13_ROW_PAIRS = {
    "salt203_salt208",
    "salt204_salt208",
    "salt205_salt208",
    "salt206_salt208",
}
PHASE5_BELOW_ROW_PAIRS = {
    "salt203_salt208",
    "salt205_salt208",
}
RIGHT208_SALT208_ROW_PAIRS = PHASE1_ANCHOR9_ROW_PAIRS | PHASE2_ANCHOR12_ROW_PAIRS | PHASE5_ANCHOR13_ROW_PAIRS


def phase1_right208_anchor9_salt203_204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 1
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 9
        and row.get("row_pair") in PHASE1_ANCHOR9_ROW_PAIRS
    )


def phase1_mod7_1_right208_anchor9_salt203_204(row: p594.Feature) -> bool:
    return phase1_right208_anchor9_salt203_204(row) and p594.mod7(row) == 1


def phase2_right208_anchor12_all_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 2
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 12
        and row.get("row_pair") in PHASE2_ANCHOR12_ROW_PAIRS
    )


def phase2_mod7_2_right208_anchor12_all_pairs(row: p594.Feature) -> bool:
    return phase2_right208_anchor12_all_pairs(row) and p594.mod7(row) == 2


def phase2_mod7_2_right208_anchor12_below_pairs(row: p594.Feature) -> bool:
    return phase2_mod7_2_right208_anchor12_all_pairs(row) and row.get("row_pair") in PHASE2_BELOW_ROW_PAIRS


def phase2_mod7_2_right208_anchor12_rank_branch(row: p594.Feature) -> bool:
    return phase2_mod7_2_right208_anchor12_all_pairs(row) and row.get("row_pair") == "salt205_salt208"


def phase5_right208_anchor13_all_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 5
        and row.get("salt_right") == 208
        and row.get("right_anchor") == 13
        and row.get("row_pair") in PHASE5_ANCHOR13_ROW_PAIRS
    )


def phase5_mod7_5_right208_anchor13_all_pairs(row: p594.Feature) -> bool:
    return phase5_right208_anchor13_all_pairs(row) and p594.mod7(row) == 5


def phase5_mod7_5_right208_anchor13_below_pairs(row: p594.Feature) -> bool:
    return phase5_mod7_5_right208_anchor13_all_pairs(row) and row.get("row_pair") in PHASE5_BELOW_ROW_PAIRS


def phase5_mod7_5_right208_anchor13_rank_branch(row: p594.Feature) -> bool:
    return phase5_mod7_5_right208_anchor13_all_pairs(row) and row.get("row_pair") == "salt204_salt208"


def p613_exact_right208_cluster(row: p594.Feature) -> bool:
    return phase1_mod7_1_right208_anchor9_salt203_204(row) or phase2_mod7_2_right208_anchor12_all_pairs(row)


def p614_exact_right208_cluster(row: p594.Feature) -> bool:
    return phase5_mod7_5_right208_anchor13_all_pairs(row)


def right208_exact_cluster_union(row: p594.Feature) -> bool:
    return p613_exact_right208_cluster(row) or p614_exact_right208_cluster(row)


def right208_phase_surface_union(row: p594.Feature) -> bool:
    return phase1_right208_anchor9_salt203_204(row) or phase2_right208_anchor12_all_pairs(row) or phase5_right208_anchor13_all_pairs(row)


def right208_below_exact_union(row: p594.Feature) -> bool:
    return (
        phase1_mod7_1_right208_anchor9_salt203_204(row)
        or phase2_mod7_2_right208_anchor12_below_pairs(row)
        or phase5_mod7_5_right208_anchor13_below_pairs(row)
    )


def right208_rank_branch_exact_union(row: p594.Feature) -> bool:
    return phase2_mod7_2_right208_anchor12_rank_branch(row) or phase5_mod7_5_right208_anchor13_rank_branch(row)


def right208_anchor9_12_13_salt208_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 208
        and row.get("row_pair") in RIGHT208_SALT208_ROW_PAIRS
        and row.get("right_anchor") in {9, 12, 13}
    )


def right208_salt208_all_anchors_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("row_pair") in RIGHT208_SALT208_ROW_PAIRS


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p618_right208_exact_cluster_union",
            "Primary exact right208 cluster: P613 phase1/anchor9, P613 phase2/anchor12, and P614 phase5/anchor13",
            right208_exact_cluster_union,
        ),
        (
            "p618_p613_exact_right208_cluster",
            "P613 exact right208 cluster: phase1/mod7=1/anchor9 plus phase2/mod7=2/anchor12",
            p613_exact_right208_cluster,
        ),
        (
            "p618_p614_exact_right208_cluster",
            "P614 exact right208 cluster: phase5/mod7=5/anchor13",
            p614_exact_right208_cluster,
        ),
        (
            "p618_right208_below_exact_union",
            "Below-rho exact row-pair union from P613/P614 right208 positives",
            right208_below_exact_union,
        ),
        (
            "p618_right208_rank_branch_exact_union",
            "Rank-bearing exact row-pair branches: P613 salt205_salt208 anchor12 and P614 salt204_salt208 anchor13",
            right208_rank_branch_exact_union,
        ),
        (
            "p618_phase1_mod7_1_right208_anchor9_salt203_204",
            "P613 phase1/mod7=1/right208/anchor9 branch at transfer 21505",
            phase1_mod7_1_right208_anchor9_salt203_204,
        ),
        (
            "p618_phase2_mod7_2_right208_anchor12_all_pairs",
            "P613 phase2/mod7=2/right208/anchor12 branch at transfer 21506",
            phase2_mod7_2_right208_anchor12_all_pairs,
        ),
        (
            "p618_phase2_mod7_2_right208_anchor12_below_pairs",
            "P613 phase2/mod7=2/right208/anchor12 below-rho row pairs",
            phase2_mod7_2_right208_anchor12_below_pairs,
        ),
        (
            "p618_phase2_mod7_2_right208_anchor12_rank_branch",
            "P613 phase2/mod7=2/right208/anchor12 rank branch salt205_salt208",
            phase2_mod7_2_right208_anchor12_rank_branch,
        ),
        (
            "p618_phase5_mod7_5_right208_anchor13_all_pairs",
            "P614 phase5/mod7=5/right208/anchor13 branch at transfer 21509",
            phase5_mod7_5_right208_anchor13_all_pairs,
        ),
        (
            "p618_phase5_mod7_5_right208_anchor13_below_pairs",
            "P614 phase5/mod7=5/right208/anchor13 below-rho row pairs",
            phase5_mod7_5_right208_anchor13_below_pairs,
        ),
        (
            "p618_phase5_mod7_5_right208_anchor13_rank_branch",
            "P614 phase5/mod7=5/right208/anchor13 rank branch salt204_salt208",
            phase5_mod7_5_right208_anchor13_rank_branch,
        ),
        (
            "p618_right208_phase_surface_union_no_mod7",
            "Right208 phase/anchor surface union without mod7 lock",
            right208_phase_surface_union,
        ),
        (
            "p618_right208_anchor9_12_13_salt208_all_phases",
            "Broad right208/salt208 anchors {9,12,13} across all phases",
            right208_anchor9_12_13_salt208_all_phases,
        ),
        (
            "p618_right208_salt208_all_anchors_all_phases",
            "Broad right208/salt208 all-anchor control across all phases",
            right208_salt208_all_anchors_all_phases,
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p613-train-source", type=Path, default=DEFAULT_P613_TRAIN_SOURCE)
    parser.add_argument("--p613-train-gate", type=Path, default=DEFAULT_P613_TRAIN_GATE)
    parser.add_argument("--p614-train-source", type=Path, default=DEFAULT_P614_TRAIN_SOURCE)
    parser.add_argument("--p614-train-gate", type=Path, default=DEFAULT_P614_TRAIN_GATE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p613_rows = p594.p570.source_rows(
        [args.p613_train_source],
        p594.p570.gate_labels([args.p613_train_gate]),
        "p613_training",
    )
    p614_rows = p594.p570.source_rows(
        [args.p614_train_source],
        p594.p570.gate_labels([args.p614_train_gate]),
        "p614_training",
    )
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p618_validation")
    predicate_reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = predicate_reports[0]
    best_below = p594.best_report(predicate_reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(predicate_reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P618_RIGHT208_EXACT_CLUSTER_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P618_RIGHT208_EXACT_CLUSTER_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO_OR_MIXED"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P618_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P618_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P618_PRIMARY_MISSED_NONQUIET_BLOCK"
    payload: dict[str, Any] = {
        "artifacts": {
            "gate": str(args.gate),
            "p613_train_gate": str(args.p613_train_gate),
            "p613_train_source": str(args.p613_train_source),
            "p614_train_gate": str(args.p614_train_gate),
            "p614_train_source": str(args.p614_train_source),
            "source": str(args.source),
        },
        "claim_status": claim_status,
        "created_at": p594.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: predicate rules use public phase, mod7, salt, anchor, row-pair, selector, and policy-role metadata only.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "RECURRENCE BOUNDARY: this block tests exact right208 recurrence points 21505, 21506, and 21509.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, target descent, and individual-log accounting remain separate gates.",
        ],
        "method": "p618_right208_exact_cluster_scout",
        "rule_reports": predicate_reports,
        "schema": "ecdlp.low_term_total2_p618_right208_exact_cluster_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p613_exact_right208_cluster": p594.cohort_summary(
                    [row for row in p613_rows if p613_exact_right208_cluster(row)],
                    "p613_exact_right208_cluster",
                ),
                "p613_phase1_anchor9": p594.cohort_summary(
                    [row for row in p613_rows if phase1_mod7_1_right208_anchor9_salt203_204(row)],
                    "p613_phase1_anchor9",
                ),
                "p613_phase2_anchor12": p594.cohort_summary(
                    [row for row in p613_rows if phase2_mod7_2_right208_anchor12_all_pairs(row)],
                    "p613_phase2_anchor12",
                ),
                "p614_exact_right208_cluster": p594.cohort_summary(
                    [row for row in p614_rows if p614_exact_right208_cluster(row)],
                    "p614_exact_right208_cluster",
                ),
                "p614_phase5_anchor13": p594.cohort_summary(
                    [row for row in p614_rows if phase5_mod7_5_right208_anchor13_all_pairs(row)],
                    "p614_phase5_anchor13",
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
