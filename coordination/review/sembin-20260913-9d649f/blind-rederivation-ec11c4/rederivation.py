#!/usr/bin/env python3
"""Blind re-derivation of the memory-charged crossover for the chained-S_3
index-calculus attack on E(F_{2^n}) against van Oorschot-Wiener parallel rho.

Joint J6-BLIND of REVIEW-SEMBIN-20260913-9d649f, handoff TASK-20260913-ec11c4.

WHAT THIS COMPUTES
  (1) the smallest integer n at which the attack is cheaper than the baseline
      under the cost measure (time * memory);
  (2) the signed margin in bits at n = 409, positive meaning attack cheaper.

WHERE THE PARAMETERS COME FROM
  The cost model is taken from the `blind_rederivation` block of
  coordination/review/sembin-20260913-9d649f/review-plan.yaml and from the
  frozen source inputs/SEMAEV-2015-310/paper_fulltext.md (Section 4.3 eq. 11,
  Section 4.5.2 eqs. 15-17, Table 3).  No producer implementation was read
  before this file was written and its figures recorded; see attestation.yaml.

ARITHMETIC
  Everything is exact.  There are no floats in the decision path.  Costs carry
  irrational factors 2^{n/m} and 2^{n/2}, so each cost is represented as a
  closed RATIONAL INTERVAL [lo, hi] of Fractions, built from integer k-th roots
  (`iroot`) at a declared relative precision of 2^-B.  Comparisons succeed only
  when the intervals are disjoint, so every reported inequality is rigorous
  rather than a floating-point accident.  log2 values are reported as
  Decimal-evaluated bounds on those same intervals, and a figure is printed only
  when its lower and upper bound round identically.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from fractions import Fraction
from typing import Iterable

getcontext().prec = 80

# Relative precision of the rational enclosure of 2^{p/q}.  Costs here reach
# ~2^300; 2^-256 relative width leaves ~2^-200 of slack, far tighter than the
# 0.01-bit resolution any reported figure needs.
PRECISION_BITS = 256

M_RANGE = range(2, 21)          # plan: integer m in [2, 20]
OMEGA = 3                       # plan: omega = 3, so the F4 factor is n^{4*omega}
F4_EXPONENT = 4 * OMEGA         # = 12
STAGE2_EXPONENT = 2             # plan: stage-2 linear-algebra exponent omega' = 2
MACAULAY_DEGREE = 4             # Assumption 1: d_F4 <= 4
BASELINE_LEAD = Fraction(886, 1000)   # 0.886 * 2^{n/2} group operations
BASELINE_DP_POINTS_LOG2 = 30          # 2^30 distinguished points
BASELINE_BITS_PER_POINT_FACTOR = 3    # 3n bits per stored point


# --------------------------------------------------------------------------
# exact integer roots and rational enclosures of 2^{p/q}
# --------------------------------------------------------------------------

def iroot(n: int, k: int) -> int:
    """floor(n ** (1/k)) for n >= 0, k >= 1, by integer Newton iteration."""
    if n < 0:
        raise ValueError("iroot of a negative integer")
    if k < 1:
        raise ValueError("iroot needs k >= 1")
    if n in (0, 1) or k == 1:
        return n
    x = 1 << -(-n.bit_length() // k)          # 2^ceil(bitlen/k) >= n^(1/k)
    while True:
        y = ((k - 1) * x + n // x ** (k - 1)) // k
        if y >= x:
            break
        x = y
    assert x ** k <= n < (x + 1) ** k
    return x


_POW2_CACHE: dict[tuple[int, int], tuple[Fraction, Fraction]] = {}


def pow2(p: int, q: int, bits: int = PRECISION_BITS) -> tuple[Fraction, Fraction]:
    """Rational enclosure (lo, hi) with lo <= 2**(p/q) <= hi.

    Exact when q divides p.  Otherwise 2^{r/q} = (2^{r + q*bits})^{1/q} / 2^bits
    gives a floor/ceil pair whose relative width is below 2^-bits.
    """
    if q <= 0:
        raise ValueError("pow2 needs q > 0")
    whole, rem = divmod(p, q)                  # Python floor-divides, so 0 <= rem < q
    scale = Fraction(2) ** whole
    if rem == 0:
        return scale, scale
    key = (rem, q, bits)
    cached = _POW2_CACHE.get(key)
    if cached is None:
        root = iroot(2 ** (rem + q * bits), q)
        denom = 1 << bits
        cached = (Fraction(root, denom), Fraction(root + 1, denom))
        _POW2_CACHE[key] = cached
    lo, hi = cached
    return lo * scale, hi * scale


@dataclass(frozen=True)
class Interval:
    """A closed interval of positive rationals."""

    lo: Fraction
    hi: Fraction

    def __post_init__(self) -> None:
        if self.lo <= 0 or self.hi < self.lo:
            raise ValueError(f"bad interval [{self.lo}, {self.hi}]")

    @staticmethod
    def exact(value) -> "Interval":
        f = Fraction(value)
        return Interval(f, f)

    @staticmethod
    def pow2(p: int, q: int) -> "Interval":
        lo, hi = pow2(p, q)
        return Interval(lo, hi)

    def __add__(self, other: "Interval") -> "Interval":
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __mul__(self, other: "Interval") -> "Interval":
        return Interval(self.lo * other.lo, self.hi * other.hi)

    def strictly_below(self, other: "Interval") -> bool:
        """True if self < other for certain; False if self >= other for certain."""
        if self.hi < other.lo:
            return True
        if self.lo >= other.hi:
            return False
        raise ArithmeticError(
            "enclosures overlap; raise PRECISION_BITS "
            f"(self=[{float(self.lo):.6e}, {float(self.hi):.6e}], "
            f"other=[{float(other.lo):.6e}, {float(other.hi):.6e}])"
        )

    def log2_bounds(self) -> tuple[Decimal, Decimal]:
        return _log2_fraction(self.lo), _log2_fraction(self.hi)


_LN2 = Decimal(2).ln()


def _log2_fraction(value: Fraction) -> Decimal:
    """log2 of a positive Fraction, via a bit-length split so Decimal only ever
    divides two numbers of comparable size."""
    num, den = value.numerator, value.denominator
    shift = num.bit_length() - den.bit_length()
    if shift >= 0:
        den <<= shift
    else:
        num <<= -shift
    return Decimal(shift) + (Decimal(num) / Decimal(den)).ln() / _LN2


def log2_str(iv: Interval, places: int = 4) -> str:
    lo, hi = iv.log2_bounds()
    q = Decimal(1).scaleb(-places)
    lo_r, hi_r = lo.quantize(q), hi.quantize(q)
    if lo_r != hi_r:
        raise ArithmeticError(f"log2 not resolved to {places} places: {lo} .. {hi}")
    return str(lo_r)


def log2_float(iv: Interval) -> float:
    lo, hi = iv.log2_bounds()
    return float((lo + hi) / 2)


# --------------------------------------------------------------------------
# the attack: time
# --------------------------------------------------------------------------

def stage1_time_closed(n: int, m: int) -> Interval:
    """Plan-literal stage 1:  m! * 2^{n/m} * n^{4*omega}.

    This is eq. (15) of the frozen paper after the yield of Section 4.3 has been
    folded in at k = n/m exactly: 1/P(n, m, m, k) ~ m! * 2^{n - mk} = m! when
    mk = n, and the 2^k relations contribute 2^{n/m}.  It is the formula the
    paper's own Table 3 column 4 tabulates.
    """
    return (
        Interval.exact(math.factorial(m))
        * Interval.pow2(n, m)
        * Interval.exact(n ** F4_EXPONENT)
    )


def stage1_time_exact_yield(n: int, m: int) -> Interval:
    """Eq. (15) read literally at integer k = ceil(n/m), dividing 2^k * n^{4w}
    by the eq. (11) yield rather than by its m! approximation.

    P = 1 - exp(-2^{mk-n}/m!).  Evaluated as an exact rational enclosure via the
    alternating series for 1 - e^{-x} so that no float enters; x = 2^{mk-n}/m!
    is a positive rational because mk >= n.
    """
    k = -(-n // m)
    x = Fraction(2) ** (m * k - n) / math.factorial(m)
    p_lo, p_hi = _one_minus_exp_neg_bounds(x)
    relations = Interval.pow2(k, 1)
    per_attempt = Interval.exact(n ** F4_EXPONENT)
    # dividing by an interval [p_lo, p_hi] inverts the endpoints
    inv_p = Interval(1 / p_hi, 1 / p_lo)
    return relations * per_attempt * inv_p


def _one_minus_exp_neg_bounds(x: Fraction, terms: int = 80) -> tuple[Fraction, Fraction]:
    """Rational bounds on 1 - exp(-x) for x > 0 by truncating the alternating
    series x - x^2/2! + x^3/3! - ...; consecutive truncations bracket the sum."""
    if x <= 0:
        raise ValueError("need x > 0")
    partials = []
    total = Fraction(0)
    power = Fraction(1)
    for i in range(1, terms + 1):
        power *= x
        term = power / math.factorial(i)
        total += term if i % 2 == 1 else -term
        partials.append(total)
        if i >= 3 and term < Fraction(1, 10) ** 60 * max(abs(total), Fraction(1)):
            break
    lo = min(partials[-1], partials[-2])
    hi = max(partials[-1], partials[-2])
    lo = max(lo, Fraction(0))
    hi = min(hi, Fraction(1))
    return lo, hi


def stage2_time(n: int, m: int) -> Interval:
    """Stage 2:  2^{omega' * n/m} with omega' = 2, i.e. 2^{2n/m}."""
    return Interval.pow2(STAGE2_EXPONENT * n, m)


def stage2_time_integer_k(n: int, m: int) -> Interval:
    k = -(-n // m)
    return Interval.pow2(STAGE2_EXPONENT * k, 1)


# --------------------------------------------------------------------------
# the attack: memory
# --------------------------------------------------------------------------

def relation_row_width_bits(n: int, m: int) -> int:
    """m*ceil(n/m) + 2n bits: m factor-base indices of ceil(n/m) bits each,
    plus the two n-bit scalars u, v of relation (7)."""
    return m * (-(-n // m)) + 2 * n


def relation_store_bits(n: int, m: int) -> int:
    """2^{ceil(n/m)} rows of relation_row_width_bits each."""
    return (1 << (-(-n // m))) * relation_row_width_bits(n, m)


def boolean_monomials_upto(nvars: int, degree: int = MACAULAY_DEGREE) -> int:
    """Number of squarefree monomials of total degree <= `degree` in `nvars`
    Boolean variables: sum_{i=0}^{degree} C(nvars, i).  The system of Section
    4.5 is Boolean (x^2 = x), so monomials are squarefree."""
    return sum(math.comb(nvars, i) for i in range(degree + 1))


def macaulay_variables_plan(n: int, m: int) -> int:
    """N as the review plan states it: N = m*ceil(n/m) + 2n."""
    return relation_row_width_bits(n, m)


def macaulay_variables_paper(n: int, m: int) -> int:
    """N as Section 4.5.1 of the frozen paper states it: the Boolean system for
    t = m has n(t-2) + kt = (m-2)n + m*ceil(n/m) variables."""
    return (m - 2) * n + m * (-(-n // m))


def attack_memory_bits(n: int, m: int, *, dense: bool, nvars_paper: bool) -> int:
    nvars = macaulay_variables_paper(n, m) if nvars_paper else macaulay_variables_plan(n, m)
    width = boolean_monomials_upto(nvars)
    working_set = width * width if dense else width
    return max(relation_store_bits(n, m), working_set)


def baseline_memory_bits(n: int) -> int:
    return (1 << BASELINE_DP_POINTS_LOG2) * BASELINE_BITS_PER_POINT_FACTOR * n


def baseline_time(n: int) -> Interval:
    return Interval.exact(BASELINE_LEAD) * Interval.pow2(n, 2)


def baseline_cost(n: int) -> Interval:
    return baseline_time(n) * Interval.exact(baseline_memory_bits(n))


# --------------------------------------------------------------------------
# model assembly
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Model:
    """One reading of the cost model.

    yield_mode   'closed'  -> stage1 = m! 2^{n/m} n^{4w}, stage2 = 2^{2n/m}
                              (plan-literal; the paper's Table 3 columns)
                 'exact'   -> stage1 = 2^k n^{4w} / P(eq. 11), stage2 = 2^{2k},
                              k = ceil(n/m)
    m_objective  'time'    -> m minimises attack time (plan-literal)
                 'cost'    -> m minimises attack time * memory
    storage      'sparse'  -> working set charged as the width
                 'dense'   -> working set charged as width^2
    nvars        'plan'    -> N = m ceil(n/m) + 2n
                 'paper'   -> N = (m-2)n + m ceil(n/m)
    """

    yield_mode: str = "closed"
    m_objective: str = "time"
    storage: str = "sparse"
    nvars: str = "plan"

    @property
    def label(self) -> str:
        return f"{self.yield_mode}/{self.m_objective}/{self.storage}/{self.nvars}"

    def attack_time(self, n: int, m: int) -> Interval:
        if self.yield_mode == "closed":
            return stage1_time_closed(n, m) + stage2_time(n, m)
        if self.yield_mode == "exact":
            return stage1_time_exact_yield(n, m) + stage2_time_integer_k(n, m)
        raise ValueError(self.yield_mode)

    def attack_memory(self, n: int, m: int) -> int:
        return attack_memory_bits(
            n, m, dense=(self.storage == "dense"), nvars_paper=(self.nvars == "paper")
        )

    def best_m(self, n: int) -> tuple[int, Interval, int, Interval]:
        """Return (m*, time, memory_bits, cost) at the optimal m."""
        best = None
        for m in M_RANGE:
            if m >= n:
                continue
            time = self.attack_time(n, m)
            mem = self.attack_memory(n, m)
            cost = time * Interval.exact(mem)
            objective = time if self.m_objective == "time" else cost
            if best is None or objective.strictly_below(best[0]):
                best = (objective, m, time, mem, cost)
        if best is None:
            raise ValueError(f"no admissible m at n={n}")
        _, m, time, mem, cost = best
        return m, time, mem, cost

    def margin_bits(self, n: int) -> tuple[float, dict]:
        m, time, mem, cost = self.best_m(n)
        base = baseline_cost(n)
        margin = log2_float(base) - log2_float(cost)
        detail = {
            "n": n,
            "m_star": m,
            "k": -(-n // m),
            "relation_row_width_bits": relation_row_width_bits(n, m),
            "macaulay_variables": (
                macaulay_variables_paper(n, m)
                if self.nvars == "paper"
                else macaulay_variables_plan(n, m)
            ),
            "macaulay_width_monomials_log2": log2_str(
                Interval.exact(
                    boolean_monomials_upto(
                        macaulay_variables_paper(n, m)
                        if self.nvars == "paper"
                        else macaulay_variables_plan(n, m)
                    )
                ),
                2,
            ),
            "relation_store_bits_log2": log2_str(
                Interval.exact(relation_store_bits(n, m)), 2
            ),
            "attack_memory_bits_log2": log2_str(Interval.exact(mem), 2),
            "attack_memory_binding_term": (
                "relation_store"
                if relation_store_bits(n, m) >= mem
                else "macaulay_working_set"
            ),
            "attack_time_log2": log2_str(time, 2),
            "attack_cost_log2": log2_str(cost, 2),
            "baseline_time_log2": log2_str(baseline_time(n), 2),
            "baseline_memory_bits_log2": log2_str(
                Interval.exact(baseline_memory_bits(n)), 2
            ),
            "baseline_cost_log2": log2_str(base, 2),
            "margin_bits": round(margin, 2),
        }
        return margin, detail

    def is_attack_cheaper(self, n: int) -> bool:
        _, _, _, cost = self.best_m(n)
        return cost.strictly_below(baseline_cost(n))

    def cheaper_region(self, lo: int = 3, hi: int = 1200) -> dict:
        """Exhaustive scan of [lo, hi] for the sign of the comparison.

        No monotonicity is assumed, and it does not hold: ceil(n/m) steps by one
        at each multiple of m, which doubles the relation store, so the margin
        saws upward rather than climbing.  Three different integers can all be
        called "the crossover", so all three are reported:

          smallest_cheaper   the literal smallest n.  Below n ~ 25 this is an
                             ARTEFACT of the baseline's fixed 2^30-point
                             distinguished-point store, which is charged even
                             when the whole group has 2^3 elements.  Reported,
                             not suppressed.
          last_not_cheaper   the largest n at which the attack is still dearer.
          final_crossover    last_not_cheaper + 1: the n from which the attack
                             is cheaper for every larger n in the scan.  This is
                             the figure I report as "the crossover".
        """
        cheaper = [n for n in range(lo, hi + 1) if self.is_attack_cheaper(n)]
        dearer = [n for n in range(lo, hi + 1) if n not in set(cheaper)]
        runs = []
        for n in cheaper:
            if runs and runs[-1][1] == n - 1:
                runs[-1][1] = n
            else:
                runs.append([n, n])
        return {
            "scan_lo": lo,
            "scan_hi": hi,
            "smallest_cheaper": cheaper[0] if cheaper else None,
            "last_not_cheaper": dearer[-1] if dearer else None,
            "final_crossover": (dearer[-1] + 1) if dearer else (cheaper[0] if cheaper else None),
            "contiguous_cheaper_runs": [tuple(r) for r in runs],
        }

    def crossover(self, lo: int = 3, hi: int = 1200) -> int | None:
        """The reported crossover: the n from which the attack is cheaper for
        every larger n in the scanned range."""
        return self.cheaper_region(lo, hi)["final_crossover"]


# --------------------------------------------------------------------------
# controls against permitted sources
# --------------------------------------------------------------------------

TABLE_3 = [
    # n, 2^{n/2}, m, stage1, stage2   -- inputs/SEMAEV-2015-310/tables.yaml
    (100, 1.12e15, 6, 7.49e31, 1.08e10),
    (150, 3.77e22, 7, 1.84e36, 7.96e12),
    (200, 1.26e30, 8, 5.54e39, 1.12e15),
    (250, 4.25e37, 9, 4.97e42, 5.29e16),
    (300, 1.42e45, 10, 2.07e45, 1.15e18),
    (310, 4.56e46, 10, 6.13e45, 4.61e18),
    (350, 4.78e52, 10, 4.21e47, 1.18e21),
    (400, 1.60e60, 11, 5.92e49, 7.81e21),
    (409, 3.63e61, 11, 1.36e50, 2.43e22),
    (450, 5.39e67, 11, 5.68e51, 4.26e24),
    (500, 1.80e75, 12, 4.08e53, 1.21e25),
    (571, 8.79e85, 12, 1.21e56, 4.44e28),
]

# tables.yaml derived_checks.stage2_memory.f4_working_set, which uses the
# paper's variable count N = (m-2)n + km.
WORKING_SET_CONTROL = [(310, 10, 41.2), (409, 11, 43.4), (571, 12, 45.9)]

# tables.yaml derived_checks.stage2_memory: "2^31 relations at n = 310, 2^38 at
# n = 409, 2^48 at n = 571".
RELATION_COUNT_CONTROL = [(310, 10, 31), (409, 11, 38), (571, 12, 48)]


def run_controls() -> list[dict]:
    """Reproduce every published cell I am permitted to see, so that a
    disagreement downstream cannot be blamed on my arithmetic."""
    results = []

    # Control 1: Table 3, all 36 numeric cells, from my own formulas.
    worst = 0.0
    m_agree = True
    for n, rho, m_paper, s1, s2 in TABLE_3:
        mine_rho = 2.0 ** log2_float(Interval.pow2(n, 2))
        mine_s1 = 2.0 ** log2_float(stage1_time_closed(n, m_paper))
        mine_s2 = 2.0 ** log2_float(stage2_time(n, m_paper))
        for published, mine in ((rho, mine_rho), (s1, mine_s1), (s2, mine_s2)):
            worst = max(worst, abs(mine - published) / published)
        m_mine, _, _, _ = Model(m_objective="time").best_m(n)
        if m_mine != m_paper:
            m_agree = False
    results.append(
        {
            "control": "table_3_all_36_cells",
            "source": "inputs/SEMAEV-2015-310/tables.yaml table_3",
            "worst_relative_error": worst,
            "passes": worst < 0.01,
            "optimal_m_matches_paper_every_row": m_agree,
            "note": "validates my stage-1, stage-2 and rho formulas and my argmin over m",
        }
    )

    # Control 2: the frozen record's own degree-<=4 monomial exponents, which
    # use the PAPER's variable count.  Validates my monomial counting.
    ws = []
    for n, m, expected in WORKING_SET_CONTROL:
        got = log2_float(
            Interval.exact(boolean_monomials_upto(macaulay_variables_paper(n, m)))
        )
        ws.append(
            {
                "n": n,
                "m": m,
                "nvars_paper": macaulay_variables_paper(n, m),
                "published_log2": expected,
                "mine_log2": round(got, 2),
                "agrees_to_1dp": abs(got - expected) < 0.05,
            }
        )
    results.append(
        {
            "control": "f4_working_set_monomial_count",
            "source": "inputs/SEMAEV-2015-310/tables.yaml derived_checks.stage2_memory.f4_working_set",
            "rows": ws,
            "passes": all(r["agrees_to_1dp"] for r in ws),
            "note": "validates boolean_monomials_upto and macaulay_variables_paper",
        }
    )

    # Control 3: the relation count 2^{ceil(n/m)}.
    rc = [
        {
            "n": n,
            "m": m,
            "published_log2": e,
            "mine_log2": -(-n // m),
            "agrees": -(-n // m) == e,
        }
        for n, m, e in RELATION_COUNT_CONTROL
    ]
    results.append(
        {
            "control": "relation_count",
            "source": "inputs/SEMAEV-2015-310/tables.yaml derived_checks.stage2_memory",
            "rows": rc,
            "passes": all(r["agrees"] for r in rc),
        }
    )

    # Control 4: eq. (11) against the P_theoretical column of Tables 1-2.
    # (n, t, k, published) read row-wise off tables.yaml; the paper TRUNCATES to
    # 4 decimals rather than rounding (0.0013889 prints as 0.0013, 0.28347 as
    # 0.2834, 0.39347 as 0.3934), so agreement is tested at one unit in the last
    # printed place rather than by exact equality of the rounded value.
    eq11 = []
    for n, t, k, expected in [
        (12, 6, 2, 0.0013),    # table_1 / table_2 n=12 m=t=6 k=2
        (13, 4, 4, 0.2834),    # table_1 n=13 t=m=4 k=4
        (15, 2, 3, 0.0009),    # table_2 n=15 m=5 t=2 k=3
        (17, 3, 6, 0.2834),    # table_1 n=17 t=m=3 k=6
        (19, 3, 7, 0.4865),    # table_2 n=19 m=3 t=3 k=7
        (21, 2, 7, 0.0038),    # table_2 n=21 m=3 t=2 k=7
        (40, 2, 20, 0.3934),   # table_2 n=40 m=2 t=2 k=20
    ]:
        x = Fraction(2) ** (t * k - n) / math.factorial(t)
        lo, hi = _one_minus_exp_neg_bounds(x)
        mine = float((lo + hi) / 2)
        eq11.append(
            {
                "n": n,
                "t": t,
                "k": k,
                "published_truncated_4dp": expected,
                "mine": float(f"{mine:.6f}"),
                "agrees_within_one_last_place": abs(mine - expected) <= 1.05e-4,
            }
        )
    results.append(
        {
            "control": "eq_11_success_probability",
            "source": "inputs/SEMAEV-2015-310 Tables 1-2, P_theoretical column",
            "rows": eq11,
            "passes": all(r["agrees_within_one_last_place"] for r in eq11),
            "note": (
                "validates my rational 1-exp(-x) evaluation, used by the "
                "exact-yield variant; the paper truncates rather than rounds"
            ),
        }
    )

    # Control 5: a null/sanity direction -- the time-only crossover, which the
    # frozen record independently states is n = 302 rather than the paper's 310.
    time_only = _time_only_crossover()
    results.append(
        {
            "control": "time_only_crossover",
            "source": "inputs/SEMAEV-2015-310/tables.yaml derived_checks.table_3_columns.crossover",
            "published": 302,
            "mine": time_only,
            "passes": time_only == 302,
            "note": (
                "stage-1 alone below 2^{n/2} with no 0.886 and no memory charge, "
                "exactly as the frozen record states it"
            ),
        }
    )
    return results


def _time_only_crossover(lo: int = 3, hi: int = 800) -> int | None:
    """First n where min_m stage1 < 2^{n/2}; the frozen record's own check."""
    for n in range(lo, hi + 1):
        best = None
        for m in M_RANGE:
            if m >= n:
                continue
            t = stage1_time_closed(n, m)
            if best is None or t.strictly_below(best):
                best = t
        if best is not None and best.strictly_below(Interval.pow2(n, 2)):
            return n
    return None


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

PRIMARY = Model(yield_mode="closed", m_objective="time", storage="sparse", nvars="plan")

SENSITIVITY = [
    Model(yield_mode="closed", m_objective="time", storage="sparse", nvars="paper"),
    Model(yield_mode="closed", m_objective="cost", storage="sparse", nvars="plan"),
    Model(yield_mode="closed", m_objective="time", storage="dense", nvars="plan"),
    Model(yield_mode="closed", m_objective="time", storage="dense", nvars="paper"),
    Model(yield_mode="exact", m_objective="time", storage="sparse", nvars="plan"),
    Model(yield_mode="exact", m_objective="time", storage="dense", nvars="plan"),
    Model(yield_mode="closed", m_objective="cost", storage="dense", nvars="plan"),
]


def main() -> int:
    controls = run_controls()
    print("CONTROLS (against permitted sources only)")
    for c in controls:
        print(f"  {c['control']:38s} passes={c['passes']}")
        if c["control"] == "table_3_all_36_cells":
            print(f"    worst relative error {c['worst_relative_error']:.2%}, "
                  f"argmin m matches paper: {c['optimal_m_matches_paper_every_row']}")
    print()

    margin_409, detail_409 = PRIMARY.margin_bits(409)
    region = PRIMARY.cheaper_region()
    crossover = region["final_crossover"]

    print(f"PRIMARY MODEL  {PRIMARY.label}")
    print(f"  crossover n (final)         = {crossover}")
    print(f"  last n NOT cheaper          = {region['last_not_cheaper']}")
    print(f"  literal smallest n cheaper  = {region['smallest_cheaper']}"
          "   <- small-n artefact of the fixed 2^30 baseline store")
    print(f"  contiguous cheaper runs     = {region['contiguous_cheaper_runs']}")
    print(f"  margin at n = 409           = {margin_409:+.2f} bits")
    for key in (
        "m_star",
        "k",
        "relation_row_width_bits",
        "macaulay_variables",
        "macaulay_width_monomials_log2",
        "relation_store_bits_log2",
        "attack_memory_bits_log2",
        "attack_memory_binding_term",
        "attack_time_log2",
        "attack_cost_log2",
        "baseline_time_log2",
        "baseline_memory_bits_log2",
        "baseline_cost_log2",
    ):
        print(f"    {key:34s} {detail_409[key]}")
    print()

    print("SENSITIVITY")
    sens = []
    for model in SENSITIVITY:
        mg, det = model.margin_bits(409)
        reg = model.cheaper_region()
        sens.append({"model": model.label,
                     "crossover_n": reg["final_crossover"],
                     "last_n_not_cheaper": reg["last_not_cheaper"],
                     "margin_bits_at_409": round(mg, 2),
                     "m_star_at_409": det["m_star"],
                     "attack_memory_bits_log2_at_409": det["attack_memory_bits_log2"],
                     "attack_memory_binding_term_at_409": det["attack_memory_binding_term"]})
        print(f"  {model.label:34s} crossover={reg['final_crossover']}  "
              f"margin(409)={mg:+.2f}  m*={det['m_star']}  "
              f"mem={det['attack_memory_binding_term']}")
    print()

    margin_curve = {
        str(n): round(PRIMARY.margin_bits(n)[0], 3)
        for n in (250, 290, 300, 305, 306, 310, 320, 340, 350, 360, 370,
                  374, 375, 376, 400, 409, 450, 571)
    }
    print("PRIMARY margin(n) in bits")
    for n, v in margin_curve.items():
        print(f"  n={n:>4s}  {v:+.3f}")

    out = {
        "schema": "crypto.autoresearch.blind_rederivation_figures.v1",
        "task_id": "TASK-20260913-ec11c4",
        "review_round": "REVIEW-SEMBIN-20260913-9d649f",
        "joint": "J6-BLIND",
        "produced_at": datetime.now(timezone.utc).isoformat(),
        "written_before_reading_blind_from": True,
        "precision_bits": PRECISION_BITS,
        "arithmetic": (
            "exact rational interval arithmetic over integer k-th roots; "
            "no float in any comparison"
        ),
        "primary_model": PRIMARY.label,
        "figures": {
            "crossover_n": crossover,
            "margin_bits_at_n_409": round(margin_409, 2),
        },
        "crossover_region_detail": region,
        "crossover_definition_note": (
            "The margin is NOT monotone in n: ceil(n/m) steps at every multiple "
            "of m and doubles the relation store, so the comparison saws. "
            "`crossover_n` is the n from which the attack is cheaper for every "
            "larger n scanned. `smallest_cheaper` in crossover_region_detail is "
            "the literal smallest n and is an artefact: the baseline is charged "
            "a fixed 2^30-point distinguished-point store at every n, which at "
            "n < 25 exceeds the whole group, so the baseline looks dear."
        ),
        "n_409_detail": detail_409,
        "primary_margin_curve_bits": margin_curve,
        "sensitivity": sens,
        "controls": controls,
    }
    path = "figures-before-reading.json"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=False)
        fh.write("\n")
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
