from __future__ import annotations

import hashlib
import math
import os
import platform
import resource
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from .records import (
    RecordValidationError,
    canonical_json_bytes,
    loads_json_strict,
    read_json,
    validate_record,
    write_json,
)


TERMINAL_STATUSES = {
    "completed_valid",
    "completed_invalid",
    "failed_infrastructure",
    "failed_implementation",
    "resource_exhaustion",
    "cancelled_by_budget",
}

RUN_ID_PATTERN = re.compile(r"RUN-[A-Z0-9-]+-[0-9]{3,}")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
GIBIBYTE = 1024**3
MEMORY_FAILURE_MARKERS = (
    "memoryerror",
    "cannot allocate memory",
    "out of memory",
    "std::bad_alloc",
    "failed to map segment",
)
CORE_ARTIFACT_NAMES = {
    "command.txt",
    "environment.json",
    "raw-result.json",
    "stderr.log",
    "stdout.log",
}
LOCKED_ARTIFACT_NAMES = CORE_ARTIFACT_NAMES | {"runner-receipt.json"}
LOCKED_RUN_FILE_NAMES = LOCKED_ARTIFACT_NAMES | {"manifest.json"}
POST_RUN_CHECK_KEYS = (
    "process_group_quiescent",
    "commit_unchanged",
    "tree_unchanged",
    "approval_lock_unchanged",
    "specification_unchanged",
    "execution_plan_unchanged",
    "protocol_hashes_unchanged",
)
LOCKED_DESCENDANT_POLICY = "forbidden-via-rlimit-nproc-zero"


@dataclass(frozen=True)
class _ChildResult:
    return_code: int | None
    timed_out: bool
    memory_killed: bool
    infrastructure_error: str | None
    stdout: str
    stderr: str
    cpu_seconds: float
    peak_rss_bytes: int
    cpu_killed: bool = False
    group_quiescent: bool = True
    wall_seconds: float = 0.0


@dataclass(frozen=True)
class _ProtocolFile:
    path: Path
    normalized_path: str
    sha256: str
    device: int
    inode: int


@dataclass(frozen=True)
class _ApprovalContext:
    path: Path
    sha256: str
    approval: dict[str, Any]
    specification_sha256: str
    execution_plan_sha256: str
    protocol_hashes_sha256: str
    run_object_sha256: str
    python_sha256: str
    descendant_policy: str
    effective_uid: int
    protocol_files: tuple[_ProtocolFile, ...]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _canonical_digest(value: Any) -> str:
    return _sha256_bytes(canonical_json_bytes(value))


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RecordValidationError(
            f"git {' '.join(args)} failed: {completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def _git_state(repo_root: Path) -> dict[str, Any]:
    return {
        "commit": _git(repo_root, "rev-parse", "HEAD"),
        "dirty": bool(_git(repo_root, "status", "--porcelain")),
    }


def _git_completed(
    repo_root: Path, *args: str, text: bool = True
) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=text,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _tree_clean_except(repo_root: Path, allowed_directory: Path) -> bool:
    for args in (("diff", "--quiet"), ("diff", "--cached", "--quiet")):
        completed = _git_completed(repo_root, *args)
        if completed.returncode != 0:
            return False
    untracked = _git_completed(
        repo_root,
        "ls-files",
        "--others",
        "--exclude-standard",
        "-z",
        text=False,
    )
    if untracked.returncode != 0:
        return False
    try:
        allowed = allowed_directory.resolve().relative_to(repo_root)
    except ValueError:
        return False
    for raw_path in untracked.stdout.split(b"\0"):
        if not raw_path:
            continue
        try:
            relative = Path(os.fsdecode(raw_path))
            relative.relative_to(allowed)
        except (ValueError, UnicodeError):
            return False
    return True


def _post_run_checks(
    repo_root: Path,
    temp_dir: Path,
    specification_path: Path,
    execution_plan: dict[str, Any],
    approval_context: _ApprovalContext,
    launch_commit: str,
    process_group_quiescent: bool,
) -> dict[str, bool]:
    try:
        current_commit = _git(repo_root, "rev-parse", "HEAD")
    except RecordValidationError:
        current_commit = ""
    try:
        approval_lock_unchanged = (
            approval_context.path.is_file()
            and _sha256(approval_context.path) == approval_context.sha256
        )
    except OSError:
        approval_lock_unchanged = False
    try:
        specification_unchanged = (
            specification_path.is_file()
            and _sha256(specification_path) == approval_context.specification_sha256
        )
    except OSError:
        specification_unchanged = False
    execution_plan_unchanged = False
    if specification_unchanged:
        try:
            current_plan = read_json(specification_path)["experiment"]["execution_plan"]
            execution_plan_unchanged = (
                _canonical_digest(current_plan)
                == approval_context.execution_plan_sha256
                and canonical_json_bytes(current_plan)
                == canonical_json_bytes(execution_plan)
            )
        except (KeyError, RecordValidationError):
            execution_plan_unchanged = False
    return {
        "process_group_quiescent": process_group_quiescent,
        "commit_unchanged": current_commit == launch_commit,
        "tree_unchanged": _tree_clean_except(repo_root, temp_dir),
        "approval_lock_unchanged": approval_lock_unchanged,
        "specification_unchanged": specification_unchanged,
        "execution_plan_unchanged": execution_plan_unchanged,
        "protocol_hashes_unchanged": _protocol_files_unchanged(
            approval_context.protocol_files
        ),
    }


def _git_blob(repo_root: Path, commit: str, relative_path: str) -> bytes:
    completed = _git_completed(
        repo_root, "show", f"{commit}:{relative_path}", text=False
    )
    if completed.returncode != 0:
        raise RecordValidationError(
            f"committed predecessor file is missing at {commit}: {relative_path}"
        )
    return completed.stdout


def _verify_committed_predecessor_transition(
    repo_root: Path,
    approved_base_commit: str,
    launch_commit: str,
    predecessor_dir: Path,
) -> None:
    if launch_commit == approved_base_commit:
        raise RecordValidationError(
            "verifier launch requires a committed predecessor transition after base commit"
        )
    ancestor = _git_completed(
        repo_root,
        "merge-base",
        "--is-ancestor",
        approved_base_commit,
        launch_commit,
    )
    if ancestor.returncode != 0:
        raise RecordValidationError(
            "verifier launch commit is not a descendant of approved base commit"
        )
    expected_paths = {
        (predecessor_dir / name).relative_to(repo_root).as_posix()
        for name in LOCKED_RUN_FILE_NAMES
    }
    changed = _git(
        repo_root,
        "diff",
        "--name-only",
        f"{approved_base_commit}..{launch_commit}",
    )
    changed_paths = set(changed.splitlines()) if changed else set()
    if changed_paths != expected_paths:
        raise RecordValidationError(
            "verifier commit transition must contain exactly committed predecessor run files"
        )
    for relative_path in sorted(expected_paths):
        working_path = repo_root / relative_path
        if not working_path.is_file():
            raise RecordValidationError(
                f"committed predecessor file is missing from worktree: {relative_path}"
            )
        if _git_blob(repo_root, launch_commit, relative_path) != working_path.read_bytes():
            raise RecordValidationError(
                f"predecessor file is not byte-identical to Git: {relative_path}"
            )


def _environment() -> dict[str, Any]:
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "sage_version": None,
        "dependencies": {},
        "selected_environment": {
            key: os.environ[key]
            for key in ("PATH", "PYTHONPATH", "HOME", "SHELL")
            if key in os.environ
        },
    }


def _max_rss_bytes(usage: resource.struct_rusage) -> int:
    if sys.platform == "darwin":
        return int(usage.ru_maxrss)
    return int(usage.ru_maxrss) * 1024


