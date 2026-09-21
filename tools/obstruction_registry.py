#!/usr/bin/env python3
"""Derive the program's standing set of measured obstructions, and ask of each
one the question its own session was in the worst position to answer.

WHY THIS EXISTS. A negative result's reusable content is the quantity it
measured, not the verdict it reached. The verdict serves the session that wrote
it; the measurement serves every later reader -- who can compare it, re-scope
it, or turn it over. Turning it over is the move this tool is built for: the
same indefiniteness, degree growth, or density defect that kills one approach
is the HYPOTHESIS of another. A form that is indefinite blocks every argument
needing positivity and is the premise of the operator theory built for
indefinite forms; a density that goes negative on part of a range blocks a
global bound and localises where the global bound was the wrong target.

WHY IT IS A TOOL AND NOT A LEDGER FILE. The reversal that matters is usually
not available to the session that measured the obstruction -- it arrives later,
against a theory nobody had in hand at the time, and frequently under a
different goal. A registry committed as state would be one more contended file
saying nothing its sources do not (CLAUDE.md, "Generated artifacts are never
committed"). Derived on demand, it crosses goals for free and cannot go stale.

WHAT IT READS. `obstruction` blocks (`templates/research-records.md`) on
evidence and decision records, and on knowledge-entry frontmatter. `--debt`
inverts the scan: negative-direction evidence carrying NO block at all, which
is the backlog of obstructions recorded as prose before the block existed and
the population most worth mining by hand.

    python3 tools/obstruction_registry.py                 # the standing set
    python3 tools/obstruction_registry.py --unexamined    # never resource-checked
    python3 tools/obstruction_registry.py --debt          # negative results, no block
    python3 tools/obstruction_registry.py --area SEMAEV   # one area
    python3 tools/obstruction_registry.py --json
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directions whose records are expected to carry an obstruction block. A
# `neutral` or `supports` record may carry one (a measurement can block a
# neighbouring approach while supporting its own) but is not chased for it.
NEGATIVE_DIRECTIONS = {"weakens", "contradicts"}

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)


def _load_yaml(path: str):
    try:
        with open(path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except (OSError, yaml.YAMLError):
        return None


def _load_frontmatter(path: str):
    try:
        with open(path, encoding="utf-8") as handle:
            match = FRONTMATTER.match(handle.read())
    except OSError:
        return None
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def _sources() -> list[tuple[str, dict]]:
    """Every record body that could carry an obstruction, with its path.

    Both ledger layouts are read. Top-level `ledger/*.yaml` are frozen legacy
    records and the subdirectories are live; a scan of only one of them
    silently halves the corpus.
    """
    found: list[tuple[str, dict]] = []
    patterns = [
        "ledger/evidence/**/*.yaml",
        "ledger/decisions/**/*.yaml",
        "ledger/EV-*.yaml",
        "ledger/DEC-*.yaml",
    ]
    for pattern in patterns:
        for path in glob.glob(os.path.join(REPO, pattern), recursive=True):
            doc = _load_yaml(path)
            if not isinstance(doc, dict):
                continue
            for key in ("evidence", "coordinator_decision"):
                body = doc.get(key)
                if isinstance(body, dict):
                    found.append((path, body))
    for pattern in ("knowledge/findings/*.md", "knowledge/open-problems/*.md"):
        for path in glob.glob(os.path.join(REPO, pattern)):
            body = _load_frontmatter(path)
            if isinstance(body, dict):
                found.append((path, body))
    return found


def _resource_state(block: dict) -> str:
    """`open`, `checked`, or `spawned` -- what has been done with the reversal."""
    check = block.get("resource_check")
    if not isinstance(check, dict):
        return "open"
    if check.get("spawned_ids"):
        return "spawned"
    if check.get("examined") is True and str(check.get("reading") or "").strip():
        return "checked"
    return "open"


def collect(area: str | None = None) -> list[dict]:
    """Obstruction blocks across the corpus, newest-looking last."""
    entries = []
    for path, body in _sources():
        block = body.get("obstruction")
        if not isinstance(block, dict):
            continue
        record_id = str(body.get("id") or "")
        if area and f"-{area.upper()}-" not in record_id:
            continue
        check = block.get("resource_check")
        check = check if isinstance(check, dict) else {}
        entries.append({
            "record_id": record_id,
            "path": os.path.relpath(path, REPO),
            "statement": block.get("statement"),
            "quantity": block.get("quantity"),
            "value": block.get("value"),
            "scope": block.get("scope"),
            "measured_by": block.get("measured_by") or [],
            "resource_state": _resource_state(block),
            "reading": check.get("reading"),
            "spawned_ids": check.get("spawned_ids") or [],
        })
    entries.sort(key=lambda e: (e["resource_state"] != "open", e["record_id"]))
    return entries


def collect_debt(area: str | None = None) -> list[dict]:
    """Negative evidence carrying no obstruction block.

    These are not errors -- they predate the block. They are the backlog: each
    one reached a verdict whose supporting measurement is somewhere in its runs
    and has never been written down where another goal can read it.
    """
    entries = []
    for path, body in _sources():
        if isinstance(body.get("obstruction"), dict):
            continue
        if body.get("direction") not in NEGATIVE_DIRECTIONS:
            continue
        record_id = str(body.get("id") or "")
        if area and f"-{area.upper()}-" not in record_id:
            continue
        entries.append({
            "record_id": record_id,
            "path": os.path.relpath(path, REPO),
            "direction": body.get("direction"),
            "strength": body.get("strength"),
            "hypothesis_id": body.get("hypothesis_id"),
        })
    entries.sort(key=lambda e: e["record_id"])
    return entries


def _print_registry(entries: list[dict]) -> None:
    if not entries:
        print("no obstruction blocks recorded")
        return
    label = {"open": "UNEXAMINED", "checked": "checked", "spawned": "SPAWNED"}
    for entry in entries:
        print(f"{entry['record_id']}  [{label[entry['resource_state']]}]")
        print(f"  {entry['path']}")
        if entry["statement"]:
            print(f"  blocks:   {entry['statement']}")
        if entry["quantity"] or entry["value"]:
            print(f"  measured: {entry['quantity']} = {entry['value']}")
        if entry["scope"]:
            print(f"  scope:    {entry['scope']}")
        if entry["measured_by"]:
            print(f"  runs:     {', '.join(map(str, entry['measured_by']))}")
        if entry["reading"]:
            print(f"  reading:  {entry['reading']}")
        if entry["spawned_ids"]:
            print(f"  spawned:  {', '.join(map(str, entry['spawned_ids']))}")
        print()
    unexamined = sum(1 for e in entries if e["resource_state"] == "open")
    print(f"{len(entries)} obstruction(s); {unexamined} never resource-checked")
    if unexamined:
        print("For each UNEXAMINED entry, ask which theory takes this "
              "measurement as its hypothesis rather than its refutation. "
              "'None found' is a complete answer; record it in resource_check.")


def _print_debt(entries: list[dict]) -> None:
    if not entries:
        print("every negative-direction record carries an obstruction block")
        return
    for entry in entries:
        print(f"{entry['record_id']}  ({entry['direction']}/{entry['strength']})"
              f"  {entry['path']}")
    print()
    print(f"{len(entries)} negative record(s) with no obstruction block. These "
          f"predate the block and are immutable: supersede with a record that "
          f"measures the obstruction, never edit in place.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--unexamined", action="store_true",
                        help="only obstructions with no resource check")
    parser.add_argument("--debt", action="store_true",
                        help="negative evidence carrying no obstruction block")
    parser.add_argument("--area", help="restrict to one area code, e.g. SEMAEV")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    if args.debt:
        entries = collect_debt(args.area)
        if args.as_json:
            json.dump(entries, sys.stdout, indent=2)
            print()
        else:
            _print_debt(entries)
        return 0

    entries = collect(args.area)
    if args.unexamined:
        entries = [e for e in entries if e["resource_state"] == "open"]
    if args.as_json:
        json.dump(entries, sys.stdout, indent=2)
        print()
    else:
        _print_registry(entries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
