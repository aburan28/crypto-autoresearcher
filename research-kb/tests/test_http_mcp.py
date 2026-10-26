import asyncio
import socket
import threading

import httpx
import pytest
import uvicorn
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from research_kb.server import http_app


@pytest.mark.asyncio
async def test_streamable_http_mcp_over_real_loopback(populated):
    lib, _, _ = populated
    # Emulate a TLS proxy forwarding the public hostname to the loopback backend.
    lib.settings.allowed_hosts.append("kb.example.test")
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(http_app(lib), log_level="error", access_log=False))
    thread = threading.Thread(target=lambda: server.run(sockets=[sock]), daemon=True)
    thread.start()
    try:
        for _ in range(100):
            if server.started:
                break
            await asyncio.sleep(0.02)
        assert server.started
        endpoint = f"http://127.0.0.1:{port}"
        async with httpx.AsyncClient(trust_env=False) as client:
            assert (
                await client.post(endpoint + "/mcp", json={"jsonrpc": "2.0", "method": "initialize", "id": 1})
            ).status_code == 401
        results = []
        for token in ("test-codex-secret", "test-claude-secret"):
            transport = StreamableHttpTransport(
                endpoint + "/mcp", headers={"Authorization": "Bearer " + token, "Host": "kb.example.test"}
            )
            async with Client(transport) as client:
                tools = await client.list_tools()
                assert len(tools) == 7
                result = await client.call_tool("search_knowledge", {"query": "KN-LIT-001"})
                results.append([(x["source_id"], x["content_hash"]) for x in result.data["results"]])
        assert results[0] == results[1]
    finally:
        server.should_exit = True
        await asyncio.to_thread(thread.join, 5)
        sock.close()
