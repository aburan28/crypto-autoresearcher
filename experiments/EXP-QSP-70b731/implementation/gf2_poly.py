"""Bit-packed GF(2)[X] arithmetic for EXP-QSP-70b731.

Polynomials are Python ints: bit i is the coefficient of X^i.
Written from first principles for this experiment. The direct-count
technique (repeated squaring of X modulo L = X^{2^{n'}} + lam) follows the
same mathematical identity as the generic helper
analysis/qsp-ecc2k130/explore/gf2rc.c (read for the sparse-reduction pattern
only; no census JSON was read).
"""
from __future__ import annotations

from typing import Iterable, List, Optional, Tuple


def degree(p: int) -> int:
    if p == 0:
        return -1
    return p.bit_length() - 1


def monomial(exp: int) -> int:
    return 1 << exp


def add(a: int, b: int) -> int:
    return a ^ b


def mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    res = 0
    while b:
        if b & 1:
            res ^= a
        a <<= 1
        b >>= 1
    return res


def square(a: int) -> int:
    """GF(2) squaring: insert a zero bit between every coefficient."""
    res = 0
    i = 0
    while a:
        if a & 1:
            res |= 1 << (2 * i)
        a >>= 1
        i += 1
    return res


def mod(a: int, m: int) -> int:
    if m == 0:
        raise ZeroDivisionError("mod by zero polynomial")
    dm = degree(m)
    if dm < 0:
        raise ZeroDivisionError("mod by zero polynomial")
    while degree(a) >= dm:
        a ^= m << (degree(a) - dm)
    return a


