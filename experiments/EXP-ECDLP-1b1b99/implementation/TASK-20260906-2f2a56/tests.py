#!/usr/bin/env python3
"""Thirteen synthetic software checks for TASK-20260906-2f2a56; no scientific fixtures."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import driver


class SyntheticContractTests(unittest.TestCase):
    PARAMS = (17, 1, 2, 19, 0, 1, 3)

    def test_01_canonical_json_is_compact(self): self.assertEqual(driver.canonical_json([1, 2]), b"[1,2]")
    def test_02_digest_is_deterministic(self): self.assertEqual(driver.stream_digest(purpose="query", parameters=self.PARAMS, seed=1, counter=0), driver.stream_digest(purpose="query", parameters=self.PARAMS, seed=1, counter=0))
    def test_03_digest_changes_counter(self): self.assertNotEqual(driver.stream_digest(purpose="query", parameters=self.PARAMS, seed=1, counter=0), driver.stream_digest(purpose="query", parameters=self.PARAMS, seed=1, counter=1))
    def test_04_rejection_n_one_consumes_digest(self): self.assertEqual(driver.rejection_draw(purpose="query", parameters=self.PARAMS, seed=1, counter=8, n=1), (0, 9))
    def test_05_rejection_range(self): self.assertIn(driver.rejection_draw(purpose="control", parameters=self.PARAMS, seed=2, counter=0, n=7)[0], range(7))
    def test_06_shuffle_is_deterministic(self): self.assertEqual(driver.fisher_yates([1, 2, 3, 4], parameters=self.PARAMS, seed=3, counter=0), driver.fisher_yates([1, 2, 3, 4], parameters=self.PARAMS, seed=3, counter=0))
    def test_07_sign_selection(self): self.assertEqual(driver.choose_eigenvalue_sign([2, 5], r=7, g0=3, i_map=lambda x: 6, scalar_mul=lambda k, x: k*x % 7), 2)
    def test_08_sign_ambiguity_rejected(self):
        with self.assertRaises(ValueError): driver.choose_eigenvalue_sign([1, 2], r=7, g0=0, i_map=lambda x: 0, scalar_mul=lambda k, x: 0)
    def test_09_transport_order_is_explicit(self): self.assertEqual(driver.charged_transport(1, psi=lambda x: x + 2, i_map=lambda x: x * 3, phi=lambda x: x + 4), 13)
    def test_10_transport_identity(self): self.assertTrue(driver.verify_transport_identity(5, m=6, scalar_mul=lambda k,x:k*x, psi=lambda x:x, i_map=lambda x:2*x, phi=lambda x:3*x))
    def test_11_cost_ledger_preserves_discovery(self):
        ledger = driver.CostLedger({term: 1.0 for term in driver.COST_TERMS}); self.assertGreater(ledger.transport_total(1), ledger.scalar_total(1))
    def test_12_baseline_requires_frozen_selection_cell(self):
        scores = {arm: i for i, arm in enumerate(driver.SCALAR_ARMS)}; self.assertEqual(driver.select_baseline(scores, selection_seed=606101, q=256), "binary_double_and_add")
    def test_13_absent_lock_is_refused(self):
        with self.assertRaises(driver.LaunchRefused): driver.require_launch_lock(Path("/definitely-not-a-lock"))
    def test_14_artifact_layout_is_prospective_only(self): self.assertEqual(len(driver.canonical_artifact_layout("RUN-FUTURE")), 9)
    def test_15_traversal_run_id_is_rejected(self):
        with self.assertRaises(ValueError): driver.canonical_artifact_layout("../bad")
    def test_16_cancellation_boundary_is_explicit(self):
        with self.assertRaises(driver.CancellationRequested): driver.check_cancellation(True, "prepare")


if __name__ == "__main__":
    unittest.main(verbosity=2)
