#!/usr/bin/env python3
"""Trace how target-eliminated factor rows are assembled from certificate forms.

The residual-collapse diagnostic reports whether a candidate row has target
columns before and after reduction by the current base rowspace.  This scout
adds assembly provenance: for each pair of source forms it records q
coefficients, q-elimination multipliers, form supports, assembled support, and
the quotient residual.  The goal is to distinguish three next actions:

* change source generation when target columns never appear in source forms;
* change pair/q-coefficient balance when source visibility is lost in assembly;
* change quotient direction or promote rows when assembled target support
  survives into a residual class.
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
DEFAULT_OUT = STATE_DIR / "low_term_total2_residual_assembly_balance_scout_probe.json"
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


def pad(values: list[int], length: int) -> list[int]:
    return values + [0] * max(0, length - len(values))


def support(values: list[int], modulus: int) -> list[int]:
    return [idx for idx, value in enumerate(values) if value % modulus]


def safe_coeff(values: list[int], index: int) -> int:
    if 0 <= index < len(values):
        return values[index]
    return 0


def support_key(items: set[int] | list[int]) -> str:
    values = sorted(items)
    return ",".join(str(value) for value in values) if values else "none"


def ratio_mod(numerator: int, denominator: int, modulus: int) -> int | None:
    if denominator % modulus == 0:
        return None
    return (numerator * pow(denominator % modulus, -1, modulus)) % modulus


def form_infos(cert: dict[str, Any], factor_count: int) -> list[dict[str, Any]]:
    order = int_value(cert.get("order"))
    forms = [form for form in (cert.get("forms") or []) if isinstance(form, dict)]
    infos: list[dict[str, Any]] = []
    for index, form in enumerate(forms):
        q_coeff, factor_coeffs, rhs = factor_bank.form_parts(form, order, factor_count)
        infos.append(
            {
                "factor_coeffs": factor_coeffs,
                "factor_support": support(factor_coeffs, order),
                "index": index,
                "q_coeff": q_coeff,
                "rhs": rhs,
            }
        )
    return infos


def compact_form(info: dict[str, Any], target_columns: set[int]) -> dict[str, Any]:
    coeffs = info.get("factor_coeffs") or []
    return {
        "factor_support": info.get("factor_support") or [],
        "index": int_value(info.get("index")),
        "q_coeff": int_value(info.get("q_coeff")),
        "rhs": int_value(info.get("rhs")),
        "target_coeffs": {
            str(column): safe_coeff(coeffs, column)
            for column in sorted(target_columns)
        },
        "target_support": [
            column for column in sorted(target_columns) if safe_coeff(coeffs, column)
        ],
    }


def target_column_details(
    left: dict[str, Any],
    right: dict[str, Any],
    canonical_coeffs: list[int],
    assembled_coeffs: list[int],
    residual: list[int],
    target_columns: set[int],
    order: int,
) -> dict[str, dict[str, Any]]:
    details: dict[str, dict[str, Any]] = {}
    left_coeffs = left.get("factor_coeffs") or []
    right_coeffs = right.get("factor_coeffs") or []
    for column in sorted(target_columns):
        left_coeff = safe_coeff(left_coeffs, column) % order
        right_coeff = safe_coeff(right_coeffs, column) % order
        assembled_coeff = safe_coeff(assembled_coeffs, column) % order
        canonical_coeff = safe_coeff(canonical_coeffs, column) % order
        residual_coeff = safe_coeff(residual, column) % order
        details[str(column)] = {
            "assembly_cancelled": bool((left_coeff or right_coeff) and not assembled_coeff),
            "assembled_coeff": assembled_coeff,
            "canonical_coeff": canonical_coeff,
            "left_coeff": left_coeff,
            "residual_coeff": residual_coeff,
            "right_coeff": right_coeff,
            "rowspace_cancelled": bool(assembled_coeff and not residual_coeff),
        }
    return details


def update_target_effect_counts(
    counts_by_column: dict[int, Counter[str]],
    details: dict[str, dict[str, Any]],
) -> None:
    for raw_column, detail in details.items():
        column = int(raw_column)
        left = bool(detail.get("left_coeff"))
        right = bool(detail.get("right_coeff"))
        assembled = bool(detail.get("assembled_coeff"))
        residual = bool(detail.get("residual_coeff"))
        if left:
            counts_by_column[column]["left_form_visible"] += 1
        if right:
            counts_by_column[column]["right_form_visible"] += 1
        if left or right:
            counts_by_column[column]["source_form_visible"] += 1
        if left and right:
            counts_by_column[column]["both_forms_visible"] += 1
        if detail.get("assembly_cancelled"):
            counts_by_column[column]["assembly_cancelled"] += 1
        if assembled:
            counts_by_column[column]["assembled_nonzero"] += 1
        if residual:
            counts_by_column[column]["residual_nonzero"] += 1
        if detail.get("rowspace_cancelled"):
            counts_by_column[column]["rowspace_cancelled"] += 1


def sample_record(
    cert_info: dict[str, Any],
    pair: list[int],
    q_coeffs: list[int],
    left: dict[str, Any],
    right: dict[str, Any],
    assembled_coeffs: list[int],
    canonical_coeffs: list[int],
    residual: list[int],
    status: str,
    target_columns: set[int],
    order: int,
) -> dict[str, Any]:
    raw_support = set(support(assembled_coeffs, order))
    canonical_support = set(support(canonical_coeffs, order))
    residual_support = set(support(residual, order))
    raw_target_hits = raw_support & target_columns
    residual_target_hits = residual_support & target_columns
    normalized = gap.normalize_vector(residual, order)
    q_left = q_coeffs[0] if q_coeffs else 0
    q_right = q_coeffs[1] if len(q_coeffs) > 1 else 0
    return {
        "candidate": cert_info,
        "canonical_factor_support": sorted(canonical_support),
        "left_form": compact_form(left, target_columns),
        "normalized_residual": list(normalized) if normalized is not None else None,
        "pair": pair,
        "q_coeffs": [q_left, q_right],
        "q_elimination_multipliers": {
            "left": q_right % order,
            "right": (-q_left) % order,
        },
        "q_ratio_right_over_left": ratio_mod(q_right, q_left, order),
        "raw_assembled_factor_support": sorted(raw_support),
        "raw_target_hits": sorted(raw_target_hits),
        "residual_support": sorted(residual_support),
        "residual_target_hits": sorted(residual_target_hits),
        "right_form": compact_form(right, target_columns),
        "status": status,
        "target_column_details": target_column_details(
            left,
            right,
            canonical_coeffs,
            assembled_coeffs,
            residual,
            target_columns,
            order,
        ),
    }


def analyze_order(
    order: int,
    base_certificates: list[dict[str, Any]],
    candidate_certificates: list[dict[str, Any]],
    target_columns: set[int],
    sample_limit: int,
    signature_limit: int,
) -> dict[str, Any]:
    all_order_certs = [
        cert for cert in base_certificates + candidate_certificates if int_value(cert.get("order")) == order
    ]
    factor_count = gap.factor_count_for_order(all_order_certs, order)
    base_rows = gap.unique_relation_rows(base_certificates, order, factor_count)
    basis, pivots = gap.rref_rows([row["coeffs"] for row in base_rows], order)
    free_columns = [idx for idx in range(factor_count) if idx not in set(pivots)]
    status_counts: Counter[str] = Counter()
    relation_status_counts: Counter[str] = Counter()
    assembly_signature_counts: Counter[str] = Counter()
    q_signature_counts: Counter[str] = Counter()
    selector_status_counts: Counter[str] = Counter()
    target_effect_counts: dict[int, Counter[str]] = {
        column: Counter() for column in sorted(target_columns)
    }
    samples_by_status: dict[str, list[dict[str, Any]]] = defaultdict(list)
    candidate_reports = []
    source_form_visible_relation_count = 0
    raw_assembled_target_relation_count = 0
    residual_target_relation_count = 0
    assembly_cancelled_relation_count = 0

    for cert in candidate_certificates:
        if int_value(cert.get("order")) != order:
            continue
        cert_info = gap.selected_info(cert)
        forms = form_infos(cert, factor_count)
        cert_status_counts: Counter[str] = Counter()
        cert_relation_status_counts: Counter[str] = Counter()
        cert_target_effect_counts: dict[int, Counter[str]] = {
            column: Counter() for column in sorted(target_columns)
        }
        cert_samples = []
        selector_key = (
            f"{cert_info.get('selector')}|top{cert_info.get('top_k')}|"
            f"{cert_info.get('clause')}"
        )
        for relation in factor_bank.target_eliminated_rows(cert):
            relation_status = str(relation.get("relation_status") or "UNKNOWN")
            relation_status_counts[relation_status] += 1
            cert_relation_status_counts[relation_status] += 1
            if relation_status != "TARGET_ELIMINATED_FACTOR_RELATION":
                continue
            pair = [int_value(value) for value in relation.get("pair") or []]
            if len(pair) != 2 or pair[0] >= len(forms) or pair[1] >= len(forms):
                continue
            left = forms[pair[0]]
            right = forms[pair[1]]
            q_coeffs = [int_value(value) % order for value in relation.get("q_coeffs") or []]
            q_left = q_coeffs[0] if q_coeffs else 0
            q_right = q_coeffs[1] if len(q_coeffs) > 1 else 0
            left_coeffs = left.get("factor_coeffs") or []
            right_coeffs = right.get("factor_coeffs") or []
            assembled_coeffs = [
                (q_right * safe_coeff(left_coeffs, idx) - q_left * safe_coeff(right_coeffs, idx)) % order
                for idx in range(factor_count)
            ]
            canonical_coeffs = pad(
                [int_value(value) % order for value in relation.get("canonical_coeffs") or []],
                factor_count,
            )
            residual = gap.reduce_row(canonical_coeffs, basis, pivots, order)
            raw_support = set(support(assembled_coeffs, order))
            residual_support = set(support(residual, order))
            raw_target_hits = raw_support & target_columns
            residual_target_hits = residual_support & target_columns
            form_target_hits = (
                set(left.get("factor_support") or []) | set(right.get("factor_support") or [])
            ) & target_columns
            status = collapse.row_status(raw_target_hits, residual_target_hits, residual_support)
            status_counts[status] += 1
            cert_status_counts[status] += 1
            selector_status_counts[f"{status}|{selector_key}"] += 1
            if form_target_hits:
                source_form_visible_relation_count += 1
            if raw_target_hits:
                raw_assembled_target_relation_count += 1
            if residual_target_hits:
                residual_target_relation_count += 1
            details = target_column_details(
                left,
                right,
                canonical_coeffs,
                assembled_coeffs,
                residual,
                target_columns,
                order,
            )
            if any(detail.get("assembly_cancelled") for detail in details.values()):
                assembly_cancelled_relation_count += 1
            update_target_effect_counts(target_effect_counts, details)
            update_target_effect_counts(cert_target_effect_counts, details)
            left_support = set(left.get("factor_support") or [])
            right_support = set(right.get("factor_support") or [])
            assembly_signature = (
                f"{status}|left={support_key(left_support)}|right={support_key(right_support)}|"
                f"assembled={support_key(raw_support)}|raw_target={support_key(raw_target_hits)}|"
                f"residual_target={support_key(residual_target_hits)}"
            )
            assembly_signature_counts[assembly_signature] += 1
            q_signature = (
                f"{status}|q_left={q_left}|q_right={q_right}|"
                f"ratio={ratio_mod(q_right, q_left, order)}"
            )
            q_signature_counts[q_signature] += 1
            if len(samples_by_status[status]) < sample_limit:
                record = sample_record(
                    cert_info,
                    pair,
                    [q_left, q_right],
                    left,
                    right,
                    assembled_coeffs,
                    canonical_coeffs,
                    residual,
                    status,
                    target_columns,
                    order,
                )
                samples_by_status[status].append(record)
                if len(cert_samples) < 4:
                    cert_samples.append(record)
        candidate_reports.append(
            {
                "candidate": cert_info,
                "relation_status_counts": dict(sorted(cert_relation_status_counts.items())),
                "sample_pairs": cert_samples,
                "status_counts": dict(sorted(cert_status_counts.items())),
                "target_effect_counts": {
                    str(column): dict(sorted(counts.items()))
                    for column, counts in cert_target_effect_counts.items()
                },
            }
        )

    candidate_reports.sort(
        key=lambda item: (
            -sum(
                count
                for status, count in (item.get("status_counts") or {}).items()
                if status.startswith("TARGET_")
            ),
            str((item.get("candidate") or {}).get("artifact")),
            int_value((item.get("candidate") or {}).get("artifact_offset")),
        )
    )
    if residual_target_relation_count:
        action = "PROMOTE_TARGET_RESIDUAL_ROWS"
        rationale = "assembled target support survives base-rowspace reduction for at least one row"
    elif raw_assembled_target_relation_count:
        action = "CHANGE_Q_COEFFICIENT_BALANCE_OR_PAIR_SELECTION"
        rationale = "target columns are assembled into factor rows but collapse under the current base rowspace"
    elif source_form_visible_relation_count:
        action = "CHANGE_Q_COEFFICIENT_BALANCE_OR_PAIR_SELECTION"
        rationale = "target columns are visible in source forms but eliminated or cancelled before quotient residuals"
    else:
        action = "CHANGE_SOURCE_GENERATION_FOR_TARGET_VISIBILITY"
        rationale = "target columns do not appear in the paired source forms"
    return {
        "assembly_cancelled_relation_count": assembly_cancelled_relation_count,
        "assembly_signature_counts": dict(
            sorted(assembly_signature_counts.items(), key=lambda item: (-item[1], item[0]))[:signature_limit]
        ),
        "base_factor_relation_count": len(base_rows),
        "base_rank": len(pivots),
        "candidate_certificate_count": sum(
            1 for cert in candidate_certificates if int_value(cert.get("order")) == order
        ),
        "candidate_reports": candidate_reports[:30],
        "factor_variable_count": factor_count,
        "free_columns": free_columns,
        "pivot_columns": pivots,
        "q_signature_counts": dict(
            sorted(q_signature_counts.items(), key=lambda item: (-item[1], item[0]))[:signature_limit]
        ),
        "raw_assembled_target_relation_count": raw_assembled_target_relation_count,
        "relation_status_counts": dict(sorted(relation_status_counts.items())),
        "residual_target_relation_count": residual_target_relation_count,
        "samples_by_status": {
            status: samples for status, samples in sorted(samples_by_status.items())
        },
        "selector_status_counts": dict(
            sorted(selector_status_counts.items(), key=lambda item: (-item[1], item[0]))[:signature_limit]
        ),
        "source_form_visible_relation_count": source_form_visible_relation_count,
        "status_counts": dict(sorted(status_counts.items())),
        "target_columns": sorted(target_columns),
        "target_effect_counts": {
            str(column): dict(sorted(counts.items()))
            for column, counts in target_effect_counts.items()
        },
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
    parser.add_argument("--sample-limit", type=int, default=8)
    parser.add_argument("--signature-limit", type=int, default=30)
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
            max(0, int_value(args.sample_limit)),
            max(1, int_value(args.signature_limit, 30)),
        )
        for order, columns in sorted(target_columns.items())
    }
    aggregate_status = Counter()
    aggregate_relation_status = Counter()
    work_orders = {}
    for order, report in order_reports.items():
        aggregate_status.update(report.get("status_counts") or {})
        aggregate_relation_status.update(report.get("relation_status_counts") or {})
        work_orders[order] = report.get("work_order")
    if aggregate_status.get("TARGET_RESIDUAL_HIT"):
        claim_status = "TARGET_RESIDUAL_ROWS_FOUND"
    elif aggregate_status.get("TARGET_SUPPORT_COLLAPSED_TO_BASE_ROWSPACE") or aggregate_status.get(
        "TARGET_SUPPORT_RESIDUAL_MOVED_TO_OTHER_COLUMNS"
    ):
        claim_status = "NEGATIVE_RESULT_TARGET_ASSEMBLY_COLLAPSES_IN_BASE_ROWSPACE"
    elif sum(
        int_value(report.get("source_form_visible_relation_count")) for report in order_reports.values()
    ):
        claim_status = "NEGATIVE_RESULT_SOURCE_VISIBILITY_LOST_DURING_ASSEMBLY"
    else:
        claim_status = "NEGATIVE_RESULT_TARGET_COLUMNS_NOT_VISIBLE_IN_SOURCE_FORMS"
    payload = {
        "artifacts": {
            "base_certificates": [str(path) for path in base_paths],
            "candidate_certificates": [str(path) for path in candidate_paths],
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: assembly rows are reduced in the verifier's current factor-column namespace.",
            "HEURISTIC: q-balance signatures guide future collector design; they are not target descent or a deployed-curve speedup claim.",
        ],
        "order_reports": order_reports,
        "parameters": {
            "sample_limit": max(0, int_value(args.sample_limit)),
            "signature_limit": max(1, int_value(args.signature_limit, 30)),
            "target_columns": {str(order): sorted(cols) for order, cols in target_columns.items()},
        },
        "schema": "ecdlp.low_term_total2_residual_assembly_balance_scout.v1",
        "summary": {
            "base_certificate_count": len(base_certificates),
            "candidate_certificate_count": len(candidate_certificates),
            "order_count": len(order_reports),
            "relation_status_counts": dict(sorted(aggregate_relation_status.items())),
            "status_counts": dict(sorted(aggregate_status.items())),
            "work_orders": work_orders,
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
