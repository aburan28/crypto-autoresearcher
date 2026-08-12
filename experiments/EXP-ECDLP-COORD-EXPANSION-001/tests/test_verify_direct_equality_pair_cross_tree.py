from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_direct_equality_pair_cross_tree.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_direct_equality_pair_cross_tree_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load cross-tree verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyDirectEqualityPairCrossTreeTests(unittest.TestCase):
    def test_independent_tree_enumeration(self) -> None:
        shapes = MODULE.enumerate_shapes(0, 5)
        self.assertEqual(len(shapes), 14)
        self.assertEqual(len(set(map(repr, shapes))), 14)

    def test_independent_affine_addition(self) -> None:
        p, a = 97, 2
        point = (3, 6)
        self.assertEqual(MODULE.ec_sum(None, point, p, a), point)
        self.assertIsNone(MODULE.ec_sum(point, (3, 91), p, a))
        self.assertEqual(MODULE.ec_sum(point, point, p, a), (80, 10))

    def test_independent_residual_normalization(self) -> None:
        p = 97
        pair = MODULE.residual(
            MODULE.homogeneous((3, 6), 7, p),
            MODULE.homogeneous((80, 10), 11, p),
            p,
        )
        base = MODULE.residual(
            MODULE.homogeneous((3, 6), 1, p),
            MODULE.homogeneous((80, 10), 1, p),
            p,
        )
        self.assertEqual(
            MODULE.normalize_residual(pair, p),
            MODULE.normalize_residual(base, p),
        )


if __name__ == "__main__":
    unittest.main()
