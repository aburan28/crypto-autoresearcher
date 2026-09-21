#!/usr/bin/env python3
"""Instrument B: at-commit archive-receipt verification, S_a..S_e.

A re-implementation of the procedure specified in
coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-2cca27/contracts/integrity-review.json
checks[0], clauses (a)-(e), quoted in BATCH-127c82's frozen contract under
procedure_under_test.specification_verbatim.

Usage:
    procedure.py <receipt_path> <repo_root> [--base <verification_base>]

<receipt_path> is a dispatch-queue-shaped JSON document. Every task in it that
carries an ``archive`` object with a non-null ``commit_sha`` is verified. The
declared values are read from whatever receipt is supplied; the observed values
are recomputed from git at <repo_root>.

Output on stdout: one JSON object with a ``flags`` list. Each flag is the
4-tuple the contract specifies, as an object with keys step, locus,
declared_value, observed_value. An empty list means the procedure reports the
receipt intact.

Exit status: 0 when the flag set is empty, 3 when it is not. An unhandled
exception is deliberately NOT caught, so that a crash is observable as a crash
rather than being laundered into a verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from typing import Any

STEPS = ("S_a", "S_b", "S_c", "S_d", "S_e")


def git(repo_root: str, arguments: list[str]) -> tuple[int, bytes, str]:
    completed = subprocess.run(
        ["git", "-C", repo_root, *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return (
        completed.returncode,
        completed.stdout,
        completed.stderr.decode("utf-8", "replace").strip(),
    )


def flag(step: str, locus: str, declared: Any, observed: Any) -> dict[str, Any]:
    return {
        "step": step,
        "locus": locus,
        "declared_value": declared,
        "observed_value": observed,
    }


def verify_archive_block(repo_root: str, base: str, task: dict[str, Any]) -> list[dict[str, Any]]:
    archive = task["archive"]
    flags: list[dict[str, Any]] = []

    declared_commit = archive.get("commit_sha")
    declared_parent = archive.get("parent_sha")
    declared_hashes = archive.get("path_sha256") or {}
    declared_record_ids = archive.get("record_ids") or []

    # ---- S_a: the commit exists and is reachable from the verification base.
    code, out, _err = git(repo_root, ["rev-parse", "--verify", f"{declared_commit}^{{commit}}"])
    if code != 0:
        flags.append(flag("S_a", "archive.commit_sha", declared_commit, "does not resolve to a commit"))
        # Nothing downstream can be recomputed from a commit that does not exist.
        return flags
    resolved_commit = out.decode("ascii").strip()

    code, _out, _err = git(repo_root, ["merge-base", "--is-ancestor", resolved_commit, base])
    if code != 0:
        flags.append(
            flag("S_a", "archive.commit_sha", declared_commit, f"not reachable from {base}")
        )

    # ---- S_b: the declared parent equals the commit's actual FIRST parent.
    code, out, err = git(repo_root, ["show", "-s", "--format=%P", resolved_commit])
    if code != 0:
        flags.append(flag("S_b", "archive.parent_sha", declared_parent, f"git error: {err}"))
    else:
        parents = out.decode("ascii").split()
        observed_parent = parents[0] if parents else None
        if declared_parent != observed_parent:
            flags.append(flag("S_b", "archive.parent_sha", declared_parent, observed_parent))

    # ---- S_c: the commit's changed path set equals the declared path set exactly.
    code, out, err = git(
        repo_root,
        ["diff-tree", "--no-commit-id", "--no-renames", "--name-only", "-r", "--root", "-z", resolved_commit],
    )
    if code != 0:
        flags.append(flag("S_c", "commit.changed_paths", sorted(declared_hashes), f"git error: {err}"))
    else:
        changed = [p for p in out.decode("utf-8", "surrogateescape").split("\0") if p]
        declared_paths = set(declared_hashes)
        observed_paths = set(changed)
        for path in sorted(declared_paths - observed_paths):
            flags.append(flag("S_c", path, "declared", "not changed by the commit"))
        for path in sorted(observed_paths - declared_paths):
            flags.append(flag("S_c", path, "not declared", "changed by the commit"))

    # ---- S_d: per-path digest comparison. The receipt names the path, git
    # supplies the bytes, this procedure recomputes and compares. Every declared
    # path is checked; no path is skipped, deferred, or special-cased.
    for path in sorted(declared_hashes):
        declared_hash = declared_hashes[path]
        code, out, err = git(repo_root, ["cat-file", "-t", f"{resolved_commit}:{path}"])
        if code != 0:
            flags.append(flag("S_d", path, declared_hash, "absent from the commit tree"))
            continue
        if out.decode("ascii").strip() != "blob":
            flags.append(flag("S_d", path, declared_hash, "not a file blob"))
            continue
        code, blob, err = git(repo_root, ["show", f"{resolved_commit}:{path}"])
        if code != 0:
            flags.append(flag("S_d", path, declared_hash, f"git error: {err}"))
            continue
        observed_hash = hashlib.sha256(blob).hexdigest()
        if observed_hash != declared_hash:
            flags.append(flag("S_d", path, declared_hash, observed_hash))

    # ---- S_e: the commit message names the required task and record IDs.
    code, out, err = git(repo_root, ["log", "-1", "--format=%B", resolved_commit])
    if code != 0:
        flags.append(flag("S_e", "commit_message", [task["id"], *declared_record_ids], f"git error: {err}"))
    else:
        message = out.decode("utf-8", "replace")
        for identifier in [task["id"], *declared_record_ids]:
            if identifier not in message:
                flags.append(
                    flag("S_e", "commit_message", identifier, "absent from the commit message")
                )

    return flags


def main() -> int:
    parser = argparse.ArgumentParser(description="instrument B: at-commit archive-receipt verification")
    parser.add_argument("receipt", help="path to the receipt (dispatch-queue-shaped JSON)")
    parser.add_argument("repo_root", help="repository root supplying the observed bytes")
    parser.add_argument(
        "--base",
        default="HEAD",
        help="verification base the archive commit must be reachable from",
    )
    args = parser.parse_args()

    with open(args.receipt, "rb") as handle:
        receipt = json.loads(handle.read().decode("utf-8"))

    flags: list[dict[str, Any]] = []
    blocks_verified: list[str] = []
    for task in receipt.get("tasks", []):
        archive = task.get("archive")
        if not isinstance(archive, dict) or not archive.get("commit_sha"):
            continue
        blocks_verified.append(task["id"])
        flags.extend(verify_archive_block(args.repo_root, args.base, task))

    json.dump(
        {
            "instrument": "B",
            "receipt": args.receipt,
            "repo_root": args.repo_root,
            "verification_base": args.base,
            "steps_implemented": list(STEPS),
            "archive_blocks_verified": blocks_verified,
            "flags": flags,
        },
        sys.stdout,
        indent=2,
        sort_keys=False,
    )
    sys.stdout.write("\n")
    return 3 if flags else 0


if __name__ == "__main__":
    raise SystemExit(main())
