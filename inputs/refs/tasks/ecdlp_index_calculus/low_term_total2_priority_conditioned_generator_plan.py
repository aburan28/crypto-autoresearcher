#!/usr/bin/env python3
"""Materialize priority-conditioned export/assembly generator work orders.

The scheduler says which cases need priority form export or q/pair variation.
The pair-option scout says whether exported-priority certificates have enough
partner/q-ratio diversity.  This planner joins those surfaces into concrete
generator lanes that a launcher can consume without re-reading the long
diagnostic artifacts.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_priority_conditioned_generator_plan_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_paths(raw: str | None) -> list[Path]:
    if not raw:
        return []
    return [Path(item) for item in raw.split(",") if item.strip()]


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def order_reports(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reports = payload.get("order_reports")
    return reports if isinstance(reports, dict) else {}


def compact_support_group(group: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact": group.get("artifact"),
        "certificate_count": int_value(group.get("certificate_count")),
        "certificate_form_target_hits": list_value(group.get("certificate_form_target_hits")),
        "direct_verified_support_priority_case_count": int_value(
            group.get("direct_verified_support_priority_case_count")
        ),
        "form_priority_case_count": int_value(group.get("form_priority_case_count")),
        "row_keys": list_value(group.get("row_keys")),
        "status": group.get("status"),
        "support_priority_case_count": int_value(group.get("support_priority_case_count")),
        "target": group.get("target"),
        "transfer_index": int_value(group.get("transfer_index")),
    }


def compact_assembly(sample: dict[str, Any]) -> dict[str, Any]:
    candidate = sample.get("candidate") if isinstance(sample.get("candidate"), dict) else {}
    return {
        "artifact": sample.get("artifact"),
        "assembly_status": sample.get("assembly_status"),
        "candidate": {
            "artifact": candidate.get("artifact"),
            "artifact_offset": int_value(candidate.get("artifact_offset")),
            "direct_ops_over_rho": candidate.get("direct_ops_over_rho"),
            "selector": candidate.get("selector"),
            "top_k": int_value(candidate.get("top_k")),
            "transfer_index": int_value(candidate.get("transfer_index")),
        },
        "q_coeffs": list_value(sample.get("q_coeffs")),
        "q_elimination_multipliers": sample.get("q_elimination_multipliers") or {},
        "raw_target_hits": list_value(sample.get("raw_target_hits")),
        "residual_target_hits": list_value(sample.get("residual_target_hits")),
        "target_column_details": sample.get("target_column_details") or {},
    }


def load_scheduler(paths: list[Path]) -> tuple[dict[str, list[dict[str, Any]]], Counter[str]]:
    by_order: dict[str, list[dict[str, Any]]] = defaultdict(list)
    action_counts: Counter[str] = Counter()
    for path in paths:
        payload = load_json(path)
        for order, report in order_reports(payload).items():
            action_counts.update(report.get("action_counts") or {})
            for index, item in enumerate(report.get("work_items") or []):
                if not isinstance(item, dict):
                    continue
                work_item = dict(item)
                work_item["_artifact"] = str(path)
                work_item["_artifact_offset"] = index
                by_order[str(order)].append(work_item)
    return by_order, action_counts


def load_pair_reports(paths: list[Path]) -> tuple[dict[str, list[dict[str, Any]]], Counter[str]]:
    by_order: dict[str, list[dict[str, Any]]] = defaultdict(list)
    status_counts: Counter[str] = Counter()
    for path in paths:
        payload = load_json(path)
        for order, report in order_reports(payload).items():
            status_counts.update(report.get("status_counts") or {})
            for index, candidate in enumerate(report.get("candidate_reports") or []):
                if not isinstance(candidate, dict):
                    continue
                item = dict(candidate)
                item["_artifact"] = str(path)
                item["_artifact_offset"] = index
                by_order[str(order)].append(item)
    return by_order, status_counts


def candidate_transfer(candidate_report: dict[str, Any]) -> int:
    candidate = candidate_report.get("candidate") if isinstance(candidate_report.get("candidate"), dict) else {}
    return int_value(candidate.get("transfer_index"))


def candidate_compact(candidate_report: dict[str, Any]) -> dict[str, Any]:
    candidate = candidate_report.get("candidate") if isinstance(candidate_report.get("candidate"), dict) else {}
    return {
        "artifact": candidate.get("artifact"),
        "artifact_offset": int_value(candidate.get("artifact_offset")),
        "direct_ops_over_rho": candidate.get("direct_ops_over_rho"),
        "forms_count": int_value(candidate.get("forms_count")),
        "rank": int_value(candidate.get("rank")),
        "selector": candidate.get("selector"),
        "target": candidate.get("target"),
        "top_k": int_value(candidate.get("top_k")),
        "transfer_index": int_value(candidate.get("transfer_index")),
        "window": candidate.get("window"),
    }


def pair_compact(candidate_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate": candidate_compact(candidate_report),
        "exported_priority_columns": list_value(candidate_report.get("exported_priority_columns")),
        "partner_support_diversity": list_value(candidate_report.get("partner_support_diversity")),
        "priority_pair_count": int_value(candidate_report.get("priority_pair_count")),
        "q_ratio_diversity": list_value(candidate_report.get("q_ratio_diversity")),
        "raw_target_pair_count": int_value(candidate_report.get("raw_target_pair_count")),
        "relation_status_counts": candidate_report.get("relation_status_counts") or {},
        "target_residual_hit_count": int_value(candidate_report.get("target_residual_hit_count")),
        "work_order": candidate_report.get("work_order") or {},
    }


def desired_columns(exported_columns: list[Any], target_columns: list[int]) -> list[int]:
    exported = {int_value(column) for column in exported_columns}
    return [column for column in target_columns if column not in exported]


def q_pair_lane_item(
    order: str,
    work_item: dict[str, Any],
    pair_reports: list[dict[str, Any]],
    target_columns: list[int],
) -> dict[str, Any]:
    support_group = compact_support_group(work_item.get("support_group") or {})
    assemblies = [compact_assembly(sample) for sample in list_value(work_item.get("related_assembly_samples"))]
    transfer = int_value(support_group.get("transfer_index"))
    matching_pairs = [pair_compact(report) for report in pair_reports if candidate_transfer(report) == transfer]
    exported_columns = sorted(
        {
            int_value(column)
            for report in matching_pairs
            for column in report.get("exported_priority_columns") or []
        }
    )
    q_ratios = sorted(
        {
            str(ratio)
            for report in matching_pairs
            for ratio in report.get("q_ratio_diversity") or []
        }
    )
    partner_supports = sorted(
        {
            str(partner)
            for report in matching_pairs
            for partner in report.get("partner_support_diversity") or []
        }
    )
    return {
        "action": "VARY_Q_PAIR_FOR_EXPORTED_PRIORITY_FORMS",
        "assembly_samples": assemblies,
        "desired_new_priority_columns": desired_columns(exported_columns, target_columns),
        "desired_new_q_ratio_count": max(3, len(q_ratios) + 2),
        "desired_new_partner_support_count": max(3, len(partner_supports) + 2),
        "exported_priority_columns": exported_columns,
        "matching_pair_reports": matching_pairs[:4],
        "order": order,
        "partner_support_diversity": partner_supports,
        "q_ratio_diversity": q_ratios,
        "rationale": (
            "Existing exported-priority forms collapse under target elimination; "
            "generate additional pairable priority forms with new q ratios and partner supports."
        ),
        "success_gate": "charged residual scout reports target_column_residual_group_count > 0",
        "support_group": support_group,
    }


def force_export_lane_item(order: str, work_item: dict[str, Any], target_columns: list[int]) -> dict[str, Any]:
    support_group = compact_support_group(work_item.get("support_group") or {})
    return {
        "action": "FORCE_PRIORITY_COLUMNS_IN_EXPORTED_RELATION_FORMS",
        "desired_priority_columns": target_columns,
        "order": order,
        "rationale": (
            "Selected-term priority support exists but verified relation forms did not "
            "export the requested columns."
        ),
        "support_group": support_group,
        "verification_gate": "support-to-form scout status becomes PRIORITY_PRESERVED_IN_EXPORTED_FORMS",
    }


def analyze_order(
    order: str,
    work_items: list[dict[str, Any]],
    pair_reports: list[dict[str, Any]],
    target_columns: list[int],
    limit: int,
) -> dict[str, Any]:
    q_pair_items = [
        item for item in work_items if item.get("action") == "VARY_Q_PAIR_FOR_EXPORTED_PRIORITY_FORMS"
    ]
    force_export_items = [
        item for item in work_items if item.get("action") == "FORCE_PRIORITY_COLUMNS_IN_EXPORTED_RELATION_FORMS"
    ]
    q_pair_lane = [
        q_pair_lane_item(order, item, pair_reports, target_columns)
        for item in q_pair_items[:limit]
    ]
    force_export_lane = [
        force_export_lane_item(order, item, target_columns)
        for item in force_export_items[:limit]
    ]
    top_action = (
        "PROMOTE_TARGET_RESIDUAL_ROWS"
        if any(
            int_value(report.get("target_residual_hit_count")) > 0
            for report in pair_reports
        )
        else "VARY_Q_PAIR_FOR_EXPORTED_PRIORITY_FORMS"
        if q_pair_lane
        else "FORCE_PRIORITY_COLUMNS_IN_EXPORTED_RELATION_FORMS"
        if force_export_lane
        else "CHANGE_SOURCE_GENERATION_FOR_PRIORITY_VISIBILITY"
    )
    return {
        "force_export_lane": force_export_lane,
        "force_export_lane_count": len(force_export_items),
        "pair_report_count": len(pair_reports),
        "q_pair_lane": q_pair_lane,
        "q_pair_lane_count": len(q_pair_items),
        "target_columns": target_columns,
        "top_action": top_action,
        "work_item_count": len(work_items),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scheduler-artifacts", required=True)
    parser.add_argument("--pair-option-artifacts", required=True)
    parser.add_argument("--target-columns", default="6,15")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scheduler_paths = parse_paths(args.scheduler_artifacts)
    pair_paths = parse_paths(args.pair_option_artifacts)
    if not scheduler_paths:
        raise ValueError("no scheduler artifacts supplied")
    if not pair_paths:
        raise ValueError("no pair-option artifacts supplied")
    target_columns = [int(item.strip()) for item in args.target_columns.split(",") if item.strip()]
    scheduler_by_order, scheduler_actions = load_scheduler(scheduler_paths)
    pair_by_order, pair_statuses = load_pair_reports(pair_paths)
    orders = sorted(set(scheduler_by_order) | set(pair_by_order), key=lambda value: int_value(value, 10**9))
    reports = {
        order: analyze_order(
            order,
            scheduler_by_order.get(order, []),
            pair_by_order.get(order, []),
            target_columns,
            args.limit,
        )
        for order in orders
    }
    q_pair_count = sum(report["q_pair_lane_count"] for report in reports.values())
    force_count = sum(report["force_export_lane_count"] for report in reports.values())
    payload = {
        "artifacts": {
            "pair_option_artifacts": [str(path) for path in pair_paths],
            "scheduler_artifacts": [str(path) for path in scheduler_paths],
        },
        "claim_status": (
            "PRIORITY_CONDITIONED_Q_PAIR_GENERATOR_PLAN_READY"
            if q_pair_count
            else "PRIORITY_CONDITIONED_FORCE_EXPORT_GENERATOR_PLAN_READY"
            if force_count
            else "NEGATIVE_RESULT_NO_PRIORITY_CONDITIONED_WORK_ITEMS"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: factor columns are the current order-specific low-term namespace.",
            "HEURISTIC: generator work items are steering hints, not target descent.",
            "OPEN: a row is promotable only after a charged residual scout finds nonzero target-column residual support.",
        ],
        "order_reports": reports,
        "schema": "ecdlp.low_term_total2_priority_conditioned_generator_plan.v1",
        "summary": {
            "force_export_lane_count": force_count,
            "order_count": len(reports),
            "pair_option_status_counts": dict(sorted(pair_statuses.items())),
            "q_pair_lane_count": q_pair_count,
            "scheduler_action_counts": dict(sorted(scheduler_actions.items())),
            "target_columns": target_columns,
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
