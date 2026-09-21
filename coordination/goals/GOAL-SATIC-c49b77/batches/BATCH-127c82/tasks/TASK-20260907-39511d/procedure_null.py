#!/usr/bin/env python3
"""Instrument C: null instrument. Unconditionally emits the empty flag set.

Reads the receipt so the invocation shape matches instruments B and D, then
emits no flags regardless of the receipt's contents. The frozen predicate
must score this instrument `insensitive`.
"""

from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="instrument C: null (empty flag set)")
    parser.add_argument("receipt", help="path to the receipt (unread for flags)")
    parser.add_argument("repo_root", help="repository root (unused)")
    parser.add_argument("--base", default="HEAD", help="verification base (unused)")
    args = parser.parse_args()

    with open(args.receipt, "rb") as handle:
        json.loads(handle.read().decode("utf-8"))

    json.dump(
        {
            "instrument": "C",
            "receipt": args.receipt,
            "repo_root": args.repo_root,
            "verification_base": args.base,
            "flags": [],
        },
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
