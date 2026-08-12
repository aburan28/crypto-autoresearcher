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


PRODUCER = load("recursive_d2_complement_test", ROOT / "recursive_d2_complement_preflight.py")
VERIFIER = load("verify_recursive_d2_complement_test", ROOT / "verify_recursive_d2_complement_preflight.py")


class RecursiveD2ComplementPreflightTests(unittest.TestCase):
    def test_d2_state_tuple_count_is_bounded(self) -> None:
        curve = PRODUCER.AffineCurve(971, 934, 886)
        sources = [(1, 2), (3, 4), (5, 6)]
        ops = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        states = PRODUCER.state_level(curve, sources, 2, ops)
        self.assertLessEqual(len(states), 6)

    def test_advice_words_charge_witness_indices(self) -> None:
        states = {(1, 2): [(0, 1)], (3, 4): [(1, 1)]}
        result = PRODUCER.advice_words(states, 2)
        self.assertEqual(result["logical_advice_words"], 2 * 2 + 2 * 2)

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
