#!/usr/bin/env python3
"""Fixed static, synthetic, and mock regression suite for TASK-20260908-ccfc14.

The suite deliberately does not call frozen fixture enumeration, T search,
pairing calibration, experimental controls, or a timing panel.  The only
arithmetic uses tiny synthetic fields and curves.  Fake locks/signatures are
isolated mocks and cannot authorize a future run.
"""
from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import json
import os
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import driver


def fixture(*, bits: int = 8, bin_name: str = "1") -> dict[str, object]:
    return {"p": 5, "A": 1, "B": 1, "N": 9, "r": 4, "k": 1,
            "bit_block": bits, "bin": bin_name}


def context() -> dict[str, object]:
    return {"p": 5, "k": 1, "r": 4, "modulus": [2], "A": [1], "B": [1],
            "G": [[1], [2]], "T": [[1], [2]], "shift": [[2], [1]], "chi_g": [2]}


def public_item(*, order: str = "curve_first", q: int = 1) -> driver.PublicEvaluatorInput:
    queries = [{"query_id": index, "Q": [[1], [2]]} for index in range(q)]
    return driver.PublicEvaluatorInput(fixture=fixture(), batch_id=1, q=q, block=0,
                                       repetition=0, order=order, queries=queries, context=context())


class PolynomialWitnessTests(unittest.TestCase):
    def test_01_degree_one_x_plus_one_over_five_is_irreducible(self) -> None:
        certificate = driver.rabin_irreducibility_certificate(5, (1,))
        self.assertTrue(certificate.irreducible)
        self.assertEqual(certificate.reduced_x, (4,))
        self.assertEqual(certificate.frobenius_x, (4,))

    def test_02_degree_one_x_plus_two_over_five_is_irreducible(self) -> None:
        self.assertTrue(driver.rabin_irreducibility_certificate(5, (2,)).irreducible)

    def test_03_degree_one_selector_returns_first_nonzero_constant(self) -> None:
        index, coefficients, seen, certificate = driver.select_certified_modulus(5, 1)
        self.assertEqual((index, coefficients, seen), (1, (1,), [1]))
        self.assertTrue(certificate.irreducible)

    def test_04_degree_two_rabin_retains_gcd_witness(self) -> None:
        certificate = driver.rabin_irreducibility_certificate(3, (1, 0))
        self.assertTrue(certificate.irreducible)
        self.assertEqual(len(certificate.gcd_witnesses), 1)
        self.assertEqual(certificate.gcd_witnesses[0][0], 2)
        self.assertEqual(certificate.gcd_witnesses[0][2], (1,))

    def test_05_reducible_degree_two_is_rejected(self) -> None:
        self.assertFalse(driver.rabin_irreducibility_certificate(3, (2, 0)).irreducible)

    def test_06_finite_field_square_root_is_deterministic(self) -> None:
        field = driver.PolynomialField(3, (1, 0))
        x = field.element((0, 1))
        root = driver.extension_sqrt(field, field.mul(x, x))
        self.assertEqual(field.mul(root, root), field.mul(x, x))
        self.assertLessEqual(root, field.neg(root))


class PublicSchemaTests(unittest.TestCase):
    def test_07_valid_closed_payload_round_trips(self) -> None:
        item = public_item()
        rebuilt = driver.PublicEvaluatorInput.from_payload(item.serialize())
        self.assertEqual(rebuilt.mapping(), item.mapping())

    def test_08_parent_schema_rejects_top_level_label(self) -> None:
        bad = public_item().mapping()
        bad["label"] = 3
        with self.assertRaises(driver.PublicSchemaError):
            driver.audit_public_payload(driver.canonical_json(bad))

    def test_09_parent_schema_rejects_unknown_nested_context_value(self) -> None:
        bad = public_item().mapping()
        bad["context"] = dict(context(), opaque_verifier_value=7)
        with self.assertRaises(driver.PublicSchemaError):
            driver.audit_public_payload(driver.canonical_json(bad))

    def test_10_parent_schema_rejects_label_in_query_object(self) -> None:
        bad = public_item().mapping()
        bad["queries"] = [{"query_id": 0, "Q": [[1], [2]], "scalar": 3}]
        with self.assertRaises(driver.PublicSchemaError):
            driver.audit_public_payload(driver.canonical_json(bad))

    def test_11_child_revalidates_dishonest_payload(self) -> None:
        bad = public_item().mapping()
        bad["label"] = 3
        with self.assertRaises(driver.PublicSchemaError):
            driver._evaluate_public_payload(driver.canonical_json(bad))

    def test_12_duplicate_json_keys_are_rejected(self) -> None:
        duplicate = b'{"fixture":{},"fixture":{},"batch_id":0}'
        with self.assertRaises(driver.PublicSchemaError):
            driver.audit_public_payload(duplicate)

    def test_13_wrong_query_count_is_rejected(self) -> None:
        item = public_item(q=1).mapping()
        item["q"] = 64
        with self.assertRaises(driver.PublicSchemaError):
            driver.audit_public_payload(driver.canonical_json(item))

    def test_14_dishonest_control_exercises_both_actual_boundaries(self) -> None:
        result = driver.dishonest_payload_control(public_item())
        self.assertEqual(result, {"parent_audit_rejected": True, "child_entry_rejected": True, "passed": True})

    def test_15_public_serialization_has_no_label_bearing_mapping(self) -> None:
        encoded = public_item().serialize()
        self.assertNotIn(b"label", encoded)
        self.assertNotIn(b"scalar", encoded)


