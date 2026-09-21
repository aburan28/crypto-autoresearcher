from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "elliptic_net_block_zero.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "elliptic_net_block_zero_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load block-zero module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class EllipticNetBlockZeroTests(unittest.TestCase):
    def test_berlekamp_massey_recovers_planted_recurrence(self) -> None:
        values, planted = MODULE.planted_linear_sequence(
            1009, 80, 4, "unit-test"
        )
        recovered = MODULE.berlekamp_massey(values, 1009)
        self.assertLessEqual(len(recovered) - 1, 4)
        self.assertEqual(
            MODULE.recurrence_violations(values, recovered, 1009), 0
        )
        self.assertEqual(
            MODULE.recurrence_violations(values, planted, 1009), 0
        )

    def test_train_test_rejects_random_sequence(self) -> None:
        values = MODULE.deterministic_values("random-test", 80, 1009)
        result = MODULE.train_test_recurrence(values, 1009)
        self.assertFalse(result["held_out_exact"])

    def test_elliptic_divisibility_ward_recurrence(self) -> None:
        p = 101
        a = 2
        b = 3
        point = (1, 39)
        self.assertEqual((point[1] ** 2 - point[0] ** 3 - 2 - 3) % p, 0)
        sequence = MODULE.division_polynomial_sequence(
            p, a, b, point, 30
        )
        self.assertEqual(MODULE.ward_violations(sequence, p), 0)
        self.assertTrue(MODULE.fit_somos4(sequence, p)["exact"])

    def test_tree_zero_descent(self) -> None:
        leaves = [
            [1, 2, 3, 4],
            [5, 0, 7, 8],
            [9, 10, 11, 12],
        ]
        tuples = [
            (0, 0, 0, 0),
            (0, 0, 0, 1),
            (0, 0, 1, 1),
        ]
        tree = MODULE.tree_from_leaves(leaves, 101)
        descent = MODULE.descend_zero(
            tree["levels_internal"], 1, tuples
        )
        self.assertTrue(descent["found"])
        self.assertEqual(descent["leaf_index"], 1)
        self.assertTrue(descent["leaf_zero"])

    def test_canonical_tuple_count(self) -> None:
        self.assertEqual(len(MODULE.canonical_tuples(5)), 70)


if __name__ == "__main__":
    unittest.main()
