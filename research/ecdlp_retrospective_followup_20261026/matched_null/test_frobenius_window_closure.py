#!/usr/bin/env python3
"""Combinatorial tests for the deterministic Frobenius-window calculation."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("frobenius_window_closure", HERE / "frobenius_window_closure.py")
closure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(closure)


class FrobeniusExpectation(unittest.TestCase):
    def test_full_non_f2_universe_counts_each_unordered_orbit_pair_once(self):
        # In GF(2^3), the six non-F2 elements form two size-three orbits:
        # 6 conjugate unordered pairs out of C(6, 2) = 15 possible pairs.
        self.assertEqual(closure.random_frobenius_pair_expectation(6, 3), 6.0)

    def test_n17_window_expectation_is_not_doubled(self):
        self.assertAlmostEqual(closure.random_frobenius_pair_expectation(1022, 17), 63.689323943876886)

    def test_composite_degree_is_outside_this_uniform_orbit_formula(self):
        with self.assertRaisesRegex(ValueError, "prime field degree"):
            closure.random_frobenius_pair_expectation(10, 4)


if __name__ == "__main__":
    unittest.main()
