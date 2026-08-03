#!/usr/bin/env python3
"""Tests for the S3 source store, against an in-memory S3 (moto).

These run offline and touch no real bucket. They exist because the tool cannot
be exercised against `s3://crypto-autoresearcher` from this environment — no
credentials reach it — so the alternative to a mocked S3 is shipping the round
trip unverified.

The properties pinned are the ones the schema's value rests on:

  - the same bytes under two different keys adopt to ONE blob (dedup), and
    re-adopting is a no-op rather than a duplicate;
  - a manifest is immutable — a second adopt into the same package id is
    refused rather than silently overwriting what a citation may name;
  - `pull` recomputes the digest locally and REFUSES a blob whose bytes do not
    hash to its own key, instead of trusting the store;
  - a pulled package lands in the exact layout `build_source_index.py` reads.

Skips if moto is unavailable rather than failing, so the harness test suite
stays green on a machine without it.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import boto3
    from moto import mock_aws
    HAVE_MOTO = True
except ImportError:                            # pragma: no cover
    HAVE_MOTO = False

import s3_source_store as store

BUCKET = "crypto-autoresearcher"
REGION = "us-east-1"


class Args:
    """Stand-in for the argparse namespace the subcommands consume."""

    def __init__(self, **kw):
        self.bucket, self.region, self.profile = BUCKET, REGION, None
        self.endpoint_url = None
        self.prefix, self.package = "incoming/", None
        self.replace_manifest = False
        self.task_id = self.goal_id = None
        self.__dict__.update(kw)


def _seed(s3, objects: dict[str, bytes]) -> None:
    s3.create_bucket(Bucket=BUCKET)
    for key, body in objects.items():
        s3.put_object(Bucket=BUCKET, Key=key, Body=body, ContentType="application/pdf")


class KeyDerivationTests(unittest.TestCase):
    def test_blob_key_shards_on_the_digest(self) -> None:
        d = "ab12" + "0" * 60
        self.assertEqual(store.blob_key(d), f"blobs/sha256/ab/12/{d}")

    def test_a_non_digest_is_refused_rather_than_keyed(self) -> None:
        for bad in ("", "xyz", "AB12" + "0" * 60, "ab12"):
            with self.subTest(bad), self.assertRaises(ValueError):
                store.blob_key(bad)

    def test_distinct_origin_keys_keep_distinct_local_names(self) -> None:
        self.assertNotEqual(store.safe_name("a/2026/w.pdf"), store.safe_name("b/w.pdf"))


@unittest.skipUnless(HAVE_MOTO, "moto not installed")
class RoundTripTests(unittest.TestCase):
    @mock_aws
    def test_identical_bytes_under_two_keys_store_one_blob(self) -> None:
        s3 = boto3.client("s3", region_name=REGION)
        _seed(s3, {"incoming/a.pdf": b"same paper",
                   "incoming/nested/copy-of-a.pdf": b"same paper",
                   "incoming/b.pdf": b"other paper"})
        store.cmd_adopt(Args(package="PKG-1"))

        blobs = s3.list_objects_v2(Bucket=BUCKET, Prefix="blobs/")["Contents"]
        self.assertEqual(len(blobs), 2, "identical bytes must dedup to one blob")

        manifest = json.loads(s3.get_object(
            Bucket=BUCKET, Key="packages/PKG-1/manifest.json")["Body"].read())
        self.assertEqual(len(manifest["files"]), 3, "all three origins stay listed")
        digests = {f["sha256"] for f in manifest["files"]}
        self.assertEqual(len(digests), 2)

    @mock_aws
    def test_readopting_the_same_prefix_adds_no_blobs(self) -> None:
        s3 = boto3.client("s3", region_name=REGION)
        _seed(s3, {"incoming/a.pdf": b"paper one"})
        store.cmd_adopt(Args(package="PKG-1"))
        before = s3.list_objects_v2(Bucket=BUCKET, Prefix="blobs/")["KeyCount"]
        store.cmd_adopt(Args(package="PKG-2"))
        after = s3.list_objects_v2(Bucket=BUCKET, Prefix="blobs/")["KeyCount"]
        self.assertEqual(before, after, "re-adoption must be idempotent")

    @mock_aws
    def test_a_manifest_is_never_silently_overwritten(self) -> None:
        s3 = boto3.client("s3", region_name=REGION)
        _seed(s3, {"incoming/a.pdf": b"paper one"})
        self.assertEqual(store.cmd_adopt(Args(package="PKG-1")), 0)
        _seed_extra = s3.put_object(Bucket=BUCKET, Key="incoming/b.pdf", Body=b"paper two")
        # Same package id, different content: must refuse, not rewrite.
        self.assertEqual(store.cmd_adopt(Args(package="PKG-1")), 1)
        manifest = json.loads(s3.get_object(
            Bucket=BUCKET, Key="packages/PKG-1/manifest.json")["Body"].read())
        self.assertEqual(len(manifest["files"]), 1, "the original manifest survived")

    @mock_aws
    def test_blob_metadata_preserves_the_name_the_key_destroys(self) -> None:
        s3 = boto3.client("s3", region_name=REGION)
        _seed(s3, {"incoming/wesolowski-p13.pdf": b"paper"})
        store.cmd_adopt(Args(package="PKG-1"))
        key = s3.list_objects_v2(Bucket=BUCKET, Prefix="blobs/")["Contents"][0]["Key"]
        meta = s3.head_object(Bucket=BUCKET, Key=key)["Metadata"]
        self.assertEqual(meta["original-filename"], "wesolowski-p13.pdf")
        self.assertEqual(meta["package"], "PKG-1")
        self.assertEqual(meta["sha256"], key.rsplit("/", 1)[1])


@unittest.skipUnless(HAVE_MOTO, "moto not installed")
class PullTests(unittest.TestCase):
    @mock_aws
    def test_pull_writes_the_layout_the_source_index_reads(self) -> None:
        s3 = boto3.client("s3", region_name=REGION)
        _seed(s3, {"incoming/a.pdf": b"paper one", "incoming/b.pdf": b"paper two"})
        store.cmd_adopt(Args(package="PKG-PULL"))

        with tempfile.TemporaryDirectory() as tmp:
            original, store.REPO = store.REPO, tmp
            try:
                self.assertEqual(store.cmd_pull(Args(package="PKG-PULL")), 0)
                base = Path(tmp) / "inputs" / "PKG-PULL"
                self.assertTrue((base / "provenance.json").exists())
                for name in ("a.pdf", "b.pdf"):
                    self.assertTrue((base / "sources" / name).exists())
                    sidecar = (base / "sources" / f"{name}.sha256").read_text()
                    # `shasum -a 256` format, so ECTD and pulled packages verify alike.
                    self.assertRegex(sidecar, rf"^[0-9a-f]{{64}}  {name}\n$")
                prov = json.loads((base / "provenance.json").read_text())
                self.assertEqual(prov["schema"], store.PROVENANCE_SCHEMA)
                self.assertTrue(all(a["status"] == "retrieved" for a in prov["attempts"]))
            finally:
                store.REPO = original

    @mock_aws
    def test_pull_refuses_a_blob_whose_bytes_do_not_match_its_key(self) -> None:
        """The store is verified, not trusted: the digest is recomputed locally."""
        s3 = boto3.client("s3", region_name=REGION)
        _seed(s3, {"incoming/a.pdf": b"paper one"})
        store.cmd_adopt(Args(package="PKG-BAD"))
        manifest = json.loads(s3.get_object(
            Bucket=BUCKET, Key="packages/PKG-BAD/manifest.json")["Body"].read())
        # Corrupt the stored bytes while leaving the key (and so the claimed
        # digest) untouched -- the exact failure content addressing must catch.
        s3.put_object(Bucket=BUCKET, Key=manifest["files"][0]["blob_key"],
                      Body=b"tampered")

        with tempfile.TemporaryDirectory() as tmp:
            original, store.REPO = store.REPO, tmp
            try:
                self.assertEqual(store.cmd_pull(Args(package="PKG-BAD")), 1)
                base = Path(tmp) / "inputs" / "PKG-BAD" / "sources"
                self.assertTrue((base / "a.pdf.FAIL").exists(), "failure marker written")
                self.assertFalse((base / "a.pdf").exists(), "bad bytes not kept")
                prov = json.loads(
                    (Path(tmp) / "inputs" / "PKG-BAD" / "provenance.json").read_text())
                self.assertEqual(prov["attempts"][0]["status"], "unretrieved")
                self.assertIn("digest mismatch", prov["attempts"][0]["reason"])
            finally:
                store.REPO = original

    @mock_aws
    def test_verify_detects_a_tampered_blob(self) -> None:
        s3 = boto3.client("s3", region_name=REGION)
        _seed(s3, {"incoming/a.pdf": b"paper one"})
        store.cmd_adopt(Args(package="PKG-V"))
        self.assertEqual(store.cmd_verify(Args(package="PKG-V")), 0)
        manifest = json.loads(s3.get_object(
            Bucket=BUCKET, Key="packages/PKG-V/manifest.json")["Body"].read())
        s3.put_object(Bucket=BUCKET, Key=manifest["files"][0]["blob_key"], Body=b"x")
        self.assertEqual(store.cmd_verify(Args(package="PKG-V")), 1)


if __name__ == "__main__":
    unittest.main()
