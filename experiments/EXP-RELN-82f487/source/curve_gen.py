"""Curve generation for EXP-RELN-82f487, per specification.yaml's inputs
"CURVES" clause: p the first prime at or above 2^k (1 + j/64) for j the
curve index, (a, b) drawn by seed until #E(F_p) is prime.

Uses harness/toycurve.py's EllipticCurve for arithmetic (the program's
existing prime-field EC code, per the contract's implementation clause);
this file implements ONLY this contract's own curve-seed convention, which
is deliberately different from EXP-RELN-f202be's (see specification.yaml
design_handoff_note).
"""
from __future__ import annotations

import hashlib
import math
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import sympy  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402


def seed_int(seed: int, tag: str) -> int:
    h = hashlib.sha256(f"{seed}:{tag}".encode()).hexdigest()
    return int(h, 16)


def first_prime_at_or_above(x: float) -> int:
    start = int(math.ceil(x))
    return int(sympy.nextprime(start - 1))


def generate_curve(rung_k: int, curve_index_j: int, curve_seed: int, max_tries: int = 2000) -> dict:
    """p = first prime >= 2^k (1 + j/64); search (a,b) by curve_seed until
    #E(F_p) is prime (naive O(p) point count, toy scale only)."""
    target = (2 ** rung_k) * (1.0 + curve_index_j / 64.0)
    p = first_prime_at_or_above(target)
    for t in range(max_tries):
        a = seed_int(curve_seed, f"a{t}") % p
        b = seed_int(curve_seed, f"b{t}") % p
        disc = (4 * a ** 3 + 27 * b ** 2) % p
        if disc == 0:
            continue
        E = EllipticCurve(p, a, b)
        N = E.order()
        if sympy.isprime(N):
            # deterministic second-method check independent of sympy for the
            # toy-scale N here (matches the sibling experiment's convention
            # of a second independent primality method).
            if not _trial_division_prime(N):
                continue
            # find a generator point (any non-identity point works: N prime)
            P = None
            for x in range(1, p):
                P = E.lift_x(x)
                if P is not None:
                    break
            if P is None:
                continue
            return {
                "rung": rung_k,
                "curve_index_j": curve_index_j,
                "curve_seed": curve_seed,
                "p": p,
                "a": a,
                "b": b,
                "N": N,
                "P": list(P),
                "tries": t + 1,
            }
    raise RuntimeError(f"no prime-order curve found for rung={rung_k} j={curve_index_j} seed={curve_seed}")


def _trial_division_prime(n: int) -> bool:
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


if __name__ == "__main__":
    rec = generate_curve(14, 1, 101)
    print(rec)
