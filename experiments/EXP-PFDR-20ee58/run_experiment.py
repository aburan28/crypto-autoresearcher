#!/usr/bin/env python3
"""EXP-PFDR-20ee58 -- the prime-field digit twin of the binary chained Semaev
system: extra-syzygy deficit at D in {5..8} against a Koszul-only baseline
(H-PFDR-9aadc0, IDEA-20260903-cf63ad).  Executor implementation for
TASK-20260903-5b46a6.

Every number written here is an exact rank over F_p (or GF(2)) produced by the
shared meter ``harness/macaulay_fp`` (TASK-20260903-ba41aa, snapshot 2d2083e5),
used unmodified.  No Groebner basis is computed; no timing is a metric; no
floating point touches a rank.

Planned runs (one immutable run directory each):

    calib          Stage 1: CTRL-BINARY-CALIBRATION -- the committed GF(2)
                   chained system at n = 12 (k = 4) under the cumulative
                   convention with the Koszul (+ Frobenius at p = 2) count;
                   KN-FIND-006 nulls; the Stage 0 identities checked
                   mechanically as a supplement to the hand derivation.
    s1             Stage 2: CTRL-S1-SLICE -- s = 1, d = B in {4, 8}: generator
                   list against IDEA-20260830-cb8e46's chained J built by the
                   meter's direct_presentation; graded ranks as a fixture.
    cell S P       Stage 3/4: one (s, p) cell over 6 curves, planted targets,
                   D in {5..8} (D in {5, 6} at s = 6), arms SEM, NULL-SUPPORT,
                   NULL-TOPOLOGY, NEARBY-NON-CURVE-CUBIC.

Deficit convention (frozen, identical across arms and identical to the
calibration arm's): cumulative multipliers deg m <= D - deg f_i, zero-product
rows dropped (and counted), multilinear in the digits, free in u;
deficit(D) = rows(D) - rank(Mac_D) - koszul(D), koszul(D) = explicit pairwise
Koszul count (1 at D = 8 for two quartics, 0 below), plus the Frobenius count
at p = 2 in the pure squarefree ring (the calibration arm).

Usage:
    python3 experiments/EXP-PFDR-20ee58/run_experiment.py calib
    python3 experiments/EXP-PFDR-20ee58/run_experiment.py s1
    python3 experiments/EXP-PFDR-20ee58/run_experiment.py cell --s 3 --p 4099
Options: --suffix S (re-run id after an infrastructure stop only), --out-root DIR
(smoke tests only).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import random
import resource
import signal
import subprocess
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness import runner  # noqa: E402
from harness.macaulay_fp import (  # noqa: E402
    ColumnSpace,
    Ring,
    analyze_degrees,
    deficit_profile,
    digit_presentation,
    direct_presentation,
    dreg_boolean_null,
    histogram_matched_system,
    preflight,
    substitute,
    support_matched_system,
)
from harness.macaulay_fp.columns import PreflightAbort  # noqa: E402
from harness.semaev import s3_eval, verify_decomposition_certificate  # noqa: E402

EXP_ID = "EXP-PFDR-20ee58"
EXP_AREA = "PFDR-20ee58"
EXP_DIR = os.path.join(REPO, "experiments", EXP_ID)

# ---------------------------------------------------------------------------
# Frozen parameters (copied from specification.yaml; never edited here)
# ---------------------------------------------------------------------------
D_BASE = 2                                   # d = 2: digits a(a - 1) = 0
S_MAIN = [3, 4, 5]                           # D in {5..8}
S_LIMITED = {6: [5, 6]}                      # s = 6 at D <= 6 only; (6, 8) excluded by name
PRIMES = [4099, 16411, 65537]
DEGREES_MAIN = [5, 6, 7, 8]
CURVE_SEEDS = [4100 + k for k in range(1, 7)]  # 4101..4106 per prime
TARGET_SEEDS_DEFAULT = [1]
TARGET_SEEDS_DECIDING = [1, 2]               # second target on the deciding cell (s = 3) only
NULL_SEEDS = [7, 11, 13, 17, 19]             # per (cell, arm)
NONCURVE_SEEDS = [51, 53, 59]
S1_BASES = [4, 8]
WALL_CLOCK_SECONDS_PER_RUN = 7200
MAX_MEMORY_GB = 16
COLUMN_CAP = 60000
DENSE_EQUIV_CAP_BYTES = 4 * 1024**3          # 4 GiB dense-equivalent working set
METER_FILES = [
    "harness/macaulay_fp/__init__.py", "harness/macaulay_fp/columns.py",
    "harness/macaulay_fp/koszul.py", "harness/macaulay_fp/linalg.py",
    "harness/macaulay_fp/localization.py", "harness/macaulay_fp/macaulay.py",
    "harness/macaulay_fp/nulls.py", "harness/macaulay_fp/poly.py",
    "harness/macaulay_fp/presentations.py", "harness/macaulay_fp/series.py",
    "harness/macaulay_fp/fixtures/gf2_chained_builder.py",
    "harness/macaulay_fp/fixtures/chained_gf2_n12_t3_seed2026.json",
    "tests/test_macaulay_fp.py",
]
METER_COMMIT = "2d2083e5"   # tooling(TASK-20260903-ba41aa) snapshot, as named in the handoff
FIXTURE_JSON = os.path.join(REPO, "harness/macaulay_fp/fixtures/chained_gf2_n12_t3_seed2026.json")
FIXTURE_SHA256 = "62d89109f94ef658885ddb5289504df159de01ee4341852b34349d01724bf8e5"

# Frozen prediction, copied for the record only (compared in analyze.py; never adjusted)
FROZEN = {
    "calibration": {"deficit_graded_D3": 1, "deficit_graded_D4": 31, "null": 0},
    "null_support": "deficit(D) = 0 for all D <= 8 at every cell (up to the small-p rank-drop budget)",
    "M1": "SEM deficit(D) = 0 for all D <= 8 at every s, p, curve (prior 0.75)",
    "M2": "deficit(8) - deficit_topology(8) = alpha s + beta, alpha CI excluding 0, p-independent (prior 0.10)",
    "M3": "neither",
}


class RunBudgetExceeded(RuntimeError):
    pass


def _alarm(signum, frame):  # pragma: no cover
    raise RunBudgetExceeded(f"wall clock budget of {WALL_CLOCK_SECONDS_PER_RUN} s exceeded")


def install_budget() -> None:
    soft = MAX_MEMORY_GB * 1024**3
    try:
        resource.setrlimit(resource.RLIMIT_AS, (soft, soft))
    except (ValueError, OSError) as exc:
        print(f"WARNING: could not set RLIMIT_AS: {exc}", file=sys.stderr)
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(WALL_CLOCK_SECONDS_PER_RUN)


# ---------------------------------------------------------------------------
# Number theory (self-contained, exact)
# ---------------------------------------------------------------------------
MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def miller_rabin(n: int) -> bool:
    if n < 2:
        return False
    for q in MR_BASES:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in MR_BASES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def sqrt_mod(a: int, p: int) -> Optional[int]:
    """Tonelli-Shanks; the smaller root, or None."""
    a %= p
    if a == 0:
        return 0
    if legendre(a, p) != 1:
        return None
    if p % 4 == 3:
        r = pow(a, (p + 1) // 4, p)
    else:
        q, s = p - 1, 0
        while q % 2 == 0:
            q //= 2
            s += 1
        z = 2
        while legendre(z, p) != -1:
            z += 1
        c = pow(z, q, p)
        r = pow(a, (q + 1) // 2, p)
        t = pow(a, q, p)
        m = s
        while t != 1:
            i, t2 = 0, t
            while t2 != 1:
                t2 = t2 * t2 % p
                i += 1
            b = pow(c, 1 << (m - i - 1), p)
            r = r * b % p
            c = b * b % p
            t = t * c % p
            m = i
    assert r * r % p == a
    return min(r, p - r)


def hint(*parts) -> int:
    return int(hashlib.sha256(":".join(str(x) for x in parts).encode()).hexdigest(), 16)


def poly_roots_mod(coeffs: Sequence[int], p: int) -> List[int]:
    """Roots in F_p of c2 X^2 + c1 X + c0 (coeffs = [c2, c1, c0]); handles degenerate leading terms."""
    c2, c1, c0 = [c % p for c in coeffs]
    if c2 == 0:
        if c1 == 0:
            return [] if c0 else ["all"]
        return [(-c0) * pow(c1, -1, p) % p]
    disc = (c1 * c1 - 4 * c2 * c0) % p
    r = sqrt_mod(disc, p)
    if r is None:
        return []
    inv = pow(2 * c2 % p, -1, p)
    return sorted({(-c1 + r) * inv % p, (-c1 - r) * inv % p})


def gcd_degree_mod(f: List[int], g: List[int], p: int) -> Optional[int]:
    """deg gcd(f, g) over F_p for univariate polynomials given as coefficient
    lists (highest degree first); None if both are zero (gcd = 0, infinite quotient)."""
    def strip(a):
        a = [c % p for c in a]
        while a and a[0] == 0:
            a.pop(0)
        return a

    def polymod(a, b):
        a = list(a)
        inv = pow(b[0], -1, p)
        while len(a) >= len(b):
            if a[0]:
                f_ = a[0] * inv % p
                for i, bc in enumerate(b):
                    a[i] = (a[i] - f_ * bc) % p
            a.pop(0)
        return strip(a)

    f, g = strip(f), strip(g)
    if not f and not g:
        return None
    while g:
        f, g = g, polymod(f, g)
    return len(f) - 1


# ---------------------------------------------------------------------------
# S_3 and the chained twin
# ---------------------------------------------------------------------------
def s3_generic_dict(a: int, b: int, p: int) -> Dict[Tuple[int, int, int], int]:
    """{(i, j, k): coeff} for S_3(x1, x2, x3) = (x1 - x2)^2 x3^2
    - 2((x1 + x2)(x1 x2 + a) + 2b) x3 + (x1 x2 - a)^2 - 4b(x1 + x2)
    (harness.semaev.s3_expr written out; that module re-evaluates certificates)."""
    d: Dict[Tuple[int, int, int], int] = {}

    def add(i, j, k, c):
        d[(i, j, k)] = (d.get((i, j, k), 0) + c) % p

    add(2, 0, 2, 1); add(1, 1, 2, -2); add(0, 2, 2, 1)
    add(2, 1, 1, -2); add(1, 2, 1, -2); add(1, 0, 1, -2 * a); add(0, 1, 1, -2 * a); add(0, 0, 1, -4 * b)
    add(2, 2, 0, 1); add(1, 1, 0, -2 * a); add(0, 0, 0, a * a)
    add(1, 0, 0, -4 * b); add(0, 1, 0, -4 * b)
    return {k: v for k, v in d.items() if v}


def s3_in_u(a: int, b: int, x1: int, x2: int, p: int) -> List[int]:
    """S_3(x1, x2, U) as [c2, c1, c0] in U (x1, x2 field elements)."""
    c2 = (x1 - x2) ** 2 % p
    c1 = (-2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)) % p
    c0 = ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p
    return [c2, c1, c0]


def chained_twin_system(a: int, b: int, xr: int):
    """system(ring, xs) -> [E1, E2] with E1 = S_3(x1, x2, u), E2 = S_3(u, x3, x_R);
    the ring's last free variable is u (digit_presentation's n_extra_free = 1)."""
    def system(ring: Ring, xs):
        u = {ring.free_var(ring.n_free - 1): 1}
        S = s3_generic_dict(a, b, ring.p)
        E1 = substitute(ring, S, [xs[0], xs[1], u])
        E2 = substitute(ring, S, [u, xs[2], ring.constant(xr)])
        return [E1, E2]
    return system


def build_twin(p: int, s: int, a: int, b: int, xr: int):
    pres = digit_presentation(p, 3, D_BASE, s, chained_twin_system(a, b, xr), n_extra_free=1)
    return pres.ring, list(pres.generators), pres


def digits(x: int, s: int) -> List[int]:
    return [(x >> i) & 1 for i in range(s)]


# ---------------------------------------------------------------------------
# Curves, planting, certificates
# ---------------------------------------------------------------------------
def ec_add(p: int, a: int, P, Q):
    """The executor's OWN affine addition (verification uses harness.toycurve)."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1 % p, -1, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def window_x_on_curve(p: int, a: int, b: int, B: int) -> List[int]:
    return [x for x in range(B) if legendre((x * x * x + a * x + b) % p, p) >= 0]


