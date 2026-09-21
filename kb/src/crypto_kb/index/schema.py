"""Collection schema.

One collection holds both child and parent chunks, distinguished by the
``is_parent`` payload flag. Keeping parents in the same collection means
context expansion is a filtered lookup rather than a second store to keep
consistent -- and a deletion that misses one of two stores is exactly how a
retracted result stays retrievable.

Payload indexes are declared here rather than created ad hoc, so a rebuilt
collection is identical to the one it replaced.
"""

from __future__ import annotations

DENSE_VECTOR = "dense"
SPARSE_VECTOR = "sparse"

#: field name -> Qdrant payload schema type. Every field a validated filter
#: can reference must appear here; an unindexed filter field turns a query
#: into a full scan.
PAYLOAD_INDEXES: dict[str, str] = {
    "source_id": "keyword",
    #: Lowercased handles this chunk's document answers to: its source id, the
    #: bare identifier, its experiment id, its run ids. Exact-identifier
    #: lookups filter on this instead of relying on lexical scoring, which
    #: cannot separate the document that *is* KN-OPEN-001 from the 26 that
    #: cite it.
    "identity_tokens": "keyword",
    "chunk_id": "keyword",
    "parent_id": "keyword",
    "source_type": "keyword",
    "primitive": "keyword",
    "field_type": "keyword",
    "curves": "keyword",
    "topics": "keyword",
    "claim_status": "keyword",
    "evidence_level": "keyword",
    "authority": "keyword",
    "experiment_id": "keyword",
    "run_ids": "keyword",
    "git_commit": "keyword",
    "publication_year": "integer",
    "superseded": "bool",
    "is_parent": "bool",
    "chunk_index": "integer",
}


def describe(dimension: int, distance: str = "cosine") -> dict:
    """Human-readable schema summary, used by `crypto-kb doctor`."""
    return {
        "vectors": {DENSE_VECTOR: {"size": dimension, "distance": distance}},
        "sparse_vectors": [SPARSE_VECTOR],
        "payload_indexes": dict(PAYLOAD_INDEXES),
    }
