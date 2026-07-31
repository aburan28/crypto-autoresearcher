#!/usr/bin/env python3
"""Join selected-term support hints to exported relation forms.

The selected-leaf support scout can report that priority columns are visible in
public source metadata, while the verified relation/certificate forms may still
export only a smaller factor support.  This diagnostic makes that loss explicit
by joining three surfaces:

* selected-term support cases;
* verified priority-form replay cases;
* public direct relation-equation certificates.

It is a source-generation work-order scout, not a target descent.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_residual_collapse_diagnostic as collapse
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_support_to_form_loss_scout_probe.json"
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


def row_key_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value)


def group_key(target: Any, transfer_index: Any, row_keys: Any) -> tuple[str, int, tuple[str, ...]]:
    return str(target or "unknown"), int_value(transfer_index), row_key_tuple(row_keys)


def exact_key(case: dict[str, Any]) -> tuple[str, int, tuple[str, ...], str, int]:
    target, transfer, rows = group_key(case.get("target"), case.get("transfer_index"), case.get("row_keys"))
    return target, transfer, rows, str(case.get("selector") or "unknown"), int_value(case.get("top_k"))


def support(values: list[int], modulus: int) -> list[int]:
    return [idx for idx, value in enumerate(values) if value % modulus]


def case_columns(case: dict[str, Any], keys: list[str]) -> set[int]:
    out: set[int] = set()
    for key in keys:
        value = case.get(key)
        if isinstance(value, list):
            out.update(int_value(item) for item in value)
    return out


def compact_support_case(case: dict[str, Any], target_columns: set[int]) -> dict[str, Any]:
    hits = sorted(case_columns(case, ["priority_hits"]) & target_columns)
    return {
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "direct_public_key_verified": case.get("direct_public_key_verified"),
        "priority_hits": hits,
        "public_product_gate_selected": case.get("public_product_gate_selected"),
        "selected_term_support": case.get("selected_term_support") or [],
        "selector": case.get("selector"),
        "shared_product_ops_over_rho": case.get("shared_product_ops_over_rho"),
        "shared_product_public_key_verified": case.get("shared_product_public_key_verified"),
        "top_k": int_value(case.get("top_k")),
    }


def compact_form_case(case: dict[str, Any], target_columns: set[int]) -> dict[str, Any]:
    term_hits = sorted(case_columns(case, ["priority_term_hits"]) & target_columns)
    coeff_hits = sorted(case_columns(case, ["priority_coeff_hits"]) & target_columns)
    return {
        "coeff_support": case.get("coeff_support") or [],
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "priority_coeff_hits": coeff_hits,
        "priority_term_hits": term_hits,
        "public_key_verified_replay": case.get("public_key_verified_replay"),
        "selector": case.get("selector"),
        "shared_ops_over_rho": case.get("shared_ops_over_rho"),
        "term_support": case.get("term_support") or [],
        "top_k": int_value(case.get("top_k")),
        "verified": case.get("verified"),
    }


def compact_certificate(cert: dict[str, Any], target_columns: set[int]) -> dict[str, Any]:
    order = int_value(cert.get("order"))
    forms = [form for form in (cert.get("forms") or []) if isinstance(form, dict)]
    factor_count = max([max(0, len(form.get("coeffs") or []) - 1) for form in forms] or [0])
    form_reports = []
    target_hits: set[int] = set()
    for index, form in enumerate(forms):
        q_coeff, factor_coeffs, rhs = factor_bank.form_parts(form, order, factor_count)
        form_support = support(factor_coeffs, order)
        form_target_hits = sorted(set(form_support) & target_columns)
        target_hits.update(form_target_hits)
        form_reports.append(
            {
                "factor_support": form_support,
                "index": index,
                "q_coeff": q_coeff,
                "rhs": rhs,
                "target_hits": form_target_hits,
            }
        )
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    return {
        "artifact": cert.get("_artifact"),
        "artifact_offset": int_value(cert.get("_artifact_offset")),
        "certificate_status": cert.get("certificate_status"),
        "direct_ops_over_rho": selected.get("direct_ops_over_rho"),
        "form_target_hits": sorted(target_hits),
        "forms": form_reports,
        "forms_count": int_value(cert.get("forms_count")),
        "selector": selected.get("selector"),
        "top_k": int_value(selected.get("top_k")),
        "transfer_index": int_value(selected.get("transfer_index")),
    }


def load_case_reports(paths: list[Path]) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for path in paths:
        payload = load_json(path)
        for offset, report in enumerate(payload.get("case_reports") or []):
            if not isinstance(report, dict):
                continue
            item = dict(report)
            item["_artifact"] = str(path)
            item["_artifact_offset"] = offset
            reports.append(item)
    return reports


def analyze_order(
    order: int,
    target_columns: set[int],
    support_cases: list[dict[str, Any]],
    form_cases: list[dict[str, Any]],
    certificates: list[dict[str, Any]],
    sample_limit: int,
) -> dict[str, Any]:
    support_by_group: dict[tuple[str, int, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    form_by_group: dict[tuple[str, int, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    cert_by_group: dict[tuple[str, int, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    support_by_exact: dict[tuple[str, int, tuple[str, ...], str, int], list[dict[str, Any]]] = defaultdict(list)
    cert_by_exact: dict[tuple[str, int, tuple[str, ...], str, int], list[dict[str, Any]]] = defaultdict(list)

    for case in support_cases:
        support_by_group[group_key(case.get("target"), case.get("transfer_index"), case.get("row_keys"))].append(case)
        support_by_exact[exact_key(case)].append(case)
    for case in form_cases:
        form_by_group[group_key(case.get("target"), case.get("transfer_index"), case.get("row_keys"))].append(case)
    for cert in certificates:
        if int_value(cert.get("order")) != order:
            continue
        selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
        key = group_key(selected.get("target"), selected.get("transfer_index"), selected.get("row_keys"))
        cert_by_group[key].append(cert)
        cert_by_exact[
            (
                key[0],
                key[1],
                key[2],
                str(selected.get("selector") or "unknown"),
                int_value(selected.get("top_k")),
            )
        ].append(cert)

    all_groups = sorted(set(support_by_group) | set(form_by_group) | set(cert_by_group))
    status_counts: Counter[str] = Counter()
    support_priority_column_counts: Counter[int] = Counter()
    exact_selected_loss_count = 0
    group_reports = []
    for key in all_groups:
        support_group = support_by_group.get(key, [])
        form_group = form_by_group.get(key, [])
        cert_group = cert_by_group.get(key, [])
        support_priority_cases = [
            case for case in support_group if case_columns(case, ["priority_hits"]) & target_columns
        ]
        direct_verified_support_priority_cases = [
            case for case in support_priority_cases if case.get("direct_public_key_verified") is True
        ]
        form_priority_cases = [
            case
            for case in form_group
            if case_columns(case, ["priority_term_hits", "priority_coeff_hits"]) & target_columns
        ]
        cert_reports = [compact_certificate(cert, target_columns) for cert in cert_group]
        cert_target_hits = sorted(
            {
                column
                for report in cert_reports
                for column in report.get("form_target_hits") or []
            }
        )
        exact_losses = []
        for cert in cert_group:
            selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
            ekey = (
                key[0],
                key[1],
                key[2],
                str(selected.get("selector") or "unknown"),
                int_value(selected.get("top_k")),
            )
            exact_support_hits = sorted(
                {
                    column
                    for case in support_by_exact.get(ekey, [])
                    for column in case_columns(case, ["priority_hits"]) & target_columns
                }
            )
            cert_report = compact_certificate(cert, target_columns)
            if exact_support_hits and not cert_report.get("form_target_hits"):
                exact_selected_loss_count += 1
                exact_losses.append(
                    {
                        "certificate": cert_report,
                        "selected_support_priority_hits": exact_support_hits,
                    }
                )
        for case in support_priority_cases:
            for column in case_columns(case, ["priority_hits"]) & target_columns:
                support_priority_column_counts[column] += 1
        if cert_target_hits or form_priority_cases:
            status = "PRIORITY_PRESERVED_IN_EXPORTED_FORMS"
        elif support_priority_cases:
            status = "SUPPORT_PRIORITY_LOST_BEFORE_EXPORTED_FORMS"
        else:
            status = "NO_SUPPORT_PRIORITY_SIGNAL"
        status_counts[status] += 1
        if support_priority_cases or cert_group or form_group:
            group_reports.append(
                {
                    "certificate_count": len(cert_group),
                    "certificate_form_target_hits": cert_target_hits,
                    "certificates": cert_reports[:sample_limit],
                    "direct_verified_support_priority_case_count": len(direct_verified_support_priority_cases),
                    "exact_selected_losses": exact_losses[:sample_limit],
                    "form_priority_case_count": len(form_priority_cases),
                    "form_replay_case_count": len(form_group),
                    "form_replay_samples": [
                        compact_form_case(case, target_columns) for case in form_group[:sample_limit]
                    ],
                    "row_keys": list(key[2]),
                    "status": status,
                    "support_priority_case_count": len(support_priority_cases),
                    "support_priority_samples": [
                        compact_support_case(case, target_columns) for case in support_priority_cases[:sample_limit]
                    ],
                    "target": key[0],
                    "transfer_index": key[1],
                }
            )
    group_reports.sort(
        key=lambda report: (
            report.get("status") != "SUPPORT_PRIORITY_LOST_BEFORE_EXPORTED_FORMS",
            -int_value(report.get("direct_verified_support_priority_case_count")),
            -int_value(report.get("support_priority_case_count")),
            int_value(report.get("transfer_index")),
        )
    )
    support_loss_count = status_counts.get("SUPPORT_PRIORITY_LOST_BEFORE_EXPORTED_FORMS", 0)
    preserved_count = status_counts.get("PRIORITY_PRESERVED_IN_EXPORTED_FORMS", 0)
    if preserved_count:
        action = "PROMOTE_PRIORITY_FORM_EXPORTS_TO_RESIDUAL_SCOUT"
        rationale = "some priority support survives into exported forms"
    elif support_loss_count:
        action = "FORCE_PRIORITY_COLUMNS_IN_EXPORTED_RELATION_FORMS"
        rationale = "priority columns are visible in selected-term support but disappear before verified forms/certificates"
    else:
        action = "CHANGE_SOURCE_GENERATION_FOR_PRIORITY_VISIBILITY"
        rationale = "selected-term support does not expose the requested priority columns"
    return {
        "certificate_count": sum(1 for cert in certificates if int_value(cert.get("order")) == order),
        "exact_selected_loss_count": exact_selected_loss_count,
        "group_reports": group_reports[:40],
        "group_status_counts": dict(sorted(status_counts.items())),
        "support_priority_column_counts": {
            str(column): support_priority_column_counts[column] for column in sorted(target_columns)
        },
        "target_columns": sorted(target_columns),
        "work_order": {
            "action": action,
            "priority_columns": sorted(target_columns),
            "rationale": rationale,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--support-artifacts", required=True)
    parser.add_argument("--form-artifacts", required=True)
    parser.add_argument("--certificates", required=True)
    parser.add_argument("--target-columns", default=DEFAULT_TARGET_COLUMNS)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--sample-limit", type=int, default=6)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    support_paths = collapse.parse_paths(args.support_artifacts)
    form_paths = collapse.parse_paths(args.form_artifacts)
    cert_paths = collapse.parse_paths(args.certificates)
    target_columns = collapse.parse_target_columns(args.target_columns)
    if not support_paths:
        raise ValueError("no support artifacts supplied")
    if not form_paths:
        raise ValueError("no form artifacts supplied")
    if not cert_paths:
        raise ValueError("no certificates supplied")
    support_cases = load_case_reports(support_paths)
    form_cases = load_case_reports(form_paths)
    certificates = factor_bank.load_certificates(cert_paths)
    order_reports = {
        str(order): analyze_order(
            order,
            columns,
            support_cases,
            form_cases,
            certificates,
            max(0, int_value(args.sample_limit, 6)),
        )
        for order, columns in sorted(target_columns.items())
    }
    aggregate_status = Counter()
    for report in order_reports.values():
        aggregate_status.update(report.get("group_status_counts") or {})
    payload = {
        "artifacts": {
            "certificates": [str(path) for path in cert_paths],
            "form_artifacts": [str(path) for path in form_paths],
            "support_artifacts": [str(path) for path in support_paths],
        },
        "claim_status": (
            "PRIORITY_SUPPORT_REACHES_EXPORTED_FORMS"
            if aggregate_status.get("PRIORITY_PRESERVED_IN_EXPORTED_FORMS")
            else "NEGATIVE_RESULT_PRIORITY_SUPPORT_LOST_BEFORE_EXPORTED_FORMS"
            if aggregate_status.get("SUPPORT_PRIORITY_LOST_BEFORE_EXPORTED_FORMS")
            else "NEGATIVE_RESULT_NO_PRIORITY_SUPPORT_SIGNAL"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: selected-term support and exported forms are the current verifier namespace.",
            "HEURISTIC: support-to-form loss guides source/exporter design; it is not target descent or a deployed-curve speedup claim.",
        ],
        "order_reports": order_reports,
        "parameters": {
            "sample_limit": max(0, int_value(args.sample_limit, 6)),
            "target_columns": {str(order): sorted(cols) for order, cols in target_columns.items()},
        },
        "schema": "ecdlp.low_term_total2_support_to_form_loss_scout.v1",
        "summary": {
            "certificate_count": len(certificates),
            "form_case_count": len(form_cases),
            "order_count": len(order_reports),
            "status_counts": dict(sorted(aggregate_status.items())),
            "support_case_count": len(support_cases),
            "work_orders": {order: report.get("work_order") for order, report in order_reports.items()},
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
