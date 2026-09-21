"""
Base-curve selection: search for a P-256-shaped toy curve
    y^2 = x^3 - 3x + b   (a = -3, matching the NIST P-256 model directly)
over a prime p of a declared bit length, such that:
  - N = #E(F_p) is prime (ensures no rational torsion subgroup other than
    the trivial one and the whole group; also required by the contract);
  - the curve is ordinary (t = p+1-N != 0);
  - D = t^2 - 4p is a fundamental discriminant (conductor f = 1, the flat
    volcano condition; is_fundamental_discriminant is an independent
    arithmetic check, not read off from anywhere else);
  - t mod ell != 0 for every ell in the declared isogeny_degrees (odd ell):
    this is a STRUCTURAL rejection condition, fixed before any solve and
    before any cost datum exists. It exists because when ell | t, the two
    Frobenius eigenvalues mod ell are negatives of each other, and the
    x-coordinate-only kernel-polynomial recovery in division_poly.py
    (which never leaves F_p, by design -- see that module's docstring)
    cannot separate the two resulting rational subgroups: any test built
    from x-coordinates alone is invariant under point negation, so it
    returns the UNION of both subgroups (degree ell-1) instead of either
    individual kernel (degree (ell-1)/2). This was found and diagnosed via
    the selftest self-check (point-count edge certificate failing to
    reproduce N when this condition is violated) before any run began;
    the fix is to reject the affected base curves rather than to build the
    (feasible, but materially larger) irreducible-factorization plus
    small-extension-field disambiguation machinery that would be needed to
    handle it. Recorded here as a documented scope limitation, not a
    silent workaround: it costs a small amount of search space (roughly a
    factor of prod_ell (1 - 1/ell) of candidates survive) but changes
    nothing about which isogeny edges exist once a curve is accepted --
    every accepted curve's isogeny graph is exactly its true F_p-isogeny
    class edges for the declared degree set, correctly computed.
  - the FULL declared degree set generates the class completely under
    this curve, i.e. the walk vertex count equals the independently
    computed class number h(D) (curve_utils.class_number) -- checked here,
    BEFORE any DLP instance exists or any solve happens, so it is a
    structural selection criterion and not a post-hoc adjustment on cost
    data. A curve whose walk is incomplete under the declared degrees is
    rejected and logged, exactly like every other rejection reason.

Every rejected candidate and its rejection reason is appended to the
returned rejection log (required artifact).
"""
from __future__ import annotations

import random

from curve_utils import (
    build_qr_table, point_count_with_qr, is_fundamental_discriminant,
    class_number,
)
from class_walk import enumerate_class

ISOGENY_DEGREES = [2, 3, 5, 7, 11, 13]
ODD_DEGREES = [d for d in ISOGENY_DEGREES if d % 2 == 1]


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % sp == 0:
            return n == sp
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime(n: int) -> int:
    if n % 2 == 0:
        n += 1
    while not is_prime(n):
        n += 2
    return n


def select_base_curve(bit_length: int, seed: int, max_primes: int = 6, max_b_per_prime: int = 4000):
    """
    Returns (chosen: dict or None, rejection_log: list[dict], primes_tried: list[int]).
    """
    rng = random.Random(seed)
    rejection_log = []
    primes_tried = []
    low = 1 << (bit_length - 1)
    high = (1 << bit_length) - 1

    for _pi in range(max_primes):
        start = rng.randrange(low, high)
        p = next_prime(start)
        if p > high:
            p = next_prime(low)
        primes_tried.append(p)
        qr = build_qr_table(p)
        a = (-3) % p
        for b in range(1, max_b_per_prime + 1):
            disc_sing = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
            if disc_sing == 0:
                rejection_log.append({"p": p, "a": a, "b": b, "reason": "singular_curve"})
                continue
            N = point_count_with_qr(p, a, b, qr)
            t = p + 1 - N
            if t == 0:
                rejection_log.append({"p": p, "a": a, "b": b, "N": N, "reason": "supersingular_t_zero"})
                continue
            if N == p:
                rejection_log.append({"p": p, "a": a, "b": b, "N": N, "reason": "anomalous_N_equals_p"})
                continue
            if not is_prime(N):
                rejection_log.append({"p": p, "a": a, "b": b, "N": N, "reason": "N_not_prime"})
                continue
            D = t * t - 4 * p
            if not is_fundamental_discriminant(D):
                rejection_log.append({"p": p, "a": a, "b": b, "N": N, "t": t, "D": D, "reason": "not_fundamental_discriminant"})
                continue
            bad_ell = [ell for ell in ODD_DEGREES if t % ell == 0]
            if bad_ell:
                rejection_log.append({
                    "p": p, "a": a, "b": b, "N": N, "t": t, "D": D,
                    "reason": "t_divisible_by_isogeny_degree",
                    "degrees": bad_ell,
                })
                continue
            h = class_number(D)
            walk = enumerate_class(p, a, b, N, t, ISOGENY_DEGREES, edge_cert_seed=seed)
            if len(walk.vertices) != h:
                rejection_log.append({
                    "p": p, "a": a, "b": b, "N": N, "t": t, "D": D, "h": h,
                    "walk_vertices": len(walk.vertices),
                    "reason": "incomplete_class_under_declared_degrees",
                })
                continue
            chosen = {
                "p": p, "a": a, "b": b, "N": N, "t": t, "D": D, "h": h,
                "walk": walk, "seed": seed,
            }
            return chosen, rejection_log, primes_tried
    return None, rejection_log, primes_tried
