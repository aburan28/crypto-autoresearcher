"""ARMS N, K, P, M -- what Nagao's O(n^{8w+1}) costs, term by term.

EXP-SEMBIN-db9bc3.  Runs only after ARM C has reported and ARM R has passed.

WHAT IS BEING CHARGED, read off the frozen source
(inputs/NAGAO-2015-984/paper_fulltext.md, sha256 337fae55...e913218):

  Section 7:  k = C_0 fixed, m ~ n/C_0, V_i = V + v_i pairwise disjoint,
              Fb_i = {P : x(P) in V_i}, #Fb_i ~ p^{C_0}, #Fb ~ m p^{C_0} = O(n).
  Def. 8:     EQS4(m,R) is the Weil descent of the chained S_3 system over the
              disjoint cosets; Nagao's own remark on the unshifted EQS2 gives
              n(m-1) variables, and the shifted system has m C_0 + (m-2) n,
              which is n(m-1) when m C_0 = n.
  Prop. 5:    d_F(EQS4) <= 4 for p = 2 and <= 3p+1 for p >= 3, "the situation is
              the same as the Semaev's case.  So, we omit the proof."
  Lemma 2:    the monomial count is <= O(N^{d_F}) and the Groebner cost is
              <= O(N^{d_F w}).
  Section 7:  the decompose step is #Fb * (nm)^{4w}, the yield is "O(1)", the
              linear algebra step is (#Fb)^w and "very very small".
  Section 6:  "Many complicated terms are included into the o(1) term and so for
              normal size input n, o(1) has HUGE value."

THE FIVE ABSORBED TERMS, each its own reported column and never only a total
(H-SEMBIN-4a80f3 mechanism; handoff constraint 5):

  T1  log2 of the monomial count of the degree-d_F block on N variables.  Two
      readings, neither privileged: Nagao's own loose N^{d_F}, and the honest
      C(N+d_F, d_F).
  T2  the linear-algebra amplification (omega - 1) * T1, so that T1 + T2 is
      exactly Lemma 2's omega * log2(monomials) -- the cost of ONE solve.
  T3  log2(#Fb + 1) = log2(m p^{C_0} + 1): the number of relations that must be
      collected.  Nagao absorbs this as O(n); at C_0 = 16 it is not O(n) in any
      useful sense and the column says so numerically.
  T4  log2(1 / Pr[decomposition succeeds]).  Nagao charges 0 bits ("O(1)").
  T5  log2 of the memory, in field elements, which the source never mentions.

  T1 + T2 + T3 + T4          = log2 charged TIME of the decompose step
  T1 + T2 + T3 + T4 + T5     = log2 charged TIME x MEMORY product
  the index-calculus linear algebra omega * T3 is log-added to the time, per
  Section 7's own final sentence, and reported separately.

EVERY NUMBER IN THIS FILE IS MODELED, not measured: it is a closed-form
evaluation of the source's own formulas at stated parameters.  No system is
solved, no curve is touched, and no degree is measured.
"""

from __future__ import annotations

import math

import arm_c_coset as C
import semaev_repro as R

# The declared grid, copied from experiments/EXP-SEMBIN-db9bc3/specification.yaml
# independent_variables.  Not re-derived and not extended.
N_FIPS = [163, 233, 283, 409, 571]
OMEGA_SET = [2.376, 2.807, 3.0]
OMEGA_SOURCE_OWN = 2.7          # Nagao's "w ~ 2.7"; reported, not a 4th value
C0_RANGE = [2, 3, 4, 6, 8, 10, 12, 16]
METRICS = ["time_only", "time_memory_product", "area_time_AT", "equal_rate_max"]
READINGS = ["nagao_loose_N_to_the_d", "binomial_C_N_plus_d_choose_d"]
MEMORY_READINGS = ["frozen_width_C_N_plus_4_4", "dense_width_squared"]


# ---------------------------------------------------------------------------
# the shared code path.  p enters ONLY here and ONLY as Prop. 2 / Prop. 5 has
# it; there is no characteristic-2 special case anywhere below.
# ---------------------------------------------------------------------------


def d_F_bound(p: int, trace: list | None = None) -> int:
    """Nagao Prop. 2 and Prop. 5: d_F <= 4 (p = 2), <= 3p+1 (p >= 3)."""
    if trace is not None:
        trace.append(f"d_F_bound(p={p})")
    return 4 if p == 2 else 3 * p + 1


