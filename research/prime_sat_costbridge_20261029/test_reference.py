"""Fixed software integrity fixtures, not scientific or performance trials."""
import copy
import unittest

import check_reference
import reference


FIXTURES = ((5, 1, 1, [0, 1]), (7, 1, 1, [0, 1]),
            (13, 1, 1, [0, 1]), (7, 1, 0, [1, 3]))


def instance(fixture=FIXTURES[0]):
    p, a, b, target = fixture
    return {"p": p, "a": a, "b": b, "target": target[:],
            "D1": list(range(p)), "D2": list(range(p))}


def oracle(spec):
    """Tiny full-y/full-pair oracle permitted ONLY in this test module."""
    p, a, b = spec["p"], spec["a"] % spec["p"], spec["b"] % spec["p"]
    def values(domain):
        if isinstance(domain, list):
            return domain
        return [(domain["offset"] + j) % p for j in range(domain["size"])]
    left, right = set(values(spec["D1"])), set(values(spec["D2"]))
    points = [(x, y) for x in range(p) for y in range(p) if (y*y - x**3 - a*x - b) % p == 0]
    models = set()
    for x, y in points:
        if x not in left:
            continue
        for u, v in points:
            if u not in right or (x == u and (y + v) % p == 0):
                continue
            if x == u:
                slope = (3*x*x + a) * pow(2*y, p - 2, p) % p
            else:
                slope = (v - y) * pow(u - x, p - 2, p) % p
            rx = (slope*slope - x - u) % p
            ry = (slope*(x - rx) - y) % p
            if [rx, ry] == spec["target"]:
                models.add((x, u))
    return models