class WorkloadAndDecoderTests(unittest.TestCase):
    def test_16_fixed_q64_workload_has_exact_prefix(self) -> None:
        labels, counter = driver.fixed_q64_labels(fixture(), 606223)
        self.assertEqual(len(labels), 64)
        self.assertEqual(labels[:1], [labels[0]])
        self.assertGreater(counter, 0)

    def test_17_fixed_workload_is_reproducible_for_same_fixture_and_seed(self) -> None:
        self.assertEqual(driver.fixed_q64_labels(fixture(), 606227), driver.fixed_q64_labels(fixture(), 606227))

    def test_18_fixed_workload_changes_with_target_seed(self) -> None:
        self.assertNotEqual(driver.fixed_q64_labels(fixture(), 606223)[0], driver.fixed_q64_labels(fixture(), 606227)[0])

    def test_19_multiplicative_bsgs_uses_explicit_prepared_table(self) -> None:
        field = driver.PolynomialField(5, (2,))
        table = driver.prepare_multiplicative_bsgs(field.element(2), 4, field)
        self.assertEqual(driver.solve_multiplicative_bsgs(table, field.element(3), field), 3)
        self.assertEqual(set(table.baby.values()), {0, 1})

    def test_20_trivial_character_is_ambiguous(self) -> None:
        field = driver.PolynomialField(5, (2,))
        with self.assertRaises(driver.NoSolution):
            driver.prepare_multiplicative_bsgs(field.one, 4, field)

    def test_21_additive_bsgs_verifies_candidate(self) -> None:
        field = driver.PolynomialField(17, (1,))
        curve = driver.ShortWeierstrassCurve(field, field.element(1), field.element(2))
        point = field.element(1), field.element(2)
        table = driver.prepare_additive_bsgs(curve, point, 24)
        self.assertEqual(driver.solve_additive_bsgs(table, curve.scalar_mul(3, point), curve), 3)

    def test_22_evaluator_obeys_curve_first_order(self) -> None:
        events: list[str] = []
        simple_table = types.SimpleNamespace(baby={"x": 0})
        with mock.patch.object(driver, "prepare_multiplicative_bsgs", return_value=simple_table), \
             mock.patch.object(driver, "prepare_additive_bsgs", return_value=simple_table), \
             mock.patch.object(driver, "solve_additive_bsgs", side_effect=lambda *args: events.append("curve") or 1), \
             mock.patch.object(driver, "evaluate_shifted_tate", side_effect=lambda *args: (events.append("chi") or (2,), 1)), \
             mock.patch.object(driver, "solve_multiplicative_bsgs", side_effect=lambda *args: events.append("field") or 1):
            result = driver._evaluate_public_payload(public_item(order="curve_first").serialize())
        self.assertEqual(events, ["curve", "chi", "field"])
        self.assertEqual(result["order"], "curve_first")

    def test_23_evaluator_obeys_character_first_order(self) -> None:
        events: list[str] = []
        simple_table = types.SimpleNamespace(baby={"x": 0})
        with mock.patch.object(driver, "prepare_multiplicative_bsgs", return_value=simple_table), \
             mock.patch.object(driver, "prepare_additive_bsgs", return_value=simple_table), \
             mock.patch.object(driver, "solve_additive_bsgs", side_effect=lambda *args: events.append("curve") or 1), \
             mock.patch.object(driver, "evaluate_shifted_tate", side_effect=lambda *args: (events.append("chi") or (2,), 1)), \
             mock.patch.object(driver, "solve_multiplicative_bsgs", side_effect=lambda *args: events.append("field") or 1):
            result = driver._evaluate_public_payload(public_item(order="character_first").serialize())
        self.assertEqual(events, ["chi", "field", "curve"])
        self.assertEqual(result["order"], "character_first")

    def test_24_evaluator_response_reports_all_cost_components(self) -> None:
        simple_table = types.SimpleNamespace(baby={"x": 0})
        with mock.patch.object(driver, "prepare_multiplicative_bsgs", return_value=simple_table), \
             mock.patch.object(driver, "prepare_additive_bsgs", return_value=simple_table), \
             mock.patch.object(driver, "solve_additive_bsgs", return_value=1), \
             mock.patch.object(driver, "evaluate_shifted_tate", return_value=((2,), 1)), \
             mock.patch.object(driver, "solve_multiplicative_bsgs", return_value=1):
            costs = driver._evaluate_public_payload(public_item().serialize())["costs"]
        self.assertEqual(set(costs["cpu_seconds"]), {"field_reconstruction", "field_table", "curve_table", "curve_giant_steps", "chi_q", "field_giant_steps", "curve_verify"})
        self.assertIn("field_table_bytes", costs)
        self.assertIn("curve_table_bytes", costs)
        self.assertIn("output_bytes", costs)


