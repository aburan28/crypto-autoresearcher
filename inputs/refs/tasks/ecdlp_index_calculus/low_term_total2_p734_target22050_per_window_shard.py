#!/usr/bin/env python3
"""P734 shard broad target-22050 materialization into scorer-compatible windows."""

from __future__ import annotations

import argparse
import copy
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = (
    STATE_DIR
    / "frontier_public_leaf_policy_p733_target22050_materialized_fixed_row_20592_20719_col15_selector_expanded_probe.json"
)
DEFAULT_SUMMARY = STATE_DIR / "low_term_total2_p734_target22050_per_window_shard_summary.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_windows(indices: list[int], width: int) -> list[tuple[int, int, set[int]]]:
    if not indices:
        return []
    sorted_indices = sorted(indices)
    windows: list[tuple[int, int, set[int]]] = []
    for offset in range(0, len(sorted_indices), width):
        chunk = sorted_indices[offset : offset + width]
        windows.append((chunk[0], chunk[-1], set(chunk)))
    return windows


def filter_rows(rows: list[dict[str, Any]], transfers: set[int]) -> list[dict[str, Any]]:
    return [copy.deepcopy(row) for row in rows if int_value(row.get("transfer_index")) in transfers]


def summarize_row_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "best_ops_over_rho": None,
            "case_count": 0,
            "cases_below_rho": 0,
            "mean_ops_over_rho": None,
            "mean_selected_row_count": None,
            "oracle_row_count": 0,
            "oracle_row_hit_count": 0,
            "source_verified_case_count": 0,
            "verified_case_count": 0,
            "verified_source_case_recall": None,
        }
    source_verified_count = sum(1 for row in rows if row.get("source_verified"))
    verified_count = sum(1 for row in rows if row.get("public_key_verified"))
    oracle_count = sum(int_value(row.get("oracle_row_count")) for row in rows)
    oracle_hits = sum(int_value(row.get("oracle_row_hit_count")) for row in rows)
    return {
        "best_ops_over_rho": min(float_value(row.get("ops_over_rho"), 999999.0) for row in rows),
        "case_count": len(rows),
        "cases_below_rho": sum(1 for row in rows if float_value(row.get("ops_over_rho"), 999999.0) < 1.0),
        "mean_ops_over_rho": sum(float_value(row.get("ops_over_rho")) for row in rows) / len(rows),
        "mean_selected_row_count": sum(int_value(row.get("selected_row_count")) for row in rows) / len(rows),
        "oracle_row_count": oracle_count,
        "oracle_row_hit_count": oracle_hits,
        "source_verified_case_count": source_verified_count,
        "verified_case_count": verified_count,
        "verified_source_case_recall": verified_count / source_verified_count if source_verified_count else None,
    }


def selector_summaries(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("selector"))].append(row)
    return {
        selector: {
            "best_ops_over_rho": min(float_value(row.get("ops_over_rho"), 999999.0) for row in group),
            "case_count": len(group),
            "cases_below_rho": sum(1 for row in group if float_value(row.get("ops_over_rho"), 999999.0) < 1.0),
            "verified_case_count": sum(1 for row in group if row.get("public_key_verified")),
        }
        for selector, group in sorted(grouped.items())
    }


def transfer_summaries(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[int_value(row.get("transfer_index"))].append(row)
    return {
        str(transfer): {
            "best_ops_over_rho": min(float_value(row.get("ops_over_rho"), 999999.0) for row in group),
            "case_count": len(group),
            "cases_below_rho": sum(1 for row in group if float_value(row.get("ops_over_rho"), 999999.0) < 1.0),
            "verified_case_count": sum(1 for row in group if row.get("public_key_verified")),
        }
        for transfer, group in sorted(grouped.items())
    }


def summarize_leaf_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "best_ops_over_rho": None,
            "case_count": 0,
            "cases_below_rho": 0,
            "mean_selected_leaf_count": None,
            "selector_summaries": {},
            "transfer_summaries": {},
            "verified_case_count": 0,
        }
    return {
        "best_ops_over_rho": min(float_value(row.get("ops_over_rho"), 999999.0) for row in rows),
        "case_count": len(rows),
        "cases_below_rho": sum(1 for row in rows if float_value(row.get("ops_over_rho"), 999999.0) < 1.0),
        "mean_selected_leaf_count": sum(int_value(row.get("selected_leaf_count")) for row in rows) / len(rows),
        "selector_summaries": selector_summaries(rows),
        "transfer_summaries": transfer_summaries(rows),
        "verified_case_count": sum(1 for row in rows if row.get("public_key_verified")),
    }


