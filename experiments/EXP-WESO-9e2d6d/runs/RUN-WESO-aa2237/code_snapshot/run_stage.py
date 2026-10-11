"""EXP-WESO-9e2d6d -- stage run wrapper.

Usage:
  python3 -B experiments/EXP-WESO-9e2d6d/implementation/run_stage.py \
      --run-id RUN-... --stage A|B|C|D --watchdog SECONDS -- <driver argv...>

Creates runs/<RUN-ID>/ (refuses if it exists: run records are immutable),
writes command.txt and environment.json BEFORE the driver starts, runs the
driver with stdout/stderr captured to stdout.log/stderr.log under the stage
watchdog, samples resident memory of the whole process tree every 2 s, and
writes manifest.yaml (top-level key `run`) after the driver exits.  The
driver writes raw-result.json, execution_report.yaml, status.json and
manifest_extra.json into the run directory.
"""
import argparse
import datetime
import json
import os
import platform
import resource
import shlex
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import yaml  # noqa: E402

TOTAL_MEM_CAP = 8 * 1024 ** 3


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_state():
    def g(*a):
        return subprocess.run(["git", "-C", common.REPO] + list(a), capture_output=True, text=True).stdout
    return {
        "commit": g("rev-parse", "HEAD").strip(),
        "branch": g("rev-parse", "--abbrev-ref", "HEAD").strip(),
        "dirty_paths": [l for l in g("status", "--porcelain").splitlines() if l.strip()],
    }


def tree_rss(pid):
    """Total RSS (bytes) of pid and all descendants, from /proc."""
    kids = {}
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open("/proc/%s/stat" % d) as f:
                parts = f.read().rsplit(")", 1)[1].split()
            kids.setdefault(int(parts[1]), []).append(int(d))
        except Exception:
            pass
    total, stack = 0, [pid]
    while stack:
        q = stack.pop()
        try:
            with open("/proc/%d/status" % q) as f:
                for l in f:
                    if l.startswith("VmRSS:"):
                        total += int(l.split()[1]) * 1024
        except Exception:
            pass
        stack.extend(kids.get(q, []))
    return total


