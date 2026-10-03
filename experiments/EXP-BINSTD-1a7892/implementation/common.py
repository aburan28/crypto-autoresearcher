"""Shared helpers for EXP-BINSTD-1a7892 run packaging."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = ROOT / "experiments" / "EXP-BINSTD-1a7892"
EXP_ID = "EXP-BINSTD-1a7892"
TASK_ID = "TASK-20261001-d6b2b5"
SEEDS = [20261001, 20261002, 20261003, 20261004, 20261005]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_state() -> dict:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    )
    return {"commit": commit, "dirty": dirty}


def peak_rss_bytes() -> int:
    # Linux: ru_maxrss is kilobytes
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_run_package(
    run_id: str,
    *,
    stage: int,
    command: str,
    seed,
    parameters: dict,
    metrics: dict,
    valid: bool,
    invalid_reason,
    termination_reason: str,
    certificate: dict,
    stdout_text: str,
    stderr_text: str = "",
    started_at: str,
    finished_at: str,
    wall_seconds: float,
    status: str = "completed_valid",
):
    run_dir = EXP_DIR / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    code = git_state()
    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "dependencies": {"numpy": _np_ver(), "pyyaml": yaml.__version__},
    }
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": stage,
            "status": status,
            "termination_reason": termination_reason,
            "code": {
                "commit": code["commit"],
                "dirty": code["dirty"],
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
            "inputs": {"curve_id": parameters.get("curve_id"), "seed": seed, "parameters": parameters},
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": wall_seconds,
            },
            "resources": {
                "peak_rss_bytes": peak_rss_bytes(),
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
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    (run_dir / "command.txt").write_text(command + "\n")
    (run_dir / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    (run_dir / "stdout.log").write_text(stdout_text)
    (run_dir / "stderr.log").write_text(stderr_text)
    raw = {
        "run_id": run_id,
        "experiment_id": EXP_ID,
        "stage": stage,
        "seed": seed,
        "parameters": parameters,
        "metrics": metrics,
        "valid": valid,
        "invalid_reason": invalid_reason,
        "termination_reason": termination_reason,
        "certificate": certificate,
        "timing": manifest["run"]["timing"],
        "resources": manifest["run"]["resources"],
        "code": code,
    }
    (run_dir / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    return run_dir


def _np_ver():
    try:
        import numpy as np

        return np.__version__
    except Exception:
        return None


def dump_yaml(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(obj, sort_keys=False))
