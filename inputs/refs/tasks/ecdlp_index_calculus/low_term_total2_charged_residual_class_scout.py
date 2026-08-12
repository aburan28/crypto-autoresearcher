#!/usr/bin/env python3
"""Scout charged candidate certificates for new quotient residual classes.

This is the active follow-up to the residual-column work orders.  The column
scout can say "create new residual classes", but the next falsifiable question
is narrower: do fresh, charged candidate certificates already contain a
target-eliminated row whose quotient residual touches the requested missing
columns?

The output is a work-order artifact.  A positive result means there are concrete
charged residual classes to promote.  A negative result means passive volume
from the supplied candidates duplicated the current rowspace, so source
generation must be changed before more harvesting is useful.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_factor_rank_gap_diagnostic as gap
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_charged_residual_class_scout_probe.json"
DEFAULT_TARGET_COLUMNS = "11779=6,15"


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


def charged_ops_over_rho(info: dict[str, Any]) -> float | None:
    generated = info.get("generated_plus_shared_ops_over_rho")
    if generated is not None:
        return float(generated)
    direct = info.get("direct_ops_over_rho")
    if direct is not None:
        return float(direct)
    shared = info.get("shared_ops_over_rho")
    if shared is not None:
        return float(shared)
    return None


def compact_candidate(info: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact": info.get("artifact"),
        "artifact_offset": int_value(info.get("artifact_offset")),
        "charged_ops_over_rho": charged_ops_over_rho(info),
        "clause": info.get("clause"),
        "direct_ops_over_rho": info.get("direct_ops_over_rho"),
        "forms_count": int_value(info.get("forms_count")),
        "generated_plus_shared_ops_over_rho": info.get("generated_plus_shared_ops_over_rho"),
        "rank": int_value(info.get("rank")),
        "selector": info.get("selector"),
        "shared_ops_over_rho": info.get("shared_ops_over_rho"),
        "target": info.get("target"),
        "top_k": int_value(info.get("top_k")),
        "transfer_index": int_value(info.get("transfer_index")),
        "window": info.get("window"),
    }


def column_scout_context(paths: list[Path], target_columns: dict[int, set[int]]) -> dict[str, Any]:
    latest: dict[str, dict[str, Any]] = {}
    status_counts: dict[str, Counter[str]] = defaultdict(Counter)
    family_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for path in sorted(paths, key=artifact_sort_key):
        payload = load_json(path)
        window = window_label(path)
        reports = payload.get("order_reports") if isinstance(payload.get("order_reports"), dict) else {}
        for order, columns in target_columns.items():
            order_report = reports.get(str(order))
            if not isinstance(order_report, dict):
                continue
            work_order = order_report.get("work_order") if isinstance(order_report.get("work_order"), dict) else {}
            target_reports = order_report.get("target_column_reports") or []
            for column in sorted(columns):
                key = f"{order}:{column}"
                found = None
                for report in target_reports:
                    if int_value(report.get("column")) == column:
                        found = report
                        break
                if found is None:
                    status = (
                        "PIVOTED_AFTER_GREEDY"
                        if column in {int_value(item) for item in order_report.get("post_greedy_pivot_columns") or []}
                        else "NOT_REPORTED"
                    )
                    families = {}
                else:
                    status = str(found.get("status") or "UNKNOWN")
                    families = found.get("candidate_form_families") if isinstance(found.get("candidate_form_families"), dict) else {}
                status_counts[key][status] += 1
                for family, count in families.items():
                    family_counts[key][str(family)] += int_value(count)
                latest[key] = {
                    "artifact": str(path),
                    "column": column,
                    "latest_action": work_order.get("action"),
                    "order": order,
                    "priority_columns": work_order.get("priority_columns") or [],
                    "status": status,
                    "window": window,
                }
    result = {}
    for key, latest_item in latest.items():
        result[key] = {
            **latest_item,
            "candidate_form_families": dict(
                sorted(family_counts[key].items(), key=lambda item: (-item[1], item[0]))[:8]
            ),
            "status_counts": dict(sorted(status_counts[key].items())),
        }
    return result


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
    groups: dict[tuple[int, ...], dict[str, Any]] = {}
    candidate_reports = []
    for cert in candidate_certificates:
        if int_value(cert.get("order")) != order:
            continue
        info = gap.selected_info(cert)
        candidate_rows = gap.relation_rows(cert, factor_count)
        residual_count = 0
        target_hit_count = 0
        candidate_samples = []
        for row in candidate_rows:
            residual = gap.reduce_row(row["coeffs"], basis, pivots, order)
            normalized = gap.normalize_vector(residual, order)
            if normalized is None:
                continue
            residual_count += 1
            residual_support = {idx for idx, value in enumerate(residual) if value % order}
            free_support = sorted(set(free_columns) & residual_support)
            target_hits = sorted(target_columns & residual_support)
            if target_hits:
                target_hit_count += 1
            group = groups.setdefault(
                normalized,
                {
                    "candidate_count": 0,
                    "candidate_samples": [],
                    "charged_ops_over_rho_values": [],
                    "free_column_support": [idx for idx in free_columns if normalized[idx] % order],
                    "residual_support": [idx for idx, value in enumerate(normalized) if value % order],
                    "target_column_hits": sorted(target_columns & {idx for idx, value in enumerate(normalized) if value % order}),
                },
            )
            group["candidate_count"] += 1
            cost = charged_ops_over_rho(info)
            if cost is not None:
                group["charged_ops_over_rho_values"].append(cost)
            if len(group["candidate_samples"]) < 8:
                group["candidate_samples"].append(compact_candidate(info))
            if len(candidate_samples) < 4:
                candidate_samples.append(
                    {
                        "free_column_support": free_support,
                        "relation_factor_support": row.get("factor_support") or [],
                        "residual_support": sorted(residual_support),
                        "target_column_hits": target_hits,
                    }
                )
        candidate_reports.append(
            {
                "candidate": compact_candidate(info),
                "candidate_relation_count": len(candidate_rows),
                "nonzero_residual_count": residual_count,
                "residual_samples": candidate_samples,
                "target_residual_hit_count": target_hit_count,
            }
        )
    group_list = []
    for signature, group in groups.items():
        costs = group.pop("charged_ops_over_rho_values")
        group_list.append(
            {
                "charged_ops_over_rho_min": min(costs) if costs else None,
                "charged_ops_over_rho_total": round(sum(costs), 8) if costs else None,
                "normalized_residual": list(signature),
                **group,
            }
        )
    group_list.sort(
        key=lambda item: (
            not bool(item.get("target_column_hits")),
            float(item.get("charged_ops_over_rho_min") or 10**9),
            -int_value(item.get("candidate_count")),
            item.get("free_column_support") or [],
        )
    )
    target_groups = [group for group in group_list if group.get("target_column_hits")]
    candidate_reports.sort(
        key=lambda item: (
            -int_value(item.get("target_residual_hit_count")),
            -int_value(item.get("nonzero_residual_count")),
            float((item.get("candidate") or {}).get("charged_ops_over_rho") or 10**9),
        )
    )
    if target_groups:
        action = "PROMOTE_CHARGED_RESIDUAL_CLASSES"
        rationale = "fresh charged candidates produce quotient residuals touching requested columns"
    elif group_list:
        action = "RETARGET_GENERATOR_TOWARD_PRIORITY_COLUMNS"
        rationale = "fresh candidates produce residuals, but not in the requested missing columns"
    else:
        action = "GENERATE_NEW_RESIDUAL_CLASSES"
        rationale = "fresh charged candidates duplicate the current target-eliminated rowspace"
    return {
        "base_factor_relation_count": len(base_rows),
        "base_rank": len(pivots),
        "candidate_certificate_count": sum(1 for cert in candidate_certificates if int_value(cert.get("order")) == order),
        "candidate_reports": candidate_reports[:30],
        "factor_variable_count": factor_count,
        "free_columns": free_columns,
        "pivot_columns": pivots,
        "residual_group_count": len(group_list),
        "residual_groups": group_list[:20],
        "target_column_residual_group_count": len(target_groups),
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
    parser.add_argument("--column-scout-artifacts")
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
    target_group_count = sum(int_value(report.get("target_column_residual_group_count")) for report in order_reports.values())
    residual_group_count = sum(int_value(report.get("residual_group_count")) for report in order_reports.values())
    column_context = column_scout_context(parse_paths(args.column_scout_artifacts), target_columns)
    payload = {
        "artifacts": {
            "base_certificates": [str(path) for path in base_paths],
            "candidate_certificates": [str(path) for path in candidate_paths],
            "column_scout_artifacts": [str(path) for path in parse_paths(args.column_scout_artifacts)],
        },
        "claim_status": (
            "CHARGED_TARGET_RESIDUAL_CLASSES_FOUND"
            if target_group_count
            else "NEGATIVE_RESULT_NO_CHARGED_TARGET_RESIDUAL_CLASSES"
            if candidate_certificates
            else "NO_CANDIDATES"
        ),
        "column_scout_context": column_context,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: quotient residuals are computed in the verifier's current factor-column namespace.",
            "HEURISTIC: charged residual classes guide source generation; they are not a complete target descent or deployed-curve speedup claim.",
            "NO SPEEDUP CLAIM: compare against Pollard rho only after a complete relation collection, linear algebra, and target-descent accounting exists.",
        ],
        "order_reports": order_reports,
        "parameters": {
            "target_columns": {str(order): sorted(cols) for order, cols in target_columns.items()},
        },
        "schema": "ecdlp.low_term_total2_charged_residual_class_scout.v1",
        "summary": {
            "base_certificate_count": len(base_certificates),
            "candidate_certificate_count": len(candidate_certificates),
            "order_count": len(order_reports),
            "residual_group_count": residual_group_count,
            "target_column_residual_group_count": target_group_count,
            "work_orders": {order: report.get("work_order") for order, report in order_reports.items()},
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
