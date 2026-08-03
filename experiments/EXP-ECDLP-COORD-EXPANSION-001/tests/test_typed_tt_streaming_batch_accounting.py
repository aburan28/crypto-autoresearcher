from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "typed_tt_streaming_batch_accounting_test",
    EXP_ROOT / "src" / "typed_tt_streaming_batch_accounting_preflight.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load streaming-batch producer")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TTStreamingBatchAccountingTests(unittest.TestCase):
    def test_batch_specs_interleave_relation_and_descent_widths(self) -> None:
        relations = [(f"relation_{index}", [index, index + 1]) for index in range(8)]
        held_out = [(f"held_out_supported_{index}", [index + 10, index + 11]) for index in range(8)]
        specs = MODULE.batch_specs(relations, held_out)
        self.assertEqual([label for label, _ in specs], ["balanced_1", "balanced_2", "balanced_4", "balanced_8", "full"])
        self.assertEqual([len(targets) for _, targets in specs], [2, 4, 8, 16, 16])
        self.assertEqual(specs[-1][1], relations + held_out)

    def test_reset_prefix_drops_only_streaming_state(self) -> None:
        class Advice:
            current_prefix_key = (1, 2, 3)
            current_prefix = (5, 6)

        advice = Advice()
        MODULE.reset_prefix(advice)
        self.assertIsNone(advice.current_prefix_key)
        self.assertIsNone(advice.current_prefix)

    def test_sealed_receipts_report_expected_batch_boundaries(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-STREAMING-BATCH-ACCOUNTING-V1" / "RUN-001"
        raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        verification = json.loads((run_dir / "verification.json").read_text(encoding="utf-8"))
        self.assertTrue(verification["valid"])
        self.assertTrue(raw["summary"]["all_full_exact"])
        self.assertTrue(raw["summary"]["all_batch_prefix_reuse"])
        self.assertEqual(len(raw["rows"]), 12)


if __name__ == "__main__":
    unittest.main()
