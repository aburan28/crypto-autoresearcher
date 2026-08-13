"""Run-record writer for EXP-FIB-001. Produces the exact artifact set the
frozen spec's required_artifacts list demands per run:
manifest.yaml, command.txt, environment.json, raw.json, summary.json,
stdout.txt, stderr.txt -- under experiments/EXP-FIB-001/runs/<RUN-ID>/.
Immutable: refuses to overwrite an existing run directory.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

import scipy
import sympy
import yaml

EXP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS_DIR = os.path.join(EXP_DIR, "runs")
REPO_ROOT = os.path.dirname(os.path.dirname(EXP_DIR))


def git_state() -> dict:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
                             capture_output=True, text=True).stdout.strip()
    status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT,
                             capture_output=True, text=True).stdout
    tracked_modified = any(
        line[:2].strip() and line[:2].strip() not in ("??",)
        for line in status.splitlines()
    )
    any_untracked_or_dirty = bool(status.strip())
    return {"commit": commit, "dirty": any_untracked_or_dirty,
            "tracked_files_modified": tracked_modified,
            "porcelain_status": status}


def environment_info() -> dict:
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "sage_version": None,
        "dependencies": {"sympy": sympy.__version__, "scipy": scipy.__version__,
                          "numpy": __import__("numpy").__version__,
                          "pyyaml": yaml.__version__},
    }


def write_run(run_id: str, *, status: str, command: str, parameters: dict,
              seeds: dict, timing: dict, resources: dict, raw: dict,
              summary: dict, stdout_text: str, stderr_text: str,
              certificate: dict, invalid_reason: str | None = None,
              deviations: list[str] | None = None,
              anomalies: list[str] | None = None) -> str:
    run_dir = os.path.join(RUNS_DIR, run_id)
    if os.path.exists(run_dir):
        raise RuntimeError(f"run directory already exists (immutability): {run_dir}")
    os.makedirs(run_dir)

    git = git_state()
    env = environment_info()

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-FIB-001",
            "status": status,
            "invalid_reason": invalid_reason,
            "code": {"commit": git["commit"], "dirty": git["dirty"],
                      "tracked_files_modified": git["tracked_files_modified"],
                      "command": command},
            "inference": {"requested_policy": "executor-implementation",
                          "resolved_model_id": "none (deterministic harness execution)",
                          "reasoning_effort": None, "fallback_used": False,
                          "adapter_version": None},
            "environment": env,
            "inputs": {"parameters": parameters, "seeds": seeds},
            "timing": timing,
            "resources": resources,
            "certificate": certificate,
            "protocol_deviations": deviations or [],
            "anomalies": anomalies or [],
            "artifacts": {"command": "command.txt", "environment": "environment.json",
                          "raw": "raw.json", "summary": "summary.json",
                          "stdout": "stdout.txt", "stderr": "stderr.txt"},
        }
    }

    with open(os.path.join(run_dir, "manifest.yaml"), "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False)
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(command + "\n")
    with open(os.path.join(run_dir, "environment.json"), "w") as f:
        json.dump(env, f, indent=2, sort_keys=True)
    with open(os.path.join(run_dir, "raw.json"), "w") as f:
        json.dump(raw, f, indent=2, sort_keys=True, default=str)
    with open(os.path.join(run_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, sort_keys=True, default=str)
    with open(os.path.join(run_dir, "stdout.txt"), "w") as f:
        f.write(stdout_text)
    with open(os.path.join(run_dir, "stderr.txt"), "w") as f:
        f.write(stderr_text)
    return run_dir


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
