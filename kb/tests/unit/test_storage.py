"""Object store and manifest behaviour."""

from __future__ import annotations

import pytest

from crypto_kb.models import IngestState, Manifest
from crypto_kb.storage.manifests import ManifestStore, manifest_key


def test_put_get_round_trip(store):
    store.put("knowledge/source/papers/a.md", b"hello")
    assert store.get("knowledge/source/papers/a.md") == b"hello"
    assert store.exists("knowledge/source/papers/a.md")


def test_head_reports_size_and_etag(store):
    store.put("knowledge/source/papers/a.md", b"hello")
    info = store.head("knowledge/source/papers/a.md")
    assert info.size == 5
    assert info.etag


def test_head_of_missing_object_is_none(store):
    assert store.head("nope/missing.md") is None


def test_list_filters_by_prefix(store):
    store.put("knowledge/source/papers/a.md", b"a")
    store.put("knowledge/source/notes/b.md", b"b")
    keys = {info.key for info in store.list("knowledge/source/papers/")}
    assert keys == {"knowledge/source/papers/a.md"}


def test_list_of_a_missing_prefix_is_empty(store):
    assert list(store.list("knowledge/source/nothing/")) == []


def test_delete_is_idempotent(store):
    store.put("k/a.md", b"a")
    store.delete("k/a.md")
    store.delete("k/a.md")
    assert not store.exists("k/a.md")


def test_keys_cannot_escape_the_root(store):
    with pytest.raises(ValueError, match="escapes the store root"):
        store.put("../escaped.md", b"x")


def test_absolute_keys_are_rejected(store):
    with pytest.raises(ValueError, match="must be relative"):
        store.get("/etc/passwd")


def test_uri_is_addressable(store):
    store.put("k/a.md", b"a")
    assert store.uri("k/a.md").startswith("file://")


def _manifest(source_id="paper:a"):
    return Manifest(
        source_id=source_id,
        s3_key="knowledge/source/papers/a.md",
        source_sha256="sha256:a",
        metadata_hash="sha256:b",
        document_fingerprint="sha256:c",
        status=IngestState.INDEXED,
        chunk_count=3,
        point_ids=["p1", "p2"],
        sparse_terms=["curve", "semaev"],
        sparse_mean_length=42,
    )


def test_manifest_round_trip(store):
    manifests = ManifestStore(store)
    manifests.put(_manifest())
    loaded = manifests.get("paper:a")
    assert loaded.chunk_count == 3
    assert loaded.point_ids == ["p1", "p2"]
    assert loaded.sparse_terms == ["curve", "semaev"]


def test_manifest_key_is_filesystem_safe():
    assert manifest_key("paper:eprint-2026/1486") == "knowledge/manifests/paper__eprint-2026__1486.json"


def test_missing_manifest_is_none(store):
    assert ManifestStore(store).get("paper:absent") is None


def test_deletion_leaves_a_tombstone_not_a_gap(store):
    manifests = ManifestStore(store)
    manifests.put(_manifest())
    manifests.mark_deleted("paper:a")

    tombstone = manifests.get("paper:a")
    assert tombstone is not None, "the manifest was removed instead of tombstoned"
    assert tombstone.status == IngestState.DELETED
    assert tombstone.point_ids == []
    assert tombstone.sparse_terms == []


def test_list_skips_non_manifest_objects(store):
    manifests = ManifestStore(store)
    manifests.put(_manifest())
    store.put("knowledge/manifests/notes.txt", b"not a manifest")
    assert [m.source_id for m in manifests.list()] == ["paper:a"]
