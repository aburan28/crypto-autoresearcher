"""Machine-protection wrapper for TASK-20261002-a8bbd8.

    python3 guard.py <label> -- <command ...>

macOS adaptation of the round's attacks/guard.py (RF-5), with THIS task's
limits: the card's RSS stop is 2.5e9 bytes per process (the archived round used
1.5e9). Runs one command at nice 19 with OMP/OPENBLAS/MKL_NUM_THREADS=1 and
PYTHONDONTWRITEBYTECODE=1, polls the child's RSS every 0.5 s via `ps` (macOS
has no /proc; the child is a single process by construction -- the generator
and analysis fork nothing), and kills it if RSS crosses 2.5e9 bytes. Appends
one JSON line to out/commands.log: label, argv, start/end UTC, wall seconds,
exit status, peak RSS bytes, and whether the RSS stop fired. A stop is
"blocked", never a finding.
"""
import datetime
import json
import os
import signal
import subprocess
import sys
import time

LIMIT = 2_500_000_000
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "..", "out", "commands.log")


def rss_bytes(pid):
    """VmRSS analogue on macOS: `ps -o rss= -p PID` reports KB."""
    try:
        out = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)],
                             capture_output=True, text=True, timeout=10)
        return int(out.stdout.strip().split()[0]) * 1024
    except Exception:
        return 0


def main():
    if "--" not in sys.argv:
        print(__doc__)
        return 2
    i = sys.argv.index("--")
    label = sys.argv[1] if i > 1 else "unlabelled"
    cmd = sys.argv[i + 1:]
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    t0 = time.time()
    start = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    proc = subprocess.Popen(cmd, env=env, preexec_fn=lambda: os.nice(19),
                            start_new_session=True)
    peak, stopped = 0, False
    while proc.poll() is None:
        r = rss_bytes(proc.pid)
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
           "wall_s": round(time.time() - t0, 1), "exit": rc,
           "peak_rss_bytes": peak, "rss_stop_fired": stopped,
           "rss_limit_bytes": LIMIT}
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), file=sys.stderr)
    return 99 if stopped else rc


if __name__ == "__main__":
    sys.exit(main())
