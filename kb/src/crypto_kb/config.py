"""Settings, from environment or `.env`, with a runnable local default.

The defaults describe the local vertical slice (Milestone 1): a filesystem
object store rooted at the repository, an in-memory Qdrant, and the pinned
dependency-free dense embedder. Nothing here reaches the network until it is
pointed at a real bucket or a real Qdrant.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

#: Prefixes inside the corpus root. Ingestion reads only from ``source/``;
#: ``normalized/`` and ``manifests/`` are written by the pipeline and must be
#: ignored as inputs or ingestion loops on its own output.
SOURCE_PREFIX = "knowledge/source/"
NORMALIZED_MARKDOWN_PREFIX = "knowledge/normalized/markdown/"
NORMALIZED_DOCLING_PREFIX = "knowledge/normalized/docling-json/"
MANIFEST_PREFIX = "knowledge/manifests/"
REJECTED_PREFIX = "knowledge/rejected/"
STATS_PREFIX = "knowledge/stats/"

IGNORED_INPUT_PREFIXES = (
    NORMALIZED_MARKDOWN_PREFIX,
    NORMALIZED_DOCLING_PREFIX,
    MANIFEST_PREFIX,
    REJECTED_PREFIX,
    STATS_PREFIX,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CRYPTO_KB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # -- object store ------------------------------------------------------
    #: "local" or "s3".
    store_backend: str = "local"
    #: Filesystem root for the local backend. Keys are relative to it.
    local_root: Path = Field(default=Path("./.kb-corpus"))
    s3_bucket: str = "crypto-autoresearcher"
    aws_region: str | None = None
    aws_profile: str | None = None
    s3_endpoint_url: str | None = None

    # -- index -------------------------------------------------------------
    #: Three forms:
    #:   ":memory:"                embedded, in-process, gone on exit
    #:   "./path" or "file://…"    embedded, file-backed, single writer
    #:   "http://host:6333"        a server
    #: The embedded forms have no payload indexes (they filter by scan), which
    #: is fine at corpus scale here and not fine in production.
    qdrant_url: str = ":memory:"
    qdrant_api_key: str | None = None
    #: Bump the suffix whenever vector semantics change. Collections are never
    #: mutated in place (plan Phase 7).
    collection: str = "crypto_knowledge_v1"
    qdrant_timeout: float = 30.0

    # -- embedding ---------------------------------------------------------
    #: "hashing" (pinned, no external model) or "sentence-transformers".
    dense_backend: str = "hashing"
    dense_model_name: str = "hashing-ngram-v1"
    dense_dimension: int = 512
    sparse_model_name: str = "bm25-v1"

    # -- chunking ----------------------------------------------------------
    chunk_target_tokens: int = 640
    chunk_max_tokens: int = 1200
    chunk_min_tokens: int = 120
    chunk_overlap_tokens: int = 100
    parent_target_tokens: int = 3000
    parent_max_tokens: int = 4000

    # -- retrieval ---------------------------------------------------------
    default_top_k: int = 6
    max_top_k: int = 10
    candidate_multiplier: int = 4
    min_candidates: int = 20
    max_chunks_per_source: int = 2
    max_chunks_per_parent: int = 3
    rerank_backend: str = "none"
    rerank_model_name: str | None = None
    #: Hard cap on characters returned per passage, so one pathological chunk
    #: cannot blow an agent's context window.
    max_chars_per_result: int = 4000

    # -- ingestion ---------------------------------------------------------
    sqs_queue_url: str | None = None
    sqs_visibility_timeout: int = 900
    sqs_max_messages: int = 5
    sqs_wait_seconds: int = 20
    max_receive_count: int = 5

    # -- observability -----------------------------------------------------
    query_log_path: Path | None = None
    log_level: str = "info"
    metrics_port: int | None = None

    def source_prefix(self) -> str:
        return SOURCE_PREFIX

    def embedding_model_version(self) -> str:
        """The embedding half of the document fingerprint."""
        return f"{self.dense_model_name}:{self.dense_dimension}+{self.sparse_model_name}"


_settings: Settings | None = None


def get_settings(**overrides) -> Settings:
    """Process-wide settings. ``overrides`` bypass the cache (used by tests)."""
    global _settings
    if overrides:
        return Settings(**overrides)
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    global _settings
    _settings = None
