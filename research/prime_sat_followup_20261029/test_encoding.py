"""Software integrity only: synthetic affine equations, no scientific fixtures."""
import unittest
from encoding import CountedRing, certificate_check, controls, solve, verify_search


class Integrity(unittest.TestCase):
    def test_controls(self):
        self.assertTrue(all(controls().values()))

    def test_boolean_identity_and_tamper(self):
        self.assertTrue(certificate_check(7,[{1:1},{1:1,0:6}],[{0:1},{0:6}])[0])
        self.assertFalse(certificate_check(7,[{1:1},{1:1,0:6}],[{0:1},{0:5}])[0])
        self.assertTrue(certificate_check(7,[{1:1},{1:1,0:6}],[{1:1},{0:6}])[0])

    def test_censor_does_not_mean_unsat(self):
        result = solve(CountedRing(1,7),[{1:1}],[],1,
                       {"sat_candidates":0,"pc_calls":0,"degree":0,"rows":1})
        self.assertEqual(result["status"],"censored")

    def test_forged_exhaustion_rejected(self):
        ring = CountedRing(2,7)
        result = {"status":"complete","models":[],"learned":[]}
        with self.assertRaises(AssertionError):
            verify_search({"s":1},ring,[{1:1}],[],result,[(0,0),(0,1)])


if __name__ == "__main__":
    unittest.main()
