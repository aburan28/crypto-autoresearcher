"""Loopback-only Streamable HTTP MCP observer for local research agents.

This is deliberately a *peer awareness* service, not a second Coordinator.
It owns only a rebuildable SQLite projection of bounded TTL heartbeats and may
report an internal controller lease observation.  It exposes no tool that can
assign work, alter a research record, advance a checkpoint, archive an
artifact, mutate a queue, or acquire a lease.

One daemon is shared by Codex, Claude Code, OpenCode, and any other local MCP
client over Streamable HTTP.  A stdio server would be launched separately by
each host and could not provide the common presence view this service exists
for.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from .projection import GOAL_ID, ProjectionError, load_materialized_goal
from .store import CampaignStore, CampaignStoreError


SERVER_NAME = "Crypto Autoresearcher Local Peer"
SERVER_SCHEMA = "crypto.autoresearch.local_peer_mcp.v1"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_PATH = "/mcp"
MAX_PEERS_RETURNED = 64
MAX_SUMMARY_LENGTH = 1_000
MAX_WRITE_SCOPES = 32
MAX_WRITE_SCOPE_LENGTH = 512

_OPAQUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@/+\-]{0,255}$")
_COMMIT = re.compile(r"^[0-9a-f]{7,64}$")
_RUNTIMES = frozenset({"codex", "claude-code", "opencode", "api-direct", "other"})
_ROLES = frozenset(
    {
        "coordinator",
        "idea-generator",
        "executor",
        "reviewer",
        "validator",
        "red-team",
        "theory-agent",
        "benchmark-agent",
    }
)
_ACTIVITY_STATES = frozenset({"starting", "working", "waiting", "blocked", "completed"})


class PeerInputError(ValueError):
    """A client supplied data outside the deliberately narrow peer contract."""


@dataclass(frozen=True)
class ServerContext:
    """Static daemon identity shared by every local MCP request."""

    repo_root: Path
    workspace_id: str
    state_db: Path | None
    endpoint: str
    store: CampaignStore


def _run_git(repo_root: Path, *arguments: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        return None
    value = completed.stdout.strip()
    return value or None


def current_source_commit(repo_root: Path) -> str | None:
    """Read the daemon checkout's commit without changing repository state."""

    return _run_git(repo_root, "rev-parse", "--verify", "HEAD")


# Kept as a small public compatibility alias for callers of the original
# observer helper.  Tool parameters also use the name ``source_commit``, so
# internal request code deliberately calls ``current_source_commit``.
source_commit = current_source_commit


