from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_typed_s4_norm_rank.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_typed_s4_norm_rank_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load typed S4 verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyTypedS4NormRankTests(unittest.TestCase):
    def test_normalize_removes_only_runtime_fields(self) -> None:
        value = {
            "wall_seconds": 1.0,
            "rank": 4,
            "nested": [
                {
                    "peak_rss_bytes_after_cell": 10,
                    "field_multiplications": 7,
                }
            ],
        }
        self.assertEqual(
            MODULE.normalize(value),
            {
                "rank": 4,
                "nested": [{"field_multiplications": 7}],
            },
        )

    def test_canonical_digest_is_order_independent(self) -> None:
        self.assertEqual(
            MODULE.canonical_digest({"a": 1, "b": 2}),
            MODULE.canonical_digest({"b": 2, "a": 1}),
        )


if __name__ == "__main__":
    unittest.main()
