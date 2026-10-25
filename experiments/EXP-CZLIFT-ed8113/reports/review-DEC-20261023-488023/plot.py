#!/usr/bin/env python3
"""Draw graph.svg for the DEC-20261023-488023 decision report (EXP-CZLIFT-ed8113).

Every value is read from plot_data.json beside this file. Each one is either a
recorded run value (RUN-CZLIFT-c3f8a8, seed 20261009; RUN-CZLIFT-218843, seed
20261010) or a reviewer value read by key from the committed validation-20261022
and redteam-20261023 artifacts. The script derives only two things. (a) Exact
one-sided 95 percent Clopper-Pearson upper bounds from the recorded counts;
these are checked against the red team's rt_stats.json values before anything
is drawn, and the script stops on a mismatch. (b) The red team's stated
pigeonhole curves, (13^r - 1)/(2p) and p^(1/r), evaluated at the eight primes.
No sampling, no fit, no extrapolation.

Panels:
  (A) dependence rate per (p, r, seed) cell with its one-sided upper bound,
      against the frozen success (0.002) and falsification (0.01) thresholds
  (B) per-seed, pooled and per-r rates with upper bounds, plus the literal
      sampler with y = 0 admitted, against the same thresholds
  (C) mod-p bounded-relation rate per cell against (13^r - 1)/(2p), with the
      Q-dependence rate (what survives the lift)
  (D) median smallest mod-p relation coefficient per cell against the relation
      bound 6 and the attacker scale p^(1/r)
  (E) lift-survival fraction with exact two-sided 95 percent intervals
  (F) height ratio against the uniform-residue law and the hypothesis' 0.7

    python3 plot.py            # writes graph.svg next to this file
"""

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
SEED_COL = {"20261009": "#2a78d6", "20261010": "#eb6834"}
R_MARK = {2: "o", 3: "s"}
OFFSET = {("20261009", 2): 0.86, ("20261009", 3): 0.95, ("20261010", 2): 1.05, ("20261010", 3): 1.16}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SUCCESS_COL, FALSIFY_COL, BOUND_COL = "#2ca02c", "#d62728", "#9467bd"
FLOOR = 1.2e-4  # display position of an observed zero on a log axis (marked open)


def binom_cdf(k, n, q):
    return sum(math.comb(n, i) * (q ** i) * ((1.0 - q) ** (n - i)) for i in range(k + 1))


def cp_upper(k, n, alpha):
    """Exact one-sided Clopper-Pearson upper bound: the q with P(X <= k | n, q) = alpha."""
    if k >= n:
        return 1.0
    lo, hi = k / n, 1.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if binom_cdf(k, n, mid) > alpha:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def check_bounds(doc):
    alpha = doc["thresholds"]["alpha_one_sided"]
    for agg in doc["aggregates"]:
        ref = agg.get("rt_one_sided_upper")
        if ref is None:
            continue
        ours = cp_upper(agg["k"], agg["n"], alpha)
        if abs(ours - ref) > 2e-5:
            raise SystemExit(f"bound mismatch for {agg['label']}: {ours:.6g} vs rt_stats {ref:.6g}")


def style(ax):
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=7.5)


def prime_axis(ax, primes):
    ax.set_xscale("log")
    ax.set_xticks(primes)
    ax.set_xticklabels([str(p) for p in primes], fontsize=6.5)
    ax.minorticks_off()
    ax.set_xlim(primes[0] * 0.75, primes[-1] * 1.35)
    ax.set_xlabel("prime p", fontsize=8)


def threshold_lines(ax, th, vertical=False):
    line = ax.axvline if vertical else ax.axhline
    line(th["success_rate_max"], color=SUCCESS_COL, linewidth=1.2, linestyle="--")
    line(th["falsification_rate_min"], color=FALSIFY_COL, linewidth=1.2, linestyle="--")


def seed_r_handles():
    h = []
    for seed, col in SEED_COL.items():
        for r, mk in R_MARK.items():
            h.append(plt.Line2D([], [], marker=mk, color=col, linestyle="none", markersize=5,
                                label=f"seed {seed}, r = {r}"))
    return h


