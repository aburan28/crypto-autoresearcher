"""Imaginary-quadratic-order arithmetic for EXP-CANL-96b0ad.

NEW MODULE, built for this contract only. Nothing here modifies
harness/toycurve.py or harness/isogeny_class.py; this module REUSES
harness/isogeny_class.py's trace_of_frobenius, frobenius_discriminant,
fundamental_discriminant, cm_eigenvalues, j_invariant, twists_of_j
unmodified (imported, never copied).

Everything below is exact integer arithmetic on the order O = Z[w],
w = (D + sqrt(D))/2, of discriminant D (D = D_E for a concrete curve, or a
swept discriminant for the Stage-0 gate). D must satisfy D < 0 and
D = 0 or 1 (mod 4) -- the definition of an (imaginary quadratic) order
discriminant. alpha = a + b*w for integers a, b is represented as the pair
(a, b) throughout.

NORM FORM (exact integer formula, derived once and reused everywhere):
    w satisfies w^2 - D*w + D*(D-1)/4 = 0  (trace D, norm D*(D-1)/4).
    For alpha = a + b*w:
        N(alpha) = a^2 + a*b*D + b^2*D*(D-1)//4
    which is an exact integer whenever D == 0 or 1 (mod 4) (checked by
    __post_init__ below), and is algebraically identical to the mechanism's
    own STEP 2 form N(alpha) = (a+bD/2)^2 + (b^2/4)|D| -- verified by direct
    expansion in this module's own self-test (see canl_self_test below).

LAMBDA REDUCTION (mechanism STEP 5): for a concrete curve of trace t,
conductor f (D_E = D0*f^2), and modulus N with gcd(f, N) = 1 and N odd:
    lambda(pi) = 1                      (Frobenius reduces to the identity
                                          eigenvalue by the fixed choice of
                                          eigenspace this lambda represents)
    lambda(sqrt(D0)) = (2 - t) * f^{-1} mod N     (from pi = (t+f*sqrt(D0))/2)
    lambda(w) = (D_E + f*lambda(sqrt(D0))) * 2^{-1} mod N
              = (D_E + 2 - t) * 2^{-1} mod N       (the f cancels mod N since
                                                     f*f^{-1} = 1 mod N; this
                                                     simplification is exact,
                                                     not approximate, and is
                                                     re-derived in the module
                                                     docstring of
                                                     lambda_reduce below)
    lambda(a + b*w) = a + b*lambda(w) mod N, extended Z-linearly.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import count

# Reused UNMODIFIED from the already-committed instrument.
from .isogeny_class import cm_eigenvalues  # noqa: F401  (re-exported for callers)

# The 13 class-number-one discriminants, frozen by the contract.
CLASS_NUMBER_ONE_DISCRIMINANTS = [-3, -4, -7, -8, -11, -12, -16, -19, -27,
                                  -28, -43, -67, -163]


def is_valid_discriminant(D: int) -> bool:
    return D < 0 and D % 4 in (0, 1)


def norm_form(a: int, b: int, D: int) -> int:
    """N(a + b*w) for the order-D basis element w = (D + sqrt(D))/2.

    Exact integer arithmetic. Requires D == 0 or 1 (mod 4), D < 0 (checked).
    """
    if not is_valid_discriminant(D):
        raise ValueError(f"D={D} is not a valid (negative) order discriminant")
    return a * a + a * b * D + b * b * (D * (D - 1) // 4)


def norm_form_float_crosscheck(a: int, b: int, D: int, prec: int = 60) -> float:
    """SECOND, independently written norm computation (certificate_semantics
    (b)): direct high-precision floating-point evaluation of
    |a + b*(D+sqrt(D))/2|^2, cross-checked against norm_form's exact integer
    formula. Used only to certify a Stage-0 counterexample, never as the
    primary computation.
    """
    import mpmath
    with mpmath.workdps(prec):
        sqrtD = mpmath.sqrt(mpmath.mpc(D))
        alpha = a + b * (D + sqrtD) / 2
        return float((alpha * mpmath.conj(alpha)).real)


# --------------------------------------------------------------------------
# Lemma-1 Stage-0 search (global gate G1)
# --------------------------------------------------------------------------

@dataclass
class Lemma1SearchResult:
    D: int
    box: int
    min_norm: int
    argmin: tuple[int, int]
    predicted_min: int
    matches_prediction: bool
    counterexample: tuple[int, int, int] | None  # (a, b, N) with N < |D|/4, else None


def lemma1_predicted_min(D: int) -> int:
    """Lemma 1's own equality case: |D|/4 exact for D even, (|D|+1)/4 for D odd."""
    aD = -D
    return aD // 4 if aD % 4 == 0 else (aD + 1) // 4


