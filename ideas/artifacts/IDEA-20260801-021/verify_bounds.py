#!/usr/bin/env python3
"""Small exact checks for the elementary bounds in IDEA-20260801-021.

This is a validation aid, not evidence at cryptographic scale.  It enumerates
prime-field elliptic curves with prime group order, checks a few low-degree
predicates against the 3d Bezout ceiling, and checks exact m-fold sumset image
cardinality against the tuple bound.
"""

from __future__ import annotations

from itertools import product


Point = tuple[int, int] | None


def inv_mod(x: int, p: int) -> int:
    return pow(x % p, -1, p)


def add(P: Point, Q: Point, p: int, a: int) -> Point:
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = ((3 * x1 * x1 + a) * inv_mod(2 * y1, p)) % p
    else:
        lam = ((y2 - y1) * inv_mod(x2 - x1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return x3, y3


def points(p: int, a: int, b: int) -> list[Point]:
    out: list[Point] = [None]
    for x in range(p):
        for y in range(p):
            if (y * y - (x * x * x + a * x + b)) % p == 0:
                out.append((x, y))
    return out


def predicate_values(P: Point, degree: int, kind: int, p: int) -> int:
    if P is None:
        # The polynomial predicate is affine; the point at infinity is not in
        # this factor-base definition.  Return a nonzero sentinel so it is not
        # selected below.
        return 1
    x, y = P
    if degree == 1 and kind == 0:
        return (x - 1) % p  # x - 1
    if degree == 1 and kind == 1:
        return (y - 1) % p  # y - 1
    if degree == 2 and kind == 0:
        return (x * x + y - 1) % p  # x^2 + y - 1
    raise ValueError((degree, kind))


def sumset(F: list[Point], m: int, p: int, a: int) -> set[Point]:
    reachable: set[Point] = set()
    for tup in product(F, repeat=m):
        cur: Point = None
        for Q in tup:
            cur = add(cur, Q, p, a)
        reachable.add(cur)
    return reachable


def main() -> None:
    curve_checks = 0
    sumset_checks = 0
    for p in (5, 7, 11, 13, 17, 19, 23):
        for a in range(p):
            for b in range(p):
                if (4 * a * a * a + 27 * b * b) % p == 0:
                    continue
                G = points(p, a, b)
                N = len(G)
                if N <= 2 or not all(N % q for q in range(2, int(N**0.5) + 1)):
                    continue
                for degree, kinds in ((1, (0, 1)), (2, (0,))):
                    for kind in kinds:
                        F = [Q for Q in G if predicate_values(Q, degree, kind, p) == 0]
                        assert len(F) <= 3 * degree, (p, a, b, degree, kind, len(F))
                        curve_checks += 1
                        for m in (1, 2, 3):
                            image = sumset(F, m, p, a)
                            assert len(image) <= len(F) ** m
                            sumset_checks += 1
    print(f"PASS curve_checks={curve_checks} sumset_checks={sumset_checks}")


if __name__ == "__main__":
    main()
