"""Figure for the superseding analysis. Reads superseding_result.json and RUN-CMFB-2010d3/raw-result.json only."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

H = Path(__file__).resolve().parent
rec = json.loads((H.parents[1] / "runs/RUN-CMFB-2010d3/raw-result.json").read_text())
sup = json.loads((H / "superseding_result.json").read_text())["superseding"]
keys = list(rec["tables"])
lab = [k.replace("|", "\n") for k in keys]
x = np.arange(len(keys))
col = {"FAM": "#1f5fa8", "N-A": "#c0561c", "N-B": "#2f7d4f"}

fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))

a = ax[0]
a.bar(x - 0.2, [rec["tables"][k]["mde"] * 100 for k in keys], 0.4, color="#999999", label="recorded (code, x1.736)")
a.bar(x + 0.2, [sup["tables"][k]["mde"] * 100 for k in keys], 0.4, color="#1f5fa8", label="superseding (contract text)")
a.axhline(0.25, color="k", ls="--", lw=1, label="powered threshold 0.25 %")
a.set_yscale("log"); a.set_xticks(x); a.set_xticklabels(lab, fontsize=6)
a.set_ylabel("minimum detectable effect (%)"); a.set_title("(a) MDE (D1): C20 crosses the threshold", fontsize=9)
a.legend(fontsize=6.5, loc="upper left"); a.set_ylim(top=8)

b = ax[1]
b.axvspan(0.75, 1.33, color="#dddddd")
y = np.arange(len(keys))
b.scatter([rec["tables"][k]["sigma_ratio"] for k in keys], y, marker="s", color="#c0561c", label="recorded vs draft 0.49/sqrt(N)")
b.scatter([sup["tables"][k]["sigma_ratio"] for k in keys], y, marker="o", color="#1f5fa8", label="superseding vs 1.4/sqrt(N)")
b.set_yticks(y); b.set_yticklabels([k.replace("|", " ") for k in keys], fontsize=7); b.invert_yaxis()
b.set_xlabel("measured null sd / reference"); b.set_title("(b) I10 (D2): band [0.75, 1.33]", fontsize=9)
b.set_xlim(0.5, 4.6); b.legend(fontsize=6.5, loc="upper right")

c = ax[2]
for i, k in enumerate(keys):
    t = sup["tables"][k]
    c.errorbar(i, t["T"] * 100, yerr=[[t["T"] * 100 - t["ci95"][0] * 100], [t["ci95"][1] * 100 - t["T"] * 100]],
               fmt="o", color=col[t["arm"]], mfc=("white" if not sup["cells"][t["cell"]]["powered"] else col[t["arm"]]), capsize=3)
c.axhspan(-0.5, 0.5, color="#eeeeee", zorder=0); c.axhline(0, color="k", lw=0.8)
c.set_ylim(-0.12, 0.12); c.set_xticks(x); c.set_xticklabels(lab, fontsize=6)
c.set_ylabel("T: mean coverage ratio - 1 (%)")
c.set_title("(c) T and 95 % interval, unchanged by D1/D2 (zoom; +-0.5 % band off scale;\nhollow: C16, unpowered)", fontsize=8)
fig.suptitle("EXP-CMFB-cea1d2 superseding analysis (non-official): recorded RUN-CMFB-2010d3 vs contract-text constants", fontsize=10)
fig.tight_layout()
fig.savefig(H / "fig_superseding.svg"); fig.savefig(H / "fig_superseding.png", dpi=130)
print("ok")
