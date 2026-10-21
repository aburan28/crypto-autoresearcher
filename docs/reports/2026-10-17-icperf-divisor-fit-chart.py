"""Render exact nearest-divisor gaps for the fixed prime ICPERF fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[2]
data = json.loads((ROOT / "research/icperf_explicit_divisor_20261017/divisor_fit.json").read_text())
rows = data["rows"]
values = [[100 * cell["relative_gap_numerator"] / cell["relative_gap_denominator"]
           for cell in row["cells"]] for row in rows]
groups = [[0 if value <= 15 else 1 if value <= 25 else 2 for value in row]
          for row in values]

fig, ax = plt.subplots(figsize=(9, 3.2))
ax.imshow(groups, cmap=ListedColormap(["#d2ead7", "#f9dfae", "#efc0b5"]),
          vmin=0, vmax=2, aspect="auto")
for i, row in enumerate(values):
    for j, value in enumerate(row):
        ax.text(j, i, f"{value:.1f}%", ha="center", va="center", fontsize=10,
                color="#1d303a")
ax.set_xticks(range(7), [f"m={m}" for m in range(2, 9)])
ax.set_yticks(range(3), [f"{row['bits']}-bit field" for row in rows])
ax.set_title("Exact nearest divisor gap from 2 × default factor-base size")
ax.tick_params(length=0)
for edge in range(8):
    ax.axvline(edge - 0.5, color="white", lw=2)
for edge in range(4):
    ax.axhline(edge - 0.5, color="white", lw=2)
fig.text(0.02, 0.005,
         "Green: within 15%; amber: 15–25%; red: above 25%. Values rounded to 0.1%.\n"
         "Source: research/icperf_explicit_divisor_20261017/divisor_fit.json; field eligibility only.",
         fontsize=8, color="#3c4c56")
fig.tight_layout(rect=(0, 0.08, 1, 1))
out = Path(__file__).with_suffix(".svg").with_name("2026-10-17-icperf-divisor-fit.svg")
fig.savefig(out, format="svg", metadata={"Date": "2026-10-17"})
out.write_text("\n".join(line.rstrip() for line in out.read_text().splitlines()) + "\n")
print(out)
