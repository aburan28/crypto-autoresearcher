#!/usr/bin/env python3
"""Allocate and check research-record identifiers.

Every identifier defect this program has hit came from one of two questions
going unasked at allocation time:

  1. "Is this identifier well-formed?"  Nobody asked. `EXP-RT1476-001`,
     `H-RT1476-001` and `EV-RT1476-001` were authored, approved, executed,
     validated, committed and pushed before `validate_ledger.py` rejected them
     for a digit in the area code (CORR-20260728-001).
  2. "Is it free EVERYWHERE?"  Allocation was done by globbing one directory.
     But `ledger/*.yaml` and the typed subdirectories are ONE identifier space
     in TWO layouts, so globbing either half produced three separate collisions
     in a single day, including a conflict-repair ruling that would itself have
     collided with the record it was repairing (DEC-20260727-005).

This tool asks both, together, before an identifier is used. It is a check and
a suggester -- it writes no records and creates no files.

    python3 tools/allocate_id.py --check EXP-RT1476-001
    python3 tools/allocate_id.py --next hypothesis --area SUBRES
    python3 tools/allocate_id.py --next coordinator_decision --date 20260728
    python3 tools/allocate_id.py --audit

Patterns are imported from `validate_ledger`, never restated, so this tool and
the build gate cannot drift apart. If they disagree, that is the bug.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_ledger as vl  # single source of truth for ID_PATTERNS

REPO = vl.REPO

# Every place a record of a given type may legally live. The union of these is
# the identifier space; no single entry is.
SEARCH_GLOBS = [
    os.path.join(REPO, "ledger", "*.yaml"),            # root, live not legacy
    os.path.join(REPO, "ledger", "*", "*.yaml"),       # typed subdirectories
    os.path.join(REPO, "experiments", "*", "specification.yaml"),
    os.path.join(REPO, "knowledge", "*", "*.md"),
]

# id prefix -> the record type whose pattern governs it
PREFIX_TYPE = {
    "RQ": "research_question",
    "IDEA": "idea",
    "H": "hypothesis",
    "EXP": "experiment",
    "EV": "evidence",
    "DEC": "coordinator_decision",
    "TASK": "handoff",
}

ID_TOKEN = re.compile(r"\b(RQ|IDEA|H|EXP|EV|DEC|TASK|CORR|GOAL|KN|RUN)-[A-Za-z0-9._-]+\b")


def _paths() -> list[str]:
    out: list[str] = []
    for pattern in SEARCH_GLOBS:
        out += [p for p in glob.glob(pattern)
                if not os.path.basename(p).startswith("._")]
    return sorted(set(out))


def occurrences(rec_id: str) -> list[str]:
    """Every file whose NAME carries this identifier, across the whole union."""
    hits = []
    for path in _paths():
        stem = os.path.basename(path)
        parent = os.path.basename(os.path.dirname(path))
        if rec_id in stem or rec_id == parent:
            hits.append(os.path.relpath(path, REPO))
    return hits


def well_formed(rec_id: str) -> tuple[bool, str]:
    """Check an identifier against the build gate's own pattern."""
    prefix = rec_id.split("-", 1)[0]
    rec_type = PREFIX_TYPE.get(prefix)
    if rec_type is None:
        return True, (f"no pattern is enforced for {prefix}-* in "
                      "validate_ledger.ID_PATTERNS; well-formedness NOT checked")
    pattern = vl.ID_PATTERNS[rec_type]
    if pattern.match(rec_id):
        return True, f"matches {rec_type} pattern {pattern.pattern}"
    return False, (f"does NOT match {rec_type} pattern {pattern.pattern} "
                   "-- area codes are letters-only; digits belong in the "
                   "record body, not the identifier")


