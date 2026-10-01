#!/usr/bin/env python3
"""J5 object O3 and J8(ii)-(iv) tallies (TASK-20260923-29e7af), from ARCHIVED
per-target records only (no pipeline run). For every family and D:
  - arm sizes; '1 in R_D' counts per arm (PS1 = any sat instance with 1 in R_D);
  - F-RANDX split by Tr(x_R) = r_0 (curve targets all have r_0 = Tr(A) = 0);
  - T_strict / T_set / T_rank retention and median f_div against own U1..U3;
  - first-divergence column degree distribution (own U1);
  - degenerate stratum '1 in R_D'.
Also M4 saturation: H(T_strict) vs log2 N; and the F-RANDX/F-S3 x_R overlap."""
import gzip, json, math, os
from collections import Counter
RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
HERE = os.path.dirname(os.path.abspath(__file__))
FAMS = ["F-S3", "F-S3-REV", "F-PLANT", "F-RANDX", "F-AFF-1", "F-AFF-2", "F-AFF-3", "F-NULLF2"]
def med(v):
    v = sorted(v); n = len(v)
    return None if n == 0 else (v[(n - 1) // 2] + v[n // 2]) / 2
def cp(k, n, a=0.05):
    # Clopper-Pearson via bisection on the exact binomial (own code)
    from math import comb
    def cdf(x, p): return sum(comb(n, i) * p**i * (1-p)**(n-i) for i in range(0, x + 1))
    def bis(f, lo=0.0, hi=1.0):
        for _ in range(60):
            m = (lo + hi) / 2
            if f(m): hi = m
            else: lo = m
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else bis(lambda p: 1 - cdf(k - 1, p) >= a / 2)
    hi = 1.0 if k == n else bis(lambda p: cdf(k, p) <= a / 2)
    return [round(lo, 4), round(hi, 4)]
out = {}
fs3_x = set()
for fam in FAMS:
    out[fam] = {}
    recs = [json.loads(l) for l in gzip.open(os.path.join(RUN, f"targets-{fam}.jsonl.gz"), "rt")]
    if fam == "F-S3": fs3_x = {r["x_R"] for r in recs}
    for D in (3, 4):
        R = [r for r in recs if r["D"] == D]
        cell = {}
        for arm in ("unsat", "sat", "degenerate"):
            A = [r for r in R if r["stratum"] == arm]
            k = sum(1 for r in A if r["one_in_R"])
            cell[arm] = {"n": len(A), "one_in_R": k, "rate": (k / len(A)) if A else None,
                         "CP95": cp(k, len(A)) if A else None}
        cell["PS1_sat_with_one_in_R"] = sum(1 for r in R if r["sat"] and r["one_in_R"])
        if fam in ("F-RANDX", "F-PLANT"):
            sp = {}
            for tr in (0, 1):
                for arm in ("unsat", "sat"):
                    A = [r for r in R if r["stratum"] == arm and (r["x_R"] & 1) == tr]
                    k = sum(1 for r in A if r["one_in_R"])
                    sp[f"r0={tr}/{arm}"] = {"n": len(A), "one_in_R": k, "rate": k / len(A) if A else None,
                                            "CP95": cp(k, len(A)) if A else None}
            cell["split_by_Tr_xR"] = sp
        # retention + f_div against own references (non-degenerate)
        nd = [r for r in R if r["stratum"] != "degenerate"]
        own = [k for k in ("U1", "U2", "U3") if nd and k in nd[0]["refs"]]
        ret = {}
        for ref in own:
            for arm in ("unsat", "sat"):
                A = [r for r in nd if r["stratum"] == arm]
                if not A: continue
                ret[f"{ref}/{arm}"] = {g: sum(r["refs"][ref]["match"][g] for r in A) / len(A) for g in ("rank", "set", "strict", "ops")}
                ret[f"{ref}/{arm}"]["median_f_div"] = med([r["refs"][ref]["f_div"] for r in A])
                ret[f"{ref}/{arm}"]["div_deg"] = dict(Counter(str(r["refs"][ref]["div_deg"]) for r in A))
        cell["retention_own"] = ret
        hs = Counter(r["h_strict"] for r in nd)
        N = len(nd)
        H = -sum(c / N * math.log2(c / N) for c in hs.values()) if N else None
        cell["M4"] = {"N": N, "distinct_T_strict": len(hs), "H_T_strict": H, "log2N": math.log2(N) if N else None}
        out[fam][f"D{D}"] = cell
rx = [json.loads(l) for l in gzip.open(os.path.join(RUN, "targets-F-RANDX.jsonl.gz"), "rt")]
out["F-RANDX_x_R_shared_with_F-S3_targets"] = sorted({r["idx"] for r in rx if r["x_R"] in fs3_x})
json.dump(out, open(os.path.join(HERE, "o3-j8-tallies.json"), "w"), indent=1)
for fam in FAMS:
    for D in ("D3", "D4"):
        c = out[fam][D]
        print(fam, D, {a: (c[a]["n"], c[a]["one_in_R"], c[a]["CP95"]) for a in ("unsat", "sat", "degenerate")},
              "PS1", c["PS1_sat_with_one_in_R"], "M4", round(c["M4"]["H_T_strict"], 3), c["M4"]["distinct_T_strict"], c["M4"]["N"])
        if "split_by_Tr_xR" in c: print("    split", {k: (v["n"], v["one_in_R"]) for k, v in c["split_by_Tr_xR"].items()})
        if D == "D4": print("    ret", {k: (round(v["strict"], 4), round(v["set"], 4), round(v["rank"], 4), v["median_f_div"]) for k, v in c["retention_own"].items() if k.startswith("U1")})
print("shared x_R", out["F-RANDX_x_R_shared_with_F-S3_targets"])