def gcd(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, mod(a, b)
    return a


def make_monic(p: int) -> int:
    """Over F_2 every nonzero poly is already monic in the leading bit."""
    return p


def poly_from_exponents(exps: Iterable[int]) -> int:
    p = 0
    for e in exps:
        p ^= 1 << int(e)
    return p


def exponents(p: int) -> List[int]:
    out: List[int] = []
    i = 0
    while p:
        if p & 1:
            out.append(i)
        p >>= 1
        i += 1
    return out


def compose(f: int, g: int) -> int:
    """Functional composition f(g(X)) over GF(2)."""
    if f == 0:
        return 0
    res = 0
    power = 1  # g^0
    ff = f
    while ff:
        if ff & 1:
            res ^= power
        power = mul(power, g)
        ff >>= 1
    return res


def iterate_compose(f: int, k: int) -> int:
    """f composed with itself k times: f^{∘k}. f^{∘0} = X, f^{∘1} = f."""
    if k < 0:
        raise ValueError("k must be >= 0")
    if k == 0:
        return monomial(1)  # X
    res = f
    for _ in range(k - 1):
        res = compose(f, res)
    return res


def eval_at_bit(poly: int, x: int, mul_fn, add_fn, one: int) -> int:
    """Horner evaluation of GF(2)-coeff poly at an element of a GF(2^n) field."""
    if poly == 0:
        return 0  # additive identity; caller interprets
    # Use bit form with field ops: result in field encoding
    d = degree(poly)
    acc = 0
    for i in range(d, -1, -1):
        acc = mul_fn(acc, x)
        if (poly >> i) & 1:
            acc = add_fn(acc, one)
    return acc


def mod_pow2_x_plus_lam(poly: int, np: int, lam: int) -> int:
    """Reduce poly modulo L = X^{2^{np}} + lam (lam degree < 2^{np})."""
    bound = 1 << np
    L = monomial(bound) ^ lam
    while degree(poly) >= bound:
        poly ^= L << (degree(poly) - bound)
    return poly


def repeated_square_x_mod_L(n: int, np: int, lam: int) -> int:
    """Compute X^{2^n} mod L with L = X^{2^{np}} + lam via n squarings."""
    bound = 1 << np
    if degree(lam) >= bound:
        raise ValueError("deg lam must be < 2^{n'}")
    # x = X
    x = monomial(1)
    for _ in range(n):
        x = mod_pow2_x_plus_lam(square(x), np, lam)
    return x


def gcd_degree_with_L(n: int, np: int, lam: int) -> int:
    """N = deg gcd(X^{2^n} - X, L) for L = X^{2^{np}} + lam.

    Computes h = (X^{2^n} - X) mod L, then deg gcd(L, h).
    """
    bound = 1 << np
    x_pow = repeated_square_x_mod_L(n, np, lam)
    h = x_pow ^ monomial(1)  # X^{2^n} + X  (char 2)
    L = monomial(bound) ^ lam
    if h == 0:
        return bound  # L divides X^{2^n}-X
    g = gcd(L, h)
    return degree(g)


def derivative(p: int) -> int:
    """Formal derivative over GF(2): only odd powers contribute."""
    res = 0
    k = 0
    pp = p
    while pp:
        if (pp & 1) and (k & 1):
            res ^= 1 << (k - 1)
        pp >>= 1
        k += 1
    return res


def square_free_part(p: int) -> int:
    """Remove repeated factors: p / gcd(p, p')."""
    if p == 0:
        return 0
    d = derivative(p)
    if d == 0:
        # p is a square (or constant). Peel one square root of bit pattern.
        # For census we only need gcd with X^{2^n}-X which is already square-free
        # in the product of distinct (X-a). Caller should pass already-reduced g.
        return p
    g = gcd(p, d)
    if g == 0 or degree(g) == 0:
        return p
    # Exact division over F_2 by repeated subtraction (Euclid quotient)
    return exact_div(p, g)


def exact_div(a: int, b: int) -> int:
    if b == 0:
        raise ZeroDivisionError("exact_div by 0")
    if a == 0:
        return 0
    q = 0
    db = degree(b)
    while a and degree(a) >= db:
        shift = degree(a) - db
        q ^= 1 << shift
        a ^= b << shift
    if a != 0:
        raise ValueError("exact_div: not divisible")
    return q


def pow_mod(base: int, exp: int, m: int) -> int:
    res = 1  # X^0
    base = mod(base, m)
    while exp > 0:
        if exp & 1:
            res = mod(mul(res, base), m)
        base = mod(mul(base, base), m)
        exp >>= 1
    return res


def x_pow_2n_minus_x(n: int) -> Tuple[int, callable]:
    """Not materialised; use modular repeated squaring against a modulus."""
    raise NotImplementedError


def gcd_with_field_poly(poly: int, n: int) -> int:
    """g = gcd(poly, X^{2^n} - X) via h = X^{2^n} mod poly, then gcd(poly, h+X)."""
    if poly == 0:
        raise ValueError("zero poly")
    if degree(poly) < 0:
        raise ValueError("zero poly")
    # X^{2^n} mod poly
    x = monomial(1)
    # If deg poly == 0 (nonzero constant), gcd is 1
    if degree(poly) == 0:
        return 1
    for _ in range(n):
        x = mod(square(x), poly)
    h = x ^ monomial(1)
    if h == 0:
        return poly  # poly divides X^{2^n}-X
    return gcd(poly, h)


def distinct_degree_factorization(f: int, n: int) -> List[Tuple[int, int]]:
    """DDF over F_2 for a square-free f that splits in F_{2^n}.

    Returns list of (product_of_irreps_of_degree_d, d).
    Uses the standard X^{2^i} progression mod f.
    """
    f = make_monic(f)
    if degree(f) <= 0:
        return []
    factors: List[Tuple[int, int]] = []
    v = f
    w = monomial(1)  # X
    for d in range(1, degree(f) + 1):
        if degree(v) == 0:
            break
        # w <- w^{2} mod v  => after d steps, w = X^{2^d} mod v
        w = mod(square(w), v)
        # g = gcd(w - X, v)
        g = gcd(w ^ monomial(1), v)
        if degree(g) > 0:
            factors.append((g, d))
            v = exact_div(v, g)
            w = mod(w, v)
        if degree(v) == 0:
            break
    if degree(v) > 0:
        factors.append((v, degree(v)))
    return factors


def berlekamp_factors_equal_degree(f: int, d: int, n_field: int) -> List[int]:
    """Split square-free equal-degree product of irreducibles of degree d over F_2.

    Uses random Cantor–Zassenhaus style traces for characteristic 2.
    """
    import random

    f = make_monic(f)
    target = degree(f) // d
    if target <= 1:
        return [f] if degree(f) > 0 else []
    factors = [f]
    rng = random.Random(0x70B731 ^ (d << 16) ^ degree(f))
    guard = 0
    while len(factors) < target and guard < 10_000:
        guard += 1
        new_factors: List[int] = []
        progressed = False
        for h in factors:
            if degree(h) == d:
                new_factors.append(h)
                continue
            # random poly of deg < deg(h)
            dh = degree(h)
            r = rng.getrandbits(dh) if dh > 0 else 0
            # Trace-like: q = r + r^2 + r^4 + ... + r^{2^{d-1}}  mod h
            # For equal-degree factorisation of degree-d irreps over F_2,
            # compute Tr(r) = sum_{i=0}^{d-1} r^{2^i} mod h, then gcd(h, Tr(r)).
            acc = 0
            power = mod(r, h)
            for _ in range(d):
                acc ^= power
                power = mod(square(power), h)
            g = gcd(acc, h)
            if degree(g) > 0 and degree(g) < degree(h):
                new_factors.append(make_monic(g))
                new_factors.append(make_monic(exact_div(h, g)))
                progressed = True
            else:
                new_factors.append(h)
        factors = new_factors
        if not progressed and guard > target * 50:
            # fallback: try (r^{(2^{d*m}-1)/c}) style with m=#factors remaining
            break
    # Filter to irreducibles of degree d (best effort)
    out = [make_monic(x) for x in factors if degree(x) == d]
    if sum(degree(x) for x in out) != degree(f):
        # Incomplete split — return what we have plus unsplit remainder as opaque block
        return [make_monic(x) for x in factors if degree(x) > 0]
    return out


def factor_squarefree_splitting(f: int, n: int) -> List[int]:
    """Factor square-free f that splits completely into irreducibles over F_2
    with degrees dividing n. Returns list of irreducible factors.
    """
    f = make_monic(gcd_with_field_poly(f, n) if True else f)
    # Ensure we work with the splitting part
    g = gcd_with_field_poly(f, n)
    g = make_monic(g)
    if degree(g) <= 0:
        return []
    # Square-free: g should already be (X^{2^n}-X shares no squares with distinct roots)
    parts = distinct_degree_factorization(g, n)
    irreps: List[int] = []
    for block, d in parts:
        if degree(block) == d:
            irreps.append(make_monic(block))
        elif degree(block) > 0:
            irreps.extend(berlekamp_factors_equal_degree(block, d, n))
    return [p for p in irreps if degree(p) > 0]
