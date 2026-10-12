"""Extract per-curve TT (m=4) relation counts per arm from the RA-04 census rows.

Review computation for TASK-20261009-bfdc5b (red team). Reads only
experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-table/rows.jsonl.gz and
experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-p0-design/design.json.
No randomness. Writes a compact npz + json to the scratch directory and a
summary json to attacks/out/.

n_{X,j} is taken as harvest.TT.at_stop.relations_nonformal (CC-7: distinct
nonformal relations, CC-1..CC-3). An independent CC-1 recount from the harvest
rows is done separately (recount_cc1.py) on the arms this review uses.
"""
import gzip, json, sys, os
import numpy as np

ROOT = "experiments/EXP-PFDR-0b3699/runs"
SCR = sys.argv[1]
OUT = sys.argv[2]
ARMS = ["small_x", "small_x_offset", "subgroup", "random_sub_r0", "random_sub_r1",
        "random_sub_r2", "known_null_sub", "planted_sub"]

design = json.load(open(f"{ROOT}/RUN-PFDR-0b3699-p0-design/design.json"))
curves = design["curves"]
key2idx = {(c["bits"], c["curve"]): i for i, c in enumerate(curves)}
n = len(curves)
cnt = {a: np.full(n, -1, dtype=np.int64) for a in ARMS}
dist = {a: np.full(n, -1, dtype=np.int64) for a in ARMS}
sign = {a: np.full(n, -1, dtype=np.int64) for a in ARMS}
size = {a: np.full(n, -1, dtype=np.int64) for a in ARMS}
status = {a: [None] * n for a in ARMS}
mult = {a: {} for a in ARMS}
tb = {a: np.full(n, -1, dtype=np.int64) for a in ARMS}
pois = {a: np.full(n, np.nan) for a in ARMS}
params = {"small_x_offset": [None] * n, "planted_sub": [None] * n, "small_x": [None] * n}
curve_mismatch = 0
seen = 0
with gzip.open(f"{ROOT}/RUN-PFDR-0b3699-table/rows.jsonl.gz", "rt") as f:
    for line in f:
        r = json.loads(line)
        if r.get("method") != "ic_m4" or r.get("mode") != "table":
            raise SystemExit(f"unexpected row shape {r.get('method')} {r.get('mode')}")
        i = key2idx[(r["bits"], r["curve"])]
        c = curves[i]
        if (r["p"], r["a"], r["b"], r["N"], r["P"]) != (c["p"], c["a"], c["b"], c["N"], c["P"]):
            curve_mismatch += 1
        a = r["arm"]
        seen += 1
        status[a][i] = r["status"]
        size[a][i] = r["fb_size"]
        if a in params:
            params[a][i] = r["fb_params"]
        h = r.get("harvest") or {}
        tt = (h.get("TT") or {}).get("at_stop")
        if tt is not None:
            cnt[a][i] = tt["relations_nonformal"]
            dist[a][i] = tt["relations_distinct"]
            sign[a][i] = tt["relations_distinct_sign"]
            pois[a][i] = tt["poisson_mean"]
            for k, v in tt["multiplicity_histogram"].items():
                mult[a][k] = mult[a].get(k, 0) + v
        tbb = (h.get("TB") or {}).get("at_stop")
        if tbb is not None:
            tb[a][i] = tbb["relations_nonformal"]

bits = np.array([c["bits"] for c in curves])
cid = np.array([c["curve"] for c in curves])
s_sub = np.array([c["s_sub"] for c in curves])
mu = np.array([c["mu_model"] for c in curves])
Nn = np.array([c["N"] for c in curves], dtype=np.float64)
np.savez(os.path.join(SCR, "counts.npz"), bits=bits, curve=cid, s_sub=s_sub, mu_model=mu, N=Nn,
         **{f"cnt_{a}": cnt[a] for a in ARMS}, **{f"dist_{a}": dist[a] for a in ARMS},
         **{f"sign_{a}": sign[a] for a in ARMS}, **{f"size_{a}": size[a] for a in ARMS},
         **{f"tb_{a}": tb[a] for a in ARMS}, **{f"pois_{a}": pois[a] for a in ARMS})
json.dump({"status": status, "params": params}, open(os.path.join(SCR, "rowmeta.json"), "w"))
summ = {
    "rows_seen": seen, "curves": n, "curve_identity_mismatch": curve_mismatch,
    "status_counts": {a: {s: status[a].count(s) for s in set(status[a])} for a in ARMS},
    "size_ne_s_sub": {a: int(np.sum(size[a] != s_sub)) for a in ARMS},
    "nonformal_ne_distinct": {a: int(np.sum(cnt[a] != dist[a])) for a in ARMS},
    "multiplicity_histogram_TT": mult,
}
json.dump(summ, open(OUT, "w"), indent=1, sort_keys=True)
print(json.dumps(summ, indent=1, sort_keys=True))
