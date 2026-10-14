"""Draw recorded census and control counts for EXP-CSIDH-999626 (RUN-CSIDH-2ea205).

Values are copied from the runner's stage1/census.json and stage1/control-table.json;
nothing is recomputed."""
import json, pathlib
import matplotlib; matplotlib.use("svg")
import matplotlib.pyplot as plt
here = pathlib.Path(__file__).parent
d = json.loads((here / "data.json").read_text())
groups = [("census G1", d["census"]["G1"]), ("census G2", d["census"]["G2"]),
          ("N1 control G1", d["N1_control"]["G1"]), ("N1 control G2", d["N1_control"]["G2"])]
keys = ["C_M2", "C_Mfree", "C_blind_M2", "C_blind_Mfree"]
fig, ax = plt.subplots(figsize=(7.5, 3.6))
w = 0.2
for i, k in enumerate(keys):
    ax.bar([j + (i - 1.5) * w for j in range(len(groups))], [g[k] for _, g in groups], w, label=k)
ax.set_xticks(range(len(groups)), [n for n, _ in groups])
ax.set_ylabel("recorded count (integer)")
ax.set_title("RUN-CSIDH-2ea205: recorded counts per arm (p=419, N=9)")
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(here / "counts.svg")
