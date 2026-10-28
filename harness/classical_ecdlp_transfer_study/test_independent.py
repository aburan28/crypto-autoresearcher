"""Synthetic software regressions only; no scientific cohort or candidate run."""
import ast
from pathlib import Path
import unittest

from independent import Group, Primitive, answer, interval_candidate, point, prime64


MODEL = {"p": 11, "a": 1, "b": 6, "r": 13}
BASE = (2, 7)
MULTIPLES = [None, (2, 7), (5, 2), (8, 3), (10, 2), (3, 6), (7, 9),
             (7, 2), (3, 5), (10, 9), (8, 8), (5, 9), (2, 4)]


class IndependentArithmeticTests(unittest.TestCase):
    def test_known_group_vectors_and_domain_rejections(self):
        group = Group(MODEL)
        self.assertTrue(group.certify_base(BASE)["ordinary"])
        self.assertEqual(group.orbit(BASE), MULTIPLES)
        for scalar, expected in enumerate(MULTIPLES):
            self.assertEqual(group.mul(scalar, BASE), expected)
            self.assertEqual(group.mul(scalar-13, BASE), expected)
        self.assertIsNone(group.add(BASE, group.neg(BASE)))
        for model in (dict(MODEL, p=15), dict(MODEL, r=11), dict(MODEL, a=0, b=0)):
            with self.assertRaises(ValueError):
                Group(model)
        with self.assertRaises(ValueError):
            group.certify_base((0, 0))
        with self.assertRaises(ValueError):
            point([True, 1], 11)
        with self.assertRaises(ValueError):
            point([13, 1], 11)

    def test_deterministic_primality_boundary_and_pseudoprimes(self):
        for n in (2, 3, 11, 13, 2147483647, 18446744073709551557):
            self.assertTrue(prime64(n))
        for n in (True, -1, 0, 1, 4, 341, 561, 3215031751, 3825123056546413051, 2**64):
            self.assertFalse(prime64(n))

    def test_independent_addition_chain_against_full_slope_sum_and_cocycle(self):
        group = Group(MODEL)
        summed, chained = Primitive(group, BASE, "slope_sum"), Primitive(group, BASE, "addition_chain")
        cumulative = Primitive(group, BASE, "orbit_coefficient")
        self.assertEqual(summed.z(BASE), 3)
        self.assertEqual(summed.z((8, 3)), 8)
        for left in MULTIPLES:
            self.assertEqual(summed.z(left), chained.z(left))
            self.assertEqual(summed.z(left), cumulative.z(left))
            self.assertEqual(summed.z(group.neg(left)), -summed.z(left) % 11)
            for right in MULTIPLES:
                self.assertEqual(summed.z(group.add(left, right)),
                                 (summed.z(left)+summed.z(right)+group.slope(left, right)) % 11)

    def test_single_hand_derived_predicate_values_and_undefined_semantics(self):
        primitive = Primitive(Group(MODEL), BASE)
        anchored = answer(primitive, BASE, BASE, 1, -4)
        self.assertEqual((anchored["anchor"], anchored["normalized"], anchored["bit"]), (6, 1, 0))
        self.assertEqual(answer(primitive, BASE, None, 1, -4)["bit"], 0)
        # Existing hand-derived negative regression, not a new fixed-circuit screen.
        zero = answer(primitive, BASE, (5, 2), 2, 0)
        self.assertEqual((zero["status"], zero["reason"], zero["g"]),
                         ("UNDEFINED", "ZERO_NUMERATOR", 0))
        invalid = answer(primitive, BASE, None, -1, 1)
        self.assertEqual((invalid["status"], invalid["reason"]), ("UNDEFINED", "ZERO_ANCHOR"))

    def test_interval_correct_for_every_synthetic_truth_and_empty_intervals(self):
        r, length = 13, 5
        for scalar in range(r):
            digits = [int((scalar*(1 << j) % r) > (r-1)//2) for j in range(length)]
            result = interval_candidate(r, digits)
            self.assertTrue(result["nonempty"])
            self.assertEqual(result["candidate"], scalar)
        self.assertFalse(interval_candidate(r, [0, 0, 0, 0, 1])["nonempty"])
        all_ones = interval_candidate(r, [1]*length)
        self.assertEqual(all_ones["candidate"], r)
        self.assertFalse(all_ones["nonempty"])
        with self.assertRaises(ValueError):
            interval_candidate(r, [True])

    def test_production_import_boundary(self):
        root = Path(__file__).parent
        # The staged verifier can share a directory with producer and transport
        # modules. Independence applies to this verifier's own import closure.
        for name in ("verify.py", "independent.py"):
            path = root/name
            if name == "independent.py" and not path.exists():
                continue  # Development facade is not in the production bundle.
            tree = ast.parse(path.read_text())
            imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
            imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
            self.assertFalse(set(imports) & {"curve", "constructor", "compute", "transfer", "baseline"})


if __name__ == "__main__":
    unittest.main()