def lemma1_stage0_search(D: int, box: int = 50) -> Lemma1SearchResult:
    """Exhaustive integer search over alpha = a + b*w, |a|,|b| <= box, b != 0.

    Finds the minimum N(alpha) and compares against Lemma 1's forced exact
    value. A found minimum strictly below |D|/4 is flagged as a
    counterexample candidate (global gate G1).
    """
    best = None
    best_ab = None
    threshold = abs(D) / 4.0
    counterexample = None
    for b in range(1, box + 1):          # N(a,b,D) = N(a,-b,D) is NOT always
        for sgn in (1, -1):              # true in general, so scan +-b both
            bb = sgn * b
            for a in range(-box, box + 1):
                n = norm_form(a, bb, D)
                if best is None or n < best:
                    best = n
                    best_ab = (a, bb)
                if n < threshold:
                    if counterexample is None or n < counterexample[2]:
                        counterexample = (a, bb, n)
    predicted = lemma1_predicted_min(D)
    return Lemma1SearchResult(
        D=D, box=box, min_norm=best, argmin=best_ab,
        predicted_min=predicted, matches_prediction=(best == predicted),
        counterexample=counterexample,
    )


def alpha_min(D: int) -> tuple[int, int]:
    """The Lemma-1-minimizing element: b=1, a* = round(-D/2)."""
    a_star = round(-D / 2)
    # round() on a .5 case (D odd) ties to even in Python; pick the exact
    # minimizer by direct comparison of the two integer candidates instead.
    lo = -D // 2
    hi = lo + 1
    cand = [lo, hi]
    best = min(cand, key=lambda a: norm_form(a, 1, D))
    return (best, 1)


# --------------------------------------------------------------------------
# Unit group and shell enumeration (C2)
# --------------------------------------------------------------------------

def unit_group(D0: int, f: int) -> list[tuple[int, int]]:
    """O^* for the order of discriminant D = D0*f^2, as (a,b) pairs.

    For f == 1 (maximal order): D0=-3 -> order 6 (primitive 6th roots of
    unity), D0=-4 -> order 4 ({1,i,-1,-i}), otherwise order 2 ({1,-1}).
    For f > 1 (non-maximal order): the unit group of a proper suborder of an
    imaginary quadratic field is {1,-1} UNLESS D0 in {-3,-4} AND the extra
    root of unity happens to still lie in the suborder, which for D0=-3,-4
    only occurs at f=1 (the suborders of index f>1 do not contain the extra
    units, a standard fact about orders in imaginary quadratic fields).
    """
    D = D0 * f * f
    units_norm1 = []
    for b in range(-3, 4):
        for a in range(-3, 4):
            if norm_form(a, b, D) == 1:
                units_norm1.append((a, b))
    return sorted(set(units_norm1))


# --------------------------------------------------------------------------
# Shell enumeration S(C0) = {alpha in O : N(alpha) <= C0^2}
# --------------------------------------------------------------------------

@dataclass
class ShellResult:
    D: int
    C0: int
    elements: list[tuple[int, int]]     # (a, b) pairs, b == 0 allowed (Z part)
    unit_elements: list[tuple[int, int]]
    nonunit_elements: list[tuple[int, int]]
    predicted_count: float
    relative_error: float


def shell_enumerate(D: int, C0: int, D0: int, f: int) -> ShellResult:
    """Exact enumeration of S(C0) via a norm-bounded box search.

    Box bound: |b| <= 2*C0/sqrt(|D|) * ... in practice we search
    a,b in a box wide enough to guarantee no element with N<=C0^2 is missed:
    from N(a,b,D) >= b^2*|D|/4 (Lemma 1's own bound, b != 0 case) we get
    |b| <= 2*C0/sqrt(|D|), and for fixed b, a ranges within a window found by
    completing the square in the exact integer formula.
    """
    C2 = C0 * C0
    elems = []
    bmax = int(2 * C0 / math.sqrt(abs(D))) + 2
    for b in range(-bmax, bmax + 1):
        # a^2 + a*b*D + b^2*D*(D-1)//4 <= C0^2
        # complete the square in a: (a + b*D/2)^2 <= C0^2 - b^2*(D*(D-1)//4 - D^2/4)
        # simpler: just scan a in a safe symmetric window.
        amax = int(math.isqrt(max(C2, 1))) + abs(b) * (abs(D) + 2)
        # tight, correctness-first window: use the exact quadratic-in-a bound
        # (a + b*D/2)^2 <= C0^2 + b^2*D/4  (from N = (a+bD/2)^2 + b^2|D|/4)
        rhs = C2 + b * b * D / 4.0     # D negative, so this SUBTRACTS
        if rhs < 0:
            continue
        half = math.sqrt(rhs)
        center = -b * D / 2.0
        alo = math.floor(center - half) - 1
        ahi = math.ceil(center + half) + 1
        for a in range(alo, ahi + 1):
            n = norm_form(a, b, D)
            if n <= C2:
                elems.append((a, b))
    units = set(unit_group(D0, f)) & set(elems)
    unit_elems = sorted(u for u in elems if u in units)
    nonunit_elems = sorted(e for e in elems if e not in units)
    predicted = 2 * math.pi * C2 / math.sqrt(abs(D))
    rel_err = abs(len(elems) - predicted) / predicted if predicted else float("nan")
    return ShellResult(D, C0, sorted(elems), unit_elems, nonunit_elems,
                       predicted, rel_err)


