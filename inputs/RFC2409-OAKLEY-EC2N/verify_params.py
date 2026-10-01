#!/usr/bin/env python3
"""Re-derive every structural fact about RFC 2409's EC2N groups from the frozen text.

Pure Python, no dependencies, a few seconds. Reads the parameters OUT OF
rfc2409.txt rather than carrying its own copy of them, so that a change to the
frozen text is caught here rather than silently trusted.

What it establishes, per group:
  * the field polynomial is irreducible over F_2;
  * the extension degree factors as 5 * (prime), so F_{2^m} is a QUINTIC
    extension of F_{2^31} (group 3) or F_{2^37} (group 4);
  * Generator One lifts to a point on the stated curve;
  * the stated Group Order N kills that point, and h = 1 is the only cofactor
    with h*N in the Hasse interval -- so the RFC's "Group Order" is #E itself;
  * #E = cofactor * r with r prime, giving the actual DLP subgroup size.

Everything printed is a computation over the frozen bytes. Nothing here is
recalled from memory about these curves, and nothing here bears on whether any
attack on them succeeds.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
RFC = HERE / "rfc2409.txt"


# ----------------------------------------------------------------------------
# F_2[u] / (f) arithmetic on Python ints
# ----------------------------------------------------------------------------
def gf_mul(a: int, b: int, mod: int, m: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> m:
            a ^= mod
    return r


def gf_pow(a: int, e: int, mod: int, m: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = gf_mul(r, a, mod, m)
        a = gf_mul(a, a, mod, m)
        e >>= 1
    return r


def gf_inv(a: int, mod: int, m: int) -> int:
    return gf_pow(a, (1 << m) - 2, mod, m)


def poly_mod(a: int, f: int) -> int:
    df = f.bit_length() - 1
    while a and a.bit_length() - 1 >= df:
        a ^= f << (a.bit_length() - 1 - df)
    return a


def poly_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, poly_mod(a, b)
    return a


def prime_factors(n: int) -> list[int]:
    out, p = [], 2
    while p * p <= n:
        while n % p == 0:
            out.append(p)
            n //= p
        p += 1
    if n > 1:
        out.append(n)
    return out


def is_irreducible(f: int, m: int) -> bool:
    """Rabin's test: u^(2^m) = u mod f, and gcd(u^(2^(m/p)) - u, f) = 1 for prime p | m."""
    def frob(a: int, k: int) -> int:
        for _ in range(k):
            a = gf_mul(a, a, f, m)
        return a
    if frob(2, m) != 2:
        return False
    return all(poly_gcd(frob(2, m // p) ^ 2, f) == 1 for p in set(prime_factors(m)))


# ----------------------------------------------------------------------------
# E: y^2 + xy = x^3 + a x^2 + b over F_{2^m}
# ----------------------------------------------------------------------------
def trace(a: int, mod: int, m: int) -> int:
    t, acc = a, 0
    for _ in range(m):
        acc ^= t
        t = gf_mul(t, t, mod, m)
    return acc


def half_trace(a: int, mod: int, m: int) -> int:
    """For odd m, z with z^2 + z = a when Tr(a) = 0: z = sum_{i=0}^{(m-1)/2} a^(2^(2i))."""
    z, t = 0, a
    for _ in range((m - 1) // 2 + 1):
        z ^= t
        t = gf_mul(t, t, mod, m)
        t = gf_mul(t, t, mod, m)
    return z


def lift_x(x: int, a: int, b: int, mod: int, m: int) -> tuple[int, int] | None:
    """y = x z where z^2 + z = x + a + b / x^2."""
    x2 = gf_mul(x, x, mod, m)
    rhs = x ^ a ^ gf_mul(b, gf_inv(x2, mod, m), mod, m)
    if trace(rhs, mod, m):
        return None
    return (x, gf_mul(x, half_trace(rhs, mod, m), mod, m))


def on_curve(P, a: int, b: int, mod: int, m: int) -> bool:
    x, y = P
    lhs = gf_mul(y, y, mod, m) ^ gf_mul(x, y, mod, m)
    x2 = gf_mul(x, x, mod, m)
    return lhs == gf_mul(x2, x, mod, m) ^ gf_mul(a, x2, mod, m) ^ b


def ec_add(P, Q, a: int, mod: int, m: int):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if x1 == 0 or (y1 ^ y2) == x1:      # Q = -P, since -(x, y) = (x, x + y)
            return None
        lam = x1 ^ gf_mul(y1, gf_inv(x1, mod, m), mod, m)
        x3 = gf_mul(lam, lam, mod, m) ^ lam ^ a
        y3 = gf_mul(x1, x1, mod, m) ^ gf_mul(lam ^ 1, x3, mod, m)
        return (x3, y3)
    lam = gf_mul(y1 ^ y2, gf_inv(x1 ^ x2, mod, m), mod, m)
    x3 = gf_mul(lam, lam, mod, m) ^ lam ^ x1 ^ x2 ^ a
    y3 = gf_mul(lam, x1 ^ x3, mod, m) ^ x3 ^ y1
    return (x3, y3)


def ec_mul(k: int, P, a: int, mod: int, m: int):
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, a, mod, m)
        P = ec_add(P, P, a, mod, m)
        k >>= 1
    return R


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


# ----------------------------------------------------------------------------
# Parse the frozen RFC
# ----------------------------------------------------------------------------
def parse_groups(text: str) -> dict[int, dict]:
    groups = {}
    for gid, heading in ((3, "6.3 Third Oakley Group"), (4, "6.4 Fourth Oakley Group")):
        i = text.rindex(heading)          # the TOC lists it first; the body is the LAST occurrence
        block = text[i:i + 2500]
        m = int(re.search(r"Field Size:\s+(\d+)", block).group(1))
        poly = re.search(r"irreducible polynomial for the field is:\s*\n?\s*u\^(\d+) \+ u\^(\d+) \+ 1", block)
        mod = (1 << int(poly.group(1))) | (1 << int(poly.group(2))) | 1
        hexpoly = int(re.search(r"Group Prime/Irreducible Polynomial:\s*\n\s*(0x[0-9a-fA-F]+)", block).group(1), 16)
        assert hexpoly == mod, f"group {gid}: hex polynomial disagrees with u^{poly.group(1)}+u^{poly.group(2)}+1"
        groups[gid] = dict(
            m=m, mod=mod,
            trinomial=(int(poly.group(1)), int(poly.group(2))),
            gx=int(re.search(r"Group Generator One:\s+(0x[0-9a-fA-F]+)", block).group(1), 16),
            a=int(re.search(r"Group Curve A:\s+(0x[0-9a-fA-F]+)", block).group(1), 16),
            b=int(re.search(r"Group Curve B:\s+(0x[0-9a-fA-F]+)", block).group(1), 16),
            order=int(re.search(r"Group Order:\s+(0[xX][0-9a-fA-F]+)", block).group(1), 16),
        )
    return groups


def main() -> int:
    text = RFC.read_text(encoding="utf-8", errors="replace")
    digest = hashlib.sha256(RFC.read_bytes()).hexdigest()
    pinned = (HERE / "rfc2409.txt.sha256").read_text().split()[0]
    print(f"rfc2409.txt sha256 {digest}  pinned: {'MATCH' if digest == pinned else 'MISMATCH'}")
    if digest != pinned:
        return 2

    ok = True
    for gid, g in parse_groups(text).items():
        m, mod, a, b, N = g["m"], g["mod"], g["a"], g["b"], g["order"]
        pf = prime_factors(m)
        big = max(pf)
        print(f"\n== Oakley Group {gid}: E/F_2^{m}, f = u^{m}+u^{g['trinomial'][1]}+1, a = {a}, b = {hex(b)}")
        irr = is_irreducible(mod, m)
        print(f"   field polynomial irreducible ........ {irr}")
        print(f"   {m} = {'*'.join(map(str, pf))}  ->  [F_2^{m} : F_2^{big}] = {m // big}")
        P = lift_x(g["gx"], a, b, mod, m)
        onc = P is not None and on_curve(P, a, b, mod, m)
        print(f"   Generator One lifts to a curve point . {onc}")
        kills = P is not None and ec_mul(N, P, a, mod, m) is None
        print(f"   stated Group Order * P == O .......... {kills}")
        lo = (1 << m) + 1 - 2 * int(2 ** (m / 2))
        hi = (1 << m) + 1 + 2 * int(2 ** (m / 2))
        hs = [h for h in range(1, 17) if lo <= h * N <= hi]
        print(f"   cofactors h with h*N in Hasse range .. {hs}  (h = 1 means N is #E)")
        small, r = [], N
        for p in range(2, 10 ** 5):
            while r % p == 0:
                small.append(p)
                r //= p
            if p * p > r:
                break
        rp = is_probable_prime(r)
        print(f"   #E = {'*'.join(map(str, small))} * r,  r is {r.bit_length()} bits, prime: {rp}")
        print(f"   r = {hex(r)}")
        print(f"   b in F_2 (Koblitz)? .................. {b in (0, 1)}")
        ok &= irr and onc and kills and hs == [1] and rp and (m // big == 5)

    print(f"\nALL CHECKS {'PASSED' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
