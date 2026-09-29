"""ARM R -- the reproduction gate.  RUNS SECOND.  HARD GATE.

EXP-SEMBIN-db9bc3, ARM R.  No cell of ARMS N, K, P, M or I is reported unless
this arm passes at its declared tolerance.  A failed reproduction is an
IMPLEMENTATION FAILURE and is not evidence about Nagao (core rule 5).

WHAT IS REPRODUCED, and the target is the CORRECTED figures:
  * COST-SEMBIN-8d123b's five-label Semaev table (time, dense and sparse
    memory, optimal m, vOW time, and all three margins), superseded in scope by
    DEC-20260913-74e208, whose time column already uses the eq. (11) yield
    charge because it uses UN-CEILED k, where CORR-20260913-53739b
    correction_1's two charges agree to 0.00e+00.
  * CORR-20260913-53739b correction_1's authoritative eq. (11) figures at
    INTEGER k = ceil(n/m), which is where the two charges DIVERGE: stage-1 at
    (571, 12, 48), the re-optimised totals and their argmins, the crossovers
    281 / 295 / 337 / 393, and the measured overcharge statistics.  The
    m!-ONLY figures (186.7 / 186.4 / 303 ...) are the UNCORRECTED ones; they are
    computed here too and reproducing THEM is recorded as a failure, not a pass.
  * EV-SEMBIN-71e5cd O-6's exactly 29.0 bits, so that this run's vOW baseline is
    validated against the recorded measurement of the dominated charge before it
    is used anywhere.
  * The DEGENERATE SLICE of H-SEMBIN-4a80f3's baseline_embedding: C_0 = k,
    m = n/k, m! yield restored, which must return the same figures.

Every formula below is written from the frozen source and from the record's own
stated conventions.  Nothing is imported from the implementation being
reproduced.

TOLERANCE, declared before the arm runs: 1e-3 bits per cell against any target
quoted with three or more decimals; against a target quoted to one decimal, the
check is at that target's own printed precision (5e-2) and the full-precision
value is reported beside it, because a 1e-3 comparison against a 1-decimal
number is not a test that can be passed or failed.  Integers must match exactly.
"""

from __future__ import annotations

import math

LOG2_0886 = math.log2(0.886)   # vOW walk constant, RELAYED via KN-TECH-006 /
                               # KN-LIT-012 through COST-SEMBIN-8d123b; the
                               # primary paper was not opened by this program.
BITS_PER_WORD = 64.0


# ---------------------------------------------------------------------------
# primitives
# ---------------------------------------------------------------------------


def log2_int(value: int) -> float:
    """log2 of an exact positive integer without float overflow."""
    if value <= 0:
        raise ValueError(value)
    bits = value.bit_length()
    if bits <= 53:
        return math.log2(value)
    shift = bits - 53
    return float(shift) + math.log2(value >> shift)


def log2_factorial(m: int) -> float:
    """Exact integer factorial, then log2.  No lgamma, so the value is exact to
    float rounding rather than to lgamma's own error."""
    return log2_int(math.factorial(m))


def log2_add(a: float, b: float) -> float:
    """log2(2^a + 2^b), stable."""
    hi, lo = max(a, b), min(a, b)
    if hi - lo > 60.0:
        return hi
    return hi + math.log2(1.0 + 2.0 ** (lo - hi))


