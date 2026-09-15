#!/usr/bin/env python3
"""Validator's OWN two-sided model, written from statements only, BEFORE opening
experiments/EXP-SEMBIN-2c40bb/code/surface_cost.py, code/sparse_independent.py or
experiments/EXP-SEMBIN-f4a17b/code/memory_charged_cost.py.

Sources used for the statements (and nothing else):
  - H-SEMBIN-97ea23 HEUR-VOW-CURVE: W = 0.886 * 2^(n/2); T = W(1/M + 1/w); Mem = 3n max(w, M) bits.
  - inputs/SEMAEV-2015-310/tables.yaml Table 3: stage1 = m! 2^(n/m) n^(4 omega) (omega = 3, so n^12),
    stage2 = 2^(2n/m); the freezing session notes the paper uses un-ceiled n/m in the exponents.
  - implementation.md's prose (no code): relation store 2^ceil(n/m) rows of (m k + 2n) bits, log2-summed
    with the working set; k reading is a TIME axis only; memory always pays ceil(n/m).
  - tables.yaml derived_checks.f4_working_set: N = (m-2) n + k m Boolean variables, degree <= 4 monomials
    (dense row-echelon memory = width^2 bits).  Alternative from KN-LIT-e77232 (Galbraith): N = (m-1) n,
    C(N+3, 4)^2.  Both are computed and reported.
  - KN-LIT-e77232 Semaev comment: columns (n m)^4 / 4!, nonzeros per row n^3 / m, rows ~ columns.

Covers M1(1), M4(1), M5(4) of REVIEW-SEMBIN-20260913-2c40bb.
"""
import json
import math
import sys
from math import comb, lgamma, log2

LOG2_W_CONST = log2(0.886)


def log2add(a, b):
    if a == -math.inf:
        return b
    if b == -math.inf:
        return a
    hi, lo = max(a, b), min(a, b)
    return hi + log2(1.0 + 2.0 ** (lo - hi))


def log2_factorial(m):
    return lgamma(m + 1) / math.log(2)


# ---------------------------------------------------------------- Semaev side
def semaev_stage1_log2(n, m, k_reading="unceiled", omega=3.0):
    """Table 3 eq.(15): m! 2^k 2^(n - m k) n^(4 omega). Unceiled k = n/m makes 2^k 2^(n-mk) = 2^(n/m)."""
    if k_reading == "unceiled":
        k = n / m
    else:
        k = math.ceil(n / m)
    return log2_factorial(m) + k + (n - m * k) + 4 * omega * log2(n)


def semaev_stage2_log2(n, m, k_reading="unceiled", omega_prime=2.0):
    k = n / m if k_reading == "unceiled" else math.ceil(n / m)
    return omega_prime * k


def semaev_time_log2(n, m, k_reading="unceiled", omega=3.0, include_stage2=True):
    s1 = semaev_stage1_log2(n, m, k_reading, omega)
    if not include_stage2:
        return s1
    return log2add(s1, semaev_stage2_log2(n, m, k_reading))


def stage1_argmin_m(n, k_reading="unceiled", m_lo=2, m_hi=30):
    best = None
    for m in range(m_lo, m_hi + 1):
        v = semaev_stage1_log2(n, m, k_reading)
        if best is None or v < best[1]:
            best = (m, v)
    return best[0]


def relation_store_log2(n, m):
    k = math.ceil(n / m)
    return k + log2(m * k + 2 * n)


def n_variables(n, m, convention="tables_yaml"):
    k = math.ceil(n / m)
    if convention == "tables_yaml":
        return (m - 2) * n + k * m
    if convention == "galbraith":
        return (m - 1) * n
    raise ValueError(convention)


def dense_ws_log2(n, m, degree=4, convention="tables_yaml", width="C(N+d,d)"):
    N = n_variables(n, m, convention)
    if width == "C(N+d,d)":
        w = comb(N + degree, degree)
    elif width == "C(N+d-1,d)":
        w = comb(N + degree - 1, degree)
    elif width == "sum_C(N,i)":
        w = sum(comb(N, i) for i in range(degree + 1))
    else:
        raise ValueError(width)
    return 2 * log2(w)


