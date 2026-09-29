"""Reward meter for the isogeny x presentation search (harness.rl_isogeny).

What is scored
--------------
A STATE is a pair (curve model, presentation).  The curve model is a short
Weierstrass curve E': y^2 = x^3 + a'x + b' inside the F_p-isogeny class of the
input curve; the presentation is the polynomial system a point-decomposition
solver would see on E' for one factor-base construction:

    direct family   u_1..u_m free variables, x_i = g(u_i) = u_i^k + c u_i,
                    membership f_V(u_i) = prod_{v < B} (u_i - v)   (box V = [0, B))
    digit family    x_i = sum_j a_{i,j} 2^j with squarefree digits (B = 2^s),
                    the EXP-PFDR digit presentation of harness.macaulay_fp
    m = 2           { S_3(x_1, x_2, x_R) }                (one relation R = P_1 + P_2)
    m = 3           { S_3(x_1, x_2, w), S_3(w, x_3, x_R) } (chained through a node w)

The score of a state is an EXACT, null-relative Macaulay reading of that
system taken with ``harness.macaulay_fp`` (no Groebner basis is computed, no
timing is a metric):

    score = -(log2 nnz(M_{D*}) + log2 max(1, m! N / B^m))
            + w_excess  * (d_ff(null) - d_ff(real))
            + w_deficit * min(cap, sum_{D <= D*} max(0, fall_real(D) - fall_null(D)))

* ``nnz(M_{D*})`` is the number of nonzero entries of the degree-D* Macaulay
  layer of the REAL system, D* the first-fall degree of the NULL: the size of
  the linear algebra the solver has to do before anything falls.  It is the
  shape-and-support cost (columns, rows, sparsity) and is the term the known
  levers move (k, c, m, digit vs direct).
* ``m! N / B^m`` is the expected number of decomposition trials per relation,
  the conservation mean of KN-FIND-007.  It is a formula, not a measurement,
  because the mean yield is provably not a design lever; it is here so that
  m = 2 and m = 3, and different B, are costed on one scale.
* ``d_ff(null) - d_ff(real)`` is the prize: a real system that falls EARLIER
  than a matched null of the same shape.  The null is either a different-trace
  random curve at the same p in the same presentation (``other_trace``, the
  DESIGN.md matched null) or the same generators with their curve-dependent
  coefficients scrambled (``curve_scramble``).  On a generic class the
  pre-registered value is 0 on every state (analysis/isogeny-dreg-search).
* the deficit term counts extra fall dimensions at or below D*, capped.

Nothing here supports a crypto-scale claim.  Claim tier: toy.
"""
from __future__ import annotations

import hashlib
import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from harness.macaulay_fp import (
    LayerResult,
    Poly,
    PreflightAbort,
    Ring,
    analyze_degrees,
    digit_presentation,
    f_V,
    first_nonzero_fall,
    generator_degrees,
    preflight,
    scramble_coefficients,
    semiregular_prediction,
    substitute,
)
from tools.isogeny_dreg_search import (
    _trim,
    count_roots,
    padd,
    pmul,
    pscale,
    random_point,
    s3_coeffs,
    s3_fibre_poly,
)


# ---------------------------------------------------------------------------
# Presentation specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PresentationSpec:
    family: str      # "direct" | "digit"
    m: int           # 2 (one S_3) or 3 (two S_3 chained through w)
    k: int           # factor-base map x = u^k + c u
    c: int           # 0 -> pure power map
    B: int           # box size |V|; for the digit family B = 2^s

    def __post_init__(self) -> None:
        if self.family not in ("direct", "digit"):
            raise ValueError(f"unknown family {self.family}")
        if self.m not in (2, 3):
            raise ValueError("m must be 2 or 3")
        if self.k < 1:
            raise ValueError("k >= 1")
        if self.B < 2:
            raise ValueError("B >= 2")
        if self.family == "digit" and (self.B & (self.B - 1)):
            raise ValueError("digit family needs B = 2^s")

    @property
    def chained(self) -> bool:
        return self.m == 3

    @property
    def s(self) -> int:
        return self.B.bit_length() - 1 if self.family == "digit" else 0

    @property
    def key(self) -> Tuple:
        return (self.family, self.m, self.k, self.c, self.B)

    def label(self) -> str:
        g = f"u^{self.k}" + (f"+{self.c}u" if self.c else "")
        return f"{self.family}(m={self.m},x={g},B={self.B})"

    def initial_cap(self) -> int:
        """First degree cap of the Macaulay scan; the null scan extends it by two
        degrees at a time (at most four times) while the null shows no fall.

        Direct family: the pre-registered structural fall of
        { S_3(g(u_1), g(u_2), x_R), f_V(u_1), f_V(u_2) } is d_ff = B + 2k, from
        u_1^{B-2k} F - lc * (...) * f_V(u_1); the chained system falls two degrees
        earlier through the w-resultant, so the same cap covers it.  Digit rings
        are squarefree, S_3 collapses to low degree, and the cap is small -- a
        loose cap in the mixed (chained) ring costs seconds per state.
        """
        if self.family == "digit":
            return 2 * self.k + 3 + (1 if self.chained else 0)
        return self.B + 2 * self.k

    structural_cap = initial_cap

    def as_dict(self) -> dict:
        return {"family": self.family, "m": self.m, "k": self.k, "c": self.c, "B": self.B,
                "label": self.label()}


