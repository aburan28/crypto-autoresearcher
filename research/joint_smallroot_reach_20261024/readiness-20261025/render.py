#!/usr/bin/env python3
"""Render archived finite counts and a readiness report; never run a trial.

Run in a fresh copy of this report directory. Existing outputs are refused.
Optional first argument adds an external Python dependency directory.
"""
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import sys

if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv[1])
os.environ.setdefault("MPLCONFIGDIR", "/tmp/joint-smallroot-readiness-mpl")
HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "artifacts/finite-audit.json"
for name in ("weighted-accounting.json", "weighted-reach.svg", "report.typ", "report.pdf"):
    if (HERE / name).exists():
        raise SystemExit(f"Refusing to replace {name}; render a fresh copy")
rows = json.loads(SOURCE.read_text())["joint_union_support"]
derived = []
for row in rows:
    a = 4 * row["coordinate_exponents"][0]
    b = 2 * row["coordinate_exponents"][4]
    k = row["budget"]
    derived.append({
        "t": row["multiplicity"], "N": row["dimension"],
        "A": a, "B": b, "K": k,
        "dense_entries": row["dense_matrix_entries"],
        "weighted_objective_ceiling": str(max(Fraction(3, a), Fraction(2, b)) * k),
        "scope": "algebra on archived counts, determinant sufficient region before losses",
    })
payload = {
    "input": "../artifacts/finite-audit.json",
    "input_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "rows": derived,
    "conditional_cost_exponent": "max(3-3*beta-2*gamma+tau, 2*beta)",
    "baseline_cB_measured": False,
    "joint_solver_executed": False,
    "pipeline_improvement_demonstrated": False,
    "independent_weighted_cost_review_completed": False,
}
(HERE / "weighted-accounting.json").write_text(json.dumps(payload, indent=2) + "\n")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(10, 4.1))
beta = np.linspace(0, .27, 400)
axes[0].fill_between(beta, 1.25 - 1.5 * beta, 1,
                     where=(beta <= .25) & (1.25 - 1.5 * beta <= 1),
                     color="#d7dce3", label="Conditional sub-rho region, tau=0")
for row, color in zip(derived, ("#9f5927", "#337b75", "#385da2")):
    g = (row["K"] - row["A"] * beta) / row["B"]
    axes[0].plot(beta, np.where(g >= 0, g, np.nan), color=color,
                 label=f't={row["t"]}, N={row["N"]}')
    axes[0].fill_between(beta, 0, g, where=g >= 0, color=color, alpha=.10)
axes[0].set(xlim=(0, .27), ylim=(0, 1.05), xlabel="Leaf exponent beta",
            ylabel="Internal exponent gamma", title="Weighted sufficient regions")
axes[0].axvline(.25, color="#666", linestyle=":", linewidth=1)
axes[0].legend(fontsize=7, loc="center left")
axes[0].text(.012, .65, "Finite regions omit norm losses.\nOutside is uncertified, not impossible.",
              fontsize=8)
axes[1].plot([r["t"] for r in derived], [r["dense_entries"] for r in derived],
             "o-", color="#385da2")
for r in derived:
    axes[1].annotate(f'{r["dense_entries"]:,}\nN={r["N"]}',
                     (r["t"], r["dense_entries"]), xytext=(0, 9),
                     textcoords="offset points", ha="center", fontsize=8)
axes[1].set(yscale="log", ylim=(200, 1e8), xticks=[1, 2, 3],
            xlabel="Multiplicity t", ylabel="Dense matrix entries (structural count)",
            title="Archived construction size")
axes[1].grid(axis="y", alpha=.2)
fig.suptitle("Three archived candidates; no joint recovery or measured solver cost", fontsize=11)
fig.tight_layout()
fig.savefig(HERE / "weighted-reach.svg", metadata={"Date": None})
plt.close(fig)
svg = HERE / "weighted-reach.svg"
svg.write_text("\n".join(s.rstrip() for s in svg.read_text().splitlines()) + "\n")

# Render the complete report text, preserving paragraphs and the recorded table.
def plain(s):
    s = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\1 (\2)", s)
    return s.replace("`", "")

def q(s):
    return json.dumps(s, ensure_ascii=False)

out = ['#set page(paper: "a4", margin: 17mm)',
       '#set text(size: 9.5pt, font: "DejaVu Sans")',
       '#set par(leading: 0.55em)',
       '#set heading(numbering: none)']
lines = (HERE / "report.md").read_text().splitlines()
i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith("#"):
        n = len(line) - len(line.lstrip("#"))
        out.append(f'#heading(level: {n}, {q(plain(line[n:].strip()))})')
        if n == 1:
            out.append('#image("weighted-reach.svg", width: 100%)')
            out.append('#text(size: 8pt, "Derived from finite-audit.json, one deterministic construction per t; no sampling uncertainty. Gray region uses an unvalidated yield/cost model and rho as a separate reference.")')
        i += 1
    elif line.startswith("|"):
        table = []
        while i < len(lines) and lines[i].startswith("|"):
            cells = [plain(c.strip()) for c in lines[i].strip("|").split("|")]
            if not all(re.fullmatch(r"[-:]+", c) for c in cells):
                table.append(cells)
            i += 1
        cells = ",\n".join("[" + "#text(" + q(c) + ")" + "]" for row in table for c in row)
        out.append('#block(breakable: false)[#text(size: 8pt)[#table(columns: (auto, auto, 2fr, auto, 1fr), inset: 4pt, ' + cells + ')]]')
    elif not line.strip():
        i += 1
    else:
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "|", "- ")):
            para.append(lines[i]); i += 1
        out.append('#text(' + q(plain(" ".join(para))) + ')\n\n')
(HERE / "report.typ").write_text("\n".join(out).rstrip() + "\n")
import typst
typst.compile(str(HERE / "report.typ"), output=str(HERE / "report.pdf"))
