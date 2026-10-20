#!/usr/bin/env python3
"""Build the PQC-100 ideation catalogue: TSV, graph (SVG+PNG), README and PDF.

Usage: python3 build_catalogue.py <manifest.json> <out_dir>
Plots only counts taken from the manifest of committed records; no measurement.
"""
import json, os, sys, textwrap
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

man = json.load(open(sys.argv[1]))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)

SCHEME = {"MLKEM": "ML-KEM", "MLDSA": "ML-DSA", "FNDSA": "FN-DSA", "NTRU": "NTRU",
          "SLHDSA": "SLH-DSA", "HQC": "HQC", "QLWE": "Quantum LWE"}
CLASSES = ["mechanism", "algorithm", "representation", "measurement",
           "composition", "control", "tooling"]
schemes = [s for s in SCHEME if any(m["area"] == s for m in man)]

with open(os.path.join(out, "catalogue.tsv"), "w") as f:
    f.write("idea_id\thypothesis_id\texperiment_id\tquestion_id\tgoal_id\tscheme\tclass\tpriority\tscale\ttitle\n")
    for m in man:
        f.write("\t".join([m["idea"], m["hypothesis"], m["experiment"], m["rq"], str(m["goal"]),
                           SCHEME[m["area"]], m["class"], m["priority"], m["scale"],
                           m["title"].replace("\t", " ")]) + "\n")

# stacked bar: ideas per scheme by class
counts = {c: [sum(1 for m in man if m["area"] == s and m["class"] == c) for s in schemes] for c in CLASSES}
colors = ["#2a6fdb", "#e0732c", "#3aa66b", "#8a5cc2", "#c94f6d", "#7a8794", "#c9a227"]
fig, ax = plt.subplots(figsize=(9, 4.8))
bottom = [0] * len(schemes)
for c, col in zip(CLASSES, colors):
    vals = counts[c]
    if sum(vals) == 0:
        continue
    ax.bar([SCHEME[s] for s in schemes], vals, bottom=bottom, color=col, label=c,
           edgecolor="white", linewidth=0.8)
    bottom = [b + v for b, v in zip(bottom, vals)]
for i, b in enumerate(bottom):
    ax.text(i, b + 0.3, str(b), ha="center", va="bottom", fontsize=9)
ax.set_ylabel("ideas (count)")
ax.set_title(f"PQC ideation batch 2026-10-18: {len(man)} ideas, each with a hypothesis and a review_required experiment")
ax.title.set_fontsize(10)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, ncol=4, loc="upper right")
ax.set_ylim(0, max(bottom) * 1.25)
fig.text(0.01, 0.01, "Counts of committed proposal records by scheme and idea class. No experiment has run; these are proposals, not evidence.",
         fontsize=7, color="#555")
fig.tight_layout(rect=(0, 0.03, 1, 1))
for ext in ("svg", "png"):
    fig.savefig(os.path.join(out, f"ideas_by_scheme_class.{ext}"), dpi=150)

# priority x scale panel
fig2, ax2 = plt.subplots(figsize=(6, 3.2))
pri = ["high", "medium", "low"]
scl = ["toy", "medium", "crypto"]
grid = [[sum(1 for m in man if m["priority"] == p and m["scale"] == s) for s in scl] for p in pri]
im = ax2.imshow(grid, cmap="Blues")
ax2.set_xticks(range(3), scl); ax2.set_yticks(range(3), pri)
ax2.set_xlabel("declared experiment scale tier"); ax2.set_ylabel("recommended priority")
for i in range(3):
    for j in range(3):
        ax2.text(j, i, grid[i][j], ha="center", va="center",
                 color="white" if grid[i][j] > max(map(max, grid)) / 2 else "black")
ax2.set_title("Priority vs declared scale tier (counts)", fontsize=10)
fig2.tight_layout()
for ext in ("svg", "png"):
    fig2.savefig(os.path.join(out, f"priority_vs_scale.{ext}"), dpi=150)

