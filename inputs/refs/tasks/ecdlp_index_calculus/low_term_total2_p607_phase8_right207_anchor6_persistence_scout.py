#!/usr/bin/env python3
"""P607 adjacent persistence scout for the P606 phase8/right207/anchor6 family.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. The adjacent block tests immediate drift/persistence;
the exact phase8/mod7=3 recurrence from P606 is transfer 21416.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594
import low_term_total2_p605_public_context_fingerprint_delta_scout as p605
import low_term_total2_p606_phase4_right207_persistence_scout as p606


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p606_phase4_right207_persistence_source_21329_21340_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p606_order9887_phase4_right207_persistence_21329_21340_density_gate_probe.json"
)
DEFAULT_P605_SCOUT = STATE_DIR / "low_term_total2_p605_public_context_fingerprint_delta_scout_21317_21328_probe.json"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p607_phase8_right207_anchor6_source_21341_21352_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p607_order9887_phase8_right207_anchor6_21341_21352_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p607_phase8_right207_anchor6_scout_21341_21352_probe.json"

P606_VERIFIED_ROW_PAIRS = {
    "salt203_salt207",
    "salt205_salt207",
    "salt206_salt207",
}
P606_BELOW_RHO_ROW_PAIRS = {
    "salt205_salt207",
    "salt206_salt207",
}


def phase8_right207_anchor6_verified_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 6
        and row.get("row_pair") in P606_VERIFIED_ROW_PAIRS
    )


def phase8_mod7_3_right207_anchor6_verified_pairs(row: p594.Feature) -> bool:
    return phase8_right207_anchor6_verified_pairs(row) and p594.mod7(row) == 3


def phase8_right207_anchor6_below_pairs(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 207
        and row.get("right_anchor") == 6
        and row.get("row_pair") in P606_BELOW_RHO_ROW_PAIRS
    )


def phase8_mod7_3_right207_anchor6_below_pairs(row: p594.Feature) -> bool:
    return phase8_right207_anchor6_below_pairs(row) and p594.mod7(row) == 3


def right207_anchor6_verified_pairs_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("right_anchor") == 6
        and row.get("row_pair") in P606_VERIFIED_ROW_PAIRS
    )


def right207_anchor6_below_pairs_all_phases(row: p594.Feature) -> bool:
    return (
        row.get("salt_right") == 207
        and row.get("right_anchor") == 6
        and row.get("row_pair") in P606_BELOW_RHO_ROW_PAIRS
    )


def phase8_right207_p605_anchor_band(row: p594.Feature) -> bool:
    return (
        p594.phase(row) == 8
        and row.get("salt_right") == 207
        and row.get("row_pair") in P606_VERIFIED_ROW_PAIRS
        and row.get("right_anchor") in p606.P605_BELOW_RHO_ANCHORS
    )


def broad_right207_anchor6_all_rowpairs(row: p594.Feature) -> bool:
    return row.get("salt_right") == 207 and row.get("right_anchor") == 6


def broad_right207_salt207(row: p594.Feature) -> bool:
    return row.get("salt_right") == 207 and row.get("row_pair") in P606_VERIFIED_ROW_PAIRS


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p607_phase8_right207_anchor6_verified_pairs",
            "Primary P606 drift branch: phase8/right207/anchor6 over all P606 direct-verified row pairs",
            phase8_right207_anchor6_verified_pairs,
        ),
        (
            "p607_phase8_mod7_3_right207_anchor6_verified_pairs_exact_recurrence",
            "Exact P606 phase8/mod7=3 recurrence control; expected transfer is 21416, outside adjacent block",
            phase8_mod7_3_right207_anchor6_verified_pairs,
        ),
        (
            "p607_phase8_right207_anchor6_below_pairs",
            "P606 below-rho row-pair split: phase8/right207/anchor6 over salt205_salt207 and salt206_salt207",
            phase8_right207_anchor6_below_pairs,
        ),
        (
            "p607_phase8_mod7_3_right207_anchor6_below_pairs_exact_recurrence",
            "Exact P606 below-rho row-pair split recurrence control",
            phase8_mod7_3_right207_anchor6_below_pairs,
        ),
        (
            "p607_right207_anchor6_verified_pairs_all_phases",
            "P606 right207/anchor6 direct-verified row pairs across all phases",
            right207_anchor6_verified_pairs_all_phases,
        ),
        (
            "p607_right207_anchor6_below_pairs_all_phases",
            "P606 right207/anchor6 below-rho row-pair split across all phases",
            right207_anchor6_below_pairs_all_phases,
        ),
        (
            "p607_phase8_right207_p605_anchor_band",
            "phase8/right207 over P605 below-rho anchor band and P606 row pairs",
            phase8_right207_p605_anchor_band,
        ),
        (
            "p607_broad_right207_anchor6_all_rowpairs",
            "Broad right207/anchor6 across all emitted row pairs and phases",
            broad_right207_anchor6_all_rowpairs,
        ),
        (
            "p607_broad_right207_salt207",
            "Broad right207/salt207 row-pair control across all phases",
            broad_right207_salt207,
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-source", type=Path, default=DEFAULT_TRAIN_SOURCE)
    parser.add_argument("--train-gate", type=Path, default=DEFAULT_TRAIN_GATE)
    parser.add_argument("--p605-scout", type=Path, default=DEFAULT_P605_SCOUT)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--context-token-count", type=int, default=5)
    return parser.parse_args()


def p605_top_tokens(path: Path, count: int) -> list[str]:
    payload = json.loads(path.read_text()) if path.exists() else {}
    tokens = (payload.get("summary") or {}).get("top_candidate_tokens") or []
    return [str(item["token"]) for item in tokens[: max(0, count)] if isinstance(item, dict) and item.get("token")]


def context_token_reports(
    rows: list[p594.Feature],
    source_path: Path,
    tokens: list[str],
) -> list[dict[str, Any]]:
    if not tokens:
        return []
    cache = p605.source_data([source_path])
    pool_rows = [row for row in rows if phase8_right207_anchor6_verified_pairs(row)]
    profiles = [p605.context_tokens(cache, row) for row in pool_rows]
    reports: list[dict[str, Any]] = []
    for index, token in enumerate(tokens, start=1):
        selected_entries = {
            profile["case_entry"]
            for profile in profiles
            if token in set(profile.get("portable_tokens") or [])
        }
        selected_rows = [row for row in rows if row["case_entry"] in selected_entries]
        reports.append(
            p594.report(
                rows,
                selected_rows,
                f"p607_p605_context_token_{index}",
                f"P605 learned context token control over phase8/right207/anchor6 pool: {token}",
            )
        )
    return reports


def main() -> int:
    args = parse_args()
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p606_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p607_validation")
    predicate_reports = [
        p594.report(validation_rows, [row for row in validation_rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    context_tokens = p605_top_tokens(args.p605_scout, args.context_token_count)
    context_reports = context_token_reports(validation_rows, args.source, context_tokens)
    reports = [*predicate_reports, *context_reports]
    main_report = predicate_reports[0]
    best_below = p594.best_report(reports, main_report, "direct_below_rho_verified_count")
    best_verified = p594.best_report(reports, main_report, "direct_verified_count")
    validation_summary = p594.dataset_summary(validation_rows)
    if main_report["direct_below_rho_verified_count"]:
        claim_status = "P607_PHASE8_RIGHT207_ANCHOR6_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P607_PHASE8_RIGHT207_ANCHOR6_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P607_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P607_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P607_PRIMARY_MISSED_NONQUIET_BLOCK"
    payload: dict[str, Any] = {
        "artifacts": {
            "gate": str(args.gate),
            "p605_scout": str(args.p605_scout),
            "source": str(args.source),
            "train_gate": str(args.train_gate),
            "train_source": str(args.train_source),
        },
        "claim_status": claim_status,
        "created_at": p594.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: predicate rules use public phase, mod7, salt, anchor, row-pair, selector, and policy-role metadata only.",
            "PRE-HIT CONTEXT: context-token controls are built before direct witness replay over the phase8/right207/anchor6 pool.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "CRT BOUNDARY: adjacent block tests drift/persistence, not exact phase8/mod7=3 recurrence; exact repeat is transfer 21416.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p607_phase8_right207_anchor6_persistence_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p607_phase8_right207_anchor6_persistence_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "context_tokens_tested": context_tokens,
            "main_rule": main_report,
            "training_cohorts": {
                "p606_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p606_direct_verified",
                ),
                "p606_phase8_right207_anchor6_verified_pairs": p594.cohort_summary(
                    [row for row in train_rows if phase8_right207_anchor6_verified_pairs(row)],
                    "p606_phase8_right207_anchor6_verified_pairs",
                ),
                "p606_phase8_right207_anchor6_below_pairs": p594.cohort_summary(
                    [row for row in train_rows if phase8_right207_anchor6_below_pairs(row)],
                    "p606_phase8_right207_anchor6_below_pairs",
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
