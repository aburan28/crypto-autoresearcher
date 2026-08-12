from __future__ import annotations

import json
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]


class TTBatchedRelationScaleTests(unittest.TestCase):
    def test_sealed_scale_receipt_preserves_negative_family(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-BATCHED-RELATION-SCALE-V1" / "RUN-001"
        raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        verification = json.loads((run_dir / "verification.json").read_text(encoding="utf-8"))
        self.assertTrue(verification["valid"])
        by_family = {row["family"]: row for row in raw["rows"]}
        self.assertTrue(by_family["random_x"]["shared_candidate"]["candidate_full_rank"])
        self.assertFalse(by_family["source_prf_x"]["shared_candidate"]["candidate_full_rank"])
        self.assertTrue(by_family["x_interval"]["shared_candidate"]["candidate_full_rank"])
        self.assertTrue(by_family["rational_union"]["shared_candidate"]["candidate_full_rank"])
        self.assertTrue(raw["summary"]["all_witnesses_valid"])
        self.assertTrue(raw["summary"]["all_supports_match"])


if __name__ == "__main__":
    unittest.main()
