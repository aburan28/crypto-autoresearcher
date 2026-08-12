#!/usr/bin/env python3
"""Extract target-eliminated factor-base relations from public certificates.

The q-zero source replay probe asks whether an individual verifier row already
has zero target coefficient.  This audit tests a stronger, active descent
question: given public relation equations

    q_i * secret(Q) + sum_j a_ij log(F_j) = rhs_i mod order,

can pairs of rows from the same certificate eliminate ``secret(Q)`` and leave a
nontrivial factor-only equation?  Such rows are not a complete target descent,
but positive factor-rank growth is a genuine index-calculus signal: it converts
local recovery certificates into reusable order-specific factor-base relations.
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
        if value is None:
            return default
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
    value = sum(coefficients[row] * rhs[row] for row in range(len(rhs))) % modulus
    return {
        "combination_row_count": sum(1 for coefficient in coefficients if coefficient % modulus),
        "derivable": True,
        "value": value,
    }


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


def selected_target(cert: dict[str, Any]) -> str:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    return str(selected.get("target") or "unknown")


def selected_clause(cert: dict[str, Any]) -> str:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    return str(cert.get("clause") or selected.get("clause") or "none")


def pad(values: list[int], length: int) -> list[int]:
    return values + [0] * max(0, length - len(values))


def form_parts(form: dict[str, Any], order: int, factor_count: int) -> tuple[int, list[int], int]:
    coeffs = [int_value(value) % order for value in form.get("coeffs") or []]
    q_coeff = coeffs[0] if coeffs else 0
    factor_coeffs = pad(coeffs[1:], factor_count)
    rhs = int_value(form.get("rhs")) % order
    return q_coeff, factor_coeffs, rhs


def canonical_relation(
    coeffs: list[int],
    rhs: int,
    order: int,
) -> tuple[tuple[int, ...], int] | None:
    reduced = [coeff % order for coeff in coeffs]
    rhs = rhs % order
    for value in reduced:
        if value % order:
            inv = pow(value % order, -1, order)
            return tuple((coeff * inv) % order for coeff in reduced), (rhs * inv) % order
    if rhs % order:
        return tuple(reduced), rhs
    return None


def target_eliminated_rows(cert: dict[str, Any]) -> list[dict[str, Any]]:
    order = int_value(cert.get("order"))
    forms = [form for form in (cert.get("forms") or []) if isinstance(form, dict)]
    factor_count = max(
        [max(0, len(form.get("coeffs") or []) - 1) for form in forms] or [0]
    )
    relations: list[dict[str, Any]] = []
    for left_index, left in enumerate(forms):
        for right_index in range(left_index + 1, len(forms)):
            right = forms[right_index]
            q_left, factors_left, rhs_left = form_parts(left, order, factor_count)
            q_right, factors_right, rhs_right = form_parts(right, order, factor_count)
            # q_right * left - q_left * right eliminates the target coefficient.
            factor_coeffs = [
                (q_right * factors_left[index] - q_left * factors_right[index]) % order
                for index in range(factor_count)
            ]
            rhs = (q_right * rhs_left - q_left * rhs_right) % order
            canonical = canonical_relation(factor_coeffs, rhs, order)
            if canonical is None:
                relations.append(
                    {
                        "certificate_index": int_value(cert.get("_global_index")),
                        "pair": [left_index, right_index],
                        "relation_status": "TRIVIAL_ZERO_RELATION",
                    }
                )
                continue
            coeff_key, canonical_rhs = canonical
            support = [index for index, coeff in enumerate(coeff_key) if coeff % order]
            relations.append(
                {
                    "canonical_coeffs": list(coeff_key),
                    "canonical_rhs": canonical_rhs,
                    "certificate_index": int_value(cert.get("_global_index")),
                    "factor_support_size": len(support),
                    "factor_support": support,
                    "pair": [left_index, right_index],
                    "q_coeffs": [q_left, q_right],
                    "relation_status": (
                        "TARGET_ELIMINATED_FACTOR_RELATION"
                        if support
                        else "INCONSISTENT_ZERO_COEFF_RELATION"
                    ),
                }
            )
    return relations


def audit_order(certificates: list[dict[str, Any]], order: int) -> dict[str, Any]:
    order_certs = [cert for cert in certificates if int_value(cert.get("order")) == order]
    factor_count = 0
    rows_by_key: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
    raw_relations = 0
    trivial_count = 0
    inconsistent_count = 0
    support_sizes: list[int] = []
    source_counts = Counter()
    clause_counts = Counter()
    pair_counts: list[int] = []
    per_certificate_samples = []
    for cert in order_certs:
        forms = [form for form in (cert.get("forms") or []) if isinstance(form, dict)]
        factor_count = max(
            factor_count,
            max([max(0, len(form.get("coeffs") or []) - 1) for form in forms] or [0]),
        )
    for cert in order_certs:
        cert_relations = target_eliminated_rows(cert)
        pair_counts.append(len(cert_relations))
        emitted_for_cert = 0
        for relation in cert_relations:
            status = relation["relation_status"]
            if status == "TRIVIAL_ZERO_RELATION":
                trivial_count += 1
                continue
            if status == "INCONSISTENT_ZERO_COEFF_RELATION":
                inconsistent_count += 1
                continue
            raw_relations += 1
            coeffs = pad([int_value(value) % order for value in relation["canonical_coeffs"]], factor_count)
            key = (tuple(coeffs), int_value(relation["canonical_rhs"]) % order)
            support_sizes.append(int_value(relation.get("factor_support_size")))
            source_counts[selected_target(cert)] += 1
            clause_counts[selected_clause(cert)] += 1
            emitted_for_cert += 1
            rows_by_key.setdefault(
                key,
                {
                    "canonical_coeffs": coeffs,
                    "canonical_rhs": key[1],
                    "example": {
                        "artifact": cert.get("_artifact"),
                        "certificate_index": int_value(cert.get("_global_index")),
                        "clause": selected_clause(cert),
                        "pair": relation.get("pair"),
                        "target": selected_target(cert),
                        "transfer_index": int_value((cert.get("selected") or {}).get("transfer_index")),
                        "window": cert.get("window"),
                    },
                    "factor_support": relation.get("factor_support"),
                    "factor_support_size": relation.get("factor_support_size"),
                    "multiplicity": 0,
                },
            )
            rows_by_key[key]["multiplicity"] += 1
        if emitted_for_cert and len(per_certificate_samples) < 12:
            selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
            per_certificate_samples.append(
                {
                    "certificate_index": int_value(cert.get("_global_index")),
                    "emitted_factor_relation_count": emitted_for_cert,
                    "target": selected_target(cert),
                    "transfer_index": int_value(selected.get("transfer_index")),
                    "window": cert.get("window"),
                }
            )
    unique_rows = list(rows_by_key.values())
    matrix = [row["canonical_coeffs"] for row in unique_rows]
    rhs = [int_value(row["canonical_rhs"]) % order for row in unique_rows]
    rank = rank_mod(matrix, order)
    augmented_rank = rank_mod([row + [rhs[index]] for index, row in enumerate(matrix)], order)
    derivable = []
    for index in range(factor_count):
        derived = derive_variable(matrix, rhs, index, order)
        if derived.get("derivable"):
            derivable.append(
                {
                    "factor_variable": f"F:{order}:column={index}",
                    "value": derived.get("value"),
                    "combination_row_count": derived.get("combination_row_count"),
                }
            )
    return {
        "augmented_rank": augmented_rank,
        "certificate_count": len(order_certs),
        "claim_status": (
            "FACTOR_BASE_FULL_RANK_TARGET_DESCENT_CANDIDATE"
            if factor_count and rank >= factor_count
            else "FACTOR_BASE_RANK_GROWTH_TARGET_DESCENT_OPEN"
            if rank > 0
            else "NO_TARGET_ELIMINATED_FACTOR_RELATIONS"
        ),
        "clause_counts": dict(sorted(clause_counts.items())),
        "deficiency": max(0, factor_count - rank),
        "factor_relation_count": raw_relations,
        "factor_support_size": stat(support_sizes),
        "factor_variable_count": factor_count,
        "factor_variables_derivable_count": len(derivable),
        "factor_variables_derivable_sample": derivable[:10],
        "full_rank": bool(factor_count and rank >= factor_count),
        "inconsistent_zero_coeff_relation_count": inconsistent_count,
        "matrix_consistent": augmented_rank == rank,
        "per_certificate_factor_relation_count": stat(pair_counts),
        "per_certificate_samples": per_certificate_samples,
        "rank": rank,
        "source_target_counts": dict(sorted(source_counts.items())),
        "trivial_zero_relation_count": trivial_count,
        "unique_factor_relation_count": len(unique_rows),
        "unique_relation_samples": unique_rows[:10],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificates", required=True, help="Comma-separated certificate JSON files.")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = [Path(item) for item in args.certificates.split(",") if item.strip()]
    certificates = load_certificates(paths)
    if not certificates:
        raise ValueError("no certificates loaded")
    order_values = sorted({int_value(cert.get("order")) for cert in certificates})
    order_audits = {str(order): audit_order(certificates, order) for order in order_values}
    total_unique = sum(audit["unique_factor_relation_count"] for audit in order_audits.values())
    total_rank = sum(audit["rank"] for audit in order_audits.values())
    total_deficiency = sum(audit["deficiency"] for audit in order_audits.values())
    total_derivable = sum(audit["factor_variables_derivable_count"] for audit in order_audits.values())
    full_rank_orders = sum(1 for audit in order_audits.values() if audit["full_rank"])
    payload = {
        "artifacts": {"certificates": [str(path) for path in paths]},
        "claim_status": (
            "TARGET_ELIMINATED_FACTOR_RELATIONS_FOUND_TARGET_DESCENT_OPEN"
            if total_rank > 0
            else "NEGATIVE_RESULT_NO_TARGET_ELIMINATED_FACTOR_RELATIONS"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: factor columns are the verifier's current order-specific factor-base namespace.",
            "HEURISTIC: rank growth is treated as an index-calculus signal, not a deployed-curve speedup.",
            "OPEN: full target descent still requires enough factor rank or a public fresh-target mapping, plus complete cost comparison against Pollard rho.",
        ],
        "order_audits": order_audits,
        "schema": "ecdlp.low_term_total2_target_eliminated_factor_relation_bank.v1",
        "summary": {
            "certificate_count": len(certificates),
            "factor_variables_derivable_count": total_derivable,
            "full_rank_order_count": full_rank_orders,
            "order_count": len(order_audits),
            "target_descent_implemented": False,
            "total_deficiency": total_deficiency,
            "total_factor_rank": total_rank,
            "total_unique_factor_relation_count": total_unique,
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
