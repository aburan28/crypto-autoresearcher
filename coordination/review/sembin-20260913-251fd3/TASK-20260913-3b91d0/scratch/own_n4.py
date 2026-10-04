#!/usr/bin/env python3
"""N4: recompute the surface's columns, flag counts, T6 table, non-monotone
crossovers and spreads from the DEFINITIONS in cost-surface.json
column_definitions -- my own implementation, not the producer's.

Definitions as I read them off column_definitions and the grid:
  m   = ceil(n / C_0)
  N   = n (m - 1)                          (the `N_frozen` column)
  T1  = d_F log2 N                         (loose reading)
      = log2 C(N + d_F, d_F)               (binomial reading)
  T2  = (omega - 1) T1                     so T1 + T2 = omega log2 monomials
  T3  = log2(m 2^{C_0} + 1)
  T4  = -log2(1 - exp(-lambda)),  lambda = 2^{m C_0 - n - Delta}
        where Delta is ARM C's total Jensen deficit m (C_0 - E[log2 #Fb_i]),
        recomputed here from my OWN binomial sum (own_bounds2's model), not
        read from the run.  [Which expectation enters lambda is the HEUR-2
        ambiguity; I record the reading the surface uses rather than resolve it.]
  T5  = log2 C(N + 4, 4)  (frozen width, FIELD ELEMENTS -- note: the binomial
        count under BOTH T1 readings) ; dense = 2 x that
  T6  = omega T3
  time = log2(2^{T1+T2+T3+T4} + 2^{T6})    (T6 log-added)
  margins: as N2.
"""
import json
import math
from math import ceil, exp, lgamma, log, log2

RUN = "/workspace/experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/"
out = {}


def lchoose2(a, b):
    return (lgamma(a + 1) - lgamma(b + 1) - lgamma(a - b + 1)) / log(2)


_defcache = {}


def jensen_deficit_per_coset(c0):
    """C_0 - E[log2 X | X >= 1] for X = 2 Bin(2^{C_0}, 1/2) -- my own sum.

    Exact while 2^{C_0} <= 2^17; beyond that the asymptotic 1/(2 t ln 2)
    (checked against the exact value on the overlap in own_bounds2.py)."""
    if c0 in _defcache:
        return _defcache[c0]
    t = 2 ** c0
    if t > 131072:
        _defcache[c0] = 1.0 / (2 * t * log(2))
        return _defcache[c0]
    p0 = exp(-t * log(2))
    acc = 0.0
    for j in range(1, t + 1):
        acc += exp(lgamma(t + 1) - lgamma(j + 1) - lgamma(t - j + 1) - t * log(2)) * log2(2 * j)
    d = c0 - acc / (1.0 - p0)
    _defcache[c0] = d
    return d


def log2W(n):
    return log2(0.886) + n / 2.0


def vow(n, metric):
    if metric == "time_only":
        return log2W(n)
    if metric in ("time_memory_product", "area_time_AT"):
        return log2(6.0 * n) + log2W(n)
    return 0.5 * (log2(6.0 * n) + log2W(n))


def my_cell(n, omega, c0, reading, d_F=4):
    m = ceil(n / c0)
    N = n * (m - 1)
    t1 = d_F * log2(N) if reading == "nagao_loose_N_to_the_d" else lchoose2(N + d_F, d_F)
    t2 = (omega - 1) * t1
    t3 = log2(m * 2 ** c0 + 1)
    delta = m * jensen_deficit_per_coset(c0)
    log2lam = m * c0 - n - delta
    lam = 2.0 ** log2lam if log2lam < 500 else float("inf")
    t4 = 0.0 if lam == float("inf") else -log2(-math.expm1(-lam))
    t5f = lchoose2(N + 4, 4)
    t5d = 2 * t5f
    t6 = omega * t3
    dec = t1 + t2 + t3 + t4
    time = dec + log2(1 + 2 ** (t6 - dec)) if t6 - dec > -1000 else dec
    return dict(m=m, N=N, T1=t1, T2=t2, T3=t3, T4=t4, T5f=t5f, T5d=t5d, T6=t6,
                decompose=dec, time=time, log2_lambda=log2lam, deficit=delta)


cs = json.load(open(RUN + "cost-surface.json"))
cells = cs["cells"]

# ---------------------------------------------------------------- (1) all cells
worst = {k: (0.0, None) for k in ["T1", "T2", "T3", "T4", "T5f", "T5d", "T6",
                                  "time", "decompose", "log2_lambda", "N", "m"]}
