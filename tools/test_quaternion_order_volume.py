import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("quaternion", Path(__file__).with_name("quaternion_order_volume.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class QuaternionVolumeTests(unittest.TestCase):
    def test_hamilton_products_and_norm(self):
        self.assertEqual(m.multiply(m.I, m.J), m.K)
        self.assertEqual(m.multiply(m.J, m.I), m.scale(-1, m.K))
        self.assertEqual(m.multiply(m.H, m.H), m.subtract(m.H, m.ONE))
        self.assertEqual(m.norm(m.H), 1)

    def test_hurwitz_and_lipschitz_are_distinct_orders(self):
        full = m.lattice_certificate((m.ONE, m.I, m.J, m.H))
        proper = m.lattice_certificate((m.ONE, m.I, m.J, m.K))
        self.assertEqual((full["index_in_hurwitz"], full["gram_determinant"]), (1, "4"))
        self.assertEqual((proper["index_in_hurwitz"], proper["gram_determinant"]), (2, "16"))
        self.assertTrue(full["unital_order"])
        self.assertTrue(proper["unital_order"])

    def test_equal_volume_does_not_certify_multiplication(self):
        bad = m.lattice_certificate((m.ONE, m.I, m.J, m.scale(2, m.K)))
        good = m.lattice_certificate((m.ONE, m.I, m.add(m.J, m.K), m.subtract(m.J, m.K)))
        self.assertEqual(bad["gram_determinant"], "64")
        self.assertEqual(bad["gram_determinant"], good["gram_determinant"])
        self.assertFalse(bad["unital_order"])
        self.assertTrue(good["unital_order"])
        self.assertIsNotNone(bad["closure_counterexample"])

    def test_noncommutation_does_not_certify_maximality(self):
        ij = m.pair_certificate(m.I, m.J)
        ih = m.pair_certificate(m.I, m.H)
        self.assertFalse(ij["commutes"])
        self.assertEqual(ij["index_in_hurwitz"], 2)
        self.assertEqual(ih["index_in_hurwitz"], 1)
        self.assertEqual(ij["commutator_norm"], 4)
        self.assertEqual(ih["commutator_norm"], 2)

    def test_rank_deficiency_and_missing_unit_are_not_orders(self):
        missing = m.lattice_certificate((m.ONE, m.I, m.scale(2, m.I), m.scale(3, m.I)))
        self.assertEqual(missing["rank"], 2)
        self.assertIsNone(missing["index_in_hurwitz"])
        ideal = m.lattice_certificate(tuple(m.scale(2, x) for x in (m.ONE, m.I, m.J, m.H)))
        self.assertTrue(ideal["multiplicatively_closed"])
        self.assertFalse(ideal["unital_order"])

    def test_outside_order_coordinates_are_rejected(self):
        with self.assertRaises(ValueError):
            m.hurwitz((0, 0, 0, m.F(1, 2)))


if __name__ == "__main__":
    unittest.main()
