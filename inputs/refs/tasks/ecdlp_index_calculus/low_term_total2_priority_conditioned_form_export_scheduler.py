#!/usr/bin/env python3
"""Schedule next form-export actions from priority-support diagnostics.

This merges two diagnostics:

* support-to-form loss scouts say whether priority columns reach public forms;
* assembly-balance scouts say whether exported priority columns survive
  target-eliminated rowspace reduction.

The output is a ranked work-order list: force priority columns into exported
forms, vary q/pair assembly for exported-but-collapsed rows, or promote any
true target residuals.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_residual_collapse_diagnostic as collapse


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_priority_conditioned_form_export_scheduler_probe.json"


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


def row_key_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value)


def group_key(report: dict[str, Any]) -> tuple[str, int, tuple[str, ...]]:
    return (
        str(report.get("target") or "unknown"),
        int_value(report.get("transfer_index")),
        row_key_tuple(report.get("row_keys")),
    )


def candidate_key(candidate: dict[str, Any]) -> tuple[str, int]:
    return str(candidate.get("artifact") or ""), int_value(candidate.get("artifact_offset"))


def load_support_reports(paths: list[Path]) -> tuple[dict[str, list[dict[str, Any]]], Counter[str]]:
    reports_by_order: dict[str, list[dict[str, Any]]] = defaultdict(list)
    status_counts: Counter[str] = Counter()
    for path in paths:
        payload = load_json(path)
        order_reports = payload.get("order_reports") if isinstance(payload.get("order_reports"), dict) else {}
        for order, report in order_reports.items():
            if not isinstance(report, dict):
                continue
            status_counts.update(report.get("group_status_counts") or {})
            for group in report.get("group_reports") or []:
                if not isinstance(group, dict):
                    continue
                item = dict(group)
                item["_artifact"] = str(path)
                reports_by_order[str(order)].append(item)
    return reports_by_order, status_counts


def load_assembly_samples(paths: list[Path]) -> tuple[dict[str, list[dict[str, Any]]], Counter[str]]:
    samples_by_order: dict[str, list[dict[str, Any]]] = defaultdict(list)
    status_counts: Counter[str] = Counter()
    for path in paths:
        payload = load_json(path)
        order_reports = payload.get("order_reports") if isinstance(payload.get("order_reports"), dict) else {}
        for order, report in order_reports.items():
            if not isinstance(report, dict):
                continue
            status_counts.update(report.get("status_counts") or {})
            samples = report.get("samples_by_status") if isinstance(report.get("samples_by_status"), dict) else {}
            for status, rows in samples.items():
                for row in rows or []:
                    if not isinstance(row, dict):
                        continue
                    item = dict(row)
                    item["_artifact"] = str(path)
                    item["_status"] = status
                    samples_by_order[str(order)].append(item)
    return samples_by_order, status_counts


def compact_support_group(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact": report.get("_artifact"),
        "certificate_count": int_value(report.get("certificate_count")),
        "certificate_form_target_hits": report.get("certificate_form_target_hits") or [],
        "direct_verified_support_priority_case_count": int_value(
            report.get("direct_verified_support_priority_case_count")
        ),
        "form_priority_case_count": int_value(report.get("form_priority_case_count")),
        "row_keys": report.get("row_keys") or [],
        "status": report.get("status"),
        "support_priority_case_count": int_value(report.get("support_priority_case_count")),
        "target": report.get("target"),
        "transfer_index": int_value(report.get("transfer_index")),
    }


def compact_assembly_sample(sample: dict[str, Any]) -> dict[str, Any]:
    candidate = sample.get("candidate") if isinstance(sample.get("candidate"), dict) else {}
    return {
        "artifact": sample.get("_artifact"),
        "assembly_status": sample.get("_status"),
        "candidate": {
            "artifact": candidate.get("artifact"),
            "artifact_offset": int_value(candidate.get("artifact_offset")),
            "direct_ops_over_rho": candidate.get("direct_ops_over_rho"),
            "selector": candidate.get("selector"),
            "top_k": int_value(candidate.get("top_k")),
            "transfer_index": int_value(candidate.get("transfer_index")),
        },
        "q_coeffs": sample.get("q_coeffs") or [],
        "q_elimination_multipliers": sample.get("q_elimination_multipliers") or {},
        "raw_target_hits": sample.get("raw_target_hits") or [],
        "residual_target_hits": sample.get("residual_target_hits") or [],
        "target_column_details": sample.get("target_column_details") or {},
    }


def analyze_order(
    order: str,
    support_reports: list[dict[str, Any]],
    assembly_samples: list[dict[str, Any]],
) -> dict[str, Any]:
    assembly_by_transfer: dict[int, list[dict[str, Any]]] = defaultdict(list)
    target_residual_samples = []
    collapsed_samples = []
    for sample in assembly_samples:
        candidate = sample.get("candidate") if isinstance(sample.get("candidate"), dict) else {}
        transfer = int_value(candidate.get("transfer_index"))
        assembly_by_transfer[transfer].append(sample)
        if sample.get("_status") == "TARGET_RESIDUAL_HIT":
            target_residual_samples.append(sample)
        if sample.get("_status") == "TARGET_SUPPORT_COLLAPSED_TO_BASE_ROWSPACE":
            collapsed_samples.append(sample)

    action_counts: Counter[str] = Counter()
    work_items = []
    for report in support_reports:
        status = str(report.get("status") or "UNKNOWN")
        transfer = int_value(report.get("transfer_index"))
        related_assembly = assembly_by_transfer.get(transfer, [])
        if status == "PRIORITY_PRESERVED_IN_EXPORTED_FORMS":
            collapsed = [
                sample for sample in related_assembly if sample.get("_status") == "TARGET_SUPPORT_COLLAPSED_TO_BASE_ROWSPACE"
            ]
            residual_hits = [
                sample for sample in related_assembly if sample.get("_status") == "TARGET_RESIDUAL_HIT"
            ]
            if residual_hits:
                action = "PROMOTE_TARGET_RESIDUAL_ROWS"
                rationale = "priority columns reach exported forms and survive quotient reduction"
                priority = 0
            elif collapsed:
                action = "VARY_Q_PAIR_FOR_EXPORTED_PRIORITY_FORMS"
                rationale = "priority columns reach exported forms but collapse into the base rowspace"
                priority = 1
            else:
                action = "RUN_RESIDUAL_SCOUT_ON_PRIORITY_EXPORT"
                rationale = "priority columns reach exported forms but no assembly sample is linked"
                priority = 2
        elif status == "SUPPORT_PRIORITY_LOST_BEFORE_EXPORTED_FORMS":
            action = "FORCE_PRIORITY_COLUMNS_IN_EXPORTED_RELATION_FORMS"
            rationale = "selected-term priority support is lost before public form export"
            priority = 3
        else:
            action = "CHANGE_SOURCE_GENERATION_FOR_PRIORITY_VISIBILITY"
            rationale = "no selected-term priority support for this row-key group"
            priority = 4
        action_counts[action] += 1
        work_items.append(
            {
                "action": action,
                "priority": priority,
                "rationale": rationale,
                "related_assembly_samples": [
                    compact_assembly_sample(sample) for sample in related_assembly[:4]
                ],
                "support_group": compact_support_group(report),
            }
        )

    work_items.sort(
        key=lambda item: (
            int_value(item.get("priority"), 9),
            -int_value((item.get("support_group") or {}).get("certificate_count")),
            -int_value((item.get("support_group") or {}).get("direct_verified_support_priority_case_count")),
            -int_value((item.get("support_group") or {}).get("support_priority_case_count")),
            int_value((item.get("support_group") or {}).get("transfer_index")),
        )
    )
    if target_residual_samples:
        action = "PROMOTE_TARGET_RESIDUAL_ROWS"
    elif collapsed_samples:
        action = "VARY_Q_PAIR_FOR_EXPORTED_PRIORITY_FORMS"
    elif action_counts.get("FORCE_PRIORITY_COLUMNS_IN_EXPORTED_RELATION_FORMS"):
        action = "FORCE_PRIORITY_COLUMNS_IN_EXPORTED_RELATION_FORMS"
    else:
        action = "CHANGE_SOURCE_GENERATION_FOR_PRIORITY_VISIBILITY"
    return {
        "action_counts": dict(sorted(action_counts.items())),
        "assembly_sample_count": len(assembly_samples),
        "collapsed_target_export_count": len(collapsed_samples),
        "support_group_count": len(support_reports),
        "target_residual_hit_count": len(target_residual_samples),
        "work_items": work_items[:40],
        "work_order": {
            "action": action,
            "rationale": {
                "PROMOTE_TARGET_RESIDUAL_ROWS": "a priority export survived quotient reduction",
                "VARY_Q_PAIR_FOR_EXPORTED_PRIORITY_FORMS": "priority export exists, but target support collapses in rowspace",
                "FORCE_PRIORITY_COLUMNS_IN_EXPORTED_RELATION_FORMS": "priority support is visible but mostly lost before form export",
                "CHANGE_SOURCE_GENERATION_FOR_PRIORITY_VISIBILITY": "priority support is not visible enough upstream",
            }[action],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--support-to-form-artifacts", required=True)
    parser.add_argument("--assembly-artifacts", required=True)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    support_paths = collapse.parse_paths(args.support_to_form_artifacts)
    assembly_paths = collapse.parse_paths(args.assembly_artifacts)
    if not support_paths:
        raise ValueError("no support-to-form artifacts supplied")
    if not assembly_paths:
        raise ValueError("no assembly artifacts supplied")
    support_by_order, support_status_counts = load_support_reports(support_paths)
    assembly_by_order, assembly_status_counts = load_assembly_samples(assembly_paths)
    orders = sorted(set(support_by_order) | set(assembly_by_order))
    order_reports = {
        order: analyze_order(order, support_by_order.get(order, []), assembly_by_order.get(order, []))
        for order in orders
    }
    action_counts = Counter()
    for report in order_reports.values():
        action_counts.update(report.get("action_counts") or {})
    payload = {
        "artifacts": {
            "assembly_artifacts": [str(path) for path in assembly_paths],
            "support_to_form_artifacts": [str(path) for path in support_paths],
        },
        "claim_status": (
            "PRIORITY_EXPORT_TARGET_RESIDUAL_FOUND"
            if any(int_value(report.get("target_residual_hit_count")) for report in order_reports.values())
            else "PRIORITY_EXPORT_COLLAPSES_IN_ROWSPACE"
            if any(int_value(report.get("collapsed_target_export_count")) for report in order_reports.values())
            else "PRIORITY_SUPPORT_NEEDS_EXPORT_CONDITIONING"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: scheduler joins current support/export/residual artifacts by public transfer and row-key metadata.",
            "NO SPEEDUP CLAIM: this is a generator work order, not target descent or deployed-curve relevance.",
        ],
        "order_reports": order_reports,
        "schema": "ecdlp.low_term_total2_priority_conditioned_form_export_scheduler.v1",
        "summary": {
            "action_counts": dict(sorted(action_counts.items())),
            "assembly_status_counts": dict(sorted(assembly_status_counts.items())),
            "order_count": len(order_reports),
            "support_status_counts": dict(sorted(support_status_counts.items())),
            "work_orders": {order: report.get("work_order") for order, report in order_reports.items()},
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
