"""
run_common.py -- shared helpers for run_impl.py / run_screen.py: git/environment
capture, the frozen factor-base-rule hash, and budget bookkeeping.
"""
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

FACTOR_BASE_RULE_TEXT = (
    "FB(E, fb_size) = the fb_size smallest non-negative integers x in [0,p), in "
    "increasing order starting from x=0, such that x^3+a*x+b is a nonzero quadratic "
    "residue mod p (i.e. a genuine affine point exists at that x-coordinate). "
    "Identical procedure applied to every curve in every class, every outside-class "
    "draw, and every degree-profile null arm."
)


def factor_base_rule_hash(fb_size):
    h = hashlib.sha256((FACTOR_BASE_RULE_TEXT + f"|fb_size={fb_size}").encode()).hexdigest()
    return h


def git_state():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).decode().strip()
    except Exception as e:
        commit = f"UNKNOWN ({e})"
    try:
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=REPO_ROOT).decode()
        dirty = len(status.strip()) > 0
    except Exception:
        dirty = None
    return {"commit": commit, "dirty": dirty}


def environment_snapshot():
    return {
        "operating_system": platform.system(),
        "platform_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "sage_version": None,
        "dependencies": {
            "runtime": "pure Python 3 standard library only (no SageMath, no external "
                       "CAS); sympy NOT used at runtime (see MANIFEST.md 'S4 via "
                       "resultant' -- S4 is evaluated directly via a hand-derived 4x4 "
                       "Sylvester determinant, independently cross-checked against "
                       "brute-force curve arithmetic in driver/selftest_semaev.py, no "
                       "symbolic-algebra dependency needed).",
        },
        "hostname_note": "container/VM identity intentionally not recorded (not relevant "
                          "to reproducibility of a pure-Python numeric computation)",
        "cpu_count": os.cpu_count(),
    }


class Budget:
    def __init__(self, wall_clock_seconds_per_run, total_cpu_hours, maximum_memory_gb, maximum_runs):
        self.wall_clock_seconds_per_run = wall_clock_seconds_per_run
        self.total_cpu_hours = total_cpu_hours
        self.maximum_memory_gb = maximum_memory_gb
        self.maximum_runs = maximum_runs
        self.start = time.time()

    def elapsed(self):
        return time.time() - self.start

    def remaining(self):
        return self.wall_clock_seconds_per_run - self.elapsed()

    def exceeded(self):
        return self.elapsed() > self.wall_clock_seconds_per_run


def _sanitize(obj):
    """Recursively replace non-finite floats (inf/-inf/nan) with JSON-safe string
    sentinels -- json.dump's `default` hook is NEVER called for native floats, so
    this must happen as a pre-pass, not inside a default= callback."""
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, (frozenset, set)):
        return sorted(_sanitize(v) for v in obj)
    if isinstance(obj, float):
        if obj != obj:
            return "nan"
        if obj == float("inf"):
            return "inf"
        if obj == float("-inf"):
            return "-inf"
        return obj
    return obj


def write_json(path, obj):
    clean = _sanitize(obj)
    with open(path, "w") as f:
        json.dump(clean, f, indent=2, default=str)


def build_run_manifest(run_id, experiment_id, command, started_at, finished_at,
                        seeds, parameters, result_dict, artifacts_list,
                        status, invalid_reason=None):
    git = git_state()
    env = environment_snapshot()
    metrics = {
        "decision_branch": result_dict.get("decision_branch"),
        "n_completed_classes": result_dict.get("n_completed_classes"),
        "wall_seconds_total": result_dict.get("wall_seconds_total"),
    }
    certificate = result_dict.get("certificate", {"kind": "none"})
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": experiment_id,
            "status": status,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "command": command,
            },
            "inference": {
                "requested_policy": None,
                "canonical_policy": None,
                "backend": None,
                "provider": None,
                "resolved_model_id": None,
                "model_provenance": "not-applicable",
                "model_verified": False,
                "requested_reasoning_effort": None,
                "reasoning_effort": None,
                "fallback_used": False,
                "fallback_reason": None,
                "degraded_requirements": [],
                "independent_session": False,
                "adapter_version": None,
                "config_digest": None,
                "note": "This run is a deterministic-seed numeric computation "
                        "(elliptic-curve arithmetic / Groebner-basis / discrete-log "
                        "search); no LLM/model is in this run's execution loop.",
            },
            "environment": env,
            "inputs": {
                "seeds": seeds,
                "parameters": parameters,
            },
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": finished_at - started_at if (started_at and finished_at) else None,
            },
            "resources": {
                "peak_rss_bytes": None,
                "cpu_seconds": None,
                "note": "single-threaded pure-Python process; peak RSS not "
                        "instrumented in this run (recorded as null rather than "
                        "fabricated).",
            },
            "result": {
                "metrics": metrics,
                "valid": status == "completed_valid",
                "invalid_reason": invalid_reason,
                "certificate": certificate,
            },
            "artifacts": artifacts_list,
        }
    }
    return manifest


def write_yaml(path, obj):
    with open(path, "w") as f:
        yaml.safe_dump(_sanitize(obj), f, default_flow_style=False, sort_keys=False, width=100)
