"""Retrieval behaviour against the real evaluation corpus."""

from __future__ import annotations

import pytest

from crypto_kb.models import Authority, ClaimStatus, SearchFilters, SourceType


@pytest.fixture(scope="module")
def retriever(eval_environment):
    return eval_environment["retriever"]


def sources(response):
    return [r.source_id for r in response.results]


# -- basics ----------------------------------------------------------------


def test_search_returns_bounded_results(retriever):
    response = retriever.search("index calculus for elliptic curves", top_k=6)
    assert 0 < len(response.results) <= 6
    assert response.latency_ms is not None
    assert response.query_id


def test_top_k_is_clamped_and_reported(retriever):
    response = retriever.search("elliptic curves", top_k=100)
    assert len(response.results) <= retriever.settings.max_top_k
    assert any("clamped" in note for note in response.notes)


def test_parents_are_never_returned_as_results(retriever):
    response = retriever.search("Semaev summation polynomials", top_k=10)
    for result in response.results:
        record = retriever.index.by_chunk_id(result.chunk_id)
        assert record["payload"]["is_parent"] is False


def test_every_result_carries_its_provenance(retriever):
    response = retriever.search("Groebner basis complexity", top_k=8)
    assert response.results
    for result in response.results:
        assert result.source_id and result.source_uri and result.content_hash
        assert result.source_type


# -- exact identifiers -----------------------------------------------------


@pytest.mark.parametrize(
    "query,expected",
    [
        ("KN-LIT-001", "paper:KN-LIT-001"),
        ("KN-OPEN-001", "open-problem:KN-OPEN-001"),
        ("KN-TECH-056", "technique:KN-TECH-056"),
        ("What does KN-FIND-002 conclude?", "finding:KN-FIND-002"),
    ],
)
def test_exact_identifier_lookup(retriever, query, expected):
    response = retriever.search(query, top_k=8)
    assert expected in sources(response), f"{query!r} did not surface {expected}"
    assert any("exact identifier match" in note for note in response.notes)


def test_exact_match_is_ranked_first(retriever):
    response = retriever.search("KN-OPEN-001", top_k=8)
    assert response.results[0].source_id == "open-problem:KN-OPEN-001"


def test_a_query_without_identifiers_has_no_exact_note(retriever):
    response = retriever.search("how are relations generated", top_k=5)
    assert not any("exact identifier" in note for note in response.notes)


# -- filters ---------------------------------------------------------------


def test_source_type_filter_does_not_leak(retriever):
    response = retriever.search(
        "index calculus", top_k=10, filters=SearchFilters(source_type=[SourceType.PAPER])
    )
    assert response.results
    assert {r.source_type for r in response.results} == {"paper"}


def test_multiple_source_types_are_allowed(retriever):
    response = retriever.search(
        "Groebner basis",
        top_k=10,
        filters=SearchFilters(source_type=[SourceType.PAPER, SourceType.INTERNAL_NOTE]),
    )
    assert response.results
    assert {r.source_type for r in response.results} <= {"paper", "internal-note"}


def test_superseded_is_excluded_by_default(retriever):
    response = retriever.search("elliptic curve discrete logarithm", top_k=10)
    assert all(result.superseded is False for result in response.results)


def test_claim_status_filter_is_respected(retriever):
    response = retriever.search(
        "evidence",
        top_k=10,
        filters=SearchFilters(claim_status=[ClaimStatus.EXTERNAL_SOURCE]),
    )
    assert all(r.claim_status == "external-source" for r in response.results)


def test_min_authority_excludes_weaker_provenance(retriever):
    response = retriever.search(
        "elliptic curve discrete logarithm",
        top_k=10,
        filters=SearchFilters(min_authority=Authority.PEER_REVIEWED),
    )
    from crypto_kb.models import authority_rank

    ceiling = authority_rank(Authority.PEER_REVIEWED)
    assert all(authority_rank(r.authority) <= ceiling for r in response.results)


