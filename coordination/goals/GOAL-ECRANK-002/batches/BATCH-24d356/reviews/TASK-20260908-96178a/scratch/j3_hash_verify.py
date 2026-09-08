#!/usr/bin/env python3
"""J3.1: hash-verify the snapshot-bound run package against the archive
receipt of TASK-20260907-5058f5. Recompute sha256 of each declared path at
HEAD (worktree) AND at the snapshot commit 03c6e3181b, compare to receipt."""
import hashlib, json, os, subprocess, sys

ROOT = "/Volumes/SSD990/crypto-autoresearcher/.worktrees/ecrank-73275e-review-20260908"
SNAP = "03c6e3181bc54b67ab3904b5f6187dbe4e6cb3ad"
RECEIPT = os.path.join(ROOT, "coordination/goals/GOAL-ECRANK-002/batches/BATCH-a2bf8b/archives/TASK-20260907-5058f5/snapshot-receipt.json")

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def git_show(commit, path):
    return subprocess.run(
        ["git", "-C", ROOT, "show", "%s:%s" % (commit, path)],
        capture_output=True).stdout

with open(RECEIPT) as f:
    rec = json.load(f)
paths = rec["path_sha256"]
print("n_paths declared:", rec.get("n_paths"), "actual dict entries:", len(paths))

mismatch_worktree = []
mismatch_snap = []
missing_worktree = []
missing_snap = []
ok = 0
for path, expected in sorted(paths.items()):
    wt = os.path.join(ROOT, path)
    # worktree (HEAD)
    if os.path.exists(wt):
        wt_h = sha256_file(wt)
    else:
        wt_h = None
        missing_worktree.append(path)
    # snapshot commit
    sb = git_show(SNAP, path)
    if sb is None or (sb == b"" and not os.path.exists(wt)):
        snap_h = None
        missing_snap.append(path)
    else:
        snap_h = sha256_bytes(sb)
    wt_ok = (wt_h == expected)
    snap_ok = (snap_h == expected)
    if wt_ok and snap_ok:
        ok += 1
    else:
        if not wt_ok:
            mismatch_worktree.append((path, expected, wt_h))
        if not snap_ok:
            mismatch_snap.append((path, expected, snap_h))

print("OK (worktree==receipt AND snapshot==receipt):", ok, "/", len(paths))
print("worktree mismatches:", len(mismatch_worktree))
for p, e, g in mismatch_worktree:
    print("  WT-MISMATCH", p, "\n    expected", e, "\n    got     ", g)
print("snapshot-commit mismatches:", len(mismatch_snap))
for p, e, g in mismatch_snap:
    print("  SNAP-MISMATCH", p, "\n    expected", e, "\n    got     ", g)
print("missing in worktree:", missing_worktree)
print("missing in snapshot commit:", missing_snap)

# Also: are the worktree bytes identical to the snapshot-commit bytes for every path?
diff_ws = []
for path in sorted(paths):
    wt = os.path.join(ROOT, path)
    if not os.path.exists(wt):
        continue
    if sha256_file(wt) != sha256_bytes(git_show(SNAP, path)):
        diff_ws.append(path)
print("worktree-vs-snapshot-commit byte differences:", diff_ws)
