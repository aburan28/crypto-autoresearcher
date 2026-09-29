#!/usr/bin/env python3
"""Validator's own full-axis cost model (written AFTER the blind step in own_rederivation.py and
AFTER reading surface_cost.py; it re-implements the column definitions in my own structure and
imports nothing from the producer's code). Used for M1(2), M2, M3, M4 and the proves-too-much
objects. Where a convention had to be taken from the producer (Boolean monomial width count,
the two extra storage readings, the sect113r2 mode, the budget shrink rule) it is named here.
"""
import math
from math import comb, lgamma, log2

INF = float("inf")
LOG2_W = log2(0.886)
N_LO, N_HI = 3, 700
M_HI = 30
STORAGES = ["dense_row_echelon", "semaev_sparse", "rows_times_cols_dense", "nonzeros_with_index_sparse"]


def log2add(a, b):
    if a == -INF:
        return b
    if b == -INF:
        return a
    hi, lo = max(a, b), min(a, b)
    return hi + log2(1.0 + 2.0 ** (lo - hi))


def lf(m):
    return lgamma(m + 1) / math.log(2)


def kval(n, m, ceiled):
    return float(math.ceil(n / m)) if ceiled else n / m


def sem_time(n, m, ceiled=False, omega=3.0, omega_p=2.0, free_yield=False):
    k = kval(n, m, ceiled)
    s1 = k + 4 * omega * log2(n)
    if not free_yield:
        s1 += lf(m) + (n - m * k)
    s2 = omega_p * k
    return log2add(s1, s2), s1


def boolean_width_log2(nvars, degree=4):
    return log2(sum(comb(nvars, d) for d in range(degree + 1)))


def sem_mem_parts(n, m, storage, degree=4):
    """(relation_store_log2_bits, working_set_log2_bits). Memory always pays ceil(n/m)."""
    k = math.ceil(n / m)
    store = k + log2(m * k + 2 * n)
    nvars = (m - 2) * n + k * m
    width = boolean_width_log2(nvars, degree)
    if storage == "dense_row_echelon":
        ws = 2 * width
    elif storage == "semaev_sparse":
        ws = log2(n ** 7 * m ** 3) - log2(24)          # (nm)^4/24 columns x n^3/m nonzeros per row
    elif storage == "rows_times_cols_dense":
        rows = log2(n * (m - 1)) + log2(nvars + 1)     # producer's reading: (m-1)n equations x (nvars+1) shifts
        ws = rows + width
    elif storage == "nonzeros_with_index_sparse":
        rows = log2(n * (m - 1)) + log2(nvars + 1)
        v = 2 * n + k
        nz = log2(sum(comb(v, d) for d in range(4)))
        ws = rows + nz + log2(width)
    else:
        raise ValueError(storage)
    return store, ws


def sem_point(n, m, storage, ceiled=False, kappa=1, p=0, free_yield=False, degree=4):
    T, _ = sem_time(n, m, ceiled, free_yield=free_yield)
    store, ws = sem_mem_parts(n, m, storage, degree)
    return T - log2(kappa) - p, log2add(store, ws + p)


def stage1_argmin(n, ceiled=False, free_yield=False):
    ms = range(2, min(M_HI, n) + 1)
    return min(ms, key=lambda m: sem_time(n, m, ceiled, free_yield=free_yield)[1])


def metric_cost(T, Mem, fam, par=None):
    if fam == "time_only":
        return T
    if fam == "time_memory_product":
        return T + Mem
    if fam == "memory_weighted_time_alpha":
        return T if par == 0.0 else T + par * Mem
    if fam == "fixed_budget_hard":
        return T if Mem <= par else INF
    if fam == "fixed_budget_soft":
        return T + max(0.0, Mem - par)
    raise ValueError(fam)


def vow_W(n, h=1, frobenius=False):
    W = LOG2_W + n / 2 - 0.5 * log2(h)
    if frobenius:
        W -= 0.5 * log2(n)
    return W


def vow_point(n, mode, store_log2, p, h=1, budget=None):
    W = vow_W(n, h)
    unit = log2(3 * n)
    room = INF if budget is None else budget - unit
    if room < 0:
        raise ValueError("budget below 3n")
    if mode == "record_point_M1_w30":
        return W - min(p, room), min(store_log2, room) + unit
    if mode == "own_curve_product_minimum":
        pe = min(p, room)
        return W - pe + 1.0, pe + unit                  # w = M: T = W(1/M + 1/M) = 2W/M
    if mode == "sect113r2_calibrated_ratio":
        if room == INF:
            pe, we = p, p + 13.3
        else:
            pe = max(0.0, min(p, room - 13.3))
            we = min(pe + 13.3, room)
        return W + log2(2.0 ** (-pe) + 2.0 ** (-we)), we + unit
    if mode == "informative_null_3n":
        return W - min(p, room), unit                  # C3 null: record mode with store_log2 = 0 (3n bits)
    if mode == "zero_memory":
        return W - p, -INF
    raise ValueError(mode)


def semaev_cost_at(n, fam, par, storage, ceiled, p, msel, kappa=1, free_yield=False):
    if msel == "stage1_argmin":
        m = stage1_argmin(n, ceiled, free_yield)
        T, Mem = sem_point(n, m, storage, ceiled, kappa, p, free_yield)
        return metric_cost(T, Mem, fam, par), m, T, Mem
    best = None
    for m in range(2, min(M_HI, n) + 1):
        T, Mem = sem_point(n, m, storage, ceiled, kappa, p, free_yield)
        c = metric_cost(T, Mem, fam, par)
        if best is None or c < best[0]:
            best = (c, m, T, Mem)
    return best


def compare(fam, par, storage, ceiled, store_log2, p, mode, kappa, h, msel, free_yield=False,
            n_lo=N_LO, n_hi=N_HI):
    budget = par if fam.startswith("fixed_budget") else None
    wins, margins, ms = [], {}, {}
    for n in range(n_lo, n_hi + 1):
        sc, m, _T, _M = semaev_cost_at(n, fam, par, storage, ceiled, p, msel, kappa, free_yield)
        bT, bM = vow_point(n, mode, store_log2, p, h, budget)
        bc = metric_cost(bT, bM, fam, par)
        if sc == INF and bc == INF:
            mg, w = None, False
        elif sc == INF:
            mg, w = -INF, False
        elif bc == INF:
            mg, w = INF, True
        else:
            mg, w = bc - sc, (bc - sc) > 0
        margins[n] = mg
        ms[n] = m
        wins.append(w)
    intervals, start = [], None
    for i, w in enumerate(wins):
        n = n_lo + i
        if w and start is None:
            start = n
        if not w and start is not None:
            intervals.append((start, n - 1))
            start = None
    if start is not None:
        intervals.append((start, n_hi))
    first = intervals[0][0] if intervals else None
    persistent = intervals[-1][0] if intervals and intervals[-1][1] == n_hi else None
    parent = next((n for n in range(250, 651) if wins[n - n_lo]), None)
    return {"first": first, "persistent": persistent, "parent_window": parent, "intervals": intervals,
            "margin_409": margins.get(409), "margin_571": margins.get(571),
            "m_409": ms.get(409), "m_571": ms.get(571)}
