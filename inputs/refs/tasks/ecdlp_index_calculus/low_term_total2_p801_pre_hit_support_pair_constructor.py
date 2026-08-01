#!/usr/bin/env python3
"""P801 pre-hit support-pair constructor audit."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P800_SCRIPT = TASK_DIR / "low_term_total2_p800_form_construction_support_pair_filter.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p801_pre_hit_support_pair_constructor_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p801_pre_hit_support_pair_constructor.md"
SCHEMA = "ecdlp.low_term_total2_p801_pre_hit_support_pair_constructor.v1"
DEFAULT_BUDGETS = "32,128,512"
POLICY_NAMES = ("requested_support_prehit", "rotated_support_prehit", "all_pair_first_hit_control")


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


def slug(value: str) -> str:
    text = "".join(ch if ch.isalnum() else "_" for ch in str(value))
    return "_".join(part for part in text.split("_") if part)


def seed_labels(count: int) -> list[str]:
    return [f"t{index:04d}" for index in range(int(count))]


def support_sum(verifier: Any, factor_base: list[Any], support: tuple[int, int], ainvs: list[int], p: int) -> Any:
    return verifier.add_points(factor_base[int(support[0])], factor_base[int(support[1])], ainvs, p)


def canonical_support(support: tuple[int, int]) -> tuple[int, int]:
    left, right = int(support[0]), int(support[1])
    if left == right:
        raise ValueError(f"support pair must be distinct: {support!r}")
    return (left, right) if left < right else (right, left)


def rotated_supports_for(supports: set[tuple[int, int]], factor_base_size: int) -> set[tuple[int, int]]:
    rotated = set()
    fb_size = int(factor_base_size)
    for support in supports:
        raw = ((int(support[0]) + 1) % fb_size, (int(support[1]) + 3) % fb_size)
        if raw[0] == raw[1]:
            continue
        rotated.add(canonical_support(raw))
    return rotated


def all_support_pairs(factor_base_size: int) -> set[tuple[int, int]]:
    return {tuple(pair) for pair in combinations(range(int(factor_base_size)), 2)}


def policy_kind(policy_name: str) -> str:
    return {
        "all_pair_first_hit_control": "all_pair_first_hit_control",
        "requested_support_prehit": "requested_support_pre_hit_constructor",
        "rotated_support_prehit": "rotated_support_pre_hit_control",
    }[policy_name]


def policy_support_sets(
    trained_by_budget: dict[int, dict[tuple[int, int, int, int], dict[str, Any]]],
    budgets: list[int],
    factor_base_size: int,
) -> dict[tuple[int, str], set[tuple[int, int]]]:
    full_pairs = all_support_pairs(factor_base_size)
    out: dict[tuple[int, str], set[tuple[int, int]]] = {}
    for budget in budgets:
        requested = {canonical_support((int(key[0]), int(key[1]))) for key in trained_by_budget[int(budget)]}
        out[(int(budget), "requested_support_prehit")] = requested
        out[(int(budget), "rotated_support_prehit")] = rotated_supports_for(requested, factor_base_size)
        out[(int(budget), "all_pair_first_hit_control")] = full_pairs
    return out


def build_point_policy_map(
    verifier: Any,
    factor_base: list[Any],
    ainvs: list[int],
    p: int,
    supports_by_policy: dict[tuple[int, str], set[tuple[int, int]]],
) -> tuple[dict[Any, dict[tuple[int, str], tuple[int, int]]], dict[tuple[int, str], dict[str, int]]]:
    point_policy: dict[Any, dict[tuple[int, str], tuple[int, int]]] = defaultdict(dict)
    stats: dict[tuple[int, str], dict[str, int]] = {}
    for policy_key, supports in supports_by_policy.items():
        seen_points = set()
        collisions = 0
        for support in sorted(supports):
            point = support_sum(verifier, factor_base, support, ainvs, p)
            if point in seen_points:
                collisions += 1
            seen_points.add(point)
            point_policy[point].setdefault(policy_key, support)
        stats[policy_key] = {
            "targeted_setup_group_additions": len(supports),
            "targeted_support_count": len(supports),
            "targeted_unique_point_count": len(seen_points),
            "targeted_point_collision_count": collisions,
        }
    return dict(point_policy), stats


def cost_model(p748: Any, order: int, walk: dict[str, Any], attempted_trials: int, setup_additions: int) -> dict[str, Any]:
    online = p748.group_cost(max(1, int(order).bit_length()), int(walk["delta_setup_group_additions"]), int(attempted_trials))
    return {
        "collection_online_group_additions": online,
        "constructor_one_shot_group_additions": int(setup_additions) + online,
        "delta_setup_group_additions": int(walk["delta_setup_group_additions"]),
        "initial_mixed_group_additions": (2 * max(1, int(order).bit_length())) + 1,
        "targeted_setup_group_additions": int(setup_additions),
    }


def base_row(
    p748: Any,
    target: str,
    seed_label: str,
    full_seed: str,
    challenge: dict[str, Any],
    secret: int,
    order: int,
    factor_base_size: int,
    walk: dict[str, Any],
    configured_trials: int,
    attempted_trials: int,
    setup_additions: int,
) -> dict[str, Any]:
    rho = int(challenge["generic_rho_steps"])
    online = cost_model(p748, order, walk, attempted_trials, setup_additions)
    return {
        "_expected_secret": int(secret),
        "accepted_mixed_relations": 0,
        "configured_trials": int(configured_trials),
        "cost_model": online,
        "decomposition_hits": 0,
        "derived": False,
        "early_public": {
            "accepted_mixed_relations": 0,
            "decomposition_hits": 0,
            "mixed_wide_relation_rank": 0,
            "observed_decomposition_rate": 0.0,
            "scanned_trials": int(attempted_trials),
            "zero_b_skips": 0,
        },
        "factor_base_size": int(factor_base_size),
        "forms": [],
        "generic_rho_steps": rho,
        "improvement_ratios": {
            "collection_online_group_additions_over_rho": ratio(online["collection_online_group_additions"], rho),
            "constructor_one_shot_group_additions_over_rho": ratio(online["constructor_one_shot_group_additions"], rho),
        },
        "matrix_challenge_id": f"{target}:{seed_label}",
        "mixed_wide_relation_rank": 0,
        "observed_decomposition_rate": 0.0,
        "policy_key": {
            "factor_base_size": int(factor_base_size),
            "subset_width": 2,
            "walk_mode": str(walk["mode"]),
        },
        "relation_trials": int(attempted_trials),
        "scanned_trials": int(attempted_trials),
        "seed": full_seed,
        "seed_label": seed_label,
        "subset_count": int(setup_additions),
        "subset_sum_collisions": 0,
        "subset_unique_sums": int(setup_additions),
        "subset_width": 2,
        "target": target,
        "targeted_point_hits": 0,
        "trials_to_derive_secret": None,
        "walk": {
            "delta_option_count": len(walk["delta_options"]),
            "mode": str(walk["mode"]),
            "scheduled": bool(walk["scheduled"]),
        },
        "zero_b_hits": 0,
        "zero_b_skips": 0,
    }


def hit_row(
    p748: Any,
    verifier: Any,
    target: str,
    seed_label: str,
    full_seed: str,
    challenge: dict[str, Any],
    secret: int,
    order: int,
    factor_base_size: int,
    walk: dict[str, Any],
    configured_trials: int,
    attempted_trials: int,
    setup_additions: int,
    relation: dict[str, Any],
    terms: list[int],
) -> dict[str, Any]:
    coeffs, rhs = verifier.relation_linear_form(relation, terms, challenge, int(order))
    row = base_row(
        p748,
        target,
        seed_label,
        full_seed,
        challenge,
        secret,
        order,
        factor_base_size,
        walk,
        configured_trials,
        attempted_trials,
        setup_additions,
    )
    row["accepted_mixed_relations"] = 1
    row["decomposition_hits"] = 1
    row["early_public"] = {
        **row["early_public"],
        "accepted_mixed_relations": 1,
        "decomposition_hits": 1,
        "mixed_wide_relation_rank": 1,
        "observed_decomposition_rate": ratio(1, attempted_trials) or 0.0,
    }
    row["forms"] = [
        {
            "a": int(relation["a"]),
            "b": int(relation["b"]),
            "coeffs": [int(value) for value in coeffs],
            "form_index": 0,
            "rhs": int(rhs),
            "terms": [int(term) for term in terms],
            "trial": int(attempted_trials),
        }
    ]
    row["mixed_wide_relation_rank"] = 1
    row["observed_decomposition_rate"] = ratio(1, attempted_trials) or 0.0
    row["targeted_point_hits"] = 1
    return row


def scan_seed_for_policies(
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
    budgets: list[int],
    point_policy: dict[Any, dict[tuple[int, str], tuple[int, int]]],
    policy_stats: dict[tuple[int, str], dict[str, int]],
    args: argparse.Namespace,
) -> dict[tuple[int, str], dict[str, Any]]:
    max_budget = max(int(value) for value in budgets)
    walk = p746.walk_schedule(verifier, str(args.walk_mode), base, public, ainvs, p)
    a, b = p746.deterministic_start(int(order), full_seed, str(args.walk_mode))
    lhs = verifier.add_points(verifier.mul_point(a, base, ainvs, p), verifier.mul_point(b, public, ainvs, p), ainvs, p)
    hits: dict[tuple[int, str], dict[str, Any]] = {}
    zero_b_hits = Counter()

    for trial in range(1, max_budget + 1):
        entries = point_policy.get(lhs) or {}
        if entries:
            for policy_key, support in entries.items():
                budget, _policy_name = policy_key
                if trial > int(budget) or policy_key in hits:
                    continue
                if b % int(order) == 0:
                    zero_b_hits[policy_key] += 1
                    continue
                relation = {"a": int(a), "b": int(b), "indices": [int(support[0]), int(support[1])]}
                terms = verifier.relation_terms(relation, challenge, ainvs, p)
                if terms is None or not verifier.verify_relation(relation, challenge, ainvs, p, base, public):
                    continue
                hits[policy_key] = hit_row(
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
                    int(budget),
                    trial,
                    int(policy_stats[policy_key]["targeted_setup_group_additions"]),
                    relation,
                    terms,
                )
        if len(hits) == len(policy_stats) or trial == max_budget:
            break
        delta = p746.select_delta(walk, full_seed, trial, a, b)
        a = (a + int(delta["da"])) % int(order)
        b = (b + int(delta["db"])) % int(order)
        lhs = verifier.add_points(lhs, delta["delta"], ainvs, p)

    rows = {}
    for policy_key, stats in policy_stats.items():
        budget, _policy_name = policy_key
        if policy_key in hits:
            row = hits[policy_key]
        else:
            row = base_row(
                p748,
                target,
                seed_label,
                full_seed,
                challenge,
                secret,
                order,
                factor_base_size,
                walk,
                int(budget),
                int(budget),
                int(stats["targeted_setup_group_additions"]),
            )
        row["_p801_policy"] = {
            "budget": int(budget),
            "policy": policy_key[1],
            "targeted_support_count": int(stats["targeted_support_count"]),
            "targeted_unique_point_count": int(stats["targeted_unique_point_count"]),
        }
        row["zero_b_hits"] = int(zero_b_hits.get(policy_key) or 0)
        row["zero_b_skips"] = int(zero_b_hits.get(policy_key) or 0)
        rows[policy_key] = row
    return rows


def collect_targeted_rows(
    p746: Any,
    p748: Any,
    relprobe: Any,
    base_item: dict[str, Any],
    trained_by_budget: dict[int, dict[tuple[int, int, int, int], dict[str, Any]]],
    budgets: list[int],
    case: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[dict[tuple[int, str], list[dict[str, Any]]], dict[tuple[int, str], dict[str, int]], int]:
    verifier, record, inv = p746.load_target(relprobe, str(base_item["target"]))
    ainvs = record["ainvs"]
    p = int(inv["p"])
    order = int(inv["base_order"])
    factor_base_size = int(case["factor_base_size"])
    sample_seed = (
        f"ecdlp-p801-{args.constructor_namespace}-{slug(base_item['target'])}:sample:"
        f"fb{factor_base_size}:w2:{args.walk_mode}"
    )
    sample_challenge, _sample_secret = relprobe.make_challenge(verifier, inv, ainvs, sample_seed, factor_base_size)
    factor_base = [
        verifier.point_from_json(point)
        for point in sample_challenge["factor_base"][: max(1, min(factor_base_size, len(sample_challenge["factor_base"])))]
    ]
    supports_by_policy = policy_support_sets(trained_by_budget, budgets, len(factor_base))
    point_policy, policy_stats = build_point_policy_map(verifier, factor_base, ainvs, p, supports_by_policy)
    rows_by_policy = {policy_key: [] for policy_key in policy_stats}
    for seed_label in seed_labels(int(args.scan_seed_count)):
        full_seed = (
            f"ecdlp-p801-{args.constructor_namespace}-{slug(base_item['target'])}:"
            f"{seed_label}:fb{factor_base_size}:w2:{args.walk_mode}"
        )
        challenge, secret = relprobe.make_challenge(verifier, inv, ainvs, full_seed, factor_base_size)
        base = verifier.point_from_json(challenge["base"])
        public = verifier.point_from_json(challenge["public"])
        rows = scan_seed_for_policies(
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
            budgets,
            point_policy,
            policy_stats,
            args,
        )
        for policy_key, row in rows.items():
            rows_by_policy[policy_key].append(row)
    return rows_by_policy, policy_stats, order


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


def determine_policy_claim(policy_result: dict[str, Any], peer_results: dict[str, dict[str, Any]]) -> str:
    aggregate = policy_result["aggregate"]
    name = policy_result["policy"]["name"]
    if int(aggregate["hit_row_count"]) == 0:
        return "no_targeted_hits"
    if int(aggregate["recovered_row_count"]) <= int(aggregate["max_control_recovered_row_count"]):
        return "does_not_beat_rotated_line_controls"
    ratio_value = aggregate["generated_once_train_total_unit_cost_over_recovered_rho"] or 10**9
    rotated_recovered = int((peer_results.get("rotated_support_prehit") or {}).get("aggregate", {}).get("recovered_row_count") or 0)
    if name == "requested_support_prehit" and int(aggregate["recovered_row_count"]) > rotated_recovered and ratio_value < 1.0:
        return "requested_support_prehit_below_rho"
    if name == "requested_support_prehit" and int(aggregate["recovered_row_count"]) > rotated_recovered:
        return "requested_support_prehit_enrichment_cost_boundary"
    if name in {"rotated_support_prehit", "all_pair_first_hit_control"}:
        return "control_boundary"
    return "cost_boundary"


def determine_claim(summary: dict[str, Any]) -> str:
    claims = [
        policy_result["policy_claim"]
        for budget_result in summary["budget_results"]
        for policy_result in budget_result["policy_results"]
    ]
    if "requested_support_prehit_below_rho" in claims:
        return "P801_REQUESTED_SUPPORT_PREHIT_BELOW_RHO_SIGNAL"
    if "requested_support_prehit_enrichment_cost_boundary" in claims:
        return "P801_REQUESTED_SUPPORT_PREHIT_ENRICHMENT_COST_BOUNDARY"
    return "NEGATIVE_RESULT_P801_PREHIT_SUPPORT_PAIR_NO_GENERATOR"


def best_result(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    viable = [
        item
        for item in items
        if item["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"] is not None
    ]
    if not viable:
        return None
    item = min(viable, key=lambda row: row["aggregate"]["generated_once_train_total_unit_cost_over_recovered_rho"])
    aggregate = item["aggregate"]
    return {
        "generated_once_train_total_unit_cost_over_recovered_rho": aggregate["generated_once_train_total_unit_cost_over_recovered_rho"],
        "generated_row_count": aggregate["generated_row_count"],
        "hit_row_count": aggregate["hit_row_count"],
        "hit_row_rate_over_generated": aggregate["hit_row_rate_over_generated"],
        "policy": item["policy"]["name"],
        "policy_claim": item["policy_claim"],
        "recovered_row_count": aggregate["recovered_row_count"],
        "targeted_support_count": aggregate["targeted_support_count"],
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    if int(args.width) != 2:
        raise ValueError("P801 is a width-2 support-pair constructor; use --width 2")
    p800 = load_module("ecdlp_p800_for_p801", P800_SCRIPT)
    p799 = p800.load_module("ecdlp_p799_for_p801", p800.P799_SCRIPT)
    p798 = p799.load_module("ecdlp_p798_for_p801", p799.P798_SCRIPT)
    p797 = p798.load_module("ecdlp_p797_for_p801", p798.P797_SCRIPT)
    p796 = p797.load_module("ecdlp_p796_for_p801", p797.P796_SCRIPT)
    p795 = p796.load_module("ecdlp_p795_for_p801", p796.P795_SCRIPT)
    p794 = p795.load_module("ecdlp_p794_for_p801", p795.P794_SCRIPT)
    p793 = p794.load_module("ecdlp_p793_for_p801", p794.P793_SCRIPT)
    p792 = p793.load_module("ecdlp_p792_for_p801", p793.P792_SCRIPT)
    p789 = p792.load_module("ecdlp_p789_for_p801", p792.P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p801", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p801", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p801", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p801", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p801", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p801", p782.P780_SCRIPT)
    stack = p780.load_stack()
    p746 = stack["p746"]
    p748 = stack["p748"]
    relprobe = stack["relprobe"]
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({item["dest_group_key"] for item in frozen_pairs})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    budgets = csv_ints(args.budgets)

    train_args = p795.namespace_args(args, args.train_seed_namespace, int(args.train_replicas))
    print(f"preparing train namespace {args.train_seed_namespace}", flush=True)
    train_prepared = {
        key: p794.prepare_target(p793, p792, p789, p787, p784, stack, base_groups[key], train_args)
        for key in required
    }
    trained_by_group_budget = {
        group_key: {
            int(budget): p794.selected_calibrations(train_prepared[group_key]["all_calibrated"], int(budget))
            for budget in budgets
        }
        for group_key in required
    }

    scan_bank = {}
    for group_key in required:
        case = p784.case_from_group(
            base_groups[group_key],
            p784.TRIM12_DELTA,
            args.constructor_namespace,
            "p801",
            p784.DEST_SEED_COUNT,
            p784.DEST_POOL_COUNT,
        )
        print(f"targeted scanning {group_key} rows={args.scan_seed_count}", flush=True)
        rows_by_policy, policy_stats, order = collect_targeted_rows(
            p746,
            p748,
            relprobe,
            base_groups[group_key],
            trained_by_group_budget[group_key],
            budgets,
            case,
            args,
        )
        scan_bank[group_key] = {
            "order": order,
            "policy_stats": policy_stats,
            "rows_by_policy": rows_by_policy,
        }

    budget_results = []
    all_policy_results = []
    for budget in budgets:
        print(f"scoring budget {budget}", flush=True)
        target_policy_results = {name: [] for name in POLICY_NAMES}
        for group_key in required:
            for policy_name in POLICY_NAMES:
                policy_key = (int(budget), policy_name)
                target_policy_results[policy_name].append(
                    evaluate_policy(
                        p797,
                        p793,
                        p792,
                        p789,
                        train_prepared[group_key],
                        trained_by_group_budget[group_key][int(budget)],
                        scan_bank[group_key]["rows_by_policy"][policy_key],
                        int(scan_bank[group_key]["order"]),
                        str(base_groups[group_key]["target"]),
                        policy_name,
                        scan_bank[group_key]["policy_stats"][policy_key],
                        args,
                    )
                )
        policy_results = []
        for policy_name in POLICY_NAMES:
            policy_results.append(aggregate_policy_results(target_policy_results[policy_name], policy_name))
        by_name = {item["policy"]["name"]: item for item in policy_results}
        for item in policy_results:
            item["budget"] = int(budget)
            item["policy_claim"] = determine_policy_claim(item, by_name)
            all_policy_results.append(item)
        budget_results.append(
            {
                "best_generated": best_result(policy_results),
                "budget": int(budget),
                "policy_results": policy_results,
            }
        )
    summary = {
        "best_generated": best_result(all_policy_results),
        "budget_results": budget_results,
        "constructor_namespace": args.constructor_namespace,
        "scan_seed_count": args.scan_seed_count,
        "train_seed_namespace": args.train_seed_namespace,
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p800_script": str(P800_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PRE-HIT MODEL: support pairs are selected before walk membership is tested, and each row stops at first targeted hit or failure budget.",
            "NO FACTOR LOGS: target tables use public factor-base point sums, not factor discrete logs or target scalar.",
            "CONTROL-BOUND: rotated support-pair tables and all-pair first-hit tables test whether requested supports add value beyond table size and generic two-factor hits.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p801_pre_hit_support_pair_constructor",
        "parameters": {
            "budgets": budgets,
            "constructor_namespace": args.constructor_namespace,
            "control_count": args.control_count,
            "field_weight": args.field_weight,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "min_line_rows": args.min_line_rows,
            "row_policy": args.row_policy,
            "scan_seed_count": args.scan_seed_count,
            "sparse_policies": args.sparse_policies,
            "train_replicas": args.train_replicas,
            "train_seed_namespace": args.train_seed_namespace,
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact_budget_results = []
    for budget_result in payload["summary"]["budget_results"]:
        compact_policies = []
        for item in budget_result["policy_results"]:
            aggregate = item["aggregate"]
            compact_policies.append(
                {
                    "aggregate": {
                        "generated_once_train_total_unit_cost_over_recovered_rho": aggregate[
                            "generated_once_train_total_unit_cost_over_recovered_rho"
                        ],
                        "generated_row_count": aggregate["generated_row_count"],
                        "hit_row_count": aggregate["hit_row_count"],
                        "hit_row_rate_over_generated": aggregate["hit_row_rate_over_generated"],
                        "max_control_recovered_row_count": aggregate["max_control_recovered_row_count"],
                        "primary_minus_max_control_recovered_rows": aggregate["primary_minus_max_control_recovered_rows"],
                        "recovered_row_count": aggregate["recovered_row_count"],
                        "recovered_row_rate_over_hit": aggregate["recovered_row_rate_over_hit"],
                        "targeted_setup_group_additions": aggregate["targeted_setup_group_additions"],
                        "targeted_support_count": aggregate["targeted_support_count"],
                        "targeted_unique_point_count": aggregate["targeted_unique_point_count"],
                    },
                    "policy": item["policy"],
                    "policy_claim": item["policy_claim"],
                }
            )
        compact_budget_results.append(
            {
                "best_generated": budget_result["best_generated"],
                "budget": budget_result["budget"],
                "policy_results": compact_policies,
            }
        )
    return {
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "schema": f"{SCHEMA}.summary",
        "summary": {
            **payload["summary"],
            "budget_results": compact_budget_results,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--train-seed-namespace", default="supportline20-v1")
    parser.add_argument("--constructor-namespace", default="prehitpair-v1")
    parser.add_argument("--train-replicas", type=int, default=20)
    parser.add_argument("--scan-seed-count", type=int, default=512)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--field-weight", type=int, default=2)
    parser.add_argument("--min-line-rows", type=int, default=2)
    parser.add_argument("--budgets", default=DEFAULT_BUDGETS)
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
                "best_generated": summary["summary"]["best_generated"],
                "budget_best": [
                    {
                        "best": item["best_generated"],
                        "budget": item["budget"],
                    }
                    for item in summary["summary"]["budget_results"]
                ],
                "claim_status": summary["claim_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
