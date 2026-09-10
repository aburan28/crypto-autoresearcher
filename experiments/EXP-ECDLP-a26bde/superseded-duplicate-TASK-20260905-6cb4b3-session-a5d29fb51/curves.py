"""Stage 0: frozen curve and prime generation for EXP-ECDLP-a26bde.

Deterministic, seeded search (seed 20260905 per specification.replication)
for five global curves y^2 = x^3 + a x + b with small-integer rational
points, each with four toy primes (10-14 bits) of good, non-anomalous
reduction, plus one anomalous toy curve/prime pair (#E(F_p) == p) as the
proves-too-much control.
"""
from __future__ import annotations

import hashlib
import sympy


def seed_stream(seed: int, tag: str):
    i = 0
    while True:
        h = hashlib.sha256(f"{seed}:{tag}:{i}".encode()).digest()
        yield int.from_bytes(h, "big")
        i += 1


def naive_add(P, Q, a, p):
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


def naive_mul(k, P, a, p):
    if k == 0 or P is None:
        return None
    R = None
    addend = P
    while k > 0:
        if k & 1:
            R = naive_add(R, addend, a, p)
        addend = naive_add(addend, addend, a, p)
        k >>= 1
    return R


def order_of_point(P0, a, p, cap):
    R, k = P0, 1
    while R is not None:
        R = naive_add(R, P0, a, p)
        k += 1
        if k > cap:
            raise RuntimeError("order search exceeded cap")
    return k


def count_points(a, p):
    total = 1
    for x in range(p):
        rhs = (x * x * x + a * x) % p
        # b added by caller via closure; see count_points_full below
    raise NotImplementedError


def count_points_full(a, b, p):
    total = 1
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            total += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:
            total += 2
    return total


def find_curve_and_point(seed: int, tag: str, bound: int = 12):
    """Deterministically search small (x0, y0, a) with b chosen so
    (x0, y0) is on y^2 = x^3 + a x + b, curve nonsingular over Q."""
    stream = seed_stream(seed, tag)
    for _ in range(20000):
        r = next(stream)
        x0 = (r % (2 * bound + 1)) - bound
        r >>= 8
        y0 = (r % (2 * bound + 1)) - bound
        r >>= 8
        a = (r % (2 * bound + 1)) - bound
        if y0 == 0:
            continue
        b = y0 * y0 - x0 ** 3 - a * x0
        disc = -16 * (4 * a ** 3 + 27 * b ** 2)
        if disc == 0:
            continue
        return {"a": a, "b": b, "x0": x0, "y0": y0, "disc": disc}
    raise RuntimeError("no curve found")


def find_primes_for_curve(curve, seed: int, tag: str, count: int,
                           bit_lo: int = 10, bit_hi: int = 14,
                           want_anomalous: bool = False):
    """Find `count` toy primes of good reduction for this curve.

    Non-anomalous: gcd(n, p) = 1 and #E(F_p) != p.
    Anomalous (want_anomalous=True): #E(F_p) == p exactly (n == p case).
    """
    a, b, x0, y0 = curve["a"], curve["b"], curve["x0"], curve["y0"]
    disc = curve["disc"]
    stream = seed_stream(seed, tag + ":primes")
    found = []
    tried = 0
    while len(found) < count and tried < 4000:
        tried += 1
        r = next(stream)
        bits = bit_lo + (r % (bit_hi - bit_lo + 1))
        r >>= 8
        cand = (r % (2 ** bits)) | (1 << (bits - 1)) | 1
        p = int(sympy.nextprime(cand))
        if p.bit_length() < bit_lo or p.bit_length() > bit_hi:
            continue
        if p <= 3:
            continue
        if disc % p == 0:
            continue  # bad reduction
        if (2 * y0) % p == 0:
            continue  # S would be 2-torsion / non-invertible slope
        S = (x0 % p, y0 % p)
        rhs = (S[0] ** 3 + a * S[0] + b) % p
        if (S[1] * S[1] - rhs) % p != 0:
            continue
        n_fp = count_points_full(a % p, b % p, p)
        try:
            n = order_of_point(S, a % p, p, 4 * p + 10)
        except RuntimeError:
            continue
        if want_anomalous:
            if n_fp == p:
                found.append({"p": p, "n": n, "n_fp": n_fp, "bits": p.bit_length()})
        else:
            if n_fp == p:
                continue
            if n % p == 0:
                continue
            if not sympy.isprime(n):
                continue  # require prime order so gcd(m, n) = 1 unless n | m
            if any(f["p"] == p for f in found):
                continue
            found.append({"p": p, "n": n, "n_fp": n_fp, "bits": p.bit_length()})
    if len(found) < count:
        raise RuntimeError(f"only found {len(found)}/{count} primes for tag {tag} "
                            f"(want_anomalous={want_anomalous}) after {tried} tries")
    return found


def build_frozen_instances(seed: int, num_curves: int = 5, primes_per_curve: int = 4):
    curves = []
    for i in range(num_curves):
        tag = f"curve{i}"
        curve = find_curve_and_point(seed, tag)
        primes = find_primes_for_curve(curve, seed, tag, primes_per_curve)
        curves.append({"tag": tag, "curve": curve, "primes": primes})
    # anomalous curve: search across a handful of curve candidates for one
    # admitting a prime with #E(F_p) == p exactly.
    anomalous = None
    for i in range(num_curves, num_curves + 30):
        tag = f"anom_candidate{i}"
        curve = find_curve_and_point(seed, tag)
        try:
            primes = find_primes_for_curve(curve, seed, tag, 1, want_anomalous=True)
        except RuntimeError:
            continue
        anomalous = {"tag": tag, "curve": curve, "primes": primes}
        break
    if anomalous is None:
        raise RuntimeError("no anomalous curve/prime found in search budget")
    return {"curves": curves, "anomalous": anomalous}
