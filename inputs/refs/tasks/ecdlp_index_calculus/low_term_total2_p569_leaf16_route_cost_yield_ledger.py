#!/usr/bin/env python3
"""Aggregate P566/P567/P568 leaf-16 route yield and cost-proxy evidence."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p569_leaf16_route_cost_yield_20605_20640_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 8)


def gate_summary(gate: dict[str, Any]) -> dict[str, Any]:
    cases = [case for case in gate.get("cases") or [] if isinstance(case, dict)]
    raw = [case for case in cases if case.get("direct_below_rho") and case.get("direct_union_public_key_verified")]
    selected = [case for case in cases if case.get("public_product_gate_selected")]
    best_direct = sorted(
        (
            float(case.get("direct_verifier_replay_ops_over_rho"))
            for case in raw
            if case.get("direct_verifier_replay_ops_over_rho") is not None
        )
    )
    return {
        "case_count": len(cases),
        "product_gate_selected_count": len(selected),
        "raw_direct_below_rho_verified_count": len(raw),
        "raw_direct_best_ops_over_rho": best_direct[0] if best_direct else None,
        "raw_transfer_counts": dict(
            sorted(Counter(str(case.get("transfer_index")) for case in raw).items(), key=lambda item: int(item[0]))
        ),
    }


def route_summary(route: dict[str, Any], rule_name: str) -> dict[str, Any]:
    reports = route.get("validation_rule_reports") or []
    report = next((item for item in reports if item.get("rule") == rule_name), {})
    return {
        "route_direct_below_rho_verified_count": int_value(report.get("direct_below_rho_verified_count")),
        "route_direct_below_rho_verified_precision": report.get("direct_below_rho_verified_precision"),
        "route_direct_verified_count": int_value(report.get("direct_verified_count")),
        "route_rule": rule_name,
        "route_selected_count": int_value(report.get("selected_count")),
        "route_selected_fraction": report.get("selected_fraction"),
        "route_transfer_counts": report.get("transfer_counts") or {},
    }


def certificate_summary(certs: dict[str, Any]) -> dict[str, Any]:
    summary = certs.get("summary") if isinstance(certs.get("summary"), dict) else {}
    return {
        "certificate_count": int_value(summary.get("certificate_count")),
        "passing_certificate_count": int_value(summary.get("passing_certificate_count")),
    }


def family_summary(holdout: dict[str, Any]) -> dict[str, Any]:
    summary = holdout.get("summary") if isinstance(holdout.get("summary"), dict) else {}
    family_counts = {}
    for report in holdout.get("reports") or []:
        if not isinstance(report, dict):
            continue
        family = report.get("family")
        key = ",".join(str(item) for item in family) if isinstance(family, list) else str(report.get("family_key"))
        family_counts[key] = {
            "candidate_form_count": int_value(report.get("candidate_form_count")),
            "false_recoverable_form_count": int_value(report.get("false_recoverable_form_count")),
            "verified_recoverable_form_count": int_value(report.get("verified_recoverable_form_count")),
        }
    return {
        "candidate_form_count": int_value(summary.get("candidate_form_count")),
        "family_count": int_value(summary.get("family_count")),
        "family_split": family_counts,
        "false_recoverable_form_count": int_value(summary.get("false_recoverable_form_count")),
        "positive_family_count": int_value(summary.get("positive_family_count")),
        "verified_recoverable_form_count": int_value(summary.get("verified_recoverable_form_count")),
    }


def block_report(
    name: str,
    gate_path: Path,
    route_path: Path | None,
    route_rule: str | None,
    cert_path: Path,
    holdout_path: Path,
) -> dict[str, Any]:
    gate = load_json(gate_path)
    certs = load_json(cert_path)
    holdout = load_json(holdout_path)
    report = {
        "artifacts": {
            "certificates": str(cert_path),
            "gate": str(gate_path),
            "route": str(route_path) if route_path else None,
            "family_holdout": str(holdout_path),
        },
        "block": name,
        **gate_summary(gate),
        **certificate_summary(certs),
        **family_summary(holdout),
    }
    if route_path and route_rule:
        report.update(route_summary(load_json(route_path), route_rule))
    else:
        report.update(
            {
                "route_direct_below_rho_verified_count": 0,
                "route_direct_below_rho_verified_precision": None,
                "route_direct_verified_count": 0,
                "route_rule": None,
                "route_selected_count": 0,
                "route_selected_fraction": None,
                "route_transfer_counts": {},
            }
        )
    return report


def aggregate(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    totals = Counter()
    family_totals: Counter[str] = Counter()
    family_false: Counter[str] = Counter()
    for block in blocks:
        for key in [
            "case_count",
            "product_gate_selected_count",
            "raw_direct_below_rho_verified_count",
            "route_selected_count",
            "route_direct_below_rho_verified_count",
            "certificate_count",
            "passing_certificate_count",
            "verified_recoverable_form_count",
            "false_recoverable_form_count",
        ]:
            totals[key] += int_value(block.get(key))
        for family, item in (block.get("family_split") or {}).items():
            family_totals[family] += int_value(item.get("verified_recoverable_form_count"))
            family_false[family] += int_value(item.get("false_recoverable_form_count"))
    return {
        "case_count": totals["case_count"],
        "certificate_count": totals["certificate_count"],
        "false_recoverable_form_count": totals["false_recoverable_form_count"],
        "family_verified_recoverable_form_totals": dict(sorted(family_totals.items())),
        "family_false_recoverable_form_totals": dict(sorted(family_false.items())),
        "passing_certificate_count": totals["passing_certificate_count"],
        "product_gate_selected_count": totals["product_gate_selected_count"],
        "raw_direct_below_rho_verified_count": totals["raw_direct_below_rho_verified_count"],
        "raw_direct_yield_per_case": ratio(totals["raw_direct_below_rho_verified_count"], totals["case_count"]),
        "route_direct_below_rho_verified_count": totals["route_direct_below_rho_verified_count"],
        "route_precision_over_selected": ratio(
            totals["route_direct_below_rho_verified_count"], totals["route_selected_count"]
        ),
        "route_selected_count": totals["route_selected_count"],
        "route_selected_fraction": ratio(totals["route_selected_count"], totals["case_count"]),
        "verified_recoverable_form_count": totals["verified_recoverable_form_count"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    blocks = [
        block_report(
            "p566_raw_validation",
            STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p566_order9887_leaf16_frozen_root_saved_20605_20616_density_gate_probe.json",
            STATE_DIR / "low_term_total2_p566_frozen_root_saved_rule_validation_20605_20616_probe.json",
            "root_saved_high_hit_candidate_7_13",
            STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p566_raw_leaf16_20605_20616_probe.json",
            STATE_DIR / "low_term_total2_factor_substitution_family_holdout_scout_p566_raw_leaf16_20605_20616_probe.json",
        ),
        block_report(
            "p567_raw_validation",
            STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p567_order9887_phase_route_20617_20628_density_gate_probe.json",
            STATE_DIR / "low_term_total2_p567_phase_route_predictor_validation_20617_20628_probe.json",
            "phase_route_union_v1",
            STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p567_raw_leaf16_20617_20628_probe.json",
            STATE_DIR / "low_term_total2_factor_substitution_family_holdout_scout_p567_raw_leaf16_20617_20628_probe.json",
        ),
        block_report(
            "p568_right207_route_validation",
            STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p568_order9887_right207_volume_20629_20640_density_gate_probe.json",
            STATE_DIR / "low_term_total2_p568_right207_volume_predictor_validation_20629_20640_probe.json",
            "right207_phase1or6_hit1",
            STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_p568_selected_right207_20629_20640_probe.json",
            STATE_DIR / "low_term_total2_factor_substitution_family_holdout_scout_p568_selected_right207_20629_20640_probe.json",
        ),
    ]
    summary = aggregate(blocks)
    payload = {
        "blocks": blocks,
        "claim_status": (
            "LEAF16_ROUTE_YIELD_LEDGER_READY_COST_BOTTLENECK_OPEN"
            if summary["route_direct_below_rho_verified_count"] and not summary["false_recoverable_form_count"]
            else "LEAF16_ROUTE_YIELD_LEDGER_NEEDS_REVIEW"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "MODEL-BOUND: relation-family recovery is measured in the current low-term factor-column namespace.",
            "POST-GATE COST GAP: current route predicates rely on hit-root metrics computed after selected-leaf replay.",
            "NO SPEEDUP CLAIM: this ledger is a cost/yield accounting step before any Pollard-rho comparison.",
        ],
        "method": "p569_leaf16_route_cost_yield_ledger",
        "schema": "ecdlp.low_term_total2_p569_leaf16_route_cost_yield_ledger.v1",
        "summary": {
            **summary,
            "next_work_order": "P570_PRE_HIT_PUBLIC_SOURCE_FEATURE_SCOUT",
            "target_descent_implemented": False,
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
