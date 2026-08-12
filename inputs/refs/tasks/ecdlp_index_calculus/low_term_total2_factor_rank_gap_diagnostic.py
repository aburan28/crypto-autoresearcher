#!/usr/bin/env python3
"""Diagnose missing target-eliminated factor-rank dimensions.

The marginal scorer says whether a certificate increases factor rank, but it
does not explain why many verified rows are duplicates.  This diagnostic uses
the same target-eliminated factor rows as the bank/scorer, reduces candidate
relations modulo the current base rowspace, and groups candidates by quotient
residual signature.  A nonzero residual signature is the concrete missing
factor-rank direction a candidate touches; repeated signatures explain why
greedy rank can stay flat while raw relation count grows.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SCORER = STATE_DIR / "low_term_total2_factor_rank_candidate_scorer_target67_multibranch_live_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_factor_rank_gap_diagnostic_target67_multibranch_live_probe.json"


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


def pad(values: list[int], length: int) -> list[int]:
    return values + [0] * max(0, length - len(values))


def selected_info(cert: dict[str, Any]) -> dict[str, Any]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    rho = int_value(selected.get("rho"))
    shared_ops = selected.get("shared_ops")
    generated_plus_shared = None
    if shared_ops is not None:
        generated_plus_shared = int_value(shared_ops) + 1
    return {
        "artifact": cert.get("_artifact"),
        "artifact_offset": int_value(cert.get("_artifact_offset")),
        "clause": cert.get("clause") or selected.get("clause"),
        "direct_ops_over_rho": selected.get("direct_ops_over_rho"),
        "expected_secret": cert.get("expected_secret"),
        "forms_count": int_value(cert.get("forms_count")),
        "generated_plus_shared_ops_over_rho": (
            round(float(generated_plus_shared) / float(rho), 8)
            if generated_plus_shared is not None and rho
            else None
        ),
        "order": int_value(cert.get("order")),
        "rank": int_value(cert.get("rank")),
        "selector": selected.get("selector"),
        "shared_ops_over_rho": selected.get("shared_ops_over_rho"),
        "target": selected.get("target"),
        "top_k": int_value(selected.get("top_k")),
        "transfer_index": int_value(selected.get("transfer_index")),
        "window": cert.get("window"),
    }


def rref_rows(rows: list[list[int]], modulus: int) -> tuple[list[list[int]], list[int]]:
    work = [[value % modulus for value in row] for row in rows if any(value % modulus for value in row)]
    if not work:
        return [], []
    row_count = len(work)
    col_count = len(work[0])
    rank = 0
    pivots: list[int] = []
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if work[row][col] % modulus:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inv = pow(work[rank][col] % modulus, -1, modulus)
        work[rank] = [(value * inv) % modulus for value in work[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = work[row][col] % modulus
            if factor:
                work[row] = [
                    (work[row][idx] - factor * work[rank][idx]) % modulus
                    for idx in range(col_count)
                ]
        pivots.append(col)
        rank += 1
        if rank == row_count:
            break
    return work[:rank], pivots


def reduce_row(row: list[int], basis: list[list[int]], pivots: list[int], modulus: int) -> list[int]:
    residual = [value % modulus for value in row]
    for basis_row, pivot in zip(basis, pivots):
        factor = residual[pivot] % modulus
        if factor:
            residual = [
                (residual[idx] - factor * basis_row[idx]) % modulus
                for idx in range(len(residual))
            ]
    return residual


def normalize_vector(row: list[int], modulus: int) -> tuple[int, ...] | None:
    reduced = [value % modulus for value in row]
    for value in reduced:
        if value % modulus:
            inv = pow(value % modulus, -1, modulus)
            return tuple((item * inv) % modulus for item in reduced)
    return None


def factor_count_for_order(certificates: list[dict[str, Any]], order: int) -> int:
    count = 0
    for cert in certificates:
        if int_value(cert.get("order")) != order:
            continue
        forms = [form for form in (cert.get("forms") or []) if isinstance(form, dict)]
        count = max(count, max([max(0, len(form.get("coeffs") or []) - 1) for form in forms] or [0]))
    return count


def relation_rows(cert: dict[str, Any], factor_count: int) -> list[dict[str, Any]]:
    order = int_value(cert.get("order"))
    rows = []
    seen = set()
    for relation in factor_bank.target_eliminated_rows(cert):
        if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
            continue
        coeffs = pad([int_value(value) % order for value in relation.get("canonical_coeffs") or []], factor_count)
        rhs = int_value(relation.get("canonical_rhs")) % order
        key = (tuple(coeffs), rhs)
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "coeffs": coeffs,
                "factor_support": [idx for idx, coeff in enumerate(coeffs) if coeff % order],
                "rhs": rhs,
            }
        )
    return rows


def unique_relation_rows(certificates: list[dict[str, Any]], order: int, factor_count: int) -> list[dict[str, Any]]:
    rows_by_key: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
    for cert in certificates:
        if int_value(cert.get("order")) != order:
            continue
        for row in relation_rows(cert, factor_count):
            key = (tuple(row["coeffs"]), int_value(row["rhs"]) % order)
            rows_by_key.setdefault(key, row)
    return list(rows_by_key.values())


def parse_path_list(value: str | None) -> list[Path]:
    if not value:
        return []
    return [Path(item) for item in value.split(",") if item.strip()]


def paths_from_scorer(path: Path) -> tuple[list[Path], list[Path]]:
    payload = load_json(path)
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
    base = [Path(item) for item in artifacts.get("base_certificates") or []]
    candidates = [Path(item) for item in artifacts.get("candidate_certificates") or []]
    return base, candidates


def diagnose_order(
    order: int,
    base_certificates: list[dict[str, Any]],
    candidate_certificates: list[dict[str, Any]],
) -> dict[str, Any]:
    all_order_certs = [
        cert for cert in base_certificates + candidate_certificates if int_value(cert.get("order")) == order
    ]
    factor_count = factor_count_for_order(all_order_certs, order)
    base_rows = unique_relation_rows(base_certificates, order, factor_count)
    base_matrix = [row["coeffs"] for row in base_rows]
    basis, pivots = rref_rows(base_matrix, order)
    free_columns = [idx for idx in range(factor_count) if idx not in set(pivots)]
    column_counts = Counter()
    for row in base_rows:
        for idx in row["factor_support"]:
            column_counts[idx] += 1
    residual_groups: dict[tuple[int, ...], dict[str, Any]] = {}
    candidate_reports = []
    for cert in candidate_certificates:
        if int_value(cert.get("order")) != order:
            continue
        candidate_rows = relation_rows(cert, factor_count)
        residual_signatures: list[tuple[int, ...]] = []
        residual_samples = []
        for row in candidate_rows:
            residual = reduce_row(row["coeffs"], basis, pivots, order)
            normalized = normalize_vector(residual, order)
            if normalized is None:
                continue
            residual_signatures.append(normalized)
            residual_samples.append(
                {
                    "free_column_support": [idx for idx in free_columns if residual[idx] % order],
                    "normalized_residual": list(normalized),
                    "residual_support": [idx for idx, value in enumerate(normalized) if value % order],
                }
            )
        residual_rank = 0
        if residual_signatures:
            residual_rank = len(rref_rows([list(signature) for signature in residual_signatures], order)[1])
        info = selected_info(cert)
        report = {
            "candidate": info,
            "candidate_relation_count": len(candidate_rows),
            "nonzero_residual_count": len(residual_signatures),
            "rank_gain_over_base": residual_rank,
            "residual_samples": residual_samples[:4],
        }
        candidate_reports.append(report)
        for signature in set(residual_signatures):
            group = residual_groups.setdefault(
                signature,
                {
                    "candidate_count": 0,
                    "candidate_samples": [],
                    "free_column_support": [idx for idx in free_columns if signature[idx] % order],
                    "residual_support": [idx for idx, value in enumerate(signature) if value % order],
                },
            )
            group["candidate_count"] += 1
            if len(group["candidate_samples"]) < 8:
                group["candidate_samples"].append(info)
    residual_group_list = [
        {"normalized_residual": list(signature), **group}
        for signature, group in residual_groups.items()
    ]
    residual_group_list.sort(
        key=lambda group: (
            -int_value(group.get("candidate_count")),
            len(group.get("free_column_support") or []),
            group.get("free_column_support") or [],
        )
    )
    candidate_reports.sort(
        key=lambda report: (
            -int_value(report.get("rank_gain_over_base")),
            -int_value(report.get("nonzero_residual_count")),
            str((report.get("candidate") or {}).get("artifact")),
        )
    )
    return {
        "base_certificate_count": sum(1 for cert in base_certificates if int_value(cert.get("order")) == order),
        "base_factor_relation_count": len(base_rows),
        "base_rank": len(pivots),
        "candidate_certificate_count": sum(
            1 for cert in candidate_certificates if int_value(cert.get("order")) == order
        ),
        "candidate_reports": candidate_reports[:40],
        "columns_unseen_in_base": [idx for idx in range(factor_count) if column_counts[idx] == 0],
        "deficiency": max(0, factor_count - len(pivots)),
        "factor_column_base_support_count": {
            str(idx): column_counts[idx] for idx in range(factor_count)
        },
        "factor_variable_count": factor_count,
        "free_columns": free_columns,
        "pivot_columns": pivots,
        "residual_group_count": len(residual_group_list),
        "residual_groups": residual_group_list[:20],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scorer-artifact", default=str(DEFAULT_SCORER))
    parser.add_argument("--base-certificates")
    parser.add_argument("--candidate-certificates")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scorer_base, scorer_candidates = paths_from_scorer(Path(args.scorer_artifact))
    base_paths = parse_path_list(args.base_certificates) or scorer_base
    candidate_paths = parse_path_list(args.candidate_certificates) or scorer_candidates
    if not base_paths:
        raise ValueError("no base certificates supplied")
    base_certificates = factor_bank.load_certificates(base_paths)
    candidate_certificates = factor_bank.load_certificates(candidate_paths)
    orders = sorted(
        {
            int_value(cert.get("order"))
            for cert in base_certificates + candidate_certificates
            if int_value(cert.get("order"))
        }
    )
    order_diagnostics = {
        str(order): diagnose_order(order, base_certificates, candidate_certificates)
        for order in orders
    }
    rank_gap_orders = [
        order for order, diag in order_diagnostics.items() if int_value(diag.get("deficiency")) > 0
    ]
    residual_groups_total = sum(int_value(diag.get("residual_group_count")) for diag in order_diagnostics.values())
    rank_gain_candidates = sum(
        1
        for diag in order_diagnostics.values()
        for report in diag.get("candidate_reports") or []
        if int_value(report.get("rank_gain_over_base")) > 0
    )
    payload = {
        "artifacts": {
            "base_certificates": [str(path) for path in base_paths],
            "candidate_certificates": [str(path) for path in candidate_paths],
            "scorer_artifact": str(args.scorer_artifact),
        },
        "claim_status": (
            "MISSING_FACTOR_RANK_DIMENSIONS_IDENTIFIED"
            if rank_gap_orders
            else "NO_FACTOR_RANK_GAP_IDENTIFIED"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: quotient residuals are computed in the verifier's current factor-column namespace.",
            "HEURISTIC: residual signatures guide collector design; they are not a complete target descent or deployed-curve speedup claim.",
        ],
        "order_diagnostics": order_diagnostics,
        "schema": "ecdlp.low_term_total2_factor_rank_gap_diagnostic.v1",
        "summary": {
            "candidate_certificate_count": len(candidate_certificates),
            "order_count": len(order_diagnostics),
            "rank_gap_order_count": len(rank_gap_orders),
            "rank_gain_candidate_report_count": rank_gain_candidates,
            "residual_group_count": residual_groups_total,
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
