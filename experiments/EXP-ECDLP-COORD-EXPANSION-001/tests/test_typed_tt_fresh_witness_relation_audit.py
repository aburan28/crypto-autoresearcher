from __future__ import annotations

import json
import importlib.util
import sys
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]
SRC = EXP_ROOT / "src"
SPEC = importlib.util.spec_from_file_location(
    "typed_tt_fresh_witness_relation_audit_test",
    SRC / "typed_tt_fresh_witness_relation_audit.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load fresh-witness producer")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TTFreshWitnessRelationAuditTests(unittest.TestCase):
    def test_full_and_truncated_receipts_are_sealed(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-FRESH-WITNESS-RELATION-AUDIT-V1" / "RUN-001"
        full = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        truncated = json.loads((run_dir / "truncated.json").read_text(encoding="utf-8"))
        verification = json.loads((run_dir / "verification.json").read_text(encoding="utf-8"))
        self.assertTrue(verification["valid"])
        self.assertTrue(full["summary"]["all_witnesses_valid"])
        self.assertTrue(full["summary"]["all_supports_match"])
        self.assertTrue(full["summary"]["all_candidate_full_tensor_mode"])
        self.assertFalse(truncated["summary"]["all_supports_match"])
        self.assertFalse(truncated["summary"]["all_candidate_full_rank"])

    def test_full_query_fraction_is_explicit(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-FRESH-WITNESS-RELATION-AUDIT-V1" / "RUN-001"
        full = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        self.assertEqual(full["summary"]["mean_candidate_query_fraction_of_full_tensor"], 1.0)
        self.assertFalse(full["summary"]["breakthrough_claim"])
        self.assertFalse(full["summary"]["algorithm_promotion_gate"])


if __name__ == "__main__":
    unittest.main()
