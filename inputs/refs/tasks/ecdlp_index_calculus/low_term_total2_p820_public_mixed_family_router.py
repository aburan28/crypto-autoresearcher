#!/usr/bin/env python3
"""P820 public mixed-family router for ECDLP continuation gates."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P819_SCRIPT = TASK_DIR / "low_term_total2_p819_support_family_oracle_bound.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p820_public_mixed_family_router_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p820_public_mixed_family_router.md"
SCHEMA = "ecdlp.low_term_total2_p820_public_mixed_family_router.v1"

PREFIX_POLICY = "prefix_all_pair"
FULL_POOL_POLICY = "continuation_all_pair"
SPAN_POLICY = "prefix_span_top"
ENDPOINT_POLICY = "prefix_endpoint_top"
INTERSECTION_POLICY = "prefix_span_endpoint_intersection"
SCORE_512_POLICY = "prefix_score_top512"
SEEN_NEIGHBOR_POLICY = "prefix_seen_neighbor1"
HASH_512_POLICY = "hash_support_top512"
SCAN_POLICY_NAMES = (
    FULL_POOL_POLICY,
    SPAN_POLICY,
    ENDPOINT_POLICY,
    INTERSECTION_POLICY,
    SCORE_512_POLICY,
    SEEN_NEIGHBOR_POLICY,
    HASH_512_POLICY,
)

EQUAL_POLICY_NAME_BY_SUPPORT = {
    FULL_POOL_POLICY: "equal_full_pool",
    SPAN_POLICY: "equal_prefix_span_top",
    ENDPOINT_POLICY: "equal_prefix_endpoint_top",
    INTERSECTION_POLICY: "equal_prefix_span_endpoint_intersection",
    SCORE_512_POLICY: "equal_prefix_score_top512",
    SEEN_NEIGHBOR_POLICY: "equal_prefix_seen_neighbor1",
    HASH_512_POLICY: "equal_hash_top512",
}

ROUTER_NAMES = (
    "router_core_equal",
    "router_core_low_combined_budget",
    "router_hash_fallback_equal",
    "router_hash_fallback_low_combined_budget",
    "router_hash_fallback_overlap_gap_budget",
    "router_hash_fallback_smallgroup_budget",
)


def load_p819() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location("ecdlp_p819_for_p820", P819_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P819 helpers from {P819_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def policy_prefix_count(item: dict[str, Any]) -> int:
    return int(item["policy"].get("prefix_seed_count") or 0)


def policy_average_budget(item: dict[str, Any]) -> int:
    return int(item["policy"].get("average_continuation_budget") or item["policy"].get("continuation_budget") or 0)


def policy_key(item: dict[str, Any]) -> tuple[int, int]:
    return (policy_prefix_count(item), policy_average_budget(item))


def compact_policy_result(p815: Any, p812: Any, item: dict[str, Any] | None) -> dict[str, Any] | None:
    return None if item is None else p815.compact_policy_result(p812, item)


def compact_by_key(p815: Any, p812: Any, items: dict[tuple[int, int], dict[str, Any] | None]) -> dict[str, dict[str, Any] | None]:
    return {
        f"p{prefix}_avg{average}": compact_policy_result(p815, p812, item)
        for (prefix, average), item in sorted(items.items())
    }


def support_rows_with_context(
    support_rows: list[dict[str, Any]],
    context_id: str,
    group_key: str,
    namespace: str,
) -> list[dict[str, Any]]:
    return [
        {
            **row,
            "context_id": context_id,
            "group_key": group_key,
            "namespace": namespace,
        }
        for row in support_rows
    ]


def support_count(record: dict[str, Any], policy_name: str) -> int:
    return int(record["support_counts_by_policy"].get(policy_name) or 0)


def concentration(record: dict[str, Any], key: str) -> float:
    value = record["diagnostics"].get(key)
    return 0.0 if value is None else float(value)


def is_small_group(record: dict[str, Any]) -> bool:
    return int(record["setup_stats"]["targeted_setup_group_additions"]) <= 5000


def choose_core_support(record: dict[str, Any]) -> str:
    span = concentration(record, "span_concentration")
    endpoint = concentration(record, "endpoint_concentration")
    intersection_count = support_count(record, INTERSECTION_POLICY)
    if is_small_group(record) and endpoint + 0.0625 >= span and intersection_count <= 180:
        return ENDPOINT_POLICY
    if is_small_group(record) and endpoint <= 0.34375 and intersection_count >= 256:
        return INTERSECTION_POLICY
    return SPAN_POLICY


def choose_hash_fallback_support(record: dict[str, Any]) -> str:
    endpoint = concentration(record, "endpoint_concentration")
    intersection_count = support_count(record, INTERSECTION_POLICY)
    if is_small_group(record) and endpoint <= 0.34375 and intersection_count < 200:
        return HASH_512_POLICY
    return choose_core_support(record)


def router_support_policy(router_name: str, record: dict[str, Any]) -> str:
    if router_name.startswith("router_hash_fallback"):
        return choose_hash_fallback_support(record)
    return choose_core_support(record)


def low_combined_score(record: dict[str, Any]) -> float:
    return 1.0 - concentration(record, "combined_concentration")


def overlap_gap_score(record: dict[str, Any]) -> float:
    span = concentration(record, "span_concentration")
    endpoint = concentration(record, "endpoint_concentration")
    intersection_count = support_count(record, INTERSECTION_POLICY)
    span_count = max(1, support_count(record, SPAN_POLICY))
    sparse_overlap = 1.0 - min(1.0, float(intersection_count) / float(span_count))
    return abs(span - endpoint) + 0.25 * sparse_overlap


def smallgroup_hash_score(record: dict[str, Any]) -> float:
    base = low_combined_score(record)
    if router_support_policy("router_hash_fallback_equal", record) == HASH_512_POLICY:
        base += 0.5
    if is_small_group(record):
        base += 0.125
    return base


def router_budget_score(router_name: str, record: dict[str, Any]) -> float:
    if router_name.endswith("_low_combined_budget"):
        return low_combined_score(record)
    if router_name.endswith("_overlap_gap_budget"):
        return overlap_gap_score(record)
    if router_name.endswith("_smallgroup_budget"):
        return smallgroup_hash_score(record)
    return 0.0


def budget_allocation(router_name: str, records: list[dict[str, Any]], average_budget: int) -> dict[str, int]:
    average = int(average_budget)
    if router_name.endswith("_equal"):
        return {record["context_id"]: average for record in records}
    if len(records) != 6:
        return {record["context_id"]: average for record in records}
    weights = [2.0, 1.5, 1.0, 0.75, 0.5, 0.25]
    ordered = sorted(
        records,
        key=lambda record: (
            router_budget_score(router_name, record),
            str(record["context_id"]),
        ),
        reverse=True,
    )
    return {
        record["context_id"]: max(1, int(round(average * weights[index])))
        for index, record in enumerate(ordered)
    }


def choose_router_contexts(
    router_name: str,
    records: list[dict[str, Any]],
    average_budget: int,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    budgets_by_context = budget_allocation(router_name, records, average_budget)
    contexts = {}
    choices = []
    for record in records:
        support_policy = router_support_policy(router_name, record)
        budget = int(budgets_by_context[record["context_id"]])
        prepared = record["prepared_by_policy_budget"][(support_policy, budget)]
        contexts[prepared["context_id"]] = prepared
        choices.append(
            {
                "base_context_id": record["context_id"],
                "budget": budget,
                "combined_concentration": concentration(record, "combined_concentration"),
                "endpoint_concentration": concentration(record, "endpoint_concentration"),
                "group_key": record["group_key"],
                "intersection_support_count": support_count(record, INTERSECTION_POLICY),
                "prepared_context_id": prepared["context_id"],
                "router_budget_score": router_budget_score(router_name, record),
                "selected_support_count": support_count(record, support_policy),
                "span_concentration": concentration(record, "span_concentration"),
                "support_policy": support_policy,
                "target": record["target"],
            }
        )
    return contexts, {
        "average_continuation_budget": int(average_budget),
        "choices": sorted(choices, key=lambda item: item["base_context_id"]),
        "router_name": router_name,
        "total_budget": sum(int(item["budget"]) for item in choices),
    }


def determine_policy_claim(
    item: dict[str, Any],
    full_pool_by_key: dict[tuple[int, int], dict[str, Any]],
    best_hash_by_key: dict[tuple[int, int], dict[str, Any] | None],
) -> str:
    aggregate = item["aggregate"]
    kind = item["policy"]["kind"]
    recovered = int(aggregate["recovered_row_count"])
    if recovered <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    ratio_value = aggregate["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    if kind == "public_router" and ratio_value is not None and ratio_value < 1.0:
        return "public_router_below_rho"
    key = policy_key(item)
    if kind == "public_router" and key in full_pool_by_key:
        full_pool = full_pool_by_key[key]
        best_hash = best_hash_by_key.get(key)
        full_ratio = full_pool["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
        hash_recovered = 0 if best_hash is None else int(best_hash["aggregate"]["recovered_row_count"])
        if ratio_value is not None and full_ratio is not None and ratio_value < full_ratio and recovered > hash_recovered:
            return "public_router_improves_equal_budget_full_pool"
    if kind == "oracle_gate":
        return "oracle_boundary"
    if kind == "adaptive_prefix_gate":
        return "adaptive_boundary"
    if kind == "hash_control":
        return "hash_control_boundary"
    if kind == "full_pool":
        return "full_pool_boundary"
    return "router_boundary"


def determine_claim(results: list[dict[str, Any]]) -> str:
    claims = {str(item.get("policy_claim")) for item in results}
    if "public_router_below_rho" in claims:
        return "P820_PUBLIC_ROUTER_BELOW_RHO"
    if "public_router_improves_equal_budget_full_pool" in claims:
        return "P820_PUBLIC_ROUTER_IMPROVES_EQUAL_BUDGET_FULL_POOL"
    return "NEGATIVE_RESULT_P820_PUBLIC_ROUTER_FAILS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p819 = load_p819()
    p818 = p819.load_p818()
    p815 = p818.load_module("ecdlp_p815_for_p820", p818.P815_SCRIPT)
    p812 = p815.load_module("ecdlp_p812_for_p820", p815.P812_SCRIPT)
    p805 = p812.load_module("ecdlp_p805_for_p820", p812.P805_SCRIPT)
    p806 = p812.load_module("ecdlp_p806_for_p820", p812.P806_SCRIPT)
    p807 = p812.load_module("ecdlp_p807_for_p820", p812.P807_SCRIPT)
    p808 = p812.load_module("ecdlp_p808_for_p820", p812.P808_SCRIPT)
    p807.configure_p807(p806)

    modules = p808.load_research_stack(p806)
    p801 = modules["p801"]
    p800 = p801.load_module("ecdlp_p800_for_p820", p801.P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p820", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p820", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p820", p798.P797_SCRIPT)
    p784 = modules["p784"]
    p787 = modules["p787"]
    p788 = modules["p788"]
    p794 = modules["p794"]
    p795 = modules["p795"]
    p793 = modules["p793"]
    p792 = modules["p792"]
    p789 = modules["p789"]
    stack = modules["stack"]
    p746 = stack["p746"]
    p748 = stack["p748"]
    relprobe = stack["relprobe"]

    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    namespaces = p815.csv_strings(args.constructor_namespaces)
    prefix_counts = sorted({int(value) for value in p815.csv_ints(args.prefix_seed_counts)})
    average_budgets = sorted({int(value) for value in p815.csv_ints(args.average_continuation_budgets)})
    calibration_budget = int(args.calibration_budget)
    scan_seed_count = int(args.scan_seed_count)
    prefix_trial_budget = int(args.prefix_trial_budget)
    if max(prefix_counts) >= scan_seed_count:
        raise ValueError("--scan-seed-count must exceed every prefix seed count")
    candidate_budgets = p818.schedule_candidate_budgets(average_budgets)

    train_args = p795.namespace_args(args, args.train_seed_namespace, int(args.train_replicas))
    train_prepared = {}
    for group_key in required:
        print(f"preparing train namespace {args.train_seed_namespace} group={group_key}", flush=True)
        train_prepared[group_key] = p794.prepare_target(
            p793,
            p792,
            p789,
            p787,
            p784,
            stack,
            base_groups[group_key],
            train_args,
        )
    trained_by_group = {
        group_key: p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], calibration_budget)
        for group_key in required
    }

    context_records_by_prefix: dict[int, list[dict[str, Any]]] = defaultdict(list)
    context_diagnostics = []
    support_diagnostics = []
    for namespace in namespaces:
        for group_key in required:
            print(f"building P820 router context namespace={namespace} group={group_key}", flush=True)
            context = p806.build_public_context(
                p801,
                p746,
                relprobe,
                base_groups[group_key],
                {calibration_budget: trained_by_group[group_key]},
                [calibration_budget],
                namespace,
                args,
            )
            base_context_id = p812.context_id(namespace, group_key)
            context["context_id"] = base_context_id
            all_pairs = p801.all_support_pairs(int(context["factor_base_size"]))
            prefix_rows_by_policy, prefix_stats = p815.scan_seed_range(
                p812,
                p805,
                p801,
                p746,
                p748,
                relprobe,
                context,
                {(0, PREFIX_POLICY): all_pairs},
                (PREFIX_POLICY,),
                0,
                max(prefix_counts),
                [prefix_trial_budget],
                args,
            )
            max_prefix_rows = prefix_rows_by_policy[(PREFIX_POLICY, prefix_trial_budget)]
            prefix_setup_stats = prefix_stats[(0, PREFIX_POLICY)]
            setup_stats = {
                "targeted_setup_group_additions": int(prefix_setup_stats["targeted_setup_group_additions"]),
                "targeted_support_count": int(prefix_setup_stats["targeted_support_count"]),
                "targeted_unique_point_count": int(prefix_setup_stats["targeted_unique_point_count"]),
                "targeted_point_collision_count": int(prefix_setup_stats["targeted_point_collision_count"]),
            }
            for prefix_count in prefix_counts:
                prefix_rows = max_prefix_rows[: int(prefix_count)]
                stats = p815.prefix_support_stats(
                    p812,
                    p793,
                    p792,
                    p789,
                    prefix_rows,
                    int(context["order"]),
                    str(context["target"]),
                    int(context["factor_base_size"]),
                    int(args.feature_bins),
                )
                diagnostics = p818.concentration_info(p815, stats, int(args.top_span_bins), int(args.top_endpoint_bins))
                support_sets, support_rows = p815.support_sets_from_prefix(p812, p801, context, prefix_rows, stats, args)
                missing = [name for name in SCAN_POLICY_NAMES if name not in support_sets]
                if missing:
                    raise ValueError(f"missing support policies for P820: {missing}")
                support_counts_by_policy = {row["policy"]: int(row["selected_support_count"]) for row in support_rows}
                support_diagnostics.extend(support_rows_with_context(support_rows, base_context_id, group_key, namespace))
                scan_supports = {(0, name): support_sets[name] for name in SCAN_POLICY_NAMES}
                continuation_rows_by_policy, _continuation_stats = p815.scan_seed_range(
                    p812,
                    p805,
                    p801,
                    p746,
                    p748,
                    relprobe,
                    context,
                    scan_supports,
                    SCAN_POLICY_NAMES,
                    int(prefix_count),
                    scan_seed_count - int(prefix_count),
                    candidate_budgets,
                    args,
                )
                prepared_by_policy_budget = {}
                for policy_name in SCAN_POLICY_NAMES:
                    for budget in candidate_budgets:
                        namespace_for_context = f"{namespace}:p{prefix_count}:p820:{policy_name}:b{budget}"
                        prepared = p815.prepare_combined_policy_context(
                            p812,
                            p793,
                            p792,
                            p789,
                            p797,
                            prefix_rows,
                            continuation_rows_by_policy[(policy_name, int(budget))],
                            int(context["order"]),
                            str(context["target"]),
                            group_key,
                            namespace_for_context,
                            trained_by_group[group_key],
                            setup_stats,
                            int(context["factor_base_size"]),
                            args,
                        )
                        prepared["allocated_continuation_budget"] = int(budget)
                        prepared["base_namespace"] = namespace
                        prepared["prefix_seed_count"] = int(prefix_count)
                        prepared["support_policy_name"] = policy_name
                        prepared_by_policy_budget[(policy_name, int(budget))] = prepared
                context_diagnostics.append(
                    {
                        **diagnostics,
                        "context_id": base_context_id,
                        "group_key": group_key,
                        "namespace": namespace,
                        "prefix_seed_count": int(prefix_count),
                        "target": str(context["target"]),
                        "targeted_setup_group_additions": int(prefix_setup_stats["targeted_setup_group_additions"]),
                    }
                )
                context_records_by_prefix[int(prefix_count)].append(
                    {
                        "context_id": base_context_id,
                        "diagnostics": diagnostics,
                        "group_key": group_key,
                        "prepared_by_policy_budget": prepared_by_policy_budget,
                        "setup_stats": setup_stats,
                        "support_counts_by_policy": support_counts_by_policy,
                        "target": str(context["target"]),
                    }
                )

    contexts_by_policy: dict[tuple[str, int, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    router_diagnostics = []

    def add_context(policy_name: str, prefix_count: int, average_budget: int, prepared: dict[str, Any]) -> None:
        contexts_by_policy[(policy_name, int(prefix_count), int(average_budget))][prepared["context_id"]] = prepared

    for prefix_count, records in sorted(context_records_by_prefix.items()):
        for average_budget in average_budgets:
            for record in records:
                for support_name, equal_name in EQUAL_POLICY_NAME_BY_SUPPORT.items():
                    add_context(
                        equal_name,
                        prefix_count,
                        average_budget,
                        record["prepared_by_policy_budget"][(support_name, average_budget)],
                    )
            for router_name in ROUTER_NAMES:
                router_contexts, diagnostics = choose_router_contexts(router_name, records, average_budget)
                for prepared in router_contexts.values():
                    add_context(router_name, prefix_count, average_budget, prepared)
                router_diagnostics.append(
                    {
                        **diagnostics,
                        "prefix_seed_count": int(prefix_count),
                    }
                )

    policy_results = []
    for (policy_name, prefix_count, average_budget), contexts in sorted(contexts_by_policy.items()):
        print(f"scoring P820 policy={policy_name} prefix={prefix_count} average_budget={average_budget}", flush=True)
        if policy_name == "equal_full_pool":
            kind = "full_pool"
        elif policy_name.startswith("equal_hash"):
            kind = "hash_control"
        elif policy_name.startswith("router_"):
            kind = "public_router"
        else:
            kind = "adaptive_prefix_gate"
        policy = {
            "average_continuation_budget": int(average_budget),
            "continuation_budget": int(average_budget),
            "kind": kind,
            "name": policy_name,
            "prefix_seed_count": int(prefix_count),
            "top_k": None,
        }
        policy_results.append(p815.aggregate_policy(p812, p797, p793, policy, contexts, trained_by_group, train_prepared, args))

    full_pool_by_key = {
        policy_key(item): item
        for item in policy_results
        if item["policy"]["name"] == "equal_full_pool"
    }
    keys = sorted({(prefix, average) for _name, prefix, average in contexts_by_policy})
    best_hash_by_key = {
        key: p819.load_p818().best_result([item for item in policy_results if policy_key(item) == key], {"hash_control"})
        for key in keys
    }
    best_equal_adaptive_by_key = {
        key: p819.load_p818().best_result([item for item in policy_results if policy_key(item) == key], {"adaptive_prefix_gate"})
        for key in keys
    }
    best_public_router_by_key = {
        key: p819.load_p818().best_result([item for item in policy_results if policy_key(item) == key], {"public_router"})
        for key in keys
    }
    for item in policy_results:
        item["policy_claim"] = determine_policy_claim(item, full_pool_by_key, best_hash_by_key)

    best_public_router = p819.load_p818().best_result(policy_results, {"public_router"})
    best_equal_adaptive = p819.load_p818().best_result(policy_results, {"adaptive_prefix_gate"})
    best_hash = p819.load_p818().best_result(policy_results, {"hash_control"})
    full_pool = p819.load_p818().best_result(policy_results, {"full_pool"})

    summary = {
        "average_continuation_budgets": average_budgets,
        "best_equal_adaptive_gate": compact_policy_result(p815, p812, best_equal_adaptive),
        "best_equal_adaptive_gate_by_prefix_average": compact_by_key(p815, p812, best_equal_adaptive_by_key),
        "best_hash_control": compact_policy_result(p815, p812, best_hash),
        "best_hash_control_by_prefix_average": compact_by_key(p815, p812, best_hash_by_key),
        "best_public_router": compact_policy_result(p815, p812, best_public_router),
        "best_public_router_by_prefix_average": compact_by_key(p815, p812, best_public_router_by_key),
        "calibration_budget": calibration_budget,
        "candidate_continuation_budgets": candidate_budgets,
        "constructor_namespaces": namespaces,
        "context_diagnostics": context_diagnostics,
        "full_pool": compact_policy_result(p815, p812, full_pool),
        "full_pool_by_prefix_average": compact_by_key(p815, p812, full_pool_by_key),
        "policy_results": policy_results,
        "prefix_seed_counts": prefix_counts,
        "prefix_trial_budget": prefix_trial_budget,
        "router_diagnostics": router_diagnostics,
        "router_names": list(ROUTER_NAMES),
        "scan_policy_names": list(SCAN_POLICY_NAMES),
        "scan_seed_count": scan_seed_count,
        "support_diagnostics": support_diagnostics,
        "target_groups": required,
        "train_seed_namespace": args.train_seed_namespace,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p819_script": str(P819_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(policy_results),
        "created_at": p819.load_p818().now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC ROUTER: support family and budget choices use prefix-derived concentrations, support counts, target setup size, and deterministic hash fallback only.",
            "BUDGET-PRESERVING: weighted router schedules preserve the same total continuation trial budget as matching equal-budget controls.",
            "SCAN-CHARGED: reported costs include prefix and continuation online scan cost plus target-once calibration and all-pair prefix setup.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p820_public_mixed_family_router",
        "parameters": {
            "average_continuation_budgets": average_budgets,
            "calibration_budget": calibration_budget,
            "candidate_continuation_budgets": candidate_budgets,
            "constructor_namespaces": namespaces,
            "control_count": int(args.control_count),
            "feature_bins": int(args.feature_bins),
            "field_weight": int(args.field_weight),
            "max_relations": int(args.max_relations),
            "max_subsets": int(args.max_subsets),
            "min_line_rows": int(args.min_line_rows),
            "prefix_seed_counts": prefix_counts,
            "prefix_trial_budget": prefix_trial_budget,
            "router_names": list(ROUTER_NAMES),
            "row_policy": args.row_policy,
            "scan_policy_names": list(SCAN_POLICY_NAMES),
            "scan_seed_count": scan_seed_count,
            "sparse_policies": args.sparse_policies,
            "support_budgets": p815.csv_ints(args.support_budgets),
            "top_endpoint_bins": int(args.top_endpoint_bins),
            "top_span_bins": int(args.top_span_bins),
            "train_replicas": int(args.train_replicas),
            "train_seed_namespace": args.train_seed_namespace,
            "walk_mode": args.walk_mode,
            "width": int(args.width),
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    p819 = load_p819()
    p818 = p819.load_p818()
    p815 = p818.load_module("ecdlp_p815_summary_for_p820", p818.P815_SCRIPT)
    p812 = p815.load_module("ecdlp_p812_summary_for_p820", p815.P812_SCRIPT)
    summary = payload["summary"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **summary,
            "policy_results": [p815.compact_policy_result(p812, item) for item in summary["policy_results"]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default="posthit-p814-adapt-v26,posthit-p814-adapt-v27,posthit-p814-adapt-v28")
    parser.add_argument("--calibration-budget", type=int, default=256)
    parser.add_argument("--prefix-seed-counts", default="8,16,32")
    parser.add_argument("--prefix-trial-budget", type=int, default=256)
    parser.add_argument("--average-continuation-budgets", default="16,32,64")
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
    payload = analyze(args)
    p819 = load_p819()
    p819.load_p818().write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    p819.load_p818().write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "best_equal_adaptive_gate": summary["summary"]["best_equal_adaptive_gate"],
                "best_hash_control": summary["summary"]["best_hash_control"],
                "best_public_router": summary["summary"]["best_public_router"],
                "claim_status": summary["claim_status"],
                "full_pool": summary["summary"]["full_pool"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
