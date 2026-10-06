#!/usr/bin/env python3
"""Carry the program's research state through a cairn lab instead of git.

Every concurrency rule in CLAUDE.md exists because sessions shared state
through git: identifiers minted from the same committed snapshot collided at
merge time, files nobody edited "in the same place" conflicted, squash merges
orphaned recorded SHAs, and news travelled only as fast as a merge digest. A
cairn lab (https://github.com/aburan28/cairn, docs/lab.md there) holds the
same files as a set of signed ops that merge like a CRDT: no server, no merge
step, a concurrent edit kept as a visible conflict, a write-once record that
cannot be replaced. This module points it at this repository:

    tools/lab_sync.py doctor                 what is configured, what is missing
    tools/lab_sync.py init [--name NAME]     create the space, with the program's policy
    tools/lab_sync.py push                   sign what changed in scope (cairn lab commit)
    tools/lab_sync.py pull  [--remote R]     reconcile, then write the space to disk
    tools/lab_sync.py sync  [--remote R]     push, then pull
    tools/lab_sync.py status | conflicts | envs

Scope and policy come from orchestration/lab.yaml: research state (ledger/,
coordination/, experiments/, knowledge/) goes through the lab; code stays in
git. A remote is `dir:PATH` (a shared or synced directory, another replica)
or `peer:ID@HOST:PORT` (cairn's encrypted transport; needs
CAIRN_LAB_PEER_IDENTITY). Configuration is environment only, so nothing
machine-specific is committed:

    CAIRN_BIN                 the cairn binary (default: `cairn` on PATH)
    CAIRN_LAB                 the lab directory (default: <repo>/.cairn-lab)
    CAIRN_LAB_IDENTITY        ed25519 identity file ops are signed with
    CAIRN_LAB_REMOTE          default remote for pull/sync
    CAIRN_LAB_PEER_IDENTITY   transport identity for a peer: remote

What this does NOT change: the Coordinator's authority, the records' schemas,
validate_ledger, or what counts as official. A lab op is a signed copy of a
file, not a decision; the program's rules about who may write which record
bind exactly as they did, and git stays the record of archive receipts until
the Coordinator decides otherwise. See docs/cairn-lab.md.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent.parent
CONFIG = HERE / "orchestration" / "lab.yaml"
# The working tree the bridge commits from and checks out into. Always this
# repository in use; LAB_SYNC_ROOT exists so tests can point it at a scratch
# tree without importing 7 GB of real records.
REPO = Path(os.environ.get("LAB_SYNC_ROOT") or HERE)


class LabError(Exception):
    """A precondition this machine does not meet. Exit 3: nothing was done."""


def load_config(path: Path = CONFIG) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    scope = data.get("scope") or {}
    policy = data.get("policy") or {}
    if not scope.get("include"):
        raise ValueError(f"{path}: scope.include is empty")
    for key in policy:
        if key not in ("write_once", "mutable", "ignore"):
            raise ValueError(f"{path}: unknown policy key {key!r}")
    for key in ("write_once", "mutable", "ignore"):
        for glob in policy.get(key, []) or []:
            if not isinstance(glob, str) or glob.startswith("/") or ".." in glob.split("/"):
                raise ValueError(f"{path}: policy.{key} entry {glob!r} is not a relative glob")
    return data


def cairn_bin() -> str:
    explicit = os.environ.get("CAIRN_BIN")
    found = explicit or shutil.which("cairn")
    if not found or not (Path(found).is_file() and os.access(found, os.X_OK)):
        raise LabError(
            "no cairn binary: install cairn (cargo install --git "
            "https://github.com/aburan28/cairn) or set CAIRN_BIN"
        )
    return found


def lab_dir() -> Path:
    return Path(os.environ.get("CAIRN_LAB") or REPO / ".cairn-lab")


def identity(required: bool = True) -> str | None:
    value = os.environ.get("CAIRN_LAB_IDENTITY")
    if required and not value:
        raise LabError(
            "CAIRN_LAB_IDENTITY is not set: create one with "
            "`cairn lab identity --out ~/.cairn/lab.identity.json` and export it"
        )
    if value and not Path(value).is_file():
        raise LabError(f"CAIRN_LAB_IDENTITY names {value}, which does not exist")
    return value


def scope_args(config: dict) -> list[str]:
    args: list[str] = []
    for glob in config["scope"]["include"]:
        args += ["--include", glob]
    for glob in config["scope"].get("exclude", []) or []:
        args += ["--exclude", glob]
    return args


def remote_args(remote: str | None) -> list[str]:
    remote = remote or os.environ.get("CAIRN_LAB_REMOTE")
    if not remote:
        raise LabError("no remote: pass --remote dir:PATH|peer:ID@HOST:PORT or set CAIRN_LAB_REMOTE")
    kind, _, target = remote.partition(":")
    if kind == "dir" and target:
        return ["--dir", target]
    if kind == "peer" and target:
        peer_identity = os.environ.get("CAIRN_LAB_PEER_IDENTITY")
        if not peer_identity:
            raise LabError("a peer: remote needs CAIRN_LAB_PEER_IDENTITY (cairn lab peer-id creates one)")
        return ["--peer", target, "--peer-identity", peer_identity]
    raise LabError(f"remote {remote!r} is not dir:PATH or peer:ID@HOST:PORT")


def run(args: list[str], check: bool = True) -> int:
    """Run `cairn lab --lab <dir> ARGS`, streaming its output."""
    command = [cairn_bin(), "lab", "--lab", str(lab_dir()), *args]
    code = subprocess.call(command)
    if check and code != 0:
        raise SystemExit(code)
    return code


def capture(args: list[str]) -> str:
    command = [cairn_bin(), "lab", "--lab", str(lab_dir()), *args]
    return subprocess.run(command, capture_output=True, text=True, check=True).stdout


def require_lab() -> None:
    cairn_bin()  # the more basic problem first
    if not (lab_dir() / "space").exists():
        raise LabError(f"no lab at {lab_dir()}: run `tools/lab_sync.py init`, or clone one with `cairn lab clone`")


# -- commands -------------------------------------------------------------------


def cmd_doctor(_: argparse.Namespace) -> int:
    problems = 0

    def line(ok: bool, what: str) -> None:
        nonlocal problems
        problems += 0 if ok else 1
        print(f"  {'ok ' if ok else 'NO '} {what}")

    print("cairn lab bridge")
    try:
        binary = cairn_bin()
        version = (subprocess.run([binary, "--version"], capture_output=True, text=True).stdout.strip().splitlines() or [""])[0]
        line(True, f"cairn: {binary} {version}")
    except LabError as error:
        line(False, str(error))
        binary = None
    line((lab_dir() / "space").exists(), f"lab: {lab_dir()}")
    try:
        line(identity() is not None, f"identity: {os.environ.get('CAIRN_LAB_IDENTITY')}")
    except LabError as error:
        line(False, str(error))
    remote = os.environ.get("CAIRN_LAB_REMOTE")
    print(f"  --  remote: {remote or 'unset (pass --remote to pull/sync)'}")
    if binary:
        sandbox = subprocess.run([binary, "lab", "sandbox"], capture_output=True, text=True).stdout
        for text in sandbox.strip().splitlines():
            print(f"  --  {text}")
    return 0 if problems == 0 else 3


def cmd_init(args: argparse.Namespace) -> int:
    config = load_config()
    if (lab_dir() / "space").exists():
        raise LabError(f"{lab_dir()} already holds a space")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(config["policy"], handle, indent=2, sort_keys=True)
        policy_path = handle.name
    try:
        return run(["init", "--name", args.name, "--identity", identity(), "--policy", policy_path])
    finally:
        os.unlink(policy_path)


def cmd_push(_: argparse.Namespace) -> int:
    require_lab()
    # Exit 2 from commit means some change was refused (an edit to a write-once
    # record); everything else in the batch was still signed, so report it and
    # pass the code on rather than raising halfway through a sync.
    return run(["commit", str(REPO), "--identity", identity(), *scope_args(load_config())], check=False)


def cmd_pull(args: argparse.Namespace) -> int:
    require_lab()
    run(["sync", *remote_args(args.remote)])
    # Never --force: a file edited here and not yet pushed is kept, and the
    # checkout says so, rather than being overwritten by the space's version.
    run(["checkout", str(REPO), *scope_args(load_config())])
    return report_conflicts()


def cmd_sync(args: argparse.Namespace) -> int:
    pushed = cmd_push(args)
    pulled = cmd_pull(args)
    return pushed or pulled


def cmd_status(_: argparse.Namespace) -> int:
    require_lab()
    run(["status"])
    return run(["changes", str(REPO), *scope_args(load_config())])


def report_conflicts() -> int:
    conflicts = json.loads(capture(["conflicts", "--json"]) or "[]")
    if conflicts:
        print(
            f"{len(conflicts)} open conflict(s): concurrent writes are kept side by side "
            "as PATH.lab-conflict-<id>; resolve by editing PATH with every side in view "
            "and pushing, or with `cairn lab resolve`"
        )
        return 1
    return 0


def cmd_conflicts(_: argparse.Namespace) -> int:
    require_lab()
    run(["conflicts"])
    return report_conflicts()


def cmd_envs(_: argparse.Namespace) -> int:
    require_lab()
    config = load_config()
    present = json.loads(capture(["env", "ls", "--json"]) or "{}")
    missing = 0
    for name, spec in (config.get("environments") or {}).items():
        if name in present:
            print(f"  ok  {name}")
        else:
            missing += 1
            print(f"  --  {name}: not imported here; build {spec.get('recipe')} from the cairn repository, then `cairn lab env import {name}`")
    return 0 if missing == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lab_sync", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor").set_defaults(func=cmd_doctor)
    init = sub.add_parser("init")
    init.add_argument("--name", default="crypto-autoresearcher")
    init.set_defaults(func=cmd_init)
    sub.add_parser("push").set_defaults(func=cmd_push)
    for name, func in (("pull", cmd_pull), ("sync", cmd_sync)):
        command = sub.add_parser(name)
        command.add_argument("--remote", help="dir:PATH or peer:ID@HOST:PORT (default $CAIRN_LAB_REMOTE)")
        command.set_defaults(func=func)
    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("conflicts").set_defaults(func=cmd_conflicts)
    sub.add_parser("envs").set_defaults(func=cmd_envs)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except LabError as error:
        print(f"lab_sync: {error}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
