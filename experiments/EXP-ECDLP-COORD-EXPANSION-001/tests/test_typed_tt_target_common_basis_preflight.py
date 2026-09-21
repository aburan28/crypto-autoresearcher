from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "src"
SPEC = importlib.util.spec_from_file_location("typed_tt_target_common_basis_test", ROOT / "typed_tt_target_common_basis_preflight.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load common-basis producer")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TTTargetCommonBasisTests(unittest.TestCase):
    def test_duplicate_control_is_rank_one(self) -> None:
        self.assertEqual(MODULE.rank_mod([[1, 2], [1, 2]], 101, {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}), 1)

    def test_independent_control_increases_rank(self) -> None:
        self.assertEqual(MODULE.rank_mod([[1, 0], [0, 1]], 101, {"field_inversions": 0, "field_multiplications": 0, "field_subtractions": 0}), 2)

    def test_unfold_shape(self) -> None:
        self.assertEqual(MODULE.unfold(list(range(24)), [2, 3, 4], 2), [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18, 19], [20, 21, 22, 23]])


if __name__ == "__main__":
    unittest.main()
