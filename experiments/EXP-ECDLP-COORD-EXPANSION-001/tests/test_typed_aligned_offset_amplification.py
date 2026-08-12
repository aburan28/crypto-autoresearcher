from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parents[1] / "src" / "typed_aligned_offset_amplification.py"


def load_module():
    spec = importlib.util.spec_from_file_location("offset_amplification_under_test", SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load offset-amplification module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class TypedAlignedOffsetAmplificationTests(unittest.TestCase):
    def test_target_schedule_is_deterministic(self) -> None:
        curve = MODULE.ALIGNED.TYPED.Curve(17, 2, 2)
        generator = (5, 1)
        targets_a, scalar_a, ops_a = MODULE.target_schedule(curve, 19, generator, generator, "c", "f", 3, 0)
        targets_b, scalar_b, ops_b = MODULE.target_schedule(curve, 19, generator, generator, "c", "f", 3, 0)
        self.assertEqual((targets_a, scalar_a, ops_a), (targets_b, scalar_b, ops_b))

    def test_offset_summary_preserves_scan_semantics(self) -> None:
        summary = {"summary": {"replay_mismatches": 0, "equation_mismatches": 0}}
        keys = {"summary": {"target_records": 3}}
        result = MODULE.summarize_offset(keys, summary, {"group_operations": 2}, 0, 7)
        self.assertTrue(result["semantics_valid"])
        self.assertEqual(result["offset"], 0)


if __name__ == "__main__":
    unittest.main()
