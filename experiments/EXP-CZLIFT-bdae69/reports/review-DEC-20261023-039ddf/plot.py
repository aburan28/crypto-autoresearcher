#!/usr/bin/env python3
"""Regenerate graph.svg from plot_data.json (DEC-20261023-039ddf decision report).

Two panels, every plotted value read from plot_data.json, which names for each
value the run manifest or review artifact it comes from:
  (A) per seed (RUN-CZLIFT-0cefcd, RUN-CZLIFT-a5c1da): Teichmuller, naive and
      random-Hensel success counts out of n = 1600, the naive bar split into
      the sub-p region (g^d < p, all succeed) and the rest region
      (g^d >= p^2); band rows (p <= g^d < p^2) are annotated (0 successes,
      impossible by derivation). Reference lines: the 1/p expected count n*m
      and the frozen 4-standard-error acceptance bound n*m + 4 sqrt(n m (1-m)),
      both derived here from the recorded n and m = reference_inv_p; diamond
      markers: the exact conditional expectation for the naive section
      (red-team r2_nulls).
  (B) pooled over both seeds: observed / expected rate ratios with the red
      team's 95% intervals (intervals_output.json), against ratio 1.
No fitted curve and no extrapolation.

    python3 plot.py            # writes graph.svg next to this file
"""

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
INK, MUTED, GRID, REF = "#0b0b0b", "#52514e", "#e4e3df", "#8a8984"
C_TEICH, C_SUBP, C_REST, C_HENS = "#7a7a7a", "#c0392b", "#eb6834", "#2a78d6"
SECTIONS = ("teichmuller", "naive", "hensel")
OFFSETS = {"teichmuller": -0.28, "naive": 0.0, "hensel": 0.28}
WIDTH = 0.24


def panel_a(ax, seeds):
    for gi, s in enumerate(seeds):
        n, m = s["n"], s["reference_inv_p"]
        mean = n * m
        bound = mean + 4.0 * math.sqrt(n * m * (1.0 - m))
        counts = s["success_counts"]
        reg = s["naive_regions"]
        # Teichmuller and Hensel bars
        for sec, col in (("teichmuller", C_TEICH), ("hensel", C_HENS)):
            x = gi + OFFSETS[sec]
            ax.bar(x, counts[sec], width=WIDTH, color=col, edgecolor="#ffffff", linewidth=1)
            ax.text(x, counts[sec] + 0.35, f"{counts[sec]}/{n}", ha="center", va="bottom", fontsize=7.5, color=INK)
        # naive bar, stacked by region
        x = gi + OFFSETS["naive"]
        sub, rest = reg["subp"]["successes"], reg["rest"]["successes"]
        ax.bar(x, sub, width=WIDTH, color=C_SUBP, edgecolor="#ffffff", linewidth=1)
        ax.bar(x, rest, width=WIDTH, bottom=sub, color=C_REST, edgecolor="#ffffff", linewidth=1)
        assert sub + reg["band"]["successes"] + rest == counts["naive"], "region split must sum to the recorded count"
        ax.text(x, sub / 2.0, f"sub-p\n{sub}/{reg['subp']['rows']}", ha="center", va="center", fontsize=6.5, color="#ffffff")
        ax.text(x + WIDTH / 2 + 0.02, sub + rest / 2.0,
                f"rest {rest}/{reg['rest']['rows']}\n(exact null {reg['rest']['expected_exact_conditional']:.2f})",
                ha="left", va="center", fontsize=6.5, color=INK)
        ax.text(x, counts["naive"] + 0.35,
                f"{counts['naive']}/{n}\nband {reg['band']['successes']}/{reg['band']['rows']}",
                ha="center", va="bottom", fontsize=7.5, color=INK)
        exact = s["naive_total_expected_exact_conditional"]
        ax.plot([x], [exact], marker="D", markersize=6.5, markerfacecolor="none", markeredgecolor=INK,
                markeredgewidth=1.3, linestyle="none", zorder=5)
        # reference lines over the seed group
        lo, hi = gi - 0.45, gi + 0.45
        ax.plot([lo, hi], [mean, mean], color=INK, linewidth=1.3, linestyle="-")
        ax.plot([lo, hi], [bound, bound], color=REF, linewidth=1.3, linestyle="--")
        ax.text(lo, mean - 0.25, f"n x mean 1/p = {mean:.2f}", fontsize=6.5, color=MUTED, va="top")
        ax.text(lo, bound + 0.2, f"4-SE bound {bound:.1f}", fontsize=6.5, color=MUTED, va="bottom")
    ax.set_xticks(range(len(seeds)))
    ax.set_xticklabels([f"seed {s['seed']}\n{s['run_id']}" for s in seeds], fontsize=8, color=INK)
    ax.set_xlim(-0.6, len(seeds) - 0.4)
    ax.set_ylim(0, 32)
    ax.set_ylabel("pairs with Smart-style ratio = d mod p (of n = 1600)", fontsize=8.5, color=INK)
    ax.set_title("(A) Success counts per seed against the 1/p expectation and the frozen 4-SE bound",
                 loc="left", fontsize=9.5, color=INK)
    h = [plt.Rectangle((0, 0), 1, 1, color=C_TEICH, label="Teichmuller (ratio never defined)"),
         plt.Rectangle((0, 0), 1, 1, color=C_SUBP, label="naive, sub-p region g^d < p (certain by D-3)"),
         plt.Rectangle((0, 0), 1, 1, color=C_REST, label="naive, rest region g^d >= p^2"),
         plt.Rectangle((0, 0), 1, 1, color=C_HENS, label="random Hensel"),
         plt.Line2D([], [], color=INK, linewidth=1.3, label="expected at mean 1/p (n*m, recorded m)"),
         plt.Line2D([], [], color=REF, linewidth=1.3, linestyle="--", label="frozen acceptance bound |z| <= 4"),
         plt.Line2D([], [], marker="D", markerfacecolor="none", markeredgecolor=INK, linestyle="none",
                    label="naive exact conditional null (g^d mod p^2 < p)")]
    ax.legend(handles=h, loc="upper left", fontsize=7, frameon=False, ncol=2)