def draw_curve(p: int, seed: int, B: int) -> dict:
    """Random short-Weierstrass curve of generic j (A B != 0, disc != 0) with at
    least three on-curve x in [0, B); rejection counts reported."""
    rejections = {"singular": 0, "special_j": 0, "window": 0}
    attempt = 0
    while True:
        a = hint(EXP_ID, "curve", p, seed, "A", attempt) % p
        b = hint(EXP_ID, "curve", p, seed, "B", attempt) % p
        attempt += 1
        if (4 * a * a * a + 27 * b * b) % p == 0:
            rejections["singular"] += 1
            continue
        if a == 0 or b == 0:
            rejections["special_j"] += 1
            continue
        xs = window_x_on_curve(p, a, b, B)
        if len(xs) < 3:
            rejections["window"] += 1
            continue
        j = 1728 * 4 * a**3 * pow((4 * a**3 + 27 * b * b) % p, -1, p) % p
        return {"p": p, "a": a, "b": b, "j": j, "seed": seed, "attempts": attempt,
                "rejections": rejections, "window_x": xs, "B": B, "kind": "random"}


def draw_singular_cubic(p: int, seed: int, B: int) -> dict:
    """4A^3 + 27B^2 = 0 with A = -3t^2, B = 2t^3, t != 0: y^2 = (x - t)^2 (x + 2t),
    nodal, no group law.  Needs >= 3 window x (x != t) with x^3 + Ax + B a square."""
    rejections = {"t_zero": 0, "window": 0}
    attempt = 0
    while True:
        t = hint(EXP_ID, "singular", p, seed, "t", attempt) % p
        attempt += 1
        if t == 0:
            rejections["t_zero"] += 1
            continue
        a = (-3 * t * t) % p
        b = (2 * t * t * t) % p
        assert (4 * a * a * a + 27 * b * b) % p == 0
        xs = [x for x in window_x_on_curve(p, a, b, B) if x != t]
        if len(xs) < 3:
            rejections["window"] += 1
            continue
        return {"p": p, "a": a, "b": b, "t": t, "seed": seed, "attempts": attempt,
                "rejections": rejections, "window_x": xs, "B": B, "kind": "singular"}


def pick3(h: int, xs: List[int]) -> Tuple[int, int, int]:
    n = len(xs)
    i = h % n
    j = (h >> 64) % (n - 1)
    if j >= i:
        j += 1
    k = (h >> 128) % (n - 2)
    for taken in sorted((i, j)):
        if k >= taken:
            k += 1
    return xs[i], xs[j], xs[k]


def plant_target(curve: dict, tseed: int) -> dict:
    """Three distinct on-curve window x; u = x(P1 + P2), x_R = x(P1 + P2 + P3);
    certificate {kind: decomposition, target R, summands [P1, P2, P3]}."""
    p, a, b = curve["p"], curve["a"], curve["b"]
    xs = curve["window_x"]
    attempt = 0
    while True:
        h = hint(EXP_ID, "target", p, curve["seed"], tseed, attempt)
        attempt += 1
        x1, x2, x3 = pick3(h, xs)
        ys = []
        for idx, x in enumerate((x1, x2, x3)):
            y = sqrt_mod((x**3 + a * x + b) % p, p)
            if (h >> (192 + idx)) & 1:
                y = (-y) % p
            ys.append(y)
        P1, P2, P3 = (x1, ys[0]), (x2, ys[1]), (x3, ys[2])
        P12 = ec_add(p, a, P1, P2)          # affine: x1 != x2
        R = ec_add(p, a, P12, P3)
        if R is None:                       # P1 + P2 = -P3: no affine target; redraw
            continue
        cert = {"kind": "decomposition",
                "statement": {"target": [R[0], R[1]], "summands": [[x1, ys[0]], [x2, ys[1]], [x3, ys[2]]],
                              "curve": {"p": p, "a": a, "b": b}}}
        return {"target_seed": tseed, "attempts": attempt, "x1": x1, "x2": x2, "x3": x3,
                "P1": list(P1), "P2": list(P2), "P3": list(P3), "P12": list(P12),
                "u": P12[0], "R": list(R), "x_R": R[0], "certificate": cert}