def workspace_fingerprint(repo_root: str | Path) -> str:
    """Return a stable opaque identity for this local repository/worktree.

    The identity is an operational partition key, not a durable record ID and
    not an authentication mechanism.  Including the resolved repository path
    makes accidentally sharing a daemon between unrelated local checkouts
    visible rather than silently mixing their agent presence.
    """

    root = Path(repo_root).expanduser().resolve()
    remote = _run_git(root, "config", "--get", "remote.origin.url")
    common_dir = _run_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    payload = {
        "repo_root": root.as_posix(),
        "remote": remote,
        "git_common_dir": common_dir,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "workspace-" + hashlib.sha256(canonical).hexdigest()[:20]


def default_state_db(repo_root: str | Path) -> Path:
    """Choose a user-state database path without dirtying the checkout."""

    state_home = os.environ.get("XDG_STATE_HOME")
    if state_home:
        base = Path(state_home).expanduser()
        if not base.is_absolute():
            raise ValueError("XDG_STATE_HOME must be an absolute path for peer-MCP state")
    else:
        # This follows the conventional Unix user-state location.  Callers can
        # always make the shared location explicit with --state-db.
        base = Path.home() / ".local" / "state"
    return (
        base
        / "crypto-autoresearcher"
        / "peer-mcp"
        / f"{workspace_fingerprint(repo_root)}.sqlite3"
    )


def _opaque_id(value: str, name: str) -> str:
    if not isinstance(value, str) or not _OPAQUE_ID.fullmatch(value):
        raise PeerInputError(
            f"{name} must be 1..256 safe opaque identifier characters; spaces and control "
            "characters are not permitted"
        )
    return value


def _goal_id(value: str) -> str:
    if not isinstance(value, str) or not GOAL_ID.fullmatch(value):
        raise PeerInputError("goal_id must be an existing-form GOAL-* identifier")
    return value


def _summary(value: str) -> str:
    if not isinstance(value, str):
        raise PeerInputError("summary must be text")
    normalized = value.strip()
    if len(normalized) > MAX_SUMMARY_LENGTH:
        raise PeerInputError(f"summary may not exceed {MAX_SUMMARY_LENGTH} characters")
    if any(ord(character) < 32 or ord(character) == 127 for character in normalized):
        raise PeerInputError("summary may not contain control characters")
    return normalized


def _write_scopes(value: list[str] | tuple[str, ...] | None) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise PeerInputError("write_scope must be a list of repository-relative paths")
    if len(value) > MAX_WRITE_SCOPES:
        raise PeerInputError(f"write_scope may contain at most {MAX_WRITE_SCOPES} paths")
    result: list[str] = []
    for entry in value:
        if not isinstance(entry, str) or not entry or len(entry) > MAX_WRITE_SCOPE_LENGTH:
            raise PeerInputError("each write_scope entry must be a bounded nonempty path")
        if "\\" in entry or any(ord(character) < 32 or ord(character) == 127 for character in entry):
            raise PeerInputError("write_scope entries must use clean POSIX relative paths")
        path = PurePosixPath(entry)
        if path.is_absolute() or ".." in path.parts or "." in path.parts:
            raise PeerInputError("write_scope entries must stay below the repository root")
        normalized = path.as_posix()
        if normalized in result:
            raise PeerInputError("write_scope entries must be unique")
        result.append(normalized)
    return result


def _enum(value: str | None, name: str, allowed: frozenset[str], *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or value not in allowed:
        choices = ", ".join(sorted(allowed))
        raise PeerInputError(f"{name} must be one of: {choices}")
    return value


def _source_commit(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not _COMMIT.fullmatch(value):
        raise PeerInputError("source_commit must be a 7..64 lowercase hexadecimal Git commit")
    return value


def _expected_workspace(context: ServerContext, value: str) -> str:
    """Require the caller to bind every operation to its local checkout.

    The workspace fingerprint is not a credential: same-host clients remain
    untrusted advisory reporters.  It does, however, prevents an agent in one
    checkout from silently registering with a daemon started for a different
    checkout merely because both happen to use the same loopback port.
    """

    expected = _opaque_id(value, "expected_workspace_id")
    if expected != context.workspace_id:
        raise PeerInputError(
            "expected_workspace_id does not match this daemon; stop and configure the "
            "peer endpoint for the current checkout"
        )
    return expected


def _paths_overlap(left: str, right: str) -> bool:
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def _same_commit(left: str, right: str) -> bool:
    """Treat an exact Git SHA and an abbreviation of it as the same revision."""

    return left.startswith(right) or right.startswith(left)


def _overlap_warnings(self_presence: Mapping[str, Any], peers: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    own_scope = self_presence.get("write_scope")
    if not isinstance(own_scope, list) or not own_scope:
        return []
    warnings: list[dict[str, Any]] = []
    for peer in peers:
        peer_scope = peer.get("write_scope")
        if not isinstance(peer_scope, list):
            continue
        overlaps = sorted(
            {
                own
                for own in own_scope
                for other in peer_scope
                if isinstance(other, str) and _paths_overlap(own, other)
            }
        )
        if overlaps:
            warnings.append(
                {
                    "kind": "advisory_write_scope_overlap",
                    "agent_id": peer.get("agent_id"),
                    "session_id": peer.get("session_id"),
                    "paths": overlaps,
                    "message": "Peer-reported write scopes overlap; verify the official dispatch scope before acting.",
                }
            )
    return warnings


def _bounded_peers(context: ServerContext, goal_id: str) -> tuple[list[dict[str, Any]], bool]:
    now = context.store._now()
    peers = [presence.as_dict(now=now) for presence in context.store.live_agents(context.workspace_id, goal_id)]
    truncated = len(peers) > MAX_PEERS_RETURNED
    return peers[:MAX_PEERS_RETURNED], truncated


def _goal_projection_summary(context: ServerContext, goal_id: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Return a bounded observer summary; no projection is written or promoted."""

    try:
        goal = load_materialized_goal(context.repo_root, goal_id)
    except ProjectionError as exc:
        return None, [
            {
                "kind": "goal_projection_unavailable",
                "message": str(exc),
            }
        ]
    checkpoint_count = goal.record.get("batch_checkpoints")
    return (
        {
            "goal_id": goal.goal_id,
            "layout": goal.layout,
            "status": goal.status,
            "next_action": goal.next_action,
            "source_commit": goal.source_commit,
            "projection_hash": goal.projection_hash,
            "source_files": [
                {"path": source.path, "sha256": source.sha256} for source in goal.source_files
            ],
            "checkpoint_count": len(checkpoint_count) if isinstance(checkpoint_count, list) else 0,
            "advisory_only": True,
        },
        [],
    )


def _base_response(context: ServerContext, goal_id: str | None = None) -> dict[str, Any]:
    return {
        "schema": SERVER_SCHEMA,
        "advisory_only": True,
        "authority": "none",
        "workspace_id": context.workspace_id,
        "goal_id": goal_id,
        # A daemon can remain alive while its checkout advances.  Re-read the
        # revision per response rather than presenting its startup revision as
        # current operational context.
        "server_source_commit": current_source_commit(context.repo_root),
        "server_endpoint": context.endpoint,
    }


def build_server(
    *,
    repo_root: str | Path,
    store: CampaignStore | None = None,
    workspace_id: str | None = None,
    state_db: str | Path | None = None,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> Any:
    """Construct the four-tool local peer server without opening a socket.

    Supplying a store makes in-process tests deterministic.  In production the
    daemon creates a disk-backed store at the supplied or default user-state
    path.  FastMCP remains an optional import so ordinary ledger tooling does
    not acquire an MCP dependency merely by importing :mod:`orchestration`.
    """

    try:
        from fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - depends on optional install
        raise RuntimeError(
            "fastmcp is required for the local peer daemon; "
            "install with `pip install -e '.[campaign-mcp]'`"
        ) from exc

    if host not in {"127.0.0.1", "::1"}:
        raise ValueError("the local peer daemon may bind only to 127.0.0.1 or ::1")
    if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65_535:
        raise ValueError("port must be between 1 and 65535")
    root = Path(repo_root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"repository root does not exist: {root}")
    if store is not None and state_db is not None:
        raise ValueError("pass either store or state_db to build_server, not both")
    db_path: Path | None
    if store is None:
        # CampaignStore normalizes without following symlinks and hardens the
        # leaf directory/files.  Do not resolve here first, which would erase
        # that safety check for an explicit state path.
        db_path = Path(state_db).expanduser() if state_db is not None else default_state_db(root)
        store = CampaignStore(db_path)
        db_path = store.path
    else:
        db_path = store.path
    context = ServerContext(
        repo_root=root,
        workspace_id=workspace_id or workspace_fingerprint(root),
        state_db=db_path,
        endpoint=f"http://{'[::1]' if host == '::1' else host}:{port}{DEFAULT_PATH}",
        store=store,
    )
    mcp = FastMCP(SERVER_NAME)

    @mcp.tool
    def check_in(
        goal_id: str,
        expected_workspace_id: str,
        agent_id: str,
        session_id: str,
        runtime: str,
        role: str | None = None,
        state: str = "working",
        summary: str = "",
        task_id: str | None = None,
        write_scope: list[str] | None = None,
        source_commit: str | None = None,
        ttl_seconds: int = CampaignStore.DEFAULT_TTL_SECONDS,
    ) -> dict[str, Any]:
        """Record a short-lived local heartbeat and return live peer awareness.

        This is advisory operational state only.  It does not assign a task,
        establish a write scope, validate a result, or grant Coordinator
        authority.  ``expected_workspace_id`` must be computed from the
        caller's checkout and matches before any state write.  Clients should
        renew by calling it again before the TTL.
        """

        goal = _goal_id(goal_id)
        _expected_workspace(context, expected_workspace_id)
        agent = _opaque_id(agent_id, "agent_id")
        session = _opaque_id(session_id, "session_id")
        checked_runtime = _enum(runtime, "runtime", _RUNTIMES)
        checked_role = _enum(role, "role", _ROLES, optional=True)
        checked_state = _enum(state, "state", _ACTIVITY_STATES)
        checked_summary = _summary(summary)
        checked_task = _opaque_id(task_id, "task_id") if task_id is not None else None
        scopes = _write_scopes(write_scope)
        checked_commit = _source_commit(source_commit)
        metadata = {
            "runtime": checked_runtime,
            "role": checked_role,
            "state": checked_state,
            "summary": checked_summary,
            "task_id": checked_task,
            "write_scope": scopes,
            "source_commit": checked_commit,
        }
        try:
            presence = context.store.check_in(
                context.workspace_id,
                goal,
                agent,
                session_id=session,
                ttl_seconds=ttl_seconds,
                metadata=metadata,
            )
        except CampaignStoreError as exc:
            raise PeerInputError(str(exc)) from exc
        peers, peers_truncated = _bounded_peers(context, goal)
        own = presence.as_dict(now=context.store._now())
        other_peers = [
            peer
            for peer in peers
            if not (peer["agent_id"] == agent and peer["session_id"] == session)
        ]
        warnings = _overlap_warnings(own, other_peers)
        server_commit = current_source_commit(context.repo_root)
        if (
            checked_commit is not None
            and server_commit is not None
            and not _same_commit(checked_commit, server_commit)
        ):
            warnings.append(
                {
                    "kind": "source_commit_mismatch",
                    "message": "Peer reports a different checkout commit; treat its status as potentially stale.",
                    "peer_source_commit": checked_commit,
                    "server_source_commit": server_commit,
                }
            )
        projection, projection_warnings = _goal_projection_summary(context, goal)
        warnings.extend(projection_warnings)
        response = _base_response(context, goal)
        response.update(
            {
                "accepted": True,
                "self": own,
                "peers": other_peers,
                "peer_count": len(other_peers),
                "peers_truncated": peers_truncated,
                "goal_projection": projection,
                "warnings": warnings,
            }
        )
        return response

    @mcp.tool
    def list_peers(goal_id: str, expected_workspace_id: str) -> dict[str, Any]:
        """Return live, bounded advisory peer summaries for one GOAL-* scope.

        A reported peer is not a task owner and its status cannot be used as
        evidence, a completion receipt, a dispatch decision, or a lease.  The
        caller's expected checkout binding is required before this read.
        """

        goal = _goal_id(goal_id)
        _expected_workspace(context, expected_workspace_id)
        peers, truncated = _bounded_peers(context, goal)
        response = _base_response(context, goal)
        response.update(
            {
                "peers": peers,
                "peer_count": len(peers),
                "peers_truncated": truncated,
            }
        )
        return response

    @mcp.tool
    def get_coordination_status(goal_id: str, expected_workspace_id: str) -> dict[str, Any]:
        """Read daemon health, a committed-goal projection, peers, and lease observation.

        The lease is observed read-only.  This tool cannot acquire, renew, or
        release a lease and a visible lease never overrides the repository's
        Coordinator/archive requirements.  The caller's expected checkout
        binding is required before this read.
        """

        goal = _goal_id(goal_id)
        _expected_workspace(context, expected_workspace_id)
        peers, truncated = _bounded_peers(context, goal)
        projection, warnings = _goal_projection_summary(context, goal)
        lease = context.store.leases.get(
            context.workspace_id, goal, include_expired=True
        )
        response = _base_response(context, goal)
        response.update(
            {
                "goal_projection": projection,
                "peers": peers,
                "peer_count": len(peers),
                "peers_truncated": truncated,
                "controller_lease_observation": (
                    lease.as_dict(now=context.store._now()) if lease is not None else None
                ),
                "warnings": warnings,
            }
        )
        return response

    @mcp.tool
    def check_out(
        goal_id: str,
        expected_workspace_id: str,
        agent_id: str,
        session_id: str,
    ) -> dict[str, Any]:
        """Remove this session's advisory heartbeat early; it changes no research state.

        The caller's expected checkout binding is required before this write.
        """

        goal = _goal_id(goal_id)
        _expected_workspace(context, expected_workspace_id)
        agent = _opaque_id(agent_id, "agent_id")
        session = _opaque_id(session_id, "session_id")
        try:
            removed = context.store.check_out(
                context.workspace_id, goal, agent, session_id=session
            )
        except CampaignStoreError as exc:
            raise PeerInputError(str(exc)) from exc
        response = _base_response(context, goal)
        response.update(
            {
                "removed": removed,
                "agent_id": agent,
                "session_id": session,
            }
        )
        return response

    return mcp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autoresearch-campaign-mcp",
        description="Run the loopback-only Crypto Autoresearcher peer check-in MCP daemon.",
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="repository checkout to observe")
    parser.add_argument(
        "--state-db",
        type=Path,
        help="explicit rebuildable SQLite state path (default: per-workspace user state)",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        choices=("127.0.0.1", "::1"),
        help="loopback address only (default: 127.0.0.1)",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="loopback TCP port")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 1 <= args.port <= 65_535:
        print("peer MCP error: --port must be between 1 and 65535", file=sys.stderr)
        return 2
    store: CampaignStore | None = None
    try:
        repo_root = Path(args.repo).expanduser().resolve()
        if not repo_root.is_dir():
            raise ValueError(f"repository root does not exist: {repo_root}")
        state_db = args.state_db if args.state_db is not None else default_state_db(repo_root)
        store = CampaignStore(state_db)
        server = build_server(
            repo_root=repo_root,
            store=store,
            host=args.host,
            port=args.port,
        )
    except (OSError, ValueError, CampaignStoreError, RuntimeError) as exc:
        if store is not None:
            store.close()
        print(f"peer MCP error: {exc}", file=sys.stderr)
        return 2
    try:
        server.run(
            transport="http",
            host=args.host,
            port=args.port,
            path=DEFAULT_PATH,
            # Never inherit a process-level opt-out.  This loopback service is
            # intentionally unauthenticated but must still reject browser/DNS
            # rebinding Host and Origin spoofing before MCP dispatch.
            host_origin_protection=True,
        )
    except KeyboardInterrupt:  # pragma: no cover - interactive process behavior
        return 130
    finally:
        if store is not None:
            store.close()
    return 0


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())


__all__ = [
    "DEFAULT_HOST",
    "DEFAULT_PATH",
    "DEFAULT_PORT",
    "PeerInputError",
    "SERVER_NAME",
    "SERVER_SCHEMA",
    "build_server",
    "default_state_db",
    "main",
    "current_source_commit",
    "source_commit",
    "workspace_fingerprint",
]
