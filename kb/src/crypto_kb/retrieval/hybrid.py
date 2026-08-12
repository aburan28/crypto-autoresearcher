"""The retrieval service.

Dense and sparse retrieval, fused by rank, filtered, deduplicated,
diversified, optionally reranked, then truncated to top-k. Kept free of any
MCP or transport concern so it can be driven from the CLI, the evaluation
harness, and the server with identical behaviour -- an evaluation that
measures a different code path than the agents use measures nothing.
"""

from __future__ import annotations

import time
from typing import Any

from crypto_kb.models import (
    ContextResponse,
    SearchFilters,
    SearchResponse,
    SearchResult,
    SourceDocument,
)
from crypto_kb.observability import Metrics, QueryLog, get_logger
from crypto_kb.retrieval import filters as filter_module
from crypto_kb.retrieval.diversify import DiversityCaps, deduplicate, diversify
from crypto_kb.retrieval.formatting import to_result
from crypto_kb.text import identifiers

log = get_logger("crypto_kb.retrieval")


class KnowledgeRetriever:
    def __init__(
        self,
        index,
        dense_embedder,
        sparse_embedder,
        settings=None,
        reranker=None,
        query_log: QueryLog | None = None,
    ) -> None:
        from crypto_kb.config import get_settings

        self.settings = settings or get_settings()
        self.index = index
        self.dense = dense_embedder
        self.sparse = sparse_embedder
        self.reranker = reranker
        self.query_log = query_log or QueryLog(self.settings.query_log_path)
        self.caps = DiversityCaps(
            max_per_source=self.settings.max_chunks_per_source,
            max_per_parent=self.settings.max_chunks_per_parent,
            max_results=self.settings.max_top_k,
        )

    # -- search ------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int | None = None,
        filters: SearchFilters | None = None,
        client: str | None = None,
        agent: str | None = None,
        task_id: str | None = None,
        mode: str = "hybrid",
    ) -> SearchResponse:
        started = time.perf_counter()
        query_id = QueryLog.new_query_id()
        notes: list[str] = []

        requested = top_k if top_k is not None else self.settings.default_top_k
        effective_k = max(1, min(requested, self.settings.max_top_k))
        if requested > effective_k:
            notes.append(f"top_k clamped from {requested} to {effective_k}")

        query_filter = filter_module.build_filter(filters)
        candidate_limit = max(
            effective_k * self.settings.candidate_multiplier, self.settings.min_candidates
        )

        hits = self._retrieve(query, candidate_limit, query_filter, mode)

        # An identifier in the query is a request for that document, not a
        # ranking hint. Lexical scoring cannot honour it -- a widely-cited id
        # appears in more text in the documents citing it than in the one it
        # names -- so exact matches are looked up by payload and placed first.
        exact = self._exact_identifier_hits(query, filters, effective_k)
        if exact:
            named = ", ".join(dict.fromkeys(h["payload"].get("source_id", "") for h in exact))
            notes.append(f"exact identifier match placed first: {named}")
            known = {h["id"] for h in exact}
            hits = exact + [hit for hit in hits if hit["id"] not in known]

        results = [to_result(hit, self.settings.max_chars_per_result) for hit in hits]

        results, duplicates = deduplicate(results)
        if duplicates:
            notes.append(f"{duplicates} duplicate passages removed")

        if self.reranker is not None and self.reranker.model_id != "none" and results:
            # Exact identifier matches keep their place: the caller named the
            # document, and a reranker's opinion of the passage does not
            # override that.
            exact_ids = {hit["id"] for hit in exact}
            pinned = [r for r in results if r.chunk_id in _chunk_ids(exact)]
            rest = [r for r in results if r.chunk_id not in _chunk_ids(exact)]
            scores = self.reranker.rerank(query, [r.text for r in rest])
            ordered = sorted(zip(rest, scores), key=lambda pair: pair[1], reverse=True)
            results = pinned + [
                result.model_copy(update={"score": float(score)}) for result, score in ordered
            ]
            notes.append(f"reranked by {self.reranker.model_id} ({len(exact_ids)} exact matches pinned)")

        kept, suppressed = diversify(results, self.caps, effective_k)
        if suppressed:
            notes.append(
                f"{suppressed} results suppressed by diversity caps "
                f"(max {self.caps.max_per_source}/source, {self.caps.max_per_parent}/section)"
            )

        latency_ms = int((time.perf_counter() - started) * 1000)
        response = SearchResponse(
            query=query,
            results=kept,
            total_candidates=len(hits),
            filters_applied=filter_module.describe(filters),
            query_id=query_id,
            latency_ms=latency_ms,
            notes=notes,
        )

        self.query_log.record(
            query_id=query_id,
            query=query,
            filters=response.filters_applied,
            retrieved_chunk_ids=[r.chunk_id for r in kept],
            scores=[r.score for r in kept],
            client=client,
            agent=agent,
            task_id=task_id,
            latency_ms=latency_ms,
            notes=notes,
        )
        self._count_query(client, "search_knowledge", latency_ms, len(kept))
        return response

    def _exact_identifier_hits(
        self, query: str, filters: SearchFilters | None, top_k: int
    ) -> list[dict[str, Any]]:
        """Chunks whose document is named by an identifier in the query.

        Returns at most ``max_chunks_per_source`` opening chunks per matched
        document -- enough to show what it is, not enough to crowd out
        everything else when a query names several.
        """
        tokens = [token for token in identifiers(query)]
        if not tokens:
            return []

        query_filter = filter_module.build_filter(filters, identity_tokens=tokens)
        try:
            records = self.index.scroll(query_filter=query_filter, limit=top_k * 4)
        except Exception as exc:  # noqa: BLE001 - a failed lookup must not fail the search
            log.warning("exact_lookup_failed", error=str(exc))
            return []

        per_source: dict[str, int] = {}
        chosen: list[dict[str, Any]] = []
        for record in sorted(records, key=lambda r: r["payload"].get("chunk_index", 0)):
            source_id = record["payload"].get("source_id", "")
            if per_source.get(source_id, 0) >= self.caps.max_per_source:
                continue
            per_source[source_id] = per_source.get(source_id, 0) + 1
            # Scroll returns no score. These are exact matches on a payload
            # field, so 1.0 states the match rather than estimating similarity.
            chosen.append({"id": record["id"], "score": 1.0, "payload": record["payload"]})
        return chosen

    def _retrieve(self, query: str, limit: int, query_filter: Any, mode: str) -> list[dict[str, Any]]:
        dense_vector = self.dense.embed_query(query)
        sparse_vector = self.sparse.embed_query(query)
        if mode == "hybrid":
            return self.index.hybrid_search(
                dense=dense_vector, sparse=sparse_vector, limit=limit, query_filter=query_filter
            )
        return self.index.single_mode_search(
            mode=mode,
            dense=dense_vector,
            sparse=sparse_vector,
            limit=limit,
            query_filter=query_filter,
        )

    # -- context -----------------------------------------------------------

    def get_context(self, chunk_id: str, before: int = 1, after: int = 1) -> ContextResponse:
        record = self.index.by_chunk_id(chunk_id)
        if record is None:
            return ContextResponse(
                chunk_id=chunk_id, source_id="", title="", notes=["chunk_id not found"]
            )

        payload = record["payload"]
        source_id = payload.get("source_id", "")
        before = max(0, min(before, 3))
        after = max(0, min(after, 3))

        siblings = self.index.by_source(source_id, include_parents=False)
        position = next(
            (i for i, s in enumerate(siblings) if s["payload"].get("chunk_id") == chunk_id), None
        )
        notes: list[str] = []
        if position is None:
            notes.append("chunk not found among its source's chunks; neighbours unavailable")
            neighbours_before: list[dict[str, Any]] = []
            neighbours_after: list[dict[str, Any]] = []
        else:
            neighbours_before = siblings[max(0, position - before) : position]
            neighbours_after = siblings[position + 1 : position + 1 + after]

        parent_text = None
        parent_id = payload.get("parent_id")
        if parent_id:
            parent = self.index.by_chunk_id(parent_id)
            if parent is not None:
                parent_text = parent["payload"].get("text")
            else:
                notes.append("parent section not in the index")

        return ContextResponse(
            chunk_id=chunk_id,
            source_id=source_id,
            title=payload.get("title", ""),
            section_path=list(payload.get("section_path") or []),
            before=[to_result(_as_hit(s)) for s in neighbours_before],
            chunk=to_result(_as_hit(record)),
            after=[to_result(_as_hit(s)) for s in neighbours_after],
            parent_text=parent_text,
            notes=notes,
        )

    # -- source ------------------------------------------------------------

    def get_source(self, source_id: str) -> SourceDocument | None:
        """Metadata, table of contents, and a bounded summary. Never the document."""
        records = self.index.by_source(source_id)
        if not records:
            return None

        children = [r for r in records if not r["payload"].get("is_parent")]
        first = (children or records)[0]["payload"]

        # Built from the headings each chunk covers, not from `section_path`:
        # a chunk that spans two short sections is attributed to their common
        # ancestor, so section_path alone would drop both headings.
        toc: list[str] = []
        for record in children:
            for heading in record["payload"].get("section_headings") or []:
                if heading and heading not in toc:
                    toc.append(heading)

        summary = None
        if children:
            head = children[0]["payload"].get("text", "")
            summary = head[:1200].rstrip()
            if len(head) > 1200:
                summary += " [...]"

        return SourceDocument(
            source_id=source_id,
            title=first.get("title", ""),
            source_type=first.get("source_type", ""),
            source_uri=first.get("source_uri", ""),
            authors=list(first.get("authors") or []),
            publication_year=first.get("publication_year"),
            claim_status=first.get("claim_status"),
            evidence_level=first.get("evidence_level"),
            authority=first.get("authority"),
            superseded=bool(first.get("superseded", False)),
            superseded_by=first.get("superseded_by"),
            experiment_id=first.get("experiment_id"),
            run_ids=list(first.get("run_ids") or []),
            git_commit=first.get("git_commit"),
            topics=list(first.get("topics") or []),
            primitive=list(first.get("primitive") or []),
            field_type=list(first.get("field_type") or []),
            table_of_contents=toc,
            chunk_count=len(children),
            summary=summary,
            content_hash=first.get("content_hash"),
            indexed_at=first.get("indexed_at"),
        )

    # -- related -----------------------------------------------------------

    def find_related(
        self, source_id: str, top_k: int | None = None, filters: SearchFilters | None = None
    ) -> SearchResponse:
        """Sources covering similar ground, excluding the source itself.

        The query is built from the document's own title, topics, and opening
        passages rather than from a stored centroid: a centroid over a whole
        paper drifts toward its most verbose section, which for a crypto paper
        is usually the preliminaries -- and every paper's preliminaries look
        alike.
        """
        started = time.perf_counter()
        records = self.index.by_source(source_id, include_parents=False)
        if not records:
            return SearchResponse(
                query=f"related:{source_id}", results=[], notes=["source_id not found"]
            )

        payload = records[0]["payload"]
        seed_parts = [payload.get("title", "")]
        seed_parts.extend(payload.get("topics") or [])
        seed_parts.extend(r["payload"].get("text", "")[:1500] for r in records[:2])
        seed = "\n".join(part for part in seed_parts if part)

        effective_k = max(1, min(top_k or self.settings.default_top_k, self.settings.max_top_k))
        query_filter = filter_module.build_filter(filters, exclude_source_ids=[source_id])
        hits = self.index.hybrid_search(
            dense=self.dense.embed_query(seed),
            sparse=self.sparse.embed_query(seed),
            limit=max(effective_k * self.settings.candidate_multiplier, self.settings.min_candidates),
            query_filter=query_filter,
        )
        results = [to_result(hit, self.settings.max_chars_per_result) for hit in hits]
        results, _ = deduplicate(results)
        # One passage per related source: the caller asked which documents are
        # related, not which passages.
        kept, suppressed = diversify(
            results, DiversityCaps(max_per_source=1, max_per_parent=1, max_results=effective_k),
            effective_k,
        )

        latency_ms = int((time.perf_counter() - started) * 1000)
        notes = [f"related to {source_id}"]
        if suppressed:
            notes.append(f"{suppressed} additional passages from the same sources suppressed")
        return SearchResponse(
            query=f"related:{source_id}",
            results=kept,
            total_candidates=len(hits),
            filters_applied=filter_module.describe(filters),
            latency_ms=latency_ms,
            notes=notes,
        )

    # -- helpers -----------------------------------------------------------

    def _count_query(self, client: str | None, tool: str, latency_ms: int, kept: int) -> None:
        try:
            metrics = Metrics.instance()
        except Exception:  # pragma: no cover - prometheus optional at runtime
            return
        metrics.queries.labels(client=client or "unknown", tool=tool).inc()
        metrics.query_latency.labels(tool=tool).observe(latency_ms / 1000.0)
        if kept == 0:
            metrics.empty_results.inc()


def _chunk_ids(hits: list[dict[str, Any]]) -> set[str]:
    return {hit["payload"].get("chunk_id", "") for hit in hits}


def _as_hit(record: dict[str, Any]) -> dict[str, Any]:
    return {"id": record.get("id"), "score": 0.0, "payload": record.get("payload", {})}


def build_retriever(settings=None) -> KnowledgeRetriever:
    from crypto_kb.config import get_settings
    from crypto_kb.embeddings.dense import build_dense_embedder
    from crypto_kb.embeddings.reranker import build_reranker
    from crypto_kb.embeddings.sparse import build_sparse_embedder
    from crypto_kb.index import build_index
    from crypto_kb.storage import build_store

    settings = settings or get_settings()
    store = build_store(settings)
    dense = build_dense_embedder(settings)
    sparse = build_sparse_embedder(store, settings)
    index = build_index(settings, dimension=dense.dimension)
    return KnowledgeRetriever(
        index=index,
        dense_embedder=dense,
        sparse_embedder=sparse,
        settings=settings,
        reranker=build_reranker(settings),
    )
