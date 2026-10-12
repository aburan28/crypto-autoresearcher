"""Dual-route mitt + matched-density HW pools for EXP-BINSTD-88a926.

Route A: TableField hash lookup on E: Y^2+XY=X^3+1.
Route B: schoolbook Field re-add certificate. No walk. No Magma/Sage/AUXIN.
"""
from __future__ import annotations

import math
import random

from curve import Curve
from gf2 import Field, TableField, MODULI, is_irreducible

YIELD_BAND = [0.7, 1.4]
DENSITY_MATCH_MAX = 0.10
ATTEMPTS = 200
STAGE1_N = 17
POOL_N = 96
CUTOFF_C = 4
POOL_SEED = 202610035638
R_SEED = 202610035639
NULL_SEED = 202610035640
NB_SEED = 202610035641
PB_SEED = 202610035642
UNI_SEED = 202610035643


def make_fields(n: int) -> tuple[TableField, Field]:
    mod = MODULI[n]
    ok, details = is_irreducible(mod)
    if not ok:
        raise RuntimeError(f"modulus n={n} not irreducible: {details}")
    return TableField(n, mod), Field(n, mod)


def make_koblitz(F) -> Curve:
    return Curve(F, A=0, B=1)


def binomial_hw_density(n: int, c: int) -> float:
    return sum(math.comb(n, k) for k in range(c + 1)) / float(1 << n)


def density_rel_err(d_a: float, d_b: float) -> float:
    mid = 0.5 * (d_a + d_b)
    if mid == 0.0:
        return 0.0 if d_a == d_b else float("inf")
    return abs(d_a - d_b) / mid


def find_normal_element(F) -> int:
    n = F.n
    for cand in range(1, F.q):
        mat = []
        x = cand
        for _ in range(n):
            mat.append(x)
            x = F.sqr(x)
        rank = 0
        ok = True
        for col in range(n):
            pivot = None
            for r in range(rank, n):
                if (mat[r] >> col) & 1:
                    pivot = r
                    break
            if pivot is None:
                ok = False
                break
            mat[rank], mat[pivot] = mat[pivot], mat[rank]
            for r in range(n):
                if r != rank and (mat[r] >> col) & 1:
                    mat[r] ^= mat[rank]
            rank += 1
        if ok and rank == n:
            return cand
    raise RuntimeError("no normal element found")


def to_normal_coords(F, beta: int, x: int) -> int:
    n = F.n
    basis = []
    b = beta
    for _ in range(n):
        basis.append(b)
        b = F.sqr(b)
    rows = [0] * n
    for bit in range(n):
        row = 0
        for j in range(n):
            if (basis[j] >> bit) & 1:
                row |= 1 << j
        if (x >> bit) & 1:
            row |= 1 << n
        rows[bit] = row
    for col in range(n):
        pivot = None
        for r in range(col, n):
            if (rows[r] >> col) & 1:
                pivot = r
                break
        if pivot is None:
            continue
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for r in range(n):
            if r != col and (rows[r] >> col) & 1:
                rows[r] ^= rows[col]
    coeffs = 0
    for col in range(n):
        if (rows[col] >> n) & 1:
            coeffs |= 1 << col
    return coeffs


def hw_normal(F, beta: int, x: int) -> int:
    return to_normal_coords(F, beta, x).bit_count()


def hw_poly(x: int) -> int:
    return int(x).bit_count()


def random_curve_point(curve: Curve, rng: random.Random):
    F = curve.F
    for _ in range(20000):
        x = rng.randrange(1, F.q)
        P = curve.lift_x(x)
        if P is not None:
            if rng.randrange(2):
                P = curve.neg(P)
            return P
    raise RuntimeError("failed to sample curve point")


def dual_add_ok(table_curve: Curve, school_curve: Curve, P, Q) -> bool:
    a = table_curve.add(P, Q)
    b = school_curve.add(P, Q)
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a[0] == b[0] and a[1] == b[1]


def reverify_schoolbook(school_curve: Curve, P, Q, R) -> bool:
    S = school_curve.add(P, Q)
    return S is not None and S[0] == R[0] and S[1] == R[1]


def models(N: int, group_order: int) -> dict:
    g = float(group_order)
    p_m1 = (N * (N - 1)) / (2.0 * g) if N >= 1 else 0.0
    p_m2 = (N * N) / g if N >= 0 else 0.0
    return {"p_m1": p_m1, "p_m2": p_m2}


def relerr(phat: float, pmod: float) -> float:
    if pmod == 0.0:
        return float("inf") if phat != 0.0 else 0.0
    return abs(phat - pmod) / pmod


def ratio(a: float, b: float) -> float:
    if b == 0.0:
        return float("inf") if a else float("nan")
    return a / b


def in_yield_band(r: float) -> bool:
    return YIELD_BAND[0] <= r <= YIELD_BAND[1]


def mitt_search(table_curve: Curve, school_curve: Curve, pool: list, n_attempts: int, seed: int) -> dict:
    rng = random.Random(seed)
    idx = {e[0]: e for e in pool}
    hits = []
    cert_pass = 0
    cert_fail = 0
    twin_fail = 0
    for attempt in range(n_attempts):
        R = random_curve_point(table_curve, rng)
        found = None
        for P in pool:
            Q = table_curve.sub(R, P)
            if Q is None:
                continue
            if Q[0] in idx:
                Q_use = Q
                if not dual_add_ok(table_curve, school_curve, P, Q_use):
                    twin_fail += 1
                    continue
                if reverify_schoolbook(school_curve, P, Q_use, R):
                    found = {
                        "attempt": attempt,
                        "R": [int(R[0]), int(R[1])],
                        "P": [int(P[0]), int(P[1])],
                        "Q": [int(Q_use[0]), int(Q_use[1])],
                    }
                    cert_pass += 1
                    break
                cert_fail += 1
        if found:
            hits.append(found)
    N = len(pool)
    p_hat = len(hits) / float(n_attempts) if n_attempts else float("nan")
    return {
        "hits": len(hits),
        "n_attempts": n_attempts,
        "pool_size_N": N,
        "p_hat": p_hat,
        "yield_rate": p_hat,
        "certificate_pass": cert_pass,
        "certificate_fail": cert_fail,
        "twin_fail": twin_fail,
        "hit_examples": hits[:3],
        "certificate_kind": "decomposition" if hits else "none",
    }


def empty_pool_null(table_curve: Curve, school_curve: Curve, attempts: int = 20) -> dict:
    return mitt_search(table_curve, school_curve, [], attempts, NULL_SEED)


def build_uniform_pool(table_curve: Curve, N: int, seed: int) -> tuple[list, int]:
    rng = random.Random(seed)
    pool = []
    seen = set()
    guard = 0
    while len(pool) < N and guard < N * 20000:
        guard += 1
        P = random_curve_point(table_curve, rng)
        if P[0] in seen:
            continue
        seen.add(P[0])
        pool.append(P)
    if len(pool) < N:
        raise RuntimeError(f"uniform pool short: {len(pool)} < {N}")
    return pool, guard


def build_hw_pool(table_curve: Curve, N: int, seed: int, accept) -> tuple[list, int]:
    rng = random.Random(seed)
    pool = []
    seen = set()
    guard = 0
    while len(pool) < N and guard < N * 400000:
        guard += 1
        P = random_curve_point(table_curve, rng)
        if not accept(P):
            continue
        if P[0] in seen:
            continue
        seen.add(P[0])
        pool.append(P)
    if len(pool) < N:
        raise RuntimeError(f"HW pool short: {len(pool)} < {N} after {guard} draws")
    return pool, guard
