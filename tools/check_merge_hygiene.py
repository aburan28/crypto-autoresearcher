#!/usr/bin/env python3
"""Refuse the three merge defects that reached main in the PR #55/#58 window.

`validate_ledger.py` is a *relative* gate: CI compares the error set on the head
against the error set on the base and fails only on strings that are new. That
design is right for a corpus with 1138 grandfathered legacy errors, and wrong
for the failures below, each of which slipped past it for its own reason:

  1. CONFLICT MARKERS. Nine files reached main carrying literal `<<<<<<< HEAD`
     lines -- among them two coordinator decisions, two evidence records and
     `knowledge/techniques/KN-TECH-056.md`, which `CLAUDE.md` names as the
     inventor-protocol abstract. Nothing looked for them, so nothing found
     them. A record holding a conflict marker is not a record.

  2. UNPARSEABLE RECORDS MASKING THEMSELVES. A record that does not parse
     cannot be schema-checked, so breaking it *removes* errors. Under a
     relative gate that reads as an improvement. Worse, `EV-SSI-002`'s invalid
     `proof_status` sat undetected on main precisely because the surrounding
     conflict markers made the file unreadable -- the corruption hid a second
     defect. Parseability is therefore absolute here and never baselined.

  3. CROSS-BRANCH ID COLLISIONS. `CLAUDE.md` says to find the next free number
     "by grepping the relevant directory", and `allocate_id.py` does that well
     across the whole identifier space -- but only within one working tree. Two
     branches grepping their own trees concurrently both see the same next free
     number. That is not a mistake either branch can detect: it is a property
     of the pair. `DEC-20260728-004` was allocated twice for unrelated
     decisions this way, and `CORR-20260729-003`/`-004` are live on two open
     PRs right now. Collisions must be found against the *remote*, before the
     merge, while renumbering is still cheap.

Checks 1 and 2 are absolute and offline. Check 3 needs a ref to compare
against and is skipped, loudly, when none is available.

    python3 tools/check_merge_hygiene.py                    # 1 and 2
    python3 tools/check_merge_hygiene.py --base origin/main # 1, 2 and 3

Exits non-zero on any violation, so it can be a pre-commit hook and a CI gate
without a wrapper.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_ledger as vl  # single source of truth for REPO

REPO = vl.REPO

# Only the opening and closing markers are matched. A bare `=======` is a legal
# line in Markdown (setext heading rules) and matching it would make this gate
# fire on the corpus it is meant to protect.
MARKERS = ("<<<<<<< ", ">>>>>>> ", "|||||||")

# Files whose failure to parse is a build-stopping defect. Kept deliberately
# narrow: these are the record types other records resolve references against.
#
# Expressed as (top-level directory, predicate) rather than as globs, because
# `ledger/` holds records at BOTH depths -- 103 frozen root-level records plus
# the typed subdirectories -- and any glob written to catch one silently drops
# the other. That is the same one-layout-of-two blind spot that produced the
# collisions `allocate_id.py` was written to close.
PARSE_RULES = (
    ("ledger", lambda rel: rel.endswith(".yaml")),
    ("experiments", lambda rel: os.path.basename(rel) == "specification.yaml"),
    ("coordination", lambda rel: rel.endswith(".json")),
)

# Identifier-bearing paths, mirroring allocate_id.SEARCH_GLOBS. A file whose
# basename carries a record id is that record; two branches introducing the
# same basename with different content is the collision we are hunting.
ID_DIRS = ("ledger", "experiments", "knowledge")

GOAL_HEAD_PATTERNS = (
    re.compile(r"^ledger/goals/(GOAL-[^/]+)\.yaml$"),
    re.compile(r"^ledger/goals/(GOAL-[^/]+)/goal\.yaml$"),
)


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True)


def tracked_files() -> list[str]:
    out = _run("git", "ls-files", "-z").stdout
    return [p for p in out.split("\0")
            if p and not os.path.basename(p).startswith("._")]


def goal_symlink_component(path: str) -> str | None:
    """First symlink component below ledger/goals, inspected without follow."""
    normalized = path.replace(os.sep, "/")
    if not normalized.startswith("ledger/goals/"):
        return None
    current = REPO
    for component in normalized.split("/"):
        current = os.path.join(current, component)
        try:
            mode = os.lstat(current).st_mode
        except OSError:
            return None
        if stat.S_ISLNK(mode):
            return os.path.relpath(current, REPO).replace(os.sep, "/")
    return None


def check_goal_symlinks(paths: list[str]) -> list[str]:
    """Reject every tracked symlink at or below a goal path."""
    bad = []
    for rel in paths:
        component = goal_symlink_component(rel)
        if component is not None:
            bad.append(
                f"{rel}: tracked goal path traverses symlink {component}; "
                "goal records must be ordinary files and directories and "
                "symlink targets are never read"
            )
    return bad


def goal_id_from_head_path(path: str) -> str | None:
    """Return the semantic GOAL id represented by a flat or sharded head."""
    normalized = path.replace(os.sep, "/")
    for pattern in GOAL_HEAD_PATTERNS:
        match = pattern.match(normalized)
        if match:
            return match.group(1)
    return None


def goal_ids_from_paths(paths: list[str]) -> set[str]:
    return {
        goal_id
        for path in paths
        if (goal_id := goal_id_from_head_path(path)) is not None
    }


def goal_ids_at_ref(ref: str) -> set[str] | None:
    """Semantic goal-head identities in one committed tree."""
    probe = _run("git", "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    if probe.returncode != 0:
        return None
    result = _run("git", "ls-tree", "-r", "--name-only", "-z", ref, "--",
                  "ledger/goals")
    if result.returncode != 0:
        return None
    return goal_ids_from_paths([path for path in result.stdout.split("\0") if path])


def check_prospective_goal_ids(base: str) -> list[str]:
    """Reject only semantic GOAL identities newly introduced after ``base``.

    The candidate set comes from Git's tracked index/worktree view, so a staged
    candidate is checked before commit and a committed candidate is checked in
    CI. Comparing identities, rather than added paths, preserves a legacy goal
    moved from its flat head to the sharded layout.
    """
    base_ids = goal_ids_at_ref(base)
    if base_ids is None:
        return [f"SKIPPED: no such ref {base!r}; prospective GOAL ids unchecked"]
    candidate_ids = goal_ids_from_paths(tracked_files())
    newly_introduced = sorted(candidate_ids - base_ids)
    return [
        f"{goal_id}: newly introduced GOAL identifier does not use the "
        "required random six-hex suffix. Mint new goals with "
        "tools/allocate_id.py --next goal --area AREA; legacy three-digit "
        "identifiers remain valid only when already present on the base."
        for goal_id in newly_introduced
        if not vl.GOAL_RANDOM_ID.fullmatch(goal_id)
    ]


def touched_files(base: str) -> list[str] | None:
    """Tracked files this branch adds or modifies relative to `base`.

    Returns None when `base` cannot be resolved, so the caller falls back to the
    absolute sweep rather than silently checking nothing.
    """
    if _run("git", "rev-parse", "--verify", "--quiet", base + "^{commit}").returncode:
        return None
    merge_base = _run("git", "merge-base", "HEAD", base).stdout.strip()
    if not merge_base:
        return None
    out = _run("git", "diff", "--name-only", "--diff-filter=ACMR", "-z",
               merge_base, "HEAD").stdout
    touched = {p for p in out.split("\0") if p}
    return [p for p in tracked_files() if p in touched]


def check_markers(paths: list[str]) -> list[str]:
    """Any tracked text file carrying an unresolved conflict marker."""
    bad = []
    for rel in paths:
        if goal_symlink_component(rel) is not None:
            continue
        full = os.path.join(REPO, rel)
        try:
            with open(full, "r", encoding="utf-8", errors="strict") as fh:
                for n, line in enumerate(fh, 1):
                    if line.startswith(MARKERS):
                        bad.append(f"{rel}:{n}: unresolved conflict marker "
                                   f"{line.strip()[:32]!r}")
                        break          # one report per file is enough to block
        except (OSError, UnicodeDecodeError):
            continue                   # binary or unreadable: not our business
    return bad


def _wanted(rel: str) -> bool:
    for root, matches in PARSE_RULES:
        if rel.startswith(root + "/") and matches(rel):
            return True
    return False


BASELINE = os.path.join(REPO, "tools", "merge_hygiene_baseline.txt")

BASELINE_HEADER = """\
# Records that already failed to parse when this gate was introduced. One
# repo-relative path per line. These are grandfathered ONLY so the gate could
# be turned on at all; they are defects, not exemptions.
#
# Lines may only ever be REMOVED, as records are repaired or superseded. Adding
# a line to silence a new failure defeats the entire point of the check: the
# masking failure it exists to catch (a broken record reports FEWER schema
# errors than a working one) is exactly what a growing baseline would hide.
"""


def _baseline() -> set[str]:
    try:
        with open(BASELINE, "r", encoding="utf-8") as fh:
            return {ln.strip() for ln in fh
                    if ln.strip() and not ln.startswith("#")}
    except OSError:
        return set()


def check_parses(paths: list[str], *, report_stale: bool = True) -> list[str]:
    """Every ledger/experiment/coordination record must actually load.

    Pre-existing failures are grandfathered by path. Anything else -- a file
    this branch broke, or a new record that never parsed -- is fatal.

    `report_stale` must be False whenever `paths` is a SUBSET of the tracked
    files. A baselined record that simply was not looked at is indistinguishable,
    from inside this function, from one that has been repaired -- so a scoped run
    that reported staleness would advise deleting baseline lines for files it
    never opened, and the baseline is append-forbidden precisely so that it can
    only ever shrink for real reasons.
    """
    import yaml
    grandfathered = _baseline()
    bad, stale = [], set(grandfathered)
    for rel in paths:
        if not _wanted(rel):
            continue
        if goal_symlink_component(rel) is not None:
            continue
        full = os.path.join(REPO, rel)
        try:
            with open(full, "r", encoding="utf-8") as fh:
                text = fh.read()
            if rel.endswith(".json"):
                json.loads(text)
            else:
                yaml.safe_load(text)
        except Exception as exc:
            first = str(exc).strip().splitlines()[0]
            if rel in grandfathered:
                stale.discard(rel)
                continue
            bad.append(f"{rel}: does not parse: {first}")
    if report_stale:
        for rel in sorted(stale):
            print(f"note: {rel} now parses; drop it from "
                  f"tools/merge_hygiene_baseline.txt", file=sys.stderr)
    return bad


def check_collisions(base: str) -> list[str]:
    """Identifiers this branch adds that `base` already spends differently.

    Compared at the merge base, not at the branch point, so a branch that has
    already merged `base` is judged only on what it still introduces.
    """
    probe = _run("git", "rev-parse", "--verify", "--quiet", base + "^{commit}")
    if probe.returncode != 0:
        return [f"SKIPPED: no such ref {base!r}; collisions unchecked"]

    merge_base = _run("git", "merge-base", "HEAD", base).stdout.strip()
    if not merge_base:
        return [f"SKIPPED: no merge base with {base!r}; collisions unchecked"]

    # Files this branch introduced since diverging.
    added = _run("git", "diff", "--name-only", "--diff-filter=A",
                 merge_base, "HEAD").stdout.split("\n")
    added = [p for p in added if p and p.split("/")[0] in ID_DIRS]

    bad = []
    for rel in added:
        if goal_symlink_component(rel) is not None:
            continue
        # Does `base` already have a record under this exact identifier?
        on_base = _run("git", "cat-file", "-e", f"{base}:{rel}")
        if on_base.returncode != 0:
            continue
        theirs = _run("git", "show", f"{base}:{rel}").stdout
        try:
            with open(os.path.join(REPO, rel), "r", encoding="utf-8") as fh:
                ours = fh.read()
        except OSError:
            continue
        if ours != theirs:
            rec = os.path.splitext(os.path.basename(rel))[0]
            bad.append(
                f"{rel}: identifier {rec} is already published on {base} with "
                f"different content. Identifiers are immutable and never "
                f"reused: reissue this record under the next free id "
                f"(tools/allocate_id.py --next ...) and file a CORR recording "
                f"the alias. Do not resolve this by choosing a side.")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", metavar="REF",
                    help="ref to check identifier collisions against, "
                         "e.g. origin/main. Also scopes the conflict-marker and "
                         "parseability sweeps to the files this branch touched, "
                         "unless --absolute is given.")
    ap.add_argument("--absolute", action="store_true",
                    help="sweep every tracked file even when --base is given. "
                         "Used on main and by the scheduled health job, where a "
                         "pre-existing defect is the point rather than noise.")
    args = ap.parse_args()

    paths = tracked_files()

    # SCOPE. The absolute sweep is right on `main` and wrong on a pull request.
    #
    # Parseability must stay absolute SOMEWHERE, for the reason in defect 2 of
    # this file's header: a record that does not parse cannot be schema-checked,
    # so breaking one REMOVES errors and reads as an improvement under the
    # diffed validator. That argument is about a branch MASKING ITS OWN damage,
    # and scoping to the files a branch touched preserves it exactly -- if you
    # broke a record, you changed it, and you are still caught.
    #
    # What the absolute sweep additionally caught was breakage that was ALREADY
    # ON MAIN, and making that every unrelated campaign's problem is a real cost
    # rather than a benefit: six truncated JSON run records from one AES batch
    # red-lighted every other campaign's PR, including one whose diff touched
    # none of them and which could not have repaired them without fabricating
    # run output. With 115 open branches that coupling is the dominant failure.
    #
    # So: PR-scoped here, absolute on push to main (.github/workflows/validate.yml)
    # and on a schedule (.github/workflows/main-health.yml), where the failure
    # reaches the campaign that owns the artifact instead of everyone else.
    scoped = touched_files(args.base) if args.base and not args.absolute else None
    parse_paths = paths if scoped is None else scoped
    if scoped is not None:
        print(f"note: parseability scoped to {len(scoped)} file(s) this branch "
              f"adds or modifies vs {args.base}; the absolute sweep runs on main",
              file=sys.stderr)

    groups = [
        ("symlinked goal paths", check_goal_symlinks(parse_paths)),
        ("unresolved conflict markers", check_markers(parse_paths)),
        ("unparseable records", check_parses(parse_paths,
                                             report_stale=scoped is None)),
    ]
    if args.base:
        groups.append(("identifier collisions", check_collisions(args.base)))
        groups.append(("new legacy GOAL identifiers",
                       check_prospective_goal_ids(args.base)))

    failed = False
    for label, problems in groups:
        real = [p for p in problems if not p.startswith("SKIPPED:")]
        for note in (p for p in problems if p.startswith("SKIPPED:")):
            print(f"note: {note[len('SKIPPED: '):]}", file=sys.stderr)
        if real:
            failed = True
            print(f"FAIL: {len(real)} {label}:", file=sys.stderr)
            for p in real:
                print(f"  - {p}", file=sys.stderr)
            print(file=sys.stderr)

    if failed:
        return 1
    print("PASS: no conflict markers, no unparseable records"
          + (", no identifier collisions, no new legacy GOAL identifiers"
             if args.base else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
