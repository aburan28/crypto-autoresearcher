#!/usr/bin/env python3
"""P757 cross-order stress for the frozen P756 public selector."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P755_SCRIPT = TASK_DIR / "low_term_total2_p755_public_row_quality_selector.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P756_SUMMARY = STATE_DIR / "low_term_total2_p756_public_selector_heldout_replication_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p757_public_selector_cross_order_stress_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p757_public_selector_cross_order_stress.md"
SCHEMA = "ecdlp.low_term_total2_p757_public_selector_cross_order_stress.v1"


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


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


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


def parse_cases(raw: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split("|")
        if len(parts) != 4:
            raise argparse.ArgumentTypeError(
                "cases must be label|target|budget|seed_prefix comma-separated entries"
            )
        label, target, budget, seed_prefix = (part.strip() for part in parts)
        cases.append({"budget": int(budget), "label": label, "seed_prefix": seed_prefix, "target": target})
    if not cases:
        raise argparse.ArgumentTypeError("at least one case is required")
    return cases


def cost_for_weight(evaluation: dict[str, Any], weight: int) -> dict[str, Any]:
    return next(cost for cost in evaluation["costs_by_field_weight"] if int(cost["field_op_weight"]) == weight)


def weight2_ratio(evaluation: dict[str, Any]) -> float | None:
    cost = cost_for_weight(evaluation, 2)
    return cost.get("total_unit_cost_over_selected_rho")


def selected_feature_stats(p755: Any, rows: list[dict[str, Any]]) -> dict[str, Any]:
    features = [p755.public_feature(row) for row in rows]
    return {
        "accepted_mixed_relations": stat([item["accepted_mixed_relations"] for item in features]),
        "decomposition_hits": stat([item["decomposition_hits"] for item in features]),
        "form_count": stat([item["form_count"] for item in features]),
        "mixed_wide_relation_rank": stat([item["mixed_wide_relation_rank"] for item in features]),
        "zero_form_rows": [item["seed_label"] for item in features if int(item["form_count"]) == 0],
    }


def slim_sparse_result(evaluation: dict[str, Any]) -> dict[str, Any]:
    return {
        "costs_by_field_weight": evaluation["costs_by_field_weight"],
        "factor_relation_count": evaluation["factor_relation_count"],
        "max_field_op_weight_below_selected_rho": evaluation["max_field_op_weight_below_selected_rho"],
        "sparse_policy": evaluation["sparse_policy"],
        "solve": evaluation["solve"],
        "substitution": evaluation["substitution"],
        "success": evaluation["success"],
    }


def policy_passes(evaluation: dict[str, Any], selected_count: int) -> bool:
    cost = cost_for_weight(evaluation, 2)
    return bool(
        evaluation["success"]
        and evaluation["substitution"]["recovered_count"] == selected_count
        and evaluation["substitution"]["mismatch_count"] == 0
        and (cost.get("total_unit_cost_over_selected_rho") or 10**18) < 1.0
    )


def best_sparse(evaluations: list[dict[str, Any]], selected_count: int) -> dict[str, Any]:
    def key(item: dict[str, Any]) -> tuple[Any, ...]:
        cost = cost_for_weight(item, 2)
        return (
            0 if policy_passes(item, selected_count) else 1,
            cost.get("total_unit_cost_over_selected_rho") or 10**18,
            0 if item["success"] else 1,
            item["substitution"]["mismatch_count"],
            item["sparse_policy"],
        )

    return min(evaluations, key=key)


def evaluate_case(
    p755: Any,
    p748: Any,
    p750: Any,
    p751: Any,
    p752: Any,
    p746: Any,
    relprobe: Any,
    case: dict[str, Any],
    args: argparse.Namespace,
    sparse_policies: list[str],
    field_weights: list[int],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows, order = p750.collect_target_rows(
        p746,
        p748,
        relprobe,
        case["target"],
        int(case["budget"]),
        args.seed_count,
        args.factor_base_size,
        args.width,
        args.walk_mode,
        str(case["seed_prefix"]),
        args.max_relations,
        args.max_subsets,
    )
    selection = p755.select_rows(rows, args.selected_count, args.pool_count, args.row_policy)
    selected_rows = selection["selected_rows"]
    scanned_rows = selection["scanned_rows"]
    evaluations = [
        p755.evaluate_sparse_policy(
            p748,
            p751,
            p752,
            selected_rows,
            scanned_rows,
            sparse_policy,
            field_weights,
            order,
        )
        for sparse_policy in sparse_policies
    ]
    frozen = next(item for item in evaluations if item["sparse_policy"] == args.frozen_sparse_policy)
    best = best_sparse(evaluations, args.selected_count)
    frozen_pass = (
        len(selected_rows) == args.selected_count
        and len(scanned_rows) >= len(selected_rows)
        and policy_passes(frozen, args.selected_count)
    )
    best_pass = (
        len(selected_rows) == args.selected_count
        and len(scanned_rows) >= len(selected_rows)
        and policy_passes(best, args.selected_count)
    )
    rho = int(selected_rows[0]["generic_rho_steps"]) if selected_rows else None
    return {
        "base_order": order,
        "best_comparator_pass_weight2_below_rho": best_pass,
        "best_sparse_policy": slim_sparse_result(best),
        "budget": int(case["budget"]),
        "case": case["label"],
        "dropped_from_scanned": selection["dropped_from_scanned"][:48],
        "frozen_policy_pass_weight2_below_rho": frozen_pass,
        "frozen_sparse_policy": slim_sparse_result(frozen),
        "generic_rho_steps": rho,
        "pool_count": selection["pool_count"],
        "row_policy": args.row_policy,
        "rows_collected": len(rows),
        "scanned_count": len(scanned_rows),
        "scanned_seed_max": selection["scanned_seed_max"],
        "selected_count": len(selected_rows),
        "selected_feature_stats": selected_feature_stats(p755, selected_rows),
        "selected_seed_sample": selection["selected_seed_labels"][:12],
        "seed_prefix": case["seed_prefix"],
        "sparse_policy_evaluations": [slim_sparse_result(item) for item in evaluations],
        "target": case["target"],
    }, rows


def determine_claim(case_summaries: list[dict[str, Any]]) -> str:
    total = len(case_summaries)
    frozen_pass = sum(1 for item in case_summaries if item["frozen_policy_pass_weight2_below_rho"])
    best_pass = sum(1 for item in case_summaries if item["best_comparator_pass_weight2_below_rho"])
    if total and frozen_pass == total:
        return "P757_FROZEN_PUBLIC_SELECTOR_CROSS_ORDER_WEIGHT2_BELOW_RHO_SIGNAL"
    if frozen_pass >= 4:
        return "P757_FROZEN_PUBLIC_SELECTOR_CROSS_ORDER_PARTIAL_WEIGHT2_SIGNAL"
    if best_pass >= 4:
        return "P757_ROW_SELECTOR_TRANSFERS_SPARSE_POLICY_GAP"
    if best_pass:
        return "P757_CROSS_ORDER_PARTIAL_COMPARATOR_SIGNAL"
    return "NEGATIVE_RESULT_P757_CROSS_ORDER_SELECTOR_STRESS"


def p756_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    cases = []
    for item in (((payload.get("summary") or {}).get("case_summaries")) or []):
        cases.append(
            {
                "case": item.get("case"),
                "safe_field_weight": item.get("max_field_op_weight_below_selected_rho"),
                "success_weight2_below_rho": item.get("success_weight2_below_rho"),
                "target": item.get("target"),
                "weight2_total_over_selected_rho": ((item.get("weight2_cost") or {}).get("total_unit_cost_over_selected_rho")),
            }
        )
    return {
        "claim_status": payload.get("claim_status"),
        "cases": cases,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p755 = load_module("ecdlp_p755_public_selector", P755_SCRIPT)
    p746 = p755.load_module("ecdlp_p746_incremental_walk", p755.P746_SCRIPT)
    p748 = p755.load_module("ecdlp_p748_matrix_bridge", p755.P748_SCRIPT)
    p750 = p755.load_module("ecdlp_p750_prospective_prefix", p755.P750_SCRIPT)
    p751 = p755.load_module("ecdlp_p751_factor_first", p755.P751_SCRIPT)
    p752 = p755.load_module("ecdlp_p752_sparse_factor_basis", p755.P752_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    cases = parse_cases(args.cases)
    sparse_policies = csv_strings(args.sparse_policies)
    if args.frozen_sparse_policy not in sparse_policies:
        sparse_policies.append(args.frozen_sparse_policy)
    field_weights = csv_ints(args.field_weights)
    case_summaries: list[dict[str, Any]] = []
    raw_results: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        summary, rows = evaluate_case(
            p755,
            p748,
            p750,
            p751,
            p752,
            p746,
            relprobe,
            case,
            args,
            sparse_policies,
            field_weights,
        )
        case_summaries.append(summary)
        raw_results[str(case["label"])] = [p750.strip_private(row) for row in rows]
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p756_summary": str(args.p756_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(case_summaries),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CROSS-ORDER-STRESS: target base orders are intentionally outside the P756 order-11779 calibration set.",
            "FROZEN-ROW-SELECTOR: row policy is fixed from P756 before cross-order evaluation.",
            "FROZEN-SPARSE-SEPARATED: support_span_asc is judged separately from best sparse-policy comparators.",
            "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p757_public_selector_cross_order_stress",
        "parameters": {
            "cases": cases,
            "factor_base_size": args.factor_base_size,
            "field_weights": field_weights,
            "frozen_sparse_policy": args.frozen_sparse_policy,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "pool_count": args.pool_count,
            "row_policy": args.row_policy,
            "seed_count": args.seed_count,
            "selected_count": args.selected_count,
            "sparse_policies": sparse_policies,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "p756_control": p756_control(args.p756_summary),
        "results": raw_results,
        "schema": SCHEMA,
        "summary": {
            "best_comparator_pass_count": sum(1 for item in case_summaries if item["best_comparator_pass_weight2_below_rho"]),
            "case_count": len(case_summaries),
            "case_summaries": case_summaries,
            "frozen_policy_pass_count": sum(1 for item in case_summaries if item["frozen_policy_pass_weight2_below_rho"]),
        },
    }


def slim_sparse_for_summary(item: dict[str, Any]) -> dict[str, Any]:
    weight2 = cost_for_weight(item, 2)
    return {
        "factor_relation_count": item["factor_relation_count"],
        "max_field_op_weight_below_selected_rho": item["max_field_op_weight_below_selected_rho"],
        "policy": item["sparse_policy"],
        "rank": item["solve"]["rank"],
        "recovered_count": item["substitution"]["recovered_count"],
        "mismatch_count": item["substitution"]["mismatch_count"],
        "success": item["success"],
        "weight2_cost": weight2,
    }


def slim_case(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "base_order": item["base_order"],
        "best_comparator_pass_weight2_below_rho": item["best_comparator_pass_weight2_below_rho"],
        "best_sparse_policy": slim_sparse_for_summary(item["best_sparse_policy"]),
        "budget": item["budget"],
        "case": item["case"],
        "dropped_from_scanned": item["dropped_from_scanned"],
        "frozen_policy_pass_weight2_below_rho": item["frozen_policy_pass_weight2_below_rho"],
        "frozen_sparse_policy": slim_sparse_for_summary(item["frozen_sparse_policy"]),
        "generic_rho_steps": item["generic_rho_steps"],
        "scanned_count": item["scanned_count"],
        "selected_count": item["selected_count"],
        "target": item["target"],
        "zero_form_selected_rows": item["selected_feature_stats"]["zero_form_rows"],
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "p756_control": payload["p756_control"],
        "parameters": payload["parameters"],
        "summary": {
            "best_comparator_pass_count": payload["summary"]["best_comparator_pass_count"],
            "case_count": payload["summary"]["case_count"],
            "case_summaries": [slim_case(item) for item in payload["summary"]["case_summaries"]],
            "frozen_policy_pass_count": payload["summary"]["frozen_policy_pass_count"],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases",
        default=(
            "order9887_67|67.a1@9803|72|ecdlp-p757-order9887-v1,"
            "order10639_22050|22050.cf1@10531|72|ecdlp-p757-order10639-v1,"
            "order9521_114224|114224.v1@9341|70|ecdlp-p757-order9521-v1,"
            "order8161_21175|21175.bc1@8089|64|ecdlp-p757-order8161-v1,"
            "order8521_23232|23232.cr1@8467|66|ecdlp-p757-order8521-v1"
        ),
    )
    parser.add_argument("--p756-summary", type=Path, default=DEFAULT_P756_SUMMARY)
    parser.add_argument("--seed-count", type=int, default=768)
    parser.add_argument("--selected-count", type=int, default=640)
    parser.add_argument("--pool-count", type=int, default=768)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--frozen-sparse-policy", default="support_span_asc")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--factor-base-size", type=int, default=48)
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--field-weights", default="1,2")
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
                "claim_status": summary["claim_status"],
                "frozen_policy_pass_count": summary["summary"]["frozen_policy_pass_count"],
                "best_comparator_pass_count": summary["summary"]["best_comparator_pass_count"],
                "cases": [
                    {
                        "best_policy": item["best_sparse_policy"]["policy"],
                        "best_weight2": item["best_sparse_policy"]["weight2_cost"].get("total_unit_cost_over_selected_rho"),
                        "case": item["case"],
                        "frozen_pass": item["frozen_policy_pass_weight2_below_rho"],
                        "frozen_weight2": item["frozen_sparse_policy"]["weight2_cost"].get("total_unit_cost_over_selected_rho"),
                        "order": item["base_order"],
                        "target": item["target"],
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
