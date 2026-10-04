#!/usr/bin/env python3
"""N2(2): the one convention asymmetry I find -- vOW's (time, memory) pair is
chosen from its own parallelism curve under each metric, while the Nagao side is
evaluated at its single modelled point.  Measure the size and the SIGN of that
asymmetry per metric, so the round knows whether it could manufacture a flag.

Counterfactual, mine: Nagao's decompose step is #Fb independent decomposition
attempts, so M solvers each with their own degree-4 working set give
time' = time / M and memory' = M * memory.  Then
  time_only:            total sequential work, invariant in M      -> 0 bits
  time_memory_product:  (time/M) * (M*mem) = time*mem, invariant   -> 0 bits
  equal_rate_max:       min_M max(time/M, M*mem) = sqrt(time*mem)
                        = (log2 time + log2 mem)/2
"""
import json
from math import log2

RUN = "/workspace/experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/cost-surface.json"
d = json.load(open(RUN))
worst = {}
flips = {"equal_rate_max": [], "time_memory_product": [], "time_only": []}
for c in d["cells"]:
    time = c["time_log2_total"]
    for memr, t5 in [("frozen_width_C_N_plus_4_4", c["T5_memory_log2_frozen_width"]),
                     ("dense_width_squared", c["T5_memory_log2_dense_width_squared"])]:
        for metric in ["time_only", "time_memory_product", "area_time_AT", "equal_rate_max"]:
            mg = c["margins"][f"{metric}|{memr}"]
            if metric == "time_only":
                nag_par = time
            elif metric in ("time_memory_product", "area_time_AT"):
                nag_par = time + t5
            else:
                nag_par = (time + t5) / 2.0 if t5 < time else max(time, t5)
            delta = nag_par - mg["nagao_metric_log2"]
            k = (metric, memr)
            if k not in worst or abs(delta) > abs(worst[k][0]):
                worst[k] = (delta, c["n"], c["omega"], c["C_0"], c["monomial_count_reading"])
            ahead_now = mg["margin_bits_nagao_minus_vow"] < 0
            ahead_par = (nag_par - mg["vow_pareto_minimum_log2"]) < 0
            if ahead_now != ahead_par:
                flips.setdefault(metric, []).append(
                    (c["n"], c["omega"], c["C_0"], memr, ahead_now, ahead_par))

print("largest |shift| in the Nagao charge if the Nagao side were given the same")
print("parallelism treatment as vOW (negative = Nagao would be charged LESS):")
for (metric, memr), (dl, n, om, c0, rd) in sorted(worst.items()):
    print(f"  {metric:<20} {memr:<28} {dl:+9.3f} bits  at n={n}, omega={om}, C_0={c0}")
print("\ncells whose nagao_ahead flag would FLIP under that treatment, by metric:")
for metric, lst in flips.items():
    on = sum(1 for x in lst if not x[4] and x[5])
    off = sum(1 for x in lst if x[4] and not x[5])
    print(f"  {metric:<20} flips ON (new flags): {on:>4}   flips OFF (lost flags): {off:>4}")
# representative cell, worked
for c in d["cells"]:
    if c["n"] == 571 and abs(c["omega"] - 2.807) < 1e-9 and c["C_0"] == 8 \
            and c["monomial_count_reading"] == "binomial_C_N_plus_d_choose_d":
        t, m5 = c["time_log2_total"], c["T5_memory_log2_frozen_width"]
        mg = c["margins"]["equal_rate_max|frozen_width_C_N_plus_4_4"]
        print(f"\nworked cell n=571, omega=2.807, C_0=8, binomial, frozen width:")
        print(f"  as charged:      equal_rate Nagao = max(time, T5) = {mg['nagao_metric_log2']:.3f}"
              f"   vOW = {mg['vow_pareto_minimum_log2']:.3f}   margin {mg['margin_bits_nagao_minus_vow']:+.3f}")
        print(f"  same treatment:  equal_rate Nagao = (time+T5)/2   = {(t + m5) / 2:.3f}"
              f"   vOW = {mg['vow_pareto_minimum_log2']:.3f}   margin "
              f"{(t + m5) / 2 - mg['vow_pareto_minimum_log2']:+.3f}")
        print(f"  asymmetry worth {(t + m5) / 2 - mg['nagao_metric_log2']:+.3f} bits, "
              f"and it runs AGAINST Nagao as charged")
