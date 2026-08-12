from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "export_direct_equality_pair_coefficients.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "export_direct_equality_coefficients_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load coefficient exporter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class ExportDirectEqualityPairCoefficientTests(unittest.TestCase):
    def test_coordinate_vector_shape(self) -> None:
        monomials = MODULE.DIRECT.basis(2)
        vectors = MODULE.coordinate_vectors(
            [(0,)],
            [(3, 6)],
            97,
            2,
            3,
            monomials,
        )
        self.assertEqual(len(vectors), 1)
        self.assertEqual(len(vectors[0]), 3)
        self.assertTrue(
            all(len(vector) == len(monomials) for vector in vectors[0])
        )

    def test_mutation_control_changes_digest_and_evaluation(self) -> None:
        monomials = MODULE.DIRECT.basis(2)
        vectors = MODULE.coordinate_vectors(
            [(0,)],
            [(3, 6)],
            97,
            2,
            3,
            monomials,
        )
        control = MODULE.mutation_control(
            vectors, monomials, [(80, 10)], 97
        )
        self.assertTrue(control["digest_changed"])
        self.assertTrue(control["evaluation_changed"])


if __name__ == "__main__":
    unittest.main()
