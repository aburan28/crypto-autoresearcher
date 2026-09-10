"""Curve generation for EXP-RELN-f202be, per specification.yaml's
curve_generation block (frozen recipe). Reuses harness/toycurve.py's
arithmetic and hashing CONVENTIONS only (EllipticCurve class, the
SHA256(f"{seed}:{tag}") seed-integer convention); generate_instance() is
NOT used, per the spec's explicit instruction, because it accepts
cofactors and this contract requires prime N exactly.

This is a helper module (not one of the two required independent
enumerators); direct_enumerator.py imports harness.toycurve for its curve
arithmetic, spectral_crosscheck.py does not import this module or
harness.toycurve at all.
"""
from __future__ import annotations

import hashlib
import math
import sys
import os

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from harness.toycurve import EllipticCurve  # noqa: E402


def seed_int(seed: int, tag: str) -> int:
    """Exactly harness/toycurve.py's _seed_int convention."""
    h = hashlib.sha256(f"{seed}:{tag}".encode()).hexdigest()
    return int(h, 16)


# ---------------------------------------------------------------------------
# Two INDEPENDENT primality-certification methods for N (spec:
# point_count_certificate). Neither uses sympy, so they are independent of
# each other and of the prime search for p below (which does use sympy, a
# convenience for finding p, not part of the N certificate).
# ---------------------------------------------------------------------------

def miller_rabin_deterministic(n: int) -> bool:
    """Deterministic Miller-Rabin with witnesses correct for all n < 3.3e24
    (Pomerance/Jaeschke bases), far above this contract's N range
    (N < 2^20 + slack)."""
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for sp in small_primes:
        if n == sp:
            return True
        if n % sp == 0:
            return False
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in small_primes:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True


def trial_division_prime(n: int) -> bool:
    """Trial division to sqrt(n). n is at most ~2^20-scale here so this is
    cheap and a genuinely independent second method."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    lim = math.isqrt(n)
    f = 3
    while f <= lim:
        if n % f == 0:
            return False
        f += 2
    return True


def certify_prime(n: int) -> dict:
    mr = miller_rabin_deterministic(n)
    td = trial_division_prime(n)
    return {"miller_rabin": mr, "trial_division": td, "agree": mr == td, "is_prime": mr and td}


# ---------------------------------------------------------------------------
# Curve generation recipe (frozen; see specification.yaml curve_generation)
# ---------------------------------------------------------------------------

def find_prime_p(rung_k: int, seed: int) -> int:
    """p_s = smallest prime >= 2^k + (SHA256('s:p') mod 2^(k-6))."""
    import sympy

    base = 2 ** rung_k
    offset = seed_int(seed, "p") % (2 ** (rung_k - 6))
    start = base + offset
    return int(sympy.nextprime(start - 1))  # nextprime(start-1) >= start if start prime


def lift_x(curve: EllipticCurve, x: int):
    return curve.lift_x(x % curve.p)


def try_generate_curve(rung_k: int, seed: int) -> dict:
    """Attempt one curve at (rung_k, seed). Returns a dict with either
    accepted=True and full certificate, or accepted=False and a reason."""
    p = find_prime_p(rung_k, seed)
    a = seed_int(seed, "a") % p
    b = seed_int(seed, "b") % p

    disc = (4 * a ** 3 + 27 * b ** 2) % p
    if disc == 0:
        return {"seed": seed, "rung": rung_k, "accepted": False, "reason": "singular_curve_disc_zero", "p": p}

    curve = EllipticCurve(p, a, b)

    # Naive Legendre-sum point count (this IS the certificate's primary
    # count method, reused from toycurve.EllipticCurve.order()).
    N = curve.order()

    # (1) Hasse bound check.
    hasse_bound = 2 * math.isqrt(p)
    hasse_ok = abs(N - p - 1) <= hasse_bound

    # (3) primality of N by two independent methods.
    prime_cert = certify_prime(N)

    if not prime_cert["is_prime"]:
        return {
            "seed": seed, "rung": rung_k, "accepted": False, "reason": "N_not_prime",
            "p": p, "a": a, "b": b, "N": N, "hasse_ok": hasse_ok,
            "primality_certificate": prime_cert,
        }
    if not hasse_ok:
        return {
            "seed": seed, "rung": rung_k, "accepted": False, "reason": "hasse_bound_failed",
            "p": p, "a": a, "b": b, "N": N,
        }

    # (2) N*R = O for 8 deterministic points R = lift_x(SHA256('s:x{j}') mod p).
    point_checks = []
    all_ok = True
    for j in range(1, 9):
        x = seed_int(seed, f"x{j}") % p
        R = lift_x(curve, x)
        tries = 0
        while R is None and tries < 50:
            tries += 1
            x = (x + 1) % p
            R = lift_x(curve, x)
        ok = curve.mul(N, R) is None
        point_checks.append({"j": j, "x_used": x, "ok": ok})
        all_ok = all_ok and ok
    if not all_ok:
        return {
            "seed": seed, "rung": rung_k, "accepted": False, "reason": "point_count_certificate_failed",
            "p": p, "a": a, "b": b, "N": N, "point_checks": point_checks,
        }

    # Generator R_1 for small-multiples / log-table base point.
    gx = seed_int(seed, "x1") % p
    R1 = lift_x(curve, gx)
    tries = 0
    while R1 is None and tries < 50:
        tries += 1
        gx = (gx + 1) % p
        R1 = lift_x(curve, gx)

    return {
        "seed": seed,
        "rung": rung_k,
        "accepted": True,
        "p": p,
        "a": a,
        "b": b,
        "N": N,
        "generator_x": R1[0],
        "generator_y": R1[1],
        "certificate": {
            "hasse_bound_ok": hasse_ok,
            "point_count_certificate_points": point_checks,
            "primality_certificate": prime_cert,
        },
    }


def generate_curves_for_rung(rung_k: int, min_curves: int = 3, max_seeds: int = 400) -> dict:
    accepted = []
    rejected = []
    seed = 1
    while len(accepted) < min_curves and seed <= max_seeds:
        rec = try_generate_curve(rung_k, seed)
        if rec["accepted"]:
            accepted.append(rec)
        else:
            rejected.append(rec)
        seed += 1
    return {
        "rung": rung_k,
        "accepted": accepted,
        "rejected": rejected,
        "seeds_scanned": seed - 1,
        "sufficient": len(accepted) >= min_curves,
    }


def build_log_table(curve: EllipticCurve, P, N: int) -> dict:
    """Full discrete-log table log_P: E(F_p) -> Z/N, keyed by (x,y); O -> 0.
    Built by repeated addition, k = 1..N-1 (one addition per step)."""
    table = {"O": 0}
    cur = P
    k = 1
    while cur is not None:
        table[cur] = k
        cur = curve.add(cur, P)
        k += 1
        if k > N:  # safety; should terminate at k==N with cur becoming None
            break
    return table
