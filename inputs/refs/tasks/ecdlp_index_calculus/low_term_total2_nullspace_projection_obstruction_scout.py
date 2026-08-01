#!/usr/bin/env python3
"""Explain why target-eliminated rows miss the remaining nullspace direction.

The deficiency-direction scorer reports whether a candidate certificate has a
nonzero projection onto the current factor-rank nullspace.  This companion
scout keeps the failed rows too, so generator work can see whether a row missed
because the target column never appeared or because symmetric coefficients
cancelled against the null vector.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_deficiency_direction_scorer as deficiency
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_nullspace_projection_obstruction_scout_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    return factor_bank.int_value(value, default)


def parse_paths(raw: str | None) -> list[Path]:
    if not raw:
        return []
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def signed(value: int, modulus: int) -> int:
    value %= modulus
    if value > modulus // 2:
        return value - modulus
    return value


def support(values: list[int], modulus: int) -> list[int]:
    return [idx for idx, value in enumerate(values) if value % modulus]


def compact_candidate(cert: dict[str, Any]) -> dict[str, Any]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    return {
        "artifact": cert.get("_artifact"),
        "artifact_offset": int_value(cert.get("_artifact_offset")),
        "direct_ops_over_rho": selected.get("direct_ops_over_rho"),
        "forms_count": int_value(cert.get("forms_count")),
        "order": int_value(cert.get("order")),
        "rank": int_value(cert.get("rank")),
        "selector": selected.get("selector"),
        "target": selected.get("target"),
        "top_k": int_value(selected.get("top_k")),
        "transfer_index": int_value(selected.get("transfer_index")),
        "window": cert.get("window"),
    }


def form_infos(cert: dict[str, Any], factor_count: int) -> list[dict[str, Any]]:
    order = int_value(cert.get("order"))
    infos: list[dict[str, Any]] = []
    for index, form in enumerate(form for form in (cert.get("forms") or []) if isinstance(form, dict)):
        q_coeff, factor_coeffs, rhs = factor_bank.form_parts(form, order, factor_count)
        infos.append(
            {
                "factor_support": support(factor_coeffs, order),
                "index": index,
                "q_coeff": q_coeff,
                "rhs": rhs,
            }
        )
    return infos


def contribution_report(row: list[int], basis: dict[str, Any], modulus: int) -> dict[str, Any]:
    vector = [int_value(value) % modulus for value in basis.get("vector") or []]
    length = min(len(row), len(vector))
    contributions = []
    projection = 0
    for index in range(length):
        coeff = row[index] % modulus
        null_coeff = vector[index] % modulus
        if not coeff or not null_coeff:
            continue
        contribution = (coeff * null_coeff) % modulus
        projection = (projection + contribution) % modulus
        contributions.append(
            {
                "column": index,
                "coefficient": coeff,
                "coefficient_signed": signed(coeff, modulus),
                "contribution": contribution,
                "contribution_signed": signed(contribution, modulus),
                "null_coefficient": null_coeff,
                "null_coefficient_signed": signed(null_coeff, modulus),
            }
        )
    pairwise_cancellations = []
    for left_pos, left in enumerate(contributions):
        for right in contributions[left_pos + 1 :]:
            if (left["null_coefficient"] + right["null_coefficient"]) % modulus != 0:
                continue
            if left["coefficient"] % modulus != right["coefficient"] % modulus:
                continue
            pairwise_cancellations.append(
                {
                    "columns": [left["column"], right["column"]],
                    "coefficient": left["coefficient"],
                    "coefficient_signed": left["coefficient_signed"],
                    "null_coefficients_signed": [
                        left["null_coefficient_signed"],
                        right["null_coefficient_signed"],
                    ],
                }
            )
    return {
        "basis_free_column": int_value(basis.get("free_column")),
        "basis_support": basis.get("support") or [],
        "contributions": contributions,
        "pairwise_equal_opposite_cancellations": pairwise_cancellations,
        "projection": projection,
        "projection_signed": signed(projection, modulus),
    }


def relation_report(
    cert: dict[str, Any],
    relation: dict[str, Any],
    basis_rows: list[dict[str, Any]],
    factor_count: int,
    modulus: int,
) -> dict[str, Any]:
    row = factor_bank.pad(
        [int_value(value) % modulus for value in relation.get("canonical_coeffs") or []],
        factor_count,
    )
    projections = [contribution_report(row, basis, modulus) for basis in basis_rows]
    pair = [int_value(item) for item in relation.get("pair") or []]
    forms = form_infos(cert, factor_count)
    left = forms[pair[0]] if len(pair) == 2 and 0 <= pair[0] < len(forms) else {}
    right = forms[pair[1]] if len(pair) == 2 and 0 <= pair[1] < len(forms) else {}
    has_nonzero_projection = any(int_value(item.get("projection")) % modulus for item in projections)
    null_support = set()
    for basis in basis_rows:
        null_support.update(int_value(item) for item in basis.get("support") or [])
    row_support = support(row, modulus)
    touches_null_support = bool(set(row_support) & null_support)
    has_pairwise_cancellation = any(
        item.get("pairwise_equal_opposite_cancellations")
        for item in projections
    )
    if has_nonzero_projection:
        status = "NONZERO_NULLSPACE_PROJECTION"
    elif touches_null_support and has_pairwise_cancellation:
        status = "ZERO_PROJECTION_BY_EQUAL_OPPOSITE_CANCELLATION"
    elif touches_null_support:
        status = "ZERO_PROJECTION_OTHER_NULLSUPPORT"
    else:
        status = "NO_NULLSPACE_SUPPORT"
    return {
        "candidate": compact_candidate(cert),
        "canonical_rhs": int_value(relation.get("canonical_rhs")) % modulus,
        "factor_support": row_support,
        "left_form": {
            "factor_support": left.get("factor_support") or [],
            "index": left.get("index"),
            "q_coeff": left.get("q_coeff"),
        },
        "pair": pair,
        "projections": projections,
        "q_coeffs": [int_value(item) % modulus for item in relation.get("q_coeffs") or []],
        "right_form": {
            "factor_support": right.get("factor_support") or [],
            "index": right.get("index"),
            "q_coeff": right.get("q_coeff"),
        },
        "status": status,
    }


def analyze(
    frontier_certificates: list[dict[str, Any]],
    candidate_certificates: list[dict[str, Any]],
    order: int,
    sample_limit: int,
) -> dict[str, Any]:
    frontier_rows, frontier_rhs, _frontier_rows_by_key, factor_count = deficiency.row_vectors(
        frontier_certificates,
        order,
    )
    rref_rows, pivot_columns = deficiency.rref_mod(frontier_rows, order)
    free_columns, null_basis = deficiency.nullspace_basis(
        rref_rows,
        pivot_columns,
        factor_count,
        order,
    )
    augmented_rank = factor_bank.rank_mod(
        [row + [frontier_rhs[index]] for index, row in enumerate(frontier_rows)],
        order,
    )
    status_counts: Counter[str] = Counter()
    relation_reports = []
    candidate_reports = []
    for cert in candidate_certificates:
        if int_value(cert.get("order")) != order:
            continue
        cert_status_counts: Counter[str] = Counter()
        for relation in factor_bank.target_eliminated_rows(cert):
            if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
                continue
            report = relation_report(cert, relation, null_basis, factor_count, order)
            status = str(report.get("status"))
            status_counts[status] += 1
            cert_status_counts[status] += 1
            if len(relation_reports) < sample_limit or status == "NONZERO_NULLSPACE_PROJECTION":
                relation_reports.append(report)
        if cert_status_counts:
            candidate = compact_candidate(cert)
            candidate_reports.append(
                {
                    "candidate": candidate,
                    "status_counts": dict(sorted(cert_status_counts.items())),
                }
            )
    nonzero = status_counts.get("NONZERO_NULLSPACE_PROJECTION", 0)
    cancellation = status_counts.get("ZERO_PROJECTION_BY_EQUAL_OPPOSITE_CANCELLATION", 0)
    if nonzero:
        action = "PROMOTE_NONZERO_NULLSPACE_PROJECTION_ROWS"
        claim_status = "NONZERO_NULLSPACE_PROJECTION_ROWS_FOUND"
    elif cancellation:
        action = "BREAK_NULLSPACE_SYMMETRY_WITH_ASYMMETRIC_FORM_PAIRS"
        claim_status = "NEGATIVE_RESULT_NULLSPACE_PROJECTION_CANCELS_BY_SYMMETRY"
    else:
        action = "GENERATE_FORMS_TOUCHING_NULLSPACE_SUPPORT"
        claim_status = "NEGATIVE_RESULT_NO_NULLSPACE_PROJECTION_ROWS"
    return {
        "candidate_certificate_count": sum(
            1 for cert in candidate_certificates if int_value(cert.get("order")) == order
        ),
        "candidate_reports": candidate_reports[:50],
        "claim_status": claim_status,
        "frontier": {
            "augmented_rank": augmented_rank,
            "deficiency": max(0, factor_count - len(pivot_columns)),
            "factor_variable_count": factor_count,
            "free_columns": free_columns,
            "nullspace_basis": null_basis,
            "order": order,
            "pivot_columns": pivot_columns,
            "rank": len(pivot_columns),
            "unique_factor_relation_count": len(frontier_rows),
        },
        "relation_reports": relation_reports[: max(sample_limit, 0)],
        "status_counts": dict(sorted(status_counts.items())),
        "work_order": {
            "action": action,
            "rationale": (
                "nonzero nullspace rows exist"
                if nonzero
                else "equal coefficients on opposite-signed nullspace columns cancel the projection"
                if cancellation
                else "candidate rows do not reach the nullspace support"
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier-certificates", required=True)
    parser.add_argument("--candidate-certificates", required=True)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--sample-limit", type=int, default=20)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frontier_paths = parse_paths(args.frontier_certificates)
    candidate_paths = parse_paths(args.candidate_certificates)
    frontier_certificates = factor_bank.load_certificates(frontier_paths)
    candidate_certificates = factor_bank.load_certificates(candidate_paths)
    report = analyze(
        frontier_certificates,
        candidate_certificates,
        int_value(args.order, 11779),
        max(0, int_value(args.sample_limit, 20)),
    )
    payload = {
        "artifacts": {
            "candidate_certificates": [str(path) for path in candidate_paths],
            "frontier_certificates": [str(path) for path in frontier_paths],
        },
        "claim_status": report["claim_status"],
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: projections are measured in the current factor-column rowspace.",
            "NO SPEEDUP CLAIM: this scout explains a failed rank-extension gate.",
        ],
        "order_report": report,
        "parameters": {
            "order": int_value(args.order, 11779),
            "sample_limit": max(0, int_value(args.sample_limit, 20)),
        },
        "schema": "ecdlp.low_term_total2_nullspace_projection_obstruction_scout.v1",
        "summary": {
            "candidate_certificate_count": report["candidate_certificate_count"],
            "claim_status": report["claim_status"],
            "frontier_rank": report["frontier"]["rank"],
            "frontier_deficiency": report["frontier"]["deficiency"],
            "status_counts": report["status_counts"],
            "work_order": report["work_order"],
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
