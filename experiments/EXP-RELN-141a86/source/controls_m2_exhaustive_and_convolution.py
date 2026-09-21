"""
INV-7 (m=2 x-class exact law) and INV-8 (semiregular degree, integer
convolution) control tables for EXP-RELN-141a86 Stage 0b, plus INV-A4
(Bose-Chowla B_3 Sidon floor).

INV-7 realization note (protocol_deviation, recorded in implementation.md):
the x-class convention (V a random B-subset of the n=(N-1)/2 x-classes of a
prime-order curve, loop counted) is realized DIRECTLY in Z/N combinatorics
rather than by constructing an actual elliptic curve: an x-class is exactly
the orbit {r, -r mod N} of the point-negation involution, which is the same
structure whether or not the group is literally an EC point group. N is
generated as an actual random prime of the requested bit size (so "N" is a
genuine prime, matching "prime-order curve" for every arithmetic purpose
this control tests), and discrete logs are trivially known (we are working
directly in the log/index group Z/N, exactly as EXP-FB3-001's own committed
cells do -- "discrete logs known by construction for measurement only").
The only thing NOT constructed is the actual (x,y) coordinate embedding,
which is irrelevant to this control's combinatorics: the closed-form target
1 - C(n-B,B)/C(n,B) is a statement about n=(N-1)/2 abstract classes only.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Prime generation (deterministic, seeded) -- no external dependency.
# ---------------------------------------------------------------------------

def _is_probable_prime(n: int, rounds: int = 40) -> bool:
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    rng = random.Random(str(("miller_rabin", n)))
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def random_prime(bits: int, seed_tag: str) -> int:
    """Deterministic (seeded) random prime with exactly `bits` bits."""
    rng = random.Random(str(("EXP-RELN-141a86", "random_prime", bits, seed_tag)))
    lo = 1 << (bits - 1)
    hi = (1 << bits) - 1
    while True:
        cand = rng.randrange(lo, hi + 1) | 1
        if _is_probable_prime(cand):
            return cand


# ---------------------------------------------------------------------------
# INV-7: x-class exhaustive m=2 control
# ---------------------------------------------------------------------------

def b0_of(N: int) -> int:
    return math.ceil((6 * N) ** (1.0 / 3.0))


def x_class_p_exist_closed_form(n: int, B: int) -> Fraction:
    """p_fail = C(n-B,B)/C(n,B); p_exist = 1 - p_fail. Returns p_exist exactly."""
    if B > n:
        return Fraction(1)
    if n - B < B:
        p_fail = Fraction(0)
    else:
        p_fail = Fraction(math.comb(n - B, B), math.comb(n, B))
    return Fraction(1) - p_fail


def x_class_p_exist_exhaustive(n: int, N: int, B: int, draws: int, seed_tag: str,
                                target_r: int = 1) -> Tuple[float, int]:
    """
    200 (by default `draws`) independent random B-subsets V of {1,...,n}
    (the x-classes); for each, test whether target_r has a signed
    2-decomposition over V (loop counted): exists v1, v2 in V with
    v1+v2 == target_r, v1-v2 == target_r, or -v1-v2 == target_r (mod N)
    (v1==v2 allowed, "loop counted"). Returns (p_exist_hat, n_success).
    """
    rng = random.Random(str(("EXP-RELN-141a86", "INV7_xclass", n, N, B, seed_tag)))
    n_success = 0
    for i in range(draws):
        V = rng.sample(range(1, n + 1), B)
        Vset = set(V)
        found = False
        for v1 in V:
            # v1+v2 == r  => v2 == r - v1
            if (target_r - v1) % N in Vset or (-(target_r - v1)) % N in Vset:
                found = True
                break
            # v1-v2 == r => v2 == v1 - r
            if (v1 - target_r) % N in Vset or (-(v1 - target_r)) % N in Vset:
                found = True
                break
            # -v1-v2 == r => v2 == -r - v1
            if (-target_r - v1) % N in Vset or (-(-target_r - v1)) % N in Vset:
                found = True
                break
        if found:
            n_success += 1
    return n_success / draws, n_success


def build_inv7_table(bit_sizes: List[int], draws_per_cell: int = 200) -> List[Dict]:
    rows = []
    for bits in bit_sizes:
        N = random_prime(bits, seed_tag=f"bits{bits}")
        n = (N - 1) // 2
        B0 = b0_of(N)
        for label, B in [("half", max(1, round(B0 / 2))), ("B0", B0), ("double", 2 * B0)]:
            if B >= n:
                continue
            p_exist_cf = x_class_p_exist_closed_form(n, B)
            p_fail_cf = Fraction(1) - p_exist_cf
            p_exist_hat, n_success = x_class_p_exist_exhaustive(
                n, N, B, draws_per_cell, seed_tag=f"{bits}-{label}"
            )
            # binomial sampling SE of p_exist_hat under `draws_per_cell` draws
            p = float(p_exist_cf)
            se = math.sqrt(max(p * (1 - p), 1e-12) / draws_per_cell)
            rows.append({
                "bits": bits, "N": N, "n": n, "B": B, "B_ladder_label": label,
                "p_fail_closed_form": float(p_fail_cf),
                "p_exist_closed_form": float(p_exist_cf),
                "p_exist_exhaustive_hat": p_exist_hat,
                "n_success": n_success,
                "draws": draws_per_cell,
                "binomial_sampling_se": se,
                "agrees_within_sampling_se": abs(p_exist_hat - p) <= 4 * se,
                "abs_diff": abs(p_exist_hat - p),
                "diff_in_se": abs(p_exist_hat - p) / se if se > 0 else None,
            })
    return rows


# ---------------------------------------------------------------------------
# INV-8: semiregular degree via exact integer polynomial convolution
# ---------------------------------------------------------------------------

def poly_pow_mul(coeffs: List[int], m: int) -> List[int]:
    """Exact integer coefficients of coeffs(z)^m via repeated exact
    convolution (schoolbook, exact int arithmetic, no FFT rounding --
    degrees here are small, <= (B-1)*m ~ 260, so O(deg^2 * m) is fine)."""
    result = [1]
    for _ in range(m):
        new = [0] * (len(result) + len(coeffs) - 1)
        for i, a in enumerate(result):
            if a == 0:
                continue
            for j, b in enumerate(coeffs):
                new[i + j] += a * b
        result = new
    return result


def d_reg_via_convolution(m: int, B: int, D_S: int) -> int:
    """
    d_reg = index of the first non-positive coefficient of
    (1 + z + ... + z^(B-1))^m (1 - z^(D_S)), exact integer convolution.
    """
    base = [1] * B
    p1 = poly_pow_mul(base, m)  # (1+...+z^{B-1})^m
    # multiply by (1 - z^{D_S})
    deg = len(p1) - 1 + D_S
    p2 = [0] * (deg + 1)
    for i, c in enumerate(p1):
        p2[i] += c
        p2[i + D_S] -= c
    for idx, c in enumerate(p2):
        if c <= 0:
            return idx
    raise ValueError("no non-positive coefficient found within computed degree range")


def d_reg_closed_form(m: int, B: int, D_S: int) -> int:
    return math.ceil((m * (B - 1) + D_S) / 2)


def build_inv8_table() -> List[Dict]:
    rows = []
    for m in (2, 3, 4):
        for B in range(4, 65):
            for D_S in (3, 5, 7):
                d_conv = d_reg_via_convolution(m, B, D_S)
                d_cf = d_reg_closed_form(m, B, D_S)
                rows.append({
                    "m": m, "B": B, "D_S": D_S,
                    "d_reg_convolution": d_conv,
                    "d_reg_closed_form": d_cf,
                    "match": d_conv == d_cf,
                })
    return rows


# ---------------------------------------------------------------------------
# INV-A4: Bose-Chowla B_3 Sidon floor in GF(q^3), realized in Z/(q^3 - 1)
# ---------------------------------------------------------------------------

def _gf_mul(a: Tuple[int, int, int], b: Tuple[int, int, int], q: int, f: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Multiply a,b in GF(q)[x]/(x^3 + f2 x^2 + f1 x + f0), a,b as (c0,c1,c2)."""
    # full product degree <=4
    prod = [0] * 5
    A = [a[0], a[1], a[2]]
    B = [b[0], b[1], b[2]]
    for i in range(3):
        if A[i] == 0:
            continue
        for j in range(3):
            prod[i + j] = (prod[i + j] + A[i] * B[j]) % q
    # reduce mod x^3 = -(f2 x^2 + f1 x + f0)
    f0, f1, f2 = f
    for deg in (4, 3):
        c = prod[deg]
        if c == 0:
            continue
        prod[deg] = 0
        # x^deg = x^(deg-3) * x^3 = x^(deg-3) * ( -f2 x^2 - f1 x - f0 )
        shift = deg - 3
        prod[shift + 2] = (prod[shift + 2] - c * f2) % q
        prod[shift + 1] = (prod[shift + 1] - c * f1) % q
        prod[shift + 0] = (prod[shift + 0] - c * f0) % q
    return (prod[0] % q, prod[1] % q, prod[2] % q)


