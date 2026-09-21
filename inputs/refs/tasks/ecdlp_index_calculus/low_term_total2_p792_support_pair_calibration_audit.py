#!/usr/bin/env python3
"""P792 support-pair local calibration audit."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P789_SCRIPT = TASK_DIR / "low_term_total2_p789_recovered_row_structural_extraction.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p792_support_pair_calibration_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p792_support_pair_calibration_audit.md"
SCHEMA = "ecdlp.low_term_total2_p792_support_pair_calibration_audit.v1"


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


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def form_key(record: dict[str, Any]) -> str:
    return f"{record['row_key']}:{record['form_index']}"


def compact_form(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "coeffs": record["factor_coeffs"],
        "form_index": int(record["form_index"]),
        "replica": int(record["replica"]),
        "rhs_known": int(record["rhs_known"]),
        "row_index": int(record["row_index"]),
        "row_key": record["row_key"],
        "seed_label": record["seed_label"],
        "support": list(record["support"]),
        "target": record["target"],
    }


def row_cost(row: dict[str, Any]) -> int:
    return int((row.get("cost_model") or {}).get("collection_online_group_additions") or 0)


def collect_form_records(
    p789: Any,
    rows_by_replica: list[tuple[int, list[dict[str, Any]], int]],
    target: str,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    records = []
    rows_meta: dict[str, dict[str, Any]] = {}
    for replica, rows, order in rows_by_replica:
        for row_index, row in enumerate(rows):
            key = f"{target}:{replica}:{row_index}"
            rows_meta[key] = {
                "generic_rho_steps": int(row.get("generic_rho_steps") or 0),
                "online_group_additions": row_cost(row),
                "replica": int(replica),
                "row_index": int(row_index),
                "seed_label": str(row.get("seed_label")),
                "target": str(row.get("target")),
            }
            for form_index, form in enumerate(row.get("forms") or []):
                coeffs = p789.form_coeffs(form, order)
                if not coeffs or not coeffs[0]:
                    continue
                support = p789.form_support(coeffs, order)
                if len(support) != 2:
                    continue
                factor_coeffs = [int(coeffs[1 + index]) % order for index in support]
                if not all(factor_coeffs):
                    continue
                rhs_known = (int(form["rhs"]) - int(coeffs[0]) * int(row["_expected_secret"])) % order
                records.append(
                    {
                        "expected_secret": int(row["_expected_secret"]) % order,
                        "factor_coeffs": factor_coeffs,
                        "form_index": int(form_index),
                        "generic_rho_steps": int(row.get("generic_rho_steps") or 0),
                        "online_group_additions": row_cost(row),
                        "q_coeff": int(coeffs[0]) % order,
                        "replica": int(replica),
                        "rhs": int(form["rhs"]) % order,
                        "rhs_known": int(rhs_known),
                        "row_index": int(row_index),
                        "row_key": key,
                        "seed_label": str(row.get("seed_label")),
                        "support": tuple(int(index) for index in support),
                        "target": str(row.get("target")),
                    }
                )
    records.sort(key=lambda item: (item["support"], item["replica"], item["row_index"], item["form_index"]))
    return records, rows_meta


def solve_two_by_two(left: dict[str, Any], right: dict[str, Any], order: int) -> dict[str, Any] | None:
    c1, c2 = [int(value) % order for value in left["factor_coeffs"]]
    d1, d2 = [int(value) % order for value in right["factor_coeffs"]]
    det = (c1 * d2 - d1 * c2) % order
    if not det:
        return None
    try:
        inv_det = pow(det, -1, order)
    except ValueError:
        return None
    r = int(left["rhs_known"]) % order
    s = int(right["rhs_known"]) % order
    x_value = ((r * d2 - s * c2) * inv_det) % order
    y_value = ((c1 * s - d1 * r) * inv_det) % order
    support = tuple(int(index) for index in left["support"])
    return {
        "calibration_forms": [compact_form(left), compact_form(right)],
        "calibration_row_keys": sorted({left["row_key"], right["row_key"]}),
        "determinant": int(det),
        "field_ops": {
            "field_additions": 3,
            "field_inversions": 1,
            "field_multiplications": 6,
            "total_field_ops": 10,
        },
        "support": list(support),
        "values": {
            str(support[0]): int(x_value),
            str(support[1]): int(y_value),
        },
    }


def select_support_solutions(records: list[dict[str, Any]], order: int) -> dict[tuple[int, int], dict[str, Any]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[tuple(record["support"])].append(record)
    solved = {}
    for support, items in sorted(grouped.items()):
        for left_pos, left in enumerate(items):
            for right in items[left_pos + 1 :]:
                if left["row_key"] == right["row_key"]:
                    continue
                solution = solve_two_by_two(left, right, order)
                if solution is not None:
                    solution["candidate_form_count"] = len(items)
                    solution["candidate_row_count"] = len({item["row_key"] for item in items})
                    solution["support_key"] = ",".join(str(value) for value in support)
                    solved[support] = solution
                    break
            if support in solved:
                break
    return solved


def support_group_stats(records: list[dict[str, Any]], order: int) -> dict[str, Any]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[tuple(record["support"])].append(record)
    repeated_form = 0
    repeated_row = 0
    independent = 0
    top = []
    for support, items in grouped.items():
        row_count = len({item["row_key"] for item in items})
        form_count = len(items)
        has_independent = False
        if row_count >= 2:
            for left_pos, left in enumerate(items):
                for right in items[left_pos + 1 :]:
                    if left["row_key"] == right["row_key"]:
                        continue
                    if solve_two_by_two(left, right, order) is not None:
                        has_independent = True
                        break
                if has_independent:
                    break
        if form_count >= 2:
            repeated_form += 1
        if row_count >= 2:
            repeated_row += 1
        if has_independent:
            independent += 1
        top.append(
            {
                "candidate_form_count": form_count,
                "candidate_row_count": row_count,
                "has_independent_pair": has_independent,
                "support": list(support),
            }
        )
    top.sort(
        key=lambda item: (
            bool(item["has_independent_pair"]),
            int(item["candidate_row_count"]),
            int(item["candidate_form_count"]),
        ),
        reverse=True,
    )
    return {
        "independent_support_count": independent,
        "repeated_form_support_count": repeated_form,
        "repeated_row_support_count": repeated_row,
        "support_pair_count": len(grouped),
        "top_supports": top[:20],
    }


def rotate_solutions(
    solved: dict[tuple[int, int], dict[str, Any]],
    shift: int,
) -> dict[tuple[int, int], dict[str, Any]]:
    supports = sorted(solved)
    if len(supports) < 2:
        return solved
    shift = shift % len(supports)
    if shift == 0:
        shift = 1
    rotated = {}
    for index, support in enumerate(supports):
        donor = solved[supports[(index + shift) % len(supports)]]
        donor_values = [int(value) for _key, value in sorted(donor["values"].items(), key=lambda item: int(item[0]))]
        rotated[support] = {
            **solved[support],
            "control_donor_support": list(supports[(index + shift) % len(supports)]),
            "values": {
                str(support[0]): donor_values[0],
                str(support[1]): donor_values[1],
            },
        }
    return rotated


def score_records(
    records: list[dict[str, Any]],
    rows_meta: dict[str, dict[str, Any]],
    solved: dict[tuple[int, int], dict[str, Any]],
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
        support = tuple(record["support"])
        if support not in solved or record["row_key"] in calibration_row_keys:
            continue
        values = solved[support]["values"]
        x_value = int(values[str(support[0])])
        y_value = int(values[str(support[1])])
        c1, c2 = [int(value) % order for value in record["factor_coeffs"]]
        acc = (int(record["rhs"]) - c1 * x_value - c2 * y_value) % order
        try:
            secret = (acc * pow(int(record["q_coeff"]), -1, order)) % order
        except ValueError:
            continue
        scored_form_count += 1
        ops["field_additions"] += 2
        ops["field_inversions"] += 1
        ops["field_multiplications"] += 3
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
                    "recovered_secret": int(secret),
                    "support": list(support),
                }
            )
        if matches and len(recovered_samples) < 16:
            recovered_samples.append(
                {
                    "form_index": int(record["form_index"]),
                    "recovered_secret": int(secret),
                    "row_key": record["row_key"],
                    "seed_label": record["seed_label"],
                    "support": list(support),
                    "target": record["target"],
                }
            )
    ops["total_field_ops"] = ops["field_additions"] + ops["field_inversions"] + ops["field_multiplications"]
    recovered_rows = [item for item in row_results.values() if item["matched_forms"]]
    target_rows = list(row_results.values())
    calibration_online = sum(rows_meta[key]["online_group_additions"] for key in calibration_row_keys)
    covered_online = calibration_online + sum(int(item["online_group_additions"]) for item in target_rows)
    all_population_online = sum(int(item["online_group_additions"]) for key, item in rows_meta.items())
    solve_ops = Counter()
    for item in solved.values():
        solve_ops.update(item.get("field_ops") or {})
    solve_ops["total_field_ops"] = (
        solve_ops["field_additions"] + solve_ops["field_inversions"] + solve_ops["field_multiplications"]
    )
    total_field_ops = int(ops["total_field_ops"]) + int(solve_ops["total_field_ops"])
    recovered_rho = sum(int(item["generic_rho_steps"]) for item in recovered_rows)
    target_rho = sum(int(item["generic_rho_steps"]) for item in target_rows)
    all_population_rho = sum(int(item["generic_rho_steps"]) for key, item in rows_meta.items() if key not in calibration_row_keys)
    covered_total_unit_cost = covered_online + field_weight * total_field_ops
    all_population_total_unit_cost = all_population_online + field_weight * total_field_ops
    return {
        "all_population_rho_baseline": all_population_rho,
        "all_population_total_unit_cost": all_population_total_unit_cost,
        "all_population_total_unit_cost_over_recovered_rho": ratio(all_population_total_unit_cost, recovered_rho),
        "calibration_online_group_additions": calibration_online,
        "calibration_row_count": len(calibration_row_keys),
        "covered_online_group_additions": covered_online,
        "covered_target_count": len(target_rows),
        "covered_target_rho_baseline": target_rho,
        "covered_total_unit_cost": covered_total_unit_cost,
        "covered_total_unit_cost_over_recovered_rho": ratio(covered_total_unit_cost, recovered_rho),
        "covered_total_unit_cost_over_target_rho": ratio(covered_total_unit_cost, target_rho),
        "field_op_weight": field_weight,
        "recovered_form_count": recovered_form_count,
        "recovered_row_count": len(recovered_rows),
        "recovered_row_rate_over_covered": ratio(len(recovered_rows), len(target_rows)),
        "recovered_rho_baseline": recovered_rho,
        "recovered_samples": recovered_samples,
        "scored_form_count": scored_form_count,
        "scoring_field_ops": dict(ops),
        "solve_field_ops": dict(solve_ops),
        "target_row_mismatch_count": len(target_rows) - len(recovered_rows),
        "total_field_ops": total_field_ops,
    }


def evaluate_target(
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
    records, rows_meta = collect_form_records(p789, rows_by_replica, str(dest_item["target"]))
    support_stats = support_group_stats(records, order)
    solved = select_support_solutions(records, order)
    calibration_row_keys = {
        key
        for solution in solved.values()
        for key in solution["calibration_row_keys"]
    }
    primary = score_records(records, rows_meta, solved, calibration_row_keys, order, int(args.field_weight))
    controls = []
    for control_index in range(int(args.control_count)):
        control_solved = rotate_solutions(solved, control_index + 1)
        controls.append(
            {
                "control_index": control_index,
                "result": score_records(
                    records,
                    rows_meta,
                    control_solved,
                    calibration_row_keys,
                    order,
                    int(args.field_weight),
                ),
            }
        )
    support_details = sorted(
        solved.values(),
        key=lambda item: (int(item["candidate_row_count"]), int(item["candidate_form_count"])),
        reverse=True,
    )
    return {
        "control_count": int(args.control_count),
        "controls": controls,
        "dest_group_key": str(dest_item.get("group_key") or dest_item.get("key") or dest_item["target"]),
        "dest_target": str(dest_item["target"]),
        "form_record_count": len(records),
        "order": order,
        "primary": primary,
        "replicas": int(args.replicas),
        "row_count": len(rows_meta),
        "solved_support_count": len(solved),
        "support_group_stats": support_stats,
        "support_detail_sample": [
            {
                "calibration_forms": item["calibration_forms"],
                "candidate_form_count": item["candidate_form_count"],
                "candidate_row_count": item["candidate_row_count"],
                "support": item["support"],
            }
            for item in support_details[:20]
        ],
    }


def aggregate_results(targets: list[dict[str, Any]]) -> dict[str, Any]:
    primary_keys = [
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
    totals = {key: sum(int((target["primary"] or {}).get(key) or 0) for target in targets) for key in primary_keys}
    totals.update(
        {
            "all_population_total_unit_cost_over_recovered_rho": ratio(
                totals["all_population_total_unit_cost"],
                totals["recovered_rho_baseline"],
            ),
            "covered_total_unit_cost_over_recovered_rho": ratio(
                totals["covered_total_unit_cost"],
                totals["recovered_rho_baseline"],
            ),
            "covered_total_unit_cost_over_target_rho": ratio(
                totals["covered_total_unit_cost"],
                totals["covered_target_rho_baseline"],
            ),
            "recovered_row_rate_over_covered": ratio(totals["recovered_row_count"], totals["covered_target_count"]),
            "solved_support_count": sum(int(target.get("solved_support_count") or 0) for target in targets),
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
    if int(aggregate["solved_support_count"]) == 0:
        return "NEGATIVE_RESULT_P792_NO_SUPPORT_PAIR_CALIBRATION_SYSTEMS"
    if int(aggregate["recovered_row_count"]) <= int(aggregate["max_control_recovered_row_count"]):
        return "NEGATIVE_RESULT_P792_SUPPORT_PAIR_RECOVERY_DOES_NOT_BEAT_CONTROLS"
    if (
        int(aggregate["recovered_row_count"]) > 0
        and (aggregate["covered_total_unit_cost_over_recovered_rho"] or 10**9) < 1.0
    ):
        return "P792_SUPPORT_PAIR_CALIBRATION_BELOW_RHO_MANY_TARGET_SIGNAL"
    if int(aggregate["recovered_row_count"]) > int(aggregate["max_control_recovered_row_count"]):
        return "P792_SUPPORT_PAIR_CALIBRATION_COST_BOUNDARY_SIGNAL"
    return "NEGATIVE_RESULT_P792_SUPPORT_PAIR_CALIBRATION_INCONCLUSIVE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p789 = load_module("ecdlp_p789_for_p792", P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p792", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p792", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p792", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p792", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p792", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p792", p782.P780_SCRIPT)
    stack = p780.load_stack()
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    targets = [
        evaluate_target(p789, p787, p784, stack, base_groups[key], args)
        for key in required
    ]
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
            "p789_script": str(P789_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CHOSEN-SECRET-CALIBRATION: calibration rows use known deterministic secrets and are excluded from held-out scoring.",
            "SUPPORT-PAIR-LOCAL: factor values are solved only for repeated two-factor support pairs; arbitrary target descent is not shown.",
            "MANY-TARGET: cost ratios are meaningful only for batches where enough targets reuse calibrated support pairs.",
            "MATCHED-CONTROL: rotated-value controls preserve solved support count and calibration row set.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p792_support_pair_calibration_audit",
        "parameters": {
            "control_count": args.control_count,
            "eval_seed_namespace": args.eval_seed_namespace,
            "field_weight": args.field_weight,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
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
    parser.add_argument("--eval-seed-namespace", default="supportpair-v1")
    parser.add_argument("--replicas", type=int, default=5)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
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
