import csv, glob, json
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

R = json.load(open("results.json")); T = list(csv.DictReader(open("curve_traits.csv")))
ink, sec, mut, surf, grid = "#0b0b0b", "#52514e", "#898781", "#fcfcfb", "#ecebe8"
COL = {"crater": "#eb6834", "floor409": "#1baf7a", "floor1721": "#4a3aa7", "bottom": "#a9a8a2", "tau": "#2a78d6"}
NAME = {"crater": "Crater  (End = O_K, f = 1)", "floor409": "409-floor  (f = 409)", "floor1721": "1721-floor  (f = 1721)", "bottom": "Bottom  (f = 409·1721)"}
LV = ["crater", "floor409", "floor1721", "bottom"]

def ops(cid, m):
    return np.array([float(r["ops"]) for f in glob.glob(f"raw/c{cid}_m{m}_r*.csv") for r in csv.DictReader(open(f))])

fig = plt.figure(figsize=(16, 9.6), dpi=160); fig.patch.set_facecolor(surf)
gs = fig.add_gridspec(2, 3, width_ratios=[1.5, 1, 1], height_ratios=[1, 1], hspace=.42, wspace=.28, left=.135, right=.975, top=.81, bottom=.08)

# A: per-curve mean steps, every curve, grouped by level
ax = fig.add_subplot(gs[:, 0]); ax.set_facecolor(surf)
ypos, yt, yl = 0, [], []
rows = [("tau", "0", 1)] + [(t["level"], t["id"], 0) for t in T]
groups = [("Crater + Frobenius", [r for r in rows if r[0] == "tau"])] + [(NAME[l], [r for r in rows if r[0] == l and r[2] == 0]) for l in LV]
for gname, rs in groups:
    vals = [ops(cid, m) for _, cid, m in rs]
    means = np.array([v.mean() for v in vals]); ses = np.array([v.std(ddof=1) / np.sqrt(len(v)) for v in vals])
    ys = ypos + np.linspace(0, .8, len(rs)) if len(rs) > 1 else np.array([ypos + .4])
    key = rs[0][0]
    ax.errorbar(means, ys, xerr=1.96 * ses, fmt="o", ms=3.2, color=COL[key], ecolor=COL[key], elinewidth=.8, alpha=.9)
    pooled = np.concatenate(vals); ax.plot([pooled.mean()] * 2, [ys.min() - .08, ys.max() + .08], color=ink, lw=1.4)
    yt.append(ypos + .4); yl.append(f"{gname}\n{len(rs)} curve{'s' if len(rs) > 1 else ''}, {len(pooled):,} solves"); ypos += 1.25
ax.set_yticks(yt); ax.set_yticklabels(yl, fontsize=9); [t.set_color(ink) for t in ax.get_yticklabels()]; ax.invert_yaxis(); ax.set_xlim(0, 820000)
ax.set_xlabel("Mean group operations to solve, per curve (dots ±95% CI; black bar = level mean)", color=sec, fontsize=9)
ax.set_title("Every curve, apples to apples", loc="left", fontsize=11.5, fontweight="bold", color=ink)

def style(a):
    a.set_facecolor(surf)
    for s in ("top", "right", "left"): a.spines[s].set_visible(False)
    a.spines["bottom"].set_color(mut); a.tick_params(colors=mut, length=0, labelsize=8.5); a.xaxis.grid(True, color=grid, lw=.8); a.set_axisbelow(True)
style(ax); [t.set_color(ink) for t in ax.get_yticklabels()]

# B: level ratio vs crater (negation only), steps & time, 90% CI vs +-3% band
ax = fig.add_subplot(gs[0, 1]); style(ax)
h2 = R["H2_level_effect_negation_only"]
AM = R["H2_time_idle_test"]["levels"]
for k, (metric, off) in enumerate((("ops", -.12), ("sec", .12))):
    for i, lev in enumerate(LV[1:]):
        t = h2[metric]["tost_vs_crater_neg"][lev] if metric == "ops" else dict(ratio=AM[lev]["sec_ratio"], ci90=AM[lev]["ci90"])
        ax.errorbar(t["ratio"], i + off, xerr=[[t["ratio"] - t["ci90"][0]], [t["ci90"][1] - t["ratio"]]], fmt="o" if metric == "ops" else "s",
                    color=COL[lev], ms=5, capsize=0, elinewidth=1.5)
ax.axvspan(.97, 1.03, color="#f0efec", zorder=0); ax.axvline(1, color=mut, lw=.8)
ax.set_yticks(range(3)); ax.set_yticklabels([NAME[l].split("  ")[0] for l in LV[1:]], fontsize=9, color=ink); ax.invert_yaxis(); ax.set_xlim(.86, 1.08)
ax.set_title("Lower levels vs crater (negation only)", loc="left", fontsize=11.5, fontweight="bold", color=ink)
ax.set_xlabel("Ratio of mean cost, 90% CI; band = ±3%\n● steps (all solves)   ■ time (idle-machine phase 3)", color=sec, fontsize=9)

# C: per-step ns
ax = fig.add_subplot(gs[1, 1]); style(ax)
ps = R["per_step_ns"]["levels"]
for i, lev in enumerate(LV):
    ax.barh(i, ps[lev]["median_ns"], height=.55, color=COL[lev], edgecolor=surf, lw=2); ax.text(ps[lev]["median_ns"] + 15, i, f"{ps[lev]['median_ns']:.0f}", va="center", fontsize=8.5, color=sec)
