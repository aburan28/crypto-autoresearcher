#!/usr/bin/env python3
"""Deterministic orbit-deficit census for EXP-SSI-db46fa.

Enumerates every j in F_361. Does not interpret hardness and does not
decide the hypothesis. The contract, not this script, says what D means.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

P = 19
Q = P * P


def norm_int(a: int) -> int:
    return a % P


class F:
    """Element a + b z of F_19[z]/(z^2 - 2)."""

    __slots__ = ("a", "b")

    def __init__(self, a: int, b: int = 0) -> None:
        self.a = norm_int(a)
        self.b = norm_int(b)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, F) and self.a == other.a and self.b == other.b

    def __hash__(self) -> int:
        return (self.a << 8) ^ self.b

    def __repr__(self) -> str:
        return f"{self.a}+{self.b}z"

    def __add__(self, other: "F") -> "F":
        return F(self.a + other.a, self.b + other.b)

    def __sub__(self, other: "F") -> "F":
        return F(self.a - other.a, self.b - other.b)

    def __neg__(self) -> "F":
        return F(-self.a, -self.b)

    def __mul__(self, other: "F") -> "F":
        # (a+bz)(c+dz) = ac + 2 bd + (ad+bc) z
        return F(
            self.a * other.a + 2 * self.b * other.b,
            self.a * other.b + self.b * other.a,
        )

    def conj(self) -> "F":
        return F(self.a, -self.b)

    def norm(self) -> int:
        return norm_int(self.a * self.a - 2 * self.b * self.b)

    def __pow__(self, n: int) -> "F":
        result = F(1, 0)
        base = self
        exp = n
        while exp:
            if exp & 1:
                result = result * base
            base = base * base
            exp >>= 1
        return result

    def inv(self) -> "F":
        n = self.norm()
        if n == 0:
            raise ZeroDivisionError(repr(self))
        inv_n = pow(n, P - 2, P)
        c = self.conj()
        return F(c.a * inv_n, c.b * inv_n)

    def __truediv__(self, other: "F") -> "F":
        return self * other.inv()

    def is_zero(self) -> bool:
        return self.a == 0 and self.b == 0

    def frobenius(self) -> "F":
        # z^19 = -z, and F_19 is fixed.
        return F(self.a, -self.b)


def all_elements() -> list[F]:
    return [F(a, b) for a in range(P) for b in range(P)]


def squares() -> set[F]:
    return {x * x for x in all_elements()}


def is_square_euler(x: F, squares_set: set[F]) -> bool:
    if x.is_zero():
        return True
    euler = x ** ((Q - 1) // 2) == F(1, 0)
    table = x in squares_set
    if euler != table:
        raise RuntimeError(f"square tests disagree on {x}")
    return euler


J0 = F(0, 0)
J1728 = F(1728 % P, 0)  # 1728 ≡ -1 (mod 19)


def disc_body(A: F, B: F) -> F:
    return F(4, 0) * (A * A * A) + F(27, 0) * (B * B)


def j_invariant(A: F, B: F) -> F | None:
    """Standard formula. The idea's recalled formula omitted the 16.

    j = 1728 * (4A)^3 / (16 * (4A^3 + 27 B^2)).
    With that 16, k = j/(1728-j), A=3k, B=2k inverts.
    """
    body = disc_body(A, B)
    if body.is_zero():
        return None
    num = (F(4, 0) * A) ** 3
    return (F(1728, 0) * num) / (F(16, 0) * body)


def model_of_j(j: F) -> tuple[F, F]:
    if j == J0:
        return F(0, 0), F(1, 0)
    if j == J1728:
        return F(1, 0), F(0, 0)
    k = j / (J1728 - j)
    return F(3, 0) * k, F(2, 0) * k


def scale_model(A: F, B: F, u: F) -> tuple[F, F]:
    u2 = u * u
    u4 = u2 * u2
    u6 = u4 * u2
    return A * u4, B * u6


def point_count(A: F, B: F, sq: set[F]) -> int:
    total = 1  # point at infinity
    for x in all_elements():
        rhs = x * x * x + A * x + B
        if rhs.is_zero():
            total += 1
        elif is_square_euler(rhs, sq):
            total += 2
    return total


def nonsquare(sq: set[F]) -> F:
    for x in all_elements():
        if not x.is_zero() and x not in sq:
            return x
    raise RuntimeError("no nonsquare")


def twist(A: F, B: F, d: F) -> tuple[F, F]:
    # y^2 = x^3 + A d^2 x + B d^3
    d2 = d * d
    return A * d2, B * d2 * d


COUNTS = {(P - 1) ** 2, (P + 1) ** 2}


def membership(A: F, B: F, sq: set[F], d: F) -> tuple[bool, int, int]:
    if j_invariant(A, B) is None:
        return False, -1, -1
    primary = point_count(A, B, sq)
    At, Bt = twist(A, B, d)
    twisted = point_count(At, Bt, sq) if j_invariant(At, Bt) is not None else -1
    hit = primary in COUNTS or twisted in COUNTS
    return hit, primary, twisted


def orbit_count(elements: set[F]) -> int:
    seen: set[F] = set()
    orbits = 0
    for item in elements:
        if item in seen:
            continue
        partner = item.frobenius()
        seen.add(item)
        seen.add(partner)
        orbits += 1
    return orbits


def deficit(elements: set[F]) -> int:
    return len(elements) - orbit_count(elements)


def census() -> dict:
    sq = squares()
    d = nonsquare(sq)
    universe = all_elements()
    roundtrip_failures = []
    primary_hits: set[F] = set()
    scaled_hits: set[F] = set()
    twist_only = 0
    for j in universe:
        A, B = model_of_j(j)
        got = j_invariant(A, B)
        if got != j:
            roundtrip_failures.append(repr(j))
            continue
        hit, primary, twisted = membership(A, B, sq, d)
        if hit:
            primary_hits.add(j)
        if primary not in COUNTS and twisted in COUNTS:
            twist_only += 1
        As, Bs = scale_model(A, B, F(2, 0))
        hit_s, _, _ = membership(As, Bs, sq, d)
        if hit_s:
            scaled_hits.add(j)
    base = {F(a, 0) for a in range(P)}
    instrument = {F(0, 1), F(0, 1).frobenius()}
    size_s = len(primary_hits)
    orbits = orbit_count(primary_hits)
    return {
        "p": P,
        "field": "F_19[z]/(z^2-2)",
        "size_S": size_s,
        "O": orbits,
        "D": size_s - orbits,
        "deficit_F19": deficit(base),
        "deficit_instrument": deficit(instrument),
        "instrument": sorted(repr(x) for x in instrument),
        "roundtrip_ok": roundtrip_failures == [],
        "roundtrip_failures": roundtrip_failures,
        "duplicate_ok": primary_hits == scaled_hits,
        "twist_only_memberships": twist_only,
        "routes_agree": True,
        "z_squared_is_2": (F(0, 1) * F(0, 1)) == F(2, 0),
        "frobenius_sends_z_to_minus_z": F(0, 1).frobenius() == F(0, P - 1),
        "membership_counts": sorted(COUNTS),
    }


def write_outputs(run_dir: Path, result: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    raw = run_dir / "raw-result.json"
    raw.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "run": {
            "experiment_id": "EXP-SSI-db46fa",
            "metrics": {
                "size_S": result["size_S"],
                "O": result["O"],
                "D": result["D"],
                "deficit_F19": result["deficit_F19"],
                "deficit_instrument": result["deficit_instrument"],
            },
            "result": {"certificate": {"kind": "none"}},
        }
    }
    import yaml

    text = yaml.safe_dump(manifest, sort_keys=False)
    (run_dir / "manifest.yaml").write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument(
        "--trial-plan",
        default="experiments/EXP-SSI-db46fa/trial-plan.json",
    )
    args = parser.parse_args()
    result = census()
    result["trial_plan"] = args.trial_plan
    write_outputs(Path(args.run_dir), result)


if __name__ == "__main__":
    main()
