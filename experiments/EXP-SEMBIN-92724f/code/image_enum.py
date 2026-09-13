#!/usr/bin/env python3
"""Arm D of EXP-SEMBIN-92724f: EXACT image sizes of the typed and untyped
decomposition families, with exact fibre-size distributions.

WHAT IS COUNTED, PRECISELY. Fix a binary curve E/F_{2^n} and an F_2-subspace
V <= F_{2^n} of dimension k.

  untyped family   F      = {P in E(F_{2^n}) : x(P) in V}
                   domain = size-m MULTISETS from F
                   image  = { P_1 + ... + P_m } (group sums), counted exactly
  typed family     F_i    = {P : x(P) in V + v_i}, i = 1..m
                   domain = prod_i F_i  (one point per type, so a typed
                            selection is already unordered-free)
                   image  = { P_1 + ... + P_m : P_i in F_i }, counted exactly

The ratio |typed image| / |untyped image| is the quantity HEUR-YT predicts to
be m!. Nothing here samples: every domain is enumerated in full, and the
enumeration is done as an exact integer convolution over the group, which
returns the FIBRE SIZE of every group element and not merely the image size.

WHY A CONVOLUTION AND NOT itertools.product. The multiplicity function of a
sumset is the convolution of the indicator functions of its summands over the
abelian group E(F_{2^n}). Coordinatising that group as Z_{N1} x Z_{N2} turns
the convolution into integer array shifts, so a domain of 2^18 tuples costs
2^18 integer additions rather than 2^18 curve additions -- and, unlike a
product loop, it yields the complete fibre-size distribution for free. The
coordinatisation is verified exhaustively (bijectivity) and homomorphically
(coords(P+Q) = coords(P) + coords(Q)) before it is used, and the whole
convolution is cross-checked against a direct itertools.product enumeration
with real curve arithmetic at the small cells (`brute_force_image`).

NO DEGREE IS COMPUTED ANYWHERE IN THIS FILE. It counts group elements.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field as dc_field

import numpy as np

from binary_field import GF2m, BinaryCurve, INFINITY


# ---------------------------------------------------------------------------
# F_2-subspaces of F_{2^n}, as spans of explicit bases
# ---------------------------------------------------------------------------
def span(basis: list[int]) -> list[int]:
    """All 2^len(basis) F_2-combinations of `basis`, in Gray-free index order."""
    out = [0]
    for b in basis:
        out += [v ^ b for v in out]
    return out


def is_independent(basis: list[int]) -> bool:
    """Gaussian elimination over F_2 on the packed integers."""
    rows: list[int] = []
    for b in basis:
        v = b
        for r in rows:
            v = min(v, v ^ r)
        if v == 0:
            return False
        rows.append(v)
        rows.sort(reverse=True)
    return True


def is_subspace(elements: set[int]) -> bool:
    """Closed under xor and containing 0 -- the definition, tested directly."""
    if 0 not in elements:
        return False
    els = sorted(elements)
    for a in els:
        for b in els:
            if a ^ b not in elements:
                return False
    return True


def low_degree_basis(k: int) -> list[int]:
    """V = {polynomials in alpha of degree < k}, Semaev section 4.5's choice."""
    return [1 << i for i in range(k)]


def random_basis(rng, n: int, k: int) -> list[int]:
    """k independent random elements of F_{2^n}, rejection-sampled."""
    while True:
        cand = [int(rng.integers(1, 1 << n)) for _ in range(k)]
        if is_independent(cand):
            return cand


