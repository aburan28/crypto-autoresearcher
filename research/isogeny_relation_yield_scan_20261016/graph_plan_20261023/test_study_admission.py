"""Admission boundary controls; no fixture here launches a scientific run."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from study_admission import (require_discovery_stage, validate_approval_fields,
                             verify_study_admission, ROOT)


def rejects_before_execution(value: dict) -> None:
    with tempfile.TemporaryDirectory(prefix="ectd-admission-boundary-") as tmp:
        path = Path(tmp) / "admission.json"
        path.write_text(json.dumps(value))
        try:
            verify_study_admission(path, Path(tmp) / "binding.json",
                                   SimpleNamespace(), {}, {}, lambda *_: None)
        except (ValueError, KeyError):
            return
        raise AssertionError("unapproved or malformed study admission passed")


class AdmissionBoundaryTests(unittest.TestCase):
    def test_unapproved_and_non_coordinator_admissions_are_rejected(self):
        rejects_before_execution({"schema": "ectd.graph-study-admission.v1",
                                  "status": "candidate_unapproved",
                                  "experiment_id": "EXP-ECTD-abcdef"})
        rejects_before_execution({"schema": "ectd.graph-study-admission.v1",
                                  "status": "approved",
                                  "approved_by": "executor",
                                  "experiment_id": "EXP-ECTD-abcdef"})
        rejects_before_execution({"schema": "ectd.graph-study-admission.v0",
                                  "status": "approved",
                                  "approved_by": "coordinator",
                                  "experiment_id": "EXP-ECTD-abcdef"})

    def test_decision_and_execution_stage_are_bound(self):
        admission = {"experiment_id": "EXP-ECTD-abcdef", "decision_id": "DEC-20261023-a1b2c3",
                     "execution_stage": 0}
        decision = {"coordinator_decision": {
            "id": "DEC-20261023-a1b2c3", "decided_by": "coordinator",
            "decision": "approve", "mode": "design_experiment_approval",
            "approved_by": "DEC-20261023-a1b2c3", "target_ids": ["EXP-ECTD-abcdef"],
            "official_transitions": {"execution_authorized_stages": [0]}}}
        specification = {"experiment": {
            "id": "EXP-ECTD-abcdef", "status": "approved",
            "approved_by": "DEC-20261023-a1b2c3", "frozen": True,
            "execution_authorized": True, "execution_authorized_stages": [0]}}
        self.assertEqual(validate_approval_fields(admission, decision, specification)[2], 0)
        self.assertEqual(require_discovery_stage(admission), 0)
        later_admission = {**admission, "execution_stage": 1}
        later_decision = {"coordinator_decision": {
            **decision["coordinator_decision"],
            "official_transitions": {"execution_authorized_stages": [1]}}}
        later_specification = {"experiment": {
            **specification["experiment"], "execution_authorized_stages": [1]}}
        self.assertEqual(validate_approval_fields(
            later_admission, later_decision, later_specification)[2], 1)
        with self.assertRaisesRegex(ValueError, "requires execution_stage 0"):
            require_discovery_stage(later_admission)
        for bad_admission, bad_decision, bad_spec in (
            ({**admission, "execution_stage": True}, decision, specification),
            (admission, {"coordinator_decision": {**decision["coordinator_decision"],
                                                   "decided_by": "executor"}}, specification),
            (admission, decision, {"experiment": {**specification["experiment"],
                                                   "execution_authorized": False}}),
            (admission, {"coordinator_decision": {**decision["coordinator_decision"],
                                                   "official_transitions": {"execution_authorized_stages": [1]}}},
             specification)):
            with self.subTest(admission=bad_admission, decision=bad_decision,
                              specification=bad_spec):
                with self.assertRaises((ValueError, TypeError, AttributeError)):
                    validate_approval_fields(bad_admission, bad_decision, bad_spec)

    def test_discovery_admission_rejects_valid_later_stage_approval(self):
        experiment_id = "EXP-ECTD-abcdef"
        decision_id = "DEC-20261023-a1b2c3"
        decision = {"coordinator_decision": {
            "id": decision_id, "decided_by": "coordinator", "decision": "approve",
            "mode": "design_experiment_approval", "approved_by": decision_id,
            "target_ids": [experiment_id],
            "official_transitions": {"execution_authorized_stages": [1]}}}
        specification = {"experiment": {
            "id": experiment_id, "status": "approved", "approved_by": decision_id,
            "frozen": True, "execution_authorized": True,
            "execution_authorized_stages": [1]}}
        with tempfile.TemporaryDirectory(prefix="ectd-stage-boundary-",
                                         dir=ROOT / "experiments") as tmp:
            directory = Path(tmp)
            decision_path = directory / "decision.yaml"
            specification_path = directory / "specification.yaml"
            decision_path.write_text(json.dumps(decision))
            specification_path.write_text(json.dumps(specification))
            admission = {
                "schema": "ectd.graph-study-admission.v1", "status": "approved",
                "approved_by": "coordinator", "experiment_id": experiment_id,
                "decision_id": decision_id, "execution_stage": 1,
                "decision_path": decision_path.relative_to(ROOT).as_posix(),
                "decision_sha256": hashlib.sha256(decision_path.read_bytes()).hexdigest(),
                "specification_path": specification_path.relative_to(ROOT).as_posix(),
                "specification_sha256": hashlib.sha256(
                    specification_path.read_bytes()).hexdigest(),
            }
            admission_path = directory / "admission.json"
            admission_path.write_text(json.dumps(admission))
            with self.assertRaisesRegex(ValueError, "requires execution_stage 0"):
                verify_study_admission(
                    admission_path, directory / "binding.json", SimpleNamespace(),
                    {}, {}, lambda *_: self.fail("source check must follow stage gate"))


def main() -> None:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AdmissionBoundaryTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(json.dumps({"schema": "ectd.study-admission-boundary-control.v1",
                      "status": "pass", "test_count": result.testsRun,
                      "scientific_launches": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
