#!/usr/bin/env python3
"""J4 -- independent re-derivation of eq. (11)'s yield-loss scaling, its regime
boundary, and the per-unit-of-t solving-cost saving under both of the paper's
own readings, checked against the MEASURED drops in Tables 1-2.

Derived from the frozen text only:
  S4.3  eq. (11): P(q,m,t,|V|) = 1 - (1-1/q)^K ~ 1 - exp(-|V|^t/(q t!)),
        K ~ |V|^t/t!.  With q = 2^n and |V| = 2^k this is
        P = 1 - exp(-x),  x = 2^{tk-n}/t!.
        "If |V|^t/(q t!) = o(1), then P ~ |V|^t/(q t!)."
  S4.5.2  solving by F4 is [n(m-1)]^{4w}; block-structured variant n^{4w};
          stage 1 = 2^k * solve / P.
  S4.5.1  the system at chain length t has n(t-1) equations in n(t-2)+kt vars.
  S3 step 3  "for t < m the solving running time ... drops dramatically and the
             probability of solving is relatively lower ... One can probably win
             in efficiency and lose in probability."
Measured data: inputs/SEMAEV-2015-310/tables.yaml (transcribed Tables 1-2).
"""
import json
import math
import sys

sys.path.insert(0, "/workspace")
import yaml  # noqa: E402

OMEGA = 3.0


def log2_fact(t):
    return math.lgamma(t + 1.0) / math.log(2.0)


def log2_x(n, t, k):
    """log2 of eq. (11)'s argument x = 2^{tk-n}/t!."""
    return t * k - n - log2_fact(t)


def log2_P(n, t, k):
    lx = log2_x(n, t, k)
    if lx < -40.0:
        return lx                                  # 1-exp(-x) = x
    if lx > 10.0:
        return 0.0
    return math.log2(-math.expm1(-(2.0 ** lx)))


def width_log2(N, D=4):
    return math.log2(sum(math.comb(N, d) for d in range(D + 1)))


def solve_log2(n, t, k, model):
    if model == "block_n4w":
        return 4.0 * OMEGA * math.log2(n)
    if model == "f4_std":
        return 4.0 * OMEGA * math.log2(n * (t - 1))
    if model == "macaulay4":
        return OMEGA * width_log2(int(round(t * k + max(t - 2, 0) * n)))
    raise ValueError(model)


out = {}

# ---------------------------------------------------------------- (a) regime
# Where does eq. (11) stop being in the small-x (exponential-yield-loss) regime?
# x >= 1  => P saturates and yield loss is NOT exponential in the chain length.
# The 5%-deviation boundary is x ~ 0.1 (1-exp(-x) = x(1 - x/2 + ...)).
def opt_m_table3(n):
    def s1(m):
        kk = n / m
        return log2_fact(m) + kk + (n - m * kk) + 4.0 * OMEGA * math.log2(n)
    return min(range(2, 31), key=s1)


