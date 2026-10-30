"""Draws fig_lvalue.svg/png from runs/lvalues.json and the split-null study's lookelsewhere.json.
Display-only Monte Carlo (seed 20261101, 50,000 draws) for the percentile sweep and null bands.
Usage: python3 figures.py"""
import json, math, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "nist_seed_split_null_20261029"))
from analysis_lib import primes, chi  # noqa: E402
plt.rcParams.update({"font.size": 9, "svg.fonttype": "none", "font.family": "DejaVu Sans"})

d = json.load(open(os.path.join(HERE, "runs", "lvalues.json")))
le = json.load(open(os.path.join(HERE, "..", "nist_seed_split_null_20261029", "runs", "lookelsewhere.json")))
v = next(r for r in d["rows"] if r["name"] == "prime239v1"); p = int(v["p"]); D = int(v["D"])
logLhat = v["logL"][str(10 ** 8)]


def law(p, l):
    dd = p % l; n0 = 1 + chi(dd, l); npl = (l - n0 - 1) // 2; nmi = (l - n0 + 1) // 2
    if dd == 1 % l: n0 -= 1
    else: npl -= 1
    w = (npl * (l * l + l), n0 * l * l, nmi * (l * l - l)); s = sum(w)
    return tuple(x / s for x in w)


grid = le["grid"]; i = le["names"].index("prime239v1"); s_pct = le["mid_pct"][i]
NMC = 50_000; rng = np.random.default_rng(20261101)
LMAX = 10 ** 5; ells = primes(3, LMAX)
band_at = sorted(set(int(x) for x in np.unique(np.logspace(np.log10(3), 5, 120).astype(int))))
acc = np.zeros(NMC); obs = 0.0; e_pct = {}; band = {}; obs_curve = {}; gset = set(grid); bi = 0
two = -math.log1p(1 / 2)  # chi(2) = -1 for every prime-order curve here
for l in ells:
    q1, q0, _ = law(p, l); u = rng.random(NMC)
    acc -= np.log1p(-np.where(u < q1, 1.0, np.where(u < q1 + q0, 0.0, -1.0)) / l)
    obs -= math.log1p(-chi(D, l) / l)
    if l in gset: e_pct[l] = 100 * ((acc < obs).mean() + 0.5 * (acc == obs).mean())
    while bi < len(band_at) and band_at[bi] <= l:
        band[band_at[bi]] = np.percentile(acc + two, [1, 50, 99]); obs_curve[band_at[bi]] = obs + two; bi += 1

fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 3.0))
gs = [g for g in grid if g in e_pct]
a.plot(grid, s_pct, color="#999999", lw=1, label="split count S(B), unweighted")
a.plot(gs, [e_pct[g] for g in gs], color="#1b6ca8", lw=1.4, label="weighted E(B) = −Σ log(1 − χ(ℓ)/ℓ)")
a.axhline(v["pct_logL"], color="#d95f02", ls="--", lw=1, label=f"log L(1, χ), x = 10⁸: {v['pct_logL']:.2f}%")
a.set_xscale("log"); a.set_yscale("log"); a.set_xlabel("cutoff B"); a.set_ylabel("percentile under prime-order null")
a.set_title("prime239v1: percentile against cutoff", fontsize=8.5); a.legend(fontsize=6.5, loc="upper left"); a.grid(lw=0.3)
xs = sorted(band); q = np.array([band[x] for x in xs])
b.fill_between(xs, q[:, 0], q[:, 2], color="#dddddd", label="null 1–99%")
b.plot(xs, q[:, 1], color="#999999", lw=0.8, label="null median")
b.plot(xs, [obs_curve[x] for x in xs], color="#1b6ca8", lw=1.4, label="prime239v1 partial log-Euler product")
b.axhline(logLhat, color="#d95f02", ls="--", lw=1, label=f"log L̂ = {logLhat:.3f} (x = 10⁸)")
b.axvline(691, color="#444444", lw=0.5, ls=":")
b.set_xscale("log"); b.set_xlabel("truncation ℓ ≤ B"); b.set_ylabel("log of partial Euler product")
b.set_title("Partial Euler product converges by B ≈ 691", fontsize=8.5); b.set_ylim(-1.9, -0.15); b.legend(fontsize=6.5, loc="lower right", ncol=2); b.grid(lw=0.3)
fig.tight_layout()
for ext in ("svg", "png"): fig.savefig(os.path.join(HERE, f"fig_lvalue.{ext}"), dpi=200)
print("wrote fig_lvalue.svg/png")
