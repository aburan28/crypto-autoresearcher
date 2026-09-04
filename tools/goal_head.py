#!/usr/bin/env python3
"""Project a goal record down to the fields an agent needs, and audit head bloat.

WHY THIS EXISTS
---------------
A goal record is the one ledger file every campaign reads to answer "where is
this goal and what do I do next". Nine small fields answer that question --
`launch-research-harness` step 2 names them exactly:

    research_goal.{id,status,title,current_batch_id,dispatch_queue_path,
                   next_action,campaign_budget,completion_criteria,
                   pause_conditions}

But the records are append-only in practice: every batch, amendment, and
terminal note is written as a NEW top-level key on the goal head. Across the
102 goal records in this repository that is 1,138 distinct ad-hoc key names
and 83% of all goal-record bytes. `GOAL-ECDLP-001` reached 651 top-level keys
and 972 KB, so reading it to recover nine fields costs ~243,000 tokens -- more
than a session's working context, to learn one batch id and one next action.
Listing all goal heads the way step 2 describes costs ~904,000 tokens.

So agents improvise: grep, head -n, partial reads -- differently every session,
each one re-deriving what the last one already knew. That is the same failure
`tools/goal_portfolio_health.py` was written for ("a session would ... spend
its whole budget discovering ... then repeat that discovery from scratch"),
and this tool is the same remedy applied to the goal head itself: read the
record HERE, where bytes are free, and hand the agent only the projection.

    goal_head.py list                  ~2k tokens for all 102 goals
    goal_head.py show GOAL-ECDLP-001   ~0.6k tokens instead of ~243k

TRUNCATION IS ALWAYS DISCLOSED. Every value this tool shortens is marked with
an explicit `[+N more ...]` / `[truncated ...]` note naming the command that
returns the full value. An agent must never mistake a projection for the whole
record; a silent truncation would be a fabricated read.

This tool is READ-ONLY. It never writes to `ledger/` or `coordination/`, and
it never edits a goal record -- goal records are immutable per AGENTS.md, and
corrections supersede rather than overwrite.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path
from typing import Any

import yaml

# The fields that answer "where is this goal and what happens next". The first
# nine are exactly those `launch-research-harness` step 2 names; the rest are
# what a resuming coordinator needs to bind to committed state and to see
# which lanes are already open (CLAUDE.md, "Concurrency: many agents, many
# worktrees").
RESUME_FIELDS = [
    "id",
    "status",
    "title",
    "current_batch_id",
    "dispatch_queue_path",
    "next_action",
    "campaign_budget",
    "completion_criteria",
    "pause_conditions",
    "open_batches",
    "latest_verified_commit",
    "question_ids",
    "active_hypothesis_ids",
    "owner",
    "updated_at",
]

# Fields declared by `templates/research-records.md`. Anything else on a goal
# head is ad-hoc narrative appended by some past session; `audit` measures it.
TEMPLATE_FIELDS = set(RESUME_FIELDS) | {
    "objective",
    "runtime",
    "completion_quorum",
    "created_at",
}

# Fields whose ENTRIES are never dropped, only their prose clipped. A goal
# closes on a declared completion criterion being met, so a projection that
# silently showed 2 of 5 criteria would invite a wrong closure call.
WHOLE_FIELDS = {
    "completion_criteria",
    "pause_conditions",
    "question_ids",
    "active_hypothesis_ids",
    "open_batches",
}

# YAML wraps at 80 columns by default, which splits the "goal_head.py show …"
# pointers this tool emits across lines and makes them un-runnable. The
# pointers are the contract that keeps compaction honest, so never wrap.
WIDTH = 10 ** 6

BRIEF_TEXT_CHARS = 600
LIST_TEXT_CHARS = 140
DEFAULT_TAIL = 2


def goal_paths(repo_root: Path) -> list[Path]:
    """Every goal record, in both layouts.

    Goals exist as a flat `ledger/goals/GOAL-X.yaml` or as a sharded
    `ledger/goals/GOAL-X/goal.yaml` (tools/shard_goal.py). Both must be
    scanned or the sharded goals are invisible -- the same requirement
    `goal_portfolio_health.discover_active_goals` documents.
    """
    paths = sorted(glob.glob(str(repo_root / "ledger" / "goals" / "GOAL-*.yaml")))
    paths += sorted(glob.glob(str(repo_root / "ledger" / "goals" / "GOAL-*" / "goal.yaml")))
    return [Path(p) for p in paths]


def load_goal(path: Path) -> dict[str, Any]:
    """Read one goal head. Unparseable records are reported, never raised.

    A record that fails to parse is a real integrity signal (that is what
    `.github/workflows/main-health.yml` sweeps for), so it is surfaced as a
    row rather than crashing a listing that other goals depend on.
    """
    # For the sharded layout every file is named "goal.yaml"; the id is the
    # directory name, not the file stem.
    fallback_id = path.parent.name if path.name == "goal.yaml" else path.stem
    try:
        doc = yaml.safe_load(path.read_text())
    except Exception as exc:  # noqa: BLE001 - reported per goal, not raised
        return {"id": fallback_id, "path": str(path), "status": "unparseable",
                "error": str(exc), "_record": {}}
    record = doc.get("research_goal", doc) if isinstance(doc, dict) else {}
    if not isinstance(record, dict):
        return {"id": fallback_id, "path": str(path), "status": "unparseable",
                "error": "research_goal is not a mapping", "_record": {}}
    return {"id": record.get("id", fallback_id), "path": str(path),
            "status": record.get("status"), "_record": record}


def checkpoint_ids(path: Path) -> list[str]:
    """Checkpoint shard names for a sharded goal -- names only, never content.

    The shards are write-once and often large; a resuming agent needs to know
    they exist and which is latest, not to read them all.
    """
    if path.name != "goal.yaml":
        return []
    return sorted(p.stem for p in (path.parent / "checkpoints").glob("*.yaml"))


def _clip(text: str, limit: int, hint: str) -> str:
    """Shorten free text, always leaving a visible, actionable marker."""
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()} … [truncated, {len(text)} chars total; {hint}]"


def _compact(value: Any, *, limit: int, tail: int, hint: str) -> Any:
    """Recursively shorten a value: clip long strings, tail large containers.

    Shape-agnostic on purpose. The append-logs on these records come in every
    shape -- `campaign_budget` is a 29-key MAPPING on GOAL-ECDLP-001 while
    `budget_amendments` is a 28-item list -- and a future session will invent a
    third. Compacting by structure rather than by a list of known-bad field
    names keeps this working without another edit here; an earlier list-only
    version silently missed the mapping and left 9k tokens in the projection.

    Every reduction leaves a disclosed marker naming `hint`, so a projection
    can never be mistaken for the whole value.
    """
    if isinstance(value, str):
        return _clip(value, limit, hint)
    if isinstance(value, list):
        if len(value) > tail:
            hidden = len(value) - tail
            kept = [_compact(v, limit=limit, tail=tail, hint=hint) for v in value[-tail:]]
            return [f"[+{hidden} earlier entries not shown; {hint}]"] + kept
        return [_compact(v, limit=limit, tail=tail, hint=hint) for v in value]
    if isinstance(value, dict):
        items = list(value.items())
        out: dict[str, Any] = {}
        if len(items) > tail:
            out["_omitted"] = f"+{len(items) - tail} earlier keys not shown; {hint}"
            items = items[-tail:]
        for k, v in items:
            out[str(k)] = _compact(v, limit=limit, tail=tail, hint=hint)
        return out
    return value


def project(entry: dict[str, Any], *, full: bool, tail: int,
            text_chars: int) -> dict[str, Any]:
    """Reduce one goal record to the resume projection.

    `full` keeps every resume field whole; otherwise long free text is clipped
    and append-log lists are shown tail-first. Both modes drop the ad-hoc keys
    entirely -- `audit` is how you see those, and `--raw` is how you read one.
    """
    record = entry["_record"]
    goal_id = entry["id"]
    out: dict[str, Any] = {}
    if entry["status"] == "unparseable":
        return {"id": goal_id, "status": "unparseable", "error": entry.get("error"),
                "path": entry["path"]}

    for field in RESUME_FIELDS:
        if field not in record:
            continue
        value = record[field]
        if full:
            out[field] = value
            continue
        hint = f"goal_head.py show {goal_id} --field {field}"
        # Criteria, pause conditions and the id/lane lists are never thinned:
        # a closure judgement rests on the FULL criterion set (CLAUDE.md rule
        # 8), and an agent that saw two of five criteria would misjudge it.
        # Their prose is still clipped; only entries are protected.
        entry_tail = 10 ** 9 if field in WHOLE_FIELDS else tail
        out[field] = _compact(value, limit=text_chars, tail=entry_tail, hint=hint)

    extras = [k for k in record if k not in TEMPLATE_FIELDS]
    if extras:
        # Never hide that the record carries more than the projection: name the
        # count and how to see it, so a projection is never mistaken for whole.
        out["_ad_hoc_keys_not_shown"] = (
            f"{len(extras)} undeclared top-level keys on this record "
            f"(goal_head.py audit {goal_id})"
        )
    shards = checkpoint_ids(Path(entry["path"]))
    if shards:
        out["_checkpoint_shards"] = (
            f"{len(shards)} shard(s), latest {shards[-1]} "
            f"(ledger/goals/{goal_id}/checkpoints/)"
        )
    return out


def audit_rows(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per-goal head cost: declared vs ad-hoc bytes, and the worst keys."""
    rows = []
    for entry in entries:
        record = entry["_record"]
        declared = adhoc = 0
        keys: list[tuple[int, str]] = []
        for key, value in record.items():
            size = len(yaml.safe_dump({key: value}, default_flow_style=False,
                                      allow_unicode=True))
            if key in TEMPLATE_FIELDS:
                declared += size
            else:
                adhoc += size
                keys.append((size, key))
        keys.sort(reverse=True)
        rows.append({
            "id": entry["id"], "path": entry["path"], "keys": len(record),
            "declared_bytes": declared, "adhoc_bytes": adhoc,
            "total_bytes": declared + adhoc,
            "top_adhoc_keys": [{"key": k, "bytes": b} for b, k in keys[:5]],
        })
    rows.sort(key=lambda r: -r["adhoc_bytes"])
    return rows