def global_leaf_summary(rows: list[dict[str, Any]], target: str, negative_target: str) -> dict[str, Any]:
    target_counts = Counter(str(row.get("target")) for row in rows)
    rel2_rows = [row for row in rows if int_value(row.get("relation_count")) == 2]
    target_rel2 = [row for row in rel2_rows if str(row.get("target")) == target]
    examples = sorted(
        target_rel2,
        key=lambda row: (
            float_value(row.get("ops_over_rho"), 999999.0),
            int_value(row.get("transfer_index")),
            str(row.get("selector")),
            int_value(row.get("top_k")),
        ),
    )[:8]
    return {
        "below_rho_count": sum(1 for row in rows if float_value(row.get("ops_over_rho"), 999999.0) < 1.0),
        "negative_target_count": target_counts.get(negative_target, 0),
        "public_key_verified_count": sum(1 for row in rows if row.get("public_key_verified")),
        "rel2_count": len(rel2_rows),
        "rel2_verified_count": sum(1 for row in rel2_rows if row.get("public_key_verified")),
        "target_count": target_counts.get(target, 0),
        "target_counts": dict(sorted(target_counts.items())),
        "target_rel2_count": len(target_rel2),
        "target_rel2_examples": [
            {
                "ops_over_rho": row.get("ops_over_rho"),
                "relation_count": row.get("relation_count"),
                "row_keys": row.get("row_keys") or [],
                "selector": row.get("selector"),
                "top_k": row.get("top_k"),
                "transfer_index": row.get("transfer_index"),
            }
            for row in examples
        ],
        "target_rel2_verified_count": sum(1 for row in target_rel2 if row.get("public_key_verified")),
        "total_count": len(rows),
    }


def raw_summary(source: dict[str, Any], transfers: set[int], rows_per_case: int) -> dict[str, Any]:
    raw = ((source.get("summary") or {}).get("raw_materialization_summary") or {})
    case_transfer_counts = {
        str(k): int_value(v)
        for k, v in (raw.get("case_transfer_counts") or {}).items()
        if int_value(k) in transfers
    }
    case_count = sum(case_transfer_counts.values())
    raw_row_count = case_count * rows_per_case
    examples = [
        copy.deepcopy(item)
        for item in raw.get("target_key_exact_row_examples") or []
        if int_value(item.get("transfer_index")) in transfers
    ]
    return {
        "case_count": case_count,
        "case_target_counts": {((source.get("parameters") or {}).get("target")): case_count},
        "case_transfer_counts": case_transfer_counts,
        "generic_rho_steps_max": raw.get("generic_rho_steps_max"),
        "negative_target_raw_row_count": 0,
        "raw_row_count": raw_row_count,
        "source_verified_case_count": None,
        "target_key_exact_raw_row_count": raw_row_count,
        "target_key_exact_row_examples": examples[:8],
    }


