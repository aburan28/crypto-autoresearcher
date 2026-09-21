#!/usr/bin/env python3
"""Instrument D: promiscuous instrument.

Unconditionally emits a flag at every procedure step and every locus that can
be named from the receipt's archive blocks (commit, parent, every declared
path, and the commit-message binding), on every input. The frozen predicate
must score this instrument `invalid` because the negative arm flags.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

STEPS = ("S_a", "S_b", "S_c", "S_d", "S_e")


def main() -> int:
    parser = argparse.ArgumentParser(description="instrument D: promiscuous (flags everything)")
    parser.add_argument("receipt", help="path to the receipt")
    parser.add_argument("repo_root", help="repository root (unused)")
    parser.add_argument("--base", default="HEAD", help="verification base (unused)")
    args = parser.parse_args()

    with open(args.receipt, "rb") as handle:
        receipt = json.loads(handle.read().decode("utf-8"))

    flags: list[dict[str, Any]] = []
    for task in receipt.get("tasks", []):
        archive = task.get("archive")
        if not isinstance(archive, dict):
            continue
        flags.append(
            {
                "step": "S_a",
                "locus": "archive.commit_sha",
                "declared_value": archive.get("commit_sha"),
                "observed_value": "promiscuous:flag",
            }
        )
        flags.append(
            {
                "step": "S_b",
                "locus": "archive.parent_sha",
                "declared_value": archive.get("parent_sha"),
                "observed_value": "promiscuous:flag",
            }
        )
        hashes = archive.get("path_sha256") or {}
        flags.append(
            {
                "step": "S_c",
                "locus": "commit.changed_paths",
                "declared_value": sorted(hashes),
                "observed_value": "promiscuous:flag",
            }
        )
        for path, declared_hash in hashes.items():
            flags.append(
                {
                    "step": "S_d",
                    "locus": path,
                    "declared_value": declared_hash,
                    "observed_value": "promiscuous:flag",
                }
            )
        flags.append(
            {
                "step": "S_e",
                "locus": "commit_message",
                "declared_value": [task.get("id"), *(archive.get("record_ids") or [])],
                "observed_value": "promiscuous:flag",
            }
        )

    if not flags:
        for step in STEPS:
            flags.append(
                {
                    "step": step,
                    "locus": "unconditional",
                    "declared_value": "promiscuous:flag",
                    "observed_value": "promiscuous:flag",
                }
            )

    json.dump(
        {
            "instrument": "D",
            "receipt": args.receipt,
            "repo_root": args.repo_root,
            "verification_base": args.base,
            "flags": flags,
        },
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
