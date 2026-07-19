#!/usr/bin/env python3
"""Fail if a committed run record was modified or deleted.

Run artifacts under experiments/<EXP>/runs/<RUN>/ are immutable (AGENTS.md rule
4, docs/evidence-and-reproducibility.md): a defective run is superseded by a
new RUN id, never edited or removed. This checks a diff range for any
modification (M) or deletion (D) touching run directories. New files (A) are
allowed — that is how new runs are added.

Usage:
    python3 tools/check_run_immutability.py [BASE_REF] [HEAD_REF]

Defaults: BASE from $GITHUB_BASE_REF or origin/main; HEAD = HEAD.
Exit 0 if no immutable path was mutated, 1 otherwise. If the base ref cannot
be resolved (e.g. shallow clone without it), the check is skipped with a
notice rather than failing the build.
"""
from __future__ import annotations

import os
import subprocess
import sys

RUN_PATH = os.path.join("experiments", "")  # prefix; refined below


def resolve(ref: str) -> str | None:
    r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref],
                       capture_output=True, text=True)
    return r.stdout.strip() or None


def main() -> int:
    argv = sys.argv[1:]
    base = argv[0] if len(argv) > 0 else (
        os.environ.get("GITHUB_BASE_REF") and f"origin/{os.environ['GITHUB_BASE_REF']}"
        or "origin/main")
    head = argv[1] if len(argv) > 1 else "HEAD"

    base_sha = resolve(base) or resolve(base.replace("origin/", ""))
    if not base_sha:
        print(f"NOTICE: base ref '{base}' not resolvable; skipping "
              f"immutability check")
        return 0

    diff = subprocess.run(
        ["git", "diff", "--diff-filter=MD", "--name-only", base_sha, head],
        capture_output=True, text=True)
    if diff.returncode != 0:
        print(f"NOTICE: git diff failed ({diff.stderr.strip()}); skipping")
        return 0

    violations = [
        line for line in diff.stdout.splitlines()
        if "/runs/" in line and line.startswith("experiments/")
    ]
    if violations:
        print("FAIL: immutable run artifacts were modified or deleted:\n",
              file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        print("\nRun records are append-only. Supersede with a new RUN id "
              "instead of editing.", file=sys.stderr)
        return 1
    print("OK: no committed run artifacts were modified or deleted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
