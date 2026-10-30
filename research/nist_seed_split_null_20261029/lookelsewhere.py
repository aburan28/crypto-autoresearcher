"""Fine cutoff grid and look-elsewhere Monte Carlo under the prime-order null.

For each prime cutoff B in [50, 5003]: within-field pair score (omitted split
count > published split count; 25 pairs) and per-curve mid-percentiles.
Monte Carlo: 19 synthetic curves with the archived fields and labels, split
indicators drawn independently per prime from the prime-order null; reports
P(score at 691 >= observed), P(max over grid >= observed max), and the min
published percentile tail. Seed fixed.
"""
import json, sys
import numpy as np
from analysis_lib import primes, probs, chi, load_rows

RAW, OUT, NREP, SEED = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rows = load_rows(RAW)
ells = primes(3, 5003); grid = [l for l in ells if l >= 50]
gidx = np.array([ells.index(b) for b in grid])
Q = np.array([[probs(r["p"], l)[0] for l in ells] for r in rows])          # 19 x L
X = np.array([[chi(r["D"], l) == 1 for l in ells] for r in rows], dtype=np.int32)
omit = [i for i, r in enumerate(rows) if r["label"] == "omitted"]
pub = [i for i, r in enumerate(rows) if r["label"] == "published"]
pairs = [(a, b) for a in omit for b in pub if rows[a]["bits"] == rows[b]["bits"]]
A = np.array([a for a, _ in pairs]); Bp = np.array([b for _, b in pairs])

def score(cum):                       # cum: (..., 19, G)
    return (cum[..., A, :] > cum[..., Bp, :]).sum(axis=-2)

obs_cum = np.cumsum(X, axis=1)[:, gidx]
obs = score(obs_cum)                  # G
i691 = grid.index(691)

# exact per-curve mid-percentiles on the grid (incremental Poisson-binomial)
pct = np.zeros((len(rows), len(grid)))
for i in range(len(rows)):
    f = np.zeros(len(ells) + 2); f[0] = 1.0; gi = 0
    for j, q in enumerate(Q[i]):
        f[1:] = f[1:] * (1 - q) + f[:-1] * q; f[0] *= (1 - q)
        if gi < len(grid) and ells[j] == grid[gi]:
            k = obs_cum[i, gi]; pct[i, gi] = 100 * (f[:k].sum() + f[k] / 2); gi += 1

rng = np.random.default_rng(SEED)
ge691 = 0; gemax = 0; minpub = []; maxsc = []; chunk = 500
for s in range(0, NREP, chunk):
    m = min(chunk, NREP - s)
    sim = (rng.random((m, len(rows), len(ells))) < Q).astype(np.int16)
    cum = np.cumsum(sim, axis=2)[:, :, gidx]
    sc = score(cum)                   # m x G
    ge691 += int((sc[:, i691] >= obs[i691]).sum())
    gemax += int((sc.max(axis=1) >= obs.max()).sum()); maxsc += sc.max(axis=1).tolist()

out = dict(grid=grid, pair_score=obs.tolist(), pairs_total=len(pairs),
           names=[r["name"] for r in rows], labels=[r["label"] for r in rows],
           mid_pct=pct.round(4).tolist(), nrep=NREP, seed=SEED,
           p_score_at_691_ge_obs=(ge691 + 1) / (NREP + 1),
           obs_max_score=int(obs.max()), argmax_B=[grid[i] for i in np.flatnonzero(obs == obs.max())],
           p_max_over_grid_ge_obs_max=(gemax + 1) / (NREP + 1),
           null_max_score_quantiles={q: float(np.quantile(maxsc, q)) for q in (0.5, 0.9, 0.99)})
json.dump(out, open(OUT, "w"))
print({k: v for k, v in out.items() if k not in ("grid", "pair_score", "names", "labels", "mid_pct")})
