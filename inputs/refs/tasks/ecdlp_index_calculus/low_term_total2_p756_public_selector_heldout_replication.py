#!/usr/bin/env python3
"""P756 held-out replication for the frozen P755 public selector."""

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
DEFAULT_P755_SUMMARY = STATE_DIR / "low_term_total2_p755_public_row_quality_selector_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p756_public_selector_heldout_replication_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p756_public_selector_heldout_replication.md"
SCHEMA = "ecdlp.low_term_total2_p756_public_selector_heldout_replication.v1"


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


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


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


def selected_feature_stats(p755: Any, rows: list[dict[str, Any]]) -> dict[str, Any]:
    features = [p755.public_feature(row) for row in rows]
    return {
        "accepted_mixed_relations": stat([item["accepted_mixed_relations"] for item in features]),
        "decomposition_hits": stat([item["decomposition_hits"] for item in features]),
        "form_count": stat([item["form_count"] for item in features]),
        "mixed_wide_relation_rank": stat([item["mixed_wide_relation_rank"] for item in features]),
        "zero_form_rows": [item["seed_label"] for item in features if int(item["form_count"]) == 0],
    }


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
    sparse = p755.evaluate_sparse_policy(
        p748,
        p751,
        p752,
        selected_rows,
        scanned_rows,
        args.sparse_policy,
        field_weights,
        order,
    )
    by_weight = {str(weight): cost_for_weight(sparse, weight) for weight in field_weights}
    weight2 = by_weight.get("2")
    success_weight2 = bool(
        sparse["success"]
        and weight2
        and (weight2.get("total_unit_cost_over_selected_rho") or 10**18) < 1.0
    )
    return {
        "case": case["label"],
        "dropped_from_scanned": selection["dropped_from_scanned"][:48],
        "factor_relation_count": sparse["factor_relation_count"],
        "factor_variable_count": sparse["factor_variable_count"],
        "max_field_op_weight_below_selected_rho": sparse["max_field_op_weight_below_selected_rho"],
        "order": order,
        "pool_count": selection["pool_count"],
        "row_policy": args.row_policy,
        "rows_collected": len(rows),
        "scanned_count": len(scanned_rows),
        "scanned_seed_max": selection["scanned_seed_max"],
        "selected_count": len(selected_rows),
        "selected_feature_stats": selected_feature_stats(p755, selected_rows),
        "selected_seed_sample": selection["selected_seed_labels"][:12],
        "seed_prefix": case["seed_prefix"],
        "sparse_policy": args.sparse_policy,
        "sparse_result": {
            "costs_by_field_weight": sparse["costs_by_field_weight"],
            "solve": sparse["solve"],
            "substitution": sparse["substitution"],
            "success": sparse["success"],
        },
        "success_weight2_below_rho": success_weight2,
        "target": case["target"],
        "weight_costs": by_weight,
    }, rows


def determine_claim(case_summaries: list[dict[str, Any]]) -> str:
    same_target = [item for item in case_summaries if str(item["case"]).startswith("same_target")]
    same_success = bool(same_target) and all(item["success_weight2_below_rho"] for item in same_target)
    all_success = all(item["success_weight2_below_rho"] for item in case_summaries)
    any_success = any(item["success_weight2_below_rho"] for item in case_summaries)
    if all_success:
        return "P756_PUBLIC_SELECTOR_HELDOUT_CROSSTARGET_WEIGHT2_BELOW_RHO_SIGNAL"
    if same_success:
        return "P756_PUBLIC_SELECTOR_SAME_TARGET_HELDOUT_WEIGHT2_BELOW_RHO_SIGNAL_CROSSTARGET_OPEN"
    if any_success:
        return "P756_PUBLIC_SELECTOR_PARTIAL_HELDOUT_WEIGHT2_SIGNAL"
    return "NEGATIVE_RESULT_P756_PUBLIC_SELECTOR_HELDOUT_NO_WEIGHT2_WIN"


