#!/usr/bin/env python3
"""Build an order-9887 trigger-family yield and cost ledger.

This summarizes the fresh-trigger line after the combined freecol7 bank:
which broad-scout windows produced order-9887 priority hits, which support
families survived family-holdout target recovery, and how much broad scout
work was charged before the hits appeared.
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
DEFAULT_OUT = STATE_DIR / "low_term_total2_order9887_trigger_family_yield_cost_ledger_probe.json"
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


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 8)


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


def parse_paths(value: str) -> list[Path]:
    if not value:
        return []
    parts: list[str] = []
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        matches = sorted(glob.glob(chunk))
        parts.extend(matches or [chunk])
    return [Path(part) for part in parts]


def parse_window(path: Path) -> tuple[int, int] | None:
    match = WINDOW_RE.search(path.name)
    if not match:
        return None
    return int(match.group("start")), int(match.group("end"))


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def support_key(value: Any) -> str:
    support = [int_value(item) for item in list_value(value)]
    return ",".join(str(item) for item in support)


def support_list_from_key(key: str) -> list[int]:
    if not key:
        return []
    return [int(part) for part in key.split(",") if part != ""]


def compact_case(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact": report.get("artifact"),
        "coeff_support": report.get("coeff_support") or [],
        "direct_ops_over_rho": report.get("direct_ops_over_rho"),
        "forms_count": int_value(report.get("forms_count")),
        "order": int_value(report.get("order")),
        "priority_coeff_hits": report.get("priority_coeff_hits") or [],
        "priority_term_hits": report.get("priority_term_hits") or [],
        "row_keys": report.get("row_keys") or [],
        "selector": report.get("selector"),
        "shared_ops_over_rho": report.get("shared_ops_over_rho"),
        "source": report.get("source"),
        "source_charged_unit_ops_over_rho": report.get("source_charged_unit_ops_over_rho"),
        "target": report.get("target"),
        "term_support": report.get("term_support") or [],
        "top_k": int_value(report.get("top_k")),
        "transfer_index": int_value(report.get("transfer_index")),
        "window": report.get("window"),
    }


def summarize_scout(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    window = parse_window(path)
    summary = dict_value(payload.get("summary"))
    reports = [report for report in list_value(payload.get("case_reports")) if isinstance(report, dict)]
    hit_reports = [
        report
        for report in reports
        if int_value(report.get("order")) == 9887 and int_value(report.get("priority_hit_count")) > 0
    ]
    family_counts = Counter(support_key(report.get("term_support")) for report in hit_reports)
    family_counts.pop("", None)
    return {
        "artifact": str(path),
        "candidate_case_count": int_value(summary.get("candidate_case_count")),
        "error_count": int_value(summary.get("error_count")),
        "hit_cases": [compact_case(report) for report in hit_reports],
        "order_hit_counts": dict_value(summary.get("order_hit_counts")),
        "positive_families": dict(sorted(family_counts.items())),
        "priority_hit_count": int_value(summary.get("priority_hit_count")),
        "replayed_case_count": int_value(summary.get("replayed_case_count")),
        "verified_priority_hit_count": int_value(summary.get("verified_priority_hit_count")),
        "window": f"{window[0]}_{window[1]}" if window else "",
        "window_end": window[1] if window else None,
        "window_start": window[0] if window else None,
        "all_case_costs": {
            "direct_ops_over_rho": numeric_stats([report.get("direct_ops_over_rho") for report in reports]),
            "shared_ops_over_rho": numeric_stats([report.get("shared_ops_over_rho") for report in reports]),
            "source_charged_unit_ops_over_rho": numeric_stats(
                [report.get("source_charged_unit_ops_over_rho") for report in reports]
            ),
        },
        "hit_case_costs": {
            "direct_ops_over_rho": numeric_stats([report.get("direct_ops_over_rho") for report in hit_reports]),
            "shared_ops_over_rho": numeric_stats([report.get("shared_ops_over_rho") for report in hit_reports]),
            "source_charged_unit_ops_over_rho": numeric_stats(
                [report.get("source_charged_unit_ops_over_rho") for report in hit_reports]
            ),
        },
    }


def summarize_family_holdout(paths: list[Path]) -> dict[str, Any]:
    families: dict[str, dict[str, Any]] = {}
    artifact_rows: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            artifact_rows.append({"artifact": str(path), "missing": True})
            continue
        payload = load_json(path)
        for report in list_value(payload.get("reports")):
            if not isinstance(report, dict):
                continue
            key = str(report.get("family_key") or support_key(report.get("family")))
            if not key:
                continue
            row = families.setdefault(
                key,
                {
                    "artifacts": [],
                    "candidate_certificate_count": 0,
                    "candidate_form_count": 0,
                    "candidate_with_verified_recovery_count": 0,
                    "claim_status_counts": Counter(),
                    "false_recoverable_form_count": 0,
                    "family": support_list_from_key(key),
                    "positive_report_count": 0,
                    "status_counts": Counter(),
                    "training_certificate_count": 0,
                    "verified_recoverable_form_count": 0,
                },
            )
            row["artifacts"].append(str(path))
            row["candidate_certificate_count"] += int_value(report.get("candidate_certificate_count"))
            row["candidate_form_count"] += int_value(report.get("candidate_form_count"))
            row["candidate_with_verified_recovery_count"] += int_value(
                report.get("candidate_with_verified_recovery_count")
            )
            row["false_recoverable_form_count"] += int_value(report.get("false_recoverable_form_count"))
            row["training_certificate_count"] = max(
                int_value(row.get("training_certificate_count")),
                int_value(report.get("training_certificate_count")),
            )
            row["verified_recoverable_form_count"] += int_value(report.get("verified_recoverable_form_count"))
            if int_value(report.get("verified_recoverable_form_count")) > 0:
                row["positive_report_count"] += 1
            row["claim_status_counts"].update([str(report.get("claim_status") or "UNKNOWN")])
            row["status_counts"].update(dict_value(report.get("status_counts")))
            artifact_rows.append(
                {
                    "artifact": str(path),
                    "candidate_certificate_count": int_value(report.get("candidate_certificate_count")),
                    "candidate_form_count": int_value(report.get("candidate_form_count")),
                    "claim_status": report.get("claim_status"),
                    "false_recoverable_form_count": int_value(report.get("false_recoverable_form_count")),
                    "family": support_list_from_key(key),
                    "family_key": key,
                    "status_counts": dict_value(report.get("status_counts")),
                    "verified_recoverable_form_count": int_value(report.get("verified_recoverable_form_count")),
                }
            )
    normalized = {}
    for key, row in sorted(families.items()):
        normalized[key] = {
            **{field: value for field, value in row.items() if field not in {"claim_status_counts", "status_counts"}},
            "artifacts": sorted(set(row["artifacts"])),
            "claim_status_counts": dict(sorted(row["claim_status_counts"].items())),
            "status_counts": dict(sorted(row["status_counts"].items())),
        }
    return {"families": normalized, "reports": artifact_rows}


def family_rollup(windows: list[dict[str, Any]], holdout_families: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows: dict[str, dict[str, Any]] = {}
    for window in windows:
        hit_cases = [case for case in window["hit_cases"] if int_value(case.get("order")) == 9887]
        for case in hit_cases:
            key = support_key(case.get("term_support"))
            if not key:
                continue
            row = rows.setdefault(
                key,
                {
                    "family": support_list_from_key(key),
                    "hit_case_count": 0,
                    "hit_costs": {"direct": [], "shared": [], "source_charged": []},
                    "positive_window_count": 0,
                    "targets": Counter(),
                    "transfer_indices": Counter(),
                    "windows": set(),
                },
            )
            row["hit_case_count"] += 1
            row["windows"].add(window["window"])
            row["targets"].update([str(case.get("target") or "unknown")])
            row["transfer_indices"].update([str(case.get("transfer_index"))])
            row["hit_costs"]["direct"].append(case.get("direct_ops_over_rho"))
            row["hit_costs"]["shared"].append(case.get("shared_ops_over_rho"))
            row["hit_costs"]["source_charged"].append(case.get("source_charged_unit_ops_over_rho"))

    for key, holdout in holdout_families.items():
        row = rows.setdefault(
            key,
            {
                "family": support_list_from_key(key),
                "hit_case_count": 0,
                "hit_costs": {"direct": [], "shared": [], "source_charged": []},
                "positive_window_count": 0,
                "targets": Counter(),
                "transfer_indices": Counter(),
                "windows": set(),
            },
        )
        row["family_holdout"] = holdout

    normalized: dict[str, Any] = {}
    for key, row in sorted(rows.items()):
        windows_seen = sorted(row["windows"])
        holdout = dict_value(row.get("family_holdout"))
        normalized[key] = {
            "family": row["family"],
            "hit_case_count": row["hit_case_count"],
            "positive_window_count": len(windows_seen),
            "windows": windows_seen,
            "targets": dict(sorted(row["targets"].items())),
            "transfer_indices": dict(sorted(row["transfer_indices"].items())),
            "hit_costs": {
                "direct_ops_over_rho": numeric_stats(row["hit_costs"]["direct"]),
                "shared_ops_over_rho": numeric_stats(row["hit_costs"]["shared"]),
                "source_charged_unit_ops_over_rho": numeric_stats(row["hit_costs"]["source_charged"]),
            },
            "family_holdout": holdout or None,
            "verified_recoverable_form_count": int_value(holdout.get("verified_recoverable_form_count")),
            "false_recoverable_form_count": int_value(holdout.get("false_recoverable_form_count")),
        }
    return normalized


def scheduler_recommendation(summary: dict[str, Any], families: dict[str, Any]) -> dict[str, Any]:
    positive_holdout = [
        row
        for key, row in families.items()
        if int_value(row.get("verified_recoverable_form_count")) > 0
        and int_value(row.get("false_recoverable_form_count")) == 0
    ]
    scout_positive = [row for row in positive_holdout if int_value(row.get("positive_window_count")) > 0]
    holdout_only = [row for row in positive_holdout if int_value(row.get("positive_window_count")) == 0]
    recurring = [row for row in positive_holdout if int_value(row.get("positive_window_count")) >= 2]
    quiet_rate = 1.0 - (summary.get("positive_window_rate") or 0.0)
    if recurring:
        action = "BUILD_SUPPORT_FAMILY_ENRICHMENT_SCHEDULER"
        rationale = "at least one holdout-positive support family recurs across multiple windows"
    elif positive_holdout:
        action = "CONTINUE_TRIGGER_SCOUT_WITH_FAMILY_PRIORS"
        rationale = "holdout-positive families exist, but recurrence remains sparse"
    else:
        action = "SEARCH_FOR_NEW_TRIGGER_SUPPORT_FAMILIES"
        rationale = "no holdout-positive trigger family is present in this ledger"
    ranked_family_keys = [
        ",".join(str(item) for item in row.get("family") or [])
        for row in sorted(
            positive_holdout,
            key=lambda item: (
                -int_value(item.get("positive_window_count")),
                -int_value(item.get("verified_recoverable_form_count")),
                int_value(item.get("false_recoverable_form_count")),
            ),
        )
    ]
    scout_family_keys = [
        ",".join(str(item) for item in row.get("family") or [])
        for row in sorted(
            scout_positive,
            key=lambda item: (
                -int_value(item.get("positive_window_count")),
                -int_value(item.get("verified_recoverable_form_count")),
                int_value(item.get("false_recoverable_form_count")),
            ),
        )
    ]
    holdout_only_family_keys = [
        ",".join(str(item) for item in row.get("family") or [])
        for row in sorted(
            holdout_only,
            key=lambda item: (
                -int_value(item.get("verified_recoverable_form_count")),
                int_value(item.get("false_recoverable_form_count")),
            ),
        )
    ]
    family_text = ", ".join(f"[{key}]" for key in scout_family_keys) or "new holdout-positive scout families"
    holdout_text = ", ".join(f"[{key}]" for key in holdout_only_family_keys)
    holdout_clause = (
        f" Track holdout-only recovered subfamilies separately, starting with {holdout_text}."
        if holdout_only_family_keys
        else ""
    )
    return {
        "action": action,
        "holdout_only_family_keys": holdout_only_family_keys,
        "rationale": rationale,
        "quiet_window_fraction": round(quiet_rate, 8),
        "ranked_family_keys": ranked_family_keys,
        "scout_positive_family_keys": scout_family_keys,
        "next_concrete_action": (
            "Generate a prospective scorer that prioritizes public rows exposing observed "
            f"holdout-positive scout supports, starting with {family_text}, then rerun "
            "direct export and P537-bank substitution on fresh windows."
            f"{holdout_clause}"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scout-glob", default=DEFAULT_SCOUT_GLOB)
    parser.add_argument("--family-holdout-artifacts", default="")
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scout_paths = [Path(path) for path in sorted(glob.glob(args.scout_glob))]
    selected_paths = []
    for path in scout_paths:
        window = parse_window(path)
        if not window:
            continue
        start, end = window
        if start >= args.start and end <= args.end:
            selected_paths.append(path)

    windows = [summarize_scout(path) for path in selected_paths]
    holdout = summarize_family_holdout(parse_paths(args.family_holdout_artifacts))
    families = family_rollup(windows, holdout["families"])

    all_case_costs = {
        "direct_ops_over_rho": numeric_stats(
            [
                case.get("direct_ops_over_rho")
                for window in windows
                for case in load_json(Path(window["artifact"])).get("case_reports", [])
            ]
        ),
        "shared_ops_over_rho": numeric_stats(
            [
                case.get("shared_ops_over_rho")
                for window in windows
                for case in load_json(Path(window["artifact"])).get("case_reports", [])
            ]
        ),
        "source_charged_unit_ops_over_rho": numeric_stats(
            [
                case.get("source_charged_unit_ops_over_rho")
                for window in windows
                for case in load_json(Path(window["artifact"])).get("case_reports", [])
            ]
        ),
    }
    hit_case_costs = {
        "direct_ops_over_rho": numeric_stats(
            [case.get("direct_ops_over_rho") for window in windows for case in window["hit_cases"]]
        ),
        "shared_ops_over_rho": numeric_stats(
            [case.get("shared_ops_over_rho") for window in windows for case in window["hit_cases"]]
        ),
        "source_charged_unit_ops_over_rho": numeric_stats(
            [case.get("source_charged_unit_ops_over_rho") for window in windows for case in window["hit_cases"]]
        ),
    }
    window_count = len(windows)
    positive_window_count = sum(1 for window in windows if int_value(window["verified_priority_hit_count"]) > 0)
    replayed_case_count = sum(int_value(window["replayed_case_count"]) for window in windows)
    verified_hit_count = sum(int_value(window["verified_priority_hit_count"]) for window in windows)
    summary = {
        "all_case_costs": all_case_costs,
        "audited_range": f"{args.start}..{args.end}",
        "candidate_case_count": sum(int_value(window["candidate_case_count"]) for window in windows),
        "error_count": sum(int_value(window["error_count"]) for window in windows),
        "family_holdout_positive_count": sum(
            1
            for row in families.values()
            if int_value(row.get("verified_recoverable_form_count")) > 0
            and int_value(row.get("false_recoverable_form_count")) == 0
        ),
        "hit_case_costs": hit_case_costs,
        "positive_window_count": positive_window_count,
        "positive_window_rate": ratio(positive_window_count, window_count),
        "replayed_case_count": replayed_case_count,
        "scout_source_charged_ops_over_rho_sum": all_case_costs["source_charged_unit_ops_over_rho"]["sum"],
        "verified_hit_per_replayed_case_rate": ratio(verified_hit_count, replayed_case_count),
        "verified_priority_hit_count": verified_hit_count,
        "window_count": window_count,
    }
    payload = {
        "created_at": now_iso(),
        "families": families,
        "family_holdout_reports": holdout["reports"],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: this ledger uses the current remaining-column scout and P537-bank substitution model.",
            "HEURISTIC: support-family recurrence is scheduler evidence, not an asymptotic claim.",
            "NO SPEEDUP CLAIM: training cost, trigger-search probability, sparse linear algebra, fresh-target transfer, and cross-target scaling remain open.",
        ],
        "parameters": {
            "end": args.end,
            "family_holdout_artifacts": [str(path) for path in parse_paths(args.family_holdout_artifacts)],
            "priority_columns": "11779=7;9887=6,7",
            "scout_glob": args.scout_glob,
            "start": args.start,
        },
        "schema": "ecdlp.low_term_total2_order9887_trigger_family_yield_cost_ledger.v1",
        "scheduler_recommendation": scheduler_recommendation(summary, families),
        "summary": summary,
        "windows": windows,
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps(payload["scheduler_recommendation"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
