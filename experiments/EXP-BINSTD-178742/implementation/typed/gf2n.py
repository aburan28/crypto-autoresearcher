"""Stdlib-only binary-field / F_2[t] helpers for EXP-BINSTD-178742 packaging.

Pattern adapted from experiments/EXP-CERTBIN-e94b27/impl/gf2n.py (schoolbook
carry-less multiply + polynomial reduction). Numpy / TableField paths are
omitted so this module stays stdlib-only for packaging. No deployed census
values, no AUXIN/FROB/QSP figures.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple


def clmul(a: int, b: int) -> int:
    """Carry-less product of two F_2[t] polynomials encoded as ints."""
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a: int, m: int) -> int:
    """Reduce polynomial a modulo modulus m."""
    if m == 0:
        raise ZeroDivisionError("modulus is zero")
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def is_irreducible(mod: int) -> Tuple[bool, Dict[str, Any]]:
    """Rabin-style irreducibility test over F_2 (stdlib schoolbook)."""
    n = mod.bit_length() - 1
    details: Dict[str, Any] = {"n": n, "gcd_checks": []}
    x = 2  # t
    cur = x
    ok = True
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)  # t^{2^i}
        if i <= n // 2:
            g = pgcd(mod, cur ^ x)
            details["gcd_checks"].append({"i": i, "gcd": g})
            if g != 1:
                ok = False
    details["t_pow_2n_equals_t"] = cur == x
    ok = ok and cur == x
    return ok, details


class Field:
    """Generic schoolbook F_{2^n} = F_2[t]/(mod)."""

    def __init__(self, n: int, mod: int):
        if n < 1:
            raise ValueError("n must be positive")
        if mod.bit_length() - 1 != n:
            raise ValueError("mod degree must equal n")
        self.n = n
        self.mod = mod
        self.q = 1 << n

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, self.q - 2)


def packaging_surface() -> Dict[str, Any]:
    """Dry packaging probe: tiny-field irreducibility and mul identity."""
    # t^3 + t + 1 is irreducible over F_2
    mod3 = (1 << 3) | (1 << 1) | 1
    ok3, det3 = is_irreducible(mod3)
    f3 = Field(3, mod3)
    mul_ok = f3.mul(0b011, 0b101) == pmod(clmul(0b011, 0b101), mod3)
    # t^2 + t + 1 irreducible
    mod2 = (1 << 2) | (1 << 1) | 1
    ok2, _ = is_irreducible(mod2)
    return {
        "module": "gf2n",
        "stdlib_only": True,
        "pattern_source": "EXP-CERTBIN-e94b27/impl/gf2n.py (schoolbook only)",
        "irreducible_t3_t_1": ok3,
        "irreducible_t2_t_1": ok2,
        "mul_identity_ok": mul_ok,
        "details_n3": det3,
        "ok": bool(ok3 and ok2 and mul_ok),
        "note": "Packaging smoke only; does not score Part 1 census or Part 2 ranks.",
    }
