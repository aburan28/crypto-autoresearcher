"""Embedders: determinism, identifier handling, and BM25 bookkeeping."""

from __future__ import annotations

import math

from crypto_kb.embeddings.dense import HashingDenseEmbedder
from crypto_kb.embeddings.sparse import Bm25SparseEmbedder, SparseStats, term_index
from crypto_kb.text import count_tokens, identifiers, search_terms, weighted_terms


def cosine(left, right):
    return sum(a * b for a, b in zip(left, right))


def test_dense_embedding_is_deterministic():
    embedder = HashingDenseEmbedder(dimension=256)
    assert embedder.embed_query("Semaev polynomials") == embedder.embed_query("Semaev polynomials")


def test_dense_embedding_is_normalised():
    vector = HashingDenseEmbedder(dimension=256).embed_query("index calculus over prime fields")
    assert math.isclose(math.sqrt(sum(v * v for v in vector)), 1.0, rel_tol=1e-9)


def test_dense_similarity_tracks_topic():
    embedder = HashingDenseEmbedder(dimension=512)
    query = embedder.embed_query("summation polynomials for elliptic curve index calculus")
    related = embedder.embed_query("index calculus with Semaev summation polynomials on curves")
    unrelated = embedder.embed_query("lattice basis reduction and shortest vector problems")
    assert cosine(query, related) > cosine(query, unrelated)


def test_dense_dimension_is_respected():
    assert len(HashingDenseEmbedder(dimension=64).embed_query("x")) == 64


def test_model_id_includes_the_dimension():
    assert HashingDenseEmbedder(dimension=64).model_id.endswith(":64")


def test_identifiers_are_kept_whole():
    terms = search_terms("EXP-GGM-001 on P-256 over F_{p^n}, see Theorem 4.3 and ePrint 2026/1486")
    for whole in ("exp-ggm-001", "p-256", "f_{p^n}", "4.3", "2026/1486"):
        assert whole in terms, f"{whole} was not kept as a whole term"


def test_identifier_parts_are_also_emitted():
    terms = search_terms("EXP-GGM-001")
    assert {"exp", "ggm", "001"} <= set(terms)


def test_identifier_parts_carry_less_weight_than_the_whole():
    weights = weighted_terms("KN-OPEN-001")
    assert weights["kn-open-001"] == 1.0
    assert weights["open"] < weights["kn-open-001"]


def test_identifiers_helper_returns_only_whole_forms():
    assert "kn-open-001" in identifiers("What does KN-OPEN-001 say?")
    assert "open" not in identifiers("What does KN-OPEN-001 say?")


def test_stopwords_are_dropped():
    assert "the" not in search_terms("the curve and the field")


def test_sparse_document_and_query_vectors_share_term_indices():
    stats = SparseStats()
    embedder = Bm25SparseEmbedder(stats)
    stats.observe(["Semaev summation polynomial relation generation"])
    document = embedder.embed_documents(["Semaev summation polynomial relation generation"])[0]
    query = embedder.embed_query("Semaev polynomial")
    assert set(query.indices) & set(document.indices)
    assert term_index("semaev") in query.indices


def test_idf_prefers_rare_terms():
    stats = SparseStats()
    for _ in range(20):
        stats.observe(["common term appears everywhere"])
    stats.observe(["rare unusual token"])
    assert stats.idf("rare") > stats.idf("common")


def test_forget_retracts_exactly_what_observe_added():
    stats = SparseStats()
    baseline_terms, baseline_length = stats.observe(["first document about curves"])
    before = (stats.doc_count, stats.total_length, dict(stats.document_frequency))

    terms, length = stats.observe(["second document about lattices"])
    stats.forget(terms, length)

    assert (stats.doc_count, stats.total_length, stats.document_frequency) == before
    assert baseline_terms and baseline_length > 0


def test_stats_round_trip_through_json():
    stats = SparseStats()
    stats.observe(["a document about elliptic curves"])
    restored = SparseStats.from_json(stats.to_json())
    assert restored.doc_count == stats.doc_count
    assert restored.document_frequency == stats.document_frequency


def test_stats_save_is_a_noop_when_clean(store):
    stats = SparseStats()
    stats.observe(["text"])
    stats.save(store)
    assert stats.dirty is False
    # A second save writes nothing new; the object still exists from the first.
    stats.save(store)
    from crypto_kb.embeddings.sparse import STATS_KEY

    assert store.exists(STATS_KEY)


def test_empty_text_yields_an_empty_sparse_vector():
    vector = Bm25SparseEmbedder(SparseStats()).embed_documents(["   "])[0]
    assert len(vector) == 0


def test_token_count_is_monotone_in_length():
    short = count_tokens("a short sentence")
    long = count_tokens("a short sentence with several more words appended to the end of it")
    assert long > short
