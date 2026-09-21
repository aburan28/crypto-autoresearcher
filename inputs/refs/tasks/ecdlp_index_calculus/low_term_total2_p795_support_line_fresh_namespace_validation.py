#!/usr/bin/env python3
"""P795 fresh-namespace validation for support-line calibration."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P794_SCRIPT = TASK_DIR / "low_term_total2_p794_support_line_budget_selector.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p795_support_line_fresh_namespace_validation_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p795_support_line_fresh_namespace_validation.md"
SCHEMA = "ecdlp.low_term_total2_p795_support_line_fresh_namespace_validation.v1"
DEFAULT_BUDGETS = "32,64,128,256,512,1024,2048,4096,8192"


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


def namespace_args(args: argparse.Namespace, namespace: str, replicas: int) -> argparse.Namespace:
    values = vars(args).copy()
    values["eval_seed_namespace"] = namespace
    values["replicas"] = int(replicas)
    return argparse.Namespace(**values)


def record_line_keys(p793: Any, records: list[dict[str, Any]], order: int) -> set[tuple[int, int, int, int]]:
    keys = set()
    for record in records:
        parts = p793.line_parts(record, order)
        if parts is not None:
            keys.add(parts["line_key"])
    return keys


def add_training_cost(
    result: dict[str, Any],
    train_calibration_online: int,
    train_calibration_row_count: int,
    train_population_online: int,
) -> dict[str, Any]:
    adjusted = dict(result)
    recovered_rho = int(adjusted.get("recovered_rho_baseline") or 0)
    target_rho = int(adjusted.get("covered_target_rho_baseline") or 0)
    adjusted["train_calibration_online_group_additions"] = int(train_calibration_online)
    adjusted["train_calibration_row_count"] = int(train_calibration_row_count)
    adjusted["train_population_online_group_additions"] = int(train_population_online)
    adjusted["eval_all_population_total_unit_cost"] = int(adjusted["all_population_total_unit_cost"]) + int(train_calibration_online)
    adjusted["train_eval_all_population_total_unit_cost"] = (
        int(adjusted["all_population_total_unit_cost"]) + int(train_calibration_online) + int(train_population_online)
    )
    adjusted["calibration_online_group_additions"] = int(train_calibration_online)
    adjusted["calibration_row_count"] = int(train_calibration_row_count)
    adjusted["covered_online_group_additions"] = int(adjusted["covered_online_group_additions"]) + int(train_calibration_online)
    adjusted["covered_total_unit_cost"] = int(adjusted["covered_total_unit_cost"]) + int(train_calibration_online)
    adjusted["all_population_total_unit_cost"] = int(adjusted["eval_all_population_total_unit_cost"])
    adjusted["covered_total_unit_cost_over_recovered_rho"] = ratio(adjusted["covered_total_unit_cost"], recovered_rho)
    adjusted["covered_total_unit_cost_over_target_rho"] = ratio(adjusted["covered_total_unit_cost"], target_rho)
    adjusted["all_population_total_unit_cost_over_recovered_rho"] = ratio(
        adjusted["all_population_total_unit_cost"],
        recovered_rho,
    )
    adjusted["train_eval_all_population_total_unit_cost_over_recovered_rho"] = ratio(
        adjusted["train_eval_all_population_total_unit_cost"],
        recovered_rho,
    )
    return adjusted


def evaluate_frozen_budget(
    p793: Any,
    p794: Any,
    train_prepared: dict[str, Any],
    eval_prepared: dict[str, Any],
    budget: int,
    args: argparse.Namespace,
) -> dict[str, Any]:
    order = int(eval_prepared["order"])
    if int(train_prepared["order"]) != order:
        raise ValueError(f"order mismatch for {eval_prepared['dest_target']}: train={train_prepared['order']} eval={order}")
    trained = p794.selected_calibrations(train_prepared["all_calibrated"], int(budget))
    train_calibration_row_keys = {item["calibration_row_key"] for item in trained.values()}
    train_calibration_online = sum(
        int(train_prepared["rows_meta"][key]["online_group_additions"]) for key in train_calibration_row_keys
    )
    train_population_online = sum(int(item["online_group_additions"]) for item in train_prepared["rows_meta"].values())
    fresh_line_keys = record_line_keys(p793, eval_prepared["records"], order)
    fresh_overlap_keys = sorted(set(trained) & fresh_line_keys)
    primary_raw = p793.score_records(
        eval_prepared["records"],
        eval_prepared["rows_meta"],
        trained,
        set(),
        order,
        int(args.field_weight),
    )
    primary = add_training_cost(
        primary_raw,
        train_calibration_online,
        len(train_calibration_row_keys),
        train_population_online,
    )
    controls = []
    for control_index in range(int(args.control_count)):
        control_calibrated = p793.rotate_calibrations(trained, control_index + 1)
        control_raw = p793.score_records(
            eval_prepared["records"],
            eval_prepared["rows_meta"],
            control_calibrated,
            set(),
            order,
            int(args.field_weight),
        )
        controls.append(
            {
                "control_index": control_index,
                "result": add_training_cost(
                    control_raw,
                    train_calibration_online,
                    len(train_calibration_row_keys),
                    train_population_online,
                ),
            }
        )
    selected_sample = sorted(
        trained.values(),
        key=lambda item: (item["candidate_row_count"], item["candidate_form_count"]),
        reverse=True,
    )[:12]
    return {
        "available_train_line_count": len(train_prepared["all_calibrated"]),
        "budget": int(budget),
        "controls": controls,
        "dest_group_key": eval_prepared["dest_group_key"],
        "dest_target": eval_prepared["dest_target"],
        "eval_form_record_count": eval_prepared["form_record_count"],
        "eval_line_count": len(fresh_line_keys),
        "eval_replicas": eval_prepared["replicas"],
        "eval_row_count": eval_prepared["row_count"],
        "fresh_overlap_line_count": len(fresh_overlap_keys),
        "fresh_overlap_line_sample": [list(key) for key in fresh_overlap_keys[:12]],
        "order": order,
        "primary": primary,
        "selected_line_sample": [
            {
                "candidate_form_count": item["candidate_form_count"],
                "candidate_row_count": item["candidate_row_count"],
                "line_key": item["line_key"],
            }
            for item in selected_sample
        ],
        "train_form_record_count": train_prepared["form_record_count"],
        "train_replicas": train_prepared["replicas"],
        "train_row_count": train_prepared["row_count"],
        "trained_line_count": len(trained),
    }


def aggregate_budget(p794: Any, targets: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate = p794.aggregate_budget(targets)
    extra_keys = [
        "eval_all_population_total_unit_cost",
        "train_calibration_online_group_additions",
        "train_calibration_row_count",
        "train_eval_all_population_total_unit_cost",
        "train_population_online_group_additions",
    ]
    for key in extra_keys:
        aggregate[key] = sum(int((target["primary"] or {}).get(key) or 0) for target in targets)
    aggregate["trained_line_count"] = sum(int(target.get("trained_line_count") or 0) for target in targets)
    aggregate["fresh_overlap_line_count"] = sum(int(target.get("fresh_overlap_line_count") or 0) for target in targets)
    aggregate["eval_all_population_total_unit_cost_over_recovered_rho"] = ratio(
        aggregate["eval_all_population_total_unit_cost"],
        aggregate["recovered_rho_baseline"],
    )
    aggregate["train_eval_all_population_total_unit_cost_over_recovered_rho"] = ratio(
        aggregate["train_eval_all_population_total_unit_cost"],
        aggregate["recovered_rho_baseline"],
    )
    return aggregate


def determine_budget_claim(item: dict[str, Any]) -> str:
    aggregate = item["aggregate"]
    if int(aggregate["trained_line_count"]) == 0:
        return "no_trained_lines"
    if int(aggregate["covered_target_count"]) == 0:
        return "no_fresh_coverage"
    if int(aggregate["recovered_row_count"]) <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_controls"
    if (aggregate["covered_total_unit_cost_over_recovered_rho"] or 10**9) < 1.0:
        return "fresh_below_rho"
    return "fresh_cost_boundary"


def determine_claim(summary: dict[str, Any]) -> str:
    if any(item["budget_claim"] == "fresh_below_rho" for item in summary["budget_results"]):
        return "P795_SUPPORT_LINE_FRESH_NAMESPACE_BELOW_RHO_SIGNAL"
    if any(item["budget_claim"] == "fresh_cost_boundary" for item in summary["budget_results"]):
        return "P795_SUPPORT_LINE_FRESH_NAMESPACE_COST_BOUNDARY"
    return "NEGATIVE_RESULT_P795_SUPPORT_LINE_NO_FRESH_NAMESPACE_RECOVERY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p794 = load_module("ecdlp_p794_for_p795", P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p795", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p795", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p795", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p795", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p795", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p795", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p795", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p795", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p795", p782.P780_SCRIPT)
    stack = p780.load_stack()
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    budgets = csv_ints(args.budgets)
    train_args = namespace_args(args, args.train_seed_namespace, int(args.train_replicas))
    eval_args = namespace_args(args, args.eval_seed_namespace, int(args.eval_replicas))
    train_prepared = {
        key: p794.prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], train_args)
        for key in required
    }
    eval_prepared = {
        key: p794.prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], eval_args)
        for key in required
    }
    budget_results = []
    for budget in budgets:
        targets = [
            evaluate_frozen_budget(p793, p794, train_prepared[key], eval_prepared[key], budget, args)
            for key in required
        ]
        result = {
            "aggregate": aggregate_budget(p794, targets),
            "budget": int(budget),
            "targets": targets,
        }
        result["budget_claim"] = determine_budget_claim(result)
        budget_results.append(result)
    best_by_cost = min(
        [item for item in budget_results if item["aggregate"]["covered_total_unit_cost_over_recovered_rho"] is not None],
        key=lambda item: item["aggregate"]["covered_total_unit_cost_over_recovered_rho"],
        default=None,
    )
    summary = {
        "best_by_cost": {
            "budget": best_by_cost["budget"],
            "covered_total_unit_cost_over_recovered_rho": best_by_cost["aggregate"]["covered_total_unit_cost_over_recovered_rho"],
            "recovered_row_count": best_by_cost["aggregate"]["recovered_row_count"],
        }
        if best_by_cost
        else None,
        "budget_results": budget_results,
        "eval_seed_namespace": args.eval_seed_namespace,
        "eval_replicas": int(args.eval_replicas),
        "train_seed_namespace": args.train_seed_namespace,
        "train_replicas": int(args.train_replicas),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p794_script": str(P794_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FRESH-NAMESPACE: evaluation rows come from a namespace independent of the train rows.",
            "FROZEN-SELECTOR: support-line keys and line values are selected from train data and not re-ranked on evaluation outcomes.",
            "CHOSEN-SECRET-CALIBRATION: train calibration rows use known deterministic secrets and are charged explicitly.",
            "MANY-TARGET: cost ratios are meaningful only for batches where enough fresh targets reuse trained support lines.",
            "MATCHED-CONTROL: rotated trained line-value controls preserve selected line keys and training calibration cost.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p795_support_line_fresh_namespace_validation",
        "parameters": {
            "budgets": budgets,
            "control_count": args.control_count,
            "eval_replicas": args.eval_replicas,
            "eval_seed_namespace": args.eval_seed_namespace,
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
    parser.add_argument("--eval-seed-namespace", default="supportlinevalid-v1")
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
                "best_by_cost": summary["summary"]["best_by_cost"],
                "claim_status": summary["claim_status"],
                "budget_claims": [
                    {
                        "budget": item["budget"],
                        "claim": item["budget_claim"],
                        "cost_over_rho": item["aggregate"]["covered_total_unit_cost_over_recovered_rho"],
                        "max_control": item["aggregate"]["max_control_recovered_row_count"],
                        "recovered": item["aggregate"]["recovered_row_count"],
                    }
                    for item in summary["summary"]["budget_results"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
