from __future__ import annotations

import hashlib
import json
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

from .records import RecordValidationError, read_json, validate_record, write_json


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


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        value = json.loads(stdout)
    except json.JSONDecodeError as exc:
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


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


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
    for index, planned in enumerate(runs):
        planned_id = planned["run_id"]
        if planned_id in positions:
            raise RecordValidationError(
                f"execution_plan contains duplicate run ID: {planned_id}"
            )
        positions[planned_id] = index

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

    selected = next((item for item in runs if item["run_id"] == run_id), None)
    if selected is None:
        raise RecordValidationError(f"run ID is not in execution_plan: {run_id}")
    return selected, set(positions)


def _protocol_path(
    repo_root: Path, path_text: str
) -> tuple[Path, str]:
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
    candidate = (repo_root / Path(*posix_path.parts)).resolve()
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
        (repo_root / "schemas" / "experiment.schema.json").resolve(),
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
) -> None:
    verified_paths: set[str] = set()
    resolved_paths: set[Path] = set()
    for record in execution_plan["protocol_hashes"]:
        path_text = record["path"]
        expected_sha256 = record["sha256"]
        if SHA256_PATTERN.fullmatch(expected_sha256) is None:
            raise RecordValidationError(
                f"execution_plan protocol hash has invalid SHA-256: {path_text!r}"
            )
        path, normalized_path = _protocol_path(repo_root, path_text)
        if normalized_path in verified_paths or path in resolved_paths:
            raise RecordValidationError(
                f"execution_plan contains duplicate protocol hash path: {path_text!r}"
            )
        verified_paths.add(normalized_path)
        resolved_paths.add(path)
        actual_sha256 = _sha256(path)
        if actual_sha256 != expected_sha256:
            raise RecordValidationError(
                f"execution_plan protocol SHA-256 mismatch for {path_text!r}: "
                f"expected {expected_sha256}, got {actual_sha256}"
            )

    missing = sorted(
        _required_protocol_paths(repo_root, experiment_dir, execution_plan)
        - verified_paths
    )
    if missing:
        raise RecordValidationError(
            "execution_plan is missing required protocol hashes: " + ", ".join(missing)
        )


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


