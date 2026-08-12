#!/usr/bin/env python3
"""P705 amortized cost crossover audit for P704 factor-value transfer.

P704 shows that P701-derived factor values transfer to three fresh endpoint
surfaces.  This audit converts that into explicit cost accounting: single-target
cost, observed three-target amortized cost, and the number of targets needed to
beat independent Pollard rho under several endpoint-relation charge policies.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P704 = STATE_DIR / "low_term_total2_p704_fresh_surface_factor_value_transfer_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p705_amortized_cost_crossover_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def surface_policy_costs(surface: dict[str, Any]) -> dict[str, float | None]:
    stats = surface.get("candidate_direct_cost_stats_over_rho") or {}
    count = int_value(stats.get("count"))
    if count <= 0:
        return {"all_forms": None, "max": None, "mean": None, "min": None}
    return {
        "all_forms": round(float_value(stats.get("mean")) * count, 8),
        "max": float_value(stats.get("max")),
        "mean": float_value(stats.get("mean")),
        "min": float_value(stats.get("min")),
    }


def break_even_target_count(factor_charge: float, target_cost: float) -> int | None:
    if target_cost >= 1.0:
        return None
    # Need factor_charge + n * target_cost < n.
    threshold = factor_charge / (1.0 - target_cost)
    return math.floor(threshold) + 1


def policy_report(policy: str, factor_charge: float, surfaces: list[dict[str, Any]]) -> dict[str, Any]:
    per_surface = []
    target_costs = []
    for surface in surfaces:
        costs = surface_policy_costs(surface)
        target_cost = costs.get(policy)
        if target_cost is None:
            continue
        target_cost = float(target_cost)
        target_costs.append(target_cost)
        per_surface.append(
            {
                "break_even_target_count_if_repeated": break_even_target_count(factor_charge, target_cost),
                "candidate_form_count": int_value(surface.get("candidate_form_count")),
                "single_target_total_over_rho": round(factor_charge + target_cost, 8),
                "surface_name": surface.get("surface_name"),
                "target_relation_charge_over_rho": round(target_cost, 8),
                "verified_form_count": int_value(surface.get("verified_form_count")),
            }
        )
    target_count = len(target_costs)
    target_total = sum(target_costs)
    total = factor_charge + target_total
    return {
        "beats_rho_for_observed_targets": bool(target_count and total < target_count),
        "factor_bank_charge_over_rho": round(factor_charge, 8),
        "observed_target_count": target_count,
        "per_surface": per_surface,
        "policy": policy,
        "single_target_below_rho_count": sum(1 for cost in target_costs if factor_charge + cost < 1.0),
        "target_relation_charge_total_over_rho": round(target_total, 8),
        "total_charge_over_rho": round(total, 8),
        "total_charge_per_target_over_rho": round(total / target_count, 8) if target_count else None,
        "vs_independent_rho_total_over_rho": target_count,
    }


def all_form_lower_bound_report(factor_charge: float, surfaces: list[dict[str, Any]]) -> dict[str, Any]:
    """Report the deliberately pessimistic policy of scanning every verified form."""
    target_count = len(surfaces)
    target_total = 0.0
    per_surface = []
    for surface in surfaces:
        costs = surface_policy_costs(surface)
        charge = float_value(costs.get("all_forms"))
        target_total += charge
        per_surface.append(
            {
                "candidate_form_count": int_value(surface.get("candidate_form_count")),
                "surface_name": surface.get("surface_name"),
                "target_relation_charge_over_rho": round(charge, 8),
            }
        )
    total = factor_charge + target_total
    return {
        "beats_rho_for_observed_targets": bool(target_count and total < target_count),
        "factor_bank_charge_over_rho": round(factor_charge, 8),
        "observed_target_count": target_count,
        "per_surface": per_surface,
        "policy": "all_forms",
        "target_relation_charge_total_over_rho": round(target_total, 8),
        "total_charge_over_rho": round(total, 8),
        "total_charge_per_target_over_rho": round(total / target_count, 8) if target_count else None,
        "vs_independent_rho_total_over_rho": target_count,
    }


def determine_claim(policy_reports: list[dict[str, Any]]) -> str:
    if any(report.get("single_target_below_rho_count") for report in policy_reports):
        return "P705_SINGLE_TARGET_AND_AMORTIZED_COST_BELOW_RHO"
    if any(report.get("beats_rho_for_observed_targets") for report in policy_reports):
        return "P705_AMORTIZED_MANY_TARGET_COST_BELOW_RHO"
    return "NEGATIVE_RESULT_P705_NO_AMORTIZED_COST_CROSSOVER"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p704 = load_json(Path(args.p704))
    summary = p704.get("summary") or {}
    factor_charge = float_value(summary.get("p701_training_charge_over_rho"))
    surfaces = [
        surface
        for surface in p704.get("surface_reports") or []
        if int_value(surface.get("verified_form_count")) and not int_value(surface.get("false_public_secret_count"))
    ]
    policy_reports = [
        policy_report(policy, factor_charge, surfaces)
        for policy in ("min", "mean", "max")
    ]
    all_forms = all_form_lower_bound_report(factor_charge, surfaces)
    claim_status = determine_claim(policy_reports)
    best_observed = min(
        (report for report in policy_reports if report["observed_target_count"]),
        key=lambda report: float_value(report.get("total_charge_per_target_over_rho"), 999.0),
        default=None,
    )
    return {
        "artifacts": {"p704": str(Path(args.p704))},
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: costs are normalized to the local Pollard-rho operation ledger.",
            "HEURISTIC: endpoint relation acquisition is represented by observed P704 direct charges, not an asymptotic source-generation theorem.",
            "NO SINGLE-TARGET SPEEDUP CLAIM unless factor-bank plus target-relation charge is below 1.0x rho for that target.",
        ],
        "method": "p705_amortized_cost_crossover",
        "parameters": {
            "factor_bank_charge_over_rho": factor_charge,
            "policies": ["min", "mean", "max", "all_forms"],
            "surface_names": [surface.get("surface_name") for surface in surfaces],
        },
        "policy_reports": policy_reports,
        "pessimistic_all_forms_report": all_forms,
        "schema": "ecdlp.low_term_total2_p705_amortized_cost_crossover.v1",
        "summary": {
            "best_observed_policy": None if best_observed is None else best_observed["policy"],
            "best_observed_total_charge_per_target_over_rho": (
                None if best_observed is None else best_observed["total_charge_per_target_over_rho"]
            ),
            "factor_bank_charge_over_rho": round(factor_charge, 8),
            "p704_claim_status": p704.get("claim_status"),
            "single_target_below_rho_policy_count": sum(
                1 for report in policy_reports if int_value(report.get("single_target_below_rho_count"))
            ),
            "surface_count": len(surfaces),
            "verified_form_count": sum(int_value(surface.get("verified_form_count")) for surface in surfaces),
            "zero_false_public_secret_surfaces": len(surfaces),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p704", default=str(DEFAULT_P704))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"policy_reports": payload["policy_reports"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
