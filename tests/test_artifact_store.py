"""Stored forms of run artifacts: compressed and offloaded, never a different content digest."""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import artifact_store as store  # noqa: E402

BIG = b'{"rows": [' + b",".join(b'{"i": %d, "x": "abcdefgh"}' % i for i in range(60_000)) + b"]}\n"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setenv("CRYPTO_AR_BLOB_CACHE", str(tmp_path / "cache"))
    monkeypatch.delenv("CRYPTO_AR_BLOBSTORE", raising=False)
    return tmp_path / "cache"


def test_small_and_kept_artifacts_stay_as_written(tmp_path, cache):
    (tmp_path / "small.json").write_bytes(b"{}")
    (tmp_path / "manifest.yaml").write_bytes(BIG)
    assert store.compact(tmp_path, ["small.json", "manifest.yaml", "absent.json"]) == {}
    assert (tmp_path / "manifest.yaml").read_bytes() == BIG


def test_large_artifact_is_gzipped_deterministically_and_reads_back(tmp_path, cache):
    for run in ("a", "b"):
        d = tmp_path / run
        d.mkdir()
        (d / "raw-result.json").write_bytes(BIG)
        entry = store.compact(d, ["raw-result.json"], compress_min=1024)["raw-result.json"]
        assert entry["path"] == "raw-result.json.gz" and entry["encoding"] == "gzip"
        assert entry["content_sha256"] == sha(BIG) and entry["content_size"] == len(BIG)
        assert not (d / "raw-result.json").exists()
        assert store.read_bytes(d / "raw-result.json") == BIG
        assert store.content_digest(d / "raw-result.json") == sha(BIG)
        assert store.stored_matches(d, "raw-result.json", entry, sha(BIG))
    # same bytes, same .gz: a re-run or a replay produces the identical stored file
    assert ((tmp_path / "a/raw-result.json.gz").read_bytes()
            == (tmp_path / "b/raw-result.json.gz").read_bytes())


def test_already_compressed_artifact_is_not_recompressed(tmp_path, cache):
    data = gzip.compress(BIG, mtime=0)
    (tmp_path / "roots.jsonl.gz").write_bytes(data)
    assert store.compact(tmp_path, ["roots.jsonl.gz"], compress_min=1024) == {}
    assert store.read_bytes(tmp_path / "roots.jsonl.gz") == data   # its content is the .gz itself


def test_offload_writes_pointer_and_fetch_verifies(tmp_path, cache):
    blobs = store.FileStore(tmp_path / "blobs")
    run = tmp_path / "run"
    run.mkdir()
    (run / "stdout.log").write_bytes(BIG)
    entry = store.compact(run, ["stdout.log"], blobs, compress_min=1024, offload_min=1)["stdout.log"]
    assert entry["path"] == "stdout.log.gz.blob.json" and entry["uri"].startswith(blobs.base)
    assert sorted(p.name for p in run.iterdir()) == ["stdout.log.gz.blob.json"]
    pointer = json.loads((run / "stdout.log.gz.blob.json").read_text())
    assert pointer["schema"] == store.POINTER_SCHEMA and pointer["content_sha256"] == sha(BIG)
    assert store.read_bytes(run / "stdout.log") == BIG            # fetched into the cache
    assert store.verify(run / "stdout.log") == sha(BIG)
    assert store.stored_matches(run, "stdout.log", entry, sha(BIG))
    # a tampered object is refused, never served
    obj = next((tmp_path / "blobs").rglob(pointer["sha256"]))
    os.chmod(obj, 0o644)
    obj.write_bytes(b"tampered")
    for cached in cache.rglob(pointer["sha256"]):
        cached.unlink()
    with pytest.raises(store.StoreError):
        store.read_bytes(run / "stdout.log")


def test_store_writes_each_object_once(tmp_path, cache):
    blobs = store.FileStore(tmp_path / "blobs")
    f = tmp_path / "x"
    f.write_bytes(b"one")
    uri = blobs.put(f, sha(b"one"))
    assert blobs.put(f, sha(b"one")) == uri
    assert len(list((tmp_path / "blobs").rglob("*"))) == 3   # sha256/, aa/, object


