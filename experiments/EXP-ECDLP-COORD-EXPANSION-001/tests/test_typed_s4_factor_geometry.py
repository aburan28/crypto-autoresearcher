from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "typed_s4_factor_geometry.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "typed_s4_factor_geometry_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load factor-geometry module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class TypedS4FactorGeometryTests(unittest.TestCase):
    def test_rank_factor_reconstructs(self) -> None:
        p = 101
        shape = [3, 4]
        values = [
            (row + 1) * (column + 2) % p
            for row in range(3)
            for column in range(4)
        ]
        factor = MODULE.rank_factor(values, shape, 1, p)
        self.assertEqual(factor["summary"]["rank"], 1)
        self.assertEqual(
            factor["summary"]["reconstruction_mismatches"], 0
        )
        self.assertEqual(factor["summary"]["zero_set_mismatches"], 0)

    def test_projective_canonicalization(self) -> None:
        self.assertEqual(
            MODULE.canonical_projective([2, 4, 0], 101),
            MODULE.canonical_projective([3, 6, 0], 101),
        )
        self.assertNotEqual(
            MODULE.canonical_projective([2, 4, 0], 101),
            MODULE.canonical_projective([2, 5, 0], 101),
        )

    def test_affine_rank(self) -> None:
        vectors = [[1, 2], [2, 3], [3, 4]]
        self.assertEqual(MODULE.affine_rank(vectors, 101), 1)

    def test_source_orbit_count(self) -> None:
        shape = [7, 5, 5, 5, 5]
        self.assertEqual(MODULE.source_orbit_count(shape, 2), 35)
        self.assertEqual(MODULE.source_orbit_count(shape, 3), 105)

    def test_incidence_s4_quotient(self) -> None:
        shape = [2, 2, 2, 2, 2]
        values = [1] * MODULE.math.prod(shape)
        for indices in (
            (0, 0, 0, 1, 1),
            (0, 0, 1, 0, 1),
            (0, 1, 0, 0, 1),
        ):
            values[MODULE.NORM.flat_index(indices, shape)] = 0
        record = MODULE.incidence_geometry(values, shape, 2)
        self.assertEqual(record["ordered_zero_pairs"], 3)
        self.assertEqual(record["canonical_s4_witnesses"], 1)

    def test_dense_control_has_matched_rank(self) -> None:
        control = MODULE.dense_control(
            "test", 8, 9, 4, 101, 2
        )
        self.assertTrue(control["all_rank_matched"])
        self.assertTrue(control["all_geometry_generic"])


if __name__ == "__main__":
    unittest.main()
