"""Embedding protocols."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class SparseVector:
    """Qdrant sparse vector: parallel index/value arrays."""

    indices: list[int]
    values: list[float]

    def __len__(self) -> int:
        return len(self.indices)

    def as_dict(self) -> dict[str, list]:
        return {"indices": self.indices, "values": self.values}


@runtime_checkable
class DenseEmbedder(Protocol):
    @property
    def dimension(self) -> int: ...

    @property
    def model_id(self) -> str: ...

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


@runtime_checkable
class SparseEmbedder(Protocol):
    @property
    def model_id(self) -> str: ...

    def embed_documents(self, texts: list[str]) -> list[SparseVector]: ...

    def embed_query(self, text: str) -> SparseVector: ...
