#!/usr/bin/env python3
"""Public static validator for the JINV amendment-v5 raw fixture.

The validator is deliberately standard-library-only. It performs no network
access, private-harness import, experiment command, curve/run measurement, or
scientific interpretation.

Exact deterministic self-test invocation:

    python3 v5-derivation-validator.py \
        --fixture v5-derivation-fixtures.json --self-test
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from typing import Any

SCHEMA = "crypto.autoresearch.jinv_v5_derivation_fixtures.v1"
TASK_ID = "TASK-20260813-1470c9"
EXPERIMENT_ID = "EXP-JINV-bd141d"
PROTOCOL_VERSION = 6
GRAMMAR = "jinv-v5-row-key-v1"
CANDIDATE_FACTORS = (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 18, 22)
CANDIDATE_DENSITIES = {
    4: (1, 8), 5: (7, 48), 6: (3, 20), 7: (5, 32),
    8: (1, 6), 9: (17, 96), 10: (9, 50), 11: (11, 60),
    12: (3, 16), 13: (19, 96), 15: (1, 5), 18: (5, 24),
    22: (11, 48),
}
QUERY_IDENTITY = [
    GRAMMAR, "family_statistic", None, None, "query-v5-family-001",
    None, 8, "decomposition_rate_m3", "d0", "positive",
    "seed_independent", 1, 0, "scientific_view", None, None,
    "q-v5-family-density",
]
REFERENCE_SELECTOR = {
    "arm": "d0",
    "bank_or_view": "reference",
    "direction": "positive",
    "factor_base_size": 8,
    "query_id": "q-v5-family-density",
    "record_type": "row_statistic_cell",
    "rung": 1,
    "statistic": "decomposition_rate_m3",
    "target_seed_or_seed_independent": "seed_independent",
}
TOP_LEVEL_KEYS = {
    "authority_boundary", "canonicalization_contract",
    "continuing_separate_blockers", "derivation_contract",
    "expected_derived", "experiment_id", "fixture_scope",
    "mutation_contract", "mutation_suite", "preserved_v4_contract",
    "protocol_version", "raw_fixture", "schema", "task_id", "tie_fixture",
}
EXPECTED_CANONICALIZATION = {
    "artifact_encoding": "UTF8_RFC8259_recursively_sorted_keys_compact_one_terminal_LF",
    "derived_encoding": "UTF8_RFC8259_recursively_sorted_keys_compact_no_terminal_LF",
    "duplicate_json_keys": "reject_during_parse",
    "duplicate_semantic_identities": "reject_before_reduction",
    "identity_array_length": 17,
    "identity_encoding": "UTF8_RFC8259_compact_JSON_array_no_whitespace",
    "identity_sort": "lexicographic_unsigned_UTF8_bytes",
    "integer_domain": "canonical_JSON_integer_no_float_exponent_or_string_alias",
    "locale_sorting": False,
    "reference_population_representation": "explicit_complete_canonical_JSON_array_of_20000_records",
}
EXPECTED_AUTHORITY = {
    "automatic_execution": False,
    "control_runs": 0,
    "curve_measurements": 0,
    "empirical_evidence_created": False,
    "experiment_runs": 0,
    "implementation_authorized": False,
    "instrument_runs": 0,
    "jinv_runs": 0,
    "mathematical_evidence_created": False,
    "network_used": False,
    "scientific_interpretation": "none",
    "status_transition": "none",
}
EXPECTED_BLOCKERS = {
    "c_transport_cert": {
        "authorized_or_executed": False,
        "requirements": [
            "source_pinned", "independently_reverified", "same_k",
            "scalar_orientation_preserving",
        ],
        "status": "separately_blocking_unchanged",
    },
    "historical_scope_discrepancy": {
        "omitted_paths": [
            "harness/exp_jinv_matched.py", "harness/run_jinv_matched.py",
        ],
        "retroactive_normalization": False,
        "status": "preserved_uncured",
        "task_id": "TASK-20260810-799ffa",
    },
    "n18": {
        "authorized_or_executed": False,
        "status": "unapproved_uncontracted_unimplemented_unexecuted",
    },
    "second_matched_N": {
        "current_scope": "one_N_19507_toy_only",
        "status": "separately_required_unchanged",
    },
}
EXPECTED_V4_BINDINGS = {
    "experiments/EXP-JINV-bd141d/amendments/v4-cost-worksheet.json": {
        "sha256": "169e7a5579cba7c2f525bddaee5287ede8fb0d78a92d39c951253d8813836ae0",
        "size_bytes": 16781,
    },
    "experiments/EXP-JINV-bd141d/amendments/v4-static-fixtures.json": {
        "sha256": "af17b908dd71a213269c7b235f6a89853c99b3488589b25d4ebad3d73a05d344",
        "size_bytes": 65029,
    },
    "experiments/EXP-JINV-bd141d/amendments/v4.yaml": {
        "sha256": "f856bba79ffa5e8b6f2b86a31ae9554f1790bf52f5eb760b35a8704bb9f01138",
        "size_bytes": 24973,
    },
}
EXPECTED_COST_ANCHORS = {
    "all_map_contexts": 773791200,
    "all_replacement_pairs_upper": 196211340000,
    "d0_bank_row_statistic_cells": 2600000,
    "largest_required_logical_artifact_bytes_upper": 50230103040000,
    "minimum_artifact_shards_by_individual_cap": 93969,
    "null_banks_and_cells_bytes": 528640000,
    "retained_artifact_bytes_upper": 50449135844608,
    "total_logical_io_bytes_upper": 151347407533824,
}
EXPECTED_RECORD_TYPES = [
    "primitive_source_record", "replacement_pair",
    "d0_governing_permutation", "d0_null_class_placement",
    "per_curve_statistic", "aut_vertex_statistic", "row_statistic_cell",
    "pseudo_crater_cell", "wilson_interval_cell",
    "specificity_margin_cell", "operating_row", "family_statistic",
    "p_value_numerator", "detection_floor", "whole_grid_disposition",
]
EXPECTED_FIELD_ORDER = [
    GRAMMAR, "record_type", "class_id_or_null", "curve_id_or_null",
    "source_record_id_or_null", "destination_record_id_or_null",
    "factor_base_size_or_null", "statistic_or_null", "arm_or_null",
    "direction_or_null", "target_seed_or_seed_independent_or_null",
    "rung_or_null", "replicate_or_null", "bank_or_view_or_null",
    "vertex_id_or_null", "designated_vertex_id_or_null", "query_id_or_null",
]


class ValidationError(ValueError):
    """Stable public validation failure."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code + (": " + detail if detail else ""))
        self.code = code
        self.detail = detail


