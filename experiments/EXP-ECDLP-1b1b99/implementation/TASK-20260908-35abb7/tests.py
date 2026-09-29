#!/usr/bin/env python3
"""Fixed nonexperimental checks for TASK-20260908-35abb7.

The suite uses only hand-chosen tiny field objects, malformed authority bytes,
and temporary custody paths.  It does not enumerate frozen prime intervals,
run any scientific control/timing matrix, create a RUN identifier, or sign a
launch payload.  There are 16 fixed test methods; each is one bounded
synthetic/static check for this implementation task.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import driver


class StaticCMImplementationTests(unittest.TestCase):
    # This fixed F_7 object is not in a protocol interval and is used only to
    # check finite formulas.  Its eight nonzero 3-torsion points are known.
    E3 = driver.Curve(7, 0, 2)

    def test_01_canonical_json_rejects_floats_and_appends_newline(self) -> None:
        self.assertEqual(driver.canonical_json({"a": 1}), b'{"a":1}\n')
        with self.assertRaises(ValueError): driver.canonical_json({"a": 1.0})

    def test_02_stream_state_persists_and_n_one_consumes_digest(self) -> None:
        state = driver.StreamState(); params = (7, 0, 2, 3, 0, 0, 0)
        self.assertEqual(state.draw("query", params, 2, 1), 0)
        self.assertEqual(state.snapshot()[json.dumps(["query", list(params), 2], separators=(",", ":"))], 1)

    def test_03_full_torsion_is_exactly_four_canonical_kernels(self) -> None:
        points, kernels = driver.full_rational_three_torsion(self.E3)
        self.assertEqual(len(points), 8); self.assertEqual(len(kernels), 4)
        self.assertEqual(len({tuple(item) for item in kernels}), 4)

    def test_04_each_velu_map_has_target_images(self) -> None:
        _, kernels = driver.full_rational_three_torsion(self.E3)
        for kernel in kernels:
            mapping = driver.normalized_velu_map(self.E3, kernel)
            for point in self.E3.points(): self.assertTrue(mapping.target.on_curve(mapping.apply(point)))

    def test_05_exact_dual_has_source_and_target_compositions(self) -> None:
        _, kernels = driver.full_rational_three_torsion(self.E3); forward = driver.normalized_velu_map(self.E3, kernels[0])
        source_point = next(point for point in self.E3.points() if point is not None and point not in forward.kernel)
        pair = driver.exact_dual(forward, source_point); target_point = forward.apply(source_point)
        self.assertTrue(pair.source_composition(source_point)); self.assertTrue(pair.target_composition(target_point))

    def test_06_coordinate_dual_uses_inverse_scale(self) -> None:
        _, kernels = driver.full_rational_three_torsion(self.E3); forward = driver.normalized_velu_map(self.E3, kernels[0])
        point = next(item for item in self.E3.points() if item is not None and item not in forward.kernel)
        endpoint = driver.Endpoint("K0", "C0", forward, driver.Isomorphism(forward.target, forward.target, 1), driver.exact_dual(forward, point))
        coordinate = endpoint.coordinate(2); target = coordinate.phi(point)
        self.assertEqual(coordinate.psi(target), self.E3.mul(3, point))

    def test_07_j1728_automorphism_squares_to_negation(self) -> None:
        curve = driver.Curve(13, 12, 0); point = (5, 4); iota = driver.j1728_automorphism(curve)
        self.assertEqual(iota(iota(point)), curve.neg(point))

    def test_08_all_six_scalar_arms_agree_including_real_pari_arm(self) -> None:
        point = next(item for item in self.E3.points() if item is not None)
        outputs = driver.scalar_arms(self.E3, 11, point)
        self.assertEqual(set(outputs), set(driver.SCALAR_ARMS)); self.assertEqual(len(set(outputs.values())), 1)

    def test_09_public_boundary_accepts_only_closed_schema(self) -> None:
        batch = driver.PublicEvaluatorBatch("opaque", (7, 0, 2), (7, 0, 2), 3, 2, "phi", "psi", ("rho_1",), ((1, 3),), 1)
        driver.validate_public_batch(batch.wire())
        leaked = batch.wire(); leaked["kernel_label"] = "K0"
        with self.assertRaises(driver.InvalidMeasurement): driver.validate_public_batch(leaked)

    def test_10_integer_allocation_reconciles_exactly(self) -> None:
        row = driver.BlockCost("I0F0", "K0", "C0", 1, 606101, 1, 2, 0, 0, "scalar_multiplication", "static", 5, 7, 0, False)
        allocations = driver.allocate_equal(row, "scalar", "measured_arm_workload", ("a", "b"), "STATIC")
        driver.reconcile_allocations((row,), allocations)
        self.assertEqual(sum(item.allocated_CPU_nanoseconds for item in allocations), 5)

    def test_11_selection_refuses_incomplete_nine_strata(self) -> None:
        row = driver.BlockCost("I0F0", "K0", "C0", 1, 606101, 256, 2, 0, 0, "scalar_multiplication", "static", 1, 1, 0, False)
        with self.assertRaises(driver.InvalidMeasurement): driver.select_baselines((row,))

    def test_12_malformed_authorization_is_typed_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            temporary = Path(name); payload = temporary / "payload"; payload.write_text("{\"x\":1}\n")
            result = driver.verify_future_authorization(payload, temporary / "missing.sig", temporary / "nonce")
            self.assertFalse(result.accepted); self.assertEqual(result.code, "AUTH_MALFORMED")

    def test_13_nonce_registry_rejects_replay(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            registry = Path(name) / "nonce"; nonce = "a" * 64
            self.assertTrue(driver.claim_nonce(registry, nonce, "FUTURE-UNIT", "b"*64).accepted)
            self.assertEqual(driver.claim_nonce(registry, nonce, "FUTURE-UNIT", "b"*64).code, "AUTH_NONCE_REPLAY")

    def test_14_custody_is_atomic_and_requires_all_twelve_files(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            custody = driver.Custody(Path(name), "FUTURE-UNIT")
            for artifact in driver.REQUIRED_ARTIFACTS: custody.write(artifact, b"static nonempty artifact\n")
            final = custody.publish(); self.assertTrue(final.is_dir()); self.assertFalse(custody.partial.exists())

    def test_15_hard_reducer_refuses_empty_and_false_collections(self) -> None:
        self.assertEqual(driver.hard_validity_reduce((), {}, {}, False, False), "partial_inconclusive")

    def test_16_source_and_runtime_bindings_remain_exact(self) -> None:
        driver.fixed_runtime_source_checks(); binding = driver.verify_pinned_runtime()
        self.assertEqual(binding["runtime"]["cypari2"], "2.2.4")


if __name__ == "__main__": unittest.main(verbosity=2)
