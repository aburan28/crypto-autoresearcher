"""Plot exact point-specialized S3..S9 degrees and chain lengths."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "research/icperf_koblitz_high_arity_20261018/inputs.json"
OUT = Path(__file__).with_name("2026-10-18-koblitz-high-arity-inputs.svg")


def main() -> None:
    rows = json.loads(RECORD.read_text())["rows"]
    arities = [row["m"] for row in rows]
    degrees = [row["direct_polynomial_degree"] for row in rows]
    terms = [row["direct_polynomial_nonzero_terms"] for row in rows]
    chain = [row["chain_equations"] for row in rows]
    fig, ax = plt.subplots(figsize=(8.8, 4.0), layout="constrained")
    ax.plot(arities, degrees, marker="o", color="#305f85", label="direct specialization degree")
    ax.plot(arities, terms, marker="s", color="#b9513e", linestyle="--",
            label="nonzero target-variable terms")
    for m, degree, count in zip(arities, degrees, terms):
        ax.annotate(f"S{m+1}: {degree}/{count}", (m, count),
                    xytext=(0, 7), textcoords="offset points", ha="center", fontsize=8)
    ax.set(xlabel="Factor-base summands m", ylabel="Exact target-variable degree / term count",
           title="Point-specialized binary Koblitz S₃–S₉ root polynomials")
    ax.set_xticks(arities)
    ax.set_ylim(0, 145)
    ax.grid(axis="y", alpha=0.25)
    other = ax.twinx()
    other.plot(arities, chain, marker="^", color="#58754c", label="chained S₃ equations")
    other.set(ylabel="Planted chained S₃ equations", ylim=(0, 8))
    lines = ax.lines + other.lines
    ax.legend(lines, [line.get_label() for line in lines], loc="upper left", fontsize=8)
    fig.savefig(OUT, format="svg",
                metadata={"Creator": "icperf-koblitz-high-arity-inputs-chart.py"})
    OUT.write_text("\n".join(line.rstrip(" \t") for line in OUT.read_text().splitlines())
                   + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
