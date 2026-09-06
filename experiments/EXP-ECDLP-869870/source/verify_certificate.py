"""INDEPENDENT certificate verifier for EXP-ECDLP-869870 curve-arm runs.

Shares no code with curve.py or instrument.py: its own field arithmetic, its
own point addition and its own double-and-add scalar multiplication on Python
integers. Verifies a discrete_log certificate (curve_id, P, Q, k): [k]P == Q,
and separately compares k with the seeded logarithm supplied by the caller.
"""
from __future__ import annotations

import hashlib


def _add(p, a, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow((2 * y1) % p, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def scalar_mul(p, a, k, P):
    R = None
    B = P
    for bit in bin(k)[2:][::-1]:
        if bit == "1":
            R = _add(p, a, R, B)
        B = _add(p, a, B, B)
    return R


def curve_id_of(p, a, b):
    return "TOY-P24-" + hashlib.sha256(f"{p}:{a}:{b}".encode()).hexdigest()[:8]


def verify(cert: dict, curve: dict, seeded_k: int | None) -> dict:
    p, a, b = curve["p"], curve["a"], curve["b"]
    P = tuple(cert["statement"]["P"]); Q = tuple(cert["statement"]["Q"]); k = int(cert["statement"]["k"])
    ok_id = cert["curve_id"] == curve_id_of(p, a, b) == curve["curve_id"]
    onP = (P[1] * P[1] - (P[0] ** 3 + a * P[0] + b)) % p == 0
    onQ = (Q[1] * Q[1] - (Q[0] ** 3 + a * Q[0] + b)) % p == 0
    R = scalar_mul(p, a, k, P)
    independent_ok = (R is not None and R[0] == Q[0] and R[1] == Q[1])
    seeded_ok = (seeded_k is None) or (k % curve["N"] == seeded_k % curve["N"])
    return {"curve_id_ok": ok_id, "P_on_curve": onP, "Q_on_curve": onQ,
            "independent_kP_eq_Q": bool(independent_ok), "matches_seeded_log": bool(seeded_ok),
            "verified": bool(ok_id and onP and onQ and independent_ok and seeded_ok)}
