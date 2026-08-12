"""Identity: fingerprints must change exactly when the index would."""

from __future__ import annotations

from crypto_kb.hashing import (
    canonical_json,
    chunk_id,
    document_fingerprint,
    hash_metadata,
    point_id,
    sha256_text,
)


def _fingerprint(**overrides):
    base = dict(
        source_content_hash="sha256:aaa",
        metadata_hash="sha256:bbb",
        parser_version="native-markdown-v1",
        chunker_version="crypto-hierarchical-v1",
        embedding_model_version="hashing-ngram-v1:512+bm25-v1",
    )
    base.update(overrides)
    return document_fingerprint(**base)


def test_fingerprint_is_stable():
    assert _fingerprint() == _fingerprint()


def test_every_stage_version_participates():
    baseline = _fingerprint()
    for field in (
        "source_content_hash",
        "metadata_hash",
        "parser_version",
        "chunker_version",
        "embedding_model_version",
    ):
        assert _fingerprint(**{field: "changed"}) != baseline, f"{field} does not affect the fingerprint"


def test_metadata_hash_ignores_key_order():
    left = hash_metadata({"a": 1, "b": [1, 2]})
    right = hash_metadata({"b": [1, 2], "a": 1})
    assert left == right


def test_metadata_hash_notices_value_changes():
    assert hash_metadata({"a": 1}) != hash_metadata({"a": 2})


def test_canonical_json_is_sorted_and_compact():
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_point_id_is_a_deterministic_uuid():
    first = point_id("paper:x", 3, sha256_text("body"))
    assert first == point_id("paper:x", 3, sha256_text("body"))
    assert first != point_id("paper:x", 4, sha256_text("body"))
    assert first != point_id("paper:y", 3, sha256_text("body"))
    assert len(first) == 36 and first.count("-") == 4


def test_point_id_changes_with_content():
    assert point_id("paper:x", 0, sha256_text("a")) != point_id("paper:x", 0, sha256_text("b"))


def test_chunk_id_separates_fields_unambiguously():
    # Without a separator, ("x", 12, "a") and ("x", 1, "2a") would collide.
    assert chunk_id("x", 12, "a") != chunk_id("x", 1, "2a")
