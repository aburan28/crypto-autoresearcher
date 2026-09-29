"""Run wrapper for EXP-ECDLP-869870: creates ONE immutable run directory,
enforces the per-run wall-clock (3600 s) and memory (8 GB) ceilings, captures
stdout/stderr, peak RSS and CPU time, and writes manifest.yaml. Refuses to
touch an existing run directory.

Usage: python3 run.py --run-id RUN-... --script run_generic_exact.py [--note ..] -- <script args>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXP = "EXP-ECDLP-869870"
RUNS = os.environ.get("EXP869870_RUNS_DIR") or os.path.join(REPO, "experiments", EXP, "runs")  # override only for dev tests outside the repo
WALL_LIMIT = 3600
MEM_LIMIT = 8 * 1024 ** 3
TASK = "TASK-20260906-d17254"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()


def git_state():
    commit = git("rev-parse", "HEAD")
    status = git("status", "--porcelain", "--untracked-files=all")
    lines = [l for l in status.splitlines() if l.strip()]
    return commit, bool(lines), lines


def inference_block():
    return {
        "requested_policy": "executor-implementation",
        "canonical_policy": "executor-implementation",
        "runtime": "claude_code",
        "backend": "anthropic",
        "binding_model_id": "claude-sonnet-5",
        "binding_note": "orchestration/model-bindings.yaml anthropic:executor-implementation -> claude-sonnet-5 (effort medium)",
        "resolved_model_id": "claude-fable-5-1",
        "model_provenance": "self-reported by the executing session; not probe-verified",
        "model_verified": False,
        "requested_reasoning_effort": "medium",
        "reasoning_effort": "medium",
        "fallback_used": False,
        "fallback_reason": "policy requirements (reasoning_effort >= medium, tool_use) are met by the session; the session's self-reported model id differs from the binding's model id and is recorded here rather than substituted",
        "degraded_requirements": [],
        "independent_session": False,
        "compute_note": "the numbers in this run come from deterministic code (source/ at the pinned hashes); no model is in the compute loop",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--script", required=True)
    ap.add_argument("--kind", required=True)
    ap.add_argument("--note", default="")
    ap.add_argument("--extra-input", action="append", default=[])
    ap.add_argument("args", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    script_args = [x for x in a.args if x != "--"]
    run_dir = os.path.join(RUNS, a.run_id)
    if os.path.exists(run_dir):
        print(f"REFUSED: run directory exists (immutable): {run_dir}", file=sys.stderr)
        sys.exit(3)
    os.makedirs(run_dir)
    cmd = [sys.executable, os.path.join(HERE, a.script), *script_args, "--out", run_dir]
    cmd_str = " ".join(cmd)
    with open(os.path.join(run_dir, "command.txt"), "w") as fh:
        fh.write(cmd_str + "\n")
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               NUMEXPR_NUM_THREADS="1", PYTHONHASHSEED="0")
    commit, dirty, dirty_files = git_state()
    src_files = sorted(f for f in os.listdir(HERE) if f.endswith(".py"))
    src_hashes = {f: sha256(os.path.join(HERE, f)) for f in src_files}
    environment = {
        "operating_system": platform.platform(), "architecture": platform.machine(),
        "python_version": platform.python_version(), "numpy_version": np.__version__,
        "pyyaml_version": yaml.__version__, "sage_version": None,
        "cpu_count": os.cpu_count(), "threads": "single (OMP/OPENBLAS/MKL=1)",
        "env_limits": {"wall_clock_seconds": WALL_LIMIT, "memory_bytes_rlimit_as": MEM_LIMIT},
    }
    with open(os.path.join(run_dir, "environment.json"), "w") as fh:
        json.dump(environment, fh, indent=1)

    def preexec():
        resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT, MEM_LIMIT))

    started = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    out = open(os.path.join(run_dir, "stdout.log"), "wb")
    err = open(os.path.join(run_dir, "stderr.log"), "wb")
    proc = subprocess.Popen(cmd, stdout=out, stderr=err, env=env, cwd=HERE, preexec_fn=preexec)
    timed_out = False
    while True:
        try:
            pid, status, ru = os.wait4(proc.pid, os.WNOHANG)
        except ChildProcessError:
            pid, status, ru = proc.pid, 0, None
        if pid != 0:
            break
        if time.time() - t0 > WALL_LIMIT:
            proc.kill()
            timed_out = True
            pid, status, ru = os.wait4(proc.pid, 0)
            break
        time.sleep(0.5)
    wall = time.time() - t0
    finished = datetime.now(timezone.utc).isoformat()
    out.close(); err.close()
    exit_code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else -os.WTERMSIG(status)
    peak_rss = ru.ru_maxrss * 1024 if ru else None
    cpu = (ru.ru_utime + ru.ru_stime) if ru else None

    summary_path = os.path.join(run_dir, "summary.json")
    raw_path = os.path.join(run_dir, "raw-result.json")
    status_s, invalid_reason, failure_class = "completed_valid", None, None
    if timed_out:
        status_s, failure_class = "failed_infrastructure", "resource_exhaustion"
        invalid_reason = f"wall clock exceeded {WALL_LIMIT} s; killed (never a result)"
    elif exit_code != 0:
        status_s, failure_class = "failed_infrastructure", "infrastructure_error"
        invalid_reason = f"compute process exited with {exit_code} (see stderr.log); never a result"
    elif not (os.path.exists(summary_path) and os.path.exists(raw_path)):
        status_s, failure_class = "failed_infrastructure", "infrastructure_error"
        invalid_reason = "compute process produced no summary/raw output"
    header = {}
    if status_s == "completed_valid":
        with open(summary_path) as fh:
            header = json.load(fh).get("header", {})
        inv = header.get("invalidity", {})
        if inv.get("completed_invalid"):
            status_s, failure_class = "completed_invalid", "implementation_error"
            invalid_reason = "invalidation rule fired: " + "; ".join(k for k, v in inv.items() if v and k != "completed_invalid")
        if peak_rss and peak_rss > MEM_LIMIT:
            status_s, failure_class = "failed_infrastructure", "resource_exhaustion"
            invalid_reason = "peak RSS above the 8 GB ceiling"
    artifacts = {f: sha256(os.path.join(run_dir, f)) for f in sorted(os.listdir(run_dir))}
    manifest = {"run": {
        "id": a.run_id, "experiment_id": EXP, "task_id": TASK, "kind": a.kind, "status": status_s,
        "failure_class": failure_class, "note": a.note,
        "code": {"commit": commit, "dirty": dirty,
                 "dirty_tree_files_this_experiment": [l for l in dirty_files if f"experiments/{EXP}" in l],
                 "dirty_tree_other_entries_count": len([l for l in dirty_files if f"experiments/{EXP}" not in l]),
                 "dirty_tree_other_entries_sample": [l for l in dirty_files if f"experiments/{EXP}" not in l][:10],
                 "dirty_note": "other entries belong to the concurrent executor of EXP-ECDLP-612fb1 in the same worktree; not written by this task",
                 "command": cmd_str, "source_dir": f"experiments/{EXP}/source",
                 "source_sha256": src_hashes,
                 "source_note": "source files are untracked at run time (committed by the Coordinator's snapshot archive); their sha256 pins the executed code"},
        "inference": inference_block(),
        "environment": environment,
        "inputs": {"curve_id": None, "seed": header.get("seed"), "seeds": header.get("seeds"),
                   "parameters": {k: header.get(k) for k in ("stage", "log2N", "N", "T", "a_grid", "r_grid", "m_factors", "sigmas", "M_online", "bits_per_entry") if k in header},
                   "script_args": script_args, "extra_inputs": a.extra_input,
                   "contract": f"experiments/{EXP}/specification.yaml (version 1, status approved, frozen)"},
        "timing": {"started_at": started, "finished_at": finished, "wall_seconds": wall,
                   "wall_clock_limit_seconds": WALL_LIMIT, "timed_out": timed_out},
        "resources": {"peak_rss_bytes": peak_rss, "cpu_seconds": cpu, "memory_limit_bytes": MEM_LIMIT,
                      "exit_code": exit_code},
        "result": {"valid": status_s == "completed_valid", "invalid_reason": invalid_reason,
                   "certificate": header.get("certificate", {"kind": "none", "verified": None, "verifier": None}),
                   "invalidity_checks": header.get("invalidity"),
                   "metrics_location": "summary.json (per cell); raw-result.json (raw)"},
        "artifacts": artifacts,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }}
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, width=100)
    print(f"{a.run_id}: {status_s} wall={wall:.1f}s rss={peak_rss} cpu={cpu}")
    sys.exit(0 if status_s.startswith("completed") else 1)


if __name__ == "__main__":
    main()
