"""Retrieval behaviour against the real evaluation corpus."""

from __future__ import annotations

from pathlib import Path

import pytest

from crypto_kb.models import Authority, ClaimStatus, SearchFilters, SourceType


REPO_ROOT = Path(__file__).resolve().parents[3]
ACTUAL_LINEAGE_PATHS = {
    "experiments/EXP-DREG-001/specification.yaml",
    "ledger/evidence/EV-GOAL-DREG-001-B003.yaml",
    "ledger/decisions/DEC-GOAL-DREG-001-B003.yaml",
    "ledger/hypotheses/H-XOR-YIELD.yaml",
    "ledger/hypotheses/H-XOR-d1a480.yaml",
}
EXPECTED_LINEAGE = {
    "experiment:EXP-DREG-001": (
        [],
        [
            "experiments/EXP-DREG-001/specification.yaml@sha256:"
            "44fe37a126e5998054cb9788e1208b13d15ee87448c78737bddd1666e2cf5c8b",
            "ledger/corrections/schema-supersessions/20260811/"
            "experiments__EXP-DREG-001__specification.v2.yaml@sha256:"
            "fa056f97306ad46e21077c46794dfab371a85f695551b13c51acaa1e6de486b2",
        ],
    ),
    "evidence:EV-DREG-7597cb": (
        ["EV-GOAL-DREG-001-B003"],
        [
            "ledger/corrections/schema-supersessions/20260811/"
            "ledger__evidence__EV-GOAL-DREG-001-B003.v2.yaml@sha256:"
            "46ab4032c6af699b993a4cffb7d314dbff8281aad4f07eeae9720c9e1c9791a6",
            "ledger/evidence/EV-GOAL-DREG-001-B003.yaml@sha256:"
            "6449908fec5b00eb2366a32d52f9a1c507b02111d5679c68f33c083736867524",
        ],
    ),
    "decision:DEC-20260811-e77b9d": (
        ["DEC-GOAL-DREG-001-B003"],
        [
            "ledger/corrections/schema-supersessions/20260811/"
            "ledger__decisions__DEC-GOAL-DREG-001-B003.v2.yaml@sha256:"
            "731520f185b37714573f9560d4d81c4a310681949b23ad53a5185b7156005120",
            "ledger/decisions/DEC-GOAL-DREG-001-B003.yaml@sha256:"
            "c7047d97f5ee7e6519e4c00d4623d101fb00b83d0094063a4b1f0c95ae22ef11",
        ],
    ),
    "hypothesis:H-XOR-d1a480": (
        ["H-XOR-YIELD"],
        [
            "ledger/corrections/schema-supersessions/20260808/"
            "ledger__hypotheses__H-XOR-d1a480.v2.yaml@sha256:"
            "b9876d58c71699b5332039d8a7dc618c007a65907649e433f03e871d2e4519a8",
            "ledger/hypotheses/H-XOR-YIELD.yaml@sha256:"
            "541bda542e20b161d3bdd606cd88c18ee65cb857f8fcd5ae6d39d459962b0ac7",
            "ledger/hypotheses/H-XOR-d1a480.yaml@sha256:"
            "655c01aa05986f760b2a348ba5e3cfdb1103cdb1af4eb27f97610db9217cd1f8",
        ],
    ),
}


@pytest.fixture(scope="module")
def retriever(eval_environment):
    return eval_environment["retriever"]


@pytest.fixture
def actual_lineage_retriever(pipeline, store):
    from crypto_kb.ingest.backfill import backfill
    from crypto_kb.ingest.repo_corpus import stage_repository
    from crypto_kb.retrieval import KnowledgeRetriever

    staged = stage_repository(REPO_ROOT, store, include=ACTUAL_LINEAGE_PATHS)
    assert {item.metadata["source_id"] for item in staged} == set(EXPECTED_LINEAGE)
    report = backfill(pipeline)
    assert not report.failed, [result.reason for result in report.failed]
    return KnowledgeRetriever(
        index=pipeline.index,
        dense_embedder=pipeline.dense,
        sparse_embedder=pipeline.sparse,
        settings=pipeline.settings,
    )


def sources(response):
    return [r.source_id for r in response.results]


