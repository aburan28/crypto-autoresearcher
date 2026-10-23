#!/usr/bin/env python3
"""Regenerate monodromy-frequencies.svg from plot-data.json (DEC-20261022-a0f165 decision report).

Three panels, every value read from plot-data.json, which records for each cell the review
artifact key it was read from (REVIEW-MONO-20261017-8aff64: TASK-20261017-8aff64 and
TASK-20261017-ccd10c, snapshot e3de77970e64):
  (A) ordered base, m = 4: identity-class (1^4) frequency per curve and source, Wilson 95%
      intervals for sampled rows, none for exhaustive rows; reference lines 1/4 (regular V_4)
      and 1/2 (order-2 competitor); exact finite-p expectations as separate markers.
  (B) symmetric base, m = 4: the five class frequencies per curve against the S_4 densities,
      classes mapped by label; the classes A_4 and D_4 cannot realise are marked.
  (C) OBS-1 reconciliation: g-split "2+1+1" counts on C1 and C2 split by squarefreeness.
No fitted curve and no extrapolation.

    python3 plot.py            # writes monodromy-frequencies.svg next to this file
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
S1, S2 = "#2a78d6", "#eb6834"  # reference palette slots 1 and 2: TASK-20261017-8aff64, TASK-20261017-ccd10c
INK, MUTED, GRID, REF = "#0b0b0b", "#52514e", "#e4e3df", "#8a8984"
CLASSES = ["1^4", "2^2", "2+1+1", "4", "3+1"]


def colour(src: str) -> str:
    return S1 if src.endswith("8aff64") else S2


def panel_a(ax, cells):
    rows = [c for c in cells if c["panel"] == "A"]
    y = list(range(len(rows)))[::-1]
    for yi, c in zip(y, rows):
        col = colour(c["source"])
        if c["ci95"]:
            lo, hi = c["ci95"]
            ax.plot([lo, hi], [yi, yi], color=col, linewidth=2)
        ax.plot([c["value"]], [yi], marker="o", markersize=7, color=col, markeredgecolor="#ffffff")
        tag = "exhaustive" if c["sampling"] == "exhaustive" else "sampled"
        ax.text(0.515, yi, f"{c['numerator']:,}/{c['denominator']:,}  ({tag})", va="center", fontsize=7.5, color=INK)
        e = c.get("expectation")
        if e:
            mk = "D" if "conditional" in e["label"] else "s"
            ax.plot([e["value"]], [yi], marker=mk, markersize=6, markerfacecolor="none", markeredgecolor=INK,
                    markeredgewidth=1.2, linestyle="none")
    for v, lab in ((0.25, "1/4  regular V_4 (Chebotarev)"), (0.5, "1/2  order-2 competitor")):
        ax.axvline(v, color=REF, linewidth=1.2, linestyle="--")
        ax.text(v, len(rows) - 0.3, lab, rotation=0, fontsize=7.5, color=MUTED, ha="center", va="bottom")
    ax.set_yticks(y)
    ax.set_yticklabels([c["curve"] for c in rows], fontsize=7.5, color=INK)
    ax.set_xlim(0.18, 0.80)
    ax.set_ylim(-0.8, len(rows) + 0.4)
    ax.set_xlabel("identity-class (1^4) frequency, ordered base, m = 4", color=INK, fontsize=8.5)
    ax.set_title("(A) Ordered base, m = 4", loc="left", fontsize=9.5, color=INK)
    h = [plt.Line2D([], [], marker="o", color=S1, linestyle="none", label="TASK-20261017-8aff64 (observed)"),
         plt.Line2D([], [], marker="o", color=S2, linestyle="none", label="TASK-20261017-ccd10c (observed)"),
         plt.Line2D([], [], marker="D", markerfacecolor="none", markeredgecolor=INK, linestyle="none",
                    label="exact, conditional on nondegeneracy (8aff64, derived)"),
         plt.Line2D([], [], marker="s", markerfacecolor="none", markeredgecolor=INK, linestyle="none",
                    label="exact over f != 0 (ccd10c, derived)"),
         plt.Line2D([], [], color=MUTED, linewidth=2, label="Wilson 95% interval (sampled rows)")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.4, -0.09), ncol=2, fontsize=7, frameon=False)


def panel_b(ax, cells, dens):
    rows = [c for c in cells if c["panel"] == "B"]
    curves = []
    for c in rows:
        if c["curve"] not in curves:
            curves.append(c["curve"])
    width = 0.7
    for ci, cv in enumerate(curves):
        off = -width / 2 + width * (ci + 0.5) / len(curves)
        for c in (r for r in rows if r["curve"] == cv):
            x = CLASSES.index(c["cls"]) + off
            col = colour(c["source"])
            mk = "^" if c["sampling"] == "exhaustive" else "o"
            if c["ci95"]:
                ax.plot([x, x], c["ci95"], color=col, linewidth=1.2)
            ax.plot([x], [c["value"]], marker=mk, markersize=4.5, color=col, linestyle="none")
    for i, cl in enumerate(CLASSES):
        ax.plot([i - 0.45, i + 0.45], [dens[cl]] * 2, color=INK, linewidth=1.4)
        ax.text(i - 0.45, dens[cl] + 0.012, f"S_4: {dens[cl]:.4f}", fontsize=7, color=MUTED, va="bottom")
    ax.set_xticks(range(len(CLASSES)))
    ax.set_xticklabels(["1^4", "2^2", "2+1+1\n(not in A_4)", "4\n(not in A_4)", "3+1\n(not in D_4)"], fontsize=8, color=INK)
    ax.set_ylim(0, 0.40)
    ax.set_ylabel("class frequency", color=INK, fontsize=8.5)
    ax.set_title(f"(B) Symmetric base, m = 4: {len(curves)} curve rows against the S_4 densities (black bars)",
                 loc="left", fontsize=9.5, color=INK)
    h = [plt.Line2D([], [], marker="o", color=S1, linestyle="none", label="8aff64, 6 curves (sampled)"),
         plt.Line2D([], [], marker="o", color=S2, linestyle="none", label="ccd10c, 4 curves (sampled)"),
         plt.Line2D([], [], marker="^", color=S2, linestyle="none", label="ccd10c C1 p=101 (exhaustive, admissible)"),
         plt.Line2D([], [], color=INK, linewidth=1.4, label="S_4 Chebotarev density (derived)")]
    ax.legend(handles=h, loc="upper left", fontsize=7, frameon=False)


def panel_c(ax, cells):
    rows = [c for c in cells if c["panel"] == "C"]
    curves = sorted({c["curve"] for c in rows})
    for i, cv in enumerate(curves):
        for j, c in enumerate(r for r in rows if r["curve"] == cv):
            col = S1 if j == 0 else S2
            ax.barh(i + (0.18 if j == 0 else -0.18), c["value"], height=0.32, color=col, edgecolor="#ffffff", linewidth=2)
            ax.text(c["value"] + 80, i + (0.18 if j == 0 else -0.18), f"{c['value']:,}  {c['cls'].split(', ')[1]}",
                    va="center", fontsize=7.5, color=INK)
    ax.set_yticks(range(len(curves)))
    ax.set_yticklabels(curves, fontsize=8, color=INK)
    ax.set_xlim(0, 11000)
    ax.set_xlabel("g-split \"2+1+1\" instances, exhaustive over the g-split block", color=INK, fontsize=8.5)
    ax.set_title("(C) OBS-1 reconciliation (TASK-20261017-8aff64 section 5)", loc="left", fontsize=9.5, color=INK)


def main() -> None:
    doc = json.loads((HERE / "plot-data.json").read_text())
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "svg.fonttype": "none",
                         "svg.hashsalt": "DEC-20261022-a0f165"})
    fig = plt.figure(figsize=(8.6, 12.4))
    gs = fig.add_gridspec(3, 1, height_ratios=[2.3, 1.4, 0.55], hspace=0.5)
    axes = [fig.add_subplot(gs[i]) for i in range(3)]
    panel_a(axes[0], doc["cells"])
    panel_b(axes[1], doc["cells"], doc["references"]["panel_B_S4_densities"])
    panel_c(axes[2], doc["cells"])
    for ax in axes:
        ax.grid(axis="x" if ax is not axes[1] else "y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(MUTED)
        ax.tick_params(colors=MUTED)
    fig.suptitle("Route-(a) review round REVIEW-MONO-20261017-8aff64: monodromy census frequencies",
                 x=0.02, ha="left", fontsize=10.5, color=INK)
    fig.text(0.02, 0.962, "Every value read by key from the committed review artifacts (snapshot e3de77970e64); "
             "see plot-data.json. Labels C1..C8 differ between the two reports.", fontsize=7.5, color=MUTED, ha="left")
    fig.subplots_adjust(left=0.34, right=0.97, top=0.935, bottom=0.04)
    fig.savefig(HERE / "monodromy-frequencies.svg", format="svg", metadata={"Date": None})


if __name__ == "__main__":
    main()
