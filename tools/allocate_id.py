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
    python3 tools/allocate_id.py --next hypothesis --area SUBRES   # random token
    python3 tools/allocate_id.py --next coordinator_decision --date 20260728
    python3 tools/allocate_id.py --next correction --date 20260728
    python3 tools/allocate_id.py --audit

Ledger patterns and the shared suffix grammar are imported from
`validate_ledger`, so this tool and the build gate cannot silently disagree on
legacy or random suffixes.
"""
from __future__ import annotations

import argparse
import glob
import random
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
    # Persistent goals support both a flat head and a sharded head whose
    # identifier is carried by its parent directory.
    os.path.join(REPO, "ledger", "goals", "*", "goal.yaml"),
    os.path.join(REPO, "ledger", "corrections", "*.md"),
    os.path.join(REPO, "experiments", "*", "specification.yaml"),
    os.path.join(REPO, "experiments", "*", "corrections", "*.yaml"),
    os.path.join(REPO, "experiments", "*", "corrections", "*.md"),
    os.path.join(REPO, "knowledge", "*", "*.md"),
    # Batch directories. Their identifier lives in the directory name; the
    # recursive collision index below sees the directory itself.
    os.path.join(REPO, "coordination", "goals", "*", "batches", "*", "*.json"),
    # Control-plane corrections may live inside a batch rather than the ledger.
    # They remain part of the same global CORR identifier space.
    os.path.join(REPO, "coordination", "goals", "*", "batches", "*",
                 "corrections", "*.yaml"),
    os.path.join(REPO, "coordination", "goals", "*", "batches", "*",
                 "corrections", "*.md"),
]

# id prefix -> the record type whose pattern governs it
PREFIX_TYPE = {
    "GOAL": "goal",
    "RQ": "research_question",
    "IDEA": "idea",
    "H": "hypothesis",
    "EXP": "experiment",
    "EV": "evidence",
    "DEC": "coordinator_decision",
    "TASK": "handoff",
    "BATCH": "batch",
    "CORR": "correction",
}

# Record types whose identifier is PREFIX-SUFFIX with no date or area segment.
NO_MIDDLE = {"batch"}
SEQUENTIAL_FORBIDDEN = {"goal"}


# Corrections are coordination/control-plane records rather than one of the
# ledger record types validated by validate_ledger.check_record, so
# validate_ledger.ID_PATTERNS has no "correction" entry. Reuse the validator's
# canonical legacy-or-random suffix expression instead of copying it.
SUPPLEMENTAL_ID_PATTERNS = {
    "correction": re.compile(rf"^CORR-\d{{8}}-{vl.SUFFIX}$"),
}

# SEARCH_GLOBS remains the curated set used by audit(): broadening that audit
# to every task receipt and archive path would count one logical task once per
# artifact and manufacture a large new duplicate-debt baseline. Allocation has
# a different requirement. An identifier is not free if it appears in ANY
# repository path component, including a deep task directory or task-card
# filename, so occurrences() uses this recursive path index instead.
PATH_SCAN_EXCLUDED_DIRS = {
    ".git",
    ".worktrees",  # other checkouts are not records in this checkout
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
}
PATH_SCAN_EXCLUDED_FILES = {".git", ".DS_Store"}
PATH_ID_PREFIX = re.compile(
    rf"^(?:{'|'.join(map(re.escape, PREFIX_TYPE))})-"
)


def _paths() -> list[str]:
    """Curated canonical record files used by the legacy-debt audit."""
    out: list[str] = []
    for pattern in SEARCH_GLOBS:
        out += [p for p in glob.glob(pattern)
                if not os.path.basename(p).startswith("._")]
    return sorted(set(out))


def _identifier_paths() -> list[str]:
    """Identifier-bearing files and directories anywhere in this checkout.

    This deliberately inspects path components only; it never parses or scans
    file contents. Directories are included because TASK, EXP, BATCH, and other
    records often carry their identifier in a parent directory while their
    artifacts have generic names such as receipt.json.
    """
    out: list[str] = []
    for current, directories, files in os.walk(REPO, followlinks=False):
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in PATH_SCAN_EXCLUDED_DIRS
            and not directory.startswith("._")
        )
        for directory in directories:
            if PATH_ID_PREFIX.match(directory):
                out.append(os.path.join(current, directory))
        for filename in sorted(files):
            if (filename in PATH_SCAN_EXCLUDED_FILES
                    or filename.startswith("._")):
                continue
            if PATH_ID_PREFIX.match(filename):
                out.append(os.path.join(current, filename))
    return sorted(set(out))


def _path_names_identifier(path: str, rec_id: str) -> bool:
    """Whether one identifier-bearing path component names rec_id."""
    name = os.path.basename(path)
    stem = os.path.splitext(name)[0]
    if name == rec_id or stem == rec_id:
        return True
    # Task cards and receipts sometimes append a descriptive suffix. Require a
    # delimiter so TASK-...-001 never matches the distinct TASK-...-0010.
    return any(stem.startswith(rec_id + delimiter)
               for delimiter in (".", "_", "-"))


def occurrences(rec_id: str) -> list[str]:
    """Every repository path component that carries this identifier."""
    return [
        os.path.relpath(path, REPO)
        for path in _identifier_paths()
        if _path_names_identifier(path, rec_id)
    ]


def _record_identifier(path: str) -> str:
    """Return the canonical record identifier carried by a curated path."""
    rel = os.path.relpath(path, REPO).replace(os.sep, "/")
    sharded_goal = re.match(r"^ledger/goals/(GOAL-[^/]+)/goal\.yaml$", rel)
    if sharded_goal:
        return sharded_goal.group(1)
    return os.path.splitext(os.path.basename(path))[0]


def well_formed(rec_id: str) -> tuple[bool, str]:
    """Check an identifier against the build gate's own pattern."""
    prefix = rec_id.split("-", 1)[0]
    rec_type = PREFIX_TYPE.get(prefix)
    if rec_type is None:
        return True, (f"no pattern is enforced for {prefix}-* in "
                      "validate_ledger.ID_PATTERNS; well-formedness NOT checked")
    pattern = vl.ID_PATTERNS.get(rec_type) or SUPPLEMENTAL_ID_PATTERNS[rec_type]
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
    print(f"  occurrences across the union "
          f"({len(_identifier_paths())} identifier-bearing paths scanned): "
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
    for path in _identifier_paths():
        stem = _record_identifier(path)
        m = pat.match(stem)
        if m:
            used.add(int(m.group(1)))
    return used


TOKEN_WIDTH = 6  # hex chars; 16**6 = 16_777_216 values per namespace


def random_token(rng: random.Random | random.SystemRandom,
                 width: int = TOKEN_WIDTH) -> str:
    """A random hex suffix. NO STATE IS SCANNED, WHICH IS THE ENTIRE POINT.

    Sequential allocation asks "what is the maximum in committed state, plus
    one". Every concurrent worktree asks the same question of the same state and
    gets the same answer, so they mint the same identifier for different records
    and only discover it at merge time -- when both records are immutable and
    neither can be renamed without breaking whatever archive binds it.

    A random token has no such question to ask. Two worktrees collide only by
    drawing the same value out of 16**6, which is why this is the default.
    """
    return "".join(rng.choice("0123456789abcdef") for _ in range(width))


def token_id(rec_type: str, middle: str, *, seed: int | None = None) -> int:
    """Mint a random-token identifier and verify it against the build gate."""
    prefix = next((p for p, t in PREFIX_TYPE.items() if t == rec_type), None)
    if prefix is None:
        print(f"REFUSE: no prefix is registered for {rec_type}", file=sys.stderr)
        return 1
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    for _ in range(64):  # bounded; a hit is overwhelmingly improbable
        token = random_token(rng)
        rec_id = (f"{prefix}-{token}" if rec_type in NO_MIDDLE
                  else f"{prefix}-{middle}-{token}")
        ok, why = well_formed(rec_id)
        if not ok:
            print(f"REFUSE: {rec_id} is malformed -- {why}", file=sys.stderr)
            return 1
        if not occurrences(rec_id):
            label = rec_type if rec_type in NO_MIDDLE else f"{rec_type} id for '{middle}'"
            print(f"free {label}: {rec_id}")
            print(f"  allocation: random {TOKEN_WIDTH}-hex token "
                  f"(1 of {16 ** TOKEN_WIDTH:,} per namespace; no state scanned)")
            print("  VERIFY BEFORE USE: python3 tools/allocate_id.py --check "
                  + rec_id)
            return 0
    print("REFUSE: could not find a free token in 64 draws; that is so unlikely "
          "it indicates a defect in the search path, not exhaustion",
          file=sys.stderr)
    return 1


def next_free(rec_type: str, middle: str) -> int:
    """LEGACY three-digit allocation. Kept for single-worktree use only.

    Returns max+1, which is exactly why it collides: every concurrent worktree
    computes it from the same committed state and gets the same answer. Never
    use it to mint a record that will be merged; use token_id instead.
    """
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
    print("  allocation: sequential (max+1) -- COLLIDES ACROSS CONCURRENT "
          "WORKTREES; prefer the default random token")
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
        stem = _record_identifier(path)
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
    ap.add_argument("--sequential", action="store_true",
                    help="legacy 3-digit suffix as max+1. COLLIDES ACROSS "
                         "CONCURRENT WORKTREES -- never use it to mint a record "
                         "that will be merged.")
    ap.add_argument("--seed", type=int, default=None,
                    help="seed the random allocator (tests and reproduction only)")
    args = ap.parse_args(argv)

    if args.check:
        return check(args.check)
    if args.audit:
        return audit()
    middle = args.area or args.date
    if not middle and args.next not in NO_MIDDLE:
        ap.error("--next requires --area (for GOAL/RQ/H/EXP/EV) or --date "
                 "(for IDEA/DEC/TASK/CORR); batch takes neither")
    if args.sequential:
        if args.next in SEQUENTIAL_FORBIDDEN:
            print("REFUSE: sequential GOAL allocation is prohibited; new goals "
                  "must use the default random 6-hex token", file=sys.stderr)
            return 1
        return next_free(args.next, middle)
    return token_id(args.next, middle, seed=args.seed)


if __name__ == "__main__":
    raise SystemExit(main())
