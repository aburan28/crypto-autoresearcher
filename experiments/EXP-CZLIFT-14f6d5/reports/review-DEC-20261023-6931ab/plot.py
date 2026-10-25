#!/usr/bin/env python3
"""Draw graph.svg for the DEC-20261023-6931ab decision report (EXP-CZLIFT-14f6d5).

Every value is read from plot_data.json beside this file. Each value there is a
recorded run value (raw-result.json counts, manifest metrics), a reviewer value
read by key from the committed validation-20261022 / redteam-20261023
artifacts, or the Hasse bound stated in plot_data.json. This script computes
nothing new except log10 of the recorded |discriminant| for the x axis of
panel A: no sampling, no fit, no extrapolation.

Panels:
  (A) N_E(3e5) per curve against log10 |disc|, coloured by rank lower bound,
      with coefficient-matched random curves
  (B) N_E(H) against H: run curves, Elkies-Watkins rows, the translation
      mutation of the rank-7 curve and the rank-0 proves-too-much objects
  (C) coverage median per run against the frozen band, its unreachable upper
      part, the null bands and the subgroup-confinement alternatives
  (D) the clauses that cannot fail: S3 attainable maximum against 0.05, and
      S4 record-curve n against the Hasse lower bound on N_p / 2

    python3 plot.py            # writes graph.svg next to this file
"""

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
INK, MUTED, GRID, BAND, DEAD = "#0b0b0b", "#52514e", "#e4e3df", "#d9ead3", "#f4cccc"
RANK_COLOURS = {0: "#7f7f7f", 7: "#e377c2", 8: "#1f77b4", 9: "#ff7f0e", 10: "#2ca02c", 11: "#d62728"}
RUN_COLOURS = {"RUN-CZLIFT-ca7450": "#2a78d6", "RUN-CZLIFT-b1dce4": "#eb6834"}


def style(ax):
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=7.5)


def panel_a(ax, cd):
    xs = {}
    for c in cd["curves"]:
        x = math.log10(int(c["abs_disc"]))
        xs[c["label"]] = x
        col = RANK_COLOURS[c["rank_lb"]]
        if c["run_curve"]:
            ax.plot([x], [c["N"]], marker="D", markersize=8, color=col, markeredgecolor=INK, linestyle="none")
        else:
            ax.plot([x], [c["N"]], marker="o", markersize=7, color=col, mfc="white", mew=1.6, linestyle="none")
        ax.annotate(f"r>={c['rank_lb']}", (x, c["N"]), textcoords="offset points", xytext=(6, 4),
                    fontsize=6.5, color=INK)
    for m in cd["matched_null"]:
        x = xs[m["matched_to"]]
        ax.plot([x], [m["max"]], marker="x", markersize=7, color=MUTED, linestyle="none")
        ax.annotate(f"max of {m['n_curves']} random", (x, m["max"]), textcoords="offset points",
                    xytext=(6, -9), fontsize=6, color=MUTED)
    ax.set_yscale("log")
    ax.set_ylim(0.6, 30000)
    ax.set_xlabel("log10 |discriminant|", fontsize=8)
    ax.set_ylabel(f"N_E(H = {cd['H']:.0e}) (O and +-P counted)", fontsize=8)
    sp = cd["spearman"]
    ax.set_title("(A) Counts order by discriminant, not rank", loc="left", fontsize=9)
    stats = (f"Spearman N(1e5): log|disc| {sp['N1e5_vs_log_abs_disc']:.2f}, rank {sp['N1e5_vs_rank_lb']:.2f}\n"
             f"Spearman N(3e5): log|disc| {sp['N3e5_vs_log_abs_disc']:.2f}, rank {sp['N3e5_vs_rank_lb']:.2f}")
    h = [plt.Line2D([], [], marker="D", color=MUTED, markeredgecolor=INK, linestyle="none",
                    label="run curve (recorded, RUN-CZLIFT-b1dce4)"),
         plt.Line2D([], [], marker="o", color=MUTED, mfc="white", linestyle="none",
                    label="Elkies-Watkins row (red team)"),
         plt.Line2D([], [], marker="x", color=MUTED, linestyle="none",
                    label="coefficient-matched random curves, max (red team)")]
    h += [plt.Line2D([], [], marker="s", color=RANK_COLOURS[r], linestyle="none", label=f"rank >= {r}")
          for r in (7, 8, 9, 10, 11)]
    ax.legend(handles=h, fontsize=6, frameon=False, loc="upper right", ncol=2, title=stats, title_fontsize=6)


