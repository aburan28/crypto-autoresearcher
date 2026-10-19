"""Draws decision.svg for DEC-20261016-f379af from committed raw data only.

For each curve (target other/BADA55-VPR-224, positive control) and each ratio
(A1/A0 persistent, A2/A0 one-shot, A3/A0 A/A): the recorded median paired
ratio with its recorded 95 % percentile-bootstrap CI (summary.json), the 41
per-repetition ratios (timings.json), the frozen threshold 1 (success: target
A2/A0 upper bound < 1; positive control: control A1/A0 upper bound < 1), the
frozen A/A margin [0.95, 1.05], the modelled ratio 1 - modelled gain from
RUN-ENDO-d7cb69 (as frozen in the specification), and a contention
sensitivity: the median ratio over repetitions not flagged by the validator's
rule (a repetition is flagged when any arm exceeds 1.10 x that arm's median;
TASK-20261016-35d324 B4). The sensitivity median is recomputed here; its CI
is not (the validator's CIs are quoted in the report).

Inputs: experiments/EXP-ENDO-33a1ee/runs/RUN-ENDO-bc1b14/{target,control}/{timings,summary}.json
"""
import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / "runs" / "RUN-ENDO-bc1b14"
MODELLED = {  # 1 - modelled gain, frozen in experiments/EXP-ENDO-33a1ee/specification.yaml inputs.curves
    ("target", "A1"): 1 - 0.15205, ("target", "A2"): 1 - 0.11441,
    ("control", "A1"): 1 - 0.15276, ("control", "A2"): 1 - 0.14465,
}
ARMS = [("A1", "ratio_A1_over_A0", "A1/A0 persistent"), ("A2", "ratio_A2_over_A0", "A2/A0 one-shot"),
        ("A3", "ratio_A3_over_A0_AA", "A3/A0 A/A")]
ROLES = [("target", "BADA55-VPR-224"), ("control", "control: 3-nbr of P-256")]

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
COL = {"target": "#2a78d6", "control": "#eb6834"}
RED = "#c0392b"
plt.rcParams.update({"font.size": 9, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.edgecolor": GRID, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "svg.fonttype": "none"})

fig, ax = plt.subplots(figsize=(11.5, 4.8))
y, ticks, labels = 0, [], []
report = []
for role, rname in ROLES:
    t = json.loads((RUN / role / "timings.json").read_text())
    s = json.loads((RUN / role / "summary.json").read_text())
    med = {a: statistics.median(t[a]) for a in ("A0", "A1", "A2", "A3")}
    n = len(t["A0"])
    flagged = [i for i in range(n) if any(t[a][i] > 1.10 * med[a] for a in ("A0", "A1", "A2", "A3"))]
    clean = [i for i in range(n) if i not in flagged]
    for arm, key, lab in ARMS:
        per = [t[arm][i] / t["A0"][i] for i in range(n)]
        m, (lo, hi) = s[key]["median"], s[key]["ci95"]
        sens = statistics.median([per[i] for i in clean])
        ax.scatter(per, [y] * n, s=9, color=COL[role], alpha=0.22, linewidths=0)
        ax.plot([lo, hi], [y, y], color=COL[role], lw=3)
        ax.scatter([m], [y], s=42, color=COL[role], zorder=3, edgecolors=SURF, linewidths=1.5)
        ax.scatter([sens], [y - 0.28], s=26, facecolors="none", edgecolors=INK, linewidths=0.9, zorder=3)
        if (role, arm) in MODELLED:
            ax.scatter([MODELLED[(role, arm)]], [y], marker="|", s=160, color=INK2, zorder=3)
        ax.text(1.01, y, f"{m:.4f} [{lo:.4f}, {hi:.4f}]", va="center", fontsize=7.5, color=INK,
                transform=ax.get_yaxis_transform(), clip_on=False)
        ticks.append(y)
        labels.append(f"{rname}: {lab}")
        report.append((role, arm, m, lo, hi, sens, statistics.median(per)))
        y += 1
    report.append((role, "flagged", len(flagged), n, None, None, None))
    y += 0.7

ax.axvspan(0.95, 1.05, color=GRID, alpha=0.5, lw=0)
ax.axvline(1.0, color=RED, lw=1.0, ls="--")
ax.set_yticks(ticks)
ax.set_yticklabels(labels, fontsize=8)
ax.invert_yaxis()
ax.set_xlim(0.45, 1.95)
ax.set_xlabel("measured wall-clock time ratio to A0 (ns per scalar multiplication; 64 points x 41 repetitions per arm)")
ax.set_title("RUN-ENDO-bc1b14: frozen criterion target A2/A0 upper CI < 1; A/A CI within [0.95, 1.05]",
             fontsize=10, loc="left")
ax.grid(axis="x", color=GRID, lw=0.6)
ax.set_axisbelow(True)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)
handles = [
    plt.Line2D([], [], color=INK2, marker="o", lw=3, label="recorded median and 95 % bootstrap CI"),
    plt.Line2D([], [], color=INK2, marker="o", lw=0, alpha=0.3, label="per-repetition ratio (41)"),
    plt.Line2D([], [], color=INK, marker="o", lw=0, markerfacecolor="none",
               label="median without contention-flagged repetitions"),
    plt.Line2D([], [], color=INK2, marker="|", lw=0, markersize=12, label="modelled ratio (RUN-ENDO-d7cb69)"),
    plt.Line2D([], [], color=RED, ls="--", label="ratio 1"),
    plt.Rectangle((0, 0), 1, 1, color=GRID, alpha=0.5, label="A/A margin [0.95, 1.05]"),
]
ax.legend(handles=handles, frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=3)
fig.tight_layout()
fig.savefig(HERE / "decision.svg", bbox_inches="tight")

for row in report:
    print(row)
