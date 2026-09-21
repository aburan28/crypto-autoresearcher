from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "typed_tt_downstream_cost_accounting_test",
    EXP_ROOT / "src" / "typed_tt_downstream_cost_accounting_preflight.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load downstream-cost producer")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TTDownstreamCostAccountingTests(unittest.TestCase):
    def test_recovery_operation_formula_charges_both_paths(self) -> None:
        ops = MODULE.recovery_ops(6, 8, 2)
        self.assertEqual(ops["field_multiplications"], 96)
        self.assertEqual(ops["field_additions"], 80)

    def test_operation_accumulator_preserves_all_declared_classes(self) -> None:
        total = MODULE.zero_ops()
        MODULE.add_ops(total, {"field_multiplications": 3, "group_operations": 2})
        MODULE.add_ops(total, {"field_multiplications": 5, "row_additions": 4})
        self.assertEqual(total["field_multiplications"], 8)
        self.assertEqual(total["group_operations"], 2)
        self.assertEqual(total["row_additions"], 4)

    def test_sealed_downstream_receipt_is_independently_valid(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-DOWNSTREAM-COST-ACCOUNTING-V1" / "RUN-001"
        raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        verification = json.loads((run_dir / "verification.json").read_text(encoding="utf-8"))
        self.assertTrue(verification["valid"])
        self.assertTrue(raw["summary"]["all_relation_transcripts_match"])
        self.assertTrue(raw["summary"]["all_descent_transcripts_match"])
        self.assertEqual(raw["summary"]["total_verified_descent_targets"], 150)


if __name__ == "__main__":
    unittest.main()