def panel_b(ax, gr):
    for s in gr["series"]:
        col = RANK_COLOURS[s["rank_lb"]]
        if s["kind"] == "run":
            ax.plot(s["H"], s["N"], marker="D", markersize=4, linewidth=1.6, color=col, label=s["label"])
        elif s["kind"] == "reviewer":
            ax.plot(s["H"], s["N"], marker="o", markersize=4, mfc="white", linewidth=1.0, linestyle="--",
                    color=col, label=s["label"])
        elif s["kind"] == "mutation":
            ax.plot(s["H"], s["N"], marker="v", markersize=6, linewidth=1.2, linestyle=":", color=col,
                    label=s["label"])
        else:
            ax.plot(s["H"], s["N"], marker="s", markersize=3, linewidth=1.0, linestyle="-.", color=MUTED,
                    label=s["label"])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.6, 30000)
    ax.set_xlabel("naive x-height bound H", fontsize=8)
    ax.set_ylabel("N_E(H)", fontsize=8)
    ax.set_title("(B) One count, many readings: model and window, not rank", loc="left", fontsize=9)
    ax.legend(fontsize=5.8, frameon=False, loc="upper left")


def panel_c(ax, cov):
    lo, hi = cov["frozen_success_band"]
    rows = []
    for run in cov["runs"]:
        for b in run["bands"]:
            rows.append((run, b))
    n = len(rows)
    top_reach = max(r["attainable_max_median"] for r in cov["runs"])
    ax.axvspan(lo, hi, color=BAND, zorder=0)
    ax.axvspan(top_reach, hi, color=DEAD, zorder=0)
    for i, (run, b) in enumerate(rows):
        y = n - 1 - i
        col = RUN_COLOURS[run["run_id"]]
        ax.plot(b["band"], [y, y], color=col, linewidth=3, solid_capstyle="butt")
        ax.plot([b["centre"]], [y], marker="o", markersize=3.5, color=INK, linestyle="none")
        if b["centre"] < 0.95:
            ax.text(b["band"][1] + 0.004, y, f"{run['label']}: {b['label']}", fontsize=5.8, color=INK,
                    ha="left", va="center")
        else:
            ax.text(b["band"][0] - 0.004, y, f"{run['label']}: {b['label']}", fontsize=5.8, color=INK,
                    ha="right", va="center")
    for run in cov["runs"]:
        col = RUN_COLOURS[run["run_id"]]
        ax.axvline(run["observed_median"], color=col, linewidth=1.2, linestyle="-")
        ax.axvline(run["hyp_definition_median"], color=col, linewidth=0.8, linestyle=":")
        ax.axvline(run["attainable_max_median"], color=col, linewidth=0.8, linestyle="--")
    ax.set_yticks([])
    ax.set_xlim(0.72, 1.23)
    ax.set_ylim(-0.8, n + 6.5)
    ax.set_xlabel("coverage-ratio median (distinct / uniform model)", fontsize=8)
    ax.set_title("(C) Coverage: band edge 1.2 unreachable; uniform null rejected", loc="left", fontsize=9)
    h = [plt.Rectangle((0, 0), 1, 1, color=BAND, label=f"frozen success band [{lo}, {hi}]"),
         plt.Rectangle((0, 0), 1, 1, color=DEAD, label="unreachable by any point set (D1)")]
    for run in cov["runs"]:
        col = RUN_COLOURS[run["run_id"]]
        h += [plt.Line2D([], [], color=col, linestyle="-",
                         label=f"{run['run_id']} observed {run['observed_median']:.4f} ({run['cells']} cells)"),
              plt.Line2D([], [], color=col, linestyle=":",
                         label=f"  hypothesis cell set {run['hyp_definition_median']:.4f} ({run['hyp_cells']} cells)"),
              plt.Line2D([], [], color=col, linestyle="--",
                         label=f"  attainable maximum {run['attainable_max_median']:.4f}")]
    h += [plt.Line2D([], [], color=MUTED, linewidth=3, label="null / alternative band, dot = centre")]
    ax.legend(handles=h, fontsize=5.6, frameon=False, loc="upper right")


