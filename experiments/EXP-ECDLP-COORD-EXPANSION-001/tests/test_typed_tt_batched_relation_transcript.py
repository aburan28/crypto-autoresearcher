from __future__ import annotations

import json
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]


class TTBatchedRelationTranscriptTests(unittest.TestCase):
    def test_sealed_relation_receipt(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-BATCHED-RELATION-TRANSCRIPT-V1" / "RUN-001"
        raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        verification = json.loads((run_dir / "verification.json").read_text(encoding="utf-8"))
        self.assertTrue(verification["valid"])
        self.assertTrue(raw["summary"]["all_witnesses_valid"])
        self.assertTrue(raw["summary"]["all_supports_match"])
        self.assertTrue(raw["summary"]["all_same_relation_rank"])
        self.assertTrue(raw["summary"]["all_held_out_supported_coverage"])
        self.assertTrue(raw["summary"]["all_diagnostic_solution_matches"])
        self.assertTrue(raw["summary"]["all_strict_source_add_saving"])
        self.assertTrue(raw["summary"]["all_candidate_full_rank"])

    def test_all_four_public_families_are_present(self) -> None:
        raw = json.loads((EXP_ROOT / "development" / "TYPED-TT-BATCHED-RELATION-TRANSCRIPT-V1" / "RUN-001" / "raw-result.json").read_text(encoding="utf-8"))
        self.assertEqual({row["family"] for row in raw["rows"]}, {"random_x", "source_prf_x", "x_interval", "rational_union"})


if __name__ == "__main__":
    unittest.main()
