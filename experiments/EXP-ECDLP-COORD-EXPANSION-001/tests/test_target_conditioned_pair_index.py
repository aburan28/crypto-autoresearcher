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


PRODUCER = load("target_conditioned_pair_index_test", ROOT / "target_conditioned_pair_index.py")
VERIFIER = load("verify_target_conditioned_pair_index_test", ROOT / "verify_target_conditioned_pair_index.py")


class TargetConditionedPairIndexTests(unittest.TestCase):
    def test_fingerprint_is_deterministic_and_separates_identity(self) -> None:
        self.assertEqual(PRODUCER.fingerprint(None, 4), (1, 0, 0))
        self.assertEqual(PRODUCER.fingerprint((19, 23), 4), PRODUCER.fingerprint((35, 39), 4))
        self.assertNotEqual(PRODUCER.fingerprint((19, 23), 4), PRODUCER.fingerprint((20, 23), 4))

    def test_pair_index_replays_recursive_hits(self) -> None:
        curve = PRODUCER.AffineCurve(971, 934, 886)
        sources = [(1, 2), (3, 4), (5, 6)]
        build = PRODUCER.empty_ops()
        d2 = PRODUCER.state_level(curve, sources, 2, build)
        pair_ops = PRODUCER.empty_ops()
        records = PRODUCER.build_pair_records(curve, d2, pair_ops)
        indices = PRODUCER.build_indices(records, [1, 4])
        target = records[0][0]
        recursive, _ = PRODUCER.query_recursive(curve, [None], sources, d2, target, PRODUCER.empty_ops())
        bucketed, _ = PRODUCER.query_pair(curve, [None], sources, indices["buckets"]["1"], target, PRODUCER.empty_ops(), "fingerprint", 2)
        self.assertEqual(recursive, bucketed)

    def test_independent_curve_addition_agrees(self) -> None:
        ops_a = PRODUCER.empty_ops(); ops_b = VERIFIER.empty_ops()
        point = PRODUCER.AffineCurve(971, 934, 886).add((12, 345), (67, 89), ops_a)
        other = VERIFIER.Curve(971, 934, 886).add((12, 345), (67, 89), ops_b)
        self.assertEqual(point, other)

    def test_malformed_protocol_fails_closed(self) -> None:
        raw = {"protocol": "wrong", "source": {}, "config": {}, "summary": {}}
        self.assertFalse(VERIFIER.check(raw, Path(__file__))["protocol"])


if __name__ == "__main__":
    unittest.main()
