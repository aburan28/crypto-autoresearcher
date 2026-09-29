"""Offline intake tests: feed formats, deduplication, and fail-closed archive."""

from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import yaml

from tools import daily_literature_ingest as intake


RSS = b"""<?xml version="1.0"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel><item>
    <title>Faster Elliptic Curve Discrete Logarithm Walks</title>
    <link>https://eprint.iacr.org/2026/2456</link>
    <dc:creator>Ada Smith, Ben Jones</dc:creator>
    <pubDate>Sat, 26 Sep 2026 08:00:00 +0000</pubDate>
    <description><![CDATA[We improve the performance of elliptic curve walks on toy instances. No general discrete logarithm break is claimed.]]></description>
  </item></channel>
</rss>"""

ATOM = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2609.12345v2</id>
    <title>ML-KEM side-channel attack</title>
    <published>2026-09-24T00:00:00Z</published>
    <updated>2026-09-26T09:00:00Z</updated>
    <author><name>Ada Smith</name></author>
    <summary>We attack a leaky implementation of ML-KEM. This does not break the scheme mathematically.</summary>
  </entry>
</feed>"""


class S3Error(Exception):
    pass


class PreconditionFailed(S3Error):
    def __init__(self):
        self.response = {"Error": {"Code": "PreconditionFailed"},
                         "ResponseMetadata": {"HTTPStatusCode": 412}}


class FakeS3:
    class exceptions:
        ClientError = S3Error

    def __init__(self):
        self.objects = {}
        self.writes = 0
        self.write_keys = []

    def head_object(self, *, Bucket, Key):  # noqa: N803
        if (Bucket, Key) not in self.objects:
            raise AssertionError("HEAD of missing key requires ListBucket")
        return self.objects[Bucket, Key]

    def put_object(self, *, Bucket, Key, Body, Metadata=None, **kwargs):  # noqa: N803
        assert kwargs["IfNoneMatch"] == "*"
        assert kwargs["ContentType"] == ("application/json" if Key.endswith(".metadata.json") else "application/pdf")
        if (Bucket, Key) in self.objects:
            raise PreconditionFailed()
        self.writes += 1
        self.write_keys.append(Key)
        self.objects[Bucket, Key] = {"Metadata": Metadata or {}, "VersionId": "version-1", "Body": Body}
        return {"VersionId": "version-1"}

    def get_object(self, *, Bucket, Key):  # noqa: N803
        return {"Body": BytesIO(self.objects[Bucket, Key]["Body"])}


class DailyLiteratureTests(unittest.TestCase):
    def test_feed_selection_parses_revisions_and_source_metadata(self):
        arxiv = intake.parse_arxiv(ATOM)[0]
        eprint = intake.parse_eprint(RSS)[0]
        self.assertEqual(arxiv.identifier, "2609.12345")  # v2 is one paper
        self.assertEqual(arxiv.url, "https://arxiv.org/abs/2609.12345")
        self.assertEqual(eprint.authors, ("Ada Smith", "Ben Jones"))
        self.assertTrue(intake.relevant(eprint))
        responses = {intake.EPRINT_FEED: RSS}
        get = lambda url: responses.get(url, ATOM)
        result = intake.recent_papers(datetime(2026, 9, 27, tzinfo=timezone.utc), 7, get)
        self.assertEqual([p.dedup_key for p in result],
                         ["arxiv:2609.12345", "eprint:2026/2456"])

    def test_missing_rss_abstract_uses_publisher_metadata_or_fails(self):
        bare = RSS.replace(b"We improve the performance of elliptic curve walks on toy instances. No general discrete logarithm break is claimed.", b"")
        paper = intake.parse_eprint(bare)[0]
        page = b'<html><meta name="citation_abstract" content="We speed up elliptic curve walks only at toy scale."></html>'
        found = intake.enrich_eprint(paper, page)
        self.assertEqual(found.abstract, "We speed up elliptic curve walks only at toy scale.")
        with self.assertRaisesRegex(ValueError, "lacks an abstract"):
            intake.enrich_eprint(paper, b"<html></html>")

    def test_archive_is_immutable_and_a_failed_download_creates_no_entry(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / "knowledge/literature").mkdir(parents=True)
            paper = intake.parse_eprint(RSS)[0]
            s3 = FakeS3()
            pdf = b"%PDF-1.7\nexample\n%%EOF\n"
            now = datetime(2026, 9, 27, tzinfo=timezone.utc)
            with patch.object(intake, "new_id", return_value="KN-LIT-abcdef"):
                with self.assertRaisesRegex(ValueError, "invalid or incomplete PDF"):
                    intake.ingest([paper], root, "papers", s3, get=lambda *_: b"bad", now=now)
                self.assertFalse(list((root / "knowledge/literature").iterdir()))
                result = intake.ingest([paper], root, "papers", s3, get=lambda *_: pdf, now=now)
            self.assertEqual(len(result["added"]), 1)
            self.assertEqual(s3.writes, 2)
            self.assertTrue(s3.write_keys[0].endswith(".metadata.json"))
            sidecar = json.loads(s3.objects["papers", s3.write_keys[0]]["Body"])
            self.assertEqual(sidecar["source_id"], "paper:eprint-2026-2456")
            self.assertEqual(sidecar["provenance_class"], "deterministic")
            self.assertEqual(sidecar["authority"], "unreviewed-preprint")
            entry = (root / "knowledge/literature/KN-LIT-abcdef.md").read_text()
            fm = yaml.safe_load(entry.split("---", 2)[1])
            self.assertEqual(fm["confidence"], "reported")
            self.assertEqual(fm["source_artifact"]["sha256"], hashlib.sha256(pdf).hexdigest())
            self.assertEqual(fm["source_artifact"]["version_id"], "version-1")
            self.assertEqual(intake.ingest([paper], root, "papers", s3, get=lambda *_: pdf)["added"], [])
            self.assertEqual(s3.writes, 2)

    def test_existing_s3_hash_mismatch_and_queue_overflow_fail_without_entry(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / "knowledge/literature").mkdir(parents=True)
            paper = intake.parse_eprint(RSS)[0]
            s3 = FakeS3()
            key = f"knowledge/source/papers/eprint/{paper.identifier}/paper.pdf"
            s3.objects["papers", key] = {"Metadata": {"sha256": "wrong"}}
            pdf = b"%PDF-1.7\nexample\n%%EOF\n"
            with self.assertRaisesRegex(ValueError, "different/unrecorded hash"):
                intake.ingest([paper], root, "papers", s3, get=lambda *_: pdf)
            with self.assertRaisesRegex(ValueError, "exceed"):
                intake.ingest([paper], root, "papers", s3, max_new=0,
                              get=lambda *_: (_ for _ in ()).throw(AssertionError("downloaded")))
            self.assertFalse(list((root / "knowledge/literature").iterdir()))

    def test_partial_run_reuses_matching_s3_object_and_deduplicates_title(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / "knowledge/literature").mkdir(parents=True)
            eprint = intake.parse_eprint(RSS)[0]
            twin = intake.parse_arxiv(ATOM)[0]
            twin = intake.replace(twin, title=eprint.title)
            pdf = b"%PDF-1.7\nexample\n%%EOF\n"
            s3 = FakeS3()
            key = f"knowledge/source/papers/eprint/{eprint.identifier}/paper.pdf"
            s3.objects["papers", key] = {"Metadata": {"sha256": hashlib.sha256(pdf).hexdigest()},
                                          "VersionId": "preexisting-version"}
            with patch.object(intake, "new_id", return_value="KN-LIT-123abc"):
                result = intake.ingest([eprint, twin], root, "papers", s3,
                                       get=lambda *_: pdf)
            self.assertEqual(len(result["added"]), 1)
            self.assertEqual(result["existing"], ["arxiv:2609.12345"])
            self.assertEqual(s3.writes, 1)  # missing sidecar is written; matching PDF is reused
            record = yaml.safe_load((root / "knowledge/literature/KN-LIT-123abc.md")
                                    .read_text().split("---", 2)[1])
            self.assertEqual(record["source_artifact"]["version_id"], "preexisting-version")

    def test_model_distillation_uses_pdf_pages_and_rejects_fabricated_quotes(self):
        try:
            import fitz
        except ImportError:
            self.skipTest("optional PyMuPDF not installed")

        paper = intake.parse_eprint(RSS)[0]
        quote = "We improve the cost of this toy walk through a new partition."
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "\n".join([quote] * 13))
        pdf = doc.tobytes()
        doc.close()
        seen = {}

        class Response(BytesIO):
            pass

        result = {"contribution": "The authors report a faster toy walk.",
                  "affected_scope": "Toy curves only.",
                  "reported_cost": "Not stated in extracted text.",
                  "limitations": "No production-size solve is described.",
                  "evidence": [{"page": 1, "quote": quote}]}

        def fake_urlopen(request, timeout):
            seen["request"] = json.loads(request.data)
            return Response(json.dumps({"stop_reason": "end_turn", "content": [
                {"type": "text", "text": json.dumps(result)}],
                "usage": {"input_tokens": 123}}).encode())

        with patch.object(intake, "urlopen", side_effect=fake_urlopen):
            distilled = intake.distill_pdf(paper, pdf, "dummy", "test-model")
        self.assertEqual(distilled["pages_extracted"], 1)
        self.assertFalse(distilled["text_truncated"])
        self.assertEqual(distilled["usage"]["input_tokens"], 123)
        self.assertIn("[PDF page 1]", seen["request"]["messages"][0]["content"])
        self.assertEqual(seen["request"]["output_config"]["format"]["type"], "json_schema")
        result["evidence"][0]["quote"] = "A full 256-bit key was recovered in seconds."
        with self.assertRaisesRegex(ValueError, "not present verbatim"):
            intake.validate_distillation(result, {1: quote})


if __name__ == "__main__":
    unittest.main()
