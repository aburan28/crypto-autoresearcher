from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role2-box0-interface/check_role2_box0_interface.py"
SPEC = importlib.util.spec_from_file_location("role2_box0_checker", CHECKER_PATH)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def _synthetic_role1_binding(decision: dict) -> dict:
    predecessor = Path(decision["paths"]["predecessor_dir"])
    predecessor_repository = Path(
        decision["paths"]["predecessor_repository_path"]
    )
    predecessor_decision = (
        predecessor_repository / "ledger/decisions/DEC-20261007-111111.yaml"
    )
    receipt = {
        "schema": "p192-wcm-independent-verifier-receipt-v1",
        "experiment_id": "EXP-SCURVE-1a8daf",
        "protocol_version": 2,
        "run_dir": str(predecessor),
        "protocol_commit": decision["protocol_commit"],
        "source_commit": decision["factor_base_source_commit"],
        "verifier_commit": decision["verifier_commit"],
        "decision_binding": {
            "decision_id": "DEC-20261007-111111",
            "decision_path": str(predecessor_decision),
            "decision_commit": "a" * 40,
            "decision_sha256": "c" * 64,
            "protocol_repository_path": str(predecessor_repository),
        },
        "wrapper": {"binary_sha256": "d" * 64},
        "producer": {
            "binary_sha256": decision["producer_binary_sha256"],
            "argv": ["producer"], "started_sequence": 1, "completed_sequence": 2,
        },
        "verifier": {
            "binary_sha256": decision["verifier_binary_sha256"],
            "argv": ["verifier"], "started_sequence": 3, "completed_sequence": 4,
        },
        "dependency_audit": {
            "audit_output_sha256": "e" * 64,
            "verifier_crypto_lib_found": False,
            "shared_implementation_components": [],
        },
        "producer_artifacts_before": [],
        "producer_artifacts_after": [],
        "agreement_sha256": "f" * 64,
        "agreement_path": "independent-agreement.json",
        "overall_status": "PASS",
    }
    inventory = [
        {"path": path, "byte_length": 0, "sha256": "1" * 64}
        for path in checker.ROLE1_REQUIRED_PATHS
    ]
    return {
        "schema": "p192-wcm-role1-predecessor-binding-v1",
        "run_id": predecessor.name,
        "run_dir": str(predecessor),
        "decision_path": receipt["decision_binding"]["decision_path"],
        "decision_commit": receipt["decision_binding"]["decision_commit"],
        "archive_commit": "b" * 40,
        "decision_sha256": receipt["decision_binding"]["decision_sha256"],
        "protocol_commit": receipt["protocol_commit"],
        "source_commit": receipt["source_commit"],
        "verifier_commit": receipt["verifier_commit"],
        "receipt_sha256": "2" * 64,
        "receipt": receipt,
        "artifact_inventory": inventory,
        "artifact_tree_sha256": checker._artifact_inventory_digest(inventory),
    }


def _synthetic_predecessor_repository_custody(decision: dict) -> dict:
    repository = Path(decision["paths"]["predecessor_repository_path"])
    profiles = decision["selective_worktree_profiles"]

    def identity(path: Path, inode: int, *, executable: bool = False) -> dict:
        return {
            "path": str(path), "device": "1", "inode": str(inode),
            "mode": "100755" if executable else "100644", "link_count": 1,
            "byte_length": 1, "sha256": f"{inode:064x}",
        }

    def receipt(phase: str, head: str, profile: dict, launch: bool) -> dict:
        selected = [{
            "path": "ledger/decisions/DEC-20261007-111111.yaml",
            "device": "1", "inode": "10", "mode": "100644",
            "link_count": 1, "byte_length": 1, "sha256": "a" * 64,
        }]
        objects = [
            {
                "object_id": head, "kind": "commit", "byte_length": 1,
                "sha256": "b" * 64,
            },
            {
                "object_id": "c" * 40, "kind": "tree", "byte_length": 1,
                "sha256": "d" * 64,
            },
        ]
        return {
            "schema": "p192-wcm-sealed-repository-custody-v1",
            "phase": phase, "repository_path": str(repository),
            "repository_identity": {
                "path": str(repository), "device": "1", "inode": "1",
            },
            "head_commit": head, "profile": copy.deepcopy(profile),
            "profile_sha256": checker._custody_digest(
                b"P192-WCM-SEALED-PROFILE-v1\0", profile,
            ),
            "custody_checker_relative_path": (
                "research/p192-weighted-cm-20261007-v2-role2-box0-interface/"
                "check_role2_box0_interface.py"
            ),
            "custody_checker_object_id": "c" * 40,
            "custody_checker_sha256": "d" * 64,
            "git_index_identity": identity(repository / ".git/index", 2),
            "git_config_identity": identity(repository / ".git/config", 3),
            "git_objects_directory_identity": {
                "path": str(repository / ".git/objects"),
                "device": "1", "inode": "4",
            },
            "head_entry_map_sha256": "e" * 64,
            "index_entry_map_sha256": "f" * 64,
            "selected_worktree_identities": selected,
            "selected_worktree_sha256": checker._custody_digest(
                b"P192-WCM-SEALED-SELECTED-WORKTREE-v1\0", selected,
            ),
            "admitted_git_objects": objects,
            "admitted_git_objects_sha256": checker._custody_digest(
                b"P192-WCM-SEALED-ADMITTED-GIT-OBJECTS-v1\0", objects,
            ),
            "omitted_leaf_payload_scope": (
                "ordinary_omitted_blobs_and_gitlink_targets_not_consulted"
            ),
            "inode_custody_scope": "original_supervised_workspace_only",
            "exclusive_workspace_boundary": (
                "trusted_local_host_exclusive_workspace_no_concurrent_mutator"
            ),
            "role1_launch_performed": launch, "overall_status": "PASS",
        }

    pre = receipt(
        "pre_role1_execution", decision["predecessor_role1"]["decision_commit"],
        profiles["predecessor_pre_execution"], False,
    )
    terminal = receipt(
        "terminal_role1_archive", decision["predecessor_role1"]["archive_commit"],
        profiles["predecessor"], True,
    )
    retained_path = checker._role1_pre_execution_retained_path(
        repository, decision["predecessor_run_id"],
    )
    return {
        "schema": "p192-wcm-role1-predecessor-repository-custody-v1",
        "pre_execution_receipt_path": str(
            repository / checker._role1_pre_execution_custody_relative(
                decision["predecessor_run_id"],
            )
        ),
        "pre_execution_retained_path": str(retained_path),
        "pre_execution_retained_identity": identity(retained_path, 20),
        "pre_execution_staging_parent_identity": {
            "path": str(retained_path.parent), "device": "1", "inode": "21",
            "uid": str(os.geteuid()), "mode": "0700",
        },
        "pre_execution_receipt_sha256": checker.sha256_bytes(
            checker.canonical_json_bytes(pre)
        ),
        "pre_execution_receipt": pre,
        "terminal_archive_receipt_sha256": checker.sha256_bytes(
            checker.canonical_json_bytes(terminal)
        ),
        "terminal_archive_receipt": terminal,
        "chronology": (
            "sealed_D1_then_pre_receipt_then_Role1_then_direct_A1_then_"
            "terminal_receipt_then_D2"
        ),
        "launch_handoff_trust_boundary": (
            "trusted_local_host_exclusive_workspace_between_pre_receipt_"
            "and_Role1_launch"
        ),
        "overall_status": "PASS",
    }


def _synthetic_build_admission(
    decision: dict,
    *,
    cargo: Path = Path("/build/toolchain/cargo"),
    rustc: Path = Path("/build/toolchain/rustc"),
    cargo_home: Path = Path("/build/cargo-home"),
    target_dir: Path = Path("/build/verifier-target"),
    metadata_bytes: bytes = b"{}",
    metadata_root_id: str = "verifier 0.1.0 (path+file:///src/verifier)",
    metadata_targets: list[dict] | None = None,
    metadata_resolve: object = None,
    real_identities: bool = False,
) -> dict:
    package = Path(decision["paths"]["verifier_package_path"])
    if metadata_targets is None:
        metadata_targets = [{
            "name": "p192_weighted_cm_verify", "kind": ["bin"],
            "crate_types": ["bin"], "src_path": str(package / "src/main.rs"),
            "edition": "2021", "required_features": [],
        }]

    def tool_identity(path: Path, inode: int) -> dict:
        if real_identities:
            return checker._file_identity(path)
        return {
            "path": str(path), "device": "1", "inode": str(inode),
            "mode": "100755", "link_count": 1, "byte_length": 1,
            "sha256": f"{inode:064x}",
        }

    directories = checker._cargo_config_search_directories(package, cargo_home)
    if real_identities:
        directory_identities = [checker._directory_identity(path) for path in directories]
    else:
        directory_identities = [
            {"path": str(path), "device": "1", "inode": str(100 + index)}
            for index, path in enumerate(directories)
        ]
    dep_info_path = target_dir / "release/p192_weighted_cm_verify.d"
    selected_source = package / "src/main.rs"
    if real_identities:
        _write_bytes(
            dep_info_path,
            f"{target_dir / 'release/p192_weighted_cm_verify'}: {selected_source}\n".encode(),
        )
        dep_info_identity = checker._file_identity(dep_info_path)
        dep_info_inputs = [checker._file_identity(selected_source)]
    else:
        dep_info_identity = {
            "path": str(dep_info_path), "device": "1", "inode": "3",
            "mode": "100644", "link_count": 1, "byte_length": 1,
            "sha256": "3" * 64,
        }
        dep_info_inputs = [{
            "path": str(selected_source), "device": "1", "inode": "4",
            "mode": "100644", "link_count": 1, "byte_length": 1,
            "sha256": "4" * 64,
        }]
    return {
        "schema": "p192-wcm-verifier-build-admission-v1",
        "trust_model": checker.VERIFIER_BUILD_TRUST_MODEL,
        "cargo_identity": tool_identity(cargo, 1),
        "rustc_identity": tool_identity(rustc, 2),
        "cwd": str(package), "cargo_home": str(cargo_home),
        "target_dir": str(target_dir),
        "build_argv": [
            str(cargo), "build", "--frozen", "--locked", "--offline", "--release",
            "--manifest-path", str(package / "Cargo.toml"), "--bin",
            "p192_weighted_cm_verify", "--target-dir", str(target_dir),
        ],
        "metadata_argv": [
            str(cargo), "metadata", "--frozen", "--locked", "--offline",
            "--format-version", "1", "--manifest-path", str(package / "Cargo.toml"),
        ],
        "metadata_execution_policy": copy.deepcopy(
            checker.VERIFIER_METADATA_EXECUTION_POLICY
        ),
        "environment": {
            "CARGO_HOME": str(cargo_home), "CARGO_INCREMENTAL": "0",
            "CARGO_NET_OFFLINE": "true", "CARGO_TARGET_DIR": str(target_dir),
            "LC_ALL": "C", "P192_WCM_PROTOCOL_COMMIT": decision["protocol_commit"],
            "P192_WCM_VERIFIER_COMMIT": decision["verifier_commit"],
            "RUSTC": str(rustc),
        },
        "forbidden_environment_prefixes_absent": checker.VERIFIER_BUILD_FORBIDDEN_ENV_PREFIXES,
        "selected_target": {
            "kind": "bin", "name": "p192_weighted_cm_verify",
            "src_path": str(package / "src/main.rs"), "features": [],
        },
        "config_candidate_paths": [
            str(path) for path in checker._cargo_config_candidate_paths(package, cargo_home)
        ],
        "config_search_directory_identities": directory_identities,
        "cargo_metadata_byte_length": len(metadata_bytes),
        "cargo_metadata_sha256": checker.sha256_bytes(metadata_bytes),
        "cargo_metadata_root_package_id": metadata_root_id,
        "cargo_metadata_root_targets": metadata_targets,
        "cargo_metadata_resolve_sha256": checker.sha256_bytes(
            checker.canonical_json_bytes(metadata_resolve)
        ),
        "selected_bin_dep_info": {
            "identity": dep_info_identity,
            "local_inputs": dep_info_inputs,
        },
        "build_script": {
            "mode": "absent", "path": None, "sha256": None,
            "allowed_directive_prefixes": [], "observed_directives": [],
        },
    }


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
        "predecessor_repository_path": "/predecessor-protocol",
        "predecessor_dir": "/predecessor-protocol/experiments/EXP-SCURVE-1a8daf/runs/RUN-SCURVE-111111",
        "factor_base_json": "/predecessor-protocol/experiments/EXP-SCURVE-1a8daf/runs/RUN-SCURVE-111111/factor-base.json",
        "run_dir": "/protocol/experiments/EXP-SCURVE-1a8daf/runs/RUN-SCURVE-222222",
        "control_dir": "/protocol/experiments/EXP-SCURVE-1a8daf/controls/RUN-SCURVE-222222-restart",
        "audit_file": "/protocol/experiments/EXP-SCURVE-1a8daf/runs/RUN-SCURVE-222222/dependency-audit.json",
    }
    value = {
        "schema": "p192-wcm-role2-box0-dispatch-authorization-v1",
        "decision_id": "DEC-20261007-abcdef",
        "approved_by": "Coordinator",
        "created_at_utc": "2026-10-07T12:00:00Z",
        "execution_authorized": True,
        "experiment_id": "EXP-SCURVE-1a8daf",
        "protocol_version": 2,
        "interface_revision": 3,
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
        "producer_binary_byte_length": 16,
        "verifier_binary_byte_length": 16,
        "supervisor_binary_byte_length": 18,
        "execution_controls": copy.deepcopy(checker.EXECUTION_CONTROLS),
        "predecessor_run_id": "RUN-SCURVE-111111",
        "predecessor_artifacts": {name: "9" * 64 for name in checker.PREDECESSOR_PATHS},
        "protected_protocol_blobs": {
            name: checker.sha256_path(path)
            for name, path in checker.PROTECTED_PROTOCOL_PATHS.items()
        },
        "paths": paths,
    }
    value["verifier_build_admission"] = _synthetic_build_admission(value)
    value["predecessor_role1"] = _synthetic_role1_binding(value)
    value["selective_worktree_profiles"] = checker.selective_worktree_profiles(value)
    value["predecessor_repository_custody"] = (
        _synthetic_predecessor_repository_custody(value)
    )
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
        ["git", "-c", "core.hooksPath=/dev/null", "-C", str(repository),
         *arguments], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
    )
    return result.stdout.decode("utf-8").strip()


def _git_input(repository: Path, arguments: list[str], payload: bytes) -> bytes:
    environment = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Role2 Test", "GIT_AUTHOR_EMAIL": "role2@example.invalid",
        "GIT_COMMITTER_NAME": "Role2 Test", "GIT_COMMITTER_EMAIL": "role2@example.invalid",
    }
    result = subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "-C", str(repository),
         *arguments], input=payload, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
    )
    return result.stdout


def _checker_probe(source: str, *arguments: object) -> subprocess.CompletedProcess[str]:
    loader = (
        "import importlib.util,json,sys;from pathlib import Path;"
        "s=importlib.util.spec_from_file_location('probe_checker',Path(sys.argv[1]));"
        "c=importlib.util.module_from_spec(s);s.loader.exec_module(c);"
    )
    return subprocess.run(
        [sys.executable, "-c", loader + source, str(CHECKER_PATH),
         *(str(argument) for argument in arguments)],
        check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, timeout=8,
    )


def _init_repository(repository: Path) -> None:
    repository.mkdir(parents=True)
    _git(repository, "init", "-q")
    _write_bytes(repository / ".git/config", checker.MINIMAL_STANDALONE_GIT_CONFIG)
    exclude = repository / ".git/info/exclude"
    if exclude.exists():
        exclude.unlink()


def _commit_all(repository: Path, message: str) -> str:
    _git(repository, "add", "-A")
    _git(repository, "commit", "-q", "-m", message)
    return _git(repository, "rev-parse", "HEAD")


def _strip_index_extensions(repository: Path) -> None:
    """Canonicalize a Git index to v3 entries plus its checksum only."""
    path = repository / ".git/index"
    raw = path.read_bytes()
    assert raw[:4] == b"DIRC"
    count = int.from_bytes(raw[8:12], "big")
    offset = 12
    for _ in range(count):
        entry_start = offset
        assert offset + 62 <= len(raw) - 20
        flags = int.from_bytes(raw[offset + 60:offset + 62], "big")
        offset += 62
        if flags & 0x4000:
            offset += 2
        nul = raw.index(b"\0", offset, len(raw) - 20)
        entry_length = nul + 1 - entry_start
        offset = entry_start + ((entry_length + 7) & ~7)
    body = bytearray(raw[:offset])
    body[4:8] = (3).to_bytes(4, "big")
    path.write_bytes(bytes(body) + hashlib.sha1(body).digest())


