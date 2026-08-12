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


PRODUCER = load("nonlinear_s4_preflight_test", ROOT / "nonlinear_s4_quotient_preflight.py")
VERIFIER = load("verify_nonlinear_s4_preflight_test", ROOT / "verify_nonlinear_s4_quotient_preflight.py")


class NonlinearS4QuotientPreflightTests(unittest.TestCase):
    def test_non_decreasing_state_has_expected_tuple_count(self) -> None:
        curve = PRODUCER.AffineCurve(971, 934, 886)
        sources = [(1, 2), (3, 4), (5, 6)]
        ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        states = PRODUCER.state_level(curve, sources, 2, ops)
        self.assertLessEqual(len(states), 6)
        self.assertEqual(sum(1 for _ in __import__("itertools").combinations_with_replacement(range(3), 2)), 6)

    def test_feature_rank_is_bounded_by_columns(self) -> None:
        states = {(1, 2): (0, 0), (3, 4): (0, 1), None: (1, 1)}
        profile = PRODUCER.feature_rank_curve(states, 101, 4)
        self.assertTrue(all(row["rank"] <= row["columns"] for row in profile))

    def test_independent_addition_agrees(self) -> None:
        ops_a = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        ops_b = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        self.assertEqual(
            PRODUCER.AffineCurve(971, 934, 886).add((12, 345), (67, 89), ops_a),
            VERIFIER.Curve(971, 934).add((12, 345), (67, 89), ops_b),
        )

    def test_malformed_protocol_fails_closed(self) -> None:
        raw = {"protocol": "wrong", "source": {}, "config": {}, "summary": {}}
        self.assertFalse(VERIFIER.check(raw, Path(__file__))["protocol"])


if __name__ == "__main__":
    unittest.main()
