"""Vector index: collection schema and the Qdrant client wrapper."""

from crypto_kb.index.schema import DENSE_VECTOR, PAYLOAD_INDEXES, SPARSE_VECTOR

__all__ = ["DENSE_VECTOR", "SPARSE_VECTOR", "PAYLOAD_INDEXES", "build_index"]


def build_index(settings=None, dimension: int | None = None):
    from crypto_kb.config import get_settings
    from crypto_kb.index.qdrant import QdrantIndex

    settings = settings or get_settings()
    return QdrantIndex(settings=settings, dimension=dimension)
