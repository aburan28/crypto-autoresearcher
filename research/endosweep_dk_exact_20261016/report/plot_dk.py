#!/usr/bin/env python3
"""Draw dk_exact.svg from ../dk_exact.json (recorded values only; no new computation beyond log2)."""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
doc = json.loads((HERE.parent / "dk_exact.json").read_text())
rows = [r for r in doc["curves"] if r["D_K"] != "-3"]
m3 = [r["curve"] for r in doc["curves"] if r["D_K"] == "-3"]
plt.rcParams.update({"font.size": 9, "svg.fonttype": "none"})
fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"width_ratios": [1, 1.25]})
colors = {"1": "#1f77b4", "2": "#ff7f0e", "5": "#2ca02c", "7": "#d62728"}
for f in sorted({r["conductor_f"] for r in rows}, key=int):
    sel = [r for r in rows if r["conductor_f"] == f]
    a.scatter([r["p_bits"] for r in sel], [r["log2_abs_D_K"] for r in sel], s=22, color=colors.get(f, "k"),
              label=f"f = {f}", zorder=3)
xs = [230, 520]
a.plot(xs, [x + 2 for x in xs], color="0.6", lw=1, ls="--", label="log2(4q) ≈ p bits + 2", zorder=1)
a.set_xlabel("p (bits)")
a.set_ylabel("log2 |D_K|")
a.set_title("(a) exact |D_K| against field size")
a.legend(frameon=False, loc="upper left")
names = [r["curve"].split("/")[1].replace("id-tc26-gost-3410-2012-512-", "gost-512-") for r in rows]
gaps = [math.log2(4 * int(r["p"])) - r["log2_abs_D_K"] for r in rows]
b.barh(range(len(rows)), gaps, color=[colors.get(r["conductor_f"], "k") for r in rows])
b.set_yticks(range(len(rows)))
b.set_yticklabels(names)
b.invert_yaxis()
b.set_xlabel("log2(4q) − log2 |D_K|  (bits)")
b.set_title("(b) bits lost to f² and to t²")
fig.text(0.01, 0.01, f"n = {len(rows)} curves; exact integers (PARI isprime-proved factorisations), no uncertainty. "
         f"Not shown: D_K = −3 on {', '.join(m3)}.", fontsize=7.5)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(HERE / "dk_exact.svg")
print("wrote", HERE / "dk_exact.svg")
