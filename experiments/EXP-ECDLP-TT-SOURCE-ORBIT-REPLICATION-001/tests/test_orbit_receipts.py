from __future__ import annotations

import json
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]


class OrbitReceiptTests(unittest.TestCase):
    def test_generator_and_verifier_are_valid(self) -> None:
        runs = EXP_ROOT / "runs"
        generator = json.loads(
            (runs / "RUN-TT-SOURCE-ORBIT-001" / "raw-result.json").read_text(
                encoding="utf-8"
            )
        )
        verifier = json.loads(
            (runs / "RUN-TT-SOURCE-ORBIT-002" / "raw-result.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(generator["valid"])
        self.assertTrue(verifier["valid"])
        for seed in ("271828", "161803"):
            self.assertTrue(verifier["checks"][f"{seed}_candidate_selector_hash"])
            self.assertTrue(verifier["checks"][f"{seed}_candidate_selector_records"])
            self.assertTrue(verifier["checks"][f"{seed}_candidate_support_and_witnesses"])
            self.assertTrue(verifier["checks"][f"{seed}_rho_certificates"])

        for case in generator["summary"]["accepted_subfull_budgets"].values():
            self.assertEqual(
                case,
                {"random_x": [], "source_prf_x": [], "x_interval": [], "rational_union": []},
            )


if __name__ == "__main__":
    unittest.main()