def sparse_ws_log2(n, m):
    """columns (nm)^4/24, nonzeros per row n^3/m, rows ~ columns -> n^7 m^3 / 24 nonzero positions (bits)."""
    return log2(n ** 7 * m ** 3) - log2(24)


def semaev_memory_log2(n, m, reading, **kw):
    store = relation_store_log2(n, m)
    if reading == "dense_row_echelon":
        ws = dense_ws_log2(n, m, **kw)
    elif reading == "semaev_sparse":
        ws = sparse_ws_log2(n, m)
    else:
        raise ValueError(reading)
    return log2add(store, ws)


# ---------------------------------------------------------------- vOW side
def vow_W_log2(n):
    return LOG2_W_CONST + n / 2


def vow_time_mem_log2(n, log2_M, log2_w):
    W = vow_W_log2(n)
    T = W + log2add(-log2_M, -log2_w)  # W (1/M + 1/w)
    Mem = log2(3 * n) + max(log2_w, log2_M)
    return T, Mem


def vow_record_point(n, store_log2=30):
    """The parent's charge: T = W/M with M = 1 (no 1/w tail), Mem = 3n * 2^store."""
    W = vow_W_log2(n)
    return W, log2(3 * n) + store_log2


def vow_own_curve_min(n, log2_M=0):
    return vow_time_mem_log2(n, log2_M, log2_M)


# ---------------------------------------------------------------- crossovers
def crossover(n_lo, n_hi, margin_fn):
    """margin_fn(n) = baseline_log2 - semaev_log2 (positive = Semaev cheaper).
    Returns (first_crossing_n, persistent_crossover_n) over [n_lo, n_hi]."""
    first = None
    persistent = None
    for n in range(n_lo, n_hi + 1):
        s = margin_fn(n) > 0
        if s and first is None:
            first = n
        if s and persistent is None:
            persistent = n
        if not s:
            persistent = None
    return first, persistent


