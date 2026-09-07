#!/usr/bin/env python3
"""run_common.py -- shared run harness for EXP-ECRANK-76a70d drivers.

Artifact policy per run (binding handoffs TASK-20260905-26364a /
TASK-20260906-908f6b): exact command, git commit and dirty-tree state,
environment and dependency versions, input parameters and ALL seeds,
inference manifest, complete stdout/stderr (shell-redirected by the driver
command), raw machine-readable results, validity status and reason,
timestamps, peak_rss_bytes reconciled against the declared 8 GB ceiling.

The SOLVER and CERTIFICATE pipeline is stdlib-only exact Fractions: no PARI,
no network, no floating point in any counted or certified quantity (IV-6).
PyYAML (when present) is used ONLY to serialize run records, never inside a
counted or certified computation.
"""

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import ecrank_engine as E

EXP_DIR = "experiments/EXP-ECRANK-76a70d"
REPO_ROOT = os.environ.get("ECRANK_REPO_ROOT", ".")

# inference manifest: recorded exactly as the dispatch record states, plus
# the runtime-reported model identifier; no silent alteration (rule 11).
INFERENCE_MANIFEST = {
    "requested_policy": "executor-implementation",
    "reasoning_effort_requested": None,
    "reasoning_effort_note": "null = policy default per handoff",
    "reasoning_effort_observed_session": "xhigh",
    "fallback_used": True,
    "fallback_reason": "role-bound executor binding balance-dead",
    "degraded_allowed": False,
    "degraded_requirements": [],
    "independent_session_required": False,
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "resolved_model_id_source": "runtime system prompt (as reported)",
    "model_verified": False,
    "model_verified_note": "no adapter probe run in this session; recorded as-is",
    "backend": "opencode api_direct (fireworks)",
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
    except Exception as exc:  # recorded, never fatal
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
        import yaml  # noqa: F401  (record serialization only)
        env["pyyaml_version"] = getattr(yaml, "__version__", "unknown")
        env["pyyaml_use"] = "run-record serialization only; never in counted/certified code"
    except ImportError:
        env["pyyaml_version"] = None
    try:
        import cypari2  # noqa: F401
        env["cypari_present"] = True
        env["cypari_use"] = "NOT USED anywhere in this experiment (present in env only)"
    except ImportError:
        env["cypari_present"] = False
    return env


def open_run(run_id, argv, params):
    """Create runs/<run_id>/, return (run_dir, header dict, t0)."""
    run_dir = os.path.join(REPO_ROOT, EXP_DIR, "runs", run_id)
    os.makedirs(run_dir, exist_ok=True)
    header = {
        "run_id": run_id,
        "experiment_id": "EXP-ECRANK-76a70d",
        "task_id": "TASK-20260906-908f6b",
        "started_at": now_iso(),
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
    return run_dir, header, time.monotonic()


def finalize_run(run_dir, header, t0, status, reason, raw_result,
                 extra_resources=None):
    """Write manifest.yaml (JSON-in-yaml via PyYAML or JSON fallback) and
    raw-result.json; returns the manifest dict."""
    header["finished_at"] = now_iso()
    header["wall_seconds"] = round(time.monotonic() - t0, 3)
    header["counted_exact_ops"] = E.ops_count()
    header["peak_rss_bytes"] = E.peak_rss_bytes()
    header["peak_rss_gb"] = round(E.peak_rss_bytes() / 1024 ** 3, 3)
    header["memory_ceiling_respected"] = header["peak_rss_gb"] < 8.0
    header["ops_cap_respected"] = E.ops_count() <= 1.0e8 + 10 ** 6
    header["validity"] = {"status": status, "reason": reason}
    if extra_resources:
        header["resources_extra"] = extra_resources
    raw_path = os.path.join(run_dir, "raw-result.json")
    with open(raw_path, "w") as f:
        json.dump(raw_result, f, indent=1, sort_keys=True)
    man_path = os.path.join(run_dir, "manifest.yaml")
    try:
        import yaml
        with open(man_path, "w") as f:
            yaml.safe_dump(header, f, sort_keys=True, width=100)
    except ImportError:
        with open(os.path.join(run_dir, "manifest.json"), "w") as f:
            json.dump(header, f, indent=1, sort_keys=True)
    return header


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    return path


def inst_json(inst):
    """Canonical JSON-ready form of a build_instance dict (all strings)."""
    return {k: (list(v) if isinstance(v, (list, tuple)) else v)
            for k, v in inst.items()}


def canon_instance_key(inst):
    """Canonical string of the instance data for bit-for-bit determinism
    comparison (IV-7): sorted-key JSON of the full instance dict."""
    return json.dumps(inst_json(inst), sort_keys=True)


def log_log_slope(levels, counts):
    """Least-squares log-log slope of count vs level over cells with
    count > 0. Metric-pipeline reporting layer (float logs are admissible
    here; IV-6 bans floats only inside the exact certificate part)."""
    import math as _m
    pts = [(_m.log10(L), _m.log10(c))
           for L, c in zip(levels, counts) if c > 0]
    if len(pts) < 2:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    n = len(pts)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in pts)
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else None
