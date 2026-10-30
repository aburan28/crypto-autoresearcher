"""Exact within-field label permutation (published counts per field fixed) and
leave-one-curve-out pair scores on the prime cutoff grid [50, 5003].
Conditions on the 19 observed curves: tests label association, not whether
the curves are unusual relative to random curves (that is lookelsewhere.py)."""
import itertools, json, sys
import numpy as np
from analysis_lib import primes, chi, load_rows

RAW, OUT = sys.argv[1], sys.argv[2]
rows = load_rows(RAW)
ells = primes(3, 5003); grid = [l for l in ells if l >= 50]
gidx = np.array([ells.index(b) for b in grid])
X = np.array([[chi(r["D"], l) == 1 for l in ells] for r in rows], dtype=np.int32)
cum = np.cumsum(X, axis=1)[:, gidx]
fields = sorted({r["bits"] for r in rows})
members = {b: [i for i, r in enumerate(rows) if r["bits"] == b] for b in fields}
npub = {b: sum(rows[i]["label"] == "published" for i in members[b]) for b in fields}

def score(pubset, exclude=()):
    s = np.zeros(len(grid), dtype=int)
    for b in fields:
        for a in members[b]:
            if a in pubset or a in exclude: continue
            for p in members[b]:
                if p in pubset and p not in exclude: s += cum[a] > cum[p]
    return s

obs_pub = {i for i, r in enumerate(rows) if r["label"] == "published"}
obs = score(obs_pub); i691 = grid.index(691)
choices = [list(itertools.combinations(members[b], npub[b])) for b in fields]
n = ge691 = gemax = 0
for combo in itertools.product(*choices):
    s = score(set(itertools.chain(*combo))); n += 1
    ge691 += s[i691] >= obs[i691]; gemax += s.max() >= obs.max()
v1 = next(i for i, r in enumerate(rows) if r["name"] == "prime239v1")
loo = {rows[i]["name"]: score(obs_pub, exclude=(i,)).tolist() for i in range(len(rows))}
out = dict(grid=grid, n_allocations=n, observed=obs.tolist(),
           perm_p_at_691=ge691 / n, perm_p_max_over_grid=gemax / n,
           leave_one_out=loo,
           without_prime239v1=dict(pairs_total=25 - 5, at_691=loo["prime239v1"][i691],
                                   max=max(loo["prime239v1"]), median_over_grid=float(np.median(loo["prime239v1"]))))
json.dump(out, open(OUT, "w"))
print({k: v for k, v in out.items() if k not in ("grid", "observed", "leave_one_out")})
