"""When each record entered the repository, read from git history.

The corpus is thin on self-declared time: 1,002 of 1,128 experiment
specifications carry no date field at all, and only 99 of 2,531 run
directories record a timestamp. But every record is committed and immutable
(AGENTS.md rule 2), so git already knows when each one arrived. This module
reads that in ONE pass over history -- about a second on the reference
corpus, warm -- and hands the index two timestamps per path:

    first_commit  the commit that ADDED the file: when the record entered
                  the ledger. For an immutable record this is its real
                  creation time, and it is what the UI shows as "committed".
    last_commit   the most recent commit touching it. For an immutable
                  record these are the same; when they differ the record was
                  amended, superseded in place, or is a goal head, and the
                  UI can say so.

These are DERIVED, not declared. A record's own `recorded_at` is what its
author asserted; this is what the repository observed. The UI labels them
differently for that reason and never presents one as the other.

SHALLOW CLONES ARE REFUSED, deliberately. `actions/checkout` clones depth 1
by default, and under that a single `git log` pass reports every file as
added by the one commit that exists -- 15,000 records all "committed" at
the same instant, which is not a missing value but a WRONG one, and wrong
in a way that looks plausible on a page. `available` is false there and the
UI shows no commit dates at all rather than a uniform fiction.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

# Only the corpus. Narrowing the pathspec is most of why this is fast: the
# repository's history is dominated by coordination and tooling churn that
# no record page ever asks about.
CORPUS_PATHS = ("ledger", "experiments", "knowledge")

# History is walked newest-first, so for any path the first sighting is its
# latest change and the last sighting is the commit that added it.
_LOG_ARGS = (
    "log", "--no-merges", "--format=C%ct", "--name-status",
    "--diff-filter=AM", "--no-renames",
)


@dataclass(slots=True)
class GitDates:
    """First and last commit time per repository-relative path."""

    first: dict[str, int] = field(default_factory=dict)
    last: dict[str, int] = field(default_factory=dict)
    # The same two facts for every ANCESTOR directory, accumulated in the
    # same pass. A run is a directory of artifacts, and answering "when did
    # this run arrive?" by scanning all 37,000 paths per run cost thirteen
    # seconds of the build; folded in here it is a dict lookup.
    dir_first: dict[str, int] = field(default_factory=dict)
    dir_last: dict[str, int] = field(default_factory=dict)
    available: bool = False
    error: str | None = None
    seconds: float = 0.0
    commits: int = 0

    def of(self, path: str) -> tuple[int | None, int | None]:
        """`(committed, last_touched)` for one path, or `(None, None)`.

        A path git has never seen is uncommitted work, not an error: the
        dashboard is often run against a dirty tree.
        """
        if not self.available:
            return None, None
        return self.first.get(path), self.last.get(path)

    def dir_span(self, directory: str) -> tuple[int | None, int | None]:
        """Earliest add and latest change across everything under a directory.

        A run is a DIRECTORY of artifacts, not one file, so its arrival is
        the first commit touching any of them.
        """
        if not self.available:
            return None, None
        key = directory.rstrip("/")
        return self.dir_first.get(key), self.dir_last.get(key)


def _run(repo: Path, *args: str, timeout: int = 180) -> tuple[int, str]:
    try:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                             text=True, timeout=timeout, check=False)
        return out.returncode, out.stdout
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, f"{type(exc).__name__}: {exc}"


def load(repo: Path, paths: tuple[str, ...] = CORPUS_PATHS) -> GitDates:
    """Read commit times for the corpus, or report why they are unavailable."""
    import time

    started = time.time()
    code, shallow = _run(repo, "rev-parse", "--is-shallow-repository", timeout=20)
    if code != 0:
        return GitDates(error="not a git repository, or git is unavailable")
    if shallow.strip() == "true":
        return GitDates(error=(
            "shallow clone: history is truncated, so every record would carry the "
            "same commit time. Fetch full history (actions/checkout fetch-depth: 0) "
            "to show commit dates."))

    code, out = _run(repo, *_LOG_ARGS, "--", *paths)
    if code != 0:
        return GitDates(error="git log failed")

    dates = GitDates(available=True)
    stamp = 0
    for line in out.splitlines():
        if line.startswith("C"):
            try:
                stamp = int(line[1:])
            except ValueError:                        # a commit subject cannot reach here
                continue
            dates.commits += 1
            continue
        if not stamp or "\t" not in line:
            continue
        path = line.split("\t", 1)[1].strip()
        if not path:
            continue
        # Newest-first: the first sighting is the latest change, and every
        # later sighting overwrites `first` until the add is reached.
        dates.last.setdefault(path, stamp)
        dates.first[path] = stamp
        cut = path.rfind("/")
        while cut > 0:
            directory = path[:cut]
            if dates.dir_last.get(directory, 0) < stamp:
                dates.dir_last[directory] = stamp
            known = dates.dir_first.get(directory)
            if known is None or stamp < known:
                dates.dir_first[directory] = stamp
            cut = path.rfind("/", 0, cut)
    dates.seconds = time.time() - started
    if not dates.first:
        return GitDates(error="git history covers none of the corpus paths")
    return dates
