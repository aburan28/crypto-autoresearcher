"""Stage 0: Moebius Phi_k(2) census and Phi_130(2) factorisation.

Pure-Python arithmetic. Census uses Moebius + v_p(2^d-1) (modular), not the
recalled cyclotomic-divisor lemma — that lemma is what the census tests.
"""
from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple


def mobius_sieve(n: int) -> List[int]:
    """mu[0]=0, mu[1..n] = Moebius function."""
    mu = [0] + [1] * n
    primes: List[int] = []
    is_comp = [False] * (n + 1)
    for i in range(2, n + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            ip = i * p
            if ip > n:
                break
            is_comp[ip] = True
            if i % p == 0:
                mu[ip] = 0
                break
            mu[ip] = -mu[i]
    return mu


def divisors_of(k: int) -> List[int]:
    out: List[int] = []
    r = int(math.isqrt(k))
    for d in range(1, r + 1):
        if k % d == 0:
            out.append(d)
            if d * d != k:
                out.append(k // d)
    out.sort()
    return out


def euler_phi(k: int) -> int:
    result = k
    n = k
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1 if p == 2 else 2
    if n > 1:
        result -= result // n
    return result


def v_p_of_2d_minus_1(d: int, p: int) -> int:
    """v_p(2^d - 1) via modular lifting (no cyclotomic-divisor lemma)."""
    if pow(2, d, p) != 1:
        return 0
    v = 1
    pe = p * p
    # Cap: for p=131 and d<=20000, valuation stays tiny
    while v < 64 and pow(2, d, pe) == 1:
        v += 1
        pe *= p
    return v


def phi_k_of_2(k: int, mu: Sequence[int]) -> int:
    """Exact Phi_k(2) = prod_{d|k} (2^d - 1)^{mu(k/d)} (num/den form)."""
    num = 1
    den = 1
    for d in divisors_of(k):
        m = mu[k // d]
        if m == 0:
            continue
        term = (1 << d) - 1
        if m == 1:
            num *= term
        else:
            den *= term
    if num % den != 0:
        raise ArithmeticError(
            f"Phi_{k}(2) Moebius product not integral: num%den={num % den}"
        )
    return num // den


def v_p_phi_k_of_2(k: int, p: int, mu: Sequence[int]) -> int:
    """v_p(Phi_k(2)) via Moebius sum of v_p(2^d-1)."""
    v = 0
    for d in divisors_of(k):
        m = mu[k // d]
        if m == 0:
            continue
        v += m * v_p_of_2d_minus_1(d, p)
    return v


def cyclotomic_divisor_set(p: int, k_max: int, mu: Sequence[int] | None = None) -> List[int]:
    """Return sorted {k <= k_max : p divides Phi_k(2)}."""
    if mu is None:
        mu = mobius_sieve(k_max)
    hits: List[int] = []
    for k in range(1, k_max + 1):
        if v_p_phi_k_of_2(k, p, mu) > 0:
            hits.append(k)
    return hits


def phi_130_factorisation() -> Dict[str, object]:
    """Exact Phi_130(2) value, cofactor, v_131, and 2^65+1 cross-check."""
    mu = mobius_sieve(130)
    value = phi_k_of_2(130, mu)
    expected = 409368176241571
    two65p1 = (1 << 65) + 1
    denom = 8193 * 11
    cross = two65p1 // denom
    cross_ok = two65p1 == cross * denom and cross == value

    p = 131
    v = 0
    tmp = value
    while tmp % p == 0:
        tmp //= p
        v += 1
    cofactor = tmp
    expected_cofactor = 3124947910241
    return {
        "Phi_130_of_2": value,
        "expected_Phi_130": expected,
        "value_matches_expected": value == expected,
        "cofactor": cofactor,
        "expected_cofactor": expected_cofactor,
        "cofactor_matches_expected": cofactor == expected_cofactor,
        "v_131": v,
        "expected_v_131": 1,
        "crosscheck_2_65_plus_1": {
            "formula": "(2^65+1)/(8193*11)",
            "numerator": two65p1,
            "denominator": denom,
            "quotient": cross,
            "ok": cross_ok,
        },
        "product_check": (value == p * cofactor) if v == 1 else None,
        "moebius_valuation_check": v_p_phi_k_of_2(130, p, mu) == v,
    }


def run_stage0(k_max: int = 20000) -> Dict[str, object]:
    mu = mobius_sieve(k_max)
    hits_131 = cyclotomic_divisor_set(131, k_max, mu)
    hits_17 = cyclotomic_divisor_set(17, k_max, mu)
    phi_vals = {k: euler_phi(k) for k in hits_131}
    fac = phi_130_factorisation()
    unexpected = [k for k in hits_131 if k not in (130, 17030)]
    return {
        "k_max": k_max,
        "hits_p131": hits_131,
        "expected_p131": [130, 17030],
        "p131_match": hits_131 == [130, 17030],
        "phi_values": phi_vals,
        "expected_phi": {130: 48, 17030: 6240},
        "phi_match": phi_vals.get(130) == 48 and phi_vals.get(17030) == 6240,
        "hits_p17": hits_17,
        "expected_p17": [8, 136, 2312],
        "p17_match": hits_17 == [8, 136, 2312],
        "Phi_130_factorisation": fac,
        "unexpected_k_inspection": unexpected,
        "unexpected_k_notes": (
            "none — set matches preregistered {130,17030}"
            if not unexpected
            else "UNEXPECTED k present; inspect Moebius/bug before outcome C"
        ),
    }


if __name__ == "__main__":
    import json
    import time

    t0 = time.time()
    out = run_stage0(20000)
    out["wall_s"] = time.time() - t0
    print(json.dumps(out, indent=2, default=str))
