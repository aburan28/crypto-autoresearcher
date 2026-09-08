#!/usr/bin/env python3
"""Driver for the EXP-ECDLP-56ee42 corrected Stage 0-2 re-run (amendment v3
V3-CHG-2 / V3-CHG-4; RC of TASK-20260908-d54138).

Runs a stage script (stage0/stage1/stage2) as a subprocess with the corrected
estimator, captures stdout/stderr/wall-clock/peak-RSS, and assembles a
schema-conformant run manifest (schemas/run-manifest.schema.json, validated
with jsonschema) plus the full artifact set required by the handoff:
  manifest.yaml, command.txt (verbatim plain string), environment.json,
  stdout.log, stderr.log, raw-result.json.

The manifest carries the git commit and honest dirty-tree state, the actual
applied seeds (from the stage's raw-result.json "seeds" section, per V3-RA-4),
environment/dependency versions, the requested model policy with the resolved
runtime model id and probe-verification status, stdout+stderr, raw results,
validity + reason, timestamps, wall-clock, and peak RSS.

Usage (from the experiment root):
    python3 implementation/run_stage_v3.py --stage stage0 --run-id RUN-ECDLP-56ee42-S0v3
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

EXP_ROOT = Path(__file__).resolve().parent.parent          # experiments/EXP-ECDLP-56ee42
IMPL_DIR = EXP_ROOT / "implementation"
REPO_ROOT = EXP_ROOT.parent.parent                          # worktree root
SCHEMA_PATH = REPO_ROOT / "schemas" / "run-manifest.schema.json"

BASE_SEED = 0x56EE42
MODEL_ID = "vllm/qwen3.8-27b"
REQUESTED_POLICY = "executor-implementation"

# Frozen ladder (design/ladder.json; reproduced exactly in the AUDIT step).
LADDER = [
    {"T": 17, "p": 131101, "b": 27, "N": 131113},
    {"T": 19, "p": 524309, "b": 80, "N": 525361},
    {"T": 21, "p": 2097169, "b": 1, "N": 2098321},
    {"T": 23, "p": 8388617, "b": 21, "N": 8391797},
    {"T": 25, "p": 33554473, "b": 49, "N": 33557891},
    {"T": 27, "p": 134217757, "b": 70, "N": 134234689},
]


def _git_info() -> tuple[str, bool]:
    def run(args):
        try:
            return subprocess.run(["git"] + args, cwd=REPO_ROOT,
                                  capture_output=True, text=True,
                                  timeout=30).stdout.strip()
        except Exception as e:  # noqa: BLE001
            return f"error: {e}"
    commit = run(["rev-parse", "HEAD"])
    dirty = run(["status", "--porcelain"])
    return commit, (dirty != "")


def _environment() -> dict:
    import numpy as np
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


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


def _dump_yaml(obj, indent=0) -> str:
    pad = "  " * indent
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{k}:")
                lines.append(_dump_yaml(v, indent + 1))
            elif isinstance(v, dict):
                lines.append(f"{pad}{k}: {{}}")
            elif isinstance(v, list):
                lines.append(f"{pad}{k}: []")
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


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True,
                    choices=["stage0", "stage1", "stage2", "calibration_c2"])
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args(argv)
    stage, run_id = args.stage, args.run_id

    run_dir = EXP_ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    script = IMPL_DIR / f"{stage}.py"
    command = (f"EXP_RUN_ID={run_id} PYTHONPATH=implementation "
               f"python3 implementation/{stage}.py")

    env = dict(os.environ)
    env["PYTHONPATH"] = "implementation"
    env["EXP_RUN_ID"] = run_id

    started = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    proc = subprocess.run([sys.executable, str(script)], cwd=EXP_ROOT, env=env,
                          capture_output=True, text=True)
    wall = time.time() - t0
    finished = datetime.now(timezone.utc).isoformat()

    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak_rss = int(child.ru_maxrss)          # bytes on macOS
    cpu_seconds = child.ru_utime + child.ru_stime

    # --- artifacts ---
    (run_dir / "command.txt").write_text(command + "\n")
    (run_dir / "environment.json").write_text(json.dumps(_environment(), indent=2) + "\n")
    (run_dir / "stdout.log").write_text(proc.stdout)
    (run_dir / "stderr.log").write_text(proc.stderr)

    raw_path = run_dir / "raw-result.json"
    raw = json.loads(raw_path.read_text()) if raw_path.exists() else {}
    seeds = raw.get("seeds", {})

    # Stage-aware validity: stage0 carries no "validity" field; its gate is
    # P3 (a polylog digit norm drops the arm, F1).  stage1/stage2 set
    # "validity" explicitly.
    if stage == "stage0":
        gate_p3 = raw.get("gate_P3", {})
        valid = all(not g.get("F1", False) for g in gate_p3.values())
        invalid_reason = (None if valid else
                          "P3: polylog digit norm dropped an arm (F1): "
                          + str({s: g for s, g in gate_p3.items() if g.get("F1")}))
    else:
        valid = raw.get("validity") == "valid"
        invalid_reason = None if valid else raw.get("validity_reason")
    status = "completed_valid" if valid else "completed_invalid"
    commit, dirty = _git_info()

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-ECDLP-56ee42",
            "status": status,
            "code": {"commit": commit, "dirty": dirty, "command": command},
            "environment": _environment(),
            "inputs": {
                "curve_id": None,  # multi-rung ladder; curves in parameters
                "seed": BASE_SEED,
                "parameters": {
                    "stage": stage,
                    "ladder": LADDER,
                    "seeds": seeds,
                    "exit_code": proc.returncode,
                },
            },
            "timing": {
                "started_at": started,
                "finished_at": finished,
                "wall_seconds": round(wall, 3),
                "total_wall_seconds": round(wall, 3),
            },
            "resources": {
                "peak_rss_bytes": peak_rss,
                "cpu_seconds": round(cpu_seconds, 3),
            },
            "result": {
                "metrics": raw.get("gates", raw),
                "valid": valid,
                "invalid_reason": invalid_reason,
                "certificate": {"kind": "none", "verified": None,
                                "verifier": None},
            },
            "artifacts": {
                "raw_result": "raw-result.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "environment": "environment.json",
                "command": "command.txt",
            },
            "inference": {
                "requested_policy": REQUESTED_POLICY,
                "resolved_model_id": MODEL_ID,
                "model_provenance": "opencode runtime, vllm backend",
                "model_verified": False,
                "reasoning_effort": None,
                "fallback_used": False,
                "degraded_requirements": [],
            },
        }
    }
    (run_dir / "manifest.yaml").write_text(_dump_yaml(manifest) + "\n")

    # --- schema validation ---
    import jsonschema
    schema = json.loads(SCHEMA_PATH.read_text())
    jsonschema.validate(manifest, schema)

    print(f"[{run_id}] status={status} exit={proc.returncode} "
          f"wall={wall:.1f}s peak_rss={peak_rss}B cpu={cpu_seconds:.1f}s")
    print(f"[{run_id}] manifest schema-VALID: {run_dir / 'manifest.yaml'}")
    return 0 if proc.returncode == 0 else proc.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
