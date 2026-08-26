#!/usr/bin/env python3
"""Write-once task claims and goal lanes, so several sessions can work one goal.

Two serialisation points made a `GOAL-*` campaign a one-session affair:

1. A task's ownership lived INSIDE the shared `dispatch_queue.json` (`state:
   running` + an optional `lease`), so claiming a task meant editing the one
   file every other session on the batch also edits.
2. A goal's head (`current_batch_id`, `dispatch_queue_path`, one
   `next_action`) named exactly one open batch, so opening a second batch on
   the same goal meant editing the one file every other session on the goal
   also edits.

Both are the failure mode CLAUDE.md "Concurrency" names: a writer made to
write shared state it had no reason to write. This module moves both facts
into write-once side files with unique names -- the same discipline as
`tools/agent_bus.py` receipts and `tools/shard_goal.py` checkpoints -- so no
two sessions ever touch the same bytes:

    <batch_dir>/claims/<TASK-ID>.<epoch>.claim.json      one per claim
    <batch_dir>/claims/<TASK-ID>.<epoch>.release.json    one per release
    coordination/goals/<GOAL>/lanes/<BATCH>.lane.json    one per open batch
    coordination/goals/<GOAL>/lanes/<BATCH>.closed.json  one per closed batch

A CLAIM says "session X holds TASK-Y's write_scope until T". It is created
with O_EXCL, carries a strictly increasing `epoch` per task (a fencing token:
a late owner can never release a claim a newer owner has taken), and expires
on its own so a crashed session frees its scope without anyone editing a
record. A RELEASE ends a claim early and records the outcome
(`completed | failed | abandoned`). `tools/research_dispatch.py --claims`
overlays these on the queue: a live claim reads as `running` (scope held,
counts toward `max_concurrent`), a completed release of a producer reads as
`completed` for its successors' readiness, and everything else leaves the
queue exactly as written. The queue's own `state` field stays the Coordinator's
record of what actually happened, written once at archive time -- claims are
how sessions avoid stepping on each other BEFORE that record exists.

A LANE says "batch B of goal G is open on branch R, opened by session X under
decision D". Lanes let a goal carry several open batches at once, each on its
own branch and PR, each with a disjoint `write_scope` (its own batch
directory, its own freshly minted ledger IDs, its own write-once checkpoint
shard). The one file every lane would otherwise share, `goal.yaml`, is edited
only inside a lane's own ledger archive and only additively (`open_batches`
entry, checkpoint pointer); `current_batch_id` becomes "the lane most recently
opened", not a lock. `lanes` is the authority on what is open.

Cross-worktree visibility is git. Claims and lanes are committed and pushed on
the claimant's branch (`--publish`), and every reader scans `git log --all`
for files ever added under the claims/ or lanes/ prefix -- one git call, about
a second on a repository with 400+ remote refs -- so a session in another
worktree sees a claim as soon as it has fetched. This is a FEED, not a lock
server: two sessions that claim the same task within one fetch interval will
both succeed locally and discover the collision on the next scan, at which
point the LOWER epoch wins and the other releases as `abandoned`. That window
is the cost of having no shared server; it is seconds wide, and the
alternative (a live lock) would not survive the session that held it.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

CLAIM_SCHEMA = "crypto.autoresearch.task_claim.v1"
RELEASE_SCHEMA = "crypto.autoresearch.task_release.v1"
LANE_SCHEMA = "crypto.autoresearch.goal_lane.v1"
LANE_CLOSE_SCHEMA = "crypto.autoresearch.goal_lane_close.v1"

RELEASE_OUTCOMES = ("completed", "failed", "abandoned")
CLAIMS_DIRNAME = "claims"
LANES_DIRNAME = "lanes"

TASK_ID = re.compile(r"^TASK-\d{8}-[0-9a-f]{6}$")
GOAL_ID = re.compile(r"^GOAL-[A-Z0-9]+-(?:[0-9a-f]{6}|\d{3})$")
BATCH_ID = re.compile(r"^BATCH-(?:[0-9a-f]{6}|\d{3})$")
ADDR = re.compile(r"^[a-z][a-z0-9-]{0,63}$")

CLAIM_NAME = re.compile(r"^(?P<task>TASK-\d{8}-[0-9a-f]{6})\.(?P<epoch>\d+)\.(?P<kind>claim|release)\.json$")
LANE_NAME = re.compile(r"^(?P<batch>BATCH-(?:[0-9a-f]{6}|\d{3}))\.(?P<kind>lane|closed)\.json$")


class LaneError(RuntimeError):
    """An expected, explained refusal."""


# ---------------------------------------------------------------------------
# time and git helpers
# ---------------------------------------------------------------------------

def utcnow() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0)


def fmt(ts: _dt.datetime) -> str:
    return ts.astimezone(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(value: Any, location: str) -> _dt.datetime:
    if not isinstance(value, str) or not value:
        raise LaneError(f"{location} must be an ISO-8601 timestamp")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = _dt.datetime.fromisoformat(text)
    except ValueError as error:
        raise LaneError(f"{location} is not ISO-8601: {value!r}") from error
    if parsed.tzinfo is None:
        raise LaneError(f"{location} must carry a timezone: {value!r}")
    return parsed.astimezone(_dt.timezone.utc)


def _git(args: list[str], cwd: Path) -> tuple[bool, str]:
    proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    return proc.returncode == 0, (proc.stdout if proc.returncode == 0 else proc.stderr).strip()


def repo_root(start: Path) -> Path | None:
    ok, out = _git(["rev-parse", "--show-toplevel"], start if start.is_dir() else start.parent)
    return Path(out) if ok else None


def current_branch(root: Path) -> str | None:
    ok, out = _git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    return out if ok and out != "HEAD" else None


def write_once(path: Path, payload: dict[str, Any]) -> None:
    """O_EXCL create. Two sessions racing on one path in one worktree must not
    both believe they won; the loser gets a loud error, not a silent merge."""
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    try:
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        raise LaneError(f"{path} already exists; claims and lanes are write-once")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(body)


# ---------------------------------------------------------------------------
# discovery: working tree + every git ref
# ---------------------------------------------------------------------------

def _scan_refs(root: Path, prefix: str) -> dict[str, dict[str, Any]]:
    """Every file ever ADDED under `prefix` on any ref, with its content.

    One `git log --all` call; files are write-once so "first commit that added
    it" is the only commit that carries it, and its content there is final.
    """
    ok, out = _git(
        ["log", "--all", "--diff-filter=A", "--format=%H", "--name-only", "--", prefix],
        root,
    )
    if not ok or not out:
        return {}
    found: dict[str, str] = {}
    sha = None
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.fullmatch(r"[0-9a-f]{40}", line):
            sha = line
            continue
        if sha and line.startswith(prefix) and line not in found:
            found[line] = sha
    records: dict[str, dict[str, Any]] = {}
    for rel, commit in found.items():
        ok, body = _git(["show", f"{commit}:{rel}"], root)
        if not ok:
            continue
        try:
            records[rel] = {"record": json.loads(body), "source": f"ref:{commit[:12]}"}
        except json.JSONDecodeError:
            records[rel] = {"record": None, "source": f"ref:{commit[:12]}", "error": "unparseable"}
    return records


def _scan_local(root: Path, prefix: str) -> dict[str, dict[str, Any]]:
    directory = root / prefix
    records: dict[str, dict[str, Any]] = {}
    if not directory.is_dir():
        return records
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.suffix != ".json":
            continue
        rel = f"{prefix}{path.name}"
        try:
            records[rel] = {"record": json.loads(path.read_text(encoding="utf-8")), "source": "worktree"}
        except json.JSONDecodeError:
            records[rel] = {"record": None, "source": "worktree", "error": "unparseable"}
    return records


def discover(root: Path, prefix: str, *, include_refs: bool) -> dict[str, dict[str, Any]]:
    """Working-tree files win over ref copies (they are the same bytes when both
    exist: write-once files are never rewritten)."""
    records = _scan_refs(root, prefix) if include_refs else {}
    records.update(_scan_local(root, prefix))
    return records


# ---------------------------------------------------------------------------
# claims
# ---------------------------------------------------------------------------

def claims_prefix(root: Path, queue_path: Path) -> str:
    rel = queue_path.resolve().parent.relative_to(root.resolve()).as_posix()
    return f"{rel}/{CLAIMS_DIRNAME}/"


def load_claims(
    root: Path, queue_path: Path, *, include_refs: bool = True
) -> dict[str, list[dict[str, Any]]]:
    """task_id -> list of {epoch, claim, release, sources}, ascending epoch."""
    prefix = claims_prefix(root, queue_path)
    by_task: dict[str, dict[int, dict[str, Any]]] = {}
    for rel, entry in discover(root, prefix, include_refs=include_refs).items():
        match = CLAIM_NAME.match(os.path.basename(rel))
        if not match or entry.get("record") is None:
            continue
        task_id, epoch, kind = match["task"], int(match["epoch"]), match["kind"]
        slot = by_task.setdefault(task_id, {}).setdefault(
            epoch, {"epoch": epoch, "claim": None, "release": None, "sources": {}}
        )
        slot[kind] = entry["record"]
        slot["sources"][kind] = entry["source"]
    return {
        task_id: [slots[epoch] for epoch in sorted(slots)]
        for task_id, slots in sorted(by_task.items())
    }


def classify(history: list[dict[str, Any]], now: _dt.datetime) -> dict[str, Any] | None:
    """The claim that currently matters for one task, or None if none ever.

    Highest epoch wins (fencing). Its status is one of:
      live       -- claimed, not released, not expired: scope is HELD
      expired    -- claimed, not released, past expires_at: scope is FREE,
                    but the owner's death is a fact the Coordinator records
      released   -- released with outcome completed|failed|abandoned
    """
    if not history:
        return None
    latest = history[-1]
    claim = latest.get("claim")
    if claim is None:
        # A release without its claim (partial fetch). Treat as free but say so.
        return {"epoch": latest["epoch"], "status": "orphan_release", "owner": None,
                "release": latest.get("release")}
    status = "live"
    if latest.get("release") is not None:
        status = "released"
    elif now >= parse_ts(claim["expires_at"], "claim.expires_at"):
        status = "expired"
    return {
        "epoch": latest["epoch"],
        "status": status,
        "owner": claim["owner"],
        "acquired_at": claim["acquired_at"],
        "expires_at": claim["expires_at"],
        "branch": claim.get("branch"),
        "session": claim.get("session"),
        "release": latest.get("release"),
        "sources": latest.get("sources", {}),
    }


def claim_task(
    root: Path,
    queue_path: Path,
    task_id: str,
    *,
    owner: str,
    ttl_minutes: int,
    session: str | None = None,
    branch: str | None = None,
    worktree: str | None = None,
    include_refs: bool = True,
    now: _dt.datetime | None = None,
    force: bool = False,
) -> Path:
    if not TASK_ID.match(task_id):
        raise LaneError(f"{task_id!r} is not a TASK-YYYYMMDD-<6hex> identifier")
    if not ADDR.match(owner):
        raise LaneError(f"{owner!r} is not a bus-style address (lowercase slug)")
    if ttl_minutes <= 0:
        raise LaneError("--ttl-minutes must be positive")
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    tasks = {task["id"]: task for task in queue.get("tasks", [])}
    if task_id not in tasks:
        raise LaneError(f"{task_id} is not in {queue_path}")
    if tasks[task_id].get("state") != "queued":
        raise LaneError(
            f"{task_id} is {tasks[task_id].get('state')!r} in the queue; only a queued task is claimable"
        )
    now = now or utcnow()
    history = load_claims(root, queue_path, include_refs=include_refs).get(task_id, [])
    current = classify(history, now)
    if current and current["status"] == "live" and not force:
        raise LaneError(
            f"{task_id} is held by {current['owner']} (epoch {current['epoch']}, "
            f"expires {current['expires_at']}, seen via {current['sources'].get('claim')}); "
            "wait for expiry, ask for a release on the bus, or --force with a recorded reason"
        )
    if current and current["status"] == "released" and current["release"].get("outcome") == "completed":
        raise LaneError(
            f"{task_id} was released as completed by {current['owner']} (epoch {current['epoch']}); "
            "a completed task is not re-claimable -- the Coordinator archives it"
        )
    epoch = (history[-1]["epoch"] + 1) if history else 1
    payload = {
        "schema": CLAIM_SCHEMA,
        "task_id": task_id,
        "epoch": epoch,
        "owner": owner,
        "session": session,
        "branch": branch or current_branch(root),
        "worktree": worktree or str(root),
        "acquired_at": fmt(now),
        "expires_at": fmt(now + _dt.timedelta(minutes=ttl_minutes)),
        "write_scope": tasks[task_id].get("write_scope", []),
        "supersedes": (
            {"epoch": current["epoch"], "owner": current["owner"], "status": current["status"]}
            if current else None
        ),
        "forced": bool(force and current and current["status"] == "live"),
    }
    path = root / claims_prefix(root, queue_path) / f"{task_id}.{epoch}.claim.json"
    write_once(path, payload)
    return path


def release_task(
    root: Path,
    queue_path: Path,
    task_id: str,
    *,
    owner: str,
    outcome: str,
    note: str | None = None,
    artifact_sha256: dict[str, str] | None = None,
    include_refs: bool = True,
    now: _dt.datetime | None = None,
) -> Path:
    if outcome not in RELEASE_OUTCOMES:
        raise LaneError(f"outcome must be one of {RELEASE_OUTCOMES}")
    now = now or utcnow()
    history = load_claims(root, queue_path, include_refs=include_refs).get(task_id, [])
    current = classify(history, now)
    if not current or current["status"] == "orphan_release":
        raise LaneError(f"{task_id} has no claim to release")
    if current["status"] == "released":
        raise LaneError(
            f"{task_id} epoch {current['epoch']} is already released "
            f"({current['release'].get('outcome')})"
        )
    if current["owner"] != owner:
        raise LaneError(
            f"{task_id} epoch {current['epoch']} is owned by {current['owner']}, not {owner}; "
            "only the owner releases (fencing). If the owner is gone, let the claim expire."
        )
    payload = {
        "schema": RELEASE_SCHEMA,
        "task_id": task_id,
        "epoch": current["epoch"],
        "owner": owner,
        "outcome": outcome,
        "released_at": fmt(now),
        "was_expired": current["status"] == "expired",
        "note": note,
        "artifact_sha256": artifact_sha256 or {},
    }
    path = root / claims_prefix(root, queue_path) / f"{task_id}.{current['epoch']}.release.json"
    write_once(path, payload)
    return path


def claim_summary(
    root: Path, queue_path: Path, *, include_refs: bool = True, now: _dt.datetime | None = None
) -> dict[str, dict[str, Any]]:
    now = now or utcnow()
    return {
        task_id: summary
        for task_id, history in load_claims(root, queue_path, include_refs=include_refs).items()
        if (summary := classify(history, now)) is not None
    }


# ---------------------------------------------------------------------------
# lanes
# ---------------------------------------------------------------------------

def lanes_prefix(goal_id: str) -> str:
    return f"coordination/goals/{goal_id}/{LANES_DIRNAME}/"


def load_lanes(root: Path, goal_id: str, *, include_refs: bool = True) -> dict[str, dict[str, Any]]:
    if not GOAL_ID.match(goal_id):
        raise LaneError(f"{goal_id!r} is not a GOAL identifier")
    lanes: dict[str, dict[str, Any]] = {}
    for rel, entry in discover(root, lanes_prefix(goal_id), include_refs=include_refs).items():
        match = LANE_NAME.match(os.path.basename(rel))
        if not match or entry.get("record") is None:
            continue
        slot = lanes.setdefault(match["batch"], {"batch_id": match["batch"], "lane": None, "closed": None, "sources": {}})
        slot[match["kind"] if match["kind"] == "lane" else "closed"] = entry["record"]
        slot["sources"][match["kind"]] = entry["source"]
    for slot in lanes.values():
        slot["status"] = "closed" if slot["closed"] else ("open" if slot["lane"] else "orphan_close")
    return dict(sorted(lanes.items()))


def open_lane(
    root: Path,
    goal_id: str,
    batch_id: str,
    *,
    queue_path: str,
    owner: str,
    decision_id: str | None,
    objective: str,
    branch: str | None = None,
    session: str | None = None,
    include_refs: bool = True,
    now: _dt.datetime | None = None,
) -> Path:
    if not BATCH_ID.match(batch_id):
        raise LaneError(f"{batch_id!r} is not a BATCH identifier")
    if not ADDR.match(owner):
        raise LaneError(f"{owner!r} is not a bus-style address")
    existing = load_lanes(root, goal_id, include_refs=include_refs)
    if batch_id in existing:
        raise LaneError(f"{batch_id} already has a lane record ({existing[batch_id]['status']})")
    queue_rel = queue_path.strip("/")
    expected_dir = f"coordination/goals/{goal_id}/batches/{batch_id}/"
    if not queue_rel.startswith(expected_dir):
        raise LaneError(f"queue path must live under {expected_dir}; got {queue_rel}")
    open_lanes = {bid: lane for bid, lane in existing.items() if lane["status"] == "open"}
    payload = {
        "schema": LANE_SCHEMA,
        "goal_id": goal_id,
        "batch_id": batch_id,
        "dispatch_queue_path": queue_rel,
        "write_scope": [expected_dir],
        "opened_by": owner,
        "session": session,
        "branch": branch or current_branch(root),
        "opened_at": fmt(now or utcnow()),
        "opening_decision_id": decision_id,
        "objective": objective,
        "concurrent_open_lanes_at_open": sorted(open_lanes),
        "goal_head_policy": (
            "This lane edits ledger/goals/<GOAL>/goal.yaml only inside its own ledger "
            "archive and only additively (open_batches entry, checkpoint pointer, its own "
            "next_action line); it never rewrites another lane's entries, and it writes its "
            "checkpoint as a write-once shard under ledger/goals/<GOAL>/checkpoints/."
        ),
    }
    path = root / lanes_prefix(goal_id) / f"{batch_id}.lane.json"
    write_once(path, payload)
    return path


def close_lane(
    root: Path,
    goal_id: str,
    batch_id: str,
    *,
    owner: str,
    outcome: str,
    decision_id: str | None,
    ledger_commit: str | None,
    include_refs: bool = True,
    now: _dt.datetime | None = None,
) -> Path:
    existing = load_lanes(root, goal_id, include_refs=include_refs)
    lane = existing.get(batch_id)
    if lane is None or lane["lane"] is None:
        raise LaneError(f"{batch_id} has no open lane record under {goal_id}")
    if lane["status"] == "closed":
        raise LaneError(f"{batch_id} lane is already closed")
    payload = {
        "schema": LANE_CLOSE_SCHEMA,
        "goal_id": goal_id,
        "batch_id": batch_id,
        "closed_by": owner,
        "closed_at": fmt(now or utcnow()),
        "outcome": outcome,
        "closing_decision_id": decision_id,
        "ledger_commit": ledger_commit,
        "opened_by": lane["lane"].get("opened_by"),
    }
    path = root / lanes_prefix(goal_id) / f"{batch_id}.closed.json"
    write_once(path, payload)
    return path


# ---------------------------------------------------------------------------
# publish
# ---------------------------------------------------------------------------

def publish(root: Path, paths: Iterable[Path], message: str, *, push: bool) -> str:
    """Commit the write-once files just created and, optionally, push the
    current branch. Nothing else is staged: a claim commit carries a claim."""
    rels = [str(Path(p).resolve().relative_to(root.resolve())) for p in paths]
    ok, out = _git(["add", "--", *rels], root)
    if not ok:
        raise LaneError(f"git add failed: {out}")
    ok, out = _git(["commit", "-q", "-m", message, "--", *rels], root)
    if not ok:
        raise LaneError(f"git commit failed: {out}")
    ok, sha = _git(["rev-parse", "--short", "HEAD"], root)
    if push:
        branch = current_branch(root)
        if branch is None:
            raise LaneError("detached HEAD: cannot push a claim; check out a branch first")
        ok, out = _git(["push", "-u", "origin", branch], root)
        if not ok:
            raise LaneError(f"git push failed: {out}")
    return sha


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _root_for(path: Path) -> Path:
    root = repo_root(path)
    if root is None:
        raise LaneError(f"{path} is not inside a git repository")
    return root


def cmd_claim(args: argparse.Namespace) -> int:
    queue = Path(args.queue).resolve()
    root = _root_for(queue)
    path = claim_task(
        root, queue, args.task, owner=args.as_addr, ttl_minutes=args.ttl_minutes,
        session=args.session, branch=args.branch, worktree=args.worktree,
        include_refs=not args.local_only, force=args.force,
    )
    print(f"claimed {args.task} -> {path.relative_to(root)}")
    if args.publish:
        sha = publish(root, [path], f"claim({args.task}): {args.as_addr} holds write_scope", push=not args.no_push)
        print(f"published {sha}{'' if args.no_push else ' and pushed'}")
    return 0


def cmd_release(args: argparse.Namespace) -> int:
    queue = Path(args.queue).resolve()
    root = _root_for(queue)
    hashes = {}
    for item in args.artifact or []:
        rel, _, digest = item.partition("=")
        hashes[rel] = digest
    path = release_task(
        root, queue, args.task, owner=args.as_addr, outcome=args.outcome, note=args.note,
        artifact_sha256=hashes, include_refs=not args.local_only,
    )
    print(f"released {args.task} as {args.outcome} -> {path.relative_to(root)}")
    if args.publish:
        sha = publish(root, [path], f"release({args.task}): {args.outcome} by {args.as_addr}", push=not args.no_push)
        print(f"published {sha}{'' if args.no_push else ' and pushed'}")
    return 0


def cmd_claims(args: argparse.Namespace) -> int:
    queue = Path(args.queue).resolve()
    root = _root_for(queue)
    summary = claim_summary(root, queue, include_refs=not args.local_only)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    if not summary:
        print("no claims")
    for task_id, item in summary.items():
        extra = f" -> {item['release']['outcome']}" if item.get("release") else ""
        print(f"{task_id}  {item['status']:<8} epoch {item['epoch']}  owner={item.get('owner')}  "
              f"expires={item.get('expires_at')}{extra}")
    return 0


def cmd_open_lane(args: argparse.Namespace) -> int:
    root = _root_for(Path.cwd())
    path = open_lane(
        root, args.goal, args.batch, queue_path=args.queue, owner=args.as_addr,
        decision_id=args.decision, objective=args.objective, branch=args.branch,
        session=args.session, include_refs=not args.local_only,
    )
    print(f"opened lane {args.batch} on {args.goal} -> {path.relative_to(root)}")
    if args.publish:
        sha = publish(root, [path], f"lane({args.goal}): open {args.batch} by {args.as_addr}", push=not args.no_push)
        print(f"published {sha}{'' if args.no_push else ' and pushed'}")
    return 0


def cmd_close_lane(args: argparse.Namespace) -> int:
    root = _root_for(Path.cwd())
    path = close_lane(
        root, args.goal, args.batch, owner=args.as_addr, outcome=args.outcome,
        decision_id=args.decision, ledger_commit=args.ledger_commit, include_refs=not args.local_only,
    )
    print(f"closed lane {args.batch} on {args.goal} -> {path.relative_to(root)}")
    if args.publish:
        sha = publish(root, [path], f"lane({args.goal}): close {args.batch} ({args.outcome})", push=not args.no_push)
        print(f"published {sha}{'' if args.no_push else ' and pushed'}")
    return 0


def cmd_lanes(args: argparse.Namespace) -> int:
    root = _root_for(Path.cwd())
    lanes = load_lanes(root, args.goal, include_refs=not args.local_only)
    if args.json:
        print(json.dumps(lanes, indent=2, sort_keys=True))
        return 0
    if not lanes:
        print(f"no lanes recorded for {args.goal} (a goal without lane records is worked the "
              "old way: one batch at a time via goal.yaml current_batch_id)")
    for batch_id, lane in lanes.items():
        rec = lane["lane"] or {}
        print(f"{batch_id}  {lane['status']:<6}  branch={rec.get('branch')}  opened_by={rec.get('opened_by')}  "
              f"queue={rec.get('dispatch_queue_path')}")
    return 0


def _common(parser: argparse.ArgumentParser, *, needs_owner: bool) -> None:
    if needs_owner:
        parser.add_argument("--as", dest="as_addr", required=True, help="bus address of this session, e.g. coordinator-endo-2")
    parser.add_argument("--local-only", action="store_true", help="do not scan git refs (working tree only)")
    parser.add_argument("--publish", action="store_true", help="commit the new write-once file on the current branch")
    parser.add_argument("--no-push", action="store_true", help="with --publish: commit but do not push")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("claim", help="hold one queued task's write_scope for a bounded time")
    p.add_argument("queue"); p.add_argument("task")
    p.add_argument("--ttl-minutes", type=int, required=True, help="claim expiry; size to the task's budget")
    p.add_argument("--session"); p.add_argument("--branch"); p.add_argument("--worktree")
    p.add_argument("--force", action="store_true", help="supersede a LIVE claim (recorded as forced)")
    _common(p, needs_owner=True); p.set_defaults(func=cmd_claim)

    p = sub.add_parser("release", help="end your own claim with an outcome")
    p.add_argument("queue"); p.add_argument("task")
    p.add_argument("--outcome", choices=RELEASE_OUTCOMES, required=True)
    p.add_argument("--note")
    p.add_argument("--artifact", action="append", help="path=sha256, repeatable")
    _common(p, needs_owner=True); p.set_defaults(func=cmd_release)

    p = sub.add_parser("claims", help="show every task's current claim status")
    p.add_argument("queue"); p.add_argument("--json", action="store_true")
    _common(p, needs_owner=False); p.set_defaults(func=cmd_claims)

    p = sub.add_parser("open-lane", help="register a new open batch on a goal")
    p.add_argument("goal"); p.add_argument("batch")
    p.add_argument("--queue", required=True, help="repo-relative dispatch_queue path under the batch dir")
    p.add_argument("--decision", help="opening DEC-* id")
    p.add_argument("--objective", required=True)
    p.add_argument("--branch"); p.add_argument("--session")
    _common(p, needs_owner=True); p.set_defaults(func=cmd_open_lane)

    p = sub.add_parser("close-lane", help="record that a lane's ledger archive landed")
    p.add_argument("goal"); p.add_argument("batch")
    p.add_argument("--outcome", required=True, help="e.g. archived, abandoned, superseded")
    p.add_argument("--decision"); p.add_argument("--ledger-commit")
    _common(p, needs_owner=True); p.set_defaults(func=cmd_close_lane)

    p = sub.add_parser("lanes", help="list a goal's lanes across every ref")
    p.add_argument("goal"); p.add_argument("--json", action="store_true")
    _common(p, needs_owner=False); p.set_defaults(func=cmd_lanes)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except LaneError as error:
        print(f"REFUSE: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
