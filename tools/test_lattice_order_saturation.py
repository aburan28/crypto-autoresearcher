import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("saturation", Path(__file__).with_name("lattice_order_saturation.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SaturationTests(unittest.TestCase):
    def test_bezout_primitive_generator_certificate(self):
        g, coefficients = m.bezout([6, 10, 15])
        self.assertEqual(g, 1)
        self.assertEqual(sum(x * y for x, y in zip(coefficients, [6, 10, 15])), 1)
        self.assertEqual(m.bezout([6, 10])[0], 2)

    def test_full_rank_does_not_mean_full_ring(self):
        self.assertEqual(m.disc_from_trace(-4, 1, 6), -144)
        self.assertEqual(m.disc_from_trace(-4, 1, 1), -4)
        self.assertEqual(m.select(-4, 1, [(0, 6)], "shortest_norm")["final_order_index"], 6)

    def test_actual_lattice_and_wrong_maximal_order_module_differ(self):
        self.assertFalse(m.division_control(-4, 6, (0, 1), 2)["kills_full_module"])
        self.assertTrue(m.division_control(-4, 1, (0, 6), 2)["kills_full_module"])

    def test_one_annihilated_torsion_generator_is_insufficient(self):
        control = m.division_control(-4, 2, (0, 1), 2)
        self.assertIn([0, 0], control["basis_images"])
        self.assertFalse(control["division_integral_on_actual_lattice"])

    def test_saturation_and_policy_controls(self):
        for D in m.DISCRIMINANTS:
            for f in m.CONDUCTORS:
                self.assertEqual(m.saturate(D, f)["final_index"], 1)
                baseline = m.select(D, f, m.GENERATORS, "shortest_norm")
                index = m.select(D, f, m.GENERATORS, "smallest_index")
                self.assertEqual(baseline["final_order_index"], 1)
                self.assertEqual(index["final_order_index"], 1)
                self.assertEqual(index["selected_generators"], 3)
                self.assertGreater(baseline["selected_generators"], 3)
                self.assertGreater(index["gcd_score_evaluations"], 3)

    def test_quadratic_multiplication_hand_fixture(self):
        self.assertEqual(m.multiply(-4, 3, (0, 2), (0, 5)), (-90, 0))
        self.assertEqual(m.multiply(-3, 2, (0, 1), (0, 1)), (-4, 2))

    def test_invalid_rank_one_discriminant_is_not_fabricated(self):
        with self.assertRaises(ValueError):
            m.disc_from_trace(-4, 1, 0)


if __name__ == "__main__":
    unittest.main()
