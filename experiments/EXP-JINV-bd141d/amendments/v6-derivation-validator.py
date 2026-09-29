#!/usr/bin/env python3
"""Public static validator for the additive JINV amendment-v6 overlay.

This standard-library-only validator composes the immutable amendment-v5
positive fixture instead of duplicating its 20,000 explicit reference records.
It verifies the exact v5 fixture and validator bytes before parsing or loading
them, performs no network, harness, experiment, target, curve, or measurement
operation, and writes no cache files.

Deterministic static self-test invocation:

    python3 v6-derivation-validator.py \
        --fixture v6-derivation-fixtures.json --self-test

The 122-entry legacy mutation suite is consumed from the bound v5 fixture and
must retain every v5 first terminal.  The separate 45-entry type_alias_suite is
defined by the v6 overlay; its future first terminals are v6 fixture authority,
not values supplied by the queue's frozen v5 baseline classification.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import types
from pathlib import Path
from typing import Any


SCHEMA = "crypto.autoresearch.jinv_v6_type_strict_overlay.v1"
TASK_ID = "TASK-20260813-5b8a62"
EXPERIMENT_ID = "EXP-JINV-bd141d"
PROTOCOL_VERSION = 7
OVERLAY_SIZE_BYTES = 28105
OVERLAY_SHA256 = "7051d6038936c679b5380b2119cfab1e7a03294badb250dc1511ddfbd179301f"
BASE_FIXTURE_NAME = "v5-derivation-fixtures.json"
BASE_FIXTURE_SIZE_BYTES = 4946954
BASE_FIXTURE_SHA256 = "8b57cd8bb0cc0cb733c8c9182e57ce1dd291b08dbc293821837cda12f0b4a0df"
BASE_VALIDATOR_NAME = "v5-derivation-validator.py"
BASE_VALIDATOR_SIZE_BYTES = 42046
BASE_VALIDATOR_SHA256 = "4e93df23ef0c4d178e85187b8d327669479c85d8858b308a396c8da9111dbaee"
ALIAS_UNIVERSE_SHA256 = "595ccde1dca6db52b96fcb078b6c7735d8b39e87db0783e4e5d7b8a05fde4455"
ALIAS_SUITE_SHA256 = "7415d195d5c7c2cd099b566a5c123f4adb3f45fb19c2ccc7077b37cf23da9c43"
LEGACY_MUTATION_SHA256 = "e96a935985d2895c5f1e113245aca412c3b9a731e502274146bcf390b3f307b1"
TYPE_MANIFEST_SHA256 = "20ab60e1af5ca31f3c66586efbd3317dfcd81f7c90609129ebed19986769281f"
POSITIVE_HASHES = {
    "aggregate": "5621ffee02ade2af52c398de807b0f979a4a57a2b577e81924b1705be72aecd3",
    "candidate_table": "9383e1f73fa792001e5cacca4cfa84d0d8fba34c6e9107e6db40fef0a6519565",
    "p_value_numerator": "77376ff0b3a978f7b62247eb0ead10a365f6d64268e2b0b65f7e5b79799470f9",
    "query_record": "35c75978dc43b50c4e8ed5649a649c5e32352c15cc729d7ba7059dafbef4a44b",
    "reference_population": "8f8ac10f4b7889535508f136952236d2004b758a22f51363e65e136045b6eea8",
    "selected_operating_row": "3ae73601f050c441df7367f602ed9f1a378bebcf8f90a7f1b98cd2d7bc6019e4",
}
TOP_LEVEL_KEYS = {
    "authority_boundary", "base_fixture", "base_validator",
    "continuing_boundaries", "experiment_id", "fixture_scope",
    "frozen_protocol", "legacy_mutation_suite", "lineage",
    "positive_bindings", "preserved_boundaries", "protocol_version",
    "recursive_type_contract", "schema", "stored_object_binding_contract",
    "task_id", "type_alias_contract", "type_alias_suite",
    "type_alias_universe",
}
SEMANTIC_ROOTS = [
    "authority_boundary", "canonicalization_contract",
    "continuing_separate_blockers", "derivation_contract",
    "expected_derived", "mutation_contract", "preserved_v4_contract",
    "tie_fixture",
]
TYPE_NODE_COUNTS = {
    "boolean": 31,
    "dict": 40313,
    "integer": 100276,
    "list": 20036,
    "null": 100005,
    "string": 180689,
    "total": 441350,
}
STORED_OBJECTS = (
    "selected_operating_row", "p_value_numerator", "aggregate",
)
OUTPUT_ERRORS = {
    "selected_operating_row": "selected_output_mismatch",
    "p_value_numerator": "p_output_mismatch",
    "aggregate": "aggregate_output_mismatch",
}
HASH_ERRORS = {
    "selected_operating_row": "selected_hash_mismatch",
    "p_value_numerator": "p_hash_mismatch",
    "aggregate": "aggregate_hash_mismatch",
}


class ValidationError(ValueError):
    """Stable public static validation failure."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code + (": " + detail if detail else ""))
        self.code = code
        self.detail = detail


