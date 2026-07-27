#!/usr/bin/env python3
"""Score public certificates against the remaining factor-rank deficiency.

The marginal rank scorer finds a greedy frontier from a base certificate bank.
This audit starts *after* that greedy frontier and asks whether the remaining
candidate certificates contain any target-eliminated factor row outside the
current rowspace.  If not, the result is a scoped negative for the current
branch family, not for ECDLP or target descent generally.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    return factor_bank.int_value(value, default)


def parse_csv_paths(raw: str | None) -> list[Path]:
    if not raw:
        return []
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def scorer_paths(path: Path) -> tuple[list[Path], list[Path]]:
    payload = load_json(path)
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
    base_paths = [
        Path(item)
        for key in ("base_certificates", "frontier_certificates")
        for item in artifacts.get(key) or []
    ]
    greedy_paths = [
        Path((item.get("candidate") or {}).get("artifact"))
        for item in payload.get("greedy_selected") or []
        if isinstance(item, dict) and (item.get("candidate") or {}).get("artifact")
    ]
    candidate_paths = [Path(item) for item in artifacts.get("candidate_certificates") or []]
    return base_paths + greedy_paths, candidate_paths


def row_vectors(
    certificates: list[dict[str, Any]],
    order: int,
) -> tuple[list[list[int]], list[int], dict[tuple[tuple[int, ...], int], dict[str, Any]], int]:
    order_certs = [cert for cert in certificates if int_value(cert.get("order")) == order]
    factor_count = 0
    for cert in order_certs:
        for form in cert.get("forms") or []:
            if isinstance(form, dict):
                factor_count = max(factor_count, max(0, len(form.get("coeffs") or []) - 1))

    rows_by_key: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
    for cert in order_certs:
        for relation in factor_bank.target_eliminated_rows(cert):
            if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
                continue
            coeffs = factor_bank.pad(
                [int_value(value) % order for value in relation.get("canonical_coeffs") or []],
                factor_count,
            )
            rhs = int_value(relation.get("canonical_rhs")) % order
            key = (tuple(coeffs), rhs)
            selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
            rows_by_key.setdefault(
                key,
                {
                    "artifact": cert.get("_artifact"),
                    "artifact_offset": int_value(cert.get("_artifact_offset")),
                    "factor_support": [idx for idx, coeff in enumerate(coeffs) if coeff % order],
                    "rhs": rhs,
                    "target": selected.get("target"),
                    "transfer_index": int_value(selected.get("transfer_index")),
                    "window": cert.get("window"),
                },
            )
    rows = [list(coeffs) for coeffs, _rhs in rows_by_key]
    rhs_values = [rhs for _coeffs, rhs in rows_by_key]
    return rows, rhs_values, rows_by_key, factor_count


def rref_mod(matrix: list[list[int]], modulus: int) -> tuple[list[list[int]], list[int]]:
    rows = [row[:] for row in matrix if any(value % modulus for value in row)]
    if not rows:
        return [], []
    row_count = len(rows)
    col_count = len(rows[0])
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
                    for idx in range(col_count)
                ]
        pivots.append(col)
        rank += 1
        if rank == row_count:
            break
    return rows[:rank], pivots


def nullspace_basis(
    rref_rows: list[list[int]],
    pivot_columns: list[int],
    col_count: int,
    modulus: int,
) -> tuple[list[int], list[dict[str, Any]]]:
    pivot_set = set(pivot_columns)
    free_columns = [col for col in range(col_count) if col not in pivot_set]
    basis: list[dict[str, Any]] = []
    for free_col in free_columns:
        vector = [0] * col_count
        vector[free_col] = 1
        for row_index, pivot_col in enumerate(pivot_columns):
            vector[pivot_col] = (-rref_rows[row_index][free_col]) % modulus
        basis.append(
            {
                "free_column": free_col,
                "support": [idx for idx, value in enumerate(vector) if value % modulus],
                "vector": vector,
            }
        )
    return free_columns, basis


def dot_mod(left: list[int], right: list[int], modulus: int) -> int:
    return sum((left[idx] % modulus) * (right[idx] % modulus) for idx in range(len(left))) % modulus


def branch_name(path: str | None) -> str:
    if not path:
        return "unknown"
    name = Path(path).name
    match = re.match(r"low_term_total2_relation_equation_certificate_target67_(.+)_\d+_\d+_probe\.json$", name)
    if match:
        return match.group(1)
    return name


def compact_certificate(cert: dict[str, Any]) -> dict[str, Any]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    artifact = cert.get("_artifact")
    return {
        "artifact": artifact,
        "artifact_offset": int_value(cert.get("_artifact_offset")),
        "branch": branch_name(artifact),
        "expected_secret": cert.get("expected_secret"),
        "forms_count": int_value(cert.get("forms_count")),
        "rank": int_value(cert.get("rank")),
        "selector": selected.get("selector"),
        "shared_ops_over_rho": selected.get("shared_ops_over_rho"),
        "target": selected.get("target"),
        "top_k": int_value(selected.get("top_k")),
        "transfer_index": int_value(selected.get("transfer_index")),
        "window": cert.get("window"),
    }


def score_candidate(
    cert: dict[str, Any],
    order: int,
    frontier_keys: set[tuple[tuple[int, ...], int]],
    free_columns: list[int],
    null_basis: list[dict[str, Any]],
) -> dict[str, Any]:
    rows, _rhs, rows_by_key, factor_count = row_vectors([cert], order)
    nonzero_projection_count = 0
    projection_rows: list[list[int]] = []
    projection_samples: list[dict[str, Any]] = []
    free_touch_columns: set[int] = set()
    for row_index, row in enumerate(rows):
        projection = [
            dot_mod(row, basis["vector"], order)
            for basis in null_basis
        ]
        projection_rows.append(projection)
        if any(value % order for value in projection):
            nonzero_projection_count += 1
            if len(projection_samples) < 5:
                projection_samples.append(
                    {
                        "projection": projection,
                        "row_index": row_index,
                        "support": [idx for idx, coeff in enumerate(row) if coeff % order],
                    }
                )
        free_touch_columns.update(
            idx
            for row in rows
            for idx, coeff in enumerate(row)
            if coeff % order and idx in free_columns
        )
    candidate_rank = factor_bank.rank_mod(projection_rows, order) if projection_rows else 0
    unique_new = sum(1 for key in rows_by_key if key not in frontier_keys)
    compact = compact_certificate(cert)
    compact.update(
        {
            "candidate_factor_column_count": factor_count,
            "free_column_touch_count": len(free_touch_columns),
            "free_columns_touched": sorted(free_touch_columns),
            "nonzero_null_projection_count": nonzero_projection_count,
            "projection_samples": projection_samples,
            "rank_gain_after_frontier": candidate_rank,
            "target_eliminated_row_count": len(rows),
            "unique_relation_gain_after_frontier": unique_new,
        }
    )
    return compact


def summarize_branch(scores: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for score in scores:
        grouped[str(score.get("branch"))].append(score)
    summary = {}
    for branch, rows in grouped.items():
        summary[branch] = {
            "candidate_count": len(rows),
            "free_touch_candidate_count": sum(1 for row in rows if int_value(row.get("free_column_touch_count")) > 0),
            "max_free_column_touch_count": max([int_value(row.get("free_column_touch_count")) for row in rows] or [0]),
            "nonzero_null_projection_candidate_count": sum(
                1 for row in rows if int_value(row.get("nonzero_null_projection_count")) > 0
            ),
            "rank_extension_candidate_count": sum(
                1 for row in rows if int_value(row.get("rank_gain_after_frontier")) > 0
            ),
            "unique_relation_gain_candidate_count": sum(
                1 for row in rows if int_value(row.get("unique_relation_gain_after_frontier")) > 0
            ),
        }
    return dict(sorted(summary.items()))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scorer", help="Existing marginal-rank scorer artifact to use for paths.")
    parser.add_argument("--frontier-certificates", help="Comma-separated base/frontier certificate artifacts.")
    parser.add_argument("--candidate-certificates", help="Comma-separated candidate certificate artifacts.")
    parser.add_argument("--order", type=int, default=9887)
    parser.add_argument(
        "--skip-candidate-projections",
        action="store_true",
        help=(
            "Do not reopen all candidate certificates. Use the scorer greedy-stop "
            "condition as the single-certificate no-extender evidence."
        ),
    )
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scorer_payload = load_json(Path(args.scorer)) if args.scorer else None
    frontier_paths = parse_csv_paths(args.frontier_certificates)
    candidate_paths = parse_csv_paths(args.candidate_certificates)
    if scorer_payload is not None:
        scorer_frontier, scorer_candidates = scorer_paths(Path(args.scorer))
        frontier_paths.extend(scorer_frontier)
        candidate_paths.extend(scorer_candidates)

    # Preserve order, remove duplicate paths, and do not score frontier paths as candidates.
    frontier_paths = list(dict.fromkeys(frontier_paths))
    frontier_path_set = {str(path) for path in frontier_paths}
    candidate_paths = [
        path for path in dict.fromkeys(candidate_paths)
        if str(path) not in frontier_path_set
    ]

    frontier_certificates = factor_bank.load_certificates(frontier_paths)
    candidate_certificates = (
        []
        if args.skip_candidate_projections
        else factor_bank.load_certificates(candidate_paths)
    )

    frontier_rows, frontier_rhs, frontier_rows_by_key, factor_count = row_vectors(
        frontier_certificates,
        args.order,
    )
    frontier_rank = factor_bank.rank_mod(frontier_rows, args.order)
    augmented_rank = factor_bank.rank_mod(
        [row + [frontier_rhs[index]] for index, row in enumerate(frontier_rows)],
        args.order,
    )
    rref_rows, pivot_columns = rref_mod(frontier_rows, args.order)
    free_columns, null_basis = nullspace_basis(
        rref_rows,
        pivot_columns,
        factor_count,
        args.order,
    )
    frontier_keys = set(frontier_rows_by_key)
    if args.skip_candidate_projections:
        scores: list[dict[str, Any]] = []
        scorer_summary = (
            scorer_payload.get("summary")
            if isinstance((scorer_payload or {}).get("summary"), dict)
            else {}
        )
        greedy_count = len((scorer_payload or {}).get("greedy_selected") or [])
        candidate_summary = {
            "candidate_certificate_count": len(candidate_paths),
            "free_column_touch_candidate_count": "not_measured",
            "greedy_selected_count": greedy_count,
            "inference": (
                "The scorer greedy loop stops only when every remaining candidate "
                "has rank_gain <= 0 against the current greedy frontier."
            ),
            "max_free_column_touch_count": "not_measured",
            "nonzero_null_projection_candidate_count": "not_measured",
            "rank_extension_candidate_count": 0,
            "rank_extension_evidence": "inferred_from_scorer_greedy_stop",
            "scorer_candidate_count_before_greedy": int_value(scorer_summary.get("candidate_count")),
            "scorer_rank_gain_candidate_count_before_greedy": int_value(
                scorer_summary.get("rank_gain_candidate_count")
            ),
            "unique_relation_gain_candidate_count": "not_measured",
        }
    else:
        scores = [
            score_candidate(
                cert,
                args.order,
                frontier_keys,
                free_columns,
                null_basis,
            )
            for cert in candidate_certificates
            if int_value(cert.get("order")) == args.order
        ]
        scores.sort(
            key=lambda row: (
                -int_value(row.get("rank_gain_after_frontier")),
                -int_value(row.get("nonzero_null_projection_count")),
                -int_value(row.get("free_column_touch_count")),
                -int_value(row.get("unique_relation_gain_after_frontier")),
                str(row.get("artifact")),
                int_value(row.get("artifact_offset")),
            )
        )
        rank_extenders = [row for row in scores if int_value(row.get("rank_gain_after_frontier")) > 0]
        projection_hits = [row for row in scores if int_value(row.get("nonzero_null_projection_count")) > 0]
        unique_gain = [row for row in scores if int_value(row.get("unique_relation_gain_after_frontier")) > 0]
        free_touch = [row for row in scores if int_value(row.get("free_column_touch_count")) > 0]
        candidate_summary = {
            "candidate_certificate_count": len(scores),
            "free_column_touch_candidate_count": len(free_touch),
            "max_free_column_touch_count": max(
                [int_value(row.get("free_column_touch_count")) for row in scores] or [0]
            ),
            "nonzero_null_projection_candidate_count": len(projection_hits),
            "rank_extension_candidate_count": len(rank_extenders),
            "rank_extension_evidence": "measured_by_nullspace_projection",
            "unique_relation_gain_candidate_count": len(unique_gain),
        }

    payload = {
        "artifacts": {
            "candidate_certificates": [str(path) for path in candidate_paths],
            "frontier_certificates": [str(path) for path in frontier_paths],
            "scorer": args.scorer,
        },
        "branch_summary": summarize_branch(scores),
        "candidate_summary": candidate_summary,
        "claim_status": (
            "DEFICIENCY_DIRECTION_EXTENDERS_FOUND"
            if int_value(candidate_summary.get("rank_extension_candidate_count")) > 0
            else "SCORER_GREEDY_STOP_IMPLIES_NO_SINGLE_DEFICIENCY_EXTENDER"
            if args.skip_candidate_projections and scores == []
            else "CURRENT_BRANCH_FAMILY_NO_SINGLE_DEFICIENCY_EXTENDER"
            if scores or candidate_paths
            else "NO_CANDIDATES_FOR_DEFICIENCY_DIRECTION_AUDIT"
        ),
        "created_at": now_iso(),
        "frontier": {
            "augmented_rank": augmented_rank,
            "deficiency": max(0, factor_count - frontier_rank),
            "factor_variable_count": factor_count,
            "free_columns": free_columns,
            "matrix_consistent": augmented_rank == frontier_rank,
            "nullspace_basis": null_basis,
            "order": args.order,
            "pivot_columns": pivot_columns,
            "rank": frontier_rank,
            "unique_factor_relation_count": len(frontier_rows_by_key),
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: factor columns are the verifier's current order-specific namespace.",
            "INFERRED: when --skip-candidate-projections is used, no-extender evidence comes from the existing scorer greedy-stop condition rather than reopening every certificate.",
            "NEGATIVE SCOPE: a no-extender result only rules out single-certificate progress from the current candidate corpus and branch family.",
            "OPEN: target descent and individual-log recovery are not implemented.",
        ],
        "schema": "ecdlp.low_term_total2_deficiency_direction_scorer.v1",
        "top_candidates": scores[: max(0, args.top)],
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["frontier"], indent=2, sort_keys=True))
    print(json.dumps(payload["candidate_summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
