#!/usr/bin/env python3
"""
Run one engine invocation under a WALL-CLOCK bound and a RESIDENT-SET bound.

Written for TASK-20260915-abf147.  The memory bound is enforced by polling the
summed VmRSS of every process in the child's session (read from /proc) and
killing the whole process group when it exceeds --rss-gb.  It deliberately does
NOT use RLIMIT_AS: the algebra engines on this host reserve far more address
space than they touch, and an address-space cap aborts them while their real
memory use is small -- the very defect BATCH-a33cda repairs.

Records, as JSON next to the captured stdout/stderr:
  exact argv, cwd, UTC start/end, 1-minute load average at start, wall seconds,
  child user+sys CPU seconds (wait4 rusage), ru_maxrss of the direct child,
  polled peak summed RSS of the session, exit status, and the outcome
  (completed | killed_wall_clock | killed_rss | failed_to_start).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def session_rss_bytes(sid: int) -> tuple[int, int]:
    total = 0
    nproc = 0
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/stat", "rb") as fh:
                stat = fh.read().decode(errors="replace")
            # field 6 (1-based) after the closing paren of comm is the session id
            rest = stat[stat.rindex(")") + 2 :].split()
            if int(rest[3]) != sid:
                continue
            with open(f"/proc/{entry}/status") as fh:
                for line in fh:
                    if line.startswith("VmRSS:"):
                        total += int(line.split()[1]) * 1024
                        nproc += 1
                        break
        except (FileNotFoundError, ProcessLookupError, ValueError, IndexError):
            continue
    return total, nproc


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--wall", type=float, required=True, help="wall-clock bound in seconds")
    ap.add_argument("--rss-gb", type=float, required=True, help="resident-set bound in GiB (summed over the session)")
    ap.add_argument("--input-file", default=None, help="engine input whose sha256 is recorded")
    ap.add_argument("--poll", type=float, default=0.25)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    cmd = args.cmd
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        ap.error("no command given")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stdout_path = outdir / f"{args.tag}.stdout.txt"
    stderr_path = outdir / f"{args.tag}.stderr.txt"
    record_path = outdir / f"{args.tag}.run.json"
    if record_path.exists():
        print(f"refusing to overwrite existing run record {record_path}", file=sys.stderr)
        return 2

    loadavg = open("/proc/loadavg").read().split()
    rss_limit = int(args.rss_gb * (1 << 30))
    rec = {
        "tag": args.tag,
        "argv": cmd,
        "cwd": os.getcwd(),
        "input_file": args.input_file,
        "input_sha256": sha256_of(Path(args.input_file)) if args.input_file else None,
        "wall_clock_bound_s": args.wall,
        "rss_bound_bytes": rss_limit,
        "rss_bound_kind": "resident set, summed over the child's session, polled from /proc (NOT RLIMIT_AS)",
        "loadavg_1min_at_start": float(loadavg[0]),
        "loadavg_5min_at_start": float(loadavg[1]),
        "loadavg_15min_at_start": float(loadavg[2]),
        "start_utc": datetime.now(timezone.utc).isoformat(),
        "host": {"nproc": os.cpu_count(), "uname": " ".join(os.uname())},
    }

    t0 = time.monotonic()
    try:
        with open(stdout_path, "wb") as so, open(stderr_path, "wb") as se:
            child = subprocess.Popen(cmd, stdout=so, stderr=se, start_new_session=True)
            sid = child.pid
            peak = 0
            peak_nproc = 0
            outcome = "completed"
            reaped = None
            while True:
                # reap with wait4 ourselves (Popen.poll() would consume the
                # status and lose the rusage)
                wpid, wstatus, ru = os.wait4(child.pid, os.WNOHANG)
                if wpid == child.pid:
                    reaped = (wstatus, ru)
                    break
                rss, nproc = session_rss_bytes(sid)
                if rss > peak:
                    peak, peak_nproc = rss, nproc
                elapsed = time.monotonic() - t0
                if rss > rss_limit:
                    outcome = "killed_rss"
                    os.killpg(sid, signal.SIGKILL)
                    break
                if elapsed > args.wall:
                    outcome = "killed_wall_clock"
                    os.killpg(sid, signal.SIGKILL)
                    break
                time.sleep(args.poll)
            if reaped is None:
                _, wstatus, ru = os.wait4(child.pid, 0)
            else:
                wstatus, ru = reaped
            child.returncode = 0  # already reaped; keep Popen from waiting again
    except FileNotFoundError as exc:
        rec.update({"outcome": "failed_to_start", "error": str(exc)})
        record_path.write_text(json.dumps(rec, indent=2) + "\n")
        print(json.dumps(rec, indent=2))
        return 127

    wall = time.monotonic() - t0
    rec.update(
        {
            "end_utc": datetime.now(timezone.utc).isoformat(),
            "outcome": outcome,
            "wall_seconds": round(wall, 3),
            "exit_code": os.waitstatus_to_exitcode(wstatus) if not os.WIFSIGNALED(wstatus) else None,
            "term_signal": os.WTERMSIG(wstatus) if os.WIFSIGNALED(wstatus) else None,
            "cpu_user_seconds": ru.ru_utime,
            "cpu_sys_seconds": ru.ru_stime,
            "cpu_total_seconds": round(ru.ru_utime + ru.ru_stime, 3),
            "ru_maxrss_bytes_direct_child": ru.ru_maxrss * 1024,
            "polled_peak_session_rss_bytes": peak,
            "polled_peak_session_nproc": peak_nproc,
            "polled_peak_session_rss_gib": round(peak / (1 << 30), 4),
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
            "stdout_sha256": sha256_of(stdout_path),
            "stderr_sha256": sha256_of(stderr_path),
        }
    )
    record_path.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))
    return 0 if outcome == "completed" and rec["exit_code"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
