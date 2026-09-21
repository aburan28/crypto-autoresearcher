#!/usr/bin/env python3
"""Aggregate priority-column visibility across residual scout artifacts.

The live ECDLP loop now has several partial views of the same index-calculus
precursor:

* the factor-column target scout says which order-specific factor columns are
  still free after greedy rank-gain candidates;
* the priority-column form scout says which shared-product verified forms
  actually expose selected columns;
* the work order needs to distinguish a source-generation gap from a
  target-elimination/rank-bank gap.

This script joins those views across completed windows.  It does not assert a
faster-than-rho algorithm; it produces a compact, durable work order for the
next collector experiment.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_residual_column_gap_scout_10200_10263_probe.json"
DEFAULT_PRIORITY_COLUMNS = "11779=6,15;9887=0,5,6,7,8"


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


def parse_priority_columns(raw: str) -> dict[int, set[int]]:
    priorities: dict[int, set[int]] = {}
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise ValueError("priority entries must look like ORDER=COL,COL")
        order_raw, cols_raw = chunk.split("=", 1)
        priorities[int(order_raw.strip())] = {
            int(item.strip()) for item in cols_raw.split(",") if item.strip()
        }
    return priorities


def parse_paths(raw: str) -> list[Path]:
    return [Path(item) for item in raw.split(",") if item.strip()]


def window_label(path: Path) -> str:
    matches = re.findall(r"(?<!\d)(\d{4,})_(\d{4,})(?!\d)", path.name)
    if matches:
        start, end = matches[-1]
        return f"{start}_{end}"
    return path.stem


def artifact_sort_key(path: Path) -> tuple[int, int, str]:
    label = window_label(path)
    if "_" in label:
        start, end = label.split("_", 1)
        if start.isdigit() and end.isdigit():
            return int(start), int(end), path.name
    return 10**18, 10**18, path.name


def case_hits(case: dict[str, Any]) -> set[int]:
    return {
        int_value(item)
        for item in (case.get("priority_term_hits") or []) + (case.get("priority_coeff_hits") or [])
    }


def priority_hit_index(priority_artifacts: list[Path]) -> dict[tuple[str, int, int], dict[str, Any]]:
    indexed: dict[tuple[str, int, int], dict[str, Any]] = defaultdict(
        lambda: {
            "case_count": 0,
            "examples": [],
            "verified_case_count": 0,
        }
    )
    for artifact in sorted(priority_artifacts, key=artifact_sort_key):
        window = window_label(artifact)
        payload = load_json(artifact)
        for case in payload.get("case_reports") or []:
            if not isinstance(case, dict):
                continue
            order = int_value(case.get("order"))
            if not order:
                continue
            for column in case_hits(case):
                bucket = indexed[(window, order, column)]
                bucket["case_count"] += 1
                if case.get("public_key_verified_replay"):
                    bucket["verified_case_count"] += 1
                examples = bucket["examples"]
                if len(examples) < 6:
                    examples.append(
                        {
                            "artifact": str(artifact),
                            "selector": case.get("selector"),
                            "target": case.get("target"),
                            "top_k": int_value(case.get("top_k")),
                            "transfer_index": int_value(case.get("transfer_index")),
                            "verified": bool(case.get("public_key_verified_replay")),
                            "window": window,
                        }
                    )
    return indexed


def target_column_report(order_report: dict[str, Any], column: int) -> dict[str, Any] | None:
    for report in order_report.get("target_column_reports") or []:
        if int_value(report.get("column")) == column:
            return report
    return None


def column_window_status(order_report: dict[str, Any], column: int) -> str:
    report = target_column_report(order_report, column)
    if report is not None:
        return str(report.get("status") or "POST_GREEDY_FREE")
    if column in {int_value(item) for item in order_report.get("post_greedy_pivot_columns") or []}:
        return "PIVOTED_AFTER_GREEDY"
    if column in {int_value(item) for item in order_report.get("base_free_columns") or []}:
        return "BASE_FREE_BUT_NOT_POST_GREEDY_FREE"
    return "NOT_FREE_OR_NOT_TRACKED"


def limited_families(report: dict[str, Any] | None) -> dict[str, int]:
    families = report.get("candidate_form_families") if isinstance(report, dict) else {}
    if not isinstance(families, dict):
        return {}
    ranked = sorted(
        ((str(name), int_value(count)) for name, count in families.items()),
        key=lambda item: (-item[1], item[0]),
    )
    return dict(ranked[:8])


def recommendation(aggregate: dict[str, Any]) -> str:
    latest_status = str(aggregate.get("latest_status"))
    if latest_status in {"PIVOTED_AFTER_GREEDY", "BASE_FREE_BUT_NOT_POST_GREEDY_FREE"}:
        return "COLUMN_CURRENTLY_ACCOUNTED_FOR_BY_GREEDY_ROWSPACE"
    if int_value(aggregate.get("verified_priority_hit_cases")) and not int_value(
        aggregate.get("post_greedy_relation_support_total")
    ):
        return "PROMOTE_VERIFIED_FORMS_TO_TARGET_ELIMINATED_ROWS"
    if int_value(aggregate.get("candidate_form_certificate_total")) and not int_value(
        aggregate.get("post_greedy_relation_support_total")
    ):
        return "TARGET_ELIMINATION_BRIDGE_NEEDED"
    if int_value(aggregate.get("post_greedy_relation_support_total")) and not int_value(
        aggregate.get("remaining_residual_support_total")
    ):
        return "CREATE_NEW_RESIDUAL_CLASSES"
    if not int_value(aggregate.get("candidate_form_certificate_total")) and not int_value(
        aggregate.get("verified_priority_hit_cases")
    ):
        return "GENERATE_ORDER_SPECIFIC_SOURCE_REPRESENTATION"
    return "EXPLOIT_REMAINING_RESIDUAL_GROUPS"


def empty_aggregate(order: int, column: int) -> dict[str, Any]:
    return {
        "candidate_form_certificate_total": 0,
        "column": column,
        "family_counts": Counter(),
        "latest_action": None,
        "latest_status": None,
        "latest_window": None,
        "order": order,
        "post_greedy_relation_support_total": 0,
        "remaining_residual_support_total": 0,
        "status_counts": Counter(),
        "verified_priority_hit_cases": 0,
        "window_count": 0,
        "window_reports": [],
        "work_order_counts": Counter(),
    }


def finalize_aggregate(aggregate: dict[str, Any]) -> dict[str, Any]:
    aggregate["family_counts"] = dict(
        sorted(aggregate["family_counts"].items(), key=lambda item: (-item[1], item[0]))[:10]
    )
    aggregate["status_counts"] = dict(sorted(aggregate["status_counts"].items()))
    aggregate["work_order_counts"] = dict(sorted(aggregate["work_order_counts"].items()))
    aggregate["recommended_next_action"] = recommendation(aggregate)
    return aggregate


def analyze(
    column_artifacts: list[Path],
    priority_artifacts: list[Path],
    priority_columns: dict[int, set[int]],
) -> dict[str, Any]:
    hits = priority_hit_index(priority_artifacts)
    aggregates = {
        (order, column): empty_aggregate(order, column)
        for order, columns in priority_columns.items()
        for column in sorted(columns)
    }
    window_reports: list[dict[str, Any]] = []
    for artifact in sorted(column_artifacts, key=artifact_sort_key):
        window = window_label(artifact)
        payload = load_json(artifact)
        for order, columns in priority_columns.items():
            order_report = (payload.get("order_reports") or {}).get(str(order))
            if not isinstance(order_report, dict):
                continue
            work_order = order_report.get("work_order") if isinstance(order_report.get("work_order"), dict) else {}
            action = str(work_order.get("action") or "UNKNOWN")
            for column in sorted(columns):
                aggregate = aggregates[(order, column)]
                report = target_column_report(order_report, column)
                status = column_window_status(order_report, column)
                priority_hits = hits.get((window, order, column), {})
                candidate_forms = int_value((report or {}).get("candidate_form_certificate_count"))
                post_relation = int_value((report or {}).get("post_greedy_relation_support_count"))
                remaining_residual = int_value((report or {}).get("remaining_residual_support_count"))
                verified_hit_count = int_value(priority_hits.get("verified_case_count"))
                family_counts = limited_families(report)
                for family, count in family_counts.items():
                    aggregate["family_counts"][family] += count
                aggregate["candidate_form_certificate_total"] += candidate_forms
                aggregate["latest_action"] = action
                aggregate["latest_status"] = status
                aggregate["latest_window"] = window
                aggregate["post_greedy_relation_support_total"] += post_relation
                aggregate["remaining_residual_support_total"] += remaining_residual
                aggregate["status_counts"][status] += 1
                aggregate["verified_priority_hit_cases"] += verified_hit_count
                aggregate["window_count"] += 1
                aggregate["work_order_counts"][action] += 1
                row = {
                    "action": action,
                    "artifact": str(artifact),
                    "candidate_form_certificate_count": candidate_forms,
                    "column": column,
                    "families": family_counts,
                    "order": order,
                    "post_greedy_relation_support_count": post_relation,
                    "priority_verified_hit_count": verified_hit_count,
                    "priority_hit_count": int_value(priority_hits.get("case_count")),
                    "remaining_residual_support_count": remaining_residual,
                    "status": status,
                    "window": window,
                }
                aggregate["window_reports"].append(row)
                window_reports.append(row)
    finalized = [finalize_aggregate(value) for value in aggregates.values()]
    active_gaps = [
        item
        for item in finalized
        if item.get("recommended_next_action")
        not in {"COLUMN_CURRENTLY_ACCOUNTED_FOR_BY_GREEDY_ROWSPACE"}
    ]
    return {
        "active_gap_count": len(active_gaps),
        "column_reports": sorted(finalized, key=lambda item: (item["order"], item["column"])),
        "window_reports": window_reports,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--column-scout-artifacts", required=True)
    parser.add_argument("--priority-scout-artifacts", required=True)
    parser.add_argument("--priority-columns", default=DEFAULT_PRIORITY_COLUMNS)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    column_artifacts = parse_paths(args.column_scout_artifacts)
    priority_artifacts = parse_paths(args.priority_scout_artifacts)
    priority_columns = parse_priority_columns(args.priority_columns)
    analysis = analyze(column_artifacts, priority_artifacts, priority_columns)
    payload = {
        "artifacts": {
            "column_scout_artifacts": [str(path) for path in sorted(column_artifacts, key=artifact_sort_key)],
            "priority_scout_artifacts": [str(path) for path in sorted(priority_artifacts, key=artifact_sort_key)],
        },
        "claim_status": (
            "RESIDUAL_COLUMN_GAPS_IDENTIFIED"
            if analysis["active_gap_count"]
            else "NO_ACTIVE_RESIDUAL_COLUMN_GAP_IDENTIFIED"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: order-specific columns are the current verifier factor namespace.",
            "HEURISTIC: recommended actions are collector-design guidance, not a complete target descent.",
            "NO SPEEDUP CLAIM: this artifact does not claim faster-than-Pollard-rho behavior.",
        ],
        "parameters": {
            "priority_columns": {str(order): sorted(cols) for order, cols in priority_columns.items()},
        },
        "schema": "ecdlp.low_term_total2_residual_column_gap_scout.v1",
        "summary": {
            "active_gap_count": analysis["active_gap_count"],
            "column_scout_artifact_count": len(column_artifacts),
            "priority_scout_artifact_count": len(priority_artifacts),
            "recommended_next_actions": {
                f"{item['order']}:{item['column']}": item["recommended_next_action"]
                for item in analysis["column_reports"]
            },
        },
        "target_columns": analysis["column_reports"],
        "window_reports": analysis["window_reports"],
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
