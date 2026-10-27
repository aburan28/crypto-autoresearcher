"""Neutral parameter-sweep export checks; synthetic sources, no scientific runs."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("sweep_progress_metrics", Path(__file__).with_name("progress_metrics.py"))
pm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pm)
REPORT = "experiments/EXP-ECDLP-f50061/reports/run-20261027T2311Z/observations.json"
OLD_REF, NEW_REF = "a" * 40, "b" * 40


class ParameterSweepMetricsTests(unittest.TestCase):
    def document(self):
        # Synthetic counts differ from the experiment to detect hard-coded estimates.
        return {
            "schema": "classical.ecdlp.parameter-sweep.observations/v1",
            "recorded_at": "2026-10-27T23:11:00+00:00",
            "experiment_id": "EXP-ECDLP-f50061", "run_id": "RUN-ECDLP-e69a23",
            "protocol_sha256": "f882380374559faae1b50d86c1583c06c36738fc5dce43d2861fadaa6204b812",
            "public_equation_verification": "passed",
            "all_clocks_wall_valid": False, "native_counter_replay_verified": False,
            "completed_children": 12, "public_fixtures": 2, "public_target_ids": 8,
            "observed_target_arm_cases": 48, "verified_case_witnesses": 46,
            "censored_target_arm_cases": 2,
        }

    def capture(self, ref=OLD_REF, since="2026-10-01"):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            pm.endpoint_reuse_sweep_observations(ref, since)
        return [json.loads(line) for line in output.getvalue().splitlines()]

    def test_selected_committed_source_retains_censoring_and_neutral_ids(self):
        old = self.document()
        newer = copy.deepcopy(old)
        newer["completed_children"] = 99
        sources = {OLD_REF: json.dumps(old), NEW_REF: json.dumps(newer)}
        with mock.patch.object(pm, "show", side_effect=lambda ref, path: sources.get(ref) if path == REPORT else None) as show:
            rows = self.capture()
            show.assert_called_once_with(OLD_REF, REPORT)
            values = {row["metric"]: row["value"] for row in rows}
            expected = {"completed_children": 12, "public_fixtures": 2, "public_target_ids": 8,
                        "observed_target_arm_cases": 48, "verified_case_witnesses": 46,
                        "censored_target_arm_cases": 2}
            self.assertEqual(values, {"endpoint_reuse.e69a23." + key: value for key, value in expected.items()})
            self.assertTrue(all(row["source"] == REPORT + "@" + OLD_REF and row["better"] == "neutral"
                                and row["kind"] == "gauge" and row["date"] == "2026-10-27" for row in rows))
            newer_rows = self.capture(NEW_REF)
            self.assertEqual(next(row["value"] for row in newer_rows if row["metric"].endswith(".completed_children")), 99)
            self.assertEqual(self.capture(since="2026-10-28"), [])
        # A working-tree report cannot supply a missing committed source.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / REPORT
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(newer))
            with mock.patch.object(pm, "REPO", root), mock.patch.object(pm, "show", return_value=None) as show:
                self.assertEqual(self.capture(), [])
                show.assert_called_once_with(OLD_REF, REPORT)

    def test_incomplete_mismatched_or_unverified_sources_emit_no_estimates(self):
        invalid = [None, "{", "[]"]
        for field in self.document():
            data = self.document()
            del data[field]
            invalid.append(json.dumps(data))
        for field, value in (
            ("schema", "other/v1"), ("experiment_id", "EXP-ECDLP-other"),
            ("run_id", "RUN-ECDLP-other"), ("protocol_sha256", "0" * 64),
            ("public_equation_verification", False), ("public_equation_verification", "failed"),
            ("all_clocks_wall_valid", True), ("native_counter_replay_verified", True),
            ("recorded_at", "2026-99-99"), ("completed_children", True),
            ("public_fixtures", -1), ("public_target_ids", "8"),
            ("censored_target_arm_cases", None), ("observed_target_arm_cases", 46),
            ("verified_case_witnesses", 48),
        ):
            data = self.document()
            data[field] = value
            invalid.append(json.dumps(data))
        for source in invalid:
            with self.subTest(source=source), mock.patch.object(pm, "show", return_value=source):
                self.assertEqual(self.capture(), [])


if __name__ == "__main__":
    unittest.main()
