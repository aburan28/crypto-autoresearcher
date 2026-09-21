from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "direct_equality_pair_cross_tree.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "direct_equality_pair_cross_tree_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load cross-tree module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class DirectEqualityPairCrossTreeTests(unittest.TestCase):
    def test_all_five_leaf_trees_agree(self) -> None:
        p, a = 97, 2
        point = (3, 6)
        leaves = (point, point, point, point, point)
        expected = MODULE.fold_add(leaves, p, a)
        trees = MODULE.full_binary_trees(0, 5)
        self.assertEqual(len(trees), 14)
        self.assertEqual(len(set(map(repr, trees))), 14)
        for tree in trees:
            self.assertEqual(
                MODULE.evaluate_tree(
                    tree,
                    leaves,
                    p,
                    a,
                    MODULE.OperationCounter(),
                    {},
                ),
                expected,
            )

    def test_affine_group_edge_cases(self) -> None:
        p, a = 97, 2
        point = (3, 6)
        inverse = (3, 91)
        self.assertEqual(MODULE.add(None, point, p, a), point)
        self.assertEqual(MODULE.add(point, None, p, a), point)
        self.assertIsNone(MODULE.add(point, inverse, p, a))
        self.assertTrue(MODULE.on_curve(point, p, a, 3))
        self.assertTrue(
            MODULE.on_curve(MODULE.add(point, point, p, a), p, a, 3)
        )

    def test_residual_scaling_and_infinity(self) -> None:
        p = 97
        point = (3, 6)
        target = (80, 10)
        base = MODULE.residual_pair(
            MODULE.projective(point, 1, p),
            MODULE.projective(target, 1, p),
            p,
        )
        scaled = MODULE.residual_pair(
            MODULE.projective(point, 7, p),
            MODULE.projective(target, 11, p),
            p,
        )
        self.assertEqual(
            MODULE.canonical_pair(base, p),
            MODULE.canonical_pair(scaled, p),
        )
        self.assertEqual(
            MODULE.residual_pair(
                MODULE.projective(None, 7, p),
                MODULE.projective(None, 11, p),
                p,
            ),
            (0, 0),
        )


if __name__ == "__main__":
    unittest.main()
