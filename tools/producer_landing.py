#!/usr/bin/env python3
"""Land a producer's output in the same turn the producer returns.

WHY THIS EXISTS
---------------
A producer subagent writes its deliverables into its assigned `write_scope` as
UNTRACKED files. They become durable only when a separate archival task runs,
and that task runs in a later turn of a session that may not exist by then.
Between production and archival the output lives in exactly one machine's
working tree.

On 2026-09-21 that window closed on three producers at once: two blind source
reads and a completed experiment run, 49 files including a run that had reached
`completed_valid` with 132 measured rows, all lost when the VM holding them was
replaced between turns (`CORR-20260921-942a62`).

The contract already required `archived_by` to be bound before dispatch, and it
WAS bound, for all three. It did not help, because **an owner is not a commit**.
This tool is the missing step: one command, run the moment a producer returns,
that makes its declared output exist somewhere other than this machine.

WHAT THIS IS NOT
----------------
NOT a replacement for the archival task. Landing makes bytes durable; the
archive still records the receipt, binds `path_sha256`, declares its binding
mode, and states what the output is evidence of. Those are different jobs and
the second one is the one a reviewer reads.

NOT a licence to write outside scope. Landing stages exactly the paths the
producing task declared, refuses anything outside its `write_scope`, and refuses
to touch a path another task owns.

NOT protection against a producer dying mid-write. The window from "subagent
starts writing" to "subagent returns" stays open, and partial output in it is
still lost. That is accepted: the exposure is bounded by one task instead of by
a whole session turn.

USAGE
-----
    python3 tools/producer_landing.py QUEUE TASK_ID [--push] [--dry-run]
    python3 tools/producer_landing.py QUEUE --check      # report, change nothing
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_MARKERS = ("AGENTS.md", ".git")


def discover_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if all((candidate / m).exists() for m in REPO_MARKERS):
            return candidate
    raise SystemExit(f"could not find a repository root above {start}")


def git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=False
    )
    if check and proc.returncode != 0:
        raise SystemExit(
            f"git {' '.join(args)} failed ({proc.returncode}):\n{proc.stderr.strip()}"
        )
    return proc.stdout


def load_queue(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read queue {path}: {exc}") from exc


def tracked_at_head(repo: Path, path: str) -> bool:
    out = git(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", path, check=False)
    return bool(out.strip())


def find_task(queue: dict, task_id: str) -> dict:
    for task in queue.get("tasks", []):
        if task["id"] == task_id:
            return task
    raise SystemExit(f"task {task_id} is not in this queue")


def is_archive(task: dict) -> bool:
    return bool(task.get("archive"))


def other_owners(queue: dict, task_id: str, paths: list[str]) -> dict[str, str]:
    """Which other task declares any of these paths as its own artifact?

    A producer landing must never stage a path a different task owns: that is
    how two tasks end up both claiming to have produced one file, which the
    dispatcher refuses for archives and which is no better here.
    """
    clashes: dict[str, str] = {}
    for other in queue.get("tasks", []):
        if other["id"] == task_id:
            continue
        for declared in other.get("artifact_paths", []):
            if declared in paths:
                clashes[declared] = other["id"]
    return clashes


def landing_status(repo: Path, queue: dict) -> list[dict]:
    """Per producer task: does its declared output exist, and is it landed?"""
    rows = []
    for task in queue.get("tasks", []):
        if is_archive(task):
            continue
        declared = list(task.get("artifact_paths", []))
        if not declared:
            continue
        on_disk, missing, landed, unlanded = [], [], [], []
        for rel in declared:
            if (repo / rel).exists():
                on_disk.append(rel)
                (landed if tracked_at_head(repo, rel) else unlanded).append(rel)
            else:
                missing.append(rel)
        rows.append({
            "task_id": task["id"],
            "state": task.get("state"),
            "declared": len(declared),
            "on_disk": on_disk,
            "missing": missing,
            "landed": landed,
            "unlanded": unlanded,
        })
    return rows


def report_check(repo: Path, queue_path: Path, queue: dict) -> int:
    rows = landing_status(repo, queue)
    exposed = [r for r in rows if r["unlanded"]]
    print(f"queue: {queue_path}")
    print(f"producer tasks with declared artifacts: {len(rows)}")
    if not exposed:
        print("\nNo unlanded producer output. Every declared artifact that exists "
              "on disk is present at HEAD.")
        return 0
    print(f"\nUNLANDED PRODUCER OUTPUT in {len(exposed)} task(s). These files exist "
          f"on this machine and NOWHERE ELSE:\n")
    for row in exposed:
        print(f"  {row['task_id']}  (state: {row['state']})")
        for rel in row["unlanded"]:
            print(f"      ! {rel}")
        if row["missing"]:
            print(f"      (declared but absent: {len(row['missing'])})")
    print("\nLand each with:")
    for row in exposed:
        print(f"  python3 tools/producer_landing.py {queue_path} {row['task_id']} --push")
    return 1


def land(repo: Path, queue_path: Path, queue: dict, task_id: str,
         push: bool, dry_run: bool) -> int:
    task = find_task(queue, task_id)
    if is_archive(task):
        raise SystemExit(
            f"{task_id} is an ARCHIVE task. Archives commit their own receipt and run "
            f"in isolation; use tools/research_dispatch.py's archival flow, not landing."
        )

    declared = list(task.get("artifact_paths", []))
    if not declared:
        raise SystemExit(f"{task_id} declares no artifact_paths; nothing to land")

    scopes = list(task.get("write_scope", []))
    outside = [
        rel for rel in declared
        if scopes and not any(rel == s or rel.startswith(s.rstrip("/") + "/")
                              for s in scopes)
    ]
    if outside:
        raise SystemExit(
            "these declared artifacts fall outside the task's own write_scope, which "
            "is a defect in the card rather than something landing may paper over:\n  "
            + "\n  ".join(outside)
        )

    clashes = other_owners(queue, task_id, declared)
    if clashes:
        lines = [f"  {p} is also declared by {t}" for p, t in sorted(clashes.items())]
        raise SystemExit("declared artifacts are owned by another task:\n"
                         + "\n".join(lines))

    present = [rel for rel in declared if (repo / rel).exists()]
    missing = [rel for rel in declared if rel not in present]
    if not present:
        raise SystemExit(
            f"{task_id} declares {len(declared)} artifact(s) and NONE exists on disk. "
            f"Nothing was produced, so there is nothing to land."
        )

    already = [rel for rel in present if tracked_at_head(repo, rel)]
    to_land = [rel for rel in present if rel not in already]

    print(f"task:     {task_id}")
    print(f"declared: {len(declared)}    on disk: {len(present)}    "
          f"already at HEAD: {len(already)}    to land: {len(to_land)}")
    if missing:
        print(f"\nDECLARED BUT ABSENT ({len(missing)}). Landing proceeds with what "
              f"exists; the gap is reported, never filled in:")
        for rel in missing:
            print(f"  - {rel}")
    if not to_land:
        print("\nEverything present is already at HEAD. Nothing to do.")
        return 0
    print("\nlanding:")
    for rel in to_land:
        print(f"  + {rel}")

    if dry_run:
        print("\n--dry-run: nothing staged, nothing committed.")
        return 0

    git(repo, "add", "--", *to_land)
    staged = [
        line for line in
        git(repo, "diff", "--cached", "--name-only").splitlines() if line.strip()
    ]
    unexpected = sorted(set(staged) - set(to_land))
    if unexpected:
        git(repo, "reset", "-q", "HEAD", "--", *staged)
        raise SystemExit(
            "staging picked up paths this task did not declare, so nothing was "
            "committed and the index was reset:\n  " + "\n  ".join(unexpected)
        )

    message = (
        f"land({task_id}): producer output, committed on return\n"
        f"\n"
        f"{len(to_land)} declared artifact(s) staged from this producer's write scope "
        f"and nothing else.\n"
        f"\n"
        f"This is a LANDING, not an archive. It makes the output exist somewhere other "
        f"than\none machine's working tree; the archival task that owns this producer "
        f"still has to\nwrite its receipt, bind path_sha256 and declare what the output "
        f"is evidence of.\nSee CORR-20260921-942a62 for the loss that made landing a "
        f"separate step.\n"
    )
    if missing:
        message += (
            f"\nDeclared but absent at landing time ({len(missing)}):\n"
            + "".join(f"  - {rel}\n" for rel in missing)
        )
    git(repo, "commit", "-q", "-m", message)
    head = git(repo, "rev-parse", "--short", "HEAD").strip()
    print(f"\ncommitted {head}")

    if push:
        branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
        git(repo, "push", "-u", "origin", branch)
        print(f"pushed to origin/{branch}")
    else:
        print("NOT PUSHED. A commit on a machine that disappears is still lost; "
              "pass --push, or push before the turn ends.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Commit a producer's declared output in the turn it returns."
    )
    parser.add_argument("queue", type=Path, help="dispatch_queue.json")
    parser.add_argument("task_id", nargs="?", help="the producing task to land")
    parser.add_argument("--check", action="store_true",
                        help="report unlanded output for every producer; change nothing")
    parser.add_argument("--push", action="store_true", help="push after committing")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would be staged; commit nothing")
    parser.add_argument("--repo-root", type=Path, default=None)
    args = parser.parse_args()

    repo = (args.repo_root or discover_repo_root(args.queue.resolve().parent)).resolve()
    queue = load_queue(args.queue)

    if args.check:
        if args.task_id:
            parser.error("--check reports on the whole queue; do not also name a task")
        return report_check(repo, args.queue, queue)
    if not args.task_id:
        parser.error("name a task to land, or pass --check")
    return land(repo, args.queue, queue, args.task_id, args.push, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
