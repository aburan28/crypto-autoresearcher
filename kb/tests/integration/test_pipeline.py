"""End-to-end ingestion: idempotence, updates, deletion, and failure handling."""

from __future__ import annotations

import json

import pytest

from crypto_kb.models import IngestState


def stage(store, key, body, metadata):
    store.put(key, body.encode("utf-8"))
    store.put(key + ".metadata.json", json.dumps(metadata).encode("utf-8"))


def test_ingest_reaches_indexed(indexed_sample):
    pipeline, source_id, _ = indexed_sample
    manifest = pipeline.manifests.get(source_id)
    assert manifest.status == IngestState.INDEXED
    assert manifest.chunk_count > 0
    assert manifest.parent_chunk_count > 0
    assert manifest.point_ids
    assert manifest.indexed_at


def test_normalized_artifacts_are_written(indexed_sample):
    pipeline, source_id, _ = indexed_sample
    safe = source_id.replace(":", "__")
    assert pipeline.store.exists(f"knowledge/normalized/markdown/{safe}.md")
    assert pipeline.store.exists(f"knowledge/normalized/docling-json/{safe}.json")


def test_reingesting_unchanged_content_is_skipped(indexed_sample):
    pipeline, source_id, key = indexed_sample
    before = pipeline.index.count()

    result = pipeline.ingest_key(key)

    assert result.skipped
    assert result.reason == "fingerprint unchanged"
    assert pipeline.index.count() == before


def test_reingesting_creates_no_duplicate_points(indexed_sample):
    pipeline, _, key = indexed_sample
    before = pipeline.index.count()
    pipeline.ingest_key(key, force=True)
    assert pipeline.index.count() == before


def test_an_update_replaces_old_chunks(indexed_sample, sample_metadata):
    pipeline, source_id, key = indexed_sample
    original_points = set(pipeline.manifests.get(source_id).point_ids)

    shortened = "# Relation generation\n\nA much shorter version of the paper.\n"
    pipeline.store.put(key, shortened.encode("utf-8"))
    result = pipeline.ingest_key(key)
    assert result.ok

    current_points = set(pipeline.manifests.get(source_id).point_ids)
    in_index = {record["id"] for record in pipeline.index.by_source(source_id)}

    # The index holds exactly what the new version produced: no leftovers from
    # the old one, and nothing the manifest does not know about.
    assert in_index == current_points
    assert not (original_points - current_points) & in_index
    assert original_points != current_points, "the update produced identical chunks"


def test_metadata_change_alone_forces_a_reindex(indexed_sample, sample_metadata):
    pipeline, source_id, key = indexed_sample
    before = pipeline.manifests.get(source_id).document_fingerprint

    updated = dict(sample_metadata, claim_status="published")
    pipeline.store.put(key + ".metadata.json", json.dumps(updated).encode("utf-8"))
    result = pipeline.ingest_key(key)

    assert not result.skipped
    assert pipeline.manifests.get(source_id).document_fingerprint != before


def test_deletion_removes_points_and_tombstones_the_manifest(indexed_sample):
    pipeline, source_id, _ = indexed_sample
    assert pipeline.index.by_source(source_id)

    pipeline.delete_source(source_id)

    assert pipeline.index.by_source(source_id) == []
    assert pipeline.manifests.get(source_id).status == IngestState.DELETED


def test_deletion_retracts_the_sparse_contribution(indexed_sample):
    pipeline, source_id, _ = indexed_sample
    before = pipeline.sparse.stats.doc_count
    pipeline.delete_source(source_id)
    assert pipeline.sparse.stats.doc_count == before - 1


def test_missing_sidecar_is_rejected_not_indexed(pipeline, store):
    key = "knowledge/source/papers/orphan.md"
    store.put(key, b"# A paper with no sidecar\n\nbody text here\n")

    result = pipeline.ingest_key(key)

    assert result.state == IngestState.REJECTED
    assert "no sidecar" in result.reason
    assert not pipeline.index.exists() or pipeline.index.count() == 0


def test_unsupported_extension_is_rejected(pipeline, store, sample_metadata):
    key = "knowledge/source/papers/data.parquet"
    stage(store, key, "binary-ish", sample_metadata)
    result = pipeline.ingest_key(key)
    assert result.state == IngestState.REJECTED
    assert "no parser" in result.reason


def test_derived_prefixes_are_never_ingested(pipeline):
    for key in (
        "knowledge/normalized/markdown/x.md",
        "knowledge/manifests/x.json",
        "knowledge/stats/sparse-bm25-v1.json",
        "knowledge/source/papers/x.md.metadata.json",
    ):
        ingestible, reason = pipeline.should_ingest(key)
        assert not ingestible, f"{key} would be ingested ({reason})"


def test_parse_warnings_reach_the_manifest(pipeline, store, sample_metadata):
    key = "knowledge/source/papers/broken.md"
    stage(store, key, "# Body\n\nThe value is $$ 1 + ∀ x\n\nand then text.\n", sample_metadata)
    pipeline.ingest_key(key)
    manifest = pipeline.manifests.get(sample_metadata["source_id"])
    assert any("unterminated" in w for w in manifest.warnings)


def test_backfill_is_idempotent(pipeline, store, sample_document, sample_metadata):
    from crypto_kb.ingest.backfill import backfill

    for i in range(3):
        metadata = dict(sample_metadata, source_id=f"paper:test-{i:03d}")
        stage(store, f"knowledge/source/papers/p{i}.md", sample_document, metadata)

    first = backfill(pipeline)
    points_after_first = pipeline.index.count()
    second = backfill(pipeline)

    assert len(first.indexed) == 3
    assert len(second.skipped) == 3 and not second.indexed
    assert pipeline.index.count() == points_after_first


def test_backfill_removes_orphans(pipeline, store, sample_document, sample_metadata):
    from crypto_kb.ingest.backfill import backfill

    key = "knowledge/source/papers/p0.md"
    stage(store, key, sample_document, sample_metadata)
    backfill(pipeline)

    store.delete(key)
    store.delete(key + ".metadata.json")
    report = backfill(pipeline)

    assert report.orphans_removed == [sample_metadata["source_id"]]
    assert pipeline.index.by_source(sample_metadata["source_id"]) == []


def test_identity_tokens_are_indexed(indexed_sample):
    pipeline, source_id, _ = indexed_sample
    payload = pipeline.index.by_source(source_id)[0]["payload"]
    assert source_id in payload["identity_tokens"]
    assert "test-001" in payload["identity_tokens"]


@pytest.mark.parametrize("state", [IngestState.INDEXED])
def test_manifest_records_every_pipeline_version(indexed_sample, state):
    pipeline, source_id, _ = indexed_sample
    manifest = pipeline.manifests.get(source_id)
    assert manifest.parser_version
    assert manifest.chunker_version
    assert manifest.dense_model == pipeline.dense.model_id
    assert manifest.sparse_model == pipeline.sparse.model_id
    assert manifest.collection == pipeline.settings.collection
