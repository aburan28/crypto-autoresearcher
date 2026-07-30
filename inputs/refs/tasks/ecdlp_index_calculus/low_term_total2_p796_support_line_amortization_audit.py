#!/usr/bin/env python3
"""P796 amortization audit for the P795 support-line table."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P795_SCRIPT = TASK_DIR / "low_term_total2_p795_support_line_fresh_namespace_validation.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p796_support_line_amortization_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p796_support_line_amortization_audit.md"
SCHEMA = "ecdlp.low_term_total2_p796_support_line_amortization_audit.v1"
DEFAULT_BUDGETS = "32,64,128,256,512,1024"
DEFAULT_EVAL_NAMESPACES = "supportlinevalid-v1,supportlinevalid-v2,supportlinevalid-v3,supportlinevalid-v4"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def train_cost_units(primary: dict[str, Any], field_weight: int) -> dict[str, int]:
    calibration_field_ops = int((primary.get("calibration_field_ops") or {}).get("total_field_ops") or 0)
    train_calibration_online = int(primary.get("train_calibration_online_group_additions") or 0)
    train_population_online = int(primary.get("train_population_online_group_additions") or 0)
    calibration_field_unit_cost = int(field_weight) * calibration_field_ops
    return {
        "calibration_field_ops": calibration_field_ops,
        "calibration_field_unit_cost": calibration_field_unit_cost,
        "covered_train_unit_cost": train_calibration_online + calibration_field_unit_cost,
        "full_train_unit_cost": train_calibration_online + train_population_online + calibration_field_unit_cost,
        "train_calibration_online_group_additions": train_calibration_online,
        "train_population_online_group_additions": train_population_online,
    }


def aggregate_prefix(
    namespace_targets: list[dict[str, Any]],
    field_weight: int,
) -> dict[str, Any]:
    keys = [
        "all_population_rho_baseline",
        "all_population_total_unit_cost",
        "calibration_online_group_additions",
        "calibration_row_count",
        "covered_online_group_additions",
        "covered_target_count",
        "covered_target_rho_baseline",
        "covered_total_unit_cost",
        "eval_all_population_total_unit_cost",
        "recovered_form_count",
        "recovered_row_count",
        "recovered_rho_baseline",
        "scored_form_count",
        "target_row_mismatch_count",
        "total_field_ops",
        "train_eval_all_population_total_unit_cost",
    ]
    totals = {key: sum(int((target["primary"] or {}).get(key) or 0) for target in namespace_targets) for key in keys}
    repeats_by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for target in namespace_targets:
        repeats_by_target[str(target["dest_target"])].append(target)
    duplicate_covered_train_cost = 0
    duplicate_full_train_cost = 0
    train_cost_once = {
        "calibration_field_ops": 0,
        "calibration_field_unit_cost": 0,
        "covered_train_unit_cost": 0,
        "full_train_unit_cost": 0,
        "train_calibration_online_group_additions": 0,
        "train_population_online_group_additions": 0,
    }
    for items in repeats_by_target.values():
        first_cost = train_cost_units(items[0]["primary"], field_weight)
        for key, value in first_cost.items():
            train_cost_once[key] += int(value)
        repeat_count = len(items)
        duplicate_covered_train_cost += max(0, repeat_count - 1) * first_cost["covered_train_unit_cost"]
        duplicate_full_train_cost += max(0, repeat_count - 1) * first_cost["full_train_unit_cost"]
    covered_once = totals["covered_total_unit_cost"] - duplicate_covered_train_cost
    full_once = totals["train_eval_all_population_total_unit_cost"] - duplicate_full_train_cost
    totals.update(
        {
            "covered_once_train_total_unit_cost": covered_once,
            "covered_once_train_total_unit_cost_over_recovered_rho": ratio(covered_once, totals["recovered_rho_baseline"]),
            "covered_repeat_train_total_unit_cost": totals["covered_total_unit_cost"],
            "covered_repeat_train_total_unit_cost_over_recovered_rho": ratio(
                totals["covered_total_unit_cost"],
                totals["recovered_rho_baseline"],
            ),
            "duplicate_covered_train_unit_cost_removed": duplicate_covered_train_cost,
            "duplicate_full_train_unit_cost_removed": duplicate_full_train_cost,
            "eval_namespace_count": len({target["eval_seed_namespace"] for target in namespace_targets}),
            "fresh_overlap_line_count": sum(int(target.get("fresh_overlap_line_count") or 0) for target in namespace_targets),
            "fresh_row_count": sum(int(target.get("eval_row_count") or 0) for target in namespace_targets),
            "full_once_train_eval_population_total_unit_cost": full_once,
            "full_once_train_eval_population_total_unit_cost_over_recovered_rho": ratio(
                full_once,
                totals["recovered_rho_baseline"],
            ),
            "full_repeat_train_eval_population_total_unit_cost": totals["train_eval_all_population_total_unit_cost"],
            "full_repeat_train_eval_population_total_unit_cost_over_recovered_rho": ratio(
                totals["train_eval_all_population_total_unit_cost"],
                totals["recovered_rho_baseline"],
            ),
            "recovered_row_rate_over_covered": ratio(totals["recovered_row_count"], totals["covered_target_count"]),
            "scan_selectivity_row_rate": ratio(totals["covered_target_count"], sum(int(target.get("eval_row_count") or 0) for target in namespace_targets)),
            "target_count": len(repeats_by_target),
            "train_cost_once": train_cost_once,
            "trained_line_count": sum(int(target.get("trained_line_count") or 0) for target in namespace_targets),
        }
    )
    control_totals = []
    control_count = max((len(target.get("controls") or []) for target in namespace_targets), default=0)
    for control_index in range(control_count):
        recovered = sum(
            int(target["controls"][control_index]["result"].get("recovered_row_count") or 0)
            for target in namespace_targets
            if control_index < len(target.get("controls") or [])
        )
        recovered_rho = sum(
            int(target["controls"][control_index]["result"].get("recovered_rho_baseline") or 0)
            for target in namespace_targets
            if control_index < len(target.get("controls") or [])
        )
        control_totals.append(
            {
                "control_index": control_index,
                "recovered_rho_baseline": recovered_rho,
                "recovered_row_count": recovered,
            }
        )
    max_control_recovered = max((item["recovered_row_count"] for item in control_totals), default=0)
    totals["control_totals"] = control_totals
    totals["max_control_recovered_row_count"] = max_control_recovered
    totals["primary_minus_max_control_recovered_rows"] = totals["recovered_row_count"] - max_control_recovered
    return totals


def determine_prefix_claim(aggregate: dict[str, Any]) -> str:
    if int(aggregate["covered_target_count"]) == 0:
        return "no_fresh_coverage"
    if int(aggregate["recovered_row_count"]) <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_controls"
    if (aggregate["full_once_train_eval_population_total_unit_cost_over_recovered_rho"] or 10**9) < 1.0:
        return "full_population_below_rho"
    if (aggregate["covered_once_train_total_unit_cost_over_recovered_rho"] or 10**9) < 1.0:
        return "covered_component_below_rho"
    return "cost_boundary"


def determine_claim(summary: dict[str, Any]) -> str:
    claims = [prefix["prefix_claim"] for result in summary["budget_results"] for prefix in result["prefix_results"]]
    if "full_population_below_rho" in claims:
        return "P796_SUPPORT_LINE_AMORTIZATION_FULL_POPULATION_BELOW_RHO_SIGNAL"
    if "covered_component_below_rho" in claims:
        return "P796_SUPPORT_LINE_AMORTIZATION_COVERED_COMPONENT_SIGNAL"
    if "cost_boundary" in claims:
        return "P796_SUPPORT_LINE_AMORTIZATION_COST_BOUNDARY"
    return "NEGATIVE_RESULT_P796_SUPPORT_LINE_AMORTIZATION_NO_CONTROLLED_RECOVERY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p795 = load_module("ecdlp_p795_for_p796", P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p796", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p796", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p796", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p796", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p796", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p796", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p796", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p796", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p796", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p796", p782.P780_SCRIPT)
    stack = p780.load_stack()
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    budgets = csv_ints(args.budgets)
    eval_namespaces = csv_strings(args.eval_seed_namespaces)
    train_args = p795.namespace_args(args, args.train_seed_namespace, int(args.train_replicas))
    print(f"preparing train namespace {args.train_seed_namespace}", flush=True)
    train_prepared = {
        key: p794.prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], train_args)
        for key in required
    }
    eval_prepared_by_namespace = {}
    for namespace in eval_namespaces:
        print(f"preparing eval namespace {namespace}", flush=True)
        eval_args = p795.namespace_args(args, namespace, int(args.eval_replicas))
        eval_prepared_by_namespace[namespace] = {
            key: p794.prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], eval_args)
            for key in required
        }
    budget_results = []
    for budget in budgets:
        print(f"scoring budget {budget}", flush=True)
        namespace_results = []
        for namespace in eval_namespaces:
            targets = [
                {
                    **p795.evaluate_frozen_budget(
                        p793,
                        p794,
                        train_prepared[key],
                        eval_prepared_by_namespace[namespace][key],
                        budget,
                        args,
                    ),
                    "eval_seed_namespace": namespace,
                }
                for key in required
            ]
            namespace_results.append(
                {
                    "aggregate": aggregate_prefix(targets, int(args.field_weight)),
                    "eval_seed_namespace": namespace,
                    "targets": targets,
                }
            )
        prefix_results = []
        for prefix_size in range(1, len(namespace_results) + 1):
            prefix_targets = [
                target
                for namespace_result in namespace_results[:prefix_size]
                for target in namespace_result["targets"]
            ]
            aggregate = aggregate_prefix(prefix_targets, int(args.field_weight))
            prefix = {
                "aggregate": aggregate,
                "eval_namespace_prefix": eval_namespaces[:prefix_size],
                "prefix_size": prefix_size,
            }
            prefix["prefix_claim"] = determine_prefix_claim(aggregate)
            prefix_results.append(prefix)
        budget_results.append(
            {
                "budget": int(budget),
                "namespace_results": namespace_results,
                "prefix_results": prefix_results,
            }
        )
    best_full = min(
        [
            {"budget": result["budget"], **prefix}
            for result in budget_results
            for prefix in result["prefix_results"]
            if prefix["aggregate"]["full_once_train_eval_population_total_unit_cost_over_recovered_rho"] is not None
        ],
        key=lambda item: item["aggregate"]["full_once_train_eval_population_total_unit_cost_over_recovered_rho"],
        default=None,
    )
    best_covered = min(
        [
            {"budget": result["budget"], **prefix}
            for result in budget_results
            for prefix in result["prefix_results"]
            if prefix["aggregate"]["covered_once_train_total_unit_cost_over_recovered_rho"] is not None
        ],
        key=lambda item: item["aggregate"]["covered_once_train_total_unit_cost_over_recovered_rho"],
        default=None,
    )
    summary = {
        "best_covered_once_train": {
            "budget": best_covered["budget"],
            "covered_once_train_total_unit_cost_over_recovered_rho": best_covered["aggregate"]["covered_once_train_total_unit_cost_over_recovered_rho"],
            "prefix_size": best_covered["prefix_size"],
            "recovered_row_count": best_covered["aggregate"]["recovered_row_count"],
        }
        if best_covered
        else None,
        "best_full_once_train_eval": {
            "budget": best_full["budget"],
            "full_once_train_eval_population_total_unit_cost_over_recovered_rho": best_full["aggregate"]["full_once_train_eval_population_total_unit_cost_over_recovered_rho"],
            "prefix_size": best_full["prefix_size"],
            "recovered_row_count": best_full["aggregate"]["recovered_row_count"],
        }
        if best_full
        else None,
        "budget_results": budget_results,
        "eval_namespaces": eval_namespaces,
        "eval_replicas": int(args.eval_replicas),
        "train_replicas": int(args.train_replicas),
        "train_seed_namespace": args.train_seed_namespace,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p795_script": str(P795_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "AMORTIZED: trained support-line table is charged once across evaluation namespace prefixes.",
            "FROZEN-SELECTOR: support-line keys and values are selected from train data and not re-ranked on evaluation outcomes.",
            "FULL-POPULATION-CONSERVATIVE: full scan accounting charges train population and every evaluation population.",
            "NO HIT GENERATOR YET: selected-line membership is measured, not generated without scanning.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p796_support_line_amortization_audit",
        "parameters": {
            "budgets": budgets,
            "control_count": args.control_count,
            "eval_replicas": args.eval_replicas,
            "eval_seed_namespaces": eval_namespaces,
            "field_weight": args.field_weight,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_line_rows": args.min_line_rows,
            "row_policy": args.row_policy,
            "sparse_policies": csv_strings(args.sparse_policies),
            "train_replicas": args.train_replicas,
            "train_seed_namespace": args.train_seed_namespace,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "schema": f"{SCHEMA}.summary",
        "summary": payload["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--eval-seed-namespaces", default=DEFAULT_EVAL_NAMESPACES)
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--eval-replicas", type=int, default=20)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--budgets", default=DEFAULT_BUDGETS)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


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
                "best_covered_once_train": summary["summary"]["best_covered_once_train"],
                "best_full_once_train_eval": summary["summary"]["best_full_once_train_eval"],
                "claim_status": summary["claim_status"],
                "prefix_claims": [
                    {
                        "budget": result["budget"],
                        "prefixes": [
                            {
                                "claim": prefix["prefix_claim"],
                                "covered": prefix["aggregate"]["covered_once_train_total_unit_cost_over_recovered_rho"],
                                "full": prefix["aggregate"]["full_once_train_eval_population_total_unit_cost_over_recovered_rho"],
                                "prefix_size": prefix["prefix_size"],
                                "recovered": prefix["aggregate"]["recovered_row_count"],
                            }
                            for prefix in result["prefix_results"]
                        ],
                    }
                    for result in summary["summary"]["budget_results"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
