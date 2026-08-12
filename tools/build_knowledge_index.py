#!/usr/bin/env python3
"""Regenerate knowledge/INDEX.md from entry frontmatter.

The index is a derived artifact: entries under knowledge/{literature,techniques,
findings,open-problems}/ are the source of truth. Run after adding or editing
entries (the /curate-knowledge skill calls this).

Usage:
    python3 tools/build_knowledge_index.py [--check]

--check exits non-zero if INDEX.md is stale (for CI), without rewriting it.
"""
from __future__ import annotations

import glob
import os
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(REPO, "knowledge", "INDEX.md")
SKIP = {"README.md", "SEEDING.md", "INDEX.md"}


def _fmt(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def collect_rows() -> list[tuple[str, ...]]:
    rows = []
    pattern = os.path.join(REPO, "knowledge", "**", "*.md")
    for path in sorted(glob.glob(pattern, recursive=True)):
        if os.path.basename(path) in SKIP:
            continue
        text = open(path, encoding="utf-8").read()
        if not text.startswith("---"):
            continue
        fm = yaml.safe_load(text.split("---", 2)[1]) or {}
        rows.append(
            (
                str(fm.get("id", "")),
                str(fm.get("title", "")),
                str(fm.get("type", "")),
                str(fm.get("confidence", "")),
                _fmt(fm.get("citation_verified", fm.get("status", ""))),
                " ".join(fm.get("tags", []) or []),
            )
        )
    rows.sort(key=lambda r: r[0])
    return rows


def render(rows: list[tuple[str, ...]]) -> str:
    out = [
        "# Knowledge Index",
        "",
        "Generated from entry frontmatter by `tools/build_knowledge_index.py` —",
        "do not hand-edit facts here. Regenerate via `/curate-knowledge`.",
        "",
        f"{len(rows)} entries.",
        "",
        "| ID | Title | Type | Confidence | Verified/Status | Tags |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out) + "\n"


def main() -> int:
    args = sys.argv[1:]

    # --verify-corpus BUILDS the index and throws away the result. It exists
    # because INDEX.md is a GENERATED FILE and is no longer committed: every
    # branch that added a knowledge entry rewrote the whole table, so the file
    # was one of the top conflict paths in the repository while carrying no
    # information the corpus does not already hold.
    #
    # What --check protected was never the file's freshness. It was the BUILDER
    # CRASHING on a corrupt corpus -- that is how conflict markers committed
    # into knowledge/techniques/KN-TECH-056.md went unreported. Building and
    # discarding preserves exactly that, and nothing is lost by dropping the
    # byte comparison against a file that no longer exists.
    if "--verify-corpus" in args:
        render(collect_rows())
        print("knowledge corpus builds cleanly")
        return 0

    content = render(collect_rows())
    if "--check" in args:
        current = open(INDEX, encoding="utf-8").read() if os.path.exists(INDEX) else ""
        if current != content:
            print("knowledge/INDEX.md is stale; run tools/build_knowledge_index.py", file=sys.stderr)
            return 1
        print("knowledge/INDEX.md is up to date")
        return 0
    open(INDEX, "w", encoding="utf-8").write(content)
    print(f"wrote {INDEX} ({content.count(chr(10)) - 9} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
