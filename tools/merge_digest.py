#!/usr/bin/env python3
"""Summarise what a merge to `main` actually changed, in research terms.

WHY THIS IS NOT A NOTIFICATION. There is no way to push an event to "all
runners": agent sessions are ephemeral, and at the moment a merge lands most of
the sessions that will care about it DO NOT YET EXIST. The available MCP
subscription (`subscribe_pr_activity`) is per-pull-request, single-consumer and
bound to one live session, so it cannot fan out and cannot reach a session
created tomorrow.

So this is a DURABLE FEED instead: one write-once record per merge under
`coordination/events/main/`, which any session can read whenever it wakes.

WHAT IT ADDS OVER `git log`. Nothing, for "which commits landed" -- use git for
that. What it adds is the SEMANTIC delta an agent actually needs before resuming:

  * which GOAL records changed STATUS or NEXT_ACTION, with old -> new;
  * which ledger and knowledge records are new, by type;
  * whether the shared contract moved (AGENTS.md, CLAUDE.md, docs/, tools/,
    .github/) -- the files that bind every campaign at once.

An agent on a 40-behind branch can answer "did anything change under my goal, or
in the rules I am bound by?" from one record rather than by diffing 40 commits.

    python3 tools/merge_digest.py --commit <sha>            # one merge
    python3 tools/merge_digest.py --since <ref> --until <ref>  # a range
    python3 tools/merge_digest.py --commit <sha> --out <path>  # write YAML
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RECORD_PATTERNS = {
    "goal": re.compile(r"^ledger/goals/(GOAL-[A-Z0-9]+-[0-9a-f]{3,6})"),
    "question": re.compile(r"^ledger/questions/(RQ-[A-Z]+-[0-9a-f]{3,6})\.yaml$"),
    "hypothesis": re.compile(r"^ledger/hypotheses/(H-[A-Z]+-[0-9a-f]{3,6})\.yaml$"),
    "evidence": re.compile(r"^ledger/evidence/(EV-[A-Z]+-[0-9a-f]{3,6})\.yaml$"),
    "decision": re.compile(r"^ledger/decisions/(DEC-\d{8}-[0-9a-f]{3,6})\.yaml$"),
    "correction": re.compile(r"^ledger/corrections/(CORR-\d{8}-[0-9a-f]{3,6})\.yaml$"),
    "handoff": re.compile(r"^ledger/handoffs/(TASK-\d{8}-[0-9a-f]{3,6})\.yaml$"),
    "experiment": re.compile(r"^experiments/(EXP-[A-Z0-9]+-[0-9a-f]{3,6})/"),
    "knowledge": re.compile(r"^knowledge/[a-z-]+/(KN-(?:LIT|TECH|FIND|OPEN)-[0-9a-f]+)\.md$"),
}

# Files that bind EVERY campaign simultaneously. A change here is the one kind of
# merge that every open branch needs to know about regardless of its own area.
CONTRACT_PREFIXES = ("AGENTS.md", "CLAUDE.md", "docs/", "tools/", ".github/",
                     "templates/", "orchestration/")


def run(*args: str) -> str:
    result = subprocess.run(args, cwd=REPO, capture_output=True, text=True)
    return result.stdout


def changed_paths(since: str, until: str) -> list[tuple[str, str]]:
    raw = run("git", "diff", "--name-status", "--no-renames", "-z", since, until)
    fields = [f for f in raw.split("\0") if f]
    out = []
    for i in range(0, len(fields) - 1, 2):
        out.append((fields[i][:1], fields[i + 1]))
    return out


def goal_at(ref: str, goal_id: str) -> dict | None:
    """Load a goal record at `ref`, from either layout."""
    for path in (f"ledger/goals/{goal_id}.yaml", f"ledger/goals/{goal_id}/goal.yaml"):
        blob = subprocess.run(["git", "-C", REPO, "show", f"{ref}:{path}"],
                              capture_output=True, text=True)
        if blob.returncode == 0:
            try:
                doc = yaml.safe_load(blob.stdout)
            except yaml.YAMLError:
                return None
            if isinstance(doc, dict) and isinstance(doc.get("research_goal"), dict):
                return doc["research_goal"]
    return None


def digest(since: str, until: str) -> dict:
    paths = changed_paths(since, until)
    records: dict[str, dict[str, list[str]]] = {}
    goals_touched: set[str] = set()

    for status, path in paths:
        for kind, pattern in RECORD_PATTERNS.items():
            match = pattern.match(path)
            if not match:
                continue
            rec_id = match.group(1)
            bucket = records.setdefault(kind, {"added": [], "modified": [],
                                               "removed": []})
            key = {"A": "added", "D": "removed"}.get(status, "modified")
            if rec_id not in bucket[key]:
                bucket[key].append(rec_id)
            if kind == "goal":
                goals_touched.add(rec_id)
            break

    # The high-value part: what actually MOVED on each goal.
    transitions = []
    for goal_id in sorted(goals_touched):
        before, after = goal_at(since, goal_id), goal_at(until, goal_id)
        if after is None:
            continue
        entry: dict = {"goal_id": goal_id}
        if before is None:
            # The goal did not exist at `since`. Reporting "status None -> active"
            # and "next_action changed" for a record that is simply NEW is noise
            # that buries the real transitions underneath it.
            entry["new_goal"] = True
            entry["status"] = after.get("status")
            transitions.append(entry)
            continue
        if before.get("status") != after.get("status"):
            entry["status"] = {"from": before.get("status"),
                               "to": after.get("status")}
        b_action = str(before.get("next_action") or "").strip()
        a_action = str(after.get("next_action") or "").strip()
        if b_action != a_action:
            entry["next_action_changed"] = True
            entry["next_action"] = a_action[:400]
        if before.get("latest_verified_commit") != after.get("latest_verified_commit"):
            entry["latest_verified_commit"] = {
                "from": before.get("latest_verified_commit"),
                "to": after.get("latest_verified_commit")}
        if len(entry) > 1:
            transitions.append(entry)

    contract = sorted({p for _s, p in paths
                       if p.startswith(CONTRACT_PREFIXES)})

    # A record whose path set was rewritten (a shard migration, say) shows up as
    # added AND removed AND modified. Report the strongest single classification
    # so a reader is not told a record was three things at once.
    for bucket in records.values():
        added = set(bucket["added"])
        bucket["modified"] = [r for r in bucket["modified"] if r not in added]
        bucket["removed"] = [r for r in bucket["removed"]
                             if r not in added and r not in set(bucket["modified"])]

    return {
        "records": {k: {kk: sorted(vv) for kk, vv in v.items() if vv}
                    for k, v in sorted(records.items())},
        "goal_transitions": transitions,
        "contract_changed": contract,
        "contract_changed_note": (
            "These bind every campaign at once. A branch that has not merged this "
            "is operating under superseded rules." if contract else None),
        "paths_changed": len(paths),
    }


def commit_meta(sha: str) -> dict:
    fmt = "%H%x00%P%x00%an%x00%aI%x00%s"
    raw = run("git", "show", "-s", f"--format={fmt}", sha).strip("\n")
    parts = raw.split("\0")
    if len(parts) < 5:
        return {"sha": sha}
    full, parents, author, when, subject = parts[:5]
    pr = re.search(r"#(\d+)", subject)
    branch = re.search(r"from\s+\S+/(\S+)", subject)
    return {
        "sha": full,
        "parents": parents.split(),
        "is_merge_commit": len(parents.split()) > 1,
        "author": author,
        "merged_at": when,
        "subject": subject,
        "pull_request": int(pr.group(1)) if pr else None,
        "merged_branch": branch.group(1) if branch else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--commit", help="digest this commit against its first parent")
    ap.add_argument("--since")
    ap.add_argument("--until", default="HEAD")
    ap.add_argument("--out", help="write YAML here instead of stdout")
    ap.add_argument("--json", action="store_true", help="emit JSON on stdout")
    args = ap.parse_args()

    if args.commit:
        meta = commit_meta(args.commit)
        parents = meta.get("parents") or []
        if not parents:
            print(f"{args.commit} has no parent to diff against", file=sys.stderr)
            return 2
        since, until = parents[0], meta["sha"]
    elif args.since:
        meta = {"range": f"{args.since}..{args.until}"}
        since, until = args.since, args.until
    else:
        ap.error("pass --commit or --since")
        return 2

    body = {"merge_event": {**meta, **digest(since, until)}}

    if args.json:
        print(json.dumps(body, indent=1, sort_keys=True))
        return 0
    text = yaml.dump(body, sort_keys=False, default_flow_style=False,
                     allow_unicode=True, width=88)
    header = (
        "# WRITE-ONCE merge event. One file per merge so concurrent merges never\n"
        "# touch the same bytes. Generated by tools/merge_digest.py; do not edit.\n"
        "#\n"
        "# This is a FEED, not a notification: agent sessions are ephemeral and\n"
        "# most of the sessions that care about this merge did not exist when it\n"
        "# landed. Read it on wake to see what moved under you.\n"
    )
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(header + text)
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(header + text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
