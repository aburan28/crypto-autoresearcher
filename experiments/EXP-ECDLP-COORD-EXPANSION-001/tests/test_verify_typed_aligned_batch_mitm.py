from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_typed_aligned_batch_mitm.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_typed_aligned_batch_mitm_under_test",
        SOURCE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load aligned-batch verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyTypedAlignedBatchMitmTests(unittest.TestCase):
    def test_normalize_runtime_fields(self) -> None:
        value = {
            "rank": 4,
            "peak_rss_bytes": 10,
            "nested": [
                {
                    "peak_rss_bytes_after_family": 20,
                    "covered": 3,
                }
            ],
        }
        self.assertEqual(
            MODULE.normalize(value),
            {"rank": 4, "nested": [{"covered": 3}]},
        )

    def test_canonical_digest_is_stable(self) -> None:
        self.assertEqual(
            MODULE.canonical_digest({"x": 1, "y": [2]}),
            MODULE.canonical_digest({"y": [2], "x": 1}),
        )


if __name__ == "__main__":
    unittest.main()
