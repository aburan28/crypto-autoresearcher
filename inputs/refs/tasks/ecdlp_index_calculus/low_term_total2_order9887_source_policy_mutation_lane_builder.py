#!/usr/bin/env python3
"""Build source-policy mutation lanes from order-9887 row-pair anchors.

This is a diagnostic bridge between the support-family scheduler and source
generation. It does not create relation certificates. It turns recurrent
row-pair anchors into explicit work orders: pin this row pair, force this
observed trigger family, and preserve the current off-family evidence.
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
DEFAULT_ANCHOR_SCHEDULER = (
    STATE_DIR / "low_term_total2_order9887_source_row_anchor_scheduler_20544_20599_probe.json"
)
DEFAULT_SCOUT_GLOB = str(
    STATE_DIR
    / "low_term_total2_priority_column_form_scout_*_remaining_cols_11779_7_9887_6_7_verified_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_order9887_source_policy_mutation_lanes_probe.json"
WINDOW_RE = re.compile(r"_scout_(?P<start>\d+)_(?P<end>\d+)_remaining_cols_")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


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


def parse_window(path: Path) -> tuple[int, int] | None:
    match = WINDOW_RE.search(path.name)
    if not match:
        return None
    return int(match.group("start")), int(match.group("end"))


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


def support_list(value: Any) -> list[int]:
    return [int_value(item) for item in list_value(value)]


def support_key(value: Any) -> str:
    return ",".join(str(item) for item in support_list(value))


def support_list_from_key(key: str) -> list[int]:
    if not key:
        return []
    return [int(part) for part in key.split(",") if part]


def row_pair_key(value: Any) -> str:
    rows = sorted(str(item) for item in list_value(value))
    return " + ".join(rows)


def compact_case(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact": report.get("artifact"),
        "coeff_support": list_value(report.get("coeff_support")),
        "direct_ops_over_rho": report.get("direct_ops_over_rho"),
        "forms_count": int_value(report.get("forms_count")),
        "order": int_value(report.get("order")),
        "priority_hit_count": int_value(report.get("priority_hit_count")),
        "row_keys": list_value(report.get("row_keys")),
        "selector": report.get("selector"),
        "shared_ops_over_rho": report.get("shared_ops_over_rho"),
        "source": report.get("source"),
        "source_charged_unit_ops_over_rho": report.get("source_charged_unit_ops_over_rho"),
        "target": report.get("target"),
        "term_support": list_value(report.get("term_support")),
        "top_k": int_value(report.get("top_k")),
        "transfer_index": int_value(report.get("transfer_index")),
        "window": report.get("window"),
    }


def choose_prior_family(work_item: dict[str, Any]) -> str:
    prior = dict_value(work_item.get("positive_row_pair_prior"))
    families = dict_value(prior.get("families"))
    if families:
        return sorted(families.items(), key=lambda item: (-int_value(item[1]), str(item[0])))[0][0]
    return str(dict_value(work_item.get("best_family_match")).get("family_key") or "")


def family_match(support: list[int], family: list[int]) -> dict[str, Any]:
    support_set = set(support)
    family_set = set(family)
    missing = sorted(family_set - support_set)
    extra = sorted(support_set - family_set)
    overlap = sorted(support_set & family_set)
    return {
        "contains_family": not missing,
        "exact_family": not missing and not extra,
        "extra_columns": extra,
        "family": sorted(family_set),
        "family_key": ",".join(str(item) for item in sorted(family_set)),
        "missing_columns": missing,
        "overlap_columns": overlap,
        "overlap_count": len(overlap),
    }


def load_contexts_by_pair(
    paths: list[Path],
    target: str,
    order: int,
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    contexts_by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    windows = []
    for path in paths:
        payload = load_json(path)
        summary = dict_value(payload.get("summary"))
        window = parse_window(path)
        window_label = f"{window[0]}_{window[1]}" if window else ""
        reports = [
            report
            for report in list_value(payload.get("case_reports"))
            if isinstance(report, dict)
            and str(report.get("target")) == target
            and int_value(report.get("order")) == order
        ]
        for report in reports:
            contexts_by_pair[row_pair_key(report.get("row_keys"))].append(compact_case(report))
        windows.append(
            {
                "artifact": str(path),
                "candidate_case_count": int_value(summary.get("candidate_case_count")),
                "error_count": int_value(summary.get("error_count")),
                "order_hit_counts": dict_value(summary.get("order_hit_counts")),
                "target_order_case_count": len(reports),
                "verified_priority_hit_count": int_value(summary.get("verified_priority_hit_count")),
                "window": window_label,
            }
        )
    return dict(contexts_by_pair), windows


def lane_status(matches: list[dict[str, Any]], contexts: list[dict[str, Any]]) -> str:
    exact_verified = any(
        bool(match.get("exact_family")) and int_value(context.get("priority_hit_count")) > 0
        for match, context in zip(matches, contexts)
    )
    if exact_verified:
        return "EXACT_FAMILY_VERIFIED_TRIGGER_OBSERVED"
    if any(bool(match.get("exact_family")) for match in matches):
        return "EXACT_FAMILY_ALREADY_VISIBLE_NEEDS_EXPORT_VARIANTS"
    if any(bool(match.get("contains_family")) for match in matches):
        return "CONTAINS_FAMILY_SUPPORT_NEEDS_EXPORT_VARIANTS"
    return "NEEDS_SOURCE_POLICY_MUTATION"


def summarize_contexts(contexts: list[dict[str, Any]], family: list[int]) -> dict[str, Any]:
    matches = [family_match(support_list(context.get("term_support")), family) for context in contexts]
    support_counts = Counter(support_key(context.get("term_support")) for context in contexts)
    support_counts.pop("", None)
    family_touch_count = sum(1 for match in matches if int_value(match.get("overlap_count")) > 0)
    exact_count = sum(1 for match in matches if bool(match.get("exact_family")))
    contains_count = sum(1 for match in matches if bool(match.get("contains_family")))
    low_cost_count = sum(
        1
        for context in contexts
        if (float_value(context.get("source_charged_unit_ops_over_rho")) or 999.0) <= 1.0
    )
    return {
        "contains_family_context_count": contains_count,
        "context_count": len(contexts),
        "direct_ops_over_rho": numeric_stats([context.get("direct_ops_over_rho") for context in contexts]),
        "exact_family_context_count": exact_count,
        "family_touch_context_count": family_touch_count,
        "low_cost_context_count": low_cost_count,
        "observed_support_counts": dict(sorted(support_counts.items())),
        "source_charged_unit_ops_over_rho": numeric_stats(
            [context.get("source_charged_unit_ops_over_rho") for context in contexts]
        ),
        "status": lane_status(matches, contexts),
        "windows": sorted({str(context.get("window")) for context in contexts if context.get("window")}),
    }


def group_anchor_work_items(work_items: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in work_items:
        if item.get("action") != "FORCE_FAMILY_COLUMNS_ON_RECURRENT_ROW_PAIR":
            continue
        row_key = str(item.get("row_pair_key") or "")
        family_key = choose_prior_family(item)
        if row_key and family_key:
            groups[(row_key, family_key)].append(item)
    return dict(groups)


def source_policy_spec(
    row_pair: str,
    family: list[int],
    base_case: dict[str, Any],
    contexts: list[dict[str, Any]],
) -> dict[str, Any]:
    selectors = sorted(
        {
            str(value)
            for value in [base_case.get("selector"), *[context.get("selector") for context in contexts]]
            if value
        }
    )
    top_ks = sorted(
        {
            int_value(value)
            for value in [base_case.get("top_k"), *[context.get("top_k") for context in contexts]]
            if int_value(value) > 0
        }
    )
    sources = sorted(
        {
            str(value)
            for value in [base_case.get("source"), *[context.get("source") for context in contexts]]
            if value
        }
    )
    return {
        "force_family_columns": family,
        "force_family_key": ",".join(str(item) for item in family),
        "pin_row_pair_key": row_pair,
        "pin_row_keys": list_value(base_case.get("row_keys")),
        "preferred_selectors": selectors,
        "preferred_top_k_values": top_ks,
        "source_artifact_candidates": sources,
    }


def build_lane(
    lane_number: int,
    row_pair: str,
    family_key: str,
    source_items: list[dict[str, Any]],
    contexts: list[dict[str, Any]],
) -> dict[str, Any]:
    family = support_list_from_key(family_key)
    source_items.sort(
        key=lambda item: (
            float_value(dict_value(item.get("case")).get("source_charged_unit_ops_over_rho")) or 999.0,
            int_value(dict_value(item.get("case")).get("transfer_index")),
            str(dict_value(item.get("case")).get("selector") or ""),
            int_value(dict_value(item.get("case")).get("top_k")),
        )
    )
    base_item = source_items[0]
    base_case = dict_value(base_item.get("case"))
    current_support = support_list(base_case.get("term_support"))
    current_match = family_match(current_support, family)
    context_summary = summarize_contexts(contexts, family)
    mutation_spec = source_policy_spec(row_pair, family, base_case, contexts)
    mutation_spec.update(
        {
            "avoid_current_extra_columns": current_match["extra_columns"],
            "current_support": current_support,
            "force_missing_columns": current_match["missing_columns"],
            "preserve_overlap_columns": current_match["overlap_columns"],
        }
    )
    return {
        "action": "PIN_ROW_PAIR_FORCE_FAMILY_COLUMNS",
        "base_case": base_case,
        "context_summary": context_summary,
        "current_family_match": current_match,
        "desired_family": family,
        "desired_family_key": family_key,
        "honesty_boundary": [
            "This lane is a source-policy work order, not a relation certificate.",
            "Promotion requires exact support replay, direct export, factor substitution, holdout checks, and rho accounting.",
        ],
        "lane_id": f"P554-L{lane_number:03d}",
        "positive_row_pair_prior": dict_value(base_item.get("positive_row_pair_prior")),
        "row_pair_key": row_pair,
        "source_policy_mutation": mutation_spec,
        "status": context_summary["status"],
        "support_contexts": contexts,
        "source_work_item_count": len(source_items),
        "source_work_items": source_items,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anchor-scheduler", type=Path, default=DEFAULT_ANCHOR_SCHEDULER)
    parser.add_argument("--scout-glob", default=DEFAULT_SCOUT_GLOB)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--order", type=int, default=9887)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--lane-limit", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    anchor = load_json(args.anchor_scheduler)
    paths = scout_paths(args.scout_glob, args.start, args.end)
    contexts_by_pair, scanned_windows = load_contexts_by_pair(paths, args.target, args.order)
    groups = group_anchor_work_items(
        [item for item in list_value(anchor.get("top_work_items")) if isinstance(item, dict)]
    )
    lanes = []
    for lane_number, ((row_pair, family_key), source_items) in enumerate(
        sorted(
            groups.items(),
            key=lambda item: (
                min(
                    float_value(dict_value(source_item.get("case")).get("source_charged_unit_ops_over_rho"))
                    or 999.0
                    for source_item in item[1]
                ),
                item[0][0],
                item[0][1],
            ),
        )[: args.lane_limit],
        start=1,
    ):
        lanes.append(
            build_lane(
                lane_number,
                row_pair,
                family_key,
                source_items,
                contexts_by_pair.get(row_pair, []),
            )
        )

    secondary_pool = [
        item
        for item in list_value(anchor.get("top_work_items"))
        if isinstance(item, dict) and item.get("action") == "LOW_COST_TARGET_ROW_FAMILY_COLUMN_SWAP"
    ]
    status_counts = Counter(str(lane.get("status")) for lane in lanes)
    payload = {
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: lanes are derived from P553 scheduler output and observed scout artifacts.",
            "HEURISTIC: row-pair/family forcing is a source-generation hypothesis.",
            "NO SPEEDUP CLAIM: no exact trigger, relation certificate, target descent, sparse-LA, or end-to-end rho comparison is established here.",
        ],
        "lanes": lanes,
        "parameters": {
            "anchor_scheduler": str(args.anchor_scheduler),
            "end": args.end,
            "order": args.order,
            "scout_glob": args.scout_glob,
            "start": args.start,
            "target": args.target,
        },
        "scanned_windows": scanned_windows,
        "schema": "ecdlp.low_term_total2_order9887_source_policy_mutation_lanes.v1",
        "secondary_low_cost_target_order_pool": secondary_pool,
        "summary": {
            "exact_family_already_visible_count": status_counts.get(
                "EXACT_FAMILY_ALREADY_VISIBLE_NEEDS_EXPORT_VARIANTS", 0
            ),
            "exact_family_verified_trigger_observed_count": status_counts.get(
                "EXACT_FAMILY_VERIFIED_TRIGGER_OBSERVED", 0
            ),
            "lane_count": len(lanes),
            "needs_source_policy_mutation_count": status_counts.get("NEEDS_SOURCE_POLICY_MUTATION", 0),
            "scanned_scout_window_count": len(scanned_windows),
            "secondary_low_cost_target_order_pool_count": len(secondary_pool),
            "source_work_item_count": sum(int_value(lane.get("source_work_item_count")) for lane in lanes),
            "status_counts": dict(sorted(status_counts.items())),
            "unique_row_pair_count": len({str(lane.get("row_pair_key")) for lane in lanes}),
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps(payload["lanes"][:5], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
