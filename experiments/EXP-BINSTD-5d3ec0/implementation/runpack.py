"""Run-package helpers for EXP-BINSTD-5d3ec0 (immutable run directories)."""
from __future__ import annotations

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

EXP_ROOT = Path(__file__).resolve().parents[1]
RUNS = EXP_ROOT / "runs"
TASK_ID = "TASK-20261001-eaf0c5"
EXP_ID = "EXP-BINSTD-5d3ec0"


def git_commit_dirty():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() != ""
    return commit, dirty


def peak_rss_bytes() -> int:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux reports KiB
    return int(usage) * 1024


def env_block():
    deps = {}
    try:
        import numpy

        deps["numpy"] = numpy.__version__
    except Exception:
        deps["numpy"] = None
    try:
        import yaml as y

        deps["pyyaml"] = getattr(y, "__version__", None)
    except Exception:
        deps["pyyaml"] = None
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "sage_version": None,
        "python_version": platform.python_version(),
        "dependencies": deps,
    }


def inference_na():
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
        "adapter_version": None,
        "config_digest": None,
    }


def write_run(
    run_id: str,
    *,
    stage: str,
    command: str,
    parameters: dict,
    metrics: dict,
    certificate: dict,
    stdout: str = "",
    stderr: str = "",
    raw: dict | None = None,
    status: str = "completed_valid",
    valid: bool = True,
    invalid_reason=None,
    seed=None,
    started: float | None = None,
    finished: float | None = None,
):
    run_dir = RUNS / run_id
    if run_dir.exists():
        raise FileExistsError(f"refusing overwrite of {run_dir}")
    run_dir.mkdir(parents=True)
    started = started if started is not None else time.time()
    finished = finished if finished is not None else time.time()
    commit, dirty = git_commit_dirty()
    rss = peak_rss_bytes()
    started_at = datetime.fromtimestamp(started, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    finished_at = datetime.fromtimestamp(finished, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": stage,
            "status": status,
            "termination_reason": status,
            "code": {
                "commit": commit,
                "dirty": dirty,
                "command": command,
            },
            "inference": inference_na(),
            "environment": env_block(),
            "inputs": {
                "curve_id": parameters.get("curve_id"),
                "seed": seed,
                "parameters": parameters,
            },
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": finished - started,
            },
            "resources": {
                "peak_rss_bytes": rss,
                "cpu_seconds": None,
            },
            "result": {
                "metrics": {**metrics, "peak_rss_bytes": rss, "wall_clock_s": finished - started},
                "valid": valid,
                "invalid_reason": invalid_reason,
                "certificate": certificate,
            },
            "amazon_bedrock": "NOT SELECTED, NOT CONFIGURED, NOT PROBED, NOT CONTACTED, NOT USED.",
            "no_break_guard": True,
            "notes": "Observations only. No rho-beating / exponent / deployed-attack claim.",
        }
    }
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (run_dir / "command.txt").write_text(command + "\n", encoding="utf-8")
    (run_dir / "environment.json").write_text(json.dumps(env_block(), indent=2) + "\n", encoding="utf-8")
    (run_dir / "stdout.log").write_text(stdout, encoding="utf-8")
    (run_dir / "stderr.log").write_text(stderr, encoding="utf-8")
    payload = raw if raw is not None else {"metrics": metrics, "certificate": certificate}
    (run_dir / "raw-result.json").write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    return run_dir
