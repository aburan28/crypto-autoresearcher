"""Dense embedders.

The default is a hashed-feature model with no external weights. That is a
deliberate starting point, not a placeholder for something better later:

* it is pinned by construction -- the same text produces the same vector on
  any machine, this year or in three years, which is what a reproducible run
  record needs from an index;
* it has no download, no GPU, and no model licence to track;
* it makes the *architecture* testable end to end before anyone commits to a
  particular neural model.

It is weaker than a trained sentence encoder on paraphrase queries, and the
evaluation harness is what should decide whether to pay for one. Switching is
a two-line config change plus a new collection; see
``SentenceTransformerEmbedder``.
"""

from __future__ import annotations

import hashlib
import math
from typing import Any

from crypto_kb.text import char_ngrams, search_terms, weighted_terms

MODEL_ID = "hashing-ngram-v1"


class HashingDenseEmbedder:
    """Deterministic hashed bag of words, word bigrams, and character 4-grams.

    Signed hashing (the sign bit of the digest decides the sign of the
    contribution) keeps collisions from systematically inflating similarity,
    which is the standard failure of naive feature hashing.
    """

    def __init__(self, dimension: int = 512, model_id: str = MODEL_ID) -> None:
        if dimension < 32:
            raise ValueError("dense dimension must be at least 32")
        self._dimension = dimension
        self._model_id = model_id

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_id(self) -> str:
        return f"{self._model_id}:{self._dimension}"

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    # -- internals ---------------------------------------------------------

    def _features(self, text: str) -> dict[str, float]:
        features: dict[str, float] = {
            f"w:{term}": weight for term, weight in weighted_terms(text).items()
        }
        terms = search_terms(text)
        for left, right in zip(terms, terms[1:]):
            key = f"b:{left}_{right}"
            features[key] = features.get(key, 0.0) + 0.5
        # Character n-grams are capped: on a 4,000-token chunk they would
        # otherwise dominate the vector and wash out the word signal.
        grams = char_ngrams(text, 4)
        weight = min(1.0, 400.0 / max(len(grams), 1)) * 0.35
        for gram in grams:
            key = f"c:{gram}"
            features[key] = features.get(key, 0.0) + weight
        return features

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self._dimension
        for feature, weight in self._features(text).items():
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            value = int.from_bytes(digest, "big")
            bucket = value % self._dimension
            sign = 1.0 if (value >> 63) & 1 else -1.0
            # Sublinear term weighting, as in tf-idf: the tenth occurrence of a
            # word says much less than the second.
            scaled = 1.0 + math.log(weight) if weight > 1.0 else weight
            vector[bucket] += sign * scaled
        norm = math.sqrt(sum(v * v for v in vector))
        if norm == 0.0:
            return vector
        return [v / norm for v in vector]


class SentenceTransformerEmbedder:
    """Adapter for a pinned sentence-transformers model.

    Requires the ``transformers`` extra. The model name is part of
    ``model_id`` and therefore part of the document fingerprint, so changing it
    invalidates the index rather than silently mixing vector spaces.
    """

    def __init__(self, model_name: str, dimension: int | None = None, model: Any | None = None) -> None:
        self._model_name = model_name
        self._model = model
        self._dimension = dimension

    @property
    def model(self) -> Any:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover - depends on install
                raise RuntimeError(
                    "sentence-transformers is required for dense_backend="
                    "'sentence-transformers'; install with `pip install "
                    "'crypto-kb[transformers]'`"
                ) from exc
            self._model = SentenceTransformer(self._model_name)
        return self._model

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._dimension = int(self.model.get_sentence_embedding_dimension())
        return self._dimension

    @property
    def model_id(self) -> str:
        return f"sentence-transformers/{self._model_name}"

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [list(map(float, v)) for v in vectors]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


def build_dense_embedder(settings=None):
    from crypto_kb.config import get_settings

    settings = settings or get_settings()
    backend = settings.dense_backend
    if backend == "hashing":
        return HashingDenseEmbedder(
            dimension=settings.dense_dimension, model_id=settings.dense_model_name
        )
    if backend == "sentence-transformers":
        return SentenceTransformerEmbedder(
            model_name=settings.dense_model_name, dimension=settings.dense_dimension
        )
    raise ValueError(
        f"unknown dense_backend {backend!r} (expected 'hashing' or 'sentence-transformers')"
    )