def plant_root_target(cubic: dict, tseed: int) -> dict:
    """Non-curve arm: u a root of S_3(x1, x2, U), x_R a root of S_3(u, x3, X),
    with x1, x2, x3 distinct window x of the singular cubic (the formula's own roots)."""
    p, a, b = cubic["p"], cubic["a"], cubic["b"]
    xs = cubic["window_x"]
    attempt = 0
    while True:
        h = hint(EXP_ID, "roottarget", p, cubic["seed"], tseed, attempt)
        attempt += 1
        x1, x2, x3 = pick3(h, xs)
        ru = [r for r in poly_roots_mod(s3_in_u(a, b, x1, x2, p), p) if r != "all"]
        if not ru:
            continue
        u = ru[(h >> 192) % len(ru)]
        rx = [r for r in poly_roots_mod(s3_in_u(a, b, u, x3, p), p) if r != "all"]
        if not rx:
            continue
        x_R = rx[(h >> 200) % len(rx)]
        cert = {"kind": "s3_root_chain",
                "statement": {"x1": x1, "x2": x2, "x3": x3, "u": u, "x_R": x_R,
                              "cubic": {"p": p, "a": a, "b": b, "t": cubic["t"]}}}
        return {"target_seed": tseed, "attempts": attempt, "x1": x1, "x2": x2, "x3": x3,
                "u": u, "x_R": x_R, "certificate": cert}


def verify_certificate(cert: dict) -> bool:
    """INDEPENDENT re-verification: harness.toycurve arithmetic (through
    harness.semaev.verify_decomposition_certificate) for decompositions;
    harness.semaev.s3_eval for the S_3 root chain.  Neither shares code with the planting."""
    if cert["kind"] == "decomposition":
        return bool(verify_decomposition_certificate(cert))
    if cert["kind"] == "s3_root_chain":
        st = cert["statement"]
        c = st["cubic"]
        return (s3_eval(c["a"], c["b"], st["x1"], st["x2"], st["u"], c["p"]) == 0
                and s3_eval(c["a"], c["b"], st["u"], st["x3"], st["x_R"], c["p"]) == 0)
    return False


# ---------------------------------------------------------------------------
# Null arms
# ---------------------------------------------------------------------------
def topology_box(ring: Ring, s: int, blocks: Sequence[int], u_max: int, total_max: int):
    """All monomials with at most 2 digits from each listed block, u-exponent <= u_max,
    total degree <= total_max: the 'same variable set and multidegree' box of the S_3
    node (block multidegree (2, 2, 2), total degree 4)."""
    from itertools import combinations
    per_block = []
    for k in blocks:
        idxs = list(range(k * s, (k + 1) * s))
        masks = [0]
        for r in (1, 2):
            for c in combinations(idxs, r):
                m = 0
                for i in c:
                    m |= 1 << i
                masks.append(m)
        per_block.append(masks)
    out = []

    def rec(bi, mask, deg):
        if bi == len(per_block):
            for e in range(u_max + 1):
                if deg + e <= total_max:
                    ex = [0] * ring.n_free
                    ex[ring.n_free - 1] = e
                    out.append((mask, tuple(ex)))
            return
        for m in per_block[bi]:
            d = bin(m).count("1")
            if deg + d <= total_max:
                rec(bi + 1, mask | m, deg + d)
    rec(0, 0, 0)
    return out


def null_topology_system(ring: Ring, s: int, seed: int):
    """NULL-TOPOLOGY (IDEA-20260808-11b8c7 carried to F_p): E1 -> random polynomial on
    the box (blocks x1, x2; u <= 2; total <= 4), E2 -> random polynomial on the box
    (block x3; u <= 2; total <= 4); u shared; coefficients uniform in F_p (0 allowed)."""
    rng = random.Random(seed)
    box1 = topology_box(ring, s, [0, 1], 2, 4)
    box2 = topology_box(ring, s, [2], 2, 4)
    g1 = {m: c for m in box1 for c in [rng.randrange(0, ring.p)] if c}
    g2 = {m: c for m in box2 for c in [rng.randrange(0, ring.p)] if c}
    return [g1, g2], {"kind": "topology_matched", "seed": seed, "box_sizes": [len(box1), len(box2)],
                      "rule": "uniform coefficients in F_p (zero allowed) on every monomial with <= 2 digits per "
                              "S_3 argument block, u^e with e <= 2, total degree <= 4; u shared between E1 and E2"}


# ---------------------------------------------------------------------------
# Quotient dimension (cb8e46's product over digit cells) and sol(D)
# ---------------------------------------------------------------------------
def u_coefficient_polys(ring: Ring, f) -> List[dict]:
    """Split f = sum_e c_e(a) u^e into [c_0, c_1, c_2, ...] (digit-only polys)."""
    j = ring.n_free - 1
    maxe = max((m[1][j] for m in f), default=0)
    out = [dict() for _ in range(maxe + 1)]
    zero = tuple([0] * ring.n_free)
    for (mask, exps), c in f.items():
        out[exps[j]][(mask, zero)] = c
    return out


def quotient_dimension(ring: Ring, s: int, polys, use_blocks: Tuple[Sequence[int], Sequence[int]]) -> dict:
    """dim_{F_p} of F_p[a]/(a^2 - a)[u] / (E1, E2) = sum over digit points of
    deg gcd(E1(pt, u), E2(pt, u)) (the multilinear ring is the product of F_p over
    its 2^{3s} points and F_p[u] is a PID).  E1 depends on blocks (0, 1) and E2 on
    block 2, so 2^{2s} + 2^s evaluations and 2^{3s} gcds suffice."""
    p = ring.p
    n = 3 * s
    c1 = u_coefficient_polys(ring, polys[0])
    c2 = u_coefficient_polys(ring, polys[1])
    pts_all = [None]

    def restricted(coeffs, point_iter):
        table = {}
        for key, sq in point_iter:
            vals = [ring.evaluate(c, sq, [0] * ring.n_free) for c in coeffs]
            table[key] = list(reversed(vals))  # highest degree first
        return table

    def points_for(blocks):
        keys = []
        for v in range(1 << (len(blocks) * s)):
            sq = [0] * n
            for bi, k in enumerate(blocks):
                for i in range(s):
                    sq[k * s + i] = (v >> (bi * s + i)) & 1
            keys.append((v, sq))
        return keys
    t1 = restricted(c1, points_for(list(use_blocks[0])))
    t2 = restricted(c2, points_for(list(use_blocks[1])))
    total = 0
    infinite = 0
    hist: Dict[str, int] = {}
    for f in t1.values():
        for g in t2.values():
            dg = gcd_degree_mod(f, g, p)
            if dg is None:
                infinite += 1
            else:
                total += dg
                hist[str(dg)] = hist.get(str(dg), 0) + 1
    return {"dimension": None if infinite else total, "infinite_cells": infinite,
            "gcd_degree_histogram": dict(sorted(hist.items())), "digit_points": (1 << n)}


# ---------------------------------------------------------------------------
# Meter readings
# ---------------------------------------------------------------------------
def layer_record(layers) -> dict:
    return {str(l.degree): {
        "row_count": l.row_count, "zero_product_rows": l.zero_product_rows,
        "ncols_full": l.ncols_full, "ncols_top": l.ncols_top,
        "full_rank": l.full_rank, "top_rank": l.top_rank,
        "fall_dim": l.fall_dim, "syzygy_dim": l.syzygy_dim,
        "koszul_pairwise": l.koszul_pairwise, "pred_rank": l.pred_rank,
        "koszul_series": l.koszul_series, "deficit_series": l.deficit_series,
        "deficit_pairwise": l.deficit_pairwise, "top_deficit_series": l.top_deficit_series,
        "frobenius_factor": l.frobenius_factor, "nnz_total": l.nnz_total, "reduction_ops": l.reduction_ops,
        "preflight": l.preflight.as_dict(),
    } for l in layers}