def _find_irreducible_cubic(q: int) -> Tuple[int, int, int]:
    """Find (f0,f1,f2) with f(x) = x^3 + f2 x^2 + f1 x + f0 irreducible over
    GF(q), by random search + no-roots-in-GF(q) test (sufficient for
    degree 3: a cubic with no roots in GF(q) cannot factor as
    linear*linear*linear or linear*quadratic, hence is irreducible)."""
    rng = random.Random(str(("EXP-RELN-141a86", "irred_cubic", q)))
    while True:
        f0 = rng.randrange(1, q)  # f0 != 0 so x=0 is not a root trivially avoided too, but check anyway
        f1 = rng.randrange(0, q)
        f2 = rng.randrange(0, q)
        has_root = False
        for x in range(q):
            val = (x ** 3 + f2 * x * x + f1 * x + f0) % q
            if val == 0:
                has_root = True
                break
        if not has_root:
            return (f0, f1, f2)


def _factorize(n: int) -> List[int]:
    """Trial-division prime factorization (n small enough, <= 101^3-1 ~ 1.03e6)."""
    factors = []
    d = 2
    m = n
    while d * d <= m:
        while m % d == 0:
            factors.append(d)
            m //= d
        d += 1
    if m > 1:
        factors.append(m)
    return sorted(set(factors))