def fail(code: str, detail: str = "") -> None:
    raise ValidationError(code, detail)


def canonical_bytes(value: Any, terminal_lf: bool = False) -> bytes:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
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


def reject_noninteger_number(token: str) -> None:
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
            text,
            object_pairs_hook=reject_duplicate_pairs,
            parse_float=reject_noninteger_number,
            parse_constant=reject_noninteger_number,
        )
    except ValidationError:
        raise
    except json.JSONDecodeError as exc:
        fail("invalid_json", str(exc))
    if canonical_bytes(value, terminal_lf=terminal_lf) != data:
        fail(canonical_code)
    return value


def exact_keys(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        fail(code)
    return value


def plain_int(value: Any, code: str) -> int:
    if type(value) is not int:
        fail(code)
    return value


def exact_json_equal(left: Any, right: Any) -> bool:
    """Exact recursive JSON types plus exact canonical bytes."""
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        if set(left) != set(right):
            return False
        return all(exact_json_equal(left[key], right[key]) for key in left)
    if type(left) is list:
        if len(left) != len(right):
            return False
        return all(exact_json_equal(a, b) for a, b in zip(left, right))
    if type(left) not in {str, int, bool, type(None)}:
        return False
    return left == right and canonical_bytes(left) == canonical_bytes(right)


def path_join(parent: str, component: str | int) -> str:
    if type(component) is int:
        return parent + "[" + str(component) + "]"
    return component if not parent else parent + "." + component


def first_type_mismatch(actual: Any, template: Any, path: str = "") -> str | None:
    """Return the first deterministic recursive JSON type/shape mismatch."""
    if type(actual) is not type(template):
        return path
    if type(actual) is dict:
        if set(actual) != set(template):
            return path
        for key in sorted(template):
            mismatch = first_type_mismatch(
                actual[key], template[key], path_join(path, key)
            )
            if mismatch is not None:
                return mismatch
        return None
    if type(actual) is list:
        if len(actual) != len(template):
            return path
        for index, (left, right) in enumerate(zip(actual, template)):
            mismatch = first_type_mismatch(
                left, right, path_join(path, index)
            )
            if mismatch is not None:
                return mismatch
        return None
    if type(actual) not in {str, int, bool, type(None)}:
        return path
    return None


def recursive_type_manifest(value: Any) -> tuple[str, dict[str, int]]:
    """Hash every key, container, and scalar type without trusting values."""
    digest = hashlib.sha256()
    digest.update(b"jinv-v6-recursive-type-tree-v1:")
    counts = {
        "boolean": 0,
        "dict": 0,
        "integer": 0,
        "list": 0,
        "null": 0,
        "string": 0,
        "total": 0,
    }

    def visit(item: Any) -> None:
        counts["total"] += 1
        if item is None:
            counts["null"] += 1
            digest.update(b"N")
        elif type(item) is list:
            counts["list"] += 1
            digest.update(b"L[")
            for child in item:
                visit(child)
            digest.update(b"]")
        elif type(item) is dict:
            counts["dict"] += 1
            digest.update(b"D{")
            for key in sorted(item):
                if type(key) is not str:
                    fail("recursive_type_mismatch", "non-string object key")
                digest.update(canonical_bytes(key))
                digest.update(b":")
                visit(item[key])
            digest.update(b"}")
        elif type(item) is str:
            counts["string"] += 1
            digest.update(b"S")
        elif type(item) is int:
            counts["integer"] += 1
            digest.update(b"I")
        elif type(item) is bool:
            counts["boolean"] += 1
            digest.update(b"B")
        else:
            fail("recursive_type_mismatch", type(item).__name__)

    visit(value)
    return digest.hexdigest(), counts


def parse_semantic_path(path: str) -> list[str | int]:
    if type(path) is not str or not path:
        fail("type_alias_path")
    result: list[str | int] = []
    index = 0
    while index < len(path):
        if path[index] == ".":
            index += 1
            continue
        if path[index] == "[":
            end = path.find("]", index)
            if end < 0 or not path[index + 1:end].isdigit():
                fail("type_alias_path", path)
            result.append(int(path[index + 1:end]))
            index = end + 1
            continue
        end = index
        while end < len(path) and path[end] not in ".[":
            end += 1
        component = path[index:end]
        if not component:
            fail("type_alias_path", path)
        result.append(component)
        index = end
    return result


def get_path(root: Any, path: str) -> Any:
    cursor = root
    for component in parse_semantic_path(path):
        cursor = cursor[component]
    return cursor


def set_path(root: Any, path: str, value: Any) -> None:
    components = parse_semantic_path(path)
    cursor = root
    for component in components[:-1]:
        cursor = cursor[component]
    cursor[components[-1]] = value


def read_exact_file(path: Path, size: int, digest: str, code: str) -> bytes:
    try:
        data = path.read_bytes()
    except OSError as exc:
        fail(code, str(exc))
    if len(data) != size or sha256_hex(data) != digest:
        fail(code, str(path))
    return data


def load_overlay(path: str) -> tuple[dict[str, Any], bytes]:
    raw = read_exact_file(
        Path(path), OVERLAY_SIZE_BYTES, OVERLAY_SHA256,
        "overlay_source_binding_mismatch",
    )
    overlay = strict_json_load(
        raw, terminal_lf=True, canonical_code="overlay_not_canonical"
    )
    if type(overlay) is not dict:
        fail("overlay_shape")
    return overlay, raw


def load_v5_module(script_dir: Path, overlay: dict[str, Any]) -> Any:
    binding = exact_keys(
        overlay["base_validator"],
        {"repository_path", "sha256", "size_bytes"},
        "base_validator_binding",
    )
    if (
        binding["repository_path"]
        != "experiments/EXP-JINV-bd141d/amendments/" + BASE_VALIDATOR_NAME
        or binding["sha256"] != BASE_VALIDATOR_SHA256
        or plain_int(binding["size_bytes"], "base_validator_binding")
        != BASE_VALIDATOR_SIZE_BYTES
    ):
        fail("base_validator_binding")
    path = script_dir / BASE_VALIDATOR_NAME
    source = read_exact_file(
        path, BASE_VALIDATOR_SIZE_BYTES, BASE_VALIDATOR_SHA256,
        "base_validator_source_binding_mismatch",
    )
    module = types.ModuleType("_bound_jinv_v5_derivation_validator")
    module.__file__ = str(path)
    try:
        code = compile(source, str(path), "exec")
        exec(code, module.__dict__)
    except Exception as exc:
        fail("base_validator_load_failure", str(exc))
    for name in (
        "ValidationError", "apply_mutation", "canonical_bytes",
        "derive_pass", "strict_json_load", "validate_fixture_object",
    ):
        if not hasattr(module, name):
            fail("base_validator_interface", name)
    if (
        module.SCHEMA != "crypto.autoresearch.jinv_v5_derivation_fixtures.v1"
        or module.PROTOCOL_VERSION != 6
    ):
        fail("base_validator_interface")
    return module


def load_base_fixture(
    script_dir: Path, overlay: dict[str, Any]
) -> tuple[dict[str, Any], bytes]:
    binding = exact_keys(
        overlay["base_fixture"],
        {"canonical_encoding", "repository_path", "schema", "sha256",
         "size_bytes"},
        "base_fixture_binding",
    )
    expected_path = (
        "experiments/EXP-JINV-bd141d/amendments/" + BASE_FIXTURE_NAME
    )
    if (
        binding["canonical_encoding"]
        != "UTF8_RFC8259_recursively_sorted_keys_compact_one_terminal_LF"
        or binding["repository_path"] != expected_path
        or binding["schema"]
        != "crypto.autoresearch.jinv_v5_derivation_fixtures.v1"
        or binding["sha256"] != BASE_FIXTURE_SHA256
        or plain_int(binding["size_bytes"], "base_fixture_binding")
        != BASE_FIXTURE_SIZE_BYTES
    ):
        fail("base_fixture_binding")
    raw = read_exact_file(
        script_dir / BASE_FIXTURE_NAME,
        BASE_FIXTURE_SIZE_BYTES,
        BASE_FIXTURE_SHA256,
        "base_fixture_source_binding_mismatch",
    )
    base = strict_json_load(
        raw, terminal_lf=True, canonical_code="base_fixture_not_canonical"
    )
    if type(base) is not dict:
        fail("base_fixture_shape")
    return base, raw


def validate_overlay_contract(overlay: dict[str, Any]) -> dict[str, str]:
    exact_keys(overlay, TOP_LEVEL_KEYS, "overlay_shape")
    if overlay["schema"] != SCHEMA:
        fail("overlay_schema")
    if overlay["task_id"] != TASK_ID:
        fail("overlay_task_id")
    if overlay["experiment_id"] != EXPERIMENT_ID:
        fail("overlay_experiment_id")
    if plain_int(overlay["protocol_version"], "overlay_protocol_version") != 7:
        fail("overlay_protocol_version")
    if overlay["fixture_scope"] != (
        "additive_future_only_static_type_strictness_overlay_no_measurement_no_execution"
    ):
        fail("overlay_scope")

    protocol = exact_keys(
        overlay["frozen_protocol"],
        {"affected_runs", "amendment_ordinal", "applies_to",
         "base_protocol_version", "controlling_objection_id",
         "resulting_protocol_version"},
        "frozen_protocol",
    )
    if (
        type(protocol["affected_runs"]) is not list
        or protocol["affected_runs"]
        or plain_int(protocol["amendment_ordinal"], "frozen_protocol") != 6
        or protocol["applies_to"] != "future_runs_only"
        or plain_int(protocol["base_protocol_version"], "frozen_protocol") != 6
        or protocol["controlling_objection_id"] != "O-JINV-V6-7f11a5"
        or plain_int(protocol["resulting_protocol_version"], "frozen_protocol") != 7
    ):
        fail("frozen_protocol")

    universe = exact_keys(
        overlay["type_alias_universe"],
        {"baseline_classification_source", "enumeration_encoding",
         "exact_position_count", "manifest_sha256", "positions",
         "semantic_roots", "terminal_v5_accepted_count",
         "terminal_v5_rejected_count"},
        "type_alias_universe",
    )
    positions = universe["positions"]
    if type(positions) is not list or len(positions) != 45:
        fail("type_alias_universe")
    if (
        universe["enumeration_encoding"]
        != "UTF8_RFC8259_recursively_sorted_keys_compact_no_terminal_LF"
        or universe["manifest_sha256"] != ALIAS_UNIVERSE_SHA256
        or sha256_hex(canonical_bytes(positions)) != ALIAS_UNIVERSE_SHA256
        or plain_int(universe["exact_position_count"], "type_alias_universe") != 45
        or plain_int(universe["terminal_v5_accepted_count"], "type_alias_universe") != 36
        or plain_int(universe["terminal_v5_rejected_count"], "type_alias_universe") != 9
        or not exact_json_equal(universe["semantic_roots"], SEMANTIC_ROOTS)
    ):
        fail("type_alias_universe")

    suite = overlay["type_alias_suite"]
    if type(suite) is not list or len(suite) != 45:
        fail("type_alias_contract")
    if sha256_hex(canonical_bytes(suite)) != ALIAS_SUITE_SHA256:
        fail("type_alias_manifest_hash")
    ids: set[str] = set()
    paths: set[str] = set()
    terminal_counts: dict[str, int] = {}
    v5_accepted = 0
    v5_rejected = 0
    for index, (position, case) in enumerate(zip(positions, suite)):
        exact_keys(
            position,
            {"alias_type", "alias_value", "path", "terminal_v5_first_terminal",
             "terminal_v5_result", "type", "value"},
            "type_alias_position_shape",
        )
        exact_keys(
            case,
            {"alias_type", "alias_value", "expected_error", "id", "operator",
             "path", "position_index", "source_type", "source_value"},
            "type_alias_case_shape",
        )
        expected_id = "TA-" + str(index + 1).zfill(3)
        if (
            case["id"] != expected_id
            or case["id"] in ids
            or case["path"] in paths
            or case["operator"] != "set_semantic_path"
            or plain_int(case["position_index"], "type_alias_coverage") != index
            or case["path"] != position["path"]
            or case["source_type"] != position["type"]
            or not exact_json_equal(case["source_value"], position["value"])
            or case["alias_type"] != position["alias_type"]
            or not exact_json_equal(case["alias_value"], position["alias_value"])
            or type(case["expected_error"]) is not str
            or not case["expected_error"]
        ):
            fail("type_alias_coverage")
        ids.add(case["id"])
        paths.add(case["path"])
        root = case["path"].split(".", 1)[0]
        if root not in SEMANTIC_ROOTS:
            fail("type_alias_coverage")
        if position["terminal_v5_result"] == "accepted":
            v5_accepted += 1
            if position["terminal_v5_first_terminal"] is not None:
                fail("type_alias_v5_baseline")
        elif position["terminal_v5_result"] == "rejected":
            v5_rejected += 1
            if type(position["terminal_v5_first_terminal"]) is not str:
                fail("type_alias_v5_baseline")
        else:
            fail("type_alias_v5_baseline")
        terminal_counts[case["expected_error"]] = (
            terminal_counts.get(case["expected_error"], 0) + 1
        )
    if v5_accepted != 36 or v5_rejected != 9:
        fail("type_alias_v5_baseline")

    contract = exact_keys(
        overlay["type_alias_contract"],
        {"coverage_enumeration_parity_required", "declared_case_count",
         "exact_rejections_required", "expected_first_terminal_source",
         "manifest_sha256", "positive_fixture_must_pass_before_cases",
         "suite_name", "terminal_counts"},
        "type_alias_contract",
    )
    if (
        contract["coverage_enumeration_parity_required"] is not True
        or plain_int(contract["declared_case_count"], "type_alias_contract") != 45
        or plain_int(contract["exact_rejections_required"], "type_alias_contract") != 45
        or contract["expected_first_terminal_source"]
        != "this_v6_fixture_is_new_authority_queue_only_froze_v5_baseline_classification"
        or contract["manifest_sha256"] != ALIAS_SUITE_SHA256
        or contract["positive_fixture_must_pass_before_cases"] is not True
        or contract["suite_name"] != "type_alias_suite"
        or not exact_json_equal(contract["terminal_counts"], terminal_counts)
    ):
        fail("type_alias_contract")

    type_contract = exact_keys(
        overlay["recursive_type_contract"],
        {"exact_container_types", "exact_scalar_types", "latent_container_probes",
         "manifest_algorithm", "manifest_node_counts", "manifest_sha256",
         "object_comparison", "plain_integer_excludes_boolean",
         "python_structural_equality_alone", "scope"},
        "recursive_type_contract",
    )
    if (
        type_contract["manifest_sha256"] != TYPE_MANIFEST_SHA256
        or not exact_json_equal(type_contract["manifest_node_counts"], TYPE_NODE_COUNTS)
        or type_contract["plain_integer_excludes_boolean"] is not True
        or type_contract["python_structural_equality_alone"] != "prohibited"
        or type_contract["object_comparison"]
        != "canonical_byte_equality_and_recursively_type_tagged_exact_equality"
    ):
        fail("recursive_type_contract")
    probes = type_contract["latent_container_probes"]
    if type(probes) is not list or len(probes) != 2:
        fail("recursive_type_contract")
    for index, probe in enumerate(probes):
        exact_keys(
            probe,
            {"expected_error", "id", "operator", "path", "replacement",
             "replacement_type", "source_type"},
            "latent_container_probe_shape",
        )
        if (
            probe["id"] != "LT-" + str(index + 1).zfill(3)
            or probe["operator"] != "replace_semantic_container"
            or probe["source_type"] not in {"dict", "list"}
            or probe["replacement_type"] not in {"dict", "list"}
            or probe["source_type"] == probe["replacement_type"]
            or type(probe["expected_error"]) is not str
            or type(probe["path"]) is not str
        ):
            fail("latent_container_probe_shape")

    stored = exact_keys(
        overlay["stored_object_binding_contract"],
        {"computation_order", "legacy_diagnostic_precedence", "objects"},
        "stored_object_binding_contract",
    )
    if not exact_json_equal(stored["objects"], list(STORED_OBJECTS)):
        fail("stored_object_binding_contract")
    if not exact_json_equal(
        stored["computation_order"],
        ["validate_recursive_types", "hash_canonical_stored_object",
         "compare_stored_hash",
         "compare_stored_and_independently_derived_canonical_bytes_and_recursive_types",
         "compare_stored_hash_and_independently_derived_hash"],
    ):
        fail("stored_object_binding_contract")

    return {case["path"]: case["expected_error"] for case in suite}


def translate_v5_error(v5: Any, operation: Any) -> Any:
    try:
        return operation()
    except v5.ValidationError as exc:
        fail(exc.code, exc.detail)


def compute_binding_audit(fixture: dict[str, Any], v5: Any) -> dict[str, Any]:
    raw = fixture["raw_fixture"]
    rows = raw["candidate_rows"]
    query = raw["query_records"][0]
    references = raw["reference_records"]
    ascending = v5.derive_pass(rows, query, references, descending=False)
    descending = v5.derive_pass(rows, query, references, descending=True)
    audit: dict[str, Any] = {
        "ascending": ascending,
        "descending": descending,
        "objects": {},
        "order_identity": {},
    }
    expected = fixture["expected_derived"]
    for name in STORED_OBJECTS:
        stored_object = expected[name]
        stored_hash = expected["hashes"][name]
        derived_object = ascending[name]
        derived_hash = ascending["hashes"][name]
        stored_object_hash = sha256_hex(canonical_bytes(stored_object))
        audit["order_identity"][name] = exact_json_equal(
            ascending[name], descending[name]
        )
        audit["objects"][name] = {
            "stored_object_hash": stored_object_hash,
            "stored_hash": stored_hash,
            "derived_hash": derived_hash,
            "stored_hash_matches_stored_object": stored_object_hash == stored_hash,
            "stored_object_matches_derived": exact_json_equal(
                stored_object, derived_object
            ),
            "stored_hash_matches_derived": stored_hash == derived_hash,
        }
    return audit


def enforce_binding_audit(audit: dict[str, Any]) -> dict[str, bool]:
    # All predicates were computed before diagnostic arbitration.  Existing
    # output-mismatch terminals win for M-105/M-106 only because their stored
    # dependent hashes still equal the independently derived hashes.  A stale
    # or otherwise divergent dependent hash keeps the legacy hash terminal
    # (M-107/M-108/M-109).  Coordinated M-113/M-114 object-plus-hash changes
    # pass that first predicate and then retain their output-mismatch terminal.
    for name in STORED_OBJECTS:
        if audit["order_identity"][name] is not True:
            fail("order_pass_mismatch", name)
        item = audit["objects"][name]
        if item["stored_hash_matches_stored_object"] is not True:
            if item["stored_hash_matches_derived"] is True:
                fail(OUTPUT_ERRORS[name])
            fail(HASH_ERRORS[name])
        if item["stored_object_matches_derived"] is not True:
            fail(OUTPUT_ERRORS[name])
        if item["stored_hash_matches_derived"] is not True:
            fail(HASH_ERRORS[name])
    return {
        "aggregate": True,
        "p_value_numerator": True,
        "selected_operating_row": True,
    }


def validate_v6_semantic_fixture(
    fixture: dict[str, Any], template: dict[str, Any], overlay: dict[str, Any],
    alias_terminals: dict[str, str], v5: Any,
) -> dict[str, Any]:
    # Compute recursive-type and stored-binding predicates first.  Diagnostics
    # are deliberately arbitrated after the frozen v5 validator so every one
    # of the 122 legacy mutations retains its existing first terminal.
    mismatch = first_type_mismatch(fixture, template)
    binding_audit: dict[str, Any] | None = None
    try:
        binding_audit = compute_binding_audit(fixture, v5)
    except Exception:
        # Invalid legacy raw shapes are classified by the frozen v5 validator.
        binding_audit = None

    try:
        positive = v5.validate_fixture_object(fixture)
    except v5.ValidationError as exc:
        # Frozen v5 ValidationError diagnostics always retain precedence.
        fail(exc.code, exc.detail)
    except Exception as exc:
        # Arbitrary latent container/scalar shape drift must never escape as a
        # Python traceback.  A precomputed mismatch gets its alias-specific or
        # generic recursive-type terminal; otherwise the frozen validator has
        # suffered a stable, fail-closed internal-validation failure.
        if mismatch is not None:
            fail(alias_terminals.get(mismatch, "recursive_type_mismatch"), mismatch)
        fail("base_validator_internal_failure", type(exc).__name__)
    if mismatch is not None:
        fail(alias_terminals.get(mismatch, "recursive_type_mismatch"), mismatch)

    manifest, counts = recursive_type_manifest(fixture)
    if manifest != TYPE_MANIFEST_SHA256 or not exact_json_equal(
        counts, TYPE_NODE_COUNTS
    ):
        fail("recursive_type_manifest_mismatch")
    if binding_audit is None:
        fail("stored_object_binding_unavailable")
    stored_verified = enforce_binding_audit(binding_audit)

    hashes = fixture["expected_derived"]["hashes"]
    if not exact_json_equal(hashes, POSITIVE_HASHES):
        fail("positive_hash_binding")
    positive_binding = overlay["positive_bindings"]
    if (
        positive_binding["selected_factor_base_size"] != 8
        or not exact_json_equal(
            positive_binding["selected_density"],
            {"denominator": 6, "numerator": 1},
        )
        or positive_binding["reference_greater_or_equal_count"] != 10000
        or positive_binding["reference_equal_count"] != 1
        or positive_binding["p_value_numerator"] != 10001
        or positive_binding["p_value_denominator"] != 20001
        or positive_binding["independent_ascending_descending_identity"] is not True
        or positive_binding["prior_lockstep_counterfeit_rejected"] is not True
    ):
        fail("positive_binding")
    for name, overlay_name in (
        ("aggregate", "aggregate_sha256"),
        ("candidate_table", "candidate_table_sha256"),
        ("p_value_numerator", "p_value_numerator_sha256"),
        ("query_record", "query_record_sha256"),
        ("reference_population", "reference_population_sha256"),
        ("selected_operating_row", "selected_operating_row_sha256"),
    ):
        if positive_binding[overlay_name] != POSITIVE_HASHES[name]:
            fail("positive_binding", name)

    return {
        **positive,
        "recursive_type_manifest_sha256": manifest,
        "recursive_type_nodes_verified": counts["total"],
        "stored_object_bindings_verified": stored_verified,
    }


def validate_legacy_manifest(base: dict[str, Any], overlay: dict[str, Any]) -> None:
    binding = exact_keys(
        overlay["legacy_mutation_suite"],
        {"byte_for_byte_manifest_preservation_required", "exact_count",
         "exact_rejections_required", "existing_first_terminal_precedence_must_remain_unchanged",
         "manifest_sha256", "source", "suite_name"},
        "legacy_mutation_contract",
    )
    suite = base["mutation_suite"]
    if (
        type(suite) is not list
        or len(suite) != 122
        or sha256_hex(canonical_bytes(suite)) != LEGACY_MUTATION_SHA256
        or binding["byte_for_byte_manifest_preservation_required"] is not True
        or binding["existing_first_terminal_precedence_must_remain_unchanged"] is not True
        or plain_int(binding["exact_count"], "legacy_mutation_contract") != 122
        or plain_int(binding["exact_rejections_required"], "legacy_mutation_contract") != 122
        or binding["manifest_sha256"] != LEGACY_MUTATION_SHA256
        or binding["source"] != "base_fixture.mutation_suite"
        or binding["suite_name"] != "mutation_suite"
    ):
        fail("legacy_mutation_contract")


def run_legacy_suite(
    base: dict[str, Any], raw: bytes, overlay: dict[str, Any],
    alias_terminals: dict[str, str], v5: Any,
) -> int:
    validate_legacy_manifest(base, overlay)
    rejected = 0
    failures: list[dict[str, str]] = []
    for mutation in base["mutation_suite"]:
        expected = mutation["expected_error"]
        try:
            if mutation["operator"] == "duplicate_json_key":
                mutated_raw = b'{"authority_boundary":null,' + raw[1:]
                strict_json_load(
                    mutated_raw, terminal_lf=True,
                    canonical_code="artifact_not_canonical",
                )
            elif mutation["operator"] == "noncanonical_artifact_json":
                strict_json_load(
                    b" " + raw, terminal_lf=True,
                    canonical_code="artifact_not_canonical",
                )
            else:
                mutated = translate_v5_error(
                    v5, lambda mutation=mutation: v5.apply_mutation(base, mutation)
                )
                validate_v6_semantic_fixture(
                    mutated, base, overlay, alias_terminals, v5
                )
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
        fail(
            "legacy_mutation_self_test_failure",
            canonical_bytes(failures).decode("utf-8"),
        )
    return rejected


def classify_v5(v5: Any, fixture: dict[str, Any]) -> tuple[str, str | None]:
    try:
        v5.validate_fixture_object(fixture)
    except v5.ValidationError as exc:
        return "rejected", exc.code
    return "accepted", None


def run_type_alias_suite(
    base: dict[str, Any], overlay: dict[str, Any],
    alias_terminals: dict[str, str], v5: Any,
) -> dict[str, int]:
    positions = overlay["type_alias_universe"]["positions"]
    cases = overlay["type_alias_suite"]
    rejected = 0
    v5_accepted = 0
    v5_rejected = 0
    failures: list[dict[str, str]] = []
    for position, case in zip(positions, cases):
        source = get_path(base, case["path"])
        if not exact_json_equal(source, case["source_value"]):
            fail("type_alias_source_binding", case["id"])
        mutated = copy.deepcopy(base)
        set_path(mutated, case["path"], copy.deepcopy(case["alias_value"]))
        reparsed = strict_json_load(
            canonical_bytes(mutated, terminal_lf=True),
            terminal_lf=True,
            canonical_code="type_alias_not_canonical",
        )

        result, terminal = classify_v5(v5, reparsed)
        if result != position["terminal_v5_result"] or not exact_json_equal(
            terminal, position["terminal_v5_first_terminal"]
        ):
            failures.append({
                "actual_error": terminal or "accepted",
                "expected_error": position["terminal_v5_first_terminal"] or "accepted",
                "id": case["id"] + "-v5-baseline",
            })
        if result == "accepted":
            v5_accepted += 1
        else:
            v5_rejected += 1

        try:
            validate_v6_semantic_fixture(
                reparsed, base, overlay, alias_terminals, v5
            )
        except ValidationError as exc:
            if exc.code == case["expected_error"]:
                rejected += 1
            else:
                failures.append({
                    "actual_error": exc.code,
                    "expected_error": case["expected_error"],
                    "id": case["id"],
                })
        else:
            failures.append({
                "actual_error": "accepted",
                "expected_error": case["expected_error"],
                "id": case["id"],
            })
    if failures:
        fail(
            "type_alias_self_test_failure",
            canonical_bytes(failures).decode("utf-8"),
        )
    if rejected != 45 or v5_accepted != 36 or v5_rejected != 9:
        fail("type_alias_count_mismatch")
    return {
        "type_aliases_rejected": rejected,
        "v5_aliases_accepted": v5_accepted,
        "v5_aliases_rejected": v5_rejected,
    }


def run_latent_container_probes(
    base: dict[str, Any], overlay: dict[str, Any],
    alias_terminals: dict[str, str], v5: Any,
) -> int:
    probes = overlay["recursive_type_contract"]["latent_container_probes"]
    rejected = 0
    failures: list[dict[str, str]] = []
    for probe in probes:
        source = get_path(base, probe["path"])
        if (
            (probe["source_type"] == "dict" and type(source) is not dict)
            or (probe["source_type"] == "list" and type(source) is not list)
        ):
            fail("latent_container_source_binding", probe["id"])
        replacement = copy.deepcopy(probe["replacement"])
        if (
            (probe["replacement_type"] == "dict" and type(replacement) is not dict)
            or (probe["replacement_type"] == "list" and type(replacement) is not list)
        ):
            fail("latent_container_probe_shape", probe["id"])
        mutated = copy.deepcopy(base)
        set_path(mutated, probe["path"], replacement)
        reparsed = strict_json_load(
            canonical_bytes(mutated, terminal_lf=True),
            terminal_lf=True,
            canonical_code="latent_container_probe_not_canonical",
        )
        try:
            validate_v6_semantic_fixture(
                reparsed, base, overlay, alias_terminals, v5
            )
        except ValidationError as exc:
            if exc.code == probe["expected_error"]:
                rejected += 1
            else:
                failures.append({
                    "actual_error": exc.code,
                    "expected_error": probe["expected_error"],
                    "id": probe["id"],
                })
        else:
            failures.append({
                "actual_error": "accepted",
                "expected_error": probe["expected_error"],
                "id": probe["id"],
            })
    if failures:
        fail(
            "latent_container_self_test_failure",
            canonical_bytes(failures).decode("utf-8"),
        )
    return rejected


def static_context(
    fixture_path: str,
) -> tuple[dict[str, Any], dict[str, Any], bytes, Any, dict[str, str]]:
    overlay, _ = load_overlay(fixture_path)
    alias_terminals = validate_overlay_contract(overlay)
    script_dir = Path(__file__).resolve().parent
    v5 = load_v5_module(script_dir, overlay)
    base, raw = load_base_fixture(script_dir, overlay)
    validate_legacy_manifest(base, overlay)
    return overlay, base, raw, v5, alias_terminals


def emit(value: Any, stream: Any = sys.stdout) -> None:
    stream.buffer.write(canonical_bytes(value, terminal_lf=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the additive static JINV v6 type-strictness overlay; "
            "no experiment, target, curve, network, or measurement access."
        )
    )
    parser.add_argument("--fixture", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--list-mutations", action="store_true")
    mode.add_argument("--list-type-aliases", action="store_true")
    args = parser.parse_args(argv)

    try:
        overlay, base, raw, v5, alias_terminals = static_context(args.fixture)
        if args.list_mutations:
            result = {
                "legacy_mutation_count": len(base["mutation_suite"]),
                "legacy_mutation_manifest_sha256": LEGACY_MUTATION_SHA256,
                "mutations": base["mutation_suite"],
                "schema": SCHEMA,
                "scope": "static_protocol_integrity_only",
                "status": "listed",
            }
        elif args.list_type_aliases:
            result = {
                "schema": SCHEMA,
                "scope": "static_protocol_integrity_only",
                "status": "listed",
                "type_alias_count": len(overlay["type_alias_suite"]),
                "type_alias_manifest_sha256": ALIAS_SUITE_SHA256,
                "type_aliases": overlay["type_alias_suite"],
                "type_alias_universe_manifest_sha256": ALIAS_UNIVERSE_SHA256,
            }
        else:
            positive = validate_v6_semantic_fixture(
                base, base, overlay, alias_terminals, v5
            )
            result = {
                **positive,
                "base_fixture_sha256": BASE_FIXTURE_SHA256,
                "base_validator_sha256": BASE_VALIDATOR_SHA256,
                "coverage_enumeration_parity": True,
                "legacy_mutation_count": 122,
                "legacy_mutation_manifest_sha256": LEGACY_MUTATION_SHA256,
                "overlay_sha256": OVERLAY_SHA256,
                "protocol_version": PROTOCOL_VERSION,
                "schema": SCHEMA,
                "scope": "static_protocol_integrity_only",
                "status": "pass",
                "type_alias_count": 45,
                "type_alias_manifest_sha256": ALIAS_SUITE_SHA256,
                "type_alias_universe_manifest_sha256": ALIAS_UNIVERSE_SHA256,
            }
            if args.self_test:
                legacy_rejected = run_legacy_suite(
                    base, raw, overlay, alias_terminals, v5
                )
                aliases = run_type_alias_suite(
                    base, overlay, alias_terminals, v5
                )
                latent_rejected = run_latent_container_probes(
                    base, overlay, alias_terminals, v5
                )
                result.update({
                    **aliases,
                    "all_legacy_mutations_rejected_for_exact_terminal": True,
                    "all_latent_container_probes_rejected_for_exact_terminal": True,
                    "all_type_aliases_rejected_for_exact_terminal": True,
                    "legacy_mutations_rejected": legacy_rejected,
                    "latent_container_probes_rejected": latent_rejected,
                })
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
    except Exception as exc:
        emit({
            "detail": type(exc).__name__,
            "error": "internal_validation_failure",
            "schema": SCHEMA,
            "scope": "static_protocol_integrity_only",
            "status": "fail",
        }, stream=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
