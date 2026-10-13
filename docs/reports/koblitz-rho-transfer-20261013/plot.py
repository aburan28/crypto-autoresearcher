#!/usr/bin/env python3
"""Render the derived NIST model and archived proxy measurements."""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent


def main() -> None:
    audit = json.loads((HERE / "audit.json").read_text())
    curves = audit["curves"]
    labels = [row["curve"] for row in curves]
    bits = [row["random_map_model"]["signed_tau_gain_vs_negation_bits"] for row in curves]
    factors = [row["random_map_model"]["signed_tau_gain_vs_negation_factor"] for row in curves]

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.5), constrained_layout=True)
    colors = ["#2f6f9f", "#377cae", "#4089bb", "#4996c8", "#52a3d5"]
    bars = axes[0].bar(labels, bits, color=colors)
    axes[0].set_ylabel("derived bits beyond negation")
    axes[0].set_title("NIST K curves: exact random-map factor")
    axes[0].set_ylim(0, 5.2)
    axes[0].grid(axis="y", alpha=0.25)
    for bar, factor in zip(bars, factors):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.08,
                     f"{factor:.2f}x", ha="center", va="bottom", fontsize=8)

    proxy_m = [37, 41]
    measured = [5.73, 6.36]
    low = [5.62, 6.20]
    high = [5.84, 6.53]
    predicted = [math.sqrt(m) for m in proxy_m]
    x = range(len(proxy_m))
    axes[1].errorbar(x, measured,
                     yerr=[[v - lo for v, lo in zip(measured, low)],
                           [hi - v for v, hi in zip(measured, high)]],
                     fmt="o", capsize=5, color="#b03a2e", label="archived measured steps")
    axes[1].scatter(x, predicted, marker="x", s=75, color="#1e8449", label="sqrt(m) model")
    axes[1].set_xticks(list(x), ["m=37\n90% CI", "m=41\n95% CI"])
    axes[1].set_ylabel("negation steps / signed-tau steps")
    axes[1].set_title("Standalone proxy studies (not ledger evidence)")
    axes[1].set_ylim(5.2, 6.9)
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(frameon=False, fontsize=8)

    fig.suptitle("Signed-Frobenius rho: structural NIST discount and bounded proxy evidence", fontsize=12)
    fig.savefig(HERE / "rho-discount.svg")
    fig.savefig(HERE / "rho-discount.png", dpi=180)


if __name__ == "__main__":
    main()