def test_two_stored_forms_of_one_name_are_ambiguous(tmp_path, cache):
    (tmp_path / "raw-result.json").write_bytes(b"{}")
    (tmp_path / "raw-result.json.gz").write_bytes(gzip.compress(b"{}"))
    with pytest.raises(store.StoreError, match="more than once"):
        store.resolve(tmp_path / "raw-result.json")


def test_logical_path_picks_the_declared_one():
    declared = {"r/raw-result.json", "r/roots.jsonl.gz"}
    assert store.logical("r/raw-result.json.gz", declared) == "r/raw-result.json"
    assert store.logical("r/raw-result.json.gz.blob.json", declared) == "r/raw-result.json"
    assert store.logical("r/roots.jsonl.gz.blob.json", declared) == "r/roots.jsonl.gz"
    assert store.logical("r/raw-result.json", declared) == "r/raw-result.json"
    assert store.logical("r/other.json.gz", declared) is None


class FakeS3:
    def __init__(self):
        self.objects: dict[str, bytes] = {}

    def head_object(self, Bucket, Key):
        if Key not in self.objects:
            error = Exception("Not Found")
            error.response = {"Error": {"Code": "404"}}
            raise error

    def upload_file(self, filename, bucket, key, ExtraArgs=None):
        assert key not in self.objects, "an object is written once"
        self.objects[key] = Path(filename).read_bytes()

    def download_file(self, bucket, key, filename):
        Path(filename).write_bytes(self.objects[key])


def test_s3_store_is_content_addressed_and_write_once(tmp_path, cache, monkeypatch):
    fake = FakeS3()
    s3 = store.store_for("s3://crypto-autoresearcher/blobs", client=fake)
    run = tmp_path / "run"
    run.mkdir()
    (run / "raw-result.json").write_bytes(BIG)
    entry = store.compact(run, ["raw-result.json"], s3, compress_min=1024, offload_min=1)["raw-result.json"]
    key = f"blobs/sha256/{entry['sha256'][:2]}/{entry['sha256']}"
    assert entry["uri"] == f"s3://crypto-autoresearcher/{key}" and key in fake.objects
    assert s3.put(tmp_path / "unused", entry["sha256"]) == entry["uri"]    # exists: no upload
    monkeypatch.setattr(store, "store_for_uri", lambda uri: s3)
    assert store.read_bytes(run / "raw-result.json") == BIG


def test_cli_cat_and_hash(tmp_path, cache, capsysbinary):
    (tmp_path / "raw-result.json").write_bytes(BIG)
    store.compact(tmp_path, ["raw-result.json"], compress_min=1024)
    assert store.main(["cat", str(tmp_path / "raw-result.json")]) == 0
    assert capsysbinary.readouterr().out == BIG
    assert store.main(["hash", str(tmp_path / "raw-result.json")]) == 0
    line = capsysbinary.readouterr().out.decode()
    assert line.split()[0] == sha((tmp_path / "raw-result.json.gz").read_bytes())


def test_failed_offload_keeps_the_compressed_form_and_says_why(tmp_path, cache):
    class Down:
        def put(self, path, sha):
            raise OSError("no credentials")
    (tmp_path / "raw-result.json").write_bytes(BIG)
    entry = store.compact(tmp_path, ["raw-result.json"], Down(), compress_min=1024, offload_min=1)["raw-result.json"]
    assert entry["path"] == "raw-result.json.gz" and "no credentials" in entry["offload_error"]
    assert store.read_bytes(tmp_path / "raw-result.json") == BIG


def test_check_remote_confirms_objects_exist_at_their_size(tmp_path, cache, monkeypatch, capsys):
    fake = FakeS3()
    real_head = fake.head_object
    def head_object(Bucket, Key):
        real_head(Bucket, Key)
        return {"ContentLength": len(fake.objects[Key])}
    fake.head_object = head_object
    s3 = store.store_for("s3://crypto-autoresearcher/blobs", client=fake)
    run = tmp_path / "run"
    run.mkdir()
    (run / "raw-result.json").write_bytes(BIG)
    store.compact(run, ["raw-result.json"], s3, compress_min=1024, offload_min=1)
    monkeypatch.setattr(store, "store_for_uri", lambda uri: s3)
    pointer = run / "raw-result.json.gz.blob.json"
    assert store.main(["check-remote", str(pointer)]) == 0
    fake.objects.clear()                                   # the upload never happened
    assert store.main(["check-remote", str(pointer)]) == 1
    assert "::error" in capsys.readouterr().out
