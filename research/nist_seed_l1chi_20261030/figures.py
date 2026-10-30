"""fig_null.svg: null density of log P_Delta per field (re-drawn with analyze.py's own
null_field and seed) with the 69 eligible curves from runs/results.json."""
import json, math, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analyze import primes_upto, null_field, X, L0, SEED
plt.rcParams.update({"font.size": 8, "svg.fonttype": "none"})
r = json.load(open("runs/results.json"))
primes = primes_upto(X); small = [l for l in primes if l <= L0]; large = [l for l in primes if l > L0]
rng = np.random.default_rng(SEED)
ps = sorted({int(x["p"]) for x in r["rows"]})
fig, axs = plt.subplots(2, 3, figsize=(7.2, 4.0), sharex=True)
for ax, p in zip(axs.flat, ps):
    S, mu, sd = null_field(p, small, large, rng)
    ax.hist(S + mu, bins=80, density=True, histtype="stepfilled", color="#d0d0d0", range=(-1.6, 0.9))
    xs = [x for x in r["rows"] if int(x["p"]) == p]
    for x in xs:
        pub = x["label"] == "published"
        c = "#c00" if x["name"] == "prime239v1" else ("#1b6ca8" if pub else "#7a7a7a")
        ax.axvline(x["logP_delta"], color=c, lw=1.4 if pub else 0.6, alpha=0.9 if pub else 0.5)
    ax.set_title(f"{p.bit_length()}-bit field: {len(xs)} eligible", fontsize=8)
    ax.set_yticks([])
for ax in axs[1]: ax.set_xlabel("log P_Δ (ℓ ≤ 10⁶)")
axs[1, 2].plot([], [], color="#1b6ca8", label="published"); axs[1, 2].plot([], [], color="#7a7a7a", label="unpublished")
axs[1, 2].plot([], [], color="#c00", label="prime239v1 (0.246%)"); axs[1, 2].legend(fontsize=6, frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig("fig_null.svg")
p = __import__("pathlib").Path("fig_null.svg"); p.write_text(p.read_text().replace("font-family: 'DejaVu Sans'", "font-family: 'Libertinus Serif', 'DejaVu Sans'"))
