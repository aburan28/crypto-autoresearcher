"""Presentation behavior and saved-data transcription; no scientific trial."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "observation_check", ROOT / "tools/check_experiment_observation.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
EXAMPLE = ROOT / "templates/examples/rotation-observation.yaml"
RAW = ROOT / "experiments/EXP-ECDLP-ad27ad/runs/RUN-ECDLP-a5281a/raw-result.json"


class ObservationPresentationTests(unittest.TestCase):
    def setUp(self):
        self.example = CHECK.load(EXAMPLE)

    def test_empty_snapshot_is_valid_without_an_anomaly(self):
        CHECK.check(CHECK.load(ROOT / "templates/experiment-observation.yaml"))

    def test_real_example_preserves_literal_status_and_counts(self):
        CHECK.check(self.example)
        self.assertEqual(self.example["runs"][0]["native_status"], "invalid_output")
        self.assertEqual(self.example["observations"][3]["value"],
                         {"returncode": 0, "check_returncode": 0})
        self.assertEqual(self.example["observations"][0]["value"][0]["hits"], 45917)

    def test_censored_and_failed_outcomes_can_remain_uninterpreted(self):
        record = copy.deepcopy(self.example)
        record["patterns"] = []
        observation = record["observations"][0]
        observation["value"] = {"completed": 0, "timeout": 9,
                                "infrastructure_error": 1, "elapsed_seconds": None}
        observation["unit"] = "attempt outcomes; duration was not recorded"
        observation["sample"] = {"n": 10, "unit": "attempt", "dependence": "unknown"}
        record["missing"].append({"field": "/observations/0/value/elapsed_seconds",
                                   "reason": "No duration measurement was saved."})
        CHECK.check(record)
        self.assertIsNone(observation["value"]["elapsed_seconds"])

    def test_missing_uncertainty_is_rejected(self):
        del self.example["observations"][0]["uncertainty"]
        with self.assertRaises(jsonschema.ValidationError):
            CHECK.check(self.example)

    def test_flag_needs_a_reference(self):
        self.example["patterns"][0]["reference_ids"] = []
        with self.assertRaises(jsonschema.ValidationError):
            CHECK.check(self.example)

    def test_flag_needs_a_concrete_proposed_next_check(self):
        self.example["next_checks"] = []
        with self.assertRaises(jsonschema.ValidationError):
            CHECK.check(self.example)

    def test_unavailable_native_status_can_be_reported_without_guessing(self):
        self.example["runs"][0]["native_status"] = None
        self.example["missing"].append({"field": "/runs/0/native_status",
                                        "reason": "Fixture simulates a missing receipt status."})
        CHECK.check(self.example)

    def test_unknown_references_are_rejected(self):
        for group, key in (("controls", "observation_ids"),
                           ("patterns", "reference_ids")):
            with self.subTest(group=group):
                record = copy.deepcopy(self.example)
                record[group][0][key] = ["nonexistent"]
                with self.assertRaisesRegex(ValueError, "unknown .*reference"):
                    CHECK.check(record)

    def test_unknown_evidence_is_rejected(self):
        self.example["observations"][0]["evidence"][0]["artifact"] = "nonexistent"
        with self.assertRaisesRegex(ValueError, "unknown evidence"):
            CHECK.check(self.example)

    def test_duplicate_ids_are_rejected(self):
        self.example["observations"].append(copy.deepcopy(self.example["observations"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate ID"):
            CHECK.check(self.example)

    def test_null_requires_a_reason(self):
        self.example["missing"] = []
        with self.assertRaisesRegex(ValueError, "null values need"):
            CHECK.check(self.example)

    def test_missing_reason_cannot_point_to_an_available_value(self):
        self.example["missing"].append({"field": "/question", "reason": "wrong path"})
        with self.assertRaisesRegex(ValueError, "must name null fields"):
            CHECK.check(self.example)

    def test_yaml_ambiguities_are_rejected(self):
        for content in ("x: 1\nx: 2\n", "1: value\n", "x: .nan\n",
                        "x: .inf\n", "x: 2026-10-18\n",
                        "x: &x {a: 1}\ny: {<<: *x}\n"):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "bad.yaml"
                path.write_text(content)
                with self.assertRaises((ValueError, TypeError)):
                    CHECK.load(path)

    def test_arbitrary_measurement_key_is_not_treated_as_an_evidence_link(self):
        self.example["observations"][0]["value"] = {"evidence": 123}
        CHECK.check(self.example)

    def test_artifact_checks_detect_tampering_and_unavailable_files(self):
        record = CHECK.load(ROOT / "templates/experiment-observation.yaml")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.txt"
            path.write_bytes(b"saved data\n")
            record["artifacts"] = [{"id": "data", "path": "data.txt", "commit": "a"*40,
                                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}]
            CHECK.check(record, tmp)
            path.write_bytes(b"changed data\n")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                CHECK.check(record, tmp)
            path.unlink()
            with self.assertRaisesRegex(ValueError, "unavailable locally"):
                CHECK.check(record, tmp)
            # Shape-only mode never reads/fetches artifacts.
            CHECK.check(record)

    def test_paths_cannot_escape_repository(self):
        for path in ("../outside", "/tmp/outside"):
            with self.subTest(path=path):
                self.example["artifacts"][0]["path"] = path
                with self.assertRaisesRegex(ValueError, "repository-relative"):
                    CHECK.check(self.example)

    @unittest.skipUnless(RAW.is_file(), "source absent from sparse checkout")
    def test_example_counts_reaggregate_the_actual_saved_rows(self):
        raw = json.loads(RAW.read_text())
        for index, arm in ((0, "rot"), (1, "hash")):
            for row in self.example["observations"][index]["value"]:
                cells = [x for x in raw["cells"] if x["c"] == row["c"] and x["m"] == 4]
                self.assertEqual(len(cells), row["cells"])
                hits = sum(x[arm]["density_hits"] for x in cells)
                draws = sum(x[arm]["density_n"] for x in cells)
                self.assertEqual((hits, draws), (row["hits"], row["draws"]))
                self.assertEqual(hits / draws, row["density"])


if __name__ == "__main__":
    unittest.main()
