"""
Run-manifest writer, per docs/evidence-and-reproducibility.md "Minimum run
manifest" and the task handoff's inference-provenance requirements.
"""
from __future__ import annotations
import json
import os
import platform
import subprocess
import sys
import time
import yaml


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=os.path.dirname(__file__), text=True
        ).strip()
    except Exception:
        return "UNKNOWN"


def git_dirty() -> bool:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=os.path.dirname(__file__), text=True
        )
        return bool(out.strip())
    except Exception:
        return True


INFERENCE_BLOCK = {
    "requested_policy": "executor-implementation",
    "canonical_policy": "executor-implementation",
    "backend": "claude_code",
    "provider": "anthropic",
    "resolved_model_id": "claude-sonnet-5",
    "model_provenance": "operator-supplied",
    "model_verified": False,
    "requested_reasoning_effort": None,
    "reasoning_effort": None,
    "fallback_used": False,
    "fallback_reason": None,
    "degraded_requirements": [],
    "independent_session": False,
    "adapter_version": None,
    "config_digest": None,
    "note": (
        "requested_reasoning_effort/reasoning_effort are recorded as null exactly "
        "as ledger/handoffs/TASK-20260903-58449b.yaml's inference block wrote them "
        "(inference.reasoning_effort: null); this runtime's per-subagent effort "
        "dial (CLAUDE.md model policy note) is not exposed to the running process "
        "as a readable value, so it is disclosed as absent rather than guessed."
    ),
}


def environment_block() -> dict:
    return {
        "operating_system": platform.system(),
        "architecture": platform.machine(),
        "sage_version": None,
        "python_version": sys.version.split()[0],
        "dependencies": {"sympy": __import__("sympy").__version__},
    }


def write_manifest(run_dir: str, run_id: str, experiment_id: str, command: str,
                    inputs: dict, timing: dict, resources: dict, result: dict,
                    artifacts: dict, extra: dict = None):
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": experiment_id,
            "status": result.get("status", "unknown"),
            "code": {
                "commit": git_commit(),
                "dirty": git_dirty(),
                "command": command,
            },
            "inference": INFERENCE_BLOCK,
            "environment": environment_block(),
            "inputs": inputs,
            "timing": timing,
            "resources": resources,
            "result": result,
            "artifacts": artifacts,
        }
    }
    if extra:
        manifest["run"].update(extra)
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False, default_flow_style=False)
    return manifest


def write_command_txt(run_dir: str, command: str):
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(command + "\n")


def write_environment_json(run_dir: str):
    with open(os.path.join(run_dir, "environment.json"), "w") as f:
        json.dump(environment_block(), f, indent=2)


def write_results_json(run_dir: str, results: dict):
    with open(os.path.join(run_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
