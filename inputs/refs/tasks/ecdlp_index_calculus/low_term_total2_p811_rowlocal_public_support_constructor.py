#!/usr/bin/env python3
"""P811 charged row-local public support constructor for the P804 signal."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P805_SCRIPT = TASK_DIR / "low_term_total2_p805_public_support_selector_pressure.py"
P806_SCRIPT = TASK_DIR / "low_term_total2_p806_public_feature_classifier.py"
P807_SCRIPT = TASK_DIR / "low_term_total2_p807_richer_public_feature_classifier.py"
P808_SCRIPT = TASK_DIR / "low_term_total2_p808_requested_support_invariant_miner.py"
P809_SCRIPT = TASK_DIR / "low_term_total2_p809_public_rank_proxy_audit.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p811_rowlocal_public_support_constructor_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p811_rowlocal_public_support_constructor.md"
SCHEMA = "ecdlp.low_term_total2_p811_rowlocal_public_support_constructor.v1"

REQUESTED = "requested_support_prehit"
ROWLOCAL_COUNT = "public_rowlocal_prehit_count"
ROWLOCAL_COUNT_FIRST = "public_rowlocal_prehit_count_then_first"
ROWLOCAL_FIRST = "public_rowlocal_first_seen"
ROWLOCAL_COUNT_XPROD = "public_rowlocal_prehit_count_xprod"
STATIC_XPROD = "public_static_sym_x_prod_low_control"
ROTATED = "rotated_support_prehit"
ALL_PAIR = "all_pair_first_hit_control"
PUBLIC_POLICIES = (
    ROWLOCAL_COUNT,
    ROWLOCAL_COUNT_FIRST,
    ROWLOCAL_FIRST,
    ROWLOCAL_COUNT_XPROD,
    STATIC_XPROD,
)
POLICY_NAMES = (REQUESTED, *PUBLIC_POLICIES, ROTATED, ALL_PAIR)


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


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in str(value))
    return "_".join(part for part in text.split("_") if part)


def seed_labels(count: int) -> list[str]:
    return [f"t{index:04d}" for index in range(int(count))]


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def canonical_support(support: tuple[int, int]) -> tuple[int, int]:
    left, right = int(support[0]), int(support[1])
    return (left, right) if left <= right else (right, left)


def support_mean(values: set[tuple[int, int]]) -> float:
    if not values:
        return 0.0
    return round(mean(abs(int(left) - int(right)) for left, right in values), 8)


def policy_kind(policy_name: str) -> str:
    if policy_name == REQUESTED:
        return "requested_support_pre_hit_constructor_positive_control"
    if policy_name == ROWLOCAL_COUNT:
        return "public_rowlocal_walk_prehit_count_selector"
    if policy_name == ROWLOCAL_COUNT_FIRST:
        return "public_rowlocal_walk_prehit_count_then_first_selector"
    if policy_name == ROWLOCAL_FIRST:
        return "public_rowlocal_walk_first_seen_selector"
    if policy_name == ROWLOCAL_COUNT_XPROD:
        return "public_rowlocal_walk_prehit_count_plus_static_geometry_selector"
    if policy_name == STATIC_XPROD:
        return "public_static_geometry_control"
    if policy_name == ROTATED:
        return "rotated_support_pre_hit_control"
    if policy_name == ALL_PAIR:
        return "all_pair_first_hit_control"
    return "unknown_policy"


def configure_p805(p805: Any) -> None:
    p805.POLICY_NAMES = POLICY_NAMES
    p805.PUBLIC_POLICIES = PUBLIC_POLICIES
    p805.policy_kind = policy_kind


def top_by_score(scores: dict[tuple[int, int], float], count: int) -> set[tuple[int, int]]:
    return {
        support
        for support, _score in sorted(scores.items(), key=lambda item: (-float(item[1]), item[0][0], item[0][1]))[
            : max(0, min(int(count), len(scores)))
        ]
    }


def rowlocal_public_scores(
    p746: Any,
    p801: Any,
    p809: Any,
    relprobe: Any,
    context: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[dict[str, dict[tuple[int, int], float]], dict[str, Any]]:
    verifier = context["verifier"]
    inv = context["inv"]
    ainvs = context["ainvs"]
    p = int(context["p"])
    order = int(context["order"])
    target = str(context["target"])
    factor_base = context["factor_base"]
    all_pairs = [canonical_support(support) for support in context["all_pairs"]]
    point_to_supports: dict[Any, list[tuple[int, int]]] = defaultdict(list)
    for support in all_pairs:
        point_to_supports[p801.support_sum(verifier, factor_base, support, ainvs, p)].append(support)

    hit_counts = Counter()
    first_seen: dict[tuple[int, int], int] = {}
    trial_budget = int(args.proxy_trial_budget)
    proxy_seed_count = int(args.proxy_seed_count)
    for seed_index in range(proxy_seed_count):
        seed_label = f"p{seed_index:04d}"
        full_seed = (
            f"ecdlp-p811-{context['namespace']}-{slug(target)}:"
            f"proxy:{seed_label}:fb{context['factor_base_size']}:w2:{args.walk_mode}"
        )
        challenge, _secret = relprobe.make_challenge(verifier, inv, ainvs, full_seed, context["factor_base_size"])
        base = verifier.point_from_json(challenge["base"])
        public = verifier.point_from_json(challenge["public"])
        walk = p746.walk_schedule(verifier, str(args.walk_mode), base, public, ainvs, p)
        a, b = p746.deterministic_start(int(order), full_seed, str(args.walk_mode))
        lhs = verifier.add_points(verifier.mul_point(a, base, ainvs, p), verifier.mul_point(b, public, ainvs, p), ainvs, p)
        for trial in range(1, trial_budget + 1):
            stamp = seed_index * trial_budget + trial
            for support in point_to_supports.get(lhs) or []:
                hit_counts[support] += 1
                first_seen.setdefault(support, stamp)
            if trial == trial_budget:
                break
            delta = p746.select_delta(walk, full_seed, trial, a, b)
            a = (a + int(delta["da"])) % int(order)
            b = (b + int(delta["db"])) % int(order)
            lhs = verifier.add_points(lhs, delta["delta"], ainvs, p)

    missing_seen = (proxy_seed_count * trial_budget) + 1
    static_scores = p809.public_static_scores(p801, context)
    xprod_scores = static_scores["static_sym_x_prod_low"]
    scores = {
        ROWLOCAL_COUNT: {},
        ROWLOCAL_COUNT_FIRST: {},
        ROWLOCAL_FIRST: {},
        ROWLOCAL_COUNT_XPROD: {},
        STATIC_XPROD: {},
    }
    for support in all_pairs:
        count = int(hit_counts[support])
        first = int(first_seen.get(support, missing_seen))
        scores[ROWLOCAL_COUNT][support] = float(count)
        scores[ROWLOCAL_COUNT_FIRST][support] = float((count * missing_seen) - first)
        scores[ROWLOCAL_FIRST][support] = -float(first)
        scores[ROWLOCAL_COUNT_XPROD][support] = float((count * missing_seen) - first) + (
            float(xprod_scores[support]) / float(max(1, p + 1))
        )
        scores[STATIC_XPROD][support] = float(xprod_scores[support])

    nonzero_counts = [int(value) for value in hit_counts.values() if int(value) > 0]
    diagnostics = {
        "all_pair_count": len(all_pairs),
        "max_public_prehit_count": max(nonzero_counts, default=0),
        "nonzero_public_prehit_supports": len(nonzero_counts),
        "proxy_seed_count": proxy_seed_count,
        "proxy_trial_budget": trial_budget,
        "proxy_total_walk_steps": proxy_seed_count * trial_budget,
        "proxy_unique_hit_points": len(hit_counts),
    }
    return scores, diagnostics


def support_overlap_stats(
    supports_by_policy: dict[tuple[int, str], set[tuple[int, int]]],
    support_budgets: list[int],
) -> list[dict[str, Any]]:
    rows = []
    for budget in support_budgets:
        requested = supports_by_policy[(int(budget), REQUESTED)]
        for policy_name in POLICY_NAMES:
            selected = supports_by_policy[(int(budget), policy_name)]
            overlap = len(selected & requested)
            union = len(selected | requested)
            rows.append(
                {
                    "jaccard_with_requested": ratio(overlap, union),
                    "mean_index_span": support_mean(selected),
                    "overlap_count": overlap,
                    "overlap_over_requested": ratio(overlap, len(requested)),
                    "policy": policy_name,
                    "requested_count": len(requested),
                    "selected_count": len(selected),
                    "support_budget": int(budget),
                }
            )
    return rows


def build_support_sets_for_context(
    p801: Any,
    p809: Any,
    p746: Any,
    relprobe: Any,
    context: dict[str, Any],
    support_budgets: list[int],
    args: argparse.Namespace,
) -> tuple[dict[tuple[int, str], set[tuple[int, int]]], list[dict[str, Any]], dict[str, Any]]:
    scores_by_policy, diagnostics = rowlocal_public_scores(p746, p801, p809, relprobe, context, args)
    supports_by_policy: dict[tuple[int, str], set[tuple[int, int]]] = {}
    all_pairs = p801.all_support_pairs(len(context["factor_base"]))
    for budget in support_budgets:
        requested = set(context["requested_by_budget"][int(budget)])
        supports_by_policy[(int(budget), REQUESTED)] = requested
        supports_by_policy[(int(budget), ROTATED)] = p801.rotated_supports_for(requested, len(context["factor_base"]))
        supports_by_policy[(int(budget), ALL_PAIR)] = all_pairs
        for policy_name in PUBLIC_POLICIES:
            supports_by_policy[(int(budget), policy_name)] = top_by_score(scores_by_policy[policy_name], len(requested))
    return supports_by_policy, support_overlap_stats(supports_by_policy, support_budgets), diagnostics


def collect_context_rows(
    p805: Any,
    p801: Any,
    p746: Any,
    p748: Any,
    relprobe: Any,
    context: dict[str, Any],
    supports_by_policy: dict[tuple[int, str], set[tuple[int, int]]],
    support_budgets: list[int],
    trial_budgets: list[int],
    args: argparse.Namespace,
) -> tuple[dict[tuple[int, int, str], list[dict[str, Any]]], dict[tuple[int, str], dict[str, int]]]:
    verifier = context["verifier"]
    ainvs = context["ainvs"]
    p = int(context["p"])
    order = int(context["order"])
    factor_base = context["factor_base"]
    point_policy, support_policy_stats = p801.build_point_policy_map(verifier, factor_base, ainvs, p, supports_by_policy)
    rows_by_grid = {
        (int(support_budget), int(trial_budget), policy_name): []
        for support_budget in support_budgets
        for trial_budget in trial_budgets
        for policy_name in POLICY_NAMES
    }
    for seed_label in seed_labels(int(args.scan_seed_count)):
        full_seed = (
            f"ecdlp-p811-{context['namespace']}-{slug(context['target'])}:"
            f"{seed_label}:fb{context['factor_base_size']}:w2:{args.walk_mode}"
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
            seed_label,
            full_seed,
            support_budgets,
            trial_budgets,
            point_policy,
            support_policy_stats,
            args,
        )
        for grid_key, row in rows.items():
            rows_by_grid[grid_key].append(row)
    return rows_by_grid, support_policy_stats


def compact_item(item: dict[str, Any] | None, model: str = "target_once_setup") -> dict[str, Any] | None:
    if item is None:
        return None
    cost_model = item["cost_models"][model]
    return {
        "cost": cost_model["cost"],
        "cost_over_recovered_rho": cost_model["cost_over_recovered_rho"],
        "generated_row_count": item["generated_row_count"],
        "hit_row_count": item["hit_row_count"],
        "hit_row_rate_over_generated": item["hit_row_rate_over_generated"],
        "max_control_recovered_row_count": item["max_control_recovered_row_count"],
        "policy": item["policy"]["name"],
        "recovered_rho_baseline": item["recovered_rho_baseline"],
        "recovered_row_count": item["recovered_row_count"],
        "support_budget": item["support_budget"],
        "targeted_support_count": item["targeted_support_count"],
        "trial_budget": item["trial_budget"],
    }


def best_by_model(items: list[dict[str, Any]], policy_names: set[str], model: str) -> dict[str, Any] | None:
    viable = [
        item
        for item in items
        if item["policy"]["name"] in policy_names
        and item["cost_models"][model]["cost_over_recovered_rho"] is not None
    ]
    if not viable:
        return None
    return min(viable, key=lambda row: row["cost_models"][model]["cost_over_recovered_rho"])


def peer_items(items: list[dict[str, Any]], support_budget: int, trial_budget: int) -> dict[str, dict[str, Any]]:
    return {
        item["policy"]["name"]: item
        for item in items
        if int(item["support_budget"]) == int(support_budget)
        and int(item["trial_budget"]) == int(trial_budget)
    }


def policy_rank(items: list[dict[str, Any]], support_budget: int, trial_budget: int, policies: tuple[str, ...]) -> list[dict[str, Any]]:
    peers = peer_items(items, support_budget, trial_budget)
    ranked = sorted(
        [peers[name] for name in policies if name in peers],
        key=lambda item: (-int(item["recovered_row_count"]), item["cost_models"]["target_once_setup"]["cost_over_recovered_rho"] or 10**18),
    )
    return [compact_item(item) for item in ranked]


def determine_policy_claim(item: dict[str, Any], peers: dict[str, dict[str, Any]]) -> str:
    policy_name = item["policy"]["name"]
    recovered = int(item["recovered_row_count"])
    requested = int((peers.get(REQUESTED) or {}).get("recovered_row_count") or 0)
    rotated = int((peers.get(ROTATED) or {}).get("recovered_row_count") or 0)
    all_pair = int((peers.get(ALL_PAIR) or {}).get("recovered_row_count") or 0)
    max_line_control = int(item["max_control_recovered_row_count"])
    target_once = item["cost_models"]["target_once_setup"]["cost_over_recovered_rho"]
    if recovered <= max_line_control:
        return "does_not_beat_line_controls"
    if policy_name == REQUESTED and target_once is not None and target_once < 1.0:
        return "requested_support_target_once_below_rho"
    if policy_name in PUBLIC_POLICIES and recovered > max(rotated, all_pair, max_line_control):
        if target_once is not None and target_once < 1.0 and requested and recovered >= int(0.8 * requested):
            return "public_rowlocal_constructor_near_requested_below_rho"
        return "public_rowlocal_constructor_beats_generic_controls"
    if policy_name in {ROTATED, ALL_PAIR}:
        return "generic_control_boundary"
    return "support_constructor_boundary"


def determine_claim(best_requested: dict[str, Any] | None, best_public: dict[str, Any] | None, grid_results: list[dict[str, Any]]) -> str:
    if best_requested is None or int(best_requested["recovered_row_count"]) == 0:
        return "NEGATIVE_RESULT_P811_REQUESTED_SUPPORT_SIGNAL_LOST"
    if best_public is None:
        return "NEGATIVE_RESULT_P811_NO_PUBLIC_ROWLOCAL_CANDIDATES"
    peers = peer_items(grid_results, int(best_public["support_budget"]), int(best_public["trial_budget"]))
    max_generic = max(
        int((peers.get(ROTATED) or {}).get("recovered_row_count") or 0),
        int((peers.get(ALL_PAIR) or {}).get("recovered_row_count") or 0),
    )
    public_ratio = best_public["cost_models"]["target_once_setup"]["cost_over_recovered_rho"]
    requested_recovered = int((peers.get(REQUESTED) or {}).get("recovered_row_count") or best_requested["recovered_row_count"])
    public_recovered = int(best_public["recovered_row_count"])
    if public_ratio is not None and public_ratio < 1.0 and requested_recovered and public_recovered >= int(0.8 * requested_recovered):
        return "P811_PUBLIC_ROWLOCAL_CONSTRUCTOR_NEAR_REQUESTED_BELOW_RHO"
    if public_recovered > max_generic:
        return "P811_PUBLIC_ROWLOCAL_CONSTRUCTOR_BEATS_GENERIC_CONTROLS"
    return "NEGATIVE_RESULT_P811_PUBLIC_ROWLOCAL_CONSTRUCTORS_FAIL_RECOVERY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    if int(args.width) != 2:
        raise ValueError("P811 validates width-2 support pairs; use --width 2")
    p805 = load_module("ecdlp_p805_for_p811", P805_SCRIPT)
    p806 = load_module("ecdlp_p806_for_p811", P806_SCRIPT)
    p807 = load_module("ecdlp_p807_for_p811", P807_SCRIPT)
    p808 = load_module("ecdlp_p808_for_p811", P808_SCRIPT)
    p809 = load_module("ecdlp_p809_for_p811", P809_SCRIPT)
    p807.configure_p807(p806)
    configure_p805(p805)

    modules = p808.load_research_stack(p806)
    p801 = modules["p801"]
    p803 = load_module("ecdlp_p803_for_p811", p805.P803_SCRIPT)
    p800 = p801.load_module("ecdlp_p800_for_p811", p801.P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p811", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p811", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p811", p798.P797_SCRIPT)
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
    support_budgets = csv_ints(args.support_budgets)
    trial_budgets = csv_ints(args.trial_budgets)
    namespaces = csv_strings(args.constructor_namespaces)

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
    trained_by_group_support = {
        group_key: {
            int(budget): p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], int(budget))
            for budget in support_budgets
        }
        for group_key in required
    }

    scan_bank = {}
    support_stats = []
    proxy_diagnostics = []
    for namespace in namespaces:
        for group_key in required:
            print(f"building P811 rowlocal context namespace={namespace} group={group_key}", flush=True)
            context = p806.build_public_context(
                p801,
                p746,
                relprobe,
                base_groups[group_key],
                trained_by_group_support[group_key],
                support_budgets,
                namespace,
                args,
            )
            supports_by_policy, support_rows, diagnostics = build_support_sets_for_context(
                p801,
                p809,
                p746,
                relprobe,
                context,
                support_budgets,
                args,
            )
            for row in support_rows:
                support_stats.append({**row, "group_key": group_key, "namespace": namespace})
            proxy_diagnostics.append({**diagnostics, "group_key": group_key, "namespace": namespace, "target": str(context["target"])})
            print(f"P811 scanning namespace={namespace} group={group_key} rows={args.scan_seed_count}", flush=True)
            rows_by_grid, support_policy_stats = collect_context_rows(
                p805,
                p801,
                p746,
                p748,
                relprobe,
                context,
                supports_by_policy,
                support_budgets,
                trial_budgets,
                args,
            )
            scan_bank[(namespace, group_key)] = {
                "order": context["order"],
                "rows_by_grid": rows_by_grid,
                "support_policy_stats": support_policy_stats,
            }

    grid_results = []
    for support_budget in support_budgets:
        for trial_budget in trial_budgets:
            print(f"scoring support_budget={support_budget} trial_budget={trial_budget}", flush=True)
            policy_items: dict[str, list[dict[str, Any]]] = {name: [] for name in POLICY_NAMES}
            for namespace in namespaces:
                for group_key in required:
                    bank = scan_bank[(namespace, group_key)]
                    for policy_name in POLICY_NAMES:
                        support_key = (int(support_budget), policy_name)
                        grid_key = (int(support_budget), int(trial_budget), policy_name)
                        item = p805.evaluate_policy(
                            p797,
                            p793,
                            p792,
                            p789,
                            train_prepared[group_key],
                            trained_by_group_support[group_key][int(support_budget)],
                            bank["rows_by_grid"][grid_key],
                            int(bank["order"]),
                            str(base_groups[group_key]["target"]),
                            policy_name,
                            bank["support_policy_stats"][support_key],
                            args,
                        )
                        item["namespace"] = namespace
                        item["group_key"] = group_key
                        policy_items[policy_name].append(item)
            for policy_name in POLICY_NAMES:
                item = p805.aggregate_policy_results(policy_items[policy_name], policy_name)
                item["support_budget"] = int(support_budget)
                item["trial_budget"] = int(trial_budget)
                grid_results.append(p805.enrich_grid_item(p803, item, int(args.field_weight)))

    for support_budget in support_budgets:
        for trial_budget in trial_budgets:
            peers = peer_items(grid_results, int(support_budget), int(trial_budget))
            for item in peers.values():
                item["policy_claim"] = determine_policy_claim(item, peers)

    best_requested = best_by_model(grid_results, {REQUESTED}, "target_once_setup")
    best_public = best_by_model(grid_results, set(PUBLIC_POLICIES), "target_once_setup")
    requested_grid_public_rank = []
    if best_requested is not None:
        requested_grid_public_rank = policy_rank(
            grid_results,
            int(best_requested["support_budget"]),
            int(best_requested["trial_budget"]),
            PUBLIC_POLICIES,
        )
    best_public_grid_rank = []
    if best_public is not None:
        best_public_grid_rank = policy_rank(
            grid_results,
            int(best_public["support_budget"]),
            int(best_public["trial_budget"]),
            (*PUBLIC_POLICIES, ROTATED, ALL_PAIR),
        )
    support_overlap_by_policy = []
    for policy_name in POLICY_NAMES:
        rows = [row for row in support_stats if row["policy"] == policy_name]
        support_overlap_by_policy.append(
            {
                "jaccard_with_requested": stat([float(row["jaccard_with_requested"] or 0.0) for row in rows]),
                "mean_index_span": stat([float(row["mean_index_span"]) for row in rows]),
                "overlap_over_requested": stat([float(row["overlap_over_requested"] or 0.0) for row in rows]),
                "policy": policy_name,
            }
        )

    summary = {
        "best_public_by_model": {
            "conservative_repeated": compact_item(best_by_model(grid_results, set(PUBLIC_POLICIES), "conservative_repeated"), "conservative_repeated"),
            "online_after_setup": compact_item(best_by_model(grid_results, set(PUBLIC_POLICIES), "online_after_setup"), "online_after_setup"),
            "target_once_setup": compact_item(best_public, "target_once_setup"),
        },
        "best_public_grid_rank": best_public_grid_rank,
        "best_requested_by_model": {
            "conservative_repeated": compact_item(best_by_model(grid_results, {REQUESTED}, "conservative_repeated"), "conservative_repeated"),
            "online_after_setup": compact_item(best_by_model(grid_results, {REQUESTED}, "online_after_setup"), "online_after_setup"),
            "target_once_setup": compact_item(best_requested, "target_once_setup"),
        },
        "constructor_namespaces": namespaces,
        "grid_results": grid_results,
        "proxy_diagnostics": proxy_diagnostics,
        "requested_grid_public_rank": requested_grid_public_rank,
        "scan_seed_count": int(args.scan_seed_count),
        "support_budgets": support_budgets,
        "support_overlap_by_policy": support_overlap_by_policy,
        "support_overlap_rows": support_stats,
        "target_groups": required,
        "train_seed_namespace": args.train_seed_namespace,
        "trial_budgets": trial_budgets,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p805_script": str(P805_SCRIPT),
            "p806_script": str(P806_SCRIPT),
            "p807_script": str(P807_SCRIPT),
            "p808_script": str(P808_SCRIPT),
            "p809_script": str(P809_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(best_requested, best_public, grid_results),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC ROW-LOCAL CONSTRUCTION: public selectors use only public walk pre-hit counts, first-seen order, and public factor-base geometry.",
            "CHARGED ROW RECOVERY: P811 evaluates recovered rows and P803/P805 target-once cost models, not only support-rank overlap.",
            "POSITIVE CONTROL: requested calibration-derived supports are retained to verify that the P804 target-once signal is still present.",
            "MODEL-BOUND TARGET-ONCE SETUP: support setup is charged once per target across fresh namespaces.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p811_rowlocal_public_support_constructor",
        "parameters": {
            "constructor_namespaces": namespaces,
            "control_count": int(args.control_count),
            "feature_bins": int(args.feature_bins),
            "field_weight": int(args.field_weight),
            "max_relations": int(args.max_relations),
            "max_subsets": int(args.max_subsets),
            "min_line_rows": int(args.min_line_rows),
            "policies": list(POLICY_NAMES),
            "proxy_seed_count": int(args.proxy_seed_count),
            "proxy_trial_budget": int(args.proxy_trial_budget),
            "row_policy": args.row_policy,
            "scan_seed_count": int(args.scan_seed_count),
            "sparse_policies": args.sparse_policies,
            "support_budgets": support_budgets,
            "train_replicas": int(args.train_replicas),
            "train_seed_namespace": args.train_seed_namespace,
            "trial_budgets": trial_budgets,
            "walk_mode": args.walk_mode,
            "width": int(args.width),
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def compact_grid_result(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "cost_models": item["cost_models"],
        "generated_row_count": item["generated_row_count"],
        "hit_row_count": item["hit_row_count"],
        "hit_row_rate_over_generated": item["hit_row_rate_over_generated"],
        "max_control_recovered_row_count": item["max_control_recovered_row_count"],
        "policy": item["policy"],
        "policy_claim": item.get("policy_claim"),
        "recovered_rho_baseline": item["recovered_rho_baseline"],
        "recovered_row_count": item["recovered_row_count"],
        "support_budget": item["support_budget"],
        "targeted_support_count": item["targeted_support_count"],
        "trial_budget": item["trial_budget"],
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **payload["summary"],
            "grid_results": [compact_grid_result(item) for item in payload["summary"]["grid_results"]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default="prehitpair-p811-rowlocal-v17,prehitpair-p811-rowlocal-v18,prehitpair-p811-rowlocal-v19")
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--trial-budgets", default="256")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--scan-seed-count", type=int, default=128)
    parser.add_argument("--proxy-seed-count", type=int, default=32)
    parser.add_argument("--proxy-trial-budget", type=int, default=64)
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
                "best_public_by_model": summary["summary"]["best_public_by_model"],
                "best_requested_by_model": summary["summary"]["best_requested_by_model"],
                "claim_status": summary["claim_status"],
                "requested_grid_public_rank": summary["summary"]["requested_grid_public_rank"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