ax.barh(4, R["per_step_ns"]["crater_frobenius_median_ns"], height=.55, color=COL["tau"], edgecolor=surf, lw=2)
ax.text(R["per_step_ns"]["crater_frobenius_median_ns"] + 15, 4, f"{R['per_step_ns']['crater_frobenius_median_ns']:.0f}", va="center", fontsize=8.5, color=sec)
ax.set_yticks(range(5)); ax.set_yticklabels([NAME[l].split("  ")[0] for l in LV] + ["Crater + Frobenius"], fontsize=9, color=ink); ax.invert_yaxis()
ax.set_xlim(0, 1500); ax.set_title("Cost of one rho step", loc="left", fontsize=11.5, fontweight="bold", color=ink)
ax.set_xlabel("ns per step, median of 3 pinned reps × each curve", color=sec, fontsize=9)

# D: endomorphism structure (log scale): min non-integer endo degree, best smooth-endo orbit
ax = fig.add_subplot(gs[0, 2]); style(ax); ax.xaxis.grid(False); ax.yaxis.grid(True, color=grid, lw=.8)
lt = json.load(open("level_traits.json")); se = json.load(open("smooth_endos.json"))
x = np.arange(4)
ax.bar(x - .2, [lt[l]["min_nonscalar_endo_degree"] for l in LV], .38, color=[COL[l] for l in LV], edgecolor=surf, lw=2)
ax.bar(x + .2, [se[l]["smallest_k"] for l in LV], .38, color=[COL[l] for l in LV], edgecolor=surf, lw=2, hatch="///", alpha=.55)
ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels(["crater", "409", "1721", "bottom"], fontsize=9, color=ink)
ax.set_title("Endomorphisms available", loc="left", fontsize=11.5, fontweight="bold", color=ink)
ax.set_xlabel("solid: min degree of a non-integer endomorphism\nhatched: smallest orbit from any smooth endomorphism", color=sec, fontsize=8.5)
for i, l in enumerate(LV): ax.text(i - .2, lt[l]["min_nonscalar_endo_degree"] * 1.4, f"{lt[l]['min_nonscalar_endo_degree']:.0e}" if i else "2 (τ)", ha="center", fontsize=7.5, color=sec)

# E: modelled best net speedup from smooth endomorphisms
ax = fig.add_subplot(gs[1, 2]); style(ax)
for i, l in enumerate(LV):
    v = se[l]["best_S"]; ax.barh(i, v, height=.55, color=COL[l], edgecolor=surf, lw=2); ax.text(v * 1.4, i, f"{v:.4g}×", va="center", fontsize=8.5, color=sec)
ax.set_xscale("log"); ax.axvline(1, color=mut, lw=.8); ax.set_xlim(1e-6, 10)
ax.set_yticks(range(4)); ax.set_yticklabels(["crater", "409-floor", "1721-floor", "bottom"], fontsize=9, color=ink); ax.invert_yaxis()
ax.set_title("Best endomorphism speedup (model)", loc="left", fontsize=11.5, fontweight="bold", color=ink)
ax.set_xlabel("vs negation-only rho; >1 helps\n(smooth degree ≤ 2^44, primes ≤ 43)", color=sec, fontsize=8.5)

sp = R["frobenius_speedup_on_crater"]
idl = R["H2_time_idle_test"]["levels"]; rr = [idl[l]["sec_ratio"] for l in LV[1:]]
tost = h2["ops"]["tost_vs_crater_neg"]; okall = all(tost[l]["equivalent_within_3pct"] for l in LV[1:])
fig.suptitle("The whole isogeny volcano of a Koblitz curve, compared on equal terms (F_2^41 replication)", x=.012, ha="left", y=.985, fontsize=14.5, fontweight="bold", color=ink)
fig.text(.012, .935, f"708,153 curves in the class: crater 1, 409-floor 410, 1721-floor 1,722, bottom 706,020. Tested {len(T)} curves (30 per lower level; floors enumerated by explicit vertical isogenies + 29-isogeny cycles, bottom from a random scan), "
         f"{R['validity']['total_solves']:,} verified solves.\nWith negation only, steps: Kruskal–Wallis p = {h2['ops']['kruskal_p_4_levels']:.2f}; "
         + ("each level within ±3% of the crater" if okall else "±3% equivalence NOT established at this n (see report)") +
         f"; idle-machine solve time {min(rr):.3f}–{max(rr):.3f}× (n=600 vs 300: CIs ±6%, inconclusive; ns per op equal within 0.2%).\nOnly the crater has a cheap non-trivial endomorphism (τ, degree 2): it saves {sp['ops'][0]:.2f}× steps / {R['H2_time_idle_test']['frobenius_time_speedup']:.2f}× time (idle). "
         f"Below the crater the cheapest orbit-producing endomorphisms would make rho far slower.\nNo curve beats crater + Frobenius (Holm p = {R['H1_any_curve_faster_than_crater_with_frobenius']['ops']['min_holm_p']:.2g}).",
         fontsize=9, color=sec, va="top")
fig.savefig("volcano_rho_study.png", facecolor=surf); fig.savefig("volcano_rho_study.svg", facecolor=surf)