worst = []
sat_cells, near_cells = [], []
for n in range(250, 601):
    for m in range(2, 21):
        k = -(-n // m)                              # ceiled, the definition
        ku = n / m                                  # un-ceiled, Table 3's
        for t in range(2, m + 1):
            for lbl, kk in (("ceiled", float(k)), ("unceiled", ku)):
                lx = log2_x(n, t, kk)
                if lx >= 0.0:
                    sat_cells.append({"n": n, "m": m, "t": t, "k": lbl,
                                      "log2_x": round(lx, 4)})
                elif lx >= math.log2(0.1):
                    near_cells.append({"n": n, "m": m, "t": t, "k": lbl,
                                       "log2_x": round(lx, 4)})
    m0 = opt_m_table3(n)
    k0 = -(-n // m0)
    worst.append({"n": n, "m_opt": m0, "k": k0,
                  "log2_x_at_t_eq_m": round(log2_x(n, m0, float(k0)), 3),
                  "yield_loss_per_unit_t_bits":
                      round(log2_P(n, m0, float(k0))
                            - log2_P(n, m0 - 1, float(k0)), 3)})

out["regime_boundary"] = {
    "criterion": "x = 2^{tk-n}/t!; small-x regime (P ~ x, yield loss "
                 "exponential in the chain length) requires x << 1",
    "cells_swept": "n in [250,600], m in [2,20], t in [2,m], k both readings",
    "n_saturated_cells_x_ge_1": len(sat_cells),
    "saturated_cells_sample": sat_cells[:8],
    "saturated_cells_m_values": sorted({c["m"] for c in sat_cells}),
    "saturated_cells_t_values": sorted({c["t"] for c in sat_cells}),
    "n_near_boundary_cells_x_ge_0.1": len(near_cells),
    "near_boundary_m_values": sorted({c["m"] for c in near_cells}),
    "max_log2_x_at_optimal_m": max(r["log2_x_at_t_eq_m"] for r in worst),
    "at_optimal_m_rows": [r for r in worst
                          if r["n"] in (250, 283, 310, 409, 500, 571, 600)],
}

# ------------------------------------------------- (b) solving saving per unit t
rows = []
for n in (163, 233, 283, 310, 409, 571):
    m = opt_m_table3(n)
    k = float(-(-n // m))
    r = {"n": n, "m_opt": m, "k": int(k),
         "yield_loss_per_unit_t_bits": round(log2_P(n, m, k)
                                             - log2_P(n, m - 1, k), 3)}
    for model in ("block_n4w", "f4_std", "macaulay4"):
        r[f"solve_saving_per_unit_t_{model}"] = round(
            solve_log2(n, m, k, model) - solve_log2(n, m - 1, k, model), 3)
        r[f"solve_saving_total_t_m_to_2_{model}"] = round(
            solve_log2(n, m, k, model) - solve_log2(n, 2, k, model), 3)
    r["yield_loss_total_t_m_to_2_bits"] = round(log2_P(n, m, k)
                                                - log2_P(n, 2, k), 3)
    rows.append(r)
out["per_unit_t_at_optimal_m"] = rows

# is the saving polynomial in n?  compare the TOTAL available saving against
# 4w*log2(m-1), the closed form of ((m-1)/1)^{4w}.
out["polynomial_check"] = [
    {"n": r["n"], "m": r["m_opt"],
     "f4_std_total_saving_bits": r["solve_saving_total_t_m_to_2_f4_std"],
     "closed_form_4w_log2_m_minus_1": round(4 * OMEGA
                                            * math.log2(r["m_opt"] - 1), 3),
     "macaulay4_total_saving_bits": r["solve_saving_total_t_m_to_2_macaulay4"],
     "yield_loss_total_bits": r["yield_loss_total_t_m_to_2_bits"]}
    for r in rows]

# ------------------------------- (b) reconcile with the MEASURED Tables 1-2
tab = yaml.safe_load(open("/workspace/inputs/SEMAEV-2015-310/tables.yaml"))
# only table_2 varies t independently of m; table_1 is all t = m.
meas = [dict(r, table="table_2") for r in tab["table_2"]["rows"]]
groups = {}
for r in meas:
    groups.setdefault((r["table"], r["n"], r["m"], r["k"]), []).append(r)
recon = []
for key, g in sorted(groups.items()):
    if len(g) < 2:
        continue
    g.sort(key=lambda r: -r["t"])
    for a, b in zip(g, g[1:]):                      # a.t = b.t + 1
        if a["t"] != b["t"] + 1 or not (a["avg_seconds"] and b["avg_seconds"]):
            continue
        k = float(a["k"])
        recon.append({
            "table": key[0], "n": a["n"], "m": a["m"], "t_from": a["t"],
            "t_to": b["t"],
            "measured_solve_drop_bits": round(math.log2(a["avg_seconds"]
                                                        / b["avg_seconds"]), 3),
            "predicted_f4_std_bits": round(solve_log2(a["n"], a["t"], k, "f4_std")
                                           - solve_log2(a["n"], b["t"], k,
                                                        "f4_std"), 3),
            "predicted_macaulay4_bits": round(
                solve_log2(a["n"], a["t"], k, "macaulay4")
                - solve_log2(a["n"], b["t"], k, "macaulay4"), 3),
            "yield_loss_theory_bits": round(math.log2(a["P_theoretical"]
                                                      / b["P_theoretical"]), 3),
            "yield_loss_eq11_recomputed_bits": round(log2_P(a["n"], a["t"], k)
                                                     - log2_P(a["n"], b["t"], k),
                                                     3),
            "measured_expected_cost_per_relation_change_bits": round(
                math.log2((a["avg_seconds"] / a["P_theoretical"])
                          / (b["avg_seconds"] / b["P_theoretical"])), 3),
        })
out["measured_tables_reconciliation"] = {
    "note": "positive measured_solve_drop_bits = solving is cheaper at the "
            "smaller t; positive measured_expected_cost_per_relation_change "
            "= the SHORTER chain is cheaper per relation, i.e. t < m PAYS at "
            "these parameters",
    "rows": recon,
    "n_rows_where_short_chain_pays": sum(
        1 for r in recon
        if r["measured_expected_cost_per_relation_change_bits"] > 0),
    "n_rows": len(recon),
}
# and the same quantity end to end, t = m down to t = 2, where measured
endpoints = []
for key, g in sorted(groups.items()):
    if len(g) < 2:
        continue
    hi = max(g, key=lambda r: r["t"])
    lo = min(g, key=lambda r: r["t"])
    if hi["t"] == lo["t"] or not lo["avg_seconds"]:
        continue
    endpoints.append({
        "table": key[0], "n": hi["n"], "m": hi["m"],
        "t_m": hi["t"], "t_min": lo["t"],
        "measured_cost_per_relation_ratio_log2": round(
            math.log2((hi["avg_seconds"] / hi["P_theoretical"])
                      / (lo["avg_seconds"] / lo["P_theoretical"])), 3),
        "k": hi["k"]})
out["measured_endpoint_cost_per_relation"] = endpoints
print(json.dumps(out, indent=1))