def fail(code: str, detail: str = "") -> None:
    raise ValidationError(code, detail)


def canonical_bytes(value: Any, terminal_lf: bool = False) -> bytes:
    encoded = json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return encoded + (b"\n" if terminal_lf else b"")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("duplicate_json_key", key)
        result[key] = value
    return result


def reject_float(token: str) -> None:
    fail("noncanonical_number", token)


def strict_json_load(
    data: bytes, *, terminal_lf: bool, canonical_code: str
) -> Any:
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        fail("invalid_utf8", str(exc))
    try:
        value = json.loads(
            text, object_pairs_hook=reject_duplicate_pairs,
            parse_float=reject_float, parse_constant=reject_float,
        )
    except ValidationError:
        raise
    except json.JSONDecodeError as exc:
        fail("invalid_json", str(exc))
    if canonical_bytes(value, terminal_lf=terminal_lf) != data:
        fail(canonical_code)
    return value


def require_exact_keys(value: Any, keys: set[str], code: str) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        fail(code)


def require_plain_int(value: Any, code: str) -> int:
    if type(value) is not int:
        fail(code)
    return value


def validate_rational(value: Any) -> tuple[int, int]:
    require_exact_keys(value, {"denominator", "numerator"}, "rational_shape")
    numerator = require_plain_int(value["numerator"], "rational_domain")
    denominator = require_plain_int(value["denominator"], "rational_domain")
    if numerator < 0 or denominator <= 0:
        fail("rational_domain")
    if math.gcd(numerator, denominator) != 1:
        fail("rational_noncanonical")
    return numerator, denominator


def identity_bytes(identity: Any) -> bytes:
    if not isinstance(identity, list) or len(identity) != 17:
        fail("identity_length")
    return canonical_bytes(identity)


def expected_reference_identity(index: int) -> list[Any]:
    return [
        GRAMMAR, "row_statistic_cell", None, None,
        "ref-v5-" + str(index).zfill(5), None, 8,
        "decomposition_rate_m3", "d0", "positive", "seed_independent",
        1, index, "reference", None, None, "q-v5-family-density",
    ]


def expected_reference_value(index: int) -> dict[str, int]:
    divisor = math.gcd(index, 20000)
    return {
        "denominator": 20000 // divisor,
        "numerator": index // divisor,
    }


