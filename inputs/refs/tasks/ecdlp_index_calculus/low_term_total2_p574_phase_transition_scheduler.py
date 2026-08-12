#!/usr/bin/env python3
"""Explicit phase-transition source scheduler for order-9887 leaf-16 routing."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p570_pre_hit_source_feature_scout as p570


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p574_leaf16_phase_transition_source_20689_20700_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p574_order9887_phase_transition_20689_20700_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p574_phase_transition_scheduler_20689_20700_probe.json"

Feature = dict[str, Any]
Predicate = Callable[[Feature], bool]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 8)


def right208_anchor3(row: Feature) -> bool:
    return row.get("salt_right") == 208 and row.get("right_anchor") == 3


def phase_in(phases: set[int]) -> Predicate:
    return lambda row: int(row.get("transfer_mod12") or -1) in phases


def all_of(*parts: Predicate) -> Predicate:
    return lambda row: all(part(row) for part in parts)


def rule_specs() -> list[tuple[str, str, Predicate]]:
    return [
        (
            "phase_transition_union_2_6_11_right208_anchor3",
            "right salt=208, anchor=3, phase in {2,6,11}; tests +3, +7, and repeat phase from P572",
            all_of(right208_anchor3, phase_in({2, 6, 11})),
        ),
        (
            "phase_plus3_to2_right208_anchor3",
            "right salt=208, anchor=3, phase=2 from P572 phase 11 plus 3 modulo 12",
            all_of(right208_anchor3, phase_in({2})),
        ),
        (
            "phase_plus7_to6_right208_anchor3",
            "right salt=208, anchor=3, phase=6 from P572 phase 11 plus 7 modulo 12",
            all_of(right208_anchor3, phase_in({6})),
        ),
        (
            "phase_repeat11_right208_anchor3",
            "right salt=208, anchor=3, phase=11 repeat of P572 family",
            all_of(right208_anchor3, phase_in({11})),
        ),
        (
            "right208_anchor3_all_phases",
            "right salt=208, anchor=3, all phases; broad source-only control",
            right208_anchor3,
        ),
        (
            "historical_right207_phase1or6",
            "right salt=207, phase in {1,6}; historical P566/P567/P568 control",
            lambda row: row.get("salt_right") == 207 and int(row.get("transfer_mod12") or -1) in {1, 6},
        ),
    ]


def compact_row(row: Feature) -> dict[str, Any]:
    return {
        "base_selector": row["base_selector"],
        "case_entry": row["case_entry"],
        "direct_below_rho_verified": row["direct_below_rho_verified"],
        "direct_ops_over_rho": row["direct_ops_over_rho"],
        "leaf_signature": row["leaf_signature"],
        "policy_role": row["policy_role"],
        "right_anchor": row["right_anchor"],
        "row_pair": row["row_pair"],
        "salt_left": row["salt_left"],
        "salt_right": row["salt_right"],
        "selector": row["selector"],
        "top_k": row["top_k"],
        "transfer_index": row["transfer_index"],
        "transfer_mod12": row["transfer_mod12"],
        "transfer_mod7": row["transfer_mod7"],
    }


def report(rows: list[Feature], selected: list[Feature], name: str, description: str) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    selected_positive = [row for row in selected if row["direct_below_rho_verified"]]
    return {
        "description": description,
        "direct_below_rho_verified_count": len(selected_positive),
        "direct_below_rho_verified_precision": ratio(len(selected_positive), len(selected)),
        "direct_below_rho_verified_recall": ratio(len(selected_positive), len(positives)),
        "examples": [compact_row(row) for row in selected[:12]],
        "positive_examples": [compact_row(row) for row in selected_positive[:12]],
        "raw_positive_count": len(positives),
        "row_pair_counts": dict(Counter(str(row["row_pair"]) for row in selected).most_common(16)),
        "rule": name,
        "selected_case_entries": [row["case_entry"] for row in selected],
        "selected_direct_below_rho_verified_case_entries": [row["case_entry"] for row in selected_positive],
        "selected_count": len(selected),
        "selected_fraction": ratio(len(selected), len(rows)),
        "transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in selected).items(), key=lambda item: int(item[0]))
        ),
    }


def dataset_summary(rows: list[Feature]) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    return {
        "case_count": len(rows),
        "direct_below_rho_verified_count": len(positives),
        "direct_verified_count": sum(1 for row in rows if row["direct_verified"]),
        "positive_phase_salt_counts": dict(
            Counter(f"{row.get('transfer_mod12')}:{row.get('salt_right')}" for row in positives).most_common()
        ),
        "positive_transfer_counts": dict(
            sorted(Counter(str(row["transfer_index"]) for row in positives).items(), key=lambda item: int(item[0]))
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = p570.source_rows([args.source], p570.gate_labels([args.gate]), "validation")
    reports = [
        report(rows, [row for row in rows if predicate(row)], name, description)
        for name, description, predicate in rule_specs()
    ]
    main_report = reports[0]
    payload = {
        "artifacts": {"gate": str(args.gate), "source": str(args.source)},
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: phase-transition rules use transfer phase, row salt, and anchor only.",
            "LABEL BOUNDARY: direct verifier outcomes are joined only for evaluation.",
            "HEURISTIC: phase transitions are empirical scheduler hypotheses, not algebraic claims.",
            "NO SPEEDUP CLAIM: relation collection, linear algebra, target descent, and costs remain open.",
        ],
        "method": "p574_phase_transition_source_scheduler",
        "rule_reports": reports,
        "schema": "ecdlp.low_term_total2_p574_phase_transition_scheduler.v1",
        "summary": {
            "claim_status": (
                "PHASE_TRANSITION_SOURCE_SCHEDULER_VALIDATION_POSITIVE"
                if main_report["direct_below_rho_verified_count"]
                else "NEGATIVE_RESULT_PHASE_TRANSITION_SOURCE_SCHEDULER_NO_VALIDATION_POSITIVE"
            ),
            "dataset": dataset_summary(rows),
            "main_rule": main_report,
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
