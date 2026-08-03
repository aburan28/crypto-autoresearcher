"""The ingestion state machine.

DISCOVERED -> DOWNLOADED -> PARSED -> NORMALIZED -> CHUNKED -> EMBEDDED ->
INDEXED, with the manifest updated at each transition so a crash leaves a
readable position rather than an unknown one.

Two properties matter more than throughput:

* **Idempotence.** Re-ingesting a document writes the same point ids over the
  same rows and deletes any point the new version no longer produces. Running
  the same backfill twice is a no-op, which is what makes at-least-once queue
  delivery safe.
* **Fail-closed.** A document that cannot be parsed, or whose sidecar is
  missing or invalid, is recorded FAILED with the reason and left out of the
  index. It is never indexed with guessed metadata -- a paper filed under the
  wrong claim status is worse than one that is absent, because absence is
  visible and a wrong filter result is not.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from crypto_kb import CHUNKER_VERSION
from crypto_kb.chunking import ChunkingConfig, HierarchicalChunker
from crypto_kb.config import IGNORED_INPUT_PREFIXES, NORMALIZED_DOCLING_PREFIX, NORMALIZED_MARKDOWN_PREFIX
from crypto_kb.hashing import document_fingerprint, point_id, sha256_bytes
from crypto_kb.metadata import METADATA_SUFFIX, MetadataError, load_metadata, metadata_fingerprint
from crypto_kb.models import Chunk, IngestState, Manifest, SourceMetadata, utcnow
from crypto_kb.observability import get_logger
from crypto_kb.parsing import UnsupportedSource, parse
from crypto_kb.storage.manifests import ManifestStore

log = get_logger("crypto_kb.ingest")


@dataclass
class IngestResult:
    source_id: str | None
    key: str
    state: IngestState
    chunk_count: int = 0
    parent_count: int = 0
    skipped: bool = False
    reason: str | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.state in {IngestState.INDEXED, IngestState.DELETED}


class IngestionPipeline:
    def __init__(
        self,
        store,
        index,
        dense_embedder,
        sparse_embedder,
        settings=None,
        manifests: ManifestStore | None = None,
        chunker: HierarchicalChunker | None = None,
    ) -> None:
        from crypto_kb.config import get_settings

        self.settings = settings or get_settings()
        self.store = store
        self.index = index
        self.dense = dense_embedder
        self.sparse = sparse_embedder
        self.manifests = manifests or ManifestStore(store)
        self.chunker = chunker or HierarchicalChunker(ChunkingConfig.from_settings(self.settings))
        self._collection_present: bool | None = None

    # -- entry points ------------------------------------------------------

    def should_ingest(self, key: str) -> tuple[bool, str | None]:
        """Whether ``key`` is an ingestible source object."""
        if key.endswith(METADATA_SUFFIX):
            return False, "metadata sidecar"
        if any(key.startswith(prefix) for prefix in IGNORED_INPUT_PREFIXES):
            return False, "derived artifact prefix"
        if not key.startswith(self.settings.source_prefix()):
            return False, f"outside {self.settings.source_prefix()}"
        return True, None

    def ingest_key(self, key: str, force: bool = False, save_stats: bool = True) -> IngestResult:
        """Run the full state machine for one object key.

        ``save_stats`` is False during a backfill, which flushes the shared
        sparse-statistics table periodically instead of once per document --
        that file is corpus-sized, and writing it per document is quadratic.
        """
        ingestible, reason = self.should_ingest(key)
        if not ingestible:
            return IngestResult(None, key, IngestState.REJECTED, skipped=True, reason=reason)

        manifest: Manifest | None = None
        try:
            info = self.store.head(key)
            if info is None:
                return IngestResult(None, key, IngestState.REJECTED, skipped=True, reason="object not found")

            metadata, warnings = load_metadata(self.store, key)
            data = self.store.get(key)
            source_hash = sha256_bytes(data)
            meta_hash = metadata_fingerprint(metadata)

            # The parser version is part of the fingerprint, so it has to be
            # known before the skip check -- selecting the parser is cheap,
            # running it is not.
            from crypto_kb.parsing import select_parser

            parser = select_parser(key)
            fingerprint = document_fingerprint(
                source_content_hash=source_hash,
                metadata_hash=meta_hash,
                parser_version=parser.version,
                chunker_version=CHUNKER_VERSION,
                embedding_model_version=self.settings.embedding_model_version(),
            )

            existing = self.manifests.get(metadata.source_id)
            if (
                not force
                and existing is not None
                and existing.status == IngestState.INDEXED
                and existing.document_fingerprint == fingerprint
                and existing.collection == self.settings.collection
                # A manifest saying INDEXED is only evidence about the index if
                # the collection is still there. Dropped collections and
                # ephemeral (in-memory) ones would otherwise make every
                # document skip into an empty index.
                and self._collection_exists()
            ):
                return IngestResult(
                    metadata.source_id,
                    key,
                    IngestState.INDEXED,
                    chunk_count=existing.chunk_count,
                    parent_count=existing.parent_chunk_count,
                    skipped=True,
                    reason="fingerprint unchanged",
                    warnings=list(existing.warnings),
                )

            manifest = Manifest(
                source_id=metadata.source_id,
                s3_bucket=getattr(self.store, "bucket", None),
                s3_key=key,
                s3_version_id=info.version_id,
                etag=info.etag,
                source_sha256=source_hash,
                metadata_hash=meta_hash,
                document_fingerprint=fingerprint,
                parser=parser.name,
                parser_version=parser.version,
                chunker_version=CHUNKER_VERSION,
                dense_model=self.dense.model_id,
                sparse_model=self.sparse.model_id,
                collection=self.settings.collection,
                status=IngestState.DOWNLOADED,
                warnings=list(warnings),
            )
            self.manifests.put(manifest)

            document = parse(data, key)
            manifest.warnings.extend(document.warnings)
            manifest.status = IngestState.PARSED
            self.manifests.put(manifest)

            self._write_normalized(metadata.source_id, document)
            manifest.status = IngestState.NORMALIZED
            self.manifests.put(manifest)

            chunks = self.chunker.chunk(document.markdown, metadata.source_id)
            if not chunks:
                manifest.status = IngestState.REJECTED
                manifest.error = "produced no chunks"
                self.manifests.put(manifest)
                return IngestResult(
                    metadata.source_id, key, IngestState.REJECTED, reason="produced no chunks",
                    warnings=manifest.warnings,
                )
            manifest.status = IngestState.CHUNKED
            manifest.chunk_count = sum(1 for c in chunks if not c.is_parent)
            manifest.parent_chunk_count = sum(1 for c in chunks if c.is_parent)
            self.manifests.put(manifest)

            points = self._embed(metadata, chunks, key, manifest, existing, save_stats)
            manifest.status = IngestState.EMBEDDED
            self.manifests.put(manifest)

            # Note: _collection_present is deliberately NOT set here. It
            # records whether the collection existed when this pipeline
            # started; creating it ourselves mid-run must not turn the
            # remaining documents' stale INDEXED manifests back into valid
            # skips against a collection that does not hold their points.
            self.index.ensure_collection()
            self.index.upsert(points)

            # Anything the previous version produced that this one does not is
            # now orphaned. Removing it here is what makes "updates replace old
            # chunks" true rather than aspirational.
            new_ids = {p["id"] for p in points}
            if existing is not None:
                stale = [pid for pid in existing.point_ids if pid not in new_ids]
                self.index.delete_points(stale)

            manifest.point_ids = sorted(new_ids)
            manifest.status = IngestState.INDEXED
            manifest.indexed_at = utcnow()
            manifest.error = None
            self.manifests.put(manifest)

            log.info(
                "indexed",
                source_id=metadata.source_id,
                chunks=manifest.chunk_count,
                parents=manifest.parent_chunk_count,
                warnings=len(manifest.warnings),
            )
            return IngestResult(
                metadata.source_id,
                key,
                IngestState.INDEXED,
                chunk_count=manifest.chunk_count,
                parent_count=manifest.parent_chunk_count,
                warnings=manifest.warnings,
            )

        except (MetadataError, UnsupportedSource) as exc:
            log.warning("rejected", key=key, error=str(exc))
            return IngestResult(
                manifest.source_id if manifest else None,
                key,
                IngestState.REJECTED,
                reason=str(exc),
            )
        except Exception as exc:  # noqa: BLE001 - the worker must not die on one document
            log.error("ingest_failed", key=key, error=str(exc))
            if manifest is not None:
                manifest.status = IngestState.FAILED
                manifest.error = f"{type(exc).__name__}: {exc}"
                self.manifests.put(manifest)
            return IngestResult(
                manifest.source_id if manifest else None,
                key,
                IngestState.FAILED,
                reason=f"{type(exc).__name__}: {exc}",
            )

    def delete_source(self, source_id: str) -> IngestResult:
        """Remove a source from the index and tombstone its manifest."""
        self.index.delete_source(source_id)
        previous = self.manifests.get(source_id)
        if previous is not None and previous.sparse_terms:
            self.sparse.stats.forget(previous.sparse_terms, previous.sparse_mean_length)
            self.sparse.stats.save(self.store)
        manifest = self.manifests.mark_deleted(source_id)
        log.info("deleted", source_id=source_id, had_manifest=manifest is not None)
        return IngestResult(source_id, manifest.s3_key if manifest else "", IngestState.DELETED)

    def source_id_for_key(self, key: str) -> str | None:
        """Resolve a key to its source id via the sidecar, then the manifests.

        A delete event arrives after the object is gone, so the sidecar may
        already be unreadable; the manifest is the fallback record of what that
        key was.
        """
        try:
            metadata, _ = load_metadata(self.store, key)
            return metadata.source_id
        except MetadataError:
            pass
        for manifest in self.manifests.list():
            if manifest.s3_key == key:
                return manifest.source_id
        return None

    # -- stages ------------------------------------------------------------

    def _collection_exists(self) -> bool:
        """Did the collection exist when this pipeline started?

        Cached: one round trip per pipeline rather than per document. The
        answer is about the *initial* state on purpose -- see the note at the
        upsert call.
        """
        if self._collection_present is None:
            try:
                self._collection_present = bool(self.index.exists())
            except Exception:  # noqa: BLE001 - an unreachable index is not a skip
                self._collection_present = False
        return self._collection_present

    def _write_normalized(self, source_id: str, document) -> None:
        safe = source_id.replace(":", "__").replace("/", "__")
        self.store.put(
            f"{NORMALIZED_MARKDOWN_PREFIX}{safe}.md",
            document.markdown.encode("utf-8"),
            content_type="text/markdown",
        )
        if document.structured is not None:
            import json

            self.store.put(
                f"{NORMALIZED_DOCLING_PREFIX}{safe}.json",
                json.dumps(document.structured, default=str).encode("utf-8"),
                content_type="application/json",
            )

    def _embed(
        self,
        metadata: SourceMetadata,
        chunks: list[Chunk],
        key: str,
        manifest: Manifest,
        existing: Manifest | None,
        save_stats: bool,
    ) -> list[dict[str, Any]]:
        # Vectors are built over the chunk text *plus* its document identity;
        # payloads keep the chunk text alone. Without this, a chunk has no
        # lexical trace of the document it belongs to -- identifiers live in
        # YAML frontmatter, which the parser strips as non-prose -- and the
        # query "KN-LIT-001" cannot retrieve KN-LIT-001. Measured on the
        # evaluation set: exact-identifier recall@5 0.44 -> 1.00.
        texts = [_embedding_text(metadata, chunk) for chunk in chunks]

        # Retract the previous version's contribution before adding this one,
        # so re-ingesting a document does not inflate its own terms' document
        # frequency and depress their IDF.
        if existing is not None and existing.sparse_terms:
            self.sparse.stats.forget(existing.sparse_terms, existing.sparse_mean_length)

        # Statistics are updated before embedding so the document's own terms
        # are reflected in the length normalisation applied to it.
        terms, mean_length = self.sparse.stats.observe(
            _embedding_text(metadata, c) for c in chunks if not c.is_parent
        )
        manifest.sparse_terms = terms
        manifest.sparse_mean_length = mean_length
        if save_stats:
            self.sparse.stats.save(self.store)

        dense_vectors = self.dense.embed_documents(texts)
        sparse_vectors = self.sparse.embed_documents(texts)
        source_uri = self.store.uri(key)
        indexed_at = utcnow()
        base_payload = metadata.payload_fields()
        base_payload["identity_tokens"] = _identity_tokens(metadata)

        points: list[dict[str, Any]] = []
        for chunk, dense_vector, sparse_vector in zip(chunks, dense_vectors, sparse_vectors):
            payload = dict(base_payload)
            payload.update(
                {
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "parent_id": chunk.parent_id,
                    "is_parent": chunk.is_parent,
                    "text": chunk.text,
                    "section_path": chunk.section_path,
                    "section_headings": chunk.section_headings,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                    "token_count": chunk.token_count,
                    "atomic_blocks": chunk.atomic_blocks,
                    "content_hash": chunk.content_hash,
                    "source_uri": source_uri,
                    "indexed_at": indexed_at,
                }
            )
            points.append(
                {
                    "id": point_id(metadata.source_id, chunk.chunk_index, chunk.content_hash),
                    "dense": dense_vector,
                    "sparse": sparse_vector,
                    "payload": payload,
                }
            )
        return points


def _identity_tokens(metadata: SourceMetadata) -> list[str]:
    """Every handle this document answers to, lowercased.

    Both the namespaced form (``open-problem:KN-OPEN-001``) and the bare one
    (``kn-open-001``), because agents cite both.
    """
    tokens = {metadata.source_id.lower()}
    _, _, bare = metadata.source_id.partition(":")
    if bare:
        tokens.add(bare.lower())
    if metadata.experiment_id:
        tokens.add(metadata.experiment_id.lower())
    tokens.update(run.lower() for run in metadata.run_ids)
    return sorted(tokens)


def _embedding_text(metadata: SourceMetadata, chunk: Chunk) -> str:
    """The text a chunk is embedded from: its own text, prefixed with identity.

    The prefix carries the source id, the title, the experiment id, and the
    section path -- the handles a reader would cite the passage by, and the
    ones an agent queries with. It is not stored in the payload, so results
    still show the passage as written.
    """
    header_parts = [metadata.source_id, metadata.title]
    if metadata.experiment_id:
        header_parts.append(metadata.experiment_id)
    header_parts.extend(metadata.run_ids)
    if chunk.section_path:
        header_parts.append(" > ".join(chunk.section_path))
    return " | ".join(part for part in header_parts if part) + "\n\n" + chunk.text


def build_pipeline(settings=None) -> IngestionPipeline:
    """Wire a pipeline from configuration."""
    from crypto_kb.config import get_settings
    from crypto_kb.embeddings.dense import build_dense_embedder
    from crypto_kb.embeddings.sparse import build_sparse_embedder
    from crypto_kb.index import build_index
    from crypto_kb.storage import build_store

    settings = settings or get_settings()
    store = build_store(settings)
    dense = build_dense_embedder(settings)
    sparse = build_sparse_embedder(store, settings)
    index = build_index(settings, dimension=dense.dimension)
    return IngestionPipeline(
        store=store, index=index, dense_embedder=dense, sparse_embedder=sparse, settings=settings
    )
