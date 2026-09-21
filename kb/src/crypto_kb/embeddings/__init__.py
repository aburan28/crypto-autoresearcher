"""Embedding backends behind narrow protocols.

The pipeline never names a concrete model. Swapping the dense backend is a
config change plus a new collection -- vector semantics are never mutated in
place, because a collection holding vectors from two models silently returns
nonsense rather than failing.
"""

from crypto_kb.embeddings.base import DenseEmbedder, SparseEmbedder, SparseVector
from crypto_kb.embeddings.dense import HashingDenseEmbedder, build_dense_embedder
from crypto_kb.embeddings.sparse import Bm25SparseEmbedder, SparseStats

__all__ = [
    "DenseEmbedder",
    "SparseEmbedder",
    "SparseVector",
    "HashingDenseEmbedder",
    "build_dense_embedder",
    "Bm25SparseEmbedder",
    "SparseStats",
]
