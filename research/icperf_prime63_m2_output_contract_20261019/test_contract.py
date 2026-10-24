"""No-solver tests for a prospective standard-supervisor output bridge."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))
import contract  # noqa: E402
import experiment_execution  # noqa: E402


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run_dir = Path(self.temp.name)
        (self.run_dir / "diagnostic").mkdir()
        launch = {"run_id": "RUN-ICPERF-123abc", "trial_id": "fixed-three-arm",
                  "plan_sha256": "a" * 64,
                  "authority": {"owner": "executor-fixture", "epoch": 1}}
        launch_bytes = contract.canonical(launch)
        (self.run_dir / "launch.json").write_bytes(launch_bytes)
        (self.run_dir / "environment.json").write_bytes(contract.canonical({
            "commit": "b" * 40, "platform": "test", "source_sha256": {"source.py": "c" * 64}}))
        (self.run_dir / "command.txt").write_text("python3 source.py --fixture\n")
        (self.run_dir / "stdout.log").write_text("")
        (self.run_dir / "stderr.log").write_text("")
        tar = b"sealed synthetic archive bytes"
        (self.run_dir / "diagnostic/raw.tar.gz").write_bytes(tar)
        self.receipt = {
            "schema": contract.DIAGNOSTIC_SCHEMA,
            "run_id": launch["run_id"], "trial_id": launch["trial_id"],
            "experiment_id": "EXP-ICPERF-123abc",
            "plan_sha256": launch["plan_sha256"],
            "launch_sha256": contract.digest(launch_bytes),
            "claim_owner": "executor-fixture", "claim_epoch": 1,
            "started_utc": "2026-10-19T00:00:00+00:00",
            "ended_utc": "2026-10-19T00:00:10+00:00",
            "raw_tar_sha256": contract.digest(tar),
            "cells": [
                {"cell": "monitor-null", "kind": "synthetic_null", "attempted": True,
                 "stop": "infrastructure_monitor_error",
                 "fault": {"code": "unreadable_live_root"}},
                {"cell": "coset-m2", "kind": "positive", "attempted": True,
                 "stop": "timeout_censored"},
                {"cell": "random-m2", "kind": "positive", "attempted": True,
                 "stop": "exited", "exit_code": 0,
                 "response_sha256": "d" * 64},
                {"cell": "small_x-m2", "kind": "positive", "attempted": True,
                 "stop": "timeout_censored"},
            ],
        }
        self.write_receipt()

    def write_receipt(self):
        (self.run_dir / "diagnostic/receipt.json").write_bytes(
            contract.canonical(self.receipt))

    def test_censored_and_canned_positive_have_complete_schema(self):
        raw_sha, manifest_sha = contract.write_outputs(self.run_dir)
        contract.verify_outputs(self.run_dir)
        self.assertEqual(raw_sha, contract.digest((self.run_dir / "raw-result.json").read_bytes()))
        self.assertEqual(manifest_sha, contract.digest((self.run_dir / "manifest.yaml").read_bytes()))
        raw = json.loads((self.run_dir / "raw-result.json").read_text())
        manifest = json.loads((self.run_dir / "manifest.yaml").read_text())
        self.assertEqual(raw["verification_status"], "pending_independent_checker")
        self.assertEqual(raw["cell_stops"]["random-m2"], "exited")
        self.assertEqual(manifest["run"]["result"]["positive_censored"], 2)
        self.assertEqual(manifest["run"]["result"]["certificate"], {"kind": "none"})
        self.assertEqual(experiment_execution.manifest_schema_errors(
            self.run_dir / "manifest.yaml"), [])
        with self.assertRaises(contract.ContractError):
            contract.write_outputs(self.run_dir)

    def test_missing_or_changed_output_rejected(self):
        contract.write_outputs(self.run_dir)
        (self.run_dir / "raw-result.json").write_text("{}\n")
        with self.assertRaisesRegex(contract.ContractError, "raw-result.json"):
            contract.verify_outputs(self.run_dir)

    def test_missing_archive_or_authority_rejected_before_output(self):
        (self.run_dir / "diagnostic/raw.tar.gz").unlink()
        with self.assertRaisesRegex(contract.ContractError, "archive"):
            contract.write_outputs(self.run_dir)
        (self.run_dir / "diagnostic/raw.tar.gz").write_bytes(b"sealed synthetic archive bytes")
        self.receipt["claim_epoch"] = 2
        self.write_receipt()
        with self.assertRaisesRegex(contract.ContractError, "authority"):
            contract.write_outputs(self.run_dir)
        self.assertFalse((self.run_dir / "manifest.yaml").exists())

    def test_integer_attempted_flag_is_rejected(self):
        self.receipt["cells"][1]["attempted"] = 1
        self.write_receipt()
        with self.assertRaisesRegex(contract.ContractError, "classification"):
            contract.write_outputs(self.run_dir)

    def test_unattempted_cell_needs_reason(self):
        self.receipt["cells"][-1] = {"cell": "small_x-m2", "kind": "positive",
                                      "attempted": False}
        self.write_receipt()
        with self.assertRaisesRegex(contract.ContractError, "reason"):
            contract.write_outputs(self.run_dir)

    def test_archived_invalid_run_is_read_only_fixture(self):
        archived = ROOT / "experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88"
        if not (archived / "diagnostic/receipt.json").is_file():
            self.skipTest("archived run is outside sparse checkout")
        # Derive in memory only. The historical run must retain its missing files.
        raw, manifest = contract.derive(archived)
        self.assertEqual(raw["run_id"], "RUN-ICPERF-eb0d88")
        self.assertEqual(manifest["run"]["result"]["positive_censored"], 3)
        self.assertFalse((archived / "manifest.yaml").exists())
        self.assertFalse((archived / "raw-result.json").exists())


    def test_archived_receipt_replays_into_validated_fixture(self):
        archived = ROOT / "experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88"
        if not (archived / "diagnostic/receipt.json").is_file():
            self.skipTest("archived run is outside sparse checkout")
        for name in ("launch.json", "environment.json", "command.txt",
                     "stdout.log", "stderr.log"):
            shutil.copyfile(archived / name, self.run_dir / name)
        for name in ("receipt.json", "raw.tar.gz"):
            shutil.copyfile(archived / "diagnostic" / name,
                            self.run_dir / "diagnostic" / name)
        contract.write_outputs(self.run_dir)
        contract.verify_outputs(self.run_dir)
        manifest = json.loads((self.run_dir / "manifest.yaml").read_text())
        self.assertEqual(manifest["run"]["result"]["positive_censored"], 3)
        self.assertEqual(experiment_execution.manifest_schema_errors(
            self.run_dir / "manifest.yaml"), [])
        self.assertFalse((archived / "manifest.yaml").exists())
        self.assertFalse((archived / "raw-result.json").exists())

    def test_nonzero_exit_is_infrastructure_and_requires_exit_code(self):
        self.receipt["cells"][2]["exit_code"] = 2
        self.write_receipt()
        contract.write_outputs(self.run_dir)
        manifest = json.loads((self.run_dir / "manifest.yaml").read_text())
        self.assertEqual(manifest["run"]["status"], "failed_infrastructure")
        (self.run_dir / "raw-result.json").unlink()
        (self.run_dir / "manifest.yaml").unlink()
        del self.receipt["cells"][2]["exit_code"]
        self.write_receipt()
        with self.assertRaisesRegex(contract.ContractError, "exit code"):
            contract.write_outputs(self.run_dir)


if __name__ == "__main__":
    unittest.main()
