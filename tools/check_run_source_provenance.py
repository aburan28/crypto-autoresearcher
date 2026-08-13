#!/usr/bin/env python3
"""Audit which committed run manifests pin the source that produced them.

GOAL-ENDO-001 next action N6, open since DEC-20260807-c8aa8b and promoted to
BLOCKING by CORR-20260807-0f5d56.

THE DEFECT THIS MEASURES. A run manifest records `code.commit` and a boolean
`code.dirty`. When `dirty` is true the commit does not identify the code that
ran, and nothing else in the manifest does either. Seventeen of
EXP-ICINV-4d33aa's nineteen measurement runs are in exactly that state. The
consequence is not hypothetical: EXP-INSTR-85b102's D6 root cause is
permanently unrecoverable because the pre-repair source existed only in a dirty
tree and no hash of it was ever written down. An independent Validator could
corroborate the stated mechanism for one of three affected cells and could not
establish it for the other two.

WHAT COUNTS AS PINNED. `harness/runner.py:source_provenance` writes
`code.source.files[<path>].sha256` for every repo `.py` the run actually
imported, derived from `sys.modules` rather than from a declared list. A run is
PINNED when `code.source.all_pinned` is true. Pinning is deliberately weaker
than a clean tree: an untracked or modified file is fine as long as its content
is hashed, because the hash stays valid once the file is committed and provably
fails if the file is later edited. That keeps the ordinary
write-a-module-then-run-it workflow legal while making it auditable.

THIS TOOL IS ADVISORY BY DEFAULT AND SAYS SO. Every run predating the fix is
unpinned, and retroactively erroring on them would convert one campaign's debt
into every campaign's red build -- the coupling `check_merge_hygiene.py` and
`main-health.yml` were split apart to remove. Use `--since-commit` to scope the
audit to runs added after the fix landed, or `--strict` to exit non-zero on any
unpinned run in scope.

Usage:
    python3 tools/check_run_source_provenance.py
    python3 tools/check_run_source_provenance.py --experiment EXP-ICINV-4d33aa
    python3 tools/check_run_source_provenance.py --since-commit <sha> --strict
"""
from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _paths_added_since(commit: str) -> set[str] | None:
    proc = subprocess.run(["git", "diff", "--name-only", "--diff-filter=A",
                           f"{commit}..HEAD"],
                          cwd=REPO, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return {p for p in proc.stdout.splitlines() if p}


def audit(experiment: str | None, since: str | None) -> tuple[list, list, list]:
    pattern = os.path.join(REPO, "experiments",
                           experiment or "*", "runs", "*", "manifest.yaml")
    scope = _paths_added_since(since) if since else None
    if since and scope is None:
        print(f"error: could not resolve commit {since!r}", file=sys.stderr)
        raise SystemExit(2)

    pinned, unpinned, unreadable = [], [], []
    for path in sorted(glob.glob(pattern)):
        rel = os.path.relpath(path, REPO)
        if scope is not None and rel not in scope:
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                body = (yaml.safe_load(fh) or {}).get("run") or {}
        except (OSError, yaml.YAMLError) as exc:
            unreadable.append((rel, f"{type(exc).__name__}: {exc}"))
            continue
        source = (body.get("code") or {}).get("source") or {}
        run_id = body.get("id") or rel
        if source.get("all_pinned"):
            pinned.append((run_id, source.get("file_count", 0),
                           bool(source.get("all_clean"))))
        else:
            unpinned.append((run_id, rel, bool((body.get("code") or {}).get("dirty"))))
    return pinned, unpinned, unreadable


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", help="restrict to one EXP-* directory")
    ap.add_argument("--since-commit", dest="since",
                    help="only audit run manifests ADDED after this commit")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any in-scope run is unpinned")
    args = ap.parse_args()

    pinned, unpinned, unreadable = audit(args.experiment, args.since)
    total = len(pinned) + len(unpinned) + len(unreadable)
    if not total:
        print("no run manifests in scope")
        return 0

    print(f"{len(pinned)} pinned, {len(unpinned)} unpinned, "
          f"{len(unreadable)} unreadable, of {total} run manifest(s) in scope")
    clean = sum(1 for _, _, c in pinned if c)
    if pinned:
        print(f"  of the pinned, {clean} also ran from a fully clean tree")
    for rel, why in unreadable:
        print(f"  UNREADABLE {rel}: {why}")
    if unpinned:
        shown = unpinned if args.strict else unpinned[:10]
        for run_id, rel, dirty in shown:
            print(f"  unpinned {run_id} (code.dirty={dirty}) {rel}")
        if len(shown) < len(unpinned):
            print(f"  ... and {len(unpinned) - len(shown)} more")

    if unreadable:
        return 1
    if args.strict and unpinned:
        print("FAIL (--strict): a run that cannot bind its own code to a hash "
              "is not a reproduction package (GOAL-ENDO-001 N6)")
        return 1
    if unpinned and not args.strict:
        print("advisory: run predating the N6 fix are expected to be unpinned; "
              "scope with --since-commit and add --strict to enforce")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
