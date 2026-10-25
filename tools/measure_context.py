#!/usr/bin/env python3
"""Measure what this repository's instructions cost each model call, and what they route.

Claude Code sends every skill's and agent's description, and CLAUDE.md, on every
model call of every session. Their cost is easy to grow by accident -- skill
descriptions nearly doubled between 2026-10-10 and 2026-10-22 as skills were
added -- and a shorter description can silently stop routing a request. This
tool measures both, for any git ref, so an instruction change carries its own
before/after numbers instead of an estimate.

    python3 tools/measure_context.py context REF [--against BASE]
    python3 tools/measure_context.py routing REF --against BASE [--runs 2]

`context` builds a config-only copy of REF per file group (empty, CLAUDE.md,
skills, agents, everything), runs one headless turn in each that answers "OK"
with no tool access, and reads the input tokens the runtime itself counted for
that call. A group's cost is its variant minus the empty floor, so the
runtime's own share cancels. Counts are deterministic: repeated runs agree.

`routing` sends each plain-language request in ROUTING_REQUESTS to config-only
copies of REF and BASE and records the first skill or subagent invoked, then
stops the run. It is a regression check, not a benchmark: compare the two
refs' misses, not the totals.

Both call the `claude` CLI and spend real tokens: `context` 5 calls per ref
(about $0.10), `routing` 2 x runs x len(ROUTING_REQUESTS) short calls.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parents[1]
MODEL = os.environ.get("MEASURE_CONTEXT_MODEL", "claude-opus-5-5")

GROUPS = {
    "claude_md": ["CLAUDE.md"],
    "skills": [".claude/skills"],
    "agents": [".claude/agents"],
    "settings": [".claude/settings.json"],
}
VARIANTS = {
    "empty": [],
    "claude_md": ["claude_md"],
    "skills": ["skills"],
    "agents": ["agents"],
    "all": ["claude_md", "skills", "agents", "settings"],
}

# Plain-language requests and the skill or subagent each should reach. Phrased
# the way a user asks, never naming the skill, so a description that stops
# carrying its trigger shows up as a miss.
ROUTING_REQUESTS = [
    ("deep-research", "Looking across the whole portfolio, what experiments should we run next? I want a ranked, justified shortlist."),
    ("research-status", "Give me a quick overview of the program's current state: open questions, what is in flight, recent decisions."),
    ("audit-curve", "Is the elliptic curve secp256k1 weak to any known ECDLP or transfer attack? Do a rigorous audit."),
    ("transfer", "Someone claims that mapping our ECDLP instance into a genus-2 Jacobian through a curve cover makes it easier. Assess that claim."),
    ("agent-bus", "Let the other session working on GOAL-ARGON-001 know that the contract for EXP-ARGON-2608c2 is now frozen."),
    ("consolidate-lanes", "Three sessions are working GOAL-ARGON-001 in parallel. Make sure no two of them are about to spend budget on the same experiment."),
    ("tune-skill", "Use the propose-ideas skill's own track record to suggest an improved version of its instructions."),
    ("curate-knowledge", "Add a literature note to the knowledge corpus for Semaev's paper 'Summation polynomials and the discrete logarithm problem on elliptic curves'."),
    ("propose-ideas", "Start ideation for research question RQ-ECDLP-001: we need fresh falsifiable proposals filed in the ledger."),
    ("coordinate", "Keep the research loop turning: rank the open work, approve what is complete and dispatch what needs doing, but do not run any trials."),
    ("sheriff", "Before this benchmark row goes in the paper, do a deep integrity audit: is this result real?"),
    ("audit-runs", "A Haiku mechanical-tier runbook session just finished. Independently check its journal chain and replay a sample of its trials before we cite it."),
    ("solver", "Our Groebner basis worker's rank certificate looks wrong. Diagnose the solver artifacts."),
    ("ic", "Review the factor-base definition and relation quality metrics in the existing index-calculus artifacts."),
    ("curve", "The EC1 alias of a curve does not match its global curve UID. Sort out the identity mismatch."),
    ("route", "I am new here. Which skill or binary implements the matched-rho cost accounting, and where does that technique live?"),
    ("validator", "The snapshot commit is in. Have an independent subagent verify the run receipts, controls and metrics of EXP-FROB-b8cf21."),
    ("red-team", "Get an independent subagent to challenge the hidden assumptions and omitted end-to-end costs in EXP-FROB-b8cf21's interpretation."),
    ("executor-mechanical", "Delegate to a subagent: re-run the frozen command for EXP-FROB-b8cf21 exactly as specified and collect the declared artifacts. Nothing needs interpreting or debugging."),
    ("idea-synthesist", "GOAL-ARGON-001 has stalled. Have a subagent look across goals, rejected hypotheses and the literature for ideas that come from connections between them."),
    ("experiment-director", "Have the right subagent compile the approved experiment EXP-CSIDH-906d0e into a runbook and a mechanical task card for the Haiku executor."),
]

# A nested `claude` started from inside a session inherits that session's
# identity and plumbing and would attach to it; these are dropped, credentials kept.
NESTED_SESSION_ENV = re.compile(
    r"^(CLAUDECODE|CLAUDE_PID|CLAUDE_CODE_SESSION_ID|CLAUDE_CODE_REMOTE.*|CLAUDE_CODE_MESSAGING_.*"
    r"|CLAUDE_CODE_TEE_SDK_STDOUT|CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2|CLAUDE_CODE_SYNC_.*"
    r"|CLAUDE_CODE_CHILD_SESSION|CLAUDE_CODE_ENTRYPOINT|CLAUDE_CODE_USE_CCR_V2|CLAUDE_CODE_WORKER_EPOCH"
    r"|CLAUDE_SESSION_INGRESS_TOKEN_FILE|CLAUDE_ADDITIONAL_DIRECTORIES"
    r"|CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD|CLAUDE_AFTER_LAST_COMPACT"
    r"|CLAUDE_AUTOCOMPACT_PCT_OVERRIDE|CLAUDE_CODE_DIAGNOSTICS_FILE|CLAUDE_CODE_DEBUG|CCR_.*"
    r"|CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION|CLAUDE_CODE_ARTIFACT_ASSETS|CLAUDE_CODE_BG_.*"
    r"|CLAUDE_AUTO_BACKGROUND_TASKS|CLAUDE_CODE_SESSION_ATTENDED|CLAUDE_ENABLE_STREAM_WATCHDOG"
    r"|CLAUDE_EFFORT|AI_AGENT)$")
BASE_FLAGS = ["--model", MODEL, "--no-session-persistence", "--strict-mcp-config",
              "--settings", '{"disableAllHooks": true}']

Runner = Callable[[list[str], Path], str]


def clean_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if not NESTED_SESSION_ENV.match(k)}


def run_claude(args: list[str], cwd: Path) -> str:
    proc = subprocess.run(["claude", *args], cwd=cwd, env=clean_env(), stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=600)
    return proc.stdout


def export(ref: str, dest: Path, paths: list[str], repo: Path = REPO) -> None:
    """Write `paths` (files or directories) as they are at `ref` into `dest`, a fresh git repo."""
    dest.mkdir(parents=True, exist_ok=True)
    for path in paths:
        names = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", ref, "--", path],
                               capture_output=True, text=True, check=True).stdout.split()
        for name in names:
            blob = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{name}"],
                                  capture_output=True, check=True).stdout
            (dest / name).parent.mkdir(parents=True, exist_ok=True)
            (dest / name).write_bytes(blob)
    subprocess.run(["git", "init", "-q", str(dest)], check=True)


def input_tokens(output: str) -> int:
    """Every input token of the call, cached or not, from a `--output-format json` result."""
    usage = json.loads(output).get("usage") or {}
    total = sum(int(usage.get(k) or 0) for k in
                ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    if total <= 0:
        raise ValueError(f"no input-token usage in the result: {output[:200]}")
    return total


def context(ref: str, run: Runner = run_claude, repo: Path = REPO) -> dict[str, int]:
    """Input tokens per call for each variant of `ref`."""
    tokens = {}
    with tempfile.TemporaryDirectory(prefix="measure-context-") as tmp:
        for name, groups in VARIANTS.items():
            directory = Path(tmp) / name
            export(ref, directory, [p for g in groups for p in GROUPS[g]], repo)
            tokens[name] = input_tokens(run(
                ["-p", "Reply with the single word OK.", "--output-format", "json",
                 "--session-id", str(uuid.uuid4()), "--max-turns", "1", *BASE_FLAGS,
                 "--disallowedTools", "Bash", "Edit", "Write", "Read", "Grep", "Glob",
                 "WebFetch", "WebSearch"], directory))
    return tokens


def attribution(tokens: dict[str, int]) -> dict[str, int]:
    """Each group's tokens over the empty floor (the runtime's own share)."""
    floor = tokens["empty"]
    return {name: tokens[name] - floor for name in tokens if name != "empty"} | {"runtime": floor}


def chosen_route(stream: str) -> str:
    """The first skill or subagent a `stream-json` transcript invokes, or 'none'."""
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        message = event.get("message")
        for part in (message.get("content") or []) if isinstance(message, dict) else []:
            if isinstance(part, dict) and part.get("type") == "tool_use" \
                    and part.get("name") in ("Skill", "Agent", "Task"):
                inp = part.get("input") or {}
                name = inp.get("skill") or inp.get("command") or inp.get("subagent_type") or "none"
                return str(name).lstrip("/").split()[0]
    return "none"


def run_route(args: list[str], cwd: Path) -> str:
    """Stream until the first Skill/Agent call, then stop: the route is all we need."""
    proc = subprocess.Popen(["claude", *args], cwd=cwd, env=clean_env(), stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    seen = []
    try:
        for line in proc.stdout:
            seen.append(line)
            if chosen_route(line) != "none" or '"type":"result"' in line.replace(" ", ""):
                break
    finally:
        proc.kill()
        proc.wait()
    return "".join(seen)


def routing(ref: str, base: str, runs: int = 2, run: Runner = run_route,
            repo: Path = REPO, workers: int = 6) -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="measure-routing-") as tmp:
        arms = {}
        for label, r in (("base", base), ("ref", ref)):
            arms[label] = Path(tmp) / label
            export(r, arms[label], [p for g in VARIANTS["all"] for p in GROUPS[g]], repo)

        def one(job: tuple[str, str, str]) -> dict:
            label, expect, prompt = job
            stream = run(["-p", prompt, "--output-format", "stream-json", "--verbose",
                          "--session-id", str(uuid.uuid4()), "--max-turns", "3", *BASE_FLAGS,
                          "--allowedTools", "Skill", "Agent", "Task",
                          "--disallowedTools", "Bash", "Edit", "Write", "WebFetch", "WebSearch"],
                         arms[label])
            got = chosen_route(stream)
            return {"arm": label, "expect": expect, "chosen": got, "ok": got == expect}

        jobs = [(label, e, p) for _ in range(runs) for label in arms for e, p in ROUTING_REQUESTS]
        with cf.ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(one, jobs))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("context", help="input tokens each call carries, by file group")
    p.add_argument("ref", nargs="?", default="HEAD")
    p.add_argument("--against", help="a second ref to compare with")
    p = sub.add_parser("routing", help="first skill/subagent each request reaches, REF vs BASE")
    p.add_argument("ref", nargs="?", default="HEAD")
    p.add_argument("--against", required=True)
    p.add_argument("--runs", type=int, default=2)
    p.add_argument("--json", action="store_true", help="print every routed request")
    args = parser.parse_args(argv)
    if shutil.which("claude") is None:
        parser.error("needs the `claude` CLI on PATH")

    if args.command == "context":
        refs = [r for r in (args.against, args.ref) if r]
        rows = {r: attribution(context(r)) for r in refs}
        print(f"{'tokens per call':24}" + "".join(f"{r[:14]:>16}" for r in refs)
              + (f"{'change':>10}" if len(refs) == 2 else ""))
        for group in ("runtime", "claude_md", "skills", "agents", "all"):
            vals = [rows[r][group] for r in refs]
            label = "all (repo total)" if group == "all" else group
            print(f"{label:24}" + "".join(f"{v:>16,}" for v in vals)
                  + (f"{vals[1] - vals[0]:>+10,}" if len(vals) == 2 else ""))
        return 0

    rows = routing(args.ref, args.against, args.runs)
    if args.json:
        print(json.dumps(rows, indent=1))
    for label in ("base", "ref"):
        mine = [r for r in rows if r["arm"] == label]
        print(f"{label}: {sum(r['ok'] for r in mine)}/{len(mine)} routed as expected")
    for expect, _prompt in ROUTING_REQUESTS:
        got = {label: sorted(r["chosen"] for r in rows if r["arm"] == label and r["expect"] == expect)
               for label in ("base", "ref")}
        if got["base"] != got["ref"]:   # with few runs, one "none" is noise: re-run before concluding
            print(f"  differs  {expect:22} base={','.join(got['base'])}  ref={','.join(got['ref'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
