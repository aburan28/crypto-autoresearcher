"""Dual-route mitt search: Route A table-field hash lookup; Route B schoolbook re-add."""
from __future__ import annotations

import math
import random

from curve import Curve
from gf2 import Field, TableField, MODULI, is_irreducible

RELERR_BAND = 0.25
TIE_BAND = 0.05
ATTEMPTS = 200
E_M2_TARGETS = [5, 15, 40]
STAGE1_N = 17
POOL_SEED = 202610015859
R_SEED = 202610015860
NULL_SEED = 202610015861


def make_fields(n: int) -> tuple[TableField, Field]:
    mod = MODULI[n]
    ok, details = is_irreducible(mod)
    if not ok:
        raise RuntimeError(f"modulus n={n} not irreducible: {details}")
    table = TableField(n, mod)
    school = Field(n, mod)
    return table, school


def make_koblitz(F) -> Curve:
    return Curve(F, A=0, B=1)


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
    p_m3 = 1.0 - math.exp(-p_m2) if N >= 0 else 0.0
    return {"p_m1": p_m1, "p_m2": p_m2, "p_m3": p_m3}


def choose_N(group_order: int, e_m2_target: int, attempts: int) -> int:
    # E_M2 = attempts * N^2 / |G|  =>  N = ceil(sqrt(e * |G| / attempts))
    inner = e_m2_target * group_order / float(attempts)
    n = int(math.ceil(math.sqrt(inner)))
    return max(n, 1)


def relerr(phat: float, pmod: float) -> float:
    if pmod == 0.0:
        return float("inf") if phat != 0.0 else 0.0
    return abs(phat - pmod) / pmod


def mitt_search(
    table_curve: Curve,
    school_curve: Curve,
    pool: list,
    n_attempts: int,
    seed: int,
) -> dict:
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
        "certificate_pass": cert_pass,
        "certificate_fail": cert_fail,
        "twin_fail": twin_fail,
        "hit_examples": hits[:3],
        "certificate_kind": "decomposition" if hits else "none",
    }


def empty_pool_null(table_curve: Curve, school_curve: Curve, attempts: int = 20) -> dict:
    return mitt_search(table_curve, school_curve, [], attempts, NULL_SEED)


def build_uniform_pool(table_curve: Curve, N: int, seed: int) -> list:
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
        raise RuntimeError(f"pool short: {len(pool)} < {N}")
    return pool
