"""
Instrumented F_p field arithmetic.

Every multiplication and squaring performed through this module increments a
global counter object passed in explicitly (never a hidden module-level
global) so that counts can be attributed to a specific measurement context
(a specific member / seed / phase) without cross-contamination between Q1
(group-operation counting, which must NOT look at field cost) and Q2 (field
multiplication/squaring counting).

Counter discipline:
  - `Counters.mul` is incremented for every general F_p multiplication.
  - `Counters.sqr` is incremented for every F_p squaring performed via the
    dedicated `fp_sqr` entry point (so callers that know an operation is a
    squaring get a cheaper AND separately-tallied operation, matching the
    contract's M/S aggregation requirement).
  - Additions, subtractions, and negations are NOT counted: the contract's
    Q2 metric is defined over multiplications and squarings only.
  - Modular inverse is counted in its own field (`inv`) since it is not a
    multiplication or squaring; the common-coordinate (affine) Q1 engine
    uses it, but Q1 itself does not read this counter (Q1 is a pure
    group-operation count, not a field-cost count).
"""
from __future__ import annotations


class Counters:
    __slots__ = ("mul", "sqr", "inv", "add")

    def __init__(self):
        self.mul = 0
        self.sqr = 0
        self.inv = 0
        self.add = 0

    def as_dict(self):
        return {"mul": self.mul, "sqr": self.sqr, "inv": self.inv, "add": self.add}

    def reset(self):
        self.mul = 0
        self.sqr = 0
        self.inv = 0
        self.add = 0


def fp_mul(x: int, y: int, p: int, ctr: "Counters | None" = None) -> int:
    if ctr is not None:
        ctr.mul += 1
    return (x * y) % p


def fp_sqr(x: int, p: int, ctr: "Counters | None" = None) -> int:
    if ctr is not None:
        ctr.sqr += 1
    return (x * x) % p


def fp_add(x: int, y: int, p: int, ctr: "Counters | None" = None) -> int:
    if ctr is not None:
        ctr.add += 1
    return (x + y) % p


def fp_sub(x: int, y: int, p: int, ctr: "Counters | None" = None) -> int:
    if ctr is not None:
        ctr.add += 1
    return (x - y) % p


def fp_inv(x: int, p: int, ctr: "Counters | None" = None) -> int:
    """Modular inverse via Fermat's little theorem (p prime, x != 0 mod p)."""
    if x % p == 0:
        raise ZeroDivisionError("fp_inv of 0")
    if ctr is not None:
        ctr.inv += 1
    return pow(x, p - 2, p)


def legendre(a: int, p: int) -> int:
    """Legendre symbol (a|p) for odd prime p. Returns -1, 0, or 1.

    Not instrumented: used only for structural/search code (base-curve
    selection, class-number computation, twist tests), never inside a
    counted solve.
    """
    a = a % p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return -1 if r == p - 1 else r


def is_fourth_power(a: int, p: int) -> bool:
    """True iff a is a nonzero fourth power mod p (a != 0 mod p required)."""
    a = a % p
    if a == 0:
        return False
    return _is_nth_power(a, p, 4)


def gcd_(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def _is_nth_power(a: int, p: int, n: int) -> bool:
    """a is a nonzero n-th power mod p iff a**((p-1)//d) == 1 where d = gcd(n, p-1)."""
    d = gcd_(n, p - 1)
    return pow(a, (p - 1) // d, p) == 1
