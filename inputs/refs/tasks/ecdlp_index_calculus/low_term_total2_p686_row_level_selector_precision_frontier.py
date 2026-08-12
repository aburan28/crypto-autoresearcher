#!/usr/bin/env python3
"""P686 row-level public selector precision frontier."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p682_right207_to_right208_transition_pair_audit as p682
import low_term_total2_p684_public_pre_rank_proxy_selector as p684
import low_term_total2_p685_row_level_public_pre_rank_selector as p685
import low_term_total2_p678_right208_salt208_public_selector_audit as p678


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p686_row_level_selector_precision_frontier_probe.json"
DEFAULT_GATES = p682.DEFAULT_GATES
DEFAULT_P685_ARTIFACT = STATE_DIR / "low_term_total2_p685_row_level_public_pre_rank_selector_probe.json"
MAX_UNION_SELECTORS = 4
POLICIES = (
    "single_recall_precision",
    "single_min_false_paircover",
    "single_efficiency",
    "greedy_paircover_union",
    "greedy_efficiency_union",
    "greedy_budgeted_union",
)


def selector_matches(selector: dict[str, Any], row: dict[str, Any]) -> bool:
    return p685.row_matches(selector, row)


def row_indices(rows: list[dict[str, Any]]) -> list[int]:
    return list(range(len(rows)))


def evaluate_indices(selected: set[int], universe: set[int], rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected_in_universe = selected & universe
    positives = {idx for idx in selected_in_universe if rows[idx]["row_positive"]}
    false_rows = selected_in_universe - positives
    available_positive_rows = {idx for idx in universe if rows[idx]["row_positive"]}
    available_positive_pairs = sorted({rows[idx]["pair_id"] for idx in available_positive_rows})
    selected_positive_pairs = sorted({rows[idx]["pair_id"] for idx in positives})
    return {
        "selected_row_count": len(selected_in_universe),
        "positive_row_count": len(positives),
        "false_row_count": len(false_rows),
        "positive_pair_count": len(selected_positive_pairs),
        "available_positive_pair_count": len(available_positive_pairs),
        "row_precision": len(positives) / len(selected_in_universe) if selected_in_universe else 0.0,
        "row_recall": len(positives) / max(1, len(available_positive_rows)),
        "pair_recall": len(selected_positive_pairs) / max(1, len(available_positive_pairs)),
        "selected_pairs": sorted({rows[idx]["pair_id"] for idx in selected_in_universe}),
        "positive_pairs": selected_positive_pairs,
        "positive_row_examples": [rows[idx]["row_id"] for idx in sorted(positives)[:24]],
        "false_row_examples": [rows[idx]["row_id"] for idx in sorted(false_rows)[:24]],
    }


def selector_selected_indices(selector: dict[str, Any], rows: list[dict[str, Any]]) -> set[int]:
    return {idx for idx, row in enumerate(rows) if selector_matches(selector, row)}


def load_p685_baseline(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text())
    return payload.get("summary", {}).get("row_level_policy_summary", {}).get("recall_first", {})


def make_candidates(rows: list[dict[str, Any]], train: set[int]) -> tuple[list[dict[str, Any]], int]:
    train_rows = [rows[idx] for idx in sorted(train)]
    selectors = p685.generate_selectors(train_rows)
    candidates: list[dict[str, Any]] = []
    rejected_broad = 0
    for selector in selectors:
        selected = selector_selected_indices(selector, rows)
        train_eval = evaluate_indices(selected, train, rows)
        if train_eval["positive_row_count"] <= 0:
            continue
        if train_eval["selected_row_count"] >= len(train):
            rejected_broad += 1
            continue
        candidates.append({"selector": selector, "selected": selected, "training": train_eval})
    return candidates, rejected_broad


def single_recall_precision(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not candidates:
        return []
    return [
        max(
            candidates,
            key=lambda item: (
                item["training"]["positive_pair_count"],
                item["training"]["row_recall"],
                item["training"]["row_precision"],
                item["training"]["positive_row_count"],
                -item["training"]["false_row_count"],
                -item["training"]["selected_row_count"],
            ),
        )
    ]


def single_min_false_paircover(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not candidates:
        return []
    max_pairs = max(item["training"]["positive_pair_count"] for item in candidates)
    pool = [item for item in candidates if item["training"]["positive_pair_count"] == max_pairs]
    return [
        min(
            pool,
            key=lambda item: (
                item["training"]["false_row_count"],
                item["training"]["selected_row_count"],
                -item["training"]["positive_row_count"],
                -item["training"]["row_precision"],
            ),
        )
    ]


def single_efficiency(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not candidates:
        return []
    return [
        max(
            candidates,
            key=lambda item: (
                item["training"]["row_precision"],
                item["training"]["positive_pair_count"],
                item["training"]["positive_row_count"],
                -item["training"]["false_row_count"],
                -item["training"]["selected_row_count"],
            ),
        )
    ]


def union_selected(chosen: list[dict[str, Any]]) -> set[int]:
    selected: set[int] = set()
    for item in chosen:
        selected |= item["selected"]
    return selected


def positive_pairs_for_indices(indices: set[int], rows: list[dict[str, Any]]) -> set[str]:
    return {rows[idx]["pair_id"] for idx in indices if rows[idx]["row_positive"]}


def greedy_paircover_union(candidates: list[dict[str, Any]], train: set[int], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    covered_pairs: set[str] = set()
    remaining = candidates[:]
    for _ in range(MAX_UNION_SELECTORS):
        current_selected = union_selected(chosen)
        best = None
        best_score = None
        for item in remaining:
            new_selected = (current_selected | item["selected"]) & train
            current_eval = evaluate_indices(current_selected, train, rows)
            new_eval = evaluate_indices(new_selected, train, rows)
            new_pairs = set(new_eval["positive_pairs"]) - covered_pairs
            if not new_pairs and new_eval["positive_row_count"] <= current_eval["positive_row_count"]:
                continue
            marginal_false = new_eval["false_row_count"] - current_eval["false_row_count"]
            marginal_positive = new_eval["positive_row_count"] - current_eval["positive_row_count"]
            score = (len(new_pairs), marginal_positive, -marginal_false, new_eval["row_precision"], -new_eval["selected_row_count"])
            if best_score is None or score > best_score:
                best = item
                best_score = score
        if best is None:
            break
        chosen.append(best)
        remaining = [item for item in remaining if item["selector"]["selector"] != best["selector"]["selector"]]
        covered_pairs = positive_pairs_for_indices(union_selected(chosen) & train, rows)
        if len(covered_pairs) >= len({rows[idx]["pair_id"] for idx in train if rows[idx]["row_positive"]}):
            break
    return chosen


def greedy_efficiency_union(candidates: list[dict[str, Any]], train: set[int], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    remaining = candidates[:]
    for _ in range(MAX_UNION_SELECTORS):
        current_selected = union_selected(chosen)
        current_eval = evaluate_indices(current_selected, train, rows)
        best = None
        best_score = None
        for item in remaining:
            new_selected = (current_selected | item["selected"]) & train
            new_eval = evaluate_indices(new_selected, train, rows)
            marginal_positive = new_eval["positive_row_count"] - current_eval["positive_row_count"]
            marginal_false = new_eval["false_row_count"] - current_eval["false_row_count"]
            if marginal_positive <= 0:
                continue
            score = (
                marginal_positive / max(1, marginal_false),
                len(set(new_eval["positive_pairs"]) - set(current_eval["positive_pairs"])),
                marginal_positive,
                -marginal_false,
                new_eval["row_precision"],
            )
            if best_score is None or score > best_score:
                best = item
                best_score = score
        if best is None:
            break
        chosen.append(best)
        remaining = [item for item in remaining if item["selector"]["selector"] != best["selector"]["selector"]]
    return chosen


def greedy_budgeted_union(candidates: list[dict[str, Any]], train: set[int], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    remaining = candidates[:]
    false_budget = min(1600, max(200, int(0.33 * len(train))))
    for _ in range(MAX_UNION_SELECTORS):
        current_selected = union_selected(chosen)
        current_eval = evaluate_indices(current_selected, train, rows)
        best = None
        best_score = None
        for item in remaining:
            new_selected = (current_selected | item["selected"]) & train
            new_eval = evaluate_indices(new_selected, train, rows)
            if new_eval["false_row_count"] > false_budget:
                continue
            marginal_positive = new_eval["positive_row_count"] - current_eval["positive_row_count"]
            if marginal_positive <= 0:
                continue
            score = (
                new_eval["positive_pair_count"],
                new_eval["positive_row_count"],
                new_eval["row_precision"],
                -new_eval["false_row_count"],
                -new_eval["selected_row_count"],
            )
            if best_score is None or score > best_score:
                best = item
                best_score = score
        if best is None:
            break
        chosen.append(best)
        remaining = [item for item in remaining if item["selector"]["selector"] != best["selector"]["selector"]]
    return chosen


POLICY_BUILDERS = {
    "single_recall_precision": single_recall_precision,
    "single_min_false_paircover": single_min_false_paircover,
    "single_efficiency": single_efficiency,
    "greedy_paircover_union": greedy_paircover_union,
    "greedy_efficiency_union": greedy_efficiency_union,
    "greedy_budgeted_union": greedy_budgeted_union,
}


def choose_for_policy(policy: str, candidates: list[dict[str, Any]], train: set[int], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if policy.startswith("single_"):
        return POLICY_BUILDERS[policy](candidates)
    return POLICY_BUILDERS[policy](candidates, train, rows)


def selector_summary(chosen: list[dict[str, Any]], rows: list[dict[str, Any]], train: set[int], heldout: set[int], all_rows: set[int]) -> dict[str, Any]:
    selected = union_selected(chosen)
    return {
        "selector_count": len(chosen),
        "selectors": [item["selector"] for item in chosen],
        "selector_names": [item["selector"]["selector"] for item in chosen],
        "selector_kind_counts": dict(Counter(item["selector"]["kind"] for item in chosen)),
        "training": evaluate_indices(selected, train, rows),
        "heldout": evaluate_indices(selected, heldout, rows),
        "all_rows": evaluate_indices(selected, all_rows, rows),
    }


def training_frontier(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best_by_pair_count: dict[int, list[dict[str, Any]]] = {}
    for item in candidates:
        pair_count = int(item["training"]["positive_pair_count"])
        best_by_pair_count.setdefault(pair_count, []).append(item)
    out: list[dict[str, Any]] = []
    for pair_count, items in sorted(best_by_pair_count.items(), reverse=True):
        items.sort(
            key=lambda item: (
                item["training"]["false_row_count"],
                item["training"]["selected_row_count"],
                -item["training"]["positive_row_count"],
            )
        )
        for item in items[:5]:
            out.append(
                {
                    "selector": item["selector"],
                    "training": item["training"],
                }
            )
    return out[:20]


def loto_audit(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    all_indices = set(row_indices(rows))
    positive_pairs = sorted({row["pair_id"] for row in rows if row["row_positive"]})
    folds: list[dict[str, Any]] = []
    for holdout_pair in positive_pairs:
        train = {idx for idx, row in enumerate(rows) if row["pair_id"] != holdout_pair}
        heldout = all_indices - train
        candidates, rejected_broad = make_candidates(rows, train)
        policies: dict[str, Any] = {}
        for policy in POLICIES:
            chosen = choose_for_policy(policy, candidates, train, rows)
            policies[policy] = selector_summary(chosen, rows, train, heldout, all_indices)
        folds.append(
            {
                "holdout_pair": holdout_pair,
                "holdout_row_count": len(heldout),
                "holdout_positive_row_count": sum(1 for idx in heldout if rows[idx]["row_positive"]),
                "candidate_selector_count": len(candidates),
                "rejected_training_broad_selector_count": rejected_broad,
                "training_frontier": training_frontier(candidates),
                "policies": policies,
            }
        )
    return folds


def aggregate_folds(folds: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for policy in POLICIES:
        heldout_pair_hits = 0
        heldout_positive_rows = 0
        heldout_selected_rows = 0
        heldout_false_rows = 0
        heldout_available_positive_rows = 0
        aggregate_selected = 0
        aggregate_false = 0
        aggregate_positive = 0
        selector_counts = 0
        rejected_broad = 0
        selector_kinds: Counter[str] = Counter()
        hit_pairs: list[str] = []
        chosen_selectors: list[list[str]] = []
        for fold in folds:
            heldout_available_positive_rows += int(fold["holdout_positive_row_count"])
            rejected_broad += int(fold["rejected_training_broad_selector_count"])
            row = fold["policies"][policy]
            heldout = row["heldout"]
            all_rows = row["all_rows"]
            heldout_positive = int(heldout["positive_row_count"])
            if heldout_positive:
                heldout_pair_hits += 1
                hit_pairs.append(str(fold["holdout_pair"]))
            heldout_positive_rows += heldout_positive
            heldout_selected_rows += int(heldout["selected_row_count"])
            heldout_false_rows += int(heldout["false_row_count"])
            aggregate_selected += int(all_rows["selected_row_count"])
            aggregate_false += int(all_rows["false_row_count"])
            aggregate_positive += int(all_rows["positive_row_count"])
            selector_counts += int(row["selector_count"])
            selector_kinds.update(row["selector_kind_counts"])
            chosen_selectors.append(row["selector_names"])
        summary[policy] = {
            "fold_count": len(folds),
            "heldout_positive_pair_hits": heldout_pair_hits,
            "heldout_hit_pairs": hit_pairs,
            "heldout_positive_row_count": heldout_positive_rows,
            "heldout_available_positive_row_count": heldout_available_positive_rows,
            "heldout_row_recall": heldout_positive_rows / max(1, heldout_available_positive_rows),
            "heldout_selected_row_count": heldout_selected_rows,
            "heldout_false_row_count": heldout_false_rows,
            "heldout_row_precision": heldout_positive_rows / max(1, heldout_selected_rows),
            "aggregate_all_rows_selected_row_count": aggregate_selected,
            "aggregate_all_rows_false_row_count": aggregate_false,
            "aggregate_all_rows_positive_row_count": aggregate_positive,
            "aggregate_row_precision": aggregate_positive / max(1, aggregate_selected),
            "selector_count_total": selector_counts,
            "rejected_training_broad_selector_count": rejected_broad,
            "selector_kind_counts": dict(selector_kinds),
            "chosen_selectors_by_fold": chosen_selectors,
        }
    return summary


def compare_to_p685(policy_summary: dict[str, dict[str, Any]], p685_baseline: dict[str, Any]) -> dict[str, Any]:
    baseline_heldout_false = int(p685_baseline.get("heldout_false_row_count") or 0)
    baseline_aggregate_false = int(p685_baseline.get("aggregate_all_rows_false_row_count") or 0)
    baseline_hits = int(p685_baseline.get("heldout_positive_pair_hits") or 0)
    out = {}
    for policy, row in policy_summary.items():
        out[policy] = {
            "heldout_false_reduction_vs_p685_recall_first": baseline_heldout_false - int(row["heldout_false_row_count"]),
            "aggregate_false_reduction_vs_p685_recall_first": baseline_aggregate_false
            - int(row["aggregate_all_rows_false_row_count"]),
            "heldout_pair_hit_delta_vs_p685_recall_first": int(row["heldout_positive_pair_hits"]) - baseline_hits,
        }
    return out


def determine_claim(policy_summary: dict[str, dict[str, Any]], comparisons: dict[str, Any]) -> str:
    strong = []
    weak = []
    for policy, row in policy_summary.items():
        cmp = comparisons.get(policy, {})
        hits = int(row["heldout_positive_pair_hits"])
        heldout_reduction = int(cmp.get("heldout_false_reduction_vs_p685_recall_first") or 0)
        aggregate_reduction = int(cmp.get("aggregate_false_reduction_vs_p685_recall_first") or 0)
        if hits >= 4 and heldout_reduction > 0 and aggregate_reduction > 0:
            strong.append(policy)
        if hits >= 2 and heldout_reduction > 0 and aggregate_reduction > 0:
            weak.append(policy)
    if strong:
        return "P686_ROW_LEVEL_PRECISION_FRONTIER_STRONG_MULTI_HELDOUT_FALSE_REDUCTION"
    if weak:
        return "P686_ROW_LEVEL_PRECISION_FRONTIER_WEAK_MULTI_HELDOUT_FALSE_REDUCTION"
    if any(int(row["heldout_positive_pair_hits"]) >= 2 for row in policy_summary.values()):
        return "P686_ROW_LEVEL_FRONTIER_MULTI_HELDOUT_NO_FALSE_REDUCTION"
    return "NEGATIVE_RESULT_P686_ROW_LEVEL_PRECISION_FRONTIER_NO_MULTI_HELDOUT_REDUCTION"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="append", default=None, help="Gate artifact to include; repeatable.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p685-artifact", default=str(DEFAULT_P685_ARTIFACT))
    args = parser.parse_args()

    gate_paths = [Path(path) for path in (args.gate or [str(path) for path in DEFAULT_GATES])]
    input_rows = p684.load_unique_rows(gate_paths)
    successor_rows = p685.build_successor_rows(input_rows)
    folds = loto_audit(successor_rows)
    policy_summary = aggregate_folds(folds)
    p685_baseline = load_p685_baseline(Path(args.p685_artifact))
    comparisons = compare_to_p685(policy_summary, p685_baseline)
    claim_status = determine_claim(policy_summary, comparisons)
    diagnostics = p685.fixed_diagnostics(successor_rows)
    positive_pairs = sorted({row["pair_id"] for row in successor_rows if row["row_positive"]})
    payload = {
        "schema": "ecdlp.low_term_total2_p686_row_level_selector_precision_frontier.v1",
        "created_at": p678.utc_now(),
        "method": "p686_row_level_selector_precision_frontier",
        "claim_status": claim_status,
        "artifacts": {
            "gates": [str(path) for path in gate_paths],
            "p685_baseline": str(args.p685_artifact),
        },
        "parameters": {
            "policies": list(POLICIES),
            "max_union_selectors": MAX_UNION_SELECTORS,
            "row_public_field_sets": [
                {"kind": kind, "fields": list(fields)} for kind, fields in p685.ROW_PUBLIC_FIELD_SETS
            ],
            "outcome": "successor right208/salt208 row is below-rho direct verified",
            "holdout_unit": "successor-positive transition pair",
            "dedupe_key": "target|transfer|selector|top_k",
            "training_broad_selector_rule": "reject if selector matches every training row",
        },
        "summary": {
            "claim_status": claim_status,
            "unique_input_row_count": len(input_rows),
            "successor_row_count": len(successor_rows),
            "positive_row_count": sum(1 for row in successor_rows if row["row_positive"]),
            "positive_pair_count": len(positive_pairs),
            "positive_pairs": positive_pairs,
            "p685_recall_first_baseline": p685_baseline,
            "policy_summary": policy_summary,
            "comparison_to_p685_recall_first": comparisons,
            "fixed_diagnostics": diagnostics,
        },
        "folds": folds,
        "honesty_boundary": [
            "Selector choices use training rows only; held-out pair labels are not used for selection.",
            "Selectors use public row-level source/gate fields only.",
            "Rank, relation count, transfer identity, direct verification labels, and below-rho labels are excluded as selector fields.",
            "Training-broad selectors are rejected before policy scoring.",
            "Selector-frontier held-out recall is relation-event evidence, not a complete faster-than-rho ECDLP algorithm.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "claim_status": claim_status,
                "successor_row_count": len(successor_rows),
                "positive_row_count": sum(1 for row in successor_rows if row["row_positive"]),
                "positive_pair_count": len(positive_pairs),
                "policy_summary": policy_summary,
                "comparison_to_p685_recall_first": comparisons,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
