"""Pippenger (bucket) multi-scalar multiplication with and without endomorphisms.

``costmodel.py`` prices ONE variable-base scalar multiplication.  This module
prices a multi-scalar multiplication ``sum_i k_i P_i`` of ``N`` points by
Pippenger's bucket method, where an endomorphism plays a different role:
the dominant term is the bucket accumulation, about ``(b/c) * N`` additions
for ``b``-bit scalars and window ``c``, and a GLV split does not shrink it --
``N`` scalars of ``b`` bits become ``2N`` scalars of ``b/2`` bits, the same
number of digit positions.  What the split does shrink is the per-window
bucket aggregation (``~2^c`` additions per window, half as many windows),
and what it pays is ``N`` endomorphism images.  This module makes that
argument quantitative with an explicit, validated operation count.

Three variants, two addition settings, every curve's own constants:

* ``plain``   -- signed-digit windows of width ``c`` (digits in
  ``[-2^(c-1), 2^(c-1)]``, the sign absorbed by negating the point), buckets
  ``1..2^(c-1)``, running-sum aggregation, ``c`` doublings per window;
* ``glv``     -- each ``k_i`` split by Babai rounding against the reduced
  relation lattice of ``lattice.py`` into ``k_i1 + k_i2*lambda`` with
  ``|k_ij|`` below the **provable** Babai bound; ``2N`` points with
  coefficients of ``bitlen(bound)`` bits, plus ``N`` images
  ``phi(P_i)`` (and, for a chain whose output is projective, their batched
  conversion to affine);
* ``fold``    -- only where ``|Aut(E)| = 6`` (``D = -3``): the reduced
  element ``z = k_i1 + k_i2*omega`` of ``Z[omega]`` is expanded in radix
  ``2^c`` with digits from the hexagonal Voronoi cell of ``2^c Z[omega]``
  (a complete residue system that is invariant under the six units up to
  its boundary), and every digit is moved by a unit into the sector
  ``{x >= 1, y >= 0}`` of the basis ``(1, omega)``: ``delta*P =
  delta'*(u*P)``.  One bucket per orbit, about ``4^c/6`` buckets per window
  where the 1-D split of the same digit positions needs ``2 * 2^(c-1)``
  buckets per ``c`` bits of each coefficient, i.e. a third of the
  equivalent ``4^c/2``.  The window sum ``sum delta'*S`` is ``X + omega(Y)``
  with ``X = sum x*S, Y = sum y*S``, each a column/row grouping followed by a
  running sum.  ``2N`` unit images (``beta*x``, ``beta^2*x``) are charged.

Addition settings (all constants from ``costmodel.py``):

* ``mixed``        -- Jacobian buckets, affine input points: accumulation
  is ``mADD``; aggregation and window combination are ``ADD``;
* ``batch_affine`` -- affine buckets; every accumulation (and, for
  ``fold``, every grouping) addition is an affine addition
  ``lambda = (y2-y1)/(x2-x1)`` (1M), ``x3 = lambda^2 - x1 - x2`` (1S),
  ``y3 = lambda*(x1 - x3) - y1`` (1M), with the inverse from Montgomery's
  batch trick: ``m`` inverses cost ``3(m-1)`` M + one inversion (prefix
  products ``m-1``, two multiplications per element on the way back).  So an
  affine addition is ``2M + 1S + 3M = 5M + 1S`` (5.8 M at ``S = 0.8 M``)
  plus its share of an inversion.  Additions are scheduled as a pairwise
  tree inside each bucket, every round batched over all buckets of all
  windows, so the number of inversions is the number of rounds,
  ``ceil(log2(max bucket load))``.  Running sums use ``mADD`` (affine
  bucket into a Jacobian sum) and ``ADD``.

What is modelled and what is measured.  ``model_1d``/``model_fold`` give
expectations under stated approximations: windows far below the top hold
digits uniform over the ``2^c`` (or ``4^c``) residues (exact for uniform
scalars); the windows near the top are computed from the scalar
distribution -- uniform on ``[0, n)`` for ``plain``, the trapezoid
``|f1*a + f2*b|`` of Babai rounding (``f1, f2`` uniform on ``[-1/2, 1/2)``)
for ``glv``, the integer points of the scaled Babai parallelogram for
``fold`` -- with the carry probability propagated upwards; bucket
occupancies and carries are treated as independent; the inversion count
follows the largest bucket load of any window.  ``run_counted`` executes the
same algorithms on secp256k1 with every field multiplication, squaring and
inversion counted and checks the result against ``[sum k_i r_i] G``;
``validate`` compares the two (all runs within 1 %).

    python -m harness.endosweep.msm --out-dir research/endosweep_msm_20261008
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import statistics
import time
from dataclasses import asdict, dataclass, field

import numpy as np
from sympy import isprime

from . import costmodel as CM
from . import lattice as LA
from . import quadorder as QO
from .targets import Target, deployed_targets, verify

FORMAT = "endosweep-msm/1"
GENERATOR = "harness/endosweep/msm.py"

S_W = CM.S_PER_M                 # a squaring in M (costmodel assumption 0.8)
I_W = CM.I_PER_M                 # an inversion in M (costmodel assumption 100)
AFFINE_ADD = (2, 1)              # (M, S) of an affine addition given 1/(x2 - x1)
BATCH_M_PER_INVERSE = 3          # Montgomery: 3(m-1) M + 1 I for m inverses
NORMALISE = (3, 1)               # (M, S) per point after the batched inverse:
                                 # Z^-2 (1S), Z^-3 (1M), x*Z^-2, y*Z^-3 (2M)
C_MAX_1D = 22
C_MAX_FOLD = 11


# ---------------------------------------------------------------------------
# per-operation costs
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OpCosts:
    model: str
    mode: str                      # 'mixed' | 'batch_affine'
    dbl: float
    add: float
    madd: float
    aff: float                     # affine addition incl. its 3 M of batch overhead
    inv: float

    @property
    def acc(self) -> float:        # one accumulation addition
        return self.madd if self.mode == "mixed" else self.aff

    @property
    def run_r(self) -> float:      # R += S_j
        return self.add if self.mode == "mixed" else self.madd

    @property
    def group(self) -> float:      # fold: column/row grouping addition
        return self.add if self.mode == "mixed" else self.aff


def op_costs(model: str, mode: str) -> OpCosts:
    if mode not in ("mixed", "batch_affine"):
        raise ValueError(mode)
    aff = AFFINE_ADD[0] + S_W * AFFINE_ADD[1] + BATCH_M_PER_INVERSE
    return OpCosts(model, mode, CM.op_cost(model, "DBL"), CM.op_cost(model, "ADD"),
                   CM.op_cost(model, "mADD"), aff, I_W)


def normalise_cost_per_point(npts: int) -> float:
    """Batched Jacobian -> affine conversion of ``npts`` points, per point:
    3(m-1) M + I for the inverses, then 3M + 1S each."""
    return (BATCH_M_PER_INVERSE * (npts - 1) + I_W) / npts + NORMALISE[0] + S_W * NORMALISE[1]


# ---------------------------------------------------------------------------
# occupancy algebra (expectations; independence of bucket occupancies assumed)
# ---------------------------------------------------------------------------

def _occ(p, npts):
    """P(a bucket of per-point probability p is non-empty after npts points)."""
    p = np.asarray(p, dtype=float)
    with np.errstate(divide="ignore"):
        return -np.expm1(npts * np.log1p(-np.minimum(p, 1.0 - 1e-300)))


def _running_sum(e_desc: np.ndarray) -> tuple[float, float]:
    """Expected (R-additions, T-additions) of ``R += S_j; T += R`` over buckets
    visited in the given order (top first) with non-empty probabilities e.

    ``R += S_j`` costs when S_j is non-empty and some earlier bucket was;
    ``T += R`` costs when some earlier bucket was non-empty (then R is too)."""
    if len(e_desc) == 0:
        return 0.0, 0.0
    none_before = np.concatenate(([1.0], np.cumprod(1.0 - e_desc)[:-1]))
    some_before = 1.0 - none_before
    return float(np.dot(e_desc, some_before)), float(some_before.sum())


def _geo(q: float, k: int) -> float:
    if k <= 0:
        return 0.0
    if q >= 1.0:
        return float(k)
    return (1.0 - q ** k) / (1.0 - q)


def uniform_window_1d(c: int, npts: int) -> dict:
    """One full signed window: digits uniform over 2^c consecutive residues.

    |d| = j has probability 2/2^c for 1 <= j < 2^(c-1), 1/2^c for j = 2^(c-1),
    and d = 0 has 1/2^c.  Closed form of the running sum (geometric)."""
    B = 1 << (c - 1)
    p, pB, p0 = 2.0 / (1 << c), 1.0 / (1 << c), 1.0 / (1 << c)
    if c == 1:                     # digits {-1, 0, 1}: one bucket of probability 1/2
        e1 = float(_occ(0.5, npts))
        return {"acc": npts * 0.5 - e1, "run_r": 0.0, "run_t": 0.0, "nonempty": e1, "buckets": 1, "pmax": 0.5}
    e1, eB = float(_occ(p, npts)), float(_occ(pB, npts))
    some = (B - 1) - (1.0 - eB) * _geo(1.0 - e1, B - 1)
    return {"acc": npts * (1.0 - p0) - ((B - 1) * e1 + eB), "run_r": e1 * some, "run_t": some,
            "nonempty": (B - 1) * e1 + eB, "buckets": B, "pmax": p}


def general_window_1d(pvec: np.ndarray, npts: int) -> dict:
    """A window with digit-magnitude distribution pvec[0..B] (pvec[0] = P(0))."""
    p0 = float(pvec[0])
    e = _occ(pvec[1:], npts)
    r, t = _running_sum(e[::-1])
    return {"acc": npts * (1.0 - p0) - float(e.sum()), "run_r": r, "run_t": t,
            "nonempty": float(e.sum()), "buckets": len(pvec) - 1, "pmax": float(pvec[1:].max(initial=0.0))}


# --- magnitude distributions of the top window -------------------------------

def cdf_uniform(nmax: int):
    """|k| uniform on [0, nmax]."""
    return lambda x: np.clip((np.floor(x) + 1.0) / (nmax + 1.0), 0.0, 1.0)


def cdf_trapezoid(a: int, b: int):
    """P(|f1*a + f2*b| <= x), f1, f2 independent uniform on [-1/2, 1/2)."""
    a, b = max(abs(a), abs(b)), min(abs(a), abs(b))
    lo, hi = (a - b) / 2.0, (a + b) / 2.0

    def G(x):
        x = np.asarray(x, dtype=float)
        if b == 0:
            return np.clip(2.0 * x / a, 0.0, 1.0)
        return np.where(x <= lo, 2.0 * x / a,
                        np.where(x <= hi, 1.0 - (hi - x) ** 2 / (a * b), 1.0)).clip(0.0, 1.0)
    return G


# --- hexagonal digit sets in Z[omega], omega = zeta_6 --------------------------

def hex_rep(a: int, b: int, h: int) -> tuple[int, int]:
    """The representative of a + b*omega modulo h*Z[omega] in the half-open
    hexagon -h < 2x+y <= h, -h < x+2y <= h, -h < x-y <= h (the Voronoi cell
    of h*Z[omega] under the norm x^2 + xy + y^2, three edges included)."""
    x0, y0 = a % h, b % h
    for ex in (0, 1, -1):
        for ey in (0, 1, -1):
            x, y = x0 - ex * h, y0 - ey * h
            if -h < 2 * x + y <= h and -h < x + 2 * y <= h and -h < x - y <= h:
                return x, y
    raise AssertionError("no hexagon representative")      # pragma: no cover


def rotate_to_sector(x: int, y: int) -> tuple[int, int, int]:
    """(x', y', j) with x + y*omega = omega^j (x' + y'*omega), x' >= 1, y' >= 0.

    Multiplying by omega^-1 = 1 - omega maps (x, y) to (x + y, -x)."""
    if x == 0 and y == 0:
        raise ValueError("zero has no sector representative")
    for j in range(6):
        if x >= 1 and y >= 0:
            return x, y, j
        x, y = x + y, -x
    raise AssertionError("rotation did not reach the sector")  # pragma: no cover


def hex_expand(a: int, b: int, c: int) -> list[tuple[int, int]]:
    """Radix-2^c expansion of a + b*omega with hexagonal digits, least significant first.

    Terminates for c >= 2: |z_{i+1}| <= (|z_i| + 2^c/sqrt3) / 2^c, so |z|
    eventually falls below 2^c/(sqrt3 (2^c - 1)) < 1, i.e. z = 0.  For c = 1
    it does not: -1 has digit 1 and (-1 - 1)/2 = -1 is a fixed point, so c = 1
    is refused."""
    if c < 2:
        raise ValueError("the hexagonal radix-2 expansion does not terminate (z = -1 is a fixed point)")
    h = 1 << c
    out = []
    while a or b:
        x, y = hex_rep(a, b, h)
        out.append((x, y))
        a, b = (a - x) >> c, (b - y) >> c
    return out


def hex_buckets(h: int) -> dict:
    """Canonical buckets of the half-open hexagon H_h: columns and rows of the
    sector {x >= 1, y >= 0}, each bucket with the number of hexagon digits in
    its unit orbit (6 inside, 3 on one included edge, 2 at an included vertex)."""
    cols: dict[int, list[int]] = {}
    rows: dict[int, list[int]] = {}
    total = 1
    for x in range(1, h // 2 + 1):
        ymax = min(h - 2 * x, (h - x) // 2)
        for y in range(0, ymax + 1):
            on = (2 * x + y == h) + (x + 2 * y == h)
            w = 6 if on == 0 else (3 if on == 1 else 2)
            total += w
            cols.setdefault(x, []).append(w)
            if y >= 1:
                rows.setdefault(y, []).append(w)
    return {"h": h, "cols": cols, "rows": rows, "digits": total}


_HEX_CACHE: dict[int, dict] = {}


def _hex(h: int) -> dict:
    if h not in _HEX_CACHE:
        _HEX_CACHE[h] = hex_buckets(h)
    return _HEX_CACHE[h]


def hex_window_general(bx: np.ndarray, by: np.ndarray, prob: np.ndarray, p0: float, npts: int) -> dict:
    """One fold window with canonical buckets (bx, by) of per-point probability
    prob (digit 0 with probability p0).  Grouping by column x (and by row y >= 1),
    then a running sum over every index from the largest down to 1."""
    e = _occ(prob, npts)
    out = {"acc": npts * (1.0 - p0) - float(e.sum()), "nonempty": float(e.sum()), "buckets": int(len(prob)),
           "group": 0.0, "run_r": 0.0, "run_t": 0.0}
    with np.errstate(divide="ignore"):
        loge = np.log1p(-np.minimum(e, 1.0 - 1e-300))
    lines = {}
    for name, key, mask in (("cols", bx, np.ones(len(bx), bool)), ("rows", by, by >= 1)):
        if not mask.any():
            lines[name] = 0
            continue
        k = key[mask].astype(np.int64)
        top = int(k.max())
        none = np.exp(np.bincount(k, weights=loge[mask], minlength=top + 1))
        g = 1.0 - none[1:]
        out["group"] += float(e[mask].sum() - g.sum())
        r, t = _running_sum(g[::-1])
        out["run_r"] += r
        out["run_t"] += t
        lines[name] = int(np.bincount(k).max())
    out["maxline"] = max(lines.values()) if lines else 1
    out["pmax"] = float(prob.max(initial=0.0))
    return out


_HEXARR: dict[int, tuple] = {}


def _hex_arrays(h: int):
    if h not in _HEXARR:
        hb = _hex(h)
        bx, by, w = [], [], []
        for x, ws in hb["cols"].items():
            for y, wt in enumerate(ws):
                bx.append(x)
                by.append(y)
                w.append(wt)
        _HEXARR[h] = (np.array(bx), np.array(by), np.array(w, dtype=float) / (h * h))
    return _HEXARR[h]


def hex_window(h: int, npts: int) -> dict:
    """One fold window with digits uniform over the h^2 digits of H_h."""
    bx, by, prob = _hex_arrays(h)
    return hex_window_general(bx, by, prob, 1.0 / (h * h), npts)


def _hex_rep_vec(x: np.ndarray, y: np.ndarray, h: int):
    x0, y0 = np.mod(x, h), np.mod(y, h)
    rx, ry = np.zeros_like(x0), np.zeros_like(y0)
    done = np.zeros(len(x0), bool)
    for ex in (0, 1, -1):
        for ey in (0, 1, -1):
            cx, cy = x0 - ex * h, y0 - ey * h
            ok = (~done & (-h < 2 * cx + cy) & (2 * cx + cy <= h) & (-h < cx + 2 * cy) & (cx + 2 * cy <= h)
                  & (-h < cx - cy) & (cx - cy <= h))
            rx[ok], ry[ok] = cx[ok], cy[ok]
            done |= ok
    assert done.all()
    return rx, ry


def _to_sector_vec(x: np.ndarray, y: np.ndarray):
    x, y = x.copy(), y.copy()
    for _ in range(6):
        bad = ~((x >= 1) & (y >= 0))
        if not bad.any():
            break
        x[bad], y[bad] = x[bad] + y[bad], -x[bad]
    return x, y


# ---------------------------------------------------------------------------
# the model
# ---------------------------------------------------------------------------
@dataclass
class MSMCost:
    variant: str
    mode: str
    N: int
    c: int
    windows: int
    coeff_bits: int
    acc_adds: float
    run_r_adds: float
    run_t_adds: float
    group_adds: float
    combine_adds: float
    doublings: float
    inversions: float
    endo_M: float
    total_M: float
    breakdown: dict = field(default_factory=dict)

    @property
    def per_point(self) -> float:
        return self.total_M / self.N


@dataclass
class ScalarShape:
    """What the model needs to know about the scalars of one variant."""
    bits: int                      # every magnitude is < 2^bits (provable)
    maxmag: int                    # largest possible magnitude
    cdfs: list                     # magnitude CDFs, one per point type (equal weights)
    points_per_scalar: int         # 1 (plain, fold) or 2 (glv)


def _max_load(mu: float, count: int) -> float:
    """Typical largest of `count` bucket loads of mean mu (Poisson/normal tail)."""
    count = max(count, 1)
    return mu + math.sqrt(2.0 * max(mu, 1.0) * math.log(2.0 * count)) + 1.0


def _rounds_from(loads: list[float]) -> int:
    return max(1, math.ceil(math.log2(max(max(loads), 2.0))))


QMAX = 64            # windows whose high part takes <= QMAX values mod 2^c are computed exactly


def window_dists_1d(shape: ScalarShape, c: int) -> tuple[int, int, list[np.ndarray]]:
    """(W, w0, pvecs): W windows; windows below w0 are uniform; pvecs[i] is the
    digit-magnitude distribution of window w0 + i, computed from the magnitude
    distribution with the carry probability propagated upwards (carries treated
    as independent of the window's own bits)."""
    cache = shape.__dict__.setdefault("_cache", {})     # per object: ids are reused after collection
    if c in cache:
        return cache[c]
    W = shape.bits // c + 1
    mm = shape.maxmag
    w0 = next(w for w in range(W) if (mm >> (c * (w + 1))) <= QMAX or w == W - 1)
    half, full = 1 << (c - 1), 1 << c
    carry = 0.5
    pvecs = []
    for w in range(w0, W):
        s = c * w
        if w < W - 1:
            v = np.arange(full, dtype=float)
            px = np.zeros(full)
            for q in range((mm >> (c * (w + 1))) + 1):
                base = float(q * full)
                for G in shape.cdfs:
                    px += (G((base + v + 1) * 2.0 ** s - 1) - G((base + v) * 2.0 ** s - 1)) / len(shape.cdfs)
            px = px / px.sum()
            pv = np.zeros(full + 1)
            pv[:-1] += (1 - carry) * px
            pv[1:] += carry * px
            pvec = np.zeros(half + 1)
            pvec[:half] += pv[:half]
            np.add.at(pvec, full - np.arange(half, full + 1), pv[half:])
            carry = float(pv[half:].sum())
        else:
            T = mm >> s
            if T + 1 > half:
                raise ValueError("top window overflows the bucket range")
            v = np.arange(T + 1, dtype=float)
            pt = np.zeros(T + 1)
            for G in shape.cdfs:
                pt += (G((v + 1) * 2.0 ** s - 1) - G(v * 2.0 ** s - 1)) / len(shape.cdfs)
            pt = pt / pt.sum()
            pvec = np.zeros(T + 2)
            pvec[:-1] += (1 - carry) * pt
            pvec[1:] += carry * pt
        pvecs.append(pvec)
    cache[c] = (W, w0, pvecs)
    return W, w0, pvecs


def model_1d(N: int, c: int, shape: ScalarShape, costs: OpCosts, *, variant: str,
             endo_M: float = 0.0) -> MSMCost:
    npts = N * shape.points_per_scalar
    W, w0, pvecs = window_dists_1d(shape, c)
    full = uniform_window_1d(c, npts)
    parts = [general_window_1d(pv, npts) for pv in pvecs]
    acc = w0 * full["acc"] + sum(x["acc"] for x in parts)
    rr = w0 * full["run_r"] + sum(x["run_r"] for x in parts)
    rt = w0 * full["run_t"] + sum(x["run_t"] for x in parts)
    dbl = (W - 1) * c
    comb = W - 1
    inv = 0
    if costs.mode == "batch_affine":
        loads = [_max_load(npts * x["pmax"], x["buckets"]) for x in parts]
        if w0:
            loads.append(_max_load(npts * full["pmax"], w0 * full["buckets"]))
        inv = _rounds_from(loads)
    total = (acc * costs.acc + rr * costs.run_r + rt * costs.add + comb * costs.add + dbl * costs.dbl
             + inv * (costs.inv - BATCH_M_PER_INVERSE) + endo_M)
    return MSMCost(variant, costs.mode, N, c, W, shape.bits, acc, rr, rt, 0.0, comb, dbl, inv, endo_M, total,
                   {"acc_M": acc * costs.acc, "aggregation_M": rr * costs.run_r + rt * costs.add,
                    "combine_M": comb * costs.add + dbl * costs.dbl, "inversions_M": inv * costs.inv,
                    "endo_M": endo_M, "exact_windows": W - w0})


@dataclass
class FoldShape:
    """z = f1*b1 + f2*b2 (f uniform on [-1/2, 1/2)^2) in Z[omega] coordinates."""
    basis: list
    n: int
    bits: int


ENUM_CAP = 1 << 18


def fold_window_dists(fs: FoldShape, c: int):
    """(L, w0, dists): windows below w0 uniform over the 4^c hexagon digits;
    window w >= w0 from the integer points of the Babai parallelogram scaled
    by 2^-(cw), reduced to hexagon digits and folded to canonical buckets."""
    cache = fs.__dict__.setdefault("_cache", {})
    if c in cache:
        return cache[c]
    h = 1 << c
    (a1, a2), (b1, b2) = fs.basis
    det = a1 * b2 - a2 * b1
    dists = {}
    w = 0
    while fs.n / 4.0 ** (c * w) > ENUM_CAP:
        w += 1
    w0 = w
    while True:
        sc = 2.0 ** (c * w)
        hx = (abs(a1) + abs(b1)) / 2.0 / sc + 1
        hy = (abs(a2) + abs(b2)) / 2.0 / sc + 1
        xs = np.arange(-math.ceil(hx), math.ceil(hx) + 1)
        ys = np.arange(-math.ceil(hy), math.ceil(hy) + 1)
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        X, Y = X.ravel(), Y.ravel()
        Xf, Yf = X.astype(float), Y.astype(float)
        f1 = (Xf * float(b2) - Yf * float(b1)) * (sc / float(det))
        f2 = (Yf * float(a1) - Xf * float(a2)) * (sc / float(det))
        m = (f1 >= -0.5) & (f1 < 0.5) & (f2 >= -0.5) & (f2 < 0.5)
        X, Y = X[m].astype(np.int64), Y[m].astype(np.int64)
        tot = len(X)
        nz = (X != 0) | (Y != 0)
        if not nz.any():
            break
        rx, ry = _hex_rep_vec(X[nz], Y[nz], h)
        nz2 = (rx != 0) | (ry != 0)
        sx, sy = _to_sector_vec(rx[nz2], ry[nz2])
        keys, counts = np.unique(np.stack([sx, sy]), axis=1, return_counts=True)
        dists[w] = (keys[0], keys[1], counts / tot, 1.0 - counts.sum() / tot)
        w += 1
    L = w
    out = (L, w0, [dists[i] for i in range(w0, L)])
    cache[c] = out
    return out


def model_fold(N: int, c: int, fs: FoldShape, costs: OpCosts, *, unit_M: float = 1.0) -> MSMCost:
    L, w0, dists = fold_window_dists(fs, c)
    full = hex_window(1 << c, N)
    parts = [hex_window_general(bx, by, pr, p0, N) for bx, by, pr, p0 in dists]
    acc = w0 * full["acc"] + sum(x["acc"] for x in parts)
    grp = w0 * full["group"] + sum(x["group"] for x in parts)
    rr = w0 * full["run_r"] + sum(x["run_r"] for x in parts)
    rt = w0 * full["run_t"] + sum(x["run_t"] for x in parts)
    dbl = (L - 1) * c
    comb = (L - 1) + L                    # Horner additions + X + omega(Y) per window
    omega_M = L * 1.0                     # omega on the Jacobian Y-sum: beta^2 * X
    endo = 2.0 * N * unit_M               # beta*x and beta^2*x for every point
    inv = 0
    if costs.mode == "batch_affine":
        loads = [_max_load(N * x["pmax"], x["buckets"]) for x in parts]
        if w0:
            loads.append(_max_load(N * full["pmax"], w0 * full["buckets"]))
        lines = [x["maxline"] for x in parts] + ([full["maxline"]] if w0 else [])
        inv = _rounds_from(loads) + 2 * _rounds_from([float(v) for v in lines])
    total = (acc * costs.acc + grp * costs.group + rr * costs.run_r + rt * costs.add + comb * costs.add
             + dbl * costs.dbl + omega_M + endo + inv * (costs.inv - BATCH_M_PER_INVERSE * (costs.mode == "batch_affine")))
    return MSMCost("fold", costs.mode, N, c, L, fs.bits, acc, rr, rt, grp, comb, dbl, inv, endo + omega_M, total,
                   {"acc_M": acc * costs.acc, "aggregation_M": grp * costs.group + rr * costs.run_r + rt * costs.add,
                    "combine_M": comb * costs.add + dbl * costs.dbl, "inversions_M": inv * costs.inv,
                    "endo_M": endo + omega_M, "exact_windows": L - w0})


def best_over_c(fn, cs) -> MSMCost:
    best = None
    for c in cs:
        try:
            r = fn(c)
        except ValueError:
            continue
        if best is None or r.total_M < best.total_M:
            best = r
    assert best is not None
    return best


# ---------------------------------------------------------------------------
# curves: n, the endomorphism used, its cost
# ---------------------------------------------------------------------------

@dataclass
class CurveSpec:
    name: str
    n: int
    D: int
    model: str                     # costmodel CURVE_MODELS key
    lam: int                       # eigenvalue of the generator alpha on the order-n subgroup
    alpha: tuple[int, int]         # alpha = a + b*omega
    alpha_ops: dict                # {"M", "S"} of one application (affine input)
    affine_output: bool            # alpha(P) comes out affine (a unit) or projective (a chain)
    note: str = ""
    p: int = 0
    lam_omega: int = 0
    weierstrass_a: int = 0

    @property
    def bits(self) -> int:
        return self.n.bit_length()

    def alpha_M(self) -> float:
        return self.alpha_ops["M"] + S_W * self.alpha_ops["S"]

    def endo_cost_per_point(self, npts: int) -> float:
        return self.alpha_M() + (0.0 if self.affine_output else normalise_cost_per_point(npts))


INPUTS_FILE = os.path.join("research", "endosweep_msm_20261008", "curves.input.json")


def freeze_inputs(std_curves: str, curves_json: str, arkworks_json: str, chains_json: str) -> dict:
    """Collect n, p, the omega eigenvalue and the cheapest element for the chain
    curves from the earlier sweeps and the std-curves checkout, verify them,
    and return the frozen record written to ``curves.input.json``."""
    from .corpus import _int
    sweep = {r["name"]: r for r in json.load(open(curves_json))["results"]}
    src = {}
    for path, key in ((os.path.join(std_curves, "other", "curves.json"), "Tom-384"),
                      (os.path.join(std_curves, "bls", "curves.json"), "Bandersnatch"),
                      (arkworks_json, "cp6_782")):
        for c in json.load(open(path))["curves"]:
            if c["name"] == key:
                src[key] = c
    chains = json.load(open(chains_json))
    out = []

    def lam_omega_from(row_name, element, eig_hex, n, D):
        a, b = element
        lam_alpha = int(eig_hex, 16)
        tau, nw = QO.omega_trace_norm(D)
        # the realised chain is the element up to a unit (+-1 here): try both signs
        for sgn in (1, -1):
            lam = (sgn * lam_alpha - a) * pow(b, -1, n) % n
            if (lam * lam - tau * lam + nw) % n == 0:
                return lam
        raise ValueError(f"{row_name}: eigenvalue does not satisfy omega's minimal polynomial")

    # chain curves from the cross-curve sweep
    for key, swname in (("Tom-384", "other/Tom-384"), ("Bandersnatch", "bls/Bandersnatch"),
                        ("cp6_782", "arkworks/cp6_782")):
        c, r = src[key], sweep[swname]
        p, n, h = _int(c["field"]["p"]), _int(c["order"]), _int(c.get("cofactor", "0x1"))
        prm = c["params"]
        if c["form"] == "Weierstrass":
            T = Target(key, p, "weierstrass", {"a": _int(prm["a"]), "b": _int(prm["b"])}, n, h)
            wa = _int(prm["a"]) % p
        else:
            T = Target(key, p, "edwards", {"a": _int(prm["a"]), "d": _int(prm["d"])}, n, h)
            wa = None
        verify(T)
        if not T.verified:
            raise ValueError(f"{key}: {T.verification}")
        rows = []
        for row in r["rows"]:
            lam_w = lam_omega_from(swname, row["element"], row["eigenvalue"], n, r["D"])
            rows.append({"element": row["element"], "norm": row["norm"], "order": row["order"],
                         "ops": row["ops"], "eigenvalue": row["eigenvalue"], "lam_omega": hex(lam_w)})
        lam_ws = {x["lam_omega"] for x in rows}
        out.append({"name": swname, "p": hex(p), "n": hex(n), "cofactor": h, "D": r["D"],
                    "class_number": r["class_number"], "arithmetic": r["arithmetic"],
                    "weierstrass_a": hex(wa) if wa is not None else None,
                    "verification": T.verification, "lam_omega_consistent": len(lam_ws) <= 2, "rows": rows})
    # CryptoPro-B from the chain sweep's frozen export (cheapest ordering per element)
    p, n = int(chains["p"], 16), int(chains["n"], 16)
    lam_w = int(chains["omega_root"], 16)
    best: dict[tuple, dict] = {}
    for ch in chains["chains"]:
        key = tuple(ch["element"])
        if key not in best or ch["model_ops"]["optimised"]["M_eq"] < best[key]["model_ops"]["optimised"]["M_eq"]:
            best[key] = ch
    rows = []
    for key, ch in sorted(best.items(), key=lambda kv: kv[1]["model_ops"]["optimised"]["M_eq"]):
        rows.append({"element": list(ch["element"]), "matched_element": ch["matched_element"], "norm": ch["norm"],
                     "order": ch["order"], "ops": ch["model_ops"], "eigenvalue": ch["eigenvalue"],
                     "lam_omega": hex(lam_w), "chain_id": ch["id"]})
    out.append({"name": "gost/CryptoPro-B", "p": hex(p), "n": hex(n), "cofactor": 1, "D": chains["D_K"],
                "class_number": chains["class_number"], "arithmetic": "a = -3: dbl-2001-b 3M + 5S",
                "weierstrass_a": chains["a"], "verification": "targets.py GOST CryptoPro-B; chains.constants.json",
                "lam_omega_consistent": True, "rows": rows})
    return {"format": FORMAT + "/inputs", "generator": GENERATOR,
            "sources": {"std_curves": "J08nY/std-curves (other/Tom-384, bls/Bandersnatch)",
                        "curves_json": curves_json, "arkworks_json": arkworks_json, "chains_json": chains_json},
            "curves": out}


def load_inputs(path: str = INPUTS_FILE) -> dict:
    data = json.load(open(path))
    for c in data["curves"]:
        n = int(c["n"], 16)
        assert isprime(n), c["name"]
        tau, nw = QO.omega_trace_norm(c["D"])
        for r in c["rows"]:
            lw = int(r["lam_omega"], 16)
            assert (lw * lw - tau * lw + nw) % n == 0, (c["name"], r["element"])
    return data


def _model_key_for(arith_note: str) -> str:
    if arith_note.startswith("a = 0"):
        return "weierstrass_jacobian_a=0"
    if arith_note.startswith("a = -3") or "isomorphic to an a = -3" in arith_note:
        return "weierstrass_jacobian_a=-3"
    return "weierstrass_jacobian_generic_a"


def chain_eigenvalue(row: dict, n: int, D: int) -> int:
    """Eigenvalue of the element itself, a + b*lam_omega (checked against the
    recorded eigenvalue of the realised chain up to sign/conjugation)."""
    a, b = row["element"]
    return (a + b * int(row["lam_omega"], 16)) % n


def curve_specs(inputs: dict | None = None) -> list[CurveSpec]:
    """The six curves of the sweep, each with its cheapest endomorphism."""
    specs: list[CurveSpec] = []
    T = {t.name: t for t in deployed_targets()}
    for name, label in (("secp256k1", "secp256k1"), ("BLS12-381 G1", "BLS12-381 G1")):
        t = T[name]
        lam_w = QO.omega_eigenvalues(-3, t.n)[0]
        lam3 = (lam_w - 1) % t.n                         # zeta_3 = omega - 1
        specs.append(CurveSpec(label, t.n, -3, t.cost_model, lam3, (-1, 1), {"M": 1, "S": 0}, True,
                               "zeta_3: (x, y) -> (beta x, y), one multiplication, affine in and out",
                               p=t.p, lam_omega=lam_w, weierstrass_a=0))
    inputs = inputs or load_inputs()
    order = {"bls/Bandersnatch": 0, "gost/CryptoPro-B": 1, "arkworks/cp6_782": 2, "other/Tom-384": 3}
    for c in sorted(inputs["curves"], key=lambda c: order.get(c["name"], 9)):
        n = int(c["n"], 16)
        row = min(c["rows"], key=lambda r: r["ops"]["optimised"]["M_eq"])
        lam = chain_eigenvalue(row, n, c["D"])
        ops = row["ops"]["optimised"]
        specs.append(CurveSpec(c["name"], n, c["D"], _model_key_for(c["arithmetic"]), lam, tuple(row["element"]),
                               {"M": ops["M"], "S": ops["S"]}, False,
                               f"{row['element'][0]} + {row['element'][1]}w as {'.'.join(map(str, row['order']))}, "
                               f"optimised evaluator {ops['M']}M + {ops['S']}S (affine input, Jacobian output); "
                               f"{c['arithmetic']}",
                               p=int(c["p"], 16), lam_omega=int(row["lam_omega"], 16),
                               weierstrass_a=int(c["weierstrass_a"], 16) if c.get("weierstrass_a") else 0))
    return specs


@dataclass
class GLVShape:
    bound: int
    bound_bits: int
    basis: list
    empirical_max_bits: int


def glv_shape(spec: CurveSpec, samples: int = 64) -> GLVShape:
    red = LA.reduce([1, spec.lam], spec.n)
    cb = LA.coefficient_bits(red, samples=samples)
    return GLVShape(red.babai_bound, red.babai_bound.bit_length(), red.basis, cb["empirical_max_bits"])


def shapes(spec: CurveSpec):
    """(plain, glv, glv lattice summary, fold shape or None)."""
    plain = ScalarShape(spec.bits, spec.n - 1, [cdf_uniform(spec.n - 1)], 1)
    g = glv_shape(spec)
    (b11, b12), (b21, b22) = g.basis
    glv = ScalarShape(g.bound_bits, g.bound - 1, [cdf_trapezoid(b11, b21), cdf_trapezoid(b12, b22)], 2)
    fold = None
    if spec.D == -3:
        red = LA.reduce([1, spec.lam_omega], spec.n)
        fold = FoldShape(red.basis, spec.n, red.babai_bound.bit_length())
    return plain, glv, g, fold


def sweep_curve(spec: CurveSpec, Ns, modes=("mixed", "batch_affine")) -> dict:
    plain_s, glv_s, g, fold_s = shapes(spec)
    out = {"curve": spec.name, "n_bits": spec.bits, "D": spec.D, "arith_model": spec.model,
           "alpha": list(spec.alpha), "alpha_ops": spec.alpha_ops, "alpha_M": spec.alpha_M(),
           "affine_output": spec.affine_output, "note": spec.note,
           "glv": {"babai_bound_bits": g.bound_bits, "empirical_max_bits": g.empirical_max_bits,
                   "basis_inf_norm_bits": [max(abs(x) for x in b).bit_length() for b in g.basis]},
           "rows": []}
    for mode in modes:
        costs = op_costs(spec.model, mode)
        for N in Ns:
            plain = best_over_c(lambda c: model_1d(N, c, plain_s, costs, variant="plain"), range(1, C_MAX_1D + 1))
            glv0 = best_over_c(lambda c: model_1d(N, c, glv_s, costs, variant="glv"), range(1, C_MAX_1D + 1))
            ce = spec.endo_cost_per_point(N)
            glv_total = glv0.total_M + N * ce
            cstar = (plain.total_M - glv0.total_M) / N
            row = {"mode": mode, "N": N, "logN": int(math.log2(N)),
                   "plain": _cost_row(plain), "glv_no_endo": _cost_row(glv0),
                   "endo_per_point_M": round(ce, 3), "glv_total_M": round(glv_total, 1),
                   "glv_gain_pct": round(100.0 * (plain.total_M - glv_total) / plain.total_M, 3),
                   "glv_gain_pct_chain_only": round(100.0 * (plain.total_M - glv0.total_M - N * spec.alpha_M())
                                                    / plain.total_M, 3),
                   "C_star_M": round(cstar, 3),
                   "C_star_hypothesis_M": round(spec.bits * costs.acc / (plain.c * (plain.c + 1)), 3),
                   "acc_cost_M": costs.acc,
                   "c_at_cap": plain.c == C_MAX_1D or glv0.c == C_MAX_1D}
            if spec.D == -3:
                fold = best_over_c(lambda c: model_fold(N, c, fold_s, costs), range(2, C_MAX_FOLD + 1))
                row["fold"] = _cost_row(fold)
                row["fold_gain_pct"] = round(100.0 * (plain.total_M - fold.total_M) / plain.total_M, 3)
                row["fold_c_at_cap"] = fold.c == C_MAX_FOLD
            out["rows"].append(row)
    return out


def _cost_row(r: MSMCost) -> dict:
    return {"c": r.c, "windows": r.windows, "coeff_bits": r.coeff_bits, "total_M": round(r.total_M, 1),
            "per_point_M": round(r.per_point, 3), "acc_adds": round(r.acc_adds, 1),
            "run_r_adds": round(r.run_r_adds, 1), "run_t_adds": round(r.run_t_adds, 1),
            "group_adds": round(r.group_adds, 1), "combine_adds": r.combine_adds, "doublings": r.doublings,
            "inversions": r.inversions,
            "breakdown": {k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.breakdown.items()}}


# ---------------------------------------------------------------------------
# counted reference implementation (a = 0 short Weierstrass, e.g. secp256k1)
# ---------------------------------------------------------------------------

class CountedField:
    """F_p with every multiplication, squaring and inversion counted.
    Additions, subtractions and multiplications by 2, 3, 4, 8 are free (EFD convention)."""

    def __init__(self, p: int):
        self.p = p
        self.M = self.S = self.I = 0

    def mul(self, a, b):
        self.M += 1
        return a * b % self.p

    def sqr(self, a):
        self.S += 1
        return a * a % self.p

    def inv(self, a):
        self.I += 1
        return pow(a, -1, self.p)

    def batch_inv(self, xs: list[int]) -> list[int]:
        """Montgomery's trick: 3(m-1) M + 1 I."""
        m = len(xs)
        if m == 0:
            return []
        pref = [xs[0]]
        for x in xs[1:]:
            pref.append(self.mul(pref[-1], x))
        inv = self.inv(pref[-1])
        out = [0] * m
        for i in range(m - 1, 0, -1):
            out[i] = self.mul(inv, pref[i - 1])
            inv = self.mul(inv, xs[i])
        out[0] = inv
        return out

    @property
    def total_M(self) -> float:
        return self.M + S_W * self.S + I_W * self.I


class Jac0:
    """Jacobian arithmetic on y^2 = x^3 + b with counted field operations and
    per-type operation counters.  Formulas: dbl-2009-l (2M + 5S),
    add-2007-bl (11M + 5S), madd-2007-bl (7M + 4S); None is the identity."""

    def __init__(self, F: CountedField):
        self.F = F
        self.ops = {"dbl": 0, "add": 0, "madd": 0, "aff": 0, "inv_rounds": 0, "endo_M": 0}

    def dbl(self, P):
        if P is None:
            return None
        F, p = self.F, self.F.p
        X1, Y1, Z1 = P
        if Y1 == 0:
            return None
        self.ops["dbl"] += 1
        A = F.sqr(X1)
        B = F.sqr(Y1)
        C = F.sqr(B)
        D = 2 * (F.sqr((X1 + B) % p) - A - C) % p
        E = 3 * A % p
        Fv = F.sqr(E)
        X3 = (Fv - 2 * D) % p
        Y3 = (F.mul(E, (D - X3) % p) - 8 * C) % p
        Z3 = 2 * F.mul(Y1, Z1) % p
        return X3, Y3, Z3

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        F, p = self.F, self.F.p
        X1, Y1, Z1 = P
        X2, Y2, Z2 = Q
        Z1Z1 = F.sqr(Z1)
        Z2Z2 = F.sqr(Z2)
        U1 = F.mul(X1, Z2Z2)
        U2 = F.mul(X2, Z1Z1)
        S1 = F.mul(F.mul(Y1, Z2), Z2Z2)
        S2 = F.mul(F.mul(Y2, Z1), Z1Z1)
        H = (U2 - U1) % p
        r = 2 * (S2 - S1) % p
        if H == 0:
            if r == 0:
                return self.dbl(P)
            return None
        self.ops["add"] += 1
        I_ = F.sqr(2 * H % p)
        J = F.mul(H, I_)
        V = F.mul(U1, I_)
        X3 = (F.sqr(r) - J - 2 * V) % p
        Y3 = (F.mul(r, (V - X3) % p) - 2 * F.mul(S1, J)) % p
        Z3 = F.mul((F.sqr((Z1 + Z2) % p) - Z1Z1 - Z2Z2) % p, H)
        return X3, Y3, Z3

    def madd(self, P, q):
        """P Jacobian (or None) + q affine."""
        if P is None:
            return (q[0], q[1], 1)
        F, p = self.F, self.F.p
        X1, Y1, Z1 = P
        x2, y2 = q
        Z1Z1 = F.sqr(Z1)
        U2 = F.mul(x2, Z1Z1)
        S2 = F.mul(F.mul(y2, Z1), Z1Z1)
        H = (U2 - X1) % p
        r = 2 * (S2 - Y1) % p
        if H == 0:
            if r == 0:
                return self.dbl(P)
            return None
        self.ops["madd"] += 1
        HH = F.sqr(H)
        I_ = 4 * HH % p
        J = F.mul(H, I_)
        V = F.mul(X1, I_)
        X3 = (F.sqr(r) - J - 2 * V) % p
        Y3 = (F.mul(r, (V - X3) % p) - 2 * F.mul(Y1, J)) % p
        Z3 = (F.sqr((Z1 + H) % p) - Z1Z1 - HH) % p
        return X3, Y3, Z3

    def tree_reduce(self, lists: list[list]) -> list:
        """Sum every list of affine points by a pairwise tree; each round's
        additions share one batched inversion.  Returns one affine point (or
        None) per list."""
        F, p = self.F, self.F.p
        cur = [list(L) for L in lists]
        while True:
            pairs = [(i, j) for i, L in enumerate(cur) for j in range(0, len(L) - 1, 2)]
            if not pairs:
                break
            self.ops["inv_rounds"] += 1
            dens = []
            for i, j in pairs:
                (x1, y1), (x2, y2) = cur[i][j], cur[i][j + 1]
                if x1 == x2:
                    raise ArithmeticError("exceptional affine addition")
                dens.append((x2 - x1) % p)
            invs = F.batch_inv(dens)
            nxt = [[] for _ in cur]
            k = 0
            for i, L in enumerate(cur):
                for j in range(0, len(L) - 1, 2):
                    (x1, y1), (x2, y2) = L[j], L[j + 1]
                    lam = F.mul((y2 - y1) % p, invs[k])
                    x3 = (F.sqr(lam) - x1 - x2) % p
                    y3 = (F.mul(lam, (x1 - x3) % p) - y1) % p
                    self.ops["aff"] += 1
                    nxt[i].append((x3, y3))
                    k += 1
                if len(L) % 2:
                    nxt[i].append(L[-1])
            cur = nxt
        return [L[0] if L else None for L in cur]


def signed_windows(m: int, c: int, W: int) -> list[int]:
    """Signed recoding of m >= 0 into W windows: digits in [-2^(c-1), 2^(c-1)]
    below the top, the top window takes the remaining bits plus the carry."""
    out, carry, half, mask = [], 0, 1 << (c - 1), (1 << c) - 1
    for _ in range(W - 1):
        v = (m & mask) + carry
        m >>= c
        if v >= half:
            d, carry = v - (1 << c), 1
        else:
            d, carry = v, 0
        out.append(d)
    v = m + carry
    if v > half:
        raise ValueError("top window overflow")
    out.append(v)
    return out


def _neg(P, p):
    return (P[0], (-P[1]) % p)


def _aggregate_1d(J: Jac0, buckets: list, mode: str):
    """sum_j j*S_j by the running sum, buckets[j-1] = S_j (Jacobian or affine)."""
    R = T = None
    for S in reversed(buckets):
        if S is not None:
            if mode == "mixed":
                R = J.add(R, S)
            else:
                R = J.madd(R, S)
        if R is not None:
            T = R if T is None else J.add(T, R)
    return T


def counted_msm_1d(J: Jac0, items: list[tuple[tuple[int, int], int]], c: int, bits: int, mode: str):
    """Pippenger over (affine point, magnitude) items; returns the Jacobian sum."""
    p = J.F.p
    W = bits // c + 1
    B = 1 << (c - 1)
    digs = [signed_windows(m, c, W) for _, m in items]
    sums = []
    if mode == "mixed":
        for w in range(W):
            bk = [None] * B
            for (P, _), d in zip(items, digs):
                dw = d[w]
                if dw:
                    bk[abs(dw) - 1] = J.madd(bk[abs(dw) - 1], P if dw > 0 else _neg(P, p))
            sums.append(_aggregate_1d(J, bk, mode))
    else:
        lists = [[] for _ in range(W * B)]
        for (P, _), d in zip(items, digs):
            for w, dw in enumerate(d):
                if dw:
                    lists[w * B + abs(dw) - 1].append(P if dw > 0 else _neg(P, p))
        red = J.tree_reduce(lists)
        for w in range(W):
            sums.append(_aggregate_1d(J, red[w * B:(w + 1) * B], mode))
    acc = sums[-1]
    for w in range(W - 2, -1, -1):
        for _ in range(c):
            acc = J.dbl(acc)
        acc = J.add(acc, sums[w])
    return acc, W


def counted_msm_fold(J: Jac0, pts: list[tuple[int, int]], zs: list[tuple[int, int]], c: int, mode: str,
                     beta: int):
    """Hexagonal radix-2^c Pippenger with unit folding; omega(x, y) = (beta^2 x, -y)."""
    F, p = J.F, J.F.p
    beta2 = beta * beta % p
    exps = [hex_expand(a, b, c) for a, b in zs]
    L = max(len(e) for e in exps)
    # unit images: x, beta x, beta^2 x (two counted multiplications per point)
    imgs = []
    for x, y in pts:
        bx, b2x = F.mul(beta, x), F.mul(beta2, x)
        J.ops["endo_M"] += 2
        xs = (x, b2x, bx)                                 # omega^j: x * beta^(2j mod 3)
        imgs.append([(xs[j % 3], y if j % 2 == 0 else (-y) % p) for j in range(6)])
    keyed: list[dict] = [dict() for _ in range(L)]
    for i, e in enumerate(exps):
        for w, (x, y) in enumerate(e):
            if x == 0 and y == 0:
                continue
            xs_, ys_, j = rotate_to_sector(x, y)
            keyed[w].setdefault((xs_, ys_), []).append(imgs[i][j])
    win = []
    if mode == "mixed":
        bsum = []
        for w in range(L):
            d = {}
            for key, plist in keyed[w].items():
                acc = None
                for P in plist:
                    acc = J.madd(acc, P)
                d[key] = acc
            bsum.append(d)
    else:
        flat = [(w, key) for w in range(L) for key in keyed[w]]
        red = J.tree_reduce([keyed[w][key] for w, key in flat])
        bsum = [dict() for _ in range(L)]
        for (w, key), S in zip(flat, red):
            bsum[w][key] = S
    # group by column x (axis 0) and by row y >= 1 (axis 1); in batch-affine
    # mode every group of every window shares the pairwise-tree rounds
    line_sums = []
    for axis in (0, 1):
        groups: dict[tuple[int, int], list] = {}
        for w in range(L):
            for (x, y), S in bsum[w].items():
                k = (x, y)[axis]
                if k >= 1:
                    groups.setdefault((w, k), []).append(S)
        keys = list(groups)
        if mode == "mixed":
            G = []
            for key in keys:
                g = None
                for S in groups[key]:
                    g = J.add(g, S)
                G.append(g)
        else:
            G = J.tree_reduce([groups[key] for key in keys])
        line_sums.append(dict(zip(keys, G)))
    for w in range(L):
        lines = {}
        for axis in (0, 1):
            idx = {k: g for (ww, k), g in line_sums[axis].items() if ww == w}
            R = T = None
            for k in range(max(idx, default=0), 0, -1):
                g = idx.get(k)
                if g is not None:
                    R = J.add(R, g) if mode == "mixed" else J.madd(R, g)
                if R is not None:
                    T = R if T is None else J.add(T, R)
            lines[axis] = T
        X, Y = lines[0], lines[1]
        if Y is not None:
            Y = (F.mul(beta2, Y[0]), (-Y[1]) % p, Y[2])       # omega on Jacobian
            J.ops["endo_M"] += 1
        win.append(J.add(X, Y))
    acc = win[-1]
    for w in range(L - 2, -1, -1):
        for _ in range(c):
            acc = J.dbl(acc)
        acc = J.add(acc, win[w])
    return acc, L


# ---------------------------------------------------------------------------
# validation on secp256k1
# ---------------------------------------------------------------------------

def _aff_add(p, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = 3 * x1 * x1 * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return x3, (lam * (x1 - x3) - y1) % p


def _aff_mul(p, k, P):
    R = None
    while k:
        if k & 1:
            R = _aff_add(p, R, P)
        P = _aff_add(p, P, P)
        k >>= 1
    return R


def _to_aff(p, P):
    if P is None:
        return None
    X, Y, Z = P
    zi = pow(Z, -1, p)
    return X * zi * zi % p, Y * zi * zi * zi % p


@dataclass
class Secp:
    p: int
    n: int
    b: int
    G: tuple[int, int]
    beta: int                      # (x, y) -> (beta x, y) acts as lam3
    lam3: int
    lam_omega: int                 # omega(x, y) = (beta^2 x, -y) acts as lam_omega = -lam3^2


def secp256k1() -> Secp:
    t = next(x for x in deployed_targets() if x.name == "secp256k1")
    p, n, b = t.p, t.n, t.coeffs["b"]
    x = 1
    while True:                                           # lift a point; cofactor 1
        rhs = (x ** 3 + b) % p
        y = pow(rhs, (p + 1) // 4, p)
        if y * y % p == rhs:
            break
        x += 1
    G = (x, y)
    assert _aff_mul(p, n, G) is None
    beta = next(r for r in (pow(g, (p - 1) // 3, p) for g in range(2, 50)) if r != 1)
    lams = [r for r in ((l - 1) % n for l in QO.omega_eigenvalues(-3, n))]
    lam3 = next(l for l in lams if _aff_mul(p, l, G) == (beta * x % p, y))
    lam_w = (-lam3 * lam3) % n
    assert _aff_mul(p, lam_w, G) == (beta * beta * x % p, (-y) % p)
    return Secp(p, n, b, G, beta, lam3, lam_w)


def _instance(cv: Secp, N: int, rng: random.Random):
    """N points P_i = [r_i] G with independent random r_i (fixed-base table,
    uncounted) and N random scalars; the expected sum is [sum k_i r_i] G.

    The r_i must be independent: points in arithmetic progression make
    partial bucket sums collide (P_a + P_b = P_c + P_d when a + b = c + d),
    which an affine pairwise tree turns into exceptional additions."""
    p, n = cv.p, cv.n
    table = [cv.G]
    for _ in range(n.bit_length()):
        table.append(_aff_add(p, table[-1], table[-1]))
    pts, rs = [], []
    for _ in range(N):
        r = rng.randrange(1, n)
        P, j, k = None, 0, r
        while k:
            if k & 1:
                P = _aff_add(p, P, table[j])
            k >>= 1
            j += 1
        pts.append(P)
        rs.append(r)
    ks = [rng.randrange(1, n) for _ in range(N)]
    expected = _aff_mul(p, sum(k * r for k, r in zip(ks, rs)) % n, cv.G)
    return pts, ks, expected


def run_counted(cv: Secp, variant: str, mode: str, pts, ks, c: int, red_glv=None, red_fold=None):
    F = CountedField(cv.p)
    J = Jac0(F)
    p = cv.p
    if variant == "plain":
        R, W = counted_msm_1d(J, list(zip(pts, ks)), c, cv.n.bit_length(), mode)
    elif variant == "glv":
        items = []
        for P, k in zip(pts, ks):
            k1, k2 = red_glv.decompose(k)
            phiP = (F.mul(cv.beta, P[0]), P[1])
            J.ops["endo_M"] += 1
            items.append((P if k1 >= 0 else _neg(P, p), abs(k1)))
            items.append((phiP if k2 >= 0 else _neg(phiP, p), abs(k2)))
        R, W = counted_msm_1d(J, items, c, red_glv.babai_bound.bit_length(), mode)
    elif variant == "fold":
        zs = [tuple(red_fold.decompose(k)) for k in ks]
        R, W = counted_msm_fold(J, pts, zs, c, mode, cv.beta)
    else:
        raise ValueError(variant)
    return _to_aff(p, R), W, F, J


def validate(Ns=(1 << 8, 1 << 9, 1 << 10, 1 << 11, 1 << 12), trials: int = 2, seed: int = 20261008,
             naive_check_upto: int = 1 << 8, progress: bool = False) -> dict:
    """Counted Pippenger on secp256k1 against the model, every variant and mode."""
    cv = secp256k1()
    spec = next(s for s in curve_specs() if s.name == "secp256k1")
    plain_s, glv_s, g, fold_s = shapes(spec)
    red_glv = LA.reduce([1, cv.lam3], cv.n)
    red_fold = LA.reduce([1, cv.lam_omega], cv.n)
    assert red_glv.babai_bound.bit_length() == g.bound_bits
    rng = random.Random(seed)
    rows = []
    for N in Ns:
        for t in range(trials):
            pts, ks, expected = _instance(cv, N, rng)
            if N <= naive_check_upto:
                naive = None
                for P, k in zip(pts, ks):
                    naive = _aff_add(cv.p, naive, _aff_mul(cv.p, k, P))
                assert naive == expected
            for mode in ("mixed", "batch_affine"):
                costs = op_costs(spec.model, mode)
                for variant in ("plain", "glv", "fold"):
                    if variant == "plain":
                        m = best_over_c(lambda c: model_1d(N, c, plain_s, costs, variant="plain"), range(1, C_MAX_1D + 1))
                    elif variant == "glv":
                        m = best_over_c(lambda c: model_1d(N, c, glv_s, costs, variant="glv", endo_M=N * 1.0),
                                        range(1, C_MAX_1D + 1))
                    else:
                        m = best_over_c(lambda c: model_fold(N, c, fold_s, costs), range(2, C_MAX_FOLD + 1))
                    t0 = time.time()
                    R, W, F, J = run_counted(cv, variant, mode, pts, ks, m.c, red_glv, red_fold)
                    ok = R == expected
                    if not ok:
                        raise AssertionError(f"MSM mismatch: {variant} {mode} N={N}")
                    # the field counters must equal op counts x formula counts
                    o = J.ops
                    fM = 2 * o["dbl"] + 11 * o["add"] + 7 * o["madd"] + 2 * o["aff"] + o["endo_M"]
                    fS = 5 * o["dbl"] + 5 * o["add"] + 4 * o["madd"] + o["aff"]
                    agg_extra = 0
                    rows.append({
                        "N": N, "trial": t, "mode": mode, "variant": variant, "c": m.c, "windows_model": m.windows,
                        "windows_run": W, "verified": ok,
                        "measured": {"M": F.M, "S": F.S, "I": F.I, "total_M": round(F.total_M, 1), **o},
                        "formula_check": {"M_minus_formula": F.M - fM - _batch_M(o, F), "S_minus_formula": F.S - fS},
                        "model": {"total_M": round(m.total_M, 1), "acc": round(m.acc_adds, 1),
                                  "agg": round(m.run_r_adds + m.run_t_adds + m.group_adds, 1),
                                  "doublings": m.doublings, "inversions": m.inversions},
                        "rel_err_total": round((F.total_M - m.total_M) / m.total_M, 5),
                        "seconds": round(time.time() - t0, 2)})
                    if progress:
                        r = rows[-1]
                        print(f"N={N} t={t} {mode:12s} {variant:5s} c={m.c} meas={F.total_M:.0f} "
                              f"model={m.total_M:.0f} err={100 * r['rel_err_total']:+.2f}% {r['seconds']}s", flush=True)
    return {"curve": "secp256k1", "seed": seed, "trials": trials, "rows": rows, "summary": _val_summary(rows)}


def _batch_M(ops: dict, F: CountedField) -> int:
    """Multiplications spent inside batched inversions: 3(m-1) per round, i.e.
    3 * (affine additions) - 3 * (rounds)."""
    return 3 * ops["aff"] - 3 * ops["inv_rounds"]


def _val_summary(rows: list[dict]) -> dict:
    out = {}
    for mode in ("mixed", "batch_affine"):
        for variant in ("plain", "glv", "fold"):
            rs = [r for r in rows if r["mode"] == mode and r["variant"] == variant]
            if not rs:
                continue
            errs = [r["rel_err_total"] for r in rs]
            out[f"{mode}/{variant}"] = {"runs": len(rs), "mean_rel_err": round(statistics.fmean(errs), 5),
                                        "max_abs_rel_err": round(max(abs(e) for e in errs), 5)}
    # per-N mean error (trials averaged), the quantity the tolerance is stated for
    byN = {}
    for r in rows:
        byN.setdefault((r["mode"], r["variant"], r["N"]), []).append(r["rel_err_total"])
    out["max_abs_trial_mean_rel_err"] = round(max(abs(statistics.fmean(v)) for v in byN.values()), 5)
    return out


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def run(Ns=None) -> dict:
    Ns = Ns or [1 << k for k in range(6, 23)]
    specs = curve_specs()
    return {"format": FORMAT, "generator": GENERATOR,
            "constants": {"S_per_M": S_W, "I_per_M": I_W, "affine_add": "2M + 1S + 3M batch = %.1f M" % op_costs(
                "weierstrass_jacobian_a=0", "batch_affine").aff,
                "normalise_per_point": "3M batch + 3M + 1S = 6.8 M (+ I/N)",
                "curve_models": {k: CM.CURVE_MODELS[k]["note"] for k in sorted({s.model for s in specs})}},
            "curves": [sweep_curve(s, Ns) for s in specs]}


def _pivot(res: dict, mode: str, key) -> list[str]:
    curves = res["curves"]
    hdr = "| log2 N | " + " | ".join(c["curve"] for c in curves) + " |"
    out = [hdr, "|" + "---|" * (len(curves) + 1)]
    Ns = sorted({r["logN"] for r in curves[0]["rows"]})
    for lg in Ns:
        cells = []
        for c in curves:
            r = next(x for x in c["rows"] if x["logN"] == lg and x["mode"] == mode)
            cells.append(key(r, c))
        out.append(f"| {lg} | " + " | ".join(cells) + " |")
    return out


def markdown(res: dict, val: dict | None) -> str:
    L = ["# Pippenger MSM with endomorphisms: modelled operation counts", "",
         "All costs in base-field multiplications M of each curve (S = %.1f M, I = %.0f M, costmodel.py). "
         "Modelled expectations, not timings; the model is validated against a counted implementation on "
         "secp256k1 (last section).  `mixed`: Jacobian buckets, mADD accumulation.  `batch_affine`: affine "
         "buckets, %.1f M per accumulation addition plus a shared inversion per pairwise-tree round." % (
             S_W, I_W, op_costs("weierstrass_jacobian_a=0", "batch_affine").aff), ""]
    L += ["## Endomorphisms and GLV coefficient sizes", "",
          "| curve | n bits | D | endomorphism | M per image | affine output | Babai bound bits (provable) | largest seen |",
          "|---|---|---|---|---|---|---|---|"]
    for c in res["curves"]:
        L.append(f"| {c['curve']} | {c['n_bits']} | {c['D']} | {c['note']} | {c['alpha_M']:.1f} | "
                 f"{'yes' if c['affine_output'] else 'no: + 6.8 M + I/N batched conversion'} | "
                 f"{c['glv']['babai_bound_bits']} | {c['glv']['empirical_max_bits']} |")
    L.append("")
    for mode in ("batch_affine", "mixed"):
        L += [f"## Break-even endomorphism cost C*(N), {mode} (M per image)", "",
              "C* = (plain - GLV without the images) / N, both at their own optimal window; "
              "GLV wins iff the per-point image cost is below C*.  In brackets: the hypothesis' "
              "b*A/(c(c+1)) with the plain optimum c and A the accumulation cost.", ""]
        L += _pivot(res, mode, lambda r, c: f"{r['C_star_M']:.1f} ({r['C_star_hypothesis_M']:.1f})")
        L += ["", f"## Gain over plain Pippenger, {mode} (%; GLV with the image cost of each curve"
              "; in brackets without the affine conversion; fold = hexagonal unit folding, D = -3 only)", ""]
        L += _pivot(res, mode, lambda r, c: (f"GLV {r['glv_gain_pct']:+.1f} ({r['glv_gain_pct_chain_only']:+.1f})"
                                             if not c["affine_output"] else f"GLV {r['glv_gain_pct']:+.1f}")
                    + (f", fold {r['fold_gain_pct']:+.1f}" if "fold" in r else ""))
        L += ["", f"## Plain Pippenger: optimal window and M per point, {mode}", ""]
        L += _pivot(res, mode, lambda r, c: f"c={r['plain']['c']}: {r['plain']['per_point_M']:.1f}")
        L.append("")
    if val:
        L += ["## Validation: counted Pippenger on secp256k1 against the model", "",
              f"Every run's MSM result equals [sum k_i r_i]G for points P_i = [r_i]G (and the naive sum for N <= 256); "
              f"{val['trials']} trials per N; the model is evaluated at the window it chose.", "",
              "| mode / variant | runs | mean rel. error | max abs rel. error |", "|---|---|---|---|"]
        for k, v in val["summary"].items():
            if isinstance(v, dict):
                L.append(f"| {k} | {v['runs']} | {100 * v['mean_rel_err']:+.2f} % | {100 * v['max_abs_rel_err']:.2f} % |")
        L += ["", "| N | mode | variant | c | windows (model/run) | measured M | model M | error |",
              "|---|---|---|---|---|---|---|---|"]
        for r in val["rows"]:
            L.append(f"| {r['N']} | {r['mode']} | {r['variant']} | {r['c']} | {r['windows_model']}/{r['windows_run']} | "
                     f"{r['measured']['total_M']:.0f} | {r['model']['total_M']:.0f} | {100 * r['rel_err_total']:+.2f} % |")
        L.append("")
    return "\n".join(L)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", default=os.path.join("research", "endosweep_msm_20261008"))
    ap.add_argument("--freeze", action="store_true", help="write curves.input.json from the sources below")
    ap.add_argument("--std-curves", default=None)
    ap.add_argument("--curves-json", default="research/endosweep_curves_20261006/curves.json")
    ap.add_argument("--arkworks-json", default="research/endosweep_curves_20261006/arkworks/curves.json")
    ap.add_argument("--chains-json", default="research/endosweep_chainsweep_20261006/chains.constants.json")
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--skip-validation", action="store_true")
    ap.add_argument("--markdown-only", action="store_true", help="rewrite msm.md from msm.json")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    if a.markdown_only:
        res = json.load(open(os.path.join(a.out_dir, "msm.json")))
        with open(os.path.join(a.out_dir, "msm.md"), "w") as f:
            f.write(markdown(res, res.get("validation")))
        return 0
    if a.freeze:
        if not a.std_curves:
            ap.error("--freeze needs --std-curves")
        rec = freeze_inputs(a.std_curves, a.curves_json, a.arkworks_json, a.chains_json)
        with open(os.path.join(a.out_dir, "curves.input.json"), "w") as f:
            json.dump(rec, f, indent=1)
        print("wrote curves.input.json")
        return 0
    t0 = time.time()
    res = run()
    val = None if a.skip_validation else validate(trials=a.trials, progress=True)
    res["validation"] = val
    res["elapsed_s"] = round(time.time() - t0, 1)
    jpath = os.path.join(a.out_dir, "msm.json")
    with open(jpath, "w") as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(a.out_dir, "msm.md"), "w") as f:
        f.write(markdown(res, val))
    print(f"wrote {jpath} ({res['elapsed_s']} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
