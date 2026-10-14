import importlib.util
from fractions import Fraction as F
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("transport", Path(__file__).with_name("lattice_transport_denominators.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TransportTests(unittest.TestCase):
    def test_hand_derived_non_nested_orders(self):
        self.assertEqual(m.isogeny_matrix(6, 10), ((5, 0), (0, 3)))
        self.assertEqual(m.transported(-4, 6, 10), ((F(0), F(-60)), (F(3, 5), F(0))))
        self.assertEqual(m.denominator(m.transported(-4, 6, 10)), 5)
        self.assertEqual(m.denominator(m.transported(-4, 10, 6)), 3)

    def test_nonprimitive_generator_conceals_gap(self):
        self.assertEqual(m.denominator(m.transported(-4, 1, 2)), 2)
        self.assertEqual(m.denominator(m.transported(-4, 1, 2, 2)), 1)

    def test_basis_oracle_and_basis_scope(self):
        for D in m.DISCRIMINANTS:
            for P in m.TRANSFORMS.values():
                self.assertEqual(m.transported(D, 6, 10, 2, P), m.direct_action(D, 6, 10, 2, P))
            self.assertEqual(m.denominator(m.transported(D, 6, 10, P=m.TRANSFORMS["unimodular_shear"])), 5)
        self.assertNotEqual(m.denominator(m.transported(-4, 1, 3)),
                            m.denominator(m.transported(-4, 1, 3, P=m.TRANSFORMS["index_six"])))

    def test_kernel_is_checked_on_actual_members(self):
        certificate = m.kernel_preservation(m.action(-4, 6), m.isogeny_matrix(6, 10))
        self.assertFalse(certificate["preserves"])
        self.assertIsNotNone(certificate["counterexample"])
        good = m.kernel_preservation(m.action(-4, 6, 5), m.isogeny_matrix(6, 10))
        self.assertTrue(good["preserves"])
        self.assertEqual(good["members_checked"], 15)

    def test_faithful_module_division_and_partial_point_trap(self):
        A = m.action(-4, 2)
        images = m.module_zero(A, 2)["basis_images"]
        self.assertIn([0, 0], images)
        self.assertFalse(m.module_zero(A, 2)["kills_full_module"])
        self.assertTrue(m.module_zero(m.action(-4, 2, 2), 2)["kills_full_module"])

    def test_global_scaling_cannot_be_detected_from_edge_denominators(self):
        for f, g in ((6, 10), (10, 15), (6, 15)):
            self.assertEqual(m.denominator(m.transported(-7, f, g)),
                             m.denominator(m.transported(-7, 7 * f, 7 * g)))

    def test_invalid_matrix_and_module_are_rejected(self):
        with self.assertRaises(ValueError):
            m.inverse(((1, 2), (2, 4)))
        with self.assertRaises(ValueError):
            m.module_zero(((F(1, 2), 0), (0, 1)), 2)


if __name__ == "__main__":
    unittest.main()
