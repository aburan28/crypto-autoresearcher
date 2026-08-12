#!/usr/bin/env python3
"""Convert a goal record to the sharded, append-only checkpoint layout.

    ledger/goals/GOAL-X-001.yaml
        ->  ledger/goals/GOAL-X-001/goal.yaml
            ledger/goals/GOAL-X-001/checkpoints/BATCH-001.yaml
            ledger/goals/GOAL-X-001/checkpoints/BATCH-002.yaml

WHY. A goal record is the one ledger file that MANY campaigns write.
`GOAL-PATH-001` is edited by all eight of its children; every batch close
appends an entry to one `batch_checkpoints` list. Two coordinators appending
independent entries to the same YAML sequence conflict every single time --
a textual conflict where there is no semantic conflict at all.

One file per checkpoint removes the conflict by construction. It is the same
move that fixed identifier collisions: stop making a writer touch shared state
it has no reason to touch. A batch close then writes ONE NEW FILE and changes
the goal record only if the goal's own status, next_action or
latest_verified_commit actually changed.

NOT AUTOMATIC, AND ON PURPOSE. Converting all goals at once would land a rename
in every one of the ~115 open branches simultaneously, which is precisely the
kind of repo-wide churn this layout exists to avoid. Convert a goal when its
Coordinator next has it open, and let the rest arrive over time;
`validate_ledger.py` reads both layouts indefinitely.

    python3 tools/shard_goal.py GOAL-PATH-001            # convert
    python3 tools/shard_goal.py GOAL-PATH-001 --dry-run  # show the plan
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOALS = os.path.join(REPO, "ledger", "goals")
SAFE = re.compile(r"[^A-Za-z0-9._-]+")


class _Dumper(yaml.SafeDumper):
    """Block style throughout, so a shard reads like every other ledger record."""


def _str_presenter(dumper, data):
    if "\n" in data or len(data) > 88:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_Dumper.add_representer(str, _str_presenter)


def dump(payload: dict) -> str:
    return yaml.dump(payload, Dumper=_Dumper, sort_keys=False,
                     default_flow_style=False, allow_unicode=True, width=88)


def shard_name(entry: dict, index: int) -> str:
    raw = str(entry.get("batch_id") or entry.get("id") or f"CHECKPOINT-{index:03d}")
    return SAFE.sub("-", raw).strip("-") or f"CHECKPOINT-{index:03d}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("goal_id")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    flat = os.path.join(GOALS, f"{args.goal_id}.yaml")
    directory = os.path.join(GOALS, args.goal_id)
    if not os.path.exists(flat):
        if os.path.isdir(directory):
            print(f"{args.goal_id} is already sharded", file=sys.stderr)
            return 0
        print(f"no such goal record: {flat}", file=sys.stderr)
        return 2

    with open(flat, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    goal = (doc or {}).get("research_goal")
    if not isinstance(goal, dict):
        print(f"{flat}: missing top-level 'research_goal'", file=sys.stderr)
        return 2

    checkpoints = goal.get("batch_checkpoints") or []
    if not isinstance(checkpoints, list):
        print(f"{flat}: batch_checkpoints is not a list", file=sys.stderr)
        return 2

    names: dict[str, int] = {}
    plan: list[tuple[str, dict]] = []
    for index, entry in enumerate(checkpoints, 1):
        if not isinstance(entry, dict):
            print(f"{flat}: batch_checkpoints[{index - 1}] is not a mapping",
                  file=sys.stderr)
            return 2
        base = shard_name(entry, index)
        names[base] = names.get(base, 0) + 1
        if names[base] > 1:
            base = f"{base}-{names[base]}"
        plan.append((base, entry))

    remainder = {k: v for k, v in goal.items() if k != "batch_checkpoints"}

    print(f"{args.goal_id}: {len(plan)} checkpoint(s) -> "
          f"ledger/goals/{args.goal_id}/checkpoints/")
    for base, _ in plan:
        print(f"  {base}.yaml")
    if args.dry_run:
        print("dry run; nothing written")
        return 0

    os.makedirs(os.path.join(directory, "checkpoints"), exist_ok=True)
    for base, entry in plan:
        target = os.path.join(directory, "checkpoints", f"{base}.yaml")
        if os.path.exists(target):
            print(f"refusing to overwrite {target}", file=sys.stderr)
            return 2
        header = (
            "# WRITE-ONCE. One checkpoint per file so that concurrent batch\n"
            "# closes in different worktrees never touch the same bytes. Append a\n"
            "# new file; never edit or reorder an existing one. Corrections\n"
            "# supersede, exactly as they do for any other immutable record.\n"
        )
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(header + dump({"batch_checkpoint": entry}))

    with open(os.path.join(directory, "goal.yaml"), "w", encoding="utf-8") as fh:
        fh.write(
            "# Sharded goal record. The mutable head lives here; the checkpoint\n"
            "# log lives one-file-per-batch under checkpoints/ so that a batch\n"
            "# close in another worktree does not conflict with this file.\n"
            "# validate_ledger.py merges the two before checking anything.\n"
            + dump({"research_goal": remainder})
        )

    subprocess.run(["git", "-C", REPO, "rm", "-q", "--cached", "--",
                    os.path.relpath(flat, REPO)], check=False,
                   capture_output=True)
    os.remove(flat)
    print(f"wrote ledger/goals/{args.goal_id}/goal.yaml and "
          f"{len(plan)} checkpoint shard(s); removed the flat record")
    print("re-run tools/validate_ledger.py before committing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
