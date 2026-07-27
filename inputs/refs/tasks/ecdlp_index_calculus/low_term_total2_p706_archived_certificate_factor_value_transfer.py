#!/usr/bin/env python3
"""P706 archived-certificate transfer audit for P702 factor values.

P704/P705 tested fresh endpoint surfaces near P658-P661.  This audit checks the
wider archived direct-certificate corpus: for each public-key-verified order-9887
certificate, substitute the P702-derived factor values into every relation form
and compare the recovered secret against the certificate's verified secret.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P702 = STATE_DIR / "low_term_total2_p702_factor_substitution_target_verification_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p706_archived_certificate_factor_value_transfer_probe.json"
DEFAULT_CERT_GLOB = str(STATE_DIR / "low_term_total2_direct_relation_equation_certificate_67_order9887_*_probe.json")
ORDER = 9887


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def p_id(path: Path) -> str:
    match = re.search(r"_p(\d+)_", path.name)
    return f"P{match.group(1)}" if match else "unknown"


def load_factor_values(path: Path) -> dict[int, int]:
    payload = load_json(path)
    values: dict[int, int] = {}
    for item in payload.get("derived_factor_values") or []:
        variable = str(item.get("factor_variable") or "")
        match = re.search(r"column=(\d+)", variable)
        if not match:
            continue
        values[int(match.group(1))] = int_value(item.get("value")) % ORDER
    return values


def expected_secret(cert: dict[str, Any], order: int) -> int | None:
    if cert.get("expected_secret") is not None:
        return int_value(cert.get("expected_secret")) % order
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    if selected.get("secret") is not None:
        return int_value(selected.get("secret")) % order
    if cert.get("derived_secret") is not None and cert.get("public_key_verified"):
        return int_value(cert.get("derived_secret")) % order
    return None


def selected_cost(cert: dict[str, Any]) -> float | None:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    value = cert.get("direct_ops_over_rho")
    if value is None:
        value = selected.get("direct_ops_over_rho")
    if value is None:
        return None
    return float_value(value)


def support(coeffs: list[int], order: int) -> list[int]:
    return [index for index, value in enumerate(coeffs) if value % order]


def substitute_form(
    cert: dict[str, Any],
    form: dict[str, Any],
    form_index: int,
    factor_values: dict[int, int],
) -> dict[str, Any]:
    order = int_value(cert.get("order"), ORDER)
    factor_count = max(16, len(form.get("coeffs") or []) - 1)
    q_coeff, factor_coeffs, rhs = factor_bank.form_parts(form, order, factor_count)
    form_support = support(factor_coeffs, order)
    missing = [index for index in form_support if index not in factor_values]
    recovered: int | None = None
    if q_coeff % order == 0:
        status = "Q_COEFF_ZERO"
    elif missing:
        status = "MISSING_FACTOR_VALUES"
    else:
        known_sum = sum(factor_coeffs[index] * factor_values[index] for index in form_support) % order
        recovered = ((rhs - known_sum) * pow(q_coeff % order, -1, order)) % order
        status = "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION"
    expected = expected_secret(cert, order)
    return {
        "derived_secret": recovered,
        "expected_secret": expected,
        "factor_support": form_support,
        "form_index": form_index,
        "missing_factor_columns": missing,
        "q_coeff": q_coeff % order,
        "rhs": rhs % order,
        "status": status,
        "verified_matches_expected": bool(recovered is not None and expected is not None and recovered == expected),
    }


def cost_stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {
        "count": len(values),
        "max": round(max(values), 8),
        "mean": round(mean(values), 8),
        "min": round(min(values), 8),
    }


def artifact_report(path: Path, factor_values: dict[int, int], sample_limit: int) -> dict[str, Any]:
    payload = load_json(path)
    status_counts: Counter[str] = Counter()
    secret_counts: Counter[str] = Counter()
    false_count = 0
    verified_count = 0
    form_count = 0
    cert_count = 0
    cost_values = []
    samples = []
    for cert_index, cert in enumerate(payload.get("certificates") or []):
        if int_value(cert.get("order"), ORDER) != ORDER:
            continue
        if cert.get("public_key_verified") is False:
            continue
        cert_count += 1
        cost = selected_cost(cert)
        if cost is not None:
            cost_values.append(cost)
        for form_index, form in enumerate(cert.get("forms") or []):
            if not isinstance(form, dict):
                continue
            report = substitute_form(cert, form, form_index, factor_values)
            status_counts[report["status"]] += 1
            if report["verified_matches_expected"]:
                verified_count += 1
                secret_counts[str(report["derived_secret"])] += 1
            elif report["status"] == "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION":
                false_count += 1
            form_count += 1
            if len(samples) < sample_limit:
                selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
                samples.append(
                    {
                        "certificate_index": cert_index,
                        "direct_ops_over_rho": cost,
                        "expected_secret": report["expected_secret"],
                        "form_index": form_index,
                        "selected": {
                            "selector": selected.get("selector"),
                            "target": selected.get("target"),
                            "transfer_index": selected.get("transfer_index"),
                        },
                        "substitution": report,
                    }
                )
    return {
        "artifact": str(path),
        "certificate_count": cert_count,
        "claim_status": (
            "ARCHIVED_CERTIFICATE_FORMS_ALL_TRANSFER"
            if form_count and verified_count == form_count and not false_count
            else "ARCHIVED_CERTIFICATE_FORMS_PARTIAL_TRANSFER"
            if verified_count and not false_count
            else "ARCHIVED_CERTIFICATE_FORMS_FALSE_RECOVERY"
            if false_count
            else "ARCHIVED_CERTIFICATE_FORMS_NO_TRANSFER"
        ),
        "direct_ops_over_rho_stats": cost_stats(cost_values),
        "false_recoverable_form_count": false_count,
        "form_count": form_count,
        "p_id": p_id(path),
        "sample_reports": samples,
        "secret_counts": dict(sorted(secret_counts.items(), key=lambda item: int(item[0]))),
        "status_counts": dict(sorted(status_counts.items())),
        "summary_claim": (payload.get("summary") or {}).get("claim_status"),
        "verified_recoverable_form_count": verified_count,
    }


def determine_claim(reports: list[dict[str, Any]]) -> str:
    total_forms = sum(int_value(report.get("form_count")) for report in reports)
    total_verified = sum(int_value(report.get("verified_recoverable_form_count")) for report in reports)
    total_false = sum(int_value(report.get("false_recoverable_form_count")) for report in reports)
    if reports and total_forms and total_verified == total_forms and not total_false:
        return "P706_ARCHIVED_CERTIFICATE_FACTOR_VALUES_ALL_TRANSFER"
    if total_verified and not total_false:
        return "P706_ARCHIVED_CERTIFICATE_FACTOR_VALUES_PARTIAL_TRANSFER"
    if total_false:
        return "NEGATIVE_RESULT_P706_ARCHIVED_FACTOR_VALUE_FALSE_RECOVERY"
    return "NEGATIVE_RESULT_P706_NO_ARCHIVED_FACTOR_VALUE_TRANSFER"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    factor_values = load_factor_values(Path(args.p702))
    paths = [Path(path) for path in sorted(glob.glob(args.certificate_glob))]
    reports = [artifact_report(path, factor_values, int_value(args.sample_limit)) for path in paths]
    reports = [report for report in reports if int_value(report.get("form_count"))]
    total_forms = sum(int_value(report.get("form_count")) for report in reports)
    total_verified = sum(int_value(report.get("verified_recoverable_form_count")) for report in reports)
    total_false = sum(int_value(report.get("false_recoverable_form_count")) for report in reports)
    cost_values = []
    for report in reports:
        stats = report.get("direct_ops_over_rho_stats") or {}
        if stats.get("min") is not None:
            cost_values.append(float_value(stats.get("min")))
        if stats.get("mean") is not None:
            cost_values.append(float_value(stats.get("mean")))
        if stats.get("max") is not None:
            cost_values.append(float_value(stats.get("max")))
    claim_status = determine_claim(reports)
    return {
        "artifacts": {
            "certificate_glob": args.certificate_glob,
            "p702": str(Path(args.p702)),
        },
        "artifact_reports": reports,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: verification uses archived public-key-verified certificate expected secrets as the oracle.",
            "HEURISTIC: this is a transfer-correctness audit over archived direct certificates, not fresh relation generation.",
            "NO DEPLOYED-CURVE CLAIM: target-source prediction, large-scale sparse LA, and asymptotics remain open.",
        ],
        "method": "p706_archived_certificate_factor_value_transfer",
        "parameters": {
            "factor_column_count": len(factor_values),
            "order": ORDER,
        },
        "schema": "ecdlp.low_term_total2_p706_archived_certificate_factor_value_transfer.v1",
        "summary": {
            "artifact_count": len(reports),
            "direct_ops_over_rho_observed_stat_values": cost_stats(cost_values),
            "factor_column_count": len(factor_values),
            "false_recoverable_form_count": total_false,
            "form_count": total_forms,
            "fully_transferred_artifact_count": sum(
                1 for report in reports if report.get("claim_status") == "ARCHIVED_CERTIFICATE_FORMS_ALL_TRANSFER"
            ),
            "verified_recoverable_form_count": total_verified,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p702", default=str(DEFAULT_P702))
    parser.add_argument("--certificate-glob", default=DEFAULT_CERT_GLOB)
    parser.add_argument("--sample-limit", type=int, default=4)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
