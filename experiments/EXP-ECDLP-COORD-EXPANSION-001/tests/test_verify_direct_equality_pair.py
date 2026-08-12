from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_direct_equality_pair.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_direct_equality_pair_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load equality-pair verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyDirectEqualityPairTests(unittest.TestCase):
    def test_normalize_removes_timing(self) -> None:
        self.assertEqual(
            MODULE.normalize(
                {
                    "peak_rss_bytes": 1,
                    "nested": {"total_wall_seconds": 2, "rank": 12},
                }
            ),
            {"nested": {"rank": 12}},
        )

    def test_accounting_rejects_wrong_fixed_state(self) -> None:
        result = {
            "rows": [
                {
                    "r_size": 5,
                    "cuts": [
                        {
                            "cut": 2,
                            "basis_dimension": 24,
                            "prefix_count": 1,
                            "suffix_count": 125,
                            "target_independent_advice_field_elements": 1,
                            "targets": {},
                        }
                    ],
                }
            ]
        }
        self.assertFalse(MODULE.accounting_consistent(result))


if __name__ == "__main__":
    unittest.main()