def validate_preserved_v4(value: Any) -> None:
    require_exact_keys(
        value,
        {
            "cost_anchors", "cost_credit", "key_grammar", "resource_gates",
            "source_bindings", "static_boundaries",
        },
        "preserved_v4_contract",
    )
    if value["source_bindings"] != EXPECTED_V4_BINDINGS:
        fail("v4_source_bindings")
    if value["cost_anchors"] != EXPECTED_COST_ANCHORS:
        fail("v4_cost_anchors")
    if value["cost_credit"] != {
        "budget_widening": False, "cell_omission": False,
        "compression": False, "deduplication": False,
        "hash_only_substitution": False,
    }:
        fail("v4_cost_credit")
    expected_key = {
        "applicability_partition_count": 15,
        "corrected_collision_count": 0,
        "exact_array_length": 17,
        "grammar_version": GRAMMAR,
        "isolated_collision_mutation_count": 7,
        "old_collision_count": 13,
        "old_source_record_count": 18,
        "record_types": EXPECTED_RECORD_TYPES,
        "universal_field_order": EXPECTED_FIELD_ORDER,
    }
    if value["key_grammar"] != expected_key:
        fail("v4_key_grammar")
    expected_gates = {
        "controlling_disposition": "resource_incomplete",
        "cpu": "FAIL_MISSING_ESTIMATE",
        "free_disk": "FAIL_INHERITED_READ_ONLY_V3_OBSERVATION",
        "individual_artifact_without_sharding": "FAIL",
        "peak_memory": "FAIL_MISSING_ESTIMATE",
        "retained_artifact_bytes": "FAIL",
        "shard_count": "FAIL",
        "total_logical_io_bytes": "FAIL",
        "wall": "FAIL_MISSING_ESTIMATE",
    }
    if value["resource_gates"] != expected_gates:
        fail("resource_incomplete_contract")
    if value["static_boundaries"] != {
        "d0_label_literal": "EXP-JINV-bd141d|v4|d0-null|bank=BANK|rep=REP",
        "factor_base_sizes": list(CANDIDATE_FACTORS),
        "matched_order_N": 19507,
        "one_N_toy_ceiling": True,
        "target_seeds": [20260810, 20260811, 11235813],
    }:
        fail("v4_static_boundaries")


def validate_derivation_contract(contract: Any) -> None:
    expected_keys = {
        "ascending_candidate_order", "ascending_reference_order",
        "candidate_distance_rule", "candidate_factor_base_sizes",
        "candidate_input_order", "candidate_tie_rule",
        "descending_candidate_order", "descending_reference_order",
        "equality_included", "independent_accumulators", "p_comparison",
        "p_value_denominator", "plus_one", "query_record_count",
        "reference_population_count", "reference_selector",
        "require_exact_byte_equality",
        "stored_output_or_hash_is_derivation_premise", "target_density",
    }
    require_exact_keys(contract, expected_keys, "derivation_contract_shape")
    checks = [
        (contract["target_density"] == {"denominator": 6, "numerator": 1},
         "target_density_contract"),
        (contract["candidate_factor_base_sizes"] == list(CANDIDATE_FACTORS),
         "candidate_membership"),
        (contract["candidate_input_order"] == "ascending_factor_base_size",
         "candidate_order"),
        (contract["candidate_distance_rule"] ==
         "absolute_exact_rational_distance_by_integer_cross_multiplication",
         "distance_rule_contract"),
        (contract["candidate_tie_rule"] == "smaller_factor_base_size",
         "tie_rule_contract"),
        (contract["query_record_count"] == 1, "query_cardinality"),
        (contract["reference_population_count"] == 20000,
         "reference_count_contract"),
        (contract["reference_selector"] == REFERENCE_SELECTOR,
         "reference_selector_contract"),
        (contract["p_comparison"] == "greater_than_or_equal",
         "p_comparison_contract"),
        (contract["equality_included"] is True, "equality_contract"),
        (contract["plus_one"] is True, "plus_one_contract"),
        (contract["p_value_denominator"] == 20001,
         "p_denominator_contract"),
        (contract["ascending_candidate_order"] ==
         "ascending_factor_base_size", "ascending_order_contract"),
        (contract["ascending_reference_order"] ==
         "ascending_canonical_identity_bytes", "ascending_order_contract"),
        (contract["descending_candidate_order"] ==
         "descending_factor_base_size", "descending_order_contract"),
        (contract["descending_reference_order"] ==
         "descending_canonical_identity_bytes", "descending_order_contract"),
        (contract["independent_accumulators"] is True,
         "independent_accumulator_contract"),
        (contract["require_exact_byte_equality"] is True,
         "byte_equality_contract"),
        (contract["stored_output_or_hash_is_derivation_premise"] is False,
         "stored_premise_contract"),
    ]
    for passed, code in checks:
        if not passed:
            fail(code)


