"""Stage-0 arithmetic: ladder, ord/f census, ord_17(4) lattice, predictions."""
from __future__ import annotations

import itertools
from math import gcd


def ord_n_of_a(n: int, a: int = 2) -> int:
    """Multiplicative order of a modulo n (n prime or coprime to a)."""
    if gcd(a, n) != 1:
        raise ValueError(f"gcd({a},{n})!=1")
    # order divides phi(n); for prime n, divides n-1
    # Find least d | (n-1) with a^d ≡ 1 (mod n) when n prime; else use phi.
    # For this experiment all n are prime.
    phi = n - 1
    # factor phi naively
    d = phi
    # remove factors
    # Get all divisors
    divisors = _divisors(phi)
    for d in sorted(divisors):
        if pow(a, d, n) == 1:
            return d
    raise RuntimeError(f"order of {a} mod {n} not found")


def _divisors(m: int) -> list[int]:
    out = []
    i = 1
    while i * i <= m:
        if m % i == 0:
            out.append(i)
            if i * i != m:
                out.append(m // i)
        i += 1
    return out


def f_from_ord(n: int, ord_val: int) -> int:
    """f = 1 + (n-1)/ord_n(2) — number of irreducible factors of x^n-1 over F_2."""
    if (n - 1) % ord_val != 0:
        raise ValueError(f"ord={ord_val} does not divide n-1={n-1}")
    return 1 + (n - 1) // ord_val


def is_primitive_prime_null(n: int, ord_val: int) -> bool:
    """Null-arm validity: ord_n(2) = n-1."""
    return ord_val == n - 1


# Frozen corrected ladder from H-BINSTD-4a2f99 (HOLD-N corrected).
DEPLOYED_PAIRS = [
    {
        "pair": 1,
        "c2pnb": "c2pnb176v1",
        "c2tnb": "c2tnb191v1",
        "c2pnb_deg": 176,
        "c2tnb_deg": 191,
        "d": 4,
        "k": 7,
        "n_null": 29,
        "role": "ladder",
        "is_primary": False,
    },
    {
        "pair": 2,
        "c2pnb": "c2pnb208w1",
        "c2tnb": "c2tnb191v1",
        "c2pnb_deg": 208,
        "c2tnb_deg": 191,
        "d": 2,
        "k": 17,
        "n_null": 37,
        "role": "primary",
        "is_primary": True,
    },
    {
        "pair": 3,
        "c2pnb": "c2pnb272w1",
        "c2tnb": "c2tnb239v1",
        "c2pnb_deg": 272,
        "c2tnb_deg": 239,
        "d": 2,
        "k": 19,
        "n_null": 37,
        "role": "ladder",
        "is_primary": False,
    },
    {
        "pair": 4,
        "c2pnb": "c2pnb304w1",
        "c2tnb": "c2tnb359v1",
        "c2pnb_deg": 304,
        "c2tnb_deg": 359,
        "d": 4,
        "k": 7,
        "n_null": 29,
        "role": "ladder",
        "is_primary": False,
    },
    {
        "pair": 5,
        "c2pnb": "c2pnb368w1",
        "c2tnb": "c2tnb359v1",
        "c2pnb_deg": 368,
        "c2tnb_deg": 359,
        "d": 2,
        "k": 19,
        "n_null": 37,
        "role": "best_ratio_match",
        "is_primary": False,
    },
]

# Frozen expected errors (percentage points) from H-BINSTD-4a2f99.
FROZEN_ERROR_PP = {1: 4.5, 2: -17.0, 3: -11.1, 4: 11.9, 5: 0.2}

N_CENSUS = [17, 29, 31, 37, 41, 53]

# Frozen expected ord_n(2)/f from H-BINSTD-4a2f99 (n=17 included for census completeness).
FROZEN_ORD_F = {
    17: {"ord_n_2": 8, "f": 3},
    29: {"ord_n_2": 28, "f": 2},
    31: {"ord_n_2": 5, "f": 7},
    37: {"ord_n_2": 36, "f": 2},
    41: {"ord_n_2": 20, "f": 3},
    53: {"ord_n_2": 52, "f": 2},
}


def corrected_ladder_rows() -> list[dict]:
    rows = []
    for p in DEPLOYED_PAIRS:
        target_exact = p["c2pnb_deg"] / p["c2tnb_deg"]
        dk = p["d"] * p["k"]
        ratio_exact = dk / p["n_null"]
        # Frozen table (H-BINSTD-4a2f99) uses 3-decimal deployed/toy ratios
        # then 1-decimal percentage-point errors.
        target = round(target_exact, 3)
        ratio = round(ratio_exact, 3)
        err_pp_rounded = round((ratio - target) * 100.0, 1)
        ord_null = ord_n_of_a(p["n_null"], 2)
        f_null = f_from_ord(p["n_null"], ord_null)
        rows.append(
            {
                "pair": p["pair"],
                "c2pnb": p["c2pnb"],
                "c2tnb": p["c2tnb"],
                "deployed_target_ratio_exact": target_exact,
                "deployed_target_ratio": target,
                "d": p["d"],
                "k": p["k"],
                "dk": dk,
                "n_null": p["n_null"],
                "toy_ratio_exact": ratio_exact,
                "toy_ratio": ratio,
                "error_pp_recomputed": err_pp_rounded,
                "error_pp_frozen": FROZEN_ERROR_PP[p["pair"]],
                "error_pp_match": err_pp_rounded == FROZEN_ERROR_PP[p["pair"]],
                "ord_n_null_of_2": ord_null,
                "f_null": f_null,
                "null_is_primitive_prime": is_primitive_prime_null(p["n_null"], ord_null),
                "role": p["role"],
                "is_primary": p["is_primary"],
                "label_recomputed": "RECOMPUTED",
                "label_frozen": "EXPECTED",
            }
        )
    return rows


def ord_f_census(n_list: list[int] | None = None) -> list[dict]:
    n_list = n_list or N_CENSUS
    rows = []
    for n in n_list:
        o = ord_n_of_a(n, 2)
        f = f_from_ord(n, o)
        frozen = FROZEN_ORD_F.get(n)
        mid_dim_stable = f > 2  # nontrivial mid-dimension stable subspaces present iff f>2
        rows.append(
            {
                "n": n,
                "ord_n_of_2": o,
                "f_irreducible_factor_count": f,
                "primitive_prime_null": is_primitive_prime_null(n, o),
                "mid_dimension_stable_V_present": mid_dim_stable,
                "role": _role_for_n(n, o),
                "frozen_ord_n_2": None if frozen is None else frozen["ord_n_2"],
                "frozen_f": None if frozen is None else frozen["f"],
                "match_frozen": (
                    frozen is not None and o == frozen["ord_n_2"] and f == frozen["f"]
                ),
                "label_recomputed": "RECOMPUTED",
            }
        )
    return rows


def _role_for_n(n: int, ord_val: int) -> str:
    if n == 37:
        return "primary_null_arm"
    if n == 31:
        return "contrast_not_null"  # NEVER null
    if n == 41:
        return "rejected_poor_control"  # NOT a poor lattice control
    if is_primitive_prime_null(n, ord_val):
        return "alternate_primitive_null_candidate"
    return "census"


def ord_k_of_q(k: int, q: int) -> int:
    return ord_n_of_a(k, q % k)


def lattice_ord17_of_4() -> dict:
    """ord_17(4)=4, f=5, 32 subspaces, dims from subset sums of {1,4,4,4,4}."""
    k, q = 17, 4
    o = ord_k_of_q(k, q)
    # f = 1 + (k-1)/ord_k(q)
    f = 1 + (k - 1) // o
    # Factor degrees of T^k - 1 over F_q: one degree-1 (T-1) and
    # (k-1)/o irreducibles of degree o.
    factor_degrees = [1] + [o] * ((k - 1) // o)
    dims = sorted(
        {
            sum(subset)
            for r in range(len(factor_degrees) + 1)
            for subset in itertools.combinations(factor_degrees, r)
        }
    )
    expected_dims = [0, 1, 4, 5, 8, 9, 12, 13, 16, 17]
    expected_f = 5
    expected_count = 32
    return {
        "k": k,
        "q": q,
        "base_field": "F_4",
        "ord_17_of_4": o,
        "f": f,
        "stable_subspace_count": 1 << f,
        "factor_degrees_T_k_minus_1_over_Fq": factor_degrees,
        "stable_dimensions": dims,
        "expected_ord": 4,
        "expected_f": expected_f,
        "expected_stable_subspace_count": expected_count,
        "expected_dimensions": expected_dims,
        "match_expected": (
            o == 4 and f == expected_f and (1 << f) == expected_count and dims == expected_dims
        ),
        "label_recomputed": "RECOMPUTED",
    }


def count_irreducible_factors_xn_minus_1(n: int) -> dict:
    """Independent factor count of x^n-1 over F_2 via distinct-degree / formula cross-check.

    Primary: closed form f=1+(n-1)/ord_n(2) (n prime).
    Secondary: square-free factorization into cyclotomic Phi_d for d|n, then
    each Phi_d splits into phi(d)/ord_d(2) irreducibles of degree ord_d(2).
    """
    o = ord_n_of_a(n, 2)
    f_formula = f_from_ord(n, o)
    # Secondary: sum over d|n of phi(d)/ord_d(2)
    total = 0
    breakdown = []
    for d in _divisors(n):
        # Phi_d has degree phi(d); factors into phi(d)/ord_d(2) irreducibles
        # when d>1; for d=1, Phi_1 = x-1, one linear factor.
        if d == 1:
            n_factors = 1
            deg = 1
            od = None
        else:
            od = ord_n_of_a(d, 2)
            phi_d = _euler_phi(d)
            assert phi_d % od == 0
            n_factors = phi_d // od
            deg = od
        total += n_factors
        breakdown.append(
            {
                "d": d,
                "phi_d": 1 if d == 1 else _euler_phi(d),
                "ord_d_of_2": od,
                "irreducible_count": n_factors,
                "irreducible_degree": deg,
            }
        )
    return {
        "n": n,
        "ord_n_of_2": o,
        "f_formula": f_formula,
        "f_cyclotomic_sum": total,
        "agreement": f_formula == total,
        "breakdown": breakdown,
        "label_recomputed": "RECOMPUTED",
    }


def _euler_phi(m: int) -> int:
    result = m
    x = m
    p = 2
    while p * p <= x:
        if x % p == 0:
            while x % p == 0:
                x //= p
            result = result // p * (p - 1)
        p += 1 if p == 2 else 2
    if x > 1:
        result = result // x * (x - 1)
    return result
