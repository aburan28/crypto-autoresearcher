#!/usr/bin/env python3
"""Mechanical task cards: the instructions the director tier hands the
mechanical tier, checked and executed by a tool rather than trusted.

`docs/model-tiers.md` is the design. The topology is three hops:

  1. the `experiment-director` (director tier, Sonnet) compiles a decided
     experiment into a task card that names every value the mechanical
     executor needs: an approved runbook (`kind: runbook`), or a list of
     frozen commands (`kind: frozen_command`);
  2. the main session relays the card to `executor-mechanical` (Haiku) as the
     exact text `prompt` prints -- it adds nothing, so the relay cannot
     introduce a choice the director did not make;
  3. the director assesses the result, starting from `check-relay`, which
     establishes without judgment whether the executor's report is the
     tool's output or something the executor wrote itself.

A card is accepted only when it leaves the executor nothing to decide. `lint`
enforces that: every field present, every path and digest real, no
operator-facing word that hands a choice back, no unfilled placeholder, and --
for an `EXP-*` card -- a committed approval. The card adds no authority: an
approval it cites is the Coordinator's.

A frozen-command card is executed by `run`, never by the model: the tool
checks the pinned commit and every bound digest, runs each argv without a
shell under its timeout, writes stdout and stderr where the card says, and
writes a write-once receipt with every exit code and digest. The executor
runs one command and relays what it prints, exactly as a runbook executor
relays `tools/runbook.py`. So `check-relay` works for both kinds.

ONE FILE, EVERY REPOSITORY. This file is canonical in
aburan28/crypto-autoresearcher and copied byte-identical into the sibling
repositories (crypto, cryptanalysis), so whichever repository's
`executor-mechanical` answers a dispatch, the same card works. It depends only
on PyYAML; `kind: runbook` additionally needs `tools/runbook.py`, which only
crypto-autoresearcher has, and is refused elsewhere. Change it here and copy
it; never edit a copy.

    python3 tools/task_card.py lint <card.yaml>
    python3 tools/task_card.py prompt <card.yaml>
    python3 tools/task_card.py run <card.yaml>            # frozen_command only
    python3 tools/task_card.py check-relay <card.yaml> --report <executor-report.txt>

Exit status: 0 clean / completed, 1 findings, 2 the card could not be read or
`run` refused to start, 3 `run` stopped at a failing command (a result to
report, not a problem to fix).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]

SCHEMA = "crypto.autoresearch.mechanical-task-card.v1"
RECEIPT_SCHEMA = "crypto.autoresearch.task-card-receipt.v1"
KINDS = ("runbook", "frozen_command")
CARD_ID = re.compile(r"^CARD-[A-Za-z0-9][A-Za-z0-9-]{2,120}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
OWNER = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
PLACEHOLDER = re.compile(r"\{([a-z_]+)\}")
SHELL_TOKENS = {"|", "||", "&&", ";", ">", ">>", "<", "&", "2>&1", "2>", "$("}
DENIED_ENV = re.compile(r"^(LD_PRELOAD|LD_LIBRARY_PATH|DYLD_.*|RISC0_DEV_MODE|"
                        r".*(TOKEN|SECRET|PASSWORD|API_KEY|CREDENTIAL).*)$")
# The same list as tools/runbook.py: words that hand a choice back to the
# operator. Kept in step by tests/test_task_card.py where both files exist.
VAGUE = re.compile(
    r"\b(appropriate(ly)?|as needed|if needed|if necessary|when necessary|"
    r"reasonabl[ey]|sensibl[ey]|judge?ment|judge|decide|choose|pick|ideally|"
    r"roughly|approximately|maybe|perhaps|might|consider|try to|feel free|"
    r"as you see fit|use your|whatever|somehow|or similar|something like|"
    r"a few|several|etc|e\.g|tbd|todo|fixme|xxx)\b|\?", re.IGNORECASE)
# Text a mechanical executor would have to fill in itself.
UNFILLED = re.compile(r"<[^<>\n]{1,60}>")
TAIL_LINES = 20
REQUIRED = ("schema", "card_id", "experiment_id", "author_role", "executor_role",
            "kind", "bus_address", "background", "write_scope", "stop_when")


class CardError(Exception):
    """A card that cannot be read at all, or a run that cannot start."""


# ---------------------------------------------------------------------------
# Small utilities (no dependency on tools/runbook.py)
# ---------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        raise CardError(f"{path} is outside the repository {repo}; cards, binds and "
                        f"outputs live inside it") from None


def safe_relative(relative: str) -> str:
    pure = PurePosixPath(relative)
    if not relative or pure.is_absolute() or ".." in pure.parts:
        raise CardError(f"{relative!r} must be a repository-relative path without '..'")
    return pure.as_posix()


def git(repo: Path, *args: str) -> tuple[int, str]:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


def committed_bytes_match(repo: Path, relative: str) -> bool:
    code, blob = git(repo, "rev-parse", f"HEAD:{relative}")
    return code == 0 and git(repo, "hash-object", relative) == (0, blob)


def _runbook_module(repo: Path):
    """`tools/runbook.py`, needed only by `kind: runbook` cards."""
    if not (repo / "tools" / "runbook.py").is_file():
        return None
    sys.path.insert(0, str(repo / "tools"))
    import runbook  # noqa: PLC0415
    return runbook


def load_card(path: str | Path, repo: Path = REPO) -> tuple[str, str, dict[str, Any]]:
    full = Path(path)
    full = (full if full.is_absolute() else repo / full).resolve()
    try:
        raw = full.read_bytes()
    except OSError as exc:
        raise CardError(f"{path}: {exc.strerror}") from None
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise CardError(f"{path}: YAML does not parse: {exc}") from None
    if not isinstance(doc, dict):
        raise CardError(f"{path}: a task card is a mapping")
    return rel(repo, full), sha256_bytes(raw), doc


def _text(where: str, value: Any) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return [f"{where}: must be non-empty text"]
    findings = []
    hits = sorted({m.group(0) for m in VAGUE.finditer(value)})
    if hits:
        findings.append(f"{where}: leaves a choice to the operator "
                        f"({', '.join(repr(h) for h in hits)}); state exactly what happens")
    if UNFILLED.search(value):
        findings.append(f"{where}: unfilled placeholder {UNFILLED.search(value).group(0)!r}")
    return findings


def _scope_covers(scope: list[str], path: str) -> bool:
    target = PurePosixPath(path)
    for entry in scope:
        base = PurePosixPath(entry.rstrip("/"))
        if target == base or base in target.parents:
            return True
    return False


def _in_scope(at: str, scope: list[str], path: Any) -> list[str]:
    if not isinstance(path, str) or not path:
        return [f"{at}: must be a repository-relative path"]
    try:
        safe_relative(path)
    except CardError as exc:
        return [f"{at}: {exc}"]
    return [] if _scope_covers(scope, path) else [f"{at}: {path} is outside write_scope"]


# ---------------------------------------------------------------------------
# Lint
# ---------------------------------------------------------------------------

def _approval_findings(repo: Path, card: dict[str, Any]) -> list[str]:
    """A frozen-command card for an EXP-* names the decision that approved it."""
    decision = card.get("approval_decision")
    if not isinstance(decision, str):
        return ["approval_decision: an EXP-* frozen-command card names its committed approval decision"]
    path = repo / decision
    if not path.is_file() or not committed_bytes_match(repo, decision):
        return [f"approval_decision: {decision} is not a committed file"]
    record = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("coordinator_decision") or {}
    if record.get("decision") != "approve" or card["experiment_id"] not in (record.get("target_ids") or []):
        return [f"approval_decision: {decision} does not approve {card['experiment_id']}"]
    return []


def _runbook_findings(repo: Path, card: dict[str, Any], scope: list[str]) -> list[str]:
    rb = _runbook_module(repo)
    if rb is None:
        return ["kind: runbook cards need tools/runbook.py, which only "
                "crypto-autoresearcher has; use kind: frozen_command here"]
    findings: list[str] = []
    path = card.get("runbook")
    if not isinstance(path, str):
        return ["runbook: a runbook card names the runbook path"]
    if not SHA256.match(str(card.get("runbook_sha256", ""))):
        findings.append("runbook_sha256: must be the runbook's 64-hex sha256")
    try:
        runbook = rb.load_runbook(repo, path)
    except (OSError, rb.RunbookError) as exc:
        return findings + [f"runbook: {exc}"]
    if card.get("runbook_sha256") != runbook.sha256:
        findings.append(f"runbook_sha256: card names {card.get('runbook_sha256')}, "
                        f"the runbook on disk is {runbook.sha256}")
    lint = rb.lint(runbook)
    findings += [f"runbook: does not lint clean: {item}" for item in lint]
    if runbook.experiment_id != card.get("experiment_id"):
        findings.append(f"experiment_id: card names {card.get('experiment_id')}, "
                        f"the runbook is {runbook.experiment_id}")
    if runbook.doc.get("executor_tier") != "mechanical":
        findings.append("runbook: executor_tier must be `mechanical` for a mechanical card")
    for needed in (f"{runbook.base_dir}/runbook-sessions/", f"{runbook.base_dir}/reports/"):
        if not _scope_covers(scope, needed):
            findings.append(f"write_scope: must include {needed}")
    if str(card.get("experiment_id", "")).startswith("EXP-") and not lint:
        if not rb.find_approval(repo, runbook.experiment_id, runbook.sha256):
            findings.append("runbook: no committed approval decision names this experiment "
                            f"and runbook_sha256 {runbook.sha256}")
    return findings


def _command_findings(repo: Path, card: dict[str, Any], scope: list[str]) -> list[str]:
    findings: list[str] = []
    commit = card.get("commit")
    if commit is not None:
        if not COMMIT.match(str(commit)):
            findings.append("commit: must be a full 40-hex commit id")
        elif git(repo, "cat-file", "-e", f"{commit}^{{commit}}")[0] != 0:
            findings.append(f"commit: {commit} is not a commit in this repository")
    findings += _in_scope("receipt", scope, card.get("receipt"))
    binds = card.get("binds") or []
    bound: set[str] = set()
    if not isinstance(binds, list):
        findings.append("binds: must be a list of {path, sha256}")
        binds = []
    for index, item in enumerate(binds):
        at = f"binds[{index}]"
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            findings.append(f"{at}: needs path and sha256")
            continue
        file = repo / item["path"]
        if not file.is_file():
            findings.append(f"{at}: {item['path']} does not exist")
        elif sha256_file(file) != item.get("sha256"):
            findings.append(f"{at}: {item['path']} does not match its sha256")
        bound.add(item["path"])
    commands = card.get("commands")
    if not isinstance(commands, list) or not commands:
        return findings + ["commands: a frozen-command card lists at least one command"]
    for index, command in enumerate(commands):
        at = f"commands[{index}]"
        if not isinstance(command, dict):
            findings.append(f"{at}: must be a mapping")
            continue
        argv = command.get("argv")
        if not (isinstance(argv, list) and argv and all(isinstance(a, str) and a for a in argv)):
            findings.append(f"{at}.argv: must be a non-empty list of strings (no shell string)")
            continue
        shell = sorted(set(argv) & SHELL_TOKENS)
        if shell:
            findings.append(f"{at}.argv: shell syntax {shell}; the command runs without a shell")
        for token in argv:
            if UNFILLED.search(token) or PLACEHOLDER.search(token):
                findings.append(f"{at}.argv: unfilled placeholder in {token!r}")
            if (repo / token).is_file() and token not in bound:
                findings.append(f"{at}.argv: names repository file {token} that binds does not pin")
        timeout = command.get("timeout_seconds")
        if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
            findings.append(f"{at}.timeout_seconds: must be a positive integer")
        codes = command.get("success_exit_codes")
        if not (isinstance(codes, list) and codes and all(isinstance(c, int) for c in codes)):
            findings.append(f"{at}.success_exit_codes: must list the exit codes that mean success")
        for stream in ("stdout", "stderr"):
            if command.get(stream) is not None:
                findings += _in_scope(f"{at}.{stream}", scope, command[stream])
        for output in command.get("outputs") or []:
            findings += _in_scope(f"{at}.outputs", scope, output)
        env = command.get("env") or {}
        if not isinstance(env, dict) or not all(isinstance(k, str) and isinstance(v, str)
                                                for k, v in env.items()):
            findings.append(f"{at}.env: must map names to string values")
        else:
            denied = sorted(k for k in env if DENIED_ENV.match(k))
            if denied:
                findings.append(f"{at}.env: may not set {denied}")
    if str(card.get("experiment_id", "")).startswith("EXP-"):
        findings += _approval_findings(repo, card)
    return findings


def lint(card: dict[str, Any], repo: Path = REPO) -> list[str]:
    """Every way this card could leave the mechanical executor a choice."""
    findings = [f"{key}: required" for key in REQUIRED if key not in card]
    if findings:
        return findings
    if card["schema"] != SCHEMA:
        findings.append(f"schema: must be {SCHEMA}")
    if not CARD_ID.match(str(card["card_id"])):
        findings.append("card_id: must look like CARD-<experiment>-<n>")
    if card["author_role"] != "experiment-director":
        findings.append("author_role: cards are written by experiment-director")
    if card["executor_role"] != "executor-mechanical":
        findings.append("executor_role: cards are executed by executor-mechanical")
    if card["kind"] not in KINDS:
        findings.append(f"kind: must be one of {list(KINDS)}")
    if not OWNER.match(str(card["bus_address"])):
        findings.append("bus_address: lowercase letters, digits and hyphens")
    if not isinstance(card["background"], bool):
        findings.append("background: true when the budget exceeds ten minutes, else false")
    scope = card["write_scope"]
    if not (isinstance(scope, list) and scope and all(isinstance(s, str) and s for s in scope)):
        findings.append("write_scope: must list at least one path")
        scope = []
    for entry in scope:
        try:
            safe_relative(entry.rstrip("/"))
        except CardError as exc:
            findings.append(f"write_scope: {exc}")
    stops = card["stop_when"]
    if not (isinstance(stops, list) and stops):
        findings.append("stop_when: list each condition on which the executor stops and returns `refused`")
        stops = []
    for index, text in enumerate(stops):
        findings += _text(f"stop_when[{index}]", text)
    if card.get("notes") is not None:
        findings += _text("notes", card["notes"])
    if card["kind"] == "runbook":
        findings += _runbook_findings(repo, card, scope)
    elif card["kind"] == "frozen_command":
        findings += _command_findings(repo, card, scope)
    return findings


# ---------------------------------------------------------------------------
# Prompt: the exact dispatch text
# ---------------------------------------------------------------------------

def render_prompt(card_path: str, card_sha: str, card: dict[str, Any], repo: Path = REPO) -> str:
    """Deterministic: same card, same bytes."""
    lines = [
        f"You are executor-mechanical. This is task card {card['card_id']} "
        f"({card_path}, sha256 {card_sha}); tools/task_card.py lint accepted it.",
        "Every value you need is below. Use no other value, run nothing else, and "
        "compute nothing: every number you report is copied from tool output.",
        "",
    ]
    if card["kind"] == "runbook":
        runbook = _runbook_module(repo).load_runbook(repo, card["runbook"])
        lines += [
            'Follow ".claude/agents/executor-mechanical.md", section "Runbook '
            'execution: the procedure", steps 1 to 8, with exactly these values:',
            f"  <runbook> = {card['runbook']}",
            f"  <your bus address> = {card['bus_address']}",
            f"  <session_dir> = {runbook.session_dir}",
            f"  <session id> = {runbook.doc['session_id']}",
            f"  step 2 in the background: {'yes' if card['background'] else 'no'}",
        ]
    else:
        lines += [
            "Run exactly this one command from the repository root, and nothing else:",
            f"  python3 tools/task_card.py run {card_path}",
            f"Run it in the background: {'yes' if card['background'] else 'no'}. "
            "The tool checks the card, runs every command on it and writes the receipt; "
            "you run none of the card's commands yourself.",
            "Exit 0: completed. Exit 3: stopped at a failing command, which is a result "
            "to report. Exit 2: refused to start; return `refused` with the IMPEDIMENT line.",
        ]
    lines += ["", "Write only inside:"] + [f"  - {entry}" for entry in card["write_scope"]]
    lines += ["", "Stop and return `refused`, naming the condition, when:"]
    lines += [f"  - {text}" for text in card["stop_when"]]
    if card.get("notes"):
        lines += ["", f"Note from the director: {card['notes']}"]
    if card["kind"] == "runbook":
        lines += ["", "Return the output of step 7 (`status --brief`) verbatim, and nothing you "
                  "composed yourself."]
    else:
        lines += ["", "Return everything the command printed, verbatim, and nothing you "
                  "composed yourself."]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Run: a frozen-command card, executed and recorded by the tool
# ---------------------------------------------------------------------------

def _tail(data: bytes) -> list[str]:
    return data.decode("utf-8", errors="replace").splitlines()[-TAIL_LINES:]


def _write(repo: Path, relative: str, data: bytes) -> None:
    path = repo / safe_relative(relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def run_card(card_path: str, card_sha: str, card: dict[str, Any], repo: Path = REPO) -> dict[str, Any]:
    """Execute a linted frozen-command card and write its write-once receipt.

    Raises CardError (an impediment: nothing ran, nothing was written) when
    the card is not a frozen-command card, does not lint, names a commit that
    is not HEAD, or already has a receipt.
    """
    if card.get("kind") != "frozen_command":
        raise CardError("run executes frozen_command cards; a runbook card runs through tools/runbook.py")
    findings = lint(card, repo)
    if findings:
        raise CardError("card does not lint: " + "; ".join(findings))
    receipt_path = repo / safe_relative(card["receipt"])
    if receipt_path.exists():
        raise CardError(f"receipt {card['receipt']} already exists; receipts are write-once")
    head = git(repo, "rev-parse", "HEAD")[1]
    if card.get("commit") and card["commit"] != head:
        raise CardError(f"card pins commit {card['commit']}, HEAD is {head}")

    results, status = [], "completed"
    for index, command in enumerate(card["commands"], 1):
        env = dict(os.environ, **(command.get("env") or {}))
        started = time.monotonic()
        try:
            proc = subprocess.run(command["argv"], cwd=repo, env=env, capture_output=True,
                                  timeout=command["timeout_seconds"])
            code, out, err, timed_out = proc.returncode, proc.stdout, proc.stderr, False
        except subprocess.TimeoutExpired as exc:
            code, out, err, timed_out = None, exc.stdout or b"", exc.stderr or b"", True
        except OSError as exc:
            code, out, err, timed_out = None, b"", str(exc).encode(), False
        elapsed = round(time.monotonic() - started, 3)
        for stream, data in (("stdout", out), ("stderr", err)):
            if command.get(stream):
                _write(repo, command[stream], data)
        outputs = {path: (sha256_file(repo / path) if (repo / path).is_file() else None)
                   for path in command.get("outputs") or []}
        ok = (not timed_out) and code in command["success_exit_codes"]
        results.append({"index": index, "argv": command["argv"], "exit_code": code,
                        "timed_out": timed_out, "seconds": elapsed, "succeeded": ok,
                        "stdout_sha256": sha256_bytes(out), "stderr_sha256": sha256_bytes(err),
                        "stdout_tail": _tail(out), "stderr_tail": _tail(err), "outputs": outputs})
        if not ok:
            status = f"stopped at command {index}"
            break
    receipt = {"schema": RECEIPT_SCHEMA, "card_id": card["card_id"], "card_path": card_path,
               "card_sha256": card_sha, "commit": head, "status": status,
               "commands_total": len(card["commands"]), "commands": results}
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def brief(receipt: dict[str, Any], receipt_rel: str, receipt_sha: str) -> str:
    """What `run` prints, derived from the receipt alone, so it can be re-derived."""
    lines = [f"card: {receipt['card_id']} (sha256 {receipt['card_sha256']})",
             f"commit: {receipt['commit']}",
             f"receipt: {receipt_rel} sha256 {receipt_sha}",
             f"status: {receipt['status']}"]
    for item in receipt["commands"]:
        exit_text = "timed out" if item["timed_out"] else f"exit {item['exit_code']}"
        lines.append(f"command {item['index']}: {json.dumps(item['argv'])} {exit_text} "
                     f"({item['seconds']} s) {'succeeded' if item['succeeded'] else 'FAILED'}")
        lines.append(f"  stdout sha256 {item['stdout_sha256']}; last {len(item['stdout_tail'])} lines:")
        lines += [f"    {line}" for line in item["stdout_tail"]]
        if item["stderr_tail"]:
            lines.append(f"  stderr last {len(item['stderr_tail'])} lines:")
            lines += [f"    {line}" for line in item["stderr_tail"]]
        for path, digest in item["outputs"].items():
            lines.append(f"  output {path}: {digest or 'MISSING'}")
    not_run = receipt["commands_total"] - len(receipt["commands"])
    if not_run:
        lines.append(f"not run: {not_run} command(s) after the stop")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Check-relay
# ---------------------------------------------------------------------------

def _normalized(text: str) -> list[str]:
    return [" ".join(line.split()) for line in text.splitlines() if line.strip()]


def _missing(expected: list[str], reported: list[str]) -> list[str]:
    position, missing = 0, []
    for line in expected:
        try:
            position = reported.index(line, position) + 1
        except ValueError:
            missing.append(line)
    return missing


def check_relay(card: dict[str, Any], report_text: str, repo: Path = REPO) -> dict[str, Any]:
    """Whether the executor's report carries the tool's own output, unedited.

    The reference is recomputed from the record, never taken from the
    executor: `tools/runbook.py status --brief` of the session for a runbook
    card, `brief` of the receipt for a frozen-command card. Every reference
    line must appear, in order, in the report; a paraphrased, rounded or
    reordered report is not a relay, whatever it says.
    """
    reported = _normalized(report_text)
    if card["kind"] == "frozen_command":
        receipt_rel = card["receipt"]
        path = repo / safe_relative(receipt_rel)
        result: dict[str, Any] = {"applicable": True, "receipt": receipt_rel}
        if not path.is_file():
            result.update(relay_verbatim=False, missing_lines=[], verify_findings=["no receipt: the card never ran"])
            return result
        receipt = json.loads(path.read_text(encoding="utf-8"))
        missing = _missing(_normalized(brief(receipt, receipt_rel, sha256_file(path))), reported)
        findings = [] if receipt.get("card_id") == card["card_id"] else ["receipt belongs to another card"]
        result.update(relay_verbatim=not missing, missing_lines=missing, verify_findings=findings,
                      status=receipt.get("status"))
        return result
    rb = _runbook_module(repo)
    runbook = rb.load_runbook(repo, card["runbook"])
    session = runbook.session_dir
    result = {"applicable": True, "session_dir": session}
    try:
        expected = _normalized(rb.brief(repo, session))
    except (OSError, rb.RunbookError, IndexError, KeyError, ValueError) as exc:
        result.update(relay_verbatim=False, verify_findings=[f"session unreadable: {exc}"], missing_lines=[])
        return result
    missing = _missing(expected, reported)
    result["relay_verbatim"] = not missing
    result["missing_lines"] = missing
    result["verify_findings"] = rb.verify(repo, session)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("lint", "prompt", "run"):
        sub.add_parser(name).add_argument("card")
    relay = sub.add_parser("check-relay")
    relay.add_argument("card")
    relay.add_argument("--report", required=True, help="the executor's returned text, saved to a file")
    args = parser.parse_args(argv)

    try:
        card_path, card_sha, card = load_card(args.card)
    except CardError as exc:
        print(f"CARD ERROR {exc}")
        return 2
    if args.command == "run":
        try:
            receipt = run_card(card_path, card_sha, card)
        except CardError as exc:
            print(f"IMPEDIMENT {exc}")
            return 2
        receipt_path = REPO / card["receipt"]
        print(brief(receipt, card["receipt"], sha256_file(receipt_path)))
        return 0 if receipt["status"] == "completed" else 3
    findings = lint(card)
    if args.command == "lint" or findings:
        for item in findings:
            print(f"CARD: {item}")
        print(f"CARD {'FAIL' if findings else 'OK'} {card_path} sha256 {card_sha}")
        return 1 if findings else 0
    if args.command == "prompt":
        sys.stdout.write(render_prompt(card_path, card_sha, card))
        return 0
    report = Path(args.report).read_text(encoding="utf-8")
    result = check_relay(card, report)
    print(json.dumps(result, indent=2, sort_keys=True))
    clean = result["relay_verbatim"] and not result["verify_findings"]
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