def shard_payload(
    source: dict[str, Any],
    lo: int,
    hi: int,
    transfers: set[int],
    rows_per_case: int,
) -> dict[str, Any]:
    payload = copy.deepcopy(source)
    params = payload.get("parameters") or {}
    target = str(params.get("target"))
    negative_target = str(params.get("negative_target"))
    payload["created_at"] = now_iso()
    payload["method"] = "p734_per_window_shard_from_p733_target22050_focus_materialization"
    payload["schema"] = "ecdlp.frontier_public_leaf_policy.p734_target22050_per_window_materialized.v1"
    params["stress_transfer_indices"] = list(range(lo, hi + 1))
    params["p734_source_parent"] = str(DEFAULT_SOURCE)
    params["p734_window_start"] = lo
    params["p734_window_end"] = hi
    all_leaf_rows: list[dict[str, Any]] = []
    all_row_results: list[dict[str, Any]] = []
    source_verified_row_results = 0
    policy_count = 0
    for policy in (payload.get("policies") or {}).values():
        if not isinstance(policy, dict):
            continue
        policy_count += 1
        row_results = filter_rows(policy.get("stress_row_results") or [], transfers)
        leaf_results = filter_rows(policy.get("stress_leaf_results") or [], transfers)
        policy["stress_row_results"] = row_results
        policy["stress_leaf_results"] = leaf_results
        policy["stress_row_summary"] = summarize_row_results(row_results)
        policy["stress_leaf_summary"] = summarize_leaf_results(leaf_results)
        all_row_results.extend(row_results)
        all_leaf_rows.extend(leaf_results)
        source_verified_row_results += sum(1 for row in row_results if row.get("source_verified"))
    raw = raw_summary(source, transfers, rows_per_case)
    raw["source_verified_case_count"] = source_verified_row_results // max(policy_count, 1)
    payload["summary"] = {
        "claim_status": "P734_TARGET22050_PER_WINDOW_SHARD_SCORING_REQUIRED",
        "leaf_summary": global_leaf_summary(all_leaf_rows, target, negative_target),
        "raw_materialization_summary": raw,
    }
    return payload


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    source_path = Path(args.source)
    source = load_json(source_path)
    params = source.get("parameters") or {}
    indices = [int_value(item) for item in params.get("stress_transfer_indices") or []]
    rows_per_case = len(params.get("leaf_selectors") or []) or 1
    outputs = []
    for lo, hi, transfers in parse_windows(indices, int_value(args.window_width, 8)):
        payload = shard_payload(source, lo, hi, transfers, rows_per_case)
        out = STATE_DIR / (
            f"frontier_public_leaf_policy_p734_target22050_materialized_fixed_row_"
            f"{lo}_{hi}_col15_selector_expanded_probe.json"
        )
        write_json(out, payload)
        leaf_summary = payload["summary"]["leaf_summary"]
        raw = payload["summary"]["raw_materialization_summary"]
        outputs.append(
            {
                "path": str(out),
                "raw_row_count": raw["raw_row_count"],
                "source_verified_case_count": raw["source_verified_case_count"],
                "target_rel2_count": leaf_summary["target_rel2_count"],
                "target_rel2_verified_count": leaf_summary["target_rel2_verified_count"],
                "transfer_first": lo,
                "transfer_last": hi,
            }
        )
    summary = {
        "claim_status": "P734_TARGET22050_PER_WINDOW_SHARDS_READY_FOR_SCORING",
        "created_at": now_iso(),
        "outputs": outputs,
        "parameters": {
            "source": str(source_path),
            "target": params.get("target"),
            "negative_target": params.get("negative_target"),
            "window_width": int_value(args.window_width, 8),
        },
        "schema": "ecdlp.low_term_total2_p734_target22050_per_window_shard_summary.v1",
        "totals": {
            "artifact_count": len(outputs),
            "raw_row_count": sum(item["raw_row_count"] for item in outputs),
            "target_rel2_count": sum(item["target_rel2_count"] for item in outputs),
            "target_rel2_verified_count": sum(item["target_rel2_verified_count"] for item in outputs),
        },
    }
    write_json(Path(args.summary_out), summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--summary-out", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--window-width", type=int, default=8)
    return parser.parse_args()


def main() -> None:
    summary = analyze(parse_args())
    print(
        json.dumps(
            {
                "claim_status": summary["claim_status"],
                "outputs": len(summary["outputs"]),
                "totals": summary["totals"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
