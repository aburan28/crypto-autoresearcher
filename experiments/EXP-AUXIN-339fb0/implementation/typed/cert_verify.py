"""Independent certificate verifier for EXP-AUXIN-339fb0.

Library-free: Python standard library ONLY (AST-audited at admission).
Shares no code with PARI, GMP-ECM, FLINT, pypdf or sympy.

Checks (per change.D7_certificates.independent_verifier):
  (i)   Pratt certificates
  (ii)  ECPP steps (Goldwasser-Kilian / Atkin-Morain) with gcd(N, 6)=1
  (iii) Compositeness witnesses via strong probable-prime failure

Version of this module at launch is the sha256 of its bytes.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

CertDict = Dict[str, Any]
VerifyResult = Tuple[bool, List[str]]


def _gcd(a: int, b: int) -> int:
    return math.gcd(int(a), int(b))


def _iroot4(n: int) -> int:
    """Least integer c with c**4 >= n is not this; return floor(n**(1/4))."""
    if n < 0:
        raise ValueError("iroot4 of negative")
    if n == 0:
        return 0
    r = int(math.isqrt(math.isqrt(n)))
    while (r + 1) ** 4 <= n:
        r += 1
    while r > 0 and r**4 > n:
        r -= 1
    return r


def strong_prp(n: int, a: int) -> bool:
    """Strong probable-prime test of odd n > 2 to base a (1 < a < n)."""
    n = int(n)
    a = int(a) % n
    if n < 3 or n % 2 == 0:
        return False
    if a <= 1 or a >= n:
        return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(s - 1):
        x = (x * x) % n
        if x == n - 1:
            return True
    return False


def verify_compositeness_witness(n: int, a: Union[int, str]) -> VerifyResult:
    """(iii) Compositeness witness.

    Odd composite: recorded base a is the smallest a >= 2 for which n fails
    the strong PRP test to base a; verifier re-runs that strong test.
    Even composite: witness is the string \"even\" (or integer 2 recorded as even).
    """
    n = int(n)
    detail: List[str] = []
    if n < 4:
        return False, [f"n={n} too small for compositeness witness"]
    if n % 2 == 0:
        if a == "even" or a == 2 or str(a) == "even":
            detail.append("even composite accepted")
            return True, detail
        return False, [f"even n requires witness 'even', got {a!r}"]
    try:
        base = int(a)
    except (TypeError, ValueError):
        return False, [f"odd composite requires integer base a, got {a!r}"]
    if base < 2:
        return False, [f"base a={base} < 2"]
    # Smallest-base check: every 2 <= b < a must PASS strong PRP.
    for b in range(2, base):
        if not strong_prp(n, b):
            return False, [f"a={base} is not smallest; fails also at b={b}"]
    if strong_prp(n, base):
        return False, [f"n passes strong PRP to claimed witness a={base}"]
    detail.append(f"strong-PRP failure at a={base} (smallest)")
    return True, detail


def verify_pratt(cert: CertDict) -> VerifyResult:
    """(i) Pratt certificate.

    Required fields:
      kind: \"pratt\"
      p: the prime
      a: witness base
      factors: list of {p, e, cert?} where product p_i^e_i == p-1;
               each prime factor carries its own valid Pratt certificate
               (leaf 2 may omit nested cert).
    """
    detail: List[str] = []
    if not isinstance(cert, dict) or cert.get("kind") != "pratt":
        return False, ["not a Pratt certificate dict"]
    p = int(cert["p"])
    a = int(cert["a"])
    factors = cert.get("factors")
    if not isinstance(factors, list):
        return False, ["Pratt factors missing or not a list"]
    if p == 2:
        detail.append("leaf prime 2")
        return True, detail
    if not factors:
        return False, ["Pratt factors missing"]
    if p < 2 or p % 2 == 0:
        return False, [f"Pratt p={p} not an odd integer >= 3"]
    prod = 1
    for entry in factors:
        f = int(entry["p"])
        e = int(entry["e"])
        if f < 2 or e < 1:
            return False, [f"bad factor {f}^{e}"]
        prod *= f**e
    if prod != p - 1:
        return False, [f"factor product {prod} != p-1={p - 1}"]
    if pow(a, p - 1, p) != 1:
        return False, [f"a^(p-1) != 1 mod p (a={a}, p={p})"]
    for entry in factors:
        f = int(entry["p"])
        if pow(a, (p - 1) // f, p) == 1:
            return False, [f"a^((p-1)/{f}) == 1 mod p"]
        if f == 2:
            continue
        nested = entry.get("cert")
        if nested is None:
            return False, [f"missing nested Pratt cert for factor {f}"]
        ok, sub = verify_pratt(nested)
        detail.extend(sub)
        if not ok:
            return False, detail + [f"nested Pratt failed for {f}"]
        if int(nested.get("p", -1)) != f:
            return False, [f"nested cert p={nested.get('p')} != factor {f}"]
    detail.append(f"Pratt ok for p={p} ({p.bit_length()} bits)")
    return True, detail


def _ec_add(
    P1: Optional[Tuple[int, int, int]],
    P2: Optional[Tuple[int, int, int]],
    a4: int,
    n: int,
) -> Optional[Tuple[int, int, int]]:
    """Projective addition on y^2 = x^3 + a4*x + b over Z/nZ."""
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    X1, Y1, Z1 = P1
    X2, Y2, Z2 = P2
    U1 = (X1 * Z2) % n
    U2 = (X2 * Z1) % n
    S1 = (Y1 * Z2) % n
    S2 = (Y2 * Z1) % n
    if U1 == U2:
        if (S1 + S2) % n == 0:
            return None
        return _ec_dbl(P1, a4, n)
    H = (U2 - U1) % n
    R = (S2 - S1) % n
    W = (Z1 * Z2) % n
    HH = (H * H) % n
    HHH = (HH * H) % n
    V = (U1 * HH) % n
    A = (R * R * W - HHH - 2 * V) % n
    X3 = (H * A) % n
    Y3 = (R * (V - A) - S1 * HHH) % n
    Z3 = (HHH * W) % n
    return (X3, Y3, Z3)


def _ec_dbl(
    P1: Optional[Tuple[int, int, int]], a4: int, n: int
) -> Optional[Tuple[int, int, int]]:
    if P1 is None:
        return None
    X1, Y1, Z1 = P1
    if Y1 % n == 0:
        return None
    W = (a4 * Z1 * Z1 + 3 * X1 * X1) % n
    S = (Y1 * Z1) % n
    B = (X1 * Y1 * S) % n
    H = (W * W - 8 * B) % n
    X3 = (2 * H * S) % n
    Y3 = (W * (4 * B - H) - 8 * Y1 * Y1 * S * S) % n
    Z3 = (8 * S * S * S) % n
    return (X3, Y3, Z3)


def _ec_mul(
    k: int, Pt: Tuple[int, int, int], a4: int, n: int
) -> Optional[Tuple[int, int, int]]:
    R: Optional[Tuple[int, int, int]] = None
    for bit in bin(int(k))[2:]:
        R = _ec_dbl(R, a4, n)
        if bit == "1":
            R = _ec_add(R, Pt, a4, n)
    return R


def verify_ecpp_step(step: Dict[str, Any], expected_N: Optional[int] = None) -> VerifyResult:
    """(ii) One ECPP step with (N, t, s, a4, P=(x,y))."""
    detail: List[str] = []
    N = int(step["N"])
    t = int(step["t"])
    s = int(step["s"])
    a4 = int(step["a4"])
    P = step["P"]
    x, y = int(P[0]), int(P[1])
    if expected_N is not None and N != expected_N:
        return False, [f"chain break: expected N={expected_N}, got {N}"]
    if _gcd(N, 6) != 1:
        return False, [f"gcd(N, 6) != 1 for N={N}"]
    m = N + 1 - t
    if s == 0 or m % s != 0:
        return False, [f"s does not divide m at N={N}"]
    q = m // s
    b = (y * y - x * x * x - a4 * x) % N
    disc = (4 * a4 * a4 * a4 + 27 * b * b) % N
    if _gcd(disc, N) != 1:
        return False, [f"singular curve disc at N={N}"]
    c = _iroot4(N)
    # least integer c with c^4 >= N; _iroot4 returns floor; bump if needed
    if c**4 < N:
        c += 1
    if not (q > (c + 1) ** 2):
        return False, [f"q <= (c+1)^2 at N={N}"]
    Pt = (x, y, 1)
    sP = _ec_mul(s, Pt, a4, N)
    if sP is None:
        return False, [f"[s]P is infinity at N={N}"]
    if _gcd(sP[2], N) != 1:
        return False, [f"[s]P denominators not invertible at N={N}"]
    mP = _ec_mul(m, Pt, a4, N)
    if mP is not None and _gcd(mP[2], N) == 1:
        return False, [f"[m]P is not infinity at N={N}"]
    detail.append(f"ECPP step N={N.bit_length()}-bit ok -> q={q.bit_length()}-bit")
    return True, detail + [str(q)]


def verify_ecpp(cert: CertDict) -> VerifyResult:
    """ECPP chain: list of steps; terminal q carries a valid Pratt certificate."""
    detail: List[str] = []
    if not isinstance(cert, dict) or cert.get("kind") != "ecpp":
        return False, ["not an ECPP certificate dict"]
    steps = cert.get("steps")
    if not isinstance(steps, Sequence) or not steps:
        return False, ["ECPP steps missing"]
    expected_N: Optional[int] = None
    q: Optional[int] = None
    for step in steps:
        ok, sub = verify_ecpp_step(step, expected_N)
        if not ok:
            return False, detail + sub
        # last element of sub is q as string when ok
        q = int(sub[-1])
        detail.extend(sub[:-1])
        expected_N = q
    terminal = cert.get("terminal")
    if terminal is None:
        return False, detail + ["missing terminal Pratt certificate"]
    if q is None:
        return False, detail + ["empty ECPP chain"]
    if int(terminal.get("p", -1)) != q:
        return False, detail + [f"terminal Pratt p={terminal.get('p')} != q={q}"]
    ok, sub = verify_pratt(terminal)
    detail.extend(sub)
    if not ok:
        return False, detail + ["terminal Pratt failed"]
    detail.append("ECPP chain accepted")
    return True, detail


def verify_certificate(cert: CertDict) -> VerifyResult:
    """Dispatch on cert['kind']: pratt | ecpp | compositeness."""
    if not isinstance(cert, dict):
        return False, ["certificate is not a dict"]
    kind = cert.get("kind")
    if kind == "pratt":
        return verify_pratt(cert)
    if kind == "ecpp":
        return verify_ecpp(cert)
    if kind == "compositeness":
        return verify_compositeness_witness(int(cert["n"]), cert["a"])
    return False, [f"unknown certificate kind {kind!r}"]


def make_pratt_leaf_two() -> CertDict:
    return {"kind": "pratt", "p": 2, "a": 1, "factors": []}


def build_pratt_for_small_prime(p: int) -> Optional[CertDict]:
    """Construct a Pratt certificate for a small prime by exhaustive search.

    Used by packaging self-checks and admission scaffolding. Returns None if
    factorization of p-1 is incomplete under trial division (p too large).
    """
    p = int(p)
    if p == 2:
        return make_pratt_leaf_two()
    if p < 3:
        return None
    # Factor p-1 by trial division.
    n = p - 1
    factors: List[Tuple[int, int]] = []
    twos = 0
    while n % 2 == 0:
        n //= 2
        twos += 1
    if twos:
        factors.append((2, twos))
    f = 3
    while f * f <= n:
        e = 0
        while n % f == 0:
            n //= f
            e += 1
        if e:
            factors.append((f, e))
        f += 2
    if n > 1:
        factors.append((n, 1))
    # Find smallest witness a.
    factor_primes = [fp for fp, _ in factors]
    a = 2
    while a < p:
        if pow(a, p - 1, p) == 1 and all(
            pow(a, (p - 1) // fp, p) != 1 for fp in factor_primes
        ):
            break
        a += 1
    else:
        return None
    entries = []
    for fp, e in factors:
        entry: Dict[str, Any] = {"p": fp, "e": e}
        if fp != 2:
            nested = build_pratt_for_small_prime(fp)
            if nested is None:
                return None
            entry["cert"] = nested
        entries.append(entry)
    return {"kind": "pratt", "p": p, "a": a, "factors": entries}
