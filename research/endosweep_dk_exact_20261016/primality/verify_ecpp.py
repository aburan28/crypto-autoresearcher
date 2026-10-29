#!/usr/bin/env python3
"""Independent checker for the ECPP primality certificates in this directory.

It shares no code with PARI/GP and does not call it.  Standard library only.

WHAT A CERTIFICATE IS
---------------------
`certificates/<N>.json` holds `{"N": "...", "kind": "ecpp", "steps": [...]}` or
`{"N": "...", "kind": "small"}`.  Each ECPP step is PARI's
`[N, t, s, a4, [x, y]]` (`primecert(N)`, flag 0), all integers as decimal
strings.  The step asserts: on `E: y^2 = x^3 + a4*x + b (mod N)`, with `b`
determined by the point, the integer `m = N + 1 - t` factors as `m = s*q`, and
the point `P = (x, y)` witnesses that `q` is the order of `[s]P`.

THE THEOREM EACH STEP USES (Goldwasser-Kilian, in Atkin-Morain's form)
----------------------------------------------------------------------
Let `N > 1` with `gcd(N, 6) = 1`, `E/Z_N` a short Weierstrass curve with
`gcd(4a^3 + 27b^2, N) = 1`, `P` a point on `E`, `m = s*q` with `q` PRIME and
`q > (N^(1/4) + 1)^2`.  If `[s]P` is an affine point mod `N` (every
denominator met while computing it is a unit) and `[q]([s]P) = O`, then `N` is
prime.  Proof: a prime `l | N` with `l <= sqrt(N)` would give a point of exact
order `q` on the nonsingular `E mod l` (it is not `O` mod `l`, because it is
affine mod `N`), so `q <= #E(F_l) <= (sqrt(l) + 1)^2 <= (N^(1/4) + 1)^2`
by Hasse, contradicting the size condition.

HOW `[q]Q = O` IS CHECKED.  The checker computes `[q-1]Q` by double-and-add
in affine coordinates and refuses ANY non-invertible denominator; then it
requires `[q-1]Q = -Q` exactly mod `N`.  Mod every prime `l | N` that is
`[q]Q = O`.  Refusing a hit of `O` part way through is stricter than the
theorem needs and loses nothing for prime `N`: there `Q` has prime order `q`,
so no partial sum `[i]Q + [j]Q` with `0 < i, j` and `i + j < q` is `O`.

The chain is followed to its last `q`, which is proved prime by a Pratt
(Lucas) certificate built here from a full factorisation of `q - 1`; the
factors are proved prime recursively, down to trial division below `10^6`.
A Pollard rho is used only to FIND factors.  Every factor it finds is checked
by multiplication and by its own recursive proof, so a rho mistake cannot
yield a false verdict.

The size condition is checked in exact integers:
`q > (N^(1/4) + 1)^2  <=>  L := q^2 + 6q + 1 - N > 0  and  L^2 > 16 q (q+1)^2`
(expand `(sqrt(q) - 1)^4 > N`).

Usage:  python3 verify_ecpp.py [CERT.json ...]   (default: every certificate)
Exit status 0 iff every certificate checked is valid.
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIAL_LIMIT = 10**6


class Invalid(Exception):
    pass


# ---------------------------------------------------------------- small primes
def is_prime_trial(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    r = math.isqrt(n)
    f = 3
    while f <= r:
        if n % f == 0:
            return False
        f += 2
    return True


def _probably_prime(n: int) -> bool:
    """Used ONLY to decide when to stop splitting in `factor`; never a verdict."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _rho(n: int, rng: random.Random) -> int:
    if n % 2 == 0:
        return 2
    while True:
        c = rng.randrange(1, n)
        f = lambda v: (v * v + c) % n
        x = y = rng.randrange(2, n)
        d = 1
        while d == 1:
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d


