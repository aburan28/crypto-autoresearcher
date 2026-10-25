#!/usr/bin/env python3
"""Check a checkout against the shared-code lock.

`docs/shared-code.lock.json` lists the files the three repositories keep
byte-identical (lab contract, section 7) with the SHA-256 each copy must have.
Every repository runs this against its own checkout, so a copy edited on one
side fails on that side until the change lands in the owner and the lock is
updated everywhere.

    python3 tools/check_lab_parity.py
    python3 tools/check_lab_parity.py --siblings   # also compare ../<repo>
    python3 tools/check_lab_parity.py --repo crypto --root /path/to/crypto

Exit 0 when every listed file matches, 1 otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def repo_name(root: Path) -> str | None:
    try:
        url = subprocess.check_output(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    name = url.rstrip("/").split("/")[-1]
    return name[:-4] if name.endswith(".git") else name


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--repo", default=None)
    parser.add_argument(
        "--siblings",
        action="store_true",
        help="also compare the sibling checkouts next to this one",
    )
    parser.add_argument("--lock", type=Path, default=None)
    args = parser.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parents[1]).resolve()
    name = args.repo or repo_name(root)
    if not name:
        print("lab-parity: cannot determine the repository name", file=sys.stderr)
        return 1
    lock_path = args.lock or root / "docs" / "shared-code.lock.json"
    lock = json.loads(lock_path.read_text())
    if lock.get("schema") != "lab.shared-code-lock/v1":
        print(f"lab-parity: unknown lock schema {lock.get('schema')!r}", file=sys.stderr)
        return 1

    errors: list[str] = []
    checked = 0
    for entry in lock["files"]:
        path = entry["path"]
        repos = entry["repos"]
        if name not in repos:
            continue
        local = root / path
        if not local.is_file():
            errors.append(f"{path}: missing in this checkout")
            continue
        checked += 1
        actual = digest(local)
        if actual != entry["sha256"]:
            errors.append(
                f"{path}: sha256 {actual[:12]}… != lock {entry['sha256'][:12]}… "
                f"(owner: {entry.get('owner', 'unknown')})"
            )

    if args.siblings:
        for entry in lock["files"]:
            path = entry["path"]
            expected = entry["sha256"]
            for repo in entry["repos"]:
                sibling = root.parent / repo
                candidate = sibling / path
                if not candidate.is_file():
                    continue
                checked += 1
                actual = digest(candidate)
                if actual != expected:
                    errors.append(
                        f"{repo}:{path}: sha256 {actual[:12]}… != lock "
                        f"{expected[:12]}… (owner: {entry.get('owner', 'unknown')})"
                    )

    if errors:
        for line in errors:
            print(f"lab-parity: {line}", file=sys.stderr)
        print(f"lab-parity: {len(errors)} problem(s) for {name}", file=sys.stderr)
        return 1
    print(f"lab-parity: OK for {name} ({checked} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
