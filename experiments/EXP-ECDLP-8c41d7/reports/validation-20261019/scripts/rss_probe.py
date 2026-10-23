#!/usr/bin/env python3
"""Sample VmRSS of a single msolve process every 10 s up to a wall limit, then kill it (informational memory growth; check 4/7)."""
import subprocess, sys, time, json
f, extra, limit = sys.argv[1], sys.argv[2].split() if sys.argv[2] != "-" else [], float(sys.argv[3])
pr = subprocess.Popen(["msolve", "-f", f, "-o", f + ".gb"] + extra + ["-g", "2", "-v", "2", "-t", "1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
t0 = time.monotonic(); samples = []
while time.monotonic() - t0 < limit and pr.poll() is None:
    time.sleep(10)
    try:
        rss = [int(l.split()[1]) for l in open(f"/proc/{pr.pid}/status") if l.startswith("VmRSS")][0] / 1024
    except Exception:
        break
    samples.append((round(time.monotonic() - t0), round(rss)))
rc = pr.poll()
if rc is None: pr.kill(); pr.wait(); rc = "killed-at-limit"
print(json.dumps(dict(file=f.split('/')[-1], rc=rc, wall_s=round(time.monotonic() - t0, 1), rss_mb_by_s=samples)))
