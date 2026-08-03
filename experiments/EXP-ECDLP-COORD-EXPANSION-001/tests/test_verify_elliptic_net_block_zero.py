from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_elliptic_net_block_zero.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_elliptic_net_block_zero_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load block-zero verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyEllipticNetBlockZeroTests(unittest.TestCase):
    def test_normalize_removes_only_timing_fields(self) -> None:
        value = {
            "peak_rss_bytes": 1,
            "nested": {
                "total_wall_seconds": 2,
                "bm_order": 10,
            },
        }
        self.assertEqual(
            MODULE.normalize(value), {"nested": {"bm_order": 10}}
        )

    def test_summary_rejects_false_promotion(self) -> None:
        result = {
            "config": {"families": ["f"]},
            "controls": {
                "c": {
                    "planted_linear": {
                        "recovered_order": 1,
                        "planted_order": 2,
                        "recovered_violations": 0,
                        "planted_violations": 0,
                        "train_test": {"held_out_exact": True},
                    },
                    "elliptic_divisibility": {
                        "ward_violations": 0,
                        "somos4": {"exact": True},
                    },
                    "deterministic_random": {
                        "somos4": {"exact": False}
                    },
                }
            },
            "rows": [
                {
                    "curve_id": "c",
                    "family": "f",
                    "recurrence_signal": False,
                    "semantics_valid": True,
                    "planted_descent_replay": True,
                }
            ],
            "summary": {
                "family_rows": 1,
                "curve_count": 1,
                "promoted_families": ["f"],
                "recurrence_signal_gate": True,
                "constructible_implicit_state": False,
                "algorithm_promotion_gate": False,
                "all_controls_valid": True,
                "all_semantics_valid": True,
            },
        }
        self.assertFalse(MODULE.summary_consistent(result))


if __name__ == "__main__":
    unittest.main()