worst_margin = (0.0, None)
flag_disagree = []
for c in cells:
    me = my_cell(c["n"], c["omega"], c["C_0"], c["monomial_count_reading"])
    pairs = {
        "T1": (me["T1"], c["T1_monomial_count_log2"]),
        "T2": (me["T2"], c["T2_linear_algebra_exponent_log2"]),
        "T3": (me["T3"], c["T3_coset_constant_log2"]),
        "T4": (me["T4"], c["T4_inverse_yield_log2"]),
        "T5f": (me["T5f"], c["T5_memory_log2_frozen_width"]),
        "T5d": (me["T5d"], c["T5_memory_log2_dense_width_squared"]),
        "T6": (me["T6"], c["T6_index_calculus_linalg_log2"]),
        "decompose": (me["decompose"], c["sum_T1_to_T4_time_decompose_log2"]),
        "time": (me["time"], c["time_log2_total"]),
        "log2_lambda": (me["log2_lambda"], c["log2_lambda"]),
        "N": (float(me["N"]), float(c["N_frozen"])),
        "m": (float(me["m"]), float(c["m"])),
    }
    for k, (a, b) in pairs.items():
        d = abs(a - b)
        if d > worst[k][0]:
            worst[k] = (d, (c["n"], c["omega"], c["C_0"], c["monomial_count_reading"]))
    for key, mg in c["margins"].items():
        metric, memr = key.split("|")
        t5 = me["T5f"] if memr == "frozen_width_C_N_plus_4_4" else me["T5d"]
        nag = {"time_only": me["time"],
               "time_memory_product": me["time"] + t5,
               "area_time_AT": me["time"] + t5,
               "equal_rate_max": max(me["time"], t5)}[metric]
        mymargin = nag - vow(c["n"], metric)
        d = abs(mymargin - mg["margin_bits_nagao_minus_vow"])
        if d > worst_margin[0]:
            worst_margin = (d, (c["n"], c["omega"], c["C_0"], c["monomial_count_reading"], key))
        if (mymargin < 0) != mg["nagao_ahead"]:
            flag_disagree.append((c["n"], c["omega"], c["C_0"], key, mymargin,
                                  mg["margin_bits_nagao_minus_vow"]))
out["recompute_all_320_cells"] = {
    "worst_abs_diff_bits_per_column": {k: {"bits": v[0], "at": v[1]} for k, v in worst.items()},
    "worst_abs_margin_diff_bits": {"bits": worst_margin[0], "at": worst_margin[1]},
    "nagao_ahead_flag_disagreements": flag_disagree,
    "cells": len(cells), "margin_checks": len(cells) * 8}
print("(1) MY recomputation of every column at all 320 cells, worst |difference| in bits:")
for k, v in worst.items():
    print(f"   {k:<12} {v[0]:.3e}   (worst at {v[1]})")
print(f"   margins     {worst_margin[0]:.3e}   (worst at {worst_margin[1]})")
print(f"   nagao_ahead flag disagreements: {len(flag_disagree)}")

# six named cells in detail
SIX = [(163, 2.376, 3, "nagao_loose_N_to_the_d"),
       (163, 3.0, 8, "binomial_C_N_plus_d_choose_d"),
       (571, 2.376, 3, "binomial_C_N_plus_d_choose_d"),
       (571, 2.376, 16, "nagao_loose_N_to_the_d"),
       (571, 3.0, 8, "binomial_C_N_plus_d_choose_d"),
       (571, 3.0, 16, "binomial_C_N_plus_d_choose_d")]
