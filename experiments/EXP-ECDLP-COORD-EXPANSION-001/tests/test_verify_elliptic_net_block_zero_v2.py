from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_elliptic_net_block_zero_v2.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_elliptic_net_block_zero_v2_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load normalized block-zero verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyEllipticNetBlockZeroV2Tests(unittest.TestCase):
    def test_normalize_removes_only_timing_fields(self) -> None:
        value = {"total_wall_seconds": 1, "nested": {"bm_order": 2}}
        self.assertEqual(MODULE.normalize(value), {"nested": {"bm_order": 2}})

    def test_mutation_rejection_is_total_for_protocol_mutation(self) -> None:
        raw = {
            "protocol": "wrong",
            "source": {},
            "summary": {
                "all_semantics_valid": True,
                "all_controls_valid": True,
                "normalization_controls_valid": True,
                "algorithm_promotion_gate": False,
                "breakthrough_claim": False,
            },
            "normalization_controls": {"all_pass": True},
            "config": {"normalization": "affine_output_locator_with_infinity_sentinel"},
            "rows": [],
        }
        # The direct check must reject the wrong protocol even if other fields
        # are incomplete in this unit-level mutation fixture.
        self.assertFalse(MODULE.check_result(raw, Path(__file__))["protocol"])


if __name__ == "__main__":
    unittest.main()
