#!/usr/bin/env python3
"""Run msolve with given args; print wall time and child peak RSS (resource.getrusage). Usage: timed_msolve.py LOG -- ARGS..."""
import resource, subprocess, sys, time, json
log = sys.argv[1]; args = sys.argv[sys.argv.index("--") + 1:]
t0 = time.monotonic()
with open(log, "w") as fh:
    rc = subprocess.run(["msolve"] + args, stdout=fh, stderr=subprocess.STDOUT).returncode
print(json.dumps(dict(args=args, rc=rc, wall_s=round(time.monotonic() - t0, 3), child_maxrss_mb=round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024, 1))))
