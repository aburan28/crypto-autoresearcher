#!/usr/bin/env python3
"""P799 exact support-pair constructive generator audit."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P798_SCRIPT = TASK_DIR / "low_term_total2_p798_public_support_pair_generator.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p799_exact_support_pair_constructive_generator_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p799_exact_support_pair_constructive_generator.md"
SCHEMA = "ecdlp.low_term_total2_p799_exact_support_pair_constructive_generator.v1"
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
    return [f"t{index:02d}" for index in range(int(count))]


def line_sort_item(item: tuple[tuple[int, int, int, int], dict[str, Any]]) -> tuple[int, int, int, tuple[int, int, int, int]]:
    key, value = item
    return (
        int(value.get("candidate_row_count") or 0),
        int(value.get("candidate_form_count") or 0),
        -int(sum(key)),
        tuple(-int(part) for part in key),
    )


def selected_lines_and_supports(
    trained: dict[tuple[int, int, int, int], dict[str, Any]],
    max_count: int,
) -> tuple[list[tuple[int, int, int, int]], list[tuple[int, int]]]:
    ranked_lines = [key for key, _value in sorted(trained.items(), key=line_sort_item, reverse=True)]
    support_scores: dict[tuple[int, int], Counter] = {}
    for line_key, value in trained.items():
        support = tuple(int(part) for part in line_key[:2])
        item = support_scores.setdefault(support, Counter())
        item["line_count"] += 1
        item["candidate_row_count"] += int(value.get("candidate_row_count") or 0)
        item["candidate_form_count"] += int(value.get("candidate_form_count") or 0)
    ranked_supports = sorted(
        support_scores,
        key=lambda support: (
            support_scores[support]["candidate_row_count"],
            support_scores[support]["candidate_form_count"],
            support_scores[support]["line_count"],
            -sum(support),
            tuple(-part for part in support),
        ),
        reverse=True,
    )
    return ranked_lines[: int(max_count)], ranked_supports[: int(max_count)]


def policy_plans(
    group_key: str,
    lines: list[tuple[int, int, int, int]],
    supports: list[tuple[int, int]],
    factor_base_size: int,
) -> dict[str, list[dict[str, Any]]]:
    support_count = len(supports)
    line_count = len(lines)
    rotated_supports = [
        ((support[0] + 1) % factor_base_size, (support[1] + 3) % factor_base_size)
        for support in supports
    ]
    return {
        "line_salted": [
            {
                "group_key": group_key,
                "intended_line": line,
                "intended_support": tuple(int(part) for part in line[:2]),
                "tag": f"line_{line[0]}_{line[1]}_{line[2]}_{line[3]}",
            }
            for line in lines
        ],
        "neutral_salted": [
            {
                "group_key": group_key,
                "intended_line": None,
                "intended_support": None,
                "tag": f"neutral_{index:03d}",
            }
            for index in range(max(support_count, line_count))
        ],
        "pair_salted": [
            {
                "group_key": group_key,
                "intended_line": None,
                "intended_support": support,
                "tag": f"pair_{support[0]}_{support[1]}",
            }
            for support in supports
        ],
        "rotated_pair_salted": [
            {
                "group_key": group_key,
                "intended_line": None,
                "intended_support": support,
                "tag": f"rotpair_{support[0]}_{support[1]}",
            }
            for support in rotated_supports
        ],
    }


def collect_rows_for_policy(
    p746: Any,
    p748: Any,
    relprobe: Any,
    target: str,
    order_case: dict[str, Any],
    plans: list[dict[str, Any]],
    policy_name: str,
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], int]:
    verifier, record, inv = p746.load_target(relprobe, target)
    rows = []
    for plan_index, plan in enumerate(plans):
        prefix = (
            f"ecdlp-p799-{args.generator_namespace}-{policy_name}-"
            f"{slug(target)}-b{order_case['budget']}-{plan['tag']}-v1"
        )
        for seed_label in seed_labels(args.seeds_per_prefix):
            full_seed = (
                f"{prefix}:{seed_label}:fb{order_case['factor_base_size']}:"
                f"w{args.width}:{args.walk_mode}"
            )
            row = p748.scan_export_walk(
                p746,
                relprobe,
                verifier,
                record,
                inv,
                target,
                int(order_case["factor_base_size"]),
                int(args.width),
                str(args.walk_mode),
                seed_label,
                full_seed,
                int(order_case["budget"]),
                min(24, int(order_case["budget"])),
                int(args.max_relations),
                int(args.max_subsets),
            )
            tagged = dict(row)
            tagged["seed_label"] = f"{policy_name}:{plan_index:03d}:{seed_label}:{plan['tag']}"
            tagged["_p799_plan"] = {
                "intended_line": list(plan["intended_line"]) if plan.get("intended_line") else None,
                "intended_support": list(plan["intended_support"]) if plan.get("intended_support") else None,
                "policy": policy_name,
                "prefix": prefix,
                "tag": plan["tag"],
            }
            rows.append(tagged)
    return rows, int(inv["base_order"])


def tag_by_row_key(target: str, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        f"{target}:0:{index}": dict(row.get("_p799_plan") or {})
        for index, row in enumerate(rows)
    }


def hit_counts(
    p793: Any,
    records: list[dict[str, Any]],
    order: int,
    selected_lines: set[tuple[int, int, int, int]],
    selected_supports: set[tuple[int, int]],
    tags: dict[str, dict[str, Any]],
) -> dict[str, int]:
    line_hit_rows: set[str] = set()
    support_hit_rows: set[str] = set()
    intended_line_hit_rows: set[str] = set()
    intended_support_hit_rows: set[str] = set()
    for record in records:
        row_key = str(record["row_key"])
        support = tuple(int(part) for part in record["support"])
        tag = tags.get(row_key) or {}
        intended_support_raw = tag.get("intended_support")
        if support in selected_supports:
            support_hit_rows.add(row_key)
        if intended_support_raw is not None and tuple(int(part) for part in intended_support_raw) == support:
            intended_support_hit_rows.add(row_key)
        parts = p793.line_parts(record, order)
        if parts is None:
            continue
        line_key = tuple(int(part) for part in parts["line_key"])
        intended_line_raw = tag.get("intended_line")
        if line_key in selected_lines:
            line_hit_rows.add(row_key)
        if intended_line_raw is not None and tuple(int(part) for part in intended_line_raw) == line_key:
            intended_line_hit_rows.add(row_key)
    return {
        "intended_line_hit_row_count": len(intended_line_hit_rows),
        "intended_support_hit_row_count": len(intended_support_hit_rows),
        "selected_line_hit_row_count": len(line_hit_rows),
        "selected_support_hit_row_count": len(support_hit_rows),
    }


def evaluate_generated_policy(
    p797: Any,
    p793: Any,
    p792: Any,
    p789: Any,
    train_prepared: dict[str, Any],
    trained: dict[tuple[int, int, int, int], dict[str, Any]],
    rows: list[dict[str, Any]],
    order: int,
    target: str,
    policy_name: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    records, rows_meta = p792.collect_form_records(p789, [(0, rows, int(order))], target)
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
    generated_total = (
        int(train_cost["calibration_online_group_additions"])
        + int(scored["generated_online_group_additions"])
        + int(args.field_weight)
        * (int(train_cost["calibration_field_ops"]) + int(scored["scoring_field_ops"]))
    )
    recovered_rho = int(scored["primary"].get("recovered_rho_baseline") or 0)
    tags = tag_by_row_key(target, rows)
    hits = hit_counts(
        p793,
        records,
        int(order),
        {tuple(int(part) for part in key) for key in trained},
        {tuple(int(part) for part in key[:2]) for key in trained},
        tags,
    )
    return {
        "aggregate": {
            **hits,
            "generated_once_train_total_unit_cost": generated_total,
            "generated_once_train_total_unit_cost_over_recovered_rho": ratio(generated_total, recovered_rho),
            "generated_online_group_additions": int(scored["generated_online_group_additions"]),
            "generated_row_count": int(scored["generated_row_count"]),
            "generated_row_rho_baseline": int(scored["generated_row_rho_baseline"]),
            "intended_line_hit_rate": ratio(hits["intended_line_hit_row_count"], int(scored["generated_row_count"])),
            "intended_support_hit_rate": ratio(hits["intended_support_hit_row_count"], int(scored["generated_row_count"])),
            "max_control_recovered_row_count": int(scored["max_control_recovered_row_count"]),
            "primary_minus_max_control_recovered_rows": int(scored["primary"].get("recovered_row_count") or 0)
            - int(scored["max_control_recovered_row_count"]),
            "recovered_row_count": int(scored["primary"].get("recovered_row_count") or 0),
            "recovered_rho_baseline": recovered_rho,
            "selected_line_hit_rate": ratio(hits["selected_line_hit_row_count"], int(scored["generated_row_count"])),
            "selected_support_hit_rate": ratio(hits["selected_support_hit_row_count"], int(scored["generated_row_count"])),
            "scored_form_count": int(scored["primary"].get("scored_form_count") or 0),
            "scoring_field_ops": int(scored["scoring_field_ops"]),
            "target_row_mismatch_count": int(scored["primary"].get("target_row_mismatch_count") or 0),
            "train_calibration_field_ops": int(train_cost["calibration_field_ops"]),
            "train_calibration_online_group_additions": int(train_cost["calibration_online_group_additions"]),
        },
        "policy": {"kind": policy_kind(policy_name), "name": policy_name},
    }


def policy_kind(policy_name: str) -> str:
    if policy_name == "pair_salted":
        return "public_pair_salted_generator"
    if policy_name == "line_salted":
        return "line_salted_diagnostic"
    if policy_name == "neutral_salted":
        return "neutral_prefix_control"
    if policy_name == "rotated_pair_salted":
        return "rotated_pair_prefix_control"
    return "unknown"


def aggregate_policy_results(items: list[dict[str, Any]], policy_name: str) -> dict[str, Any]:
    totals = Counter()
    controls = []
    for item in items:
        aggregate = item["aggregate"]
        for key, value in aggregate.items():
            if isinstance(value, int):
                totals[key] += value
        controls.append(int(aggregate["max_control_recovered_row_count"]))
    generated_rows = int(totals["generated_row_count"])
    recovered_rho = int(totals["recovered_rho_baseline"])
    return {
        "aggregate": {
            **dict(totals),
            "generated_once_train_total_unit_cost_over_recovered_rho": ratio(
                int(totals["generated_once_train_total_unit_cost"]),
                recovered_rho,
            ),
            "intended_line_hit_rate": ratio(int(totals["intended_line_hit_row_count"]), generated_rows),
            "intended_support_hit_rate": ratio(int(totals["intended_support_hit_row_count"]), generated_rows),
            "max_control_recovered_row_count": max(controls, default=0),
            "primary_minus_max_control_recovered_rows": int(totals["recovered_row_count"]) - max(controls, default=0),
            "selected_line_hit_rate": ratio(int(totals["selected_line_hit_row_count"]), generated_rows),
            "selected_support_hit_rate": ratio(int(totals["selected_support_hit_row_count"]), generated_rows),
            "target_count": len(items),
        },
        "policy": {"kind": policy_kind(policy_name), "name": policy_name},
        "target_results": items,
    }


def determine_policy_claim(policy_result: dict[str, Any], peer_results: dict[str, dict[str, Any]]) -> str:
    aggregate = policy_result["aggregate"]
    name = policy_result["policy"]["name"]
    if int(aggregate["generated_row_count"]) == 0:
        return "no_generated_rows"
    if int(aggregate["recovered_row_count"]) <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    ratio_value = aggregate["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9
    neutral_recovered = int((peer_results.get("neutral_salted") or {}).get("aggregate", {}).get("recovered_row_count") or 0)
    rotated_recovered = int((peer_results.get("rotated_pair_salted") or {}).get("aggregate", {}).get("recovered_row_count") or 0)
    peer_max = max(neutral_recovered, rotated_recovered)
    if name == "pair_salted" and int(aggregate["recovered_row_count"]) > peer_max and ratio_value < 1.0:
        return "pair_salted_below_rho_beats_prefix_controls"
    if name == "pair_salted" and int(aggregate["recovered_row_count"]) > peer_max:
        return "pair_salted_enrichment_cost_boundary"
    if name == "line_salted" and int(aggregate["recovered_row_count"]) > peer_max and ratio_value < 1.0:
        return "line_salted_diagnostic_below_rho"
    if name in {"neutral_salted", "rotated_pair_salted"}:
        return "prefix_control"
    return "cost_boundary"


def determine_claim(summary: dict[str, Any]) -> str:
    claims = [
        policy_result["policy_claim"]
        for budget_result in summary["budget_results"]
        for policy_result in budget_result["policy_results"]
    ]
    if "pair_salted_below_rho_beats_prefix_controls" in claims:
        return "P799_PAIR_SALTED_GENERATOR_BELOW_RHO_SIGNAL"
    if "pair_salted_enrichment_cost_boundary" in claims:
        return "P799_PAIR_SALTED_ENRICHMENT_COST_BOUNDARY"
    if "line_salted_diagnostic_below_rho" in claims:
        return "P799_LINE_SALTED_DIAGNOSTIC_BELOW_RHO_SIGNAL"
    return "NEGATIVE_RESULT_P799_PREFIX_SALTING_NO_SUPPORT_PAIR_GENERATOR"


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
        "generated_once_train_total_unit_cost_over_recovered_rho": aggregate["generated_once_train_total_unit_cost_over_recovered_rho"],
        "generated_row_count": aggregate["generated_row_count"],
        "intended_support_hit_rate": aggregate["intended_support_hit_rate"],
        "policy": item["policy"]["name"],
        "policy_claim": item["policy_claim"],
        "recovered_row_count": aggregate["recovered_row_count"],
        "selected_line_hit_rate": aggregate["selected_line_hit_rate"],
        "selected_support_hit_rate": aggregate["selected_support_hit_rate"],
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p798 = load_module("ecdlp_p798_for_p799", P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p799", p798.P797_SCRIPT)
    p796 = p797.load_module("ecdlp_p796_for_p799", p797.P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p799", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p799", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p799", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p799", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p799", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p799", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p799", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p799", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p799", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p799", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p799", p782.P780_SCRIPT)
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
    budget_results = []
    all_policy_results = []
    for budget in budgets:
        print(f"scoring budget {budget}", flush=True)
        target_policy_results: dict[str, list[dict[str, Any]]] = {
            "line_salted": [],
            "neutral_salted": [],
            "pair_salted": [],
            "rotated_pair_salted": [],
        }
        for group_key in required:
            trained = p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], int(budget))
            lines, supports = selected_lines_and_supports(trained, int(args.max_items_per_target))
            target_plans = policy_plans(
                group_key,
                lines,
                supports,
                int(base_groups[group_key]["factor_base_size"]),
            )
            case = p784.case_from_group(
                base_groups[group_key],
                p784.TRIM12_DELTA,
                args.generator_namespace,
                "p799",
                p784.DEST_SEED_COUNT,
                p784.DEST_POOL_COUNT,
            )
            for policy_name, plans in target_plans.items():
                rows, order = collect_rows_for_policy(
                    p746,
                    p748,
                    relprobe,
                    str(base_groups[group_key]["target"]),
                    case,
                    plans,
                    policy_name,
                    args,
                )
                target_policy_results[policy_name].append(
                    evaluate_generated_policy(
                        p797,
                        p793,
                        p792,
                        p789,
                        train_prepared[group_key],
                        trained,
                        rows,
                        order,
                        str(base_groups[group_key]["target"]),
                        policy_name,
                        args,
                    )
                )
        policy_results = []
        for policy_name, items in target_policy_results.items():
            policy_results.append(aggregate_policy_results(items, policy_name))
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
        "generator_namespace": args.generator_namespace,
        "train_seed_namespace": args.train_seed_namespace,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p798_script": str(P798_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PREFIX-SCHEDULE-AUDIT: support pairs are encoded only into deterministic public seed prefixes; this is not direct algebraic form construction.",
            "MODEL-BOUND: trained support lines come from the supportline20-v1 calibration namespace.",
            "CONTROL-BOUND: neutral and rotated-prefix policies test whether support-pair labels add value beyond extra random rows.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p799_exact_support_pair_constructive_generator",
        "parameters": {
            "budgets": budgets,
            "control_count": args.control_count,
            "field_weight": args.field_weight,
            "generator_namespace": args.generator_namespace,
            "max_items_per_target": args.max_items_per_target,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_line_rows": args.min_line_rows,
            "row_policy": args.row_policy,
            "seeds_per_prefix": args.seeds_per_prefix,
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
                        "generated_once_train_total_unit_cost_over_recovered_rho": aggregate["generated_once_train_total_unit_cost_over_recovered_rho"],
                        "generated_row_count": aggregate["generated_row_count"],
                        "intended_line_hit_rate": aggregate["intended_line_hit_rate"],
                        "intended_support_hit_rate": aggregate["intended_support_hit_rate"],
                        "max_control_recovered_row_count": aggregate["max_control_recovered_row_count"],
                        "primary_minus_max_control_recovered_rows": aggregate["primary_minus_max_control_recovered_rows"],
                        "recovered_row_count": aggregate["recovered_row_count"],
                        "selected_line_hit_rate": aggregate["selected_line_hit_rate"],
                        "selected_support_hit_rate": aggregate["selected_support_hit_rate"],
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
    parser.add_argument("--generator-namespace", default="supportpairgen-v1")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--budgets", default=DEFAULT_BUDGETS)
    parser.add_argument("--max-items-per-target", type=int, default=32)
    parser.add_argument("--seeds-per-prefix", type=int, default=4)
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
