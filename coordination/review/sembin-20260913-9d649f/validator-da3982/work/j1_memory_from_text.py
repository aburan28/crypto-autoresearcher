#!/usr/bin/env python3
"""J1 -- a memory accounting for the chained-S_3 algorithm derived from the
FROZEN TEXT ONLY, stated independently of the record's implementation.

Sections cited (inputs/SEMAEV-2015-310/paper_fulltext.md):
  S3 step 3   : the chain (5) at length t has t-1 equations S3(...)=0.
  S3 step 3/4 : "At most |V| relations (7) are necessary on the average",
                |V| = 2^k, k = ceil(n/m); each relation carries <= t
                factor-base entries plus the pair (u, v).
  S4.2        : "(5) for t = m is equivalent to a system of (m-1)n multivariate
                equations in (m-2)n + km ~ (m-1)n variables in F_p", and
                "keeping it in computer memory before solving is difficult by
                itself for m >= 4".
  S4.5        : deg_{F2} S3(x1,x2,x3) = 3; deg_{F2} S3(x1,x2,z) = 2 for z a
                constant.  Assumption 1: d_F4 <= 4 for all 2 <= t <= m.
  S4.5.1      : "n(t-1) coordinate equations in n(t-2) + kt variables".
  S4.5.2      : stage 1 = 2^k n^{4w} / P; solving by F4 is [n(m-1)]^{4w}; the
                block-structured variant is n^{4w}; no memory anywhere.

Nothing here reads the producer's memory model; the producer's figures are
pasted in at the end ONLY for the differencing step, from the committed COST
record, and are labelled as such.
"""
import json
import math

FIPS = [163, 233, 283, 409, 571]
# argmin over m of Table 3's printed stage-1 column, recomputed here from
# eq. (15) with the un-ceiled k the printed table reproduces from.
def log2_fact(m):
    return math.lgamma(m + 1.0) / math.log(2.0)


def stage1_log2(n, m, omega=3.0):
    k = n / m                       # un-ceiled, the reading Table 3 prints
    return log2_fact(m) + k + (n - m * k) + 4.0 * omega * math.log2(n)


def opt_m(n):
    return min(range(2, 31), key=lambda m: stage1_log2(n, m))


def width_log2(N, D=4):
    """log2 #{Boolean monomials of degree <= D in N variables}."""
    return math.log2(sum(math.comb(N, d) for d in range(D + 1)))


