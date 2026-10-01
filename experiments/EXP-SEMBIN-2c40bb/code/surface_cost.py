#!/usr/bin/env python3
"""EXP-SEMBIN-2c40bb -- the memory-charged comparison as a two-parameter SURFACE.

Closed-form log2-domain arithmetic only. No curve is instantiated, no relation is
computed, no Groebner basis is run, no degree is measured: degree bounds 4/5/6 are
swept as GIVEN parameters (IMP-SEMBIN-ENGINE).

Semaev side (frozen paper inputs/SEMAEV-2015-310/, time model as COST-SEMBIN-8d123b):
  stage 1   m! * 2^k * 2^(n - m k) * n^(4 omega)      k per k_reading
  stage 2   2^(k omega'),  omega' = 2
  memory    relation store 2^ceil(n/m) rows of (m k + 2n) bits, plus a working set
            under FOUR storage readings (two from the parent record, two from the
            validator's J1 re-derivation), summed in the log2 domain as the parent did.
  parallel  M = 2^p workers: time / M, memory log2add(store, p + working set).
  units     Semaev's counts are converted field -> group operations at kappa
            (EXP-ICEX-c32447 unit discipline): time - log2(kappa).

Baseline (van Oorschot-Wiener parallel collision search; HEUR-VOW-CURVE, UNVALIDATED,
primary paper NOT opened by any agent in this program; the tradeoff restatement is the
red team's, coordination/review/sembin-20260913-9d649f/red-team-cf9d98/report.md J2(b)):
  W = 0.886 * 2^(n/2) / sqrt(h) [/ sqrt(n) Frobenius discount for Koblitz labels]
  record_point_M1_w30       T = W / M,                Mem = 3n * w      (w = 2^store_log2)
  own_curve_product_minimum T = W (1/M + 1/w), w = M, Mem = 3n * M      (min of T*Mem)
  sect113r2_calibrated_ratio  w = M * 2^13.3,  T = W (1/M + 1/w),  Mem = 3n * w
Under a fixed budget B the baseline shrinks w and M to fit (any B >= 3n bits is feasible).
"""

from __future__ import annotations

import math

LOG2_10 = math.log2(10.0)
VOW_CONSTANT_LOG2 = math.log2(0.886)
SECT113R2_RATIO_LOG2 = 13.3
INF = float("inf")

N_LO, N_HI = 3, 700
M_HI = 30
FIPS_N = [163, 233, 283, 409, 571]
PARENT_WINDOW = (250, 650)

METRIC_FAMILIES = ["time_only", "time_memory_product", "memory_weighted_time_alpha",
                   "fixed_budget_hard", "fixed_budget_soft"]
STORE_GRID = [0, 10, 20, 30, 40, 48, 60]
PROC_GRID = [0, 20, 40]
MODES = ["record_point_M1_w30", "own_curve_product_minimum", "sect113r2_calibrated_ratio"]
KAPPA_GRID = [1, 10, 100]
COFACTOR_GRID = [1, 2, 4]
BUDGET_GRID = [30, 40, 50, 60, 64, 65, 70, 80, 89, 90]
ALPHA_GRID = [0.0, 0.25, 0.5, 0.75, 0.811, 1.0]
STORAGES = ["dense_row_echelon", "semaev_sparse", "rows_times_cols_dense",
            "nonzeros_with_index_sparse"]
K_READINGS = ["unceiled_n_over_m_as_in_table3", "ceil_n_over_m"]
M_SELECTIONS = ["stage1_argmin", "metric_reoptimised"]
OMEGA_GRID = [2.376, 2.807, 3.0]
DEGREE_GRID = [4, 5, 6]

TABLE3 = [
    (100, 6, 1.12e15, 7.49e31, 1.08e10), (150, 7, 3.77e22, 1.84e36, 7.96e12),
    (200, 8, 1.26e30, 5.54e39, 1.12e15), (250, 9, 4.25e37, 4.97e42, 5.29e16),
    (300, 10, 1.42e45, 2.07e45, 1.15e18), (310, 10, 4.56e46, 6.13e45, 4.61e18),
    (350, 10, 4.78e52, 4.21e47, 1.18e21), (400, 11, 1.60e60, 5.92e49, 7.81e21),
    (409, 11, 3.63e61, 1.36e50, 2.43e22), (450, 11, 5.39e67, 5.68e51, 4.26e24),
    (500, 12, 1.80e75, 4.08e53, 1.21e25), (571, 12, 8.79e85, 1.21e56, 4.44e28),
]


