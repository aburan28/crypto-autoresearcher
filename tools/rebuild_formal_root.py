#!/usr/bin/env python3
"""Regenerate the formal workspace's root module from what is on disk.

Thin wrapper over `orchestration.formal.workspace`, which the formalize
pipeline calls directly after staging a theorem file.  See that module for why
the root is derived rather than committed.

    python3 tools/rebuild_formal_root.py [--workspace formal] [--check]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestration.formal.workspace import DEFAULT_LIBRARY, modules, rebuild_root, render_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default="formal")
    parser.add_argument("--library", default=DEFAULT_LIBRARY)
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if the root is stale instead of writing it")
    args = parser.parse_args(argv)

    workspace = Path(args.workspace)
    if not workspace.is_dir():
        print(f"error: no such workspace: {workspace}", file=sys.stderr)
        return 2

    target = workspace / f"{args.library}.lean"
    if args.check:
        current = target.read_text(encoding="utf-8") if target.is_file() else None
        if current == render_root(workspace, args.library):
            print(f"{target} is current")
            return 0
        print(f"{target} is stale; run tools/rebuild_formal_root.py", file=sys.stderr)
        return 1

    (workspace / args.library).mkdir(parents=True, exist_ok=True)
    rebuild_root(workspace, args.library)
    print(f"{target}: {len(modules(workspace, args.library))} module(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
