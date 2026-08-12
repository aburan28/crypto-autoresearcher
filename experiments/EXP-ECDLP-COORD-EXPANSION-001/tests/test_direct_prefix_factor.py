from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "direct_prefix_factor.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "direct_prefix_factor_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load direct-prefix module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class DirectPrefixFactorTests(unittest.TestCase):
    def test_basis_dimension(self) -> None:
        self.assertEqual(len(MODULE.basis(16)), 48)
        self.assertEqual(len(MODULE.basis(8)), 24)

    def test_cubic_reduction(self) -> None:
        p, a, b = 101, 2, 3
        reduced = MODULE.reduce_poly({(3, 0, 0): 1}, p, a, b)
        expected = {
            (0, 2, 1): 1,
            (1, 0, 2): -a % p,
            (0, 0, 3): -b % p,
        }
        self.assertEqual(reduced, expected)

    def test_algebra_controls(self) -> None:
        controls = MODULE.algebra_controls()
        self.assertTrue(controls["cubic_reduces_to_zero"])
        self.assertTrue(controls["symbolic_rcb_matches_numeric"])
        self.assertEqual(controls["symbolic_rcb_degrees"], [2, 2, 2])

    def test_target_component_identity(self) -> None:
        p, a, b, nu = 101, 2, 3, 2
        output = MODULE.variables()
        components = MODULE.locator_components(
            output, p, a, b, nu
        )
        target = (1, 39)
        combined = MODULE.combine_components(
            components,
            MODULE.target_weights(target, p, nu),
            p,
        )
        value = MODULE.evaluate_polynomial(combined, (3, 6, 1), p)
        exact = MODULE.NORM.locator_tensors(
            {
                "outputs_internal": [(3, 6, 1)],
                "affine_sums_internal": [(3, 6)],
            },
            target,
            p,
            nu,
            [1],
        )["tensors_internal"]["h^1"][0]
        self.assertEqual(value, exact)


if __name__ == "__main__":
    unittest.main()