def validate_candidate_rows(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or len(rows) != 13:
        fail("candidate_cardinality")
    for row in rows:
        require_exact_keys(
            row, {"candidate_row_id", "density", "factor_base_size"},
            "candidate_row_shape",
        )
        require_plain_int(row["factor_base_size"], "candidate_membership")
        if not isinstance(row["candidate_row_id"], str):
            fail("candidate_row_id_contract")
    factors = [row["factor_base_size"] for row in rows]
    if len(set(factors)) != len(factors):
        fail("candidate_duplicate")
    if set(factors) != set(CANDIDATE_FACTORS):
        fail("candidate_membership")
    if factors != list(CANDIDATE_FACTORS):
        fail("candidate_order")
    row_ids = [row["candidate_row_id"] for row in rows]
    if len(set(row_ids)) != len(row_ids):
        fail("candidate_row_id_duplicate")
    for row in rows:
        factor = row["factor_base_size"]
        if row["candidate_row_id"] != "candidate-fb-" + str(factor).zfill(2):
            fail("candidate_row_id_contract")
        if validate_rational(row["density"]) != CANDIDATE_DENSITIES[factor]:
            fail("candidate_density_contract")
    return rows


def validate_query_records(records: Any) -> dict[str, Any]:
    if not isinstance(records, list) or len(records) != 1:
        fail("query_cardinality")
    record = records[0]
    require_exact_keys(record, {"identity", "value"}, "query_record_shape")
    identity_bytes(record["identity"])
    if canonical_bytes(record["identity"]) != canonical_bytes(QUERY_IDENTITY):
        fail("query_identity_contract")
    if validate_rational(record["value"]) != (1, 2):
        fail("query_value_contract")
    return record


def validate_reference_records(records: Any) -> list[dict[str, Any]]:
    if not isinstance(records, list) or len(records) != 20000:
        fail("reference_cardinality")
    encountered: list[bytes] = []
    seen: set[bytes] = set()
    for record in records:
        require_exact_keys(record, {"identity", "value"},
                           "reference_record_shape")
        identity = record["identity"]
        encoded = identity_bytes(identity)
        if encoded in seen:
            fail("reference_duplicate_identity")
        seen.add(encoded)
        encountered.append(encoded)
        if identity[13] != "reference":
            fail("reference_selector_membership")
        if identity[4] == "query-v5-family-001":
            fail("reference_self_selected")
        selector_projection = {
            "record_type": identity[1],
            "factor_base_size": identity[6],
            "statistic": identity[7],
            "arm": identity[8],
            "direction": identity[9],
            "target_seed_or_seed_independent": identity[10],
            "rung": identity[11],
            "bank_or_view": identity[13],
            "query_id": identity[16],
        }
        if selector_projection != REFERENCE_SELECTOR:
            fail("reference_selector_membership")
        validate_rational(record["value"])
    if encountered != sorted(encountered):
        fail("reference_order")
    for index, record in enumerate(records):
        if canonical_bytes(record["identity"]) != canonical_bytes(
            expected_reference_identity(index)
        ):
            fail("reference_identity_contract")
        if record["value"] != expected_reference_value(index):
            fail("reference_value_contract")
    return records


def exact_distance(row: dict[str, Any],
                   target: dict[str, int]) -> tuple[int, int]:
    numerator = row["density"]["numerator"]
    denominator = row["density"]["denominator"]
    target_numerator = target["numerator"]
    target_denominator = target["denominator"]
    return (
        abs(numerator * target_denominator -
            target_numerator * denominator),
        denominator * target_denominator,
    )


def derive_selected_row(
    rows: list[dict[str, Any]], target: dict[str, int], *,
    descending: bool,
) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: row["factor_base_size"],
                     reverse=descending)
    best: dict[str, Any] | None = None
    best_distance: tuple[int, int] | None = None
    for row in ordered:
        distance = exact_distance(row, target)
        if best is None:
            best, best_distance = row, distance
            continue
        assert best_distance is not None
        left = distance[0] * best_distance[1]
        right = best_distance[0] * distance[1]
        if left < right or (
            left == right and
            row["factor_base_size"] < best["factor_base_size"]
        ):
            best, best_distance = row, distance
    assert best is not None
    return {
        "factor_base_size": best["factor_base_size"],
        "row_density": copy.deepcopy(best["density"]),
        "rule": "minimum_exact_distance_to_1_over_6_then_smaller_factor_base_size",
        "target_density": copy.deepcopy(target),
    }


def derive_p_value(
    query: dict[str, Any], records: list[dict[str, Any]], *,
    descending: bool,
) -> dict[str, Any]:
    ordered = sorted(records, key=lambda record:
                     identity_bytes(record["identity"]),
                     reverse=descending)
    query_numerator = query["value"]["numerator"]
    query_denominator = query["value"]["denominator"]
    greater_or_equal_count = 0
    equal_count = 0
    for record in ordered:
        numerator = record["value"]["numerator"]
        denominator = record["value"]["denominator"]
        left = numerator * query_denominator
        right = query_numerator * denominator
        if left >= right:
            greater_or_equal_count += 1
        if left == right:
            equal_count += 1
    return {
        "denominator": len(records) + 1,
        "equality_included": True,
        "plus_one": True,
        "reference_equal_count": equal_count,
        "reference_greater_or_equal_count": greater_or_equal_count,
        "value": greater_or_equal_count + 1,
    }