# --------------------------------------------------------------------------- helpers

def log2_add(a: float, b: float) -> float:
    if a == -INF:
        return b
    if b == -INF:
        return a
    hi, lo = max(a, b), min(a, b)
    return hi if hi - lo > 60 else hi + math.log2(1.0 + 2.0 ** (lo - hi))


def log2_factorial(m: int) -> float:
    return math.lgamma(m + 1.0) / math.log(2.0)


def metric_instances() -> list:
    out = [("time_only", None), ("time_memory_product", None)]
    out += [("memory_weighted_time_alpha", a) for a in ALPHA_GRID]
    out += [("fixed_budget_hard", b) for b in BUDGET_GRID]
    out += [("fixed_budget_soft", b) for b in BUDGET_GRID]
    return out


def metric_label(inst) -> str:
    fam, par = inst
    if par is None:
        return fam
    if fam == "memory_weighted_time_alpha":
        return f"{fam}[alpha={par}]"
    return f"{fam}[budget_log2={par}]"


def validate_inputs(n=None, m=None, t=None, store_log2=None, budget_log2=None,
                    kappa=None) -> None:
    """C9: reject invalid parameters with an error rather than a number."""
    if n is not None and (not isinstance(n, int) or isinstance(n, bool)):
        raise ValueError(f"n must be an integer (got {n!r})")
    if n is not None and n < 3:
        raise ValueError(f"n must be >= 3 (got {n})")
    if m is not None and m < 2:
        raise ValueError(f"m must be >= 2 (got {m})")
    if m is not None and n is not None and m > n:
        raise ValueError(f"m must be <= n (got m={m}, n={n})")
    if t is not None and m is not None and t > m:
        raise ValueError(f"t must be <= m (got t={t}, m={m})")
    if store_log2 is not None and store_log2 < 0:
        raise ValueError(f"store_log2 must be >= 0 (got {store_log2})")
    if budget_log2 is not None and n is not None and budget_log2 < math.log2(3 * n):
        raise ValueError(f"budget 2^{budget_log2} bits is below the 3n = {3 * n} bits "
                         f"the baseline needs")
    if kappa is not None and kappa <= 0:
        raise ValueError(f"kappa must be > 0 (got {kappa})")


# --------------------------------------------------------------------------- Semaev

