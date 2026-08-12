#!/usr/bin/env python3
"""P825 shared full-pool pilot/sketch allocator for ECDLP support routing."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P823_SCRIPT = TASK_DIR / "low_term_total2_p823_public_oracle_choice_predictor.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p825_shared_full_pool_pilot_allocator_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p825_shared_full_pool_pilot_allocator.md"
SCHEMA = "ecdlp.low_term_total2_p825_shared_full_pool_pilot_allocator.v1"

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

PUBLIC_SELECTORS = (
    "membership_rows",
    "membership_forms",
    "membership_density",
    "membership_cost_density",
)
ORACLE_SELECTORS = ("oracle_pilot_rho",)
SELECTORS = PUBLIC_SELECTORS + ORACLE_SELECTORS
PUBLIC_ALLOCATORS = (
    "equal_remaining",
    "membership_weighted_remaining",
    "density_weighted_remaining",
)
ORACLE_ALLOCATORS = ("oracle_rho_weighted_remaining",)
ALLOCATORS = PUBLIC_ALLOCATORS + ORACLE_ALLOCATORS


def load_p823() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p823_for_p825", P823_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P823 helpers from {P823_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def support_count(record: dict[str, Any], policy_name: str) -> int:
    return int(record["support_counts_by_policy"].get(policy_name) or 0)


def option_for(record: dict[str, Any], support_policy: str, budget: int) -> dict[str, Any]:
    for option in record["oracle_options_by_mode"][support_policy]:
        if int(option["budget"]) == int(budget):
            return option
    raise KeyError((record["context_id"], support_policy, budget))


def rows_by_key(prepared: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in prepared["prepared"]["records"]:
        by_key[str(record["row_key"])].append(record)
    return by_key


def examples_by_key(prepared: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(example["row_key"]): example for example in prepared["examples"]}


def continuation_row_keys(prepared: dict[str, Any]) -> set[str]:
    prefix_count = int(prepared.get("prefix_row_count") or 0)
    out = set()
    for row_key, meta in prepared["prepared"]["rows_meta"].items():
        if int(meta.get("row_index") or 0) >= prefix_count:
            out.add(str(row_key))
    return out


def continuation_record_count(prepared: dict[str, Any]) -> int:
    prefix_count = int(prepared.get("prefix_row_count") or 0)
    return sum(1 for record in prepared["prepared"]["records"] if int(record.get("row_index") or 0) >= prefix_count)


def normalized_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "factor_coeffs": [int(value) for value in record.get("factor_coeffs") or []],
        "form_index": int(record.get("form_index") or 0),
        "q_coeff": int(record.get("q_coeff") or 0),
        "rhs": int(record.get("rhs") or 0),
        "support": [int(value) for value in record.get("support") or []],
    }


def row_fingerprint(prepared: dict[str, Any], row_key: str, by_row: dict[str, list[dict[str, Any]]]) -> str:
    meta = prepared["prepared"]["rows_meta"][row_key]
    payload = {
        "generic_rho_steps": int(meta.get("generic_rho_steps") or 0),
        "online_group_additions": int(meta.get("online_group_additions") or 0),
        "records": sorted(normalized_record(record) for record in by_row.get(row_key, [])),
        "seed_label": str(meta.get("seed_label")),
        "target": str(meta.get("target")),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def pilot_profile(record: dict[str, Any], policy_name: str, pilot_budget: int) -> dict[str, Any]:
    prepared = record["prepared_by_policy_budget"][(policy_name, int(pilot_budget))]
    continuation_keys = continuation_row_keys(prepared)
    continuation_online = sum(
        int(prepared["prepared"]["rows_meta"][row_key]["online_group_additions"]) for row_key in continuation_keys
    )
    continuation_rho = sum(int(prepared["prepared"]["rows_meta"][row_key]["generic_rho_steps"]) for row_key in continuation_keys)
    option = option_for(record, policy_name, int(pilot_budget))
    form_count = continuation_record_count(prepared)
    selected_support_count = support_count(record, policy_name)
    return {
        "continuation_form_count": int(form_count),
        "continuation_online_group_additions": int(continuation_online),
        "continuation_rho_baseline": int(continuation_rho),
        "continuation_row_count": len(continuation_keys),
        "oracle_recovered_rho_baseline": int(option["recovered_rho_baseline"]),
        "oracle_recovered_row_count": int(option["recovered_row_count"]),
        "pilot_budget": int(pilot_budget),
        "policy_name": policy_name,
        "selected_support_count": int(selected_support_count),
    }


def profile_density(profile: dict[str, Any]) -> float:
    return float(profile["continuation_form_count"]) / max(1.0, float(profile["selected_support_count"]))


def profile_cost_density(profile: dict[str, Any]) -> float:
    return float(profile["continuation_form_count"]) / max(1.0, float(profile["continuation_online_group_additions"]))


def choose_support(record: dict[str, Any], slate: tuple[str, ...], pilot_budget: int, selector: str) -> dict[str, Any]:
    profiles = [pilot_profile(record, policy, int(pilot_budget)) for policy in slate]
    if selector == "membership_forms":
        key = lambda profile: (
            int(profile["continuation_form_count"]),
            int(profile["continuation_row_count"]),
            -int(profile["selected_support_count"]),
            str(profile["policy_name"]),
        )
    elif selector == "membership_density":
        key = lambda profile: (
            profile_density(profile),
            int(profile["continuation_form_count"]),
            int(profile["continuation_row_count"]),
            str(profile["policy_name"]),
        )
    elif selector == "membership_cost_density":
        key = lambda profile: (
            profile_cost_density(profile),
            int(profile["continuation_form_count"]),
            int(profile["continuation_row_count"]),
            str(profile["policy_name"]),
        )
    elif selector == "oracle_pilot_rho":
        key = lambda profile: (
            int(profile["oracle_recovered_rho_baseline"]),
            int(profile["oracle_recovered_row_count"]),
            -int(profile["continuation_online_group_additions"]),
            str(profile["policy_name"]),
        )
    else:
        key = lambda profile: (
            int(profile["continuation_row_count"]),
            int(profile["continuation_form_count"]),
            -int(profile["selected_support_count"]),
            str(profile["policy_name"]),
        )
    return max(profiles, key=key)


def allocate_budgets(
    profiles: list[dict[str, Any]],
    candidate_budgets: list[int],
    target_total: int,
    allocator: str,
) -> list[int] | None:
    candidates = [int(value) for value in candidate_budgets if int(value) > 0]
    if not candidates:
        return None
    if allocator == "membership_weighted_remaining":
        weights = [max(1.0, float(profile["continuation_form_count"])) for profile in profiles]
    elif allocator == "density_weighted_remaining":
        weights = [max(1.0e-6, profile_density(profile)) for profile in profiles]
    elif allocator == "oracle_rho_weighted_remaining":
        weights = [max(1.0, float(profile["oracle_recovered_rho_baseline"])) for profile in profiles]
    else:
        weights = [1.0 for _profile in profiles]
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


def merge_prepared_contexts(
    env: dict[str, Any],
    record: dict[str, Any],
    pilot_prepared: dict[str, Any],
    final_prepared: dict[str, Any],
    namespace: str,
    selected_policy: str,
    pilot_budget: int,
    final_budget: int,
) -> tuple[dict[str, Any], dict[str, int]]:
    context_id = env["p812"].context_id(namespace, record["group_key"])
    rows_meta: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    examples: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    stats = defaultdict(int)

    for source_name, prepared in (
        ("shared_full_pool_pilot", pilot_prepared),
        ("selected_support_continuation", final_prepared),
    ):
        by_row = rows_by_key(prepared)
        by_example = examples_by_key(prepared)
        for old_key in sorted(prepared["prepared"]["rows_meta"]):
            fingerprint = row_fingerprint(prepared, old_key, by_row)
            if fingerprint in seen:
                stats[f"{source_name}_deduped_rows"] += 1
                continue
            row_index = len(rows_meta)
            new_key = f"{record['target']}:825:{row_index}"
            seen[fingerprint] = new_key
            meta = copy.deepcopy(prepared["prepared"]["rows_meta"][old_key])
            meta["replica"] = 0
            meta["row_index"] = row_index
            rows_meta[new_key] = meta
            stats[f"{source_name}_added_rows"] += 1
            for old_record in by_row.get(old_key, []):
                new_record = copy.deepcopy(old_record)
                new_record["replica"] = 0
                new_record["row_index"] = row_index
                new_record["row_key"] = new_key
                records.append(new_record)
            source_example = by_example.get(old_key)
            if source_example is None:
                source_example = {
                    "features": {},
                    "label": False,
                    "target": record["target"],
                }
            example = copy.deepcopy(source_example)
            example["context_id"] = context_id
            example["group_key"] = record["group_key"]
            example["namespace"] = namespace
            example["row_key"] = new_key
            example["target"] = record["target"]
            examples.append(example)

    records.sort(key=lambda item: (tuple(item.get("support") or ()), int(item.get("replica") or 0), int(item.get("row_index") or 0), int(item.get("form_index") or 0)))
    row_keys = set(rows_meta)
    context = {
        "allocated_continuation_budget": int(final_budget),
        "base_namespace": record["namespace"],
        "context_id": context_id,
        "examples": examples,
        "factor_base_size": int(final_prepared.get("factor_base_size") or pilot_prepared.get("factor_base_size") or 0),
        "group_key": record["group_key"],
        "namespace": namespace,
        "order": int(final_prepared["order"]),
        "pilot_budget": int(pilot_budget),
        "pool_online_group_additions": int(env["p797"].row_online(rows_meta, row_keys)),
        "pool_recovered_label_count": sum(1 for example in examples if example.get("label")),
        "pool_rho_baseline": int(env["p797"].row_rho(rows_meta, row_keys)),
        "pool_row_count": len(row_keys),
        "prefix_row_count": int(final_prepared.get("prefix_row_count") or pilot_prepared.get("prefix_row_count") or 0),
        "prepared": {
            "dest_target": record["target"],
            "order": int(final_prepared["order"]),
            "records": records,
            "row_count": len(row_keys),
            "rows_meta": rows_meta,
        },
        "setup_stats": final_prepared["setup_stats"],
        "shared_pilot_policy_name": "continuation_all_pair",
        "support_policy_name": selected_policy,
        "target": record["target"],
    }
    return context, {key: int(value) for key, value in stats.items()}


def is_public_policy(selector: str, allocator: str) -> bool:
    return selector in PUBLIC_SELECTORS and allocator in PUBLIC_ALLOCATORS


def evaluate_shared_pilot_policy(
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
    shared_pilot_budget_total = int(pilot_budget) * context_count
    remaining_total = target_total - shared_pilot_budget_total
    if remaining_total <= 0:
        return None

    selected_profiles = [choose_support(record, slate, int(pilot_budget), selector) for record in records]
    final_budgets = allocate_budgets(selected_profiles, env["candidate_budgets"], remaining_total, allocator)
    if final_budgets is None:
        return None

    contexts = {}
    choices = []
    merge_totals = defaultdict(int)
    for record, profile, final_budget in zip(records, selected_profiles, final_budgets):
        selected_policy = str(profile["policy_name"])
        pilot_prepared = record["prepared_by_policy_budget"][(env["p823"].FULL_POOL_POLICY, int(pilot_budget))]
        final_prepared = record["prepared_by_policy_budget"][(selected_policy, int(final_budget))]
        namespace = (
            f"{record['namespace']}:p{prefix_count}:p825:{slate_name}:"
            f"{selector}:{allocator}:{selected_policy}:pilot{pilot_budget}:b{final_budget}"
        )
        merged, merge_stats = merge_prepared_contexts(
            env,
            record,
            pilot_prepared,
            final_prepared,
            namespace,
            selected_policy,
            int(pilot_budget),
            int(final_budget),
        )
        contexts[merged["context_id"]] = merged
        for key, value in merge_stats.items():
            merge_totals[key] += int(value)
        choices.append(
            {
                "allocated_final_budget": int(final_budget),
                "base_context_id": record["context_id"],
                "continuation_form_count": int(profile["continuation_form_count"]),
                "continuation_online_group_additions": int(profile["continuation_online_group_additions"]),
                "continuation_row_count": int(profile["continuation_row_count"]),
                "group_key": record["group_key"],
                "membership_cost_density": ratio(profile["continuation_form_count"], profile["continuation_online_group_additions"]),
                "membership_density": ratio(profile["continuation_form_count"], max(1, profile["selected_support_count"])),
                "namespace": record["namespace"],
                "oracle_recovered_rho_baseline": int(profile["oracle_recovered_rho_baseline"]),
                "oracle_recovered_row_count": int(profile["oracle_recovered_row_count"]),
                "pilot_budget": int(pilot_budget),
                "selected_policy": selected_policy,
                "selected_support_count": int(profile["selected_support_count"]),
                "synthetic_context_id": merged["context_id"],
                "synthetic_pool_online_group_additions": int(merged["pool_online_group_additions"]),
                "synthetic_pool_row_count": int(merged["pool_row_count"]),
                "target": record["target"],
            }
        )

    public = is_public_policy(selector, allocator)
    name = f"shared_{slate_name}_{selector}_{allocator}_p{pilot_budget}"
    kind = "shared_public_pilot_allocator" if public else "shared_oracle_pilot_allocator"
    item = env["p823"].aggregate_policy(env, name, kind, prefix_count, average_budget, contexts)
    item["policy"].update(
        {
            "allocator": allocator,
            "pilot_budget": int(pilot_budget),
            "public_selector": bool(public),
            "selector": selector,
            "slate": slate_name,
        }
    )
    item["aggregate"]["allocated_final_budget_total"] = sum(int(value) for value in final_budgets)
    item["aggregate"]["shared_pilot_budget_total"] = int(shared_pilot_budget_total)
    item["aggregate"]["total_budget_units"] = int(target_total)
    for key, value in merge_totals.items():
        item["aggregate"][key] = int(value)
    item["shared_pilot_choices"] = choices
    return item


def classify_claim(item: dict[str, Any], full_pool: dict[str, Any], best_hash: dict[str, Any] | None) -> str:
    aggregate = item["aggregate"]
    recovered = int(aggregate["recovered_row_count"])
    if recovered <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    ratio_value = aggregate["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    full_ratio = full_pool["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    hash_recovered = 0 if best_hash is None else int(best_hash["aggregate"]["recovered_row_count"])
    is_public = bool(item["policy"].get("public_selector"))
    if is_public and ratio_value is not None and ratio_value < 1.0:
        return "shared_public_pilot_below_rho"
    if is_public and ratio_value is not None and full_ratio is not None and ratio_value < full_ratio and recovered > hash_recovered:
        return "shared_public_pilot_improves_full_pool"
    if not is_public and ratio_value is not None and ratio_value < 1.0:
        return "shared_oracle_pilot_below_rho"
    if not is_public and ratio_value is not None and full_ratio is not None and ratio_value < full_ratio and recovered > hash_recovered:
        return "shared_oracle_pilot_improves_full_pool"
    return "shared_pilot_boundary"


def compact_policy_result(env: dict[str, Any], item: dict[str, Any] | None) -> dict[str, Any] | None:
    if item is None:
        return None
    compact = env["p815"].compact_policy_result(env["p812"], item)
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
            compact["aggregate"][key] = item["aggregate"][key]
    compact["policy"]["allocator"] = item["policy"].get("allocator")
    compact["policy"]["pilot_budget"] = item["policy"].get("pilot_budget")
    compact["policy"]["public_selector"] = item["policy"].get("public_selector")
    compact["policy"]["selector"] = item["policy"].get("selector")
    compact["policy"]["slate"] = item["policy"].get("slate")
    if "shared_pilot_choices" in item:
        compact["shared_pilot_choices"] = item["shared_pilot_choices"]
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

    shared_results = []
    for pilot_budget in env["pilot_budgets"]:
        if int(pilot_budget) >= int(average_budget):
            continue
        for slate_name, slate in SLATES.items():
            for selector in SELECTORS:
                for allocator in ALLOCATORS:
                    item = evaluate_shared_pilot_policy(
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
                    shared_results.append(item)

    for item in policy_results:
        if "policy_claim" not in item:
            if item["policy"]["kind"] == "full_pool":
                item["policy_claim"] = "full_pool_boundary"
            elif item["policy"]["kind"] == "hash_control":
                item["policy_claim"] = "hash_control_boundary"
            else:
                item["policy_claim"] = "adaptive_boundary"

    best_public = p818.best_result(shared_results, {"shared_public_pilot_allocator"})
    best_oracle = p818.best_result(shared_results, {"shared_oracle_pilot_allocator"})
    best_equal_adaptive = p818.best_result(policy_results, {"adaptive_prefix_gate"})
    return {
        "average_continuation_budget": int(average_budget),
        "best_equal_adaptive_gate": compact_policy_result(env, best_equal_adaptive),
        "best_hash_control": compact_policy_result(env, best_hash),
        "best_shared_oracle_pilot": compact_policy_result(env, best_oracle),
        "best_shared_public_pilot": compact_policy_result(env, best_public),
        "full_pool": compact_policy_result(env, full_pool),
        "policy_results": policy_results,
        "prefix_seed_count": int(prefix_count),
    }


def determine_claim(policy_results: list[dict[str, Any]]) -> str:
    claims = {
        str(item.get("policy_claim"))
        for item in policy_results
        if item["policy"]["kind"] in {"shared_public_pilot_allocator", "shared_oracle_pilot_allocator"}
    }
    if "shared_public_pilot_below_rho" in claims:
        return "P825_SHARED_PUBLIC_FULL_POOL_PILOT_BELOW_RHO"
    if "shared_public_pilot_improves_full_pool" in claims:
        return "P825_SHARED_PUBLIC_FULL_POOL_PILOT_IMPROVES_FULL_POOL"
    if "shared_oracle_pilot_below_rho" in claims:
        return "P825_SHARED_ORACLE_FULL_POOL_PILOT_BELOW_RHO"
    if "shared_oracle_pilot_improves_full_pool" in claims:
        return "P825_SHARED_ORACLE_FULL_POOL_PILOT_CEILING_ONLY"
    return "NEGATIVE_RESULT_P825_SHARED_FULL_POOL_PILOT_ALLOCATOR_FAILS"


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

    best_public = env["p818"].best_result(
        [item for item in policy_results if item["policy"]["kind"] == "shared_public_pilot_allocator"],
        {"shared_public_pilot_allocator"},
    )
    best_oracle = env["p818"].best_result(
        [item for item in policy_results if item["policy"]["kind"] == "shared_oracle_pilot_allocator"],
        {"shared_oracle_pilot_allocator"},
    )
    best_full = env["p818"].best_result([item for item in policy_results if item["policy"]["kind"] == "full_pool"], {"full_pool"})
    claim_status = determine_claim(policy_results)

    summary = {
        "average_continuation_budgets": env["average_budgets"],
        "best_full_pool": compact_policy_result(env, best_full),
        "best_shared_oracle_pilot": compact_policy_result(env, best_oracle),
        "best_shared_public_pilot": compact_policy_result(env, best_public),
        "candidate_continuation_budgets": env["candidate_budgets"],
        "cell_results": cell_results,
        "pilot_budgets": env["pilot_budgets"],
        "policy_results": policy_results,
        "prefix_seed_counts": env["prefix_counts"],
        "public_allocators": list(PUBLIC_ALLOCATORS),
        "public_selectors": list(PUBLIC_SELECTORS),
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
            "SHARED-PILOT MODEL: one all-pair pilot context is merged with one selected support-family continuation context.",
            "PUBLIC SKETCH SEPARATED: membership selectors and membership-weighted allocators use row/form/support counts, not recovered-secret labels.",
            "ORACLE SKETCH SEPARATED: oracle selectors or oracle allocators use recovered pilot counters and are reported only as nonpublic ceilings.",
            "BUDGET-PRESERVING: shared pilot budget plus selected-family final budgets preserve the same total continuation trial budget as matching controls.",
            "SCAN-CHARGED: reported costs use the synthetic union row table, target-once calibration, and all-pair prefix setup.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p825_shared_full_pool_pilot_allocator",
        "parameters": {
            "average_continuation_budgets": env["average_budgets"],
            "calibration_budget": int(args.calibration_budget),
            "candidate_continuation_budgets": env["candidate_budgets"],
            "oracle_allocators": list(ORACLE_ALLOCATORS),
            "oracle_selectors": list(ORACLE_SELECTORS),
            "pilot_budgets": env["pilot_budgets"],
            "prefix_seed_counts": env["prefix_counts"],
            "prefix_trial_budget": int(args.prefix_trial_budget),
            "public_allocators": list(PUBLIC_ALLOCATORS),
            "public_selectors": list(PUBLIC_SELECTORS),
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
    p815 = p818.load_module("ecdlp_p815_summary_for_p825", p818.P815_SCRIPT)
    p812 = p815.load_module("ecdlp_p812_summary_for_p825", p815.P812_SCRIPT)

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
                "best_shared_oracle_pilot": summary["summary"]["best_shared_oracle_pilot"],
                "best_shared_public_pilot": summary["summary"]["best_shared_public_pilot"],
                "claim_status": summary["claim_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
