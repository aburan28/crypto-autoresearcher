"""Machine-protection wrapper for TASK-20260929-575e80 (RF-5).

    python guard.py <label> -- <command ...>

Runs one command at nice 19 with OMP/OPENBLAS/MKL_NUM_THREADS=1 and
PYTHONDONTWRITEBYTECODE=1, polls VmRSS of the child (and its descendants) every
0.5 s, and kills it if the sum crosses 1.5e9 bytes. Appends one JSON line to
attacks/commands.log: label, argv, start/end UTC, wall seconds, exit status,
peak RSS bytes, and whether the RSS stop fired. A stop is "blocked", never a
finding (RF-6).
"""
import datetime
import json
import os
import signal
import subprocess
import sys
import time

LIMIT = 1_500_000_000
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "commands.log")


def rss_tree(pid):
    """Sum of VmRSS (bytes) over pid and its descendants."""
    total = 0
    todo = [pid]
    seen = set()
    while todo:
        p = todo.pop()
        if p in seen:
            continue
        seen.add(p)
        try:
            with open(f"/proc/{p}/status") as fh:
                for line in fh:
                    if line.startswith("VmRSS:"):
                        total += int(line.split()[1]) * 1024
                        break
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
        try:
            with open(f"/proc/{p}/task/{p}/children") as fh:
                todo.extend(int(c) for c in fh.read().split())
        except (FileNotFoundError, PermissionError):
            pass
    return total


def main():
    if "--" not in sys.argv:
        print(__doc__)
        return 2
    i = sys.argv.index("--")
    label = sys.argv[1] if i > 1 else "unlabelled"
    cmd = sys.argv[i + 1:]
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               PYTHONDONTWRITEBYTECODE="1")
    t0 = time.time()
    start = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    proc = subprocess.Popen(cmd, env=env, preexec_fn=lambda: os.nice(19), start_new_session=True)
    peak, stopped = 0, False
    while proc.poll() is None:
        r = rss_tree(proc.pid)
        peak = max(peak, r)
        if r > LIMIT:
            stopped = True
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                proc.kill()
            break
        time.sleep(0.5)
    rc = proc.wait()
    end = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rec = {"label": label, "argv": cmd, "start_utc": start, "end_utc": end,
           "wall_s": round(time.time() - t0, 1), "exit": rc, "peak_rss_bytes": peak,
           "rss_stop_fired": stopped}
    with open(LOG, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), file=sys.stderr)
    return 99 if stopped else rc


if __name__ == "__main__":
    sys.exit(main())
