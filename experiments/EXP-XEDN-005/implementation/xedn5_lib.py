#!/usr/bin/env python3
"""EXP-XEDN-005 helpers: frozen predicate loader and run writers."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FROZEN_PATH = os.path.join(REPO_ROOT, "experiments", "EXP-XEDN-001", "xedni_sections.py")
EXP_DIR = os.path.join(REPO_ROOT, "experiments", "EXP-XEDN-005")

SIZES = [7, 13, 19, 31]
SEEDS = [2026072511, 2026072512]
SAGE = os.environ.get(
    "SAGE",
    "/opt/homebrew/Caskroom/sage/10.9,10.9.0/SageMath-10-9.app/Contents/Frameworks/Sage.framework/Versions/10.9/local/bin/sage",
)


def load_frozen():
    with open(FROZEN_PATH, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    spec = importlib.util.spec_from_file_location("xedn001_frozen", FROZEN_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod, digest


def git_state() -> dict[str, Any]:
    def run(args: list[str]) -> str:
        return subprocess.check_output(args, cwd=REPO_ROOT, text=True).strip()

    dirty = run(["git", "status", "--porcelain"])
    return {
        "commit": run(["git", "rev-parse", "HEAD"]),
        "branch": run(["git", "branch", "--show-current"]),
        "dirty": bool(dirty),
        "dirty_summary": dirty.splitlines()[:40],
    }


def write_run(
    run_id: str,
    command: str,
    raw: dict[str, Any],
    stdout: str,
    stderr: str,
    validity: str,
    validity_reason: str,
) -> str:
    run_dir = os.path.join(EXP_DIR, "runs", run_id)
    os.makedirs(run_dir, exist_ok=True)
    env = {
        "python": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
        "sage": subprocess.getoutput(f"{SAGE} --version").splitlines()[:1],
        "frozen_xedni_sections_sha256": load_frozen()[1],
        "git": git_state(),
        "written_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(os.path.join(run_dir, "command.txt"), "w", encoding="utf-8") as fh:
        fh.write(command.rstrip() + "\n")
    with open(os.path.join(run_dir, "environment.json"), "w", encoding="utf-8") as fh:
        json.dump(env, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(run_dir, "stdout.log"), "w", encoding="utf-8") as fh:
        fh.write(stdout)
    with open(os.path.join(run_dir, "stderr.log"), "w", encoding="utf-8") as fh:
        fh.write(stderr)
    with open(os.path.join(run_dir, "raw-result.json"), "w", encoding="utf-8") as fh:
        json.dump(raw, fh, indent=2)
        fh.write("\n")
    # also results.json alias required by specification
    with open(os.path.join(run_dir, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(raw, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(run_dir, "manifest.yaml"), "w", encoding="utf-8") as fh:
        fh.write(f"run_id: {run_id}\n")
        fh.write("experiment_id: EXP-XEDN-005\n")
        fh.write("hypothesis_id: H-XEDN-004\n")
        fh.write(f"validity: {validity}\n")
        fh.write(f"validity_reason: {json.dumps(validity_reason)}\n")
        fh.write("inference:\n")
        fh.write("  requested_policy: executor-terra\n")
        fh.write("  resolved_model: cursor-grok-4.5\n")
        fh.write("  fallback_used: true\n")
        fh.write(
            '  fallback_reason: "GPT-5.6 Terra alias unresolved in Cursor harness."\n'
        )
        fh.write(f"git_commit: {env['git']['commit']}\n")
    return run_dir
