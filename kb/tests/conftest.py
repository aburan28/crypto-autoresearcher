"""Shared fixtures.

The integration fixtures build a real corpus from this repository, run the
real pipeline, and query a real (embedded) Qdrant. Nothing is mocked between
"a file on disk" and "a search result" -- a retrieval test against fakes tests
the fakes.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from crypto_kb.config import Settings
from crypto_kb.embeddings.dense import build_dense_embedder
from crypto_kb.embeddings.sparse import build_sparse_embedder
from crypto_kb.index.qdrant import QdrantIndex
from crypto_kb.ingest.pipeline import IngestionPipeline
from crypto_kb.storage import LocalObjectStore

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        store_backend="local",
        local_root=tmp_path / "corpus",
        qdrant_url=":memory:",
        collection="test_knowledge_v1",
    )


@pytest.fixture
def store(settings) -> LocalObjectStore:
    return LocalObjectStore(settings.local_root)


@pytest.fixture
def pipeline(settings, store) -> IngestionPipeline:
    dense = build_dense_embedder(settings)
    sparse = build_sparse_embedder(store, settings)
    index = QdrantIndex(settings=settings, dimension=dense.dimension)
    return IngestionPipeline(
        store=store,
        index=index,
        dense_embedder=dense,
        sparse_embedder=sparse,
        settings=settings,
    )


@pytest.fixture
def retriever(pipeline):
    from crypto_kb.retrieval import KnowledgeRetriever

    return KnowledgeRetriever(
        index=pipeline.index,
        dense_embedder=pipeline.dense,
        sparse_embedder=pipeline.sparse,
        settings=pipeline.settings,
    )


@pytest.fixture
def sample_document():
    """A small document with the structures the chunker must not split."""
    return (
        "---\n"
        "id: KN-TEST-001\n"
        "tags: [semaev, index-calculus]\n"
        "---\n"
        "\n"
        "# Relation generation\n"
        "\n"
        "## 4.2 Semaev decomposition\n"
        "\n"
        "We generate relations by decomposing points over the factor base. The "
        "decomposition succeeds with probability governed by the summation "
        "polynomial S_4 evaluated at the factor-base coordinates, which for a "
        "generic prime field is what determines the yield of each trial.\n"
        "\n"
        "**Theorem 4.3.** Let E be an elliptic curve over F_p with p prime. Then the "
        "expected number of relations per trial is bounded by 1/m! where m is the "
        "decomposition arity, and this bound is tight for generic curves.\n"
        "\n"
        "*Proof.* Count the ordered decompositions and divide by the symmetry group "
        "of the factor base. The bound follows from the pigeonhole principle applied "
        "to the m! orderings of any unordered decomposition, which the relation "
        "search cannot distinguish. This completes the argument for generic curves.\n"
        "\n"
        "The cost model then follows from Theorem 4.3 directly.\n"
        "\n"
        "## 4.3 Results\n"
        "\n"
        "Table 3: measured yields on P-256.\n"
        "\n"
        "| curve | trials | relations |\n"
        "| ----- | ------ | --------- |\n"
        "| P-256 | 10000  | 12        |\n"
        "| P-384 | 10000  | 4         |\n"
        "\n"
        "# References\n"
        "\n"
        "[1] Semaev, Summation polynomials, 2004.\n"
        "[2] Gaudry, Index calculus, 2009.\n"
        "[3] Diem, On the discrete logarithm problem, 2011.\n"
        "[4] Faugere, F4, 1999.\n"
    )


@pytest.fixture
def sample_markdown(sample_document):
    """``sample_document`` as the chunker actually receives it: post-parse.

    Chunking the raw file would put the YAML frontmatter in as an unheaded
    preamble block, which is not what the pipeline does.
    """
    from crypto_kb.parsing import parse

    return parse(sample_document.encode("utf-8"), "knowledge/source/papers/sample.md").markdown


@pytest.fixture
def sample_metadata():
    return {
        "schema_version": 1,
        "source_id": "paper:test-001",
        "title": "Relation generation for prime-field index calculus",
        "source_type": "paper",
        "authors": ["Test Author"],
        "publication_year": 2026,
        "primitive": ["ECDLP"],
        "field_type": ["generic-prime-field"],
        "curves": ["P-256"],
        "topics": ["index-calculus", "semaev-polynomials"],
        "claim_status": "external-source",
        "provenance_class": "human-authored",
    }


@pytest.fixture
def indexed_sample(pipeline, store, sample_document, sample_metadata):
    """One document, staged and ingested. Returns (pipeline, source_id, key)."""
    import json

    key = "knowledge/source/papers/test-001.md"
    store.put(key, sample_document.encode("utf-8"))
    store.put(key + ".metadata.json", json.dumps(sample_metadata).encode("utf-8"))
    result = pipeline.ingest_key(key)
    assert result.ok, result.reason
    return pipeline, sample_metadata["source_id"], key


@pytest.fixture(scope="session")
def eval_environment(tmp_path_factory):
    """The full evaluation corpus: staged, ingested, and queryable.

    Session-scoped -- it stages ~400 real documents and takes ~20 seconds, and
    every test that needs it needs exactly the same one.
    """
    from crypto_kb.eval.corpus import build_eval_corpus
    from crypto_kb.ingest.backfill import backfill
    from crypto_kb.retrieval import KnowledgeRetriever

    root = tmp_path_factory.mktemp("eval-corpus")
    settings = Settings(
        store_backend="local",
        local_root=root,
        qdrant_url=":memory:",
        collection="eval_knowledge_v1",
    )
    store = LocalObjectStore(settings.local_root)
    build_eval_corpus(REPO_ROOT, store)

    dense = build_dense_embedder(settings)
    sparse = build_sparse_embedder(store, settings)
    index = QdrantIndex(settings=settings, dimension=dense.dimension)
    pipeline = IngestionPipeline(
        store=store, index=index, dense_embedder=dense, sparse_embedder=sparse, settings=settings
    )
    report = backfill(pipeline)
    assert not report.failed, [r.reason for r in report.failed]

    retriever = KnowledgeRetriever(
        index=index, dense_embedder=dense, sparse_embedder=sparse, settings=settings
    )
    return {
        "settings": settings,
        "store": store,
        "pipeline": pipeline,
        "retriever": retriever,
        "report": report,
    }
