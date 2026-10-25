"""Unit controls for rootless worker admission and public binding projection."""
from __future__ import annotations

import unittest

from prepared_worker import (PUBLIC_BINDING_SCHEMA, assert_rootless,
                             public_binding)


class PreparedWorkerTests(unittest.TestCase):
    def test_forbidden_seed_locators_are_rejected_recursively(self):
        for document in (
            {"root_files": {"base": "private/base"}},
            {"nested": [{"q_scalar_commitment_sha256": "a" * 64}]},
            {"base_root_file": "/private/base"},
        ):
            with self.subTest(document=document):
                with self.assertRaisesRegex(ValueError, "executor-forbidden"):
                    assert_rootless(document)

    def test_public_binding_drops_low_entropy_scalar_commitment(self):
        private = {
            "schema": "ectd.graph-prepared-arm-binding.v1",
            "arm_key": "P37-v0000-low_x",
            "prepared_input_sha256": "a" * 64,
            "prepared_manifest_sha256": "b" * 64,
            "q_scalar_commitment_sha256": "c" * 64,
            "target_count": 2048,
        }
        public = public_binding(private)
        self.assertEqual(public["schema"], PUBLIC_BINDING_SCHEMA)
        self.assertNotIn("q_scalar_commitment_sha256", public)
        assert_rootless(public)

    def test_unknown_private_fields_do_not_get_silently_projected(self):
        private = {"schema": "ectd.graph-prepared-arm-binding.v0",
                   "root_files": {"base": "private/base"}}
        with self.assertRaisesRegex(ValueError, "unexpected private"):
            public_binding(private)


if __name__ == "__main__":
    unittest.main()
