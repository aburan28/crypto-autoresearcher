#!/usr/bin/env python3
"""P764 widened-factor-basis cost validation after P763 limit propagation."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from types import SimpleNamespace
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P760_SCRIPT = TASK_DIR / "low_term_total2_p760_public_sparse_policy_selector.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P763_SUMMARY = STATE_DIR / "low_term_total2_p763_factor_base_limit_extension_smoke_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p764_widened_factor_basis_cost_validation_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p764_widened_factor_basis_cost_validation.md"
SCHEMA = "ecdlp.low_term_total2_p764_widened_factor_basis_cost_validation.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def parse_cases(raw: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split("|")
        if len(parts) != 9:
            raise argparse.ArgumentTypeError(
                "cases must be label|target|budget|factor_base_size|selected_count|seed_count|pool_count|seed_prefix|arm entries"
            )
        label, target, budget, factor_base_size, selected_count, seed_count, pool_count, seed_prefix, arm = (
            part.strip() for part in parts
        )
        cases.append(
            {
                "arm": arm,
                "budget": int(budget),
                "factor_base_size": int(factor_base_size),
                "label": label,
                "pool_count": int(pool_count),
                "seed_count": int(seed_count),
                "seed_prefix": seed_prefix,
                "selected_count": int(selected_count),
                "target": target,
            }
        )
    if not cases:
        raise argparse.ArgumentTypeError("at least one case is required")
    return cases


def factor_count_for_rows(rows: list[dict[str, Any]]) -> int:
    return max((len(form.get("coeffs") or []) - 1 for row in rows for form in row.get("forms") or []), default=0)


def factor_base_size_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return stat([int(row.get("factor_base_size") or 0) for row in rows])


def tail_form_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    form_count = 0
    tail_form_count = 0
    for row in rows:
        for form in row.get("forms") or []:
            form_count += 1
            coeffs = [int(value) for value in (form.get("coeffs") or [])]
            if any(value for value in coeffs[49:]):
                tail_form_count += 1
    return {
        "form_count": form_count,
        "tail_form_count_ge_48": tail_form_count,
    }


def relation_support_stats(p748: Any, p752: Any, selected_rows: list[dict[str, Any]], order: int, factor_count: int) -> dict[str, Any]:
    relations = p752.annotated_relations(
        p748.factor_eliminated_relations(selected_rows, order, factor_count),
        order,
    )
    active_columns: set[int] = set()
    tail_relation_count = 0
    source_counts = Counter(str(relation.get("source") or "") for relation in relations)
    for relation in relations:
        support = [
            index
            for index, value in enumerate(relation.get("coeffs") or [])
            if int(value) % order
        ]
        if any(index >= 48 for index in support):
            tail_relation_count += 1
        active_columns.update(support)
    return {
        "active_column_count": len(active_columns),
        "active_columns_ge_48": sum(1 for index in active_columns if index >= 48),
        "max_active_column": max(active_columns) if active_columns else None,
        "relation_count": len(relations),
        "relation_source_counts": {key: source_counts[key] for key in sorted(source_counts)},
        "tail_relation_count_ge_48": tail_relation_count,
    }


def weight2_cost(evaluation: dict[str, Any]) -> dict[str, Any]:
    for cost in evaluation.get("costs_by_field_weight") or []:
        if int(cost.get("field_op_weight") or 0) == 2:
            return cost
    return {}


def slim_sparse(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "factor_relation_count": item.get("factor_relation_count"),
        "factor_variable_count": item.get("factor_variable_count"),
        "max_field_op_weight_below_selected_rho": item.get("max_field_op_weight_below_selected_rho"),
        "mismatch_count": (item.get("substitution") or {}).get("mismatch_count"),
        "policy": item.get("sparse_policy"),
        "rank": (item.get("solve") or {}).get("rank"),
        "recovered_count": (item.get("substitution") or {}).get("recovered_count"),
        "success": item.get("success"),
        "weight2_cost": weight2_cost(item),
    }


def classify_case(item: dict[str, Any]) -> str:
    selected = int(item["selected_count"])
    target_selected = int(item["selected_target_count"])
    factor_base_size = int(item["factor_base_size"])
    chosen = item["public_selector_sparse_policy"]
    zero_forms = item["selected_feature_stats"]["zero_form_rows"]
    if (
        int(item["selected_exported_factor_count"]) < factor_base_size
        or int(item["selected_relation_support_stats"]["active_column_count"]) < factor_base_size
    ):
        return "capacity_or_support_failure"
    if selected != target_selected or zero_forms:
        return "row_budget_failure"
    if (
        chosen["solve"]["rank"] < factor_base_size
        or chosen["substitution"]["recovered_count"] != target_selected
        or chosen["substitution"]["mismatch_count"] != 0
    ):
        return "rank_or_recovery_failure"
    if item["oracle_best_pass_weight2_below_rho"] and not item["public_selector_pass_weight2_below_rho"]:
        return "selector_gap"
    if not item["public_selector_pass_weight2_below_rho"]:
        return "widened_cost_failure"
    return "pass"


def arm_summaries(case_summaries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in case_summaries:
        arm = str(item["arm"])
        bucket = out.setdefault(
            arm,
            {
                "case_count": 0,
                "failure_classes": {},
                "oracle_best_pass_count": 0,
                "public_selector_gap_count": 0,
                "public_selector_pass_count": 0,
                "public_selector_recovery_ok_count": 0,
                "strict_pass_count": 0,
            },
        )
        bucket["case_count"] += 1
        bucket["oracle_best_pass_count"] += int(bool(item["oracle_best_pass_weight2_below_rho"]))
        bucket["public_selector_gap_count"] += int(
            bool(item["oracle_best_pass_weight2_below_rho"] and not item["public_selector_pass_weight2_below_rho"])
        )
        bucket["public_selector_pass_count"] += int(bool(item["public_selector_pass_weight2_below_rho"]))
        bucket["public_selector_recovery_ok_count"] += int(bool(item["public_selector_recovery_ok"]))
        bucket["strict_pass_count"] += int(item["failure_class"] == "pass")
        failures = bucket["failure_classes"]
        failures[item["failure_class"]] = failures.get(item["failure_class"], 0) + 1
    return out


def determine_claim(case_summaries: list[dict[str, Any]], args: argparse.Namespace) -> str:
    total = len(case_summaries)
    strict_pass = sum(1 for item in case_summaries if item["failure_class"] == "pass")
    recovery_ok = sum(1 for item in case_summaries if item["public_selector_recovery_ok"])
    gaps = sum(1 for item in case_summaries if item["failure_class"] == "selector_gap")
    capacity_failures = sum(1 for item in case_summaries if item["failure_class"] == "capacity_or_support_failure")
    arms = arm_summaries(case_summaries)
    arm_min_pass = min((summary["strict_pass_count"] for summary in arms.values()), default=0)
    if total and strict_pass == total:
        return "P764_WIDENED_FACTOR_BASIS_COST_ALL_CASE_SIGNAL"
    if strict_pass >= int(args.primary_threshold) and arm_min_pass >= int(args.arm_threshold) and gaps == 0 and capacity_failures == 0:
        return "P764_WIDENED_FACTOR_BASIS_COST_PRIMARY_SIGNAL"
    if capacity_failures:
        return "P764_WIDENED_FACTOR_BASIS_CAPACITY_REGRESSION"
    if gaps:
        return "P764_WIDENED_FACTOR_BASIS_SELECTOR_GAP"
    if recovery_ok == total:
        return "P764_WIDENED_FACTOR_BASIS_RECOVERY_OK_COST_NEGATIVE"
    return "NEGATIVE_RESULT_P764_WIDENED_FACTOR_BASIS_COST_VALIDATION"


def p763_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    summary = payload.get("summary") or {}
    return {
        "claim_status": payload.get("claim_status"),
        "max_active_columns_ge_48": summary.get("max_active_columns_ge_48"),
        "max_exported_factor_count": summary.get("max_exported_factor_count"),
        "max_sparse_rank": summary.get("max_sparse_rank"),
        "rank_expansion_case_count": summary.get("rank_expansion_case_count"),
        "wide_support_case_count": summary.get("wide_support_case_count"),
    }


def evaluate_case(
    p755: Any,
    p748: Any,
    p750: Any,
    p751: Any,
    p752: Any,
    p746: Any,
    p760: Any,
    relprobe: Any,
    case: dict[str, Any],
    args: argparse.Namespace,
    sparse_policies: list[str],
    field_weights: list[int],
) -> dict[str, Any]:
    case_args = SimpleNamespace(
        factor_base_size=case["factor_base_size"],
        field_weights=field_weights,
        max_relations=args.max_relations,
        max_subsets=args.max_subsets,
        pool_count=case["pool_count"],
        public_substitution_ops_per_selected=args.public_substitution_ops_per_selected,
        row_policy=args.row_policy,
        seed_count=case["seed_count"],
        selected_count=case["selected_count"],
        sparse_policies=sparse_policies,
        walk_mode=args.walk_mode,
        width=args.width,
    )
    p760_case = {
        "budget": case["budget"],
        "label": case["label"],
        "role": case["arm"],
        "seed_prefix": case["seed_prefix"],
        "target": case["target"],
    }
    summary, rows = p760.evaluate_case(
        p755,
        p748,
        p750,
        p751,
        p752,
        p746,
        relprobe,
        p760_case,
        case_args,
        sparse_policies,
        field_weights,
    )
    selection = p755.select_rows(rows, case["selected_count"], case["pool_count"], args.row_policy)
    selected_rows = selection["selected_rows"]
    factor_count = factor_count_for_rows(selected_rows)
    summary.update(
        {
            "actual_factor_base_size": factor_base_size_stats(rows),
            "arm": case["arm"],
            "factor_base_size": case["factor_base_size"],
            "pool_count": case["pool_count"],
            "seed_count": case["seed_count"],
            "selected_exported_factor_count": factor_count,
            "selected_relation_support_stats": relation_support_stats(p748, p752, selected_rows, int(summary["base_order"]), factor_count),
            "selected_tail_form_stats": tail_form_stats(selected_rows),
            "selected_target_count": case["selected_count"],
        }
    )
    summary["failure_class"] = classify_case(summary)
    return summary


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p760 = load_module("ecdlp_p760_public_sparse_policy_selector", P760_SCRIPT)
    p755 = p760.load_module("ecdlp_p755_public_selector", p760.P755_SCRIPT)
    p746 = p755.load_module("ecdlp_p746_incremental_walk", p755.P746_SCRIPT)
    p748 = p755.load_module("ecdlp_p748_matrix_bridge", p755.P748_SCRIPT)
    p750 = p755.load_module("ecdlp_p750_prospective_prefix", p755.P750_SCRIPT)
    p751 = p755.load_module("ecdlp_p751_factor_first", p755.P751_SCRIPT)
    p752 = p755.load_module("ecdlp_p752_sparse_factor_basis", p755.P752_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    cases = parse_cases(args.cases)
    sparse_policies = p760.csv_strings(args.sparse_policies)
    field_weights = p760.csv_ints(args.field_weights)
    if 2 not in field_weights:
        field_weights.append(2)
        field_weights = sorted(set(field_weights))
    case_summaries = [
        evaluate_case(
            p755,
            p748,
            p750,
            p751,
            p752,
            p746,
            p760,
            relprobe,
            case,
            args,
            sparse_policies,
            field_weights,
        )
        for case in cases
    ]
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p763_summary": str(args.p763_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(case_summaries, args),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "WIDENED-FACTOR-BASIS: P763 factor-base-limit propagation is active; requested fb64/fb80 must be exported.",
            "PUBLIC-SELECTION: sparse policy is selected from public full-rank solve cost before substitution verification.",
            "PRIVATE-VERIFY-ONLY: expected secrets are used only after public policy selection to verify recovery and mismatches.",
            "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p764_widened_factor_basis_cost_validation",
        "p763_control": p763_control(args.p763_summary),
        "parameters": {
            "arm_threshold": args.arm_threshold,
            "cases": cases,
            "field_weights": field_weights,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "primary_threshold": args.primary_threshold,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "row_policy": args.row_policy,
            "sparse_policies": sparse_policies,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": {
            "arm_summaries": arm_summaries(case_summaries),
            "case_count": len(case_summaries),
            "case_summaries": case_summaries,
            "oracle_best_pass_count": sum(1 for item in case_summaries if item["oracle_best_pass_weight2_below_rho"]),
            "public_selector_gap_count": sum(1 for item in case_summaries if item["failure_class"] == "selector_gap"),
            "public_selector_pass_count": sum(1 for item in case_summaries if item["public_selector_pass_weight2_below_rho"]),
            "public_selector_recovery_ok_count": sum(1 for item in case_summaries if item["public_selector_recovery_ok"]),
            "strict_pass_case_count": sum(1 for item in case_summaries if item["failure_class"] == "pass"),
        },
    }


def slim_case(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "actual_factor_base_size": item["actual_factor_base_size"],
        "arm": item["arm"],
        "base_order": item["base_order"],
        "budget": item["budget"],
        "case": item["case"],
        "factor_base_size": item["factor_base_size"],
        "failure_class": item["failure_class"],
        "generic_rho_steps": item["generic_rho_steps"],
        "oracle_best_pass_weight2_below_rho": item["oracle_best_pass_weight2_below_rho"],
        "oracle_best_sparse_policy": slim_sparse(item["oracle_best_sparse_policy"]),
        "pool_count": item["pool_count"],
        "public_selector_pass_weight2_below_rho": item["public_selector_pass_weight2_below_rho"],
        "public_selector_recovery_ok": item["public_selector_recovery_ok"],
        "public_selector_sparse_policy": slim_sparse(item["public_selector_sparse_policy"]),
        "scanned_count": item["scanned_count"],
        "seed_count": item["seed_count"],
        "selected_count": item["selected_count"],
        "selected_exported_factor_count": item["selected_exported_factor_count"],
        "selected_relation_support_stats": item["selected_relation_support_stats"],
        "selected_tail_form_stats": item["selected_tail_form_stats"],
        "selected_target_count": item["selected_target_count"],
        "target": item["target"],
        "zero_form_selected_rows": item["selected_feature_stats"]["zero_form_rows"],
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "p763_control": payload["p763_control"],
        "parameters": payload["parameters"],
        "summary": {
            "arm_summaries": payload["summary"]["arm_summaries"],
            "case_count": payload["summary"]["case_count"],
            "case_summaries": [slim_case(item) for item in payload["summary"]["case_summaries"]],
            "oracle_best_pass_count": payload["summary"]["oracle_best_pass_count"],
            "public_selector_gap_count": payload["summary"]["public_selector_gap_count"],
            "public_selector_pass_count": payload["summary"]["public_selector_pass_count"],
            "public_selector_recovery_ok_count": payload["summary"]["public_selector_recovery_ok_count"],
            "strict_pass_case_count": payload["summary"]["strict_pass_case_count"],
        },
    }


def default_cases() -> str:
    targets = [
        ("67.a1@9803", 66, "67"),
        ("21175.bc1@8089", 58, "21175"),
        ("23232.cr1@9643", 64, "23232b"),
    ]
    entries = []
    for factor_base_size in (64, 80):
        for target, budget, tag in targets:
            entries.append(
                f"fb{factor_base_size}_{tag}|{target}|{budget}|{factor_base_size}|640|768|768|ecdlp-p764-fb{factor_base_size}-{tag}-v1|fb{factor_base_size}"
            )
    return ",".join(entries)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default=default_cases())
    parser.add_argument("--p763-summary", type=Path, default=DEFAULT_P763_SUMMARY)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--field-weights", default="1,2")
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
    parser.add_argument("--primary-threshold", type=int, default=4)
    parser.add_argument("--arm-threshold", type=int, default=2)
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
                "arm_summaries": summary["summary"]["arm_summaries"],
                "claim_status": summary["claim_status"],
                "oracle_best_pass_count": summary["summary"]["oracle_best_pass_count"],
                "public_selector_gap_count": summary["summary"]["public_selector_gap_count"],
                "public_selector_pass_count": summary["summary"]["public_selector_pass_count"],
                "public_selector_recovery_ok_count": summary["summary"]["public_selector_recovery_ok_count"],
                "strict_pass_case_count": summary["summary"]["strict_pass_case_count"],
                "cases": [
                    {
                        "arm": item["arm"],
                        "case": item["case"],
                        "exported": item["selected_exported_factor_count"],
                        "failure_class": item["failure_class"],
                        "policy": item["public_selector_sparse_policy"]["policy"],
                        "rank": item["public_selector_sparse_policy"]["rank"],
                        "target": item["target"],
                        "verified_weight2": item["public_selector_sparse_policy"]["weight2_cost"].get("total_unit_cost_over_selected_rho"),
                    }
                    for item in summary["summary"]["case_summaries"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
