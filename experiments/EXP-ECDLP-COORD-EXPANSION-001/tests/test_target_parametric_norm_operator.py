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


PRODUCER = load("target_parametric_norm_operator_test", ROOT / "target_parametric_norm_operator.py")
VERIFIER = load("verify_target_parametric_norm_operator_test", ROOT / "verify_target_parametric_norm_operator.py")


class TargetParametricNormOperatorTests(unittest.TestCase):
    def test_target_coefficients_reconstruct_affine_norm(self) -> None:
        p, nu = 101, 2
        target = (7, 11)
        output = (19, 23)
        c = PRODUCER.coefficients(target, p, nu)
        features = [1, output[0], output[1], output[0] ** 2 - nu * output[1] ** 2, 0]
        expected = ((output[0] - target[0]) ** 2 - nu * (output[1] - target[1]) ** 2) % p
        self.assertEqual(sum(a * b for a, b in zip(c, features)) % p, expected)

    def test_rank_one_feature_is_rank_one(self) -> None:
        self.assertEqual(PRODUCER.rank_profile([1] * 12, [2, 3, 2], 101), {"1": 1, "2": 1})

    def test_independent_point_addition_agrees(self) -> None:
        a = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        b = {"point_add_calls": 0, "field_inversions": 0, "field_multiplications": 0}
        left, right = (12, 345), (67, 89)
        self.assertEqual(
            PRODUCER.AffineCurve(971, 934, 886).add(left, right, a),
            VERIFIER.Curve(971, 934).add(left, right, b),
        )

    def test_mutation_rejects_protocol(self) -> None:
        raw = {"protocol": "wrong", "source": {}, "config": {}, "summary": {}, "rows": []}
        self.assertFalse(VERIFIER.check(raw, Path(__file__))["protocol"])


if __name__ == "__main__":
    unittest.main()
