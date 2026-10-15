#!/usr/bin/env python3
"""Summaries, frozen criteria and graphs for EXP-ECDLP-502ae2 (recorded values only).

Usage: analyze.py OUT_DIR MSOLVE_RUN_DIR SINGULAR_RUN_DIR
SINGULAR_RUN_DIR is EXP-ECDLP-f49f75/runs/RUN-ECDLP-f49f75-02 (same m = 3 instances).
"""
import json, os, statistics, sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

out, ms_dir, sg_dir = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
ms = [json.loads(l) for l in open(os.path.join(ms_dir, "raw-result.jsonl"))]
sg = [json.loads(l) for l in open(os.path.join(sg_dir, "raw-result.jsonl"))]

cells = defaultdict(list)
for r in ms:
    for k, v in r["results"].items():
        cells[(r["L"], k)].append(dict(v, inst=r["inst"], kind=r["kind"], p_bits=r["p_bits"]))

summary = []
for (L, k), vs in sorted(cells.items()):
    rec = dict(L=L, arm=k, p_bits=vs[0]["p_bits"], n=len(vs),
               n_ok=sum(v["status"] == "ok" for v in vs),
               n_timeout=sum(v["status"] == "timeout" for v in vs),
               n_degenerate=sum(v["status"] == "degenerate_target" for v in vs),
               n_crash=sum(str(v["status"]).startswith("rc") for v in vs))
    ok = [v for v in vs if v["status"] == "ok"]
    if k == "E":
        if ok:
            rec.update(median_group_ops=statistics.median(v["group_ops"] for v in ok),
                       median_fb=statistics.median(v["fb_size"] for v in ok))
    elif ok:
        s = [1000 * v["solve_wall_s"] for v in ok]
        g = [1000 * v["gb_wall_s"] for v in ok]
        rec.update(median_solve_ms=statistics.median(s), min_solve_ms=min(s), max_solve_ms=max(s),
                   median_gb_ms=statistics.median(g),
                   max_f4_deg=max(v.get("f4_max_deg", 0) for v in ok),
                   median_quotient_dim=statistics.median(v.get("quotient_dim", 0) for v in ok),
                   nvars=ok[0]["nvars"],
                   planted_checked=sum("planted_in_variety" in v for v in ok),
                   planted_ok=sum(v.get("planted_in_variety") is True for v in ok))
    # gb-only completions (solve timed out) still carry a degree
    gbdone = [v for v in vs if v.get("gb_status") == "ok"]
    if gbdone and k != "E":
        rec["max_f4_deg_gb_done"] = max(v.get("f4_max_deg", 0) for v in gbdone)
        rec["n_gb_done"] = len(gbdone)
    summary.append(rec)
json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)

by = {(s["L"], s["arm"]): s for s in summary}
joint = sorted(L for (L, k) in by if k == "A" and "median_solve_ms" in by[(L, k)] and "median_solve_ms" in by.get((L, "B"), {}))
faster = [L for L in joint if by[(L, "A")]["median_solve_ms"] < by[(L, "B")]["median_solve_ms"]]
def last_ok(arm):
    Ls = [L for (L, k), s in by.items() if k == arm and s["n_ok"] > 0]
    return max(Ls) if Ls else None
def retired(arm):
    Ls = [L for (L, k), s in by.items() if k == arm and s["n_ok"] == 0 and s["n_timeout"]]
    return min(Ls) if Ls else None
crit = dict(jointly_completed_L=joint, A_faster=len(faster),
            ratio_A_over_B={f"L{L}": round(by[(L, "A")]["median_solve_ms"] / by[(L, "B")]["median_solve_ms"], 1) for L in joint},
            retirement={a: dict(largest_L_completed=last_ok(a), retired_at_L=retired(a)) for a in "ABC"})

