"""Public small-group control for the same-point plain-rho adapter."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from matched_rho import run
from check_matched_rho import check

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
INPUT = (STUDY / "graph_solve_candidate_20261023/controls/attempt-1/q7/input.txt")
PUBLIC = (STUDY / "graph_solve_candidate_20261023/controls/attempt-1/q7/public.json")


class MatchedRhoTests(unittest.TestCase):
    def test_plain_rho_recovers_the_bound_public_fixture_point(self):
        curve = INPUT.read_text().splitlines()[0].split()
        public = json.loads(PUBLIC.read_text())
        manifest = {"p": int(curve[1]), "a": int(curve[2]), "b": int(curve[3]),
                    "r": int(curve[4]), "generator": public["generator"],
                    "Q": public["Q"]}
        with tempfile.TemporaryDirectory(prefix="ectd-rho-small-control-") as temp:
            path = Path(temp) / "manifest.json"
            path.write_text(json.dumps(manifest))
            result = run(INPUT, path, seed=73, max_steps=10000)
            result_path = Path(temp) / "result.json"
            result_path.write_text(json.dumps(result))
            checked = check(INPUT, path, result_path)
        self.assertEqual(result["status"], "verified_scalar")
        self.assertTrue(result["verified"])
        self.assertEqual(result["scalar"], public["expected_scalar_for_control"])
        self.assertEqual((result["generator"], result["Q"]),
                         (public["generator"], public["Q"]))
        self.assertEqual(checked["status"], "valid_verified_scalar")


if __name__ == "__main__":
    unittest.main()
