#!/usr/bin/env python3
"""P688 replay-weighted row selector frontier."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

import low_term_total2_p682_right207_to_right208_transition_pair_audit as p682
import low_term_total2_p685_row_level_public_pre_rank_selector as p685
import low_term_total2_p687_frontier_source_charge_replay_audit as p687
import low_term_total2_p678_right208_salt208_public_selector_audit as p678


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p688_replay_weighted_row_selector_frontier_probe.json"
DEFAULT_GATES = p682.DEFAULT_GATES
DEFAULT_P687_ARTIFACT = STATE_DIR / "low_term_total2_p687_frontier_source_charge_replay_audit_probe.json"
MAX_COMBO_SIZE = 2
MAX_UNION_SELECTORS = 4
MAX_CANDIDATES_PER_FOLD = 800
EPSILON = 1.0e-9
POLICIES = (
    "single_replay_efficiency",
    "single_replay_budget",
    "greedy_replay_efficiency_union",
    "greedy_pair_cost_union",
    "greedy_row_budget_1x_union",
    "greedy_row_budget_2x_union",
)

EXTRA_PUBLIC_FIELDS = (
    "selector_mode",
    "right_anchor_token",
    "left_salt_token",
    "row_pair",
    "leaf_signature",
    "top_k_token",
    "unique_selected_leaf_signature_count",
    "duplicate_signature_density_bucket",
    "shared_selected_leaf_product_ops",
    "direct_selected_leaf_check_ops",
    "direct_selected_leaf_product_ops",
    "shared_selected_leaf_product_saved_ops",
    "unique_signature_fraction_bucket",
    "public_gate_bool_token",
)


def selector_name(kind: str, fields: tuple[str, ...], values: tuple[str, ...]) -> str:
    return f"{kind}::" + ",".join(f"{field}={value}" for field, value in zip(fields, values))


def selector_key(fields: tuple[str, ...], row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(row.get(field)) for field in fields)


def make_field_sets(max_combo_size: int) -> list[tuple[str, tuple[str, ...]]]:
    field_sets: list[tuple[str, tuple[str, ...]]] = []
    seen: set[tuple[str, ...]] = set()
    for kind, fields in p685.ROW_PUBLIC_FIELD_SETS:
        fields_tuple = tuple(fields)
        if fields_tuple in seen:
            continue
        seen.add(fields_tuple)
        field_sets.append((kind, fields_tuple))
    for size in range(1, max_combo_size + 1):
        for fields in combinations(EXTRA_PUBLIC_FIELDS, size):
            if fields in seen:
                continue
            seen.add(fields)
            field_sets.append((f"cw{size}_" + "_".join(fields), fields))
    return field_sets


def bucket_rows(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> dict[tuple[str, ...], set[int]]:
    buckets: dict[tuple[str, ...], set[int]] = {}
    for idx, row in enumerate(rows):
        buckets.setdefault(selector_key(fields, row), set()).add(idx)
    return buckets


def make_candidates(
    rows: list[dict[str, Any]],
    train: set[int],
    field_sets: list[tuple[str, tuple[str, ...]]],
) -> tuple[list[dict[str, Any]], int]:
    train_positive = sorted(idx for idx in train if rows[idx]["row_positive"])
    candidates: dict[str, dict[str, Any]] = {}
    rejected_broad = 0
    for kind, fields in field_sets:
        buckets = bucket_rows(rows, fields)
        values_to_test = {selector_key(fields, rows[idx]) for idx in train_positive}
        for values in values_to_test:
            selected = buckets.get(values, set())
            train_selected = set(selected) & train
            training = fast_delta(train_selected, rows)
            if training["positive_row_count"] <= 0:
                continue
            if training["selected_row_count"] >= len(train):
                rejected_broad += 1
                continue
            selector = {
                "selector": selector_name(kind, fields, values),
                "kind": kind,
                "fields": list(fields),
                "values": list(values),
                "uses_transfer_identity": False,
                "uses_rank_or_relation_count": False,
                "uses_verifier_label_as_feature": False,
            }
            candidates[selector["selector"]] = {
                "selector": selector,
                "selected": set(selected),
                "train_selected": train_selected,
                "training": training,
            }
    out = list(candidates.values())
    out.sort(key=lambda item: item["selector"]["selector"])
    return out, rejected_broad


def candidate_score(item: dict[str, Any], mode: str) -> tuple[Any, ...]:
    training = item["training"]
    replay = float(training["direct_replay_ops_over_rho"])
    budget = float(training["direct_replay_over_positive_row_rho_budget"])
    positives = float(training["positive_row_count"])
    pairs = float(training["positive_pair_count"])
    precision = float(training["row_precision"])
    false_replay = float(training["false_direct_replay_ops_over_rho"])
    selected = float(training["selected_row_count"])
    if mode == "row_efficiency":
        return (positives / max(EPSILON, replay), pairs, precision, -budget, -false_replay, -selected)
    if mode == "pair_efficiency":
        return (pairs / max(EPSILON, replay), positives / max(EPSILON, replay), pairs, -budget, -false_replay)
    if mode == "low_budget":
        return (-budget, pairs, positives, precision, -replay, -selected)
    if mode == "precision":
        return (precision, pairs, positives, -budget, -false_replay, -selected)
    if mode == "pair_coverage":
        return (pairs, positives, -budget, positives / max(EPSILON, replay), precision, -selected)
    return (pairs, positives / max(EPSILON, replay), precision, -budget, -selected)


def prune_candidates(candidates: list[dict[str, Any]], max_count: int) -> tuple[list[dict[str, Any]], int]:
    if max_count <= 0 or len(candidates) <= max_count:
        return candidates, 0
    modes = ("row_efficiency", "pair_efficiency", "low_budget", "precision", "pair_coverage", "default")
    per_mode = max(50, max_count // len(modes))
    chosen_by_name: dict[str, dict[str, Any]] = {}
    for mode in modes:
        ranked = sorted(candidates, key=lambda item: candidate_score(item, mode), reverse=True)
        for item in ranked[:per_mode]:
            chosen_by_name[item["selector"]["selector"]] = item
    if len(chosen_by_name) < max_count:
        ranked = sorted(candidates, key=lambda item: candidate_score(item, "default"), reverse=True)
        for item in ranked:
            chosen_by_name[item["selector"]["selector"]] = item
            if len(chosen_by_name) >= max_count:
                break
    pruned = list(chosen_by_name.values())
    pruned.sort(key=lambda item: item["selector"]["selector"])
    return pruned, len(candidates) - len(pruned)


def union_selected(chosen: list[dict[str, Any]]) -> set[int]:
    selected: set[int] = set()
    for item in chosen:
        selected |= item["selected"]
    return selected


def fast_delta(indices: set[int], rows: list[dict[str, Any]]) -> dict[str, Any]:
    positive_pairs: set[str] = set()
    positive_count = 0
    false_count = 0
    replay_over_rho = 0.0
    false_replay_over_rho = 0.0
    positive_replay_over_rho = 0.0
    for idx in indices:
        row = rows[idx]
        row_replay = float(row["direct_verifier_replay_ops_over_rho"])
        replay_over_rho += row_replay
        if row["row_positive"]:
            positive_count += 1
            positive_pairs.add(str(row["pair_id"]))
            positive_replay_over_rho += row_replay
        else:
            false_count += 1
            false_replay_over_rho += row_replay
    return {
        "selected_row_count": len(indices),
        "positive_row_count": positive_count,
        "false_row_count": false_count,
        "positive_pairs": positive_pairs,
        "positive_pair_count": len(positive_pairs),
        "direct_replay_ops_over_rho": replay_over_rho,
        "false_direct_replay_ops_over_rho": false_replay_over_rho,
        "positive_direct_replay_ops_over_rho": positive_replay_over_rho,
        "row_precision": positive_count / len(indices) if indices else 0.0,
        "direct_replay_over_positive_row_rho_budget": replay_over_rho / max(1, positive_count),
    }


def single_replay_efficiency(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not candidates:
        return []
    return [
        max(
            candidates,
            key=lambda item: (
                item["training"]["positive_pair_count"],
                item["training"]["positive_row_count"] / max(EPSILON, item["training"]["direct_replay_ops_over_rho"]),
                -item["training"]["direct_replay_over_positive_row_rho_budget"],
                item["training"]["row_precision"],
                -item["training"]["false_direct_replay_ops_over_rho"],
                -item["training"]["selected_row_count"],
            ),
        )
    ]


def single_replay_budget(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not candidates:
        return []
    below_budget = [
        item for item in candidates if item["training"]["direct_replay_over_positive_row_rho_budget"] <= 1.0
    ]
    pool = below_budget or candidates
    return [
        max(
            pool,
            key=lambda item: (
                item["training"]["positive_pair_count"],
                item["training"]["positive_row_count"],
                -item["training"]["direct_replay_over_positive_row_rho_budget"],
                item["training"]["row_precision"],
                -item["training"]["false_direct_replay_ops_over_rho"],
            ),
        )
    ]


def choose_greedy(
    candidates: list[dict[str, Any]],
    train: set[int],
    rows: list[dict[str, Any]],
    mode: str,
    row_budget_cap: float | None = None,
) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    remaining = candidates[:]
    for _ in range(MAX_UNION_SELECTORS):
        current_selected = union_selected(chosen) & train
        current_eval = fast_delta(current_selected, rows)
        current_pairs = set(current_eval["positive_pairs"])
        best = None
        best_score = None
        for item in remaining:
            marginal = item["train_selected"] - current_selected
            if not marginal:
                continue
            delta = fast_delta(marginal, rows)
            new_positive_count = current_eval["positive_row_count"] + delta["positive_row_count"]
            new_selected_count = current_eval["selected_row_count"] + delta["selected_row_count"]
            new_replay = current_eval["direct_replay_ops_over_rho"] + delta["direct_replay_ops_over_rho"]
            new_budget = new_replay / max(1, new_positive_count)
            if row_budget_cap is not None and new_budget > row_budget_cap:
                continue
            marginal_positive = delta["positive_row_count"]
            marginal_replay = delta["direct_replay_ops_over_rho"]
            new_pairs = delta["positive_pairs"] - current_pairs
            if marginal_positive <= 0 and not new_pairs:
                continue
            row_efficiency = marginal_positive / max(EPSILON, marginal_replay)
            pair_efficiency = len(new_pairs) / max(EPSILON, marginal_replay)
            if mode == "pair_cost":
                score = (
                    pair_efficiency,
                    row_efficiency,
                    len(new_pairs),
                    marginal_positive,
                    -marginal_replay,
                    -new_budget,
                )
            else:
                score = (
                    row_efficiency,
                    pair_efficiency,
                    len(new_pairs),
                    marginal_positive,
                    -marginal_replay,
                    -new_budget,
                    -new_selected_count,
                )
            if best_score is None or score > best_score:
                best = item
                best_score = score
        if best is None:
            break
        chosen.append(best)
        best_name = best["selector"]["selector"]
        remaining = [item for item in remaining if item["selector"]["selector"] != best_name]
    return chosen


def choose_for_policy(
    policy: str,
    candidates: list[dict[str, Any]],
    train: set[int],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if policy == "single_replay_efficiency":
        return single_replay_efficiency(candidates)
    if policy == "single_replay_budget":
        return single_replay_budget(candidates)
    if policy == "greedy_pair_cost_union":
        return choose_greedy(candidates, train, rows, "pair_cost")
    if policy == "greedy_row_budget_1x_union":
        return choose_greedy(candidates, train, rows, "row_cost", row_budget_cap=1.0)
    if policy == "greedy_row_budget_2x_union":
        return choose_greedy(candidates, train, rows, "row_cost", row_budget_cap=2.0)
    return choose_greedy(candidates, train, rows, "row_cost")


def selector_summary(
    chosen: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    train: set[int],
    heldout: set[int],
    all_rows: set[int],
) -> dict[str, Any]:
    selected = union_selected(chosen)
    selector_kinds = Counter(item["selector"]["kind"] for item in chosen)
    selector_sizes = Counter(len(item["selector"]["fields"]) for item in chosen)
    return {
        "selector_count": len(chosen),
        "selectors": [item["selector"] for item in chosen],
        "selector_names": [item["selector"]["selector"] for item in chosen],
        "selector_kind_counts": dict(selector_kinds),
        "selector_size_counts": {str(key): value for key, value in selector_sizes.items()},
        "training": p687.cost_summary(selected, train, rows),
        "heldout": p687.cost_summary(selected, heldout, rows),
        "all_rows": p687.cost_summary(selected, all_rows, rows),
    }


def jsonable_training(summary: dict[str, Any]) -> dict[str, Any]:
    out = dict(summary)
    if isinstance(out.get("positive_pairs"), set):
        out["positive_pairs"] = sorted(out["positive_pairs"])
    return out


def training_frontier(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items = sorted(
        candidates,
        key=lambda item: (
            item["training"]["direct_replay_over_positive_row_rho_budget"],
            -item["training"]["positive_pair_count"],
            -item["training"]["positive_row_count"],
            -item["training"]["row_precision"],
        ),
    )
    return [
        {
            "selector": item["selector"],
            "training": jsonable_training(item["training"]),
        }
        for item in items[:20]
    ]


def loto_audit(
    rows: list[dict[str, Any]],
    field_sets: list[tuple[str, tuple[str, ...]]],
    max_candidates_per_fold: int,
) -> list[dict[str, Any]]:
    all_indices = set(range(len(rows)))
    positive_pairs = sorted({row["pair_id"] for row in rows if row["row_positive"]})
    folds: list[dict[str, Any]] = []
    for holdout_pair in positive_pairs:
        train = {idx for idx, row in enumerate(rows) if row["pair_id"] != holdout_pair}
        heldout = all_indices - train
        raw_candidates, rejected_broad = make_candidates(rows, train, field_sets)
        candidates, pruned_count = prune_candidates(raw_candidates, max_candidates_per_fold)
        policies = {}
        for policy in POLICIES:
            chosen = choose_for_policy(policy, candidates, train, rows)
            policies[policy] = selector_summary(chosen, rows, train, heldout, all_indices)
        folds.append(
            {
                "holdout_pair": holdout_pair,
                "holdout_row_count": len(heldout),
                "holdout_positive_row_count": sum(1 for idx in heldout if rows[idx]["row_positive"]),
                "candidate_selector_count": len(candidates),
                "raw_candidate_selector_count": len(raw_candidates),
                "pruned_candidate_selector_count": pruned_count,
                "rejected_training_broad_selector_count": rejected_broad,
                "training_frontier": training_frontier(candidates),
                "policies": policies,
            }
        )
    return folds


def combine_scope(folds: list[dict[str, Any]], policy: str, scope: str) -> dict[str, Any]:
    keys = [
        "selected_row_count",
        "positive_row_count",
        "false_row_count",
        "direct_replay_ops",
        "direct_replay_ops_over_rho",
        "false_direct_replay_ops",
        "false_direct_replay_ops_over_rho",
        "positive_direct_replay_ops",
        "positive_direct_replay_ops_over_rho",
        "gate_leaf_check_ops",
        "gate_leaf_product_ops",
        "gate_shared_product_ops",
        "gate_shared_product_saved_ops",
        "gate_hit_root_ops",
    ]
    out = {key: 0.0 for key in keys}
    hit_pairs: set[str] = set()
    for fold in folds:
        row = fold["policies"][policy][scope]
        if row["positive_row_count"]:
            hit_pairs.update(row["positive_pairs"])
        for key in keys:
            out[key] += row[key]
    out["positive_pair_count"] = len(hit_pairs)
    out["row_precision"] = out["positive_row_count"] / max(1.0, out["selected_row_count"])
    out["replay_over_positive_row_rho_budget"] = out["direct_replay_ops_over_rho"] / max(
        1.0, out["positive_row_count"]
    )
    out["replay_over_positive_pair_rho_budget"] = out["direct_replay_ops_over_rho"] / max(1.0, len(hit_pairs))
    return out


def aggregate_folds(folds: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    heldout_keys = [
        "selected_row_count",
        "positive_row_count",
        "false_row_count",
        "direct_replay_ops",
        "direct_replay_ops_over_rho",
        "false_direct_replay_ops",
        "false_direct_replay_ops_over_rho",
        "positive_direct_replay_ops",
        "positive_direct_replay_ops_over_rho",
        "gate_leaf_check_ops",
        "gate_leaf_product_ops",
        "gate_shared_product_ops",
        "gate_shared_product_saved_ops",
        "gate_hit_root_ops",
    ]
    for policy in POLICIES:
        aggregate: dict[str, Any] = {f"heldout_{key}": 0.0 for key in heldout_keys}
        hit_pairs: list[str] = []
        selector_kinds: Counter[str] = Counter()
        selector_sizes: Counter[str] = Counter()
        selector_count_total = 0
        candidate_selector_count = 0
        raw_candidate_selector_count = 0
        pruned_candidate_selector_count = 0
        rejected_broad = 0
        chosen_selectors_by_fold: list[list[str]] = []
        for fold in folds:
            candidate_selector_count += int(fold["candidate_selector_count"])
            raw_candidate_selector_count += int(fold["raw_candidate_selector_count"])
            pruned_candidate_selector_count += int(fold["pruned_candidate_selector_count"])
            rejected_broad += int(fold["rejected_training_broad_selector_count"])
            row = fold["policies"][policy]
            heldout = row["heldout"]
            selector_count_total += int(row["selector_count"])
            selector_kinds.update(row["selector_kind_counts"])
            selector_sizes.update(row["selector_size_counts"])
            chosen_selectors_by_fold.append(row["selector_names"])
            if heldout["positive_row_count"]:
                hit_pairs.append(str(fold["holdout_pair"]))
            for key in heldout_keys:
                aggregate[f"heldout_{key}"] += heldout[key]
        aggregate["fold_count"] = len(folds)
        aggregate["heldout_positive_pair_hits"] = len(hit_pairs)
        aggregate["heldout_hit_pairs"] = hit_pairs
        aggregate["heldout_row_precision"] = aggregate["heldout_positive_row_count"] / max(
            1.0, aggregate["heldout_selected_row_count"]
        )
        aggregate["heldout_replay_over_positive_row_rho_budget"] = aggregate[
            "heldout_direct_replay_ops_over_rho"
        ] / max(1.0, aggregate["heldout_positive_row_count"])
        aggregate["heldout_replay_over_positive_pair_rho_budget"] = aggregate[
            "heldout_direct_replay_ops_over_rho"
        ] / max(1.0, aggregate["heldout_positive_pair_hits"])
        aggregate["selector_count_total"] = selector_count_total
        aggregate["candidate_selector_count_total"] = candidate_selector_count
        aggregate["raw_candidate_selector_count_total"] = raw_candidate_selector_count
        aggregate["pruned_candidate_selector_count_total"] = pruned_candidate_selector_count
        aggregate["rejected_training_broad_selector_count"] = rejected_broad
        aggregate["selector_kind_counts"] = dict(selector_kinds)
        aggregate["selector_size_counts"] = dict(selector_sizes)
        aggregate["chosen_selectors_by_fold"] = chosen_selectors_by_fold
        aggregate["all_rows"] = combine_scope(folds, policy, "all_rows")
        aggregate["training"] = combine_scope(folds, policy, "training")
        summary[policy] = aggregate
    return summary


def load_p687_baseline(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text())
    return payload.get("summary", {}).get("frontier_summary", {})


def compare_to_p687(policy_summary: dict[str, dict[str, Any]], baseline: dict[str, Any]) -> dict[str, dict[str, Any]]:
    baseline_replay = float(baseline.get("heldout_direct_replay_ops_over_rho") or 0.0)
    baseline_budget = float(baseline.get("heldout_replay_over_positive_row_rho_budget") or 0.0)
    baseline_hits = int(baseline.get("heldout_positive_pair_hits") or 0)
    out: dict[str, dict[str, Any]] = {}
    for policy, row in policy_summary.items():
        replay = float(row["heldout_direct_replay_ops_over_rho"])
        budget = float(row["heldout_replay_over_positive_row_rho_budget"])
        out[policy] = {
            "heldout_replay_reduction_vs_p687": baseline_replay - replay,
            "heldout_row_budget_reduction_vs_p687": baseline_budget - budget,
            "heldout_positive_pair_hit_delta_vs_p687": int(row["heldout_positive_pair_hits"]) - baseline_hits,
            "heldout_replay_ratio_vs_p687": replay / baseline_replay if baseline_replay else None,
        }
    return out


def choose_lead_policy(policy_summary: dict[str, dict[str, Any]]) -> str:
    return max(
        policy_summary,
        key=lambda policy: (
            policy_summary[policy]["heldout_positive_pair_hits"],
            -policy_summary[policy]["heldout_replay_over_positive_row_rho_budget"],
            -policy_summary[policy]["heldout_direct_replay_ops_over_rho"],
            policy_summary[policy]["heldout_positive_row_count"],
            policy_summary[policy]["heldout_row_precision"],
        ),
    )


def determine_claim(policy_summary: dict[str, dict[str, Any]], comparisons: dict[str, dict[str, Any]]) -> str:
    strong = []
    useful = []
    weak = []
    under_budget = []
    multi_pair = []
    for policy, row in policy_summary.items():
        hits = int(row["heldout_positive_pair_hits"])
        budget = float(row["heldout_replay_over_positive_row_rho_budget"])
        replay_reduction = float(comparisons.get(policy, {}).get("heldout_replay_reduction_vs_p687") or 0.0)
        budget_reduction = float(comparisons.get(policy, {}).get("heldout_row_budget_reduction_vs_p687") or 0.0)
        if hits >= 5 and budget < 1.0:
            strong.append(policy)
        if hits >= 5 and replay_reduction > 0.0 and budget_reduction > 0.0:
            useful.append(policy)
        if hits >= 4 and replay_reduction > 0.0 and budget_reduction > 0.0:
            weak.append(policy)
        if hits >= 1 and budget < 1.0:
            under_budget.append(policy)
        if hits >= 4:
            multi_pair.append(policy)
    if strong:
        return "P688_REPLAY_WEIGHTED_FRONTIER_BELOW_ROW_RHO_MULTI_PAIR"
    if useful:
        return "P688_REPLAY_WEIGHTED_FRONTIER_COST_REDUCTION_5PAIR_POSITIVE"
    if weak:
        return "P688_REPLAY_WEIGHTED_FRONTIER_COST_REDUCTION_WEAK_MULTI_PAIR"
    if under_budget:
        return "P688_REPLAY_WEIGHTED_FRONTIER_SINGLE_OR_FEW_PAIR_BELOW_RHO_SIGNAL"
    if multi_pair:
        return "P688_REPLAY_WEIGHTED_FRONTIER_MULTI_PAIR_REPLAY_STILL_ABOVE_P687"
    return "NEGATIVE_RESULT_P688_REPLAY_WEIGHTED_FRONTIER_NO_COSTED_HELDOUT_SIGNAL"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="append", default=None, help="Gate artifact to include; repeatable.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p687-artifact", default=str(DEFAULT_P687_ARTIFACT))
    parser.add_argument("--max-combo-size", type=int, default=MAX_COMBO_SIZE)
    parser.add_argument("--max-candidates-per-fold", type=int, default=MAX_CANDIDATES_PER_FOLD)
    args = parser.parse_args()

    gate_paths = [Path(path) for path in (args.gate or [str(path) for path in DEFAULT_GATES])]
    input_rows = p687.load_unique_cost_rows(gate_paths)
    successor_rows = p685.build_successor_rows(input_rows)
    field_sets = make_field_sets(args.max_combo_size)
    folds = loto_audit(successor_rows, field_sets, args.max_candidates_per_fold)
    policy_summary = aggregate_folds(folds)
    p687_baseline = load_p687_baseline(Path(args.p687_artifact))
    comparisons = compare_to_p687(policy_summary, p687_baseline)
    claim_status = determine_claim(policy_summary, comparisons)
    lead_policy = choose_lead_policy(policy_summary)
    payload = {
        "schema": "ecdlp.low_term_total2_p688_replay_weighted_row_selector_frontier.v1",
        "created_at": p678.utc_now(),
        "method": "p688_replay_weighted_row_selector_frontier",
        "claim_status": claim_status,
        "artifacts": {
            "gates": [str(path) for path in gate_paths],
            "p687_baseline": str(args.p687_artifact),
        },
        "parameters": {
            "policies": list(POLICIES),
            "max_union_selectors": MAX_UNION_SELECTORS,
            "max_combo_size": args.max_combo_size,
            "max_candidates_per_fold": args.max_candidates_per_fold,
            "field_set_count": len(field_sets),
            "extra_public_fields": list(EXTRA_PUBLIC_FIELDS),
            "outcome": "successor right208/salt208 row is below-rho direct verified",
            "holdout_unit": "successor-positive transition pair",
            "dedupe_key": "target|transfer|selector|top_k",
            "training_broad_selector_rule": "reject if selector matches every training row",
        },
        "summary": {
            "claim_status": claim_status,
            "lead_policy": lead_policy,
            "unique_input_row_count": len(input_rows),
            "successor_row_count": len(successor_rows),
            "positive_row_count": sum(1 for row in successor_rows if row["row_positive"]),
            "positive_pair_count": len({row["pair_id"] for row in successor_rows if row["row_positive"]}),
            "p687_frontier_baseline": p687_baseline,
            "policy_summary": policy_summary,
            "comparison_to_p687": comparisons,
        },
        "folds": folds,
        "honesty_boundary": [
            "Selector choices use training rows only; held-out pair labels are not used for selector choice.",
            "Selectors use public row-level source/gate fields only.",
            "Rank, relation count, transfer identity, direct verification labels, below-rho labels, and derived secrets are excluded as selector fields.",
            "Direct replay cost is not a full source-generation, sparse-linear-algebra, target-descent, or individual-log cost.",
            "A cost reduction here remains relation-event evidence, not a deployed-curve ECDLP break.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "claim_status": claim_status,
                "lead_policy": lead_policy,
                "successor_row_count": len(successor_rows),
                "positive_row_count": sum(1 for row in successor_rows if row["row_positive"]),
                "lead_summary": policy_summary[lead_policy],
                "lead_comparison_to_p687": comparisons[lead_policy],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
