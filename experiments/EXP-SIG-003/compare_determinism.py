# EXP-SIG-003 determinism control (C4): deep-compare two raw.json cell
# payloads modulo timing fields. Writes its own receipt raw.json.
# Usage: python3 compare_determinism.py RUN-A-dir RUN-B-dir OUT-dir
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


def main():
    da, db, dout = (Path(sys.argv[i]) for i in (1, 2, 3))
    ra = json.loads((da / "raw.json").read_text())
    rb = json.loads((db / "raw.json").read_text())
    ca, cb = strip(ra.get("cell")), strip(rb.get("cell"))
    same = json.dumps(ca, sort_keys=True) == json.dumps(cb, sort_keys=True)
    rec = {
        "experiment": "EXP-SIG-003",
        "kind": "determinism_compare",
        "run_a": da.name, "run_b": db.name,
        "comparison": "cell payloads, all fields except timing",
        "identical": bool(same),
        "diff_paths": [] if same else diff_paths(ca, cb)[:50],
        "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    dout.mkdir(parents=True, exist_ok=True)
    (dout / "raw.json").write_text(json.dumps(rec, indent=1) + "\n")
    print("determinism compare %s vs %s: identical=%s" % (da.name, db.name, same))
    if not same:
        for p in rec["diff_paths"]:
            print("  DIFF", p)


if __name__ == "__main__":
    main()