def _parse_stdout(stdout: str) -> tuple[dict[str, Any], str | None]:
    try:
        value = loads_json_strict(stdout, "child stdout")
    except RecordValidationError as exc:
        return {"stdout_json": None}, str(exc)
    if not isinstance(value, dict):
        return {"stdout_json": value}, None
    return value, None


def _remove_appledouble(root: Path) -> None:
    for path in root.rglob("._*"):
        if path.is_file():
            path.unlink()


def _finite_number(value: Any, name: str, *, positive: bool = False) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise RecordValidationError(f"{name} must be a finite number")
    number = float(value)
    if number < 0 or (positive and number <= 0):
        comparison = "positive" if positive else "non-negative"
        raise RecordValidationError(f"{name} must be {comparison}")
    return number


def _planned_run(
    experiment: dict[str, Any], run_id: str, wall_clock_limit: float
) -> tuple[dict[str, Any] | None, set[str]]:
    execution_plan = experiment.get("execution_plan")
    if execution_plan is None:
        return None, set()
    if execution_plan["allow_dirty"] is not False:
        raise RecordValidationError("execution_plan must forbid allow_dirty")

    runs = execution_plan["runs"]
    maximum_runs = experiment["budget"]["maximum_runs"]
    if len(runs) > maximum_runs:
        raise RecordValidationError(
            "execution_plan contains more runs than budget.maximum_runs"
        )

    positions: dict[str, int] = {}
    planned_by_id: dict[str, dict[str, Any]] = {}
    for index, planned in enumerate(runs):
        planned_id = planned["run_id"]
        if planned_id in positions:
            raise RecordValidationError(
                f"execution_plan contains duplicate run ID: {planned_id}"
            )
        positions[planned_id] = index
        planned_by_id[planned_id] = planned

        planned_timeout = _finite_number(
            planned["timeout_seconds"],
            f"execution_plan run {planned_id} timeout_seconds",
            positive=True,
        )
        if planned_timeout > wall_clock_limit:
            raise RecordValidationError(
                f"execution_plan run {planned_id} timeout_seconds exceeds "
                "budget.wall_clock_seconds_per_run"
            )
        if not planned["argv"] or any(not argument for argument in planned["argv"]):
            raise RecordValidationError(
                f"execution_plan run {planned_id} argv must contain non-empty strings"
            )

        predecessor = planned["predecessor"]
        if planned["role"] == "generator":
            if predecessor is not None:
                raise RecordValidationError(
                    f"generator run {planned_id} must not declare a predecessor"
                )
        elif predecessor is None:
            raise RecordValidationError(
                f"verifier run {planned_id} must declare a predecessor"
            )
        else:
            predecessor_id = predecessor["run_id"]
            if predecessor_id not in positions:
                raise RecordValidationError(
                    f"verifier run {planned_id} predecessor must appear earlier "
                    f"in execution_plan: {predecessor_id}"
                )
            if predecessor["artifact"] != "raw-result.json":
                raise RecordValidationError(
                    f"verifier run {planned_id} must link raw-result.json"
                )
            if planned_by_id[predecessor_id]["role"] != "generator":
                raise RecordValidationError(
                    f"verifier run {planned_id} predecessor must be a generator run"
                )

    selected = next((item for item in runs if item["run_id"] == run_id), None)
    if selected is None:
        raise RecordValidationError(f"run ID is not in execution_plan: {run_id}")
    return selected, set(positions)


def _protocol_path(
    repo_root: Path, path_text: str
) -> tuple[Path, str]:
    if "\\" in path_text:
        raise RecordValidationError(
            f"execution_plan protocol hash path must use canonical POSIX separators: "
            f"{path_text!r}"
        )
    posix_path = PurePosixPath(path_text)
    windows_path = PureWindowsPath(path_text)
    if posix_path.is_absolute() or windows_path.is_absolute():
        raise RecordValidationError(
            f"execution_plan protocol hash path must be repository-relative: {path_text!r}"
        )
    if ".." in posix_path.parts or ".." in windows_path.parts:
        raise RecordValidationError(
            f"execution_plan protocol hash path contains parent traversal: {path_text!r}"
        )

    normalized_path = posix_path.as_posix()
    if normalized_path != path_text or any(part in {"", "."} for part in posix_path.parts):
        raise RecordValidationError(
            f"execution_plan protocol hash path is not canonical: {path_text!r}"
        )
    unresolved = repo_root / Path(*posix_path.parts)
    if unresolved.is_symlink():
        raise RecordValidationError(
            f"execution_plan protocol hash path must not be a symlink: {path_text!r}"
        )
    candidate = unresolved.resolve()
    try:
        candidate.relative_to(repo_root)
    except ValueError as exc:
        raise RecordValidationError(
            f"execution_plan protocol hash path escapes repository: {path_text!r}"
        ) from exc
    if not candidate.is_file():
        raise RecordValidationError(
            f"execution_plan protocol hash path is missing or not a file: {path_text!r}"
        )
    return candidate, normalized_path


def _repo_file_argument(argv: list[str], repo_root: Path) -> str | None:
    if "-c" in argv:
        return None
    for argument in argv:
        argument_path = Path(argument)
        candidate = (
            argument_path.resolve()
            if argument_path.is_absolute()
            else (repo_root / argument_path).resolve()
        )
        try:
            relative = candidate.relative_to(repo_root)
        except ValueError:
            continue
        if candidate.is_file():
            return relative.as_posix()
    return None


def _required_protocol_paths(
    repo_root: Path,
    experiment_dir: Path,
    execution_plan: dict[str, Any],
) -> set[str]:
    fixed_paths = (
        Path(__file__).resolve(),
        (repo_root / "src" / "crypto_autoresearcher" / "__init__.py").resolve(),
        (repo_root / "src" / "crypto_autoresearcher" / "cli.py").resolve(),
        (repo_root / "src" / "crypto_autoresearcher" / "records.py").resolve(),
        (repo_root / "schemas" / "experiment.schema.json").resolve(),
        (repo_root / "schemas" / "run-manifest.schema.json").resolve(),
        (repo_root / "schemas" / "execution-approval.schema.json").resolve(),
        (repo_root / "schemas" / "runner-receipt.schema.json").resolve(),
        (experiment_dir / "contract.md").resolve(),
    )
    required: set[str] = set()
    for path in fixed_paths:
        try:
            required.add(path.relative_to(repo_root).as_posix())
        except ValueError as exc:
            raise RecordValidationError(
                f"required protocol file is outside repository: {path}"
            ) from exc

    for planned in execution_plan["runs"]:
        source_path = _repo_file_argument(planned["argv"], repo_root)
        if source_path is None and "-c" not in planned["argv"]:
            raise RecordValidationError(
                f"cannot identify repository source for planned run "
                f"{planned['run_id']}"
            )
        if source_path is not None:
            required.add(source_path)
    return required


def _verify_protocol_hashes(
    repo_root: Path,
    experiment_dir: Path,
    execution_plan: dict[str, Any],
) -> tuple[_ProtocolFile, ...]:
    verified_paths: set[str] = set()
    resolved_paths: set[Path] = set()
    file_identities: set[tuple[int, int]] = set()
    protocol_files: list[_ProtocolFile] = []
    for record in execution_plan["protocol_hashes"]:
        path_text = record["path"]
        expected_sha256 = record["sha256"]
        if SHA256_PATTERN.fullmatch(expected_sha256) is None:
            raise RecordValidationError(
                f"execution_plan protocol hash has invalid SHA-256: {path_text!r}"
            )
        path, normalized_path = _protocol_path(repo_root, path_text)
        stat_result = path.stat()
        identity = (stat_result.st_dev, stat_result.st_ino)
        if (
            normalized_path in verified_paths
            or path in resolved_paths
            or identity in file_identities
        ):
            raise RecordValidationError(
                f"execution_plan contains duplicate protocol hash path: {path_text!r}"
            )
        verified_paths.add(normalized_path)
        resolved_paths.add(path)
        file_identities.add(identity)
        actual_sha256 = _sha256(path)
        if actual_sha256 != expected_sha256:
            raise RecordValidationError(
                f"execution_plan protocol SHA-256 mismatch for {path_text!r}: "
                f"expected {expected_sha256}, got {actual_sha256}"
            )
        protocol_files.append(
            _ProtocolFile(
                path=path,
                normalized_path=normalized_path,
                sha256=actual_sha256,
                device=stat_result.st_dev,
                inode=stat_result.st_ino,
            )
        )

    missing = sorted(
        _required_protocol_paths(repo_root, experiment_dir, execution_plan)
        - verified_paths
    )
    if missing:
        raise RecordValidationError(
            "execution_plan is missing required protocol hashes: " + ", ".join(missing)
        )
    return tuple(protocol_files)


