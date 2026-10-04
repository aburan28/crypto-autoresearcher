"""
External monitor + sequential driver for RUN-RELN-141a86-stage0c-repair.

For each of the three failing controls (INV-1 mean, INV-7 p_fail, INV-7
p_exist, INV-8 d_reg -- four targets total since INV-7 carries two), this
launches target_enumerate_worker.py as a REAL, SEPARATE background OS
process (subprocess.Popen), and polls that process's own
/proc/<pid>/status VmRSS every POLL_INTERVAL_S seconds from THIS (parent)
process -- a real, timed, external ps/proc memory-polling loop, independent
of the worker's own internal soft-cap check -- writing every sample to a
per-target memory-timeseries log. If external RSS reaches HARD_KILL_GB
(deliberately set below the worker's own internal soft cap, as a backstop
that should in practice never fire) the process is SIGTERM'd and, after a
grace period, SIGKILL'd; this is recorded as resource_exhaustion for that
target, never a result.

Targets are run ONE AT A TIME (never concurrently), specifically so each
gets the full host memory budget rather than splitting it -- the prior
run (RUN-RELN-141a86-stage0bcde) ran multiple such jobs CONCURRENTLY and
attributed part of its early, conservative termination decision to that
concurrency; this is recorded as a protocol/engineering deviation from the
prior attempt in implementation.md.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time

RUN_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../runs/RUN-RELN-141a86-stage0c-repair"
RUN_DIR = os.path.abspath(RUN_DIR)
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

POLL_INTERVAL_S = 2.0
# Internal soft cap given to the worker (it stops itself cleanly here).
WORKER_SOFT_CAP_GB = 11.0
# External hard-kill backstop (above the worker's own soft cap but safely
# below the host's measured 15 GB total, leaving margin for the monitor
# process itself and the OS/page cache).
MONITOR_HARD_KILL_GB = 13.0
WORKER_WALL_CLOCK_SOFT_CAP_S = 5400.0
MONITOR_HARD_WALL_CLOCK_S = 6000.0


def _proc_rss_bytes(pid: int):
    try:
        with open(f"/proc/{pid}/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


def run_one_target(target_id, pack, max_complexity, target_expr, extra_leaves=None):
    out_json = os.path.join(RUN_DIR, f"worker-result-{target_id}.json")
    mem_log = os.path.join(RUN_DIR, f"memory-timeseries-{target_id}.json")
    cmd = [
        sys.executable, os.path.join(SOURCE_DIR, "target_enumerate_worker.py"),
        "--pack", pack,
        "--max-complexity", str(max_complexity),
        "--target-expr", target_expr,
        "--target-id", target_id,
        "--out", out_json,
        "--mem-soft-cap-gb", str(WORKER_SOFT_CAP_GB),
        "--wall-clock-soft-cap-s", str(WORKER_WALL_CLOCK_SOFT_CAP_S),
    ]
    if extra_leaves:
        cmd += ["--extra-leaves-json", json.dumps(extra_leaves)]

    samples = []
    t0 = time.monotonic()
    proc = subprocess.Popen(cmd, cwd=SOURCE_DIR,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    killed = False
    kill_reason = None
    while True:
        ret = proc.poll()
        rss = _proc_rss_bytes(proc.pid)
        now = time.monotonic()
        samples.append({
            "t_elapsed_s": round(now - t0, 3),
            "rss_bytes": rss,
            "rss_gb": round(rss / 1e9, 4) if rss is not None else None,
        })
        if ret is not None:
            break
        if rss is not None and rss >= MONITOR_HARD_KILL_GB * (1024 ** 3):
            killed = True
            kill_reason = f"external_hard_cap_{MONITOR_HARD_KILL_GB}GB_exceeded"
            proc.send_signal(signal.SIGTERM)
            time.sleep(3.0)
            if proc.poll() is None:
                proc.kill()
            break
        if (now - t0) >= MONITOR_HARD_WALL_CLOCK_S:
            killed = True
            kill_reason = f"external_hard_wall_clock_cap_{MONITOR_HARD_WALL_CLOCK_S}s_exceeded"
            proc.send_signal(signal.SIGTERM)
            time.sleep(3.0)
            if proc.poll() is None:
                proc.kill()
            break
        time.sleep(POLL_INTERVAL_S)

    try:
        stdout, stderr = proc.communicate(timeout=10)
    except Exception:
        stdout, stderr = "", ""
    t1 = time.monotonic()

    with open(mem_log, "w") as f:
        json.dump({
            "target_id": target_id, "pid": proc.pid,
            "poll_interval_seconds": POLL_INTERVAL_S,
            "samples": samples,
            "n_samples": len(samples),
            "peak_rss_bytes": max((s["rss_bytes"] for s in samples if s["rss_bytes"]), default=None),
            "wall_clock_seconds_measured": round(t1 - t0, 3),
            "killed_by_monitor": killed,
            "kill_reason": kill_reason,
            "returncode": proc.returncode,
        }, f, indent=2)

    worker_result = None
    if os.path.exists(out_json) and not killed:
        with open(out_json) as f:
            worker_result = json.load(f)
    elif os.path.exists(out_json) and killed:
        # worker wrote a result but the monitor also decided to kill it
        # (race at the boundary of its own soft cap and the external hard
        # cap) -- prefer the worker's own clean result if it exists.
        with open(out_json) as f:
            worker_result = json.load(f)

    return {
        "target_id": target_id,
        "pack": pack,
        "max_complexity_requested": max_complexity,
        "target_expr": target_expr,
        "monitor_killed": killed,
        "monitor_kill_reason": kill_reason,
        "wall_clock_seconds_measured": round(t1 - t0, 3),
        "peak_rss_gb_measured": max((s["rss_gb"] for s in samples if s["rss_gb"]), default=None),
        "returncode": proc.returncode,
        "worker_stdout": stdout.strip(),
        "worker_stderr_tail": stderr[-4000:] if stderr else "",
        "worker_result": worker_result,
        "memory_timeseries_path": mem_log,
    }


TARGETS = [
    {
        "target_id": "INV-1_mean",
        "pack": "fb3_unsigned_m3_and_enum_unsigned_m3",
        "max_complexity": 9,
        "target_expr": "div(binomial(sub(add(B,m),CONST[1]),m),N)",
    },
    {
        "target_id": "INV-7_p_fail",
        "pack": "enum_xclass_signed_m2",
        "max_complexity": 9,
        "target_expr": "div(binomial(sub(n,B),B),binomial(n,B))",
    },
    {
        "target_id": "INV-8_d_reg",
        "pack": "degree_table",
        "max_complexity": 10,
        "target_expr": "ceil(div(add(mul(m,sub(B,CONST[1])),D_S),CONST[2]))",
    },
    {
        "target_id": "INV-7_p_exist",
        "pack": "enum_xclass_signed_m2",
        "max_complexity": 11,
        "target_expr": "sub(CONST[1],div(binomial(sub(n,B),B),binomial(n,B)))",
    },
]


if __name__ == "__main__":
    results = []
    for spec in TARGETS:
        print(f"=== starting target {spec['target_id']} (pack={spec['pack']}, "
              f"max_complexity={spec['max_complexity']}) ===", file=sys.stderr, flush=True)
        r = run_one_target(spec["target_id"], spec["pack"], spec["max_complexity"], spec["target_expr"])
        results.append(r)
        print(json.dumps({"target_id": spec["target_id"],
                           "monitor_killed": r["monitor_killed"],
                           "returncode": r["returncode"],
                           "peak_rss_gb_measured": r["peak_rss_gb_measured"],
                           "wall_clock_seconds_measured": r["wall_clock_seconds_measured"]}),
              file=sys.stderr, flush=True)
    out_path = os.path.join(RUN_DIR, "stage0c-repair-raw-results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote {out_path}", file=sys.stderr)
