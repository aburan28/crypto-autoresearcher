#!/usr/bin/env python3
"""Validator J-work: re-verify the 73 receipt-bound path hashes.

Reads the snapshot receipt (TASK-20260909-b95f26, recorded in
tasks/TASK-20260909-2989a0/snapshot-receipt.json) and recomputes sha256 of
each bound path in the working tree. Also compares against the snapshot
commit's tree where the commit is reachable, to separate working-tree drift
from commit-vs-receipt drift.
"""
import hashlib
import json
import subprocess
import sys

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e962f6-20260910"
RECEIPT = f"{ROOT}/experiments/EXP-ECDLP-e962f6/tasks/TASK-20260909-2989a0/snapshot-receipt.json"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    with open(RECEIPT) as f:
        receipt = json.load(f)
    paths = receipt["path_sha256"]
    print(f"receipt n_paths field: {receipt['n_paths']}; entries: {len(paths)}")
    print(f"parent_sha: {receipt['parent_sha']}")

    # Find the snapshot commit: the commit whose message names TASK-20260909-b95f26
    # and whose parent is parent_sha.
    log = subprocess.run(
        ["git", "log", "--format=%H %P %s", "--all"],
        capture_output=True, text=True, cwd=ROOT,
    ).stdout
    snap = None
    for line in log.splitlines():
        parts = line.split(" ", 2)
        if len(parts) == 3 and "TASK-20260909-b95f26" in parts[2] and parts[1].startswith(receipt["parent_sha"][:12]):
            snap = parts[0]
    print(f"snapshot commit (message names b95f26, parent matches): {snap}")

    ok = bad = missing = 0
    bad_rows = []
    for p, expected in sorted(paths.items()):
        fp = f"{ROOT}/{p}"
        try:
            actual = sha256_file(fp)
        except FileNotFoundError:
            missing += 1
            bad_rows.append((p, "MISSING", expected))
            continue
        if actual == expected:
            ok += 1
        else:
            bad += 1
            bad_rows.append((p, actual, expected))
    print(f"working-tree: match={ok} mismatch={bad} missing={missing}")
    for p, a, e in bad_rows:
        print(f"  MISMATCH {p}\n    actual   {a}\n    expected {e}")

    if snap:
        # Compare receipt against the snapshot commit's tree (git cat-file)
        okc = badc = 0
        badc_rows = []
        for p, expected in sorted(paths.items()):
            r = subprocess.run(
                ["git", "cat-file", "-p", f"{snap}:{p}"],
                capture_output=True, cwd=ROOT,
            )
            if r.returncode != 0:
                badc += 1
                badc_rows.append((p, "NOT IN COMMIT", expected))
                continue
            actual = hashlib.sha256(r.stdout).hexdigest()
            if actual == expected:
                okc += 1
            else:
                badc += 1
                badc_rows.append((p, actual, expected))
        print(f"snapshot-commit {snap[:12]}: match={okc} mismatch={badc}")
        for p, a, e in badc_rows:
            print(f"  COMMIT-MISMATCH {p}\n    actual   {a}\n    expected {e}")
    return 0 if (bad == 0 and missing == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
