"""Medium-scale curve samplers for GOAL-CZLIFT-1516d5 (IDEA-20261009-93b29f).

New module; harness/czlift.py is reused unmodified. The lane-1 samplers
enumerate every prime in a range and count points on each twist, which is
O(p) per curve and fine below 2000 but not between 10^4 and 10^5. Here the
candidate (D, p) pairs are enumerated first (primality only), a seeded
subsample is drawn, and only the sampled curves are counted exactly, so the
cost stays at a few seconds per curve while the count remains exact.
"""
from __future__ import annotations

import random

import sympy

from harness import czlift
from harness.toycurve import EllipticCurve


def anomalous_candidates(pmin: int, pmax: int, discriminants=(-3, -11, -19, -43, -67, -163)):
    """(D, p) with 4p = 1 + |D| v^2, p prime in [pmin, pmax]; no counting."""
    czlift.cm_self_test()
    out = []
    for D in discriminants:
        A0, B0 = czlift.CM_MODELS[D]
        disc = 4 * A0 ** 3 + 27 * B0 ** 2
        v = 1
        while True:
            num = 1 + abs(D) * v * v
            if num % 4 == 0:
                p = num // 4
                if p > pmax:
                    break
                if p >= pmin and p > 5 and sympy.isprime(p) and disc % p and (6 * D) % p:
                    out.append((D, p))
            v += 2
    return out


def resolve_anomalous(D: int, p: int):
    """The integral CM model twisted so that #E(F_p) = p, or None."""
    A0, B0 = czlift.CM_MODELS[D]
    for A, B in czlift._twists(D, A0, B0, p):
        if EllipticCurve(p, A % p, B % p).order() == p:
            return (D, p, A, B, czlift.CM_J[D])
    return None


def sample_anomalous(pmin: int, pmax: int, count: int, rng: random.Random):
    cands = anomalous_candidates(pmin, pmax)
    rng.shuffle(cands)
    out = []
    for D, p in cands:
        r = resolve_anomalous(D, p)
        if r is not None:
            out.append(r)
        if len(out) >= count:
            break
    return sorted(out, key=lambda t: (t[1], t[0]))


def sample_cm_prime_subgroup(pmin: int, pmax: int, count: int, nmin: int, rng: random.Random,
                             discriminants=(-3, -7, -8, -11, -19, -43, -67, -163)):
    """(D, p, A, B, N, n) for sampled primes, odd order, prime subgroup n != p, n >= nmin."""
    czlift.cm_self_test()
    primes = list(sympy.primerange(pmin, pmax))
    rng.shuffle(primes)
    out = []
    for p in primes:
        D = rng.choice(discriminants)
        A0, B0 = czlift.CM_MODELS[D]
        if (6 * D * (4 * A0 ** 3 + 27 * B0 ** 2)) % p == 0:
            continue
        for A, B in czlift._twists(D, A0, B0, p):
            N = EllipticCurve(p, A % p, B % p).order()
            n = czlift.largest_prime_factor(N)
            if n >= nmin and n != p and N % 2 == 1:
                out.append((D, p, A, B, N, n))
                break
        if len(out) >= count:
            break
    return sorted(out, key=lambda t: t[1])


def sample_random_prime_subgroup(pmin: int, pmax: int, count: int, nmin: int, rng: random.Random):
    primes = list(sympy.primerange(pmin, pmax))
    rng.shuffle(primes)
    out = []
    for p in primes:
        found = czlift.random_curves_with_prime_subgroup([p], nmin, random.Random(rng.randrange(1 << 30)), tries=40)
        if found:
            out.append(found[0])
        if len(out) >= count:
            break
    return sorted(out)
