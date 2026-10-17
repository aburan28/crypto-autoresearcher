#!/usr/bin/env python3
"""Mechanical task cards: the instructions the director tier hands the
mechanical tier, checked by a tool rather than trusted.

`docs/model-tiers.md` is the design. The topology is three hops:

  1. the `experiment-director` (director tier, Sonnet) compiles an approved
     experiment into a runbook that lints clean and a task card that names
     every value the mechanical executor needs;
  2. the main session relays the card to `executor-mechanical` (Haiku) as the
     exact text `prompt` prints -- it adds nothing, so the relay cannot
     introduce a choice the director did not make;
  3. the director assesses the finished session, starting from `check-relay`,
     which establishes without judgment whether the executor's report is the
     tool's output or something the executor wrote itself.

A card is accepted only when it leaves the executor nothing to decide. `lint`
enforces that the same way `tools/runbook.py lint` does for a runbook: every
field present, every path and digest real, no operator-facing word that hands
a choice back (the runbook's own vagueness list), no unfilled placeholder,
and -- for an `EXP-*` card -- a committed approval naming the runbook's exact
bytes. The card adds no authority: an approval it cites is the Coordinator's,
and a card can never make an unapproved runbook runnable.

    python3 tools/task_card.py lint <card.yaml>
    python3 tools/task_card.py prompt <card.yaml>
    python3 tools/task_card.py check-relay <card.yaml> --report <executor-report.txt>

Exit status: 0 clean, 1 findings, 2 the card could not be read.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import runbook as rb  # noqa: E402

SCHEMA = "crypto.autoresearch.mechanical-task-card.v1"
KINDS = ("runbook", "frozen_command")
CARD_ID = re.compile(r"^CARD-[A-Za-z0-9][A-Za-z0-9-]{2,120}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
# Text a mechanical executor would have to fill in itself.
UNFILLED = re.compile(r"<[^<>\n]{1,60}>")
REQUIRED = ("schema", "card_id", "experiment_id", "author_role", "executor_role",
            "kind", "bus_address", "background", "write_scope", "stop_when")


class CardError(Exception):
    """A card that cannot be read at all."""


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
    return rb.rel(repo.resolve(), full), rb.sha256_bytes(raw), doc


def _text(where: str, value: Any) -> list[str]:
    findings = rb._text_findings(where, value, operator_facing=True)
    if isinstance(value, str) and UNFILLED.search(value):
        findings.append(f"{where}: unfilled placeholder {UNFILLED.search(value).group(0)!r}")
    return findings


def _scope_covers(scope: list[str], path: str) -> bool:
    target = PurePosixPath(path)
    for entry in scope:
        base = PurePosixPath(entry.rstrip("/"))
        if target == base or base in target.parents:
            return True
    return False


def _approval_findings(repo: Path, card: dict[str, Any]) -> list[str]:
    """A frozen-command card for an EXP-* names the decision that approved it."""
    decision = card.get("approval_decision")
    if not isinstance(decision, str):
        return ["approval_decision: an EXP-* frozen-command card names its committed approval decision"]
    path = repo / decision
    if not path.is_file() or not rb.committed_bytes_match(repo, decision):
        return [f"approval_decision: {decision} is not a committed file"]
    record = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("coordinator_decision") or {}
    if record.get("decision") != "approve" or card["experiment_id"] not in (record.get("target_ids") or []):
        return [f"approval_decision: {decision} does not approve {card['experiment_id']}"]
    return []


def _runbook_findings(repo: Path, card: dict[str, Any], scope: list[str]) -> list[str]:
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
        elif rb.sha256_file(file) != item.get("sha256"):
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
        shell = sorted(set(argv) & rb.SHELL_TOKENS)
        if shell:
            findings.append(f"{at}.argv: shell syntax {shell}; the command runs without a shell")
        for token in argv:
            if UNFILLED.search(token) or rb.PLACEHOLDER.search(token):
                findings.append(f"{at}.argv: unfilled placeholder in {token!r}")
            if (repo / token).is_file() and token not in bound:
                findings.append(f"{at}.argv: names repository file {token} that binds does not pin")
        timeout = command.get("timeout_seconds")
        if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
            findings.append(f"{at}.timeout_seconds: must be a positive integer")
        codes = command.get("success_exit_codes")
        if not (isinstance(codes, list) and codes and all(isinstance(c, int) for c in codes)):
            findings.append(f"{at}.success_exit_codes: must list the exit codes that mean success")
        for output in command.get("outputs") or []:
            if not _scope_covers(scope, str(output)):
                findings.append(f"{at}.outputs: {output} is outside write_scope")
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
    if not rb.OWNER.match(str(card["bus_address"])):
        findings.append("bus_address: lowercase letters, digits and hyphens")
    if not isinstance(card["background"], bool):
        findings.append("background: true when the budget exceeds ten minutes, else false")
    scope = card["write_scope"]
    if not (isinstance(scope, list) and scope and all(isinstance(s, str) and s for s in scope)):
        findings.append("write_scope: must list at least one path")
        scope = []
    for entry in scope:
        try:
            rb.safe_relative(entry.rstrip("/"))
        except rb.RunbookError as exc:
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


def render_prompt(card_path: str, card_sha: str, card: dict[str, Any], repo: Path = REPO) -> str:
    """The exact dispatch text. Deterministic: same card, same bytes."""
    lines = [
        f"You are executor-mechanical. This is task card {card['card_id']} "
        f"({card_path}, sha256 {card_sha}); tools/task_card.py lint accepted it.",
        "Every value you need is below. Use no other value, run nothing else, and "
        "compute nothing: every number you report is copied from tool output.",
        "",
    ]
    if card["kind"] == "runbook":
        runbook = rb.load_runbook(repo, card["runbook"])
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
        lines += ["Run these commands in this order, each exactly as written, with no shell:"]
        for index, command in enumerate(card["commands"], 1):
            lines.append(f"  {index}. {json.dumps(command['argv'])}  "
                         f"(timeout {command['timeout_seconds']} s; success exit codes "
                         f"{command['success_exit_codes']})")
        lines += ["After each command report its exit code and the last 20 lines of its output, "
                  "verbatim. A command whose exit code is not a success code stops the card: run "
                  "nothing after it."]
    lines += ["", "Write only inside:"] + [f"  - {entry}" for entry in card["write_scope"]]
    lines += ["", "Stop and return `refused`, naming the condition, when:"]
    lines += [f"  - {text}" for text in card["stop_when"]]
    if card.get("notes"):
        lines += ["", f"Note from the director: {card['notes']}"]
    if card["kind"] == "runbook":
        lines += ["", "Return the output of step 7 (`status --brief`) verbatim, and nothing you "
                  "composed yourself."]
    else:
        lines += ["", "Return the exit codes and output lines above verbatim, and nothing you "
                  "composed yourself."]
    return "\n".join(lines) + "\n"


def _normalized(text: str) -> list[str]:
    return [" ".join(line.split()) for line in text.splitlines() if line.strip()]


def check_relay(card: dict[str, Any], report_text: str, repo: Path = REPO) -> dict[str, Any]:
    """Whether the executor's report carries the tool's own output, unedited.

    For a runbook card the reference is `tools/runbook.py status --brief` of
    the card's session, recomputed here from the journal; every one of its
    lines must appear, in order, in the report. A report that paraphrases,
    rounds or reorders is not a relay, whatever it says. The session itself
    must also pass `verify`.
    """
    if card["kind"] != "runbook":
        return {"applicable": False, "reason": "frozen-command cards have no journal to compare against"}
    runbook = rb.load_runbook(repo, card["runbook"])
    session = runbook.session_dir
    result: dict[str, Any] = {"applicable": True, "session_dir": session}
    try:
        expected = _normalized(rb.brief(repo, session))
    except (OSError, rb.RunbookError, IndexError, KeyError, ValueError) as exc:
        result.update(relay_verbatim=False, verify_findings=[f"session unreadable: {exc}"],
                      missing_lines=[])
        return result
    reported = _normalized(report_text)
    position, missing = 0, []
    for line in expected:
        try:
            position = reported.index(line, position) + 1
        except ValueError:
            missing.append(line)
    result["relay_verbatim"] = not missing
    result["missing_lines"] = missing
    result["verify_findings"] = rb.verify(repo, session)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("lint", "prompt"):
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
    clean = not result.get("applicable") or (result["relay_verbatim"] and not result["verify_findings"])
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
