#!/usr/bin/env python3
"""P823 public oracle-choice predictor for ECDLP support-family routing."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P819_SCRIPT = TASK_DIR / "low_term_total2_p819_support_family_oracle_bound.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p823_public_oracle_choice_predictor_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p823_public_oracle_choice_predictor.md"
SCHEMA = "ecdlp.low_term_total2_p823_public_oracle_choice_predictor.v1"

PREFIX_POLICY = "prefix_all_pair"
FULL_POOL_POLICY = "continuation_all_pair"

PREDICTOR_SPECS = (
    {"name": "public_knn1_same_group_equal_budget", "kind": "knn", "k": 1, "same_group": True, "budget_mode": "equal"},
    {"name": "public_knn1_same_group_dp_budget", "kind": "knn", "k": 1, "same_group": True, "budget_mode": "dp"},
    {"name": "public_knn3_same_group_dp_budget", "kind": "knn", "k": 3, "same_group": True, "budget_mode": "dp"},
    {"name": "public_knn1_any_group_dp_budget", "kind": "knn", "k": 1, "same_group": False, "budget_mode": "dp"},
    {"name": "public_knn3_any_group_dp_budget", "kind": "knn", "k": 3, "same_group": False, "budget_mode": "dp"},
    {"name": "public_prototype_equal_budget", "kind": "prototype", "k": 0, "same_group": False, "budget_mode": "equal"},
    {"name": "public_prototype_dp_budget", "kind": "prototype", "k": 0, "same_group": False, "budget_mode": "dp"},
)


def load_p819() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p819_for_p823", P819_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P819 helpers from {P819_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def unique_csv_strings(p815: Any, *items: str) -> list[str]:
    seen = set()
    out = []
    for item in items:
        for value in p815.csv_strings(item):
            if value not in seen:
                seen.add(value)
                out.append(value)
    return out


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


def feature_map(record: dict[str, Any], support_policies: tuple[str, ...]) -> dict[str, float]:
    diagnostics = record["diagnostics"]
    total_prefix = max(1, int(diagnostics.get("total_prefix_record_count") or 0))
    full_support = max(1, support_count(record, FULL_POOL_POLICY))
    features = {
        "combined_concentration": concentration(record, "combined_concentration"),
        "endpoint_concentration": concentration(record, "endpoint_concentration"),
        "is_small_group": 1.0 if int(record["setup_stats"]["targeted_setup_group_additions"]) <= 5000 else 0.0,
        "prefix_seed_count_scaled": float(record["prefix_seed_count"]) / 32.0,
        "setup_group_scaled": float(record["setup_stats"]["targeted_setup_group_additions"]) / 10000.0,
        "span_concentration": concentration(record, "span_concentration"),
        "top_endpoint_rate": float(diagnostics.get("top_endpoint_hit_count") or 0) / float(total_prefix),
        "top_span_rate": float(diagnostics.get("top_span_hit_count") or 0) / float(total_prefix),
    }
    full_log = math.log1p(full_support)
    for policy_name in support_policies:
        count = support_count(record, policy_name)
        features[f"support_log:{policy_name}"] = math.log1p(count) / full_log
        features[f"support_ratio:{policy_name}"] = float(count) / float(full_support)
    return features


def vectorize(features: dict[str, float], feature_names: list[str]) -> tuple[float, ...]:
    return tuple(float(features.get(name, 0.0)) for name in feature_names)


def squared_distance(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return sum((a - b) * (a - b) for a, b in zip(left, right))


def constant_cost_for_records(env: dict[str, Any], records: list[dict[str, Any]]) -> int:
    p812 = env["p812"]
    p797 = env["p797"]
    args = env["args"]
    groups = sorted({record["group_key"] for record in records})
    setup_items = [
        {
            "group_key": record["group_key"],
            "targeted_setup_group_additions": record["setup_stats"]["targeted_setup_group_additions"],
        }
        for record in records
    ]
    train_costs = {
        group_key: p797.train_cost(env["trained_by_group"][group_key], env["train_prepared"][group_key])
        for group_key in groups
    }
    return (
        sum(int(cost["calibration_online_group_additions"]) for cost in train_costs.values())
        + p812.group_once_sum(setup_items, "targeted_setup_group_additions")
        + int(args.field_weight) * sum(int(cost["calibration_field_ops"]) for cost in train_costs.values())
    )


def oracle_for_records(
    env: dict[str, Any],
    records: list[dict[str, Any]],
    average_budget: int,
) -> dict[str, Any] | None:
    p818 = env["p818"]
    return p818.choose_oracle_allocation(
        records,
        env["oracle_support_policies"],
        int(average_budget),
        constant_cost_for_records(env, records),
    )


def label_examples_from_oracle(
    records: list[dict[str, Any]],
    oracle: dict[str, Any] | None,
    feature_names: list[str],
) -> list[dict[str, Any]]:
    if oracle is None:
        return []
    record_by_context = {record["context_id"]: record for record in records}
    examples = []
    for choice in oracle["choices"]:
        base_context_id = choice["base_context_id"]
        record = record_by_context[base_context_id]
        features = record["features"]
        examples.append(
            {
                "budget": int(choice["budget"]),
                "features": features,
                "group_key": record["group_key"],
                "namespace": record["namespace"],
                "policy_name": str(choice["policy_name"]),
                "record_context_id": base_context_id,
                "target": record["target"],
                "vector": vectorize(features, feature_names),
            }
        )
    return examples


def choose_weighted_policy(neighbors: list[tuple[float, dict[str, Any]]]) -> tuple[str, float, str, float]:
    weights_by_policy: dict[str, float] = defaultdict(float)
    budgets_by_policy: dict[str, list[tuple[float, int]]] = defaultdict(list)
    for dist, example in neighbors:
        weight = 1.0 / (math.sqrt(max(dist, 0.0)) + 1.0e-9)
        policy_name = str(example["policy_name"])
        weights_by_policy[policy_name] += weight
        budgets_by_policy[policy_name].append((weight, int(example["budget"])))
    selected_policy = max(sorted(weights_by_policy), key=lambda name: weights_by_policy[name])
    weighted_budget_num = sum(weight * budget for weight, budget in budgets_by_policy[selected_policy])
    weighted_budget_den = sum(weight for weight, _budget in budgets_by_policy[selected_policy])
    desired_budget = weighted_budget_num / max(weighted_budget_den, 1.0e-9)
    nearest = min(neighbors, key=lambda item: item[0])[1]
    return selected_policy, desired_budget, str(nearest["record_context_id"]), math.sqrt(neighbors[0][0])


def predict_knn(
    record: dict[str, Any],
    train_examples: list[dict[str, Any]],
    feature_names: list[str],
    *,
    k: int,
    same_group: bool,
) -> dict[str, Any]:
    candidates = train_examples
    if same_group:
        same = [example for example in train_examples if example["group_key"] == record["group_key"]]
        if same:
            candidates = same
    vector = vectorize(record["features"], feature_names)
    neighbors = sorted(
        ((squared_distance(vector, example["vector"]), example) for example in candidates),
        key=lambda item: (item[0], str(item[1]["record_context_id"])),
    )[: max(1, int(k))]
    policy_name, desired_budget, neighbor_id, distance = choose_weighted_policy(neighbors)
    return {
        "desired_budget": desired_budget,
        "neighbor_context_id": neighbor_id,
        "neighbor_distance": round(distance, 8),
        "support_policy": policy_name,
    }


def prototype_model(train_examples: list[dict[str, Any]], feature_names: list[str]) -> dict[str, Any]:
    by_policy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for example in train_examples:
        by_policy[str(example["policy_name"])].append(example)
    centroids = {}
    for policy_name, examples in by_policy.items():
        vectors = [example["vector"] for example in examples]
        centroids[policy_name] = tuple(sum(vector[index] for vector in vectors) / len(vectors) for index in range(len(feature_names)))
    budgets = {
        policy_name: float(median([int(example["budget"]) for example in examples]))
        for policy_name, examples in by_policy.items()
    }
    return {"budgets": budgets, "centroids": centroids}


def predict_prototype(
    record: dict[str, Any],
    model: dict[str, Any],
    feature_names: list[str],
    average_budget: int,
) -> dict[str, Any]:
    vector = vectorize(record["features"], feature_names)
    if not model["centroids"]:
        return {"desired_budget": float(average_budget), "neighbor_context_id": None, "neighbor_distance": None, "support_policy": FULL_POOL_POLICY}
    policy_name, dist = min(
        (
            (policy_name, squared_distance(vector, centroid))
            for policy_name, centroid in model["centroids"].items()
        ),
        key=lambda item: (item[1], item[0]),
    )
    return {
        "desired_budget": float(model["budgets"].get(policy_name, average_budget)),
        "neighbor_context_id": f"prototype:{policy_name}",
        "neighbor_distance": round(math.sqrt(dist), 8),
        "support_policy": policy_name,
    }


def allocate_budgets(
    desired_budgets: list[float],
    average_budget: int,
    candidate_budgets: list[int],
    budget_mode: str,
) -> list[int]:
    target_total = int(average_budget) * len(desired_budgets)
    if budget_mode == "equal":
        return [int(average_budget)] * len(desired_budgets)
    candidates = sorted({int(average_budget), *(int(value) for value in candidate_budgets if int(value) > 0)})
    dp: dict[int, tuple[float, list[int]]] = {0: (0.0, [])}
    for desired in desired_budgets:
        next_dp: dict[int, tuple[float, list[int]]] = {}
        desired = max(1.0, float(desired))
        for used, (cost, budgets) in dp.items():
            for budget in candidates:
                new_used = used + budget
                if new_used > target_total:
                    continue
                new_cost = cost + abs(math.log(float(budget) / desired))
                existing = next_dp.get(new_used)
                new_budgets = budgets + [budget]
                if existing is None or (new_cost, new_budgets) < (existing[0], existing[1]):
                    next_dp[new_used] = (new_cost, new_budgets)
        dp = next_dp
    if target_total not in dp:
        return [int(average_budget)] * len(desired_budgets)
    return dp[target_total][1]


def aggregate_policy(
    env: dict[str, Any],
    name: str,
    kind: str,
    prefix_count: int,
    average_budget: int,
    contexts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    policy = {
        "average_continuation_budget": int(average_budget),
        "continuation_budget": int(average_budget),
        "kind": kind,
        "name": name,
        "prefix_seed_count": int(prefix_count),
        "top_k": None,
    }
    return env["p815"].aggregate_policy(
        env["p812"],
        env["p797"],
        env["p793"],
        policy,
        contexts,
        env["trained_by_group"],
        env["train_prepared"],
        env["args"],
    )


def compact_policy_result(env: dict[str, Any], item: dict[str, Any] | None) -> dict[str, Any] | None:
    if item is None:
        return None
    return env["p815"].compact_policy_result(env["p812"], item)


def best_result(p818: Any, results: list[dict[str, Any]], kinds: set[str]) -> dict[str, Any] | None:
    return p818.best_result(results, kinds)


def predictor_contexts(
    env: dict[str, Any],
    spec: dict[str, Any],
    train_examples: list[dict[str, Any]],
    prototype: dict[str, Any],
    test_records: list[dict[str, Any]],
    feature_names: list[str],
    average_budget: int,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    predicted = []
    for record in sorted(test_records, key=lambda item: item["context_id"]):
        if spec["kind"] == "prototype":
            choice = predict_prototype(record, prototype, feature_names, average_budget)
        else:
            choice = predict_knn(
                record,
                train_examples,
                feature_names,
                k=int(spec["k"]),
                same_group=bool(spec["same_group"]),
            )
        predicted.append({"record": record, **choice})

    budgets = allocate_budgets(
        [float(item["desired_budget"]) for item in predicted],
        average_budget,
        env["candidate_budgets"],
        str(spec["budget_mode"]),
    )
    contexts = {}
    choices = []
    for item, allocated_budget in zip(predicted, budgets):
        record = item["record"]
        support_policy = str(item["support_policy"])
        prepared = record["prepared_by_policy_budget"][(support_policy, int(allocated_budget))]
        contexts[prepared["context_id"]] = prepared
        choices.append(
            {
                "allocated_budget": int(allocated_budget),
                "base_context_id": record["context_id"],
                "desired_budget": ratio(float(item["desired_budget"]), 1.0),
                "group_key": record["group_key"],
                "neighbor_context_id": item["neighbor_context_id"],
                "neighbor_distance": item["neighbor_distance"],
                "namespace": record["namespace"],
                "selected_support_count": support_count(record, support_policy),
                "support_policy": support_policy,
                "target": record["target"],
            }
        )
    diagnostics = {
        "budget_mode": spec["budget_mode"],
        "choices": sorted(choices, key=lambda item: item["base_context_id"]),
        "predictor_name": spec["name"],
        "total_budget": sum(int(item["allocated_budget"]) for item in choices),
    }
    return contexts, diagnostics


def classify_claim(
    item: dict[str, Any],
    full_pool: dict[str, Any],
    best_hash: dict[str, Any] | None,
) -> str:
    recovered = int(item["aggregate"]["recovered_row_count"])
    if recovered <= int(item["aggregate"]["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    ratio_value = item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    if item["policy"]["kind"] == "public_predictor" and ratio_value is not None and ratio_value < 1.0:
        return "public_predictor_below_rho"
    if item["policy"]["kind"] == "public_predictor":
        full_ratio = full_pool["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
        hash_recovered = 0 if best_hash is None else int(best_hash["aggregate"]["recovered_row_count"])
        if ratio_value is not None and full_ratio is not None and ratio_value < full_ratio and recovered > hash_recovered:
            return "public_predictor_improves_split_full_pool"
        return "public_predictor_boundary"
    if item["policy"]["kind"] == "oracle_gate":
        return "oracle_ceiling"
    if item["policy"]["kind"] == "adaptive_prefix_gate":
        return "adaptive_boundary"
    if item["policy"]["kind"] == "hash_control":
        return "hash_control_boundary"
    if item["policy"]["kind"] == "full_pool":
        return "full_pool_boundary"
    return "boundary"


def evaluate_split(
    env: dict[str, Any],
    split_name: str,
    train_namespaces: list[str],
    test_namespaces: list[str],
    prefix_count: int,
    average_budget: int,
) -> dict[str, Any]:
    p818 = env["p818"]
    records = env["records_by_prefix"][int(prefix_count)]
    train_records = [record for record in records if record["namespace"] in set(train_namespaces)]
    test_records = [record for record in records if record["namespace"] in set(test_namespaces)]
    if not train_records or not test_records:
        raise ValueError(f"split {split_name} has train={len(train_records)} test={len(test_records)} records")

    train_oracle = oracle_for_records(env, train_records, average_budget)
    test_oracle = oracle_for_records(env, test_records, average_budget)
    train_examples = label_examples_from_oracle(train_records, train_oracle, env["feature_names"])
    prototype = prototype_model(train_examples, env["feature_names"])

    policy_results = []
    predictor_diagnostics = []

    def add_policy(name: str, kind: str, contexts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        item = aggregate_policy(env, name, kind, prefix_count, average_budget, contexts)
        item["split"] = {
            "average_continuation_budget": int(average_budget),
            "name": split_name,
            "prefix_seed_count": int(prefix_count),
            "test_namespaces": list(test_namespaces),
            "train_namespaces": list(train_namespaces),
        }
        policy_results.append(item)
        return item

    for support_name, equal_name in env["equal_policy_name_by_support"].items():
        if support_name not in env["scan_policy_names"]:
            continue
        contexts = {
            record["prepared_by_policy_budget"][(support_name, int(average_budget))]["context_id"]: record["prepared_by_policy_budget"][
                (support_name, int(average_budget))
            ]
            for record in test_records
        }
        if equal_name == "equal_full_pool":
            kind = "full_pool"
        elif equal_name.startswith("equal_hash"):
            kind = "hash_control"
        else:
            kind = "adaptive_prefix_gate"
        add_policy(equal_name, kind, contexts)

    if test_oracle is not None:
        contexts = {choice["prepared"]["context_id"]: choice["prepared"] for choice in test_oracle["choices"]}
        add_policy("oracle_all_supports_ceiling", "oracle_gate", contexts)

    full_pool = next(item for item in policy_results if item["policy"]["name"] == "equal_full_pool")
    best_hash = best_result(p818, policy_results, {"hash_control"})

    for spec in PREDICTOR_SPECS:
        contexts, diagnostics = predictor_contexts(
            env,
            spec,
            train_examples,
            prototype,
            test_records,
            env["feature_names"],
            int(average_budget),
        )
        item = add_policy(str(spec["name"]), "public_predictor", contexts)
        diagnostics["aggregate"] = {
            "cost_over_recovered_rho": item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"],
            "recovered_rho_baseline": int(item["aggregate"]["recovered_rho_baseline"]),
            "recovered_row_count": int(item["aggregate"]["recovered_row_count"]),
        }
        predictor_diagnostics.append(diagnostics)

    for item in policy_results:
        item["policy_claim"] = classify_claim(item, full_pool, best_hash)

    best_public = best_result(p818, policy_results, {"public_predictor"})
    best_equal_adaptive = best_result(p818, policy_results, {"adaptive_prefix_gate"})
    best_oracle = best_result(p818, policy_results, {"oracle_gate"})
    split_claims = {str(item.get("policy_claim")) for item in policy_results}
    if "public_predictor_below_rho" in split_claims:
        claim = "public_predictor_below_rho"
    elif "public_predictor_improves_split_full_pool" in split_claims:
        claim = "public_predictor_improves_split_full_pool"
    else:
        claim = "negative_public_predictor_boundary"

    return {
        "average_continuation_budget": int(average_budget),
        "best_equal_adaptive_gate": compact_policy_result(env, best_equal_adaptive),
        "best_hash_control": compact_policy_result(env, best_hash),
        "best_oracle_ceiling": compact_policy_result(env, best_oracle),
        "best_public_predictor": compact_policy_result(env, best_public),
        "claim": claim,
        "full_pool": compact_policy_result(env, full_pool),
        "oracle_test_labels": None if test_oracle is None else [
            {
                "base_context_id": choice["base_context_id"],
                "budget": int(choice["budget"]),
                "policy_name": choice["policy_name"],
                "target": choice["target"],
            }
            for choice in test_oracle["choices"]
        ],
        "policy_results": policy_results,
        "predictor_diagnostics": predictor_diagnostics,
        "prefix_seed_count": int(prefix_count),
        "split_name": split_name,
        "test_namespaces": list(test_namespaces),
        "train_namespaces": list(train_namespaces),
        "train_oracle_label_count": len(train_examples),
    }


def determine_claim(split_results: list[dict[str, Any]]) -> str:
    claims = {str(result["claim"]) for result in split_results if str(result["split_name"]) == "primary_train_v26_v28_test_v29_v31"}
    if "public_predictor_below_rho" in claims:
        return "P823_PUBLIC_ORACLE_CHOICE_PREDICTOR_BELOW_RHO"
    if "public_predictor_improves_split_full_pool" in claims:
        return "P823_PUBLIC_ORACLE_CHOICE_PREDICTOR_IMPROVES_HELDOUT_FULL_POOL"
    return "NEGATIVE_RESULT_P823_PUBLIC_ORACLE_CHOICE_PREDICTOR_FAILS"


def build_environment(args: argparse.Namespace) -> dict[str, Any]:
    p819 = load_p819()
    p818 = p819.load_p818()
    p815 = p818.load_module("ecdlp_p815_for_p823", p818.P815_SCRIPT)
    p812 = p815.load_module("ecdlp_p812_for_p823", p815.P812_SCRIPT)
    p805 = p812.load_module("ecdlp_p805_for_p823", p812.P805_SCRIPT)
    p806 = p812.load_module("ecdlp_p806_for_p823", p812.P806_SCRIPT)
    p807 = p812.load_module("ecdlp_p807_for_p823", p812.P807_SCRIPT)
    p808 = p812.load_module("ecdlp_p808_for_p823", p812.P808_SCRIPT)
    p807.configure_p807(p806)

    modules = p808.load_research_stack(p806)
    p801 = modules["p801"]
    p800 = p801.load_module("ecdlp_p800_for_p823", p801.P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p823", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p823", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p823", p798.P797_SCRIPT)
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

    train_namespaces = p815.csv_strings(args.train_constructor_namespaces)
    test_namespaces = p815.csv_strings(args.test_constructor_namespaces)
    loo_namespaces = (
        unique_csv_strings(p815, args.train_constructor_namespaces, args.test_constructor_namespaces)
        if not args.loo_constructor_namespaces
        else p815.csv_strings(args.loo_constructor_namespaces)
    )
    namespaces = unique_csv_strings(
        p815,
        args.train_constructor_namespaces,
        args.test_constructor_namespaces,
        ",".join(loo_namespaces),
    )
    prefix_counts = sorted({int(value) for value in p815.csv_ints(args.prefix_seed_counts)})
    average_budgets = sorted({int(value) for value in p815.csv_ints(args.average_continuation_budgets)})
    calibration_budget = int(args.calibration_budget)
    scan_seed_count = int(args.scan_seed_count)
    prefix_trial_budget = int(args.prefix_trial_budget)
    if max(prefix_counts) >= scan_seed_count:
        raise ValueError("--scan-seed-count must exceed every prefix seed count")
    candidate_budgets = p818.schedule_candidate_budgets(average_budgets)

    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)

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

    scan_policy_names = tuple(p819.SCAN_POLICY_NAMES)
    oracle_support_policies = tuple(p819.ORACLE_SUPPORT_POLICIES)
    equal_policy_name_by_support = dict(p819.EQUAL_POLICY_NAME_BY_SUPPORT)
    records_by_prefix: dict[int, list[dict[str, Any]]] = defaultdict(list)
    context_diagnostics = []
    support_diagnostics = []

    for namespace in namespaces:
        for group_key in required:
            print(f"building P823 predictor context namespace={namespace} group={group_key}", flush=True)
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
                "targeted_point_collision_count": int(prefix_setup_stats["targeted_point_collision_count"]),
                "targeted_setup_group_additions": int(prefix_setup_stats["targeted_setup_group_additions"]),
                "targeted_support_count": int(prefix_setup_stats["targeted_support_count"]),
                "targeted_unique_point_count": int(prefix_setup_stats["targeted_unique_point_count"]),
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
                missing = [name for name in scan_policy_names if name not in support_sets]
                if missing:
                    raise ValueError(f"missing support policies for P823: {missing}")
                support_counts_by_policy = {row["policy"]: int(row["selected_support_count"]) for row in support_rows}
                support_diagnostics.extend(support_rows_with_context(support_rows, base_context_id, group_key, namespace))
                scan_supports = {(0, name): support_sets[name] for name in scan_policy_names}
                continuation_rows_by_policy, _continuation_stats = p815.scan_seed_range(
                    p812,
                    p805,
                    p801,
                    p746,
                    p748,
                    relprobe,
                    context,
                    scan_supports,
                    scan_policy_names,
                    int(prefix_count),
                    scan_seed_count - int(prefix_count),
                    candidate_budgets,
                    args,
                )
                prepared_by_policy_budget = {}
                oracle_options_by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)
                for policy_name in scan_policy_names:
                    for budget in candidate_budgets:
                        namespace_for_context = f"{namespace}:p{prefix_count}:p823:{policy_name}:b{budget}"
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
                        if policy_name in oracle_support_policies:
                            metrics = p818.score_prepared_context(p812, p797, p793, prepared, trained_by_group, args)
                            oracle_options_by_mode[policy_name].append(
                                {
                                    **metrics,
                                    "base_context_id": base_context_id,
                                    "budget": int(budget),
                                    "context_id": prepared["context_id"],
                                    "group_key": group_key,
                                    "policy_name": policy_name,
                                    "prepared": prepared,
                                    "target": str(context["target"]),
                                }
                            )
                record = {
                    "context_id": base_context_id,
                    "diagnostics": diagnostics,
                    "group_key": group_key,
                    "namespace": namespace,
                    "oracle_options_by_mode": oracle_options_by_mode,
                    "prefix_seed_count": int(prefix_count),
                    "prepared_by_policy_budget": prepared_by_policy_budget,
                    "setup_stats": setup_stats,
                    "support_counts_by_policy": support_counts_by_policy,
                    "target": str(context["target"]),
                }
                record["features"] = feature_map(record, oracle_support_policies)
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
                records_by_prefix[int(prefix_count)].append(record)

    feature_names = sorted({name for records in records_by_prefix.values() for record in records for name in record["features"]})
    return {
        "args": args,
        "average_budgets": average_budgets,
        "candidate_budgets": candidate_budgets,
        "context_diagnostics": context_diagnostics,
        "equal_policy_name_by_support": equal_policy_name_by_support,
        "feature_names": feature_names,
        "loo_namespaces": loo_namespaces,
        "namespaces": namespaces,
        "oracle_support_policies": oracle_support_policies,
        "p812": p812,
        "p815": p815,
        "p818": p818,
        "p819": p819,
        "p793": p793,
        "p797": p797,
        "prefix_counts": prefix_counts,
        "records_by_prefix": records_by_prefix,
        "scan_policy_names": scan_policy_names,
        "support_diagnostics": support_diagnostics,
        "target_groups": required,
        "test_namespaces": test_namespaces,
        "train_namespaces": train_namespaces,
        "train_prepared": train_prepared,
        "trained_by_group": trained_by_group,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    env = build_environment(args)
    split_results = []
    policy_results = []

    for prefix_count in env["prefix_counts"]:
        for average_budget in env["average_budgets"]:
            primary = evaluate_split(
                env,
                "primary_train_v26_v28_test_v29_v31",
                env["train_namespaces"],
                env["test_namespaces"],
                prefix_count,
                average_budget,
            )
            split_results.append(primary)
            policy_results.extend(primary.pop("policy_results"))
            if not args.skip_loo:
                for heldout in env["loo_namespaces"]:
                    train_namespaces = [name for name in env["loo_namespaces"] if name != heldout]
                    loo = evaluate_split(
                        env,
                        f"loo_holdout_{heldout}",
                        train_namespaces,
                        [heldout],
                        prefix_count,
                        average_budget,
                    )
                    split_results.append(loo)
                    policy_results.extend(loo.pop("policy_results"))

    primary_splits = [result for result in split_results if result["split_name"] == "primary_train_v26_v28_test_v29_v31"]
    primary_best_public = env["p818"].best_result(
        [
            item
            for item in policy_results
            if item["split"]["name"] == "primary_train_v26_v28_test_v29_v31"
        ],
        {"public_predictor"},
    )
    primary_best_oracle = env["p818"].best_result(
        [
            item
            for item in policy_results
            if item["split"]["name"] == "primary_train_v26_v28_test_v29_v31"
        ],
        {"oracle_gate"},
    )
    claim_status = determine_claim(split_results)
    summary = {
        "average_continuation_budgets": env["average_budgets"],
        "best_primary_oracle_ceiling": compact_policy_result(env, primary_best_oracle),
        "best_primary_public_predictor": compact_policy_result(env, primary_best_public),
        "candidate_continuation_budgets": env["candidate_budgets"],
        "constructor_namespaces": env["namespaces"],
        "context_diagnostics": env["context_diagnostics"],
        "feature_names": env["feature_names"],
        "loo_namespaces": [] if args.skip_loo else env["loo_namespaces"],
        "policy_results": policy_results,
        "prefix_seed_counts": env["prefix_counts"],
        "predictor_specs": list(PREDICTOR_SPECS),
        "primary_split_results": [
            {
                **result,
                "best_equal_adaptive_gate": result["best_equal_adaptive_gate"],
                "best_hash_control": result["best_hash_control"],
                "best_oracle_ceiling": result["best_oracle_ceiling"],
                "best_public_predictor": result["best_public_predictor"],
                "full_pool": result["full_pool"],
            }
            for result in primary_splits
        ],
        "split_results": split_results,
        "support_diagnostics": env["support_diagnostics"],
        "target_groups": env["target_groups"],
        "test_constructor_namespaces": env["test_namespaces"],
        "train_constructor_namespaces": env["train_namespaces"],
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p819_script": str(P819_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": env["p818"].now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC PREDICTOR: held-out support family and budget choices use only prefix-derived diagnostics, support counts, target setup size, and labels learned from training constructors.",
            "TRAIN/TEST SPLIT: primary claim trains on P814-compatible namespaces v26-v28 and tests P821-heldout namespaces v29-v31.",
            "ORACLE CEILING SEPARATED: oracle choices are reported only as a ceiling, not as a public algorithm.",
            "BUDGET-PRESERVING: public DP-budget predictors preserve the same total continuation trial budget as matching equal-budget controls.",
            "SCAN-CHARGED: reported costs include prefix and continuation online scan cost plus target-once calibration and all-pair prefix setup.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p823_public_oracle_choice_predictor",
        "parameters": {
            "average_continuation_budgets": env["average_budgets"],
            "calibration_budget": int(args.calibration_budget),
            "candidate_continuation_budgets": env["candidate_budgets"],
            "control_count": int(args.control_count),
            "feature_bins": int(args.feature_bins),
            "field_weight": int(args.field_weight),
            "loo_constructor_namespaces": [] if args.skip_loo else env["loo_namespaces"],
            "max_relations": int(args.max_relations),
            "max_subsets": int(args.max_subsets),
            "min_line_rows": int(args.min_line_rows),
            "prefix_seed_counts": env["prefix_counts"],
            "prefix_trial_budget": int(args.prefix_trial_budget),
            "predictor_specs": list(PREDICTOR_SPECS),
            "row_policy": args.row_policy,
            "scan_policy_names": list(env["scan_policy_names"]),
            "scan_seed_count": int(args.scan_seed_count),
            "sparse_policies": args.sparse_policies,
            "support_budgets": env["p815"].csv_ints(args.support_budgets),
            "test_constructor_namespaces": env["test_namespaces"],
            "top_endpoint_bins": int(args.top_endpoint_bins),
            "top_span_bins": int(args.top_span_bins),
            "train_constructor_namespaces": env["train_namespaces"],
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
    p815 = p818.load_module("ecdlp_p815_summary_for_p823", p818.P815_SCRIPT)
    p812 = p815.load_module("ecdlp_p812_summary_for_p823", p815.P812_SCRIPT)
    summary = payload["summary"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **summary,
            "policy_results": [p815.compact_policy_result(p812, item) for item in summary.get("policy_results", [])],
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
    parser.add_argument("--skip-loo", action="store_true")
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
    p819 = load_p819()
    p818 = p819.load_p818()
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
                "best_primary_oracle_ceiling": summary["summary"]["best_primary_oracle_ceiling"],
                "best_primary_public_predictor": summary["summary"]["best_primary_public_predictor"],
                "claim_status": summary["claim_status"],
                "test_constructor_namespaces": summary["summary"]["test_constructor_namespaces"],
                "train_constructor_namespaces": summary["summary"]["train_constructor_namespaces"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
