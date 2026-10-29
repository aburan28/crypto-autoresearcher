"""Software-integrity tests only: no elliptic scientific fixture is run."""
import itertools
import unittest

import coefficients as subject
import check_coefficients as checker


class IntegrityTests(unittest.TestCase):
    def test_finite_ring_matches_evaluation(self):
        ring = subject.PolynomialRing(7, finite=True)
        ordinary = checker.Arithmetic(7)
        a, b = [1, 3, 0, 2, 4, 5], [6, 0, 2, 1, 3]
        product = ring.mul(a, b)
        self.assertLessEqual(len(product), 7)
        for x in range(7):
            self.assertEqual(ordinary.evaluate(product, x),
                             ordinary.evaluate(a, x)*ordinary.evaluate(b, x) % 7)

    def test_ordinary_euclidean_bezout(self):
        ring = subject.PolynomialRing(7)
        a, b = [1, 0, 1], [3, 1]
        g, u, v = subject.egcd(a, b, ring)
        independent = checker.Arithmetic(7)
        self.assertEqual(independent.plus(independent.times(a, u), independent.times(b, v)), g)
        self.assertEqual(independent.division(a, g)[1], [0])
        self.assertEqual(independent.division(b, g)[1], [0])

    def test_explicit_corruption_and_repeated_root_controls(self):
        result = subject.instrument_controls()
        self.assertTrue(result["positive_bezout_identity"])
        self.assertTrue(result["corrupted_bezout_rejected"])
        self.assertTrue(result["negative_repeated_root_quotient_rejected"])
        self.assertTrue(result["finite_field_polynomial_reduces_to_zero"])

    def test_monic_x_reduction_over_function_ring(self):
        ring = subject.PolynomialRing(7, finite=True)
        U = [[1, 1], [0, 1], [2], [1, 2], [3], [1]]
        P = [[i % 7, (i+1) % 7] for i in range(9)]
        remainder = subject.xreduce(P, U, ring)
        for t in range(7):
            scalar = checker.Arithmetic(7)
            p = [scalar.evaluate(f, t) for f in P]
            u = [scalar.evaluate(f, t) for f in U]
            expected = scalar.division(p, u)[1]
            got = scalar.clean([scalar.evaluate(f, t) for f in remainder])
            self.assertEqual(got, expected)

    def test_field_bit_domain_is_canonical(self):
        p = 7
        width = p.bit_length()
        domain = subject.domain_clauses(p)
        for values in itertools.product(range(1 << width), repeat=4):
            literals = set(subject.value_literals(values, p))
            valid = all(any(lit in literals for lit in clause) for clause in domain)
            self.assertEqual(valid, all(v < p for v in values))

    def test_packed_leaf_certificate_coordinates(self):
        for values in ([0, 0, 0, 0], [3, 2, 6, 1], [6, 6, 6, 6]):
            self.assertEqual(checker.unpack(checker.pack(values, 7), 7), values)
        with self.assertRaises(ValueError):
            checker.unpack(7**4, 7)


if __name__ == "__main__":
    unittest.main()
