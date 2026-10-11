#!/usr/bin/env python3
"""J1 (g) views: R15/R16 view-map.json files_sha256 against the archived bytes (fixed relpath), and the calibration pin.
TASK-20261002-0114ff. Standard library plus PyYAML (parsing only)."""
import hashlib, json, os, sys, yaml
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
EXP = "experiments/EXP-PFDR-011cd0"
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()
out = {}
for run in ("RUN-PFDR-011cd0-calibrate", "RUN-PFDR-011cd0-analysis"):
    vm = json.load(open(f"{WT}/{EXP}/runs/{run}/view-map.json"))
    res = {}
    for e in vm["entries"]:
        tgt = os.path.join(WT, e["target"])
        present = set()
        for r, _, fs in os.walk(tgt):
            for f in fs:
                present.add(os.path.relpath(os.path.join(r, f), tgt))
        listed = set(e["files_sha256"])
        bad = sorted(f for f in listed if f not in present or sha(os.path.join(tgt, f)) != e["files_sha256"][f])
        res[e["target"]] = {"listed": len(listed), "present": len(present), "listed_hash_mismatch_or_absent": bad,
                            "present_not_listed": sorted(present - listed)[:20], "present_not_listed_count": len(present - listed)}
    out[run] = res
nd = yaml.safe_load(open(f"{WT}/{EXP}/implementation-notes-236691.yaml"))
out["pin_calibration_json"] = nd.get("pin_calibration_json")
json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True, default=str)
print(json.dumps(out, indent=1, default=str)[:3000])
