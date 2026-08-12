#!/usr/bin/env python3
"""P692 source-form coverage audit for P691 missing factor columns."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import low_term_total2_p678_right208_salt208_public_selector_audit as p678
import low_term_total2_p690_false_rank_certificate_factor_audit as p690
import low_term_total2_p691_factor_bank_deficiency_target_audit as p691
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p692_missing_column_source_form_coverage_audit_probe.json"
DEFAULT_P691_ARTIFACT = STATE_DIR / "low_term_total2_p691_factor_bank_deficiency_target_audit_probe.json"
ORDER = p690.ORDER


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def form_parts(form: dict[str, Any], factor_count: int) -> tuple[int, list[int], int]:
    coeffs = [int_value(value) % ORDER for value in form.get("coeffs") or []]
    q_coeff = coeffs[0] if coeffs else 0
    factors = factor_bank.pad(coeffs[1:], factor_count)
    rhs = int_value(form.get("rhs")) % ORDER
    return q_coeff, factors, rhs


def load_missing_columns(path: Path) -> list[int]:
    if not path.exists():
        return [0, 15]
    payload = json.loads(path.read_text())
    return [int_value(value) for value in payload.get("summary", {}).get("missing_columns", [0, 15])]


def factor_count_for(certificates: list[dict[str, Any]]) -> int:
    count = 0
    for cert in certificates:
        forms = [form for form in (cert.get("forms") or []) if isinstance(form, dict)]
        count = max(count, max([max(0, len(form.get("coeffs") or []) - 1) for form in forms] or [0]))
    return count


def selected_key(cert: dict[str, Any]) -> tuple[str, int, str, int]:
    return p690.selected_key(cert)


def certificate_missing_audit(
    cert: dict[str, Any],
    missing_columns: list[int],
    factor_count: int,
) -> dict[str, Any]:
    forms = [form for form in (cert.get("forms") or []) if isinstance(form, dict)]
    parts = [form_parts(form, factor_count) for form in forms]
    feature = p691.cert_feature(cert)
    per_column: dict[str, dict[str, Any]] = {}
    for column in missing_columns:
        form_nonzero_indices = [idx for idx, (_q, factors, _rhs) in enumerate(parts) if factors[column] % ORDER]
        q_nonzero_with_missing = [
            idx for idx in form_nonzero_indices if parts[idx][0] % ORDER
        ]
        q_zero_with_missing = [
            idx for idx in form_nonzero_indices if not parts[idx][0] % ORDER
        ]
        ratios = []
        for idx in q_nonzero_with_missing:
            q_coeff, factors, _rhs = parts[idx]
            ratios.append((factors[column] * pow(q_coeff, -1, ORDER)) % ORDER)
        pair_nonzero = []
        for left_index, (q_left, factors_left, _rhs_left) in enumerate(parts):
            for right_index in range(left_index + 1, len(parts)):
                q_right, factors_right, _rhs_right = parts[right_index]
                value = (q_right * factors_left[column] - q_left * factors_right[column]) % ORDER
                if value:
                    pair_nonzero.append({"pair": [left_index, right_index], "value": value})
        per_column[str(column)] = {
            "form_nonzero_count": len(form_nonzero_indices),
            "form_nonzero_indices": form_nonzero_indices,
            "pair_nonzero_after_elimination_count": len(pair_nonzero),
            "pair_nonzero_after_elimination_examples": pair_nonzero[:8],
            "q_nonzero_with_missing_count": len(q_nonzero_with_missing),
            "q_zero_with_missing_count": len(q_zero_with_missing),
            "ratio_values": sorted(set(ratios))[:16],
            "target_proportional_cancellation": bool(form_nonzero_indices and not pair_nonzero),
        }
    return {
        "feature": feature,
        "forms_count": len(forms),
        "per_missing_column": per_column,
        "touches_missing_source_form": any(row["form_nonzero_count"] for row in per_column.values()),
        "survives_target_elimination": any(
            row["pair_nonzero_after_elimination_count"] for row in per_column.values()
        ),
    }


def summarize_buckets(certificate_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fields = [
        "selector_mode",
        "right_anchor_token",
        "row_pair",
        "mode_anchor_row_pair",
        "mode_leaf",
        "leaf_signature",
        "selected_term_support",
        "transfer_mod7",
        "transfer_mod12",
    ]
    buckets: dict[tuple[str, str], dict[str, Any]] = {}
    for row in certificate_rows:
        feature = row["feature"]
        touches = bool(row["touches_missing_source_form"])
        survives = bool(row["survives_target_elimination"])
        for field in fields:
            key = (field, str(feature.get(field)))
            bucket = buckets.setdefault(
                key,
                {
                    "certificate_count": 0,
                    "field": field,
                    "surviving_certificate_count": 0,
                    "touching_certificate_count": 0,
                    "value": str(feature.get(field)),
                },
            )
            bucket["certificate_count"] += 1
            if touches:
                bucket["touching_certificate_count"] += 1
            if survives:
                bucket["surviving_certificate_count"] += 1
    out = []
    for bucket in buckets.values():
        if bucket["certificate_count"] < 3:
            continue
        out.append(
            {
                **bucket,
                "source_touch_density": bucket["touching_certificate_count"] / max(1, bucket["certificate_count"]),
                "survival_density": bucket["surviving_certificate_count"] / max(1, bucket["certificate_count"]),
            }
        )
    out.sort(
        key=lambda item: (
            -float(item["source_touch_density"]),
            -int(item["touching_certificate_count"]),
            -int(item["certificate_count"]),
            str(item["field"]),
            str(item["value"]),
        )
    )
    return out


def determine_claim(summary: dict[str, Any]) -> str:
    if summary["surviving_pair_coeff_count"]:
        return "P692_MISSING_COLUMNS_SURVIVE_TARGET_ELIMINATION_EXTRACTION_CONFLICT"
    if summary["forms_with_missing_coeff_count"]:
        return "P692_MISSING_COLUMNS_CANCEL_UNDER_TARGET_ELIMINATION"
    return "P692_MISSING_COLUMNS_ABSENT_FROM_SOURCE_FORMS"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", action="append", default=None, help="Certificate artifact to include.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p691-artifact", default=str(DEFAULT_P691_ARTIFACT))
    args = parser.parse_args()

    paths = [Path(path) for path in (args.certificate or [str(path) for path in p690.DEFAULT_CERTIFICATE_PATHS])]
    certificates = factor_bank.load_certificates(paths)
    candidates, _missing = p690.find_candidates(certificates)
    candidate_keys = {selected_key(cert) for cert in candidates}
    base = [cert for cert in certificates if selected_key(cert) not in candidate_keys]
    missing_columns = load_missing_columns(Path(args.p691_artifact))
    factor_count = factor_count_for(base)
    rows = [certificate_missing_audit(cert, missing_columns, factor_count) for cert in base]
    per_column = {}
    for column in missing_columns:
        key = str(column)
        touching = [row for row in rows if row["per_missing_column"][key]["form_nonzero_count"]]
        surviving = [
            row for row in rows if row["per_missing_column"][key]["pair_nonzero_after_elimination_count"]
        ]
        per_column[key] = {
            "certificates_with_source_coeff_count": len(touching),
            "certificates_with_surviving_pair_coeff_count": len(surviving),
            "forms_with_source_coeff_count": sum(
                row["per_missing_column"][key]["form_nonzero_count"] for row in rows
            ),
            "surviving_pair_coeff_count": sum(
                row["per_missing_column"][key]["pair_nonzero_after_elimination_count"] for row in rows
            ),
            "target_proportional_certificate_count": sum(
                1 for row in touching if row["per_missing_column"][key]["target_proportional_cancellation"]
            ),
        }
    summary = {
        "base_certificate_count": len(base),
        "candidate_excluded_count": len(candidates),
        "certificates_with_missing_coeff_count": sum(1 for row in rows if row["touches_missing_source_form"]),
        "certificates_with_surviving_pair_coeff_count": sum(1 for row in rows if row["survives_target_elimination"]),
        "factor_variable_count": factor_count,
        "forms_count": sum(row["forms_count"] for row in rows),
        "forms_with_missing_coeff_count": sum(
            sum(row["per_missing_column"][str(column)]["form_nonzero_count"] for column in missing_columns)
            for row in rows
        ),
        "missing_columns": missing_columns,
        "per_missing_column": per_column,
        "surviving_pair_coeff_count": sum(
            sum(
                row["per_missing_column"][str(column)]["pair_nonzero_after_elimination_count"]
                for column in missing_columns
            )
            for row in rows
        ),
    }
    claim_status = determine_claim(summary)
    buckets = summarize_buckets(rows)
    payload = {
        "schema": "ecdlp.low_term_total2_p692_missing_column_source_form_coverage_audit.v1",
        "created_at": p678.utc_now(),
        "method": "p692_missing_column_source_form_coverage_audit",
        "claim_status": claim_status,
        "artifacts": {"certificates": [str(path) for path in paths], "p691_artifact": str(args.p691_artifact)},
        "parameters": {
            "base_rule": "all listed direct certificate artifacts excluding exact P690 candidate selected rows",
            "elimination_formula": "q_right * f_left[column] - q_left * f_right[column] mod order",
            "missing_columns": missing_columns,
            "order": ORDER,
        },
        "summary": summary,
        "top_source_touch_feature_buckets": buckets[:40],
        "certificate_examples": [
            row
            for row in rows
            if row["touches_missing_source_form"] or row["survives_target_elimination"]
        ][:24],
        "honesty_boundary": [
            "This audit only explains why current certificates miss P691 columns.",
            "It does not generate new endpoint-column relations.",
            "Target-proportional cancellation is a constructive obstruction and should produce the next generator requirement.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_status": claim_status, "summary": summary, "top_buckets": buckets[:8]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
