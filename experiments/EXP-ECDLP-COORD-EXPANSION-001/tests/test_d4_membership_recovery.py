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


PRODUCER = load("d4_membership_recovery_test", ROOT / "d4_membership_recovery.py")
VERIFIER = load("verify_d4_membership_recovery_test", ROOT / "verify_d4_membership_recovery.py")


class D4MembershipRecoveryTests(unittest.TestCase):
    def test_support_only_advice_excludes_d4_witness_payload(self) -> None:
        curve = PRODUCER.AffineCurve(971, 934, 886)
        sources = [(1, 2), (3, 4), (5, 6)]
        d2 = PRODUCER.states(curve, sources, 2, PRODUCER.empty_ops())
        d4 = PRODUCER.states(curve, sources, 4, PRODUCER.empty_ops())
        d2_advice = PRODUCER.advice_d2(d2)
        self.assertEqual(PRODUCER.advice_d2(d2)["logical_advice_words"], d2_advice["logical_advice_words"])
        membership = d2_advice["logical_advice_words"] + 2 * len(d4)
        materialized = 2 * len(d4) + 4 * sum(len(value) for value in d4.values())
        self.assertLess(membership, materialized)

    def test_membership_recovery_matches_recursive(self) -> None:
        curve = PRODUCER.AffineCurve(971, 934, 886)
        sources = [(1, 2), (3, 4), (5, 6)]
        d2 = PRODUCER.states(curve, sources, 2, PRODUCER.empty_ops())
        d4 = PRODUCER.states(curve, sources, 4, PRODUCER.empty_ops())
        target = next(iter(d4))
        recovered, _ = PRODUCER.query_membership_recovery(curve, [None], sources, d2, set(d4), target, PRODUCER.empty_ops())
        recursive, _ = PRODUCER.query_recursive(curve, [None], sources, d2, target, PRODUCER.empty_ops())
        self.assertEqual(recovered, recursive)

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
