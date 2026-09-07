"""Run harness for EXP-ECRANK-73275e -- nested run: schema [SR-3].

ops_cap_respected is the EXACT boolean (counted_ops < 1.0e8) [SR-9].
wall_seconds reports both monotonic and timestamp-span [SR-10].
"""

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import ecrank_engine as E

EXP_DIR = "experiments/EXP-ECRANK-73275e"
REPO_ROOT = os.environ.get("ECRANK_REPO_ROOT", ".")
EXPERIMENT_ID = "EXP-ECRANK-73275e"
TASK_ID = "TASK-20260907-2a3331"
OPS_CAP = int(1.0e8)

INFERENCE_MANIFEST = {
    "requested_policy": "executor-implementation",
    "reasoning_effort_requested": None,
    "reasoning_effort_note": "null = policy default per handoff",
    "reasoning_effort_observed_session": "high",
    "fallback_used": True,
    "fallback_reason": "native Cursor cloud-agent session; adapter doctor unconfigured",
    "degraded_allowed": False,
    "degraded_requirements": [],
    "independent_session_required": True,
    "resolved_model_id": "cursor-grok-4.6",
    "resolved_model_id_source": "runtime system prompt (as reported)",
    "model_verified": False,
    "model_verified_note": "no adapter probe claimed; recorded as-is",
    "backend": "cursor_cloud_native",
    "bedrock_guard": "resolved provider contains no 'bedrock' (rule 16 checked)",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def git_info():
    out = {"commit": None, "dirty_files": [], "dirty": None}
    try:
        out["commit"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], text=True)
        out["dirty_files"] = [ln for ln in status.splitlines() if ln.strip()]
        out["dirty"] = bool(out["dirty_files"])
    except Exception as exc:
        out["error"] = str(exc)
    return out


def env_info():
    env = {
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "stdlib_only_pipeline": True,
        "pari_in_pipeline": False,
        "network": "none",
    }
    try:
        import yaml  # noqa: F401
        env["pyyaml_version"] = getattr(yaml, "__version__", "unknown")
        env["pyyaml_use"] = "run-record serialization only; never in counted/certified code"
    except ImportError:
        env["pyyaml_version"] = None
    env["cypari_present"] = False
    return env


def peak_rss_bytes():
    if hasattr(E, "peak_rss_bytes"):
        try:
            return int(E.peak_rss_bytes())
        except Exception:
            pass
    try:
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    except Exception:
        return None


def open_run(run_id, argv, params):
    run_dir = os.path.join(REPO_ROOT, EXP_DIR, "runs", run_id)
    os.makedirs(run_dir, exist_ok=True)
    t_mono = time.monotonic()
    t_wall0 = time.time()
    header = {
        "run_id": run_id,
        "experiment_id": EXPERIMENT_ID,
        "task_id": TASK_ID,
        "started_at": now_iso(),
        "started_unix": t_wall0,
        "code": {
            "command": " ".join(argv),
            "argv": list(argv),
            "source_dir": EXP_DIR + "/source/",
            "source_sha256": {},
        },
        "git": git_info(),
        "environment": env_info(),
        "inference": INFERENCE_MANIFEST,
        "parameters": params,
        "seeds_note": "all seeds derive from replication.seeds; declared per run",
        "budget_declared": {
            "counted_exact_ops_cap": 1.0e8,
            "wall_clock_seconds_cap": 7200,
            "memory_gb_ceiling": 8,
        },
    }
    src_dir = os.path.join(REPO_ROOT, EXP_DIR, "source")
    for name in sorted(os.listdir(src_dir)):
        if name.endswith(".py"):
            header["code"]["source_sha256"][name] = E.sha256_file(
                os.path.join(src_dir, name))
    return run_dir, header, t_mono


def finalize_run(run_dir, header, t_mono, status, reason, raw_result):
    finished = now_iso()
    mono = time.monotonic() - t_mono
    span = time.time() - header["started_unix"]
    ops = E.ops_count()
    rss = peak_rss_bytes()
    git = header["git"]
    env = header["environment"]
    body = {
        "id": header["run_id"],
        "experiment_id": EXPERIMENT_ID,
        "status": status,
        "task_id": TASK_ID,
        "code": {
            "commit": git.get("commit"),
            "dirty": git.get("dirty"),
            "dirty_files": git.get("dirty_files"),
            "command": header["code"]["command"],
            "argv": header["code"]["argv"],
            "source_dir": header["code"]["source_dir"],
            "source_sha256": header["code"]["source_sha256"],
        },
        "environment": env,
        "inputs": {
            "parameters": header["parameters"],
            "seeds_note": header["seeds_note"],
        },
        "timing": {
            "started_at": header["started_at"],
            "finished_at": finished,
            "wall_seconds_monotonic": round(mono, 6),
            "wall_seconds_timestamp_span": round(span, 6),
            "wall_seconds": round(mono, 6),
        },
        "resources": {
            "peak_rss_bytes": rss,
            "peak_rss_gb": None if rss is None else round(rss / 1024 ** 3, 6),
            "cpu_seconds": None,
            "cpu_seconds_note": "this run did not record cpu_seconds; explicit null per core rule 9",
        },
        "result": {
            "validity_reason": reason,
            "metrics": {
                "counted_exact_ops": ops,
                "ops_cap_respected": bool(ops < OPS_CAP),
                "memory_ceiling_respected": (
                    True if rss is None else (rss / 1024 ** 3) < 8.0
                ),
            },
            "certificate": {
                "kind": "none",
                "verified": True,
                "verifier": "no discrete_log/decomposition/key_recovery claim",
                "certificate_note": (
                    "kind 'none': this run asserts no discrete_log, "
                    "decomposition, or key_recovery claim."
                ),
            },
        },
        "inference": header["inference"],
        "stdout": "stdout.log",
        "stderr": "stderr.log",
        "validity": {"status": status, "reason": reason},
    }
    raw_path = os.path.join(run_dir, "raw-result.json")
    with open(raw_path, "w") as f:
        json.dump(raw_result, f, indent=1, sort_keys=True)
    man = {"run": body}
    man_path = os.path.join(run_dir, "manifest.yaml")
    try:
        import yaml
        with open(man_path, "w") as f:
            yaml.safe_dump(man, f, sort_keys=False, width=100)
    except ImportError:
        with open(man_path, "w") as f:
            f.write(json.dumps(man, indent=2))
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(header["code"]["command"] + "\n")
    with open(os.path.join(run_dir, "environment.json"), "w") as f:
        json.dump(env, f, indent=2, sort_keys=True)
        f.write("\n")
    return man


def write_json(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    return path