def check(rec_id: str) -> int:
    ok, why = well_formed(rec_id)
    hits = occurrences(rec_id)
    print(f"identifier: {rec_id}")
    print(f"  well-formed: {'YES' if ok else 'NO'} -- {why}")
    print(f"  occurrences across the union ({len(_paths())} files scanned): "
          f"{len(hits)}")
    for h in hits:
        print(f"    {h}")
    if not ok:
        print("\nREFUSE: malformed. Do not author a record under this id.")
        return 1
    if hits:
        print("\nREFUSE: taken. Allocate above the union maximum; never reuse, "
              "and never fill a gap.")
        return 1
    print("\nOK: well-formed and free across the union.")
    return 0


def _used_numbers(prefix: str, middle: str) -> set[int]:
    pat = re.compile(rf"^{re.escape(prefix)}-{re.escape(middle)}-(\d{{3}})$")
    used: set[int] = set()
    for path in _paths():
        for token in ID_TOKEN.findall(os.path.basename(path)) or []:
            pass
        stem = os.path.splitext(os.path.basename(path))[0]
        m = pat.match(stem)
        if m:
            used.add(int(m.group(1)))
    return used


def next_free(rec_type: str, middle: str) -> int:
    prefix = next(p for p, t in PREFIX_TYPE.items() if t == rec_type)
    candidate = f"{prefix}-{middle}-001"
    ok, why = well_formed(candidate)
    if not ok:
        print(f"REFUSE: {candidate} is malformed -- {why}", file=sys.stderr)
        return 1
    used = _used_numbers(prefix, middle)
    # Strictly above the maximum. Gaps are never filled: their provenance is
    # usually undetermined, and reusing one silently revives a retired record.
    nxt = (max(used) + 1) if used else 1
    rec_id = f"{prefix}-{middle}-{nxt:03d}"
    print(f"next free {rec_type} id for '{middle}': {rec_id}")
    if used:
        gaps = sorted(set(range(1, max(used))) - used)
        print(f"  in use: {len(used)} (max {max(used):03d})")
        if gaps:
            print(f"  gaps NOT reused: {', '.join(f'{g:03d}' for g in gaps)}")
    else:
        print("  in use: none -- this is a new area code")
    return 0


def audit() -> int:
    """Report every malformed or duplicated identifier in the repository."""
    seen: dict[str, list[str]] = {}
    malformed: list[tuple[str, str, str]] = []
    for path in _paths():
        stem = os.path.splitext(os.path.basename(path))[0]
        prefix = stem.split("-", 1)[0]
        if prefix not in PREFIX_TYPE:
            continue
        ok, why = well_formed(stem)
        if not ok:
            malformed.append((stem, os.path.relpath(path, REPO), why))
        seen.setdefault(stem, []).append(os.path.relpath(path, REPO))

    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    print(f"scanned {len(_paths())} record files across the union\n")
    print(f"malformed identifiers: {len(malformed)}")
    for rec_id, path, why in malformed:
        print(f"  {rec_id:24} {path}")
        print(f"      {why}")
    print(f"\nidentifiers occupying more than one path: {len(dupes)}")
    for rec_id, paths in sorted(dupes.items()):
        print(f"  {rec_id:24} {', '.join(paths)}")
    return 1 if (malformed or dupes) else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python3 tools/allocate_id.py",
        description="Check an identifier is well-formed AND free across the "
                    "whole identifier space, or suggest the next free one.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", metavar="ID",
                   help="check one identifier for form and freedom")
    g.add_argument("--next", metavar="TYPE", choices=sorted(set(PREFIX_TYPE.values())),
                   help="suggest the next free id of this record type")
    g.add_argument("--audit", action="store_true",
                   help="report every malformed or doubly-occupied identifier")
    ap.add_argument("--area", help="area code for --next (letters only)")
    ap.add_argument("--date", help="YYYYMMDD for --next on dated record types")
    args = ap.parse_args(argv)

    if args.check:
        return check(args.check)
    if args.audit:
        return audit()
    middle = args.area or args.date
    if not middle:
        ap.error("--next requires --area (for RQ/H/EXP/EV) or --date "
                 "(for IDEA/DEC/TASK)")
    return next_free(args.next, middle)


if __name__ == "__main__":
    raise SystemExit(main())
