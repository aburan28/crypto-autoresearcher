#!/usr/bin/env python3
"""N4(4) proper: the crossover surface -- reproduce crossover_n by my own
bisection, find the cells the JSON flags `monotone_for_200_beyond: false`, and
recompute the margin at n and n + 200 there.  Also reproduce the crossover
RANGES the task-report tabulates."""
import json
from math import ceil, exp, lgamma, log, log2
import math

RUN = "/workspace/experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/"
_d = {}


def deficit(c0):
    if c0 in _d:
        return _d[c0]
    t = 2 ** c0
    if t > 131072:
        _d[c0] = 1.0 / (2 * t * log(2))
        return _d[c0]
    p0 = exp(-t * log(2))
    acc = sum(exp(lgamma(t + 1) - lgamma(j + 1) - lgamma(t - j + 1) - t * log(2)) * log2(2 * j)
              for j in range(1, t + 1))
    _d[c0] = c0 - acc / (1 - p0)
    return _d[c0]


def lchoose2(a, b):
    return (lgamma(a + 1) - lgamma(b + 1) - lgamma(a - b + 1)) / log(2)


def log2W(n):
    return log2(0.886) + n / 2.0


def vow(n, metric):
    if metric == "time_only":
        return log2W(n)
    if metric == "equal_rate_max":
        return 0.5 * (log2(6.0 * n) + log2W(n))
    return log2(6.0 * n) + log2W(n)


def margin(n, omega, c0, reading, metric, memr, d_F=4):
    m = ceil(n / c0)
    N = n * (m - 1)
    t1 = d_F * log2(N) if reading == "nagao_loose_N_to_the_d" else lchoose2(N + d_F, d_F)
    t3 = log2(m * 2 ** c0 + 1)
    log2lam = m * c0 - n - m * deficit(c0)
    lam = 2.0 ** log2lam if log2lam < 500 else float("inf")
    t4 = 0.0 if lam == float("inf") else -log2(-math.expm1(-lam))
    t5 = lchoose2(N + 4, 4) * (1 if memr == "frozen_width_C_N_plus_4_4" else 2)
    t6 = omega * t3
    dec = omega * t1 + t3 + t4
    time = dec + log2(1 + 2 ** (t6 - dec)) if t6 - dec > -1000 else dec
    nag = {"time_only": time, "time_memory_product": time + t5,
           "area_time_AT": time + t5, "equal_rate_max": max(time, t5)}[metric]
    return nag - vow(n, metric)


cs = json.load(open(RUN + "cost-surface.json"))
surf = cs["crossover_surface"]
out = {}

# ---- reproduce crossover_n by my own scan over the same search window --------
def my_crossover(e, lo=16, hi=2000):
    prev = None
    for n in range(lo, hi + 1):
        s = margin(n, e["omega"], e["C_0"], e["monomial_count_reading"],
                   e["metric"], e["memory_reading"]) < 0
        if prev is False and s:
            return n
        prev = s
    return None


import random
random.seed(7)
sample = random.sample(range(len(surf)), 24)
rows, bad = [], []
for i in sample:
    e = surf[i]
    mine = my_crossover(e)
    rows.append(dict(omega=e["omega"], C_0=e["C_0"], reading=e["monomial_count_reading"],
                     metric=e["metric"], memory_reading=e["memory_reading"],
                     json=e["crossover_n"], mine=mine, match=(mine == e["crossover_n"])))
    if mine != e["crossover_n"]:
        bad.append(rows[-1])
out["crossover_sample_24"] = rows
print(f"(4a) 24 random crossover_surface entries, my own first-sign-change scan over [16, 2000]:")
print(f"     matches: {sum(r['match'] for r in rows)}/24; mismatches: {bad}")

# ---- the monotonicity flag --------------------------------------------------
nm = [e for e in surf if e.get("monotone_for_200_beyond") is False]
out["entries_flagged_non_monotone"] = len(nm)
out["entries_total"] = len(surf)
out["null_crossovers"] = [e for e in surf if e["crossover_n"] is None]
print(f"\n(4b) crossover_surface: {len(surf)} entries; "
      f"`monotone_for_200_beyond: false` at {len(nm)}; null crossovers: {len(out['null_crossovers'])}")
