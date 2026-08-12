"""Deterministic identity for every artifact in the pipeline.

Three distinct notions, deliberately not collapsed into one:

* ``content_hash`` -- what the bytes are. Changes when the source changes.
* ``document_fingerprint`` -- what the *derived index* would be. Changes when
  the source, its metadata, or any pipeline stage version changes. This is the
  skip key: equal fingerprint means re-ingesting cannot produce a different
  index, so the work is skipped.
* ``point_id`` -- the Qdrant primary key. A UUIDv5 over (source, index,
  chunk content), so re-ingesting the same document upserts over the same
  rows instead of duplicating them.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

# Fixed namespace for point IDs. Never change it: doing so orphans every point
# already in a collection. A new embedding model gets a new collection instead
# (see index/schema.py).
POINT_NAMESPACE = uuid.UUID("6f4c2b1e-1f8a-5d3c-9a72-0e5b7a1d4c88")

_PREFIX = "sha256:"


def sha256_bytes(data: bytes) -> str:
    """Prefixed hex digest of raw bytes."""
    return _PREFIX + hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    """Prefixed hex digest of text, hashed as UTF-8."""
    return sha256_bytes(text.encode("utf-8"))


def canonical_json(value: Any) -> str:
    """Stable JSON encoding: sorted keys, no insignificant whitespace.

    Metadata dictionaries reach us from JSON sidecars, YAML frontmatter, and
    Python literals. Hashing their repr would make the fingerprint depend on
    key insertion order, so everything goes through this first.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def hash_metadata(metadata: dict[str, Any]) -> str:
    """Hash of a metadata mapping, order-independent."""
    return sha256_text(canonical_json(metadata))


def document_fingerprint(
    *,
    source_content_hash: str,
    metadata_hash: str,
    parser_version: str,
    chunker_version: str,
    embedding_model_version: str,
) -> str:
    """Fingerprint covering the source and every stage that derives from it.

    Equality means: re-running the pipeline on this document would write the
    same points, so it can be skipped. Any stage version bump breaks equality
    for every document, which is what forces a rebuild.
    """
    joined = "\n".join(
        [
            source_content_hash,
            metadata_hash,
            parser_version,
            chunker_version,
            embedding_model_version,
        ]
    )
    return sha256_text(joined)


def chunk_id(source_id: str, chunk_index: int, chunk_text: str) -> str:
    """Stable identifier for a chunk, used as the agent-facing handle."""
    return sha256_text(f"{source_id}\x1f{chunk_index}\x1f{chunk_text}")


def point_id(source_id: str, chunk_index: int, chunk_content_hash: str) -> str:
    """Deterministic Qdrant point ID.

    Qdrant accepts unsigned integers or UUIDs, not arbitrary strings, so the
    chunk identity is folded into a UUIDv5 rather than passed through.
    """
    name = f"{source_id}\x1f{chunk_index}\x1f{chunk_content_hash}"
    return str(uuid.uuid5(POINT_NAMESPACE, name))


def short(hash_value: str, length: int = 12) -> str:
    """Human-readable abbreviation of a prefixed hash, for logs and reports."""
    body = hash_value[len(_PREFIX) :] if hash_value.startswith(_PREFIX) else hash_value
    return body[:length]
