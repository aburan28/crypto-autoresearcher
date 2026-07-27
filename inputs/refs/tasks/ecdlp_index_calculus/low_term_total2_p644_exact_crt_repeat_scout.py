#!/usr/bin/env python3
"""P644 exact CRT repeat scan for P642 phase surfaces."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p643_phase0_salt203_burst_scout as p643


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_GATE = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p644_order9887_exact_crt_repeat_22209_22212_density_gate_probe.json"
)
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p644_exact_crt_repeat_source_22209_22212_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p644_exact_crt_repeat_scout_22209_22212_probe.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def exact_transfer(t: int, pred: Callable[[dict[str, Any]], bool]) -> Callable[[dict[str, Any]], bool]:
    return lambda f: f.get("transfer_index") == t and pred(f)


def t22209_right207_anchor9_salt207_family(f: dict[str, Any]) -> bool:
    return p643.right207_salt207_family(f) and f.get("right_anchor") == 9


def t22209_right207_anchor9_salt203_salt207(f: dict[str, Any]) -> bool:
    return t22209_right207_anchor9_salt207_family(f) and f.get("salt_left") == 203


def t22209_right207_anchor9_salt205_salt207(f: dict[str, Any]) -> bool:
    return t22209_right207_anchor9_salt207_family(f) and f.get("salt_left") == 205


def t22209_right207_anchor9_salt206_salt207(f: dict[str, Any]) -> bool:
    return t22209_right207_anchor9_salt207_family(f) and f.get("salt_left") == 206


def t22211_right207_anchor13_salt207_family(f: dict[str, Any]) -> bool:
    return p643.right207_salt207_family(f) and f.get("right_anchor") == 13


def t22211_right207_anchor13_salt203_salt207(f: dict[str, Any]) -> bool:
    return t22211_right207_anchor13_salt207_family(f) and f.get("salt_left") == 203


def t22212_right207_salt203_salt207(f: dict[str, Any]) -> bool:
    return p643.right207_salt203_salt207(f)


def t22212_right207_anchor9_salt203_salt207(f: dict[str, Any]) -> bool:
    return p643.right207_anchor9_salt203_salt207(f)


def t22212_right208_salt203_salt208(f: dict[str, Any]) -> bool:
    return p643.right208_salt203_salt208(f)


def t22212_salt203_union(f: dict[str, Any]) -> bool:
    return t22212_right207_salt203_salt207(f) or t22212_right208_salt203_salt208(f)


def t22212_broad_right208_salt208(f: dict[str, Any]) -> bool:
    return p643.right208_salt208_family(f)


RULES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    (
        "p644_t22209_phase9_mod7_5_right207_anchor9_salt207_family",
        "Exact repeat of P642 transfer 22125 phase9/mod7=5 right207 anchor9 salt207 row-pair family",
        exact_transfer(22209, t22209_right207_anchor9_salt207_family),
    ),
    (
        "p644_t22209_right207_anchor9_salt203_salt207",
        "Exact repeat row-pair salt203_salt207 at phase9 right207 anchor9",
        exact_transfer(22209, t22209_right207_anchor9_salt203_salt207),
    ),
    (
        "p644_t22209_right207_anchor9_salt205_salt207",
        "Exact repeat row-pair salt205_salt207 at phase9 right207 anchor9",
        exact_transfer(22209, t22209_right207_anchor9_salt205_salt207),
    ),
    (
        "p644_t22209_right207_anchor9_salt206_salt207",
        "Exact repeat row-pair salt206_salt207 at phase9 right207 anchor9",
        exact_transfer(22209, t22209_right207_anchor9_salt206_salt207),
    ),
    (
        "p644_t22211_phase11_mod7_0_right207_anchor13_salt207_family",
        "Exact repeat of P642 transfer 22127 phase11/mod7=0 right207 anchor13 salt207 family",
        exact_transfer(22211, t22211_right207_anchor13_salt207_family),
    ),
    (
        "p644_t22211_right207_anchor13_salt203_salt207_rank3",
        "Exact repeat rank/unique-gain row-pair salt203_salt207 at phase11 right207 anchor13",
        exact_transfer(22211, t22211_right207_anchor13_salt203_salt207),
    ),
    (
        "p644_t22212_phase0_mod7_1_right207_salt203_salt207_all_anchor",
        "Exact repeat of P642 phase0/mod7=1 right207 salt203_salt207 all-anchor burst",
        exact_transfer(22212, t22212_right207_salt203_salt207),
    ),
    (
        "p644_t22212_phase0_mod7_1_right207_anchor9_salt203_salt207_rank3",
        "Exact repeat rank-3 row-pair right207 anchor9 salt203_salt207",
        exact_transfer(22212, t22212_right207_anchor9_salt203_salt207),
    ),
    (
        "p644_t22212_phase0_mod7_1_right208_salt203_salt208_all_anchor",
        "Exact repeat of P642 phase0/mod7=1 right208 salt203_salt208 all-anchor burst",
        exact_transfer(22212, t22212_right208_salt203_salt208),
    ),
    (
        "p644_t22212_phase0_mod7_1_salt203_right207_right208_union",
        "Exact repeat salt203 union across right207 and right208",
        exact_transfer(22212, t22212_salt203_union),
    ),
    (
        "p644_t22212_broad_right208_salt208_all_anchor",
        "Exact repeat broad right208/salt208 control at phase0/mod7=1",
        exact_transfer(22212, t22212_broad_right208_salt208),
    ),
]


def report_named(reports: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((r for r in reports if r["rule"] == name), None)


def determine_claim(reports: list[dict[str, Any]], raw: dict[str, Any]) -> str:
    t22212_anchor9 = report_named(reports, "p644_t22212_phase0_mod7_1_right207_anchor9_salt203_salt207_rank3")
    t22212_right207 = report_named(reports, "p644_t22212_phase0_mod7_1_right207_salt203_salt207_all_anchor")
    t22212_right208 = report_named(reports, "p644_t22212_phase0_mod7_1_right208_salt203_salt208_all_anchor")
    t22209 = report_named(reports, "p644_t22209_phase9_mod7_5_right207_anchor9_salt207_family")
    t22211 = report_named(reports, "p644_t22211_phase11_mod7_0_right207_anchor13_salt207_family")
    if (
        t22212_anchor9
        and t22212_anchor9["direct_below_rho_verified_count"]
        and t22212_anchor9["rank3_direct_verified_count"]
    ):
        return "P644_EXACT_PHASE0_RIGHT207_ANCHOR9_SALT203_RANK3_BELOW_RHO_RECURRENCE"
    if t22212_right207 and t22212_right207["direct_below_rho_verified_count"]:
        return "P644_EXACT_PHASE0_RIGHT207_SALT203_BELOW_RHO_RECURRENCE"
    if t22212_right208 and t22212_right208["direct_below_rho_verified_count"]:
        return "P644_EXACT_PHASE0_RIGHT208_SALT203_BELOW_RHO_RECURRENCE"
    if t22209 and t22209["direct_below_rho_verified_count"]:
        return "P644_EXACT_PHASE9_RIGHT207_ANCHOR9_SALT207_BELOW_RHO_RECURRENCE"
    if t22211 and t22211["rank3_direct_verified_count"]:
        return "P644_EXACT_PHASE11_RIGHT207_ANCHOR13_SALT207_RANK_SURFACE_RECURRENCE"
    if any(r["direct_below_rho_verified_count"] for r in reports):
        return "P644_REGISTERED_EXACT_BELOW_RHO_POSITIVE"
    if any(r["rank3_direct_verified_count"] for r in reports):
        return "P644_REGISTERED_EXACT_RANK_SURFACE_POSITIVE"
    if any(r["direct_verified_count"] for r in reports):
        return "P644_REGISTERED_EXACT_ABOVE_RHO_POSITIVE"
    if raw["direct_verified_count"]:
        return "NEGATIVE_RESULT_P644_EXACT_CONTROLS_MISSED_NONQUIET_BLOCK"
    return "NEGATIVE_RESULT_P644_EXACT_REPEAT_QUIET_BLOCK"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default=str(DEFAULT_GATE))
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    gate = json.loads(Path(args.gate).read_text())
    features = [p643.feature(case) for case in gate.get("cases", [])]
    raw_summary = p643.summarize_cases(features)
    reports = [p643.rule_report(name, desc, pred, features, raw_summary) for name, desc, pred in RULES]
    claim_status = determine_claim(reports, raw_summary)

    payload = {
        "schema": "ecdlp.low_term_total2_p644_exact_crt_repeat_scout.v1",
        "created_at": utc_now(),
        "method": "p644_exact_crt_repeat_scout",
        "claim_status": claim_status,
        "artifacts": {"source": str(args.source), "gate": str(args.gate)},
        "summary": {
            "claim_status": claim_status,
            "validation_dataset": raw_summary,
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
            "Verifier labels are used only for post-run evaluation, not for rule definition.",
            "P644 tests exact CRT repeat transfers for P642 phase surfaces after P643 adjacent quiet.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Rank-3 rows and unique factor-relation gain are relation-bank signals, not solved linear algebra.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, **raw_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