def k_value(n: int, m: int, k_reading: str) -> float:
    if k_reading == "unceiled_n_over_m_as_in_table3":
        return n / m
    if k_reading == "ceil_n_over_m":
        return float(-(-n // m))
    raise ValueError(k_reading)


def semaev_time_log2(n: int, m: int, k_reading: str, omega: float = 3.0,
                     omega_prime: float = 2.0, free_yield: bool = False) -> dict:
    k = k_value(n, m, k_reading)
    stage1 = k + 4.0 * omega * math.log2(n)
    if not free_yield:                      # C4 deletes exactly log2(m!) + (n - m k)
        stage1 += log2_factorial(m) + (n - m * k)
    stage2 = k * omega_prime
    return {"stage1": stage1, "stage2": stage2, "total": log2_add(stage1, stage2), "k": k}


def macaulay_nvars(n: int, m: int, k_int: int) -> int:
    return (m - 2) * n + k_int * m


def log2_macaulay_width(nvars: int, degree: int) -> float:
    return math.log2(sum(math.comb(nvars, d) for d in range(degree + 1)))


def semaev_memory_log2(n: int, m: int, storage: str, degree: int = 4) -> dict:
    """Memory in log2 BITS. k is ALWAYS ceiled here (the relation store pays it)."""
    k_int = -(-n // m)
    row_bits = m * k_int + 2 * n
    rel_store = k_int + math.log2(row_bits)
    nvars = macaulay_nvars(n, m, k_int)
    width_log2 = log2_macaulay_width(nvars, degree)
    if storage == "dense_row_echelon":
        ws = 2.0 * width_log2
    elif storage == "semaev_sparse":
        ws = (4.0 * math.log2(n * m) - math.log2(24.0)) + (3.0 * math.log2(n) - math.log2(m))
    elif storage == "rows_times_cols_dense":
        rows_log2 = math.log2(n * (m - 1)) + math.log2(nvars + 1)
        ws = rows_log2 + width_log2
    elif storage == "nonzeros_with_index_sparse":
        rows_log2 = math.log2(n * (m - 1)) + math.log2(nvars + 1)
        v = 2 * n + k_int
        nz_row_log2 = math.log2(sum(math.comb(v, d) for d in range(4)))
        ws = rows_log2 + nz_row_log2 + math.log2(width_log2)
    else:
        raise ValueError(storage)
    return {"relation_store_log2_bits": rel_store, "working_set_log2_bits": ws,
            "macaulay_width_log2": width_log2, "nvars": nvars, "k_int": k_int,
            "total_log2_bits": log2_add(rel_store, ws)}


class Tables:
    """Per-(n, m) precomputation for one (omega, degree)."""

    def __init__(self, omega: float = 3.0, degree: int = 4, omega_prime: float = 2.0):
        self.omega, self.degree = omega, degree
        self.ns = list(range(N_LO, N_HI + 1))
        self.time = {kr: {} for kr in K_READINGS}       # [kr][n] -> list over m of dict
        self.free = {kr: {} for kr in K_READINGS}
        self.argmin_m = {kr: {} for kr in K_READINGS}
        self.argmin_free = {kr: {} for kr in K_READINGS}
        self.mem = {s: {} for s in STORAGES}            # [s][n] -> {m: (rel, ws)}
        for n in self.ns:
            ms = list(range(2, min(M_HI, n) + 1))
            for kr in K_READINGS:
                tt = {m: semaev_time_log2(n, m, kr, omega, omega_prime) for m in ms}
                ff = {m: semaev_time_log2(n, m, kr, omega, omega_prime, True) for m in ms}
                self.time[kr][n] = tt
                self.free[kr][n] = ff
                self.argmin_m[kr][n] = min(ms, key=lambda m: tt[m]["stage1"])
                self.argmin_free[kr][n] = min(ms, key=lambda m: ff[m]["stage1"])
            for s in STORAGES:
                self.mem[s][n] = {}
            for m in ms:
                k_int = -(-n // m)
                nvars = macaulay_nvars(n, m, k_int)
                width = log2_macaulay_width(nvars, degree)
                rel = k_int + math.log2(m * k_int + 2 * n)
                rows = math.log2(n * (m - 1)) + math.log2(nvars + 1)
                self.mem["dense_row_echelon"][n][m] = (rel, 2.0 * width)
                self.mem["semaev_sparse"][n][m] = (
                    rel, 4.0 * math.log2(n * m) - math.log2(24.0)
                    + 3.0 * math.log2(n) - math.log2(m))
                self.mem["rows_times_cols_dense"][n][m] = (rel, rows + width)
                v = 2 * n + k_int
                nz = math.log2(sum(math.comb(v, d) for d in range(4)))
                self.mem["nonzeros_with_index_sparse"][n][m] = (
                    rel, rows + nz + math.log2(width))

    def semaev_point(self, n, m, storage, k_reading, kappa=1, p=0, free_yield=False):
        t = (self.free if free_yield else self.time)[k_reading][n][m]
        rel, ws = self.mem[storage][n][m]
        return (t["total"] - math.log2(kappa) - p, log2_add(rel, ws + p))


# --------------------------------------------------------------------------- metrics

def metric_cost(T: float, Mem: float, inst) -> float:
    fam, par = inst
    if fam == "time_only":
        return T
    if fam == "time_memory_product":
        return T + Mem                              # -inf memory -> -inf (DEGENERATE)
    if fam == "memory_weighted_time_alpha":
        if par == 0.0:
            return T
        return T + par * Mem
    if fam == "fixed_budget_hard":
        return T if Mem <= par else INF
    if fam == "fixed_budget_soft":
        return T + max(0.0, Mem - par)
    raise ValueError(fam)


# --------------------------------------------------------------------------- baseline

def vow_work_log2(n: int, cofactor_h: int = 1, frobenius_discount: bool = False) -> float:
    W = VOW_CONSTANT_LOG2 + n / 2.0 - 0.5 * math.log2(cofactor_h)
    if frobenius_discount:
        W -= 0.5 * math.log2(n)                    # sqrt(2n)/sqrt(2): KN-TECH-018 reading
    return W


def vow_point(n: int, mode: str, store_log2: float, p: float, cofactor_h: int = 1,
              frobenius_discount: bool = False, budget_log2=None) -> tuple:
    """(T, Mem) in log2 (group operations, bits). Under a budget, w and M shrink to fit."""
    W = vow_work_log2(n, cofactor_h, frobenius_discount)
    unit = math.log2(3.0 * n)
    if budget_log2 is not None:
        room = budget_log2 - unit                 # log2 of how many 3n-bit records fit
        if room < 0:
            raise ValueError("budget below 3n bits")
    else:
        room = INF
    if mode == "record_point_M1_w30":
        p_eff = min(p, room)
        w_eff = min(store_log2, room)
        return (W - p_eff, w_eff + unit)
    if mode == "own_curve_product_minimum":
        p_eff = min(p, room)                      # w = M
        return (W - p_eff + 1.0, p_eff + unit)
    if mode == "sect113r2_calibrated_ratio":
        if room == INF:
            p_eff, w_eff = p, p + SECT113R2_RATIO_LOG2
        else:
            p_eff = max(0.0, min(p, room - SECT113R2_RATIO_LOG2))
            w_eff = min(p_eff + SECT113R2_RATIO_LOG2, room)
        T = W + math.log2(2.0 ** (-p_eff) + 2.0 ** (-w_eff))
        return (T, w_eff + unit)
    if mode == "zero_memory_comparator":
        return (W - p, -INF)
    raise ValueError(mode)


# --------------------------------------------------------------------------- curves

def semaev_curve(tab: Tables, inst, storage, k_reading, p, m_selection, kappa=1,
                 free_yield=False):
    """Per n: (cost, m, T, Mem). kappa enters as a uniform shift and never moves m."""
    out = {}
    for n in tab.ns:
        if m_selection == "stage1_argmin":
            m = (tab.argmin_free if free_yield else tab.argmin_m)[k_reading][n]
            T, Mem = tab.semaev_point(n, m, storage, k_reading, kappa, p, free_yield)
            out[n] = (metric_cost(T, Mem, inst), m, T, Mem)
        else:
            best = None
            for m in tab.time[k_reading][n]:
                T, Mem = tab.semaev_point(n, m, storage, k_reading, kappa, p, free_yield)
                c = metric_cost(T, Mem, inst)
                if best is None or c < best[0]:
                    best = (c, m, T, Mem)
            out[n] = best
    return out


def baseline_curve(inst, mode, store_log2, p, cofactor_h=1, frobenius_discount=False):
    fam, par = inst
    budget = par if fam in ("fixed_budget_hard", "fixed_budget_soft") else None
    out = {}
    for n in range(N_LO, N_HI + 1):
        T, Mem = vow_point(n, mode, store_log2, p, cofactor_h, frobenius_discount, budget)
        out[n] = (metric_cost(T, Mem, inst), T, Mem)
    return out


def compare_curves(sem, base, n_lo=N_LO, n_hi=N_HI) -> dict:
    """Cheaper set as intervals; first crossing; persistent crossover; parent window."""
    wins, margins = [], {}
    degenerate = False
    for n in range(n_lo, n_hi + 1):
        sc, m, _T, _M = sem[n]
        bc = base[n][0]
        if bc == -INF:
            degenerate = True
        if sc == INF and bc == INF:
            margin = None
            w = False
        elif sc == INF:
            margin = -INF
            w = False
        elif bc == INF:
            margin = INF
            w = True
        else:
            margin = bc - sc
            w = margin > 0
        margins[n] = margin
        wins.append(w)
    intervals, start = [], None
    for i, w in enumerate(wins):
        n = n_lo + i
        if w and start is None:
            start = n
        if not w and start is not None:
            intervals.append([start, n - 1])
            start = None
    if start is not None:
        intervals.append([start, n_hi])
    first = intervals[0][0] if intervals else None
    persistent = intervals[-1][0] if intervals and intervals[-1][1] == n_hi else None
    parent = None
    for n in range(PARENT_WINDOW[0], PARENT_WINDOW[1] + 1):
        if wins[n - n_lo]:
            parent = n
            break

    def fmt(x):
        if x is None:
            return None
        if x == INF:
            return "semaev_only_feasible"
        if x == -INF:
            return "semaev_infeasible"
        return round(x, 4)

    return {"first_crossing_n": first, "persistent_crossover_n": persistent,
            "crossover_n_parent_window_250_650": parent,
            "monotone_after_first_crossing": (first is not None and first == persistent),
            "semaev_cheaper_intervals": intervals,
            "margin_409_bits": fmt(margins[409]), "margin_571_bits": fmt(margins[571]),
            "m_at_409": sem[409][1], "m_at_571": sem[571][1],
            "degenerate": degenerate}


# --------------------------------------------------------------------------- Table 3 (C2)

def table3_control(tab: Tables) -> dict:
    """Reproduce all 36 Table 3 cells under the un-ceiled k with the parent's
    truncation convention: the printed 3-significant-figure mantissa is compared to the
    recomputed value TRUNCATED (floored) to 2 decimals of mantissa, exponent exact."""
    kr = "unceiled_n_over_m_as_in_table3"
    cells, exact, within = [], 0, 0
    for (n, m, rho, s1, s2) in TABLE3:
        pred = {"rho": n / 2.0,
                "stage1": log2_factorial(m) + n / m + 12.0 * math.log2(n),
                "stage2": 2.0 * n / m}
        printed = {"rho": rho, "stage1": s1, "stage2": s2}
        for col in ("rho", "stage1", "stage2"):
            p_exp = math.floor(math.log10(printed[col]))
            p_mant = round(printed[col] / 10.0 ** p_exp, 2)
            log10v = pred[col] / LOG2_10
            e = math.floor(log10v)
            mant = math.floor(10.0 ** (log10v - e) * 100.0) / 100.0
            ok = (e == p_exp and abs(mant - p_mant) < 5e-3)
            rel = abs(2.0 ** pred[col] / printed[col] - 1.0)
            exact += ok
            within += rel < 0.007
            cells.append({"n": n, "m": m, "column": col, "printed": printed[col],
                          "recomputed_trunc3sf": f"{mant:.2f}e{e}",
                          "relative_residual": rel, "agrees_truncated": ok})
    argmin = {n: tab.argmin_m[kr][n] for (n, *_r) in TABLE3}
    printed_m = {n: m for (n, m, *_r) in TABLE3}
    paper_n0 = None
    for n in range(250, 651):
        m = tab.argmin_m[kr][n]
        if tab.time[kr][n][m]["stage1"] < n / 2.0:
            paper_n0 = n
            break
    return {"cells": cells, "cells_agreeing_truncated_3sf": f"{exact}/{len(cells)}",
            "cells_within_0p7pct": f"{within}/{len(cells)}",
            "truncation_convention": ("recomputed mantissa floored to 2 decimals and "
                                      "compared to the printed 3-significant-figure value; "
                                      "exponent must match exactly (the parent's convention)"),
            "argmin_m_recomputed": argmin, "argmin_m_printed": printed_m,
            "argmin_agrees": argmin == printed_m,
            "argmin_at_310_409_571": {n: argmin[n] for n in (310, 409, 571)},
            "crossover_papers_own_convention_stage1_vs_bare_2_pow_n_half": paper_n0,
            "expected": 302,
            "passed": (exact == len(cells) and argmin == printed_m and paper_n0 == 302)}


# --------------------------------------------------------------------------- eq. (4) (C5)

def eq4_typo_detector(tab: Tables) -> dict:
    rows = []
    for (n, m) in [(310, 10), (409, 11), (571, 12)]:
        k = -(-n // m)
        nvars_chain = macaulay_nvars(n, m, k)
        w_chain = log2_macaulay_width(nvars_chain, 4)
        nvars_eq4 = m * n
        degree_eq4 = 2 ** (m - 1)
        w_eq4_lower = math.log2(math.comb(nvars_eq4, min(degree_eq4, nvars_eq4)))
        rows.append({"n": n, "m": m, "chain_width_log2_D4": round(w_chain, 3),
                     "eq4_degree": degree_eq4,
                     "eq4_width_log2_lower_bound": round(w_eq4_lower, 3),
                     "chain_cheaper": w_chain < w_eq4_lower,
                     "margin_bits": round(w_eq4_lower - w_chain, 3)})
    return {"passed": all(r["chain_cheaper"] for r in rows), "rows": rows,
            "status": ("TYPO DETECTOR ONLY. Passes by thousands of bits; detects a "
                       "transposition between D = 4 and 2^(m-1). NOT a validity check on "
                       "the cost model and NOT counted as one.")}
