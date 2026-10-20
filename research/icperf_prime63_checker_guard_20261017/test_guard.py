"""Focused regression for a unit-ideal contradiction on a planted control."""
from __future__ import annotations

import unittest
from unittest.mock import patch

import guard
from test_inflight import InflightControls


class PositiveContradictionGuard(unittest.TestCase):
    def fixture(self, response: dict):
        old = InflightControls(methodName="test_censored_positive_and_forged_ok")
        old.setUp()
        self.addCleanup(old.doCleanups)
        panel, rows, witnesses = old.panel_fixture(response)
        return old, rows, witnesses

    def test_unit_ideal_positive_is_invalid(self):
        old, rows, witnesses = self.fixture({"status": "certified_no_solution",
                                             "roots": [],
                                             "certificate": "Groebner basis contains 1"})
        with patch.object(guard.execute, "OLD", witnesses):
            archived_checker = guard.check.verify(
                old.run_dir, old.plan_path, old.owner, old.epoch, old.trial_id,
                root=old.root, rows=rows)
            self.assertEqual(archived_checker["positive_controls_censored"], 1)
            with self.assertRaisesRegex(ValueError, "planted positive contradiction"):
                guard.verify(old.run_dir, old.plan_path, old.owner, old.epoch,
                             old.trial_id, root=old.root, rows=rows)

    def test_model_cap_positive_stays_censored(self):
        old, rows, witnesses = self.fixture({"status": "model_cap_censored",
                                             "roots": [], "variety_called": False})
        with patch.object(guard.execute, "OLD", witnesses):
            result = guard.verify(old.run_dir, old.plan_path, old.owner,
                                  old.epoch, old.trial_id, root=old.root, rows=rows)
        self.assertEqual(result["positive_controls_censored"], 1)
        self.assertEqual(result["positive_controls_verified"], 0)


if __name__ == "__main__":
    unittest.main()