# ---------------------------------------------------------------------------
# The group E(F_{2^n}), coordinatised so that sums become integer shifts
# ---------------------------------------------------------------------------
def _divisors(n: int) -> list[int]:
    ds = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            ds.append(i)
            if i != n // i:
                ds.append(n // i)
        i += 1
    return sorted(ds)


@dataclass
class GroupModel:
    """E(F_{2^n}) as Z_{N1} x Z_{N2} with an explicit, verified coordinate map."""

    n: int
    a: int
    b: int
    field: GF2m = dc_field(repr=False, default=None)
    curve: BinaryCurve = dc_field(repr=False, default=None)
    points: list = dc_field(repr=False, default_factory=list)
    coords: dict = dc_field(repr=False, default_factory=dict)
    order: int = 0
    n1: int = 0
    n2: int = 0
    verification: dict = dc_field(default_factory=dict)

    @classmethod
    def build(cls, n: int, a: int, b: int) -> "GroupModel":
        f = GF2m(n)
        E = BinaryCurve(f, a, b)
        pts = [INFINITY] + E.affine_points()
        N = len(pts)
        g = cls._max_order_point(E, pts, N)
        n1 = cls._point_order(E, g, N)
        model = cls(n=n, a=a, b=b, field=f, curve=E, points=pts, order=N,
                    n1=n1, n2=N // n1)
        model._coordinatise(g)
        model._verify()
        return model

    # -- group structure ---------------------------------------------------
    @staticmethod
    def _point_order(E: BinaryCurve, p, N: int) -> int:
        for d in _divisors(N):
            if E.mul_scalar(p, d) is INFINITY:
                return d
        raise ArithmeticError("no divisor of the group order annihilates the "
                              "point; the point count is wrong")

    @classmethod
    def _max_order_point(cls, E, pts, N):
        """A point whose order is the group exponent.

        The exponent is the lcm of the orders of enough random elements; a
        point attaining it then exists and is found by scanning. Both steps are
        checked rather than assumed: the returned point's order is recomputed.
        """
        rng = np.random.default_rng(12345)
        expo = 1
        for _ in range(min(40, N - 1)):
            p = pts[int(rng.integers(1, N))]
            expo = math.lcm(expo, cls._point_order(E, p, N))
        for p in pts[1:]:
            if cls._point_order(E, p, N) == expo:
                return p
        raise ArithmeticError("no point attains the computed exponent")

    def _coordinatise(self, g) -> None:
        E = self.curve
        cyc: dict = {}
        cur = INFINITY
        for i in range(self.n1):
            cyc[cur] = i
            cur = E.add(cur, g)
        if cur is not INFINITY:
            raise ArithmeticError("the cyclic walk did not close up")
        self.coords = {p: (i, 0) for p, i in cyc.items()}
        if self.n2 == 1:
            return
        # Non-cyclic: find h with <g> (+) <h> = E, i.e. a complement.
        for h in self.points[1:]:
            if h in cyc:
                continue
            trial: dict = {}
            acc = INFINITY
            ok = True
            for j in range(self.n2):
                shifted = {E.add(p, acc): (i, j) for p, i in cyc.items()}
                if any(p in trial for p in shifted):
                    ok = False
                    break
                trial.update(shifted)
                acc = E.add(acc, h)
            if ok and acc is INFINITY and len(trial) == self.order:
                self.coords = trial
                return
        raise ArithmeticError("no complement found for the cyclic part")

    def _verify(self) -> None:
        """Bijectivity exhaustively; the homomorphism law on a random sample."""
        if len(self.coords) != self.order:
            raise ArithmeticError("coordinate map is not injective")
        if len(set(self.coords.values())) != self.order:
            raise ArithmeticError("coordinate map is not surjective onto "
                                  "Z_N1 x Z_N2")
        rng = np.random.default_rng(777)
        checks = min(3000, self.order * self.order)
        for _ in range(checks):
            p = self.points[int(rng.integers(0, self.order))]
            q = self.points[int(rng.integers(0, self.order))]
            try:
                s = self.curve.add(p, q)
            except ArithmeticError:
                continue
            cp, cq, cs = self.coords[p], self.coords[q], self.coords[s]
            if ((cp[0] + cq[0]) % self.n1, (cp[1] + cq[1]) % self.n2) != cs:
                raise ArithmeticError("coordinate map is not a homomorphism")
        self.verification = {
            "group_order": self.order,
            "structure": f"Z_{self.n1} x Z_{self.n2}",
            "cyclic": self.n2 == 1,
            "bijectivity_checked_exhaustively": True,
            "homomorphism_law_random_pairs_checked": checks,
        }

    # -- factor bases ------------------------------------------------------
    def factor_base(self, xs: list[int]) -> list:
        """{P : x(P) in xs}, as points; both y-roots are kept when they exist."""
        out = []
        for x in xs:
            for y in self.curve.ys_for_x(x):
                p = (x, y)
                if not self.curve.is_on_curve(p):
                    raise ArithmeticError("constructed a point off the curve")
                out.append(p)
        return out

    def coord_array(self, pts: list) -> list[tuple[int, int]]:
        return [self.coords[p] for p in pts]


# ---------------------------------------------------------------------------
# Exact enumeration by integer convolution over the group
# ---------------------------------------------------------------------------
def _shift_add(dst: np.ndarray, src: np.ndarray, c: tuple[int, int]) -> None:
    dst += np.roll(src, c, axis=(0, 1))


def typed_multiplicities(model: GroupModel, bases: list[list]) -> np.ndarray:
    """Fibre sizes of prod_i F_i -> group, by exact integer convolution.

    Entry [i, j] is the number of typed selections (P_1, ..., P_m) with
    P_i in F_i whose group sum has coordinates (i, j). The array sums to
    prod_i |F_i| by construction, which is asserted.
    """
    acc = np.zeros((model.n1, model.n2), dtype=np.int64)
    acc[0, 0] = 1
    for base in bases:
        nxt = np.zeros_like(acc)
        for c in model.coord_array(base):
            _shift_add(nxt, acc, c)
        acc = nxt
    total = int(acc.sum())
    expect = 1
    for base in bases:
        expect *= len(base)
    if total != expect:
        raise ArithmeticError(f"convolution mass {total} != domain {expect}")
    return acc


def untyped_multiset_multiplicities(model: GroupModel, base: list,
                                    m: int) -> np.ndarray:
    """Fibre sizes of {size-m multisets from F} -> group, exactly.

    Dynamic programme over the distinct points of F: for each point, choose how
    many copies enter the multiset. Exact, and the total mass is asserted
    against binom(|F| + m - 1, m).
    """
    n1, n2 = model.n1, model.n2
    dp = [np.zeros((n1, n2), dtype=np.int64) for _ in range(m + 1)]
    dp[0][0, 0] = 1
    for c in model.coord_array(base):
        for j in range(m, 0, -1):
            acc = np.zeros((n1, n2), dtype=np.int64)
            for cnt in range(1, j + 1):
                cc = ((c[0] * cnt) % n1, (c[1] * cnt) % n2)
                _shift_add(acc, dp[j - cnt], cc)
            dp[j] += acc
    total = int(dp[m].sum())
    expect = math.comb(len(base) + m - 1, m) if base else 0
    if total != expect:
        raise ArithmeticError(f"multiset DP mass {total} != binom {expect}")
    return dp[m]


def untyped_ordered_multiplicities(model: GroupModel, base: list,
                                   m: int) -> np.ndarray:
    """Fibre sizes of the ORDERED untyped family F^m -> group, exactly."""
    return typed_multiplicities(model, [base] * m)


# ---------------------------------------------------------------------------
# Independent cross-check: direct enumeration with real curve arithmetic
# ---------------------------------------------------------------------------
def brute_force_image(model: GroupModel, bases: list[list],
                      permute_rng=None) -> dict:
    """Enumerate prod_i F_i with itertools.product and real group additions.

    Deliberately shares no code with the convolution path: the sums are formed
    by BinaryCurve.add on points, not by integer shifts, and the image is a
    Python set of points. `permute_rng` implements the shuffled-types control by
    permuting each tuple before summing.
    """
    E = model.curve
    hist: dict = {}
    for tup in itertools.product(*bases):
        seq = list(tup)
        if permute_rng is not None:
            order = permute_rng.permutation(len(seq))
            seq = [seq[i] for i in order]
        s = INFINITY
        for p in seq:
            s = E.add(s, p)
        hist[s] = hist.get(s, 0) + 1
    return {"image_size": len(hist),
            "fibre_histogram": _histogram_of_counts(hist.values()),
            "sum_multiplicities": sum(hist.values())}


def brute_force_untyped_multiset_image(model: GroupModel, base: list,
                                       m: int) -> dict:
    E = model.curve
    hist: dict = {}
    for combo in itertools.combinations_with_replacement(range(len(base)), m):
        s = INFINITY
        for i in combo:
            s = E.add(s, base[i])
        hist[s] = hist.get(s, 0) + 1
    return {"image_size": len(hist),
            "fibre_histogram": _histogram_of_counts(hist.values()),
            "sum_multiplicities": sum(hist.values())}


def _histogram_of_counts(counts) -> dict:
    out: dict = {}
    for c in counts:
        out[int(c)] = out.get(int(c), 0) + 1
    return dict(sorted(out.items()))


# ---------------------------------------------------------------------------
# Summaries: image size, fibre distribution, Poisson tail
# ---------------------------------------------------------------------------
def summarise(mult: np.ndarray, domain: int, group_order: int,
              lam_declared: float) -> dict:
    """Image size and the FULL fibre-size distribution, plus Poisson tails.

    Two Poisson references are reported and never mixed: `lam_declared` is the
    contract's 2^{mk-n}, and `lam_exact` is the measured domain/|E|. The
    declared one is what the pre-registered prediction names; the exact one is
    the diagnostic that separates a prediction failure from a domain-size
    mismatch.
    """
    flat = mult.reshape(-1)
    image = int(np.count_nonzero(flat))
    nz = flat[flat > 0]
    hist = _histogram_of_counts(nz.tolist())
    hist[0] = int(group_order - image)
    hist = dict(sorted(hist.items()))
    lam_exact = domain / group_order
    maxmult = int(nz.max()) if image else 0
    return {
        "image_size": image,
        "domain_size": int(domain),
        "group_order": int(group_order),
        "fibre_histogram": {str(k): int(v) for k, v in hist.items()},
        "fibre_max": maxmult,
        "fibre_min_over_image": int(nz.min()) if image else 0,
        "fibre_mean_over_group": float(domain / group_order),
        "fibre_mean_over_image": float(domain / image) if image else None,
        "poisson_declared_lambda_2_pow_mk_minus_n": lam_declared,
        "poisson_declared_expected_counts":
            _poisson_expected(lam_declared, group_order, maxmult),
        "poisson_exact_lambda_domain_over_group": lam_exact,
        "poisson_exact_expected_counts":
            _poisson_expected(lam_exact, group_order, maxmult),
        "poisson_exact_upper_tail_above_observed_max":
            _poisson_tail(lam_exact, group_order, maxmult),
    }


def _poisson_expected(lam: float, group_order: int, upto: int) -> dict:
    out = {}
    for j in range(0, max(upto, 1) + 1):
        out[str(j)] = float(group_order * math.exp(-lam) * lam ** j
                            / math.factorial(j))
    return out


def _poisson_tail(lam: float, group_order: int, maxmult: int) -> float:
    """Expected number of group elements with fibre size > observed maximum."""
    cdf = sum(math.exp(-lam) * lam ** j / math.factorial(j)
              for j in range(0, maxmult + 1))
    return float(group_order * max(0.0, 1.0 - cdf))
