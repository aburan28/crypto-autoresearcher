#!/usr/bin/env python3
"""Fail-closed v8 provenance validator for the synthetic EXP-XOR controls.

The validator first runs the immutable v7 fixture-only validator. It then
checks exact command, predecessor-manifest, case-filename, per-arm provenance,
and source-token bindings. It never executes an experiment and never writes
repository artifacts.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

sys.dont_write_bytecode = True

V6_MANIFEST = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/tasks/TASK-20260809-c40deb/fixtures/fixture_manifest_xor_v6.json"
V6_MATRIX = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/tasks/TASK-20260809-c40deb/fixtures/canonical_matrix.json"
V6_EVENT = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/tasks/TASK-20260809-c40deb/fixtures/canonical_event_ledger.json"
V8_TASK_ROOT = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/tasks/TASK-20260809-0e21cd"
CANONICAL_ARGV = [
    "python3",
    V8_TASK_ROOT + "/validate_xor_v8.py",
    "--v7-root", "coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/tasks/TASK-20260809-2cca8f",
    "--contract", V8_TASK_ROOT + "/validation_contract_xor_v8.json",
    "--manifest", V8_TASK_ROOT + "/fixture_manifest_xor_v8.json",
    "--case-schema", V8_TASK_ROOT + "/case_xor_v8.schema.json",
    "--run-bindings", V8_TASK_ROOT + "/per_arm_run_bindings_xor_v8.json",
    "--source-bindings", V8_TASK_ROOT + "/matrix_source_bindings_xor_v8.json",
    "--validator-metadata", V8_TASK_ROOT + "/matrix_validator_metadata_xor_v8.json",
    "--repo-root", ".",
]


def fail(message: str) -> None:
    raise ValueError(message)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def compact(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(compact(value)).hexdigest()


def check_schema(schema: Any, data: Any, label: str) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        fail(f"{label}: schema error at {list(errors[0].path)}: {errors[0].message}")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_v7_exact(v7: Any, v7_root: Path, repo_root: Path) -> None:
    v6_root = v7_root.parent / "TASK-20260809-c40deb"
    command = [
        sys.executable,
        str(v7_root / "validate_xor_v7.py"),
        "--v6-root", str(v6_root),
        "--contract", str(v7_root / "validation_contract_xor_v7.json"),
        "--manifest", str(v7_root / "fixture_manifest_xor_v7.json"),
        "--case-schema", str(v7_root / "case_xor_v7.schema.json"),
        "--run-index", str(v7_root / "per_arm_run_index_xor_v7.json"),
        "--source-bindings", str(v7_root / "matrix_source_bindings_xor_v7.json"),
        "--validator-metadata", str(v7_root / "matrix_validator_metadata_xor_v7.json"),
        "--repo-root", str(repo_root),
    ]
    result = subprocess.run(command, cwd=repo_root, text=True, capture_output=True, check=False)
    if result.returncode != 0 or result.stdout.strip() != "VALIDATION_PASS":
        fail(f"immutable v7 predecessor validator failed: exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}")


def strict_manifest(manifest: dict[str, Any], contract: dict[str, Any], repo_root: Path) -> None:
    if manifest["schema"] != "xor-fixture-manifest/v8" or manifest["validator_version"] != "xor-validator/v8":
        fail("v8 manifest version is not authoritative")
    binding = contract["manifest_binding"]
    if manifest["v6_manifest"] != V6_MANIFEST or manifest["v6_manifest"] != binding["v6_manifest_path"]:
        fail("v6 manifest pointer is not the exact canonical path")
    path = repo_root / V6_MANIFEST
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != binding["v6_manifest_sha256"] or manifest["v6_manifest_sha256"] != binding["v6_manifest_sha256"]:
        fail("v6 manifest content hash is not bound")
    v6_manifest = read_json(path)
    if v6_manifest.get("schema") != "xor-fixture-manifest/v6":
        fail("v6 predecessor manifest schema is not exact")
    expected_cases = contract["case_authority"]["accepted_case_file_map"]
    if manifest["accepted_case_file_map"] != expected_cases:
        fail("v8 accepted-case map disagrees with contract")
    if manifest["strict_mutation_ids"] != [x["id"] for x in contract["strict_negative_mutations"]]:
        fail("v8 strict mutation list is not authoritative")
    if manifest["v7_accepted_case_count"] != 6 or manifest["v7_negative_mutation_count"] != 21 or not manifest["all_cases_are_applied"] or not manifest["all_negative_cases_must_fail"] or not manifest["fixture_only"] or not manifest["no_experiment_execution"]:
        fail("v8 manifest coverage or no-run boundary failed")


def strict_cases(case_schema: dict[str, Any], v6_contract: dict[str, Any], contract: dict[str, Any], repo_root: Path, case_overrides: dict[str, dict[str, Any]] | None = None) -> None:
    fixture_root = repo_root / contract["case_authority"]["fixture_root"]
    v6_cases = {entry["id"]: entry for entry in v6_contract["accepted_cases"]}
    for binding in contract["case_authority"]["accepted_case_file_map"]:
        fixture_id = binding["fixture_id"]
        path = fixture_root / binding["path"]
        if path.stem != fixture_id or path.name != fixture_id + ".json":
            fail(f"accepted case filename is not bound to fixture id: {path.name}")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != binding["sha256"]:
            fail(f"accepted case hash mismatch: {path.name}")
        case = copy.deepcopy((case_overrides or {}).get(binding["path"], read_json(path)))
        check_schema(case_schema, case, f"accepted case {path.name}")
        if case.get("fixture_id") != fixture_id:
            fail(f"accepted case fixture ID does not match filename: {path.name}")
        spec = v6_cases[fixture_id]
        if case["kind"] != spec["kind"] or case["expected"] != spec["expected"]:
            fail(f"accepted case contract mismatch: {path.name}")
        if case["kind"] == "run" and case["patch"] != spec["patch"]:
            fail(f"accepted case patch mismatch: {path.name}")
        if case["kind"] == "matrix_arm" and (case["terminal_reason"] is None or case["timing_interval"]["stop_ns"] <= case["timing_interval"]["start_ns"] or not case["rss_samples"]):
            fail("unattempted case retained fields are malformed")


def strict_metadata(metadata: dict[str, Any], contract: dict[str, Any]) -> None:
    if contract["command_contract"]["accepted_argv"] != CANONICAL_ARGV:
        fail("contract accepted argv is not the validator's canonical argv")
    if metadata["schema"] != "matrix-validator-metadata/xor-v8" or metadata["validator_version"] != "xor-validator/v8":
        fail("v8 metadata version is not authoritative")
    if metadata["accepted_argv"] != CANONICAL_ARGV or metadata["corrected_command"] != shlex.join(CANONICAL_ARGV):
        fail("corrected command is not the exact accepted argv")
    if "--run" in metadata["accepted_argv"] or "--matrix" in metadata["accepted_argv"] or metadata["command_scope"] != "fixture_only_no_run_or_matrix_argument" or metadata["legacy_command_is_not_authoritative"] is not True or metadata["no_experiment_execution"] is not True:
        fail("v8 command scope or legacy-command boundary failed")


def record_from_binding(entry: dict[str, Any]) -> dict[str, Any]:
    p, b_num, b_den, arm, seed, process_replica, null_replica, shard = entry["arm_key"]
    state, terminal_reason, included, repeats, byte_values, interval_values, rss, cpu = entry["record"]
    raw, stdout, stderr = byte_values
    start_ns, stop_ns, clock_source, unit, flush_complete = interval_values
    return {
        "arm_key": {"p": p, "b_num": b_num, "b_den": b_den, "arm": arm, "seed": seed, "process_replica": process_replica, "null_replica": null_replica, "shard": shard},
        "state": state,
        "run_id": entry["run_id"],
        "terminal_reason": terminal_reason,
        "included_in_metrics": included,
        "wall_repeats": repeats,
        "resource_bytes": {"raw": raw, "stdout": stdout, "stderr": stderr},
        "timing_interval": {"start_ns": start_ns, "stop_ns": stop_ns, "clock_source": clock_source, "unit": unit, "flush_complete": flush_complete},
        "rss_samples": rss,
        "cpu_seconds": cpu,
    }


def strict_source_bindings(bindings: dict[str, Any], contract: dict[str, Any], repo_root: Path) -> None:
    expected = contract["source_binding"]
    if bindings["schema"] != "matrix-source-bindings/xor-v8" or bindings["source_matrix"] != expected["source_matrix"] or bindings["source_matrix_sha256"] != expected["source_matrix_sha256"]:
        fail("source matrix binding is not exact")
    if bindings["source_blobs"] != expected["source_blob_map"]:
        fail("source-token key-to-path map was relabelled or changed")
    for key, item in bindings["source_blobs"].items():
        path = repo_root / item["path"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            fail(f"source blob hash mismatch: {key}")
    source_matrix = repo_root / expected["source_matrix"]
    if not source_matrix.is_file() or hashlib.sha256(source_matrix.read_bytes()).hexdigest() != expected["source_matrix_sha256"]:
        fail("source matrix content hash mismatch")
    if bindings["per_arm_binding"] != {"path": contract["per_arm_binding"]["path"], "sha256": contract["per_arm_binding"]["sha256"]} or bindings["no_experiment_execution"] is not True:
        fail("per-arm binding source identity or no-run boundary failed")


def strict_matrix(matrix: dict[str, Any], bindings: dict[str, Any], binding_file_bytes: bytes, contract: dict[str, Any], repo_root: Path, v6: Any, v7: Any, v7_contract: dict[str, Any], v7_index: dict[str, Any], v7_bindings: dict[str, Any], v7_metadata: dict[str, Any]) -> None:
    v7.strict_matrix(matrix, v6, v7_contract, v7_index, v7_bindings, v7_metadata, repo_root)
    expected_binding = contract["per_arm_binding"]
    if hashlib.sha256(binding_file_bytes).hexdigest() != expected_binding["sha256"]:
        fail("per-arm binding file hash is not archive-bound")
    if bindings["schema"] != "per-arm-run-bindings/xor-v8" or bindings["entry_count"] != expected_binding["entry_count"] or len(bindings["entries"]) != expected_binding["entry_count"]:
        fail("per-arm binding count or schema is incomplete")
    if bindings["source_matrix"] != V6_MATRIX or bindings["source_matrix_sha256"] != contract["source_binding"]["source_matrix_sha256"] or bindings["source_event_template"] != V6_EVENT:
        fail("per-arm source paths are not canonical")
    event_path = repo_root / V6_EVENT
    if not event_path.is_file() or hashlib.sha256(event_path.read_bytes()).hexdigest() != bindings["source_event_template_sha256"]:
        fail("event template source hash mismatch")
    event_template = read_json(event_path)
    entries = bindings["entries"]
    if [x["ordinal"] for x in entries] != list(range(1, 401)):
        fail("per-arm ordinals are not complete and ordered")
    for ordinal, (arm, entry) in enumerate(zip(matrix["arms"], entries), 1):
        expected_run_id = f"RUN-XOR-{ordinal:06d}"
        if entry["run_id"] != expected_run_id or arm["run_id"] != expected_run_id:
            fail("per-arm run ID is not bound to canonical ordinal")
        expected_arm = record_from_binding(entry)
        if expected_arm != arm:
            fail(f"per-arm run record differs at ordinal {ordinal}")
        if entry["arm_key_sha256"] != digest(arm["arm_key"]):
            fail(f"per-arm key digest mismatch at ordinal {ordinal}")
        if entry["record_sha256"] != digest(arm):
            fail(f"per-arm record digest mismatch at ordinal {ordinal}")
        event_record = copy.deepcopy(event_template)
        event_record["run_id"] = expected_run_id
        if entry["event_ledger_sha256"] != digest(event_record):
            fail(f"per-arm event digest mismatch at ordinal {ordinal}")


def expect_reject(name: str, fn: Callable[[], None]) -> None:
    try:
        fn()
    except (ValueError, KeyError, TypeError, AssertionError, json.JSONDecodeError):
        return
    fail(f"v8 strict mutation unexpectedly passed: {name}")


def strict_mutations(manifest: dict[str, Any], metadata: dict[str, Any], contract: dict[str, Any], case_schema: dict[str, Any], v6_contract: dict[str, Any], matrix: dict[str, Any], run_bindings: dict[str, Any], source_bindings: dict[str, Any], binding_file_bytes: bytes, repo_root: Path, v6: Any, v7: Any, v7_contract: dict[str, Any], v7_index: dict[str, Any], v7_bindings: dict[str, Any], v7_metadata: dict[str, Any]) -> None:
    declared = [x["id"] for x in contract["strict_negative_mutations"]]
    seen: list[str] = []
    def probe(name: str, fn: Callable[[], None]) -> None:
        seen.append(name)
        expect_reject(name, fn)
    bad_metadata = copy.deepcopy(metadata)
    bad_metadata["corrected_command"] = "not-an-invocation"
    probe("arbitrary_corrected_argv", lambda: strict_metadata(bad_metadata, contract))
    bad_manifest = copy.deepcopy(manifest)
    bad_manifest["v6_manifest"] = "wrong/manifest.json"
    probe("forged_v6_manifest_pointer", lambda: strict_manifest(bad_manifest, contract, repo_root))
    valid_case = read_json(repo_root / contract["case_authority"]["fixture_root"] / "completed_valid.json")
    probe("accepted_case_filename_swap", lambda: strict_cases(case_schema, v6_contract, contract, repo_root, {"completed_invalid.json": valid_case}))
    bad_matrix = copy.deepcopy(matrix)
    bad_matrix["arms"][0]["cpu_seconds"] += 998
    bad_matrix["shards"][0]["cpu_seconds"] += 998
    bad_matrix["totals"]["arm_cpu_seconds"] += 998
    bad_matrix["totals"]["cpu_seconds"] += 998
    probe("per_arm_cpu_with_recomputed_totals", lambda: strict_matrix(bad_matrix, run_bindings, binding_file_bytes, contract, repo_root, v6, v7, v7_contract, v7_index, v7_bindings, v7_metadata))
    bad_bindings = copy.deepcopy(source_bindings)
    bad_bindings["source_blobs"]["design"] = copy.deepcopy(bad_bindings["source_blobs"]["validator"])
    probe("source_token_relabel", lambda: strict_source_bindings(bad_bindings, contract, repo_root))
    if seen != declared:
        fail(f"v8 mutation declaration mismatch: seen={seen}, declared={declared}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v7-root", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--case-schema", required=True, type=Path)
    parser.add_argument("--run-bindings", required=True, type=Path)
    parser.add_argument("--source-bindings", required=True, type=Path)
    parser.add_argument("--validator-metadata", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    v7_root = args.v7_root.resolve()
    contract = read_json(args.contract)
    manifest = read_json(args.manifest)
    case_schema = read_json(args.case_schema)
    source_bindings = read_json(args.source_bindings)
    binding_path = args.run_bindings.resolve()
    binding_file_bytes = binding_path.read_bytes()
    run_bindings = json.loads(binding_file_bytes)
    metadata = read_json(args.validator_metadata)
    v7 = load_module("xor_validator_v7", v7_root / "validate_xor_v7.py")
    v6_root = v7_root.parent / "TASK-20260809-c40deb"
    v6 = load_module("xor_validator_v6", v6_root / "validate_xor_v6.py")
    v7_contract = read_json(v7_root / "validation_contract_xor_v7.json")
    v7_index = read_json(v7_root / "per_arm_run_index_xor_v7.json")
    v7_bindings = read_json(v7_root / "matrix_source_bindings_xor_v7.json")
    v7_metadata = read_json(v7_root / "matrix_validator_metadata_xor_v7.json")
    matrix = read_json(repo_root / V6_MATRIX)
    run_v7_exact(v7, v7_root, repo_root)
    strict_manifest(manifest, contract, repo_root)
    v6_contract = read_json(v6_root / "validation_contract_xor_v6.json")
    strict_cases(case_schema, v6_contract, contract, repo_root)
    strict_metadata(metadata, contract)
    strict_source_bindings(source_bindings, contract, repo_root)
    strict_matrix(matrix, run_bindings, binding_file_bytes, contract, repo_root, v6, v7, v7_contract, v7_index, v7_bindings, v7_metadata)
    strict_mutations(manifest, metadata, contract, case_schema, v6_contract, matrix, run_bindings, source_bindings, binding_file_bytes, repo_root, v6, v7, v7_contract, v7_index, v7_bindings, v7_metadata)
    print("VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