def cmd_list(args: argparse.Namespace, entries: list[dict[str, Any]]) -> int:
    rows = []
    for entry in entries:
        record = entry["_record"]
        status = entry["status"] or "unset"
        if args.status and status not in args.status:
            continue
        rows.append({
            "id": entry["id"],
            "status": status,
            "current_batch_id": record.get("current_batch_id"),
            "dispatch_queue_path": record.get("dispatch_queue_path"),
            "next_action": _clip(record.get("next_action") or "",
                                 LIST_TEXT_CHARS,
                                 f"goal_head.py show {entry['id']}") or None,
        })
    if args.json:
        print(json.dumps({"goals": rows}, indent=2))
        return 0
    if not rows:
        print("# No goal records matched.")
        return 0
    print(f"# Goal heads ({len(rows)} of {len(entries)})"
          + (f", status in {sorted(args.status)}" if args.status else ""))
    print("# Projection only -- `goal_head.py show <GOAL>` for a goal's full head fields.\n")
    for row in rows:
        print(f"{row['id']}  [{row['status']}]"
              + (f"  batch={row['current_batch_id']}" if row["current_batch_id"] else ""))
        if row["next_action"] and not args.brief:
            print(f"    next: {row['next_action']}")
    return 0


def cmd_show(args: argparse.Namespace, entries: list[dict[str, Any]]) -> int:
    match = [e for e in entries if e["id"] == args.goal]
    if not match:
        print(f"error: no goal record with id {args.goal!r} "
              f"(goal_head.py list)", file=sys.stderr)
        return 2
    entry = match[0]
    record = entry["_record"]

    if args.raw:
        # Escape hatch: the whole record, cost and all. Deliberately explicit
        # so that paying 243k tokens is always a decision, never a default.
        print(Path(entry["path"]).read_text(), end="")
        return 0

    if args.field:
        if args.field not in record:
            declared = sorted(k for k in record if k in TEMPLATE_FIELDS)
            n_adhoc = sum(1 for k in record if k not in TEMPLATE_FIELDS)
            print(f"error: field {args.field!r} not on {args.goal}.\n"
                  f"  declared fields present: {', '.join(declared)}\n"
                  f"  plus {n_adhoc} ad-hoc key(s) — `goal_head.py audit "
                  f"{args.goal}` names the largest.", file=sys.stderr)
            return 2
        payload = {args.field: record[args.field]}
        print(json.dumps(payload, indent=2, default=str) if args.json
              else yaml.safe_dump(payload, default_flow_style=False,
                                  allow_unicode=True, sort_keys=False,
                                  width=WIDTH), end="")
        return 0

    projection = project(entry, full=args.full, tail=args.tail,
                         text_chars=BRIEF_TEXT_CHARS)
    if args.json:
        print(json.dumps(projection, indent=2, default=str))
        return 0
    print(f"# {entry['id']} — head projection from {entry['path']}")
    print("# Resume fields only; ad-hoc keys and checkpoint bodies are not shown.\n")
    print(yaml.safe_dump(projection, default_flow_style=False, allow_unicode=True,
                         sort_keys=False, width=WIDTH), end="")
    return 0


