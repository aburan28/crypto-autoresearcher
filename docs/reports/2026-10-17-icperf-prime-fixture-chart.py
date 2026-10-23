"""Render the public prime-curve fixture search counts from the saved records."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research/icperf_prime_fixtures_20261017"
OUT = Path(__file__).with_suffix(".svg").with_name(
    "2026-10-17-icperf-prime-fixture.svg"
)

rows = []
for bits in (50, 53, 63):
    record = json.loads((BASE / f"n{bits}_seed20261017.json").read_text())
    rows.append((bits, len(record["attempts"]), record["candidate_index"]))

fig, ax = plt.subplots(figsize=(8.5, 3.5))
bars = ax.barh([f"{bits}-bit prime-order curve" for bits, _, _ in rows],
               [count for _, count, _ in rows],
               color=["#266b97", "#c27c37", "#527b58"])
for bar, (_, count, index) in zip(bars, rows):
    ax.text(count + 2, bar.get_y() + bar.get_height() / 2,
            f"{count} checked; accepted index {index}",
            va="center", fontsize=10)
ax.set_xlim(0, max(count for _, count, _ in rows) + 100)
ax.set_xlabel("Deterministic curve candidates checked (count)")
ax.set_title("Public fixture preparation at seed 20261017")
ax.invert_yaxis()
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.02, 0.005,
         "Source: research/icperf_prime_fixtures_20261017/n{50,53,63}_seed20261017.json. "
         "This is selection effort, not IC or rho cost.", fontsize=8, color="#3c4c56")
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(OUT, format="svg", metadata={"Date": "2026-10-17"})
OUT.write_text("\n".join(line.rstrip() for line in OUT.read_text().splitlines()) + "\n")
print(OUT)
