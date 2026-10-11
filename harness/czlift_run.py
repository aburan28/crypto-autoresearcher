"""Run-record writer shared by the three GOAL-CZLIFT-1516d5 drivers.

Writes the canonical run package into a directory the trial-plan supervisor
(tools/experiment_execution.py) has already created: manifest.yaml,
raw-result.json, and (if the supervisor did not write them first) command.txt,
environment.json, stdout.log and stderr.log. Never overwrites a file that
exists. Carries no scientific content; the driver's metrics are recorded
verbatim and are observations until the Coordinator reviews them.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                              text=True, check=False).stdout.strip()
    except OSError:
        return ""


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _write_once(path: str, text: str) -> None:
    if os.path.exists(path):
        return
    with open(path, "x", encoding="utf-8") as fh:
        fh.write(text)


def write_run_record(run_dir: str, *, run_id: str, exp_id: str, status: str,
                     command: list[str], sources: list[str], seed: int | None,
                     parameters: dict, metrics: dict, raw: dict,
                     started: float, finished: float,
                     curve_id: str = "czlift-toy-family",
                     valid: bool = True, invalid_reason: str | None = None,
                     stdout: str = "", stderr: str = "") -> str:
    os.makedirs(run_dir, exist_ok=True)
    commit = _git("rev-parse", "HEAD") or "unknown"
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no"))
    source = {os.path.relpath(s, REPO): sha256_file(s) for s in sources}
    env = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
    }
    manifest = {"run": {
        "id": run_id,
        "experiment_id": exp_id,
        "status": status,
        "code": {"commit": commit, "dirty": dirty,
                 "command": " ".join(command), "source_sha256": source},
        "environment": env,
        "inputs": {"curve_id": curve_id, "seed": seed, "parameters": parameters},
        "timing": {
            "started_at": datetime.fromtimestamp(started, tz=timezone.utc).isoformat(),
            "finished_at": datetime.fromtimestamp(finished, tz=timezone.utc).isoformat(),
            "wall_seconds": round(finished - started, 6),
            "timing_source": "driver_monotonic_bracket",
        },
        "result": {
            "metrics": metrics,
            "valid": valid,
            "invalid_reason": invalid_reason,
            "certificate": {"kind": "none"},
            "outcome_note": "Observation only. No hypothesis status changes here.",
        },
        "artifacts": {"command": "command.txt", "environment": "environment.json",
                      "stdout": "stdout.log", "stderr": "stderr.log",
                      "raw_result": "raw-result.json"},
    }}
    _write_once(os.path.join(run_dir, "manifest.yaml"),
                yaml.safe_dump(manifest, sort_keys=False))
    _write_once(os.path.join(run_dir, "raw-result.json"),
                json.dumps({"metrics": metrics, "certificate": {"kind": "none"},
                            "raw": raw}, indent=1, sort_keys=True, default=str) + "\n")
    _write_once(os.path.join(run_dir, "command.txt"), json.dumps(command) + "\n")
    _write_once(os.path.join(run_dir, "environment.json"),
                json.dumps(env, indent=2, sort_keys=True) + "\n")
    _write_once(os.path.join(run_dir, "stdout.log"), stdout)
    _write_once(os.path.join(run_dir, "stderr.log"), stderr)
    return run_id


def now() -> float:
    return time.time()
