"""Exact deterministic engineering fixtures; no research-grid execution."""
import unittest
from sage.all import EllipticCurve, GF, PolynomialRing
from section_encoding import check_section, coefficient_system, fixture_assignment, specialize


class SectionEncodingFixtures(unittest.TestCase):
    def setUp(self):
        self.p = 31
        self.ring = PolynomialRing(GF(self.p), "t")
        self.t = t = self.ring.gen()
        self.a, self.b = t, t**2 - t - 1
        # P=(1,t). Double with the independent Sage group law below.
        self.z = t
        self.x = (t + 3)**2 / 4 - 2 * t**2
        self.y = -t**4 + (t + 3) * (t**2 - self.x) / 2

    def test_denominator_fixture_matches_independent_group_law(self):
        field = self.ring.fraction_field()
        curve = EllipticCurve(field, [self.a, self.b])
        doubled = 2 * curve([1, self.t])
        self.assertEqual(doubled[0], self.x / self.z**2)
        self.assertEqual(doubled[1], self.y / self.z**3)
        self.assertEqual(specialize(31, self.a, self.b, 1, 1, self.x, self.y, self.z, 0), "O")

    def test_coefficients_include_nontrivial_section_through_O(self):
        system = coefficient_system(31, self.a, self.b, 1, 1, 1, 0, "O")
        values = fixture_assignment(system, self.x, self.y, self.z, 0)
        self.assertTrue(system.accepts(values))
        values["x0"] += 1
        self.assertFalse(system.accepts(values))

    def test_affine_target_and_denominator_saturation(self):
        target = specialize(31, self.a, self.b, 1, 1, self.x, self.y, self.z, 2)
        system = coefficient_system(31, self.a, self.b, 1, 1, 1, 2, target)
        values = fixture_assignment(system, self.x, self.y, self.z, 2)
        self.assertTrue(system.accepts(values))
        values["target_unit"] = 0
        self.assertFalse(system.accepts(values))

    def test_base_inversion_includes_O_at_infinity(self):
        t = self.t
        reverse = lambda poly, degree: self.ring(list(reversed([poly[i] for i in range(degree + 1)])))
        a, b = reverse(self.a, 4), reverse(self.b, 6)
        x, y, z = reverse(self.x, 4), reverse(self.y, 6), reverse(self.z, 1)
        self.assertEqual(z, 1)
        self.assertEqual(specialize(31, a, b, 1, 1, x, y, z, "infinity"), "O")
        system = coefficient_system(31, a, b, 1, 1, 0, "infinity", "O")
        self.assertTrue(system.accepts(fixture_assignment(system, x, y, z, "infinity")))
        with self.assertRaises(ValueError):
            coefficient_system(31, a, b, 1, 1, 1, "infinity", "O")

    def test_polynomial_section_and_weighted_constant_normalization(self):
        x, y, z = self.ring(1), self.t, self.ring(1)
        self.assertEqual(check_section(31, self.a, self.b, 1, 0, 4*x, 8*y, 2*z), (x, y, z))
        system = coefficient_system(31, self.a, self.b, 1, 0, 0, 2, (1, 2))
        self.assertTrue(system.accepts(fixture_assignment(system, x, y, z, 2)))

    def test_reject_common_factor_and_fake_projective_degree(self):
        t = self.t
        with self.assertRaisesRegex(ValueError, "Nonprimitive finite"):
            check_section(31, self.a, self.b, 1, 2, self.x*t**2, self.y*t**3, self.z*t)
        with self.assertRaisesRegex(ValueError, "infinity"):
            check_section(31, self.a, self.b, 1, 1, self.ring(1), t, self.ring(1))

    def test_bad_fibre_and_off_curve_target_refused(self):
        with self.assertRaisesRegex(ValueError, "not smooth"):
            coefficient_system(31, self.a, self.b, 1, 1, 1, 1, "O")
        with self.assertRaisesRegex(ValueError, "not on"):
            coefficient_system(31, self.a, self.b, 1, 1, 1, 0, (0, 0))

    def test_nonprime_and_singular_generic_model_refused(self):
        with self.assertRaisesRegex(ValueError, "prime"):
            coefficient_system(32, [1], [1], 1, 0, 0, 0, "O")
        with self.assertRaisesRegex(ValueError, "generic fibre"):
            coefficient_system(31, [0], [0], 1, 0, 0, 0, "O")


if __name__ == "__main__":
    unittest.main(verbosity=2)
