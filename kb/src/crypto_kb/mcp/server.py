"""The agent-facing MCP server.

Four read-only tools. Ingestion and deletion are deliberately absent: an agent
that can write to the index can change what every other agent believes the
corpus says, and no research conclusion downstream of that is auditable. The
write path is the ingestion worker, driven by S3 events, and nothing else.

Every bound is enforced here as well as in the retriever -- ``top_k`` is
clamped, context expansion is capped at three chunks either side, and
``get_source`` returns a summary and a table of contents rather than a
document. The server is the only surface agents reach, so it is where limits
have to hold even if a caller ignores the documented ones.
"""

from __future__ import annotations

import os
from typing import Any

from crypto_kb.models import ClaimStatus, EvidenceLevel, SearchFilters, SourceType
from crypto_kb.observability import configure_logging, get_logger

log = get_logger("crypto_kb.mcp")

_retriever = None


def get_retriever():
    """Built once, on first use, so the process starts without touching Qdrant."""
    global _retriever
    if _retriever is None:
        from crypto_kb.retrieval import build_retriever

        _retriever = build_retriever()
    return _retriever


def set_retriever(retriever) -> None:
    """Inject a retriever. Used by tests and by embedded hosts."""
    global _retriever
    _retriever = retriever


def _as_list(value: str | list[str] | None) -> list[str] | None:
    """Accept a scalar or a list -- clients differ, and both are unambiguous."""
    if value is None:
        return None
    if isinstance(value, str):
        return [value] if value else None
    return list(value) or None


def build_filters(
    source_type: str | list[str] | None = None,
    field_type: str | list[str] | None = None,
    primitive: str | list[str] | None = None,
    claim_status: str | list[str] | None = None,
    evidence_level: str | list[str] | None = None,
    curves: str | list[str] | None = None,
    topics: str | list[str] | None = None,
    source_id: str | list[str] | None = None,
    experiment_id: str | list[str] | None = None,
    include_superseded: bool = False,
) -> SearchFilters:
    """Validate agent-supplied filter values against the closed vocabularies.

    An unknown value raises rather than being dropped: silently ignoring
    ``claim_status="verified"`` would return unfiltered results that the caller
    believes are filtered, which is the failure this whole layer exists to
    prevent.
    """
    return SearchFilters(
        source_type=[SourceType(v) for v in (_as_list(source_type) or [])] or None,
        field_type=_as_list(field_type),
        primitive=_as_list(primitive),
        claim_status=[ClaimStatus(v) for v in (_as_list(claim_status) or [])] or None,
        evidence_level=[EvidenceLevel(v) for v in (_as_list(evidence_level) or [])] or None,
        curves=_as_list(curves),
        topics=_as_list(topics),
        source_id=_as_list(source_id),
        experiment_id=_as_list(experiment_id),
        superseded=None if include_superseded else False,
    )


def build_server(name: str = "Crypto Knowledge Base"):
    """Construct the FastMCP app. Importable without running it."""
    try:
        from fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - depends on install
        raise RuntimeError(
            "fastmcp is required to run the MCP server; "
            "install with `pip install 'crypto-kb[mcp]'`"
        ) from exc

    mcp = FastMCP(name)

    @mcp.tool
    def search_knowledge(
        query: str,
        top_k: int = 6,
        source_type: str | list[str] | None = None,
        field_type: str | list[str] | None = None,
        primitive: str | list[str] | None = None,
        claim_status: str | list[str] | None = None,
        evidence_level: str | list[str] | None = None,
        curves: str | list[str] | None = None,
        topics: str | list[str] | None = None,
        experiment_id: str | list[str] | None = None,
        include_superseded: bool = False,
    ) -> dict[str, Any]:
        """Search cryptography papers, experiments, proofs, and research notes.

        Hybrid dense + lexical retrieval, so exact identifiers (EXP-GGM-001,
        P-256, ePrint 2026/1486, Theorem 4.3) work as well as paraphrases.
        Results are capped at 2 passages per source so contradictory sources
        stay visible. Superseded material is excluded unless asked for.

        Retrieval score is a relevance signal only. Evidence quality is in
        `claim_status`, `evidence_level`, and `authority` -- read those, not
        the score, before treating a passage as established.
        """
        filters = build_filters(
            source_type=source_type,
            field_type=field_type,
            primitive=primitive,
            claim_status=claim_status,
            evidence_level=evidence_level,
            curves=curves,
            topics=topics,
            experiment_id=experiment_id,
            include_superseded=include_superseded,
        )
        response = get_retriever().search(
            query=query,
            top_k=top_k,
            filters=filters,
            client=os.environ.get("CRYPTO_KB_CLIENT", "mcp"),
            agent=os.environ.get("CRYPTO_KB_AGENT"),
            task_id=os.environ.get("CRYPTO_KB_TASK_ID"),
        )
        return response.model_dump(mode="json")

    @mcp.tool
    def get_context(chunk_id: str, before: int = 1, after: int = 1) -> dict[str, Any]:
        """Return the passages surrounding a chunk, plus its parent section.

        Call this only for results that actually affect a conclusion; each
        expansion costs context. `before` and `after` are capped at 3.
        """
        response = get_retriever().get_context(
            chunk_id=chunk_id, before=min(before, 3), after=min(after, 3)
        )
        return response.model_dump(mode="json")

    @mcp.tool
    def get_source(source_id: str) -> dict[str, Any]:
        """Return a source's metadata, section list, and a bounded summary.

        Never returns the whole document. `source_uri` points at the canonical
        object if the full text is genuinely needed.
        """
        document = get_retriever().get_source(source_id)
        if document is None:
            return {"source_id": source_id, "found": False}
        payload = document.model_dump(mode="json")
        payload["found"] = True
        return payload

    @mcp.tool
    def find_related(source_id: str, top_k: int = 5) -> dict[str, Any]:
        """Find other sources covering similar ground, one passage each.

        Useful for spotting prior internal work before proposing an experiment,
        and for finding the papers a finding should have cited.
        """
        response = get_retriever().find_related(source_id=source_id, top_k=top_k)
        return response.model_dump(mode="json")

    return mcp


def main() -> None:  # pragma: no cover - process entry point
    from crypto_kb.config import get_settings

    settings = get_settings()
    configure_logging(settings.log_level)
    if settings.metrics_port:
        from crypto_kb.observability import start_metrics_server

        start_metrics_server(settings.metrics_port)
    if settings.qdrant_url == ":memory:":
        # Every tool would answer "nothing found", correctly and uselessly, and
        # an agent has no way to tell an empty index from an absent result.
        log.warning(
            "qdrant_url_is_in_memory",
            detail=(
                "an in-process index is empty in a fresh server; set "
                "CRYPTO_KB_QDRANT_URL in kb/.env to a running Qdrant "
                "(make qdrant-up) or a file-backed path"
            ),
        )
    log.info("mcp_server_starting", collection=settings.collection, qdrant=settings.qdrant_url)
    build_server().run()


if __name__ == "__main__":  # pragma: no cover
    main()
