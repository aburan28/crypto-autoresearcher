#!/usr/bin/env python3
"""Characteristic-2 nearby-object control of EXP-PEXT-212d5c: the classical GHS magic number at n = 7.

For K = F_{2^N}, N = 7 l, q = 2^l, sigma the q-Frobenius and b in K*, the classical GHS magic number of
E: y^2 + x y = x^3 + a x^2 + b is m_b = dim_{F_2} span{(1, sigma^i(sqrt b)) : 0 <= i < 7} (Gaudry-Hess-Smart;
Menezes-Qu). Square root commutes with sigma and is an F_2-linear bijection, so the span of (1, sigma^i sqrt b) has
the dimension of the span of (1, sigma^i b); this script computes the latter for every b in K*, exactly.
It also computes Ord_b, the monic divisor of x^7 - 1 over F_2 of least degree with Ord_b(sigma) b = 0, and records
whether m_b = deg lcm(Ord_b, x + 1) (the cross-characteristic form of Lemma M7 in H-PEXT-d536a1) for every b.
Predicted before any run (H-PEXT-d536a1, P6): m_b in {1, 4, 7} with counts q - 1, 2 q^4 - 2 q, q^7 - 2 q^4 + q.
The genus of the GHS cover, 2^(m-1) - 1 or 2^(m-1) (source cited in the contract), is not computed here.

  python3 char2_magic.py L [L ...]     -> one JSON line per l in {1, 2, 3}. Standard library only.
"""
from __future__ import annotations

import json
import sys
import time

# divisors of x^7 - 1 over F_2 as bit masks (bit i = coefficient of x^i)
X1 = 0b11            # x + 1
F1 = 0b1011          # x^3 + x + 1
F2 = 0b1101          # x^3 + x^2 + 1


def pmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


DIVISORS = sorted({pmul(pmul(a, b), c) for a in (1, X1) for b in (1, F1) for c in (1, F2)}, key=lambda d: (d.bit_length(), d))
assert pmul(pmul(X1, F1), F2) == (1 << 7) | 1


def deg(a: int) -> int:
    return a.bit_length() - 1


def pmod(a: int, b: int) -> int:
    db = deg(b)
    while a and deg(a) >= db:
        a ^= b << (deg(a) - db)
    return a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def plcm(a: int, b: int) -> int:
    g = pgcd(a, b)
    p = pmul(a, b)
    q = 0
    while p and deg(p) >= deg(g):
        s = deg(p) - deg(g)
        q |= 1 << s
        p ^= g << s
    return q


def irreducible(f: int) -> bool:
    """Rabin test for f over F_2 of degree N."""
    n = deg(f)

    def mulmod(a: int, b: int) -> int:
        return pmod(pmul(a, b), f)

    def xpow2k(k: int) -> int:
        x = 0b10
        for _ in range(k):
            x = mulmod(x, x)
        return x

    if xpow2k(n) != 0b10:
        return False
    for p in {p for p in range(2, n + 1) if n % p == 0 and all(p % r for r in range(2, p))}:
        if deg(pgcd(f, xpow2k(n // p) ^ 0b10)) > 0:
            return False
    return True


def modulus(n: int) -> int:
    """Lowest-weight, then smallest, irreducible polynomial of degree n (trinomials first)."""
    for weight in (3, 5):
        cands = []
        if weight == 3:
            cands = [(1 << n) | (1 << k) | 1 for k in range(1, n)]
        else:
            cands = [(1 << n) | (1 << a) | (1 << b) | (1 << c) | 1 for a in range(3, n) for b in range(2, a) for c in range(1, b)]
        for f in sorted(cands):
            if irreducible(f):
                return f
    raise ValueError("no modulus")


def census(l: int) -> dict:
    t0 = time.time()
    n = 7 * l
    q = 1 << l
    f = modulus(n)

    def sq(a: int) -> int:
        return pmod(pmul(a, a), f)

    def frob(a: int) -> int:
        for _ in range(l):
            a = sq(a)
        return a

    # sigma is F_2-linear: tabulate it on bytes of the input
    nbytes = (n + 7) // 8
    tables = []
    for k in range(nbytes):
        tab = [0] * 256
        for v in range(256):
            tab[v] = frob(v << (8 * k)) if (v << (8 * k)) < (1 << n) else 0
        tables.append(tab)

    def sigma(a: int) -> int:
        r = 0
        k = 0
        while a:
            r ^= tables[k][a & 0xFF]
            a >>= 8
            k += 1
        return r

    const = 1 << n
    hist: dict[int, int] = {}
    ord_hist: dict[str, int] = {}
    mismatch = 0
    for b in range(1, 1 << n):
        orb = [b]
        for _ in range(6):
            orb.append(sigma(orb[-1]))
        assert sigma(orb[-1]) == b, "sigma^7 is the identity on K"
        basis: list[int] = []
        for v in orb:
            w = v | const
            for e in basis:
                w = min(w, w ^ e)
            if w:
                basis.append(w)
        m = len(basis)
        hist[m] = hist.get(m, 0) + 1
        ordb = None
        for d in DIVISORS:
            acc = 0
            for i in range(8):
                if d >> i & 1:
                    acc ^= orb[i % 7]
            if acc == 0:
                ordb = d
                break
        assert ordb is not None
        ord_hist[bin(ordb)[2:]] = ord_hist.get(bin(ordb)[2:], 0) + 1
        if deg(plcm(ordb, X1)) != m:
            mismatch += 1
    predicted = {1: q - 1, 4: 2 * q ** 4 - 2 * q, 7: q ** 7 - 2 * q ** 4 + q}
    return {"rec": "char2_magic", "l": l, "N": n, "q": q, "modulus_bits": bin(f)[2:], "elements": (1 << n) - 1,
            "m_hist": {str(k): v for k, v in sorted(hist.items())},
            "m_hist_predicted": {str(k): v for k, v in sorted(predicted.items())},
            "matches_prediction": hist == predicted,
            "ord_b_hist": dict(sorted(ord_hist.items())),
            "m_equals_deg_lcm_ord_b_x_plus_1_mismatches": mismatch,
            "wall_s": round(time.time() - t0, 2)}


if __name__ == "__main__":
    for arg in sys.argv[1:] or ["1", "2", "3"]:
        print(json.dumps(census(int(arg)), sort_keys=True), flush=True)
