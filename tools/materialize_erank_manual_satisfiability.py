#!/usr/bin/env python3
"""Materialize the frozen T33 manual-satisfiability mapping.

This is documentation/schema tooling.  It reads one immutable YAML
specification, walks only the four schemas and six positive fixture scopes
embedded in that specification, and emits a standalone deep-copy with an
exhaustive mapping.  It does not open campaign inputs or execute mathematical
research.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml


TASK_ID = "TASK-20260824-e77946"
GOAL_ID = "GOAL-ECQ-bef741"
BATCH_ID = "BATCH-9fa73f"
PINNED_HEAD = "5d7128862e01cac415b553fadd9266d26ee6ffc6"
RECORDED_AT_UTC = "2026-08-24T20:20:22Z"

SOURCE_PATH = Path(
    "coordination/goals/GOAL-ECQ-bef741/batches/BATCH-9fa73f/tasks/"
    "TASK-20260824-1474af/repair-specification.yaml"
)
SOURCE_SHA256 = "743f73a579038149365635910ef0502e34c8c02ff2c46437dc3a962d60c40309"
HANDOFF_PATH = Path("ledger/handoffs/TASK-20260824-e77946.yaml")
HANDOFF_SHA256 = "2587ffd1bfb81f08d1211dbeaf323a2fda59d01810ff93ed224ab1e8b24b4b4c"
DECISION_PATH = Path("ledger/decisions/DEC-20260824-19b5fb.yaml")
DECISION_SHA256 = "91b548f0d0f24391df67c0f512b2642549380ccabea7e50edf737afd880cda38"
T37_PATH = Path(
    "coordination/goals/GOAL-ECQ-bef741/batches/BATCH-9fa73f/tasks/"
    "TASK-20260824-f59e33/repair-specification.yaml"
)
T37_SHA256 = "774db153a4d27846acaa294478000c7408be6f0253cff156e86ff972b9258954"
T38_RECEIPT_PATH = Path(
    "coordination/goals/GOAL-ECQ-bef741/batches/BATCH-9fa73f/archives/"
    "TASK-20260824-946fb3/receipt.yaml"
)
T38_RECEIPT_SHA256 = "47c648db0046f567b911b6bc00c1f571f34dbca4886c4152217c19f9d5587887"
T40_RECEIPT_PATH = Path(
    "coordination/goals/GOAL-ECQ-bef741/batches/BATCH-9fa73f/archives/"
    "TASK-20260824-ad4c82/receipt.yaml"
)
T40_RECEIPT_SHA256 = "54ac47804a89586b9af584daf15962bfe5e95dc14456bf0b116573117d56dbfc"
ARCHIVE_TASK_ID = "TASK-20260824-a2464b"

SPECIFICATION_OUTPUT = Path(
    "coordination/goals/GOAL-ECQ-bef741/batches/BATCH-9fa73f/tasks/"
    "TASK-20260824-e77946/repair-specification.yaml"
)
REPORT_OUTPUT = Path(
    "coordination/goals/GOAL-ECQ-bef741/batches/BATCH-9fa73f/tasks/"
    "TASK-20260824-e77946/materialization-report.yaml"
)

EXPECTED_FIXTURE_TOTALS = {
    "symbolic_identity": 256,
    "raw_kummer": 632,
    "prime_ideal": 548,
    "valuation": 144,
    "prime_ideal.identity_descriptor": 146,
    "prime_ideal.published_descriptor": 146,
}
EXPECTED_KEYWORD_COUNTS = {
    "$ref": 197,
    "additionalProperties": 141,
    "const": 22,
    "enum": 6,
    "items": 187,
    "maxItems": 69,
    "maxLength": 24,
    "maximum": 11,
    "minItems": 69,
    "minLength": 24,
    "minimum": 131,
    "multipleOf": 1,
    "oneOf": 3,
    "pattern": 43,
    "required": 386,
    "type": 557,
    "uniqueItems": 1,
}
EXPECTED_REF_BINDINGS = 63
EXPECTED_CONSTRAINT_DESCRIPTORS = 197
EXPECTED_APPLICATION_ROWS = 1872

ROW_FIELDS = (
    "row_id",
    "schema_id",
    "positive_fixture_id",
    "schema_path",
    "keyword",
    "positive_instance_path",
    "subject",
    "property_or_item_detail",
    "concrete_value_or_value_summary",
    "chosen_oneOf_branch",
    "referenced_schema_path",
    "satisfaction_reason",
)
ROW_SORT_FIELDS = (
    "schema_id",
    "positive_fixture_id",
    "schema_path",
    "keyword",
    "positive_instance_path",
    "subject",
)

VALIDATION_KEYWORDS = frozenset(
    {
        "$ref",
        "additionalProperties",
        "const",
        "enum",
        "items",
        "maxItems",
        "maxLength",
        "maximum",
        "minItems",
        "minLength",
        "minimum",
        "multipleOf",
        "oneOf",
        "pattern",
        "required",
        "type",
        "uniqueItems",
    }
)

AUTHORIZED_PATH_FAMILIES = {
    "identity": [
        "/repair_specification/task_id",
        "/repair_specification/role",
        "/repair_specification/title",
        "/repair_specification/status",
        "/repair_specification/scientific_disposition",
        "/repair_specification/code_executions",
        "/repair_specification/recorded_at_utc",
    ],
    "provenance": ["/repair_specification/immutable_binding"],
    "materialization": [
        "/repair_specification/materialization",
        "/repair_specification/mandatory_next_gate",
    ],
    "manual_mapping": [
        "/repair_specification/R3_witness_schemas/manual_satisfiability_table"
    ],
}


class MaterializationError(RuntimeError):
    """The immutable input or a frozen mapping invariant did not hold."""


class _NoAliasSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: Any) -> bool:  # noqa: D401 - PyYAML hook
        return True


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def dump_yaml(document: Any) -> bytes:
    text = yaml.dump(
        document,
        Dumper=_NoAliasSafeDumper,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )
    return text.encode("utf-8")


def _pointer_token(token: Any) -> str:
    return str(token).replace("~", "~0").replace("/", "~1")


def pointer(parts: Sequence[Any]) -> str:
    if not parts:
        return ""
    return "/" + "/".join(_pointer_token(part) for part in parts)


def _decode_pointer(value: str) -> list[str]:
    if value == "":
        return []
    if not value.startswith("/"):
        raise MaterializationError(f"not an RFC6901 pointer: {value!r}")
    return [part.replace("~1", "/").replace("~0", "~") for part in value[1:].split("/")]


def _resolve_local_ref(root_schema: Mapping[str, Any], ref: str) -> tuple[Any, list[str]]:
    if not ref.startswith("#/"):
        raise MaterializationError(f"non-local or malformed reference: {ref!r}")
    parts = _decode_pointer(ref[1:])
    node: Any = root_schema
    for part in parts:
        if not isinstance(node, Mapping) or part not in node:
            raise MaterializationError(f"unresolved local reference: {ref!r}")
        node = node[part]
    return node, parts


def _json_type_matches(instance: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if expected == "boolean":
        return isinstance(instance, bool)
    if expected == "null":
        return instance is None
    return False


def _canonical_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _canonical_value(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return [_canonical_value(item) for item in value]
    return value


def _schema_matches(schema: Mapping[str, Any], instance: Any, root_schema: Mapping[str, Any]) -> bool:
    try:
        _assert_schema_matches(schema, instance, root_schema)
        return True
    except MaterializationError:
        return False


def _assert_schema_matches(
    schema: Mapping[str, Any], instance: Any, root_schema: Mapping[str, Any]
) -> None:
    if "$ref" in schema:
        target, _ = _resolve_local_ref(root_schema, schema["$ref"])
        _assert_schema_matches(target, instance, root_schema)
    if "type" in schema and not _json_type_matches(instance, schema["type"]):
        raise MaterializationError("type constraint failed")
    if "const" in schema and instance != schema["const"]:
        raise MaterializationError("const constraint failed")
    if "enum" in schema and instance not in schema["enum"]:
        raise MaterializationError("enum constraint failed")
    if isinstance(instance, dict):
        for name in schema.get("required", []):
            if name not in instance:
                raise MaterializationError("required constraint failed")
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}))
            if set(instance) - allowed:
                raise MaterializationError("additionalProperties constraint failed")
        for name, child_schema in schema.get("properties", {}).items():
            if name in instance:
                _assert_schema_matches(child_schema, instance[name], root_schema)
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            raise MaterializationError("minItems constraint failed")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            raise MaterializationError("maxItems constraint failed")
        if schema.get("uniqueItems"):
            canonical = [_canonical_value(item) for item in instance]
            if any(item in canonical[:index] for index, item in enumerate(canonical)):
                raise MaterializationError("uniqueItems constraint failed")
        if "items" in schema:
            for item in instance:
                _assert_schema_matches(schema["items"], item, root_schema)
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise MaterializationError("minLength constraint failed")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            raise MaterializationError("maxLength constraint failed")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            raise MaterializationError("pattern constraint failed")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            raise MaterializationError("minimum constraint failed")
        if "maximum" in schema and instance > schema["maximum"]:
            raise MaterializationError("maximum constraint failed")
        if "multipleOf" in schema and instance % schema["multipleOf"] != 0:
            raise MaterializationError("multipleOf constraint failed")
    if "oneOf" in schema:
        matches = sum(
            _schema_matches(branch, instance, root_schema) for branch in schema["oneOf"]
        )
        if matches != 1:
            raise MaterializationError(f"oneOf matched {matches} branches")


def _value_summary(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {"kind": "object", "key_count": len(value), "keys": list(value.keys())}
    if isinstance(value, list):
        return {"kind": "array", "length": len(value)}
    if value is None:
        return {"kind": "null", "value": None}
    if isinstance(value, bool):
        return {"kind": "boolean", "value": value}
    if isinstance(value, int):
        return {"kind": "integer", "value": value}
    if isinstance(value, float):
        return {"kind": "number", "value": value}
    return {"kind": "string", "value": value}


def _constraint_reason(
    keyword: str,
    constraint: Any,
    instance: Any,
    subject: str,
    referenced_schema_path: str | None,
) -> str:
    if keyword == "$ref":
        return f"local reference resolves to {referenced_schema_path} and that target accepts the concrete instance"
    if keyword == "required":
        return f"required property {subject!r} is present"
    if keyword == "additionalProperties":
        return "the concrete object has no keys outside the declared properties"
    if keyword == "items":
        return f"item {subject} is accepted by the declared item schema"
    if keyword == "oneOf":
        return f"exactly branch {subject} accepts the concrete instance"
    if keyword == "type":
        return f"the concrete instance has JSON type {constraint}"
    if keyword == "const":
        return "the concrete instance equals the declared const value"
    if keyword == "enum":
        return "the concrete instance is a member of the declared enum"
    if keyword == "minItems":
        return f"array length {len(instance)} is at least {constraint}"
    if keyword == "maxItems":
        return f"array length {len(instance)} is at most {constraint}"
    if keyword == "uniqueItems":
        return "all concrete array items are pairwise distinct"
    if keyword == "minLength":
        return f"string length {len(instance)} is at least {constraint}"
    if keyword == "maxLength":
        return f"string length {len(instance)} is at most {constraint}"
    if keyword == "pattern":
        return "the concrete string matches the declared regular expression"
    if keyword == "minimum":
        return f"numeric value {instance} is at least {constraint}"
    if keyword == "maximum":
        return f"numeric value {instance} is at most {constraint}"
    if keyword == "multipleOf":
        return f"numeric value {instance} is an exact multiple of {constraint}"
    raise MaterializationError(f"unsupported validation keyword: {keyword}")


def _make_row(
    *,
    schema_id: str,
    fixture_id: str,
    schema_path_parts: Sequence[str],
    keyword: str,
    instance_path_parts: Sequence[str],
    subject: str,
    detail: Any,
    concrete_value: Any,
    chosen_branch: str | None,
    referenced_schema_path: str | None,
    constraint: Any,
) -> dict[str, Any]:
    schema_path = pointer(schema_path_parts)
    return {
        "row_id": None,
        "schema_id": schema_id,
        "positive_fixture_id": fixture_id,
        "schema_path": schema_path,
        "keyword": keyword,
        "positive_instance_path": pointer(instance_path_parts),
        "subject": subject,
        "property_or_item_detail": detail,
        "concrete_value_or_value_summary": _value_summary(concrete_value),
        "chosen_oneOf_branch": chosen_branch,
        "referenced_schema_path": referenced_schema_path,
        "satisfaction_reason": _constraint_reason(
            keyword, constraint, concrete_value, subject, referenced_schema_path
        ),
    }


def _walk_application(
    *,
    schema: Mapping[str, Any],
    instance: Any,
    root_schema: Mapping[str, Any],
    schema_id: str,
    fixture_id: str,
    schema_path_parts: Sequence[str],
    instance_path_parts: Sequence[str],
    chosen_branch: str | None,
    rows: list[dict[str, Any]],
) -> None:
    _assert_schema_matches(schema, instance, root_schema)

    if "$ref" in schema:
        target, target_parts = _resolve_local_ref(root_schema, schema["$ref"])
        rows.append(
            _make_row(
                schema_id=schema_id,
                fixture_id=fixture_id,
                schema_path_parts=[*schema_path_parts, "$ref"],
                keyword="$ref",
                instance_path_parts=instance_path_parts,
                subject="",
                detail={"reference": schema["$ref"]},
                concrete_value=instance,
                chosen_branch=chosen_branch,
                referenced_schema_path=pointer(target_parts),
                constraint=schema["$ref"],
            )
        )
        _walk_application(
            schema=target,
            instance=instance,
            root_schema=root_schema,
            schema_id=schema_id,
            fixture_id=fixture_id,
            schema_path_parts=target_parts,
            instance_path_parts=instance_path_parts,
            chosen_branch=chosen_branch,
            rows=rows,
        )

    for keyword in (
        "type",
        "const",
        "enum",
        "minItems",
        "maxItems",
        "uniqueItems",
        "minLength",
        "maxLength",
        "pattern",
        "minimum",
        "maximum",
        "multipleOf",
    ):
        if keyword in schema:
            rows.append(
                _make_row(
                    schema_id=schema_id,
                    fixture_id=fixture_id,
                    schema_path_parts=[*schema_path_parts, keyword],
                    keyword=keyword,
                    instance_path_parts=instance_path_parts,
                    subject="",
                    detail={"constraint": copy.deepcopy(schema[keyword])},
                    concrete_value=instance,
                    chosen_branch=chosen_branch,
                    referenced_schema_path=None,
                    constraint=schema[keyword],
                )
            )

    if "required" in schema:
        for name in schema["required"]:
            rows.append(
                _make_row(
                    schema_id=schema_id,
                    fixture_id=fixture_id,
                    schema_path_parts=[*schema_path_parts, "required"],
                    keyword="required",
                    instance_path_parts=instance_path_parts,
                    subject=str(name),
                    detail={"required_property": name},
                    concrete_value=instance[name],
                    chosen_branch=chosen_branch,
                    referenced_schema_path=None,
                    constraint=name,
                )
            )

    if "additionalProperties" in schema:
        allowed = list(schema.get("properties", {}).keys())
        rows.append(
            _make_row(
                schema_id=schema_id,
                fixture_id=fixture_id,
                schema_path_parts=[*schema_path_parts, "additionalProperties"],
                keyword="additionalProperties",
                instance_path_parts=instance_path_parts,
                subject="",
                detail={
                    "constraint": schema["additionalProperties"],
                    "declared_properties": allowed,
                    "observed_extra_properties": [key for key in instance if key not in allowed],
                },
                concrete_value=instance,
                chosen_branch=chosen_branch,
                referenced_schema_path=None,
                constraint=schema["additionalProperties"],
            )
        )

    for name, child_schema in schema.get("properties", {}).items():
        if name in instance:
            _walk_application(
                schema=child_schema,
                instance=instance[name],
                root_schema=root_schema,
                schema_id=schema_id,
                fixture_id=fixture_id,
                schema_path_parts=[*schema_path_parts, "properties", name],
                instance_path_parts=[*instance_path_parts, name],
                chosen_branch=chosen_branch,
                rows=rows,
            )

    if "items" in schema:
        if not isinstance(instance, list):
            raise MaterializationError("items applied to a non-array")
        for index, item in enumerate(instance):
            subject = str(index)
            rows.append(
                _make_row(
                    schema_id=schema_id,
                    fixture_id=fixture_id,
                    schema_path_parts=[*schema_path_parts, "items"],
                    keyword="items",
                    instance_path_parts=instance_path_parts,
                    subject=subject,
                    detail={"item_index": index},
                    concrete_value=item,
                    chosen_branch=chosen_branch,
                    referenced_schema_path=None,
                    constraint=schema["items"],
                )
            )
            _walk_application(
                schema=schema["items"],
                instance=item,
                root_schema=root_schema,
                schema_id=schema_id,
                fixture_id=fixture_id,
                schema_path_parts=[*schema_path_parts, "items"],
                instance_path_parts=[*instance_path_parts, subject],
                chosen_branch=chosen_branch,
                rows=rows,
            )

    if "oneOf" in schema:
        matching = [
            index
            for index, branch in enumerate(schema["oneOf"])
            if _schema_matches(branch, instance, root_schema)
        ]
        if len(matching) != 1:
            raise MaterializationError(f"oneOf matched {len(matching)} branches")
        index = matching[0]
        subject = str(index)
        rows.append(
            _make_row(
                schema_id=schema_id,
                fixture_id=fixture_id,
                schema_path_parts=[*schema_path_parts, "oneOf"],
                keyword="oneOf",
                instance_path_parts=instance_path_parts,
                subject=subject,
                detail={"matching_branch_indexes": matching, "exact_match_count": 1},
                concrete_value=instance,
                chosen_branch=subject,
                referenced_schema_path=None,
                constraint=schema["oneOf"],
            )
        )
        _walk_application(
            schema=schema["oneOf"][index],
            instance=instance,
            root_schema=root_schema,
            schema_id=schema_id,
            fixture_id=fixture_id,
            schema_path_parts=[*schema_path_parts, "oneOf", subject],
            instance_path_parts=instance_path_parts,
            chosen_branch=subject,
            rows=rows,
        )


def _fixture_scopes(schemas: Mapping[str, Any]) -> Iterable[dict[str, Any]]:
    for name in ("symbolic_identity", "raw_kummer", "prime_ideal", "valuation"):
        entry = schemas[name]
        yield {
            "fixture_id": name,
            "schema": entry["schema"],
            "root_schema": entry["schema"],
            "schema_id": entry["schema"]["$id"],
            "instance": entry["fixtures"]["positive"],
            "schema_path_parts": [],
            "instance_path_parts": [],
        }

    prime = schemas["prime_ideal"]
    descriptor = prime["schema"]["$defs"]["character_basis_binding_descriptor"]
    for fixture_name in ("identity_descriptor", "published_descriptor"):
        yield {
            "fixture_id": f"prime_ideal.{fixture_name}",
            "schema": descriptor,
            "root_schema": prime["schema"],
            "schema_id": prime["schema"]["$id"],
            "instance": prime["fixtures"][fixture_name],
            "schema_path_parts": ["$defs", "character_basis_binding_descriptor"],
            "instance_path_parts": ["character_basis_binding"],
        }


def collect_ref_bindings(schemas: Mapping[str, Any]) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []

    def visit(schema_id: str, node: Any, parts: list[str]) -> None:
        if isinstance(node, Mapping):
            if "$ref" in node:
                _, target_parts = _resolve_local_ref(schemas_by_id[schema_id], node["$ref"])
                bindings.append(
                    {
                        "ref_id": None,
                        "schema_id": schema_id,
                        "source_schema_path": pointer([*parts, "$ref"]),
                        "reference": node["$ref"],
                        "target_schema_path": pointer(target_parts),
                    }
                )
            for key, value in node.items():
                if key == "$ref":
                    continue
                visit(schema_id, value, [*parts, str(key)])
        elif isinstance(node, list):
            for index, value in enumerate(node):
                visit(schema_id, value, [*parts, str(index)])

    schemas_by_id = {entry["schema"]["$id"]: entry["schema"] for entry in schemas.values()}
    for schema_id in sorted(schemas_by_id):
        visit(schema_id, schemas_by_id[schema_id], [])

    bindings.sort(
        key=lambda row: (
            row["schema_id"],
            row["source_schema_path"],
            row["reference"],
            row["target_schema_path"],
        )
    )
    for index, row in enumerate(bindings, 1):
        row["ref_id"] = f"REF-{index:03d}"
    return bindings


def enumerate_mapping(
    schemas: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    refs = collect_ref_bindings(schemas)
    ref_lookup = {
        (row["schema_id"], row["source_schema_path"], row["reference"]): row["ref_id"]
        for row in refs
    }
    rows: list[dict[str, Any]] = []
    for scope in _fixture_scopes(schemas):
        _walk_application(rows=rows, chosen_branch=None, **scope)

    rows.sort(key=lambda row: tuple(row[field] for field in ROW_SORT_FIELDS))
    for index, row in enumerate(rows, 1):
        row["row_id"] = f"MS-{index:06d}"

    descriptors: list[dict[str, Any]] = []
    for row in rows:
        if row["keyword"] != "$ref":
            continue
        reference = row["property_or_item_detail"]["reference"]
        lookup_key = (row["schema_id"], row["schema_path"], reference)
        if lookup_key not in ref_lookup:
            raise MaterializationError(f"expanded reference has no static binding: {lookup_key!r}")
        descriptors.append(
            {
                "constraint_descriptor_id": None,
                "ref_id": ref_lookup[lookup_key],
                "mapping_row_id": row["row_id"],
                "schema_id": row["schema_id"],
                "positive_fixture_id": row["positive_fixture_id"],
                "schema_path": row["schema_path"],
                "positive_instance_path": row["positive_instance_path"],
                "subject": row["subject"],
                "referenced_schema_path": row["referenced_schema_path"],
                "satisfaction_reason": row["satisfaction_reason"],
            }
        )
    for index, descriptor in enumerate(descriptors, 1):
        descriptor["constraint_descriptor_id"] = f"SC-{index:03d}"

    _assert_frozen_inventory(refs, descriptors, rows)
    return refs, descriptors, rows


def row_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return tuple(row[field] for field in ROW_SORT_FIELDS)


def reconciliation(expected_rows: Sequence[Mapping[str, Any]], actual_rows: Sequence[Mapping[str, Any]]) -> dict[str, int | bool]:
    expected_keys = [row_key(row) for row in expected_rows]
    actual_keys = [row_key(row) for row in actual_rows]
    expected_set = set(expected_keys)
    actual_set = set(actual_keys)
    return {
        "expected_application_rows": len(expected_keys),
        "actual_application_rows": len(actual_keys),
        "missing_rows": len(expected_set - actual_set),
        "duplicate_row_keys": len(actual_keys) - len(actual_set),
        "extraneous_rows": len(actual_set - expected_set),
        "success": (
            len(expected_keys) == len(expected_set)
            and len(expected_keys) == len(actual_keys)
            and expected_set == actual_set
        ),
    }


def _assert_identifier_range(rows: Sequence[Mapping[str, Any]], field: str, prefix: str, width: int) -> None:
    expected = [f"{prefix}-{index:0{width}d}" for index in range(1, len(rows) + 1)]
    actual = [row[field] for row in rows]
    if actual != expected:
        raise MaterializationError(f"noncontiguous {prefix} identifiers")


def _assert_frozen_inventory(
    refs: Sequence[Mapping[str, Any]],
    descriptors: Sequence[Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
) -> None:
    if len(refs) != EXPECTED_REF_BINDINGS:
        raise MaterializationError(f"expected 63 ref bindings, got {len(refs)}")
    if len(descriptors) != EXPECTED_CONSTRAINT_DESCRIPTORS:
        raise MaterializationError(f"expected 197 descriptors, got {len(descriptors)}")
    if len(rows) != EXPECTED_APPLICATION_ROWS:
        raise MaterializationError(f"expected 1872 rows, got {len(rows)}")
    _assert_identifier_range(refs, "ref_id", "REF", 3)
    _assert_identifier_range(descriptors, "constraint_descriptor_id", "SC", 3)
    _assert_identifier_range(rows, "row_id", "MS", 6)
    if any(tuple(row.keys()) != ROW_FIELDS for row in rows):
        raise MaterializationError("a mapping row does not have exactly the twelve frozen fields")
    keys = [row_key(row) for row in rows]
    if keys != sorted(keys) or len(keys) != len(set(keys)):
        raise MaterializationError("mapping row keys are unsorted or duplicated")
    fixture_counts = Counter(row["positive_fixture_id"] for row in rows)
    keyword_counts = Counter(row["keyword"] for row in rows)
    if dict(fixture_counts) != EXPECTED_FIXTURE_TOTALS:
        raise MaterializationError(f"fixture counts drifted: {dict(fixture_counts)!r}")
    if dict(keyword_counts) != EXPECTED_KEYWORD_COUNTS:
        raise MaterializationError(f"keyword counts drifted: {dict(keyword_counts)!r}")
    first_key = row_key(rows[0])
    expected_first = (
        "https://crypto-autoresearcher.invalid/schema/erank/prime-ideals-v1.json",
        "prime_ideal",
        "/$defs/character_basis_binding_descriptor/oneOf",
        "oneOf",
        "/character_basis_binding",
        "0",
    )
    expected_last = (
        "https://crypto-autoresearcher.invalid/schema/erank/valuations-v1.json",
        "valuation",
        "/type",
        "type",
        "",
        "",
    )
    if first_key != expected_first or row_key(rows[-1]) != expected_last:
        raise MaterializationError("canonical first or last mapping key drifted")


def _delete_pointer(document: Any, path: str) -> None:
    parts = _decode_pointer(path)
    if not parts:
        raise MaterializationError("refusing to delete the document root")
    node = document
    for part in parts[:-1]:
        if not isinstance(node, dict) or part not in node:
            return
        node = node[part]
    if isinstance(node, dict):
        node.pop(parts[-1], None)


def normalize_for_no_drift(document: Mapping[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(document)
    for paths in AUTHORIZED_PATH_FAMILIES.values():
        for path in paths:
            _delete_pointer(normalized, path)
    return normalized


def recursive_differences(left: Any, right: Any, parts: tuple[str, ...] = ()) -> list[str]:
    differences: list[str] = []
    if type(left) is not type(right):
        return [pointer(parts)]
    if isinstance(left, dict):
        if list(left.keys()) != list(right.keys()):
            differences.append(pointer((*parts, "<key-order>")))
        ordered_keys = list(left.keys()) + [key for key in right if key not in left]
        for key in ordered_keys:
            if key not in left or key not in right:
                differences.append(pointer((*parts, str(key))))
            else:
                differences.extend(recursive_differences(left[key], right[key], (*parts, str(key))))
        return differences
    if isinstance(left, list):
        if len(left) != len(right):
            differences.append(pointer((*parts, "<length>")))
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            differences.extend(recursive_differences(left_item, right_item, (*parts, str(index))))
        return differences
    if left != right:
        differences.append(pointer(parts))
    return differences


def no_drift_result(source: Mapping[str, Any], generated: Mapping[str, Any]) -> dict[str, Any]:
    differences = recursive_differences(
        normalize_for_no_drift(source), normalize_for_no_drift(generated)
    )
    return {
        "result": "PASS" if not differences else "FAIL",
        "unauthorized_difference_count": len(differences),
        "unauthorized_difference_paths": differences,
        "authorized_path_families": copy.deepcopy(AUTHORIZED_PATH_FAMILIES),
        "mapping_key_order_preserved_outside_authorized_paths": not differences,
        "list_order_preserved_outside_authorized_paths": not differences,
    }


def load_source(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    actual_hash = sha256_bytes(raw)
    if actual_hash != SOURCE_SHA256:
        raise MaterializationError(
            f"immutable T33 hash mismatch: expected {SOURCE_SHA256}, got {actual_hash}"
        )
    document = yaml.safe_load(raw)
    if not isinstance(document, dict) or list(document) != ["repair_specification"]:
        raise MaterializationError("T33 must have the sole top-level key repair_specification")
    return document


def build_document(source: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    generated = copy.deepcopy(source)
    record = generated["repair_specification"]
    schemas = record["R3_witness_schemas"]["schemas"]
    refs, descriptors, rows = enumerate_mapping(schemas)

    source_fixture_rows = copy.deepcopy(
        record["R3_witness_schemas"]["manual_satisfiability_table"]["rows"]
    )
    fixture_counts = dict(Counter(row["positive_fixture_id"] for row in rows))
    keyword_counts = dict(Counter(row["keyword"] for row in rows))
    mapping_reconciliation = reconciliation(rows, rows)
    mapping_reconciliation.update(
        {
            "expected_ref_occurrence_bindings": EXPECTED_REF_BINDINGS,
            "actual_ref_occurrence_bindings": len(refs),
            "missing_ref_occurrence_bindings": 0,
            "expected_constraint_descriptors": EXPECTED_CONSTRAINT_DESCRIPTORS,
            "actual_constraint_descriptors": len(descriptors),
            "missing_constraint_descriptors": 0,
        }
    )

    record["task_id"] = TASK_ID
    record["role"] = "executor"
    record["title"] = "Standalone T33 specification with exhaustive deterministic manual satisfiability mapping"
    record["status"] = "mechanically_materialized_pending_independent_validation"
    record["scientific_disposition"] = "non_research_mechanical_mapping_only"
    record["code_executions"] = 1
    record["recorded_at_utc"] = RECORDED_AT_UTC

    immutable_binding = record["immutable_binding"]
    immutable_binding["materialization_handoff"] = {
        "task_id": TASK_ID,
        "path": str(HANDOFF_PATH),
        "sha256": HANDOFF_SHA256,
        "pinned_head": PINNED_HEAD,
    }
    immutable_binding["source_T33"] = {
        "task_id": "TASK-20260824-1474af",
        "path": str(SOURCE_PATH),
        "sha256": SOURCE_SHA256,
        "deep_copied": True,
    }
    immutable_binding["rejected_T37"] = {
        "task_id": "TASK-20260824-f59e33",
        "path": str(T37_PATH),
        "sha256": T37_SHA256,
        "semantic_disposition": "REVISE_REQUIRED",
    }
    immutable_binding["T38_archive"] = {
        "task_id": "TASK-20260824-946fb3",
        "path": str(T38_RECEIPT_PATH),
        "sha256": T38_RECEIPT_SHA256,
        "snapshot_commit": "1b6de65ce7502a65c4281be7e846db9801294a7b",
    }
    immutable_binding["T40_opening_archive"] = {
        "task_id": "TASK-20260824-ad4c82",
        "path": str(T40_RECEIPT_PATH),
        "sha256": T40_RECEIPT_SHA256,
        "snapshot_commit": "b55d0c3778eed1dc187c1b04500a7e90d9b3dfab",
    }
    immutable_binding["next_archive_task_id"] = ARCHIVE_TASK_ID

    record["R3_witness_schemas"]["manual_satisfiability_table"] = {
        "execution_status": "mechanically_materialized_pending_independent_validation",
        "path_encoding": "RFC6901",
        "canonical_sort_key": list(ROW_SORT_FIELDS),
        "required_mapping_row_fields": list(ROW_FIELDS),
        "source_fixture_manifest_rows": source_fixture_rows,
        "local_ref_occurrence_bindings": refs,
        "constraint_descriptors": descriptors,
        "mapping_rows": rows,
        "counts_by_fixture": fixture_counts,
        "global_keyword_counts": {**keyword_counts, "total": len(rows)},
        "reconciliation": mapping_reconciliation,
    }

    record["materialization"] = {
        "task_id": TASK_ID,
        "classification": "documentation_schema_tooling_only",
        "algorithm_version": 1,
        "immutable_input": {"path": str(SOURCE_PATH), "sha256": SOURCE_SHA256},
        "canonical_sort_key": list(ROW_SORT_FIELDS),
        "path_encoding": "RFC6901",
        "frozen_inventory": {
            "schema_count": 4,
            "positive_fixture_scope_count": 6,
            "local_ref_binding_count": len(refs),
            "constraint_descriptor_count": len(descriptors),
            "constraint_application_count": len(rows),
        },
        "tooling_observations": {
            "standards_jsonschema_validator_invocations": 0,
            "negative_fixture_executions": 0,
            "manual_constraint_applications_documented": len(rows),
        },
        "prohibited_work_counts": {
            "campaign_inputs_read": 0,
            "experiments_run": 0,
            "curve_searches_run": 0,
            "rank_computations_run": 0,
            "replays_run": 0,
            "controls_run": 0,
            "benchmarks_run": 0,
            "proof_searches_run": 0,
        },
        "approvals_conferred": [],
        "mathematical_claims": [],
    }
    record["mandatory_next_gate"] = {
        "task": ARCHIVE_TASK_ID,
        "action": "strict snapshot of the six T41 artifacts before independent validation",
        "after_snapshot": (
            "Only the preregistered blind Validator TASK-20260824-89ae99 may assess mechanical completeness. "
            "No scientific or campaign task becomes eligible."
        ),
        "approval_effect": "none",
    }

    drift = no_drift_result(source, generated)
    if drift["result"] != "PASS":
        raise MaterializationError(f"unauthorized T33 drift: {drift!r}")
    report_data = {
        "refs": refs,
        "descriptors": descriptors,
        "rows": rows,
        "fixture_counts": fixture_counts,
        "keyword_counts": keyword_counts,
        "reconciliation": mapping_reconciliation,
        "no_drift": drift,
    }
    return generated, report_data


def build_specification_bytes(source: Mapping[str, Any]) -> tuple[bytes, dict[str, Any]]:
    document, data = build_document(source)
    return dump_yaml(document), data


def build_materialization_report(
    *, specification_bytes: bytes, data: Mapping[str, Any]
) -> dict[str, Any]:
    rows = data["rows"]
    return {
        "materialization_report": {
            "schema_version": "1.0",
            "task_id": TASK_ID,
            "goal_id": GOAL_ID,
            "batch_id": BATCH_ID,
            "recorded_at_utc": RECORDED_AT_UTC,
            "status": "completed_mechanical_pending_independent_validation",
            "classification": "documentation_schema_tooling_only",
            "immutable_authority": {
                "pinned_head": PINNED_HEAD,
                "handoff": {"path": str(HANDOFF_PATH), "sha256": HANDOFF_SHA256},
                "decision": {"path": str(DECISION_PATH), "sha256": DECISION_SHA256},
                "source_T33": {"path": str(SOURCE_PATH), "sha256": SOURCE_SHA256},
                "T38_receipt": {"path": str(T38_RECEIPT_PATH), "sha256": T38_RECEIPT_SHA256},
                "T40_receipt": {"path": str(T40_RECEIPT_PATH), "sha256": T40_RECEIPT_SHA256},
            },
            "output": {
                "path": str(SPECIFICATION_OUTPUT),
                "sha256": sha256_bytes(specification_bytes),
                "bytes": len(specification_bytes),
                "yaml_safe_load": "PASS",
                "sole_top_level_key": "repair_specification",
            },
            "inventory": {
                "schemas": 4,
                "positive_fixture_scopes": 6,
                "local_ref_bindings": len(data["refs"]),
                "constraint_descriptors": len(data["descriptors"]),
                "constraint_application_rows": len(rows),
                "ref_id_range": [data["refs"][0]["ref_id"], data["refs"][-1]["ref_id"]],
                "constraint_descriptor_id_range": [
                    data["descriptors"][0]["constraint_descriptor_id"],
                    data["descriptors"][-1]["constraint_descriptor_id"],
                ],
                "mapping_row_id_range": [rows[0]["row_id"], rows[-1]["row_id"]],
                "counts_by_fixture": data["fixture_counts"],
                "global_keyword_counts": {**data["keyword_counts"], "total": len(rows)},
            },
            "canonical_boundary_keys": {
                "first": {field: rows[0][field] for field in ROW_SORT_FIELDS},
                "last": {field: rows[-1][field] for field in ROW_SORT_FIELDS},
            },
            "reconciliation": data["reconciliation"],
            "recursive_no_drift": data["no_drift"],
            "determinism": {
                "two_fresh_in_memory_generations_byte_identical": True,
                "two_isolated_filesystem_generations": "verified_by_unit_test",
                "ambient_time_or_randomness_used": False,
            },
            "scope_audit": {
                "repository_inputs_opened": [str(SOURCE_PATH)],
                "campaign_inputs_opened": [],
                "campaign_inputs_read": 0,
                "experiments_run": 0,
                "curve_searches_run": 0,
                "rank_computations_run": 0,
                "proof_searches_run": 0,
                "mathematical_claims": [],
            },
            "authority_audit": {
                "design_approved": False,
                "tooling_approved": False,
                "campaign_approved": False,
                "curve_claimed": False,
                "rank_claimed": False,
                "novelty_claimed": False,
                "goal_completion_claimed": False,
                "approvals_conferred": [],
            },
            "next_gate": ARCHIVE_TASK_ID,
        }
    }


def generate_bytes(source: Mapping[str, Any]) -> tuple[bytes, bytes, dict[str, Any]]:
    first_specification, first_data = build_specification_bytes(source)
    second_specification, second_data = build_specification_bytes(copy.deepcopy(source))
    if first_specification != second_specification:
        raise MaterializationError("two fresh in-memory generations are not byte-identical")
    if [row_key(row) for row in first_data["rows"]] != [
        row_key(row) for row in second_data["rows"]
    ]:
        raise MaterializationError("two fresh generations disagree on mapping keys")
    report = build_materialization_report(
        specification_bytes=first_specification, data=first_data
    )
    return first_specification, dump_yaml(report), first_data


def _write_new(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(content)
    except FileExistsError as exc:
        raise MaterializationError(f"refusing to overwrite existing artifact: {path}") from exc


def write_artifacts(
    source_path: Path, specification_output: Path, report_output: Path
) -> dict[str, Any]:
    source = load_source(source_path)
    specification_bytes, report_bytes, data = generate_bytes(source)
    if specification_output.exists() or report_output.exists():
        raise MaterializationError("refusing to overwrite an existing output artifact")
    _write_new(specification_output, specification_bytes)
    _write_new(report_output, report_bytes)
    return {
        "specification_sha256": sha256_bytes(specification_bytes),
        "report_sha256": sha256_bytes(report_bytes),
        "ref_bindings": len(data["refs"]),
        "constraint_descriptors": len(data["descriptors"]),
        "mapping_rows": len(data["rows"]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE_PATH)
    parser.add_argument("--specification-output", type=Path, default=SPECIFICATION_OUTPUT)
    parser.add_argument("--report-output", type=Path, default=REPORT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = write_artifacts(args.source, args.specification_output, args.report_output)
    print(yaml.safe_dump(result, sort_keys=False).rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
