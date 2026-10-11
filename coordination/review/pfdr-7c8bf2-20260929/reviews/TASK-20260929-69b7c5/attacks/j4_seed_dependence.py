"""J4 / J6: Monte Carlo error of the frozen interval endpoints against the exclusion margins.

The frozen procedure fixes the bootstrap seed at 0, so its outcome id is reproducible; its
evidential content should not depend on that seed.  With 2000 replicates the 2.5% and 97.5%
endpoints carry Monte Carlo error; S6's lower end clears 1/12 by 0.0008 and S7's lower end
misses 0 by 0.0002.  For bootstrap seeds 0..499, stats.bootstrap_slope (literal call, groups =
bits, reps = 2000, level = 0.95) on all eight primary series (12..32) on the committed rows,
then the F-2/F-3 exclusion per series and the outcome id with every other condition held at
its archived value (min ratio 1.4835, P6 overlap true, all point estimates inside their
windows -- none of these depends on the bootstrap seed except P6, which is not recomputed).
Also: row-order sensitivity -- S6 rows sorted by (bits, curve) instead of file order, seed 0.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

stats = C.load_stats()
SEEDS = range(500)
names = list(C.SERIES)
data = {}
for name in names:
    data[name] = C.xs_ys(C.series_rows(name))
res = {"seeds": [SEEDS.start, SEEDS.stop - 1], "per_series": {}, "outcomes": {}}
ex = {n: [] for n in names}
lo_ = {n: [] for n in names}
hi_ = {n: [] for n in names}
for s in SEEDS:
    for name in names:
        xs, ys, gs = data[name]
        v = stats.bootstrap_slope(xs, ys, groups=gs, reps=C.REPS, level=C.LEVEL, seed=s)
        th = C.model_value(C.SERIES[name][1])
        lo_[name].append(v["lo"])
        hi_[name].append(v["hi"])
        ex[name].append(not (v["lo"] <= th <= v["hi"]))
for name in names:
    L, H = np.array(lo_[name]), np.array(hi_[name])
    res["per_series"][name] = {"p_exclude_over_seeds": float(np.mean(ex[name])),
                               "lo_mean": float(L.mean()), "lo_sd_over_seeds": float(L.std(ddof=1)),
                               "hi_mean": float(H.mean()), "hi_sd_over_seeds": float(H.std(ddof=1)),
                               "seed0": [lo_[name][0], hi_[name][0]]}
    print("%-22s P(exclude over seeds)=%.3f lo=%.4f+-%.4f hi=%.4f+-%.4f seed0=[%.4f, %.4f]" % (
        name, np.mean(ex[name]), L.mean(), L.std(ddof=1), H.mean(), H.std(ddof=1), lo_[name][0], hi_[name][0]),
        flush=True)
M = np.array([ex[n] for n in names]).T
res["outcomes"] = {"OUT-SLOPE-INTERVAL": float(M.any(1).mean()), "OUT-CONSISTENT": float((~M.any(1)).mean()),
                   "S6_only": float((M[:, names.index("S6-smallx")] & (M.sum(1) == 1)).mean()),
                   "S7_excludes": float(M[:, names.index("S7-smallx")].mean()),
                   "S6_and_S7": float((M[:, names.index("S6-smallx")] & M[:, names.index("S7-smallx")]).mean())}
print("outcome distribution over seeds:", res["outcomes"])
# row-order sensitivity at seed 0
rows = sorted(C.series_rows("S6-smallx"), key=lambda r: (r["bits"], r["curve"]))
xs, ys, gs = C.xs_ys(rows)
v = stats.bootstrap_slope(xs, ys, groups=gs, reps=C.REPS, level=C.LEVEL, seed=0)
res["S6_rows_sorted_by_bits_curve_seed0"] = v
print("S6 rows sorted by (bits, curve), seed 0:", v)
print(C.dump("j4_seed_dependence.json", res))
