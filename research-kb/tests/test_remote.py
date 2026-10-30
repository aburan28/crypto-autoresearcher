import json

import pytest
from fastmcp import Client
from starlette.testclient import TestClient

from research_kb.config import Settings
from research_kb.library import Library
from research_kb.server import build_mcp, http_app


def test_remote_requires_auth_and_supports_two_clients(populated):
    lib, _, _ = populated
    with TestClient(http_app(lib)) as client:
        assert client.get("/healthz").status_code == 200
        assert client.get("/v1/search", params={"q": "Semaev"}).status_code == 401
        assert client.get("/v1/status", headers={"Authorization": "Bearer wrong"}).status_code == 401
        results = []
        for token in ("test-codex-secret", "test-claude-secret"):
            response = client.get(
                "/v1/search", params={"q": "KN-LIT-001"}, headers={"Authorization": "Bearer " + token}
            )
            assert response.status_code == 200, response.text
            results.append([(x["source_id"], x["content_hash"]) for x in response.json()["results"]])
        assert results[0] == results[1]
        assert (
            client.get(
                "/v1/search",
                params={"q": "x", "top_k": "invalid"},
                headers={"Authorization": "Bearer test-codex-secret"},
            ).status_code
            == 400
        )
        assert (
            client.post("/v1/ingest", headers={"Authorization": "Bearer test-codex-secret"}).status_code
            == 404
        )


def test_revocation_rate_limit_and_original_retrieval(populated):
    lib, a, _ = populated
    lib.settings.requests_per_minute = 2
    headers = {"Authorization": "Bearer test-codex-secret"}
    source = lib.source("crypto:KN-LIT-001")
    with TestClient(http_app(lib)) as client:
        r = client.get("/v1/sources/" + source["source_id"] + "/original", headers=headers)
        assert r.status_code == 200
        assert r.content == (a / "note.md").read_bytes()
        assert client.get("/v1/status", headers=headers).status_code == 200
        assert client.get("/v1/status", headers=headers).status_code == 429
        raw = json.loads(lib.settings.auth_file.read_text())
        raw["tokens"].pop("codex-cloud")
        lib.settings.auth_file.write_text(json.dumps(raw))
        assert client.get("/v1/status", headers=headers).status_code == 401


def test_http_fails_closed_without_auth_and_empty_readiness(tmp_path):
    with pytest.raises(ValueError, match="AUTH_FILE"):
        http_app(Library(Settings(home=tmp_path)))


@pytest.mark.asyncio
async def test_mcp_tools_are_read_only_and_return_real_evidence(populated):
    lib, _, _ = populated
    async with Client(build_mcp(lib)) as client:
        tools = {t.name for t in await client.list_tools()}
        assert tools == {
            "search_knowledge",
            "get_context",
            "get_source",
            "find_related",
            "search_theorems",
            "get_theorem",
            "kb_status",
        }
        result = await client.call_tool("search_knowledge", {"query": "KN-LIT-001", "repo": "cryptanalysis"})
        assert result.data["results"][0]["origins"][0]["repo"] == "cryptanalysis"
        theorem = await client.call_tool("search_theorems", {"query": "CryptoLean.Semaev.sample"})
        assert theorem.data["results"][0]["verification"] == "source-only"
