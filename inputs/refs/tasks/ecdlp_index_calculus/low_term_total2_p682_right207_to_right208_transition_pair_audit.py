#!/usr/bin/env python3
"""P682 transition-pair audit for right207 -> right208 surface shifts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p639_right208_salt208_recurrence_scout as p639
import low_term_total2_p678_right208_salt208_public_selector_audit as p678
import low_term_total2_p680_anchor11_salt203_right208_recurrence_scout as p680


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p682_right207_to_right208_transition_pair_audit_probe.json"
DEFAULT_GATES = [
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p658_order9887_phase3_right207_salt207_postquiet_22330_22342_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p659_order9887_salt204_right206_anchor11_right208_22343_22355_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p661_order9887_right207_salt207_p659_branch_22356_22368_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p660_order9887_exact_p658_salt204_right206_anchor11_right208_22417_22423_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p663_order9887_p661_drift_surfaces_22369_22381_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p662_order9887_exact_p659_right207_salt207_22431_22436_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p664_order9887_exact_p661_drift_surfaces_22442_22446_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p665_order9887_phase0_salt204_drift_22382_22394_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p666_order9887_right207_salt207_offbranch_22395_22407_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p667_order9887_right207_salt207_drift_family_22408_22420_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p668_order9887_right207_salt207_exact_repeats_22469_22491_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p669_order9887_phase5_mod7_6_second_repeat_22548_22560_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p670_order9887_offsurface_phase2_phase11_corridor_22561_22573_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p671_order9887_exact_offsurface_repeats_22634_22643_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p673_order9887_adjacent_row_pair_shift_22635_22647_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p672_order9887_exact_row_pair_shift_22718_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p674_order9887_exact_rank_surface_22722_22723_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p675_order9887_exact_below_rho_surface_22807_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p676_order9887_adjacent_below_rho_surface_22724_22736_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p677_order9887_exact_right208_salt208_22808_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p680_order9887_anchor11_salt203_right208_22809_22821_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p681_order9887_anchor11_salt203_right208_backward_22711_22723_density_gate_probe.json",
]
PUBLIC_FIELD_SETS: list[tuple[str, tuple[str, ...]]] = [
    ("all_pairs", ()),
    ("t_phase", ("t_phase",)),
    ("t_mod7", ("t_mod7",)),
    ("t_phase_mod7", ("t_phase_mod7",)),
    ("next_phase", ("next_phase",)),
    ("next_mod7", ("next_mod7",)),
    ("next_phase_mod7", ("next_phase_mod7",)),
    ("t_next_phase_mod7", ("t_phase_mod7", "next_phase_mod7")),
    ("precursor_public_case_count", ("precursor_public_case_count",)),
    ("precursor_public_row_pair_set", ("precursor_public_row_pair_set",)),
    ("precursor_public_mode_set", ("precursor_public_mode_set",)),
    ("precursor_public_gate_unique_set", ("precursor_public_gate_unique_set",)),
    ("precursor_public_gate_density_set", ("precursor_public_gate_density_set",)),
    ("precursor_public_shared_product_ops_set", ("precursor_public_shared_product_ops_set",)),
    ("t_phase_mod7_precursor_mode_set", ("t_phase_mod7", "precursor_public_mode_set")),
    ("t_phase_mod7_precursor_gate_unique_set", ("t_phase_mod7", "precursor_public_gate_unique_set")),
]
POLICIES = ("balanced", "recall_first", "precision_first", "low_false_pair_first")


def selector_mode(selector: str) -> str:
    return selector.split("__", 1)[0]


def density_bucket(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "none"


def row_id(feature: dict[str, Any]) -> str:
    return f"{feature.get('target')}|{feature.get('transfer_index')}|{feature.get('selector')}|{feature.get('top_k')}"


def row_from_case(case: dict[str, Any], path: Path) -> dict[str, Any] | None:
    feature = p639.feature(case)
    if not feature.get("parse_ok"):
        return None
    gate_metrics = case.get("gate_metrics") or {}
    return {
        **feature,
        "artifact": p678.artifact_id(path),
        "artifact_path": str(path),
        "row_id": row_id(feature),
        "selector_mode": selector_mode(str(case.get("selector") or "")),
        "unique_selected_leaf_signature_count": str(gate_metrics.get("unique_selected_leaf_signature_count")),
        "duplicate_signature_density_bucket": density_bucket(gate_metrics.get("duplicate_signature_density")),
        "shared_selected_leaf_product_ops": str(gate_metrics.get("shared_selected_leaf_product_ops")),
        "rank3_direct_verified": bool(feature.get("direct_verified") and int(feature.get("rank") or 0) >= 3),
    }


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


def right207_anchor8_salt207(row: dict[str, Any]) -> bool:
    return p680.anchor(8, p680.right207_salt207)(row)


def right208_salt208(row: dict[str, Any]) -> bool:
    return p680.right208_salt208(row)


def right208_anchor11_salt203(row: dict[str, Any]) -> bool:
    return p680.anchor(11, p680.row_pair(203, 208))(row)


def mode_set(rows: list[dict[str, Any]]) -> str:
    return ",".join(sorted({str(row.get("selector_mode")) for row in rows})) or "none"


def value_set(rows: list[dict[str, Any]], key: str) -> str:
    return ",".join(sorted({str(row.get(key)) for row in rows})) or "none"


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
        precursor_public = [row for row in current_rows if right207_anchor8_salt207(row)]
        precursor_below = [row for row in precursor_public if row["direct_below_rho_verified"]]
        next_right208 = [row for row in next_rows if right208_salt208(row)]
        next_right208_below = [row for row in next_right208 if row["direct_below_rho_verified"]]
        next_anchor11 = [row for row in next_rows if right208_anchor11_salt203(row)]
        next_anchor11_below = [row for row in next_anchor11 if row["direct_below_rho_verified"]]
        next_rank3 = [row for row in next_right208 if row["rank3_direct_verified"]]
        pair = {
            "pair_id": f"{transfer}->{transfer + 1}",
            "t": transfer,
            "next_t": transfer + 1,
            "t_phase": str(transfer % 12),
            "t_mod7": str(transfer % 7),
            "t_phase_mod7": f"{transfer % 12}/{transfer % 7}",
            "next_phase": str((transfer + 1) % 12),
            "next_mod7": str((transfer + 1) % 7),
            "next_phase_mod7": f"{(transfer + 1) % 12}/{(transfer + 1) % 7}",
            "precursor_public_case_count": str(len(precursor_public)),
            "precursor_public_row_pair_set": value_set(precursor_public, "row_pair"),
            "precursor_public_mode_set": mode_set(precursor_public),
            "precursor_public_gate_unique_set": value_set(precursor_public, "unique_selected_leaf_signature_count"),
            "precursor_public_gate_density_set": value_set(precursor_public, "duplicate_signature_density_bucket"),
            "precursor_public_shared_product_ops_set": value_set(precursor_public, "shared_selected_leaf_product_ops"),
            "precursor_anchor8_salt207_below_count": len(precursor_below),
            "precursor_anchor8_salt207_direct_count": sum(1 for row in precursor_public if row["direct_verified"]),
            "next_right208_direct_count": sum(1 for row in next_right208 if row["direct_verified"]),
            "next_right208_below_count": len(next_right208_below),
            "next_right208_rank3_count": len(next_rank3),
            "next_anchor11_salt203_below_count": len(next_anchor11_below),
            "outcome_positive": bool(next_right208_below),
            "outcome_anchor11_positive": bool(next_anchor11_below),
            "next_below_row_ids": [row["row_id"] for row in next_right208_below],
            "next_anchor11_below_row_ids": [row["row_id"] for row in next_anchor11_below],
            "precursor_below_row_ids": [row["row_id"] for row in precursor_below],
        }
        pairs.append(pair)
    pairs.sort(key=lambda pair: int(pair["t"]))
    return pairs


def selector_name(kind: str, fields: tuple[str, ...], values: tuple[str, ...]) -> str:
    if not fields:
        return kind
    return f"{kind}::" + ",".join(f"{field}={value}" for field, value in zip(fields, values))


def selector_key(fields: tuple[str, ...], pair: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(pair.get(field)) for field in fields)


def generate_public_selectors(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positive_pairs = [pair for pair in pairs if pair["outcome_positive"]]
    selectors: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...], tuple[str, ...]]] = set()
    for kind, fields in PUBLIC_FIELD_SETS:
        source_pairs = positive_pairs if fields else pairs[:1]
        for pair in source_pairs:
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
        "next_right208_below_count": selected_below_rows,
        "next_anchor11_salt203_below_count": selected_anchor11_rows,
        "next_right208_rank3_count": selected_rank3_rows,
        "pair_precision": len(positives) / len(selected) if selected else 0.0,
        "pair_recall": len(positives) / max(1, available_positive_pairs),
        "below_row_recall": selected_below_rows / max(1, available_below_rows),
        "selected_pairs": [pair["pair_id"] for pair in selected],
        "positive_pairs": [pair["pair_id"] for pair in positives],
        "false_pairs": [pair["pair_id"] for pair in false_pairs[:40]],
        "below_row_examples": [row for pair in positives for row in pair["next_below_row_ids"][:4]][:24],
    }


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
    if policy == "recall_first":
        return (recall, below, positives, rank3, precision, -false_pairs, -selected)
    if policy == "precision_first":
        return (precision, positives, below, recall, rank3, -false_pairs, -selected)
    if policy == "low_false_pair_first":
        return (-false_pairs, precision, positives, below, recall, rank3, -selected)
    return (f1(precision, recall), below, positives, precision, recall, rank3, -false_pairs, -selected)


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
        selectors = generate_public_selectors(train_pairs)
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
        folds.append(
            {
                "holdout_pair": holdout["pair_id"],
                "holdout_next_right208_below_count": holdout["next_right208_below_count"],
                "holdout_next_anchor11_salt203_below_count": holdout["next_anchor11_salt203_below_count"],
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
        heldout_anchor11 = 0
        heldout_available_below = 0
        selector_kinds: Counter[str] = Counter()
        hit_pairs: list[str] = []
        for fold in folds:
            heldout_available_below += int(fold["holdout_next_right208_below_count"])
            row = fold["policies"].get(policy) or {}
            selector = row.get("selector") or {}
            heldout = row.get("heldout") or {}
            below = int(heldout.get("next_right208_below_count") or 0)
            anchor11 = int(heldout.get("next_anchor11_salt203_below_count") or 0)
            if below:
                heldout_hits += 1
                hit_pairs.append(str(fold["holdout_pair"]))
            heldout_below += below
            heldout_anchor11 += anchor11
            if selector.get("kind"):
                selector_kinds[str(selector["kind"])] += 1
        summary[policy] = {
            "fold_count": len(folds),
            "heldout_positive_pair_hits": heldout_hits,
            "heldout_hit_pairs": hit_pairs,
            "heldout_next_right208_below_count": heldout_below,
            "heldout_next_anchor11_salt203_below_count": heldout_anchor11,
            "heldout_available_next_right208_below_count": heldout_available_below,
            "heldout_below_row_recall": heldout_below / max(1, heldout_available_below),
            "selector_kind_counts": dict(selector_kinds),
        }
    return summary


def fixed_transition_diagnostics(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    diagnostics = {
        "broad_all_pairs": {
            "selector": {
                "selector": "all_pairs",
                "fields": [],
                "values": [],
                "uses_transfer_identity": False,
                "uses_verifier_label_as_feature": False,
            }
        },
        "label_p674_anchor8_below_present": {
            "selector": {
                "selector": "label_p674_anchor8_below_present",
                "fields": ["precursor_anchor8_salt207_below_count"],
                "values": [">0"],
                "uses_transfer_identity": False,
                "uses_verifier_label_as_feature": True,
            }
        },
        "public_t_phase7_mod7_1": {
            "selector": {
                "selector": "public_t_phase7_mod7_1",
                "fields": ["t_phase_mod7"],
                "values": ["7/1"],
                "uses_transfer_identity": False,
                "uses_verifier_label_as_feature": False,
            }
        },
    }
    for name, item in diagnostics.items():
        selector = item["selector"]
        if name == "label_p674_anchor8_below_present":
            selected_pairs = [pair for pair in pairs if int(pair["precursor_anchor8_salt207_below_count"]) > 0]
            item["evaluation"] = evaluate_custom_pairs(selected_pairs, pairs)
        else:
            item["evaluation"] = evaluate_selector(selector, pairs)
    return diagnostics


def evaluate_custom_pairs(selected: list[dict[str, Any]], all_pairs: list[dict[str, Any]]) -> dict[str, Any]:
    selected_ids = {pair["pair_id"] for pair in selected}
    selector = {
        "fields": ["pair_id"],
        "values": [],
    }
    selected_eval = evaluate_selector(selector, [])
    positives = [pair for pair in selected if pair["outcome_positive"]]
    available_positive_pairs = sum(1 for pair in all_pairs if pair["outcome_positive"])
    available_below_rows = sum(int(pair["next_right208_below_count"]) for pair in all_pairs)
    below_count = sum(int(pair["next_right208_below_count"]) for pair in selected)
    anchor11_count = sum(int(pair["next_anchor11_salt203_below_count"]) for pair in selected)
    rank3_count = sum(int(pair["next_right208_rank3_count"]) for pair in selected)
    selected_eval.update(
        {
            "selected_pair_count": len(selected),
            "positive_pair_count": len(positives),
            "false_pair_count": len(selected) - len(positives),
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
    return selected_eval


def determine_claim(policy_summary: dict[str, dict[str, Any]], diagnostics: dict[str, Any]) -> str:
    specific_rows = [
        row
        for row in policy_summary.values()
        if set(row.get("selector_kind_counts") or {}) != {"all_pairs"}
    ]
    best_specific_hits = max((row["heldout_positive_pair_hits"] for row in specific_rows), default=0)
    best_specific_recall = max((row["heldout_below_row_recall"] for row in specific_rows), default=0.0)
    best_broad_hits = max(row["heldout_positive_pair_hits"] for row in policy_summary.values())
    label_eval = diagnostics["label_p674_anchor8_below_present"]["evaluation"]
    label_hits = int(label_eval["positive_pair_count"])
    label_false = int(label_eval["false_pair_count"])
    if best_specific_hits >= 2:
        return "P682_PUBLIC_TRANSITION_SELECTOR_MULTI_HELDOUT_POSITIVE"
    if best_specific_hits == 1:
        return "P682_PUBLIC_TRANSITION_SELECTOR_SINGLE_HELDOUT_POSITIVE"
    if best_broad_hits and label_hits and label_false:
        return "NEGATIVE_RESULT_P682_PUBLIC_TRANSITION_SPECIFIC_SELECTORS_NO_HELDOUT_BROAD_ONLY_LABEL_MIXED"
    if label_hits and label_false:
        return "NEGATIVE_RESULT_P682_PUBLIC_TRANSITION_NO_HELDOUT_LABEL_TRANSITION_MIXED"
    if label_hits:
        return "P682_LABEL_TRANSITION_DIAGNOSTIC_POSITIVE_PUBLIC_SELECTOR_NEGATIVE"
    if best_specific_recall > 0:
        return "P682_PUBLIC_TRANSITION_SELECTOR_WEAK_RECALL"
    return "NEGATIVE_RESULT_P682_PUBLIC_TRANSITION_SELECTOR_NO_HELDOUT_RECALL"


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
    diagnostics = fixed_transition_diagnostics(pairs)
    claim_status = determine_claim(policy_summary, diagnostics)
    positive_pairs = [pair for pair in pairs if pair["outcome_positive"]]
    payload = {
        "schema": "ecdlp.low_term_total2_p682_right207_to_right208_transition_pair_audit.v1",
        "created_at": p678.utc_now(),
        "method": "p682_right207_to_right208_transition_pair_audit",
        "claim_status": claim_status,
        "artifacts": {"gates": [str(path) for path in gate_paths]},
        "parameters": {
            "public_field_sets": [{"kind": kind, "fields": list(fields)} for kind, fields in PUBLIC_FIELD_SETS],
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
            "policy_summary": policy_summary,
            "fixed_transition_diagnostics": diagnostics,
        },
        "pairs": pairs,
        "folds": folds,
        "honesty_boundary": [
            "Public LOTO selectors use only phase/mod7 and public precursor-row geometry/gate metrics, not verifier labels.",
            "The P674-anchor8-below diagnostic explicitly uses verifier labels and is not a deployable public selector.",
            "Pair-level held-out recall is relation-event evidence, not a complete faster-than-rho ECDLP algorithm.",
            "Repeated artifacts are deduplicated by target, transfer, selector, and top_k.",
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
                "policy_summary": policy_summary,
                "fixed_transition_diagnostics": diagnostics,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