class CoverageAndCustodyTests(unittest.TestCase):
    def _selected_panel(self) -> list[dict[str, object]]:
        return [fixture(bits=bits, bin_name=bin_name) for bits in (8, 10) for bin_name in ("1", "2", "3_6", "7_12")]

    def _complete_cells(self, panel: list[dict[str, object]]) -> list[dict[str, object]]:
        control = {"exact_character": {"all_powers": True}, "null_and_injection": {"dishonest_encoder": {"passed": True}}, "full_decoder": {"curve_verified": True}}
        return [{"fixture": item, "seed": seed, "controls": control} for item in panel for seed in driver.TARGET_SEEDS]

    def test_25_complete_coverage_gate_requires_exact_eight_and_two_seeds(self) -> None:
        panel = self._selected_panel()
        calibration = {"status": "completed_valid", "controls": {"exact_character": {"all_powers": True}, "null_and_injection": {"dishonest_encoder": {"passed": True}}}}
        result = driver.validate_panel_coverage(panel, self._complete_cells(panel), calibration)
        self.assertTrue(result["complete"])

    def test_26_coverage_gate_rejects_missing_fixture(self) -> None:
        panel = self._selected_panel()[:-1]
        result = driver.validate_panel_coverage(panel, [], {"status": "completed_valid", "controls": {"exact_character": {"all_powers": True}, "null_and_injection": {"dishonest_encoder": {"passed": True}}}})
        self.assertFalse(result["complete"])

    def test_27_coverage_gate_rejects_missing_seed(self) -> None:
        panel = self._selected_panel()
        cells = self._complete_cells(panel)[1:]
        result = driver.validate_panel_coverage(panel, cells, {"status": "completed_valid", "controls": {"exact_character": {"all_powers": True}, "null_and_injection": {"dishonest_encoder": {"passed": True}}}})
        self.assertFalse(result["complete"])

    def test_28_coverage_gate_rejects_missing_calibration(self) -> None:
        panel = self._selected_panel()
        self.assertFalse(driver.validate_panel_coverage(panel, self._complete_cells(panel), None)["complete"])

    def test_29_decision_matrix_uses_q64_medians_only(self) -> None:
        panel = self._selected_panel()
        rows = []
        for item in panel:
            key = f"{item['bit_block']}:{item['bin']}:{item['p']}:{item['B']}:{item['r']}"
            for seed in driver.TARGET_SEEDS:
                rows.extend([{"fixture_key": key, "seed": seed, "q": 1, "ratio_curve_over_character": 0.1},
                             {"fixture_key": key, "seed": seed, "q": 64, "ratio_curve_over_character": 1.3},
                             {"fixture_key": key, "seed": seed, "q": 64, "ratio_curve_over_character": 1.2}])
        matrix = driver.decision_matrix(rows, panel)
        self.assertTrue(matrix["positive_predicate"]["at_least_one_bin_both_bit_blocks_both_seeds_ge_1_20"])
        self.assertFalse(matrix["negative_predicate"]["all_cells_both_seeds_le_1_00"])

    def test_30_progressive_writer_retains_checkpoint_then_publishes_all_files_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            writer = driver.ProgressiveRunWriter(root, "RUN-MOCK-CUSTODY")
            writer.checkpoint({"event": "prepared", "partial_cells": 1})
            self.assertTrue((writer.partial / "progress.json").is_file())
            records = {"manifest": {"run": {"id": "RUN-MOCK-CUSTODY"}}, "command": "mock", "environment": {},
                       "raw_result": {}, "fixtures": {}, "raw": [], "controls": {}, "cost_rows": [], "certificates": [], "report": "# mock\n"}
            paths = writer.publish(records)
            self.assertEqual(set(paths), set(driver.RUN_FILES))
            self.assertTrue(all(path.is_file() for path in paths.values()))
            self.assertFalse(writer.partial.exists())

    def test_31_canonical_run_path_refuses_traversal(self) -> None:
        with self.assertRaises(driver.LaunchRefused):
            driver.canonical_run_paths(Path("."), "../not-a-run")

    def test_32_canonical_run_path_is_deterministic(self) -> None:
        self.assertTrue(str(next(iter(driver.canonical_run_paths(Path("."), "RUN-ONE").values()))).endswith("runs/RUN-ONE/manifest.yaml"))


