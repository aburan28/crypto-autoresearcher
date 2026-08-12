#!/usr/bin/env python3
"""P1015 public invariant learner after the P1014 frozen-rule failure."""

from __future__ import annotations

import argparse
import itertools
import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1008_p231_expanded_rule_early_stop_11984 as p1008
import low_term_total2_p1009_p231_expanded_rule_family_fallback_11984 as p1009
import low_term_total2_p1010_p231_stress_row_completion_11992 as p1010


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1015_p231_cross_window_public_invariant_12056.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1015_p231_cross_window_public_invariant_12056_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1015_p231_cross_window_public_invariant_12056.v1"
DEFAULT_TARGET = p1010.DEFAULT_TARGET
TRAIN_WINDOWS = ["12040_12047", "12048_12055"]
PRIMARY_WINDOW = "12056_12063"
SWEEP_WINDOWS = ["12064_12071", "12072_12079", "12080_12087", "12088_12095"]
MAX_SELECTED_PER_WINDOW = 96
MAX_REPRESENTATIVE_CANDIDATES = 12

Predicate = Callable[[dict[str, Any]], bool]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1010.int_value(value, default)


def safe_ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    return p1007.safe_ratio(numerator, denominator)


def features(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("features") or {}


def source_case(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_case") or {}


def source_ops(row: dict[str, Any]) -> float:
    return float(source_case(row).get("source_ops_over_rho") or 0.0)


def selector(row: dict[str, Any]) -> str:
    return str(features(row).get("leaf_selector"))


def selector_prefix(value: str) -> str:
    for prefix in (
        "mode_cost_low_term_support",
        "mode_low_term_support",
        "mode_double_pair",
        "mode_cost_low_leaf_index",
        "mode_low_leaf_index",
        "mode_cost_hybrid_support_monic_b",
        "mode_hybrid_support_monic_b",
        "mode_cost_",
        "mode_hybrid",
    ):
        if value.startswith(prefix):
            return prefix
    return value


def total_suffix(value: str) -> int:
    match = re.search(r"total(\d+)$", value)
    return int(match.group(1)) if match else 0


def leaf_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in features(row).get("unique_leaf_indices") or [])


def leaf_set(row: dict[str, Any]) -> set[int]:
    return set(leaf_tuple(row))


def leaf_gap_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in features(row).get("leaf_gap_tuple") or [])


def max_leaf_gap(row: dict[str, Any]) -> int:
    gaps = leaf_gap_tuple(row)
    return max(gaps) if gaps else -1


def transfer_index(row: dict[str, Any]) -> int:
    return int_value(source_case(row).get("transfer_index"))


def transfer_offset(row: dict[str, Any]) -> int:
    return transfer_index(row) % 8


def top_k(row: dict[str, Any]) -> int:
    return int_value(features(row).get("top_k"))


def salt_gap(row: dict[str, Any]) -> int:
    return int_value(features(row).get("salt_gap"))


def unique_leaf_count(row: dict[str, Any]) -> int:
    return int_value(features(row).get("unique_leaf_count"), len(leaf_set(row)))


def source_positive(row: dict[str, Any]) -> bool:
    return p1010.source_stress_positive(row)


def selected_case_summary(row: dict[str, Any]) -> dict[str, Any]:
    f = features(row)
    return {
        **p1010.selected_case_summary(row),
        "leaf_gap_tuple": f.get("leaf_gap_tuple"),
        "salt_gap": f.get("salt_gap"),
        "selector_prefix": selector_prefix(selector(row)),
        "total_suffix": total_suffix(selector(row)),
        "unique_leaf_count": f.get("unique_leaf_count"),
    }


def add_rule(rules: list[dict[str, Any]], name: str, description: str, predicate: Predicate) -> None:
    if any(rule["name"] == name for rule in rules):
        return
    rules.append({"description": description, "members": [name], "name": name, "predicate": predicate})


