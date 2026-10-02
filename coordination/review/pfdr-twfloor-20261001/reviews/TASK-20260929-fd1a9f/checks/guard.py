"""Machine-protection wrapper (VF-5) for TASK-20260929-fd1a9f.

guard.py --label L [--rss-stop BYTES] -- cmd args...

Runs cmd under nice 19 with OMP/OPENBLAS/MKL threads = 1 and
PYTHONDONTWRITEBYTECODE=1, polls the VmRSS of the child and all its
descendants every 0.25 s, and kills the process group if the summed RSS
crosses the stop (default 2.0e9 bytes). Appends one JSON record per command
to checks/commands.log: label, argv, cwd, start/end UTC, exit status, wall
seconds, peak summed RSS, killed flag. A kill is BLOCKED, never a finding.
"""
import json, os, signal, subprocess, sys, time, datetime

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commands.log")


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def tree_rss(root):
    # map ppid -> children from /proc
    kids = {}
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open(f"/proc/{d}/stat") as f:
                st = f.read()
            ppid = int(st[st.rfind(")") + 2:].split()[1])
            kids.setdefault(ppid, []).append(int(d))
        except Exception:
            pass
    total, stack = 0, [root]
    while stack:
        pid = stack.pop()
        try:
            with open(f"/proc/{pid}/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        total += int(line.split()[1]) * 1024
                        break
        except Exception:
            pass
        stack.extend(kids.get(pid, []))
    return total


def main():
    argv = sys.argv[1:]
    label, stop = "unlabelled", 2.0e9
    while argv and argv[0] != "--":
        if argv[0] == "--label":
            label = argv[1]; argv = argv[2:]
        elif argv[0] == "--rss-stop":
            stop = float(argv[1]); argv = argv[2:]
        else:
            raise SystemExit("bad option " + argv[0])
    cmd = argv[1:]
    env = dict(os.environ)
    env.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                "PYTHONDONTWRITEBYTECODE": "1"})
    start, t0 = utc(), time.time()
    proc = subprocess.Popen(cmd, env=env, preexec_fn=lambda: (os.setsid(), os.nice(19)))
    peak, killed = 0, False
    while proc.poll() is None:
        r = tree_rss(proc.pid)
        peak = max(peak, r)
        if r > stop:
            killed = True
            os.killpg(proc.pid, signal.SIGKILL)
            break
        time.sleep(0.25)
    rc = proc.wait()
    rec = {"label": label, "argv": cmd, "cwd": os.getcwd(), "start": start, "end": utc(),
           "exit": rc, "wall_seconds": round(time.time() - t0, 3), "peak_tree_rss_bytes": peak,
           "rss_stop_bytes": stop, "killed_by_rss_stop": killed}
    with open(LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print("[guard]", json.dumps(rec), file=sys.stderr)
    sys.exit(rc if not killed else 137)


if __name__ == "__main__":
    main()
