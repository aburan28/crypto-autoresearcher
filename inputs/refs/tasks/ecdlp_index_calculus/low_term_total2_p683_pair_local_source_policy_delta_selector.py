#!/usr/bin/env python3
"""P683 public pair-local source-policy delta selector audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p682_right207_to_right208_transition_pair_audit as p682
import low_term_total2_p678_right208_salt208_public_selector_audit as p678


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p683_pair_local_source_policy_delta_selector_probe.json"
DEFAULT_GATES = p682.DEFAULT_GATES
POLICIES = ("balanced", "recall_first", "precision_first", "spend_efficiency", "low_false_pair_first")

PRIMARY_PUBLIC_FIELD_SETS: list[tuple[str, tuple[str, ...]]] = [
    ("next_public_case_count_bucket", ("next_public_case_count_bucket",)),
    ("public_count_delta_bucket", ("public_count_delta_bucket",)),
    ("next_public_anchor_set", ("next_public_anchor_set",)),
    ("next_public_left_salt_set", ("next_public_left_salt_set",)),
    ("next_public_row_pair_set", ("next_public_row_pair_set",)),
    ("next_public_mode_set", ("next_public_mode_set",)),
    ("next_public_leaf_signature_set", ("next_public_leaf_signature_set",)),
    ("next_public_gate_unique_set", ("next_public_gate_unique_set",)),
    ("next_public_gate_density_set", ("next_public_gate_density_set",)),
    ("next_public_shared_product_ops_set", ("next_public_shared_product_ops_set",)),
    ("anchor_transition_set", ("anchor_transition_set",)),
    ("left_salt_transition_set", ("left_salt_transition_set",)),
    ("mode_overlap_set", ("mode_overlap_set",)),
    ("left_salt_overlap_set", ("left_salt_overlap_set",)),
    ("leaf_signature_overlap_set", ("leaf_signature_overlap_set",)),
    ("next_anchor_left_salt_signature", ("next_anchor_left_salt_signature",)),
    ("next_mode_anchor_signature", ("next_mode_anchor_signature",)),
    ("next_mode_left_salt_signature", ("next_mode_left_salt_signature",)),
    ("gate_profile_delta_signature", ("gate_profile_delta_signature",)),
    ("source_policy_delta_signature", ("source_policy_delta_signature",)),
    (
        "count_delta_next_mode_left_salt",
        ("public_count_delta_bucket", "next_public_mode_set", "next_public_left_salt_set"),
    ),
    (
        "overlap_next_anchor_left_salt",
        ("mode_overlap_set", "left_salt_overlap_set", "next_public_anchor_set", "next_public_left_salt_set"),
    ),
    (
        "gate_profile_next_anchor_left_salt",
        ("next_public_gate_unique_set", "next_public_gate_density_set", "next_public_anchor_set", "next_public_left_salt_set"),
    ),
]

RANK_DIAGNOSTIC_FIELD_SETS: list[tuple[str, tuple[str, ...]]] = [
    ("next_rank_set", ("next_rank_set",)),
    ("next_relation_count_bucket_set", ("next_relation_count_bucket_set",)),
    ("next_rank_relation_signature", ("next_rank_relation_signature",)),
    ("next_rank_anchor_signature", ("next_rank_set", "next_public_anchor_set")),
    ("next_rank_left_salt_signature", ("next_rank_set", "next_public_left_salt_set")),
]


def count_bucket(count: int) -> str:
    if count <= 0:
        return "0"
    if count == 1:
        return "1"
    if count <= 3:
        return "2-3"
    if count <= 7:
        return "4-7"
    if count <= 15:
        return "8-15"
    if count <= 31:
        return "16-31"
    if count <= 63:
        return "32-63"
    return "64+"


def delta_bucket(next_count: int, previous_count: int) -> str:
    delta = next_count - previous_count
    if delta == 0:
        return "same"
    if delta > 0:
        if delta <= 4:
            return "next_plus_1_4"
        if delta <= 16:
            return "next_plus_5_16"
        return "next_plus_17_plus"
    if delta >= -4:
        return "next_minus_1_4"
    if delta >= -16:
        return "next_minus_5_16"
    return "next_minus_17_plus"


def csv_set(values: set[str]) -> str:
    cleaned = {value for value in values if value and value != "None"}
    return ",".join(sorted(cleaned)) or "none"


def row_value_set(rows: list[dict[str, Any]], key: str) -> str:
    return csv_set({str(row.get(key)) for row in rows})


def left_salt_set(rows: list[dict[str, Any]]) -> str:
    return csv_set({f"salt{row.get('salt_left')}" for row in rows})


def rank_set(rows: list[dict[str, Any]]) -> str:
    return csv_set({str(int(row.get("rank") or 0)) for row in rows})


def relation_count_bucket_set(rows: list[dict[str, Any]]) -> str:
    return csv_set({count_bucket(int(row.get("relation_count") or 0)) for row in rows})


def split_csv(value: str) -> set[str]:
    if not value or value == "none":
        return set()
    return {item for item in value.split(",") if item}


def overlap_csv(left: str, right: str) -> str:
    return csv_set(split_csv(left) & split_csv(right))


def transition_signature(left: str, right: str) -> str:
    return f"{left}->{right}"


def pair_public_features(precursor_rows: list[dict[str, Any]], successor_rows: list[dict[str, Any]]) -> dict[str, str]:
    precursor_count = len(precursor_rows)
    successor_count = len(successor_rows)
    precursor_anchor_set = row_value_set(precursor_rows, "right_anchor")
    successor_anchor_set = row_value_set(successor_rows, "right_anchor")
    precursor_left_set = left_salt_set(precursor_rows)
    successor_left_set = left_salt_set(successor_rows)
    precursor_row_pair_set = row_value_set(precursor_rows, "row_pair")
    successor_row_pair_set = row_value_set(successor_rows, "row_pair")
    precursor_mode_set = row_value_set(precursor_rows, "selector_mode")
    successor_mode_set = row_value_set(successor_rows, "selector_mode")
    precursor_leaf_set = row_value_set(precursor_rows, "leaf_signature")
    successor_leaf_set = row_value_set(successor_rows, "leaf_signature")
    precursor_gate_unique = row_value_set(precursor_rows, "unique_selected_leaf_signature_count")
    successor_gate_unique = row_value_set(successor_rows, "unique_selected_leaf_signature_count")
    precursor_gate_density = row_value_set(precursor_rows, "duplicate_signature_density_bucket")
    successor_gate_density = row_value_set(successor_rows, "duplicate_signature_density_bucket")
    precursor_shared_ops = row_value_set(precursor_rows, "shared_selected_leaf_product_ops")
    successor_shared_ops = row_value_set(successor_rows, "shared_selected_leaf_product_ops")
    features = {
        "precursor_public_case_count_bucket": count_bucket(precursor_count),
        "next_public_case_count_bucket": count_bucket(successor_count),
        "public_count_delta_bucket": delta_bucket(successor_count, precursor_count),
        "precursor_public_anchor_set": precursor_anchor_set,
        "next_public_anchor_set": successor_anchor_set,
        "precursor_public_left_salt_set": precursor_left_set,
        "next_public_left_salt_set": successor_left_set,
        "precursor_public_row_pair_set": precursor_row_pair_set,
        "next_public_row_pair_set": successor_row_pair_set,
        "precursor_public_mode_set": precursor_mode_set,
        "next_public_mode_set": successor_mode_set,
        "precursor_public_leaf_signature_set": precursor_leaf_set,
        "next_public_leaf_signature_set": successor_leaf_set,
        "precursor_public_gate_unique_set": precursor_gate_unique,
        "next_public_gate_unique_set": successor_gate_unique,
        "precursor_public_gate_density_set": precursor_gate_density,
        "next_public_gate_density_set": successor_gate_density,
        "precursor_public_shared_product_ops_set": precursor_shared_ops,
        "next_public_shared_product_ops_set": successor_shared_ops,
        "anchor_transition_set": transition_signature(precursor_anchor_set, successor_anchor_set),
        "left_salt_transition_set": transition_signature(precursor_left_set, successor_left_set),
        "mode_overlap_set": overlap_csv(precursor_mode_set, successor_mode_set),
        "left_salt_overlap_set": overlap_csv(precursor_left_set, successor_left_set),
        "leaf_signature_overlap_set": overlap_csv(precursor_leaf_set, successor_leaf_set),
        "next_anchor_left_salt_signature": f"{successor_anchor_set}|{successor_left_set}",
        "next_mode_anchor_signature": f"{successor_mode_set}|{successor_anchor_set}",
        "next_mode_left_salt_signature": f"{successor_mode_set}|{successor_left_set}",
        "gate_profile_delta_signature": (
            f"u:{precursor_gate_unique}->{successor_gate_unique}|"
            f"d:{precursor_gate_density}->{successor_gate_density}|"
            f"ops:{precursor_shared_ops}->{successor_shared_ops}"
        ),
        "source_policy_delta_signature": (
            f"count:{delta_bucket(successor_count, precursor_count)}|"
            f"mode_overlap:{overlap_csv(precursor_mode_set, successor_mode_set)}|"
            f"left_overlap:{overlap_csv(precursor_left_set, successor_left_set)}|"
            f"anchor:{precursor_anchor_set}->{successor_anchor_set}|"
            f"gate:{successor_gate_unique}/{successor_gate_density}/{successor_shared_ops}"
        ),
        "next_rank_set": rank_set(successor_rows),
        "next_relation_count_bucket_set": relation_count_bucket_set(successor_rows),
    }
    features["next_rank_relation_signature"] = (
        f"rank:{features['next_rank_set']}|relations:{features['next_relation_count_bucket_set']}"
    )
    return features


def summarize_transfer_rows(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    by_transfer: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_transfer.setdefault(int(row["transfer_index"]), []).append(row)
    return dict(sorted(by_transfer.items()))


def build_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_transfer = summarize_transfer_rows(rows)
    pairs: list[dict[str, Any]] = []
    for transfer, current_rows in by_transfer.items():
        next_rows = by_transfer.get(transfer + 1)
        if not next_rows:
            continue
        precursor_public = [row for row in current_rows if p682.right207_anchor8_salt207(row)]
        successor_public = [row for row in next_rows if p682.right208_salt208(row)]
        successor_below = [row for row in successor_public if row["direct_below_rho_verified"]]
        successor_anchor11 = [row for row in successor_public if p682.right208_anchor11_salt203(row)]
        successor_anchor11_below = [row for row in successor_anchor11 if row["direct_below_rho_verified"]]
        successor_rank3 = [row for row in successor_public if row["rank3_direct_verified"]]
        features = pair_public_features(precursor_public, successor_public)
        pair = {
            "pair_id": f"{transfer}->{transfer + 1}",
            "t": transfer,
            "next_t": transfer + 1,
            "t_phase_mod7": f"{transfer % 12}/{transfer % 7}",
            "next_phase_mod7": f"{(transfer + 1) % 12}/{(transfer + 1) % 7}",
            **features,
            "next_right208_public_case_count": len(successor_public),
            "next_right208_below_count": len(successor_below),
            "next_anchor11_salt203_below_count": len(successor_anchor11_below),
            "next_right208_rank3_count": len(successor_rank3),
            "outcome_positive": bool(successor_below),
            "outcome_anchor11_positive": bool(successor_anchor11_below),
            "next_below_row_ids": [row["row_id"] for row in successor_below],
            "next_anchor11_below_row_ids": [row["row_id"] for row in successor_anchor11_below],
        }
        pairs.append(pair)
    pairs.sort(key=lambda pair: int(pair["t"]))
    return pairs


def selector_name(kind: str, fields: tuple[str, ...], values: tuple[str, ...]) -> str:
    return f"{kind}::" + ",".join(f"{field}={value}" for field, value in zip(fields, values))


def selector_key(fields: tuple[str, ...], pair: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(pair.get(field)) for field in fields)


def generate_selectors(
    pairs: list[dict[str, Any]], field_sets: list[tuple[str, tuple[str, ...]]], selector_class: str
) -> list[dict[str, Any]]:
    positive_pairs = [pair for pair in pairs if pair["outcome_positive"]]
    selectors: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...], tuple[str, ...]]] = set()
    for kind, fields in field_sets:
        for pair in positive_pairs:
            values = selector_key(fields, pair)
            key = (kind, fields, values)
            if key in seen:
                continue
            seen.add(key)
            selectors.append(
                {
                    "selector": selector_name(kind, fields, values),
                    "kind": kind,
                    "class": selector_class,
                    "fields": list(fields),
                    "values": list(values),
                    "uses_transfer_identity": False,
                    "uses_verifier_label_as_feature": False,
                    "uses_rank_diagnostic": selector_class == "rank_diagnostic",
                }
            )
    return selectors


def pair_matches(selector: dict[str, Any], pair: dict[str, Any]) -> bool:
    for field, value in zip(selector["fields"], selector["values"]):
        if str(pair.get(field)) != value:
            return False
    return True


def evaluate_selector(selector: dict[str, Any], pairs: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [pair for pair in pairs if pair_matches(selector, pair)]
    positives = [pair for pair in selected if pair["outcome_positive"]]
    available_positive_pairs = sum(1 for pair in pairs if pair["outcome_positive"])
    available_below_rows = sum(int(pair["next_right208_below_count"]) for pair in pairs)
    selected_below_rows = sum(int(pair["next_right208_below_count"]) for pair in selected)
    selected_anchor11_rows = sum(int(pair["next_anchor11_salt203_below_count"]) for pair in selected)
    selected_rank3_rows = sum(int(pair["next_right208_rank3_count"]) for pair in selected)
    false_pairs = [pair for pair in selected if not pair["outcome_positive"]]
    return {
        "selected_pair_count": len(selected),
        "positive_pair_count": len(positives),
        "false_pair_count": len(false_pairs),
        "next_right208_public_case_count": sum(int(pair["next_right208_public_case_count"]) for pair in selected),
        "next_right208_below_count": selected_below_rows,
        "next_anchor11_salt203_below_count": selected_anchor11_rows,
        "next_right208_rank3_count": selected_rank3_rows,
        "pair_precision": len(positives) / len(selected) if selected else 0.0,
        "pair_recall": len(positives) / max(1, available_positive_pairs),
        "below_row_recall": selected_below_rows / max(1, available_below_rows),
        "selected_pairs": [pair["pair_id"] for pair in selected],
        "positive_pairs": [pair["pair_id"] for pair in positives],
        "false_pairs": [pair["pair_id"] for pair in false_pairs[:80]],
        "below_row_examples": [row for pair in positives for row in pair["next_below_row_ids"][:4]][:24],
    }


def evaluate_custom_pairs(selected: list[dict[str, Any]], all_pairs: list[dict[str, Any]]) -> dict[str, Any]:
    selected_ids = {pair["pair_id"] for pair in selected}
    selector = {"fields": ["pair_id"], "values": []}
    result = evaluate_selector(selector, [])
    positives = [pair for pair in selected if pair["outcome_positive"]]
    available_positive_pairs = sum(1 for pair in all_pairs if pair["outcome_positive"])
    available_below_rows = sum(int(pair["next_right208_below_count"]) for pair in all_pairs)
    below_count = sum(int(pair["next_right208_below_count"]) for pair in selected)
    anchor11_count = sum(int(pair["next_anchor11_salt203_below_count"]) for pair in selected)
    rank3_count = sum(int(pair["next_right208_rank3_count"]) for pair in selected)
    result.update(
        {
            "selected_pair_count": len(selected),
            "positive_pair_count": len(positives),
            "false_pair_count": len(selected) - len(positives),
            "next_right208_public_case_count": sum(int(pair["next_right208_public_case_count"]) for pair in selected),
            "next_right208_below_count": below_count,
            "next_anchor11_salt203_below_count": anchor11_count,
            "next_right208_rank3_count": rank3_count,
            "pair_precision": len(positives) / len(selected) if selected else 0.0,
            "pair_recall": len(positives) / max(1, available_positive_pairs),
            "below_row_recall": below_count / max(1, available_below_rows),
            "selected_pairs": sorted(selected_ids),
            "positive_pairs": [pair["pair_id"] for pair in positives],
            "false_pairs": [pair["pair_id"] for pair in selected if not pair["outcome_positive"]],
            "below_row_examples": [row for pair in positives for row in pair["next_below_row_ids"][:4]][:24],
        }
    )
    return result


def f1(precision: float, recall: float) -> float:
    return (2.0 * precision * recall / (precision + recall)) if precision + recall else 0.0


def policy_score(policy: str, evaluation: dict[str, Any]) -> tuple[Any, ...]:
    precision = float(evaluation["pair_precision"])
    recall = float(evaluation["pair_recall"])
    below = int(evaluation["next_right208_below_count"])
    positives = int(evaluation["positive_pair_count"])
    false_pairs = int(evaluation["false_pair_count"])
    selected = int(evaluation["selected_pair_count"])
    rank3 = int(evaluation["next_right208_rank3_count"])
    public_cases = int(evaluation["next_right208_public_case_count"])
    if policy == "recall_first":
        return (recall, below, positives, -false_pairs, -public_cases, precision, -selected)
    if policy == "precision_first":
        return (precision, positives, below, recall, -false_pairs, -public_cases, -selected)
    if policy == "spend_efficiency":
        return (
            below / max(1, public_cases),
            positives / max(1, selected),
            below,
            positives,
            precision,
            -false_pairs,
            -public_cases,
            -selected,
        )
    if policy == "low_false_pair_first":
        return (-false_pairs, precision, positives, below, recall, rank3, -public_cases, -selected)
    return (f1(precision, recall), below, positives, precision, recall, -false_pairs, -public_cases, -selected)


def choose_selector(policy: str, selectors: list[dict[str, Any]], train_pairs: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated = []
    for selector in selectors:
        training = evaluate_selector(selector, train_pairs)
        if training["positive_pair_count"] <= 0:
            continue
        evaluated.append((policy_score(policy, training), selector, training))
    if not evaluated:
        return {"selector": None, "training": None}
    evaluated.sort(key=lambda item: item[0], reverse=True)
    _, selector, training = evaluated[0]
    return {"selector": selector, "training": training}


def loto_audit(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positive_pairs = [pair for pair in pairs if pair["outcome_positive"]]
    folds: list[dict[str, Any]] = []
    for holdout in positive_pairs:
        train_pairs = [pair for pair in pairs if pair["pair_id"] != holdout["pair_id"]]
        primary_selectors = generate_selectors(train_pairs, PRIMARY_PUBLIC_FIELD_SETS, "primary_public")
        rank_selectors = generate_selectors(train_pairs, RANK_DIAGNOSTIC_FIELD_SETS, "rank_diagnostic")
        class_policies = {}
        for selector_class, selectors in {
            "primary_public": primary_selectors,
            "rank_diagnostic": rank_selectors,
        }.items():
            policies = {}
            for policy in POLICIES:
                choice = choose_selector(policy, selectors, train_pairs)
                selector = choice["selector"]
                if selector is None:
                    policies[policy] = {"selector": None, "training": None, "heldout": None}
                    continue
                policies[policy] = {
                    "selector": selector,
                    "training": choice["training"],
                    "heldout": evaluate_selector(selector, [holdout]),
                    "all_pairs": evaluate_selector(selector, pairs),
                }
            class_policies[selector_class] = policies
        folds.append(
            {
                "holdout_pair": holdout["pair_id"],
                "holdout_next_right208_below_count": holdout["next_right208_below_count"],
                "holdout_next_anchor11_salt203_below_count": holdout["next_anchor11_salt203_below_count"],
                "primary_candidate_selector_count": len(primary_selectors),
                "rank_diagnostic_candidate_selector_count": len(rank_selectors),
                "policies": class_policies,
            }
        )
    return folds


def aggregate_folds(folds: list[dict[str, Any]], selector_class: str) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for policy in POLICIES:
        heldout_hits = 0
        heldout_below = 0
        heldout_anchor11 = 0
        heldout_available_below = 0
        selector_kinds: Counter[str] = Counter()
        selected_pair_count = 0
        false_pair_count = 0
        hit_pairs: list[str] = []
        chosen_selectors: list[str] = []
        for fold in folds:
            heldout_available_below += int(fold["holdout_next_right208_below_count"])
            row = ((fold["policies"].get(selector_class) or {}).get(policy) or {})
            selector = row.get("selector") or {}
            heldout = row.get("heldout") or {}
            all_pairs = row.get("all_pairs") or {}
            below = int(heldout.get("next_right208_below_count") or 0)
            anchor11 = int(heldout.get("next_anchor11_salt203_below_count") or 0)
            if below:
                heldout_hits += 1
                hit_pairs.append(str(fold["holdout_pair"]))
            heldout_below += below
            heldout_anchor11 += anchor11
            selected_pair_count += int(all_pairs.get("selected_pair_count") or 0)
            false_pair_count += int(all_pairs.get("false_pair_count") or 0)
            if selector.get("kind"):
                selector_kinds[str(selector["kind"])] += 1
            if selector.get("selector"):
                chosen_selectors.append(str(selector["selector"]))
        summary[policy] = {
            "fold_count": len(folds),
            "heldout_positive_pair_hits": heldout_hits,
            "heldout_hit_pairs": hit_pairs,
            "heldout_next_right208_below_count": heldout_below,
            "heldout_next_anchor11_salt203_below_count": heldout_anchor11,
            "heldout_available_next_right208_below_count": heldout_available_below,
            "heldout_below_row_recall": heldout_below / max(1, heldout_available_below),
            "aggregate_all_pairs_selected_pair_count": selected_pair_count,
            "aggregate_all_pairs_false_pair_count": false_pair_count,
            "selector_kind_counts": dict(selector_kinds),
            "chosen_selectors": chosen_selectors,
        }
    return summary


def fixed_diagnostics(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    all_pairs = evaluate_custom_pairs(pairs, pairs)
    positive_pairs = [pair for pair in pairs if pair["outcome_positive"]]
    return {
        "broad_all_pairs": {
            "selector": {
                "selector": "all_pairs",
                "fields": [],
                "values": [],
                "uses_transfer_identity": False,
                "uses_verifier_label_as_feature": False,
                "uses_rank_diagnostic": False,
            },
            "evaluation": all_pairs,
        },
        "oracle_positive_pairs": {
            "selector": {
                "selector": "oracle_positive_pairs",
                "fields": ["outcome_positive"],
                "values": ["true"],
                "uses_transfer_identity": False,
                "uses_verifier_label_as_feature": True,
                "uses_rank_diagnostic": False,
            },
            "evaluation": evaluate_custom_pairs(positive_pairs, pairs),
        },
    }


def non_broad_policy_rows(summary: dict[str, dict[str, Any]], pair_count: int) -> list[dict[str, Any]]:
    rows = []
    for row in summary.values():
        broad_selected = int(row["fold_count"]) * pair_count
        if int(row["aggregate_all_pairs_selected_pair_count"]) < broad_selected:
            rows.append(row)
    return rows


def materially_reduced_policy_rows(summary: dict[str, dict[str, Any]], pair_count: int) -> list[dict[str, Any]]:
    rows = []
    for row in summary.values():
        broad_selected = int(row["fold_count"]) * pair_count
        selected = int(row["aggregate_all_pairs_selected_pair_count"])
        if selected < broad_selected and selected <= int(0.75 * broad_selected):
            rows.append(row)
    return rows


def determine_claim(
    primary_summary: dict[str, dict[str, Any]], rank_summary: dict[str, dict[str, Any]], pair_count: int
) -> str:
    primary_non_broad = non_broad_policy_rows(primary_summary, pair_count)
    primary_material = materially_reduced_policy_rows(primary_summary, pair_count)
    best_primary_hits = max((row["heldout_positive_pair_hits"] for row in primary_non_broad), default=0)
    best_primary_material_hits = max((row["heldout_positive_pair_hits"] for row in primary_material), default=0)
    best_primary_all_hits = max((row["heldout_positive_pair_hits"] for row in primary_summary.values()), default=0)
    best_primary_recall = max((row["heldout_below_row_recall"] for row in primary_non_broad), default=0.0)
    best_rank_hits = max((row["heldout_positive_pair_hits"] for row in rank_summary.values()), default=0)
    if best_primary_material_hits >= 2:
        return "P683_PUBLIC_SOURCE_POLICY_DELTA_MULTI_HELDOUT_POSITIVE"
    if best_primary_hits == 1:
        return "P683_PUBLIC_SOURCE_POLICY_DELTA_SINGLE_HELDOUT_POSITIVE"
    if best_primary_all_hits and not best_primary_hits and best_rank_hits >= 2:
        return "P683_PRIMARY_PUBLIC_BROAD_EQUIVALENT_RECALL_RANK_DIAGNOSTIC_POSITIVE"
    if best_primary_all_hits and not best_primary_hits:
        return "NEGATIVE_RESULT_P683_PRIMARY_PUBLIC_SOURCE_POLICY_DELTAS_BROAD_EQUIVALENT_ONLY"
    if best_rank_hits >= 2:
        return "P683_RANK_DIAGNOSTIC_HELDOUT_POSITIVE_PUBLIC_DELTA_NEGATIVE"
    if best_rank_hits == 1:
        return "P683_RANK_DIAGNOSTIC_SINGLE_HELDOUT_PUBLIC_DELTA_NEGATIVE"
    if best_primary_recall > 0:
        return "P683_PUBLIC_SOURCE_POLICY_DELTA_WEAK_ROW_RECALL"
    return "NEGATIVE_RESULT_P683_PUBLIC_SOURCE_POLICY_DELTAS_NO_HELDOUT_RECALL"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="append", default=None, help="Gate artifact to include; repeatable.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    gate_paths = [Path(path) for path in (args.gate or [str(path) for path in DEFAULT_GATES])]
    rows = p682.load_unique_rows(gate_paths)
    pairs = build_pairs(rows)
    folds = loto_audit(pairs)
    primary_summary = aggregate_folds(folds, "primary_public")
    rank_summary = aggregate_folds(folds, "rank_diagnostic")
    diagnostics = fixed_diagnostics(pairs)
    claim_status = determine_claim(primary_summary, rank_summary, len(pairs))
    positive_pairs = [pair for pair in pairs if pair["outcome_positive"]]
    payload = {
        "schema": "ecdlp.low_term_total2_p683_pair_local_source_policy_delta_selector.v1",
        "created_at": p678.utc_now(),
        "method": "p683_pair_local_source_policy_delta_selector",
        "claim_status": claim_status,
        "artifacts": {"gates": [str(path) for path in gate_paths]},
        "parameters": {
            "primary_public_field_sets": [
                {"kind": kind, "fields": list(fields)} for kind, fields in PRIMARY_PUBLIC_FIELD_SETS
            ],
            "rank_diagnostic_field_sets": [
                {"kind": kind, "fields": list(fields)} for kind, fields in RANK_DIAGNOSTIC_FIELD_SETS
            ],
            "policies": list(POLICIES),
            "outcome": "successor transfer has at least one below-rho direct verified right208/salt208 row",
            "dedupe_key": "target|transfer|selector|top_k",
        },
        "summary": {
            "claim_status": claim_status,
            "unique_row_count": len(rows),
            "pair_count": len(pairs),
            "positive_pair_count": len(positive_pairs),
            "positive_pairs": [pair["pair_id"] for pair in positive_pairs],
            "total_successor_right208_below_rows": sum(pair["next_right208_below_count"] for pair in pairs),
            "primary_public_policy_summary": primary_summary,
            "rank_diagnostic_policy_summary": rank_summary,
            "primary_non_broad_policies": [
                policy
                for policy, row in primary_summary.items()
                if row in non_broad_policy_rows(primary_summary, len(pairs))
            ],
            "primary_materially_reduced_policies": [
                policy
                for policy, row in primary_summary.items()
                if row in materially_reduced_policy_rows(primary_summary, len(pairs))
            ],
            "fixed_diagnostics": diagnostics,
        },
        "pairs": pairs,
        "folds": folds,
        "honesty_boundary": [
            "Primary selectors use source/gate geometry fields only: counts, sets, overlaps, and delta signatures.",
            "Rank-diagnostic selectors are reported separately and do not determine a primary public positive claim.",
            "No selector uses exact transfer identity, below-rho labels, or direct public-key verification labels as fields.",
            "Pair-level held-out recall is relation-event evidence, not a complete faster-than-rho ECDLP algorithm.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "claim_status": claim_status,
                "unique_row_count": len(rows),
                "pair_count": len(pairs),
                "positive_pair_count": len(positive_pairs),
                "positive_pairs": [pair["pair_id"] for pair in positive_pairs],
                "primary_public_policy_summary": primary_summary,
                "rank_diagnostic_policy_summary": rank_summary,
                "fixed_diagnostics": diagnostics,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