# paired msolve vs Singular (same instance): Singular std+fglm and slimgb+fglm totals
sgi = {(r["L"], r["inst"]): r for r in sg}
pairs = defaultdict(list)
for r in ms:
    s = sgi.get((r["L"], r["inst"]))
    if not s:
        continue
    for arm in "ABC":
        a, b = r["results"].get(arm, {}), s["results"].get(arm, {})
        for solver, key in (("std", arm), ("slimgb", f"{arm}:slimgb")):
            b = s["results"].get(key, {})
            if a.get("status") == "ok" and b.get("status") == "ok":
                pairs[(r["L"], arm, solver)].append((b["std_ms"] + b["fglm_ms"]) / max(1000 * a["solve_wall_s"], 1))
crit["singular_over_msolve_median"] = {f"L{L}-{arm}-{sv}": round(statistics.median(v), 2) for (L, arm, sv), v in sorted(pairs.items())}
json.dump(crit, open(os.path.join(out, "criteria.json"), "w"), indent=1)

# graph
col = {"A": "#c0392b", "B": "#2471a3", "C": "#7d8c8d"}
name = {"A": "A chain (PKM isogeny)", "B": "B dense, same set", "C": "C dense, random set"}
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
sgcells = defaultdict(list)
for r in sg:
    for arm in "ABC":
        v = r["results"].get(arm, {})
        if v.get("status") == "ok":
            sgcells[(r["L"], arm)].append(v["std_ms"] + v["fglm_ms"])
for arm in "ABC":
    pts = [s for s in summary if s["arm"] == arm and "median_solve_ms" in s]
    Ls = [s["L"] for s in pts]
    med = [s["median_solve_ms"] for s in pts]
    ax.errorbar(Ls, med, yerr=[[m - s["min_solve_ms"] for m, s in zip(med, pts)], [s["max_solve_ms"] - m for m, s in zip(med, pts)]],
                color=col[arm], marker="o", ms=4, capsize=2, label=f"{name[arm]} [msolve -P 1]")
    sp = sorted((L, statistics.median(v)) for (L, a), v in sgcells.items() if a == arm)
    if sp:
        ax.plot([x for x, _ in sp], [y for _, y in sp], color=col[arm], ls=":", marker="s", ms=3, alpha=0.6,
                label=f"{name[arm]} [Singular std, EXP-f49f75]")
    to = [s["L"] for s in summary if s["arm"] == arm and s["n_ok"] == 0 and s["n_timeout"]]
    if to:
        ax.scatter(to, [6e5 * (1.25 if arm == "A" else 1)] * len(to), marker="x", color=col[arm], s=70, zorder=5, clip_on=False)
    dp = [s for s in summary if s["arm"] == arm and "max_f4_deg_gb_done" in s]
    ax2.plot([s["L"] for s in dp], [s["max_f4_deg_gb_done"] for s in dp], color=col[arm], marker="o", label=name[arm])
ax.axhline(6e5, color="black", lw=0.6, ls=":")
ax.annotate("L=6: only the 2 random\n(no-solution) targets finished;\nall 4 planted timed out", xy=(6, 2.2e5), xytext=(4.6, 3e3),
            fontsize=6.5, arrowprops=dict(arrowstyle="->", lw=0.6))
ax.set_yscale("log"); ax.set_xlabel("L  (|V| = 2^L; m = 3; p ~ 2^(3L))")
ax.set_ylabel("median full-solve time (ms, log)\nbars = min..max, x = all timed out (600 s)")
ax.legend(fontsize=6.3, loc="lower right"); ax.grid(alpha=.3)
ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
ax2.set_xlabel("L"); ax2.set_ylabel("max F4 degree reached (msolve -v 2)")
ax2.set_title("solving degree proxy (instances whose basis completed)", fontsize=8)
ax2.legend(fontsize=7); ax2.grid(alpha=.3)
ax2.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
fig.suptitle("EXP-ECDLP-502ae2 / RUN-ECDLP-502ae2-01: m = 3 decomposition under msolve 0.6.5 (n = 6 instances per cell)", fontsize=9)
fig.tight_layout()
for ext in ("svg", "png"):
    fig.savefig(os.path.join(out, f"msolve-cost-vs-L.{ext}"), dpi=150)
print(json.dumps(crit, indent=1))
