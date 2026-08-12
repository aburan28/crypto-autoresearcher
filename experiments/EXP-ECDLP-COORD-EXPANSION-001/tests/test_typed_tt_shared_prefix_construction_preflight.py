from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "src"
SPEC = importlib.util.spec_from_file_location("typed_tt_shared_prefix_construction_test", ROOT / "typed_tt_shared_prefix_construction_preflight.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load shared-prefix producer")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TTSharedPrefixConstructionTests(unittest.TestCase):
    def test_duplicate_control_passes_and_independent_control_rejects(self) -> None:
        result = MODULE.synthetic_controls(101)
        self.assertTrue(result["pass"])
        self.assertTrue(result["duplicate_pass"])
        self.assertTrue(result["independent_rejected"])

    def test_unfold_shape(self) -> None:
        self.assertEqual(MODULE.unfold(list(range(24)), [2, 3, 4], 2), [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18, 19], [20, 21, 22, 23]])

    def test_rank_one_skeleton_reconstructs(self) -> None:
        counters = {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}
        matrix = [[1, 2, 3], [2, 4, 6]]
        skeleton = MODULE.build_skeleton(matrix, 101, counters)
        self.assertEqual(skeleton["rank"], 1)
        self.assertEqual(MODULE.reconstruct(matrix, skeleton, 101)[0], 0)


if __name__ == "__main__":
    unittest.main()
