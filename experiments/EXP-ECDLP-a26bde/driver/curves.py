"""Deterministic, seeded generator for the five frozen global curves (each
with a small-integer rational point) and their four toy reduction primes
apiece, plus one anomalous toy curve with a rational point. See
experiments/EXP-ECDLP-a26bde/derivation_note.md Stage 0 for the frozen list
this produces (run once and pasted there) and the exact criteria below.

Criteria for a MAIN (curve, prime) pair:
  - E^: y^2 = x^3 + A x + B, integer A, small integer point (x0, y0), with
    B = y0^2 - x0^3 - A x0 (so the point is exact by construction).
  - E^ nonsingular over Q (discriminant != 0).
  - S^ = (x0, y0) has infinite order over Q (checked up to the m-ladder's
    largest multiple: none of them is O).
  - p in [2**10, 2**14) (10 to 14 bits), p does not divide the curve
    discriminant (good reduction), ordinary (trace of Frobenius != 0 mod p,
    automatic for p > 3 since |trace| < 2 sqrt(p) < p unless trace = 0
    exactly), and #E(F_p) != p (non-anomalous, which for p >= 5 is exactly
    the condition p does not divide #E(F_p) at all, since #E(F_p) mod p =
    1 - trace mod p and |trace| < p forces trace = 1 as the only way p |
    #E(F_p) -- i.e. #E(F_p) != p already implies gcd(n, p) = 1 for every
    point order n | #E(F_p), which is asserted directly below rather than
    just assumed).
  - n = order of S = (S^ mod p) in E(F_p); gcd(n, p) = 1 (asserted).

Criteria for the ANOMALOUS pair: same curve shape and point, but a prime p
in the same bit range with #E(F_p) == p exactly (so E(F_p) is cyclic of
prime order p, trace of Frobenius = 1, and every nonzero point -- including
S = S^ mod p -- has order exactly p).
"""
from __future__ import annotations

import hashlib
import os
import sys
from fractions import Fraction

import sympy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from harness.toycurve import EllipticCurve  # noqa: E402

from exactcurve import is_on_curve as is_on_curve_q, mul as mul_q  # noqa: E402

P_BITS_LO = 10
P_BITS_HI = 14
M_LADDER = list(range(1, 65)) + [96, 128, 192, 256]
PRIMES_PER_CURVE = 4


def _seed_int(seed: int, tag: str) -> int:
    h = hashlib.sha256(f"{seed}:{tag}".encode()).hexdigest()
    return int(h, 16)


def _nonsingular(A: int, B: int) -> bool:
    return (4 * A ** 3 + 27 * B ** 2) != 0


def _infinite_order_up_to_ladder(A: int, B: int, x0: int, y0: int) -> bool:
    P = (Fraction(x0), Fraction(y0))
    for m in M_LADDER:
        Q = mul_q(A, B, m, P)
        if Q is None:
            return False
    return True


def _candidate_curves(seed: int, count: int, avoid=None):
    """Yield (A, B, x0, y0) candidates in increasing search order, skipping
    any curve already used (by (A, B, x0, y0) tuple, via `avoid`)."""
    avoid = avoid or set()
    found = 0
    t = 0
    while found < count:
        t += 1
        x0 = 1 + (_seed_int(seed, f"x0.{t}") % 9)
        y0 = 1 + (_seed_int(seed, f"y0.{t}") % 9)
        A = 1 + (_seed_int(seed, f"A.{t}") % 9)
        B = y0 * y0 - x0 ** 3 - A * x0
        if B == 0:
            continue
        if not _nonsingular(A, B):
            continue
        if not is_on_curve_q(A, B, (Fraction(x0), Fraction(y0))):
            continue
        key = (A, B, x0, y0)
        if key in avoid:
            continue
        if not _infinite_order_up_to_ladder(A, B, x0, y0):
            continue
        avoid.add(key)
        found += 1
        yield key


