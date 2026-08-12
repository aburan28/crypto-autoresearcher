#!/usr/bin/env python3
"""Emit an integrated relation-collection contract status artifact.

This joins the current low-term selected-product pipeline outputs into one
machine-readable audit record. It is deliberately conservative: selected-row
validation can be positive while the integrated solver contract remains OPEN if
rejected-row charging, row-stop policy, or target descent are not implemented.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def compact_gate_summary(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    return {
        "artifact": payload.get("source"),
        "case_count": int_value(summary.get("case_count")),
        "claim_status": summary.get("claim_status"),
        "gate_false_positive_count": int_value(summary.get("gate_false_positive_count")),
        "gate_name": summary.get("gate_name"),
        "gate_verified_above_rho_count": int_value(summary.get("gate_verified_above_rho_count")),
        "public_selected_count": int_value(
            summary.get("public_product_gate_selected_count")
            if "public_product_gate_selected_count" in summary
            else summary.get("public_low_prefix_gate_selected_count")
        ),
        "selected_below_rho_count": int_value(
            summary.get("selected_shared_product_below_rho_count")
            if "selected_shared_product_below_rho_count" in summary
            else summary.get("selected_direct_below_rho_count")
        ),
        "selected_unverified_count": int_value(summary.get("selected_unverified_count")),
        "selected_verified_count": int_value(
            summary.get("selected_shared_product_verified_count")
            if "selected_shared_product_verified_count" in summary
            else summary.get("selected_direct_verified_count")
        ),
    }


def compact_timing(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    summary = payload.get("summary") or payload
    return {
        "artifact": str(path),
        "claim_status": summary.get("claim_status"),
        "direct_ops": summary.get("direct_verifier_replay_ops"),
        "direct_ops_over_rho": summary.get("direct_verifier_replay_ops_over_rho"),
        "direct_secret": summary.get("direct_union_derived_secret"),
        "public_key_verified": bool(summary.get("shared_product_union_public_key_verified")),
        "rank": summary.get("shared_product_union_rank"),
        "relation_count": summary.get("shared_product_union_relation_count"),
        "rho": summary.get("rho"),
        "selector": summary.get("selector"),
        "shared_ops": summary.get("shared_product_ledger_ops"),
        "shared_ops_over_rho": summary.get("shared_product_ledger_ops_over_rho"),
        "shared_product_beats_rho": bool(summary.get("shared_product_ledger_beats_rho")),
        "shared_secret": summary.get("shared_product_union_derived_secret"),
        "status": summary.get("status"),
        "target": summary.get("target"),
        "top_k": summary.get("top_k"),
        "transfer_index": summary.get("transfer_index"),
    }


def compact_stop_rule(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    audits = payload.get("audits") or []
    first_selected = next((audit for audit in audits if audit.get("selected")), None)
    selected = (first_selected or {}).get("selected") or {}
    return {
        "artifact": str(path),
        "claim_status": summary.get("claim_status"),
        "parameters": payload.get("parameters") or {},
        "passes": (
            int_value(summary.get("stopped_count")) > 0
            and int_value(summary.get("unverified_stop_count")) == 0
            and int_value(summary.get("verified_above_screened_rho_count")) == 0
            and int_value(summary.get("screened_below_rho_count")) == int_value(summary.get("stopped_count"))
        ),
        "screened_below_rho_count": int_value(summary.get("screened_below_rho_count")),
        "selected": selected or None,
        "selected_only_below_rho_count": int_value(summary.get("selected_only_below_rho_count")),
        "stopped_count": int_value(summary.get("stopped_count")),
        "unverified_stop_count": int_value(summary.get("unverified_stop_count")),
        "verified_above_screened_rho_count": int_value(
            summary.get("verified_above_screened_rho_count")
        ),
        "window_count": int_value(summary.get("window_count")),
        "first_stop_rejected_before_stop_count": int_value(
            (first_selected or {}).get("rejected_before_stop_count")
        ),
        "first_stop_rejected_screen_ops_before_stop": int_value(
            (first_selected or {}).get("rejected_screen_ops_before_stop")
        ),
        "first_stop_screened_total_ops": (first_selected or {}).get("screened_total_ops"),
        "first_stop_screened_total_ops_over_rho": (first_selected or {}).get(
            "screened_total_ops_over_rho"
        ),
    }


def compact_source_charge(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    audits = payload.get("audits") or []
    first_selected = next((audit for audit in audits if audit.get("selected")), None)
    selected = (first_selected or {}).get("selected") or {}
    passes = (
        int_value(summary.get("stopped_count")) > 0
        and int_value(summary.get("unverified_stop_count")) == 0
        and int_value(summary.get("verified_above_source_charged_rho_count")) == 0
        and int_value(summary.get("source_charged_below_rho_count")) == int_value(summary.get("stopped_count"))
    )
    return {
        "artifact": str(path),
        "claim_status": summary.get("claim_status"),
        "honesty_boundary": payload.get("honesty_boundary") or [],
        "parameters": payload.get("parameters") or {},
        "passes": passes,
        "selected": selected or None,
        "source_charged_below_rho_count": int_value(summary.get("source_charged_below_rho_count")),
        "stopped_count": int_value(summary.get("stopped_count")),
        "total_generated_source_row_count": int_value(summary.get("total_generated_source_row_count")),
        "total_source_row_generation_ops": int_value(summary.get("total_source_row_generation_ops")),
        "unverified_stop_count": int_value(summary.get("unverified_stop_count")),
        "verified_above_source_charged_rho_count": int_value(
            summary.get("verified_above_source_charged_rho_count")
        ),
        "window_count": int_value(summary.get("window_count")),
        "first_stop_generated_source_row_count": int_value(
            (first_selected or {}).get("generated_source_row_count")
        ),
        "first_stop_rejected_screen_ops_before_stop": int_value(
            (first_selected or {}).get("rejected_screen_ops_before_stop")
        ),
        "first_stop_source_charged_total_ops": (first_selected or {}).get(
            "source_charged_total_ops"
        ),
        "first_stop_source_charged_total_ops_over_rho": (first_selected or {}).get(
            "source_charged_total_ops_over_rho"
        ),
        "first_stop_source_row_generation_ops": (first_selected or {}).get(
            "source_row_generation_ops"
        ),
    }


def source_summary(payload: dict[str, Any]) -> dict[str, Any]:
    summaries = (payload.get("summary") or {}).get("policy_summaries") or []
    policy = summaries[0] if summaries else {}
    params = payload.get("parameters") or {}
    return {
        "claim_scope": "component source artifact; not yet a one-process relation collector",
        "fixed_row_selectors": params.get("fixed_row_selectors"),
        "leaf_selectors": params.get("leaf_selectors"),
        "stress_leaf_below_rho": int_value(policy.get("stress_leaf_below_rho")),
        "stress_leaf_best_ops_over_rho": policy.get("stress_leaf_best_ops_over_rho"),
        "stress_leaf_verified": int_value(policy.get("stress_leaf_verified")),
        "stress_row_below_rho": int_value(policy.get("stress_row_below_rho")),
        "stress_row_verified": int_value(policy.get("stress_row_verified")),
        "stress_transfer_indices": params.get("stress_transfer_indices"),
        "top_k_grid": params.get("top_k_grid"),
    }


def selected_row_validation(summary: dict[str, Any]) -> dict[str, Any]:
    selected_below = int_value(summary.get("selected_below_rho_count"))
    selected_unverified = int_value(summary.get("selected_unverified_count"))
    selected_above = int_value(summary.get("selected_verified_above_rho_count"))
    distinct = int_value(summary.get("selected_distinct_below_rho_solution_count"))
    return {
        "passes": selected_below > 0 and selected_unverified == 0 and selected_above == 0 and distinct > 0,
        "selected_below_rho_count": selected_below,
        "selected_distinct_below_rho_solution_count": distinct,
        "selected_route_case_count": int_value(summary.get("selected_route_case_count")),
        "selected_unverified_count": selected_unverified,
        "selected_verified_above_rho_count": selected_above,
        "selected_verified_count": int_value(summary.get("selected_verified_count")),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--strict", required=True)
    parser.add_argument("--density", required=True)
    parser.add_argument("--low-prefix", required=True)
    parser.add_argument("--split", required=True)
    parser.add_argument("--stop-rule")
    parser.add_argument("--source-charge")
    parser.add_argument("--timing", action="append", default=[])
    parser.add_argument("--window", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    source_path = Path(args.source)
    strict_path = Path(args.strict)
    density_path = Path(args.density)
    low_prefix_path = Path(args.low_prefix)
    split_path = Path(args.split)
    stop_rule_path = Path(args.stop_rule) if args.stop_rule else None
    source_charge_path = Path(args.source_charge) if args.source_charge else None
    timing_paths = [Path(path) for path in args.timing]

    source = load_json(source_path)
    strict = load_json(strict_path)
    density = load_json(density_path)
    low_prefix = load_json(low_prefix_path)
    split = load_json(split_path)
    stop_rule = compact_stop_rule(load_json(stop_rule_path), stop_rule_path) if stop_rule_path else None
    source_charge = (
        compact_source_charge(load_json(source_charge_path), source_charge_path)
        if source_charge_path
        else None
    )
    timings = [compact_timing(load_json(path), path) for path in timing_paths]

    split_summary = split.get("summary") or {}
    selected_validation = selected_row_validation(split_summary)
    strict_app = split.get("strict_guard_application") or {}
    density_app = split.get("guard_application") or {}
    low_prefix_app = split.get("low_prefix_application") or {}

    stop_covered = bool((source_charge and source_charge["passes"]) or (stop_rule and stop_rule["passes"]))
    source_covered = bool(source_charge and source_charge["passes"])

    missing_integrated_fields = ["target_descent"]
    if not source_covered:
        missing_integrated_fields.append("one_process_source_generation_charge")
    if not stop_covered:
        missing_integrated_fields.extend(["public_row_stop_rule", "rejected_row_cost_before_stop"])

    if stop_covered and source_covered:
        integrated_reason = (
            "public stop rule, rejected-row screen, and fixed-leaf source-row charge are covered for the audited schedule; "
            "target descent remains open"
        )
    elif stop_rule and stop_rule["passes"]:
        integrated_reason = (
            "public stop rule and rejected-row screen are covered by the stop-rule artifact, "
            "but source generation and target descent remain open"
        )
    else:
        integrated_reason = "selected rows are replay-positive, but row-stop, rejected-row charging, and target descent are still component/open fields"
    claim_prefix = (
        "OPEN / PUBLIC STOP-RULE OBSERVATION POSITIVE"
        if stop_rule and stop_rule["passes"]
        else "OPEN / SELECTED-ROW OBSERVATION POSITIVE"
    )

    payload = {
        "artifacts": {
            "density": str(density_path),
            "low_prefix": str(low_prefix_path),
            "source": str(source_path),
            "source_charge": str(source_charge_path) if source_charge_path else None,
            "split": str(split_path),
            "stop_rule": str(stop_rule_path) if stop_rule_path else None,
            "strict": str(strict_path),
            "timing": [str(path) for path in timing_paths],
        },
        "claim_status": f"{claim_prefix} / INTEGRATED CONTRACT NOT YET SATISFIED",
        "created_at": now_iso(),
        "density_gate": compact_gate_summary(density),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: local operation-ledger rho comparison, not deployment wall-clock complexity.",
            "UNTESTED: target descent is a placeholder.",
            (
                "PARTIAL: rejected-row screen and public row-stop are covered by the audited stop/source-charge schedule."
                if stop_covered
                else "OPEN: rejected-row and row-stop costs are not yet charged in one live collector."
            ),
            (
                "PARTIAL: fixed-leaf strict-product source-row charge is covered by a source-charge artifact."
                if source_charge and source_charge["passes"]
                else "OPEN: fixed-leaf source-row generation charge is not covered by a passing source-charge artifact."
            ),
        ],
        "integrated_contract": {
            "missing_fields": missing_integrated_fields,
            "passes": False,
            "reason": integrated_reason,
        },
        "low_prefix_gate": compact_gate_summary(low_prefix),
        "rank_and_replay": timings,
        "rejected_rows": {
            "density_abstained_count": int_value(density_app.get("abstained_density_product_case_count")),
            "density_rejected_count": int_value(density_app.get("rejected_density_product_case_count")),
            "low_prefix_enabled": bool(low_prefix_app.get("enabled")),
            "low_prefix_selected_count": int_value(low_prefix_app.get("selected_low_prefix_case_count")),
            "strict_abstained_count": int_value(strict_app.get("abstained_strict_product_case_count")),
            "strict_rejected_count": int_value(strict_app.get("rejected_strict_product_case_count")),
        },
        "row_stop": {
            "implemented": stop_covered,
            "public_rule": (
                (source_charge or {}).get("parameters")
                if source_charge and source_charge["passes"]
                else (stop_rule or {}).get("parameters") if stop_rule else None
            ),
            "status": "OBSERVATION" if stop_covered else "OPEN",
        },
        "selected_row_validation": selected_validation,
        "source_generation": source_summary(source),
        "source_generation_charge": source_charge,
        "stop_rule_validation": stop_rule,
        "strict_gate": compact_gate_summary(strict),
        "target_descent": {
            "implemented": False,
            "status": "UNTESTED",
        },
        "window": args.window,
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["selected_row_validation"], indent=2, sort_keys=True))
    print(json.dumps(payload["integrated_contract"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