class ReferenceIntegrity(unittest.TestCase):
    def assert_all(self, spec):
        result = reference.solve(spec)
        checked = check_reference.verify(spec, result)
        self.assertTrue(checked["valid"], checked)
        self.assertTrue(checked["completeness_verified"])
        self.assertFalse(checked["primality_verified"])
        self.assertFalse(checked["execution_counts_verified"])
        self.assertEqual(set(map(tuple, result["projected_pairs"])), oracle(spec))
        return result

    def reject_mutation(self, mutate):
        spec = instance()
        result = reference.solve(spec)
        mutate(result)
        checked = check_reference.verify(spec, result)
        self.assertFalse(checked["valid"], checked)
        self.assertFalse(checked["completeness_verified"])

    def test_full_domains_fixed_curves(self):
        for fixture in FIXTURES:
            with self.subTest(fixture=fixture):
                self.assert_all(instance(fixture))

    def test_domain_boundaries(self):
        base = instance()
        cases = (([], base["D2"]), (base["D1"], []),
                 ({"kind": "interval", "offset": 4, "size": 3}, [4, 0, 2]),
                 ({"kind": "interval", "offset": 2, "size": 5},
                  {"kind": "interval", "offset": 4, "size": 5}),
                 ([4, 0, 2], {"kind": "interval", "offset": 3, "size": 2}),
                 ({"kind": "interval", "offset": 1, "size": 0}, []))
        for d1, d2 in cases:
            with self.subTest(D1=d1, D2=d2):
                self.assert_all(dict(base, D1=d1, D2=d2))

    def test_first_witness_and_exhaustion_never_complete(self):
        for fixture in FIXTURES:
            spec = instance(fixture)
            result = reference.solve(spec, "first")
            checked = check_reference.verify(spec, result)
            self.assertTrue(checked["valid"], checked)
            self.assertTrue(checked["witness_verified"])
            self.assertFalse(checked["completeness_verified"])
            self.assertEqual(len(result["projected_pairs"]), 1)
            self.assertLessEqual(set(map(tuple, result["projected_pairs"])), oracle(spec))
        for d1, d2 in (([], [0]), ([0], [])):
            spec = dict(instance(), D1=d1, D2=d2)
            result = reference.solve(spec, "first")
            checked = check_reference.verify(spec, result)
            self.assertTrue(checked["valid"], checked)
            self.assertFalse(checked["completeness_verified"])
            self.assertFalse(checked["witness_verified"])

    def test_zero_ordinate_lift_and_exceptional_x(self):
        spec = instance(FIXTURES[3])
        result = self.assert_all(spec)
        self.assertIn({"x": 0, "kind": "zero", "roots": [0]}, result["lift_records"])
        self.assertTrue(any(pair[0] == spec["target"][0] for pair in result["projected_pairs"]))

    def test_supplied_nonresidue_and_coefficient_normalization(self):
        spec = dict(instance(), nonresidue=2, a=6, b=-4)
        result = self.assert_all(spec)
        self.assertEqual(result["setup"]["method"], "supplied")

    def test_missing_lift_record(self):
        self.reject_mutation(lambda r: r["lift_records"].pop())

    def test_duplicate_lift_record(self):
        def mutate(r):
            r["lift_records"][1] = copy.deepcopy(r["lift_records"][0])
        self.reject_mutation(mutate)

    def test_missing_exceptional_root(self):
        def mutate(r):
            i = next(i for i, pair in enumerate(r["projected_pairs"]) if pair[0] == 0)
            r["projected_pairs"].pop(i)
            r["witnesses"].pop(i)
        self.reject_mutation(mutate)

    def test_missing_sign(self):
        def mutate(r):
            next(row for row in r["lift_records"] if row["kind"] == "square")["roots"].pop()
        self.reject_mutation(mutate)

    def test_false_global_nonsquare(self):
        self.reject_mutation(lambda r: r["setup"].update(nonresidue=1))

    def test_zero_twisted_root(self):
        def mutate(r):
            next(row for row in r["lift_records"] if row["kind"] == "nonsquare")["twisted_root"] = 0
        self.reject_mutation(mutate)

    def test_corrupted_nonzero_twisted_root(self):
        def mutate(r):
            row = next(row for row in r["lift_records"] if row["kind"] == "nonsquare")
            row["twisted_root"] = next(w for w in range(1, 5) if w*w % 5 != row["twisted_root"]**2 % 5)
        self.reject_mutation(mutate)

    def test_wrong_witness_sum(self):
        def mutate(r):
            x, y = r["witnesses"][0]["P"]
            r["witnesses"][0]["Q"] = [x, (-y) % 5]
        self.reject_mutation(mutate)

    def test_first_false_completeness(self):
        spec = instance()
        result = reference.solve(spec, "first")
        result["complete"] = True
        self.assertFalse(check_reference.verify(spec, result)["valid"])

    def test_false_first_exhaustion(self):
        spec = instance()
        result = reference.solve(spec, "first")
        result["projected_pairs"], result["witnesses"] = [], []
        self.assertFalse(check_reference.verify(spec, result)["valid"])

    def test_duplicate_projected_output(self):
        def mutate(r):
            r["projected_pairs"].append(r["projected_pairs"][0])
            r["witnesses"].append(r["witnesses"][0])
        self.reject_mutation(mutate)

    def test_wrong_input_digest(self):
        self.reject_mutation(lambda r: r.update(input_sha256="0" * 64))

    def test_invalid_instances(self):
        base = instance()
        bad_specs = [dict(base, D1=[0, 0]), dict(base, D2=[1, 1]), dict(base, D1=[False]),
                     dict(base, nonresidue=1), dict(base, nonresidue=None),
                     dict(base, D1={"kind": "interval", "offset": 0, "size": 6}),
                     dict(base, D2={"kind": "interval", "offset": 5, "size": 0}),
                     dict(base, a=0, b=0), dict(base, target=[0, 2]),
                     dict(instance(FIXTURES[3]), target=[0, 0])]
        valid_result = reference.solve(base)
        for spec in bad_specs:
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError):
                    reference.solve(spec)
                self.assertFalse(check_reference.verify(spec, valid_result)["valid"])


if __name__ == "__main__":
    unittest.main()
