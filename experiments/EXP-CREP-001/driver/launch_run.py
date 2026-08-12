#!/usr/bin/env python3
"""EXP-CREP-001 run launcher: executes one planned run under supervision and
writes the immutable run record.

Responsibilities:
  - enforce the frozen budgets: wall_clock_seconds_per_run = 1800 (hard cap;
    the child is killed on expiry and the run classified resource_exhaustion),
    total_wall_clock_seconds = 5400 (checked against already-recorded runs
    before launch), maximum_runs = 4, memory 4 GiB (best-effort RLIMIT_AS).
  - capture stdout/stderr to files, measure wall-clock seconds (monotonic),
    CPU seconds and peak RSS bytes (getrusage RUSAGE_CHILDREN; ru_maxrss is
    bytes on Darwin), record exact argv, git commit and dirty-tree state,
    environment and dependency versions, start/end timestamps.
  - write manifest.yaml, command.txt, environment.json and the specification
    alias files (raw-result.json = raw.json, stdout.log = stdout.txt,
    stderr.log = stderr.txt) after the child exits. The child itself writes
    raw.json and summary.json.

Usage:
  python3 experiments/EXP-CREP-001/driver/launch_run.py RUN-CREP-001-A phase-a
"""
import hashlib
import json
import os
import platform
import resource
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

import yaml

EXP_ROOT = "experiments/EXP-CREP-001"
PLANNED = {
    "RUN-CREP-001-A": "phase-a",
    "RUN-CREP-001-B": "phase-b",
    "RUN-CREP-001-C": "phase-c",
    "RUN-CREP-001-D": "phase-d",
}
WALL_CAP_PER_RUN = 1800
TOTAL_WALL_CAP = 5400
MAX_RUNS = 4
MEM_CAP_BYTES = 4 * 1024 ** 3


def utcnow():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def git(args):
    return subprocess.run(["git"] + args, capture_output=True, text=True)


def dependency_versions():
    deps = {}
    try:
        import yaml as _y
        deps["pyyaml"] = _y.__version__
    except ImportError:
        deps["pyyaml"] = "absent"
    try:
        import sympy as _s
        deps["sympy"] = _s.__version__ + " (available; not required by this experiment)"
    except ImportError:
        deps["sympy"] = "absent (not required)"
    try:
        import jsonschema as _j
        deps["jsonschema"] = _j.__version__
    except ImportError:
        deps["jsonschema"] = "absent (not required; verifier validates natively against package_schema.json)"
    return deps


