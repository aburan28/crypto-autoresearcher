"""Campaign observation and an opt-in supervisor over existing skills.

The supervisor invokes the existing run/coordinate agents as separate bounded
actions. It does not edit the ledger or grant itself Coordinator authority.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

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
    from .session_tools import repository_fingerprint
    _emit(
        {
            "schema": "crypto.autoresearch.peer_workspace.v1",
            "workspace_id": workspace_fingerprint(repo),
            "repository_id": repository_fingerprint(repo),
            "checkout_root": str(repo),
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


def cmd_autopilot(args: argparse.Namespace) -> int:
    import shutil
    from .autopilot import report, select_next, supervise

    repo = Path(args.repo).expanduser().resolve()
    state_dir = (Path(args.state_dir).expanduser().resolve() if args.state_dir
                 else repo / ".git" / "autoresearch-autopilot")
    if args.report:
        _emit(report(state_dir))
        return 0
    if args.dry_run:
        action = select_next(repo)
        _emit({"action": action.as_dict() if action else None,
               "advisory_only": True, "model_calls": 0})
        return 0
    if not shutil.which("opencode"):
        print("autopilot: OpenCode CLI is unavailable; install it before starting "
              "a live supervisor", file=sys.stderr)
        return 2
    from .autopilot import candidates
    coordinator = candidates("coordinator", args.backend)
    if not coordinator:
        print("autopilot: no role-eligible coordinator binding; "
              "configure and probe models before running", file=sys.stderr)
        return 2
    if not repo.joinpath(".git").exists():
        print("autopilot: --repo must be a Git checkout", file=sys.stderr)
        return 2
    state = supervise(repo, state_dir, backends=args.backend,
                      max_actions=1 if args.once else args.max_actions,
                      idle_seconds=args.idle_seconds,
                      retry_seconds=args.retry_seconds,
                      timeout=args.timeout, attach=args.attach)
    _emit({"attempts": state["attempts"],
           "completed_actions": state["completed_actions"],
           "pending_reconcile": state.get("pending_reconcile"),
           "metrics": report(state_dir)})
    return 0


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

    autopilot = sub.add_parser(
        "autopilot", help="keep selecting bounded run/design/coordination actions")
    autopilot.add_argument("--repo", type=Path, default=Path.cwd())
    autopilot.add_argument("--state-dir", type=Path,
                           help="local private state (default: .git/autoresearch-autopilot)")
    autopilot.add_argument("--backend", action="append",
                           default=None, help="ordered model backends; repeat to enable failover")
    autopilot.add_argument("--once", action="store_true")
    autopilot.add_argument("--max-actions", type=int)
    autopilot.add_argument("--dry-run", action="store_true")
    autopilot.add_argument("--report", action="store_true")
    autopilot.add_argument("--idle-seconds", type=int, default=60)
    autopilot.add_argument("--retry-seconds", type=int, default=300)
    autopilot.add_argument("--timeout", type=int, default=7200,
                           help="per-worker watchdog in seconds, not a campaign cap")
    autopilot.add_argument("--attach", help="reuse a running local opencode serve URL")
    autopilot.set_defaults(func=cmd_autopilot)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "autopilot":
        args.backend = args.backend or ["local", "zai", "fireworks", "openai", "anthropic"]
        if (args.max_actions is not None and args.max_actions < 1
                or args.idle_seconds < 1 or args.retry_seconds < 1 or args.timeout < 1):
            print("autopilot: action count and durations must be positive", file=sys.stderr)
            return 2
        if args.attach:
            parsed = urlsplit(args.attach)
            if (parsed.scheme != "http" or parsed.hostname not in
                    ("localhost", "127.0.0.1", "::1") or parsed.username
                    or parsed.password or parsed.path not in ("", "/")):
                print("autopilot: --attach requires a local HTTP OpenCode server",
                      file=sys.stderr)
                return 2
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
