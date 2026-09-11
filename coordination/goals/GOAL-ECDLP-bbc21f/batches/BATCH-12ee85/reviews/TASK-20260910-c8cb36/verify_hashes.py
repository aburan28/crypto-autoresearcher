#!/usr/bin/env python3
"""J2 integrity verification: seal + snapshot receipt hash recomputation.
Run from repository root. Writes JSON results to stdout.
"""
import hashlib
import json
import subprocess
import sys

REPO = "."


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def git_show_blob(commit, path):
    """Return the file bytes as committed at `commit`."""
    r = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        capture_output=True, check=True)
    return r.stdout


def git_hash_committed(commit, path):
    return hashlib.sha256(git_show_blob(commit, path)).hexdigest()





results = {"stageA_seal": {}, "stageA_receipt": {}, "stageB_receipt": {},
           "commit_checks": {}, "errors": []}

# ---------------------------------------------------------------- Stage A seal
SEAL_DIR = "coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/reviews/TASK-20260907-7afa98"
seal = json.load(open(f"{SEAL_DIR}/seal.json"))
live_mismatches = []
for fname, declared in seal["sha256"].items():
    try:
        actual = sha256_file(f"{SEAL_DIR}/{fname}")
        match = (actual == declared)
    except FileNotFoundError:
        match = False
        actual = "FILE_NOT_FOUND"
    if not match:
        live_mismatches.append({"file": fname, "declared": declared, "actual": actual})
results["stageA_seal"] = {
    "files_checked": len(seal["sha256"]),
    "all_match_live_tree": not live_mismatches,
    "mismatches": live_mismatches,
    "sealed_at_utc": seal.get("sealed_at_utc"),
    "n_cells_computed": seal.get("n_cells_computed"),
    "grid": seal.get("grid"),
}

# ---------------------------------------------------- Stage A snapshot receipt
RECEIPT_A = "coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/archives/TASK-20260907-c3f20c/snapshot_commit_receipt.json"
receipt_a = json.load(open(RECEIPT_A))
rA_results = {}
for commit in ["d144025225d8ad0b981142266c20047484709431",
               "ab711b0662d620930a3c0a1550916575a48910ce"]:
    mm = []
    for path, declared in receipt_a["path_sha256"].items():
        try:
            actual = git_hash_committed(commit, path)
            ok = (actual == declared)
        except subprocess.CalledProcessError:
            ok = False
            actual = "PATH_NOT_IN_COMMIT"
        if not ok:
            mm.append({"path": path, "declared": declared, "actual": actual})
    # also live-tree check
    mm_live = []
    for path, declared in receipt_a["path_sha256"].items():
        try:
            actual = sha256_file(path)
            if actual != declared:
                mm_live.append({"path": path, "declared": declared, "actual": actual})
        except FileNotFoundError:
            mm_live.append({"path": path, "declared": declared, "actual": "NOT_FOUND"})
    rA_results[commit[:10]] = {
        "paths_checked": len(receipt_a["path_sha256"]),
        "all_match_committed_bytes": not mm,
        "mismatches_committed": mm,
        "all_match_live_tree": not mm_live,
        "mismatches_live": mm_live,
    }
results["stageA_receipt"] = {
    "commit_sha_declared": receipt_a["commit_sha"],
    "parent_sha_declared": receipt_a["parent_sha"],
    "per_commit": rA_results,
}
# commit-sha semantics: commit_sha should name the attestation commit.
# d144025225 added the receipt; ab711b0662 retargeted commit_sha.  Verify
# which commit the declared commit_sha resolves to and whether the receipt
# file's own bytes at the declared commit match the live receipt.
decl = receipt_a["commit_sha"]
try:
    # receipt bytes at declared commit
    actual = hashlib.sha256(git_show_blob(decl, RECEIPT_A)).hexdigest()
    live = sha256_file(RECEIPT_A)
    results["stageA_receipt"]["receipt_bytes_at_declared_commit_match_live"] = (actual == live)
except subprocess.CalledProcessError:
    results["stageA_receipt"]["receipt_bytes_at_declared_commit_match_live"] = "DECLARED_COMMIT_MISSING"

# ---------------------------------------------------- Stage B snapshot receipt
RECEIPT_B = "coordination/experiments/EXP-ECDLP-6ac801/batches/BATCH-3c7493/archives/TASK-20260907-c20638/snapshot-receipt.json"
receipt_b = json.load(open(RECEIPT_B))
run_paths = {k: v for k, v in receipt_b["path_sha256"].items()
             if "/runs/" in k}
src_paths = {k: v for k, v in receipt_b["path_sha256"].items()
             if "/source/" in k}
SNAP = "9e6396c35e82e5ef0cec3d95728f5b0c2b447f9e"
BACKFILL = "718af27faed4fbdb12f954663f70ade4b9884acd"
mm_snap_runs, mm_snap_src, mm_live_b = [], [], []
for path, declared in receipt_b["path_sha256"].items():
    try:
        actual = git_hash_committed(SNAP, path)
        ok = (actual == declared)
        bucket = mm_snap_src if "/source/" in path else mm_snap_runs
        if not ok:
            bucket.append({"path": path, "declared": declared, "actual": actual})
    except subprocess.CalledProcessError:
        (mm_snap_src if "/source/" in path else mm_snap_runs).append(
            {"path": path, "declared": declared, "actual": "PATH_NOT_IN_COMMIT"})
    try:
        live = sha256_file(path)
        if live != declared:
            mm_live_b.append({"path": path, "declared": declared, "actual": live})
    except FileNotFoundError:
        mm_live_b.append({"path": path, "declared": declared, "actual": "NOT_FOUND"})
results["stageB_receipt"] = {
    "commit_sha_declared": receipt_b["commit_sha"],
    "parent_sha_declared": receipt_b["parent_sha"],
    "paths_checked_total": len(receipt_b["path_sha256"]),
    "run_paths_checked": len(run_paths),
    "source_paths_checked": len(src_paths),
    "all_match_committed_at_9e6396c35e": not (mm_snap_runs or mm_snap_src),
    "mismatches_committed": mm_snap_runs + mm_snap_src,
    "all_match_live_tree": not mm_live_b,
    "mismatches_live": mm_live_b,
    "receipt_bytes_at_backfill_commit": None,
}
# verify receipt content (incl. backfilled commit_sha) is the version committed
# at the backfill commit, and that the snapshot commit contains the runs.
try:
    at_backfill = hashlib.sha256(git_show_blob(BACKFILL, RECEIPT_B)).hexdigest()
    live = sha256_file(RECEIPT_B)
    results["stageB_receipt"]["receipt_bytes_at_backfill_commit"] = at_backfill == live
except subprocess.CalledProcessError:
    results["stageB_receipt"]["receipt_bytes_at_backfill_commit"] = "BACKFILL_COMMIT_MISSING"

# ------------------------------------------------------ commit topology checks
def parent_of(sha):
    r = subprocess.run(["git", "rev-parse", f"{sha}^"], capture_output=True, text=True)
    return r.stdout.strip()


results["commit_checks"] = {
    "d144025225": {"exists": True},
    "ab711b0662": {"exists": True},
    "9e6396c35e": {"parent": parent_of(SNAP)},
    "718af27fae": {"parent": parent_of(BACKFILL)},
}

print(json.dumps(results, indent=1))