byc0 = {}
for e in nm:
    byc0.setdefault(e["C_0"], 0)
    byc0[e["C_0"]] += 1
print(f"     non-monotone entries by C_0: {byc0}")
out["non_monotone_by_C0"] = byc0

checks = []
for e in nm[:6] + [e for e in nm if e["C_0"] == 3][:4]:
    n0 = e["crossover_n"]
    if n0 is None:
        continue
    pts = {d: margin(n0 + d, e["omega"], e["C_0"], e["monomial_count_reading"],
                     e["metric"], e["memory_reading"]) for d in (0, 50, 100, 150, 200)}
    reverts = [d for d, v in pts.items() if v >= 0 and d > 0]
    checks.append(dict(omega=e["omega"], C_0=e["C_0"], reading=e["monomial_count_reading"],
                       metric=e["metric"], memory_reading=e["memory_reading"],
                       crossover_n=n0, margins=pts,
                       margin_becomes_positive_again_within_200=bool(reverts),
                       at_offsets=reverts))
out["non_monotone_cell_checks"] = checks
print("\n(4c) my recomputed margins at n, n+50, ..., n+200 for cells the JSON flags non-monotone:")
for c in checks:
    print(f"     omega={c['omega']} C_0={c['C_0']} {c['metric']}|{c['memory_reading']} "
          f"[{c['reading'][:8]}] crossover {c['crossover_n']}: "
          + " ".join(f"{d}:{v:+.2f}" for d, v in c["margins"].items())
          + f"   reverts: {c['margin_becomes_positive_again_within_200']} {c['at_offsets']}")

# ---- the crossover RANGES the task-report tabulates -------------------------
COMMITTED = {2.376, 2.807, 3.0}
ranges = {}
for metric, memr, reading, label in [
        ("time_only", "frozen_width_C_N_plus_4_4", "binomial_C_N_plus_d_choose_d", "time_only|binomial"),
        ("time_only", "frozen_width_C_N_plus_4_4", "nagao_loose_N_to_the_d", "time_only|loose"),
        ("time_memory_product", "frozen_width_C_N_plus_4_4", "binomial_C_N_plus_d_choose_d", "TxM|binomial|frozen"),
        ("time_memory_product", "dense_width_squared", "binomial_C_N_plus_d_choose_d", "TxM|binomial|dense"),
        ("time_memory_product", "frozen_width_C_N_plus_4_4", "nagao_loose_N_to_the_d", "TxM|loose|frozen"),
        ("time_memory_product", "dense_width_squared", "nagao_loose_N_to_the_d", "TxM|loose|dense"),
        ("equal_rate_max", "frozen_width_C_N_plus_4_4", "binomial_C_N_plus_d_choose_d", "ER|binomial"),
        ("equal_rate_max", "frozen_width_C_N_plus_4_4", "nagao_loose_N_to_the_d", "ER|loose")]:
    es = [e for e in surf if e["metric"] == metric and e["memory_reading"] == memr
          and e["monomial_count_reading"] == reading and round(e["omega"], 3) in COMMITTED]
    xs = [e["crossover_n"] for e in es if e["crossover_n"] is not None]
    bb = [e["crossover_n"] for e in es
          if e["crossover_n"] is not None and e["C_0_satisfies_ARM_C_bound_B_at_crossover"]]
    ranges[label] = {"cells": len(es), "all_C_0": [min(xs), max(xs)],
                     "bound_B_only": [min(bb), max(bb)] if bb else None}
    print(f"(4d) {label:<22} {len(es):>2} cells  all C_0: {min(xs)}-{max(xs)}   "
          f"bound-B C_0: {min(bb) if bb else None}-{max(bb) if bb else None}")
out["crossover_ranges"] = ranges

json.dump(out, open("own_n4b.json", "w"), indent=1, default=str)
print("\nwrote own_n4b.json")
