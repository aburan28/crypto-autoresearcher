"""Independent witness and deterministic recipe checks for prime fixtures."""

import unittest

from tools.icperf_prime_fixture import curve_parameters, verify_prime_order_witness


class PrimeFixtureTests(unittest.TestCase):
    def test_known_prime_order_curve(self):
        # Exhaustive small-field census: #E(F_101) = 83 for y^2=x^3+6x+9.
        # The verifier receives only the proposed order and one witness.
        verify_prime_order_witness(101, 6, 9, 83, (0, 3))

    def test_certificate_rejects_wrong_order_and_point(self):
        with self.assertRaisesRegex(ValueError, "annihilate"):
            verify_prime_order_witness(101, 6, 9, 89, (0, 3))
        with self.assertRaisesRegex(ValueError, "not on the curve"):
            verify_prime_order_witness(101, 6, 9, 83, (0, 4))
        with self.assertRaisesRegex(ValueError, "not an admitted prime"):
            verify_prime_order_witness(101, 6, 9, 82, (0, 3))

    def test_hasse_and_canonical_coordinate_guards(self):
        with self.assertRaisesRegex(ValueError, "Hasse"):
            verify_prime_order_witness(101, 6, 9, 127, (0, 3))
        with self.assertRaisesRegex(ValueError, "canonical"):
            verify_prime_order_witness(101, 6, 9, 83, (101, 3))

    def test_recipe_is_deterministic_and_in_requested_field_range(self):
        for bits in (50, 53, 63):
            first = curve_parameters(bits, 20261017, 0)
            self.assertEqual(first, curve_parameters(bits, 20261017, 0))
            self.assertEqual(first[0], curve_parameters(bits, 20261017, 1)[0])
            self.assertEqual(first[0].bit_length(), bits)
            self.assertNotEqual(first[1:], curve_parameters(bits, 20261017, 1)[1:])


if __name__ == "__main__":
    unittest.main()