def _predecessor_link(
    experiment_dir: Path,
    planned: dict[str, Any] | None,
    existing_runs: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    if planned is None or planned["role"] != "verifier":
        return None
    predecessor = planned["predecessor"]
    predecessor_id = predecessor["run_id"]
    artifact_name = predecessor["artifact"]
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

    artifact_path = experiment_dir / "runs" / predecessor_id / artifact_name
    if not artifact_path.is_file():
        raise RecordValidationError(
            f"verifier predecessor artifact is missing: {predecessor_id}/{artifact_name}"
        )
    actual_sha256 = _sha256(artifact_path)
    recorded_artifact = manifest["artifacts"].get(artifact_name)
    if (
        not isinstance(recorded_artifact, dict)
        or recorded_artifact.get("sha256") != actual_sha256
    ):
        raise RecordValidationError(
            f"verifier predecessor artifact SHA-256 disagrees with its manifest: "
            f"{predecessor_id}/{artifact_name}"
        )
    return {
        "run_id": predecessor_id,
        "artifact": artifact_name,
        "path": artifact_path,
        "sha256": actual_sha256,
    }


def _limit_value(resource_name: int, requested: int) -> int:
    _soft, inherited_hard = resource.getrlimit(resource_name)
    if inherited_hard == resource.RLIM_INFINITY:
        return requested
    return min(requested, int(inherited_hard))


def _resource_limiter(memory_bytes: int, cpu_seconds: float) -> Any:
    def apply_limits() -> None:
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
    except ProcessLookupError:
        pass


def _current_rss_bytes(process_id: int) -> int | None:
    if sys.platform != "darwin":
        return None
    completed = subprocess.run(
        ["ps", "-o", "rss=", "-p", str(process_id)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    try:
        return int(completed.stdout.strip()) * 1024
    except ValueError:
        return None


def _wait_for_child(
    process: subprocess.Popen[Any], timeout_seconds: float, memory_bytes: int
) -> tuple[int, bool, bool, float, int]:
    if hasattr(os, "wait4"):
        deadline = time.monotonic() + timeout_seconds
        timed_out = False
        memory_killed = False
        observed_peak_rss = 0
        while True:
            try:
                waited_pid, wait_status, usage = os.wait4(process.pid, os.WNOHANG)
            except InterruptedError:
                continue
            if waited_pid == process.pid:
                return_code = os.waitstatus_to_exitcode(wait_status)
                process.returncode = return_code
                return (
                    return_code,
                    timed_out,
                    memory_killed,
                    max(0.0, usage.ru_utime + usage.ru_stime),
                    max(observed_peak_rss, _max_rss_bytes(usage)),
                )
            current_rss = _current_rss_bytes(process.pid)
            if current_rss is not None:
                observed_peak_rss = max(observed_peak_rss, current_rss)
                if current_rss > memory_bytes:
                    memory_killed = True
                    _kill_process(process)
                    while True:
                        try:
                            waited_pid, wait_status, usage = os.wait4(process.pid, 0)
                        except InterruptedError:
                            continue
                        if waited_pid == process.pid:
                            break
                    return_code = os.waitstatus_to_exitcode(wait_status)
                    process.returncode = return_code
                    return (
                        return_code,
                        timed_out,
                        memory_killed,
                        max(0.0, usage.ru_utime + usage.ru_stime),
                        max(observed_peak_rss, _max_rss_bytes(usage)),
                    )
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                _kill_process(process)
                while True:
                    try:
                        waited_pid, wait_status, usage = os.wait4(process.pid, 0)
                    except InterruptedError:
                        continue
                    if waited_pid == process.pid:
                        break
                return_code = os.waitstatus_to_exitcode(wait_status)
                process.returncode = return_code
                return (
                    return_code,
                    timed_out,
                    memory_killed,
                    max(0.0, usage.ru_utime + usage.ru_stime),
                    max(observed_peak_rss, _max_rss_bytes(usage)),
                )
            time.sleep(min(0.01, remaining))

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
    return return_code, timed_out, False, cpu_seconds, _max_rss_bytes(usage_after)


def _run_child(
    command: list[str],
    cwd: Path,
    timeout_seconds: float,
    memory_bytes: int,
    cpu_seconds: float,
    stdout_path: Path,
    stderr_path: Path,
) -> _ChildResult:
    infrastructure_error: str | None = None
    return_code: int | None = None
    timed_out = False
    memory_killed = False
    measured_cpu_seconds = 0.0
    peak_rss_bytes = 0
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
                    _resource_limiter(memory_bytes, cpu_seconds)
                    if os.name == "posix"
                    else None
                ),
            )
            (
                return_code,
                timed_out,
                memory_killed,
                measured_cpu_seconds,
                peak_rss_bytes,
            ) = _wait_for_child(process, timeout_seconds, memory_bytes)
        except (OSError, subprocess.SubprocessError) as exc:
            infrastructure_error = str(exc)
            stderr_handle.write(str(exc))

    return _ChildResult(
        return_code=return_code,
        timed_out=timed_out,
        memory_killed=memory_killed,
        infrastructure_error=infrastructure_error,
        stdout=stdout_path.read_text(encoding="utf-8", errors="replace"),
        stderr=stderr_path.read_text(encoding="utf-8", errors="replace"),
        cpu_seconds=measured_cpu_seconds,
        peak_rss_bytes=peak_rss_bytes,
    )


def _memory_limit_hit(child: _ChildResult, memory_bytes: int) -> bool:
    if child.memory_killed or child.peak_rss_bytes > memory_bytes:
        return True
    stderr = child.stderr.lower()
    return child.return_code not in (None, 0) and any(
        marker in stderr for marker in MEMORY_FAILURE_MARKERS
    )


def _cpu_limit_hit(
    child: _ChildResult,
    remaining_cpu_seconds: float,
    cumulative_cpu_seconds: float,
    total_cpu_seconds: float,
) -> bool:
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
) -> Path:
    repo_root = repo_root.resolve()
    experiment_dir = experiment_dir.resolve()
    specification_path = experiment_dir / "specification.json"
    validate_record(specification_path, repo_root)
    experiment = read_json(specification_path)["experiment"]
    if experiment["status"] != "approved" or not experiment["approved_by"]:
        raise RecordValidationError(
            f"{experiment['id']} is not an approved, frozen experiment"
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
    if planned is not None:
        _verify_protocol_hashes(
            repo_root,
            experiment_dir,
            experiment["execution_plan"],
        )
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
        if _canonical_json(parameters) != _canonical_json(planned["parameters"]):
            raise RecordValidationError(
                f"run {run_id} parameters do not match execution_plan"
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

    predecessor = _predecessor_link(experiment_dir, planned, existing_runs)
    git_state = _git_state(repo_root)
    if git_state["dirty"] and not allow_dirty:
        message = "working tree is dirty; commit the protocol and implementation"
        if planned is None:
            message += " or pass --allow-dirty"
        raise RecordValidationError(message)

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
    started = time.monotonic()
    child = _run_child(
        command=command,
        cwd=(cwd or repo_root),
        timeout_seconds=effective_timeout,
        memory_bytes=memory_bytes,
        cpu_seconds=remaining_cpu_seconds,
        stdout_path=temp_dir / "stdout.log",
        stderr_path=temp_dir / "stderr.log",
    )
    finished_at = _utc_now()
    wall_seconds = time.monotonic() - started
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
    wall_limit_hit = child.timed_out or wall_seconds > effective_timeout
    if wall_limit_hit:
        status = "resource_exhaustion"
    elif memory_limit_hit or cpu_limit_hit:
        status = "resource_exhaustion"
    elif child.infrastructure_error is not None:
        status = "failed_infrastructure"
    elif child.return_code != 0:
        status = "failed_implementation"
    elif (
        parse_error is not None
        or declared_valid is not True
        or verifier_link_error is not None
    ):
        status = "completed_invalid"
    else:
        status = "completed_valid"
    assert status in TERMINAL_STATUSES

    (temp_dir / "command.txt").write_text(command_text + "\n", encoding="utf-8")
    write_json(temp_dir / "environment.json", _environment())
    write_json(temp_dir / "raw-result.json", raw_result)
    _remove_appledouble(temp_dir)

    artifacts = {
        path.name: {
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(temp_dir.iterdir())
        if path.is_file()
    }
    metrics = raw_result.get("summary", raw_result.get("metrics", {}))
    if not isinstance(metrics, dict):
        metrics = {}
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": experiment["id"],
            "status": status,
            "code": {
                **git_state,
                "command": command_text,
            },
            "environment": _environment(),
            "inputs": {
                "curve_id": curve_id,
                "seed": seed,
                "parameters": parameters,
            },
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": wall_seconds,
            },
            "resources": {
                "peak_rss_bytes": child.peak_rss_bytes,
                "cpu_seconds": child.cpu_seconds,
            },
            "result": {
                "metrics": metrics,
                "valid": status == "completed_valid",
                "invalid_reason": (
                    (
                        f"wall-clock limit exceeded: {wall_seconds:.6f} > "
                        f"{effective_timeout:.6f} seconds"
                        if wall_limit_hit
                        else None
                    )
                    or (
                        f"maximum memory budget exhausted: peak RSS "
                        f"{child.peak_rss_bytes} bytes; limit {memory_bytes} bytes"
                        if memory_limit_hit
                        else None
                    )
                    or (
                        f"cumulative CPU budget exceeded: {cumulative_cpu_seconds:.6f} > "
                        f"{total_cpu_seconds:.6f} seconds"
                        if cpu_limit_hit
                        else None
                    )
                    or child.infrastructure_error
                    or (f"exit code {child.return_code}" if child.return_code else None)
                    or (f"stdout JSON parse error: {parse_error}" if parse_error else None)
                    or (
                        "result did not declare exact JSON valid=true"
                        if declared_valid is not True
                        else None
                    )
                    or verifier_link_error
                ),
            },
            "artifacts": artifacts,
        }
    }
    write_json(temp_dir / "manifest.json", manifest)
    validate_record(temp_dir / "manifest.json", repo_root)
    _remove_appledouble(temp_dir)
    os.replace(temp_dir, final_dir)
    return final_dir


def remove_incomplete_run(path: Path) -> None:
    """Remove only an unpublished temporary directory after an interrupted wrapper."""
    if path.name.startswith(".") and path.is_dir():
        shutil.rmtree(path)