def main():
    out = {}
    # ------------------------------------------------------------ M1(1)
    m1 = {}
    for include_stage2 in (True, False):
        for reading in ("dense_row_echelon", "semaev_sparse"):
            for conv in ("tables_yaml", "galbraith"):
                def margin_time_only(n):
                    m = stage1_argmin_m(n)
                    return vow_W_log2(n) - semaev_time_log2(n, m, include_stage2=include_stage2)

                def margin_product_record(n):
                    m = stage1_argmin_m(n)
                    T, Mem = vow_record_point(n)
                    return (T + Mem) - (semaev_time_log2(n, m, include_stage2=include_stage2)
                                        + semaev_memory_log2(n, m, reading, convention=conv))

                def margin_product_own(n):
                    m = stage1_argmin_m(n)
                    T, Mem = vow_own_curve_min(n)
                    return (T + Mem) - (semaev_time_log2(n, m, include_stage2=include_stage2)
                                        + semaev_memory_log2(n, m, reading, convention=conv))

                key = f"stage2={'incl' if include_stage2 else 'excl'}|{reading}|N={conv}"
                m1[key] = {
                    "time_only_first_persistent": crossover(3, 700, margin_time_only),
                    "product_record_first_persistent": crossover(3, 700, margin_product_record),
                    "product_own_curve_first_persistent": crossover(3, 700, margin_product_own),
                    "margin_409_time_only": margin_time_only(409),
                    "margin_409_product_record": margin_product_record(409),
                    "margin_409_product_own": margin_product_own(409),
                    "time_only_first_persistent_window_250_650": crossover(250, 650, margin_time_only),
                    "product_record_first_persistent_window_250_650": crossover(250, 650, margin_product_record),
                    "product_own_first_persistent_window_250_650": crossover(250, 650, margin_product_own),
                }
    # excess of record charge over 6nW at the labels
    excess = {}
    for n in (163, 233, 283, 409, 571):
        T, Mem = vow_record_point(n)
        T2, Mem2 = vow_own_curve_min(n)
        excess[n] = {"record_product_log2": T + Mem, "own_min_product_log2": T2 + Mem2,
                     "six_nW_log2": log2(6 * n) + vow_W_log2(n), "excess_bits": (T + Mem) - (T2 + Mem2)}
    # product invariance along the ray: check a few (w, M) with w = M and w != M
    inv = {}
    for lw, lM in ((0, 0), (10, 10), (30, 30), (30, 0), (0, 30), (40, 20), (13.3, 0)):
        T, Mem = vow_time_mem_log2(409, lM, lw)
        inv[f"w=2^{lw},M=2^{lM}"] = {"T": T, "Mem": Mem, "product_minus_6nW": (T + Mem) - (log2(6 * 409) + vow_W_log2(409))}
    m1["record_excess_over_6nW_at_labels"] = excess
    m1["product_along_curve_n409"] = inv
    m1["argmin_m_at_labels_unceiled"] = {n: stage1_argmin_m(n) for n in (310, 409, 571)}
    out["M1_1"] = m1

    # ------------------------------------------------------------ M4(1)
    m4 = {}
    n = 409
    for reading in ("dense_row_echelon", "semaev_sparse"):
        for conv in (("tables_yaml", "C(N+d,d)"), ("tables_yaml", "sum_C(N,i)"), ("galbraith", "C(N+d-1,d)")):
            if reading == "semaev_sparse" and conv != ("tables_yaml", "C(N+d,d)"):
                continue
            rows = []
            for m in range(2, 31):
                kw = {} if reading == "semaev_sparse" else {"convention": conv[0], "width": conv[1]}
                mem = semaev_memory_log2(n, m, reading, **kw)
                rows.append((m, mem, relation_store_log2(n, m),
                             sparse_ws_log2(n, m) if reading == "semaev_sparse" else dense_ws_log2(n, m, **kw)))
            best = min(rows, key=lambda r: r[1])
            m4[f"{reading}|{conv[0]}|{conv[1]}"] = {
                "cheapest_m": best[0], "cheapest_memory_log2": best[1],
                "store_at_cheapest": best[2], "ws_at_cheapest": best[3],
                "table_m_mem_store_ws": rows,
            }
    out["M4_1"] = m4

    # ------------------------------------------------------------ M5(4)
    n, m = 571, 12
    cols = log2((n * m) ** 4) - log2(24)
    nnz = 3 * log2(n) - log2(m)
    total = cols + nnz
    out["M5_4"] = {
        "n": n, "m": m,
        "columns_log2_(nm)^4/24": cols,
        "nonzeros_per_row_log2_n^3/m": nnz,
        "total_log2_rows_times_nnz": total,
        "exact_integer_n7m3_over_24_log2": log2(n ** 7 * m ** 3 / 24),
        "targets": {"columns": 46.38, "nonzeros": 23.89, "total": 70.3, "record_total": 70.2718},
        "at_labels_total_log2": {nn: sparse_ws_log2(nn, stage1_argmin_m(nn)) for nn in (163, 233, 283, 409, 571)},
    }
    json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)

    # -------------------------------------------------------- short print
    print("== M1(1) crossovers (first, persistent) over n in [3,700]; targets 303/303/435/375 and 520/460")
    for k, v in m1.items():
        if "|" in k:
            print(f"{k:55s} time_only={v['time_only_first_persistent']} "
                  f"prod_record={v['product_record_first_persistent']} prod_own={v['product_own_curve_first_persistent']} "
                  f"m409: to={v['margin_409_time_only']:.4f} rec={v['margin_409_product_record']:.4f} own={v['margin_409_product_own']:.4f}")
    print("excess over 6nW:", {k: round(v["excess_bits"], 4) for k, v in excess.items()})
    print("product along curve minus 6nW at n=409:", {k: round(v["product_minus_6nW"], 4) for k, v in inv.items()})
    print("argmin m:", m1["argmin_m_at_labels_unceiled"])
    print("== M4(1) cheapest Semaev memory over m at n=409")
    for k, v in m4.items():
        print(f"{k:50s} m*={v['cheapest_m']} mem={v['cheapest_memory_log2']:.4f} store={v['store_at_cheapest']:.4f} ws={v['ws_at_cheapest']:.4f}")
    print("== M5(4)", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out["M5_4"].items() if k != "at_labels_total_log2"})
    print("   at labels:", {k: round(v, 4) for k, v in out["M5_4"]["at_labels_total_log2"].items()})


if __name__ == "__main__":
    main()
