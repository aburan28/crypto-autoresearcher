"""Small, independent curve-arithmetic checks for the affine S4 generator.

Run with Sage's Python, for example `sage -sh -c 'python tests/...py'`.
These checks do not authorize Stage 2 of EXP-ICPERF-42ef30: AP-2 requires
byte identity on all shipped fixtures in addition to mathematical validity.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from sage.all import EllipticCurve, GF

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from affine_weil_descent import build_instance, canonical_anf  # noqa: E402


def evaluate_anf(anf: str, symmetric_count: int, bits: list[int]):
    _, equations = canonical_anf(anf, symmetric_count)
    values = []
    for identifier, terms in equations:
        value = bits[identifier - 1] if identifier is not None else 0
        for term in terms:
            value ^= int(all(bits[index - 1] for index in term))
        values.append(value)
    return values


class AffineWeilDescentTests(unittest.TestCase):
    def test_planted_nonmonomial_affine_slice(self):
        n = 7
        basis = [3, 5, 33]
        offset = 2
        field = GF(2**n, name="a")
        curve = EllipticCurve(field, [1, 1, 0, 0, 1])
        masks = [0, 2, 3]
        x_values = [offset ^ (basis[1] if mask & 2 else 0)
                    ^ (basis[0] if mask & 1 else 0) for mask in masks]
        points = [curve.lift_x(field.from_integer(x), all=True)[0] for x in x_values]
        target = int(sum(points, curve(0))[0].to_integer())
        _, anf, metadata = build_instance(n, basis, offset, target)

        x_bits = []
        for mask in masks:
            x_bits.extend((mask >> j) & 1 for j in range(len(basis)))
        x1, x2, x3 = [field.from_integer(x) for x in x_values]
        symmetric = [x1 + x2 + x3, x1 * x2 + x1 * x3 + x2 * x3, x1 * x2 * x3]
        e_bits = []
        for value, width in zip(symmetric, metadata["symmetric_widths"]):
            encoded = int(value.to_integer())
            self.assertLess(encoded, 1 << width)
            e_bits.extend((encoded >> j) & 1 for j in range(width))
        bits = x_bits + e_bits
        self.assertEqual(evaluate_anf(anf, sum(metadata["symmetric_widths"]), bits),
                         [0] * (sum(metadata["symmetric_widths"]) + n))

        _, wrong_anf, _ = build_instance(n, basis, offset, target ^ 1)
        self.assertTrue(any(evaluate_anf(wrong_anf, sum(metadata["symmetric_widths"]), bits)))

    def test_dependent_basis_rejected(self):
        with self.assertRaisesRegex(ValueError, "linearly dependent"):
            build_instance(7, [1, 2, 3], 0, 1)


if __name__ == "__main__":
    unittest.main()
