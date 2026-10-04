#!/usr/bin/env python3
"""Receipt and semantic-control checks for RUN-KIC-8b5038."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class ValidationError(RuntimeError):
    def __init__(self, message: str, *, unexpected: bool = False) -> None:
        super().__init__(message)
        self.unexpected = unexpected


def require(condition: bool, message: str, *, unexpected: bool = False) -> None:
    if not condition:
        raise ValidationError(message, unexpected=unexpected)


def field(record: dict[str, Any], name: str, *, nullable: bool = False) -> Any:
    require(name in record, f"missing required field {name!r}")
    value = record[name]
    if not nullable:
        require(value is not None, f"required field {name!r} is null")
    return value


def digest_value(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def parse_json_lines(data: bytes) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(data.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"stdout line {line_number} is not JSON: {exc}") from exc
        require(isinstance(value, dict), f"stdout line {line_number} is not an object")
        records.append(value)
    require(bool(records), "stdout contains no JSON records")
    return records


def exact_one(records: list[dict[str, Any]], kind: str) -> dict[str, Any]:
    matches = [record for record in records if record.get("kind") == kind]
    require(len(matches) == 1, f"expected one {kind}, found {len(matches)}")
    return matches[0]


def parse_direct_output(
    data: bytes,
    *,
    expected_scalar: int,
    expected_n: int,
    expected_k: int,
    expected_backend: str = "aarch64_pmull",
) -> dict[str, Any]:
    records = parse_json_lines(data)
    allowed = {"point_defined_factor_base", "relation_rank_receipt", "relation_rank_summary"}
    for record in records:
        require(record.get("kind") in allowed, f"unexpected direct kind {record.get('kind')!r}")
    base = exact_one(records, "point_defined_factor_base")
    summary = exact_one(records, "relation_rank_summary")
    relations = sorted(
        [record for record in records if record.get("kind") == "relation_rank_receipt"],
        key=lambda record: field(record, "accepted_relation"),
    )
    base_hash = field(base, "base_hash")
    require(isinstance(base_hash, str) and len(base_hash) == 64, "invalid base hash")
    require(field(base, "n") == expected_n, "base n mismatch")
    require(field(base, "orbit_columns") == expected_k, "factor-base K mismatch")
    require(field(base, "subgroup_membership_verified") is True, "base subgroup check failed")
    require(field(base, "selection_uses_scalar_labels") is False, "base used scalar labels")
    require(field(base, "parallel_support_expansion") is False, "parallel support enabled")
    require(field(base, "pipelined_support_expansion") is False, "pipelined support enabled")
    require(field(base, "parallel_support_expansion_threads") == 0, "support threads not zero")
    base_coordinates = field(base, "factor_base_point_coordinates")
    base_labels = field(base, "factor_base_point_labels")
    require(isinstance(base_coordinates, list) and isinstance(base_labels, list), "base details absent")
    require(len(base_coordinates) == len(base_labels) == field(base, "factor_base_points"), "base details length mismatch")

    require(field(summary, "n") == expected_n and field(summary, "base_hash") == base_hash, "summary/base mismatch")
    require(field(summary, "status") == "FULL_RANK", "direct status is not FULL_RANK")
    require(field(summary, "fixture_scalar_source") == "explicit_public_validation_scalar", "target is not explicit scalar")
    require(field(summary, "target_kind") == "known_scalar_multiple", "target kind mismatch")
    require(field(summary, "target_scalar_constructed") is True, "target not scalar constructed")
    require(field(summary, "published_fixture_scalar") == expected_scalar, "published scalar mismatch", unexpected=True)
    require(field(summary, "recovered_fixture_scalar") == expected_scalar, "recovered scalar mismatch", unexpected=True)
    require(field(summary, "linear_solution_verified") is True, "linear verification failed", unexpected=True)
    require(field(summary, "all_relations_group_verified") is True, "group verification failed", unexpected=True)
    require(field(summary, "query_parallel_threads") == 1, "query threads not one")
    require(field(summary, "query_mode") == "pair_pair_parallel_4096", "query mode mismatch")
    require(field(summary, "field_mul_backend") == expected_backend, "multiplication backend mismatch", unexpected=True)
    require(field(summary, "field_square_backend") == expected_backend, "squaring backend mismatch", unexpected=True)
    published_q = field(summary, "published_q")
    require(isinstance(published_q, list) and len(published_q) == 2, "published_q malformed")
    admitted = field(summary, "admitted_relations")
    require(isinstance(admitted, int) and admitted > 0 and len(relations) == admitted, "relation count mismatch")
    require(field(summary, "reference_relations_validated") == admitted, "not all relations validated")
    require([field(row, "accepted_relation") for row in relations] == list(range(1, admitted + 1)), "relation sequence incomplete")
    relation_hashes, sparse_rows, rank_progression = [], [], []
    for relation in relations:
        require(field(relation, "n") == expected_n and field(relation, "base_hash") == base_hash, "relation/base mismatch")
        require(field(relation, "published_fixture_scalar") == expected_scalar, "relation scalar mismatch", unexpected=True)
        require(field(relation, "target_kind") == "known_scalar_multiple", "relation target mismatch")
        require(field(relation, "target_scalar_constructed") is True, "relation target not constructed")
        require(field(relation, "fixture_scalar_used_by_collector") is False, "collector used fixture scalar")
        require(field(relation, "verified_group_identity") is True, "relation group identity failed", unexpected=True)
        relation_hash = field(relation, "relation_hash")
        sparse_row = field(relation, "sparse_row")
        require(isinstance(relation_hash, str) and len(relation_hash) == 64, "invalid relation hash")
        require(isinstance(sparse_row, list) and bool(sparse_row), "invalid sparse row")
        relation_hashes.append(relation_hash)
        sparse_rows.append(sparse_row)
        rank_progression.append({key: field(relation, key) for key in ("accepted_relation", "rank_before", "rank_after", "rank_incremented")})
    summary_hashes = field(summary, "relation_hashes", nullable=True)
    if summary_hashes is not None:
        require(summary_hashes == relation_hashes, "summary relation hashes differ")
    columns = field(summary, "matrix_columns")
    terminal_rank = field(summary, "terminal_rank")
    require(columns == expected_k + 1 and terminal_rank == columns, "terminal rank or K+1 mismatch")
    require(field(summary, "surplus_relations") == 0, "surplus relation count is not zero")
    rank_fields = {
        "matrix_columns": columns,
        "terminal_rank": terminal_rank,
        "full_rank_at_relation": field(summary, "full_rank_at_relation"),
        "admitted_relations": admitted,
        "surplus_relations": 0,
        "rank_progression": rank_progression,
    }
    semantic = {
        "n": expected_n,
        "status": "FULL_RANK",
        "factor_base_k": expected_k,
        "base_hash": base_hash,
        "factor_base_points": field(base, "factor_base_points"),
        "factor_base_point_coordinates": base_coordinates,
        "factor_base_point_labels": base_labels,
        "base_detail_digest": digest_value([base_coordinates, base_labels]),
        "relation_hashes": relation_hashes,
        "sparse_rows": sparse_rows,
        "rank_fields": rank_fields,
        "published_fixture_scalar": expected_scalar,
        "recovered_fixture_scalar": expected_scalar,
        "published_q": published_q,
        "linear_solution_verified": True,
        "all_relations_group_verified": True,
        "query_parallel_threads": 1,
        "parallel_support_expansion_threads": 0,
        "field_mul_backend": expected_backend,
        "field_square_backend": expected_backend,
        "setup_ms": field(summary, "setup_ms"),
        "collection_ms": field(summary, "collection_ms"),
        "query_ms": sum(float(field(row, "query_ms")) for row in relations),
        "linear_solve_ms": field(summary, "linear_solve_ms"),
        "solution_validation_ms": field(summary, "solution_validation_ms"),
        "charged_total_ms": field(summary, "charged_total_ms"),
        "support_index_entries": field(base, "support_index_entries"),
        "support_table_allocated_bytes": field(base, "support_table_allocated_bytes"),
    }
    return {
        **semantic,
        "accepted_relation_digest": digest_value(relation_hashes),
        "sparse_rows_digest": digest_value(sparse_rows),
        "result_digest": digest_value(semantic),
        "relation_hashes_derived_from_receipts": summary_hashes is None,
        "record_count": len(records),
    }


def parse_rho_output(
    data: bytes,
    *,
    expected_scalar: int,
    expected_n: int,
    expected_backend: str = "aarch64_pmull",
) -> dict[str, Any]:
    records = parse_json_lines(data)
    require(len(records) == 1 and records[0].get("kind") == "rho_public_fixture", "rho output shape mismatch")
    receipt = records[0]
    require(field(receipt, "n") == expected_n, "rho n mismatch")
    require(field(receipt, "fixture_scalar_source") == "explicit_public_validation_scalar", "rho target is not explicit")
    require(field(receipt, "target_kind") == "known_scalar_multiple", "rho target kind mismatch")
    require(field(receipt, "target_scalar_constructed") is True, "rho target not constructed")
    require(field(receipt, "published_fixture_scalar") == expected_scalar, "rho published scalar mismatch", unexpected=True)
    require(field(receipt, "recovered_fixture_scalar") == expected_scalar, "rho recovered scalar mismatch", unexpected=True)
    require(field(receipt, "verified") is True and field(receipt, "reference_group_validation") is True, "rho verification failed", unexpected=True)
    require(field(receipt, "field_multiplication_backend") == expected_backend, "rho multiplication backend mismatch", unexpected=True)
    require(field(receipt, "field_squaring_backend") == expected_backend, "rho squaring backend mismatch", unexpected=True)
    published_q = field(receipt, "published_q")
    require(isinstance(published_q, list) and len(published_q) == 2, "rho published_q malformed")
    semantic = {
        "n": expected_n,
        "published_fixture_scalar": expected_scalar,
        "recovered_fixture_scalar": expected_scalar,
        "published_q": published_q,
        "verified": True,
        "reference_group_validation": True,
        "quotient_mode": field(receipt, "quotient_mode"),
        "arithmetic_backend": field(receipt, "arithmetic_backend"),
        "field_multiplication_backend": expected_backend,
        "field_squaring_backend": expected_backend,
        "setup_ms": field(receipt, "setup_ms"),
        "walk_ms": field(receipt, "walk_ms"),
        "validation_ms": field(receipt, "validation_ms"),
        "total_ms": field(receipt, "total_ms"),
    }
    return {**semantic, "result_digest": digest_value(semantic), "record_count": 1}


def validate_semantic_controls(record: dict[str, Any]) -> None:
    baseline = record["baseline"]
    candidate = record["candidate"]
    for key in ("base_digest", "domain_digest", "lookup_digest", "active_x_count", "table_len"):
        require(baseline[key] == candidate[key], f"semantic control mismatch in {key}")
    require(baseline["table_capacity"] * 2 == candidate["table_capacity"], "test capacity is not exactly doubled")
    for arm in (baseline, candidate):
        require(arm["all_x_membership_exhaustive"] is True, "x membership control incomplete")
        require(arm["all_returned_witness_group_identities"] is True, "witness identity control incomplete")
        require(arm["actual_backend"] == "aarch64_pmull", "semantic control backend mismatch")


def validate_untimed_controls(record: dict[str, Any], semantic_controls: dict[str, Any]) -> None:
    require(record.get("valid") is True, "untimed control summary is not valid")
    baseline = record["parsed"]["baseline"]
    candidate = record["parsed"]["candidate"]
    rho = record["parsed"]["rho"]
    for key in ("base_hash", "factor_base_points", "base_detail_digest", "published_fixture_scalar", "recovered_fixture_scalar", "published_q"):
        require(baseline[key] == candidate[key], f"untimed direct mismatch in {key}")
    require(baseline["published_q"] == rho["published_q"], "untimed direct/rho public point mismatch")
    validate_semantic_controls(semantic_controls)


if __name__ == "__main__":
    raise SystemExit("library module; use runner.py or prepare.py")
