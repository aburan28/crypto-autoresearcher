"""Integration tests for the intentionally narrow local peer-MCP surface."""
from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest
import tomllib

fastmcp = pytest.importorskip("fastmcp", reason="peer MCP is an optional extra")
httpx = pytest.importorskip("httpx", reason="peer MCP HTTP transport needs httpx")

from orchestration.campaign.mcp_server import (
    SERVER_SCHEMA,
    build_server,
    default_state_db,
    workspace_fingerprint,
)
from orchestration.campaign.store import CampaignStore


class Clock:
    def __init__(self, value: float = 1_700_000_000.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value


def _write_goal(repo: Path, goal_id: str = "GOAL-TEST-001") -> None:
    path = repo / "ledger" / "goals" / f"{goal_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""research_goal:
  id: {goal_id}
  status: active
  next_action: preserve the exact test boundary
""",
        encoding="utf-8",
    )


@pytest.fixture
def peer_app(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_goal(repo)
    store = CampaignStore(tmp_path / "state" / "peer.sqlite", clock=Clock())
    app = build_server(repo_root=repo, store=store, workspace_id="workspace-test")
    try:
        yield app, store, repo
    finally:
        store.close()


async def _call(app, name: str, **arguments):
    arguments.setdefault("expected_workspace_id", "workspace-test")
    async with fastmcp.Client(app) as client:
        result = await client.call_tool(name, arguments)
    return result.data


@pytest.mark.anyio
async def test_exact_peer_tool_catalog_has_no_authoritative_mutations(peer_app) -> None:
    app, _, _ = peer_app
    async with fastmcp.Client(app) as client:
        names = {tool.name for tool in await client.list_tools()}
    assert names == {"check_in", "list_peers", "get_coordination_status", "check_out"}
    forbidden = {
        "dispatch",
        "claim",
        "archive",
        "promote",
        "ledger",
        "advance_checkpoint",
        "set_goal_status",
        "acquire_lease",
        "renew_lease",
        "release_lease",
    }
    assert names.isdisjoint(forbidden)


@pytest.mark.anyio
async def test_two_independent_clients_share_presence_and_get_overlap_warning(peer_app) -> None:
    app, _, _ = peer_app
    first = await _call(
        app,
        "check_in",
        goal_id="GOAL-TEST-001",
        agent_id="codex-agent",
        session_id="codex-session",
        runtime="codex",
        role="executor",
        state="working",
        summary="writing the bounded implementation",
        write_scope=["orchestration/campaign/store.py"],
        source_commit="a" * 40,
    )
    assert first["accepted"] is True
    assert first["advisory_only"] is True
    assert first["authority"] == "none"
    assert first["peers"] == []

    second = await _call(
        app,
        "check_in",
        goal_id="GOAL-TEST-001",
        agent_id="claude-agent",
        session_id="claude-session",
        runtime="claude-code",
        role="validator",
        state="working",
        summary="validating the local state store",
        write_scope=["orchestration/campaign"],
    )
    assert second["peer_count"] == 1
    assert second["peers"][0]["agent_id"] == "codex-agent"
    assert any(warning["kind"] == "advisory_write_scope_overlap" for warning in second["warnings"])

    peers = await _call(app, "list_peers", goal_id="GOAL-TEST-001")
    assert peers["peer_count"] == 2
    assert {peer["runtime"] for peer in peers["peers"]} == {"codex", "claude-code"}


@pytest.mark.anyio
async def test_status_reads_projection_and_lease_but_cannot_mutate_it(peer_app) -> None:
    app, store, repo = peer_app
    lease = store.leases.acquire(
        "workspace-test",
        "GOAL-TEST-001",
        "controller-process",
        owner_session_id="controller-process-session",
        source_commit="c" * 40,
    )
    before = (repo / "ledger" / "goals" / "GOAL-TEST-001.yaml").read_bytes()
    status = await _call(app, "get_coordination_status", goal_id="GOAL-TEST-001")

    assert status["schema"] == SERVER_SCHEMA
    assert status["goal_projection"]["status"] == "active"
    assert status["goal_projection"]["next_action"] == "preserve the exact test boundary"
    assert status["controller_lease_observation"]["owner_id"] == "controller-process"
    assert status["controller_lease_observation"]["epoch"] == lease.epoch
    assert status["controller_lease_observation"]["authority"] == "none"
    assert (repo / "ledger" / "goals" / "GOAL-TEST-001.yaml").read_bytes() == before


@pytest.mark.anyio
async def test_checkout_is_session_scoped_and_rejects_authoritative_looking_input(peer_app) -> None:
    app, _, _ = peer_app
    await _call(
        app,
        "check_in",
        goal_id="GOAL-TEST-001",
        agent_id="opencode-agent",
        session_id="opencode-session",
        runtime="opencode",
    )
    with pytest.raises(Exception, match="Unexpected keyword argument"):
        await _call(
            app,
            "check_in",
            goal_id="GOAL-TEST-001",
            agent_id="opencode-agent",
            session_id="opencode-session",
            runtime="opencode",
            set_goal_status="completed",
        )
    with pytest.raises(Exception, match="repository root"):
        await _call(
            app,
            "check_in",
            goal_id="GOAL-TEST-001",
            agent_id="opencode-agent",
            session_id="opencode-session",
            runtime="opencode",
            write_scope=["../ledger/goals/GOAL-TEST-001.yaml"],
        )

    receipt = await _call(
        app,
        "check_out",
        goal_id="GOAL-TEST-001",
        agent_id="opencode-agent",
        session_id="opencode-session",
    )
    assert receipt["removed"] is True
    assert (await _call(app, "list_peers", goal_id="GOAL-TEST-001"))["peers"] == []


@pytest.mark.anyio
async def test_workspace_mismatch_fails_before_presence_is_written(peer_app) -> None:
    app, _, _ = peer_app
    with pytest.raises(Exception, match="expected_workspace_id does not match"):
        await _call(
            app,
            "check_in",
            expected_workspace_id="workspace-from-another-checkout",
            goal_id="GOAL-TEST-001",
            agent_id="misrouted-agent",
            session_id="misrouted-session",
            runtime="codex",
        )
    assert (await _call(app, "list_peers", goal_id="GOAL-TEST-001"))["peers"] == []


def test_default_state_path_is_outside_the_checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    user_state = tmp_path / "user-state"
    monkeypatch.setenv("XDG_STATE_HOME", str(user_state))
    path = default_state_db(repo)
    assert path.is_relative_to(user_state)
    assert not path.is_relative_to(repo)


def test_default_state_path_rejects_relative_xdg_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("XDG_STATE_HOME", "relative-state")
    with pytest.raises(ValueError, match="absolute"):
        default_state_db(tmp_path / "repo")


def test_fastmcp_floor_includes_explicit_http_host_origin_protection_fix() -> None:
    pyproject = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text())
    assert pyproject["project"]["optional-dependencies"]["campaign-mcp"] == [
        "fastmcp>=3.4.3,<4"
    ]


def _free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_:
        socket_.bind(("127.0.0.1", 0))
        return int(socket_.getsockname()[1])


@pytest.mark.anyio
async def test_real_loopback_http_daemon_shares_presence_between_clients(tmp_path: Path) -> None:
    """Exercise the documented Streamable HTTP transport, not only an in-process app."""

    repo = tmp_path / "repo"
    repo.mkdir()
    _write_goal(repo)
    port = _free_loopback_port()
    endpoint = f"http://127.0.0.1:{port}/mcp"
    expected_workspace_id = workspace_fingerprint(repo)
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "orchestration.campaign.mcp_server",
            "--repo",
            str(repo),
            "--state-db",
            str(tmp_path / "state" / "peer.sqlite"),
            "--port",
            str(port),
        ],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env={**os.environ, "FASTMCP_HTTP_HOST_ORIGIN_PROTECTION": "false"},
    )
    last_error: BaseException | None = None
    try:
        for _ in range(40):
            try:
                async with fastmcp.Client(endpoint, timeout=1) as client:
                    names = {tool.name for tool in await client.list_tools()}
                assert names == {"check_in", "list_peers", "get_coordination_status", "check_out"}
                break
            except BaseException as exc:  # server startup races are expected briefly
                last_error = exc
                await asyncio.sleep(0.1)
        else:
            output = (
                process.stdout.read()
                if process.poll() is not None and process.stdout is not None
                else "<daemon process was still running but did not accept MCP requests>"
            )
            raise AssertionError(f"peer daemon never became ready: {last_error!r}\n{output}")

        # Explicitly set the FastMCP env toggle *off* for the subprocess above.
        # The daemon must still reject a browser/DNS-rebinding style Host/Origin
        # pair before the request reaches its MCP initialization handler.
        async with httpx.AsyncClient(timeout=2) as hostile_client:
            hostile = await hostile_client.post(
                endpoint,
                headers={
                    "Host": "attacker.invalid",
                    "Origin": "https://attacker.invalid",
                },
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {},
                        "clientInfo": {"name": "hostile-test", "version": "1"},
                    },
                },
            )
        assert hostile.status_code in {400, 403, 421}

        async with fastmcp.Client(endpoint, timeout=2) as first:
            result = await first.call_tool(
                "check_in",
                {
                    "goal_id": "GOAL-TEST-001",
                    "expected_workspace_id": expected_workspace_id,
                    "agent_id": "codex-http",
                    "session_id": "session-one",
                    "runtime": "codex",
                },
            )
        assert result.data["accepted"] is True
        async with fastmcp.Client(endpoint, timeout=2) as second:
            peers = await second.call_tool(
                "list_peers",
                {
                    "goal_id": "GOAL-TEST-001",
                    "expected_workspace_id": expected_workspace_id,
                },
            )
        assert peers.data["peer_count"] == 1
        assert peers.data["peers"][0]["agent_id"] == "codex-http"
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


@pytest.fixture
def anyio_backend():
    return "asyncio"
