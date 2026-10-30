"""Draw the two run-report graphs from the recorded t8 raw-result.json only.
No new computation: values are read from RUN-CMFB-2010d3/raw-result.json."""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2] / "runs" / "RUN-CMFB-2010d3" / "raw-result.json"
r = json.loads(root.read_text())
out = Path(__file__).resolve().parent
cells = ["C16", "C20", "C24"]
arms = ["FAM", "N-A", "N-B"]
col = {"FAM": "#1f5fa8", "N-A": "#c0561c", "N-B": "#2f7d4f"}

fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw={"width_ratios": [1.5, 1]})
a = ax[0]
for j, arm in enumerate(arms):
    xs, ys, lo, hi, ns = [], [], [], [], []
    for i, c in enumerate(cells):
        t = r["tables"].get(f"{arm}|{c}")
        if not t:
            continue
        xs.append(i + (j - 1) * 0.22)
        ys.append(100 * t["T"]); lo.append(100 * (t["T"] - t["ci95"][0])); hi.append(100 * (t["ci95"][1] - t["T"]))
        ns.append(t["n"])
    a.errorbar(xs, ys, yerr=[lo, hi], fmt="o", color=col[arm], capsize=3, label=arm)
    for x, y, n in zip(xs, ys, ns):
        a.annotate(f"n={n}", (x, y), textcoords="offset points", xytext=(5, 6), fontsize=7, color=col[arm])
a.axhspan(-0.5, 0.5, color="#bbbbbb", alpha=0.25, label="±δ = ±0.5 %")
a.axhline(0, color="k", lw=0.6)
a.set_xticks(range(3)); a.set_xticklabels([f"{c}\n({'powered' if r['cells'][c]['powered'] else 'not powered'})" for c in cells])
a.set_ylabel("recorded T: mean coverage ratio − 1  (%)")
a.set_title("Coverage excess T vs matched random base, 95 % interval")
a.legend(fontsize=8, loc="upper right"); a.grid(alpha=0.25)

b = ax[1]
labels, vals, wr = [], [], []
for arm in arms:
    for c in cells:
        p = r["scan_efficiency"]["pools"].get(f"{arm}|{c}")
        if p:
            labels.append(f"{arm}|{c}"); vals.append(p["R_pool"]); wr.append(p["R_wrong"])
y = range(len(labels))
b.axvspan(1.98, 2.02, color="#bbbbbb", alpha=0.3, label="gate [1.98, 2.02]")
b.plot(vals, y, "o", color="#1f5fa8", label="R (f(x) residuosity)")
b.plot(wr, y, "s", color="#c0561c", label="R_wrong (Legendre of x)")
b.set_yticks(list(y)); b.set_yticklabels(labels, fontsize=7); b.invert_yaxis()
b.set_xlim(0.95, 2.05); b.set_xlabel("scan efficiency ratio")
b.set_title("qr_window control by pool")
b.legend(fontsize=7, loc="center", bbox_to_anchor=(0.5, 0.5)); b.grid(alpha=0.25)
fig.suptitle("EXP-CMFB-cea1d2, RUN-CMFB-2010d3 (t8), recorded values only", fontsize=9)
fig.tight_layout()
fig.savefig(out / "fig_run_summary.svg")
fig.savefig(out / "fig_run_summary.png", dpi=150)
print("ok")
