"""Qdrant wrapper.

Everything the pipeline needs from a vector store, and nothing more: create,
upsert, hybrid query, fetch by id, scroll by source, delete by source, count.
The retrieval service talks to this, never to ``qdrant_client`` directly, so
the fusion strategy and the filter translation stay in one place.
"""

from __future__ import annotations

from typing import Any, Iterable

from crypto_kb.embeddings.base import SparseVector
from crypto_kb.index.schema import DENSE_VECTOR, PAYLOAD_INDEXES, SPARSE_VECTOR
from crypto_kb.observability import get_logger

log = get_logger("crypto_kb.index")


class QdrantUnavailable(RuntimeError):
    """qdrant-client is not installed. Install the `index` extra."""


class CollectionMissing(RuntimeError):
    """The collection does not exist, so there is nothing to search.

    Most often this is the embedded ``:memory:`` index seen from a second
    process: ingesting in one command and searching in another gives the
    search a fresh, empty Qdrant. The message says so, because the raw
    client error ("Collection ... not found") reads like data loss.
    """


def is_embedded_path(url: str) -> bool:
    """True for a filesystem location rather than a server URL."""
    return url.startswith(("file://", "./", "../", "/"))


def embedded_path(url: str) -> str:
    return url[len("file://") :] if url.startswith("file://") else url


def is_embedded(url: str) -> bool:
    return url == ":memory:" or is_embedded_path(url)


def _models():
    try:
        from qdrant_client import models
    except ImportError as exc:  # pragma: no cover - depends on install
        raise QdrantUnavailable(
            "qdrant-client is required for indexing and search; "
            "install with `pip install 'crypto-kb[index]'`"
        ) from exc
    return models


