#!/usr/bin/env python3
"""Frontmatter-parsing audit for claim-class mutual exclusion (R-CC-1).

Supersedes AUDIT-1 and AUDIT-2 in knowledge/TAG-CLAIM-CLASS.md; see
knowledge/TAG-CLAIM-CLASS-v2.md for the full supersession record and the
carried-forward vocabulary (R-CC-1..R-CC-6). AUDIT-1 and AUDIT-2 matched the
`tags:` LINE with regular expressions and were falsified by construction in
VAL-20260808-71bdb1 control_checks C-4 (ledger/evidence/EV-MCE-3d6e9a.yaml
observation O-5b): five legal YAML encodings of the same tag LIST -- a
multi-line flow sequence, quoted flow items, a block sequence with a
trailing comment, a block sequence with quoted items, and tags nested under
a mapping key -- evaded both regexes while parsing to the identical
semantic value under PyYAML. This script tests the PARSED tag LIST, not the
source line, so it is immune to line-wrapping, quoting, block-vs-flow style,
trailing comments, and indentation by construction rather than by patching
each observed evasion.

Usage:
    python3 tools/claim_class_audit.py [root] [--report-skipped]

`root` defaults to `knowledge/` resolved relative to the repository root
(this file's grandparent directory), and may be overridden -- e.g. to run
against tools/fixtures/claim_class_evasions/ for regression testing.

Prints one path per line, to stdout, for every *.md file under root whose
frontmatter's TOP-LEVEL `tags` contains BOTH 'distinguisher' and
'key-recovery' as exact list members. Prints nothing when the scanned tree
is clean. As with AUDIT-1/AUDIT-2 (TAG-CLAIM-CLASS.md section 2), exit
status is not the signal; check stdout, not $?.

Skip handling (never crashes the run on one bad file): a file with no
leading '---' has no frontmatter and is silently out of scope -- most files
under knowledge/ are not frontmatter'd corpus entries (README.md, INDEX.md,
TAG-CLAIM-CLASS.md, the gathers/ notes, ...) and treating that as an error
would make the diagnostic channel useless. A file that OPENS a frontmatter
block (`---`) but cannot be read as one -- no closing `---`, invalid YAML,
or a block that parses to something other than a mapping -- is reported by
path and reason on stderr and then skipped, never allowed to raise out of
the scan loop.

Design note, carried forward explicitly rather than left implicit: unlike
AUDIT-1, this script does NOT drop entries that some other entry's
`supersedes:` field names, or that themselves carry `superseded_by:`.
AUDIT-1's final pipeline stage was supersession-aware and is why it printed
nothing against the corpus's actual 2026-08-08 state even though four
already-superseded entries still literally carry the banned tag pair
(EV-MCE-3d6e9a observation O-5a / VAL-20260808-71bdb1 control_check C-3).
This script reports the literal frontmatter tag state of every live file
and leaves supersession-awareness out of scope: the commissioning task
(TASK-20260809-3e30b8) specifies only the frontmatter/tag-list check, and
BATCH-73a1b7 scope item SUB-2 is where the corpus-wide `superseded_by`
convention is to be settled. Running this script against the real corpus
today WILL print those four legacy paths on stdout; that is documented
behavior, not a defect of this file. See "what this audit does NOT do" in
knowledge/TAG-CLAIM-CLASS-v2.md.
"""
from __future__ import annotations

import argparse
import os
import sys

import yaml

DISTINGUISHER = "distinguisher"
KEY_RECOVERY = "key-recovery"
BANNED_PAIR = {DISTINGUISHER, KEY_RECOVERY}

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ROOT = os.path.join(REPO_ROOT, "knowledge")