def panel_d(ax3, ax4, uc):
    s3 = uc["S3"]
    labels = [r["run_id"] for r in s3["rows"]]
    ys = range(len(labels))
    for y, r in zip(ys, s3["rows"]):
        col = RUN_COLOURS[r["run_id"]]
        ax3.barh([y + 0.18], [r["attainable_max"]], height=0.32, color=col, alpha=0.55)
        ax3.barh([y - 0.18], [max(r["observed"], 0.0004)], height=0.32, color=col)
        ax3.text(r["attainable_max"] + 0.001, y + 0.18, f"max {r['attainable_max']:.4f}", fontsize=6,
                 va="center", color=INK)
        ax3.text(0.0015, y - 0.18, f"observed {r['observed']}", fontsize=6, va="center", color=INK)
    ax3.axvline(s3["threshold"], color=INK, linewidth=1.0, linestyle="--")
    ax3.text(s3["threshold"], len(labels) - 0.45, f"fail at >= {s3['threshold']}", fontsize=6, ha="right",
             color=INK)
    ax3.set_yticks(list(ys))
    ax3.set_yticklabels(labels, fontsize=6)
    ax3.set_xlim(0, 0.06)
    ax3.set_ylim(-0.6, len(labels) + 0.2)
    ax3.set_xlabel("frac of cells with ratio > 1.5", fontsize=7.5)
    ax3.set_title("(D) S3 cannot fail", loc="left", fontsize=9)

    s4 = uc["S4"]
    bound = s4["half_Np_lower_bound_p_ge_1000"]
    for y, r in enumerate(s4["rows"]):
        col = RUN_COLOURS[r["run_id"]]
        ax4.barh([y], [r["n_at_hmax"]], height=0.6, color=col)
        ax4.text(r["n_at_hmax"] + 6, y, f"{r['n_at_hmax']}", fontsize=6, va="center", color=INK)
    ax4.axvline(bound, color=INK, linewidth=1.0, linestyle="--")
    ax4.text(bound - 5, len(s4["rows"]) - 0.4, f"N_p/2 >= {bound} (Hasse, p >= 1000)", fontsize=6,
             ha="right", color=INK)
    ax4.set_yticks(range(len(s4["rows"])))
    ax4.set_yticklabels([f"{r['curve']}\n{r['run_id']}" for r in s4["rows"]], fontsize=5.6)
    ax4.set_xlim(0, 520)
    ax4.set_ylim(-0.6, len(s4["rows"]) + 0.4)
    ax4.set_xlabel("record-curve points n at hmax (distinct <= n)", fontsize=7.5)
    ax4.set_title("(D') S4 cannot fail", loc="left", fontsize=9)


def main() -> None:
    doc = json.loads((HERE / "plot_data.json").read_text())
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "none",
                         "svg.hashsalt": doc["decision_id"]})
    fig = plt.figure(figsize=(11.0, 10.5))
    gsp = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], hspace=0.32, wspace=0.24)
    ax_a = fig.add_subplot(gsp[0, 0])
    ax_b = fig.add_subplot(gsp[0, 1])
    ax_c = fig.add_subplot(gsp[1, 0])
    sub = gsp[1, 1].subgridspec(2, 1, hspace=0.75)
    ax_d3 = fig.add_subplot(sub[0, 0])
    ax_d4 = fig.add_subplot(sub[1, 0])
    panel_a(ax_a, doc["counts_vs_disc"])
    panel_b(ax_b, doc["growth"])
    panel_c(ax_c, doc["coverage"])
    panel_d(ax_d3, ax_d4, doc["unfailable_clauses"])
    for ax in (ax_a, ax_b, ax_c, ax_d3, ax_d4):
        style(ax)
    fig.suptitle(f"{doc['experiment_id']} / {doc['hypothesis_id']}: evidence for {doc['decision_id']} "
                 f"({doc['evidence_id']})", x=0.02, ha="left", fontsize=11, color=INK)
    fig.text(0.02, 0.955, "Runs RUN-CZLIFT-ca7450 (hmax 1e5) and RUN-CZLIFT-b1dce4 (hmax 3e5); reduced minimal "
             "models; 16 primes 103..20011; toy tier. Exact counts (no sampling error). Values: plot_data.json "
             "(recorded run values; reviewer values by key).", fontsize=7, color=MUTED, ha="left")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.06)
    fig.savefig(HERE / "graph.svg", format="svg", metadata={"Date": None})


if __name__ == "__main__":
    main()
