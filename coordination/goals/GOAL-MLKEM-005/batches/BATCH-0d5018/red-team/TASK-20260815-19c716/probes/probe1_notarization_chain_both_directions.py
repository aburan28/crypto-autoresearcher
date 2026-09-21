#!/usr/bin/env python3
"""RT probe 1 (TASK-20260815-19c716): verify the TASK-20260815-02b01b snapshot
notarization chain in BOTH directions with git plumbing only.

Direction A (declared -> commit): every path_sha256 entry declared in
dispatch_queue.json for TASK-20260815-02b01b must equal sha256 of that path's
blob AS STORED IN commit 856ff0a6e.

Direction B (commit -> working tree): every path the commit actually changed
must have identical bytes in the working tree I am reading, so that the
artifacts I review are the artifacts that were notarized. Any divergence means
I am reviewing working-tree-only material, which agents/red-team.md forbids as
durable evidence.

Also checks: commit reachability from origin/main and HEAD, declared parent,
and exact changed-path-set equality against the declared key set.

Read-only. Writes nothing outside this probe's own stdout.
"""
import hashlib
import json
import subprocess
import sys

REPO = "/Volumes/SSD990/crypto-autoresearcher"
QUEUE = (
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/dispatch_queue.json"
)
SNAP = "856ff0a6ee4d3998e72aca570a4e5d31d577b952"
PARENT_DECLARED = "b325e87382477c1fb3cf4aa59626ccdb1ad3b110"
ARCHIVE_TASK = "TASK-20260815-02b01b"


def git(*args, binary=False):
    r = subprocess.run(
        ["git", "-C", REPO, *args],
        capture_output=True,
        check=False,
    )
    if r.returncode != 0:
        return None
    return r.stdout if binary else r.stdout.decode().strip()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def main():
    out = {"probe": "probe1_notarization_chain_both_directions", "checks": {}}

    q = json.load(open(f"{REPO}/{QUEUE}"))
    task = next(t for t in q["tasks"] if t["id"] == ARCHIVE_TASK)
    declared = task["archive"]["path_sha256"]
    declared_parent = task["archive"]["parent_sha"]
    declared_sha = task["archive"]["commit_sha"]

    out["checks"]["declared_commit_sha_matches_dispatch_brief"] = (
        declared_sha == SNAP
    )
    out["checks"]["declared_parent_matches_dispatch_brief"] = (
        declared_parent == PARENT_DECLARED
    )

    # --- commit object sanity ---
    out["checks"]["commit_object_exists"] = git("cat-file", "-t", SNAP) == "commit"
    out["checks"]["actual_parent"] = git("rev-parse", f"{SNAP}^")
    out["checks"]["parent_matches"] = (
        out["checks"]["actual_parent"] == declared_parent
    )
    for ref in ("origin/main", "HEAD"):
        rc = subprocess.run(
            ["git", "-C", REPO, "merge-base", "--is-ancestor", SNAP, ref],
            capture_output=True,
        ).returncode
        out["checks"][f"reachable_from_{ref.replace('/', '_')}"] = rc == 0

    # --- exact changed-path set ---
    changed = set(
        (git("diff-tree", "--no-commit-id", "--name-only", "-r", SNAP) or "").split(
            "\n"
        )
    )
    changed.discard("")
    out["checks"]["changed_path_count"] = len(changed)
    out["checks"]["declared_path_count"] = len(declared)
    out["checks"]["changed_set_equals_declared_set"] = changed == set(declared)
    out["checks"]["declared_not_changed"] = sorted(set(declared) - changed)
    out["checks"]["changed_not_declared"] = sorted(changed - set(declared))

    # --- Direction A: declared digest vs commit blob ---
    dirA = {"match": [], "mismatch": [], "missing_in_commit": [], "non_hash": []}
    for path, dsha in sorted(declared.items()):
        blob = git("show", f"{SNAP}:{path}", binary=True)
        if blob is None:
            dirA["missing_in_commit"].append(path)
            continue
        actual = sha256_bytes(blob)
        if not isinstance(dsha, str) or len(dsha) != 64 or any(
            c not in "0123456789abcdef" for c in dsha.lower()
        ):
            dirA["non_hash"].append(
                {"path": path, "declared": dsha, "actual_in_commit": actual}
            )
            continue
        (dirA["match"] if actual == dsha.lower() else dirA["mismatch"]).append(
            path if actual == dsha.lower() else
            {"path": path, "declared": dsha, "actual": actual}
        )
    out["direction_A_declared_vs_commit"] = {
        "n_match": len(dirA["match"]),
        "n_mismatch": len(dirA["mismatch"]),
        "n_missing_in_commit": len(dirA["missing_in_commit"]),
        "n_non_hash_sentinel": len(dirA["non_hash"]),
        "mismatch_detail": dirA["mismatch"],
        "missing_detail": dirA["missing_in_commit"],
        "non_hash_detail": dirA["non_hash"],
    }

    # --- Direction B: commit blob vs working tree bytes I actually read ---
    dirB = {"identical": [], "divergent": [], "absent_in_worktree": []}
    for path in sorted(changed):
        blob = git("show", f"{SNAP}:{path}", binary=True)
        try:
            wt = open(f"{REPO}/{path}", "rb").read()
        except FileNotFoundError:
            dirB["absent_in_worktree"].append(path)
            continue
        if blob == wt:
            dirB["identical"].append(path)
        else:
            dirB["divergent"].append(
                {
                    "path": path,
                    "commit_sha256": sha256_bytes(blob),
                    "worktree_sha256": sha256_bytes(wt),
                    "commit_bytes": len(blob),
                    "worktree_bytes": len(wt),
                }
            )
    out["direction_B_commit_vs_worktree"] = {
        "n_identical": len(dirB["identical"]),
        "n_divergent": len(dirB["divergent"]),
        "n_absent_in_worktree": len(dirB["absent_in_worktree"]),
        "divergent_detail": dirB["divergent"],
        "absent_detail": dirB["absent_in_worktree"],
    }

    # --- follow-up commit that wrote commit_sha back into the receipt ---
    log = git(
        "log", "--format=%H %s", "-5", "--",
        "coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/archives/"
        f"{ARCHIVE_TASK}/snapshot-receipt.json",
    )
    out["receipt_commit_history"] = log

    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
