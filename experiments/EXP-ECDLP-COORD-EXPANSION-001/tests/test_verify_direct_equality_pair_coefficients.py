from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_direct_equality_pair_coefficients.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_direct_equality_coefficients_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load coefficient verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyDirectEqualityPairCoefficientTests(unittest.TestCase):
    def test_cubic_normal_form_vanishes_on_curve(self) -> None:
        p, a, b = 97, 2, 3
        reduced = MODULE.cubic_normal_form(
            {(3, 0, 0): 1}, p, a, b
        )
        point = (3, 6, 1)
        ordered = MODULE.basis(3)
        vector = MODULE.vector(reduced, ordered)
        self.assertEqual(
            MODULE.evaluate(vector, ordered, point, p),
            pow(point[0], 3, p),
        )
        self.assertTrue(all(monomial[0] <= 2 for monomial in reduced))

    def test_complete_add_polynomial_evaluation(self) -> None:
        p, a, b = 97, 2, 3
        left = (80, 10)
        right = (3, 6)
        state = MODULE.complete_add_polynomials(
            MODULE.variables(),
            (right[0], right[1], 1),
            p,
            a,
            b,
        )
        ordered = MODULE.basis(2)
        output = tuple(
            MODULE.evaluate(
                MODULE.vector(poly, ordered),
                ordered,
                (left[0], left[1], 1),
                p,
            )
            for poly in state
        )
        inverse = pow(output[2], p - 2, p)
        affine = (
            output[0] * inverse % p,
            output[1] * inverse % p,
        )
        self.assertEqual(affine, MODULE.affine_add(left, right, p, a))

    def test_rank_reducer(self) -> None:
        self.assertEqual(
            MODULE.row_rank([[1, 0], [0, 1], [1, 1]], 97),
            2,
        )


if __name__ == "__main__":
    unittest.main()
