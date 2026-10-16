"""Draws decision.svg for DEC-20261016-5752c0 from committed raw data only.

Left: arm M. For every population curve with a positive best route in
RUN-ENDO-d7cb69 (and the control+model row), the recorded one-shot gain
against E's best model (the frozen criterion: > 0; the frozen prediction
band: (0, 15 %]) beside the recorded one-shot gain of the same route against
E's verified chain 2-GLV (RUN-ENDO-795989, model_change_vs_glv_on_E).
Right: arm A. |D_K| of every population curve with a certified D_K, against
the frozen threshold |D_K| <= 20, split by whether the root is a j = 0 / 1728
crater (f_E = 1) or not (f_E unresolved).

Inputs:
  experiments/EXP-ENDO-25ad84/runs/RUN-ENDO-d7cb69/raw-result.json
  experiments/EXP-ENDO-7494e7/runs/RUN-ENDO-795989/raw-result.json
No value is recomputed; gains are the recorded fractions times 100.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[1]
RAW1 = EXP / "runs" / "RUN-ENDO-d7cb69" / "raw-result.json"
RAW2 = EXP.parent / "EXP-ENDO-7494e7" / "runs" / "RUN-ENDO-795989" / "raw-result.json"
rows = json.loads(RAW1.read_text())["rows"]
glv = {r["name"]: r for r in json.loads(RAW2.read_text())["rows"]}

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
BLUE, ORANGE, RED, GREY = "#2a78d6", "#eb6834", "#c0392b", "#9a9890"
plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.edgecolor": GRID, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "svg.fonttype": "none"})

# ---- arm M --------------------------------------------------------------
pos = [r for r in rows if r["role"] == "population" and r.get("best") and r["best"]["persistent_gain"] > 0]
pos.sort(key=lambda r: -r["best"]["oneshot_gain"])
ctrl = [r for r in rows if r["role"] == "control+model"]
sel = ctrl + pos
names = [r["name"].replace("control+: 3-isogenous neighbour of NIST P-256", "control+ model (3-nbr of P-256)")
         .replace("GOST 2001 test curve", "GOST 2001 test") for r in sel]
vs_model = [100 * r["best"]["oneshot_gain"] for r in sel]
vs_glv = [100 * glv[r["name"]]["model_change_vs_glv_on_E"]["oneshot_gain"]
          if r["name"] in glv and glv[r["name"]].get("model_change_vs_glv_on_E") else None for r in sel]
verified = [bool((r.get("verification") or {}).get("ok")) for r in sel]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 5.0), gridspec_kw={"width_ratios": [1.35, 1]})
ys = list(range(len(sel)))
h = 0.38
a1.axvspan(0, 15, color=GRID, alpha=0.55, lw=0, label="frozen prediction band (0, 15 %]")
a1.barh([y - h / 2 for y in ys], vs_model, height=h, color=BLUE,
        label="vs E's best model + unit GLV (frozen baseline)")
a1.barh([y + h / 2 for y, v in zip(ys, vs_glv) if v is not None], [v for v in vs_glv if v is not None],
        height=h, color=RED, label="vs E's verified chain 2-GLV (RUN-ENDO-795989)")
for y, v, ok in zip(ys, vs_model, verified):
    a1.text(v + 0.6, y - h / 2, f"{v:+.2f}" + (" (8/8)" if ok else ""), va="center", fontsize=7, color=INK)
for y, v, r in zip(ys, vs_glv, sel):
    if v is not None:
        a1.text(v - 0.6, y + h / 2, f"{v:+.2f}", va="center", ha="right", fontsize=7, color=INK)
    elif r["role"] == "population":
        a1.text(0.6, y + h / 2, "no |D_K| <= 2e6: no GLV on E", va="center", fontsize=7, color=INK2)
    else:
        a1.text(0.6, y + h / 2, "control: not in RUN-ENDO-795989", va="center", fontsize=7, color=INK2)
a1.axvline(0, color=INK2, lw=0.9)
a1.set_yticks(ys)
a1.set_yticklabels(names, fontsize=8)
a1.invert_yaxis()
a1.set_xlim(-40, 22)
a1.set_xlabel("modelled one-shot k*P saving, % of reference M_eq (M + S, S = 1 M; 200 scalars)")
a1.set_title("Arm M: frozen criterion one-shot gain > 0 (RUN-ENDO-d7cb69)", fontsize=10, loc="left")
a1.grid(axis="x", color=GRID, lw=0.6)
a1.set_axisbelow(True)
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, -0.12), ncol=1)

# ---- arm A --------------------------------------------------------------
pop = [r for r in rows if r["role"] == "population" and r["ascent"]["D_K"] is not None]
crater = [r for r in pop if r["ascent"]["f_E"] == 1]
other = [r for r in pop if r["ascent"]["f_E"] != 1]
hits = [r for r in other if abs(r["ascent"]["D_K"]) <= 20]
a2.scatter([r["bits"] for r in crater], [abs(r["ascent"]["D_K"]) for r in crater], s=18, color=GREY,
           label=f"root is a j = 0 / 1728 crater, f_E = 1 (n = {len(crater)})")
a2.scatter([r["bits"] for r in other], [abs(r["ascent"]["D_K"]) for r in other], s=18, color=ORANGE,
           label=f"root not a j = 0 / 1728 crater, f_E unresolved (n = {len(other)})")
for r in hits:
    a2.annotate(f"{r['name']}  D_K = {r['ascent']['D_K']}", (r["bits"], abs(r["ascent"]["D_K"])),
                xytext=(8, 10), textcoords="offset points", fontsize=7.5, color=RED,
                arrowprops={"arrowstyle": "-", "color": RED, "lw": 0.7})
a2.axhline(20, color=RED, lw=0.9, ls="--", label="frozen threshold |D_K| = 20 (predicted hits: 0)")
a2.set_yscale("log")
a2.set_xlabel("field size, bits")
a2.set_ylabel("|D_K| (certified, |D_K| <= 2^20)")
a2.set_title(f"Arm A: {len(hits)} hits against a predicted 0", fontsize=10, loc="left")
a2.grid(color=GRID, lw=0.6)
a2.set_axisbelow(True)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=1)

fig.tight_layout()
fig.savefig(HERE / "decision.svg")

print("arm M positives:", len(pos), [(r["name"], r["best"]["oneshot_gain"]) for r in pos])
print("arm M vs GLV on E:", [(r["name"], (glv.get(r["name"], {}).get("model_change_vs_glv_on_E") or {}).get("oneshot_gain")) for r in pos])
print("arm A certified D_K rows:", len(pop), "crater:", len(crater), "other:", len(other))
print("arm A hits:", [(r["name"], r["ascent"]["D_K"], r["ascent"]["f_pi"]) for r in hits])
