"""Toy elliptic-curve arithmetic over prime fields for ECDLP experiments.

Exact and deterministic at toy scale (fields up to ~32 bits). Everything here
is verifiable: a discrete-log claim k is checked by recomputing k*P, and curve
membership by the defining equation. This module is the independent verifier
the certificate discipline (docs/claims-and-verification.md) relies on, so it
deliberately uses straightforward, auditable formulas rather than fast ones.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import sympy

# A curve point: (x, y) affine, or None for the point at infinity O.
Point = tuple[int, int] | None


class EllipticCurve:
    """y^2 = x^3 + a*x + b over F_p (short Weierstrass, p > 3)."""

    def __init__(self, p: int, a: int, b: int):
        if p <= 3:
            raise ValueError("this toy model requires p > 3")
        a %= p
        b %= p
        disc = (4 * a * a * a + 27 * b * b) % p
        if disc == 0:
            raise ValueError("singular curve (discriminant 0)")
        self.p, self.a, self.b = p, a, b

    # -- membership / arithmetic -------------------------------------------
    def is_on_curve(self, pt: Point) -> bool:
        if pt is None:
            return True
        x, y = pt
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def negate(self, pt: Point) -> Point:
        if pt is None:
            return None
        x, y = pt
        return (x, (-y) % self.p)

    def add(self, P: Point, Q: Point) -> Point:
        if P is None:
            return Q
        if Q is None:
            return P
        p = self.p
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if P == Q:
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1 % p, -1, p) % p
        else:
            lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p
        return (x3, y3)

    def mul(self, k: int, P: Point) -> Point:
        """Scalar multiplication k*P by double-and-add (k may be any integer)."""
        if P is None:
            return None
        if k < 0:
            return self.mul(-k, self.negate(P))
        result: Point = None
        addend = P
        while k > 0:
            if k & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return result

    # -- structure ---------------------------------------------------------
    def order(self) -> int:
        """#E(F_p) by naive point counting (exact; toy-scale only)."""
        p = self.p
        total = 1  # point at infinity
        for x in range(p):
            rhs = (x * x * x + self.a * x + self.b) % p
            if rhs == 0:
                total += 1
            elif pow(rhs, (p - 1) // 2, p) == 1:
                total += 2
        return total

    def order_bsgs(self) -> int:
        """#E(F_p) via Hasse-bound candidate search.

        Uses the Hasse bound |t| <= 2*sqrt(p): for each candidate trace
        t in [-2*sqrt(p), 2*sqrt(p)], tests whether (p+1-t)*R == O for a
        random point R. Cost O(sqrt(p)) scalar multiplications, each
        O(log p) group operations — far faster than the O(p) naive count
        for p > 2^20.
        """
        import math
        p = self.p
        hasse = int(2 * math.isqrt(p))
        center = p + 1

        # Pick a random point R on E
        R = None
        for x in range(1, p):
            R = self.lift_x(x)
            if R is not None:
                break
        if R is None:
            raise RuntimeError("no point on curve")

        for t in range(-hasse, hasse + 1):
            n = center - t
            if n <= 0:
                continue
            if self.mul(n, R) is None:
                # Verify with a second point to avoid small-order artifacts
                R2 = None
                for x2 in range(p // 2, p):
                    R2 = self.lift_x(x2)
                    if R2 is not None and R2 != R:
                        break
                if R2 is not None and self.mul(n, R2) is None:
                    return n
                # If only R works, R has smaller order; try next candidate
        # Fallback
        return self.order()

    def lift_x(self, x: int) -> Point:
        """A point with the given x-coordinate, or None if x is not on E."""
        p = self.p
        rhs = (x * x * x + self.a * x + self.b) % p
        if rhs == 0:
            return (x % p, 0)
        if pow(rhs, (p - 1) // 2, p) != 1:
            return None
        y = _sqrt_mod(rhs, p)
        return None if y is None else (x % p, y)


def _sqrt_mod(a: int, p: int) -> int | None:
    r = sympy.ntheory.residue_ntheory.sqrt_mod(a, p)
    return int(r) if r is not None else None


@dataclass(frozen=True)
class ECDLPInstance:
    """A reproducible ECDLP challenge Q = k*P with P of prime order n."""
    p: int
    a: int
    b: int
    P: Point
    Q: Point
    n: int          # prime order of P
    k: int          # the secret (kept for verification/oracle, never used by solvers)
    field_bits: int
    seed: int

    def curve(self) -> EllipticCurve:
        return EllipticCurve(self.p, self.a, self.b)


def _seed_int(seed: int, tag: str) -> int:
    h = hashlib.sha256(f"{seed}:{tag}".encode()).hexdigest()
    return int(h, 16)


def generate_instance(seed: int, field_bits: int,
                      min_prime_order_bits: int = 3) -> ECDLPInstance:
    """Deterministically build an ECDLP instance of the given field bit size.

    Picks a prime p near 2**field_bits, a non-singular curve, a base point P
    generating a prime-order subgroup (the largest prime factor of #E), and a
    secret k with Q = k*P. Fully determined by (seed, field_bits).
    """
    if field_bits < 4:
        raise ValueError("field_bits must be >= 4 for this toy model")
    p = int(sympy.nextprime(_seed_int(seed, "p") % (2 ** field_bits) | (1 << (field_bits - 1))))
    # Search deterministically for a non-singular curve with a usable subgroup.
    for t in range(1, 2000):
        a = _seed_int(seed, f"a{t}") % p
        b = _seed_int(seed, f"b{t}") % p
        try:
            E = EllipticCurve(p, a, b)
        except ValueError:
            continue
        order = E.order() if field_bits <= 24 else E.order_bsgs()
        factors = sympy.factorint(order)
        n = int(max(factors))                 # largest prime factor -> subgroup order
        if n.bit_length() < min_prime_order_bits or n < 5:
            continue
        cofactor = order // n
        P = _find_point_of_order(E, n, cofactor, seed, t)
        if P is None:
            continue
        k = _seed_int(seed, f"k{t}") % (n - 2) + 2   # 2 <= k <= n-1
        Q = E.mul(k, P)
        return ECDLPInstance(p, a, b, P, Q, n, k, field_bits, seed)
    raise RuntimeError(f"no suitable curve found for seed={seed}, bits={field_bits}")


def _find_point_of_order(E: EllipticCurve, n: int, cofactor: int,
                         seed: int, t: int) -> Point:
    p = E.p
    for j in range(1, 4000):
        x = _seed_int(seed, f"x{t}.{j}") % p
        R = E.lift_x(x)
        if R is None:
            continue
        P = E.mul(cofactor, R)          # kill the cofactor -> order divides n
        # n is prime, so if P != O and n*P == O then P has order exactly n.
        if P is not None and E.mul(n, P) is None:
            return P
    return None
