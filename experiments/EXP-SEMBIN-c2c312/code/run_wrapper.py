#!/usr/bin/env python3
"""Wrapper for RUN-SEMBIN-595308: records environment, git identity, engine
versions and the exact command, then runs run_cells.py with logs captured."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

CODE = Path(__file__).resolve().parent
REPO = CODE.parents[2]
RUN = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO / "experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-595308"
EXTRA = sys.argv[2:]
RUN.mkdir(parents=True, exist_ok=True)


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=REPO).stdout.strip()
    except Exception as exc:  # pragma: no cover
        return f"error: {exc}"


cmd = [sys.executable, str(CODE / "run_cells.py"), "--out-dir", str(RUN / "cells")] + EXTRA
(RUN / "command.txt").write_text(" ".join(cmd) + f"\nworking_directory: {CODE}\n")
env = {
    "python_executable": sys.executable,
    "python_version": platform.python_version(),
    "python_implementation": platform.python_implementation(),
    "operating_system": platform.platform(),
    "architecture": platform.machine(),
    "processor_count": os.cpu_count(),
    "hostname": platform.node(),
    "cwd": str(CODE),
    "msolve_version": sh(["msolve", "-h"]).splitlines()[0] if sh(["msolve", "-h"]) else None,
    "m4ri_package": sh(["dpkg-query", "-W", "-f=${Version}", "libm4ri-dev"]),
    "singular_package": sh(["dpkg-query", "-W", "-f=${Version}", "singular"]),
    "gcc_version": sh(["gcc", "--version"]).splitlines()[0],
    "git_commit": sh(["git", "rev-parse", "HEAD"]),
    "git_branch": sh(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
    "git_dirty": bool(sh(["git", "status", "--porcelain"])),
    "code_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(CODE.iterdir()) if p.is_file() and p.suffix in (".py", ".c", ".so")},
    "started_at": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
}
(RUN / "environment.json").write_text(json.dumps(env, indent=2, sort_keys=True) + "\n")
t0 = time.time()
with open(RUN / "stdout.log", "a") as so, open(RUN / "stderr.log", "a") as se:
    proc = subprocess.run(cmd, cwd=CODE, stdout=so, stderr=se)
env["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
env["wall_seconds"] = time.time() - t0
env["exit_code"] = proc.returncode
(RUN / "environment.json").write_text(json.dumps(env, indent=2, sort_keys=True) + "\n")
print(f"wrapper_exit={proc.returncode} wall={time.time()-t0:.1f}s")
sys.exit(proc.returncode)