def yield_log2_trials(spec: PresentationSpec, N: int) -> float:
    """log2 of the expected trials per relation, m! N / B^m (KN-FIND-007), >= 0."""
    return max(0.0, math.log2(math.factorial(spec.m) * N / float(spec.B) ** spec.m))


# ---------------------------------------------------------------------------
# Building the presentation in the meter's ring
# ---------------------------------------------------------------------------


@dataclass
class Built:
    ring: Ring
    polys: List[Poly]
    n_system: int                 # leading generators that carry the curve
    degrees: List[int]
    description: str


def map_poly(ring: Ring, u: Poly, k: int, c: int) -> Poly:
    x = ring.power(u, k)
    if c % ring.p:
        x = ring.add(x, ring.scale(u, c))
    return x


def _system(ring: Ring, S3: Dict[Tuple[int, int, int], int], xs: Sequence[Poly], x_R: int,
            chained: bool, w: Optional[Poly]) -> List[Poly]:
    if not chained:
        return [substitute(ring, S3, [xs[0], xs[1], ring.constant(x_R)])]
    assert w is not None
    return [substitute(ring, S3, [xs[0], xs[1], w]),
            substitute(ring, S3, [w, xs[2], ring.constant(x_R)])]


def build_presentation(p: int, S3: Dict[Tuple[int, int, int], int], x_R: int,
                       spec: PresentationSpec) -> Built:
    m = spec.m
    extra = 1 if spec.chained else 0
    if spec.family == "direct":
        ring = Ring(p, 0, m + extra)
        us = [{ring.free_var(i): 1} for i in range(m)]
        w = {ring.free_var(m): 1} if spec.chained else None
        xs = [map_poly(ring, u, spec.k, spec.c) for u in us]
        polys = _system(ring, S3, xs, x_R, spec.chained, w)
        n_sys = len(polys)
        polys += [f_V(ring, ring.free_var(i), spec.B) for i in range(m)]
        desc = f"direct m={m} k={spec.k} c={spec.c} B={spec.B} p={p}"
    else:
        def system(ring: Ring, xs_lin: Sequence[Poly]) -> List[Poly]:
            w = {ring.free_var(0): 1} if spec.chained else None
            xs = [map_poly(ring, x, spec.k, spec.c) for x in xs_lin]
            return _system(ring, S3, xs, x_R, spec.chained, w)
        pres = digit_presentation(p, m, 2, spec.s, system, n_extra_free=extra)
        ring = pres.ring
        polys = list(pres.generators)
        n_sys = 2 if spec.chained else 1
        desc = pres.description + f" k={spec.k} c={spec.c}"
    return Built(ring, polys, n_sys, generator_degrees(ring, polys), desc)


def shape_feasible(p: int, spec: PresentationSpec, max_rows: int, max_cols: int) -> bool:
    """Feasibility of a presentation SHAPE (curve-independent): pre-flight the
    row/column counts at the structural cap without allocating anything."""
    S3 = s3_coeffs(1, 1, p)
    built = build_presentation(p, S3, 1, spec)
    try:
        preflight(built.ring, built.degrees, spec.initial_cap() + 1, "per_layer",
                  max_rows=max_rows, max_cols=max_cols)
    except PreflightAbort:
        return False
    return True


# ---------------------------------------------------------------------------
# Scanning and profiles
# ---------------------------------------------------------------------------


@dataclass
class Profile:
    d_ff: Optional[int]
    D_min: int
    D_max: int
    falls: Dict[int, int]
    nnz: Dict[int, int]
    cols: Dict[int, int]
    rows: Dict[int, int]
    d_reg_pred: Optional[int]


