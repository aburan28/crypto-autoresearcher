"""Construct deterministic Koblitz prime-subgroup fixtures for input selection.

This is field and group arithmetic, not an ECDLP experiment. It certifies an
irreducible binary field polynomial and checks each projected point's curve
equation and exact prime order. The prime divisors come from the separately
recorded Koblitz candidate screen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "research/icperf_koblitz_subgroup_candidates_20261017/candidates.json"


def rem(a: int, f: int) -> int:
    n = f.bit_length() - 1
    while a.bit_length() > n:
        a ^= f << (a.bit_length() - n - 1)
    return a


def mul(a: int, b: int, f: int) -> int:
    n = f.bit_length() - 1
    z = 0
    while b:
        if b & 1:
            z ^= a
        b >>= 1
        a <<= 1
        if a >> n:
            a ^= f
    return z


def inv(a: int, f: int) -> int:
    assert a
    u, v, g1, g2 = a, f, 1, 0
    while u != 1:
        j = u.bit_length() - v.bit_length()
        if j < 0:
            u, v = v, u
            g1, g2 = g2, g1
            j = -j
        u ^= v << j
        g1 ^= g2 << j
    result = rem(g1, f)
    assert mul(a, result, f) == 1
    return result


def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, rem(a, b)
    return a


def trinomial(n: int) -> tuple[int, int]:
    # n=71 and 73 are prime; Rabin's test has only the divisor n to check.
    assert n in (71, 73)
    for k in range(1, n):
        f = (1 << n) | (1 << k) | 1
        x = 2
        for _ in range(n):
            x = mul(x, x, f)
        if x == 2 and gcd(0b110, f) == 1:  # x^2 + x over GF(2)
            return k, f
    raise AssertionError("no irreducible trinomial found")


def square(a: int, f: int) -> int:
    return mul(a, a, f)


def trace(a: int, n: int, f: int) -> int:
    t = 0
    for _ in range(n):
        t ^= a
        a = square(a, f)
    assert t in (0, 1)
    return t


def halftrace(a: int, n: int, f: int) -> int:
    assert n & 1
    original = a
    z = 0
    for _ in range((n + 1) // 2):
        z ^= a
        a = square(square(a, f), f)
    assert trace(original, n, f) == 0
    assert square(z, f) ^ z == original
    return z


Point = tuple[int, int] | None


def on_curve(p: Point, a: int, f: int) -> bool:
    if p is None:
        return True
    x, y = p
    lhs = square(y, f) ^ mul(x, y, f)
    rhs = mul(square(x, f), x, f) ^ (a * square(x, f)) ^ 1
    return lhs == rhs


def add(p: Point, q: Point, a: int, f: int) -> Point:
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
        lam = x1 ^ mul(y1, inv(x1, f), f)
        x3 = square(lam, f) ^ lam ^ a
        y3 = square(x1, f) ^ mul(lam ^ 1, x3, f)
    else:
        lam = mul(y1 ^ y2, inv(x1 ^ x2, f), f)
        x3 = square(lam, f) ^ lam ^ x1 ^ x2 ^ a
        y3 = mul(lam, x1 ^ x3, f) ^ x3 ^ y1
    result = (x3, y3)
    assert on_curve(result, a, f)
    return result


def scale(k: int, p: Point, a: int, f: int) -> Point:
    result = None
    while k:
        if k & 1:
            result = add(result, p, a, f)
        p = add(p, p, a, f)
        k >>= 1
    return result


def lift_x(x: int, a: int, n: int, f: int) -> Point:
    if x == 0:
        return (0, 1)
    x2_inv = inv(square(x, f), f)
    b = x ^ a ^ x2_inv
    if trace(b, n, f):
        return None
    z = halftrace(b, n, f)
    p = (x, mul(x, z, f))
    assert on_curve(p, a, f)
    return p


def fixture(a: int, n: int, order: int, r: int) -> dict:
    k, f = trinomial(n)
    h = order // r
    assert h * r == order
    for x in range(1, 1025):
        p = lift_x(x, a, n, f)
        if p is None:
            continue
        g = scale(h, p, a, f)
        if g is None:
            continue
        assert on_curve(g, a, f)
        assert scale(r, g, a, f) is None
        assert scale(order, p, a, f) is None
        return {"a": a, "field_degree": n, "field_polynomial": f,
                "field_polynomial_exponents": [n, k, 0],
                "irreducibility_test": "Rabin: x^(2^n)=x mod f and gcd(x^2-x,f)=1; n prime",
                "group_order": order, "prime_order": r, "cofactor": h,
                "source_x": x, "source_point": list(p), "generator": list(g),
                "checks": ["curve equation for source and generator",
                           "cofactor times source equals generator",
                           "r times generator is identity",
                           "group order times source is identity"]}
    raise AssertionError(f"no subgroup point found within 1024 x values for {(a, n)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    candidate_bytes = CANDIDATES.read_bytes()
    candidate_record = json.loads(candidate_bytes)
    fixtures = []
    for row in candidate_record["rows"]:
        for candidate in row["certified_candidates"]:
            fixtures.append(fixture(row["a"], row["field_degree"],
                                    row["group_order"], candidate["prime_order"]))
    assert len(fixtures) == 3
    record = {"schema": "icperf-koblitz-subgroup-fixture-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "candidate_record_sha256": hashlib.sha256(candidate_bytes).hexdigest(),
              "fixtures": fixtures,
              "scope": "deterministic point construction and arithmetic checks; input selection only"}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "fixtures": len(fixtures)}, sort_keys=True))


if __name__ == "__main__":
    main()
