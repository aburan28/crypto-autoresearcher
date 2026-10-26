from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from urllib.parse import quote

from research_kb.catalog import Catalog
from research_kb.config import Settings


class Library:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.settings.home = self.settings.home.expanduser().resolve()
        self.catalog = Catalog(self.settings.database)
        self._dense = None
        self._hybrid_cache = None

    def require_ready(self):
        if not self.catalog.status().get("ready"):
            raise RuntimeError(
                "knowledge base has no active sources; register and refresh or import a bundle"
            )

    def status(self):
        status = self.catalog.status()
        pointer = self.settings.home / "active-index.json"
        active_index = json.loads(pointer.read_text()) if pointer.exists() else None
        return {
            **status,
            "backend": "sqlite+qdrant" if self.settings.qdrant_url else "sqlite-fts5",
            "active_index": active_index,
            "hybrid_current": bool(active_index and active_index["revision"] == status.get("revision")),
            "shared_home": str(self.settings.home),
            "network_fetch_on_search": False,
        }

    @property
    def dense(self):
        if self._dense is None:
            from crypto_kb.embeddings.dense import HashingDenseEmbedder, SentenceTransformerEmbedder

            if self.settings.dense_backend == "hashing":
                self._dense = HashingDenseEmbedder(dimension=self.settings.dense_dimension)
            elif self.settings.dense_backend == "sentence-transformers":
                model_path = Path(self.settings.dense_model)
                if not model_path.is_dir():
                    raise RuntimeError("dense_model must point to a pre-cached local model directory")
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer(str(model_path), local_files_only=True, device="cpu")
                if model.get_sentence_embedding_dimension() != self.settings.dense_dimension:
                    raise ValueError("configured dense dimension differs from the cached model")
                self._dense = SentenceTransformerEmbedder(
                    str(model_path), self.settings.dense_dimension, model
                )
            else:
                raise ValueError("unknown dense backend")
        return self._dense

    def index(self):
        """Build an immutable index and publish its stats and collection together."""
        if not self.settings.qdrant_url or self.settings.qdrant_url == ":memory:":
            raise ValueError("index requires a persistent Qdrant server URL or embedded path")
        from crypto_kb.config import Settings as EngineSettings
        from crypto_kb.embeddings.sparse import Bm25SparseEmbedder, SparseStats
        from crypto_kb.hashing import point_id
        from crypto_kb.index.qdrant import QdrantIndex
        from crypto_kb.index.schema import PAYLOAD_INDEXES

        PAYLOAD_INDEXES["origin_repositories"] = "keyword"
        with self.catalog.connect() as db:
            rows = [
                dict(r)
                for r in db.execute(
                    "SELECT p.*,d.id document_id,d.kind,v.metadata FROM passages p JOIN versions v ON p.version_id=v.id JOIN documents d ON v.document_id=d.id WHERE v.id=d.active_version AND EXISTS(SELECT 1 FROM locations l WHERE l.document_id=d.id AND l.version_id=v.id AND l.present=1)"
                )
            ]
        stats = SparseStats()
        per_version = {}
        for row in rows:
            if not row["is_parent"]:
                per_version.setdefault(row["version_id"], []).append(row["text"])
        for texts in per_version.values():
            stats.observe(texts)
        sparse = Bm25SparseEmbedder(stats=stats)
        generation = uuid.uuid4().hex[:12]
        collection = self.settings.collection + "_" + generation
        settings = EngineSettings(
            qdrant_url=self.settings.qdrant_url,
            qdrant_api_key=self.settings.qdrant_api_key,
            collection=collection,
            dense_dimension=self.settings.dense_dimension,
        )
        index = QdrantIndex(settings, dimension=self.settings.dense_dimension)
        index.ensure_collection()
        try:
            for offset in range(0, len(rows), 64):
                points = []
                group = rows[offset : offset + 64]
                texts = [r["title"] + "\n" + r["text"] for r in group]
                for row, dense, sp in zip(
                    group, self.dense.embed_documents(texts), sparse.embed_documents(texts)
                ):
                    enriched = self.catalog.enrich(row)
                    payload = {
                        **enriched,
                        "source_type": row["kind"],
                        "is_parent": bool(row["is_parent"]),
                        "superseded": bool(enriched.get("superseded", False)),
                    }
                    points.append(
                        {
                            "id": str(point_id(row["document_id"], row["chunk_index"], row["content_hash"])),
                            "dense": dense,
                            "sparse": sp,
                            "payload": payload,
                        }
                    )
                index.upsert(points)
            # Save exactly the statistics used by the published collection.
            from dataclasses import asdict

            stats_path = self.settings.home / "indexes" / (generation + ".json")
            stats_path.parent.mkdir(parents=True, exist_ok=True)
            stats_path.write_text(json.dumps(asdict(stats)))
            pointer = {
                "collection": collection,
                "stats": str(stats_path),
                "revision": self.catalog.status()["revision"],
                "dense_backend": self.settings.dense_backend,
                "dense_model": self.settings.dense_model,
                "dimension": self.settings.dense_dimension,
                "points": len(rows),
            }
            temp = self.settings.home / "active-index.json.tmp"
            temp.write_text(json.dumps(pointer, indent=2))
            os.replace(temp, self.settings.home / "active-index.json")
        finally:
            index.client.close()
        return pointer

    def _index_reader(self):
        from crypto_kb.config import Settings as EngineSettings
        from crypto_kb.embeddings.sparse import Bm25SparseEmbedder, SparseStats
        from crypto_kb.index.qdrant import QdrantIndex

        status = self.status()
        active = status["active_index"]
        if not active or not status["hybrid_current"]:
            raise RuntimeError("hybrid index is missing or stale; operator must run research-kb index")
        if (active["dense_backend"], active["dense_model"], active["dimension"]) != (
            self.settings.dense_backend,
            self.settings.dense_model,
            self.settings.dense_dimension,
        ):
            raise RuntimeError("embedding configuration differs from the active index; rebuild the index")
        if not self._hybrid_cache or self._hybrid_cache[0] != active["collection"]:
            if self._hybrid_cache:
                self._hybrid_cache[1].client.close()
            settings = EngineSettings(
                qdrant_url=self.settings.qdrant_url,
                qdrant_api_key=self.settings.qdrant_api_key,
                collection=active["collection"],
                dense_dimension=self.settings.dense_dimension,
            )
            stats = SparseStats(**json.loads(Path(active["stats"]).read_text()))
            self._hybrid_cache = (
                active["collection"],
                QdrantIndex(settings),
                Bm25SparseEmbedder(stats=stats),
            )
        return self._hybrid_cache[1:]

    def search(self, query, top_k=6, repo=None, source_type=None, mode="lexical", include_superseded=False):
        self.require_ready()
        if mode not in {"lexical", "hybrid"}:
            raise ValueError("mode must be lexical or hybrid")
        if source_type not in {None, "paper", "proof", "internal-note"}:
            raise ValueError("unsupported source_type")
        started = time.perf_counter()
        results = self.catalog.search(query, top_k, repo, source_type, include_superseded)
        if mode == "hybrid":
            from qdrant_client import models

            index, sparse = self._index_reader()
            must = [models.FieldCondition(key="is_parent", match=models.MatchValue(value=False))]
            if not include_superseded:
                must.append(models.FieldCondition(key="superseded", match=models.MatchValue(value=False)))
            if repo:
                must.append(
                    models.FieldCondition(key="origin_repositories", match=models.MatchValue(value=repo))
                )
            if source_type:
                must.append(
                    models.FieldCondition(key="source_type", match=models.MatchValue(value=source_type))
                )
            hits = index.hybrid_search(
                self.dense.embed_query(query),
                sparse.embed_query(query),
                query_filter=models.Filter(must=must),
                limit=max(20, min(top_k, 10) * 4),
            )
            # Fuse catalog and vector ranks; exact aliases remain first.
            with self.catalog.connect() as db:
                exact = db.execute(
                    "SELECT 1 FROM aliases WHERE alias=? COLLATE NOCASE LIMIT 1", (query,)
                ).fetchone()
            ranks, merged = {}, {}
            for weight, group in [(2 if exact else 1, results), (1, [h["payload"] for h in hits])]:
                for rank, result in enumerate(group, 1):
                    key = result["chunk_id"]
                    ranks[key] = ranks.get(key, 0) + weight / (60 + rank)
                    merged[key] = result
            results = []
            per_source = {}
            for key in sorted(ranks, key=ranks.get, reverse=True):
                result = merged[key]
                if per_source.get(result["source_id"], 0) >= 2:
                    continue
                per_source[result["source_id"]] = per_source.get(result["source_id"], 0) + 1
                result["score"] = ranks[key]
                results.append(result)
                if len(results) >= max(1, min(top_k, 10)):
                    break
        results = [self.with_source_link(r) for r in results]
        return {
            "query": query,
            "results": results,
            "mode": mode,
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
            "revision": self.catalog.status().get("revision"),
            "notes": ["Scores measure relevance, not evidence quality.", "No result does not prove absence."],
        }

    def source(self, source_id):
        return self.with_source_link(self.catalog.source(source_id))

    def with_source_link(self, result):
        if result.get("version_id"):
            if self.settings.public_url:
                result["source_uri"] = (
                    self.settings.public_url.rstrip("/")
                    + "/v1/versions/"
                    + quote(result["version_id"], safe="")
                    + "/original"
                )
            else:
                path = self.original(version_id=result["version_id"])
                result["source_uri"] = path.as_uri() if path else None
        return result

    def context(self, chunk_id, before=1, after=1):
        result = self.catalog.context(chunk_id, before, after)
        if result.get("found"):
            self.with_source_link(result["chunk"])
            for row in result["context"]:
                self.with_source_link(row)
        return result

    def original(self, source_id=None, version_id=None):
        with self.catalog.connect() as db:
            if version_id:
                row = db.execute("SELECT original_key FROM versions WHERE id=?", (version_id,)).fetchone()
            else:
                row = db.execute(
                    "SELECT v.original_key FROM documents d JOIN versions v ON v.id=d.active_version WHERE d.id=?",
                    (source_id,),
                ).fetchone()
        if row is None:
            return None
        path = (self.settings.home / row[0]).resolve()
        if not path.is_relative_to(self.settings.home / "objects"):
            raise RuntimeError("invalid original object location")
        return path

    def related(self, source_id, top_k=5):
        source = self.source(source_id)
        if not source.get("found"):
            return source
        result = self.search(source["title"], 10)
        result["results"] = [r for r in result["results"] if r["source_id"] != source["source_id"]][
            : max(1, min(top_k, 10))
        ]
        return result
