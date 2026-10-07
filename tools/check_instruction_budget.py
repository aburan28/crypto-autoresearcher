#!/usr/bin/env python3
"""Word budgets for the instruction a session reads before it acts.

`docs/track-record-review-20261006.md` (P1.6) measured the always-loaded
contract at 12,146 words -- more than the longest skill, read by every session
before it did anything -- and set two budgets:

  * ALWAYS_LOADED: AGENTS.md + CLAUDE.md, loaded by every runtime on every
    wake, at most 4,000 words.
  * WAKE: the always-loaded set plus the one skill or agent contract a session
    actually runs, at most 7,000 words. Checked for every skill under
    .claude/skills and every generated agent under .claude/agents, since a
    session loads one of each at most.

Budgets are on words (`str.split`), the same number `wc -w` prints, so a
reader can verify a failure with one command. A failure names the file and
the overrun; the fix is to move narrative to docs/ and link it, never to
raise the budget to match what was just written -- a budget moved to turn a
red check green has stopped being a check. Raising one is a reviewed change
to this file with the reason in the commit.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

ALWAYS_LOADED = ("AGENTS.md", "CLAUDE.md")
ALWAYS_LOADED_BUDGET = 4_000
WAKE_BUDGET = 7_000
SKILL_GLOB = ".claude/skills/*/SKILL.md"
AGENT_GLOB = ".claude/agents/*.md"


def words(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def measure(repo: Path = REPO) -> dict:
    always = {name: words(repo / name) for name in ALWAYS_LOADED
              if (repo / name).is_file()}
    base = sum(always.values())
    wakes = {}
    for pattern in (SKILL_GLOB, AGENT_GLOB):
        for path in sorted(repo.glob(pattern)):
            rel = str(path.relative_to(repo))
            wakes[rel] = {"own": words(path), "wake": base + words(path)}
    return {"always_loaded": always, "always_loaded_total": base,
            "always_loaded_budget": ALWAYS_LOADED_BUDGET,
            "wake_budget": WAKE_BUDGET, "wakes": wakes}


def failures(report: dict) -> list[str]:
    out = []
    total = report["always_loaded_total"]
    if total > report["always_loaded_budget"]:
        parts = ", ".join(f"{k} {v}" for k, v in report["always_loaded"].items())
        out.append(f"always-loaded instruction is {total} words "
                   f"(budget {report['always_loaded_budget']}): {parts}")
    for rel, m in report["wakes"].items():
        if m["wake"] > report["wake_budget"]:
            out.append(f"{rel}: wake is {m['wake']} words "
                       f"({m['own']} own + {total} always loaded; "
                       f"budget {report['wake_budget']})")
    return out


def render(report: dict) -> str:
    lines = [f"always loaded: {report['always_loaded_total']} / "
             f"{report['always_loaded_budget']} words"]
    for name, n in report["always_loaded"].items():
        lines.append(f"  {n:>6}  {name}")
    lines.append(f"wake budget: {report['wake_budget']} words "
                 f"(own + always loaded)")
    for rel, m in sorted(report["wakes"].items(), key=lambda kv: -kv[1]["wake"]):
        lines.append(f"  {m['wake']:>6}  {m['own']:>5} own  {rel}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", type=Path, default=REPO)
    ap.add_argument("--list", action="store_true",
                    help="print every measured file, largest wake first")
    args = ap.parse_args(argv)
    report = measure(args.repo_root)
    bad = failures(report)
    if args.list or bad:
        print(render(report))
    for msg in bad:
        print(f"FAIL: {msg}", file=sys.stderr)
    if not bad:
        print(f"OK: always loaded {report['always_loaded_total']} words, "
              f"largest wake {max((m['wake'] for m in report['wakes'].values()), default=0)} words")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
