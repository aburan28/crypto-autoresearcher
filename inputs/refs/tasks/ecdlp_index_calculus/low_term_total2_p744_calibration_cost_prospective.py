#!/usr/bin/env python3
"""P744 calibration cost and prospective relation-generation audit.

P743 showed a same-target column-transport signal once a calibration certificate
exists. This script keeps the cost boundary explicit: it compares the warm-start
calibration result against a fresh relation_probe run and Pollard rho under
primary group-addition accounting plus clearly labeled diagnostic abstractions.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P742 = STATE_DIR / "low_term_total2_p742_disjoint_target_relation_transfer_probe.json"
DEFAULT_P743 = STATE_DIR / "low_term_total2_p743_target_column_transport_probe.json"
DEFAULT_PROSPECTIVE = STATE_DIR / "low_term_total2_p744_prospective_relation_probe_67_a1_11789_wide1024.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p744_calibration_cost_prospective_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p744_calibration_cost_prospective.md"
SCHEMA = "ecdlp.low_term_total2_p744_calibration_cost_prospective.v1"


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


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "median": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "median": median(values),
        "min": min(values),
    }


def threshold(precompute: int, per_challenge: int, rho: int) -> int | None:
    if rho <= per_challenge:
        return None
    return math.floor(precompute / (rho - per_challenge)) + 1


def split_by_name(p743: dict[str, Any], name: str) -> dict[str, Any]:
    for row in p743.get("splits") or []:
        if isinstance(row, dict) and row.get("name") == name:
            return row
    return {}


def selected_direct_ops(cert: dict[str, Any]) -> int:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    return int_value(selected.get("direct_ops"), int_value(cert.get("raw_relation_count"), 0))


def p742_negative_control(p742: dict[str, Any]) -> dict[str, Any]:
    audit = p742.get("transfer_audit") or {}
    return {
        "candidate_form_count": int_value(audit.get("candidate_form_count")),
        "false_recoverable_form_count": int_value(audit.get("false_recoverable_form_count")),
        "passes": (
            int_value(audit.get("verified_recoverable_form_count")) == 0
            and int_value(audit.get("false_recoverable_form_count")) == int_value(audit.get("candidate_form_count"))
        ),
        "verified_recoverable_form_count": int_value(audit.get("verified_recoverable_form_count")),
    }


def p743_positive_control(p743: dict[str, Any]) -> dict[str, Any]:
    split = split_by_name(p743, "prefix_train_1_heldout_11")
    result = split.get("transfer_result") or {}
    return {
        "claim_status": split.get("claim_status"),
        "false_recoverable_form_count": int_value(result.get("false_recoverable_form_count")),
        "passed": bool(split.get("passed")),
        "test_certificate_count": int_value(result.get("test_certificate_count")),
        "test_form_count": int_value(result.get("test_form_count")),
        "verified_recoverable_form_count": int_value(result.get("verified_recoverable_form_count")),
    }


def warm_start_cost_model(p742: dict[str, Any], p743: dict[str, Any], rho: int) -> dict[str, Any]:
    certs = [cert for cert in p742.get("candidate_certificates") or [] if isinstance(cert, dict)]
    split = split_by_name(p743, "prefix_train_1_heldout_11")
    train_indices = [int_value(item) for item in split.get("train_certificate_indices") or [0]]
    test_indices = [int_value(item) for item in split.get("test_certificate_indices") or []]
    calibration_ops = sum(
        selected_direct_ops(certs[index])
        for index in train_indices
        if 0 <= index < len(certs)
    )
    heldout_rho = len(test_indices) * rho
    all_rho = len(certs) * rho
    all_warm_start_ops = sum(selected_direct_ops(cert) for cert in certs)
    return {
        "all_certificate_count": len(certs),
        "all_independent_rho_steps": all_rho,
        "all_warm_start_direct_ops": all_warm_start_ops,
        "all_warm_start_direct_ops_over_independent_rho": ratio(all_warm_start_ops, all_rho),
        "calibration_certificate_indices": train_indices,
        "calibration_direct_ops": calibration_ops,
        "calibration_direct_ops_over_single_rho": ratio(calibration_ops, rho),
        "heldout_certificate_indices": test_indices,
        "heldout_independent_rho_steps": heldout_rho,
        "heldout_recovery_direct_ops_over_heldout_rho_after_calibration": ratio(calibration_ops, heldout_rho),
        "model_boundary": (
            "Warm-start lower bound only: it uses existing top-trial relation rows and does not count "
            "prospective relation generation for calibration or held-out challenges."
        ),
    }


def prospective_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = load_json(path)
        for result_index, result in enumerate(payload.get("results") or []):
            if not isinstance(result, dict):
                continue
            cost = result.get("cost_model") if isinstance(result.get("cost_model"), dict) else {}
            rho = int_value(result.get("generic_rho_steps"))
            subset_additions = int_value(cost.get("one_time_subset_group_additions"))
            online_group_additions = int_value(cost.get("estimated_online_group_additions"))
            online_scalar_mults = int_value(cost.get("online_scalar_mults"))
            relation_trials = int_value(result.get("relation_trials"))
            single_group_additions = int_value(cost.get("single_challenge_group_additions"))
            rows.append(
                {
                    "accepted_mixed_relations": int_value(result.get("accepted_mixed_relations")),
                    "actual_subset_coverage": result.get("actual_subset_coverage"),
                    "amortization": {
                        "group_addition_threshold_challenges": threshold(subset_additions, online_group_additions, rho),
                        "online_group_additions_over_rho": ratio(online_group_additions, rho),
                        "online_scalar_mults_over_rho": ratio(online_scalar_mults, rho),
                        "relation_trials_over_rho": ratio(relation_trials, rho),
                        "scalar_mult_threshold_challenges_mixed_units": threshold(subset_additions, online_scalar_mults, rho),
                        "trial_count_threshold_challenges_mixed_units": threshold(subset_additions, relation_trials, rho),
                    },
                    "cost_model": cost,
                    "decomposition_hits": int_value(result.get("decomposition_hits")),
                    "derived": bool(result.get("mixed_wide_relations_derive_secret")),
                    "first_hit_at_trial": result.get("first_hit_at_trial"),
                    "generic_rho_steps": rho,
                    "mixed_wide_relation_rank": int_value(result.get("mixed_wide_relation_rank")),
                    "one_shot_group_additions_over_rho": ratio(single_group_additions, rho),
                    "path": str(path),
                    "probe_summary": payload.get("summary") or {},
                    "relation_trials": relation_trials,
                    "result_index": result_index,
                    "single_challenge_group_additions": single_group_additions,
                    "subset_count": int_value(result.get("subset_count")),
                    "subset_unique_sums": int_value(result.get("subset_unique_sums")),
                    "subset_width": int_value(result.get("subset_width")),
                    "target": result.get("target"),
                    "trials_to_derive_secret": result.get("trials_to_derive_secret"),
                }
            )
    return rows


def best_prospective(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    return sorted(
        rows,
        key=lambda row: (
            not bool(row.get("derived")),
            row.get("one_shot_group_additions_over_rho") if row.get("one_shot_group_additions_over_rho") is not None else 10**18,
            int_value(row.get("relation_trials"), 10**18),
        ),
    )[0]


def determine_claim(p743_control: dict[str, Any], prospective: list[dict[str, Any]]) -> str:
    if not p743_control.get("passed"):
        return "NEGATIVE_RESULT_P744_P743_CONTROL_FAILED"
    derived = [row for row in prospective if row.get("derived")]
    if not derived:
        return "NEGATIVE_RESULT_P744_PROSPECTIVE_CALIBRATION_NOT_DERIVED"
    if any((row.get("one_shot_group_additions_over_rho") or 10**18) < 1.0 for row in derived):
        return "P744_PROSPECTIVE_CALIBRATION_ONE_SHOT_BELOW_RHO_SIGNAL"
    if any((row.get("amortization") or {}).get("group_addition_threshold_challenges") for row in derived):
        return "P744_PROSPECTIVE_CALIBRATION_GROUP_AMORTIZATION_SIGNAL"
    return "P744_PROSPECTIVE_CALIBRATION_DERIVES_GROUP_COST_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p742 = load_json(args.p742)
    p743 = load_json(args.p743)
    probes = prospective_rows(args.prospective_probe)
    p743_control = p743_positive_control(p743)
    p742_control = p742_negative_control(p742)
    rho = int_value((p742.get("parameters") or {}).get("pollard_rho_baseline_steps"))
    best = best_prospective(probes)
    payload = {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p742": str(args.p742),
            "p743": str(args.p743),
            "prospective_probes": [str(path) for path in args.prospective_probe],
        },
        "claim_status": "",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "WARM-START BOUNDARY: P743 uses existing top-trial relation rows; prospective relation_probe evidence is reported separately.",
            "PRIMARY COST MODEL: group additions including subset precomputation are compared to Pollard rho.",
            "DIAGNOSTIC COST MODELS: scalar-multiplication and trial-count thresholds are mixed-unit hints only, not speedup claims.",
            "NO DEPLOYED-CURVE CLAIM: relation density, calibration setup cost, sparse linear algebra, and scaling remain open.",
        ],
        "method": "p744_calibration_cost_and_prospective_relation_generation",
        "parameters": {
            "best_prospective_probe": None if best is None else best.get("path"),
            "order": int_value((p742.get("target_metadata") or {}).get("base_order"), 11779),
            "pollard_rho_baseline_steps": rho,
            "target": (p742.get("target_metadata") or {}).get("label", "67.a1"),
            "target_key": ((p742.get("candidate_certificate_summary") or {}).get("candidate_targets") or ["67.a1@11789"])[0],
        },
        "p742_negative_control": p742_control,
        "p743_positive_control": p743_control,
        "prospective_probe_summary": {
            "derived_probe_count": sum(1 for row in probes if row.get("derived")),
            "group_addition_amortization_threshold_count": sum(
                1
                for row in probes
                if (row.get("amortization") or {}).get("group_addition_threshold_challenges")
            ),
            "one_shot_below_rho_count": sum(
                1 for row in probes if (row.get("one_shot_group_additions_over_rho") or 10**18) < 1.0
            ),
            "probe_count": len(probes),
            "relation_trials_stats": stat([int_value(row.get("relation_trials")) for row in probes]),
        },
        "prospective_probes": probes,
        "schema": SCHEMA,
        "warm_start_cost_model": warm_start_cost_model(p742, p743, rho),
    }
    payload["claim_status"] = determine_claim(p743_control, probes)
    return payload


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    best = best_prospective(payload["prospective_probes"])
    return {
        "schema": f"{SCHEMA}.summary",
        "created_at": payload["created_at"],
        "claim_status": payload["claim_status"],
        "honesty_boundary": payload["honesty_boundary"],
        "parameters": payload["parameters"],
        "p742_negative_control": payload["p742_negative_control"],
        "p743_positive_control": payload["p743_positive_control"],
        "prospective_best_probe": best,
        "prospective_probe_summary": payload["prospective_probe_summary"],
        "warm_start_cost_model": payload["warm_start_cost_model"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p742", type=Path, default=DEFAULT_P742)
    parser.add_argument("--p743", type=Path, default=DEFAULT_P743)
    parser.add_argument("--prospective-probe", type=Path, action="append", default=None)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    args = parser.parse_args()
    args.prospective_probe = args.prospective_probe or [DEFAULT_PROSPECTIVE]
    return args


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": summary["claim_status"],
                "prospective_best_probe": {
                    key: summary["prospective_best_probe"].get(key)
                    for key in [
                        "path",
                        "derived",
                        "relation_trials",
                        "accepted_mixed_relations",
                        "mixed_wide_relation_rank",
                        "one_shot_group_additions_over_rho",
                        "amortization",
                    ]
                }
                if summary["prospective_best_probe"]
                else None,
                "prospective_probe_summary": summary["prospective_probe_summary"],
                "warm_start_cost_model": summary["warm_start_cost_model"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