def k_of(n: int, m: int, reading: str) -> float:
    if reading == "unceiled":
        return n / m
    if reading == "ceiled":
        return float(-(-n // m))
    raise ValueError(reading)


def log2_boolean_monomials(n_vars: int, degree: int) -> float:
    """log2 sum_{d<=degree} C(N, d): the SQUAREFREE monomial count, which is the
    count over F_2 once the field equations X^2 = X are imposed.

    This is the count COST-SEMBIN-8d123b uses, and it is NOT the same object as
    this contract's ARM I quantity C(N+4,4), which counts monomials of degree
    <= 4 without the field equations.  The two differ by under 0.01 bits at the
    N of these cells, and both are reported rather than conflated.
    """
    return log2_int(sum(math.comb(n_vars, d) for d in range(degree + 1)))


# ---------------------------------------------------------------------------
# the Semaev side, both yield charges
# ---------------------------------------------------------------------------


def semaev_stage1_log2(n: int, m: int, omega: float = 3.0,
                       yield_charge: str = "eq11",
                       k_reading: str = "unceiled",
                       d_sat: int | None = None, d_unsat: int = 4) -> dict:
    """log2 of stage 1.

    yield_charge:
      'eq11'   -- 1/P = m! 2^{n-mk}, Semaev eq. (11) linearised, the FAITHFUL
                  charge per CORR-20260913-53739b correction_1
      'm_only' -- 1/P = m!, the UNCORRECTED charge

    d_sat is None for COST-SEMBIN-8d123b's single-term stage 1
    (2^k * (1/P) * n^{4 omega}); giving d_sat selects correction_1's two-term
    form 2^k * ((1/P) n^{d_unsat omega} + n^{d_sat omega}).
    """
    k = k_of(n, m, k_reading)
    inv_p = log2_factorial(m)
    if yield_charge == "eq11":
        inv_p += (n - m * k)
    elif yield_charge != "m_only":
        raise ValueError(yield_charge)
    log2n = math.log2(n)
    if d_sat is None:
        stage1 = k + inv_p + d_unsat * omega * log2n
    else:
        stage1 = k + log2_add(inv_p + d_unsat * omega * log2n,
                              d_sat * omega * log2n)
    return {"log2_stage1": stage1, "k": k, "log2_inverse_yield": inv_p}


def semaev_time_log2(n: int, m: int, omega: float = 3.0,
                     omega_prime: float = 2.0, yield_charge: str = "eq11",
                     k_reading: str = "unceiled", d_sat: int | None = None,
                     d_unsat: int = 4) -> dict:
    s1 = semaev_stage1_log2(n, m, omega, yield_charge, k_reading, d_sat, d_unsat)
    stage2 = s1["k"] * omega_prime
    return {"log2_stage1": s1["log2_stage1"], "log2_stage2": stage2,
            "log2_total": log2_add(s1["log2_stage1"], stage2), "k": s1["k"],
            "log2_inverse_yield": s1["log2_inverse_yield"]}


def semaev_memory_degree_sensitivity(n: int, m: int, degree: int) -> float:
    """Bits added to the DENSE memory reading by raising the degree bound from 4.

    RECORDED OBSERVATION about the target, not about Semaev: 8d123b's
    `degree_bound_sensitivity` block is labelled as applying to "every time and
    memory figure", and its own stated time charge n^{4 omega} would add
    omega log2 n = 24.83 bits at n = 310 for a bound of 5.  The tabulated value
    is 18.246.  It is reproduced EXACTLY -- to 1e-3 at all six cells -- by the
    change in the DENSE WORKING SET alone, 2 (log2 W_D - log2 W_4) with
    W_D = sum_{d<=D} C(N, d).  The block is therefore a memory sensitivity that
    the surrounding prose reads as a time-and-memory one.  Both quantities are
    reported here so a later reader can see which the figures are.
    """
    base = semaev_memory_log2(n, m, 4, "dense")["working_set_log2_bits"]
    at_d = semaev_memory_log2(n, m, degree, "dense")["working_set_log2_bits"]
    return at_d - base


def semaev_memory_log2(n: int, m: int, degree: int = 4,
                       storage: str = "dense") -> dict:
    """Memory in log2 BITS.  The paper states no memory model; both readings are
    from the recorded ellipticnews/ePrint dispute and neither is privileged."""
    k_int = int(math.ceil(k_of(n, m, "ceiled")))
    row_bits = m * k_int + 2 * n
    store = float(k_int) + math.log2(row_bits)
    n_vars = (m - 2) * n + k_int * m
    width = log2_boolean_monomials(n_vars, degree)
    if storage == "dense":
        working = 2.0 * width
    elif storage == "semaev_sparse":
        working = (4.0 * math.log2(n * m) - math.log2(24.0)
                   + 3.0 * math.log2(n) - math.log2(m))
    else:
        raise ValueError(storage)
    return {"relation_store_log2_bits": store, "macaulay_nvars": n_vars,
            "macaulay_width_log2": width, "working_set_log2_bits": working,
            "log2_total_bits": log2_add(store, working),
            "dominant_term": "working_set" if working > store else
                             "relation_store"}


def semaev_optimal_m(n: int, omega: float = 3.0, omega_prime: float = 2.0,
                     yield_charge: str = "eq11", k_reading: str = "unceiled",
                     m_hi: int = 30, d_sat: int | None = None,
                     d_unsat: int = 4) -> int:
    """argmin over m of STAGE 1, which is the quantity Section 4.5.2 minimises."""
    return min(range(2, min(m_hi, n) + 1),
               key=lambda m: semaev_stage1_log2(n, m, omega, yield_charge,
                                                k_reading, d_sat,
                                                d_unsat)["log2_stage1"])


# ---------------------------------------------------------------------------
# the baseline, on its own curve
# ---------------------------------------------------------------------------


def vow_walk_work_log2(n: int) -> float:
    """log2 W, the total walk work: 0.886 sqrt(q) with q = 2^n.

    The cofactor of the FIPS binary curves (2 or 4) is neglected, which makes
    rho look marginally CHEAPER than it is and therefore does not flatter the
    attack side.
    """
    return LOG2_0886 + n / 2.0


def vow_at_operating_point(n: int, log2_processors: float,
                           log2_store: float) -> dict:
    """One point of the vOW curve: T = W(1/M + 1/w), Mem = 3n max(w, M).

    EV-SEMBIN-71e5cd O-6 measured that charging the MEMORY of a 2^30 store and
    the TIME of one processor -- two different points of this curve -- overcharges
    the baseline by exactly 29.0 bits at n = 283, 310, 409 and 571 alike.  That
    incoherent charge is reproduced here BY NAME so the correction is auditable,
    and is never used as this run's baseline.
    """
    m_proc = 2.0 ** log2_processors
    w = 2.0 ** log2_store
    time = vow_walk_work_log2(n) + math.log2(1.0 / m_proc + 1.0 / w)
    mem = math.log2(3.0 * n * max(w, m_proc))
    return {"log2_time": time, "log2_memory_bits": mem,
            "log2_processors": log2_processors, "log2_store": log2_store}


def vow_dominated_charge_8d123b(n: int) -> dict:
    """COST-SEMBIN-8d123b's own charge: time of ONE processor, memory of a 2^30
    point store.  Reproduced to validate against O-6, not used as a baseline."""
    return {"log2_time": vow_walk_work_log2(n),
            "log2_memory_bits": 30.0 + math.log2(3.0 * n)}


def vow_pareto_minimum(n: int, metric: str) -> dict:
    """The baseline charged at the Pareto minimum of ITS OWN curve, per metric.

    T x Mem = 3n W (max(w,M)/M + max(w,M)/w) >= 2 * 3n * W, invariant along
    w = M with the minimum anywhere on that ray, so the product minimum is
    6nW exactly.  max(T, Mem) is minimised where 2W/M = 3nM, giving
    sqrt(6nW).  TIME ALONE has no interior minimum -- it falls without bound in
    the processor count, and so does the attack side -- so the time-only metric
    is charged at the DECLARED single-processor total-work point M = 1, w -> inf,
    which is total sequential work W and is exactly the convention
    COST-SEMBIN-8d123b's vow_time_log2 uses.  That declaration is recorded here
    rather than left implicit, because it is the one place where 'Pareto
    minimum' does not by itself pick a point.
    """
    w_log2 = vow_walk_work_log2(n)
    product_min = math.log2(6.0 * n) + w_log2
    if metric == "time_only":
        return {"metric_log2": w_log2, "log2_time": w_log2,
                "log2_memory_bits": None,
                "point": "M = 1, w -> inf (declared total-work convention)"}
    if metric in ("time_memory_product", "area_time_AT"):
        return {"metric_log2": product_min, "log2_time": None,
                "log2_memory_bits": None,
                "point": "anywhere on w = M; T x Mem = 6nW is invariant there"}
    if metric == "equal_rate_max":
        return {"metric_log2": product_min / 2.0, "log2_time": None,
                "log2_memory_bits": None,
                "point": "w = M = sqrt(2W/(3n)); max(T, Mem) = sqrt(6nW)"}
    raise ValueError(metric)


# ---------------------------------------------------------------------------
# metric combination, in COST-SEMBIN-8d123b's own names and sign convention
# ---------------------------------------------------------------------------

METRICS_8D123B = ["time_only_zero_memory_weight", "time_memory_product",
                  "area_time_AT", "equal_rate_max_of_time_and_memory"]


def metric_value(log2_time: float, log2_memory_bits: float,
                 metric: str) -> float:
    mem = log2_memory_bits if log2_memory_bits is not None else -1e9
    if metric == "time_only_zero_memory_weight":
        return log2_time
    if metric in ("time_memory_product", "area_time_AT"):
        return log2_time + mem
    if metric == "equal_rate_max_of_time_and_memory":
        return max(log2_time, mem)
    raise ValueError(metric)


def compare_8d123b(n: int, metric: str, storage: str, degree: int = 4,
                   omega: float = 3.0, omega_prime: float = 2.0,
                   yield_charge: str = "eq11",
                   k_reading: str = "unceiled") -> dict:
    """One row of COST-SEMBIN-8d123b's comparison, in ITS sign convention:
    margin = baseline - semaev, POSITIVE meaning SEMAEV WINS.

    This is the OPPOSITE of the convention EXP-SEMBIN-db9bc3 declares for ARM N
    (margin = Nagao - vOW, positive meaning NAGAO IS WORSE).  Both are used in
    this run, in their own arms, and the difference is stated here so that a
    reader cannot mistake a declared sign convention for a disagreement -- the
    exact failure a shared inverted sign convention produced in the earlier
    round (validator TASK-20260913-da3982, proves-too-much object 3).
    """
    m = semaev_optimal_m(n, omega, omega_prime, yield_charge, k_reading)
    t = semaev_time_log2(n, m, omega, omega_prime, yield_charge, k_reading)
    mem = semaev_memory_log2(n, m, degree, storage)
    base = vow_dominated_charge_8d123b(n)
    sem = metric_value(t["log2_total"], mem["log2_total_bits"], metric)
    bas = metric_value(base["log2_time"], base["log2_memory_bits"], metric)
    return {"n": n, "m_optimal": m, "metric": metric, "storage": storage,
            "semaev_log2_time": t["log2_total"],
            "semaev_log2_memory_bits": mem["log2_total_bits"],
            "baseline_log2_time": base["log2_time"],
            "baseline_log2_memory_bits": base["log2_memory_bits"],
            "margin_bits_8d123b_sign": bas - sem,
            "semaev_wins": bool(sem < bas)}


def crossover_8d123b(metric: str, storage: str, n_lo: int = 250,
                     n_hi: int = 650, **kw):
    for n in range(n_lo, n_hi + 1):
        if compare_8d123b(n, metric, storage, **kw)["semaev_wins"]:
            return n
    return None


def crossover_vs_bare_rho(d_sat: int, yield_charge: str, k_reading: str,
                          omega: float = 3.0, omega_prime: float = 2.0,
                          d_unsat: int = 4, n_lo: int = 100, n_hi: int = 900,
                          use_total: bool = True):
    """CORR-20260913-53739b's crossover convention: the RE-OPTIMISED cost
    against a bare 2^{n/2}, with no walk constant on the baseline."""
    for n in range(n_lo, n_hi + 1):
        m = semaev_optimal_m(n, omega, omega_prime, yield_charge, k_reading,
                             30, d_sat, d_unsat)
        t = semaev_time_log2(n, m, omega, omega_prime, yield_charge, k_reading,
                             d_sat, d_unsat)
        val = t["log2_total"] if use_total else t["log2_stage1"]
        if val < n / 2.0:
            return n
    return None


def reoptimised_total(n: int, d_sat: int, yield_charge: str,
                      k_reading: str = "ceiled", omega: float = 3.0,
                      omega_prime: float = 2.0, d_unsat: int = 4) -> dict:
    m = semaev_optimal_m(n, omega, omega_prime, yield_charge, k_reading, 30,
                         d_sat, d_unsat)
    t = semaev_time_log2(n, m, omega, omega_prime, yield_charge, k_reading,
                         d_sat, d_unsat)
    return {"n": n, "m": m, "k": int(t["k"]), "log2_total": t["log2_total"],
            "log2_stage1": t["log2_stage1"]}


def exact_yield_control(n: int, m: int, k_reading: str = "ceiled") -> dict:
    """CORR-20260913-53739b correction_1 control_the_linearisation: eq. (11)
    linearised against the unlinearised P = 1 - (1 - 1/q)^K."""
    k = k_of(n, m, k_reading)
    log2_lambda = m * k - n - log2_factorial(m)
    lam = 2.0 ** log2_lambda
    # P = 1 - (1 - 2^{-n})^{K}, K = 2^{mk}/m!; log-space
    log_one_minus = math.log1p(-2.0 ** (-n))
    log_p_exact = math.log1p(-math.exp(lam * (2.0 ** n) * log_one_minus))
    return {"log2_lambda": log2_lambda,
            "log2_inv_P_linearised": -log2_lambda,
            "log2_inv_P_exact": -log_p_exact / math.log(2.0)}


# ---------------------------------------------------------------------------
# the degenerate slice: Nagao's accounting at C_0 = k reduces to Semaev's
# ---------------------------------------------------------------------------


def degenerate_slice(n: int, m: int, omega: float = 3.0) -> dict:
    """H-SEMBIN-4a80f3 baseline_embedding: set C_0 = k, m = n/k, RESTORE the m!
    yield that the disjoint construction removes, and collapse the m disjoint
    cosets to one shared V.  At that slice the disjoint-coset accounting IS the
    unshifted accounting, so the same figure must come back out.

    Charged from the NAGAO side's own quantities: relation count #Fb = p^{C_0}
    (one shared V, so no factor m), per-solve cost n^{4 omega} by Lemma 2, and
    the restored inverse yield m! 2^{n - m C_0}.

    Reported at BOTH readings of C_0:
      un-ceiled C_0 = n/m, Table 3's own convention -- the two sides must agree
        EXACTLY (difference 0), and that exact agreement is the gate cell;
      integer C_0 = ceil(n/m) -- both sides carry the same integer k, so the
        identity is again exact (difference 0).  The ceiling slack C_0 - n/m
        is reported beside it as its own number so that a reader comparing
        the ceiled and un-ceiled rows sees where their difference comes from.
    (Attempt 2 corrected this docstring: attempt 1's text claimed the ceiled
    rows differ by the slack, which the implementation never did; the
    self-test now pins difference 0 at both readings.)
    """
    out = {"n": n, "m": m, "omega": omega}
    per_solve = 4.0 * omega * math.log2(n)
    for reading in ("unceiled", "ceiled"):
        c0 = k_of(n, m, reading)
        nagao = c0 + per_solve + log2_factorial(m) + (n - m * c0)
        semaev = semaev_stage1_log2(n, m, omega, "eq11", reading)["log2_stage1"]
        out[reading] = {
            "C_0": c0,
            "nagao_degenerate_log2_stage1": nagao,
            "semaev_log2_stage1": semaev,
            "difference_bits": nagao - semaev,
            "predicted_difference_bits": 0.0,
            "agrees_to_1e_9": abs(nagao - semaev) < 1e-9,
        }
    out["ceiling_slack_bits_closed_form"] = k_of(n, m, "ceiled") - n / m
    return out


# ---------------------------------------------------------------------------
# the gate itself: every target cell, its reproduction, and the error
# ---------------------------------------------------------------------------

TABLE_8D123B = {
    163: dict(time=123.7697, dense=70.3526, sparse=55.2782, m=7, vow=81.3254,
              mt=-42.4443, mtd=-73.8632, mts=-58.7888),
    233: dict(time=138.7283, dense=77.7467, sparse=59.9741, m=9, vow=116.3254,
              mt=-22.4029, mtd=-60.7004, mts=-42.9278),
    283: dict(time=147.6495, dense=80.0103, sparse=61.9374, m=9, vow=141.3254,
              mt=-6.3241, mtd=-46.6047, mts=-28.5319),
    409: dict(time=166.5438, dense=86.8371, sparse=66.5250, m=11, vow=204.3254,
              mt=37.7816, mtd=-8.7946, mts=11.5175),
    571: dict(time=186.3070, dense=91.7726, sparse=70.2718, m=12, vow=285.3254,
              mt=99.0184, mtd=47.9882, mts=69.4889),
}


def _cell(name: str, reproduced, target, tol: float, group: str,
          integer: bool = False) -> dict:
    if integer:
        err = 0.0 if reproduced == target else float("inf")
        passed = reproduced == target
    else:
        err = abs(float(reproduced) - float(target))
        passed = err <= tol
    return {"cell": name, "group": group, "reproduced": reproduced,
            "target": target, "abs_error_bits": (None if integer else err),
            "integer_exact_match": (passed if integer else None),
            "tolerance": (None if integer else tol), "passed": bool(passed)}


def reproduction_cells() -> list:
    """Every cell of the ARM R gate.

    TOLERANCES, declared here rather than chosen per cell after the fact:
      1e-3 bits against a target printed to >= 4 decimals;
      5e-2 bits against a target printed to 1 decimal (a 1e-3 comparison
        against a 1-decimal number is not a test that can be passed);
      5e-3 bits against a target printed to 2 decimals;
      exact equality for every integer (m, k, crossover n).
    The one-decimal cells are ALSO reported at full precision beside their
    rounded reproduction so a reader can see the agreement is not marginal.
    """
    cells = []

    # -- group 1: the five-label table, as printed (eq. 11 at un-ceiled k,
    #    where CORR-20260913-53739b correction_1 records the two yield charges
    #    agreeing to 0.00e+00, so this group is corrected-and-uncorrected alike
    for n, tg in TABLE_8D123B.items():
        m = semaev_optimal_m(n)
        t = semaev_time_log2(n, m)["log2_total"]
        md = semaev_memory_log2(n, m, 4, "dense")["log2_total_bits"]
        ms = semaev_memory_log2(n, m, 4, "semaev_sparse")["log2_total_bits"]
        base = vow_dominated_charge_8d123b(n)
        dom = base["log2_time"] + base["log2_memory_bits"]
        g = "8d123b_table"
        cells += [
            _cell(f"semaev_optimal_m[n={n}]", m, tg["m"], 0, g, integer=True),
            _cell(f"semaev_time_log2[n={n}]", t, tg["time"], 1e-3, g),
            _cell(f"semaev_memory_log2_dense[n={n}]", md, tg["dense"], 1e-3, g),
            _cell(f"semaev_memory_log2_sparse[n={n}]", ms, tg["sparse"], 1e-3, g),
            _cell(f"vow_time_log2[n={n}]", base["log2_time"], tg["vow"], 1e-3, g),
            _cell(f"margin_bits_time_only[n={n}]", base["log2_time"] - t,
                  tg["mt"], 1e-3, g),
            _cell(f"margin_bits_time_memory_dense[n={n}]", dom - (t + md),
                  tg["mtd"], 1e-3, g),
            _cell(f"margin_bits_time_memory_sparse[n={n}]", dom - (t + ms),
                  tg["mts"], 1e-3, g),
        ]

    # -- group 2: 8d123b's crossovers, ceiling discrepancy, degree sensitivity
    g = "8d123b_crossovers"
    for metric, tgs in [("time_only_zero_memory_weight", (303, 303)),
                        ("time_memory_product", (435, 375)),
                        ("area_time_AT", (435, 375)),
                        ("equal_rate_max_of_time_and_memory", (303, 303))]:
        for storage, tgv in zip(("dense", "semaev_sparse"), tgs):
            cells.append(_cell(f"crossover[{metric},{storage}]",
                               crossover_8d123b(metric, storage, 250, 700),
                               tgv, 0, g, integer=True))
    cells.append(_cell("crossover_published[stage1_vs_bare_rho,unceiled]",
                       crossover_vs_bare_rho(None, "eq11", "unceiled",
                                             use_total=False), 302, 0, g,
                       integer=True))
    cells.append(_cell("crossover_unceiled[total_vs_walk_constant]",
                       _crossover_with_walk("unceiled"), 303, 0, g,
                       integer=True))
    cells.append(_cell("crossover_ceiled[total_vs_walk_constant]",
                       _crossover_with_walk("ceiled"), 281, 0, g, integer=True))

    g = "8d123b_ceiling_discrepancy"
    for n, tgv in [(233, -0.89), (283, -4.44), (310, 0.00), (409, -8.18),
                   (571, -4.58)]:
        m = semaev_optimal_m(n)
        a = semaev_stage1_log2(n, m, 3.0, "eq11", "ceiled")["log2_stage1"]
        b = semaev_stage1_log2(n, m, 3.0, "eq11", "unceiled")["log2_stage1"]
        cells.append(_cell(f"per_n_stage1_discrepancy_bits[n={n}]", a - b,
                           tgv, 5e-3, g))

    g = "8d123b_degree_bound_sensitivity_is_a_memory_quantity"
    for degree, tgs in [(5, {310: 18.246, 409: 19.356, 571: 20.590}),
                        (6, {310: 35.964, 409: 38.186, 571: 40.654})]:
        for n, tgv in tgs.items():
            m = semaev_optimal_m(n)
            cells.append(_cell(f"bits_added_if_bound_is_{degree}[n={n}]",
                               semaev_memory_degree_sensitivity(n, m, degree),
                               tgv, 1e-3, g))

    # -- group 3: CORR-20260913-53739b correction_1, THE CORRECTED TARGET
    g = "CORR_53739b_authoritative_eq11"
    for d_sat, tgv in zip((4, 5, 6, 7), (181.7, 185.5, 212.8, 240.3)):
        cells.append(_cell(f"stage1[571,12,48,eq11,d_sat={d_sat}]",
                           semaev_stage1_log2(571, 12, 3.0, "eq11", "ceiled",
                                              d_sat, 4)["log2_stage1"],
                           tgv, 5e-2, g))
    for d_sat, tgv, tgmk in zip((4, 5, 6), (175.1, 176.9, 192.8),
                                ((15, 39), (15, 39), (21, 28))):
        r = reoptimised_total(571, d_sat, "eq11")
        cells.append(_cell(f"reoptimised_total[571,eq11,d_sat={d_sat}]",
                           r["log2_total"], tgv, 5e-2, g))
        cells.append(_cell(f"reoptimised_argmin_m_k[571,eq11,d_sat={d_sat}]",
                           (r["m"], r["k"]), tgmk, 0, g, integer=True))
    for d_sat, tgv in zip((4, 5, 6, 7), (281, 295, 337, 393)):
        cells.append(_cell(f"crossover[eq11,d_sat={d_sat}]",
                           crossover_vs_bare_rho(d_sat, "eq11", "ceiled"),
                           tgv, 0, g, integer=True))

    # the UNCORRECTED figures, reproduced BY NAME so that reproducing them is
    # visible as a failure rather than mistakable for a pass
    g = "CORR_53739b_UNCORRECTED_m_only_reproducing_these_is_a_failure"
    for d_sat, tgv in zip((4, 5, 6, 7), (186.7, 187.2, 212.8, 240.3)):
        cells.append(_cell(f"stage1[571,12,48,m_only,d_sat={d_sat}]",
                           semaev_stage1_log2(571, 12, 3.0, "m_only", "ceiled",
                                              d_sat, 4)["log2_stage1"],
                           tgv, 5e-2, g))
    for d_sat, tgv in zip((4, 5, 6), (186.4, 186.5, 197.1)):
        cells.append(_cell(f"reoptimised_total[571,m_only,d_sat={d_sat}]",
                           reoptimised_total(571, d_sat, "m_only")["log2_total"],
                           tgv, 5e-2, g))
    for d_sat, tgv in zip((4, 5, 6, 7), (303, 307, 347, 400)):
        cells.append(_cell(f"crossover[m_only,d_sat={d_sat}]",
                           crossover_vs_bare_rho(d_sat, "m_only", "ceiled"),
                           tgv, 0, g, integer=True))

    # correction_1's controls
    g = "CORR_53739b_controls"
    for n in (283, 571):
        m = semaev_optimal_m(n, 3.0, 2.0, "eq11", "unceiled")
        a = semaev_stage1_log2(n, m, 3.0, "eq11", "unceiled")["log2_stage1"]
        b = semaev_stage1_log2(n, m, 3.0, "m_only", "unceiled")["log2_stage1"]
        cells.append(_cell(f"two_charges_agree_at_unceiled_k[n={n}]", a - b,
                           0.0, 1e-9, g))
    for n, tgv in ((163, -10.47), (1000, -36.25)):
        m = semaev_optimal_m(n, 3.0, 2.0, "eq11", "ceiled", 30, 4, 4)
        cells.append(_cell(f"log2_lambda_at_optimum[n={n}]",
                           exact_yield_control(n, m)["log2_lambda"], tgv,
                           5e-3, g))
    for omega_prime in (1.0, 2.0, 2.376, 3.0):
        m = semaev_optimal_m(571, 3.0, omega_prime, "m_only", "ceiled", 30, 6, 4)
        t = semaev_time_log2(571, m, 3.0, omega_prime, "m_only", "ceiled", 6, 4)
        t21 = semaev_time_log2(571, 21, 3.0, omega_prime, "m_only", "ceiled",
                               6, 4)
        cells.append(_cell(f"omega_prime_invariant_argmin[omega'={omega_prime}]",
                           (m, int(t["k"])), (18, 32), 0, g, integer=True))
        cells.append(_cell(f"m_eq_21_is_worse_by[omega'={omega_prime}]",
                           t21["log2_total"] - t["log2_total"], 6.3, 5e-2, g))
        cells.append(_cell(f"m_eq_21_total[omega'={omega_prime}]",
                           t21["log2_total"], 203.36, 5e-3, g))
        cells.append(_cell(f"argmin_total[omega'={omega_prime}]",
                           t["log2_total"], 197.08, 5e-3, g))

    # -- group 4: EV-SEMBIN-71e5cd O-6 and O-7, the baseline charge itself
    g = "EV_71e5cd_O6_O7_baseline"
    for n in (283, 310, 409, 571):
        d = vow_dominated_charge_8d123b(n)
        dom = d["log2_time"] + d["log2_memory_bits"]
        mn = vow_pareto_minimum(n, "time_memory_product")["metric_log2"]
        cells.append(_cell(f"O6_dominated_charge_overcharge_bits[n={n}]",
                           dom - mn, 29.0, 5e-2, g))
    for storage, tgv in (("dense", 520), ("semaev_sparse", 460)):
        cells.append(_cell(f"O7_crossover_vow_at_minimum[{storage}]",
                           _crossover_vs_pareto(storage, joint_m=False), tgv,
                           0, g, integer=True))
    for storage, tgv in (("dense", 518), ("semaev_sparse", 460)):
        cells.append(_cell(f"O7_crossover_both_at_own_minimum[{storage}]",
                           _crossover_vs_pareto(storage, joint_m=True), tgv,
                           0, g, integer=True))
    for storage, tgv in (("dense", -37.79), ("semaev_sparse", -17.48)):
        m = semaev_optimal_m(409)
        sem = (semaev_time_log2(409, m)["log2_total"]
               + semaev_memory_log2(409, m, 4, storage)["log2_total_bits"])
        cells.append(_cell(f"O7_margin_at_409_coherent[{storage}]",
                           vow_pareto_minimum(409, "time_memory_product")
                           ["metric_log2"] - sem, tgv, 5e-3, g))
    m = semaev_optimal_m(571)
    sem = (semaev_time_log2(571, m)["log2_total"]
           + semaev_memory_log2(571, m, 4, "semaev_sparse")["log2_total_bits"])
    cells.append(_cell("O7_margin_at_571_sparse_coherent",
                       vow_pareto_minimum(571, "time_memory_product")
                       ["metric_log2"] - sem, 40.49, 5e-3, g))
    return cells


def _crossover_with_walk(k_reading: str, n_lo: int = 100, n_hi: int = 900):
    """8d123b's own 303 / 281: re-optimised TOTAL against 0.886 * 2^{n/2}."""
    for n in range(n_lo, n_hi + 1):
        m = semaev_optimal_m(n, 3.0, 2.0, "eq11", k_reading)
        t = semaev_time_log2(n, m, 3.0, 2.0, "eq11", k_reading)
        if t["log2_total"] < vow_walk_work_log2(n):
            return n
    return None


def _crossover_vs_pareto(storage: str, joint_m: bool, degree: int = 4,
                         n_lo: int = 250, n_hi: int = 700):
    """O-7's two conventions.

    joint_m False: m at the stage-1 argmin, which is 8d123b's own choice, and
      the baseline moved to the minimum of its curve -- gives 520 / 460.
    joint_m True: m re-chosen to minimise the PRODUCT, i.e. each algorithm at
      the minimum of its own time-memory curve, which is what O-7's second
      sentence describes -- gives 518 / 460.
    """
    for n in range(n_lo, n_hi + 1):
        if joint_m:
            m = min(range(2, 31),
                    key=lambda mm: (semaev_time_log2(n, mm)["log2_total"]
                                    + semaev_memory_log2(n, mm, degree, storage)
                                    ["log2_total_bits"]))
        else:
            m = semaev_optimal_m(n)
        sem = (semaev_time_log2(n, m)["log2_total"]
               + semaev_memory_log2(n, m, degree, storage)["log2_total_bits"])
        if sem < vow_pareto_minimum(n, "time_memory_product")["metric_log2"]:
            return n
    return None
