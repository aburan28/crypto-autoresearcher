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


if __name__ == "__main__":
    unittest.main()
