"""Replay a sorted-prefix representation counterexample without a solver."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import encode_sorted as producer
import verify_inputs as checker


class SortedExceptionTest(unittest.TestCase):
    def test_valid_unsorted_witness_can_have_exceptional_sorted_prefix(self):
        path = Path(__file__).resolve().parents[1] / "review-corrections/20261019-sorted-exception.json"
        record = json.loads(path.read_bytes())
        points = [tuple(point) for point in record["points"]]
        manifest = json.loads(checker.MANIFEST.read_bytes())
        gamma = manifest["gamma"]
        base = json.loads(checker.BASES[record["base"]].read_bytes())
        with patch("subprocess.Popen", side_effect=AssertionError("solver launch forbidden")):
            primary = checker.primary_for(points, gamma, 31)
            self.assertEqual(hex(primary), record["original_primary_hex"])
            total = checker.point_sum(points, 31)
            self.assertEqual(total, tuple(record["raw_target"]))
            target = checker.phi_from_x(total[0], gamma)
            raw, metadata = producer.original_encode(
                "torsion_phi", 11, 4096, target, gamma,
                producer.allowed_values("torsion_phi", base, 4096, 11))
            checker.full_values(raw, primary, metadata["live_gates"])
            arm = {"kind": "torsion_phi", "base_dimension": 11, "offset": 4096,
                   "primary_variables": 454, "target_coordinate": target}
            chain = {"gamma": gamma,
                     "curve": {"b_polynomial_bits": 31, "prime_order": 576460752557211763},
                     "selected_channel": 0, "target_channels": [list(total)] * 4,
                     "subgroup_target": list(checker.scale(4, total, 31))}
            self.assertTrue(checker.certificate(primary, base, chain, arm)["certified"])
            sorted_points = checker.stable_points(points, gamma)
            self.assertEqual(checker.point_sum(sorted_points, 31), total)
            self.assertIsNone(checker.point_sum(sorted_points[:2], 31))
            with self.assertRaisesRegex(ValueError, "exceptional intermediate point"):
                checker.primary_for(sorted_points, gamma, 31)


if __name__ == "__main__":
    unittest.main()
