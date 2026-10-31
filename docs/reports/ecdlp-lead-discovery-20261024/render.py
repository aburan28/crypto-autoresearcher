#!/usr/bin/env python3
"""Draw the arity / oracle-order threshold figure for the 2026-10-24 lead-discovery report.

Editable source for threshold-line.svg (research-visuals skill). The curves are the
closed forms proved in formal/CryptoResearch/IC/ArityOracleThreshold.lean:

  E*_all(m, k) = 2/(m+1-k)  for 0 <= k <= 2 (k <= m-2),  k/(m-1) for 2 <= k <= m-1,  1 beyond
  E*_one(m, k) = 2/(m+1-k)  for 0 <= k <= 1,               (1+k)/m for 1 <= k <= m-1

The measured points are the two sealed prime toy IC bounds (aburan28/crypto
docs/bounds/frontier.json, fit v2, 4 sizes, log2 r 17.7-24.0):
  ECBND1h9879c0aa348f  ic.pipeline oracle=subtract            alpha 1.0054 [0.8805, 1.0769]  (m = 2, k = 1)
  ECBND1h93b7a9d5c187  ic.pipeline oracle=mitm:negation_folded alpha 0.8407 [0.6459, 0.9528]  (m = 2, k = 1)
and the atlas row LEAD-ICP-generic-table-decomposition: mitm exponents 0.67 / 0.75 / 0.60 at
m = 3 / 4 / 5 (toy, 12-32 bits; no interval recorded there), model k = ceil(m/2).
Nothing in this figure is a measurement produced by this session.
"""
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def e_all(m, k):
    if k >= m - 1:
        return 1.0
    if k <= 2:
        return 2.0 / (m + 1 - k)
    return k / (m - 1)


def e_one(m, k):
    if k <= 1:
        return 2.0 / (m + 1 - k)
    if k >= m - 1:
        return max(1.0, (1 + k) / m)
    return (1 + k) / m


def main():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    ms = [2, 3, 4, 5, 6, 8, 10]
    ks = [i / 10 for i in range(0, 101)]
    for ax, fn, title in (
        (axes[0], e_all, "all-decompositions oracle: E*(m,k)"),
        (axes[1], e_one, "one-decomposition oracle: E*(m,k)"),
    ):
        for m in ms:
            ys = [fn(m, k) for k in ks if k <= m - 1]
            xs = [k for k in ks if k <= m - 1]
            ax.plot(xs, ys, label=f"m = {m}")
        ax.axhline(0.5, color="black", linestyle="--", linewidth=1, label="generic 1/2 (rho)")
        ax.set_xlabel("oracle enumeration order k  (attempt cost = B^k)")
        ax.set_title(title)
        ax.set_xlim(0, 6)
        ax.set_ylim(0.2, 1.05)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("cost exponent (base r)")
    # measured points (prime toy, sealed bounds), all at m = 2, k = 1 -> model 1.0
    axes[0].errorbar([1.0], [1.0054], yerr=[[1.0054 - 0.8805], [1.0769 - 1.0054]], fmt="o",
                     color="tab:red", capsize=3, label="ECBND1h9879c0aa348f subtract (m=2)")
    axes[0].errorbar([1.0], [0.8407], yerr=[[0.8407 - 0.6459], [0.9528 - 0.8407]], fmt="s",
                     color="tab:purple", capsize=3, label="ECBND1h93b7a9d5c187 mitm (m=2)")
    # atlas mitm exponents at m = 3,4,5 with model k = ceil(m/2) (no CI recorded)
    for m, alpha in ((3, 0.67), (4, 0.75), (5, 0.60)):
        axes[0].plot([math.ceil(m / 2)], [alpha], marker="^", color="tab:gray")
        axes[0].annotate(f"mitm m={m}", (math.ceil(m / 2), alpha), textcoords="offset points",
                         xytext=(5, -10), fontsize=7, color="tab:gray")
    axes[0].legend(fontsize=7, loc="lower right")
    axes[1].legend(fontsize=7, loc="lower right")
    fig.suptitle("Arity / oracle-order threshold (Lean: CryptoResearch.IC.ArityOracleThreshold); "
                 "points: sealed prime toy bounds and atlas mitm exponents, toy tier, not this session's data",
                 fontsize=9)
    fig.tight_layout()
    out = os.path.join(HERE, "threshold-line.svg")
    fig.savefig(out, format="svg")
    fig.savefig(os.path.join(HERE, "threshold-line.png"), dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main()