def cmd_audit(args: argparse.Namespace, entries: list[dict[str, Any]]) -> int:
    if args.goal:
        entries = [e for e in entries if e["id"] == args.goal]
        if not entries:
            print(f"error: no goal record with id {args.goal!r}", file=sys.stderr)
            return 2
    rows = audit_rows(entries)
    total = sum(r["total_bytes"] for r in rows)
    adhoc = sum(r["adhoc_bytes"] for r in rows)
    if args.json:
        print(json.dumps({"total_bytes": total, "adhoc_bytes": adhoc,
                          "goals": rows}, indent=2))
        return 0
    print(f"# Goal head cost audit ({len(rows)} record(s))\n")
    print(f"total head bytes : {total:>12,}  (~{total // 4:,} tokens)")
    if total:
        print(f"  declared fields: {total - adhoc:>12,}  "
              f"(~{(total - adhoc) // 4:,} t)  {100 * (total - adhoc) / total:.1f}%")
        print(f"  ad-hoc appended: {adhoc:>12,}  (~{adhoc // 4:,} t)  "
              f"{100 * adhoc / total:.1f}%")
    print("\n# Ad-hoc keys are undeclared top-level keys on the goal head — narrative")
    print("# appended by past sessions. Every reader of the record pays for them.\n")
    limit = len(rows) if args.goal else args.top
    for row in rows[:limit]:
        if not row["adhoc_bytes"]:
            continue
        print(f"{row['id']}  keys={row['keys']}  "
              f"ad-hoc ~{row['adhoc_bytes'] // 4:,}t / "
              f"declared ~{row['declared_bytes'] // 4:,}t")
        for k in row["top_adhoc_keys"]:
            print(f"    ~{k['bytes'] // 4:>6,}t  {k['key']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Project goal records to the fields agents need (read-only).")
    parser.add_argument("--repo-root", default=".", type=Path,
                        help="repository root (default: cwd)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="one compact line per goal")
    p_list.add_argument("--status", action="append",
                        help="only this status (repeatable), e.g. --status active")
    p_list.add_argument("--brief", action="store_true",
                        help="ids and status only, no next_action prose")

    p_show = sub.add_parser("show", help="one goal's head fields")
    p_show.add_argument("goal")
    p_show.add_argument("--full", action="store_true",
                        help="do not clip text or tail append-logs")
    p_show.add_argument("--field", help="print exactly one field, whole")
    p_show.add_argument("--tail", type=int, default=DEFAULT_TAIL,
                        help=f"append-log entries to show (default {DEFAULT_TAIL})")
    p_show.add_argument("--raw", action="store_true",
                        help="print the entire record — can be >200k tokens")

    p_audit = sub.add_parser("audit", help="head bloat: declared vs ad-hoc bytes")
    p_audit.add_argument("goal", nargs="?")
    p_audit.add_argument("--top", type=int, default=10, help="goals to detail")

    argv = sys.argv[1:] if argv is None else list(argv)
    # Bare `goal_head.py` means `list`. Re-parse with the subcommand injected
    # rather than patching the namespace by hand: hand-setting attributes has
    # to be redone for every option `list` ever gains, and missing one is an
    # AttributeError at runtime instead of a parse error.
    args = parser.parse_args(argv)
    if args.command is None:
        args = parser.parse_args([*argv, "list"])

    entries = [load_goal(p) for p in goal_paths(args.repo_root)]
    if not entries:
        print(f"error: no goal records under {args.repo_root}/ledger/goals/",
              file=sys.stderr)
        return 2
    return {"list": cmd_list, "show": cmd_show, "audit": cmd_audit}[args.command](args, entries)


if __name__ == "__main__":
    raise SystemExit(main())
