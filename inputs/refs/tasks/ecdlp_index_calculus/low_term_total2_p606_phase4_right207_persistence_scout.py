#!/usr/bin/env python3
"""P606 adjacent persistence scout for the P605 phase4/right207 relation supply.

Rules use source-public metadata only. Direct verifier outcomes are joined only
as labels after selection. The adjacent block tests immediate drift/persistence;
the exact phase4/mod7=6 recurrence from P605 is transfer 21412.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p594_phase10_right207_anchor9_salt206_scout as p594
import low_term_total2_p605_public_context_fingerprint_delta_scout as p605


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p605_public_context_fingerprint_delta_source_21317_21328_probe.json"
DEFAULT_TRAIN_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p605_order9887_public_context_fingerprint_delta_21317_21328_density_gate_probe.json"
)
DEFAULT_P605_SCOUT = STATE_DIR / "low_term_total2_p605_public_context_fingerprint_delta_scout_21317_21328_probe.json"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p606_phase4_right207_persistence_source_21329_21340_probe.json"
DEFAULT_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p606_order9887_phase4_right207_persistence_21329_21340_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p606_phase4_right207_persistence_scout_21329_21340_probe.json"

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


def rule_specs() -> list[tuple[str, str, p594.Predicate]]:
    return [
        (
            "p606_phase4_right207_p605_below_anchor_band",
            "Primary P605 drift branch: phase4/right207 row pairs with below-rho P605 anchors {3,6,7,8,9,11}",
            phase4_right207_p605_below_anchor_band,
        ),
        (
            "p606_phase4_mod7_6_right207_p605_below_anchor_band_exact_recurrence",
            "Exact P605 phase4/mod7=6 recurrence control; expected transfer is 21412, outside adjacent block",
            phase4_mod7_6_right207_p605_below_anchor_band,
        ),
        (
            "p606_phase4_right207_p605_verified_anchor_band",
            "P605 direct-verified anchor band including above-rho anchor13",
            phase4_right207_p605_verified_anchor_band,
        ),
        (
            "p606_phase4_right207_p605_anchor13",
            "P605 direct-verified above-rho anchor13 control",
            phase4_right207_p605_anchor13,
        ),
        (
            "p606_right207_p605_below_anchor_band_all_phases",
            "P605 below-rho anchor band across all phases",
            right207_p605_below_anchor_band_all_phases,
        ),
        (
            "p606_right207_p605_verified_anchor_band_all_phases",
            "P605 direct-verified anchor band across all phases",
            right207_p605_verified_anchor_band_all_phases,
        ),
        (
            "p606_phase4_broad_right207_salt207",
            "phase4/right207 over all P605 salt207 row pairs and all emitted anchors",
            phase4_broad_right207_salt207,
        ),
        (
            "p606_broad_right207_salt207",
            "Broad right207/salt207 control over all phases",
            broad_right207_salt207,
        ),
        (
            "p606_phase4_anchor_band_all_rights",
            "phase4 P605 below-rho anchor band over all emitted right-row salts",
            phase4_anchor_band_all_rights,
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
    pool_rows = [row for row in rows if phase4_broad_right207_salt207(row)]
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
                f"p606_p605_context_token_{index}",
                f"P605 learned context token control over phase4/right207/salt207 pool: {token}",
            )
        )
    return reports


def main() -> int:
    args = parse_args()
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p605_training")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p606_validation")
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
        claim_status = "P606_PHASE4_RIGHT207_P605_ANCHOR_BAND_BELOW_RHO_VALIDATION_POSITIVE"
    elif main_report["direct_verified_count"]:
        claim_status = "P606_PHASE4_RIGHT207_P605_ANCHOR_BAND_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif best_below["direct_below_rho_verified_count"] or best_verified["direct_verified_count"]:
        claim_status = "P606_CONTROL_RULE_VALIDATION_POSITIVE_PRIMARY_MISSED"
    elif validation_summary["direct_verified_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P606_VALIDATION_QUIET_BLOCK"
    else:
        claim_status = "NEGATIVE_RESULT_P606_PRIMARY_MISSED_NONQUIET_BLOCK"
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
            "PRE-HIT CONTEXT: context-token controls are built before direct witness replay over the phase4/right207/salt207 pool.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "CRT BOUNDARY: adjacent block tests drift/persistence, not exact phase4/mod7=6 recurrence; exact repeat is transfer 21412.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and target descent remain separate gates.",
        ],
        "method": "p606_phase4_right207_persistence_scout",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p606_phase4_right207_persistence_scout.v1",
        "summary": {
            "best_below_rho_rule": best_below,
            "best_direct_verified_rule": best_verified,
            "claim_status": claim_status,
            "context_tokens_tested": context_tokens,
            "main_rule": main_report,
            "training_cohorts": {
                "p605_direct_verified": p594.cohort_summary(
                    [row for row in train_rows if row["direct_verified"]],
                    "p605_direct_verified",
                ),
                "p605_phase4_mod7_6_right207_below_anchor_band": p594.cohort_summary(
                    [row for row in train_rows if phase4_mod7_6_right207_p605_below_anchor_band(row)],
                    "p605_phase4_mod7_6_right207_below_anchor_band",
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
