"""The MCP surface: the tools agents actually call, and what they refuse to do."""

from __future__ import annotations

import pytest

from crypto_kb.mcp import server as mcp_server

fastmcp = pytest.importorskip("fastmcp")


@pytest.fixture(scope="module")
def app(eval_environment):
    mcp_server.set_retriever(eval_environment["retriever"])
    try:
        yield mcp_server.build_server("Crypto Knowledge Base (test)")
    finally:
        mcp_server.set_retriever(None)


async def call(app, name: str, **arguments):
    async with fastmcp.Client(app) as client:
        result = await client.call_tool(name, arguments)
    return result.data


@pytest.mark.anyio
async def test_the_four_tools_are_exposed(app):
    async with fastmcp.Client(app) as client:
        names = {tool.name for tool in await client.list_tools()}
    assert names == {"search_knowledge", "get_context", "get_source", "find_related"}


@pytest.mark.anyio
async def test_no_write_tool_is_exposed(app):
    async with fastmcp.Client(app) as client:
        names = {tool.name for tool in await client.list_tools()}
    for forbidden in ("ingest", "delete", "upsert", "reindex", "stage_repo"):
        assert forbidden not in names


@pytest.mark.anyio
async def test_search_returns_the_documented_schema(app):
    data = await call(app, "search_knowledge", query="Semaev summation polynomials", top_k=5)
    assert data["results"]
    first = data["results"][0]
    for field in (
        "chunk_id",
        "source_id",
        "title",
        "text",
        "section_path",
        "score",
        "source_uri",
        "source_type",
        "claim_status",
        "content_hash",
    ):
        assert field in first, f"{field} missing from the search result schema"


@pytest.mark.anyio
async def test_search_top_k_is_clamped_server_side(app):
    data = await call(app, "search_knowledge", query="elliptic curves", top_k=500)
    assert len(data["results"]) <= 10


@pytest.mark.anyio
async def test_search_filters_are_applied(app):
    data = await call(app, "search_knowledge", query="index calculus", source_type="paper", top_k=8)
    assert data["results"]
    assert {r["source_type"] for r in data["results"]} == {"paper"}


@pytest.mark.anyio
async def test_a_filter_accepts_a_list(app):
    data = await call(
        app, "search_knowledge", query="Groebner", source_type=["paper", "internal-note"], top_k=8
    )
    assert {r["source_type"] for r in data["results"]} <= {"paper", "internal-note"}


@pytest.mark.anyio
async def test_an_invalid_filter_value_is_an_error_not_a_silent_pass(app):
    with pytest.raises(Exception) as excinfo:
        await call(app, "search_knowledge", query="curves", claim_status="verified")
    assert "verified" in str(excinfo.value)


@pytest.mark.anyio
async def test_get_context_expands_a_result(app):
    search = await call(app, "search_knowledge", query="index calculus", top_k=3)
    context = await call(app, "get_context", chunk_id=search["results"][0]["chunk_id"])
    assert context["chunk"]["chunk_id"] == search["results"][0]["chunk_id"]


@pytest.mark.anyio
async def test_get_context_is_capped_server_side(app):
    search = await call(app, "search_knowledge", query="index calculus", top_k=3)
    context = await call(
        app, "get_context", chunk_id=search["results"][0]["chunk_id"], before=99, after=99
    )
    assert len(context["before"]) <= 3 and len(context["after"]) <= 3


@pytest.mark.anyio
async def test_get_source_returns_metadata_not_the_document(app):
    data = await call(app, "get_source", source_id="paper:KN-LIT-001")
    assert data["found"] is True
    assert data["table_of_contents"]
    assert "text" not in data
    assert len(data.get("summary") or "") <= 1210


@pytest.mark.anyio
async def test_get_source_reports_a_miss(app):
    data = await call(app, "get_source", source_id="paper:absent")
    assert data["found"] is False


@pytest.mark.anyio
async def test_find_related(app):
    data = await call(app, "find_related", source_id="paper:KN-LIT-001", top_k=4)
    assert data["results"]
    assert "paper:KN-LIT-001" not in {r["source_id"] for r in data["results"]}


@pytest.fixture
def anyio_backend():
    return "asyncio"
