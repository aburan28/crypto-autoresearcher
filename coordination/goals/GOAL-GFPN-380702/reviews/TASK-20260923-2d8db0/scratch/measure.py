#!/usr/bin/env python3
"""Run a command, report wall seconds, child CPU seconds and peak child RSS (resource usage record)."""
import resource, subprocess, sys, time, datetime
t0 = time.time(); st = datetime.datetime.now(datetime.timezone.utc).isoformat()
rc = subprocess.call(sys.argv[1:])
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
print(f"MEASURE started={st} wall_seconds={time.time()-t0:.2f} cpu_seconds={ru.ru_utime+ru.ru_stime:.2f} peak_child_rss_mb={ru.ru_maxrss/1024:.1f} exit={rc}", file=sys.stderr)
sys.exit(rc)
