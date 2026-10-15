#!/usr/bin/env python3
"""Derive per-cell summaries and the cost-vs-L graph from RUN-ECDLP-f49f75-01.

Reads recorded values only (raw-result.jsonl); no recomputation or sampling.
Usage: analyze.py RAW_JSONL OUT_DIR
"""
import json, os, statistics, sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

raw, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
rows = [json.loads(l) for l in open(raw)]

cells = defaultdict(lambda: defaultdict(list))  # (m,L) -> key -> [records]
meta = {}
for r in rows:
    meta[(r["m"], r["L"])] = dict(p=r["p"], p_bits=r["p_bits"])
    for k, v in r["results"].items():
        cells[(r["m"], r["L"])][k].append(v)

def tot(v):
    return v["std_ms"] + v["fglm_ms"]

summary = []
for (m, L), arms in sorted(cells.items()):
    for k, vs in sorted(arms.items()):
        ok = [v for v in vs if v["status"] == "ok"]
        rec = dict(m=m, L=L, p=meta[(m, L)]["p"], p_bits=meta[(m, L)]["p_bits"], arm=k,
                   n=len(vs), n_ok=len(ok),
                   n_timeout=sum(v["status"] == "timeout" for v in vs),
                   n_degenerate=sum(v["status"] == "degenerate_target" for v in vs),
                   n_other=sum(v["status"] not in ("ok", "timeout", "degenerate_target") for v in vs))
        if k == "E":
            if ok:
                rec.update(median_group_ops=statistics.median(v["group_ops"] for v in ok),
                           median_wall_ms=1000 * statistics.median(v["wall_s"] for v in ok),
                           median_fb=statistics.median(v["fb_size"] for v in ok))
        elif ok:
            t = [tot(v) for v in ok]
            rec.update(median_total_ms=statistics.median(t), min_total_ms=min(t), max_total_ms=max(t),
                       median_vdim=statistics.median(v["vdim"] for v in ok),
                       max_gb_maxdeg=max(v["gb_maxdeg"] for v in ok),
                       max_mem_bytes=max(v.get("mem_bytes", 0) for v in ok),
                       planted_checked=sum("planted_in_variety" in v for v in ok),
                       planted_ok=sum(v.get("planted_in_variety") is True for v in ok))
        summary.append(rec)
json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)

# ---- graph
style = {"A": ("#c0392b", "A chain (PKM isogeny)"), "B": ("#2471a3", "B dense, same set"),
         "C": ("#7d8c8d", "C dense, random set"), "E": ("#1e8449", "E enumeration, Python wall (<0.1 ms shown at floor)")}
fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
for ax, m in zip(axes, (2, 3)):
    for arm in "ABC":
        for solver, ls, mk in (("std", "-", "o"), ("slimgb", "--", "s")):
            key = arm if solver == "std" else f"{arm}:slimgb"
            pts = [s for s in summary if s["m"] == m and s["arm"] == key and "median_total_ms" in s]
            if not pts:
                continue
            Ls = [s["L"] for s in pts]
            med = [max(s["median_total_ms"], 0.5) for s in pts]
            lo = [med[i] - max(s["min_total_ms"], 0.5) for i, s in enumerate(pts)]
            hi = [max(s["max_total_ms"], 0.5) - med[i] for i, s in enumerate(pts)]
            ax.errorbar(Ls, med, yerr=[lo, hi], color=style[arm][0], ls=ls, marker=mk, ms=4, capsize=2,
                        label=f"{style[arm][1]} [{solver}]")
        to = [s["L"] for s in summary if s["m"] == m and s["arm"] == arm and s["n_ok"] == 0 and s["n_timeout"]]
        if to:
            ax.scatter(to, [6e5] * len(to), marker="x", color=style[arm][0], s=60, zorder=5)
    pts = [s for s in summary if s["m"] == m and s["arm"] == "E" and "median_wall_ms" in s]
    ax.plot([s["L"] for s in pts], [max(s["median_wall_ms"], 0.5) for s in pts], color=style["E"][0],
            marker="^", ms=4, label=style["E"][1])
    ax.axhline(6e5, color="black", lw=0.6, ls=":")
    ax.set_yscale("log")
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.set_xlabel("L  (|V| = 2^L candidate x-coordinates; p ~ 2^(mL))")
    ax.set_title(f"m = {m}  (Semaev S_{m+1})")
    ax.grid(alpha=0.3)
axes[0].set_ylabel("median time per decomposition (ms, log)\nGroebner = std + fglm; bars = min..max")
axes[1].text(0.02, 0.97, "x = every instance hit the 600 s timeout (dotted line)", transform=axes[1].transAxes,
             fontsize=7, va="top")
axes[0].legend(fontsize=6.5, loc="upper left")
fig.suptitle("EXP-ECDLP-f49f75 / RUN-ECDLP-f49f75-01: decomposition cost vs factor-base set size "
             "(n = 6 instances per cell, values floored at 0.5 ms)", fontsize=9)
fig.tight_layout()
for ext in ("svg", "png"):
    fig.savefig(os.path.join(out, f"cost-vs-L.{ext}"), dpi=150)
print(json.dumps(summary[:3], indent=1))
