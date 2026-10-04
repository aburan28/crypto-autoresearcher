#!/usr/bin/env python3
"""J2 check 1 (corrected tree verification): compare git blob SHAs
(git hash-object of disk file) against the snapshot commit's tree entries.
The receipt's path_sha256 is RAW sha256 of content (verified separately);
the git tree stores SHA-1 of the git blob object, so the two must be
compared in their own domains.
"""
import subprocess

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
COMMIT = "796eed5fa06ac369f592175b55395d5853329dfa"
PARENT = "9a8403c650c4192a91f40353712fb76338a64694"

import json
receipt = json.load(open(f"{ROOT}/coordination/goals/GOAL-ECRANK-002/batches/BATCH-e3cf55/archives/TASK-20260908-9439c0/snapshot-receipt.json"))
staged = receipt["staged_paths"]

def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)

# tree of the snapshot commit
r = git("ls-tree", "-r", COMMIT)
tree = {}
for line in r.stdout.splitlines():
    meta, path = line.split("\t", 1)
    mode, typ, sha = meta.split()
    tree[path] = sha

bad = []
for p in staged:
    blob_at_commit = tree.get(p)
    disk_blob = git("hash-object", p).stdout.strip()
    if blob_at_commit != disk_blob:
        bad.append((p, blob_at_commit, disk_blob))

print(f"staged paths: {len(staged)}")
print(f"present in commit tree: {sum(1 for p in staged if p in tree)}/{len(staged)}")
print(f"blob sha (git) disk == commit tree: {len(staged) - len(bad)}/{len(staged)}")
for p, a, b in bad:
    print("TREE MISMATCH", p, "commit", a, "disk", b)

# also: is the worktree clean at HEAD for these paths (no uncommitted drift)?
r = git("status", "--porcelain")
dirty = [l for l in r.stdout.splitlines() if not l.startswith("??")]
print("tracked-file modifications in worktree:", dirty if dirty else "none (clean)")

# parent verification
r = git("rev-parse", COMMIT + "^")
print("git parent of", COMMIT[:8], "=", r.stdout.strip(), "| matches declared parent:", r.stdout.strip() == PARENT)
r = git("cat-file", "-p", COMMIT)
print("commit header:")
print("\n".join(r.stdout.splitlines()[:6]))
