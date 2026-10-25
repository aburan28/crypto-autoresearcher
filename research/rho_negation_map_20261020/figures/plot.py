"""Plot recorded values from ../results.json and ../jumps.json (no new runs)."""
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

H = Path(__file__).resolve().parent.parent
d = json.loads((H / "results.json").read_text())
jm = json.loads((H / "jumps.json").read_text())["summary"]
S = [s for s in d["summary"] if s["bits"] != "all"]
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
b = [s["bits"] for s in S]
for walk, col, fl in (("negation", "#1f6feb", "pi/4"), ("plain", "#d1242f", "pi/2")):
    ax[0].plot(b, [s[f"mean_s_walk_{walk}"] for s in S], "o-", color=col,
               label=f"{walk}: mean walk_ops / sqrt(N)")
    ax[0].axhline(math.sqrt(math.pi / (4 if walk == "negation" else 2)), color=col, ls=":", lw=1)
ax[0].set_xlabel("bits"); ax[0].set_ylabel("walk_ops / sqrt(N)")
ax[0].set_title("index_calculus.rho, 128 paired solves per size\nfloors sqrt(pi/4), sqrt(pi/2) dotted", fontsize=10)
ax[0].legend(fontsize=8); ax[0].set_ylim(0.6, 1.8)
r = [s["ratio_plain_over_negation"] for s in S]
lo = [s["ratio_plain_over_negation"] - s["ratio_ci95"][0] for s in S]
hi = [s["ratio_ci95"][1] - s["ratio_plain_over_negation"] for s in S]
ax[1].errorbar(b, r, yerr=[lo, hi], fmt="o", color="k", capsize=3, label="plain / negation, ratio of means ± 95% (cluster bootstrap)")
ax[1].axhline(math.sqrt(2), color="#1f6feb", ls="--", lw=1, label="sqrt(2)")
ax[1].axhline(1, color="grey", lw=0.8)
ax[1].set_xlabel("bits"); ax[1].set_ylabel("walk_ops ratio")
ax[1].set_title("paired walk_ops ratio per size", fontsize=10)
ax[1].legend(fontsize=8, loc="upper left"); ax[1].set_ylim(0.8, 1.9)
fig.suptitle(f"Negation map in index_calculus.rho (seed {d['seed']}; side check r = 20/32/64: "
             + ", ".join(f"{jm[k]['mean_over_floor']:.2f}" for k in ("20", "32", "64")) + "x floor)", fontsize=10)
fig.tight_layout()
fig.savefig(H / "figures/negation_vs_plain.svg"); fig.savefig(H / "figures/negation_vs_plain.png", dpi=150)