def preflight_gate(ring: Ring, polys, degrees: Sequence[int]) -> dict:
    """CTRL-MEMORY-PREFLIGHT: counts by binomial arithmetic before any allocation;
    abort above 60,000 columns or 4 GiB dense-equivalent (rows x cols x 8 bytes)."""
    degs = [ring.degree(f) for f in polys]
    out = {}
    for D in degrees:
        pf = preflight(ring, degs, D, "cumulative")
        dense = pf.rows * pf.cols * 8
        out[str(D)] = {"rows": pf.rows, "cols": pf.cols, "cols_top": pf.cols_top,
                       "dense_equivalent_bytes": dense,
                       "aborted": bool(pf.cols > COLUMN_CAP or dense > DENSE_EQUIV_CAP_BYTES)}
    return out


def measure_twin(ring: Ring, polys, degrees: Sequence[int], quotient_dim: Optional[int]) -> dict:
    """The contract's deficit at each D: deficit(D) = rows - rank - koszul(D) under the
    cumulative convention (LayerResult.deficit_pairwise), plus the meter's other readings."""
    gate = preflight_gate(ring, polys, degrees)
    aborted = [D for D in degrees if gate[str(D)]["aborted"]]
    run_degrees = [D for D in degrees if D not in aborted]
    out = {"preflight": gate, "preflight_aborted_degrees": aborted,
           "generator_degrees": [ring.degree(f) for f in polys],
           "generator_term_counts": [len(f) for f in polys],
           "generator_degree_histograms": [ring.degree_histogram(f) for f in polys]}
    if not run_degrees:
        return out
    layers = analyze_degrees(ring, polys, min(run_degrees), max(run_degrees), convention="cumulative")
    layers = [l for l in layers if l.degree in run_degrees]
    out["cumulative"] = layer_record(layers)
    out["deficit"] = {str(l.degree): l.deficit_pairwise for l in layers}      # THE frozen quantity
    out["deficit_vector"] = [l.deficit_pairwise for l in layers]
    out["rows"] = [l.row_count for l in layers]
    out["ncols"] = [l.ncols_full for l in layers]
    out["rank"] = [l.full_rank for l in layers]
    out["koszul"] = [l.koszul_pairwise for l in layers]
    out["deficit_series"] = [l.deficit_series for l in layers]
    if all(l.pred_rank is not None for l in layers):
        prof = deficit_profile(layers)
        out["deficit_graded_series"] = list(prof.deficit_graded)
    out["quotient_dimension"] = quotient_dim
    out["sol"] = {str(l.degree): (None if quotient_dim is None else bool(l.full_rank >= l.ncols_full - quotient_dim))
                  for l in layers}
    return out


