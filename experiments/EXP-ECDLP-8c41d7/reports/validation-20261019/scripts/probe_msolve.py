#!/usr/bin/env python3
"""Run msolve on a captured .ms file and report rc / wall / max RSS / head of output.

usage: probe_msolve.py <file.ms> <timeout_s> [extra msolve args...]
Pinned by the caller with taskset; runs `msolve -f file -o file.gb <extra> -g 2 -v 2 -t 1`.
Prints one JSON line.  rc is subprocess returncode (negative = killed by signal; -11 = SIGSEGV).
"""
import json, os, resource, subprocess, sys, time

f, to = sys.argv[1], float(sys.argv[2])
extra = sys.argv[3:]
out = f + ".gb"
t0 = time.monotonic()
try:
    r = subprocess.run(["msolve", "-f", f, "-o", out] + extra + ["-g", "2", "-v", "2", "-t", "1"],
                       capture_output=True, text=True, timeout=to)
    rc, log = r.returncode, r.stdout + r.stderr
    st = "ok" if rc == 0 else f"rc{rc}"
except subprocess.TimeoutExpired:
    rc, log, st = None, "", "timeout"
wall = round(time.monotonic() - t0, 3)
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
head = [l for l in log.splitlines() if l.strip()][:6]
print(json.dumps(dict(file=os.path.basename(f), status=st, rc=rc, wall_s=wall, maxrss_mb=round(ru.ru_maxrss / 1024, 1),
                      first_lines=head, gb_written=os.path.exists(out))))
