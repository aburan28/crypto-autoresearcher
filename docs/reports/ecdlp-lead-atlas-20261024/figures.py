#!/usr/bin/env python3
"""Draw the atlas report's figures from the committed rows (no new data).

  python3 figures.py   # from this directory; writes dispositions.svg,
                       # table_a_gap.svg and harness_loop.svg
"""
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

matplotlib.rcParams["svg.fonttype"] = "path"  # glyphs as paths: no font substitution
matplotlib.rcParams["svg.hashsalt"] = "ecdlp-lead-atlas-20261024"
SVG_METADATA = {"Date": "2026-10-24"}

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))
import lead_atlas as la  # noqa: E402

rows = la.load_leads()
fams = list(la.FAMILIES)
colors = {"closed_obstructed": "#3b5b92", "closed_known": "#6f8fc2",
          "closed_dominated": "#a9bde0", "exhausted_at_scale": "#8c8c8c",
          "open_next_step": "#d9822b", "open_blocked": "#c0392b",
          "open_unexamined": "#f2c14e"}
fig, ax = plt.subplots(figsize=(8, 4.8))
left = [0] * len(fams)
for d in la.DISPOSITIONS:
    vals = [sum(r["family"] == f and r["disposition"] == d for r in rows)
            for f in fams]
    ax.barh(fams, vals, left=left, color=colors[d], label=d.replace("_", " "))
    left = [a + b for a, b in zip(left, vals)]
for i, tot in enumerate(left):
    ax.text(tot + 0.3, i, str(tot), va="center", fontsize=9)
ax.invert_yaxis()
ax.set_xlabel("leads (count)")
ax.set_title(f"ECDLP lead atlas, 2026-10-24: {len(rows)} leads by family "
             "and disposition")
ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=4,
          frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "dispositions.svg"), metadata=SVG_METADATA)

# Table A, one target: published x reference vs rho at the canonical step.
# Sources: crypto docs/ic/LEADERBOARD.md (Table A, 2026-10-24) and
# crypto research/validation_sweep_20261019/A-leaderboard/REPORT.md.
curves = ["n47", "n57", "n41", "n53", "n59", "n61"]
log2r = [36.6, 38.0, 39.0, 44.3, 44.5, 47.2]
published = [5.23, 6.12, 7.66, 13.2, 12.0, 21.0]
canonical = [9.13, 10.25, 14.60, 25.40, 23.11, 41.12]
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(log2r, published, "o-", label="published (rho as built)")
ax.plot(log2r, canonical, "s-", label="rho at the canonical step (sweep A)")
for x, y, c in zip(log2r, canonical, curves):
    ax.annotate(c, (x, y), textcoords="offset points", xytext=(4, 4),
                fontsize=8)
ax.axhline(1, color="k", lw=0.8, ls=":")
ax.text(36.6, 1.1, "parity with matched rho", fontsize=8)
ax.set_yscale("log")
ax.set_xlabel("log2 r")
ax.set_ylabel("S_IC / S_rho (distance remaining)")
ax.set_title("Koblitz Table A, one target per process, 64 targets per size;\n"
             "all rows unvalidated (pre-gate)", fontsize=10)
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "table_a_gap.svg"), metadata=SVG_METADATA)

# The harness loop.
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
box = dict(boxstyle="round,pad=0.5", fc="#eef2f8", ec="#3b5b92")
row = [(0.09, "clone or\nsession start"),
       (0.33, "lead_atlas.py brief:\ndelta against the\npinned commits"),
       (0.60, "nothing new: work an\nopen next step or\npropose a NEW lead"),
       (0.87, "new idea: match it,\nname prior_art.lead\n(validator)")]
for x, t in row:
    ax.text(x, 0.72, t, ha="center", va="center", fontsize=8, bbox=box)
for a, b in [(0.155, 0.245), (0.42, 0.505), (0.695, 0.78)]:
    ax.annotate("", xy=(b, 0.72), xytext=(a, 0.72),
                arrowprops=dict(arrowstyle="->", lw=1.2))
ax.text(0.33, 0.2, "changed since review: the lead-atlas\nskill folds the delta, "
        "updates coverage,\nruns the check, then stamps", ha="center",
        va="center", fontsize=8,
        bbox=dict(boxstyle="round,pad=0.5", fc="#fdf2e3", ec="#d9822b"))
ax.annotate("", xy=(0.33, 0.33), xytext=(0.33, 0.56),
            arrowprops=dict(arrowstyle="->", lw=1.2))
ax.annotate("", xy=(0.56, 0.56), xytext=(0.47, 0.25),
            arrowprops=dict(arrowstyle="->", lw=1.0, ls="--"))
ax.set_title("How a fresh clone learns it has already examined everything",
             fontsize=10)
fig.savefig(os.path.join(HERE, "harness_loop.svg"), bbox_inches="tight",
            metadata=SVG_METADATA)

# Matplotlib leaves spaces at the ends of multiline SVG path attributes.
# They have no drawing meaning; normalize them for stable, clean diffs.
for name in ("dispositions.svg", "table_a_gap.svg", "harness_loop.svg"):
    path = Path(HERE) / name
    path.write_text("\n".join(line.rstrip() for line in
                              path.read_text(encoding="utf-8").splitlines())
                    + "\n", encoding="utf-8")
print("ok")
