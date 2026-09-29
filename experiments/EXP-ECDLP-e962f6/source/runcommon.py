"""Shared run wrapper for EXP-ECDLP-e962f6 (Stages 1-2).

Each runner writes <run-dir>/run-meta.json (run-specific fields: kind,
params, seeds, validity, reason, key results). The wrapper then:
  - writes command.txt (the exact command),
  - runs the runner as a subprocess, capturing stdout.log / stderr.log,
  - measures wall clock and peak RSS (child),
  - writes environment.json,
  - writes manifest.yaml (full artifact policy).

The runner itself also records elapsed_seconds and peak_rss_bytes inside
raw-result.json / summary.json (self-measured); the wrapper's numbers are
the external measurement.
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

import numpy as np

TASK_ID = "TASK-20260909-2989a0"
EXPERIMENT_ID = "EXP-ECDLP-e962f6"
REQUESTED_POLICY = "executor-implementation"
RESOLVED_MODEL_ID = "vllm/qwen3.8-27b"
BACKEND = "vllm (opencode runtime, local)"
MODEL_VERIFIED = False  # per DEC-20260909-0d8274 inference block; no probe run by this task
REASONING_EFFORT = None  # policy default
FALLBACK_USED = False
FALLBACK_REASON = None
DEGRADED_REQUIREMENTS = []


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_state() -> dict:
    def sh(cmd):
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
    head = sh("git rev-parse HEAD").stdout.strip()
    branch = sh("git rev-parse --abbrev-ref HEAD").stdout.strip()
    status = sh("git status --porcelain").stdout.strip()
    dirty = bool(status)
    return {"commit": head, "branch": branch, "dirty": dirty,
            "status_porcelain": status.splitlines() if dirty else []}


def environment() -> dict:
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "numpy_version": np.__version__,
        "scipy_version": __import__("scipy").__version__,
        "cpu_count": os.cpu_count(),
        "threads": "single process, numpy vectorised (no explicit thread pinning)",
    }


def yaml_scalar(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    s = str(v)
    if any(c in s for c in ":#{}[]") or s != s.strip() or s == "":
        return json.dumps(s)
    return s


def to_yaml(obj, indent=0) -> str:
    pad = "  " * indent
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{k}:")
                lines.append(to_yaml(v, indent + 1))
            elif isinstance(v, dict):
                lines.append(f"{pad}{k}: {{}}")
            elif isinstance(v, list):
                lines.append(f"{pad}{k}: []")
            else:
                lines.append(f"{pad}{k}: {yaml_scalar(v)}")
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(to_yaml(v, indent + 1))
            else:
                lines.append(f"{pad}- {yaml_scalar(v)}")
    return "\n".join(lines)


def run(run_dir: str, argv: list[str]) -> int:
    """Run the runner subprocess; write command.txt, logs, environment.json,
    manifest.yaml. Returns the runner's exit code."""
    os.makedirs(run_dir, exist_ok=True)
    cwd = os.getcwd()
    # absolute script path so the command is unambiguous regardless of cwd
    cmd = [sys.executable] + argv
    if len(cmd) > 1 and not os.path.isabs(cmd[1]):
        cmd[1] = os.path.join(cwd, cmd[1])
    command_line = " ".join(cmd)
    with open(os.path.join(run_dir, "command.txt"), "w") as fh:
        fh.write(command_line + "\n")

    t0 = time.time()
    started = now_iso()
    proc = subprocess.run(cmd, stdout=open(os.path.join(run_dir, "stdout.log"), "w"),
                          stderr=open(os.path.join(run_dir, "stderr.log"), "w"))
    wall = time.time() - t0
    ended = now_iso()
    peak_rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss  # bytes on macOS
    rc = proc.returncode

    with open(os.path.join(run_dir, "environment.json"), "w") as fh:
        json.dump(environment(), fh, indent=1)

    meta_path = os.path.join(run_dir, "run-meta.json")
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path) as fh:
            meta = json.load(fh)

    manifest = {
        "run": {
            "id": meta.get("run_id"),
            "experiment_id": EXPERIMENT_ID,
            "task_id": TASK_ID,
            "kind": meta.get("kind"),
            "stage": meta.get("stage"),
            "status": meta.get("status", "unknown"),
            "failure_class": meta.get("failure_class"),
            "validity": meta.get("validity"),
            "validity_reason": meta.get("validity_reason"),
            "note": meta.get("note"),
        },
        "command": command_line,
        "working_directory": cwd,
        "git": git_state(),
        "code": {
            "source_dir": "experiments/EXP-ECDLP-e962f6/source/",
            "source_sha256": meta.get("source_sha256", {}),
            "reference_instrument": "experiments/EXP-ECDLP-869870/source/instrument.py (committed, read-only reference for key derivation and pointer jumping)",
        },
        "environment": environment(),
        "seeds": meta.get("seeds", {}),
        "params": meta.get("params", {}),
        "inference": {
            "requested_policy": REQUESTED_POLICY,
            "backend": BACKEND,
            "resolved_model_id": RESOLVED_MODEL_ID,
            "model_verified": MODEL_VERIFIED,
            "model_verified_note": "no adapter doctor probe run by this task; resolved model is the model serving this executor session (per DEC-20260909-0d8274 inference block, model_verified false)",
            "reasoning_effort": REASONING_EFFORT,
            "fallback_used": FALLBACK_USED,
            "fallback_reason": FALLBACK_REASON,
            "degraded_requirements": DEGRADED_REQUIREMENTS,
            "fallback_allowed": False,
            "degraded_allowed": False,
        },
        "timing": {
            "started_at": started,
            "ended_at": ended,
            "wall_clock_seconds": round(wall, 3),
            "wall_clock_limit_seconds": 600,
            "within_wall_clock_limit": bool(wall <= 600.0),
            "peak_rss_bytes": int(peak_rss),
            "peak_rss_limit_bytes": 4 * 1024 ** 3,
            "within_memory_limit": bool(peak_rss <= 4 * 1024 ** 3),
            "runner_self_reported": meta.get("self_reported", {}),
        },
        "exit_code": rc,
        "protocol_deviations": meta.get("protocol_deviations", []),
        "artifacts": ["manifest.yaml", "command.txt", "environment.json", "stdout.log",
                      "stderr.log", "raw-result.json", "summary.json"],
    }
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as fh:
        fh.write(to_yaml(manifest) + "\n")
    return rc


def source_hashes() -> dict:
    import hashlib
    out = {}
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    for name in sorted(os.listdir(src)):
        if name.endswith(".py"):
            with open(os.path.join(src, name), "rb") as fh:
                out[name] = hashlib.sha256(fh.read()).hexdigest()
    return out
