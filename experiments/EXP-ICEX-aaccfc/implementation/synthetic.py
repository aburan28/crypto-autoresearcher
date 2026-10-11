"""Non-frozen synthetic fixtures for smoke checks (AMD-20260929-5a84eb FX-5).

A smoke check must not evaluate a frozen fixture at its frozen (m, B). This
module builds small prime-order curves by a deterministic search (no RNG, no
Sage) using the uncharged verifier arithmetic. Their bit length (13) differs
from every frozen fixture (16, 20 bits) and `common.is_frozen_fixture` is
checked on every result.

  synthetic_fixture(0)  -> first curve found from p = 4099 upward
"""

from __future__ import annotations

import common
from verify import VCurve

P_START = 4099
SEED_BASE = 900


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def _order(vc: VCurve) -> int:
    p = vc.p
    n = 1  # point at infinity
    for x in range(p):
        r = vc.rhs(x)
        if r == 0:
            n += 1
        elif pow(r, (p - 1) // 2, p) == 1:
            n += 2
    return n


def _L(vc: VCurve, m: int) -> int:
    B = common.fb_bound(vc.p, m)
    return sum(1 for x in range(B) if vc.liftable(x))


def synthetic_fixture(index: int = 0) -> dict:
    """index-th curve (p >= P_START prime, y^2 = x^3 + a x + b) with prime order N != p,
    L >= 3 at m = 5 and L >= 1 at m = 6 and 8, so every smoke cell kind is exercisable."""
    found = -1
    p = P_START
    while True:
        if _is_prime(p):
            for a in range(1, 8):
                for b in range(1, 8):
                    if (4 * a ** 3 + 27 * b ** 2) % p == 0:
                        continue
                    vc = VCurve(p, a, b)
                    if min(_L(vc, 5) - 2, _L(vc, 6), _L(vc, 8)) < 1:
                        continue
                    N = _order(vc)
                    if N == p or not _is_prime(N):
                        continue
                    found += 1
                    if found < index:
                        continue
                    x = 3
                    while not vc.liftable(x):
                        x += 1
                    fx = {"G": list(vc.lift(x)), "N": N, "a": a, "b": b, "bits": p.bit_length(),
                          "counter": 0, "exp": "synthetic-smoke (NOT a frozen fixture)", "p": p,
                          "seed": SEED_BASE + index}
                    if common.is_frozen_fixture(fx):
                        raise AssertionError("synthetic fixture collides with a frozen fixture")
                    return fx
        p += 1
