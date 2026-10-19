"""Draw the decision graph for DEC-20261019-f33f3e from graph_data.json only.

No new computation of any measured quantity: every plotted value is read from
graph_data.json, which holds values read from RUN-CMFB-2010d3/raw-result.json
(recorded) or from the two review reports (named in the file). The only
arithmetic here is the derived contract-text MDE check (recorded MDE divided by
the code's inflation factor), compared with the validator's tabulated value and
reported on stdout.

Usage: python3 plot.py        (writes fig_review.svg and fig_review.png here)
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "graph_data.json").read_text())

ARMS = data["arms"]
CELLS = data["cell_order"]
DELTA = data["delta_pct"]
THRESH = data["powered_threshold_mde_pct"]
FACTOR = data["mde_inflation_factor_in_code"]["value"]
COL = {"FAM": "#1f5fa8", "N-A": "#c0561c", "N-B": "#2f7d4f"}
rows = {(r["arm"], r["cell"]): r for r in data["rows"]}
POWERED_CONTRACT = set(data["powered"]["contract_text"])


def draw_T(ax, cells, ylim, title, annotate_n=True):
    for j, arm in enumerate(ARMS):
        for i, cell in enumerate(cells):
            r = rows[(arm, cell)]
            x = i + (j - 1) * 0.24
            t = r["T_pct"]
            lo, hi = r["ci95_pct"]
            filled = cell in POWERED_CONTRACT
            ax.errorbar(
                [x], [t], yerr=[[t - lo], [hi - t]], fmt="o", color=COL[arm],
                mfc=COL[arm] if filled else "white", capsize=3, ms=5,
            )
            if annotate_n:
                ax.annotate(f"n={r['n']}", (x, hi), textcoords="offset points",
                            xytext=(0, 4), ha="center", fontsize=6.5, color=COL[arm])
    ax.axhspan(-DELTA, DELTA, color="#bbbbbb", alpha=0.25)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xticks(range(len(cells)))
    ax.set_xticklabels([f"{c}\n{data['cell_bands'][c]}" for c in cells], fontsize=7)
    ax.set_xlim(-0.6, len(cells) - 0.4)
    ax.set_ylim(*ylim)
    ax.set_ylabel("T: mean coverage ratio - 1  (%)", fontsize=8)
    ax.set_title(title, fontsize=8.5)
    ax.grid(alpha=0.25)


fig = plt.figure(figsize=(13.5, 8.4))
gs = fig.add_gridspec(2, 3, hspace=0.55, wspace=0.32)

# (a) full scale against delta
a = fig.add_subplot(gs[0, 0])
draw_T(a, CELLS, (-0.62, 0.62), "(a) T with recorded 95% interval vs delta = +-0.5%")
a.text(0.02, 0.97, "grey band: +-delta = +-0.5 %\nhollow: C16, underpowered",
       transform=a.transAxes, fontsize=6.5, va="top")
handles = [Line2D([0], [0], marker="o", color=COL[k], ls="", label=k) for k in ARMS]
a.legend(handles=handles, fontsize=7, loc="lower right")

# (b) zoom on C20 and C24
b = fig.add_subplot(gs[0, 1])
draw_T(b, ["C20", "C24"], (-0.10, 0.10), "(b) zoom, C20 and C24 (+-0.1 %; band +-0.5 % is off scale)")
b.text(0.02, 0.97, "C24 intervals within +-0.04 %\nC20 powered under the contract text only",
       transform=b.transAxes, fontsize=6.5, va="top")

# (c) MDE: recorded (code) vs contract text vs threshold
c = fig.add_subplot(gs[0, 2])
labels, rec, con = [], [], []
for arm in ARMS:
    for cell in CELLS:
        r = rows[(arm, cell)]
        labels.append(f"{arm}\n{cell}")
        rec.append(r["mde_recorded_pct"])
        con.append(r["mde_contract_pct_VAL_D1"])
        derived = r["mde_recorded_pct"] / FACTOR
        if abs(derived - r["mde_contract_pct_VAL_D1"]) > 0.0015:
            print(f"warning: derived contract MDE {derived:.4f} differs from tabulated "
                  f"{r['mde_contract_pct_VAL_D1']:.3f} for {arm} {cell}")
xs = list(range(len(labels)))
c.bar([x - 0.2 for x in xs], rec, width=0.4, color="#c0561c", label="recorded (code, x1.736)")
c.bar([x + 0.2 for x in xs], con, width=0.4, color="#1f5fa8", label="contract text (no factor)")
c.axhline(THRESH, color="k", ls="--", lw=0.9, label="powered threshold 0.25 %")
c.set_yscale("log")
c.set_xticks(xs)
c.set_xticklabels(labels, fontsize=5.5)
c.set_ylabel("minimum detectable effect (%)", fontsize=8)
c.set_title("(c) MDE: code vs contract text (defect D1)", fontsize=8.5)
c.set_ylim(top=8)
c.legend(fontsize=6.5, loc="upper left")
c.grid(alpha=0.25, which="both")

# (d) planted-base sensitivity gate
d = fig.add_subplot(gs[1, 0])
cells_p = data["sensitivity_planted"]
for i, s in enumerate(cells_p):
    d.errorbar([i - 0.12], [s["known_excess_pct"]], yerr=[[s["tolerance_pct"]], [s["tolerance_pct"]]],
               fmt="D", mfc="white", color="k", capsize=4, ms=5)
    d.errorbar([i + 0.12], [s["observed_excess_pct"]], yerr=[[s["pooled_se_pct"]], [s["pooled_se_pct"]]],
               fmt="o", color="#1f5fa8", capsize=3, ms=5)
    d.annotate(f"detected {s['detected']}/{s['n_curves']}", (i, 0.0), textcoords="offset points",
               xytext=(0, 6), ha="center", fontsize=6.5)
d.axhline(DELTA, color="#888888", ls=":", lw=0.8)
d.text(2.45, DELTA, "delta 0.5 %", fontsize=6, va="bottom", ha="right")
d.set_xticks(range(len(cells_p)))
d.set_xticklabels([s["cell"] for s in cells_p])
d.set_xlim(-0.6, len(cells_p) - 0.4)
d.set_ylim(-0.3, 4.2)
d.set_ylabel("planted coverage excess (%)", fontsize=8)
d.set_title("(d) planted B+1 base: known (diamond, +-tolerance) vs observed (+-se)", fontsize=7.5)
d.grid(alpha=0.25)
d.text(0.02, 0.97, "RUN-CMFB-66b0fe", transform=d.transAxes, fontsize=6.5, va="top")

# (e) I10 null-spread ratio: recorded (draft formula) vs frozen 1.4/sqrt(N)
e = fig.add_subplot(gs[1, 1])
ylab, yy = [], 0
lo_b, hi_b = data["i10_band"]
e.axvspan(lo_b, hi_b, color="#bbbbbb", alpha=0.3)
for arm in ARMS:
    for cell in CELLS:
        r = rows[(arm, cell)]
        e.plot(r["sigma_ratio_recorded_vs_draft_formula"], yy, "s", color="#c0561c", ms=4.5)
        e.plot(r["sigma_ratio_vs_1p4_VAL_D2"], yy, "o", color="#1f5fa8", ms=4.5)
        e.plot(r["sigma_ratio_vs_1p4_RT_O5"], yy, "^", color="#2f7d4f", ms=4.5)
        ylab.append(f"{arm} {cell}")
        yy += 1
e.set_yticks(range(len(ylab)))
e.set_yticklabels(ylab, fontsize=6.5)
e.invert_yaxis()
e.set_xlim(0.6, 5.4)
e.set_xlabel("measured null sd / reference", fontsize=8)
e.set_title("(e) I10 spread ratio: band [0.75, 1.33] (defect D2)", fontsize=8.5)
e.legend(handles=[
    Line2D([0], [0], marker="s", color="#c0561c", ls="", label="recorded vs draft 0.49/sqrt(N)"),
    Line2D([0], [0], marker="o", color="#1f5fa8", ls="", label="vs 1.4/sqrt(N), VAL"),
    Line2D([0], [0], marker="^", color="#2f7d4f", ls="", label="vs 1.4/sqrt(N), RT"),
], fontsize=6, loc="upper right")
e.grid(alpha=0.25)

# (f) text panel
f = fig.add_subplot(gs[1, 2])
f.axis("off")
txt = (
    f"Decision {data['decision_id']}: {data['decision']}\n"
    f"Evidence {data['evidence_id']}: strength {data['evidence_strength']}, tier {data['claim_tier']}\n"
    f"Hypothesis {data['hypothesis_id']}: specified -> analyzed\n\n"
    "Scoped claim: no coverage difference above 0.5 % between the\n"
    "small-x base and a matched random base was observed (m = 3,\n"
    "unsigned, 107 curves, 2^14 < p <= 2^25); C24 intervals within\n"
    "+-0.04 %. Not a no-effect claim; CM structure, signed form,\n"
    "growth, cost and the 53-bit pair are untested.\n\n"
    "Defects of the frozen code, recorded, not edited:\n"
    "D1 MDE factor 1.736: powered {C24} -> {C20, C24}; Holm FAM C24\n"
    "0.0936 -> 0.1872; class unchanged.  D2 I10 reference: false\n"
    "positive in 9/9, 0.815-0.971 vs 1.4/sqrt(N).\n\n"
    f"Reviews: {data['validation_id']} passed;\n"
    f"{data['red_team_id']} requires narrowing.\n"
    "No ECDLP, rho or pair-46 claim; no ranking made."
)
f.text(0.0, 1.0, txt, va="top", ha="left", fontsize=7.2, family="monospace")

fig.suptitle(
    "EXP-CMFB-cea1d2 evidence review: recorded values from RUN-CMFB-2010d3 (t8) "
    "and runs 3dc120, 42a578, e13f0e, c71d35, 66b0fe",
    fontsize=9,
)
fig.savefig(HERE / "fig_review.svg")
fig.savefig(HERE / "fig_review.png", dpi=150)
print("ok")
