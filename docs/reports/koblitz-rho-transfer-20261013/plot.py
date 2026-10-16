#!/usr/bin/env python3
"""Render the derived NIST model and fresh exploratory proxy measurements."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main() -> None:
    audit = json.loads((HERE / "audit.json").read_text())
    curves = audit["curves"]
    labels = [row["curve"] for row in curves]
    bits = [row["random_map_model"]["signed_tau_gain_vs_negation_bits"] for row in curves]
    factors = [row["random_map_model"]["signed_tau_gain_vs_negation_factor"] for row in curves]
    ladder = json.loads(
        (ROOT / "research/koblitz_rho_ladder_20261013/analysis.json").read_text()
    )["cells"]

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.5), constrained_layout=True)
    colors = ["#2f6f9f", "#377cae", "#4089bb", "#4996c8", "#52a3d5"]
    bars = axes[0].bar(labels, bits, color=colors)
    axes[0].set_ylabel("modelled rho-work bits beyond negation")
    axes[0].set_title("NIST K curves: derived random-map model")
    axes[0].set_ylim(0, 5.2)
    axes[0].grid(axis="y", alpha=0.25)
    for bar, factor in zip(bars, factors):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.08,
                     f"{factor:.2f}x", ha="center", va="bottom", fontsize=8)

    for a, color, marker in ((0, "#2f6f9f", "o"), (1, "#d17a22", "s")):
        selected = [cell for cell in ladder if cell["a"] == a]
        x = np.asarray([cell["m"] + (-0.22 if a == 0 else 0.22) for cell in selected])
        y = np.asarray([cell["walk_neg_over_frob"]["bits"] for cell in selected])
        lo = np.asarray(
            [cell["walk_neg_over_frob"]["bits_ci95_low"] for cell in selected]
        )
        hi = np.asarray(
            [cell["walk_neg_over_frob"]["bits_ci95_high"] for cell in selected]
        )
        axes[1].errorbar(
            x,
            y,
            yerr=[y - lo, hi - y],
            fmt=marker,
            capsize=4,
            color=color,
            label=f"observed a={a}",
        )
    model_m = np.linspace(22.5, 47.5, 160)
    axes[1].plot(
        model_m,
        0.5 * np.log2(model_m),
        color="#1e8449",
        linewidth=1.5,
        label="0.5 log₂(m) model",
    )
    axes[1].set_xticks([23, 31, 37, 41, 43, 47])
    axes[1].set_xlabel("field degree m")
    axes[1].set_ylabel("observed rho-work bits beyond negation")
    axes[1].set_title("Fresh 512-pair/cell toy ladder (95% BCa)")
    axes[1].grid(alpha=0.25)
    axes[1].legend(frameon=False, fontsize=8, loc="lower right")

    fig.suptitle("Signed-Frobenius rho: NIST model and exploratory proxy calibration", fontsize=12)
    fig.savefig(HERE / "rho-discount.svg")
    fig.savefig(HERE / "rho-discount.png", dpi=180)


if __name__ == "__main__":
    main()
