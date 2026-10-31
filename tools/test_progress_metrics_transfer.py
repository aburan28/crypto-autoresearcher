"""Synthetic committed-source regression; no transfer trial or verifier execution."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("transfer_progress_metrics", Path(__file__).with_name("progress_metrics.py"))
pm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pm)
REPORT = "experiments/EXP-ECDLP-8dc19d/reports/run-20261028T1728Z/observations.json"


class TransferMetricsTests(unittest.TestCase):
    def capture(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            pm.transfer_study_observations("a" * 40, "2026-10-28")
        return [json.loads(line) for line in output.getvalue().splitlines()]

    def test_committed_neutral_events_and_unique_pairs_are_distinct_without_missing_defaults(self):
        # Synthetic counts differ from the experiment, detecting hard-coded workloads.
        document = {"schema": "classical.ecdlp.transfer-study.observations/v1",
                    "experiment_id": "EXP-ECDLP-8dc19d", "run_id": "RUN-ECDLP-994f70",
                    "protocol_sha256": "fa961d179668d86e1dfcdc393d80c60e4f6a6f3ac541b9015f6011beba050c71",
                    "recorded_at": "2026-10-28T01:00:00+00:00", "verification_status": "passed",
                    "cohort_complete": True, "all_clocks_wall_valid": False, "counter_execution_replayed": False,
                    "fresh_curves": 2, "target_ids": 3, "attempt_rows": 123, "checked_attempt_rows": 123,
                    "working_baseline_verified_target_ids": 3, "candidate_success_events": 6,
                    "unique_target_arm_pairs_recovered": 4}
        with mock.patch.object(pm, "show", return_value=json.dumps(document)) as show:
            rows = self.capture()
            show.assert_called_once_with("a" * 40, REPORT)
        counts = {name: value for name, value in document.items() if type(value) is int}
        self.assertEqual({row["metric"]: row["value"] for row in rows},
                         {"transfer.994f70." + name: value for name, value in counts.items()})
        self.assertTrue(all(row["better"] == "neutral" and row["kind"] == "gauge"
                            and row["source"] == REPORT + "@" + "a" * 40 for row in rows))
        bad = [None, "{}", "[]"]
        for key, value in (("experiment_id", "EXP-ECDLP-ef7323"), ("run_id", "RUN-ECDLP-ea5986"),
                           ("protocol_sha256", "0" * 64), ("cohort_complete", False),
                           ("verification_status", False), ("all_clocks_wall_valid", True),
                           ("counter_execution_replayed", True), ("candidate_success_events", None),
                           ("fresh_curves", True), ("checked_attempt_rows", 124),
                           ("working_baseline_verified_target_ids", 4), ("unique_target_arm_pairs_recovered", 7)):
            bad.append(json.dumps({**document, key: value}))
        bad += [json.dumps({key: value for key, value in document.items() if key != name}) for name in counts]
        for source in bad:
            with self.subTest(source=source), mock.patch.object(pm, "show", return_value=source):
                self.assertEqual(self.capture(), [])
        with mock.patch.object(pm, "show", return_value=json.dumps({**document, "candidate_success_events": 0,
                                                                    "unique_target_arm_pairs_recovered": 0})):
            zeros = {row["metric"]: row["value"] for row in self.capture()}
            self.assertEqual(zeros["transfer.994f70.candidate_success_events"], 0)


if __name__ == "__main__":
    unittest.main()
