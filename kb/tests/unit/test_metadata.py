"""Provenance discipline: what a sidecar is allowed to assert."""

from __future__ import annotations

import json

import pytest

from crypto_kb.metadata import MetadataError, load_metadata, metadata_fingerprint, normalize
from crypto_kb.models import Authority, ClaimStatus, EvidenceLevel, SourceType, authority_rank


def base(**overrides):
    data = {
        "schema_version": 1,
        "source_id": "paper:test-001",
        "title": "A paper",
        "source_type": "paper",
    }
    data.update(overrides)
    return data


def test_model_suggested_sidecar_cannot_assert_authority():
    metadata, warnings = normalize(
        base(
            provenance_class="model-suggested",
            claim_status="reproduced",
            evidence_level="independently-reproduced",
            run_ids=["run-1"],
            topics=["index-calculus"],
        )
    )
    assert metadata.evidence_level is None
    assert metadata.run_ids == []
    assert metadata.claim_status == ClaimStatus.EXTERNAL_SOURCE
    # The soft field survives -- topics are a suggestion, not a claim.
    assert metadata.topics == ["index-calculus"]
    assert any("model-suggested" in w for w in warnings)


def test_human_authored_sidecar_keeps_its_fields():
    metadata, _ = normalize(
        base(
            source_type="experiment",
            source_id="experiment:EXP-1",
            evidence_level="independently-reproduced",
            run_ids=["run-1"],
        )
    )
    assert metadata.evidence_level == EvidenceLevel.INDEPENDENTLY_REPRODUCED
    assert metadata.run_ids == ["run-1"]


def test_evidence_level_overrides_a_disagreeing_authority():
    metadata, warnings = normalize(
        base(
            source_type="experiment",
            source_id="experiment:EXP-1",
            evidence_level="single-run",
            authority="reproduced-experiment",
        )
    )
    assert metadata.authority == Authority.SINGLE_RUN_EXPERIMENT
    assert any("disagrees with evidence_level" in w for w in warnings)


def test_missing_authority_is_derived_conservatively():
    note, _ = normalize(base(source_type="internal-note", source_id="note:n-1"))
    assert note.authority == Authority.INTERNAL_ANALYSIS
    paper, _ = normalize(base())
    assert paper.authority == Authority.PREPRINT


def test_internal_claim_status_on_a_paper_is_rejected():
    metadata, warnings = normalize(base(claim_status="reproduced"))
    assert metadata.claim_status == ClaimStatus.EXTERNAL_SOURCE
    assert any("internal status on an external paper" in w for w in warnings)


def test_superseded_by_implies_superseded():
    metadata, warnings = normalize(base(superseded_by="paper:test-002"))
    assert metadata.superseded is True
    assert any("superseded_by is set" in w for w in warnings)


def test_unknown_field_is_rejected():
    with pytest.raises(MetadataError):
        normalize(base(confidence="high"))


def test_unnamespaced_source_id_is_rejected():
    with pytest.raises(MetadataError):
        normalize(base(source_id="test-001"))


def test_missing_sidecar_is_an_error_not_a_guess(store):
    store.put("knowledge/source/papers/x.md", b"# body")
    with pytest.raises(MetadataError, match="no sidecar"):
        load_metadata(store, "knowledge/source/papers/x.md")


def test_invalid_json_sidecar_is_an_error(store):
    store.put("knowledge/source/papers/x.md", b"# body")
    store.put("knowledge/source/papers/x.md.metadata.json", b"{not json")
    with pytest.raises(MetadataError, match="not valid JSON"):
        load_metadata(store, "knowledge/source/papers/x.md")


def test_fingerprint_is_computed_after_normalisation():
    """A sidecar edit that normalises to the same values must not re-index."""
    stated, _ = normalize(base(source_type="experiment", source_id="experiment:E", evidence_level="single-run", authority="single-run-experiment"))
    implied, _ = normalize(base(source_type="experiment", source_id="experiment:E", evidence_level="single-run"))
    assert metadata_fingerprint(stated) == metadata_fingerprint(implied)


def test_fingerprint_changes_on_a_real_edit():
    left, _ = normalize(base())
    right, _ = normalize(base(title="A different paper"))
    assert metadata_fingerprint(left) != metadata_fingerprint(right)


def test_authority_ordering_is_total_and_ranked():
    assert authority_rank(Authority.MACHINE_CHECKED_PROOF) < authority_rank(Authority.REPRODUCED_EXPERIMENT)
    assert authority_rank(Authority.REPRODUCED_EXPERIMENT) < authority_rank(Authority.SINGLE_RUN_EXPERIMENT)
    assert authority_rank(Authority.SINGLE_RUN_EXPERIMENT) < authority_rank(Authority.PEER_REVIEWED)
    assert authority_rank(Authority.PEER_REVIEWED) < authority_rank(Authority.PREPRINT)
    assert authority_rank(Authority.INTERNAL_ANALYSIS) < authority_rank(Authority.AGENT_HYPOTHESIS)
    assert authority_rank(None) > authority_rank(Authority.AGENT_HYPOTHESIS)


def test_payload_fields_cover_every_filterable_field():
    from crypto_kb.retrieval.filters import _LIST_FIELDS

    metadata, _ = normalize(base())
    payload = metadata.payload_fields()
    for field in _LIST_FIELDS.values():
        assert field in payload, f"{field} is filterable but never reaches the payload"


def test_sidecar_round_trips_through_the_store(store):
    store.put("knowledge/source/papers/x.md", b"# body")
    store.put(
        "knowledge/source/papers/x.md.metadata.json",
        json.dumps(base(topics=["semaev"])).encode("utf-8"),
    )
    metadata, warnings = load_metadata(store, "knowledge/source/papers/x.md")
    assert metadata.source_id == "paper:test-001"
    assert metadata.source_type == SourceType.PAPER
    assert metadata.topics == ["semaev"]
    assert warnings == []
