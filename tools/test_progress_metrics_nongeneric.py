"""One synthetic-source regression for fixed-screen neutral progress exports."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("ng_progress_metrics", Path(__file__).with_name("progress_metrics.py"))
pm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pm)
REPORT = "experiments/EXP-ECDLP-c45dd8/reports/run-20261027T2329Z/observations.json"


class NongenericMetricsTests(unittest.TestCase):
    def capture(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            pm.nongeneric_screen_observations("a" * 40, "2026-10-01")
        return [json.loads(line) for line in output.getvalue().splitlines()]

    def test_committed_neutral_counts_keep_repeated_views_and_refuse_missing_or_mismatched_sources(self):
        # Synthetic values detect hard-coded experiment counts; no scientific execution.
        document = {"schema": "classical.ecdlp.nongeneric-screen.observations/v1",
                    "recorded_at": "2026-10-27T23:29:00+00:00",
                    "experiment_id": "EXP-ECDLP-c45dd8", "run_id": "RUN-ECDLP-a11661",
                    "protocol_sha256": "31d6425d88c3217ddab47fe3fbc295a6ec6b0af3513942f0fc2a9156ccea7d3d",
                    "verification_status": "passed", "all_clocks_wall_valid": False,
                    "candidate_counter_execution_replayed": False,
                    "observed_cases": 48, "candidate_cases": 40, "control_cases": 8,
                    "passing_groups": 2, "templates_with_passing_groups": 1,
                    "verified_recovered_targets": 26, "fresh_predicate_evaluations": 130}
        with mock.patch.object(pm, "show", return_value=json.dumps(document)) as show:
            rows = self.capture()
            show.assert_called_once_with("a" * 40, REPORT)
        counts = {key: value for key, value in document.items() if type(value) is int}
        self.assertEqual({row["metric"]: row["value"] for row in rows},
                         {"nongeneric.a11661." + key: value for key, value in counts.items()})
        self.assertTrue(all(row["better"] == "neutral" and row["kind"] == "gauge"
                            and row["source"] == REPORT + "@" + "a" * 40 for row in rows))
        recovered = next(row for row in rows if row["metric"].endswith(".verified_recovered_targets"))
        self.assertIn("repeated coordinate views", recovered["label"])
        bad = [None, "{}", "[]"]
        for key, value in (("protocol_sha256", "0" * 64), ("run_id", "RUN-ECDLP-other"),
                           ("verification_status", False), ("candidate_counter_execution_replayed", True),
                           ("all_clocks_wall_valid", True), ("candidate_cases", True),
                           ("observed_cases", 47), ("templates_with_passing_groups", 41)):
            bad.append(json.dumps({**document, key: value}))
        for key in counts:
            bad.append(json.dumps({name: value for name, value in document.items() if name != key}))
        for source in bad:
            with self.subTest(source=source), mock.patch.object(pm, "show", return_value=source):
                self.assertEqual(self.capture(), [])


if __name__ == "__main__":
    unittest.main()
