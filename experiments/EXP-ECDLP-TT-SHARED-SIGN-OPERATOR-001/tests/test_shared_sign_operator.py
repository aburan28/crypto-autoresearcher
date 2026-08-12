from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LOCATOR = load("shared_sign_locator_test", ROOT / "src" / "shared_sign_locator.py")


class TinyCurve:
    p = 101

    def add(self, left, right, ops):
        return (0, 0) if left == right else (1, 1)


def test_paired_generic_branches_match_direct_curve_arithmetic():
    curve = LOCATOR.ORBIT.STREAMING.ORACLE.Curve(101, 2)
    left = (3, 6)
    right = (1, 39)
    ops = LOCATOR.ORBIT.zero_ops()
    plus, minus = LOCATOR.paired_affine_add(curve, left, right, ops)
    direct_plus = curve.add(left, right, LOCATOR.ORBIT.zero_ops())
    direct_minus = curve.add(left, LOCATOR.ORBIT.neg_point(right, curve.p, LOCATOR.ORBIT.zero_ops()), LOCATOR.ORBIT.zero_ops())
    assert plus == direct_plus
    assert minus == direct_minus
    assert ops["paired_shared_inversions"] == 1


def test_paired_identity_and_diagonal_fallbacks_are_defined():
    curve = LOCATOR.ORBIT.STREAMING.ORACLE.Curve(101, 2)
    ops = LOCATOR.ORBIT.zero_ops()
    assert LOCATOR.paired_affine_add(curve, None, (3, 6), ops) == ((3, 6), (3, 6))
    assert LOCATOR.paired_affine_add(curve, (3, 6), None, ops) == ((3, 6), (3, 6))
    plus, minus = LOCATOR.paired_affine_add(curve, (3, 6), (3, 6), ops)
    assert plus == curve.add((3, 6), (3, 6), LOCATOR.ORBIT.zero_ops())
    assert minus == curve.add((3, 6), LOCATOR.ORBIT.neg_point((3, 6), 101, LOCATOR.ORBIT.zero_ops()), LOCATOR.ORBIT.zero_ops())
    assert ops["paired_fallback_calls"] == 1
