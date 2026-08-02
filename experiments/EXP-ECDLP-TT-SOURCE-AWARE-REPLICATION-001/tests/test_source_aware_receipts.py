from __future__ import annotations

import json
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]


class SourceAwareReceiptTests(unittest.TestCase):
    def test_valid_generator_and_independent_verifier(self) -> None:
        runs = EXP_ROOT / "runs"
        generator = json.loads(
            (runs / "RUN-TT-SOURCE-AWARE-003" / "raw-result.json").read_text(
                encoding="utf-8"
            )
        )
        verifier = json.loads(
            (runs / "RUN-TT-SOURCE-AWARE-005" / "raw-result.json").read_text(
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

        accepted = generator["summary"]["accepted_subfull_budgets"]
        self.assertEqual(
            accepted["recursive-toy-p15667-a10428-b3105-q15583"]["source_prf_x"],
            ["64"],
        )
        self.assertEqual(
            accepted["recursive-toy-p15683-a13370-b621-q15749"],
            {"random_x": [], "source_prf_x": [], "x_interval": [], "rational_union": []},
        )

    def test_failed_implementation_receipts_are_preserved(self) -> None:
        runs = EXP_ROOT / "runs"
        for run_id in ("RUN-TT-SOURCE-AWARE-001", "RUN-TT-SOURCE-AWARE-002", "RUN-TT-SOURCE-AWARE-004"):
            manifest = json.loads((runs / run_id / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["run"]["status"], "failed_implementation")


if __name__ == "__main__":
    unittest.main()
