#!/usr/bin/env python3
"""Run wrapper for EXP-QSP-82a906: one immutable directory per stage."""
from __future__ import annotations

import datetime
import json
import os
import platform
import resource
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
EXP_DIR = os.path.join(REPO, "experiments", "EXP-QSP-82a906")
RUNS_DIR = os.path.join(EXP_DIR, "runs")
IMPL = os.path.join(EXP_DIR, "implementation")

EXPERIMENT_ID = "EXP-QSP-82a906"
HYPOTHESIS_ID = "H-QSP-411d8f"
TASK_ID = "TASK-20260917-66ec2b"

INFERENCE = {
    "requested_policy": "executor-implementation",
    "requested_policy_source": "ledger/handoffs/%s.yaml inference.policy" % TASK_ID,
    "reasoning_effort": "medium",
    "reasoning_effort_source": "handoff inference.reasoning_effort; orchestration/model-policies.yaml executor-implementation",
    "backend": "cursor cloud agent runtime",
    "adapter_resolved_binding": "anthropic:claude-sonnet-5",
    "adapter_resolve_command": "python3 -m orchestration.adapter resolve --role executor",
    "resolved_model_id": "cursor-grok-4.6",
    "model_provenance": (
        "Self-reported by the serving runtime (Cursor Grok 4.6). The adapter "
        "binding for executor-implementation is anthropic:claude-sonnet-5. "
        "Recorded rather than silently substituted. The Executor did not select "
        "the serving model."
    ),
    "probe_verified": False,
    "probe_status": "not probe-verified: no model probe was run in this session",
    "fallback_used": False,
    "fallback_reason": None,
    "degraded_requirements": [],
    "model_in_the_measurement_loop": False,
    "model_in_the_measurement_loop_note": (
        "Every number comes from deterministic C/Python arithmetic in "
        "experiments/EXP-QSP-82a906/implementation/. No model output enters "
        "deg_elim, rho, or a certificate."
    ),
}


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True).stdout.strip()


def git_state() -> dict:
    status = git("status", "--porcelain")
    return {
        "commit": git("rev-parse", "HEAD"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(status),
        "dirty_paths": [l[3:] for l in status.splitlines()] if status else [],
        "dirty_tree_note": (
            "The working tree carries this task's write scope "
            "(experiments/EXP-QSP-82a906/implementation, runs, "
            "execution-report.yaml) uncommitted: the Executor does not commit. "
            "A later Coordinator snapshot archive commits the package."
        ),
    }


def compiler_info() -> dict:
    try:
        v = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    except Exception as exc:
        v = "unavailable: %s" % exc
    return {
        "compiler": v,
        "flags": "-O2",
        "helper_source": "implementation/i1_sylvester.c",
        "helper_binary": "implementation/i1_sylvester (built at run time, not committed)",
    }


def environment() -> dict:
    deps = {}
    try:
        import numpy
        deps["numpy"] = numpy.__version__
    except Exception:
        deps["numpy"] = "not installed"
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "hostname_class": "container",
        "cpu_count": os.cpu_count(),
        "dependencies": deps,
        "external_engines": {
            "sage": "not installed",
            "sympy": "not imported",
            "magma": "not installed",
            "macaulay2": "not installed",
            "singular": "not installed",
            "msolve": "not installed",
            "ntl_or_flint": "not installed",
        },
        "compiler": compiler_info(),
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", "unset"),
    }


