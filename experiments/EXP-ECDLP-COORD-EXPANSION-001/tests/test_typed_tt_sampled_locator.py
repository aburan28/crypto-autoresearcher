from __future__ import annotations

import json
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]


class TTSampledLocatorTests(unittest.TestCase):
    def test_sealed_receipt_preserves_full_control_and_rank_negative(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-SAMPLED-LOCATOR-V1" / "RUN-001"
        raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        verification = json.loads((run_dir / "verification.json").read_text(encoding="utf-8"))
        self.assertTrue(verification["valid"])
        self.assertTrue(raw["summary"]["full_budget_exact"])
        self.assertTrue(raw["summary"]["known_p4027_source_prf_rank_deficient"])
        self.assertTrue(any(raw["summary"]["subfull_exact_budgets"].values()))
        for row in raw["rows"]:
            self.assertEqual(row["budgets"][-1]["budget_label"], "full")
            self.assertTrue(row["budgets"][-1]["all_support_exact"])


if __name__ == "__main__":
    unittest.main()