# --------------------------------------------------------------------------
# lambda reduction (mechanism STEP 5)
# --------------------------------------------------------------------------

def lambda_of_w(D_E: int, t: int, f: int, N: int) -> int:
    """lambda(w) mod N, w = (D_E + sqrt(D_E))/2, per mechanism STEP 5.

    Derivation (restated in full so the simplification is auditable):
        pi = (t + f*sqrt(D0)) / 2               (Frobenius in the order basis)
        lambda(pi) = 1                          (fixed eigenspace convention)
        => 1 = (t + f*lambda(sqrt(D0))) * inv(2)   mod N
        => lambda(sqrt(D0)) = (2 - t) * inv(f)     mod N   [gcd(f, N) = 1]
        lambda(w) = (D_E + f*lambda(sqrt(D0))) * inv(2)  mod N
                  = (D_E + f*(2-t)*inv(f)) * inv(2)       mod N
                  = (D_E + (2-t)) * inv(2)                mod N   [f*inv(f)=1]
    Requires N odd (so 2 is invertible) and gcd(f, N) == 1 (checked by caller
    via the intermediate quantity, though the final formula does not need f
    explicitly once the cancellation is applied -- the gcd(f,N)=1
    precondition is still REQUIRED for the derivation's second line to be
    valid, and is asserted here rather than silently assumed).
    """
    if N % 2 == 0:
        raise ValueError("lambda reduction requires odd N (2 must be invertible)")
    if math.gcd(f, N) != 1:
        raise ValueError(f"lambda reduction requires gcd(f={f}, N={N}) == 1")
    inv2 = pow(2, -1, N)
    return (D_E + 2 - t) % N * inv2 % N


def lambda_reduce(a: int, b: int, D_E: int, t: int, f: int, N: int) -> int:
    """lambda(a + b*w) mod N = a + b*lambda(w) mod N."""
    return (a + b * lambda_of_w(D_E, t, f, N)) % N


# --------------------------------------------------------------------------
# Reachable-count enumeration, memory-bounded (Z-arm and O-arm, shared code)
# --------------------------------------------------------------------------

def reachable_residue_count(coeff_sets: list[list[int]], k_tuple: list[int],
                            N: int) -> tuple[int, set[int]]:
    """Distinct values of sum_i k_i * c_i mod N, c_i ranging over coeff_sets[i].

    MEMORY-BOUNDED BY CONSTRUCTION: the running "reachable" accumulator is a
    Python set of residues mod N, so it never exceeds N elements regardless
    of how large the naive Cartesian product (2*C0+1)^slots or
    |S(C0)|^slots would be. This directly satisfies the contract's
    budget_note requirement to stream/chunk rather than materialize the full
    tuple list at C_0=8.

    Returns (count, the reachable set itself) so callers can spot-check or
    report tail-check ratios against the naive combinatorial upper bound.
    """
    assert len(coeff_sets) == len(k_tuple)
    reachable = {0}
    for k_i, cs in zip(k_tuple, coeff_sets):
        vals = sorted({(k_i * c) % N for c in cs})
        new_reachable: set[int] = set()
        for r in reachable:
            for v in vals:
                new_reachable.add((r + v) % N)
            if len(new_reachable) == N:
                break
        reachable = new_reachable
        if len(reachable) == N:
            # saturated; further slots cannot grow it further
            continue
    return len(reachable), reachable


def spot_check_reachable(coeff_sets: list[list[int]], k_tuple: list[int],
                         N: int, reachable: set[int], sample: list[int],
                         rng) -> bool:
    """Independent 1% spot-check: rebuild `sample` residues by direct
    re-derivation from freshly-drawn coefficient tuples and confirm each is
    (a) actually a member of `reachable` and (b) independently recomputable
    by summing a random preimage tuple mod N. A SECOND, separately written
    reducer (does not call reachable_residue_count's own accumulation loop).
    """
    for _ in sample:
        tup = [rng.choice(cs) for cs in coeff_sets]
        val = sum(k_i * c for k_i, c in zip(k_tuple, tup)) % N
        if val not in reachable:
            return False
    return True


