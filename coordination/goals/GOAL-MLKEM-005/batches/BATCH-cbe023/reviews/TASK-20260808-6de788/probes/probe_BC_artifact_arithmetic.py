#!/usr/bin/env python3
"""RED-TEAM PROBES, NOT PRE-REGISTERED.  TASK-20260808-6de788.

Four probes, all of which read ONLY the committed BATCH-cbe023 producer
artifacts and recompute from the numbers already in them.  No producer
artifact is modified, no frozen verdict is rescored, and nothing here is a new
measurement of any lattice, frame or draw.  Claim tier TOY.

  B-1  independent recomputation of c_min and n_fire(c = 6) from the committed
       per-step quantities, and the identity c_min - c_pos = 1 + t_crit *
       SE_step / SE_diff at every step with Delta <= 0.
  B-2  NULL-STEP CONTROL: keep SE_step(i) and SE_diff(t_i) exactly, set
       Delta_i := 0 (an exact null step -- no descent and no increase), and
       recompute n_fire.  This is the null object Section B does not carry.
  C-1  split Section C's null firing rate into its two frozen conditions, from
       the per-replicate |t|, nu_eff and relative difference recorded in
       results_am7.json.
  C-2  SE_2way vs the plain sample SE of the same S x E table, per target;
       and the SE-irrelevance probe on the frozen verdict.
"""
import json
import os

import numpy as np
from scipy.stats import t as tdist

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "tasks"))
G3 = os.path.join(TASKS, "TASK-20260808-cece0c", "results_g3.json")
AM7 = os.path.join(TASKS, "TASK-20260808-3a5f18", "results_am7.json")
TCRIT = 4.2071245566046755
ALPHA_PAIR = 0.10 / 11
TAU_REL = 0.15

g3 = json.load(open(G3))
am7 = json.load(open(AM7))

print("=" * 78)
print("B-1  recomputation of c_min / n_fire(c=6) from the committed per-step data")
print("=" * 78)
pool = [0, 0]
for cell, cd in g3["cells"].items():
    cm = [1 + (TCRIT * s["se_step_paired"] - s["delta"]) / s["se_diff_at_t_lo"]
          for s in cd["steps"]]
    dev = max(abs(a - s["c_min"]) for a, s in zip(cm, cd["steps"]))
    n6 = sum(1 for c in cm if c <= 6)
    n6e = sum(1 for c, s in zip(cm, cd["steps"])
              if c <= 6 and not s["flag_delta_gt_0_in_raw_data"])
    pool[0] += n6
    pool[1] += n6e
    print("  %-10s n_fire(6)=%d  excluding-already-increasing=%d  "
          "max|c_min recomputed - c_min committed| = %.2e"
          % (cell, n6, n6e, dev))
print("  pooled %d of 48 (excluding already-increasing: %d)" % tuple(pool))
bad = tot = 0
for cd in g3["cells"].values():
    for s in cd["steps"]:
        if s["delta"] <= 0:
            tot += 1
            ident = 1 + TCRIT * s["se_step_paired"] / s["se_diff_at_t_lo"]
            bad += abs(ident - s["c_min_minus_c_pos"]) > 1e-9
print("  identity c_min - c_pos == 1 + t_crit*SE_step/SE_diff : fails at %d of "
      "%d steps with Delta <= 0" % (bad, tot))

print()
print("=" * 78)
print("B-2  NULL-STEP CONTROL -- same SEs, Delta_i := 0 (exact null step)")
print("=" * 78)
print("  %-10s %10s %10s %10s %10s" % ("cell", "n6 real", "n6 NULL",
                                       "n4 real", "n4 NULL"))
tot4 = [0, 0, 0, 0]
allnull = []
for cell, cd in g3["cells"].items():
    cr = [s["c_min"] for s in cd["steps"]]
    cn = [1 + TCRIT * s["se_step_paired"] / s["se_diff_at_t_lo"]
          for s in cd["steps"]]
    allnull += cn
    row = [sum(1 for c in cr if c <= 6), sum(1 for c in cn if c <= 6),
           sum(1 for c in cr if c <= 4), sum(1 for c in cn if c <= 4)]
    tot4 = [a + b for a, b in zip(tot4, row)]
    print("  %-10s %10d %10d %10d %10d" % (cell, *row))
print("  %-10s %10d %10d %10d %10d" % ("POOLED/48", *tot4))
print("  c_min on an EXACT-NULL step: min %.3f median %.3f max %.3f"
      % (min(allnull), float(np.median(allnull)), max(allnull)))

print()
print("=" * 78)
print("C-1  Section C null rate split into its two frozen conditions")
print("=" * 78)
print("  %-16s %5s %10s %10s %6s %9s %9s"
      % ("unit", "R", "cond(i)", "cond(ii)", "both", "med tcrit", "p95 rel"))
for k, u in am7["nulls"].items():
    reps = u["replicates"]
    at = np.array([r["abs_t"] for r in reps])
    nu = np.array([r["nu_eff"] for r in reps])
    rel = np.array([r["relative_difference"] for r in reps])
    tc = tdist.ppf(1 - ALPHA_PAIR / 2, nu)
    c1, c2 = at > tc, rel > TAU_REL
    print("  %-16s %5d %10s %10s %6d %9.2f %9.4f"
          % (k, u["R_realized"], "%d (%.4f)" % (c1.sum(), c1.mean()),
             "%d (%.4f)" % (c2.sum(), c2.mean()), (c1 & c2).sum(),
             float(np.median(tc)), float(np.percentile(rel, 95))))

print()
print("=" * 78)
print("C-2  SE_2way vs the plain sample SE of the same S x E table")
print("=" * 78)
print("  %-9s %-16s %9s %9s %6s %7s %8s %8s %7s"
      % ("cell", "target", "SE_2way", "SE_naive", "ratio", "nu_eff",
         "tcrit", "tcrit31", "rel%"))
maxrel = 0.0
for tg in am7["targets"]:
    D = np.array(tg["Delta_table_S_by_E"], dtype=float)
    sc = tg["scoring"]
    sen = D.std(ddof=1) / np.sqrt(D.size)
    rel = abs(sc["Delta_bar"]) / sc["denominator_M_max_abs_D"]
    maxrel = max(maxrel, rel)
    print("  %-9s %-16s %.3e %.3e %6.2f %7.2f %8.3f %8.3f %7.2f"
          % (tg["cell"], tg["target"], sc["SE_Delta_bar"], sen,
             sc["SE_Delta_bar"] / sen, sc["nu_eff"], sc["t_crit"],
             tdist.ppf(1 - ALPHA_PAIR / 2, 31), 100 * rel))
print("  max relative difference over the 10 targets = %.4f  vs tau_rel = %.2f"
      % (maxrel, TAU_REL))
print("  -> frozen condition (ii) fails at EVERY target for ANY value of the "
      "SE, including SE = 0:")
print("     the CONSISTENT verdict is invariant to the entire AM-7 SE rebuild.")
