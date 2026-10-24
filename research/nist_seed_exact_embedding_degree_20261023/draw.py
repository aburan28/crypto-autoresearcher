"""Draw exact embedding-degree bit lengths from the sealed run."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
run = json.loads((HERE / "runs/exact-20261023T1811Z/exact/results.json").read_text())
rows = sorted(run["rows"], key=lambda r: (r["field_bits"], r["label"] != "omitted", r["seed_ordinal_one_based"]))
fig, ax = plt.subplots(figsize=(8.0, 6.6))
y = list(range(len(rows)))
gap = [r["field_bits"]-r["k_bits"] for r in rows]
colors = ["#db7b29" if r["label"] == "omitted" else "#3979ac" for r in rows]
ax.barh(y, gap, color=colors, height=0.7)
ax.set_yticks(y, [f"{r['field_bits']} · {r['seed_ordinal_one_based']}" for r in rows])
ax.invert_yaxis()
ax.set_xlim(0, max(gap)+0.8)
ax.set_xticks(range(max(gap)+1))
ax.set_xlabel("Field bit length minus exact embedding-degree bit length")
ax.set_ylabel("Field bits · seed ordinal")
ax.set_title("Every exact embedding degree remains close to the group-order size")
ax.grid(axis="x", alpha=0.18)
ax.set_axisbelow(True)
ax.legend(handles=[Patch(color="#db7b29", label="omitted"), Patch(color="#3979ac", label="published")], loc="lower right")
fig.tight_layout()
fig.savefig(HERE / "k_gap.svg", format="svg")