def derive_pass(
    rows: list[dict[str, Any]], query: dict[str, Any],
    references: list[dict[str, Any]], *, descending: bool,
) -> dict[str, Any]:
    selected = derive_selected_row(
        copy.deepcopy(rows), {"denominator": 6, "numerator": 1},
        descending=descending,
    )
    p_value = derive_p_value(
        copy.deepcopy(query), copy.deepcopy(references),
        descending=descending,
    )
    candidate_hash = sha256_hex(canonical_bytes(rows))
    query_hash = sha256_hex(canonical_bytes(query))
    reference_hash = sha256_hex(canonical_bytes(references))
    aggregate = {
        "candidate_table_sha256": candidate_hash,
        "p_value_numerator": p_value,
        "query_record_sha256": query_hash,
        "reference_population_sha256": reference_hash,
        "selected_operating_row": selected,
    }
    return {
        "aggregate": aggregate,
        "hashes": {
            "aggregate": sha256_hex(canonical_bytes(aggregate)),
            "candidate_table": candidate_hash,
            "p_value_numerator": sha256_hex(canonical_bytes(p_value)),
            "query_record": query_hash,
            "reference_population": reference_hash,
            "selected_operating_row": sha256_hex(canonical_bytes(selected)),
        },
        "p_value_numerator": p_value,
        "selected_operating_row": selected,
    }


def validate_tie_fixture(value: Any) -> None:
    require_exact_keys(
        value,
        {"expected_distance", "expected_selected_factor_base_size",
         "rows", "target_density"},
        "tie_fixture_shape",
    )
    if value["target_density"] != {"denominator": 6, "numerator": 1}:
        fail("target_density_contract")
    rows = value["rows"]
    expected_rows = [
        {"candidate_row_id": "tie-fb-05",
         "density": {"denominator": 8, "numerator": 1},
         "factor_base_size": 5},
        {"candidate_row_id": "tie-fb-07",
         "density": {"denominator": 24, "numerator": 5},
         "factor_base_size": 7},
    ]
    if not isinstance(rows, list) or len(rows) != 2:
        fail("tie_rows_contract")
    for row in rows:
        require_exact_keys(
            row, {"candidate_row_id", "density", "factor_base_size"},
            "tie_rows_contract",
        )
        validate_rational(row["density"])
    if [row["factor_base_size"] for row in rows] != [5, 7]:
        fail("tie_order")
    if rows != expected_rows:
        fail("tie_rows_contract")
    if value["expected_distance"] != {"denominator": 24, "numerator": 1}:
        fail("tie_expected")
    ascending = derive_selected_row(
        rows, value["target_density"], descending=False)
    descending = derive_selected_row(
        rows, value["target_density"], descending=True)
    if canonical_bytes(ascending) != canonical_bytes(descending):
        fail("tie_order_dependence")
    if (value["expected_selected_factor_base_size"] != 5 or
            ascending["factor_base_size"] != 5):
        fail("tie_expected")


def validate_mutation_manifest(fixture: dict[str, Any]) -> None:
    contract = fixture["mutation_contract"]
    require_exact_keys(
        contract,
        {"all_declared_mutations_must_fail_for_expected_error",
         "declared_mutation_count", "manifest_sha256",
         "minimum_mutation_count", "positive_fixture_must_pass_before_mutations",
         "prior_lockstep_counterfeit_required"},
        "mutation_contract",
    )
    suite = fixture["mutation_suite"]
    if not isinstance(suite, list):
        fail("mutation_contract")
    if contract["minimum_mutation_count"] != 98 or len(suite) < 98:
        fail("mutation_contract")
    if contract["declared_mutation_count"] != len(suite):
        fail("mutation_contract")
    if contract["manifest_sha256"] != sha256_hex(canonical_bytes(suite)):
        fail("mutation_manifest_hash")
    if (contract["all_declared_mutations_must_fail_for_expected_error"]
            is not True or
            contract["positive_fixture_must_pass_before_mutations"]
            is not True or
            contract["prior_lockstep_counterfeit_required"] is not True):
        fail("mutation_contract")
    seen: set[str] = set()
    operators: set[str] = set()
    for mutation in suite:
        require_exact_keys(
            mutation,
            {"expected_error", "id", "mutation_class", "operator", "params"},
            "mutation_shape",
        )
        if not all(isinstance(mutation[name], str)
                   for name in ("expected_error", "id",
                                "mutation_class", "operator")):
            fail("mutation_shape")
        if not isinstance(mutation["params"], dict):
            fail("mutation_shape")
        if mutation["id"] in seen:
            fail("mutation_duplicate_id")
        seen.add(mutation["id"])
        operators.add(mutation["operator"])
    if "lockstep_counterfeit" not in operators:
        fail("mutation_contract")


