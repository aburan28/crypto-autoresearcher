#!/usr/bin/env python3
"""Recompute the EXP-SSI-db46fa census and compare it to raw-result.json.

Independent of run.py: the arithmetic below is copied, not imported.
A mismatch is an instrument failure, not a scientific verdict.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

P = 19


def n(a: int) -> int:
    return a % P


class F:
    __slots__ = ("a", "b")

    def __init__(self, a: int, b: int = 0) -> None:
        self.a = n(a)
        self.b = n(b)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, F) and (self.a, self.b) == (other.a, other.b)

    def __hash__(self) -> int:
        return (self.a << 8) ^ self.b

    def __add__(self, other: "F") -> "F":
        return F(self.a + other.a, self.b + other.b)

    def __sub__(self, other: "F") -> "F":
        return F(self.a - other.a, self.b - other.b)

    def __mul__(self, other: "F") -> "F":
        return F(
            self.a * other.a + 2 * self.b * other.b,
            self.a * other.b + self.b * other.a,
        )

    def __pow__(self, exp: int) -> "F":
        result = F(1, 0)
        base = self
        while exp:
            if exp & 1:
                result = result * base
            base = base * base
            exp >>= 1
        return result

    def inv(self) -> "F":
        norm = n(self.a * self.a - 2 * self.b * self.b)
        inv_n = pow(norm, P - 2, P)
        return F(self.a * inv_n, -self.b * inv_n)

    def __truediv__(self, other: "F") -> "F":
        return self * other.inv()

    def zero(self) -> bool:
        return self.a == 0 and self.b == 0

    def frob(self) -> "F":
        return F(self.a, -self.b)


def elements() -> list[F]:
    return [F(a, b) for a in range(P) for b in range(P)]


def j_of(A: F, B: F) -> F | None:
    body = F(4, 0) * (A * A * A) + F(27, 0) * (B * B)
    if body.zero():
        return None
    num = (F(4, 0) * A) ** 3
    return (F(1728, 0) * num) / (F(16, 0) * body)


def model(j: F) -> tuple[F, F]:
    j1728 = F(1728 % P, 0)
    if j == F(0, 0):
        return F(0, 0), F(1, 0)
    if j == j1728:
        return F(1, 0), F(0, 0)
    k = j / (j1728 - j)
    return F(3, 0) * k, F(2, 0) * k


def squares() -> set[F]:
    return {x * x for x in elements()}


def count(A: F, B: F, sq: set[F]) -> int:
    total = 1
    half = (P * P - 1) // 2
    for x in elements():
        rhs = x * x * x + A * x + B
        if rhs.zero():
            total += 1
        elif (rhs ** half) == F(1, 0) and rhs in sq:
            total += 2
        elif (rhs ** half) == F(1, 0) or rhs in sq:
            raise SystemExit("square tests disagree")
    return total


def orbits(items: set[F]) -> int:
    seen: set[F] = set()
    found = 0
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        seen.add(item.frob())
        found += 1
    return found


def recompute() -> dict:
    sq = squares()
    d = next(x for x in elements() if not x.zero() and x not in sq)
    targets = {(P - 1) ** 2, (P + 1) ** 2}
    hits: set[F] = set()
    for j in elements():
        A, B = model(j)
        if j_of(A, B) != j:
            raise SystemExit(f"roundtrip failed for {j.a}+{j.b}z")
        primary = count(A, B, sq)
        d2 = d * d
        At, Bt = A * d2, B * d2 * d
        twisted = count(At, Bt, sq)
        if primary in targets or twisted in targets:
            hits.add(j)
    base = {F(a, 0) for a in range(P)}
    instrument = {F(0, 1), F(0, P - 1)}
    return {
        "size_S": len(hits),
        "O": orbits(hits),
        "D": len(hits) - orbits(hits),
        "deficit_F19": len(base) - orbits(base),
        "deficit_instrument": len(instrument) - orbits(instrument),
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check.py RUN_DIR")
    run_dir = Path(sys.argv[1])
    raw_path = run_dir / "raw-result.json"
    manifest_path = run_dir / "manifest.yaml"
    if not raw_path.is_file() or not manifest_path.is_file():
        raise SystemExit("missing manifest.yaml or raw-result.json")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    again = recompute()
    for key, value in again.items():
        if raw.get(key) != value:
            raise SystemExit(f"mismatch {key}: file {raw.get(key)!r} recomputed {value!r}")
    if raw.get("deficit_F19") != 0 or raw.get("deficit_instrument") != 1:
        raise SystemExit("instrument deficit is not 0 and 1")
    if raw.get("roundtrip_ok") is not True or raw.get("duplicate_ok") is not True:
        raise SystemExit("roundtrip or duplicate control failed")
    if raw.get("z_squared_is_2") is not True:
        raise SystemExit("z^2 is not 2")
    if raw.get("frobenius_sends_z_to_minus_z") is not True:
        raise SystemExit("Frobenius did not send z to -z")


if __name__ == "__main__":
    main()
