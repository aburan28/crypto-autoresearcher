"""INDEPENDENT certificate verifier for the EXP-ECDLP-612fb1 curve arm.

This module deliberately shares no code with curve.py or instrument.py:
its own affine group law (extended-Euclid inverse, not pow(x, -1, p)), its
own Montgomery-ladder scalar multiplication, its own primality test bases.
It is the run wrapper's re-check of every claimed discrete logarithm
([k]P == Q) and of the curve record (docs/claims-and-verification.md).
It is also the only code that reads the seeded logarithm x_u.
"""
from __future__ import annotations

import math
import random


def _egcd_inv(a: int, p: int) -> int:
    a %= p
    if a == 0:
        raise ZeroDivisionError("inverse of zero")
    r0, r1 = p, a
    s0, s1 = 0, 1
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    if r0 != 1:
        raise ZeroDivisionError("not invertible")
    return s0 % p


def _add(P1, P2, a: int, p: int):
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    x1, y1 = P1
    x2, y2 = P2
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2 and y1 == y2:
        lam = ((3 * x1 * x1 + a) * _egcd_inv(2 * y1, p)) % p
    else:
        lam = ((y2 - y1) * _egcd_inv((x2 - x1) % p, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def scalar_mul(k: int, P, a: int, p: int):
    """Montgomery ladder (constant structure, right-to-left independent of
    the solver's left-to-right double-and-add)."""
    if k < 0:
        raise ValueError("negative scalar")
    R0, R1 = None, P
    for bit in bin(k)[2:] if k else "0":
        if bit == "1":
            R0 = _add(R0, R1, a, p)
            R1 = _add(R1, R1, a, p)
        else:
            R1 = _add(R0, R1, a, p)
            R0 = _add(R0, R0, a, p)
    return R0


def on_curve(Q, a: int, b: int, p: int) -> bool:
    if Q is None:
        return True
    x, y = Q
    return 0 <= x < p and 0 <= y < p and (y * y - (x * x * x + a * x + b)) % p == 0


def is_prime(n: int) -> bool:
    """Miller-Rabin with bases {11, 13, 17, 19, 23, 29, 31, 37}: deterministic
    for n < 3.3e24, disjoint from the solver's bases."""
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for q in small:
        if n % q == 0:
            return n == q
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a_ in (11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a_, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def verify_discrete_log(cert: dict, curve: dict) -> dict:
    """cert: {curve_id, P: [x, y], Q: [x, y], k}; curve: {p, a, b, N, curve_id}.
    Returns {verified: bool, reason}."""
    p, a, b, N = curve["p"], curve["a"], curve["b"], curve["N"]
    if cert.get("curve_id") != curve["curve_id"]:
        return {"verified": False, "reason": "curve_id mismatch"}
    P = tuple(cert["P"])
    Q = tuple(cert["Q"])
    k = int(cert["k"])
    if not (0 <= k < N):
        return {"verified": False, "reason": "k out of range"}
    if not on_curve(P, a, b, p) or not on_curve(Q, a, b, p):
        return {"verified": False, "reason": "point not on curve"}
    R = scalar_mul(k, P, a, p)
    if R is None or tuple(R) != Q:
        return {"verified": False, "reason": "[k]P != Q"}
    return {"verified": True, "reason": None}


def verify_curve_record(rec: dict, n_random_points: int = 20, seed: int = 2000) -> dict:
    """Independent check of a curve record {p, a, b, N, P}: p prime, N prime,
    discriminant nonzero, Hasse bound, N > (p + 1 + 2 sqrt p)/2 (so that N
    is the only multiple of N in the Hasse interval), and [N]R = O for the
    generator and n_random_points random points R.  A random point R != O has
    order N (N prime and [N]R = O), so N | #E, and with #E in the Hasse
    interval and #E < 2N this forces #E = N."""
    p, a, b, N = rec["p"], rec["a"], rec["b"], rec["N"]
    out = {"p_prime": is_prime(p), "N_prime": is_prime(N),
           "discriminant_nonzero": (4 * a ** 3 + 27 * b ** 2) % p != 0,
           "hasse": abs(N - p - 1) <= 2 * math.isqrt(p) + 1,
           "N_gt_half_hasse_upper": N > (p + 1 + 2 * math.isqrt(p) + 1) / 2,
           "generator_on_curve": on_curve(tuple(rec["P"]), a, b, p),
           "N_times_generator_is_O": scalar_mul(N, tuple(rec["P"]), a, p) is None,
           "random_points_checked": 0, "random_points_N_times_is_O": True, "random_point_seed": seed}
    rng = random.Random(seed)
    checked = 0
    while checked < n_random_points:
        x = rng.randrange(p)
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            continue
        if pow(rhs, (p - 1) // 2, p) != 1:
            continue
        y = pow(rhs, (p + 1) // 4, p)
        if y * y % p != rhs:
            out["random_points_N_times_is_O"] = False
            break
        R = (x, y)
        if scalar_mul(N, R, a, p) is not None:
            out["random_points_N_times_is_O"] = False
            break
        checked += 1
    out["random_points_checked"] = checked
    out["verified"] = all(v for k, v in out.items() if isinstance(v, bool))
    return out
