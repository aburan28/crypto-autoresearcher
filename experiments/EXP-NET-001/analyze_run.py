#!/usr/bin/env python3
"""analyze_run.py — canonical analysis pass over runs/RUN-NET-001-a/raw.json (EXP-NET-001).
Computes the tables cited in analysis.md: ratio-of-total enrichments, tautology
decomposition, k-yield rates main vs permuted control, charged-op/exponent tables.
Pure stdlib; deterministic; reads only raw.json, prints tables to stdout."""
import json, math, sys

d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else
                  "experiments/EXP-NET-001/runs/RUN-NET-001-a/raw.json"))

insts = [i for i in d["instances"] if i.get("status") == "ok"]

def f(x):
    return "%.4f" % x if x is not None else "  -- "

print("=== per-instance core table ===")
print("p    seed       n     B   S2cols  exp_tot  enr_tot  Qcols  univ  yld  yld_perm meanS   first_yld")
for i in insts:
    exp_tot = sum(i["s2"]["expected"].values())
    obs_tot = sum(i["s2"]["by_fampair"].values())
    ka = i["k_analysis_s2"]
    nc2 = i["nc2"]
    print("%-4d %-10d %-5d %-3d %-7d %-8.2f %-8.4f %-6d %-5d %-4d %-8s %-7s %s" % (
        i["p"], i["seed"], i["curve"]["n"], i["B"], obs_tot, exp_tot,
        obs_tot / exp_tot if exp_tot else float("nan"),
        ka["total_q_collisions"], ka["universal"], ka["yielding"],
        str(nc2.get("permuted_yielding")), f(ka["mean_S"]), ka["first_yielding_rank"]))

print("\n=== per-size ratio-of-totals (S2) ===")
for p in (101, 431, 1601):
    sub = [i for i in insts if i["p"] == p]
    obs = sum(sum(i["s2"]["by_fampair"].values()) for i in sub)
    exp = sum(sum(i["s2"]["expected"].values()) for i in sub)
    # tautology split: universal collisions (k-independent) from k-analysis
    univ = sum(i["k_analysis_s2"]["universal"] for i in sub)
    yld = sum(i["k_analysis_s2"]["yielding"] for i in sub)
    ana = sum(i["k_analysis_s2"]["analyzed"] for i in sub)
    qtot = sum(i["k_analysis_s2"]["total_q_collisions"] for i in sub)
    yldp = sum(i["nc2"].get("permuted_yielding", 0) for i in sub)
    anap = sum(i["nc2"].get("permuted_analyzed", 0) for i in sub)
    ns = [i["curve"]["n"] for i in sub]
    print("p=%-4d obs=%-6d exp=%-8.1f enr=%.4f | Qcols=%-6d analyzed=%-5d univ=%-4d yld=%-4d (%.3f/analyzed) | permuted yld=%-4d (%.3f/analyzed) | n range %d..%d" % (
        p, obs, exp, obs/exp, qtot, ana, univ, yld, yld/ana, yldp, yldp/anap if anap else float("nan"), min(ns), max(ns)))

print("\n=== per-family-pair enrichment, totals over all 18 instances ===")
keys = ["PPPP", "PPQQ", "PPPQ", "QQQQ", "PQQQ", "PQPQ"]
for k in keys:
    obs = sum(i["s2"]["by_fampair"].get(k, 0) for i in insts)
    exp = sum(i["s2"]["expected"].get(k, 0.0) for i in insts)
    print("%-5s obs=%-6d exp=%-9.2f enr=%.4f" % (k, obs, exp, obs/exp))

print("\n=== large-n subset (n >= 400) ratio-of-totals ===")
sub = [i for i in insts if i["curve"]["n"] >= 400]
obs = sum(sum(i["s2"]["by_fampair"].values()) for i in sub)
exp = sum(sum(i["s2"]["expected"].values()) for i in sub)
print("instances: %s" % [(i["p"], i["curve"]["n"]) for i in sub])
print("obs=%d exp=%.1f enr=%.4f" % (obs, exp, obs/exp))

print("\n=== charged-op / exponent table (S2 scope) ===")
print("p    n     B  ops_fb+enum  ops_pre    per_col  ops_opt    ops_full   bsgs  exp_opt exp_full bsgs_exp ops_opt/bsgs")
for i in insts:
    r = i["recovery"]
    oa = i["op_accounting"]
    if not r:
        continue
    base = oa["ops_fb"] + oa["ops_enum_s2"]
    print("%-4d %-5d %-3d %-12d %-10d %-8d %-10d %-10d %-6d %-8.4f %-8.4f %-8.4f %.1f" % (
        i["p"], i["curve"]["n"], i["B"], base, oa["ops_pre"], oa["ops_verify_per_collision"],
        r["ops_recovery_optimistic"], r["ops_recovery_fullscan"], r["bsgs_ops"],
        r["exponent_optimistic"], r["exponent_fullscan"], r["bsgs_exponent"],
        r["ops_recovery_optimistic"] / r["bsgs_ops"]))

print("\n=== NC1 independent-curve enrichments (per instance) ===")
for i in insts:
    if i["nc1"]:
        print("p=%-4d seed=%d singles: %d/%.2f (%.3f)  products: %d/%.2f (%.3f)" % (
            i["p"], i["seed"], i["nc1"]["singles_cross"], i["nc1"]["singles_expected"], i["nc1"]["singles_enrichment"],
            i["nc1"]["products_cross"], i["nc1"]["products_expected"], i["nc1"]["products_enrichment"]))

print("\n=== NC2 permuted-target, Q-involving collision counts main vs permuted ===")
for i in insts:
    nc2 = i["nc2"]
    print("p=%-4d seed=%d main=%-6d permuted=%-6d ratio=%s" % (
        i["p"], i["seed"], nc2["qinvolving_collisions_main"], nc2["qinvolving_collisions_permuted"], f(nc2.get("ratio"))))

print("\n=== NC3 random-oracle enrichment totals ===")
for p in (101, 431, 1601):
    sub = [i for i in insts if i["p"] == p]
    obs = sum(sum(i["nc3"]["by_fampair"].values()) for i in sub)
    exp = sum(sum(i["s2"]["expected"].values()) for i in sub)
    print("p=%-4d obs=%-6d exp=%-8.1f enr=%.4f" % (p, obs, exp, obs/exp))

print("\n=== S1 (single-term scope) totals ===")
for p in (101, 431, 1601):
    sub = [i for i in insts if i["p"] == p]
    obs = sum(sum(i["s1"]["by_fampair"].values()) for i in sub)
    exp = sum(sum(i["s1"]["expected"].values()) for i in sub)
    yld1 = sum(i["k_analysis_s1"]["yielding"] for i in sub if i["k_analysis_s1"])
    print("p=%-4d obs=%-4d exp=%-6.2f enr=%s yielding_S1=%d" % (p, obs, exp, f(obs/exp if exp else None), yld1))