def _planned_transitions(execution_plan: dict[str, Any]) -> dict[str, dict[str, str]]:
    transitions: dict[str, dict[str, str]] = {}
    for planned in execution_plan["runs"]:
        if planned["role"] != "verifier":
            continue
        predecessor = planned["predecessor"]
        transitions[planned["run_id"]] = {
            "verifier_run_id": planned["run_id"],
            "predecessor_run_id": predecessor["run_id"],
            "artifact": predecessor["artifact"],
            "commit_policy": "base-plus-committed-predecessor-run-only",
        }
    return transitions


def _resolve_command_executable(command: str, repo_root: Path) -> Path | None:
    candidate = shutil.which(command, path=os.environ.get("PATH"))
    if candidate is None:
        command_path = Path(command)
        if not command_path.is_absolute():
            command_path = repo_root / command_path
        candidate = str(command_path) if command_path.is_file() else None
    return Path(candidate).resolve() if candidate is not None else None


def _load_approval_context(
    repo_root: Path,
    experiment_dir: Path,
    specification_path: Path,
    experiment: dict[str, Any],
    planned: dict[str, Any],
    approval_lock_path: Path | None,
    approval_lock_sha256: str | None,
) -> _ApprovalContext:
    if approval_lock_path is None or approval_lock_sha256 is None:
        raise RecordValidationError(
            "execution_plan runs require --approval-lock and "
            "--approval-lock-sha256"
        )
    if SHA256_PATTERN.fullmatch(approval_lock_sha256) is None:
        raise RecordValidationError("approval lock expected SHA-256 is invalid")
    lock_path = approval_lock_path.resolve()
    if not lock_path.is_file():
        raise RecordValidationError(f"approval lock is missing or not a file: {lock_path}")
    lock_sha256 = _sha256(lock_path)
    if lock_sha256 != approval_lock_sha256:
        raise RecordValidationError(
            f"approval lock SHA-256 mismatch: expected {approval_lock_sha256}, "
            f"got {lock_sha256}"
        )
    validate_record(lock_path, repo_root)
    approval = read_json(lock_path)["execution_approval"]
    execution_plan = experiment["execution_plan"]
    specification_sha256 = _sha256(specification_path)
    execution_plan_sha256 = _canonical_digest(execution_plan)
    protocol_hashes_sha256 = _canonical_digest(execution_plan["protocol_hashes"])

    if approval["experiment_id"] != experiment["id"]:
        raise RecordValidationError("approval lock experiment ID does not match")
    if approval["specification_sha256"] != specification_sha256:
        raise RecordValidationError("approval lock specification SHA-256 does not match")
    if approval["execution_plan_sha256"] != execution_plan_sha256:
        raise RecordValidationError("approval lock execution-plan SHA-256 does not match")
    if canonical_json_bytes(approval["protocol_hashes"]) != canonical_json_bytes(
        execution_plan["protocol_hashes"]
    ):
        raise RecordValidationError(
            "approval lock protocol hash list does not exactly match execution_plan"
        )

    transitions: dict[str, dict[str, str]] = {}
    for transition in approval["allowed_verifier_transitions"]:
        verifier_id = transition["verifier_run_id"]
        if verifier_id in transitions:
            raise RecordValidationError(
                f"approval lock contains duplicate verifier transition: {verifier_id}"
            )
        transitions[verifier_id] = transition
    if canonical_json_bytes(transitions) != canonical_json_bytes(
        _planned_transitions(execution_plan)
    ):
        raise RecordValidationError(
            "approval lock verifier transitions do not exactly match execution_plan"
        )

    for planned_run in execution_plan["runs"]:
        if "-c" in planned_run["argv"]:
            raise RecordValidationError(
                f"locked run {planned_run['run_id']} forbids inline -c"
            )

    python_boundary = approval["python"]
    python_path = Path(sys.executable).resolve()
    if python_boundary["executable"] != str(python_path):
        raise RecordValidationError("approval lock Python executable does not match runtime")
    if python_boundary["version"] != platform.python_version():
        raise RecordValidationError("approval lock Python version does not match runtime")
    python_sha256 = _sha256(python_path)
    if python_boundary["sha256"] != python_sha256:
        raise RecordValidationError("approval lock Python executable SHA-256 does not match")
    for planned_run in execution_plan["runs"]:
        command_path = Path(planned_run["argv"][0])
        executable = _resolve_command_executable(planned_run["argv"][0], repo_root)
        if (
            not command_path.is_absolute()
            or command_path != python_path
            or executable != python_path
        ):
            raise RecordValidationError(
                f"locked run {planned_run['run_id']} does not use the absolute "
                "approved Python executable"
            )
        if planned_run["argv"][1:4] != ["-I", "-S", "-B"]:
            raise RecordValidationError(
                f"locked run {planned_run['run_id']} must use the approved "
                "Python isolation flags -I -S -B"
            )

    resource_policy = _locked_resource_policy()
    if canonical_json_bytes(approval["resource_policy"]) != canonical_json_bytes(
        resource_policy
    ):
        raise RecordValidationError(
            "approval lock resource policy does not match the current runtime"
        )

    protocol_files = _verify_protocol_hashes(repo_root, experiment_dir, execution_plan)
    return _ApprovalContext(
        path=lock_path,
        sha256=lock_sha256,
        approval=approval,
        specification_sha256=specification_sha256,
        execution_plan_sha256=execution_plan_sha256,
        protocol_hashes_sha256=protocol_hashes_sha256,
        run_object_sha256=_canonical_digest(planned),
        python_sha256=python_sha256,
        descendant_policy=resource_policy["descendant_policy"],
        effective_uid=resource_policy["effective_uid"],
        protocol_files=protocol_files,
    )


def _protocol_files_unchanged(protocol_files: tuple[_ProtocolFile, ...]) -> bool:
    for record in protocol_files:
        try:
            stat_result = record.path.stat()
        except OSError:
            return False
        if (stat_result.st_dev, stat_result.st_ino) != (record.device, record.inode):
            return False
        try:
            if not record.path.is_file() or _sha256(record.path) != record.sha256:
                return False
        except OSError:
            return False
    return True


def _read_existing_runs(
    runs_dir: Path, repo_root: Path, experiment_id: str
) -> dict[str, dict[str, Any]]:
    if not runs_dir.exists():
        return {}
    active = sorted(
        path.name for path in runs_dir.iterdir() if path.is_dir() and path.name.startswith(".")
    )
    if active:
        raise RecordValidationError(
            "an incomplete or active run prevents reliable budget accounting: "
            + ", ".join(active)
        )

    manifests: dict[str, dict[str, Any]] = {}
    for run_dir in sorted(
        path for path in runs_dir.iterdir() if path.is_dir() and not path.name.startswith(".")
    ):
        manifest_path = run_dir / "manifest.json"
        if not manifest_path.is_file():
            raise RecordValidationError(
                f"existing run has no manifest for budget accounting: {run_dir.name}"
            )
        validate_record(manifest_path, repo_root)
        manifest = read_json(manifest_path)["run"]
        if manifest["id"] != run_dir.name:
            raise RecordValidationError(
                f"run directory and manifest ID disagree: {run_dir.name}"
            )
        if manifest["experiment_id"] != experiment_id:
            raise RecordValidationError(
                f"run {run_dir.name} belongs to {manifest['experiment_id']}, "
                f"not {experiment_id}"
            )
        manifests[run_dir.name] = manifest
    return manifests


