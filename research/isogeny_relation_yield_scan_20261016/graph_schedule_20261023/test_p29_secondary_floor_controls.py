"""Identity and shared-target-domain controls for the P29 E2/E3 supplement."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
sys.path.insert(0, str(HERE))
import p29_secondary_floor_controls as controls  # noqa: E402
sys.path.insert(0, str(STUDY / "preparation"))
import prepare_graph_input as graph  # noqa: E402


class SecondaryFloorScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, _ = controls.expected_rows()

    def test_exact_endpoint_models_and_fixed_arm_quotas(self):
        by_key = {row["arm_key"]: row for row in self.rows}
        self.assertEqual(set(by_key), {
            "P29-E2-low_x", "P29-E2-random_x",
            "P29-E3-low_x", "P29-E3-random_x"})
        self.assertEqual({row["endpoint_id"] for row in self.rows}, {"P29-E2", "P29-E3"})
        self.assertEqual({row["discovery_targets"] for row in self.rows}, {8192})
        self.assertEqual({row["base_x_orbits"] for row in self.rows}, {256})
        self.assertTrue(all(row["finalist_selection_eligible"] is False for row in self.rows))

    def test_p29_shared_target_coefficient_stream_matches_graph_domain(self):
        seed_dir = STUDY / "seed_custody_20261022/control"
        roots = {name: bytes.fromhex((seed_dir / f"{name}.hex").read_text().strip())
                 for name in ("target", "verifier")}
        expected = graph.target_coefficients(roots["target"], "P29", "discovery",
                                             320091991, 8192, roots["verifier"])[1]
        digests = set()
        for row in self.rows:
            self.assertEqual(row["target_domain"], ["P29", "discovery"])
            self.assertEqual(row["r"], 320091991)
            observed = graph.target_coefficients(
                roots["target"], "P29", "discovery", row["r"],
                row["discovery_targets"], roots["verifier"])[1]
            self.assertEqual(observed, expected)
            digests.add(json.dumps(observed, separators=(",", ":")))
        self.assertEqual(len(digests), 1)

    def test_write_once_schedule_verifier_accepts_generated_supplement(self):
        result = controls.verify()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["arms_checked"], 4)
        self.assertEqual(result["target_probes"], 32768)


if __name__ == "__main__":
    unittest.main()
