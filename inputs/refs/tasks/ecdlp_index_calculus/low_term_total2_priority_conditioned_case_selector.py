#!/usr/bin/env python3
"""Select direct-source cases from a priority-conditioned generator plan.

The generator plan names the row-key/transfer groups where priority columns
either reached exported forms and collapsed, or existed in selected support but
were lost before export.  This selector turns those work orders into concrete
`TARGET|TRANSFER|SELECTOR|TOP_K` batches for the existing direct certificate
exporter, while keeping row-key and validation gates visible.

It does not force a new relation form by itself.  Its job is to remove the
passive "export every verified case" step and give the launcher an auditable,
priority-conditioned subset.
"""

from __future__ import annotations

import argparse
import json
import shlex
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_PLAN = (
    STATE_DIR
    / "low_term_total2_priority_conditioned_generator_plan_10464_10535_col6_col15_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_priority_conditioned_case_selector_probe.json"
DEFAULT_SOURCE_TEMPLATE = (
    "ecdlp_index_calculus_state/"
    "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_{start}_{end}_col15_selector_expanded_probe.json"
)
DEFAULT_DIRECT_CERT_TEMPLATE = (
    "ecdlp_index_calculus_state/"
    "low_term_total2_direct_relation_equation_certificate_22050_col15_lowterm_support5_{start}_{end}_probe.json"
)
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_SELECTOR = "mode_low_term_support_total5"


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


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def row_key_list(value: Any) -> list[str]:
    return [str(item) for item in list_value(value)]


def row_key_set(value: Any) -> set[str]:
    return set(row_key_list(value))


def window_bounds(transfer_index: int, window_size: int) -> tuple[int, int]:
    start = transfer_index - (transfer_index % window_size)
    return start, start + window_size - 1


def format_window_path(template: str, transfer_index: int, window_size: int) -> str:
    start, end = window_bounds(transfer_index, window_size)
    return template.format(start=start, end=end, transfer=transfer_index)


def order_reports(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reports = payload.get("order_reports")
    return reports if isinstance(reports, dict) else {}


def source_case_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for policy_name, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        for offset, row in enumerate(result.get("stress_leaf_results") or []):
            if not isinstance(row, dict):
                continue
            rows.append(
                {
                    **row,
                    "_policy": policy_name,
                    "_policy_offset": offset,
                    "row_selector": row.get("row_selector") or row_selector,
                }
            )
    return rows


def compact_source_case(row: dict[str, Any], required_rows: set[str]) -> dict[str, Any]:
    rows = row_key_list(row.get("row_keys"))
    overlap = sorted(set(rows) & required_rows)
    return {
        "ops_over_rho": row.get("ops_over_rho"),
        "policy": row.get("_policy"),
        "policy_offset": int_value(row.get("_policy_offset")),
        "public_key_verified": row.get("public_key_verified"),
        "rank": int_value(row.get("rank")),
        "row_key_match": set(rows) == required_rows if required_rows else None,
        "row_key_overlap": overlap,
        "row_keys": rows,
        "selector": row.get("selector"),
        "source_verified": row.get("source_verified"),
        "target": row.get("target"),
        "top_k": int_value(row.get("top_k")),
        "transfer_index": int_value(row.get("transfer_index")),
    }


def find_matching_source_cases(
    source: dict[str, Any],
    target: str,
    transfer_index: int,
    selector: str,
    required_rows: set[str],
    max_cases: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = []
    for row in source_case_rows(source):
        if str(row.get("target")) != target:
            continue
        if int_value(row.get("transfer_index")) != transfer_index:
            continue
        if str(row.get("selector")) != selector:
            continue
        candidates.append(row)

    def sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
        rows = row_key_set(row.get("row_keys"))
        exact = rows == required_rows if required_rows else True
        overlap = len(rows & required_rows)
        ops = row.get("ops_over_rho")
        return (
            not exact,
            not bool(row.get("public_key_verified")),
            -int_value(row.get("rank")),
            -overlap,
            float(ops if ops is not None else 10**18),
            int_value(row.get("top_k")),
            str(row.get("_policy")),
        )

    candidates.sort(key=sort_key)
    exact_verified = [
        row
        for row in candidates
        if row_key_set(row.get("row_keys")) == required_rows
        and row.get("public_key_verified") is True
        and int_value(row.get("rank")) > 0
    ]
    selected = exact_verified[:max_cases]
    preview = [compact_source_case(row, required_rows) for row in candidates[: max(6, max_cases)]]
    return [compact_source_case(row, required_rows) for row in selected], preview


def lane_support_group(lane: dict[str, Any]) -> dict[str, Any]:
    group = lane.get("support_group")
    return group if isinstance(group, dict) else {}


def lane_desired_columns(lane: dict[str, Any]) -> list[int]:
    if lane.get("action") == "VARY_Q_PAIR_FOR_EXPORTED_PRIORITY_FORMS":
        raw = lane.get("desired_new_priority_columns")
    else:
        raw = lane.get("desired_priority_columns")
    return [int_value(item) for item in list_value(raw)]


def plan_lane_items(
    plan: dict[str, Any],
    max_q_pair: int,
    max_force_export: int,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for order, report in order_reports(plan).items():
        q_items = list_value(report.get("q_pair_lane"))[:max_q_pair]
        force_items = list_value(report.get("force_export_lane"))[:max_force_export]
        for lane_index, lane in enumerate(q_items):
            if isinstance(lane, dict):
                items.append({"lane": lane, "lane_index": lane_index, "order": str(order)})
        for lane_index, lane in enumerate(force_items):
            if isinstance(lane, dict):
                items.append({"lane": lane, "lane_index": lane_index, "order": str(order)})
    return items


def case_arg(case: dict[str, Any]) -> str:
    return "|".join(
        [
            str(case["target"]),
            str(case["transfer_index"]),
            str(case["selector"]),
            str(case["top_k"]),
        ]
    )


def command_for_batch(batch: dict[str, Any]) -> str:
    parts = [
        "python3",
        "tasks/ecdlp_index_calculus/low_term_total2_direct_source_relation_equation_certificate.py",
        "--source",
        str(batch["source"]),
        "--cases",
        str(batch["cases_arg"]),
        "--out",
        str(batch["out"]),
    ]
    return " ".join(shlex.quote(part) for part in parts)


def selector_summary(selected_cases: list[dict[str, Any]], lane_reports: list[dict[str, Any]]) -> dict[str, Any]:
    lane_status_counts: dict[str, int] = defaultdict(int)
    action_counts: dict[str, int] = defaultdict(int)
    for report in lane_reports:
        lane_status_counts[str(report.get("selection_status"))] += 1
        action_counts[str(report.get("action"))] += 1
    exact_lanes = sum(1 for report in lane_reports if report.get("selection_status") == "EXACT_SOURCE_CASES_SELECTED")
    return {
        "action_counts": dict(sorted(action_counts.items())),
        "exact_source_lane_count": exact_lanes,
        "lane_count": len(lane_reports),
        "lane_status_counts": dict(sorted(lane_status_counts.items())),
        "selected_case_count": len(selected_cases),
    }


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    plan_path = Path(args.plan)
    plan = load_json(plan_path)
    lane_items = plan_lane_items(plan, args.max_q_pair, args.max_force_export)
    source_cache: dict[Path, dict[str, Any] | None] = {}
    lane_reports = []
    selected_cases = []
    seen_cases: set[tuple[str, int, str, int, str]] = set()

    for item in lane_items:
        lane = item["lane"]
        group = lane_support_group(lane)
        transfer = int_value(group.get("transfer_index"))
        target = str(group.get("target") or args.target)
        selector = str(args.selector)
        required_rows = row_key_set(group.get("row_keys"))
        source_path = Path(format_window_path(args.source_template, transfer, args.window_size))
        direct_cert_path = Path(format_window_path(args.direct_cert_template, transfer, args.window_size))
        source_status = "SOURCE_ARTIFACT_FOUND" if source_path.exists() else "SOURCE_ARTIFACT_MISSING"
        if source_path not in source_cache:
            source_cache[source_path] = load_json(source_path) if source_path.exists() else None
        source = source_cache[source_path]
        matches: list[dict[str, Any]] = []
        preview: list[dict[str, Any]] = []
        if source is not None:
            matches, preview = find_matching_source_cases(
                source,
                target,
                transfer,
                selector,
                required_rows,
                args.max_cases_per_lane,
            )
        action = str(lane.get("action") or "unknown")
        status = (
            "EXACT_SOURCE_CASES_SELECTED"
            if matches
            else "NEEDS_SOURCE_REGENERATION_OR_ROWKEY_FORCE"
            if source_path.exists()
            else "NEEDS_SOURCE_ARTIFACT"
        )
        report = {
            "action": action,
            "desired_priority_columns": lane_desired_columns(lane),
            "direct_certificate_artifact": str(direct_cert_path),
            "direct_certificate_artifact_exists": direct_cert_path.exists(),
            "lane_index": int_value(item.get("lane_index")),
            "order": str(item.get("order")),
            "preview_matching_source_cases": preview,
            "required_row_keys": sorted(required_rows),
            "selection_status": status,
            "source_artifact": str(source_path),
            "source_status": source_status,
            "support_group": group,
            "transfer_index": transfer,
            "validation_gate": lane.get("success_gate") or lane.get("verification_gate"),
        }
        lane_reports.append(report)
        for match in matches:
            key = (
                str(match["target"]),
                int_value(match["transfer_index"]),
                str(match["selector"]),
                int_value(match["top_k"]),
                str(source_path),
            )
            if key in seen_cases:
                continue
            seen_cases.add(key)
            selected_cases.append(
                {
                    "action": action,
                    "case_arg": case_arg(match),
                    "desired_priority_columns": lane_desired_columns(lane),
                    "direct_certificate_artifact": str(direct_cert_path),
                    "direct_certificate_artifact_exists": direct_cert_path.exists(),
                    "order": str(item.get("order")),
                    "row_keys": match.get("row_keys") or [],
                    "selector": match.get("selector"),
                    "source_artifact": str(source_path),
                    "source_policy": match.get("policy"),
                    "source_policy_offset": int_value(match.get("policy_offset")),
                    "target": match.get("target"),
                    "top_k": int_value(match.get("top_k")),
                    "transfer_index": int_value(match.get("transfer_index")),
                    "validation_gate": report.get("validation_gate"),
                }
            )

    batches_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in selected_cases:
        batches_by_source[str(case["source_artifact"])].append(case)
    direct_export_batches = []
    for source, cases in sorted(batches_by_source.items()):
        transfers = sorted({int_value(case.get("transfer_index")) for case in cases})
        start, end = window_bounds(transfers[0], args.window_size)
        out_path = Path(args.out).with_name(
            f"{Path(args.out).stem}_direct_{start}_{end}_probe.json"
        )
        cases_arg = ";".join(case["case_arg"] for case in sorted(cases, key=lambda row: row["case_arg"]))
        batch = {
            "case_count": len(cases),
            "cases": cases,
            "cases_arg": cases_arg,
            "out": str(out_path),
            "source": source,
            "transfer_indices": transfers,
        }
        batch["command"] = command_for_batch(batch)
        direct_export_batches.append(batch)

    summary = selector_summary(selected_cases, lane_reports)
    claim_status = (
        "PRIORITY_CONDITIONED_CASE_SELECTOR_READY"
        if selected_cases
        else "NEGATIVE_RESULT_NO_EXACT_PRIORITY_SOURCE_CASES_SELECTED"
    )
    return {
        "artifacts": {
            "plan": str(plan_path),
            "source_template": args.source_template,
            "direct_cert_template": args.direct_cert_template,
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "direct_export_batches": direct_export_batches,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: selected cases are direct-source replay cases in the local verifier relation model.",
            "HEURISTIC: priority-conditioned selection is a generator steering step, not a proof of target descent.",
            "OPEN: success requires a later support/form scout or charged-residual scout to expose nonzero target-column residual support.",
            "This is not a faster-than-Pollard-rho ECDLP algorithm.",
        ],
        "lane_reports": lane_reports,
        "schema": "ecdlp.low_term_total2_priority_conditioned_case_selector.v1",
        "selected_cases": selected_cases,
        "summary": summary,
        "validation_gates": [
            "support-to-form status becomes PRIORITY_PRESERVED_IN_EXPORTED_FORMS for forced-export lanes",
            "pair-option scout observes at least three q ratios and partner supports for q-pair lanes",
            "charged-residual scout reports target_column_residual_group_count > 0",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    parser.add_argument("--source-template", default=DEFAULT_SOURCE_TEMPLATE)
    parser.add_argument("--direct-cert-template", default=DEFAULT_DIRECT_CERT_TEMPLATE)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--selector", default=DEFAULT_SELECTOR)
    parser.add_argument("--window-size", type=int, default=8)
    parser.add_argument("--max-q-pair", type=int, default=8)
    parser.add_argument("--max-force-export", type=int, default=16)
    parser.add_argument("--max-cases-per-lane", type=int, default=4)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_manifest(args)
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
