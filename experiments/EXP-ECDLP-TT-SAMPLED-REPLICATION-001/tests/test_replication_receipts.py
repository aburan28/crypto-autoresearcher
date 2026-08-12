from __future__ import annotations

import json
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]


class FreshReplicationReceiptTests(unittest.TestCase):
    def test_generator_and_independent_verifier_are_valid(self) -> None:
        runs = EXP_ROOT / "runs"
        generator = json.loads(
            (runs / "RUN-TT-REPLICATION-005" / "raw-result.json").read_text(
                encoding="utf-8"
            )
        )
        verifier = json.loads(
            (runs / "RUN-TT-REPLICATION-006" / "raw-result.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertTrue(generator["valid"])
        self.assertTrue(verifier["valid"])
        self.assertTrue(verifier["checks"]["generator_valid"])
        self.assertTrue(verifier["checks"]["271828_candidate_fixture_hash"])
        self.assertTrue(verifier["checks"]["161803_candidate_fixture_hash"])
        self.assertTrue(verifier["checks"]["271828_candidate_support_and_witnesses"])
        self.assertTrue(verifier["checks"]["161803_candidate_support_and_witnesses"])
        self.assertTrue(verifier["checks"]["271828_rho_certificates"])
        self.assertTrue(verifier["checks"]["161803_rho_certificates"])

        accepted = generator["summary"]["accepted_subfull_budgets"]
        self.assertEqual(
            {family: budgets for case in accepted.values() for family, budgets in case.items()},
            {
                "random_x": [],
                "source_prf_x": [],
                "x_interval": [],
                "rational_union": [],
            },
        )


if __name__ == "__main__":
    unittest.main()
