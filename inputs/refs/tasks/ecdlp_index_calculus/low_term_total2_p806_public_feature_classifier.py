#!/usr/bin/env python3
"""P806 public-feature support-pair classifier for the P804/P805 signal."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P801_SCRIPT = TASK_DIR / "low_term_total2_p801_pre_hit_support_pair_constructor.py"
P803_SCRIPT = TASK_DIR / "low_term_total2_p803_prehit_support_setup_amortization.py"
P805_SCRIPT = TASK_DIR / "low_term_total2_p805_public_support_selector_pressure.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p806_public_feature_classifier_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p806_public_feature_classifier.md"
SCHEMA = "ecdlp.low_term_total2_p806_public_feature_classifier.v1"

REQUESTED = "requested_support_prehit"
CROSS_TARGET = "public_logodds_cross_target"
SAME_TARGET_UPPER = "public_logodds_same_target_upper"
ROTATED = "rotated_support_prehit"
ALL_PAIR = "all_pair_first_hit_control"
PUBLIC_POLICIES = (CROSS_TARGET, SAME_TARGET_UPPER)
POLICY_NAMES = (REQUESTED, CROSS_TARGET, SAME_TARGET_UPPER, ROTATED, ALL_PAIR)


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


def policy_kind(policy_name: str) -> str:
    if policy_name == REQUESTED:
        return "requested_support_pre_hit_constructor"
    if policy_name == CROSS_TARGET:
        return "cross_target_public_feature_logodds_selector"
    if policy_name == SAME_TARGET_UPPER:
        return "same_target_public_feature_logodds_upper_bound"
    if policy_name == ROTATED:
        return "rotated_support_pre_hit_control"
    if policy_name == ALL_PAIR:
        return "all_pair_first_hit_control"
    return "unknown_policy"


def configure_p805(p805: Any) -> None:
    p805.POLICY_NAMES = POLICY_NAMES
    p805.PUBLIC_POLICIES = PUBLIC_POLICIES
    p805.policy_kind = policy_kind


def point_x(point: Any, p: int) -> int:
    if point is None:
        return int(p)
    return int(point[0]) % int(p)


def bounded_bin(value: int, modulus: int, bins: int) -> int:
    if modulus <= 0:
        return 0
    return max(0, min(int(bins) - 1, int(value) * int(bins) // int(modulus)))


def index_bin(value: int, size: int, bins: int) -> int:
    return bounded_bin(int(value), max(1, int(size)), int(bins))


def canonical_support(support: tuple[int, int]) -> tuple[int, int]:
    left, right = int(support[0]), int(support[1])
    return (left, right) if left <= right else (right, left)


def support_mean(values: set[tuple[int, int]]) -> float:
    if not values:
        return 0.0
    return round(mean(abs(int(left) - int(right)) for left, right in values), 8)


def public_features(
    p801: Any,
    verifier: Any,
    factor_base: list[Any],
    ainvs: list[int],
    p: int,
    support: tuple[int, int],
    bins: int,
    pair_sum_x_cache: dict[tuple[int, int], int],
) -> tuple[str, ...]:
    left, right = canonical_support(support)
    size = len(factor_base)
    lx = point_x(factor_base[left], p)
    rx = point_x(factor_base[right], p)
    if support not in pair_sum_x_cache:
        pair_sum_x_cache[support] = point_x(p801.support_sum(verifier, factor_base, support, ainvs, p), p)
    pair_x = pair_sum_x_cache[support]
    span = abs(left - right)
    index_sum = left + right
    x_gap = abs(lx - rx)
    return (
        f"left_bin={index_bin(left, size, bins)}",
        f"right_bin={index_bin(right, size, bins)}",
        f"span_bin={index_bin(span, size, bins)}",
        f"sum_bin={index_bin(index_sum, max(1, 2 * size), bins)}",
        f"left_x_bin={bounded_bin(lx, p, bins)}",
        f"right_x_bin={bounded_bin(rx, p, bins)}",
        f"min_x_bin={bounded_bin(min(lx, rx), p, bins)}",
        f"max_x_bin={bounded_bin(max(lx, rx), p, bins)}",
        f"x_gap_bin={bounded_bin(x_gap, p, bins)}",
        f"pair_x_bin={bounded_bin(pair_x, p, bins)}",
        f"same_x={int(lx == rx)}",
        f"index_parity={left % 2}:{right % 2}",
        f"span_mod4={span % 4}",
        f"sum_mod8={index_sum % 8}",
    )


def requested_supports(
    p801: Any,
    trained_by_budget: dict[int, dict[tuple[int, int, int, int], dict[str, Any]]],
    budget: int,
) -> set[tuple[int, int]]:
    return {
        p801.canonical_support((int(key[0]), int(key[1])))
        for key in trained_by_budget[int(budget)]
    }


def build_public_context(
    p801: Any,
    p746: Any,
    relprobe: Any,
    base_item: dict[str, Any],
    trained_by_budget: dict[int, dict[tuple[int, int, int, int], dict[str, Any]]],
    support_budgets: list[int],
    namespace: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    verifier, record, inv = p746.load_target(relprobe, str(base_item["target"]))
    ainvs = record["ainvs"]
    p = int(inv["p"])
    order = int(inv["base_order"])
    factor_base_size = int(base_item["factor_base_size"])
    sample_seed = (
        f"ecdlp-p806-{namespace}-{slug(base_item['target'])}:sample:"
        f"fb{factor_base_size}:w2:{args.walk_mode}"
    )
    sample_challenge, _sample_secret = relprobe.make_challenge(verifier, inv, ainvs, sample_seed, factor_base_size)
    factor_base = [
        verifier.point_from_json(point)
        for point in sample_challenge["factor_base"][: max(1, min(factor_base_size, len(sample_challenge["factor_base"])))]
    ]
    all_pairs = sorted(p801.all_support_pairs(len(factor_base)))
    pair_sum_x_cache: dict[tuple[int, int], int] = {}
    features_by_support = {
        support: public_features(
            p801,
            verifier,
            factor_base,
            ainvs,
            p,
            support,
            int(args.feature_bins),
            pair_sum_x_cache,
        )
        for support in all_pairs
    }
    return {
        "ainvs": ainvs,
        "all_pairs": all_pairs,
        "base_item": base_item,
        "factor_base": factor_base,
        "factor_base_size": factor_base_size,
        "features_by_support": features_by_support,
        "group_key": str(base_item["group_key"]),
        "inv": inv,
        "namespace": namespace,
        "order": order,
        "p": p,
        "requested_by_budget": {
            int(budget): requested_supports(p801, trained_by_budget, int(budget))
            for budget in support_budgets
        },
        "target": str(base_item["target"]),
        "verifier": verifier,
    }


def train_logodds_model(contexts: list[dict[str, Any]], budget: int, smoothing: float) -> dict[str, Any]:
    feature_counts: dict[str, Counter] = defaultdict(Counter)
    totals = Counter()
    for context in contexts:
        requested = context["requested_by_budget"][int(budget)]
        for support in context["all_pairs"]:
            label = int(support in requested)
            totals["positive" if label else "negative"] += 1
            for feature in context["features_by_support"][support]:
                feature_counts[feature]["positive" if label else "negative"] += 1
    positive = int(totals["positive"])
    negative = int(totals["negative"])
    base = math.log((positive + smoothing) / (negative + smoothing))
    weights = {
        feature: math.log((counts["positive"] + smoothing) / (counts["negative"] + smoothing))
        for feature, counts in feature_counts.items()
    }
    ranked = sorted(weights.items(), key=lambda item: item[1])
    return {
        "base_log_odds": base,
        "feature_count": len(weights),
        "negative_examples": negative,
        "positive_examples": positive,
        "smoothing": float(smoothing),
        "top_negative_features": [{"feature": key, "weight": round(value, 8)} for key, value in ranked[:8]],
        "top_positive_features": [{"feature": key, "weight": round(value, 8)} for key, value in reversed(ranked[-8:])],
        "weights": weights,
    }


def score_support(context: dict[str, Any], support: tuple[int, int], model: dict[str, Any]) -> float:
    score = float(model["base_log_odds"])
    weights = model["weights"]
    for feature in context["features_by_support"][support]:
        score += float(weights.get(feature, 0.0))
    return score


def select_model_supports(context: dict[str, Any], model: dict[str, Any], count: int) -> set[tuple[int, int]]:
    ranked = sorted(
        context["all_pairs"],
        key=lambda support: (-score_support(context, support, model), support[0], support[1]),
    )
    return set(ranked[: max(0, min(int(count), len(ranked)))])


def support_overlap_stats(
    supports_by_budget_policy: dict[tuple[int, str], set[tuple[int, int]]],
    support_budgets: list[int],
) -> list[dict[str, Any]]:
    rows = []
    for budget in support_budgets:
        requested = supports_by_budget_policy[(int(budget), REQUESTED)]
        for policy_name in POLICY_NAMES:
            selected = supports_by_budget_policy[(int(budget), policy_name)]
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
    context: dict[str, Any],
    all_contexts: dict[tuple[str, str], dict[str, Any]],
    support_budgets: list[int],
    args: argparse.Namespace,
) -> tuple[dict[tuple[int, str], set[tuple[int, int]]], list[dict[str, Any]], list[dict[str, Any]]]:
    supports_by_policy: dict[tuple[int, str], set[tuple[int, int]]] = {}
    model_rows = []
    for budget in support_budgets:
        requested = context["requested_by_budget"][int(budget)]
        same_model = train_logodds_model([context], int(budget), float(args.logodds_smoothing))
        cross_contexts = [
            other
            for (namespace, group_key), other in sorted(all_contexts.items())
            if namespace == context["namespace"] and group_key != context["group_key"]
        ]
        cross_model = train_logodds_model(cross_contexts, int(budget), float(args.logodds_smoothing))
        cross_supports = select_model_supports(context, cross_model, len(requested))
        same_supports = select_model_supports(context, same_model, len(requested))
        supports_by_policy[(int(budget), REQUESTED)] = requested
        supports_by_policy[(int(budget), CROSS_TARGET)] = cross_supports
        supports_by_policy[(int(budget), SAME_TARGET_UPPER)] = same_supports
        supports_by_policy[(int(budget), ROTATED)] = p801.rotated_supports_for(requested, len(context["factor_base"]))
        supports_by_policy[(int(budget), ALL_PAIR)] = p801.all_support_pairs(len(context["factor_base"]))
        model_rows.extend(
            [
                {
                    "group_key": context["group_key"],
                    "model": CROSS_TARGET,
                    "namespace": context["namespace"],
                    "support_budget": int(budget),
                    **{key: value for key, value in cross_model.items() if key != "weights"},
                },
                {
                    "group_key": context["group_key"],
                    "model": SAME_TARGET_UPPER,
                    "namespace": context["namespace"],
                    "support_budget": int(budget),
                    **{key: value for key, value in same_model.items() if key != "weights"},
                },
            ]
        )
    return supports_by_policy, support_overlap_stats(supports_by_policy, support_budgets), model_rows


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
            f"ecdlp-p806-{context['namespace']}-{slug(context['target'])}:"
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
    max_line_control = int(item["max_control_recovered_row_count"])
    requested = int((peers.get(REQUESTED) or {}).get("recovered_row_count") or 0)
    target_once = item["cost_models"]["target_once_setup"]["cost_over_recovered_rho"]
    if recovered <= max_line_control:
        return "does_not_beat_line_controls"
    if policy_name == REQUESTED and target_once is not None and target_once < 1.0:
        return "requested_support_target_once_below_rho"
    if policy_name == CROSS_TARGET and recovered >= requested and target_once is not None and target_once < 1.0:
        return "cross_target_public_feature_matches_requested_below_rho"
    if policy_name == SAME_TARGET_UPPER and recovered >= requested and target_once is not None and target_once < 1.0:
        return "same_target_public_feature_upper_bound_matches_requested"
    if policy_name in PUBLIC_POLICIES:
        return "public_feature_classifier_boundary"
    if policy_name in {ROTATED, ALL_PAIR}:
        return "generic_control_boundary"
    return "support_selector_boundary"


def determine_claim(best_requested: dict[str, Any] | None, best_cross: dict[str, Any] | None, best_upper: dict[str, Any] | None) -> str:
    if best_requested is None or int(best_requested["recovered_row_count"]) == 0:
        return "NEGATIVE_RESULT_P806_REQUESTED_SUPPORT_SIGNAL_LOST"
    requested_recovered = int(best_requested["recovered_row_count"])
    if best_cross is not None:
        cross_ratio = best_cross["cost_models"]["target_once_setup"]["cost_over_recovered_rho"]
        if cross_ratio is not None and cross_ratio < 1.0 and int(best_cross["recovered_row_count"]) >= requested_recovered:
            return "P806_CROSS_TARGET_PUBLIC_FEATURE_CLASSIFIER_MATCHES_REQUESTED"
    if best_upper is not None:
        upper_ratio = best_upper["cost_models"]["target_once_setup"]["cost_over_recovered_rho"]
        if upper_ratio is not None and upper_ratio < 1.0 and int(best_upper["recovered_row_count"]) >= requested_recovered:
            return "P806_SAME_TARGET_PUBLIC_FEATURE_UPPER_BOUND_ONLY"
    return "P806_PUBLIC_FEATURE_CLASSIFIER_FAILS_REQUESTED_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    if int(args.width) != 2:
        raise ValueError("P806 validates width-2 support pairs; use --width 2")
    p801 = load_module("ecdlp_p801_for_p806", P801_SCRIPT)
    p803 = load_module("ecdlp_p803_for_p806", P803_SCRIPT)
    p805 = load_module("ecdlp_p805_for_p806", P805_SCRIPT)
    configure_p805(p805)

    p800 = p801.load_module("ecdlp_p800_for_p806", p801.P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p806", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p806", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p806", p798.P797_SCRIPT)
    p796 = p797.load_module("ecdlp_p796_for_p806", p797.P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p806", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p806", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p806", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p806", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p806", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p806", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p806", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p806", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p806", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p806", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p806", p782.P780_SCRIPT)
    stack = p780.load_stack()
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
    print(f"preparing train namespace {args.train_seed_namespace}", flush=True)
    train_prepared = {
        key: p794.prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], train_args)
        for key in required
    }
    trained_by_group_support = {
        group_key: {
            int(budget): p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], int(budget))
            for budget in support_budgets
        }
        for group_key in required
    }

    contexts = {}
    for namespace in namespaces:
        for group_key in required:
            contexts[(namespace, group_key)] = build_public_context(
                p801,
                p746,
                relprobe,
                base_groups[group_key],
                trained_by_group_support[group_key],
                support_budgets,
                namespace,
                args,
            )

    scan_bank = {}
    support_stats = []
    model_stats = []
    for namespace in namespaces:
        for group_key in required:
            context = contexts[(namespace, group_key)]
            supports_by_policy, support_rows, model_rows = build_support_sets_for_context(
                p801,
                context,
                contexts,
                support_budgets,
                args,
            )
            for row in support_rows:
                support_stats.append({**row, "group_key": group_key, "namespace": namespace})
            model_stats.extend(model_rows)
            print(f"classifier scanning namespace={namespace} group={group_key} rows={args.scan_seed_count}", flush=True)
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
            policy_results = [p805.aggregate_policy_results(policy_items[policy_name], policy_name) for policy_name in POLICY_NAMES]
            for item in policy_results:
                item["support_budget"] = int(support_budget)
                item["trial_budget"] = int(trial_budget)
                grid_results.append(p805.enrich_grid_item(p803, item, int(args.field_weight)))

    for support_budget in support_budgets:
        for trial_budget in trial_budgets:
            peers = peer_items(grid_results, int(support_budget), int(trial_budget))
            for item in peers.values():
                item["policy_claim"] = determine_policy_claim(item, peers)

    best_requested = best_by_model(grid_results, {REQUESTED}, "target_once_setup")
    best_cross = best_by_model(grid_results, {CROSS_TARGET}, "target_once_setup")
    best_upper = best_by_model(grid_results, {SAME_TARGET_UPPER}, "target_once_setup")
    requested_grid_public_rank = []
    if best_requested is not None:
        requested_grid_public_rank = policy_rank(
            grid_results,
            int(best_requested["support_budget"]),
            int(best_requested["trial_budget"]),
            PUBLIC_POLICIES,
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
        "best_cross_target_by_model": {
            "conservative_repeated": compact_item(best_by_model(grid_results, {CROSS_TARGET}, "conservative_repeated"), "conservative_repeated"),
            "online_after_setup": compact_item(best_by_model(grid_results, {CROSS_TARGET}, "online_after_setup"), "online_after_setup"),
            "target_once_setup": compact_item(best_cross, "target_once_setup"),
        },
        "best_requested_by_model": {
            "conservative_repeated": compact_item(best_by_model(grid_results, {REQUESTED}, "conservative_repeated"), "conservative_repeated"),
            "online_after_setup": compact_item(best_by_model(grid_results, {REQUESTED}, "online_after_setup"), "online_after_setup"),
            "target_once_setup": compact_item(best_requested, "target_once_setup"),
        },
        "best_same_target_upper_by_model": {
            "conservative_repeated": compact_item(best_by_model(grid_results, {SAME_TARGET_UPPER}, "conservative_repeated"), "conservative_repeated"),
            "online_after_setup": compact_item(best_by_model(grid_results, {SAME_TARGET_UPPER}, "online_after_setup"), "online_after_setup"),
            "target_once_setup": compact_item(best_upper, "target_once_setup"),
        },
        "constructor_namespaces": namespaces,
        "feature_bins": int(args.feature_bins),
        "grid_results": grid_results,
        "logodds_smoothing": float(args.logodds_smoothing),
        "model_stats": model_stats,
        "requested_grid_public_rank": requested_grid_public_rank,
        "scan_seed_count": args.scan_seed_count,
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
            "p801_script": str(P801_SCRIPT),
            "p803_script": str(P803_SCRIPT),
            "p805_script": str(P805_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(best_requested, best_cross, best_upper),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC-FEATURE ONLY: classifier inputs are coarse factor-base index, x-coordinate, and pair-sum-x features.",
            "CROSS-TARGET TEST: the main classifier trains on the other target group in the same namespace and predicts supports on the held-out group.",
            "SAME-TARGET UPPER BOUND: same-target classifier uses held-out target support labels and is diagnostic only, not a valid public derivation claim.",
            "MODEL-BOUND TARGET-ONCE SETUP: line calibration and support setup are charged once per target across fresh namespaces.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p806_public_feature_classifier",
        "parameters": {
            "constructor_namespaces": namespaces,
            "control_count": args.control_count,
            "feature_bins": args.feature_bins,
            "field_weight": args.field_weight,
            "logodds_smoothing": args.logodds_smoothing,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_line_rows": args.min_line_rows,
            "policies": list(POLICY_NAMES),
            "row_policy": args.row_policy,
            "scan_seed_count": args.scan_seed_count,
            "sparse_policies": args.sparse_policies,
            "support_budgets": support_budgets,
            "train_replicas": args.train_replicas,
            "train_seed_namespace": args.train_seed_namespace,
            "trial_budgets": trial_budgets,
            "walk_mode": args.walk_mode,
            "width": args.width,
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
    parser.add_argument("--constructor-namespaces", default="prehitpair-p806-clf-v11,prehitpair-p806-clf-v12,prehitpair-p806-clf-v13")
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--trial-budgets", default="256")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--scan-seed-count", type=int, default=128)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--feature-bins", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--logodds-smoothing", type=float, default=1.0)
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
                "best_cross_target_by_model": summary["summary"]["best_cross_target_by_model"],
                "best_requested_by_model": summary["summary"]["best_requested_by_model"],
                "best_same_target_upper_by_model": summary["summary"]["best_same_target_upper_by_model"],
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
