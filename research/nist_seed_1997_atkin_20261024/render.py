#!/usr/bin/env sage -python
"""Render only the archived, independently checked cutoff values."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

here = Path(__file__).resolve().parent
raw_path = here/"runs/scan-v1/raw.json"
raw = json.loads(raw_path.read_text())
verification = json.loads((here/"runs/verification-v2/verification.json").read_text())
assert verification["status"] == "passed"
assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == verification["raw_sha256"]
fig, axes = plt.subplots(4, 1, figsize=(9.2, 9.1), sharex=True, gridspec_kw={"height_ratios":[5,4,8,2]})
for ax, bits in zip(axes,(192,224,239,256)):
    rows = sorted([r for r in raw["rows"] if r["field_bits"] == bits], key=lambda r:(r["label"] == "published",r["name"]))
    labels=[]
    for y,row in enumerate(rows):
        old,new = row["elkies_only_cutoff"],row["residue_density_cutoff"]
        color="#d26723" if row["label"] == "omitted" else "#246caa"
        ax.plot([new,old],[y,y],color="#b7bec8",linewidth=1.5,zorder=1)
        ax.scatter(old,y,marker="o",s=26,facecolors="white",edgecolors="#7d8795",zorder=2)
        ax.scatter(new,y,marker="D",s=32,color=color,zorder=3)
        ax.text(new-3,y,f"{new}",ha="right",va="center",fontsize=8,color=color)
        labels.append(row["name"].replace("omitted_", "omitted ").replace("_", " / "))
    ax.set_yticks(range(len(rows)),labels,fontsize=9)
    ax.invert_yaxis()
    ax.set_ylim(len(rows)-0.5,-0.5)
    ax.set_title(f"{bits}-bit field",loc="left",fontsize=11,fontweight="bold")
    ax.grid(axis="x",alpha=.22)
    ax.spines[["top","right","left"]].set_visible(False)
    ax.tick_params(axis="y",length=0)
axes[-1].set_xlabel("Largest small prime scanned at the declared cutoff (prime value)")
axes[-1].set_xlim(90,278)
fig.suptitle("Including Atkin residues changes the point-counting proxy",fontsize=14,fontweight="bold",y=.99)
fig.legend(handles=[Line2D([0],[0],marker="D",color="none",markerfacecolor="#d26723",markeredgecolor="#d26723",label="Omitted, residue density"),Line2D([0],[0],marker="D",color="none",markerfacecolor="#246caa",markeredgecolor="#246caa",label="Published, residue density"),Line2D([0],[0],marker="o",color="none",markeredgecolor="#7d8795",markerfacecolor="white",label="Prior Elkies-only cutoff")],loc="upper center",bbox_to_anchor=(.55,.966),ncol=3,fontsize=8,frameon=False)
fig.subplots_adjust(left=.28,right=.98,top=.92,bottom=.07,hspace=.55)
fig.savefig(here/"cutoffs.svg")
svg = here/"cutoffs.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
plt.close(fig)
