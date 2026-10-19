"""Draws ratios.svg from RUN-ENDO-bc1b14's recorded timings and summaries only."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / "runs" / "RUN-ENDO-bc1b14"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
COL = {"target": "#2a78d6", "control": "#eb6834"}
plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.edgecolor": GRID, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "svg.fonttype": "none"})
arms = [("A1", "ratio_A1_over_A0", "A1 persistent / A0"), ("A2", "ratio_A2_over_A0", "A2 one-shot / A0"),
        ("A3", "ratio_A3_over_A0_AA", "A3 A/A / A0")]
roles = [("target", "BADA55-VPR-224"), ("control", "control: 3-neighbour of P-256")]
fig, ax = plt.subplots(figsize=(9, 4.2))
y, ticks, labels = 0, [], []
for role, rname in roles:
    t = json.loads((RUN / role / "timings.json").read_text())
    s = json.loads((RUN / role / "summary.json").read_text())
    for arm, key, lab in arms:
        per = [b / a for a, b in zip(t["A0"], t[arm])]
        ax.scatter(per, [y] * len(per), s=10, color=COL[role], alpha=0.25, linewidths=0)
        m, (lo, hi) = s[key]["median"], s[key]["ci95"]
        ax.plot([lo, hi], [y, y], color=COL[role], lw=2.5)
        ax.scatter([m], [y], s=40, color=COL[role], zorder=3, edgecolors=SURF, linewidths=1.5)
        ax.text(max(per) + 0.004, y, f"{m:.3f} [{lo:.3f}, {hi:.3f}]", va="center", fontsize=8, color=INK)
        ticks.append(y); labels.append(f"{rname}: {lab}")
        y += 1
    y += 0.6
ax.axvline(1.0, color=INK2, lw=0.8)
ax.axvspan(0.95, 1.05, color=GRID, alpha=0.45, lw=0)
ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=8); ax.invert_yaxis()
ax.set_xlabel("measured time ratio to A0 (per repetition: faint dots; median with 95 % bootstrap CI)")
ax.set_title("Timed scalar multiplication, RUN-ENDO-bc1b14 (41 repetitions x 64 points per arm)", fontsize=10, loc="left")
ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
x0, x1 = ax.get_xlim(); ax.set_xlim(x0, x1 + 0.05)
fig.tight_layout()
fig.savefig(HERE / "ratios.svg")
