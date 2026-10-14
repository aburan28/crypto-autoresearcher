"""Write-once artifact envelope for the four lattice experiment drivers.

Canonical provenance comes from the existing supervisor's launch/environment
files. Standalone outputs explicitly remain development observations.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import shlex
import sys
import time


def write_artifacts(result: dict, directory: Path, seed: int,
                    started: str, wall_start: float, cpu_start: float) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    launch_path, env_path = directory / "launch.json", directory / "environment.json"
    supervised = launch_path.is_file() and env_path.is_file()
    if supervised:
        launch, environment = json.loads(launch_path.read_text()), json.loads(env_path.read_text())
        run_id = launch["run_id"]
        experiment_id = directory.parent.parent.name
        commit = environment["commit"]
        command = launch["argv"]
        dirty = environment.get("dirty_tree")
    else:
        run_id, experiment_id, commit = "RUN-DEVELOPMENT-000", "EXP-DEVELOPMENT-000", "uncommitted_development"
        environment = {"python": sys.version, "platform": platform.platform(), "dependencies": "Python standard library"}
        command, dirty = [sys.executable, *sys.argv], True
    finished = datetime.now(timezone.utc).isoformat()
    manifest = {"run": {
        "id": run_id, "experiment_id": experiment_id,
        "status": "completed" if supervised else "development_only",
        "code": {"commit": commit, "command": shlex.join(command), "argv": command,
                 "dirty_tree": dirty, "source_binding": environment.get("source_sha256", {}),
                 "dirty_tree_note": "Full working-tree state not sampled by this driver; supervisor admits each committed source hash.",
                 "provenance": "existing_supervisor" if supervised else "standalone_development"},
        "environment": environment,
        "inputs": {"parameters": result["parameters"], "seeds": [seed],
                   "instance_policy": "supplied exact synthetic lattices with planted ambient orders"},
        "timing": {"started_at": started, "finished_at": finished,
                   "wall_seconds": time.monotonic() - wall_start,
                   "process_cpu_seconds": time.process_time() - cpu_start,
                   "measurement_scope": "driver arithmetic and raw-result assembly; checker/supervisor costs separate"},
        "result": {"raw_result": "raw-result.json", "outcome": "observations_only",
                   "checks": result["checks"], "certificate": {"kind": "none"},
                   "interpretation": "No independent scientific review or official hypothesis promotion."},
    }}
    for filename, value in (("raw-result.json", result), ("manifest.yaml", manifest)):
        with (directory / filename).open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