def and_rule(parts: list[dict[str, Any]]) -> dict[str, Any]:
    names = [part["name"] for part in parts]
    predicates = [part["predicate"] for part in parts]

    def predicate(row: dict[str, Any], predicates: list[Predicate] = predicates) -> bool:
        return all(item(row) for item in predicates)

    return {
        "description": " AND ".join(part["description"] for part in parts),
        "members": names,
        "name": " AND ".join(names),
        "predicate": predicate,
    }


def primitive_rules(train_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positives = [row for row in train_rows if source_positive(row)]
    rules: list[dict[str, Any]] = []
    for offset in sorted({transfer_offset(row) for row in positives}):
        add_rule(rules, f"offset={offset}", f"transfer index modulo 8 == {offset}", lambda row, offset=offset: transfer_offset(row) == offset)
    for value in sorted({top_k(row) for row in positives}):
        add_rule(rules, f"topk={value}", f"top_k == {value}", lambda row, value=value: top_k(row) == value)
    for value in sorted({selector(row) for row in positives}):
        add_rule(rules, f"selector={value}", f"leaf_selector == {value}", lambda row, value=value: selector(row) == value)
    for value in sorted({selector_prefix(selector(row)) for row in positives}):
        add_rule(
            rules,
            f"selector_prefix={value}",
            f"leaf_selector starts with {value}",
            lambda row, value=value: selector(row).startswith(value),
        )
    for value in sorted({total_suffix(selector(row)) for row in positives}):
        add_rule(rules, f"total_suffix={value}", f"selector total suffix == {value}", lambda row, value=value: total_suffix(selector(row)) == value)
        add_rule(rules, f"total_suffix>={value}", f"selector total suffix >= {value}", lambda row, value=value: total_suffix(selector(row)) >= value)
    for value in sorted({leaf_tuple(row) for row in positives}):
        add_rule(rules, f"leaf_tuple={list(value)}", f"unique_leaf_indices == {list(value)}", lambda row, value=value: leaf_tuple(row) == value)
    for leaf in sorted({leaf for row in positives for leaf in leaf_set(row)}):
        add_rule(rules, f"contains_leaf={leaf}", f"unique_leaf_indices contains {leaf}", lambda row, leaf=leaf: leaf in leaf_set(row))
    for value in sorted({salt_gap(row) for row in positives}):
        add_rule(rules, f"salt_gap={value}", f"salt_gap == {value}", lambda row, value=value: salt_gap(row) == value)
        add_rule(rules, f"salt_gap<={value}", f"salt_gap <= {value}", lambda row, value=value: salt_gap(row) <= value)
        add_rule(rules, f"salt_gap>={value}", f"salt_gap >= {value}", lambda row, value=value: salt_gap(row) >= value)
    for value in sorted({unique_leaf_count(row) for row in positives}):
        add_rule(rules, f"unique_leaf_count={value}", f"unique_leaf_count == {value}", lambda row, value=value: unique_leaf_count(row) == value)
    for value in sorted({max_leaf_gap(row) for row in positives if max_leaf_gap(row) >= 0}):
        add_rule(rules, f"max_leaf_gap={value}", f"max leaf gap == {value}", lambda row, value=value: max_leaf_gap(row) == value)
        add_rule(rules, f"max_leaf_gap>={value}", f"max leaf gap >= {value}", lambda row, value=value: max_leaf_gap(row) >= value)
    return rules


def row_signature_rules(row: dict[str, Any], primitives_by_name: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    names = [
        f"offset={transfer_offset(row)}",
        f"topk={top_k(row)}",
        f"selector={selector(row)}",
        f"selector_prefix={selector_prefix(selector(row))}",
        f"total_suffix={total_suffix(selector(row))}",
        f"total_suffix>={total_suffix(selector(row))}",
        f"leaf_tuple={list(leaf_tuple(row))}",
        f"salt_gap={salt_gap(row)}",
        f"unique_leaf_count={unique_leaf_count(row)}",
    ]
    names.extend(f"contains_leaf={leaf}" for leaf in sorted(leaf_set(row)))
    names = [name for name in names if name in primitives_by_name]
    templates = [
        ("topk", "selector"),
        ("topk", "selector_prefix"),
        ("topk", "leaf_tuple"),
        ("topk", "contains_leaf"),
        ("selector", "leaf_tuple"),
        ("selector_prefix", "leaf_tuple"),
        ("selector_prefix", "contains_leaf"),
        ("offset", "topk"),
        ("offset", "selector_prefix"),
        ("offset", "contains_leaf"),
        ("topk", "salt_gap"),
        ("topk", "salt_gap", "selector_prefix"),
        ("topk", "selector_prefix", "contains_leaf"),
        ("offset", "topk", "selector_prefix"),
        ("offset", "topk", "contains_leaf"),
        ("topk", "selector", "leaf_tuple"),
        ("topk", "selector_prefix", "leaf_tuple"),
    ]
    out: list[dict[str, Any]] = []
    for template in templates:
        groups: list[list[str]] = []
        for prefix in template:
            matching = [name for name in names if name.startswith(prefix + "=") or name.startswith(prefix + ">=") or name.startswith(prefix + "<=")]
            if not matching:
                groups = []
                break
            groups.append(matching)
        for combo in itertools.product(*groups):
            parts = [primitives_by_name[name] for name in combo]
            out.append(and_rule(parts))
    return out


def candidate_rules(train_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    primitives = primitive_rules(train_rows)
    by_name = {rule["name"]: rule for rule in primitives}
    candidates = list(primitives)
    for row in [row for row in train_rows if source_positive(row)]:
        candidates.extend(row_signature_rules(row, by_name))
    unique: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        unique.setdefault(candidate["name"], candidate)
    return list(unique.values())


def stress_score(rows: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    positives = [row for row in rows if source_positive(row)]
    selected = [row for row in rows if predicate(row)]
    selected_positive = [row for row in selected if source_positive(row)]
    selected_ops = sum(source_ops(row) for row in selected)
    return {
        "case_count": len(rows),
        "positive_count": len(positives),
        "precision": safe_ratio(len(selected_positive), len(selected)),
        "recall": safe_ratio(len(selected_positive), len(positives)),
        "selected_count": len(selected),
        "selected_direct_sum_ops_over_rho": round(selected_ops, 8),
        "selected_positive_count": len(selected_positive),
        "useful_amortized_ops_over_rho": safe_ratio(selected_ops, len(selected_positive)),
    }


def selected_signature(rows_by_window: dict[str, list[dict[str, Any]]], predicate: Predicate) -> tuple[str, ...]:
    return tuple(
        sorted(
            str(row.get("case_id"))
            for rows in rows_by_window.values()
            for row in rows
            if predicate(row)
        )
    )


def useful_score(value: Any) -> float:
    return float(value) if value is not None else 10**9


def rank_candidates(candidates: list[dict[str, Any]], train_by_window: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    for candidate in candidates:
        signature = selected_signature(train_by_window, candidate["predicate"])
        if not signature or signature in seen:
            continue
        seen.add(signature)
        per_window = {window: stress_score(rows, candidate["predicate"]) for window, rows in train_by_window.items()}
        if any(int_value(score.get("selected_count")) > MAX_SELECTED_PER_WINDOW for score in per_window.values()):
            continue
        hit_windows = sum(1 for score in per_window.values() if int_value(score.get("selected_positive_count")) > 0)
        if hit_windows == 0:
            continue
        total_selected = sum(int_value(score.get("selected_count")) for score in per_window.values())
        total_positive = sum(int_value(score.get("selected_positive_count")) for score in per_window.values())
        min_precision = min(float(score.get("precision") or 0.0) for score in per_window.values())
        mean_precision = sum(float(score.get("precision") or 0.0) for score in per_window.values()) / len(per_window)
        useful_values = [useful_score(score.get("useful_amortized_ops_over_rho")) for score in per_window.values()]
        scored.append(
            {
                "candidate": {
                    "description": candidate["description"],
                    "member_count": len(candidate["members"]),
                    "members": candidate["members"],
                    "name": candidate["name"],
                },
                "hit_windows": hit_windows,
                "mean_precision": round(mean_precision, 8),
                "min_precision": round(min_precision, 8),
                "per_window": per_window,
                "predicate": candidate["predicate"],
                "total_positive": total_positive,
                "total_selected": total_selected,
                "useful_mean": round(sum(useful_values) / len(useful_values), 8),
            }
        )
    scored.sort(
        key=lambda row: (
            -int_value(row.get("hit_windows")),
            -float(row.get("min_precision") or 0.0),
            -float(row.get("mean_precision") or 0.0),
            useful_score(row.get("useful_mean")),
            int_value(row.get("total_selected")),
            int_value((row.get("candidate") or {}).get("member_count")),
            str((row.get("candidate") or {}).get("name")),
        )
    )
    return scored


def choose_candidate(scored: list[dict[str, Any]]) -> dict[str, Any] | None:
    viable = [
        row
        for row in scored
        if int_value(row.get("hit_windows")) == len(TRAIN_WINDOWS)
        and int_value(row.get("total_positive")) > 0
        and all(int_value(score.get("selected_count")) <= MAX_SELECTED_PER_WINDOW for score in row["per_window"].values())
    ]
    return viable[0] if viable else (scored[0] if scored else None)


def lane_full(
    name: str,
    rows: list[dict[str, Any]],
    candidate: dict[str, Any],
    order: dict[str, Any],
    baseline_rank: int,
) -> dict[str, Any]:
    predicate = candidate["predicate"]
    selected = [row for row in rows if predicate(row)]
    analysis, groups = p1005.scalar_valid_groups(
        selected,
        {"lane": name, "rule_family": candidate["candidate"]["name"], "rule_members": candidate["candidate"]["members"]},
        baseline_rank,
    )
    fixed_first = p1008.first_hit_summary(selected, groups, order)
    return {
        "analysis_summary": analysis.get("summary"),
        "fixed_order_first_hit": fixed_first,
        "groups": [p1005.compact_group(group) for group in groups[:12]],
        "selected_cases": [selected_case_summary(row) for row in selected[:48]],
        "stress_selection": stress_score(rows, predicate),
    }


def score_order(order: dict[str, Any], lanes: list[dict[str, Any]]) -> dict[str, Any]:
    hits = []
    misses = 0
    for lane in lanes:
        first = (p1008.first_hit_summary(lane["selected"], lane["groups"], order).get("first_scalar_valid_group"))
        if first:
            hits.append(
                {
                    "charged_ops_over_rho": first.get("charged_ops_over_rho"),
                    "lane": lane["name"],
                    "ordered_index": first.get("ordered_index"),
                }
            )
        else:
            misses += 1
    charges = [float(hit["charged_ops_over_rho"]) for hit in hits]
    return {
        "below_rho_hit_count": sum(1 for value in charges if value < 1.0),
        "hit_count": len(hits),
        "lane_hits": hits,
        "max_charge": max(charges) if charges else None,
        "mean_charge": round(sum(charges) / len(charges), 8) if charges else None,
        "miss_count": misses,
        "order_description": order["description"],
        "order_name": order["name"],
    }


def choose_order(training_rows_by_window: dict[str, list[dict[str, Any]]], candidate: dict[str, Any], baseline_rank: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    lanes = []
    for window, rows in training_rows_by_window.items():
        selected = [row for row in rows if candidate["predicate"](row)]
        analysis, groups = p1005.scalar_valid_groups(
            selected,
            {"lane": f"training_{window}", "rule_family": candidate["candidate"]["name"]},
            baseline_rank,
        )
        lanes.append({"analysis": analysis, "groups": groups, "name": f"training_{window}", "selected": selected})
    scores = [score_order(order, lanes) for order in p1009.public_order_candidates()]
    scores.sort(
        key=lambda row: (
            -int_value(row.get("below_rho_hit_count")),
            -int_value(row.get("hit_count")),
            useful_score(row.get("mean_charge")),
            useful_score(row.get("max_charge")),
            str(row.get("order_name")),
        )
    )
    by_name = {order["name"]: order for order in p1009.public_order_candidates()}
    return by_name[str(scores[0]["order_name"])], scores


def lane_success(lane: dict[str, Any]) -> bool:
    stress = lane.get("stress_selection") or {}
    analysis = lane.get("analysis_summary") or {}
    first_hit = lane.get("fixed_order_first_hit") or {}
    first = first_hit.get("first_scalar_valid_group") or {}
    return (
        int_value(stress.get("selected_positive_count")) > 0
        and int_value(analysis.get("context_safe_scalar_valid_group_count")) > 0
        and bool(first_hit.get("first_scalar_valid_group_below_rho"))
        and float(first.get("charged_ops_over_rho") or 10**9) < 1.0
    )


def compact_lane_summary(lane: dict[str, Any]) -> dict[str, Any]:
    stress = lane.get("stress_selection") or {}
    analysis = lane.get("analysis_summary") or {}
    first_hit = lane.get("fixed_order_first_hit") or {}
    first = first_hit.get("first_scalar_valid_group") or {}
    return {
        "best_amortized_ops_over_rho": analysis.get("scalar_valid_best_amortized_ops_over_rho"),
        "context_safe_scalar_valid_group_count": analysis.get("context_safe_scalar_valid_group_count"),
        "fixed_first_below_rho": first_hit.get("first_scalar_valid_group_below_rho"),
        "fixed_first_charge": first.get("charged_ops_over_rho"),
        "fixed_first_secret": first.get("derived_secret"),
        "precision": stress.get("precision"),
        "recall": stress.get("recall"),
        "selected_count": stress.get("selected_count"),
        "selected_positive_count": stress.get("selected_positive_count"),
        "total_selected_ops_over_rho": stress.get("selected_direct_sum_ops_over_rho"),
    }


def determine_claim(candidate: dict[str, Any] | None, primary: dict[str, Any] | None, sweep: dict[str, dict[str, Any]]) -> str:
    if candidate is None:
        return "NEGATIVE_RESULT_P1015_NO_CROSS_WINDOW_CANDIDATE"
    if primary and lane_success(primary):
        return "P1015_CROSS_WINDOW_INVARIANT_PRIMARY_BELOW_RHO"
    if any(lane_success(lane) for lane in sweep.values()):
        return "NEGATIVE_RESULT_P1015_PRIMARY_MISS_WITH_LATER_REAPPEARANCE"
    if primary is None:
        return "NEGATIVE_RESULT_P1015_NO_PRIMARY_LANE"
    stress = primary.get("stress_selection") or {}
    analysis = primary.get("analysis_summary") or {}
    if int_value(stress.get("selected_count")) == 0:
        return "NEGATIVE_RESULT_P1015_PRIMARY_SELECTS_NO_ROWS"
    if int_value(stress.get("selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P1015_PRIMARY_NO_BUILDER_VISIBLE_POSITIVES"
    if int_value(analysis.get("context_safe_scalar_valid_group_count")) == 0:
        return "NEGATIVE_RESULT_P1015_PRIMARY_NO_CONTEXT_SAFE_SCALAR_GROUP"
    return "NEGATIVE_RESULT_P1015_PRIMARY_FIRST_HIT_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = [*TRAIN_WINDOWS, PRIMARY_WINDOW, *SWEEP_WINDOWS]
    by_window, exists = p1010.build_window_rows(windows, args.targets, args.min_source_rank)
    train_by_window = {window: by_window[window] for window in TRAIN_WINDOWS}
    train_rows = [row for window in TRAIN_WINDOWS for row in by_window[window]]
    candidates = candidate_rules(train_rows)
    scored = rank_candidates(candidates, train_by_window)
    chosen = choose_candidate(scored)
    if chosen is None:
        claim = determine_claim(None, None, {})
        return {
            "artifacts": {"contract": str(args.contract), "script": str(Path(__file__))},
            "artifact_hashes": {"contract_sha256": p1005.sha256_file(Path(args.contract)), "script_sha256": p1005.sha256_file(Path(__file__))},
            "claim_status": claim,
            "claim_taxonomy": "NEGATIVE RESULT",
            "method": "p1015_p231_cross_window_public_invariant_12056",
            "parameters": {"targets": [target.strip() for target in args.targets.split(",") if target.strip()]},
            "schema": SCHEMA,
            "summary": {"claim_status": claim, "candidate_count": len(candidates), "scored_candidate_count": len(scored)},
        }
    order, order_scores = choose_order(train_by_window, chosen, args.baseline_rank)
    training_lanes = {
        window: lane_full(f"training_{window}", by_window[window], chosen, order, args.baseline_rank)
        for window in TRAIN_WINDOWS
    }
    primary_lane = lane_full(f"primary_{PRIMARY_WINDOW}", by_window[PRIMARY_WINDOW], chosen, order, args.baseline_rank)
    sweep_lanes = {
        window: lane_full(f"sweep_{window}", by_window[window], chosen, order, args.baseline_rank)
        for window in SWEEP_WINDOWS
    }
    claim = determine_claim(chosen, primary_lane, sweep_lanes)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": {window: p1005.sha256_file(p1007.expanded_source_path(window)) for window in windows},
        },
        "candidate_search": {
            "candidate_count": len(candidates),
            "chosen_training_score": {key: value for key, value in chosen.items() if key != "predicate"},
            "top_candidates": [{key: value for key, value in row.items() if key != "predicate"} for row in scored[:MAX_REPRESENTATIVE_CANDIDATES]],
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim == "P1015_CROSS_WINDOW_INVARIANT_PRIMARY_BELOW_RHO" else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "TRAINING BOUNDARY: predicate and order are fit only on 12040_12047 and 12048_12055.",
            "PRIMARY-VALIDATION BOUNDARY: 12056_12063 is the primary claim window; later positives are stress-sweep evidence.",
            "CONTEXT-SAFE-GATE: scalar-valid groups spanning multiple public fingerprints are rejected.",
            "INDEX-CALCULUS BOUNDARY: this is relation-surface prediction, not sparse linear algebra, target descent, or cryptographic-size evidence.",
        ],
        "method": "p1015_p231_cross_window_public_invariant_12056",
        "order_search": {
            "chosen_order": {"description": order["description"], "name": order["name"]},
            "training_scores": order_scores,
        },
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "max_selected_per_window": MAX_SELECTED_PER_WINDOW,
            "min_source_rank": args.min_source_rank,
            "primary_window": PRIMARY_WINDOW,
            "sweep_windows": SWEEP_WINDOWS,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "training_windows": TRAIN_WINDOWS,
        },
        "rule": chosen["candidate"],
        "schema": SCHEMA,
        "source": {
            "exists": exists,
            "summaries": {window: p1007.source_summary(window) for window in windows},
        },
        "summary": {
            "claim_status": claim,
            "chosen_order": order["name"],
            "primary": compact_lane_summary(primary_lane),
            "primary_success": lane_success(primary_lane),
            "sweep": {window: compact_lane_summary(lane) for window, lane in sweep_lanes.items()},
            "sweep_success_windows": [window for window, lane in sweep_lanes.items() if lane_success(lane)],
            "training": {window: compact_lane_summary(lane) for window, lane in training_lanes.items()},
            "training_hit_windows": chosen.get("hit_windows"),
        },
        "lanes": {
            "primary": primary_lane,
            "sweep": sweep_lanes,
            "training": training_lanes,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1015 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for builder labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    primary = summary.get("primary") or {}
    print(
        "claim={claim} rule={rule} order={order} primary_selected={primary_selected} "
        "primary_pos={primary_pos} primary_groups={primary_groups} primary_first={primary_first} "
        "sweep_success={sweep_success} out={out}".format(
            claim=payload["claim_status"],
            rule=(payload.get("rule") or {}).get("name"),
            order=summary.get("chosen_order"),
            primary_selected=primary.get("selected_count"),
            primary_pos=primary.get("selected_positive_count"),
            primary_groups=primary.get("context_safe_scalar_valid_group_count"),
            primary_first=primary.get("fixed_first_charge"),
            sweep_success=",".join(summary.get("sweep_success_windows") or []) or "none",
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
