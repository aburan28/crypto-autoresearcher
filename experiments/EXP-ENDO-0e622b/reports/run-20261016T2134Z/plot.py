"""Draws oneshot.svg from RUN-ENDO-f461e9 (and RUN-ENDO-795989 for the earlier column) recorded rows only."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[1]
new = json.loads((EXP / "runs" / "RUN-ENDO-f461e9" / "raw-result.json").read_text())["rows"]
old = {r["name"]: r for r in json.loads((EXP.parent / "EXP-ENDO-7494e7" / "runs" / "RUN-ENDO-795989" / "raw-result.json").read_text())["rows"]}
PRED = {"GOST 2001 test curve": 2.20, "mnt/mnt3/1": 5.78, "mnt/mnt3/3": 5.78, "mnt/mnt5/2": 7.55, "mnt/mnt5/3": 7.55, "other/Tom-384": 9.46}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.edgecolor": GRID, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "svg.fonttype": "none"})
rows = [r for r in new if r.get("combined_vs_glv_on_E")]
fig, ax = plt.subplots(figsize=(9, 3.8))
h = 0.26
for i, r in enumerate(rows):
    n = r["name"]
    pers = 100 * r["combined_vs_glv_on_E"]["persistent_gain"]
    prior = 100 * old[n]["combined_vs_glv_on_E"]["oneshot_gain"]
    now = 100 * r["combined_vs_glv_on_E"]["oneshot_gain"]
    ax.barh(i - h, pers, height=h - 0.03, color=BLUE, label="persistent" if i == 0 else None)
    ax.barh(i, prior, height=h - 0.03, color=ORANGE, label="one-shot, RUN-ENDO-795989 (under-charged)" if i == 0 else None)
    ax.barh(i + h, now, height=h - 0.03, color=AQUA, label="one-shot, RUN-ENDO-f461e9 (input-format term charged)" if i == 0 else None)
    ax.plot([PRED[n] - 0.02, PRED[n] + 0.02], [i + h, i + h], color=INK, lw=3, solid_capstyle="butt")
    ax.text(now + 0.15, i + h, f"{now:+.2f} (predicted {PRED[n]:+.2f})", va="center", fontsize=7.5, color=INK)
ax.plot([], [], color=INK, lw=3, label="frozen prediction ±0.02")
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r["name"] for r in rows], fontsize=8); ax.invert_yaxis()
ax.axvline(0, color=INK2, lw=0.8)
ax.set_xlabel("modelled saving of the combined route vs 2-GLV on E, % of GLV-on-E M_eq (M + S)")
ax.set_title("Combined route vs GLV on E: corrected one-shot pricing (RUN-ENDO-f461e9)", fontsize=10, loc="left")
ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.set_xlim(0, 15.5)
ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, -0.16), ncol=2)
fig.tight_layout()
fig.savefig(HERE / "oneshot.svg")
