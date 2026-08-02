from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_four_sum_divisor_barrier.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_four_sum_divisor_barrier_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load divisor verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyFourSumDivisorBarrierTests(unittest.TestCase):
    def test_combination_count(self) -> None:
        self.assertEqual(MODULE.math_comb(8, 4), 70)
        self.assertEqual(MODULE.math_comb(12, 4), 495)

    def test_normalize_removes_timing(self) -> None:
        self.assertEqual(
            MODULE.normalize(
                {
                    "peak_rss_bytes": 1,
                    "nested": {
                        "total_wall_seconds": 2,
                        "support": 70,
                    },
                }
            ),
            {"nested": {"support": 70}},
        )


if __name__ == "__main__":
    unittest.main()
