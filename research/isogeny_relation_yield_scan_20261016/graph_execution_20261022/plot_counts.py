"""Plot only the two saved fixed-public ordered-count vectors."""
from __future__ import annotations

from itertools import accumulate
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent


def values(name):
    lines = (HERE / name / "attempt/count.stdout").read_text().splitlines()
    return [int(line.split("\t")[2]) for line in lines[1:]]


def main():
    source = values("control-5-source")
    graph = values("control-4")
    if len(source) != 128 or source != graph:
        raise ValueError("saved source/check vectors differ")
    x = list(range(1, 129))
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 4.7), sharex=True,
                             gridspec_kw={"height_ratios": [1.25, 1]})
    axes[0].vlines([i - 0.12 for i in x], 0, source, colors="#244c77", linewidth=1.2,
                   label="source low_x")
    axes[0].vlines([i + 0.12 for i in x], 0, graph, colors="#d7772b", linewidth=1.2,
                   label="vertex 8 graph_transport")
    axes[0].set_ylabel("Ordered triples / target")
    axes[0].legend(loc="upper right", frameon=False, fontsize=8)
    axes[0].grid(axis="y", alpha=0.2)
    axes[1].plot(x, list(accumulate(source)), color="#244c77", linewidth=2,
                 label="source and vertex 8 (identical)")
    axes[1].set_ylabel("Cumulative ordered triples")
    axes[1].set_xlabel("Fixed public target index")
    axes[1].set_xlim(0, 129)
    axes[1].grid(alpha=0.2)
    axes[1].legend(loc="upper left", frameon=False, fontsize=8)
    fig.suptitle("P29 source to check vertex 8: exact count transport, n=128", fontsize=11)
    fig.tight_layout()
    fig.savefig(HERE / "counts.svg", format="svg")


if __name__ == "__main__":
    main()
