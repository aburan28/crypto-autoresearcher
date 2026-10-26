from __future__ import annotations

from contextlib import asynccontextmanager

from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.concurrency import run_in_threadpool

from research_kb.auth import BearerAuth, principal
from research_kb.library import Library


def build_mcp(library: Library):
    mcp = FastMCP(
        "Research KB",
        instructions="Search the shared local corpus first. Cite original sources and retain assumptions. Scores are relevance, not truth. No result does not prove absence.",
    )

    @mcp.tool
    def search_knowledge(
        query: str,
        top_k: int = 6,
        repo: str | None = None,
        source_type: str | None = None,
        mode: str = "lexical",
        include_superseded: bool = False,
    ) -> dict:
        """Search all repositories and papers; optionally filter by repo or paper/proof/internal-note.

        Results distinguish original text from literature notes and source-only declarations.
        Use hybrid only when an operator has built a current Qdrant index.
        """
        result = library.search(query, top_k, repo, source_type, mode, include_superseded)
        result["client"] = principal.get()
        return result

    @mcp.tool
    def get_context(chunk_id: str, before: int = 1, after: int = 1) -> dict:
        """Read a bounded excerpt around one selected passage; expansions are capped at three."""
        return library.context(chunk_id, before, after)

    @mcp.tool
    def get_source(source_id: str) -> dict:
        """Read source metadata, coverage and all origins. Ambiguous legacy aliases are explicit."""
        return library.source(source_id)

    @mcp.tool
    def find_related(source_id: str, top_k: int = 5) -> dict:
        """Find other sources about a selected source, with bounded excerpts."""
        return library.related(source_id, top_k)

    @mcp.tool
    def search_theorems(
        query: str, top_k: int = 6, repo: str | None = None, environment: str | None = None
    ) -> dict:
        """Find Lean declarations by exact name or statement. Source-only is not a checked proof.

        Restrict by environment digest to find declarations usable with a particular toolchain.
        """
        library.require_ready()
        return {
            "results": [
                library.with_source_link(r)
                for r in library.catalog.search_theorems(query[:4000], top_k, repo, environment)
            ]
        }

    @mcp.tool
    def get_theorem(declaration_id: str) -> dict:
        """Read one declaration by stable ID, including source statement and verification state."""
        rows = [library.with_source_link(r) for r in library.catalog.search_theorems(declaration_id, 10)]
        return {"found": bool(rows), "declarations": rows}

    @mcp.tool
    def kb_status() -> dict:
        """Check shared corpus counts, revision and whether hybrid indexing is current."""
        return library.status()

    return mcp


def http_app(library: Library):
    settings = library.settings
    if settings.auth_file is None:
        raise ValueError("HTTP requires RESEARCH_KB_AUTH_FILE; use token create first")
    mcp_app = build_mcp(library).http_app(path="/mcp", stateless_http=True, json_response=True)

    @asynccontextmanager
    async def lifespan(app):
        async with mcp_app.lifespan(app):
            yield

    async def health(request):
        return JSONResponse({"status": "alive"})

    async def status(request):
        result = await run_in_threadpool(library.status)
        return JSONResponse(result, status_code=200 if result.get("ready") else 503)

    async def search(request):
        p = request.query_params
        try:
            result = await run_in_threadpool(
                library.search,
                p.get("q", ""),
                int(p.get("top_k", "6")),
                p.get("repo"),
                p.get("source_type"),
                p.get("mode", "lexical"),
                p.get("include_superseded") == "true",
            )
            result["client"] = principal.get()
            return JSONResponse(result)
        except ValueError as exc:
            return JSONResponse({"error": str(exc)}, 400)
        except RuntimeError as exc:
            return JSONResponse({"error": str(exc)}, 503)

    async def source(request):
        result = await run_in_threadpool(library.source, request.path_params["source_id"])
        return JSONResponse(
            result, status_code=200 if result.get("found") else 409 if result.get("ambiguous") else 404
        )

    async def original(request):
        source_id = request.path_params["source_id"]
        result = await run_in_threadpool(library.source, source_id)
        if not result.get("found"):
            return JSONResponse({"error": "source not found"}, 404)
        path = await run_in_threadpool(library.original, result["source_id"])
        if path is None or not path.is_file():
            return JSONResponse({"error": "original unavailable"}, 404)
        filename = result["origins"][0]["path"].rsplit("/", 1)[-1]
        return FileResponse(path, filename=filename, headers={"Cache-Control": "private, no-store"})

    async def theorems(request):
        try:
            p = request.query_params
            result = await run_in_threadpool(
                library.catalog.search_theorems,
                p.get("q", "")[:4000],
                int(p.get("top_k", "6")),
                p.get("repo"),
                p.get("environment"),
            )
            return JSONResponse({"results": result})
        except ValueError as exc:
            return JSONResponse({"error": str(exc)}, 400)

    async def version_original(request):
        version_id = request.path_params["version_id"]
        path = await run_in_threadpool(library.original, version_id=version_id)
        if path is None or not path.is_file():
            return JSONResponse({"error": "original unavailable"}, 404)
        with library.catalog.connect() as db:
            row = db.execute(
                "SELECT path FROM provenance WHERE version_id=? LIMIT 1", (version_id,)
            ).fetchone()
        filename = row[0].rsplit("/", 1)[-1] if row else "original"
        return FileResponse(path, filename=filename, headers={"Cache-Control": "private, no-store"})

    # No write, upload, shell, ingestion, index or arbitrary filesystem tools.
    app = Starlette(
        routes=[
            Route("/healthz", health),
            Route("/readyz", status),
            Route("/v1/status", status),
            Route("/v1/search", search),
            Route("/v1/theorems", theorems),
            Route("/v1/versions/{version_id}/original", version_original),
            Route("/v1/sources/{source_id}/original", original),
            Route("/v1/sources/{source_id}", source),
            Mount("/", app=mcp_app),
        ],
        lifespan=lifespan,
        middleware=[Middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)],
        max_body_size=128 * 1024,
    )
    return BearerAuth(
        app,
        auth_file=settings.auth_file,
        per_minute=settings.requests_per_minute,
        concurrent=settings.max_concurrent_requests,
    )
