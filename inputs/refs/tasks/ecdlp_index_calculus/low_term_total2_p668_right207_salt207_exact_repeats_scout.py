#!/usr/bin/env python3
"""P668 exact-repeat validation for P665/P666 right207/salt207 positives."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p667_right207_salt207_drift_family_scout as p667


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p668_order9887_right207_salt207_exact_repeats_22469_22491_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p668_right207_salt207_exact_repeats_source_22469_22491_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p668_right207_salt207_exact_repeats_scout_22469_22491_probe.json"
REPEAT_TRANSFERS = (22469, 22474, 22487, 22491)


def at_transfer(transfer_index: int, pred: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    def wrapped(f: dict[str, Any]) -> bool:
        return f.get("transfer_index") == transfer_index and pred(f)

    return wrapped


def transfer_right207_salt207(transfer_index: int) -> Callable[[dict[str, Any]], bool]:
    return at_transfer(transfer_index, p667.p666.right207_salt207)


def phase_mod_union(phase: int, mod7: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return p667.p666.right207_salt207(f) and f.get("transfer_mod12") == phase and f.get("transfer_mod7") == mod7

    return pred


def phase_mod_anchor_pred(phase: int, mod7: int, anchor: int) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        return (
            p667.p666.right207_salt207(f)
            and f.get("transfer_mod12") == phase
            and f.get("transfer_mod7") == mod7
            and f.get("right_anchor") == anchor
        )

    return pred


def phase_mod_anchor_row_pair_pred(
    phase: int, mod7: int, anchor: int | None, salt_left: int
) -> Callable[[dict[str, Any]], bool]:
    def pred(f: dict[str, Any]) -> bool:
        if not p667.p666.salt207_row_pair(salt_left)(f):
            return False
        if f.get("transfer_mod12") != phase or f.get("transfer_mod7") != mod7:
            return False
        return anchor is None or f.get("right_anchor") == anchor

    return pred


EXACT_SURFACES: list[tuple[str, int, int, int, int | None, str]] = [
    ("p665_t22469_phase5_mod7_6_anchor6", 22469, 5, 6, 6, "P665 transfer-22385 +84 phase5/mod7=6 anchor6 repeat"),
    ("p665_t22474_phase10_mod7_4_all_anchor", 22474, 10, 4, None, "P665 transfer-22390 +84 phase10/mod7=4 broad-anchor repeat"),
    ("p666_t22487_phase11_mod7_3_anchor6", 22487, 11, 3, 6, "P666 transfer-22403 +84 phase11/mod7=3 anchor6 repeat"),
    ("p666_t22491_phase3_mod7_0_anchor12", 22491, 3, 0, 12, "P666 transfer-22407 +84 phase3/mod7=0 anchor12 repeat"),
]


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = []

for slug, transfer_index, phase, mod7, anchor, description in EXACT_SURFACES:
    base = phase_mod_union(phase, mod7) if anchor is None else phase_mod_anchor_pred(phase, mod7, anchor)
    RULES.append((f"p668_{slug}_right207_salt207", f"{description} right207/salt207 union", at_transfer(transfer_index, base)))
    RULES.append(
        (
            f"p668_t{transfer_index}_broad_right207_salt207",
            f"Transfer {transfer_index} broad right207/salt207 control",
            transfer_right207_salt207(transfer_index),
        )
    )
    for salt_left in sorted(p667.p666.SALT207_LEFTS):
        row_pred = phase_mod_anchor_row_pair_pred(phase, mod7, anchor, salt_left)
        RULES.append(
            (
                f"p668_{slug}_salt{salt_left}_salt207",
                f"{description} salt{salt_left}_salt207 split",
                at_transfer(transfer_index, row_pred),
            )
        )

RULES.append(
    (
        "p668_all_exact_repeat_right207_salt207_union",
        "All P665/P666 exact repeat transfers broad right207/salt207 union",
        lambda f: f.get("transfer_index") in REPEAT_TRANSFERS and p667.p666.right207_salt207(f),
    )
)


def report_named(reports: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((r for r in reports if r["rule"] == name), None)


def determine_claim(
    reports: list[dict[str, Any]],
    raw: dict[str, Any],
    claim_prefix: str,
    quiet_claim: str,
) -> str:
    exact_positive = [
        r
        for r in reports
        if not r["rule"].endswith("_broad_right207_salt207")
        and r["rule"] != "p668_all_exact_repeat_right207_salt207_union"
        and (r["direct_below_rho_verified_count"] or r["rank3_direct_verified_count"])
    ]
    broad = report_named(reports, "p668_all_exact_repeat_right207_salt207_union")
    if any(r["direct_below_rho_verified_count"] and r["rank3_direct_verified_count"] for r in exact_positive):
        return f"{claim_prefix}_EXACT_REPEAT_BELOW_RHO_RANK3_POSITIVE"
    if any(r["direct_below_rho_verified_count"] for r in exact_positive):
        return f"{claim_prefix}_EXACT_REPEAT_BELOW_RHO_POSITIVE"
    if any(r["rank3_direct_verified_count"] for r in exact_positive):
        return f"{claim_prefix}_EXACT_REPEAT_RANK3_POSITIVE"
    if p667.p666.p665.has_below(broad):
        return f"{claim_prefix}_BROAD_EXACT_REPEAT_BELOW_RHO_DRIFT"
    if p667.p666.p665.has_rank3(broad):
        return f"{claim_prefix}_BROAD_EXACT_REPEAT_RANK3_DRIFT"
    if any(r["direct_below_rho_verified_count"] for r in reports):
        return f"{claim_prefix}_REGISTERED_BELOW_RHO_POSITIVE"
    if any(r["rank3_direct_verified_count"] for r in reports):
        return f"{claim_prefix}_REGISTERED_RANK_SURFACE_POSITIVE"
    if any(r["direct_verified_count"] for r in reports):
        return f"{claim_prefix}_REGISTERED_ABOVE_RHO_POSITIVE"
    if raw["direct_verified_count"]:
        return f"NEGATIVE_RESULT_{claim_prefix}_REGISTERED_CONTROLS_MISSED_NONQUIET_BLOCK"
    return quiet_claim


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default=str(DEFAULT_GATE))
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--claim-prefix", default="P668")
    parser.add_argument("--quiet-claim", default="NEGATIVE_RESULT_P668_RIGHT207_SALT207_EXACT_REPEATS_QUIET")
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p667.p666.p665.p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p667.p666.p665.summarize_cases(features)
    reports = [p667.p666.p665.rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary, args.claim_prefix, args.quiet_claim)

    payload = {
        "schema": "ecdlp.low_term_total2_p668_right207_salt207_exact_repeats_scout.v1",
        "created_at": p667.p666.p665.utc_now(),
        "method": "p668_right207_salt207_exact_repeats_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
            "public_feature_counts": p667.p666.p665.public_feature_counts(features),
            "best_below_rho_rule": max(
                reports,
                key=lambda r: (
                    r["direct_below_rho_verified_count"],
                    r["direct_below_rho_verified_precision"],
                    -r["selected_count"],
                ),
            ),
            "best_direct_verified_rule": max(
                reports,
                key=lambda r: (
                    r["direct_verified_count"],
                    r["direct_verified_precision"],
                    -r["selected_count"],
                ),
            ),
            "best_rank3_rule": max(
                reports,
                key=lambda r: (
                    r["rank3_direct_verified_count"],
                    r["direct_verified_precision"],
                    -r["selected_count"],
                ),
            ),
        },
        "rule_reports": reports,
        "honesty_boundary": [
            "Verifier labels are used only after public selector evaluation.",
            "P668 tests exact-repeat recurrence for P665/P666 right207/salt207 positives.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Above-rho substitution recovery is bounded relation-bank evidence, not arbitrary target descent.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