def test_source_id_filter_pins_one_document(retriever):
    response = retriever.search(
        "index calculus", top_k=10, filters=SearchFilters(source_id=["paper:KN-LIT-002"])
    )
    assert set(sources(response)) == {"paper:KN-LIT-002"}


def test_filters_are_reported_back(retriever):
    response = retriever.search(
        "curves", top_k=5, filters=SearchFilters(source_type=[SourceType.PAPER])
    )
    assert response.filters_applied.get("source_type") == ["paper"]


# -- diversification -------------------------------------------------------


def test_no_single_source_monopolises_results(retriever):
    response = retriever.search("summation polynomial decomposition", top_k=8)
    counts: dict[str, int] = {}
    for result in response.results:
        counts[result.source_id] = counts.get(result.source_id, 0) + 1
    assert max(counts.values()) <= retriever.settings.max_chunks_per_source


def test_suppression_is_reported_not_silent(retriever):
    response = retriever.search("index calculus", top_k=8)
    suppressed_notes = [n for n in response.notes if "suppressed" in n]
    # Either nothing was suppressed, or the caller was told about it.
    assert suppressed_notes or len(set(sources(response))) == len(response.results)


def test_results_are_deduplicated_by_content(retriever):
    response = retriever.search("relation generation", top_k=10)
    hashes = [r.content_hash for r in response.results]
    assert len(hashes) == len(set(hashes))


# -- context ---------------------------------------------------------------


def test_get_context_returns_neighbours_and_parent(retriever):
    response = retriever.search("Semaev summation polynomials", top_k=3)
    chunk_id = response.results[0].chunk_id

    context = retriever.get_context(chunk_id, before=2, after=2)

    assert context.chunk is not None and context.chunk.chunk_id == chunk_id
    assert context.source_id == response.results[0].source_id
    assert len(context.before) <= 2 and len(context.after) <= 2
    if context.parent_text:
        assert len(context.parent_text) >= len(context.chunk.text)


def test_get_context_is_capped(retriever):
    response = retriever.search("index calculus", top_k=3)
    context = retriever.get_context(response.results[0].chunk_id, before=50, after=50)
    assert len(context.before) <= 3 and len(context.after) <= 3


def test_get_context_of_unknown_chunk_says_so(retriever):
    context = retriever.get_context("sha256:does-not-exist")
    assert context.chunk is None
    assert "not found" in context.notes[0]


# -- source ----------------------------------------------------------------


def test_get_source_is_bounded_and_descriptive(retriever):
    document = retriever.get_source("paper:KN-LIT-001")
    assert document is not None
    assert document.title
    assert document.chunk_count > 0
    assert document.source_uri
    assert document.summary and len(document.summary) <= 1210


def test_get_source_does_not_return_the_document(retriever):
    document = retriever.get_source("technique:KN-TECH-056")
    full_text = "".join(
        record["payload"]["text"]
        for record in retriever.index.by_source("technique:KN-TECH-056", include_parents=False)
    )
    assert len(document.summary) < len(full_text)


def test_get_source_lists_sections(retriever):
    document = retriever.get_source("technique:KN-TECH-056")
    assert document.table_of_contents


def test_get_source_of_unknown_id_is_none(retriever):
    assert retriever.get_source("paper:absent") is None


# -- related ---------------------------------------------------------------


def test_find_related_excludes_the_source_itself(retriever):
    response = retriever.find_related("paper:KN-LIT-001", top_k=5)
    assert "paper:KN-LIT-001" not in sources(response)
    assert response.results


def test_find_related_returns_one_passage_per_source(retriever):
    response = retriever.find_related("paper:KN-LIT-002", top_k=5)
    assert len(set(sources(response))) == len(response.results)


def test_find_related_on_unknown_source_says_so(retriever):
    response = retriever.find_related("paper:absent")
    assert response.results == []
    assert "not found" in response.notes[0]


# -- baselines -------------------------------------------------------------


def test_single_mode_searches_work(retriever):
    for mode in ("dense", "sparse"):
        response = retriever.search("Semaev polynomials", top_k=5, mode=mode)
        assert response.results, f"{mode} returned nothing"
