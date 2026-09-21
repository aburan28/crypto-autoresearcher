from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "direct_equality_pair.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "direct_equality_pair_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load equality-pair module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class DirectEqualityPairTests(unittest.TestCase):
    def test_projective_pair_scale_invariance(self) -> None:
        self.assertEqual(
            MODULE.canonical_pair(7, 19, 101),
            MODULE.canonical_pair(7 * 23, 19 * 23, 101),
        )
        self.assertEqual(MODULE.canonical_pair(0, 0, 101), (0, 0))

    def test_residual_pair_zero(self) -> None:
        self.assertEqual(
            MODULE.residual_pair((3, 6, 1), (3, 6), 101),
            (0, 0),
        )
        self.assertNotEqual(
            MODULE.residual_pair((3, 6, 1), (1, 39), 101),
            (0, 0),
        )

    def test_dimensions(self) -> None:
        self.assertEqual(len(MODULE.DIRECT.basis(8)), 24)
        self.assertEqual(len(MODULE.DIRECT.basis(4)), 12)

    def test_symbolic_coordinate_degree(self) -> None:
        state = MODULE.derive_suffix_coordinates(
            [(3, 6)], 101, 2, 3
        )
        self.assertEqual(
            [MODULE.DIRECT.polynomial_degree(poly) for poly in state],
            [2, 2, 2],
        )


if __name__ == "__main__":
    unittest.main()