class QdrantIndex:
    def __init__(self, settings=None, dimension: int | None = None, client: Any | None = None) -> None:
        from crypto_kb.config import get_settings

        self.settings = settings or get_settings()
        self.collection = self.settings.collection
        self.dimension = dimension or self.settings.dense_dimension
        self._client = client

    # -- connection --------------------------------------------------------

    @property
    def client(self) -> Any:
        if self._client is None:
            try:
                from qdrant_client import QdrantClient
            except ImportError as exc:  # pragma: no cover
                raise QdrantUnavailable(
                    "qdrant-client is required; install with `pip install 'crypto-kb[index]'`"
                ) from exc
            url = self.settings.qdrant_url
            if url == ":memory:":
                # Embedded, in-process: fine for the vertical slice and the
                # eval harness, gone when the process exits.
                self._client = QdrantClient(":memory:")
            elif is_embedded_path(url):
                # Embedded, file-backed: survives the process, so `ingest`
                # then `search` works from separate commands with no server.
                # Single-writer only -- one process may hold the directory.
                self._client = QdrantClient(path=embedded_path(url))
            else:
                self._client = QdrantClient(
                    url=url,
                    api_key=self.settings.qdrant_api_key,
                    timeout=int(self.settings.qdrant_timeout),
                )
        return self._client

    # -- schema ------------------------------------------------------------

    def ensure_collection(self) -> bool:
        """Create the collection and its payload indexes if absent.

        Returns True when it was created. Existing collections are left alone:
        changing vector semantics in place is never correct, so a dimension
        mismatch raises instead.
        """
        models = _models()
        if self.client.collection_exists(self.collection):
            self._check_dimension()
            return False

        self.client.create_collection(
            collection_name=self.collection,
            vectors_config={
                DENSE_VECTOR: models.VectorParams(
                    size=self.dimension, distance=models.Distance.COSINE
                )
            },
            sparse_vectors_config={SPARSE_VECTOR: models.SparseVectorParams()},
        )
        if is_embedded(self.settings.qdrant_url):
            # Embedded mode has no payload indexes -- it filters by scan. The
            # schema is still declared in schema.py so a server-backed
            # collection is built identically; skipping the calls here just
            # avoids a warning per field.
            log.debug("payload_indexes_skipped", reason="embedded qdrant filters by scan")
            return True

        for field, schema in PAYLOAD_INDEXES.items():
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name=field,
                field_schema=schema,
            )
        return True

    def _check_dimension(self) -> None:
        info = self.client.get_collection(self.collection)
        params = getattr(getattr(info, "config", None), "params", None)
        vectors = getattr(params, "vectors", None)
        configured = None
        if isinstance(vectors, dict):
            entry = vectors.get(DENSE_VECTOR)
            configured = getattr(entry, "size", None)
        elif vectors is not None:
            configured = getattr(vectors, "size", None)
        if configured is not None and int(configured) != int(self.dimension):
            raise ValueError(
                f"collection {self.collection!r} holds {configured}-dimensional vectors but the "
                f"configured embedder produces {self.dimension}; bump the collection name "
                "(crypto_knowledge_v2) rather than mixing vector spaces"
            )

    def require_collection(self) -> None:
        """Guard for read paths. Raises ``CollectionMissing`` with the fix."""
        if self.exists():
            return
        if self.settings.qdrant_url == ":memory:":
            raise CollectionMissing(
                f"collection {self.collection!r} does not exist in this process. "
                "CRYPTO_KB_QDRANT_URL is ':memory:', which is an embedded index "
                "that lives and dies with the process -- ingesting in one command "
                "and searching in another cannot work. Either point at a server "
                "(`make qdrant-up`, then CRYPTO_KB_QDRANT_URL=http://localhost:6333) "
                "or use a file-backed embedded index "
                "(CRYPTO_KB_QDRANT_URL=./.kb-index), then re-run `crypto-kb ingest`."
            )
        raise CollectionMissing(
            f"collection {self.collection!r} does not exist at {self.settings.qdrant_url}. "
            "Run `crypto-kb ingest` to build it."
        )

    def drop_collection(self) -> None:
        if self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)

    # -- writes ------------------------------------------------------------

    def upsert(self, points: Iterable[dict[str, Any]]) -> int:
        """Upsert points described as ``{id, dense, sparse, payload}`` dicts."""
        models = _models()
        batch = [
            models.PointStruct(
                id=point["id"],
                vector={
                    DENSE_VECTOR: point["dense"],
                    SPARSE_VECTOR: models.SparseVector(
                        indices=point["sparse"].indices, values=point["sparse"].values
                    )
                    if isinstance(point["sparse"], SparseVector)
                    else models.SparseVector(**point["sparse"]),
                },
                payload=point["payload"],
            )
            for point in points
        ]
        if not batch:
            return 0
        self.client.upsert(collection_name=self.collection, points=batch, wait=True)
        return len(batch)

    def delete_source(self, source_id: str) -> None:
        """Remove every point belonging to a source, parents included."""
        models = _models()
        self.client.delete(
            collection_name=self.collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[models.FieldCondition(key="source_id", match=models.MatchValue(value=source_id))]
                )
            ),
            wait=True,
        )

    def delete_points(self, point_ids: list[str]) -> None:
        if not point_ids:
            return
        models = _models()
        self.client.delete(
            collection_name=self.collection,
            points_selector=models.PointIdsList(points=point_ids),
            wait=True,
        )

    # -- reads -------------------------------------------------------------

    def hybrid_search(
        self,
        dense: list[float],
        sparse: SparseVector,
        limit: int,
        query_filter: Any | None = None,
        prefetch_limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Dense + sparse retrieval fused with reciprocal rank fusion.

        RRF rather than a score-weighted blend: BM25 scores and cosine
        similarities are not on a comparable scale, and any fixed weighting
        between them is a tuning parameter that silently rots as the corpus
        changes. Rank fusion has no such parameter.
        """
        self.require_collection()
        models = _models()
        prefetch_limit = prefetch_limit or max(limit * 4, 40)
        prefetch = [
            models.Prefetch(
                query=dense, using=DENSE_VECTOR, limit=prefetch_limit, filter=query_filter
            )
        ]
        if len(sparse):
            prefetch.append(
                models.Prefetch(
                    query=models.SparseVector(indices=sparse.indices, values=sparse.values),
                    using=SPARSE_VECTOR,
                    limit=prefetch_limit,
                    filter=query_filter,
                )
            )
        response = self.client.query_points(
            collection_name=self.collection,
            prefetch=prefetch,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit,
            with_payload=True,
        )
        return [{"id": str(p.id), "score": float(p.score), "payload": p.payload or {}} for p in response.points]

    def single_mode_search(
        self,
        *,
        mode: str,
        dense: list[float] | None = None,
        sparse: SparseVector | None = None,
        limit: int,
        query_filter: Any | None = None,
    ) -> list[dict[str, Any]]:
        """Dense-only or sparse-only search. Used by the evaluation baselines."""
        self.require_collection()
        models = _models()
        if mode == "dense":
            if dense is None:
                raise ValueError("dense mode needs a dense vector")
            query, using = dense, DENSE_VECTOR
        elif mode == "sparse":
            if sparse is None:
                raise ValueError("sparse mode needs a sparse vector")
            if not len(sparse):
                return []
            query = models.SparseVector(indices=sparse.indices, values=sparse.values)
            using = SPARSE_VECTOR
        else:
            raise ValueError(f"unknown mode {mode!r} (expected 'dense' or 'sparse')")

        response = self.client.query_points(
            collection_name=self.collection,
            query=query,
            using=using,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        )
        return [{"id": str(p.id), "score": float(p.score), "payload": p.payload or {}} for p in response.points]

    def scroll(
        self, query_filter: Any | None = None, limit: int = 256, with_vectors: bool = False
    ) -> list[dict[str, Any]]:
        self.require_collection()
        records, _ = self.client.scroll(
            collection_name=self.collection,
            scroll_filter=query_filter,
            limit=limit,
            with_payload=True,
            with_vectors=with_vectors,
        )
        return [
            {"id": str(r.id), "payload": r.payload or {}, "vector": getattr(r, "vector", None)}
            for r in records
        ]

    def by_chunk_id(self, chunk_id: str) -> dict[str, Any] | None:
        models = _models()
        found = self.scroll(
            query_filter=models.Filter(
                must=[models.FieldCondition(key="chunk_id", match=models.MatchValue(value=chunk_id))]
            ),
            limit=1,
        )
        return found[0] if found else None

    def by_source(self, source_id: str, limit: int = 1024, include_parents: bool = True) -> list[dict[str, Any]]:
        models = _models()
        must = [models.FieldCondition(key="source_id", match=models.MatchValue(value=source_id))]
        if not include_parents:
            must.append(models.FieldCondition(key="is_parent", match=models.MatchValue(value=False)))
        found = self.scroll(query_filter=models.Filter(must=must), limit=limit)
        return sorted(found, key=lambda r: r["payload"].get("chunk_index", 0))

    def count(self, query_filter: Any | None = None) -> int:
        result = self.client.count(
            collection_name=self.collection, count_filter=query_filter, exact=True
        )
        return int(result.count)

    def exists(self) -> bool:
        return bool(self.client.collection_exists(self.collection))
