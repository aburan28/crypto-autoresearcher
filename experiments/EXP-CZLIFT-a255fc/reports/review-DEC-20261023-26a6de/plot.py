#!/usr/bin/env python3
"""Draw graph.svg for the DEC-20261023-26a6de decision report (EXP-CZLIFT-a255fc).

Every value is read from plot_data.json beside this file. Each value there is a
recorded run-manifest value or a reviewer value read by key from the committed
validation-20261022 / redteam-20261023 artifacts. This script computes
nothing new: no sampling, no fit, no extrapolation.

Panels:
  (A) coverage-ratio median per run against the frozen success band [0.8, 1.2]
  (B) the same medians, zoomed, against the seeded null bands, the mechanism
      nulls and the instrument ceiling
  (C) growth slope minus r/2 against the frozen tolerance +-1
  (D) H_half slope / (2/r), on and off the grid, against the frozen [0.5, 2]
  (E) obstruction quantity q1: N_E(H) over the volume law, against H
  (F) log H_half / log p at the resolved toy primes

    python3 plot.py            # writes graph.svg next to this file
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
RUN_MAIN, RUN_REP = "RUN-CZLIFT-74f172", "RUN-CZLIFT-490b33"
C_MAIN, C_REP = "#2a78d6", "#eb6834"
INK, MUTED, GRID, BAND = "#0b0b0b", "#52514e", "#e4e3df", "#d9ead3"
NULL_COLOURS = ["#7f7f7f", "#4d4d4d", "#9467bd", "#8c564b", "#17becf", "#2ca02c"]
RANK_COLOURS = {1: "#1f77b4", 2: "#ff7f0e", 3: "#2ca02c", 4: "#d62728", 5: "#9467bd", 6: "#8c564b", 7: "#e377c2"}


def style(ax):
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=7.5)


def panel_a(ax, cov):
    lo, hi = cov["frozen_success_band"]
    ax.axvspan(lo, hi, color=BAND, label=f"frozen success band [{lo}, {hi}]")
    for i, run in enumerate(cov["runs"]):
        col = C_MAIN if run["run_id"] == RUN_MAIN else C_REP
        ax.plot([run["observed_median"]], [i], marker="D", markersize=7, color=col, linestyle="none")
        ax.text(run["observed_median"] + 0.01, i + 0.18,
                f"{run['observed_median']:.4f}  ({run['cells']} cells, frac>1.5 = {run['frac_above_1p5']})",
                fontsize=7, color=INK)
        top = max(c["value"] for c in run["ceilings"])
        ax.plot([top], [i - 0.25], marker="|", markersize=10, color=INK, linestyle="none")
    ax.set_yticks(range(len(cov["runs"])))
    ax.set_yticklabels([f"{r['run_id']}\n{r['label']}" for r in cov["runs"]], fontsize=7)
    ax.set_xlim(0.75, 1.25)
    ax.set_ylim(-0.7, len(cov["runs"]) - 0.3)
    ax.set_xlabel("coverage-ratio median (distinct / uniform model)", fontsize=8)
    ax.set_title("(A) Frozen criterion: met, but cannot fail upward", loc="left", fontsize=9)
    h = [plt.Line2D([], [], marker="D", color=C_MAIN, linestyle="none", label="observed median (recorded)"),
         plt.Line2D([], [], marker="|", color=INK, markersize=10, linestyle="none",
                    label="max-spread ceiling (any point set, derived)"),
         plt.Rectangle((0, 0), 1, 1, color=BAND, label="frozen band [0.8, 1.2]")]
    ax.legend(handles=h, loc="lower left", fontsize=6.5, frameon=False)


def panel_b(ax, cov):
    rows = []
    for run in cov["runs"]:
        tag = "main" if run["run_id"] == RUN_MAIN else "rep"
        for k, n in enumerate(run["nulls"]):
            rows.append((f"{tag}: {n['label']}", n["centre"], n["band95"], run["observed_median"],
                         NULL_COLOURS[k], n["reps_ge_observed"]))
    for k, r in enumerate(cov["subset_H_le_3e4"]["rows"]):
        rows.append((f"H<=3e4: {r['label']}", r["centre"], r["band95"], r["observed_median"],
                     NULL_COLOURS[3 + k], r["reps_ge_observed"]))
    n = len(rows)
    for i, (label, centre, band, obs, col, reps) in enumerate(rows):
        y = n - 1 - i
        ax.plot(band, [y, y], color=col, linewidth=3, solid_capstyle="butt")
        ax.plot([centre], [y], marker="o", markersize=4, color=col, linestyle="none")
        ax.plot([obs], [y], marker="D", markersize=5, color=INK, linestyle="none")
        ax.text(1.0005, y + 0.28, f"{label}   reps >= observed: {reps}", fontsize=5.8, color=INK)
    for run in cov["runs"]:
        col = C_MAIN if run["run_id"] == RUN_MAIN else C_REP
        ax.axvline(run["observed_median"], color=col, linewidth=0.8, linestyle=":")
        for c in run["ceilings"]:
            if c["label"].startswith("planted"):
                ax.axvline(c["value"], color=col, linewidth=0.8, linestyle="--")
    ax.set_yticks([])
    ax.set_xlim(0.999, 1.062)
    ax.set_ylim(-0.8, n)
    ax.set_xlabel("coverage-ratio median; bars = 95% null band, dot = null centre, diamond = observed", fontsize=7.5)
    ax.set_title("(B) Calibrated nulls: uniform rejected, kernel-floor model fits", loc="left", fontsize=9)
    h = [plt.Line2D([], [], color=C_MAIN, linestyle=":", label=f"observed {RUN_MAIN}"),
         plt.Line2D([], [], color=C_REP, linestyle=":", label=f"observed {RUN_REP}"),
         plt.Line2D([], [], color=MUTED, linestyle="--", label="planted max-spread median (passes frozen criterion)")]
    ax.legend(handles=h, loc="lower right", fontsize=6, frameon=False)


def panel_c(ax, gs):
    tol = gs["frozen_tolerance_abs"]
    ax.axhspan(-tol, tol, color=BAND)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    for run, col, dx in ((RUN_MAIN, C_MAIN, -0.1), (RUN_REP, C_REP, 0.1)):
        xs = [r["rank"] + dx for r in gs["rows"]]
        ys = [r[run] - r["predicted"] for r in gs["rows"]]
        ax.plot(xs, ys, marker="o", markersize=5, color=col, linestyle="none", label=run)
    ax.set_xticks([r["rank"] for r in gs["rows"]])
    ax.set_xticklabels([f"{r['rank']}\n{r['curve']}" for r in gs["rows"]], fontsize=6)
    ax.set_ylim(-1.1, 1.1)
    ax.set_ylabel("slope - r/2", fontsize=8)
    ax.set_title("(C) Growth slope vs r/2 (frozen tolerance +-1 shaded)", loc="left", fontsize=9)
    ax.legend(fontsize=6.5, frameon=False, loc="lower left")


def panel_d(ax, hh):
    lo, hi = hh["frozen_tolerance_ratio"]
    ax.axhspan(lo, hi, color=BAND)
    ax.axhline(1.0, color=MUTED, linewidth=0.8)
    for run, col, dx in ((RUN_MAIN, C_MAIN, -0.12), (RUN_REP, C_REP, 0.12)):
        for r in hh["rows"]:
            d = r[run]
            t = r["two_over_r"]
            ax.errorbar([r["rank"] + dx - 0.04], [d["grid"] / t], yerr=[d["grid_se"] / t], fmt="s",
                        markersize=4, color=col, mfc="none", elinewidth=0.8, capsize=2)
            ax.errorbar([r["rank"] + dx + 0.04], [d["offgrid"] / t], yerr=[d["offgrid_se"] / t], fmt="o",
                        markersize=4, color=col, elinewidth=0.8, capsize=2)
    ax.set_xticks([r["rank"] for r in hh["rows"]])
    ax.set_xticklabels([f"{r['rank']}\n{r['curve']}" for r in hh["rows"]], fontsize=6)
    ax.set_ylim(0.4, 2.1)
    ax.set_ylabel("H_half slope / (2/r)", fontsize=8)
    ax.set_title("(D) H_half slope vs 2/r (frozen [0.5, 2] shaded)", loc="left", fontsize=9)
    h = [plt.Line2D([], [], marker="s", mfc="none", color=MUTED, linestyle="none", label="frozen grid (recorded), +-1 SE"),
         plt.Line2D([], [], marker="o", color=MUTED, linestyle="none", label="off grid (red team), +-1 SE"),
         plt.Line2D([], [], marker="o", color=C_MAIN, linestyle="none", label=RUN_MAIN),
         plt.Line2D([], [], marker="o", color=C_REP, linestyle="none", label=RUN_REP)]
    ax.legend(handles=h, fontsize=6, frameon=False, loc="upper right")


def panel_e(ax, vl):
    ax.axhline(1.0, color=MUTED, linewidth=0.8)
    for r in vl["rows"]:
        ax.plot(vl["H"], r["ratio"], marker="o", markersize=3.5, linewidth=1.0,
                color=RANK_COLOURS[r["rank"]], label=f"r={r['rank']} {r['curve']}")
    ax.set_xscale("log")
    ax.set_ylim(0.9, 1.35)
    ax.set_xlabel("naive height bound H", fontsize=8)
    ax.set_ylabel("N_E(H) / volume law", fontsize=8)
    ax.set_title(f"(E) Obstruction q1: count vs V_r (log H)^(r/2)/sqrt(Reg), {vl['run_id']}", loc="left", fontsize=9)
    ax.legend(fontsize=6, frameon=False, ncol=2, loc="upper right")


def panel_f(ax, he):
    for r in he["rows"]:
        ax.plot(r["p"], r["exponent"], marker="o", markersize=3.5, linewidth=1.0,
                color=RANK_COLOURS[r["rank"]], label=f"r={r['rank']} {r['curve']}")
    ax.set_xscale("log")
    ax.set_ylim(0.8, 1.9)
    ax.set_xlabel("prime p (resolved toy primes)", fontsize=8)
    ax.set_ylabel("log H_half / log p", fontsize=8)
    ax.set_title("(F) Half coverage is polynomial in p at toy scale (<= p^1.71)", loc="left", fontsize=9)
    ax.legend(fontsize=6, frameon=False, ncol=2, loc="lower right")


def main() -> None:
    doc = json.loads((HERE / "plot_data.json").read_text())
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "none",
                         "svg.hashsalt": doc["decision_id"]})
    fig = plt.figure(figsize=(11.0, 13.0))
    gsp = fig.add_gridspec(3, 2, height_ratios=[1.25, 1.0, 1.0], hspace=0.42, wspace=0.22)
    axes = {
        "A": fig.add_subplot(gsp[0, 0]),
        "B": fig.add_subplot(gsp[0, 1]),
        "C": fig.add_subplot(gsp[1, 0]),
        "D": fig.add_subplot(gsp[1, 1]),
        "E": fig.add_subplot(gsp[2, 0]),
        "F": fig.add_subplot(gsp[2, 1]),
    }
    panel_a(axes["A"], doc["coverage"])
    panel_b(axes["B"], doc["coverage"])
    panel_c(axes["C"], doc["growth_slopes"])
    panel_d(axes["D"], doc["h_half_slopes"])
    panel_e(axes["E"], doc["volume_law_ratio"])
    panel_f(axes["F"], doc["h_half_exponent"])
    for ax in axes.values():
        style(ax)
    fig.suptitle(f"{doc['experiment_id']} / {doc['hypothesis_id']}: evidence for {doc['decision_id']} "
                 f"({doc['evidence_id']})", x=0.02, ha="left", fontsize=11, color=INK)
    fig.text(0.02, 0.962, f"Runs {RUN_MAIN} (hmax 1e5) and {RUN_REP} (hmax 3e5); ladder 11a1..382623908456a1; "
             "p = 103..20011; toy tier. Values: plot_data.json (recorded manifests; reviewer values by key).",
             fontsize=7.5, color=MUTED, ha="left")
    fig.subplots_adjust(left=0.1, right=0.98, top=0.935, bottom=0.04)
    fig.savefig(HERE / "graph.svg", format="svg", metadata={"Date": None})


if __name__ == "__main__":
    main()
