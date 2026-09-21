"""Optional cross-encoder reranking.

Off by default. A reranker is the right way to spend latency once retrieval is
measured -- and the wrong thing to add before, because it masks a weak
candidate set instead of fixing it. The evaluation harness compares with and
without.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Reranker(Protocol):
    @property
    def model_id(self) -> str: ...

    def rerank(self, query: str, passages: list[str]) -> list[float]: ...


class NoopReranker:
    """Preserves fusion order. ``rerank`` returns descending placeholder scores."""

    model_id = "none"

    def rerank(self, query: str, passages: list[str]) -> list[float]:
        return [float(len(passages) - i) for i in range(len(passages))]


class CrossEncoderReranker:
    def __init__(self, model_name: str, model: Any | None = None) -> None:
        self._model_name = model_name
        self._model = model

    @property
    def model_id(self) -> str:
        return f"cross-encoder/{self._model_name}"

    @property
    def model(self) -> Any:
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
            except ImportError as exc:  # pragma: no cover - depends on install
                raise RuntimeError(
                    "sentence-transformers is required for rerank_backend="
                    "'cross-encoder'; install with `pip install 'crypto-kb[transformers]'`"
                ) from exc
            self._model = CrossEncoder(self._model_name)
        return self._model

    def rerank(self, query: str, passages: list[str]) -> list[float]:
        if not passages:
            return []
        scores = self.model.predict([(query, passage) for passage in passages])
        return [float(score) for score in scores]


def build_reranker(settings=None) -> Reranker:
    from crypto_kb.config import get_settings

    settings = settings or get_settings()
    if settings.rerank_backend in {"none", "", None}:
        return NoopReranker()
    if settings.rerank_backend == "cross-encoder":
        if not settings.rerank_model_name:
            raise ValueError("rerank_backend='cross-encoder' requires rerank_model_name")
        return CrossEncoderReranker(settings.rerank_model_name)
    raise ValueError(f"unknown rerank_backend {settings.rerank_backend!r}")