def scan(built: Built, D_max: int, max_rows: int, max_cols: int) -> Profile:
    degs = [d for d in built.degrees if d > 0]
    D_min = min(degs)
    layers = analyze_degrees(built.ring, built.polys, D_min, D_max, convention="per_layer",
                             max_rows=max_rows, max_cols=max_cols)
    pred = semiregular_prediction(built.ring, degs, D_max)
    return Profile(
        d_ff=first_nonzero_fall(layers),
        D_min=D_min, D_max=D_max,
        falls={l.degree: l.fall_dim for l in layers},
        nnz={l.degree: l.nnz_total for l in layers},
        cols={l.degree: l.ncols_full for l in layers},
        rows={l.degree: l.row_count for l in layers},
        d_reg_pred=pred.d_reg,
    )


def fibre_poly_general(a: int, b: int, p: int, k: int, c: int, x1: int, x_R: int) -> List[int]:
    """S_3(x1, g(u), x_R) as a univariate polynomial in u for g(u) = u^k + c u."""
    q = s3_fibre_poly(a, b, p, x1, x_R)          # in X = g(u): [q0, q1, q2]
    g = [0] * (k + 1)
    g[k] = 1
    g[1] = (g[1] + c) % p
    g = _trim(g)
    out: List[int] = []
    powg = [1]
    for e, coeff in enumerate(q):
        if e:
            powg = pmul(powg, g, p)
        out = padd(out, pscale(powg, coeff, p), p)
    return _trim(out)


def coverage_estimate(a: int, b: int, p: int, k: int, c: int, samples: int, rng: random.Random) -> float:
    """Fraction of random (R, u_1) whose fibre S_3(g(u_1), g(u_2), x_R) = 0 has an
    F_p-root u_2.  Reported as a feature, never rewarded (KN-FIND-007)."""
    if samples <= 0:
        return 0.0
    hits = 0
    for _ in range(samples):
        R = random_point(a, b, p, rng)
        u1 = rng.randrange(1, p)
        x1 = (pow(u1, k, p) + c * u1) % p
        f = fibre_poly_general(a, b, p, k, c, x1, R[0])
        if len(f) > 1 and count_roots(f, p) > 0:
            hits += 1
    return hits / samples


