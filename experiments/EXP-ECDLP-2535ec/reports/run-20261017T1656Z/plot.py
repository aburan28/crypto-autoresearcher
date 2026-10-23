"""Draw the recorded double-smoothness yield ratios of EXP-ECDLP-2535ec (RUN-ECDLP-d214b6).

Values are copied from the run's raw-result.json into data.json; nothing is recomputed."""
import json, pathlib
import matplotlib; matplotlib.use("svg")
import matplotlib.pyplot as plt
here = pathlib.Path(__file__).parent
d = json.loads((here / "data.json").read_text()); boxes = d["boxes"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
groups = sorted(set((b["d"], b["bits"]) for b in boxes)); xs = {g: i for i, g in enumerate(groups)}
for key, ax, title in (("ratio_vs_random", a1, "special vs matched random prime (same box)"), ("ratio_vs_same", a2, "special vs same prime, generic cubic/quartic/quintic")):
    ci = "ci_vs_random" if key == "ratio_vs_random" else "ci_vs_same"
    for b in boxes:
        x = xs[(b["d"], b["bits"])] + {(150, 512): -0.3, (150, 2048): -0.1, (300, 512): 0.1, (300, 2048): 0.3}[(b["A"], b["B_s"])] + (b["seed"] - 2) * 0.03
        ax.errorbar(x, b[key], yerr=[[b[key] - b[ci][0]], [b[ci][1] - b[key]]], fmt="o", ms=3, color="#4a7bb7", ecolor="#4a7bb7", alpha=0.7, capsize=2)
    ax.axhline(1.0, ls="--", color="k", lw=1); ax.set_yscale("log")
    ax.set_xticks(range(len(groups))); ax.set_xticklabels([f"d={g[0]}\n{g[1]} bits" for g in groups], fontsize=8)
    ax.set_ylabel("recorded yield ratio (bootstrap 95% CI)", fontsize=8); ax.set_title(title, fontsize=9)
a1.text(0.01, 0.97, "per group, left to right: (A,B_s) = (150,512), (150,2048), (300,512), (300,2048); seeds 1-3 jittered", transform=a1.transAxes, fontsize=6, va="top")
fig.suptitle("RUN-ECDLP-d214b6: counted double-smoothness yield, 72 boxes (18 cells x 4 (A,B_s))", fontsize=9)
fig.tight_layout(); fig.savefig(here / "yield.svg")