def validate_fixture_object(fixture: Any) -> dict[str, Any]:
    require_exact_keys(fixture, TOP_LEVEL_KEYS, "fixture_shape")
    if fixture["schema"] != SCHEMA:
        fail("fixture_schema")
    if fixture["task_id"] != TASK_ID:
        fail("fixture_task_id")
    if fixture["experiment_id"] != EXPERIMENT_ID:
        fail("fixture_experiment_id")
    if fixture["protocol_version"] != PROTOCOL_VERSION:
        fail("fixture_protocol_version")
    if fixture["fixture_scope"] != (
        "complete_synthetic_raw_static_protocol_integrity_no_measurement_no_execution"
    ):
        fail("fixture_scope")
    if fixture["canonicalization_contract"] != EXPECTED_CANONICALIZATION:
        fail("canonicalization_contract")
    if fixture["authority_boundary"] != EXPECTED_AUTHORITY:
        fail("authority_boundary")
    if fixture["continuing_separate_blockers"] != EXPECTED_BLOCKERS:
        fail("continuing_blockers")
    validate_preserved_v4(fixture["preserved_v4_contract"])
    validate_derivation_contract(fixture["derivation_contract"])

    raw = fixture["raw_fixture"]
    require_exact_keys(
        raw, {"candidate_rows", "query_records", "reference_records"},
        "raw_fixture_shape",
    )
    rows = validate_candidate_rows(raw["candidate_rows"])
    query = validate_query_records(raw["query_records"])
    references = validate_reference_records(raw["reference_records"])
    validate_tie_fixture(fixture["tie_fixture"])

    ascending = derive_pass(
        rows, query, references, descending=False)
    descending = derive_pass(
        rows, query, references, descending=True)
    for name in ("selected_operating_row", "p_value_numerator", "aggregate"):
        if canonical_bytes(ascending[name]) != canonical_bytes(descending[name]):
            fail("order_pass_mismatch", name)

    expected = fixture["expected_derived"]
    require_exact_keys(
        expected,
        {"aggregate", "hashes", "p_value_numerator",
         "selected_operating_row"},
        "expected_derived_shape",
    )
    if expected["selected_operating_row"] != ascending["selected_operating_row"]:
        fail("selected_output_mismatch")
    if expected["p_value_numerator"] != ascending["p_value_numerator"]:
        fail("p_output_mismatch")
    hashes = expected["hashes"]
    require_exact_keys(
        hashes,
        {"aggregate", "candidate_table", "p_value_numerator",
         "query_record", "reference_population", "selected_operating_row"},
        "expected_hash_shape",
    )
    actual = ascending["hashes"]
    for name, code in (
        ("candidate_table", "candidate_hash_mismatch"),
        ("query_record", "query_hash_mismatch"),
        ("reference_population", "reference_expected_hash_mismatch"),
        ("selected_operating_row", "selected_hash_mismatch"),
        ("p_value_numerator", "p_hash_mismatch"),
    ):
        if hashes[name] != actual[name]:
            fail(code)
    if expected["aggregate"] != ascending["aggregate"]:
        fail("aggregate_output_mismatch")
    if hashes["aggregate"] != actual["aggregate"]:
        fail("aggregate_hash_mismatch")
    validate_mutation_manifest(fixture)
    return {
        "aggregate_sha256": actual["aggregate"],
        "candidate_table_sha256": actual["candidate_table"],
        "mutation_count": len(fixture["mutation_suite"]),
        "p_value_denominator": ascending["p_value_numerator"]["denominator"],
        "p_value_numerator": ascending["p_value_numerator"]["value"],
        "query_record_sha256": actual["query_record"],
        "reference_population_count": len(references),
        "reference_population_sha256": actual["reference_population"],
        "selected_factor_base_size":
            ascending["selected_operating_row"]["factor_base_size"],
        "selected_operating_row_sha256":
            actual["selected_operating_row"],
    }


def load_fixture(path: str) -> tuple[dict[str, Any], bytes]:
    with open(path, "rb") as handle:
        raw = handle.read()
    fixture = strict_json_load(
        raw, terminal_lf=True, canonical_code="artifact_not_canonical")
    if not isinstance(fixture, dict):
        fail("fixture_shape")
    return fixture, raw


def reduce_pair(numerator: int, denominator: int) -> tuple[int, int]:
    divisor = math.gcd(numerator, denominator)
    return numerator // divisor, denominator // divisor


def set_path(root: dict[str, Any], path: list[Any], value: Any) -> None:
    cursor: Any = root
    for component in path[:-1]:
        cursor = cursor[component]
    cursor[path[-1]] = value


def refresh_stored_dependent_hashes(fixture: dict[str, Any]) -> None:
    expected = fixture["expected_derived"]
    hashes = expected["hashes"]
    hashes["selected_operating_row"] = sha256_hex(
        canonical_bytes(expected["selected_operating_row"]))
    hashes["p_value_numerator"] = sha256_hex(
        canonical_bytes(expected["p_value_numerator"]))
    expected["aggregate"] = {
        "candidate_table_sha256": hashes["candidate_table"],
        "p_value_numerator": copy.deepcopy(expected["p_value_numerator"]),
        "query_record_sha256": hashes["query_record"],
        "reference_population_sha256": hashes["reference_population"],
        "selected_operating_row":
            copy.deepcopy(expected["selected_operating_row"]),
    }
    hashes["aggregate"] = sha256_hex(canonical_bytes(expected["aggregate"]))


