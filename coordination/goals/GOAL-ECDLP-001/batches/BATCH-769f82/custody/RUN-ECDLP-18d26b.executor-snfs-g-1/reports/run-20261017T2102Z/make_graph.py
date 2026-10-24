"""Draws graph.svg from the recorded raw-result.json only (maximum recorded Rmax per summary key and arm)."""
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
raw = json.load(open("experiments/EXP-ECDLP-84af7b/runs/RUN-ECDLP-18d26b/raw-result.json"))
S = raw["summary"]
keys = sorted(S)
def mx(rows):
    v = [r["Rmax"] for r in rows if r.get("Rmax") is not None]
    return max(v) if v else None
arms = [("cyclotomic", "tab:blue"), ("abelian_control", "tab:orange"), ("random_split", "tab:green")]
fig, ax = plt.subplots(figsize=(11, 4))
w = 0.27
for i, (arm, col) in enumerate(arms):
    ys = [mx(S[k].get(arm) or []) for k in keys]
    xs = [j + (i - 1) * w for j, y in enumerate(ys) if y is not None]
    ax.bar(xs, [y for y in ys if y is not None], w, label=arm, color=col)
ax.set_xticks(range(len(keys))); ax.set_xticklabels(keys, rotation=90, fontsize=6)
ax.set_ylabel("max recorded Rmax over seeds/curves (relation-yield ratio)")
ax.set_title("EXP-ECDLP-84af7b RUN-ECDLP-18d26b: recorded maximum Rmax per (c, d) cell and arm")
ax.legend(); fig.tight_layout(); fig.savefig(sys.argv[1] if len(sys.argv) > 1 else "graph.svg")
