#!/usr/bin/env python3
"""P815 gated-continuation budget sweep for ECDLP post-hit support gates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P812_SCRIPT = TASK_DIR / "low_term_total2_p812_posthit_public_row_quality_sieve.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p815_gated_continuation_budget_sweep_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p815_gated_continuation_budget_sweep.md"
SCHEMA = "ecdlp.low_term_total2_p815_gated_continuation_budget_sweep.v1"
PREFIX_POLICY = "prefix_all_pair"


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


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def stable_hash_score(*parts: Any) -> int:
    text = "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest(), "big")


def policy_kind(policy_name: str) -> str:
    if policy_name == PREFIX_POLICY:
        return "adaptive_prefix_all_pair_probe"
    return "adaptive_prefix_gated_continuation"


def configure_policies(p805: Any, policy_names: tuple[str, ...]) -> None:
    p805.POLICY_NAMES = policy_names
    p805.PUBLIC_POLICIES = tuple(name for name in policy_names if name != PREFIX_POLICY)
    p805.policy_kind = policy_kind


def seed_label(index: int) -> str:
    return f"t{int(index):04d}"


def scan_seed_range(
    p812: Any,
    p805: Any,
    p801: Any,
    p746: Any,
    p748: Any,
    relprobe: Any,
    context: dict[str, Any],
    supports_by_policy: dict[tuple[int, str], set[tuple[int, int]]],
    policy_names: tuple[str, ...],
    start_index: int,
    seed_count: int,
    trial_budgets: list[int],
    args: argparse.Namespace,
) -> tuple[dict[tuple[str, int], list[dict[str, Any]]], dict[tuple[int, str], dict[str, int]]]:
    configure_policies(p805, policy_names)
    budgets = sorted({int(value) for value in trial_budgets})
    verifier = context["verifier"]
    ainvs = context["ainvs"]
    p = int(context["p"])
    order = int(context["order"])
    factor_base = context["factor_base"]
    point_policy, support_policy_stats = p801.build_point_policy_map(verifier, factor_base, ainvs, p, supports_by_policy)
    rows_by_policy = {(name, budget): [] for name in policy_names for budget in budgets}
    for index in range(int(start_index), int(start_index) + int(seed_count)):
        label = seed_label(index)
        full_seed = (
            f"ecdlp-p814-{context['namespace']}-{p812.slug(context['target'])}:"
            f"{label}:fb{context['factor_base_size']}:w2:{args.walk_mode}"
        )
        challenge, secret = relprobe.make_challenge(verifier, context["inv"], ainvs, full_seed, context["factor_base_size"])
        base = verifier.point_from_json(challenge["base"])
        public = verifier.point_from_json(challenge["public"])
        rows = p805.scan_seed_grid(
            p801,
            p746,
            p748,
            verifier,
            challenge,
            secret,
            base,
            public,
            ainvs,
            p,
            order,
            context["target"],
            len(factor_base),
            label,
            full_seed,
            [0],
            budgets,
            point_policy,
            support_policy_stats,
            args,
        )
        for name in policy_names:
            for budget in budgets:
                rows_by_policy[(name, budget)].append(rows[(0, int(budget), name)])
    return rows_by_policy, support_policy_stats


def canonical_support(support: tuple[int, int]) -> tuple[int, int]:
    left, right = int(support[0]), int(support[1])
    return (left, right) if left <= right else (right, left)


def support_bins(p812: Any, support: tuple[int, int], factor_base_size: int, bins: int) -> dict[str, Any]:
    left, right = canonical_support(support)
    span = abs(left - right)
    return {
        "endpoint": (p812.index_bin(left, factor_base_size, bins), p812.index_bin(right, factor_base_size, bins)),
        "left_bin": p812.index_bin(left, factor_base_size, bins),
        "right_bin": p812.index_bin(right, factor_base_size, bins),
        "span_bin": p812.index_bin(span, factor_base_size, bins),
    }


def prefix_support_stats(
    p812: Any,
    p793: Any,
    p792: Any,
    p789: Any,
    prefix_rows: list[dict[str, Any]],
    order: int,
    target: str,
    factor_base_size: int,
    bins: int,
) -> dict[str, Any]:
    records, _rows_meta = p792.collect_form_records(p789, [(0, prefix_rows, int(order))], str(target))
    support_counts = Counter()
    span_counts = Counter()
    endpoint_counts = Counter()
    left_counts = Counter()
    right_counts = Counter()
    line_axis_counts = Counter()
    for record in records:
        support = canonical_support(tuple(int(index) for index in record["support"]))
        support_counts[support] += 1
        bins_row = support_bins(p812, support, int(factor_base_size), int(bins))
        span_counts[bins_row["span_bin"]] += 1
        endpoint_counts[bins_row["endpoint"]] += 1
        left_counts[bins_row["left_bin"]] += 1
        right_counts[bins_row["right_bin"]] += 1
        parts = p793.line_parts(record, int(order))
        if parts is not None:
            line_axis_counts[int(parts["line_key"][2])] += 1
    return {
        "endpoint_counts": endpoint_counts,
        "left_counts": left_counts,
        "line_axis_counts": line_axis_counts,
        "record_count": len(records),
        "right_counts": right_counts,
        "span_counts": span_counts,
        "support_counts": support_counts,
    }


def top_keys(counter: Counter, count: int) -> set[Any]:
    return {key for key, _value in counter.most_common(max(0, int(count)))}


def neighbor_supports(p801: Any, supports: set[tuple[int, int]], factor_base_size: int, radius: int) -> set[tuple[int, int]]:
    out = set()
    fb_size = int(factor_base_size)
    for left, right in supports:
        for dl in range(-int(radius), int(radius) + 1):
            for dr in range(-int(radius), int(radius) + 1):
                candidate = ((int(left) + dl) % fb_size, (int(right) + dr) % fb_size)
                if candidate[0] != candidate[1]:
                    out.add(p801.canonical_support(candidate))
    return out


def hash_supports(all_pairs: list[tuple[int, int]], context_id: str, count: int) -> set[tuple[int, int]]:
    ranked = sorted(all_pairs, key=lambda support: (stable_hash_score(context_id, support[0], support[1]), support))
    return set(ranked[: max(0, min(int(count), len(ranked)))])


def ranked_prefix_supports(
    p812: Any,
    all_pairs: list[tuple[int, int]],
    stats: dict[str, Any],
    factor_base_size: int,
    bins: int,
    count: int,
) -> set[tuple[int, int]]:
    support_counts = stats["support_counts"]
    span_counts = stats["span_counts"]
    endpoint_counts = stats["endpoint_counts"]
    left_counts = stats["left_counts"]
    right_counts = stats["right_counts"]

    def score(support: tuple[int, int]) -> tuple[int, int, int, int, int, int]:
        bins_row = support_bins(p812, support, int(factor_base_size), int(bins))
        return (
            int(support_counts[support]),
            int(span_counts[bins_row["span_bin"]]),
            int(endpoint_counts[bins_row["endpoint"]]),
            int(left_counts[bins_row["left_bin"]]) + int(right_counts[bins_row["right_bin"]]),
            -abs(int(support[0]) - int(support[1])),
            -int(sum(support)),
        )

    ranked = sorted(all_pairs, key=lambda support: (score(support), tuple(-part for part in support)), reverse=True)
    return set(ranked[: max(0, min(int(count), len(ranked)))])


def support_sets_from_prefix(
    p812: Any,
    p801: Any,
    context: dict[str, Any],
    prefix_rows: list[dict[str, Any]],
    stats: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[dict[str, set[tuple[int, int]]], list[dict[str, Any]]]:
    factor_base_size = int(context["factor_base_size"])
    bins = int(args.feature_bins)
    all_pairs = sorted(p801.all_support_pairs(factor_base_size))
    support_budgets = csv_ints(args.support_budgets)
    top_spans = top_keys(stats["span_counts"], int(args.top_span_bins))
    top_endpoints = top_keys(stats["endpoint_counts"], int(args.top_endpoint_bins))
    seen_supports = set(stats["support_counts"])
    out: dict[str, set[tuple[int, int]]] = {"continuation_all_pair": set(all_pairs)}
    for budget in support_budgets:
        out[f"hash_support_top{budget}"] = hash_supports(all_pairs, context["context_id"], int(budget))
        out[f"prefix_score_top{budget}"] = ranked_prefix_supports(
            p812,
            all_pairs,
            stats,
            factor_base_size,
            bins,
            int(budget),
        )
    out["prefix_seen_supports"] = set(seen_supports)
    out["prefix_seen_neighbor1"] = neighbor_supports(p801, seen_supports, factor_base_size, 1)
    out["prefix_span_top"] = {
        support for support in all_pairs if support_bins(p812, support, factor_base_size, bins)["span_bin"] in top_spans
    }
    out["prefix_endpoint_top"] = {
        support for support in all_pairs if support_bins(p812, support, factor_base_size, bins)["endpoint"] in top_endpoints
    }
    out["prefix_span_endpoint_intersection"] = out["prefix_span_top"] & out["prefix_endpoint_top"]
    diagnostics = [
        {
            "policy": name,
            "prefix_record_count": int(stats["record_count"]),
            "prefix_row_count": len(prefix_rows),
            "selected_support_count": len(supports),
        }
        for name, supports in sorted(out.items())
    ]
    return out, diagnostics


def prepare_combined_policy_context(
    p812: Any,
    p793: Any,
    p792: Any,
    p789: Any,
    p797: Any,
    prefix_rows: list[dict[str, Any]],
    continuation_rows: list[dict[str, Any]],
    order: int,
    target: str,
    group_key: str,
    namespace: str,
    trained: dict[tuple[int, int, int, int], dict[str, Any]],
    setup_stats: dict[str, Any],
    factor_base_size: int,
    args: argparse.Namespace,
) -> dict[str, Any]:
    combined_rows = list(prefix_rows) + list(continuation_rows)
    prepared = p812.prepare_context(
        p793,
        p792,
        p789,
        p797,
        combined_rows,
        int(order),
        str(target),
        group_key,
        namespace,
        trained,
        setup_stats,
        int(factor_base_size),
        args,
    )
    prepared["prefix_row_count"] = len(prefix_rows)
    prepared["continuation_row_count"] = len(continuation_rows)
    prepared["factor_base_size"] = int(factor_base_size)
    return prepared


def aggregate_policy(
    p812: Any,
    p797: Any,
    p793: Any,
    policy: dict[str, Any],
    contexts: dict[str, dict[str, Any]],
    trained_by_group: dict[str, dict[tuple[int, int, int, int], dict[str, Any]]],
    train_prepared_by_group: dict[str, dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    selected_by_context = {
        cid: {str(example["row_key"]) for example in context["examples"]}
        for cid, context in contexts.items()
    }
    item = p812.aggregate_policy(
        p797,
        p793,
        policy,
        selected_by_context,
        contexts,
        trained_by_group,
        train_prepared_by_group,
        args,
    )
    return item


def best_result(results: list[dict[str, Any]], kinds: set[str]) -> dict[str, Any] | None:
    candidates = [
        item
        for item in results
        if item["policy"]["kind"] in kinds
        and item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"] is not None
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: item["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"])


def policy_continuation_budget(item: dict[str, Any]) -> int:
    return int(item["policy"].get("continuation_budget") or 0)


def determine_policy_claim(
    item: dict[str, Any],
    full_pool_by_budget: dict[int, dict[str, Any]],
    best_hash_by_budget: dict[int, dict[str, Any]],
) -> str:
    aggregate = item["aggregate"]
    kind = item["policy"]["kind"]
    budget = policy_continuation_budget(item)
    recovered = int(aggregate["recovered_row_count"])
    if recovered <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    ratio_value = aggregate["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
    if kind == "adaptive_prefix_gate" and ratio_value is not None and ratio_value < 1.0:
        return "budgeted_adaptive_gate_below_rho"
    if kind == "adaptive_prefix_gate" and budget in full_pool_by_budget:
        full_pool = full_pool_by_budget[budget]
        best_hash = best_hash_by_budget.get(budget)
        full_ratio = full_pool["aggregate"]["post_hit_scan_once_train_total_unit_cost_over_recovered_rho"]
        hash_recovered = 0 if best_hash is None else int(best_hash["aggregate"]["recovered_row_count"])
        if ratio_value is not None and full_ratio is not None and ratio_value < full_ratio and recovered > hash_recovered:
            return "budgeted_adaptive_gate_improves_same_budget_full_pool"
    if kind == "hash_control":
        return "hash_control_boundary"
    if kind == "full_pool":
        return "full_pool_boundary"
    return "adaptive_boundary"


def determine_claim(results: list[dict[str, Any]]) -> str:
    claims = {str(item.get("policy_claim")) for item in results}
    if "budgeted_adaptive_gate_below_rho" in claims:
        return "P815_BUDGETED_ADAPTIVE_GATE_BELOW_RHO"
    if "budgeted_adaptive_gate_improves_same_budget_full_pool" in claims:
        return "P815_BUDGETED_ADAPTIVE_GATE_IMPROVES_SAME_BUDGET_FULL_POOL"
    return "NEGATIVE_RESULT_P815_BUDGET_SWEEP_FAILS"


def compact_policy_result(p812: Any, item: dict[str, Any] | None) -> dict[str, Any] | None:
    return None if item is None else p812.compact_policy_result(item)


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p812 = load_module("ecdlp_p812_for_p815", P812_SCRIPT)
    p805 = p812.load_module("ecdlp_p805_for_p815", p812.P805_SCRIPT)
    p806 = p812.load_module("ecdlp_p806_for_p815", p812.P806_SCRIPT)
    p807 = p812.load_module("ecdlp_p807_for_p815", p812.P807_SCRIPT)
    p808 = p812.load_module("ecdlp_p808_for_p815", p812.P808_SCRIPT)
    p807.configure_p807(p806)

    modules = p808.load_research_stack(p806)
    p801 = modules["p801"]
    p800 = p801.load_module("ecdlp_p800_for_p815", p801.P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p815", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p815", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p815", p798.P797_SCRIPT)
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
    namespaces = csv_strings(args.constructor_namespaces)
    calibration_budget = int(args.calibration_budget)
    prefix_count = int(args.prefix_seed_count)
    scan_seed_count = int(args.scan_seed_count)
    continuation_count = scan_seed_count - prefix_count
    if continuation_count <= 0:
        raise ValueError("--scan-seed-count must exceed --prefix-seed-count")
    prefix_trial_budget = int(args.prefix_trial_budget)
    continuation_budgets = sorted({int(value) for value in csv_ints(args.continuation_budgets)})
    if not continuation_budgets:
        raise ValueError("--continuation-budgets must include at least one positive integer")

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

    contexts_by_policy: dict[tuple[str, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    context_diagnostics = []
    support_diagnostics = []
    for namespace in namespaces:
        for group_key in required:
            print(f"building P815 prefix context namespace={namespace} group={group_key}", flush=True)
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
            context["context_id"] = p812.context_id(namespace, group_key)
            all_pairs = p801.all_support_pairs(int(context["factor_base_size"]))
            prefix_rows_by_policy, prefix_stats = scan_seed_range(
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
                prefix_count,
                [prefix_trial_budget],
                args,
            )
            prefix_rows = prefix_rows_by_policy[(PREFIX_POLICY, prefix_trial_budget)]
            stats = prefix_support_stats(
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
            support_sets, support_rows = support_sets_from_prefix(p812, p801, context, prefix_rows, stats, args)
            policy_names = tuple(sorted(support_sets))
            continuation_rows_by_policy, continuation_stats = scan_seed_range(
                p812,
                p805,
                p801,
                p746,
                p748,
                relprobe,
                context,
                {(0, name): supports for name, supports in support_sets.items()},
                policy_names,
                prefix_count,
                continuation_count,
                continuation_budgets,
                args,
            )
            for row in support_rows:
                support_diagnostics.append({**row, "context_id": context["context_id"], "group_key": group_key, "namespace": namespace})
            context_diagnostics.append(
                {
                    "context_id": context["context_id"],
                    "continuation_budgets": continuation_budgets,
                    "continuation_seed_count": continuation_count,
                    "group_key": group_key,
                    "namespace": namespace,
                    "prefix_record_count": int(stats["record_count"]),
                    "prefix_seed_count": prefix_count,
                    "prefix_trial_budget": prefix_trial_budget,
                    "target": str(context["target"]),
                    "targeted_setup_group_additions": int(prefix_stats[(0, PREFIX_POLICY)]["targeted_setup_group_additions"]),
                }
            )
            for (policy_name, continuation_budget), continuation_rows in continuation_rows_by_policy.items():
                budget_namespace = f"{namespace}:b{continuation_budget}"
                prepared_context = prepare_combined_policy_context(
                    p812,
                    p793,
                    p792,
                    p789,
                    p797,
                    prefix_rows,
                    continuation_rows,
                    int(context["order"]),
                    str(context["target"]),
                    group_key,
                    budget_namespace,
                    trained_by_group[group_key],
                    {
                        "targeted_setup_group_additions": int(prefix_stats[(0, PREFIX_POLICY)]["targeted_setup_group_additions"]),
                        "targeted_support_count": int(prefix_stats[(0, PREFIX_POLICY)]["targeted_support_count"]),
                        "targeted_unique_point_count": int(prefix_stats[(0, PREFIX_POLICY)]["targeted_unique_point_count"]),
                        "targeted_point_collision_count": int(prefix_stats[(0, PREFIX_POLICY)]["targeted_point_collision_count"]),
                    },
                    int(context["factor_base_size"]),
                    args,
                )
                prepared_context["base_namespace"] = namespace
                prepared_context["continuation_budget"] = int(continuation_budget)
                contexts_by_policy[(policy_name, int(continuation_budget))][prepared_context["context_id"]] = prepared_context

    policy_results = []
    for (policy_name, budget_value), contexts in sorted(contexts_by_policy.items()):
        print(f"scoring P815 policy={policy_name} continuation_budget={budget_value}", flush=True)
        if policy_name == "continuation_all_pair":
            policy = {"continuation_budget": int(budget_value), "kind": "full_pool", "name": policy_name, "top_k": None}
        elif policy_name.startswith("hash_support"):
            policy = {"continuation_budget": int(budget_value), "kind": "hash_control", "name": policy_name, "top_k": None}
        else:
            policy = {
                "continuation_budget": int(budget_value),
                "kind": "adaptive_prefix_gate",
                "name": policy_name,
                "top_k": None,
            }
        policy_results.append(aggregate_policy(p812, p797, p793, policy, contexts, trained_by_group, train_prepared, args))

    full_pool_by_budget = {
        policy_continuation_budget(item): item
        for item in policy_results
        if item["policy"]["name"] == "continuation_all_pair"
    }
    best_hash_by_budget = {
        budget: best_result(
            [item for item in policy_results if policy_continuation_budget(item) == budget],
            {"hash_control"},
        )
        for budget in continuation_budgets
    }
    best_adaptive_by_budget = {
        budget: best_result(
            [item for item in policy_results if policy_continuation_budget(item) == budget],
            {"adaptive_prefix_gate"},
        )
        for budget in continuation_budgets
    }
    for item in policy_results:
        item["policy_claim"] = determine_policy_claim(item, full_pool_by_budget, best_hash_by_budget)
    best_adaptive = best_result(policy_results, {"adaptive_prefix_gate"})
    best_hash = best_result(policy_results, {"hash_control"})
    full_pool = best_result(policy_results, {"full_pool"})

    summary = {
        "best_adaptive_prefix_gate": compact_policy_result(p812, best_adaptive),
        "best_adaptive_prefix_gate_by_budget": {
            str(budget): compact_policy_result(p812, item) for budget, item in sorted(best_adaptive_by_budget.items())
        },
        "best_hash_control": compact_policy_result(p812, best_hash),
        "best_hash_control_by_budget": {
            str(budget): compact_policy_result(p812, item) for budget, item in sorted(best_hash_by_budget.items())
        },
        "calibration_budget": calibration_budget,
        "continuation_budgets": continuation_budgets,
        "constructor_namespaces": namespaces,
        "context_diagnostics": context_diagnostics,
        "full_pool": compact_policy_result(p812, full_pool),
        "full_pool_by_budget": {
            str(budget): compact_policy_result(p812, item) for budget, item in sorted(full_pool_by_budget.items())
        },
        "policy_results": policy_results,
        "prefix_seed_count": prefix_count,
        "prefix_trial_budget": prefix_trial_budget,
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
            "p812_script": str(P812_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(policy_results),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ADAPTIVE PREFIX GATE: prefix rows use all-pair post-hit scanning; continuation rows use only public prefix-derived support gates.",
            "BUDGET SWEEP: continuation rows are separately materialized at each configured trial budget and compared only against same-budget controls.",
            "NO LABEL TRAINING: recovered-row labels are used only for evaluation, not for support gate construction.",
            "SCAN-CHARGED: reported costs include prefix and continuation online scan cost plus target-once calibration and all-pair prefix setup.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p815_gated_continuation_budget_sweep",
        "parameters": {
            "calibration_budget": calibration_budget,
            "continuation_budgets": continuation_budgets,
            "constructor_namespaces": namespaces,
            "control_count": int(args.control_count),
            "feature_bins": int(args.feature_bins),
            "field_weight": int(args.field_weight),
            "max_relations": int(args.max_relations),
            "max_subsets": int(args.max_subsets),
            "min_line_rows": int(args.min_line_rows),
            "prefix_seed_count": prefix_count,
            "prefix_trial_budget": prefix_trial_budget,
            "row_policy": args.row_policy,
            "scan_seed_count": scan_seed_count,
            "sparse_policies": args.sparse_policies,
            "support_budgets": csv_ints(args.support_budgets),
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
    p812 = load_module("ecdlp_p812_summary_for_p815", P812_SCRIPT)
    summary = payload["summary"]
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **summary,
            "policy_results": [p812.compact_policy_result(item) for item in summary["policy_results"]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default="posthit-p814-adapt-v26,posthit-p814-adapt-v27,posthit-p814-adapt-v28")
    parser.add_argument("--calibration-budget", type=int, default=256)
    parser.add_argument("--prefix-trial-budget", type=int, default=256)
    parser.add_argument("--continuation-budgets", default="32,64,128,256")
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--prefix-seed-count", type=int, default=32)
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
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "best_adaptive_prefix_gate": summary["summary"]["best_adaptive_prefix_gate"],
                "best_adaptive_prefix_gate_by_budget": summary["summary"]["best_adaptive_prefix_gate_by_budget"],
                "best_hash_control": summary["summary"]["best_hash_control"],
                "claim_status": summary["claim_status"],
                "full_pool": summary["summary"]["full_pool"],
                "full_pool_by_budget": summary["summary"]["full_pool_by_budget"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