# ---------------------------------------------------------------------------
# Stage 3 cell: one (s, p) over all curves, targets, degrees and arms
# ---------------------------------------------------------------------------
def cell_run(s: int, p: int, label: str, log: io.StringIO) -> runner.RunResult:
    t_start = time.monotonic()
    B = 1 << s
    degrees = S_LIMITED.get(s, DEGREES_MAIN)
    target_seeds = TARGET_SEEDS_DECIDING if s == 3 else TARGET_SEEDS_DEFAULT
    draws: List[dict] = []
    curves: List[dict] = []
    cubics: List[dict] = []
    stopped = None
    templates = None   # (ring, polys) of curve 4101 / target 1: null templates
    try:
        for cs in CURVE_SEEDS:
            curve = draw_curve(p, cs, B)
            curves.append(curve)
            print(f"[{label}] curve seed {cs}: a={curve['a']} b={curve['b']} j={curve['j']} window_x={curve['window_x']} "
                  f"rejections={curve['rejections']}", file=log)
            for ts in target_seeds:
                tgt = plant_target(curve, ts)
                ring, polys, _ = build_twin(p, s, curve["a"], curve["b"], tgt["x_R"])
                point = digits(tgt["x1"], s) + digits(tgt["x2"], s) + digits(tgt["x3"], s)
                vanish = all(ring.evaluate(f, point, [tgt["u"]]) == 0 for f in polys)
                cert_ok = verify_certificate(tgt["certificate"])
                qd = quotient_dimension(ring, s, polys, ([0, 1], [2]))
                rec = {"arm": "semaev", "curve_seed": cs, "target_seed": ts, "s": s, "p": p,
                       "x1": tgt["x1"], "x2": tgt["x2"], "x3": tgt["x3"], "u": tgt["u"], "x_R": tgt["x_R"],
                       "target_attempts": tgt["attempts"], "planted_digits": point,
                       "generators_vanish_at_planted_point": vanish,
                       "certificate": tgt["certificate"], "certificate_verified": cert_ok,
                       "quotient": qd, "valid": bool(cert_ok and vanish)}
                if not rec["valid"]:
                    rec["invalid_reason"] = "certificate failed independent re-verification or E1/E2 do not vanish at the planted point"
                rec.update(measure_twin(ring, polys, degrees, qd["dimension"]))
                draws.append(rec)
                print(f"[{label}]   target {ts}: x=({tgt['x1']},{tgt['x2']},{tgt['x3']}) u={tgt['u']} x_R={tgt['x_R']} "
                      f"cert={cert_ok} vanish={vanish} |Z|={qd['dimension']} SEM deficit{degrees}={rec.get('deficit_vector')} "
                      f"rows={rec.get('rows')} rank={rec.get('rank')} | {time.monotonic() - t_start:.1f}s", file=log)
                if templates is None:
                    templates = (ring, polys, cs, ts)
        # null arms: 5 frozen seeds per (cell, arm), templates of curve 4101 / target 1
        ring, polys, tcs, tts = templates
        for ns in NULL_SEEDS:
            npolys, meta = support_matched_system(ring, polys, ns)
            qd = quotient_dimension(ring, s, npolys, ([0, 1], [2]))
            rec = {"arm": "null_support", "s": s, "p": p, "null_seed": ns, "template_curve_seed": tcs,
                   "template_target_seed": tts, "null_meta": meta.as_dict(),
                   "support_sizes": [len(q) for q in npolys], "quotient": qd, "valid": True}
            rec.update(measure_twin(ring, npolys, degrees, qd["dimension"]))
            draws.append(rec)
            print(f"[{label}]   NULL-SUPPORT seed {ns}: degrees={rec['generator_degrees']} |Z|={qd['dimension']} "
                  f"deficit={rec.get('deficit_vector')} | {time.monotonic() - t_start:.1f}s", file=log)
        for ns in NULL_SEEDS:
            npolys, meta = null_topology_system(ring, s, ns)
            qd = quotient_dimension(ring, s, npolys, ([0, 1], [2]))
            rec = {"arm": "null_topology", "s": s, "p": p, "null_seed": ns, "null_meta": meta,
                   "support_sizes": [len(q) for q in npolys], "quotient": qd, "valid": True}
            rec.update(measure_twin(ring, npolys, degrees, qd["dimension"]))
            draws.append(rec)
            print(f"[{label}]   NULL-TOPOLOGY seed {ns}: degrees={rec['generator_degrees']} |Z|={qd['dimension']} "
                  f"deficit={rec.get('deficit_vector')} | {time.monotonic() - t_start:.1f}s", file=log)
        # nearby non-curve cubic: seeds 51, 53, 59; planted via the formula's own roots
        for cseed in NONCURVE_SEEDS:
            cubic = draw_singular_cubic(p, cseed, B)
            cubics.append(cubic)
            tgt = plant_root_target(cubic, TARGET_SEEDS_DEFAULT[0])
            ring2, polys2, _ = build_twin(p, s, cubic["a"], cubic["b"], tgt["x_R"])
            point = digits(tgt["x1"], s) + digits(tgt["x2"], s) + digits(tgt["x3"], s)
            vanish = all(ring2.evaluate(f, point, [tgt["u"]]) == 0 for f in polys2)
            cert_ok = verify_certificate(tgt["certificate"])
            qd = quotient_dimension(ring2, s, polys2, ([0, 1], [2]))
            rec = {"arm": "noncurve_cubic", "cubic_seed": cseed, "target_seed": tgt["target_seed"], "s": s, "p": p,
                   "t": cubic["t"], "x1": tgt["x1"], "x2": tgt["x2"], "x3": tgt["x3"], "u": tgt["u"], "x_R": tgt["x_R"],
                   "target_attempts": tgt["attempts"], "planted_digits": point,
                   "generators_vanish_at_planted_point": vanish,
                   "certificate": tgt["certificate"], "certificate_verified": cert_ok,
                   "quotient": qd, "valid": bool(cert_ok and vanish)}
            if not rec["valid"]:
                rec["invalid_reason"] = "S_3 root-chain certificate failed independent re-evaluation or generators do not vanish at the planted point"
            rec.update(measure_twin(ring2, polys2, degrees, qd["dimension"]))
            draws.append(rec)
            print(f"[{label}]   NON-CURVE cubic seed {cseed}: t={cubic['t']} x=({tgt['x1']},{tgt['x2']},{tgt['x3']}) u={tgt['u']} "
                  f"x_R={tgt['x_R']} cert={cert_ok} vanish={vanish} |Z|={qd['dimension']} deficit={rec.get('deficit_vector')} "
                  f"| {time.monotonic() - t_start:.1f}s", file=log)
    except RunBudgetExceeded as exc:
        stopped = str(exc)
        print(f"[{label}] STOPPED: {stopped}", file=log)
    except PreflightAbort as exc:
        stopped = f"pre-flight abort: {exc}"
        print(f"[{label}] STOPPED: {stopped}", file=log)
    signal.alarm(0)

    arms = sorted({d["arm"] for d in draws})
    cert_total = sum(1 for d in draws if "certificate_verified" in d)
    cert_fail = sum(1 for d in draws if "certificate_verified" in d and not d["certificate_verified"])

    def vec_hist(arm):
        return _hist(str(d.get("deficit_vector")) for d in draws if d["arm"] == arm)
    metrics = {
        "s": s, "p": p, "degrees": degrees, "window": B, "draw_count": len(draws),
        "valid_draws": sum(1 for d in draws if d.get("valid")),
        "arms": arms, "draws_per_arm": {a: sum(1 for d in draws if d["arm"] == a) for a in arms},
        "planted_certificates_total": cert_total, "planted_certificates_failed": cert_fail,
        "preflight_aborted": sorted({(d["arm"], D) for d in draws for D in d.get("preflight_aborted_degrees", [])}),
        "stopped": stopped,
        "deficit_vector_histogram": {a: vec_hist(a) for a in arms},
        "max_abs_deficit": {a: max((abs(v) for d in draws if d["arm"] == a for v in d.get("deficit_vector", [])), default=None) for a in arms},
        "null_generator_degree_histogram": {a: _hist(str(d["generator_degrees"]) for d in draws if d["arm"] == a)
                                            for a in arms if a.startswith("null")},
        "quotient_dimension_histogram": {a: _hist(d["quotient"]["dimension"] for d in draws if d["arm"] == a) for a in arms},
        "sol_histogram": {a: _hist(str(d.get("sol")) for d in draws if d["arm"] == a) for a in arms},
        "curve_rejections": {str(c["seed"]): c["rejections"] for c in curves},
        "cubic_rejections": {str(c["seed"]): c["rejections"] for c in cubics},
        "template_for_nulls": {"curve_seed": templates[2], "target_seed": templates[3]} if templates else None,
    }
    valid = stopped is None and cert_fail == 0
    return runner.RunResult(
        run_suffix=label, curve_id=f"cell-s{s}-p{p}-6-random-curves", seed=CURVE_SEEDS[0],
        parameters=common_parameters(stage="stage-3-separating-cells" if s != 4 else "stage-3-separating-cells+stage-4-p-ladder",
                                     extra={"s": s, "p": p, "prime_check": {"p": p, "miller_rabin_12_bases": miller_rabin(p)},
                                            "degrees": degrees, "window": B, "curve_seeds": CURVE_SEEDS,
                                            "target_seeds": target_seeds, "null_seeds": NULL_SEEDS,
                                            "noncurve_seeds": NONCURVE_SEEDS,
                                            "expected_counts_from_contract": {"rows_D8": {"3": 886, "4": 2372, "5": 5310},
                                                                              "cols_D8": {"3": 2304, "4": 12381, "5": 56751},
                                                                              "cols_s6_D6": 49024}}),
        metrics=metrics,
        certificate={"kind": "none",
                     "note": ("No solve is claimed. Every planted target carries a per-draw certificate in raw.draws[*] "
                              "(decomposition R = P1 + P2 + P3 re-verified by harness.semaev / harness.toycurve; S_3 root "
                              "chain re-evaluated by harness.semaev.s3_eval); failures are counted in metrics.")},
        valid=valid,
        invalid_reason=(stopped if stopped else ("planted certificate failed" if cert_fail else None)),
        stdout=log.getvalue(),
        raw={"curves": curves, "singular_cubics": cubics, "draws": draws, "meter_selftest": METER_SELFTEST,
             "frozen_prediction_copy": FROZEN},
    )


def _hist(values) -> dict:
    h: Dict[str, int] = {}
    for v in values:
        h[str(v)] = h.get(str(v), 0) + 1
    return dict(sorted(h.items()))


# ---------------------------------------------------------------------------
# Stage 1: binary calibration (CTRL-BINARY-CALIBRATION) + Stage 0 mechanical checks
# ---------------------------------------------------------------------------
def stage0_mechanical_checks() -> dict:
    """Mechanical confirmation of the hand derivation in stage0-derivation.md, at
    s = 3 and p = 4099 (symbolic in the digit ring, curve constants generic)."""
    out = {}
    for p in (4099, 65537):
        ring, polys, _ = build_twin(p, 3, 941, 428, 3690)
        E1, E2 = polys
        top1, top2 = ring.top_form(E1), ring.top_form(E2)
        j = ring.n_free - 1
        ufree_top1 = {m: c for m, c in top1.items() if m[1][j] == 0}
        # x1^2 x2^2's multilinear image: a_{1,i} a_{1,i'} a_{2,k} a_{2,k'} monomials, u-free
        four_digit_two_two = [m for m in ufree_top1 if bin(m[0] & 0b111).count("1") == 2 and bin((m[0] >> 3) & 0b111).count("1") == 2]
        e2_all_u2 = all(m[1][j] == 2 for m in top2)
        e2_digits_block3 = all((m[0] & 0b111111) == 0 for m in top2)
        # f = a1 + a2: f^2 - f = 2 a1 a2
        f = ring.add({ring.sq_var(0): 1}, {ring.sq_var(1): 1})
        f2mf = ring.sub(ring.mul(f, f), f)
        out[str(p)] = {
            "deg_E1": ring.degree(E1), "deg_E2": ring.degree(E2),
            "E1_top_form_has_u_free_monomials": bool(ufree_top1),
            "E1_top_form_u_free_(2,2)-digit_monomials": len(four_digit_two_two),
            "E2_top_form_all_u^2": e2_all_u2, "E2_top_form_digits_only_block3": e2_digits_block3,
            "top_forms_share_no_monomial": not (set(top1) & set(top2)),
            "subset_sum_degree_4_for_all_nonzero_(c1,c2)": bool(ufree_top1) and e2_all_u2,
            "f=a1+a2: f^2 - f": ring.to_string(f2mf), "f^2_equals_f": f2mf == {},
        }
    return out


