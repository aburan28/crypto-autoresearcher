"""Meaningful exact controls for the CM Hom degree experiment."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("hom_degree", Path(__file__).with_name("lattice_hom_degree.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class HomDegreeTests(unittest.TestCase):
    def test_complete_basis_matches_direct_lattice_membership(self):
        for D in m.DISCRIMINANTS:
            for f, g in ((1, 2), (6, 10), (7, 3), (12, 8)):
                u, v = m.hom_basis(f, g)
                for a in range(-12, 13):
                    for b in range(-12, 13):
                        self.assertEqual(m.preserves(D, f, g, a, b),
                                         a % u[0] == 0 and b % v[1] == 0)

    def test_hand_derived_gaussian_fixture(self):
        q = m.form(-4, 6, 10, m.TRANSFORMS["complete"])
        self.assertEqual(q, (15, 0, 60))
        self.assertEqual(m.invariants(q), (-3600, 15))
        self.assertEqual(m.pair_product(-4, q), 60)
        self.assertEqual(m.triangle((60, 90, 150)), (6, 10, 15))

    def test_uniform_scaling_is_a_false_triangle_certificate(self):
        products = [m.pair_product(-4, m.form(-4, f, g, m.TRANSFORMS["uniform_two"]))
                    for f, g in ((6, 10), (6, 15), (10, 15))]
        self.assertEqual(m.triangle(products), (12, 20, 30))
        self.assertFalse(m.complete_form_constraints(
            -4, m.form(-4, 6, 10, m.TRANSFORMS["uniform_two"]), 12, 20))

    def test_shear_preserves_form_invariants(self):
        for D in m.DISCRIMINANTS:
            self.assertEqual(m.invariants(m.form(D, 6, 10, m.TRANSFORMS["complete"])),
                             m.invariants(m.form(D, 6, 10, m.TRANSFORMS["unimodular_shear"])))

    def test_bipartite_product_graph_is_ambiguous(self):
        solutions = m.graph_assignments([(0, 1, 6), (1, 2, 12), (2, 3, 24), (3, 0, 12)], 4, 60)
        self.assertIn([2, 3, 4, 6], solutions)
        self.assertGreater(len(solutions), 1)
        self.assertEqual(m.graph_assignments([(0, 1, 60), (0, 2, 90), (1, 2, 150)], 3, 60), [[6, 10, 15]])

    def test_invalid_forms_and_products_are_rejected(self):
        with self.assertRaises(ValueError):
            m.invariants((1, 2, 1))
        with self.assertRaises(ValueError):
            m.triangle((2, 3, 4))
        with self.assertRaises(ValueError):
            m.degree(-4, 6, 10, 1, 0)


if __name__ == "__main__":
    unittest.main()
