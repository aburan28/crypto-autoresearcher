#!/usr/bin/env python3
"""Summaries, frozen criteria and graph for EXP-ECDLP-20a588 (recorded values only).

Usage: analyze.py OUT_DIR RUN_DIR [RUN_DIR ...]   (runs cover disjoint cells; see the amendments)
"""
import json, os, statistics, sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

out, run_dirs = sys.argv[1], sys.argv[2:]
os.makedirs(out, exist_ok=True)
rows = []
for d in run_dirs:
    for l in open(os.path.join(d, "raw-result.jsonl")):
        r = json.loads(l)
        r["run_id"] = os.path.basename(os.path.normpath(d))
        rows.append(r)
M = rows[0]["m"]
EXP = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(run_dirs[0]))))
RUNS = ", ".join(sorted({r["run_id"] for r in rows}))
# Several runs may cover the same (L, instance) with DIFFERENT arms (amendments re-run arms after an instrument
# failure). Merge per arm; a later run's result for an arm replaces an earlier run's (EXP-ECDLP-8c41d7 AMD-03:
# RUN-03's crashed msolve rows are replaced by RUN-04's). Each result records its source run and prime size.
merged = {}
for r in sorted(rows, key=lambda r: r["run_id"]):
    cell = merged.setdefault((r["L"], r["inst"]), dict(r, results={}))
    for arm, v in r["results"].items():
        cell["results"][arm] = dict(v, p_bits=r["p_bits"], p=r["p"], src=r["run_id"])
rows = [merged[k] for k in sorted(merged)]
ARMS = ["A_elim_ms", "A_drl_ms", "B_ms", "A_block_sg", "B_sg"]

cells = defaultdict(list)
elim_eq = defaultdict(list)
for r in rows:
    for k, v in r["results"].items():
        cells[(r["L"], k)].append(dict(v, kind=r["kind"]))
    if "elim_equals_B" in r:
        elim_eq[r["L"]].append(r["elim_equals_B"])

summary = []
for (L, k), vs in sorted(cells.items()):
    ok = [v for v in vs if v["status"] == "ok"]
    rec = dict(L=L, arm=k, p_bits=sorted({v["p_bits"] for v in vs}), runs=sorted({v["src"] for v in vs}), n=len(vs), n_ok=len(ok),
               n_timeout=sum(v["status"] == "timeout" for v in vs),
               n_degenerate=sum(v["status"] == "degenerate_target" for v in vs),
               n_other=sum(v["status"] not in ("ok", "timeout", "degenerate_target") for v in vs))
    if ok:
        w = [1000 * v["wall_s"] for v in ok]
        rec.update(median_ms=statistics.median(w), min_ms=min(w), max_ms=max(w),
                   planted_checked=sum("planted_in_variety" in v for v in ok),
                   planted_ok=sum(v.get("planted_in_variety") is True for v in ok))
        if any("f4_max_deg" in v for v in ok):
            rec["max_f4_deg"] = max(v.get("f4_max_deg", 0) for v in ok)
        if any("std_ms" in v for v in ok):
            rec["median_std_ms"] = statistics.median(v["std_ms"] for v in ok)
    summary.append(rec)
json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)

by = {(s["L"], s["arm"]): s for s in summary}
def criteria(a, b):
    joint = sorted(L for (L, k) in by if k == a and "median_ms" in by[(L, k)] and "median_ms" in by.get((L, b), {}))
    faster = [L for L in joint if by[(L, a)]["median_ms"] < by[(L, b)]["median_ms"]]
    def last_ok(arm):
        Ls = [L for (L, k), s in by.items() if k == arm and s["n_ok"] > 0]
        return max(Ls) if Ls else None
    def retired(arm):
        Ls = [L for (L, k), s in by.items() if k == arm and s["n_ok"] == 0 and s["n_timeout"]]
        return min(Ls) if Ls else None
    return dict(jointly_completed_L=joint, a_faster=len(faster),
                ratio=({f"L{L}": round(by[(L, a)]["median_ms"] / by[(L, b)]["median_ms"], 2) for L in joint}),
                largest_L=dict([(a, last_ok(a)), (b, last_ok(b))]), retired_at=dict([(a, retired(a)), (b, retired(b))]))
