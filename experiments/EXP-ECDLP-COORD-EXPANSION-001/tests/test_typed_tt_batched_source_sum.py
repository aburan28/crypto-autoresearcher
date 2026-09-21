from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


EXP_ROOT = Path(__file__).resolve().parents[1]
PRODUCER_SPEC = importlib.util.spec_from_file_location(
    "typed_tt_batched_source_sum_test",
    EXP_ROOT / "src" / "typed_tt_batched_source_sum.py",
)
if PRODUCER_SPEC is None or PRODUCER_SPEC.loader is None:
    raise RuntimeError("unable to load batched source-sum producer")
PRODUCER = importlib.util.module_from_spec(PRODUCER_SPEC)
sys.modules[PRODUCER_SPEC.name] = PRODUCER
PRODUCER_SPEC.loader.exec_module(PRODUCER)


class TTBatchedSourceSumTests(unittest.TestCase):
    def test_prefix_sample_is_deterministic_and_bounded(self) -> None:
        first = PRODUCER.validation_prefix_sample(14, 14, 64, 123)
        second = PRODUCER.validation_prefix_sample(14, 14, 64, 123)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_sealed_receipt_has_exact_reference_and_saving(self) -> None:
        run_dir = EXP_ROOT / "development" / "TYPED-TT-ROWSPACE-BATCHED-SOURCE-SUM-V1" / "RUN-001"
        raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        verification = json.loads((run_dir / "verification.json").read_text(encoding="utf-8"))
        self.assertTrue(verification["valid"])
        self.assertTrue(raw["summary"]["all_shared_direct_reference_exact"])
        self.assertTrue(raw["summary"]["all_control_direct_reference_exact"])
        for row in raw["rows"]:
            control = row["separated_control"]["batches"][-1]
            candidate = row["shared_candidate"]["batches"][-1]
            self.assertLess(candidate["source_ops"]["point_add_calls"], control["source_ops"]["point_add_calls"])


if __name__ == "__main__":
    unittest.main()
