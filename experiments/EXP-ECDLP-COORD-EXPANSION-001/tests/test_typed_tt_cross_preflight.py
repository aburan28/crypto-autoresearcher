from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "src"
SPEC = importlib.util.spec_from_file_location("typed_tt_cross_preflight_test", ROOT / "typed_tt_cross_preflight.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load cross producer")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TTCrossPreflightTests(unittest.TestCase):
    def test_rank_one_cross_control(self) -> None:
        oracle = MODULE.Oracle
        self.assertEqual(MODULE.independent_rows([[1, 2], [2, 4]], 101)[1], 1)

    def test_unrank_round_trip(self) -> None:
        dimensions = [2, 3, 4]
        for value in range(24):
            indices = MODULE.unrank(value, dimensions)
            flat = 0
            for index, dimension in zip(indices, dimensions):
                flat = flat * dimension + index
            self.assertEqual(flat, value)

    def test_cross_rejects_above_ambient(self) -> None:
        class EmptyOracle:
            p = 101

            def value(self, indices):
                raise AssertionError("ambient rejection must not query")

        result = MODULE.cross_cut(EmptyOracle(), [2, 2], 1, 3, 1)
        self.assertEqual(result["status"], "REJECTED_ABOVE_AMBIENT")


if __name__ == "__main__":
    unittest.main()
