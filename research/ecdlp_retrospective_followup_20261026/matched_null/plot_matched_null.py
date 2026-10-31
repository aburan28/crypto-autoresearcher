#!/usr/bin/env python3
"""Draw matched_null/output.json: recorded values only, no new computation.

Writes matched_null.svg (the graph) and matched_null_report.pdf (graph plus the
numbers it shows). Usage: python3 plot_matched_null.py output.json
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

res = json.load(open(sys.argv[1]))
labels = ["producer's replica\n(open window,\nunfolded key)", "negation-closed,\nunfolded key",
          "open window,\nsign-folded key", "negation-closed,\nsign-folded key\n(MATCHED)", "curve census\n(reported)"]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, c in zip(axes, res["cells"]):
    g, p = c["generic_matched_simulation"], c["prefix_window_closed"]
    keys = ["ratio_open_window_unfolded_key_producer_replica_style", "ratio_closed_window_unfolded_key",
            "ratio_open_window_folded_key", "ratio_closed_window_folded_key"]
    means = [g[k]["mean"] for k in keys] + [p["reported_style_ratio"]]
    errs = [g[k]["sd"] for k in keys] + [0.0]
    colors = ["#8da0cb", "#8da0cb", "#8da0cb", "#66c2a5", "#fc8d62"]
    ax.bar(range(5), means, yerr=errs, color=colors, capsize=3)
    ax.axhline(p["leading_order_prediction_2_plus_N_over_T"], color="k", ls="--", lw=1)
    ax.text(-0.45, p["leading_order_prediction_2_plus_N_over_T"] + 0.06, "2 + N/T (dashed)", ha="left", fontsize=8)
    ax.set_ylim(0, 3.5)
    ax.axhspan(0.5, 2.0, color="0.9", zorder=0)
    ax.set_xticks(range(5))
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_title(f"{c['cell']}: n={c['n']}, N={c['group_order']}, |V|={p['window_size']}, T={p['T']}", fontsize=9)
    for i, m in enumerate(means):
        ax.text(i, m + 0.08, f"{m:.3f}", ha="center", fontsize=8)
axes[0].set_ylabel("combined / (T^2 / 2N)")
fig.suptitle("EV-BINSTD-769c7c: collision ratio under matched generic nulls "
             "(bars: mean of 20 windows +/- sd; grey band: the DO-1 band [0.5, 2])", fontsize=9)
fig.tight_layout()
fig.savefig("matched_null.svg")
with PdfPages("matched_null_report.pdf") as pdf:
    pdf.savefig(fig)
    t = plt.figure(figsize=(11, 4.6))
    t.text(0.02, 0.97, open("summary.txt").read(), va="top", family="monospace", fontsize=3.6)
    pdf.savefig(t)