def main():
    if len(sys.argv) != 3:
        print("usage: launch_run.py RUN-ID phase-a|phase-b|phase-c|phase-d", file=sys.stderr)
        sys.exit(2)
    run_id, phase = sys.argv[1], sys.argv[2]
    if run_id not in PLANNED or PLANNED[run_id] != phase:
        print("run id %s / phase %s is not in the frozen planned_runs" % (run_id, phase), file=sys.stderr)
        sys.exit(2)
    run_dir = os.path.join(EXP_ROOT, "runs", run_id)
    if os.path.exists(run_dir):
        print("run directory already exists (immutable): %s" % run_dir, file=sys.stderr)
        sys.exit(3)
    runs_root = os.path.join(EXP_ROOT, "runs")
    existing = [d for d in os.listdir(runs_root)
                if d.startswith("RUN-CREP-001-") and os.path.isdir(os.path.join(runs_root, d))]
    if len(existing) >= MAX_RUNS:
        print("maximum_runs=%d already reached" % MAX_RUNS, file=sys.stderr)
        sys.exit(4)
    spent = 0.0
    for d in existing:
        mpath = os.path.join(runs_root, d, "manifest.yaml")
        if os.path.exists(mpath):
            with open(mpath) as f:
                spent += yaml.safe_load(f)["run"]["timing"]["wall_seconds"]
    if spent + WALL_CAP_PER_RUN > TOTAL_WALL_CAP:
        print("total wall-clock budget would be exceeded (spent %.1f s)" % spent, file=sys.stderr)
        sys.exit(5)

    os.makedirs(run_dir)
    commit = git(["rev-parse", "HEAD"]).stdout.strip()
    status = git(["status", "--porcelain"]).stdout
    dirty = bool(status.strip())
    dirty_paths = [l[3:] for l in status.splitlines() if l.strip()]
    dirty_note = ("dirty tree present: %d paths; paths outside this task's write scope "
                  "(pre-existing ._ AppleDouble artifacts under experiments/EXP-SIG-008/ and other "
                  "tasks' untracked artifacts in the shared worktree) were not created or modified by "
                  "this task; this task's own artifacts under experiments/EXP-CREP-001/ are untracked "
                  "new files awaiting the Coordinator's snapshot archive task"
                  % len(dirty_paths)) if dirty else "clean"

    inner_argv = [sys.executable, os.path.join(EXP_ROOT, "driver", "run_crep.py"), phase,
                  "--run-id", run_id, "--exp-root", EXP_ROOT, "--repo-root", ".", "--out", run_dir]
    command_str = " ".join(inner_argv)
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(command_str + "\n")

    env = {
        "operating_system": platform.system() + " " + platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "dependencies": dependency_versions(),
        "git": {"commit": commit, "dirty": dirty},
        "working_directory": os.getcwd(),
    }
    with open(os.path.join(run_dir, "environment.json"), "w") as f:
        json.dump(env, f, indent=2, sort_keys=True)
        f.write("\n")

    started_at = utcnow()
    t0 = time.monotonic()
    exit_code = None
    timed_out = False

    def limits():
        try:
            resource.setrlimit(resource.RLIMIT_AS, (MEM_CAP_BYTES, MEM_CAP_BYTES))
        except (ValueError, OSError):
            pass

    with open(os.path.join(run_dir, "stdout.txt"), "w") as out_f, \
         open(os.path.join(run_dir, "stderr.txt"), "w") as err_f:
        proc = subprocess.Popen(inner_argv, stdout=out_f, stderr=err_f,
                                preexec_fn=limits if hasattr(resource, "RLIMIT_AS") else None)
        try:
            exit_code = proc.wait(timeout=WALL_CAP_PER_RUN)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            proc.wait()
    wall = time.monotonic() - t0
    finished_at = utcnow()
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_seconds = usage.ru_utime + usage.ru_stime
    peak_rss = usage.ru_maxrss  # bytes on Darwin

    raw_path = os.path.join(run_dir, "raw.json")
    if timed_out:
        status_str = "resource_exhaustion"
        reason = "wall_clock_seconds_per_run=%d hard cap exceeded; child killed" % WALL_CAP_PER_RUN
    elif exit_code != 0:
        status_str = "failed_implementation"
        reason = "run driver exited with code %s (see stderr.txt)" % exit_code
    elif not os.path.exists(raw_path):
        status_str = "failed_implementation"
        reason = "run driver produced no raw.json"
    else:
        with open(raw_path) as f:
            raw = json.load(f)
        rv = raw.get("run_validity", {})
        status_str = rv.get("status", "failed_implementation")
        reason = rv.get("reason", "run_validity missing from raw.json")
        if status_str not in ("completed_valid", "completed_invalid"):
            status_str = "failed_implementation"
            reason = "unexpected run_validity payload: %s" % reason

    for alias, src in [("stdout.log", "stdout.txt"), ("stderr.log", "stderr.txt"), ("raw-result.json", "raw.json")]:
        sp = os.path.join(run_dir, src)
        if os.path.exists(sp):
            shutil.copyfile(sp, os.path.join(run_dir, alias))

    artifacts = {}
    for name in sorted(os.listdir(run_dir)):
        if name.startswith("._"):
            continue
        artifacts[name] = {"sha256": sha256_file(os.path.join(run_dir, name))}

    summary_metrics = None
    summary_path = os.path.join(run_dir, "summary.json")
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            summary_metrics = json.load(f)

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-CREP-001",
            "status": status_str,
            "validity_reason": reason,
            "code": {
                "commit": commit,
                "dirty": dirty,
                "dirty_note": dirty_note,
                "dirty_paths": dirty_paths[:50],
                "command": command_str,
                "launcher_command": " ".join([sys.executable] + sys.argv),
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": None,
                "reasoning_effort": None,
                "fallback_used": False,
                "degraded_allowed": False,
                "adapter_version": None,
                "model_verified": False,
                "note": "executor runtime does not expose the adapter-resolved model identifier; unverified configuration recorded as null (see handoff TASK-20260727-005 inference block)",
            },
            "environment": env,
            "inputs": {
                "seeds": [],
                "seed_policy": "deterministic construction and deterministic audit; no randomness anywhere",
                "parameters": {"phase": phase, "planned_run_id": run_id},
            },
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": round(wall, 3),
            },
            "resources": {
                "cpu_seconds": round(cpu_seconds, 3),
                "peak_rss_bytes": int(peak_rss),
                "measurement": "wall: time.monotonic; cpu: getrusage(RUSAGE_CHILDREN) ru_utime+ru_stime; peak_rss: ru_maxrss (bytes on Darwin); memory cap: best-effort RLIMIT_AS 4 GiB",
            },
            "budget": {
                "wall_clock_seconds_per_run_cap": WALL_CAP_PER_RUN,
                "total_wall_clock_seconds_cap": TOTAL_WALL_CAP,
                "total_wall_clock_seconds_spent_before_this_run": round(spent, 3),
                "maximum_memory_gb": 4,
                "maximum_runs": MAX_RUNS,
            },
            "result": {
                "metrics": summary_metrics,
                "valid": status_str == "completed_valid",
                "invalid_reason": None if status_str == "completed_valid" else reason,
                "certificate": {"kind": "none", "verified": None, "verifier": None},
            },
            "artifacts": artifacts,
        }
    }
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False, default_flow_style=False)
    print("%s: %s (%s) wall=%.2fs cpu=%.2fs peak_rss=%dB" % (run_id, status_str, reason, wall, cpu_seconds, peak_rss))


if __name__ == "__main__":
    main()
