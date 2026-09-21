#!/usr/bin/env python3
"""Sixteen synthetic contract tests; no curve, pairing, fixture, or timing run."""
import unittest
from pathlib import Path

import driver


class SyntheticContractTests(unittest.TestCase):
    params = (17, 1, 2, 19, 6, 0, 0)
    def test_01_canonical_json(self): self.assertEqual(driver.canonical_json([1, 2]), b"[1,2]")
    def test_02_stream_deterministic(self): self.assertEqual(driver.stream_digest(purpose="query", parameters=self.params, seed=1, counter=0), driver.stream_digest(purpose="query", parameters=self.params, seed=1, counter=0))
    def test_03_rejection_n_one_consumes(self): self.assertEqual(driver.rejection_draw(purpose="query", parameters=self.params, seed=1, counter=0, n=1)[1], 1)
    def test_04_shuffle_deterministic(self): self.assertEqual(driver.fisher_yates([1,2,3], parameters=self.params, seed=2, counter=0), driver.fisher_yates([1,2,3], parameters=self.params, seed=2, counter=0))
    def test_05_coeff_order(self): self.assertEqual(driver.polynomial_coefficients(1 + 2*5 + 3*25, p=5, k=3), (1,2,3))
    def test_06_poly_skips_zero_constant(self): self.assertEqual(next(driver.bounded_monic_polynomials(p=3,k=2))[0], 1)
    def test_07_poly_cap(self): self.assertEqual(len(list(driver.bounded_monic_polynomials(p=5,k=2,cap=3))), 3)
    def test_08_poly_select_mock(self): self.assertEqual(driver.select_irreducible_polynomial(p=3,k=2,is_irreducible=lambda c:c==(2,0),cap=3)[0], 2)
    def test_09_tate_final_exponent(self): self.assertEqual(driver.reduced_tate(miller_value=2,p=7,k=1,r=3,power=lambda a,n:pow(a,n,7)), (4,2))
    def test_10_bsgs_multiplicative(self): self.assertEqual(driver.multiplicative_bsgs(base=2,target=13,order=11,one=1,multiply=lambda a,b:a*b%23,inverse=lambda a:pow(a,-1,23),power=lambda a,n:pow(a,n,23),verify=lambda x:pow(2,x,23)==13), 7)
    def test_11_bsgs_additive(self): self.assertEqual(driver.additive_bsgs(base=1,target=7,order=11,identity=0,add=lambda a,b:(a+b)%11,negate=lambda a:-a%11,scalar_mul=lambda n,a:n*a%11,verify=lambda x:x%11==7), 7)
    def test_12_isolated_target(self):
        target=driver.PublicTarget(1,7); self.assertFalse(hasattr(target,"label")); self.assertEqual(driver.evaluator_decode(target,G=1,r=11,identity=0,add=lambda a,b:(a+b)%11,negate=lambda a:-a%11,scalar_mul=lambda n,a:n*a%11),7)
    def test_13_t_candidate_logs_exception(self):
        with self.assertRaises(driver.SearchExhausted): driver.select_second_argument(candidates=[0],evaluate=lambda _:(_ for _ in ()).throw(ZeroDivisionError()),power=lambda a,n:a,one=1,r=3,cap=1)
    def test_14_cost_keeps_setup(self): self.assertGreater(driver.CostLedger(1,2,3,4,5,6,7,8,9,10).character_total(1), driver.CostLedger(1,2,3,4,5,6,7,8,9,10).curve_total(1))
    def test_15_layout_rejects_traversal(self):
        with self.assertRaises(ValueError): driver.canonical_artifact_layout("../bad")
    def test_16_absent_lock_refused(self):
        with self.assertRaises(driver.LaunchRefused): driver.require_launch_lock(Path("/definitely-not-a-lock"))


if __name__ == "__main__": unittest.main(verbosity=2)
