#!/usr/bin/env python3
"""Runtime relay: hand a session's work from Claude Code to Codex (or back)
when one runtime's budget runs out, without losing what only it knew.

A handoff is three files under .resume/ (gitignored), rebuilt from facts
rather than from the model's memory:

  HANDOFF.md     what the next runtime reads: why the last one stopped, git
                 state (branch, HEAD, unpushed commits, dirty files), the
                 last user request and assistant message, the last shell
                 commands, pointers to RESUME.md and the session log, and a
                 takeover checklist.
  handoff.json   the same, machine-readable, with status draft|pending|accepted.
  relay.jsonl    append-only history of hops (from, to, reason, HEAD).

The hooks keep a draft current after every turn, so a session that dies on a
usage limit still leaves one. On a budget failure (Claude Code `StopFailure`
with error rate_limit or billing_error) the draft becomes pending and a
checkpoint goes to S3 (scripts/checkpoint.sh), so another machine can restore it.

    relay.py out --to codex [--reason budget] [--note TEXT] [--no-push]
                              mark a handoff pending, push a checkpoint and
                              print the command that starts the other runtime
    relay.py switch --to codex [--exec]
                              out, then start (or print) the other runtime
                              interactively with the takeover prompt
    relay.py accept           the incoming runtime claims the handoff: checks
                              the branch and HEAD still match, prints it
    relay.py status           show the current handoff
    relay.py prompt [--to R]  print the takeover prompt
    relay.py run [--prefer claude,codex] [--max-hops N] [--cooldown S] -- TASK
                              headless failover loop: run TASK on the
                              preferred runtime, and on a budget stop hand it
                              to the next one, until it finishes
    relay.py doctor           check both runtimes are wired for relaying
    relay.py install DIR      copy this script into another checkout's scripts/
    relay.py snapshot | session-start   (hook entry points; read hook JSON on stdin)

Configuration (environment):
  RELAY_CLAUDE_CMD   headless Claude command (default "claude -p")
  RELAY_CODEX_CMD    headless Codex command  (default "codex exec")
  RELAY_CLAUDE_TUI   interactive Claude      (default "claude")
  RELAY_CODEX_TUI    interactive Codex       (default "codex")
  RELAY_BUDGET_RE    extra regex that marks a budget stop in runtime output
  RELAY_RUNTIME      this session's runtime when no hook says so

Stdlib only, so the same file works in every checkout and on any host.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RUNTIMES = ("claude", "codex")
BUDGET_ERRORS = {"rate_limit", "billing_error"}
# Text the runtimes print when an account's budget, not the task, stopped them.
BUDGET_RE = re.compile(
    r"usage[ _-]?limit|rate[ _-]?limit|hit your (usage )?limit|limit reached|"
    r"insufficient_quota|quota exceeded|exceeded your current quota|"
    r"credit balance is too low|billing_error|429 Too Many Requests|"
    r"try again (at|in) |resets? (at|in) ",
    re.IGNORECASE,
)
SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"\b(sk|rk)-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"X-Amz-(Signature|Credential|Security-Token)=[^&\s\"']+"),
    re.compile(r"(?i)\b(secret|token|password|passwd|api[_-]?key|authorization)(\s*[:=]\s*|\s+)['\"]?[^\s'\"]{8,}"),
    re.compile(r"[A-Za-z0-9+/=_-]{80,}"),
]
EXCERPT = 2000
TAIL_BYTES = 4 * 1024 * 1024


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: UP017 -- runs on python3 < 3.11 too


def redact(text: str, limit: int = EXCERPT) -> str:
    for pat in SECRET_PATTERNS:
        text = pat.sub("[redacted]", text)
    text = text.strip()
    return text if len(text) <= limit else text[: limit - 20].rstrip() + "\n[... truncated]"


def git(root: Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def toplevel(start: str | None = None) -> Path:
    top = git(Path(start or "."), "rev-parse", "--show-toplevel")
    if not top:
        sys.exit("relay: not inside a git worktree")
    return Path(top)


def paths(root: Path) -> dict[str, Path]:
    d = root / ".resume"
    return {"dir": d, "md": d / "HANDOFF.md", "json": d / "handoff.json", "log": d / "relay.jsonl"}


def load(root: Path) -> dict:
    try:
        return json.loads(paths(root)["json"].read_text())
    except (OSError, ValueError):
        return {}


def other(runtime: str) -> str:
    return "codex" if runtime == "claude" else "claude"


def detect_runtime(hook: dict) -> str:
    if os.environ.get("RELAY_RUNTIME") in RUNTIMES:
        return os.environ["RELAY_RUNTIME"]
    tp = str(hook.get("transcript_path") or "")
    if "/.codex/" in tp or os.environ.get("CODEX_HOME") or os.environ.get("CODEX_SANDBOX"):
        return "codex"
    if "/.claude/" in tp or os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_PROJECT_DIR"):
        return "claude"
    return "unknown"


# --- transcripts ---------------------------------------------------------

def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict) and c.get("type") in ("text", "input_text", "output_text"):
                parts.append(str(c.get("text", "")))
        return "\n".join(p for p in parts if p)
    return ""


def _command(name: str, args) -> str:
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            return args
    if not isinstance(args, dict):
        return ""
    cmd = args.get("command") or args.get("cmd") or ""
    if isinstance(cmd, list):
        cmd = cmd[-1] if len(cmd) >= 3 and cmd[0] in ("bash", "sh", "zsh") and cmd[1] in ("-c", "-lc") else shlex.join(map(str, cmd))
    return str(cmd)


def read_transcript(path: str) -> dict:
    """Last user request, last assistant text and recent shell commands from a
    Claude Code (projects/*.jsonl) or Codex (sessions/rollout-*.jsonl) transcript."""
    out = {"last_user": "", "last_assistant": "", "commands": []}
    if not path:
        return out
    p = Path(path).expanduser()
    try:
        size = p.stat().st_size
        with p.open("rb") as fh:
            if size > TAIL_BYTES:
                fh.seek(size - TAIL_BYTES)
                fh.readline()
            lines = fh.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return out
    commands: list[str] = []
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if not isinstance(e, dict):
            continue
        if e.get("type") in ("user", "assistant") and isinstance(e.get("message"), dict):  # Claude Code
            if e.get("isSidechain") or e.get("isMeta"):
                continue
            msg = e["message"]
            text = _text(msg.get("content"))
            if e["type"] == "user" and text and not text.lstrip().startswith("<"):
                out["last_user"] = text
            elif e["type"] == "assistant":
                if text:
                    out["last_assistant"] = text
                for c in msg.get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Bash":
                        commands.append(_command("Bash", c.get("input")))
            continue
        payload = e.get("payload") if isinstance(e.get("payload"), dict) else e  # Codex rollout
        kind = payload.get("type")
        if kind == "message":
            text = _text(payload.get("content"))
            if payload.get("role") == "user" and text and not text.lstrip().startswith("<"):
                out["last_user"] = text
            elif payload.get("role") == "assistant" and text:
                out["last_assistant"] = text
        elif kind in ("function_call", "local_shell_call", "custom_tool_call"):
            cmd = _command(payload.get("name", ""), payload.get("arguments") or payload.get("action") or payload.get("input"))
            if cmd:
                commands.append(cmd)
        elif kind == "user_message" and payload.get("message"):
            out["last_user"] = str(payload["message"])
        elif kind == "agent_message" and payload.get("message"):
            out["last_assistant"] = str(payload["message"])
    out["commands"] = [redact(c, 300) for c in commands if c][-10:]
    out["last_user"] = redact(out["last_user"])
    out["last_assistant"] = redact(out["last_assistant"])
    return out


# --- state ---------------------------------------------------------------

def git_state(root: Path) -> dict:
    branch = git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    upstream = git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    unpushed = git(root, "log", "--oneline", "-n", "20", "HEAD", "--not", "--remotes")
    status = git(root, "status", "--porcelain=v1", "--untracked-files=normal")
    url = git(root, "config", "--get", "remote.origin.url")
    return {
        "repo": Path(url).stem if url else root.name,
        "origin": re.sub(r"//[^@/]+@", "//", url),
        "worktree": str(root),
        "branch": branch or "(detached)",
        "head": git(root, "rev-parse", "HEAD"),
        "head_subject": git(root, "log", "-1", "--format=%s"),
        "upstream": upstream,
        "unpushed": [l for l in unpushed.splitlines() if l],
        "dirty": [l for l in status.splitlines() if l and not l[3:].startswith(".resume/")][:60],
        "stashes": len([l for l in git(root, "stash", "list").splitlines() if l]),
    }


def pr_for_branch(root: Path, branch: str) -> str:
    if not shutil.which("gh") or branch == "(detached)":
        return ""
    try:
        out = subprocess.run(["gh", "pr", "view", branch, "--json", "number,url,state,isDraft"],
                             cwd=root, capture_output=True, text=True, timeout=20, check=False)
        if out.returncode == 0:
            d = json.loads(out.stdout)
            return f"#{d['number']} {d['state'].lower()}{' draft' if d.get('isDraft') else ''} {d['url']}"
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
        pass
    return ""


def resume_state(root: Path) -> str:
    f = root / ".resume" / "RESUME.md"
    if not f.exists():
        return "missing (scripts/checkpoint.sh init writes the template)"
    return "has TODO(checkpoint) placeholders" if "TODO(checkpoint)" in f.read_text(errors="replace") else "present"


def session_log(root: Path) -> str:
    d = root / "docs" / "session-logs"
    logs = sorted(p for p in d.glob("20*.md")) if d.is_dir() else []
    return str(logs[-1].relative_to(root)) if logs else ""


def history(root: Path, n: int = 5) -> list[dict]:
    try:
        rows = [json.loads(l) for l in paths(root)["log"].read_text().splitlines() if l.strip()]
    except (OSError, ValueError):
        return []
    return rows[-n:]


def render(h: dict) -> str:
    g = h["git"]
    t = h.get("transcript") or {}
    lines = [
        f"# Handoff: {g['repo']} @ {g['branch']}",
        "",
        f"- status: **{h['status']}**",
        f"- from: {h['from']} (session {h.get('session_id') or 'unknown'})  →  to: {h.get('to') or 'either'}",
        f"- reason: {h['reason']}" + (f" ({h['error_detail']})" if h.get("error_detail") else ""),
        f"- written: {h['written_utc']}",
        f"- checkpoint: {h.get('checkpoint') or 'not pushed'}",
    ]
    if h.get("note"):
        lines += ["", "## Note from the outgoing session", "", h["note"]]
    lines += [
        "",
        "## Git",
        "",
        f"- worktree: `{g['worktree']}`",
        f"- branch: `{g['branch']}`  upstream: `{g['upstream'] or 'none'}`",
        f"- HEAD: `{g['head'][:12]}` {g['head_subject']}",
        f"- pull request: {h.get('pr') or 'none found (or gh unavailable)'}",
        f"- stashes: {g['stashes']}",
        "",
        f"Unpushed commits ({len(g['unpushed'])}):",
        "",
    ]
    lines += [f"    {c}" for c in g["unpushed"]] or ["    none"]
    lines += ["", f"Uncommitted changes ({len(g['dirty'])}):", ""]
    lines += [f"    {c}" for c in g["dirty"]] or ["    none"]
    lines += [
        "",
        "## Where the work stood",
        "",
        f"- RESUME.md: `.resume/RESUME.md` ({h['resume']})",
        f"- session log: `{h['session_log']}`" if h.get("session_log") else "- session log: none",
    ]
    if t.get("last_user"):
        lines += ["", "### Last user request (excerpt)", "", "```text", t["last_user"], "```"]
    if t.get("last_assistant"):
        lines += ["", "### Last assistant message (excerpt)", "", "```text", t["last_assistant"], "```"]
    if t.get("commands"):
        lines += ["", "### Last shell commands", ""] + [f"    {c}" for c in t["commands"]]
    if h.get("history"):
        lines += ["", "## Relay history", ""]
        lines += [f"- {r.get('utc')} {r.get('from')} → {r.get('to')} ({r.get('reason')}) at {str(r.get('head', ''))[:12]}"
                  for r in h["history"]]
    lines += [
        "",
        "## Takeover checklist",
        "",
        "1. `python3 scripts/relay.py accept` (checks branch and HEAD, claims the handoff).",
        "2. Read `AGENTS.md`, then `.resume/RESUME.md` and the session log above.",
        "3. Check runs in flight before relaunching anything; do not redo finished steps.",
        "4. Continue the last user request from where the git state shows it stopped.",
        "5. Keep `.resume/RESUME.md` current; `python3 scripts/relay.py out` when you stop.",
        "",
    ]
    return "\n".join(lines)


def push_checkpoint(root: Path) -> str:
    script = root / "scripts" / "checkpoint.sh"
    if not os.access(script, os.X_OK):
        return ""
    try:
        out = subprocess.run([str(script), "push", "--force"], cwd=root, capture_output=True, text=True, timeout=90, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"push failed: {exc}"
    text = (out.stdout + out.stderr).strip().splitlines()
    last = text[-1] if text else ""
    if out.returncode == 0:
        m = re.search(r"s3://\S+", last)
        return m.group(0) if m else last
    return f"push failed: {last}"


def write(root: Path, *, status: str, reason: str, frm: str, to: str = "", hook: dict | None = None,
          note: str = "", detail: str = "", push: bool = False) -> dict:
    hook = hook or {}
    p = paths(root)
    p["dir"].mkdir(exist_ok=True)
    prev = load(root)
    g = git_state(root)
    tpath = hook.get("transcript_path") or ""
    if not tpath and prev.get("session_id") == hook.get("session_id"):
        tpath = prev.get("transcript_path", "")
    transcript = read_transcript(tpath) if tpath else prev.get("transcript") or {}
    if hook.get("last_assistant_message"):
        transcript = {**transcript, "last_assistant": redact(str(hook["last_assistant_message"]))}
    h = {
        "schema": "runtime-relay/v1",
        "status": status,
        "reason": reason,
        "error_detail": redact(detail, 300) if detail else "",
        "from": frm,
        "to": to,
        "session_id": hook.get("session_id") or (prev.get("session_id") if frm == prev.get("from") else ""),
        "transcript_path": tpath,
        "written_utc": now(),
        "note": redact(note, 4000) if note else (prev.get("note", "") if status != "draft" else ""),
        "git": g,
        "pr": pr_for_branch(root, g["branch"]) if status == "pending" else prev.get("pr", ""),
        "resume": resume_state(root),
        "session_log": session_log(root),
        "transcript": transcript,
        "history": history(root),
        "checkpoint": "",
    }
    p["json"].write_text(json.dumps(h, indent=2) + "\n")
    p["md"].write_text(render(h))
    if push:
        h["checkpoint"] = push_checkpoint(root)
        p["json"].write_text(json.dumps(h, indent=2) + "\n")
        p["md"].write_text(render(h))
    return h


def log_hop(root: Path, row: dict) -> None:
    with paths(root)["log"].open("a") as fh:
        fh.write(json.dumps({"utc": now(), **row}) + "\n")


def takeover_prompt(root: Path, h: dict, task: str = "") -> str:
    g = h.get("git", {})
    s = (f"You are taking over work from a {h.get('from', 'previous')} session that stopped "
         f"({h.get('reason', 'handoff')}) in {g.get('worktree', root)} on branch {g.get('branch', '?')}. "
         "First run `python3 scripts/relay.py accept`, then read AGENTS.md, .resume/HANDOFF.md and "
         ".resume/RESUME.md, and continue the work from where it stopped: verify runs in flight before "
         "relaunching, do not redo finished steps, and follow the repository's rules for commits and PRs.")
    if task:
        s += f"\n\nThe task you are continuing:\n{task}"
    return s


def launch_argv(runtime: str, interactive: bool, prompt: str) -> list[str]:
    # "--" ends option parsing, so a configured command that ends in a
    # multi-value flag (claude -p --allowedTools A B) cannot swallow the prompt.
    return [*runtime_cmd(runtime, interactive), "--", prompt]


def runtime_cmd(runtime: str, interactive: bool) -> list[str]:
    key = f"RELAY_{runtime.upper()}_{'TUI' if interactive else 'CMD'}"
    default = runtime if interactive else {"claude": "claude -p", "codex": "codex exec"}[runtime]
    return shlex.split(os.environ.get(key, default))


# --- commands ------------------------------------------------------------

def read_hook() -> dict:
    if sys.stdin.isatty():
        return {}
    try:
        data = sys.stdin.read()
        return json.loads(data) if data.strip() else {}
    except (OSError, ValueError):
        return {}


def cmd_snapshot(args) -> int:
    """Hook entry: keep a draft current; on a budget failure make it pending and push."""
    hook = read_hook()
    try:
        root = Path(git(Path(hook.get("cwd") or "."), "rev-parse", "--show-toplevel"))
        if not str(root) or not root.is_dir():
            return 0
        runtime = args.runtime or detect_runtime(hook)
        prev = load(root)
        event = hook.get("hook_event_name", "")
        error = str(hook.get("error") or "")
        budget = event == "StopFailure" and error in BUDGET_ERRORS
        # A pending handoff stays until it is accepted, even across the outgoing
        # session's own Stop hook; only a new budget stop replaces it.
        if prev.get("status") == "pending" and not budget:
            return 0
        if budget:
            h = write(root, status="pending", reason=f"budget: {error}", frm=runtime, to=other(runtime),
                      hook=hook, detail=str(hook.get("error_details") or ""), push=True)
            log_hop(root, {"from": runtime, "to": other(runtime), "reason": h["reason"],
                           "head": h["git"]["head"], "checkpoint": h["checkpoint"], "auto": True})
        elif event == "StopFailure":
            write(root, status="draft", reason=f"api error: {error or 'unknown'}", frm=runtime, hook=hook,
                  detail=str(hook.get("error_details") or ""))
        else:
            write(root, status="draft", reason="turn ended", frm=runtime, hook=hook)
    except Exception as exc:  # noqa: BLE001 -- a hook must never break the session
        print(f"relay snapshot: {exc}", file=sys.stderr)
    return 0


def cmd_session_start(args) -> int:
    hook = read_hook()
    root_s = git(Path(hook.get("cwd") or "."), "rev-parse", "--show-toplevel")
    if not root_s:
        return 0
    root = Path(root_s)
    h = load(root)
    if h.get("status") != "pending" or h.get("session_id") == hook.get("session_id"):
        return 0
    runtime = args.runtime or detect_runtime(hook)
    msg = (f"A pending runtime handoff from {h.get('from')} ({h.get('reason')}, {h.get('written_utc')}) is in "
           f"{root}/.resume/HANDOFF.md. " + takeover_prompt(root, h))
    if runtime == "claude":
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}}))
    else:
        print(msg)
    return 0


def cmd_out(args) -> int:
    root = toplevel()
    frm = args.runtime or detect_runtime({})
    to = args.to or other(frm)
    prev = load(root)
    # Reuse the transcript the hooks last saw, when it was this runtime's.
    hook = {k: prev.get(k, "") for k in ("session_id", "transcript_path")} if prev.get("from") == frm else {}
    h = write(root, status="pending", reason=args.reason, frm=frm, to=to, note=args.note or "",
              hook=hook, push=not args.no_push)
    log_hop(root, {"from": frm, "to": to, "reason": args.reason, "head": h["git"]["head"],
                   "checkpoint": h["checkpoint"], "auto": False})
    print(f"relay: handoff pending in {paths(root)['md']}")
    if h["checkpoint"]:
        print(f"relay: checkpoint {h['checkpoint']}")
    if h["git"]["unpushed"]:
        print(f"relay: {len(h['git']['unpushed'])} unpushed commit(s): push them, or restore from the checkpoint elsewhere")
    if not args.quiet:
        print("\nStart the other runtime here with:\n")
        print("  " + shlex.join(launch_argv(to, True, takeover_prompt(root, h))))
    return 0


def cmd_switch(args) -> int:
    args.quiet = True
    cmd_out(args)
    root = toplevel()
    h = load(root)
    argv = launch_argv(h["to"], True, takeover_prompt(root, h))
    if args.exec:
        if not shutil.which(argv[0]):
            sys.exit(f"relay: {argv[0]} is not on PATH")
        os.chdir(root)
        os.execvp(argv[0], argv)
    print(shlex.join(argv))
    return 0


def cmd_accept(args) -> int:
    root = toplevel()
    h = load(root)
    if not h:
        print("relay: no handoff in .resume/; nothing to accept")
        return 1
    g = git_state(root)
    problems = []
    if h["git"].get("branch") != g["branch"]:
        problems.append(f"branch is {g['branch']}, handoff was written on {h['git'].get('branch')}")
    if h["git"].get("head") != g["head"]:
        problems.append(f"HEAD is {g['head'][:12]}, handoff was written at {h['git'].get('head', '')[:12]}"
                        " (restore the checkpoint, or check what moved)")
    print(paths(root)["md"].read_text())
    for p in problems:
        print(f"relay: WARNING: {p}")
    runtime = args.runtime or detect_runtime({})
    if h.get("status") == "pending":
        h["status"] = "accepted"
        h["accepted_by"] = runtime
        h["accepted_utc"] = now()
        paths(root)["json"].write_text(json.dumps(h, indent=2) + "\n")
        paths(root)["md"].write_text(render(h))
        log_hop(root, {"from": h.get("from"), "to": runtime, "reason": "accepted", "head": g["head"]})
    return 0


def cmd_status(args) -> int:
    root = toplevel()
    h = load(root)
    if not h:
        print("relay: no handoff yet")
        return 0
    if args.json:
        print(json.dumps(h, indent=2))
        return 0
    g = h["git"]
    print(f"status   : {h['status']} ({h['reason']})")
    print(f"from/to  : {h['from']} -> {h.get('to') or 'either'}  written {h['written_utc']}")
    print(f"git      : {g['branch']} @ {g['head'][:12]}, {len(g['unpushed'])} unpushed, {len(g['dirty'])} dirty")
    print(f"checkpoint: {h.get('checkpoint') or 'not pushed'}")
    print(f"file     : {paths(root)['md']}")
    return 0


def cmd_prompt(args) -> int:
    root = toplevel()
    print(takeover_prompt(root, load(root) or {"git": git_state(root)}))
    return 0


def budget_stop(output: str, code: int, root: Path, started: str, runtime: str) -> bool:
    h = load(root)
    if (h.get("status") == "pending" and h.get("from") == runtime and h.get("written_utc", "") >= started
            and h.get("reason", "").startswith("budget")):  # its StopFailure hook already said so
        return True
    if code == 0:
        return False
    extra = os.environ.get("RELAY_BUDGET_RE")
    tail = output[-20000:]
    return bool(BUDGET_RE.search(tail) or (extra and re.search(extra, tail, re.IGNORECASE)))


def cmd_run(args) -> int:
    root = toplevel()
    order = [r.strip() for r in args.prefer.split(",") if r.strip() in RUNTIMES]
    if not order:
        sys.exit("relay: --prefer names no known runtime (claude, codex)")
    task = " ".join(args.task).strip()
    if not task:
        sys.exit("relay: run needs a task after --")
    logdir = paths(root)["dir"] / "relay-runs"
    logdir.mkdir(parents=True, exist_ok=True)
    prompt, i, hops, exhausted, missing = task, 0, 0, set(), set()
    while hops <= args.max_hops:
        rt = order[i % len(order)]
        argv = launch_argv(rt, False, prompt)
        if not shutil.which(argv[0]):
            print(f"relay: {argv[0]} not on PATH; skipping {rt}", file=sys.stderr)
            missing.add(rt)
            if missing >= set(order):
                print("relay: no runtime executable is available", file=sys.stderr)
                return 127
        else:
            started = now()
            log = logdir / f"{started.replace(':', '')}-{rt}.log"
            print(f"relay: [{hops}] {rt}: {shlex.join(argv[:-2])} -- <prompt>  (log {log})", file=sys.stderr)
            env = {**os.environ, "RELAY_RUNTIME": rt}
            with log.open("w") as fh:
                proc = subprocess.Popen(argv, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                buf = []
                for line in proc.stdout:
                    sys.stdout.write(line)
                    fh.write(line)
                    buf.append(line)
                code = proc.wait()
            if not budget_stop("".join(buf), code, root, started, rt):
                print(f"relay: {rt} finished (exit {code})", file=sys.stderr)
                return code
            exhausted.add(rt)
            nxt = order[(i + 1) % len(order)]
            h = load(root)
            if not (h.get("status") == "pending" and h.get("from") == rt and h.get("written_utc", "") >= started):
                h = write(root, status="pending", reason="budget: runtime output", frm=rt, to=nxt,
                          detail=f"exit {code}", push=not args.no_push)
                log_hop(root, {"from": rt, "to": nxt, "reason": h["reason"], "head": h["git"]["head"],
                               "checkpoint": h["checkpoint"], "auto": True})
            prompt = takeover_prompt(root, h, task)
            hops += 1
        i += 1
        if exhausted | missing >= set(order):
            print(f"relay: every runtime is out of budget; waiting {args.cooldown}s", file=sys.stderr)
            time.sleep(args.cooldown)
            exhausted.clear()
    print(f"relay: stopped after {args.max_hops} hop(s); handoff in {paths(root)['md']}", file=sys.stderr)
    return 75


def cmd_doctor(args) -> int:
    root = toplevel()
    rel = os.path.relpath(Path(__file__).resolve(), root)
    checks: list[tuple[bool, str]] = []
    for rt in RUNTIMES:
        exe = runtime_cmd(rt, False)[0]
        checks.append((bool(shutil.which(exe)), f"{rt} CLI `{exe}` on PATH"))
    claude = root / ".claude" / "settings.json"
    try:
        hooks = json.loads(claude.read_text()).get("hooks", {})
    except (OSError, ValueError):
        hooks = {}
    for ev in ("StopFailure", "Stop", "SessionStart"):
        ok = "relay.py" in json.dumps(hooks.get(ev, []))
        checks.append((ok, f"Claude Code {ev} hook runs relay.py (.claude/settings.json)"))
    codex = root / ".codex" / "hooks.json"
    try:
        chooks = json.loads(codex.read_text()).get("hooks", {})
    except (OSError, ValueError):
        chooks = {}
    for ev in ("Stop", "SessionStart"):
        checks.append(("relay.py" in json.dumps(chooks.get(ev, [])), f"Codex {ev} hook runs relay.py (.codex/hooks.json)"))
    agents = root / "AGENTS.md"
    checks.append((agents.exists() and "relay" in agents.read_text(errors="replace"),
                   "AGENTS.md points every runtime at the relay"))
    checks.append(((root / ".gitignore").exists() and ".resume/" in (root / ".gitignore").read_text(),
                   ".resume/ is gitignored"))
    cp = root / "scripts" / "checkpoint.sh"
    checks.append((os.access(cp, os.X_OK), "scripts/checkpoint.sh present (S3 checkpoints)"))
    if os.access(cp, os.X_OK):
        checks.append(("HANDOFF.md" in cp.read_text(), "checkpoint.sh carries .resume/HANDOFF.md"))
    a, c = root / ".agents" / "skills", root / ".claude" / "skills"
    if a.is_dir() or c.is_dir():
        an = {p.name for p in a.iterdir() if (p / "SKILL.md").exists()} if a.is_dir() else set()
        cn = {p.name for p in c.iterdir() if (p / "SKILL.md").exists()} if c.is_dir() else set()
        checks.append((an == cn, (f"skills on both surfaces ({len(an & cn)} shared, "
                                  f"{len(cn - an)} Claude-only, {len(an - cn)} Codex-only)")))
    bad = 0
    for ok, what in checks:
        bad += not ok
        print(f"  [{'ok' if ok else '!!'}] {what}")
    print(f"relay doctor ({rel}): {'ready' if not bad else f'{bad} gap(s)'}")
    return 1 if bad else 0


def cmd_install(args) -> int:
    dest_root = toplevel(args.dir)
    dest = dest_root / "scripts" / "relay.py"
    dest.parent.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__).resolve(), dest)
    dest.chmod(0o755)
    print(f"relay: installed {dest}")
    print("Wire the hooks as in docs/runtime-relay.md, then run: python3 scripts/relay.py doctor")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="relay.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runtime", choices=RUNTIMES, help="this session's runtime (default: detected)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("out", "switch"):
        s = sub.add_parser(name)
        s.add_argument("--to", choices=RUNTIMES)
        s.add_argument("--reason", default="budget")
        s.add_argument("--note", help="what the next runtime most needs to know")
        s.add_argument("--no-push", action="store_true", help="skip the S3 checkpoint")
        s.add_argument("--quiet", action="store_true")
        if name == "switch":
            s.add_argument("--exec", action="store_true", help="replace this process with the other runtime")
    sub.add_parser("accept")
    st = sub.add_parser("status")
    st.add_argument("--json", action="store_true")
    sub.add_parser("prompt").add_argument("--to", choices=RUNTIMES)
    r = sub.add_parser("run")
    r.add_argument("--prefer", default="claude,codex")
    r.add_argument("--max-hops", type=int, default=6)
    r.add_argument("--cooldown", type=int, default=900, help="seconds to wait when every runtime is exhausted")
    r.add_argument("--no-push", action="store_true")
    r.add_argument("task", nargs=argparse.REMAINDER)
    sub.add_parser("doctor")
    sub.add_parser("install").add_argument("dir")
    sub.add_parser("snapshot")
    sub.add_parser("session-start")
    args = ap.parse_args(argv)
    if args.cmd == "run" and args.task[:1] == ["--"]:
        args.task = args.task[1:]
    return {
        "out": cmd_out, "switch": cmd_switch, "accept": cmd_accept, "status": cmd_status,
        "prompt": cmd_prompt, "run": cmd_run, "doctor": cmd_doctor, "install": cmd_install,
        "snapshot": cmd_snapshot, "session-start": cmd_session_start,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
