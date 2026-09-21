#!/usr/bin/env python3
"""P794 public budget selector for support-line calibration."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P793_SCRIPT = TASK_DIR / "low_term_total2_p793_support_line_calibration_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p794_support_line_budget_selector_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p794_support_line_budget_selector.md"
SCHEMA = "ecdlp.low_term_total2_p794_support_line_budget_selector.v1"
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


def calibration_sort_key(item: tuple[tuple[int, int, int, int], dict[str, Any]]) -> tuple[int, int, int, tuple[int, int, int, int]]:
    key, value = item
    return (
        int(value["candidate_row_count"]),
        int(value["candidate_form_count"]),
        -int(sum(key)),
        tuple(-int(part) for part in key),
    )


def selected_calibrations(
    calibrated: dict[tuple[int, int, int, int], dict[str, Any]],
    budget: int,
) -> dict[tuple[int, int, int, int], dict[str, Any]]:
    ranked = sorted(calibrated.items(), key=calibration_sort_key, reverse=True)
    return dict(ranked[: min(int(budget), len(ranked))])


def prepare_target(
    p793: Any,
    p792: Any,
    p789: Any,
    p787: Any,
    p784: Any,
    stack: dict[str, Any],
    dest_item: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    rows_by_replica = []
    for replica in range(int(args.replicas)):
        dest_case = p787.destination_case(p784, dest_item, args.eval_seed_namespace, replica)
        rows, order = p784.collect_destination(stack, dest_case, args)
        rows_by_replica.append((replica, rows, order))
    orders = sorted({order for _replica, _rows, order in rows_by_replica})
    if len(orders) != 1:
        raise ValueError(f"target {dest_item['target']} produced multiple orders: {orders}")
    order = int(orders[0])
    records, rows_meta = p792.collect_form_records(p789, rows_by_replica, str(dest_item["target"]))
    all_calibrated = p793.select_line_calibrations(records, order, int(args.min_line_rows))
    return {
        "all_calibrated": all_calibrated,
        "dest_group_key": str(dest_item.get("group_key") or dest_item.get("key") or dest_item["target"]),
        "dest_target": str(dest_item["target"]),
        "form_record_count": len(records),
        "line_stats": p793.line_stats(records, order),
        "order": order,
        "records": records,
        "replicas": int(args.replicas),
        "row_count": len(rows_meta),
        "rows_meta": rows_meta,
    }


def evaluate_prepared_target_budget(
    p793: Any,
    prepared: dict[str, Any],
    budget: int,
    args: argparse.Namespace,
) -> dict[str, Any]:
    order = int(prepared["order"])
    records = prepared["records"]
    rows_meta = prepared["rows_meta"]
    all_calibrated = prepared["all_calibrated"]
    calibrated = selected_calibrations(all_calibrated, int(budget))
    calibration_row_keys = {item["calibration_row_key"] for item in calibrated.values()}
    primary = p793.score_records(records, rows_meta, calibrated, calibration_row_keys, order, int(args.field_weight))
    controls = []
    for control_index in range(int(args.control_count)):
        control_calibrated = p793.rotate_calibrations(calibrated, control_index + 1)
        controls.append(
            {
                "control_index": control_index,
                "result": p793.score_records(
                    records,
                    rows_meta,
                    control_calibrated,
                    calibration_row_keys,
                    order,
                    int(args.field_weight),
                ),
            }
        )
    selected_sample = sorted(calibrated.values(), key=lambda item: (item["candidate_row_count"], item["candidate_form_count"]), reverse=True)[:12]
    return {
        "available_line_count": len(all_calibrated),
        "budget": int(budget),
        "calibrated_line_count": len(calibrated),
        "controls": controls,
        "dest_group_key": prepared["dest_group_key"],
        "dest_target": prepared["dest_target"],
        "form_record_count": prepared["form_record_count"],
        "line_stats": prepared["line_stats"],
        "order": order,
        "primary": primary,
        "replicas": prepared["replicas"],
        "row_count": prepared["row_count"],
        "selected_line_sample": [
            {
                "candidate_form_count": item["candidate_form_count"],
                "candidate_row_count": item["candidate_row_count"],
                "line_key": item["line_key"],
            }
            for item in selected_sample
        ],
    }


def aggregate_budget(targets: list[dict[str, Any]]) -> dict[str, Any]:
    keys = [
        "all_population_rho_baseline",
        "all_population_total_unit_cost",
        "calibration_online_group_additions",
        "calibration_row_count",
        "covered_online_group_additions",
        "covered_target_count",
        "covered_target_rho_baseline",
        "covered_total_unit_cost",
        "recovered_form_count",
        "recovered_row_count",
        "recovered_rho_baseline",
        "scored_form_count",
        "target_row_mismatch_count",
        "total_field_ops",
    ]
    totals = {key: sum(int((target["primary"] or {}).get(key) or 0) for target in targets) for key in keys}
    totals.update(
        {
            "all_population_total_unit_cost_over_recovered_rho": ratio(
                totals["all_population_total_unit_cost"],
                totals["recovered_rho_baseline"],
            ),
            "available_line_count": sum(int(target.get("available_line_count") or 0) for target in targets),
            "calibrated_line_count": sum(int(target.get("calibrated_line_count") or 0) for target in targets),
            "covered_total_unit_cost_over_recovered_rho": ratio(
                totals["covered_total_unit_cost"],
                totals["recovered_rho_baseline"],
            ),
            "covered_total_unit_cost_over_target_rho": ratio(
                totals["covered_total_unit_cost"],
                totals["covered_target_rho_baseline"],
            ),
            "recovered_row_rate_over_covered": ratio(totals["recovered_row_count"], totals["covered_target_count"]),
            "target_count": len(targets),
        }
    )
    control_totals = []
    control_count = max((len(target.get("controls") or []) for target in targets), default=0)
    for control_index in range(control_count):
        recovered = sum(
            int(target["controls"][control_index]["result"].get("recovered_row_count") or 0)
            for target in targets
            if control_index < len(target.get("controls") or [])
        )
        covered_cost = sum(
            int(target["controls"][control_index]["result"].get("covered_total_unit_cost") or 0)
            for target in targets
            if control_index < len(target.get("controls") or [])
        )
        recovered_rho = sum(
            int(target["controls"][control_index]["result"].get("recovered_rho_baseline") or 0)
            for target in targets
            if control_index < len(target.get("controls") or [])
        )
        control_totals.append(
            {
                "control_index": control_index,
                "covered_total_unit_cost": covered_cost,
                "covered_total_unit_cost_over_recovered_rho": ratio(covered_cost, recovered_rho),
                "recovered_rho_baseline": recovered_rho,
                "recovered_row_count": recovered,
            }
        )
    max_control_recovered = max((item["recovered_row_count"] for item in control_totals), default=0)
    totals["control_totals"] = control_totals
    totals["max_control_recovered_row_count"] = max_control_recovered
    totals["primary_minus_max_control_recovered_rows"] = totals["recovered_row_count"] - max_control_recovered
    return totals


def determine_budget_claim(item: dict[str, Any]) -> str:
    aggregate = item["aggregate"]
    if int(aggregate["calibrated_line_count"]) == 0:
        return "no_calibrated_lines"
    if int(aggregate["recovered_row_count"]) <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_controls"
    if (aggregate["covered_total_unit_cost_over_recovered_rho"] or 10**9) < 1.0:
        return "below_rho"
    return "cost_boundary"


def determine_claim(summary: dict[str, Any]) -> str:
    if any(item["budget_claim"] == "below_rho" for item in summary["budget_results"]):
        return "P794_SUPPORT_LINE_BUDGET_SELECTOR_BELOW_RHO_SIGNAL"
    if any(item["budget_claim"] == "cost_boundary" for item in summary["budget_results"]):
        return "P794_SUPPORT_LINE_BUDGET_SELECTOR_COST_BOUNDARY"
    return "NEGATIVE_RESULT_P794_SUPPORT_LINE_BUDGET_SELECTOR_NO_CONTROLLED_RECOVERY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p793 = load_module("ecdlp_p793_for_p794", P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p794", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p794", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p794", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p794", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p794", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p794", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p794", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p794", p782.P780_SCRIPT)
    stack = p780.load_stack()
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    budgets = csv_ints(args.budgets)
    prepared_targets = [
        prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], args)
        for key in required
    ]
    budget_results = []
    for budget in budgets:
        targets = [
            evaluate_prepared_target_budget(p793, prepared, budget, args)
            for prepared in prepared_targets
        ]
        result = {
            "aggregate": aggregate_budget(targets),
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
        "replicas": int(args.replicas),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p793_script": str(P793_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC-SELECTOR: line ranking uses public row/form reuse counts, not recovered-secret outcomes.",
            "CHOSEN-SECRET-CALIBRATION: selected calibration rows use known deterministic secrets and are excluded from held-out scoring.",
            "SUPPORT-LINE-LOCAL: calibration is only for repeated public support/coefficient-ratio lines.",
            "MATCHED-CONTROL: rotated-line controls preserve selected line count and calibration row set.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p794_support_line_budget_selector",
        "parameters": {
            "budgets": budgets,
            "control_count": args.control_count,
            "eval_seed_namespace": args.eval_seed_namespace,
            "field_weight": args.field_weight,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_line_rows": args.min_line_rows,
            "replicas": args.replicas,
            "row_policy": args.row_policy,
            "sparse_policies": csv_strings(args.sparse_policies),
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
    parser.add_argument("--eval-seed-namespace", default="supportline20-v1")
    parser.add_argument("--replicas", type=int, default=20)
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
