from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role2-box0-interface/check_role2_box0_interface.py"
SPEC = importlib.util.spec_from_file_location("role2_box0_checker", CHECKER_PATH)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def _decision() -> dict:
    paths = {
        "protocol_repository_path": "/protocol",
        "protocol_package_path": "/protocol",
        "decision_json": "/protocol/ledger/decisions/DEC-20261007-abcdef.json",
        "producer_bin": "/build/producer/p192_weighted_cm",
        "verifier_bin": "/build/verifier/p192_weighted_cm_verify",
        "supervisor_bin": "/build/supervisor/p192_wcm_box0_supervisor",
        "producer_repository_path": "/src/producer-repository",
        "producer_package_path": "/src/producer-repository/tools/p192-weighted-cm",
        "verifier_repository_path": "/src/verifier-repository",
        "verifier_package_path": "/src/verifier-repository/tools/p192-weighted-cm-verify",
        "supervisor_repository_path": "/src/supervisor-repository",
        "supervisor_package_path": "/src/supervisor-repository/tools/p192-weighted-cm-supervisor",
        "predecessor_dir": "/runs/RUN-SCURVE-111111",
        "factor_base_json": "/runs/RUN-SCURVE-111111/factor-base.json",
        "run_dir": "/runs/RUN-SCURVE-222222",
        "control_dir": "/controls/RUN-SCURVE-222222-restart",
        "audit_file": "/runs/RUN-SCURVE-222222/dependency-audit.json",
    }
    value = {
        "schema": "p192-wcm-role2-box0-dispatch-authorization-v1",
        "decision_id": "DEC-20261007-abcdef",
        "approved_by": "Coordinator",
        "created_at_utc": "2026-10-07T12:00:00Z",
        "execution_authorized": True,
        "experiment_id": "EXP-SCURVE-1a8daf",
        "protocol_version": 2,
        "planned_run_label": "P192-WCM-BOX0",
        "run_id": "RUN-SCURVE-222222",
        "protocol_repository": checker.PROTOCOL_REPOSITORY,
        "protocol_commit": "1" * 40,
        "factor_base_source_commit": "2" * 40,
        "producer_commit": "2" * 40,
        "verifier_commit": "4" * 40,
        "supervisor_commit": "5" * 40,
        "producer_binary_sha256": "6" * 64,
        "verifier_binary_sha256": "7" * 64,
        "supervisor_binary_sha256": "8" * 64,
        "predecessor_run_id": "RUN-SCURVE-111111",
        "predecessor_artifacts": {name: "9" * 64 for name in checker.PREDECESSOR_PATHS},
        "protected_protocol_blobs": {
            name: checker.sha256_path(path)
            for name, path in checker.PROTECTED_PROTOCOL_PATHS.items()
        },
        "paths": paths,
    }
    value.update(checker.resolved_argv(value))
    return value


def _git(repository: Path, *arguments: str) -> str:
    environment = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Role2 Test",
        "GIT_AUTHOR_EMAIL": "role2@example.invalid",
        "GIT_COMMITTER_NAME": "Role2 Test",
        "GIT_COMMITTER_EMAIL": "role2@example.invalid",
    }
    result = subprocess.run(
        ["git", "-C", str(repository), *arguments], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
    )
    return result.stdout.decode("utf-8").strip()


def _init_repository(repository: Path) -> None:
    repository.mkdir(parents=True)
    _git(repository, "init", "-q")


def _commit_all(repository: Path, message: str) -> str:
    _git(repository, "add", "-A")
    _git(repository, "commit", "-q", "-m", message)
    return _git(repository, "rev-parse", "HEAD")


