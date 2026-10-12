"""RV-8 machine-protection launcher for TASK-20260929-accb8e.

python guard.py [--log FILE] -- cmd args...
Runs cmd under nice 19 with OMP/OPENBLAS/MKL threads = 1 and
PYTHONDONTWRITEBYTECODE=1, polls VmRSS of the child and all its descendants
every 0.25 s, and kills the process group if the total crosses 1.0e9 bytes (the
stop is BLOCKED, never a finding). Prints and appends to --log: command, exit
status, wall seconds, peak RSS, and whether the RSS stop fired."""
import os, sys, time, signal, subprocess, json, datetime

LIMIT = 1.0e9


def rss_of(pid):
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return 0
    return 0


def descendants(pid):
    out = []
    try:
        with open(f"/proc/{pid}/task/{pid}/children") as f:
            kids = [int(x) for x in f.read().split()]
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return out
    for k in kids:
        out.append(k)
        out.extend(descendants(k))
    return out


def main():
    args = sys.argv[1:]
    log = None
    if args and args[0] == "--log":
        log = args[1]
        args = args[2:]
    if args and args[0] == "--":
        args = args[1:]
    env = dict(os.environ)
    env.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                "PYTHONDONTWRITEBYTECODE": "1"})
    t0 = time.time()
    start = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    p = subprocess.Popen(args, env=env, preexec_fn=lambda: (os.setpgrp(), os.nice(19)))
    peak, stopped = 0, False
    while p.poll() is None:
        tot = rss_of(p.pid) + sum(rss_of(d) for d in descendants(p.pid))
        peak = max(peak, tot)
        if tot > LIMIT:
            stopped = True
            os.killpg(p.pid, signal.SIGKILL)
            break
        time.sleep(0.25)
    rc = p.wait()
    rec = {"started_at": start, "command": args, "exit_status": rc, "wall_seconds": round(time.time() - t0, 3),
           "peak_rss_bytes_polled": peak, "rss_stop_fired": stopped}
    msg = json.dumps(rec)
    print("GUARD " + msg, file=sys.stderr)
    if log:
        with open(log, "a") as f:
            f.write(msg + "\n")
    sys.exit(rc if not stopped else 137)


if __name__ == "__main__":
    main()
