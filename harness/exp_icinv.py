"""EXP-ICINV: is any ECDLP attack-cost functional non-constant across an
F_p-isogeny class?

This is the gating measurement of GOAL-ENDO-001 (lane L1). The design point is
that the isogeny class fixes p, t, N and #E(F_p) exactly, so any functional that
is a function of those alone has ZERO within-class variance by construction.
The experiment therefore measures, for every curve in a completely enumerated
class, a battery of functionals and asks of each one whether its within-class
variance exceeds what its own null predicts.

Three nulls, and the choice between them matters:

  NULL-A  between-class at matched N bit-length. Controls for p but NOT for N,
          so a functional depending on N shows between-class spread for a
          trivial reason. Reported, never used alone.
  NULL-B  the functional's own sampling distribution. For a rate estimated from
          T Bernoulli trials the null is Binomial(T, rate) and the test is
          over-dispersion. This is the primary null: it needs no second class.
  NULL-C  label permutation. Shuffle curve labels across the pooled measured set
          and recompute the within-group variance. Tests whether the grouping
          "same isogeny class" carries any information at all.

Every rate is measured by EXACT ENUMERATION over the factor base, not by a
solver, so the measurement itself needs no certificate beyond curve membership.
Toy scale only.
"""
from __future__ import annotations

import hashlib
import math
import statistics
from dataclasses import dataclass, asdict

from .isogeny_class import CurveRecord, enumerate_curves, isogeny_classes, class_census
from .toycurve import EllipticCurve, Point


# --------------------------------------------------------------------------
# factor bases -- size-controlled, which is the whole point
# --------------------------------------------------------------------------


def factor_base_fixed_size(E: EllipticCurve, size: int, start: int = 0) -> list[int]:
    """The first `size` liftable x-coordinates at or above `start`.

    SIZE-CONTROLLED across curves: every curve gets exactly `size` base points,
    so a difference in any measured rate cannot be an artifact of base size.
    The x-values themselves differ per curve, which is the intended degree of
    freedom -- it is the curve equation, resource R2, doing the varying.
    """
    xs: list[int] = []
    x = start
    while len(xs) < size and x < E.p:
        if E.lift_x(x) is not None:
            xs.append(x)
        x += 1
    return xs


def factor_base_window(E: EllipticCurve, bound: int) -> list[int]:
    """Every liftable x in [0, bound). Size VARIES per curve -- deliberately."""
    return [x for x in range(min(bound, E.p)) if E.lift_x(x) is not None]


# --------------------------------------------------------------------------
# functionals
# --------------------------------------------------------------------------


def liftable_density(E: EllipticCurve, bound: int) -> float:
    """|{x < bound : x^3+ax+b is a square}| / bound.

    A character sum: Weil gives bound/2 + O(sqrt(p) log p), so this is NOT a
    function of (p, t, N) and is expected to vary within a class. Included
    precisely because it is a functional that SHOULD show within-class variance,
    which makes it the campaign's positive control for the variance instrument.
    """
    return len(factor_base_window(E, bound)) / bound


def decomposition_rate_m2(E: EllipticCurve, fb: list[int], targets: list[Point]
                          ) -> tuple[int, int]:
    """(hits, trials): how many targets are a sum of two factor-base points.

    Exact: builds the full sum set of the base by enumeration, then tests
    membership. No solver, no heuristic, no certificate needed beyond the curve
    arithmetic itself.
    """
    pts: list[Point] = []
    for x in fb:
        P = E.lift_x(x)
        if P is not None:
            pts.append(P)
            pts.append(E.negate(P))
    sums = set()
    for i in range(len(pts)):
        for jx in range(i, len(pts)):
            S = E.add(pts[i], pts[jx])
            if S is not None:
                sums.add(S)
    hits = sum(1 for T in targets if T in sums)
    return hits, len(targets)


