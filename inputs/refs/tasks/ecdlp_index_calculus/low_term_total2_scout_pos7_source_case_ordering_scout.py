#!/usr/bin/env python3
"""Replay scout-7 preform collection under public source-case orderings.

The broad scout-7 double ``[11,15]`` preform collector still finds fresh
rank-gain stops, but some held-out windows pay earlier no-hit source cases
before reaching the useful case.  This scout tests whether public metadata from
the source artifacts can reorder source cases inside each source window before
the preform scan.

The default policies use only source-case metadata already present before the
scout-7 point-match replay: transfer offset, row salt gaps, row-leaf shapes, and
deterministic public hashes.  Replay-derived diagnostics such as rank and
public-key verification are deliberately not features.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from low_term_total2_scout_pos7_preform_source_charged_collector import (
    artifact_window,
    case_key,
    int_value,
    load_json,
    preform_accepts,
    rank_labels_by_source_case,
    ratio,
    scan_preform_case,
    source_cases,
    write_json,
)


SALT_RE = re.compile(r":salt(\d+)$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def salt_values(row_keys: Any) -> list[int]:
    salts: list[int] = []
    for row_key in row_keys or []:
        match = SALT_RE.search(str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return salts


def row_leaf_shapes(row: dict[str, Any]) -> list[tuple[int, ...]]:
    shapes: list[tuple[int, ...]] = []
    for item in row.get("row_leaf_keys") or []:
        if isinstance(item, dict):
            shapes.append(tuple(int_value(index) for index in item.get("leaf_indices") or []))
    return shapes


def stable_u64(parts: list[Any]) -> int:
    raw = json.dumps(parts, sort_keys=True, separators=(",", ":")).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")


def public_profile(row: dict[str, Any], window_start: int) -> dict[str, Any]:
    salts = salt_values(row.get("row_keys"))
    sorted_salts = sorted(salts)
    shapes = row_leaf_shapes(row)
    leaf_union = sorted({index for shape in shapes for index in shape})
    shared_leaf_count = 0
    leaf_counts: dict[int, int] = {}
    for shape in shapes:
        for index in set(shape):
            leaf_counts[index] = leaf_counts.get(index, 0) + 1
    shared_leaf_count = sum(1 for count in leaf_counts.values() if count >= 2)
    first_shape = shapes[0] if shapes else ()
    second_shape = shapes[1] if len(shapes) > 1 else ()
    salt_gap = max(sorted_salts) - min(sorted_salts) if len(sorted_salts) >= 2 else 0
    transfer = int_value(row.get("transfer_index"))
    return {
        "first_leaf_has_90": 90 in first_shape,
        "first_leaf_size": len(first_shape),
        "first_leaf_shape": ",".join(str(index) for index in first_shape) if first_shape else "none",
        "leaf_shape_signature": ";".join(",".join(str(index) for index in shape) for shape in shapes) or "none",
        "leaf_union_count": len(leaf_union),
        "public_hash": stable_u64(
            [
                row.get("target"),
                transfer,
                row.get("selector"),
                row.get("top_k"),
                row.get("row_keys") or [],
                row.get("row_leaf_keys") or [],
            ]
        ),
        "salt_gap": salt_gap,
        "salt_max": max(sorted_salts) if sorted_salts else 0,
        "salt_min": min(sorted_salts) if sorted_salts else 0,
        "salt_sum": sum(sorted_salts),
        "second_leaf_has_90": 90 in second_shape,
        "second_leaf_size": len(second_shape),
        "selected_leaf_count": int_value(row.get("selected_leaf_count")),
        "selected_row_count": int_value(row.get("selected_row_count")),
        "shared_leaf_count": shared_leaf_count,
        "source_ops_over_rho_proxy": float_value(row.get("ops_over_rho")),
        "transfer_index": transfer,
        "transfer_offset": transfer - window_start,
    }


def order_key(policy: str, case: dict[str, Any]) -> tuple[Any, ...]:
    profile = case["public_profile"]
    transfer = int_value(profile.get("transfer_index"))
    salt_gap = int_value(profile.get("salt_gap"))
    public_hash = int_value(profile.get("public_hash"))
    first_leaf_has_90 = bool(profile.get("first_leaf_has_90"))
    second_leaf_has_90 = bool(profile.get("second_leaf_has_90"))
    ops_proxy = float_value(profile.get("source_ops_over_rho_proxy"))
    offset = int_value(profile.get("transfer_offset"))
    if policy == "baseline_transfer_order":
        return (transfer, public_hash)
    if policy == "transfer_offset_desc":
        return (-offset, transfer, public_hash)
    if policy == "salt_gap_desc":
        return (-salt_gap, transfer, public_hash)
    if policy == "salt_gap_asc":
        return (salt_gap, transfer, public_hash)
    if policy == "leaf90_first":
        return (0 if first_leaf_has_90 else 1, transfer, public_hash)
    if policy == "leaf90_first_salt_gap_desc":
        return (0 if first_leaf_has_90 else 1, -salt_gap, transfer, public_hash)
    if policy == "salt_gap_desc_leaf90_first":
        return (-salt_gap, 0 if first_leaf_has_90 else 1, transfer, public_hash)
    if policy == "second_leaf90_first":
        return (0 if second_leaf_has_90 else 1, transfer, public_hash)
    if policy == "public_hash_order":
        return (public_hash,)
    if policy == "ops_proxy_asc":
        return (ops_proxy, transfer, public_hash)
    if policy == "ops_proxy_desc":
        return (-ops_proxy, transfer, public_hash)
    raise ValueError(f"unknown policy {policy!r}")


def split_groups(groups: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [group for group in groups if int_value(group.get("window_start")) <= calibration_end],
        [group for group in groups if int_value(group.get("window_start")) > calibration_end],
    )


def scan_case(
    source: dict[str, Any],
    source_path: Path,
    row: dict[str, Any],
    rank_labels: dict[tuple[str, str, int, str, int, tuple[str, ...]], dict[str, Any]],
    source_case_charge_ops: int,
    accept_rule: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    scan, errors = scan_preform_case(source, row, accept_rule)
    score = rank_labels.get(case_key(source_path, row), {})
    charged_ops = source_case_charge_ops + int_value(scan.get("preform_ops"))
    rho = int_value(scan.get("rho"))
    attempt = {
        **scan,
        "accepted": preform_accepts(scan.get("point_matches") or [], accept_rule),
        "charged_ops": charged_ops,
        "charged_ops_over_rho": ratio(charged_ops, rho),
        "public_key_verified_diagnostic": bool(row.get("public_key_verified")),
        "rank_diagnostic": int_value(row.get("rank")),
        "rank_gain": int_value(score.get("rank_gain")) if score else None,
        "row_keys": row.get("row_keys") or [],
        "row_selector": row.get("row_selector"),
        "selector": row.get("selector"),
        "selected_leaf_count": int_value(row.get("selected_leaf_count")),
        "selected_row_count": int_value(row.get("selected_row_count")),
        "source_case_charge_ops": source_case_charge_ops,
        "source_path": str(source_path),
        "source_policy": row.get("source_policy"),
        "source_verified": bool(row.get("source_verified")),
        "top_k": int_value(row.get("top_k")),
        "transfer_index": int_value(row.get("transfer_index")),
        "unique_factor_relation_gain": int_value(score.get("unique_factor_relation_gain")) if score else None,
    }
    return attempt, errors


def build_case_bank(
    source_paths: list[Path],
    rank_labels: dict[tuple[str, str, int, str, int, tuple[str, ...]], dict[str, Any]],
    target: str,
    selector: str,
    top_k: int,
    min_transfer: int,
    source_case_charge_ops: int,
    accept_rule: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for source_path in source_paths:
        source = load_json(source_path)
        window = artifact_window(source_path)
        window_start = window[0] if window else 0
        rows = source_cases(source_path, source, target, selector, top_k, min_transfer)
        cases: list[dict[str, Any]] = []
        for row in rows:
            attempt, attempt_errors = scan_case(
                source,
                source_path,
                row,
                rank_labels,
                source_case_charge_ops,
                accept_rule,
            )
            cases.append(
                {
                    "attempt": attempt,
                    "public_profile": public_profile(row, window_start),
                }
            )
            errors.extend(
                {
                    **item,
                    "source_path": str(source_path),
                    "transfer_index": int_value(row.get("transfer_index")),
                }
                for item in attempt_errors
            )
        if not cases:
            continue
        groups.append(
            {
                "case_count": len(cases),
                "cases": cases,
                "source_path": str(source_path),
                "window": f"{window[0]}_{window[1]}" if window else "",
                "window_start": window_start,
            }
        )
    groups.sort(key=lambda group: (int_value(group.get("window_start")), str(group.get("source_path"))))
    return groups, errors


def simulate_policy(policy: str, groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for group in groups:
        ordered = sorted(group.get("cases") or [], key=lambda case: order_key(policy, case))
        attempts: list[dict[str, Any]] = []
        stop: dict[str, Any] | None = None
        for case in ordered:
            attempt = case["attempt"]
            attempts.append(
                {
                    "accepted": bool(attempt.get("accepted")),
                    "charged_ops_over_rho": attempt.get("charged_ops_over_rho"),
                    "point_match_support_multiset": attempt.get("point_match_support_multiset"),
                    "pos7_11111515_candidate_pos_multiset": attempt.get("pos7_11111515_candidate_pos_multiset"),
                    "pos7_11111515_point_match_count": attempt.get("pos7_11111515_point_match_count"),
                    "public_profile": case["public_profile"],
                    "rank_gain": attempt.get("rank_gain"),
                    "row_keys": attempt.get("row_keys") or [],
                    "transfer_index": attempt.get("transfer_index"),
                    "unique_factor_relation_gain": attempt.get("unique_factor_relation_gain"),
                }
            )
            if bool(attempt.get("accepted")):
                stop = attempt
                break
        rho_values = [int_value(case["attempt"].get("rho")) for case in ordered if int_value(case["attempt"].get("rho")) > 0]
        rho = max(rho_values) if rho_values else 0
        total_charged = sum(int_value((case["attempt"]).get("charged_ops")) for case in ordered[: len(attempts)])
        out.append(
            {
                "attempt_count": len(attempts),
                "attempts": attempts,
                "case_count": int_value(group.get("case_count")),
                "charged_ops": total_charged,
                "charged_ops_over_rho": ratio(total_charged, rho),
                "has_accepted_stop": stop is not None,
                "has_rank_gain_stop": bool(stop and int_value(stop.get("rank_gain")) > 0),
                "policy": policy,
                "rho": rho,
                "source_path": group.get("source_path"),
                "stop": attempts[-1] if stop else None,
                "window": group.get("window"),
                "window_start": group.get("window_start"),
            }
        )
    return out


def summarize(groups: list[dict[str, Any]]) -> dict[str, Any]:
    accepted = [group for group in groups if group.get("has_accepted_stop")]
    rank_hits = [group for group in groups if group.get("has_rank_gain_stop")]
    charged = sum(int_value(group.get("charged_ops")) for group in groups)
    rho = max([int_value(group.get("rho")) for group in groups if int_value(group.get("rho")) > 0] or [0])
    return {
        "accepted_stop_count": len(accepted),
        "attempt_count": sum(int_value(group.get("attempt_count")) for group in groups),
        "case_count": sum(int_value(group.get("case_count")) for group in groups),
        "charged_ops": charged,
        "charged_ops_over_rho": ratio(charged, rho),
        "cost_per_accepted_stop_over_rho": ratio(charged, rho * len(accepted)) if accepted and rho else None,
        "cost_per_rank_gain_stop_over_rho": ratio(charged, rho * len(rank_hits)) if rank_hits and rho else None,
        "group_count": len(groups),
        "rank_gain_stop_count": len(rank_hits),
    }


def policy_status(validation_summary: dict[str, Any]) -> str:
    rank_hits = int_value(validation_summary.get("rank_gain_stop_count"))
    cost = validation_summary.get("cost_per_rank_gain_stop_over_rho")
    if rank_hits <= 0:
        return "MISSES_VALIDATION_RANK_GAIN"
    if cost is not None and float_value(cost) < 1.0:
        return "BELOW_RHO"
    return "VALIDATES_ABOVE_RHO"


def best_calibration_policy(policy_summaries: list[dict[str, Any]]) -> dict[str, Any] | None:
    viable = [
        item
        for item in policy_summaries
        if int_value((item.get("calibration") or {}).get("rank_gain_stop_count")) > 0
    ]
    if not viable:
        return None
    viable.sort(
        key=lambda item: (
            float_value((item.get("calibration") or {}).get("cost_per_rank_gain_stop_over_rho"), 999999.0),
            -int_value((item.get("calibration") or {}).get("rank_gain_stop_count")),
            str(item.get("policy")),
        )
    )
    return viable[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", required=True)
    parser.add_argument("--calibration-end", type=int, default=4064)
    parser.add_argument(
        "--policies",
        default="baseline_transfer_order,salt_gap_desc,salt_gap_asc,leaf90_first,leaf90_first_salt_gap_desc,salt_gap_desc_leaf90_first,second_leaf90_first,transfer_offset_desc,public_hash_order,ops_proxy_asc,ops_proxy_desc",
    )
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collector_path = Path(args.collector)
    collector = load_json(collector_path)
    artifacts = collector.get("artifacts") if isinstance(collector.get("artifacts"), dict) else {}
    parameters = collector.get("parameters") if isinstance(collector.get("parameters"), dict) else {}
    source_paths = [Path(str(path)) for path in artifacts.get("source_paths") or []]
    rank_labels = rank_labels_by_source_case(
        [Path(str(path)) for path in artifacts.get("direct_certificates") or []],
        [Path(str(path)) for path in artifacts.get("rank_scorers") or []],
    )
    target = str(parameters.get("target") or "22050.cf1@11731")
    selector = str(parameters.get("selector") or "mode_low_term_support_total5")
    top_k = int_value(parameters.get("top_k"), 16)
    min_transfer = int_value(parameters.get("min_transfer"), 3560)
    source_case_charge_ops = int_value(parameters.get("source_case_charge_ops"), 1)
    accept_rule = str(parameters.get("accept_rule") or "point_match_scout7_double_11111515")
    policies = [item.strip() for item in str(args.policies).split(",") if item.strip()]
    case_bank, errors = build_case_bank(
        source_paths,
        rank_labels,
        target,
        selector,
        top_k,
        min_transfer,
        source_case_charge_ops,
        accept_rule,
    )
    policy_summaries: list[dict[str, Any]] = []
    groups_by_policy: dict[str, list[dict[str, Any]]] = {}
    for policy in policies:
        simulated = simulate_policy(policy, case_bank)
        groups_by_policy[policy] = simulated
        calibration, validation = split_groups(simulated, args.calibration_end)
        calibration_summary = summarize(calibration)
        validation_summary = summarize(validation)
        policy_summaries.append(
            {
                "calibration": calibration_summary,
                "claim_status": policy_status(validation_summary),
                "policy": policy,
                "validation": validation_summary,
            }
        )
    selected = best_calibration_policy(policy_summaries)
    selected_policy = str(selected.get("policy")) if selected else None
    payload = {
        "artifacts": {
            "collector": str(collector_path),
            "direct_certificates": artifacts.get("direct_certificates") or [],
            "rank_scorers": artifacts.get("rank_scorers") or [],
            "source_paths": [str(path) for path in source_paths],
        },
        "case_bank_summary": {
            "group_count": len(case_bank),
            "source_case_count": sum(int_value(group.get("case_count")) for group in case_bank),
        },
        "claim_status": (
            "SCOUT_POS7_SOURCE_CASE_ORDERING_NO_CALIBRATION_POLICY"
            if selected is None
            else f"SCOUT_POS7_SOURCE_CASE_ORDERING_{selected.get('claim_status')}"
        ),
        "created_at": now_iso(),
        "errors": errors,
        "groups_by_selected_policy": groups_by_policy.get(selected_policy, []) if selected_policy else [],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: source-case ordering is tested inside the existing scout-7 preform relation stream.",
            "Default policies use public transfer/salt/row-leaf metadata; rank and public-key verification are recorded only as diagnostics.",
            "The script rescans each source case to remove censoring from the previous early-stop collector.",
            "A below-rho ordered stream is an index-calculus precursor work order, not a deployed-curve ECDLP break.",
        ],
        "parameters": {
            "accept_rule": accept_rule,
            "calibration_end": args.calibration_end,
            "min_transfer": min_transfer,
            "policies": policies,
            "selector": selector,
            "source_case_charge_ops": source_case_charge_ops,
            "target": target,
            "top_k": top_k,
        },
        "policy_summaries": policy_summaries,
        "schema": "ecdlp.low_term_total2_scout_pos7_source_case_ordering_scout.v1",
        "selected_policy": selected,
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "case_bank_summary": payload["case_bank_summary"],
                "claim_status": payload["claim_status"],
                "error_count": len(errors),
                "selected_policy": selected_policy,
                "selected_validation": (selected or {}).get("validation"),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
