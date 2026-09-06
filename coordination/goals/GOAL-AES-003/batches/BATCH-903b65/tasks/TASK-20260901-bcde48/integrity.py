import hashlib
import json
import os
import subprocess

TASKDIR = os.path.dirname(os.path.abspath(__file__))
SNAP = "6ff55eacd"
DIRS = [
    "coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-d7d0ec",
    "coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-f5e58b",
]

out = {"snapshot_commit": SNAP, "checks": []}

anc = subprocess.run(
    ["git", "merge-base", "--is-ancestor", SNAP, "HEAD"], capture_output=True
)
out["snapshot_is_ancestor_of_HEAD"] = anc.returncode == 0

head = subprocess.run(
    ["git", "rev-parse", "HEAD"], capture_output=True, text=True
).stdout.strip()
out["HEAD"] = head

diff = subprocess.run(
    ["git", "diff", "--name-only", SNAP, "HEAD", "--", *DIRS],
    capture_output=True,
    text=True,
).stdout.strip()
out["paths_changed_between_snapshot_and_HEAD"] = diff.splitlines() if diff else []

status = subprocess.run(
    ["git", "status", "--porcelain", "--", *DIRS], capture_output=True, text=True
).stdout.strip()
out["worktree_uncommitted_changes_in_dirs"] = status.splitlines() if status else []

mismatch = 0
total = 0
rows = []
for d in DIRS:
    files = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", SNAP, "--", d],
        capture_output=True,
        text=True,
    ).stdout.split()
    for p in files:
        if p.endswith("/"):
            continue
        blob = subprocess.run(
            ["git", "show", f"{SNAP}:{p}"], capture_output=True
        ).stdout
        h_commit = hashlib.sha256(blob).hexdigest()
        try:
            with open(p, "rb") as f:
                h_work = hashlib.sha256(f.read()).hexdigest()
        except FileNotFoundError:
            h_work = None
        ok = h_commit == h_work
        total += 1
        if not ok:
            mismatch += 1
        rows.append({"path": p, "sha256_at_snapshot": h_commit,
                     "sha256_worktree": h_work, "match": ok})

out["files_checked"] = total
out["mismatches"] = mismatch
out["files"] = rows
out["verdict"] = "PASS" if (mismatch == 0 and out["snapshot_is_ancestor_of_HEAD"]
                            and not out["paths_changed_between_snapshot_and_HEAD"]
                            and not out["worktree_uncommitted_changes_in_dirs"]) else "FAIL"
print(json.dumps(out, indent=1))
with open(os.path.join(TASKDIR, "integrity_result.json"), "w") as f:
    json.dump(out, f, indent=1)
