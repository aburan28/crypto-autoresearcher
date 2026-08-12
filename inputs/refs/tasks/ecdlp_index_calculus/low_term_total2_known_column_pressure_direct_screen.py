#!/usr/bin/env python3
"""Screen low-term source cases for known-column individual-log descent.

This probe is the next step after the support10 scheduled miss.  It uses only
public selected-leaf support to choose source cases, then runs the direct
relation scan and tests whether any single relation form:

  * has nonzero target coefficient;
  * has factor support fully inside known factor columns;
  * derives a candidate scalar from the training-bank factor logs; and
  * verifies that scalar against the public key.

The final public-key check is post-relation evidence.  It is intentionally
separated from the public selection gate and does not use the source row's
precomputed public_key_verified label.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
from frontier_signed_eval_cover_dependency_circuit_probe import public_secret_matches
from low_term_total2_known_factor_holdout_descent_probe import known_factors


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


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


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def parse_int_set(raw: str) -> set[int]:
    return {int(item.strip()) for item in raw.split(",") if item.strip()}


def source_cases(source: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for policy_name, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        for row in result.get("stress_leaf_results") or []:
            if not isinstance(row, dict):
                continue
            cases.append(
                {
                    **row,
                    "source_policy": policy_name,
                    "row_selector": row.get("row_selector") or row_selector,
                }
            )
    return cases


def report_key(report: dict[str, Any]) -> tuple[str, int, str, int, tuple[str, ...]]:
    return (
        str(report.get("target")),
        int_value(report.get("transfer_index")),
        str(report.get("selector")),
        int_value(report.get("top_k")),
        tuple(sorted(str(row) for row in report.get("row_keys") or [])),
    )


def source_case_key(case: dict[str, Any]) -> tuple[str, int, str, int, tuple[str, ...]]:
    return (
        str(case.get("target")),
        int_value(case.get("transfer_index")),
        str(case.get("selector")),
        int_value(case.get("top_k")),
        tuple(sorted(str(row) for row in case.get("row_keys") or [])),
    )


def find_exact_source_case(source_index: dict[tuple[str, int, str, int, tuple[str, ...]], list[dict[str, Any]]], report: dict[str, Any]) -> dict[str, Any]:
    matches = source_index.get(report_key(report), [])
    if not matches:
        raise ValueError(f"no exact source case for scout report {report_key(report)!r}")
    return sorted(matches, key=lambda item: str(item.get("source_policy")))[0]


def public_support_metrics(
    support: set[int],
    known_columns: set[int],
    priority_columns: set[int],
    forbid_columns: set[int],
) -> dict[str, Any]:
    known_overlap = sorted(support & known_columns)
    priority_overlap = sorted(support & priority_columns)
    forbidden_overlap = sorted(support & forbid_columns)
    unknown = sorted(support - known_columns)
    score = 2 * len(known_overlap) + len(priority_overlap) - len(unknown) - 3 * len(forbidden_overlap)
    return {
        "forbidden_overlap": forbidden_overlap,
        "known_overlap": known_overlap,
        "known_overlap_count": len(known_overlap),
        "priority_overlap": priority_overlap,
        "pressure_score": score,
        "selected_support_size": len(support),
        "unknown_selected_support": unknown,
        "unknown_selected_support_count": len(unknown),
    }


def select_reports(
    support: dict[str, Any],
    target: str,
    selector: str,
    known_columns: set[int],
    priority_columns: set[int],
    forbid_columns: set[int],
    min_known_overlap: int,
    max_support_size: int,
    min_pressure_score: int,
    max_cases: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str, int, tuple[str, ...]]] = set()
    for report in support.get("case_reports") or []:
        if not isinstance(report, dict):
            continue
        if target and str(report.get("target")) != target:
            continue
        if selector and str(report.get("selector")) != selector:
            continue
        key = report_key(report)
        if key in seen:
            continue
        seen.add(key)
        selected_support = {int_value(value) for value in report.get("selected_term_support") or []}
        metrics = public_support_metrics(selected_support, known_columns, priority_columns, forbid_columns)
        if len(selected_support) > max_support_size:
            continue
        if metrics["known_overlap_count"] < min_known_overlap:
            continue
        if metrics["forbidden_overlap"]:
            continue
        if int_value(metrics["pressure_score"]) < min_pressure_score:
            continue
        rows.append(
            {
                **report,
                "public_selection_metrics": metrics,
                "selected_term_support": sorted(selected_support),
            }
        )
    rows.sort(
        key=lambda item: (
            -int_value(item["public_selection_metrics"].get("pressure_score")),
            -int_value(item["public_selection_metrics"].get("known_overlap_count")),
            int_value(item["public_selection_metrics"].get("selected_support_size")),
            int_value(item.get("transfer_index")),
            int_value(item.get("top_k")),
            tuple(str(row) for row in item.get("row_keys") or []),
        )
    )
    return rows[:max_cases] if max_cases > 0 else rows


def direct_unique_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    for row in rows:
        scan = row.get("_scan") if isinstance(row.get("_scan"), dict) else {}
        for event in scan.get("relation_events") or []:
            coeffs, rhs, _terms = event["form"]
            key = (tuple(int(coeff) for coeff in coeffs), int(rhs))
            if key in seen:
                continue
            seen.add(key)
            events.append(event)
    return events


def attempt_known_factor_form(
    verifier: Any,
    built: dict[str, Any],
    event: dict[str, Any],
    known: dict[int, int],
) -> dict[str, Any]:
    order = int_value(built.get("order"))
    p = int_value(built.get("p"))
    coeffs_raw, rhs_raw, terms_raw = event["form"]
    coeffs = [int_value(value) % order for value in coeffs_raw]
    rhs = int_value(rhs_raw) % order
    terms = [int_value(term) for term in terms_raw]
    if not coeffs:
        return {"recoverable": False, "reason": "empty_coefficients", "terms": terms}
    target_coeff = coeffs[0] % order
    factor_coeffs = coeffs[1:]
    support = [idx for idx, coeff in enumerate(factor_coeffs) if coeff % order]
    if target_coeff == 0:
        return {
            "recoverable": False,
            "reason": "zero_target_coefficient",
            "support": support,
            "terms": terms,
        }
    if not support:
        return {
            "recoverable": False,
            "reason": "empty_factor_support",
            "support": support,
            "target_coefficient": target_coeff,
            "terms": terms,
        }
    unknown = [idx for idx in support if idx not in known]
    if unknown:
        return {
            "known_support": [idx for idx in support if idx in known],
            "recoverable": False,
            "reason": "unknown_factor_support",
            "support": support,
            "target_coefficient": target_coeff,
            "terms": terms,
            "unknown_factor_support": unknown,
        }
    factor_sum = sum((factor_coeffs[idx] * known[idx]) for idx in support) % order
    derived = ((rhs - factor_sum) * pow(target_coeff, -1, order)) % order
    verified = public_secret_matches(
        verifier,
        derived,
        built["base"],
        built["public"],
        built["ainvs"],
        p,
        order,
    )
    return {
        "derived_secret": derived,
        "factor_sum": factor_sum,
        "known_support": support,
        "public_key_verified": verified,
        "recoverable": True,
        "rhs": rhs,
        "support": support,
        "target_coefficient": target_coeff,
        "terms": terms,
    }


def scan_case(
    source: dict[str, Any],
    source_index: dict[tuple[str, int, str, int, tuple[str, ...]], list[dict[str, Any]]],
    report: dict[str, Any],
    known_by_order: dict[int, dict[int, int]],
) -> dict[str, Any]:
    source_case = find_exact_source_case(source_index, report)
    verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(
        source,
        source_case,
    )
    direct_rows, direct_ops, rho, _row_profiles = timing_probe.direct_witness_rows(verifier, contexts)
    if not contexts:
        raise ValueError(f"no contexts for {report_key(report)!r}")
    built = contexts[0]["built"]
    order = int_value(built.get("order"))
    known = known_by_order.get(order, {})
    attempts = []
    for form_index, event in enumerate(direct_unique_events(direct_rows)):
        attempt = attempt_known_factor_form(verifier, built, event, known)
        attempt["form_index"] = form_index
        attempts.append(attempt)
    verified_attempts = [attempt for attempt in attempts if attempt.get("public_key_verified")]
    recoverable_attempts = [attempt for attempt in attempts if attempt.get("recoverable")]
    known_support_attempts = [
        attempt
        for attempt in attempts
        if attempt.get("recoverable") and not attempt.get("unknown_factor_support")
    ]
    return {
        "attempts": attempts,
        "direct_ops": direct_ops,
        "direct_ops_over_rho": ratio(direct_ops, rho),
        "known_support_form_count": len(known_support_attempts),
        "order": order,
        "public_known_factor_verified": bool(verified_attempts),
        "recoverable_form_count": len(recoverable_attempts),
        "rho": rho,
        "scanned_form_count": len(attempts),
        "selected": {
            "row_keys": report.get("row_keys") or [],
            "selector": report.get("selector"),
            "target": report.get("target"),
            "top_k": int_value(report.get("top_k")),
            "transfer_index": int_value(report.get("transfer_index")),
        },
        "selected_term_support": report.get("selected_term_support") or [],
        "verified_attempts": verified_attempts,
    }


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None, "sum": 0.0}
    return {
        "count": len(values),
        "max": round(max(values), 8),
        "mean": round(mean(values), 8),
        "min": round(min(values), 8),
        "sum": round(sum(values), 8),
    }


def first_hit_stop_rule(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    cost = 0.0
    scanned = 0
    for case in case_results:
        scanned += 1
        if case.get("direct_ops_over_rho") is not None:
            cost += float(case["direct_ops_over_rho"])
        if case.get("public_known_factor_verified"):
            return {
                "cost_over_rho": round(cost, 8),
                "hit": True,
                "recovered_window_count": 1,
                "scanned_case_count": scanned,
            }
    return {
        "cost_over_rho": round(cost, 8),
        "hit": False,
        "recovered_window_count": 0,
        "scanned_case_count": scanned,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--support", required=True)
    parser.add_argument("--training-audit", required=True)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--priority-columns", default="15")
    parser.add_argument("--forbid-selected-columns", default="2,3")
    parser.add_argument("--min-known-overlap", type=int, default=4)
    parser.add_argument("--max-selected-support-size", type=int, default=10)
    parser.add_argument("--min-pressure-score", type=int, default=2)
    parser.add_argument("--max-cases", type=int, default=24)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = Path(args.source)
    support_path = Path(args.support)
    training_path = Path(args.training_audit)
    source = load_json(source_path)
    support = load_json(support_path)
    training_audit = load_json(training_path)
    known_by_order = known_factors(training_audit)
    known_columns = {
        int(column)
        for columns in known_by_order.values()
        for column in columns
    }
    priority_columns = parse_int_set(args.priority_columns)
    forbid_columns = parse_int_set(args.forbid_selected_columns)
    index: dict[tuple[str, int, str, int, tuple[str, ...]], list[dict[str, Any]]] = {}
    for case in source_cases(source):
        index.setdefault(source_case_key(case), []).append(case)
    selected_reports = select_reports(
        support,
        args.target,
        args.selector,
        known_columns,
        priority_columns,
        forbid_columns,
        args.min_known_overlap,
        args.max_selected_support_size,
        args.min_pressure_score,
        args.max_cases,
    )
    case_results = [
        {
            **scan_case(source, index, report, known_by_order),
            "public_selection_metrics": report.get("public_selection_metrics"),
        }
        for report in selected_reports
    ]
    verified = [case for case in case_results if case.get("public_known_factor_verified")]
    structural = [case for case in case_results if int_value(case.get("known_support_form_count")) > 0]
    costs = [
        float(case["direct_ops_over_rho"])
        for case in case_results
        if case.get("direct_ops_over_rho") is not None
    ]
    cost_sum = sum(costs)
    stop_rule = first_hit_stop_rule(case_results)
    payload = {
        "artifacts": {
            "source": str(source_path),
            "support": str(support_path),
            "training_audit": str(training_path),
        },
        "case_results": case_results,
        "claim_status": (
            "KNOWN_COLUMN_PRESSURE_PUBLIC_FACTOR_RECOVERY_FOUND"
            if verified
            else (
                "KNOWN_COLUMN_PRESSURE_STRUCTURAL_FORMS_ONLY"
                if structural
                else "KNOWN_COLUMN_PRESSURE_NO_STRUCTURAL_FORM"
            )
        ),
        "created_at": now_iso(),
        "honesty_boundary": {
            "assumptions": [
                "Known factor values are inherited from the provided training audit.",
                "Public source-case selection uses selected-leaf support only and exact row-key matching.",
                "Known-factor scalar verification is post-relation public-key evidence, not a pre-scan predictor.",
            ],
            "evidence": "TOY-EVIDENCE / MODEL-BOUND / HEURISTIC-COST",
            "not_claimed": [
                "complete faster-than-rho prime-field ECDLP algorithm",
                "shared-product amortized collector",
                "deployment-relevant key recovery",
            ],
            "scope": "Direct-source low-term relation scan after a public known-column pressure gate.",
        },
        "known_factor_columns": sorted(known_columns),
        "parameters": {
            "forbid_selected_columns": sorted(forbid_columns),
            "max_cases": args.max_cases,
            "max_selected_support_size": args.max_selected_support_size,
            "min_known_overlap": args.min_known_overlap,
            "min_pressure_score": args.min_pressure_score,
            "priority_columns": sorted(priority_columns),
            "selector": args.selector,
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_known_column_pressure_direct_screen.v1",
        "summary": {
            "cost_over_rho": stat(costs),
            "cost_per_public_known_factor_recovery_over_rho": (
                round(cost_sum / len(verified), 8) if verified else None
            ),
            "cost_per_structural_known_support_case_over_rho": (
                round(cost_sum / len(structural), 8) if structural else None
            ),
            "first_public_hit_stop_rule": stop_rule,
            "public_known_factor_verified_count": len(verified),
            "scanned_case_count": len(case_results),
            "selected_report_count": len(selected_reports),
            "structural_known_support_case_count": len(structural),
            "support_report_count": len(support.get("case_reports") or []),
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
