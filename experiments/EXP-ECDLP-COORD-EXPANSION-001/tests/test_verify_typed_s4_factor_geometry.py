from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_typed_s4_factor_geometry.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_typed_s4_factor_geometry_under_test",
        SOURCE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load factor-geometry verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyTypedS4FactorGeometryTests(unittest.TestCase):
    def test_normalize_runtime_fields(self) -> None:
        value = {
            "rank": 24,
            "total_wall_seconds": 1.0,
            "nested": [{"peak_rss_bytes_after_cell": 7, "zeros": 2}],
        }
        self.assertEqual(
            MODULE.normalize(value),
            {"rank": 24, "nested": [{"zeros": 2}]},
        )

    def test_canonical_digest_is_stable(self) -> None:
        self.assertEqual(
            MODULE.canonical_digest({"a": [1, 2], "b": 3}),
            MODULE.canonical_digest({"b": 3, "a": [1, 2]}),
        )


if __name__ == "__main__":
    unittest.main()
