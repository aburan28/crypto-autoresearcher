#!/usr/bin/env python3
"""P826 frozen P825 shared-pilot validation on fresh constructor namespaces."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P825_SCRIPT = TASK_DIR / "low_term_total2_p825_shared_full_pool_pilot_allocator.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p826_frozen_shared_pilot_validation_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p826_frozen_shared_pilot_validation.md"
SCHEMA = "ecdlp.low_term_total2_p826_frozen_shared_pilot_validation.v1"

FROZEN_PREFIX_SEED_COUNT = 8
FROZEN_AVERAGE_BUDGET = 64
FROZEN_PILOT_BUDGET = 16
FROZEN_SLATE = "core_score_hash"
FROZEN_SELECTOR = "membership_rows"
FROZEN_ALLOCATOR = "equal_remaining"


def load_p825() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p825_for_p826", P825_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P825 helpers from {P825_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def add_equal_controls(
    p825: Any,
    env: dict[str, Any],
    records: list[dict[str, Any]],
    prefix_count: int,
    average_budget: int,
) -> list[dict[str, Any]]:
    p823 = env["p823"]
    results = []
    for support_name, equal_name in env["equal_policy_name_by_support"].items():
        contexts = {
            record["prepared_by_policy_budget"][(support_name, int(average_budget))]["context_id"]: record["prepared_by_policy_budget"][
                (support_name, int(average_budget))
            ]
            for record in records
        }
        if equal_name == "equal_full_pool":
            kind = "full_pool"
        elif equal_name.startswith("equal_hash"):
            kind = "hash_control"
        else:
            kind = "adaptive_prefix_gate"
        item = p823.aggregate_policy(env, equal_name, kind, prefix_count, average_budget, contexts)
        if kind == "full_pool":
            item["policy_claim"] = "full_pool_boundary"
        elif kind == "hash_control":
            item["policy_claim"] = "hash_control_boundary"
        else:
            item["policy_claim"] = "adaptive_boundary"
        results.append(item)
    return results


def claim_status(public_item: dict[str, Any], full_pool: dict[str, Any]) -> str:
    public_claim = str(public_item.get("policy_claim"))
    public_ratio = public_item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    full_ratio = full_pool["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    if public_claim == "shared_public_pilot_below_rho":
        return "P826_FROZEN_SHARED_PUBLIC_PILOT_BELOW_RHO"
    if public_claim == "shared_public_pilot_improves_full_pool":
        return "P826_FROZEN_SHARED_PUBLIC_PILOT_VALIDATES_FULL_POOL_IMPROVEMENT"
    if public_ratio is not None and full_ratio is not None and public_ratio < full_ratio:
        return "P826_FROZEN_SHARED_PUBLIC_PILOT_COST_IMPROVES_WITHOUT_RECALL_GATE"
    return "NEGATIVE_RESULT_P826_FROZEN_SHARED_PUBLIC_PILOT_DOES_NOT_VALIDATE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p825 = load_p825()
    p823 = p825.load_p823()
    env = p823.build_environment(args)
    env["p823"] = p823
    env["pilot_budgets"] = [FROZEN_PILOT_BUDGET]

    prefix_count = FROZEN_PREFIX_SEED_COUNT
    average_budget = FROZEN_AVERAGE_BUDGET
    records = [
        record
        for record in env["records_by_prefix"][int(prefix_count)]
        if record["namespace"] in set(env["test_namespaces"])
    ]
    if not records:
        raise ValueError("P826 found no fresh validation records")

    policy_results = add_equal_controls(p825, env, records, prefix_count, average_budget)
    full_pool = next(item for item in policy_results if item["policy"]["name"] == "equal_full_pool")
    best_hash = env["p818"].best_result(policy_results, {"hash_control"})
    best_adaptive = env["p818"].best_result(policy_results, {"adaptive_prefix_gate"})

    public_item = p825.evaluate_shared_pilot_policy(
        env,
        records,
        prefix_count,
        average_budget,
        FROZEN_PILOT_BUDGET,
        FROZEN_SLATE,
        p825.SLATES[FROZEN_SLATE],
        FROZEN_SELECTOR,
        FROZEN_ALLOCATOR,
    )
    if public_item is None:
        raise RuntimeError("frozen P825 public policy could not allocate budgets")
    public_item["policy_claim"] = p825.classify_claim(public_item, full_pool, best_hash)
    policy_results.append(public_item)

    oracle_item = p825.evaluate_shared_pilot_policy(
        env,
        records,
        prefix_count,
        average_budget,
        FROZEN_PILOT_BUDGET,
        FROZEN_SLATE,
        p825.SLATES[FROZEN_SLATE],
        "oracle_pilot_rho",
        "oracle_rho_weighted_remaining",
    )
    if oracle_item is not None:
        oracle_item["policy_claim"] = p825.classify_claim(oracle_item, full_pool, best_hash)
        policy_results.append(oracle_item)

    status = claim_status(public_item, full_pool)
    summary = {
        "average_continuation_budget": average_budget,
        "best_equal_adaptive_gate": p825.compact_policy_result(env, best_adaptive),
        "best_hash_control": p825.compact_policy_result(env, best_hash),
        "best_oracle_sketch_ceiling": p825.compact_policy_result(env, oracle_item),
        "frozen_public_shared_pilot": p825.compact_policy_result(env, public_item),
        "full_pool": p825.compact_policy_result(env, full_pool),
        "policy_results": policy_results,
        "prefix_seed_count": prefix_count,
        "test_constructor_namespaces": env["test_namespaces"],
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p825_script": str(P825_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": status,
        "created_at": env["p818"].now_iso(),
        "frozen_policy": {
            "allocator": FROZEN_ALLOCATOR,
            "average_continuation_budget": FROZEN_AVERAGE_BUDGET,
            "pilot_budget": FROZEN_PILOT_BUDGET,
            "prefix_seed_count": FROZEN_PREFIX_SEED_COUNT,
            "selector": FROZEN_SELECTOR,
            "slate": FROZEN_SLATE,
            "slate_policies": list(p825.SLATES[FROZEN_SLATE]),
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN POLICY: the public P825 selector, slate, pilot budget, and allocator are fixed before scanning P826 namespaces.",
            "PUBLIC SKETCH: the promoted policy uses public membership row counts only; oracle-sketch output is reported separately as a nonpublic ceiling.",
            "SCAN-CHARGED: reported costs use synthetic union row tables, target-once calibration, and all-pair prefix setup.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p826_frozen_shared_pilot_validation",
        "parameters": {
            "calibration_budget": int(args.calibration_budget),
            "candidate_continuation_budgets": env["candidate_budgets"],
            "prefix_trial_budget": int(args.prefix_trial_budget),
            "scan_seed_count": int(args.scan_seed_count),
            "test_constructor_namespaces": env["test_namespaces"],
            "train_constructor_namespaces": env["train_namespaces"],
            "train_seed_namespace": args.train_seed_namespace,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p825 = load_p825()
    p823 = p825.load_p823()
    p819 = p823.load_p819()
    p818 = p819.load_p818()
    p815 = p818.load_module("ecdlp_p815_summary_for_p826", p818.P815_SCRIPT)
    p812 = p815.load_module("ecdlp_p812_summary_for_p826", p815.P812_SCRIPT)

    def compact(item: dict[str, Any]) -> dict[str, Any]:
        compacted = p815.compact_policy_result(p812, item)
        for key in (
            "allocated_final_budget_total",
            "selected_support_continuation_added_rows",
            "selected_support_continuation_deduped_rows",
            "shared_full_pool_pilot_added_rows",
            "shared_full_pool_pilot_deduped_rows",
            "shared_pilot_budget_total",
            "total_budget_units",
        ):
            if key in item["aggregate"]:
                compacted["aggregate"][key] = item["aggregate"][key]
        for key in ("allocator", "pilot_budget", "public_selector", "selector", "slate"):
            compacted["policy"][key] = item["policy"].get(key)
        if "shared_pilot_choices" in item:
            compacted["shared_pilot_choices"] = item["shared_pilot_choices"]
        return compacted

    summary = payload["summary"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **summary,
            "policy_results": [compact(item) for item in summary["policy_results"]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--train-constructor-namespaces", default="")
    parser.add_argument(
        "--test-constructor-namespaces",
        default="posthit-p826-fresh-v32,posthit-p826-fresh-v33,posthit-p826-fresh-v34",
    )
    parser.add_argument("--loo-constructor-namespaces", default="")
    parser.add_argument("--skip-loo", action="store_true", default=True)
    parser.add_argument("--calibration-budget", type=int, default=256)
    parser.add_argument("--prefix-seed-counts", default=str(FROZEN_PREFIX_SEED_COUNT))
    parser.add_argument("--prefix-trial-budget", type=int, default=256)
    parser.add_argument("--average-continuation-budgets", default=str(FROZEN_AVERAGE_BUDGET))
    parser.add_argument("--pilot-budgets", default=str(FROZEN_PILOT_BUDGET))
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--scan-seed-count", type=int, default=128)
    parser.add_argument("--top-span-bins", type=int, default=2)
    parser.add_argument("--top-endpoint-bins", type=int, default=4)
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--feature-bins", type=int, default=8)
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
    p825 = load_p825()
    p818 = p825.load_p823().load_p819().load_p818()
    payload = analyze(args)
    p818.write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    p818.write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": summary["claim_status"],
                "frozen_public_shared_pilot": summary["summary"]["frozen_public_shared_pilot"],
                "full_pool": summary["summary"]["full_pool"],
                "oracle_sketch_ceiling": summary["summary"]["best_oracle_sketch_ceiling"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