def panel_a(ax, doc):
    th = doc["thresholds"]
    alpha = th["alpha_one_sided"]
    for c in doc["cells"]:
        x = c["p"] * OFFSET[(c["seed"], c["r"])]
        k, n = c["dependent"], c["valid"]
        up = cp_upper(k, n, alpha)
        y = k / n if k > 0 else FLOOR
        col = SEED_COL[c["seed"]]
        ax.plot([x, x], [y, up], color=col, linewidth=0.9)
        ax.plot([x], [up], marker="_", markersize=8, color=col, linestyle="none")
        ax.plot([x], [y], marker=R_MARK[c["r"]], markersize=5, color=col,
                mfc=(col if k > 0 else "white"), linestyle="none")
        if k > 0:
            ax.annotate("1/100: 2P~1 + P~2 = O\n(tangent; trial 61)", xy=(x, y), xytext=(x * 1.6, 0.0045),
                        fontsize=6.5, color=INK, arrowprops={"arrowstyle": "->", "color": MUTED, "lw": 0.8})
    threshold_lines(ax, th)
    prime_axis(ax, doc["primes"])
    ax.set_yscale("log")
    ax.set_ylim(8e-5, 0.09)
    ax.set_ylabel("dependence rate within |m| <= 6 (per cell, n = 100)", fontsize=7.5)
    ax.set_title("(A) Per cell: 1 of 3200; every cell's bound exceeds both thresholds", loc="left", fontsize=9)
    h = seed_r_handles() + [
        plt.Line2D([], [], color=MUTED, marker="_", label="one-sided 95% upper bound (exact)"),
        plt.Line2D([], [], color=MUTED, marker="o", mfc="white", linestyle="none", label="0 observed (drawn at floor)"),
        plt.Line2D([], [], color=SUCCESS_COL, linestyle="--", label="success threshold 0.002"),
        plt.Line2D([], [], color=FALSIFY_COL, linestyle="--", label="falsification threshold 0.01")]
    ax.legend(handles=h, fontsize=5.8, frameon=False, ncol=2, loc="upper right")


def panel_b(ax, doc):
    th = doc["thresholds"]
    alpha = th["alpha_one_sided"]
    rows = list(doc["aggregates"])
    n_rows = len(rows) + 1
    for i, agg in enumerate(rows):
        yy = n_rows - 1 - i
        k, n = agg["k"], agg["n"]
        up = cp_upper(k, n, alpha)
        x = k / n if k > 0 else FLOOR
        literal = agg["source"].startswith("VAL")
        col = "#7f7f7f" if literal else INK
        ax.plot([x, up], [yy, yy], color=col, linewidth=1.6)
        ax.plot([up], [yy], marker="|", markersize=9, color=col, linestyle="none")
        ax.plot([x], [yy], marker="D", markersize=5, color=col, mfc=(col if k > 0 else "white"), linestyle="none")
        ax.text(1.05e-4, yy + 0.22, f"{agg['label']}: {k}/{n}, upper {up:.5f}", fontsize=6.3, color=INK)
    lit = doc["literal_sampler_expected_rate"]
    ax.plot([lit["value"]], [0], marker="*", markersize=10, color="#7f7f7f", linestyle="none")
    ax.text(1.05e-4, 0.22, f"literal sampler, expected 2-torsion rate {lit['value']} "
            f"(about {lit['per_seed_expected_dependent']} per seed; red team)", fontsize=6.3, color=INK)
    threshold_lines(ax, th, vertical=True)
    ax.set_xscale("log")
    ax.set_xlim(1e-4, 0.05)
    ax.set_ylim(-0.6, n_rows - 0.2)
    ax.set_yticks([])
    ax.set_xlabel("dependence rate; diamond = observed, bar end = one-sided 95% upper bound", fontsize=7.5)
    ax.set_title("(B) Success criterion met only under the y != 0 sampler", loc="left", fontsize=9)


def panel_c(ax, doc):
    primes = doc["primes"]
    for c in doc["cells"]:
        x = c["p"] * OFFSET[(c["seed"], c["r"])]
        col = SEED_COL[c["seed"]]
        ax.plot([x], [c["modp_bounded_relations"] / c["valid"]], marker=R_MARK[c["r"]], markersize=5,
                color=col, linestyle="none")
        if c["dependent"] > 0:
            ax.plot([x], [c["dependent"] / c["valid"]], marker="x", markersize=8, color=INK, linestyle="none")
    for r, ls in ((2, "-"), (3, ":")):
        ax.plot(primes, [min(1.0, (13 ** r - 1) / (2.0 * p)) for p in primes], color=MUTED, linestyle=ls,
                linewidth=1.0)
    prime_axis(ax, primes)
    ax.set_ylim(-0.03, 1.05)
    ax.set_ylabel("fraction of trials with a relation |n| <= 6", fontsize=7.5)
    ax.set_title("(C) Mod-p null: bounded relations decay by pigeonhole", loc="left", fontsize=9)
    h = seed_r_handles() + [
        plt.Line2D([], [], color=MUTED, linestyle="-", label="min(1, (13^2 - 1)/(2p)), r = 2"),
        plt.Line2D([], [], color=MUTED, linestyle=":", label="min(1, (13^3 - 1)/(2p)), r = 3"),
        plt.Line2D([], [], color=INK, marker="x", linestyle="none", label="Q-dependence (recorded); 0 elsewhere")]
    ax.legend(handles=h, fontsize=5.8, frameon=False, ncol=2, loc="upper right")


