#!/usr/bin/env python3
"""
Lab 04 — The elliptic curve discrete logarithm problem (ECDLP).

Companion to course module 07. Run directly:

    python3 lab04_ecdlp.py

Given P of prime order n and Q = d*P, recover d. Three generic-group
algorithms, in increasing sophistication:

  * brute force                O(n)   time
  * baby-step giant-step       O(sqrt n) time AND memory
  * Pollard's rho              O(sqrt n) time, O(1) memory

"Generic" means they only use the group operation — they work in ANY
group. Shoup proved sqrt(n) is optimal for generic algorithms, which is
exactly why 256-bit curves give ~128-bit security, and why this course's
host repository studies whether non-generic structure can ever be
exploited. (For comparison: F_p^* falls to sub-exponential index calculus,
which is why ECC keys are so much shorter than classic DH/RSA keys.)
"""

from __future__ import annotations

import random
from math import gcd, isqrt

from lab01_arithmetic import factorize, is_probable_prime, modinv
from lab02_finite_fields import Fp
from lab03_elliptic_curves import (EllipticCurve, Point, count_points_Fp,
                                   point_order)


def dlog_bruteforce(P: Point, Q: Point, n: int) -> int:
    """Walk P, 2P, 3P, ... until we hit Q. O(n) additions."""
    R = P.curve.zero()
    for d in range(n):
        if R == Q:
            return d
        R = R + P
    raise ValueError("no discrete log (Q not in <P>?)")


def dlog_bsgs(P: Point, Q: Point, n: int) -> int:
    """Baby-step giant-step (Shanks). Write d = i*m - j with m = ceil(sqrt n):
    then Q + j*P = i*(m*P). Store baby steps Q + j*P in a table, walk giant
    steps i*(m*P) until a collision. O(sqrt n) time and memory."""
    m = isqrt(n) + 1
    baby: dict[Point, int] = {}
    R = Q
    for j in range(m):
        baby[R] = j
        R = R + P
    mP = m * P
    S = mP
    for i in range(1, m + 1):
        if S in baby:
            return (i * m - baby[S]) % n
        S = S + mP
    raise ValueError("no discrete log found")


def dlog_pollard_rho(P: Point, Q: Point, n: int,
                     rng: random.Random | None = None,
                     counter: list[int] | None = None) -> int:
    """Pollard's rho with Floyd cycle-finding. Pseudorandom walk over
    X = a*P + b*Q in 3 partitions keyed by the x-coordinate; a collision
    X_i = X_j gives (a_i - a_j) P = (b_j - b_i) Q, i.e. a linear relation
    that reveals d when b_j - b_i is invertible mod the prime n.

    Expected ~sqrt(pi*n/2) steps by the birthday paradox, with constant
    memory — the reason it, and not BSGS, is the practical ECDLP attack.
    """
    if not is_probable_prime(n):
        raise ValueError("rho as written needs prime order n")
    rng = rng or random.Random(0xD106)
    steps = 0

    def step(X: Point, a: int, b: int) -> tuple[Point, int, int]:
        nonlocal steps
        steps += 1
        # Partition by x-coordinate; O goes to a fixed branch.
        s = 0 if X.inf else hash(X.x) % 3
        if s == 0:
            return X + P, (a + 1) % n, b
        if s == 1:
            return 2 * X, 2 * a % n, 2 * b % n
        return X + Q, a, (b + 1) % n

    while True:
        a0, b0 = rng.randrange(n), rng.randrange(n)
        X = a0 * P + b0 * Q
        tort = (X, a0, b0)
        hare = step(*tort)
        while tort[0] != hare[0]:
            tort = step(*tort)
            hare = step(*step(*hare))
        _, a1, b1 = tort
        _, a2, b2 = hare
        db = (b1 - b2) % n
        if db == 0:
            continue  # degenerate collision; restart with a new start point
        if counter is not None:
            counter.append(steps)
        return (a2 - a1) * modinv(db, n) % n


def make_prime_order_generator(curve: EllipticCurve, n_curve: int,
                               rng: random.Random) -> tuple[Point, int]:
    """Return (G, n) with G of prime order n, the largest prime factor of
    #E: compute a random point's exact order o and clear the cofactor o/n."""
    n = max(factorize(n_curve))
    while True:
        G = curve.random_point(rng)
        o = point_order(G, n_curve)
        if o % n == 0:
            return (o // n) * G, n


# ----------------------------------------------------------------------
# Self-checks and demo
# ----------------------------------------------------------------------

def _selfcheck() -> None:
    rng = random.Random(5)
    p = 1013
    E = EllipticCurve(Fp(p, 1), Fp(p, 1))
    N = count_points_Fp(E)
    G, n = make_prime_order_generator(E, N, rng)
    for _ in range(10):
        d = rng.randrange(1, n)
        Q = d * G
        assert dlog_bruteforce(G, Q, n) == d
        assert dlog_bsgs(G, Q, n) == d
        assert dlog_pollard_rho(G, Q, n, rng) == d
    # Edge cases: d = 0 and d = n - 1.
    assert dlog_bsgs(G, E.zero(), n) == 0
    assert dlog_bsgs(G, (n - 1) * G, n) == n - 1
    print("lab04: all self-checks passed")


def _demo() -> None:
    rng = random.Random(6)
    print("\n-- demo: sqrt-n scaling of generic ECDLP attacks --")
    print(f"{'p':>8} {'n (order)':>10} {'sqrt(n)':>8} {'rho steps (avg of 5)':>21}")
    for p in (1013, 10007, 100003, 1000003):
        # Pick b so that #E has a large prime factor (a real subgroup, the
        # way standardized curves are chosen with tiny cofactor).
        for bval in range(1, 200):
            try:
                E = EllipticCurve(Fp(p, 1), Fp(p, bval))
            except ValueError:
                continue
            N = count_points_Fp(E)
            if max(factorize(N)) > p // 8:
                break
        G, n = make_prime_order_generator(E, N, rng)
        counter: list[int] = []
        for _ in range(5):
            d = rng.randrange(1, n)
            assert dlog_pollard_rho(G, d * G, n, rng, counter) == d
        avg = sum(counter) / len(counter)
        print(f"{p:>8} {n:>10} {isqrt(n):>8} {avg:>21.0f}")
    print("n grows ~1000x from top to bottom; rho's work grows ~sqrt(1000)"
          " ~ 32x.")
    print("Extrapolate to n ~ 2^256: sqrt(n) = 2^128 steps. Infeasible.")
    # EXERCISE 4.1: replace Floyd cycle-finding with Brent's algorithm and
    #   measure the speedup.
    # EXERCISE 4.2: implement Pohlig-Hellman on a curve whose order is
    #   smooth (many small prime factors) by combining dlog_bsgs per prime
    #   power with crt() from lab 01 — then explain why standards insist on
    #   (near-)prime-order curves.
    # EXERCISE 4.3: rho's walk must be "random enough". Break it: use a
    #   single partition (always X + P) and watch the running time revert
    #   to O(n).


if __name__ == "__main__":
    _selfcheck()
    _demo()
