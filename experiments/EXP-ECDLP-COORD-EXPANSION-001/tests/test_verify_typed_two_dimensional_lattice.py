from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parents[1] / "src" / "verify_typed_two_dimensional_lattice.py"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_two_dimensional_lattice_under_test", SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load lattice verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyTypedTwoDimensionalLatticeTests(unittest.TestCase):
    def test_normalize_runtime_fields(self) -> None:
        self.assertEqual(MODULE.normalize({"x": 1, "peak_rss_bytes": 2, "nested": {"total_wall_seconds": 3, "y": 4}}), {"x": 1, "nested": {"y": 4}})


if __name__ == "__main__":
    unittest.main()
