#!/usr/bin/env python3
"""Render only archived Semaev counts and the scoped proof/evidence diagram."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROWS = json.loads((ROOT / "research/verification/ffd_semaev_results.json").read_text())
assert len(ROWS) == 8
assert all(sum(row["semaev_dist"].values()) == 10 for row in ROWS)


def counts_chart():
    labels = [f"n={row['n']}\nn′={row['nprime']}" for row in ROWS]
    twos = [row["semaev_dist"].get("2", 0) for row in ROWS]
    threes = [row["semaev_dist"].get("3", 0) for row in ROWS]
    fig, ax = plt.subplots(figsize=(10.4, 4.5), layout="constrained")
    x = range(len(ROWS))
    ax.bar(x, twos, color="#326b86", label="recorded d_ff = 2")
    ax.bar(x, threes, bottom=twos, color="#c57b41", label="recorded d_ff = 3")
    ax.set_xticks(list(x), labels)
    ax.set_ylim(0, 11.2)
    ax.set_yticks(range(0, 11, 2))
    ax.set_ylabel("Semaev draws (count)")
    ax.set_title("Toy first-fall outcomes: 70 of 80 at degree 2, 10 at degree 3")
    ax.legend(loc="upper center", ncol=2, frameon=False)
    ax.text(0, -0.25, "Source: research/verification/ffd_semaev_results.json; 10 draws per cell; no per-draw intervals recorded.",
            transform=ax.transAxes, fontsize=8, color="#475569")
    fig.savefig(HERE / "fall_counts.svg", format="svg")
    plt.close(fig)


def boundary_diagram():
    fig, ax = plt.subplots(figsize=(11, 4.5), layout="constrained")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.5)
    ax.axis("off")

    def box(x, y, width, height, title, body, fill):
        patch = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.08,rounding_size=0.12",
                               linewidth=1.2, edgecolor="#29475c", facecolor=fill)
        ax.add_patch(patch)
        ax.text(x + 0.14, y + height - 0.31, title, fontsize=11, fontweight="bold", va="top")
        ax.text(x + 0.14, y + height - 0.80, body, fontsize=8.8, va="top", linespacing=1.5)

    def arrow(x1, y1, x2, y2, color="#29475c", style="-"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=14, linewidth=1.7,
                                     linestyle=style, color=color))

    box(0.2, 2.42, 3.05, 1.52, "Archived toy outcomes", "8 cells × 10 draws\n70 d_ff=2; 10 d_ff=3", "#e8f1f5")
    box(3.98, 2.42, 3.05, 1.52, "Lean trace lemma", "Quadratic coefficients\nare annihilated", "#e4f2e9")
    box(7.77, 2.42, 3.02, 1.52, "Full first-fall claim", "Needs a nonzero residue\nand a filtration bridge", "#fff0e2")
    ax.text(3.62, 3.18, "separate\nevidence", ha="center", va="center",
            fontsize=8.2, color="#475569")
    arrow(7.08, 3.18, 7.71, 3.18, color="#bb6b34", style="--")
    ax.text(7.39, 3.49, "OPEN", ha="center", fontsize=8.5,
            fontweight="bold", color="#a75628")
    box(0.2, 0.34, 4.9, 1.16, "Orbit pair-index theorem", "Exact modular lookup for already enumerated representatives", "#e4f2e9")
    box(5.88, 0.34, 4.91, 1.16, "Orbit experiment conclusions", "Enumeration, interpolation and ECDLP cost remain separate", "#fff0e2")
    arrow(5.14, 0.92, 5.82, 0.92, color="#bb6b34", style="--")
    ax.text(5.49, 1.23, "OPEN", ha="center", fontsize=8.5,
            fontweight="bold", color="#a75628")
    fig.savefig(HERE / "proof_boundary.svg", format="svg")
    plt.close(fig)


if __name__ == "__main__":
    counts_chart()
    boundary_diagram()
    print("rendered", HERE / "fall_counts.svg", HERE / "proof_boundary.svg")
