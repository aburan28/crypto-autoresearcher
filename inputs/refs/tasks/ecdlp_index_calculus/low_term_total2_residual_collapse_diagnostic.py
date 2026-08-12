#!/usr/bin/env python3
"""Explain how candidate factor rows fail to create target residual classes.

The charged residual-class scout answers whether a candidate creates a nonzero
quotient residual for requested columns.  This diagnostic explains the failure
mode row by row:

* the target columns never appear in target-eliminated factor rows;
* they appear before reduction but collapse into the current rowspace;
* they leave a residual, but only outside the requested columns;
* they produce the desired residual hit.

This keeps a negative result useful for source-generation: it tells the next
collector whether to change form visibility, pair selection, or quotient
direction.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_factor_rank_gap_diagnostic as gap
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_residual_collapse_diagnostic_probe.json"
DEFAULT_TARGET_COLUMNS = "11779=6,15"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def parse_paths(raw: str | None) -> list[Path]:
    if not raw:
        return []
    return [Path(item) for item in raw.split(",") if item.strip()]


def parse_target_columns(raw: str) -> dict[int, set[int]]:
    out: dict[int, set[int]] = {}
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise ValueError("target column entries must look like ORDER=COL,COL")
        order_raw, cols_raw = chunk.split("=", 1)
        out[int(order_raw.strip())] = {
            int(item.strip()) for item in cols_raw.split(",") if item.strip()
        }
    return out


def charged_ops_over_rho(info: dict[str, Any]) -> float | None:
    for key in ("generated_plus_shared_ops_over_rho", "direct_ops_over_rho", "shared_ops_over_rho"):
        if info.get(key) is not None:
            return float(info[key])
    return None


def compact_candidate(info: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact": info.get("artifact"),
        "artifact_offset": int_value(info.get("artifact_offset")),
        "charged_ops_over_rho": charged_ops_over_rho(info),
        "clause": info.get("clause"),
        "direct_ops_over_rho": info.get("direct_ops_over_rho"),
        "forms_count": int_value(info.get("forms_count")),
        "rank": int_value(info.get("rank")),
        "selector": info.get("selector"),
        "target": info.get("target"),
        "top_k": int_value(info.get("top_k")),
        "transfer_index": int_value(info.get("transfer_index")),
        "window": info.get("window"),
    }


def row_status(
    raw_target_hits: set[int],
    residual_target_hits: set[int],
    residual_support: set[int],
) -> str:
    if residual_target_hits:
        return "TARGET_RESIDUAL_HIT"
    if raw_target_hits and not residual_support:
        return "TARGET_SUPPORT_COLLAPSED_TO_BASE_ROWSPACE"
    if raw_target_hits and residual_support:
        return "TARGET_SUPPORT_RESIDUAL_MOVED_TO_OTHER_COLUMNS"
    if residual_support:
        return "NON_TARGET_RESIDUAL_ONLY"
    return "NO_TARGET_SUPPORT_AND_BASE_DEPENDENT"


def analyze_order(
    order: int,
    base_certificates: list[dict[str, Any]],
    candidate_certificates: list[dict[str, Any]],
    target_columns: set[int],
) -> dict[str, Any]:
    all_order_certs = [
        cert for cert in base_certificates + candidate_certificates if int_value(cert.get("order")) == order
    ]
    factor_count = gap.factor_count_for_order(all_order_certs, order)
    base_rows = gap.unique_relation_rows(base_certificates, order, factor_count)
    basis, pivots = gap.rref_rows([row["coeffs"] for row in base_rows], order)
    free_columns = [idx for idx in range(factor_count) if idx not in set(pivots)]
    status_counts: Counter[str] = Counter()
    column_counts: dict[int, Counter[str]] = {column: Counter() for column in sorted(target_columns)}
    selector_counts: Counter[str] = Counter()
    samples_by_status: dict[str, list[dict[str, Any]]] = defaultdict(list)
    candidate_reports = []
    for cert in candidate_certificates:
        if int_value(cert.get("order")) != order:
            continue
        info = gap.selected_info(cert)
        compact = compact_candidate(info)
        relation_rows = gap.relation_rows(cert, factor_count)
        candidate_status_counts: Counter[str] = Counter()
        for relation in relation_rows:
            raw_support = {int_value(idx) for idx in relation.get("factor_support") or []}
            residual = gap.reduce_row(relation["coeffs"], basis, pivots, order)
            residual_support = {idx for idx, value in enumerate(residual) if value % order}
            raw_target_hits = target_columns & raw_support
            residual_target_hits = target_columns & residual_support
            status = row_status(raw_target_hits, residual_target_hits, residual_support)
            status_counts[status] += 1
            candidate_status_counts[status] += 1
            selector_key = f"{compact.get('selector')}|top{compact.get('top_k')}|{compact.get('clause')}"
            selector_counts[f"{status}|{selector_key}"] += 1
            for column in sorted(target_columns):
                if column in raw_target_hits:
                    column_counts[column]["raw_support"] += 1
                if column in residual_target_hits:
                    column_counts[column]["residual_support"] += 1
                if column in raw_target_hits and status == "TARGET_SUPPORT_COLLAPSED_TO_BASE_ROWSPACE":
                    column_counts[column]["collapsed_to_base"] += 1
                if column in raw_target_hits and status == "TARGET_SUPPORT_RESIDUAL_MOVED_TO_OTHER_COLUMNS":
                    column_counts[column]["moved_to_other_columns"] += 1
            if len(samples_by_status[status]) < 8:
                normalized = gap.normalize_vector(residual, order)
                samples_by_status[status].append(
                    {
                        "candidate": compact,
                        "free_column_residual_support": sorted(set(free_columns) & residual_support),
                        "normalized_residual": list(normalized) if normalized is not None else None,
                        "raw_factor_support": sorted(raw_support),
                        "raw_target_hits": sorted(raw_target_hits),
                        "residual_support": sorted(residual_support),
                        "residual_target_hits": sorted(residual_target_hits),
                    }
                )
        candidate_reports.append(
            {
                "candidate": compact,
                "relation_count": len(relation_rows),
                "status_counts": dict(sorted(candidate_status_counts.items())),
            }
        )
    candidate_reports.sort(
        key=lambda item: (
            -sum(
                count
                for status, count in (item.get("status_counts") or {}).items()
                if status.startswith("TARGET_")
            ),
            float((item.get("candidate") or {}).get("charged_ops_over_rho") or 10**9),
        )
    )
    if status_counts.get("TARGET_RESIDUAL_HIT"):
        action = "PROMOTE_TARGET_RESIDUAL_ROWS"
        rationale = "some candidate rows already leave target-column residual support"
    elif status_counts.get("TARGET_SUPPORT_COLLAPSED_TO_BASE_ROWSPACE") or status_counts.get(
        "TARGET_SUPPORT_RESIDUAL_MOVED_TO_OTHER_COLUMNS"
    ):
        action = "CHANGE_PAIRING_OR_COEFFICIENT_ASSEMBLY"
        rationale = "target columns appear in raw factor rows but reduction removes them from the quotient target"
    else:
        action = "CHANGE_SOURCE_GENERATION_FOR_TARGET_VISIBILITY"
        rationale = "target columns do not appear in candidate target-eliminated factor rows"
    return {
        "base_factor_relation_count": len(base_rows),
        "base_rank": len(pivots),
        "candidate_certificate_count": sum(1 for cert in candidate_certificates if int_value(cert.get("order")) == order),
        "candidate_reports": candidate_reports[:30],
        "column_counts": {str(column): dict(sorted(counts.items())) for column, counts in column_counts.items()},
        "factor_variable_count": factor_count,
        "free_columns": free_columns,
        "pivot_columns": pivots,
        "samples_by_status": {status: samples for status, samples in sorted(samples_by_status.items())},
        "selector_status_counts": dict(sorted(selector_counts.items(), key=lambda item: (-item[1], item[0]))[:20]),
        "status_counts": dict(sorted(status_counts.items())),
        "target_columns": sorted(target_columns),
        "work_order": {
            "action": action,
            "priority_columns": sorted(target_columns),
            "rationale": rationale,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-certificates", required=True)
    parser.add_argument("--candidate-certificates", required=True)
    parser.add_argument("--target-columns", default=DEFAULT_TARGET_COLUMNS)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_paths = parse_paths(args.base_certificates)
    candidate_paths = parse_paths(args.candidate_certificates)
    target_columns = parse_target_columns(args.target_columns)
    if not base_paths:
        raise ValueError("no base certificates supplied")
    if not candidate_paths:
        raise ValueError("no candidate certificates supplied")
    base_certificates = factor_bank.load_certificates(base_paths)
    candidate_certificates = factor_bank.load_certificates(candidate_paths)
    order_reports = {
        str(order): analyze_order(order, base_certificates, candidate_certificates, columns)
        for order, columns in sorted(target_columns.items())
    }
    aggregate_status = Counter()
    for report in order_reports.values():
        aggregate_status.update(report.get("status_counts") or {})
    payload = {
        "artifacts": {
            "base_certificates": [str(path) for path in base_paths],
            "candidate_certificates": [str(path) for path in candidate_paths],
        },
        "claim_status": (
            "TARGET_RESIDUAL_ROWS_FOUND"
            if aggregate_status.get("TARGET_RESIDUAL_HIT")
            else "NEGATIVE_RESULT_TARGET_SUPPORT_COLLAPSES"
            if aggregate_status.get("TARGET_SUPPORT_COLLAPSED_TO_BASE_ROWSPACE")
            or aggregate_status.get("TARGET_SUPPORT_RESIDUAL_MOVED_TO_OTHER_COLUMNS")
            else "NEGATIVE_RESULT_TARGET_COLUMNS_NOT_VISIBLE_IN_ROWS"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: rowspace reduction uses the verifier's current factor-column namespace.",
            "HEURISTIC: collapse classes guide source-generation design; they are not target descent or a deployed-curve speedup claim.",
        ],
        "order_reports": order_reports,
        "parameters": {
            "target_columns": {str(order): sorted(cols) for order, cols in target_columns.items()},
        },
        "schema": "ecdlp.low_term_total2_residual_collapse_diagnostic.v1",
        "summary": {
            "base_certificate_count": len(base_certificates),
            "candidate_certificate_count": len(candidate_certificates),
            "order_count": len(order_reports),
            "status_counts": dict(sorted(aggregate_status.items())),
            "work_orders": {order: report.get("work_order") for order, report in order_reports.items()},
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
