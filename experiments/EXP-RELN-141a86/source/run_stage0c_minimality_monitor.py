"""
External monitor + sequential driver for RUN-RELN-141a86-stage0c-minimality
(TASK-20260907-6333af / DEC-20260907-2a3727).

For each target, launches target_enumerate_worker_checkpoint.py as a real,
separate OS subprocess with max_complexity = target_canonical_complexity - 1
(a MINIMALITY search, never the blind-search-to-target-complexity method
already tried and already failed twice), and polls that process's own
/proc/<pid>/status VmRSS every POLL_INTERVAL_S seconds from this parent
process, writing every sample to a per-target memory-timeseries log. The
worker ALSO writes its own checkpoint file continuously (one atomic
overwrite per completed level; see grammar_engine_checkpoint.py), so even a
hard external kill preserves every level completed up to that point.

Targets run ONE AT A TIME (never concurrently), matching the repair run's
practice.

Order (per handoff): INV-1, INV-7 p_fail, INV-8; INV-7 p_exist attempted
last only if substantial time remains.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time

RUN_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "runs", "RUN-RELN-141a86-stage0c-minimality"))
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

POLL_INTERVAL_S = 2.0
# Internal worker soft cap (unchanged from the repair run's memory reasoning):
WORKER_SOFT_CAP_GB = 11.0
MONITOR_HARD_KILL_GB = 13.0

# Wall-clock caps: per the handoff, 6000s per target is the starting point,
# extendable by executor judgment since memory is known (from the prior two
# attempts) not to be the binding constraint at these LOWER levels (this run
# stops at target_complexity - 1, one full level below what failed twice).
# Kept at 6000s here as the external hard backstop; the internal worker soft
# cap is set slightly below it so the worker has a chance to checkpoint
# cleanly before the external monitor's harder kill.
WORKER_WALL_CLOCK_SOFT_CAP_S = 5700.0
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


def run_one_target(target_id, pack, minimality_max_complexity, target_expr,
                    wall_clock_hard_s=MONITOR_HARD_WALL_CLOCK_S):
    out_json = os.path.join(RUN_DIR, f"worker-result-{target_id}.json")
    ckpt_json = os.path.join(RUN_DIR, f"checkpoint-{target_id}.json")
    mem_log = os.path.join(RUN_DIR, f"memory-timeseries-{target_id}.json")
    cmd = [
        sys.executable, os.path.join(SOURCE_DIR, "target_enumerate_worker_checkpoint.py"),
        "--pack", pack,
        "--max-complexity", str(minimality_max_complexity),
        "--target-expr", target_expr,
        "--target-id", target_id,
        "--out", out_json,
        "--checkpoint", ckpt_json,
        "--mem-soft-cap-gb", str(WORKER_SOFT_CAP_GB),
        "--wall-clock-soft-cap-s", str(WORKER_WALL_CLOCK_SOFT_CAP_S),
    ]

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
        if (now - t0) >= wall_clock_hard_s:
            killed = True
            kill_reason = f"external_hard_wall_clock_cap_{wall_clock_hard_s}s_exceeded"
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
    if os.path.exists(out_json):
        with open(out_json) as f:
            worker_result = json.load(f)

    checkpoint_state = None
    if os.path.exists(ckpt_json):
        with open(ckpt_json) as f:
            checkpoint_state = json.load(f)

    return {
        "target_id": target_id,
        "pack": pack,
        "minimality_max_complexity_requested": minimality_max_complexity,
        "target_expr": target_expr,
        "monitor_killed": killed,
        "monitor_kill_reason": kill_reason,
        "wall_clock_seconds_measured": round(t1 - t0, 3),
        "peak_rss_gb_measured": max((s["rss_gb"] for s in samples if s["rss_gb"]), default=None),
        "returncode": proc.returncode,
        "worker_stdout": stdout.strip(),
        "worker_stderr_tail": stderr[-4000:] if stderr else "",
        "worker_result": worker_result,
        "checkpoint_state": checkpoint_state,
        "memory_timeseries_path": mem_log,
        "checkpoint_path": ckpt_json,
    }


# canonical complexities per specification.yaml node_counting_rule note:
# INV-1 mean -> 9 (minimality max_complexity 8)
# INV-7 p_fail -> 9 (minimality max_complexity 8)
# INV-8 d_reg -> 10 (minimality max_complexity 9)
# INV-7 p_exist -> 11 (minimality max_complexity 10), attempted last
TARGETS = [
    {
        "target_id": "INV-1_mean",
        "pack": "fb3_unsigned_m3_and_enum_unsigned_m3",
        "canonical_complexity": 9,
        "minimality_max_complexity": 8,
        "target_expr": "div(binomial(sub(add(B,m),CONST[1]),m),N)",
    },
    {
        "target_id": "INV-7_p_fail",
        "pack": "enum_xclass_signed_m2",
        "canonical_complexity": 9,
        "minimality_max_complexity": 8,
        "target_expr": "div(binomial(sub(n,B),B),binomial(n,B))",
    },
    {
        "target_id": "INV-8_d_reg",
        "pack": "degree_table",
        "canonical_complexity": 10,
        "minimality_max_complexity": 9,
        "target_expr": "ceil(div(add(mul(m,sub(B,CONST[1])),D_S),CONST[2]))",
    },
    {
        "target_id": "INV-7_p_exist",
        "pack": "enum_xclass_signed_m2",
        "canonical_complexity": 11,
        "minimality_max_complexity": 10,
        "target_expr": "sub(CONST[1],div(binomial(sub(n,B),B),binomial(n,B)))",
    },
]


if __name__ == "__main__":
    attempt_p_exist = "--attempt-p-exist" in sys.argv
    results = []
    order = TARGETS[:3] + (TARGETS[3:] if attempt_p_exist else [])
    for spec in order:
        print(f"=== starting minimality search {spec['target_id']} (pack={spec['pack']}, "
              f"minimality_max_complexity={spec['minimality_max_complexity']}, "
              f"canonical_complexity={spec['canonical_complexity']}) ===",
              file=sys.stderr, flush=True)
        r = run_one_target(spec["target_id"], spec["pack"],
                            spec["minimality_max_complexity"], spec["target_expr"])
        r["canonical_complexity"] = spec["canonical_complexity"]
        results.append(r)
        print(json.dumps({"target_id": spec["target_id"],
                           "monitor_killed": r["monitor_killed"],
                           "returncode": r["returncode"],
                           "peak_rss_gb_measured": r["peak_rss_gb_measured"],
                           "wall_clock_seconds_measured": r["wall_clock_seconds_measured"]}),
              file=sys.stderr, flush=True)
    out_path = os.path.join(RUN_DIR, "minimality-search-raw-results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote {out_path}", file=sys.stderr)
