#!/usr/bin/env python3
"""P1074 disjoint-source validation for the P1073 two-stage packet."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1069_p231_forward_transfer_descent_accounting as p1069
import low_term_total2_p1071_p231_remaining_column_source_expansion as p1071
import low_term_total2_p1072_p231_topk7_split_validation as p1072
import low_term_total2_p1073_p231_topk7_order_compression as p1073


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1074_p231_disjoint_source_packet_validation.md"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1067 = STATE_DIR / "low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json"
DEFAULT_P1069 = STATE_DIR / "low_term_total2_p1069_p231_forward_transfer_descent_accounting_probe.json"
DEFAULT_P1072 = STATE_DIR / "low_term_total2_p1072_p231_topk7_split_validation_probe.json"
DEFAULT_P1073 = STATE_DIR / "low_term_total2_p1073_p231_topk7_order_compression_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1074_p231_disjoint_source_packet_validation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1074_p231_disjoint_source_packet_validation.v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def below_rho(prefix: dict[str, Any] | None) -> bool:
    if not prefix:
        return False
    return (p1055.float_value(prefix.get("marginal_charge_over_rho")) or float("inf")) < 1.0


def compact_ref(ref: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": ref.get("case_id"),
        "direct_ops_over_rho": ref.get("direct_ops_over_rho"),
        "priority_hits": ref.get("priority_hits") or [],
        "row_keys": ref.get("row_keys") or [],
        "salt_max": p1073.salt_max(ref),
        "salt_min": p1073.salt_min(ref),
        "salt_span": p1073.salt_span(ref),
        "selector": ref.get("selector"),
        "top_k": ref.get("top_k"),
        "transfer_index": ref.get("transfer_index"),
        "window": ref.get("window"),
        "window_start": ref.get("window_start"),
    }


def compact_policy_scan(result: dict[str, Any], ordered: list[dict[str, Any]], max_ids: int = 12) -> dict[str, Any]:
    return {
        "case_count": len(ordered),
        "first_rank_gain_prefix": result.get("first_rank_gain_prefix"),
        "first_target_column_prefix": result.get("first_target_column_prefix"),
        "final_stats": result.get("final_stats"),
        "ordered_case_ids": [ref["case_id"] for ref in ordered[:max_ids]],
        "ordered_case_ids_truncated": len(ordered) > max_ids,
        "top_ordered_refs": [compact_ref(ref) for ref in ordered[: min(5, len(ordered))]],
        "window_count": len({ref["window"] for ref in ordered}),
        "windows": sorted({ref["window"] for ref in ordered}, key=lambda item: int(str(item).split("_")[0])),
    }


def scan_refs(
    refs: list[dict[str, Any]],
    stage1_refs: list[dict[str, Any]],
    stage1_packet: dict[str, Any],
    factor_rows: dict[str, dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
    priority_columns: list[int],
    policy: dict[str, Any],
) -> dict[str, Any]:
    ordered = sorted(refs, key=policy["key"])
    result = p1072.prefix_scan(
        ordered,
        stage1_refs,
        stage1_packet,
        factor_rows,
        cache,
        args,
        priority_columns,
        args.target_column,
    )
    return compact_policy_scan(result, ordered)


def selected_target_inventory(args: argparse.Namespace, promotion_window_end: int) -> dict[str, Any]:
    targets: Counter[str] = Counter()
    combos: Counter[tuple[str, str, int]] = Counter()
    windows_by_target: dict[str, set[str]] = defaultdict(set)
    paths = sorted(args.state_dir.glob(args.selected_glob))
    case_count = 0
    for path in paths:
        window = p1055.window_from_name(path)
        if window is None:
            continue
        start, end = window
        if start <= promotion_window_end:
            continue
        payload = load_json(path)
        for case in payload.get("case_reports") or []:
            if not isinstance(case, dict):
                continue
            target = str(case.get("target"))
            selector = str(case.get("selector"))
            top_k = p1055.int_value(case.get("top_k"), -1)
            targets[target] += 1
            combos[(target, selector, top_k)] += 1
            windows_by_target[target].add(f"{start}_{end}")
            case_count += 1
    fresh_targets = sorted(target for target in targets if target != args.target)
    return {
        "case_count_after_promotion": case_count,
        "fresh_target_available": bool(fresh_targets),
        "fresh_targets": fresh_targets,
        "selected_artifact_count": len(paths),
        "target_counts": dict(targets),
        "top_combos": [
            {
                "case_count": count,
                "selector": selector,
                "target": target,
                "top_k": top_k,
                "window_count": len(windows_by_target[target]),
            }
            for (target, selector, top_k), count in combos.most_common(16)
        ],
        "window_counts_by_target": {target: len(windows) for target, windows in windows_by_target.items()},
    }


def per_window_scans(
    refs: list[dict[str, Any]],
    stage1_refs: list[dict[str, Any]],
    stage1_packet: dict[str, Any],
    factor_rows: dict[str, dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
    priority_columns: list[int],
    policy: dict[str, Any],
) -> list[dict[str, Any]]:
    windows = sorted({ref["window"] for ref in refs}, key=lambda item: factor_rows[item]["window_start"])
    rows = []
    for window in windows:
        scan = scan_refs(
            [ref for ref in refs if ref["window"] == window],
            stage1_refs,
            stage1_packet,
            factor_rows,
            cache,
            args,
            priority_columns,
            policy,
        )
        rows.append(
            {
                "below_rho_target_column": below_rho(scan.get("first_target_column_prefix")),
                "case_count": scan["case_count"],
                "final_stats": scan["final_stats"],
                "first_target_column_prefix": scan["first_target_column_prefix"],
                "top_ordered_refs": scan["top_ordered_refs"],
                "window": window,
                "window_start": factor_rows[window]["window_start"],
            }
        )
    return rows


def split_holdout_scans(
    refs: list[dict[str, Any]],
    stage1_refs: list[dict[str, Any]],
    stage1_packet: dict[str, Any],
    factor_rows: dict[str, dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
    priority_columns: list[int],
    policy: dict[str, Any],
) -> list[dict[str, Any]]:
    windows = sorted({ref["window"] for ref in refs}, key=lambda item: factor_rows[item]["window_start"])
    rows = []
    for split_after in range(1, len(windows)):
        holdout_windows = set(windows[split_after:])
        holdout_refs = [ref for ref in refs if ref["window"] in holdout_windows]
        scan = scan_refs(
            holdout_refs,
            stage1_refs,
            stage1_packet,
            factor_rows,
            cache,
            args,
            priority_columns,
            policy,
        )
        first = scan.get("first_target_column_prefix")
        rows.append(
            {
                "below_rho_target_column": below_rho(first),
                "first_target_column_prefix": first,
                "holdout_case_count": scan["case_count"],
                "holdout_window_count": scan["window_count"],
                "split_after_window_count": split_after,
                "split_after_window": windows[split_after - 1],
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1067", type=Path, default=DEFAULT_P1067)
    parser.add_argument("--p1069", type=Path, default=DEFAULT_P1069)
    parser.add_argument("--p1072", type=Path, default=DEFAULT_P1072)
    parser.add_argument("--p1073", type=Path, default=DEFAULT_P1073)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--priority-columns", default="6,7,10,14,15")
    parser.add_argument("--target-column", type=int, default=15)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--source", default="direct_source")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=7)
    parser.add_argument("--promoted-selector", default="mode_low_term_support_total5")
    parser.add_argument("--promoted-top-k", type=int, default=16)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    args = parser.parse_args()

    priority_columns = [int(item) for item in args.priority_columns.split(",") if item.strip()]
    p1073_payload = load_json(args.p1073)
    stage1_refs, validation_refs, stage1_packet, factor_rows, cache, inventory, factor_paths, selected_paths = p1073.build_context(args)
    policy = next(item for item in p1073.policy_catalog() if item["name"] == "high_salt_max")

    all_validation = scan_refs(validation_refs, stage1_refs, stage1_packet, factor_rows, cache, args, priority_columns, policy)
    winner_case_id = (all_validation.get("first_target_column_prefix") or {}).get("last_case_id")
    winner_ref = next((ref for ref in validation_refs if ref["case_id"] == winner_case_id), None)
    if winner_ref is None:
        raise ValueError("positive-control winner was not found in validation refs")

    exclude_winner_case_refs = [ref for ref in validation_refs if ref["case_id"] != winner_case_id]
    exclude_winner_window_refs = [ref for ref in validation_refs if ref["window"] != winner_ref["window"]]
    future_after_winner_refs = [ref for ref in validation_refs if ref["window_start"] > p1069.window_end(winner_ref)]

    exclude_winner_case = scan_refs(
        exclude_winner_case_refs,
        stage1_refs,
        stage1_packet,
        factor_rows,
        cache,
        args,
        priority_columns,
        policy,
    )
    exclude_winner_window = scan_refs(
        exclude_winner_window_refs,
        stage1_refs,
        stage1_packet,
        factor_rows,
        cache,
        args,
        priority_columns,
        policy,
    )
    future_after_winner = scan_refs(
        future_after_winner_refs,
        stage1_refs,
        stage1_packet,
        factor_rows,
        cache,
        args,
        priority_columns,
        policy,
    )
    per_window = per_window_scans(
        validation_refs,
        stage1_refs,
        stage1_packet,
        factor_rows,
        cache,
        args,
        priority_columns,
        policy,
    )
    split_holdouts = split_holdout_scans(
        validation_refs,
        stage1_refs,
        stage1_packet,
        factor_rows,
        cache,
        args,
        priority_columns,
        policy,
    )
    promotion_window_end = p1069.window_end((load_json(args.p1069).get("parameters") or {})["promotion_case"])
    target_inventory = selected_target_inventory(args, promotion_window_end)

    strict_success = bool(below_rho(exclude_winner_case.get("first_target_column_prefix")) or below_rho(exclude_winner_window.get("first_target_column_prefix")))
    disjoint_single_windows = [
        row
        for row in per_window
        if row["below_rho_target_column"] and row["window"] != winner_ref["window"]
    ]
    weak_success = bool(disjoint_single_windows)
    if strict_success:
        claim_status = "POSITIVE_SIGNAL_P1074_FROZEN_POLICY_DISJOINT_BELOW_RHO"
    elif weak_success:
        claim_status = "OBSERVATION_P1074_DISJOINT_COLUMN15_SINGLE_EXISTS_BUT_POLICY_FAILS_STRICT_SPLIT"
    else:
        claim_status = "NEGATIVE_RESULT_P1074_NO_DISJOINT_COLUMN15_SOURCE_SIGNAL"

    payload = {
        "artifact_hashes": {
            "contract": p1069.sha256_file(args.contract) if args.contract.exists() else None,
            "factor_artifact_count": len(factor_paths),
            "factor_artifact_digest": p1069.digest_paths(factor_paths),
            "p1059": p1069.sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1067": p1069.sha256_file(args.p1067) if args.p1067.exists() else None,
            "p1069": p1069.sha256_file(args.p1069) if args.p1069.exists() else None,
            "p1072": p1069.sha256_file(args.p1072) if args.p1072.exists() else None,
            "p1073": p1069.sha256_file(args.p1073) if args.p1073.exists() else None,
            "script": p1069.sha256_file(Path(__file__)),
            "selected_artifact_count": len(selected_paths),
            "selected_artifact_digest": p1069.digest_paths(selected_paths),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1059": str(args.p1059),
            "p1067": str(args.p1067),
            "p1069": str(args.p1069),
            "p1072": str(args.p1072),
            "p1073": str(args.p1073),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "DISJOINT-SOURCE-VALIDATION",
            "PUBLIC-SALT-ORDERING",
            "POLLARD-RHO-BOUNDARY",
            "TARGET-DESCENT-OPEN",
        ],
        "controls": {
            "all_validation_positive_control": all_validation,
            "exclude_winner_case": exclude_winner_case,
            "exclude_winner_window": exclude_winner_window,
            "future_after_winner_window": future_after_winner,
            "p1073_summary": p1073_payload.get("summary"),
            "per_window_scans": per_window,
            "split_holdout_scans": split_holdouts,
        },
        "expanded_source_inventory": inventory,
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "fresh_target_artifacts_available": target_inventory["fresh_target_available"],
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "strict_disjoint_policy_validated": strict_success,
            "target_descent_closed": False,
            "window_local_single_is_not_public_global_policy": weak_success and not strict_success,
        },
        "parameters": {
            "family_selector": args.selector,
            "family_top_k": args.top_k,
            "order": args.order,
            "policy": policy["name"],
            "priority_columns": priority_columns,
            "source": args.source,
            "stage1_refs": [compact_ref(ref) for ref in stage1_refs],
            "target": args.target,
            "target_column": args.target_column,
            "winner_case": compact_ref(winner_ref),
        },
        "record_counts": {
            "disjoint_single_window_count": len(disjoint_single_windows),
            "split_holdout_count": len(split_holdouts),
            "validation_case_count": len(validation_refs),
            "validation_window_count": len({ref["window"] for ref in validation_refs}),
        },
        "schema": SCHEMA,
        "strict_success": strict_success,
        "summary": {
            "all_validation_first_target": all_validation.get("first_target_column_prefix"),
            "case_excluded_first_target": exclude_winner_case.get("first_target_column_prefix"),
            "claim_status": claim_status,
            "disjoint_single_windows": [
                {
                    "case_count": row["case_count"],
                    "first_target_column_prefix": row["first_target_column_prefix"],
                    "top_ordered_refs": row["top_ordered_refs"],
                    "window": row["window"],
                }
                for row in disjoint_single_windows
            ],
            "fresh_target_available": target_inventory["fresh_target_available"],
            "fresh_targets": target_inventory["fresh_targets"],
            "future_after_winner_first_target": future_after_winner.get("first_target_column_prefix"),
            "strict_success": strict_success,
            "target_inventory": target_inventory,
            "weak_success": weak_success,
            "window_excluded_first_target": exclude_winner_window.get("first_target_column_prefix"),
            "winner_case_id": winner_case_id,
            "winner_window": winner_ref["window"],
        },
        "timestamp_utc": p1071.now_iso(),
    }
    write_json(args.out, payload)
    print(
        "claim={claim} strict_success={strict} weak_success={weak} "
        "fresh_targets={fresh} disjoint_single_windows={single} "
        "case_excluded_first={case_first} window_excluded_first={window_first} out={out}".format(
            claim=claim_status,
            strict=strict_success,
            weak=weak_success,
            fresh=len(target_inventory["fresh_targets"]),
            single=len(disjoint_single_windows),
            case_first=exclude_winner_case.get("first_target_column_prefix"),
            window_first=exclude_winner_window.get("first_target_column_prefix"),
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
