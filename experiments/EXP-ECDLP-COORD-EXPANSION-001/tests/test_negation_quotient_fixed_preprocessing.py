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


PRODUCER = load("negation_quotient_fixed_test", ROOT / "negation_quotient_fixed_preprocessing.py")
VERIFIER = load("verify_negation_quotient_fixed_test", ROOT / "verify_negation_quotient_fixed_preprocessing.py")


class NegationQuotientFixedPreprocessingTests(unittest.TestCase):
    def test_sign_bit_separates_negation(self) -> None:
        self.assertNotEqual(PRODUCER.sign_bit(3, 11), PRODUCER.sign_bit(8, 11))

    def test_x_index_preserves_sign_witnesses(self) -> None:
        states = {(7, 3): [(0, 1)], (7, 8): [(1, 2)]}
        index = PRODUCER.build_x_index(states, 11)
        self.assertEqual(index["buckets"]["7"]["0"], [(0, 1)])
        self.assertEqual(index["buckets"]["7"]["1"], [(1, 2)])

    def test_independent_addition_agrees(self) -> None:
        a = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        b = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        self.assertEqual(
            PRODUCER.AffineCurve(971, 934, 886).add((12, 345), (67, 89), a),
            VERIFIER.Curve(971, 934).add((12, 345), (67, 89), b),
        )

    def test_malformed_protocol_fails_closed(self) -> None:
        raw = {"protocol": "wrong", "source": {}, "config": {}, "summary": {}}
        self.assertFalse(VERIFIER.check(raw, Path(__file__))["protocol"])


if __name__ == "__main__":
    unittest.main()
