#!/usr/bin/env python3
"""J2 check 1: hash-verify the v2 snapshot-bound package against the
TASK-20260908-9439c0 snapshot receipt (content_first, commit 796eed5...).
Recomputes sha256 of every declared path; compares to receipt path_sha256
and to the queue-archive-block pin (which also pins the receipt file itself).
"""
import hashlib, json, subprocess, sys

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
RECEIPT = "coordination/goals/GOAL-ECRANK-002/batches/BATCH-e3cf55/archives/TASK-20260908-9439c0/snapshot-receipt.json"
QUEUE = "coordination/goals/GOAL-ECRANK-002/batches/BATCH-e3cf55/dispatch_queue.json"

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

receipt = json.load(open(f"{ROOT}/{RECEIPT}"))
queue = json.load(open(f"{ROOT}/{QUEUE}"))

# locate the snapshot archive block in the queue
snap = None
for t in queue["tasks"]:
    if t.get("archive", {}).get("kind") == "snapshot":
        snap = t["archive"]
        break
assert snap is not None, "no snapshot archive block in queue"

print("== receipt header ==")
print("task_id:", receipt["task_id"])
print("kind:", receipt["kind"])
print("binding_mode (queue):", snap.get("binding_mode"))
print("receipt commit_sha:", receipt["commit_sha"], "parent_sha:", receipt["parent_sha"])
print("queue commit_sha:", snap["commit_sha"])
print("queue parent_sha:", snap["parent_sha"])
print("expected_path_count:", receipt["expected_path_count"])
print("len(staged_paths):", len(receipt["staged_paths"]))
print("len(path_sha256):", len(receipt["path_sha256"]))

# 1a. receipt file itself vs queue pin
receipt_disk = sha256_file(f"{ROOT}/{RECEIPT}")
print("\n== receipt file self-hash ==")
print("disk sha256:", receipt_disk)
print("queue pin  :", snap["path_sha256"][RECEIPT])
print("MATCH" if receipt_disk == snap["path_sha256"][RECEIPT] else "MISMATCH")

# 1b. every declared path
staged = receipt["staged_paths"]
declared = receipt["path_sha256"]
mismatch = []
missing = []
for p in staged:
    disk = sha256_file(f"{ROOT}/{p}")
    rec = declared.get(p)
    qpin = snap["path_sha256"].get(p)
    ok_rec = (rec == disk)
    ok_q = (qpin == disk)
    if not (ok_rec and ok_q):
        mismatch.append((p, disk, rec, qpin))
print("\n== per-path sha256 (63 declared) ==")
print(f"checked {len(staged)} paths; mismatches: {len(mismatch)}")
for p, disk, rec, qpin in mismatch:
    print("MISMATCH", p, "disk", disk, "receipt", rec, "queue", qpin)

# 1c. staged_paths vs path_sha256 key set
s1, s2 = set(staged), set(declared)
print("\nstaged==path_sha256 keys:", s1 == s2,
      "| only-staged:", sorted(s1 - s2), "| only-hash:", sorted(s2 - s1))

# 1d. queue archive block path set vs receipt
qset = set(snap["path_sha256"])
print("queue pin set == staged set:", qset == s1,
      "| only-queue:", sorted(qset - s1), "| only-staged:", sorted(s1 - qset))

# 1e. git object verification of commit/parent.
# PRIMARY (in-scope): commit from review-plan input_binding.snapshot_commit;
# parent from the receipt's own base_commit_checked note (merge commit 9a8403c650).
# SECONDARY (disclosed, out-of-scope read): queue archive block backfill.
def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)

commit = "796eed5fa06ac369f592175b55395d5853329dfa"  # review-plan input_binding
parent = "9a8403c650c4192a91f40353712fb76338a64694"  # receipt base_commit_checked note
print("\nqueue backfill cross-check: commit", snap["commit_sha"] == commit,
      "parent", snap["parent_sha"] == parent)
r = git("cat-file", "-t", commit)
print("\n== git objects ==")
print("commit type:", r.stdout.strip(), r.stderr.strip())
r = git("cat-file", "-t", parent)
print("parent type:", r.stdout.strip(), r.stderr.strip())
r = git("rev-parse", commit + "^")
print("git parent of commit:", r.stdout.strip())
print("parent matches queue parent_sha:", r.stdout.strip() == parent)
r = git("log", "--format=%s", "-1", commit)
print("commit subject:", r.stdout.strip())
r = git("merge-base", "--is-ancestor", commit, "HEAD")
print("commit reachable from HEAD:", r.returncode == 0)

# 1f. tree check: every staged path present in commit tree with matching blob sha
r = git("ls-tree", "-r", commit)
tree = {}
for line in r.stdout.splitlines():
    meta, path = line.split("\t", 1)
    mode, typ, sha = meta.split()
    tree[path] = sha
print("\n== commit tree vs staged paths ==")
tree_bad = []
for p in staged:
    blob = tree.get(p)
    disk = sha256_file(f"{ROOT}/{p}")
    if blob != disk:
        tree_bad.append((p, blob, disk))
print(f"paths in commit tree with blob sha == disk sha: {len(staged) - len(tree_bad)}/{len(staged)}")
for p, blob, disk in tree_bad:
    print("TREE MISMATCH", p, "tree", blob, "disk", disk)
print("commit tree total paths:", len(tree))
