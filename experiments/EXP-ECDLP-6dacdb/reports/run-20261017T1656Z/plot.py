"""Draw the recorded census of EXP-ECDLP-6dacdb (RUN-ECDLP-c770f6 part A, RUN-ECDLP-393d10 part B).

Values are copied from both runs' raw-result.json into data.json; the only arithmetic is
k/l per recorded row (labelled as derived) and bar placement."""
import json, pathlib, math
import matplotlib; matplotlib.use("svg")
import matplotlib.pyplot as plt
here = pathlib.Path(__file__).parent
d = json.loads((here / "data.json").read_text())
A = d["part_a"]; B = d["part_b"]
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(11, 3.6))
# (1) recorded t histogram, both arms
h = A["tests"]["t_histogram"]; labels = [f"{lo}-{hi}" if hi < 10**9 else f">={lo}" for lo, hi in h["bins"]]
x = range(len(labels)); w = 0.38
a1.bar([i - w/2 for i in x], h["special"], w, color="#4a7bb7", label=f"special (n={A['tests']['n_curves']['special']})")
a1.bar([i + w/2 for i in x], h["random"], w, color="#999999", label=f"random (n={A['tests']['n_curves']['random']})")
a1.set_xticks(list(x)); a1.set_xticklabels(labels, fontsize=8); a1.set_xlabel("t = (p-1)/k bin (recorded)"); a1.set_ylabel("curves (count)")
a1.set_title(f"part A: recorded t histogram; perm. p={h['permutation_p_value']:.3f}", fontsize=8); a1.legend(fontsize=7)
# (2) derived k/l per curve, by arm
for arm, c in (("special", "#4a7bb7"), ("random", "#999999")):
    vals = [k / l for cell in A["cells"] if cell["arm"] == arm for k, l in zip(cell["k_values"], cell["l_values"])]
    a2.hist([math.log2(v) for v in vals], bins=30, alpha=0.6, color=c, label=f"{arm} ({len(vals)} curves)")
a2.set_xlabel("log2(k/l), derived per recorded row"); a2.set_ylabel("curves (count)"); a2.set_title("part A: embedding degree relative to l", fontsize=8); a2.legend(fontsize=7)
# (3) part B k* per deployed curve
names = [r["name"] for r in B["rows"]]; consts = list(B["constants"].keys())
for i, cst in enumerate(consts):
    a3.bar([j + (i - 1) * 0.27 for j in range(len(names))], [r["transfer_threshold"][cst]["k_star"] for r in B["rows"]], 0.27, label=cst.replace("_", " "))
a3.set_xticks(range(len(names))); a3.set_xticklabels(names, fontsize=7, rotation=20); a3.set_ylabel("recorded k* (transfer cheaper than rho below k*)")
a3.set_title("part B: k* per curve; measured k > 10^6 for all six", fontsize=8); a3.legend(fontsize=6)
fig.suptitle("RUN-ECDLP-c770f6 (part A, 16-bit primes, 64 curves per cell) and RUN-ECDLP-393d10 (part B)", fontsize=9)
fig.tight_layout(); fig.savefig(here / "census.svg")
