"""check_approval_capacity: a continuation of an approved contract that already
has runs is not a new approval.

The capacity rule exists to stop approvals that only add to the backlog of
approved-but-unrun contracts. Approving an amendment and continuation of a
contract that already has runs adds nothing to that backlog, so it is not
counted (user ruling 2026-10-09; DEC-20261009-ff58fe). Everything else about
the rule -- the cap, the enforcement date, the release keys and the message --
is pinned unchanged by the cases below. No repository file is read or written.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import validate_ledger                           # noqa: E402

UNRUN = ("EXP-TST-a00001", "EXP-TST-a00002", "EXP-TST-a00003", "EXP-TST-a00004")
WITH_RUNS = "EXP-TST-b00001"


class ApprovalCapacityContinuationTest(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        self.ctx = validate_ledger.Ctx(legacy_paths=set())
        for exp_id in UNRUN + (WITH_RUNS,):
            exp_dir = os.path.join(self.root, exp_id)
            os.makedirs(exp_dir)
            self.ctx.register(exp_id, os.path.join(exp_dir, "specification.yaml"),
                              {"id": exp_id, "status": "approved"}, "experiment")
        os.makedirs(os.path.join(self.root, WITH_RUNS, "runs", "RUN-TST-000001"))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _decide(self, dec_id: str, targets: list[str], **extra) -> list[str]:
        body = {"id": dec_id, "decision": "approve", "target_ids": targets, **extra}
        self.ctx.register(dec_id, os.path.join(self.root, f"{dec_id}.yaml"),
                          body, "coordinator_decision")
        validate_ledger.check_approval_capacity(self.ctx)
        return [e for e in self.ctx.errors if "approval capacity" in e]

    def test_t1_continuation_not_refused(self) -> None:
        self.assertEqual(self._decide("DEC-20261009-c00001", [WITH_RUNS]), [])

    def test_t2_new_approval_still_refused(self) -> None:
        errors = self._decide("DEC-20261009-c00002", ["EXP-TST-a00001"])
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("area:TST already holds 3 approved contract(s) with no run (cap 3)", errors[0])
        self.assertIn("EXP-TST-a00001", errors[0])

    def test_t3_release_keys_still_honoured(self) -> None:
        errors = self._decide("DEC-20261009-c00003", ["EXP-TST-a00001"],
                              withdraws_experiments=["EXP-TST-a00002"])
        self.assertEqual(errors, [])

    def test_t4_enforcement_date_unchanged(self) -> None:
        self.assertEqual(self._decide("DEC-20261006-c00004", ["EXP-TST-a00001"]), [])

    def test_t5_mixed_targets(self) -> None:
        errors = self._decide("DEC-20261009-c00005", [WITH_RUNS, "EXP-TST-a00001"])
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("EXP-TST-a00001", errors[0])
        self.assertNotIn(WITH_RUNS, errors[0])


if __name__ == "__main__":
    unittest.main()