def decomposition_rate_m3(E: EllipticCurve, fb: list[int], targets: list[Point]
                          ) -> tuple[int, int]:
    """(hits, trials) for sums of three factor-base points. Exact enumeration."""
    pts: list[Point] = []
    for x in fb:
        P = E.lift_x(x)
        if P is not None:
            pts.append(P)
            pts.append(E.negate(P))
    two = set()
    for i in range(len(pts)):
        for jx in range(i, len(pts)):
            S = E.add(pts[i], pts[jx])
            if S is not None:
                two.add(S)
    three = set()
    for S in two:
        for R in pts:
            T = E.add(S, R)
            if T is not None:
                three.add(T)
    hits = sum(1 for T in targets if T in three)
    return hits, len(targets)


def max_sums(fb_size: int, m: int) -> int:
    """Number of multisets of size m from the 2*fb_size points +-V.

    The ceiling on how many DISTINCT points an m-fold sum over the factor base
    could possibly hit, before any additive collisions on the curve.
    """
    n = 2 * fb_size
    num = 1
    for i in range(m):
        num = num * (n + i)
    for i in range(1, m + 1):
        num //= i
    return num


def decomposition_efficiency(rate: float, order: int, fb_size: int, m: int) -> float:
    """rate * order / max_sums -- the fraction of POSSIBLE sums that are distinct.

    THIS IS THE STATISTIC THAT MAY BE COMPARED ACROSS ISOGENY CLASSES, and the
    raw rate is not. A raw decomposition rate is approximately |mV| / #E, and #E
    differs between classes by construction (that is what a class IS), so a
    permutation null on raw rates detects the group order and reports it as
    structure. Replicating EXP-ICINV at p = 6007 produced exactly that false
    positive: NULL-C on raw rate_m2 gave p = 0.0075 while the same null at
    p = 4001 gave p = 0.538, and the difference is the spread of #E across the
    classes sampled, not anything about the curves.

    Dividing by max_sums removes the factor-base size, and multiplying by the
    order removes #E, leaving a dimensionless additive-collision statistic that
    is a property of the curve's point set alone.
    """
    return rate * order / max_sums(fb_size, m)


def two_torsion_x_count(p: int, a: int, b: int) -> int:
    """z = #{x in F_p : x^3 + ax + b = 0}, i.e. rational 2-torsion x-coordinates.

    z is in {0, 1, 3} and is NOT an isogeny-class invariant: an isogeny can
    change the group structure, so curves of the same trace can differ here.
    """
    return sum(1 for x in range(p) if (x * x % p * x + a * x + b) % p == 0)


def liftable_count_identity(order: int, z: int) -> int:
    """#{x in F_p : x^3+ax+b is a square} = (#E(F_p) - 1 + z) / 2.

    Derivation, not a fit. For each x the number of y with y^2 = f(x) is
    1 + chi(f(x)); summing gives #E = p + 1 + sum_x chi(f(x)). Writing z for the
    root count and s for the count of x with f(x) a nonzero square,
    #E - 1 = z + 2s and the liftable-x count is z + s, so it equals
    (#E - 1 + z)/2.

    CONSEQUENCE, and it is the whole point: over the FULL field the liftable
    density is a function of (#E, z) alone. #E is class-invariant; z is not.
    So the entire within-class variation of full-field liftable density is the
    2-torsion structure and nothing else -- both terms are computable in
    negligible time from the curve equation, so the quantity carries no ECDLP
    attack content whatever its variance.
    """
    return (order - 1 + z) // 2