idx = {(c["n"], round(c["omega"], 3), c["C_0"], c["monomial_count_reading"]): c for c in cells}
six_rows = []
print("\n(1b) six cells in full (mine vs JSON):")
for key in SIX:
    n, om, c0, rd = key
    c = idx[(n, round(om, 3), c0, rd)]
    me = my_cell(n, om, c0, rd)
    row = {"cell": key, "m": [me["m"], c["m"]], "N": [me["N"], c["N_frozen"]]}
    for nm, mk, jk in [("T1", "T1", "T1_monomial_count_log2"),
                       ("T2", "T2", "T2_linear_algebra_exponent_log2"),
                       ("T3", "T3", "T3_coset_constant_log2"),
                       ("T4", "T4", "T4_inverse_yield_log2"),
                       ("T5_frozen", "T5f", "T5_memory_log2_frozen_width"),
                       ("T5_dense", "T5d", "T5_memory_log2_dense_width_squared"),
                       ("T6", "T6", "T6_index_calculus_linalg_log2"),
                       ("time", "time", "time_log2_total")]:
        row[nm] = [me[mk], c[jk], abs(me[mk] - c[jk])]
    row["margins"] = {}
    for k, mg in c["margins"].items():
        metric, memr = k.split("|")
        t5 = me["T5f"] if memr == "frozen_width_C_N_plus_4_4" else me["T5d"]
        nag = {"time_only": me["time"], "time_memory_product": me["time"] + t5,
               "area_time_AT": me["time"] + t5, "equal_rate_max": max(me["time"], t5)}[metric]
        row["margins"][k] = [nag - vow(n, metric), mg["margin_bits_nagao_minus_vow"],
                             abs(nag - vow(n, metric) - mg["margin_bits_nagao_minus_vow"])]
    six_rows.append(row)
    print(f"  {key}: m {row['m']}, N {row['N']}, "
          + ", ".join(f"{nm} {row[nm][0]:.4f}/{row[nm][1]:.4f} (d={row[nm][2]:.1e})"
                      for nm in ["T1", "T2", "T3", "T4", "T5_frozen", "T5_dense", "T6", "time"]))
    print("      margins max |diff| = %.2e" % max(v[2] for v in row["margins"].values()))
out["six_cells"] = six_rows

# ---------------------------------------------------------------- (2) flag counts
MEMORY_CHARGING = {"time_memory_product", "area_time_AT", "equal_rate_max"}
FIPS = {163, 233, 283, 409, 571}
COMMITTED = {2.376, 2.807, 3.0}
flags = []
for c in cells:
    me = my_cell(c["n"], c["omega"], c["C_0"], c["monomial_count_reading"])
    for key, mg in c["margins"].items():
        metric, memr = key.split("|")
        if metric not in MEMORY_CHARGING or c["n"] not in FIPS:
            continue
        t5 = me["T5f"] if memr == "frozen_width_C_N_plus_4_4" else me["T5d"]
        nag = {"time_memory_product": me["time"] + t5, "area_time_AT": me["time"] + t5,
               "equal_rate_max": max(me["time"], t5)}[metric]
        margin = nag - vow(c["n"], metric)
        if margin < 0:
            flags.append(dict(n=c["n"], omega=c["omega"], C_0=c["C_0"],
                              reading=c["monomial_count_reading"], metric=metric,
                              memory_reading=memr, margin=margin,
                              omega_committed=round(c["omega"], 3) in COMMITTED,
                              bound_B_ok=c["C_0_satisfies_ARM_C_bound_B_1bit"],
                              bound_B_value=c["ARM_C_bound_B_1bit"],
                              T6=me["T6"], time=me["time"],
                              T6_minus_time=me["T6"] - me["time"]))
f180 = [f for f in flags if f["omega_committed"]]
f120 = [f for f in f180 if f["bound_B_ok"]]
# check bound-B flag independently from MY bound B
my_boundB = {}


def my_bound_b(n, tol=1.0):
    for c0 in range(1, 35):
        if all(ceil(n / c) * jensen_deficit_per_coset(c) <= tol for c in range(c0, 35)):
            return c0
    return None


for n in sorted(FIPS):
    my_boundB[n] = my_bound_b(n)
f120_mine = [f for f in f180 if f["C_0"] >= my_boundB[f["n"]]]
out["flag_counts"] = dict(
    total_memory_charging_nagao_ahead_at_FIPS=len(flags),
    with_committed_omega=len(f180),
    with_committed_omega_and_bound_B=len(f120),
    with_committed_omega_and_MY_bound_B=len(f120_mine),
    my_bound_B=my_boundB,
    json_reported={"242": cs.get("escalation_flags_memory_charging_metric_nagao_ahead")
                   and len(cs["escalation_flags_memory_charging_metric_nagao_ahead"])},
)
print(f"\n(2) MY filter: memory-charging metric, FIPS label, nagao_ahead -> {len(flags)} cells; "
      f"committed omega -> {len(f180)}; and bound-B-satisfying C_0 -> {len(f120)} "
      f"(using MY OWN bound B {my_boundB}: {len(f120_mine)})")
print(f"    JSON's own escalation list length: {len(cs['escalation_flags_memory_charging_metric_nagao_ahead'])}")

