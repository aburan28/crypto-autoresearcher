#!/usr/bin/env python3
"""Run a check script in-process under a 3 GB address-space cap (CP-6) and
report wall time and peak RSS on stderr. Usage: capped.py script.py [args...]"""
import resource, runpy, sys, time

CAP = 3 * 1024 ** 3
resource.setrlimit(resource.RLIMIT_AS, (CAP, CAP))
t0 = time.time()
script = sys.argv[1]
sys.argv = sys.argv[1:]
try:
    runpy.run_path(script, run_name="__main__")
finally:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    print("[capped] %s wall_s=%.1f peak_rss_mb=%.1f cap_gb=3" % (script, time.time() - t0, ru.ru_maxrss / 1024.0), file=sys.stderr)
