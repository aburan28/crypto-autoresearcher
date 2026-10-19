"""Construct a point and Hasse-unique group-order proof for the selected curve.

The bounded Sage screen selects b; this independent GF(2^61) arithmetic
constructs a nonzero prime-order generator. Hasse's interval then determines
the whole curve order because only one multiple of r lies in that interval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from math import isqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_koblitz_subgroup_fixture import halftrace, inv, mul, trace  # noqa: E402
from tools.icperf_koblitz_size_screen import prime64  # noqa: E402

SCREEN = ROOT / "research/icperf_ordinary_binary_fixture_20261017/screen.json"
FIELD_DEGREE = 61
FIELD_POLYNOMIAL = (1 << 61) | (1 << 5) | (1 << 2) | (1 << 1) | 1


def square(v: int) -> int:
    return mul(v, v, FIELD_POLYNOMIAL)


def on_curve(point: tuple[int, int] | None, b: int) -> bool:
    if point is None:
        return True
    x, y = point
    return square(y) ^ mul(x, y, FIELD_POLYNOMIAL) == mul(square(x), x, FIELD_POLYNOMIAL) ^ b


def add(p: tuple[int, int] | None, q: tuple[int, int] | None, b: int):
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2:
        if y1 != y2 or x1 == 0:
            assert y1 ^ y2 == x1 or (x1 == 0 and y1 == y2)
            return None
        lam = x1 ^ mul(y1, inv(x1, FIELD_POLYNOMIAL), FIELD_POLYNOMIAL)
        x3 = square(lam) ^ lam
        y3 = square(x1) ^ mul(lam ^ 1, x3, FIELD_POLYNOMIAL)
    else:
        lam = mul(y1 ^ y2, inv(x1 ^ x2, FIELD_POLYNOMIAL), FIELD_POLYNOMIAL)
        x3 = square(lam) ^ lam ^ x1 ^ x2
        y3 = mul(lam, x1 ^ x3, FIELD_POLYNOMIAL) ^ x3 ^ y1
    result = (x3, y3)
    assert on_curve(result, b)
    return result


def scale(k: int, point: tuple[int, int] | None, b: int):
    result = None
    while k:
        if k & 1:
            result = add(result, point, b)
        point = add(point, point, b)
        k >>= 1
    return result


def lift_x(x: int, b: int):
    assert x != 0
    beta = x ^ mul(b, inv(square(x), FIELD_POLYNOMIAL), FIELD_POLYNOMIAL)
    if trace(beta, FIELD_DEGREE, FIELD_POLYNOMIAL):
        return None
    z = halftrace(beta, FIELD_DEGREE, FIELD_POLYNOMIAL)
    point = (x, mul(x, z, FIELD_POLYNOMIAL))
    assert on_curve(point, b)
    return point


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    screen_bytes = SCREEN.read_bytes()
    screen = json.loads(screen_bytes)
    selected = screen["rows"][-1]
    b = selected["b_polynomial_bits"]
    order = selected["group_order"]
    r, = selected["certified_prime_candidates"]
    assert b == 31 and prime64(r) and order % r == 0
    h = order // r
    q = 1 << FIELD_DEGREE
    hasse_bound = isqrt(4 * q)
    lower_multiple = (q + 1 - hasse_bound + r - 1) // r
    upper_multiple = (q + 1 + hasse_bound) // r
    assert lower_multiple == upper_multiple == h == 4
    for x in range(1, 1025):
        p = lift_x(x, b)
        if p is None:
            continue
        g = scale(h, p, b)
        if g is None:
            continue
        assert on_curve(g, b)
        assert scale(r, g, b) is None
        assert scale(order, p, b) is None
        break
    else:
        raise AssertionError("no prime-order point within 1024 x values")
    record = {"schema": "icperf-ordinary-binary-fixture-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "reused_field_source_sha256": hashlib.sha256((ROOT / "tools/icperf_koblitz_subgroup_fixture.py").read_bytes()).hexdigest(),
              "reused_prime_source_sha256": hashlib.sha256((ROOT / "tools/icperf_koblitz_size_screen.py").read_bytes()).hexdigest(),
              "screen_sha256": hashlib.sha256(screen_bytes).hexdigest(),
              "field_degree": FIELD_DEGREE,
              "field_polynomial": FIELD_POLYNOMIAL,
              "field_polynomial_exponents": [61, 5, 2, 1, 0],
              "curve_equation": "y^2 + xy = x^3 + b",
              "b_polynomial_bits": b, "j_not_in_f2": True,
              "group_order": order, "prime_order": r, "cofactor": h,
              "source_x": x, "source_point": list(p), "generator": list(g),
              "hasse": {"field_order": q, "integer_bound_floor_2_sqrt_q": hasse_bound,
                        "only_multiple_index_in_interval": h},
              "checks": ["irreducible field polynomial in Sage screen",
                         "prime r via deterministic MR64",
                         "source and generator curve equations",
                         "cofactor times source equals generator",
                         "r times generator is identity",
                         "one multiple of r in Hasse interval, so curve order is h*r"],
              "scope": "exact subgroup and group-order input certification; no IC trial"}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "prime_order": r,
                      "cofactor": h}, sort_keys=True))


if __name__ == "__main__":
    main()