def _seal_selective_worktree(repository: Path, profile: dict) -> None:
    """Trusted fixture preparation for the sealed full-index H/S state."""
    output = subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "-C", str(repository),
         "ls-tree", "-r", "-z", "HEAD"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout
    head: dict[str, tuple[str, str]] = {}
    for record in (item for item in output.split(b"\0") if item):
        header, raw_path = record.split(b"\t", 1)
        mode, _kind, object_id = header.decode("ascii").split(" ")
        head[raw_path.decode("utf-8")] = (mode, object_id)
    profile_errors: list[str] = []
    selected = checker._sparse_selected_paths(head, profile, profile_errors)
    assert profile_errors == [] and selected is not None
    omitted = sorted(set(head) - selected)
    if selected:
        _git(repository, "update-index", "--no-skip-worktree", "--", *sorted(selected))
    if omitted:
        _git(repository, "update-index", "--skip-worktree", "--", *omitted)
    for relative in omitted:
        path = repository / relative
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
    # Drop now-empty directories outside the selected parent topology.
    expected_directories: set[Path] = {repository}
    for relative in selected:
        parent = (repository / relative).parent
        while parent != repository:
            expected_directories.add(parent)
            parent = parent.parent
    for directory, directories, _files in os.walk(repository, topdown=False):
        current = Path(directory)
        if current == repository or repository / ".git" in (current, *current.parents):
            continue
        if current not in expected_directories and not any(current.iterdir()):
            current.rmdir()
    for forbidden in (
        repository / ".git/info/exclude",
        repository / ".git/info/attributes",
        repository / ".git/info/sparse-checkout",
        repository / ".git/config.worktree",
    ):
        if forbidden.exists() or forbidden.is_symlink():
            forbidden.unlink()
    _write_bytes(repository / ".git/config", checker.MINIMAL_STANDALONE_GIT_CONFIG)
    _strip_index_extensions(repository)


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
    manifest = f"[workspace]\n[package]\nname='{role}'\nversion='0.1.0'\n"
    if role == "verifier":
        manifest += (
            "autobins=false\nautoexamples=false\nautotests=false\n"
            "autobenches=false\n\n[[bin]]\nname='p192_weighted_cm_verify'\n"
            "path='src/main.rs'\n"
        )
    _write_bytes(package / "Cargo.toml", manifest.encode())
    _write_bytes(package / "src/lib.rs", f"pub fn {role}() {{}}\n".encode())
    if role == "verifier":
        _write_bytes(package / "src/main.rs", b"fn main() {}\n")
    _write_bytes(
        package / "Cargo.lock",
        f'version = 3\n\n[[package]]\nname = "{role}"\nversion = "0.1.0"\n'.encode(),
    )
    _write_bytes(repository / "Cargo.lock", f"# {role} lock\n".encode())
    for prefix in checker.SOURCE_SPARSE_PREFIXES:
        _write_bytes(
            repository / prefix / ".sealed-profile-sentinel",
            f"{role}:{prefix}\n".encode(),
        )
    commit = _commit_all(repository, f"{role} source")
    return repository, package, commit


def _committed_decision_fixture(base: Path) -> tuple[Path, dict, dict]:
    protocol = base / "protocol"
    _init_repository(protocol)
    for relative in checker.PROTECTED_PROTOCOL_RELATIVE_PATHS.values():
        _write_bytes(protocol / relative, (ROOT / relative).read_bytes())
    protocol_commit = _commit_all(protocol, "frozen protocol")

    # The predecessor archive is a distinct standalone checkout on the other
    # direct-child fork from the same self-hashed protocol commit P.
    predecessor_repository = base / "predecessor-repository"
    shutil.copytree(protocol, predecessor_repository)
    predecessor_decision_path = (
        predecessor_repository / "ledger/decisions/DEC-20261007-111111.yaml"
    )
    _write_bytes(
        predecessor_decision_path,
        b"decision_id: DEC-20261007-111111\noverall_status: PASS\n",
    )
    predecessor_decision_commit = _commit_all(
        predecessor_repository, "fresh Role1 decision",
    )
    predecessor_pre_profile = checker._role1_pre_execution_profile(
        predecessor_decision_path.relative_to(predecessor_repository).as_posix(),
        "RUN-SCURVE-111111",
    )
    _seal_selective_worktree(
        predecessor_repository, predecessor_pre_profile,
    )
    pre_custody_errors: list[str] = []
    predecessor_pre_receipt = checker._sealed_repository_custody_receipt(
        predecessor_repository, predecessor_decision_commit,
        predecessor_pre_profile, "pre_role1_execution", pre_custody_errors,
    )
    assert pre_custody_errors == [] and predecessor_pre_receipt is not None
    predecessor_pre_receipt_path = (
        predecessor_repository
        / checker._role1_pre_execution_custody_relative(
            "RUN-SCURVE-111111",
        )
    )
    predecessor_pre_retained_path = checker._role1_pre_execution_retained_path(
        predecessor_repository, "RUN-SCURVE-111111",
    )
    predecessor_pre_retained_path.parent.mkdir(mode=0o700)
    predecessor_pre_retained_path.parent.chmod(0o700)
    _canonical(predecessor_pre_retained_path, predecessor_pre_receipt)

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

    predecessor = (
        predecessor_repository / checker.RUNS_RELATIVE_DIRECTORY
        / "RUN-SCURVE-111111"
    )
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
    for relative in checker.ROLE1_REQUIRED_PATHS:
        path = predecessor / relative
        if path.exists():
            continue
        if path.suffix in {".json", ".yaml"}:
            _canonical(path, {})
        else:
            _write_bytes(path, f"synthetic Role1 {relative}\n".encode())
    # The Role-1 checkout remains exactly clean while it runs.  Only after the
    # run completes are the retained pre-launch bytes copied into their fixed
    # archive sibling path for the direct A1 commit.
    _write_bytes(
        predecessor_pre_receipt_path,
        predecessor_pre_retained_path.read_bytes(),
    )
    predecessor_archive_commit = _commit_all(
        predecessor_repository, "archive exact Role1 run",
    )

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
        "producer_binary_byte_length": binaries["producer"].stat().st_size,
        "verifier_binary_byte_length": binaries["verifier"].stat().st_size,
        "supervisor_binary_byte_length": binaries["supervisor"].stat().st_size,
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
        "predecessor_repository_path": str(predecessor_repository),
        "predecessor_dir": str(predecessor),
        "factor_base_json": str(predecessor / "factor-base.json"),
        "run_dir": str(protocol / checker.RUNS_RELATIVE_DIRECTORY / "RUN-SCURVE-222222"),
        "control_dir": str(protocol / checker.CONTROLS_RELATIVE_DIRECTORY / "RUN-SCURVE-222222-restart"),
        "audit_file": str(protocol / checker.RUNS_RELATIVE_DIRECTORY / "RUN-SCURVE-222222/dependency-audit.json"),
    }
    tool_dir = base / "trusted-toolchain"
    cargo = tool_dir / "cargo"
    rustc = tool_dir / "rustc"
    cargo_home = base / "cargo-home"
    target_dir = base / "verifier-build-target"
    cargo_home.mkdir()
    target_dir.mkdir()
    root_id = f"path+file://{verifier_package}#verifier@0.1.0"
    targets = [
        {
            "name": "p192_weighted_cm_verify", "kind": ["bin"],
            "crate_types": ["bin"], "src_path": str(verifier_package / "src/main.rs"),
            "edition": "2015", "required_features": [],
        },
        {
            "name": "verifier", "kind": ["lib"], "crate_types": ["lib"],
            "src_path": str(verifier_package / "src/lib.rs"),
            "edition": "2015", "required_features": [],
        },
    ]
    resolve = {
        "root": root_id,
        "nodes": [{
            "id": root_id, "dependencies": [], "deps": [], "features": [],
        }],
    }
    metadata = {
        "packages": [{
            "name": "verifier", "version": "0.1.0", "id": root_id,
            "license": None, "license_file": None, "description": None,
            "source": None, "dependencies": [], "targets": [
                {
                    "kind": row["kind"], "crate_types": row["crate_types"],
                    "name": row["name"], "src_path": row["src_path"],
                    "edition": row["edition"], "doc": True,
                    "doctest": row["kind"] == ["lib"], "test": True,
                }
                for row in targets
            ],
            "features": {}, "manifest_path": str(verifier_package / "Cargo.toml"),
            "metadata": None, "publish": None, "authors": [], "categories": [],
            "keywords": [], "readme": None, "repository": None,
            "homepage": None, "documentation": None, "edition": "2015",
            "links": None, "default_run": None, "rust_version": None,
        }],
        "workspace_members": [root_id], "workspace_default_members": [root_id],
        "resolve": resolve, "target_directory": str(target_dir), "version": 1,
        "workspace_root": str(verifier_package), "metadata": None,
    }
    metadata_bytes = json.dumps(metadata, separators=(",", ":"), sort_keys=True).encode()
    _write_bytes(
        cargo,
        b"#!/bin/sh\nprintf '%s' '" + metadata_bytes + b"'\n",
        executable=True,
    )
    _write_bytes(rustc, b"#!/bin/sh\nexit 0\n", executable=True)
    decision["verifier_build_admission"] = _synthetic_build_admission(
        decision, cargo=cargo, rustc=rustc, cargo_home=cargo_home,
        target_dir=target_dir, metadata_bytes=metadata_bytes,
        metadata_root_id=root_id, metadata_targets=targets,
        metadata_resolve=resolve, real_identities=True,
    )
    decision["predecessor_role1"] = _synthetic_role1_binding(decision)
    decision["predecessor_role1"].update({
        "decision_path": str(predecessor_decision_path),
        "decision_commit": predecessor_decision_commit,
        "archive_commit": predecessor_archive_commit,
        "decision_sha256": checker.sha256_path(predecessor_decision_path),
        "protocol_commit": protocol_commit,
    })
    predecessor_receipt = decision["predecessor_role1"]["receipt"]
    predecessor_receipt["protocol_commit"] = protocol_commit
    predecessor_receipt["decision_binding"].update({
        "decision_path": str(predecessor_decision_path),
        "decision_commit": predecessor_decision_commit,
        "decision_sha256": checker.sha256_path(predecessor_decision_path),
        "protocol_repository_path": str(predecessor_repository),
    })
    decision["selective_worktree_profiles"] = checker.selective_worktree_profiles(
        decision,
    )
    _seal_selective_worktree(
        predecessor_repository,
        decision["selective_worktree_profiles"]["predecessor"],
    )
    terminal_custody_errors: list[str] = []
    predecessor_terminal_receipt = checker._sealed_repository_custody_receipt(
        predecessor_repository, predecessor_archive_commit,
        decision["selective_worktree_profiles"]["predecessor"],
        "terminal_role1_archive", terminal_custody_errors,
    )
    assert terminal_custody_errors == [] and predecessor_terminal_receipt is not None
    decision["predecessor_repository_custody"] = {
        "schema": "p192-wcm-role1-predecessor-repository-custody-v1",
        "pre_execution_receipt_path": str(predecessor_pre_receipt_path),
        "pre_execution_retained_path": str(predecessor_pre_retained_path),
        "pre_execution_retained_identity": checker._file_identity(
            predecessor_pre_retained_path,
        ),
        "pre_execution_staging_parent_identity": (
            checker._owned_private_directory_identity(
                predecessor_pre_retained_path.parent,
            )
        ),
        "pre_execution_receipt_sha256": checker.sha256_path(
            predecessor_pre_receipt_path,
        ),
        "pre_execution_receipt": predecessor_pre_receipt,
        "terminal_archive_receipt_sha256": checker.sha256_bytes(
            checker.canonical_json_bytes(predecessor_terminal_receipt)
        ),
        "terminal_archive_receipt": predecessor_terminal_receipt,
        "chronology": (
            "sealed_D1_then_pre_receipt_then_Role1_then_direct_A1_then_"
            "terminal_receipt_then_D2"
        ),
        "launch_handoff_trust_boundary": (
            "trusted_local_host_exclusive_workspace_between_pre_receipt_"
            "and_Role1_launch"
        ),
        "overall_status": "PASS",
    }
    decision.update(checker.resolved_argv(decision))
    decision_path = Path(decision["paths"]["decision_json"])
    _canonical(decision_path, decision)
    decision_commit = _commit_all(protocol, "fresh Role2 decision")
    for repository in (producer_repo, verifier_repo, supervisor_repo):
        _seal_selective_worktree(
            repository, decision["selective_worktree_profiles"]["source"],
        )
    _seal_selective_worktree(
        protocol, decision["selective_worktree_profiles"]["protocol"],
    )
    custody = checker._decision_custody(decision, decision_path, decision_path.read_bytes(), decision_commit)
    return decision_path, decision, custody


def _fixture_dispatch(
    decision_path: Path, phase: str, run_dir: Path | None = None,
) -> tuple[dict | None, dict | None, list[str]]:
    """Stub only the unrelated Role-1 replay in synthetic temp-Git fixtures."""
    try:
        decision = checker.decode_canonical_json(decision_path.read_bytes())
    except ValueError:
        return checker.validate_dispatch_decision(decision_path, phase, run_dir)
    original = checker._role1_predecessor_binding

    def synthetic_binding(
        _predecessor: Path, _repository: Path, _errors: list[str],
    ) -> dict:
        return copy.deepcopy(decision["predecessor_role1"])

    checker._role1_predecessor_binding = synthetic_binding
    try:
        return checker.validate_dispatch_decision(decision_path, phase, run_dir)
    finally:
        checker._role1_predecessor_binding = original


def _artifact_for(base: Path, relative: str) -> dict:
    return checker._artifact_record(base / relative, relative)


