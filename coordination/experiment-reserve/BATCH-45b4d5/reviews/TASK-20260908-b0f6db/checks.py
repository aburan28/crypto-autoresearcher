#!/usr/bin/env python3
"""Independent fixed-object review for TASK-20260908-b0f6db.

This checker does not import or execute any producer checker.  It reads the
committed source set in full, compares the fifth and sixth definitions as data,
and exercises only fixed serialization objects.  It performs no scientific
fixture generation, CM computation, allocator operation, model probe, or
prospective launcher invocation.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator, FormatChecker


TASK_ID = "TASK-20260908-b0f6db"
EXPERIMENT_ID = "EXP-ECDLP-1b1b99"
RESERVATION_RECORDED_AT_UTC = "2026-09-09T04:51:51.538500000Z"
MAXIMUM_TOTAL_CASE_EXECUTIONS = 320
PER_CASE_SECONDS = 10.0
AGGREGATE_EXECUTED_CHECK_WALL_CPU_SECONDS = 1800.0
MAXIMUM_WORKERS = 1
MEMORY_LIMIT_BYTES = 2 * 1024**3

AUTHORITY_COMMIT = "9673835d73f0878298b1c76d0e6ab11af2873380"
PUBLISHED_CLAIM_COMMIT = "4d439622eabe7de841b30ce51335d4b550e79cb4"
SOURCE_SNAPSHOT_COMMIT = "32507534bfc10f2299450957dc3ec519e749eb3e"

HANDOFF_PATH = Path("ledger/handoffs/TASK-20260908-b0f6db.yaml")
PLAN_PATH = Path(
    "coordination/experiment-reserve/BATCH-45b4d5/"
    "review-plan-TASK-20260908-b0f6db.yaml"
)
PREDECESSOR_CONTRACT_PATH = Path(
    "coordination/experiment-reserve/BATCH-45b4d5/corrections/"
    "TASK-20260908-e06add/EXP-ECDLP-1b1b99.yaml"
)
PREDECESSOR_SCHEMA_PATH = Path(
    "coordination/experiment-reserve/BATCH-45b4d5/corrections/"
    "TASK-20260908-e06add/schema.json"
)
CURRENT_CONTRACT_PATH = Path(
    "coordination/experiment-reserve/BATCH-45b4d5/corrections/"
    "TASK-20260908-d18d13/EXP-ECDLP-1b1b99.yaml"
)
CURRENT_SCHEMA_PATH = Path(
    "coordination/experiment-reserve/BATCH-45b4d5/corrections/"
    "TASK-20260908-d18d13/schema.json"
)
SNAPSHOT_PATH = Path(
    "coordination/experiment-reserve/BATCH-45b4d5/archives/"
    "TASK-20260908-e5fdfd/snapshot.json"
)

FIXED_TASK = "TASK-20260908-d18d13"
FIXED_HANDOFF_SHA256 = "a" * 64
FIXED_OBSERVED_BYTES = b"independent fixed malformed authorization input"
FIXED_RECORDED_AT = "2026-09-09T04:00:00Z"


class CheckFailure(AssertionError):
    pass


@dataclass(frozen=True)
class Case:
    case_id: str
    category: str
    description: str
    body: Callable[[], dict[str, Any] | None]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def jsonable(value: Any) -> Any:
    if isinstance(value, set):
        return sorted(jsonable(item) for item in value)
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def schema_wrapper(root: dict[str, Any], definition: str) -> dict[str, Any]:
    return {
        "$schema": root["$schema"],
        "$defs": root["$defs"],
        "$ref": f"#/$defs/{definition}",
    }


def schema_errors(
    root: dict[str, Any], value: Any, definition: str | None = None
) -> list[str]:
    target = schema_wrapper(root, definition) if definition else root
    validator = Draft202012Validator(target, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(value),
        key=lambda error: "/".join(str(part) for part in error.absolute_path),
    )
    return [
        f"{'.'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in errors
    ]


def require_schema_valid(
    root: dict[str, Any], value: Any, definition: str | None = None
) -> dict[str, Any]:
    errors = schema_errors(root, value, definition)
    require(not errors, f"unexpected schema rejection: {errors[:3]}")
    return {"schema_errors": []}


def require_schema_invalid(
    root: dict[str, Any], value: Any, definition: str | None = None
) -> dict[str, Any]:
    errors = schema_errors(root, value, definition)
    require(bool(errors), "known-invalid object was admitted")
    return {"first_error": errors[0], "error_count": len(errors)}


def fixed_policy_failure() -> dict[str, Any]:
    return {
        "requested_policy": "executor-implementation",
        "canonical_policy": "executor-implementation",
        "backend": None,
        "provider": None,
        "resolved_model_id": None,
        "model_provenance": "not-applicable",
        "model_verified": False,
        "requested_reasoning_effort": None,
        "reasoning_effort": None,
        "fallback_used": False,
        "fallback_reason": None,
        "degraded_requirements": [],
        "independent_session": False,
        "adapter_version": "independent-fixed-adapter-v1",
        "config_digest": None,
        "note": "policy resolution failed",
        "resolution_error": "LookupError: fixed unavailable policy",
    }


def fixed_trusted_context(*, independent: bool = True) -> dict[str, Any]:
    return {
        "task_id": FIXED_TASK,
        "handoff_sha256": FIXED_HANDOFF_SHA256,
        "provenance": "independently_established" if independent else "receipt_copy",
    }


def fixed_pre_run(
    reason: str,
    status: str,
    *,
    observed: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if observed is None:
        observed = {
            "kind": "sha256",
            "sha256": sha256_bytes(FIXED_OBSERVED_BYTES),
            "byte_length": len(FIXED_OBSERVED_BYTES),
        }
    value: dict[str, Any] = {
        "record_type": "pre_run_outcome",
        "experiment_id": EXPERIMENT_ID,
        "status": status,
        "reason_code": reason,
        "stage": "authorize_and_claim_nonce",
        "recorded_at_UTC": FIXED_RECORDED_AT,
        "trusted_handoff": {
            "task_id": FIXED_TASK,
            "handoff_sha256": FIXED_HANDOFF_SHA256,
        },
        "observed_authorization_input": observed,
    }
    if reason == "POLICY_RESOLUTION_FAILED":
        value["policy_resolution_failure"] = fixed_policy_failure()
    return value


def parse_utc(value: str) -> datetime:
    require(isinstance(value, str), "recorded_at_UTC is not text")
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise CheckFailure(f"malformed UTC: {exc}") from exc
    require(parsed.tzinfo is not None, "UTC offset missing")
    require(parsed.utcoffset() is not None, "UTC offset unavailable")
    require(parsed.utcoffset().total_seconds() == 0, "non-UTC offset")
    return parsed


_UNSET = object()


def semantic_errors(
    value: dict[str, Any],
    *,
    schema: dict[str, Any],
    allowed_pairs: set[tuple[str, str]],
    trusted_context: dict[str, Any] | None,
    observed_bytes: bytes | object = _UNSET,
    expected_unavailable_reason: str | None = None,
    expected_policy_failure: dict[str, Any] | None = None,
    policy_failure_independently_obtained: bool = True,
) -> list[str]:
    errors = schema_errors(schema, value, "pre_run_outcome")
    if errors:
        return ["schema: " + error for error in errors]

    if trusted_context is None:
        errors.append("trusted context absent")
    elif trusted_context.get("provenance") != "independently_established":
        errors.append("trusted context was not independently established")
    else:
        expected_handoff = {
            "task_id": trusted_context.get("task_id"),
            "handoff_sha256": trusted_context.get("handoff_sha256"),
        }
        if value["trusted_handoff"] != expected_handoff:
            errors.append("trusted handoff mismatch")

    pair = (value["reason_code"], value["status"])
    if pair not in allowed_pairs:
        errors.append("status/reason pair is outside derived relation")
    if value["stage"] != "authorize_and_claim_nonce":
        errors.append("stage is outside pre-run boundary")

    try:
        parse_utc(value["recorded_at_UTC"])
    except CheckFailure as exc:
        errors.append(str(exc))

    observed = value["observed_authorization_input"]
    if observed["kind"] == "sha256":
        if observed_bytes is _UNSET:
            errors.append("complete observed bytes unavailable for digest comparison")
        else:
            assert isinstance(observed_bytes, bytes)
            if observed["byte_length"] != len(observed_bytes):
                errors.append("observed byte length mismatch")
            if observed["sha256"] != sha256_bytes(observed_bytes):
                errors.append("observed SHA-256 mismatch")
        if expected_unavailable_reason is not None:
            errors.append("available observation conflicts with expected unavailability")
    else:
        if observed_bytes is not _UNSET:
            errors.append("unavailable observation conflicts with observed bytes")
        if expected_unavailable_reason is None:
            errors.append("unavailability reason was not independently established")
        elif observed["reason"] != expected_unavailable_reason:
            errors.append("unavailability reason mismatch")

    actual_policy = value.get("policy_resolution_failure")
    if value["reason_code"] == "POLICY_RESOLUTION_FAILED":
        if not policy_failure_independently_obtained:
            errors.append("expected policy failure was copied from receipt")
        if expected_policy_failure is None:
            errors.append("authoritative policy failure block unavailable")
        elif actual_policy != expected_policy_failure:
            errors.append("policy failure block differs from authoritative writer output")
    elif actual_policy is not None:
        errors.append("non-policy outcome smuggles policy failure block")
    return errors


def require_semantic_valid(value: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    errors = semantic_errors(value, **context)
    require(not errors, f"unexpected semantic rejection: {errors}")
    return {"semantic_errors": []}


def require_semantic_invalid(value: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    errors = semantic_errors(value, **context)
    require(bool(errors), "known-invalid semantic object was admitted")
    return {"semantic_errors": errors}


def run_git(*args: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args], check=False, capture_output=True, text=True
    )
    return {
        "command": ["git", *args],
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def attempt_memory_limit() -> dict[str, Any]:
    recorded_at = utc_now()
    try:
        before_soft, before_hard = resource.getrlimit(resource.RLIMIT_AS)
        effective_soft = MEMORY_LIMIT_BYTES
        if before_hard != resource.RLIM_INFINITY:
            effective_soft = min(effective_soft, before_hard)
        resource.setrlimit(resource.RLIMIT_AS, (effective_soft, before_hard))
        after_soft, after_hard = resource.getrlimit(resource.RLIMIT_AS)
        return {
            "attempted": True,
            "succeeded": True,
            "recorded_at_utc": recorded_at,
            "requested_soft_bytes": MEMORY_LIMIT_BYTES,
            "before": [before_soft, before_hard],
            "after": [after_soft, after_hard],
            "error": None,
        }
    except Exception as exc:
        return {
            "attempted": True,
            "succeeded": False,
            "recorded_at_utc": recorded_at,
            "requested_soft_bytes": MEMORY_LIMIT_BYTES,
            "before": None,
            "after": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def verify_sources(repo: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    handoff_bytes = (repo / HANDOFF_PATH).read_bytes()
    handoff_document = yaml.safe_load(handoff_bytes)
    handoff = handoff_document["handoff"]
    bindings = handoff["source_bindings"]
    declared_inputs = handoff["inputs"]
    require(len(bindings) == 86, f"expected 86 bindings, found {len(bindings)}")
    require(
        declared_inputs == [binding["path"] for binding in bindings],
        "input and source-binding order differ",
    )

    records: list[dict[str, Any]] = []
    failures: list[str] = []
    parsed_counts = {"yaml": 0, "json": 0, "python": 0, "text": 0}
    documents: dict[str, Any] = {}
    for binding in bindings:
        relative = binding["path"]
        path = repo / relative
        data = path.read_bytes()
        actual = sha256_bytes(data)
        matched = actual == binding["sha256"]
        if not matched:
            failures.append(relative)
        record = {
            "path": relative,
            "expected_sha256": binding["sha256"],
            "actual_sha256": actual,
            "byte_length": len(data),
            "matched": matched,
        }
        try:
            text = data.decode("utf-8")
            if path.suffix in {".yaml", ".yml"}:
                documents[relative] = yaml.safe_load(text)
                parsed_counts["yaml"] += 1
                record["complete_read"] = "utf8_yaml_parsed"
            elif path.suffix == ".json":
                documents[relative] = json.loads(text)
                parsed_counts["json"] += 1
                record["complete_read"] = "utf8_json_parsed"
            elif path.suffix == ".py":
                compile(text, relative, "exec")
                parsed_counts["python"] += 1
                record["complete_read"] = "utf8_python_compiled_without_execution"
            else:
                parsed_counts["text"] += 1
                record["complete_read"] = "utf8_text_decoded"
        except Exception as exc:  # retained as source failure, never concealed
            record["complete_read"] = "parse_failed"
            record["parse_error"] = f"{type(exc).__name__}: {exc}"
            failures.append(relative + "#parse")
        records.append(record)

    require(not failures, f"source verification failures: {failures}")
    source_verification = {
        "declared_count": len(bindings),
        "matched_count": sum(1 for item in records if item["matched"]),
        "all_complete_reads_succeeded": all(
            item["complete_read"] != "parse_failed" for item in records
        ),
        "parsed_counts": parsed_counts,
        "records": records,
        "handoff_path": str(HANDOFF_PATH),
        "handoff_sha256": sha256_bytes(handoff_bytes),
        "review_plan_path": str(PLAN_PATH),
        "review_plan_sha256": sha256_bytes((repo / PLAN_PATH).read_bytes()),
    }
    return source_verification, documents


def verify_git_bindings(repo: Path) -> dict[str, Any]:
    commands = [
        run_git("rev-parse", "HEAD"),
        run_git("show", "-s", "--format=%P", "HEAD"),
        run_git("merge-base", "--is-ancestor", SOURCE_SNAPSHOT_COMMIT, "HEAD"),
        run_git("show", f"{AUTHORITY_COMMIT}:{HANDOFF_PATH.as_posix()}"),
        run_git("show", "-s", "--format=%P", SOURCE_SNAPSHOT_COMMIT),
        run_git("diff-tree", "--no-commit-id", "--name-only", "-r", SOURCE_SNAPSHOT_COMMIT),
    ]
    require(all(item["exit_code"] == 0 for item in commands), "git binding command failed")
    head = commands[0]["stdout"].strip()
    parents = commands[1]["stdout"].split()
    require(head == PUBLISHED_CLAIM_COMMIT, f"unexpected HEAD {head}")
    require(parents == [AUTHORITY_COMMIT], f"unexpected claim parents {parents}")
    authority_handoff = commands[3]["stdout"].encode("utf-8")
    current_handoff = HANDOFF_PATH.read_bytes()
    require(authority_handoff == current_handoff, "handoff differs from authority blob")

    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    snapshot_parent = commands[4]["stdout"].strip()
    require(snapshot_parent == snapshot["parent_sha"], "snapshot parent mismatch")
    changed = set(commands[5]["stdout"].splitlines())
    expected = set(snapshot["source_path_sha256"]) | {SNAPSHOT_PATH.as_posix()}
    require(changed == expected, f"snapshot path set differs: {sorted(changed ^ expected)}")
    for relative, expected_hash in snapshot["source_path_sha256"].items():
        blob = subprocess.run(
            ["git", "show", f"{SOURCE_SNAPSHOT_COMMIT}:{relative}"],
            check=False,
            capture_output=True,
        )
        require(blob.returncode == 0, f"snapshot blob unavailable: {relative}")
        require(sha256_bytes(blob.stdout) == expected_hash, f"snapshot blob mismatch: {relative}")
    return {
        "published_claim_commit": head,
        "authority_commit": AUTHORITY_COMMIT,
        "source_snapshot_commit": SOURCE_SNAPSHOT_COMMIT,
        "snapshot_parent": snapshot_parent,
        "snapshot_changed_paths": sorted(changed),
        "snapshot_path_sha256": snapshot["source_path_sha256"],
        "authority_handoff_matches_current": True,
        "commands": commands,
    }


def add_case(
    cases: list[Case], category: str, name: str, body: Callable[[], dict[str, Any] | None]
) -> None:
    index = len(cases) + 1
    cases.append(Case(f"CM6-{index:03d}", category, name, body))


def equality_body(actual: Any, expected: Any, label: str) -> Callable[[], dict[str, Any]]:
    def body() -> dict[str, Any]:
        require(actual == expected, f"{label} differs")
        return {"canonical_sha256": sha256_bytes(canonical_json(jsonable(actual)))}
    return body


def build_cases(
    predecessor_contract: dict[str, Any],
    current_contract: dict[str, Any],
    predecessor_schema: dict[str, Any],
    current_schema: dict[str, Any],
) -> tuple[list[Case], dict[str, Any]]:
    cases: list[Case] = []
    old_effective = predecessor_contract["effective_contract"]
    new_effective = current_contract["effective_contract"]
    old_artifact = old_effective["artifact_custody"]
    new_artifact = new_effective["artifact_custody"]

    require(len(old_effective) == 25 and len(new_effective) == 25, "unexpected section count")
    require(list(old_effective) == list(new_effective), "effective-contract key order changed")
    for section in old_effective:
        if section == "artifact_custody":
            continue
        add_case(
            cases,
            "definition_preservation",
            f"effective_contract.{section} is unchanged",
            equality_body(new_effective[section], old_effective[section], section),
        )

    for definition in ("raw_cost", "allocation_edge", "manifest"):
        add_case(
            cases,
            "schema_preservation",
            f"$defs.{definition} is unchanged",
            equality_body(
                current_schema["$defs"][definition],
                predecessor_schema["$defs"][definition],
                definition,
            ),
        )

    unchanged_schema_keys = [
        "$schema",
        "$id",
        "title",
        "$comment",
        "x-component-plane-arm-relation",
        "x-outcome-relation",
        "x-edge-reason-relation",
    ]
    for key in unchanged_schema_keys:
        add_case(
            cases,
            "schema_preservation",
            f"top-level schema key {key} is unchanged",
            equality_body(current_schema[key], predecessor_schema[key], key),
        )

    def schema_delta() -> dict[str, Any]:
        old_keys = set(predecessor_schema)
        new_keys = set(current_schema)
        require(new_keys - old_keys == {"x-pre-run-outcome-relation"}, "unexpected schema key added")
        require(old_keys - new_keys == set(), "predecessor schema key removed")
        require(set(current_schema["$defs"]) - set(predecessor_schema["$defs"]) == {"pre_run_outcome"}, "unexpected definition delta")
        require(set(predecessor_schema["$defs"]) <= set(current_schema["$defs"]), "prior definition removed")
        return {"added_top_key": "x-pre-run-outcome-relation", "added_definition": "pre_run_outcome"}

    add_case(cases, "schema_preservation", "schema delta is limited to the fourth carrier", schema_delta)

    def one_of_extension() -> dict[str, Any]:
        old_refs = predecessor_schema["oneOf"]
        new_refs = current_schema["oneOf"]
        require(new_refs[:3] == old_refs, "prior oneOf alternatives changed or reordered")
        require(new_refs[3:] == [{"$ref": "#/$defs/pre_run_outcome"}], "fourth alternative differs")
        return {"alternatives": new_refs}

    add_case(cases, "schema_preservation", "oneOf preserves three domains and appends pre_run_outcome", one_of_extension)

    for key in old_artifact:
        if key == "manifest_schema":
            continue
        add_case(
            cases,
            "artifact_custody_preservation",
            f"artifact_custody.{key} is unchanged",
            equality_body(new_artifact[key], old_artifact[key], f"artifact_custody.{key}"),
        )

    def artifact_delta() -> dict[str, Any]:
        require(set(new_artifact) - set(old_artifact) == {"pre_run_outcome"}, "unexpected artifact-custody key added")
        require(set(old_artifact) - set(new_artifact) == set(), "artifact-custody key removed")
        old_ms = old_artifact["manifest_schema"]
        new_ms = new_artifact["manifest_schema"]
        require(set(old_ms) == set(new_ms), "manifest-schema metadata shape changed")
        changed = {key for key in old_ms if old_ms[key] != new_ms[key]}
        require(changed == {"path", "sha256"}, f"unexpected manifest-schema changes {changed}")
        require(new_ms["path"] == CURRENT_SCHEMA_PATH.as_posix(), "current schema path not bound")
        require(new_ms["sha256"] == sha256_bytes(CURRENT_SCHEMA_PATH.read_bytes()), "current schema hash not bound")
        require(
            new_effective["cost_contract"]["serialized_schema"]
            == old_effective["cost_contract"]["serialized_schema"],
            "reviewed cost schema binding changed",
        )
        return {"changed_existing_paths": ["manifest_schema.path", "manifest_schema.sha256"], "added": "pre_run_outcome"}

    add_case(cases, "artifact_custody_preservation", "artifact-custody delta is exactly scoped", artifact_delta)

    for field, expected in (
        ("approved_by", None),
        ("execution_authorized", False),
        ("evidence_eligible", False),
        ("scientific_run_performed", False),
    ):
        add_case(
            cases,
            "scope_boundary",
            f"{field} remains {expected!r}",
            equality_body(current_contract[field], expected, field),
        )

    allowed_rows = [
        copy.deepcopy(row)
        for row in old_artifact["outcome_relation"]
        if row["status"] in {"refused_before_run", "infrastructure_stopped"}
        and "authorize_and_claim_nonce" in row["stages"]
    ]
    allowed_pairs = {(row["reason_code"], row["status"]) for row in allowed_rows}
    reason_to_status = {reason: status for reason, status in allowed_pairs}
    require(len(allowed_rows) == len(allowed_pairs) == 15, "derived relation is not exactly 15 pairs")
    require(sum(reason.startswith("AUTH_") for reason, _ in allowed_pairs) == 7, "AUTH count differs")
    require(sum(status == "infrastructure_stopped" for _, status in allowed_pairs) == 7, "infrastructure count differs")

    add_case(
        cases,
        "relation_derivation",
        "contract pre-run relation equals filtered predecessor outcome relation",
        equality_body(new_artifact["pre_run_outcome"]["status_reason_relation"], allowed_rows, "contract relation"),
    )
    add_case(
        cases,
        "relation_derivation",
        "schema x-pre-run relation equals filtered predecessor outcome relation",
        equality_body(current_schema["x-pre-run-outcome-relation"], allowed_rows, "schema relation"),
    )
    add_case(
        cases,
        "relation_derivation",
        "contract and schema pre-run relations agree",
        equality_body(current_schema["x-pre-run-outcome-relation"], new_artifact["pre_run_outcome"]["status_reason_relation"], "schema-contract relation"),
    )

    pre_def = current_schema["$defs"]["pre_run_outcome"]
    schema_reasons = set(pre_def["properties"]["reason_code"]["enum"])
    schema_statuses = set(pre_def["properties"]["status"]["enum"])
    add_case(cases, "relation_derivation", "reason enum is exactly the derived domain", equality_body(schema_reasons, set(reason_to_status), "reason enum"))
    add_case(cases, "relation_derivation", "status enum is exactly the derived codomain", equality_body(schema_statuses, {"refused_before_run", "infrastructure_stopped"}, "status enum"))

    base_context = {
        "schema": current_schema,
        "allowed_pairs": allowed_pairs,
        "trusted_context": fixed_trusted_context(),
        "observed_bytes": FIXED_OBSERVED_BYTES,
        "expected_unavailable_reason": None,
        "expected_policy_failure": None,
        "policy_failure_independently_obtained": True,
    }

    for reason, status in sorted(allowed_pairs):
        value = fixed_pre_run(reason, status)
        context = dict(base_context)
        if reason == "POLICY_RESOLUTION_FAILED":
            context["expected_policy_failure"] = fixed_policy_failure()
        add_case(
            cases,
            "required_valid_early_outcomes",
            f"{reason}/{status} validates without RUN facts",
            lambda value=value, context=context: require_semantic_valid(value, context),
        )

    unavailable_reasons = ["not_read", "not_provided", "read_failed", "capture_unavailable"]
    for index, (reason, status) in enumerate(sorted(allowed_pairs)):
        unavailable_reason = unavailable_reasons[index % len(unavailable_reasons)]
        value = fixed_pre_run(
            reason,
            status,
            observed={"kind": "unavailable", "reason": unavailable_reason},
        )
        context = dict(base_context)
        context["observed_bytes"] = _UNSET
        context["expected_unavailable_reason"] = unavailable_reason
        if reason == "POLICY_RESOLUTION_FAILED":
            context["expected_policy_failure"] = fixed_policy_failure()
        add_case(
            cases,
            "required_valid_early_outcomes",
            f"{reason}/{status} validates with explicit unavailable input",
            lambda value=value, context=context: require_semantic_valid(value, context),
        )

    for reason, status in sorted(allowed_pairs):
        wrong = "infrastructure_stopped" if status == "refused_before_run" else "refused_before_run"
        value = fixed_pre_run(reason, wrong)
        add_case(
            cases,
            "closed_relation_rejections",
            f"{reason} rejects wrong status {wrong}",
            lambda value=value: require_schema_invalid(current_schema, value, "pre_run_outcome"),
        )

    required_fields = list(pre_def["required"])
    for field in required_fields:
        value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
        del value[field]
        add_case(
            cases,
            "closed_shape_rejections",
            f"missing required field {field} is rejected",
            lambda value=value: require_schema_invalid(current_schema, value, "pre_run_outcome"),
        )

    forbidden_fields: list[tuple[str, Any]] = [
        ("run_id", "RUN-fixed"),
        ("id", "RUN-fixed"),
        ("run", {}),
        ("code", {}),
        ("source_sha256", "b" * 64),
        ("inputs", {}),
        ("input", {}),
        ("resources", {}),
        ("directory", {}),
        ("admission", {}),
        ("curve_id", "fixed-curve"),
        ("nonce", "fixed-nonce"),
    ]
    for field, injected in forbidden_fields:
        value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
        value[field] = injected
        add_case(
            cases,
            "forbidden_fabricated_facts",
            f"pre-run carrier rejects {field}",
            lambda value=value: require_schema_invalid(current_schema, value, "pre_run_outcome"),
        )

    trusted_mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("missing task_id", lambda x: x["trusted_handoff"].pop("task_id")),
        ("missing handoff_sha256", lambda x: x["trusted_handoff"].pop("handoff_sha256")),
        ("malformed task_id", lambda x: x["trusted_handoff"].__setitem__("task_id", "TASK-bad")),
        ("sequential new-style ambiguity", lambda x: x["trusted_handoff"].__setitem__("task_id", "TASK-20260908-12")),
        ("uppercase handoff digest", lambda x: x["trusted_handoff"].__setitem__("handoff_sha256", "A" * 64)),
        ("short handoff digest", lambda x: x["trusted_handoff"].__setitem__("handoff_sha256", "a" * 63)),
        ("extra trusted field", lambda x: x["trusted_handoff"].__setitem__("from_receipt", True)),
    ]
    for name, mutate in trusted_mutations:
        value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
        mutate(value)
        add_case(
            cases,
            "trusted_context_schema",
            f"trusted handoff rejects {name}",
            lambda value=value: require_schema_invalid(current_schema, value, "pre_run_outcome"),
        )

    semantic_trust_cases: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
    value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
    context = dict(base_context); context["trusted_context"] = None
    semantic_trust_cases.append(("missing independent context", value, context))
    context = dict(base_context); context["trusted_context"] = fixed_trusted_context(independent=False)
    semantic_trust_cases.append(("receipt-copied expected context", value, context))
    value_bad_task = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
    value_bad_task["trusted_handoff"]["task_id"] = "TASK-20260908-abcdef"
    semantic_trust_cases.append(("mismatched task", value_bad_task, dict(base_context)))
    value_bad_hash = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
    value_bad_hash["trusted_handoff"]["handoff_sha256"] = "b" * 64
    semantic_trust_cases.append(("mismatched handoff hash", value_bad_hash, dict(base_context)))
    for name, value, context in semantic_trust_cases:
        add_case(
            cases,
            "trusted_context_semantics",
            f"semantic verifier rejects {name}",
            lambda value=value, context=context: require_semantic_invalid(value, context),
        )

    valid_timestamps = ["2026-09-09T04:00:00Z", "2026-09-09T04:00:00+00:00"]
    for timestamp in valid_timestamps:
        value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
        value["recorded_at_UTC"] = timestamp
        add_case(
            cases,
            "utc_semantics",
            f"UTC timestamp {timestamp} is admitted",
            lambda value=value: require_semantic_valid(value, dict(base_context)),
        )

    invalid_timestamps = [
        "not-a-dateZ",
        "2026-13-09T04:00:00Z",
        "2026-09-09T25:00:00Z",
        "2026-09-09T04:00:00",
        "2026-09-09T04:00:00+01:00",
        "2026-09-09T04:00:00z",
        "Z",
        "2026-09-09",
    ]
    for timestamp in invalid_timestamps:
        value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
        value["recorded_at_UTC"] = timestamp
        add_case(
            cases,
            "utc_semantics",
            f"malformed or non-UTC timestamp {timestamp!r} is rejected",
            lambda value=value: require_semantic_invalid(value, dict(base_context)),
        )

    observed_schema_mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("available missing kind", lambda x: x["observed_authorization_input"].pop("kind")),
        ("available missing sha256", lambda x: x["observed_authorization_input"].pop("sha256")),
        ("available missing byte_length", lambda x: x["observed_authorization_input"].pop("byte_length")),
        ("available negative byte_length", lambda x: x["observed_authorization_input"].__setitem__("byte_length", -1)),
        ("available uppercase digest", lambda x: x["observed_authorization_input"].__setitem__("sha256", "A" * 64)),
        ("available short digest", lambda x: x["observed_authorization_input"].__setitem__("sha256", "a" * 63)),
        ("available raw bytes", lambda x: x["observed_authorization_input"].__setitem__("raw", "secret")),
        ("unavailable missing reason", lambda x: x["observed_authorization_input"].pop("reason")),
        ("unavailable unknown reason", lambda x: x["observed_authorization_input"].__setitem__("reason", "partial_capture")),
        ("unavailable digest smuggling", lambda x: x["observed_authorization_input"].__setitem__("sha256", "a" * 64)),
    ]
    for name, mutate in observed_schema_mutations:
        unavailable = name.startswith("unavailable")
        observed = {"kind": "unavailable", "reason": "not_read"} if unavailable else None
        value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run", observed=observed)
        mutate(value)
        add_case(
            cases,
            "observed_input_schema",
            f"observed input rejects {name}",
            lambda value=value: require_schema_invalid(current_schema, value, "pre_run_outcome"),
        )

    semantic_observation_cases: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
    value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
    context = dict(base_context); context["observed_bytes"] = FIXED_OBSERVED_BYTES[:-1]
    semantic_observation_cases.append(("partial bytes presented as complete capture", value, context))
    value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
    context = dict(base_context); context["observed_bytes"] = b"different fixed bytes of same length........"[:len(FIXED_OBSERVED_BYTES)]
    semantic_observation_cases.append(("wrong complete bytes", value, context))
    value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
    context = dict(base_context); context["observed_bytes"] = _UNSET
    semantic_observation_cases.append(("digest without independently available complete bytes", value, context))
    value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run", observed={"kind": "unavailable", "reason": "not_read"})
    context = dict(base_context); context["observed_bytes"] = _UNSET; context["expected_unavailable_reason"] = None
    semantic_observation_cases.append(("unavailable form without independent reason", value, context))
    value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run", observed={"kind": "unavailable", "reason": "not_read"})
    context = dict(base_context); context["observed_bytes"] = _UNSET; context["expected_unavailable_reason"] = "read_failed"
    semantic_observation_cases.append(("mismatched unavailable reason", value, context))
    value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run", observed={"kind": "unavailable", "reason": "not_read"})
    context = dict(base_context); context["observed_bytes"] = FIXED_OBSERVED_BYTES; context["expected_unavailable_reason"] = "not_read"
    semantic_observation_cases.append(("unavailable form despite observed bytes", value, context))
    for name, value, context in semantic_observation_cases:
        add_case(
            cases,
            "observed_input_semantics",
            f"semantic verifier rejects {name}",
            lambda value=value, context=context: require_semantic_invalid(value, context),
        )

    empty_value = fixed_pre_run(
        "AUTH_MALFORMED",
        "refused_before_run",
        observed={"kind": "sha256", "sha256": sha256_bytes(b""), "byte_length": 0},
    )
    empty_context = dict(base_context); empty_context["observed_bytes"] = b""
    add_case(cases, "observed_input_semantics", "complete empty input has exact digest and length", lambda: require_semantic_valid(empty_value, empty_context))

    policy_value = fixed_pre_run("POLICY_RESOLUTION_FAILED", "refused_before_run")
    policy_context = dict(base_context); policy_context["expected_policy_failure"] = fixed_policy_failure()
    add_case(cases, "policy_writer_semantics", "exact independently supplied writer failure block is admitted", lambda: require_semantic_valid(policy_value, policy_context))

    missing_policy = fixed_pre_run("POLICY_RESOLUTION_FAILED", "refused_before_run")
    del missing_policy["policy_resolution_failure"]
    add_case(cases, "policy_writer_semantics", "policy failure without writer block is rejected", lambda: require_schema_invalid(current_schema, missing_policy, "pre_run_outcome"))

    for reason, status in sorted(allowed_pairs):
        if reason == "POLICY_RESOLUTION_FAILED":
            continue
        value = fixed_pre_run(reason, status)
        value["policy_resolution_failure"] = fixed_policy_failure()
        add_case(
            cases,
            "policy_writer_semantics",
            f"{reason} cannot smuggle policy writer block",
            lambda value=value: require_schema_invalid(current_schema, value, "pre_run_outcome"),
        )

    for field in list(fixed_policy_failure()):
        value = fixed_pre_run("POLICY_RESOLUTION_FAILED", "refused_before_run")
        del value["policy_resolution_failure"][field]
        add_case(
            cases,
            "policy_writer_semantics",
            f"policy failure rejects stripped writer field {field}",
            lambda value=value: require_schema_invalid(current_schema, value, "pre_run_outcome"),
        )

    policy_schema_mutations: list[tuple[str, str, Any]] = [
        ("served backend", "backend", "openai"),
        ("served provider", "provider", "openai"),
        ("served model", "resolved_model_id", "fixed-model"),
        ("fabricated provenance", "model_provenance", "runtime-verified"),
        ("verified failure", "model_verified", True),
        ("requested effort", "requested_reasoning_effort", "high"),
        ("resolved effort", "reasoning_effort", "high"),
        ("fallback used", "fallback_used", True),
        ("fallback reason", "fallback_reason", "fixed fallback"),
        ("degraded requirements", "degraded_requirements", ["fixed gap"]),
        ("independent serving session", "independent_session", True),
        ("config digest", "config_digest", "b" * 64),
        ("wrong literal note", "note", "resolution failed"),
        ("empty error", "resolution_error", ""),
    ]
    for name, field, replacement in policy_schema_mutations:
        value = fixed_pre_run("POLICY_RESOLUTION_FAILED", "refused_before_run")
        value["policy_resolution_failure"][field] = replacement
        add_case(
            cases,
            "policy_writer_semantics",
            f"policy failure rejects {name}",
            lambda value=value: require_schema_invalid(current_schema, value, "pre_run_outcome"),
        )

    semantic_policy_mutations: list[tuple[str, str, Any]] = [
        ("requested/canonical mismatch", "canonical_policy", "executor-mechanical"),
        ("fabricated adapter version", "adapter_version", "fabricated-v2"),
        ("different exact error", "resolution_error", "LookupError: different"),
    ]
    for name, field, replacement in semantic_policy_mutations:
        value = fixed_pre_run("POLICY_RESOLUTION_FAILED", "refused_before_run")
        value["policy_resolution_failure"][field] = replacement
        context = dict(policy_context)
        add_case(
            cases,
            "policy_writer_semantics",
            f"semantic verifier rejects {name}",
            lambda value=value, context=context: require_semantic_invalid(value, context),
        )

    context = dict(base_context); context["expected_policy_failure"] = None
    add_case(cases, "policy_writer_semantics", "semantic verifier rejects missing authoritative writer output", lambda: require_semantic_invalid(policy_value, context))
    context = dict(policy_context); context["policy_failure_independently_obtained"] = False
    add_case(cases, "policy_writer_semantics", "semantic verifier rejects writer block copied from receipt", lambda: require_semantic_invalid(policy_value, context))

    def standalone_auth_malformed() -> dict[str, Any]:
        value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
        require_schema_valid(current_schema, value)
        require_schema_invalid(predecessor_schema, value)
        require("run" not in value and "id" not in value, "standalone carrier gained RUN facts")
        return {"new_union": "accepted", "predecessor_union": "rejected", "keys": sorted(value)}

    add_case(cases, "union_controls", "standalone AUTH_MALFORMED is the new required-valid domain", standalone_auth_malformed)

    union_invalid_objects = [
        {},
        {"record_type": "pre_run_outcome"},
        {"record_type": "banana"},
        {"status": "refused_before_run", "reason_code": "AUTH_MALFORMED"},
        {"run": {}},
        {"record_type": "raw_cost"},
        {"record_type": "allocation_edge"},
    ]
    for index, value in enumerate(union_invalid_objects, 1):
        add_case(
            cases,
            "union_controls",
            f"four-domain union rejects fixed malformed object {index}",
            lambda value=value: require_schema_invalid(current_schema, value),
        )

    def pre_run_unique_domain() -> dict[str, Any]:
        value = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
        outcomes = {
            name: not schema_errors(current_schema, value, name)
            for name in ("raw_cost", "allocation_edge", "manifest", "pre_run_outcome")
        }
        require(outcomes == {"raw_cost": False, "allocation_edge": False, "manifest": False, "pre_run_outcome": True}, f"domain overlap: {outcomes}")
        return outcomes

    add_case(cases, "union_controls", "pre-run object belongs to exactly the fourth domain", pre_run_unique_domain)

    def manifest_definition_identity_implies_compatibility() -> dict[str, Any]:
        old_bytes = canonical_json(predecessor_schema["$defs"]["manifest"])
        new_bytes = canonical_json(current_schema["$defs"]["manifest"])
        require(old_bytes == new_bytes, "manifest definition changed")
        return {"manifest_definition_sha256": sha256_bytes(new_bytes)}

    add_case(cases, "full_manifest_boundary", "full-manifest schema compatibility is exact definition identity", manifest_definition_identity_implies_compatibility)

    incomplete_manifest = {"run": {"id": "RUN-fixed"}}
    add_case(cases, "full_manifest_boundary", "predecessor rejects manifest with unavailable facts", lambda: require_schema_invalid(predecessor_schema, incomplete_manifest, "manifest"))
    add_case(cases, "full_manifest_boundary", "current schema rejects manifest with unavailable facts", lambda: require_schema_invalid(current_schema, incomplete_manifest, "manifest"))

    mixed = fixed_pre_run("AUTH_MALFORMED", "refused_before_run")
    mixed["run"] = incomplete_manifest["run"]
    add_case(cases, "full_manifest_boundary", "pre-run object mixed with incomplete full manifest is rejected", lambda: require_schema_invalid(current_schema, mixed))

    semantic_contract_strings = {
        "trusted_context": ["already verified task ID", "Neither value is copied from the authorization payload", "Missing trusted dispatch context"],
        "initialization_boundary": ["Do not advance beyond authorize_and_claim_nonce", "actual facts exist", "never by filling fabricated values"],
        "observed_input": ["complete observed byte string", "exact SHA256", "byte length", "partial capture is never"],
        "policy_failure": ["exact governing writer failure block", "not a serving fact"],
        "privacy_and_scope": ["forbid RUN IDs", "scientific inputs", "source/code hashes", "resources", "directories", "admission"],
        "delivery": ["one final LF", "invoking control plane", "Never derive a write path from untrusted requested run data", "failed delivery is not claimed durable"],
    }
    for field, needles in semantic_contract_strings.items():
        def string_body(field=field, needles=needles) -> dict[str, Any]:
            text = new_artifact["pre_run_outcome"][field]
            missing = [needle for needle in needles if needle not in text]
            require(not missing, f"{field} omits {missing}")
            return {"text_sha256": sha256_bytes(text.encode("utf-8")), "required_phrases": needles}
        add_case(cases, "explicit_interface_boundary", f"contract explicitly binds {field}", string_body)

    case_ids = [case.case_id for case in cases]
    require(len(case_ids) == len(set(case_ids)), "duplicate case id")
    require(len(cases) <= MAXIMUM_TOTAL_CASE_EXECUTIONS, "registered suite exceeds budget")
    plan = {
        "registered_complete_suite_cases": len(cases),
        "case_ids": case_ids,
        "case_plan_sha256": sha256_bytes(canonical_json([
            {"case_id": case.case_id, "category": case.category, "description": case.description}
            for case in cases
        ])),
        "derived_early_pairs": [
            {"reason_code": reason, "status": status}
            for reason, status in sorted(allowed_pairs)
        ],
    }
    return cases, plan


def load_context(repo: Path) -> dict[str, Any]:
    source_verification, documents = verify_sources(repo)
    git_binding = verify_git_bindings(repo)
    predecessor_contract = documents[PREDECESSOR_CONTRACT_PATH.as_posix()]
    current_contract = documents[CURRENT_CONTRACT_PATH.as_posix()]
    predecessor_schema = documents[PREDECESSOR_SCHEMA_PATH.as_posix()]
    current_schema = documents[CURRENT_SCHEMA_PATH.as_posix()]
    Draft202012Validator.check_schema(predecessor_schema)
    Draft202012Validator.check_schema(current_schema)
    cases, plan = build_cases(
        predecessor_contract,
        current_contract,
        predecessor_schema,
        current_schema,
    )
    return {
        "source_verification": source_verification,
        "git_binding": git_binding,
        "predecessor_contract": predecessor_contract,
        "current_contract": current_contract,
        "predecessor_schema": predecessor_schema,
        "current_schema": current_schema,
        "cases": cases,
        "plan": plan,
    }


def execute(
    repo: Path,
    context: dict[str, Any],
    selected_case_id: str | None = None,
) -> tuple[dict[str, Any], int]:
    registered_cases: list[Case] = context["cases"]
    cases = [
        case for case in registered_cases
        if selected_case_id is None or case.case_id == selected_case_id
    ]
    require(cases, f"unknown selected case {selected_case_id}")
    started_at = utc_now()
    wall_start = time.perf_counter_ns()
    cpu_start = time.process_time_ns()
    usage_start = resource.getrusage(resource.RUSAGE_SELF)
    results: list[dict[str, Any]] = []
    for case in cases:
        case_started = utc_now()
        case_wall_start = time.perf_counter_ns()
        case_cpu_start = time.process_time_ns()
        try:
            observation = case.body() or {}
            passed = True
            error = None
        except Exception as exc:
            observation = {}
            passed = False
            error = f"{type(exc).__name__}: {exc}"
        case_cpu_ns = time.process_time_ns() - case_cpu_start
        case_wall_ns = time.perf_counter_ns() - case_wall_start
        if case_wall_ns > int(PER_CASE_SECONDS * 1e9):
            passed = False
            error = (error + "; " if error else "") + "per-case wall limit exceeded"
        results.append({
            "case_id": case.case_id,
            "category": case.category,
            "description": case.description,
            "started_at_utc": case_started,
            "finished_at_utc": utc_now(),
            "wall_nanoseconds": case_wall_ns,
            "cpu_nanoseconds": case_cpu_ns,
            "passed": passed,
            "error": error,
            "observation": observation,
        })

    usage_end = resource.getrusage(resource.RUSAGE_SELF)
    total_wall_ns = time.perf_counter_ns() - wall_start
    total_cpu_ns = time.process_time_ns() - cpu_start
    max_rss_raw = usage_end.ru_maxrss
    max_rss_bytes = max_rss_raw if sys.platform == "darwin" else max_rss_raw * 1024
    passed_count = sum(item["passed"] for item in results)
    failed_count = len(results) - passed_count
    aggregate_limit_ok = (
        (total_wall_ns + total_cpu_ns) / 1e9
        <= AGGREGATE_EXECUTED_CHECK_WALL_CPU_SECONDS
    )
    if not aggregate_limit_ok:
        failed_count += 1

    checks_sha256 = sha256_bytes(Path(__file__).read_bytes())
    targeted = selected_case_id is not None
    receipt = {
        "schema": "crypto.autoresearch.independent_fixed_check_receipt.v1",
        "task_id": TASK_ID,
        "experiment_id": EXPERIMENT_ID,
        "reservation": {
            "recorded_at_utc": RESERVATION_RECORDED_AT_UTC,
            "suite_kind": "one complete final independent fixed-object suite",
            "registered_complete_suite_cases": context["plan"]["registered_complete_suite_cases"],
            "case_plan_sha256": context["plan"]["case_plan_sha256"],
            "maximum_total_case_executions": MAXIMUM_TOTAL_CASE_EXECUTIONS,
            "per_case_seconds": PER_CASE_SECONDS,
            "aggregate_executed_check_wall_cpu_seconds": AGGREGATE_EXECUTED_CHECK_WALL_CPU_SECONDS,
            "maximum_workers": MAXIMUM_WORKERS,
            "memory_limit_bytes": MEMORY_LIMIT_BYTES,
            "scientific_runs": 0,
        },
        "invocation": {
            "started_at_utc": started_at,
            "finished_at_utc": utc_now(),
            "command": [sys.executable, str(Path(__file__).resolve())]
            + (["--case", selected_case_id] if selected_case_id else []),
            "working_directory": str(repo),
            "python": sys.version,
            "platform": platform.platform(),
            "pid": os.getpid(),
            "stdout_contract": "one JSON receipt emitted after terminal completion",
            "stderr_contract": "empty unless interpreter-level failure",
        },
        "source_verification": (
            {
                "declared_count": context["source_verification"]["declared_count"],
                "matched_count": context["source_verification"]["matched_count"],
                "all_complete_reads_succeeded": context["source_verification"]["all_complete_reads_succeeded"],
                "handoff_sha256": context["source_verification"]["handoff_sha256"],
                "review_plan_sha256": context["source_verification"]["review_plan_sha256"],
                "full_records_retained_in_complete_suite": True,
            }
            if targeted else context["source_verification"]
        ),
        "git_binding": (
            {
                "published_claim_commit": context["git_binding"]["published_claim_commit"],
                "authority_commit": context["git_binding"]["authority_commit"],
                "source_snapshot_commit": context["git_binding"]["source_snapshot_commit"],
                "authority_handoff_matches_current": context["git_binding"]["authority_handoff_matches_current"],
                "full_commands_retained_in_complete_suite": True,
            }
            if targeted else context["git_binding"]
        ),
        "checker": {
            "path": str(Path(__file__).resolve().relative_to(repo)),
            "sha256": checks_sha256,
            "producer_checker_imported": False,
            "producer_checker_executed": False,
            "fixed_objects_only": True,
        },
        "plan": context["plan"],
        "cases": results,
        "summary": {
            "complete_suite_invocations": 0 if targeted else 1,
            "targeted_invocations": 1 if targeted else 0,
            "total_fixed_case_executions": len(results),
            "passed_case_executions": passed_count,
            "failed_case_executions": len(results) - passed_count,
            "rerun_case_executions": 0,
            "all_cases_under_10_seconds": all(
                item["wall_nanoseconds"] <= int(PER_CASE_SECONDS * 1e9)
                for item in results
            ),
            "aggregate_wall_nanoseconds": total_wall_ns,
            "aggregate_cpu_nanoseconds": total_cpu_ns,
            "aggregate_wall_plus_cpu_limit_ok": aggregate_limit_ok,
            "maximum_observed_rss_bytes": max_rss_bytes,
            "ru_utime_delta_seconds": usage_end.ru_utime - usage_start.ru_utime,
            "ru_stime_delta_seconds": usage_end.ru_stime - usage_start.ru_stime,
            "workers": 1,
            "memory_enforcement_attempted": context["memory_enforcement"]["attempted"],
            "memory_enforcement_succeeded": context["memory_enforcement"]["succeeded"],
            "memory_enforcement": context["memory_enforcement"],
            "memory_enforcement_note": "The exact RLIMIT_AS attempt is retained; process RSS is measured independently.",
            "scientific_runs": 0,
            "exit_code": 0 if failed_count == 0 and aggregate_limit_ok else 1,
        },
        "inference": {
            "requested_policy": "review-adversarial",
            "resolved_model_id": "gpt-5.6-sol",
            "reasoning_effort": "xhigh",
            "independent_session": True,
            "fallback_used": False,
            "degraded": False,
            "degraded_requirements": [],
            "bedrock_used": False,
            "model_verified": False,
            "probe_performed": False,
            "provenance": "native session assignment; no exact-session serving probe claim",
        },
        "prohibited_operations": {
            "scientific_fixture_generation": False,
            "curve_point_or_divisor_generation": False,
            "cm_or_allocator_computation": False,
            "experimental_panel": False,
            "sage_or_pari_process": False,
            "private_key_signature_or_nonce_operation": False,
            "lock_or_run_allocation": False,
            "prospective_runtime_invocation": False,
            "model_serving_probe": False,
            "state_or_git_mutation": False,
        },
        "administrative_attempts": [],
        "external_process_custody": None,
    }
    return receipt, receipt["summary"]["exit_code"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--describe", action="store_true", help="print the registered plan without executing cases")
    parser.add_argument("--case", help="execute one registered case as a targeted follow-up")
    args = parser.parse_args()
    repo = Path.cwd().resolve()
    memory_enforcement = attempt_memory_limit()
    context = load_context(repo)
    context["memory_enforcement"] = memory_enforcement
    if args.describe:
        print(json.dumps({
            "task_id": TASK_ID,
            "reservation_recorded_at_utc": RESERVATION_RECORDED_AT_UTC,
            "execution_performed": False,
            "plan": context["plan"],
        }, indent=2, sort_keys=True))
        return 0
    receipt, exit_code = execute(repo, context, selected_case_id=args.case)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
