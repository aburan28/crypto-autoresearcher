"""Write immutable run records for EXP-ECDLP-a98ea9 stage invocations."""
from __future__ import annotations

import json
import platform
import resource
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _git_info(repo_root: Path) -> dict:
    def _run(args):
        try:
            return subprocess.run(
                ["git"] + args,
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=30,
            ).stdout.strip()
        except Exception as exc:
            return f"error: {exc}"

    commit = _run(["rev-parse", "HEAD"])
    dirty = _run(["status", "--porcelain"])
    return {"commit": commit, "dirty": dirty != "", "dirty_summary": dirty[:2000]}


def _environment() -> dict:
    env = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }
    try:
        import sympy

        env["sympy"] = sympy.__version__
    except Exception:
        env["sympy"] = None
    return env


def peak_rss_bytes() -> int:
    # Linux: ru_maxrss is kilobytes.
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


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


def write_run_record(
    run_dir: Path,
    stage: str,
    command: str,
    params: dict,
    seeds: dict,
    validity: str,
    validity_reason: str,
    wall_clock_s: float,
    stdout: str,
    stderr: str,
    raw_result_file: str,
    model_id: str,
    repo_root: Path,
    extra_artifacts: dict | None = None,
    task_id: str = "TASK-20260907-cd0cf9",
    scientific_boundary: str | None = None,
) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    env = _environment()
    git = _git_info(repo_root)
    now = datetime.now(timezone.utc).isoformat()
    peak = peak_rss_bytes()
    (run_dir / "command.txt").write_text(command + "\n")
    (run_dir / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    (run_dir / "stdout.log").write_text(stdout)
    (run_dir / "stderr.log").write_text(stderr)
    artifacts = {
        "raw_result": raw_result_file,
        "stdout": "stdout.log",
        "stderr": "stderr.log",
        "environment": "environment.json",
        "command": "command.txt",
    }
    if extra_artifacts:
        artifacts.update(extra_artifacts)
    manifest = {
        "run_id": run_dir.name,
        "experiment_id": "EXP-ECDLP-a98ea9",
        "hypothesis_id": "H-ECDLP-07c7c6",
        "task_id": task_id,
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
            "model_provenance": "cursor cloud agent session acting as executor",
            "model_verified": False,
            "reasoning_effort": "medium",
            "fallback_used": False,
            "degraded_requirements": [],
        },
        "resources": {
            "wall_clock_seconds": round(wall_clock_s, 3),
            "peak_rss_bytes": peak,
        },
        "artifacts": artifacts,
        "certificate": {"kind": "none"},
        "validity": {"status": validity, "reason": validity_reason},
        "scientific_boundary": scientific_boundary
        or (
            "Stage 0-1 only. No ADV, no D2 disposition, no attack, no breakthrough."
        ),
    }
    path = run_dir / "manifest.yaml"
    path.write_text(_dump_yaml(manifest) + "\n")
    return path
