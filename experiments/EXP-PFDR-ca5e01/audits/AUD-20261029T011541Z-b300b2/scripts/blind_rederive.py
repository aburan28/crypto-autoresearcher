#!/usr/bin/env python3
"""Blind re-derivation of the primary metric (kappa per cell, z, z_cal, class, calibration,
outcome) of EXP-PFDR-ca5e01 from the raw job records, using only the definitions in
specification.yaml (statistics, cell_classes, calibration_gate, outcome_rules).

Does not import or read run.py, check.py, paircount.c or the producer's analysis code.
Compares to RUN-PFDR-b7c582/analysis.json and raw-result.json /summary only AFTER computing.
Usage: blind_rederive.py <experiment_dir>
"""
import json, math, sys, statistics
import numpy as np
from decimal import Decimal, ROUND_HALF_EVEN

exp = sys.argv[1]
runs = exp + "/runs/"
NREP = 20


def load_jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


# ---- cell grid from the specification text -------------------------------------------
def spec_cells():
    out = []
    for bits in (16, 18, 20, 22):
        for th in (0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65):
            for d in (1, 2, 3):
                x = 2.0 ** (bits * th) / 2
                # 'round' read as half-away-from-zero and as banker's; report if they differ
                r1 = int(math.floor(x + 0.5))
                r2 = round(x)
                if r1 != r2:
                    print("NOTE round ambiguity", bits, th, x)
                b = 2 * r2
                if 16 <= b <= 8192:
                    out.append((f"b{bits}-t{th:.2f}-d{d}", bits, th, d, b))
    return out


cells = spec_cells()
print("spec grid cells:", len(cells))
design = json.load(open(runs + "RUN-PFDR-93c865/design.json"))
dmap = {c["cell"]: c for c in design["cells"]}
assert set(dmap) == {c[0] for c in cells}, "design cell ids differ from spec grid"
assert all(dmap[c[0]]["b"] == c[4] for c in cells), "design b differs from spec"
print("design.json cells equal spec grid (ids and b): OK")

# ---- pilot sizing re-derivation ------------------------------------------------------
pil = load_jsonl(runs + "RUN-PFDR-93c865/pilot-jobs.jsonl")
bycell = {}
for r in pil:
    assert r["status"] == "ok"
    bycell.setdefault(r["cell"], []).append(r)
bad = 0
for cid, rs in bycell.items():
    assert len(rs) == 8, (cid, len(rs))
    mn = sum(sum(r["null"]) / NREP for r in rs) / 8
    n = 4000 if mn <= 0 else min(4000, max(10, math.ceil(1.1 * 2500 / mn)))
    if n != dmap[cid]["n_curves"]:
        bad += 1
        print("sizing mismatch", cid, n, dmap[cid]["n_curves"])
print("pilot sizing mismatches:", bad)

# ---- main census ---------------------------------------------------------------------
main = load_jsonl(runs + "RUN-PFDR-eb4733/main-jobs.jsonl")
print("main records:", len(main), "non-ok:", sum(r["status"] != "ok" for r in main))
mc = {}
for r in main:
    mc.setdefault(r["cell"], {})[r["c"]] = r
assert sum(len(v) for v in mc.values()) == len(main), "duplicate (cell,c)"
for cid, v in mc.items():
    assert sorted(v) == list(range(dmap[cid]["n_curves"])), ("incomplete", cid)
print("completeness: every cell has exactly curves 0..n-1: OK; total", sum(dmap[c]["n_curves"] for c in dmap))

