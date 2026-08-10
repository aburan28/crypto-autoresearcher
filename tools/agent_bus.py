#!/usr/bin/env python3
"""A durable, write-once message bus between agent sessions.

WHY THIS EXISTS, AND WHY IT IS NOT A CHAT CHANNEL
-------------------------------------------------
Sessions in this program are ephemeral and mutually invisible. A Coordinator
running in one chat cannot see an Executor running in another: different
container, different worktree, possibly a different runtime entirely. The
runtime's own `SendMessage` reaches a peer only while BOTH sessions are alive
and mutually reachable, which is the minority case here -- most sessions that
need to hear something do not exist when it is said.

So this bus follows the rule the merge feed already established in
`coordination/events/main/`: IT IS A FEED, NOT A NOTIFICATION. A sender writes
a message and stops caring. A receiver reads its inbox when it wakes. Nothing
is delivered, nothing is pushed, and no session blocks on another being up.

Everything is one file per fact, named by a random token:

    coordination/bus/messages/MSG-YYYYMMDD-<6hex>.yaml   write-once
    coordination/bus/receipts/MSG-....--<addr>.yaml      write-once
    coordination/bus/sessions/<addr>.yaml                presence, last-writer

That shape is not incidental. Two agents appending to one shared mailbox file
conflict on every send where there is no semantic conflict at all -- the exact
defect that took `knowledge/INDEX.md` and the dispatch plans out of git. One
file per message, with a name nobody else can draw, merges cleanly by
construction across any number of concurrent worktrees.

READ STATE IS DERIVED, NEVER MUTATED. A message is "unread" for an address
when no receipt file names that pair. Acknowledging writes a new file; it never
edits the message. This is the same immutability rule the ledger runs under,
for the same reason: a corrected or retracted message supersedes, it does not
overwrite.

WHAT THIS IS NOT: bus messages are coordination traffic, not research records.
They are not evidence, they carry no claim tier, and `validate_ledger.py` does
not know about them. A message may REFERENCE ledger IDs (`--ref`), and that is
the intended way to point a peer at real state -- but the state itself always
lives in `ledger/`, `experiments/`, and `knowledge/`, never in an inbox.

USAGE
-----
    python3 tools/agent_bus.py register --as coordinator --role coordinator
    python3 tools/agent_bus.py send --from coordinator --to executor \\
        --subject "run EXP-SMTH-afd6f7" --body "Contract frozen; budget 1h." \\
        --ref EXP-SMTH-afd6f7
    python3 tools/agent_bus.py inbox --as executor
    python3 tools/agent_bus.py read MSG-20260809-a1b2c3
    python3 tools/agent_bus.py reply MSG-20260809-a1b2c3 --from executor \\
        --body "Accepted. RUN records will land under experiments/."
    python3 tools/agent_bus.py ack MSG-20260809-a1b2c3 --as executor

Across containers the bus travels by git like everything else:

    python3 tools/agent_bus.py sync --push        # publish mine, collect theirs
    python3 tools/agent_bus.py watch --as executor --sync   # poll loop
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import random
import re
import subprocess
import sys
import time

import yaml

# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ROOT = os.path.join(REPO, "coordination", "bus")

TOKEN_WIDTH = 6  # hex chars; 16**6 per day-namespace, same as allocate_id.py
MSG_ID = re.compile(r"^MSG-(\d{8})-([0-9a-f]{%d})$" % TOKEN_WIDTH)

# An address is a slug. Deliberately not an email, a URL, or a session UUID:
# sessions are ephemeral and their UUIDs die with them, but the ROLE a session
# is playing outlives it, and that is what a peer actually wants to address.
ADDR = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

# Reserved recipient meaning "every address". Broadcasts are read by anyone who
# asks and acked per-reader, so `all` never hides an unread message from one
# reader behind another reader's ack.
BROADCAST = "all"

PRIORITIES = ("low", "normal", "high")


def _root(args) -> str:
    return os.path.abspath(
        getattr(args, "root", None)
        or os.environ.get("AGENT_BUS_ROOT")
        or DEFAULT_ROOT
    )


def _dir(root: str, name: str) -> str:
    path = os.path.join(root, name)
    os.makedirs(path, exist_ok=True)
    return path


def _show(path: str) -> str:
    """Repo-relative when the bus lives in the repo, absolute when it does not.

    A bus rooted outside the tree renders as ../../../tmp/... under a plain
    relpath, which is unreadable and un-pasteable.
    """
    rel = os.path.relpath(path, REPO)
    return path if rel.startswith(os.pardir) else rel


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d")


# --------------------------------------------------------------------------
# Identifiers
# --------------------------------------------------------------------------

def mint_id(root: str, *, seed: int | None = None, today: str | None = None) -> str:
    """Draw a message id. NO STATE IS SCANNED, which is the point.

    Same reasoning as tools/allocate_id.py: asking "what is the next free
    number" gives every concurrent worktree the same answer, so they mint the
    same id for different records and find out at merge time. A random token
    has no such question to ask. The existence check below is a cheap sanity
    guard against a same-worktree collision, not the allocation strategy.
    """
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    day = today or _today()
    msgs = _dir(root, "messages")
    for _ in range(64):
        token = "".join(rng.choice("0123456789abcdef") for _ in range(TOKEN_WIDTH))
        mid = f"MSG-{day}-{token}"
        if not os.path.exists(os.path.join(msgs, mid + ".yaml")):
            return mid
    raise RuntimeError(
        "could not draw a free message id in 64 attempts; that is so unlikely "
        "it indicates a defect in the search path, not exhaustion"
    )


def _check_addr(addr: str) -> str:
    if not ADDR.match(addr):
        raise SystemExit(
            f"REFUSE: {addr!r} is not a valid address. Use a lowercase slug "
            "such as 'coordinator', 'executor-2', or 'red-team'."
        )
    return addr


def _check_msg_id(mid: str) -> str:
    if not MSG_ID.match(mid):
        raise SystemExit(f"REFUSE: {mid!r} is not a well-formed message id "
                         f"(expected MSG-YYYYMMDD-<{TOKEN_WIDTH} hex>).")
    return mid


# --------------------------------------------------------------------------
# Write-once primitives
# --------------------------------------------------------------------------

def _write_once(path: str, payload: dict, *, header: str) -> None:
    """Create a file that must not already exist.

    O_EXCL rather than a check-then-write: two sessions in the SAME worktree
    racing on the same path is rare but not impossible, and a lost message is
    worse than a loud failure.
    """
    body = header.rstrip("\n") + "\n" + yaml.safe_dump(
        payload, sort_keys=False, allow_unicode=True, width=88)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        raise SystemExit(
            f"REFUSE: {_show(path)} already exists. Bus records "
            "are write-once: supersede with a new message, never overwrite."
        )
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(body)


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


MESSAGE_HEADER = """\
# WRITE-ONCE bus message. One file per message so concurrent senders never
# touch the same bytes. Written by tools/agent_bus.py; do not edit.
#
# This is a FEED, not a notification. Nothing delivered it; a peer reads it
# when that peer next wakes. Read state lives in coordination/bus/receipts/,
# never in this file.
#
# NOT a research record: no claim is evidence because it appeared here. The
# refs below point at the ledger, which is where the state actually lives.
"""

RECEIPT_HEADER = """\
# WRITE-ONCE read receipt. Its existence is the entire payload: it marks one
# (message, reader) pair handled. Written by tools/agent_bus.py; do not edit.
"""

SESSION_HEADER = """\
# Presence record for one bus address. Unlike messages and receipts this file
# is CURRENT-STATE and is rewritten by its own address on each register --
# presence is inherently now, and only one writer ever owns this path, so it
# cannot conflict.
"""


# --------------------------------------------------------------------------
# Reading the store
# --------------------------------------------------------------------------

def _message_paths(root: str) -> list[str]:
    msgs = _dir(root, "messages")
    return sorted(
        os.path.join(msgs, n) for n in os.listdir(msgs)
        if n.endswith(".yaml") and not n.startswith("._")
    )


def load_messages(root: str) -> list[dict]:
    out = []
    for path in _message_paths(root):
        try:
            rec = (_load(path) or {}).get("message")
        except yaml.YAMLError as exc:
            print(f"warning: skipping unparseable {os.path.basename(path)}: {exc}",
                  file=sys.stderr)
            continue
        if isinstance(rec, dict) and rec.get("id"):
            out.append(rec)
    # Wall-clock order, with the id as a stable tiebreak so two messages sent in
    # the same second never swap places between two readers.
    out.sort(key=lambda r: (str(r.get("sent_at") or ""), str(r.get("id"))))
    return out


def _receipt_path(root: str, mid: str, addr: str) -> str:
    return os.path.join(_dir(root, "receipts"), f"{mid}--{addr}.yaml")


def acked_by(root: str, mid: str, addr: str) -> bool:
    return os.path.exists(_receipt_path(root, mid, addr))


def addressed_to(rec: dict, addr: str) -> bool:
    to = rec.get("to") or []
    return addr in to or BROADCAST in to


def inbox_for(root: str, addr: str, *, include_read: bool = False,
              include_own: bool = False) -> list[dict]:
    out = []
    for rec in load_messages(root):
        if not addressed_to(rec, addr):
            continue
        if not include_own and rec.get("from") == addr:
            continue
        if not include_read and acked_by(root, rec["id"], addr):
            continue
        out.append(rec)
    return out


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def cmd_register(args) -> int:
    root = _root(args)
    addr = _check_addr(args.addr)
    path = os.path.join(_dir(root, "sessions"), addr + ".yaml")
    prior = _load(path).get("session", {}) if os.path.exists(path) else {}
    payload = {"session": {
        "address": addr,
        "role": args.role or prior.get("role"),
        "goal": args.goal or prior.get("goal"),
        "note": args.note or prior.get("note"),
        "runtime": args.runtime or prior.get("runtime") or "claude_code",
        "branch": _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=root) or None,
        "worktree": _git(["rev-parse", "--show-toplevel"], cwd=root) or None,
        "first_registered_at": prior.get("first_registered_at") or _now(),
        "last_registered_at": _now(),
    }}
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(SESSION_HEADER + yaml.safe_dump(
            payload, sort_keys=False, allow_unicode=True, width=88))
    print(f"registered {addr} at {_show(path)}")
    pending = inbox_for(root, addr)
    print(f"  unread messages for {addr}: {len(pending)}"
          + ("  (run: agent_bus.py inbox --as " + addr + ")" if pending else ""))
    return 0


def cmd_send(args) -> int:
    root = _root(args)
    sender = _check_addr(args.sender)
    recipients = [_check_addr(a.strip()) if a.strip() != BROADCAST else BROADCAST
                  for a in args.to.split(",") if a.strip()]
    if not recipients:
        raise SystemExit("REFUSE: --to named no recipient.")

    body = args.body
    if args.body_file:
        with open(args.body_file, encoding="utf-8") as fh:
            body = fh.read()
    if not body or not body.strip():
        raise SystemExit("REFUSE: an empty message wastes a peer's wake. "
                         "Give --body or --body-file.")

    thread = args.thread
    if thread:
        _check_msg_id(thread)
        if not os.path.exists(os.path.join(root, "messages", thread + ".yaml")):
            raise SystemExit(f"REFUSE: --thread {thread} does not exist.")

    mid = mint_id(root, seed=args.seed)
    payload = {"message": {
        "id": mid,
        "from": sender,
        "to": recipients,
        "subject": args.subject,
        "priority": args.priority,
        "thread": thread or mid,
        "in_reply_to": thread,
        "sent_at": _now(),
        "refs": list(args.ref or []),
        "commit": _git(["rev-parse", "HEAD"], cwd=root) or None,
        "branch": _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=root) or None,
        "body": body.rstrip() + "\n",
    }}
    _write_once(os.path.join(_dir(root, "messages"), mid + ".yaml"),
                payload, header=MESSAGE_HEADER)
    print(f"{mid}  {sender} -> {', '.join(recipients)}")
    print(f"  {_show(os.path.join(root, 'messages', mid + '.yaml'))}")
    if not args.no_sync_hint:
        print("  NOT yet visible to sessions in other containers. Publish with: "
              "python3 tools/agent_bus.py sync --push")
    return 0


def _fmt_row(rec: dict, root: str, addr: str) -> str:
    mark = " " if acked_by(root, rec["id"], addr) else "*"
    pri = {"high": "!", "normal": " ", "low": "."}.get(rec.get("priority"), " ")
    to = ",".join(rec.get("to") or [])
    return (f"{mark}{pri} {rec['id']}  {rec.get('sent_at', '?'):20} "
            f"{rec.get('from', '?'):>14} -> {to:<14} {rec.get('subject') or ''}")


def cmd_inbox(args) -> int:
    root = _root(args)
    addr = _check_addr(args.addr)
    msgs = inbox_for(root, addr, include_read=args.all, include_own=args.all)
    if args.json:
        print(json.dumps(msgs, indent=2))
        return 0
    label = "all messages" if args.all else "unread"
    if not msgs:
        print(f"no {label} for {addr}.")
        return 0
    print(f"{len(msgs)} {label} for {addr}   (* = unread, ! = high priority)\n")
    for rec in msgs:
        print(_fmt_row(rec, root, addr))
    print(f"\nread one:  python3 tools/agent_bus.py read <MSG-id>")
    print(f"handle it: python3 tools/agent_bus.py ack <MSG-id> --as {addr}")
    return 0


def _find(root: str, mid: str) -> dict:
    _check_msg_id(mid)
    path = os.path.join(root, "messages", mid + ".yaml")
    if not os.path.exists(path):
        raise SystemExit(f"REFUSE: no such message {mid}. If a peer sent it from "
                         "another container, run: agent_bus.py sync")
    return _load(path)["message"]


def _print_message(rec: dict, root: str) -> None:
    print(f"id:       {rec['id']}")
    print(f"from:     {rec.get('from')}")
    print(f"to:       {', '.join(rec.get('to') or [])}")
    print(f"subject:  {rec.get('subject')}")
    print(f"sent_at:  {rec.get('sent_at')}   priority: {rec.get('priority')}")
    if rec.get("in_reply_to"):
        print(f"reply to: {rec['in_reply_to']}   thread: {rec.get('thread')}")
    if rec.get("refs"):
        print(f"refs:     {', '.join(rec['refs'])}")
    if rec.get("branch") or rec.get("commit"):
        print(f"sent from {rec.get('branch')} @ {str(rec.get('commit'))[:12]}")
    readers = sorted(
        n[len(rec["id"]) + 2:-5] for n in os.listdir(_dir(root, "receipts"))
        if n.startswith(rec["id"] + "--") and n.endswith(".yaml"))
    print(f"acked by: {', '.join(readers) if readers else '(nobody yet)'}")
    print("\n" + "-" * 72)
    print(rec.get("body", "").rstrip())
    print("-" * 72)


def cmd_read(args) -> int:
    root = _root(args)
    rec = _find(root, args.msg_id)
    if args.json:
        print(json.dumps(rec, indent=2))
        return 0
    _print_message(rec, root)
    return 0


def cmd_ack(args) -> int:
    root = _root(args)
    addr = _check_addr(args.addr)
    rec = _find(root, args.msg_id)
    if not addressed_to(rec, addr):
        raise SystemExit(f"REFUSE: {rec['id']} is not addressed to {addr} "
                         f"(to: {', '.join(rec.get('to') or [])}).")
    path = _receipt_path(root, rec["id"], addr)
    if os.path.exists(path):
        print(f"{rec['id']} was already acked by {addr}; nothing to do.")
        return 0
    _write_once(path, {"receipt": {
        "message": rec["id"],
        "reader": addr,
        "acked_at": _now(),
        "note": args.note,
    }}, header=RECEIPT_HEADER)
    print(f"acked {rec['id']} as {addr}")
    return 0


def cmd_reply(args) -> int:
    root = _root(args)
    parent = _find(root, args.msg_id)
    sender = _check_addr(args.sender)
    # Reply goes back to the sender plus every other recipient, minus yourself.
    # A broadcast reply that fanned back out to `all` would be a loop generator,
    # so `all` is dropped and the original sender is always kept.
    to = [parent.get("from")] + [a for a in (parent.get("to") or [])
                                 if a not in (sender, BROADCAST)]
    seen, recipients = set(), []
    for a in to:
        if a and a != sender and a not in seen:
            seen.add(a)
            recipients.append(a)
    if not recipients:
        raise SystemExit(f"REFUSE: {parent['id']} leaves nobody to reply to.")

    reply_args = argparse.Namespace(
        root=getattr(args, "root", None), sender=sender,
        to=",".join(recipients),
        subject=args.subject or f"Re: {parent.get('subject') or parent['id']}",
        body=args.body, body_file=args.body_file, priority=args.priority,
        thread=parent.get("thread") or parent["id"], ref=args.ref, seed=args.seed,
        no_sync_hint=args.no_sync_hint)
    # A reply is a statement that you handled it, so record the receipt too.
    rc = cmd_send(reply_args)
    if rc == 0 and addressed_to(parent, sender) and not acked_by(root, parent["id"], sender):
        _write_once(_receipt_path(root, parent["id"], sender), {"receipt": {
            "message": parent["id"], "reader": sender, "acked_at": _now(),
            "note": "acked implicitly by replying",
        }}, header=RECEIPT_HEADER)
    return rc


def cmd_thread(args) -> int:
    root = _root(args)
    rec = _find(root, args.msg_id)
    tid = rec.get("thread") or rec["id"]
    members = [m for m in load_messages(root) if (m.get("thread") or m["id"]) == tid]
    print(f"thread {tid}  ({len(members)} message(s))\n")
    for i, m in enumerate(members):
        if i:
            print()
        _print_message(m, root)
    return 0


def cmd_peers(args) -> int:
    root = _root(args)
    sessions = _dir(root, "sessions")
    names = sorted(n[:-5] for n in os.listdir(sessions) if n.endswith(".yaml"))
    if not names:
        print("no registered addresses. Each session should run:\n"
              "  python3 tools/agent_bus.py register --as <addr> --role <role>")
        return 0
    print(f"{len(names)} registered address(es)\n")
    for name in names:
        s = _load(os.path.join(sessions, name + ".yaml")).get("session", {})
        unread = len(inbox_for(root, name))
        print(f"  {name:<18} role={s.get('role') or '?':<14} "
              f"branch={s.get('branch') or '?':<32} unread={unread}")
        if s.get("goal"):
            print(f"  {'':<18} goal={s['goal']}")
    return 0


# --------------------------------------------------------------------------
# Git transport
# --------------------------------------------------------------------------

def _git_run(argv: list[str], *, cwd: str, check: bool = False) -> tuple[bool, str]:
    """Run git, returning (succeeded, stripped stdout).

    Success is the EXIT CODE, never the output. `fetch` and `push` report their
    work on stderr and leave stdout empty, so a stdout-truthiness test calls a
    perfectly good push a failure and retries it four times.

    Non-fatal by default: the bus is useful on a single machine with no remote
    at all, and a session must not lose a message because `git` was unhappy.
    """
    try:
        proc = subprocess.run(["git"] + argv, cwd=cwd, capture_output=True,
                              text=True, timeout=180)
    except (OSError, subprocess.SubprocessError) as exc:
        if check:
            raise SystemExit(f"git {' '.join(argv)} failed: {exc}")
        return False, ""
    if proc.returncode != 0:
        if check:
            raise SystemExit(f"git {' '.join(argv)} failed:\n{proc.stderr.strip()}")
        return False, ""
    return True, proc.stdout.strip()


def _git(argv: list[str], *, cwd: str, check: bool = False) -> str:
    """Stripped stdout, or "" on failure. For queries, where "" is a fine answer."""
    return _git_run(argv, cwd=cwd, check=check)[1]


def cmd_sync(args) -> int:
    """Publish local bus records and collect everyone else's.

    Merge, never rebase: bus records are write-once files with unique names, so
    a merge cannot conflict, while a rebase would rewrite the commits a peer may
    already have pulled.
    """
    root = _root(args)
    top = _git(["rev-parse", "--show-toplevel"], cwd=root)
    if not top:
        print("not a git repository; the bus is local-only here. That is fine "
              "for sessions sharing one filesystem.", file=sys.stderr)
        return 0
    rel = os.path.relpath(root, top)
    branch = args.branch or _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=top)
    remote = args.remote

    if _git(["status", "--porcelain", "--", rel], cwd=top):
        _git(["add", "--", rel], cwd=top, check=True)
        _git(["commit", "-m", args.message or f"bus: publish records from {rel}",
              "--", rel], cwd=top, check=True)
        print(f"committed local bus records under {rel}")

    for attempt, backoff in enumerate((2, 4, 8, 16, None)):
        if _git_run(["fetch", remote, branch], cwd=top)[0]:
            break
        if backoff is None:
            print(f"warning: could not fetch {remote}/{branch} after "
                  f"{attempt} retries; syncing with local state only",
                  file=sys.stderr)
            break
        time.sleep(backoff)

    if _git(["rev-parse", "--verify", "--quiet", f"{remote}/{branch}"], cwd=top):
        ok, out = _git_run(["merge", "--no-edit", f"{remote}/{branch}"], cwd=top)
        if ok:
            print(out or f"merged {remote}/{branch}")
        else:
            # Cannot happen from bus records alone -- they are write-once files
            # with unique names. It means the branch carries other work, so this
            # is the human's merge to resolve, not the bus's.
            print(f"ERROR: merging {remote}/{branch} failed. The bus itself "
                  "cannot conflict, so this is other work on the branch; "
                  "resolve it and re-run sync.", file=sys.stderr)
            return 1

    if args.push:
        for backoff in (2, 4, 8, 16, None):
            if _git_run(["push", "-u", remote, branch], cwd=top)[0]:
                print(f"pushed {branch} to {remote}")
                break
            if backoff is None:
                print(f"ERROR: push to {remote}/{branch} failed after retries. "
                      "Local records are committed and will publish on the next "
                      "successful sync.", file=sys.stderr)
                return 1
            time.sleep(backoff)
    return 0


def cmd_watch(args) -> int:
    """Poll for new mail, printing one line per message.

    Built for the harness `Monitor` tool, which turns each stdout line into a
    notification. Line-buffered on purpose so a match is not sitting in a pipe
    when the interesting thing happens.
    """
    root = _root(args)
    addr = _check_addr(args.addr)
    seen = {rec["id"] for rec in inbox_for(root, addr, include_read=True)} \
        if args.only_new else set()
    deadline = time.monotonic() + args.max_seconds if args.max_seconds else None
    while True:
        if args.sync:
            cmd_sync(argparse.Namespace(
                root=getattr(args, "root", None), branch=args.branch,
                remote=args.remote, push=False, message=None))
        for rec in inbox_for(root, addr):
            if rec["id"] in seen:
                continue
            seen.add(rec["id"])
            pri = "HIGH " if rec.get("priority") == "high" else ""
            print(f"{pri}{rec['id']} from {rec.get('from')}: "
                  f"{rec.get('subject') or '(no subject)'}", flush=True)
        if deadline and time.monotonic() >= deadline:
            return 0
        time.sleep(args.interval)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _add_common(p) -> None:
    p.add_argument("--root", help="bus directory (default coordination/bus, "
                                  "or $AGENT_BUS_ROOT)")


def _add_send_fields(p) -> None:
    p.add_argument("--body", help="message body")
    p.add_argument("--body-file", help="read the body from a file")
    p.add_argument("--priority", choices=PRIORITIES, default="normal")
    p.add_argument("--ref", action="append", metavar="ID",
                   help="ledger/experiment id this message points at "
                        "(repeatable) -- the state lives there, not here")
    p.add_argument("--seed", type=int, default=None,
                   help="seed the id allocator (tests and reproduction only)")
    p.add_argument("--no-sync-hint", action="store_true",
                   help="suppress the 'publish with sync' reminder")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="python3 tools/agent_bus.py",
        description="Durable write-once messaging between agent sessions.",
        epilog="Messages are coordination traffic, never research evidence. "
               "Point at ledger IDs with --ref; do not restate findings here.")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("register", help="declare this session's address")
    _add_common(p)
    p.add_argument("--as", dest="addr", required=True)
    p.add_argument("--role", help="role contract this session is running")
    p.add_argument("--goal", help="GOAL-* this session is working")
    p.add_argument("--runtime", help="claude_code, codex_cli, opencode, ...")
    p.add_argument("--note")
    p.set_defaults(func=cmd_register)

    p = sub.add_parser("send", help="write a message to one or more addresses")
    _add_common(p)
    p.add_argument("--from", dest="sender", required=True)
    p.add_argument("--to", required=True,
                   help=f"comma-separated addresses, or '{BROADCAST}'")
    p.add_argument("--subject", required=True)
    p.add_argument("--thread", help="MSG-id this belongs to")
    _add_send_fields(p)
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("inbox", help="list messages waiting for an address")
    _add_common(p)
    p.add_argument("--as", dest="addr", required=True)
    p.add_argument("--all", action="store_true", help="include already-acked")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_inbox)

    p = sub.add_parser("read", help="print one message in full")
    _add_common(p)
    p.add_argument("msg_id")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("ack", help="record that an address handled a message")
    _add_common(p)
    p.add_argument("msg_id")
    p.add_argument("--as", dest="addr", required=True)
    p.add_argument("--note")
    p.set_defaults(func=cmd_ack)

    p = sub.add_parser("reply", help="answer a message in its thread and ack it")
    _add_common(p)
    p.add_argument("msg_id")
    p.add_argument("--from", dest="sender", required=True)
    p.add_argument("--subject", help="default: Re: <original subject>")
    _add_send_fields(p)
    p.set_defaults(func=cmd_reply)

    p = sub.add_parser("thread", help="print every message in a thread")
    _add_common(p)
    p.add_argument("msg_id")
    p.set_defaults(func=cmd_thread)

    p = sub.add_parser("peers", help="list registered addresses and their unread")
    _add_common(p)
    p.set_defaults(func=cmd_peers)

    p = sub.add_parser("sync", help="exchange bus records with the git remote")
    _add_common(p)
    p.add_argument("--remote", default="origin")
    p.add_argument("--branch", help="default: the current branch")
    p.add_argument("--push", action="store_true", help="publish local records")
    p.add_argument("--message", help="commit message")
    p.set_defaults(func=cmd_sync)

    p = sub.add_parser("watch", help="poll for new mail, one line per message")
    _add_common(p)
    p.add_argument("--as", dest="addr", required=True)
    p.add_argument("--interval", type=float, default=30.0, metavar="SECONDS")
    p.add_argument("--sync", action="store_true",
                   help="git-sync each poll (required across containers)")
    p.add_argument("--remote", default="origin")
    p.add_argument("--branch")
    p.add_argument("--max-seconds", type=float, default=None,
                   help="stop after this long (default: run until killed)")
    p.add_argument("--only-new", action="store_true", default=True,
                   help="skip mail that was already unread at startup")
    p.add_argument("--include-existing", dest="only_new", action="store_false",
                   help="report currently-unread mail on the first poll too")
    p.set_defaults(func=cmd_watch)

    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
