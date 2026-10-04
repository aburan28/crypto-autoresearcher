#!/usr/bin/env python3
"""J1 -- Semaev's memory model, re-derived from the frozen text.

TASK-20260913-da3982, validator, REVIEW-SEMBIN-20260913-9d649f.

This file does NOT import the producer's code. Every formula is written from
inputs/SEMAEV-2015-310/paper_fulltext.md with the section noted inline. The
record's figures are hard-coded as literals ONLY for comparison, quoted from
COST-SEMBIN-8d123b.yaml.

What is derived here:
  (c) the variable count N of the chained system at t = m, from Section 4.5.1
  (b) three storage accountings of the degree-4 Macaulay matrix, including the
      ROW COUNT that both the record's readings assume away
  (d) MAX versus SUM of relation store and working set
  and an empirical check of all three accountings against the memory column of
  Tables 1-2, which is the only memory measurement of this object that exists.
"""

from __future__ import annotations

import json
import math
from math import comb, log2

# ---------------------------------------------------------------------------
# Semaev's own parameters. Section references are to the frozen text.
# ---------------------------------------------------------------------------


def k_ceiled(n: int, m: int) -> int:
    """Section 3 step 1 / Section 4.5: |V| = 2^k, k = ceil(n/m)."""
    return -(-n // m)


def n_variables(n: int, t: int, k: int) -> int:
    """Section 4.5.1, verbatim: the system resulting from (5) 'consists of
    n(t-1) coordinate equations in n(t-2) + kt variables'. Section 4.2 states
    the same count at t = m as '(m-2)n + km'.

    Structurally: x_1..x_t range over V, a k-dimensional F_2-subspace, giving
    t*k Boolean variables; u_1..u_{t-2} range over F_q = F_{2^n}, giving
    (t-2)*n Boolean variables under Weil descent.
    """
    return n * max(t - 2, 0) + k * t


def n_equations(n: int, t: int) -> int:
    """Section 4.5.1: n(t-1) coordinate equations. (5) has t-1 equations over
    F_q, each descending to n Boolean coordinate equations of total degree 3
    (Section 4.5: degF2 S_3 = 3)."""
    return n * (t - 1)


def macaulay_width(nvars: int, degree: int = 4) -> int:
    """Number of columns of the degree-<=`degree` Macaulay matrix over F_2.

    Section 4.4: 'The matrix incorporates at most C(n+d-1, d) < n^d columns.'
    Over F_2 with the field equations x^2 = x adjoined, monomials are
    SQUAREFREE, so the count is sum_{d'<=d} C(nvars, d'). This is the record's
    own width and the count KN-OPEN-86e7e1 quotes.
    """
    return sum(comb(nvars, d) for d in range(degree + 1))


def macaulay_rows(n: int, t: int, nvars: int, degree: int = 4) -> int:
    """Number of ROWS of the degree-4 Macaulay matrix M_4 of the chained system.

    Section 4.4 defines the rows as the products m_i * f_j with
    deg(m_i) + deg(f_j) <= d. Here every f_j is a coordinate equation of (5),
    of total degree 3 (Section 4.5), and d = 4 under Assumption 1. So
    deg(m_i) <= 1 and m_i ranges over {1, x_1, ..., x_N}: N + 1 multipliers per
    equation.

    This quantity appears NOWHERE in the record, and it is the one both of the
    record's storage readings assume equals the column count.
    """
    return n_equations(n, t) * (nvars + 1)


# ---------------------------------------------------------------------------
# The three storage accountings.
# ---------------------------------------------------------------------------


def relation_store_bits(n: int, m: int, k: int) -> float:
    """Section 3 step 3 ('At most |V| relations (7) are necessary on the
    average') and Section 4.5.2 ('collecting a system of <= 2^k ... relations').

    2^k rows, each holding <= m factor-base indices of k bits and the pair
    (u, v) of n bits each. This is the record's own charge and I take it as
    correct and generous-to-Semaev.
    """
    return k + log2(m * k + 2 * n)


def record_dense_bits(width: int) -> float:
    """The record's DENSE reading: width^2 bits.

    Provenance: this is GALBRAITH'S formula, not the frozen paper's. KN-LIT-e77232
    records it as 'C(N+3, 4)^2 entries' with N = (m-1)n, read from the live
    ellipticnews page (citation_provenance: retrieved). It presumes a SQUARE
    matrix of side = the column count.
    """
    return 2.0 * log2(width)


def record_sparse_bits(n: int, m: int) -> float:
    """The record's SEMAEV-SPARSE reading: (nm)^4/24 columns times n^3/m
    nonzeros per row.

    Provenance: Semaev's own reply in the same thread (KN-LIT-e77232, comment of
    2015-04-20). That entry records the load-bearing step explicitly: 'with row
    count OF THE ORDER OF THE COLUMN COUNT that is 2^70.3 nonzero positions'.
    So this reading also presumes rows ~ cols.
    """
    cols = 4.0 * log2(n * m) - log2(24.0)
    nz_per_row = 3.0 * log2(n) - log2(m)
    return cols + nz_per_row


def honest_dense_bits(rows: int, width: int) -> float:
    """Dense storage of the matrix Section 4.4 actually describes: rows x cols.

    Not a new model -- the SAME dense-row-echelon convention as the record's,
    with the row count derived rather than assumed equal to the column count.
    """
    return log2(rows) + log2(width)


def honest_nonzeros_bits(rows: int, n: int, t: int, k: int) -> float:
    """Total nonzeros of M_4, one bit each: rows x (nonzeros per row).

    A row is m_i * f_j where f_j is a cubic in the Boolean variables of at most
    3 field elements of (5) -- two intermediate u's (n bits each) and one x
    (k bits) -- so v = 2n + k variables, and the row's support is bounded by
    the squarefree monomials of degree <= 3 in those v variables (times the one
    multiplier m_i, which cannot increase the count).
    """
    v = 2 * n + k
    nz_per_row = sum(comb(v, d) for d in range(4))
    return log2(rows) + log2(nz_per_row)


# ---------------------------------------------------------------------------
# Comparator, from COST-SEMBIN-8d123b's own stated convention.
# ---------------------------------------------------------------------------


def semaev_time_log2(n: int, m: int, omega: float = 3.0) -> float:
    """Table 3's printed stage 1 (m! 2^{n/m} n^12) plus eq. (16) stage 2."""
    s1 = math.lgamma(m + 1.0) / math.log(2.0) + n / m + 4.0 * omega * log2(n)
    s2 = 2.0 * n / m
    hi, lo = max(s1, s2), min(s1, s2)
    return hi if hi - lo > 60 else hi + log2(1.0 + 2.0 ** (lo - hi))


def optimal_m(n: int, m_hi: int = 30) -> int:
    def s1(m):
        return math.lgamma(m + 1.0) / math.log(2.0) + n / m + 12.0 * log2(n)
    return min(range(2, min(m_hi, n) + 1), key=s1)


def vow_log2(n: int, store_log2: float = 30.0) -> tuple[float, float]:
    return log2(0.886) + n / 2.0, store_log2 + log2(3.0 * n)


# ---------------------------------------------------------------------------

FIPS = [163, 233, 283, 409, 571]
CELLS = [(310, 10), (409, 11), (571, 12)]

# quoted from COST-SEMBIN-8d123b.yaml parameter_sets, for comparison only
RECORD = {
    163: dict(m=7, time=123.7697, dense=70.3526, sparse=55.2782,
              margin_dense=-73.8632, margin_sparse=-58.7888),
    233: dict(m=9, time=138.7283, dense=77.7467, sparse=59.9741,
              margin_dense=-60.7004, margin_sparse=-42.9278),
    283: dict(m=9, time=147.6495, dense=80.0103, sparse=61.9374,
              margin_dense=-46.6047, margin_sparse=-28.5319),
    409: dict(m=11, time=166.5438, dense=86.8371, sparse=66.5250,
              margin_dense=-8.7946, margin_sparse=11.5175),
    571: dict(m=12, time=186.3070, dense=91.7726, sparse=70.2718,
              margin_dense=47.9882, margin_sparse=69.4889),
}
RECORD_N = {310: 2790, 409: 4099, 571: 6286}   # the record's N, from the contract

out: dict = {}

# =========================================================================
# (c) the variable count N
# =========================================================================
nvar_check = []
for (n, m) in CELLS:
    k = k_ceiled(n, m)
    N_451 = n_variables(n, m, k)                 # Section 4.5.1, t = m
    N_42 = (m - 2) * n + k * m                   # Section 4.2, verbatim
    nvar_check.append({
        "n": n, "m": m, "k_ceil_n_over_m": k,
        "N_from_section_4_5_1_n(t-2)+kt": N_451,
        "N_from_section_4_2_(m-2)n+km": N_42,
        "two_section_formulas_agree": N_451 == N_42,
        "record_N": RECORD_N[n],
        "agrees_with_record": N_451 == RECORD_N[n],
        "n_equations_n(t-1)": n_equations(n, m),
    })
out["j1c_variable_count"] = {
    "derivation": ("x_1..x_t in V give t*k Boolean variables (V is a "
                   "k-dimensional F_2-subspace, Section 4.5); u_1..u_{t-2} in "
                   "F_{2^n} give (t-2)*n. Section 4.5.1 states exactly this."),
    "rows": nvar_check,
    "all_agree": all(r["agrees_with_record"] and r["two_section_formulas_agree"]
                     for r in nvar_check),
}

# =========================================================================
# (b) + (d) the storage accountings at the FIPS labels
# =========================================================================
acct = []
for n in FIPS:
    m = optimal_m(n)
    k = k_ceiled(n, m)
    N = n_variables(n, m, k)
    width = macaulay_width(N, 4)
    rows = macaulay_rows(n, m, N, 4)
    store = relation_store_bits(n, m, k)

    r_dense = record_dense_bits(width)
    r_sparse = record_sparse_bits(n, m)
    h_dense = honest_dense_bits(rows, width)
    h_nz = honest_nonzeros_bits(rows, n, m, k)
    # sparse storage needs a column index per nonzero as well
    h_nz_indexed = h_nz + log2(log2(width))

    def total_max(ws):
        return max(store, ws)

    def total_sum(ws):
        hi, lo = max(store, ws), min(store, ws)
        return hi if hi - lo > 60 else hi + log2(1.0 + 2.0 ** (lo - hi))

    t_time = semaev_time_log2(n, m)
    vt, vm = vow_log2(n)

    acct.append({
        "n": n, "m_argmin": m, "k": k, "N": N,
        "macaulay_columns_log2": round(log2(width), 4),
        "macaulay_rows_log2": round(log2(rows), 4),
        "rows_over_cols_log2": round(log2(rows) - log2(width), 4),
        "relation_store_log2_bits": round(store, 4),
        "A_record_dense_width_squared": round(r_dense, 4),
        "B_record_semaev_sparse": round(r_sparse, 4),
        "C_honest_dense_rows_times_cols": round(h_dense, 4),
        "D_honest_nonzeros_one_bit_each": round(h_nz, 4),
        "E_honest_nonzeros_with_column_index": round(h_nz_indexed, 4),
        "record_dense_minus_honest_dense_bits": round(r_dense - h_dense, 4),
        "record_sparse_minus_honest_indexed_bits": round(r_sparse - h_nz_indexed, 4),
        "max_vs_sum_delta_bits_dense": round(total_sum(r_dense)
                                             - total_max(r_dense), 8),
        "max_vs_sum_delta_bits_sparse": round(total_sum(r_sparse)
                                              - total_max(r_sparse), 8),
        "working_set_dominates_store_dense": r_dense > store,
        "working_set_dominates_store_sparse": r_sparse > store,
        "semaev_time_log2": round(t_time, 4),
        "record_time_log2": RECORD[n]["time"],
        "time_agrees_to_0_01_bits": abs(t_time - RECORD[n]["time"]) < 0.01,
        "record_dense_total": RECORD[n]["dense"],
        "my_dense_total_max": round(total_max(r_dense), 4),
        "dense_total_agrees": abs(total_max(r_dense) - RECORD[n]["dense"]) < 0.01,
        "record_sparse_total": RECORD[n]["sparse"],
        "my_sparse_total_max": round(total_max(r_sparse), 4),
        "sparse_total_agrees": abs(total_max(r_sparse) - RECORD[n]["sparse"]) < 0.01,
        # margin = baseline metric cost - semaev metric cost, product metric
        "margin_product_record_dense": RECORD[n]["margin_dense"],
        "margin_product_honest_dense": round((vt + vm) - (t_time + total_max(h_dense)), 4),
        "margin_product_honest_indexed_sparse": round(
            (vt + vm) - (t_time + total_max(h_nz_indexed)), 4),
    })
out["j1bd_storage_accountings"] = {
    "note": ("A/B are the record's two readings. C/D/E are the same storage "
             "conventions with the ROW COUNT derived from Section 4.4 rather "
             "than assumed equal to the column count."),
    "rows": acct,
}

# crossover under each accounting, product metric
def crossover(kind: str, n_lo: int = 250, n_hi: int = 700) -> int | None:
    for n in range(n_lo, n_hi + 1):
        m = optimal_m(n)
        k = k_ceiled(n, m)
        N = n_variables(n, m, k)
        width = macaulay_width(N, 4)
        rows = macaulay_rows(n, m, N, 4)
        store = relation_store_bits(n, m, k)
        ws = {"record_dense": record_dense_bits(width),
              "record_sparse": record_sparse_bits(n, m),
              "honest_dense": honest_dense_bits(rows, width),
              "honest_indexed": honest_nonzeros_bits(rows, n, m, k)
                                + log2(log2(width))}[kind]
        mem = max(store, ws)
        vt, vm = vow_log2(n)
        if semaev_time_log2(n, m) + mem < vt + vm:
            return n
    return None


out["j1b_crossover_by_accounting_product_metric"] = {
    k: crossover(k) for k in ("record_dense", "record_sparse",
                              "honest_dense", "honest_indexed")
}
out["j1b_crossover_record_quoted"] = {"dense": 435, "semaev_sparse": 375}

# =========================================================================
# empirical check the record never ran: Tables 1-2 memory column
# =========================================================================
# (n, m, t, k, total_MB) from inputs/SEMAEV-2015-310/tables.yaml
T12 = [
    (12, 6, 6, 2, 257.8), (13, 4, 4, 4, 739.8), (13, 5, 5, 3, 1597.8),
    (14, 4, 4, 4, 879.7), (14, 5, 5, 3, 960.2), (15, 4, 4, 4, 1457.3),
    (15, 5, 5, 3, 3286.9), (16, 4, 4, 4, 1657.7), (17, 3, 3, 6, 378.1),
    (17, 3, 3, 6, 364.1), (17, 3, 3, 6, 355.1), (17, 3, 3, 6, 693.2),
    (12, 6, 6, 2, 289.9), (13, 4, 4, 4, 981.8), (13, 5, 5, 3, 1633.0),
    (14, 4, 4, 4, 1056.7), (14, 5, 5, 3, 1154.2), (15, 4, 4, 4, 1177.5),
    (15, 4, 3, 4, 64.1), (15, 4, 2, 4, 32.1), (15, 5, 5, 3, 2635.4),
    (15, 5, 4, 3, 424.9), (15, 5, 3, 3, 32.1), (15, 5, 2, 3, 32.1),
    (16, 4, 4, 4, 1145.2), (16, 4, 3, 4, 64.1), (16, 4, 2, 4, 32.1),
    (17, 3, 3, 6, 375.8), (19, 3, 3, 7, 1812.8), (19, 3, 2, 7, 32.1),
    (21, 3, 3, 7, 2437.8), (21, 3, 2, 7, 32.1), (40, 2, 2, 20, 3913.3),
]
BITS_PER_MB = 8.0 * 1024 * 1024
emp = []
for (n, m, t, k, mb) in T12:
    N = n_variables(n, t, k)
    width = macaulay_width(N, 4)
    rows = macaulay_rows(n, t, N, 4)
    measured_peak = log2(mb * BITS_PER_MB)
    # Two readings of the column, kept both because the sources disagree:
    #  tables.yaml transcription_limits: "memory is the total over 100 systems"
    #  internal evidence: 32.1 MB recurs exactly on 6 unrelated easy rows,
    #  which is the signature of a process floor, i.e. a PEAK not a sum.
    measured_per_system_if_total = log2(max(mb / 100.0, 1e-9) * BITS_PER_MB)
    marginal_over_floor = (log2(max(mb - 32.1, 1e-9) * BITS_PER_MB)
                           if mb > 32.2 else None)
    emp.append({
        "n": n, "m": m, "t": t, "k": k, "N": N, "measured_MB": mb,
        "measured_log2_bits_as_peak": round(measured_peak, 3),
        "measured_log2_bits_if_total_over_100": round(measured_per_system_if_total, 3),
        "measured_log2_bits_peak_minus_32MB_floor": (
            None if marginal_over_floor is None else round(marginal_over_floor, 3)),
        "pred_record_dense": round(record_dense_bits(width), 3),
        "pred_record_sparse": round(record_sparse_bits(n, m), 3),
        "pred_honest_dense_rows_x_cols": round(honest_dense_bits(rows, width), 3),
        "dense_minus_measured_peak": round(record_dense_bits(width) - measured_peak, 3),
        "sparse_minus_measured_peak": round(record_sparse_bits(n, m) - measured_peak, 3),
        "honest_dense_minus_measured_peak": round(
            honest_dense_bits(rows, width) - measured_peak, 3),
        "measured_peak_brackets_between_sparse_and_dense": bool(
            record_sparse_bits(n, m) <= measured_peak <= record_dense_bits(width)),
    })
nontrivial = [r for r in emp if r["measured_MB"] > 32.2]
out["j1_empirical_check_tables_1_2"] = {
    "why": ("The frozen source carries 34 memory measurements of THIS object "
            "(Tables 1-2, total_MB). The record's memory model is never "
            "compared against any of them. This is the only memory measurement "
            "of the chained-S_3 system that exists at any scale."),
    "reading_conflict": ("tables.yaml transcription_limits says the column is "
                         "the TOTAL over 100 systems; but 32.1 MB recurs "
                         "exactly on 6 unrelated easy rows, which is the "
                         "signature of a process floor and so of a PEAK. Both "
                         "readings are computed; neither is picked."),
    "rows": emp,
    "n_nontrivial_rows": len(nontrivial),
    "n_bracketed_peak_reading": sum(
        r["measured_peak_brackets_between_sparse_and_dense"] for r in nontrivial),
    "dense_minus_measured_peak_range": [
        round(min(r["dense_minus_measured_peak"] for r in nontrivial), 3),
        round(max(r["dense_minus_measured_peak"] for r in nontrivial), 3)],
    "sparse_minus_measured_peak_range": [
        round(min(r["sparse_minus_measured_peak"] for r in nontrivial), 3),
        round(max(r["sparse_minus_measured_peak"] for r in nontrivial), 3)],
    "honest_dense_minus_measured_peak_range": [
        round(min(r["honest_dense_minus_measured_peak"] for r in nontrivial), 3),
        round(max(r["honest_dense_minus_measured_peak"] for r in nontrivial), 3)],
}

# Kosters' n=45 m=t=2 measurement, from KN-LIT-e77232 (retrieved citation)
N45 = n_variables(45, 2, k_ceiled(45, 2))
w45 = macaulay_width(N45, 4)
r45 = macaulay_rows(45, 2, N45, 4)
out["j1_kosters_n45_anchor"] = {
    "source": "KN-LIT-e77232 comment of 2015-05-02, citation_provenance retrieved",
    "reported": "126 GB of RAM, step degree 5 reached (NOT 4)",
    "measured_log2_bits": round(log2(126.0 * 1024 * BITS_PER_MB), 3),
    "N": N45, "cols_log2": round(log2(w45), 3), "rows_log2": round(log2(r45), 3),
    "pred_record_dense_D4": round(record_dense_bits(w45), 3),
    "pred_record_sparse": round(record_sparse_bits(45, 2), 3),
    "pred_honest_dense_D4": round(honest_dense_bits(r45, w45), 3),
    "caveat": ("step degree 5 was reached, so a D=4 model is out of scope at "
               "this point; and 126 GB is a whole-process peak, not a matrix."),
}

print(json.dumps(out, indent=1))
