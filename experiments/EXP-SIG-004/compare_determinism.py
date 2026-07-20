# EXP-SIG-004 determinism control (C4b): deep-compare one cell's payload
# across two run raw.json files modulo timing fields. Writes its own receipt.
# Usage: python3 compare_determinism.py RUN-A-dir RUN-B-dir n:seed:arm OUT-dir
import json, sys, datetime
from pathlib import Path

TIMING_KEYS = {"sec", "wall_s", "wall_seconds", "elapsed_s_so_far",
               "started_at", "finished_at", "stage_times"}


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in TIMING_KEYS}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


def diff_paths(a, b, prefix=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append(prefix + "/" + str(k) + " (only in B)")
            elif k not in b:
                out.append(prefix + "/" + str(k) + " (only in A)")
            else:
                out.extend(diff_paths(a[k], b[k], prefix + "/" + str(k)))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(prefix + " (list length %d vs %d)" % (len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out.extend(diff_paths(x, y, prefix + "/%d" % i))
    elif a != b:
        out.append(prefix + " (%r vs %r)" % (a, b))
    return out


def find_cell(raw, n, seed, arm):
    for c in raw.get("cells", []):
        if c.get("n") == n and c.get("seed") == seed and c.get("arm") == arm:
            return c
    return None


def main():
    da, db = Path(sys.argv[1]), Path(sys.argv[2])
    n, seed, arm = sys.argv[3].split(":")
    n, seed = int(n), int(seed)
    dout = Path(sys.argv[4])
    ra = json.loads((da / "raw.json").read_text())
    rb = json.loads((db / "raw.json").read_text())
    ca = find_cell(ra, n, seed, arm)
    cb = find_cell(rb, n, seed, arm)
    if ca is None or cb is None:
        rec = {"experiment": "EXP-SIG-004", "kind": "determinism_compare",
               "error": "cell not found", "cell": sys.argv[3],
               "run_a": da.name, "run_b": db.name, "identical": False}
    else:
        sa, sb = strip(ca), strip(cb)
        same = json.dumps(sa, sort_keys=True) == json.dumps(sb, sort_keys=True)
        rec = {
            "experiment": "EXP-SIG-004",
            "kind": "determinism_compare",
            "run_a": da.name, "run_b": db.name, "cell": sys.argv[3],
            "comparison": "cell payload, all fields except timing",
            "identical": bool(same),
            "diff_paths": [] if same else diff_paths(sa, sb)[:50],
        }
    rec["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    dout.mkdir(parents=True, exist_ok=True)
    (dout / "raw.json").write_text(json.dumps(rec, indent=1) + "\n")
    print("determinism compare %s vs %s cell %s: identical=%s"
          % (da.name, db.name, sys.argv[3], rec["identical"]))
    for pth in rec.get("diff_paths", []):
        print("  DIFF", pth)


if __name__ == "__main__":
    main()