def apply_mutation(
    source: dict[str, Any], mutation: dict[str, Any]
) -> dict[str, Any]:
    fixture = copy.deepcopy(source)
    operator = mutation["operator"]
    params = mutation["params"]
    rows = fixture["raw_fixture"]["candidate_rows"]
    references = fixture["raw_fixture"]["reference_records"]
    queries = fixture["raw_fixture"]["query_records"]

    if operator == "set_path":
        set_path(fixture, params["path"], params["value"])
    elif operator in {"candidate_numerator", "candidate_denominator"}:
        density = rows[params["index"]]["density"]
        numerator = density["numerator"]
        denominator = density["denominator"]
        if operator == "candidate_numerator":
            numerator += params["delta"]
        else:
            denominator += params["delta"]
        numerator, denominator = reduce_pair(numerator, denominator)
        density.update(numerator=numerator, denominator=denominator)
    elif operator == "candidate_membership":
        rows[params["index"]]["factor_base_size"] =             params["new_factor_base_size"]
    elif operator == "candidate_duplicate":
        rows[params["target_index"]] =             copy.deepcopy(rows[params["source_index"]])
    elif operator == "candidate_omit":
        del rows[params["index"]]
    elif operator == "candidate_extra":
        factor = params["factor_base_size"]
        rows.append({
            "candidate_row_id": "candidate-fb-" + str(factor).zfill(2),
            "density": {"denominator": 4, "numerator": 1},
            "factor_base_size": factor,
        })
    elif operator == "candidate_nonreduced":
        density = rows[params["index"]]["density"]
        density["numerator"] *= params["multiplier"]
        density["denominator"] *= params["multiplier"]
    elif operator == "candidate_negative_numerator":
        rows[params["index"]]["density"]["numerator"] = -1
    elif operator == "candidate_zero_denominator":
        rows[params["index"]]["density"]["denominator"] = 0
    elif operator == "candidate_reverse_order":
        rows.reverse()
    elif operator == "candidate_duplicate_row_id":
        rows[params["target_index"]]["candidate_row_id"] =             rows[params["source_index"]]["candidate_row_id"]
    elif operator == "candidate_row_id_alias":
        rows[params["index"]]["candidate_row_id"] = params["value"]
    elif operator == "candidate_extra_field":
        rows[params["index"]]["alias"] = "forbidden"
    elif operator == "tie_density":
        density = fixture["tie_fixture"]["rows"][params["index"]]["density"]
        numerator, denominator = reduce_pair(
            density["numerator"] + params["delta"], density["denominator"])
        density.update(numerator=numerator, denominator=denominator)
    elif operator == "tie_reverse_order":
        fixture["tie_fixture"]["rows"].reverse()
    elif operator == "query_identity":
        queries[0]["identity"][params["position"]] = params["value"]
    elif operator in {"query_numerator", "query_denominator"}:
        value = queries[0]["value"]
        numerator, denominator = value["numerator"], value["denominator"]
        if operator == "query_numerator":
            numerator += params["delta"]
        else:
            denominator += params["delta"]
        numerator, denominator = reduce_pair(numerator, denominator)
        value.update(numerator=numerator, denominator=denominator)
    elif operator == "query_nonreduced":
        value = queries[0]["value"]
        value["numerator"] *= params["multiplier"]
        value["denominator"] *= params["multiplier"]
    elif operator == "query_duplicate":
        queries.append(copy.deepcopy(queries[0]))
    elif operator == "query_omit":
        fixture["raw_fixture"]["query_records"] = []
    elif operator == "query_extra_field":
        queries[0]["alias"] = "forbidden"
    elif operator == "reference_identity":
        references[params["index"]]["identity"][params["position"]] =             params["value"]
    elif operator == "reference_value":
        value = references[params["index"]]["value"]
        numerator, denominator = reduce_pair(
            value["numerator"] + params["delta"], value["denominator"])
        value.update(numerator=numerator, denominator=denominator)
    elif operator == "reference_omit":
        del references[params["index"]]
    elif operator == "reference_add":
        references.append({
            "identity": expected_reference_identity(20000),
            "value": {"denominator": 1, "numerator": 1},
        })
    elif operator in {"reference_duplicate_identity",
                      "reference_duplicate_record"}:
        references[params["target_index"]] =             copy.deepcopy(references[params["source_index"]])
    elif operator == "reference_reverse_order":
        references.reverse()
    elif operator == "reference_outer_bank":
        references[params["index"]]["identity"][13] = "outer"
    elif operator == "reference_self_selected":
        references[params["index"]]["identity"][4] =             "query-v5-family-001"
    elif operator == "reference_nonreduced":
        value = references[params["index"]]["value"]
        value["numerator"] *= params["multiplier"]
        value["denominator"] *= params["multiplier"]
    elif operator == "reference_negative_numerator":
        references[params["index"]]["value"]["numerator"] = -1
    elif operator == "reference_zero_denominator":
        references[params["index"]]["value"]["denominator"] = 0
    elif operator == "reference_identity_short":
        references[params["index"]]["identity"].pop()
    elif operator == "reference_identity_long":
        references[params["index"]]["identity"].append(None)
    elif operator == "reference_selector_query_id":
        references[params["index"]]["identity"][16] = params["value"]
    elif operator == "reference_extra_field":
        references[params["index"]]["alias"] = "forbidden"
    elif operator == "reference_swap_adjacent":
        left, right = params["left"], params["right"]
        references[left], references[right] = references[right], references[left]
    elif operator == "reference_value_string":
        references[params["index"]]["value"]["numerator"] = "0"
    elif operator == "reference_identity_boolean_replicate":
        references[params["index"]]["identity"][12] = False
    elif operator == "reference_query_alias":
        references[params["index"]]["identity"][16] = "q-v5-family-density-alias"
    elif operator == "lockstep_counterfeit":
        fixture["expected_derived"]["selected_operating_row"] = {
            "factor_base_size": 22,
            "row_density": {"denominator": 48, "numerator": 8},
            "rule":
                "minimum_exact_distance_to_1_over_6_then_smaller_factor_base_size",
            "target_density": {"denominator": 6, "numerator": 1},
        }
        p_value = fixture["expected_derived"]["p_value_numerator"]
        p_value["reference_greater_or_equal_count"] = 17
        p_value["value"] = 18
        refresh_stored_dependent_hashes(fixture)
    elif operator == "selected_output_only":
        fixture["expected_derived"]["selected_operating_row"][
            "factor_base_size"] = 22
    elif operator == "p_output_only":
        fixture["expected_derived"]["p_value_numerator"]["value"] = 10000
    elif operator == "stale_hash":
        fixture["expected_derived"]["hashes"][params["name"]] = "0" * 64
    elif operator == "coordinated_selected_and_hash":
        fixture["expected_derived"]["selected_operating_row"][
            "factor_base_size"] = 22
        refresh_stored_dependent_hashes(fixture)
    elif operator == "coordinated_p_and_hash":
        fixture["expected_derived"]["p_value_numerator"]["value"] = 10000
        refresh_stored_dependent_hashes(fixture)
    elif operator == "unknown_top_level_key":
        fixture["forbidden_alias"] = True
    else:
        fail("unknown_mutation_operator", operator)
    return fixture


