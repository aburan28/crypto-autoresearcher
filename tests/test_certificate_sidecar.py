"""harness/certificate_sidecar.py keeps a witness statement beside the run,
without touching the pinned run wrapper."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest

from harness import certificate_sidecar as sidecar
from harness import finite_yaml_locked_v3 as locked

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CertificateSidecarTests(unittest.TestCase):
    def test_a_statement_is_written_once_and_read_back(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "runs", "RUN-X-1"))
            cert = {"kind": "discrete_log", "verified": True, "verifier": "v",
                    "statement": {"curve": {"p": 223, "a": 0, "b": 171}, "P": [105, 42], "Q": [81, 42], "k": 2}}
            path = sidecar.write_statement("EXP-X", "RUN-X-1", cert, out_root=root)
            self.assertEqual(os.path.basename(path), "certificate.json")
            doc = json.load(open(path))
            self.assertEqual(doc["statement"]["k"], 2)
            self.assertEqual(doc["kind"], "discrete_log")
            self.assertEqual(sidecar.read_statement("EXP-X", "RUN-X-1", out_root=root)["k"], 2)
            with self.assertRaises(FileExistsError):
                sidecar.write_statement("EXP-X", "RUN-X-1", cert, out_root=root)

    def test_a_certificate_without_a_statement_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "runs", "RUN-X-2"))
            self.assertIsNone(sidecar.write_statement("EXP-X", "RUN-X-2", {"kind": "none"}, out_root=root))
            self.assertIsNone(sidecar.write_statement("EXP-X", "RUN-X-2", None, out_root=root))
            self.assertIsNone(sidecar.read_statement("EXP-X", "RUN-X-2", out_root=root))
            self.assertFalse(os.path.exists(os.path.join(root, "runs", "RUN-X-2", "certificate.json")))

    def test_a_missing_run_directory_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(FileNotFoundError):
                sidecar.write_statement("EXP-X", "RUN-X-3", {"statement": {"k": 1}}, out_root=root)

    def test_the_pinned_run_wrapper_is_untouched(self) -> None:
        """The reason this module exists: the locked plans pin harness/runner.py."""
        digest = hashlib.sha256(open(os.path.join(REPO, "harness", "runner.py"), "rb").read()).hexdigest()
        self.assertEqual(digest, locked.ORIGINAL_SOURCE_PINS["harness/runner.py"])
