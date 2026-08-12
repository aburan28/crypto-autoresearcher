#!/usr/bin/env python3
"""Scout q/pair options for certificates that export priority columns.

The support-to-form scheduler can identify an exported priority form, but a
certificate with only one compatible target-elimination pair may still collapse
into the current rowspace.  This scout scans candidate certificates for:

* which priority columns reach source forms;
* how many target-eliminated pair options touch those columns;
* whether any option leaves a quotient residual in the requested columns;
* whether the next experiment should add form-export partners or vary q/pair
  balance.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_factor_rank_gap_diagnostic as gap
import low_term_total2_residual_collapse_diagnostic as collapse
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_priority_export_pair_option_scout_probe.json"
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


def support(values: list[int], modulus: int) -> list[int]:
    return [idx for idx, value in enumerate(values) if value % modulus]


def pad(values: list[int], length: int) -> list[int]:
    return values + [0] * max(0, length - len(values))


def safe_coeff(values: list[int], index: int) -> int:
    if 0 <= index < len(values):
        return values[index]
    return 0


def ratio_mod(numerator: int, denominator: int, modulus: int) -> int | None:
    if denominator % modulus == 0:
        return None
    return (numerator * pow(denominator % modulus, -1, modulus)) % modulus


def support_key(values: set[int] | list[int]) -> str:
    items = sorted(values)
    return ",".join(str(item) for item in items) if items else "none"


def form_infos(cert: dict[str, Any], factor_count: int, target_columns: set[int]) -> list[dict[str, Any]]:
    order = int_value(cert.get("order"))
    forms = [form for form in (cert.get("forms") or []) if isinstance(form, dict)]
    infos = []
    for index, form in enumerate(forms):
        q_coeff, factor_coeffs, rhs = factor_bank.form_parts(form, order, factor_count)
        form_support = support(factor_coeffs, order)
        target_hits = sorted(set(form_support) & target_columns)
        infos.append(
            {
                "factor_coeffs": factor_coeffs,
                "factor_support": form_support,
                "index": index,
                "q_coeff": q_coeff,
                "rhs": rhs,
                "target_column_coeffs": {
                    str(column): safe_coeff(factor_coeffs, column) % order
                    for column in sorted(target_columns)
                },
                "target_hits": target_hits,
            }
        )
    return infos


def selected_info(cert: dict[str, Any]) -> dict[str, Any]:
    info = gap.selected_info(cert)
    return {
        "artifact": info.get("artifact"),
        "artifact_offset": int_value(info.get("artifact_offset")),
        "direct_ops_over_rho": info.get("direct_ops_over_rho"),
        "forms_count": int_value(info.get("forms_count")),
        "rank": int_value(info.get("rank")),
        "selector": info.get("selector"),
        "target": info.get("target"),
        "top_k": int_value(info.get("top_k")),
        "transfer_index": int_value(info.get("transfer_index")),
        "window": info.get("window"),
    }


def relation_pair_report(
    relation: dict[str, Any],
    forms: list[dict[str, Any]],
    residual: list[int],
    target_columns: set[int],
    order: int,
) -> dict[str, Any]:
    pair = [int_value(item) for item in relation.get("pair") or []]
    left = forms[pair[0]] if len(pair) == 2 and pair[0] < len(forms) else {}
    right = forms[pair[1]] if len(pair) == 2 and pair[1] < len(forms) else {}
    canonical = [int_value(value) % order for value in relation.get("canonical_coeffs") or []]
    raw_support = set(relation.get("factor_support") or [])
    residual_support = {idx for idx, value in enumerate(residual) if value % order}
    raw_target_hits = sorted(raw_support & target_columns)
    residual_target_hits = sorted(residual_support & target_columns)
    q_coeffs = [int_value(value) % order for value in relation.get("q_coeffs") or []]
    q_left = q_coeffs[0] if q_coeffs else 0
    q_right = q_coeffs[1] if len(q_coeffs) > 1 else 0
    return {
        "left_form": {
            "factor_support": left.get("factor_support") or [],
            "index": int_value(left.get("index")),
            "q_coeff": int_value(left.get("q_coeff")),
            "target_hits": left.get("target_hits") or [],
        },
        "normalized_residual": list(gap.normalize_vector(residual, order) or []),
        "pair": pair,
        "q_coeffs": [q_left, q_right],
        "q_ratio_right_over_left": ratio_mod(q_right, q_left, order),
        "raw_factor_support": sorted(raw_support),
        "raw_target_hits": raw_target_hits,
        "residual_support": sorted(residual_support),
        "residual_target_hits": residual_target_hits,
        "right_form": {
            "factor_support": right.get("factor_support") or [],
            "index": int_value(right.get("index")),
            "q_coeff": int_value(right.get("q_coeff")),
            "target_hits": right.get("target_hits") or [],
        },
    }


def analyze_order(
    order: int,
    base_certificates: list[dict[str, Any]],
    candidate_certificates: list[dict[str, Any]],
    target_columns: set[int],
    sample_limit: int,
) -> dict[str, Any]:
    all_order_certs = [
        cert for cert in base_certificates + candidate_certificates if int_value(cert.get("order")) == order
    ]
    factor_count = gap.factor_count_for_order(all_order_certs, order)
    base_rows = gap.unique_relation_rows(base_certificates, order, factor_count)
    basis, pivots = gap.rref_rows([row["coeffs"] for row in base_rows], order)
    status_counts: Counter[str] = Counter()
    work_order_counts: Counter[str] = Counter()
    column_export_counts: Counter[int] = Counter()
    q_ratio_counts: Counter[str] = Counter()
    pair_signature_counts: Counter[str] = Counter()
    candidate_reports = []
    target_residual_candidates = 0

    for cert in candidate_certificates:
        if int_value(cert.get("order")) != order:
            continue
        forms = form_infos(cert, factor_count, target_columns)
        exported_columns = sorted({column for form in forms for column in form.get("target_hits") or []})
        for column in exported_columns:
            column_export_counts[column] += 1
        if not exported_columns:
            continue
        info = selected_info(cert)
        relation_reports = []
        relation_status_counts: Counter[str] = Counter()
        partner_supports: set[str] = set()
        q_ratios: set[str] = set()
        priority_pair_count = 0
        target_residual_hit_count = 0
        raw_target_pair_count = 0
        collapsed_pair_count = 0
        for relation in factor_bank.target_eliminated_rows(cert):
            if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
                continue
            pair = [int_value(item) for item in relation.get("pair") or []]
            if len(pair) != 2 or pair[0] >= len(forms) or pair[1] >= len(forms):
                continue
            pair_form_target_hits = set(forms[pair[0]].get("target_hits") or []) | set(
                forms[pair[1]].get("target_hits") or []
            )
            canonical_coeffs = pad(
                [int_value(value) % order for value in relation.get("canonical_coeffs") or []],
                factor_count,
            )
            residual = gap.reduce_row(canonical_coeffs, basis, pivots, order)
            raw_support = {idx for idx, value in enumerate(canonical_coeffs) if value % order}
            raw_target_hits = target_columns & raw_support
            residual_support = {idx for idx, value in enumerate(residual) if value % order}
            residual_target_hits = target_columns & residual_support
            if not pair_form_target_hits and not raw_target_hits and not residual_target_hits:
                continue
            priority_pair_count += 1
            if raw_target_hits:
                raw_target_pair_count += 1
            status = collapse.row_status(raw_target_hits, residual_target_hits, residual_support)
            relation_status_counts[status] += 1
            status_counts[status] += 1
            if status == "TARGET_SUPPORT_COLLAPSED_TO_BASE_ROWSPACE":
                collapsed_pair_count += 1
            if residual_target_hits:
                target_residual_hit_count += 1
                target_residual_candidates += 1
            q_coeffs = [int_value(value) % order for value in relation.get("q_coeffs") or []]
            q_ratio = ratio_mod(q_coeffs[1] if len(q_coeffs) > 1 else 0, q_coeffs[0] if q_coeffs else 0, order)
            q_ratio_key = str(q_ratio)
            q_ratios.add(q_ratio_key)
            q_ratio_counts[f"{status}|ratio={q_ratio_key}"] += 1
            left_support = set(forms[pair[0]].get("factor_support") or [])
            right_support = set(forms[pair[1]].get("factor_support") or [])
            partner_supports.add(support_key((left_support | right_support) - set(exported_columns)))
            signature = (
                f"{status}|left={support_key(left_support)}|right={support_key(right_support)}|"
                f"raw={support_key(raw_support)}|target={support_key(raw_target_hits)}"
            )
            pair_signature_counts[signature] += 1
            if len(relation_reports) < sample_limit:
                relation_reports.append(
                    {
                        "pair_report": relation_pair_report(relation, forms, residual, target_columns, order),
                        "status": status,
                    }
                )
        if target_residual_hit_count:
            action = "PROMOTE_TARGET_RESIDUAL_ROWS"
            priority = 0
        elif collapsed_pair_count and len(q_ratios) > 1:
            action = "SEARCH_Q_PAIR_COEFFICIENT_BALANCE"
            priority = 1
        elif collapsed_pair_count:
            action = "GENERATE_MORE_PRIORITY_FORM_PARTNERS"
            priority = 2
        elif priority_pair_count:
            action = "EXPAND_PRIORITY_PAIR_OPTIONS"
            priority = 3
        else:
            action = "EXPORT_PRIORITY_FORMS_WITH_PAIRABLE_PARTNERS"
            priority = 4
        work_order_counts[action] += 1
        candidate_reports.append(
            {
                "candidate": info,
                "exported_priority_columns": exported_columns,
                "forms": [
                    {
                        "factor_support": form.get("factor_support") or [],
                        "index": form.get("index"),
                        "q_coeff": form.get("q_coeff"),
                        "target_column_coeffs": form.get("target_column_coeffs") or {},
                        "target_hits": form.get("target_hits") or [],
                    }
                    for form in forms
                ],
                "partner_support_diversity": sorted(partner_supports),
                "priority": priority,
                "priority_pair_count": priority_pair_count,
                "q_ratio_diversity": sorted(q_ratios),
                "raw_target_pair_count": raw_target_pair_count,
                "relation_status_counts": dict(sorted(relation_status_counts.items())),
                "sample_relations": relation_reports,
                "target_residual_hit_count": target_residual_hit_count,
                "work_order": {
                    "action": action,
                    "rationale": {
                        "PROMOTE_TARGET_RESIDUAL_ROWS": "at least one priority pair leaves target residual support",
                        "SEARCH_Q_PAIR_COEFFICIENT_BALANCE": "multiple q ratios exist but priority target support collapses",
                        "GENERATE_MORE_PRIORITY_FORM_PARTNERS": "priority target support collapses and the certificate has too little q/pair diversity",
                        "EXPAND_PRIORITY_PAIR_OPTIONS": "priority forms exist but current pairs do not create target residuals",
                        "EXPORT_PRIORITY_FORMS_WITH_PAIRABLE_PARTNERS": "priority columns reach forms but no pairable target-eliminated option was found",
                    }[action],
                },
            }
        )
    candidate_reports.sort(
        key=lambda report: (
            int_value(report.get("priority"), 9),
            -int_value(report.get("target_residual_hit_count")),
            -int_value(report.get("priority_pair_count")),
            -len(report.get("q_ratio_diversity") or []),
            int_value((report.get("candidate") or {}).get("transfer_index")),
        )
    )
    if target_residual_candidates:
        action = "PROMOTE_TARGET_RESIDUAL_ROWS"
    elif work_order_counts.get("SEARCH_Q_PAIR_COEFFICIENT_BALANCE"):
        action = "SEARCH_Q_PAIR_COEFFICIENT_BALANCE"
    elif work_order_counts.get("GENERATE_MORE_PRIORITY_FORM_PARTNERS"):
        action = "GENERATE_MORE_PRIORITY_FORM_PARTNERS"
    elif candidate_reports:
        action = "EXPORT_PRIORITY_FORMS_WITH_PAIRABLE_PARTNERS"
    else:
        action = "FORCE_PRIORITY_COLUMNS_IN_EXPORTED_RELATION_FORMS"
    return {
        "base_factor_relation_count": len(base_rows),
        "base_rank": len(pivots),
        "candidate_reports": candidate_reports[:50],
        "candidate_with_priority_export_count": len(candidate_reports),
        "factor_variable_count": factor_count,
        "pair_signature_counts": dict(
            sorted(pair_signature_counts.items(), key=lambda item: (-item[1], item[0]))[:40]
        ),
        "q_ratio_counts": dict(sorted(q_ratio_counts.items(), key=lambda item: (-item[1], item[0]))[:40]),
        "status_counts": dict(sorted(status_counts.items())),
        "target_column_export_counts": {str(column): column_export_counts[column] for column in sorted(target_columns)},
        "target_columns": sorted(target_columns),
        "work_order": {
            "action": action,
            "rationale": {
                "PROMOTE_TARGET_RESIDUAL_ROWS": "a priority export pair already creates target residual support",
                "SEARCH_Q_PAIR_COEFFICIENT_BALANCE": "priority forms have pair diversity but target support collapses",
                "GENERATE_MORE_PRIORITY_FORM_PARTNERS": "priority forms exist but need more partner/q-ratio diversity",
                "EXPORT_PRIORITY_FORMS_WITH_PAIRABLE_PARTNERS": "priority exports exist but are not yet pairable into useful residuals",
                "FORCE_PRIORITY_COLUMNS_IN_EXPORTED_RELATION_FORMS": "no priority columns reached exported forms",
            }[action],
        },
        "work_order_counts": dict(sorted(work_order_counts.items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-certificates", required=True)
    parser.add_argument("--candidate-certificates", required=True)
    parser.add_argument("--target-columns", default=DEFAULT_TARGET_COLUMNS)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--sample-limit", type=int, default=8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_paths = collapse.parse_paths(args.base_certificates)
    candidate_paths = collapse.parse_paths(args.candidate_certificates)
    target_columns = collapse.parse_target_columns(args.target_columns)
    if not base_paths:
        raise ValueError("no base certificates supplied")
    if not candidate_paths:
        raise ValueError("no candidate certificates supplied")
    base_certificates = factor_bank.load_certificates(base_paths)
    candidate_certificates = factor_bank.load_certificates(candidate_paths)
    order_reports = {
        str(order): analyze_order(
            order,
            base_certificates,
            candidate_certificates,
            columns,
            max(0, int_value(args.sample_limit, 8)),
        )
        for order, columns in sorted(target_columns.items())
    }
    aggregate_status = Counter()
    aggregate_work = Counter()
    for report in order_reports.values():
        aggregate_status.update(report.get("status_counts") or {})
        aggregate_work.update(report.get("work_order_counts") or {})
    if aggregate_status.get("TARGET_RESIDUAL_HIT"):
        claim_status = "PRIORITY_EXPORT_TARGET_RESIDUAL_FOUND"
    elif aggregate_status.get("TARGET_SUPPORT_COLLAPSED_TO_BASE_ROWSPACE"):
        claim_status = "NEGATIVE_RESULT_PRIORITY_EXPORT_COLLAPSES_IN_ROWSPACE"
    elif aggregate_work:
        claim_status = "PRIORITY_EXPORT_PAIR_OPTIONS_IDENTIFIED"
    else:
        claim_status = "NEGATIVE_RESULT_NO_PRIORITY_EXPORT_PAIR_OPTIONS"
    payload = {
        "artifacts": {
            "base_certificates": [str(path) for path in base_paths],
            "candidate_certificates": [str(path) for path in candidate_paths],
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: pair options are computed in the current verifier factor-column namespace.",
            "NO SPEEDUP CLAIM: pair-option diversity is a generator work order, not target descent.",
        ],
        "order_reports": order_reports,
        "parameters": {
            "sample_limit": max(0, int_value(args.sample_limit, 8)),
            "target_columns": {str(order): sorted(cols) for order, cols in target_columns.items()},
        },
        "schema": "ecdlp.low_term_total2_priority_export_pair_option_scout.v1",
        "summary": {
            "candidate_certificate_count": len(candidate_certificates),
            "order_count": len(order_reports),
            "status_counts": dict(sorted(aggregate_status.items())),
            "work_order_counts": dict(sorted(aggregate_work.items())),
            "work_orders": {order: report.get("work_order") for order, report in order_reports.items()},
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