# ---------------------------------------------------------------------------
# Measurement and score
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Weights:
    excess: float = 4.0
    deficit: float = 0.5
    deficit_cap: int = 8
    planted_bonus: float = 6.0

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class Measurement:
    a: int
    b: int
    j: int
    spec: PresentationSpec
    x_R: int
    feasible: bool
    d_ff_real: Optional[int]
    d_ff_null: Optional[int]
    D_max: int
    excess_fall: int
    deficit_excess: int
    log2_nnz: float
    log2_cols: float
    yield_log2_trials: float
    coverage: float
    d_reg_pred: Optional[int]
    null_kind: str
    n_null: int
    seconds: float
    score: float
    falls_real: Dict[int, int] = field(default_factory=dict)
    falls_null: Dict[int, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        d = dict(self.__dict__)
        d["spec"] = self.spec.as_dict()
        d["falls_real"] = {str(k): v for k, v in self.falls_real.items()}
        d["falls_null"] = {str(k): v for k, v in self.falls_null.items()}
        return d


def _seed_from(*parts) -> int:
    h = hashlib.sha256(":".join(str(x) for x in parts).encode()).hexdigest()
    return int(h[:16], 16)


class RewardMeter:
    """Scores (curve, presentation) states; caches by (iso_key, spec.key)."""

    def __init__(self, p: int, N: int, null_curves: Sequence[Tuple[int, int]], *, seed: int = 0,
                 null_kind: str = "other_trace", weights: Optional[Weights] = None,
                 max_rows: int = 40000, max_cols: int = 40000, coverage_samples: int = 16):
        if null_kind not in ("other_trace", "curve_scramble"):
            raise ValueError("null_kind must be other_trace or curve_scramble")
        if null_kind == "other_trace" and not null_curves:
            raise ValueError("other_trace null needs at least one null curve")
        self.p = p
        self.N = N
        self.null_curves = list(null_curves)
        self.seed = seed
        self.null_kind = null_kind
        self.weights = weights or Weights()
        self.max_rows = max_rows
        self.max_cols = max_cols
        self.coverage_samples = coverage_samples
        self._null: Dict[Tuple, Tuple[Optional[int], Dict[int, int], int]] = {}
        self._cache: Dict[Tuple, Measurement] = {}
        self.evaluations = 0
        self.seconds = 0.0

    # -- nulls ---------------------------------------------------------------
    def _aggregate(self, profiles: Sequence[Profile], D_max: int) -> Tuple[Optional[int], Dict[int, int]]:
        d_ffs = [pr.d_ff for pr in profiles]
        d_ff = None if all(d is None for d in d_ffs) else min(d for d in d_ffs if d is not None)
        falls: Dict[int, int] = {}
        for pr in profiles:
            for D, v in pr.falls.items():
                falls[D] = max(falls.get(D, 0), v)
        return d_ff, falls

    def null_profile(self, spec: PresentationSpec) -> Tuple[Optional[int], Dict[int, int], int]:
        """(d_ff_null, falls_null, D_max) for the other_trace null of ``spec``."""
        if spec.key in self._null:
            return self._null[spec.key]
        D_max = spec.initial_cap()
        for _attempt in range(5):
            profiles = []
            for (na, nb) in self.null_curves:
                rng = random.Random(_seed_from(self.seed, "null", na, nb, spec.key))
                x_R = random_point(na, nb, self.p, rng)[0]
                built = build_presentation(self.p, s3_coeffs(na, nb, self.p), x_R, spec)
                profiles.append(scan(built, D_max, self.max_rows, self.max_cols))
            d_ff, falls = self._aggregate(profiles, D_max)
            if d_ff is not None:
                break
            D_max += 2          # no fall by the cap: look two degrees further
        self._null[spec.key] = (d_ff, falls, D_max)
        return self._null[spec.key]

    # -- states --------------------------------------------------------------
    def measure(self, a: int, b: int, j: int, iso_key: Tuple, spec: PresentationSpec) -> Measurement:
        ck = (iso_key, spec.key)
        if ck in self._cache:
            return self._cache[ck]
        t0 = time.time()
        p = self.p
        rng = random.Random(_seed_from(self.seed, "real", iso_key, spec.key))
        x_R = random_point(a, b, p, rng)[0]
        S3 = s3_coeffs(a, b, p)
        built = build_presentation(p, S3, x_R, spec)
        try:
            if self.null_kind == "other_trace":
                d_ff_null, falls_null, D_max = self.null_profile(spec)
            else:
                nb = list(range(built.n_system))
                scr, _, _ = scramble_coefficients(built.ring, built.polys,
                                                  _seed_from(self.seed, "scramble", iso_key, spec.key),
                                                  select=lambda gi, m, c: gi in nb)
                null_built = Built(built.ring, scr, built.n_system, built.degrees, "scrambled")
                D_max = spec.initial_cap()
                for _attempt in range(5):
                    pr = scan(null_built, D_max, self.max_rows, self.max_cols)
                    d_ff_null, falls_null = pr.d_ff, pr.falls
                    if d_ff_null is not None:
                        break
                    D_max += 2
            # the real system is scanned one degree past the null's fall: enough to
            # see it fall earlier (the prize), at the same degree, or one later
            D_real = D_max if d_ff_null is None else min(D_max, d_ff_null + 1)
            real = scan(built, D_real, self.max_rows, self.max_cols)
            feasible = True
        except PreflightAbort:
            meas = Measurement(a, b, j, spec, x_R, False, None, None, spec.initial_cap(), 0, 0,
                               float("inf"), float("inf"), yield_log2_trials(spec, self.N), 0.0, None,
                               self.null_kind, len(self.null_curves), time.time() - t0, -1e6)
            self._cache[ck] = meas
            return meas
        dn = d_ff_null if d_ff_null is not None else D_max + 1
        dr = real.d_ff if real.d_ff is not None else D_real + 1
        excess = dn - dr
        D_star = min(dn, D_real)
        deficit = sum(max(0, real.falls.get(D, 0) - falls_null.get(D, 0))
                      for D in real.falls if D <= D_star)
        nnz = real.nnz.get(D_star, 0)
        cols = real.cols.get(D_star, 0)
        log2_nnz = math.log2(nnz) if nnz > 0 else 0.0
        log2_cols = math.log2(cols) if cols > 0 else 0.0
        ylt = yield_log2_trials(spec, self.N)
        cov = 0.0
        if spec.m == 2:
            crng = random.Random(_seed_from(self.seed, "cov", iso_key, spec.key))
            cov = coverage_estimate(a, b, p, spec.k, spec.c, self.coverage_samples, crng)
        w = self.weights
        score = (-(log2_nnz + ylt) + w.excess * excess
                 + w.deficit * min(w.deficit_cap, deficit))
        dt = time.time() - t0
        meas = Measurement(a, b, j, spec, x_R, feasible, real.d_ff, d_ff_null, D_real, excess, deficit,
                           log2_nnz, log2_cols, ylt, cov, real.d_reg_pred, self.null_kind,
                           len(self.null_curves) if self.null_kind == "other_trace" else 1, dt, score,
                           falls_real=dict(real.falls), falls_null=dict(falls_null))
        self._cache[ck] = meas
        self.evaluations += 1
        self.seconds += dt
        return meas