def _replace_success_with_failure(
    run_dir: Path,
    decision: dict,
    custody: dict,
    failed_phase: str,
    failure_reason: str,
) -> dict:
    control_dir = Path(decision["paths"]["control_dir"])
    phase_names = list(checker.FAILURE_PHASE_ARTIFACTS)
    failed_index = phase_names.index(failed_phase)
    for index, phase in enumerate(phase_names):
        if index > failed_index:
            for relative in checker.FAILURE_PHASE_ARTIFACTS[phase]:
                path = run_dir / relative
                if os.path.lexists(path):
                    path.unlink()
    for relative in ("manifest.yaml", checker.TERMINAL_CUSTODY_PATH):
        path = run_dir / relative
        if os.path.lexists(path):
            path.unlink()
    completed = [
        _artifact_for(run_dir, relative)
        for relative in checker.FAILURE_COMPLETION_ORDER
        if checker._schema_valid_completed_artifact(run_dir, relative, decision)
    ]
    raw = {
        "schema": "p192-wcm-role2-box0-failure-v1",
        "experiment_id": "EXP-SCURVE-1a8daf", "run_id": decision["run_id"],
        "stage": "P192-WCM-BOX0", "decision_custody": custody,
        "protocol_commit": decision["protocol_commit"],
        "factor_base_source_commit": decision["factor_base_source_commit"],
        "producer_commit": decision["producer_commit"],
        "verifier_commit": decision["verifier_commit"],
        "supervisor_commit": decision["supervisor_commit"],
        "run_dir": str(run_dir), "control_dir": str(control_dir),
        "control_state": "retained", "control_retained": True,
        "control_created_before_failure": True,
        "invalid_count": 0, "unresolved_count": 0,
        "failed_phase": failed_phase, "failure_reason": failure_reason,
        "completed_artifacts": completed,
        "scientific_result": False, "scientific_results": [],
        "status": "INCOMPLETE" if failure_reason == "incomplete_child_artifact" else "FAIL",
    }
    raw["terminal_failure_custody"] = {
        "custody_check_id": "post_directory_creation_terminal_failure_v1",
        "inode_custody_scope": "original_supervised_workspace_only",
        "run_entries_before_failure_record": [
            record for record in checker._directory_custody_entries(run_dir)
            if record["path"] != "raw-result.json"
        ],
        "control_directory_before_children": checker._directory_identity(control_dir),
        "control_directory_terminal": checker._directory_identity(control_dir),
        "control_entries": checker._directory_custody_entries(control_dir),
        "failure_record_excluded_from_own_inventory": True,
        "pass_manifest_transition": "not_reached",
        "provisional_pass_manifest": None,
        "provisional_success_raw_result": None,
        "stale_pass_manifest_present_before_finalization": False,
        "stale_pass_manifest_removed": False,
        "pass_manifest_absent_after_finalization": True,
        "in_transaction_control_cleanup_performed": False,
    }
    _canonical(run_dir / "raw-result.json", raw)
    return raw


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
    control_dir = Path(decision["paths"]["control_dir"])
    control_dir.mkdir(parents=True)
    for relative in checker.PRODUCER_PATHS:
        shutil.copyfile(run_dir / relative, control_dir / relative)
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
        "control_dir": str(control_dir),
        "fault_state_artifacts": [
            _artifact_for(run_dir, path) for path in checker.CONTROL_CHECKPOINT_PATHS
        ],
        "injected_state_artifacts": [
            {
                "path": path,
                "byte_length": len((run_dir / path).read_bytes())
                + (len(bytes.fromhex("503139322d57434d2d554e434f4d4d49545445442d5355464649582d763100")) if path in checker.APPEND_PATHS else 0),
                "sha256": checker.sha256_bytes(
                    (run_dir / path).read_bytes()
                    + (bytes.fromhex("503139322d57434d2d554e434f4d4d49545445442d5355464649582d763100") if path in checker.APPEND_PATHS else b"")
                ),
            }
            for path in checker.CONTROL_CHECKPOINT_PATHS
        ],
        "resumed_control_artifacts": [_artifact_for(control_dir, path) for path in checker.PRODUCER_PATHS],
        "control_directory_terminal": checker._directory_identity(control_dir),
        "control_retained_after_terminal_validation": True,
        "control_cleanup_authority": "out_of_band_after_terminal_validation_and_archival_only",
        "comparisons": [
            {"field": path, "fresh_sha256": checker.sha256_path(run_dir / path),
             "resumed_sha256": checker.sha256_path(control_dir / path), "equal": True}
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
    source_build_rows: dict[str, list[dict]] = {}
    for role in ("producer", "verifier", "supervisor"):
        package = Path(decision["paths"][f"{role}_package_path"])
        repository = Path(decision["paths"][f"{role}_repository_path"])
        source_rows[role] = checker._collect_rust_hash_rows(package)
        source_errors: list[str] = []
        rows = checker._source_build_input_rows(
            repository, package, decision[f"{role}_commit"], role, source_errors,
        )
        assert source_errors == [] and rows is not None
        source_build_rows[role] = rows
    audit = {
        "schema": "p192-wcm-role2-dependency-audit-v1",
        "git_execution_policy": copy.deepcopy(checker.GIT_EXECUTION_POLICY),
        "verifier_forbidden_dependency_scan": checker._verifier_dependency_scan_record(decision),
        "verifier_build_custody": checker._verifier_build_custody(decision),
        "identical_source_hashes": [],
        "producer_cargo_lock_path": str(Path(decision["paths"]["producer_package_path"]) / "Cargo.lock"),
        "producer_cargo_lock_sha256": checker.sha256_path(Path(decision["paths"]["producer_package_path"]) / "Cargo.lock"),
        "producer_cargo_toml_sha256": checker.sha256_path(Path(decision["paths"]["producer_package_path"]) / "Cargo.toml"),
        "producer_git": {"git_head": decision["producer_commit"], "git_top_level": decision["paths"]["producer_repository_path"], "package_root": decision["paths"]["producer_package_path"], "worktree_clean": True},
        "producer_rust_sources": source_rows["producer"],
        "producer_executable_before": checker._file_identity(Path(decision["paths"]["producer_bin"])),
        "producer_executable_after": checker._file_identity(Path(decision["paths"]["producer_bin"])),
        "producer_source_build_inputs_before": source_build_rows["producer"],
        "producer_source_build_inputs_after": source_build_rows["producer"],
        "producer_source_build_tree_sha256_before": checker._source_input_digest(source_build_rows["producer"]),
        "producer_source_build_tree_sha256_after": checker._source_input_digest(source_build_rows["producer"]),
        "source_clone_screen": checker.compute_source_clone_screen(
            Path(decision["paths"]["producer_package_path"]),
            Path(decision["paths"]["verifier_package_path"]),
        ),
        "shared_implementation_components": [],
        "supervisor_cargo_lock_path": str(Path(decision["paths"]["supervisor_package_path"]) / "Cargo.lock"),
        "supervisor_cargo_lock_sha256": checker.sha256_path(Path(decision["paths"]["supervisor_package_path"]) / "Cargo.lock"),
        "supervisor_cargo_toml_sha256": checker.sha256_path(Path(decision["paths"]["supervisor_package_path"]) / "Cargo.toml"),
        "supervisor_curve_arithmetic_found": False,
        "supervisor_git": {"git_head": decision["supervisor_commit"], "git_top_level": decision["paths"]["supervisor_repository_path"], "package_root": decision["paths"]["supervisor_package_path"], "worktree_clean": True},
        "supervisor_rust_sources": source_rows["supervisor"],
        "supervisor_executable_before": checker._file_identity(Path(decision["paths"]["supervisor_bin"])),
        "supervisor_executable_after": checker._file_identity(Path(decision["paths"]["supervisor_bin"])),
        "supervisor_source_build_inputs_before": source_build_rows["supervisor"],
        "supervisor_source_build_inputs_after": source_build_rows["supervisor"],
        "supervisor_source_build_tree_sha256_before": checker._source_input_digest(source_build_rows["supervisor"]),
        "supervisor_source_build_tree_sha256_after": checker._source_input_digest(source_build_rows["supervisor"]),
        "verifier_cargo_lock_path": str(Path(decision["paths"]["verifier_package_path"]) / "Cargo.lock"),
        "verifier_cargo_lock_sha256": checker.sha256_path(Path(decision["paths"]["verifier_package_path"]) / "Cargo.lock"),
        "verifier_cargo_toml_sha256": checker.sha256_path(Path(decision["paths"]["verifier_package_path"]) / "Cargo.toml"),
        "verifier_crypto_lib_found": False,
        "verifier_git": {"git_head": decision["verifier_commit"], "git_top_level": decision["paths"]["verifier_repository_path"], "package_root": decision["paths"]["verifier_package_path"], "worktree_clean": True},
        "verifier_rust_sources": source_rows["verifier"],
        "verifier_executable_before": checker._file_identity(Path(decision["paths"]["verifier_bin"])),
        "verifier_executable_after": checker._file_identity(Path(decision["paths"]["verifier_bin"])),
        "verifier_source_build_inputs_before": source_build_rows["verifier"],
        "verifier_source_build_inputs_after": source_build_rows["verifier"],
        "verifier_source_build_tree_sha256_before": checker._source_input_digest(source_build_rows["verifier"]),
        "verifier_source_build_tree_sha256_after": checker._source_input_digest(source_build_rows["verifier"]),
    }
    _canonical(run_dir / "dependency-audit.json", audit)
    payloads = {child["role"]: b"" for child in checker.SUPERVISOR_CHILDREN}
    _write_bytes(run_dir / "stdout.log", _framed_log("stdout", payloads))
    _write_bytes(run_dir / "stderr.log", _framed_log("stderr", payloads))
    predecessor_inventory = [_artifact_for(predecessor, path) for path in checker.PREDECESSOR_PATHS]
    producer_inventory = [_artifact_for(run_dir, path) for path in checker.PRODUCER_PATHS]
    predecessor_fd_snapshots = [
        checker._file_identity(predecessor / path, path)
        for path in checker.PREDECESSOR_PATHS
    ]
    predecessor_snapshot_sha256 = checker._identity_bundle_digest(predecessor_fd_snapshots)
    binary_identities = {
        role: checker._file_identity(Path(decision["paths"][f"{role}_bin"]))
        for role in ("producer", "verifier", "supervisor")
    }
    sealed_paths = checker.SEALED_EXEC_FD_PATHS
    children = []
    for role, binary_hash, commit, argv, exit_code in (
        ("canonical_producer", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_fresh_argv"], 0),
        ("checkpoint_fault_control", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_fault_argv"], 75),
        ("checkpoint_resume_control", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_resume_argv"], 0),
        ("isolated_independent_verifier", decision["verifier_binary_sha256"], decision["verifier_commit"], decision["independent_verifier_argv"], 0),
    ):
        image_role = "verifier" if role == "isolated_independent_verifier" else "producer"
        children.append({
            "role": role, "binary_sha256": binary_hash, "commit": commit, "argv": argv,
            "sealed_image_id": f"{image_role}-sealed-image-v1",
            "actual_exec_path": sealed_paths[image_role],
            "logical_argv0": decision["paths"][f"{image_role}_bin"],
            "running_image_sha256": binary_hash,
            "source_executable_before_launch": binary_identities[image_role],
            "source_executable_after_launch": binary_identities[image_role],
            "predecessor_snapshot_sha256": predecessor_snapshot_sha256,
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
        "verifier_build_custody": checker._verifier_build_custody(decision),
        "predecessor_artifacts_before": predecessor_inventory,
        "predecessor_artifacts_after": predecessor_inventory,
        "predecessor_retained_fd_snapshots": predecessor_fd_snapshots,
        "producer_artifacts_before_verifier": producer_inventory,
        "producer_artifacts_after_verifier": producer_inventory,
        "run_producer_artifacts_terminal": [
            checker._file_identity(run_dir / path, path) for path in checker.PRODUCER_PATHS
        ],
        "control_producer_artifacts_terminal": [
            checker._file_identity(control_dir / path, path) for path in checker.PRODUCER_PATHS
        ],
        "binary_identities_before": binary_identities,
        "binary_identities_after": binary_identities,
        "source_build_tree_sha256_before": {
            role: checker._source_input_digest(source_build_rows[role])
            for role in ("producer", "verifier", "supervisor")
        },
        "source_build_tree_sha256_after": {
            role: checker._source_input_digest(source_build_rows[role])
            for role in ("producer", "verifier", "supervisor")
        },
        "execution_custody": {
            "supervisor": {
                "raw_argv0": decision["paths"]["supervisor_bin"],
                "current_exe": decision["paths"]["supervisor_bin"],
                "decision_supervisor_path": decision["paths"]["supervisor_bin"],
                "proc_self_exe_sha256": decision["supervisor_binary_sha256"],
                "source_before": binary_identities["supervisor"],
                "source_terminal": binary_identities["supervisor"],
            },
            "sealed_images": [
                {
                    "role": role,
                    "sealed_image_id": f"{role}-sealed-image-v1",
                    "source_path": decision["paths"][f"{role}_bin"],
                    "source_before": binary_identities[role],
                    "source_terminal": binary_identities[role],
                    "opened_once": True,
                    "open_flags": checker.EXECUTION_CONTROLS["child_open_flags"],
                    "memfd_flags": checker.EXECUTION_CONTROLS["child_memfd_flags"],
                    "seals": checker.EXECUTION_CONTROLS["child_memfd_seals"],
                    "memfd_byte_length": binary_identities[role]["byte_length"],
                    "memfd_sha256": binary_identities[role]["sha256"],
                    "launch_path": sealed_paths[role],
                    "logical_argv0": decision["paths"][f"{role}_bin"],
                    "launch_count": 3 if role == "producer" else 1,
                    "source_descriptor_cloexec": True,
                    "target_fd_cloexec_cleared": True,
                }
                for role in ("producer", "verifier")
            ],
            "predecessor_fd_interface": {
                "file_names": checker.PREDECESSOR_PATHS,
                "open_flags": ["O_RDONLY", "O_CLOEXEC", "O_NOFOLLOW"],
                "snapshot_sha256": predecessor_snapshot_sha256,
                "snapshot_strategy": "sealed_memfd_from_once_opened_nofollow_fd",
                "snapshot_images": [
                    {
                        "name": name,
                        "original_before": identity,
                        "original_terminal": identity,
                        "memfd_flags": checker.EXECUTION_CONTROLS["child_memfd_flags"],
                        "seals": checker.EXECUTION_CONTROLS["child_memfd_seals"],
                        "snapshot_byte_length": identity["byte_length"],
                        "snapshot_sha256": identity["sha256"],
                        "retained_fd_path": checker.PREDECESSOR_SNAPSHOT_FD_PATHS[name],
                        "source_descriptor_cloexec": True,
                        "target_fd_cloexec_cleared": True,
                    }
                    for name, identity in zip(
                        checker.PREDECESSOR_PATHS, predecessor_fd_snapshots
                    )
                ],
                "retained_through_terminal": True,
                "original_paths_rechecked_before_each_child": True,
                "original_paths_rechecked_terminally": True,
                "child_reads_from_inherited_fds_only": True,
                "source_descriptors_cloexec": True,
                "child_target_fd_cloexec_cleared": True,
                "handoff_order": [
                    "open_original_nofollow_once", "copy_to_sealed_memfd",
                    "duplicate_to_fixed_child_fd", "clear_target_FD_CLOEXEC",
                    "exec_child", "retain_original_and_sealed_sources_through_terminal",
                ],
                "children": [
                    {
                        "role": item["role"],
                        "snapshot_sha256": predecessor_snapshot_sha256,
                        "inherited_fds": [
                            {"name": name, "fd_path": checker.PREDECESSOR_SNAPSHOT_FD_PATHS[name]}
                            for name in checker.PREDECESSOR_PATHS
                        ],
                        "target_fd_cloexec_cleared": True,
                        "reads_inherited_fds_only": True,
                    }
                    for item in checker.SUPERVISOR_CHILDREN
                ],
            },
        },
        "directory_custody": {
            "identities": [
                checker._directory_identity(Path(decision["paths"]["protocol_repository_path"]) / checker.EXPERIMENT_RELATIVE_DIRECTORY),
                checker._directory_identity(Path(decision["paths"]["protocol_repository_path"]) / checker.RUNS_RELATIVE_DIRECTORY),
                checker._directory_identity(Path(decision["paths"]["protocol_repository_path"]) / checker.CONTROLS_RELATIVE_DIRECTORY),
                checker._directory_identity(run_dir),
                checker._directory_identity(control_dir),
            ],
            "open_flags": ["O_RDONLY", "O_CLOEXEC", "O_DIRECTORY", "O_NOFOLLOW"],
            "opened_once_and_retained": True,
            "exclusive_fd_relative_leaf_creation": True,
            "fd_relative_io_only": True,
            "same_directory_atomic_rename_only": True,
            "path_identity_checked_before_each_child": True,
            "path_identity_checked_terminally": True,
            "fixed_fd_paths": checker.DIRECTORY_FD_PATHS,
            "source_descriptors_cloexec": True,
            "child_target_fd_cloexec_cleared": True,
            "creation_open_retention_order": [
                "open_and_retain_existing_parents", "mkdirat_run_and_control_exclusive",
                "open_created_run_and_control_nofollow", "verify_path_fd_identity",
                "duplicate_to_fixed_child_fds", "clear_target_FD_CLOEXEC",
                "launch_children", "terminal_path_fd_recheck",
            ],
            "children_use_inherited_directory_fds_only": True,
            "logical_paths_are_identity_labels_only": True,
            "children": [
                {
                    "role": item["role"],
                    "directory_fds": checker.DIRECTORY_FD_PATHS,
                    "target_fd_cloexec_cleared": True,
                    "openat_only": True,
                    "logical_paths_identity_only": True,
                }
                for item in checker.SUPERVISOR_CHILDREN
            ],
        },
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
        "producer_build": {
            "embedded_protocol_commit": decision["protocol_commit"],
            "embedded_role_commit": decision["producer_commit"],
            "embedded_build_profile": "release", "embedded_dirty": False,
            "embedded_git_metadata_present": True,
            "binary_byte_length": decision["producer_binary_byte_length"],
            "binary_sha256": decision["producer_binary_sha256"],
        },
        "verifier_build": {
            "embedded_protocol_commit": decision["protocol_commit"],
            "embedded_role_commit": decision["verifier_commit"],
            "embedded_build_profile": "release", "embedded_dirty": False,
            "embedded_git_metadata_present": True,
            "binary_byte_length": decision["verifier_binary_byte_length"],
            "binary_sha256": decision["verifier_binary_sha256"],
        },
        "supervisor_build": {
            "embedded_protocol_commit": decision["protocol_commit"], "embedded_producer_commit": decision["producer_commit"],
            "embedded_verifier_commit": decision["verifier_commit"], "embedded_supervisor_commit": decision["supervisor_commit"],
            "embedded_build_profile": "release", "embedded_supervisor_dirty": False, "embedded_git_metadata_present": True,
            "binary_byte_length": decision["supervisor_binary_byte_length"],
            "binary_sha256": decision["supervisor_binary_sha256"],
        },
        "execution_controls": copy.deepcopy(checker.EXECUTION_CONTROLS),
        "child_environment_policy": "inherit_except_removed_commit_variables_and_forbid_loader_overrides",
        "removed_variable_names": ["P192_WCM_PROTOCOL_COMMIT", "P192_WCM_SOURCE_COMMIT", "P192_WCM_VERIFIER_COMMIT"],
        "loader_override_prefixes": ["LD_", "DYLD_"],
        "forbidden_loader_override_names_present": [], "secret_values_recorded": False,
    }
    _canonical(run_dir / "environment.json", environment)
    _canonical(run_dir / "command.txt", decision["supervisor_argv"])
    control_artifact_inventory = [
        _artifact_for(control_dir, path) for path in checker.PRODUCER_PATHS
    ]
    control_tree_sha256 = checker._artifact_inventory_digest(control_artifact_inventory)
    raw = {
        "schema": "p192-wcm-role2-box0-raw-result-v1", "experiment_id": "EXP-SCURVE-1a8daf",
        "run_id": decision["run_id"], "stage": "P192-WCM-BOX0", "decision_custody": custody,
        "protocol_commit": decision["protocol_commit"], "factor_base_source_commit": decision["factor_base_source_commit"],
        "producer_commit": decision["producer_commit"], "verifier_commit": decision["verifier_commit"],
        "supervisor_commit": decision["supervisor_commit"], "run_dir": str(run_dir),
        "control_dir": str(control_dir), "control_tree_sha256": control_tree_sha256,
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
            "inputs": {"parameters": {"stage": "P192-WCM-BOX0", "shell_id": "BOX-0", "candidate_count": 262148, "predecessor_run_id": decision["predecessor_run_id"], "factor_base_sha256": factor_base_sha256, "decision_id": decision["decision_id"], "decision_commit": custody["decision_commit"], "decision_sha256": custody["decision_sha256"], "control_dir": str(control_dir), "control_tree_sha256": control_tree_sha256}},
            "timing": {"started_at_utc": "2026-10-07T12:00:00Z", "completed_at_utc": "2026-10-07T12:00:01Z", "duration_milliseconds": "1000"},
            "result": {"raw_result": "raw-result.json", "scientific_result": True, "certificate": {"kind": "independently_verified_box0_census", "path": "candidate-stream.json", "sha256": checker.sha256_path(run_dir / "candidate-stream.json")}},
            "artifacts": [_artifact_for(run_dir, path) for path in checker.MANIFEST_ARTIFACT_PATHS],
        }
    }
    _canonical(run_dir / "manifest.yaml", manifest)
    terminal_seal = {
        "schema": "p192-wcm-role2-terminal-custody-v1",
        "run_id": decision["run_id"],
        "decision_id": decision["decision_id"],
        "decision_commit": custody["decision_commit"],
        "decision_path_terminal": decision["paths"]["decision_json"],
        "decision_sha256_terminal": custody["decision_sha256"],
        "protocol_commit": decision["protocol_commit"],
        "protocol_head_at_runtime": custody["decision_commit"],
        "protocol_terminal_state": {
            "runtime_mode": "exact_untracked_output_trees",
            "allowed_output_roots": [
                run_dir.relative_to(Path(decision["paths"]["protocol_repository_path"])).as_posix(),
                control_dir.relative_to(Path(decision["paths"]["protocol_repository_path"])).as_posix(),
            ],
            "unexpected_paths": [],
        },
        "manifest_sha256": checker.sha256_path(run_dir / "manifest.yaml"),
        "raw_result_sha256": checker.sha256_path(run_dir / "raw-result.json"),
        "receipt_sha256": checker.sha256_path(run_dir / "independent-verifier-receipt.json"),
        "protected_protocol_blobs": decision["protected_protocol_blobs"],
        "binary_identities": binary_identities,
        "source_build_commits": {
            role: decision[f"{role}_commit"]
            for role in ("producer", "verifier", "supervisor")
        },
        "source_build_tree_sha256": {
            role: checker._source_input_digest(source_build_rows[role])
            for role in ("producer", "verifier", "supervisor")
        },
        "verifier_build_custody": checker._verifier_build_custody(decision),
        "predecessor_retained_fd_snapshots": predecessor_fd_snapshots,
        "run_directory_identity": checker._directory_identity(run_dir),
        "control_directory_identity": checker._directory_identity(control_dir),
        "run_inventory_before_terminal_seal": [
            checker._file_identity(run_dir / path, path)
            for path in checker.STAGE_PATHS + checker.CUSTODY_PATHS
        ],
        "control_inventory": [
            checker._file_identity(control_dir / path, path)
            for path in checker.PRODUCER_PATHS
        ],
        "sealed_image_sha256": {
            "producer": decision["producer_binary_sha256"],
            "verifier": decision["verifier_binary_sha256"],
        },
        "post_manifest_directory_fsync": True,
        "path_and_fd_rechecks_complete": True,
        "control_dir_retained": True,
        "inode_custody_scope": "original_supervised_workspace_only",
        "overall_status": "PASS",
    }
    _canonical(run_dir / checker.TERMINAL_CUSTODY_PATH, terminal_seal)
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


def test_restart_receipt_precedes_verifier_and_setup_failures_are_representable() -> None:
    addendum_document = yaml.safe_load(checker.ADDENDUM.read_text())
    overlay = yaml.safe_load(checker.OVERLAY.read_text())
    addendum = addendum_document["role2_box0_interface_addendum"]
    sequence = addendum["supervisor_custody"]["launch_sequence"]
    assert sequence == checker.SUPERVISOR_LAUNCH_SEQUENCE
    assert sequence.index("compare_all_producer_outputs_roots_counters_prefixes") < sequence.index(
        "write_checkpoint_resume_control"
    ) < sequence.index("launch_isolated_independent_verifier")

    resource = addendum["resource_admission"]
    admitted = resource["admitted_failure_mapping"]
    assert "status INCOMPLETE" in admitted
    assert "failure_reason incomplete_child_artifact" in admitted
    assert "both directories remain retained" in admitted.lower()
    setup = resource["paired_directory_setup_boundary"]
    assert "pre-evidence setup operation" in setup
    assert "freshly-created empty half-directory" in setup
    assert "reverse creation order" in setup
    assert "fsyncs each affected parent" in setup
    assert "hard custody violation requiring operator remediation" in setup
    assert "never a schema failure record" in setup
    assert "no raw result or PASS claim" in setup
    failure_prefix = addendum["terminal_status_semantics"][
        "failure_precedence_and_reason"
    ]
    assert (
        "all producer paths plus checkpoint-resume-control and "
        "independent-verification"
    ) in failure_prefix

    mutated = copy.deepcopy(addendum_document)
    mutated_sequence = mutated["role2_box0_interface_addendum"]["supervisor_custody"]["launch_sequence"]
    mutated_sequence.remove("write_checkpoint_resume_control")
    mutated_sequence.insert(
        mutated_sequence.index("prove_producer_sources_stable"),
        "write_checkpoint_resume_control",
    )
    assert any(
        "supervisor launch sequence" in error
        for error in checker.collect_contract_errors(mutated, overlay)
    )


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
        parsed, observed_custody, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert errors == []
        assert parsed == decision
        assert observed_custody == custody
        assert custody["decision_sha256"] == checker.sha256_path(decision_path)
        protected = Path(decision["paths"]["protocol_repository_path"]) / checker.PROTECTED_PROTOCOL_RELATIVE_PATHS["role2-artifacts.schema.json"]
        original_mode = stat.S_IMODE(protected.stat().st_mode)
        protected.chmod(original_mode | 0o100)
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any("protected current mode" in error for error in errors)
        protected.chmod(original_mode)
        decision_path.write_bytes(decision_path.read_bytes() + b"\n")
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
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
        profile = _decision()["selective_worktree_profiles"]["source"]
        _seal_selective_worktree(repository, profile)
        errors: list[str] = []
        checker._validate_git_checkout(
            repository, package, "f" * 40,
            ("tools", "p192-weighted-cm"), profile, "producer", errors,
        )
        assert any("Git HEAD" in error for error in errors)
        alias = base / "package-alias"
        alias.symlink_to(package, target_is_directory=True)
        errors = []
        checker._validate_git_checkout(
            repository, alias, commit, ("tools", "p192-weighted-cm"),
            profile, "producer", errors,
        )
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
        parsed, observed_custody, errors = _fixture_dispatch(
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
        assert any("retained CONTROL_DIR byte equality disposition.bin" in error for error in errors)
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
            (package / "build.rs").write_text(shared)
        rows = checker._collect_rust_hash_rows(producer)
        assert [row["path"] for row in rows] == ["build.rs", "src/lib.rs", "src/target/mod.rs"]
        screen = checker.compute_source_clone_screen(producer, verifier)
        assert screen["overall_status"] == "FAIL"
        assert screen["max_match_tokens"] >= 128
        assert any(match["producer_path"] == "src/target/mod.rs" for match in screen["matches"])
        assert any(match["producer_path"] == "build.rs" for match in screen["matches"])


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
        assert any("directly names forbidden package/target p192-weighted-cm" in error for error in errors)
        assert any("resolves to forbidden producer source package" in error for error in errors)


def test_failure_raw_counts_and_completed_inventory_are_replayed() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = Path(decision["paths"]["run_dir"])
        run_dir.mkdir()
        control_dir = Path(decision["paths"]["control_dir"])
        control_dir.mkdir()
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
            "control_dir": decision["paths"]["control_dir"],
            "control_state": "retained",
            "control_retained": True,
            "control_created_before_failure": True,
            "invalid_count": 0,
            "unresolved_count": 0,
            "failed_phase": "canonical_producer",
            "failure_reason": "incomplete_child_artifact",
            "completed_artifacts": [],
            "scientific_result": False,
            "scientific_results": [],
            "status": "INCOMPLETE",
        }
        _write_bytes(run_dir / "candidate-stream.json", b"{malformed")
        raw["terminal_failure_custody"] = {
            "custody_check_id": "post_directory_creation_terminal_failure_v1",
            "inode_custody_scope": "original_supervised_workspace_only",
            "run_entries_before_failure_record": checker._directory_custody_entries(run_dir),
            "control_directory_before_children": checker._directory_identity(control_dir),
            "control_directory_terminal": checker._directory_identity(control_dir),
            "control_entries": [],
            "failure_record_excluded_from_own_inventory": True,
            "pass_manifest_transition": "not_reached",
            "provisional_pass_manifest": None,
            "provisional_success_raw_result": None,
            "stale_pass_manifest_present_before_finalization": False,
            "stale_pass_manifest_removed": False,
            "pass_manifest_absent_after_finalization": True,
            "in_transaction_control_cleanup_performed": False,
        }
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
        _canonical(run_dir / "raw-result.json", raw)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any(
            "independent_verifier failure control retention" in error
            or "failure chronology lacks completed prior phase" in error
            for error in errors
        )

        raw["failed_phase"] = "canonical_producer"
        raw["completed_artifacts"] = [_artifact_for(run_dir, "candidate-stream.json")]
        _canonical(run_dir / "raw-result.json", raw)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("failure completed artifacts" in error for error in errors)


def test_every_failure_phase_passes_dispatch_and_artifact_validation_together() -> None:
    failed_artifact = {
        "restart_control": "checkpoint-resume-control.json",
        "independent_verifier": "independent-verification.json",
        "agreement": "independent-agreement.json",
        "final_custody": "dependency-audit.json",
    }
    for phase in checker.FAILURE_PHASE_ARTIFACTS:
        with tempfile.TemporaryDirectory() as temporary:
            decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
            run_dir = Path(decision["paths"]["run_dir"])
            control_dir = Path(decision["paths"]["control_dir"])
            if phase == "canonical_producer":
                run_dir.mkdir()
                control_dir.mkdir()
                raw = {
                    "schema": "p192-wcm-role2-box0-failure-v1",
                    "experiment_id": "EXP-SCURVE-1a8daf", "run_id": decision["run_id"],
                    "stage": "P192-WCM-BOX0", "decision_custody": custody,
                    "protocol_commit": decision["protocol_commit"],
                    "factor_base_source_commit": decision["factor_base_source_commit"],
                    "producer_commit": decision["producer_commit"],
                    "verifier_commit": decision["verifier_commit"],
                    "supervisor_commit": decision["supervisor_commit"],
                    "run_dir": str(run_dir), "control_dir": str(control_dir),
                    "control_state": "retained", "control_retained": True,
                    "control_created_before_failure": True,
                    "invalid_count": 0, "unresolved_count": 0,
                    "failed_phase": phase,
                    "failure_reason": "incomplete_child_artifact",
                    "completed_artifacts": [], "scientific_result": False,
                    "scientific_results": [], "status": "INCOMPLETE",
                    "terminal_failure_custody": {
                        "custody_check_id": "post_directory_creation_terminal_failure_v1",
                        "inode_custody_scope": "original_supervised_workspace_only",
                        "run_entries_before_failure_record": [],
                        "control_directory_before_children": checker._directory_identity(control_dir),
                        "control_directory_terminal": checker._directory_identity(control_dir),
                        "control_entries": [],
                        "failure_record_excluded_from_own_inventory": True,
                        "pass_manifest_transition": "not_reached",
                        "provisional_pass_manifest": None,
                        "provisional_success_raw_result": None,
                        "stale_pass_manifest_present_before_finalization": False,
                        "stale_pass_manifest_removed": False,
                        "pass_manifest_absent_after_finalization": True,
                        "in_transaction_control_cleanup_performed": False,
                    },
                }
                _canonical(run_dir / "raw-result.json", raw)
            else:
                run_dir = _build_valid_run(decision, custody)
                (run_dir / failed_artifact[phase]).unlink()
                _replace_success_with_failure(
                    run_dir, decision, custody, phase,
                    "incomplete_child_artifact",
                )
            _, _, dispatch_errors = _fixture_dispatch(
                decision_path, "post-run", run_dir,
            )
            artifact_errors = checker.validate_post_run(run_dir, decision, custody)
            assert dispatch_errors == [], (phase, dispatch_errors)
            assert artifact_errors == [], (phase, artifact_errors)
            if phase == "canonical_producer":
                _write_bytes(control_dir / "unexpected.tmp", b"forbidden")
                errors = checker.validate_post_run(run_dir, decision, custody)
                assert any("empty CONTROL_DIR" in error for error in errors)
                (control_dir / "unexpected.tmp").unlink()
                original_control = control_dir.with_name(control_dir.name + "-original")
                control_dir.rename(original_control)
                control_dir.mkdir()
                errors = checker.validate_post_run(run_dir, decision, custody)
                assert any("failure terminal custody" in error for error in errors)


def test_dispatch_rejects_noncanonical_output_roots_and_equal_binary_bindings() -> None:
    decision = _decision()
    decision["paths"]["run_dir"] = "/protocol/runs/RUN-SCURVE-222222"
    decision["paths"]["audit_file"] = decision["paths"]["run_dir"] + "/dependency-audit.json"
    decision.update(checker.resolved_argv(decision))
    assert any("canonical RUN_DIR" in error for error in checker.validate_decision(decision))

    decision = _decision()
    decision["paths"]["verifier_bin"] = decision["paths"]["producer_bin"]
    decision.update(checker.resolved_argv(decision))
    assert any("binary paths" in error for error in checker.validate_decision(decision))

    decision = _decision()
    decision["verifier_binary_sha256"] = decision["producer_binary_sha256"]
    assert any("binary hashes" in error for error in checker.validate_decision(decision))


def test_dispatch_rejects_binary_hardlinks() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        producer = Path(decision["paths"]["producer_bin"])
        verifier = Path(decision["paths"]["verifier_bin"])
        verifier.unlink()
        os.link(producer, verifier)
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any(
            "share a device/inode" in error
            or ("binary" in error and "link count" in error)
            for error in errors
        )


def test_source_binding_rejects_ignored_extra_inputs_and_index_flags() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        repository = Path(decision["paths"]["producer_repository_path"])
        package = Path(decision["paths"]["producer_package_path"])
        (repository / ".git/info/exclude").write_text("*.rs\n*.bin\n", encoding="utf-8")
        _write_bytes(package / "src/ignored.rs", b"pub fn ignored() {}\n")
        _write_bytes(package / "src/generated.bin", b"ignored build data\n")
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any(
            "source/build path inventory" in error
            or "info/exclude" in error
            for error in errors
        )

    for flag, clear_flag in (("--skip-worktree", "--no-skip-worktree"), ("--assume-unchanged", "--no-assume-unchanged")):
        with tempfile.TemporaryDirectory() as temporary:
            decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
            repository = Path(decision["paths"]["producer_repository_path"])
            relative = "tools/p192-weighted-cm/src/lib.rs"
            _git(repository, "update-index", flag, relative)
            _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
            assert any(
                "index" in error and "flag" in error for error in errors
            )
            _git(repository, "update-index", clear_flag, relative)


def test_post_run_protocol_state_rejects_unrelated_untracked_path() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        protocol = Path(decision["paths"]["protocol_repository_path"])
        _write_bytes(protocol / "rogue-untracked.txt", b"rogue\n")
        _, _, errors = _fixture_dispatch(decision_path, "post-run", run_dir)
        assert any(
            "protocol post-run unexpected path" in error
            or "protocol topology worktree has unexpected files" in error
            for error in errors
        )


def test_archival_replay_accepts_exact_committed_output_descendant() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        parsed, observed, errors = _fixture_dispatch(
            decision_path, "post-run", run_dir,
        )
        assert errors == [] and parsed == decision and observed == custody
        assert checker.validate_post_run(run_dir, decision, custody) == []

        protocol = Path(decision["paths"]["protocol_repository_path"])
        descendant = _commit_all(protocol, "archive exact Role2 outputs")
        _seal_selective_worktree(
            protocol, decision["selective_worktree_profiles"]["protocol"],
        )
        assert descendant != custody["decision_commit"]
        parsed, replay_custody, errors = _fixture_dispatch(
            decision_path, "post-run", run_dir,
        )
        assert errors == [] and parsed == decision
        assert replay_custody == custody
        assert replay_custody["decision_commit"] != descendant
        assert checker.validate_post_run(run_dir, decision, replay_custody) == []


def test_verifier_dependency_scan_rejects_crypto_lib_all_routes() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        repository = root / "native"
        verifier = repository / "tools/p192-weighted-cm-verify"
        producer = repository / "tools/p192-weighted-cm"
        verifier.mkdir(parents=True)
        producer.mkdir(parents=True)
        _write_bytes(repository / "Cargo.toml", b"[package]\nname='crypto'\nversion='0.1.0'\n[lib]\nname='crypto_lib'\n")
        _write_bytes(producer / "Cargo.toml", b"[package]\nname='p192-weighted-cm'\nversion='0.1.0'\n")
        _write_bytes(verifier / "Cargo.toml", b"[package]\nname='verifier'\nversion='0.1.0'\n")
        manifest = (
            "[package]\nname='verifier'\nversion='0.1.0'\n"
            f"[build-dependencies]\nmath={{package='crypto',path='{repository}'}}\n"
            "[dev-dependencies]\nprod={package='p192-weighted-cm',path='../p192-weighted-cm'}\n"
            "[target.'cfg(unix)'.dependencies]\nworkspace_math={workspace=true}\n"
            "git_math={git='https://example.invalid/crypto'}\n"
        ).encode()
        lock = (
            b"version = 3\n"
            b"[[package]]\nname='verifier'\nversion='0.1.0'\n"
            b"[[package]]\nname='crypto'\nversion='0.1.0'\n"
        )
        errors = checker._verifier_dependency_errors(
            manifest, lock, repository, verifier, repository, producer,
        )
        assert any("directly names forbidden package/target crypto" in error for error in errors)
        assert any("forbidden production-library repository root" in error for error in errors)
        assert any("forbidden producer source package" in error for error in errors)
        assert any("forbidden workspace inheritance" in error for error in errors)
        assert any("forbidden git source" in error for error in errors)
        assert any("Cargo.lock contains forbidden package crypto" in error for error in errors)


def test_verifier_dependency_scan_rejects_root_alias_path_variants_and_wrappers() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        repository = root / "native"
        verifier = repository / "tools/p192-weighted-cm-verify"
        producer = repository / "tools/p192-weighted-cm"
        verifier.mkdir(parents=True)
        producer.mkdir(parents=True)
        _write_bytes(repository / "Cargo.toml", b"[package]\nname='crypto'\nversion='0.1.0'\n[lib]\nname='crypto_lib'\n")
        _write_bytes(producer / "Cargo.toml", b"[package]\nname='p192-weighted-cm'\nversion='0.1.0'\n")
        _write_bytes(verifier / "Cargo.toml", b"[package]\nname='verifier'\nversion='0.1.0'\n")
        lock = (
            b"version = 3\n"
            b"[[package]]\nname='verifier'\nversion='0.1.0'\n"
            b"[[package]]\nname='crypto'\nversion='0.1.0'\n"
        )
        repository_link = root / "production-link"
        repository_link.symlink_to(repository, target_is_directory=True)
        for dependency_path in (str(repository), "../..", str(repository_link)):
            manifest = (
                "[package]\nname='verifier'\nversion='0.1.0'\n"
                f"[dependencies]\nmath={{package='crypto',path={dependency_path!r}}}\n"
            ).encode()
            errors = checker._verifier_dependency_errors(
                manifest, lock, repository, verifier, repository, producer,
            )
            assert any(
                "resolves to forbidden production-library repository root" in error
                for error in errors
            ), dependency_path
            if dependency_path == str(repository_link):
                assert any("path has symlink component" in error for error in errors)

        disguised = root / "disguised"
        disguised.mkdir()
        _write_bytes(disguised / "Cargo.toml", b"[package]\nname='harmless'\nversion='0.1.0'\n[lib]\nname='crypto_lib'\n")
        disguised_manifest = (
            "[package]\nname='verifier'\nversion='0.1.0'\n"
            f"[dependencies]\nmath={{package='harmless',path={str(disguised)!r}}}\n"
        ).encode()
        errors = checker._verifier_dependency_errors(
            disguised_manifest, lock, repository, verifier, repository, producer,
        )
        assert any("path exposes forbidden package/target crypto-lib" in error for error in errors)

        helper = root / "hidden-helper"
        helper.mkdir()
        _write_bytes(
            helper / "Cargo.toml",
            (
                "[package]\nname='helper'\nversion='0.1.0'\n"
                f"[dependencies]\nbackend={{package='crypto',path={str(repository)!r}}}\n"
            ).encode(),
        )
        wrapper_manifest = (
            "[package]\nname='verifier'\nversion='0.1.0'\n"
            f"[dependencies]\nhelper={{path={str(helper)!r}}}\n"
        ).encode()
        errors = checker._verifier_dependency_errors(
            wrapper_manifest, lock, repository, verifier, repository, producer,
        )
        assert any("uses forbidden path source" in error for error in errors)
        assert any("resolves to forbidden production-library repository root" in error for error in errors)

        missing_manifest = (
            "[package]\nname='verifier'\nversion='0.1.0'\n"
            f"[dependencies]\nmissing={{path={str(root / 'missing')!r}}}\n"
        ).encode()
        errors = checker._verifier_dependency_errors(
            missing_manifest, lock, repository, verifier, repository, producer,
        )
        assert any("path cannot be resolved" in error for error in errors)


def test_verifier_dependency_scan_accepts_only_checksum_bound_registry_graph() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        verifier_repository = root / "verifier-repository"
        verifier = verifier_repository / "tools/p192-weighted-cm-verify"
        producer_repository = root / "producer-repository"
        producer = producer_repository / "tools/p192-weighted-cm"
        verifier.mkdir(parents=True)
        producer.mkdir(parents=True)
        _write_bytes(verifier / "Cargo.toml", b"[package]\nname='verifier'\nversion='0.1.0'\n")
        _write_bytes(producer / "Cargo.toml", b"[package]\nname='p192-weighted-cm'\nversion='0.1.0'\n")
        manifest = b"[workspace]\n[package]\nname='verifier'\nversion='0.1.0'\n[dependencies]\nserde='1'\n"
        lock = (
            b"version = 3\n"
            b"[[package]]\nname='verifier'\nversion='0.1.0'\n"
            b"[[package]]\nname='serde'\nversion='1.0.0'\n"
            b"source='registry+https://github.com/rust-lang/crates.io-index'\n"
            + f"checksum='{'a' * 64}'\n".encode()
        )
        assert checker._verifier_dependency_errors(
            manifest, lock, verifier_repository, verifier,
            producer_repository, producer,
        ) == []


def test_retained_control_inventory_rejects_missing_suffix_symlink_and_hardlink() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        control = Path(decision["paths"]["control_dir"])
        target = control / checker.PRODUCER_PATHS[0]
        original = target.read_bytes()

        target.unlink()
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("CONTROL_DIR exact path set" in error for error in errors)
        _write_bytes(target, original)

        suffix = control / "verification.json.tmp"
        _write_bytes(suffix, b"suffix")
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("CONTROL_DIR exact path set" in error for error in errors)
        suffix.unlink()

        target.unlink()
        target.symlink_to(run_dir / checker.PRODUCER_PATHS[0])
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any(
            "symlink" in error or "nonregular leaf" in error
            for error in errors
        )
        target.unlink()
        _write_bytes(target, original)

        target.write_bytes(original + b"mismatch")
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("retained CONTROL_DIR byte equality" in error for error in errors)
        target.write_bytes(original)

        target.unlink()
        os.link(run_dir / checker.PRODUCER_PATHS[0], target)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("link count is not one" in error or "aliases another output" in error for error in errors)

        target.unlink()
        os.link(Path(decision["paths"]["predecessor_dir"]) / checker.PREDECESSOR_PATHS[0], target)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any(
            "aliases an immutable input" in error
            or "link count is not one" in error
            for error in errors
        )


def test_terminal_seal_and_snapshot_swap_are_admission_gates() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        terminal_path = run_dir / checker.TERMINAL_CUSTODY_PATH
        terminal = checker.decode_canonical_json(terminal_path.read_bytes())
        terminal["post_manifest_directory_fsync"] = False
        _canonical(terminal_path, terminal)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("terminal-custody.json" in error for error in errors)

        terminal["post_manifest_directory_fsync"] = True
        terminal["decision_sha256_terminal"] = "f" * 64
        _canonical(terminal_path, terminal)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("decision_sha256_terminal" in error or "post-manifest terminal custody seal" in error for error in errors)

        terminal["decision_sha256_terminal"] = custody["decision_sha256"]
        _canonical(terminal_path, terminal)
        receipt_path = run_dir / "independent-verifier-receipt.json"
        receipt = checker.decode_canonical_json(receipt_path.read_bytes())
        receipt["binary_identities_after"]["producer"] = receipt["binary_identities_after"]["verifier"]
        _canonical(receipt_path, receipt)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("binary identities after" in error for error in errors)

        receipt["binary_identities_after"] = copy.deepcopy(receipt["binary_identities_before"])
        receipt["source_build_tree_sha256_after"]["producer"] = "e" * 64
        _canonical(receipt_path, receipt)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("source/build tree digests after" in error for error in errors)


def test_fixed_child_fd_abi_is_an_admission_gate() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        receipt_path = run_dir / "independent-verifier-receipt.json"
        receipt = checker.decode_canonical_json(receipt_path.read_bytes())
        receipt["execution_custody"]["sealed_images"][0]["launch_path"] = "/proc/self/fd/42"
        receipt["children"][0]["actual_exec_path"] = "/proc/self/fd/42"
        _canonical(receipt_path, receipt)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any(
            "independent-verifier-receipt.json" in error
            and "/proc/self/fd/42" in error
            for error in errors
        )


def test_full_role1_replay_rejects_near_valid_forgery_classes() -> None:
    predecessor = ROOT / "experiments/EXP-SCURVE-1a8daf/runs/RUN-SCURVE-561a96"
    historical_receipt = checker.decode_canonical_json(
        (predecessor / "independent-verifier-receipt.json").read_bytes()
    )
    historical_protocol = historical_receipt["protocol_commit"]
    historical_decision = historical_receipt["decision_binding"]["decision_commit"]

    def historical_unit_replay(path: Path, errors: list[str]) -> dict | None:
        """Keep the old archive only as a semantic fixture, not admissible lineage."""
        original = checker._raw_commit_parents

        def direct_parents(
            repository: Path, commit: str, label: str, target: list[str],
        ) -> list[str] | None:
            if label == "Role-1 predecessor decision":
                return [historical_protocol]
            if label == "Role-1 predecessor archive":
                return [historical_decision]
            return original(repository, commit, label, target)

        checker._raw_commit_parents = direct_parents
        try:
            return checker._role1_predecessor_binding(path, ROOT, errors)
        finally:
            checker._raw_commit_parents = original

    errors: list[str] = []
    binding = historical_unit_replay(predecessor, errors)
    assert errors == [] and binding is not None
    assert binding["receipt"] == checker.decode_canonical_json(
        (predecessor / "independent-verifier-receipt.json").read_bytes()
    )
    assert len(binding["artifact_inventory"]) == len(checker.ROLE1_REQUIRED_PATHS) == 20

    mutations = ("wrong_verifier_commit", "wrong_verifier_binary", "shallow_receipt", "malformed_inventory", "duplicate_comparison")
    for mutation in mutations:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / predecessor.name
            shutil.copytree(predecessor, forged)
            if mutation == "duplicate_comparison":
                path = forged / "independent-agreement.json"
                document = checker.decode_canonical_json(path.read_bytes())
                document["comparisons"][1] = copy.deepcopy(document["comparisons"][0])
            else:
                path = forged / "independent-verifier-receipt.json"
                document = checker.decode_canonical_json(path.read_bytes())
                if mutation == "wrong_verifier_commit":
                    document["verifier_commit"] = "3" * 40
                elif mutation == "wrong_verifier_binary":
                    document["verifier"]["binary_sha256"] = "4" * 64
                elif mutation == "shallow_receipt":
                    document = {
                        "schema": "p192-wcm-independent-verifier-receipt-v1",
                        "overall_status": "PASS",
                    }
                else:
                    document["producer_artifacts_before"] = []
            _canonical(path, document)
            forgery_errors: list[str] = []
            historical_unit_replay(forged, forgery_errors)
            assert forgery_errors, mutation
            if mutation != "shallow_receipt":
                assert any(
                    "Role-1 run replay" in error
                    or "receipt/run-directory identity" in error
                    for error in forgery_errors
                ), mutation


def test_directory_fd_handoff_and_runtime_mode_are_admission_gates() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        receipt_path = run_dir / "independent-verifier-receipt.json"
        receipt = checker.decode_canonical_json(receipt_path.read_bytes())
        receipt["directory_custody"]["children"][0]["directory_fds"]["run_dir"] = "/proc/self/fd/65"
        _canonical(receipt_path, receipt)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("independent-verifier-receipt.json" in error and "/proc/self/fd/65" in error for error in errors)

        receipt["directory_custody"]["children"][0]["directory_fds"]["run_dir"] = "/proc/self/fd/63"
        original_inode = receipt["directory_custody"]["identities"][3]["inode"]
        receipt["directory_custody"]["identities"][3]["inode"] = str(int(original_inode) + 1)
        _canonical(receipt_path, receipt)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("retained directory identities" in error for error in errors)

        receipt["directory_custody"]["identities"][3]["inode"] = original_inode
        receipt["execution_custody"]["predecessor_fd_interface"][
            "original_paths_rechecked_before_each_child"
        ] = False
        _canonical(receipt_path, receipt)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any(
            "predecessor original path prelaunch rechecks" in error
            or "original_paths_rechecked_before_each_child" in error
            for error in errors
        )

    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        seal_path = run_dir / checker.TERMINAL_CUSTODY_PATH
        seal = checker.decode_canonical_json(seal_path.read_bytes())
        seal["protocol_terminal_state"]["runtime_mode"] = "exact_committed_evidence"
        _canonical(seal_path, seal)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("terminal-custody.json" in error and "exact_committed_evidence" in error for error in errors)


def test_protocol_git_state_rejects_ignored_hybrid_index_and_unrelated_archive_delta() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        protocol = Path(decision["paths"]["protocol_repository_path"])
        exclude = protocol / ".git/info/exclude"
        exclude.write_text("rogue-ignored.txt\n", encoding="utf-8")
        _write_bytes(protocol / "rogue-ignored.txt", b"ignored rogue\n")
        _, _, errors = _fixture_dispatch(decision_path, "post-run", run_dir)
        assert any("info/exclude" in error for error in errors)

    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        protocol = Path(decision["paths"]["protocol_repository_path"])
        raw_relative = (run_dir / "raw-result.json").relative_to(protocol).as_posix()
        (protocol / ".git/info/exclude").write_text(raw_relative + "\n", encoding="utf-8")
        _, _, errors = _fixture_dispatch(decision_path, "post-run", run_dir)
        assert any("info/exclude" in error for error in errors)

    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        protocol = Path(decision["paths"]["protocol_repository_path"])
        relative = (run_dir / "candidate-stream.json").relative_to(protocol).as_posix()
        _git(protocol, "add", "--", relative)
        _git(protocol, "commit", "-q", "-m", "partial evidence must fail")
        _, _, errors = _fixture_dispatch(decision_path, "post-run", run_dir)
        assert any("hybrid or incomplete" in error or "tracked output inventory differs" in error for error in errors)

    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        protocol = Path(decision["paths"]["protocol_repository_path"])
        _write_bytes(protocol / "unrelated-post-run-commit.txt", b"not evidence\n")
        _git(protocol, "add", "--", "unrelated-post-run-commit.txt")
        _git(protocol, "commit", "-q", "-m", "unrelated post-run commit")
        _, _, errors = _fixture_dispatch(decision_path, "post-run", run_dir)
        assert any(
            "untracked evidence protocol HEAD/decision commit" in error
            for error in errors
        )
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any(
            "untracked evidence protocol HEAD/decision commit" in error
            for error in errors
        )

    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        protocol = Path(decision["paths"]["protocol_repository_path"])
        _write_bytes(protocol / "unrelated-archive-note.txt", b"not evidence\n")
        _commit_all(protocol, "archive evidence plus unrelated delta")
        _, _, errors = _fixture_dispatch(decision_path, "post-run", run_dir)
        assert any("exact decision-to-archive delta" in error for error in errors)

    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        protocol = Path(decision["paths"]["protocol_repository_path"])
        flagged = checker.PROTECTED_PROTOCOL_RELATIVE_PATHS["run-family.yaml"]
        _git(protocol, "update-index", "--skip-worktree", "--", flagged)
        _, _, errors = _fixture_dispatch(decision_path, "post-run", run_dir)
        assert any(
            "index" in error and ("flag" in error or "skip" in error)
            for error in errors
        )


def test_protocol_topology_rejects_filter_routes_without_executing_side_effects() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        protocol = Path(decision["paths"]["protocol_repository_path"])
        victim = protocol / "tracked-filtered.txt"
        marker = Path(temporary) / "filter-executed"
        script = Path(temporary) / "side-effect-filter.sh"
        _write_bytes(protocol / ".gitattributes", b"tracked-filtered.txt filter=sideeffect\n")
        _write_bytes(protocol / "tracked-filtered.txt", b"CANONICAL")
        _git(protocol, "add", "--", ".gitattributes", "tracked-filtered.txt")
        _git(protocol, "commit", "-q", "--amend", "--no-edit")
        _write_bytes(
            script,
            (
                f"#!/bin/sh\nprintf MUTATED > '{victim}'\nprintf EXECUTED > '{marker}'\ncat\n"
            ).encode(),
            executable=True,
        )
        _git(protocol, "config", "filter.sideeffect.clean", str(script))
        _git(protocol, "config", "filter.sideeffect.process", str(script))
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any(
            "filter/diff/include execution route" in error
            or "forbidden conversion route" in error
            or "canonical minimal standalone Git config" in error
            for error in errors
        )
        assert victim.read_bytes() == b"CANONICAL"
        assert not marker.exists()


def test_cargo_metadata_cannot_mutate_source_git_admin_after_initial_scan() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        verifier_repository = Path(decision["paths"]["verifier_repository_path"])
        cargo = Path(decision["verifier_build_admission"]["cargo_identity"]["path"])
        original = cargo.read_bytes()
        assert original.startswith(b"#!/bin/sh\n")
        mutation = (
            b"printf '[user]\\n\\tname = mutated-by-cargo\\n' >> '"
            + str(verifier_repository / ".git/config").encode()
            + b"'\n"
        )
        _write_bytes(cargo, b"#!/bin/sh\n" + mutation + original[len(b"#!/bin/sh\n"):], executable=True)
        decision["verifier_build_admission"]["cargo_identity"] = checker._file_identity(cargo)
        _canonical(decision_path, decision)
        _git(
            Path(decision["paths"]["protocol_repository_path"]),
            "commit", "-q", "--amend", "--no-edit", "--all",
        )
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any(
            "terminal verifier" in error
            and (
                "canonical minimal standalone Git config" in error
                or "Git preflight config" in error
            )
            for error in errors
        ), errors


def test_protocol_topology_rejects_rogue_empty_directory() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        protocol = Path(decision["paths"]["protocol_repository_path"])
        (protocol / "rogue-empty-directory").mkdir()
        assert _git(protocol, "status", "--porcelain=v1") == ""

        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any(
            "protocol topology worktree has unexpected or empty directories" in error
            and "rogue-empty-directory" in error
            for error in errors
        )


def test_protocol_topology_walk_caps_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, _, _ = _committed_decision_fixture(Path(temporary))
        saved = (
            checker.PROTOCOL_TOPOLOGY_ENTRY_CAP,
            checker.PROTOCOL_TOPOLOGY_DEPTH_CAP,
            checker.PROTOCOL_TOPOLOGY_PATH_BYTES_CAP,
        )
        try:
            checker.PROTOCOL_TOPOLOGY_ENTRY_CAP = 1
            _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
            assert any("entry cap" in error for error in errors)
            checker.PROTOCOL_TOPOLOGY_ENTRY_CAP = saved[0]
            checker.PROTOCOL_TOPOLOGY_DEPTH_CAP = 0
            _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
            assert any("depth cap" in error for error in errors)
            checker.PROTOCOL_TOPOLOGY_DEPTH_CAP = saved[1]
            checker.PROTOCOL_TOPOLOGY_PATH_BYTES_CAP = 1
            _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
            assert any("path exceeds byte cap" in error for error in errors)
        finally:
            (
                checker.PROTOCOL_TOPOLOGY_ENTRY_CAP,
                checker.PROTOCOL_TOPOLOGY_DEPTH_CAP,
                checker.PROTOCOL_TOPOLOGY_PATH_BYTES_CAP,
            ) = saved

    with tempfile.TemporaryDirectory() as temporary:
        repository = Path(temporary) / "protocol"
        run_dir = repository / "runs/run"
        control_dir = repository / "controls/run-restart"
        _write_bytes(run_dir / "one", b"1")
        _write_bytes(run_dir / "two", b"2")
        control_dir.mkdir(parents=True)
        saved_entry_cap = checker.PROTOCOL_TOPOLOGY_ENTRY_CAP
        try:
            checker.PROTOCOL_TOPOLOGY_ENTRY_CAP = 1
            errors: list[str] = []
            checker._output_leaf_paths(
                repository, (run_dir, control_dir), errors,
            )
            assert any(
                "protocol output inventory" in error and "entry cap" in error
                for error in errors
            )
        finally:
            checker.PROTOCOL_TOPOLOGY_ENTRY_CAP = saved_entry_cap


@pytest.mark.parametrize("admin_path", ["objects", "index", "config", "refs"])
def test_protocol_rejects_externalized_git_admin_paths(admin_path: str) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        protocol = Path(decision["paths"]["protocol_repository_path"])
        source = protocol / ".git" / admin_path
        external = Path(temporary) / f"external-{admin_path}"
        source.rename(external)
        source.symlink_to(external, target_is_directory=external.is_dir())
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any(
            "Git administration symlink is forbidden" in error
            or "not a real nofollow directory" in error
            or "local Git config cannot be read" in error
            for error in errors
        ), (admin_path, errors)


def test_protocol_rejects_linked_worktree_and_object_alternates() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        protocol = Path(decision["paths"]["protocol_repository_path"])
        primary = protocol.with_name("protocol-primary")
        protocol.rename(primary)
        _git(primary, "worktree", "add", "-q", "--detach", str(protocol), "HEAD")
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any(".git is not a real nofollow directory" in error for error in errors)

    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        protocol = Path(decision["paths"]["protocol_repository_path"])
        objects = protocol / ".git/objects"
        external = Path(temporary) / "external-objects"
        objects.rename(external)
        (objects / "info").mkdir(parents=True)
        (objects / "pack").mkdir()
        _write_bytes(objects / "info/alternates", (str(external) + "\n").encode())
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any(
            "objects/info/alternates" in error
            or "standalone Git object dir" in error
            for error in errors
        )


def test_protocol_rejects_bom_include_and_gpg_program_before_execution() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        protocol = Path(decision["paths"]["protocol_repository_path"])
        marker = Path(temporary) / "gpg-program-executed"
        helper = Path(temporary) / "gpg-helper.sh"
        _write_bytes(helper, f"#!/bin/sh\nprintf EXECUTED > '{marker}'\nexit 0\n".encode(), executable=True)
        current = _git(protocol, "rev-parse", "HEAD")
        raw_commit = _git_input(protocol, ["cat-file", "commit", current], b"")
        header, message = raw_commit.split(b"\n\n", 1)
        forged = (
            header
            + b"\ngpgsig -----BEGIN PGP SIGNATURE-----\n forged\n -----END PGP SIGNATURE-----"
            + b"\n\n" + message
        )
        forged_id = _git_input(
            protocol, ["hash-object", "-t", "commit", "-w", "--stdin"], forged,
        ).decode().strip()
        _git(protocol, "update-ref", "HEAD", forged_id)
        external = Path(temporary) / "included.config"
        _write_bytes(external, f"[gpg]\n\tprogram = {helper}\n".encode())
        _write_bytes(
            protocol / ".git/config",
            b"\xef\xbb\xbf[include]\n\tpath = " + str(external).encode()
            + b"\n[log]\n\tshowSignature = true\n",
        )
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any("canonical minimal standalone Git config" in error for error in errors)
        assert not marker.exists()


def test_protocol_rejects_hidden_empty_tree_in_decision_commit() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        protocol = Path(decision["paths"]["protocol_repository_path"])
        listing = _git_input(protocol, ["ls-tree", "HEAD"], b"")
        empty_tree = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
        forged_tree = _git_input(
            protocol, ["mktree"],
            listing + f"040000 tree {empty_tree}\trogue-empty-git-tree\n".encode(),
        ).decode().strip()
        forged_commit = _git_input(
            protocol,
            ["commit-tree", forged_tree, "-p", decision["protocol_commit"], "-m", "decision with hidden tree"],
            b"",
        ).decode().strip()
        _git(protocol, "reset", "--hard", "-q", forged_commit)
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any(
            "raw HEAD directory tree inventory" in error
            or "protocol-to-decision full tree topology delta" in error
            for error in errors
        )


def test_output_inventory_is_independent_of_git_ignore_rules() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        repository = Path(temporary) / "repository"
        run_dir = repository / "runs/run"
        control_dir = repository / "controls/run-restart"
        _write_bytes(repository / ".gitignore", b"ignored-output.json\n")
        _write_bytes(run_dir / "ignored-output.json", b"still inventoried\n")
        control_dir.mkdir(parents=True)
        errors: list[str] = []
        observed = checker._output_leaf_paths(
            repository, (run_dir, control_dir), errors,
        )
        assert errors == []
        assert observed == {"runs/run/ignored-output.json"}
        assert not hasattr(checker, "_ignored_output_paths")


def test_fifo_inputs_are_rejected_promptly_without_blocking() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        decision_path.unlink()
        os.mkfifo(decision_path)
        completed = _checker_probe(
            "d,cu,e=c.validate_dispatch_decision(Path(sys.argv[2]),'pre-dispatch');"
            "print(json.dumps(e))",
            decision_path,
        )
        assert completed.returncode == 0, completed.stderr
        assert (
            "not a regular nofollow file" in completed.stdout
            or "special file is forbidden" in completed.stdout
        )

    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        protocol = Path(decision["paths"]["protocol_repository_path"])
        config = protocol / ".git/config"
        config.unlink()
        os.mkfifo(config)
        profile = json.dumps(decision["selective_worktree_profiles"]["protocol"])
        completed = _checker_probe(
            "print(json.dumps(c._repository_git_preflight_errors("
            "Path(sys.argv[2]),json.loads(sys.argv[3]))))",
            protocol, profile,
        )
        assert completed.returncode == 0, completed.stderr
        assert "special entry is forbidden" in completed.stdout

    with tempfile.TemporaryDirectory() as temporary:
        _, decision, _ = _committed_decision_fixture(Path(temporary))
        protocol = Path(decision["paths"]["protocol_repository_path"])
        attributes = protocol / ".gitattributes"
        _write_bytes(attributes, b"* -text\n")
        head = _commit_all(protocol, "tracked non-conversion attributes")
        profile = decision["selective_worktree_profiles"]["protocol"]
        _seal_selective_worktree(protocol, profile)
        if os.path.lexists(attributes):
            attributes.unlink()
        os.mkfifo(attributes)
        completed = _checker_probe(
            "print(json.dumps(c._protocol_repository_topology_errors("
            "Path(sys.argv[2]),sys.argv[3],(),json.loads(sys.argv[4]))))",
            protocol, head, json.dumps(profile),
        )
        assert completed.returncode == 0, completed.stderr
        assert (
            "not a regular nofollow file" in completed.stdout
            or "special file is forbidden" in completed.stdout
        )

    with tempfile.TemporaryDirectory() as temporary:
        artifact = Path(temporary) / "raw-result.json"
        os.mkfifo(artifact)
        completed = _checker_probe(
            "e=[];c._load_json_artifact(Path(sys.argv[2]),'FIFO artifact',e);"
            "print(json.dumps(e))",
            artifact,
        )
        assert completed.returncode == 0, completed.stderr
        assert "not a regular nofollow file" in completed.stdout


def test_decision_merge_and_multicommit_archive_history_are_rejected() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        protocol = Path(decision["paths"]["protocol_repository_path"])
        decision_tree = _git(protocol, "rev-parse", "HEAD^{tree}")
        _git(protocol, "checkout", "-q", "-b", "rogue-parent", decision["protocol_commit"])
        _write_bytes(protocol / "rogue-second-parent.txt", b"hidden history\n")
        rogue_parent = _commit_all(protocol, "rogue second parent")
        forged = _git_input(
            protocol,
            [
                "commit-tree", decision_tree,
                "-p", decision["protocol_commit"], "-p", rogue_parent,
                "-m", "merge-shaped decision",
            ],
            b"",
        ).decode().strip()
        _git(protocol, "reset", "--hard", "-q", forged)
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any(
            "single-parent chain" in error
            or "single direct protocol parent" in error
            for error in errors
        )

    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        protocol = Path(decision["paths"]["protocol_repository_path"])
        transient = protocol / "transient-unrelated.txt"
        _write_bytes(transient, b"must never enter archive history\n")
        _commit_all(protocol, "archive outputs plus transient unrelated path")
        transient.unlink()
        _commit_all(protocol, "launder transient path by revert")
        _, _, errors = _fixture_dispatch(decision_path, "post-run", run_dir)
        assert any(
            "more than one archive commit" in error
            or "not exactly one commit" in error
            or "one direct archive commit" in error
            for error in errors
        )

    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        protocol = Path(decision["paths"]["protocol_repository_path"])
        transient = run_dir / "transient-rogue.txt"
        _write_bytes(transient, b"must not be laundered inside output root\n")
        _commit_all(protocol, "archive outputs plus transient output leaf")
        transient.unlink()
        _commit_all(protocol, "delete transient output leaf")
        _, _, errors = _fixture_dispatch(decision_path, "post-run", run_dir)
        assert any(
            "more than one archive commit" in error
            or "not exactly one commit" in error
            or "one direct archive commit" in error
            for error in errors
        )


def test_sanitized_no_hardlink_clone_preflight_and_relocated_replay_scope() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        protocol = Path(decision["paths"]["protocol_repository_path"])
        _commit_all(protocol, "single exact evidence archive")
        clone = Path(temporary) / "sanitized-standalone-clone"
        subprocess.run(
            ["git", "clone", "-q", "--no-hardlinks", str(protocol), str(clone)],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        profile = decision["selective_worktree_profiles"]["protocol"]
        _seal_selective_worktree(clone, profile)
        assert checker._repository_git_preflight_errors(clone, profile) == []
        clone_head = _git(clone, "rev-parse", "HEAD")
        assert checker._protocol_repository_topology_errors(
            clone, clone_head, (), profile,
        ) == []

        clone_decision = clone / decision_path.relative_to(protocol)
        clone_run = clone / run_dir.relative_to(protocol)
        _, _, errors = checker.validate_dispatch_decision(
            clone_decision, "post-run", clone_run,
        )
        assert errors
        assert any(
            "supplied/exact decision path" in error
            or "protocol repository" in error
            or "original" in error
            for error in errors
        )


def test_active_package_lock_and_external_binary_hardlink_are_rejected() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        package_lock = Path(decision["paths"]["verifier_package_path"]) / "Cargo.lock"
        root_lock = Path(decision["paths"]["verifier_repository_path"]) / "Cargo.lock"
        assert b"crypto_lib" not in root_lock.read_bytes()
        package_lock.write_text(
            'version = 3\n\n[[package]]\nname = "verifier"\nversion = "0.1.0"\n'
            '[[package]]\nname = "crypto_lib"\nversion = "9.9.9"\n',
            encoding="utf-8",
        )
        audit_path = run_dir / "dependency-audit.json"
        audit = checker.decode_canonical_json(audit_path.read_bytes())
        audit["verifier_cargo_lock_sha256"] = checker.sha256_path(package_lock)
        _canonical(audit_path, audit)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any("Cargo.lock contains forbidden package crypto_lib" in error for error in errors)

    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        external = Path(temporary) / "external-producer-hardlink"
        os.link(decision["paths"]["producer_bin"], external)
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert any("link count is not one" in error for error in errors)


def test_failure_completion_requires_exact_schema_cardinality_and_truthful_cleanup() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = Path(decision["paths"]["run_dir"])
        run_dir.mkdir()
        control_dir = Path(decision["paths"]["control_dir"])
        control_dir.mkdir()
        _write_bytes(run_dir / "checkpoint-chain.jsonl", b"")
        assert not checker._schema_valid_completed_artifact(
            run_dir, "checkpoint-chain.jsonl", decision,
        )
        _canonical(run_dir / "candidate-stream.json", {
            "schema": "p192-wcm-role2-box0-environment-v1",
        })
        assert not checker._schema_valid_completed_artifact(
            run_dir, "candidate-stream.json", decision,
        )

        raw = {
            "schema": "p192-wcm-role2-box0-failure-v1",
            "experiment_id": "EXP-SCURVE-1a8daf", "run_id": decision["run_id"],
            "stage": "P192-WCM-BOX0", "decision_custody": custody,
            "protocol_commit": decision["protocol_commit"],
            "factor_base_source_commit": decision["factor_base_source_commit"],
            "producer_commit": decision["producer_commit"],
            "verifier_commit": decision["verifier_commit"],
            "supervisor_commit": decision["supervisor_commit"],
            "run_dir": str(run_dir), "control_dir": decision["paths"]["control_dir"],
            "control_state": "retained", "control_retained": True,
            "control_created_before_failure": True,
            "terminal_failure_custody": {
                "custody_check_id": "post_directory_creation_terminal_failure_v1",
                "inode_custody_scope": "original_supervised_workspace_only",
                "run_entries_before_failure_record": [],
                "control_directory_before_children": checker._directory_identity(control_dir),
                "control_directory_terminal": checker._directory_identity(control_dir),
                "control_entries": [],
                "failure_record_excluded_from_own_inventory": True,
                "pass_manifest_transition": "not_reached",
                "provisional_pass_manifest": None,
                "provisional_success_raw_result": None,
                "stale_pass_manifest_present_before_finalization": False,
                "stale_pass_manifest_removed": True,
                "pass_manifest_absent_after_finalization": True,
                "in_transaction_control_cleanup_performed": False,
            },
            "invalid_count": 0, "unresolved_count": 0,
            "failed_phase": "canonical_producer",
            "failure_reason": "incomplete_child_artifact", "completed_artifacts": [],
            "scientific_result": False, "scientific_results": [], "status": "INCOMPLETE",
        }
        _canonical(run_dir / "raw-result.json", raw)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any(
            "stale PASS manifest removal truthfulness" in error
            or "stale_pass_manifest_removed" in error
            for error in errors
        )


def test_failure_manifest_transition_is_phase_bound_and_hashes_provisional_state() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        sample_record = {"path": "manifest.yaml", "byte_length": 1, "sha256": "a" * 64}
        sample_raw = {"path": "raw-result.json", "byte_length": 1, "sha256": "b" * 64}
        base = {
            "schema": "p192-wcm-role2-box0-failure-v1",
            "experiment_id": "EXP-SCURVE-1a8daf", "run_id": decision["run_id"],
            "stage": "P192-WCM-BOX0", "decision_custody": custody,
            "protocol_commit": decision["protocol_commit"],
            "factor_base_source_commit": decision["factor_base_source_commit"],
            "producer_commit": decision["producer_commit"],
            "verifier_commit": decision["verifier_commit"],
            "supervisor_commit": decision["supervisor_commit"],
            "run_dir": decision["paths"]["run_dir"],
            "control_dir": decision["paths"]["control_dir"],
            "control_state": "retained", "control_retained": True,
            "control_created_before_failure": True,
            "terminal_failure_custody": {
                "custody_check_id": "post_directory_creation_terminal_failure_v1",
                "inode_custody_scope": "original_supervised_workspace_only",
                "run_entries_before_failure_record": [],
                "control_directory_before_children": {
                    "path": decision["paths"]["control_dir"],
                    "device": "1", "inode": "1",
                },
                "control_directory_terminal": {
                    "path": decision["paths"]["control_dir"],
                    "device": "1", "inode": "1",
                },
                "control_entries": [],
                "failure_record_excluded_from_own_inventory": True,
                "pass_manifest_transition": "post_manifest_failure_cleanup",
                "provisional_pass_manifest": sample_record,
                "provisional_success_raw_result": sample_raw,
                "stale_pass_manifest_present_before_finalization": True,
                "stale_pass_manifest_removed": True,
                "pass_manifest_absent_after_finalization": True,
                "in_transaction_control_cleanup_performed": False,
            },
            "invalid_count": 0, "unresolved_count": 0,
            "failure_reason": "incomplete_child_artifact",
            "completed_artifacts": [], "scientific_result": False,
            "scientific_results": [], "status": "INCOMPLETE",
        }
        for phase in (
            "canonical_producer", "restart_control",
            "independent_verifier", "agreement",
        ):
            document = copy.deepcopy(base)
            document["failed_phase"] = phase
            errors = checker.validate_artifact_document(document)
            assert errors, phase
            assert any(
                "pass_manifest_transition" in error
                or "stale_pass_manifest" in error
                or "provisional_pass_manifest" in error
                for error in errors
            ), (phase, errors)

    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = _build_valid_run(decision, custody)
        control_dir = Path(decision["paths"]["control_dir"])
        provisional_manifest = _artifact_for(run_dir, "manifest.yaml")
        provisional_success_raw = _artifact_for(run_dir, "raw-result.json")
        (run_dir / checker.TERMINAL_CUSTODY_PATH).unlink()
        (run_dir / "manifest.yaml").unlink()
        completed = [
            _artifact_for(run_dir, relative)
            for relative in checker.FAILURE_COMPLETION_ORDER
            if checker._schema_valid_completed_artifact(run_dir, relative, decision)
        ]
        failure = {
            "schema": "p192-wcm-role2-box0-failure-v1",
            "experiment_id": "EXP-SCURVE-1a8daf", "run_id": decision["run_id"],
            "stage": "P192-WCM-BOX0", "decision_custody": custody,
            "protocol_commit": decision["protocol_commit"],
            "factor_base_source_commit": decision["factor_base_source_commit"],
            "producer_commit": decision["producer_commit"],
            "verifier_commit": decision["verifier_commit"],
            "supervisor_commit": decision["supervisor_commit"],
            "run_dir": str(run_dir), "control_dir": str(control_dir),
            "control_state": "retained", "control_retained": True,
            "control_created_before_failure": True,
            "terminal_failure_custody": {
                "custody_check_id": "post_directory_creation_terminal_failure_v1",
                "inode_custody_scope": "original_supervised_workspace_only",
                "run_entries_before_failure_record": [
                    record for record in checker._directory_custody_entries(run_dir)
                    if record["path"] != "raw-result.json"
                ],
                "control_directory_before_children": checker._directory_identity(control_dir),
                "control_directory_terminal": checker._directory_identity(control_dir),
                "control_entries": checker._directory_custody_entries(control_dir),
                "failure_record_excluded_from_own_inventory": True,
                "pass_manifest_transition": "post_manifest_failure_cleanup",
                "provisional_pass_manifest": provisional_manifest,
                "provisional_success_raw_result": provisional_success_raw,
                "stale_pass_manifest_present_before_finalization": True,
                "stale_pass_manifest_removed": True,
                "pass_manifest_absent_after_finalization": True,
                "in_transaction_control_cleanup_performed": False,
            },
            "invalid_count": 0, "unresolved_count": 0,
            "failed_phase": "final_custody", "failure_reason": "custody_failure",
            "completed_artifacts": completed, "scientific_result": False,
            "scientific_results": [], "status": "FAIL",
        }
        _canonical(run_dir / "raw-result.json", failure)
        assert checker.validate_post_run(run_dir, decision, custody) == []


def test_verifier_compiler_inputs_reject_target_build_and_rust_include_escapes() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        package = root / "verifier"
        _write_bytes(package / "src/main.rs", b"fn main() {}\n")
        baseline = (
            b"[workspace]\n[package]\nname='verifier'\nversion='0.1.0'\n"
            b"autobins=false\nautoexamples=false\nautotests=false\nautobenches=false\n"
            b"[[bin]]\nname='p192_weighted_cm_verify'\npath='src/main.rs'\n"
        )
        _write_bytes(package / "Cargo.toml", baseline)
        assert checker._verifier_compiler_input_errors(baseline, package) == []

        outside = root / "outside.rs"
        _write_bytes(outside, b"fn main() {}\n")
        for fragment, marker in (
            (b"[[bin]]\nname='p192_weighted_cm_verify'\npath='../outside.rs'\n", "normalized package-relative"),
            (b"build='../outside.rs'\n", "normalized package-relative"),
        ):
            manifest = b"[workspace]\n[package]\nname='verifier'\nversion='0.1.0'\n" + fragment
            errors = checker._verifier_compiler_input_errors(manifest, package)
            assert any(marker in error or "escapes the verifier package" in error for error in errors)

        linked = package / "src/linked.rs"
        linked.symlink_to(outside)
        manifest = baseline.replace(b"src/main.rs", b"src/linked.rs")
        errors = checker._verifier_compiler_input_errors(manifest, package)
        assert any("symlink component" in error for error in errors)
        linked.unlink()

        attacks = {
            "include": b"include /* comment */ ! (\"../outside.rs\");\nfn main() {}\n",
            "include_bytes": b"const X: &[u8] = include_bytes /*x*/ ! (\"../outside.rs\");\nfn main() {}\n",
            "include_str": b"const X: &str = include_str! (\"../outside.rs\");\nfn main() {}\n",
            "core_alias": b"use core::include as hidden; hidden!(\"../outside.rs\");\nfn main() {}\n",
            "std_group_alias": b"pub use std::{include_bytes as hidden}; const X: &[u8] = hidden!(\"../outside.rs\");\nfn main() {}\n",
            "underscore_reexport": b"use core::include_str as _;\nfn main() {}\n",
            "raw_identifier": b"use core::r#include as hidden; hidden!(\"../outside.rs\");\nfn main() {}\n",
            "macro_forwarder": b"macro_rules! hidden { ($p:expr) => { include!($p) } }\nhidden!(\"../outside.rs\");\nfn main() {}\n",
            "path": b"# [ path /*x*/ = \"../outside.rs\" ] mod hidden;\nfn main() {}\n",
            "cfg_attr": b"#[cfg_attr(any(), path = \"../outside.rs\")] mod hidden;\nfn main() {}\n",
            "out_dir": b"const X: &str = env!(\"OUT_DIR\");\nfn main() {}\n",
        }
        for name, source in attacks.items():
            _write_bytes(package / "src/main.rs", source)
            errors = checker._verifier_compiler_input_errors(baseline, package)
            assert errors, name
            assert any(
                "forbidden local-input macro" in error
                or "forbidden #[path]/cfg_attr(path)" in error
                or "OUT_DIR" in error
                for error in errors
            ), (name, errors)

        _write_bytes(package / "src/main.rs", b"fn main() {}\n")
        proc_macro = baseline + b"\n[lib]\nproc-macro=true\npath='src/main.rs'\n"
        assert any(
            "proc-macro" in error
            for error in checker._verifier_compiler_input_errors(proc_macro, package)
        )


def test_verifier_selected_bin_dep_info_rejects_external_and_uncommitted_inputs() -> None:
    for attack in ("external", "uncommitted"):
        with tempfile.TemporaryDirectory() as temporary:
            _, decision, _ = _committed_decision_fixture(Path(temporary))
            package = Path(decision["paths"]["verifier_package_path"])
            admission = decision["verifier_build_admission"]
            dep_info = Path(admission["selected_bin_dep_info"]["identity"]["path"])
            if attack == "external":
                injected = Path(temporary) / "outside.rs"
            else:
                injected = package / "src/uncommitted.rs"
            _write_bytes(injected, b"pub fn injected() {}\n")
            _write_bytes(
                dep_info,
                f"{dep_info.with_suffix('')}: {package / 'src/main.rs'} {injected}\n".encode(),
            )
            admission["selected_bin_dep_info"] = {
                "identity": checker._file_identity(dep_info),
                "local_inputs": sorted(
                    [checker._file_identity(package / "src/main.rs"), checker._file_identity(injected)],
                    key=lambda item: item["path"].encode(),
                ),
            }
            errors = checker._verifier_build_admission_errors(decision, runtime=True)
            assert any(
                "dep-info input escapes bound package" in error
                or "dep-info input is absent from committed inventory" in error
                or "package file inventory" in error
                for error in errors
            ), (attack, errors)


def test_source_build_inventory_rejects_empty_directories_hardlinks_and_clean_filters() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        repository, package, commit = _implementation_checkout(
            root, "producer", ("tools", "p192-weighted-cm"),
        )
        (package / "rogue-empty").mkdir()
        errors: list[str] = []
        checker._source_build_input_rows(repository, package, commit, "producer", errors)
        assert any("package directory inventory" in error for error in errors)
        (package / "rogue-empty").rmdir()

        external = root / "external-hardlink"
        os.link(package / "src/lib.rs", external)
        errors = []
        checker._source_build_input_rows(repository, package, commit, "producer", errors)
        assert any("link count is not one" in error for error in errors)
        external.unlink()

        _write_bytes(repository / ".gitattributes", b"*.rs filter=hide\n")
        _git(repository, "add", ".gitattributes")
        _git(repository, "commit", "-q", "-m", "attribute attack baseline")
        commit = _git(repository, "rev-parse", "HEAD")
        _git(repository, "config", "filter.hide.clean", "sed s/MUTATED/producer/")
        (package / "src/lib.rs").write_text("pub fn MUTATED() {}\n", encoding="utf-8")
        errors = []
        checker._source_build_input_rows(repository, package, commit, "producer", errors)
        assert any("Git/working bytes" in error for error in errors)


def test_verifier_build_admission_binds_tools_env_configs_metadata_and_targets() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _ = _committed_decision_fixture(Path(temporary))
        _, _, errors = _fixture_dispatch(decision_path, "pre-dispatch")
        assert errors == []

        cargo_home = Path(decision["verifier_build_admission"]["cargo_home"])
        _write_bytes(cargo_home / "config.toml", b"[source.crates-io]\nreplace-with='evil'\n")
        errors = checker._verifier_build_admission_errors(decision, runtime=True)
        assert any("configuration/source override exists" in error for error in errors)
        (cargo_home / "config.toml").unlink()

        decision["verifier_build_admission"]["environment"]["RUSTFLAGS"] = "-C linker=/tmp/evil"
        errors = checker.validate_decision(decision)
        assert any("Additional properties are not allowed" in error for error in errors)

    with tempfile.TemporaryDirectory() as temporary:
        _, decision, _ = _committed_decision_fixture(Path(temporary))
        admission = decision["verifier_build_admission"]
        package = Path(decision["paths"]["verifier_package_path"])
        cargo = Path(admission["cargo_identity"]["path"])
        outside = Path(temporary) / "outside.rs"
        _write_bytes(outside, b"fn main() {}\n")
        metadata = {
            "packages": [{
                "id": admission["cargo_metadata_root_package_id"],
                "targets": [{
                    "name": "p192_weighted_cm_verify", "kind": ["bin"],
                    "crate_types": ["bin"], "src_path": str(outside),
                    "edition": "2015", "required-features": [],
                }],
            }],
            "workspace_members": [admission["cargo_metadata_root_package_id"]],
            "workspace_root": str(package), "resolve": {"nodes": []},
        }
        raw = json.dumps(metadata, separators=(",", ":"), sort_keys=True).encode()
        _write_bytes(cargo, b"#!/bin/sh\nprintf '%s' '" + raw + b"'\n", executable=True)
        admission["cargo_identity"] = checker._file_identity(cargo)
        admission["cargo_metadata_byte_length"] = len(raw)
        admission["cargo_metadata_sha256"] = checker.sha256_bytes(raw)
        admission["cargo_metadata_root_targets"] = checker._metadata_root_target_rows(
            metadata, admission["cargo_metadata_root_package_id"],
        )
        admission["cargo_metadata_resolve_sha256"] = checker.sha256_bytes(
            checker.canonical_json_bytes(metadata["resolve"])
        )
        errors = checker._verifier_build_admission_errors(decision, runtime=True)
        assert any("root target escapes package" in error for error in errors)


def test_failure_custody_rejects_nested_mutation_and_nonregular_or_aliased_leaves() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = Path(decision["paths"]["run_dir"])
        nested = run_dir / "unknown.partial"
        _write_bytes(nested / "unrecorded.bin", b"A")
        control_dir = Path(decision["paths"]["control_dir"])
        control_dir.mkdir()
        raw = {
            "schema": "p192-wcm-role2-box0-failure-v1",
            "experiment_id": "EXP-SCURVE-1a8daf", "run_id": decision["run_id"],
            "stage": "P192-WCM-BOX0", "decision_custody": custody,
            "protocol_commit": decision["protocol_commit"],
            "factor_base_source_commit": decision["factor_base_source_commit"],
            "producer_commit": decision["producer_commit"],
            "verifier_commit": decision["verifier_commit"],
            "supervisor_commit": decision["supervisor_commit"],
            "run_dir": str(run_dir), "control_dir": decision["paths"]["control_dir"],
            "control_state": "retained", "control_retained": True,
            "control_created_before_failure": True,
            "invalid_count": 0, "unresolved_count": 0,
            "failed_phase": "canonical_producer",
            "failure_reason": "incomplete_child_artifact",
            "completed_artifacts": [], "scientific_result": False,
            "scientific_results": [], "status": "INCOMPLETE",
        }
        raw["terminal_failure_custody"] = {
            "custody_check_id": "post_directory_creation_terminal_failure_v1",
            "inode_custody_scope": "original_supervised_workspace_only",
            "run_entries_before_failure_record": checker._directory_custody_entries(run_dir),
            "control_directory_before_children": checker._directory_identity(control_dir),
            "control_directory_terminal": checker._directory_identity(control_dir),
            "control_entries": [], "failure_record_excluded_from_own_inventory": True,
            "pass_manifest_transition": "not_reached", "provisional_pass_manifest": None,
            "provisional_success_raw_result": None,
            "stale_pass_manifest_present_before_finalization": False,
            "stale_pass_manifest_removed": False,
            "pass_manifest_absent_after_finalization": True,
            "in_transaction_control_cleanup_performed": False,
        }
        _canonical(run_dir / "raw-result.json", raw)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any(
            "flat regular leaf" in error or "nonregular leaf" in error
            for error in errors
        )
        _write_bytes(nested / "unrecorded.bin", b"changed after finalization")
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any(
            "flat regular leaf" in error or "nonregular leaf" in error
            for error in errors
        )
        _write_bytes(nested / "added.bin", b"new")
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any(
            "flat regular leaf" in error or "nonregular leaf" in error
            for error in errors
        )

    with tempfile.TemporaryDirectory() as temporary:
        _, decision, custody = _committed_decision_fixture(Path(temporary))
        run_dir = Path(decision["paths"]["run_dir"])
        run_dir.mkdir()
        control_dir = Path(decision["paths"]["control_dir"])
        control_dir.mkdir()
        os.link(Path(decision["paths"]["predecessor_dir"]) / "factor-base.json", run_dir / "alias.bin")
        raw = {
            "schema": "p192-wcm-role2-box0-failure-v1",
            "experiment_id": "EXP-SCURVE-1a8daf", "run_id": decision["run_id"],
            "stage": "P192-WCM-BOX0", "decision_custody": custody,
            "protocol_commit": decision["protocol_commit"],
            "factor_base_source_commit": decision["factor_base_source_commit"],
            "producer_commit": decision["producer_commit"], "verifier_commit": decision["verifier_commit"],
            "supervisor_commit": decision["supervisor_commit"], "run_dir": str(run_dir),
            "control_dir": decision["paths"]["control_dir"], "control_state": "retained",
            "control_retained": True, "control_created_before_failure": True,
            "invalid_count": 0, "unresolved_count": 0, "failed_phase": "canonical_producer",
            "failure_reason": "incomplete_child_artifact", "completed_artifacts": [],
            "scientific_result": False, "scientific_results": [], "status": "INCOMPLETE",
        }
        raw["terminal_failure_custody"] = {
            "custody_check_id": "post_directory_creation_terminal_failure_v1",
            "inode_custody_scope": "original_supervised_workspace_only",
            "run_entries_before_failure_record": checker._directory_custody_entries(run_dir),
            "control_directory_before_children": checker._directory_identity(control_dir),
            "control_directory_terminal": checker._directory_identity(control_dir),
            "control_entries": [], "failure_record_excluded_from_own_inventory": True,
            "pass_manifest_transition": "not_reached", "provisional_pass_manifest": None,
            "provisional_success_raw_result": None,
            "stale_pass_manifest_present_before_finalization": False,
            "stale_pass_manifest_removed": False,
            "pass_manifest_absent_after_finalization": True,
            "in_transaction_control_cleanup_performed": False,
        }
        _canonical(run_dir / "raw-result.json", raw)
        errors = checker.validate_post_run(run_dir, decision, custody)
        assert any(
            "link count one" in error
            or "link count is not one" in error
            or "aliases an immutable input" in error
            for error in errors
        )


def test_failure_phase_chronology_requires_semantic_pass_not_schema_only() -> None:
    cases = (
        ("restart_control", "verification.json", "producer", "restart_mismatch"),
        ("restart_control", "candidate-stream.json", "producer_root", "restart_mismatch"),
        ("independent_verifier", "checkpoint-resume-control.json", "restart", "verification_failure"),
        ("agreement", "independent-verification.json", "independent", "verification_failure"),
        ("final_custody", "independent-agreement.json", "agreement", "custody_failure"),
        ("final_custody", "independent-verifier-receipt.json", "receipt", "custody_failure"),
    )
    for phase, relative, mutation, reason in cases:
        with tempfile.TemporaryDirectory() as temporary:
            _, decision, custody = _committed_decision_fixture(Path(temporary))
            run_dir = _build_valid_run(decision, custody)
            path = run_dir / relative
            document = checker.decode_canonical_json(path.read_bytes())
            if mutation == "producer":
                document["checks"][-1]["status"] = "FAIL"
                document["overall_status"] = "FAIL"
            elif mutation == "producer_root":
                document["candidate_shell_sha256"] = "0" * 64
            elif mutation == "restart":
                document["comparisons"][0]["resumed_sha256"] = "0" * 64
                document["comparisons"][0]["equal"] = False
                document["roots_equal"] = False
                document["overall_status"] = "FAIL"
            elif mutation == "independent":
                document["checks"][-1]["status"] = "FAIL"
                document["overall_status"] = "FAIL"
            elif mutation == "agreement":
                document["comparisons"][0]["verifier"] = "wrong"
                document["comparisons"][0]["equal"] = False
                document["overall_status"] = "FAIL"
            else:
                document["children"][0]["observed_exit_code"] = 1
                document["overall_status"] = "FAIL"
            _canonical(path, document)
            if mutation == "producer_root":
                verification_path = run_dir / "verification.json"
                verification = checker.decode_canonical_json(verification_path.read_bytes())
                verification["bindings"] = checker._binding_values_from_candidate(document)
                for record in verification["artifacts"]:
                    if record["path"] == "candidate-stream.json":
                        record.update(_artifact_for(run_dir, "candidate-stream.json"))
                _canonical(verification_path, verification)
            _replace_success_with_failure(run_dir, decision, custody, phase, reason)
            errors = checker.validate_post_run(run_dir, decision, custody)
            assert errors, (phase, mutation)
            assert any(
                "failure prior" in error
                or "canonical-producer" in error
                or "failure completed receipt status" in error
                for error in errors
            ), (phase, mutation, errors)


def test_interface_files_do_not_contain_result_or_authorization_state() -> None:
    addendum = yaml.safe_load(checker.ADDENDUM.read_text())["role2_box0_interface_addendum"]
    overlay = yaml.safe_load(checker.OVERLAY.read_text())
    assert addendum["interface_revision"] == 3
    assert addendum["supersedes_unexecuted_revision"] == 2
    assert addendum["execution_authorized"] is False
    assert addendum["scientific_status"] == "not_started"
    assert addendum["scientific_results"] == []
    assert overlay["interface_revision"] == 3
    assert overlay["supersedes_unexecuted_revision"] == 2
    assert overlay["execution_authorized"] is False
    assert overlay["scientific_results"] == []


def test_source_target_root_must_be_untracked_even_when_profile_selects_it() -> None:
    for mutation in ("absent", "modified"):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository, package, _ = _implementation_checkout(
                base, "producer", ("tools", "p192-weighted-cm"),
            )
            tracked_target = package / "target/tracked.bin"
            _write_bytes(tracked_target, b"tracked build output\n")
            commit = _commit_all(repository, "track forbidden target output")
            profile = checker.selective_worktree_profiles(_decision())["source"]
            _seal_selective_worktree(repository, profile)
            if mutation == "absent":
                tracked_target.unlink()
            else:
                _write_bytes(tracked_target, b"mutated build output\n")
            errors: list[str] = []
            checker._validate_git_checkout(
                repository, package, commit,
                ("tools", "p192-weighted-cm"), profile, "producer", errors,
            )
            assert any(
                "tracked paths beneath a mutable output root" in error
                for error in errors
            ), (mutation, errors)


def test_terminal_git_batch_handles_large_first_object_without_pipe_deadlock() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        repository = Path(temporary) / "repo"
        _init_repository(repository)
        payloads = {
            "large.bin": b"L" * (2 * 1024 * 1024 + 17),
            "empty.bin": b"",
            "tiny.bin": b"tiny\n",
        }
        for relative, payload in payloads.items():
            _write_bytes(repository / relative, payload)
        _commit_all(repository, "batch payloads")
        object_ids = {
            relative: _git(repository, "rev-parse", f"HEAD:{relative}")
            for relative in payloads
        }
        sizes = {
            object_id: len(payloads[relative])
            for relative, object_id in object_ids.items()
        }
        bindings = {
            object_id: [(repository / relative, relative)]
            for relative, object_id in object_ids.items()
        }
        errors: list[str] = []
        observed = checker._stream_git_blob_batch_file_equality(
            repository, sizes, bindings, "large-first batch", errors,
            object_kinds={object_id: "blob" for object_id in sizes},
            expected_payload_sha256={
                object_ids[relative]: hashlib.sha256(payload).hexdigest()
                for relative, payload in payloads.items()
            },
        )
        assert errors == []
        assert observed == {
            object_ids[relative]: hashlib.sha256(payload).hexdigest()
            for relative, payload in payloads.items()
        }


def test_topology_selected_leaf_uses_streamed_digest_and_detects_mutation() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        repository = Path(temporary) / "repo"
        _init_repository(repository)
        selected_path = repository / "selected.bin"
        _write_bytes(selected_path, b"selected bytes\n")
        head = _commit_all(repository, "selected leaf")
        profile = {
            "profile_id": "test-v1",
            "materialized_exact_paths": ["selected.bin"],
            "materialized_subtree_prefixes": [],
            "required_existing_subtree_prefixes": [],
            "mutable_output_subtree_prefixes": [],
            "mutable_output_exact_paths": [],
        }
        _seal_selective_worktree(repository, profile)
        assert checker._protocol_repository_topology_errors(
            repository, head, (), profile,
        ) == []
        _write_bytes(selected_path, b"mutated bytes\n")
        errors = checker._protocol_repository_topology_errors(
            repository, head, (), profile,
        )
        assert any(
            "selected file" in error
            or "worktree SHA-256" in error
            or "worktree exact" in error
            for error in errors
        )


def test_raw_v3_index_rejects_intent_extensions_order_and_nonzero_padding() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        repository = Path(temporary) / "repo"
        _init_repository(repository)
        _write_bytes(repository / "aa", b"")
        _write_bytes(repository / "bb", b"bb\n")
        _commit_all(repository, "two index entries")
        profile = {
            "profile_id": "test-v1",
            "materialized_exact_paths": ["aa"],
            "materialized_subtree_prefixes": [],
            "required_existing_subtree_prefixes": [],
            "mutable_output_subtree_prefixes": [],
            "mutable_output_exact_paths": [],
        }
        _seal_selective_worktree(repository, profile)
        head_errors: list[str] = []
        head = checker._raw_protocol_head_tree(
            repository, _git(repository, "rev-parse", "HEAD"), head_errors,
        )
        assert head_errors == [] and head is not None
        selected = {"aa"}
        index_path = repository / ".git/index"
        baseline = index_path.read_bytes()
        assert checker._raw_index_v3_flag_errors(
            repository, head, selected, "baseline",
        ) == []

        def spans(raw: bytes) -> tuple[list[tuple[int, int, int, int]], int]:
            body = raw[:-20]
            offset = 12
            found: list[tuple[int, int, int, int]] = []
            for _ in range(int.from_bytes(body[8:12], "big")):
                start = offset
                flags = int.from_bytes(body[offset + 60:offset + 62], "big")
                offset += 62
                extended_offset = -1
                if flags & 0x4000:
                    extended_offset = offset
                    offset += 2
                nul = body.index(b"\0", offset)
                end = start + (((nul + 1 - start) + 7) & ~7)
                found.append((start, end, nul, extended_offset))
                offset = end
            return found, offset

        def install(body: bytes) -> list[str]:
            index_path.write_bytes(body + hashlib.sha1(body).digest())
            return checker._raw_index_v3_flag_errors(
                repository, head, selected, "adversarial",
            )

        baseline_body = baseline[:-20]
        entry_spans, entries_end = spans(baseline)
        assert len(entry_spans) == 2 and entries_end == len(baseline_body)

        extension_errors = install(baseline_body + b"TREE" + (0).to_bytes(4, "big"))
        assert any("extension absence" in error for error in extension_errors)

        reversed_body = (
            baseline_body[:12]
            + baseline_body[entry_spans[1][0]:entry_spans[1][1]]
            + baseline_body[entry_spans[0][0]:entry_spans[0][1]]
        )
        order_errors = install(reversed_body)
        assert any("path order" in error for error in order_errors)

        padded = bytearray(baseline_body)
        first_start, first_end, first_nul, _ = entry_spans[0]
        assert first_end > first_nul + 1 and first_start < first_end
        padded[first_nul + 1] = 1
        padding_errors = install(bytes(padded))
        assert any("padding is nonzero" in error for error in padding_errors)

        intent = bytearray(baseline_body)
        omitted = next(row for row in entry_spans if row[3] >= 0)
        intent[omitted[3]:omitted[3] + 2] = (0x6000).to_bytes(2, "big")
        intent_errors = install(bytes(intent))
        assert any("extended flags" in error for error in intent_errors)


def test_cross_repository_shared_base_payload_map_is_not_oid_only() -> None:
    cases = (
        (
            "Role-1 shared-base execution payloads",
            "shared protocol base selected/policy blob SHA-256 custody map",
        ),
        (
            "terminal Role-1 shared-base execution payloads",
            "terminal Role-1 shared-base payload custody stability",
        ),
    )
    for attacked_label, expected_error in cases:
        with tempfile.TemporaryDirectory() as temporary:
            decision_path, _decision_value, _custody = _committed_decision_fixture(
                Path(temporary),
            )
            original = checker._git_blob_payload_custody_map

            def forged_map(
                repository: Path, object_ids: object, label: str,
                errors: list[str],
            ) -> list[dict] | None:
                rows = original(repository, object_ids, label, errors)
                if rows and label == attacked_label:
                    rows = copy.deepcopy(rows)
                    rows[0]["sha256"] = "0" * 64
                return rows

            checker._git_blob_payload_custody_map = forged_map
            try:
                _parsed, _observed, errors = _fixture_dispatch(
                    decision_path, "pre-dispatch",
                )
            finally:
                checker._git_blob_payload_custody_map = original
            assert any(expected_error in error for error in errors), (
                attacked_label, errors,
            )


def test_role1_custody_staging_parent_and_repository_isolation_are_enforced() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _custody = _committed_decision_fixture(
            Path(temporary),
        )
        staging_parent = Path(
            decision["predecessor_repository_custody"][
                "pre_execution_retained_path"
            ]
        ).parent
        staging_parent.chmod(0o755)
        _parsed, _observed, errors = _fixture_dispatch(
            decision_path, "pre-dispatch",
        )
        assert any("staging-parent identity" in error for error in errors)

    with tempfile.TemporaryDirectory() as temporary:
        decision_path, decision, _custody = _committed_decision_fixture(
            Path(temporary),
        )
        decision["paths"]["supervisor_repository_path"] = decision["paths"][
            "producer_repository_path"
        ]
        decision["paths"]["supervisor_package_path"] = str(
            Path(decision["paths"]["producer_repository_path"])
            / "tools/p192-weighted-cm-supervisor"
        )
        decision.update(checker.resolved_argv(decision))
        _canonical(decision_path, decision)
        protocol = Path(decision["paths"]["protocol_repository_path"])
        _git(protocol, "add", str(decision_path.relative_to(protocol)))
        _git(protocol, "commit", "--amend", "-q", "--no-edit")
        _seal_selective_worktree(
            protocol, decision["selective_worktree_profiles"]["protocol"],
        )
        _parsed, _observed, errors = _fixture_dispatch(
            decision_path, "pre-dispatch",
        )
        assert any("repositories overlap" in error for error in errors)


def test_full_post_run_terminal_batch_includes_historical_protocol_objects() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        _decision_path, decision, custody = _committed_decision_fixture(
            Path(temporary),
        )
        run_dir = _build_valid_run(decision, custody)
        repository = Path(decision["paths"]["protocol_repository_path"])
        historical_object = decision["protocol_commit"]
        loose = repository / ".git/objects" / historical_object[:2] / historical_object[2:]
        original_raw = loose.read_bytes()
        original_mode = stat.S_IMODE(loose.stat().st_mode)
        original = checker._stream_git_blob_batch_file_equality
        calls = 0

        def corrupt_before_final_batch(*args: object, **kwargs: object) -> object:
            nonlocal calls
            label = str(args[3])
            if label.startswith("untracked evidence terminal admitted-object batch"):
                calls += 1
                if calls == 3:
                    loose.chmod(0o600)
                    loose.write_bytes(b"corrupt historical object")
                    try:
                        return original(*args, **kwargs)
                    finally:
                        loose.write_bytes(original_raw)
                        loose.chmod(original_mode)
            return original(*args, **kwargs)

        checker._stream_git_blob_batch_file_equality = corrupt_before_final_batch
        try:
            errors = checker.validate_post_run(run_dir, decision, custody)
        finally:
            checker._stream_git_blob_batch_file_equality = original
            loose.chmod(0o600)
            loose.write_bytes(original_raw)
            loose.chmod(original_mode)
        assert calls >= 3
        assert any(
            "terminal admitted-object batch" in error
            or "protocol output" in error
            or "terminal protocol output-state stability" in error
            for error in errors
        ), errors


def test_sealed_repository_receipt_rechecks_selected_and_rogue_worktree_state() -> None:
    for mutation in ("selected", "rogue"):
        with tempfile.TemporaryDirectory() as temporary:
            _decision_path, decision, _custody = _committed_decision_fixture(
                Path(temporary),
            )
            repository = Path(decision["paths"]["predecessor_repository_path"])
            head = decision["predecessor_role1"]["archive_commit"]
            profile = decision["selective_worktree_profiles"]["predecessor"]
            selected_path = repository / checker.PROTECTED_PROTOCOL_RELATIVE_PATHS[
                "check_role2_box0_interface.py"
            ]
            selected_raw = selected_path.read_bytes()
            rogue = repository / "rogue-after-policy.txt"
            original = checker._protocol_repository_topology_errors
            calls = 0

            def mutate_after_terminal_topology(*args: object, **kwargs: object) -> list[str]:
                nonlocal calls
                result = original(*args, **kwargs)
                if Path(args[0]) == repository:
                    calls += 1
                    if calls == 2:
                        if mutation == "selected":
                            selected_path.write_bytes(selected_raw + b"late\n")
                        else:
                            rogue.write_bytes(b"late rogue\n")
                return result

            checker._protocol_repository_topology_errors = mutate_after_terminal_topology
            errors: list[str] = []
            try:
                receipt = checker._sealed_repository_custody_receipt(
                    repository, head, profile, "terminal_role1_archive", errors,
                )
            finally:
                checker._protocol_repository_topology_errors = original
                selected_path.write_bytes(selected_raw)
                if rogue.exists():
                    rogue.unlink()
            assert calls >= 2
            assert receipt is None
            assert errors, mutation


def test_evidence_size_gates_are_inclusive_and_path_weighted() -> None:
    def sparse(path: Path, size: int) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.ftruncate(descriptor, size)
        finally:
            os.close(descriptor)

    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        run_dir = base / "run"
        control_dir = base / "control"
        run_dir.mkdir()
        control_dir.mkdir()
        sparse(
            run_dir / "retained-candidates.jsonl",
            checker.EVIDENCE_ARTIFACT_BYTE_CAP,
        )
        assert checker._evidence_size_errors(run_dir, control_dir) == []
        os.truncate(
            run_dir / "retained-candidates.jsonl",
            checker.EVIDENCE_ARTIFACT_BYTE_CAP + 1,
        )
        errors = checker._evidence_size_errors(run_dir, control_dir)
        assert any("exceeds 512 MiB" in error for error in errors)

    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        run_dir = base / "run"
        control_dir = base / "control"
        run_dir.mkdir()
        control_dir.mkdir()
        first = checker.EVIDENCE_ARTIFACT_BYTE_CAP
        second = checker.PRODUCER_TREE_BYTE_CAP - first
        sparse(run_dir / "retained-candidates.jsonl", first)
        sparse(run_dir / "complete-relations.jsonl", second)
        assert checker._evidence_size_errors(run_dir, control_dir) == []
        os.truncate(run_dir / "complete-relations.jsonl", second + 1)
        errors = checker._evidence_size_errors(run_dir, control_dir)
        assert any("producer tree exceeds 844 MiB" in error for error in errors)

    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        run_dir = base / "run"
        control_dir = base / "control"
        run_dir.mkdir()
        control_dir.mkdir()
        sparse(run_dir / "receipt-metadata.json", checker.RUN_METADATA_BYTE_CAP)
        assert checker._evidence_size_errors(run_dir, control_dir) == []
        os.truncate(
            run_dir / "receipt-metadata.json", checker.RUN_METADATA_BYTE_CAP + 1,
        )
        errors = checker._evidence_size_errors(run_dir, control_dir)
        assert any("nonproducer metadata exceeds 64 MiB" in error for error in errors)

    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        run_dir = base / "run"
        control_dir = base / "control"
        run_dir.mkdir()
        control_dir.mkdir()
        producer_first = checker.EVIDENCE_ARTIFACT_BYTE_CAP
        producer_second = checker.PRODUCER_TREE_BYTE_CAP - producer_first
        metadata = checker.EVIDENCE_TREE_BYTE_CAP - checker.PRODUCER_TREE_BYTE_CAP
        for root in (run_dir, control_dir):
            sparse(root / "retained-candidates.jsonl", producer_first)
            sparse(root / "complete-relations.jsonl", producer_second)
            sparse(root / "tree-metadata.bin", metadata)
        assert checker._evidence_size_errors(run_dir, control_dir) == []
        os.truncate(run_dir / "tree-metadata.bin", metadata + 1)
        errors = checker._evidence_size_errors(run_dir, control_dir)
        assert any("RUN_DIR tree exceeds 896 MiB" in error for error in errors)
        assert any("combined RUN_DIR/CONTROL_DIR evidence exceeds 1792 MiB" in error for error in errors)
        os.truncate(run_dir / "tree-metadata.bin", metadata)
        os.truncate(control_dir / "tree-metadata.bin", metadata + 1)
        errors = checker._evidence_size_errors(run_dir, control_dir)
        assert any("CONTROL_DIR tree exceeds 896 MiB" in error for error in errors)
        assert any("combined RUN_DIR/CONTROL_DIR evidence exceeds 1792 MiB" in error for error in errors)

    object_a = "a" * 40
    object_b = "b" * 40
    object_c = "c" * 40
    assert checker._distinct_blob_payload_size_errors(
        {
            object_a: checker.EVIDENCE_ARTIFACT_BYTE_CAP,
            object_b: checker.EVIDENCE_ARTIFACT_BYTE_CAP,
        },
        "exact distinct boundary",
    ) == []
    distinct_errors = checker._distinct_blob_payload_size_errors(
        {
            object_a: checker.EVIDENCE_ARTIFACT_BYTE_CAP,
            object_b: checker.EVIDENCE_ARTIFACT_BYTE_CAP,
            object_c: 1,
        },
        "distinct boundary plus one",
    )
    assert any("distinct blob payload exceeds 1 GiB" in error for error in distinct_errors)
    per_object_errors = checker._distinct_blob_payload_size_errors(
        {object_a: checker.EVIDENCE_ARTIFACT_BYTE_CAP + 1},
        "per-object boundary plus one",
    )
    assert any("blob exceeds 512 MiB" in error for error in per_object_errors)

    with tempfile.TemporaryDirectory() as temporary:
        # Both sparse leaves are byte-identical all-zero payloads.  The
        # filesystem gate counts their two paths, while the committed-object
        # gate receives their one verified content OID exactly once.
        run_dir = Path(temporary) / "run"
        control_dir = Path(temporary) / "control"
        run_dir.mkdir()
        control_dir.mkdir()
        repeated_size = 450 * 1024 * 1024
        sparse(run_dir / "retained-candidates.jsonl", repeated_size)
        sparse(run_dir / "complete-relations.jsonl", repeated_size)
        logical_errors = checker._evidence_size_errors(run_dir, control_dir)
        assert any("producer tree exceeds 844 MiB" in error for error in logical_errors)
        assert any("RUN_DIR tree exceeds 896 MiB" in error for error in logical_errors)
        assert checker._distinct_blob_payload_size_errors(
            {object_a: repeated_size}, "one deduplicated repeated payload",
        ) == []