def run_self_tests(
    fixture: dict[str, Any], raw_fixture_bytes: bytes
) -> dict[str, Any]:
    positive = validate_fixture_object(fixture)
    rejected = 0
    failures: list[dict[str, str]] = []
    for mutation in fixture["mutation_suite"]:
        operator = mutation["operator"]
        expected = mutation["expected_error"]
        try:
            if operator == "duplicate_json_key":
                mutated_raw = b'{"authority_boundary":null,' +                     raw_fixture_bytes[1:]
                strict_json_load(
                    mutated_raw, terminal_lf=True,
                    canonical_code="artifact_not_canonical")
            elif operator == "noncanonical_artifact_json":
                strict_json_load(
                    b" " + raw_fixture_bytes, terminal_lf=True,
                    canonical_code="artifact_not_canonical")
            else:
                validate_fixture_object(apply_mutation(fixture, mutation))
        except ValidationError as exc:
            if exc.code == expected:
                rejected += 1
            else:
                failures.append({
                    "actual_error": exc.code,
                    "expected_error": expected,
                    "id": mutation["id"],
                })
        else:
            failures.append({
                "actual_error": "accepted",
                "expected_error": expected,
                "id": mutation["id"],
            })
    if failures:
        fail("mutation_self_test_failure",
             canonical_bytes(failures).decode("utf-8"))
    return {
        **positive,
        "all_mutations_rejected_for_expected_reason": True,
        "mutations_rejected": rejected,
    }


def emit(value: Any, stream: Any = sys.stdout) -> None:
    stream.buffer.write(canonical_bytes(value, terminal_lf=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the complete static JINV v5 raw-derivation fixture; "
            "no experiment or network access is performed."
        )
    )
    parser.add_argument("--fixture", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--list-mutations", action="store_true")
    args = parser.parse_args(argv)

    try:
        fixture, raw = load_fixture(args.fixture)
        if args.list_mutations:
            validate_mutation_manifest(fixture)
            result = {
                "mutation_count": len(fixture["mutation_suite"]),
                "mutations": fixture["mutation_suite"],
                "schema": SCHEMA,
                "status": "listed",
            }
        elif args.self_test:
            result = {
                **run_self_tests(fixture, raw),
                "schema": SCHEMA,
                "scope": "static_protocol_integrity_only",
                "status": "pass",
            }
        else:
            result = {
                **validate_fixture_object(fixture),
                "schema": SCHEMA,
                "scope": "static_protocol_integrity_only",
                "status": "pass",
            }
        emit(result)
        return 0
    except ValidationError as exc:
        emit({
            "detail": exc.detail,
            "error": exc.code,
            "schema": SCHEMA,
            "scope": "static_protocol_integrity_only",
            "status": "fail",
        }, stream=sys.stderr)
        return 2
    except (OSError, UnicodeError) as exc:
        emit({
            "detail": str(exc),
            "error": "io_error",
            "schema": SCHEMA,
            "scope": "static_protocol_integrity_only",
            "status": "fail",
        }, stream=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
