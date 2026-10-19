"""Draws decision.svg for DEC-20261016-4f3a1a from committed raw data only.

Left: combined route against GLV on E, per population curve with a GLV arm:
recorded persistent gain, recorded one-shot gain, and the one-shot gain with
the validator's minimum omitted input-format cost charged
(CORR-20261016-ac9fc8). Frozen criterion: one-shot > 0. Frozen prediction
for the persistent gain: (0, 13 %].
Right: corollary arm, model change alone against GLV on E (one-shot), against
the frozen prediction band [-40 %, -20 %] and the criterion <= 0.

Input: experiments/EXP-ENDO-7494e7/runs/RUN-ENDO-795989/raw-result.json.
The only value not read from it is OMITTED, the validator's minimum omitted
cost per chain (experiments/EXP-ENDO-7494e7/validation/TASK-20261016-35d324.md,
section A4 table), copied into CORR-20261016-ac9fc8.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "runs" / "RUN-ENDO-795989" / "raw-result.json"
rows = json.loads(RAW.read_text())["rows"]

OMITTED = {  # M_eq, validator TASK-20261016-35d324 A4 ("minimum omitted cost")
    "GOST 2001 test curve": 32.0,
    "mnt/mnt3/1": 29.0,
    "mnt/mnt3/3": 29.0,
    "mnt/mnt5/2": 32.0,
    "mnt/mnt5/3": 32.0,
    "other/Tom-384": 29.0,
}
CLASS = {"GOST 2001 test curve": "class 1", "mnt/mnt3/1": "class 2", "mnt/mnt3/3": "class 2",
         "mnt/mnt5/2": "class 3", "mnt/mnt5/3": "class 3", "other/Tom-384": "class 4"}

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
BLUE, ORANGE, GREEN, RED = "#2a78d6", "#eb6834", "#1baf7a", "#c0392b"
plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.edgecolor": GRID, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "svg.fonttype": "none"})

sel = [r for r in rows if r["name"] in OMITTED and r.get("combined_vs_glv_on_E")]
labels, pers, rec, cor, mc = [], [], [], [], []
for r in sel:
    ge = r["glv_on_E"]["glv_M_eq"]
    gn = r["combined"]["glv"]["glv_M_eq"]
    conv = r["combined"]["conversion_M_eq"]
    labels.append(f"{r['name'].replace('GOST 2001 test curve', 'GOST 2001 test')} ({CLASS[r['name']]})")
    pers.append(100 * r["combined_vs_glv_on_E"]["persistent_gain"])
    rec.append(100 * r["combined_vs_glv_on_E"]["oneshot_gain"])
    cor.append(100 * (1 - (gn + conv + OMITTED[r["name"]]) / ge))
    mc.append(100 * r["model_change_vs_glv_on_E"]["oneshot_gain"])

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.8), gridspec_kw={"width_ratios": [1.5, 1]})
ys = list(range(len(sel)))
h = 0.26
a1.axvspan(0, 13, color=GRID, alpha=0.55, lw=0, label="frozen persistent prediction (0, 13 %]")
a1.barh([y - h for y in ys], pers, height=h, color=BLUE, label="persistent (recorded)")
a1.barh(ys, rec, height=h, color=ORANGE, label="one-shot (recorded, under-charged)")
a1.barh([y + h for y in ys], cor, height=h, color=GREEN,
        label="one-shot, minimum omitted cost charged (CORR-20261016-ac9fc8)")
for y, v in zip(ys, cor):
    a1.text(v + 0.2, y + h, f"<= {v:+.2f}", va="center", fontsize=7, color=INK)
for y, v in zip(ys, rec):
    a1.text(v + 0.2, y, f"{v:+.2f}", va="center", fontsize=7, color=INK)
a1.axvline(0, color=RED, lw=1.0, ls="--", label="frozen criterion: one-shot > 0")
a1.set_yticks(ys)
a1.set_yticklabels(labels, fontsize=8)
a1.invert_yaxis()
a1.set_xlim(-0.5, 15)
a1.set_xlabel("modelled saving of the combined route vs 2-GLV on E, % of GLV-on-E M_eq (M + S, S = 1 M)")
a1.set_title("Combined route vs GLV on E (RUN-ENDO-795989; routes verified 8/8)", fontsize=10, loc="left")
a1.grid(axis="x", color=GRID, lw=0.6)
a1.set_axisbelow(True)
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, -0.14), ncol=2)

a2.axvspan(-40, -20, color=GRID, alpha=0.55, lw=0, label="frozen prediction band [-40 %, -20 %]")
a2.barh(ys, mc, height=0.5, color=RED, label="model change alone vs GLV on E, one-shot")
for y, v in zip(ys, mc):
    a2.text(v - 0.5, y, f"{v:+.2f}", va="center", ha="right", fontsize=7, color=INK)
a2.axvline(0, color=INK2, lw=0.9, label="corollary: <= 0")
a2.set_yticks(ys)
a2.set_yticklabels([""] * len(ys))
a2.invert_yaxis()
a2.set_xlim(-45, 3)
a2.set_xlabel("% of GLV-on-E M_eq")
a2.set_title("Corollary arm", fontsize=10, loc="left")
a2.grid(axis="x", color=GRID, lw=0.6)
a2.set_axisbelow(True)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=1)

fig.tight_layout()
fig.savefig(HERE / "decision.svg")

for lab, p_, r_, c_, m_ in zip(labels, pers, rec, cor, mc):
    print(f"{lab}: persistent {p_:+.2f} one-shot recorded {r_:+.2f} corrected {c_:+.2f} model-change {m_:+.2f}")