class Run:
    def __init__(self, run_id: str, stage: str, command: str, inputs: dict):
        self.run_id = run_id
        self.stage = stage
        self.command = command
        self.inputs = inputs
        self.dir = os.path.join(RUNS_DIR, run_id)
        if os.path.exists(self.dir):
            raise SystemExit("REFUSING to reuse run directory %s" % self.dir)
        os.makedirs(self.dir)
        self.t0 = time.time()
        self.started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.git = git_state()
        self.env = environment()
        self.stdout_lines: list[str] = []
        self.stderr_lines: list[str] = []
        with open(os.path.join(self.dir, "command.txt"), "w") as fh:
            fh.write(command + "\n")
        with open(os.path.join(self.dir, "environment.json"), "w") as fh:
            json.dump(self.env, fh, indent=1, sort_keys=True)

    def log(self, *parts) -> None:
        line = " ".join(str(p) for p in parts)
        self.stdout_lines.append(line)
        print(line, flush=True)

    def warn(self, *parts) -> None:
        line = " ".join(str(p) for p in parts)
        self.stderr_lines.append(line)
        print(line, file=sys.stderr, flush=True)

    def finish(self, raw: dict, status: str, validity_reason: str) -> None:
        wall = time.time() - self.t0
        ru = resource.getrusage(resource.RUSAGE_SELF)
        ruc = resource.getrusage(resource.RUSAGE_CHILDREN)
        with open(os.path.join(self.dir, "raw-result.json"), "w") as fh:
            json.dump(raw, fh, indent=1, sort_keys=True, default=str)
        with open(os.path.join(self.dir, "stdout.log"), "w") as fh:
            fh.write("\n".join(self.stdout_lines) + "\n")
        with open(os.path.join(self.dir, "stderr.log"), "w") as fh:
            fh.write("\n".join(self.stderr_lines) + ("\n" if self.stderr_lines else ""))
        manifest = {
            "run": {
                "id": self.run_id,
                "experiment_id": EXPERIMENT_ID,
                "hypothesis_id": HYPOTHESIS_ID,
                "task_id": TASK_ID,
                "stage": self.stage,
                "status": status,
                "specification_version": 2,
                "amendments_in_force": ["experiments/EXP-QSP-82a906/amendments/v2.yaml"],
                "code": {
                    "command": self.command,
                    "commit": self.git["commit"],
                    "branch": self.git["branch"],
                    "dirty": self.git["dirty"],
                    "dirty_paths": self.git["dirty_paths"],
                    "dirty_tree_note": self.git["dirty_tree_note"],
                    "implementation_paths": [
                        "experiments/EXP-QSP-82a906/implementation/i1_sylvester.c",
                        "experiments/EXP-QSP-82a906/implementation/i2_python.py",
                        "experiments/EXP-QSP-82a906/implementation/chain.py",
                        "experiments/EXP-QSP-82a906/implementation/driver.py",
                    ],
                },
                "inference": INFERENCE,
                "environment": self.env,
                "inputs": self.inputs,
                "timing": {
                    "started_at": self.started_at,
                    "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "wall_seconds": round(wall, 3),
                    "budget_wall_clock_seconds": 1800,
                    "budget_exceeded": wall > 1800,
                },
                "resources": {
                    "peak_rss_bytes": max(ru.ru_maxrss, ruc.ru_maxrss) * 1024,
                    "peak_rss_bytes_note": "ru_maxrss (KiB on Linux) x 1024, self and children",
                    "cpu_seconds": round(ru.ru_utime + ru.ru_stime + ruc.ru_utime + ruc.ru_stime, 3),
                    "workers": 1,
                    "memory_cap_gb": 4,
                },
                "result": {
                    "valid": status == "completed_valid",
                    "validity_status": status,
                    "validity_reason": validity_reason,
                    "certificate": {"kind": "none", "verified": None, "verifier": None},
                    "raw_result": "raw-result.json",
                },
                "protocol_deviations": [],
                "anomalies": [],
                "artifacts": {
                    "command": "command.txt",
                    "environment": "environment.json",
                    "stdout": "stdout.log",
                    "stderr": "stderr.log",
                    "raw_result": "raw-result.json",
                    "manifest_v2": "manifest_v2.yaml",
                },
                "provenance_declaration": (
                    "Every number in raw-result.json was produced by this invocation. "
                    "No value was read from analysis/qsp-ecc2k130/explore/."
                ),
            }
        }
        try:
            import yaml
            with open(os.path.join(self.dir, "manifest_v2.yaml"), "w") as fh:
                yaml.safe_dump(manifest, fh, sort_keys=False)
            with open(os.path.join(self.dir, "manifest.yaml"), "w") as fh:
                yaml.safe_dump(manifest, fh, sort_keys=False)
        except Exception:
            with open(os.path.join(self.dir, "manifest_v2.yaml"), "w") as fh:
                json.dump(manifest, fh, indent=1)
            with open(os.path.join(self.dir, "manifest.yaml"), "w") as fh:
                json.dump(manifest, fh, indent=1)
