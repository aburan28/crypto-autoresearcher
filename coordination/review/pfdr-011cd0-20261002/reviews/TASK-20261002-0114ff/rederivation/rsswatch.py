#!/usr/bin/env python3
"""RV-7 machine protection for TASK-20261002-0114ff (validator).

Runs one command as a child process at nice 19 with single-threaded BLAS
environment, polls the resident set size (VmRSS) of the child and all of its
descendants every 0.5 s, and kills the process group if the sum crosses the
cap (default 3.0e9 bytes). Writes a small JSON record (exit code, peak RSS,
wall seconds, whether the cap fired) to the path given by --record.

A cap stop is reported as BLOCKED, never as a finding.
Standard library only.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time


def rss_of(pid):
    try:
        with open(f"/proc/{pid}/status") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
    except OSError:
        return 0
    return 0


def descendants(pid):
    out = []
    try:
        kids = open(f"/proc/{pid}/task/{pid}/children").read().split()
    except OSError:
        return out
    for k in kids:
        k = int(k)
        out.append(k)
        out.extend(descendants(k))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=3.0e9)
    ap.add_argument("--record", required=True)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    env = dict(os.environ)
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
    t0 = time.time()
    p = subprocess.Popen(["nice", "-n", "19"] + cmd, env=env, start_new_session=True)
    peak, capped = 0, False
    while p.poll() is None:
        tot = rss_of(p.pid) + sum(rss_of(d) for d in descendants(p.pid))
        peak = max(peak, tot)
        if tot > a.cap:
            capped = True
            os.killpg(p.pid, signal.SIGKILL)
            break
        time.sleep(0.5)
    rc = p.wait()
    rec = {"cmd": cmd, "exit_code": rc, "peak_rss_bytes": peak, "cap_bytes": a.cap,
           "cap_fired": capped, "wall_seconds": round(time.time() - t0, 3),
           "started_unix": t0, "status": "BLOCKED (memory cap)" if capped else "ran"}
    with open(a.record, "w") as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({k: rec[k] for k in ("exit_code", "peak_rss_bytes", "cap_fired", "wall_seconds")}),
          file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
