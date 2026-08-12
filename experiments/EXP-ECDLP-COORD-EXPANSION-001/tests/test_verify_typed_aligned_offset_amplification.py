from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parents[1] / "src" / "verify_typed_aligned_offset_amplification.py"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_offset_amplification_under_test", SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load offset-amplification verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyTypedAlignedOffsetAmplificationTests(unittest.TestCase):
    def test_normalize_removes_runtime_fields_recursively(self) -> None:
        self.assertEqual(
            MODULE.normalize({"a": 1, "total_wall_seconds": 4, "nested": {"peak_rss_bytes": 2, "b": 3}}),
            {"a": 1, "nested": {"b": 3}},
        )


if __name__ == "__main__":
    unittest.main()
