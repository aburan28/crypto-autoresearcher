#!/usr/bin/env python3
"""P678 cross-surface public selector audit for right208/salt208 rows."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p639_right208_salt208_recurrence_scout as p639


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p678_right208_salt208_public_selector_audit_probe.json"
DEFAULT_GATES = [
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p658_order9887_phase3_right207_salt207_postquiet_22330_22342_density_gate_probe.json",
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p661_order9887_right207_salt207_p659_branch_22356_22368_density_gate_probe.json",
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p663_order9887_p661_drift_surfaces_22369_22381_density_gate_probe.json",
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p668_order9887_right207_salt207_exact_repeats_22469_22491_density_gate_probe.json",
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p669_order9887_phase5_mod7_6_second_repeat_22548_22560_density_gate_probe.json",
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p670_order9887_offsurface_phase2_phase11_corridor_22561_22573_density_gate_probe.json",
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p676_order9887_adjacent_below_rho_surface_22724_22736_density_gate_probe.json",
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p677_order9887_exact_right208_salt208_22808_density_gate_probe.json",
]

PID_RE = re.compile(r"_p(?P<pid>\d+)_")
PUBLIC_FIELD_SETS: list[tuple[str, tuple[str, ...]]] = [
    ("right208_salt208_broad", ()),
    ("phase", ("transfer_mod12",)),
    ("mod7", ("transfer_mod7",)),
    ("phase_mod7", ("phase_mod7",)),
    ("anchor", ("right_anchor",)),
    ("row_pair", ("row_pair",)),
    ("mode", ("selector_mode",)),
    ("leaf_signature", ("leaf_signature",)),
    ("phase_anchor", ("transfer_mod12", "right_anchor")),
    ("phase_row_pair", ("transfer_mod12", "row_pair")),
    ("phase_mode", ("transfer_mod12", "selector_mode")),
    ("mod7_anchor", ("transfer_mod7", "right_anchor")),
    ("mod7_row_pair", ("transfer_mod7", "row_pair")),
    ("mod7_mode", ("transfer_mod7", "selector_mode")),
    ("anchor_row_pair", ("right_anchor", "row_pair")),
    ("anchor_mode", ("right_anchor", "selector_mode")),
    ("row_pair_mode", ("row_pair", "selector_mode")),
    ("phase_mod7_anchor", ("phase_mod7", "right_anchor")),
    ("phase_mod7_row_pair", ("phase_mod7", "row_pair")),
    ("phase_mod7_mode", ("phase_mod7", "selector_mode")),
    ("phase_anchor_row_pair", ("transfer_mod12", "right_anchor", "row_pair")),
    ("phase_anchor_mode", ("transfer_mod12", "right_anchor", "selector_mode")),
    ("phase_row_pair_mode", ("transfer_mod12", "row_pair", "selector_mode")),
    ("mod7_anchor_row_pair", ("transfer_mod7", "right_anchor", "row_pair")),
    ("mod7_anchor_mode", ("transfer_mod7", "right_anchor", "selector_mode")),
    ("mod7_row_pair_mode", ("transfer_mod7", "row_pair", "selector_mode")),
    ("anchor_row_pair_mode", ("right_anchor", "row_pair", "selector_mode")),
    ("phase_mod7_anchor_row_pair", ("phase_mod7", "right_anchor", "row_pair")),
    ("phase_mod7_anchor_mode", ("phase_mod7", "right_anchor", "selector_mode")),
    ("phase_mod7_row_pair_mode", ("phase_mod7", "row_pair", "selector_mode")),
    ("phase_mod7_anchor_row_pair_mode", ("phase_mod7", "right_anchor", "row_pair", "selector_mode")),
    ("gate_unique_signature_count", ("unique_selected_leaf_signature_count",)),
    ("gate_duplicate_density", ("duplicate_signature_density_bucket",)),
    ("gate_shared_product_ops", ("shared_selected_leaf_product_ops",)),
    (
        "phase_mod7_anchor_row_pair_gate_unique",
        ("phase_mod7", "right_anchor", "row_pair", "unique_selected_leaf_signature_count"),
    ),
    (
        "phase_mod7_anchor_row_pair_gate_density",
        ("phase_mod7", "right_anchor", "row_pair", "duplicate_signature_density_bucket"),
    ),
]
POLICIES = ("balanced", "recall_first", "precision_first", "rank_first", "low_ops_first")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def artifact_id(path: Path) -> str:
    match = PID_RE.search(path.name)
    return f"P{match.group('pid')}" if match else path.stem


def mode_from_selector(selector: str) -> str:
    return selector.split("__", 1)[0]


def density_bucket(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "none"


def row_from_case(case: dict[str, Any], path: Path) -> dict[str, Any] | None:
    feature = p639.feature(case)
    if not p639.right208_salt208_family(feature):
        return None
    selector = str(case.get("selector") or "")
    gate_metrics = case.get("gate_metrics") or {}
    rank = int(feature.get("rank") or 0)
    ops_over_rho = feature.get("direct_ops_over_rho")
    row = {
        **feature,
        "artifact": artifact_id(path),
        "artifact_path": str(path),
        "row_id": f"{artifact_id(path)}|{p639.case_entry(feature)}",
        "selector_mode": mode_from_selector(selector),
        "phase_mod7": f"{feature.get('transfer_mod12')}/{feature.get('transfer_mod7')}",
        "unique_selected_leaf_signature_count": str(gate_metrics.get("unique_selected_leaf_signature_count")),
        "duplicate_signature_density_bucket": density_bucket(gate_metrics.get("duplicate_signature_density")),
        "shared_selected_leaf_product_ops": str(gate_metrics.get("shared_selected_leaf_product_ops")),
        "public_product_gate_selected": bool(case.get("public_product_gate_selected")),
        "rank3_direct_verified": bool(feature.get("direct_verified") and rank >= 3),
        "ops_over_rho_bucket": density_bucket(ops_over_rho),
    }
    return row


def load_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text())
        for case in payload.get("cases", []):
            row = row_from_case(case, path)
            if row:
                rows.append(row)
    rows.sort(key=lambda r: (int(r["transfer_index"]), r["artifact"], r["selector"]))
    return rows


def transfer_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["transfer_index"]), []).append(row)
    out: dict[str, dict[str, Any]] = {}
    for transfer, group in grouped.items():
        verified = [r for r in group if r["direct_verified"]]
        below = [r for r in group if r["direct_below_rho_verified"]]
        rank3 = [r for r in group if r["rank3_direct_verified"]]
        out[transfer] = {
            "case_count": len(group),
            "direct_verified_count": len(verified),
            "direct_below_rho_verified_count": len(below),
            "rank3_direct_verified_count": len(rank3),
            "artifact_counts": dict(Counter(str(r["artifact"]) for r in group)),
            "below_anchor_counts": dict(Counter(str(r["right_anchor"]) for r in below)),
            "below_row_pair_counts": dict(Counter(str(r["row_pair"]) for r in below)),
            "below_mode_counts": dict(Counter(str(r["selector_mode"]) for r in below)),
            "rank3_anchor_counts": dict(Counter(str(r["right_anchor"]) for r in rank3)),
            "rank3_row_pair_counts": dict(Counter(str(r["row_pair"]) for r in rank3)),
        }
    return dict(sorted(out.items(), key=lambda kv: int(kv[0])))


def selector_key(fields: tuple[str, ...], row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(row.get(field)) for field in fields)


def selector_name(kind: str, fields: tuple[str, ...], values: tuple[str, ...]) -> str:
    if not fields:
        return kind
    return f"{kind}::" + ",".join(f"{field}={value}" for field, value in zip(fields, values))


def generate_selectors(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positive_rows = [row for row in rows if row["direct_below_rho_verified"]]
    seen: set[tuple[str, tuple[str, ...], tuple[str, ...]]] = set()
    selectors: list[dict[str, Any]] = []
    for kind, fields in PUBLIC_FIELD_SETS:
        source_rows = positive_rows if fields else rows[:1]
        for row in source_rows:
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
    verified = [row for row in selected if row["direct_verified"]]
    below = [row for row in selected if row["direct_below_rho_verified"]]
    rank3 = [row for row in selected if row["rank3_direct_verified"]]
    available_below = sum(1 for row in rows if row["direct_below_rho_verified"])
    available_verified = sum(1 for row in rows if row["direct_verified"])
    selected_count = len(selected)
    false_count = selected_count - len(verified)
    below_ops = [
        float(row["direct_ops_over_rho"])
        for row in below
        if row.get("direct_ops_over_rho") is not None
    ]
    return {
        "selected_count": selected_count,
        "direct_verified_count": len(verified),
        "direct_below_rho_verified_count": len(below),
        "rank3_direct_verified_count": len(rank3),
        "false_selected_count": false_count,
        "direct_precision": len(verified) / selected_count if selected_count else 0.0,
        "below_rho_precision": len(below) / selected_count if selected_count else 0.0,
        "below_rho_recall": len(below) / max(1, available_below),
        "direct_recall": len(verified) / max(1, available_verified),
        "min_below_ops_over_rho": min(below_ops) if below_ops else None,
        "mean_below_ops_over_rho": sum(below_ops) / len(below_ops) if below_ops else None,
        "transfer_counts": dict(Counter(str(row["transfer_index"]) for row in selected)),
        "below_transfer_counts": dict(Counter(str(row["transfer_index"]) for row in below)),
        "rank3_transfer_counts": dict(Counter(str(row["transfer_index"]) for row in rank3)),
        "selected_examples": [row["row_id"] for row in selected[:24]],
        "below_examples": [row["row_id"] for row in below[:24]],
        "rank3_examples": [row["row_id"] for row in rank3[:24]],
    }


def f1(precision: float, recall: float) -> float:
    return (2.0 * precision * recall / (precision + recall)) if precision + recall else 0.0


def policy_score(policy: str, evaluation: dict[str, Any]) -> tuple[Any, ...]:
    precision = float(evaluation["below_rho_precision"])
    recall = float(evaluation["below_rho_recall"])
    selected = int(evaluation["selected_count"])
    below = int(evaluation["direct_below_rho_verified_count"])
    verified = int(evaluation["direct_verified_count"])
    rank3 = int(evaluation["rank3_direct_verified_count"])
    false_count = int(evaluation["false_selected_count"])
    min_ops = evaluation["min_below_ops_over_rho"]
    ops_score = -float(min_ops) if min_ops is not None else -9999.0
    common_tail = (below, verified, rank3, -false_count, -selected)
    if policy == "recall_first":
        return (recall, *common_tail, precision)
    if policy == "precision_first":
        return (precision, below, recall, verified, rank3, -false_count, -selected)
    if policy == "rank_first":
        return (rank3, below, precision, recall, verified, -false_count, -selected)
    if policy == "low_ops_first":
        return (ops_score, precision, recall, *common_tail)
    return (f1(precision, recall), below, precision, recall, verified, rank3, -false_count, -selected)


def choose_policy_selector(
    policy: str,
    selectors: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    evaluated = []
    for selector in selectors:
        train_eval = evaluate_selector(selector, train_rows)
        if train_eval["direct_below_rho_verified_count"] <= 0:
            continue
        evaluated.append((policy_score(policy, train_eval), selector, train_eval))
    if not evaluated:
        return {"selector": None, "training": None}
    evaluated.sort(key=lambda item: item[0], reverse=True)
    _, selector, train_eval = evaluated[0]
    return {"selector": selector, "training": train_eval}


def quiet_control_rows(rows: list[dict[str, Any]], positive_transfers: set[int]) -> list[dict[str, Any]]:
    by_transfer = transfer_summary(rows)
    quiet_transfers = {
        int(transfer)
        for transfer, summary in by_transfer.items()
        if int(transfer) not in positive_transfers
        and summary["direct_verified_count"] == 0
        and summary["direct_below_rho_verified_count"] == 0
    }
    return [row for row in rows if int(row["transfer_index"]) in quiet_transfers]


def fold_audit(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    by_transfer = transfer_summary(rows)
    positive_transfers = {
        int(transfer)
        for transfer, summary in by_transfer.items()
        if summary["direct_below_rho_verified_count"] > 0
    }
    quiet_rows = quiet_control_rows(rows, positive_transfers)
    folds: list[dict[str, Any]] = []
    for holdout_transfer in sorted(positive_transfers):
        train_rows = [row for row in rows if int(row["transfer_index"]) != holdout_transfer]
        heldout_rows = [row for row in rows if int(row["transfer_index"]) == holdout_transfer]
        selectors = generate_selectors(train_rows)
        policy_rows: dict[str, Any] = {}
        for policy in POLICIES:
            choice = choose_policy_selector(policy, selectors, train_rows)
            selector = choice.get("selector")
            if not selector:
                policy_rows[policy] = {"selector": None, "training": None, "heldout": None, "quiet_controls": None}
                continue
            policy_rows[policy] = {
                "selector": selector,
                "training": choice["training"],
                "heldout": evaluate_selector(selector, heldout_rows),
                "quiet_controls": evaluate_selector(selector, quiet_rows),
            }
        folds.append(
            {
                "holdout_transfer": holdout_transfer,
                "heldout_available_below_rho_count": by_transfer[str(holdout_transfer)][
                    "direct_below_rho_verified_count"
                ],
                "heldout_available_direct_count": by_transfer[str(holdout_transfer)]["direct_verified_count"],
                "heldout_available_rank3_count": by_transfer[str(holdout_transfer)]["rank3_direct_verified_count"],
                "candidate_selector_count": len(selectors),
                "policies": policy_rows,
            }
        )
    return folds, by_transfer


def aggregate_policy(folds: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for policy in POLICIES:
        heldout_selected = 0
        heldout_direct = 0
        heldout_below = 0
        heldout_rank3 = 0
        heldout_available_below = 0
        quiet_selected = 0
        quiet_direct = 0
        quiet_below = 0
        hit_transfers: list[int] = []
        selected_kinds: Counter[str] = Counter()
        for fold in folds:
            policy_row = fold["policies"].get(policy) or {}
            selector = policy_row.get("selector") or {}
            heldout = policy_row.get("heldout") or {}
            quiet = policy_row.get("quiet_controls") or {}
            heldout_available_below += int(fold["heldout_available_below_rho_count"])
            heldout_selected += int(heldout.get("selected_count") or 0)
            heldout_direct += int(heldout.get("direct_verified_count") or 0)
            heldout_below += int(heldout.get("direct_below_rho_verified_count") or 0)
            heldout_rank3 += int(heldout.get("rank3_direct_verified_count") or 0)
            quiet_selected += int(quiet.get("selected_count") or 0)
            quiet_direct += int(quiet.get("direct_verified_count") or 0)
            quiet_below += int(quiet.get("direct_below_rho_verified_count") or 0)
            if int(heldout.get("direct_below_rho_verified_count") or 0) > 0:
                hit_transfers.append(int(fold["holdout_transfer"]))
            if selector.get("kind"):
                selected_kinds[str(selector["kind"])] += 1
        summary[policy] = {
            "fold_count": len(folds),
            "heldout_selected_count": heldout_selected,
            "heldout_direct_verified_count": heldout_direct,
            "heldout_direct_below_rho_verified_count": heldout_below,
            "heldout_rank3_direct_verified_count": heldout_rank3,
            "heldout_available_below_rho_count": heldout_available_below,
            "heldout_below_rho_case_recall": heldout_below / max(1, heldout_available_below),
            "heldout_below_rho_transfer_hits": len(hit_transfers),
            "heldout_below_rho_hit_transfers": hit_transfers,
            "quiet_control_selected_count": quiet_selected,
            "quiet_control_direct_verified_count": quiet_direct,
            "quiet_control_below_rho_count": quiet_below,
            "selected_selector_kind_counts": dict(selected_kinds),
        }
    return summary


def determine_claim(policy_summary: dict[str, dict[str, Any]]) -> str:
    best_hits = max(row["heldout_below_rho_transfer_hits"] for row in policy_summary.values())
    best_recall = max(row["heldout_below_rho_case_recall"] for row in policy_summary.values())
    zero_quiet_hit = any(
        row["heldout_direct_below_rho_verified_count"] > 0 and row["quiet_control_selected_count"] == 0
        for row in policy_summary.values()
    )
    if zero_quiet_hit:
        return "P678_PUBLIC_SELECTOR_HELDOUT_BELOW_RHO_ZERO_QUIET_SELECTION"
    if best_hits >= 2:
        return "P678_PUBLIC_SELECTOR_MULTI_HELDOUT_BELOW_RHO_WITH_FALSE_SELECTION"
    if best_hits == 1:
        return "P678_PUBLIC_SELECTOR_SINGLE_HELDOUT_BELOW_RHO_WITH_FALSE_SELECTION"
    if best_recall > 0:
        return "P678_PUBLIC_SELECTOR_HELDOUT_BELOW_RHO_WEAK_RECALL"
    return "NEGATIVE_RESULT_P678_PUBLIC_SELECTOR_NO_HELDOUT_BELOW_RHO"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="append", default=None, help="Gate artifact to include; repeatable.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    gate_paths = [Path(path) for path in (args.gate or [str(path) for path in DEFAULT_GATES])]
    rows = load_rows(gate_paths)
    folds, by_transfer = fold_audit(rows)
    policy_summary = aggregate_policy(folds)
    claim_status = determine_claim(policy_summary)
    positive_transfers = [
        int(transfer)
        for transfer, summary in by_transfer.items()
        if summary["direct_below_rho_verified_count"] > 0
    ]
    quiet_transfers = [
        int(transfer)
        for transfer, summary in by_transfer.items()
        if summary["direct_verified_count"] == 0 and summary["direct_below_rho_verified_count"] == 0
    ]
    payload = {
        "schema": "ecdlp.low_term_total2_p678_right208_salt208_public_selector_audit.v1",
        "created_at": utc_now(),
        "method": "p678_cross_surface_right208_salt208_public_selector_audit",
        "claim_status": claim_status,
        "artifacts": {"gates": [str(path) for path in gate_paths]},
        "parameters": {
            "public_field_sets": [{"kind": kind, "fields": list(fields)} for kind, fields in PUBLIC_FIELD_SETS],
            "policies": list(POLICIES),
            "positive_transfer_definition": "transfer has at least one direct below-rho verified right208/salt208 row",
            "selector_feature_boundary": "selectors use only pre-registered public fields; verifier labels choose selectors only on training folds and score held-out folds",
        },
        "summary": {
            "claim_status": claim_status,
            "row_count": len(rows),
            "gate_count": len(gate_paths),
            "transfer_count": len(by_transfer),
            "positive_transfer_count": len(positive_transfers),
            "positive_transfers": positive_transfers,
            "quiet_transfer_count": len(quiet_transfers),
            "quiet_transfers": quiet_transfers[:80],
            "policy_summary": policy_summary,
        },
        "transfer_summary": by_transfer,
        "folds": folds,
        "honesty_boundary": [
            "Selector predicates use only public fields parsed from row geometry and public gate metrics.",
            "Verifier labels are used to choose a selector on training folds and to score held-out folds; this is a model-selection audit, not a deployed selector theorem.",
            "Held-out recall is measured on transfer groups, not on fresh curves or arbitrary targets.",
            "A below-rho direct replay is a relation-event metric, not a complete faster-than-rho ECDLP algorithm.",
            "Promotion still requires source-generation charge, sparse linear algebra, target descent, and individual-log accounting against Pollard rho.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "claim_status": claim_status,
                "row_count": len(rows),
                "positive_transfer_count": len(positive_transfers),
                "policy_summary": policy_summary,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
