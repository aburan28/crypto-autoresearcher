"""Factor bases over E(F_p).

A factor base is a set of points, one representative per +/- pair, given by a
predicate on the x-coordinate.  Three families are provided:

* ``small_x``   -- x in [0, bound): Semaev's prime-field proposal;
* ``subgroup``  -- x in a coset g * mu_d of the order-d subgroup of F_p^*
  (a high-degree membership predicate, x^d = g^d);
* ``random``    -- a seeded random set of x-coordinates, the null control.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .curve import Curve, Point


@dataclass
class FactorBase:
    kind: str
    points: list[Point]
    params: dict = field(default_factory=dict)
    index: dict[int, int] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.index = {P[0]: i for i, P in enumerate(self.points)}

    def __len__(self) -> int:
        return len(self.points)

    def lookup(self, x: int) -> int | None:
        return self.index.get(x)

    def describe(self) -> dict:
        return {"kind": self.kind, "size": len(self), **self.params}

    # -- builders ---------------------------------------------------------
    @classmethod
    def _from_xs(cls, E: Curve, xs, kind: str, params: dict) -> "FactorBase":
        pts = []
        for x in xs:
            P = E.lift_x(x)
            if P is not None and P[1] != 0:
                pts.append(P)
        return cls(kind, pts, params)

    @classmethod
    def small_x(cls, E: Curve, size: int) -> "FactorBase":
        """The ``size`` points of smallest x-coordinate."""
        pts: list[Point] = []
        x = 0
        while len(pts) < size and x < E.p:
            P = E.lift_x(x)
            if P is not None and P[1] != 0:
                pts.append(P)
            x += 1
        return cls("small_x", pts, {"bound": x})

    @classmethod
    def random(cls, E: Curve, size: int, seed: int = 0) -> "FactorBase":
        rng = random.Random(f"fb-random|{E.p}|{E.a}|{E.b}|{size}|{seed}")
        pts: list[Point] = []
        seen: set[int] = set()
        while len(pts) < size:
            x = rng.randrange(E.p)
            if x in seen:
                continue
            seen.add(x)
            P = E.lift_x(x)
            if P is not None and P[1] != 0:
                pts.append(P)
        return cls("random", pts, {"seed": seed})

    @classmethod
    def subgroup(cls, E: Curve, size: int, seed: int = 0) -> "FactorBase":
        """Points with x in a coset g * mu_d, d | p-1 chosen so |FB| ~ size.

        About half of the d coset elements are x-coordinates of points, so d
        is the divisor of p - 1 closest to 2 * size.
        """
        p = E.p
        divisors = _divisors(p - 1)
        d = min(divisors, key=lambda t: (abs(t - 2 * size), t))
        gen = _primitive_root(p)
        zeta = pow(gen, (p - 1) // d, p)
        rng = random.Random(f"fb-subgroup|{p}|{d}|{seed}")
        g = pow(gen, rng.randrange(p - 1), p)
        xs, z = [], g
        for _ in range(d):
            xs.append(z)
            z = z * zeta % p
        return cls._from_xs(E, xs, "subgroup", {"d": d, "coset": g, "seed": seed})


def _factor(n: int) -> dict[int, int]:
    f: dict[int, int] = {}
    q = 2
    while q * q <= n:
        while n % q == 0:
            f[q] = f.get(q, 0) + 1
            n //= q
        q += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def _divisors(n: int) -> list[int]:
    divs = [1]
    for q, e in _factor(n).items():
        divs = [d * q**k for d in divs for k in range(e + 1)]
    return sorted(divs)


def _primitive_root(p: int) -> int:
    qs = list(_factor(p - 1))
    g = 2
    while any(pow(g, (p - 1) // q, p) == 1 for q in qs):
        g += 1
    return g
