"""Pure controls for the candidate confirmation analysis."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).with_name("confirm.py")
spec = importlib.util.spec_from_file_location("graph_confirm", MODULE)
assert spec and spec.loader
confirm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(confirm)


class ConfirmationControls(unittest.TestCase):
    def test_graph_commitments_are_stage_and_stratum_specific(self):
        def row(stratum, target, commitment):
            return {"stratum": stratum, "base_root_sha256": "b" * 64,
                    "target_root_sha256": target * 64,
                    "verifier_root_sha256": "v" * 64,
                    "commitment_sha256": commitment * 64}
        discovery = [row("P29", "d", "1"), row("P29", "d", "1"),
                     row("P37", "d", "2")]
        confirmation = [row("P29", "c", "3"), row("P29", "c", "3"),
                        row("P37", "c", "4")]
        selection = {"strata": {"P29": {"commitment_sha256": "1" * 64},
                                 "P37": {"commitment_sha256": "2" * 64}}}
        confirm.check_stage_roots(confirmation, discovery, selection)
        changed = [dict(item) for item in confirmation]
        changed[1]["commitment_sha256"] = "5" * 64
        with self.assertRaisesRegex(ValueError, "graph commitment"):
            confirm.check_stage_roots(changed, discovery, selection)
        changed = [dict(item) for item in confirmation]
        changed[-1]["commitment_sha256"] = "3" * 64
        with self.assertRaisesRegex(ValueError, "distinct confirmation graph"):
            confirm.check_stage_roots(changed, discovery, selection)
        changed = [dict(item) for item in confirmation]
        changed[0]["target_root_sha256"] = "d" * 64
        with self.assertRaisesRegex(ValueError, "target_root_sha256"):
            confirm.check_stage_roots(changed, discovery, selection)

    def test_exact_interval_boundaries(self):
        for population in range(5, 21):
            for draws in range(1, min(population, 6) + 1):
                for observed in range(draws + 1):
                    value = confirm.interval(population, draws, observed, 1, 200)
                    confirm.verify_interval_endpoints({"interval": value,
                        "population": population, "draws": draws,
                        "observed": observed, "tail_denominator": 200})

    def test_ratio_interval_and_zero_cases(self):
        ci = lambda lo, hi: {"lower_successes": lo, "upper_successes": hi}
        row = lambda value: {"useful_targets": value}
        ordinary = confirm.ratio_record(row(12), row(10), ci(11, 13), ci(9, 11))
        self.assertEqual(ordinary["interval_lower"], {"numerator": 1, "denominator": 1})
        self.assertFalse(ordinary["prespecified_20_percent_lead"])
        infinite = confirm.ratio_record(row(1), row(0), ci(0, 2), ci(0, 1))
        self.assertTrue(infinite["point_ratio_unbounded"])
        undefined = confirm.ratio_record(row(0), row(0), ci(0, 1), ci(0, 1))
        self.assertTrue(undefined["point_ratio_undefined"])
        self.assertFalse(undefined["prespecified_20_percent_lead"])

    def test_finalist_ties_and_undefined_ratio(self):
        selected = {"strata": {"P29": {"selected_vertices":
            [{"index": index} for index in (0, 1, 2)]}}}
        rows = []
        for index, j, low, random in ((0, 30, 0, 0), (1, 10, 4, 2), (2, 20, 4, 4)):
            for arm, value in (("low_x", low), ("random_x", random)):
                rows.append({"arm_key": f"P29-v{index:04d}-{arm}",
                             "stratum": "P29", "index": index, "j": j,
                             "useful_targets": value})
        intervals = {row["arm_key"]: {"lower_successes": 0, "upper_successes": 8}
                     for row in rows}
        ratios, finalists = confirm.finalist_selection(selected, rows, intervals)
        self.assertTrue(ratios["P29-v0000"]["point_ratio_undefined"])
        self.assertEqual(finalists["P29"][0]["index"], 0)
        self.assertIn("best_low_x", finalists["P29"][1]["reasons"])
        self.assertEqual(len(finalists["P29"]), 3)

    def test_cache_binding_and_mutation_refusal(self):
        row = {"arm_key": "P29-v0000-low_x", "r": 19, "targets": 5,
               "useful_targets": 2, "execution_receipt_sha256": "a" * 64}
        with tempfile.TemporaryDirectory() as name:
            cache = Path(name)
            first, first_hash = confirm.interval_cell(cache, row, 1)
            second, second_hash = confirm.interval_cell(cache, row, 1)
            self.assertEqual((first, first_hash), (second, second_hash))
            path = cache / "P29-v0000-low_x.json"
            payload = json.loads(path.read_text())
            payload["interval"]["lower_successes"] += 1
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, "cached exact lower endpoint differs"):
                confirm.interval_cell(cache, row, 1)
            row["execution_receipt_sha256"] = "b" * 64
            with self.assertRaisesRegex(ValueError, "cached interval identity differs"):
                confirm.interval_cell(cache, row, 1)


if __name__ == "__main__":
    unittest.main()
