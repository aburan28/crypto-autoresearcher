"""Decision-report graph for DEC-20261023-147f9f (EXP-CZLIFT-17b7eb).

Reads plot_data.json beside this file and writes graph.svg beside it.
It plots recorded or reviewer-computed values only; it computes no
statistic.

    python3 plot.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "plot_data.json").read_text())
RUNS = DATA["runs"]
SEED = DATA["seeds"]
ZMAX = DATA["threshold"]["abs_z_max"]
MARK = {RUNS[0]: ("o", "tab:blue"), RUNS[1]: ("s", "tab:orange")}


def run_label(run):
    return f"{run} (seed {SEED[run]})"


fig, axes = plt.subplots(2, 2, figsize=(13.0, 9.2))
(ax_a, ax_b), (ax_c, ax_d) = axes

# Panel A: pooled degenerate next-digit z under each definition and null.
pa = DATA["panel_a_pooled_degenerate_z"]
rows = pa["rows"]
ys = list(range(len(rows)))[::-1]
ax_a.axvspan(-ZMAX, ZMAX, color="0.92", zorder=0, label=f"|z| <= {ZMAX} (frozen criterion)")
for edge in (-ZMAX, ZMAX):
    ax_a.axvline(edge, color="tab:red", lw=1.2, ls="--")
ax_a.axvline(0, color="0.5", lw=0.8)
for k, run in enumerate(RUNS):
    marker, color = MARK[run]
    ax_a.scatter([r["z"][run] for r in rows], [y + (0.12 if k == 0 else -0.12) for y in ys],
                 marker=marker, color=color, s=46, zorder=3, label=run_label(run))
ax_a.set_yticks(ys)
ax_a.set_yticklabels([r["label"] for r in rows], fontsize=8)
ax_a.set_xlim(-ZMAX - 0.8, ZMAX + 0.8)
ax_a.set_xlabel("z (null-count standard deviations)")
n0 = pa["n_degenerate_rows"][RUNS[0]]
succ = " / ".join(str(pa["successes_all_v_ge_2"][run]) for run in RUNS)
ax_a.set_title(f"A. Pooled degenerate next-digit rate vs null by definition\n"
               f"n = {n0} degenerate rows per seed (all v>=2); successes {succ}", fontsize=9.5)
ax_a.legend(fontsize=7, loc="lower left")

# Panel B: per-section z against 1/p (producer definition) and against the exact null.
pb = DATA["panel_b_section_z"]
sections = pb["sections"]
xs = range(len(sections))
for edge in (-ZMAX, ZMAX):
    ax_b.axhline(edge, color="tab:red", lw=1.2, ls="--")
for edge in (-2, 2):
    ax_b.axhline(edge, color="0.6", lw=0.8, ls=":")
ax_b.axhline(0, color="0.5", lw=0.8)
offsets = {("inv_p", RUNS[0]): -0.27, ("inv_p", RUNS[1]): -0.09,
           ("exact", RUNS[0]): 0.09, ("exact", RUNS[1]): 0.27}
for run in RUNS:
    marker, color = MARK[run]
    ax_b.scatter([x + offsets[("inv_p", run)] for x in xs], pb["z_vs_inv_p_producer_definition"][run],
                 marker=marker, facecolors="none", edgecolors=color, s=52, zorder=3,
                 label=f"vs 1/p, producer def., {run}")
    ax_b.scatter([x + offsets[("exact", run)] for x in xs], pb["z_vs_exact_null"][run],
                 marker=marker, color=color, s=52, zorder=3,
                 label=f"vs exact null given lifts, {run}")
ax_b.set_xticks(list(xs))
ax_b.set_xticklabels(sections)
ax_b.set_ylim(-ZMAX - 0.8, ZMAX + 0.8)
ax_b.set_ylabel("z (null-count standard deviations)")
ax_b.set_title("B. Per-section z: Teichmuller deficit vs 1/p vanishes under the exact null\n"
               f"{pb['rows_per_section_per_seed']} degenerate rows per section and seed", fontsize=9.5)
ax_b.legend(fontsize=6.5, loc="lower left", ncol=1)

# Panel C: large-p per-section successes against the null and two leak alternatives.
pc = DATA["panel_c_large_p_sections"]
bars = ax_c.bar(pc["sections"], pc["successes"], color="tab:gray", width=0.5,
                label="observed successes (both seeds)")
for bar, n in zip(bars, pc["rows"]):
    ax_c.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6,
              f"{int(bar.get_height())} / {n}", ha="center", fontsize=8)
ax_c.axhline(pc["expected_null"], color="tab:green", lw=1.4,
             label=f"null expectation {pc['expected_null']}")
ax_c.axhline(pc["expected_if_10_over_p"], color="tab:purple", lw=1.2, ls="--",
             label=f"if rate 10/p: {pc['expected_if_10_over_p']}")
ax_c.axhline(pc["expected_if_inv_sqrt_p"], color="tab:red", lw=1.2, ls="--",
             label=f"if rate 1/sqrt(p): {pc['expected_if_inv_sqrt_p']}")
ax_c.set_ylim(0, 45)
ax_c.set_ylabel("successes at p > 500 (count)")
ax_c.set_title("C. Large-p per-section successes (post hoc red-team reading)\n"
               "RUN-CZLIFT-041d05 + RUN-CZLIFT-6709c9 pooled", fontsize=9.5)
ax_c.legend(fontsize=7, loc="upper left")

# Panel D: exact-1.0 predictions (rule agreement; non-degenerate Smart recovery).
pd = DATA["panel_d_rule_and_control"]
labels = [b["label"] for b in pd["bars"]]
fracs = [b["num"] / b["den"] for b in pd["bars"]]
colors = ["tab:blue", "tab:orange", "tab:blue", "tab:orange", "tab:gray"]
dbars = ax_d.barh(labels[::-1], fracs[::-1], color=colors[::-1], height=0.55)
for bar, b in zip(dbars, pd["bars"][::-1]):
    ax_d.text(0.5, bar.get_y() + bar.get_height() / 2, f"{b['num']} / {b['den']}",
              va="center", ha="center", color="white", fontsize=8.5, fontweight="bold")
ax_d.axvline(pd["required"], color="tab:red", lw=1.2, ls="--", label="required exactly 1.0")
ax_d.set_xlim(0, 1.05)
ax_d.set_xlabel("fraction of rows (frozen runs) or lifts (red-team sweep)")
ax_d.tick_params(axis="y", labelsize=8)
ax_d.set_title("D. Exact predictions: rule agreement and non-degenerate recovery\n"
               "0 disagreements; the rule is a theorem, so this calibrates instruments", fontsize=9.5)
ax_d.legend(fontsize=7, loc="lower left")

fig.suptitle("DEC-20261023-147f9f / EV-CZLIFT-712fe4: EXP-CZLIFT-17b7eb, 29 CM anomalous curves, "
             "7 <= p <= 1373, precision p^8 (toy tier)", fontsize=10.5)
fig.tight_layout(rect=(0, 0, 1, 0.965))
fig.savefig(HERE / "graph.svg", format="svg")
print(f"wrote {HERE / 'graph.svg'}")
