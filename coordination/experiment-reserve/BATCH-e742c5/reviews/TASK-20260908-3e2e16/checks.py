#!/usr/bin/env python3
"""Bounded implementation-conformance checks for TASK-20260908-3e2e16.

Exactly 50 fixed static, tiny-arithmetic, synthetic, or mock cases are run.
The checker never calls fixture discovery, T search, a real pairing/control
panel, a timing panel, a future-run entrypoint, or a real signature/lock.
"""
from __future__ import annotations

import ast
import base64
import contextlib
import dataclasses
import importlib.util
import io
import json
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest import mock


TASK_ID = "TASK-20260908-3e2e16"
REPO = Path(__file__).resolve().parents[5]
DRIVER_PATH = REPO / "experiments/EXP-ECDLP-910fcd/implementation/TASK-20260908-ccfc14/driver.py"
EXPECTED_CASES = 50

spec = importlib.util.spec_from_file_location("tate_ccfc14_under_review", DRIVER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to load hash-bound producer driver")
driver = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = driver
spec.loader.exec_module(driver)
SOURCE = DRIVER_PATH.read_text(encoding="utf-8")


def fixture(*, bits: int = 8, bin_name: str = "1", k: int = 1) -> dict[str, object]:
    return {"p": 5, "A": 1, "B": 1, "N": 9, "r": 4, "k": k,
            "bit_block": bits, "bin": bin_name}


def context() -> dict[str, object]:
    return {"p": 5, "k": 1, "r": 4, "modulus": [2], "A": [1], "B": [1],
            "G": [[1], [2]], "T": [[1], [2]], "shift": [[2], [1]], "chi_g": [2]}


def public_item(*, order: str = "curve_first", q: int = 1) -> object:
    queries = [{"query_id": index, "Q": [[1], [2]]} for index in range(q)]
    return driver.PublicEvaluatorInput(
        fixture=fixture(), batch_id=1, q=q, block=0, repetition=0,
        order=order, queries=queries, context=context())


def selected_panel() -> list[dict[str, object]]:
    # Deliberately reuses one arithmetic tuple under eight metadata slots.
    return [fixture(bits=bits, bin_name=bin_name) for bits in (8, 10)
            for bin_name in ("1", "2", "3_6", "7_12")]


def minimal_complete_cells(panel: list[dict[str, object]]) -> list[dict[str, object]]:
    controls = {
        "exact_character": {"all_powers": True},
        "null_and_injection": {"dishonest_encoder": {"passed": True}},
        "full_decoder": {"curve_verified": True},
    }
    return [{"fixture": item, "seed": seed, "controls": controls}
            for item in panel for seed in driver.TARGET_SEEDS]


def minimal_calibration() -> dict[str, object]:
    return {"status": "completed_valid", "controls": {
        "exact_character": {"all_powers": True},
        "null_and_injection": {"dishonest_encoder": {"passed": True}},
    }}


def evaluator_with_mocks(item: object) -> tuple[dict[str, object], list[str]]:
    events: list[str] = []
    table = types.SimpleNamespace(baby={"x": 0})
    with mock.patch.object(driver, "prepare_multiplicative_bsgs", return_value=table), \
         mock.patch.object(driver, "prepare_additive_bsgs", return_value=table), \
         mock.patch.object(driver, "solve_additive_bsgs", side_effect=lambda *args: events.append("curve") or 1), \
         mock.patch.object(driver, "evaluate_shifted_tate", side_effect=lambda *args: (events.append("chi") or (2,), 1)), \
         mock.patch.object(driver, "solve_multiplicative_bsgs", side_effect=lambda *args: events.append("field") or 1):
        result = driver._evaluate_public_payload(item.serialize())
    return result, events


def synthetic_lock(plan: Path, root: Path, token: str = "CASE-CUSTODY") -> dict[str, object]:
    closure = {
        str(Path(driver.__file__).resolve()): driver.sha256_file(Path(driver.__file__)),
        str(driver._prior_path.resolve()): driver.PREDECESSOR_SHA256,
    }
    return {
        "kind": "genuine_runtime_code_execution_lock",
        "experiment_id": driver.EXPERIMENT_ID,
        "frozen_approval_decision_id": driver.FROZEN_APPROVAL_ID,
        "implementation_approval_decision_id": driver.IMPLEMENTATION_APPROVAL_ID,
        "spec_sha256": driver.SPEC_SHA256,
        "execution_plan_sha256": driver.sha256_file(plan),
        "source_closure": closure,
        "review_archive": {
            "snapshot_task_id": driver.REVIEWED_SNAPSHOT_TASK_ID,
            "reviewed_snapshot_commit": "c" * 40,
            "reviewed_source_closure": closure,
            "review_task_id": "TASK-SYNTHETIC-REVIEW",
            "review_commit": "a" * 40,
            "verdict": "PASS",
        },
        "runtime": {"provider": "openai", "resolved_model_id": "synthetic", "model_verified": True},
        "implementation_commit": "b" * 40,
        "dirty_tree": False,
        "run_id": token,
        "nonce": "n" * 32,
        "output_path": str(next(iter(driver.canonical_run_paths(root, token).values())).parent),
        "resource_limits": driver.RESOURCE_LIMITS,
        "machine_protection": {
            "parent_rlimit_as": True,
            "child_rlimit_as": True,
            "serial_worker": True,
            "process_group_termination": True,
            "watchdog_seconds": 10,
            "watchdog_justification": "fixed synthetic custody check",
        },
        "signature_b64": base64.b64encode(b"synthetic-only").decode("ascii"),
    }


class ConformanceChecks(unittest.TestCase):
    # Polynomial / field preparation (1-5)
    def test_01_linear_x_plus_one(self) -> None:
        self.assertTrue(driver.rabin_irreducibility_certificate(5, (1,)).irreducible)

    def test_02_linear_x_plus_two(self) -> None:
        self.assertTrue(driver.rabin_irreducibility_certificate(5, (2,)).irreducible)

    def test_03_linear_selector_first_nonzero(self) -> None:
        index, coefficients, tested, certificate = driver.select_certified_modulus(5, 1)
        self.assertEqual((index, coefficients, tested, certificate.irreducible), (1, (1,), [1], True))

    def test_04_quadratic_irreducible_witness(self) -> None:
        certificate = driver.rabin_irreducibility_certificate(3, (1, 0))
        self.assertTrue(certificate.irreducible)
        self.assertEqual(certificate.gcd_witnesses[0][2], (1,))

    def test_05_quadratic_reducible_rejected(self) -> None:
        self.assertFalse(driver.rabin_irreducibility_certificate(3, (2, 0)).irreducible)

    # Closed public input boundary (6-18)
    def test_06_valid_public_payload(self) -> None:
        self.assertEqual(driver.PublicEvaluatorInput.from_payload(public_item().serialize()).mapping(), public_item().mapping())

    def test_07_parent_rejects_top_unknown(self) -> None:
        value = public_item().mapping(); value["label"] = 3
        with self.assertRaises(driver.PublicSchemaError): driver.audit_public_payload(driver.canonical_json(value))

    def test_08_parent_rejects_context_unknown(self) -> None:
        value = public_item().mapping(); value["context"] = dict(context(), hidden=3)
        with self.assertRaises(driver.PublicSchemaError): driver.audit_public_payload(driver.canonical_json(value))

    def test_09_parent_rejects_query_unknown(self) -> None:
        value = public_item().mapping(); value["queries"] = [{"query_id": 0, "Q": [[1], [2]], "scalar": 3}]
        with self.assertRaises(driver.PublicSchemaError): driver.audit_public_payload(driver.canonical_json(value))

    def test_10_parent_rejects_top_duplicate(self) -> None:
        payload = public_item().serialize().replace(b'"batch_id":1', b'"batch_id":1,"batch_id":2', 1)
        with self.assertRaises(driver.PublicSchemaError): driver.audit_public_payload(payload)

    def test_11_parent_rejects_context_duplicate(self) -> None:
        payload = public_item().serialize().replace(b'"chi_g":[2]', b'"chi_g":[2],"chi_g":[3]', 1)
        with self.assertRaises(driver.PublicSchemaError): driver.audit_public_payload(payload)

    def test_12_parent_rejects_query_duplicate(self) -> None:
        payload = public_item().serialize().replace(b'"query_id":0', b'"query_id":0,"query_id":1', 1)
        with self.assertRaises(driver.PublicSchemaError): driver.audit_public_payload(payload)

    def test_13_child_rejects_context_unknown_before_work(self) -> None:
        value = public_item().mapping(); value["context"] = dict(context(), hidden=3)
        with self.assertRaises(driver.PublicSchemaError): driver._evaluate_public_payload(driver.canonical_json(value))

    def test_14_child_rejects_nested_duplicate_before_work(self) -> None:
        payload = public_item().serialize().replace(b'"chi_g":[2]', b'"chi_g":[2],"chi_g":[3]', 1)
        with self.assertRaises(driver.PublicSchemaError): driver._evaluate_public_payload(payload)

    def test_15_wrong_query_count_rejected(self) -> None:
        value = public_item().mapping(); value["q"] = 64
        with self.assertRaises(driver.PublicSchemaError): driver.audit_public_payload(driver.canonical_json(value))

    def test_16_labels_absent_from_serialization(self) -> None:
        payload = public_item().serialize()
        self.assertNotIn(b"label", payload); self.assertNotIn(b"scalar", payload)

    def test_17_out_of_range_coefficient_is_accepted(self) -> None:
        value = public_item().mapping(); value["context"] = dict(context()); value["context"]["A"] = [6]
        self.assertEqual(driver.validate_public_payload(driver.canonical_json(value))["context"]["A"], [6])

    def test_18_fixture_context_curve_mismatch_is_accepted(self) -> None:
        value = public_item().mapping(); value["context"] = dict(context()); value["context"]["A"] = [2]
        self.assertEqual(driver.validate_public_payload(driver.canonical_json(value))["fixture"]["A"], 1)

    # Workload, explicit decoders, and real arm order with fixed mocks (19-29)
    def test_19_q1_is_seed_606223_prefix(self) -> None:
        labels, _ = driver.fixed_q64_labels(fixture(), 606223)
        self.assertEqual(labels[:1], [labels[0]])

    def test_20_target_seed_changes_fixed_sequence(self) -> None:
        self.assertNotEqual(driver.fixed_q64_labels(fixture(), 606223), driver.fixed_q64_labels(fixture(), 606227))

    def test_21_multiplicative_bsgs_zero(self) -> None:
        field = driver.PolynomialField(5, (2,)); table = driver.prepare_multiplicative_bsgs(field.element(2), 4, field)
        self.assertEqual(driver.solve_multiplicative_bsgs(table, field.one, field), 0)

    def test_22_multiplicative_bsgs_one(self) -> None:
        field = driver.PolynomialField(5, (2,)); table = driver.prepare_multiplicative_bsgs(field.element(2), 4, field)
        self.assertEqual(driver.solve_multiplicative_bsgs(table, field.element(2), field), 1)

    def test_23_multiplicative_bsgs_two(self) -> None:
        field = driver.PolynomialField(5, (2,)); table = driver.prepare_multiplicative_bsgs(field.element(2), 4, field)
        self.assertEqual(driver.solve_multiplicative_bsgs(table, field.element(4), field), 2)

    def test_24_multiplicative_bsgs_three(self) -> None:
        field = driver.PolynomialField(5, (2,)); table = driver.prepare_multiplicative_bsgs(field.element(2), 4, field)
        self.assertEqual(driver.solve_multiplicative_bsgs(table, field.element(3), field), 3)

    def test_25_trivial_character_refused(self) -> None:
        field = driver.PolynomialField(5, (2,))
        with self.assertRaises(driver.NoSolution): driver.prepare_multiplicative_bsgs(field.one, 4, field)

    def test_26_additive_bsgs_zero(self) -> None:
        field = driver.PolynomialField(17, (1,)); curve = driver.ShortWeierstrassCurve(field, field.element(1), field.element(2)); point = (field.element(1), field.element(2))
        table = driver.prepare_additive_bsgs(curve, point, 24)
        self.assertEqual(driver.solve_additive_bsgs(table, None, curve), 0)

    def test_27_additive_bsgs_three(self) -> None:
        field = driver.PolynomialField(17, (1,)); curve = driver.ShortWeierstrassCurve(field, field.element(1), field.element(2)); point = (field.element(1), field.element(2))
        table = driver.prepare_additive_bsgs(curve, point, 24)
        self.assertEqual(driver.solve_additive_bsgs(table, curve.scalar_mul(3, point), curve), 3)

    def test_28_curve_first_is_executable_order(self) -> None:
        result, events = evaluator_with_mocks(public_item(order="curve_first"))
        self.assertEqual((events, result["order"]), (["curve", "chi", "field"], "curve_first"))

    def test_29_character_first_is_executable_order(self) -> None:
        result, events = evaluator_with_mocks(public_item(order="character_first"))
        self.assertEqual((events, result["order"]), (["chi", "field", "curve"], "character_first"))

    # Cost, coverage, controls, and resolution (30-42)
    def test_30_evaluator_emits_declared_local_cost_keys(self) -> None:
        result, _ = evaluator_with_mocks(public_item())
        self.assertEqual(set(result["costs"]["cpu_seconds"]), {"field_reconstruction", "field_table", "curve_table", "curve_giant_steps", "chi_q", "field_giant_steps", "curve_verify"})
        self.assertEqual(result["costs"]["operation_counts"], {"field": "unavailable_uninstrumented", "group": "unavailable_uninstrumented"})

    def test_31_generator_cost_counterexample(self) -> None:
        ledger = driver.ChargingLedger(field_construction=5.0)
        self.assertEqual((ledger.character_total(), ledger.curve_total()), (5.0, 0.0))
        self.assertLess(SOURCE.index("generator, generator_attempts"), SOURCE.index("field_cpu = time.process_time() - field_started"))

    def test_32_scaffolding_cost_keys_are_missing(self) -> None:
        fields = {item.name for item in dataclasses.fields(driver.ChargingLedger)}
        self.assertTrue({"query_generation", "exact_controls", "coordinate_control"}.isdisjoint(fields))

    def test_33_field_byte_encoder_is_missing(self) -> None:
        public_source = SOURCE[SOURCE.index("class PublicEvaluatorInput"):SOURCE.index("# Pairing and explicit BSGS")]
        self.assertNotIn("to_bytes", public_source)
        self.assertIn("canonical_json", public_source)

    def test_34_fixture_selector_has_no_one_bin_break(self) -> None:
        tree = ast.parse(SOURCE)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "build_future_fixtures")
        self.assertEqual(sum(isinstance(node, ast.Break) for node in ast.walk(function)), 0)

    def test_35_basic_synthetic_coverage_passes(self) -> None:
        panel = selected_panel()
        self.assertTrue(driver.validate_panel_coverage(panel, minimal_complete_cells(panel), minimal_calibration())["complete"])

    def test_36_missing_fixture_fails_coverage(self) -> None:
        panel = selected_panel()[:-1]
        self.assertFalse(driver.validate_panel_coverage(panel, minimal_complete_cells(panel), minimal_calibration())["complete"])

    def test_37_relabelled_duplicate_arithmetic_cells_pass_coverage(self) -> None:
        panel = selected_panel()
        self.assertEqual(len({(row["p"], row["A"], row["B"], row["r"], row["k"]) for row in panel}), 1)
        self.assertTrue(driver.validate_panel_coverage(panel, minimal_complete_cells(panel), minimal_calibration())["complete"])

    def test_38_incomplete_control_set_passes_coverage(self) -> None:
        panel = selected_panel()
        result = driver.validate_panel_coverage(panel, minimal_complete_cells(panel), minimal_calibration())
        self.assertTrue(result["complete"])
        self.assertNotIn("coordinates", minimal_complete_cells(panel)[0]["controls"])

    def test_39_missing_calibration_fails_coverage(self) -> None:
        panel = selected_panel()
        self.assertFalse(driver.validate_panel_coverage(panel, minimal_complete_cells(panel), None)["complete"])

    def test_40_sparse_positive_cost_rows_pass_predicate(self) -> None:
        panel = selected_panel(); rows = []
        for item in panel:
            key = f"{item['bit_block']}:{item['bin']}:{item['p']}:{item['B']}:{item['r']}"
            for seed in driver.TARGET_SEEDS: rows.append({"fixture_key": key, "seed": seed, "q": 64, "ratio_curve_over_character": 1.3})
        self.assertTrue(driver.decision_matrix(rows, panel)["positive_predicate"]["at_least_one_bin_both_bit_blocks_both_seeds_ge_1_20"])

    def test_41_one_row_can_trigger_negative_predicate(self) -> None:
        panel = selected_panel(); item = panel[0]
        row = {"fixture_key": f"{item['bit_block']}:{item['bin']}:{item['p']}:{item['B']}:{item['r']}", "seed": driver.TARGET_SEEDS[0], "q": 64, "ratio_curve_over_character": 0.9}
        self.assertTrue(driver.decision_matrix([row], panel)["negative_predicate"]["all_cells_both_seeds_le_1_00"])

    def test_42_resolution_is_one_combined_accumulator(self) -> None:
        cell_source = SOURCE[SOURCE.index("def _future_cell"):SOURCE.index("def validate_panel_coverage")]
        self.assertIn('elapsed_cpu += costs["total_cpu_seconds"]', cell_source)
        self.assertNotIn("elapsed_cpu_by_q", cell_source)

    # Control ordering, failure semantics, and partial custody (43-46)
    def test_43_weil_self_pairing_control_is_absent(self) -> None:
        self.assertNotIn("weil", SOURCE.casefold())

    def test_44_exact_controls_follow_timing_workload(self) -> None:
        cell_source = SOURCE[SOURCE.index("def _future_cell"):SOURCE.index("def validate_panel_coverage")]
        self.assertLess(cell_source.index("while repetitions < 100"), cell_source.index("exact = exact_character_control"))

    def test_45_search_exhaustion_maps_to_completed_invalid(self) -> None:
        execute_source = SOURCE[SOURCE.index("def execute_authorized_run"):SOURCE.index("def coverage")]
        search_block = execute_source[execute_source.index("except SearchExhausted"):execute_source.index("except RunInterrupted")]
        self.assertIn('status = "completed_invalid"', search_block)

    def test_46_current_cell_rejection_state_is_not_recovered(self) -> None:
        execute_source = SOURCE[SOURCE.index("def execute_authorized_run"):SOURCE.index("def coverage")]
        search_block = execute_source[execute_source.index("except SearchExhausted"):execute_source.index("except RunInterrupted")]
        self.assertNotIn("t_attempts", search_block)
        self.assertNotIn("generator_attempts", search_block)
        self.assertNotIn("tested_indices", search_block)

    # Review/source authority and process/canonical custody (47-50)
    def test_47_forged_unreachable_review_commits_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); plan = root / "plan.json"; key = root / "key.pub"; lock_path = root / "synthetic.json"
            plan.write_text("{}\n", encoding="utf-8"); key.write_text("synthetic\n", encoding="utf-8")
            value = synthetic_lock(plan, root); lock_path.write_bytes(driver.canonical_json(value))
            with mock.patch.object(driver, "repository_git_state", return_value=("b" * 40, False)), mock.patch.object(driver, "_verify_detached_signature"):
                accepted = driver.verify_launch_lock(lock_path, key, plan, "CASE-CUSTODY", root)
        self.assertEqual(accepted["review_archive"]["review_commit"], "a" * 40)

    def test_48_altered_executing_source_closure_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); plan = root / "plan.json"; key = root / "key.pub"; lock_path = root / "synthetic.json"
            plan.write_text("{}\n", encoding="utf-8"); key.write_text("synthetic\n", encoding="utf-8")
            value = synthetic_lock(plan, root); value["source_closure"] = dict(value["source_closure"]); value["source_closure"][str(Path(driver.__file__).resolve())] = "0" * 64
            lock_path.write_bytes(driver.canonical_json(value))
            with mock.patch.object(driver, "_verify_detached_signature") as verify:
                with self.assertRaises(driver.LaunchRefused): driver.verify_launch_lock(lock_path, key, plan, "CASE-CUSTODY", root)
            verify.assert_not_called()

    def test_49_process_group_kill_targets_group(self) -> None:
        process = mock.Mock(pid=12345); process.wait.return_value = 0
        with mock.patch.object(driver.os, "killpg") as killpg: driver._kill_process_group(process)
        killpg.assert_called_once_with(12345, driver.signal.SIGTERM)

    def test_50_atomic_mock_publication_leaves_unbound_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            writer = driver.ProgressiveRunWriter(Path(temporary), "CASE-PUBLICATION")
            writer.checkpoint({"event": "partial", "cost": 1})
            records = {"manifest": {"run": {"id": "CASE-PUBLICATION"}}, "command": "synthetic", "environment": {},
                       "raw_result": {}, "fixtures": {}, "raw": [], "controls": {}, "cost_rows": [], "certificates": [], "report": "synthetic\n"}
            paths = writer.publish(records); final = next(iter(paths.values())).parent
            self.assertTrue(all(path.is_file() for path in paths.values()))
            self.assertTrue((final / "progress.json").is_file())
            self.assertNotIn("progress.json", paths)


if __name__ == "__main__":
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    stream = io.StringIO()
    with contextlib.redirect_stderr(stream):
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(ConformanceChecks))
    summary = {
        "task_id": TASK_ID,
        "expected_cases": EXPECTED_CASES,
        "cases_run": result.testsRun,
        "passed": result.wasSuccessful() and result.testsRun == EXPECTED_CASES,
        "failures": [str(test) for test, _ in result.failures],
        "errors": [str(test) for test, _ in result.errors],
        "skipped": len(result.skipped),
        "wall_seconds_internal": time.monotonic() - started_wall,
        "cpu_seconds_internal": time.process_time() - started_cpu,
        "scientific_runs": 0,
        "forbidden_stage_invocations": 0,
    }
    print(stream.getvalue(), end="")
    print(json.dumps(summary, sort_keys=True))
    raise SystemExit(0 if summary["passed"] else 1)
