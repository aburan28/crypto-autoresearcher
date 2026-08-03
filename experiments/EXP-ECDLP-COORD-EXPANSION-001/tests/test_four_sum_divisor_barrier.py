from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "four_sum_divisor_barrier.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "four_sum_divisor_barrier_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load divisor-barrier module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class FourSumDivisorBarrierTests(unittest.TestCase):
    def test_support_level_matches_d2_pair(self) -> None:
        curve = MODULE.TYPED.Curve(101, 2, 3)
        points = [(1, 39), (3, 6), (5, 21)]
        d2 = MODULE.support_level(curve, points, 2)
        d4 = MODULE.support_level(curve, points, 4)
        replay = MODULE.d2_pair_support(
            curve, d2["support_internal"]
        )
        self.assertEqual(
            d4["support_internal"], replay["support_internal"]
        )

    def test_canonical_tuple_count(self) -> None:
        curve = MODULE.TYPED.Curve(101, 2, 3)
        points = [(1, 39), (3, 6), (5, 21)]
        level = MODULE.support_level(curve, points, 4)
        self.assertEqual(level["summary"]["canonical_tuple_count"], 15)

    def test_point_payload_is_stable(self) -> None:
        points = {(3, 6), None, (1, 39)}
        self.assertEqual(
            MODULE.point_payload(points),
            [None, [1, 39], [3, 6]],
        )


if __name__ == "__main__":
    unittest.main()
