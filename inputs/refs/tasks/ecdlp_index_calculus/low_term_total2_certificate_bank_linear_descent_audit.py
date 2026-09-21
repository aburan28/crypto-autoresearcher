#!/usr/bin/env python3
"""Audit whether a public certificate bank supports target descent.

The relation-equation certificates prove that selected source rows can derive
their own toy scalar from public equations.  Target descent needs a stronger
property: reusable factor-base information, or cross-certificate recovery of a
fresh target without reading that target's own secret label.

This audit models each certificate form as a linear equation

    q_i * secret(Q_i) + sum_j a_ij * log(F_j) = rhs_i mod order

with one target-secret variable per public target instance and shared
factor-base variables per order.  It then checks which variables are determined
by the public equation rowspace, and whether a target remains determined after
removing its own certificate rows.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def certificate_is_usable(cert: dict[str, Any]) -> bool:
    status = str(cert.get("certificate_status") or "")
    if "NEEDS_REVIEW" in status:
        return False
    if cert.get("rowspace_derives_expected_secret") is False:
        return False
    if cert.get("public_key_verified") is False:
        return False
    return True


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "min": min(values),
    }


def selected_key(cert: dict[str, Any], cert_index: int) -> str:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    target = str(selected.get("target") or "unknown")
    transfer = int_value(selected.get("transfer_index"))
    window = str(cert.get("window") or "unknown")
    return f"Q:{target}:transfer={transfer}:window={window}:cert={cert_index}"


def load_certificates(paths: list[Path]) -> list[dict[str, Any]]:
    certificates: list[dict[str, Any]] = []
    for path in paths:
        payload = load_json(path)
        for offset, cert in enumerate(payload.get("certificates") or []):
            if not isinstance(cert, dict):
                continue
            if not certificate_is_usable(cert):
                continue
            item = dict(cert)
            item["_artifact"] = str(path)
            item["_artifact_offset"] = offset
            item["_global_index"] = len(certificates)
            certificates.append(item)
    return certificates


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


def solve_mod(matrix: list[list[int]], rhs: list[int], modulus: int) -> list[int] | None:
    if not matrix:
        return [] if not rhs else None
    row_count = len(matrix)
    col_count = len(matrix[0])
    rows = [
        [(value % modulus) for value in matrix[row]] + [rhs[row] % modulus]
        for row in range(row_count)
    ]
    rank = 0
    pivots: list[int] = []
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
                    for idx in range(col_count + 1)
                ]
        pivots.append(col)
        rank += 1
        if rank == row_count:
            break
    for row in rows:
        if not any(row[col] % modulus for col in range(col_count)) and row[-1] % modulus:
            return None
    solution = [0] * col_count
    for row, col in enumerate(pivots):
        solution[col] = rows[row][-1] % modulus
    return solution


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    if not matrix:
        return []
    return [list(col) for col in zip(*matrix)]


def derive_variable(
    rows: list[list[int]],
    rhs: list[int],
    var_index: int,
    modulus: int,
) -> dict[str, Any]:
    if not rows:
        return {"derivable": False, "value": None}
    unit = [0] * len(rows[0])
    unit[var_index] = 1
    coefficients = solve_mod(transpose(rows), unit, modulus)
    if coefficients is None:
        return {"derivable": False, "value": None}
    value = sum((coefficients[row] * rhs[row]) for row in range(len(rhs))) % modulus
    nonzero_rows = sum(1 for coefficient in coefficients if coefficient % modulus)
    return {
        "combination_row_count": nonzero_rows,
        "derivable": True,
        "value": value,
    }


def build_order_system(certificates: list[dict[str, Any]], order: int) -> dict[str, Any]:
    order_certs = [cert for cert in certificates if int_value(cert.get("order")) == order]
    target_vars = [selected_key(cert, int_value(cert.get("_global_index"))) for cert in order_certs]
    target_index = {
        int_value(cert.get("_global_index")): index
        for index, cert in enumerate(order_certs)
    }
    max_factor_columns = 0
    for cert in order_certs:
        for form in cert.get("forms") or []:
            coeffs = form.get("coeffs") or []
            max_factor_columns = max(max_factor_columns, max(0, len(coeffs) - 1))
    factor_vars = [f"F:{order}:column={index}" for index in range(max_factor_columns)]
    variables = target_vars + factor_vars
    rows: list[list[int]] = []
    rhs: list[int] = []
    row_certificate_indices: list[int] = []
    for cert in order_certs:
        cert_id = int_value(cert.get("_global_index"))
        for form in cert.get("forms") or []:
            coeffs = [int_value(value) % order for value in (form.get("coeffs") or [])]
            if not coeffs:
                continue
            row = [0] * len(variables)
            row[target_index[cert_id]] = coeffs[0] % order
            for offset, coeff in enumerate(coeffs[1:]):
                row[len(target_vars) + offset] = coeff % order
            rows.append(row)
            rhs.append(int_value(form.get("rhs")) % order)
            row_certificate_indices.append(cert_id)
    return {
        "certificates": order_certs,
        "factor_vars": factor_vars,
        "row_certificate_indices": row_certificate_indices,
        "rows": rows,
        "rhs": rhs,
        "target_vars": target_vars,
        "variables": variables,
    }


def certificate_summary(cert: dict[str, Any], derived: dict[str, Any]) -> dict[str, Any]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    expected = int_value(cert.get("expected_secret"))
    value = derived.get("value")
    return {
        "artifact": cert.get("_artifact"),
        "certificate_index": int_value(cert.get("_global_index")),
        "clause": cert.get("clause") or selected.get("clause"),
        "derived_matches_expected_secret": bool(derived.get("derivable")) and value == expected,
        "forms_count": int_value(cert.get("forms_count")),
        "public_rowspace_derivable": bool(derived.get("derivable")),
        "rowspace_derived_secret": value,
        "target": selected.get("target"),
        "top_k": int_value(selected.get("top_k")),
        "transfer_index": int_value(selected.get("transfer_index")),
        "window": cert.get("window"),
    }


def audit_order(
    certificates: list[dict[str, Any]],
    order: int,
    max_target_derivations: int | None = None,
    max_cross_certificate_checks: int | None = None,
) -> dict[str, Any]:
    system = build_order_system(certificates, order)
    rows = system["rows"]
    rhs = system["rhs"]
    variables = system["variables"]
    target_vars = system["target_vars"]
    factor_vars = system["factor_vars"]
    row_cert_indices = system["row_certificate_indices"]
    rank = rank_mod(rows, order)
    target_derivations: list[dict[str, Any]] = []
    cross_certificate_recoveries = 0
    local_matches = 0
    target_check_limit = (
        len(system["certificates"])
        if max_target_derivations is None
        else max(0, max_target_derivations)
    )
    cross_check_limit = (
        len(system["certificates"])
        if max_cross_certificate_checks is None
        else max(0, max_cross_certificate_checks)
    )
    target_checks = 0
    cross_checks = 0
    for target_pos, cert in enumerate(system["certificates"]):
        if target_checks >= target_check_limit:
            break
        derived = derive_variable(rows, rhs, target_pos, order)
        target_checks += 1
        item = certificate_summary(cert, derived)
        cert_id = int_value(cert.get("_global_index"))
        if cross_checks < cross_check_limit:
            reduced_rows = [
                row
                for row, row_cert_id in zip(rows, row_cert_indices)
                if row_cert_id != cert_id
            ]
            reduced_rhs = [
                value
                for value, row_cert_id in zip(rhs, row_cert_indices)
                if row_cert_id != cert_id
            ]
            cross = derive_variable(reduced_rows, reduced_rhs, target_pos, order)
            cross_checks += 1
            item["cross_certificate_derivable_without_own_forms"] = bool(cross.get("derivable"))
            item["cross_certificate_derived_secret"] = cross.get("value")
        else:
            cross = {"derivable": False, "value": None}
            item["cross_certificate_derivable_without_own_forms"] = None
            item["cross_certificate_derived_secret"] = None
        if item["cross_certificate_derivable_without_own_forms"]:
            cross_certificate_recoveries += 1
        if item["derived_matches_expected_secret"]:
            local_matches += 1
        target_derivations.append(item)
    factor_derivations = []
    for offset, name in enumerate(factor_vars):
        derived = derive_variable(rows, rhs, len(target_vars) + offset, order)
        if derived.get("derivable"):
            factor_derivations.append({"factor_variable": name, "value": derived.get("value")})
    clause_counts = Counter(
        str(cert.get("clause") or (cert.get("selected") or {}).get("clause") or "none")
        for cert in system["certificates"]
    )
    target_derivation_skipped_count = max(0, len(system["certificates"]) - target_checks)
    cross_certificate_skipped_count = max(0, len(system["certificates"]) - cross_checks)
    return {
        "certificate_count": len(system["certificates"]),
        "claim_status": (
            "LOCAL_TARGET_RECOVERY_ONLY_TARGET_DESCENT_OPEN"
            if target_derivation_skipped_count == 0
            and cross_certificate_skipped_count == 0
            and local_matches == len(system["certificates"])
            and not factor_derivations
            and cross_certificate_recoveries == 0
            else "TARGET_DESCENT_SIGNALS_NEED_REVIEW"
        ),
        "clause_counts": dict(sorted(clause_counts.items())),
        "cross_certificate_recoveries": cross_certificate_recoveries,
        "cross_certificate_check_count": cross_checks,
        "cross_certificate_skipped_count": cross_certificate_skipped_count,
        "factor_variable_count": len(factor_vars),
        "factor_variables_derivable_count": len(factor_derivations),
        "factor_variables_derivable_sample": factor_derivations[:10],
        "local_target_recovery_count": local_matches,
        "matrix_rank": rank,
        "order": order,
        "row_count": len(rows),
        "target_derivations": target_derivations,
        "target_derivation_check_count": target_checks,
        "target_derivation_skipped_count": target_derivation_skipped_count,
        "target_variable_count": len(target_vars),
        "underdetermined_dimension": len(variables) - rank,
        "variable_count": len(variables),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificates", required=True, help="Comma-separated certificate JSON files.")
    parser.add_argument(
        "--max-target-derivations",
        type=int,
        default=None,
        help="Bound per-target derivation checks for large banks; default checks all targets.",
    )
    parser.add_argument(
        "--max-cross-certificate-checks",
        type=int,
        default=None,
        help="Bound expensive own-certificate removal checks; default checks all targets.",
    )
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = [Path(item) for item in args.certificates.split(",") if item.strip()]
    certificates = load_certificates(paths)
    if not certificates:
        raise ValueError("no certificates loaded")
    order_values = sorted({int_value(cert.get("order")) for cert in certificates})
    order_audits = {
        str(order): audit_order(
            certificates,
            order,
            max_target_derivations=args.max_target_derivations,
            max_cross_certificate_checks=args.max_cross_certificate_checks,
        )
        for order in order_values
    }
    total_factor_derivable = sum(
        audit["factor_variables_derivable_count"] for audit in order_audits.values()
    )
    total_cross = sum(audit["cross_certificate_recoveries"] for audit in order_audits.values())
    total_local = sum(audit["local_target_recovery_count"] for audit in order_audits.values())
    total_target_checks = sum(audit["target_derivation_check_count"] for audit in order_audits.values())
    total_target_skipped = sum(
        audit["target_derivation_skipped_count"] for audit in order_audits.values()
    )
    total_cross_checks = sum(audit["cross_certificate_check_count"] for audit in order_audits.values())
    total_cross_skipped = sum(
        audit["cross_certificate_skipped_count"] for audit in order_audits.values()
    )
    payload = {
        "artifacts": {"certificates": [str(path) for path in paths]},
        "claim_status": (
            "NEGATIVE_RESULT_LOCAL_RECOVERY_NOT_TARGET_DESCENT"
            if total_target_skipped == 0
            and total_cross_skipped == 0
            and total_local == len(certificates)
            and total_factor_derivable == 0
            and total_cross == 0
            else "PARTIAL_TARGET_DESCENT_AUDIT_NEEDS_REVIEW"
            if total_target_skipped or total_cross_skipped
            else "OPEN_TARGET_DESCENT_SIGNALS_NEED_REVIEW"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: linear system assumes a shared factor-column namespace within each group order.",
            "NEGATIVE RESULT scope: this rules out reusable target descent for the current exported bank shape, not for all representations or future descent rules.",
            "OPEN: a future descent rule could add target-independent factor-base relations or map a fresh public target into a certified order-specific source row.",
        ],
        "order_audits": order_audits,
        "schema": "ecdlp.low_term_total2_certificate_bank_linear_descent_audit.v1",
        "summary": {
            "certificate_count": len(certificates),
            "cross_certificate_check_count": total_cross_checks,
            "cross_certificate_recoveries": total_cross,
            "cross_certificate_skipped_count": total_cross_skipped,
            "factor_variables_derivable_count": total_factor_derivable,
            "local_target_recovery_count": total_local,
            "order_count": len(order_audits),
            "target_descent_implemented": False,
            "target_derivation_check_count": total_target_checks,
            "target_derivation_skipped_count": total_target_skipped,
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