def panel_b(ax, ratios):
    y = list(range(len(ratios)))[::-1]
    for yi, r in zip(y, ratios):
        col = C_HENS if r["label"].startswith("Hensel") else (C_TEICH if r["label"].startswith("Teich") else C_REST)
        if r["ci95"]:
            ax.plot(r["ci95"], [yi, yi], color=col, linewidth=2)
        ax.plot([r["ratio"]], [yi], marker="o", markersize=6.5, color=col, markeredgecolor="#ffffff", linestyle="none")
        ci = f"  [{r['ci95'][0]:.2f}, {r['ci95'][1]:.2f}]" if r["ci95"] else "  (no interval)"
        ax.text(9.3, yi, f"{r['obs']} / {r['exp']:.2f} = {r['ratio']:.2f}{ci}", va="center", fontsize=7, color=INK)
    ax.axvline(1.0, color=INK, linewidth=1.1, linestyle="--")
    ax.text(1.05, len(ratios) - 0.45, "ratio 1 (null)", fontsize=7, color=MUTED, va="bottom")
    ax.set_yticks(y)
    ax.set_yticklabels([r["label"] for r in ratios], fontsize=7.5, color=INK)
    ax.set_xlim(-0.2, 9.2)
    ax.set_ylim(-0.7, len(ratios) - 0.1)
    ax.set_xlabel("observed / expected successes, pooled over both seeds (3200 pairs), red-team 95% interval",
                  fontsize=8.5, color=INK)
    ax.set_title("(B) Pooled rate ratios: the naive excess vanishes against the exact null",
                 loc="left", fontsize=9.5, color=INK)


def main() -> None:
    doc = json.loads((HERE / "plot_data.json").read_text())
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "none",
                         "svg.hashsalt": "DEC-20261023-039ddf"})
    fig = plt.figure(figsize=(8.6, 9.6))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.6, 1.0], hspace=0.42)
    ax_a, ax_b = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    panel_a(ax_a, doc["seeds"])
    panel_b(ax_b, doc["pooled_rate_ratios"])
    for ax in (ax_a, ax_b):
        ax.grid(axis="y" if ax is ax_a else "x", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(MUTED)
        ax.tick_params(colors=MUTED)
    fig.suptitle("EXP-CZLIFT-bdae69 (H-CZLIFT-d37231): Smart-style recovery on F_p^*, 50 < p < 2000, k = 4",
                 x=0.02, ha="left", fontsize=10.5, color=INK)
    fig.text(0.02, 0.955, "Values from the run manifests and the committed review artifacts (see plot_data.json); "
             "g = smallest primitive root as frozen in run.py.", fontsize=7.5, color=MUTED, ha="left")
    fig.subplots_adjust(left=0.24, right=0.80, top=0.92, bottom=0.07)
    fig.savefig(HERE / "graph.svg", format="svg", metadata={"Date": None})


if __name__ == "__main__":
    main()
