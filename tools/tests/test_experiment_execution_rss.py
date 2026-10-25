"""Focused macOS process-monitor transition checks."""

import unittest
from unittest import mock

from tools import experiment_execution as execution


class DarwinRssTransitionTests(unittest.TestCase):
    def setUp(self):
        self.process = mock.Mock()
        self.process.pid = 12345

    def test_transient_unreadable_group_recovers(self):
        self.process.poll.return_value = None
        with mock.patch.object(execution, "darwin_group_rss_bytes", side_effect=[
            execution.ExecutionError("transient process exit"), 4096,
        ]) as sample, mock.patch.object(execution.time, "sleep"):
            self.assertEqual(execution.read_darwin_rss_during_transition(self.process), 4096)
        self.assertEqual(sample.call_count, 2)

    def test_leader_exit_during_unreadable_group(self):
        self.process.poll.return_value = 0
        with mock.patch.object(execution, "darwin_group_rss_bytes",
                               side_effect=execution.ExecutionError("process exited")):
            self.assertIsNone(execution.read_darwin_rss_during_transition(self.process))

    def test_persistent_monitor_loss_fails_closed(self):
        self.process.poll.return_value = None
        with mock.patch.object(execution, "darwin_group_rss_bytes",
                               side_effect=execution.ExecutionError("persistent loss")), \
             mock.patch.object(execution.time, "monotonic", side_effect=[0.0, 0.06]), \
             mock.patch.object(execution.time, "sleep"):
            with self.assertRaisesRegex(execution.ExecutionError, "persistent loss"):
                execution.read_darwin_rss_during_transition(self.process, grace_seconds=0.05)


class InvalidOutputStopTests(unittest.TestCase):
    def run_fixture(self, stop_on_invalid_output):
        root = execution.Path("/tmp/ectd-stop-control")
        path = root / "experiments/EXP-ECTD-stop-control/trial-plan.json"
        plan = {
            "task_id": "TASK-20261023-a1b2c3",
            "stop_on_invalid_output": stop_on_invalid_output,
            "trials": [{"id": "first"}, {"id": "second"}],
        }
        report = {"trials": {"first": "planned", "second": "planned"}}
        gate = mock.Mock(return_value={"owner": "control"})
        with mock.patch.object(execution, "load_plan", return_value=plan), \
             mock.patch.object(execution, "materialized"), \
             mock.patch.object(execution, "task_lock", return_value=mock.MagicMock()), \
             mock.patch.object(execution, "coverage", return_value=report), \
             mock.patch.object(execution, "sha256", return_value="fixed-plan-digest"), \
             mock.patch.object(execution, "execute_trial",
                               side_effect=["invalid_output", "output_validated"]) as execute:
            execution.run_plan(root, path, owner="control", epoch=1, gate=gate)
        return execute.call_count

    def test_integrity_failure_stops_when_frozen_plan_requires_it(self):
        self.assertEqual(self.run_fixture(True), 1)

    def test_legacy_plan_keeps_existing_continue_behavior(self):
        self.assertEqual(self.run_fixture(False), 2)


if __name__ == "__main__":
    unittest.main()
