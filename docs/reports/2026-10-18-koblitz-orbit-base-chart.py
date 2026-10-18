"""Render the exact finite orbit-base membership-term screen as SVG."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "research/icperf_koblitz_orbit_base_20261018/base.json"
OUT = Path(__file__).with_name("2026-10-18-koblitz-orbit-base.svg")


def main() -> None:
    record = json.loads(RECORD.read_text())
    controls = record["controls"]["random_orbit_panels"]
    selected = record["membership"]["term_count"]
    first = record["controls"]["first_five_term_count"]
    fig, ax = plt.subplots(figsize=(9.0, 4.2), layout="constrained")
    ax.scatter([row["index"] + 1 for row in controls],
               [row["term_count"] for row in controls],
               s=30, color="#5585ac")
    ax.axhline(selected, color="#ba473d", linewidth=2,
               )
    ax.axhline(first, color="#59734d", linestyle="--", linewidth=1.5,
               )
    ax.text(31.7, selected + 1.5, f"selected: {selected}",
            color="#ba473d", ha="right", va="bottom", fontsize=9)
    ax.text(31.7, first - 1.5, f"first five: {first}",
            color="#59734d", ha="right", va="top", fontsize=9)
    ax.set(xlabel="Seeded control panel (seed 20261018 + index)",
           ylabel="Nonzero F₂ coefficients in degree-365 membership polynomial",
           title="Koblitz GF(2⁷³), a=1, r=5,384,682,420,498,870,703")
    ax.set_xlim(0, 33)
    ax.set_ylim(145, 218)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(OUT, format="svg", metadata={"Creator": "icperf-koblitz-orbit-base-chart.py"})
    # Matplotlib emits trailing spaces on path-command lines; keep the SVG
    # diff check clean without changing the drawn geometry.
    OUT.write_text("\n".join(line.rstrip(" \t") for line in OUT.read_text().splitlines())
                   + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