rng = np.random.default_rng(20261029)  # auditor's own seed; not the producer's
res = {}
for cid, bits, th, d, b in cells:
    recs = [mc[cid][c] for c in range(dmap[cid]["n_curves"])]
    nul = np.array([r["null"] for r in recs], dtype=np.float64)
    st = np.array([r["struct"] for r in recs], dtype=np.float64)
    pl = np.array([r["plant"] for r in recs], dtype=np.float64)
    mean = nul.mean(1)
    var = nul.var(1, ddof=1)
    S, M, V = st.sum(), mean.sum(), var.sum()
    kappa = S / M
    z = (S - M) / math.sqrt(V * (1 + 1 / 20))
    pk = pl.sum() / M
    pz = (pl.sum() - M) / math.sqrt(V * (1 + 1 / 20))
    # null-vs-null: replicate 0 vs other 19
    o = nul[:, 1:]
    Mc = o.mean(1).sum()
    Vc = o.var(1, ddof=1).sum()
    zcal = (nul[:, 0].sum() - Mc) / math.sqrt(Vc * (1 + 1 / 19))
    # curve-cluster bootstrap of kappa (own seed)
    n = len(recs)
    idx = rng.integers(0, n, size=(2000, n))
    ks = st[idx].sum(1) / mean[idx].sum(1)
    lo, hi = np.percentile(ks, [2.5, 97.5])
    feas = all(r["plant_feasible"] for r in recs)
    powered = M >= 2500
    if not powered:
        cls = "inconclusive_underpowered"
    elif not (feas and pk >= 1.15 and pz > 4):
        cls = "inconclusive_plant_not_recovered"
    elif abs(kappa - 1) >= 0.10 and abs(z) > 4:
        cls = "flagged"
    elif abs(kappa - 1) < 0.05 and lo >= 0.90 and hi <= 1.10:
        cls = "null"
    else:
        cls = "intermediate"
    res[cid] = dict(S=S, M=M, V=V, kappa=kappa, z=z, zcal=zcal, pk=pk, pz=pz, lo=lo, hi=hi, cls=cls, powered=powered, n=n)

pw = [r for r in res.values() if r["powered"]]
zc = [r["zcal"] for r in pw]
cal_mean, cal_sd = statistics.fmean(zc), statistics.pstdev(zc)
cal_pass = 0.85 <= cal_sd <= 1.15 and abs(cal_mean) <= 0.25
valid = [r for r in res.values() if r["cls"] in ("null", "flagged", "intermediate")]
fv = len(valid) / 90
flagged = [c for c, r in res.items() if r["cls"] == "flagged"]
if not cal_pass or fv < 0.5:
    outcome = "O-INVALID"
elif flagged:
    outcome = "O-PENDING-REPLICATION (no replication records)"
elif all(r["cls"] == "null" for r in valid) and fv >= 0.8:
    outcome = "O-NULL"
else:
    outcome = "O-MIXED"
print("MINE: calibration n=%d mean=%.12f sd=%.12f pass=%s; fraction_valid=%.12f; flagged=%s; outcome=%s"
      % (len(zc), cal_mean, cal_sd, cal_pass, fv, flagged, outcome))
from collections import Counter
print("MINE class counts:", dict(Counter(r["cls"] for r in res.values())))

# ---- compare with the session ---------------------------------------------------------
A = json.load(open(runs + "RUN-PFDR-b7c582/analysis.json"))
RR = json.load(open(runs + "RUN-PFDR-b7c582/raw-result.json"))["summary"]
print("SESSION summary:", RR)
mx = dict(S=0, M=0, V=0, kappa=0, z=0, zcal=0, pk=0, pz=0, lo=0, hi=0)
clsdiff = []
for c in A["cells"]:
    r = res[c["cell"]]
    mx["S"] = max(mx["S"], abs(c["S"] - r["S"]))
    mx["M"] = max(mx["M"], abs(c["M"] - r["M"]))
    mx["V"] = max(mx["V"], abs(c["V"] - r["V"]))
    mx["kappa"] = max(mx["kappa"], abs(c["kappa"] - r["kappa"]))
    mx["z"] = max(mx["z"], abs(c["z"] - r["z"]))
    if c.get("z_cal") is not None:
        mx["zcal"] = max(mx["zcal"], abs(c["z_cal"] - r["zcal"]))
    mx["pk"] = max(mx["pk"], abs(c["plant_kappa"] - r["pk"]))
    mx["pz"] = max(mx["pz"], abs(c["plant_z"] - r["pz"]))
    mx["lo"] = max(mx["lo"], abs(c["ci95"][0] - r["lo"]))
    mx["hi"] = max(mx["hi"], abs(c["ci95"][1] - r["hi"]))
    if c["cls"] != r["cls"]:
        clsdiff.append((c["cell"], c["cls"], r["cls"], c["ci95"], (r["lo"], r["hi"])))
print("max abs differences (session vs mine):", mx)
print("class differences:", clsdiff)
print("calibration diffs: n", A["calibration"]["n"] - len(zc), "mean", A["calibration"]["mean"] - cal_mean,
      "sd", A["calibration"]["sd"] - cal_sd)
print("fraction_valid diff:", A["fraction_valid"] - fv, "| outcome session:", A["outcome"])