def _point_order(E: EllipticCurve, S) -> int:
    n = 1
    Q = S
    limit = 4 * E.p  # generous; Hasse bound guarantees order <= p + 1 + 2*sqrt(p)
    while Q is not None:
        Q = E.add(Q, S)
        n += 1
        if n > limit:
            raise RuntimeError("_point_order: did not terminate within Hasse bound")
    return n


def _reduce_point(x0: int, y0: int, p: int):
    return (x0 % p, y0 % p)


def _find_primes_for_curve(A: int, B: int, x0: int, y0: int, seed: int,
                            curve_idx: int, count: int = PRIMES_PER_CURVE):
    primes = []
    lo, hi = 2 ** P_BITS_LO, 2 ** P_BITS_HI
    # deterministic order: walk primes starting from a seeded offset within
    # [lo, hi), wrapping, so different curves/seeds get different prime sets
    start = lo + (_seed_int(seed, f"pstart.{curve_idx}") % (hi - lo))
    p = int(sympy.nextprime(start - 1))
    seen_start = p
    first = True
    while len(primes) < count:
        if p >= hi:
            p = int(sympy.nextprime(lo - 1))
        if not first and p == seen_start:
            raise RuntimeError(f"_find_primes_for_curve: exhausted range "
                                f"[{lo},{hi}) for curve {curve_idx}")
        first = False
        if p > 3 and (4 * A ** 3 + 27 * B ** 2) % p != 0:
            E = EllipticCurve(p, A, B)
            order = E.order()
            trace = p + 1 - order
            if trace % p != 0 and order != p:
                Smod = _reduce_point(x0, y0, p)
                if Smod[1] % p != 0 and E.is_on_curve(Smod):
                    n = _point_order(E, Smod)
                    import math
                    if math.gcd(n, p) == 1:
                        primes.append({"p": p, "order": order, "trace": trace, "n": n})
        p = int(sympy.nextprime(p))
    return primes


def _find_anomalous(seed: int, avoid) -> dict:
    """Search for a (curve, prime) pair with #E(F_p) == p exactly, reusing
    the same small-height rational-point curve shape."""
    lo, hi = 2 ** P_BITS_LO, 2 ** P_BITS_HI
    t = 0
    while True:
        t += 1
        x0 = 1 + (_seed_int(seed, f"anom.x0.{t}") % 9)
        y0 = 1 + (_seed_int(seed, f"anom.y0.{t}") % 9)
        A = 1 + (_seed_int(seed, f"anom.A.{t}") % 9)
        B = y0 * y0 - x0 ** 3 - A * x0
        if B == 0 or not _nonsingular(A, B):
            continue
        if (A, B, x0, y0) in avoid:
            continue
        for p in sympy.primerange(lo, hi):
            if (4 * A ** 3 + 27 * B ** 2) % p == 0:
                continue
            E = EllipticCurve(p, A, B)
            if E.order() == p:
                Smod = _reduce_point(x0, y0, p)
                if Smod[1] % p != 0 and E.is_on_curve(Smod):
                    return {"A": A, "B": B, "x0": x0, "y0": y0, "p": p, "order": p}
        if t > 5000:
            raise RuntimeError("_find_anomalous: search exhausted")


def frozen_instances(seed: int = 20260905, num_curves: int = 5):
    """Returns (curves, anomalous):
      curves: list of dicts {idx, A, B, x0, y0, primes: [ {p, order, trace, n}, ... ]}
      anomalous: dict {A, B, x0, y0, p, order}
    Deterministic in `seed` alone."""
    avoid = set()
    curves = []
    for idx, (A, B, x0, y0) in enumerate(_candidate_curves(seed, num_curves, avoid)):
        primes = _find_primes_for_curve(A, B, x0, y0, seed, idx)
        curves.append({"idx": idx, "A": A, "B": B, "x0": x0, "y0": y0, "primes": primes})
    anomalous = _find_anomalous(seed, avoid)
    return curves, anomalous


if __name__ == "__main__":
    import json
    curves, anomalous = frozen_instances()
    print(json.dumps({"curves": curves, "anomalous": anomalous}, indent=2))
