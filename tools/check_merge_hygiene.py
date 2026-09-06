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
import hashlib
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

TRUSTED_GOAL_PREFIXES = ("ledger", "ledger/goals")


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True)


def tracked_files() -> list[str]:
    out = _run("git", "ls-files", "-z").stdout
    return [p for p in out.split("\0")
            if p and not os.path.basename(p).startswith("._")]


def _diff_destination_paths(*arguments: str) -> set[str]:
    """Paths holding the post-image of an A/C/M/R/T diff entry.

    ``--name-status -z`` emits the status, then one path for ordinary entries
    and the source plus destination for copies and renames.  Only destinations
    can hold the candidate object that the scoped checks must inspect.
    """
    result = _run(
        "git", "diff", "--name-status", "-z", "--find-renames",
        "--find-copies", "--diff-filter=ACMRT", *arguments, "--",
    )
    if result.returncode != 0:
        return set()

    fields = result.stdout.split("\0")
    destinations: set[str] = set()
    index = 0
    while index < len(fields) and fields[index]:
        status = fields[index]
        index += 1
        if not status or index >= len(fields):
            break
        if status[0] in {"C", "R"}:
            if index + 1 >= len(fields):
                break
            index += 1  # source path
            destination = fields[index]
            index += 1
        else:
            destination = fields[index]
            index += 1
        if destination:
            destinations.add(destination)
    return destinations


def _index_symlink_paths() -> set[str]:
    """Tracked goal paths whose staged object has Git mode 120000."""
    result = _run(
        "git", "ls-files", "--stage", "-z", "--", "ledger/goals"
    )
    if result.returncode != 0:
        return set()
    symlinks = set()
    for entry in result.stdout.split("\0"):
        if not entry or "\t" not in entry:
            continue
        metadata, path = entry.split("\t", 1)
        mode = metadata.split(" ", 1)[0]
        if mode == "120000":
            symlinks.add(path)
    return symlinks


def _tree_mode(ref: str, path: str) -> str | None:
    """Git mode for one exact path in a committed tree, without checkout."""
    result = _run("git", "ls-tree", "-z", ref, "--", path)
    if result.returncode != 0:
        return None
    for entry in result.stdout.split("\0"):
        if not entry or "\t" not in entry:
            continue
        metadata, candidate = entry.split("\t", 1)
        if candidate == path:
            return metadata.split(" ", 1)[0]
    return None


def _index_mode(path: str) -> str | None:
    """Conceptual index mode for a required prefix, without reading targets.

    Git stores no directory entries in the index.  Descendants therefore prove
    the ordinary tree case; an exact entry is necessarily a file or symlink and
    its real mode is returned.
    """
    result = _run("git", "ls-files", "--stage", "-z", "--", path)
    if result.returncode != 0:
        return None
    descendants = False
    for entry in result.stdout.split("\0"):
        if not entry or "\t" not in entry:
            continue
        metadata, candidate = entry.split("\t", 1)
        if candidate == path:
            return metadata.split(" ", 1)[0]
        if candidate.startswith(path + "/"):
            descendants = True
    return "040000" if descendants else None


def _mode_description(mode: str | None) -> str:
    if mode is None:
        return "missing"
    if mode == "120000":
        return "symlink (Git mode 120000)"
    if mode == "040000":
        return "ordinary directory (Git mode 040000)"
    return f"non-directory Git mode {mode}"


def check_trusted_goal_prefixes() -> list[str]:
    """Prove ledger and ledger/goals are ordinary candidate directories.

    HEAD and index inspection use Git metadata only.  Filesystem inspection is
    component-by-component with lstat, and stops at the first forbidden object,
    so a symlink target is never resolved, opened, globbed, or traversed.
    """
    bad: list[str] = []
    for state, mode_for in (("committed HEAD tree", lambda p: _tree_mode("HEAD", p)),
                            ("staged index", _index_mode)):
        for prefix in TRUSTED_GOAL_PREFIXES:
            mode = mode_for(prefix)
            if mode != "040000":
                bad.append(
                    f"{prefix}: trusted goal prefix in {state} is "
                    f"{_mode_description(mode)}; required ordinary directory "
                    "and target was not read"
                )
                break

    for prefix in TRUSTED_GOAL_PREFIXES:
        full = os.path.join(REPO, *prefix.split("/"))
        try:
            mode = os.lstat(full).st_mode
        except OSError:
            description = "missing"
        else:
            if stat.S_ISLNK(mode):
                description = "symlink"
            elif stat.S_ISDIR(mode):
                continue
            elif stat.S_ISREG(mode):
                description = "regular file"
            else:
                description = "special file"
        bad.append(
            f"{prefix}: trusted goal prefix in tracked worktree/absolute tree "
            f"is {description}; required ordinary directory and target was "
            "not read"
        )
        break
    return bad


