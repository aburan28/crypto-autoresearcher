#!/usr/bin/env python3
"""P809 public rank-proxy audit for the P794 support-aggregate rank."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P806_SCRIPT = TASK_DIR / "low_term_total2_p806_public_feature_classifier.py"
P807_SCRIPT = TASK_DIR / "low_term_total2_p807_richer_public_feature_classifier.py"
P808_SCRIPT = TASK_DIR / "low_term_total2_p808_requested_support_invariant_miner.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p809_public_rank_proxy_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p809_public_rank_proxy_audit.md"
SCHEMA = "ecdlp.low_term_total2_p809_public_rank_proxy_audit.v1"


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


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in str(value))
    return "_".join(part for part in text.split("_") if part)


def canonical_support(support: tuple[int, int]) -> tuple[int, int]:
    left, right = int(support[0]), int(support[1])
    return (left, right) if left <= right else (right, left)


def point_x(point: Any, p: int) -> int:
    if point is None:
        return int(p)
    return int(point[0]) % int(p)


def point_y(point: Any, p: int) -> int:
    if point is None:
        return int(p)
    return int(point[1]) % int(p)


def inv_mod(value: int, p: int) -> int | None:
    value %= int(p)
    if value == 0:
        return None
    return pow(value, -1, int(p))


def line_numeric_features(left_point: Any, right_point: Any, ainvs: list[int], p: int) -> tuple[int, int, int]:
    if left_point is None or right_point is None:
        return (3, int(p), int(p))
    a1, a2, a3, a4, _a6 = [int(value) % int(p) for value in ainvs]
    x1, y1 = int(left_point[0]) % int(p), int(left_point[1]) % int(p)
    x2, y2 = int(right_point[0]) % int(p), int(right_point[1]) % int(p)
    if x1 == x2 and (y1 + y2 + a1 * x2 + a3) % int(p) == 0:
        return (2, x1, int(p))
    if x1 == x2 and y1 == y2:
        den = (2 * y1 + a1 * x1 + a3) % int(p)
        inv_den = inv_mod(den, p)
        if inv_den is None:
            return (3, x1, int(p))
        slope = ((3 * x1 * x1 + 2 * a2 * x1 + a4 - a1 * y1) * inv_den) % int(p)
        kind = 1
    else:
        den = (x2 - x1) % int(p)
        inv_den = inv_mod(den, p)
        if inv_den is None:
            return (2, x1, int(p))
        slope = ((y2 - y1) * inv_den) % int(p)
        kind = 0
    intercept = (y1 - slope * x1) % int(p)
    return (kind, slope, intercept)


def stable_hash_score(*parts: Any) -> int:
    text = "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest(), "big")


def rank_map_from_scores(scores: dict[tuple[int, int], float]) -> dict[tuple[int, int], float]:
    ranked = sorted(scores.items(), key=lambda item: (-float(item[1]), item[0][0], item[0][1]))
    ranks: dict[tuple[int, int], float] = {}
    index = 0
    while index < len(ranked):
        end = index + 1
        value = float(ranked[index][1])
        while end < len(ranked) and float(ranked[end][1]) == value:
            end += 1
        average_rank = (index + 1 + end) / 2.0
        for cursor in range(index, end):
            ranks[ranked[cursor][0]] = average_rank
        index = end
    return ranks


def rank_map_from_sort_keys(sort_keys: dict[tuple[int, int], Any]) -> dict[tuple[int, int], float]:
    ranked = sorted(sort_keys.items(), key=lambda item: (item[1], tuple(-part for part in item[0])), reverse=True)
    return {support: float(index + 1) for index, (support, _key) in enumerate(ranked)}


def spearman_rank_maps(left: dict[tuple[int, int], float], right: dict[tuple[int, int], float]) -> float | None:
    supports = sorted(set(left) & set(right))
    if len(supports) < 2:
        return None
    xs = [float(left[support]) for support in supports]
    ys = [float(right[support]) for support in supports]
    x_mean = mean(xs)
    y_mean = mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_den = math.sqrt(sum((x - x_mean) ** 2 for x in xs))
    y_den = math.sqrt(sum((y - y_mean) ** 2 for y in ys))
    if x_den == 0.0 or y_den == 0.0:
        return None
    return round(numerator / (x_den * y_den), 8)


def top_by_score(scores: dict[tuple[int, int], float], count: int) -> set[tuple[int, int]]:
    return {
        support
        for support, _score in sorted(scores.items(), key=lambda item: (-float(item[1]), item[0][0], item[0][1]))[
            : max(0, min(int(count), len(scores)))
        ]
    }


def top_by_sort_key(sort_keys: dict[tuple[int, int], Any], count: int) -> set[tuple[int, int]]:
    return {
        support
        for support, _key in sorted(sort_keys.items(), key=lambda item: (item[1], tuple(-part for part in item[0])), reverse=True)[
            : max(0, min(int(count), len(sort_keys)))
        ]
    }


def overlap_stats(selected: set[tuple[int, int]], exact: set[tuple[int, int]]) -> dict[str, Any]:
    overlap = len(selected & exact)
    union = len(selected | exact)
    return {
        "jaccard_with_exact_rank": ratio(overlap, union),
        "overlap_count": overlap,
        "overlap_over_exact_rank": ratio(overlap, len(exact)),
        "selected_count": len(selected),
        "exact_count": len(exact),
    }


def proxy_family(name: str) -> str:
    if name.startswith("cheap_prehit"):
        return "public_target_conditioned_cheap_prehit"
    if name.startswith("static"):
        return "public_static"
    if name.startswith("hash"):
        return "public_hash_control"
    return "public_rule"


def exact_support_rank_keys(
    p808: Any,
    grouped: dict[tuple[int, int], list[tuple[tuple[int, int, int, int], dict[str, Any]]]],
    all_pairs: list[tuple[int, int]],
) -> dict[tuple[int, int], Any]:
    floor_key = (-1, -1, -10**9, tuple(-10**9 for _ in range(4)))
    return {
        support: p808.trace_sort_tuple(grouped[support][0]) if support in grouped and grouped[support] else floor_key
        for support in all_pairs
    }


def public_static_scores(
    p801: Any,
    context: dict[str, Any],
) -> dict[str, dict[tuple[int, int], float]]:
    verifier = context["verifier"]
    factor_base = context["factor_base"]
    ainvs = context["ainvs"]
    p = int(context["p"])
    target = str(context["target"])
    all_pairs = [canonical_support(support) for support in context["all_pairs"]]
    pair_points = {support: p801.support_sum(verifier, factor_base, support, ainvs, p) for support in all_pairs}
    pair_x_counts = Counter(point_x(point, p) for point in pair_points.values())
    pair_y_counts = Counter(point_y(point, p) for point in pair_points.values())
    pair_point_counts = Counter(
        None if point is None else (int(point[0]) % p, int(point[1]) % p)
        for point in pair_points.values()
    )
    factor_x_counts = Counter(point_x(point, p) for point in factor_base)
    factor_y_counts = Counter(point_y(point, p) for point in factor_base)
    scores: dict[str, dict[tuple[int, int], float]] = defaultdict(dict)
    size = len(factor_base)
    for support in all_pairs:
        left, right = support
        lp, rp = factor_base[left], factor_base[right]
        lx, rx = point_x(lp, p), point_x(rp, p)
        ly, ry = point_y(lp, p), point_y(rp, p)
        pair_point = pair_points[support]
        pair_x, pair_y = point_x(pair_point, p), point_y(pair_point, p)
        point_key = None if pair_point is None else (int(pair_point[0]) % p, int(pair_point[1]) % p)
        span = abs(left - right)
        index_sum = left + right
        kind, slope, intercept = line_numeric_features(lp, rp, ainvs, p)
        scores["static_span_low"][support] = -float(span)
        scores["static_span_high"][support] = float(span)
        scores["static_index_sum_low"][support] = -float(index_sum)
        scores["static_index_sum_high"][support] = float(index_sum)
        scores["static_endpoint_low"][support] = -float(min(left, right))
        scores["static_endpoint_high"][support] = float(max(left, right))
        scores["static_center_span"][support] = -abs(float(span) - (float(size) / 3.0))
        scores["static_pair_x_low"][support] = -float(pair_x)
        scores["static_pair_x_high"][support] = float(pair_x)
        scores["static_pair_y_low"][support] = -float(pair_y)
        scores["static_pair_y_high"][support] = float(pair_y)
        scores["static_pair_point_collision_high"][support] = float(pair_point_counts[point_key])
        scores["static_pair_x_collision_high"][support] = float(pair_x_counts[pair_x])
        scores["static_pair_y_collision_high"][support] = float(pair_y_counts[pair_y])
        scores["static_factor_xy_mult_high"][support] = float(
            factor_x_counts[lx] + factor_x_counts[rx] + factor_y_counts[ly] + factor_y_counts[ry]
        )
        scores["static_x_gap_low"][support] = -float(abs(lx - rx))
        scores["static_y_gap_low"][support] = -float(abs(ly - ry))
        scores["static_sym_x_sum_low"][support] = -float((lx + rx) % p)
        scores["static_sym_x_prod_low"][support] = -float((lx * rx) % p)
        scores["static_line_kind_tangent"][support] = 1.0 if kind == 1 else 0.0
        scores["static_line_slope_low"][support] = -float(slope)
        scores["static_line_intercept_low"][support] = -float(intercept)
        scores["hash_target_support_control"][support] = -float(stable_hash_score(target, support[0], support[1]))
    return {key: dict(value) for key, value in scores.items()}


def cheap_prehit_scores(
    p746: Any,
    p801: Any,
    relprobe: Any,
    context: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, dict[tuple[int, int], float]]:
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
    for seed_index in range(int(args.proxy_seed_count)):
        seed_label = f"p{seed_index:04d}"
        full_seed = (
            f"ecdlp-p809-{context['namespace']}-{slug(target)}:"
            f"{seed_label}:fb{context['factor_base_size']}:w2:{args.walk_mode}"
        )
        challenge, _secret = relprobe.make_challenge(verifier, inv, ainvs, full_seed, context["factor_base_size"])
        base = verifier.point_from_json(challenge["base"])
        public = verifier.point_from_json(challenge["public"])
        walk = p746.walk_schedule(verifier, str(args.walk_mode), base, public, ainvs, p)
        a, b = p746.deterministic_start(int(order), full_seed, str(args.walk_mode))
        lhs = verifier.add_points(verifier.mul_point(a, base, ainvs, p), verifier.mul_point(b, public, ainvs, p), ainvs, p)
        for trial in range(1, trial_budget + 1):
            supports = point_to_supports.get(lhs) or []
            stamp = seed_index * trial_budget + trial
            for support in supports:
                hit_counts[support] += 1
                first_seen.setdefault(support, stamp)
            if trial == trial_budget:
                break
            delta = p746.select_delta(walk, full_seed, trial, a, b)
            a = (a + int(delta["da"])) % int(order)
            b = (b + int(delta["db"])) % int(order)
            lhs = verifier.add_points(lhs, delta["delta"], ainvs, p)

    missing_seen = (int(args.proxy_seed_count) * trial_budget) + 1
    out = {
        "cheap_prehit_count": {},
        "cheap_prehit_first_seen": {},
        "cheap_prehit_count_then_first": {},
    }
    for support in all_pairs:
        count = int(hit_counts[support])
        first = int(first_seen.get(support, missing_seen))
        out["cheap_prehit_count"][support] = float(count)
        out["cheap_prehit_first_seen"][support] = -float(first)
        out["cheap_prehit_count_then_first"][support] = float(count * missing_seen - first)
    return out


def aggregate_proxy_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["proxy"], int(row["support_budget"]))].append(row)
    out = []
    for (proxy, budget), items in sorted(grouped.items()):
        out.append(
            {
                "family": proxy_family(proxy),
                "proxy": proxy,
                "support_budget": int(budget),
                "jaccard_with_exact_rank": stat([float(item["jaccard_with_exact_rank"] or 0.0) for item in items]),
                "overlap_over_exact_rank": stat([float(item["overlap_over_exact_rank"] or 0.0) for item in items]),
                "overlap_count": stat([float(item["overlap_count"]) for item in items]),
                "spearman_rho": stat([float(item["spearman_rho"]) for item in items if item["spearman_rho"] is not None]),
            }
        )
    return out


def best_proxy_row(rows: list[dict[str, Any]], support_budget: int | None = None) -> dict[str, Any] | None:
    candidates = rows if support_budget is None else [row for row in rows if int(row["support_budget"]) == int(support_budget)]
    candidates = [row for row in candidates if not row["proxy"].startswith("hash")]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda row: (
            float(row["overlap_over_exact_rank"] or 0.0),
            float(row["jaccard_with_exact_rank"] or 0.0),
            float(row["spearman_rho"] or -2.0),
        ),
    )


def best_aggregate_at_budget(aggregate_rows: list[dict[str, Any]], support_budget: int) -> dict[str, Any] | None:
    candidates = [row for row in aggregate_rows if int(row["support_budget"]) == int(support_budget) and not row["proxy"].startswith("hash")]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda row: (
            float(row["overlap_over_exact_rank"]["min"] or 0.0),
            float(row["overlap_over_exact_rank"]["mean"] or 0.0),
            float(row["jaccard_with_exact_rank"]["mean"] or 0.0),
        ),
    )


def determine_claim(aggregate_rows: list[dict[str, Any]], promote_budget: int) -> str:
    best = best_aggregate_at_budget(aggregate_rows, promote_budget)
    if best is None:
        return "NEGATIVE_RESULT_P809_NO_PUBLIC_PROXY_ROWS"
    min_overlap = float(best["overlap_over_exact_rank"]["min"] or 0.0)
    max_overlap = float(best["overlap_over_exact_rank"]["max"] or 0.0)
    if min_overlap >= 0.80:
        return "P809_PUBLIC_RANK_PROXY_READY_FOR_CHARGED_SCAN"
    if max_overlap >= 0.80:
        return "P809_PARTIAL_PUBLIC_RANK_PROXY_SIGNAL"
    return "NEGATIVE_RESULT_P809_PUBLIC_RANK_PROXIES_FAIL_TRACE_RANK"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    if int(args.width) != 2:
        raise ValueError("P809 audits width-2 support-pair ranks; use --width 2")
    p806 = load_module("ecdlp_p806_for_p809", P806_SCRIPT)
    p807 = load_module("ecdlp_p807_for_p809", P807_SCRIPT)
    p808 = load_module("ecdlp_p808_for_p809", P808_SCRIPT)
    p807.configure_p807(p806)
    modules = p808.load_research_stack(p806)
    p801 = modules["p801"]
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
    relprobe = stack["relprobe"]

    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    support_budgets = csv_ints(args.support_budgets)
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

    proxy_rows = []
    context_rows = []
    for namespace in namespaces:
        for group_key in required:
            print(f"building proxy context namespace={namespace} group={group_key}", flush=True)
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
            all_pairs = [canonical_support(support) for support in context["all_pairs"]]
            _trace_features, grouped = p808.build_trace_features(
                all_pairs,
                train_prepared[group_key]["all_calibrated"],
                int(context["order"]),
                int(args.feature_bins),
            )
            exact_keys = exact_support_rank_keys(p808, grouped, all_pairs)
            exact_rank_map = rank_map_from_sort_keys(exact_keys)
            scores_by_proxy = public_static_scores(p801, context)
            scores_by_proxy.update(cheap_prehit_scores(p746, p801, relprobe, context, args))
            proxy_setup_additions = len(all_pairs) + (int(args.proxy_seed_count) * int(args.proxy_trial_budget))
            rho_estimate = math.isqrt(int(context["order"])) + 1
            context_rows.append(
                {
                    "all_pair_count": len(all_pairs),
                    "group_key": group_key,
                    "namespace": namespace,
                    "proxy_seed_count": int(args.proxy_seed_count),
                    "proxy_setup_additions": proxy_setup_additions,
                    "proxy_setup_over_target_rho_estimate": ratio(proxy_setup_additions, rho_estimate),
                    "proxy_trial_budget": int(args.proxy_trial_budget),
                    "target": str(context["target"]),
                    "target_rho_estimate": rho_estimate,
                }
            )
            for proxy_name, scores in sorted(scores_by_proxy.items()):
                proxy_rank_map = rank_map_from_scores(scores)
                rho = spearman_rank_maps(exact_rank_map, proxy_rank_map)
                for budget in support_budgets:
                    selected = top_by_score(scores, int(budget))
                    exact = top_by_sort_key(exact_keys, int(budget))
                    proxy_rows.append(
                        {
                            **overlap_stats(selected, exact),
                            "family": proxy_family(proxy_name),
                            "group_key": group_key,
                            "namespace": namespace,
                            "proxy": proxy_name,
                            "scope": "PUBLIC-TARGET-CONDITIONED" if proxy_name.startswith("cheap_prehit") else "PUBLIC-STATIC",
                            "spearman_rho": rho,
                            "support_budget": int(budget),
                            "target": str(context["target"]),
                        }
                    )

    aggregate = aggregate_proxy_rows(proxy_rows)
    promote_budget = int(args.promote_support_budget)
    summary = {
        "aggregate_proxy_rows": aggregate,
        "best_context_proxy": best_proxy_row(proxy_rows, promote_budget),
        "best_global_proxy": best_proxy_row(proxy_rows),
        "best_promote_budget_aggregate": best_aggregate_at_budget(aggregate, promote_budget),
        "constructor_namespaces": namespaces,
        "context_rows": context_rows,
        "promote_support_budget": promote_budget,
        "proxy_rows": proxy_rows,
        "support_budgets": support_budgets,
        "target_groups": required,
        "train_seed_namespace": args.train_seed_namespace,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p806_script": str(P806_SCRIPT),
            "p807_script": str(P807_SCRIPT),
            "p808_script": str(P808_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(aggregate, promote_budget),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC-PROXY ONLY: proxy rankings use public factor-base geometry, public target-conditioned walk pre-hit counts, and deterministic hash controls.",
            "NO CALIBRATION LABELS IN PROXY: candidate row counts, selected calibration lines, line values, rhs, scale, and target scalar are used only to define the evaluation rank, not the candidate proxy ranking.",
            "SUPPORT-RANK ONLY: P809 measures top-k and rank overlap with the P794 support-aggregate rank; it does not claim recovered rows.",
            "PROMOTION GATE: a proxy must recover at least 80 percent of exact top-256 supports across contexts before a charged row-recovery scan is promoted.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p809_public_rank_proxy_audit",
        "parameters": {
            "constructor_namespaces": namespaces,
            "feature_bins": int(args.feature_bins),
            "min_line_rows": int(args.min_line_rows),
            "promote_support_budget": promote_budget,
            "proxy_seed_count": int(args.proxy_seed_count),
            "proxy_trial_budget": int(args.proxy_trial_budget),
            "row_policy": args.row_policy,
            "sparse_policies": args.sparse_policies,
            "support_budgets": support_budgets,
            "train_replicas": int(args.train_replicas),
            "train_seed_namespace": args.train_seed_namespace,
            "walk_mode": args.walk_mode,
            "width": int(args.width),
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        **payload,
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **payload["summary"],
            "proxy_rows": [
                {
                    key: value
                    for key, value in row.items()
                    if key in {
                        "family",
                        "group_key",
                        "jaccard_with_exact_rank",
                        "namespace",
                        "overlap_count",
                        "overlap_over_exact_rank",
                        "proxy",
                        "scope",
                        "spearman_rho",
                        "support_budget",
                        "target",
                    }
                }
                for row in payload["summary"]["proxy_rows"]
            ],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespaces", default="prehitpair-p807-rich-v14,prehitpair-p807-rich-v15,prehitpair-p807-rich-v16")
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--promote-support-budget", type=int, default=256)
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--feature-bins", type=int, default=8)
    parser.add_argument("--proxy-seed-count", type=int, default=32)
    parser.add_argument("--proxy-trial-budget", type=int, default=64)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
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
                "best_context_proxy": summary["summary"]["best_context_proxy"],
                "best_promote_budget_aggregate": summary["summary"]["best_promote_budget_aggregate"],
                "claim_status": summary["claim_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
