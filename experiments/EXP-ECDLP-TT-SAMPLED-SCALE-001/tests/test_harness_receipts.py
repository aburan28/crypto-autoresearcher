from __future__ import annotations

import json
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]


class SampledScaleHarnessTests(unittest.TestCase):
    def test_generator_and_verifier_receipts_are_valid(self) -> None:
        runs = EXP_ROOT / "runs"
        generator = json.loads((runs / "RUN-TT-SAMPLED-001" / "raw-result.json").read_text(encoding="utf-8"))
        verifier = json.loads((runs / "RUN-TT-SAMPLED-002" / "raw-result.json").read_text(encoding="utf-8"))
        self.assertTrue(generator["valid"])
        self.assertTrue(verifier["valid"])
        self.assertTrue(verifier["checks"]["result_digest"])
        self.assertTrue(verifier["checks"]["rho_direct_certificates"])
        candidate = generator["candidate"]
        self.assertTrue(candidate["summary"]["full_budget_exact"])
        self.assertEqual(candidate["summary"]["rows"], 4)
        self.assertTrue(any(generator["summary"]["subfull_exact_budgets"].values()))


if __name__ == "__main__":
    unittest.main()
