#!/usr/bin/env python3
"""P687 source-charge and replay audit for the P686 row frontier."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p682_right207_to_right208_transition_pair_audit as p682
import low_term_total2_p684_public_pre_rank_proxy_selector as p684
import low_term_total2_p685_row_level_public_pre_rank_selector as p685
import low_term_total2_p686_row_level_selector_precision_frontier as p686
import low_term_total2_p678_right208_salt208_public_selector_audit as p678


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p687_frontier_source_charge_replay_audit_probe.json"
DEFAULT_GATES = p682.DEFAULT_GATES
DEFAULT_P686_ARTIFACT = STATE_DIR / "low_term_total2_p686_row_level_selector_precision_frontier_probe.json"
DEFAULT_POLICY = "greedy_budgeted_union"


def number(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def cost_row_from_case(case: dict[str, Any], path: Path) -> dict[str, Any] | None:
    row = p684.row_from_case(case, path)
    if not row:
        return None
    gate_metrics = case.get("gate_metrics") or {}
    rho = number(case.get("rho"))
    replay_ops = number(case.get("direct_verifier_replay_ops"))
    replay_ops_over_rho = number(case.get("direct_verifier_replay_ops_over_rho"))
    source_ops_over_rho = case.get("source_ops_over_rho")
    row.update(
        {
            "rho": rho,
            "direct_verifier_replay_ops": replay_ops,
            "direct_verifier_replay_ops_over_rho": replay_ops_over_rho,
            "source_ops_over_rho": number(source_ops_over_rho) if source_ops_over_rho is not None else None,
            "source_public_key_verified": bool(case.get("source_public_key_verified")),
            "source_below_rho": bool(case.get("source_below_rho")),
            "direct_selected_hit_root_ops": number(gate_metrics.get("direct_selected_hit_root_ops")),
            "direct_selected_leaf_check_ops_num": number(gate_metrics.get("direct_selected_leaf_check_ops")),
            "direct_selected_leaf_product_ops_num": number(gate_metrics.get("direct_selected_leaf_product_ops")),
            "shared_selected_leaf_product_ops_num": number(gate_metrics.get("shared_selected_leaf_product_ops")),
            "shared_selected_leaf_product_saved_ops_num": number(gate_metrics.get("shared_selected_leaf_product_saved_ops")),
            "shared_signature_root_charge": number(gate_metrics.get("shared_signature_root_charge")),
            "shared_signature_root_saved_ops": number(gate_metrics.get("shared_signature_root_saved_ops")),
        }
    )
    return row


def load_unique_cost_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows_by_id: dict[str, dict[str, Any]] = {}
    for path in paths:
        payload = json.loads(path.read_text())
        for case in payload.get("cases", []):
            row = cost_row_from_case(case, path)
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


def load_policy_selectors(path: Path, policy: str) -> dict[str, list[dict[str, Any]]]:
    payload = json.loads(path.read_text())
    selectors_by_fold: dict[str, list[dict[str, Any]]] = {}
    for fold in payload.get("folds", []):
        fold_policy = (fold.get("policies") or {}).get(policy) or {}
        selectors_by_fold[str(fold["holdout_pair"])] = list(fold_policy.get("selectors") or [])
    return selectors_by_fold


def selected_by_selectors(rows: list[dict[str, Any]], selectors: list[dict[str, Any]]) -> set[int]:
    selected: set[int] = set()
    for idx, row in enumerate(rows):
        if any(p685.row_matches(selector, row) for selector in selectors):
            selected.add(idx)
    return selected


def cost_summary(selected_indices: set[int], universe_indices: set[int], rows: list[dict[str, Any]]) -> dict[str, Any]:
    indices = selected_indices & universe_indices
    positives = {idx for idx in indices if rows[idx]["row_positive"]}
    false_rows = indices - positives
    available_positive_rows = {idx for idx in universe_indices if rows[idx]["row_positive"]}
    replay_ops = sum(rows[idx]["direct_verifier_replay_ops"] for idx in indices)
    replay_over_rho = sum(rows[idx]["direct_verifier_replay_ops_over_rho"] for idx in indices)
    false_replay_ops = sum(rows[idx]["direct_verifier_replay_ops"] for idx in false_rows)
    false_replay_over_rho = sum(rows[idx]["direct_verifier_replay_ops_over_rho"] for idx in false_rows)
    positive_replay_ops = sum(rows[idx]["direct_verifier_replay_ops"] for idx in positives)
    positive_replay_over_rho = sum(rows[idx]["direct_verifier_replay_ops_over_rho"] for idx in positives)
    source_known = [rows[idx]["source_ops_over_rho"] for idx in indices if rows[idx]["source_ops_over_rho"] is not None]
    source_positive_known = [
        rows[idx]["source_ops_over_rho"] for idx in positives if rows[idx]["source_ops_over_rho"] is not None
    ]
    selected_positive_pairs = sorted({rows[idx]["pair_id"] for idx in positives})
    available_positive_pairs = sorted({rows[idx]["pair_id"] for idx in available_positive_rows})
    positive_rho_budget = float(len(positives))
    pair_rho_budget = float(len(selected_positive_pairs))
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
        "selected_pairs": sorted({rows[idx]["pair_id"] for idx in indices}),
        "positive_pairs": selected_positive_pairs,
        "direct_replay_ops": replay_ops,
        "direct_replay_ops_over_rho": replay_over_rho,
        "false_direct_replay_ops": false_replay_ops,
        "false_direct_replay_ops_over_rho": false_replay_over_rho,
        "positive_direct_replay_ops": positive_replay_ops,
        "positive_direct_replay_ops_over_rho": positive_replay_over_rho,
        "direct_replay_over_positive_row_rho_budget": replay_over_rho / max(1.0, positive_rho_budget),
        "direct_replay_over_positive_pair_rho_budget": replay_over_rho / max(1.0, pair_rho_budget),
        "below_rho_selected_positive_row_count": sum(
            1 for idx in positives if rows[idx]["direct_verifier_replay_ops_over_rho"] < 1.0
        ),
        "source_ops_over_rho_known_count": len(source_known),
        "source_ops_over_rho_sum_known": sum(source_known),
        "source_positive_ops_over_rho_known_count": len(source_positive_known),
        "source_positive_ops_over_rho_sum_known": sum(source_positive_known),
        "gate_leaf_check_ops": sum(rows[idx]["direct_selected_leaf_check_ops_num"] for idx in indices),
        "gate_leaf_product_ops": sum(rows[idx]["direct_selected_leaf_product_ops_num"] for idx in indices),
        "gate_shared_product_ops": sum(rows[idx]["shared_selected_leaf_product_ops_num"] for idx in indices),
        "gate_shared_product_saved_ops": sum(rows[idx]["shared_selected_leaf_product_saved_ops_num"] for idx in indices),
        "gate_hit_root_ops": sum(rows[idx]["direct_selected_hit_root_ops"] for idx in indices),
        "positive_row_examples": [rows[idx]["row_id"] for idx in sorted(positives)[:24]],
        "false_row_examples": [rows[idx]["row_id"] for idx in sorted(false_rows)[:24]],
    }


def fold_audit(rows: list[dict[str, Any]], selectors_by_fold: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    all_indices = set(range(len(rows)))
    folds: list[dict[str, Any]] = []
    for holdout_pair, selectors in sorted(selectors_by_fold.items()):
        selected = selected_by_selectors(rows, selectors)
        heldout = {idx for idx, row in enumerate(rows) if row["pair_id"] == holdout_pair}
        train = all_indices - heldout
        folds.append(
            {
                "holdout_pair": holdout_pair,
                "selector_count": len(selectors),
                "selectors": selectors,
                "selector_kind_counts": dict(Counter(str(selector.get("kind")) for selector in selectors)),
                "training": cost_summary(selected, train, rows),
                "heldout": cost_summary(selected, heldout, rows),
                "all_rows": cost_summary(selected, all_indices, rows),
            }
        )
    return folds


def aggregate_folds(folds: list[dict[str, Any]]) -> dict[str, Any]:
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
    aggregate: dict[str, Any] = {f"heldout_{key}": 0.0 for key in heldout_keys}
    hit_pairs: list[str] = []
    selector_kinds: Counter[str] = Counter()
    for fold in folds:
        selector_kinds.update(fold["selector_kind_counts"])
        heldout = fold["heldout"]
        if heldout["positive_row_count"]:
            hit_pairs.append(fold["holdout_pair"])
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
    aggregate["selector_kind_counts"] = dict(selector_kinds)
    aggregate["all_rows"] = combine_scope(folds, "all_rows")
    aggregate["training"] = combine_scope(folds, "training")
    return aggregate


def combine_scope(folds: list[dict[str, Any]], scope: str) -> dict[str, Any]:
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
        row = fold[scope]
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


def broad_cost(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return cost_summary(set(range(len(rows))), set(range(len(rows))), rows)


def determine_claim(summary: dict[str, Any]) -> str:
    hits = int(summary["heldout_positive_pair_hits"])
    replay_over_rows = float(summary["heldout_replay_over_positive_row_rho_budget"])
    replay_over_pairs = float(summary["heldout_replay_over_positive_pair_rho_budget"])
    if hits >= 5 and replay_over_rows < 1.0:
        return "P687_FRONTIER_REPLAY_CHARGE_BELOW_ROW_RHO_BUDGET"
    if hits >= 5 and replay_over_pairs < 1.0:
        return "P687_FRONTIER_REPLAY_CHARGE_BELOW_PAIR_RHO_BUDGET"
    if hits >= 4 and replay_over_rows < 2.0:
        return "P687_FRONTIER_REPLAY_CHARGE_NEAR_ROW_RHO_BUDGET"
    if hits >= 4:
        return "P687_FRONTIER_SELECTOR_POSITIVE_REPLAY_CHARGE_ABOVE_RHO"
    return "NEGATIVE_RESULT_P687_FRONTIER_REPLAY_CHARGE_NO_MULTI_PAIR_SUPPORT"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="append", default=None, help="Gate artifact to include; repeatable.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p686-artifact", default=str(DEFAULT_P686_ARTIFACT))
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    args = parser.parse_args()

    gate_paths = [Path(path) for path in (args.gate or [str(path) for path in DEFAULT_GATES])]
    input_rows = load_unique_cost_rows(gate_paths)
    successor_rows = p685.build_successor_rows(input_rows)
    selectors_by_fold = load_policy_selectors(Path(args.p686_artifact), args.policy)
    folds = fold_audit(successor_rows, selectors_by_fold)
    summary = aggregate_folds(folds)
    broad = broad_cost(successor_rows)
    claim_status = determine_claim(summary)
    payload = {
        "schema": "ecdlp.low_term_total2_p687_frontier_source_charge_replay_audit.v1",
        "created_at": p678.utc_now(),
        "method": "p687_frontier_source_charge_replay_audit",
        "claim_status": claim_status,
        "artifacts": {
            "gates": [str(path) for path in gate_paths],
            "p686_frontier": str(args.p686_artifact),
        },
        "parameters": {
            "policy": args.policy,
            "cost_fields": [
                "direct_verifier_replay_ops",
                "direct_verifier_replay_ops_over_rho",
                "source_ops_over_rho",
                "gate_metrics.direct_selected_leaf_check_ops",
                "gate_metrics.direct_selected_leaf_product_ops",
                "gate_metrics.shared_selected_leaf_product_ops",
            ],
            "holdout_unit": "successor-positive transition pair",
            "dedupe_key": "target|transfer|selector|top_k",
        },
        "summary": {
            "claim_status": claim_status,
            "unique_input_row_count": len(input_rows),
            "successor_row_count": len(successor_rows),
            "positive_row_count": sum(1 for row in successor_rows if row["row_positive"]),
            "frontier_summary": summary,
            "broad_all_rows_cost": broad,
        },
        "folds": folds,
        "honesty_boundary": [
            "This audit charges selected rows from the P686 public selector frontier.",
            "Selector choice is inherited from P686 and did not use held-out labels as selector fields.",
            "Direct replay cost is not a full source-generation, sparse-linear-algebra, or target-descent cost.",
            "A favorable replay charge remains relation-event evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "claim_status": claim_status,
                "successor_row_count": len(successor_rows),
                "positive_row_count": sum(1 for row in successor_rows if row["row_positive"]),
                "frontier_summary": summary,
                "broad_all_rows_cost": {
                    key: broad[key]
                    for key in (
                        "selected_row_count",
                        "positive_row_count",
                        "false_row_count",
                        "direct_replay_ops_over_rho",
                        "direct_replay_over_positive_row_rho_budget",
                    )
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
