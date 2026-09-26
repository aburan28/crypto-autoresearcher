"""Run a command, then append wall time and peak RSS (children, KiB) to a
JSONL resource log. Usage: rusage.py <logfile> <label> -- cmd args..."""
import json
import resource
import subprocess
import sys
import time

log, label = sys.argv[1], sys.argv[2]
cmd = sys.argv[sys.argv.index("--") + 1:]
t0 = time.time()
start = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
rc = subprocess.call(cmd)
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
rec = {"label": label, "cmd": cmd, "start_utc": start, "wall_s": round(time.time() - t0, 1), "exit": rc,
       "peak_rss_kib_largest_child": ru.ru_maxrss, "user_cpu_s": round(ru.ru_utime, 1)}
with open(log, "a") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec))
sys.exit(rc)