def theorem1_exponent(p: int, omega: float, trace: list | None = None) -> dict:
    """Theorem 1's exponent, DERIVED from the same formulas rather than quoted.

    decompose step = #Fb * (n m)^{d_F omega} with m ~ n/C_0 and #Fb = O(n), so
    the exponent in n is 2 d_F omega + 1.  At p = 2 that is 8w+1; at p >= 3,
    d_F = 3p+1 gives 2(3p+1)w+1 = (6p+2)w+1.  ONE formula, both branches.
    """
    if trace is not None:
        trace.append(f"theorem1_exponent(p={p},omega={omega})")
    d_f = d_F_bound(p, trace)
    return {"p": p, "omega": omega, "d_F": d_f,
            "exponent_in_n": 2.0 * d_f * omega + 1.0,
            "symbolic": f"2*{d_f}*w+1",
            "matches_source_form": ("8w+1" if p == 2 else f"({6 * p + 2})w+1")}


def m_of(n: int, c0: int, trace: list | None = None) -> int:
    """m ~ n/C_0, charged as ceil so that m C_0 >= n and the m cosets can carry
    a product of sizes reaching p^n.  The floor reading is reported as a
    sensitivity because the source writes only '~'."""
    if trace is not None:
        trace.append(f"m_of(n={n},C_0={c0})")
    return max(2, -((-n) // c0))


def variable_count(n: int, m: int, c0: int, trace: list | None = None) -> dict:
    """N.  The frozen quantity is n(m-1); the exact count for the SHIFTED system
    is m C_0 + (m-2) n, which differs from it by exactly m C_0 - n, the ceiling
    slack.  Both are reported: this is the precise place where the earlier
    round's disagreement lived (a parameter block giving a row width where it
    said variable count), so the two are never conflated here."""
    if trace is not None:
        trace.append(f"variable_count(n={n},m={m},C_0={c0})")
    frozen = n * (m - 1)
    exact_shifted = m * c0 + (m - 2) * n
    return {"N_frozen_n_times_m_minus_1": frozen,
            "N_exact_shifted_system": exact_shifted,
            "slack_m_C0_minus_n": m * c0 - n,
            "difference": exact_shifted - frozen}


def log2_monomials(n_vars: int, d_f: int, reading: str,
                   trace: list | None = None) -> float:
    """T1's two readings.  Exact integer binomial, then log2."""
    if trace is not None:
        trace.append(f"log2_monomials(reading={reading},d_F={d_f})")
    if reading == "nagao_loose_N_to_the_d":
        return d_f * math.log2(n_vars)
    if reading == "binomial_C_N_plus_d_choose_d":
        return R.log2_int(math.comb(n_vars + d_f, d_f))
    raise ValueError(reading)


def inverse_yield_bits(n: int, p: int, c0: int, m: int,
                       trace: list | None = None) -> dict:
    """T4.  Nagao charges 0 bits.  This charges HEUR-2 on top of HEUR-1.

    lambda = E[#decompositions of a random R] = prod_i #Fb_i / #E, and
    log2 prod_i #Fb_i = m C_0 log2 p - Delta with Delta the ARM C deficit, so
    log2 lambda = (m C_0 - n) log2 p - Delta.  Then P = 1 - exp(-lambda) (HEUR-2)
    and T4 = -log2 P.

    lambda is charged at the TYPICAL product (expected log), not at the mean
    product; the mean is inflated by the upper tail of the coset-size
    distribution and an attacker faces a typical instance.  The difference is
    exactly Delta and is reported as its own column.
    """
    if trace is not None:
        trace.append(f"inverse_yield_bits(n={n},p={p},C_0={c0},m={m})")
    deficit = C.total_log2_deficit(n, p, c0)
    log2_lambda = ((m * c0 - n) * math.log2(p)
                   - deficit["total_deficit_bits"])
    if log2_lambda > 20.0:
        t4 = 0.0
    elif log2_lambda < -40.0:
        t4 = -log2_lambda            # P ~ lambda to better than 1e-12 bits
    else:
        lam = 2.0 ** log2_lambda
        t4 = -math.log2(-math.expm1(-lam))
    return {"T4_inverse_yield_bits": t4,
            "log2_lambda": log2_lambda,
            "total_log2_deficit_bits": deficit["total_deficit_bits"],
            "per_coset_deficit_bits": deficit["per_coset_deficit_bits"],
            "source_charges_bits": 0.0,
            "absorbed_by_the_source_bits": t4}


_BOUND_A_CACHE: dict = {}
_BOUND_B_CACHE: dict = {}


def _bound_A_min(n: int, p: int):
    """ARM C bound A's C_0_min, memoised.  The bound itself is ARM C's; this is a
    read of it, never a recomputation with different conventions."""
    key = (n, p)
    if key not in _BOUND_A_CACHE:
        _BOUND_A_CACHE[key] = C.bound_A(n, p)["C_0_min"]
    return _BOUND_A_CACHE[key]


def _bound_B_min(n: int, p: int, tol_bits: float = 1.0):
    key = (n, p, tol_bits)
    if key not in _BOUND_B_CACHE:
        _BOUND_B_CACHE[key] = C.bound_B(n, p, tol_bits)["C_0_min"]
    return _BOUND_B_CACHE[key]


def nagao_cell(n: int, p: int, c0: int, omega: float, reading: str,
               d_f: int | None = None, trace: list | None = None,
               free_yield_null: bool = False,
               zero_memory_null: bool = False) -> dict:
    """One cell of the surface: every named term, the sum, and memory beside
    time.  No selection of C_0, no metric applied yet."""
    if trace is not None:
        trace.append(f"nagao_cell(n={n},p={p},C_0={c0},omega={omega})")
    if d_f is None:
        d_f = d_F_bound(p, trace)
    m = m_of(n, c0, trace)
    nv = variable_count(n, m, c0, trace)
    n_vars = nv["N_frozen_n_times_m_minus_1"]

    t1 = log2_monomials(n_vars, d_f, reading, trace)
    t2 = (omega - 1.0) * t1
    factor_base_log2 = math.log2(m) + c0 * math.log2(p)
    t3 = R.log2_add(factor_base_log2, 0.0)          # log2(#Fb + 1)
    y = inverse_yield_bits(n, p, c0, m, trace)
    t4 = 0.0 if free_yield_null else y["T4_inverse_yield_bits"]
    # T5 is the MACAULAY WIDTH in field elements, which is the monomial count of
    # the degree-d_F block: C(N + d_F, d_F).  It is charged at the BINOMIAL count
    # regardless of which reading T1 uses, because the width of a matrix is a
    # count of columns and Nagao's loose N^{d_F} is an upper bound on that count
    # rather than a second reading of it.  At d_F = 4 this is exactly ARM I's
    # declared quantity C(N+4,4), so the two arms compare cell for cell.
    t5_frozen = log2_monomials(n_vars, d_f, "binomial_C_N_plus_d_choose_d", trace)
    t5_dense = 2.0 * t5_frozen       # a dense square block, the other reading
    t5 = 0.0 if zero_memory_null else t5_frozen

    time_decompose = t1 + t2 + t3 + t4
    time_linalg = omega * t3
    time_total = R.log2_add(time_decompose, time_linalg)

    bound_a = _bound_A_min(n, p)
    bound_b = _bound_B_min(n, p)
    return {
        "n": n, "p": p, "C_0": c0, "omega": omega, "d_F": d_f,
        "monomial_count_reading": reading,
        "m": m,
        "N_frozen": n_vars,
        "N_exact_shifted_system": nv["N_exact_shifted_system"],
        "N_readings_differ_by": nv["difference"],
        "T1_monomial_count_log2": t1,
        "T2_linear_algebra_exponent_log2": t2,
        "T3_coset_constant_log2": t3,
        "T4_inverse_yield_log2": t4,
        "T5_memory_log2": t5,
        "T5_memory_log2_frozen_width": t5_frozen,
        "T5_memory_log2_dense_width_squared": t5_dense,
        "sum_T1_to_T4_time_decompose_log2": time_decompose,
        "T6_index_calculus_linalg_log2": time_linalg,
        "time_log2_total": time_total,
        "sum_T1_to_T5_time_memory_product_log2": time_total + t5,
        "log2_lambda": y["log2_lambda"],
        "total_log2_deficit_bits": y["total_log2_deficit_bits"],
        "source_absorbed_T3_as": "O(n)",
        "source_absorbed_T4_as": "O(1) yield, i.e. 0 bits",
        "source_absorbed_T5_as": "not mentioned at all",
        "theorem1_stated_exponent_cost_log2":
            theorem1_exponent(p, omega, trace)["exponent_in_n"] * math.log2(n),
        "C_0_satisfies_ARM_C_bound_A": (bound_a is not None and c0 >= bound_a),
        "C_0_satisfies_ARM_C_bound_B_1bit": (bound_b is not None and c0 >= bound_b),
        "ARM_C_bound_A": bound_a,
        "ARM_C_bound_B_1bit": bound_b,
        "free_yield_null": free_yield_null,
        "zero_memory_null": zero_memory_null,
        "modeled_not_measured": True,
    }


# ---------------------------------------------------------------------------
# metric application and the margin against vOW at its own Pareto minimum
# ---------------------------------------------------------------------------


def nagao_metric_value(cell: dict, metric: str,
                       memory_reading: str = "frozen_width_C_N_plus_4_4"
                       ) -> float:
    mem = (cell["T5_memory_log2_frozen_width"]
           if memory_reading == "frozen_width_C_N_plus_4_4"
           else cell["T5_memory_log2_dense_width_squared"])
    if cell["zero_memory_null"]:
        mem = 0.0
    t = cell["time_log2_total"]
    if metric == "time_only":
        return t
    if metric in ("time_memory_product", "area_time_AT"):
        return t + mem
    if metric == "equal_rate_max":
        return max(t, mem)
    raise ValueError(metric)


def margin(cell: dict, metric: str,
           memory_reading: str = "frozen_width_C_N_plus_4_4") -> dict:
    """SIGN CONVENTION, this contract's: margin = Nagao - vOW, POSITIVE meaning
    NAGAO IS WORSE.  This is the OPPOSITE of COST-SEMBIN-8d123b's convention,
    which ARM R reproduces in its own sign; both are stated wherever used."""
    nag = nagao_metric_value(cell, metric, memory_reading)
    vow = R.vow_pareto_minimum(cell["n"], metric)
    return {"metric": metric, "memory_reading": memory_reading,
            "nagao_metric_log2": nag,
            "vow_pareto_minimum_log2": vow["metric_log2"],
            "vow_operating_point": vow["point"],
            "margin_bits_nagao_minus_vow": nag - vow["metric_log2"],
            "nagao_ahead": bool(nag < vow["metric_log2"])}


def crossover(p: int, c0: int, omega: float, metric: str, reading: str,
              memory_reading: str = "frozen_width_C_N_plus_4_4",
              n_lo: int = 16, n_hi: int = 3000, d_f: int | None = None) -> dict:
    """Smallest n at which Nagao's charged cost falls below vOW's, per cell.

    Reported as one point of a SURFACE over (omega, C_0, metric, reading), never
    as 'the' crossover: EV-SEMBIN-71e5cd O-9 fired on exactly that collapse and
    handoff constraint 3 forbids it.
    """
    first = None
    for n in range(n_lo, n_hi + 1):
        if n <= c0:
            continue
        cell = nagao_cell(n, p, c0, omega, reading, d_f)
        if margin(cell, metric, memory_reading)["nagao_ahead"]:
            first = n
            break
    monotone = None
    if first is not None:
        monotone = all(
            margin(nagao_cell(n, p, c0, omega, reading, d_f), metric,
                   memory_reading)["nagao_ahead"]
            for n in range(first, min(n_hi, first + 200) + 1))
    return {"p": p, "C_0": c0, "omega": omega, "metric": metric,
            "monomial_count_reading": reading, "memory_reading": memory_reading,
            "crossover_n": first,
            "reason_if_none": (None if first is not None else
                               f"no crossover for n in [{n_lo}, {n_hi}]"),
            "monotone_for_200_beyond": monotone}


# ---------------------------------------------------------------------------
# unit disclosure, quantified
# ---------------------------------------------------------------------------


def unit_conversion_sensitivity(n: int) -> dict:
    """The largest single source of imprecision in the comparison, disclosed
    rather than modelled -- exactly as COST-SEMBIN-8d123b discloses it.

    Nagao's cost is counted in F_p-operations on a Macaulay block -- at p = 2
    one bit operation -- while vOW's is counted in GROUP operations, and a group
    operation on E(F_{2^n}) costs a field inversion plus a few multiplications,
    of order n^2 bit operations schoolbook.  So the two units differ by about
    n^2 IN vOW's FAVOUR AS CHARGED: expressing both in bit operations leaves
    Nagao's figure essentially unchanged and RAISES vOW's by ~2 log2 n.

    NO CONVERSION IS APPLIED to any figure in this run, because the frozen
    source supplies none.  The direction matters and is stated exactly: the
    figures as reported are PESSIMISTIC for Nagao by this amount, so applying a
    conversion would WIDEN any Nagao advantage rather than close it.  This
    disclosure therefore cannot be read as a reserve that might absorb an
    observed margin.
    """
    return {"n": n,
            "unconverted": True,
            "bits_that_would_be_added_to_vow_if_a_group_op_cost_n_squared":
                2.0 * math.log2(n),
            "bits_that_would_be_added_if_a_group_op_cost_n_log_n":
                math.log2(n) + math.log2(math.log2(n)),
            "bits_that_would_be_added_to_nagao": 0.0,
            "direction": ("applying any conversion moves the comparison IN "
                          "NAGAO'S FAVOUR, because vOW's unit is the more "
                          "expensive one and is charged as though it were "
                          "free; the figures as reported are PESSIMISTIC for "
                          "Nagao by this amount and no observed margin can be "
                          "explained away by it")}
