from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "src"
SPEC = importlib.util.spec_from_file_location("typed_tt_source_aware_skeleton_test", ROOT / "typed_tt_source_aware_skeleton_preflight.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load source-aware producer")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TTSourceAwareSkeletonTests(unittest.TestCase):
    def test_prefix_order_is_unique_and_complete(self) -> None:
        prefixes = MODULE.prefix_order(2, 3)
        self.assertEqual(len(prefixes), 18)
        self.assertEqual(len(set(prefixes)), 18)

    def test_row_reduce_add_detects_new_direction(self) -> None:
        basis = {}
        counters = {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}
        self.assertTrue(MODULE.row_reduce_add([1, 2, 3], basis, 101, counters))
        self.assertFalse(MODULE.row_reduce_add([2, 4, 6], basis, 101, counters))
        self.assertTrue(MODULE.row_reduce_add([0, 1, 1], basis, 101, counters))

    def test_unrank_round_trip(self) -> None:
        dims = [2, 3, 4]
        for value in range(24):
            indices = MODULE.unrank(value, dims)
            flat = 0
            for index, dimension in zip(indices, dims):
                flat = flat * dimension + index
            self.assertEqual(flat, value)


if __name__ == "__main__":
    unittest.main()
