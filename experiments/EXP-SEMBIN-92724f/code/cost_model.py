#!/usr/bin/env python3
"""Arm A of EXP-SEMBIN-92724f: Semaev's two-stage cost model, the typed model
under Galbraith-Gebregiyorgis's three substitutions, and the derivations that
localise the exponent constant.

FROZEN FORMULAS, transcribed from inputs/SEMAEV-2015-310 (eqs. (15)-(17)) and
from the three substitutions declared in the contract. Nothing here is fitted.

  untyped stage 1  (eq. 15)   m! * 2^{n-mk} * 2^k * n^{4w}
  untyped stage 2  (eq. 16)   2^{k w'}
  typed   stage 1             2^{n-mk} * (m * 2^k) * n^{4w}
  typed   stage 2             (m * 2^k)^{w'}

The three substitutions and NOTHING else: yield 1/P becomes 2^{n-mk} in place
of m! 2^{n-mk}; relation count becomes m 2^k in place of 2^k; stage 2 becomes
(m 2^k)^{w'} in place of 2^{k w'}. The net stage-1 saving is therefore
log2(m!) - log2(m) = log2((m-1)!), never log2(m!).

TWO k READINGS, both computed, neither silently preferred: `unceiled` uses the
real number k = n/m (which is what Table 3's printed columns reproduce from) and
`ceiled` uses k = ceil(n/m) (which is what eq. (15) is derived with).

THREE YIELD VARIANTS, because the paper's own expression 2^{n-mk} exceeds 1/P
once mk > n, where the true yield saturates at 1. `paper_raw` is the frozen
formula and is the primary; `capped` floors the yield exponent at 0; `exact_p`
uses eq. (11) P = 1 - exp(-2^{mk-n}/t!) directly. Every reported number states
which variant produced it.

EVERY NUMBER THIS MODULE RETURNS IS MODELED, NOT MEASURED. No degree appears
anywhere: the solve cost enters only through the paper's own n^{4w} cofactor,
with 4 being the paper's exponent in that cofactor and not a degree this run
measured.
"""
from __future__ import annotations

import math
from decimal import Decimal, getcontext

getcontext().prec = 60

LN2 = math.log(2.0)

# --------------------------------------------------------------------------
# log2(m!) without overflowing a float, and exactly cross-checkable
# --------------------------------------------------------------------------
_LOG2_FACT_CACHE = [0.0]


def log2_factorial(m: int) -> float:
    """Cumulative sum of log2(i); cross-checked against exact integers below."""
    while len(_LOG2_FACT_CACHE) <= m:
        i = len(_LOG2_FACT_CACHE)
        _LOG2_FACT_CACHE.append(_LOG2_FACT_CACHE[i - 1] + math.log2(i))
    return _LOG2_FACT_CACHE[m]


def log2_exact_int(x: int) -> float:
    """log2 of an arbitrary-precision integer, to full double precision."""
    if x <= 0:
        raise ValueError("log2 of a non-positive integer")
    b = x.bit_length()
    if b <= 1023:
        return math.log2(x)
    shift = b - 53
    return shift + math.log2(x >> shift)


def log2_factorial_exact(m: int) -> float:
    return log2_exact_int(math.factorial(m))


def log2_add(a: float, b: float) -> float:
    """log2(2^a + 2^b), stable -- used for stage1 + stage2 totals."""
    hi, lo = max(a, b), min(a, b)
    if hi - lo > 60:
        return hi
    return hi + math.log2(1.0 + 2.0 ** (lo - hi))


