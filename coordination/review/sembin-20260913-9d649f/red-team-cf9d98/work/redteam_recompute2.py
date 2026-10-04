#!/usr/bin/env python3
"""Second red-team pass for TASK-20260913-cf9d98.

Five things the first pass showed were needed, three of which cut AGAINST the
record and two of which cut FOR it:

  A  the fixed-memory-budget metric done properly -- the baseline is NOT charged
     a budget penalty, because at any budget above 3n bits vOW's total work is
     unchanged, and Semaev is allowed to re-choose m to fit the budget;
  B  m re-optimised UNDER EACH METRIC. The record fixes m at the argmin of
     stage-1 TIME and then evaluates every memory-charged metric there, which
     under-charges nothing on the baseline's side and over-charges Semaev;
  C  the ceiled-k reading under the product metric (the record reports the
     ceiling effect only under time-only);
  D  a unit-conversion sensitivity: a rho step is a group operation, a Semaev
     stage-1 unit is a field-operation-scale quantity, and the record applies no
     conversion. This is the record's own disclosed largest imprecision and it
     runs in the baseline's favour;
  E  the Pareto comparison each algorithm is entitled to: the MINIMUM of its own
     time-memory product over its own parallelism curve.
"""

from __future__ import annotations

import json
import math

from redteam_recompute import (semaev_time_log2, semaev_memory_log2,
                               semaev_optimal_m, vow_time_log2,
                               vow_memory_log2, log2_add, log2_factorial,
                               log2_macaulay_width)

FIPS_N = [163, 233, 283, 409, 571]
M_RANGE = range(2, 31)


# ---------------------------------------------------------------- A ----------
def budget_metric() -> dict:
    """Fixed memory budget B bits, charged honestly on both sides.

    baseline: total work 0.886*2^{n/2} for ANY B >= 3n bits. A larger store buys
      wall-clock (parallelism) but not total work, and at M = 1 cycle detection
      needs O(1) points, so the baseline is never budget-limited here.
    Semaev  : must pick m. HARD -- only m with memory(n,m) <= B are admissible.
              SOFT -- an inadmissible m runs in memory/B external passes,
              costing time * (memory/B).
    """
    out = {"hard": {}, "soft": {}}
    for b in (30, 40, 50, 60, 64, 70, 80, 90):
        hard, soft = {}, {}
        for storage in ("dense", "semaev_sparse"):
            def h(n: int):
                feas = [(semaev_time_log2(n, m), m) for m in M_RANGE
                        if semaev_memory_log2(n, m, storage) <= b]
                return min(feas) if feas else (math.inf, None)

            def s(n: int):
                return min(((semaev_time_log2(n, m)
                             + max(0.0, semaev_memory_log2(n, m, storage) - b), m)
                            for m in M_RANGE))

            x_h = next((n for n in range(250, 1501) if h(n)[0] < vow_time_log2(n)),
                       None)
            x_s = next((n for n in range(250, 1501) if s(n)[0] < vow_time_log2(n)),
                       None)
            c409h, m409h = h(409)
            c409s, m409s = s(409)
            c571h, _ = h(571)
            c571s, _ = s(571)
            hard[storage] = {
                "crossover": x_h,
                "feasible_at_409": m409h is not None,
                "m_at_409": m409h,
                "margin_409": (None if not math.isfinite(c409h)
                               else round(vow_time_log2(409) - c409h, 4)),
                "verdict_409": ("semaev" if c409h < vow_time_log2(409) else "vow"),
                "verdict_571": ("semaev" if c571h < vow_time_log2(571) else "vow")}
            soft[storage] = {
                "crossover": x_s, "m_at_409": m409s,
                "margin_409": round(vow_time_log2(409) - c409s, 4),
                "margin_571": round(vow_time_log2(571) - c571s, 4),
                "verdict_409": ("semaev" if c409s < vow_time_log2(409) else "vow"),
                "verdict_571": ("semaev" if c571s < vow_time_log2(571) else "vow")}
        out["hard"][f"B=2^{b}"] = hard
        out["soft"][f"B=2^{b}"] = soft

    flip = {}
    for storage in ("dense", "semaev_sparse"):
        lo, hi = 0.0, 250.0
        for _ in range(200):
            mid = (lo + hi) / 2.0
            c = min((semaev_time_log2(409, m)
                     + max(0.0, semaev_memory_log2(409, m, storage) - mid))
                    for m in M_RANGE)
            if c < vow_time_log2(409):
                hi = mid
            else:
                lo = mid
        flip[storage] = round(hi, 3)
    out["soft_budget_log2_bits_at_which_409_turns_semaev"] = flip
    out["budget_reference_points"] = {
        "2^40 bits": "128 GB", "2^50 bits": "128 TB",
        "2^60 bits": "131 PB", "2^70 bits": "134 EB",
        "2^80 bits": "137 ZB -- above any storage that exists"}
    return out


