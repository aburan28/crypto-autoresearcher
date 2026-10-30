"""Pure planted byte/commit controls; never invokes credentials or a probe."""
import copy
import gzip
from hashlib import sha256
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("storage_probe_tested", HERE / "run_probe.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class StoredObjectTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "public.gz"
        self.logical = b"planted public bytes; no curve records" * 20
        self.path.write_bytes(gzip.compress(self.logical, mtime=0))
        digest = sha256(self.path.read_bytes()).hexdigest()
        self.pointer = dict(schema="crypto.autoresearch.blob_pointer.v1", sha256=digest,
                            size=self.path.stat().st_size, encoding="gzip",
                            content_sha256=sha256(self.logical).hexdigest(), content_size=len(self.logical),
                            uri=f"{M.REMOTE}/sha256/{digest[:2]}/{digest}")

    def test_both_stored_and_logical_bytes_pass(self):
        result = M.verify_object(self.pointer, self.path)
        self.assertEqual(result["content_sha256"], sha256(self.logical).hexdigest())
        self.assertEqual(result["content_bytes"], len(self.logical))

    def test_wrong_object_destination_rejected_before_get(self):
        pointer = dict(self.pointer, uri="s3://unrelated/payload")
        with self.assertRaisesRegex(ValueError, "canonical pointer"):
            M.validate_pointer(pointer)

    def test_wrong_stored_digest_rejected(self):
        self.path.write_bytes(self.path.read_bytes() + b"wrong")
        with self.assertRaisesRegex(ValueError, "stored object"):
            M.verify_object(self.pointer, self.path)

    def test_wrong_logical_digest_or_size_rejected(self):
        for change in ({"content_sha256": "0" * 64}, {"content_size": 1}):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "logical object"):
                M.verify_object(dict(self.pointer, **change), self.path)

    def test_only_positive_integer_sizes_are_accepted(self):
        for value in (True, -1, 0, "10"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                M.validate_pointer(dict(self.pointer, content_size=value))


if __name__ == "__main__":
    unittest.main()
