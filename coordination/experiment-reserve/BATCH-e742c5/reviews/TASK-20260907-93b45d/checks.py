#!/usr/bin/env python3
"""Bounded Validator checks for TASK-20260907-93b45d.

These are twelve fixed static, synthetic, or mock cases.  They do not enumerate
the frozen fixture panel, evaluate a pairing calibration, execute an
experimental control, or collect a timing panel.
"""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import inspect
import json
import subprocess
import sys
import tempfile
import types
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest import mock

import yaml


TASK_ID = "TASK-20260907-93b45d"
HANDOFF_COMMIT = "baefa00db9140147c9cbf11e239310bd299c37d3"
SNAPSHOT_COMMIT = "8d43ab4a2badcce5e969e9fb0295ae6fc442e194"
PRIOR_COMMIT = "bdd003870990d545a84859eb131c902b45e51983"
REPO = Path(__file__).resolve().parents[5]
HANDOFF_PATH = "ledger/handoffs/TASK-20260907-93b45d.yaml"
QUEUE_PATH = "coordination/experiment-reserve/BATCH-e742c5/dispatch_queue.json"
DRIVER_REL = "experiments/EXP-ECDLP-910fcd/implementation/TASK-20260907-a14fd7/driver.py"
TESTS_REL = "experiments/EXP-ECDLP-910fcd/implementation/TASK-20260907-a14fd7/tests.py"
REPORT_REL = "experiments/EXP-ECDLP-910fcd/implementation/TASK-20260907-a14fd7/implementation-report.yaml"
PRIOR_REL = "experiments/EXP-ECDLP-910fcd/implementation/TASK-20260906-681152/driver.py"
DRIVER_SHA256 = "3e095238ee18c8ff13751d207dc1854bb283fb43acfc1f91285fc532280606fc"
PRIOR_SHA256 = "1cb875e5d9cc50351f64357af7f20485c54243d2215fe3bf92cae250a0d097e0"


def git_show(commit: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(REPO), "show", f"{commit}:{path}"]
    )


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# The final driver imports the predecessor by live relative path.  Refuse to
# load either until both live files match the producer's committed bindings.
driver_path = REPO / DRIVER_REL
prior_path = REPO / PRIOR_REL
if sha256(driver_path.read_bytes()) != DRIVER_SHA256:
    raise RuntimeError("final driver differs from the committed review snapshot")
if sha256(prior_path.read_bytes()) != PRIOR_SHA256:
    raise RuntimeError("transitive predecessor differs from its recorded snapshot")

driver_spec = importlib.util.spec_from_file_location("_validator_tate_driver", driver_path)
if driver_spec is None or driver_spec.loader is None:
    raise RuntimeError("unable to load pinned Tate driver")
driver = importlib.util.module_from_spec(driver_spec)
sys.modules[driver_spec.name] = driver
driver_spec.loader.exec_module(driver)