def calibration_control(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    best = (((payload.get("summary") or {}).get("best_weight2")) or {})
    weight2 = (((best.get("best_by_field_weight") or {}).get("2") or {}).get("cost") or {})
    return {
        "claim_status": payload.get("claim_status"),
        "dropped_from_scanned": best.get("dropped_from_scanned"),
        "scanned_count": best.get("scanned_count"),
        "selected_count": best.get("selected_count"),
        "success_weight2_below_rho": best.get("success_weight2_below_rho"),
        "target": ((payload.get("summary") or {}).get("target")),
        "weight2_total_over_selected_rho": weight2.get("total_unit_cost_over_selected_rho"),
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
    field_weights = csv_ints(args.field_weights)
    case_summaries: list[dict[str, Any]] = []
    raw_results: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        summary, rows = evaluate_case(p755, p748, p750, p751, p752, p746, relprobe, case, args, field_weights)
        case_summaries.append(summary)
        raw_results[str(case["label"])] = [p750.strip_private(row) for row in rows]
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p755_summary": str(args.p755_summary),
            "script": str(Path(__file__)),
        },
        "calibration_control": calibration_control(args.p755_summary),
        "claim_status": determine_claim(case_summaries),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled order-11779 ECDLP harness only.",
            "FROZEN-PUBLIC-SELECTOR: row policy and sparse policy are fixed from P755 before held-out evaluation.",
            "HELD-OUT-SEED-PREFIXES: same-target cases use disjoint synthetic challenge seeds from P755.",
            "SCANNED-POOL-CHARGED: replacement policies pay group cost for all scanned candidate rows.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling or production-key relevance is implied.",
        ],
        "method": "p756_public_selector_heldout_replication",
        "parameters": {
            "cases": cases,
            "factor_base_size": args.factor_base_size,
            "field_weights": field_weights,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "pool_count": args.pool_count,
            "row_policy": args.row_policy,
            "seed_count": args.seed_count,
            "selected_count": args.selected_count,
            "sparse_policy": args.sparse_policy,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "results": raw_results,
        "schema": SCHEMA,
        "summary": {
            "case_summaries": case_summaries,
        },
    }


def slim_case(item: dict[str, Any]) -> dict[str, Any]:
    weight2 = (item.get("weight_costs") or {}).get("2") or {}
    return {
        "case": item["case"],
        "dropped_from_scanned": item["dropped_from_scanned"],
        "factor_relation_count": item["factor_relation_count"],
        "max_field_op_weight_below_selected_rho": item["max_field_op_weight_below_selected_rho"],
        "scanned_count": item["scanned_count"],
        "selected_count": item["selected_count"],
        "solve": item["sparse_result"]["solve"],
        "substitution": item["sparse_result"]["substitution"],
        "success_weight2_below_rho": item["success_weight2_below_rho"],
        "target": item["target"],
        "weight2_cost": weight2,
        "zero_form_selected_rows": item["selected_feature_stats"]["zero_form_rows"],
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "calibration_control": payload["calibration_control"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "summary": {
            "case_summaries": [slim_case(item) for item in payload["summary"]["case_summaries"]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases",
        default=(
            "same_target_fresh_a|67.a1@11789|80|ecdlp-p756-heldout-a-v1,"
            "same_target_fresh_b|67.a1@11789|80|ecdlp-p756-heldout-b-v1,"
            "cross_target_22050|22050.cf1@11731|72|ecdlp-p756-cross-target-v1"
        ),
    )
    parser.add_argument("--p755-summary", type=Path, default=DEFAULT_P755_SUMMARY)
    parser.add_argument("--seed-count", type=int, default=768)
    parser.add_argument("--selected-count", type=int, default=640)
    parser.add_argument("--pool-count", type=int, default=768)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policy", default="support_span_asc")
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
                "cases": [
                    {
                        "case": item["case"],
                        "scanned": item["scanned_count"],
                        "selected": item["selected_count"],
                        "success_weight2": item["success_weight2_below_rho"],
                        "target": item["target"],
                        "weight2": item["weight2_cost"],
                    }
                    for item in summary["summary"]["case_summaries"]
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
