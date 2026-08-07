"""Repair the two YAML quoting failures that recur in generated proposals.

Both are ordinary YAML footguns, not content problems:

  1. A list item written as a plain scalar that CONTAINS ": " -- YAML starts
     reading it as a mapping key and then chokes on the continuation line.
     Fix: convert the item to a folded block scalar (`- >-`).
  2. A list item whose text BEGINS with "|" or ">" -- YAML reads the character
     as a block-scalar indicator. In this corpus it is almost always "|Aut|".
     Fix: double-quote the item.

The tool touches only UNPARSEABLE files, only the offending lines, and never
changes wording.

KNOWN COST, recorded rather than hidden: folding a plain list item into a block
scalar preserves the TEXT but not the STRUCTURE. Where an author wrote a
`proof_obligations` entry as a mapping whose value contained ": ", the repaired
file carries a single string "claim: ... responsibility: ..." instead of a
two-key mapping. IDEA-20260807-5f5ace is the known instance (its author flagged
it). The proposal schema is not machine-enforced, so this does not fail
validation, but a consumer that reads proof_obligations as mappings must handle
both shapes. It refuses to run on a file that already parses, and it
verifies the file parses after the edit -- reverting if it does not. Proposals
are pre-commit drafts here; a file that does not parse is not yet a record.

Usage:
    python3 tools/repair_proposal_yaml.py ledger/proposals/IDEA-20260807-*.yaml
"""
from __future__ import annotations

import re
import sys

import yaml

# The lookahead must NOT exclude '|' and '>': those are exactly the two
# characters case 2 exists to fix. Excluding them made the first version of this
# tool skip every item it was written for -- "|Aut| enumerated ..." and
# ">= 8 comparator draws ..." both slipped through untouched. Only real YAML
# node prefixes that we must leave alone are excluded here: quotes, anchors,
# aliases, and tags.
BLOCK_HEADER = re.compile(r"^[|>][-+]?\d?$")
ITEM = re.compile(r"^(\s*)- (?!['\"&*!])(.*\S)\s*$")


def _parses(text: str) -> bool:
    try:
        yaml.safe_load(text)
        return True
    except Exception:
        return False


def repair(text: str) -> tuple[str, list[str]]:
    lines = text.split("\n")
    notes: list[str] = []
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = ITEM.match(line)
        if not m:
            out.append(line)
            i += 1
            continue
        indent, body = m.group(1), m.group(2)

        if body[0] in "|>" and not BLOCK_HEADER.match(body):
            # BLOCK_HEADER guard: "- >-" and "- |" are LEGITIMATE block-scalar
            # headers, and an earlier version of this rule quoted them too,
            # turning every valid folded item in three files into the literal
            # string ">-" followed by an orphaned continuation block. Quote only
            # items that start with | or > and carry other text on the line.
            esc = body.replace('\\', '\\\\').replace('"', '\\"')
            out.append(f'{indent}- "{esc}"')
            notes.append(f"line {i+1}: quoted a list item beginning with "
                         f"{body[0]!r}")
            i += 1
            continue

        # a plain item containing ": " with continuation lines under it
        cont = []
        j = i + 1
        deeper = len(indent) + 2
        while j < len(lines):
            nxt = lines[j]
            if not nxt.strip():
                break
            lead = len(nxt) - len(nxt.lstrip())
            if lead <= len(indent) or nxt.lstrip().startswith("- "):
                break
            cont.append(nxt.strip())
            j += 1
        if ": " in body and cont:
            out.append(f"{indent}- >-")
            for piece in [body] + cont:
                out.append(" " * deeper + piece)
            notes.append(f"line {i+1}: folded a plain list item containing "
                         f"': ' into a block scalar")
            i = j
            continue
        out.append(line)
        i += 1
    return "\n".join(out), notes


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    fixed = failed = clean = 0
    for path in argv:
        original = open(path, encoding="utf-8").read()
        if _parses(original):
            clean += 1
            continue
        repaired, notes = repair(original)
        if not _parses(repaired):
            print(f"UNREPAIRED {path}")
            for n in notes:
                print("   attempted:", n)
            failed += 1
            continue
        open(path, "w", encoding="utf-8").write(repaired)
        print(f"repaired {path}")
        for n in notes:
            print("   ", n)
        fixed += 1
    print(f"\nalready valid: {clean}   repaired: {fixed}   still broken: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
