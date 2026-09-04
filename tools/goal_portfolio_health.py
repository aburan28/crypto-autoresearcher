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
        # A null dispatch_queue_path is a deliberate, legal committed value
        # in this ledger, not a defect: several goals' own audited head
        # notes explain exactly why (a design-only batch dispatched directly
        # by a skill rather than tools/research_dispatch.py, or an explicit
        # no-queue hold) -- see e.g. GOAL-ARGON-001's
        # dispatch_queue_path_note_20260813_batch_ba7b2f and GOAL-HAWK-001's
        # dispatch_queue_path_note_head_reconciliation_20260810. Nothing is
        # dispatchable, which is exactly what "blocked" means; it is never
        # evidence that anything is broken.
        result["bucket"] = "blocked"
        result["reason"] = "goal record has no dispatch_queue_path (may be legitimate -- check the goal's own head notes before treating as a defect)"
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


FOCUS_PATH = "orchestration/research-focus.yaml"


def load_focus(repo_root: Path) -> dict[str, Any] | None:
    """Read the declared research focus, or None when none is declared.

    Absent or unparseable, every goal ranks equally and this tool behaves
    exactly as it did before the focus existed. The focus is a PRIORITY
    ORDER, never a filter: an unlisted goal still appears in every bucket and
    is still dispatchable.
    """

    path = repo_root / FOCUS_PATH
    if not path.exists():
        return None
    try:
        import yaml
    except ImportError:
        return None
    try:
        data = yaml.safe_load(path.read_text())
    except Exception as error:  # a malformed focus must not break the sweep
        print(f"NOTE: ignoring unreadable {FOCUS_PATH}: {error}", file=sys.stderr)
        return None
    return data if isinstance(data, dict) and data.get("tiers") else None


def goal_area(goal_id: str) -> str:
    """`GOAL-<AREA>-<tok>` -> AREA. Legacy three-digit IDs share the shape."""

    parts = goal_id.split("-")
    return parts[1] if len(parts) >= 2 else ""


def focus_tier(goal_id: str, focus: dict[str, Any] | None) -> int:
    """Rank one goal against the declared focus. Lower sorts first."""

    if not focus:
        return 0
    for entry in focus.get("tiers") or []:
        if goal_id in (entry.get("goals") or []):
            return int(entry["tier"])
        if goal_area(goal_id) in (entry.get("areas") or []):
            return int(entry["tier"])
    return int(focus.get("default_tier", 99))


def tier_names(focus: dict[str, Any] | None) -> dict[int, str]:
    if not focus:
        return {}
    return {int(e["tier"]): e.get("name", "") for e in focus.get("tiers") or []}


def is_shallow_clone(repo_root: Path) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--is-shallow-repository"],
        capture_output=True, text=True,
    )
    return proc.stdout.strip() == "true"


def deepen_clone(repo_root: Path) -> tuple[bool, str]:
    """Fetch the full history a shallow clone is missing.

    Returns (deepened, detail). This is a fetch: it only ADDS history. It
    rewrites nothing, touches no working tree, and cannot invalidate an archive
    receipt -- the failure mode it removes is entirely one of missing objects.

    Doing it automatically is the point. The sweep has been able to detect a
    shallow clone and name the one command that fixes it for as long as the
    warning has existed, and a session still had to read the banner, believe
    it, and act on it before any result below could be trusted. A session that
    skipped that step read 26 correctly-archived goals as corrupt and had
    nothing to dispatch.
    """

    proc = subprocess.run(
        ["git", "-C", str(repo_root), "fetch", "--unshallow", "origin"],
        capture_output=True, text=True,
    )
    if proc.returncode == 0 and not is_shallow_clone(repo_root):
        return True, "deepened via `git fetch --unshallow origin`"
    detail = (proc.stderr or proc.stdout).strip().splitlines()
    return False, detail[-1] if detail else f"git exited {proc.returncode}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", default=".", help="Repository root (default: cwd)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of a table")
    parser.add_argument(
        "--focus-only", action="store_true",
        help="Show only goals in the declared focus's dispatch_first tiers "
             f"({FOCUS_PATH}). Use when a session should work the focus lane "
             "and nothing else.")
    parser.add_argument(
        "--no-deepen", action="store_true",
        help="Do not auto-fetch missing history on a shallow clone. The "
             "needs_repair bucket is then untrustworthy -- see the warning it prints.")
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
    deepened = False
    if shallow and not args.no_deepen:
        deepened, detail = deepen_clone(repo_root)
        shallow = not deepened
        print(
            f"Shallow clone detected: {detail}." if deepened
            else f"Shallow clone detected and could NOT be deepened: {detail}.",
            file=sys.stderr,
        )
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

    focus = load_focus(repo_root)
    names = tier_names(focus)
    dispatch_first = {int(e["tier"]) for e in (focus or {}).get("tiers") or []
                      if e.get("dispatch_first")}
    for r in results:
        r["focus_tier"] = focus_tier(r["id"], focus)
    if args.focus_only:
        if not dispatch_first:
            print(f"--focus-only: no dispatch_first tier declared in {FOCUS_PATH}.",
                  file=sys.stderr)
            return 2
        results = [r for r in results if r["focus_tier"] in dispatch_first]
    # Rank by focus first, then by ID. This is the ordering the goal-selection
    # step consumes, so it is what actually aims the program.
    results.sort(key=lambda r: (r["focus_tier"], r["id"]))

    if args.json:
        print(json.dumps({"shallow_clone_warning": shallow,
                          "clone_deepened": deepened,
                          "focus": (focus or {}).get("focus"),
                          "focus_path": FOCUS_PATH,
                          "goals": results}, indent=2))
        return 0

    buckets: dict[str, list[dict[str, Any]]] = {"ready": [], "blocked": [], "needs_repair": []}
    for r in results:
        buckets.setdefault(r["bucket"], []).append(r)

    scope = " in focus" if args.focus_only else ""
    print(f"# Goal portfolio health ({len(results)} active goals{scope})\n")
    if focus:
        listed = ", ".join(
            f"tier {t} {names[t]}" for t in sorted(names)) or "none"
        print(f"Focus: **{focus.get('focus')}** ({FOCUS_PATH}) — {listed}.")
        print("Goals are listed focus-first; dispatch from the top.\n")

    def label(r: dict[str, Any]) -> str:
        tier = r.get("focus_tier", 0)
        return f" [tier {tier}]" if focus and tier else ""

    print(f"## Ready ({len(buckets['ready'])}) — dispatchable now\n")
    for r in buckets["ready"]:
        print(f"- {r['id']}{label(r)} ({r['current_batch_id']}): "
              f"{', '.join(r['ready_task_ids'])}")
    print(f"\n## Blocked ({len(buckets['blocked'])}) — nothing to start, not an error\n")
    for r in buckets["blocked"]:
        print(f"- {r['id']}{label(r)} ({r['current_batch_id']})")
    print(f"\n## Needs repair ({len(buckets['needs_repair'])}) — integrity problem, not a research result\n")
    for r in buckets["needs_repair"]:
        print(f"- {r['id']}{label(r)}: {r['reason']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
