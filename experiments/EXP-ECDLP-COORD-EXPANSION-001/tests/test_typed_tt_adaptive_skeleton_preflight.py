from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "src"
SPEC = importlib.util.spec_from_file_location("typed_tt_adaptive_skeleton_test", ROOT / "typed_tt_adaptive_skeleton_preflight.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load adaptive producer")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RankOneOracle:
    p = 101

    def value(self, indices):
        return (indices[0] + 1) * (indices[1] + 2) * (indices[2] + 3) % self.p


class TTAdaptiveSkeletonTests(unittest.TestCase):
    def test_rank_one_plateau_stops_without_full_prefix_scan(self) -> None:
        result = MODULE.adaptive_build(RankOneOracle(), 2, 3)
        self.assertEqual(result["rank"], 1)
        self.assertLess(result["candidate_prefixes_examined"], result["total_prefixes"])
        self.assertEqual(result["stopping_reason"], "dependent_prefix_plateau")

    def test_prefix_order_is_complete(self) -> None:
        prefixes = MODULE.SOURCE_AWARE.prefix_order(2, 3)
        self.assertEqual(len(prefixes), 18)
        self.assertEqual(len(set(prefixes)), 18)

    def test_row_reduce_add_rejects_dependent_row(self) -> None:
        basis = {}
        counters = {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}
        self.assertTrue(MODULE.SOURCE_AWARE.row_reduce_add([1, 2, 3], basis, 101, counters))
        self.assertFalse(MODULE.SOURCE_AWARE.row_reduce_add([2, 4, 6], basis, 101, counters))


if __name__ == "__main__":
    unittest.main()
