"""Render the exact 19-row invalid-curve check as editable-source SVG."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "results.json").read_text())
keys = ["a_equals_minus_three", "b_nonzero", "wrong_curve_nonsingular",
        "Q_on_wrong_curve", "Q_off_configured_curve", "two_Q_is_identity"]
rows = sorted(data["rows"], key=lambda r: (r["field_bits"], r["label"] != "omitted", r["seed_ordinal_one_based"]))
labels = [f"{r['field_bits']} · {r['seed_ordinal_one_based']}" for r in rows]
values = [sum(r[key] for key in keys) for r in rows]
colors = ["#db7b29" if r["label"] == "omitted" else "#3979ac" for r in rows]
fig, ax = plt.subplots(figsize=(8.2, 7.4))
y = list(range(len(rows)))
ax.barh(y, values, color=colors, height=0.72)
ax.set_yticks(y, labels)
ax.invert_yaxis()
ax.set_xlim(0, 6.5)
ax.set_xticks(range(7))
ax.set_xlabel("Exact checks passed (of 6)")
ax.set_ylabel("Field bits · seed ordinal")
ax.grid(axis="x", alpha=0.18)
ax.set_axisbelow(True)
ax.legend(handles=[Patch(color="#db7b29", label="omitted"), Patch(color="#3979ac", label="published")], loc="lower right")
ax.set_title("Identical wrong-curve witness across the 19 comparable candidates")
fig.tight_layout()
fig.savefig(HERE / "surface.svg", format="svg")