def factor(n: int, rng: random.Random) -> dict[int, int]:
    """Complete factorisation; correctness is re-checked by the caller."""
    out: dict[int, int] = {}
    stack = [n]
    while stack:
        m = stack.pop()
        if m == 1:
            continue
        if m < TRIAL_LIMIT or _probably_prime(m):
            if m < TRIAL_LIMIT:
                # split small cofactors completely by trial division
                f = 2
                while f * f <= m:
                    while m % f == 0:
                        out[f] = out.get(f, 0) + 1
                        m //= f
                    f += 1
                if m > 1:
                    out[m] = out.get(m, 0) + 1
            else:
                out[m] = out.get(m, 0) + 1
            continue
        d = _rho(m, rng)
        stack += [d, m // d]
    return out


def prove_prime_pratt(n: int, rng: random.Random, depth: int = 0) -> None:
    """Raise `Invalid` unless `n` is proved prime (trial division or Lucas)."""
    if depth > 64:
        raise Invalid("Pratt recursion too deep")
    if n < TRIAL_LIMIT:
        if not is_prime_trial(n):
            raise Invalid(f"{n} is not prime (trial division)")
        return
    fac = factor(n - 1, rng)
    prod = 1
    for p, e in fac.items():
        prod *= p**e
    if prod != n - 1:
        raise Invalid(f"factorisation of {n}-1 does not multiply back")
    for p in fac:
        prove_prime_pratt(p, rng, depth + 1)
    # Lucas: some a of order exactly n-1 in (Z/n)^*
    for a in range(2, 2000):
        if pow(a, n - 1, n) != 1:
            raise Invalid(f"{n} fails Fermat to base {a}: composite")
        if all(pow(a, (n - 1) // p, n) != 1 for p in fac):
            return
    raise Invalid(f"no Lucas witness found for {n} below 2000")


# ------------------------------------------------------------ curve arithmetic
def inv(v: int, n: int) -> int:
    v %= n
    if math.gcd(v, n) != 1:
        raise Invalid("non-invertible denominator")
    return pow(v, -1, n)


def ec_add(P, Q, a: int, n: int):
    """Strict affine addition; `None` is never an input or an output."""
    x1, y1 = P
    x2, y2 = Q
    if (x1 - x2) % n == 0:
        if (y1 - y2) % n != 0:
            raise Invalid("hit the point at infinity part way through")
        lam = (3 * x1 * x1 + a) * inv(2 * y1, n) % n
    else:
        lam = (y2 - y1) * inv(x2 - x1, n) % n
    x3 = (lam * lam - x1 - x2) % n
    return x3, (lam * (x1 - x3) - y1) % n


def ec_mul(k: int, P, a: int, n: int):
    if k < 1:
        raise Invalid("scalar must be positive")
    R = None
    for bit in bin(k)[2:]:
        if R is not None:
            R = ec_add(R, R, a, n)
        if bit == "1":
            R = P if R is None else ec_add(R, P, a, n)
    return R


def size_condition(q: int, N: int) -> bool:
    """Exact `q > (N^(1/4) + 1)^2`."""
    L = q * q + 6 * q + 1 - N
    return q > 1 and L > 0 and L * L > 16 * q * (q + 1) ** 2


def check_step(step) -> int:
    """Verify one step and return the `q` it reduces primality of `N` to."""
    N, t, s, a, (x, y) = int(step[0]), int(step[1]), int(step[2]), int(step[3]), step[4]
    x, y = int(x), int(y)
    if N < 5 or math.gcd(N, 6) != 1:
        raise Invalid("N must exceed 3 and be coprime to 6")
    m = N + 1 - t
    if s < 1 or m <= 0 or m % s:
        raise Invalid("s does not divide m = N + 1 - t")
    q = m // s
    if not size_condition(q, N):
        raise Invalid("q <= (N^(1/4) + 1)^2")
    a %= N
    b = (y * y - x * x * x - a * x) % N
    if math.gcd((4 * a**3 + 27 * b * b) % N, N) != 1:
        raise Invalid("curve is singular modulo a factor of N")
    Q = ec_mul(s, (x % N, y % N), a, N)
    R = ec_mul(q - 1, Q, a, N)
    if not ((R[0] - Q[0]) % N == 0 and (R[1] + Q[1]) % N == 0):
        raise Invalid("[q]([s]P) != O")
    return q


def check_certificate(cert: dict, rng: random.Random) -> dict:
    N = int(cert["N"])
    if cert["kind"] == "small":
        prove_prime_pratt(N, rng)
        return {"N": str(N), "valid": True, "steps": 0, "final_q": str(N)}
    if cert["kind"] != "ecpp":
        raise Invalid(f"unknown kind {cert['kind']!r}")
    steps = cert["steps"]
    if not steps or int(steps[0][0]) != N:
        raise Invalid("first step is not for N")
    q = None
    for i, st in enumerate(steps):
        if q is not None and int(st[0]) != q:
            raise Invalid(f"step {i} does not continue the chain")
        q = check_step(st)
    prove_prime_pratt(q, rng)
    return {"N": str(N), "valid": True, "steps": len(steps), "final_q": str(q)}


def main(argv: list[str]) -> int:
    paths = [Path(p) for p in argv] or sorted((HERE / "certificates").glob("*.json"))
    rng = random.Random(20261029)
    bad = 0
    for p in paths:
        cert = json.loads(p.read_text())
        try:
            r = check_certificate(cert, rng)
            print(json.dumps({"file": p.name, **r}))
        except Invalid as e:
            bad += 1
            print(json.dumps({"file": p.name, "N": cert.get("N"), "valid": False, "reason": str(e)}))
    print(f"# {len(paths) - bad}/{len(paths)} certificates valid", file=sys.stderr)
    return 1 if bad or not paths else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
