#!/usr/bin/env python3
"""
Joint J1 (c): recompute the S2 gate table arithmetic from
RUN-ECDLP-56ee42-S2/raw-result.json ONLY (no other input needed; this is not
a blind re-derivation, it is an arithmetic recomputation from the archived
raw numbers, per the attack_plan: "Recompute all six T4 survival ratios and
the POS-A/POS-B gate quantities from the S2 raw JSON; any mismatch is a
break.").
"""
import json
import math

with open(
    "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-56ee42/"
    "implementation/runs/RUN-ECDLP-56ee42-S2/raw-result.json"
) as f:
    s2 = json.load(f)

print("=== (c) POS-A recompute ===")
two_over_pi = 2.0 / math.pi
posA_max_diff = 0.0
for row in s2["steps"]["POS-A"]["results"]:
    diff = abs(row["A"] - two_over_pi)
    ok = math.isclose(diff, row["abs_diff_2pi"], rel_tol=1e-9, abs_tol=1e-18)
    posA_max_diff = max(posA_max_diff, diff)
    print(f"  T{row['T']}: A={row['A']!r}  recomputed|A-2/pi|={diff!r}  "
          f"recorded={row['abs_diff_2pi']!r}  match={ok}")
recorded_max = s2["steps"]["POS-A"]["max_abs_diff_2pi"]
print(f"  recomputed max_abs_diff_2pi = {posA_max_diff!r}, recorded = {recorded_max!r}, "
      f"match={math.isclose(posA_max_diff, recorded_max, rel_tol=1e-9)}")
gate_pass_recomputed = posA_max_diff <= 0.005
print(f"  gate (<=0.005): recomputed={gate_pass_recomputed}, recorded={s2['steps']['POS-A']['gate_pass']}")

print()
print("=== (c) POS-B beta recompute (log-log least squares of A vs n) ===")
rows = s2["steps"]["POS-B"]["results"]
xs = [math.log(r["n"]) for r in rows]
ys = [math.log(r["A"]) for r in rows]
n = len(xs)
mean_x = sum(xs) / n
mean_y = sum(ys) / n
cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
var = sum((x - mean_x) ** 2 for x in xs)
slope = cov / var
beta_recomputed = -slope
recorded_beta = s2["steps"]["POS-B"]["fitted_beta"]
print(f"  recomputed beta (OLS on ln A vs ln n) = {beta_recomputed!r}")
print(f"  recorded fitted_beta                  = {recorded_beta!r}")
print(f"  relative difference = {abs(beta_recomputed-recorded_beta)/recorded_beta:.4%}")
print(f"  both in [0.10, 0.35]: recomputed={0.10 <= beta_recomputed <= 0.35}, "
      f"recorded={0.10 <= recorded_beta <= 0.35}")

print()
print("=== (c) CONTROL-C survival ratio recompute ===")
dec_quoted_ratios = [0.785, 0.934, 0.828, 0.780, 0.855, 0.813]
all_ratios = []
for i, row in enumerate(s2["steps"]["CONTROL-C"]["results"]):
    pre = row["A_noDC_pre_shuffle"]
    postmax_recomputed = max(row["A_noDC_post_shuffle_all"])
    postmax_recorded = row["A_noDC_post_shuffle_max"]
    ratio = postmax_recomputed / pre
    excess_removed_recomputed = pre - postmax_recomputed
    excess_removed_recorded = row["excess_removed"]
    all_ratios.append(ratio)
    match_postmax = math.isclose(postmax_recomputed, postmax_recorded, rel_tol=1e-12)
    match_excess = math.isclose(excess_removed_recomputed, excess_removed_recorded, rel_tol=1e-9)
    dec_ratio = dec_quoted_ratios[i]
    match_dec = math.isclose(ratio, dec_ratio, abs_tol=5e-4)
    print(f"  T{row['T']}: pre={pre!r} postmax(recomputed from all[])={postmax_recomputed!r} "
          f"postmax(recorded field)={postmax_recorded!r} match={match_postmax}")
    print(f"        ratio(recomputed)={ratio:.6f}  DEC-quoted={dec_ratio}  match(~3dp)={match_dec}")
    print(f"        excess_removed recomputed={excess_removed_recomputed!r} recorded={excess_removed_recorded!r} "
          f"match={match_excess}")
    gate_this_row = ratio <= 0.5
    print(f"        gate (ratio<=0.5) this row: {gate_this_row}")

overall_gate_recomputed = all(r <= 0.5 for r in all_ratios)
print(f"  overall CONTROL-C gate_pass recomputed = {overall_gate_recomputed}, "
      f"recorded = {s2['steps']['CONTROL-C']['gate_pass']}")

print()
print("=== (c) top-level gates dict cross-check ===")
print(f"  recorded gates block: {s2['gates']}")
print(f"  POS-A matches steps.POS-A.gate_pass: {s2['gates']['POS-A'] == s2['steps']['POS-A']['gate_pass']}")
print(f"  POS-B matches steps.POS-B.gate_pass: {s2['gates']['POS-B'] == s2['steps']['POS-B']['gate_pass']}")
print(f"  CONTROL-C matches steps.CONTROL-C.gate_pass: "
      f"{s2['gates']['CONTROL-C'] == s2['steps']['CONTROL-C']['gate_pass']}")
static_all_pass = s2["steps"]["static_provenance_check"]["all_pass"]
print(f"  static_provenance matches steps.static_provenance_check.all_pass: "
      f"{s2['gates']['static_provenance'] == static_all_pass}")