def environment():
    import numpy, sympy, mpmath
    env = {
        "gp_version_short": common.gp_version(),
        "gp_path": common.GP_BIN,
        "gp_realpath": os.path.realpath(common.GP_BIN),
        "gp_sha256": common.sha256_file(os.path.realpath(common.GP_BIN)),
        "gp_parisizemax": common.PARISIZEMAX,
        "python": sys.version,
        "python_executable": sys.executable,
        "numpy": numpy.__version__,
        "sympy": sympy.__version__,
        "mpmath": mpmath.__version__,
        "pyyaml": yaml.__version__,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "mem_total_kb": int(open("/proc/meminfo").readline().split()[1]),
        "loadavg_at_start": open("/proc/loadavg").read().strip(),
        "https_proxy_set": bool(os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")),
    }
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--watchdog", type=int, required=True)
    ap.add_argument("driver", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    drv = a.driver[1:] if a.driver and a.driver[0] == "--" else a.driver
    rundir = os.path.join(common.EXP_DIR, "runs", a.run_id)
    if os.path.exists(rundir):
        sys.exit("refusing: %s exists (run records are immutable)" % rundir)
    os.makedirs(rundir)

    env = environment()
    if not env["gp_version_short"].startswith("2.15."):
        # SR-7: infrastructure stop
        common.write_json(os.path.join(rundir, "environment.json"), env)
        sys.exit("SR-7: gp version %r is not 2.15.x" % env["gp_version_short"])

    wrapper_argv = [sys.executable, "-B"] + [os.path.relpath(os.path.abspath(sys.argv[0]), common.REPO)] + sys.argv[1:]
    driver_argv = [sys.executable, "-B"] + drv + ["--run-dir", rundir]
    with open(os.path.join(rundir, "command.txt"), "w") as f:
        f.write("# cwd: %s\n" % common.REPO)
        f.write("# wrapper (exact argv):\n%s\n" % " ".join(shlex.quote(x) for x in wrapper_argv))
        f.write("# driver launched by the wrapper (exact argv):\n%s\n" % " ".join(shlex.quote(x) for x in driver_argv))
        f.write("# environment: PYTHONDONTWRITEBYTECODE=1; gp -q -f -D parisizemax=%s -D parisize=64M per worker\n" % common.PARISIZEMAX)
    git0 = git_state()
    impl0 = common.impl_hashes()
    common.write_json(os.path.join(rundir, "environment.json"), env)

    t0, c0 = time.time(), utc()
    ru0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    envv = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    with open(os.path.join(rundir, "stdout.log"), "w") as fo, open(os.path.join(rundir, "stderr.log"), "w") as fe:
        proc = subprocess.Popen(driver_argv, stdout=fo, stderr=fe, cwd=common.REPO, env=envv)
        peak = {"rss": 0, "over_cap": False}
        stop = threading.Event()

        def mon():
            while not stop.is_set():
                r = tree_rss(proc.pid)
                if r > peak["rss"]:
                    peak["rss"] = r
                if r > TOTAL_MEM_CAP and not peak["over_cap"]:
                    peak["over_cap"] = True
                    proc.kill()
                stop.wait(2.0)
        th = threading.Thread(target=mon, daemon=True)
        th.start()
        timed_out = False
        try:
            rc = proc.wait(timeout=a.watchdog)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            rc = proc.wait()
        stop.set()
        th.join()
    t1, c1 = time.time(), utc()
    ru1 = resource.getrusage(resource.RUSAGE_CHILDREN)

    st_path = os.path.join(rundir, "status.json")
    status = json.load(open(st_path)) if os.path.exists(st_path) else None
    extra_path = os.path.join(rundir, "manifest_extra.json")
    extra = json.load(open(extra_path)) if os.path.exists(extra_path) else {}
    if timed_out:
        status = {"status": "failed", "validity": "invalid",
                  "reason": "infrastructure: stage watchdog %d s expired (SR-9 checkpoint); completed samples preserved, not analysed" % a.watchdog,
                  "failure_class": "resource_exhaustion"}
    elif peak["over_cap"]:
        status = {"status": "failed", "validity": "invalid",
                  "reason": "machine protection: process-tree RSS exceeded 8 GB; killed", "failure_class": "resource_exhaustion"}
    elif status is None:
        status = {"status": "failed", "validity": "invalid",
                  "reason": "driver exited rc=%d without status.json (see stderr.log)" % rc,
                  "failure_class": "implementation_error"}

    git1 = git_state()
    impl1 = common.impl_hashes()
    manifest = {"run": {
        "id": a.run_id,
        "experiment_id": "EXP-WESO-9e2d6d",
        "stage": "STAGE-" + a.stage,
        "task_id": "TASK-20260926-41c7e7",
        "archived_by": "TASK-20260926-b8e6be",
        "approval_decision": "DEC-20260926-ec2847",
        "specification": {"path": "experiments/EXP-WESO-9e2d6d/specification.yaml", "version": 1,
                          "sha256": common.sha256_file(os.path.join(common.EXP_DIR, "specification.yaml"))},
        "status": status["status"],
        "validity": status.get("validity"),
        "validity_reason": status.get("reason"),
        "failure_class": status.get("failure_class"),
        "stage_outcome": status.get("stage_outcome"),
        "claim_tier": {"A": "toy", "B": "toy", "C": "medium", "D": "crypto"}[a.stage],
        "certificate": {"kind": "none",
                        "note": "Pure measurement run: no discrete-log solve and no factor-base relation is claimed. "
                                "Every factorisation of delta and of null integers is verified (product equals the integer, "
                                "each factor passes PARI isprime) and recorded per sample."},
        "code": {
            "commit_at_start": git0["commit"], "branch": git0["branch"],
            "dirty_at_start": bool(git0["dirty_paths"]), "dirty_paths_at_start": git0["dirty_paths"],
            "commit_at_end": git1["commit"], "dirty_at_end": bool(git1["dirty_paths"]),
            "dirty_paths_at_end": git1["dirty_paths"],
            "implementation_sha256_at_start": impl0,
            "implementation_sha256_at_end": impl1,
            "implementation_unchanged_during_run": impl0 == impl1,
        },
        "command": {"wrapper_argv": wrapper_argv, "driver_argv": driver_argv, "cwd": common.REPO,
                    "file": "command.txt"},
        "environment": {"file": "environment.json", "gp_version_short": env["gp_version_short"],
                        "gp_sha256": env["gp_sha256"], "gp_path": env["gp_path"],
                        "python": sys.version.split()[0], "numpy": env["numpy"], "sympy": env["sympy"],
                        "mpmath": env["mpmath"], "parisizemax": common.PARISIZEMAX},
        "timing": {"started_utc": c0, "ended_utc": c1, "wall_seconds": round(t1 - t0, 3),
                   "cpu_seconds_children_user": round(ru1.ru_utime - ru0.ru_utime, 3),
                   "cpu_seconds_children_sys": round(ru1.ru_stime - ru0.ru_stime, 3),
                   "watchdog_seconds": a.watchdog, "watchdog_expired": timed_out},
        "resources": {"peak_rss_process_tree_bytes_sampled_2s": peak["rss"],
                      "peak_rss_single_child_maxrss_kb": ru1.ru_maxrss,
                      "memory_cap_total_bytes": TOTAL_MEM_CAP, "memory_cap_triggered": peak["over_cap"],
                      "gp_parisizemax_per_process": common.PARISIZEMAX},
        "driver_exit_code": rc,
        "inference": {"requested_policy": "executor-implementation",
                      "resolved_model_id": "claude-opus-5-5",
                      "resolved_model_source": "executor subagent session system context (model ID stated to the session); AUTORESEARCH_POLICY/AUTORESEARCH_BACKEND not set in the environment",
                      "autoresearch_policy_env": os.environ.get("AUTORESEARCH_POLICY"),
                      "autoresearch_backend_env": os.environ.get("AUTORESEARCH_BACKEND"),
                      "reasoning_effort": None, "fallback_used": False,
                      "bedrock_used": False},
    }}
    manifest["run"].update(extra)
    with open(os.path.join(rundir, "manifest.yaml"), "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False, width=110, allow_unicode=False)
    print("run %s finished: %s (%s)" % (a.run_id, status["status"], status.get("reason")))


if __name__ == "__main__":
    main()