# ---------------------------------------------------------------- B ----------
def m_reoptimised() -> dict:
    """Does re-choosing m under the metric help Semaev, and by how much?"""
    rows = []
    for n in FIPS_N + [310]:
        m_time = semaev_optimal_m(n)
        for storage in ("dense", "semaev_sparse"):
            def prod(m):
                return semaev_time_log2(n, m) + semaev_memory_log2(n, m, storage)
            m_prod = min(M_RANGE, key=prod)
            rows.append({
                "n": n, "storage": storage,
                "m_time_argmin": m_time, "m_product_argmin": m_prod,
                "product_at_time_argmin": round(prod(m_time), 4),
                "product_at_product_argmin": round(prod(m_prod), 4),
                "bits_the_record_leaves_on_the_table":
                    round(prod(m_time) - prod(m_prod), 4),
                "margin_409_gain": None})
    # crossovers with m re-optimised for the product
    cross = {}
    for storage in ("dense", "semaev_sparse"):
        for label, store in (("store_2^30_as_record", 30.0),
                             ("coherent_store_2^1", 1.0)):
            x = None
            for n in range(250, 901):
                sc = min(semaev_time_log2(n, m) + semaev_memory_log2(n, m, storage)
                         for m in M_RANGE)
                bc = vow_time_log2(n) + vow_memory_log2(n, store)
                if sc < bc:
                    x = n
                    break
            m409 = min(M_RANGE,
                       key=lambda m: semaev_time_log2(409, m)
                       + semaev_memory_log2(409, m, storage))
            sc409 = (semaev_time_log2(409, m409)
                     + semaev_memory_log2(409, m409, storage))
            cross[f"{storage}/{label}"] = {
                "crossover_m_reoptimised": x,
                "margin_409": round(vow_time_log2(409)
                                    + vow_memory_log2(409, store) - sc409, 4),
                "m_409": m409}
    return {"per_n": rows, "crossovers": cross}


