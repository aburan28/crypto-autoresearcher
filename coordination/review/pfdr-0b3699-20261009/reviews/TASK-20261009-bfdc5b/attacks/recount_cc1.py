"""Independent CC-1..CC-3 recount of TT relations at m = 4 from every job's harvest rows,
and the planted-vector membership for planted_sub (PC-R iii input to J-PLANT).
TASK-20261009-bfdc5b. Written from EXP-PFDR-011cd0 counting_conventions CC-1..CC-3
only; shares no code with harvest.py or analyze_a.py. Deterministic.
"""
import glob
import gzip
import json
import sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C

OUT = sys.argv[2]
ROOT = "experiments/EXP-PFDR-0b3699/runs"
design = json.load(open(f"{ROOT}/RUN-PFDR-0b3699-p0-design/design.json"))
curves = design["curves"]
key2i = {(c["bits"], c["curve"]): i for i, c in enumerate(curves)}
meta = json.load(open(f"{C.SCR}/rowmeta.json"))
d = C.load()


def monic(vec, N):
    """vec: dict with integer keys (base index) and 'k', 'r'. Returns tuple or None (zero)."""
    items = sorted((k, v % N) for k, v in vec.items() if isinstance(k, int))
    items = [(k, v) for k, v in items if v]
    kc = vec.get("k", 0) % N
    rh = vec.get("r", 0) % N
    if items:
        lead = items[0][1]
    elif kc:
        lead = kc
    elif rh:
        lead = rh
    else:
        return None
    inv = pow(lead, -1, N)
    return (tuple((k, v * inv % N) for k, v in items), kc * inv % N, rh * inv % N)


def rowvec(r):
    v = {int(i): int(c) for i, c in r["coeffs"]}
    v["k"] = int(r["kcoef"])
    v["r"] = int(r["rhs"])
    return v


def sub(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) - v
    return out


groups = defaultdict(lambda: defaultdict(list))  # (i, arm) -> first-element key -> [rows]
nrows = 0
classes = defaultdict(int)
for fn in sorted(glob.glob(f"{ROOT}/RUN-PFDR-0b3699-table/attempt-1/jobs/*/harvest-rows.jsonl.gz")):
    with gzip.open(fn, "rt") as f:
        for line in f:
            r = json.loads(line)
            classes[(r["class"], r["m"], r["mode"])] += 1
            if r["class"] != "TT":
                continue
            nrows += 1
            i = key2i[(r["bits"], r["curve"])]
            fk = json.dumps(r["elements"][0], sort_keys=True)
            groups[(i, r["arm"])][fk].append(r)

ARMS = ["small_x", "small_x_offset", "subgroup", "random_sub_r0", "random_sub_r1", "random_sub_r2",
        "known_null_sub", "planted_sub"]
recount = {a: np.zeros(len(curves), dtype=np.int64) for a in ARMS}
multh = {a: defaultdict(int) for a in ARMS}
planted_present = np.zeros(len(curves), dtype=bool)
planted_mult = np.zeros(len(curves), dtype=np.int64)
cert_bad = 0
for (i, arm), g in groups.items():
    N = curves[i]["N"]
    mult = defaultdict(int)
    for fk, rows in g.items():
        vecs = [rowvec(r) for r in rows]
        for r in rows:
            if not r.get("cert_ok", True):
                cert_bad += 1
        for j in range(len(vecs)):
            mv = monic(vecs[j], N)
            if mv is not None:
                mult[mv] += 1
            for ii in range(j):
                mv = monic(sub(vecs[j], vecs[ii]), N)
                if mv is not None:
                    mult[mv] += 1
    recount[arm][i] = len(mult)
    for v in mult.values():
        multh[arm][v] += 1
    if arm == "planted_sub":
        prm = meta["params"]["planted_sub"][i]
        tt = [pr for pr in prm["planted_relations"] if pr["class"] == "TT"]
        assert len(tt) == 1, (i, prm)
        vec = {int(ix): int(sg) for ix, sg in zip(tt[0]["indices"], tt[0]["signs"])}
        vec["k"] = 0
        vec["r"] = 0
        pv = monic(vec, N)
        planted_present[i] = pv in mult
        planted_mult[i] = mult.get(pv, 0)

mism = {a: int((recount[a] != d[f"cnt_{a}"]).sum()) for a in ARMS}
np.savez(f"{C.SCR}/recount.npz", **{f"rc_{a}": recount[a] for a in ARMS}, planted_present=planted_present,
         planted_mult=planted_mult)
n_tt = [meta["params"]["planted_sub"][i]["n_tt"] for i in range(len(curves))]
skipped = sum(1 for i in range(len(curves)) if meta["params"]["planted_sub"][i]["skipped_tuples"])
tt_idx = {}
for i in range(len(curves)):
    t = tuple(next(pr for pr in meta["params"]["planted_sub"][i]["planted_relations"] if pr["class"] == "TT")["indices"])
    tt_idx[str(t)] = tt_idx.get(str(t), 0) + 1
res = {"task": "TASK-20261009-bfdc5b", "what": "CC-1 recount of TT relations from harvest rows",
       "harvest_row_classes": {str(k): v for k, v in classes.items()}, "TT_rows": nrows,
       "cert_ok_false_rows": cert_bad,
       "recount_totals": {a: int(recount[a].sum()) for a in ARMS},
       "census_totals": {a: int(d[f"cnt_{a}"].sum()) for a in ARMS},
       "curves_recount_ne_census": mism,
       "multiplicity_recount": {a: dict(sorted(multh[a].items())) for a in ARMS},
       "planted": {"curves": len(curves), "planted_TT_vector_present": int(planted_present.sum()),
                   "absent_curves": [(curves[i]["bits"], curves[i]["curve"]) for i in np.nonzero(~planted_present)[0]],
                   "planted_vector_multiplicity_hist": np.bincount(planted_mult).tolist(),
                   "n_tt_values": sorted(set(n_tt)), "curves_with_skipped_tuples": skipped,
                   "TT_plant_index_tuples": tt_idx}}
C.jdump(res, OUT)
print(json.dumps(res, indent=1, default=str)[:4000])