# README
rq_counts = Counter(m["rq"] for m in man)
lines = [
    "# PQC ideation batch, 2026-10-18 (PQC-100-20261018)",
    "",
    "**Status: proposals and review_required contracts only.** No experiment in this batch has run,",
    "none is approved, and nothing here is evidence about ML-KEM, ML-DSA, FN-DSA, SLH-DSA, HQC or",
    "NTRU. Every instance an experiment would use is self-generated at reduced scale.",
    "",
    "**Static review correction:** 35 draft contracts have explicit protocol holds. Read the",
    "[entry-specific findings and qualifications](../../docs/reviews/pr2404/qualification.md)",
    "before interpreting the original proposal claims or planning any implementation.",
    "",
    f"The batch adds {len(man)} ideas under `ledger/proposals/`, one specified hypothesis per idea under",
    "`ledger/hypotheses/`, and one experiment contract per hypothesis under `experiments/`. Each",
    "contract carries a variable ledger with an A/A comparison, prediction provenance, decision impact",
    "and an `approval_gate` block naming what blocks Coordinator approval. Shared original blockers",
    "are: no committed launcher, no preapproval packet, no compiled runbook, and no",
    "novelty screen. Contracts under RQ-MLKEM-003 also need a goal, because both goals that served",
    "that question are closed at budget. The linked review adds item-specific protocol corrections",
    "that must be resolved prospectively; the original IDEA and hypothesis records remain intact.",
    "",
    "![ideas by scheme and class](ideas_by_scheme_class.svg)",
    "",
    "![priority vs scale](priority_vs_scale.svg)",
    "",
    "## Ideas per research question",
    "",
    "| research question | ideas |",
    "| --- | --- |",
] + [f"| {rq} | {n} |" for rq, n in sorted(rq_counts.items())] + [
    "",
    "## Catalogue",
    "",
    "| # | idea | experiment | scheme | class | priority | title |",
    "| --- | --- | --- | --- | --- | --- | --- |",
] + [f"| {i} | [{m['idea']}](../../ledger/proposals/{m['idea']}.yaml) | [{m['experiment']}](../../experiments/{m['experiment']}/specification.yaml) | {SCHEME[m['area']]} | {m['class']} | {m['priority']} | {m['title'].replace('|', '/')} |"
     for i, m in enumerate(man, 1)] + [
    "",
    "## How this was produced",
    "",
    "Five drafting sessions each wrote twenty ideas against a shared brief, after reading the",
    "existing 229 PQC proposals for deduplication and the knowledge corpus for citations. A",
    "generator minted every id with `tools/allocate_id.py --check` and wrote the records. Citations",
    "to `KN-LIT-*` entries are `kb` provenance (the file was opened); every other reference is",
    "`recalled` and is a pointer only. All ideas are `novelty_status: unverified`.",
    "",
    "Rebuild the graphs, TSV and PDF from the manifest with:",
    "",
    "```",
    "python3 ideas/catalogue-20261018-pqc/build_catalogue.py ideas/catalogue-20261018-pqc/manifest.json ideas/catalogue-20261018-pqc",
    "```",
    "",
    "## Next step",
    "",
    "Resolve the linked design findings and exact parameter/control contracts first. Then rank",
    "the high-priority reduced-scale proposals. For each, commit a launcher, build the",
    "preapproval packet, compile the runbook, and have the Coordinator record approval under the",
    "standing authorization. Only then does `run` execute it.",
]
open(os.path.join(out, "README.md"), "w").write("\n".join(lines) + "\n")

# PDF: graphs plus a paginated catalogue table
with PdfPages(os.path.join(out, "catalogue.pdf")) as pdf:
    pdf.savefig(fig)
    pdf.savefig(fig2)
    per = 28
    for start in range(0, len(man), per):
        f3 = plt.figure(figsize=(8.27, 11.69))
        f3.text(0.05, 0.97, f"PQC-100 catalogue, entries {start+1}-{min(start+per, len(man))} (proposals; no runs)",
                fontsize=10, weight="bold")
        y = 0.94
        for i, m in enumerate(man[start:start + per], start + 1):
            t = textwrap.shorten(m["title"], 110)
            f3.text(0.05, y, f"{i:3d}. {m['idea']}  {m['experiment']}  [{SCHEME[m['area']]}, {m['class']}, {m['priority']}]",
                    fontsize=6.5, family="monospace")
            f3.text(0.08, y - 0.012, t, fontsize=6.5)
            y -= 0.032
        pdf.savefig(f3)
        plt.close(f3)
print("catalogue built in", out)
