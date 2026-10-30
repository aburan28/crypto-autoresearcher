"""Decision-report graph for DEC-20261029-01405d (EXP-PFDR-bb0d26).

Reads the hash-bound analysis.json of RUN-PFDR-089edc, writes plot_data.json
and graph.svg: kappa with its curve-cluster bootstrap 95% interval per powered
cell against the P1 band, and plant_kappa against the P2 threshold.
Usage: python plot.py   (run from this directory)
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "runs" / "RUN-PFDR-089edc" / "analysis.json"

analysis = json.loads(SRC.read_text())
cells = sorted(analysis["cells"], key=lambda c: (c["bits"], c["r"], c["n"]))
rows = [
    {k: c.get(k) for k in ("cell", "bits", "r", "n", "curves", "S", "M", "kappa", "ci95", "z",
                       "plant_kappa", "plant_z", "cls", "powered")}
    for c in cells
]
(HERE / "plot_data.json").write_text(json.dumps(
    {"source": "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-089edc/analysis.json",
     "outcome": analysis["outcome"], "calibration": analysis["calibration"], "cells": rows},
    indent=1) + "\n")

powered = [c for c in cells if c["powered"] and c["cls"] != "invalid"]
x = list(range(len(powered)))
colors = {20: "#2a6fb0", 24: "#c46a1b", 28: "#3d8a4a"}

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True,
                               gridspec_kw={"height_ratios": [3, 2]})
ax1.axhspan(0.90, 1.10, color="#eeeeee", label="P1 interval band [0.90, 1.10]")
ax1.axhspan(0.95, 1.05, color="#d6e6d6", label="P1 null band |kappa - 1| < 0.05")
ax1.axhline(1.0, color="black", lw=0.8)
for i, c in zip(x, powered):
    lo, hi = c["ci95"]
    ax1.errorbar(i, c["kappa"], yerr=[[c["kappa"] - lo], [hi - c["kappa"]]], fmt="o", ms=4,
                 color=colors[c["bits"]], capsize=2)
for b, col in colors.items():
    ax1.plot([], [], "o", color=col, label=f"{b}-bit curves")
ax1.set_ylabel("kappa = S / M (95% curve-cluster CI)")
ax1.set_ylim(0.88, 1.12)
ax1.legend(fontsize=7, ncol=3, loc="upper left")
ax1.set_title("EXP-PFDR-bb0d26, RUN-PFDR-089edc: 44 powered cells (b20-r3-n4096 invalid, not shown); "
              "50 to 1440 curves per cell", fontsize=9)

ax2.axhline(1.15, color="red", lw=1, ls="--", label="P2 threshold plant_kappa >= 1.15")
ax2.bar(x, [c["plant_kappa"] for c in powered], color=[colors[c["bits"]] for c in powered])
ax2.set_ylim(1.0, max(c["plant_kappa"] for c in powered) * 1.05)
ax2.set_ylabel("plant_kappa (planted label AP)")
ax2.legend(fontsize=7, loc="upper left")
ax2.set_xticks(x)
ax2.set_xticklabels([c["cell"] for c in powered], rotation=90, fontsize=6)
fig.tight_layout()
fig.savefig(HERE / "graph.svg")
print(f"{len(powered)} powered cells plotted")
