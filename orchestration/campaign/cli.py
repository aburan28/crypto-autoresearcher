"""Read-only campaign-observer commands.

The command deliberately exposes inspection and daemon startup only.  It does
not have a ``run``, ``dispatch``, or ``advance`` subcommand: those actions
remain behind the existing Coordinator/archive lifecycle until the proposed
frontier, verifier, and controller phases have been implemented.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .checkpoint import checkpoint_by_batch, checkpoints
from .mcp_server import current_source_commit, workspace_fingerprint
from .projection import ProjectionError, load_materialized_goal


def _emit(value: object) -> None:
    print(json.dumps(value, sort_keys=True, indent=2, default=str))


def cmd_status(args: argparse.Namespace) -> int:
    goal = load_materialized_goal(args.repo, args.goal)
    output = goal.as_dict()
    output["checkpoints"] = [view.as_dict() for view in checkpoints(goal)]
    output["advisory_only"] = True
    _emit(output)
    return 0


def cmd_checkpoint(args: argparse.Namespace) -> int:
    goal = load_materialized_goal(args.repo, args.goal)
    view = checkpoint_by_batch(goal, args.batch)
    if view is None:
        print(
            f"no materialized legacy checkpoint for {args.batch!r} in {args.goal}",
            file=sys.stderr,
        )
        return 1
    _emit(view.as_dict())
    return 0


def cmd_workspace(args: argparse.Namespace) -> int:
    """Print the non-secret checkout binding required by peer-MCP calls."""

    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        print(f"campaign workspace error: repository root does not exist: {repo}", file=sys.stderr)
        return 2
    _emit(
        {
            "schema": "crypto.autoresearch.peer_workspace.v1",
            "workspace_id": workspace_fingerprint(repo),
            "source_commit": current_source_commit(repo),
            "advisory_only": True,
        }
    )
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from .mcp_server import main as mcp_main

    argv = ["--repo", str(Path(args.repo).resolve())]
    if args.state_db:
        argv.extend(["--state-db", str(Path(args.state_db).expanduser())])
    if args.port is not None:
        argv.extend(["--port", str(args.port)])
    if args.host is not None:
        argv.extend(["--host", args.host])
    return mcp_main(argv)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autoresearch campaign",
        description="Observe committed research state or run the local peer daemon.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo", type=Path, default=Path.cwd())
    common.add_argument("--goal", required=True, help="existing GOAL-* identifier")

    status = sub.add_parser("status", parents=[common], help="materialize one goal read-only")
    status.set_defaults(func=cmd_status)

    checkpoint = sub.add_parser(
        "checkpoint", parents=[common], help="read one existing legacy batch checkpoint"
    )
    checkpoint.add_argument("--batch", required=True)
    checkpoint.set_defaults(func=cmd_checkpoint)

    workspace = sub.add_parser(
        "workspace", help="print the current checkout binding for peer-MCP calls"
    )
    workspace.add_argument("--repo", type=Path, default=Path.cwd())
    workspace.set_defaults(func=cmd_workspace)

    serve = sub.add_parser(
        "serve", help="start the loopback-only local peer MCP daemon"
    )
    serve.add_argument("--repo", type=Path, default=Path.cwd())
    serve.add_argument("--state-db", type=Path)
    serve.add_argument("--port", type=int)
    serve.add_argument(
        "--host",
        choices=("127.0.0.1", "::1"),
        help="loopback address only (default: 127.0.0.1)",
    )
    serve.set_defaults(func=cmd_serve)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ProjectionError as exc:
        print(f"campaign projection error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
