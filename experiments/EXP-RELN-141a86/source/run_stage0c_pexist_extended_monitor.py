"""
External monitor + driver for RUN-RELN-141a86-stage0c-pexist-extended
(TASK-20260907-8e0165 / DEC-20260907-bc69ee).

Extends the ONE remaining Stage-0c control -- INV-7 p_exist, canonical
complexity 11, pack enum_xclass_signed_m2 -- through level 9 (and, if reached
with time remaining, level 10) via the same targeted-minimality method
already validated in RUN-RELN-141a86-stage0c-minimality (levels 1-8 completed
there with no match; killed by that run's own 6000s external cap while
building level 9).

RESUME DECISION (see target_enumerate_worker_checkpoint.py's
--resume-from-checkpoint docstring for the full reasoning): the prior run's
checkpoint-INV-7_p_exist.json stores only per-level summary counts, not the
by_complexity expr-tree dict or seen_string_hashes/seen_fp_hashes dedup sets
those counts were computed from. Those cannot be reconstructed from the
summary counts alone, so a genuine resume (skip straight to building level 9
from a restored level-8 state) is not feasible without adding serialization
of millions of canonical expression trees and two large hash sets to the
checkpoint writer -- a nontrivial change to re-derive levels that themselves
only cost ~1800 seconds (level 1-8, per the prior run's own checkpoint) out
of an estimated 12-14+ HOUR cost for level 9 alone. Given that ratio, this
run RESTARTS the enumeration at level 1 (identical algorithm, identical
checkpointing), continues past level 8 into level 9 (and 10 if reached), and
cross-checks its own levels 1-8 cumulative counts against the prior run's
checkpoint via --resume-from-checkpoint (a verification, not a state
transplant). This is the disclosed deviation from a literal "resume".

External hard caps for this extended attempt (this host measured via `free
-h` at launch time: 15 GiB total RAM, ~14 GiB available, 4 cores -- NOT the
specification's budget sizing_note assumption of >=32 GB / 8 cores; disclosed
here and in execution-report.md):
  - wall clock: 72000s (20h), per the handoff's contract_budget_envelope
    exception.
  - memory: worker-internal soft cap 10.0 GB (checked only between fully
    completed levels, same mechanism as the prior run), external monitor
    hard cap 12.5 GB (leaves >1.5 GB headroom below the ~14 GB actually
    available on this host before the OS OOM-killer would act
    uncontrolled). This is LOWER than the handoff's advisory 16 GB because
    16 GB exceeds this host's physical RAM; using the full nominal 16 GB
    would risk an uncontrolled OOM-kill instead of a clean, checkpoint-
    preserving monitor kill.

Based on the prior run's own measured level 7->8 growth (~7.5x in both
cumulative_registered and rss_bytes), level 9 could plausibly approach or
exceed this reduced memory cap before it finishes building; if so the
monitor kills the worker cleanly (SIGTERM then SIGKILL) with whatever
level-8-complete state remains on disk (level 9 is NOT checkpointed until it
fully completes -- per-level granularity is unchanged from the prior run),
and this is resource_exhaustion, never a result.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time

RUN_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "runs", "RUN-RELN-141a86-stage0c-pexist-extended"))
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
PRIOR_CHECKPOINT = os.path.abspath(os.path.join(
    SOURCE_DIR, "..", "runs", "RUN-RELN-141a86-stage0c-minimality",
    "checkpoint-INV-7_p_exist.json"))

POLL_INTERVAL_S = 5.0
WORKER_SOFT_CAP_GB = 10.0
MONITOR_HARD_KILL_GB = 12.5
WORKER_WALL_CLOCK_SOFT_CAP_S = 71400.0
MONITOR_HARD_WALL_CLOCK_S = 72000.0

TARGET_ID = "INV-7_p_exist"
PACK = "enum_xclass_signed_m2"
CANONICAL_COMPLEXITY = 11
MINIMALITY_MAX_COMPLEXITY = 10  # canonical_complexity - 1; covers levels 9 AND 10 in one pass
TARGET_EXPR = "sub(CONST[1],div(binomial(sub(n,B),B),binomial(n,B)))"


def _proc_rss_bytes(pid: int):
    try:
        with open(f"/proc/{pid}/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


def main():
    out_json = os.path.join(RUN_DIR, f"worker-result-{TARGET_ID}.json")
    ckpt_json = os.path.join(RUN_DIR, f"checkpoint-{TARGET_ID}.json")
    mem_log = os.path.join(RUN_DIR, f"memory-timeseries-{TARGET_ID}.json")

    cmd = [
        sys.executable, os.path.join(SOURCE_DIR, "target_enumerate_worker_checkpoint.py"),
        "--pack", PACK,
        "--max-complexity", str(MINIMALITY_MAX_COMPLEXITY),
        "--target-expr", TARGET_EXPR,
        "--target-id", TARGET_ID,
        "--out", out_json,
        "--checkpoint", ckpt_json,
        "--mem-soft-cap-gb", str(WORKER_SOFT_CAP_GB),
        "--wall-clock-soft-cap-s", str(WORKER_WALL_CLOCK_SOFT_CAP_S),
        "--resume-from-checkpoint", PRIOR_CHECKPOINT,
    ]

    samples = []
    t0 = time.monotonic()
    proc = subprocess.Popen(cmd, cwd=SOURCE_DIR,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(json.dumps({"event": "worker_started", "pid": proc.pid, "cmd": cmd,
                       "t_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}),
          file=sys.stderr, flush=True)

    killed = False
    kill_reason = None
    last_sample_write = 0.0
    while True:
        ret = proc.poll()
        rss = _proc_rss_bytes(proc.pid)
        now = time.monotonic()
        samples.append({
            "t_elapsed_s": round(now - t0, 3),
            "rss_bytes": rss,
            "rss_gb": round(rss / 1e9, 4) if rss is not None else None,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
        # Write the memory timeseries incrementally (not just at the end) so a
        # future check-in can observe live progress without waiting for exit.
        if now - last_sample_write >= 30.0 or ret is not None:
            with open(mem_log, "w") as f:
                json.dump({
                    "target_id": TARGET_ID, "pid": proc.pid,
                    "poll_interval_seconds": POLL_INTERVAL_S,
                    "samples": samples,
                    "n_samples": len(samples),
                    "peak_rss_bytes": max((s["rss_bytes"] for s in samples if s["rss_bytes"]), default=None),
                    "wall_clock_seconds_so_far": round(now - t0, 3),
                    "still_running": ret is None,
                }, f, indent=2)
            last_sample_write = now
        if ret is not None:
            break
        if rss is not None and rss >= MONITOR_HARD_KILL_GB * (1024 ** 3):
            killed = True
            kill_reason = f"external_hard_memory_cap_{MONITOR_HARD_KILL_GB}GB_exceeded"
            proc.send_signal(signal.SIGTERM)
            time.sleep(5.0)
            if proc.poll() is None:
                proc.kill()
            break
        if (now - t0) >= MONITOR_HARD_WALL_CLOCK_S:
            killed = True
            kill_reason = f"external_hard_wall_clock_cap_{MONITOR_HARD_WALL_CLOCK_S}s_exceeded"
            proc.send_signal(signal.SIGTERM)
            time.sleep(5.0)
            if proc.poll() is None:
                proc.kill()
            break
        time.sleep(POLL_INTERVAL_S)

    try:
        stdout, stderr = proc.communicate(timeout=15)
    except Exception:
        stdout, stderr = "", ""
    t1 = time.monotonic()

    with open(mem_log, "w") as f:
        json.dump({
            "target_id": TARGET_ID, "pid": proc.pid,
            "poll_interval_seconds": POLL_INTERVAL_S,
            "samples": samples,
            "n_samples": len(samples),
            "peak_rss_bytes": max((s["rss_bytes"] for s in samples if s["rss_bytes"]), default=None),
            "wall_clock_seconds_measured": round(t1 - t0, 3),
            "killed_by_monitor": killed,
            "kill_reason": kill_reason,
            "returncode": proc.returncode,
            "still_running": False,
        }, f, indent=2)

    worker_result = None
    if os.path.exists(out_json):
        with open(out_json) as f:
            worker_result = json.load(f)

    checkpoint_state = None
    if os.path.exists(ckpt_json):
        with open(ckpt_json) as f:
            checkpoint_state = json.load(f)

    final = {
        "target_id": TARGET_ID,
        "pack": PACK,
        "minimality_max_complexity_requested": MINIMALITY_MAX_COMPLEXITY,
        "canonical_complexity": CANONICAL_COMPLEXITY,
        "target_expr": TARGET_EXPR,
        "monitor_killed": killed,
        "monitor_kill_reason": kill_reason,
        "wall_clock_seconds_measured": round(t1 - t0, 3),
        "peak_rss_gb_measured": max((s["rss_gb"] for s in samples if s["rss_gb"]), default=None),
        "returncode": proc.returncode,
        "worker_stdout": stdout.strip() if stdout else "",
        "worker_stderr_tail": stderr[-4000:] if stderr else "",
        "worker_result": worker_result,
        "checkpoint_state": checkpoint_state,
        "memory_timeseries_path": mem_log,
        "checkpoint_path": ckpt_json,
        "prior_checkpoint_used_for_cross_check_only": PRIOR_CHECKPOINT,
    }
    out_path = os.path.join(RUN_DIR, "pexist-extended-search-raw-result.json")
    with open(out_path, "w") as f:
        json.dump(final, f, indent=2)
    print(json.dumps({"summary": {
        "target_id": TARGET_ID,
        "monitor_killed": killed,
        "kill_reason": kill_reason,
        "returncode": proc.returncode,
        "peak_rss_gb_measured": final["peak_rss_gb_measured"],
        "wall_clock_s": final["wall_clock_seconds_measured"],
    }}), file=sys.stderr, flush=True)
    print(f"wrote {out_path}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
