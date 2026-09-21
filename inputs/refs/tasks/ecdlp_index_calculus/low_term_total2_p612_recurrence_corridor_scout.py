#!/usr/bin/env python3
"""P612 recurrence-corridor scout for due P605/P610 relation surfaces.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. The block includes transfer 21412, the exact
phase4/mod7=6 recurrence point for the P605 right207 relation-supply family.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p605_public_context_fingerprint_delta_source_21317_21328_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p605_order9887_public_context_fingerprint_delta_21317_21328_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p612_recurrence_corridor_source_21401_21412_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p612_order9887_recurrence_corridor_21401_21412_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p612_recurrence_corridor_scout_21401_21412_probe.json"

P605_ROW_PAIRS = {
    "salt203_salt207",
    "salt205_salt207",
    "salt206_salt207",
}
P605_BELOW_RHO_ANCHORS = {3, 6, 7, 8, 9, 11}
P605_VERIFIED_ANCHORS = {3, 6, 7, 8, 9, 11, 13}


def phase4_right207_p605_below_anchor_band(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 4
        and row.get("salt_right") == 207
        and row.get("row_pair") in P605_ROW_PAIRS
        and row.get("right_anchor") in P605_BELOW_RHO_ANCHORS
    )


def phase4_mod7_6_right207_p605_below_anchor_band(row: p594.Feature) -> bool:
    return phase4_right207_p605_below_anchor_band(row) and p594.mod7(row) == 6


def phase4_right207_p605_verified_anchor_band(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 4
        and row.get("salt_right") == 207
        and row.get("row_pair") in P605_ROW_PAIRS
        and row.get("right_anchor") in P605_VERIFIED_ANCHORS
    )


def phase4_right207_p605_anchor13(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 4
        and row.get("salt_right") == 207
        and row.get("row_pair") in P605_ROW_PAIRS
        and row.get("right_anchor") == 13
    )


def right207_p605_below_anchor_band_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("row_pair") in P605_ROW_PAIRS
        and row.get("right_anchor") in P605_BELOW_RHO_ANCHORS
    )


def right207_p605_verified_anchor_band_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("row_pair") in P605_ROW_PAIRS
        and row.get("right_anchor") in P605_VERIFIED_ANCHORS
    )


def phase4_broad_right207_salt207(row: p594.Feature) -> bool:
    return p594.phase(row) == 4 and row.get("salt_right") == 207 and row.get("row_pair") in P605_ROW_PAIRS


def broad_right207_salt207(row: p594.Feature) -> bool:
    return row.get("salt_right") == 207 and row.get("row_pair") in P605_ROW_PAIRS


def phase4_anchor_band_all_rights(row: p594.Feature) -> bool:
    return p594.phase(row) == 4 and row.get("right_anchor") in P605_BELOW_RHO_ANCHORS


def phase5_mod7_6_right206_anchor7_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 5
        and p594.mod7(row) == 6
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 7
        and row.get("row_pair") == "salt204_salt206"
    )


def phase8_mod7_2_right206_anchor9_salt204(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and p594.mod7(row) == 2
        and row.get("salt_right") == 206
        and row.get("right_anchor") == 9
        and row.get("row_pair") == "salt204_salt206"
    )


def p610_exact_surface_union(row: p594.Feature) -> bool:
    return phase5_mod7_6_right206_anchor7_salt204(row) or phase8_mod7_2_right206_anchor9_salt204(row)


def right206_salt204_anchor7_or9_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 206
        and row.get("row_pair") == "salt204_salt206"
        and row.get("right_anchor") in {7, 9}
    )


def right206_salt204_all_anchors_all_phases(row: p594.Feature) -> bool:
    return row.get("salt_right") == 206 and row.get("row_pair") == "salt204_salt206"


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p612_phase4_mod7_6_right207_p605_below_anchor_band_exact",
            "Primary exact P605 recurrence: phase4/mod7=6/right207 below-rho anchor band; expected transfer 21412",
            phase4_mod7_6_right207_p605_below_anchor_band,
        ),
        (
            "p612_phase4_right207_p605_below_anchor_band",
            "P605 phase4/right207 below-rho anchor band across all mod7 residues",
            phase4_right207_p605_below_anchor_band,
        ),
        (
            "p612_phase4_right207_p605_verified_anchor_band",
            "P605 phase4/right207 verified anchor band including anchor13",
            phase4_right207_p605_verified_anchor_band,
        ),
        (
            "p612_phase4_right207_p605_anchor13",
            "P605 phase4/right207 anchor13 above-rho control",
            phase4_right207_p605_anchor13,
        ),
        (
            "p612_right207_p605_below_anchor_band_all_phases",
            "P605 below-rho right207/salt207 anchor band across all phases",
            right207_p605_below_anchor_band_all_phases,
        ),
        (
            "p612_right207_p605_verified_anchor_band_all_phases",
            "P605 verified right207/salt207 anchor band across all phases",
            right207_p605_verified_anchor_band_all_phases,
        ),
        (
            "p612_phase4_broad_right207_salt207",
            "phase4/right207 over all P605 salt207 row pairs and anchors",
            phase4_broad_right207_salt207,
        ),
        (
            "p612_broad_right207_salt207",
            "Broad right207/salt207 control over all phases",
            broad_right207_salt207,
        ),
        (
            "p612_phase4_anchor_band_all_rights",
            "phase4 P605 below-rho anchor band over all emitted right-row salts",
            phase4_anchor_band_all_rights,
        ),
        (
            "p612_p610_exact_surface_union",
            "P610 exact right206/salt204 substitution surface union",
            p610_exact_surface_union,
        ),
        (
            "p612_right206_salt204_anchor7_or9_all_phases",
            "P610 right206/salt204 anchors {7,9} across all phases",
            right206_salt204_anchor7_or9_all_phases,
        ),
        (
            "p612_right206_salt204_all_anchors_all_phases",
            "Broad right206/salt204_salt206 control across all anchors and phases",
            right206_salt204_all_anchors_all_phases,
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p605_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p612_validation")
    predicate_reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = predicate_reports[0]
    best_below = p594.best_report(predicate_reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(predicate_reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P612_EXACT_P605_RECURRENCE_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P612_EXACT_P605_RECURRENCE_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P612_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P612_RECURRENCE_CORRIDOR_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P612_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "SOURCE-ONLY SELECTION: predicate rules use public phase, mod7, salt, anchor, row-pair, selector, and policy-role metadata only.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "RECURRENCE BOUNDARY: transfer 21412 is tested as the exact P605 phase4/mod7=6 recurrence point; other recurrences remain outside this block.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, target descent, and individual-log accounting remain separate gates.",
        ],
        "method": "p612_recurrence_corridor_scout",
        "rule_reports": predicate_reports,
        "schema": "ecdlp.low_term_total2_p612_recurrence_corridor_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p605_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p605_direct_verified",
                ),
                "p605_exact_phase4_mod7_6_right207_below_anchor_band": p594.cohort_summary(
                    [row for row in train_rows if phase4_mod7_6_right207_p605_below_anchor_band(row)],
                    "p605_exact_phase4_mod7_6_right207_below_anchor_band",
                ),
                "p605_phase4_right207_below_anchor_band": p594.cohort_summary(
                    [row for row in train_rows if phase4_right207_p605_below_anchor_band(row)],
                    "p605_phase4_right207_below_anchor_band",
                ),
                "p605_phase4_right207_verified_anchor_band": p594.cohort_summary(
                    [row for row in train_rows if phase4_right207_p605_verified_anchor_band(row)],
                    "p605_phase4_right207_verified_anchor_band",
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