def calibration_run(log: io.StringIO) -> runner.RunResult:
    with open(FIXTURE_JSON, "rb") as fh:
        raw = fh.read()
    fixture_sha = hashlib.sha256(raw).hexdigest()
    data = json.loads(raw)
    ring = Ring(2, data["nb"])
    polys = [{(sum(1 << v for v in m), ()): 1 for m in f} for f in data["generators"]]
    degs = [ring.degree(f) for f in polys]
    print(f"[calib] fixture sha256 {fixture_sha} (expected {FIXTURE_SHA256}); n={data['n']} k={data['k']} nb={data['nb']} "
          f"generators={len(polys)} degrees={_hist(degs)} system_hash={data['system_hash']} "
          f"matches_archived={data['matches_archived_system_hash']}", file=log)
    stopped = None
    result: dict = {"fixture_sha256": fixture_sha, "fixture_sha256_expected": FIXTURE_SHA256,
                    "fixture_meta": {k: data[k] for k in ("n", "k", "nb", "t", "ti", "seed", "rng_seed", "n_candidates",
                                                            "system_hash", "archived_system_hash",
                                                            "matches_archived_system_hash", "root_order", "R_X")}}
    try:
        # (a) the calibration arm: cumulative convention, Koszul + Frobenius count, D = 2..5
        layers = analyze_degrees(ring, polys, 2, 5, convention="cumulative")
        prof = deficit_profile(layers)
        result["semaev_arm"] = {"cumulative": layer_record(layers), "profile": prof.as_dict()}
        print(f"[calib] SEM arm D=2..5: rows={prof.rows} rank={prof.rank} pred={prof.pred} koszul_pairwise={prof.koszul_pairwise} "
              f"koszul_series={prof.koszul_series} deficit_cumulative={prof.deficit_cumulative} deficit_graded={prof.deficit_graded} "
              f"deficit_pairwise={prof.deficit_pairwise}", file=log)
        # (b) KN-FIND-006's null (EXP-DREG-001 boolean_null, RNG state continued after the builder's sample)
        rng = random.Random(data["rng_seed"])
        rng.sample(list(range(data["n_candidates"])), 3)
        null = dreg_boolean_null(ring, polys, rng)
        nl = analyze_degrees(ring, null, 2, 5, convention="cumulative")
        nprof = deficit_profile(nl)
        result["null_dreg_boolean"] = {"cumulative": layer_record(nl), "profile": nprof.as_dict(),
                                       "generator_degrees": [ring.degree(f) for f in null]}
        print(f"[calib] DREG boolean_null D=2..5: deficit_cumulative={nprof.deficit_cumulative} deficit_graded={nprof.deficit_graded}", file=log)
        # (c) histogram-matched nulls at the five frozen seeds (D = 2..4)
        result["null_histogram_matched"] = {}
        for seed in NULL_SEEDS:
            hm, meta = histogram_matched_system(ring, polys, seed)
            hl = analyze_degrees(ring, hm, 2, 4, convention="cumulative")
            hp = deficit_profile(hl)
            result["null_histogram_matched"][str(seed)] = {"cumulative": layer_record(hl), "profile": hp.as_dict(),
                                                           "meta": meta.as_dict(), "generator_degrees": [ring.degree(f) for f in hm]}
            print(f"[calib] histogram-matched null seed {seed} D=2..4: deficit_cumulative={hp.deficit_cumulative} deficit_graded={hp.deficit_graded}", file=log)
        # (d) identical-support null at p = 2 is the identity (flagged, recorded, not used)
        sm, smeta = support_matched_system(ring, polys, NULL_SEEDS[0])
        result["support_matched_identity_at_p2"] = {"meta": smeta.as_dict(), "equals_input": sm == polys}
        # (e) mixed-mode code path on the same system: one UNUSED free variable u appended,
        #     Frobenius count forced on (every generator is u-free and Boolean).  Derived
        #     expectation (not a KN-FIND-006 integer): the u^k row blocks are independent,
        #     so deficit_mixed(D) = sum_{k>=0} deficit_squarefree(D - k) = 1 at D = 3, 33 at D = 4.
        mring = Ring(2, data["nb"], 1)
        mpolys = [{(m[0], (0,)): 1 for m in f} for f in polys]
        ml = analyze_degrees(mring, mpolys, 2, 4, convention="cumulative", frobenius=True)
        result["mixed_mode_code_path"] = {"cumulative": layer_record(ml),
                                          "deficit_pairwise": [l.deficit_pairwise for l in ml],
                                          "derived_expectation_deficit_pairwise": [0, 1, 33],
                                          "derivation": "rows u^k m' f with distinct k occupy disjoint column sets; the k-block "
                                                        "at D is the squarefree cumulative layer at D - k, and the Koszul/Frobenius "
                                                        "counts decompose the same way"}
        print(f"[calib] mixed-mode code path (unused u, Frobenius on) D=2..4: deficit_pairwise={[l.deficit_pairwise for l in ml]} "
              f"(derived expectation [0, 1, 33])", file=log)
        result["stage0_mechanical_checks"] = stage0_mechanical_checks()
        print(f"[calib] stage 0 mechanical checks: {json.dumps(result['stage0_mechanical_checks'])}", file=log)
    except RunBudgetExceeded as exc:
        stopped = str(exc)
        print(f"[calib] STOPPED: {stopped}", file=log)
    signal.alarm(0)

    sem = result.get("semaev_arm", {}).get("profile", {})
    graded = sem.get("deficit_graded", [])
    cum = sem.get("deficit_cumulative", [])
    nulls_zero = (result.get("null_dreg_boolean", {}).get("profile", {}).get("deficit_cumulative", [1])[:3] == [0, 0, 0]
                  and all(v["profile"]["deficit_cumulative"] == [0, 0, 0] for v in result.get("null_histogram_matched", {}).values()))
    calib_ok = (len(graded) >= 3 and graded[1] == 1 and graded[2] == 31 and cum[2] == 32 and nulls_zero
                and fixture_sha == FIXTURE_SHA256)
    metrics = {
        "fixture_sha256_matches": fixture_sha == FIXTURE_SHA256,
        "deficit_graded_D2_D3_D4_D5": graded, "deficit_cumulative_D2_D3_D4_D5": cum,
        "deficit_pairwise_D2_D3_D4_D5": sem.get("deficit_pairwise", []),
        "koszul_pairwise_D2_D3_D4_D5": sem.get("koszul_pairwise", []),
        "rows_D2_D3_D4_D5": sem.get("rows", []), "rank_D2_D3_D4_D5": sem.get("rank", []), "pred_D2_D3_D4_D5": sem.get("pred", []),
        "frozen_expected": {"deficit_graded_D3": 1, "deficit_graded_D4": 31, "cumulative_D4_8k": 32, "null": 0},
        "deficit_D3_equals_1": bool(len(graded) >= 2 and graded[1] == 1),
        "deficit_D4_equals_31": bool(len(graded) >= 3 and graded[2] == 31),
        "cumulative_D4_equals_8k": bool(len(cum) >= 3 and cum[2] == 32),
        "null_deficits_all_zero": nulls_zero,
        "calibration_reproduced": calib_ok,
        "mixed_mode_deficit_pairwise_D2_D3_D4": result.get("mixed_mode_code_path", {}).get("deficit_pairwise"),
        "mixed_mode_matches_derived_expectation": result.get("mixed_mode_code_path", {}).get("deficit_pairwise") == [0, 1, 33],
        "stage0_checks_all_pass": all(
            v["E1_top_form_has_u_free_monomials"] and v["E2_top_form_all_u^2"] and not v["f^2_equals_f"] and v["deg_E1"] == 4 and v["deg_E2"] == 4
            for v in result.get("stage0_mechanical_checks", {}).values()) if result.get("stage0_mechanical_checks") else None,
        "stopped": stopped,
    }
    return runner.RunResult(
        run_suffix="calib-gf2-n12", curve_id="GF(2^12) y^2+xy=x^3+x^2+alpha (EXP-DREG-001 fixture, n=12, k=4)", seed=data["seed"],
        parameters=common_parameters(stage="stage-1-instrument-calibration",
                                     extra={"p": 2, "ring": "squarefree, 24 Boolean variables (the fixture's own ring)",
                                            "fixture": os.path.relpath(FIXTURE_JSON, REPO), "fixture_sha256": fixture_sha,
                                            "degrees": [2, 5], "null_seeds": NULL_SEEDS,
                                            "koszul_count": "pairwise Koszul + Frobenius f^2 = f (p = 2, squarefree; koszul.frobenius_count)",
                                            "series_factor": "Boolean 1/(1 + z^d) (default_frobenius True at p = 2 squarefree)"}),
        metrics=metrics,
        certificate={"kind": "none", "note": "Instrument calibration; no solve is claimed."},
        valid=stopped is None and calib_ok,
        invalid_reason=stopped if stopped else (None if calib_ok else "calibration miss (instrument finding): see metrics"),
        stdout=log.getvalue(),
        raw={"result": result, "meter_selftest": METER_SELFTEST, "frozen_prediction_copy": FROZEN},
    )


