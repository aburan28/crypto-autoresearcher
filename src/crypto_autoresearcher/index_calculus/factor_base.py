"""Factor bases over E(F_p).

A factor base is a set of points, one representative per +/- pair, given by a
predicate on the x-coordinate.  Three families are provided:

* ``small_x``   -- the |F| points of smallest x: Semaev's prime-field proposal;
* ``subgroup``  -- x in a coset g * mu_d of the order-d subgroup of F_p^*
  (membership is the sparse, high-degree equation x^d = g^d);
* ``random``    -- a seeded random set of x-coordinates, the null control;
* ``dickson``   -- x = u + c/u for u in a coset g * mu_d (membership is the
  Dickson equation D_d(x, c) = lambda, lambda = g^d + c^d g^-d);
* ``known_log`` -- the small multiples j*P, j = 1..|F| (H017 control: every
  logarithm is known).  Built only by the census panel; not in FACTOR_BASES.

Each base also exposes its membership polynomial, the equation an algebraic
solver is given: prod (x - x_j) over the base for ``small_x`` and ``random``
(dense, degree |F|), and x^d - g^d for ``subgroup`` (two terms, degree d, about
twice |F| since roughly half of the coset are x-coordinates of points).
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from .curve import Curve, Point, divisors, primitive_root

FACTOR_BASES = ("small_x", "subgroup", "random", "dickson")


def default_fb_size(N: int, m: int) -> int:
    """|F| giving about one decomposition per two attempts.

    A random target is a sum of m signed factor-base points with probability
    about (2|F|)^m / (m! N), so |F| = ((m! N) / 2)^(1/m) / 2.
    """
    return max(4, math.ceil((math.factorial(m) * N / 2) ** (1 / m) / 2))


def nearest_divisor(n: int, target: float) -> int:
    """The divisor of n closest to target (ties go to the smaller one)."""
    return min(divisors(n), key=lambda d: (abs(d - target), d))


def _base_divisor(p: int, size: int, divisor_multiple_of: int) -> int:
    """d | p - 1 for a coset base: the divisor closest to 2 * size (ties to the
    smaller) among the multiples of ``divisor_multiple_of``."""
    if divisor_multiple_of == 1:
        return nearest_divisor(p - 1, 2 * size)
    ds = [d for d in divisors(p - 1) if d % divisor_multiple_of == 0]
    if not ds:
        raise ValueError(f"p - 1 = {p - 1} has no divisor that is a multiple of "
                         f"{divisor_multiple_of}")
    return min(ds, key=lambda d: (abs(d - 2 * size), d))


def dickson_value(x: int, c: int, d: int, p: int) -> int:
    """D_d(x, c) mod p by the recurrence D_n = x D_{n-1} - c D_{n-2}, D_0 = 2, D_1 = x."""
    if d == 0:
        return 2 % p
    a, b = 2 % p, x % p
    for _ in range(d - 1):
        a, b = b, (x * b - c * a) % p
    return b


def dickson_coefficients(d: int, c: int, p: int) -> dict[int, int]:
    """D_d(x, c) = sum_{i=0}^{floor(d/2)} d/(d-i) C(d-i, i) (-c)^i x^(d-2i), mod p."""
    out: dict[int, int] = {}
    for i in range(d // 2 + 1):
        coef = d * math.comb(d - i, i) // (d - i)  # exact integer
        v = coef % p * pow(-c % p, i, p) % p
        if v:
            out[d - 2 * i] = (out.get(d - 2 * i, 0) + v) % p
    return out


def subgroup_prime_filter(arities: Iterable[int], tolerance: float = 0.15,
                          sizes: Iterable[int] = ()) -> Callable[[int], bool]:
    """Accept p when p - 1 can host a fair subgroup base.

    For every arity m the default size |F| = default_fb_size(p, m) is targeted
    (the group order is p + O(sqrt p), so p stands in for it), and for every
    explicit size s in ``sizes`` the target is s itself.  The subgroup of order
    d contributes about d/2 points, so p is accepted when each target t has a
    divisor d of p - 1 with |d - 2t| <= tolerance * 2t.
    """
    arities, sizes = tuple(arities), tuple(sizes)

    def accept(p: int) -> bool:
        targets = [default_fb_size(p, m) for m in arities] + list(sizes)
        divs = divisors(p - 1)
        return all(any(abs(d - 2 * t) <= tolerance * 2 * t for d in divs)
                   for t in targets)

    accept.label = f"subgroup(m={list(arities)},sizes={list(sizes)},tol={tolerance})"
    return accept


@dataclass
class FactorBase:
    kind: str
    points: list[Point]
    params: dict = field(default_factory=dict)
    p: int = 0
    index: dict[int, int] = field(init=False, repr=False)
    _arrays: object = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        self.index = {P[0]: i for i, P in enumerate(self.points)}

    def __len__(self) -> int:
        return len(self.points)

    def lookup(self, x: int) -> int | None:
        return self.index.get(x)

    def describe(self) -> dict:
        return {"kind": self.kind, "size": len(self), **self.params}

    def membership_poly(self) -> dict[int, int]:
        """The base's defining equation as {exponent: coefficient mod p}."""
        p = self.p
        if self.kind == "subgroup":
            d, g = self.params["d"], self.params["coset"]
            return {d: 1, 0: (-pow(g, d, p)) % p}
        if self.kind == "dickson":
            d, c, lam = self.params["d"], self.params["c"], self.params["lambda"]
            f = dickson_coefficients(d, c, p)
            f[0] = (f.get(0, 0) - lam) % p
            return {k: v for k, v in f.items() if v}
        if self.kind == "known_log":
            raise NotImplementedError("the known_log base has no membership polynomial")
        coeffs = [1]
        for P in self.points:
            xj = P[0]
            nxt = [0] * (len(coeffs) + 1)
            for k, c in enumerate(coeffs):
                nxt[k + 1] = (nxt[k + 1] + c) % p
                nxt[k] = (nxt[k] - xj * c) % p
            coeffs = nxt
        return {k: c for k, c in enumerate(coeffs) if c}

    def arrays(self):
        """numpy views of the base for the vectorised scan (built once)."""
        if self._arrays is None:
            from . import _accel

            self._arrays = _accel.FBArrays(self)
        return self._arrays

    # -- builders ---------------------------------------------------------
    @classmethod
    def _from_xs(cls, E: Curve, xs, kind: str, params: dict) -> "FactorBase":
        pts = []
        for x in xs:
            P = E.lift_x(x)
            if P is not None and P[1] != 0:
                pts.append(P)
        return cls(kind, pts, params, E.p)

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
        return cls("small_x", pts, {"bound": x}, E.p)

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
        return cls("random", pts, {"seed": seed}, E.p)

    @classmethod
    def subgroup(cls, E: Curve, size: int, seed: int = 0,
                 divisor_multiple_of: int = 1) -> "FactorBase":
        """Points with x in a coset g * mu_d, d | p-1 chosen so |F| ~ size.

        About half of the d coset elements are x-coordinates of points, so d
        is the divisor of p - 1 closest to 2 * size.  How close that can be
        depends on p; ``subgroup_prime_filter`` picks primes where it is close.
        ``divisor_multiple_of`` restricts d to multiples of that number (the
        j = 0 control uses 3); with the default 1 nothing changes.
        """
        p = E.p
        d = _base_divisor(p, size, divisor_multiple_of)
        gen = primitive_root(p)
        zeta = pow(gen, (p - 1) // d, p)
        rng = random.Random(f"fb-subgroup|{p}|{d}|{seed}")
        g = pow(gen, rng.randrange(p - 1), p)
        xs, z = [], g
        for _ in range(d):
            xs.append(z)
            z = z * zeta % p
        params = {"d": d, "coset": g, "seed": seed, "target_size": size}
        if divisor_multiple_of != 1:
            params["divisor_multiple_of"] = divisor_multiple_of
        return cls._from_xs(E, xs, "subgroup", params)

    @classmethod
    def dickson(cls, E: Curve, size: int, seed: int = 0,
                divisor_multiple_of: int = 1) -> "FactorBase":
        """Points with x = u + c/u, u in a coset g * mu_d: D_d(x, c) = lambda.

        d is chosen exactly as for ``subgroup``.  c is drawn until c is not in
        g^2 * mu_d, which makes the d values u + c/u distinct.
        """
        p = E.p
        d = _base_divisor(p, size, divisor_multiple_of)
        gen = primitive_root(p)
        zeta = pow(gen, (p - 1) // d, p)
        rng = random.Random(f"fb-dickson|{p}|{d}|{seed}")
        g = pow(gen, rng.randrange(p - 1), p)
        g_2 = pow(g, -2, p)
        for _ in range(10_000):
            c = rng.randrange(1, p)
            if pow(c * g_2 % p, d, p) != 1:
                break
        else:  # pragma: no cover - needs d = p - 1
            raise ValueError("no Dickson parameter c outside g^2 * mu_d")
        xs, u = [], g
        for _ in range(d):
            xs.append((u + c * pow(u, -1, p)) % p)
            u = u * zeta % p
        assert len(set(xs)) == d, "Dickson preimages must give distinct x"
        lam = (pow(g, d, p) + pow(c, d, p) * pow(g, -d, p)) % p
        params = {"d": d, "coset": g, "c": c, "lambda": lam, "seed": seed, "target_size": size}
        if divisor_multiple_of != 1:
            params["divisor_multiple_of"] = divisor_multiple_of
        return cls._from_xs(E, xs, "dickson", params)

    @classmethod
    def known_log(cls, E: Curve, P, size: int) -> "FactorBase":
        """The H017 small-multiples base F_j = j*P, j = 1..size (log F_j = j).

        Computed on a separate Curve instance, so nothing is charged to E.ops,
        and stored exactly as computed (no y normalisation).
        """
        E2 = Curve(E.p, E.a, E.b, E.order)
        pts, R = [], None
        for _ in range(size):
            R = E2.add(R, P)
            assert R is not None, "j*P is the point at infinity"
            pts.append(R)
        assert len({Pt[0] for Pt in pts}) == len(pts), "known_log x-coordinates must be distinct"
        return cls("known_log", pts, {"logs": f"1..{size}", "note": "H017 small multiples"}, E.p)


def build_factor_base(E: Curve, kind: str, size: int, seed: int = 0) -> FactorBase:
    if kind == "small_x":
        return FactorBase.small_x(E, size)
    if kind == "subgroup":
        return FactorBase.subgroup(E, size, seed)
    if kind == "random":
        return FactorBase.random(E, size, seed)
    if kind == "dickson":
        return FactorBase.dickson(E, size, seed)
    raise ValueError(f"unknown factor base {kind!r}; choose from {FACTOR_BASES}")
