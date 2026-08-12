#!/usr/bin/env python3
"""P679 support-stable false-spend reducer for right208/salt208 selectors."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p678_right208_salt208_public_selector_audit as p678


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p679_right208_salt208_support_stable_selector_audit_probe.json"
MIN_SUPPORT_TRANSFERS = 2
NON_PHASE_FIELD_SETS: list[tuple[str, tuple[str, ...]]] = [
    ("anchor", ("right_anchor",)),
    ("row_pair", ("row_pair",)),
    ("mode", ("selector_mode",)),
    ("leaf_signature", ("leaf_signature",)),
    ("gate_unique_signature_count", ("unique_selected_leaf_signature_count",)),
    ("gate_duplicate_density", ("duplicate_signature_density_bucket",)),
    ("gate_shared_product_ops", ("shared_selected_leaf_product_ops",)),
    ("anchor_row_pair", ("right_anchor", "row_pair")),
    ("anchor_mode", ("right_anchor", "selector_mode")),
    ("row_pair_mode", ("row_pair", "selector_mode")),
    ("anchor_gate_unique", ("right_anchor", "unique_selected_leaf_signature_count")),
    ("row_pair_gate_unique", ("row_pair", "unique_selected_leaf_signature_count")),
    ("mode_gate_unique", ("selector_mode", "unique_selected_leaf_signature_count")),
    ("anchor_gate_density", ("right_anchor", "duplicate_signature_density_bucket")),
    ("row_pair_gate_density", ("row_pair", "duplicate_signature_density_bucket")),
    ("mode_gate_density", ("selector_mode", "duplicate_signature_density_bucket")),
    ("anchor_row_pair_mode", ("right_anchor", "row_pair", "selector_mode")),
    (
        "anchor_row_pair_gate_unique",
        ("right_anchor", "row_pair", "unique_selected_leaf_signature_count"),
    ),
    (
        "anchor_mode_gate_unique",
        ("right_anchor", "selector_mode", "unique_selected_leaf_signature_count"),
    ),
    (
        "row_pair_mode_gate_unique",
        ("row_pair", "selector_mode", "unique_selected_leaf_signature_count"),
    ),
    (
        "anchor_row_pair_mode_gate_unique",
        ("right_anchor", "row_pair", "selector_mode", "unique_selected_leaf_signature_count"),
    ),
]
POLICIES = ("support_first", "spend_efficiency", "quiet_first", "precision_then_support")


def generate_selectors(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positive_rows = [row for row in rows if row["direct_below_rho_verified"]]
    selectors: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...], tuple[str, ...]]] = set()
    for kind, fields in NON_PHASE_FIELD_SETS:
        for row in positive_rows:
            values = p678.selector_key(fields, row)
            key = (kind, fields, values)
            if key in seen:
                continue
            seen.add(key)
            selectors.append(
                {
                    "selector": p678.selector_name(kind, fields, values),
                    "kind": kind,
                    "fields": list(fields),
                    "values": list(values),
                    "uses_transfer_identity": False,
                    "uses_phase_or_mod7": False,
                    "uses_verifier_label_as_feature": False,
                }
            )
    return selectors


def selected_rows(selector: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if p678.row_matches(selector, row)]


def enrich_eval(selector: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    evaluation = p678.evaluate_selector(selector, rows)
    below_rows = [row for row in selected_rows(selector, rows) if row["direct_below_rho_verified"]]
    direct_rows = [row for row in selected_rows(selector, rows) if row["direct_verified"]]
    evaluation.update(
        {
            "below_rho_transfer_support": len({int(row["transfer_index"]) for row in below_rows}),
            "direct_transfer_support": len({int(row["transfer_index"]) for row in direct_rows}),
            "below_row_pair_counts": dict(Counter(str(row["row_pair"]) for row in below_rows)),
            "below_anchor_counts": dict(Counter(str(row["right_anchor"]) for row in below_rows)),
            "below_mode_counts": dict(Counter(str(row["selector_mode"]) for row in below_rows)),
        }
    )
    return evaluation


def support_candidate(
    selector: dict[str, Any],
    train_rows: list[dict[str, Any]],
    quiet_rows: list[dict[str, Any]],
) -> dict[str, Any] | None:
    train_eval = enrich_eval(selector, train_rows)
    if train_eval["direct_below_rho_verified_count"] <= 0:
        return None
    if train_eval["below_rho_transfer_support"] < MIN_SUPPORT_TRANSFERS:
        return None
    quiet_eval = enrich_eval(selector, quiet_rows)
    return {"selector": selector, "training": train_eval, "quiet_controls": quiet_eval}


def score_candidate(policy: str, candidate: dict[str, Any]) -> tuple[Any, ...]:
    train = candidate["training"]
    quiet = candidate["quiet_controls"]
    below = int(train["direct_below_rho_verified_count"])
    selected = int(train["selected_count"])
    support = int(train["below_rho_transfer_support"])
    precision = float(train["below_rho_precision"])
    recall = float(train["below_rho_recall"])
    quiet_selected = int(quiet["selected_count"])
    quiet_direct = int(quiet["direct_verified_count"])
    efficiency = below / max(1, quiet_selected + selected)
    common_tail = (support, below, precision, recall, -quiet_selected, -quiet_direct, -selected)
    if policy == "spend_efficiency":
        return (efficiency, *common_tail)
    if policy == "quiet_first":
        return (-quiet_selected, -quiet_direct, support, below, precision, recall, -selected)
    if policy == "precision_then_support":
        return (precision, support, below, recall, -quiet_selected, -quiet_direct, -selected)
    return (support, below, precision, recall, -quiet_selected, -quiet_direct, -selected)


def choose(policy: str, candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not candidates:
        return None
    return sorted(candidates, key=lambda candidate: score_candidate(policy, candidate), reverse=True)[0]


def audit(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_transfer = p678.transfer_summary(rows)
    positive_transfers = {
        int(transfer)
        for transfer, summary in by_transfer.items()
        if summary["direct_below_rho_verified_count"] > 0
    }
    quiet_rows = p678.quiet_control_rows(rows, positive_transfers)
    folds: list[dict[str, Any]] = []
    for holdout_transfer in sorted(positive_transfers):
        train_rows = [row for row in rows if int(row["transfer_index"]) != holdout_transfer]
        heldout_rows = [row for row in rows if int(row["transfer_index"]) == holdout_transfer]
        candidates = [
            candidate
            for selector in generate_selectors(train_rows)
            if (candidate := support_candidate(selector, train_rows, quiet_rows)) is not None
        ]
        policy_rows = {}
        for policy in POLICIES:
            candidate = choose(policy, candidates)
            if candidate is None:
                policy_rows[policy] = None
                continue
            policy_rows[policy] = {
                **candidate,
                "heldout": enrich_eval(candidate["selector"], heldout_rows),
            }
        folds.append(
            {
                "holdout_transfer": holdout_transfer,
                "candidate_selector_count": len(candidates),
                "heldout_available_below_rho_count": by_transfer[str(holdout_transfer)][
                    "direct_below_rho_verified_count"
                ],
                "heldout_available_direct_count": by_transfer[str(holdout_transfer)]["direct_verified_count"],
                "heldout_available_rank3_count": by_transfer[str(holdout_transfer)]["rank3_direct_verified_count"],
                "policies": policy_rows,
            }
        )
    metadata = {
        "positive_transfers": sorted(positive_transfers),
        "quiet_transfer_count": len(
            [
                transfer
                for transfer, summary in by_transfer.items()
                if int(transfer) not in positive_transfers
                and summary["direct_verified_count"] == 0
                and summary["direct_below_rho_verified_count"] == 0
            ]
        ),
        "quiet_row_count": len(quiet_rows),
        "transfer_summary": by_transfer,
    }
    return folds, metadata


def aggregate(folds: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for policy in POLICIES:
        heldout_selected = 0
        heldout_below = 0
        heldout_direct = 0
        heldout_rank3 = 0
        available_below = 0
        quiet_selected = 0
        quiet_direct = 0
        hit_transfers: list[int] = []
        kinds: Counter[str] = Counter()
        for fold in folds:
            row = fold["policies"].get(policy)
            available_below += int(fold["heldout_available_below_rho_count"])
            if row is None:
                continue
            selector = row["selector"]
            heldout = row["heldout"]
            quiet = row["quiet_controls"]
            heldout_selected += int(heldout["selected_count"])
            heldout_below += int(heldout["direct_below_rho_verified_count"])
            heldout_direct += int(heldout["direct_verified_count"])
            heldout_rank3 += int(heldout["rank3_direct_verified_count"])
            quiet_selected += int(quiet["selected_count"])
            quiet_direct += int(quiet["direct_verified_count"])
            kinds[str(selector["kind"])] += 1
            if int(heldout["direct_below_rho_verified_count"]) > 0:
                hit_transfers.append(int(fold["holdout_transfer"]))
        out[policy] = {
            "fold_count": len(folds),
            "heldout_available_below_rho_count": available_below,
            "heldout_selected_count": heldout_selected,
            "heldout_direct_verified_count": heldout_direct,
            "heldout_direct_below_rho_verified_count": heldout_below,
            "heldout_rank3_direct_verified_count": heldout_rank3,
            "heldout_below_rho_case_recall": heldout_below / max(1, available_below),
            "heldout_below_rho_transfer_hits": len(hit_transfers),
            "heldout_below_rho_hit_transfers": hit_transfers,
            "quiet_control_selected_count": quiet_selected,
            "quiet_control_direct_verified_count": quiet_direct,
            "quiet_spend_reduction_vs_p678_broad": 1.0 - quiet_selected / 65100.0,
            "selector_kind_counts": dict(kinds),
        }
    return out


def determine_claim(summary: dict[str, dict[str, Any]]) -> str:
    positive = [
        row
        for row in summary.values()
        if row["heldout_direct_below_rho_verified_count"] > 0 and row["quiet_control_selected_count"] < 65100
    ]
    if any(row["heldout_below_rho_transfer_hits"] >= 2 for row in positive):
        return "P679_SUPPORT_STABLE_SUBSELECTOR_MULTI_HELDOUT_RECALL_REDUCES_FALSE_SPEND"
    if any(row["heldout_below_rho_transfer_hits"] == 1 for row in positive):
        return "P679_SUPPORT_STABLE_SUBSELECTOR_SINGLE_HELDOUT_RECALL_REDUCES_FALSE_SPEND"
    if any(row["quiet_control_selected_count"] < 65100 for row in summary.values()):
        return "NEGATIVE_RESULT_P679_SUPPORT_STABLE_REDUCES_SPEND_BUT_LOSES_HELDOUT_RECALL"
    return "NEGATIVE_RESULT_P679_SUPPORT_STABLE_NO_FALSE_SPEND_REDUCTION"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="append", default=None, help="Gate artifact to include; repeatable.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    gate_paths = [Path(path) for path in (args.gate or [str(path) for path in p678.DEFAULT_GATES])]
    rows = p678.load_rows(gate_paths)
    folds, metadata = audit(rows)
    policy_summary = aggregate(folds)
    claim_status = determine_claim(policy_summary)
    payload = {
        "schema": "ecdlp.low_term_total2_p679_right208_salt208_support_stable_selector_audit.v1",
        "created_at": p678.utc_now(),
        "method": "p679_right208_salt208_support_stable_false_spend_reducer",
        "claim_status": claim_status,
        "artifacts": {"gates": [str(path) for path in gate_paths]},
        "parameters": {
            "non_phase_field_sets": [{"kind": kind, "fields": list(fields)} for kind, fields in NON_PHASE_FIELD_SETS],
            "policies": list(POLICIES),
            "min_support_transfers": MIN_SUPPORT_TRANSFERS,
            "baseline_p678_broad_quiet_control_selected_count": 65100,
        },
        "summary": {
            "claim_status": claim_status,
            "row_count": len(rows),
            "positive_transfers": metadata["positive_transfers"],
            "quiet_transfer_count": metadata["quiet_transfer_count"],
            "quiet_row_count": metadata["quiet_row_count"],
            "policy_summary": policy_summary,
        },
        "folds": folds,
        "transfer_summary": metadata["transfer_summary"],
        "honesty_boundary": [
            "P679 excludes exact transfer identity, phase/mod7, and the broad right208/salt208 selector from candidate subselectors.",
            "Selectors use public non-phase fields only; verifier labels choose selectors only on training folds and score held-out folds.",
            "Quiet-spend reduction is measured against P678's broad-family aggregate quiet-control selection count of 65100.",
            "Held-out recall is relation-event evidence, not a complete faster-than-rho ECDLP algorithm.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, "policy_summary": policy_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
