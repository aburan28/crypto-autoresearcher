#!/usr/bin/env python3
"""Report which proposals are genuinely unconverted, across every branch tip.

A proposal is CONVERTED when some hypothesis or experiment contract cites its
IDEA id. Answering that question wrongly is expensive in one direction only:
an identifier left unspent costs nothing, while a duplicate hypothesis for an
already-converted proposal is immutable and can only be superseded.

This campaign got the question wrong twice, and each fix widened the search:

  1. Querying only `source_proposal` reported 151 unconverted where 63 were.
     Provenance is also recorded as `derived_from_idea`, and as a bare IDEA id
     inside `source_refs`. Match the id ANYWHERE in the record, not in one
     field -- the records are immutable, so the field cannot be retrofitted.

  2. Querying only the working tree reported 97 unconverted in the ECDLP slice
     where 54 were. N concurrent worktrees each convert proposals on their own
     branch, so a proposal already contracted on an unmerged branch looks open
     to every session but the one that did it. Scan every branch tip.

  3. Counting a proposal as CONVERTED is not the same as counting it as
     dispatchable. A committed correction can retire a proposal outright --
     CORR-20260808-f4d780 marks IDEA-20260808-2e14f7 `do_not_dispatch: true`,
     its mechanism refuted by Burnside -- and a hypothesis converting it
     exists anyway. Such a proposal is neither backlog nor a healthy
     conversion, so it is excluded and reported separately.

The first two mistakes are the same mistake: the audit saw less state than the
writers collectively hold. Widen before you trust a drop in this number.

Usage:
    python3 tools/audit_proposal_backlog.py                 # all questions
    python3 tools/audit_proposal_backlog.py --area ECDLP    # one area
    python3 tools/audit_proposal_backlog.py --question RQ-ECDLP-002 --list
"""
from __future__ import annotations

import argparse
import collections
import glob
import os
import re
import subprocess
import sys

import yaml

IDEA_RE = r"IDEA-[0-9]{8}-[0-9a-zA-Z]{3,6}"
RECORD_GLOBS = ("ledger/hypotheses/*.yaml", "experiments/*/specification.yaml")
# A status that means the proposal will never be contracted, so it is not backlog.
CLOSED_STATUSES = {"rejected", "withdrawn", "superseded", "converted", "closed"}
# git chokes on an argv holding every ref at once, and fails SILENTLY -- it
# reports zero matches rather than an error, which reads exactly like a clean
# backlog. Chunk the refs and never trust a zero from this scan.
REF_CHUNK = 40


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    ).stdout


def referenced_idea_ids() -> set[str]:
    """Every IDEA id cited by any H-*/EXP-* record at any branch tip."""
    refs = sorted(set(_git("for-each-ref", "--format=%(objectname)",
                           "refs/heads", "refs/remotes").split()))
    if not refs:
        print("warning: no branch tips found; falling back to the working tree",
              file=sys.stderr)
        refs = ["HEAD"]
    found: set[str] = set()
    for i in range(0, len(refs), REF_CHUNK):
        out = _git("grep", "-hoE", IDEA_RE, *refs[i:i + REF_CHUNK],
                   "--", *RECORD_GLOBS)
        found.update(out.split())
    return found, len(refs)


def retired_idea_ids() -> set[str]:
    """Proposals a committed correction says must not be dispatched.

    Matched structurally rather than by proximity: the flag must sit in the
    block introduced by the IDEA id, so an id merely mentioned near an
    unrelated retirement is not swept up with it.
    """
    flagged: set[str] = set()
    pattern = re.compile(
        r"(" + IDEA_RE + r"):\s*\n(?:\s+\w+:.*\n){0,6}?\s+do_not_dispatch(?:_as_filed)?:\s*true"
    )
    for path in glob.glob("ledger/corrections/*.yaml"):
        text = open(path, encoding="utf8", errors="replace").read()
        if "do_not_dispatch" not in text:
            continue
        flagged.update(m.group(1) for m in pattern.finditer(text))
    return flagged


def load_proposal(path: str) -> dict:
    try:
        doc = yaml.safe_load(open(path, encoding="utf8", errors="replace")) or {}
    except Exception:
        return {}
    # Some records nest everything under a single top-level key; unwrap it.
    if isinstance(doc, dict) and len(doc) == 1:
        inner = next(iter(doc.values()))
        if isinstance(inner, dict):
            return inner
    return doc if isinstance(doc, dict) else {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--area", help="restrict to question ids containing this token, e.g. ECDLP")
    ap.add_argument("--question", help="restrict to one exact question id")
    ap.add_argument("--list", action="store_true", help="print the unconverted ids")
    args = ap.parse_args()

    referenced, n_refs = referenced_idea_ids()
    retired = retired_idea_ids()
    paths = sorted(glob.glob("ledger/proposals/IDEA-*.yaml"))
    if not paths:
        print("no proposals found; run from the repository root", file=sys.stderr)
        return 2

    by_question: dict[str, list[str]] = collections.defaultdict(list)
    for path in paths:
        pid = os.path.basename(path)[:-5]
        if pid in referenced or pid in retired:
            continue
        doc = load_proposal(path)
        if str(doc.get("status", "")).lower() in CLOSED_STATUSES:
            continue
        by_question[str(doc.get("question_id") or "?")].append(pid)

    present = {os.path.basename(p)[:-5] for p in paths}
    selected = {
        q: v for q, v in by_question.items()
        if (not args.question or q == args.question)
        and (not args.area or args.area in q)
    }

    print(f"branch tips scanned          : {n_refs}")
    print(f"proposals in tree            : {len(paths)}")
    print(f"converted (any branch tip)   : {len(present & referenced)}")
    print(f"retired by a correction      : {len(present & retired)}")
    both = sorted(present & retired & referenced)
    if both:
        print(f"  !! converted DESPITE retirement, needs adjudication: {', '.join(both)}")
    print(f"UNCONVERTED + open           : {sum(len(v) for v in by_question.values())}")
    if args.area or args.question:
        print(f"  ... in scope               : {sum(len(v) for v in selected.values())}")
    print()
    for q, ids in sorted(selected.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(ids):4d}  {q}")
        if args.list:
            for pid in sorted(ids):
                print(f"          {pid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