class ExactLookupWindowIndex:
    """Minimal exact-filter index with references ordered before canonicals."""

    def __init__(self, records):
        self.records = records
        self.count_limits: list[int] = []

    def count(self, query_filter=None):
        del query_filter
        return len(self.records)

    def scroll(self, query_filter=None, limit=256):
        del query_filter
        self.count_limits.append(limit)
        return self.records[:limit]


def _exact_payload(source_id, chunk_index=0, **overrides):
    payload = {
        "chunk_id": f"{source_id}-{chunk_index}",
        "source_id": source_id,
        "title": source_id,
        "text": source_id,
        "section_path": [],
        "source_uri": f"memory://{source_id}",
        "source_type": source_id.split(":", 1)[0],
        "content_hash": f"hash-{source_id}-{chunk_index}",
        "chunk_index": chunk_index,
        "identity_tokens": [],
        "is_parent": False,
    }
    payload.update(overrides)
    return payload


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


def test_actual_canonical_and_legacy_ids_return_exact_lineage_everywhere(
    actual_lineage_retriever,
):
    expected_alias_tokens = {
        "evidence:EV-DREG-7597cb": {
            "ev-goal-dreg-001-b003",
            "evidence:ev-goal-dreg-001-b003",
        },
        "decision:DEC-20260811-e77b9d": {
            "dec-goal-dreg-001-b003",
            "decision:dec-goal-dreg-001-b003",
        },
        "hypothesis:H-XOR-d1a480": {
            "h-xor-yield",
            "hypothesis:h-xor-yield",
        },
    }
    for canonical_id, aliases in expected_alias_tokens.items():
        payload = actual_lineage_retriever.index.by_source(canonical_id)[0]["payload"]
        assert set(payload["identity_tokens"]) >= aliases

    queries = [
        ("EXP-DREG-001", "experiment:EXP-DREG-001"),
        ("EV-DREG-7597cb", "evidence:EV-DREG-7597cb"),
        ("EV-GOAL-DREG-001-B003", "evidence:EV-DREG-7597cb"),
        ("DEC-20260811-e77b9d", "decision:DEC-20260811-e77b9d"),
        ("DEC-GOAL-DREG-001-B003", "decision:DEC-20260811-e77b9d"),
        ("H-XOR-d1a480", "hypothesis:H-XOR-d1a480"),
        ("H-XOR-YIELD", "hypothesis:H-XOR-d1a480"),
    ]

    for query, canonical_id in queries:
        response = actual_lineage_retriever.search(query, top_k=4)
        result = response.results[0]
        supersedes, artifacts = EXPECTED_LINEAGE[canonical_id]

        assert result.source_id == canonical_id
        assert result.score == 1.0
        assert any("exact identifier match placed first" in note for note in response.notes)
        assert result.supersedes == supersedes
        assert result.verification_artifacts == artifacts

        context = actual_lineage_retriever.get_context(result.chunk_id)
        assert context.chunk is not None
        assert context.chunk.supersedes == supersedes
        assert context.chunk.verification_artifacts == artifacts

        source = actual_lineage_retriever.get_source(canonical_id)
        assert source is not None
        assert source.supersedes == supersedes
        assert source.verification_artifacts == artifacts


def test_a_query_without_identifiers_has_no_exact_note(retriever):
    response = retriever.search("how are relations generated", top_k=5)
    assert not any("exact identifier" in note for note in response.notes)


def test_exact_lookup_fetches_all_filtered_rows_before_identity_priority(retriever):
    records = [
        {
            "id": f"reference-{index}",
            "payload": _exact_payload(
                f"evidence:EV-REF-{index:03d}",
                experiment_id="EXP-DREG-001",
            ),
        }
        for index in range(38)
    ]
    records.extend(
        [
            {
                "id": "canonical-exp",
                "payload": _exact_payload("experiment:EXP-DREG-001"),
            },
            {
                "id": "canonical-ev",
                "payload": _exact_payload("evidence:EV-DREG-7597cb"),
            },
        ]
    )
    fake = ExactLookupWindowIndex(records)
    original = retriever.index
    retriever.index = fake
    try:
        hits = retriever._exact_identifier_hits(
            "EXP-DREG-001 and EV-DREG-7597cb", filters=None, top_k=4
        )
    finally:
        retriever.index = original

    assert fake.count_limits == [len(records)]
    assert [hit["payload"]["source_id"] for hit in hits[:2]] == [
        "evidence:EV-DREG-7597cb",
        "experiment:EXP-DREG-001",
    ]


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
