"""The MCP surface: the tools agents actually call, and what they refuse to do."""

from __future__ import annotations

from pathlib import Path

import pytest

from crypto_kb.mcp import server as mcp_server

fastmcp = pytest.importorskip("fastmcp")

REPO_ROOT = Path(__file__).resolve().parents[3]
ACTUAL_LINEAGE_PATHS = {
    "experiments/EXP-DREG-001/specification.yaml",
    "ledger/evidence/EV-GOAL-DREG-001-B003.yaml",
    "ledger/decisions/DEC-GOAL-DREG-001-B003.yaml",
    "ledger/hypotheses/H-XOR-YIELD.yaml",
    "ledger/hypotheses/H-XOR-d1a480.yaml",
}


@pytest.fixture(scope="module")
def app(eval_environment):
    mcp_server.set_retriever(eval_environment["retriever"])
    try:
        yield mcp_server.build_server("Crypto Knowledge Base (test)")
    finally:
        mcp_server.set_retriever(None)


@pytest.fixture
def lineage_app(pipeline, store, retriever):
    from crypto_kb.ingest.backfill import backfill
    from crypto_kb.ingest.repo_corpus import stage_repository

    staged = stage_repository(REPO_ROOT, store, include=ACTUAL_LINEAGE_PATHS)
    expected = {
        item.metadata["source_id"]: {
            "supersedes": item.metadata.get("supersedes", []),
            "verification_artifacts": item.metadata.get("verification_artifacts", []),
        }
        for item in staged
    }
    report = backfill(pipeline)
    assert not report.failed, [result.reason for result in report.failed]

    previous = mcp_server._retriever
    mcp_server.set_retriever(retriever)
    try:
        yield {
            "app": mcp_server.build_server("Crypto Knowledge Base (lineage test)"),
            "expected": expected,
        }
    finally:
        mcp_server.set_retriever(previous)


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
        "supersedes",
        "verification_artifacts",
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
async def test_actual_legacy_ids_expose_lineage_through_literal_mcp_calls(lineage_app):
    aliases = {
        "EV-GOAL-DREG-001-B003": "evidence:EV-DREG-7597cb",
        "DEC-GOAL-DREG-001-B003": "decision:DEC-20260811-e77b9d",
        "H-XOR-YIELD": "hypothesis:H-XOR-d1a480",
    }
    app = lineage_app["app"]

    for legacy_id, canonical_id in aliases.items():
        search = await call(app, "search_knowledge", query=legacy_id, top_k=4)
        result = search["results"][0]
        expected = lineage_app["expected"][canonical_id]

        assert result["source_id"] == canonical_id
        assert result["score"] == 1.0
        assert any("exact identifier match placed first" in note for note in search["notes"])
        assert result["supersedes"] == expected["supersedes"]
        assert result["verification_artifacts"] == expected["verification_artifacts"]

        context = await call(app, "get_context", chunk_id=result["chunk_id"])
        assert context["chunk"]["supersedes"] == expected["supersedes"]
        assert (
            context["chunk"]["verification_artifacts"]
            == expected["verification_artifacts"]
        )

        source = await call(app, "get_source", source_id=canonical_id)
        assert source["found"] is True
        assert source["supersedes"] == expected["supersedes"]
        assert source["verification_artifacts"] == expected["verification_artifacts"]


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
