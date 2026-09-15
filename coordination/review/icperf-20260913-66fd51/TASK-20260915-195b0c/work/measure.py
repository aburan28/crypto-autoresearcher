#!/usr/bin/env python3
"""V2 measurement harness (TASK-20260915-195b0c, validator, joint V2).

Runs one child at a time and records, per row:
  loadavg (1/5/15 min) read immediately before the fork
  wall seconds
  per-child rusage (user+sys CPU, ru_maxrss peak RSS) via os.wait4 -- NOT the
    RUSAGE_CHILDREN high-water bench.py records, so this is a true per-row peak
  VmPeak (peak virtual address space) and VmHWM (peak resident) sampled from
    /proc/<pid>/status, which is what distinguishes an RLIMIT_AS artifact from
    real memory exhaustion
  exit status / signal, timeout flag, and the RLIMIT_AS actually applied

Written for this validation; it does not import bench.py.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

KB = 1024


def _sample_proc(pid: int, out: dict, stop: threading.Event, interval: float,
                 traj: list | None = None, traj_every: float = 2.0,
                 t_start: float = 0.0) -> None:
    """Poll /proc/<pid>/status for the kernel's own high-water marks, and
    optionally record a coarse time series so growth can be seen, not just
    the peak."""
    path = Path(f"/proc/{pid}/status")
    keys = ("VmPeak", "VmHWM", "VmSize", "VmRSS", "Threads")
    next_traj = 0.0
    while not stop.is_set():
        try:
            cur = {}
            for line in path.read_text().splitlines():
                k = line.split(":", 1)[0]
                if k in keys:
                    v = int(line.split()[1])
                    cur[k] = v
                    out[k] = max(out.get(k, 0), v)
        except (FileNotFoundError, ProcessLookupError, ValueError, IndexError):
            return
        if traj is not None:
            el = time.monotonic() - t_start
            if el >= next_traj:
                traj.append({"t_s": round(el, 1), **{k: cur.get(k) for k in keys}})
                next_traj = el + traj_every
        stop.wait(interval)


def run_one(argv, tag, timeout, logdir: Path, rlimit_as_gb=None, env_extra=None,
            sample_interval=0.02, cwd=None, rss_kill_gb=None, trajectory=False) -> dict:
    logdir.mkdir(parents=True, exist_ok=True)
    out_p, err_p = logdir / f"{tag}.out", logdir / f"{tag}.err"

    load = os.getloadavg()
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)

    def limits():
        if rlimit_as_gb is not None:
            lim = int(rlimit_as_gb * (1 << 30))
            resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
        os.setpgrp()

    t0 = time.monotonic()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    peaks: dict = {}
    traj: list | None = [] if trajectory else None
    stop = threading.Event()
    timed_out = False

    with open(out_p, "wb") as fo, open(err_p, "wb") as fe:
        p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL,
                             preexec_fn=limits, env=env, cwd=cwd)
        sampler = threading.Thread(target=_sample_proc,
                                   args=(p.pid, peaks, stop, sample_interval, traj, 2.0, t0),
                                   daemon=True)
        sampler.start()
        deadline = t0 + timeout
        rss_kill_kb = int(rss_kill_gb * (1 << 20)) if rss_kill_gb else None
        pid = rc = ru = None
        rss_killed = False
        while True:
            try:
                pid, status, ru = os.wait4(p.pid, os.WNOHANG)
            except ChildProcessError:
                break
            if pid == p.pid:
                rc = -os.WTERMSIG(status) if os.WIFSIGNALED(status) else os.WEXITSTATUS(status)
                break
            over_rss = rss_kill_kb is not None and peaks.get("VmRSS", 0) > rss_kill_kb
            if time.monotonic() > deadline or over_rss:
                timed_out = not over_rss
                rss_killed = over_rss
                try:
                    os.killpg(p.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                pid, status, ru = os.wait4(p.pid, 0)
                rc = None
                break
            time.sleep(0.002)
        stop.set()
        sampler.join(timeout=1.0)
    wall = time.monotonic() - t0
    p.returncode = rc if rc is not None else -9

    rec = {
        "tag": tag, "argv": [str(a) for a in argv], "started_utc": started,
        "loadavg1_at_start": round(load[0], 2),
        "loadavg5_at_start": round(load[1], 2),
        "loadavg15_at_start": round(load[2], 2),
        "wall_s": round(wall, 4),
        "timeout_s": timeout, "timed_out": timed_out,
        "rss_watchdog_killed": rss_killed, "rss_kill_gb": rss_kill_gb,
        "returncode": rc,
        "rlimit_as_gb": rlimit_as_gb,
        "stdout": str(out_p), "stderr": str(err_p),
    }
    if ru is not None:
        rec["cpu_s"] = round(ru.ru_utime + ru.ru_stime, 4)
        rec["ru_utime_s"] = round(ru.ru_utime, 4)
        rec["ru_stime_s"] = round(ru.ru_stime, 4)
        rec["peak_rss_kb_this_child"] = ru.ru_maxrss
    rec["proc_peaks_kb"] = {k: v for k, v in peaks.items() if k != "Threads"}
    if traj is not None:
        rec["trajectory_kb"] = traj
    if "Threads" in peaks:
        rec["max_threads_observed"] = peaks["Threads"]
    rec["stdout_head"] = out_p.read_text(errors="replace")[:2000]
    rec["stderr_head"] = err_p.read_text(errors="replace")[:2000]
    if rec.get("cpu_s") and rec["wall_s"] > 0:
        rec["cpu_per_wall"] = round(rec["cpu_s"] / rec["wall_s"], 3)
    return rec


def parse_wdsat(stdout_text: str) -> dict:
    """WDSat prints the assignment string (SAT) or 'UNSAT' on line 1 and the
    conflict count on line 2.  Parsed here from the format, not from bench.py."""
    lines = [l.strip() for l in stdout_text.splitlines() if l.strip()]
    res = {"status": "unknown", "assignment": None, "conflicts": None}
    if not lines:
        return res
    if lines[0] == "UNSAT":
        res["status"] = "UNSAT"
    elif set(lines[0]) <= {"0", "1"} and len(lines[0]) > 1:
        res["status"] = "SAT"
        res["assignment"] = lines[0]
    for l in lines[1:]:
        if l.isdigit():
            res["conflicts"] = int(l)
            break
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="path to a JSON list of row specs")
    ap.add_argument("--out", required=True)
    ap.add_argument("--logdir", required=True)
    a = ap.parse_args()
    specs = json.loads(Path(a.json).read_text())
    outp = Path(a.out)
    rows = []
    for s in specs:
        print(f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {s['tag']} "
              f"loadavg={os.getloadavg()[0]:.2f} ...", flush=True)
        rec = run_one(s["argv"], s["tag"], s["timeout"], Path(a.logdir),
                      rlimit_as_gb=s.get("rlimit_as_gb"), env_extra=s.get("env"),
                      cwd=s.get("cwd"), rss_kill_gb=s.get("rss_kill_gb"),
                      trajectory=s.get("trajectory", False))
        if s.get("parse") == "wdsat":
            rec.update(parse_wdsat(rec["stdout_head"]))
        rows.append(rec)
        outp.write_text(json.dumps(rows, indent=1))
        print(f"    -> rc={rec['returncode']} wall={rec['wall_s']}s cpu={rec.get('cpu_s')}s "
              f"VmPeak={rec['proc_peaks_kb'].get('VmPeak')}kB VmHWM={rec['proc_peaks_kb'].get('VmHWM')}kB "
              f"status={rec.get('status')} conflicts={rec.get('conflicts')}", flush=True)
    print(f"wrote {outp}")


if __name__ == "__main__":
    sys.exit(main())