# ---------------------------------------------------------------------------
# Stage 2: s = 1 slice against cb8e46's chained J (CTRL-S1-SLICE)
# ---------------------------------------------------------------------------
def s1_run(log: io.StringIO) -> runner.RunResult:
    stopped = None
    cells = []
    identity_all = True
    try:
        for p in PRIMES:
            for Bv in S1_BASES:
                curve = draw_curve(p, CURVE_SEEDS[0], Bv)
                tgt = plant_target(curve, TARGET_SEEDS_DEFAULT[0])
                a, b, xr = curve["a"], curve["b"], tgt["x_R"]
                # the twin at s = 1, d = B: digit_presentation (free digit a_{k,0}, membership prod_{j<B}(a - j), u appended)
                twin = digit_presentation(p, 3, Bv, 1, chained_twin_system(a, b, xr), n_extra_free=1)
                # cb8e46's chained J via the meter's direct presentation: x_k free, f_V(x_k) = prod_{v in [0,B)} (x_k - v), u appended
                J = direct_presentation(p, 3, Bv, chained_twin_system(a, b, xr), n_extra_free=1)
                same_ring = (twin.ring == J.ring)
                per_gen = [twin.generators[i] == J.generators[i] for i in range(len(J.generators))]
                identical = same_ring and len(twin.generators) == len(J.generators) and all(per_gen)
                identity_all = identity_all and identical
                names = {"twin": list(twin.variable_names), "J": list(J.variable_names)}
                ring = twin.ring
                # graded ranks as a frozen fixture, both conventions, D = 4..10
                cum = analyze_degrees(ring, list(twin.generators), 4, 10, convention="cumulative")
                per = analyze_degrees(ring, list(twin.generators), 4, 10, convention="per_layer")
                point = [tgt["x1"], tgt["x2"], tgt["x3"], tgt["u"]]
                vanish = all(ring.evaluate(f, [], point) == 0 for f in twin.generators)
                cert_ok = verify_certificate(tgt["certificate"])
                cells.append({"p": p, "B": Bv, "curve": curve, "target": tgt, "certificate_verified": cert_ok,
                              "generators_vanish_at_planted_point": vanish,
                              "symbolic_identity": identical, "same_ring": same_ring, "per_generator_equal": per_gen,
                              "generator_order": ["S_3(x1,x2,u)", "S_3(u,x3,xR)", "fV(x1)", "fV(x2)", "fV(x3)"],
                              "variable_names": names,
                              "generator_degrees": [ring.degree(f) for f in twin.generators],
                              "generator_term_counts": [len(f) for f in twin.generators],
                              "generators_rendered": [ring.to_string(f, free_names=["x1", "x2", "x3", "u"]) for f in twin.generators],
                              "cumulative": layer_record(cum), "per_layer": layer_record(per),
                              "cumulative_deficit_pairwise": [l.deficit_pairwise for l in cum],
                              "cumulative_rank": [l.full_rank for l in cum], "cumulative_rows": [l.row_count for l in cum],
                              "per_layer_rank": [l.full_rank for l in per], "per_layer_top_rank": [l.top_rank for l in per],
                              "per_layer_fall_dim": [l.fall_dim for l in per]})
                print(f"[s1] p={p} B={Bv}: curve a={a} b={b} window_x={curve['window_x']} target x=({tgt['x1']},{tgt['x2']},{tgt['x3']}) "
                      f"u={tgt['u']} x_R={xr} cert={cert_ok} vanish={vanish} | identity={identical} per_gen={per_gen} | "
                      f"cumulative rank D=4..10 {[l.full_rank for l in cum]} deficit_pairwise {[l.deficit_pairwise for l in cum]} | "
                      f"per-layer rank {[l.full_rank for l in per]} top {[l.top_rank for l in per]}", file=log)
    except RunBudgetExceeded as exc:
        stopped = str(exc)
        print(f"[s1] STOPPED: {stopped}", file=log)
    signal.alarm(0)
    cert_fail = sum(1 for c in cells if not c["certificate_verified"])
    metrics = {"cells": [(c["p"], c["B"]) for c in cells], "symbolic_identity_all_cells": identity_all,
               "identity_per_cell": {f"p{c['p']}-B{c['B']}": c["symbolic_identity"] for c in cells},
               "cumulative_deficit_pairwise_D4_D10": {f"p{c['p']}-B{c['B']}": c["cumulative_deficit_pairwise"] for c in cells},
               "cumulative_rank_D4_D10": {f"p{c['p']}-B{c['B']}": c["cumulative_rank"] for c in cells},
               "per_layer_rank_D4_D10": {f"p{c['p']}-B{c['B']}": c["per_layer_rank"] for c in cells},
               "planted_certificates_failed": cert_fail, "stopped": stopped}
    return runner.RunResult(
        run_suffix="s1-slice", curve_id="s1-slice-3-primes-2-bases-curve-seed-4101", seed=CURVE_SEEDS[0],
        parameters=common_parameters(stage="stage-2-s1-slice",
                                     extra={"s": 1, "bases": S1_BASES, "primes": PRIMES, "curve_seed": CURVE_SEEDS[0],
                                            "target_seed": TARGET_SEEDS_DEFAULT[0], "degrees": [4, 10],
                                            "ring": "ordinary mode: free x1, x2, x3 (= a_{k,0}) and u; membership generators explicit"}),
        metrics=metrics,
        certificate={"kind": "none", "note": "Baseline slice; no solve is claimed; per-cell planted certificates in raw.cells[*].target.certificate re-verified independently."},
        valid=stopped is None and identity_all and cert_fail == 0,
        invalid_reason=stopped if stopped else (None if (identity_all and cert_fail == 0) else "s = 1 slice not symbolically identical to cb8e46's J, or certificate failure"),
        stdout=log.getvalue(),
        raw={"cells": cells, "meter_selftest": METER_SELFTEST, "frozen_prediction_copy": FROZEN},
    )


# ---------------------------------------------------------------------------
# Manifest lineage helpers
# ---------------------------------------------------------------------------
def meter_hashes() -> dict:
    out = {}
    for rel in METER_FILES:
        with open(os.path.join(REPO, rel), "rb") as fh:
            out[rel] = hashlib.sha256(fh.read()).hexdigest()
    return out


def meter_selftest() -> dict:
    t0 = time.monotonic()
    proc = subprocess.run([sys.executable, "-m", "pytest", "tests/test_macaulay_fp.py", "-q", "-p", "no:cacheprovider"],
                          cwd=REPO, capture_output=True, text=True)
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    return {"command": "python3 -m pytest tests/test_macaulay_fp.py -q -p no:cacheprovider",
            "returncode": proc.returncode, "summary_line": tail, "seconds": round(time.monotonic() - t0, 3)}


METER_SELFTEST: dict = {}


def adapter_inference_block() -> dict:
    try:
        from orchestration.adapter.manifest import block_from_env
        return block_from_env()
    except Exception as exc:  # pragma: no cover
        return {"adapter_error": f"{type(exc).__name__}: {exc}"}


