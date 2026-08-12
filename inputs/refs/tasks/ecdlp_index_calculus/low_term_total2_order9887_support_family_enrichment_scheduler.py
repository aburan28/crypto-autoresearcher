#!/usr/bin/env python3
"""Schedule support-family enrichment work for order-9887 trigger rows.

The input trigger-family ledger identifies holdout-positive support families.
This scheduler scans later broad-scout windows and ranks target/order row
contexts that did not become trigger hits but may be useful anchors for a
source generator that tries to force those families prospectively.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SCOUT_GLOB = str(
    STATE_DIR
    / "low_term_total2_priority_column_form_scout_*_remaining_cols_11779_7_9887_6_7_verified_probe.json"
)
DEFAULT_LEDGER = STATE_DIR / "low_term_total2_order9887_trigger_family_yield_cost_ledger_20048_20343_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_order9887_support_family_enrichment_scheduler_probe.json"
WINDOW_RE = re.compile(r"_scout_(?P<start>\d+)_(?P<end>\d+)_remaining_cols_")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def numeric_stats(values: list[Any]) -> dict[str, Any]:
    nums = [number for value in values if (number := float_value(value)) is not None]
    if not nums:
        return {"count": 0, "max": None, "mean": None, "min": None, "sum": 0.0}
    total = sum(nums)
    return {
        "count": len(nums),
        "max": round(max(nums), 8),
        "mean": round(total / len(nums), 8),
        "min": round(min(nums), 8),
        "sum": round(total, 8),
    }


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def parse_window(path: Path) -> tuple[int, int] | None:
    match = WINDOW_RE.search(path.name)
    if not match:
        return None
    return int(match.group("start")), int(match.group("end"))


def support_key(value: Any) -> str:
    support = [int_value(item) for item in list_value(value)]
    return ",".join(str(item) for item in support)


def support_list_from_key(key: str) -> list[int]:
    if not key:
        return []
    return [int(part) for part in key.split(",") if part != ""]


def row_pair_key(value: Any) -> str:
    rows = sorted(str(item) for item in list_value(value))
    return " + ".join(rows)


def family_keys_from_ledger(ledger: dict[str, Any]) -> list[str]:
    recommendation = dict_value(ledger.get("scheduler_recommendation"))
    scout_positive = [
        str(item) for item in list_value(recommendation.get("scout_positive_family_keys")) if str(item)
    ]
    if scout_positive:
        return scout_positive
    ranked = [str(item) for item in list_value(recommendation.get("ranked_family_keys")) if str(item)]
    if ranked:
        return ranked
    return sorted(dict_value(ledger.get("families")).keys())


def holdout_only_family_keys_from_ledger(ledger: dict[str, Any]) -> list[str]:
    recommendation = dict_value(ledger.get("scheduler_recommendation"))
    return [str(item) for item in list_value(recommendation.get("holdout_only_family_keys")) if str(item)]


def positive_row_pairs(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for window in list_value(ledger.get("windows")):
        if not isinstance(window, dict):
            continue
        for case in list_value(window.get("hit_cases")):
            if not isinstance(case, dict):
                continue
            key = row_pair_key(case.get("row_keys"))
            if not key:
                continue
            support = support_key(case.get("term_support"))
            row = rows.setdefault(
                key,
                {
                    "families": Counter(),
                    "hit_case_count": 0,
                    "source_charged_costs": [],
                    "transfers": Counter(),
                    "windows": Counter(),
                },
            )
            row["families"].update([support])
            row["hit_case_count"] += 1
            row["source_charged_costs"].append(case.get("source_charged_unit_ops_over_rho"))
            row["transfers"].update([str(case.get("transfer_index"))])
            row["windows"].update([str(window.get("window"))])
    normalized: dict[str, dict[str, Any]] = {}
    for key, row in sorted(rows.items()):
        normalized[key] = {
            "families": dict(sorted(row["families"].items())),
            "hit_case_count": row["hit_case_count"],
            "source_charged_unit_ops_over_rho": numeric_stats(row["source_charged_costs"]),
            "transfers": dict(sorted(row["transfers"].items())),
            "windows": dict(sorted(row["windows"].items())),
        }
    return normalized


def best_family_match(support: list[int], family_keys: list[str]) -> dict[str, Any]:
    support_set = set(support)
    best: dict[str, Any] | None = None
    for rank, key in enumerate(family_keys):
        family = set(support_list_from_key(key))
        overlap = sorted(support_set & family)
        missing = sorted(family - support_set)
        extra = sorted(support_set - family)
        exact = not missing and not extra
        contains = not missing
        score = (100 if exact else 80 if contains else 0) + 10 * len(overlap) - rank
        row = {
            "contains_family": contains,
            "exact_family": exact,
            "extra_columns": extra,
            "family": sorted(family),
            "family_key": key,
            "family_rank": rank,
            "missing_columns": missing,
            "overlap_columns": overlap,
            "overlap_count": len(overlap),
            "score": score,
        }
        if best is None or row["score"] > best["score"]:
            best = row
    return best or {
        "contains_family": False,
        "exact_family": False,
        "extra_columns": support,
        "family": [],
        "family_key": "",
        "family_rank": 999,
        "missing_columns": [],
        "overlap_columns": [],
        "overlap_count": 0,
        "score": 0,
    }


def scout_paths(scout_glob: str, start: int, end: int) -> list[Path]:
    paths = []
    for item in sorted(glob.glob(scout_glob)):
        path = Path(item)
        window = parse_window(path)
        if not window:
            continue
        window_start, window_end = window
        if window_start >= start and window_end <= end:
            paths.append(path)
    return paths


def compact_case(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "coeff_support": list_value(report.get("coeff_support")),
        "direct_ops_over_rho": report.get("direct_ops_over_rho"),
        "order": int_value(report.get("order")),
        "priority_hit_count": int_value(report.get("priority_hit_count")),
        "row_keys": list_value(report.get("row_keys")),
        "selector": report.get("selector"),
        "source_charged_unit_ops_over_rho": report.get("source_charged_unit_ops_over_rho"),
        "target": report.get("target"),
        "term_support": list_value(report.get("term_support")),
        "top_k": int_value(report.get("top_k")),
        "transfer_index": int_value(report.get("transfer_index")),
        "window": report.get("window"),
    }


def action_for_case(
    report: dict[str, Any],
    match: dict[str, Any],
    positive_pair: dict[str, Any] | None,
) -> tuple[str, str, int]:
    priority_hit = int_value(report.get("priority_hit_count")) > 0
    source_cost = float_value(report.get("source_charged_unit_ops_over_rho"))
    below_rho = source_cost is not None and source_cost <= 1.0
    if match.get("exact_family") and priority_hit:
        return "EXPORT_EXACT_FAMILY_TRIGGER", "exact holdout-positive support has a verified priority hit", 0
    if match.get("exact_family"):
        return "REPLAY_EXACT_FAMILY_WITH_EXPORT_VARIANTS", "exact family support appears without priority-hit promotion", 1
    if positive_pair is not None:
        return (
            "FORCE_FAMILY_COLUMNS_ON_RECURRENT_ROW_PAIR",
            "row pair has prior holdout-positive hits but current support is off-family",
            2,
        )
    if int_value(match.get("overlap_count")) >= 2:
        return "EXPAND_NEAR_FAMILY_SUPPORT", "current support overlaps a holdout-positive family in at least two columns", 3
    if below_rho:
        return "LOW_COST_TARGET_ROW_FAMILY_COLUMN_SWAP", "target/order row is below rho but off the validated support families", 4
    return "LOW_PRIORITY_OFF_FAMILY_CONTEXT", "target/order row is off-family and not below rho", 5


def analyze_case(
    report: dict[str, Any],
    family_keys: list[str],
    row_pairs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    support = [int_value(item) for item in list_value(report.get("term_support"))]
    match = best_family_match(support, family_keys)
    pair_key = row_pair_key(report.get("row_keys"))
    positive_pair = row_pairs.get(pair_key)
    action, rationale, priority = action_for_case(report, match, positive_pair)
    source_cost = float_value(report.get("source_charged_unit_ops_over_rho"))
    direct_cost = float_value(report.get("direct_ops_over_rho"))
    score = (
        100
        - 15 * priority
        + 4 * int_value(match.get("overlap_count"))
        + (8 if positive_pair else 0)
        + (6 if source_cost is not None and source_cost <= 1.0 else 0)
        - (float(match.get("family_rank") or 0) * 0.1)
    )
    return {
        "action": action,
        "best_family_match": match,
        "case": compact_case(report),
        "direct_ops_over_rho": direct_cost,
        "positive_row_pair_prior": positive_pair,
        "priority": priority,
        "rationale": rationale,
        "row_pair_key": pair_key,
        "score": round(score, 8),
        "source_charged_unit_ops_over_rho": source_cost,
    }


def analyze_window(
    path: Path,
    family_keys: list[str],
    row_pairs: dict[str, dict[str, Any]],
    target: str,
    order: int,
) -> dict[str, Any]:
    payload = load_json(path)
    summary = dict_value(payload.get("summary"))
    cases = [
        report
        for report in list_value(payload.get("case_reports"))
        if isinstance(report, dict)
        and str(report.get("target")) == target
        and int_value(report.get("order")) == order
    ]
    analyzed = [analyze_case(case, family_keys, row_pairs) for case in cases]
    action_counts = Counter(item["action"] for item in analyzed)
    return {
        "artifact": str(path),
        "candidate_case_count": int_value(summary.get("candidate_case_count")),
        "error_count": int_value(summary.get("error_count")),
        "order_hit_counts": dict_value(summary.get("order_hit_counts")),
        "replayed_case_count": int_value(summary.get("replayed_case_count")),
        "target_order_action_counts": dict(sorted(action_counts.items())),
        "target_order_case_count": len(analyzed),
        "target_order_cases": analyzed,
        "verified_priority_hit_count": int_value(summary.get("verified_priority_hit_count")),
        "window": list_value(payload.get("case_reports"))[0].get("window")
        if list_value(payload.get("case_reports")) and isinstance(list_value(payload.get("case_reports"))[0], dict)
        else "",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--scout-glob", default=DEFAULT_SCOUT_GLOB)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--order", type=int, default=9887)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--work-item-limit", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ledger = load_json(args.ledger)
    family_keys = family_keys_from_ledger(ledger)
    holdout_only_family_keys = holdout_only_family_keys_from_ledger(ledger)
    row_pairs = positive_row_pairs(ledger)
    paths = scout_paths(args.scout_glob, args.start, args.end)
    windows = [analyze_window(path, family_keys, row_pairs, args.target, args.order) for path in paths]
    work_items = [
        item
        for window in windows
        for item in list_value(window.get("target_order_cases"))
        if item.get("action") != "LOW_PRIORITY_OFF_FAMILY_CONTEXT"
    ]
    work_items.sort(
        key=lambda item: (
            int_value(item.get("priority"), 99),
            -float(item.get("score") or 0.0),
            float_value(item.get("source_charged_unit_ops_over_rho")) or 999.0,
            int_value(dict_value(item.get("case")).get("transfer_index")),
        )
    )
    action_counts = Counter(item["action"] for item in work_items)
    target_case_count = sum(int_value(window.get("target_order_case_count")) for window in windows)
    exact_hit_count = sum(
        1 for item in work_items if item.get("action") == "EXPORT_EXACT_FAMILY_TRIGGER"
    )
    if exact_hit_count:
        top_action = "EXPORT_EXACT_FAMILY_TRIGGER"
    elif action_counts.get("FORCE_FAMILY_COLUMNS_ON_RECURRENT_ROW_PAIR"):
        top_action = "FORCE_FAMILY_COLUMNS_ON_RECURRENT_ROW_PAIR"
    elif action_counts.get("EXPAND_NEAR_FAMILY_SUPPORT"):
        top_action = "EXPAND_NEAR_FAMILY_SUPPORT"
    elif action_counts.get("LOW_COST_TARGET_ROW_FAMILY_COLUMN_SWAP"):
        top_action = "LOW_COST_TARGET_ROW_FAMILY_COLUMN_SWAP"
    else:
        top_action = "GENERATE_FAMILY_SUPPORT_ROWS_FROM_PRIORS"

    payload = {
        "created_at": now_iso(),
        "family_keys": family_keys,
        "holdout_only_family_keys": holdout_only_family_keys,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: scheduler uses current scout artifacts and the P537-bank trigger-family ledger.",
            "HEURISTIC: work-item ranking is a source-generation guide, not a relation certificate.",
            "NO SPEEDUP CLAIM: direct export, factor substitution, sparse-LA, fresh-target transfer, and rho accounting remain separate gates.",
        ],
        "parameters": {
            "end": args.end,
            "ledger": str(args.ledger),
            "order": args.order,
            "scout_glob": args.scout_glob,
            "start": args.start,
            "target": args.target,
        },
        "positive_row_pairs": row_pairs,
        "schema": "ecdlp.low_term_total2_order9887_support_family_enrichment_scheduler.v1",
        "summary": {
            "action_counts": dict(sorted(action_counts.items())),
            "exact_exportable_trigger_count": exact_hit_count,
            "low_cost_target_order_case_count": sum(
                1
                for window in windows
                for item in list_value(window.get("target_order_cases"))
                if (float_value(item.get("source_charged_unit_ops_over_rho")) or 999.0) <= 1.0
            ),
            "recurrent_row_pair_work_item_count": action_counts.get(
                "FORCE_FAMILY_COLUMNS_ON_RECURRENT_ROW_PAIR", 0
            ),
            "target_order_case_count": target_case_count,
            "top_action": top_action,
            "window_count": len(windows),
            "work_item_count": len(work_items),
        },
        "top_work_items": work_items[: args.work_item_limit],
        "windows": windows,
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps(payload["top_work_items"][:5], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
