"""Read-log helper for TASK-20260929-accb8e. Every script of this task opens
committed files through `opened(path, note)` so that checks/read-log.txt records
each path in the order it was read."""
import datetime, os, fcntl
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-census-a32e70808"
SHARED = "/home/user/crypto-autoresearcher"
LOG = os.path.join(W, "checks", "read-log.txt")

def _loc(path):
    p = os.path.abspath(path)
    if p.startswith(WT + "/"):
        return "WT", os.path.relpath(p, WT)
    if p.startswith(W + "/"):
        return "OWN", os.path.relpath(p, SHARED)
    if p.startswith(SHARED + "/"):
        return "SHARED", os.path.relpath(p, SHARED)
    return "OWN", p

def _nextseq():
    n = 0
    with open(LOG) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) > 1 and parts[1].isdigit():
                n = max(n, int(parts[1]))
    return n + 1

def log(path, note=""):
    loc, rel = _loc(path)
    t = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        seq = _nextseq()
        f.write(f"{t}\t{seq}\t{loc}\t{rel}\t{note}\n")
        fcntl.flock(f, fcntl.LOCK_UN)

def opened(path, note=""):
    log(path, note)
    return path

if __name__ == "__main__":
    import sys
    # usage: python rl.py <path> [note...]
    log(sys.argv[1], " ".join(sys.argv[2:]))
