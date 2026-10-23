"""Admission boundary controls; no fixture here launches a scientific run."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from study_admission import validate_approval_fields, verify_study_admission


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