def _first_path_component(path: str, candidates: set[str]) -> str | None:
    normalized = path.replace(os.sep, "/")
    if not normalized.startswith("ledger/goals/"):
        return None
    components = normalized.split("/")
    for length in range(3, len(components) + 1):
        component = "/".join(components[:length])
        if component in candidates:
            return component
    return None


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
    """Reject every index or worktree symlink at or below a goal path."""
    bad = []
    index_symlinks = _index_symlink_paths()
    for rel in paths:
        index_component = _first_path_component(rel, index_symlinks)
        component = index_component or goal_symlink_component(rel)
        if component is not None:
            representation = (
                f"traverses symlink {component} in staged index "
                "(object mode 120000)"
                if index_component is not None
                else f"traverses symlink {component}"
            )
            bad.append(
                f"{rel}: tracked goal path {representation}; "
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


def _identical_to_base(path: str, base: str) -> bool:
    """True when the candidate's current content at ``path`` equals ``base``'s.

    Used to exclude a path from the touched-files set when it is provably
    unchanged relative to ``base`` -- the case a merge commit creates for
    every file `main` altered since the branch's last commit, which a plain
    diff against pre-merge HEAD cannot distinguish from a path the branch
    itself edited (see the note on ``touched_files`` below). Compares the
    candidate's committed blob first (covers the ordinary "merged, not
    otherwise touched" case without a filesystem read), then the worktree
    file, so a file also matches when the working tree still holds the
    identical content pre-commit.
    """
    try:
        base_blob = _run("git", "show", f"{base}:{path}")
    except UnicodeDecodeError:
        return False  # binary or non-UTF-8 content: leave the cautious default
    if base_blob.returncode != 0:
        return False  # path does not exist at base: cannot be "unchanged"
    try:
        candidate_blob = _run("git", "show", f":{path}")
    except UnicodeDecodeError:
        candidate_blob = None
    if candidate_blob is not None and candidate_blob.returncode == 0 \
            and candidate_blob.stdout == base_blob.stdout:
        return True
    try:
        with open(os.path.join(REPO, path), encoding="utf-8", errors="surrogateescape") as fh:
            worktree_text = fh.read()
    except OSError:
        return False
    return worktree_text == base_blob.stdout


def touched_files(base: str) -> list[str] | None:
    """Committed, staged, or tracked-worktree candidate destinations.

    Returns None when `base` cannot be resolved, so the caller falls back to the
    absolute sweep rather than silently checking nothing.  Untracked paths are
    intentionally absent until they enter the index.

    MERGE COMMITS. The three diffs below all compare against ``HEAD``, which
    is the branch's PRE-merge tip while a merge is staged but not yet
    committed. For an ordinary content-authoring commit that is exactly the
    right comparison. For a merge, it is not: every file `base` changed since
    the branch's last commit now differs from that stale `HEAD`, even where
    the merge introduced byte-for-byte identical content from `base` with no
    branch-authored change at all. Left uncorrected, that inflates the
    touched set to most of `base`'s own recent history and reintroduces
    exactly the failure mode PR-scoping exists to avoid: blaming a branch for
    breakage that was already on `base` (see the module-level comment above
    `main()`). The fix is narrow: drop any path whose candidate content is
    provably identical to `base`'s own content at that path, since such a
    path cannot carry branch-introduced breakage regardless of why it showed
    up in a HEAD-relative diff.
    """
    if _run("git", "rev-parse", "--verify", "--quiet", base + "^{commit}").returncode:
        return None
    merge_base = _run("git", "merge-base", "HEAD", base).stdout.strip()
    if not merge_base:
        return None
    committed = _diff_destination_paths(merge_base, "HEAD")
    staged = _diff_destination_paths("--cached", "HEAD")
    tracked_worktree = _diff_destination_paths()
    candidates = committed | staged | tracked_worktree
    touched = {p for p in candidates if not _identical_to_base(p, base)}
    return sorted(touched)


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
SCHEMA_SUPERSESSION_REGISTRY = os.path.join(
    REPO, "tools", "schema_supersession_registry.yaml")

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


def _retired_by_supersession() -> dict[str, str]:
    """Records the schema-supersession registry has RETIRED and replaced.

    `tools/schema_supersession_registry.yaml` routes an archived record to a
    complete replacement, pinning the hash of both sides; validate_ledger.py
    already honours it ("91 archived schema record(s) routed to complete
    replacements"). This gate did not, so seven records correctly superseded on
    2026-08-08 -- three P13/SSI specifications, three DEC-20260805 decisions and
    EV-HAWK-af783e -- failed the absolute sweep on every push, and `main` was
    red on all of the last ten merges because of them.

    Neither other route was open. Editing them is what the registry exists to
    forbid: the validator answers an edit with "supersede it instead of editing
    it", and the originals are preserved broken on purpose, immutability working
    as designed. Baselining them is forbidden too -- that file may only ever
    SHRINK, "as records are repaired or superseded", and these are the
    superseded case it names.

    So the exemption is recognition of a retirement that already happened, and
    it verifies that retirement rather than trusting it. An entry exempts its
    record only when the broken original still hashes to the pinned value, the
    replacement exists and hashes to ITS pinned value, and the replacement
    actually parses. Tamper with either side, or lose the replacement, and the
    exemption disappears and the record is reported exactly as before.
    """

    import yaml
    try:
        with open(SCHEMA_SUPERSESSION_REGISTRY, "r", encoding="utf-8") as fh:
            registry = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError):
        return {}
    if not isinstance(registry, dict):
        return {}

    retired: dict[str, str] = {}
    for entry in registry.get("records") or []:
        if not isinstance(entry, dict):
            continue
        old, new = entry.get("superseded_path"), entry.get("superseding_path")
        if not isinstance(old, str) or not isinstance(new, str):
            continue
        if _sha256_of(os.path.join(REPO, old)) != entry.get("superseded_sha256"):
            continue
        new_full = os.path.join(REPO, new)
        if _sha256_of(new_full) != entry.get("superseding_sha256"):
            continue
        try:
            with open(new_full, "r", encoding="utf-8") as fh:
                replacement = fh.read()
            json.loads(replacement) if new.endswith(".json") else yaml.safe_load(replacement)
        except Exception:                                            # noqa: BLE001
            continue
        retired[old] = new
    return retired


def _sha256_of(path: str) -> str | None:
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


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
    retired = _retired_by_supersession()
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
            if rel in retired:
                # Archived, and already replaced by a record that parses. Both
                # halves were hash-verified above, so this is not a hidden
                # defect: it is a defect that was disclosed and superseded.
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
        print(f"note: parseability scoped to {len(scoped)} committed, staged, "
              f"or tracked-worktree candidate path(s) vs {args.base}; the "
              "absolute sweep runs on main",
              file=sys.stderr)

    trusted_prefix_problems = check_trusted_goal_prefixes()
    if trusted_prefix_problems:
        # No later filesystem check may touch ledger: an invalid ledger prefix
        # could redirect every open/glob beneath it. Git-only prefix inspection
        # above is the complete and blocking result for that candidate.
        parse_paths = [p for p in parse_paths
                       if p != "ledger" and not p.startswith("ledger/")]

    groups = [
        ("invalid trusted goal prefixes", trusted_prefix_problems),
        ("symlinked goal paths", check_goal_symlinks(parse_paths)),
        ("unresolved conflict markers", check_markers(parse_paths)),
        ("unparseable records", check_parses(parse_paths,
                                             report_stale=scoped is None)),
    ]
    if args.base and not trusted_prefix_problems:
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