def extract_frontmatter(text: str):
    """Return (frontmatter_dict_or_None, error_message_or_None).

    - No leading '---': (None, None) -- not an error, just not a
      frontmatter'd file.
    - Leading '---' with no closing '---': (None, "unterminated ...").
    - Leading '---' whose block is invalid YAML: (None, "YAML parse error: ...").
    - Leading '---' whose block parses to something other than a mapping
      (e.g. a bare list, a scalar): (None, "did not parse to a mapping ...").
    - An empty frontmatter block (`---\\n---\\n`) is valid and yields ({}, None).

    Never raises.
    """
    if not text.startswith("---"):
        return None, None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "opening '---' with no closing '---' (unterminated frontmatter block)"
    block = parts[1]
    try:
        loaded = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        return None, f"YAML parse error: {exc}"
    if loaded is None:
        return {}, None
    if not isinstance(loaded, dict):
        return None, f"frontmatter block did not parse to a mapping (got {type(loaded).__name__})"
    return loaded, None


def tag_set(frontmatter: dict) -> set:
    """The top-level `tags` value as a set of strings. Never raises.

    A missing `tags` key, or one set to null, yields the empty set (R-CC-3:
    silence is permitted). A bare scalar (`tags: distinguisher`) is ONE tag,
    not a list to explode into characters -- `set("distinguisher")` would
    otherwise silently iterate individual letters, which is not the intent
    of "a subset of set(tags)" and was one of the cases this script was
    deliberately tested against (see the GATE-A break-attempt log in the
    execution report). Any list/set item that is not itself a string (a
    nested mapping, a number, a bool) is not a claim-class token and is
    skipped rather than raising.

    `tags` as a YAML `!!set` node (PyYAML's safe constructor turns that into
    an actual Python `set`) is accepted alongside `list`/`tuple`: GATE-A
    found this by construction -- `tags: !!set {distinguisher: null,
    key-recovery: null}` is legal, safely-loadable YAML carrying the exact
    same two members and was MISSED before `set`/`frozenset` were added to
    this check. See the execution report's GATE-A log (case G11) for the
    failing run this fixes.

    `tags` as a MAPPING keyed by the tokens (e.g. `tags: {distinguisher:
    true, key-recovery: true}`, GATE-A case G12) is deliberately NOT treated
    as equivalent and yields the empty set here. This is a disclosed
    boundary, not an oversight: a mapping is not the tags-list shape R-CC-5
    and every real corpus entry use, and "is a key present" vs. "is its
    value truthy" is an ambiguous reading this script does not invent an
    answer for. If this shape is ever found in a real entry it needs a
    human read, not a silent auto-catch. See knowledge/TAG-CLAIM-CLASS-v2.md
    "what this audit does NOT do".
    """
    tags = frontmatter.get("tags")
    if tags is None:
        return set()
    if isinstance(tags, str):
        return {tags}
    if isinstance(tags, (list, tuple, set, frozenset)):
        return {t for t in tags if isinstance(t, str)}
    return set()


def scan(root: str):
    """Walk `root` for *.md files; return (hits, skipped).

    `hits` is a sorted list of paths whose frontmatter tags carry both
    claim-class tokens. `skipped` is a list of (path, reason) pairs for
    files that could not be read or whose frontmatter could not be parsed.
    Both lists are exhaustive -- one bad file never stops the scan.
    """
    hits: list[str] = []
    skipped: list[tuple[str, str]] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in sorted(filenames):
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    text = fh.read()
            except (OSError, UnicodeDecodeError) as exc:
                skipped.append((path, f"read error: {exc}"))
                continue
            frontmatter, err = extract_frontmatter(text)
            if err is not None:
                skipped.append((path, err))
                continue
            if frontmatter is None:
                continue  # no frontmatter at all -- not an error, out of scope
            try:
                tags = tag_set(frontmatter)
            except TypeError as exc:  # belt-and-suspenders; tag_set is designed not to raise
                skipped.append((path, f"unreadable tags value: {exc}"))
                continue
            if BANNED_PAIR <= tags:
                hits.append(path)
    return sorted(hits), skipped


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "root",
        nargs="?",
        default=DEFAULT_ROOT,
        help="root directory to scan (default: knowledge/ at the repo root)",
    )
    parser.add_argument(
        "--report-skipped",
        action="store_true",
        help="also print, to stderr, every skipped file and why",
    )
    args = parser.parse_args(argv)

    hits, skipped = scan(args.root)
    for h in hits:
        print(h)
    if args.report_skipped:
        for path, reason in skipped:
            print(f"SKIPPED: {path}: {reason}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
