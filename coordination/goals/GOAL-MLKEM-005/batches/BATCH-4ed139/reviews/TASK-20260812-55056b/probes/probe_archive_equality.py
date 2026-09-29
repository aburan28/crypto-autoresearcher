#!/usr/bin/env python3
"""VAL TASK-20260812-55056b probe A: change-set equality on all three archive commits.

Declared set = archive task's own artifact_paths UNION every source task's
artifact_paths, taken from the COMMITTED dispatch_queue.json state at the archive
commit is NOT used -- the queue is a live coordination record, so the declared set
is read from the live queue AND cross-checked against the committed
snapshot-receipt.json inside each commit (path_sha256 + declared_path_count).

Actual change set = `git diff-tree --no-commit-id -r --name-only <commit>`.

Reports, per archive: |declared|, |actual|, extra (actual - declared),
missing (declared - actual), and per-path blob-hash agreement with both the
receipt's path_sha256 and the queue archive block's path_sha256.

Run from the repository root. Read-only; writes nothing.
"""
import hashlib
import json
import subprocess
import sys

REPO = "/home/user/crypto-autoresearcher"
QUEUE = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/dispatch_queue.json")

ARCHIVES = [
    ("TASK-20260812-1ed548", "8d72f2c038a577e216ab9d6d0e5995f65d5ff819", 3),
    ("TASK-20260812-b581a8", "3aac83fd8a7293f1311db710a0d5b9beb9e7982d", 8),
    ("TASK-20260812-b53c2f", "d38514d228b4a9e523e82e0b606f72ae3eeef9ff", 22),
]


def git(*args):
    return subprocess.run(["git", "-C", REPO, *args], check=True,
                          capture_output=True).stdout


def blob_sha256(commit, path):
    return hashlib.sha256(git("cat-file", "blob", f"{commit}:{path}")).hexdigest()


def main():
    q = json.load(open(f"{REPO}/{QUEUE}"))
    tasks = {t["id"]: t for t in q["tasks"]}
    ok = True
    for tid, commit, expect_n in ARCHIVES:
        t = tasks[tid]
        arch = t["archive"]
        declared = set(t.get("artifact_paths", []))
        for src in arch["source_task_ids"]:
            declared |= set(tasks[src].get("artifact_paths", []))
        actual = set(
            git("diff-tree", "--no-commit-id", "-r", "--name-only", commit)
            .decode().split()
        )
        extra = sorted(actual - declared)
        missing = sorted(declared - actual)
        print(f"=== {tid} @ {commit[:9]} ===")
        print(f"  declared_count = {len(declared)}   (queue expects {expect_n})")
        print(f"  actual_count   = {len(actual)}")
        print(f"  extra   ({len(extra)}): {extra}")
        print(f"  missing ({len(missing)}): {missing}")
        equal = not extra and not missing and len(declared) == expect_n
        # parent check
        parent = git("rev-parse", f"{commit}^").decode().strip()
        print(f"  parent_actual  = {parent}")
        print(f"  parent_receipt = {arch['parent_sha']}   "
              f"{'MATCH' if parent == arch['parent_sha'] else 'MISMATCH'}")
        # hash agreement: queue archive block covers ALL declared paths incl. receipt
        mism = []
        for p, h in sorted(arch["path_sha256"].items()):
            got = blob_sha256(commit, p)
            if got != h:
                mism.append((p, h, got))
        print(f"  queue-block hashes checked = {len(arch['path_sha256'])}, "
              f"mismatches = {len(mism)}")
        for m in mism:
            print(f"    MISMATCH {m}")
        # receipt-internal path_sha256 (excludes itself by construction)
        rpath = [p for p in declared if p.endswith("snapshot-receipt.json")][0]
        receipt = json.loads(git("cat-file", "blob", f"{commit}:{rpath}"))
        rmism = []
        for p, h in sorted(receipt["path_sha256"].items()):
            got = blob_sha256(commit, p)
            if got != h:
                rmism.append((p, h, got))
        print(f"  receipt hashes checked = {len(receipt['path_sha256'])}, "
              f"mismatches = {len(rmism)}, "
              f"receipt.declared_path_count = {receipt['declared_path_count']}, "
              f"receipt.commit_sha = {receipt['commit_sha']!r}")
        for m in rmism:
            print(f"    MISMATCH {m}")
        verdict = equal and not mism and not rmism and parent == arch["parent_sha"] \
            and receipt["declared_path_count"] == expect_n \
            and receipt["commit_sha"] is None
        print(f"  VERDICT: {'EQUAL/CLEAN' if verdict else 'DEFECT'}")
        print()
        ok = ok and verdict
    print("ALL THREE ARCHIVES:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