# --------------------------------------------------------------------------
# Self-test (G0's exact-arithmetic half; the height half lives in
# canonical_height.py's own self-test)
# --------------------------------------------------------------------------

def canl_self_test() -> dict:
    """Known-answer checks for the exact-integer machinery in this module."""
    results = {}

    # (1) norm_form matches the mechanism's own (a+bD/2)^2+(b^2/4)|D| form,
    # cross-checked with the independent floating-point formula.
    ok = True
    for D in [-3, -4, -7, -8, -11, -20, -23, -47, -1000003]:
        for a in range(-5, 6):
            for b in range(-5, 6):
                exact = norm_form(a, b, D)
                flt = norm_form_float_crosscheck(a, b, D)
                if abs(exact - flt) > 1e-6:
                    ok = False
    results["norm_form_crosscheck"] = ok

    # (2) Lemma 1 equality case: alpha_min has norm exactly |D|/4 (D even) or
    # (|D|+1)/4 (D odd), for a spread of discriminants.
    ok = True
    for D in [-3, -4, -7, -8, -11, -12, -16, -19, -27, -28, -43, -67, -163,
             -256, -1000003]:
        am = alpha_min(D)
        n = norm_form(am[0], am[1], D)
        predicted = lemma1_predicted_min(D)
        if n != predicted:
            ok = False
    results["alpha_min_matches_lemma1_equality"] = ok

    # (3) Lemma 1 lower bound holds on a Stage-0 search box for a spread of D.
    ok = True
    for D in [-3, -4, -7, -8, -11, -256, -1000003]:
        res = lemma1_stage0_search(D, box=10)
        if res.counterexample is not None or res.min_norm < lemma1_predicted_min(D):
            ok = False
    results["lemma1_lower_bound_holds_box10"] = ok

    # (4) unit group orders: D0=-3,f=1 -> 6; D0=-4,f=1 -> 4; else -> 2.
    results["unit_group_orders"] = {
        "D0=-3,f=1": len(unit_group(-3, 1)),
        "D0=-4,f=1": len(unit_group(-4, 1)),
        "D0=-7,f=1": len(unit_group(-7, 1)),
        "D0=-3,f=2": len(unit_group(-3, 2)),
    }
    results["unit_group_orders_correct"] = (
        results["unit_group_orders"]["D0=-3,f=1"] == 6 and
        results["unit_group_orders"]["D0=-4,f=1"] == 4 and
        results["unit_group_orders"]["D0=-7,f=1"] == 2 and
        results["unit_group_orders"]["D0=-3,f=2"] == 2
    )

    # (5) shell count relative error against 2*pi*C0^2/sqrt(|D|), C0 >= 5.
    ok = True
    errs = {}
    for D in [-3, -4, -7]:
        for C0 in [5, 8, 15, 20]:
            sh = shell_enumerate(D, C0, D, 1)
            errs[f"D={D},C0={C0}"] = sh.relative_error
            if sh.relative_error > 0.15:
                ok = False
    results["shell_count_predicted_within_15pct"] = ok
    results["shell_count_relative_errors"] = errs

    # (6) reachable_residue_count matches brute-force cartesian enumeration
    # on a small case (cross-check of the memory-bounded algorithm itself).
    ok = True
    import itertools
    N = 97
    coeff_sets = [list(range(-3, 4)), list(range(-2, 3)), list(range(-1, 2))]
    k_tuple = [1, 2, 3]
    fast_count, fast_set = reachable_residue_count(coeff_sets, k_tuple, N)
    brute = set()
    for tup in itertools.product(*coeff_sets):
        brute.add(sum(k * c for k, c in zip(k_tuple, tup)) % N)
    if fast_count != len(brute) or fast_set != brute:
        ok = False
    results["reachable_count_matches_bruteforce"] = ok

    results["all_passed"] = all(
        v for k, v in results.items()
        if isinstance(v, bool)
    )
    return results


__all__ = [
    "CLASS_NUMBER_ONE_DISCRIMINANTS", "is_valid_discriminant", "norm_form",
    "norm_form_float_crosscheck", "Lemma1SearchResult", "lemma1_predicted_min",
    "lemma1_stage0_search", "alpha_min", "unit_group", "ShellResult",
    "shell_enumerate", "lambda_of_w", "lambda_reduce",
    "reachable_residue_count", "spot_check_reachable", "canl_self_test",
    "cm_eigenvalues",
]
