"""Twin independent meters: k(d) and cover simulation.

Path A and path B must agree on k(d) and on formula P(cover).
Cover Monte Carlo uses different hashes (blake2b vs sha256) and is
checked against the formula, not against each other.
"""
from __future__ import annotations

import hashlib
import random
from typing import Iterable

from ntheory import factor_trial, reconstruct


def divisors_path_a(factors: list[tuple[int, int]]) -> list[int]:
    divs = [1]
    for p, e in factors:
        if e <= 0:
            continue
        more: list[int] = []
        for d in divs:
            pe = p
            for _ in range(e):
                more.append(d * pe)
                pe *= p
        divs.extend(more)
    return divs


def divisors_path_b(factors: list[tuple[int, int]]) -> list[int]:
    items = [(p, e) for p, e in factors if e > 0]
    out: list[int] = []

    def rec(i: int, acc: int) -> None:
        if i == len(items):
            out.append(acc)
            return
        p, e = items[i]
        pe = 1
        for _ in range(e + 1):
            rec(i + 1, acc * pe)
            pe *= p

    rec(0, 1)
    return out


def k_window(divisors: Iterable[int], d: int, X: int) -> tuple[int, list[int]]:
    lo = (d + X - 1) // X  # ceil(d/X)
    hi = X
    admissible = sorted({a for a in divisors if lo <= a <= hi})
    return len(admissible), admissible


def k_both(factors: list[tuple[int, int]], d: int, X: int) -> dict:
    da = divisors_path_a(factors)
    db = divisors_path_b(factors)
    if sorted(da) != sorted(db):
        return {"agree": False, "k_a": None, "k_b": None, "A": []}
    if reconstruct(factors) != d:
        return {"agree": False, "k_a": None, "k_b": None, "A": []}
    ka, Aa = k_window(da, d, X)
    kb, Ab = k_window(db, d, X)
    return {"agree": ka == kb and Aa == Ab, "k_a": ka, "k_b": kb, "A": Aa}


def cover_formula(k: int, rho: float) -> float:
    if k < 0:
        raise ValueError("k")
    if k == 0:
        return 0.0
    return 1.0 - (1.0 - rho * rho) ** (k / 2.0)


def _u64_blake(key: bytes, a: int) -> int:
    h = hashlib.blake2b(digest_size=8, person=b"ssiq-a")
    h.update(key)
    h.update(a.to_bytes((a.bit_length() + 7) // 8 or 1, "big"))
    return int.from_bytes(h.digest(), "big")


def _u64_sha(key: bytes, a: int) -> int:
    h = hashlib.sha256()
    h.update(b"ssiq-b")
    h.update(key)
    h.update(a.to_bytes((a.bit_length() + 7) // 8 or 1, "big"))
    return int.from_bytes(h.digest()[:8], "big")


def _unit(u64: int) -> float:
    return u64 / float(1 << 64)


def pair_covered(admissible: list[int], d: int, rho: float, key: bytes, path: str) -> bool:
    fn = _u64_blake if path == "a" else _u64_sha
    in_s = {}
    for a in admissible:
        if a not in in_s:
            in_s[a] = _unit(fn(key, a)) < rho
        b = d // a
        if b not in in_s:
            in_s[b] = _unit(fn(key, b)) < rho
        if in_s[a] and in_s[b]:
            return True
    return False


def simulate_cover(admissible: list[int], d: int, k: int, rho: float, n_seeds: int, rng: random.Random, path: str) -> float:
    if k == 0 or not admissible:
        return 0.0
    hits = 0
    for _ in range(n_seeds):
        key = rng.getrandbits(64).to_bytes(8, "big")
        if pair_covered(admissible, d, rho, key, path):
            hits += 1
    return hits / n_seeds


def character_cover(admissible: list[int], d: int, mod: int = 5) -> bool:
    """Perfectly correlated thinning: keep a iff jacobi(a, mod)=+1 (plus degree 1)."""
    from ntheory import jacobi

    def keep(a: int) -> bool:
        if a == 1:
            return True
        return jacobi(a, mod) == 1

    for a in admissible:
        if keep(a) and keep(d // a):
            return True
    return False


def sample_bsmooth_factors(primes: list[int], B: int, dmax: int, rng: random.Random) -> list[tuple[int, int]] | None:
    """Construct a random B-smooth integer in (dmax//4, dmax] via prime products."""
    lo = max(2, dmax // 4)
    primes_b = [p for p in primes if p <= B]
    if not primes_b:
        return None
    for _ in range(200):
        n = 1
        counts: dict[int, int] = {}
        guard = 0
        while n < lo and guard < 400:
            p = primes_b[rng.randrange(len(primes_b))]
            if n > dmax // p:
                break
            n *= p
            counts[p] = counts.get(p, 0) + 1
            guard += 1
        if lo < n <= dmax:
            return sorted(counts.items())
        if n > dmax and counts:
            # drop last prime if possible
            p, e = next(reversed(list(counts.items())))
            n //= p
            if e == 1:
                del counts[p]
            else:
                counts[p] = e - 1
            if lo < n <= dmax:
                return sorted(counts.items())
    return None


def _random_prime(rng: random.Random, bits: int) -> int:
    from ntheory import miller_rabin

    if bits < 3:
        bits = 3
    for _ in range(10000):
        n = rng.getrandbits(bits) | 1 | (1 << (bits - 1))
        if miller_rabin(n):
            return n
    raise RuntimeError(f"failed to sample a {bits}-bit prime")


def two_prime_k2(primes: list[int], target_bits: int, rng: random.Random, X: int | None = None) -> tuple[int, list[tuple[int, int]]]:
    """d=l1*l2 with both primes within factor 2 of sqrt(d) and k=2 in window X.

    Need X < d <= X^2 so 1 and d fall outside [d/X, X] while the two
    midpoints remain inside.
    """
    del primes  # not used; MR primes are generated to sit above X
    half = max(8, (int(X).bit_length() + 2) // 2) if X else max(8, target_bits // 2)
    for _ in range(400):
        p = _random_prime(rng, half)
        q = _random_prime(rng, half)
        if p == q:
            continue
        if p > q:
            p, q = q, p
        if q > 2 * p:
            continue
        d = p * q
        if X is not None and not (X < d <= X * X):
            continue
        if X is not None:
            lo = (d + X - 1) // X
            if not (lo <= p <= X and lo <= q <= X):
                continue
        return d, [(p, 1), (q, 1)]
    raise RuntimeError("failed to construct k=2 two-prime object")


def fourteen_prime_product(primes: list[int]) -> tuple[int, list[tuple[int, int]]]:
    fac = [(p, 1) for p in primes[:14]]
    d = 1
    for p, e in fac:
        d *= p**e
    return d, fac
