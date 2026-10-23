"""Selection-bound controls for the finalist solve-stage compiler."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(HERE))
import build_solve_plan as plan  # noqa: E402

SCHEDULE = STUDY / "graph_schedule_20261023/discovery-arms.jsonl"


class SolvePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.by_key = {row["arm_key"]: row for row in
                      (json.loads(line) for line in SCHEDULE.read_text().splitlines())}

    def inputs(self):
        selection = {"schema": "ectd.graph-discovery-selection-candidate/v1",
                     "status": "selected_from_validated_discovery",
                     "discovery_arms_checked": 8206,
                     "schedule_sha256": plan.sha(SCHEDULE), "strata": {}}
        finalists = {}
        for stratum in ("P29", "P37"):
            row = self.by_key[f"{stratum}-v0000-low_x"]
            selection["strata"][stratum] = {"selected_vertices": [{"index": 0}]}
            finalists[stratum] = [{"index": 0, "j": row["model"]["j"],
                                   "reasons": ["prespecified_test_fixture"]}]
        selection_hash = "a" * 64
        analysis = {"schema": "ectd.graph-confirmation-analysis-candidate/v1",
                    "status": "confirmed_receipts_analyzed",
                    "selection_sha256": selection_hash,
                    "schedule_sha256": plan.sha(SCHEDULE),
                    "finalists": finalists}
        return analysis, selection, selection_hash

    def test_finalists_expand_to_exact_three_paired_bases(self):
        analysis, selection, digest = self.inputs()
        rows = plan.finalist_rows(analysis, selection, digest)
        self.assertEqual(len(rows), 6)
        for stratum in ("P29", "P37"):
            group = [row for row in rows if row["stratum"] == stratum]
            self.assertEqual([row["base_rule"] for row in group],
                             ["low_x", "mid_x", "random_x"])
            self.assertEqual({row["path_index"] for row in group}, {0})

    def test_rejects_finalist_outside_discovery_selection(self):
        analysis, selection, digest = self.inputs()
        analysis["finalists"]["P37"][0]["index"] = 1
        with self.assertRaisesRegex(ValueError, "not a unique prespecified selected vertex"):
            plan.finalist_rows(analysis, selection, digest)

    def test_rejects_confirmation_from_different_selection(self):
        analysis, selection, _ = self.inputs()
        with self.assertRaisesRegex(ValueError, "exact selected-discovery receipt"):
            plan.finalist_rows(analysis, selection, "b" * 64)

    def test_rho_repetitions_bind_same_finalist_and_all_three_relation_arms(self):
        analysis, selection, digest = self.inputs()
        rows = plan.finalist_rows(analysis, selection, digest)
        relation_ids = {row["arm_key"]: f"RUN-ECTD-{index:06x}"
                        for index, row in enumerate(rows, 1)}
        trials = plan.make_rho_trials(
            rows, [f"RUN-ECTD-{index:06x}" for index in range(101, 121)],
            relation_ids, list(range(10)), experiment_id="EXP-ECTD-abcdef")
        self.assertEqual(len(trials), 20)
        for family, index in (("P29", 0), ("P37", 0)):
            group = [trial for trial in trials
                     if trial["parameters"]["stratum"] == family]
            self.assertEqual(len(group), 10)
            self.assertEqual({tuple(trial["depends_on"]) for trial in group},
                             {(f"{family}-v{index:04d}-low_x",
                               f"{family}-v{index:04d}-mid_x",
                               f"{family}-v{index:04d}-random_x")})
            low_run = relation_ids[f"{family}-v{index:04d}-low_x"]
            self.assertTrue(all(any(path.endswith(
                f"runs/{low_run}/prepared/prepared.txt") for path in trial["argv"])
                for trial in group))
            self.assertEqual({trial["parameters"]["max_steps"] for trial in group},
                             {60_000_000})


if __name__ == "__main__":
    unittest.main()