def accounting(n, m):
    k = -(-n // m)                                    # ceil(n/m), S4.5 / S4.2
    # ---- (1) relation store, S3 step 3 -------------------------------------
    rows = k                                          # log2 of 2^k relations
    row_bits = m * k + 2 * n                          # <=m entries of k bits + (u,v)
    store_log2 = rows + math.log2(row_bits)
    # ---- (2) the degree-4 system, S4.2 / S4.5.1 ----------------------------
    N = (m - 2) * n + k * m                           # t = m
    W = width_log2(N, 4)                              # columns at degree <= 4
    # rows actually reachable at degree <= 4: the degree-<=4 part of the ideal
    # is spanned by f_i * (monomials of degree <= 4 - deg f_i).  S4.5 gives
    # deg f_i = 3 for the (t-2)n interior coordinate equations and 2 for the n
    # coordinate equations of the last equation S3(u_{t-2}, x_t, R_X) = 0.
    mult_deg1 = 1 + N
    mult_deg2 = 1 + N + math.comb(N, 2)
    span = (m - 2) * n * mult_deg1 + n * mult_deg2
    span_log2 = math.log2(span)
    rank_log2 = min(span_log2, W)
    return {
        "n": n, "m": m, "k": k, "N_variables": N,
        "relation_store_row_bits": row_bits,
        "relation_store_log2_bits": store_log2,
        "macaulay_width_log2": W,
        "reachable_row_count_log2": span_log2,
        "rank_bound_log2": rank_log2,
        # reading A: SQUARE W x W matrix (Galbraith's C(N+3,4)^2; also the
        # object whose W^omega elimination is Semaev's own [n(m-1)]^{4w}).
        "workingset_dense_square_log2": 2.0 * W,
        "workingset_sparse_square_log2": W + (3.0 * math.log2(n) - math.log2(m)),
        # reading B: the ACTUAL degree-4 matrix shape, rank x W.
        "workingset_dense_actual_log2": rank_log2 + W,
        "workingset_sparse_actual_log2": rank_log2
        + (3.0 * math.log2(n) - math.log2(m)),
        "square_inflation_bits": W - rank_log2,
    }


def log2_add(a, b):
    hi, lo = max(a, b), min(a, b)
    return hi if hi - lo > 60 else hi + math.log2(1.0 + 2.0 ** (lo - hi))


# figures QUOTED from the committed COST-SEMBIN-8d123b.yaml for differencing
RECORD = {163: (70.3526, 55.2782, 7), 233: (77.7467, 59.9741, 9),
          283: (80.0103, 61.9374, 9), 409: (86.8371, 66.5250, 11),
          571: (91.7726, 70.2718, 12)}

out = {"note": "derived from inputs/SEMAEV-2015-310/ only; RECORD_* columns are "
               "quoted from COST-SEMBIN-8d123b.yaml for differencing",
       "rows": []}
for n in FIPS:
    m = opt_m(n)
    a = accounting(n, m)
    tot_sq_dense = log2_add(a["relation_store_log2_bits"],
                            a["workingset_dense_square_log2"])
    tot_sq_sparse = log2_add(a["relation_store_log2_bits"],
                             a["workingset_sparse_square_log2"])
    tot_ac_dense = log2_add(a["relation_store_log2_bits"],
                            a["workingset_dense_actual_log2"])
    tot_ac_sparse = log2_add(a["relation_store_log2_bits"],
                             a["workingset_sparse_actual_log2"])
    rd, rs, rm = RECORD[n]
    a.update({
        "m_agrees_with_record": m == rm, "record_m": rm,
        "MY_total_dense_square": round(tot_sq_dense, 4),
        "MY_total_sparse_square": round(tot_sq_sparse, 4),
        "MY_total_dense_actual_shape": round(tot_ac_dense, 4),
        "MY_total_sparse_actual_shape": round(tot_ac_sparse, 4),
        "RECORD_dense": rd, "RECORD_sparse": rs,
        "delta_dense_square_vs_record": round(tot_sq_dense - rd, 4),
        "delta_sparse_square_vs_record": round(tot_sq_sparse - rs, 4),
        "delta_dense_actual_vs_record": round(tot_ac_dense - rd, 4),
        "delta_sparse_actual_vs_record": round(tot_ac_sparse - rs, 4),
        "store_dominates": a["relation_store_log2_bits"]
        > a["workingset_sparse_square_log2"],
        "sum_minus_max_dense_bits": round(
            tot_sq_dense - max(a["relation_store_log2_bits"],
                               a["workingset_dense_square_log2"]), 9),
        "sum_minus_max_sparse_bits": round(
            tot_sq_sparse - max(a["relation_store_log2_bits"],
                                a["workingset_sparse_square_log2"]), 9),
    })
    for kk in ("relation_store_log2_bits", "macaulay_width_log2",
               "reachable_row_count_log2", "rank_bound_log2",
               "workingset_dense_square_log2", "workingset_sparse_square_log2",
               "workingset_dense_actual_log2", "workingset_sparse_actual_log2",
               "square_inflation_bits"):
        a[kk] = round(a[kk], 4)
    out["rows"].append(a)

# the plan's stated variable count, checked against the paper's
out["plan_variable_count_check"] = [
    {"n": n, "m": m, "k": -(-n // m),
     "plan_formula_m_k_plus_2n": m * (-(-n // m)) + 2 * n,
     "paper_S4.2_formula_m_minus_2_n_plus_km": (m - 2) * n + (-(-n // m)) * m,
     "record_asserts": rec}
    for n, m, rec in ((310, 10, 2790), (409, 11, 4099), (571, 12, 6286))]
print(json.dumps(out, indent=1))
