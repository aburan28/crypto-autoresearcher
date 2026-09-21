#!/usr/bin/env python3
"""P754 extended-batch sparse weight-2 audit."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P746_SCRIPT = TASK_DIR / "low_term_total2_p746_incremental_walk_online_cost.py"
P748_SCRIPT = TASK_DIR / "low_term_total2_p748_setup_amortization_matrix_bridge.py"
P750_SCRIPT = TASK_DIR / "low_term_total2_p750_prospective_prefix_linear_algebra_charge.py"
P751_SCRIPT = TASK_DIR / "low_term_total2_p751_factor_first_linear_algebra.py"
P752_SCRIPT = TASK_DIR / "low_term_total2_p752_sparse_factor_basis_selection.py"
P753_SCRIPT = TASK_DIR / "low_term_total2_p753_sparse_scaling_red_team.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P753 = STATE_DIR / "low_term_total2_p753_sparse_scaling_red_team_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p754_extended_batch_sparse_weight2_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p754_extended_batch_sparse_weight2.md"
SCHEMA = "ecdlp.low_term_total2_p754_extended_batch_sparse_weight2.v1"


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


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def parse_target_budgets(raw: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        target, sep, budget = item.partition("=")
        if not sep:
            raise argparse.ArgumentTypeError(f"target budget must be target=budget, got {item!r}")
        out[target.strip()] = int(budget)
    return out


def p753_baseline(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    out: dict[str, dict[str, Any]] = {}
    for target in ((payload.get("summary") or {}).get("target_summaries") or []):
        full_prefix = int(target.get("full_prefix_count") or 0)
        full_eval = next((item for item in target.get("prefix_evaluations") or [] if int(item.get("prefix_count") or 0) == full_prefix), None)
        out[str(target.get("target"))] = {
            "full_prefix_count": full_prefix,
            "full_prefix_max_field_op_weight_below_selected_rho": target.get("full_prefix_max_field_op_weight_below_selected_rho"),
            "full_weight1_total_over_rho": ((full_eval or {}).get("best_by_field_weight") or {}).get("1", {}).get("cost", {}).get("total_unit_cost_over_selected_rho"),
            "full_weight2_total_over_rho": ((full_eval or {}).get("best_by_field_weight") or {}).get("2", {}).get("cost", {}).get("total_unit_cost_over_selected_rho"),
        }
    return out


def best_cost(prefix_eval: dict[str, Any], weight: int) -> dict[str, Any]:
    return prefix_eval["best_by_field_weight"][str(weight)]


def target_claim(prefix_evaluations: list[dict[str, Any]], full_prefix: int) -> str:
    full = next(item for item in prefix_evaluations if item["prefix_count"] == full_prefix)
    if not best_cost(full, 1)["success"]:
        return "NEGATIVE_RESULT_P754_EXTENDED_BATCH_FAILED_RECOVERY"
    if best_cost(full, 2)["success"] and (best_cost(full, 2)["cost"].get("total_unit_cost_over_selected_rho") or 10**18) < 1.0:
        return "P754_EXTENDED_BATCH_WEIGHT2_BELOW_RHO"
    if (best_cost(full, 1)["cost"].get("total_unit_cost_over_selected_rho") or 10**18) < 1.0:
        return "P754_EXTENDED_BATCH_WEIGHT1_ONLY"
    return "NEGATIVE_RESULT_P754_EXTENDED_BATCH_ABOVE_RHO"


def determine_claim(target_summaries: list[dict[str, Any]]) -> str:
    all_weight2 = all(summary["target_claim"] == "P754_EXTENDED_BATCH_WEIGHT2_BELOW_RHO" for summary in target_summaries)
    any_weight2 = any(summary["target_claim"] == "P754_EXTENDED_BATCH_WEIGHT2_BELOW_RHO" for summary in target_summaries)
    all_recovered = all(not summary["target_claim"].startswith("NEGATIVE_RESULT_P754_EXTENDED_BATCH_FAILED") for summary in target_summaries)
    all_improved = all(bool(summary.get("headroom_improved_vs_p753")) for summary in target_summaries)
    if all_weight2:
        return "P754_EXTENDED_BATCH_WEIGHT2_BELOW_RHO_SIGNAL"
    if any_weight2:
        return "P754_EXTENDED_BATCH_PARTIAL_WEIGHT2_BELOW_RHO_SIGNAL"
    if all_recovered and all_improved:
        return "P754_EXTENDED_BATCH_IMPROVES_HEADROOM_WEIGHT2_NEGATIVE"
    if all_recovered:
        return "P754_EXTENDED_BATCH_RECOVERS_WEIGHT2_NEGATIVE"
    return "NEGATIVE_RESULT_P754_EXTENDED_BATCH_FAILED"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p746 = load_module("ecdlp_p746_incremental_walk", P746_SCRIPT)
    p748 = load_module("ecdlp_p748_matrix_bridge", P748_SCRIPT)
    p750 = load_module("ecdlp_p750_prospective_prefix", P750_SCRIPT)
    p751 = load_module("ecdlp_p751_factor_first", P751_SCRIPT)
    p752 = load_module("ecdlp_p752_sparse_factor_basis", P752_SCRIPT)
    p753 = load_module("ecdlp_p753_sparse_scaling_red_team", P753_SCRIPT)
    relprobe = p746.load_relation_probe_module()
    target_budgets = parse_target_budgets(args.target_budgets)
    prefixes = sorted(set(csv_ints(args.prefixes)))
    field_weights = sorted(set(csv_ints(args.field_weights)))
    policies = csv_strings(args.policies)
    baseline = p753_baseline(args.p753_summary)
    raw_results: dict[str, list[dict[str, Any]]] = {}
    target_summaries: list[dict[str, Any]] = []
    for target, budget in target_budgets.items():
        rows, order = p750.collect_target_rows(
            p746,
            p748,
            relprobe,
            target,
            budget,
            args.seed_count,
            args.factor_base_size,
            args.width,
            args.walk_mode,
            args.seed_prefix,
            args.max_relations,
            args.max_subsets,
        )
        raw_results[target] = [p750.strip_private(row) for row in rows]
        prefix_evaluations = [
            p753.evaluate_prefix(p748, p751, p752, target, rows, prefix, policies, field_weights, order)
            for prefix in prefixes
            if prefix <= len(rows)
        ]
        full_prefix = max(item["prefix_count"] for item in prefix_evaluations)
        full = next(item for item in prefix_evaluations if item["prefix_count"] == full_prefix)
        target_base = baseline.get(target) or {}
        base_headroom = target_base.get("full_prefix_max_field_op_weight_below_selected_rho")
        full_headroom = full.get("max_field_op_weight_below_selected_rho")
        headroom_improved = (
            full_headroom is not None
            and base_headroom is not None
            and float(full_headroom) > float(base_headroom)
        )
        target_summaries.append(
            {
                "baseline_p753": target_base,
                "budget": budget,
                "full_prefix_count": full_prefix,
                "full_prefix_max_field_op_weight_below_selected_rho": full_headroom,
                "headroom_improved_vs_p753": headroom_improved,
                "prefix_evaluations": prefix_evaluations,
                "target": target,
                "target_claim": target_claim(prefix_evaluations, full_prefix),
                "weight2_below_rho_prefixes": [
                    item["prefix_count"]
                    for item in prefix_evaluations
                    if best_cost(item, 2)["success"]
                    and (best_cost(item, 2)["cost"].get("total_unit_cost_over_selected_rho") or 10**18) < 1.0
                ],
            }
        )
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p753_summary": str(args.p753_summary),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(target_summaries),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled order-11779 ECDLP harness only.",
            "PROSPECTIVE-COLLECTION: rows are newly collected at fixed public budgets, not replayed from longer scans.",
            "PUBLIC-PREFIX MODEL: prefixes use deterministic seed-label order.",
            "SPARSE-WEIGHT MODEL: field-operation weights are accounting stress tests, not calibrated hardware timings.",
            "MANY-TARGET MODEL: target-specific factor-base setup is shared across many synthetic public keys.",
        ],
        "method": "p754_extended_batch_sparse_weight2",
        "parameters": {
            "factor_base_size": args.factor_base_size,
            "field_weights": field_weights,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "p753_summary": str(args.p753_summary),
            "policies": policies,
            "prefixes": prefixes,
            "seed_count": args.seed_count,
            "seed_prefix": args.seed_prefix,
            "target_budgets": target_budgets,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "results": raw_results,
        "schema": SCHEMA,
        "summary": {
            "target_summaries": target_summaries,
        },
    }


def slim_prefix(p753: Any, item: dict[str, Any]) -> dict[str, Any]:
    return p753.slim_prefix(item)


def summary_from_payload(payload: dict[str, Any], p753: Any) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "created_at": payload["created_at"],
        "claim_status": payload["claim_status"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "summary": {
            "target_summaries": [
                {
                    "baseline_p753": target["baseline_p753"],
                    "budget": target["budget"],
                    "full_prefix_count": target["full_prefix_count"],
                    "full_prefix_max_field_op_weight_below_selected_rho": target["full_prefix_max_field_op_weight_below_selected_rho"],
                    "headroom_improved_vs_p753": target["headroom_improved_vs_p753"],
                    "prefix_evaluations": [slim_prefix(p753, item) for item in target["prefix_evaluations"]],
                    "target": target["target"],
                    "target_claim": target["target_claim"],
                    "weight2_below_rho_prefixes": target["weight2_below_rho_prefixes"],
                }
                for target in payload["summary"]["target_summaries"]
            ]
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-budgets", default="22050.cf1@11731=72,67.a1@11789=80")
    parser.add_argument("--seed-count", type=int, default=512)
    parser.add_argument("--seed-prefix", default="ecdlp-p746-scheduled-seed-extension-v1")
    parser.add_argument("--factor-base-size", type=int, default=48)
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--prefixes", default="256,384,512")
    parser.add_argument("--field-weights", default="1,2,4")
    parser.add_argument("--policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--p753-summary", type=Path, default=DEFAULT_P753)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p753 = load_module("ecdlp_p753_sparse_scaling_red_team_summary", P753_SCRIPT)
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload, p753)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": summary["claim_status"],
                "targets": [
                    {
                        "full_prefix_max_weight": target["full_prefix_max_field_op_weight_below_selected_rho"],
                        "headroom_improved_vs_p753": target["headroom_improved_vs_p753"],
                        "target": target["target"],
                        "target_claim": target["target_claim"],
                        "weight2_below_rho_prefixes": target["weight2_below_rho_prefixes"],
                    }
                    for target in summary["summary"]["target_summaries"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
