"""Exact subgroup and Dickson-base controls with a supplied field divisor."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.factor_base import (
    FactorBase,
    dickson_value,
)
from tools.icperf_explicit_base import verify_base_record


class ExplicitDivisorBaseTests(unittest.TestCase):
    def setUp(self):
        self.curve = Curve(101, 6, 9, 83)

    def test_subgroup_coset_has_exact_order_and_membership(self):
        base = FactorBase.subgroup(self.curve, 10, seed=7, divisor=20)
        g, zeta = base.params["coset"], base.params["zeta"]
        orbit = {g * pow(zeta, j, 101) % 101 for j in range(20)}
        self.assertEqual(len(orbit), 20)
        self.assertEqual(pow(zeta, 20, 101), 1)
        self.assertNotEqual(pow(zeta, 10, 101), 1)
        self.assertNotEqual(pow(zeta, 4, 101), 1)
        self.assertEqual({point[0] for point in base.points},
                         {x for x in orbit if self.curve.lift_x(x) is not None})
        self.assertEqual(base.membership_poly(), {20: 1, 0: -pow(g, 20, 101) % 101})

    def test_dickson_values_and_distinct_preimages(self):
        base = FactorBase.dickson(self.curve, 10, seed=11, divisor=20)
        p = self.curve.p
        g, zeta, c = (base.params[name] for name in ("coset", "zeta", "c"))
        us = [g * pow(zeta, j, p) % p for j in range(20)]
        xs = [(u + c * pow(u, -1, p)) % p for u in us]
        self.assertEqual(len(set(xs)), 20)
        self.assertEqual({point[0] for point in base.points},
                         {x for x in xs if self.curve.lift_x(x) is not None})
        self.assertTrue(all(dickson_value(x, c, 20, p) == base.params["lambda"]
                            for x in xs))

    def test_explicit_path_does_not_factor_p_minus_one(self):
        with patch("crypto_autoresearcher.index_calculus.factor_base._base_divisor",
                   side_effect=AssertionError("factored p-1")), patch(
                       "crypto_autoresearcher.index_calculus.factor_base.primitive_root",
                       side_effect=AssertionError("searched primitive root")):
            self.assertTrue(FactorBase.subgroup(self.curve, 10, divisor=20).points)
            self.assertTrue(FactorBase.dickson(self.curve, 10, divisor=20).points)

    def test_invalid_divisor_refused(self):
        for d in (0, 7, 101):
            with self.subTest(d=d), self.assertRaises(ValueError):
                FactorBase.subgroup(self.curve, 10, divisor=d)
        with self.assertRaisesRegex(ValueError, "divisor_multiple_of"):
            FactorBase.subgroup(self.curve, 10, divisor=20, divisor_multiple_of=3)

    def test_wide_public_fixture(self):
        path = (Path(__file__).resolve().parents[1] /
                "research/icperf_prime_fixtures_20261017/n63_seed20261017.json")
        fixture = json.loads(path.read_text())["curve"]
        curve = Curve(fixture["p"], fixture["a"], fixture["b"], fixture["order"])
        base = FactorBase.subgroup(curve, 406, seed=20261017, divisor=788)
        self.assertEqual(base.params["d"], 788)
        self.assertEqual(base.params["divisor_source"], "explicit")
        self.assertEqual(len({point[0] for point in base.points}), len(base.points))
        self.assertTrue(all(curve.is_on_curve(point) for point in base.points))
        self.assertTrue(all(pow(point[0], 788, curve.p) ==
                            pow(base.params["coset"], 788, curve.p)
                            for point in base.points))

    def test_archived_base_rejects_a_changed_point(self):
        root = Path(__file__).resolve().parents[1]
        fixture = root / "research/icperf_prime_fixtures_20261017/n63_seed20261017.json"
        path = root / "research/icperf_explicit_divisor_20261017/n63_m8_subgroup_seed20261017.json"
        record = json.loads(path.read_text())
        verify_base_record(record, fixture)
        record["points"][0][1] += 1
        with self.assertRaisesRegex(ValueError, "complete coset enumeration"):
            verify_base_record(record, fixture)


if __name__ == "__main__":
    unittest.main()
