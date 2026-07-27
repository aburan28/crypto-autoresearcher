#!/usr/bin/env python3
"""P689 rank-value audit for P686/P688 row frontiers."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p682_right207_to_right208_transition_pair_audit as p682
import low_term_total2_p685_row_level_public_pre_rank_selector as p685
import low_term_total2_p687_frontier_source_charge_replay_audit as p687
import low_term_total2_p678_right208_salt208_public_selector_audit as p678


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p689_rank_value_relation_surface_audit_probe.json"
DEFAULT_GATES = p682.DEFAULT_GATES
DEFAULT_P686_ARTIFACT = STATE_DIR / "low_term_total2_p686_row_level_selector_precision_frontier_probe.json"
DEFAULT_P688_ARTIFACT = STATE_DIR / "low_term_total2_p688_replay_weighted_row_selector_frontier_probe.json"
P686_POLICY = "greedy_budgeted_union"
EPSILON = 1.0e-9


def number(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def row_rank(row: dict[str, Any]) -> int:
    return int_value(row.get("rank"))


def row_relation_count(row: dict[str, Any]) -> int:
    return int_value(row.get("relation_count"))


def direct_verified(row: dict[str, Any]) -> bool:
    return bool(row.get("direct_verified"))


def rank_value(row: dict[str, Any]) -> int:
    if not direct_verified(row):
        return 0
    return max(0, row_rank(row) - 2)


def relation_value(row: dict[str, Any]) -> int:
    if not direct_verified(row):
        return 0
    return max(0, row_relation_count(row) - 2)


def rank3_value(row: dict[str, Any]) -> bool:
    return direct_verified(row) and row_rank(row) >= 3


def relation3_value(row: dict[str, Any]) -> bool:
    return direct_verified(row) and row_relation_count(row) >= 3


def selected_by_selectors(rows: list[dict[str, Any]], selectors: list[dict[str, Any]]) -> set[int]:
    selected: set[int] = set()
    for idx, row in enumerate(rows):
        if any(p685.row_matches(selector, row) for selector in selectors):
            selected.add(idx)
    return selected


def surface_key(row: dict[str, Any]) -> str:
    return "|".join(
        [
            str(row.get("pair_id")),
            str(row.get("selector_mode")),
            str(row.get("right_anchor_token")),
            str(row.get("row_pair")),
            str(row.get("leaf_signature")),
            str(row_rank(row)),
            str(row_relation_count(row)),
        ]
    )


def summarize_indices(selected_indices: set[int], universe_indices: set[int], rows: list[dict[str, Any]]) -> dict[str, Any]:
    indices = selected_indices & universe_indices
    positives = {idx for idx in indices if rows[idx]["row_positive"]}
    false_rows = indices - positives
    direct = {idx for idx in indices if direct_verified(rows[idx])}
    direct_false = direct - positives
    rank3 = {idx for idx in direct if rank3_value(rows[idx])}
    relation3 = {idx for idx in direct if relation3_value(rows[idx])}
    rank3_false = rank3 - positives
    relation3_false = relation3 - positives
    available_positive_rows = {idx for idx in universe_indices if rows[idx]["row_positive"]}
    replay = sum(number(rows[idx].get("direct_verifier_replay_ops_over_rho")) for idx in indices)
    false_replay = sum(number(rows[idx].get("direct_verifier_replay_ops_over_rho")) for idx in false_rows)
    rank_excess = sum(rank_value(rows[idx]) for idx in indices)
    false_rank_excess = sum(rank_value(rows[idx]) for idx in false_rows)
    relation_excess = sum(relation_value(rows[idx]) for idx in indices)
    false_relation_excess = sum(relation_value(rows[idx]) for idx in false_rows)
    selected_positive_pairs = sorted({rows[idx]["pair_id"] for idx in positives})
    available_positive_pairs = sorted({rows[idx]["pair_id"] for idx in available_positive_rows})
    value_indices = rank3 | relation3
    false_value_indices = rank3_false | relation3_false
    return {
        "selected_row_count": len(indices),
        "positive_row_count": len(positives),
        "false_row_count": len(false_rows),
        "available_positive_row_count": len(available_positive_rows),
        "positive_pair_count": len(selected_positive_pairs),
        "available_positive_pair_count": len(available_positive_pairs),
        "row_precision": len(positives) / len(indices) if indices else 0.0,
        "row_recall": len(positives) / max(1, len(available_positive_rows)),
        "pair_recall": len(selected_positive_pairs) / max(1, len(available_positive_pairs)),
        "positive_pairs": selected_positive_pairs,
        "selected_pairs": sorted({rows[idx]["pair_id"] for idx in indices}),
        "direct_verified_row_count": len(direct),
        "direct_false_verified_row_count": len(direct_false),
        "rank3_direct_verified_row_count": len(rank3),
        "rank3_positive_row_count": len(rank3 & positives),
        "rank3_false_verified_row_count": len(rank3_false),
        "relation3_direct_verified_row_count": len(relation3),
        "relation3_positive_row_count": len(relation3 & positives),
        "relation3_false_verified_row_count": len(relation3_false),
        "rank_or_relation_value_row_count": len(value_indices),
        "false_rank_or_relation_value_row_count": len(false_value_indices),
        "rank_excess_sum": rank_excess,
        "false_rank_excess_sum": false_rank_excess,
        "relation_excess_sum": relation_excess,
        "false_relation_excess_sum": false_relation_excess,
        "max_rank": max([row_rank(rows[idx]) for idx in direct] or [0]),
        "max_relation_count": max([row_relation_count(rows[idx]) for idx in direct] or [0]),
        "direct_replay_ops_over_rho": replay,
        "false_direct_replay_ops_over_rho": false_replay,
        "rank_excess_per_replay": rank_excess / max(EPSILON, replay),
        "false_rank_excess_per_false_replay": false_rank_excess / max(EPSILON, false_replay),
        "relation_excess_per_replay": relation_excess / max(EPSILON, replay),
        "false_relation_excess_per_false_replay": false_relation_excess / max(EPSILON, false_replay),
        "unique_value_surface_count": len({surface_key(rows[idx]) for idx in value_indices}),
        "unique_false_value_surface_count": len({surface_key(rows[idx]) for idx in false_value_indices}),
        "rank3_false_examples": [rows[idx]["row_id"] for idx in sorted(rank3_false)[:24]],
        "relation3_false_examples": [rows[idx]["row_id"] for idx in sorted(relation3_false)[:24]],
        "rank3_positive_examples": [rows[idx]["row_id"] for idx in sorted(rank3 & positives)[:24]],
    }


def load_policy_folds(path: Path, artifact_name: str, policies: list[str] | None = None) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    out: list[dict[str, Any]] = []
    if policies is None:
        policies = sorted((payload.get("summary", {}).get("policy_summary") or {}).keys())
    for policy in policies:
        folds = []
        for fold in payload.get("folds", []):
            policy_row = (fold.get("policies") or {}).get(policy) or {}
            folds.append(
                {
                    "holdout_pair": str(fold["holdout_pair"]),
                    "selectors": list(policy_row.get("selectors") or []),
                }
            )
        out.append({"artifact": artifact_name, "policy": policy, "folds": folds})
    return out


def evaluate_policy_spec(spec: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    all_indices = set(range(len(rows)))
    folds: list[dict[str, Any]] = []
    selector_kinds: Counter[str] = Counter()
    for fold in spec["folds"]:
        selectors = list(fold["selectors"])
        selected = selected_by_selectors(rows, selectors)
        heldout = {idx for idx, row in enumerate(rows) if row["pair_id"] == fold["holdout_pair"]}
        train = all_indices - heldout
        selector_kinds.update(str(selector.get("kind")) for selector in selectors)
        folds.append(
            {
                "holdout_pair": fold["holdout_pair"],
                "selector_count": len(selectors),
                "selector_names": [selector.get("selector") for selector in selectors],
                "training": summarize_indices(selected, train, rows),
                "heldout": summarize_indices(selected, heldout, rows),
                "all_rows": summarize_indices(selected, all_indices, rows),
            }
        )
    return {
        "artifact": spec["artifact"],
        "policy": spec["policy"],
        "selector_kind_counts": dict(selector_kinds),
        "folds": folds,
        "summary": aggregate_policy_folds(folds),
    }


def aggregate_policy_folds(folds: list[dict[str, Any]]) -> dict[str, Any]:
    keys = [
        "selected_row_count",
        "positive_row_count",
        "false_row_count",
        "direct_verified_row_count",
        "direct_false_verified_row_count",
        "rank3_direct_verified_row_count",
        "rank3_positive_row_count",
        "rank3_false_verified_row_count",
        "relation3_direct_verified_row_count",
        "relation3_positive_row_count",
        "relation3_false_verified_row_count",
        "rank_or_relation_value_row_count",
        "false_rank_or_relation_value_row_count",
        "rank_excess_sum",
        "false_rank_excess_sum",
        "relation_excess_sum",
        "false_relation_excess_sum",
        "direct_replay_ops_over_rho",
        "false_direct_replay_ops_over_rho",
        "unique_value_surface_count",
        "unique_false_value_surface_count",
    ]
    heldout = {f"heldout_{key}": 0.0 for key in keys}
    hit_pairs: list[str] = []
    rank_value_pairs: list[str] = []
    false_rank_value_pairs: list[str] = []
    for fold in folds:
        row = fold["heldout"]
        if row["positive_row_count"]:
            hit_pairs.append(fold["holdout_pair"])
        if row["rank_or_relation_value_row_count"]:
            rank_value_pairs.append(fold["holdout_pair"])
        if row["false_rank_or_relation_value_row_count"]:
            false_rank_value_pairs.append(fold["holdout_pair"])
        for key in keys:
            heldout[f"heldout_{key}"] += row[key]
    heldout["fold_count"] = len(folds)
    heldout["heldout_positive_pair_hits"] = len(hit_pairs)
    heldout["heldout_hit_pairs"] = hit_pairs
    heldout["heldout_rank_value_pair_hits"] = len(rank_value_pairs)
    heldout["heldout_rank_value_pairs"] = rank_value_pairs
    heldout["heldout_false_rank_value_pair_hits"] = len(false_rank_value_pairs)
    heldout["heldout_false_rank_value_pairs"] = false_rank_value_pairs
    heldout["heldout_row_precision"] = heldout["heldout_positive_row_count"] / max(
        1.0, heldout["heldout_selected_row_count"]
    )
    heldout["heldout_rank_excess_per_replay"] = heldout["heldout_rank_excess_sum"] / max(
        EPSILON, heldout["heldout_direct_replay_ops_over_rho"]
    )
    heldout["heldout_false_rank_excess_per_false_replay"] = heldout["heldout_false_rank_excess_sum"] / max(
        EPSILON, heldout["heldout_false_direct_replay_ops_over_rho"]
    )
    heldout["heldout_relation_excess_per_replay"] = heldout["heldout_relation_excess_sum"] / max(
        EPSILON, heldout["heldout_direct_replay_ops_over_rho"]
    )
    heldout["heldout_false_relation_excess_per_false_replay"] = heldout[
        "heldout_false_relation_excess_sum"
    ] / max(EPSILON, heldout["heldout_false_direct_replay_ops_over_rho"])
    return heldout


def broad_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    all_indices = set(range(len(rows)))
    return summarize_indices(all_indices, all_indices, rows)


def determine_claim(policy_results: list[dict[str, Any]], broad: dict[str, Any]) -> str:
    useful_false = []
    any_value = []
    for result in policy_results:
        summary = result["summary"]
        if int(summary["heldout_rank_or_relation_value_row_count"]) > 0:
            any_value.append(result["policy"])
        if (
            int(summary["heldout_positive_pair_hits"]) >= 4
            and int(summary["heldout_false_rank_or_relation_value_row_count"]) > 0
            and float(summary["heldout_false_rank_excess_per_false_replay"])
            >= float(broad["false_rank_excess_per_false_replay"])
        ):
            useful_false.append(result["policy"])
    if useful_false:
        return "P689_FALSE_ROWS_CARRY_HELDOUT_RANK_VALUE"
    if any_value:
        return "P689_SELECTED_RANK_VALUE_ONLY_DIRECT_POSITIVE_OR_LOW_COVERAGE"
    return "NEGATIVE_RESULT_P689_NO_HELDOUT_RANK_VALUE_IN_SELECTED_FRONTIERS"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="append", default=None, help="Gate artifact to include; repeatable.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p686-artifact", default=str(DEFAULT_P686_ARTIFACT))
    parser.add_argument("--p688-artifact", default=str(DEFAULT_P688_ARTIFACT))
    args = parser.parse_args()

    gate_paths = [Path(path) for path in (args.gate or [str(path) for path in DEFAULT_GATES])]
    input_rows = p687.load_unique_cost_rows(gate_paths)
    successor_rows = p685.build_successor_rows(input_rows)
    policy_specs = []
    policy_specs.extend(load_policy_folds(Path(args.p686_artifact), "p686", [P686_POLICY]))
    policy_specs.extend(load_policy_folds(Path(args.p688_artifact), "p688"))
    policy_results = [evaluate_policy_spec(spec, successor_rows) for spec in policy_specs]
    broad = broad_summary(successor_rows)
    claim_status = determine_claim(policy_results, broad)
    lead_by_false_rank = max(
        policy_results,
        key=lambda result: (
            result["summary"]["heldout_false_rank_or_relation_value_row_count"],
            result["summary"]["heldout_false_rank_excess_sum"],
            result["summary"]["heldout_false_rank_excess_per_false_replay"],
            result["summary"]["heldout_positive_pair_hits"],
        ),
    )
    lead_by_pair_hits = max(
        policy_results,
        key=lambda result: (
            result["summary"]["heldout_positive_pair_hits"],
            result["summary"]["heldout_rank_or_relation_value_row_count"],
            -result["summary"]["heldout_direct_replay_ops_over_rho"],
        ),
    )
    payload = {
        "schema": "ecdlp.low_term_total2_p689_rank_value_relation_surface_audit.v1",
        "created_at": p678.utc_now(),
        "method": "p689_rank_value_relation_surface_audit",
        "claim_status": claim_status,
        "artifacts": {
            "gates": [str(path) for path in gate_paths],
            "p686_artifact": str(args.p686_artifact),
            "p688_artifact": str(args.p688_artifact),
        },
        "parameters": {
            "rank_value": "direct_verified and max(rank - 2, 0)",
            "relation_value": "direct_verified and max(relation_count - 2, 0)",
            "rank_or_relation_value": "direct_verified and (rank >= 3 or relation_count >= 3)",
            "holdout_unit": "successor-positive transition pair",
            "direct_positive_label": "direct_union_public_key_verified and direct_below_rho",
            "dedupe_key": "target|transfer|selector|top_k",
        },
        "summary": {
            "claim_status": claim_status,
            "unique_input_row_count": len(input_rows),
            "successor_row_count": len(successor_rows),
            "positive_row_count": sum(1 for row in successor_rows if row["row_positive"]),
            "broad_all_rows": broad,
            "lead_by_false_rank_value": {
                "artifact": lead_by_false_rank["artifact"],
                "policy": lead_by_false_rank["policy"],
                "summary": lead_by_false_rank["summary"],
            },
            "lead_by_pair_hits": {
                "artifact": lead_by_pair_hits["artifact"],
                "policy": lead_by_pair_hits["policy"],
                "summary": lead_by_pair_hits["summary"],
            },
            "policy_summaries": {
                f"{result['artifact']}::{result['policy']}": result["summary"] for result in policy_results
            },
        },
        "policies": policy_results,
        "honesty_boundary": [
            "This audit uses available direct union rank and relation-count counters from toy-prime gate artifacts.",
            "Rank/relation value here is diagnostic and not a substitute for certificate-level factor-rank verification.",
            "Selector choices are inherited from P686/P688 and use public fields, but rank/relation scoring is post-hoc diagnostic.",
            "A positive diagnostic remains an index-calculus precursor, not an end-to-end faster-than-rho ECDLP algorithm.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "claim_status": claim_status,
                "successor_row_count": len(successor_rows),
                "positive_row_count": sum(1 for row in successor_rows if row["row_positive"]),
                "broad_rank_value": {
                    key: broad[key]
                    for key in (
                        "rank3_direct_verified_row_count",
                        "rank3_false_verified_row_count",
                        "rank_excess_sum",
                        "false_rank_excess_sum",
                        "direct_replay_ops_over_rho",
                    )
                },
                "lead_by_false_rank_value": {
                    "artifact": lead_by_false_rank["artifact"],
                    "policy": lead_by_false_rank["policy"],
                    "summary": lead_by_false_rank["summary"],
                },
                "lead_by_pair_hits": {
                    "artifact": lead_by_pair_hits["artifact"],
                    "policy": lead_by_pair_hits["policy"],
                    "summary": lead_by_pair_hits["summary"],
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
