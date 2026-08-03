from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "src"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PRODUCER = load("tt_zero_locator_rank_census_test", ROOT / "tt_zero_locator_rank_census.py")
VERIFIER = load("verify_tt_zero_locator_rank_census_test", ROOT / "verify_tt_zero_locator_rank_census.py")


class TTZeroLocatorRankCensusTests(unittest.TestCase):
    def test_exact_rank_has_known_tensor_ranks(self) -> None:
        dimensions = [2, 3, 2]
        values = [1] * 12
        self.assertEqual(PRODUCER.rank_profile(values, dimensions, 101), {"1": 1, "2": 1})

    def test_rank_two_control_is_not_rank_one_at_a_middle_cut(self) -> None:
        controls = PRODUCER.synthetic_controls(101)
        self.assertTrue(controls["pass"])
        self.assertEqual(controls["rank_one"]["ranks"]["2"], 1)

    def test_matched_random_support_is_exact(self) -> None:
        values = PRODUCER.support_matched_random(20, 4, "test")
        self.assertEqual(sum(values), 4)
        self.assertEqual(values, VERIFIER.support_matched_random(20, 4, "test"))

    def test_affine_addition_replay_matches_independent_implementation(self) -> None:
        ops_a = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        ops_b = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        curve_a = PRODUCER.AffineCurve(971, 934, 886)
        curve_b = VERIFIER.AffineCurve(971, 934, 886)
        left = (12, 345)
        right = (67, 89)
        self.assertEqual(curve_a.add(left, right, ops_a), curve_b.add(left, right, ops_b))

    def test_mutation_changes_are_rejected(self) -> None:
        raw = {
            "protocol": "wrong",
            "source": {},
            "config": {"rank_field": "exact modular Gaussian elimination over F_p"},
            "summary": {"algorithm_promotion_gate": False, "breakthrough_claim": False, "cells": 0, "boundary": "not a compact locator"},
            "controls": {"rank_one_pass": True, "rank_one": {"ranks": {"1": 1}}},
            "rows": [],
        }
        self.assertFalse(VERIFIER.check_result(raw, Path(__file__))["protocol"])


if __name__ == "__main__":
    unittest.main()
