"""Run a command, measure wall / child CPU / peak RSS; optional RLIMIT_AS (GB) and an
RSS watchdog (GB) that kills the child if its polled VmRSS exceeds the limit.
Writes a JSON line to stdout and the child's stdout/stderr to the given files.

usage: runmeasure.py --out OUT --err ERR [--timeout S] [--rlimit-as-gb G] [--rss-watchdog-gb G] -- argv...
"""
import argparse
import json
import os
import resource
import subprocess
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--err", required=True)
ap.add_argument("--timeout", type=float, default=None)
ap.add_argument("--rlimit-as-gb", type=float, default=None)
ap.add_argument("--rss-watchdog-gb", type=float, default=None)
ap.add_argument("argv", nargs=argparse.REMAINDER)
a = ap.parse_args()
argv = a.argv[1:] if a.argv and a.argv[0] == "--" else a.argv


def preexec():
    if a.rlimit_as_gb:
        lim = int(a.rlimit_as_gb * (1 << 30))
        resource.setrlimit(resource.RLIMIT_AS, (lim, lim))


def rss_kb(pid):
    try:
        with open(f"/proc/{pid}/status") as f:
            for ln in f:
                if ln.startswith("VmRSS:"):
                    return int(ln.split()[1])
    except FileNotFoundError:
        return None
    return None


before = resource.getrusage(resource.RUSAGE_CHILDREN)
t0 = time.monotonic()
with open(a.out, "wb") as fo, open(a.err, "wb") as fe:
    p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL, preexec_fn=preexec)
    peak_polled = 0
    killed_by = None
    while True:
        rc = p.poll()
        if rc is not None:
            break
        r = rss_kb(p.pid)
        if r:
            peak_polled = max(peak_polled, r)
        el = time.monotonic() - t0
        if a.rss_watchdog_gb and r and r > a.rss_watchdog_gb * (1 << 20):
            killed_by = "rss_watchdog"
            p.kill()
        elif a.timeout and el > a.timeout:
            killed_by = "timeout"
            p.kill()
        time.sleep(0.05)
    rc = p.wait()
wall = time.monotonic() - t0
after = resource.getrusage(resource.RUSAGE_CHILDREN)
print(json.dumps(dict(argv=argv, returncode=rc, killed_by=killed_by, wall_s=round(wall, 4),
                      cpu_s=round((after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime), 4),
                      ru_maxrss_kb=after.ru_maxrss, peak_polled_vmrss_kb=peak_polled,
                      rlimit_as_gb=a.rlimit_as_gb, rss_watchdog_gb=a.rss_watchdog_gb, timeout_s=a.timeout,
                      loadavg1_at_start=round(os.getloadavg()[0], 2))))
