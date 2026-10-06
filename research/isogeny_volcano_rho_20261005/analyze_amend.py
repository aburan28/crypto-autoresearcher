import csv, glob, json, numpy as np
rng = np.random.default_rng(11); B = 4000
LV = {"crater": ["0"], "floor73": ["1", "2"], "floor2663": ["101", "102"], "bottom": ["201", "202"]}
def load(ids, m):
    o, s, ok = [], [], []
    for i in ids:
        for f in glob.glob(f"raw_amend/c{i}_m{m}_r*.csv"):
            for r in csv.DictReader(open(f)): o.append(float(r["ops"])); s.append(float(r["sec"])); ok.append(int(r["ok"]))
    return np.array(o), np.array(s), np.array(ok)
D = {l: load(ids, 0) for l, ids in LV.items()}; tau = load(["0"], 1)
out = {"all_verified": bool(all(d[2].all() for d in list(D.values()) + [tau])), "n": {l: len(d[0]) for l, d in D.items()}}
ref = D["crater"][1]
for l in ["floor73", "floor2663", "bottom"]:
    x = D[l][1]; r = rng.choice(x, (B, len(x))).mean(1) / rng.choice(ref, (B, len(ref))).mean(1)
    lo, hi = np.quantile(r, [.05, .95])
    out[l] = dict(sec_ratio=float(x.mean() / ref.mean()), ci90=[float(lo), float(hi)], equivalent_within_3pct=bool(lo > .97 and hi < 1.03),
                  ns_per_op=float(D[l][1].sum() / D[l][0].sum() * 1e9))
out["crater_ns_per_op"] = float(ref.sum() / D["crater"][0].sum() * 1e9)
out["crater_mean_ms"] = float(ref.mean() * 1e3); out["crater_tau_mean_ms"] = float(tau[1].mean() * 1e3)
out["frobenius_time_speedup"] = float(ref.mean() / tau[1].mean())
json.dump(out, open("results_amendment1.json", "w"), indent=1); print(json.dumps(out, indent=1))
