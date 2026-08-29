#!/usr/bin/env python3
"""Sweep every `active` goal's current dispatch queue and classify it.

This exists because the harness kept stalling on a per-goal basis: a session
would pick one `active` goal, spend its whole budget discovering that its
queue fails content-hash verification or has nothing dispatchable, then
repeat that discovery from scratch on the next goal. Nothing recorded the
outcome, so the next session paid the same cost again.

This tool renders `tools/research_dispatch.py` against every `active` goal's
`dispatch_queue_path` (from a throwaway output location — it writes no
ledger or coordination state) and classifies each goal into exactly one
bucket:

  ready        - dispatch succeeded and at least one Ready Task has
                 claim: null (something is actually dispatchable now).
  blocked      - dispatch succeeded but there is nothing to start (every
                 task is gated, claimed, or deferred). Not an error; this is
                 an ordinary campaign state.
  needs_repair - dispatch itself failed (hash mismatch, malformed queue,
                 missing file, ...). This is an integrity problem with the
                 queue or the local worktree, never a research result, and
                 it is never negative evidence about the goal's hypothesis.

Use `--json` for machine consumption (the launch-research-harness skill
reads this to pick a goal without re-deriving the sweep by hand) or the
default table for a human-readable status board.

This is read-only: it never writes to `ledger/`, `coordination/`, or claims.
"""

from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml


def discover_active_goals(repo_root: Path) -> list[dict[str, Any]]:
    goals: list[dict[str, Any]] = []
    # Goals exist in two layouts (CLAUDE.md "Concurrency: many agents, many
    # worktrees" -- tools/shard_goal.py): a flat ledger/goals/GOAL-X.yaml, or
    # a sharded ledger/goals/GOAL-X/goal.yaml (with checkpoints/ alongside).
    # Both must be scanned or the sharded goals are invisible to this sweep.
    goal_paths = sorted(glob.glob(str(repo_root / "ledger" / "goals" / "GOAL-*.yaml")))
    goal_paths += sorted(glob.glob(str(repo_root / "ledger" / "goals" / "GOAL-*" / "goal.yaml")))
    for path in goal_paths:
        p = Path(path)
        # For the sharded layout the filename is always "goal.yaml"; the
        # real id is the parent directory name, not the file stem.
        fallback_id = p.parent.name if p.name == "goal.yaml" else p.stem
        try:
            doc = yaml.safe_load(p.read_text())
        except Exception as exc:  # noqa: BLE001 - reported per-goal, not raised
            goals.append({
                "id": fallback_id,
                "path": path,
                "status": "unparseable",
                "error": str(exc),
            })
            continue
        record = doc.get("research_goal", doc) if isinstance(doc, dict) else {}
        if record.get("status") != "active":
            continue
        goals.append({
            "id": record.get("id", fallback_id),
            "path": path,
            "status": "active",
            "dispatch_queue_path": record.get("dispatch_queue_path"),
            "current_batch_id": record.get("current_batch_id"),
            "next_action": record.get("next_action"),
        })
    return goals


def classify(repo_root: Path, goal: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    queue_path = goal.get("dispatch_queue_path")
    result: dict[str, Any] = {
        "id": goal["id"],
        "current_batch_id": goal.get("current_batch_id"),
        "dispatch_queue_path": queue_path,
    }

    if goal["status"] != "active":
        result["bucket"] = "needs_repair"
        result["reason"] = f"goal record unparseable: {goal.get('error')}"
        return result

    if not queue_path:
        result["bucket"] = "needs_repair"
        result["reason"] = "goal record has no dispatch_queue_path"
        return result

    abs_queue = repo_root / queue_path
    if not abs_queue.exists():
        result["bucket"] = "needs_repair"
        result["reason"] = f"dispatch_queue_path does not exist: {queue_path}"
        return result

    out_json = out_dir / f"{goal['id']}.plan.json"
    out_md = out_dir / f"{goal['id']}.plan.md"
    proc = subprocess.run(
        [
            sys.executable,
            str(repo_root / "tools" / "research_dispatch.py"),
            str(abs_queue),
            "--output", str(out_json),
            "--report", str(out_md),
            "--claims", "refs",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    if proc.returncode != 0:
        result["bucket"] = "needs_repair"
        result["reason"] = (proc.stderr or proc.stdout).strip().splitlines()[-1] if (proc.stderr or proc.stdout) else "dispatch failed with no message"
        return result

    plan = json.loads(out_json.read_text())
    ready_tasks = [
        t for t in plan.get("dispatches", [])
        if t.get("claim") in (None, "null") or not t.get("claim")
    ]
    result["bucket"] = "ready" if ready_tasks else "blocked"
    result["ready_task_ids"] = [t.get("id") for t in ready_tasks]
    result["next_action"] = goal.get("next_action")
    return result


def is_shallow_clone(repo_root: Path) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--is-shallow-repository"],
        capture_output=True, text=True,
    )
    return proc.stdout.strip() == "true"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", default=".", help="Repository root (default: cwd)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of a table")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    # A shallow clone makes research_dispatch.py's commit-reachability checks
    # fail for perfectly good archives whose commit is real but older than the
    # shallow fetch boundary, or lives on a branch this clone never fetched
    # deep enough to see. That produced a false needs_repair epidemic here
    # once (31 of 47 goals) that dropped to 12 after `git fetch --unshallow`
    # -- nearly all of it was this artifact, not real corruption. Surface it
    # loudly rather than let every session re-diagnose it as repository rot.
    shallow = is_shallow_clone(repo_root)
    if shallow and not args.json:
        print(
            "WARNING: this is a SHALLOW git clone. Commit-reachability checks below\n"
            "will misclassify real, correctly-archived work as needs_repair. Run\n"
            "`git fetch --unshallow origin` first and re-run this sweep before trusting\n"
            "the needs_repair bucket.\n",
            file=sys.stderr,
        )

    goals = discover_active_goals(repo_root)

    with tempfile.TemporaryDirectory(prefix="goal_portfolio_health_") as tmp:
        out_dir = Path(tmp)
        results = [classify(repo_root, g, out_dir) for g in goals]

    if args.json:
        print(json.dumps({"shallow_clone_warning": shallow, "goals": results}, indent=2))
        return 0

    buckets: dict[str, list[dict[str, Any]]] = {"ready": [], "blocked": [], "needs_repair": []}
    for r in results:
        buckets.setdefault(r["bucket"], []).append(r)

    print(f"# Goal portfolio health ({len(results)} active goals)\n")
    print(f"## Ready ({len(buckets['ready'])}) — dispatchable now\n")
    for r in buckets["ready"]:
        print(f"- {r['id']} ({r['current_batch_id']}): {', '.join(r['ready_task_ids'])}")
    print(f"\n## Blocked ({len(buckets['blocked'])}) — nothing to start, not an error\n")
    for r in buckets["blocked"]:
        print(f"- {r['id']} ({r['current_batch_id']})")
    print(f"\n## Needs repair ({len(buckets['needs_repair'])}) — integrity problem, not a research result\n")
    for r in buckets["needs_repair"]:
        print(f"- {r['id']}: {r['reason']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
