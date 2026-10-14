"""Draw recorded census quantities for EXP-AUXIN-fef6ac (RUN-AUXIN-aa27b4).

Values are copied from the runner's stage1/census.json and stage1/control-table.json;
nothing is recomputed."""
import json, pathlib
import matplotlib; matplotlib.use("svg")
import matplotlib.pyplot as plt
here = pathlib.Path(__file__).parent
d = json.loads((here / "data.json").read_text()); c, t = d["census"], d["control"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3.4))
a1.bar(["B_minus", "B_plus", "B_rho"], [c["B_minus"], c["B_plus"], c["B_rho"]], color=["#4a7bb7", "#6aa56a", "#999999"])
a1.set_ylabel("recorded cost value (runner units)"); a1.set_title("recorded B values (r=61)")
a2.bar(["pinned_ratio\n(d-=6, d+=2)", "d2_ratio\n(d-=d+=2 null)"], [c["pinned_ratio"], t["d2_null"]["ratio"]], color=["#4a7bb7", "#999999"])
a2.axhline(t["d2_null"]["threshold"], ls="--", color="k", lw=1, label=f"recorded threshold {t['d2_null']['threshold']}")
a2.set_ylabel("recorded ratio (dimensionless)"); a2.set_title("recorded ratios"); a2.legend(fontsize=8)
fig.suptitle("RUN-AUXIN-aa27b4: E: y^2=x^3+x+1 over F_10007, N=10065", fontsize=10)
fig.tight_layout(); fig.savefig(here / "census.svg")