from collections import Counter
dist = Counter((f["n"], f["metric"], f["memory_reading"]) for f in f120)
out["flag_120_distribution"] = {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in sorted(dist.items())}
print("    the 120, by (n, metric, memory reading):")
for k, v in sorted(dist.items()):
    print(f"      {k[0]} {k[1]:<20} {k[2]:<28} {v}")
byom = Counter((f["n"], f["omega"], f["metric"], f["memory_reading"]) for f in f120)
out["flag_120_by_n_omega"] = {f"{k[0]}|{k[1]}|{k[2]}|{k[3]}": v for k, v in sorted(byom.items())}
print("    the 120, by (n, omega, metric, memory reading):")
for k, v in sorted(byom.items()):
    print(f"      n={k[0]} omega={k[1]:<6} {k[2]:<20} {k[3]:<28} {v}")
print("    C_0 values present per (n, omega, metric, memory reading):")
c0map = {}
for f in f120:
    c0map.setdefault((f["n"], f["omega"], f["metric"], f["memory_reading"]), []).append((f["C_0"], f["reading"][:8]))
for k in sorted(c0map):
    print(f"      n={k[0]} omega={k[1]:<6} {k[2]:<20} {k[3]:<28} {sorted(set(c0map[k]))}")
out["flag_120_C0_map"] = {str(k): sorted(set(c0map[k])) for k in c0map}

# ---------------------------------------------------------------- (3) T6 at the 120
t6rows = [(f["n"], f["omega"], f["C_0"], f["metric"], f["memory_reading"], f["T6"], f["time"],
           f["T6"] - f["time"]) for f in f120]
mx = max(t6rows, key=lambda r: r[7])
out["T6_at_the_120"] = dict(
    max_T6_minus_time_bits=mx[7], at=mx[:5], T6=mx[5], time=mx[6],
    min_gap_time_minus_T6_bits=min(r[6] - r[5] for r in t6rows),
    max_T6_bits=max(r[5] for r in t6rows), min_time_bits=min(r[6] for r in t6rows),
    any_within_10_bits=any(r[7] > -10 for r in t6rows),
    rows=[{"n": r[0], "omega": r[1], "C_0": r[2], "metric": r[3], "memory_reading": r[4],
           "T6": r[5], "time": r[6], "T6_minus_time": r[7]} for r in t6rows])
print(f"\n(3) T6 over the 120 flagged cells: max(T6 - time) = {mx[7]:.3f} bits at "
      f"n={mx[0]}, omega={mx[1]}, C_0={mx[2]}, {mx[3]}|{mx[4]} (T6 {mx[5]:.2f} vs time {mx[6]:.2f}); "
      f"max T6 = {out['T6_at_the_120']['max_T6_bits']:.2f}, min time = {out['T6_at_the_120']['min_time_bits']:.2f}; "
      f"any within 10 bits: {out['T6_at_the_120']['any_within_10_bits']}")

# ---------------------------------------------------------------- (4) non-monotone crossovers
def margin_at(n, omega, c0, reading, metric, memr):
    me = my_cell(n, omega, c0, reading)
    t5 = me["T5f"] if memr == "frozen_width_C_N_plus_4_4" else me["T5d"]
    nag = {"time_only": me["time"], "time_memory_product": me["time"] + t5,
           "area_time_AT": me["time"] + t5, "equal_rate_max": max(me["time"], t5)}[metric]
    return nag - vow(n, metric)


nonmono = []
for (omega, c0, reading, metric, memr) in [
        (2.807, 3, "binomial_C_N_plus_d_choose_d", "time_only", "frozen_width_C_N_plus_4_4"),
        (3.0, 3, "binomial_C_N_plus_d_choose_d", "time_memory_product", "frozen_width_C_N_plus_4_4"),
        (2.376, 3, "binomial_C_N_plus_d_choose_d", "time_only", "frozen_width_C_N_plus_4_4"),
        (2.807, 8, "binomial_C_N_plus_d_choose_d", "time_only", "frozen_width_C_N_plus_4_4")]:
    seq = [(n, margin_at(n, omega, c0, reading, metric, memr)) for n in range(200, 1401, 100)]
    signs = [s for _, s in seq]
    crossings = [seq[i][0] for i in range(1, len(seq)) if (signs[i] < 0) != (signs[i - 1] < 0)]
    nonmono.append(dict(omega=omega, C_0=c0, metric=metric, memory_reading=memr,
                        margins={n: v for n, v in seq}, sign_changes_at=crossings,
                        n_sign_changes=len(crossings)))
    print(f"\n(4) margin sweep omega={omega}, C_0={c0}, {metric}|{memr}:")
    print("     " + "  ".join(f"{n}:{v:+.1f}" for n, v in seq))
    print(f"     sign changes: {len(crossings)} at n ~ {crossings}")
