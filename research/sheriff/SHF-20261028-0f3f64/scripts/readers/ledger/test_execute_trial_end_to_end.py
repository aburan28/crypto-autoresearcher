#!/usr/bin/env python3
"""End-to-end probes of the completion gate through execute_trial(), reusing
the temp-dir harness of tests/test_experiment_execution.py (fixture driver,
temporary git repo; no scientific trial, nothing written in the repository).

Sheriff case SHF-20261028-0f3f64, B7 ledger reader. argv[1] = JSON output path.

E1  manifest.yaml declared in allow_empty_artifacts and written as 0 bytes:
    complete_manifest() is skipped (size 0) and check_run() reports nothing for
    a document that loads as None. Does the trial reach output_validated?
E2  a partial envelope whose task_id and inputs.seed contradict the plan:
    is it refused, or completed and validated?
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(REPO / "tests"))
import test_experiment_execution as T  # noqa: E402

execution = T.execution
EXTRA = '''if kind == "contra":  # partial envelope contradicting the plan off the id fields
    manifest = {"run": {"experiment_id": p.parent.parent.name, "run_id": p.name,
                        "attack_claimed": False, "metrics": {"planted_ok": True},
                        "task_id": "TASK-20990101-ffffff", "inputs": {"seed": 999},
                        "code": {"commit": "f" * 40}}}
if kind == "bad_code":'''
assert 'if kind == "bad_code":' in T.DRIVER
T.DRIVER = T.DRIVER.replace('if kind == "bad_code":', EXTRA, 1)
OUT: dict = {}


class Reader(T.ExecutionTests):
    def test_r_empty_manifest_allowed_empty(self):
        trial = self.trial(70, "empty_manifest")
        trial["allow_empty_artifacts"] = ["manifest.yaml"]
        self.plan["trials"] = [trial]
        self.write_plan_queue(); self.commit()
        report = self.run_plan()
        receipt = execution.read_json(self.directory() / "execution-receipt.json")
        manifest = self.directory() / "manifest.yaml"
        OUT["E1_empty_manifest_allowed_empty"] = {
            "status": receipt["status"], "check_returncode": receipt["check_returncode"],
            "manifest_completion": receipt["manifest_completion"],
            "manifest_size": manifest.stat().st_size,
            "output_validated": report.get("output_validated"),
            "measurement_complete": report.get("measurement_complete"),
            "coverage": execution.coverage(self.root, self.path)["trials"][trial["id"]],
            "gate_held": receipt["status"] != "output_validated"}

    def test_r_contradicting_partial_envelope(self):
        self.plan["trials"] = [self.trial(71, "contra")]
        self.plan["trials"][0]["seed"] = 1
        self.write_plan_queue(); self.commit()
        report = self.run_plan()
        receipt = execution.read_json(self.directory() / "execution-receipt.json")
        run = execution.yaml.safe_load((self.directory() / "manifest.yaml").read_text())["run"]
        OUT["E2_contradicting_partial_envelope"] = {
            "plan_task_id": self.plan["task_id"], "plan_seed": 1,
            "authority_commit": receipt["authority"]["commit"],
            "status": receipt["status"], "detail": receipt["detail"],
            "completion_action": (receipt["manifest_completion"] or {}).get("action"),
            "published_task_id": run.get("task_id"),
            "published_inputs": run.get("inputs"),
            "published_code_commit": run.get("code", {}).get("commit"),
            "refused": receipt["status"] == "invalid_output"}


def main():
    suite = unittest.TestSuite([Reader("test_r_empty_manifest_allowed_empty"),
                                Reader("test_r_contradicting_partial_envelope")])
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    OUT["unittest"] = {"run": result.testsRun, "errors": [str(e[1]) for e in result.errors],
                       "failures": [str(f[1]) for f in result.failures]}
    Path(sys.argv[1]).write_text(json.dumps(OUT, indent=2, default=str) + "\n")
    print(json.dumps(OUT, indent=2, default=str))


if __name__ == "__main__":
    main()
