"""Draws arms.svg from RUN-ENDO-795989's recorded rows only (no recomputation)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
rows = json.loads((HERE.parents[1] / "runs" / "RUN-ENDO-795989" / "raw-result.json").read_text())["rows"]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
C = {"E model": "#c3c2b7", "model change": "#eb6834", "GLV on E": "#2a78d6", "combined": "#1baf7a"}
plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.edgecolor": GRID, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "svg.fonttype": "none"})
sel = [r for r in rows if r.get("glv_on_E", {}).get("ok")]
names = [r["name"].replace("GOST 2001 test curve", "GOST 2001 test") for r in sel]
series = {
    "E model": [r["E_model_baseline"]["M_eq"] for r in sel],
    "model change": [r["model_change"]["oneshot_M_eq"] if r["model_change"] else None for r in sel],
    "GLV on E": [r["glv_on_E"]["glv_M_eq"] for r in sel],
    "combined": [(r["combined"]["glv"]["glv_M_eq"] + r["combined"]["conversion_M_eq"]) if r["combined"] else None for r in sel],
}
fig, ax = plt.subplots(figsize=(10, 4.4))
w = 0.2
for j, (k, vals) in enumerate(series.items()):
    xs = [i + (j - 1.5) * w for i in range(len(sel))]
    ax.bar([x for x, v in zip(xs, vals) if v], [v for v in vals if v], width=w - 0.03, color=C[k], label=k)
ax.set_xticks(range(len(sel)))
ax.set_xticklabels(names, fontsize=8)
ax.set_ylabel("modelled one-shot cost, M_eq (M + S)")
ax.set_title("One-shot scalar multiplication cost per arm (RUN-ENDO-795989)", fontsize=10, loc="left")
ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.legend(frameon=False, fontsize=8, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.1))
fig.tight_layout()
fig.savefig(HERE / "arms.svg")
