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


LOCATOR = load("projective_shared_sign_test", ROOT / "src" / "projective_shared_sign_locator.py")


def affine(point, p):
    if point is None:
        return None
    x, y, z = point
    inverse = pow(z, -1, p)
    return x * inverse * inverse % p, y * inverse * inverse * inverse % p


def test_projective_pair_reconstructs_both_signs():
    curve = LOCATOR.ORBIT.STREAMING.ORACLE.Curve(101, 2)
    left = (13, 1)
    right = (16, 47)
    ops = LOCATOR.ORBIT.zero_ops()
    pair = LOCATOR.paired_projective_add(curve, left, right, ops)
    assert affine(pair.plus, 101) == curve.add(left, right, LOCATOR.ORBIT.zero_ops())
    assert affine(pair.minus, 101) == curve.add(left, LOCATOR.ORBIT.neg_point(right, 101, LOCATOR.ORBIT.zero_ops()), LOCATOR.ORBIT.zero_ops())
    assert ops["paired_projective_calls"] == 1
    assert ops["field_inversions"] == 0


def test_projective_homogeneous_predicate_has_source_only_scale():
    curve = LOCATOR.ORBIT.STREAMING.ORACLE.Curve(101, 2)
    target = (14, 67)
    nu = 3
    pair = LOCATOR.paired_projective_add(curve, (13, 1), (16, 47), LOCATOR.ORBIT.zero_ops())
    for point in (pair.plus, pair.minus):
        affine_point = affine(point, 101)
        dx = (affine_point[0] - target[0]) % 101
        dy = (affine_point[1] - target[1]) % 101
        affine_value = (dx * dx - nu * dy * dy) % 101
        projective_value = LOCATOR.projective_predicate(point, pair.z2, pair.z3, target, 101, nu, LOCATOR.ORBIT.zero_ops())
        scale = pow(point[2], 6, 101)
        assert projective_value == affine_value * scale % 101
