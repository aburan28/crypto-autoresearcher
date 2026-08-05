"""BM25 sparse retrieval.

Sparse is not a nicety here. Half the queries this index has to answer are
exact lookups -- ``EXP-GGM-001``, ``P-256``, ``ePrint 2026/1486``,
``Theorem 4.3`` -- and a dense encoder has no reason to place two adjacent
experiment IDs far apart in vector space. Lexical matching is what makes those
queries reliable; the dense side is what makes paraphrases work.

BM25 factorises usefully for an incremental index: the document-side weight
depends only on term frequency and document length, and the IDF lives entirely
on the query side. So document vectors are written once and stay valid as the
corpus grows, and every query uses the current statistics.

``avgdl`` is the exception -- it appears in the document-side length
normalisation and drifts as documents arrive. The drift is small and bounded
(it rescales weights, it does not reorder terms within a document), and
``crypto-kb reindex`` recomputes from scratch when it matters.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Iterable

from crypto_kb.embeddings.base import SparseVector
from crypto_kb.text import search_terms, weighted_terms

MODEL_ID = "bm25-v1"
#: Deliberately outside the manifest prefix: the manifest store lists every
#: object under its own prefix and parses each as a Manifest.
STATS_KEY = "knowledge/stats/sparse-bm25-v1.json"

K1 = 1.2
B = 0.75
#: 32-bit term buckets. Qdrant sparse indices are unsigned ints; collisions at
#: this width are rare enough not to affect ranking on a corpus of this size.
_INDEX_MASK = 0xFFFFFFFF


def term_index(term: str) -> int:
    digest = hashlib.blake2b(term.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(digest, "big") & _INDEX_MASK


@dataclass
class SparseStats:
    """Corpus statistics backing IDF.

    Only corpus-wide aggregates live here. The per-source term sets needed to
    *retract* a document's contribution are stored on that document's manifest
    instead: keeping them in this file made it grow with the corpus while
    being rewritten once per document, which is quadratic write volume over a
    backfill. The manifest is written once per document anyway.
    """

    doc_count: int = 0
    total_length: int = 0
    document_frequency: dict[str, int] = field(default_factory=dict)
    #: Set when the in-memory table has changes not yet written out.
    dirty: bool = False

    @property
    def average_length(self) -> float:
        if self.doc_count == 0:
            return 1.0
        return max(self.total_length / self.doc_count, 1.0)

    def observe(self, texts: Iterable[str]) -> tuple[list[str], int]:
        """Add one source's contribution. Returns (terms, mean chunk length).

        Document frequency is counted per *source*, not per chunk: a term
        appearing in forty chunks of one paper is one document's worth of
        evidence that it is common, not forty. ``total_length`` tracks the mean
        chunk length, because that is the scale the document-side length
        normalisation is applied at.

        The caller records the returned terms on the manifest and passes them
        back to ``forget`` when the document is replaced or deleted.
        """
        terms: set[str] = set()
        length = 0
        count = 0
        for text in texts:
            tokens = search_terms(text)
            terms.update(tokens)
            length += len(tokens)
            count += 1
        for term in terms:
            self.document_frequency[term] = self.document_frequency.get(term, 0) + 1
        mean_length = length // max(count, 1)
        self.doc_count += 1
        self.total_length += mean_length
        self.dirty = True
        return sorted(terms), mean_length

    def forget(self, terms: Iterable[str], mean_length: int) -> None:
        """Retract a previously observed source's contribution."""
        retracted = False
        for term in terms:
            remaining = self.document_frequency.get(term, 0) - 1
            if remaining <= 0:
                self.document_frequency.pop(term, None)
            else:
                self.document_frequency[term] = remaining
            retracted = True
        if not retracted:
            return
        self.doc_count = max(self.doc_count - 1, 0)
        self.total_length = max(self.total_length - mean_length, 0)
        self.dirty = True

    def idf(self, term: str) -> float:
        """Robertson/Sparck-Jones IDF, floored so a ubiquitous term is not negative."""
        df = self.document_frequency.get(term, 0)
        value = math.log(1.0 + (self.doc_count - df + 0.5) / (df + 0.5))
        return max(value, 0.01)

    # -- persistence -------------------------------------------------------

    def to_json(self) -> str:
        return json.dumps(
            {
                "model_id": MODEL_ID,
                "doc_count": self.doc_count,
                "total_length": self.total_length,
                "document_frequency": self.document_frequency,
            },
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, raw: str) -> "SparseStats":
        data = json.loads(raw)
        return cls(
            doc_count=data.get("doc_count", 0),
            total_length=data.get("total_length", 0),
            document_frequency=data.get("document_frequency", {}),
        )

    @classmethod
    def load(cls, store) -> "SparseStats":
        if not store.exists(STATS_KEY):
            return cls()
        return cls.from_json(store.get(STATS_KEY).decode("utf-8"))

    def save(self, store, force: bool = False) -> None:
        """Write the table out. A no-op when nothing changed since the last write."""
        if not (self.dirty or force):
            return
        store.put(STATS_KEY, self.to_json().encode("utf-8"), content_type="application/json")
        self.dirty = False


class Bm25SparseEmbedder:
    def __init__(self, stats: SparseStats | None = None, model_id: str = MODEL_ID) -> None:
        self.stats = stats or SparseStats()
        self._model_id = model_id

    @property
    def model_id(self) -> str:
        return self._model_id

    def embed_documents(self, texts: list[str]) -> list[SparseVector]:
        avgdl = self.stats.average_length
        return [self._embed_document(text, avgdl) for text in texts]

    def embed_query(self, text: str) -> SparseVector:
        seen: dict[int, float] = {}
        for term, weight in weighted_terms(text).items():
            scaled = 1.0 + math.log(weight) if weight > 1.0 else weight
            index = term_index(term)
            seen[index] = seen.get(index, 0.0) + self.stats.idf(term) * scaled
        return SparseVector(
            indices=list(seen.keys()), values=[round(v, 6) for v in seen.values()]
        )

    def _embed_document(self, text: str, avgdl: float) -> SparseVector:
        weights = weighted_terms(text)
        if not weights:
            return SparseVector(indices=[], values=[])
        length = sum(weights.values())
        norm = K1 * (1.0 - B + B * length / avgdl)
        seen: dict[int, float] = {}
        for term, tf in weights.items():
            weight = tf * (K1 + 1.0) / (tf + norm)
            index = term_index(term)
            seen[index] = seen.get(index, 0.0) + weight
        return SparseVector(
            indices=list(seen.keys()), values=[round(v, 6) for v in seen.values()]
        )


def build_sparse_embedder(store=None, settings=None) -> Bm25SparseEmbedder:
    """Load persisted statistics, if a store is available."""
    from crypto_kb.config import get_settings

    settings = settings or get_settings()
    stats = SparseStats.load(store) if store is not None else SparseStats()
    return Bm25SparseEmbedder(stats=stats, model_id=settings.sparse_model_name)
