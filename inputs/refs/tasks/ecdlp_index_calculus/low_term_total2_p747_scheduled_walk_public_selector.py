#!/usr/bin/env python3
"""P747 public-selector validation for order-11779 scheduled walks.

P746 found amortized-online below-rho derivations after a scheduled-walk seed
extension. This probe tests whether that component survives a public selector:
choose a (factor-base size, width, walk mode) policy from early public hit/rank
features on even seeds, then evaluate odd seeds and a second order-11779 target.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P746_SCRIPT = TASK_DIR / "low_term_total2_p746_incremental_walk_online_cost.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p747_scheduled_walk_public_selector_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p747_scheduled_walk_public_selector.md"
DEFAULT_P746_SUMMARY = STATE_DIR / "low_term_total2_p746_incremental_walk_online_cost_scheduled_seed_extension_summary.json"
DEFAULT_TRAIN_TARGET = "67.a1@11789"
DEFAULT_SECOND_TARGET = "22050.cf1@11731"
SCHEMA = "ecdlp.low_term_total2_p747_scheduled_walk_public_selector.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def load_p746_module() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_p746_incremental_walk", P746_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import P746 helper from {P746_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_csv_ints(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def parse_csv_strings(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def seed_index(seed_label: str) -> int:
    match = re.search(r"(\d+)$", seed_label)
    if not match:
        raise ValueError(f"seed label must end in digits for split discipline: {seed_label!r}")
    return int(match.group(1))


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "median": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "median": median(values),
        "min": min(values),
    }


def public_rank_probe(relprobe: Any, verifier: Any, forms: list[tuple[Any, int, list[int]]], order: int) -> dict[str, Any]:
    if not forms:
        return {"mixed_wide_relation_rank": 0, "mixed_wide_relations_derive_secret": False, "derived_secret": None}
    return relprobe.linear_rank_probe(verifier, forms, order)


def amortization_threshold(subset_group_additions: int, online_group_additions: int, rho: int) -> int | None:
    margin = rho - online_group_additions
    if margin <= 0:
        return None
    return int(math.ceil(subset_group_additions / margin))


def scan_public_walk(
    p746: Any,
    relprobe: Any,
    verifier: Any,
    record: dict[str, Any],
    inv: dict[str, Any],
    target: str,
    factor_base_size: int,
    width: int,
    mode: str,
    seed_label: str,
    full_seed: str,
    trials: int,
    early_budget: int,
    max_relations: int,
    max_subsets: int,
) -> dict[str, Any]:
    ainvs = record["ainvs"]
    p = int(inv["p"])
    order = int(inv["base_order"])
    challenge, secret = relprobe.make_challenge(verifier, inv, ainvs, full_seed, factor_base_size)
    base = verifier.point_from_json(challenge["base"])
    public = verifier.point_from_json(challenge["public"])
    full_factor_base = [verifier.point_from_json(point) for point in challenge["factor_base"]]
    factor_base = full_factor_base[: max(1, min(factor_base_size, len(full_factor_base)))]

    subset_table, subset_count, subset_collisions = relprobe.build_subset_table(
        verifier,
        factor_base,
        ainvs,
        p,
        width,
        max_subsets,
    )
    walk = p746.walk_schedule(verifier, mode, base, public, ainvs, p)
    initial_a, initial_b = p746.deterministic_start(order, full_seed, mode)
    a, b = initial_a, initial_b
    lhs = verifier.add_points(
        verifier.mul_point(a, base, ainvs, p),
        verifier.mul_point(b, public, ainvs, p),
        ainvs,
        p,
    )

    forms: list[tuple[Any, int, list[int]]] = []
    seen_forms: set[tuple[Any, int]] = set()
    relations: list[dict[str, Any]] = []
    hits = 0
    first_hit_at = None
    zero_b_hits = 0
    zero_b_skips = 0
    derived_at = None
    derived = {"mixed_wide_relations_derive_secret": False, "mixed_wide_relation_rank": 0, "derived_secret": None}
    early_snapshot: dict[str, Any] | None = None
    attempted_trials = 0
    started = time.monotonic()

    for trial in range(1, trials + 1):
        attempted_trials = trial
        indices = subset_table.get(lhs)
        if indices is not None:
            hits += 1
            first_hit_at = first_hit_at or trial
            if b % order == 0:
                zero_b_hits += 1
                zero_b_skips += 1
            else:
                relation = {"a": int(a), "b": int(b), "indices": [int(index) for index in indices]}
                terms = verifier.relation_terms(relation, challenge, ainvs, p)
                if terms is not None and verifier.verify_relation(relation, challenge, ainvs, p, base, public):
                    coeffs, rhs = verifier.relation_linear_form(relation, terms, challenge, order)
                    key = (coeffs, rhs)
                    if key not in seen_forms:
                        seen_forms.add(key)
                        relations.append(relation)
                        forms.append((coeffs, rhs, terms))
                        if len(relations) >= 8:
                            current = relprobe.linear_rank_probe(verifier, forms, order)
                            if current["mixed_wide_relations_derive_secret"]:
                                derived = current
                                derived_at = derived_at or trial
                        if len(relations) >= max_relations and trial >= early_budget:
                            break

        if trial == early_budget:
            early_rank = public_rank_probe(relprobe, verifier, forms, order)
            early_snapshot = {
                "accepted_mixed_relations": len(relations),
                "decomposition_hits": hits,
                "mixed_wide_relation_rank": int(early_rank["mixed_wide_relation_rank"]),
                "observed_decomposition_rate": round(hits / trial, 6),
                "scanned_trials": trial,
                "zero_b_skips": zero_b_skips,
            }

        if derived_at is not None and trial >= early_budget:
            break
        if trial == trials:
            break

        delta = p746.select_delta(walk, full_seed, trial, a, b)
        a = (a + int(delta["da"])) % order
        b = (b + int(delta["db"])) % order
        lhs = verifier.add_points(lhs, delta["delta"], ainvs, p)

    if early_snapshot is None:
        early_rank = public_rank_probe(relprobe, verifier, forms, order)
        divisor = max(1, attempted_trials)
        early_snapshot = {
            "accepted_mixed_relations": len(relations),
            "decomposition_hits": hits,
            "mixed_wide_relation_rank": int(early_rank["mixed_wide_relation_rank"]),
            "observed_decomposition_rate": round(hits / divisor, 6),
            "scanned_trials": attempted_trials,
            "zero_b_skips": zero_b_skips,
        }

    if not derived["mixed_wide_relations_derive_secret"]:
        derived = public_rank_probe(relprobe, verifier, forms, order)
        if derived["mixed_wide_relations_derive_secret"]:
            derived_at = attempted_trials

    elapsed = round(time.monotonic() - started, 6)
    rho = int(challenge["generic_rho_steps"])
    bit_length = max(1, order.bit_length())
    initial_mixed_group_additions = (2 * bit_length) + 1
    delta_setup_group_additions = int(walk["delta_setup_group_additions"])
    trials_for_cost = derived_at if derived_at is not None else attempted_trials
    updates_for_cost = max(0, int(trials_for_cost) - 1)
    walk_update_group_additions = updates_for_cost * int(walk["walk_update_group_additions"])
    online_group_additions = initial_mixed_group_additions + delta_setup_group_additions + walk_update_group_additions
    subset_group_additions = subset_count * max(0, width - 1)
    one_shot_group_additions = subset_group_additions + online_group_additions
    naive_independent_group_additions = int(trials_for_cost) * 2 * bit_length
    coverage = len(subset_table) / max(1, order)
    derived_ok = bool(derived["mixed_wide_relations_derive_secret"] and derived["derived_secret"] == secret)

    return {
        "accepted_mixed_relations": len(relations),
        "actual_subset_coverage": round(coverage, 6),
        "configured_trials": trials,
        "cost_model": {
            "amortization_threshold_challenges": amortization_threshold(
                subset_group_additions,
                online_group_additions,
                rho,
            ),
            "cost_caveat": (
                "Online walk cost counts the initial mixed point, public walk-delta setup, and one "
                "group addition per subsequent trial. One-shot cost also counts subset precomputation."
            ),
            "delta_setup_group_additions": delta_setup_group_additions,
            "initial_mixed_group_additions": initial_mixed_group_additions,
            "naive_independent_group_additions": naive_independent_group_additions,
            "online_group_additions": online_group_additions,
            "online_group_additions_beats_rho": online_group_additions < rho,
            "one_shot_group_additions": one_shot_group_additions,
            "one_shot_group_additions_beats_rho": one_shot_group_additions < rho,
            "subset_group_additions": subset_group_additions,
            "walk_update_group_additions": walk_update_group_additions,
        },
        "decomposition_hits": hits,
        "derived": derived_ok,
        "elapsed_seconds": elapsed,
        "early_public": early_snapshot,
        "factor_base_size": len(factor_base),
        "generic_rho_steps": rho,
        "improvement_ratios": {
            "naive_independent_group_additions_over_rho": ratio(naive_independent_group_additions, rho),
            "online_group_additions_over_rho": ratio(online_group_additions, rho),
            "one_shot_group_additions_over_rho": ratio(one_shot_group_additions, rho),
            "relation_trials_over_rho": ratio(trials_for_cost, rho),
            "subset_additions_over_rho": ratio(subset_group_additions, rho),
        },
        "max_relations": max_relations,
        "max_subsets": max_subsets,
        "mixed_wide_relation_rank": int(derived["mixed_wide_relation_rank"]),
        "observed_decomposition_rate": round(hits / max(1, attempted_trials), 6),
        "policy_key": {
            "factor_base_size": len(factor_base),
            "subset_width": width,
            "walk_mode": mode,
        },
        "relation_trials": int(trials_for_cost),
        "scanned_trials": attempted_trials,
        "seed": full_seed,
        "seed_label": seed_label,
        "subset_count": subset_count,
        "subset_sum_collisions": subset_collisions,
        "subset_unique_sums": len(subset_table),
        "subset_width": width,
        "target": target,
        "trials_to_derive_secret": derived_at,
        "walk": {
            "delta_option_count": len(walk["delta_options"]),
            "initial_a": int(initial_a),
            "initial_b": int(initial_b),
            "mode": mode,
            "scheduled": bool(walk["scheduled"]),
            "step_a": None if walk["scheduled"] else int(walk["delta_options"][0]["da"]),
            "step_b": None if walk["scheduled"] else int(walk["delta_options"][0]["db"]),
        },
        "zero_b_hits": zero_b_hits,
        "zero_b_skips": zero_b_skips,
    }


def policy_tuple(row: dict[str, Any]) -> tuple[int, int, str]:
    key = row["policy_key"]
    return (int(key["factor_base_size"]), int(key["subset_width"]), str(key["walk_mode"]))


def mode_tiebreak(mode: str) -> int:
    return 1 if mode == "hash6" else 0


def aggregate_public_policy_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[policy_tuple(row)].append(row)

    aggregates: list[dict[str, Any]] = []
    for (factor_base_size, width, mode), group_rows in grouped.items():
        early = [row["early_public"] for row in group_rows]
        setup_values = [row["cost_model"]["subset_group_additions"] for row in group_rows]
        coverage_values = [row["actual_subset_coverage"] for row in group_rows]
        aggregate = {
            "factor_base_size": factor_base_size,
            "mean_early_accepted_mixed_relations": round(mean(item["accepted_mixed_relations"] for item in early), 8),
            "mean_early_decomposition_hits": round(mean(item["decomposition_hits"] for item in early), 8),
            "mean_early_observed_decomposition_rate": round(mean(item["observed_decomposition_rate"] for item in early), 8),
            "mean_early_rank": round(mean(item["mixed_wide_relation_rank"] for item in early), 8),
            "mean_setup_group_additions": round(mean(setup_values), 8),
            "mean_subset_coverage": round(mean(coverage_values), 8),
            "mode_tiebreak": mode_tiebreak(mode),
            "policy_key": {
                "factor_base_size": factor_base_size,
                "subset_width": width,
                "walk_mode": mode,
            },
            "row_count": len(group_rows),
            "subset_width": width,
            "walk_mode": mode,
        }
        aggregate["public_selector_score"] = [
            aggregate["mean_early_rank"],
            aggregate["mean_early_accepted_mixed_relations"],
            aggregate["mean_early_decomposition_hits"],
            aggregate["mean_subset_coverage"],
            -aggregate["mean_setup_group_additions"],
            aggregate["mode_tiebreak"],
        ]
        aggregates.append(aggregate)

    aggregates.sort(
        key=lambda item: (
            item["mean_early_rank"],
            item["mean_early_accepted_mixed_relations"],
            item["mean_early_decomposition_hits"],
            item["mean_subset_coverage"],
            -item["mean_setup_group_additions"],
            item["mode_tiebreak"],
            item["factor_base_size"],
        ),
        reverse=True,
    )
    return aggregates


def derived_sort_key(row: dict[str, Any]) -> tuple[float, float, int, int, str]:
    ratios = row.get("improvement_ratios") or {}
    online = ratios.get("online_group_additions_over_rho")
    one_shot = ratios.get("one_shot_group_additions_over_rho")
    return (
        float(online) if online is not None else 10**18,
        float(one_shot) if one_shot is not None else 10**18,
        int(row.get("relation_trials") or 10**9),
        int(row.get("factor_base_size") or 10**9),
        str(row.get("seed")),
    )


def row_beats_online(row: dict[str, Any]) -> bool:
    return bool(row.get("derived") and row["cost_model"]["online_group_additions_beats_rho"])


def row_beats_one_shot(row: dict[str, Any]) -> bool:
    return bool(row.get("derived") and row["cost_model"]["one_shot_group_additions_beats_rho"])


def summarize_rows(rows: list[dict[str, Any]], label: str) -> dict[str, Any]:
    derived_rows = [row for row in rows if row.get("derived")]
    derived_rows.sort(key=derived_sort_key)
    online_wins = [row for row in derived_rows if row_beats_online(row)]
    one_shot_wins = [row for row in derived_rows if row_beats_one_shot(row)]
    thresholds = [
        row["cost_model"]["amortization_threshold_challenges"]
        for row in online_wins
        if row["cost_model"]["amortization_threshold_challenges"] is not None
    ]
    return {
        "best_derived_by_online_group_cost": derived_rows[0] if derived_rows else None,
        "derived_count": len(derived_rows),
        "derived_online_ratio_stats": stat(
            [
                row["improvement_ratios"]["online_group_additions_over_rho"]
                for row in derived_rows
                if row["improvement_ratios"]["online_group_additions_over_rho"] is not None
            ]
        ),
        "derived_one_shot_ratio_stats": stat(
            [
                row["improvement_ratios"]["one_shot_group_additions_over_rho"]
                for row in derived_rows
                if row["improvement_ratios"]["one_shot_group_additions_over_rho"] is not None
            ]
        ),
        "label": label,
        "nonderived_count": len(rows) - len(derived_rows),
        "online_below_rho_count": len(online_wins),
        "one_shot_below_rho_count": len(one_shot_wins),
        "row_count": len(rows),
        "setup_amortization_threshold_stats": stat(thresholds),
        "top_derived_by_online_group_cost": derived_rows[:8],
    }


def selected_policy_matches(row: dict[str, Any], selected: dict[str, Any]) -> bool:
    key = row["policy_key"]
    return (
        int(key["factor_base_size"]) == int(selected["factor_base_size"])
        and int(key["subset_width"]) == int(selected["subset_width"])
        and str(key["walk_mode"]) == str(selected["walk_mode"])
    )


def claim_status(same_target: dict[str, Any], second_target: dict[str, Any]) -> str:
    if same_target["one_shot_below_rho_count"] > 0 or second_target["one_shot_below_rho_count"] > 0:
        return "P747_PUBLIC_SELECTOR_ONE_SHOT_BELOW_RHO_SIGNAL"
    if same_target["online_below_rho_count"] > 0 and second_target["online_below_rho_count"] > 0:
        return "P747_PUBLIC_SELECTOR_CROSS_TARGET_ONLINE_SIGNAL_ONE_SHOT_ABOVE_RHO"
    if same_target["online_below_rho_count"] > 0:
        return "P747_PUBLIC_SELECTOR_HELDOUT_ONLINE_SIGNAL_TARGET_BOUND"
    if same_target["derived_count"] > 0 or second_target["derived_count"] > 0:
        return "P747_PUBLIC_SELECTOR_DERIVES_ABOVE_RHO_OR_CROSS_TARGET_ONLY"
    return "NEGATIVE_RESULT_P747_SELECTED_POLICY_NO_HELDOUT_DERIVATION"


def target_context(p746: Any, relprobe: Any, target: str) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    return p746.load_target(relprobe, target)


def run_rows_for_target(
    p746: Any,
    relprobe: Any,
    verifier: Any,
    record: dict[str, Any],
    inv: dict[str, Any],
    target: str,
    seed_labels: list[str],
    factor_base_sizes: list[int],
    widths: list[int],
    modes: list[str],
    seed_prefix: str,
    trials: int,
    early_budget: int,
    max_relations: int,
    max_subsets: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for width in widths:
        for factor_base_size in factor_base_sizes:
            if factor_base_size < width:
                continue
            for mode in modes:
                for seed_label in seed_labels:
                    full_seed = f"{seed_prefix}:{seed_label}:fb{factor_base_size}:w{width}:{mode}"
                    rows.append(
                        scan_public_walk(
                            p746,
                            relprobe,
                            verifier,
                            record,
                            inv,
                            target,
                            factor_base_size,
                            width,
                            mode,
                            seed_label,
                            full_seed,
                            trials,
                            early_budget,
                            max_relations,
                            max_subsets,
                        )
                    )
    return rows


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p746 = load_p746_module()
    relprobe = p746.load_relation_probe_module()
    train_verifier, train_record, train_inv = target_context(p746, relprobe, args.train_target)
    second_verifier, second_record, second_inv = target_context(p746, relprobe, args.second_target)

    factor_base_sizes = parse_csv_ints(args.factor_base_sizes)
    widths = parse_csv_ints(args.widths)
    modes = parse_csv_strings(args.walk_modes)
    seed_labels = parse_csv_strings(args.seeds)
    train_seed_labels = [seed for seed in seed_labels if seed_index(seed) % 2 == 0]
    holdout_seed_labels = [seed for seed in seed_labels if seed_index(seed) % 2 == 1]

    train_rows = run_rows_for_target(
        p746,
        relprobe,
        train_verifier,
        train_record,
        train_inv,
        args.train_target,
        train_seed_labels,
        factor_base_sizes,
        widths,
        modes,
        args.seed_prefix,
        args.trials,
        args.early_budget,
        args.max_relations,
        args.max_subsets,
    )
    policy_ranking = aggregate_public_policy_rows(train_rows)
    if not policy_ranking:
        raise RuntimeError("public selector had no policies to rank")
    selected_policy = policy_ranking[0]["policy_key"]

    same_target_holdout_all_policy_rows = run_rows_for_target(
        p746,
        relprobe,
        train_verifier,
        train_record,
        train_inv,
        args.train_target,
        holdout_seed_labels,
        [selected_policy["factor_base_size"]],
        [selected_policy["subset_width"]],
        [selected_policy["walk_mode"]],
        args.seed_prefix,
        args.trials,
        args.early_budget,
        args.max_relations,
        args.max_subsets,
    )
    second_target_selected_policy_rows = run_rows_for_target(
        p746,
        relprobe,
        second_verifier,
        second_record,
        second_inv,
        args.second_target,
        seed_labels,
        [selected_policy["factor_base_size"]],
        [selected_policy["subset_width"]],
        [selected_policy["walk_mode"]],
        args.seed_prefix,
        args.trials,
        args.early_budget,
        args.max_relations,
        args.max_subsets,
    )

    train_selected_policy_rows = [row for row in train_rows if selected_policy_matches(row, selected_policy)]
    same_target_summary = summarize_rows(same_target_holdout_all_policy_rows, "same_target_odd_seed_holdout")
    second_target_summary = summarize_rows(second_target_selected_policy_rows, "second_target_all_seed_holdout")
    combined_summary = summarize_rows(
        same_target_holdout_all_policy_rows + second_target_selected_policy_rows,
        "combined_selected_policy_holdouts",
    )
    p746_summary = load_json(args.p746_summary)

    payload = {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p746_scheduled_seed_extension_summary": str(args.p746_summary),
            "script": str(Path(__file__)),
        },
        "baseline": {
            "p746_claim_status": p746_summary.get("claim_status"),
            "p746_topline": (p746_summary.get("summary") or {}).get("best_derived_by_online_group_cost"),
            "pollard_rho_baseline_steps": int(train_inv["base_order"] and math.ceil(math.sqrt(math.pi * int(train_inv["base_order"]) / 2.0))),
        },
        "claim_status": claim_status(same_target_summary, second_target_summary),
        "created_at": now_iso(),
        "grid_parameters": {
            "early_budget": args.early_budget,
            "factor_base_sizes": factor_base_sizes,
            "holdout_seed_labels": holdout_seed_labels,
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "second_target": args.second_target,
            "second_target_seed_labels": seed_labels,
            "seed_prefix": args.seed_prefix,
            "train_seed_labels": train_seed_labels,
            "train_target": args.train_target,
            "trials": args.trials,
            "walk_modes": modes,
            "widths": widths,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: relation_probe subset-table decomposition and deterministic public walks.",
            "PUBLIC-SELECTOR: policy ranking uses only early public hit/rank/coverage/setup features.",
            "AMORTIZED-ONLINE: online wins exclude reusable subset setup; one-shot setup remains charged.",
            "NO DEPLOYED-CURVE CLAIM: no sparse-linear-algebra, target-descent, or large-prime scaling result is implied.",
        ],
        "method": "p747_public_early_feature_policy_selector_for_scheduled_walks",
        "results": {
            "same_target_holdout_selected_policy_rows": same_target_holdout_all_policy_rows,
            "second_target_selected_policy_rows": second_target_selected_policy_rows,
            "train_rows": train_rows,
        },
        "schema": SCHEMA,
        "selector": {
            "policy_ranking": policy_ranking,
            "selected_policy": selected_policy,
            "selection_inputs": [
                "mean_early_rank",
                "mean_early_accepted_mixed_relations",
                "mean_early_decomposition_hits",
                "mean_subset_coverage",
                "negative_mean_setup_group_additions",
                "deterministic_hash6_tiebreak",
            ],
            "selection_not_allowed_to_use": [
                "final derived labels",
                "derived secrets",
                "final online cost",
                "held-out outcomes",
            ],
        },
        "summary": {
            "combined_selected_policy_holdouts": combined_summary,
            "same_target_holdout_selected_policy": same_target_summary,
            "second_target_selected_policy": second_target_summary,
            "selected_policy": selected_policy,
            "train_audit_selected_policy": summarize_rows(train_selected_policy_rows, "train_even_seed_selected_policy_audit"),
            "train_policy_ranking_top": policy_ranking[:8],
        },
    }
    return payload


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"{SCHEMA}.summary",
        "created_at": payload["created_at"],
        "claim_status": payload["claim_status"],
        "grid_parameters": payload["grid_parameters"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "selector": payload["selector"],
        "summary": payload["summary"],
    }


def default_seeds() -> str:
    return ",".join(f"t{index:02d}" for index in range(64))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-target", default=DEFAULT_TRAIN_TARGET)
    parser.add_argument("--second-target", default=DEFAULT_SECOND_TARGET)
    parser.add_argument("--factor-base-sizes", default="36,40,44,48")
    parser.add_argument("--widths", default="2")
    parser.add_argument("--walk-modes", default="cycle6,hash6")
    parser.add_argument("--seeds", default=default_seeds())
    parser.add_argument("--seed-prefix", default="ecdlp-p746-scheduled-seed-extension-v1")
    parser.add_argument("--trials", type=int, default=128)
    parser.add_argument("--early-budget", type=int, default=24)
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--p746-summary", type=Path, default=DEFAULT_P746_SUMMARY)
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
    selected = summary["summary"]["selected_policy"]
    same = summary["summary"]["same_target_holdout_selected_policy"]
    second = summary["summary"]["second_target_selected_policy"]
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": summary["claim_status"],
                "same_target_holdout": {
                    "derived_count": same["derived_count"],
                    "online_below_rho_count": same["online_below_rho_count"],
                    "one_shot_below_rho_count": same["one_shot_below_rho_count"],
                    "row_count": same["row_count"],
                    "setup_amortization_threshold_stats": same["setup_amortization_threshold_stats"],
                },
                "second_target": {
                    "derived_count": second["derived_count"],
                    "online_below_rho_count": second["online_below_rho_count"],
                    "one_shot_below_rho_count": second["one_shot_below_rho_count"],
                    "row_count": second["row_count"],
                    "setup_amortization_threshold_stats": second["setup_amortization_threshold_stats"],
                },
                "selected_policy": selected,
                "top_public_policy": summary["summary"]["train_policy_ranking_top"][0],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
