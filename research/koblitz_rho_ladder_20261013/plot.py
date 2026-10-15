#!/usr/bin/env python3
"""Render the fresh paired Koblitz rho calibration ladder."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
COLORS = {0: "#2f6f9f", 1: "#d17a22"}


def main() -> None:
    analysis = json.loads((HERE / "analysis.json").read_text())
    cells = analysis["cells"]
    labels = [
        f"m={cell['m']}, μ={cell['mu']:+d}\nlog₂r={cell['log2_r']:.1f}"
        for cell in cells
    ]
    x = np.arange(len(cells), dtype=float)
    observed = np.asarray([cell["walk_neg_over_frob"]["bits"] for cell in cells])
    low = np.asarray(
        [cell["walk_neg_over_frob"]["bits_ci95_low"] for cell in cells]
    )
    high = np.asarray(
        [cell["walk_neg_over_frob"]["bits_ci95_high"] for cell in cells]
    )
    model = np.asarray([cell["model"]["rho_bits"] for cell in cells])
    residual = observed - model
    log2_r = np.asarray([cell["log2_r"] for cell in cells])

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.9), constrained_layout=True)

    axes[0].errorbar(
        x,
        observed,
        yerr=[observed - low, high - observed],
        fmt="none",
        ecolor="#36454f",
        elinewidth=1.5,
        capsize=4,
        zorder=1,
    )
    for a in (0, 1):
        idx = [i for i, cell in enumerate(cells) if cell["a"] == a]
        axes[0].scatter(
            x[idx],
            observed[idx],
            s=55,
            color=COLORS[a],
            label=f"observed a={a}",
            zorder=3,
        )
    axes[0].scatter(
        x,
        model,
        marker="x",
        s=65,
        linewidth=1.8,
        color="#1e8449",
        label="0.5 log₂(m) model",
        zorder=4,
    )
    axes[0].set_xticks(x, labels)
    axes[0].tick_params(axis="x", labelsize=8)
    axes[0].set_ylabel("rho-work bits: log₂(mean Wneg / mean Wτ)")
    axes[0].set_title("Paired walk-operation result (95% BCa)")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(frameon=False, fontsize=8, loc="lower right")

    axes[1].axhspan(-0.15, 0.15, color="#a9cce3", alpha=0.25, label="±0.15-bit marker")
    axes[1].axhline(0.0, color="#1e8449", linewidth=1.2)
    for a in (0, 1):
        idx = [i for i, cell in enumerate(cells) if cell["a"] == a]
        axes[1].scatter(
            log2_r[idx],
            residual[idx],
            s=60,
            color=COLORS[a],
            label=f"a={a}",
            zorder=3,
        )
    for cell, xr, yr in zip(cells, log2_r, residual):
        at_right_edge = xr > max(log2_r) - 1.0
        axes[1].annotate(
            f"m{cell['m']}",
            (xr, yr),
            xytext=((-4 if at_right_edge else 4), 5),
            textcoords="offset points",
            fontsize=8,
            ha=("right" if at_right_edge else "left"),
        )
    axes[1].set_xlabel("prime-subgroup size log₂(r)")
    axes[1].set_ylabel("observed minus model (bits)")
    axes[1].set_title("Finite-size departure versus subgroup scale")
    axes[1].grid(alpha=0.25)
    axes[1].legend(frameon=False, fontsize=8, loc="lower right")

    fig.suptitle(
        "Exploratory signed-Frobenius rho ladder — 512 paired targets per cell",
        fontsize=12,
    )
    fig.text(
        0.5,
        -0.015,
        "Walk operations exclude setup; canonicalisations are counted but unpriced. "
        "Toy calibration only, not ledger evidence or a weak-curve result.",
        ha="center",
        fontsize=8,
        color="#555555",
    )
    fig.savefig(HERE / "ladder.svg", bbox_inches="tight")
    fig.savefig(HERE / "ladder.png", dpi=180, bbox_inches="tight")


if __name__ == "__main__":
    main()