def _artifact_metadata(path: Path) -> dict[str, Any]:
    return {"sha256": _sha256(path), "bytes": path.stat().st_size}


def _successful_post_run_checks() -> dict[str, bool]:
    return {key: True for key in POST_RUN_CHECK_KEYS}


def _predecessor_link(
    repo_root: Path,
    experiment_dir: Path,
    execution_plan: dict[str, Any],
    planned: dict[str, Any],
    existing_runs: dict[str, dict[str, Any]],
    approval_context: _ApprovalContext,
    launch_commit: str,
) -> dict[str, Any] | None:
    if planned["role"] != "verifier":
        return None
    predecessor = planned["predecessor"]
    predecessor_id = predecessor["run_id"]
    artifact_name = predecessor["artifact"]
    predecessor_plan = next(
        (run for run in execution_plan["runs"] if run["run_id"] == predecessor_id),
        None,
    )
    if predecessor_plan is None or predecessor_plan["role"] != "generator":
        raise RecordValidationError(
            f"verifier predecessor is not a planned generator: {predecessor_id}"
        )
    manifest = existing_runs.get(predecessor_id)
    if manifest is None:
        raise RecordValidationError(
            f"verifier predecessor has not completed: {predecessor_id}"
        )
    if manifest["status"] != "completed_valid" or manifest["result"]["valid"] is not True:
        raise RecordValidationError(
            f"verifier predecessor is not completed_valid: {predecessor_id}"
        )
    if manifest["code"]["dirty"] is not False:
        raise RecordValidationError(
            f"verifier predecessor was executed from a dirty tree: {predecessor_id}"
        )

    predecessor_dir = experiment_dir / "runs" / predecessor_id
    actual_files = {
        path.name for path in predecessor_dir.iterdir() if path.is_file()
    }
    if actual_files != LOCKED_RUN_FILE_NAMES or any(
        not path.is_file() for path in predecessor_dir.iterdir()
    ):
        raise RecordValidationError(
            f"verifier predecessor does not contain the complete runner-created "
            f"artifact set: {predecessor_id}"
        )

    expected_command = shlex.join(predecessor_plan["argv"])
    if manifest["code"]["command"] != expected_command:
        raise RecordValidationError(
            f"verifier predecessor command does not match execution_plan: "
            f"{predecessor_id}"
        )
    approved_base_commit = approval_context.approval["approved_base_commit"]
    if manifest["code"]["commit"] != approved_base_commit:
        raise RecordValidationError(
            f"verifier predecessor launch commit does not match approved base commit: "
            f"{predecessor_id}"
        )
    expected_inputs = {
        "curve_id": predecessor_plan["curve_id"],
        "seed": predecessor_plan["seed"],
        "parameters": predecessor_plan["parameters"],
    }
    if canonical_json_bytes(manifest["inputs"]) != canonical_json_bytes(
        expected_inputs
    ):
        raise RecordValidationError(
            f"verifier predecessor inputs do not match execution_plan: {predecessor_id}"
        )

    expected_protocol = {
        "approval_lock_path": str(approval_context.path),
        "approval_lock_sha256": approval_context.sha256,
        "specification_sha256": approval_context.specification_sha256,
        "execution_plan_sha256": approval_context.execution_plan_sha256,
        "run_object_sha256": _canonical_digest(predecessor_plan),
        "protocol_hashes_sha256": approval_context.protocol_hashes_sha256,
        "approved_base_commit": approved_base_commit,
        "launch_commit": approved_base_commit,
        "python_sha256": approval_context.python_sha256,
        "descendant_policy": approval_context.descendant_policy,
        "effective_uid": approval_context.effective_uid,
        "timeout_seconds": float(predecessor_plan["timeout_seconds"]),
        "post_run_checks": _successful_post_run_checks(),
    }
    if canonical_json_bytes(manifest.get("protocol")) != canonical_json_bytes(
        expected_protocol
    ):
        raise RecordValidationError(
            f"verifier predecessor protocol receipt does not match approval lock and "
            f"execution_plan: {predecessor_id}"
        )

    receipt_path = predecessor_dir / "runner-receipt.json"
    validate_record(receipt_path, repo_root)
    receipt = read_json(receipt_path)["runner_receipt"]
    expected_receipt_values = {
        "experiment_id": manifest["experiment_id"],
        "run_id": predecessor_id,
        "role": "generator",
        "status": "completed_valid",
        "argv": predecessor_plan["argv"],
        "command": expected_command,
        "inputs": expected_inputs,
        "timeout_seconds": float(predecessor_plan["timeout_seconds"]),
        "approval_lock_sha256": approval_context.sha256,
        "specification_sha256": approval_context.specification_sha256,
        "execution_plan_sha256": approval_context.execution_plan_sha256,
        "run_object_sha256": _canonical_digest(predecessor_plan),
        "protocol_hashes_sha256": approval_context.protocol_hashes_sha256,
        "approved_base_commit": approved_base_commit,
        "launch_commit": approved_base_commit,
        "python_sha256": approval_context.python_sha256,
        "post_run_checks": _successful_post_run_checks(),
        "predecessor": None,
    }
    for key, expected in expected_receipt_values.items():
        if canonical_json_bytes(receipt.get(key)) != canonical_json_bytes(expected):
            raise RecordValidationError(
                f"verifier predecessor runner receipt field {key!r} does not match: "
                f"{predecessor_id}"
            )
    if receipt["format_version"] != 1:
        raise RecordValidationError(
            f"verifier predecessor runner receipt version is unsupported: "
            f"{predecessor_id}"
        )
    if (
        receipt["process_group"]["quiescent"] is not True
        or receipt["process_group"]["direct_parent_return_code"] != 0
        or receipt["process_group"]["descendant_policy"]
        != approval_context.descendant_policy
        or receipt["process_group"]["effective_uid"]
        != approval_context.effective_uid
    ):
        raise RecordValidationError(
            f"verifier predecessor process group did not complete cleanly: "
            f"{predecessor_id}"
        )

    computed_artifacts = {
        name: _artifact_metadata(predecessor_dir / name)
        for name in sorted(LOCKED_ARTIFACT_NAMES)
    }
    if canonical_json_bytes(manifest["artifacts"]) != canonical_json_bytes(
        computed_artifacts
    ):
        raise RecordValidationError(
            f"verifier predecessor manifest does not hash every runner artifact: "
            f"{predecessor_id}"
        )
    expected_receipt_artifacts = {
        name: computed_artifacts[name] for name in sorted(CORE_ARTIFACT_NAMES)
    }
    if canonical_json_bytes(receipt["artifacts"]) != canonical_json_bytes(
        expected_receipt_artifacts
    ):
        raise RecordValidationError(
            f"verifier predecessor receipt artifact hashes do not match: "
            f"{predecessor_id}"
        )

    receipt_sha256 = computed_artifacts["runner-receipt.json"]["sha256"]
    expected_manifest_receipt = {
        "artifact": "runner-receipt.json",
        "sha256": receipt_sha256,
        "predecessor": None,
    }
    if canonical_json_bytes(manifest.get("receipt")) != canonical_json_bytes(
        expected_manifest_receipt
    ):
        raise RecordValidationError(
            f"verifier predecessor manifest receipt linkage does not match: "
            f"{predecessor_id}"
        )

    artifact_path = predecessor_dir / artifact_name
    if not artifact_path.is_file():
        raise RecordValidationError(
            f"verifier predecessor artifact is missing: {predecessor_id}/{artifact_name}"
        )
    actual_sha256 = _sha256(artifact_path)
    if computed_artifacts[artifact_name]["sha256"] != actual_sha256:
        raise RecordValidationError(
            f"verifier predecessor artifact SHA-256 disagrees with its manifest: "
            f"{predecessor_id}/{artifact_name}"
        )

    _verify_committed_predecessor_transition(
        repo_root,
        approved_base_commit,
        launch_commit,
        predecessor_dir,
    )
    manifest_sha256 = _sha256(predecessor_dir / "manifest.json")
    return {
        "run_id": predecessor_id,
        "artifact": artifact_name,
        "path": artifact_path,
        "sha256": actual_sha256,
        "receipt": {
            "run_id": predecessor_id,
            "launch_commit": approved_base_commit,
            "manifest_sha256": manifest_sha256,
            "receipt_sha256": receipt_sha256,
            "raw_result_sha256": actual_sha256,
        },
    }


