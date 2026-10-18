"""Render the exact six-orbit membership-polynomial support screen."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "research/icperf_koblitz_orbit_six_20261018/base.json"
OUT = Path(__file__).with_name("2026-10-18-koblitz-six-orbit.svg")


def main() -> None:
    record = json.loads(RECORD.read_text())
    controls = record["controls"]["random_orbit_panels"]
    selected = record["membership"]["term_count"]
    first = record["controls"]["first_six_term_count"]
    fig, ax = plt.subplots(figsize=(9.0, 4.0), layout="constrained")
    ax.scatter([row["index"] + 1 for row in controls],
               [row["term_count"] for row in controls],
               s=30, color="#5585ac")
    ax.axhline(selected, color="#ba473d", linewidth=2)
    ax.axhline(first, color="#59734d", linestyle="--", linewidth=1.5)
    ax.text(31.7, selected + 1.5, f"selected: {selected}",
            color="#ba473d", ha="right", va="bottom", fontsize=9)
    ax.text(31.7, first - 1.5, f"first six: {first}",
            color="#59734d", ha="right", va="top", fontsize=9)
    ax.set(xlabel="Seeded six-orbit control panel (seed 20261050 + index)",
           ylabel="Nonzero F₂ coefficients in degree-438 membership polynomial",
           title="Koblitz GF(2⁷³), 62.224-bit prime subgroup")
    ax.set_xlim(0, 33)
    ax.set_ylim(176, 260)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(OUT, format="svg",
                metadata={"Creator": "icperf-koblitz-six-orbit-chart.py"})
    OUT.write_text("\n".join(line.rstrip(" \t") for line in OUT.read_text().splitlines())
                   + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
