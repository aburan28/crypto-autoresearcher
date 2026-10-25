#!/usr/bin/env python3
"""Decision-report graph for DEC-20261023-36b4f0 (EXP-CZLIFT-ae0a13).

Reads plot_data.json (recorded producer metrics and committed red-team outputs
only) and writes graph.svg next to this file. Derived quantities: success
counts = success_rate x n (asserted integral) and Wilson 95 % intervals.

Usage: python3 plot.py
"""
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
Z95 = 1.959963984540054


def wilson(x, n, z=Z95):
    """Wilson score 95 % interval for x successes in n trials."""
    if n == 0:
        return 0.0, 1.0
    phat = x / n
    denom = 1.0 + z * z / n
    centre = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def count_of(rate, n):
    x = rate * n
    k = round(x)
    assert abs(x - k) < 1e-6, f"success_rate x n = {x} is not integral"
    return int(k)


def panel_a(ax, d):
    first = True
    for c in d["curves"]:
        ax.plot(c["K"], c["v_tor"], "o-", color="tab:blue", alpha=0.7,
                label="s_tor (3 curves, red team)" if first else None)
        ax.plot(c["K"], c["v_naive"], "s--", color="tab:orange", alpha=0.7,
                label="naive section (3 curves, red team)" if first else None)
        first = False
    ks = [2, 8]
    ax.plot(ks, ks, ":", color="grey", label="v = k (vanishing at precision k)")
    pp = d["producer_point"]
    ax.plot([pp["k"]], [pp["v_tor"]], "*", color="black", markersize=13,
            label=f"producer, k = 4: {pp['pairs_with_v_tor_equal_k']}/{pp['pairs']} pairs")
    ax.set_xlabel("working precision k")
    ax.set_ylabel("v_p( z([n] s(P)) )")
    ax.set_title("(a) Smart functional on s_tor vanishes to precision k", fontsize=9)
    ax.set_xticks([2, 3, 4, 6, 8])
    ax.legend(fontsize=6.5, loc="upper left")


def panel_b(ax, d):
    cells = d["cells"]
    floors = {(r["run_id"], r["arm"]): r for r in d["frozen_floor"]["rows"]}
    groups = []
    for c in cells:
        key = (c["run_id"], c["seed"], c["arm"])
        if key not in groups:
            groups.append(key)
    colours = {"hensel_random": "tab:green", "naive": "tab:purple", "teichmuller": "tab:red"}
    offsets = {"hensel_random": -0.22, "naive": 0.0, "teichmuller": 0.22}
    plotted = set()
    for gi, (run_id, seed, arm) in enumerate(groups):
        for c in cells:
            if (c["run_id"], c["arm"]) != (run_id, arm):
                continue
            ref = c["reference_inv_p"]
            x = count_of(c["success_rate"], c["n"])
            lo, hi = wilson(x, c["n"])
            ratio = c["success_rate"] / ref
            xpos = gi + offsets[c["section"]]
            lab = c["section"] if c["section"] not in plotted else None
            plotted.add(c["section"])
            ax.errorbar([xpos], [ratio], yerr=[[ratio - lo / ref], [hi / ref - ratio]],
                        fmt="o", color=colours[c["section"]], capsize=2, markersize=4, label=lab)
            ax.annotate(f"{x}/{c['n']}", (xpos, hi / ref), fontsize=5.5,
                        ha="center", va="bottom", rotation=90, xytext=(0, 2),
                        textcoords="offset points")
        fl = floors[(run_id, arm)]
        ax.hlines(fl["multiple_of_reference"], gi - 0.35, gi + 0.35, colors="black",
                  linewidth=2, label="frozen 4-sigma floor" if gi == 0 else None)
    ax.axhline(1.0, color="grey", linestyle="--", linewidth=1, label="null: rate = mean 1/p")
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([f"{arm.replace('_', ' ')}\nseed {seed}" for (_r, seed, arm) in groups], fontsize=6.5)
    ax.set_ylabel("success rate / mean(1/p)  (Wilson 95 %)")
    ax.set_ylim(0, 9.5)
    ax.set_title("(b) Identity-readout success vs 1/p (RUN-CZLIFT-dab752, -5b2581)", fontsize=9)
    ax.legend(fontsize=6, loc="upper right", ncol=2)


def panel_c(ax, d):
    pa = d["per_arm_rule_same_arm_both_seeds"]
    ax.plot(pa["c"], pa["cm_canonical"], "o-", color="tab:blue",
            label="per-arm z > 4, both seeds: cm arm")
    ax.plot(pa["c"], pa["random_naive"], "s-", color="tab:cyan",
            label="per-arm z > 4, both seeds: random arm")
    ad = d["arm_difference_rule_both_seeds"]
    ax.plot(ad["cm_leaks"]["c"], ad["cm_leaks"]["p_fire"], "o--", color="tab:red",
            label="arm |z| > 3, both seeds: cm arm leaks")
    ax.plot(ad["random_leaks"]["c"], ad["random_leaks"]["p_fire"], "s--", color="tab:pink",
            label="arm |z| > 3, both seeds: random arm leaks")
    ax.axhline(0.8, color="grey", linestyle=":", linewidth=1, label="power 0.8")
    ax.set_xscale("log")
    ax.set_xticks([1, 2, 4, 8, 16, 32])
    ax.set_xticklabels(["1", "2", "4", "8", "16", "32"])
    ax.set_xlabel("planted leak rate, multiple c of 1/p")
    ax.set_ylabel("P(frozen rule fires)")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title("(c) Power of the frozen rules (red team, realized rows)", fontsize=9)
    ax.legend(fontsize=6, loc="lower right")


def panel_d(ax, d):
    rows = d["rows"]
    labels = []
    for i, r in enumerate(rows):
        y = len(rows) - 1 - i
        band = Z95 * r["null_sd"] / r["null_mean"]
        ax.barh(y, 2 * band, left=1 - band, height=0.6, color="lightgrey",
                label="null 95 % band" if i == 0 else None)
        ratio = r["success"] / r["null_mean"]
        colour = "tab:blue" if r["lift"] == "recorded" else "tab:orange"
        ax.plot([ratio], [y], "o", color=colour,
                label=(f"{r['lift']} lift" if i in (0, 2) else None))
        labels.append(f"{r['group'].replace('_', ' ')} / {r['section']} ({r['cells']:,} cells)")
    ax.axvline(1.0, color="grey", linestyle="--", linewidth=1)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(list(reversed(labels)), fontsize=6)
    ax.set_xlim(0.9, 1.1)
    ax.set_xlabel("successes / same-shape null mean  (frozen floor 4.2x-5.2x is off scale)")
    ax.set_title("(d) Exhaustive control, all P and all d (red team)", fontsize=9)
    ax.legend(fontsize=6, loc="lower right")


def main():
    with open(os.path.join(HERE, "plot_data.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    plt.rcParams["svg.hashsalt"] = "DEC-20261023-36b4f0"
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    panel_a(axes[0][0], data["panel_a_precision_sweep"])
    panel_b(axes[0][1], data["panel_b_success_vs_reference"])
    panel_c(axes[1][0], data["panel_c_power"])
    panel_d(axes[1][1], data["panel_d_exhaustive_control"])
    fig.suptitle("DEC-20261023-36b4f0 / EV-CZLIFT-ad28f5: EXP-CZLIFT-ae0a13, toy scale "
                 "(50 <= p <= 600, 11 <= n <= 613, k = 4)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = os.path.join(HERE, "graph.svg")
    fig.savefig(out, format="svg", metadata={"Date": None})
    print(out)


if __name__ == "__main__":
    main()