def _write_bytes(path: Path, data: bytes, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    if executable:
        path.chmod(0o755)


def _canonical(path: Path, value: object) -> None:
    _write_bytes(path, checker.canonical_json_bytes(value))


def _implementation_checkout(base: Path, role: str, suffix: tuple[str, ...]) -> tuple[Path, Path, str]:
    repository = base / f"{role}-repository"
    package = repository.joinpath(*suffix)
    _init_repository(repository)
    _write_bytes(package / "Cargo.toml", f"[package]\nname='{role}'\nversion='0.1.0'\n".encode())
    _write_bytes(package / "src/lib.rs", f"pub fn {role}() {{}}\n".encode())
    _write_bytes(repository / "Cargo.lock", f"# {role} lock\n".encode())
    commit = _commit_all(repository, f"{role} source")
    return repository, package, commit


def _committed_decision_fixture(base: Path) -> tuple[Path, dict, dict]:
    protocol = base / "protocol"
    _init_repository(protocol)
    for relative in checker.PROTECTED_PROTOCOL_RELATIVE_PATHS.values():
        _write_bytes(protocol / relative, (ROOT / relative).read_bytes())
    protocol_commit = _commit_all(protocol, "frozen protocol")

    producer_repo, producer_package, producer_commit = _implementation_checkout(
        base, "producer", ("tools", "p192-weighted-cm"),
    )
    verifier_repo, verifier_package, verifier_commit = _implementation_checkout(
        base, "verifier", ("tools", "p192-weighted-cm-verify"),
    )
    supervisor_repo, supervisor_package, supervisor_commit = _implementation_checkout(
        base, "supervisor", ("tools", "p192-weighted-cm-supervisor"),
    )
    binaries: dict[str, Path] = {}
    for role, name in (
        ("producer", "p192_weighted_cm"),
        ("verifier", "p192_weighted_cm_verify"),
        ("supervisor", "p192_wcm_box0_supervisor"),
    ):
        binaries[role] = base / "binaries" / role / name
        _write_bytes(binaries[role], f"{role}-binary\n".encode(), executable=True)

    predecessor = base / "runs/RUN-SCURVE-111111"
    factor_base = {"schema": "p192-wcm-factor-base-v1", "source_commit": producer_commit}
    _canonical(predecessor / "factor-base.json", factor_base)
    _write_bytes(
        predecessor / "factor-base.sha256",
        f'{checker.sha256_path(predecessor / "factor-base.json")}  factor-base.json\n'.encode(),
    )
    for name in (
        "verification.json", "independent-verification.json",
        "independent-agreement.json", "independent-verifier-receipt.json",
    ):
        _canonical(predecessor / name, {
            "protocol_commit": protocol_commit,
            "source_commit": producer_commit,
            "overall_status": "PASS",
        })

    decision = _decision()
    decision.update({
        "protocol_commit": protocol_commit,
        "factor_base_source_commit": producer_commit,
        "producer_commit": producer_commit,
        "verifier_commit": verifier_commit,
        "supervisor_commit": supervisor_commit,
        "producer_binary_sha256": checker.sha256_path(binaries["producer"]),
        "verifier_binary_sha256": checker.sha256_path(binaries["verifier"]),
        "supervisor_binary_sha256": checker.sha256_path(binaries["supervisor"]),
        "predecessor_artifacts": {
            name: checker.sha256_path(predecessor / name) for name in checker.PREDECESSOR_PATHS
        },
    })
    decision["paths"] = {
        "protocol_repository_path": str(protocol),
        "protocol_package_path": str(protocol),
        "decision_json": str(protocol / "ledger/decisions/DEC-20261007-abcdef.json"),
        "producer_bin": str(binaries["producer"]),
        "verifier_bin": str(binaries["verifier"]),
        "supervisor_bin": str(binaries["supervisor"]),
        "producer_repository_path": str(producer_repo),
        "producer_package_path": str(producer_package),
        "verifier_repository_path": str(verifier_repo),
        "verifier_package_path": str(verifier_package),
        "supervisor_repository_path": str(supervisor_repo),
        "supervisor_package_path": str(supervisor_package),
        "predecessor_dir": str(predecessor),
        "factor_base_json": str(predecessor / "factor-base.json"),
        "run_dir": str(base / "runs/RUN-SCURVE-222222"),
        "control_dir": str(base / "controls/RUN-SCURVE-222222-restart"),
        "audit_file": str(base / "runs/RUN-SCURVE-222222/dependency-audit.json"),
    }
    decision.update(checker.resolved_argv(decision))
    decision_path = Path(decision["paths"]["decision_json"])
    _canonical(decision_path, decision)
    decision_commit = _commit_all(protocol, "fresh Role2 decision")
    custody = checker._decision_custody(decision, decision_path, decision_path.read_bytes(), decision_commit)
    return decision_path, decision, custody


def _artifact_for(base: Path, relative: str) -> dict:
    return checker._artifact_record(base / relative, relative)


def _framed_log(stream: str, payloads: dict[str, bytes]) -> bytes:
    domain = f"P192-WCM-BOX0-SUPERVISOR-{stream.upper()}-v1".encode() + b"\0"
    result = domain + len(checker.SUPERVISOR_CHILDREN).to_bytes(4, "big")
    for child in checker.SUPERVISOR_CHILDREN:
        role = child["role"].encode()
        payload = payloads[child["role"]]
        result += len(role).to_bytes(4, "big") + role + len(payload).to_bytes(8, "big") + payload
    return result


def _build_valid_run(decision: dict, custody: dict) -> Path:
    run_dir = Path(decision["paths"]["run_dir"])
    run_dir.mkdir(parents=True)
    predecessor = Path(decision["paths"]["predecessor_dir"])
    factor_base_sha256 = checker.sha256_path(predecessor / "factor-base.json")
    curve_uid = "urn:ec-record:1:sha256:5531c4a08bdb64b6e86a6e30e9a08aa57edef7af15ac5f6d4d2a83a53bf2f646"

    _write_bytes(run_dir / "retained-candidates.jsonl", b"")
    _write_bytes(run_dir / "complete-relations.jsonl", b"")
    _write_bytes(run_dir / "partial-relations.jsonl", b"")
    disposition = bytearray()
    for index, v, x in checker.box0_pairs():
        primitive = __import__("math").gcd(abs((x - checker.TRACE_T * v) // 2), v) == 1
        disposition += bytes([4 if primitive else 0]) + index.to_bytes(8, "big") + b"\x00"
    _write_bytes(run_dir / "disposition.bin", bytes(disposition))
    counts = {
        "nonprimitive_duplicate": 93158,
        "complete": 0,
        "one_large_prime": 0,
        "two_large_prime": 0,
        "rejected": 168990,
        "invalid": 0,
        "unresolved": 0,
    }
    disposition_schema = {
        "schema": "p192-wcm-disposition-schema-v1",
        "experiment_id": "EXP-SCURVE-1a8daf",
        "protocol_version": 2,
        "protocol_commit": decision["protocol_commit"],
        "producer_commit": decision["producer_commit"],
        "producer_binary_sha256": decision["producer_binary_sha256"],
        "curve_uid": curve_uid,
        "factor_base_source_commit": decision["factor_base_source_commit"],
        "factor_base_sha256": factor_base_sha256,
        "shell_id": "BOX-0",
        "logical_shard_record_count": 1048576,
        "worker_count": 32,
        "byte_order": "big-endian",
        "record_prefix_byte_length": 10,
        "certificate_digest_byte_length": 64,
        "candidate_index_scope": "shell-local-zero-based",
        "status_codes": [
            {"code": code, "name": name, "has_certificates": code in (1, 2, 3)}
            for code, name in checker.STATUS_NAMES.items()
        ],
        "append_paths": checker.APPEND_PATHS,
    }
    _canonical(run_dir / "disposition-schema.json", disposition_schema)
    candidate_raw, candidate_shard, candidate_shell = checker._candidate_roots()
    disposition_raw, disposition_shard, disposition_shell = checker._disposition_roots(bytes(disposition))
    checkpoint = {
        "schema": "p192-wcm-checkpoint-v1",
        "curve_uid": curve_uid,
        "protocol_commit": decision["protocol_commit"],
        "producer_commit": decision["producer_commit"],
        "producer_binary_sha256": decision["producer_binary_sha256"],
        "factor_base_sha256": factor_base_sha256,
        "shell_id": "BOX-0",
        "shard_index": 0,
        "first_candidate_index": 0,
        "record_count": 262148,
        "candidate_shard_sha256": candidate_shard,
        "disposition_shard_sha256": disposition_shard,
        "next_candidate_index": 262148,
        "phase_counters": {
            "seen": "262148", "primitive": "168990", "duplicate": "93158",
            "complete": "0", "one_lp": "0", "two_lp": "0",
            "rejected": "168990", "invalid": "0", "unresolved": "0",
        },
        "committed_outputs": {
            relative: {
                "byte_length": str((run_dir / relative).stat().st_size),
                "prefix_sha256": checker.sha256_path(run_dir / relative),
            }
            for relative in checker.APPEND_PATHS
        },
        "previous_checkpoint_sha256": "0" * 64,
    }
    _write_bytes(
        run_dir / "checkpoint-chain.jsonl",
        checker.canonical_json_bytes(checkpoint) + b"\n",
    )
    predecessor_records = {
        "run_id": decision["predecessor_run_id"],
        "factor_base": _artifact_for(predecessor, "factor-base.json"),
        "factor_base_sidecar": _artifact_for(predecessor, "factor-base.sha256"),
        "producer_verification": _artifact_for(predecessor, "verification.json"),
        "independent_verification": _artifact_for(predecessor, "independent-verification.json"),
        "independent_agreement": _artifact_for(predecessor, "independent-agreement.json"),
        "supervisor_receipt": _artifact_for(predecessor, "independent-verifier-receipt.json"),
    }
    candidate = {
        "schema": "p192-wcm-candidate-stream-v1",
        "experiment_id": "EXP-SCURVE-1a8daf",
        "protocol_version": 2,
        "protocol_commit": decision["protocol_commit"],
        "producer_commit": decision["producer_commit"],
        "producer_binary_sha256": decision["producer_binary_sha256"],
        "curve_uid": curve_uid,
        "factor_base_sha256": factor_base_sha256,
        "factor_base_source_commit": decision["factor_base_source_commit"],
        "predecessor": predecessor_records,
        "shell_id": "BOX-0",
        "bounds": {"v_min": 1, "v_max": 8, "x_min": 0, "x_max_inclusive": 65536},
        "candidate_count": 262148,
        "primitive_count": 168990,
        "duplicate_count": 93158,
        "logical_shard_record_count": 1048576,
        "shard_count": 1,
        "candidate_shards": [{
            "shard_index": 0, "first_candidate_index": 0, "record_count": 262148,
            "virtual_record_byte_length": 4194368, "records_sha256": candidate_raw,
            "candidate_shard_sha256": candidate_shard,
        }],
        "candidate_shell_sha256": candidate_shell,
        "disposition_schema": _artifact_for(run_dir, "disposition-schema.json"),
        "disposition": {
            "artifact": _artifact_for(run_dir, "disposition.bin"),
            "record_count": 262148,
            "shards": [{
                "shard_index": 0, "first_candidate_index": 0,
                "record_count": 262148, "byte_offset": 0,
                "byte_length": len(disposition), "records_sha256": disposition_raw,
                "disposition_shard_sha256": disposition_shard,
            }],
            "shell_sha256": disposition_shell,
        },
        "status_counts": counts,
        "retained_candidates": {"artifact": _artifact_for(run_dir, "retained-candidates.jsonl"), "record_count": 0},
        "complete_relations": {"artifact": _artifact_for(run_dir, "complete-relations.jsonl"), "record_count": 0},
        "partial_relations": {"artifact": _artifact_for(run_dir, "partial-relations.jsonl"), "record_count": 0},
        "checkpoint_chain": {"artifact": _artifact_for(run_dir, "checkpoint-chain.jsonl"), "record_count": 1},
        "complete": True,
    }
    _canonical(run_dir / "candidate-stream.json", candidate)
    bindings = checker._binding_values_from_candidate(candidate)
    verification = {
        "schema": "p192-wcm-shell-verification-v1",
        "experiment_id": "EXP-SCURVE-1a8daf", "protocol_version": 2,
        "role": "producer_self_check", "overall_status": "PASS", "worker_count": 32,
        "bindings": bindings,
        "checks": [{"check_id": name, "status": "PASS"} for name in checker.PRODUCER_CHECKS],
        "artifacts": [_artifact_for(run_dir, path) for path in checker.PRODUCER_PATHS[:-1]],
    }
    _canonical(run_dir / "verification.json", verification)
    independent = {
        "schema": "p192-wcm-shell-independent-verification-v1",
        "experiment_id": "EXP-SCURVE-1a8daf", "protocol_version": 2,
        "role": "isolated_independent_verifier", "overall_status": "PASS", "worker_count": 1,
        "verifier_commit": decision["verifier_commit"],
        "verifier_binary_sha256": decision["verifier_binary_sha256"],
        "bindings": bindings,
        "checks": [{"check_id": name, "status": "PASS"} for name in checker.INDEPENDENT_CHECKS],
        "source_artifacts": [_artifact_for(run_dir, path) for path in checker.PRODUCER_PATHS],
        "independence": {
            "separate_process": True, "producer_outputs_closed_before_start": True,
            "no_in_memory_producer_state": True, "crypto_lib_dependency": False,
            "producer_package_dependency": False, "shared_implementation_components": [],
        },
    }
    _canonical(run_dir / "independent-verification.json", independent)
    restart = {
        "schema": "p192-wcm-checkpoint-resume-control-v1",
        "experiment_id": "EXP-SCURVE-1a8daf", "protocol_version": 2,
        "protocol_commit": decision["protocol_commit"], "producer_commit": decision["producer_commit"],
        "producer_binary_sha256": decision["producer_binary_sha256"],
        "factor_base_source_commit": decision["factor_base_source_commit"],
        "factor_base_sha256": factor_base_sha256, "shell_id": "BOX-0",
        "fault_point": "after_shard_0_checkpoint_before_final_manifests",
        "expected_fault_exit_code": 75, "observed_fault_exit_code": 75,
        "injected_suffix_hex": "503139322d57434d2d554e434f4d4d49545445442d5355464649582d763100",
        "injected_paths": checker.APPEND_PATHS,
        "fault_argv": decision["producer_fault_argv"], "resume_argv": decision["producer_resume_argv"],
        "comparisons": [
            {"field": path, "fresh_sha256": checker.sha256_path(run_dir / path),
             "resumed_sha256": checker.sha256_path(run_dir / path), "equal": True}
            for path in checker.PRODUCER_PATHS
        ],
        "roots_equal": True, "counters_equal": True, "prefixes_equal": True,
        "overall_status": "PASS",
    }
    _canonical(run_dir / "checkpoint-resume-control.json", restart)
    agreement = {
        "schema": "p192-wcm-shell-independent-agreement-v1",
        "experiment_id": "EXP-SCURVE-1a8daf", "protocol_version": 2, "shell_id": "BOX-0",
        "producer_verification_sha256": checker.sha256_path(run_dir / "verification.json"),
        "independent_verification_sha256": checker.sha256_path(run_dir / "independent-verification.json"),
        "comparisons": [
            {"field": field, "producer": str(bindings[field]), "verifier": str(bindings[field]), "equal": True}
            for field in checker.AGREEMENT_FIELDS
        ],
        "overall_status": "PASS",
    }
    _canonical(run_dir / "independent-agreement.json", agreement)

    source_rows: dict[str, list[dict]] = {}
    for role in ("producer", "verifier", "supervisor"):
        package = Path(decision["paths"][f"{role}_package_path"])
        source_rows[role] = [{"path": "src/lib.rs", "sha256": checker.sha256_path(package / "src/lib.rs")}]
    audit = {
        "schema": "p192-wcm-role2-dependency-audit-v1",
        "identical_source_hashes": [],
        "producer_cargo_lock_sha256": checker.sha256_path(Path(decision["paths"]["producer_repository_path"]) / "Cargo.lock"),
        "producer_cargo_toml_sha256": checker.sha256_path(Path(decision["paths"]["producer_package_path"]) / "Cargo.toml"),
        "producer_git": {"git_head": decision["producer_commit"], "git_top_level": decision["paths"]["producer_repository_path"], "package_root": decision["paths"]["producer_package_path"], "worktree_clean": True},
        "producer_rust_sources": source_rows["producer"],
        "source_clone_screen": checker.compute_source_clone_screen(
            Path(decision["paths"]["producer_package_path"]) / "src",
            Path(decision["paths"]["verifier_package_path"]) / "src",
        ),
        "shared_implementation_components": [],
        "supervisor_cargo_lock_sha256": checker.sha256_path(Path(decision["paths"]["supervisor_repository_path"]) / "Cargo.lock"),
        "supervisor_cargo_toml_sha256": checker.sha256_path(Path(decision["paths"]["supervisor_package_path"]) / "Cargo.toml"),
        "supervisor_curve_arithmetic_found": False,
        "supervisor_git": {"git_head": decision["supervisor_commit"], "git_top_level": decision["paths"]["supervisor_repository_path"], "package_root": decision["paths"]["supervisor_package_path"], "worktree_clean": True},
        "supervisor_rust_sources": source_rows["supervisor"],
        "verifier_cargo_lock_sha256": checker.sha256_path(Path(decision["paths"]["verifier_repository_path"]) / "Cargo.lock"),
        "verifier_cargo_toml_sha256": checker.sha256_path(Path(decision["paths"]["verifier_package_path"]) / "Cargo.toml"),
        "verifier_crypto_lib_found": False,
        "verifier_git": {"git_head": decision["verifier_commit"], "git_top_level": decision["paths"]["verifier_repository_path"], "package_root": decision["paths"]["verifier_package_path"], "worktree_clean": True},
        "verifier_rust_sources": source_rows["verifier"],
    }
    _canonical(run_dir / "dependency-audit.json", audit)
    payloads = {child["role"]: b"" for child in checker.SUPERVISOR_CHILDREN}
    _write_bytes(run_dir / "stdout.log", _framed_log("stdout", payloads))
    _write_bytes(run_dir / "stderr.log", _framed_log("stderr", payloads))
    predecessor_inventory = [_artifact_for(predecessor, path) for path in checker.PREDECESSOR_PATHS]
    producer_inventory = [_artifact_for(run_dir, path) for path in checker.PRODUCER_PATHS]
    children = []
    for role, binary_hash, commit, argv, exit_code in (
        ("canonical_producer", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_fresh_argv"], 0),
        ("checkpoint_fault_control", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_fault_argv"], 75),
        ("checkpoint_resume_control", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_resume_argv"], 0),
        ("isolated_independent_verifier", decision["verifier_binary_sha256"], decision["verifier_commit"], decision["independent_verifier_argv"], 0),
    ):
        children.append({
            "role": role, "binary_sha256": binary_hash, "commit": commit, "argv": argv,
            "expected_exit_code": exit_code, "observed_exit_code": exit_code,
            "stdout_sha256": checker.sha256_bytes(b""), "stderr_sha256": checker.sha256_bytes(b""),
        })
    receipt = {
        "schema": "p192-wcm-shell-supervisor-receipt-v1",
        "experiment_id": "EXP-SCURVE-1a8daf", "protocol_version": 2,
        "planned_run_label": "P192-WCM-BOX0", "run_id": decision["run_id"],
        "decision_id": decision["decision_id"], "decision_custody": custody,
        "protocol_commit": decision["protocol_commit"],
        "factor_base_source_commit": decision["factor_base_source_commit"],
        "producer_commit": decision["producer_commit"], "verifier_commit": decision["verifier_commit"],
        "supervisor_commit": decision["supervisor_commit"], "supervisor_binary_sha256": decision["supervisor_binary_sha256"],
        "predecessor_artifacts_before": predecessor_inventory,
        "predecessor_artifacts_after": predecessor_inventory,
        "producer_artifacts_before_verifier": producer_inventory,
        "producer_artifacts_after_verifier": producer_inventory,
        "children": children,
        "checkpoint_resume_control_sha256": checker.sha256_path(run_dir / "checkpoint-resume-control.json"),
        "independent_agreement_sha256": checker.sha256_path(run_dir / "independent-agreement.json"),
        "independent_verification_sha256": checker.sha256_path(run_dir / "independent-verification.json"),
        "dependency_audit_sha256": checker.sha256_path(run_dir / "dependency-audit.json"),
        "overall_status": "PASS",
    }
    _canonical(run_dir / "independent-verifier-receipt.json", receipt)
    environment = {
        "schema": "p192-wcm-role2-box0-environment-v1", "decision_custody": custody,
        "protocol_commit": decision["protocol_commit"], "factor_base_source_commit": decision["factor_base_source_commit"],
        "producer_commit": decision["producer_commit"], "verifier_commit": decision["verifier_commit"],
        "supervisor_commit": decision["supervisor_commit"], "supervisor_binary_sha256": decision["supervisor_binary_sha256"],
        "producer_binary_sha256": decision["producer_binary_sha256"], "verifier_binary_sha256": decision["verifier_binary_sha256"],
        "supervisor_build": {
            "embedded_protocol_commit": decision["protocol_commit"], "embedded_producer_commit": decision["producer_commit"],
            "embedded_verifier_commit": decision["verifier_commit"], "embedded_supervisor_commit": decision["supervisor_commit"],
            "embedded_build_profile": "release", "embedded_supervisor_dirty": False, "embedded_git_metadata_present": True,
        },
        "child_environment_policy": "inherit_except_removed_commit_variables_and_forbid_loader_overrides",
        "removed_variable_names": ["P192_WCM_PROTOCOL_COMMIT", "P192_WCM_SOURCE_COMMIT", "P192_WCM_VERIFIER_COMMIT"],
        "forbidden_loader_override_names_present": [], "secret_values_recorded": False,
    }
    _canonical(run_dir / "environment.json", environment)
    _canonical(run_dir / "command.txt", decision["supervisor_argv"])
    raw = {
        "schema": "p192-wcm-role2-box0-raw-result-v1", "experiment_id": "EXP-SCURVE-1a8daf",
        "run_id": decision["run_id"], "stage": "P192-WCM-BOX0", "decision_custody": custody,
        "protocol_commit": decision["protocol_commit"], "factor_base_source_commit": decision["factor_base_source_commit"],
        "producer_commit": decision["producer_commit"], "verifier_commit": decision["verifier_commit"],
        "supervisor_commit": decision["supervisor_commit"], "run_dir": str(run_dir),
        "candidate_stream_sha256": checker.sha256_path(run_dir / "candidate-stream.json"),
        "checkpoint_resume_control_sha256": checker.sha256_path(run_dir / "checkpoint-resume-control.json"),
        "agreement_sha256": checker.sha256_path(run_dir / "independent-agreement.json"),
        "audit_sha256": checker.sha256_path(run_dir / "dependency-audit.json"),
        "receipt_sha256": checker.sha256_path(run_dir / "independent-verifier-receipt.json"),
        "scientific_result": True, "scientific_results": ["candidate-stream.json"], "status": "PASS",
    }
    _canonical(run_dir / "raw-result.json", raw)
    manifest = {
        "run": {
            "id": decision["run_id"], "experiment_id": "EXP-SCURVE-1a8daf", "status": "completed",
            "code": {"repository": decision["paths"]["supervisor_repository_path"], "commit": decision["supervisor_commit"], "command": "command.txt", "supervisor_binary_sha256": decision["supervisor_binary_sha256"]},
            "environment": {"path": "environment.json", "sha256": checker.sha256_path(run_dir / "environment.json")},
            "inputs": {"parameters": {"stage": "P192-WCM-BOX0", "shell_id": "BOX-0", "candidate_count": 262148, "predecessor_run_id": decision["predecessor_run_id"], "factor_base_sha256": factor_base_sha256, "decision_id": decision["decision_id"], "decision_commit": custody["decision_commit"], "decision_sha256": custody["decision_sha256"]}},
            "timing": {"started_at_utc": "2026-10-07T12:00:00Z", "completed_at_utc": "2026-10-07T12:00:01Z", "duration_milliseconds": "1000"},
            "result": {"raw_result": "raw-result.json", "scientific_result": True, "certificate": {"kind": "independently_verified_box0_census", "path": "candidate-stream.json", "sha256": checker.sha256_path(run_dir / "candidate-stream.json")}},
            "artifacts": [_artifact_for(run_dir, path) for path in checker.MANIFEST_ARTIFACT_PATHS],
        }
    }
    _canonical(run_dir / "manifest.yaml", manifest)
    return run_dir


def _disposition_schema() -> dict:
    return {
        "schema": "p192-wcm-disposition-schema-v1",
        "experiment_id": "EXP-SCURVE-1a8daf",
        "protocol_version": 2,
        "protocol_commit": "1" * 40,
        "producer_commit": "2" * 40,
        "producer_binary_sha256": "3" * 64,
        "curve_uid": "urn:ec-record:1:sha256:5531c4a08bdb64b6e86a6e30e9a08aa57edef7af15ac5f6d4d2a83a53bf2f646",
        "factor_base_source_commit": "2" * 40,
        "factor_base_sha256": "5" * 64,
        "shell_id": "BOX-0",
        "logical_shard_record_count": 1048576,
        "worker_count": 32,
        "byte_order": "big-endian",
        "record_prefix_byte_length": 10,
        "certificate_digest_byte_length": 64,
        "candidate_index_scope": "shell-local-zero-based",
        "status_codes": [
            {"code": code, "name": name, "has_certificates": code in (1, 2, 3)}
            for code, name in checker.STATUS_NAMES.items()
        ],
        "append_paths": checker.APPEND_PATHS,
    }


def _artifact(path: str) -> dict:
    return {"path": path, "byte_length": 1, "sha256": "a" * 64}


def _producer_verification() -> dict:
    return {
        "schema": "p192-wcm-shell-verification-v1",
        "experiment_id": "EXP-SCURVE-1a8daf",
        "protocol_version": 2,
        "role": "producer_self_check",
        "overall_status": "PASS",
        "worker_count": 32,
        "bindings": {
            "protocol_commit": "1" * 40,
            "producer_commit": "2" * 40,
            "producer_binary_sha256": "3" * 64,
            "factor_base_source_commit": "2" * 40,
            "factor_base_sha256": "5" * 64,
            "shell_id": "BOX-0",
            "candidate_shell_sha256": "6" * 64,
            "disposition_shell_sha256": "7" * 64,
            "disposition_schema_sha256": "8" * 64,
            "status_counts_sha256": "9" * 64,
            "retained_candidates_sha256": "a" * 64,
            "complete_relations_sha256": "b" * 64,
            "partial_relations_sha256": "c" * 64,
            "checkpoint_chain_sha256": "d" * 64,
        },
        "checks": [{"check_id": name, "status": "PASS"} for name in checker.PRODUCER_CHECKS],
        "artifacts": [_artifact(path) for path in checker.PRODUCER_PATHS[:-1]],
    }


def test_package_contract_and_hash_manifest_pass() -> None:
    assert checker.check_package() == []


def test_box0_iterator_count_primitivity_and_boundaries() -> None:
    assert checker.box0_counts() == (262148, 168990, 93158)
    pairs = list(checker.box0_pairs())
    assert pairs[0] == (0, 1, 1)
    assert pairs[32767] == (32767, 1, 65535)
    assert pairs[32768] == (32768, 2, 0)
    assert pairs[65536] == (65536, 2, 65536)
    assert pairs[229379] == (229379, 8, 0)
    assert pairs[-1] == (262147, 8, 65536)


def test_static_contract_rejects_authorization_or_verifier_path_regression() -> None:
    addendum = yaml.safe_load(checker.ADDENDUM.read_text())
    overlay = yaml.safe_load(checker.OVERLAY.read_text())
    mutated = copy.deepcopy(addendum)
    mutated["role2_box0_interface_addendum"]["execution_authorized"] = True
    assert any("authorization" in error for error in checker.collect_contract_errors(mutated, overlay))
    mutated = copy.deepcopy(addendum)
    argv = mutated["role2_box0_interface_addendum"]["stage_binding"]["independent_verifier_argv_template"]
    del argv[4:6]
    assert any("verifier argv" in error for error in checker.collect_contract_errors(mutated, overlay))
    mutated = copy.deepcopy(addendum)
    mutated["role2_box0_interface_addendum"]["checkpoint_and_resume"]["recognized_temporary_paths_in_order"].append("arbitrary.tmp")
    assert any("temporary paths" in error for error in checker.collect_contract_errors(mutated, overlay))
    mutated = copy.deepcopy(addendum)
    mutated["role2_box0_interface_addendum"]["protected_protocol_paths_in_order"].remove(
        "tests/test_p192_wcm_role2_interface.py"
    )
    assert any("protected protocol paths" in error for error in checker.collect_contract_errors(mutated, overlay))


def test_yaml_loader_rejects_duplicate_contract_keys() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "duplicate.yaml"
        path.write_text("shell:\n  shard_count: 1\n  shard_count: 2\n", encoding="utf-8")
        with pytest.raises(yaml.constructor.ConstructorError):
            checker.load_yaml(path)


def test_json_loader_rejects_duplicate_schema_keys() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "duplicate.json"
        path.write_text('{"schema":1,"schema":2}', encoding="utf-8")
        with pytest.raises(ValueError, match="duplicate JSON key"):
            checker.load_json(path)


def test_dispatch_preserves_source_identity_and_exact_resolved_argv() -> None:
    decision = _decision()
    assert decision["factor_base_source_commit"] == decision["producer_commit"]
    assert decision["producer_commit"] != decision["verifier_commit"]
    assert checker.validate_decision(decision) == []
    mutated = copy.deepcopy(decision)
    mutated["independent_verifier_argv"][5] = "/wrong/predecessor"
    assert any("independent_verifier_argv" in error for error in checker.validate_decision(mutated))
    mutated = copy.deepcopy(decision)
    mutated["factor_base_source_commit"] = "a" * 40
    assert any(
        "producer_commit does not equal" in error
        for error in checker.validate_decision(mutated)
    )


def test_dispatch_rejects_implicit_or_overlapping_paths() -> None:
    decision = _decision()
    decision["paths"]["factor_base_json"] = "/tmp/other-factor-base.json"
    decision.update(checker.resolved_argv(decision))
    assert any("factor_base_json" in error for error in checker.validate_decision(decision))
    decision = _decision()
    decision["paths"]["control_dir"] = decision["paths"]["run_dir"] + "/control"
    decision.update(checker.resolved_argv(decision))
    assert any("overlap" in error for error in checker.validate_decision(decision))
    decision = _decision()
    decision["paths"]["producer_package_path"] += "/"
    decision.update(checker.resolved_argv(decision))
    assert checker.validate_decision(decision)
    decision = _decision()
    decision["paths"]["decision_json"] = "//protocol/ledger/decisions/DEC-20261007-abcdef.json"
    decision.update(checker.resolved_argv(decision))
    assert checker.validate_decision(decision)
    decision = _decision()
    decision["paths"]["run_dir"] = decision["paths"]["predecessor_dir"] + "/RUN-SCURVE-222222"
    decision["paths"]["audit_file"] = decision["paths"]["run_dir"] + "/dependency-audit.json"
    decision.update(checker.resolved_argv(decision))
    assert any("immutable input predecessor_dir" in error for error in checker.validate_decision(decision))


def test_committed_decision_binds_git_blob_ancestry_sources_and_binaries() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        parsed, observed_custody, errors = checker.validate_dispatch_decision(decision_path, "pre-dispatch")
        assert errors == []
        assert parsed == decision
        assert observed_custody == custody
        assert custody["decision_sha256"] == checker.sha256_path(decision_path)
        protected = Path(decision["paths"]["protocol_repository_path"]) / checker.PROTECTED_PROTOCOL_RELATIVE_PATHS["role2-artifacts.schema.json"]
        original_mode = stat.S_IMODE(protected.stat().st_mode)
        protected.chmod(original_mode | 0o100)
        _, _, errors = checker.validate_dispatch_decision(decision_path, "pre-dispatch")
        assert any("protected current mode" in error for error in errors)
        protected.chmod(original_mode)
        decision_path.write_bytes(decision_path.read_bytes() + b"\n")
        _, _, errors = checker.validate_dispatch_decision(decision_path, "pre-dispatch")
        assert any("decision bytes invalid" in error or "worktree cleanliness" in error for error in errors)


def test_raw_ancestry_ignores_legacy_graft_overlay() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        repository = Path(temporary) / "repository"
        _init_repository(repository)
        _write_bytes(repository / "protocol.txt", b"frozen\n")
        ancestor = _commit_all(repository, "protocol")
        tree = _git(repository, "rev-parse", f"{ancestor}^{{tree}}")
        descendant = _git(repository, "commit-tree", tree, "-m", "unrelated decision root")
        (repository / ".git/info/grafts").write_text(
            f"{descendant} {ancestor}\n", encoding="ascii",
        )
        forged = subprocess.run(
            ["git", "-C", str(repository), "merge-base", "--is-ancestor", ancestor, descendant],
            check=False,
        )
        assert forged.returncode == 0
        errors: list[str] = []
        assert checker._raw_commit_is_strict_ancestor(
            repository, ancestor, descendant, errors,
        ) is False
        assert errors == []


def test_git_checkout_rejects_symlink_package_and_wrong_head() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        repository, package, commit = _implementation_checkout(
            base, "producer", ("tools", "p192-weighted-cm"),
        )
        errors: list[str] = []
        checker._validate_git_checkout(repository, package, "f" * 40, ("tools", "p192-weighted-cm"), "producer", errors)
        assert any("Git HEAD" in error for error in errors)
        alias = base / "package-alias"
        alias.symlink_to(package, target_is_directory=True)
        errors = []
        checker._validate_git_checkout(repository, alias, commit, ("tools", "p192-weighted-cm"), "producer", errors)
        assert any("symlink" in error for error in errors)


def test_artifact_schema_is_closed_and_requires_factor_base_provenance() -> None:
    document = _disposition_schema()
    assert checker.validate_artifact_document(document) == []
    document["unexpected"] = 1
    assert checker.validate_artifact_document(document)
    document = _disposition_schema()
    del document["factor_base_source_commit"]
    assert checker.validate_artifact_document(document)
    document = _disposition_schema()
    document["schema"] = "p192-wcm-candidate-stream-v1"
    assert checker.validate_artifact_document(document)


def test_verification_schema_and_semantics_freeze_check_and_artifact_order() -> None:
    document = _producer_verification()
    assert checker.validate_artifact_document(document) == []
    document["checks"][0], document["checks"][1] = document["checks"][1], document["checks"][0]
    assert checker.validate_artifact_document(document)
    document = _producer_verification()
    document["checks"][-1]["status"] = "FAIL"
    assert any("overall status" in error for error in checker.validate_artifact_document(document))


def test_canonical_json_and_jsonl_framing() -> None:
    value = {"z": 2, "a": [1, "x"]}
    data = b'{"a":[1,"x"],"z":2}'
    assert checker.canonical_json_bytes(value) == data
    assert checker.decode_canonical_json(data) == value
    with pytest.raises(ValueError):
        checker.decode_canonical_json(data + b"\n")
    with pytest.raises(ValueError):
        checker.decode_canonical_json(b'{"a":1,"a":1}')
    assert checker.decode_canonical_jsonl(data + b"\n" + data + b"\n") == [value, value]
    with pytest.raises(ValueError):
        checker.decode_canonical_jsonl(data)


def test_disposition_parser_enforces_width_index_flag_and_trailing_bytes() -> None:
    raw = b"".join([
        bytes([0]) + (0).to_bytes(8, "big") + b"\x00",
        bytes([1]) + (1).to_bytes(8, "big") + b"\x01" + b"a" * 64,
        bytes([6]) + (2).to_bytes(8, "big") + b"\x00",
    ])
    counts = checker.parse_disposition_bytes(raw, expected_count=3)
    assert counts["nonprimitive_duplicate"] == 1
    assert counts["complete"] == 1
    assert counts["unresolved"] == 1
    with pytest.raises(ValueError):
        checker.parse_disposition_bytes(raw + b"x", expected_count=3)
    bad_flag = bytearray(raw)
    bad_flag[9] = 1
    with pytest.raises(ValueError):
        checker.parse_disposition_bytes(bytes(bad_flag), expected_count=3)


def test_checkpoint_conservation_is_checked() -> None:
    checkpoint = {
        "next_candidate_index": 262148,
        "phase_counters": {
            "seen": "262148", "primitive": "168990", "duplicate": "93158",
            "complete": "100", "one_lp": "200", "two_lp": "300",
            "rejected": "168390", "invalid": "0", "unresolved": "0",
        },
    }
    assert checker.validate_checkpoint(checkpoint) == []
    checkpoint["phase_counters"]["duplicate"] = "93157"
    assert checker.validate_checkpoint(checkpoint)


def test_terminal_status_precedence_is_deterministic() -> None:
    raw = {"failed_phase": "canonical_producer", "failure_reason": "invalid_disposition"}
    assert checker._terminal_failure_expectation(raw, 1, 1) == (
        "FAIL", "canonical_producer", "invalid_disposition",
    )
    assert checker._terminal_failure_expectation(raw, 0, 1) == (
        "INCOMPLETE", "canonical_producer", "unresolved_disposition",
    )
    raw = {"failed_phase": "independent_verifier", "failure_reason": "incomplete_child_artifact"}
    assert checker._terminal_failure_expectation(raw, 0, 0) == (
        "INCOMPLETE", "independent_verifier", "incomplete_child_artifact",
    )


def test_post_run_cross_document_validation_and_receipt_attack() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        parsed, observed_custody, errors = checker.validate_dispatch_decision(
            decision_path, "post-run", run_dir,
        )
        assert errors == []
        assert parsed == decision and observed_custody == custody
        assert checker.validate_post_run(run_dir, decision, custody) == []
        receipt_path = run_dir / "independent-verifier-receipt.json"
        original_receipt = receipt_path.read_bytes()
        receipt = checker.decode_canonical_json(receipt_path.read_bytes())
        receipt["children"][0]["argv"][3] = "BOX-1-minus-BOX-0"
        _canonical(receipt_path, receipt)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("receipt child argv canonical_producer" in error for error in errors)
        receipt_path.write_bytes(original_receipt)
        disposition_path = run_dir / "disposition.bin"
        corrupted = bytearray(disposition_path.read_bytes())
        corrupted[0] = 0
        disposition_path.write_bytes(corrupted)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("primitivity mismatch" in error for error in errors)
        stdout_path = run_dir / "stdout.log"
        stdout_path.unlink()
        stdout_path.symlink_to(run_dir / "stderr.log")
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("symlink" in error for error in errors)


def test_post_run_recomputes_dependency_inventory_cargo_and_clone_screen() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        audit_path = run_dir / "dependency-audit.json"
        audit = checker.decode_canonical_json(audit_path.read_bytes())
        audit["producer_rust_sources"][0]["sha256"] = "f" * 64
        audit["producer_cargo_lock_sha256"] = "e" * 64
        audit["source_clone_screen"]["producer_tree_sha256"] = "d" * 64
        _canonical(audit_path, audit)
        verifier_source = Path(decision["paths"]["verifier_package_path"]) / "src/lib.rs"
        verifier_source.write_bytes(b"pub fn verifier_marker() { crypto_lib::forbidden(); }\n")
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("complete Rust inventory" in error for error in errors)
        assert any("Cargo.lock hash" in error for error in errors)
        assert any("recomputed source clone screen" in error for error in errors)
        assert any("forbidden source marker crypto_lib" in error for error in errors)


def test_nested_target_sources_are_inventoried_and_clone_screened() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        producer = root / "producer"
        verifier = root / "verifier"
        shared = "pub fn hidden() {\n" + "\n".join(
            f"let producer_value_{index} = {index};" for index in range(48)
        ) + "\n}\n"
        for package, marker in ((producer, "producer"), (verifier, "verifier")):
            (package / "src/target").mkdir(parents=True)
            (package / "target").mkdir()
            (package / "src/lib.rs").write_text(f"mod target; pub fn {marker}() {{}}\n")
            (package / "src/target/mod.rs").write_text(shared)
            (package / "target/generated.rs").write_text(shared)
        rows = checker._collect_rust_hash_rows(producer)
        assert [row["path"] for row in rows] == ["src/lib.rs", "src/target/mod.rs"]
        screen = checker.compute_source_clone_screen(producer / "src", verifier / "src")
        assert screen["overall_status"] == "FAIL"
        assert screen["max_match_tokens"] >= 128
        assert any(match["producer_path"] == "target/mod.rs" for match in screen["matches"])


def test_post_run_rejects_compact_or_aliased_producer_dependency() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        verifier_package = Path(decision["paths"]["verifier_package_path"])
        producer_package = Path(decision["paths"]["producer_package_path"])
        relative = os.path.relpath(producer_package, verifier_package)
        manifest = verifier_package / "Cargo.toml"
        manifest.write_text(
            "[package]\nname='verifier'\nversion='0.1.0'\n"
            f"[dependencies]\nbridge={{package='p192-weighted-cm',path='{relative}'}}\n",
            encoding="utf-8",
        )
        audit_path = run_dir / "dependency-audit.json"
        audit = checker.decode_canonical_json(audit_path.read_bytes())
        audit["verifier_cargo_toml_sha256"] = checker.sha256_path(manifest)
        _canonical(audit_path, audit)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("directly names p192-weighted-cm" in error for error in errors)
        assert any("resolves to the producer package" in error for error in errors)


def test_failure_raw_counts_and_completed_inventory_are_replayed() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = Path(decision["paths"]["run_dir"])
        run_dir.mkdir()
        raw = {
            "schema": "p192-wcm-role2-box0-failure-v1",
            "experiment_id": "EXP-SCURVE-1a8daf",
            "run_id": decision["run_id"],
            "stage": "P192-WCM-BOX0",
            "decision_custody": custody,
            "protocol_commit": decision["protocol_commit"],
            "factor_base_source_commit": decision["factor_base_source_commit"],
            "producer_commit": decision["producer_commit"],
            "verifier_commit": decision["verifier_commit"],
            "supervisor_commit": decision["supervisor_commit"],
            "run_dir": str(run_dir),
            "invalid_count": 0,
            "unresolved_count": 0,
            "failed_phase": "independent_verifier",
            "failure_reason": "incomplete_child_artifact",
            "completed_artifacts": [],
            "scientific_result": False,
            "scientific_results": [],
            "status": "INCOMPLETE",
        }
        _write_bytes(run_dir / "candidate-stream.json", b"{malformed")
        _canonical(run_dir / "raw-result.json", raw)
        assert checker.validate_post_run(run_dir, decision, custody) == []

        raw["invalid_count"] = 1
        raw["failed_phase"] = "canonical_producer"
        raw["failure_reason"] = "invalid_disposition"
        raw["status"] = "FAIL"
        _canonical(run_dir / "raw-result.json", raw)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("failure invalid count" in error for error in errors)

        raw["invalid_count"] = 0
        raw["failed_phase"] = "independent_verifier"
        raw["failure_reason"] = "incomplete_child_artifact"
        raw["status"] = "INCOMPLETE"
        raw["completed_artifacts"] = [_artifact_for(run_dir, "candidate-stream.json")]
        _canonical(run_dir / "raw-result.json", raw)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("failure completed artifacts" in error for error in errors)


def test_interface_files_do_not_contain_result_or_authorization_state() -> None:
    addendum = yaml.safe_load(checker.ADDENDUM.read_text())["role2_box0_interface_addendum"]
    overlay = yaml.safe_load(checker.OVERLAY.read_text())
    assert addendum["execution_authorized"] is False
    assert addendum["scientific_status"] == "not_started"
    assert addendum["scientific_results"] == []
    assert overlay["execution_authorized"] is False
    assert overlay["scientific_results"] == []