def panel_d(ax, doc):
    primes = doc["primes"]
    bound = doc["thresholds"]["relation_bound"]
    for c in doc["cells"]:
        x = c["p"] * OFFSET[(c["seed"], c["r"])]
        ax.plot([x], [c["min_modp_relation_median"]], marker=R_MARK[c["r"]], markersize=5,
                color=SEED_COL[c["seed"]], linestyle="none")
    ax.axhline(bound, color=BOUND_COL, linewidth=1.4)
    for r, ls in ((2, "-"), (3, ":")):
        ax.plot(primes, [p ** (1.0 / r) for p in primes], color=MUTED, linestyle=ls, linewidth=1.0)
    prime_axis(ax, primes)
    ax.set_yscale("log")
    ax.set_ylim(2, 150)
    ax.set_ylabel("median smallest mod-p relation, max |n| (100 trials)", fontsize=7.5)
    ax.set_title("(D) The bound 6 sits below the attacker's coefficient regime", loc="left", fontsize=9)
    h = seed_r_handles() + [
        plt.Line2D([], [], color=BOUND_COL, label="frozen relation bound 6"),
        plt.Line2D([], [], color=MUTED, linestyle="-", label="p^(1/2) (r = 2 attacker scale)"),
        plt.Line2D([], [], color=MUTED, linestyle=":", label="p^(1/3) (r = 3 attacker scale)")]
    ax.legend(handles=h, fontsize=5.8, frameon=False, ncol=2, loc="upper left")


def panel_e(ax, doc):
    rows = doc["lift_survival"]
    for i, row in enumerate(rows):
        yy = len(rows) - 1 - i
        k, n = row["k"], row["n"]
        lo, hi = row["ci95_two_sided"]
        floor_e = 1.5e-5  # an observed zero is drawn open at this floor
        x = k / n if k > 0 else floor_e
        ax.plot([max(lo, floor_e), hi], [yy, yy], color=INK, linewidth=1.6)
        ax.plot([x], [yy], marker="D", markersize=5, color=INK, mfc=(INK if k > 0 else "white"), linestyle="none")
        ax.text(1.05e-5, yy + 0.2, f"{row['label']}: {k}/{n}, 95% CI [{lo:.1e}, {hi:.1e}]", fontsize=6.5, color=INK)
    ax.set_xscale("log")
    ax.set_xlim(1e-5, 0.05)
    ax.set_ylim(-0.6, len(rows) - 0.2)
    ax.set_yticks([])
    ax.set_xlabel("lift-survival fraction f = Q-relations / bounded mod-p relations (red team, replayed inputs)",
                  fontsize=7)
    ax.set_title("(E) What the lift contributes: f = 1/1261 (not frozen)", loc="left", fontsize=9)


def panel_f(ax, doc):
    primes = doc["primes"]
    hr = doc["height_ratio"]
    for seed, col in SEED_COL.items():
        vals = hr["recorded"][seed]
        ax.plot(primes, [vals[str(p)] for p in primes], marker="o", markersize=4, color=col, linewidth=1.0,
                label=f"recorded, seed {seed} ({doc['runs'][seed]})")
    law = hr["law_uniform_symmetric_residue"]
    ax.plot(primes, [law["values"][str(p)] for p in primes], color=INK, linestyle="--", linewidth=1.0,
            label=f"uniform-residue law {law['formula']}")
    ax.axhline(doc["thresholds"]["height_ratio_claimed"], color=FALSIFY_COL, linestyle=":", linewidth=1.0,
               label="hypothesis wording 'about 0.7'")
    prime_axis(ax, primes)
    ax.set_ylim(0.58, 0.88)
    ax.set_ylabel("naive log-height / ln p (r = 2 cells)", fontsize=7.5)
    ax.set_title("(F) Height ratio rises with p; it is not a constant 0.7", loc="left", fontsize=9)
    ax.legend(fontsize=6, frameon=False, loc="lower right")


def main() -> None:
    doc = json.loads((HERE / "plot_data.json").read_text())
    check_bounds(doc)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "none",
                         "svg.hashsalt": doc["decision_id"]})
    fig = plt.figure(figsize=(11.0, 13.0))
    gsp = fig.add_gridspec(3, 2, height_ratios=[1.15, 1.0, 1.0], hspace=0.42, wspace=0.22)
    axes = {
        "A": fig.add_subplot(gsp[0, 0]),
        "B": fig.add_subplot(gsp[0, 1]),
        "C": fig.add_subplot(gsp[1, 0]),
        "D": fig.add_subplot(gsp[1, 1]),
        "E": fig.add_subplot(gsp[2, 0]),
        "F": fig.add_subplot(gsp[2, 1]),
    }
    panel_a(axes["A"], doc)
    panel_b(axes["B"], doc)
    panel_c(axes["C"], doc)
    panel_d(axes["D"], doc)
    panel_e(axes["E"], doc)
    panel_f(axes["F"], doc)
    for ax in axes.values():
        style(ax)
    fig.suptitle(f"{doc['experiment_id']} / {doc['hypothesis_id']}: evidence for {doc['decision_id']} "
                 f"({doc['evidence_id']})", x=0.02, ha="left", fontsize=11, color=INK)
    fig.text(0.02, 0.962, f"Runs {doc['runs']['20261009']} (seed 20261009) and {doc['runs']['20261010']} "
             "(seed 20261010); p = 101..12809, r in {2, 3}, 100 trials per cell, y != 0 sampler, bound 6; "
             "toy tier. Panels C-E: red-team values on exactly replayed inputs.",
             fontsize=7.2, color=MUTED, ha="left")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.935, bottom=0.04)
    fig.savefig(HERE / "graph.svg", format="svg", metadata={"Date": None})


if __name__ == "__main__":
    main()
