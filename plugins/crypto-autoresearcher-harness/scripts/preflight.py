#!/usr/bin/env python3
"""Read-only readiness checks for the portable harness front door.

The plugin deliberately delegates all research state and execution to the
checked-out repository.  This helper verifies that the expected contracts and
runtime bindings are present before the host agent spends tokens or starts a
task.  It never writes to the checkout, calls a backend, or prints secrets.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REQUIRED = (
    "AGENTS.md",
    "orchestration/roles.yaml",
    "tools/research_dispatch.py",
    "tools/generate_runtime_agents.py",
    "tools/check_runtime_bindings.py",
)

RUNTIME_BINDINGS = {
    "claude-code": ("CLAUDE.md", ".claude/agents", ".claude/skills"),
    "opencode": ("opencode.json", ".opencode/agent", ".agents/skills"),
    "codex": (".codex/config.toml", ".codex/agents"),
}

CLI_MAIN = (
    "from orchestration.cli import main; import sys; "
    "raise SystemExit(main(sys.argv[1:]))"
)


def _run(repo: Path, command: list[str], label: str) -> bool:
    """Run one repository-owned check and retain its ordinary diagnostics."""
    print(f"\n== {label} ==")
    completed = subprocess.run(command, cwd=repo, check=False)
    if completed.returncode:
        print(f"FAIL: {label} exited {completed.returncode}")
        return False
    print(f"OK: {label}")
    return True


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only Crypto Autoresearcher harness readiness checks."
    )
    parser.add_argument(
        "--repo", required=True, type=Path,
        help="path to the Crypto Autoresearcher checkout",
    )
    parser.add_argument(
        "--runtime", choices=("claude-code", "opencode", "codex"),
        required=True, help="host runtime whose checked-in binding to check",
    )
    parser.add_argument(
        "--doctor", action="store_true",
        help="also run the repository's no-cost doctor command",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    repo = args.repo.expanduser().resolve()
    if not repo.is_dir():
        print(f"FAIL: checkout does not exist: {repo}")
        return 2

    missing = [str(repo / relative) for relative in REQUIRED
               if not (repo / relative).exists()]
    missing.extend(
        str(repo / relative) for relative in RUNTIME_BINDINGS[args.runtime]
        if not (repo / relative).exists()
    )
    if missing:
        print("FAIL: this is not a complete Crypto Autoresearcher checkout.")
        for path in missing:
            print(f"  missing: {path}")
        return 2

    print(f"checkout: {repo}")
    print(f"runtime:  {args.runtime}")
    print("mode:     read-only")

    passed = _run(
        repo,
        [sys.executable, "tools/generate_runtime_agents.py", "--check"],
        "generated runtime bindings",
    )
    passed &= _run(
        repo,
        [sys.executable, "tools/check_runtime_bindings.py"],
        "runtime authority bindings",
    )
    if args.doctor:
        passed &= _run(
            repo,
            [sys.executable, "-c", CLI_MAIN, "doctor"],
            "harness doctor",
        )

    if passed:
        print("\nREADY: contracts and selected runtime binding are consistent.")
        return 0
    print("\nBLOCKED: repair the failed readiness check before dispatching work.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