out["non_monotone_sweeps"] = nonmono
cross = cs["crossover_surface"]
nm_json = [x for x in cross if x.get("non_monotone")]
out["crossover_surface_non_monotone_entries"] = len(nm_json)
out["crossover_surface_keys"] = sorted(cross[0].keys())
print(f"\n    crossover_surface entries: {len(cross)}; keys {sorted(cross[0].keys())}; "
      f"entries flagged non_monotone: {len(nm_json)}")

# ---------------------------------------------------------------- (5) spreads at n = 571
def spread_table():
    res = {}
    for metric in ["time_only", "time_memory_product", "area_time_AT", "equal_rate_max"]:
        for memr in ["frozen_width_C_N_plus_4_4", "dense_width_squared"]:
            for reading in ["nagao_loose_N_to_the_d", "binomial_C_N_plus_d_choose_d"]:
                perom, perc0 = {}, {}
                for om in sorted(COMMITTED):
                    vals = {c0: margin_at(571, om, c0, reading, metric, memr)
                            for c0 in [2, 3, 4, 6, 8, 10, 12, 16]}
                    perom[om] = {"declared": max(vals.values()) - min(vals.values()),
                                 "bound_B": max(v for c0, v in vals.items() if c0 >= my_boundB[571])
                                            - min(v for c0, v in vals.items() if c0 >= my_boundB[571])}
                for c0 in [2, 3, 4, 6, 8, 10, 12, 16]:
                    vals = [margin_at(571, om, c0, reading, metric, memr) for om in sorted(COMMITTED)]
                    perc0[c0] = max(vals) - min(vals)
                res[f"{metric}|{memr}|{reading}"] = {
                    "max_C_0_spread_declared": max(v["declared"] for v in perom.values()),
                    "max_C_0_spread_bound_B": max(v["bound_B"] for v in perom.values()),
                    "max_omega_spread": max(perc0.values())}
    return res


mine_sp = spread_table()
json_sp = cs["spreads_at_n_571"]
sp_cmp = []
for k, v in mine_sp.items():
    j = json_sp[k]
    sp_cmp.append(dict(key=k, mine=v,
                       json={"max_C_0_spread_declared": j["max_C_0_spread_bits_declared_range"],
                             "max_C_0_spread_bound_B": j["max_C_0_spread_bits_bound_B_range"],
                             "max_omega_spread": j["max_omega_spread_bits"]},
                       max_abs_diff=max(abs(v["max_C_0_spread_declared"] - j["max_C_0_spread_bits_declared_range"]),
                                        abs(v["max_C_0_spread_bound_B"] - j["max_C_0_spread_bits_bound_B_range"]),
                                        abs(v["max_omega_spread"] - j["max_omega_spread_bits"]))))
out["spreads_at_571"] = sp_cmp
out["theorem_form_omega_spread_571"] = {
    "mine": (8 * 3.0 + 1) * log2(571) - (8 * 2.376 + 1) * log2(571),
    "json": cs["omega_spread_of_theorem_form_n_8w_plus_1_at_571_bits"]}
print("\n(5) spreads at n = 571 -- my recomputation vs the JSON, worst |diff| per key:")
for r in sp_cmp:
    print(f"   {r['key']:<66} declared {r['mine']['max_C_0_spread_declared']:7.3f}/"
          f"{r['json']['max_C_0_spread_declared']:7.3f}  boundB {r['mine']['max_C_0_spread_bound_B']:6.3f}/"
          f"{r['json']['max_C_0_spread_bound_B']:6.3f}  omega {r['mine']['max_omega_spread']:7.3f}/"
          f"{r['json']['max_omega_spread']:7.3f}   maxdiff {r['max_abs_diff']:.1e}")
print(f"   theorem form n^(8w+1) omega spread at 571: mine "
      f"{out['theorem_form_omega_spread_571']['mine']:.4f}, json "
      f"{out['theorem_form_omega_spread_571']['json']:.4f}")

json.dump(out, open("own_n4.json", "w"), indent=1, default=str)
print("\nwrote own_n4.json")
