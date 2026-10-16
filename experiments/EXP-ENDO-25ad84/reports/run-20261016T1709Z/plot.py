"""Draws gains.svg from RUN-ENDO-d7cb69's recorded rows only (no recomputation)."""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "runs" / "RUN-ENDO-d7cb69" / "raw-result.json"
rows = json.loads(RAW.read_text())["rows"]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.edgecolor": GRID, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "svg.fonttype": "none"})

pop = [r for r in rows if r["role"] == "population"]
def klass(r):
    n = r["baseline"]["note"]
    if "2-GLV" in n: return "j = 0 / 1728 unit GLV"
    if n.startswith("twisted Edwards"): return "twisted Edwards"
    if n.startswith("a = -3"): return "a = -3"
    if n.startswith("isomorphic to an a = -3"): return "isomorphic to a = -3"
    return "other Weierstrass a (generic doubling)"
order = ["a = -3", "isomorphic to a = -3", "twisted Edwards", "j = 0 / 1728 unit GLV",
         "other Weierstrass a (generic doubling)"]
counts = [sum(1 for r in pop if klass(r) == k) for k in order]
other = sum(1 for r in pop if klass(r) not in order)

sel = [r for r in rows if r["role"].startswith("control")] + \
      [r for r in pop if klass(r) == "other Weierstrass a (generic doubling)"]
def label(r):
    n = r["name"].replace("control+: 3-isogenous neighbour of NIST P-256", "control+ model (3-neighbour of P-256)")
    n = n.replace("control+ascent: 11-descendant of a j = 0 curve (256-bit)", "control+ ascent (j=0, f=11)")
    return n
sel.sort(key=lambda r: (not r["role"].startswith("control"), -(r["best"] or {}).get("persistent_gain", -9)))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 5.0), gridspec_kw={"width_ratios": [1, 1.5]})
y = range(len(order))
a1.barh(list(y), counts, color=BLUE, height=0.6)
for i, c in zip(y, counts):
    a1.text(c + 1, i, str(c), va="center", color=INK, fontsize=8)
a1.set_yticks(list(y)); a1.set_yticklabels(order); a1.invert_yaxis()
a1.set_xlabel("population curves (n = %d)" % len(pop))
a1.set_title("Cheapest model already on E", fontsize=10, loc="left")
a1.grid(axis="x", color=GRID, lw=0.6); a1.set_axisbelow(True)
for s in ("top", "right"): a1.spines[s].set_visible(False)

ys = list(range(len(sel)))
pers = [100 * ((r["best"] or {}).get("persistent_gain") or 0) for r in sel]
one = [100 * ((r["best"] or {}).get("oneshot_gain") or 0) for r in sel]
h = 0.36
a2.barh([v - h / 2 - 0.02 for v in ys], pers, height=h, color=BLUE, label="persistent (stay on neighbour)")
a2.barh([v + h / 2 + 0.02 for v in ys], one, height=h, color=ORANGE, label="one-shot (map, k'P, dual map)")
a2.axvline(0, color=INK2, lw=0.8)
a2.set_yticks(ys); a2.set_yticklabels([label(r) + ("" if r["best"] else " (no neighbour)") for r in sel], fontsize=8)
a2.invert_yaxis()
a2.set_xlabel("modelled saving vs best model on E (% of M_eq, S = 1 M)")
a2.set_title("Best neighbour route: controls and generic-a curves", fontsize=10, loc="right")
a2.grid(axis="x", color=GRID, lw=0.6); a2.set_axisbelow(True)
for s in ("top", "right"): a2.spines[s].set_visible(False)
a2.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.3, -0.13), ncol=2)
fig.tight_layout()
fig.savefig(HERE / "gains.svg")
print("other-class population rows:", other)
