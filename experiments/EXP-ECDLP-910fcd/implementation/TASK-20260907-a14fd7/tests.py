#!/usr/bin/env python3
"""Ten bounded synthetic checks; none enumerates a frozen fixture or pairing panel."""
import unittest
from pathlib import Path
import driver

class SyntheticTests(unittest.TestCase):
    def test_01_rabin_irreducible(self):
        c=driver.rabin_irreducibility_certificate(3,(1,0)); self.assertTrue(c.irreducible); self.assertEqual(c.frobenius_x,(0,1))
    def test_02_rabin_reducible(self): self.assertFalse(driver.rabin_irreducibility_certificate(3,(2,0)).irreducible)
    def test_03_certified_selection(self):
        i,c,seen,cert=driver.select_certified_modulus(3,2); self.assertEqual((i,c,seen),(1,(1,0),[1])); self.assertTrue(cert.irreducible)
    def test_04_extension_sqrt(self):
        f=driver.PolynomialField(3,(1,0)); x=f.element((0,1)); y=driver.extension_sqrt(f,f.mul(x,x)); self.assertEqual(f.mul(y,y),f.mul(x,x))
    def test_05_multiplicative_bsgs(self):
        f=driver.PolynomialField(5,(2,)); self.assertEqual(driver.bounded_multiplicative_bsgs(f.element(2),f.element(3),4,f),3)
    def test_06_additive_bsgs(self):
        f=driver.PolynomialField(17,(1,)); c=driver.ShortWeierstrassCurve(f,f.element(1),f.element(2)); P=(f.element(1),f.element(2)); self.assertTrue(c.is_on_curve(P)); self.assertEqual(driver.bounded_additive_bsgs(c,P,c.scalar_mul(3,P),24),3)
    def test_07_public_input_has_no_label(self):
        p=driver.PublicEvaluatorInput({"p":3},1,[1,2]); driver.audit_public_input(p); self.assertNotIn(b"label",p.serialize())
    def test_08_injection_audit(self): self.assertTrue(driver.injection_control(7,driver.PublicEvaluatorInput({"p":3},0,[1])))
    def test_09_safe_paths(self):
        with self.assertRaises(driver.LaunchRefused): driver.canonical_run_paths(Path("."),"../bad")
    def test_10_cost_charge(self):
        x=driver.ChargingLedger(fixture_selection=1,field_construction=2,t_search=3,chi_g=4,field_table=5,chi_q=6,field_giant_steps=7,curve_verify=8,curve_table=9,curve_giant_steps=10)
        self.assertGreater(x.character_total(64),x.curve_total(64))

if __name__ == "__main__": unittest.main(verbosity=2)
