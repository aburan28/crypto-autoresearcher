#!/usr/bin/env python3
"""Regression tests for replay_strict.compare, including the counterexample from review of
PR 2425 (scientific fields whose names contain 'date' / 'dir', and tiny numeric values)."""
import sys, unittest, tempfile
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay_strict as R
import replay  # the historical normaliser, to show it was wrong


class T(unittest.TestCase):
    A = {"candidate_scalar": 7, "candidate_point": [1, 2], "direction": "above", "value": 1e-10}
    B = {"candidate_scalar": 19, "candidate_point": [3, 4], "direction": "below", "value": 2e-10}

    def test_historical_normaliser_was_wrong(self):
        self.assertEqual(replay.strip(self.A), replay.strip(self.B))  # the false equality

    def test_strict_detects_changed_candidate_data(self):
        d, bad = R.compare(self.A, self.B, [])
        self.assertEqual({x[0] for x in bad}, {"/candidate_scalar", "/candidate_point/0", "/candidate_point/1", "/direction", "/value"})

    def test_small_values_exact(self):
        d, bad = R.compare({"v": 1e-10}, {"v": 1.0000001e-10}, [])
        self.assertEqual(len(bad), 1)
        d, bad = R.compare({"v": 1e-10}, {"v": 1e-10}, [])
        self.assertEqual(bad, [])

    def test_int_float_and_bool_differ(self):
        self.assertEqual(len(R.compare({"v": 1}, {"v": 1.0}, [])[1]), 1)
        self.assertEqual(len(R.compare({"v": True}, {"v": 1}, [])[1]), 1)

    def test_allowlist_is_exact_path(self):
        old, new = {"environment": {"platform": "a"}, "candidate": {"platform": "a"}}, {"environment": {"platform": "b"}, "candidate": {"platform": "b"}}
        d, bad = R.compare(old, new, ["/environment/platform"])
        self.assertEqual([x[0] for x in bad], ["/candidate/platform"])

    def test_wildcard_one_segment_only(self):
        d, bad = R.compare({"t": {"a": {"s": 1}}}, {"t": {"a": {"s": 2}}}, ["/t/*"])
        self.assertEqual(len(bad), 1)  # /t/a/s has two segments under t; '*' matches one
        d, bad = R.compare({"t": {"a": 1}}, {"t": {"a": 2}}, ["/t/*"])
        self.assertEqual(bad, [])

    def test_length_and_absent_keys(self):
        self.assertEqual(len(R.compare({"l": [1, 2]}, {"l": [1]}, [])[1]), 1)
        self.assertEqual(len(R.compare({"a": 1}, {"a": 1, "b": 2}, [])[1]), 1)

    def test_literal_slash_key_does_not_alias_nested_metadata(self):
        old, new = {"environment/platform": "a"}, {"environment/platform": "b"}
        self.assertEqual(R.compare(old, new, ["/environment/platform"])[1],
                         [("/environment~1platform", "a", "b")])
        self.assertEqual(R.compare(old, new, ["/environment~1platform"])[1], [])

    def test_tilde_and_trailing_slash_keys_are_distinct(self):
        old, new = {"t~1": 1, "platform/": 1}, {"t~1": 2, "platform/": 2}
        self.assertEqual(len(R.compare(old, new, ["/t/", "/platform"])[1]), 2)
        self.assertEqual(R.compare(old, new, ["/t~01", "/platform~1"])[1], [])

    def test_missing_allowlisted_metadata_is_not_excused(self):
        self.assertEqual(len(R.compare({"elapsed": 1}, {}, ["/elapsed"])[1]), 1)

    def test_allowlisted_container_loss_and_type_change_are_not_excused(self):
        old = {"timings": {"scientific": 7}}
        self.assertEqual(len(R.compare(old, {}, ["/timings"])[1]), 1)
        self.assertEqual(len(R.compare(old, {"timings": 0}, ["/timings"])[1]), 1)

    def test_nonfinite_and_unsupported_values_are_refused(self):
        for value in (float("inf"), float("-inf"), float("nan"), {1, 2}):
            with self.assertRaises(ValueError):
                R.compare({"value": value}, {"value": value}, ["/value"])

    def test_artifact_agreement_does_not_certify_complete_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "command.txt").write_text("python3 fixture.py\n")
            wt = root / "wt"
            wt.mkdir()
            (wt / "output.json").write_text('{"value": 7}\n')

            def completed(argv, **kwargs):
                out = ""
                if "status" in argv:
                    out = " M output.json\n"
                elif "show" in argv:
                    out = '{"value": 7}\n'
                elif "rev-parse" in argv:
                    out = "fixed-fixture-head\n"
                return SimpleNamespace(returncode=0, stdout=out, stderr="")

            with patch.object(R, "REPO", root), patch.object(R, "PAIRS", root / "pairs"), \
                    patch.object(R.subprocess, "run", side_effect=completed):
                result = R.run_one(str(wt), "FIXTURE", {
                    "FIXTURE": {"replay_command_file": "command.txt"}}, {}, False)
            self.assertEqual(result["status"], "artifact_comparison_pass")
            self.assertFalse(result["execution_certified"])
            self.assertIn("expected output inventory not certified", result["comparison_scope"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
