#!/usr/bin/env python3
"""P824 public continuation micro-pilot allocator for ECDLP support routing."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P823_SCRIPT = TASK_DIR / "low_term_total2_p823_public_oracle_choice_predictor.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p824_public_micro_pilot_allocator_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p824_public_micro_pilot_allocator.md"
SCHEMA = "ecdlp.low_term_total2_p824_public_micro_pilot_allocator.v1"

SLATES = {
    "core_score_hash": (
        "prefix_span_top",
        "prefix_endpoint_top",
        "prefix_score_top512",
        "hash_support_top512",
    ),
    "score_seen_hash": (
        "prefix_endpoint_top",
        "prefix_score_top512",
        "prefix_seen_neighbor1",
        "hash_support_top512",
    ),
    "oracle_seen_score_hash": (
        "prefix_seen_neighbor1",
        "prefix_endpoint_top",
        "prefix_score_top512",
        "hash_support_top512",
    ),
}

SELECTORS = ("pilot_rho", "pilot_density", "pilot_rows_then_cost")
ALLOCATORS = ("equal_remaining", "rho_weighted_remaining", "density_weighted_remaining")


def load_p823() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p823_for_p824", P823_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P823 helpers from {P823_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def option_for(record: dict[str, Any], support_policy: str, budget: int) -> dict[str, Any]:
    for option in record["oracle_options_by_mode"][support_policy]:
        if int(option["budget"]) == int(budget):
            return option
    raise KeyError((record["context_id"], support_policy, budget))


def choose_support(record: dict[str, Any], slate: tuple[str, ...], pilot_budget: int, selector: str) -> dict[str, Any]:
    options = [option_for(record, policy, pilot_budget) for policy in slate]
    if selector == "pilot_density":
        return max(
            options,
            key=lambda option: (
                ratio(int(option["recovered_rho_baseline"]), max(1, int(option["variable_cost"]))) or 0.0,
                int(option["recovered_rho_baseline"]),
                -int(option["variable_cost"]),
                str(option["policy_name"]),
            ),
        )
    if selector == "pilot_rows_then_cost":
        return max(
            options,
            key=lambda option: (
                int(option["recovered_row_count"]),
                int(option["recovered_rho_baseline"]),
                -int(option["variable_cost"]),
                str(option["policy_name"]),
            ),
        )
    return max(
        options,
        key=lambda option: (
            int(option["recovered_rho_baseline"]),
            int(option["recovered_row_count"]),
            -int(option["variable_cost"]),
            str(option["policy_name"]),
        ),
    )


def allocate_budgets(
    records: list[dict[str, Any]],
    selected_pilots: list[dict[str, Any]],
    candidate_budgets: list[int],
    pilot_budget: int,
    target_total: int,
    allocator: str,
) -> list[int] | None:
    candidates = [int(value) for value in candidate_budgets if int(value) >= int(pilot_budget)]
    if not candidates:
        return None
    if allocator == "rho_weighted_remaining":
        weights = [max(1.0, float(option["recovered_rho_baseline"])) for option in selected_pilots]
    elif allocator == "density_weighted_remaining":
        weights = [
            max(1.0e-6, float(option["recovered_rho_baseline"]) / max(1.0, float(option["variable_cost"])))
            for option in selected_pilots
        ]
    else:
        weights = [1.0 for _record in records]
    weight_sum = sum(weights) or 1.0
    desired = [float(target_total) * weight / weight_sum for weight in weights]

    states: dict[int, tuple[float, list[int]]] = {0: (0.0, [])}
    for want in desired:
        next_states: dict[int, tuple[float, list[int]]] = {}
        for used, (cost, budgets) in states.items():
            for budget in candidates:
                new_used = used + budget
                if new_used > target_total:
                    continue
                penalty = abs(math.log(float(budget) / max(1.0, want)))
                new_item = (cost + penalty, budgets + [budget])
                old_item = next_states.get(new_used)
                if old_item is None or new_item < old_item:
                    next_states[new_used] = new_item
        states = next_states
    if target_total not in states:
        return None
    return states[target_total][1]


def adjusted_micro_pilot_result(
    base_item: dict[str, Any],
    extra_variable_cost: int,
    nonchosen_pilot_budget: int,
    slate: tuple[str, ...],
    choices: list[dict[str, Any]],
) -> dict[str, Any]:
    item = copy.deepcopy(base_item)
    aggregate = item["aggregate"]
    adjusted_cost = int(aggregate["post_hit_scan_once_train_total_unit_cost"]) + int(extra_variable_cost)
    recovered_rho = int(aggregate["recovered_rho_baseline"])
    aggregate["micro_pilot_extra_variable_cost"] = int(extra_variable_cost)
    aggregate["micro_pilot_nonchosen_pilot_budget"] = int(nonchosen_pilot_budget)
    aggregate["micro_pilot_slate_size"] = len(slate)
    aggregate["post_hit_scan_once_train_total_unit_cost"] = adjusted_cost
    aggregate["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"] = ratio(adjusted_cost, recovered_rho)
    aggregate["selected_only_once_train_total_unit_cost"] = adjusted_cost
    aggregate["selected_only_once_train_total_unit_cost_over_recovered_rho"] = ratio(adjusted_cost, recovered_rho)
    item["micro_pilot_choices"] = choices
    return item


def classify_claim(item: dict[str, Any], full_pool: dict[str, Any], best_hash: dict[str, Any] | None) -> str:
    aggregate = item["aggregate"]
    recovered = int(aggregate["recovered_row_count"])
    if recovered <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    ratio_value = aggregate["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    if ratio_value is not None and ratio_value < 1.0:
        return "micro_pilot_below_rho"
    full_ratio = full_pool["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    hash_recovered = 0 if best_hash is None else int(best_hash["aggregate"]["recovered_row_count"])
    if ratio_value is not None and full_ratio is not None and ratio_value < full_ratio and recovered > hash_recovered:
        return "micro_pilot_improves_full_pool"
    return "micro_pilot_boundary"


def evaluate_micro_pilot_policy(
    env: dict[str, Any],
    records: list[dict[str, Any]],
    prefix_count: int,
    average_budget: int,
    pilot_budget: int,
    slate_name: str,
    slate: tuple[str, ...],
    selector: str,
    allocator: str,
) -> dict[str, Any] | None:
    context_count = len(records)
    target_total = int(average_budget) * context_count
    nonchosen_pilot_budget = int(pilot_budget) * (len(slate) - 1) * context_count
    remaining_total = target_total - nonchosen_pilot_budget
    if remaining_total < int(pilot_budget) * context_count:
        return None

    selected_pilots = [choose_support(record, slate, pilot_budget, selector) for record in records]
    final_budgets = allocate_budgets(records, selected_pilots, env["candidate_budgets"], pilot_budget, remaining_total, allocator)
    if final_budgets is None:
        return None

    contexts = {}
    choices = []
    extra_variable_cost = 0
    for record, selected, final_budget in zip(records, selected_pilots, final_budgets):
        selected_policy = str(selected["policy_name"])
        prepared = record["prepared_by_policy_budget"][(selected_policy, int(final_budget))]
        contexts[prepared["context_id"]] = prepared
        nonchosen_options = [option_for(record, policy, pilot_budget) for policy in slate if policy != selected_policy]
        extra_variable_cost += sum(int(option["variable_cost"]) for option in nonchosen_options)
        choices.append(
            {
                "allocated_final_budget": int(final_budget),
                "base_context_id": record["context_id"],
                "nonchosen_pilot_variable_cost": sum(int(option["variable_cost"]) for option in nonchosen_options),
                "pilot_budget": int(pilot_budget),
                "pilot_recovered_rho": int(selected["recovered_rho_baseline"]),
                "pilot_recovered_rows": int(selected["recovered_row_count"]),
                "selected_policy": selected_policy,
                "target": record["target"],
            }
        )

    name = f"micro_{slate_name}_{selector}_{allocator}_p{pilot_budget}"
    base = env["p823"].aggregate_policy(env, name, "micro_pilot_allocator", prefix_count, average_budget, contexts)
    return adjusted_micro_pilot_result(base, extra_variable_cost, nonchosen_pilot_budget, slate, choices)


def compact_policy_result(env: dict[str, Any], item: dict[str, Any] | None) -> dict[str, Any] | None:
    if item is None:
        return None
    compact = env["p815"].compact_policy_result(env["p812"], item)
    for key in (
        "micro_pilot_extra_variable_cost",
        "micro_pilot_nonchosen_pilot_budget",
        "micro_pilot_slate_size",
    ):
        if key in item["aggregate"]:
            compact["aggregate"][key] = item["aggregate"][key]
    if "micro_pilot_choices" in item:
        compact["micro_pilot_choices"] = item["micro_pilot_choices"]
    return compact


def evaluate_cell(env: dict[str, Any], prefix_count: int, average_budget: int) -> dict[str, Any]:
    p823 = env["p823"]
    p818 = env["p818"]
    records = [
        record
        for record in env["records_by_prefix"][int(prefix_count)]
        if record["namespace"] in set(env["test_namespaces"])
    ]
    policy_results = []

    def add_policy(name: str, kind: str, contexts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        item = p823.aggregate_policy(env, name, kind, prefix_count, average_budget, contexts)
        policy_results.append(item)
        return item

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
        add_policy(equal_name, kind, contexts)

    full_pool = next(item for item in policy_results if item["policy"]["name"] == "equal_full_pool")
    best_hash = p818.best_result(policy_results, {"hash_control"})

    micro_results = []
    for pilot_budget in env["pilot_budgets"]:
        if int(pilot_budget) > int(average_budget):
            continue
        for slate_name, slate in SLATES.items():
            for selector in SELECTORS:
                for allocator in ALLOCATORS:
                    item = evaluate_micro_pilot_policy(
                        env,
                        records,
                        prefix_count,
                        average_budget,
                        int(pilot_budget),
                        slate_name,
                        slate,
                        selector,
                        allocator,
                    )
                    if item is None:
                        continue
                    item["policy_claim"] = classify_claim(item, full_pool, best_hash)
                    policy_results.append(item)
                    micro_results.append(item)

    for item in policy_results:
        if "policy_claim" not in item:
            if item["policy"]["kind"] == "full_pool":
                item["policy_claim"] = "full_pool_boundary"
            elif item["policy"]["kind"] == "hash_control":
                item["policy_claim"] = "hash_control_boundary"
            else:
                item["policy_claim"] = "adaptive_boundary"

    best_micro = p818.best_result(micro_results, {"micro_pilot_allocator"})
    best_equal_adaptive = p818.best_result(policy_results, {"adaptive_prefix_gate"})
    return {
        "average_continuation_budget": int(average_budget),
        "best_equal_adaptive_gate": compact_policy_result(env, best_equal_adaptive),
        "best_hash_control": compact_policy_result(env, best_hash),
        "best_micro_pilot": compact_policy_result(env, best_micro),
        "full_pool": compact_policy_result(env, full_pool),
        "policy_results": policy_results,
        "prefix_seed_count": int(prefix_count),
    }


def determine_claim(cell_results: list[dict[str, Any]]) -> str:
    claims = {
        str(item.get("policy_claim"))
        for cell in cell_results
        for item in cell["policy_results"]
        if item["policy"]["kind"] == "micro_pilot_allocator"
    }
    if "micro_pilot_below_rho" in claims:
        return "P824_PUBLIC_MICRO_PILOT_ALLOCATOR_BELOW_RHO"
    if "micro_pilot_improves_full_pool" in claims:
        return "P824_PUBLIC_MICRO_PILOT_ALLOCATOR_IMPROVES_FULL_POOL"
    return "NEGATIVE_RESULT_P824_PUBLIC_MICRO_PILOT_ALLOCATOR_FAILS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p823 = load_p823()
    env = p823.build_environment(args)
    env["p823"] = p823
    env["pilot_budgets"] = sorted({int(value) for value in env["p815"].csv_ints(args.pilot_budgets)})

    cell_results = []
    policy_results = []
    for prefix_count in env["prefix_counts"]:
        for average_budget in env["average_budgets"]:
            cell = evaluate_cell(env, int(prefix_count), int(average_budget))
            policy_results.extend(cell.pop("policy_results"))
            cell_results.append(cell)

    best_micro = env["p818"].best_result(
        [item for item in policy_results if item["policy"]["kind"] == "micro_pilot_allocator"],
        {"micro_pilot_allocator"},
    )
    best_full = env["p818"].best_result([item for item in policy_results if item["policy"]["kind"] == "full_pool"], {"full_pool"})
    claim_status = determine_claim([{**cell, "policy_results": []} for cell in cell_results])
    claims = {
        str(item.get("policy_claim"))
        for item in policy_results
        if item["policy"]["kind"] == "micro_pilot_allocator"
    }
    if "micro_pilot_below_rho" in claims:
        claim_status = "P824_PUBLIC_MICRO_PILOT_ALLOCATOR_BELOW_RHO"
    elif "micro_pilot_improves_full_pool" in claims:
        claim_status = "P824_PUBLIC_MICRO_PILOT_ALLOCATOR_IMPROVES_FULL_POOL"
    else:
        claim_status = "NEGATIVE_RESULT_P824_PUBLIC_MICRO_PILOT_ALLOCATOR_FAILS"

    summary = {
        "average_continuation_budgets": env["average_budgets"],
        "best_full_pool": compact_policy_result(env, best_full),
        "best_micro_pilot": compact_policy_result(env, best_micro),
        "candidate_continuation_budgets": env["candidate_budgets"],
        "cell_results": cell_results,
        "pilot_budgets": env["pilot_budgets"],
        "policy_results": policy_results,
        "prefix_seed_counts": env["prefix_counts"],
        "selector_names": list(SELECTORS),
        "slates": {name: list(policies) for name, policies in SLATES.items()},
        "test_constructor_namespaces": env["test_namespaces"],
        "train_constructor_namespaces": env["train_namespaces"],
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p823_script": str(P823_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": env["p818"].now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "MICRO-PILOT DIAGNOSTIC: support family selection uses observed pilot recovered-yield counters from the harness.",
            "CONSERVATIVE CHARGE: non-selected pilot families are charged as extra variable cost; their possible recovered rows are not credited.",
            "BUDGET-PRESERVING: selected-family final budgets plus non-selected pilot budgets preserve the same total continuation trial budget as matching controls.",
            "SCAN-CHARGED: reported costs include prefix and continuation online scan cost plus target-once calibration and all-pair prefix setup.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p824_public_micro_pilot_allocator",
        "parameters": {
            "average_continuation_budgets": env["average_budgets"],
            "calibration_budget": int(args.calibration_budget),
            "candidate_continuation_budgets": env["candidate_budgets"],
            "pilot_budgets": env["pilot_budgets"],
            "prefix_seed_counts": env["prefix_counts"],
            "prefix_trial_budget": int(args.prefix_trial_budget),
            "selector_names": list(SELECTORS),
            "slates": {name: list(policies) for name, policies in SLATES.items()},
            "test_constructor_namespaces": env["test_namespaces"],
            "train_constructor_namespaces": env["train_namespaces"],
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p823 = load_p823()
    p819 = p823.load_p819()
    p818 = p819.load_p818()
    p815 = p818.load_module("ecdlp_p815_summary_for_p824", p818.P815_SCRIPT)
    p812 = p815.load_module("ecdlp_p812_summary_for_p824", p815.P812_SCRIPT)

    def compact(item: dict[str, Any]) -> dict[str, Any]:
        compacted = p815.compact_policy_result(p812, item)
        for key in (
            "micro_pilot_extra_variable_cost",
            "micro_pilot_nonchosen_pilot_budget",
            "micro_pilot_slate_size",
        ):
            if key in item["aggregate"]:
                compacted["aggregate"][key] = item["aggregate"][key]
        if "micro_pilot_choices" in item:
            compacted["micro_pilot_choices"] = item["micro_pilot_choices"]
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
    parser.add_argument(
        "--train-constructor-namespaces",
        default="posthit-p814-adapt-v26,posthit-p814-adapt-v27,posthit-p814-adapt-v28",
    )
    parser.add_argument(
        "--test-constructor-namespaces",
        default="posthit-p821-heldout-v29,posthit-p821-heldout-v30,posthit-p821-heldout-v31",
    )
    parser.add_argument("--loo-constructor-namespaces", default="")
    parser.add_argument("--skip-loo", action="store_true", default=True)
    parser.add_argument("--calibration-budget", type=int, default=256)
    parser.add_argument("--prefix-seed-counts", default="8,16,32")
    parser.add_argument("--prefix-trial-budget", type=int, default=256)
    parser.add_argument("--average-continuation-budgets", default="16,32,64")
    parser.add_argument("--pilot-budgets", default="4,8,16")
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
    p823 = load_p823()
    p818 = p823.load_p819().load_p818()
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
                "best_full_pool": summary["summary"]["best_full_pool"],
                "best_micro_pilot": summary["summary"]["best_micro_pilot"],
                "claim_status": summary["claim_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
