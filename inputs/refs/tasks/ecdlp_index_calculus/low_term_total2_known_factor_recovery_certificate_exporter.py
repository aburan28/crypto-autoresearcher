#!/usr/bin/env python3
"""Export certificates for source-family known-factor recoveries.

The source-family expansion scout can verify a target scalar by substituting
previously derived factor logs into a single public relation form.  That is not
the same evidence surface as a direct public-source certificate, so this
exporter gives it its own durable certificate format:

* replay the exact public source/support report;
* keep the public relation forms from the direct scan;
* record the factor-log substitution that recovers the target scalar; and
* attach a target-eliminated factor-rank audit for these exported forms.

This is still a toy ECDLP index-calculus diagnostic, not a deployed-curve break.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import glob
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank
from frontier_signed_eval_cover_dependency_circuit_probe import public_secret_matches
from low_term_total2_known_column_pressure_direct_screen import (
    find_exact_source_case,
    int_value,
    report_key,
    source_case_key,
    source_cases,
)
from low_term_total2_known_factor_holdout_descent_probe import known_factors
from low_term_total2_source_relation_equation_certificate import compact_form


WINDOW_RE = re.compile(r"(?:fixed_row_|selector_expanded_|col15_)(\d+)_(\d+)")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def float_value(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def parse_paths(raw: str) -> list[Path]:
    paths: list[Path] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        matches = sorted(Path(path) for path in glob.glob(item))
        paths.extend(matches or [Path(item)])
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def window_from_path(path: Path) -> str:
    match = WINDOW_RE.search(path.name)
    if not match:
        return ""
    return f"{int(match.group(1))}_{int(match.group(2))}"


def window_from_row(row: dict[str, Any]) -> str:
    return str(row.get("window") or "")


def build_window_map(paths: list[Path]) -> dict[str, Path]:
    mapped: dict[str, Path] = {}
    for path in paths:
        window = window_from_path(path)
        if window:
            mapped[window] = path
    return mapped


def canonical_rows(row_keys: Any) -> list[str]:
    if not isinstance(row_keys, list):
        return []
    return sorted(str(row) for row in row_keys)


def row_case(row: dict[str, Any]) -> dict[str, Any]:
    hit_case = row.get("hit_case")
    if isinstance(hit_case, dict):
        return hit_case
    structural_case = row.get("structural_case")
    if isinstance(structural_case, dict):
        return structural_case
    scanned_rows = row.get("scanned_rows")
    if isinstance(scanned_rows, list):
        for scanned in scanned_rows:
            if isinstance(scanned, dict):
                return scanned
    return {}


def case_public(row: dict[str, Any]) -> dict[str, Any]:
    case = row_case(row)
    public = case.get("public")
    return public if isinstance(public, dict) else {}


def source_family_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = load_json(path)
        for row_offset, row in enumerate(payload.get("rows") or []):
            if not isinstance(row, dict):
                continue
            if not row.get("hit"):
                continue
            public = case_public(row)
            if not public:
                continue
            rows.append(
                {
                    "artifact": path,
                    "row": row,
                    "row_offset": row_offset,
                    "window": window_from_row(row),
                    "public": public,
                }
            )
    rows.sort(key=lambda item: (item["window"], str(item["artifact"]), int_value(item["row_offset"])))
    return rows


def find_report(support_payload: dict[str, Any], public: dict[str, Any], target: str) -> dict[str, Any]:
    wanted = (
        str(target or public.get("target")),
        int_value(public.get("transfer_index")),
        str(public.get("selector")),
        int_value(public.get("top_k")),
        tuple(canonical_rows(public.get("row_keys"))),
    )
    matches = []
    for report in support_payload.get("case_reports") or []:
        if not isinstance(report, dict):
            continue
        key = report_key(report)
        normalized = (key[0], key[1], key[2], key[3], tuple(canonical_rows(list(key[4]))))
        if normalized == wanted:
            matches.append(report)
    if not matches:
        raise ValueError(f"no support report for source-family public key {wanted!r}")
    return sorted(matches, key=lambda item: str(item.get("source_policy")))[0]


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


def rank_mod(matrix: list[list[int]], modulus: int) -> int:
    rows = [row[:] for row in matrix if any(value % modulus for value in row)]
    if not rows:
        return 0
    row_count = len(rows)
    col_count = len(rows[0])
    rank = 0
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if rows[row][col] % modulus:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col] % modulus, -1, modulus)
        rows[rank] = [(value * inv) % modulus for value in rows[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = rows[row][col] % modulus
            if factor:
                rows[row] = [
                    (rows[row][idx] - factor * rows[rank][idx]) % modulus
                    for idx in range(col_count)
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def rich_known_factor_attempt(
    verifier: Any,
    built: dict[str, Any],
    event: dict[str, Any],
    known: dict[int, int],
    form_index: int,
) -> dict[str, Any]:
    order = int_value(built.get("order"))
    p = int_value(built.get("p"))
    coeffs_raw, rhs_raw, terms_raw = event["form"]
    coeffs = [int_value(value) % order for value in coeffs_raw]
    rhs = int_value(rhs_raw) % order
    terms = [int_value(term) for term in terms_raw]
    if not coeffs:
        return {"form_index": form_index, "recoverable": False, "reason": "empty_coefficients", "terms": terms}
    target_coeff = coeffs[0] % order
    factor_coeffs = coeffs[1:]
    support = [idx for idx, coeff in enumerate(factor_coeffs) if coeff % order]
    if target_coeff == 0:
        return {
            "form": {"coeffs": coeffs, "rhs": rhs, "terms": terms},
            "form_index": form_index,
            "recoverable": False,
            "reason": "zero_target_coefficient",
            "support": support,
            "terms": terms,
        }
    unknown = [idx for idx in support if idx not in known]
    known_support = [idx for idx in support if idx in known]
    if unknown:
        return {
            "form": {"coeffs": coeffs, "rhs": rhs, "terms": terms},
            "form_index": form_index,
            "known_support": known_support,
            "recoverable": False,
            "reason": "unknown_factor_support",
            "support": support,
            "target_coefficient": target_coeff,
            "terms": terms,
            "unknown_factor_support": unknown,
        }
    known_terms = [
        {
            "coefficient": factor_coeffs[column] % order,
            "column": column,
            "contribution": (factor_coeffs[column] * known[column]) % order,
            "known_log": known[column] % order,
        }
        for column in support
    ]
    factor_sum = sum(item["contribution"] for item in known_terms) % order
    residual = (rhs - factor_sum) % order
    derived = (residual * pow(target_coeff, -1, order)) % order
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
        "form": {"coeffs": coeffs, "rhs": rhs, "terms": terms},
        "form_index": form_index,
        "known_factor_terms": known_terms,
        "known_support": support,
        "public_key_verified": verified,
        "recoverable": True,
        "residual_after_factor_substitution": residual,
        "rhs": rhs,
        "support": support,
        "target_coefficient": target_coeff,
        "terms": terms,
    }


def selected_term_support(contexts: list[dict[str, Any]]) -> list[int]:
    support: set[int] = set()
    for context in contexts:
        selected = {int_value(leaf) for leaf in context.get("selected_leaf_indices") or []}
        for scout in context["built"].get("scouts") or []:
            pos = scout.get("scout_pos")
            if pos in selected or (isinstance(pos, int) and pos - 1 in selected):
                support.update(int_value(index) for index, _sign in scout.get("signed_terms") or [])
    return sorted(support)


def export_certificate(
    source_path: Path,
    support_path: Path,
    source_payload: dict[str, Any],
    support_payload: dict[str, Any],
    source_index: dict[tuple[str, int, str, int, tuple[str, ...]], list[dict[str, Any]]],
    source_family_item: dict[str, Any],
    known_by_order: dict[int, dict[int, int]],
    target: str,
) -> dict[str, Any]:
    public = source_family_item["public"]
    report = find_report(support_payload, public, target)
    source_case = find_exact_source_case(source_index, report)
    verifier, contexts, product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(
        source_payload,
        source_case,
    )
    direct_rows, direct_ops, rho, _row_profiles = timing_probe.direct_witness_rows(verifier, contexts)
    if not contexts:
        raise ValueError(f"no selected contexts for {report_key(report)!r}")
    built = contexts[0]["built"]
    order = int_value(built.get("order"))
    known = known_by_order.get(order, {})
    events = direct_unique_events(direct_rows)
    attempts = [
        rich_known_factor_attempt(verifier, built, event, known, form_index)
        for form_index, event in enumerate(events)
    ]
    verified_attempts = [attempt for attempt in attempts if attempt.get("public_key_verified")]
    recoverable_attempts = [attempt for attempt in attempts if attempt.get("recoverable")]
    derived_values = sorted({int_value(attempt.get("derived_secret")) for attempt in verified_attempts})
    forms = [compact_form(event, order) for event in events]
    form_rank = rank_mod([[int_value(value) % order for value in form.get("coeffs") or []] for form in forms], order)
    selected = {
        "clause": "known_factor_substitution",
        "direct_ops": direct_ops,
        "direct_ops_over_rho": ratio(direct_ops, rho),
        "rho": rho,
        "row_keys": report.get("row_keys") or [],
        "secret": derived_values[0] if len(derived_values) == 1 else None,
        "selector": report.get("selector"),
        "source_family_cost_over_rho": source_family_item["row"].get("cost_over_rho"),
        "source_family_row_offset": int_value(source_family_item.get("row_offset")),
        "source_family_scanned_candidate_count": int_value(source_family_item["row"].get("scanned_candidate_count")),
        "target": target or report.get("target"),
        "top_k": int_value(report.get("top_k")),
        "transfer_index": int_value(report.get("transfer_index")),
    }
    return {
        "certificate_status": (
            "KNOWN_FACTOR_SUBSTITUTION_RECOVERY_VERIFIES_PUBLIC_KEY"
            if verified_attempts and len(derived_values) == 1
            else "KNOWN_FACTOR_SUBSTITUTION_RECOVERY_NEEDS_REVIEW"
            if verified_attempts
            else "KNOWN_FACTOR_SUBSTITUTION_NO_VERIFIED_RECOVERY"
        ),
        "clause": "known_factor_substitution",
        "derived_secret": selected["secret"],
        "expected_secret": selected["secret"],
        "forms": forms,
        "forms_count": len(forms),
        "known_factor_recoveries": verified_attempts,
        "known_factor_recovery_count": len(verified_attempts),
        "known_factor_recovery_values": derived_values,
        "known_factor_supports": sorted({tuple(attempt.get("support") or []) for attempt in verified_attempts}),
        "known_support_form_count": sum(
            1
            for attempt in recoverable_attempts
            if not attempt.get("unknown_factor_support")
        ),
        "order": order,
        "product_factor": product_factor,
        "public_key_verified": bool(verified_attempts and len(derived_values) == 1),
        "rank": form_rank,
        "recoverable_form_count": len(recoverable_attempts),
        "scan_row_count": len(direct_rows),
        "scanned_form_count": len(attempts),
        "selected": selected,
        "selected_term_support": selected_term_support(contexts),
        "source": str(source_path),
        "source_case_selector": {
            "selector": source_case.get("selector"),
            "target": source_case.get("target"),
            "top_k": int_value(source_case.get("top_k")),
            "transfer_index": int_value(source_case.get("transfer_index")),
        },
        "source_family": {
            "artifact": str(source_family_item["artifact"]),
            "bridge_gap_window": source_family_item["window"],
            "cost_over_rho": source_family_item["row"].get("cost_over_rho"),
            "hit_case_public": public,
            "row_offset": int_value(source_family_item.get("row_offset")),
        },
        "support": str(support_path),
        "timing": None,
        "window": source_family_item["window"],
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


def summarize(certificates: list[dict[str, Any]], rank_audits: dict[str, Any]) -> dict[str, Any]:
    passing = [cert for cert in certificates if cert.get("public_key_verified")]
    costs = [
        float_value((cert.get("selected") or {}).get("source_family_cost_over_rho"))
        for cert in certificates
        if float_value((cert.get("selected") or {}).get("source_family_cost_over_rho")) is not None
    ]
    supports = sorted(
        {
            tuple(support)
            for cert in certificates
            for support in cert.get("known_factor_supports") or []
        }
    )
    total_rank = sum(int_value(audit.get("rank")) for audit in rank_audits.values())
    total_unique = sum(int_value(audit.get("unique_factor_relation_count")) for audit in rank_audits.values())
    return {
        "certificate_count": len(certificates),
        "cost_over_rho": stat([float(value) for value in costs]),
        "known_factor_recovery_count": sum(int_value(cert.get("known_factor_recovery_count")) for cert in certificates),
        "known_factor_supports": [list(support) for support in supports],
        "passing_certificate_count": len(passing),
        "target_eliminated_factor_rank_total": total_rank,
        "target_eliminated_unique_factor_relation_count": total_unique,
        "window_count": len({str(cert.get("window")) for cert in certificates}),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-family-artifacts", required=True, help="Comma-separated source-family JSON paths/globs.")
    parser.add_argument(
        "--source-glob",
        default=(
            "ecdlp_index_calculus_state/"
            "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_*_col15_selector_expanded_probe.json"
        ),
    )
    parser.add_argument(
        "--support-glob",
        default=(
            "ecdlp_index_calculus_state/"
            "low_term_total2_selected_leaf_term_support_scout_22050_col15_selector_expanded_*_probe.json"
        ),
    )
    parser.add_argument("--training-audit", required=True)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_family_paths = parse_paths(args.source_family_artifacts)
    source_rows = source_family_rows(source_family_paths)
    source_paths = build_window_map(parse_paths(args.source_glob))
    support_paths = build_window_map(parse_paths(args.support_glob))
    training_audit_path = Path(args.training_audit)
    known_by_order = known_factors(load_json(training_audit_path))

    source_cache: dict[Path, dict[str, Any]] = {}
    support_cache: dict[Path, dict[str, Any]] = {}
    index_cache: dict[Path, dict[tuple[str, int, str, int, tuple[str, ...]], list[dict[str, Any]]]] = {}
    certificates: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for item in source_rows:
        window = item["window"]
        source_path = source_paths.get(window)
        support_path = support_paths.get(window)
        if source_path is None or support_path is None:
            errors.append(
                {
                    "error": "missing_source_or_support_artifact",
                    "source_family_artifact": str(item["artifact"]),
                    "window": window,
                }
            )
            continue
        source_payload = source_cache.setdefault(source_path, load_json(source_path))
        support_payload = support_cache.setdefault(support_path, load_json(support_path))
        if source_path not in index_cache:
            index: dict[tuple[str, int, str, int, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
            for case in source_cases(source_payload):
                index[source_case_key(case)].append(case)
            index_cache[source_path] = dict(index)
        try:
            certificates.append(
                export_certificate(
                    source_path,
                    support_path,
                    source_payload,
                    support_payload,
                    index_cache[source_path],
                    item,
                    known_by_order,
                    args.target,
                )
            )
        except Exception as exc:  # Preserve failed exports as evidence without aborting all windows.
            errors.append(
                {
                    "error": type(exc).__name__,
                    "message": str(exc),
                    "source_family_artifact": str(item["artifact"]),
                    "window": window,
                }
            )

    audit_certificates = [
        {
            **cert,
            "_artifact": args.out,
            "_artifact_offset": index,
            "_global_index": index,
        }
        for index, cert in enumerate(certificates)
    ]
    rank_audits = {
        str(order): factor_bank.audit_order(audit_certificates, order)
        for order in sorted({int_value(cert.get("order")) for cert in audit_certificates})
    }
    summary = summarize(certificates, rank_audits)
    payload = {
        "artifacts": {
            "source_family": [str(path) for path in source_family_paths],
            "source_glob": args.source_glob,
            "support_glob": args.support_glob,
            "training_audit": str(training_audit_path),
        },
        "certificates": certificates,
        "claim_status": (
            "KNOWN_FACTOR_RECOVERY_CERTIFICATES_EXPORTED"
            if summary["passing_certificate_count"]
            else "KNOWN_FACTOR_RECOVERY_CERTIFICATE_EXPORT_NO_PASSING_RECOVERY"
        ),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: factor logs are inherited from the provided training audit and are substituted into replayed public relation forms.",
            "These are known-factor recovery certificates, not direct public-source certificates and not shared-product amortized certificates.",
            "OPEN: this does not by itself beat Pollard rho; it creates a separate target-descent accounting surface for the index-calculus candidate.",
        ],
        "known_factor_columns": {
            str(order): sorted(columns)
            for order, columns in known_by_order.items()
        },
        "order_audits": rank_audits,
        "schema": "ecdlp.low_term_total2_known_factor_recovery_certificate_exporter.v1",
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"], "error_count": len(errors)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