class ValidatorChecks(unittest.TestCase):
    maxDiff = None

    def test_01_pinned_sources_hold_but_transitive_predecessor_is_outside_declared_read_scope(self):
        handoff_doc = yaml.safe_load(git_show(HANDOFF_COMMIT, HANDOFF_PATH))
        handoff = handoff_doc["handoff"]
        for binding in handoff["source_bindings"]:
            commit = binding.get("snapshot_commit") or HANDOFF_COMMIT
            self.assertEqual(sha256(git_show(commit, binding["path"])), binding["sha256"])

        implementation_report = yaml.safe_load(git_show(SNAPSHOT_COMMIT, REPORT_REL))["implementation"]
        prior_binding = next(
            item for item in implementation_report["source_bindings"]
            if item["path"] == PRIOR_REL
        )
        self.assertEqual(prior_binding["snapshot_commit"], PRIOR_COMMIT)
        self.assertEqual(prior_binding["sha256"], PRIOR_SHA256)
        self.assertEqual(sha256(git_show(PRIOR_COMMIT, PRIOR_REL)), PRIOR_SHA256)

        queue = json.loads(git_show(HANDOFF_COMMIT, QUEUE_PATH))
        task = next(item for item in queue["tasks"] if item["id"] == TASK_ID)
        self.assertNotIn(PRIOR_REL, handoff["inputs"])
        self.assertNotIn(PRIOR_REL, task["read_scope"])

    def test_02_final_producer_tests_construct_public_input_with_obsolete_signature(self):
        parameters = inspect.signature(driver.PublicEvaluatorInput).parameters
        self.assertEqual(list(parameters), ["fixture", "query_id", "Q", "context"])
        with self.assertRaises(TypeError):
            driver.PublicEvaluatorInput({"p": 3}, 1, [1, 2])
        tests_source = git_show(SNAPSHOT_COMMIT, TESTS_REL).decode("utf-8")
        self.assertIn('PublicEvaluatorInput({"p":3},1,[1,2])', tests_source)
        self.assertIn('PublicEvaluatorInput({"p":3},0,[1])', tests_source)

    def test_03_degree_one_rabin_rejects_irreducible_linear_polynomials(self):
        # X+1 over F_5 is irreducible.  The implementation compares X^5 mod
        # (X+1) with unreduced X, so the k=1 fixture bin cannot prepare.
        certificate = driver.rabin_irreducibility_certificate(5, (1,))
        self.assertFalse(certificate.irreducible)
        with self.assertRaises(driver.SearchExhausted):
            driver.select_certified_modulus(5, 1)

    def test_04_public_input_blacklist_allows_withheld_scalar_under_unrecognised_key(self):
        item = driver.PublicEvaluatorInput(
            {"p": 3}, 0, [1, 2], {"opaque_verifier_value": 7}
        )
        driver.audit_public_input(item)
        self.assertIn(b'"opaque_verifier_value":7', item.serialize())
        cell_source = inspect.getsource(driver._future_cell)
        self.assertIn('dishonest["label"]=label', cell_source)
        self.assertNotIn("audit_public_input(dishonest)", cell_source)

    def test_05_target_prefix_reuse_and_timing_alternation_are_labels_only(self):
        cell_source = inspect.getsource(driver._future_cell)
        self.assertLess(cell_source.index("while repeats < 100"), cell_source.index("for block in range(7)"))
        self.assertLess(cell_source.index("for block in range(7)"), cell_source.index("for q in (1,64)"))
        self.assertLess(cell_source.index("for q in (1,64)"), cell_source.index('purpose="query"'))
        self.assertIn('"character_first" if block%2 else "curve_first"', cell_source)

        evaluator_source = inspect.getsource(driver._evaluate_public_payload)
        self.assertLess(evaluator_source.index("bounded_additive_bsgs"), evaluator_source.index("evaluate_shifted_tate"))
        self.assertLess(evaluator_source.index("evaluate_shifted_tate"), evaluator_source.index("bounded_multiplicative_bsgs"))
        self.assertNotIn("block", evaluator_source)

    def test_06_cost_decomposition_omits_setup_splits_and_child_reconstruction(self):
        cell_source = inspect.getsource(driver._future_cell)
        self.assertIn(
            "fixture_selection=field_done-began,field_construction=field_done-began",
            cell_source,
        )
        for component in ("chi_g", "field_table", "curve_table"):
            self.assertNotIn(f"phase.{component}+", cell_source)

        evaluator_source = inspect.getsource(driver._evaluate_public_payload)
        self.assertLess(evaluator_source.index("field=PolynomialField"), evaluator_source.index("c0=time.process_time()"))
        self.assertLess(evaluator_source.index("curve=ShortWeierstrassCurve"), evaluator_source.index("c0=time.process_time()"))

    def test_07_timeout_does_not_kill_the_started_process_group(self):
        item = driver.PublicEvaluatorInput({}, 0, [1, 2], {})
        timeout = subprocess.TimeoutExpired(cmd=["child"], timeout=1)
        with mock.patch.object(driver.subprocess, "run", side_effect=timeout), \
             mock.patch.object(driver.os, "killpg", create=True) as killpg:
            with self.assertRaises(driver.RunInterrupted):
                driver.invoke_public_evaluator(item, timeout_seconds=1)
        killpg.assert_not_called()

    def test_08_launch_lock_accepts_prohibited_unverified_runtime_and_omits_custody_fields(self):
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            plan = temp / "plan.json"
            key = temp / "coordinator.pub"
            lock_path = temp / "lock.json"
            plan.write_text("{}\n")
            key.write_text("mock public key\n")
            lock = {
                "kind": "genuine_runtime_code_execution_lock",
                "experiment_id": driver.EXPERIMENT_ID,
                "approval_decision_id": driver.APPROVAL_ID,
                "spec_sha256": driver.SPEC_SHA256,
                "driver_sha256": driver.sha256_file(Path(driver.__file__)),
                "execution_plan_sha256": driver.sha256_file(plan),
                "runtime": {
                    "provider": "Amazon Bedrock",
                    "model_verified": False,
                    "resolved_model_id": "bedrock/mock",
                },
                "resource_limits": driver.RESOURCE_LIMITS,
                "signature_b64": base64.b64encode(b"mock signature").decode("ascii"),
            }
            lock_path.write_text(json.dumps(lock))
            with mock.patch.object(
                driver.subprocess, "run", return_value=types.SimpleNamespace(returncode=0)
            ):
                accepted = driver.verify_launch_lock(lock_path, key, plan)
            self.assertEqual(accepted["runtime"]["provider"], "Amazon Bedrock")

        verifier_source = inspect.getsource(driver.verify_launch_lock)
        self.assertNotIn("IMPLEMENTATION_APPROVAL_ID", verifier_source)
        self.assertNotIn("run_id", verifier_source)
        self.assertNotIn("predecessor", verifier_source)

    def test_09_incomplete_panel_without_calibration_is_marked_completed(self):
        captured: dict[str, object] = {}
        fixture = {"p": 257, "A": 1, "B": 1, "N": 272, "r": 17, "k": 1, "bit_block": 8, "bin": "1"}

        def fake_cell(item, seed):
            return (
                {"fixture": item, "seed": seed, "repetitions": 1, "raw": [{"seed": seed}]},
                {"synthetic": True},
                asdict(driver.ChargingLedger()),
                {"synthetic": True},
            )

        def capture_package(root, run_id, records):
            captured["records"] = records
            return {}

        with mock.patch.object(
            driver,
            "verify_launch_lock",
            return_value={"runtime": {}, "implementation_commit": None, "dirty_tree": None},
        ), mock.patch.object(driver, "build_future_fixtures", return_value=([fixture], [])), \
             mock.patch.object(driver, "_future_cell", side_effect=fake_cell), \
             mock.patch.object(driver, "write_run_package", side_effect=capture_package):
            driver.execute_authorized_run(
                Path("lock"), Path("key"), Path("plan"), "RUN-MOCK-ONE-CELL", Path(".")
            )

        records = captured["records"]
        self.assertEqual(records["raw_result"]["status"], "completed_pending_review")
        self.assertEqual(len(records["fixtures"]["selected"]), 1)
        self.assertNotIn("calibration", records["fixtures"])
        self.assertIsNone(records["manifest"]["run"]["code"]["commit"])
        self.assertIsNone(records["manifest"]["run"]["code"]["dirty"])
        self.assertIsNone(records["manifest"]["run"]["resources"]["peak_rss_bytes"])
        self.assertNotIn("--run-id", records["command"])

    def test_10_search_exhaustion_is_misclassified_and_has_no_progressive_receipt(self):
        captured: dict[str, object] = {}

        def capture_package(root, run_id, records):
            captured["records"] = records
            return {}

        with mock.patch.object(
            driver,
            "verify_launch_lock",
            return_value={"runtime": {}, "implementation_commit": "mock", "dirty_tree": False},
        ), mock.patch.object(
            driver,
            "build_future_fixtures",
            side_effect=driver.SearchExhausted("missing frozen fixture bin"),
        ), mock.patch.object(driver, "write_run_package", side_effect=capture_package):
            driver.execute_authorized_run(
                Path("lock"), Path("key"), Path("plan"), "RUN-MOCK-MISSING", Path(".")
            )

        records = captured["records"]
        self.assertEqual(records["raw_result"]["status"], "failed")
        self.assertEqual(
            records["raw_result"]["failures"][0]["classification"], "invalid_measurement"
        )
        self.assertEqual(records["fixtures"]["selected"], [])

    def test_11_main_resource_limits_and_progressive_writes_are_not_enforced(self):
        execute_source = inspect.getsource(driver.execute_authorized_run)
        self.assertNotIn("setrlimit", execute_source)
        self.assertNotIn("signal.signal", execute_source)
        self.assertNotIn("timeout=", execute_source)
        self.assertEqual(execute_source.count("write_run_package("), 1)
        self.assertGreater(
            execute_source.index("return write_run_package"),
            execute_source.index("except Exception"),
        )

    def test_12_complete_mock_package_publishes_once_to_canonical_directory(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            records = {
                "manifest": {"run": {"id": "RUN-MOCK-ATOMIC"}},
                "command": "mock command",
                "environment": {},
                "raw_result": {},
                "fixtures": {},
                "raw": [],
                "controls": {},
                "costs": {"cpu_seconds": 0.0},
                "certificates": [],
                "stdout": "",
                "stderr": "",
                "report": "# Mock only\n",
            }
            paths = driver.write_run_package(root, "RUN-MOCK-ATOMIC", records)
            self.assertEqual(set(paths), set(driver.RUN_FILES))
            self.assertTrue(all(path.is_file() for path in paths.values()))
            self.assertFalse(list((root / "runs").glob("*.partial-*")))
            with self.assertRaises(driver.LaunchRefused):
                driver.write_run_package(root, "RUN-MOCK-ATOMIC", records)


if __name__ == "__main__":
    unittest.main(verbosity=2)
