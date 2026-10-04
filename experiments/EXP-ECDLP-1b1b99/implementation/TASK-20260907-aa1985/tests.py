#!/usr/bin/env python3
"""Ten bounded synthetic/mock checks for TASK-20260907-aa1985.

They use a fixed tiny algebra object and no protocol interval, candidate search,
scientific control panel, timing loop, or persisted run artifact.  One test
invocation executes ten cases and is the sole planned fresh test invocation.
"""
import tempfile
import unittest
from pathlib import Path

import driver


class SyntheticBackendTests(unittest.TestCase):
    # A fixed synthetic F_7 curve with all eight nonzero 3-torsion points.
    E3 = driver.Curve(7, 0, 2)

    def test_01_stream_is_fixed_and_counter_advances(self):
        params=(7,0,2,3,0,0,0)
        self.assertEqual(driver.rejection_draw(purpose="query",parameters=params,seed=2,counter=4,n=1),(0,5))
        self.assertNotEqual(driver.stream_digest(purpose="query",parameters=params,seed=2,counter=4),driver.stream_digest(purpose="query",parameters=params,seed=2,counter=5))

    def test_02_full_torsion_has_four_canonical_kernels(self):
        points,kernels=driver.full_rational_three_torsion(self.E3)
        self.assertEqual(len(points),8); self.assertEqual(len(kernels),4)
        self.assertEqual(len({tuple(k) for k in kernels}),4)

    def test_03_all_four_normalized_maps_have_on_curve_images(self):
        _,kernels=driver.full_rational_three_torsion(self.E3)
        for kernel in kernels:
            phi=driver.normalized_velu_map(self.E3,kernel)
            for P in self.E3.points():
                image=phi.apply(P)
                self.assertTrue(phi.target.on_curve(image))

    def test_04_exact_dual_composes_to_three(self):
        _,kernels=driver.full_rational_three_torsion(self.E3); phi=driver.normalized_velu_map(self.E3,kernels[0])
        P=next(P for P in self.E3.points() if P not in phi.kernel and P is not None)
        dual=driver.exact_dual(phi,P)
        self.assertTrue(dual.check(P))

    def test_05_coordinate_conjugation_round_trip(self):
        change=driver.coordinate_isomorphism(self.E3,2); P=next(P for P in self.E3.points() if P is not None)
        self.assertEqual(change.inverse(change.apply(P)),P)

    def test_06_j1728_automorphism_squares_to_negation(self):
        E=driver.Curve(13,12,0); i=driver.j1728_automorphism(E); P=(5,4)
        self.assertEqual(i(i(P)),E.neg(P))

    def test_07_scalar_arms_agree_on_mock_group(self):
        P=next(P for P in self.E3.points() if P is not None)
        out=driver.scalar_arms(self.E3,11,P)
        self.assertEqual(set(out),set(driver.SCALAR_ARMS)); self.assertEqual(len(set(out.values())),1)

    def test_08_selection_and_costs_retain_charges(self):
        scores={arm:float(i) for i,arm in enumerate(driver.SCALAR_ARMS)}
        self.assertEqual(driver.select_baseline(scores,selection_seed=606101,q=256),"binary_double_and_add")
        ledger=driver.CostLedger({term:1.0 for term in driver.COST_TERMS})
        self.assertGreater(ledger.transport_total(1),ledger.scalar_total(1))

    def test_09_missing_authenticator_lock_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(driver.LaunchRefused): driver.verify_launch_lock(Path(d)/"lock.json",Path(d)/"authorization.json",Path(d)/"authenticator")

    def test_10_artifact_layout_is_prospective_and_safe(self):
        self.assertEqual(len(driver.canonical_artifact_layout("RUN-FUTURE")),9)
        with self.assertRaises(ValueError): driver.canonical_artifact_layout("../unsafe")


if __name__ == "__main__": unittest.main(verbosity=2)
