"""Point-lift regression for the binary-curve zero-x branch."""

import unittest

from gf2 import Curve, make_field


class ZeroXLiftTest(unittest.TestCase):
    def test_default_archived_curve(self):
        field = make_field(17)
        self.assertEqual(Curve(field).lift_x(0), (0, 1))

    def test_nonunit_b_satisfies_curve_equation(self):
        field = make_field(17)
        for b in (2, 3, 5, field.q - 1):
            curve = Curve(field, B=b)
            point = curve.lift_x(0)
            self.assertEqual(point[0], 0)
            self.assertEqual(field.sqr(point[1]), b)
            self.assertIsNone(curve.add(point, point))


if __name__ == "__main__":
    unittest.main()
