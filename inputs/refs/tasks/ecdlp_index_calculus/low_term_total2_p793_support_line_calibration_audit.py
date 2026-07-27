#!/usr/bin/env python3
"""P793 support-line local calibration audit."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P792_SCRIPT = TASK_DIR / "low_term_total2_p792_support_pair_calibration_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p793_support_line_calibration_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p793_support_line_calibration_audit.md"
SCHEMA = "ecdlp.low_term_total2_p793_support_line_calibration_audit.v1"


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


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def line_parts(record: dict[str, Any], order: int) -> dict[str, Any] | None:
    c1, c2 = [int(value) % order for value in record["factor_coeffs"]]
    if c1:
        try:
            inv = pow(c1, -1, order)
        except ValueError:
            return None
        ratio_value = (c2 * inv) % order
        return {
            "line_key": (*record["support"], 1, int(ratio_value)),
            "scale": c1,
        }
    if c2:
        return {
            "line_key": (*record["support"], 0, 1),
            "scale": c2,
        }
    return None


def compact_line_record(record: dict[str, Any], order: int) -> dict[str, Any]:
    parts = line_parts(record, order) or {"line_key": (*record["support"], None, None), "scale": None}
    return {
        "coeffs": record["factor_coeffs"],
        "form_index": int(record["form_index"]),
        "line_key": list(parts["line_key"]),
        "replica": int(record["replica"]),
        "rhs_known": int(record["rhs_known"]),
        "row_index": int(record["row_index"]),
        "row_key": record["row_key"],
        "scale": parts["scale"],
        "seed_label": record["seed_label"],
        "support": list(record["support"]),
        "target": record["target"],
    }


def select_line_calibrations(
    records: list[dict[str, Any]],
    order: int,
    min_line_rows: int,
) -> dict[tuple[int, int, int, int], dict[str, Any]]:
    grouped: dict[tuple[int, int, int, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        parts = line_parts(record, order)
        if parts is None:
            continue
        grouped[parts["line_key"]].append({**record, "_line_scale": int(parts["scale"])})
    calibrated = {}
    for line_key, items in sorted(grouped.items()):
        row_keys = {item["row_key"] for item in items}
        if len(row_keys) < min_line_rows:
            continue
        calibration = items[0]
        try:
            line_value = (int(calibration["rhs_known"]) * pow(int(calibration["_line_scale"]), -1, order)) % order
        except ValueError:
            continue
        calibrated[line_key] = {
            "calibration_form": compact_line_record(calibration, order),
            "calibration_row_key": calibration["row_key"],
            "candidate_form_count": len(items),
            "candidate_row_count": len(row_keys),
            "field_ops": {
                "field_additions": 0,
                "field_inversions": 1,
                "field_multiplications": 1,
                "total_field_ops": 2,
            },
            "line_key": list(line_key),
            "line_value": int(line_value),
        }
    return calibrated


def rotate_calibrations(
    calibrated: dict[tuple[int, int, int, int], dict[str, Any]],
    shift: int,
) -> dict[tuple[int, int, int, int], dict[str, Any]]:
    keys = sorted(calibrated)
    if len(keys) < 2:
        return calibrated
    shift = shift % len(keys)
    if shift == 0:
        shift = 1
    rotated = {}
    for index, key in enumerate(keys):
        donor_key = keys[(index + shift) % len(keys)]
        rotated[key] = {
            **calibrated[key],
            "control_donor_line_key": list(donor_key),
            "line_value": int(calibrated[donor_key]["line_value"]),
        }
    return rotated


def line_stats(records: list[dict[str, Any]], order: int) -> dict[str, Any]:
    grouped: dict[tuple[int, int, int, int], set[str]] = defaultdict(set)
    form_counts = Counter()
    for record in records:
        parts = line_parts(record, order)
        if parts is None:
            continue
        grouped[parts["line_key"]].add(record["row_key"])
        form_counts[parts["line_key"]] += 1
    top = [
        {
            "candidate_form_count": int(form_counts[key]),
            "candidate_row_count": len(rows),
            "line_key": list(key),
        }
        for key, rows in grouped.items()
    ]
    top.sort(key=lambda item: (item["candidate_row_count"], item["candidate_form_count"]), reverse=True)
    return {
        "calibratable_line_count": sum(1 for rows in grouped.values() if len(rows) >= 2),
        "line_count": len(grouped),
        "repeated_form_line_count": sum(1 for key, count in form_counts.items() if count >= 2),
        "top_lines": top[:20],
    }


def score_records(
    records: list[dict[str, Any]],
    rows_meta: dict[str, dict[str, Any]],
    calibrated: dict[tuple[int, int, int, int], dict[str, Any]],
    calibration_row_keys: set[str],
    order: int,
    field_weight: int,
) -> dict[str, Any]:
    row_results: dict[str, dict[str, Any]] = {}
    scored_form_count = 0
    recovered_form_count = 0
    ops = Counter()
    recovered_samples = []
    for record in records:
        parts = line_parts(record, order)
        if parts is None or parts["line_key"] not in calibrated or record["row_key"] in calibration_row_keys:
            continue
        line_value = int(calibrated[parts["line_key"]]["line_value"])
        known_sum = (int(parts["scale"]) * line_value) % order
        try:
            secret = ((int(record["rhs"]) - known_sum) * pow(int(record["q_coeff"]), -1, order)) % order
        except ValueError:
            continue
        scored_form_count += 1
        ops["field_additions"] += 1
        ops["field_inversions"] += 1
        ops["field_multiplications"] += 2
        matches = secret == int(record["expected_secret"])
        if matches:
            recovered_form_count += 1
        row = row_results.setdefault(
            record["row_key"],
            {
                **rows_meta[record["row_key"]],
                "matched_forms": [],
                "scored_form_count": 0,
            },
        )
        row["scored_form_count"] += 1
        if matches and len(row["matched_forms"]) < 4:
            row["matched_forms"].append(
                {
                    "form_index": int(record["form_index"]),
                    "line_key": list(parts["line_key"]),
                    "recovered_secret": int(secret),
                    "support": list(record["support"]),
                }
            )
        if matches and len(recovered_samples) < 16:
            recovered_samples.append(
                {
                    "form_index": int(record["form_index"]),
                    "line_key": list(parts["line_key"]),
                    "recovered_secret": int(secret),
                    "row_key": record["row_key"],
                    "seed_label": record["seed_label"],
                    "support": list(record["support"]),
                    "target": record["target"],
                }
            )
    ops["total_field_ops"] = ops["field_additions"] + ops["field_inversions"] + ops["field_multiplications"]
    calibration_ops = Counter()
    for item in calibrated.values():
        calibration_ops.update(item.get("field_ops") or {})
    calibration_ops["total_field_ops"] = (
        calibration_ops["field_additions"]
        + calibration_ops["field_inversions"]
        + calibration_ops["field_multiplications"]
    )
    recovered_rows = [item for item in row_results.values() if item["matched_forms"]]
    target_rows = list(row_results.values())
    calibration_online = sum(rows_meta[key]["online_group_additions"] for key in calibration_row_keys)
    covered_online = calibration_online + sum(int(item["online_group_additions"]) for item in target_rows)
    all_population_online = sum(int(item["online_group_additions"]) for item in rows_meta.values())
    total_field_ops = int(ops["total_field_ops"]) + int(calibration_ops["total_field_ops"])
    recovered_rho = sum(int(item["generic_rho_steps"]) for item in recovered_rows)
    target_rho = sum(int(item["generic_rho_steps"]) for item in target_rows)
    all_population_rho = sum(
        int(item["generic_rho_steps"]) for key, item in rows_meta.items() if key not in calibration_row_keys
    )
    covered_total = covered_online + field_weight * total_field_ops
    all_population_total = all_population_online + field_weight * total_field_ops
    return {
        "all_population_rho_baseline": all_population_rho,
        "all_population_total_unit_cost": all_population_total,
        "all_population_total_unit_cost_over_recovered_rho": ratio(all_population_total, recovered_rho),
        "calibration_online_group_additions": calibration_online,
        "calibration_row_count": len(calibration_row_keys),
        "calibration_field_ops": dict(calibration_ops),
        "covered_online_group_additions": covered_online,
        "covered_target_count": len(target_rows),
        "covered_target_rho_baseline": target_rho,
        "covered_total_unit_cost": covered_total,
        "covered_total_unit_cost_over_recovered_rho": ratio(covered_total, recovered_rho),
        "covered_total_unit_cost_over_target_rho": ratio(covered_total, target_rho),
        "field_op_weight": field_weight,
        "recovered_form_count": recovered_form_count,
        "recovered_row_count": len(recovered_rows),
        "recovered_row_rate_over_covered": ratio(len(recovered_rows), len(target_rows)),
        "recovered_rho_baseline": recovered_rho,
        "recovered_samples": recovered_samples,
        "scored_form_count": scored_form_count,
        "scoring_field_ops": dict(ops),
        "target_row_mismatch_count": len(target_rows) - len(recovered_rows),
        "total_field_ops": total_field_ops,
    }


def evaluate_target(p792: Any, p789: Any, p787: Any, p784: Any, stack: dict[str, Any], dest_item: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
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
    calibrated = select_line_calibrations(records, order, int(args.min_line_rows))
    calibration_row_keys = {item["calibration_row_key"] for item in calibrated.values()}
    primary = score_records(records, rows_meta, calibrated, calibration_row_keys, order, int(args.field_weight))
    controls = []
    for control_index in range(int(args.control_count)):
        control_calibrated = rotate_calibrations(calibrated, control_index + 1)
        controls.append(
            {
                "control_index": control_index,
                "result": score_records(
                    records,
                    rows_meta,
                    control_calibrated,
                    calibration_row_keys,
                    order,
                    int(args.field_weight),
                ),
            }
        )
    details = sorted(
        calibrated.values(),
        key=lambda item: (int(item["candidate_row_count"]), int(item["candidate_form_count"])),
        reverse=True,
    )
    return {
        "calibrated_line_count": len(calibrated),
        "control_count": int(args.control_count),
        "controls": controls,
        "dest_group_key": str(dest_item.get("group_key") or dest_item.get("key") or dest_item["target"]),
        "dest_target": str(dest_item["target"]),
        "form_record_count": len(records),
        "line_detail_sample": [
            {
                "calibration_form": item["calibration_form"],
                "candidate_form_count": item["candidate_form_count"],
                "candidate_row_count": item["candidate_row_count"],
                "line_key": item["line_key"],
            }
            for item in details[:20]
        ],
        "line_stats": line_stats(records, order),
        "order": order,
        "primary": primary,
        "replicas": int(args.replicas),
        "row_count": len(rows_meta),
    }


def aggregate_results(targets: list[dict[str, Any]]) -> dict[str, Any]:
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


def determine_claim(summary: dict[str, Any]) -> str:
    aggregate = summary["aggregate"]
    if int(aggregate["calibrated_line_count"]) == 0:
        return "NEGATIVE_RESULT_P793_NO_SUPPORT_LINE_CALIBRATION_SYSTEMS"
    if int(aggregate["recovered_row_count"]) <= int(aggregate["max_control_recovered_row_count"]):
        return "NEGATIVE_RESULT_P793_SUPPORT_LINE_RECOVERY_DOES_NOT_BEAT_CONTROLS"
    if (
        int(aggregate["recovered_row_count"]) > 0
        and (aggregate["covered_total_unit_cost_over_recovered_rho"] or 10**9) < 1.0
    ):
        return "P793_SUPPORT_LINE_CALIBRATION_BELOW_RHO_MANY_TARGET_SIGNAL"
    return "P793_SUPPORT_LINE_CALIBRATION_COST_BOUNDARY_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p792 = load_module("ecdlp_p792_for_p793", P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p793", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p793", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p793", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p793", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p793", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p793", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p793", p782.P780_SCRIPT)
    stack = p780.load_stack()
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    targets = [evaluate_target(p792, p789, p787, p784, stack, base_groups[key], args) for key in required]
    summary = {
        "aggregate": aggregate_results(targets),
        "eval_seed_namespace": args.eval_seed_namespace,
        "replicas": int(args.replicas),
        "targets": targets,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p792_script": str(P792_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CHOSEN-SECRET-CALIBRATION: calibration rows use known deterministic secrets and are excluded from held-out scoring.",
            "SUPPORT-LINE-LOCAL: calibration is only for repeated public support/coefficient-ratio lines; arbitrary target descent is not shown.",
            "MANY-TARGET: cost ratios are meaningful only for batches where enough targets reuse calibrated support lines.",
            "MATCHED-CONTROL: rotated-line controls preserve calibrated line count and calibration row set.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p793_support_line_calibration_audit",
        "parameters": {
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
    parser.add_argument("--eval-seed-namespace", default="supportline-v1")
    parser.add_argument("--replicas", type=int, default=5)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
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
                "aggregate": summary["summary"]["aggregate"],
                "claim_status": summary["claim_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
