"""Pure Python 3 stdlib F_p arithmetic primitives shared by every stage.

Used by both Stage 0 (curve enumeration, isomorphism testing) and Stage 1
(base-point classification). No F_{p^2}/F_{p^4} arithmetic anywhere in this
module or this experiment's implementation -- unlike the sibling
EXP-MONO-4c7479, this contract's inert-case classification never lifts to
an extension field (see H-MONO-0f9170 mechanism /
`stage1_classification.independence_from_sibling_arms`).

Modular-square-root routine: GENERAL TONELLI-SHANKS, unconditionally, for
BOTH tested primes (101 and 211). p=101 = 1 mod 4, so the p=3-mod-4
shortcut is unavailable there; the contract requires using the SAME
routine for both primes for consistency once the general routine is
needed at all, so the p%4==3 fast-path branch is deliberately NOT used
even for p=211 (where it would apply) -- see `stage1_classification`'s
`environment_preconditions` requirement in the frozen specification.
"""
from __future__ import annotations


def legendre(a: int, p: int) -> int:
    """Legendre symbol (a/p) in {-1, 0, 1}, p an odd prime."""
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return -1 if r == p - 1 else 1


def inverse(a: int, p: int) -> int:
    a %= p
    if a == 0:
        raise ZeroDivisionError(f"no inverse of 0 mod {p}")
    return pow(a, p - 2, p)


def tonelli_shanks(n: int, p: int):
    """General Tonelli-Shanks square root mod p. Returns one root, or None
    if n is a non-residue. n=0 -> 0. Used unconditionally (no p=3-mod-4
    shortcut branch) for both tested primes, per the frozen contract's
    consistency requirement."""
    n %= p
    if n == 0:
        return 0
    if legendre(n, p) != 1:
        return None
    # Write p - 1 = q * 2^s with q odd.
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    # Find a quadratic non-residue z.
    z = 2
    while legendre(z, p) != -1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2i = 0, t
        while t2i != 1:
            t2i = (t2i * t2i) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p
    return r
