#!/usr/bin/env python3
"""Print the blind re-derivation (rederive_out.json) as plain tables."""
import json
import sys

res = json.load(open(sys.argv[1]))
f = lambda x, n=4: "-" if x is None else f"{x:.{n}f}"
ci = lambda c, n=4: "-" if c is None else f"[{c[0]:.{n}f}, {c[1]:.{n}f}]"
for s, d in res.items():
    print(f"== {s} {d['curve']['slug']} log2r={d['curve']['log2_r']:.2f} records={d['n_records']} "
          f"status={d['status_counts']} warmups={d['warmups']} S=tot/sqrt(r):{d['s_equals_total_over_sqrt_r']}")
    print("  table: arm | verified/runs | mean S | 95% cluster CI | S/ref | levels")
    for a, t in d["table"].items():
        print(f"    {a:15s} {t['verified']}/{t['runs']} {f(t['mean_s'],3):>9s} {ci(t['ci95'],3):>20s} "
              f"{f(t['s_over_ref'],3):>8s} {t['levels']}")
    print("  compare (B over A): ratio | ecbench-method CI | np target-cluster CI | pairs/workloads/unpaired/same_seeds")
    for k, c in d["compare"].items():
        print(f"    {k:24s} {f(c['ratio'])} {ci(c['ci95_ecbench_method'] if 'ci95_ecbench_method' in c else c['ci95'])} "
              f"np {ci(c['np_cluster_boot']['ci95'])} {c['pairs']}/{c['workloads']}/{c['unpaired']}/{c['same_seeds']} {c['ci_method']}")
    print("  band mean S at w=0,0.1,1 | mean unpriced ops/run")
    for a, b in d["band"].items():
        print(f"    {a:15s} " + " ".join(f(x, 3) for x in b["mean_s"]) + f"  U={b['mean_unpriced_ops']:.1f} unc={b['uncounted']}")
    print("  band ratios alt/plan per weight: ratio [ecbench-method CI] class | np CI class ; label ; order holds")
    for b, br in d["band_ratios"].items():
        if b == "plan_over_rho":
            print("    plan/rho  " + " | ".join(f"w={p['w']}: {f(p['ratio'])} {ci(p['ci95_ecbench_method'])}" for p in br))
            continue
        print(f"    {b:15s} " + " | ".join(
            f"w={p['w']}: {f(p['ratio'])} {ci(p['ci95_ecbench_method'])} {p['class']}/{p['class_np']}" for p in br["per_weight"])
              + f" ; {br['protocol_label']} ; order_holds={br['band_order_holds']}")
    print("  determinism", d["determinism"])
    print("  P1", d["P1"], "P4", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d["P4"].items()})
