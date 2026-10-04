"""Find good-reduction ordinary curves with a prime-order subgroup."""
from __future__ import annotations

import random

import sympy
from sympy.ntheory.residue_ntheory import sqrt_mod

from ec_jac import Curve


def fp_add(P, Q, p, A):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        if y1 % p == 0:
            return None
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def fp_mul(k, P, p, A):
    R = None
    Q = P
    while k > 0:
        if k & 1:
            R = fp_add(R, Q, p, A)
        Q = fp_add(Q, Q, p, A)
        k >>= 1
    return R


def count_points(A, B, p) -> int:
    cnt = 1
    for x in range(p):
        rhs = (x**3 + A * x + B) % p
        if rhs == 0:
            cnt += 1
        else:
            if pow(rhs, (p - 1) // 2, p) == 1:
                cnt += 2
    return cnt


def find_point_of_order_n(A, B, p, N, n):
    cofactor = N // n
    for x in range(p):
        rhs = (x**3 + A * x + B) % p
        if rhs == 0:
            continue
        if pow(rhs, (p - 1) // 2, p) != 1:
            continue
        y = sqrt_mod(rhs, p)
        if y is None or y % p == 0:
            continue
        S = fp_mul(cofactor, (x, y), p, A)
        if S is None or S[1] % p == 0:
            continue
        if fp_mul(n, S, p, A) is None:
            return S
    return None


def pick_prime_factor_in_band(N: int, bit_lo: int, bit_hi: int):
    """Largest prime factor of N whose bit length sits in [bit_lo, bit_hi]."""
    fac = sympy.factorint(N)
    candidates = [
        q for q in fac if sympy.isprime(q) and bit_lo <= q.bit_length() <= bit_hi
    ]
    if not candidates:
        return None
    return max(candidates)


def find_curve(bits: int, seed: int, bit_lo: int = 16, bit_hi: int = 26, max_tries: int = 80):
    """Return a dict describing one ordinary good-reduction instance."""
    rng = random.Random(seed)
    lo = 1 << (bits - 1)
    hi = 1 << bits
    for _ in range(max_tries):
        p = int(sympy.nextprime(rng.randrange(lo, hi)))
        if p.bit_length() > bits:
            continue
        A = rng.randrange(p)
        B = rng.randrange(1, p)
        disc = (-16 * (4 * A**3 + 27 * B**2)) % p
        if disc == 0:
            continue
        N = count_points(A, B, p)
        if N == p:
            continue  # anomalous: order-n lift does not exist
        if N == p + 1:
            continue  # supersingular
        n = pick_prime_factor_in_band(N, bit_lo, bit_hi)
        if n is None:
            if sympy.isprime(N) and bit_lo <= N.bit_length() <= bit_hi:
                n = N
            else:
                continue
        if n == p:
            continue
        S = find_point_of_order_n(A, B, p, N, n)
        if S is None:
            continue
        curve = Curve(p=p, A=A, B=B)
        return {
            "curve": curve,
            "p": p,
            "A": A,
            "B": B,
            "N": N,
            "n": n,
            "S": S,
            "a_p": p + 1 - N,
            "disc_mod_p": disc,
            "bits_p": p.bit_length(),
            "bits_n": n.bit_length(),
        }
    raise RuntimeError(f"no curve found at {bits} bits with seed={seed}")
