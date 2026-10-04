"""Synthetic software controls; these are not Frobenius experiment results."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from frobenius_rank_diagnostics import audit_metrics


def fixture(u=4, same=1, all_rank=2, accepted=8, mixed=4, t=2):
    return {"cells": [{"id": "object", "status": "completed", "N": 31, "cover_count": 1}],
            "covers": [{"cell": "object", "cover": "1,2", "t": t,
                        "ordered_pairs": 100, "unique_single_base_pairs": 40,
                        "accepted_pairs": accepted, "mixed_accepted_pairs": mixed,
                        "same_base_accepted_pairs": accepted - mixed,
                        "presentations": {"frobenius_negation": {
                            "U": u, "same_rank": same, "all_rank": all_rank,
                            "Delta_rank": all_rank - same, "rank_deficit": u - all_rank}}}]}


class DiagnosticsTests(unittest.TestCase):
    def row(self, **kwargs):
        return audit_metrics(fixture(**kwargs))["presentations"][0]

    def test_positive_gain_and_exact_cost(self):
        row = self.row(all_rank=3)
        self.assertEqual(row["diagnosis"], "mixed_span_gain")
        self.assertEqual(row["all_pairs_per_added_dimension"], {"numerator": 50, "denominator": 1})
        self.assertEqual(row["extra_pairs_per_added_dimension"], {"numerator": 30, "denominator": 1})
        self.assertEqual(row["ambient_headroom_after_mixing"], 0)

    def test_saturation_is_not_a_refutation(self):
        row = self.row(u=3, same=2, all_rank=2)
        self.assertEqual(row["diagnosis"], "ambient_rank_saturated")
        self.assertIsNone(row["all_pairs_per_added_dimension"])

    def test_no_relations_with_headroom(self):
        row = self.row(u=2, same=0, all_rank=0, accepted=0, mixed=0)
        self.assertEqual(row["diagnosis"], "no_relations")
        self.assertEqual(row["ambient_headroom_before_mixing"], 1)

    def test_no_mixed_relations(self):
        self.assertEqual(self.row(all_rank=1, mixed=0)["diagnosis"], "no_mixed_relations")

    def test_dependent_mixed_relations(self):
        self.assertEqual(self.row(all_rank=1)["diagnosis"], "mixed_rows_add_no_rank")

    def test_single_base_control(self):
        self.assertEqual(self.row(all_rank=1, mixed=0, t=1)["diagnosis"], "single_base_control")

    def test_empty_presentation(self):
        self.assertEqual(self.row(u=0, same=0, all_rank=0, accepted=0, mixed=0)["diagnosis"], "empty_presentation")

    def test_incomplete_panel_is_preserved(self):
        data = fixture()
        data["cells"].append({"id": "missing", "status": "ineligible_object", "reason": "pool_exhausted"})
        panel = audit_metrics(data)["panel"]
        self.assertEqual((panel["planned_cells"], panel["completed_cells"]), (2, 1))
        self.assertEqual(panel["incomplete_cells"][0]["reason"], "pool_exhausted")

    def test_invalid_rank_and_integer_fields(self):
        for key, value in [("all_rank", 4), ("Delta_rank", 9), ("U", True), ("same_rank", 1.0), ("rank_deficit", -1)]:
            with self.subTest(key=key, value=value):
                data = fixture()
                data["covers"][0]["presentations"]["frobenius_negation"][key] = value
                with self.assertRaises(ValueError):
                    audit_metrics(data)

    def test_duplicate_and_missing_cover(self):
        data = fixture()
        data["covers"].append(copy.deepcopy(data["covers"][0]))
        with self.assertRaises(ValueError):
            audit_metrics(data)
        data = fixture()
        data["covers"] = []
        with self.assertRaises(ValueError):
            audit_metrics(data)

    def test_unknown_or_incomplete_cell(self):
        for status in [None, "ineligible_object"]:
            data = fixture()
            if status is None:
                data["covers"][0]["cell"] = "missing"
            else:
                data["cells"][0]["status"] = status
            with self.assertRaises(ValueError):
                audit_metrics(data)

    def test_inconsistent_pair_counts(self):
        data = fixture()
        data["covers"][0]["accepted_pairs"] = 99
        with self.assertRaises(ValueError):
            audit_metrics(data)

    def test_cli_hash_binding_and_no_overwrite(self):
        script = Path(__file__).with_name("frobenius_rank_diagnostics.py")
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "metrics.json", Path(directory) / "diagnostic.json"
            raw = json.dumps(fixture()).encode()
            source.write_bytes(raw)
            command = [sys.executable, str(script), str(source), "--expected-sha256", hashlib.sha256(raw).hexdigest(), "--output", str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            saved = output.read_bytes()
            self.assertEqual(json.loads(saved)["source"]["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(output.read_bytes(), saved)
            output.unlink()
            source.write_bytes(raw + b" ")
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