def _limit_value(resource_name: int, requested: int) -> int:
    _soft, inherited_hard = resource.getrlimit(resource_name)
    if inherited_hard == resource.RLIM_INFINITY:
        return requested
    return min(requested, int(inherited_hard))


def _locked_resource_policy() -> dict[str, Any]:
    nproc_resource = getattr(resource, "RLIMIT_NPROC", None)
    if os.name != "posix" or not hasattr(os, "geteuid") or nproc_resource is None:
        raise RecordValidationError(
            "locked runs require POSIX RLIMIT_NPROC descendant suppression"
        )
    effective_uid = os.geteuid()
    if effective_uid == 0:
        raise RecordValidationError(
            "locked runs require a non-root effective UID because root can bypass "
            "RLIMIT_NPROC"
        )
    return {
        "descendant_policy": LOCKED_DESCENDANT_POLICY,
        "effective_uid": effective_uid,
    }


def _resource_limiter(
    memory_bytes: int, cpu_seconds: float, forbid_descendants: bool
) -> Any:
    def apply_limits() -> None:
        if forbid_descendants:
            nproc_resource = getattr(resource, "RLIMIT_NPROC", None)
            if nproc_resource is None:
                raise RuntimeError("RLIMIT_NPROC is unavailable")
            resource.setrlimit(nproc_resource, (0, 0))
        address_space = getattr(resource, "RLIMIT_AS", None)
        if address_space is not None and sys.platform != "darwin":
            memory_limit = _limit_value(address_space, memory_bytes)
            resource.setrlimit(address_space, (memory_limit, memory_limit))
        cpu_resource = getattr(resource, "RLIMIT_CPU", None)
        if cpu_resource is not None:
            cpu_limit = _limit_value(cpu_resource, max(1, math.ceil(cpu_seconds)))
            resource.setrlimit(cpu_resource, (cpu_limit, cpu_limit))

    return apply_limits


def _kill_process(process: subprocess.Popen[Any]) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except (ProcessLookupError, PermissionError):
        try:
            process.kill()
        except (ProcessLookupError, PermissionError, OSError):
            pass


def _proc_cpu_seconds(process_id: int) -> float | None:
    """Per-process CPU seconds from /proc, with sub-second precision."""
    if not sys.platform.startswith("linux"):
        return None
    try:
        clk_tck = os.sysconf("SC_CLK_TCK")
        with open(f"/proc/{process_id}/stat", encoding="ascii") as handle:
            fields = handle.read().split()
        utime = int(fields[13])
        stime = int(fields[14])
        return (utime + stime) / clk_tck
    except (FileNotFoundError, ProcessLookupError, IndexError, OSError, ValueError):
        return None


