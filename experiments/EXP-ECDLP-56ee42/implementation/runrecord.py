"""
Run-record writer for EXP-ECDLP-56ee42 stage invocations.

Each stage invocation produces an immutable run record under runs/ with the
full artifact policy: exact command, git commit and dirty-tree state,
environment and dependency versions, input parameters and seeds, requested
model policy and resolved runtime model identifier, reasoning effort,
fallback and degraded flags, stdout and stderr, raw machine-readable results,
validity status and reason, timestamps and resource measurements
(wall-clock, peak_rss_bytes).

The run record is written by the driver (run_stage.py) after the stage
function returns.  The stage function writes its raw results to a
raw-result.json (or .yaml) file in the run directory; the driver captures
stdout/stderr, measures wall-clock and peak RSS, and assembles the manifest.
"""
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

import numpy as np


def _git_info(repo_root: Path) -> dict:
    """git commit and dirty-tree state."""
    def _run(args):
        try:
            return subprocess.run(
                ["git"] + args, cwd=repo_root, capture_output=True, text=True,
                timeout=30).stdout.strip()
        except Exception as e:
            return f"error: {e}"
    commit = _run(["rev-parse", "HEAD"])
    dirty = _run(["status", "--porcelain"])
    return {"commit": commit, "dirty": dirty != "", "dirty_summary": dirty[:2000]}


def _environment() -> dict:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def peak_rss_bytes() -> int:
    """Peak RSS of this process in bytes (macOS: ru_maxrss is in bytes)."""
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def write_run_record(run_dir: Path, stage: str, command: str, params: dict,
                     seeds: dict, validity: str, validity_reason: str,
                     wall_clock_s: float, stdout: str, stderr: str,
                     raw_result_file: str, model_id: str,
                     repo_root: Path) -> Path:
    """Write the full run record to run_dir.  Returns the manifest path."""
    run_dir.mkdir(parents=True, exist_ok=True)
    env = _environment()
    git = _git_info(repo_root)
    now = datetime.now(timezone.utc).isoformat()
    peak = peak_rss_bytes()

    # command.txt
    (run_dir / "command.txt").write_text(command + "\n")
    # environment.json
    (run_dir / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    # stdout.log, stderr.log
    (run_dir / "stdout.log").write_text(stdout)
    (run_dir / "stderr.log").write_text(stderr)

    manifest = {
        "run_id": run_dir.name,
        "experiment_id": "EXP-ECDLP-56ee42",
        "hypothesis_id": "H-ECDLP-a4be60",
        "task_id": "TASK-20260903-087076",
        "stage": stage,
        "recorded_at": now,
        "command": command,
        "git": git,
        "environment": env,
        "parameters": params,
        "seeds": seeds,
        "inference": {
            "requested_policy": "executor-implementation",
            "resolved_model_id": model_id,
            "model_provenance": "opencode runtime, vllm backend",
            "model_verified": False,
            "reasoning_effort": None,
            "fallback_used": False,
            "degraded_requirements": [],
        },
        "resources": {
            "wall_clock_seconds": round(wall_clock_s, 3),
            "peak_rss_bytes": peak,
        },
        "artifacts": {
            "raw_result": raw_result_file,
            "stdout": "stdout.log",
            "stderr": "stderr.log",
            "environment": "environment.json",
            "command": "command.txt",
        },
        "validity": {
            "status": validity,
            "reason": validity_reason,
        },
    }
    # write manifest.yaml (simple YAML dump)
    manifest_path = run_dir / "manifest.yaml"
    manifest_path.write_text(_dump_yaml(manifest) + "\n")
    return manifest_path


def _dump_yaml(obj, indent=0) -> str:
    """Minimal YAML dumper (no external dependency)."""
    pad = "  " * indent
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.append(_dump_yaml(v, indent + 1))
            else:
                lines.append(f"{pad}{k}: {_yaml_scalar(v)}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(_dump_yaml(item, indent + 1))
            else:
                lines.append(f"{pad}- {_yaml_scalar(item)}")
    else:
        lines.append(f"{pad}{_yaml_scalar(obj)}")
    return "\n".join(lines)


def _yaml_scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if any(c in s for c in ":#{}[]&*!|>'\"%@`") or s != s.strip() or s == "":
        return json.dumps(s)
    return s
