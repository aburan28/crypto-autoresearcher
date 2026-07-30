#!/usr/bin/env python3
"""P800 form-construction support-pair forcing audit."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P799_SCRIPT = TASK_DIR / "low_term_total2_p799_exact_support_pair_constructive_generator.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p800_form_construction_support_pair_filter_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p800_form_construction_support_pair_filter.md"
SCHEMA = "ecdlp.low_term_total2_p800_form_construction_support_pair_filter.v1"
DEFAULT_BUDGETS = "32,128,512"


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


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in str(value))
    return "_".join(part for part in text.split("_") if part)


def seed_labels(count: int) -> list[str]:
    return [f"t{index:04d}" for index in range(int(count))]


def form_support(form: dict[str, Any], order: int) -> tuple[int, ...]:
    coeffs = [int(value) % int(order) for value in form["coeffs"]]
    return tuple(index for index, value in enumerate(coeffs[1:]) if value)


def form_line_key(p793: Any, form: dict[str, Any], order: int) -> tuple[int, int, int, int] | None:
    support = form_support(form, order)
    if len(support) != 2:
        return None
    coeffs = [int(value) % int(order) for value in form["coeffs"]]
    record = {
        "factor_coeffs": [coeffs[1 + support[0]], coeffs[1 + support[1]]],
        "support": support,
    }
    parts = p793.line_parts(record, int(order))
    if parts is None:
        return None
    return tuple(int(value) for value in parts["line_key"])


def filter_row_forms(
    p793: Any,
    rows: list[dict[str, Any]],
    order: int,
    policy_name: str,
    selected_lines: set[tuple[int, int, int, int]],
    selected_supports: set[tuple[int, int]],
    rotated_supports: set[tuple[int, int]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    filtered_rows = []
    stats = Counter()
    for row in rows:
        kept_forms = []
        for form in row.get("forms") or []:
            support = form_support(form, order)
            if len(support) != 2:
                continue
            line_key = form_line_key(p793, form, order)
            support_pair = tuple(int(value) for value in support)
            stats["two_factor_form_count"] += 1
            if support_pair in selected_supports:
                stats["selected_support_form_count"] += 1
            if line_key in selected_lines:
                stats["selected_line_form_count"] += 1
            keep = False
            if policy_name == "all_two_factor_control":
                keep = True
            elif policy_name == "requested_support_filter":
                keep = support_pair in selected_supports
            elif policy_name == "requested_line_filter":
                keep = line_key in selected_lines
            elif policy_name == "rotated_support_filter":
                keep = support_pair in rotated_supports
            else:
                raise ValueError(f"unknown policy {policy_name!r}")
            if keep:
                kept_forms.append(form)
        if kept_forms:
            filtered_rows.append({**row, "forms": kept_forms})
            stats["filtered_row_count"] += 1
            stats["filtered_form_count"] += len(kept_forms)
    return filtered_rows, {
        "filtered_form_count": int(stats.get("filtered_form_count") or 0),
        "filtered_row_count": int(stats.get("filtered_row_count") or 0),
        "selected_line_form_count": int(stats.get("selected_line_form_count") or 0),
        "selected_support_form_count": int(stats.get("selected_support_form_count") or 0),
        "two_factor_form_count": int(stats.get("two_factor_form_count") or 0),
    }


def collect_scan_rows(
    p746: Any,
    p748: Any,
    relprobe: Any,
    base_item: dict[str, Any],
    case: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], int]:
    verifier, record, inv = p746.load_target(relprobe, str(base_item["target"]))
    rows = []
    for seed_label in seed_labels(int(args.scan_seed_count)):
        full_seed = (
            f"ecdlp-p800-{args.scan_namespace}-{slug(base_item['target'])}:"
            f"{seed_label}:fb{case['factor_base_size']}:w{args.width}:{args.walk_mode}"
        )
        rows.append(
            p748.scan_export_walk(
                p746,
                relprobe,
                verifier,
                record,
                inv,
                str(base_item["target"]),
                int(case["factor_base_size"]),
                int(args.width),
                str(args.walk_mode),
                seed_label,
                full_seed,
                int(case["budget"]),
                min(24, int(case["budget"])),
                int(args.max_relations),
                int(args.max_subsets),
            )
        )
    return rows, int(inv["base_order"])


def evaluate_filtered_policy(
    p797: Any,
    p793: Any,
    p792: Any,
    p789: Any,
    p784: Any,
    train_prepared: dict[str, Any],
    trained: dict[tuple[int, int, int, int], dict[str, Any]],
    scanned_rows: list[dict[str, Any]],
    order: int,
    target: str,
    policy_name: str,
    selected_lines: set[tuple[int, int, int, int]],
    selected_supports: set[tuple[int, int]],
    rotated_supports: set[tuple[int, int]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    filtered_rows, filter_stats = filter_row_forms(
        p793,
        scanned_rows,
        int(order),
        policy_name,
        selected_lines,
        selected_supports,
        rotated_supports,
    )
    records, rows_meta = p792.collect_form_records(p789, [(0, filtered_rows, int(order))], target)
    prepared = {
        "dest_target": target,
        "order": int(order),
        "records": records,
        "row_count": len(rows_meta),
        "rows_meta": rows_meta,
    }
    row_keys = set(rows_meta)
    scored = p797.score_subset(
        p793,
        prepared,
        trained,
        row_keys,
        int(args.field_weight),
        int(args.control_count),
    )
    train_cost = p797.train_cost(trained, train_prepared)
    scan_online = sum(int((row.get("cost_model") or {}).get("collection_online_group_additions") or 0) for row in scanned_rows)
    generated_total = (
        int(train_cost["calibration_online_group_additions"])
        + scan_online
        + int(args.field_weight)
        * (int(train_cost["calibration_field_ops"]) + int(scored["scoring_field_ops"]))
    )
    recovered_rho = int(scored["primary"].get("recovered_rho_baseline") or 0)
    generated_rows = len(scanned_rows)
    return {
        "aggregate": {
            **filter_stats,
            "filtered_form_rate_over_two_factor": ratio(
                int(filter_stats.get("filtered_form_count") or 0),
                int(filter_stats.get("two_factor_form_count") or 0),
            ),
            "filtered_row_rate_over_scanned": ratio(int(filter_stats.get("filtered_row_count") or 0), generated_rows),
            "generated_once_train_total_unit_cost": generated_total,
            "generated_once_train_total_unit_cost_over_recovered_rho": ratio(generated_total, recovered_rho),
            "max_control_recovered_row_count": int(scored["max_control_recovered_row_count"]),
            "primary_minus_max_control_recovered_rows": int(scored["primary"].get("recovered_row_count") or 0)
            - int(scored["max_control_recovered_row_count"]),
            "recovered_row_count": int(scored["primary"].get("recovered_row_count") or 0),
            "recovered_rho_baseline": recovered_rho,
            "scanned_online_group_additions": scan_online,
            "scanned_row_count": generated_rows,
            "scored_form_count": int(scored["primary"].get("scored_form_count") or 0),
            "scoring_field_ops": int(scored["scoring_field_ops"]),
            "selected_line_form_rate": ratio(
                int(filter_stats.get("selected_line_form_count") or 0),
                int(filter_stats.get("two_factor_form_count") or 0),
            ),
            "selected_support_form_rate": ratio(
                int(filter_stats.get("selected_support_form_count") or 0),
                int(filter_stats.get("two_factor_form_count") or 0),
            ),
            "target_row_mismatch_count": int(scored["primary"].get("target_row_mismatch_count") or 0),
            "train_calibration_field_ops": int(train_cost["calibration_field_ops"]),
            "train_calibration_online_group_additions": int(train_cost["calibration_online_group_additions"]),
        },
        "policy": {"kind": policy_kind(policy_name), "name": policy_name},
    }


def policy_kind(policy_name: str) -> str:
    return {
        "all_two_factor_control": "broad_form_control",
        "requested_line_filter": "requested_line_filter_model",
        "requested_support_filter": "requested_support_filter_model",
        "rotated_support_filter": "rotated_support_control",
    }[policy_name]


def aggregate_policy_results(items: list[dict[str, Any]], policy_name: str) -> dict[str, Any]:
    totals = Counter()
    controls = []
    for item in items:
        aggregate = item["aggregate"]
        for key, value in aggregate.items():
            if isinstance(value, int):
                totals[key] += value
        controls.append(int(aggregate["max_control_recovered_row_count"]))
    recovered_rho = int(totals["recovered_rho_baseline"])
    scanned_rows = int(totals["scanned_row_count"])
    two_factor_forms = int(totals["two_factor_form_count"])
    return {
        "aggregate": {
            **dict(totals),
            "filtered_form_rate_over_two_factor": ratio(int(totals["filtered_form_count"]), two_factor_forms),
            "filtered_row_rate_over_scanned": ratio(int(totals["filtered_row_count"]), scanned_rows),
            "generated_once_train_total_unit_cost_over_recovered_rho": ratio(
                int(totals["generated_once_train_total_unit_cost"]),
                recovered_rho,
            ),
            "max_control_recovered_row_count": max(controls, default=0),
            "primary_minus_max_control_recovered_rows": int(totals["recovered_row_count"]) - max(controls, default=0),
            "selected_line_form_rate": ratio(int(totals["selected_line_form_count"]), two_factor_forms),
            "selected_support_form_rate": ratio(int(totals["selected_support_form_count"]), two_factor_forms),
            "target_count": len(items),
        },
        "policy": {"kind": policy_kind(policy_name), "name": policy_name},
        "target_results": items,
    }


def determine_policy_claim(policy_result: dict[str, Any], peer_results: dict[str, dict[str, Any]]) -> str:
    aggregate = policy_result["aggregate"]
    name = policy_result["policy"]["name"]
    if int(aggregate["filtered_form_count"]) == 0:
        return "no_filtered_forms"
    if int(aggregate["recovered_row_count"]) <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    ratio_value = aggregate["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9
    rotated = int((peer_results.get("rotated_support_filter") or {}).get("aggregate", {}).get("recovered_row_count") or 0)
    if name == "requested_support_filter" and int(aggregate["recovered_row_count"]) > rotated and ratio_value < 1.0:
        return "requested_support_scan_charged_below_rho"
    if name == "requested_support_filter" and int(aggregate["recovered_row_count"]) > rotated:
        return "requested_support_enrichment_cost_boundary"
    if name == "requested_line_filter" and ratio_value < 1.0:
        return "requested_line_scan_charged_below_rho"
    if name in {"all_two_factor_control", "rotated_support_filter"}:
        return "control_boundary"
    return "cost_boundary"


def determine_claim(summary: dict[str, Any]) -> str:
    claims = [
        policy_result["policy_claim"]
        for budget_result in summary["budget_results"]
        for policy_result in budget_result["policy_results"]
    ]
    if "requested_support_scan_charged_below_rho" in claims:
        return "P800_REQUESTED_SUPPORT_FORM_FILTER_BELOW_RHO_SIGNAL"
    if "requested_support_enrichment_cost_boundary" in claims:
        return "P800_REQUESTED_SUPPORT_FORM_FILTER_ENRICHMENT_COST_BOUNDARY"
    if "requested_line_scan_charged_below_rho" in claims:
        return "P800_REQUESTED_LINE_FORM_FILTER_BELOW_RHO_DIAGNOSTIC"
    return "NEGATIVE_RESULT_P800_FORM_FILTER_NO_SCAN_CHARGED_GENERATOR"


def best_result(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    viable = [
        item
        for item in items
        if item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] is not None
    ]
    if not viable:
        return None
    item = min(viable, key=lambda row: row["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"])
    aggregate = item["aggregate"]
    return {
        "filtered_form_count": aggregate["filtered_form_count"],
        "filtered_row_count": aggregate["filtered_row_count"],
        "filtered_row_rate_over_scanned": aggregate["filtered_row_rate_over_scanned"],
        "generated_once_train_total_unit_cost_over_recovered_rho": aggregate["generated_once_train_total_unit_cost_over_recovered_rho"],
        "policy": item["policy"]["name"],
        "policy_claim": item["policy_claim"],
        "recovered_row_count": aggregate["recovered_row_count"],
        "scanned_row_count": aggregate["scanned_row_count"],
        "selected_line_form_rate": aggregate["selected_line_form_rate"],
        "selected_support_form_rate": aggregate["selected_support_form_rate"],
    }


def rotated_supports_for(
    supports: set[tuple[int, int]],
    factor_base_size: int,
) -> set[tuple[int, int]]:
    rotated = set()
    fb_size = int(factor_base_size)
    for support in supports:
        shifted = tuple(sorted(((int(support[0]) + 1) % fb_size, (int(support[1]) + 3) % fb_size)))
        if shifted[0] != shifted[1]:
            rotated.add(shifted)
    return rotated


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p799 = load_module("ecdlp_p799_for_p800", P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p800", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p800", p798.P797_SCRIPT)
    p796 = p797.load_module("ecdlp_p796_for_p800", p797.P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p800", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p800", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p800", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p800", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p800", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p800", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p800", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p800", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p800", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p800", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p800", p782.P780_SCRIPT)
    stack = p780.load_stack()
    p746 = stack["p746"]
    p748 = stack["p748"]
    relprobe = stack["relprobe"]
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    budgets = csv_ints(args.budgets)

    train_args = p795.namespace_args(args, args.train_seed_namespace, int(args.train_replicas))
    print(f"preparing train namespace {args.train_seed_namespace}", flush=True)
    train_prepared = {
        key: p794.prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], train_args)
        for key in required
    }

    scan_bank = {}
    for group_key in required:
        case = p784.case_from_group(
            base_groups[group_key],
            p784.TRIM12_DELTA,
            args.scan_namespace,
            "p800",
            p784.DEST_SEED_COUNT,
            p784.DEST_POOL_COUNT,
        )
        print(f"scanning {group_key} rows={args.scan_seed_count}", flush=True)
        rows, order = collect_scan_rows(p746, p748, relprobe, base_groups[group_key], case, args)
        scan_bank[group_key] = {"case": case, "order": order, "rows": rows}

    policy_names = [
        "requested_line_filter",
        "requested_support_filter",
        "rotated_support_filter",
        "all_two_factor_control",
    ]
    budget_results = []
    all_policy_results = []
    for budget in budgets:
        print(f"scoring budget {budget}", flush=True)
        target_policy_results = {name: [] for name in policy_names}
        for group_key in required:
            trained = p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], int(budget))
            selected_lines = {tuple(int(part) for part in key) for key in trained}
            selected_supports = {tuple(int(part) for part in key[:2]) for key in trained}
            rotated = rotated_supports_for(selected_supports, int(base_groups[group_key]["factor_base_size"]))
            for policy_name in policy_names:
                target_policy_results[policy_name].append(
                    evaluate_filtered_policy(
                        p797,
                        p793,
                        p792,
                        p789,
                        p784,
                        train_prepared[group_key],
                        trained,
                        scan_bank[group_key]["rows"],
                        int(scan_bank[group_key]["order"]),
                        str(base_groups[group_key]["target"]),
                        policy_name,
                        selected_lines,
                        selected_supports,
                        rotated,
                        args,
                    )
                )
        policy_results = []
        for policy_name in policy_names:
            policy_results.append(aggregate_policy_results(target_policy_results[policy_name], policy_name))
        by_name = {item["policy"]["name"]: item for item in policy_results}
        for item in policy_results:
            item["budget"] = int(budget)
            item["policy_claim"] = determine_policy_claim(item, by_name)
            all_policy_results.append(item)
        budget_results.append(
            {
                "best_generated": best_result(policy_results),
                "budget": int(budget),
                "policy_results": policy_results,
            }
        )
    summary = {
        "best_generated": best_result(all_policy_results),
        "budget_results": budget_results,
        "scan_namespace": args.scan_namespace,
        "scan_seed_count": args.scan_seed_count,
        "train_seed_namespace": args.train_seed_namespace,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p799_script": str(P799_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "POST-ENUMERATION MODEL: forms are filtered after public relation construction; this is not a pre-hit support-pair generator.",
            "SCAN-CHARGED: every scanned row in the bank is charged, including rows with no requested support-pair forms.",
            "CONTROL-BOUND: rotated support filters test whether requested supports add value beyond similarly sized support sets.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p800_form_construction_support_pair_filter",
        "parameters": {
            "budgets": budgets,
            "control_count": args.control_count,
            "field_weight": args.field_weight,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_line_rows": args.min_line_rows,
            "row_policy": args.row_policy,
            "scan_namespace": args.scan_namespace,
            "scan_seed_count": args.scan_seed_count,
            "sparse_policies": args.sparse_policies,
            "train_replicas": args.train_replicas,
            "train_seed_namespace": args.train_seed_namespace,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact_budget_results = []
    for budget_result in payload["summary"]["budget_results"]:
        compact_policies = []
        for item in budget_result["policy_results"]:
            aggregate = item["aggregate"]
            compact_policies.append(
                {
                    "aggregate": {
                        "filtered_form_count": aggregate["filtered_form_count"],
                        "filtered_form_rate_over_two_factor": aggregate["filtered_form_rate_over_two_factor"],
                        "filtered_row_count": aggregate["filtered_row_count"],
                        "filtered_row_rate_over_scanned": aggregate["filtered_row_rate_over_scanned"],
                        "generated_once_train_total_unit_cost_over_recovered_rho": aggregate["generated_once_train_total_unit_cost_over_recovered_rho"],
                        "max_control_recovered_row_count": aggregate["max_control_recovered_row_count"],
                        "primary_minus_max_control_recovered_rows": aggregate["primary_minus_max_control_recovered_rows"],
                        "recovered_row_count": aggregate["recovered_row_count"],
                        "scanned_row_count": aggregate["scanned_row_count"],
                        "selected_line_form_rate": aggregate["selected_line_form_rate"],
                        "selected_support_form_rate": aggregate["selected_support_form_rate"],
                    },
                    "policy": item["policy"],
                    "policy_claim": item["policy_claim"],
                }
            )
        compact_budget_results.append(
            {
                "best_generated": budget_result["best_generated"],
                "budget": budget_result["budget"],
                "policy_results": compact_policies,
            }
        )
    return {
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **payload["summary"],
            "budget_results": compact_budget_results,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--scan-namespace", default="supportpairforce-v1")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--scan-seed-count", type=int, default=512)
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
                "best_generated": summary["summary"]["best_generated"],
                "budget_best": [
                    {
                        "best": item["best_generated"],
                        "budget": item["budget"],
                    }
                    for item in summary["summary"]["budget_results"]
                ],
                "claim_status": summary["claim_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