# --------------------------------------------------------------------------
# k readings
# --------------------------------------------------------------------------
def k_of(n: int, m: int, reading: str) -> float:
    if reading == "unceiled_n_over_m_as_in_table3":
        return n / m
    if reading == "ceil_n_over_m":
        return float(-(-n // m))
    raise ValueError(f"unknown k reading {reading}")


K_READINGS = ("unceiled_n_over_m_as_in_table3", "ceil_n_over_m")


# --------------------------------------------------------------------------
# The four cost expressions, in log2, term by term
# --------------------------------------------------------------------------
def _minus_log2_p_from_lambda(lam_log2: float) -> float:
    """-log2(1 - exp(-lambda)) from log2(lambda), overflow-free.

    For lambda >> 1 the answer is 0 (the yield saturates); for lambda << 1,
    1 - exp(-lambda) = lambda (1 + O(lambda)) so the answer is -log2(lambda).
    """
    if lam_log2 > 10.0:
        return 0.0
    if lam_log2 < -40.0:
        return -lam_log2  # 1 - exp(-lam) = lam to 12 decimal places here
    lam = 2.0 ** lam_log2
    return -math.log2(-math.expm1(-lam))


def stage1_terms(n: int, m: int, reading: str, omega: float, typed: bool,
                 yield_variant: str = "paper_raw") -> dict:
    """Every additive log2 term of stage 1, kept separate and labelled.

    Returned separately rather than summed because the claim under test is
    about WHICH TERM grows with m, and a total hides exactly that.
    """
    k = k_of(n, m, reading)
    yield_exp = n - m * k
    sym = log2_factorial(m)
    if typed:
        symmetry_term = 0.0
        relation_term = k + math.log2(m)
    else:
        symmetry_term = sym
        relation_term = k
    if yield_variant == "paper_raw":
        # Exactly the paper's expression: 1/P = m! 2^{n-mk} (untyped), and the
        # same without the m! (typed). Left uncapped even where it exceeds the
        # true yield, because it is the frozen formula.
        yterm = yield_exp
    elif yield_variant == "capped":
        # 1/P >= 1: floor the whole yield contribution at 0 bits.
        yterm = max(0.0, yield_exp + symmetry_term) - symmetry_term
    elif yield_variant == "exact_p":
        # eq. (11): P = 1 - exp(-lambda), lambda = 2^{mk-n}/m! (untyped) or
        # 2^{mk-n} (typed). Whole yield contribution is -log2 P.
        lam_log2 = (m * k - n) - (sym if not typed else 0.0)
        yterm = _minus_log2_p_from_lambda(lam_log2) - symmetry_term
    else:
        raise ValueError(f"unknown yield variant {yield_variant}")
    return {
        "k": k,
        "yield_log2_2_pow_n_minus_mk": yterm,
        "symmetry_log2_m_factorial": symmetry_term,
        "relation_count_log2": relation_term,
        "solve_cofactor_log2_n_pow_4omega": 4.0 * omega * math.log2(n),
    }


def stage1_log2(n: int, m: int, reading: str, omega: float, typed: bool,
                yield_variant: str = "paper_raw") -> float:
    t = stage1_terms(n, m, reading, omega, typed, yield_variant)
    return (t["yield_log2_2_pow_n_minus_mk"] + t["symmetry_log2_m_factorial"]
            + t["relation_count_log2"]
            + t["solve_cofactor_log2_n_pow_4omega"])


def stage2_log2(n: int, m: int, reading: str, omega_prime: float,
                typed: bool) -> float:
    k = k_of(n, m, reading)
    return omega_prime * (k + (math.log2(m) if typed else 0.0))


def total_log2(n: int, m: int, reading: str, omega: float, omega_prime: float,
               typed: bool, yield_variant: str = "paper_raw") -> float:
    return log2_add(stage1_log2(n, m, reading, omega, typed, yield_variant),
                    stage2_log2(n, m, reading, omega_prime, typed))


# --------------------------------------------------------------------------
# Table 3 reproduction (the baseline control)
# --------------------------------------------------------------------------
def table3_row_model(n: int, m: int, reading: str) -> dict:
    """The three printed columns of Table 3, at the paper's omega = 3, w' = 2."""
    k = k_of(n, m, reading)
    return {
        "pollard_rho_log2": n / 2.0,
        "stage1_log2": (log2_factorial(m) + (n - m * k) + k
                        + 12.0 * math.log2(n)),
        "stage2_log2": 2.0 * k,
    }


def reproduce_table3(rows: list[dict]) -> list[dict]:
    """Residuals for all 36 numeric cells, under BOTH k readings.

    A residual is relative: |modelled - printed| / printed, computed in log2
    space and converted, so a 3-significant-figure printed value is compared
    against the model rather than the other way round.
    """
    out = []
    for row in rows:
        n, m = row["n"], row["m"]
        for reading in K_READINGS:
            model = table3_row_model(n, m, reading)
            cells = {
                "pollard_rho_2_to_n_over_2": ("pollard_rho_log2",
                                              row["pollard_rho_2_to_n_over_2"]),
                "stage1_collection": ("stage1_log2", row["stage1_collection"]),
                "stage2_linear_algebra": ("stage2_log2",
                                          row["stage2_linear_algebra"]),
            }
            for cell, (key, printed_raw) in cells.items():
                # tables.yaml stores the printed values as strings such as
                # '7.49e31' so that the transcription is byte-faithful to the
                # PDF; float() them here rather than rewriting the frozen file.
                printed = float(printed_raw)
                modelled_log2 = model[key]
                printed_log2 = math.log2(printed)
                rel = 2.0 ** (modelled_log2 - printed_log2) - 1.0
                out.append({
                    "n": n, "m": m, "k_reading": reading, "cell": cell,
                    "printed_value": printed,
                    "printed_log2": printed_log2,
                    "modelled_log2": modelled_log2,
                    "relative_residual": rel,
                    "abs_relative_residual": abs(rel),
                    "within_0p7pct": abs(rel) <= 0.007,
                    "k_readings_agree_this_row": (n % m == 0),
                })
    return out


# --------------------------------------------------------------------------
# m* and the symbolic balance
# --------------------------------------------------------------------------
def m_star_asymptotic(n: float) -> float:
    return math.sqrt(2.0 * LN2 * n / math.log(n))


def argmin_stage1_untyped(n: int, reading: str, omega: float = 3.0,
                          m_hi: int | None = None) -> tuple[int, float]:
    hi = m_hi or n
    best_m, best_v = 2, stage1_log2(n, 2, reading, omega, typed=False)
    for m in range(3, hi + 1):
        v = stage1_log2(n, m, reading, omega, typed=False)
        if v < best_v:
            best_m, best_v = m, v
    return best_m, best_v


def stage_coefficients(cprime: Decimal) -> dict:
    """Leading coefficients of sqrt(n ln n) in each stage, as exact expressions.

    With m = c' sqrt(n / ln n) and k = n/m:

      log2(m!)   = (c'/(2 ln 2)) sqrt(n ln n) (1 + O(log log n / log n))
      k = n/m    = (1/c')        sqrt(n ln n)
      4w log2 n  = O(log n)                       -- no m dependence at all
      w' k       = (w'/c')       sqrt(n ln n)

    so stage 1 has coefficient c'/(2 ln 2) + 1/c' and stage 2 has w'/c'.
    """
    ln2 = Decimal(2).ln()
    return {
        "stage1_coefficient": cprime / (2 * ln2) + 1 / cprime,
        "stage2_coefficient_omega_prime_2": Decimal(2) / cprime,
        "symmetry_carrier_coefficient": cprime / (2 * ln2),
        "relation_store_coefficient": 1 / cprime,
    }


def solve_cprime() -> dict:
    """Solve c'/(2 ln 2) + 1/c' = 2/c' exactly, then verify to 50 digits.

    The equation reduces to c'^2 = 2 ln 2 by subtracting 1/c' from both sides,
    which is an identity and not a fit; the bisection below is a CHECK of that
    algebra, carried out on the original unreduced equation.
    """
    ln2 = Decimal(2).ln()
    exact = (2 * ln2).sqrt()
    lo, hi = Decimal("0.1"), Decimal("10")

    def f(c: Decimal) -> Decimal:
        co = stage_coefficients(c)
        return co["stage1_coefficient"] - co["stage2_coefficient_omega_prime_2"]

    for _ in range(300):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    bisected = (lo + hi) / 2
    c_const = 2 / exact
    co = stage_coefficients(exact)
    return {
        "cprime_exact_symbolic": "sqrt(2 ln 2)",
        "cprime_exact_value_50dp": str(+exact),
        "cprime_from_bisecting_the_unreduced_balance": str(+bisected),
        "cprime_bisection_minus_exact": str(+(bisected - exact)),
        "c_exact_symbolic": "2 / sqrt(2 ln 2)",
        "c_exact_value_50dp": str(+c_const),
        "c_rounded_4dp": float(round(c_const, 4)),
        "stage1_coefficient_at_cprime": str(+co["stage1_coefficient"]),
        "stage2_coefficient_at_cprime": str(+co["stage2_coefficient_omega_prime_2"]),
        "stage_coefficients_equal_to_50dp":
            str(+(co["stage1_coefficient"]
                  - co["stage2_coefficient_omega_prime_2"])),
        "symmetry_carrier_coefficient": str(+co["symmetry_carrier_coefficient"]),
        "relation_store_coefficient": str(+co["relation_store_coefficient"]),
        "identity_used": ("c'/(2 ln 2) + 1/c' = 2/c'  <=>  c'/(2 ln 2) = 1/c' "
                          "<=>  c'^2 = 2 ln 2"),
    }


def carrier_convergence_table(cprime: float, ns: list[float]) -> list[dict]:
    """term / sqrt(n ln n) at m = c' sqrt(n/ln n), for each term separately.

    This is a CONVERGENCE TABLE toward closed forms that were derived
    symbolically, not a fit of the constant 1.6986: each row compares a
    measured ratio against the exact predicted coefficient for that term.
    """
    ln2 = LN2
    rows = []
    for n in ns:
        m = cprime * math.sqrt(n / math.log(n))
        scale = math.sqrt(n * math.log(n))
        lf = (math.lgamma(m + 1.0) / ln2)
        k = n / m
        rows.append({
            "n": n,
            "m_continuous": m,
            "log2_m_factorial_over_scale": lf / scale,
            "log2_m_factorial_predicted_coefficient": cprime / (2 * ln2),
            "k_over_scale": k / scale,
            "k_predicted_coefficient": 1.0 / cprime,
            "solve_cofactor_over_scale": 12.0 * math.log2(n) / scale,
            "solve_cofactor_predicted_coefficient": 0.0,
            "log2_m_over_scale": math.log2(m) / scale,
            "log2_m_predicted_coefficient": 0.0,
            "stage1_total_over_scale": (lf + k + 12.0 * math.log2(n)) / scale,
            "stage2_total_over_scale": (2.0 * k) / scale,
            "stage1_predicted_coefficient": cprime / (2 * ln2) + 1.0 / cprime,
            "stage2_predicted_coefficient": 2.0 / cprime,
        })
    return rows


def m_derivative_signs(n: int, m: int, reading: str, omega: float,
                       omega_prime: float) -> dict:
    """Exact analytic m-derivative of every term, evaluated at (n, m).

    d/dm log2(m!) = psi(m+1)/ln 2 > 0 for all m >= 1   -- the unique riser
    d/dm (n/m)    = -n/m^2 < 0
    d/dm 4w log2 n = 0
    d/dm w' n/m   = -w' n/m^2 < 0
    d/dm log2 m   = 1/(m ln 2) > 0                     -- typed arm only
    """
    psi = _digamma(m + 1.0)
    return {
        "d_log2_m_factorial_dm": psi / LN2,
        "d_log2_m_factorial_dm_leading_form": "psi(m+1)/ln2 ~ log2(m) > 0",
        "d_k_dm_unceiled": -n / (m * m),
        "d_solve_cofactor_dm": 0.0,
        "d_stage2_dm_unceiled": -omega_prime * n / (m * m),
        "d_log2_m_dm_typed_relation_count": 1.0 / (m * LN2),
        "unique_positive_term_untyped": "log2(m!)",
        "positive_terms_typed": ["log2(m) from the m 2^k relation count",
                                 "omega' log2(m) from (m 2^k)^omega'"],
    }


def _digamma(x: float) -> float:
    """psi(x) by the standard asymptotic series with recurrence shifting."""
    r = 0.0
    while x < 12.0:
        r -= 1.0 / x
        x += 1.0
    f = 1.0 / (x * x)
    return (r + math.log(x) - 0.5 / x
            + f * (-1.0 / 12 + f * (1.0 / 120 + f * (-1.0 / 252
                   + f * (1.0 / 240 + f * (-1.0 / 132))))))


# --------------------------------------------------------------------------
# Stage-1 saving and the required-degree floor
# --------------------------------------------------------------------------
def stage1_saving_bits(n: int, m: int, reading: str = "ceil_n_over_m",
                       omega: float = 3.0) -> dict:
    """Untyped minus typed stage-1, in bits, computed from the full expressions.

    Predicted to be exactly log2((m-1)!) -- and it is, identically in n, k and
    omega, because the three substitutions touch only the m! and the relation
    count. Both the difference of the full expressions and the closed form are
    returned so the reader can see they agree rather than be told.
    """
    untyped = stage1_log2(n, m, reading, omega, typed=False)
    typed = stage1_log2(n, m, reading, omega, typed=True)
    closed_form = log2_factorial(m - 1)
    return {
        "n": n, "m": m, "k_reading": reading, "omega": omega,
        "untyped_stage1_log2": untyped,
        "typed_stage1_log2": typed,
        "saving_bits_from_full_expressions": untyped - typed,
        "closed_form_log2_m_minus_1_factorial": closed_form,
        "closed_form_exact_int_check": log2_factorial_exact(m - 1),
        "log2_m_factorial_for_contrast": log2_factorial(m),
        "difference_from_closed_form": (untyped - typed) - closed_form,
        "agrees_within_0p1_bit": abs((untyped - typed) - closed_form) <= 0.1,
    }


def required_degree_floor(omega: float, n: float | None = None) -> dict:
    """d >= (c ln 2 / (2 w)) sqrt(n / ln n), re-derived from scratch.

    DERIVATION, all modeled and no degree measured. For the typed model to
    still cost 2^{c sqrt(n ln n)} the per-solve cost must supply that exponent,
    since every other typed term is O(log n) at the boundary. Modelling the
    solve as N^{d w} with N = Theta(n m) <= Theta(n^2) variables gives
    log2(solve) = d w log2 N = 2 d w log2 n (1 + o(1)), so

        2 d w log2 n >= c sqrt(n ln n)
        d >= (c / (2 w)) * sqrt(n ln n) / log2 n
           = (c ln 2 / (2 w)) sqrt(n / ln n).

    Note c ln 2 = (2/c') ln 2 = c', so the coefficient is exactly c'/(2 w).
    """
    ln2 = Decimal(2).ln()
    cprime = (2 * ln2).sqrt()
    c = 2 / cprime
    coeff = c * ln2 / (2 * Decimal(str(omega)))
    out = {
        "omega": omega,
        "coefficient_symbolic": "c ln 2 / (2 omega) = sqrt(2 ln 2) / (2 omega)",
        "coefficient_value": float(coeff),
        "coefficient_50dp": str(+coeff),
        "equals_cprime_over_2omega": float(cprime / (2 * Decimal(str(omega)))),
        "assumes_log2_N_equals_2_log2_n": True,
        "no_degree_measured": True,
    }
    if n is not None:
        val = float(coeff) * math.sqrt(n / math.log(n))
        out["n"] = n
        out["floor_value_at_n"] = val
        out["exceeds_assumption1_bound_4"] = val > 4.0
    return out


def floor_crossing_of_four(omega: float) -> int:
    """Smallest integer n at which the floor exceeds Assumption 1's d_F4 <= 4."""
    coeff = required_degree_floor(omega)["coefficient_value"]
    n = 10
    while coeff * math.sqrt(n / math.log(n)) <= 4.0:
        n += 1
        if n > 10 ** 7:
            raise RuntimeError("no crossing below 10^7")
    return n


# --------------------------------------------------------------------------
# Cost surfaces, monotonicity, near-optimal width
# --------------------------------------------------------------------------
def surface_row(n: int, reading: str, omega: float, omega_prime: float,
                typed: bool, yield_variant: str = "paper_raw",
                objective: str = "total") -> dict:
    """The full objective over m in [2, n] for one (n, reading, w, w', typing).

    Returns the shape facts the contract asks for -- argmin, monotonicity, every
    interior local minimum with its depth, and the near-optimal width -- plus
    the values themselves at a traceable grid of m. The full surface is written
    separately in binary form by the driver; this is the summary that travels
    inside the JSON.
    """
    ms = list(range(2, n + 1))
    if objective == "total":
        vals = [total_log2(n, m, reading, omega, omega_prime, typed,
                           yield_variant) for m in ms]
    elif objective == "stage1":
        vals = [stage1_log2(n, m, reading, omega, typed, yield_variant)
                for m in ms]
    else:
        raise ValueError(objective)
    imin = min(range(len(vals)), key=lambda i: vals[i])
    strictly_decreasing = all(vals[i + 1] < vals[i] for i in range(len(vals) - 1))
    nonincreasing = all(vals[i + 1] <= vals[i] + 1e-12
                        for i in range(len(vals) - 1))
    interior = []
    for i in range(1, len(vals) - 1):
        if vals[i] < vals[i - 1] and vals[i] < vals[i + 1]:
            interior.append({"m": ms[i], "value": vals[i],
                             "depth_below_right_boundary_bits":
                                 vals[-1] - vals[i]})
    boundary = vals[-1]
    near = [ms[i] for i in range(len(vals)) if vals[i] <= boundary + 1.0]
    near_argmin = [ms[i] for i in range(len(vals)) if vals[i] <= vals[imin] + 1.0]
    return {
        "n": n, "k_reading": reading, "omega": omega,
        "omega_prime": omega_prime, "typed": typed,
        "yield_variant": yield_variant, "objective": objective,
        "argmin_m": ms[imin], "argmin_value_log2": vals[imin],
        "value_at_m_2": vals[0], "value_at_m_n": boundary,
        "strictly_decreasing_in_m": strictly_decreasing,
        "nonincreasing_in_m": nonincreasing,
        "interior_local_minima_count": len(interior),
        "interior_local_minima": interior[:10],
        "deepest_interior_minimum_bits_below_boundary":
            (max(x["depth_below_right_boundary_bits"] for x in interior)
             if interior else None),
        "near_optimal_width_within_1_bit_of_boundary": len(near),
        "near_optimal_m_range_of_boundary": [min(near), max(near)] if near else [],
        "near_optimal_width_within_1_bit_of_argmin": len(near_argmin),
        "near_optimal_m_range_of_argmin":
            [min(near_argmin), max(near_argmin)] if near_argmin else [],
        "m_star_asymptotic": m_star_asymptotic(n),
        "values_at_traceable_m": {
            str(m): vals[ms.index(m)]
            for m in ([mm for mm in range(2, min(21, n + 1))]
                      + [mm for mm in range(30, n + 1, max(1, (n // 20) or 1))]
                      + [n])
            if m in ms},
    }


# --------------------------------------------------------------------------
# Vectorised surfaces (identical formulas; cross-checked against surface_row)
# --------------------------------------------------------------------------
def surface_arrays(n: int, reading: str):
    """(m, k, n - mk, log2(m!)) as numpy arrays over m in [2, n].

    The base quantities from which every (omega, omega') combination of both
    stages, typed and untyped, is an exact affine function -- which is why the
    full surfaces can be archived as these four arrays plus the formulas.
    """
    import numpy as np
    m = np.arange(2, n + 1, dtype=np.int64)
    if reading == "unceiled_n_over_m_as_in_table3":
        k = n / m
    elif reading == "ceil_n_over_m":
        k = np.ceil(n / m)
    else:
        raise ValueError(reading)
    log2_factorial(int(m[-1]))
    lf = np.asarray(_LOG2_FACT_CACHE[2:n + 1], dtype=np.float64)
    return m, k, n - m * k, lf


def surface_summary_vectorised(n: int, reading: str, omega: float,
                               omega_prime: float, typed: bool) -> dict:
    """Same summary as surface_row, computed with numpy at the paper_raw yield."""
    import numpy as np
    m, k, yexp, lf = surface_arrays(n, reading)
    log2m = np.log2(m.astype(np.float64))
    if typed:
        s1 = yexp + log2m + k + 4.0 * omega * math.log2(n)
        s2 = omega_prime * (k + log2m)
    else:
        s1 = lf + yexp + k + 4.0 * omega * math.log2(n)
        s2 = omega_prime * k
    hi = np.maximum(s1, s2)
    lo = np.minimum(s1, s2)
    tot = hi + np.log2(1.0 + np.exp2(np.maximum(lo - hi, -60.0)))
    out = {}
    for name, vals in (("stage1", s1), ("total", tot)):
        i = int(np.argmin(vals))
        d = np.diff(vals)
        strict = bool(np.all(d < 0))
        noninc = bool(np.all(d <= 1e-12))
        interior_mask = np.zeros(len(vals), dtype=bool)
        if len(vals) > 2:
            interior_mask[1:-1] = (vals[1:-1] < vals[:-2]) & (vals[1:-1] < vals[2:])
        idx = np.flatnonzero(interior_mask)
        boundary = float(vals[-1])
        near = int(np.count_nonzero(vals <= boundary + 1.0))
        near_arg = int(np.count_nonzero(vals <= float(vals[i]) + 1.0))
        nearm = m[vals <= boundary + 1.0]
        out[name] = {
            "argmin_m": int(m[i]),
            "argmin_value_log2": float(vals[i]),
            "value_at_m_2": float(vals[0]),
            "value_at_m_n": boundary,
            "strictly_decreasing_in_m": strict,
            "nonincreasing_in_m": noninc,
            "interior_local_minima_count": int(len(idx)),
            "interior_local_minima_m": [int(x) for x in m[idx][:10]],
            "deepest_interior_minimum_bits_below_boundary":
                (float(np.max(boundary - vals[idx])) if len(idx) else None),
            "near_optimal_width_within_1_bit_of_boundary": near,
            "near_optimal_m_range_of_boundary":
                [int(nearm.min()), int(nearm.max())] if len(nearm) else [],
            "near_optimal_width_within_1_bit_of_argmin": near_arg,
        }
    out.update({"n": n, "k_reading": reading, "omega": omega,
                "omega_prime": omega_prime, "typed": typed,
                "yield_variant": "paper_raw",
                "m_star_asymptotic": m_star_asymptotic(n)})
    return out


# --------------------------------------------------------------------------
# Control: the subset-sum corner (m = n, k = 1)
# --------------------------------------------------------------------------
def subset_sum_corner(n: int, omega: float = 3.0,
                      omega_prime: float = 2.0) -> dict:
    """The typed formula at m = n, k = 1. The RETURN is the reductio.

    At m = n the factor base is m single points and the decomposition problem is
    subset-sum over n group elements. A cost model that returns a polynomial
    value there has lost a constraint; a model that refused to return one, or
    returned an exponential one, would have been silently patched.
    """
    m, k = n, 1.0
    yield_exp = n - m * k
    s1 = yield_exp + math.log2(m) + k + 4.0 * omega * math.log2(n)
    s2 = omega_prime * (k + math.log2(m))
    tot = log2_add(s1, s2)
    return {
        "n": n, "m": m, "k": k, "omega": omega, "omega_prime": omega_prime,
        "formula_returned_a_value": True,
        "typed_stage1_log2": s1,
        "typed_stage1_closed_form": "log2(2 * n^{4w+1}) = 1 + (4w+1) log2 n",
        "typed_stage1_closed_form_value": 1.0 + (4.0 * omega + 1.0) * math.log2(n),
        "typed_stage2_log2": s2,
        "typed_stage2_closed_form": "log2((2n)^{w'}) = w'(1 + log2 n)",
        "typed_total_log2": tot,
        "is_polynomial_in_n": True,
        "polynomial_degree_in_n": 4.0 * omega + 1.0,
        "pollard_rho_log2": n / 2.0,
        "untyped_stage1_log2_same_corner":
            log2_factorial(n) + yield_exp + math.log2(1) + k
            + 4.0 * omega * math.log2(n),
        "reductio_note": ("The typed model prices subset-sum over n group "
                          "elements at n^{4w+1}. This is a REDUCTIO against a "
                          "premise of the model, never a claimed algorithm."),
    }


# --------------------------------------------------------------------------
# Control: proves-too-much on two nearby objects
# --------------------------------------------------------------------------
def nearby_object_gg_symmetrised(n: int, omega: float = 3.0,
                                 omega_prime: float = 2.0) -> dict:
    """(i) Galbraith-Gebregiyorgis's own symmetrised presentation.

    The localisation argument needs the per-solve cost to be UNIFORMLY
    polynomial in n, with no super-polynomial dependence on m; Semaev's chained
    presentation supplies that as n^{4w}. GG's presentation expresses the
    summation polynomial in elementary symmetric coordinates, where their own
    stated cost of coset typing is extra variables ("we require one more
    variable than the previous case, and things get worse for higher degree
    terms", transcribed in H-SEMBIN-c59e50's structural_ingredients).

    The control is run as a PARAMETRIC family: replace n^{4w} by n^{4w} G(m)
    and ask, for each G, whether the argument still collapses the objective.
    G is a declared parameter, NOT a measured degree; nothing here asserts any
    degree of any system.
    """
    gs = {
        "G_equals_1_semaev_chain": lambda m: 0.0,
        "G_equals_2_pow_m": lambda m: float(m),
        "G_equals_2_pow_m_log2_m": lambda m: m * math.log2(m),
        "G_equals_m_factorial": lambda m: log2_factorial(m),
        "G_equals_m_pow_2_polynomial_in_m": lambda m: 2.0 * math.log2(m),
    }
    out = {}
    for name, g in gs.items():
        vals = []
        for m in range(2, n + 1):
            k = k_of(n, m, "ceil_n_over_m")
            s1 = (n - m * k) + math.log2(m) + k + 4.0 * omega * math.log2(n) \
                + g(m)
            s2 = omega_prime * (k + math.log2(m))
            vals.append(log2_add(s1, s2))
        imin = min(range(len(vals)), key=lambda i: vals[i])
        m_poly = max(2, int(n / max(1.0, math.log2(n))))
        k_poly = k_of(n, m_poly, "ceil_n_over_m")
        poly_val = log2_add(
            (n - m_poly * k_poly) + math.log2(m_poly) + k_poly
            + 4.0 * omega * math.log2(n) + g(m_poly),
            omega_prime * (k_poly + math.log2(m_poly)))
        out[name] = {
            "argmin_m": imin + 2,
            "argmin_at_boundary_m_equals_n": (imin + 2) == n,
            "value_at_m_over_log2n_log2": poly_val,
            "polynomial_reference_log2_at_that_m":
                (4.0 * omega + 4.0) * math.log2(n),
            "collapses_to_polynomial":
                poly_val <= (4.0 * omega + 4.0) * math.log2(n) + 10.0,
            "pollard_rho_log2": n / 2.0,
            "beats_pollard_rho": poly_val < n / 2.0,
        }
    return {
        "n": n, "omega": omega, "omega_prime": omega_prime,
        "families": out,
        "per_n_flag_is_not_the_discriminator": (
            "the 'collapses_to_polynomial' flag above compares two numbers at a "
            "SINGLE n against a 10-bit slack, and at n = 283 that cannot "
            "separate G(m) = 2^m from a polynomial G: with m = n/log2 n = 34 "
            "the added 34 bits is small beside the 130-bit polynomial "
            "reference, so 2^m is flagged as collapsing even though it is "
            "super-polynomial. Polynomiality is a GROWTH property and is "
            "decided by gg_growth_discriminator below, across n. The per-n "
            "numbers are retained because they are what was computed, but they "
            "are not read as the verdict."),
        "argument_goes_through_only_when":
            "G(m) is polynomial in m (uniformly polynomial per-solve cost)",
        "gg_growth_discriminator": gg_growth_discriminator(omega, omega_prime),
        "gg_setting_verdict": (
            "The argument does NOT go through in GG's symmetrised presentation: "
            "their own stated cost of typing is additional variables per "
            "summand, i.e. a per-solve cost that is not uniform in m, and with "
            "any super-polynomial G(m) the value at m = n/log2 n grows faster "
            "than every polynomial in log2 n, as the growth discriminator "
            "shows. Read the growth table, not the single-n flag."),
        "provenance_note": (
            "GG's cost statements are transcribed from H-SEMBIN-c59e50's "
            "structural_ingredients and from this contract's inputs, not "
            "re-read from 2014/806 in this task."),
    }


def typed_interior_optimum_closed_form(ns: list[int], omega: float = 3.0,
                                       omega_prime: float = 2.0) -> dict:
    """The interior optimum the prediction says does not exist, in closed form.

    Under the un-ceiled reading k = n/m the yield exponent n - mk vanishes
    identically, so the typed objective of eq. (15) with GG's three
    substitutions reduces to

        T(m) = (1 + omega') * (n/m + log2 m) + 4 omega log2 n,

    whose only m-dependence is n/m + log2 m. That has

        dT/dm = 0  <=>  -n/m^2 + 1/(m ln 2) = 0  <=>  m = n ln 2,

    an INTERIOR stationary point for every n > 2/ln 2, and it is a minimum
    since the second derivative 2n/m^3 - 1/(m^2 ln 2) is positive there. Its
    depth below the m = n boundary is

        T(n) - T(n ln 2) = (1 + omega') * (1 - 1/ln 2 - log2(ln 2)),

    so the per-(1 + omega') depth is the absolute constant
    1 - 1/ln 2 - log2(ln 2) = 0.0860713... bits, INDEPENDENT OF n.

    The rising term that creates it is log2 m, and it enters from
    Galbraith-Gebregiyorgis's substitution of the typed relation store m 2^k
    for the untyped 2^k: m cosets of size 2^k hold m 2^k relations, worth
    +log2 m in stage 1 and +omega' log2 m in stage 2. That is the missed rising
    term the falsification criterion asks to be named.
    """
    unit_depth = 1.0 - 1.0 / math.log(2) - math.log2(math.log(2))
    rows = []
    for n in ns:
        m_opt = n * math.log(2)
        rows.append({
            "n": n,
            "argmin_m_closed_form_n_ln2": m_opt,
            "argmin_m_closed_form_rounded": int(round(m_opt)),
            "is_interior_for_this_n": 2 < m_opt < n,
            "depth_below_boundary_bits": (1.0 + omega_prime) * unit_depth,
            "depth_per_1_plus_omega_prime_bits": unit_depth,
            "second_derivative_at_optimum_positive": True,
        })
    return {
        "reading": "unceiled_n_over_m_as_in_table3",
        "objective": ("T(m) = (1 + omega')(n/m + log2 m) + 4 omega log2 n, the "
                      "typed objective with GG's three substitutions at "
                      "k = n/m, where the yield exponent n - mk vanishes"),
        "stationarity": "dT/dm = 0 <=> m = n ln 2",
        "argmin_is_interior_at_every_tested_n": True,
        "depth_closed_form": ("(1 + omega')(1 - 1/ln 2 - log2(ln 2)) bits "
                              "below the m = n boundary"),
        "unit_depth_bits_exact": unit_depth,
        "unit_depth_is_independent_of_n": True,
        "missed_rising_term_named": "log2 m",
        "where_the_missed_term_enters": (
            "GG's substitution of the typed relation store m 2^k for the "
            "untyped 2^k: m cosets of size 2^k hold m 2^k relations, "
            "contributing +log2 m to stage 1 and +omega' log2 m to stage 2"),
        "rows": rows,
        "relation_to_the_frozen_prediction": (
            "the frozen prediction states the typed objective is monotone "
            "DECREASING in m with the argmin at the boundary and NO interior "
            "optimum. This closed form exhibits an interior minimum at "
            "m = n ln 2 at every n, so the prediction is not met. The "
            "prediction is scored as written and is not adjusted."),
    }


def gg_growth_discriminator(omega: float = 3.0,
                            omega_prime: float = 2.0) -> dict:
    """Decide polynomiality by GROWTH in n, which is what the word means.

    A cost is polynomial in n exactly when its log2 is O(log2 n). So the test
    is whether value(n) / log2(n) stays BOUNDED as n grows, evaluated at the
    localisation argument's own operating point m = n / log2 n. A single n
    cannot answer this and the ratio below is what separates the families.

    The yield exponent is taken as max(0, n - mk): a negative exponent would be
    a relation probability above 1, which is not a probability. That cap is
    stated rather than assumed, because leaving it off is what let the
    single-n flag above misbehave.
    """
    ns = [163, 283, 409, 571, 1000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7]
    gs = {
        "G_equals_1_semaev_chain": (lambda m: 0.0, "polynomial"),
        "G_equals_m_pow_2_polynomial_in_m": (lambda m: 2.0 * math.log2(m),
                                             "polynomial"),
        "G_equals_2_pow_m": (lambda m: float(m), "super_polynomial"),
        "G_equals_2_pow_m_log2_m": (lambda m: m * math.log2(m),
                                    "super_polynomial"),
        "G_equals_m_factorial": (lambda m: log2_factorial(m),
                                 "super_polynomial"),
    }
    out = {}
    for name, (g, declared) in gs.items():
        series = []
        for n in ns:
            m = max(2, int(n / max(1.0, math.log2(n))))
            k = k_of(n, m, "ceil_n_over_m")
            s1 = max(0.0, n - m * k) + math.log2(m) + k \
                + 4.0 * omega * math.log2(n) + g(m)
            s2 = omega_prime * (k + math.log2(m))
            v = log2_add(s1, s2)
            series.append({"n": n, "m_operating_point": m,
                           "value_log2": v,
                           "value_over_log2n": v / math.log2(n)})
        r0 = series[0]["value_over_log2n"]
        r1 = series[-1]["value_over_log2n"]
        out[name] = {
            "declared_class_of_G": declared,
            "series": series,
            "value_over_log2n_at_smallest_n": r0,
            "value_over_log2n_at_largest_n": r1,
            "growth_factor_of_the_ratio": r1 / r0 if r0 else None,
            "ratio_bounded_i_e_polynomial": (r1 / r0) < 10.0 if r0 else None,
            "agrees_with_declared_class": (
                ((r1 / r0) < 10.0) == (declared == "polynomial")
                if r0 else None),
        }
    return {
        "test": ("value(n)/log2(n) bounded as n grows, at the argument's own "
                 "operating point m = n/log2 n, with the yield exponent capped "
                 "at max(0, n - mk)"),
        "n_grid": ns,
        "families": out,
        "all_families_agree_with_their_declared_class":
            all(v["agrees_with_declared_class"] for v in out.values()),
        "reading": (
            "the localisation argument collapses the objective to a polynomial "
            "ONLY for a per-solve cost G(m) that is polynomial in m. GG's "
            "symmetrised presentation states a per-summand variable cost, "
            "which is not of that form, so the argument fails on their own "
            "object -- the required proves-too-much outcome."),
    }


def nearby_object_trimoska(ns: list[int], ls: list[int]) -> dict:
    """(ii) Trimoska-Ionica-Dequen's search-side removal, total O~(2^{n+l}).

    Their Theorem 1 total is O~(2^{n+l}) and their proof KEEPS the probability
    factorial explicitly; the factorial they remove is the search-side
    redundancy inside one solver call. So the localisation transform -- delete
    the unique m-growing term of the yield -- has NO TARGET in their exponent,
    and their total stays above 2^{n/2} for every l >= 1.
    """
    grid = []
    for n in ns:
        for l in ls:
            total = float(n + l)
            grid.append({
                "n": n, "l": l,
                "their_total_log2": total,
                "pollard_rho_log2": n / 2.0,
                "worse_than_pollard_by_bits": total - n / 2.0,
                "beats_pollard_rho": total < n / 2.0,
            })
    return {
        "grid": grid,
        "localisation_transform_target_present_in_their_exponent": False,
        "verdict": (
            "The argument does NOT go through. The m! their construction "
            "removes is the SEARCH-side redundancy, not the yield factorial "
            "that carries the exponent; their exponent n + l contains no "
            "m-growing term to delete, and their solve is exponential in l, so "
            "the total remains at least 2^{n+1}, worse than 2^{n/2} at every "
            "(n, l) on the grid."),
        "provenance_note": (
            "Transcribed from H-SEMBIN-c59e50's structural_ingredients "
            "(iacr:2019/313 sections 4-5 and Theorem 1, provenance retrieved "
            "under TASK-20260913-6519c9); not re-read in this task."),
    }
