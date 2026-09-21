#!/usr/bin/env python3
"""Summarize branch-family certificates for a missing-quotient scheduler.

The rank-novelty gate tells us after a duplicate-hit stop whether a certificate
adds factor-row rank.  This audit turns that evidence into a scheduler-facing
table: which branch/support families ever moved the target-eliminated rowspace,
which families are now repeatedly dependent, and which factor columns remain
outside the current pivot set.

This remains a toy-prime, model-bound diagnostic.  It is not target descent and
not a deployed-curve speedup claim; it is a work order for moving rank novelty
earlier than full branch setup.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


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


def parse_paths(raw: str) -> list[Path]:
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def selected(cert: dict[str, Any]) -> dict[str, Any]:
    value = cert.get("selected")
    return value if isinstance(value, dict) else {}


def branch_key(cert: dict[str, Any]) -> str:
    return str(cert.get("branch_key") or selected(cert).get("branch_key") or "unknown")


def transfer_index(cert: dict[str, Any]) -> int:
    return int_value(cert.get("transfer_index"), int_value(selected(cert).get("transfer_index")))


def relation_rows(
    certificates: list[dict[str, Any]],
    order: int,
    factor_count: int,
) -> tuple[list[tuple[tuple[int, ...], int]], list[dict[str, Any]]]:
    keys: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
    for cert in certificates:
        if int_value(cert.get("order")) != order:
            continue
        for relation in factor_bank.target_eliminated_rows(cert):
            if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
                continue
            coeffs = [int_value(value) % order for value in relation.get("canonical_coeffs") or []]
            coeffs = coeffs + [0] * max(0, factor_count - len(coeffs))
            key = (tuple(coeffs[:factor_count]), int_value(relation.get("canonical_rhs")) % order)
            keys.setdefault(
                key,
                {
                    "canonical_coeffs": list(key[0]),
                    "canonical_rhs": key[1],
                    "factor_support": [
                        index for index, coeff in enumerate(key[0]) if coeff % order
                    ],
                    "multiplicity": 0,
                },
            )
            keys[key]["multiplicity"] += 1
    return list(keys), list(keys.values())


def audit_rank(certificates: list[dict[str, Any]], order: int, factor_count: int) -> dict[str, Any]:
    keys, rows = relation_rows(certificates, order, factor_count)
    matrix = [list(coeffs) for coeffs, _rhs in keys]
    rank = factor_bank.rank_mod(matrix, order)
    return {
        "rank": rank,
        "unique_factor_relation_count": len(keys),
        "deficiency": max(0, factor_count - rank),
        "unique_rows": rows,
    }


def pivot_columns(matrix: list[list[int]], modulus: int) -> list[int]:
    rows = [row[:] for row in matrix if any(value % modulus for value in row)]
    if not rows:
        return []
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
                    (rows[row][index] - factor * rows[rank][index]) % modulus
                    for index in range(col_count)
                ]
        pivots.append(col)
        rank += 1
        if rank == row_count:
            break
    return pivots


def support_labels(cert: dict[str, Any], order: int, factor_count: int) -> list[str]:
    labels: list[str] = []
    for relation in factor_bank.target_eliminated_rows(cert):
        if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
            continue
        coeffs = [int_value(value) % order for value in relation.get("canonical_coeffs") or []]
        coeffs = coeffs + [0] * max(0, factor_count - len(coeffs))
        support = [str(index) for index, coeff in enumerate(coeffs[:factor_count]) if coeff % order]
        labels.append(",".join(support) if support else "zero")
    return sorted(set(labels))


def chronological_scores(
    base: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    order: int,
    factor_count: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    accepted = list(base)
    scores: list[dict[str, Any]] = []
    for cert in sorted(
        candidates,
        key=lambda item: (
            transfer_index(item),
            str(item.get("_artifact")),
            int_value(item.get("_artifact_offset")),
        ),
    ):
        before = audit_rank(accepted, order, factor_count)
        after = audit_rank(accepted + [cert], order, factor_count)
        rank_gain = after["rank"] - before["rank"]
        unique_gain = after["unique_factor_relation_count"] - before["unique_factor_relation_count"]
        item = {
            "artifact": cert.get("_artifact"),
            "artifact_offset": int_value(cert.get("_artifact_offset")),
            "branch_key": branch_key(cert),
            "claim_status": (
                "CHRONOLOGICAL_MARGINAL_RANK_GAIN"
                if rank_gain > 0
                else "CHRONOLOGICAL_DEPENDENT_NEW_RELATION"
                if unique_gain > 0
                else "CHRONOLOGICAL_NO_NEW_RELATION"
            ),
            "factor_support_labels": support_labels(cert, order, factor_count),
            "forms_count": int_value(cert.get("forms_count")),
            "rank_after": after["rank"],
            "rank_before": before["rank"],
            "rank_gain": rank_gain,
            "transfer_index": transfer_index(cert),
            "unique_factor_relation_gain": unique_gain,
            "window": cert.get("window"),
        }
        scores.append(item)
        if rank_gain > 0:
            accepted.append(cert)
    final_audit = audit_rank(accepted, order, factor_count)
    return scores, accepted, final_audit


def branch_table(scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for score in scores:
        grouped[str(score.get("branch_key"))].append(score)
    rows: list[dict[str, Any]] = []
    for key, items in grouped.items():
        rank_gains = [item for item in items if int_value(item.get("rank_gain")) > 0]
        unique_gains = [item for item in items if int_value(item.get("unique_factor_relation_gain")) > 0]
        supports = sorted(
            {
                label
                for item in items
                for label in (item.get("factor_support_labels") or [])
            }
        )
        if rank_gains:
            policy = "productive_once_now_test_for_missing_quotient"
        elif unique_gains:
            policy = "dependent_relation_control"
        else:
            policy = "skip_repeated_no_new_relation"
        rows.append(
            {
                "branch_key": key,
                "first_transfer": min(int_value(item.get("transfer_index")) for item in items),
                "last_transfer": max(int_value(item.get("transfer_index")) for item in items),
                "observed_count": len(items),
                "policy_hint": policy,
                "rank_gain_count": len(rank_gains),
                "support_labels": supports,
                "unique_relation_gain_count": len(unique_gains),
            }
        )
    rows.sort(
        key=lambda item: (
            item["policy_hint"] != "productive_once_now_test_for_missing_quotient",
            -int_value(item.get("rank_gain_count")),
            -int_value(item.get("observed_count")),
            str(item.get("branch_key")),
        )
    )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-certificates", required=True)
    parser.add_argument("--candidate-certificates", required=True)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--factor-count", type=int, default=16)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_paths = parse_paths(args.base_certificates)
    candidate_paths = parse_paths(args.candidate_certificates)
    base = factor_bank.load_certificates(base_paths)
    candidates = [
        cert
        for cert in factor_bank.load_certificates(candidate_paths)
        if cert.get("public_key_verified")
    ]
    scores, accepted_rank_gain_certs, rank_gain_only_audit = chronological_scores(
        base, candidates, args.order, args.factor_count
    )
    full_audit = audit_rank(base + candidates, args.order, args.factor_count)
    full_matrix = [row["canonical_coeffs"] for row in full_audit["unique_rows"]]
    pivots = pivot_columns(full_matrix, args.order)
    missing_columns = [index for index in range(args.factor_count) if index not in pivots]
    branches = branch_table(scores)
    payload = {
        "artifacts": {
            "base_certificates": [str(path) for path in base_paths],
            "candidate_certificates": [str(path) for path in candidate_paths],
        },
        "branch_policy_table": branches,
        "claim_status": (
            "MISSING_QUOTIENT_SCHEDULER_HAS_RANK_GAIN_HISTORY"
            if any(int_value(row.get("rank_gain_count")) > 0 for row in branches)
            else "MISSING_QUOTIENT_SCHEDULER_NO_RANK_GAIN_HISTORY"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: branch policy is inferred from order-specific verifier factor columns.",
            "HEURISTIC: pivot columns are a scheduler hint, not a theorem about all future branches.",
            "OPEN: this audit does not implement target descent; it emits a work order for pre-setup rank novelty.",
        ],
        "parameters": {
            "factor_count": args.factor_count,
            "order": args.order,
        },
        "rank_gain_chronology": scores,
        "schema": "ecdlp.low_term_total2_branch_family_missing_quotient_scheduler_audit.v1",
        "scheduler_work_order": {
            "avoid_branch_keys": [
                row["branch_key"]
                for row in branches
                if row["policy_hint"] == "skip_repeated_no_new_relation"
            ],
            "dependent_relation_branch_keys": [
                row["branch_key"]
                for row in branches
                if row["policy_hint"] == "dependent_relation_control"
            ],
            "deprioritize_exact_repeat_branch_keys": [
                row["branch_key"]
                for row in branches
                if row["policy_hint"] != "productive_once_now_test_for_missing_quotient"
            ],
            "missing_pivot_columns": missing_columns,
            "prefer_support_labels": sorted(
                {
                    label
                    for row in branches
                    if row["policy_hint"] == "productive_once_now_test_for_missing_quotient"
                    for label in row.get("support_labels") or []
                }
            ),
            "productive_branch_keys": [
                row["branch_key"]
                for row in branches
                if row["policy_hint"] == "productive_once_now_test_for_missing_quotient"
            ],
        },
        "summary": {
            "candidate_certificate_count": len(candidates),
            "chronological_rank_gain_count": sum(
                1 for item in scores if int_value(item.get("rank_gain")) > 0
            ),
            "full_bank_deficiency": full_audit["deficiency"],
            "full_bank_rank": full_audit["rank"],
            "full_bank_unique_factor_relation_count": full_audit["unique_factor_relation_count"],
            "missing_pivot_column_count": len(missing_columns),
            "rank_gain_only_deficiency": rank_gain_only_audit["deficiency"],
            "rank_gain_only_rank": rank_gain_only_audit["rank"],
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
