#!/usr/bin/env python3
"""P684 public pre-rank proxy selector audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p682_right207_to_right208_transition_pair_audit as p682
import low_term_total2_p683_pair_local_source_policy_delta_selector as p683
import low_term_total2_p678_right208_salt208_public_selector_audit as p678


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p684_public_pre_rank_proxy_selector_probe.json"
DEFAULT_GATES = p682.DEFAULT_GATES
POLICIES = ("balanced", "recall_first", "precision_first", "spend_efficiency", "low_false_pair_first")
PUBLIC_PROXY_FIELD_SETS: list[tuple[str, tuple[str, ...]]] = [
    ("next_anchor_count_signature", ("next_anchor_count_signature",)),
    ("next_left_salt_count_signature", ("next_left_salt_count_signature",)),
    ("next_row_pair_count_signature", ("next_row_pair_count_signature",)),
    ("next_mode_count_signature", ("next_mode_count_signature",)),
    ("next_leaf_signature_count_signature", ("next_leaf_signature_count_signature",)),
    ("next_anchor_left_count_signature", ("next_anchor_left_count_signature",)),
    ("next_mode_anchor_count_signature", ("next_mode_anchor_count_signature",)),
    ("next_mode_left_count_signature", ("next_mode_left_count_signature",)),
    ("next_gate_check_ops_count_signature", ("next_gate_check_ops_count_signature",)),
    ("next_gate_product_ops_count_signature", ("next_gate_product_ops_count_signature",)),
    ("next_gate_product_saved_ops_count_signature", ("next_gate_product_saved_ops_count_signature",)),
    ("next_unique_fraction_count_signature", ("next_unique_fraction_count_signature",)),
    ("next_public_gate_bool_count_signature", ("next_public_gate_bool_count_signature",)),
    ("proxy_anchor_gate_signature", ("next_anchor_count_signature", "next_gate_product_ops_count_signature")),
    ("proxy_mode_gate_signature", ("next_mode_count_signature", "next_gate_product_ops_count_signature")),
    ("proxy_left_gate_signature", ("next_left_salt_count_signature", "next_gate_product_ops_count_signature")),
    ("proxy_mode_unique_signature", ("next_mode_count_signature", "next_unique_fraction_count_signature")),
    ("proxy_anchor_bool_signature", ("next_anchor_count_signature", "next_public_gate_bool_count_signature")),
    (
        "proxy_complexity_signature",
        (
            "next_gate_check_ops_count_signature",
            "next_gate_product_ops_count_signature",
            "next_gate_product_saved_ops_count_signature",
            "next_unique_fraction_count_signature",
        ),
    ),
]


def metric_bucket(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "none"


def bool_token(value: Any) -> str:
    return "true" if bool(value) else "false"


def count_signature(values: list[str]) -> str:
    counts = Counter(value for value in values if value and value != "None")
    if not counts:
        return "none"
    return ",".join(f"{key}:{counts[key]}" for key in sorted(counts))


def pair_count_signature(rows: list[dict[str, Any]], left_key: str, right_key: str) -> str:
    return count_signature([f"{row.get(left_key)}|{row.get(right_key)}" for row in rows])


def row_from_case(case: dict[str, Any], path: Path) -> dict[str, Any] | None:
    row = p682.row_from_case(case, path)
    if not row:
        return None
    gate_metrics = case.get("gate_metrics") or {}
    row.update(
        {
            "direct_selected_leaf_check_ops": str(gate_metrics.get("direct_selected_leaf_check_ops")),
            "direct_selected_leaf_product_ops": str(gate_metrics.get("direct_selected_leaf_product_ops")),
            "duplicate_selected_leaf_check_saved_ops": str(gate_metrics.get("duplicate_selected_leaf_check_saved_ops")),
            "shared_selected_leaf_product_saved_ops": str(gate_metrics.get("shared_selected_leaf_product_saved_ops")),
            "unique_signature_fraction_bucket": metric_bucket(gate_metrics.get("unique_signature_fraction")),
            "public_gate_all_rows_share_selected_signatures": bool_token(
                gate_metrics.get("public_gate_all_rows_share_selected_signatures")
            ),
            "public_gate_duplicate_density_ge_half_product_ge1": bool_token(
                gate_metrics.get("public_gate_duplicate_density_ge_half_product_ge1")
            ),
            "public_gate_duplicate_ge5_product_ge1": bool_token(
                gate_metrics.get("public_gate_duplicate_ge5_product_ge1")
            ),
        }
    )
    row["public_gate_bool_token"] = (
        f"share:{row['public_gate_all_rows_share_selected_signatures']}|"
        f"dup_half:{row['public_gate_duplicate_density_ge_half_product_ge1']}|"
        f"dup5:{row['public_gate_duplicate_ge5_product_ge1']}"
    )
    return row


def load_unique_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows_by_id: dict[str, dict[str, Any]] = {}
    for path in paths:
        payload = json.loads(path.read_text())
        for case in payload.get("cases", []):
            row = row_from_case(case, path)
            if not row:
                continue
            if row["row_id"] not in rows_by_id:
                row["artifact_paths"] = [path.name]
                rows_by_id[row["row_id"]] = row
            else:
                rows_by_id[row["row_id"]]["artifact_paths"].append(path.name)
    rows = list(rows_by_id.values())
    rows.sort(key=lambda row: (int(row["transfer_index"]), str(row["selector"])))
    return rows


def summarize_transfer_rows(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    by_transfer: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_transfer.setdefault(int(row["transfer_index"]), []).append(row)
    return dict(sorted(by_transfer.items()))


def public_proxy_features(successor_rows: list[dict[str, Any]]) -> dict[str, str]:
    return {
        "next_anchor_count_signature": count_signature([str(row.get("right_anchor")) for row in successor_rows]),
        "next_left_salt_count_signature": count_signature([f"salt{row.get('salt_left')}" for row in successor_rows]),
        "next_row_pair_count_signature": count_signature([str(row.get("row_pair")) for row in successor_rows]),
        "next_mode_count_signature": count_signature([str(row.get("selector_mode")) for row in successor_rows]),
        "next_leaf_signature_count_signature": count_signature([str(row.get("leaf_signature")) for row in successor_rows]),
        "next_anchor_left_count_signature": pair_count_signature(successor_rows, "right_anchor", "salt_left"),
        "next_mode_anchor_count_signature": pair_count_signature(successor_rows, "selector_mode", "right_anchor"),
        "next_mode_left_count_signature": pair_count_signature(successor_rows, "selector_mode", "salt_left"),
        "next_gate_check_ops_count_signature": count_signature(
            [str(row.get("direct_selected_leaf_check_ops")) for row in successor_rows]
        ),
        "next_gate_product_ops_count_signature": count_signature(
            [str(row.get("direct_selected_leaf_product_ops")) for row in successor_rows]
        ),
        "next_gate_product_saved_ops_count_signature": count_signature(
            [str(row.get("shared_selected_leaf_product_saved_ops")) for row in successor_rows]
        ),
        "next_unique_fraction_count_signature": count_signature(
            [str(row.get("unique_signature_fraction_bucket")) for row in successor_rows]
        ),
        "next_public_gate_bool_count_signature": count_signature(
            [str(row.get("public_gate_bool_token")) for row in successor_rows]
        ),
    }


def build_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_transfer = summarize_transfer_rows(rows)
    pairs: list[dict[str, Any]] = []
    for transfer, _current_rows in by_transfer.items():
        next_rows = by_transfer.get(transfer + 1)
        if not next_rows:
            continue
        successor_public = [row for row in next_rows if p682.right208_salt208(row)]
        successor_below = [row for row in successor_public if row["direct_below_rho_verified"]]
        successor_anchor11 = [row for row in successor_public if p682.right208_anchor11_salt203(row)]
        successor_anchor11_below = [row for row in successor_anchor11 if row["direct_below_rho_verified"]]
        successor_rank3 = [row for row in successor_public if row["rank3_direct_verified"]]
        pair = {
            "pair_id": f"{transfer}->{transfer + 1}",
            "t": transfer,
            "next_t": transfer + 1,
            **public_proxy_features(successor_public),
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


def generate_selectors(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positive_pairs = [pair for pair in pairs if pair["outcome_positive"]]
    selectors: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...], tuple[str, ...]]] = set()
    for kind, fields in PUBLIC_PROXY_FIELD_SETS:
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
                    "fields": list(fields),
                    "values": list(values),
                    "uses_transfer_identity": False,
                    "uses_rank_or_relation_count": False,
                    "uses_verifier_label_as_feature": False,
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
    false_pairs = [pair for pair in selected if not pair["outcome_positive"]]
    available_positive_pairs = sum(1 for pair in pairs if pair["outcome_positive"])
    available_below_rows = sum(int(pair["next_right208_below_count"]) for pair in pairs)
    selected_below_rows = sum(int(pair["next_right208_below_count"]) for pair in selected)
    return {
        "selected_pair_count": len(selected),
        "positive_pair_count": len(positives),
        "false_pair_count": len(false_pairs),
        "next_right208_public_case_count": sum(int(pair["next_right208_public_case_count"]) for pair in selected),
        "next_right208_below_count": selected_below_rows,
        "next_anchor11_salt203_below_count": sum(int(pair["next_anchor11_salt203_below_count"]) for pair in selected),
        "next_right208_rank3_count": sum(int(pair["next_right208_rank3_count"]) for pair in selected),
        "pair_precision": len(positives) / len(selected) if selected else 0.0,
        "pair_recall": len(positives) / max(1, available_positive_pairs),
        "below_row_recall": selected_below_rows / max(1, available_below_rows),
        "selected_pairs": [pair["pair_id"] for pair in selected],
        "positive_pairs": [pair["pair_id"] for pair in positives],
        "false_pairs": [pair["pair_id"] for pair in false_pairs[:80]],
        "below_row_examples": [row for pair in positives for row in pair["next_below_row_ids"][:4]][:24],
    }


def policy_score(policy: str, evaluation: dict[str, Any]) -> tuple[Any, ...]:
    precision = float(evaluation["pair_precision"])
    recall = float(evaluation["pair_recall"])
    below = int(evaluation["next_right208_below_count"])
    positives = int(evaluation["positive_pair_count"])
    false_pairs = int(evaluation["false_pair_count"])
    selected = int(evaluation["selected_pair_count"])
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
        return (-false_pairs, precision, positives, below, recall, -public_cases, -selected)
    return (p683.f1(precision, recall), below, positives, precision, recall, -false_pairs, -public_cases, -selected)


def choose_selector(policy: str, selectors: list[dict[str, Any]], train_pairs: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated = []
    rejected_broad = 0
    for selector in selectors:
        training = evaluate_selector(selector, train_pairs)
        if training["positive_pair_count"] <= 0:
            continue
        if training["selected_pair_count"] >= len(train_pairs):
            rejected_broad += 1
            continue
        evaluated.append((policy_score(policy, training), selector, training))
    if not evaluated:
        return {"selector": None, "training": None, "rejected_training_broad_selectors": rejected_broad}
    evaluated.sort(key=lambda item: item[0], reverse=True)
    _, selector, training = evaluated[0]
    return {"selector": selector, "training": training, "rejected_training_broad_selectors": rejected_broad}


def loto_audit(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positive_pairs = [pair for pair in pairs if pair["outcome_positive"]]
    folds: list[dict[str, Any]] = []
    for holdout in positive_pairs:
        train_pairs = [pair for pair in pairs if pair["pair_id"] != holdout["pair_id"]]
        selectors = generate_selectors(train_pairs)
        policies = {}
        for policy in POLICIES:
            choice = choose_selector(policy, selectors, train_pairs)
            selector = choice["selector"]
            if selector is None:
                policies[policy] = {
                    "selector": None,
                    "training": None,
                    "heldout": None,
                    "rejected_training_broad_selectors": choice["rejected_training_broad_selectors"],
                }
                continue
            policies[policy] = {
                "selector": selector,
                "training": choice["training"],
                "heldout": evaluate_selector(selector, [holdout]),
                "all_pairs": evaluate_selector(selector, pairs),
                "rejected_training_broad_selectors": choice["rejected_training_broad_selectors"],
            }
        folds.append(
            {
                "holdout_pair": holdout["pair_id"],
                "holdout_next_right208_below_count": holdout["next_right208_below_count"],
                "candidate_selector_count": len(selectors),
                "policies": policies,
            }
        )
    return folds


def aggregate_folds(folds: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for policy in POLICIES:
        heldout_hits = 0
        heldout_below = 0
        heldout_available_below = 0
        selector_kinds: Counter[str] = Counter()
        selected_pair_count = 0
        false_pair_count = 0
        rejected_broad = 0
        hit_pairs: list[str] = []
        chosen_selectors: list[str] = []
        for fold in folds:
            heldout_available_below += int(fold["holdout_next_right208_below_count"])
            row = fold["policies"].get(policy) or {}
            selector = row.get("selector") or {}
            heldout = row.get("heldout") or {}
            all_pairs = row.get("all_pairs") or {}
            rejected_broad += int(row.get("rejected_training_broad_selectors") or 0)
            below = int(heldout.get("next_right208_below_count") or 0)
            if below:
                heldout_hits += 1
                hit_pairs.append(str(fold["holdout_pair"]))
            heldout_below += below
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
            "heldout_available_next_right208_below_count": heldout_available_below,
            "heldout_below_row_recall": heldout_below / max(1, heldout_available_below),
            "aggregate_all_pairs_selected_pair_count": selected_pair_count,
            "aggregate_all_pairs_false_pair_count": false_pair_count,
            "rejected_training_broad_selector_count": rejected_broad,
            "selector_kind_counts": dict(selector_kinds),
            "chosen_selectors": chosen_selectors,
        }
    return summary


def fixed_diagnostics(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "broad_all_pairs": {
            "evaluation": p683.evaluate_custom_pairs(pairs, pairs),
            "selector": {
                "selector": "all_pairs",
                "fields": [],
                "values": [],
                "uses_transfer_identity": False,
                "uses_rank_or_relation_count": False,
                "uses_verifier_label_as_feature": False,
            },
        }
    }


def determine_claim(policy_summary: dict[str, dict[str, Any]]) -> str:
    best_hits = max((row["heldout_positive_pair_hits"] for row in policy_summary.values()), default=0)
    best_recall = max((row["heldout_below_row_recall"] for row in policy_summary.values()), default=0.0)
    if best_hits >= 2:
        return "P684_PUBLIC_PRE_RANK_PROXY_MULTI_HELDOUT_POSITIVE"
    if best_hits == 1:
        return "P684_PUBLIC_PRE_RANK_PROXY_SINGLE_HELDOUT_POSITIVE"
    if best_recall > 0:
        return "P684_PUBLIC_PRE_RANK_PROXY_WEAK_ROW_RECALL"
    return "NEGATIVE_RESULT_P684_PUBLIC_PRE_RANK_PROXY_NO_HELDOUT_RECALL"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="append", default=None, help="Gate artifact to include; repeatable.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    gate_paths = [Path(path) for path in (args.gate or [str(path) for path in DEFAULT_GATES])]
    rows = load_unique_rows(gate_paths)
    pairs = build_pairs(rows)
    folds = loto_audit(pairs)
    policy_summary = aggregate_folds(folds)
    diagnostics = fixed_diagnostics(pairs)
    claim_status = determine_claim(policy_summary)
    positive_pairs = [pair for pair in pairs if pair["outcome_positive"]]
    payload = {
        "schema": "ecdlp.low_term_total2_p684_public_pre_rank_proxy_selector.v1",
        "created_at": p678.utc_now(),
        "method": "p684_public_pre_rank_proxy_selector",
        "claim_status": claim_status,
        "artifacts": {"gates": [str(path) for path in gate_paths]},
        "parameters": {
            "public_proxy_field_sets": [{"kind": kind, "fields": list(fields)} for kind, fields in PUBLIC_PROXY_FIELD_SETS],
            "policies": list(POLICIES),
            "outcome": "successor transfer has at least one below-rho direct verified right208/salt208 row",
            "dedupe_key": "target|transfer|selector|top_k",
            "training_broad_selector_rule": "reject if selector matches every training pair",
        },
        "summary": {
            "claim_status": claim_status,
            "unique_row_count": len(rows),
            "pair_count": len(pairs),
            "positive_pair_count": len(positive_pairs),
            "positive_pairs": [pair["pair_id"] for pair in positive_pairs],
            "total_successor_right208_below_rows": sum(pair["next_right208_below_count"] for pair in pairs),
            "public_proxy_policy_summary": policy_summary,
            "fixed_diagnostics": diagnostics,
        },
        "pairs": pairs,
        "folds": folds,
        "honesty_boundary": [
            "Selectors use public source/gate histogram features only.",
            "Rank, relation count, transfer identity, direct verification labels, and below-rho labels are excluded as selector fields.",
            "Training-broad selectors are rejected before policy scoring.",
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
                "public_proxy_policy_summary": policy_summary,
                "fixed_diagnostics": diagnostics,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