def _cpu_time_seconds(value: str) -> float:
    days = 0
    if "-" in value:
        day_text, value = value.split("-", 1)
        days = int(day_text)
    parts = value.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours = "0"
        minutes, seconds = parts
    else:
        raise ValueError(f"unrecognized process CPU time: {value!r}")
    return days * 86400 + int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _process_table() -> dict[int, tuple[int, int, int, float, str]]:
    completed = subprocess.run(
        ["ps", "-axo", "pid=,ppid=,pgid=,rss=,time=,state="],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise OSError(f"process-group ps failed: {completed.stderr.strip()}")
    table: dict[int, tuple[int, int, int, float, str]] = {}
    for line in completed.stdout.splitlines():
        fields = line.split(None, 5)
        if len(fields) != 6:
            continue
        try:
            process_id = int(fields[0])
            parent_id = int(fields[1])
            group_id = int(fields[2])
            rss_kib = int(fields[3])
            process_cpu = _proc_cpu_seconds(process_id)
            if process_cpu is None:
                process_cpu = _cpu_time_seconds(fields[4])
        except ValueError:
            continue
        table[process_id] = (
            parent_id,
            group_id,
            rss_kib * 1024,
            process_cpu,
            fields[5],
        )
    return table


def _monitored_processes(
    process_group_id: int,
    tracked_process_ids: set[int],
    table: dict[int, tuple[int, int, int, float, str]],
) -> set[int]:
    active = {
        process_id
        for process_id, (_parent, group_id, _rss, _cpu, state) in table.items()
        if not state.startswith("Z")
        and (group_id == process_group_id or process_id in tracked_process_ids)
    }
    changed = True
    while changed:
        changed = False
        for process_id, (parent_id, _group, _rss, _cpu, state) in table.items():
            if state.startswith("Z") or process_id in active:
                continue
            if parent_id in active or parent_id in tracked_process_ids:
                active.add(process_id)
                changed = True
    tracked_process_ids.update(active)
    return active


def _kill_monitored_processes(
    process: subprocess.Popen[Any], tracked_process_ids: set[int]
) -> None:
    _kill_process(process)
    for process_id in sorted(tracked_process_ids):
        try:
            os.kill(process_id, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass


def _wait_for_child(
    process: subprocess.Popen[Any],
    timeout_seconds: float,
    memory_bytes: int,
    cpu_seconds_limit: float,
) -> tuple[int, bool, bool, bool, float, int, bool, float]:
    started = time.monotonic()
    if hasattr(os, "wait4"):
        deadline = started + timeout_seconds
        timed_out = False
        memory_killed = False
        cpu_killed = False
        observed_peak_rss = 0
        cpu_by_process: dict[int, float] = {}
        tracked_process_ids = {process.pid}
        parent_reaped = False
        return_code: int | None = None
        kill_started: float | None = None
        while True:
            table = _process_table()
            process_ids = _monitored_processes(
                process.pid, tracked_process_ids, table
            )
            current_rss = sum(table[pid][2] for pid in process_ids)
            for process_id in process_ids:
                cpu_by_process[process_id] = max(
                    cpu_by_process.get(process_id, 0.0), table[process_id][3]
                )
            observed_peak_rss = max(observed_peak_rss, current_rss)

            if not parent_reaped:
                try:
                    waited_pid, wait_status, usage = os.wait4(process.pid, os.WNOHANG)
                except InterruptedError:
                    continue
                if waited_pid == process.pid:
                    parent_reaped = True
                    cpu_by_process[process.pid] = max(
                        cpu_by_process.get(process.pid, 0.0),
                        max(0.0, usage.ru_utime + usage.ru_stime),
                    )
                    observed_peak_rss = max(observed_peak_rss, _max_rss_bytes(usage))
                    return_code = os.waitstatus_to_exitcode(wait_status)
                    process.returncode = return_code

            observed_cpu_seconds = sum(cpu_by_process.values())
            now = time.monotonic()
            if current_rss > memory_bytes:
                memory_killed = True
            if observed_cpu_seconds > cpu_seconds_limit:
                cpu_killed = True
            if now >= deadline:
                timed_out = True
            if memory_killed or cpu_killed or timed_out:
                if kill_started is None:
                    kill_started = now
                _kill_monitored_processes(process, tracked_process_ids)

            if parent_reaped and not process_ids:
                assert return_code is not None
                return (
                    return_code,
                    timed_out,
                    memory_killed,
                    cpu_killed,
                    observed_cpu_seconds,
                    observed_peak_rss,
                    True,
                    time.monotonic() - started,
                )

            if kill_started is not None and now - kill_started >= 2.0:
                if not parent_reaped:
                    while True:
                        try:
                            waited_pid, wait_status, usage = os.wait4(process.pid, 0)
                        except InterruptedError:
                            continue
                        if waited_pid == process.pid:
                            break
                    cpu_by_process[process.pid] = max(
                        cpu_by_process.get(process.pid, 0.0),
                        max(0.0, usage.ru_utime + usage.ru_stime),
                    )
                    observed_peak_rss = max(observed_peak_rss, _max_rss_bytes(usage))
                    return_code = os.waitstatus_to_exitcode(wait_status)
                    process.returncode = return_code
                    parent_reaped = True
                assert return_code is not None
                return (
                    return_code,
                    timed_out,
                    memory_killed,
                    cpu_killed,
                    sum(cpu_by_process.values()),
                    observed_peak_rss,
                    not process_ids,
                    time.monotonic() - started,
                )
            time.sleep(0.01 if kill_started is not None else min(0.01, max(0.0, deadline - now)))

    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    timed_out = False
    try:
        return_code = process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill_process(process)
        return_code = process.wait()
    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_seconds = max(
        0.0,
        usage_after.ru_utime
        + usage_after.ru_stime
        - usage_before.ru_utime
        - usage_before.ru_stime,
    )
    return (
        return_code,
        timed_out,
        False,
        cpu_seconds > cpu_seconds_limit,
        cpu_seconds,
        _max_rss_bytes(usage_after),
        True,
        time.monotonic() - started,
    )


def _run_child(
    command: list[str],
    cwd: Path,
    timeout_seconds: float,
    memory_bytes: int,
    cpu_seconds: float,
    stdout_path: Path,
    stderr_path: Path,
    forbid_descendants: bool = False,
) -> _ChildResult:
    infrastructure_error: str | None = None
    return_code: int | None = None
    timed_out = False
    memory_killed = False
    cpu_killed = False
    group_quiescent = True
    measured_cpu_seconds = 0.0
    peak_rss_bytes = 0
    group_wall_seconds = 0.0
    with stdout_path.open("w", encoding="utf-8", errors="replace") as stdout_handle, stderr_path.open(
        "w", encoding="utf-8", errors="replace"
    ) as stderr_handle:
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                text=True,
                stdout=stdout_handle,
                stderr=stderr_handle,
                start_new_session=os.name == "posix",
                preexec_fn=(
                    _resource_limiter(
                        memory_bytes, cpu_seconds, forbid_descendants
                    )
                    if os.name == "posix"
                    else None
                ),
            )
            (
                return_code,
                timed_out,
                memory_killed,
                cpu_killed,
                measured_cpu_seconds,
                peak_rss_bytes,
                group_quiescent,
                group_wall_seconds,
            ) = _wait_for_child(
                process,
                timeout_seconds,
                memory_bytes,
                cpu_seconds,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            infrastructure_error = str(exc)
            stderr_handle.write(str(exc))
            if "process" in locals():
                group_quiescent = False
                _kill_process(process)
                try:
                    process.wait(timeout=2)
                except (subprocess.SubprocessError, OSError):
                    pass

    return _ChildResult(
        return_code=return_code,
        timed_out=timed_out,
        memory_killed=memory_killed,
        infrastructure_error=infrastructure_error,
        stdout=stdout_path.read_text(encoding="utf-8", errors="replace"),
        stderr=stderr_path.read_text(encoding="utf-8", errors="replace"),
        cpu_seconds=measured_cpu_seconds,
        peak_rss_bytes=peak_rss_bytes,
        cpu_killed=cpu_killed,
        group_quiescent=group_quiescent,
        wall_seconds=group_wall_seconds,
    )


def _memory_limit_hit(child: _ChildResult, memory_bytes: int) -> bool:
    if child.memory_killed or child.peak_rss_bytes > memory_bytes:
        return True
    stderr = child.stderr.lower()
    return any(marker in stderr for marker in MEMORY_FAILURE_MARKERS)


def _cpu_limit_hit(
    child: _ChildResult,
    remaining_cpu_seconds: float,
    cumulative_cpu_seconds: float,
    total_cpu_seconds: float,
) -> bool:
    if child.cpu_killed:
        return True
    if cumulative_cpu_seconds > total_cpu_seconds:
        return True
    cpu_signal = getattr(signal, "SIGXCPU", None)
    if cpu_signal is not None and child.return_code == -cpu_signal:
        return True
    return (
        child.return_code == -signal.SIGKILL
        and child.cpu_seconds >= max(0.0, remaining_cpu_seconds - 0.05)
    )


def _verifier_link_error(
    raw_result: dict[str, Any], predecessor: dict[str, Any] | None
) -> str | None:
    if predecessor is None:
        return None
    artifact_path = predecessor["path"]
    if not artifact_path.is_file():
        return "verifier predecessor raw-result.json disappeared during execution"
    actual_sha256 = _sha256(artifact_path)
    if actual_sha256 != predecessor["sha256"]:
        return "verifier predecessor raw-result.json changed during execution"
    input_record = raw_result.get("input")
    reported_sha256 = input_record.get("sha256") if isinstance(input_record, dict) else None
    if reported_sha256 != actual_sha256:
        return (
            "verifier output input.sha256 does not match predecessor "
            "raw-result.json"
        )
    return None


def run_experiment(
    repo_root: Path,
    experiment_dir: Path,
    run_id: str,
    command: list[str],
    seed: int,
    curve_id: str | None,
    parameters: dict[str, Any],
    timeout_seconds: float | None,
    allow_dirty: bool,
    cwd: Path | None = None,
    approval_lock_path: Path | None = None,
    approval_lock_sha256: str | None = None,
) -> Path:
    repo_root = repo_root.resolve()
    experiment_dir = experiment_dir.resolve()
    specification_path = experiment_dir / "specification.json"
    validate_record(specification_path, repo_root)
    experiment = read_json(specification_path)["experiment"]
    execution_plan = experiment.get("execution_plan")
    if experiment["status"] == "approved":
        if not experiment["approved_by"] or execution_plan is None:
            raise RecordValidationError(
                f"{experiment['id']} is approved but lacks an approver or locked "
                "execution_plan"
            )
    elif experiment["status"] == "draft":
        if experiment["approved_by"] is not None or execution_plan is not None:
            raise RecordValidationError(
                "draft development runs must be unapproved and unplanned"
            )
        if not allow_dirty:
            raise RecordValidationError(
                "draft development runs require explicit allow_dirty"
            )
    else:
        raise RecordValidationError(
            f"{experiment['id']} is neither an approved locked experiment nor "
            "a draft development experiment"
        )
    if not command:
        raise RecordValidationError("run command is empty")
    if any(not isinstance(argument, str) or not argument for argument in command):
        raise RecordValidationError("run command must contain non-empty strings")
    if RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise RecordValidationError(f"invalid run ID: {run_id!r}")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise RecordValidationError("run seed must be an integer")
    if curve_id is not None and not isinstance(curve_id, str):
        raise RecordValidationError("run curve_id must be a string or null")
    if not isinstance(parameters, dict):
        raise RecordValidationError("run parameters must be an object")
    canonical_json_bytes(parameters)

    budget = experiment["budget"]
    wall_clock_limit = _finite_number(
        budget["wall_clock_seconds_per_run"],
        "budget.wall_clock_seconds_per_run",
        positive=True,
    )
    total_cpu_seconds = 3600 * _finite_number(
        budget["total_cpu_hours"], "budget.total_cpu_hours", positive=True
    )
    maximum_memory_gb = _finite_number(
        budget["maximum_memory_gb"], "budget.maximum_memory_gb", positive=True
    )
    memory_bytes = math.floor(maximum_memory_gb * GIBIBYTE)
    if memory_bytes <= 0:
        raise RecordValidationError("budget.maximum_memory_gb is too small to launch")

    planned, planned_ids = _planned_run(experiment, run_id, wall_clock_limit)
    approval_context: _ApprovalContext | None = None
    if planned is not None and allow_dirty:
        raise RecordValidationError("execution_plan forbids allow_dirty")
    if planned is not None and cwd is not None and cwd.resolve() != repo_root:
        raise RecordValidationError("execution_plan requires the repository root as cwd")
    if planned is not None:
        comparisons = (
            ("argv", command, planned["argv"]),
            ("seed", seed, planned["seed"]),
            ("curve_id", curve_id, planned["curve_id"]),
        )
        for field, actual, expected in comparisons:
            if actual != expected:
                raise RecordValidationError(
                    f"run {run_id} {field} does not match execution_plan"
                )
        if canonical_json_bytes(parameters) != canonical_json_bytes(
            planned["parameters"]
        ):
            raise RecordValidationError(
                f"run {run_id} parameters do not match execution_plan"
            )
        approval_context = _load_approval_context(
            repo_root,
            experiment_dir,
            specification_path,
            experiment,
            planned,
            approval_lock_path,
            approval_lock_sha256,
        )
    elif approval_lock_path is not None or approval_lock_sha256 is not None:
        raise RecordValidationError(
            "approval lock arguments require an execution_plan"
        )

    if timeout_seconds is None:
        effective_timeout = (
            float(planned["timeout_seconds"]) if planned is not None else wall_clock_limit
        )
    else:
        effective_timeout = _finite_number(
            timeout_seconds, "caller timeout_seconds", positive=True
        )
        if effective_timeout > wall_clock_limit:
            raise RecordValidationError(
                "caller timeout_seconds exceeds budget.wall_clock_seconds_per_run"
            )
        if planned is not None and effective_timeout != float(planned["timeout_seconds"]):
            raise RecordValidationError(
                f"run {run_id} timeout_seconds does not match execution_plan"
            )

    final_dir = experiment_dir / "runs" / run_id
    if final_dir.exists():
        raise RecordValidationError(f"run ID already exists and is immutable: {run_id}")
    runs_dir = final_dir.parent
    existing_runs = _read_existing_runs(runs_dir, repo_root, experiment["id"])
    if planned is not None:
        unplanned = sorted(set(existing_runs) - planned_ids)
        if unplanned:
            raise RecordValidationError(
                "existing runs are absent from execution_plan: " + ", ".join(unplanned)
            )
    maximum_runs = budget["maximum_runs"]
    if len(existing_runs) >= maximum_runs:
        raise RecordValidationError(
            f"budget.maximum_runs exhausted: {len(existing_runs)} of {maximum_runs}"
        )

    prior_cpu_seconds = sum(
        float(manifest["resources"]["cpu_seconds"])
        for manifest in existing_runs.values()
    )
    remaining_cpu_seconds = total_cpu_seconds - prior_cpu_seconds
    if remaining_cpu_seconds <= 0:
        raise RecordValidationError(
            "budget.total_cpu_hours is exhausted before launch: "
            f"{prior_cpu_seconds:.6f} CPU seconds already consumed"
        )

    git_state = _git_state(repo_root)
    if git_state["dirty"] and not allow_dirty:
        message = "working tree is dirty; commit the protocol and implementation"
        if planned is None:
            message += " or pass --allow-dirty"
        raise RecordValidationError(message)
    predecessor: dict[str, Any] | None = None
    if planned is not None:
        assert approval_context is not None
        approved_base_commit = approval_context.approval["approved_base_commit"]
        if planned["role"] == "generator":
            if git_state["commit"] != approved_base_commit:
                raise RecordValidationError(
                    "generator launch commit does not match approval lock "
                    "approved_base_commit"
                )
        else:
            predecessor = _predecessor_link(
                repo_root,
                experiment_dir,
                experiment["execution_plan"],
                planned,
                existing_runs,
                approval_context,
                git_state["commit"],
            )

    runs_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{run_id}.", dir=runs_dir))
    run_directories = [path for path in runs_dir.iterdir() if path.is_dir()]
    if len(run_directories) > maximum_runs:
        shutil.rmtree(temp_dir)
        raise RecordValidationError("budget.maximum_runs exhausted during launch reservation")
    competing_runs = [
        path for path in run_directories if path.name.startswith(".") and path != temp_dir
    ]
    if competing_runs:
        shutil.rmtree(temp_dir)
        raise RecordValidationError(
            "another run became active during launch reservation; retry after it completes"
        )
    command_text = shlex.join(command)
    started_at = _utc_now()
    child_started = time.monotonic()
    child = _run_child(
        command=command,
        cwd=(cwd or repo_root),
        timeout_seconds=effective_timeout,
        memory_bytes=memory_bytes,
        cpu_seconds=remaining_cpu_seconds,
        stdout_path=temp_dir / "stdout.log",
        stderr_path=temp_dir / "stderr.log",
        forbid_descendants=planned is not None,
    )
    child_elapsed = time.monotonic() - child_started
    finished_at = _utc_now()
    process_group_wall_seconds = max(child.wall_seconds, child_elapsed)
    wrapper_started = time.monotonic()
    wrapper_usage_before = resource.getrusage(resource.RUSAGE_SELF)
    raw_result, parse_error = _parse_stdout(child.stdout)
    declared_valid = raw_result.get("valid")
    verifier_link_error = _verifier_link_error(raw_result, predecessor)
    cumulative_cpu_seconds = prior_cpu_seconds + child.cpu_seconds
    memory_limit_hit = _memory_limit_hit(child, memory_bytes)
    cpu_limit_hit = _cpu_limit_hit(
        child,
        remaining_cpu_seconds,
        cumulative_cpu_seconds,
        total_cpu_seconds,
    )
    wall_limit_hit = (
        child.timed_out or process_group_wall_seconds > effective_timeout
    )

    (temp_dir / "command.txt").write_text(command_text + "\n", encoding="utf-8")
    environment = _environment()
    write_json(temp_dir / "environment.json", environment)
    write_json(temp_dir / "raw-result.json", raw_result)
    _remove_appledouble(temp_dir)

    core_artifacts = {
        name: _artifact_metadata(temp_dir / name)
        for name in sorted(CORE_ARTIFACT_NAMES)
    }
    post_run_checks: dict[str, bool] | None = None
    if planned is not None:
        assert approval_context is not None
        post_run_checks = _post_run_checks(
            repo_root,
            temp_dir,
            specification_path,
            experiment["execution_plan"],
            approval_context,
            git_state["commit"],
            child.group_quiescent,
        )

    wrapper_usage_after = resource.getrusage(resource.RUSAGE_SELF)
    wrapper_postprocessing = {
        "wall_seconds": max(0.0, time.monotonic() - wrapper_started),
        "cpu_seconds": max(
            0.0,
            wrapper_usage_after.ru_utime
            + wrapper_usage_after.ru_stime
            - wrapper_usage_before.ru_utime
            - wrapper_usage_before.ru_stime,
        ),
        "peak_rss_bytes": _max_rss_bytes(wrapper_usage_after),
        "boundary": (
            "through-core-artifact-hashing-before-receipt-and-manifest-write"
        ),
    }

    def status_for(checks: dict[str, bool] | None) -> str:
        integrity_failed = checks is not None and not all(checks.values())
        if wall_limit_hit or memory_limit_hit or cpu_limit_hit:
            return "resource_exhaustion"
        if child.infrastructure_error is not None:
            return "failed_infrastructure"
        if child.return_code != 0:
            return "failed_implementation"
        if (
            parse_error is not None
            or declared_valid is not True
            or verifier_link_error is not None
            or integrity_failed
        ):
            return "completed_invalid"
        return "completed_valid"

    def invalid_reason_for(checks: dict[str, bool] | None) -> str | None:
        reasons: list[str] = []
        if wall_limit_hit:
            reasons.append(
                f"wall-clock limit exceeded: {process_group_wall_seconds:.6f} > "
                f"{effective_timeout:.6f} seconds"
            )
        if memory_limit_hit:
            reasons.append(
                f"maximum memory budget exhausted: process-group peak RSS "
                f"{child.peak_rss_bytes} bytes; limit {memory_bytes} bytes"
            )
        if cpu_limit_hit:
            reasons.append(
                f"cumulative CPU budget exceeded: {cumulative_cpu_seconds:.6f} > "
                f"{total_cpu_seconds:.6f} seconds"
            )
        if child.infrastructure_error is not None:
            reasons.append(child.infrastructure_error)
        if child.return_code not in (None, 0):
            reasons.append(f"exit code {child.return_code}")
        if parse_error is not None:
            reasons.append(f"stdout JSON parse error: {parse_error}")
        if declared_valid is not True:
            reasons.append("result did not declare exact JSON valid=true")
        if verifier_link_error is not None:
            reasons.append(verifier_link_error)
        if checks is not None:
            failed_checks = sorted(key for key, passed in checks.items() if not passed)
            if failed_checks:
                reasons.append(
                    "post-run integrity checks failed: " + ", ".join(failed_checks)
                )
        return "; ".join(reasons) if reasons else None

    status = status_for(post_run_checks)
    invalid_reason = invalid_reason_for(post_run_checks)
    assert status in TERMINAL_STATUSES
    metrics = raw_result.get("summary", raw_result.get("metrics", {}))
    if not isinstance(metrics, dict):
        metrics = {}
    inputs = {
        "curve_id": curve_id,
        "seed": seed,
        "parameters": parameters,
    }
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": experiment["id"],
            "status": status,
            "code": {
                **git_state,
                "command": command_text,
            },
            "environment": environment,
            "inputs": inputs,
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": process_group_wall_seconds,
            },
            "resources": {
                "peak_rss_bytes": child.peak_rss_bytes,
                "cpu_seconds": child.cpu_seconds,
            },
            "result": {
                "metrics": metrics,
                "valid": status == "completed_valid",
                "invalid_reason": invalid_reason,
            },
            "artifacts": core_artifacts,
        }
    }

    def write_locked_records(checks: dict[str, bool]) -> None:
        assert planned is not None
        assert approval_context is not None
        predecessor_receipt = predecessor["receipt"] if predecessor is not None else None
        receipt = {
            "runner_receipt": {
                "format_version": 1,
                "experiment_id": experiment["id"],
                "run_id": run_id,
                "role": planned["role"],
                "status": manifest["run"]["status"],
                "argv": command,
                "command": command_text,
                "inputs": inputs,
                "timeout_seconds": effective_timeout,
                "approval_lock_sha256": approval_context.sha256,
                "specification_sha256": approval_context.specification_sha256,
                "execution_plan_sha256": approval_context.execution_plan_sha256,
                "run_object_sha256": approval_context.run_object_sha256,
                "protocol_hashes_sha256": approval_context.protocol_hashes_sha256,
                "approved_base_commit": approval_context.approval[
                    "approved_base_commit"
                ],
                "launch_commit": git_state["commit"],
                "python_sha256": approval_context.python_sha256,
                "process_group": {
                    "wall_seconds": process_group_wall_seconds,
                    "cpu_seconds": child.cpu_seconds,
                    "peak_rss_bytes": child.peak_rss_bytes,
                    "quiescent": child.group_quiescent,
                    "direct_parent_return_code": child.return_code,
                    "descendant_policy": approval_context.descendant_policy,
                    "effective_uid": approval_context.effective_uid,
                },
                "wrapper_postprocessing": wrapper_postprocessing,
                "post_run_checks": checks,
                "predecessor": predecessor_receipt,
                "artifacts": core_artifacts,
            }
        }
        receipt_path = temp_dir / "runner-receipt.json"
        write_json(receipt_path, receipt)
        validate_record(receipt_path, repo_root)
        receipt_metadata = _artifact_metadata(receipt_path)
        manifest["run"]["artifacts"] = {
            **core_artifacts,
            "runner-receipt.json": receipt_metadata,
        }
        manifest["run"]["protocol"] = {
            "approval_lock_path": str(approval_context.path),
            "approval_lock_sha256": approval_context.sha256,
            "specification_sha256": approval_context.specification_sha256,
            "execution_plan_sha256": approval_context.execution_plan_sha256,
            "run_object_sha256": approval_context.run_object_sha256,
            "protocol_hashes_sha256": approval_context.protocol_hashes_sha256,
            "approved_base_commit": approval_context.approval[
                "approved_base_commit"
            ],
            "launch_commit": git_state["commit"],
            "python_sha256": approval_context.python_sha256,
            "descendant_policy": approval_context.descendant_policy,
            "effective_uid": approval_context.effective_uid,
            "timeout_seconds": effective_timeout,
            "post_run_checks": checks,
        }
        manifest["run"]["receipt"] = {
            "artifact": "runner-receipt.json",
            "sha256": receipt_metadata["sha256"],
            "predecessor": predecessor_receipt,
        }
        manifest["run"]["timing"]["total_wall_seconds"] = (
            process_group_wall_seconds + wrapper_postprocessing["wall_seconds"]
        )
        manifest["run"]["resources"][
            "wrapper_postprocessing"
        ] = wrapper_postprocessing
        write_json(temp_dir / "manifest.json", manifest)
        validate_record(temp_dir / "manifest.json", repo_root)

    if planned is None:
        write_json(temp_dir / "manifest.json", manifest)
        validate_record(temp_dir / "manifest.json", repo_root)
    else:
        assert post_run_checks is not None
        write_locked_records(post_run_checks)
        assert approval_context is not None
        final_checks = _post_run_checks(
            repo_root,
            temp_dir,
            specification_path,
            experiment["execution_plan"],
            approval_context,
            git_state["commit"],
            child.group_quiescent,
        )
        merged_checks = {
            key: post_run_checks[key] and final_checks[key]
            for key in POST_RUN_CHECK_KEYS
        }
        if merged_checks != post_run_checks:
            post_run_checks = merged_checks
            status = status_for(post_run_checks)
            invalid_reason = invalid_reason_for(post_run_checks)
            manifest["run"]["status"] = status
            manifest["run"]["result"]["valid"] = status == "completed_valid"
            manifest["run"]["result"]["invalid_reason"] = invalid_reason
            write_locked_records(post_run_checks)
        _remove_appledouble(temp_dir)
        actual_files = {
            path.name for path in temp_dir.iterdir() if path.is_file()
        }
        if actual_files != LOCKED_RUN_FILE_NAMES:
            raise RecordValidationError(
                "locked run publication does not contain the complete runner-created "
                "artifact set"
            )
    _remove_appledouble(temp_dir)
    os.replace(temp_dir, final_dir)
    return final_dir


def remove_incomplete_run(path: Path) -> None:
    """Remove only an unpublished temporary directory after an interrupted wrapper."""
    if path.name.startswith(".") and path.is_dir():
        shutil.rmtree(path)
