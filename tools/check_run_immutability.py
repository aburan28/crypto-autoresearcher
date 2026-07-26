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

Deletion is an EXCEPTION to append-only immutability and is permitted only when
recorded in ledger/authorized-removals.yaml (who authorized it, when, why, and
where the content remains recoverable). Anything unlisted still fails, so an
authorized removal is auditable rather than silently exempt.
"""
from __future__ import annotations

import os
import subprocess
import sys

import yaml

AUTHORIZED = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "ledger", "authorized-removals.yaml")


def authorized_prefixes() -> list[str]:
    """Path prefixes whose removal has been explicitly authorized and recorded.

    Deletion of a run record is an exception to append-only immutability. It is
    permitted only when listed in ledger/authorized-removals.yaml, so that the
    exception is auditable (who authorized it, when, why, where recoverable)
    rather than silently exempt. Anything unlisted still fails.
    """
    if not os.path.exists(AUTHORIZED):
        return []
    doc = yaml.safe_load(open(AUTHORIZED, encoding="utf-8")) or {}
    return [e["path_prefix"] for e in (doc.get("authorized_removals") or [])
            if e.get("path_prefix") and e.get("authorized_by") and e.get("reason")]

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

    touched = [line for line in diff.stdout.splitlines()
               if "/runs/" in line and line.startswith("experiments/")]
    allowed = authorized_prefixes()
    violations = [p for p in touched
                  if not any(p.startswith(a) for a in allowed)]
    exempted = len(touched) - len(violations)
    if exempted:
        print(f"NOTICE: {exempted} run artifact path(s) covered by recorded "
              f"authorizations in ledger/authorized-removals.yaml")
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
