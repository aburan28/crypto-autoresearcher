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


PRODUCER = load("implicit_pair_state_index_test", ROOT / "implicit_pair_state_index.py")
VERIFIER = load("verify_implicit_pair_state_index_test", ROOT / "verify_implicit_pair_state_index.py")


class ImplicitPairStateIndexTests(unittest.TestCase):
    def test_pair_records_store_state_ids_only(self) -> None:
        curve = PRODUCER.AffineCurve(971, 934, 886)
        sources = [(1, 2), (3, 4), (5, 6)]
        d2 = PRODUCER.state_level(curve, sources, 2, PRODUCER.empty_ops())
        points, records = PRODUCER.build_pair_states(curve, d2, PRODUCER.empty_ops())
        self.assertEqual(len(records), len(points) * (len(points) + 1) // 2)
        self.assertTrue(all(len(record) == 3 and isinstance(record[1], int) and isinstance(record[2], int) for record in records))

    def test_exact_state_pair_lift_matches_recursive(self) -> None:
        curve = PRODUCER.AffineCurve(971, 934, 886)
        sources = [(1, 2), (3, 4), (5, 6)]
        d2 = PRODUCER.state_level(curve, sources, 2, PRODUCER.empty_ops())
        points, records = PRODUCER.build_pair_states(curve, d2, PRODUCER.empty_ops())
        indexes = PRODUCER.build_indexes(records, [1, 4])
        target = records[0][0]
        recursive, _ = PRODUCER.query_recursive(curve, [None], sources, d2, target, PRODUCER.empty_ops())
        exact, _ = PRODUCER.query_index(curve, [None], sources, points, d2, indexes["exact"], target, PRODUCER.empty_ops())
        self.assertEqual(recursive, exact)

    def test_independent_curve_addition_agrees(self) -> None:
        ops_a = PRODUCER.empty_ops(); ops_b = VERIFIER.empty_ops()
        left = PRODUCER.AffineCurve(971, 934, 886).add((12, 345), (67, 89), ops_a)
        right = VERIFIER.Curve(971, 934, 886).add((12, 345), (67, 89), ops_b)
        self.assertEqual(left, right)

    def test_malformed_protocol_fails_closed(self) -> None:
        raw = {"protocol": "wrong", "source": {}, "config": {}, "summary": {}}
        self.assertFalse(VERIFIER.check(raw, Path(__file__))["protocol"])


if __name__ == "__main__":
    unittest.main()
