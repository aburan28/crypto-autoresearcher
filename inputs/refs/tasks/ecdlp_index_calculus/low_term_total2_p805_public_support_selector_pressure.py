#!/usr/bin/env python3
"""P805 public support-selector pressure test for the P804 target-once signal."""

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
P801_SCRIPT = TASK_DIR / "low_term_total2_p801_pre_hit_support_pair_constructor.py"
P803_SCRIPT = TASK_DIR / "low_term_total2_p803_prehit_support_setup_amortization.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p805_public_support_selector_pressure_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p805_public_support_selector_pressure.md"
SCHEMA = "ecdlp.low_term_total2_p805_public_support_selector_pressure.v1"

REQUESTED = "requested_support_prehit"
ROTATED = "rotated_support_prehit"
ALL_PAIR = "all_pair_first_hit_control"
PUBLIC_POLICIES = (
    "public_index_sum_low",
    "public_close_span",
    "public_pair_sum_x_low",
    "public_pair_sum_x_high",
    "public_same_x_then_span",
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


def int_value(row: dict[str, Any], key: str) -> int:
    return int(row.get(key) or 0)


def policy_kind(policy_name: str) -> str:
    if policy_name == REQUESTED:
        return "requested_support_pre_hit_constructor"
    if policy_name == ROTATED:
        return "rotated_support_pre_hit_control"
    if policy_name == ALL_PAIR:
        return "all_pair_first_hit_control"
    if policy_name in PUBLIC_POLICIES:
        return "public_support_feature_pre_hit_control"
    return "unknown_policy"


def point_x(point: Any, p: int) -> int:
    if point is None:
        return int(p)
    return int(point[0]) % int(p)


def support_mean(values: set[tuple[int, int]]) -> float:
    if not values:
        return 0.0
    return round(mean(abs(int(left) - int(right)) for left, right in values), 8)


def select_public_supports(
    p801: Any,
    verifier: Any,
    factor_base: list[Any],
    ainvs: list[int],
    p: int,
    policy_name: str,
    count: int,
) -> set[tuple[int, int]]:
    all_pairs = sorted(p801.all_support_pairs(len(factor_base)))
    pair_sum_x_cache: dict[tuple[int, int], int] = {}

    def pair_sum_x(support: tuple[int, int]) -> int:
        if support not in pair_sum_x_cache:
            pair_sum_x_cache[support] = point_x(p801.support_sum(verifier, factor_base, support, ainvs, p), p)
        return pair_sum_x_cache[support]

    def key(support: tuple[int, int]) -> tuple[Any, ...]:
        left, right = int(support[0]), int(support[1])
        lx = point_x(factor_base[left], p)
        rx = point_x(factor_base[right], p)
        span = abs(left - right)
        index_sum = left + right
        if policy_name == "public_index_sum_low":
            return (index_sum, span, left, right)
        if policy_name == "public_close_span":
            return (span, index_sum, left, right)
        if policy_name == "public_pair_sum_x_low":
            return (pair_sum_x(support), index_sum, span, left, right)
        if policy_name == "public_pair_sum_x_high":
            return (-pair_sum_x(support), index_sum, span, left, right)
        if policy_name == "public_same_x_then_span":
            return (0 if lx == rx else 1, span, index_sum, left, right)
        raise ValueError(f"unknown public support policy {policy_name!r}")

    return set(sorted(all_pairs, key=key)[: max(0, min(int(count), len(all_pairs)))])


def support_sets_for_budget(
    p801: Any,
    verifier: Any,
    factor_base: list[Any],
    ainvs: list[int],
    p: int,
    trained_by_budget: dict[int, dict[tuple[int, int, int, int], dict[str, Any]]],
    budget: int,
) -> dict[str, set[tuple[int, int]]]:
    requested = {
        p801.canonical_support((int(key[0]), int(key[1])))
        for key in trained_by_budget[int(budget)]
    }
    out = {
        REQUESTED: requested,
        ROTATED: p801.rotated_supports_for(requested, len(factor_base)),
        ALL_PAIR: p801.all_support_pairs(len(factor_base)),
    }
    for policy_name in PUBLIC_POLICIES:
        out[policy_name] = select_public_supports(
            p801,
            verifier,
            factor_base,
            ainvs,
            p,
            policy_name,
            len(requested),
        )
    return out


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


def scan_seed_grid(
    p801: Any,
    p746: Any,
    p748: Any,
    verifier: Any,
    challenge: dict[str, Any],
    secret: int,
    base: Any,
    public: Any,
    ainvs: list[int],
    p: int,
    order: int,
    target: str,
    factor_base_size: int,
    seed_label: str,
    full_seed: str,
    support_budgets: list[int],
    trial_budgets: list[int],
    point_policy: dict[Any, dict[tuple[int, str], tuple[int, int]]],
    support_policy_stats: dict[tuple[int, str], dict[str, int]],
    args: argparse.Namespace,
) -> dict[tuple[int, int, str], dict[str, Any]]:
    max_trial = max(int(value) for value in trial_budgets)
    walk = p746.walk_schedule(verifier, str(args.walk_mode), base, public, ainvs, p)
    a, b = p746.deterministic_start(int(order), full_seed, str(args.walk_mode))
    lhs = verifier.add_points(verifier.mul_point(a, base, ainvs, p), verifier.mul_point(b, public, ainvs, p), ainvs, p)
    hits: dict[tuple[int, str], dict[str, Any]] = {}
    zero_b_hits = Counter()

    for trial in range(1, max_trial + 1):
        entries = point_policy.get(lhs) or {}
        if entries:
            for support_key, support in entries.items():
                if support_key in hits:
                    continue
                if b % int(order) == 0:
                    zero_b_hits[support_key] += 1
                    continue
                relation = {"a": int(a), "b": int(b), "indices": [int(support[0]), int(support[1])]}
                terms = verifier.relation_terms(relation, challenge, ainvs, p)
                if terms is None or not verifier.verify_relation(relation, challenge, ainvs, p, base, public):
                    continue
                setup = int(support_policy_stats[support_key]["targeted_setup_group_additions"])
                hits[support_key] = p801.hit_row(
                    p748,
                    verifier,
                    target,
                    seed_label,
                    full_seed,
                    challenge,
                    secret,
                    order,
                    factor_base_size,
                    walk,
                    max_trial,
                    trial,
                    setup,
                    relation,
                    terms,
                )
        if len(hits) == len(support_policy_stats) or trial == max_trial:
            break
        delta = p746.select_delta(walk, full_seed, trial, a, b)
        a = (a + int(delta["da"])) % int(order)
        b = (b + int(delta["db"])) % int(order)
        lhs = verifier.add_points(lhs, delta["delta"], ainvs, p)

    rows = {}
    for support_budget in support_budgets:
        for policy_name in POLICY_NAMES:
            support_key = (int(support_budget), policy_name)
            stats = support_policy_stats[support_key]
            hit = hits.get(support_key)
            for trial_budget in trial_budgets:
                if hit is not None and int(hit["scanned_trials"]) <= int(trial_budget):
                    row = {**hit, "configured_trials": int(trial_budget)}
                else:
                    row = p801.base_row(
                        p748,
                        target,
                        seed_label,
                        full_seed,
                        challenge,
                        secret,
                        order,
                        factor_base_size,
                        walk,
                        int(trial_budget),
                        int(trial_budget),
                        int(stats["targeted_setup_group_additions"]),
                    )
                row["_p805_policy"] = {
                    "policy": policy_name,
                    "support_budget": int(support_budget),
                    "targeted_support_count": int(stats["targeted_support_count"]),
                    "targeted_unique_point_count": int(stats["targeted_unique_point_count"]),
                    "trial_budget": int(trial_budget),
                }
                row["zero_b_hits"] = int(zero_b_hits.get(support_key) or 0)
                row["zero_b_skips"] = int(zero_b_hits.get(support_key) or 0)
                rows[(int(support_budget), int(trial_budget), policy_name)] = row
    return rows


def collect_namespace_rows(
    p801: Any,
    p746: Any,
    p748: Any,
    relprobe: Any,
    base_item: dict[str, Any],
    trained_by_support_budget: dict[int, dict[tuple[int, int, int, int], dict[str, Any]]],
    support_budgets: list[int],
    trial_budgets: list[int],
    case: dict[str, Any],
    namespace: str,
    args: argparse.Namespace,
) -> tuple[
    dict[tuple[int, int, str], list[dict[str, Any]]],
    dict[tuple[int, str], dict[str, int]],
    int,
    list[dict[str, Any]],
]:
    verifier, record, inv = p746.load_target(relprobe, str(base_item["target"]))
    ainvs = record["ainvs"]
    p = int(inv["p"])
    order = int(inv["base_order"])
    factor_base_size = int(case["factor_base_size"])
    sample_seed = (
        f"ecdlp-p805-{namespace}-{slug(base_item['target'])}:sample:"
        f"fb{factor_base_size}:w2:{args.walk_mode}"
    )
    sample_challenge, _sample_secret = relprobe.make_challenge(verifier, inv, ainvs, sample_seed, factor_base_size)
    factor_base = [
        verifier.point_from_json(point)
        for point in sample_challenge["factor_base"][: max(1, min(factor_base_size, len(sample_challenge["factor_base"])))]
    ]

    supports_by_policy: dict[tuple[int, str], set[tuple[int, int]]] = {}
    for support_budget in support_budgets:
        sets = support_sets_for_budget(
            p801,
            verifier,
            factor_base,
            ainvs,
            p,
            trained_by_support_budget,
            int(support_budget),
        )
        for policy_name, supports in sets.items():
            supports_by_policy[(int(support_budget), policy_name)] = supports
    support_stats = support_overlap_stats(supports_by_policy, support_budgets)
    point_policy, support_policy_stats = p801.build_point_policy_map(verifier, factor_base, ainvs, p, supports_by_policy)
    rows_by_grid = {
        (int(support_budget), int(trial_budget), policy_name): []
        for support_budget in support_budgets
        for trial_budget in trial_budgets
        for policy_name in POLICY_NAMES
    }
    for seed_label in seed_labels(int(args.scan_seed_count)):
        full_seed = (
            f"ecdlp-p805-{namespace}-{slug(base_item['target'])}:"
            f"{seed_label}:fb{factor_base_size}:w2:{args.walk_mode}"
        )
        challenge, secret = relprobe.make_challenge(verifier, inv, ainvs, full_seed, factor_base_size)
        base = verifier.point_from_json(challenge["base"])
        public = verifier.point_from_json(challenge["public"])
        rows = scan_seed_grid(
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
            str(base_item["target"]),
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
    return rows_by_grid, support_policy_stats, order, support_stats


def evaluate_policy(
    p797: Any,
    p793: Any,
    p792: Any,
    p789: Any,
    train_prepared: dict[str, Any],
    trained: dict[tuple[int, int, int, int], dict[str, Any]],
    rows: list[dict[str, Any]],
    order: int,
    target: str,
    policy_name: str,
    setup_stats: dict[str, int],
    args: argparse.Namespace,
) -> dict[str, Any]:
    records, rows_meta = p792.collect_form_records(p789, [(0, rows, int(order))], target)
    prepared = {
        "dest_target": target,
        "order": int(order),
        "records": records,
        "row_count": len(rows_meta),
        "rows_meta": rows_meta,
    }
    row_keys = set(rows_meta)
    scored = p797.score_subset(
        p793,
        prepared,
        trained,
        row_keys,
        int(args.field_weight),
        int(args.control_count),
    )
    train_cost = p797.train_cost(trained, train_prepared)
    generated_online = int(scored["generated_online_group_additions"])
    setup_additions = int(setup_stats["targeted_setup_group_additions"])
    generated_total = (
        int(train_cost["calibration_online_group_additions"])
        + setup_additions
        + generated_online
        + int(args.field_weight) * (int(train_cost["calibration_field_ops"]) + int(scored["scoring_field_ops"]))
    )
    recovered_rho = int(scored["primary"].get("recovered_rho_baseline") or 0)
    hit_rows = [row for row in rows if row.get("forms")]
    return {
        "aggregate": {
            "generated_once_train_total_unit_cost": generated_total,
            "generated_once_train_total_unit_cost_over_recovered_rho": ratio(generated_total, recovered_rho),
            "generated_online_group_additions": generated_online,
            "generated_row_count": int(scored["generated_row_count"]),
            "generated_row_rho_baseline": int(scored["generated_row_rho_baseline"]),
            "hit_row_count": len(hit_rows),
            "hit_row_rate_over_generated": ratio(len(hit_rows), int(scored["generated_row_count"])),
            "max_control_recovered_row_count": int(scored["max_control_recovered_row_count"]),
            "primary_minus_max_control_recovered_rows": int(scored["primary"].get("recovered_row_count") or 0)
            - int(scored["max_control_recovered_row_count"]),
            "recovered_row_count": int(scored["primary"].get("recovered_row_count") or 0),
            "recovered_rho_baseline": recovered_rho,
            "recovered_row_rate_over_hit": ratio(int(scored["primary"].get("recovered_row_count") or 0), len(hit_rows)),
            "scored_form_count": int(scored["primary"].get("scored_form_count") or 0),
            "scoring_field_ops": int(scored["scoring_field_ops"]),
            "target_row_mismatch_count": int(scored["primary"].get("target_row_mismatch_count") or 0),
            "targeted_point_collision_count": int(setup_stats["targeted_point_collision_count"]),
            "targeted_setup_group_additions": setup_additions,
            "targeted_support_count": int(setup_stats["targeted_support_count"]),
            "targeted_unique_point_count": int(setup_stats["targeted_unique_point_count"]),
            "train_calibration_field_ops": int(train_cost["calibration_field_ops"]),
            "train_calibration_online_group_additions": int(train_cost["calibration_online_group_additions"]),
            "zero_b_skip_count": sum(int(row.get("zero_b_skips") or 0) for row in rows),
        },
        "policy": {"kind": policy_kind(policy_name), "name": policy_name},
    }


def aggregate_policy_results(items: list[dict[str, Any]], policy_name: str) -> dict[str, Any]:
    totals = Counter()
    controls = []
    for item in items:
        aggregate = item["aggregate"]
        for key, value in aggregate.items():
            if isinstance(value, int):
                totals[key] += value
        controls.append(int(aggregate["max_control_recovered_row_count"]))
    recovered_rho = int(totals["recovered_rho_baseline"])
    generated_rows = int(totals["generated_row_count"])
    hit_rows = int(totals["hit_row_count"])
    return {
        "aggregate": {
            **dict(totals),
            "generated_once_train_total_unit_cost_over_recovered_rho": ratio(
                int(totals["generated_once_train_total_unit_cost"]),
                recovered_rho,
            ),
            "hit_row_rate_over_generated": ratio(hit_rows, generated_rows),
            "max_control_recovered_row_count": max(controls, default=0),
            "primary_minus_max_control_recovered_rows": int(totals["recovered_row_count"]) - max(controls, default=0),
            "recovered_row_rate_over_hit": ratio(int(totals["recovered_row_count"]), hit_rows),
            "target_count": len(items),
        },
        "policy": {"kind": policy_kind(policy_name), "name": policy_name},
        "target_results": items,
    }


def enrich_grid_item(p803: Any, item: dict[str, Any], field_weight: int) -> dict[str, Any]:
    enriched = p803.enrich_grid_item(item, field_weight)
    enriched["policy_claim"] = item.get("policy_claim")
    return enriched


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


def public_policy_rank(items: list[dict[str, Any]], support_budget: int, trial_budget: int) -> list[dict[str, Any]]:
    peers = peer_items(items, support_budget, trial_budget)
    public = [peers[name] for name in PUBLIC_POLICIES if name in peers]
    ranked = sorted(public, key=lambda item: (-int(item["recovered_row_count"]), item["cost_models"]["target_once_setup"]["cost_over_recovered_rho"] or 10**18))
    return [compact_item(item) for item in ranked]


def determine_policy_claim(item: dict[str, Any], peers: dict[str, dict[str, Any]]) -> str:
    policy_name = item["policy"]["name"]
    recovered = int(item["recovered_row_count"])
    max_line_control = int(item["max_control_recovered_row_count"])
    rotated = int((peers.get(ROTATED) or {}).get("recovered_row_count") or 0)
    all_pair = int((peers.get(ALL_PAIR) or {}).get("recovered_row_count") or 0)
    requested = int((peers.get(REQUESTED) or {}).get("recovered_row_count") or 0)
    target_once = item["cost_models"]["target_once_setup"]["cost_over_recovered_rho"]
    if recovered <= max_line_control:
        return "does_not_beat_line_controls"
    if policy_name == REQUESTED and recovered > max(rotated, all_pair) and target_once is not None and target_once < 1.0:
        return "requested_support_target_once_below_rho"
    if policy_name in PUBLIC_POLICIES and recovered >= requested and target_once is not None and target_once < 1.0:
        return "public_support_selector_matches_requested_below_rho"
    if policy_name in PUBLIC_POLICIES and recovered > max(rotated, all_pair):
        return "public_support_selector_beats_generic_controls"
    if policy_name in {ROTATED, ALL_PAIR}:
        return "generic_control_boundary"
    return "support_selector_boundary"


def determine_claim(items: list[dict[str, Any]], best_requested: dict[str, Any] | None, best_public: dict[str, Any] | None) -> str:
    if best_requested is None or int(best_requested["recovered_row_count"]) == 0:
        return "NEGATIVE_RESULT_P805_REQUESTED_SUPPORT_SIGNAL_LOST"
    if best_public is not None:
        public_ratio = best_public["cost_models"]["target_once_setup"]["cost_over_recovered_rho"]
        if (
            public_ratio is not None
            and public_ratio < 1.0
            and int(best_public["recovered_row_count"]) >= int(best_requested["recovered_row_count"])
        ):
            return "P805_PUBLIC_SUPPORT_SELECTOR_MATCHES_REQUESTED_BELOW_RHO"
    public_best_recovered = 0 if best_public is None else int(best_public["recovered_row_count"])
    requested_recovered = int(best_requested["recovered_row_count"])
    if public_best_recovered < requested_recovered:
        return "P805_PUBLIC_SUPPORT_SELECTORS_FAIL_REQUESTED_SIGNAL"
    return "P805_PUBLIC_SUPPORT_SELECTOR_PARTIAL_BOUNDARY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    if int(args.width) != 2:
        raise ValueError("P805 validates width-2 support pairs; use --width 2")
    p801 = load_module("ecdlp_p801_for_p805", P801_SCRIPT)
    p803 = load_module("ecdlp_p803_for_p805", P803_SCRIPT)
    p800 = p801.load_module("ecdlp_p800_for_p805", p801.P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p805", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p805", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p805", p798.P797_SCRIPT)
    p796 = p797.load_module("ecdlp_p796_for_p805", p797.P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p805", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p805", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p805", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p805", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p805", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p805", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p805", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p805", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p805", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p805", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p805", p782.P780_SCRIPT)
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

    scan_bank = {}
    support_stats = []
    for namespace in namespaces:
        for group_key in required:
            case = p784.case_from_group(
                base_groups[group_key],
                p784.TRIM12_DELTA,
                namespace,
                "p805",
                p784.DEST_SEED_COUNT,
                p784.DEST_POOL_COUNT,
            )
            print(f"public-selector scanning namespace={namespace} group={group_key} rows={args.scan_seed_count}", flush=True)
            rows_by_grid, support_policy_stats, order, stats_rows = collect_namespace_rows(
                p801,
                p746,
                p748,
                relprobe,
                base_groups[group_key],
                trained_by_group_support[group_key],
                support_budgets,
                trial_budgets,
                case,
                namespace,
                args,
            )
            for row in stats_rows:
                support_stats.append({**row, "group_key": group_key, "namespace": namespace})
            scan_bank[(namespace, group_key)] = {
                "order": order,
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
                        item = evaluate_policy(
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
            policy_results = [aggregate_policy_results(policy_items[policy_name], policy_name) for policy_name in POLICY_NAMES]
            for item in policy_results:
                item["support_budget"] = int(support_budget)
                item["trial_budget"] = int(trial_budget)
                grid_results.append(enrich_grid_item(p803, item, int(args.field_weight)))

    for support_budget in support_budgets:
        for trial_budget in trial_budgets:
            peers = peer_items(grid_results, int(support_budget), int(trial_budget))
            for item in peers.values():
                item["policy_claim"] = determine_policy_claim(item, peers)

    best_requested = best_by_model(grid_results, {REQUESTED}, "target_once_setup")
    best_public = best_by_model(grid_results, set(PUBLIC_POLICIES), "target_once_setup")
    best_requested_grid_public_rank = []
    if best_requested is not None:
        best_requested_grid_public_rank = public_policy_rank(
            grid_results,
            int(best_requested["support_budget"]),
            int(best_requested["trial_budget"]),
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
        "best_public_by_target_once": compact_item(best_public),
        "best_requested_by_model": {
            "conservative_repeated": compact_item(best_by_model(grid_results, {REQUESTED}, "conservative_repeated"), "conservative_repeated"),
            "online_after_setup": compact_item(best_by_model(grid_results, {REQUESTED}, "online_after_setup"), "online_after_setup"),
            "target_once_setup": compact_item(best_requested, "target_once_setup"),
        },
        "best_requested_grid_public_rank": best_requested_grid_public_rank,
        "constructor_namespaces": namespaces,
        "grid_results": grid_results,
        "public_policies": list(PUBLIC_POLICIES),
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
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(grid_results, best_requested, best_public),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SUPPORT-SELECTOR ISOLATION: P805 keeps the trained line-scoring layer and varies only pre-hit support selection.",
            "PUBLIC-RULE CONTROLS: public selectors use factor-base indices, point x-coordinates, and pair-sum x-coordinates; they do not use factor logs or target scalar.",
            "MODEL-BOUND TARGET-ONCE SETUP: line calibration and support setup are charged once per target across fresh namespaces.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p805_public_support_selector_pressure",
        "parameters": {
            "constructor_namespaces": namespaces,
            "control_count": args.control_count,
            "field_weight": args.field_weight,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_line_rows": args.min_line_rows,
            "public_policies": list(PUBLIC_POLICIES),
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
    parser.add_argument("--constructor-namespaces", default="prehitpair-p805-public-v8,prehitpair-p805-public-v9,prehitpair-p805-public-v10")
    parser.add_argument("--support-budgets", default="128,256,512")
    parser.add_argument("--trial-budgets", default="256")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--scan-seed-count", type=int, default=128)
    parser.add_argument("--control-count", type=int, default=8)
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
                "best_public_by_target_once": summary["summary"]["best_public_by_target_once"],
                "best_requested_by_model": summary["summary"]["best_requested_by_model"],
                "best_requested_grid_public_rank": summary["summary"]["best_requested_grid_public_rank"],
                "claim_status": summary["claim_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
