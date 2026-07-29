from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_direct_equality_pair_cross_tree_strict.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_cross_tree_strict_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load strict verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyCrossTreeStrictTests(unittest.TestCase):
    def test_tracked_add_counts_branches(self) -> None:
        counts = {
            "additions": 0,
            "doublings": 0,
            "identity_returns": 0,
            "inverse_returns": 0,
            "inversions": 0,
            "multiplications": 0,
        }
        point = (3, 6)
        self.assertEqual(
            MODULE.tracked_add(None, point, 97, 2, counts), point
        )
        self.assertIsNone(
            MODULE.tracked_add(point, (3, 91), 97, 2, counts)
        )
        self.assertEqual(counts["additions"], 2)
        self.assertEqual(counts["identity_returns"], 1)
        self.assertEqual(counts["inverse_returns"], 1)

    def test_row_valid_rejects_mutation_failure(self) -> None:
        row = {
            "tree_count": 14,
            "controls": {"a": True},
            "tree_mismatches": 0,
            "cut2_mismatches": 0,
            "cut3_mismatches": 0,
            "zero_semantic_mismatches": 0,
            "projective_scale_mismatches": 0,
            "mutation_control_failures": 1,
            "witness_counts": {"planted": 1},
        }
        self.assertFalse(MODULE.row_valid(row))


if __name__ == "__main__":
    unittest.main()