def common_parameters(stage: str, extra: dict) -> dict:
    return {
        "experiment": EXP_ID, "hypothesis": "H-PFDR-9aadc0", "handoff": "TASK-20260903-5b46a6",
        "stage": stage, "shape": {"m": 3, "tree": "chained t = 3: E1 = S_3(x1, x2, u), E2 = S_3(u, x3, x_R); u free; x_R constant",
                                  "d": D_BASE},
        "meter": {"package": "harness/macaulay_fp", "snapshot_commit": METER_COMMIT,
                  "per_file_sha256": meter_hashes(), "selftest_in_this_lineage": METER_SELFTEST},
        "budget": {"wall_clock_seconds_per_run": WALL_CLOCK_SECONDS_PER_RUN, "maximum_memory_gb": MAX_MEMORY_GB,
                   "maximum_workers": 1, "maximum_runs": 60, "column_cap": COLUMN_CAP,
                   "dense_equivalent_cap_bytes": DENSE_EQUIV_CAP_BYTES},
        "deficit_convention": {
            "definition": "deficit(D) = rows(D) - rank(Mac_D) - koszul(D)",
            "multipliers": "cumulative: all monomials m with deg m <= D - deg f_i (multilinear in the digits, free in u); zero-product rows dropped and counted",
            "koszul": "explicit pairwise Koszul count (koszul.koszul_pair_count; = 1 at D = 8 for two quartics, 0 below) plus the Frobenius count at p = 2 in the pure squarefree ring only",
            "meter_field": "LayerResult.deficit_pairwise under convention='cumulative'",
            "identical_across_arms": True,
            "identical_to_calibration_arm": "yes: the same LayerResult.deficit_pairwise / deficit_profile under convention='cumulative'; at p = 2 the count includes Frobenius, which is absent for p > 2 and in mixed mode (S2)",
            "secondary_readings_recorded": ["deficit_series = pred - rank (series with the naive factor (1 - z^d) at p > 2)",
                                            "deficit_graded_series (per-degree increments)", "fall_dim", "top_rank", "sol(D) covariate"],
        },
        "null_arms": {
            "null_support": "support_matched_system: identical monomial support of E1 and E2, coefficients uniform in [1, p-1]; random.Random(seed) with the frozen seed verbatim; 5 seeds per (cell, arm) on the templates of curve 4101 / target 1",
            "null_topology": "random polynomials on the monomial box of each node (<= 2 digits per S_3 argument block, u^e with e <= 2, total degree <= 4), coefficients uniform in F_p (0 allowed), u shared; random.Random(seed) with the frozen seed verbatim; 5 seeds per (cell, arm)",
        },
        "curve_and_target_rules": {
            "curve": "A, B = sha256(EXP:curve:p:seed:A|B:attempt) mod p; reject disc = 0, A = 0 or B = 0 (j in {0, 1728}), or fewer than 3 on-curve x in [0, 2^s)",
            "target": "x1, x2, x3 distinct on-curve window x by sha256(EXP:target:p:curve_seed:t:attempt); y-signs from hash bits; P12 = P1 + P2, R = P12 + P3 by the executor's own affine addition (redraw if R = O); u = x(P12), x_R = x(R); certificate {decomposition, R, [P1, P2, P3]} re-verified by harness.semaev.verify_decomposition_certificate (harness.toycurve arithmetic)",
            "noncurve": "A = -3t^2, B = 2t^3 (4A^3 + 27B^2 = 0), t = sha256(EXP:singular:p:seed:t:attempt) mod p != 0; x1, x2, x3 distinct window x with square rhs and x != t; u a root of S_3(x1, x2, U), x_R a root of S_3(u, x3, X); re-verified by harness.semaev.s3_eval",
            "quotient_dimension": "sum over the 2^{3s} digit points of deg gcd(E1(pt, u), E2(pt, u)) over F_p (cb8e46: product over cells of F_p[u]/(d_c)); sol(D) = [rank(Mac_D) >= ncols(D) - dim] (IDEA-20260806-7ea402), a covariate only",
        },
        "executor_session_inference": {
            "requested_policy": "executor-implementation", "requested_reasoning_effort": "medium",
            "adapter_resolution": "python3 -m orchestration.adapter resolve --role executor -> anthropic:claude-sonnet-5 (effort=medium)",
            "runtime_reported_model": "claude-fable-5-1", "model_verified": False,
            "fallback_used": "unknown (adapter binding and runtime-reported identifier differ; cannot be verified from inside the session)",
            "degraded": False, "independent_session": True,
            "adapter_block_from_env": adapter_inference_block(),
            "note": "The run itself is deterministic code with no model in its loop (see run.inference, which the wrapper writes from a harness default: see implementation.md D9); this block records the executor SESSION's policy as the handoff requires.",
        },
        **extra,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["calib", "s1", "cell"])
    ap.add_argument("--s", type=int, default=None)
    ap.add_argument("--p", type=int, default=None)
    ap.add_argument("--suffix", default=None, help="override run suffix (re-runs after an infrastructure stop only)")
    ap.add_argument("--out-root", default=None, help="smoke tests only: write the run package elsewhere")
    args = ap.parse_args()
    global METER_SELFTEST
    METER_SELFTEST = meter_selftest()
    if METER_SELFTEST["returncode"] != 0:
        print("meter self-test FAILED; refusing to measure", file=sys.stderr)
        return 2
    install_budget()
    log = io.StringIO()
    print(f"meter self-test: {METER_SELFTEST['summary_line']} (rc {METER_SELFTEST['returncode']})", file=log)
    command = f"python3 experiments/{EXP_ID}/run_experiment.py {args.stage}"
    if args.stage == "cell":
        if args.s is None or args.p is None:
            print("cell needs --s and --p", file=sys.stderr)
            return 4
        if args.s not in S_MAIN + list(S_LIMITED) or args.p not in PRIMES:
            print(f"(s, p) = ({args.s}, {args.p}) is not a planned cell", file=sys.stderr)
            return 4
        if not miller_rabin(args.p):
            print(f"p = {args.p} is not prime", file=sys.stderr)
            return 4
        command += f" --s {args.s} --p {args.p}"
        label = args.suffix or f"s{args.s}-p{args.p}"
        fn = lambda: cell_run(args.s, args.p, label, log)  # noqa: E731
    elif args.stage == "calib":
        fn = lambda: calibration_run(log)  # noqa: E731
    else:
        fn = lambda: s1_run(log)  # noqa: E731
    if args.suffix:
        command += f" --suffix {args.suffix}"
    if args.out_root:
        command += f" --out-root {args.out_root}"

    def status_of(res: runner.RunResult) -> str:
        if res.metrics.get("stopped"):
            return "failed_infrastructure"
        if not res.valid:
            return "invalid_measurement"
        return "completed_valid"

    # harness.runner.run_wrapped requires the terminal status BEFORE fn() runs, but the
    # status here (completed_valid | failed_infrastructure | invalid_measurement) is decided
    # by the measurement.  The bracket below is run_wrapped's body verbatim (time.time +
    # monotonic clock around fn, then write_run with the measured wall_seconds); the only
    # difference is that the status is decided from the returned RunResult (implementation.md D1).
    started_wall = time.time()
    t0 = time.monotonic()
    res = fn()
    if args.suffix:
        res.run_suffix = args.suffix
    t1 = time.monotonic()
    finished_wall = time.time()
    run_id = runner.write_run(EXP_ID, EXP_AREA, res, status=status_of(res), command=command,
                              started=started_wall, finished=finished_wall, out_root=args.out_root,
                              wall_seconds=t1 - t0,
                              timing_source="run_experiment.py bracket (harness.runner.run_wrapped body verbatim; status decided after fn)")
    run_dir = os.path.join(args.out_root or EXP_DIR, "runs", run_id)
    sums = []
    for name in ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json"]:
        with open(os.path.join(run_dir, name), "rb") as fh:
            sums.append(f"{hashlib.sha256(fh.read()).hexdigest()}  {name}")
    with open(os.path.join(run_dir, "checksums.sha256"), "w") as fh:
        fh.write("\n".join(sums) + "\n")
    print(run_id)
    print(f"status={status_of(res)} wall={t1 - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
