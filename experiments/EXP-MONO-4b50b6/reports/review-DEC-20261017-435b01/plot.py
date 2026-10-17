#!/usr/bin/env python3
"""Regenerate obstruction.svg from obstruction-data.json (DEC-20261017-435b01 decision report).

Fraction of generic fibres with non-trivial Frobenius, per (curve, m) cell: ON the factor-base locus
(TASK-20261016-9c1bc5 review_report.md Part 1.3 Checks 2 and 4, plus RUN-MONO-4b50b6-002 V4 as
EV-MONO-a0a89c OBS-4 records it) beside the proves-too-much null object OFF the locus (Part 5,
object 1). For every 0-of-N cell the one-sided 95% upper bound 1 - 0.05^(1/N) is drawn and labelled
"derived". No value is computed here beyond that bound; all counts come from the data file.

    python3 plot.py            # writes obstruction.svg next to this file
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ON, OFF = "#2a78d6", "#eb6834"  # reference palette slots 1 and 2 (validated adjacent pair)
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def main() -> None:
    doc = json.loads((HERE / "obstruction-data.json").read_text())
    cells = doc["cells"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.fonttype": "none",
                         "svg.hashsalt": "DEC-20261017-435b01"})
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    fig.patch.set_facecolor("#ffffff")
    y = list(range(len(cells)))[::-1]
    for yi, c in zip(y, cells):
        on = c["locus"].startswith("on")
        color = ON if on else OFF
        frac = c["fraction"]
        ax.barh(yi, frac, height=0.56, color=color, edgecolor="#ffffff", linewidth=2)
        if c["upper_bound_95"] is not None:
            ub = c["upper_bound_95"]
            ax.plot([0, ub], [yi, yi], color=color, linewidth=2)
            ax.plot([ub], [yi], marker="|", markersize=10, color=color, markeredgewidth=2)
            unit = "non-split pairs" if c["cell"].startswith("RUN-002") else "non-trivial"
            txt = f"0 {unit} of {c['n']:,}  (95% bound {ub:.3g}, derived)"
            ax.text(max(ub, 0.0) + 0.012, yi, txt, va="center", color=INK)
        else:
            txt = f"{c['nontrivial']:,} of {c['n']:,} = {frac:.3f}  (measured)"
            ax.text(frac + 0.012, yi, txt, va="center", color=INK)
    ax.axvline(0, color=INK, linewidth=1.2)
    ax.text(0.003, -0.62, "← reference line: 0 by derivation (on the locus, every m ≥ 3)",
            color=MUTED, fontsize=8, va="bottom")
    ax.set_yticks(y)
    ax.set_yticklabels([f"{c['cell']}  (p={c['p']})" for c in cells], color=INK)
    ax.set_xlim(0, 1.45)
    ax.set_ylim(-0.7, len(cells) - 0.1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel("fraction of generic fibres with non-trivial Frobenius", color=INK)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED)
    handles = [plt.Rectangle((0, 0), 1, 1, color=ON), plt.Rectangle((0, 0), 1, 1, color=OFF)]
    ax.legend(handles, ["on the factor-base locus (EV-MONO-1ef611 scope)",
                        "off the locus: proves-too-much null object 1"],
              loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=2, frameon=False, fontsize=8)
    fig.suptitle("Generic-fibre Frobenius census: on vs off the factor-base locus", x=0.02, ha="left",
                 fontsize=10, color=INK)
    fig.text(0.02, 0.925, "Sources: TASK-20261016-9c1bc5 computations.json; EV-MONO-a0a89c OBS-4 (V4). "
             "Thin lines: derived 95% bounds", fontsize=8, color=MUTED, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(HERE / "obstruction.svg", format="svg", metadata={"Date": None})


if __name__ == "__main__":
    main()
