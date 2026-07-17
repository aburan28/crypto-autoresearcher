from __future__ import annotations

import hashlib
import json
import os
import platform
import resource
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
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

    final_dir = experiment_dir / "runs" / run_id
    if final_dir.exists():
        raise RecordValidationError(f"run ID already exists and is immutable: {run_id}")
    git_state = _git_state(repo_root)
    if git_state["dirty"] and not allow_dirty:
        raise RecordValidationError(
            "working tree is dirty; commit the protocol and implementation or pass --allow-dirty"
        )

    runs_dir = final_dir.parent
    runs_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{run_id}.", dir=runs_dir))
    command_text = shlex.join(command)
    started_at = _utc_now()
    started = time.monotonic()
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    return_code: int | None = None
    timed_out = False
    infrastructure_error: str | None = None
    stdout = ""
    stderr = ""

    try:
        completed = subprocess.run(
            command,
            cwd=(cwd or repo_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
        return_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    except OSError as exc:
        infrastructure_error = str(exc)
        stderr = str(exc)

    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    finished_at = _utc_now()
    wall_seconds = time.monotonic() - started
    raw_result, parse_error = _parse_stdout(stdout)
    declared_valid = raw_result.get("valid")
    if timed_out:
        status = "resource_exhaustion"
    elif infrastructure_error is not None:
        status = "failed_infrastructure"
    elif return_code != 0:
        status = "failed_implementation"
    elif parse_error is not None or declared_valid is not True:
        status = "completed_invalid"
    else:
        status = "completed_valid"
    assert status in TERMINAL_STATUSES

    (temp_dir / "command.txt").write_text(command_text + "\n", encoding="utf-8")
    (temp_dir / "stdout.log").write_text(stdout, encoding="utf-8")
    (temp_dir / "stderr.log").write_text(stderr, encoding="utf-8")
    write_json(temp_dir / "environment.json", _environment())
    write_json(temp_dir / "raw-result.json", raw_result)
    _remove_appledouble(temp_dir)

    cpu_seconds = (
        usage_after.ru_utime
        + usage_after.ru_stime
        - usage_before.ru_utime
        - usage_before.ru_stime
    )
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
                "peak_rss_bytes": _max_rss_bytes(usage_after),
                "cpu_seconds": cpu_seconds,
            },
            "result": {
                "metrics": metrics,
                "valid": status == "completed_valid",
                "invalid_reason": (
                    "timeout"
                    if timed_out
                    else infrastructure_error
                    or (f"exit code {return_code}" if return_code else None)
                    or (f"stdout JSON parse error: {parse_error}" if parse_error else None)
                    or (
                        "result did not declare exact JSON valid=true"
                        if declared_valid is not True
                        else None
                    )
                ),
            },
            "artifacts": artifacts,
        }
    }
    write_json(temp_dir / "manifest.json", manifest)
    _remove_appledouble(temp_dir)
    os.replace(temp_dir, final_dir)
    return final_dir


def remove_incomplete_run(path: Path) -> None:
    """Remove only an unpublished temporary directory after an interrupted wrapper."""
    if path.name.startswith(".") and path.is_dir():
        shutil.rmtree(path)