class AuthorityAndProtectionTests(unittest.TestCase):
    def _lock(self, plan: Path, root: Path, run_id: str) -> dict[str, object]:
        return {"kind": "genuine_runtime_code_execution_lock", "experiment_id": driver.EXPERIMENT_ID,
                "frozen_approval_decision_id": driver.FROZEN_APPROVAL_ID,
                "implementation_approval_decision_id": driver.IMPLEMENTATION_APPROVAL_ID,
                "spec_sha256": driver.SPEC_SHA256, "execution_plan_sha256": driver.sha256_file(plan),
                "source_closure": {str(Path(driver.__file__).resolve()): driver.sha256_file(Path(driver.__file__)),
                                   str(driver._prior_path.resolve()): driver.PREDECESSOR_SHA256},
                "review_archive": {"snapshot_task_id": driver.REVIEWED_SNAPSHOT_TASK_ID, "reviewed_snapshot_commit": "c" * 40,
                                   "reviewed_source_closure": {str(Path(driver.__file__).resolve()): driver.sha256_file(Path(driver.__file__)),
                                                               str(driver._prior_path.resolve()): driver.PREDECESSOR_SHA256},
                                   "review_task_id": "TASK-FUTURE-INDEPENDENT-REVIEW", "review_commit": "a" * 40, "verdict": "PASS"},
                "runtime": {"provider": "openai", "resolved_model_id": "gpt-5.6-terra", "model_verified": True},
                "implementation_commit": "b" * 40, "dirty_tree": False, "run_id": run_id, "nonce": "n" * 32,
                "output_path": str(next(iter(driver.canonical_run_paths(root, run_id).values())).parent),
                "resource_limits": driver.RESOURCE_LIMITS,
                "machine_protection": {"parent_rlimit_as": True, "child_rlimit_as": True, "serial_worker": True,
                                       "process_group_termination": True, "watchdog_seconds": 10,
                                       "watchdog_justification": "protects a future process group from runaway resources"},
                "signature_b64": base64.b64encode(b"synthetic test signature").decode("ascii")}

    def test_33_source_closure_binds_current_driver_and_transitive_predecessor(self) -> None:
        self.assertEqual(driver.sha256_file(driver._prior_path), driver.PREDECESSOR_SHA256)
        self.assertIn("source_closure", driver.verify_launch_lock.__code__.co_consts)

    def test_34_bedrock_runtime_is_refused_before_signature_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan, key, lock_path = root / "plan.json", root / "key.pub", root / "lock.json"
            plan.write_text("{}\n"); key.write_text("synthetic key\n")
            lock = self._lock(plan, root, "RUN-MOCK-BEDROCK")
            lock["runtime"] = {"provider": "Amazon Bedrock", "resolved_model_id": "bedrock/mock", "model_verified": True}
            lock_path.write_bytes(driver.canonical_json(lock))
            with mock.patch.object(driver, "repository_git_state", return_value=("b" * 40, False)), \
                 mock.patch.object(driver, "_verify_detached_signature") as verify:
                with self.assertRaises(driver.LaunchRefused):
                    driver.verify_launch_lock(lock_path, key, plan, "RUN-MOCK-BEDROCK", root)
            verify.assert_not_called()

    def test_35_mocked_valid_future_lock_requires_all_custody_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan, key, lock_path = root / "plan.json", root / "key.pub", root / "lock.json"
            plan.write_text("{}\n"); key.write_text("synthetic key\n")
            lock = self._lock(plan, root, "RUN-MOCK-LOCK")
            lock_path.write_bytes(driver.canonical_json(lock))
            with mock.patch.object(driver, "repository_git_state", return_value=("b" * 40, False)), \
                 mock.patch.object(driver, "_verify_detached_signature") as verify:
                accepted = driver.verify_launch_lock(lock_path, key, plan, "RUN-MOCK-LOCK", root)
            self.assertEqual(accepted["run_id"], "RUN-MOCK-LOCK")
            verify.assert_called_once()

    def test_35b_lock_refuses_reviewed_snapshot_at_executing_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan, key, lock_path = root / "plan.json", root / "key.pub", root / "lock.json"
            plan.write_text("{}\n"); key.write_text("synthetic key\n")
            lock = self._lock(plan, root, "RUN-MOCK-SNAPSHOT")
            lock["review_archive"]["reviewed_snapshot_commit"] = "b" * 40
            lock_path.write_bytes(driver.canonical_json(lock))
            with mock.patch.object(driver, "repository_git_state", return_value=("b" * 40, False)), \
                 mock.patch.object(driver, "_verify_detached_signature") as verify:
                with self.assertRaises(driver.LaunchRefused):
                    driver.verify_launch_lock(lock_path, key, plan, "RUN-MOCK-SNAPSHOT", root)
            verify.assert_not_called()

    def test_36_lock_refuses_missing_nonce(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan, key, lock_path = root / "plan.json", root / "key.pub", root / "lock.json"
            plan.write_text("{}\n"); key.write_text("synthetic key\n")
            lock = self._lock(plan, root, "RUN-MOCK-NONCE")
            lock.pop("nonce")
            lock_path.write_bytes(driver.canonical_json(lock))
            with self.assertRaises(driver.LaunchRefused):
                driver.verify_launch_lock(lock_path, key, plan, "RUN-MOCK-NONCE", root)

    def test_37_lock_refuses_dirty_runtime_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan, key, lock_path = root / "plan.json", root / "key.pub", root / "lock.json"
            plan.write_text("{}\n"); key.write_text("synthetic key\n")
            lock = self._lock(plan, root, "RUN-MOCK-DIRTY")
            lock_path.write_bytes(driver.canonical_json(lock))
            with mock.patch.object(driver, "repository_git_state", return_value=("b" * 40, True)), \
                 mock.patch.object(driver, "_verify_detached_signature") as verify:
                with self.assertRaises(driver.LaunchRefused):
                    driver.verify_launch_lock(lock_path, key, plan, "RUN-MOCK-DIRTY", root)
            verify.assert_not_called()

    def test_38_kill_process_group_uses_group_target(self) -> None:
        process = mock.Mock(pid=12345)
        process.wait.return_value = 0
        with mock.patch.object(driver.os, "killpg") as killpg:
            driver._kill_process_group(process)
        killpg.assert_called_once_with(12345, driver.signal.SIGTERM)

    def test_39_watchdog_interruption_is_operational(self) -> None:
        guard = driver.MachineProtection(watchdog_seconds=1, started_monotonic=0)
        with mock.patch.object(driver.time, "monotonic", return_value=2):
            with self.assertRaises(driver.RunInterrupted):
                guard.checkpoint()

    def test_40_dry_run_does_not_invoke_fixture_search(self) -> None:
        capture = io.StringIO()
        with mock.patch.object(driver, "build_future_fixtures", side_effect=AssertionError("must not search")), \
             contextlib.redirect_stdout(capture):
            self.assertEqual(driver.main(["--dry-run"]), 0)
        self.assertIn("dry_run_not_launched", capture.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
