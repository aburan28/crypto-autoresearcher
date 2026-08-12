from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "src"
SPEC = importlib.util.spec_from_file_location("typed_exact_tt_factor_preflight_test", ROOT / "typed_exact_tt_factor_preflight.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load exact TT producer")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ExactTTFactorPreflightTests(unittest.TestCase):
    def test_rank_one_tensor_factors_and_reconstructs(self) -> None:
        dimensions = [2, 3, 2]
        values = []
        for i in range(2):
            for j in range(3):
                for k in range(2):
                    values.append((i + 1) * (j + 2) * (k + 3) % 101)
        result = MODULE.exact_tt_factor(values, dimensions, 101)
        self.assertEqual(result["ranks"], [1, 1, 1, 1])
        for index, value in enumerate(values):
            indices = (index // 6, (index // 2) % 3, index % 2)
            self.assertEqual(MODULE.core_value(result["cores"], dimensions, indices, 101), value)

    def test_rank_two_control_has_middle_bond(self) -> None:
        dimensions = [2, 2, 2]
        values = [0, 1, 1, 0, 1, 0, 0, 1]
        result = MODULE.exact_tt_factor(values, dimensions, 101)
        self.assertGreater(result["ranks"][2], 1)

    def test_raw_schedule_is_nontrivial(self) -> None:
        ranks = MODULE.raw_shape_schedule()
        self.assertEqual(ranks[0], 1)
        self.assertEqual(ranks[-1], 1)
        self.assertGreater(ranks[1], 1)
        self.assertEqual(ranks[2], ranks[1])


if __name__ == "__main__":
    unittest.main()
