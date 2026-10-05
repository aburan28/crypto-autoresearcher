#!/usr/bin/env python3
"""Render a per-user launchd agent for the Cairn campaign service.

The file contains paths and loopback ports, never provider credentials. Copy
the rendered plist into ~/Library/LaunchAgents and bootstrap it with launchctl.
"""
from __future__ import annotations

import argparse
import os
import plistlib
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LABEL = "com.crypto-autoresearcher.cairn"


def render(*, repo: Path, state_dir: Path, cairn_bin: Path, identity: Path,
           cairn_data: Path, opencode_port: int, cairn_serve: str,
           cairn_listen: str, backend: str, opencode_bin: Path,
           bootstrap: list[Path] | None = None, attest_identity: Path | None = None) -> dict:
    service = repo / "tools" / "cairn_autopilot_service.py"
    argv = [sys.executable, str(service), "--repo", str(repo),
            "--state-dir", str(state_dir), "--cairn-bin", str(cairn_bin),
            "--identity", str(identity), "--cairn-data", str(cairn_data),
            "--opencode-port", str(opencode_port), "--cairn-serve", cairn_serve,
            "--cairn-listen", cairn_listen, "--backend", backend]
    for peer in bootstrap or []:
        argv.extend(["--bootstrap", str(peer)])
    if attest_identity:
        argv.extend(["--attest-identity", str(attest_identity)])
    return {
        "Label": LABEL,
        "ProgramArguments": argv,
        "WorkingDirectory": str(repo),
        "EnvironmentVariables": {
            "PATH": os.pathsep.join((str(opencode_bin.parent), str(Path(sys.executable).parent),
                                     "/usr/local/bin", "/usr/bin", "/bin",
                                     "/usr/sbin", "/sbin")),
        },
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 30,
        "ProcessType": "Background",
        "StandardOutPath": str(state_dir / "service.stdout.log"),
        "StandardErrorPath": str(state_dir / "service.stderr.log"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--cairn-bin", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--cairn-data", type=Path, required=True)
    parser.add_argument("--opencode-port", type=int, default=4096)
    parser.add_argument("--cairn-serve", default="127.0.0.1:8081")
    parser.add_argument("--cairn-listen", default="127.0.0.1:9001")
    parser.add_argument("--backend", default="local")
    parser.add_argument("--bootstrap", type=Path, action="append", default=[])
    parser.add_argument("--attest-identity", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    opencode = shutil.which("opencode")
    if not opencode:
        parser.error("opencode is not on PATH")
    repo = args.repo.resolve()
    state_dir = args.state_dir.resolve()
    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    destination = args.out.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    document = render(
        repo=repo, state_dir=state_dir, cairn_bin=args.cairn_bin.resolve(),
        identity=args.identity.resolve(), cairn_data=args.cairn_data.resolve(),
        opencode_port=args.opencode_port, cairn_serve=args.cairn_serve,
        cairn_listen=args.cairn_listen, backend=args.backend,
        bootstrap=[peer.resolve() for peer in args.bootstrap],
        attest_identity=args.attest_identity.resolve() if args.attest_identity else None,
        # Keep the configured executable path rather than its current Cellar
        # target, so a package-manager upgrade can update the symlink.
        opencode_bin=Path(opencode).absolute())
    with destination.open("wb") as stream:
        plistlib.dump(document, stream, sort_keys=True)
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
