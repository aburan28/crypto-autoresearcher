"""J-MUT: the small_x_offset construction, the height screen, z_M, z_Delta, and the
per-curve distributions of small_x, small_x_offset and the randoms.
TASK-20261009-bfdc5b. Deterministic (no randomness beyond the frozen seed rule
re-derived with the standard random module). Reads design.json, the census
rows (via the scratch counts extracted by extract_counts.py) and every job's
bases.jsonl.gz. Uses only the standard library and numpy.
"""
import glob
import gzip
import json
import random
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C

OUT = sys.argv[2]
cal = json.load(open(sys.argv[3]))
ROOT = "experiments/EXP-PFDR-0b3699/runs"
design = json.load(open(f"{ROOT}/RUN-PFDR-0b3699-p0-design/design.json"))
curves = design["curves"]
meta = json.load(open(f"{C.SCR}/rowmeta.json"))
d = C.load()


def rhs(c, x):
    return (x * x * x + c["a"] * x + c["b"]) % c["p"]


def liftable(c, x):
    r = rhs(c, x)
    return r != 0 and pow(r, (c["p"] - 1) // 2, c["p"]) == 1


x0_mis_design, x0_mis_row, bound_mis_row, bound_mis_design, range_viol = [], [], [], [], []
screen = {30: [], 32: []}
spans = []
for i, c in enumerate(curves):
    p, s = c["p"], c["s_sub"]
    x0 = p // 4 + random.Random(f"fb-smallx-offset|{p}|{c['a']}|{c['b']}|{s}|{c['curve'] + 9000}").randrange(p // 2)
    if x0 != c["x0"]:
        x0_mis_design.append((c["bits"], c["curve"]))
    prm = meta["params"]["small_x_offset"][i]
    if prm["x0"] != x0:
        x0_mis_row.append((c["bits"], c["curve"]))
    xs = []
    x = x0
    while len(xs) < s:
        if liftable(c, x):
            xs.append(x)
        x += 1
    bound = x
    if prm["bound"] != bound:
        bound_mis_row.append((c["bits"], c["curve"]))
    if c.get("offset_bound") != bound:
        bound_mis_design.append((c["bits"], c["curve"]))
    if not (x0 >= p / 4 and bound - 1 < 3 * p / 4):
        range_viol.append((c["bits"], c["curve"]))
    spans.append(bound - x0)
    hit = False
    for xx in xs:
        for v in range(1, 17):
            t = xx * v % p
            if t <= 4096 or t >= p - 4096:
                hit = True
                break
        if hit:
            break
    if hit:
        screen[c["bits"]].append(c["curve"])

# sampled bases (c % 10 == 0): offset and small_x points
key2c = {(c["bits"], c["curve"]): c for c in curves}
bchk = {"offset_records": 0, "offset_fail": [], "smallx_records": 0, "smallx_fail": [], "arms_seen": {}}
for fn in sorted(glob.glob(f"{ROOT}/RUN-PFDR-0b3699-table/attempt-1/jobs/*/bases.jsonl.gz")):
    with gzip.open(fn, "rt") as f:
        for line in f:
            r = json.loads(line)
            bchk["arms_seen"][r["arm"]] = bchk["arms_seen"].get(r["arm"], 0) + 1
            if r["arm"] not in ("small_x_offset", "small_x"):
                continue
            c = key2c[(r["bits"], r["curve"])]
            pts = r["points"]
            p = c["p"]
            ok = len(pts) == c["s_sub"] and len({q[0] for q in pts}) == len(pts)
            ok = ok and all((y * y - rhs(c, x)) % p == 0 and y != 0 and y == min(y, p - y) for x, y in pts)
            start = c["x0"] if r["arm"] == "small_x_offset" else 0
            exp, x = [], start
            while len(exp) < c["s_sub"]:
                if liftable(c, x):
                    exp.append(x)
                x += 1
            ok = ok and [q[0] for q in pts] == exp
            if r["arm"] == "small_x_offset":
                bchk["offset_records"] += 1
                if not ok:
                    bchk["offset_fail"].append((r["bits"], r["curve"]))
            else:
                bchk["smallx_records"] += 1
                if not ok:
                    bchk["smallx_fail"].append((r["bits"], r["curve"]))

# z_M, z_Delta, t_Delta
A = d["cnt_small_x"]; M = d["cnt_small_x_offset"]
r0, r1, r2 = d["cnt_random_sub_r0"], d["cnt_random_sub_r1"], d["cnt_random_sub_r2"]
adm = np.ones(len(A), bool)  # no CC-6 exclusion, empty height screen (checked above)
zA = C.cc8(A, r0, r1, r2)
zM = C.cc8(M, r0, r1, r2)
zD_V_all = (A.sum() - M.sum()) / np.sqrt(2 * zA["V"])
per_rung = {}
for b in C.RUNGS:
    s = d["bits"] == b
    per_rung[b] = {"small_x": C.cc8(A[s], r0[s], r1[s], r2[s]), "small_x_offset": C.cc8(M[s], r0[s], r1[s], r2[s])}

# distribution comparison
def hist(x, k=5):
    return np.bincount(np.minimum(x, k), minlength=k + 1).tolist()


def chi2_homog(tabs):
    T = np.array(tabs, dtype=float)
    T = T[:, T.sum(axis=0) > 0]
    # merge sparse upper cells into the last column with expected >= 5
    while T.shape[1] > 2:
        E = T.sum(axis=1, keepdims=True) * T.sum(axis=0, keepdims=True) / T.sum()
        if E[:, -1].min() >= 5:
            break
        T[:, -2] += T[:, -1]
        T = T[:, :-1]
    E = T.sum(axis=1, keepdims=True) * T.sum(axis=0, keepdims=True) / T.sum()
    stat = float(((T - E) ** 2 / E).sum())
    df = (T.shape[0] - 1) * (T.shape[1] - 1)
    return stat, df, T.tolist()


rpool = np.concatenate([r0, r1, r2])
comp = {}
for name, sel in (("pooled", np.ones(len(A), bool)), ("b30", d["bits"] == 30), ("b32", d["bits"] == 32)):
    hA, hM = hist(A[sel]), hist(M[sel])
    hR = (np.array(hist(r0[sel])) + np.array(hist(r1[sel])) + np.array(hist(r2[sel]))).tolist()
    st, df, T = chi2_homog([hA, hM])
    comp[name] = {"hist_small_x": hA, "hist_small_x_offset": hM, "hist_randoms_sum_of_3": hR,
                  "chi2_A_vs_M": st, "df": df, "merged_table": T,
                  "zero_frac": {"A": float((A[sel] == 0).mean()), "M": float((M[sel] == 0).mean()),
                                "R": float((np.vstack([r0, r1, r2])[:, sel] == 0).mean())}}
# rate by mu_model tertile (does M differ from A other than in level?)
tert = np.quantile(d["mu_model"], [1 / 3, 2 / 3])
grp = np.digitize(d["mu_model"], tert)
by_tert = {}
for g in range(3):
    s = grp == g
    Rm = (r0[s].sum() + r1[s].sum() + r2[s].sum()) / 3
    by_tert[g] = {"curves": int(s.sum()), "mu_sum": float(d["mu_model"][s].sum()), "C_A": int(A[s].sum()),
                  "C_M": int(M[s].sum()), "C_R": float(Rm), "kA": float(A[s].sum() / Rm), "kM": float(M[s].sum() / Rm)}
# per-curve paired difference A - M: variance vs the null expectation 2 x D x m_j
fit = C.fit_gnbr(d)
model = C.Model(d, fit)
diff = (A - M).astype(float)
paired = {"sum_diff": float(diff.sum()), "sum_sq_diff": float((diff ** 2).sum()),
          "null_expect_sum_sq_2Dm": float((2 * model.D * model.m).sum()),
          "ratio": float((diff ** 2).sum() / (2 * model.D * model.m).sum())}
mult = json.load(open(sys.argv[4]))["multiplicity_histogram_TT"]
tb = {a: int(d[f"tb_{a}"].sum()) for a in ("small_x", "small_x_offset", "random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub")}
sign_vs_proj = {a: int((d[f"sign_{a}"] != d[f"dist_{a}"]).sum()) for a in ("small_x", "small_x_offset")}

res = {"task": "TASK-20261009-bfdc5b", "joint": "J-MUT",
       "x0": {"curves": len(curves), "mismatch_vs_design": x0_mis_design, "mismatch_vs_census_params": x0_mis_row,
              "bound_mismatch_vs_census_params": bound_mis_row, "bound_mismatch_vs_design_offset_bound": bound_mis_design,
              "outside_p4_3p4": range_viol, "span_min_max_mean": [int(min(spans)), int(max(spans)), float(np.mean(spans))]},
       "height_screen_recomputed": screen, "height_screen_design": design["height_screen"],
       "height_screen_equal": {str(b): sorted(screen[b]) == sorted(design["height_screen"][str(b)]) for b in C.RUNGS},
       "sampled_bases": bchk,
       "z_A": zA, "z_M": zM, "z_Delta": zD_V_all, "z_Delta_curves": int(adm.sum()),
       "t_Delta_review": cal["t_Delta"], "z_Delta_gt_t_Delta": bool(zD_V_all > cal["t_Delta"]["mean"]),
       "per_rung": {str(b): v for b, v in per_rung.items()},
       "distribution_comparison": comp, "by_mu_tertile": by_tert, "paired_A_minus_M": paired,
       "multiplicity_TT": {a: mult[a] for a in ("small_x", "small_x_offset", "random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub")},
       "TB_totals": tb, "sign_only_ne_projective_curves": sign_vs_proj}
C.jdump(res, OUT)
print(json.dumps({k: res[k] for k in ("x0", "height_screen_equal", "z_Delta", "z_Delta_gt_t_Delta")}, indent=1, default=str))
print("bases", {k: (v if not isinstance(v, list) else len(v)) for k, v in bchk.items()})
print("zM", zM)
print(json.dumps(comp, indent=1))
print(json.dumps(by_tert, indent=1), paired)