crit = {"msolve A_elim vs B": criteria("A_elim_ms", "B_ms"),
        "Singular A_block vs B": criteria("A_block_sg", "B_sg"),
        "dynamic range A_drl vs A_elim (msolve)": criteria("A_drl_ms", "A_elim_ms"),
        "elim_equals_B": {f"L{L}": f"{sum(v)}/{len(v)}" for L, v in sorted(elim_eq.items())}}
json.dump(crit, open(os.path.join(out, "criteria.json"), "w"), indent=1)


# ---- supplementary (not a frozen criterion): paired per-instance ratios with a bootstrap interval.
# The chain and dense arms run on the SAME instance, so the ratio chain/dense is paired; with n = 4..6 per cell the
# interval is wide and is reported as such. Deterministic seed; 4000 resamples of the paired ratios; percentile 95%.
import random
def paired(a, b):
    by_inst = defaultdict(dict)
    for r in rows:
        for arm in (a, b):
            v = r["results"].get(arm, {})
            if v.get("status") == "ok":
                by_inst[(r["L"], r["inst"])][arm] = v["wall_s"]
    res = defaultdict(list)
    for (L, inst), d in by_inst.items():
        if a in d and b in d and d[b] > 0:
            res[L].append(d[a] / d[b])
    out_ = {}
    for L, xs in sorted(res.items()):
        rng = random.Random(f"{a}-{b}-{L}")
        meds = sorted(statistics.median(rng.choices(xs, k=len(xs))) for _ in range(4000))
        out_[f"L{L}"] = dict(n=len(xs), median_ratio=round(statistics.median(xs), 3),
                             ci95=[round(meds[int(0.025 * len(meds))], 3), round(meds[int(0.975 * len(meds)) - 1], 3)])
    return out_
crit["paired_ratio_ms_A_elim_over_B"] = paired("A_elim_ms", "B_ms")
crit["paired_ratio_sg_A_block_over_B"] = paired("A_block_sg", "B_sg")
crit["paired_ratio_ms_A_drl_over_A_elim"] = paired("A_drl_ms", "A_elim_ms")
json.dump(crit, open(os.path.join(out, "criteria.json"), "w"), indent=2)

style = {"A_elim_ms": ("#c0392b", "-", "o", "A chain, block order [msolve -e]"),
         "A_drl_ms": ("#e6a19a", "--", "o", "A chain, plain DRL [msolve]"),
         "B_ms": ("#2471a3", "-", "s", "B dense same set [msolve]"),
         "A_block_sg": ("#c0392b", ":", "^", "A chain, block order [Singular]"),
         "B_sg": ("#2471a3", ":", "^", "B dense same set [Singular]")}
fig, ax = plt.subplots(figsize=(8.5, 4.6))
for arm in ARMS:
    c, ls, mk, lab = style[arm]
    pts = [s for s in summary if s["arm"] == arm and "median_ms" in s]
    if pts:
        med = [s["median_ms"] for s in pts]
        ax.errorbar([s["L"] for s in pts], med, yerr=[[m - s["min_ms"] for m, s in zip(med, pts)], [s["max_ms"] - m for m, s in zip(med, pts)]],
                    color=c, ls=ls, marker=mk, ms=4, capsize=2, label=lab)
    to = [s["L"] for s in summary if s["arm"] == arm and s["n_ok"] == 0 and s["n_timeout"]]
    if to:
        ax.scatter(to, [6e5] * len(to), marker="x", color=c, s=60, zorder=5, clip_on=False)
ax.axhline(6e5, color="black", lw=0.6, ls=":")
ax.set_yscale("log"); ax.set_xlabel(f"L  (|V| = 2^L; m = {M}; p ~ 2^({M}L))")
ax.set_ylabel("median basis wall time (ms, log)\nbars = min..max; x = all timed out (600 s)")
ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
ax.legend(fontsize=7, loc="upper left"); ax.grid(alpha=.3)
ax.set_title(f"{EXP}: chain arm under a block elimination order, m = {M} (n = 6 per cell)\nruns: {RUNS.replace('RUN-ECDLP-', '')}", fontsize=8)
fig.tight_layout()
for ext in ("svg", "png"):
    fig.savefig(os.path.join(out, f"block-order-vs-L.{ext}"), dpi=150)
print(json.dumps(crit, indent=1))
