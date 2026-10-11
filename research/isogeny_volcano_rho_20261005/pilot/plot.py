import csv, glob, json
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = json.load(open("results.json"))
NAMES = ["K-tau", "K-neg"] + [f"I{i}" for i in range(1, 9)]
LAB = {"K-tau": "Koblitz, ±1 + Frobenius", "K-neg": "Koblitz, ±1 only (control)", **{f"I{i}": f"Isogenous curve I{i}" for i in range(1, 9)}}
COL = {"K-tau": "#2a78d6", "K-neg": "#eb6834", **{f"I{i}": "#a9a8a2" for i in range(1, 9)}}
ink, sec, mut, surf, grid = "#0b0b0b", "#52514e", "#898781", "#fcfcfb", "#ecebe8"
def load(n, col):
    return np.array([float(r[col]) for f in sorted(glob.glob(f"raw/{n}_r*.csv")) for r in csv.DictReader(open(f))])
ns = {n: [] for n in NAMES}
for r in csv.reader(open("bench/ns_per_step.csv")): ns[r[0]].append(float(r[2]))
fig, axs = plt.subplots(1, 3, figsize=(15, 6.4), dpi=170, sharey=True, gridspec_kw=dict(width_ratios=[1.25, 1.25, 1]))
fig.patch.set_facecolor(surf)
y = np.arange(len(NAMES))[::-1]
panels = [("ops", 1, "Group operations per solve", "Steps to solve (hardware-independent)"),
          ("sec", 1e3, "Milliseconds per solve", "Wall-clock time to solve"),
          (None, 1, "ns per walk step (median, IQR)", "Cost of one rho step")]
for ax, (col, sc, xl, tt) in zip(axs, panels):
    ax.set_facecolor(surf)
    for yi, n in zip(y, NAMES):
        if col:
            v = load(n, col) * sc
            q = np.quantile(v, [.1, .25, .5, .75, .9])
            ax.plot([q[0], q[4]], [yi, yi], color=COL[n], lw=1.5, solid_capstyle="round")
            ax.barh(yi, q[3] - q[1], left=q[1], height=.5, color=COL[n], edgecolor=surf, lw=2)
            ax.plot([q[2]] * 2, [yi - .25, yi + .25], color=surf, lw=2)
            ax.plot(v.mean(), yi, "o", ms=6, color=ink, mec=surf, mew=1.5)
        else:
            v = np.array(ns[n]); q = np.quantile(v, [.25, .5, .75])
            ax.plot([q[0], q[2]], [yi, yi], color=COL[n], lw=3, solid_capstyle="round")
            ax.plot(q[1], yi, "o", ms=8, color=COL[n], mec=surf, mew=1.5)
            ax.text(q[2] + 25, yi, f"{q[1]:.0f}", va="center", fontsize=8.5, color=sec)
    ax.set_title(tt, loc="left", fontsize=11, color=ink, fontweight="bold")
    ax.set_xlabel(xl, color=sec, fontsize=9.5); ax.set_xlim(left=0)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(mut); ax.tick_params(colors=mut, length=0, labelsize=9)
    ax.xaxis.grid(True, color=grid, lw=.8); ax.set_axisbelow(True)
axs[0].set_yticks(y); axs[0].set_yticklabels([LAB[n] for n in NAMES], color=ink, fontsize=9.5)
axs[2].set_xlim(0, 1450)
sp = R["speedup_Kneg_over_Ktau"]; h2 = R["H2_curve_choice_without_tau"]
fig.suptitle("Pollard rho on a Koblitz curve vs. 8 curves isogenous to it — 5,000 verified solves per arm",
             x=.012, ha="left", fontsize=14, fontweight="bold", color=ink, y=.985)
fig.text(.012, .905,
    "Toy proxy for ECC2K-130: y²+xy=x³+1 over F_2^37, prime subgroup ℓ ≈ 2^27.8; isogenous curves built by explicit 73-isogenies (same #E, distinct j). "
    f"Isogenous curves = Koblitz-without-Frobenius\n(Kruskal–Wallis p = {h2['ops']['kruskal_p']:.2f} on steps, {h2['sec']['kruskal_p']:.2f} on time; every curve equivalent to the control within ±5%). "
    f"None is faster than Koblitz+Frobenius (Holm-adjusted p = 1.0). Frobenius saves {sp['ops'][0]:.2f}× steps [95% CI {sp['ops'][1]:.2f}–{sp['ops'][2]:.2f}],\n"
    f"{sp['sec'][0]:.2f}× wall-clock [{sp['sec'][1]:.2f}–{sp['sec'][2]:.2f}]: each Frobenius step costs 2.16× more here because a polynomial basis needs 37 squarings per canonicalization (a normal basis makes it a rotation).",
    fontsize=9, color=sec, va="top")
fig.text(.012, .012, "Boxes: interquartile range, whiskers 10th–90th percentile, white tick median, black dot mean. Right panel: 21 interleaved reps of 2^20 steps on one pinned core. "
         "Every solution verified against the secret and by recomputing [k]P = Q. Protocol frozen before the run (PROTOCOL.md).", fontsize=7.8, color=mut)
fig.tight_layout(rect=(0, .03, 0.99, .86)); fig.savefig("isogeny_rho_measured.png", facecolor=surf)
