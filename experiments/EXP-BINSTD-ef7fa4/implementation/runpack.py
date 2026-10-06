"""Immutable run-package helpers for EXP-BINSTD-ef7fa4."""
from __future__ import annotations

import json
import platform
import resource
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

EXP_ID = "EXP-BINSTD-ef7fa4"
TASK_ID = "TASK-20261001-2fe20a"
EXP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXP_ROOT.parents[1]


def git_commit_and_dirty() -> tuple[str, bool]:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()
    dirty = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
        ).strip()
    )
    return commit, dirty


def peak_rss_bytes() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dump_yaml(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.write_text(yaml.safe_dump(obj, sort_keys=False, allow_unicode=True), encoding="utf-8")


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def dump_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.write_text(text, encoding="utf-8")


def write_run_package(
    run_id: str,
    *,
    stage: int,
    arm: str,
    seed,
    command: str,
    parameters: dict,
    metrics: dict,
    valid: bool,
    invalid_reason: str | None,
    termination_reason: str,
    stdout_text: str,
    stderr_text: str = "",
    started_at: str,
    finished_at: str,
    wall_seconds: float,
    certificate: dict,
    status_override: str | None = None,
    curve_id: str | None = None,
) -> Path:
    run_dir = EXP_ROOT / "runs" / run_id
    if run_dir.exists() and any(run_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite existing run directory {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)
    commit, dirty = git_commit_and_dirty()
    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "sage_version": None,
        "python_version": platform.python_version(),
        "dependencies": {
            "numpy": __import__("numpy").__version__,
            "pyyaml": yaml.__version__,
        },
    }
    dump_text(run_dir / "command.txt", command + "\n")
    dump_json(run_dir / "environment.json", env)
    dump_text(run_dir / "stdout.log", stdout_text)
    dump_text(run_dir / "stderr.log", stderr_text)
    raw = {
        "run_id": run_id,
        "experiment_id": EXP_ID,
        "stage": stage,
        "arm": arm,
        "metrics": metrics,
        "certificate": certificate,
        "valid": valid,
        "termination_reason": termination_reason,
    }
    dump_json(run_dir / "raw-result.json", raw)
    if status_override:
        status = status_override
    elif termination_reason in ("timeout", "oom", "crash", "watchdog"):
        status = "failed_infrastructure"
    elif not valid:
        status = "invalid_measurement"
    else:
        status = "completed_valid"
    kind = certificate.get("kind")
    if kind not in ("discrete_log", "decomposition", "key_recovery", "none"):
        raise ValueError(f"certificate.kind outside vocabulary: {kind!r}")
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": stage,
            "arm": arm,
            "status": status,
            "termination_reason": termination_reason,
            "code": {
                "commit": commit,
                "dirty": dirty,
                "command": command,
            },
            "inference": {
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
                "adapter_version": None,
                "config_digest": None,
            },
            "environment": env,
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
                "peak_rss_bytes": metrics.get("peak_rss_bytes", peak_rss_bytes()),
                "cpu_seconds": None,
            },
            "result": {
                "metrics": metrics,
                "valid": valid,
                "invalid_reason": invalid_reason,
                "certificate": certificate,
            },
        }
    }
    dump_yaml(run_dir / "manifest.yaml", manifest)
    return run_dir
