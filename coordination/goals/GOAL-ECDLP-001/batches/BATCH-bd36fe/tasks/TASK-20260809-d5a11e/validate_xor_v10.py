#!/usr/bin/env python3
"""Fail-closed v10 control validator for the synthetic EXP-XOR package.

The v10 validator makes the exact archived v8 invocation authoritative instead
of relying on v9's non-canonical nested v8 subprocess. It also binds raw case
path spellings, complete unique case coverage, and the canonical fixture root.
It never executes an experiment and never writes repository artifacts.
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

V6_FIXTURE_ROOT = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/tasks/TASK-20260809-c40deb/fixtures"
V8_ROOT = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/tasks/TASK-20260809-0e21cd"
V8_VALIDATOR = V8_ROOT + "/validate_xor_v8.py"
V8_CONTRACT = V8_ROOT + "/validation_contract_xor_v8.json"
V8_MANIFEST = V8_ROOT + "/fixture_manifest_xor_v8.json"
V8_CASE_SCHEMA = V8_ROOT + "/case_xor_v8.schema.json"
V8_RUN_BINDINGS = V8_ROOT + "/per_arm_run_bindings_xor_v8.json"
V8_SOURCE_BINDINGS = V8_ROOT + "/matrix_source_bindings_xor_v8.json"
V8_METADATA = V8_ROOT + "/matrix_validator_metadata_xor_v8.json"
V7_ROOT = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/tasks/TASK-20260809-2cca8f"
V9_ROOT = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/tasks/TASK-20260809-bcf758"
V10_ROOT = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/tasks/TASK-20260809-d5a11e"

V8_CANONICAL_ARGV = [
    "python3",
    V8_VALIDATOR,
    "--v7-root", V7_ROOT,
    "--contract", V8_CONTRACT,
    "--manifest", V8_MANIFEST,
    "--case-schema", V8_CASE_SCHEMA,
    "--run-bindings", V8_RUN_BINDINGS,
    "--source-bindings", V8_SOURCE_BINDINGS,
    "--validator-metadata", V8_METADATA,
    "--repo-root", ".",
]
V9_CANONICAL_ARGV = [
    "python3",
    V9_ROOT + "/validate_xor_v9.py",
    "--v8-root", V8_ROOT,
    "--contract", V9_ROOT + "/validation_contract_xor_v9.json",
    "--manifest", V9_ROOT + "/fixture_manifest_xor_v9.json",
    "--case-schema", V9_ROOT + "/case_xor_v9.schema.json",
    "--run-bindings", V9_ROOT + "/per_arm_run_bindings_xor_v9.json",
    "--source-bindings", V9_ROOT + "/matrix_source_bindings_xor_v9.json",
    "--validator-metadata", V9_ROOT + "/matrix_validator_metadata_xor_v9.json",
    "--repo-root", ".",
]
V10_CANONICAL_ARGV = [
    "python3",
    V10_ROOT + "/validate_xor_v10.py",
    "--v9-root", V9_ROOT,
    "--contract", V10_ROOT + "/validation_contract_xor_v10.json",
    "--manifest", V10_ROOT + "/fixture_manifest_xor_v10.json",
    "--validator-metadata", V10_ROOT + "/matrix_validator_metadata_xor_v10.json",
    "--repo-root", ".",
]


def fail(message: str) -> None:
    raise ValueError(message)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def compact(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


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


def strict_actual_argv(actual: list[str], canonical: list[str] = V10_CANONICAL_ARGV[1:]) -> None:
    if actual != canonical:
        fail("actual v10 invocation argv is not the exact canonical argv")


def run_exact(command: list[str], expected: list[str], repo_root: Path, label: str) -> None:
    if command != expected:
        fail(f"{label} command is not the exact archived canonical argv")
    result = subprocess.run(command, cwd=repo_root, text=True, capture_output=True, check=False)
    if result.returncode != 0 or result.stdout.strip() != "VALIDATION_PASS":
        fail(f"{label} validator failed: exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}")


def strict_commands(metadata: dict[str, Any], contract: dict[str, Any], repo_root: Path) -> None:
    if contract["command_contract"]["accepted_argv"] != V10_CANONICAL_ARGV:
        fail("v10 contract accepted argv is not canonical")
    if metadata["schema"] != "matrix-validator-metadata/xor-v10" or metadata["validator_version"] != "xor-validator/v10":
        fail("v10 metadata version is not authoritative")
    if metadata["accepted_argv"] != V10_CANONICAL_ARGV or metadata["corrected_command"] != shlex.join(V10_CANONICAL_ARGV):
        fail("v10 corrected command is not exact")
    if contract["authoritative_v8"]["accepted_argv"] != V8_CANONICAL_ARGV:
        fail("authoritative v8 argv is not the exact archived canonical argv")
    if metadata.get("authoritative_v8_argv_bound") is not True or metadata.get("v9_nested_v8_invocation_is_not_authoritative") is not True:
        fail("v10 predecessor authority boundary is missing")
    if any(x in ("--run", "--matrix") for x in metadata["accepted_argv"]):
        fail("v10 command contains an experiment argument")
    if metadata["command_scope"] != "fixture_only_no_run_or_matrix_argument" or metadata["no_experiment_execution"] is not True or contract["no_experiment_execution"] is not True:
        fail("v10 no-run boundary failed")
    if repo_root.is_symlink():
        fail("repository root symlink is not an acceptable command authority")


def strict_v9_snapshot(manifest: dict[str, Any], contract: dict[str, Any], repo_root: Path, v9_root: Path) -> None:
    predecessor = contract["predecessor"]
    if v9_root != repo_root / V9_ROOT or manifest["v9_root"] != V9_ROOT or predecessor["v9_root"] != V9_ROOT:
        fail("v9 predecessor root is not the exact canonical root")
    if manifest["v9_snapshot_commit"] != predecessor["v9_snapshot_commit"] or manifest["v9_snapshot_parent"] != predecessor["v9_snapshot_parent"]:
        fail("v9 snapshot identity disagrees between manifest and contract")
    if predecessor["v9_snapshot_commit"] != "2513b4e7b15ac4ec343fe2622903a47667ba39ce" or predecessor["v9_snapshot_parent"] != "efe31d0812484370f8804644f273f76ed885e1f7":
        fail("v9 snapshot identity is not the archived identity")
    expected = predecessor["v9_artifact_sha256"]
    if manifest["v9_artifact_sha256"] != expected:
        fail("v9 artifact hash map disagrees with contract")
    for path, expected_hash in expected.items():
        actual = repo_root / path
        if not actual.is_file() or hashlib.sha256(actual.read_bytes()).hexdigest() != expected_hash:
            fail(f"v9 artifact hash mismatch: {path}")
    receipt = repo_root / predecessor["v9_snapshot_receipt"]
    if not receipt.is_file() or hashlib.sha256(receipt.read_bytes()).hexdigest() != predecessor["v9_snapshot_receipt_sha256"]:
        fail("v9 snapshot receipt hash mismatch")


def strict_case_authority(manifest: dict[str, Any], contract: dict[str, Any], repo_root: Path) -> None:
    authority = contract["case_authority"]
    if authority["fixture_root"] != V6_FIXTURE_ROOT or Path(authority["fixture_root"]).is_absolute():
        fail("case fixture root is not the exact canonical v6 root")
    if manifest["case_authority"]["fixture_root"] != authority["fixture_root"] or manifest["case_authority"]["accepted_case_file_map"] != authority["accepted_case_file_map"]:
        fail("v10 manifest case authority disagrees with contract")
    v8_manifest = read_json(repo_root / V8_MANIFEST)
    expected = v8_manifest["accepted_case_file_map"]
    if authority["accepted_case_file_map"] != expected:
        fail("v10 case map is not bound to immutable v8 manifest content")
    ids = [item["fixture_id"] for item in authority["accepted_case_file_map"]]
    paths = [item["path"] for item in authority["accepted_case_file_map"]]
    if ids != authority["expected_fixture_ids"] or len(ids) != 6 or len(set(ids)) != 6 or len(paths) != 6 or len(set(paths)) != 6:
        fail("v10 accepted-case coverage is not unique and complete")
    fixture_root = repo_root / authority["fixture_root"]
    for item in authority["accepted_case_file_map"]:
        fixture_id = item["fixture_id"]
        raw_path = item["path"]
        if raw_path != fixture_id + ".json":
            fail(f"accepted case raw path spelling is not canonical: {raw_path}")
        relative = Path(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            fail(f"accepted case path is not root-relative: {raw_path}")
        path = fixture_root / relative
        if path.parent != fixture_root or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            fail(f"accepted case root or hash binding failed: {raw_path}")


def replay_v9_strict_checks(repo_root: Path, v9_root: Path) -> None:
    v9 = load_module("xor_validator_v9_replay", v9_root / "validate_xor_v9.py")
    v7_root = repo_root / V7_ROOT
    v6_root = repo_root / "coordination/goals/GOAL-ECDLP-001/batches/BATCH-bd36fe/tasks/TASK-20260809-c40deb"
    v7 = load_module("xor_validator_v7_replay", v7_root / "validate_xor_v7.py")
    v6 = load_module("xor_validator_v6_replay", v6_root / "validate_xor_v6.py")
    v9_contract = read_json(v9_root / "validation_contract_xor_v9.json")
    v9_manifest = read_json(v9_root / "fixture_manifest_xor_v9.json")
    v9_case_schema = read_json(v9_root / "case_xor_v9.schema.json")
    v9_source_bindings = read_json(v9_root / "matrix_source_bindings_xor_v9.json")
    binding_path = v9_root / "per_arm_run_bindings_xor_v9.json"
    binding_bytes = binding_path.read_bytes()
    v9_run_bindings = json.loads(binding_bytes)
    v9_metadata = read_json(v9_root / "matrix_validator_metadata_xor_v9.json")
    v7_contract = read_json(v7_root / "validation_contract_xor_v7.json")
    v7_index = read_json(v7_root / "per_arm_run_index_xor_v7.json")
    v7_bindings = read_json(v7_root / "matrix_source_bindings_xor_v7.json")
    v7_metadata = read_json(v7_root / "matrix_validator_metadata_xor_v7.json")
    v6_contract = read_json(v6_root / "validation_contract_xor_v6.json")
    matrix = read_json(v6_root / "fixtures/canonical_matrix.json")
    v9.strict_manifest(v9_manifest, v9_contract, repo_root, repo_root / V8_ROOT)
    v9.strict_cases(v9_case_schema, v6_contract, v9_contract, repo_root)
    v9.strict_metadata(v9_metadata, v9_contract)
    v9.strict_source_bindings(v9_source_bindings, v9_contract, repo_root)
    v9.strict_matrix(matrix, v9_run_bindings, binding_bytes, v9_contract, repo_root, v6, v7, v7_contract, v7_index, v7_bindings, v7_metadata)
    v9.strict_mutations(v9_manifest, v9_metadata, v9_contract, v9_case_schema, v6_contract, matrix, v9_run_bindings, v9_source_bindings, binding_bytes, repo_root, repo_root / V8_ROOT, v6, v7, v7_contract, v7_index, v7_bindings, v7_metadata)


def expect_reject(name: str, fn: Callable[[], None]) -> None:
    try:
        fn()
    except (ValueError, KeyError, TypeError, AssertionError, json.JSONDecodeError):
        return
    fail(f"v10 strict mutation unexpectedly passed: {name}")


def strict_mutations(manifest: dict[str, Any], metadata: dict[str, Any], contract: dict[str, Any], repo_root: Path) -> None:
    declared = [item["id"] for item in contract["strict_negative_mutations"]]
    seen: list[str] = []
    def probe(name: str, fn: Callable[[], None]) -> None:
        seen.append(name)
        expect_reject(name, fn)
    bad_contract = copy.deepcopy(contract)
    bad_contract["authoritative_v8"]["accepted_argv"][-1] = str(repo_root)
    probe("exact_v8_argv_relabel", lambda: strict_commands(metadata, bad_contract, repo_root))
    bad_contract = copy.deepcopy(contract)
    bad_manifest = copy.deepcopy(manifest)
    bad_contract["case_authority"]["accepted_case_file_map"][0]["path"] = "./completed_valid.json"
    bad_manifest["case_authority"]["accepted_case_file_map"][0]["path"] = "./completed_valid.json"
    probe("accepted_case_dot_prefix", lambda: strict_case_authority(bad_manifest, bad_contract, repo_root))
    bad_contract = copy.deepcopy(contract)
    bad_manifest = copy.deepcopy(manifest)
    duplicate = [copy.deepcopy(bad_contract["case_authority"]["accepted_case_file_map"][0]) for _ in range(6)]
    bad_contract["case_authority"]["accepted_case_file_map"] = duplicate
    bad_manifest["case_authority"]["accepted_case_file_map"] = copy.deepcopy(duplicate)
    probe("duplicate_case_map", lambda: strict_case_authority(bad_manifest, bad_contract, repo_root))
    bad_contract = copy.deepcopy(contract)
    bad_manifest = copy.deepcopy(manifest)
    relocated = str((repo_root / V6_FIXTURE_ROOT).resolve())
    bad_contract["case_authority"]["fixture_root"] = relocated
    bad_manifest["case_authority"]["fixture_root"] = relocated
    probe("fixture_root_relocation", lambda: strict_case_authority(bad_manifest, bad_contract, repo_root))
    if seen != declared:
        fail(f"v10 mutation declaration mismatch: seen={seen}, declared={declared}")


def main() -> int:
    strict_actual_argv([sys.argv[0], *sys.argv[1:]])
    parser = argparse.ArgumentParser()
    parser.add_argument("--v9-root", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--validator-metadata", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    v9_root = args.v9_root.resolve()
    contract = read_json(args.contract)
    manifest = read_json(args.manifest)
    metadata = read_json(args.validator_metadata)
    strict_commands(metadata, contract, repo_root)
    strict_v9_snapshot(manifest, contract, repo_root, v9_root)
    strict_case_authority(manifest, contract, repo_root)
    run_exact(V8_CANONICAL_ARGV, contract["authoritative_v8"]["accepted_argv"], repo_root, "authoritative v8")
    run_exact(V9_CANONICAL_ARGV, V9_CANONICAL_ARGV, repo_root, "legacy v9")
    replay_v9_strict_checks(repo_root, v9_root)
    strict_mutations(manifest, metadata, contract, repo_root)
    print("VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