# ---------------------------------------------------------------- C ----------
def ceiled_reading() -> dict:
    """The ceiled k the paper defines, under the product metric."""
    def s_time_ceiled(n, m, omega=3.0, omega_prime=2.0):
        k = float(-(-n // m))
        s1 = log2_factorial(m) + k + (n - m * k) + 4.0 * omega * math.log2(n)
        return log2_add(s1, k * omega_prime)

    def argmin_ceiled(n):
        return min(M_RANGE, key=lambda m: s_time_ceiled(n, m))

    out = {}
    for storage in ("dense", "semaev_sparse"):
        for metric in ("time_only", "product"):
            xs = {}
            for reading, tf, af in (("unceiled", semaev_time_log2,
                                     semaev_optimal_m),
                                    ("ceiled", s_time_ceiled, argmin_ceiled)):
                x = None
                for n in range(250, 901):
                    m = af(n)
                    sc = tf(n, m)
                    bc = vow_time_log2(n)
                    if metric == "product":
                        sc += semaev_memory_log2(n, m, storage)
                        bc += vow_memory_log2(n, 30.0)
                    if sc < bc:
                        x = n
                        break
                xs[reading] = x
            out[f"{storage}/{metric}"] = xs
    return {"crossovers": out,
            "record_reports_ceiling_only_under_time_only": {"unceiled": 303,
                                                            "ceiled": 281}}


# ---------------------------------------------------------------- D ----------
def unit_conversion() -> dict:
    """A rho step is a group operation; a Semaev stage-1 unit is not.

    The record discloses this as its largest single imprecision and applies no
    factor. Charging the baseline 2^u field-operation-equivalents per group
    operation moves the crossover DOWN -- the direction that says the record is
    too kind to the baseline.
    """
    out = {}
    for u in (0.0, 3.32, 5.0, 6.64):        # 1, 10, 32, 100 field ops per group op
        row = {}
        for storage in ("dense", "semaev_sparse"):
            for metric in ("time_only", "product"):
                x = None
                for n in range(200, 901):
                    m = semaev_optimal_m(n)
                    sc = semaev_time_log2(n, m)
                    bc = vow_time_log2(n) + u
                    if metric == "product":
                        sc += semaev_memory_log2(n, m, storage)
                        bc += vow_memory_log2(n, 30.0)
                    if sc < bc:
                        x = n
                        break
                row[f"{storage}/{metric}"] = x
        out[f"group_op_costs_2^{u}_field_ops"] = row
    return out


# ---------------------------------------------------------------- E ----------
def pareto_own_curves() -> dict:
    """Charge each algorithm the MINIMUM of its own time-memory product.

    Semaev, M workers: time T0/M; memory max(relation store, M * working set),
      because the store is shared and the Groebner working set is per worker.
      product = T0 * max(WS, store/M) -> minimum T0 * WS at M >= store/WS.
    vOW, M processors and w stored points: time W*(1/M + 1/w),
      memory 3n*max(w, M) -> minimum ~2 * 3n * W at w ~ M.
    Both minima are attained on each algorithm's own curve, which is what a
    Pareto comparison of two tunable algorithms means.
    """
    rows = []
    for n in range(250, 901):
        rec = {}
        for storage in ("dense", "semaev_sparse"):
            best = None
            for m in M_RANGE:
                k = -(-n // m)
                store = k + math.log2(m * k + 2 * n)
                if storage == "dense":
                    ws = 2.0 * log2_macaulay_width((m - 2) * n + k * m, 4)
                else:
                    ws = (4.0 * math.log2(n * m) - math.log2(24.0)
                          + 3.0 * math.log2(n) - math.log2(m))
                p = semaev_time_log2(n, m) + max(ws, store)  # M large enough
                if best is None or p < best:
                    best = p
            rec[storage] = best
        vow_min = vow_time_log2(n) + math.log2(3.0 * n) + 1.0
        rows.append({"n": n, "vow_min_product": vow_min, **rec})
    out = {"crossover_pareto_min_product": {}, "at_fips": {}}
    for storage in ("dense", "semaev_sparse"):
        out["crossover_pareto_min_product"][storage] = next(
            (r["n"] for r in rows if r[storage] < r["vow_min_product"]), None)
    for n in (283, 310, 409, 571):
        r = next(x for x in rows if x["n"] == n)
        out["at_fips"][n] = {
            "vow_min_product": round(r["vow_min_product"], 4),
            "semaev_min_product_dense": round(r["dense"], 4),
            "semaev_min_product_sparse": round(r["semaev_sparse"], 4),
            "margin_dense": round(r["vow_min_product"] - r["dense"], 4),
            "margin_sparse": round(r["vow_min_product"] - r["semaev_sparse"], 4)}
    return out


# ---------------------------------------------------------------- F ----------
def attribution_decomposition() -> dict:
    """What the record's matched-null control should have reported."""
    steps = {}
    for storage in ("dense", "semaev_sparse"):
        x_time = next(n for n in range(250, 901)
                      if semaev_time_log2(n, semaev_optimal_m(n))
                      < vow_time_log2(n))
        x_sem_only = next(
            (n for n in range(250, 1201)
             if semaev_time_log2(n, semaev_optimal_m(n))
             + semaev_memory_log2(n, semaev_optimal_m(n), storage)
             < vow_time_log2(n) + math.log2(3.0 * n)), None)
        x_both = next(
            (n for n in range(250, 1201)
             if semaev_time_log2(n, semaev_optimal_m(n))
             + semaev_memory_log2(n, semaev_optimal_m(n), storage)
             < vow_time_log2(n) + vow_memory_log2(n, 30.0)), None)
        steps[storage] = {
            "step0_time_only": x_time,
            "step1_charge_semaev_memory_only_baseline_at_3n_bits": x_sem_only,
            "step2_also_charge_baseline_a_2^30_point_store": x_both,
            "shift_from_semaev_memory": x_sem_only - x_time,
            "shift_from_baseline_store": x_both - x_sem_only,
            "net_shift_the_record_reports": x_both - x_time,
            "record_claims_baseline_share": 0}
    return steps


def main() -> None:
    print(json.dumps({
        "A_fixed_memory_budget_metric": budget_metric(),
        "B_m_reoptimised_under_the_metric": m_reoptimised(),
        "C_ceiled_k_under_product": ceiled_reading(),
        "D_unit_conversion_sensitivity": unit_conversion(),
        "E_pareto_min_of_own_curves": pareto_own_curves(),
        "F_attribution_decomposition": attribution_decomposition(),
    }, indent=2))


if __name__ == "__main__":
    main()
