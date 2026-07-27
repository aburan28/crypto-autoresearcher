#!/usr/bin/env python3
"""P685 row-level public pre-rank selector audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p682_right207_to_right208_transition_pair_audit as p682
import low_term_total2_p683_pair_local_source_policy_delta_selector as p683
import low_term_total2_p684_public_pre_rank_proxy_selector as p684
import low_term_total2_p678_right208_salt208_public_selector_audit as p678


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p685_row_level_public_pre_rank_selector_probe.json"
DEFAULT_GATES = p682.DEFAULT_GATES
POLICIES = ("balanced", "recall_first", "precision_first", "spend_efficiency", "low_false_row_first")
ROW_PUBLIC_FIELD_SETS: list[tuple[str, tuple[str, ...]]] = [
    ("anchor", ("right_anchor_token",)),
    ("left_salt", ("left_salt_token",)),
    ("row_pair", ("row_pair",)),
    ("selector_mode", ("selector_mode",)),
    ("leaf_signature", ("leaf_signature",)),
    ("top_k", ("top_k_token",)),
    ("mode_anchor", ("selector_mode", "right_anchor_token")),
    ("mode_left_salt", ("selector_mode", "left_salt_token")),
    ("mode_row_pair", ("selector_mode", "row_pair")),
    ("anchor_row_pair", ("right_anchor_token", "row_pair")),
    ("anchor_left_salt", ("right_anchor_token", "left_salt_token")),
    ("row_pair_leaf", ("row_pair", "leaf_signature")),
    ("mode_leaf", ("selector_mode", "leaf_signature")),
    ("anchor_leaf", ("right_anchor_token", "leaf_signature")),
    ("mode_anchor_row_pair", ("selector_mode", "right_anchor_token", "row_pair")),
    ("mode_anchor_leaf", ("selector_mode", "right_anchor_token", "leaf_signature")),
    ("gate_unique", ("unique_selected_leaf_signature_count",)),
    ("gate_density", ("duplicate_signature_density_bucket",)),
    ("gate_shared_ops", ("shared_selected_leaf_product_ops",)),
    ("gate_check_ops", ("direct_selected_leaf_check_ops",)),
    ("gate_product_ops", ("direct_selected_leaf_product_ops",)),
    ("gate_product_saved_ops", ("shared_selected_leaf_product_saved_ops",)),
    ("unique_fraction", ("unique_signature_fraction_bucket",)),
    ("public_gate_bool", ("public_gate_bool_token",)),
    ("mode_gate_unique", ("selector_mode", "unique_selected_leaf_signature_count")),
    ("mode_gate_product_ops", ("selector_mode", "direct_selected_leaf_product_ops")),
    ("mode_gate_product_saved_ops", ("selector_mode", "shared_selected_leaf_product_saved_ops")),
    ("anchor_gate_unique", ("right_anchor_token", "unique_selected_leaf_signature_count")),
    ("anchor_gate_product_ops", ("right_anchor_token", "direct_selected_leaf_product_ops")),
    ("row_pair_gate_product_ops", ("row_pair", "direct_selected_leaf_product_ops")),
    ("mode_row_pair_gate_product_ops", ("selector_mode", "row_pair", "direct_selected_leaf_product_ops")),
    ("mode_anchor_gate_product_ops", ("selector_mode", "right_anchor_token", "direct_selected_leaf_product_ops")),
    ("mode_row_pair_public_bool", ("selector_mode", "row_pair", "public_gate_bool_token")),
]


def row_selector_fields(row: dict[str, Any]) -> dict[str, str]:
    return {
        "right_anchor_token": f"anchor{row.get('right_anchor')}",
        "left_salt_token": f"salt{row.get('salt_left')}",
        "row_pair": str(row.get("row_pair")),
        "selector_mode": str(row.get("selector_mode")),
        "leaf_signature": str(row.get("leaf_signature")),
        "top_k_token": f"top{row.get('top_k')}",
        "unique_selected_leaf_signature_count": str(row.get("unique_selected_leaf_signature_count")),
        "duplicate_signature_density_bucket": str(row.get("duplicate_signature_density_bucket")),
        "shared_selected_leaf_product_ops": str(row.get("shared_selected_leaf_product_ops")),
        "direct_selected_leaf_check_ops": str(row.get("direct_selected_leaf_check_ops")),
        "direct_selected_leaf_product_ops": str(row.get("direct_selected_leaf_product_ops")),
        "shared_selected_leaf_product_saved_ops": str(row.get("shared_selected_leaf_product_saved_ops")),
        "unique_signature_fraction_bucket": str(row.get("unique_signature_fraction_bucket")),
        "public_gate_bool_token": str(row.get("public_gate_bool_token")),
    }


def summarize_transfer_rows(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    by_transfer: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_transfer.setdefault(int(row["transfer_index"]), []).append(row)
    return dict(sorted(by_transfer.items()))


def build_successor_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_transfer = summarize_transfer_rows(rows)
    successor_rows: list[dict[str, Any]] = []
    for transfer in by_transfer:
        next_rows = by_transfer.get(transfer + 1)
        if not next_rows:
            continue
        pair_id = f"{transfer}->{transfer + 1}"
        for row in next_rows:
            if not p682.right208_salt208(row):
                continue
            record = {
                **row,
                **row_selector_fields(row),
                "pair_id": pair_id,
                "pair_t": transfer,
                "pair_next_t": transfer + 1,
                "row_positive": bool(row["direct_below_rho_verified"]),
                "anchor11_salt203_positive": bool(p682.right208_anchor11_salt203(row) and row["direct_below_rho_verified"]),
            }
            successor_rows.append(record)
    successor_rows.sort(key=lambda row: (str(row["pair_id"]), str(row["selector"]), int(row["top_k"])))
    return successor_rows


def selector_name(kind: str, fields: tuple[str, ...], values: tuple[str, ...]) -> str:
    return f"{kind}::" + ",".join(f"{field}={value}" for field, value in zip(fields, values))


def selector_key(fields: tuple[str, ...], row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(row.get(field)) for field in fields)


def generate_selectors(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positive_rows = [row for row in rows if row["row_positive"]]
    selectors: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...], tuple[str, ...]]] = set()
    for kind, fields in ROW_PUBLIC_FIELD_SETS:
        for row in positive_rows:
            values = selector_key(fields, row)
            key = (kind, fields, values)
            if key in seen:
                continue
            seen.add(key)
            selectors.append(
                {
                    "selector": selector_name(kind, fields, values),
                    "kind": kind,
                    "fields": list(fields),
                    "values": list(values),
                    "uses_transfer_identity": False,
                    "uses_rank_or_relation_count": False,
                    "uses_verifier_label_as_feature": False,
                }
            )
    return selectors


def row_matches(selector: dict[str, Any], row: dict[str, Any]) -> bool:
    for field, value in zip(selector["fields"], selector["values"]):
        if str(row.get(field)) != value:
            return False
    return True


def evaluate_selector(selector: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if row_matches(selector, row)]
    positives = [row for row in selected if row["row_positive"]]
    false_rows = [row for row in selected if not row["row_positive"]]
    available_positive_rows = sum(1 for row in rows if row["row_positive"])
    selected_positive_pairs = sorted({row["pair_id"] for row in positives})
    available_positive_pairs = sorted({row["pair_id"] for row in rows if row["row_positive"]})
    return {
        "selected_row_count": len(selected),
        "positive_row_count": len(positives),
        "false_row_count": len(false_rows),
        "anchor11_salt203_positive_row_count": sum(1 for row in positives if row["anchor11_salt203_positive"]),
        "positive_pair_count": len(selected_positive_pairs),
        "available_positive_pair_count": len(available_positive_pairs),
        "row_precision": len(positives) / len(selected) if selected else 0.0,
        "row_recall": len(positives) / max(1, available_positive_rows),
        "pair_recall": len(selected_positive_pairs) / max(1, len(available_positive_pairs)),
        "selected_pairs": sorted({row["pair_id"] for row in selected}),
        "positive_pairs": selected_positive_pairs,
        "false_row_examples": [row["row_id"] for row in false_rows[:24]],
        "positive_row_examples": [row["row_id"] for row in positives[:24]],
    }


def evaluate_custom_rows(selected: list[dict[str, Any]], all_rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected_ids = {row["row_id"] for row in selected}
    selector = {"fields": ["row_id"], "values": []}
    result = evaluate_selector(selector, [])
    positives = [row for row in selected if row["row_positive"]]
    false_rows = [row for row in selected if not row["row_positive"]]
    available_positive_rows = sum(1 for row in all_rows if row["row_positive"])
    available_positive_pairs = sorted({row["pair_id"] for row in all_rows if row["row_positive"]})
    selected_positive_pairs = sorted({row["pair_id"] for row in positives})
    result.update(
        {
            "selected_row_count": len(selected),
            "positive_row_count": len(positives),
            "false_row_count": len(false_rows),
            "anchor11_salt203_positive_row_count": sum(1 for row in positives if row["anchor11_salt203_positive"]),
            "positive_pair_count": len(selected_positive_pairs),
            "available_positive_pair_count": len(available_positive_pairs),
            "row_precision": len(positives) / len(selected) if selected else 0.0,
            "row_recall": len(positives) / max(1, available_positive_rows),
            "pair_recall": len(selected_positive_pairs) / max(1, len(available_positive_pairs)),
            "selected_pairs": sorted({row["pair_id"] for row in selected}),
            "positive_pairs": selected_positive_pairs,
            "selected_row_ids": sorted(selected_ids)[:80],
            "false_row_examples": [row["row_id"] for row in false_rows[:24]],
            "positive_row_examples": [row["row_id"] for row in positives[:24]],
        }
    )
    return result


def policy_score(policy: str, evaluation: dict[str, Any]) -> tuple[Any, ...]:
    precision = float(evaluation["row_precision"])
    row_recall = float(evaluation["row_recall"])
    pair_recall = float(evaluation["pair_recall"])
    positives = int(evaluation["positive_row_count"])
    false_rows = int(evaluation["false_row_count"])
    selected = int(evaluation["selected_row_count"])
    if policy == "recall_first":
        return (pair_recall, row_recall, positives, precision, -false_rows, -selected)
    if policy == "precision_first":
        return (precision, pair_recall, row_recall, positives, -false_rows, -selected)
    if policy == "spend_efficiency":
        return (
            positives / max(1, selected),
            positives / max(1, false_rows + 1),
            pair_recall,
            row_recall,
            -false_rows,
            -selected,
        )
    if policy == "low_false_row_first":
        return (-false_rows, precision, pair_recall, row_recall, positives, -selected)
    return (p683.f1(precision, row_recall), pair_recall, positives, precision, row_recall, -false_rows, -selected)


def choose_selector(policy: str, selectors: list[dict[str, Any]], train_rows: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated = []
    rejected_broad = 0
    for selector in selectors:
        training = evaluate_selector(selector, train_rows)
        if training["positive_row_count"] <= 0:
            continue
        if training["selected_row_count"] >= len(train_rows):
            rejected_broad += 1
            continue
        evaluated.append((policy_score(policy, training), selector, training))
    if not evaluated:
        return {"selector": None, "training": None, "rejected_training_broad_selectors": rejected_broad}
    evaluated.sort(key=lambda item: item[0], reverse=True)
    _, selector, training = evaluated[0]
    return {"selector": selector, "training": training, "rejected_training_broad_selectors": rejected_broad}


def loto_audit(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positive_pairs = sorted({row["pair_id"] for row in rows if row["row_positive"]})
    folds: list[dict[str, Any]] = []
    for holdout_pair in positive_pairs:
        train_rows = [row for row in rows if row["pair_id"] != holdout_pair]
        heldout_rows = [row for row in rows if row["pair_id"] == holdout_pair]
        selectors = generate_selectors(train_rows)
        policies = {}
        for policy in POLICIES:
            choice = choose_selector(policy, selectors, train_rows)
            selector = choice["selector"]
            if selector is None:
                policies[policy] = {
                    "selector": None,
                    "training": None,
                    "heldout": None,
                    "all_rows": None,
                    "rejected_training_broad_selectors": choice["rejected_training_broad_selectors"],
                }
                continue
            policies[policy] = {
                "selector": selector,
                "training": choice["training"],
                "heldout": evaluate_selector(selector, heldout_rows),
                "all_rows": evaluate_selector(selector, rows),
                "rejected_training_broad_selectors": choice["rejected_training_broad_selectors"],
            }
        folds.append(
            {
                "holdout_pair": holdout_pair,
                "holdout_row_count": len(heldout_rows),
                "holdout_positive_row_count": sum(1 for row in heldout_rows if row["row_positive"]),
                "candidate_selector_count": len(selectors),
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
        rejected_broad = 0
        selector_kinds: Counter[str] = Counter()
        hit_pairs: list[str] = []
        chosen_selectors: list[str] = []
        for fold in folds:
            heldout_available_positive_rows += int(fold["holdout_positive_row_count"])
            row = fold["policies"].get(policy) or {}
            selector = row.get("selector") or {}
            heldout = row.get("heldout") or {}
            all_rows = row.get("all_rows") or {}
            rejected_broad += int(row.get("rejected_training_broad_selectors") or 0)
            heldout_positive = int(heldout.get("positive_row_count") or 0)
            if heldout_positive:
                heldout_pair_hits += 1
                hit_pairs.append(str(fold["holdout_pair"]))
            heldout_positive_rows += heldout_positive
            heldout_selected_rows += int(heldout.get("selected_row_count") or 0)
            heldout_false_rows += int(heldout.get("false_row_count") or 0)
            aggregate_selected += int(all_rows.get("selected_row_count") or 0)
            aggregate_false += int(all_rows.get("false_row_count") or 0)
            aggregate_positive += int(all_rows.get("positive_row_count") or 0)
            if selector.get("kind"):
                selector_kinds[str(selector["kind"])] += 1
            if selector.get("selector"):
                chosen_selectors.append(str(selector["selector"]))
        summary[policy] = {
            "fold_count": len(folds),
            "heldout_positive_pair_hits": heldout_pair_hits,
            "heldout_hit_pairs": hit_pairs,
            "heldout_positive_row_count": heldout_positive_rows,
            "heldout_available_positive_row_count": heldout_available_positive_rows,
            "heldout_row_recall": heldout_positive_rows / max(1, heldout_available_positive_rows),
            "heldout_selected_row_count": heldout_selected_rows,
            "heldout_false_row_count": heldout_false_rows,
            "aggregate_all_rows_selected_row_count": aggregate_selected,
            "aggregate_all_rows_false_row_count": aggregate_false,
            "aggregate_all_rows_positive_row_count": aggregate_positive,
            "rejected_training_broad_selector_count": rejected_broad,
            "selector_kind_counts": dict(selector_kinds),
            "chosen_selectors": chosen_selectors,
        }
    return summary


def fixed_diagnostics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    positive_rows = [row for row in rows if row["row_positive"]]
    return {
        "broad_all_rows": {
            "selector": {
                "selector": "all_rows",
                "fields": [],
                "values": [],
                "uses_transfer_identity": False,
                "uses_rank_or_relation_count": False,
                "uses_verifier_label_as_feature": False,
            },
            "evaluation": evaluate_custom_rows(rows, rows),
        },
        "oracle_positive_rows": {
            "selector": {
                "selector": "oracle_positive_rows",
                "fields": ["row_positive"],
                "values": ["true"],
                "uses_transfer_identity": False,
                "uses_rank_or_relation_count": False,
                "uses_verifier_label_as_feature": True,
            },
            "evaluation": evaluate_custom_rows(positive_rows, rows),
        },
    }


def determine_claim(policy_summary: dict[str, dict[str, Any]]) -> str:
    best_pair_hits = max((row["heldout_positive_pair_hits"] for row in policy_summary.values()), default=0)
    best_row_recall = max((row["heldout_row_recall"] for row in policy_summary.values()), default=0.0)
    if best_pair_hits >= 2:
        return "P685_ROW_LEVEL_PUBLIC_PRE_RANK_MULTI_HELDOUT_POSITIVE"
    if best_pair_hits == 1:
        return "P685_ROW_LEVEL_PUBLIC_PRE_RANK_SINGLE_HELDOUT_POSITIVE"
    if best_row_recall > 0:
        return "P685_ROW_LEVEL_PUBLIC_PRE_RANK_WEAK_ROW_RECALL"
    return "NEGATIVE_RESULT_P685_ROW_LEVEL_PUBLIC_PRE_RANK_NO_HELDOUT_RECALL"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="append", default=None, help="Gate artifact to include; repeatable.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    gate_paths = [Path(path) for path in (args.gate or [str(path) for path in DEFAULT_GATES])]
    rows = p684.load_unique_rows(gate_paths)
    successor_rows = build_successor_rows(rows)
    folds = loto_audit(successor_rows)
    policy_summary = aggregate_folds(folds)
    diagnostics = fixed_diagnostics(successor_rows)
    claim_status = determine_claim(policy_summary)
    positive_pairs = sorted({row["pair_id"] for row in successor_rows if row["row_positive"]})
    payload = {
        "schema": "ecdlp.low_term_total2_p685_row_level_public_pre_rank_selector.v1",
        "created_at": p678.utc_now(),
        "method": "p685_row_level_public_pre_rank_selector",
        "claim_status": claim_status,
        "artifacts": {"gates": [str(path) for path in gate_paths]},
        "parameters": {
            "row_public_field_sets": [{"kind": kind, "fields": list(fields)} for kind, fields in ROW_PUBLIC_FIELD_SETS],
            "policies": list(POLICIES),
            "outcome": "successor right208/salt208 row is below-rho direct verified",
            "holdout_unit": "successor-positive transition pair",
            "dedupe_key": "target|transfer|selector|top_k",
            "training_broad_selector_rule": "reject if selector matches every training row",
        },
        "summary": {
            "claim_status": claim_status,
            "unique_input_row_count": len(rows),
            "successor_row_count": len(successor_rows),
            "positive_row_count": sum(1 for row in successor_rows if row["row_positive"]),
            "positive_pair_count": len(positive_pairs),
            "positive_pairs": positive_pairs,
            "row_level_policy_summary": policy_summary,
            "fixed_diagnostics": diagnostics,
        },
        "folds": folds,
        "honesty_boundary": [
            "Selectors use public row-level source/gate fields only.",
            "Rank, relation count, transfer identity, direct verification labels, and below-rho labels are excluded as selector fields.",
            "Training-broad selectors are rejected before policy scoring.",
            "Held-out recall is measured by positive transition pair to avoid testing on the same positive pair used for training.",
            "Row-level held-out recall is relation-event evidence, not a complete faster-than-rho ECDLP algorithm.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "claim_status": claim_status,
                "unique_input_row_count": len(rows),
                "successor_row_count": len(successor_rows),
                "positive_row_count": sum(1 for row in successor_rows if row["row_positive"]),
                "positive_pair_count": len(positive_pairs),
                "positive_pairs": positive_pairs,
                "row_level_policy_summary": policy_summary,
                "fixed_diagnostics": diagnostics,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
