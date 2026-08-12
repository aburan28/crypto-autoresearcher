#!/usr/bin/env python3
"""P595 exact phase10/mod7=0/right207/anchor9/salt206 holdout scout.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. This block contains the next exact CRT recurrence of
the P593 phase10/mod7=0 pocket at transfer 21070.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = p594.DEFAULT_TRAIN_SOURCE
DEFAULT_TRAIN_GATE = p594.DEFAULT_TRAIN_GATE
DEFAULT_SOURCE = (
    STATE_DIR / "low_term_total2_order9887_p595_phase10_mod7_0_right207_anchor9_salt206_exact_crt_source_21065_21076_probe.json"
)
DEFAULT_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p595_order9887_phase10_mod7_0_right207_anchor9_salt206_exact_crt_21065_21076_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p595_phase10_mod7_0_right207_anchor9_salt206_scout_21065_21076_probe.json"


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p595_exact_phase10_mod7_0_right207_anchor9_salt206",
            "Primary exact-CRT P593 pocket: phase10/mod7=0/right207/anchor9/salt206_salt207",
            p594.phase10_mod7_0_right207_anchor9_salt206,
        ),
        (
            "p595_phase10_right207_anchor9_salt206_all_mod7",
            "P593 pocket without mod7 restriction: phase10/right207/anchor9/salt206_salt207",
            p594.primary_phase10_right207_anchor9_salt206,
        ),
        (
            "p595_phase10_right207_anchor9_all_pairs",
            "phase10/right207/anchor9 across emitted salt207 row pairs",
            p594.phase10_right207_anchor9_all_pairs,
        ),
        (
            "p595_phase10_right207_anchor_band",
            "phase10/right207 anchor band {3,6,9,13}",
            p594.phase10_right207_anchor_band,
        ),
        (
            "p595_right207_anchor9_all_phases",
            "right207/anchor9 across all phases",
            p594.right207_anchor9_all_phases,
        ),
        (
            "p595_right207_anchor_band_all_phases",
            "right207 anchor band {3,6,9,13} across all phases",
            p594.right207_anchor_band_all_phases,
        ),
        (
            "p595_broad_salt206_replay",
            "Broad salt206 row-pair replay control",
            p594.broad_salt206_replay,
        ),
        (
            "p595_phase10_anchor9_all_rowpairs",
            "phase10/anchor9 across all emitted row pairs",
            p594.phase10_anchor9_all_rowpairs,
        ),
        (
            "p595_stale_phase3_mod7_0_right207_anchor9",
            "Failed P593 primary family as stale-family control",
            p594.stale_phase3_mod7_0_right207_anchor9,
        ),
        (
            "p595_failed_phase9_right208_anchor7",
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
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p593_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p595_validation")
    reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    best_below = p594.best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P595_EXACT_PHASE10_MOD7_0_RIGHT207_ANCHOR9_SALT206_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P595_EXACT_PHASE10_MOD7_0_RIGHT207_ANCHOR9_SALT206_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P595_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P595_EXACT_CRT_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P595_EXACT_CRT_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "EXACT-CRT BOUNDARY: this block tests the next phase10/mod7=0 recurrence at transfer 21070.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p595_exact_phase10_mod7_0_right207_anchor9_salt206_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p595_phase10_mod7_0_right207_anchor9_salt206_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "main_rule": main_report,
            "training_cohorts": {
                "p593_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p593_direct_verified",
                ),
                "p593_exact_phase10_mod7_0_pocket": p594.cohort_summary(
                    [row for row in train_rows if p594.phase10_mod7_0_right207_anchor9_salt206(row)],
                    "p593_exact_phase10_mod7_0_pocket",
                ),
                "p593_phase10_right207_anchor9_salt206": p594.cohort_summary(
                    [row for row in train_rows if p594.primary_phase10_right207_anchor9_salt206(row)],
                    "p593_phase10_right207_anchor9_salt206",
                ),
                "p593_right207_anchor9_all_phases": p594.cohort_summary(
                    [row for row in train_rows if p594.right207_anchor9_all_phases(row)],
                    "p593_right207_anchor9_all_phases",
                ),
                "p593_broad_salt206": p594.cohort_summary(
                    [row for row in train_rows if p594.broad_salt206_replay(row)],
                    "p593_broad_salt206",
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
