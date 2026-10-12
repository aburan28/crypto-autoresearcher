#!/usr/bin/env python3
"""Fail a sparse CI shard whose tests touch what its checkout left off disk.

validate.yml checks out most test shards sparse (the `harness` exclusions of
tools/sparse_checkout.py). A test that reads an excluded path fails there with
FileNotFoundError, but one that lists a directory, or checks that one exists,
would see less and could pass on less data, silently. So the shard re-creates
every excluded directory that held tracked files, empty: listings above and
existence checks of directories match a full checkout. An audit hook, loaded
into every Python process through
tools/sparse_guard_site/sitecustomize.py, logs any open or listing inside one.
`report` then fails the job and names the test file to move into
.github/test-full-checkout.txt, the files shard 1 runs with a full checkout.

    python3 tools/ci_sparse_guard.py tripwires        # after a sparse checkout
    python3 tools/ci_sparse_guard.py report LOG       # after the tests

The hook is active only when CI_SPARSE_GUARD_ROOT, CI_SPARSE_GUARD_RULES (the
checkout's sparse-checkout file) and CI_SPARSE_GUARD_LOG are all set.
"""
from __future__ import annotations

import fnmatch
import os
import subprocess
import sys
from pathlib import Path

EVENTS = ("open", "os.listdir", "os.scandir", "glob.glob")
FULL_CHECKOUT_LIST = ".github/test-full-checkout.txt"


def exclusions(rules_text: str) -> list[list[str]]:
    """`!/a/*/b/` rules as segment lists. Re-include rules are not used in CI."""
    return [line[2:].strip().strip("/").split("/")
            for line in rules_text.splitlines() if line.startswith("!/")]


def off_disk(rel: str, excluded: list[list[str]]) -> bool:
    """Whether `rel` (a path or a glob pattern) lies inside an excluded directory."""
    parts = rel.strip("/").split("/")
    return any(len(parts) >= len(ex) and
               all(fnmatch.fnmatchcase(p, e) or fnmatch.fnmatchcase(e, p)
                   for p, e in zip(parts, ex))
               for ex in excluded)


def tripwire_dirs(skipped: list[str], excluded: list[list[str]]) -> list[str]:
    """Every excluded directory that held a tracked file, from each exclusion's
    root down to the file's parent: the full checkout's directory skeleton."""
    dirs = set()
    for path in skipped:
        parts = path.split("/")
        for ex in excluded:
            if len(parts) > len(ex) and all(
                    fnmatch.fnmatchcase(p, e) for p, e in zip(parts, ex)):
                dirs.update("/".join(parts[:k]) for k in range(len(ex), len(parts)))
                break
    return sorted(dirs)


def install() -> None:
    root, rules, log = (os.environ.get(k) for k in (
        "CI_SPARSE_GUARD_ROOT", "CI_SPARSE_GUARD_RULES", "CI_SPARSE_GUARD_LOG"))
    if not (root and rules and log):
        return
    excluded = exclusions(Path(rules).read_text())
    prefix = os.path.abspath(root) + os.sep

    def hook(event: str, args: tuple) -> None:
        if event not in EVENTS or not args or isinstance(args[0], int) or args[0] is None:
            return
        try:
            full = os.path.abspath(os.fsdecode(args[0]))
        except (TypeError, ValueError):
            return
        if full.startswith(prefix) and off_disk(full[len(prefix):], excluded):
            test = os.environ.get("PYTEST_CURRENT_TEST", "?").split(" ")[0]
            with open(log, "a", encoding="utf-8") as fh:
                fh.write(f"{test}\t{event}\t{full[len(prefix):]}\n")

    sys.addaudithook(hook)


def _tripwires(repo: Path) -> int:
    rules = subprocess.run(["git", "-C", str(repo), "rev-parse", "--git-path",
                            "info/sparse-checkout"], capture_output=True, text=True,
                           check=True).stdout.strip()
    excluded = exclusions((repo / rules).read_text())
    listing = subprocess.run(["git", "-C", str(repo), "ls-files", "-t"],
                             capture_output=True, text=True, check=True).stdout
    skipped = [line[2:] for line in listing.splitlines() if line.startswith("S ")]
    dirs = tripwire_dirs(skipped, excluded)
    for d in dirs:
        (repo / d).mkdir(parents=True, exist_ok=True)
    print(f"ci_sparse_guard: {len(skipped)} files off disk; {len(dirs)} tripwire directories")
    return 0


def _report(log: Path) -> int:
    lines = log.read_text().splitlines() if log.exists() else []
    if not lines:
        print("ci_sparse_guard: no test touched an off-disk path")
        return 0
    by_file: dict[str, set[str]] = {}
    for line in lines:
        test, _event, path = line.split("\t", 2)
        by_file.setdefault(test.split("::")[0], set()).add(path)
    for test_file, paths in sorted(by_file.items()):
        sample = ", ".join(sorted(paths)[:3]) + (" ..." if len(paths) > 3 else "")
        print(f"::error::{test_file} touched {len(paths)} path(s) a sparse shard leaves "
              f"off disk ({sample}); add it to {FULL_CHECKOUT_LIST}")
    return 1


def main(argv: list[str]) -> int:
    if argv[:1] == ["tripwires"]:
        return _tripwires(Path(argv[1]) if len(argv) > 1 else Path.cwd())
    if argv[:1] == ["report"] and len(argv) == 2:
        return _report(Path(argv[1]))
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