def s3_monomial_support(p: int, a: int, b: int) -> int:
    """Number of monomials with nonzero coefficient in Semaev's S_3 over F_p.

    S_3 = (x1-x2)^2 x3^2 - 2((x1+x2)(x1 x2 + a) + 2b) x3 + ((x1 x2 - a)^2 - 4b(x1+x2))

    Purely a function of (a, b) mod p, hence a legitimate R2 functional. For
    a = 0 (j=0) and b = 0 (j=1728) whole monomials vanish, which is the sharpest
    version of "special j-invariant changes the polynomial system".
    """
    import sympy
    x1, x2, x3 = sympy.symbols("x1 x2 x3")
    expr = ((x1 - x2) ** 2 * x3 ** 2
            - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
            + ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)))
    poly = sympy.Poly(sympy.expand(expr), x1, x2, x3, modulus=p)
    return len([c for c in poly.coeffs() if c % p != 0])


def group_structure(E: EllipticCurve, order: int) -> tuple[int, int]:
    """(n1, n2) with E(F_p) ~ Z/n1 x Z/n2, n1 | n2. Class-invariant check.

    Determined by the largest m with E[m] fully rational. Computed at toy scale
    by finding the exponent of the group: the least e with [e]P = O for all P.
    """
    e = 1
    for x in range(E.p):
        P = E.lift_x(x)
        if P is None:
            continue
        # order of P divides `order`
        o = order
        for q, mult in _factor(order).items():
            for _ in range(mult):
                if o % q == 0 and E.mul(o // q, P) is None:
                    o //= q
                else:
                    break
        e = e * o // math.gcd(e, o)
        if e == order:
            break
    return order // e, e


def _factor(n: int) -> dict[int, int]:
    f: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


# --------------------------------------------------------------------------
# per-curve measurement
# --------------------------------------------------------------------------


@dataclass
class CurveMeasurement:
    p: int
    a: int
    b: int
    j: int
    trace: int
    order: int
    aut_order: int
    fb_size: int
    n_targets: int
    liftable_density_w: float
    decomp_hits_m2: int
    decomp_rate_m2: float
    decomp_hits_m3: int
    decomp_rate_m3: float
    s3_support: int
    window_fb_size: int
    group_n1: int
    group_n2: int


def _targets(E: EllipticCurve, count: int, seed: int) -> list[Point]:
    """CONFOUNDED SAMPLER -- retained only so superseded runs stay reproducible.

    Hashes (seed, i) to an x and keeps it if it lifts on the curve. The comment
    this function used to carry claimed that using a curve-independent x sequence
    kept the sampler from being a per-curve degree of freedom. That reasoning is
    WRONG, and the error is the reverse of what it claims: which x values lift
    differs per curve, the liftable density over the full field is an exact
    function of #E and the 2-torsion (see `liftable_count_identity`), and #E is
    exactly what defines an isogeny class. So the accepted target multiset is
    systematically different BETWEEN classes by construction, and any
    between-class comparison built on it is measuring the sampler.

    Measured effect: at p = 6007 the label-permutation null on m = 2
    decomposition efficiency gives p = 0.0035 with this sampler and p = 0.1910
    with `targets_uniform` on the identical curves, factor bases and seed. The
    apparent class-level signal is entirely the sampler. See CORR-20260807-*.

    WITHIN a class the bias is constant (all curves share #E), so within-class
    over-dispersion, the liftable-count identity, the decay test and the
    invariance of #E and s3_support are UNAFFECTED. Only between-class
    comparisons are.

    Use `targets_uniform` for anything new.
    """
    out: list[Point] = []
    i = 0
    while len(out) < count and i < 200 * count + 5000:
        h = hashlib.sha256(f"{seed}:{i}".encode()).hexdigest()
        x = int(h, 16) % E.p
        P = E.lift_x(x)
        if P is not None:
            out.append(P)
        i += 1
    return out


def _point_order(E: EllipticCurve, P: Point, n: int) -> int:
    """Exact order of P, given that ord(P) | n."""
    o = n
    for q in _factor(n):
        while o % q == 0 and E.mul(o // q, P) is None:
            o //= q
    return o


def targets_uniform(E: EllipticCurve, order: int, count: int, seed: int,
                    max_candidates: int = 200) -> list[Point]:
    """Uniform targets on E(F_p): pseudo-random multiples of a HIGH-ORDER base point.

    Every curve's targets are drawn from its own group with the same
    distribution, so acceptance cannot depend on liftability and the sampler
    cannot encode #E. This is the sampler any between-class comparison must use.

    CORRECTED: the first version of this function used "the first liftable x"
    as its base point unconditionally. That point's order can be SMALL --
    concretely, on the p=4001, trace=30 class, curve (a,b)=(2175,1450), the
    first liftable x is 3, giving the point (3, 0), which is 2-TORSION. Every
    "uniform" sample then collapsed to `[h % order] * G` alternating between
    (3,0) (h odd) and the identity (h even, dropped since `E.mul` returns None),
    so 300 "independent uniform targets" were in fact one point repeated. On
    that curve the m=3 decomposition rate was measured at 1.0 (300/300 hits) --
    astronomically impossible for a genuine uniform sample against a sum-set of
    density 0.016 -- and that single degenerate curve dominated the within-class
    variance of an entire sweep (ratio 56x the binomial null; found while
    building EXP-ICINV-55c2d8's saturation-decay sweep, GOAL-ENDO-001
    BATCH-523510). See CORR-20260807-* for the record.

    This version searches up to `max_candidates` liftable x-coordinates and
    keeps the point of LARGEST order found, stopping early if a point of the
    full claimed `order` is found (i.e. the group is cyclic and this is a
    generator). It still cannot reach a non-cyclic group's full structure from
    one generator -- a genuine limitation of any single-generator sampler, not
    a bug -- but it can no longer degenerate to a near-trivial subgroup by
    accident, which is what actually happened here.
    """
    G, gen_order, x = None, 0, 2
    tried = 0
    while tried < max_candidates and gen_order < order and x < E.p:
        P = E.lift_x(x)
        x += 1
        if P is None:
            continue
        tried += 1
        o = _point_order(E, P, order)
        if o > gen_order:
            G, gen_order = P, o
    if G is None:
        return []
    out: list[Point] = []
    for i in range(count):
        h = int(hashlib.sha256(f"{seed}:u:{i}".encode()).hexdigest(), 16)
        R = E.mul(h % gen_order, G)
        if R is not None:
            out.append(R)
    return out


def measure_curve(rec: CurveRecord, fb_size: int, window: int,
                  n_targets: int, seed: int, with_group: bool = False
                  ) -> CurveMeasurement:
    E = rec.curve()
    fb = factor_base_fixed_size(E, fb_size)
    tg = _targets(E, n_targets, seed)
    h2, t2 = decomposition_rate_m2(E, fb, tg)
    h3, t3 = decomposition_rate_m3(E, fb, tg)
    n1, n2 = group_structure(E, rec.order) if with_group else (0, 0)
    return CurveMeasurement(
        p=rec.p, a=rec.a, b=rec.b, j=rec.j, trace=rec.trace, order=rec.order,
        aut_order=rec.aut_order, fb_size=len(fb), n_targets=len(tg),
        liftable_density_w=liftable_density(E, window),
        decomp_hits_m2=h2, decomp_rate_m2=(h2 / t2 if t2 else float("nan")),
        decomp_hits_m3=h3, decomp_rate_m3=(h3 / t3 if t3 else float("nan")),
        s3_support=s3_monomial_support(rec.p, rec.a, rec.b),
        window_fb_size=len(factor_base_window(E, window)),
        group_n1=n1, group_n2=n2,
    )


# --------------------------------------------------------------------------
# nulls and statistics
# --------------------------------------------------------------------------


@dataclass
class VarianceVerdict:
    functional: str
    n_curves: int
    mean: float
    variance: float
    null_variance: float
    ratio: float                  # observed / null
    null_kind: str
    verdict: str                  # "invariant" | "over-dispersed" | "under-dispersed" | "inconclusive"
    detail: str = ""


def binomial_null_verdict(name: str, hits: list[int], trials: int) -> VarianceVerdict:
    """NULL-B: is the spread of an estimated rate more than binomial noise?

    Under the invariance hypothesis every curve in the class has the SAME true
    rate r, and the observed counts are i.i.d. Binomial(trials, r). The variance
    of the observed rates is then r(1-r)/trials exactly. Over-dispersion is the
    only signature that would indicate genuine curve-dependence.
    """
    n = len(hits)
    rates = [h / trials for h in hits]
    rbar = sum(rates) / n
    obs = statistics.variance(rates) if n > 1 else 0.0
    null = rbar * (1 - rbar) / trials if 0 < rbar < 1 else 0.0
    ratio = (obs / null) if null > 0 else float("inf") if obs > 0 else 1.0
    # chi-square dispersion test: (n-1)*obs/null ~ chi2_{n-1}
    stat = (n - 1) * ratio if null > 0 else float("nan")
    # 95% two-sided bounds via Wilson-Hilferty normal approximation to chi2
    df = n - 1
    if df > 0 and null > 0:
        z = 1.96
        lo = df * (1 - 2 / (9 * df) - z * math.sqrt(2 / (9 * df))) ** 3
        hi = df * (1 - 2 / (9 * df) + z * math.sqrt(2 / (9 * df))) ** 3
        if stat > hi:
            verdict = "over-dispersed"
        elif stat < lo:
            verdict = "under-dispersed"
        else:
            verdict = "invariant"
        detail = f"chi2={stat:.2f} df={df} accept=[{lo:.2f},{hi:.2f}]"
    else:
        verdict, detail = "inconclusive", "degenerate null"
    return VarianceVerdict(name, n, rbar, obs, null, ratio, "NULL-B binomial",
                           verdict, detail)


def exact_null_verdict(name: str, values: list[float]) -> VarianceVerdict:
    """For a functional predicted to be EXACTLY class-invariant, the null
    variance is zero and any spread at all refutes invariance."""
    n = len(values)
    mean = sum(values) / n
    obs = statistics.variance(values) if n > 1 else 0.0
    verdict = "invariant" if obs == 0.0 else "over-dispersed"
    return VarianceVerdict(name, n, mean, obs, 0.0,
                           float("inf") if obs > 0 else 1.0,
                           "NULL-exact (zero-variance prediction)", verdict,
                           f"distinct values: {len(set(values))}")


def permutation_null(groups: dict[int, list[float]], iterations: int = 2000,
                     seed: int = 0) -> tuple[float, float, float]:
    """NULL-C: does the grouping by isogeny class carry any information?

    Statistic: the mean within-group variance. Compare the observed value
    against its distribution when curve labels are shuffled across all groups
    with group sizes held fixed. Returns (observed, null_mean, p_value).
    """
    import random
    rng = random.Random(seed)
    sizes = [len(v) for v in groups.values()]
    pooled = [x for v in groups.values() for x in v]

    def mean_within(assign: list[list[float]]) -> float:
        vs = [statistics.variance(g) for g in assign if len(g) > 1]
        return sum(vs) / len(vs) if vs else 0.0

    observed = mean_within(list(groups.values()))
    worse = 0
    nulls = []
    for _ in range(iterations):
        rng.shuffle(pooled)
        out, i = [], 0
        for s in sizes:
            out.append(pooled[i:i + s])
            i += s
        v = mean_within(out)
        nulls.append(v)
        if v <= observed:
            worse += 1
    return observed, sum(nulls) / len(nulls), worse / iterations


__all__ = [
    "CurveMeasurement", "VarianceVerdict",
    "factor_base_fixed_size", "factor_base_window", "liftable_density",
    "decomposition_rate_m2", "decomposition_rate_m3", "s3_monomial_support",
    "group_structure", "measure_curve",
    "binomial_null_verdict", "exact_null_verdict", "permutation_null",
]