def build_inv_a4_table(qs: List[int]) -> List[Dict]:
    rows = []
    for q in qs:
        N = q ** 3 - 1
        f = _find_irreducible_cubic(q)
        order = N
        prime_factors = _factorize(order)
        one = (1, 0, 0)
        zero = (0, 0, 0)
        x = (0, 1, 0)

        def gf_pow(base, e):
            result = one
            b = base
            e_bits = e
            while e_bits > 0:
                if e_bits & 1:
                    result = _gf_mul(result, b, q, f)
                b = _gf_mul(b, b, q, f)
                e_bits >>= 1
            return result

        # find a generator theta of the multiplicative group of order N
        rng = random.Random(str(("EXP-RELN-141a86", "gf_gen", q)))
        theta = None
        for _ in range(2000):
            cand = (rng.randrange(0, q), rng.randrange(0, q), rng.randrange(0, q))
            if cand == zero:
                continue
            if gf_pow(cand, N) != one:
                continue  # should always be identity by Lagrange; sanity only
            is_generator = True
            for p in prime_factors:
                if gf_pow(cand, N // p) == one:
                    is_generator = False
                    break
            if is_generator:
                theta = cand
                break
        if theta is None:
            rows.append({"q": q, "error": "no_generator_found_in_search_budget"})
            continue

        # build discrete-log table by repeated multiplication by theta
        logtable = {}
        cur = one
        for k in range(N):
            logtable[cur] = k
            cur = _gf_mul(cur, theta, q, f)
        assert cur == one, "theta order verification failed: did not return to 1 at step N"

        # Bose-Chowla base: D = { log(theta + c) : c in GF(q) }, theta fixed
        # representative element x (the generator of the field extension
        # used as the "variable"), NOT necessarily the same as `theta`
        # above; use x (0,1,0) shifted by c, and separately require D's
        # discrete logs relative to `theta`.
        D = []
        for c in range(q):
            elt = ((x[0] + c) % q, x[1], x[2])
            if elt == zero:
                continue
            D.append(logtable[elt])
        D = sorted(set(D))
        B = len(D)

        # exact count vector via direct enumeration (B <= 102, m=3: C(B+2,3) <= ~176851)
        import count_vectors as cv
        counts = cv.count_vector_direct(D, N, 3)
        stats = cv.stats_from_count_vector(counts, N)
        M = math.comb(B + 2, 3)
        mu = M / N
        coverage_cf = math.comb(B + 2, 3) / N
        delta_cf = 1 - mu
        delta_measured = cv.dispersion_delta(stats["mean"], stats["concentration"])

        rows.append({
            "q": q, "N": N, "B": B, "M": M, "mu": mu,
            "max_count": stats["max_count"],
            "is_b3_set_exact": stats["max_count"] == 1,
            "coverage_measured": stats["coverage"],
            "coverage_closed_form": coverage_cf,
            "coverage_matches": abs(stats["coverage"] - coverage_cf) < 1e-9,
            "delta_measured": delta_measured,
            "delta_closed_form": delta_cf,
            "delta_matches": abs(delta_measured - delta_cf) < 1e-9,
        })
    return rows


if __name__ == "__main__":
    import json
    print("INV-8 self-test (small):")
    print(json.dumps(build_inv8_table()[:3], indent=2))
    print("INV-7 self-test (8-bit only, 20 draws):")
    print(json.dumps(build_inv7_table([8], draws_per_cell=20), indent=2))
