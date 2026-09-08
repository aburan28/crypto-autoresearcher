#!/usr/bin/env python3
"""J2.4 (ordering) + J3.6 (dirty-tree / source binding). Extract timing from
all 8 manifests, verify audit-before-construction ordering, and verify the
per-run manifest source_sha256 against the worktree source."""
import os, hashlib, yaml

ROOT = "/Volumes/SSD990/crypto-autoresearcher/.worktrees/ecrank-73275e-review-20260908"
RUNS = ["R1-audit-smoke","R2-draw-support","R3-construct-n6","R4-construct-n6-replay",
        "R5-construct-n8","R6-null","R7-known-false","R8-planted"]

def sha256_file(p):
    h = hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda: f.read(1<<20), b""): h.update(c)
    return h.hexdigest()

print("=== J2.4 run ordering (started_at / finished_at) ===")
times = {}
for r in RUNS:
    m = yaml.safe_load(open(os.path.join(ROOT,"experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-%s/manifest.yaml"%r)))["run"]
    t = m["timing"]
    times[r] = (t["started_at"], t["finished_at"])
    print("  %-22s start=%s end=%s" % (r, t["started_at"], t["finished_at"]))

# ordering: R1.start < R2.start < R3.start (audit before construction)
order_ok = (times["R1-audit-smoke"][0] < times["R2-draw-support"][0]
            < times["R3-construct-n6"][0])
print("R1.start < R2.start < R3.start:", order_ok)
# R2 (audit) finished before R3 (construction) started?
r2_end = times["R2-draw-support"][1]; r3_start = times["R3-construct-n6"][0]
print("R2.finished < R3.started:", r2_end < r3_start, "(%s < %s)" % (r2_end, r3_start))
# R1 finished before R3 started
print("R1.finished < R3.started:", times["R1-audit-smoke"][1] < r3_start)

print("\n=== J3.6 per-run manifest source_sha256 vs worktree source ===")
src_dir = os.path.join(ROOT,"experiments/EXP-ECRANK-73275e/source")
all_ok = True
seen = {}
for r in RUNS:
    m = yaml.safe_load(open(os.path.join(ROOT,"experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-%s/manifest.yaml"%r)))["run"]
    ss = m["code"]["source_sha256"]
    commit = m["code"]["commit"]; dirty = m["code"]["dirty"]
    for fn, exp in ss.items():
        got = sha256_file(os.path.join(src_dir, fn))
        ok = (got == exp)
        all_ok = all_ok and ok
        seen.setdefault(fn, set()).add(exp)
        if not ok:
            print("  MISMATCH %s %s: manifest=%s worktree=%s" % (r, fn, exp, got))
print("all per-run source_sha256 match worktree:", all_ok)
# are the source hashes consistent across runs (same source for all runs)?
consistent = all(len(v)==1 for v in seen.values())
print("source hashes identical across all 8 runs:", consistent)
for fn in sorted(seen):
    print("  %s: %d distinct hash(es)" % (fn, len(seen[fn])))
# commit + dirty across runs
commits = set()
dirties = set()
for r in RUNS:
    m = yaml.safe_load(open(os.path.join(ROOT,"experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-%s/manifest.yaml"%r)))["run"]
    commits.add(m["code"]["commit"]); dirties.add(m["code"]["dirty"])
print("commits across runs:", commits)
print("dirty flags across runs:", dirties)
# dirty_files for R2
m2 = yaml.safe_load(open(os.path.join(ROOT,"experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R2-draw-support/manifest.yaml")))["run"]
print("R2 dirty_files:", m2["code"]["dirty_files"])
