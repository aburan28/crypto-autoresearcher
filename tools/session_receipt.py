#!/usr/bin/env python3
"""Write one write-once receipt per interactive skill session.

The program measures its research outputs in detail and its own cost not at
all: no record says how many sessions a validated outcome took, which skill
they ran, or what they read. `docs/token-efficiency.md` asks for "tokens per
validated outcome" and has never had a denominator. This is the denominator.

Every skill ends with

    python3 tools/session_receipt.py --skill design-experiment --role coordinator \
        --outcome approved --created EXP-FROB-123456,H-FROB-000001 [--files-read 41]

which appends one YAML file under coordination/sessions/receipts/<YYYYMMDD>/.
A receipt is a *claim about process*, not evidence: it records the skill, role,
runtime, model, start and end, the records created by kind, how many files
were read, the outcome, and provider usage **only where the runtime exposes
it** -- `--usage-json` from the runtime's own counters, otherwise `null`,
never an estimate (core rule 5). Write-once like the bus: O_EXCL, never
edited, a correction is a new receipt with `supersedes`.

`start` prints an ISO timestamp for `SESSION_RECEIPT_STARTED`, so the end
receipt can carry a real start. `summary` aggregates receipts by skill and
outcome, which is the first thing `tune-skill` and the track-record review can
read instead of inferring sessions from record dates.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

try:  # libyaml, with the pure loader's errors (orchestration/fast_yaml.py)
    import fast_yaml
except ImportError:  # imported as tools.<name>, the repository root importable
    from orchestration import fast_yaml

REPO = Path(__file__).resolve().parents[1]
RECEIPTS_DIR = Path("coordination") / "sessions" / "receipts"
SCHEMA = "crypto.autoresearch.session_receipt.v1"
KINDS = ("GOAL", "RQ", "IDEA", "H", "EXP", "RUN", "EV", "DEC", "TASK", "KN", "CORR", "BATCH")
OUTCOMES = (
    "approved", "review_required", "refused_capacity", "proposed", "ran", "nothing_executable",
    "reviewed", "archived", "published", "impeded", "no_change", "other",
)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def detect_runtime(env: dict[str, str] | None = None) -> str | None:
    """Name the runtime from its own environment markers; None when unsure.

    Each marker is one the runtime sets itself, so a receipt never guesses: a
    plain shell with none of them records null.
    """
    env = os.environ if env is None else env
    if env.get("AUTORESEARCH_RUNTIME"):
        return env["AUTORESEARCH_RUNTIME"]
    if env.get("CURSOR_AGENT") or env.get("CURSOR_CONVERSATION_ID"):
        return "cursor_cloud" if env.get("CURSOR_WORKLOAD_CGROUP") else "cursor"
    if env.get("CLAUDECODE") or env.get("CLAUDE_CODE_ENTRYPOINT"):
        return "claude_code"
    if env.get("CODEX_SANDBOX") or env.get("CODEX_CLI"):
        return "codex_cli"
    if env.get("OPENCODE"):
        return "opencode"
    return None


def detect_model(env: dict[str, str] | None = None) -> str | None:
    env = os.environ if env is None else env
    for key in ("AUTORESEARCH_RESOLVED_MODEL", "AUTORESEARCH_MODEL", "ANTHROPIC_MODEL", "CURSOR_MODEL"):
        if env.get(key):
            return env[key]
    return None


def _git(repo_root: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(repo_root), *args], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip() or None


def created_by_kind(ids: list[str]) -> dict[str, list[str]]:
    by_kind: dict[str, list[str]] = defaultdict(list)
    for rid in ids:
        rid = rid.strip()
        if not rid:
            continue
        prefix = rid.split("-", 1)[0]
        by_kind[prefix if prefix in KINDS else "other"].append(rid)
    return {k: sorted(v) for k, v in sorted(by_kind.items())}


def receipt(args: argparse.Namespace, *, repo_root: Path, now: datetime | None = None,
            env: dict[str, str] | None = None) -> dict[str, Any]:
    now = now or _now()
    env = os.environ if env is None else env
    started = args.started or env.get("SESSION_RECEIPT_STARTED")
    usage = None
    if args.usage_json:
        usage = json.loads(args.usage_json)
        if not isinstance(usage, dict):
            raise ValueError("--usage-json must be a JSON object of the runtime's own counters")
    ids = [s for s in (args.created or "").split(",") if s.strip()]
    return {
        "schema": SCHEMA,
        "id": f"SR-{now.strftime('%Y%m%d')}-{secrets.token_hex(3)}",
        "recorded_at": now.isoformat(),
        "skill": args.skill,
        "role": args.role,
        "mode": args.mode,
        "runtime": args.runtime or detect_runtime(env),
        "model": args.model or detect_model(env),
        "policy": args.policy or env.get("AUTORESEARCH_POLICY"),
        "started_at": started,
        "ended_at": now.isoformat(),
        "outcome": args.outcome,
        "records_created": created_by_kind(ids),
        "records_created_count": len(ids),
        "files_read": args.files_read,
        "bounced": args.bounced,
        "usage": usage,
        "usage_source": args.usage_source if usage else None,
        "branch": _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD"),
        "commit": _git(repo_root, "rev-parse", "HEAD"),
        "goal_id": args.goal,
        "notes": args.notes,
        "supersedes": args.supersedes,
        "asserts_nothing_about": "the science; this is a process receipt, not evidence",
    }


def write(rec: dict[str, Any], repo_root: Path) -> Path:
    day = rec["recorded_at"][:10].replace("-", "")
    out_dir = repo_root / RECEIPTS_DIR / day
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{rec['id']}.yaml"
    # O_EXCL: write-once, like the bus. A collision on the random token is
    # refused rather than overwritten.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write("# Session receipt: process record, write-once, not evidence.\n")
        fh.write(yaml.safe_dump(rec, sort_keys=False, allow_unicode=True))
    return path


def load_all(repo_root: Path) -> list[dict[str, Any]]:
    root = repo_root / RECEIPTS_DIR
    if not root.is_dir():
        return []
    rows = []
    for path in sorted(root.rglob("SR-*.yaml")):
        try:
            doc = fast_yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if isinstance(doc, dict) and doc.get("schema") == SCHEMA:
            rows.append(doc)
    return rows


def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_skill: dict[str, Counter] = defaultdict(Counter)
    created: Counter = Counter()
    bounced: Counter = Counter()
    usage_known = 0
    for r in rows:
        by_skill[r.get("skill") or "?"][r.get("outcome") or "?"] += 1
        created[r.get("skill") or "?"] += int(r.get("records_created_count") or 0)
        bounced[r.get("skill") or "?"] += int(r.get("bounced") or 0)
        if r.get("usage"):
            usage_known += 1
    return {
        "receipts": len(rows),
        "usage_known": usage_known,
        "by_skill": {k: dict(v) for k, v in sorted(by_skill.items())},
        "records_created_by_skill": dict(created),
        "bounced_by_skill": {k: v for k, v in bounced.items() if v},
    }


def render_summary(s: dict[str, Any]) -> str:
    if not s["receipts"]:
        return "session receipts: none yet (every skill ends with tools/session_receipt.py)"
    lines = [f"session receipts: {s['receipts']}, provider usage known for {s['usage_known']}"]
    for skill, outcomes in s["by_skill"].items():
        total = sum(outcomes.values())
        parts = ", ".join(f"{o} {n}" for o, n in sorted(outcomes.items(), key=lambda kv: -kv[1]))
        line = f"  {skill}: {total} ({parts}); records created {s['records_created_by_skill'].get(skill, 0)}"
        if s.get("bounced_by_skill", {}).get(skill):
            line += f"; bounced {s['bounced_by_skill'][skill]}"
        lines.append(line)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("start", help="print an ISO timestamp for SESSION_RECEIPT_STARTED")
    sub.add_parser("summary", help="aggregate receipts by skill and outcome")
    w = sub.add_parser("write", help="write one receipt (default when no subcommand)")
    for p in (parser, w):
        p.add_argument("--skill", help="skill that ran (run, coordinate, design-experiment, ...)")
        p.add_argument("--role", help="role played (coordinator, executor, validator, ...)")
        p.add_argument("--mode", help="skill mode where the skill has one (status, goal, portfolio)")
        p.add_argument("--outcome", choices=OUTCOMES)
        p.add_argument("--created", help="comma-separated record ids this session created")
        p.add_argument("--files-read", type=int, help="count of files read, if the session counted")
        p.add_argument("--bounced", type=int,
                       help="records sent back to a subagent for schema completeness before filing "
                            "(propose-ideas step 4); the tune-skill signal that used to leave no trace")
        p.add_argument("--started", help="ISO start time; defaults to $SESSION_RECEIPT_STARTED")
        p.add_argument("--runtime", help="override the detected runtime")
        p.add_argument("--model", help="resolved model id, if the runtime exposes it")
        p.add_argument("--policy", help="requested inference policy")
        p.add_argument("--usage-json", help="runtime's own usage counters as JSON; never an estimate")
        p.add_argument("--usage-source", help="where --usage-json came from (e.g. cursor run-info)")
        p.add_argument("--goal", help="GOAL-* the session worked, if one")
        p.add_argument("--notes", help="one line; anything longer belongs in a record")
        p.add_argument("--supersedes", help="id of the receipt this one corrects")
        p.add_argument("--json", action="store_true", help="print the receipt as JSON too")
    args = parser.parse_args(argv)
    if args.cmd == "start":
        print(_now().isoformat())
        return 0
    if args.cmd == "summary":
        print(render_summary(summary(load_all(args.repo_root))))
        return 0
    if not args.skill or not args.outcome:
        parser.error("--skill and --outcome are required to write a receipt")
    try:
        rec = receipt(args, repo_root=args.repo_root)
    except (ValueError, json.JSONDecodeError) as error:
        print(f"session_receipt: {error}", file=sys.stderr)
        return 2
    path = write(rec, args.repo_root)
    rel = path.relative_to(args.repo_root) if path.is_relative_to(args.repo_root) else path
    print(f"receipt {rec['id']} -> {rel}")
    if args.json:
        print(json.dumps(rec, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
