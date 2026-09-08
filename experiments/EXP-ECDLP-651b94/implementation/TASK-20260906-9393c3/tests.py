#!/usr/bin/env python3
"""Sixteen synthetic contract checks; no frozen fixture/census/control is run."""
import math
import unittest
from pathlib import Path
import driver

class SyntheticTests(unittest.TestCase):
    p = (17, 1, 2, 19, 0, 1, 1)
    def test_01_json(self): self.assertEqual(driver.canonical_json([1,2]), b"[1,2]")
    def test_02_digest(self): self.assertEqual(driver.stream_digest(purpose="query", params=self.p, seed=1, counter=0), driver.stream_digest(purpose="query", params=self.p, seed=1, counter=0))
    def test_03_n_one(self): self.assertEqual(driver.rejection_draw(purpose="query", params=self.p, seed=1, counter=0, n=1)[1], 1)
    def test_04_shuffle(self): self.assertEqual(driver.fisher_yates([0,1,2], params=self.p, seed=3), driver.fisher_yates([0,1,2], params=self.p, seed=3))
    def test_05_curve_add(self): self.assertTrue(driver.Curve(17, 2, 2).on_curve((5,1)))
    def test_06_transport_infinity(self): self.assertIsNone(driver.coordinate_transport(driver.Curve(17,2,2), None, 3))
    def test_07_factor(self): self.assertEqual(driver.factor(84), [(2,2),(3,1),(7,1)])
    def test_08_rho_public_label(self): self.assertEqual(driver.rho_step(driver.Curve(17,2,2), None, (5,1), (5,1), 0, 0, 19)[3], "add")
    def test_09_binary_synthetic_group(self): self.assertEqual(driver.binary_verifier(driver.Curve(17,2,2), 0, (5,1))[0], None)
    def test_10_occupancy_counts(self):
        a,_=driver.occupancy_assignment([None,(1,1),(2,2)], [0,1,1], params=self.p, seed=2); self.assertEqual(sorted(a.values()), [0,1,1])
    def test_11_pool_infinity(self): self.assertTrue(math.isinf(driver.pooled_null_cost([{ "transition_group_operations":1,"verification_group_operations":0,"successes":0}])) )
    def test_12_branch_incomplete(self): self.assertEqual(driver.heldout_branch([]), "inconclusive")
    def test_13_cayley_stochastic(self): self.assertLess(driver.cayley_control(5,1,2)["row_column_error"], 1e-12)
    def test_14_layout(self): self.assertEqual(len(driver.canonical_artifact_layout("RUN-FUTURE")), 9)
    def test_15_no_traversal(self):
        with self.assertRaises(ValueError): driver.canonical_artifact_layout("../bad")
    def test_16_absent_lock(self):
        with self.assertRaises(driver.LaunchRefused): driver.require_launch_lock(Path("/definitely-not-a-lock"))

if __name__ == "__main__": unittest.main(verbosity=2)
